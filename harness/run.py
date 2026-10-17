#!/usr/bin/env python3
"""The measurement: build every kernel NONE, FAST and NONE-NOVEC, time them, write results/results.json.

Runs on a GitHub Actions runner, ubuntu-24.04 (x64, the default) or ubuntu-24.04-arm (arm64, Neoverse-N2), chosen by
the runner input of measure.yml, with clang-18, libc++-18-dev and valgrind from apt; the laptop has no
compiler. For every kernel it records the binary hashes, clang's vectorization remark for the marked loop, the trap count and the assembly of kern_<id>, the NONE-to-FAST
assembly diff, and Cachegrind instruction counts at the L1 size. For every cell (kernel x size)
it times NONE against FAST in ABBA order (20 processes per side, pinned to one CPU), and NONE
against NOVEC for kernels vectorized in NONE at the in-cache sizes. The A/A control times the
k02_add_fwd NONE binary at the L1 size against a byte-identical copy of itself.

Nothing here looks at a FAST timing to choose anything: sizes come from the cache sizes, inner
iterations from the NONE build only, and the rules are in harness/criteria.json, committed first.

Stage S2 adds the two real programs (harness/programs.py; sources and pinned fetch scripts in
programs/): each built NONE and FAST, whole-binary trap counts, 20 alternating processes per side,
an A/A pair of its own (its NONE binary against a byte-identical copy), Cachegrind instructions per
iteration, and the row's "consistent with at most X%" beside that A/A floor. It also times extra
A/A pairs of the A/A kernel at the other requested sizes; schema 1 has room for one A/A in
controls, so those go to details.json ("aa_extra") and never into the verdict.

Stage S3 (harness/criteria-v2.json; why: investigate/FINDINGS.md, the k02 loop-placement finding):
- every kernel and program is also built NONE and FAST with -falign-loops=64 (builds none_a64 and
  fast_a64), and every cell and program gets a second, "loops aligned" FAST/NONE pair (key "aligned");
- a layout A/A, NONE against NONE built with -falign-loops=64, for every kernel at the in-cache sizes
  (k02_add_fwd at L1 and L2 always: the designated pairs) and for every program (controls.layout_aa);
- each loop of kern_<id> in every build: start, length, 64-byte crossing (harness/placement.py,
  cells[].loops), and a whole-binary loop count for the programs (details.json);
- the verdict under criteria-v2 for this runner's CPU model, plus verdict_v1 (criteria.json, the
  as-compiled column) so the pre-registered answer stays visible. The workflow runs this as a
  matrix of jobs; harness/combine.py turns their results into the page-level line.

Stage S4-measurement (harness/criteria-v3.json, --criteria harness/criteria-v3.json): 40 processes
per side (fixed in the criteria), Cachegrind for NONE, FAST and the aligned pair at L1 and L2, and the
raw samples of the A/A and NOVEC pairs kept in results.json, so harness/pool.py can pool every job of
a CPU model with a two-level bootstrap. 'verdict' is then the per-job v2 rule (informational).

Usage:
  python3 harness/run.py                               # the full matrix: 8 kernels x L1, L2, RAM + programs
  python3 harness/run.py --kernels k02_add_fwd,k04_rev --sizes L1,L2 --programs none   # a subset
Writes <out>/results.json (schema 1), <out>/details.json (everything else the run saw),
<out>/asm/, <out>/remarks/ and <out>/cachegrind/.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import asm  # noqa: E402
import cachegrind  # noqa: E402
import placement  # noqa: E402
import programs  # noqa: E402
import remarks  # noqa: E402
import schema  # noqa: E402
import stats  # noqa: E402
import verdict  # noqa: E402

CXX = os.environ.get("HARNESS_CXX", "clang++-18")
OBJDUMP = os.environ.get("HARNESS_OBJDUMP", "objdump")
VALGRIND = os.environ.get("HARNESS_VALGRIND", "valgrind")
COMMON = ["-O2", "-std=c++20", "-stdlib=libc++"]
FLAGS = {
    "none": ["-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE"],
    "fast": ["-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"],
    "novec": ["-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE", "-fno-vectorize"],
}
ALIGN = ["-falign-loops=64"]  # criteria-v2.json, v2.align_flag
BUILD_FLAGS = {**FLAGS, "none_a64": FLAGS["none"] + ALIGN, "fast_a64": FLAGS["fast"] + ALIGN}
CRITERIA_V1 = "harness/criteria.json"
CRITERIA_V2 = "harness/criteria-v2.json"
CRITERIA_V3 = "harness/criteria-v3.json"
LAYOUT_AA_KERNEL_SIZES = ("L1", "L2")  # the designated layout A/A pairs (k02_add_fwd) are always timed at both
REMARK_FLAGS = ["-Rpass=loop-vectorize", "-Rpass-missed=loop-vectorize", "-Rpass-analysis=loop-vectorize"]
ALL_KERNELS = ["k01_sum_fwd", "k02_add_fwd", "k03_stencil", "k04_rev", "k05_stride2",
               "k06_gather", "k07_hist", "k08_matmul"]
# working set in bytes for the first argument n, counting every array of the kernel
BYTES_PER_N = {"k01_sum_fwd": 4, "k02_add_fwd": 12, "k03_stencil": 8, "k04_rev": 8, "k05_stride2": 12,
               "k06_gather": 12, "k07_hist": 4}
HIST_BYTES = 256 * 4
SKIPPED = {"k08_matmul.RAM"}  # see harness/criteria.json, design.skipped_cells
AA_KERNEL, AA_SIZE = "k02_add_fwd", "L1"
SIZES = ["L1", "L2", "RAM"]
IN_CACHE = ("L1", "L2")
TARGET_NS = 75e6
RAM_CAP = 256 * 1024 * 1024
CG_ITERS = 20


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, **kw)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path):
    return os.path.relpath(path, REPO).replace("\\", "/")


# ---------------------------------------------------------------- the machine

def parse_size(s):
    s = s.strip()
    mult = {"K": 1024, "M": 1024 ** 2, "G": 1024 ** 3}
    return int(s[:-1]) * mult[s[-1]] if s[-1] in mult else int(s)


def caches():
    base = "/sys/devices/system/cpu/cpu0/cache"
    found = {}
    for d in sorted(os.listdir(base)):
        if not d.startswith("index"):
            continue
        def rd(f):
            with open(os.path.join(base, d, f)) as fh:
                return fh.read().strip()
        if rd("type") == "Instruction":
            continue
        found[int(rd("level"))] = parse_size(rd("size"))
    return {"l1d": found[1], "l2": found[2], "l3": found.get(3), "llc": found[max(found)]}


def runner_info(cache):
    lscpu = sh(["lscpu"]).stdout
    model = re.search(r"Model name:\s*(.*)", lscpu)
    return {
        "os": sh(["lsb_release", "-ds"]).stdout.strip() or None,
        "kernel": sh(["uname", "-r"]).stdout.strip() or None,
        "arch": sh(["uname", "-m"]).stdout.strip() or None,
        "cpu_model": model.group(1).strip() if model else None,
        "cores": os.cpu_count(),
        "l1d_kib": cache["l1d"] // 1024,
        "l2_kib": cache["l2"] // 1024,
        "l3_kib": cache["l3"] // 1024 if cache["l3"] else None,
    }, lscpu


def toolchain():
    v = sh([CXX, "--version"]).stdout.splitlines()
    pkg = sh(["dpkg-query", "-W", "-f=${Version}", "libc++-18-dev"]).stdout.strip()
    return {"clang": v[0] if v else None, "libcxx_package": ("libc++-18-dev " + pkg) if pkg else None}


# ---------------------------------------------------------------- sizes

def n_for(kernel, target_bytes):
    """The first argument of the kernel binary that makes its working set about target_bytes."""
    if kernel == "k08_matmul":
        return max(8, int((target_bytes / 12) ** 0.5))
    if kernel == "k07_hist":
        return max(64, (target_bytes - HIST_BYTES) // BYTES_PER_N[kernel])
    return max(64, target_bytes // BYTES_PER_N[kernel])


def working_set(kernel, n):
    if kernel == "k08_matmul":
        return 12 * n * n
    if kernel == "k07_hist":
        return 4 * n + HIST_BYTES
    return BYTES_PER_N[kernel] * n


# ---------------------------------------------------------------- build

def compile_cmd(kernel, mode, out):
    return [CXX] + COMMON + BUILD_FLAGS[mode] + REMARK_FLAGS + ["-o", rel(out), f"kernels/{kernel}.cpp"]


def build_kernel(kernel, build_dir, out_dir):
    src = os.path.join(REPO, "kernels", kernel + ".cpp")
    with open(src, encoding="utf-8") as f:
        line = remarks.loop_line(f.read())
    info = {"source": f"kernels/{kernel}.cpp", "loop_line": line, "builds": {}}
    fn_lines = {}
    for mode in BUILD_FLAGS:
        out = os.path.join(build_dir, f"{kernel}.{mode}")
        cmd = compile_cmd(kernel, mode, out)
        r = sh(cmd)
        if r.returncode != 0:
            raise SystemExit(f"build failed {kernel} {mode}:\n{r.stderr}")
        with open(os.path.join(out_dir, "remarks", f"{kernel}.{mode}.txt"), "w", encoding="utf-8") as f:
            f.write(r.stderr)
        dump = sh([OBJDUMP, "-d", "--no-show-raw-insn", out]).stdout
        lines = asm.function_lines(dump, "kern_" + kernel)
        if not lines:
            raise SystemExit(f"kern_{kernel} not found in the objdump of {out}")
        fn_lines[mode] = lines
        with open(os.path.join(out_dir, "asm", f"{kernel}.{mode}.s"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        info["builds"][mode] = {"binary": out, "sha256": sha256(out), "command": " ".join(cmd),
                                "vectorization": remarks.vectorization(r.stderr, src, line),
                                "traps": asm.count_traps(lines), "asm_lines": len(lines),
                                "loops": placement.loops(lines)}
    info["diff"] = asm.unified_diff(fn_lines["none"], fn_lines["fast"], f"{kernel}.none.s", f"{kernel}.fast.s")
    info["diff_aligned"] = asm.unified_diff(fn_lines["none_a64"], fn_lines["fast_a64"], f"{kernel}.none_a64.s",
                                            f"{kernel}.fast_a64.s")
    return info


# ---------------------------------------------------------------- time

def run_bin(binary, args, cpu):
    r = sh(["taskset", "-c", cpu, binary] + [str(a) for a in args])
    if r.returncode != 0:
        raise RuntimeError(f"{binary} {args} exited {r.returncode}: {r.stderr[-500:]}")
    d = dict(kv.split("=", 1) for kv in r.stdout.split())
    return float(d["ns"]), d["checksum"]


def calibrate(binary, n, cpu):
    best = min(run_bin(binary, [n, 1], cpu)[0] for _ in range(3))
    return max(1, min(10_000_000, int(round(TARGET_NS / best)))), best


def pair(a_bin, b_bin, args, reps, cpu):
    """ABBA order: A B B A A B B A ... `reps` processes per side."""
    a_ns, b_ns, a_ck, b_ck, order = [], [], set(), set(), []
    for k in range(reps):
        for side in (("A", "B") if k % 2 == 0 else ("B", "A")):
            ns, ck = run_bin(a_bin if side == "A" else b_bin, args, cpu)
            (a_ns if side == "A" else b_ns).append(ns)
            (a_ck if side == "A" else b_ck).add(ck)
            order.append(side)
    return {"a_ns": a_ns, "b_ns": b_ns, "a_checksums": sorted(a_ck), "b_checksums": sorted(b_ck),
            "checksum_match": len(a_ck) == 1 and a_ck == b_ck, "order": "".join(order)}


def instr_count(binary, kernel, n, out_dir, tag):
    if shutil.which(VALGRIND) is None:
        return None, "valgrind not found"
    cg_file = os.path.join(out_dir, "cachegrind", f"{tag}.out")
    r = sh([VALGRIND, "--tool=cachegrind", "--cache-sim=no", f"--cachegrind-out-file={cg_file}",
            binary, str(n), str(CG_ITERS)])
    if r.returncode != 0 or not os.path.exists(cg_file):
        return None, f"valgrind exited {r.returncode}: {r.stderr[-300:]}"
    with open(cg_file, encoding="utf-8", errors="replace") as f:
        ir = cachegrind.per_call(f.read(), "kern_" + kernel, CG_ITERS + 1)
    return (ir if ir > 0 else None), ("ok" if ir > 0 else "kern function not found in the cachegrind output")


# ---------------------------------------------------------------- real programs (stage S2)

def calibrate_args(binary, args, cpu):
    """Inner iterations for about TARGET_NS per process; `args` come before the iteration count."""
    best = min(run_bin(binary, args + [1], cpu)[0] for _ in range(3))
    return max(1, min(10_000_000, int(round(TARGET_NS / best)))), best


def program_ir(binary, args, out_dir, tag):
    """Cachegrind Ir of one timed iteration of a whole program (see programs.per_iteration_ir)."""
    if shutil.which(VALGRIND) is None:
        return None, "valgrind not found"
    totals = []
    for iters in (1, 1 + programs.CG_EXTRA_ITERS):
        cg_file = os.path.join(out_dir, "cachegrind", f"{tag}.i{iters}.out")
        r = sh([VALGRIND, "--tool=cachegrind", "--cache-sim=no", f"--cachegrind-out-file={cg_file}",
                binary] + [str(x) for x in args] + [str(iters)])
        if r.returncode != 0 or not os.path.exists(cg_file):
            return None, f"valgrind exited {r.returncode}: {r.stderr[-300:]}"
        with open(cg_file, encoding="utf-8", errors="replace") as f:
            totals.append(programs.summary_ir(f.read()))
    ir = programs.per_iteration_ir(totals[0], totals[1])
    return ir, {"ir_total_iters_1": totals[0], f"ir_total_iters_{1 + programs.CG_EXTRA_ITERS}": totals[1],
                "ir_per_iteration": ir}


def measure_program(name, deps, build_dir, out_dir, cpu, reps, use_cachegrind):
    """Builds, times and counts one real program. Returns (its results.json row, its details)."""
    spec = programs.PROGRAMS[name]
    inc = os.path.join(deps, spec["include"])
    det = {"source": spec["source"], "builds": {}}
    b = {}
    for mode in ("none", "fast", "none_a64", "fast_a64"):
        out = os.path.join(build_dir, f"{name}.{mode}")
        cmd = [CXX] + COMMON + BUILD_FLAGS[mode] + REMARK_FLAGS + ["-I", rel(inc), "-o", rel(out), spec["source"]]
        t = time.time()
        r = sh(cmd)
        if r.returncode != 0:
            raise SystemExit(f"build failed {name} {mode}:\n{r.stderr[-3000:]}")
        with open(os.path.join(out_dir, "remarks", f"{name}.{mode}.txt"), "w", encoding="utf-8") as f:
            f.write(r.stderr)
        dump = sh([OBJDUMP, "-d", "--no-show-raw-insn", out]).stdout.splitlines()
        b[mode] = {"binary": out, "sha256": sha256(out), "traps": asm.count_traps(dump), "command": " ".join(cmd)}
        det["builds"][mode] = {"sha256": b[mode]["sha256"], "command": b[mode]["command"],
                               "traps_whole_binary": b[mode]["traps"], "compile_seconds": round(time.time() - t, 1),
                               "loop_remarks": programs.remark_counts(r.stderr),
                               "loop_placement_whole_binary": placement.binary_summary(dump)}
    print(f"[build] {name}: traps none/fast {b['none']['traps']}/{b['fast']['traps']}  loop remarks "
          f"none {det['builds']['none']['loop_remarks']} fast {det['builds']['fast']['loop_remarks']}", flush=True)

    # the input and its sha256 (a generated input is dumped by the program itself, before any timing)
    if spec["input"]:
        input_path = os.path.join(deps, spec["input"])
    else:
        input_path = os.path.join(build_dir, f"{name}.input.bin")
        r = sh([b["none"]["binary"]] + spec["args"] + ["1", input_path])
        if r.returncode != 0 or not os.path.exists(input_path):
            raise SystemExit(f"{name}: could not dump its generated input: {r.stderr[-500:]}")
    input_sha = sha256(input_path)
    det["input"] = {"path": rel(input_path), "bytes": os.path.getsize(input_path), "sha256": input_sha}
    args = [input_path if x == "{input}" else x for x in spec["args"]]

    copy = os.path.join(build_dir, f"{name}.none_copy")
    shutil.copyfile(b["none"]["binary"], copy)
    shutil.copymode(b["none"]["binary"], copy)
    if sha256(copy) != b["none"]["sha256"]:
        raise SystemExit(f"{name}: A/A copy is not byte-identical")

    iters, one = calibrate_args(b["none"]["binary"], args, cpu)
    t = time.time()
    fp = pair(b["none"]["binary"], b["fast"]["binary"], args + [iters], reps, cpu)
    aa = pair(b["none"]["binary"], copy, args + [iters], reps, cpu)
    ap = pair(b["none_a64"]["binary"], b["fast_a64"]["binary"], args + [iters], reps, cpu)
    lp = pair(b["none"]["binary"], b["none_a64"]["binary"], args + [iters], reps, cpu)
    for what, pr in (("NONE and FAST", fp), ("aligned NONE and FAST", ap), ("NONE and aligned NONE", lp)):
        if not pr["checksum_match"]:
            raise SystemExit(f"{name}: {what} checksums differ: {pr['a_checksums']} {pr['b_checksums']}")
    s = stats.summarize(fp["a_ns"], fp["b_ns"])
    aa_s = stats.summarize(aa["a_ns"], aa["b_ns"])
    a_s = stats.summarize(ap["a_ns"], ap["b_ns"])
    l_s = stats.summarize(lp["a_ns"], lp["b_ns"])
    shown = [rel(x) if os.path.isabs(str(x)) else str(x) for x in args]
    det.update({"iters": iters, "calibration_ns_one_iter": one,
                "run_lines": [f"taskset -c {cpu} {rel(b[m]['binary'])} {' '.join(shown)} {iters}"
                              for m in ("none", "fast")],
                "fast_pair": fp, "aa_pair": aa, "aa": {**aa_s, "binary_sha256": b["none"]["sha256"]},
                "aligned_pair": ap, "layout_aa_pair": lp,
                "seconds_timing": round(time.time() - t, 1)})

    instr = None
    if use_cachegrind:
        ir_n, why_n = program_ir(b["none"]["binary"], args, out_dir, f"{name}.none")
        ir_f, why_f = program_ir(b["fast"]["binary"], args, out_dir, f"{name}.fast")
        det["cachegrind"] = {"none": why_n, "fast": why_f, "unit": "instructions per timed iteration, not time"}
        if ir_n and ir_f:
            instr = {"none": ir_n, "fast": ir_f, "ratio": ir_f / ir_n}

    row = {"name": name, "pin": spec["pin"], "input_sha256": input_sha,
           "none_sha256": b["none"]["sha256"], "fast_sha256": b["fast"]["sha256"],
           "traps_none": b["none"]["traps"], "traps_fast": b["fast"]["traps"],
           "ratio": s["ratio"], "ci95": s["ci95"], "aa_half_width_pct": aa_s["half_width_pct"],
           "consistent_with_at_most_pct": programs.consistent_with_at_most_pct(s["ci95"], aa_s["half_width_pct"]),
           "none_ns": fp["a_ns"], "fast_ns": fp["b_ns"], "instr": instr,
           "aligned": {"none_sha256": b["none_a64"]["sha256"], "fast_sha256": b["fast_a64"]["sha256"],
                       "traps_none": b["none_a64"]["traps"], "traps_fast": b["fast_a64"]["traps"],
                       "none_ns": ap["a_ns"], "fast_ns": ap["b_ns"], "ratio": a_s["ratio"], "ci95": a_s["ci95"],
                       "consistent_with_at_most_pct": programs.consistent_with_at_most_pct(
                           a_s["ci95"], aa_s["half_width_pct"])}}
    layout = layout_row(name, "none", "none_a64", b["none"]["sha256"], b["none_a64"]["sha256"], lp, l_s, reps)
    print(f"[program] {name} aligned fast/none {a_s['ratio']:.4f} [{a_s['ci95'][0]:.4f}, {a_s['ci95'][1]:.4f}]  "
          f"layout A/A {l_s['ratio']:.4f} half-width {l_s['half_width_pct']:.3f}%", flush=True)
    print(f"[program] {name} iters={iters} fast/none {s['ratio']:.4f} [{s['ci95'][0]:.4f}, {s['ci95'][1]:.4f}] "
          f"A/A half-width {aa_s['half_width_pct']:.3f}% -> consistent with at most "
          f"{row['consistent_with_at_most_pct']:.2f}% (whole program; never a confirmation of 0.30%)"
          + (f"  Ir/iteration {instr['none']}/{instr['fast']}" if instr else ""), flush=True)
    return row, det, layout


def layout_row(ident, a_build, b_build, a_sha, b_sha, pr, summ, reps):
    """One controls.layout_aa entry: NONE against NONE with a different loop alignment."""
    return {"id": ident, "a_build": a_build, "b_build": b_build, "a_sha256": a_sha, "b_sha256": b_sha,
            "n_per_side": reps, "ratio": summ["ratio"], "ci95": summ["ci95"],
            "half_width_pct": summ["half_width_pct"], "a_ns": pr["a_ns"], "b_ns": pr["b_ns"]}


def loops_of(builds):
    return {m: builds[m]["loops"] for m in ("none", "fast", "novec", "none_a64", "fast_a64")}


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--kernels", default="all", help="comma-separated kernel ids, or all")
    ap.add_argument("--sizes", default="L1,L2,RAM", help="comma-separated size classes")
    ap.add_argument("--reps", type=int, default=None,
                    help="processes per side (default: the criteria file's; v1/v2 20, v3 40)")
    ap.add_argument("--out", default=os.path.join(REPO, "results"))
    ap.add_argument("--build", default=os.path.join(REPO, "build"))
    ap.add_argument("--cpu", default=os.environ.get("HARNESS_CPU", "1"))
    ap.add_argument("--no-cachegrind", action="store_true")
    ap.add_argument("--programs", default="all", help="comma-separated program names, all, or none")
    ap.add_argument("--deps", default=os.path.join(REPO, "build", "deps"),
                    help="where programs/<name>/fetch.sh put the pinned downloads")
    ap.add_argument("--criteria", default=CRITERIA_V2, choices=(CRITERIA_V1, CRITERIA_V2, CRITERIA_V3),
                    help="the criteria file that decides results.json 'verdict' (verdict_v1 always uses v1)")
    a = ap.parse_args(argv)
    with open(os.path.join(REPO, a.criteria), encoding="utf-8") as f:
        crit_pre = json.load(f)
    v3 = crit_pre.get("version", 1) >= 3
    if a.reps is None:
        a.reps = crit_pre["v3"]["timing"]["reps_per_side"] if v3 else crit_pre["design"]["timing"]["reps_per_side"]
    # criteria-v3 (stage S4-measurement): Cachegrind for NONE, FAST and the aligned pair at every
    # in-cache size, and the raw samples of the A/A and NOVEC pairs in results.json (for pooling).
    cg_sizes = IN_CACHE if v3 else ("L1",)
    kernels = ALL_KERNELS if a.kernels == "all" else [k.strip() for k in a.kernels.split(",") if k.strip()]
    sizes = [s.strip() for s in a.sizes.split(",") if s.strip()]
    for k in kernels:
        if k not in ALL_KERNELS:
            raise SystemExit(f"unknown kernel {k}")
    for s in sizes:
        if s not in SIZES:
            raise SystemExit(f"unknown size class {s}")
    progs = ([] if a.programs == "none" else programs.ALL_PROGRAMS if a.programs == "all"
             else [p.strip() for p in a.programs.split(",") if p.strip()])
    for p in progs:
        if p not in programs.PROGRAMS:
            raise SystemExit(f"unknown program {p}")
    out_dir, build_dir = os.path.abspath(a.out), os.path.abspath(a.build)
    for d in (build_dir, out_dir, os.path.join(out_dir, "asm"), os.path.join(out_dir, "remarks"),
              os.path.join(out_dir, "cachegrind")):
        os.makedirs(d, exist_ok=True)

    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cache = caches()
    runner, lscpu = runner_info(cache)
    # The runner's CPU first: S1 saw the identical k02_add_fwd binary cost 1.6x on two EPYC models and
    # 0.98x on a third, so every result is read against the CPU it ran on, never averaged across CPUs.
    print(f"[runner] cpu_model: {runner['cpu_model']}  cores: {runner['cores']}  L1d {runner['l1d_kib']} KiB  "
          f"L2 {runner['l2_kib']} KiB  L3 {runner['l3_kib']} KiB", flush=True)
    targets = {"L1": cache["l1d"] // 2, "L2": cache["l2"] // 2, "RAM": min(4 * cache["llc"], RAM_CAP)}
    details = {"note": "everything the run saw that results.json (schema 1) has no key for",
               "lscpu": lscpu, "cache_bytes": cache, "size_targets_bytes": targets, "reps_per_side": a.reps,
               "pinned_cpu": a.cpu, "target_ns_per_process": TARGET_NS, "remark_flags": " ".join(REMARK_FLAGS),
               "kernels_requested": kernels, "sizes_requested": sizes, "kernels": {}, "cells": {}}

    # build (the A/A kernel is always built)
    built = {}
    for k in sorted(set(kernels) | {AA_KERNEL}, key=ALL_KERNELS.index):
        built[k] = build_kernel(k, build_dir, out_dir)
        b = built[k]["builds"]
        details["kernels"][k] = {
            "loop_line": built[k]["loop_line"],
            **{m: {"sha256": b[m]["sha256"], "command": b[m]["command"], "traps": b[m]["traps"],
                   "asm_lines": b[m]["asm_lines"], "vectorization": b[m]["vectorization"],
                   "loops": b[m]["loops"]} for m in b}}
        print(f"[build] {k}: none vec={b['none']['vectorization']['vectorized']} "
              f"w={b['none']['vectorization']['width']}  fast vec={b['fast']['vectorization']['vectorized']} "
              f"traps none/fast {b['none']['traps']}/{b['fast']['traps']}", flush=True)
        print(f"[loops] {k}: " + "  ".join(f"{m} {placement.summary(b[m]['loops'])}" for m in
                                         ("none", "fast", "none_a64", "fast_a64")), flush=True)

    # A/A control
    aa_none = built[AA_KERNEL]["builds"]["none"]["binary"]
    aa_copy = os.path.join(build_dir, f"{AA_KERNEL}.none_copy")
    shutil.copyfile(aa_none, aa_copy)
    shutil.copymode(aa_none, aa_copy)
    if sha256(aa_none) != sha256(aa_copy):
        raise SystemExit("A/A copy is not byte-identical")
    aa_n = n_for(AA_KERNEL, targets[AA_SIZE])
    aa_iters, _ = calibrate(aa_none, aa_n, a.cpu)
    aa_pair = pair(aa_none, aa_copy, [aa_n, aa_iters], a.reps, a.cpu)
    aa_sum = stats.summarize(aa_pair["a_ns"], aa_pair["b_ns"])
    details["aa"] = {"cell": f"{AA_KERNEL}.{AA_SIZE}", "n": aa_n, "iters": aa_iters, **aa_pair}
    print(f"[aa] {AA_KERNEL}.{AA_SIZE} ratio {aa_sum['ratio']:.4f} half-width {aa_sum['half_width_pct']:.3f}%",
          flush=True)

    # extra A/A pairs (stage S2): the A/A kernel at every other requested size; details.json only
    details["aa_extra"] = {}
    for sc in sizes:
        if sc == AA_SIZE:
            continue
        n_x = n_for(AA_KERNEL, targets[sc])
        it_x, _ = calibrate(aa_none, n_x, a.cpu)
        p_x = pair(aa_none, aa_copy, [n_x, it_x], a.reps, a.cpu)
        s_x = stats.summarize(p_x["a_ns"], p_x["b_ns"])
        details["aa_extra"][f"{AA_KERNEL}.{sc}"] = {"n": n_x, "iters": it_x, **s_x, **p_x}
        print(f"[aa-extra] {AA_KERNEL}.{sc} ratio {s_x['ratio']:.4f} half-width {s_x['half_width_pct']:.3f}% "
              "(details.json only)", flush=True)

    # layout A/A (stage S3): NONE against NONE built with -falign-loops=64. The designated pairs
    # (criteria-v2.json, v2.layout_aa_designated: k02_add_fwd at L1 and L2) are timed in every run,
    # the other kernels at the requested in-cache sizes inside the cell loop below.
    layout_aa = []

    def time_layout(k, sc, n, iters):
        bk = built[k]["builds"]
        lp = pair(bk["none"]["binary"], bk["none_a64"]["binary"], [n, iters], a.reps, a.cpu)
        if not lp["checksum_match"]:
            raise SystemExit(f"{k}.{sc}: NONE and aligned NONE checksums differ")
        ls = stats.summarize(lp["a_ns"], lp["b_ns"])
        layout_aa.append(layout_row(f"{k}.{sc}", "none", "none_a64", bk["none"]["sha256"], bk["none_a64"]["sha256"],
                                    lp, ls, a.reps))
        print(f"[layout-aa] {k}.{sc} none_a64/none {ls['ratio']:.4f} half-width {ls['half_width_pct']:.3f}%", flush=True)
        return lp, ls

    for sc in LAYOUT_AA_KERNEL_SIZES:
        if AA_KERNEL in kernels and sc in sizes:
            continue  # timed with its cell below
        n_l = n_for(AA_KERNEL, targets[sc])
        it_l, _ = calibrate(aa_none, n_l, a.cpu)
        time_layout(AA_KERNEL, sc, n_l, it_l)

    cells, positive = [], []
    for k in kernels:
        b = built[k]["builds"]
        vec_none, vec_fast = b["none"]["vectorization"], b["fast"]["vectorization"]
        diff_text = built[k]["diff"]
        for sc in sizes:
            cid = f"{k}.{sc}"
            if cid in SKIPPED:
                print(f"[skip] {cid} (criteria.json design.skipped_cells)", flush=True)
                continue
            n = n_for(k, targets[sc])
            iters, one = calibrate(b["none"]["binary"], n, a.cpu)
            args = [n, iters]
            t = time.time()
            fp = pair(b["none"]["binary"], b["fast"]["binary"], args, a.reps, a.cpu)
            s = stats.summarize(fp["a_ns"], fp["b_ns"])
            apr = pair(b["none_a64"]["binary"], b["fast_a64"]["binary"], args, a.reps, a.cpu)
            a_s = stats.summarize(apr["a_ns"], apr["b_ns"])
            det = {"n": n, "iters": iters, "calibration_ns_one_call": one, "fast_pair": fp, "aligned_pair": apr}
            if sc in IN_CACHE:
                lp, ls = time_layout(k, sc, n, iters)
                det["layout_aa_pair"] = lp
            if vec_none["vectorized"] is True and sc in IN_CACHE:
                npair = pair(b["none"]["binary"], b["novec"]["binary"], args, a.reps, a.cpu)
                ns = stats.summarize(npair["a_ns"], npair["b_ns"])
                det["novec_pair"] = npair
                det["novec"] = ns
                positive.append({"cell_id": cid, "novec_ratio": ns["ratio"], "ci95": ns["ci95"],
                                 **({"none_ns": npair["a_ns"], "novec_ns": npair["b_ns"]} if v3 else {})})
            instr = instr_a = None
            if sc in cg_sizes and not a.no_cachegrind:
                tag = f"{k}" if sc == "L1" else f"{k}.{sc}"
                ir_none, why_n = instr_count(b["none"]["binary"], k, n, out_dir, f"{tag}.none")
                ir_fast, why_f = instr_count(b["fast"]["binary"], k, n, out_dir, f"{tag}.fast")
                det["cachegrind"] = {"none": why_n, "fast": why_f, "iters": CG_ITERS}
                if ir_none and ir_fast:
                    instr = {"none": ir_none, "fast": ir_fast, "ratio": ir_fast / ir_none}
                if v3:
                    ir_na, why_na = instr_count(b["none_a64"]["binary"], k, n, out_dir, f"{tag}.none_a64")
                    ir_fa, why_fa = instr_count(b["fast_a64"]["binary"], k, n, out_dir, f"{tag}.fast_a64")
                    det["cachegrind"].update({"none_a64": why_na, "fast_a64": why_fa})
                    if ir_na and ir_fa:
                        instr_a = {"none": ir_na, "fast": ir_fa, "ratio": ir_fa / ir_na}
            diff_path = f"results/asm/{cid}.diff"
            with open(os.path.join(out_dir, "asm", f"{cid}.diff"), "w", encoding="utf-8") as f:
                f.write(diff_text)
            with open(os.path.join(out_dir, "asm", f"{cid}.aligned.diff"), "w", encoding="utf-8") as f:
                f.write(built[k]["diff_aligned"])
            run_lines = [f"taskset -c {a.cpu} {rel(b[m]['binary'])} {n} {iters}" for m in ("none", "fast")]
            cells.append({
                "cell_id": cid, "kernel": k, "size_class": sc, "working_set_bytes": working_set(k, n),
                "none_sha256": b["none"]["sha256"], "fast_sha256": b["fast"]["sha256"],
                "checksum_match": fp["checksum_match"],
                "vectorized_none": {"vectorized": vec_none["vectorized"], "width": vec_none["width"]},
                "vectorized_fast": {"vectorized": vec_fast["vectorized"], "width": vec_fast["width"]},
                "traps_none": b["none"]["traps"], "traps_fast": b["fast"]["traps"],
                "none_ns": fp["a_ns"], "fast_ns": fp["b_ns"],
                "ratio": s["ratio"], "ci95": s["ci95"], "instr": instr,
                "command": "\n".join([b["none"]["command"], b["fast"]["command"]] + run_lines),
                "asm_diff_path": diff_path,
                "aligned": {
                    "none_sha256": b["none_a64"]["sha256"], "fast_sha256": b["fast_a64"]["sha256"],
                    "checksum_match": apr["checksum_match"] and apr["a_checksums"] == fp["a_checksums"],
                    "vectorized_none": {"vectorized": b["none_a64"]["vectorization"]["vectorized"],
                                        "width": b["none_a64"]["vectorization"]["width"]},
                    "vectorized_fast": {"vectorized": b["fast_a64"]["vectorization"]["vectorized"],
                                        "width": b["fast_a64"]["vectorization"]["width"]},
                    "traps_none": b["none_a64"]["traps"], "traps_fast": b["fast_a64"]["traps"],
                    "none_ns": apr["a_ns"], "fast_ns": apr["b_ns"], "ratio": a_s["ratio"], "ci95": a_s["ci95"],
                    "asm_diff_path": f"results/asm/{cid}.aligned.diff",
                    **({"instr": instr_a} if v3 else {})},
                "loops": loops_of(b)})
            det["seconds"] = round(time.time() - t, 1)
            details["cells"][cid] = det
            print(f"[time] {cid} n={n} iters={iters} fast/none {s['ratio']:.3f} "
                  f"[{s['ci95'][0]:.3f}, {s['ci95'][1]:.3f}] aligned {a_s['ratio']:.3f} "
                  f"[{a_s['ci95'][0]:.3f}, {a_s['ci95'][1]:.3f}] ck={fp['checksum_match']}/{apr['checksum_match']}"
                  + (f" novec {det['novec']['ratio']:.3f}" if "novec" in det else "")
                  + (f" Ir {instr['none']}/{instr['fast']}" if instr else "")
                  + (f" Ir aligned {instr_a['none']}/{instr_a['fast']}" if instr_a else "")
                  + f" {det['seconds']}s", flush=True)

    prog_rows = []
    details["programs"] = {}
    details["programs_rule"] = ("consistent_with_at_most_pct = max(0, 100 * (ci95_hi - 1), aa_half_width_pct): "
                                "an upper bound never below the program's own A/A floor; whole-program time is "
                                "never a confirmation of 0.30%")
    for p in progs:
        t = time.time()
        row, det, lay = measure_program(p, os.path.abspath(a.deps), build_dir, out_dir, a.cpu, a.reps,
                                        not a.no_cachegrind)
        det["seconds"] = round(time.time() - t, 1)
        prog_rows.append(row)
        layout_aa.append(lay)
        details["programs"][p] = det

    cls = verdict.classes(cells)
    negative = [c["cell_id"] for c in cells if c["kernel"] in cls["kept"] and c["size_class"] in IN_CACHE]
    with open(os.path.join(REPO, a.criteria), "rb") as f:
        criteria_raw = f.read()
    criteria_sha = hashlib.sha256(criteria_raw).hexdigest()
    criteria_doc = json.loads(criteria_raw.decode("utf-8"))
    server, repo, run_id = (os.environ.get(x) for x in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"))
    results = {
        "schema": 1, "sample": False,
        "run": {"id": run_id or ("local-" + started), "commit": os.environ.get("GITHUB_SHA"),
                "workflow_run_url": f"{server}/{repo}/actions/runs/{run_id}" if run_id else None,
                "started_at": started, "runner": runner, "toolchain": toolchain(),
                "flags": {"common": " ".join(COMMON), **{m: " ".join(f) for m, f in FLAGS.items()},
                          "align": " ".join(ALIGN)},
                "criteria_sha256": criteria_sha, "criteria_file": a.criteria},
        "controls": {"aa": {"ratio": aa_sum["ratio"], "ci95": aa_sum["ci95"],
                            "half_width_pct": aa_sum["half_width_pct"], "n_per_side": a.reps,
                            "binary_sha256": sha256(aa_none),
                            **({"a_ns": aa_pair["a_ns"], "b_ns": aa_pair["b_ns"]} if v3 else {})},
                     "negative": negative, "positive": positive, "layout_aa": layout_aa},
        "cells": cells,
        "programs": prog_rows,
        "verdict": None,
        "prior_numbers": [],
    }
    results["verdict"] = verdict.compute(results, criteria_doc)
    results["verdict_v1"] = verdict.compute(results, verdict.load_criteria(os.path.join(REPO, CRITERIA_V1)))
    details["classes"] = cls
    details["seconds"] = round(time.time() - t0, 1)
    schema.validate(results)
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(out_dir, "details.json"), "w", encoding="utf-8") as f:
        json.dump(details, f, indent=1)
    print(f"[verdict] ({a.criteria}) {results['verdict']['form']}: {results['verdict']['line']}")
    print(f"[verdict_v1] ({CRITERIA_V1}, as compiled) {results['verdict_v1']['form']}: "
          f"{results['verdict_v1']['line']}")
    print(f"[done] {details['seconds']}s, schema ok, {len(cells)} cells -> {rel(out_dir)}/results.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
