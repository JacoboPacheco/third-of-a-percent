#!/usr/bin/env python3
"""Sibling toolchains: is the finding specific to clang 18 + libc++ 18 FAST at baseline SSE2?

Same 8 kernels (kernels/*.cpp, compiled in place, unchanged), same method as harness/run.py:
for each toolchain, an unhardened build and a hardened build, plus both again with
-falign-loops=64 (the "aligned" pair, the headline column); 20 processes per side in ABBA order,
pinned with taskset to one CPU; ratio of medians with a percentile-bootstrap 95 % interval
(siblings/stats.py, a verbatim copy of harness/stats.py: same seed, same 10 000 resamples);
inner iterations calibrated to about 75 ms per process on each toolchain's own unhardened build;
an A/A (unhardened k02_add_fwd at L1 against a byte-identical copy) and a layout A/A (unhardened
against unhardened -falign-loops=64) per toolchain per job; the compiler's vectorization remark
for the marked loop, the check-trap count and the loop placement for every build.

Variants (hardened build vs that toolchain's unhardened build):
  clang18-fast        clang++-18, libc++ 18, _LIBCPP_HARDENING_MODE_FAST   (the reference row)
  clang18-extensive   same, _LIBCPP_HARDENING_MODE_EXTENSIVE
  clang18-debug       same, _LIBCPP_HARDENING_MODE_DEBUG (recorded as not built if it fails)
  clang18v3-fast      same as the reference, all builds with -march=x86-64-v3 (AVX2); timed only
                      when /proc/cpuinfo has every x86-64-v3 flag, otherwise recorded as skipped
  gcc14-O2-assert     g++-14 -O2, libstdc++, -D_GLIBCXX_ASSERTIONS vs -U_GLIBCXX_ASSERTIONS
  gcc14-O3-assert     the same at -O3 (an extra: GCC's -O2 uses the "very cheap" vectorizer cost model)
  clangNEW-fast       the newest clang apt provides (CLANG_NEW=<version>), FAST, with libc++ of the
                      same version when apt has it (CLANG_NEW_LIBCXX=<version>), else libc++ 18

The variants are split into parts so one job stays well under the 25-minute limit:
  part A: clang18-fast, clang18-extensive, clang18-debug, clang18v3-fast
  part B: clang18-fast, gcc14-O2-assert, gcc14-O3-assert
  part C: clangNEW-fast (alone: libc++-20-dev and libc++-18-dev cannot be installed together)
Parts A and B repeat the reference row, so those jobs can be read against their own reference;
part C is read against the reference row of A and B jobs on the same CPU model.

Sizes: L1 and L2 only (half of L1d, half of L2). RAM cells did not reproduce in the day-one runs
and are not in the headline, so they are not timed here.

Usage: python3 siblings/run.py --part A --out out [--reps 20] [--sizes L1,L2] [--kernels all]
Writes <out>/siblings.json (every raw sample), <out>/asm/, <out>/remarks/.
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
import placement  # noqa: E402
import remarks  # noqa: E402
import stats  # noqa: E402

OBJDUMP = "objdump"
ALIGN = ["-falign-loops=64"]
CLANG_REMARKS = ["-Rpass=loop-vectorize", "-Rpass-missed=loop-vectorize", "-Rpass-analysis=loop-vectorize"]
GCC_REMARKS = ["-fopt-info-vec-optimized", "-fopt-info-vec-missed"]
ALL_KERNELS = ["k01_sum_fwd", "k02_add_fwd", "k03_stencil", "k04_rev", "k05_stride2",
               "k06_gather", "k07_hist", "k08_matmul"]
BYTES_PER_N = {"k01_sum_fwd": 4, "k02_add_fwd": 12, "k03_stencil": 8, "k04_rev": 8, "k05_stride2": 12,
               "k06_gather": 12, "k07_hist": 4}
HIST_BYTES = 256 * 4
SIZES = ["L1", "L2"]
AA_KERNEL, AA_SIZE = "k02_add_fwd", "L1"
TARGET_NS = 75e6
V3_FLAGS = ("avx", "avx2", "bmi1", "bmi2", "f16c", "fma", "abm", "movbe", "xsave")
TIME_BUDGET_S = 19 * 60  # stop starting new cells after this, so the job writes its file before the timeout

LCX = "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_"


def toolchains(clang_new, clang_new_libcxx):
    """id -> spec. A spec: cxx, common flags, gcc (bool), none flags, hard {variant: flags}."""
    clang_common = ["-O2", "-std=c++20", "-stdlib=libc++"]
    tcs = {
        "clang18": {"cxx": "clang++-18", "common": clang_common, "gcc": False, "none": [LCX + "NONE"],
                    "hard": {"clang18-fast": [LCX + "FAST"], "clang18-extensive": [LCX + "EXTENSIVE"],
                             "clang18-debug": [LCX + "DEBUG"]},
                    "libcxx_package": "libc++-18-dev"},
        "clang18v3": {"cxx": "clang++-18", "common": clang_common + ["-march=x86-64-v3"], "gcc": False,
                      "none": [LCX + "NONE"], "hard": {"clang18v3-fast": [LCX + "FAST"]},
                      "libcxx_package": "libc++-18-dev"},
        "gcc14O2": {"cxx": "g++-14", "common": ["-O2", "-std=c++20"], "gcc": True,
                    "none": ["-U_GLIBCXX_ASSERTIONS"], "hard": {"gcc14-O2-assert": ["-D_GLIBCXX_ASSERTIONS"]},
                    "libcxx_package": "libstdc++-14-dev"},
        "gcc14O3": {"cxx": "g++-14", "common": ["-O3", "-std=c++20"], "gcc": True,
                    "none": ["-U_GLIBCXX_ASSERTIONS"], "hard": {"gcc14-O3-assert": ["-D_GLIBCXX_ASSERTIONS"]},
                    "libcxx_package": "libstdc++-14-dev"},
    }
    if clang_new:
        common = ["-O2", "-std=c++20", "-stdlib=libc++"]
        if clang_new_libcxx and clang_new_libcxx != clang_new:
            lib = f"/usr/lib/llvm-{clang_new_libcxx}"
            common += ["-nostdinc++", "-isystem", f"{lib}/include/c++/v1", f"-L{lib}/lib", f"-Wl,-rpath,{lib}/lib"]
        tcs["clangNEW"] = {"cxx": f"clang++-{clang_new}", "common": common, "gcc": False, "none": [LCX + "NONE"],
                           "hard": {f"clang{clang_new}-fast": [LCX + "FAST"]},
                           "libcxx_package": f"libc++-{clang_new_libcxx or clang_new}-dev"}
    return tcs


PARTS = {"A": {"clang18": ["clang18-fast", "clang18-extensive", "clang18-debug"], "clang18v3": ["clang18v3-fast"]},
         "B": {"clang18": ["clang18-fast"], "gcc14O2": ["gcc14-O2-assert"], "gcc14O3": ["gcc14-O3-assert"]},
         "C": {"clangNEW": None}}  # None: every hard variant of that toolchain


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
    return {"l1d": found[1], "l2": found[2], "l3": found.get(3)}


def cpu_flags():
    with open("/proc/cpuinfo") as f:
        for ln in f:
            if ln.startswith("flags"):
                return set(ln.split(":", 1)[1].split())
    return set()


def n_for(kernel, target_bytes):
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

def build(tc_id, tc, kernel, mode, flags, build_dir, out_dir, loop_line):
    """One binary. Returns its record, or {"failed": stderr tail} when it does not compile."""
    out = os.path.join(build_dir, f"{kernel}.{tc_id}.{mode}")
    cmd = [tc["cxx"]] + tc["common"] + flags + (GCC_REMARKS if tc["gcc"] else CLANG_REMARKS) + \
        ["-o", rel(out), f"kernels/{kernel}.cpp"]
    r = sh(cmd)
    tag = f"{kernel}.{tc_id}.{mode}"
    with open(os.path.join(out_dir, "remarks", tag + ".txt"), "w", encoding="utf-8") as f:
        f.write(" ".join(cmd) + "\n" + r.stderr)
    if r.returncode != 0:
        return {"failed": True, "command": " ".join(cmd), "stderr_tail": r.stderr[-1500:]}
    dump = sh([OBJDUMP, "-d", "--no-show-raw-insn", out]).stdout
    blocks = asm.function_blocks(dump, "kern_" + kernel)
    body = asm.main_block(blocks)
    if not body:
        return {"failed": True, "command": " ".join(cmd), "stderr_tail": f"kern_{kernel} not found in objdump"}
    all_lines = [ln for v in blocks.values() for ln in v]
    with open(os.path.join(out_dir, "asm", tag + ".s"), "w", encoding="utf-8") as f:
        f.write("\n\n".join("\n".join(v) for v in blocks.values()) + "\n")
    return {"binary": out, "sha256": sha256(out), "command": " ".join(cmd),
            "vectorization": remarks.vectorization(r.stderr, f"{kernel}.cpp", loop_line, tc["gcc"]),
            "traps": asm.trap_counts(all_lines), "blocks": list(blocks), "asm_lines": len(body),
            "loops": placement.loops(body), "body": body}


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
    """ABBA order: A B B A A B B A ... `reps` processes per side (as harness/run.py)."""
    a_ns, b_ns, a_ck, b_ck, order = [], [], set(), set(), []
    for k in range(reps):
        for side in (("A", "B") if k % 2 == 0 else ("B", "A")):
            ns, ck = run_bin(a_bin if side == "A" else b_bin, args, cpu)
            (a_ns if side == "A" else b_ns).append(ns)
            (a_ck if side == "A" else b_ck).add(ck)
            order.append(side)
    s = stats.summarize(a_ns, b_ns)
    return {"a_ns": a_ns, "b_ns": b_ns, "a_checksums": sorted(a_ck), "b_checksums": sorted(b_ck),
            "checksum_match": len(a_ck) == 1 and a_ck == b_ck, "order": "".join(order), **s}


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--part", required=True, choices=sorted(PARTS))
    ap.add_argument("--kernels", default="all")
    ap.add_argument("--sizes", default="L1,L2")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--cpu", default="1")
    ap.add_argument("--out", default="out")
    ap.add_argument("--build", default="build-siblings")
    ap.add_argument("--packages", default="", help="a file with `dpkg-query -W` lines of the installed toolchains")
    a = ap.parse_args(argv)
    kernels = ALL_KERNELS if a.kernels == "all" else [k.strip() for k in a.kernels.split(",") if k.strip()]
    sizes = [s.strip() for s in a.sizes.split(",") if s.strip()]
    assert all(k in ALL_KERNELS for k in kernels) and all(s in SIZES for s in sizes)
    out_dir, build_dir = os.path.abspath(a.out), os.path.abspath(a.build)
    for d in (out_dir, build_dir, os.path.join(out_dir, "asm"), os.path.join(out_dir, "remarks")):
        os.makedirs(d, exist_ok=True)

    t0 = time.time()
    clang_new, clang_new_lib = os.environ.get("CLANG_NEW", ""), os.environ.get("CLANG_NEW_LIBCXX", "")
    tcs = toolchains(clang_new, clang_new_lib)
    want = {}
    for tc_id, vs in PARTS[a.part].items():
        if tc_id not in tcs:
            continue
        want[tc_id] = list(tcs[tc_id]["hard"]) if vs is None else vs

    cache = caches()
    lscpu = sh(["lscpu"]).stdout
    m = re.search(r"Model name:\s*(.*)", lscpu)
    flags = cpu_flags()
    v3_missing = [f for f in V3_FLAGS if f not in flags]
    runner = {"cpu_model": m.group(1).strip() if m else None, "cores": os.cpu_count(),
              "kernel": sh(["uname", "-r"]).stdout.strip(), "os": sh(["lsb_release", "-ds"]).stdout.strip(),
              "l1d_kib": cache["l1d"] // 1024, "l2_kib": cache["l2"] // 1024,
              "l3_kib": cache["l3"] // 1024 if cache["l3"] else None,
              "x86_64_v3_flags_missing": v3_missing}
    print(f"[runner] {runner['cpu_model']}  L1d {runner['l1d_kib']} KiB  L2 {runner['l2_kib']} KiB  "
          f"x86-64-v3 flags missing: {v3_missing or 'none'}", flush=True)
    targets = {"L1": cache["l1d"] // 2, "L2": cache["l2"] // 2}
    skipped = []
    if "clang18v3" in want and v3_missing:
        skipped.append({"what": "clang18v3 (all cells)", "why": f"CPU lacks x86-64-v3 flags {v3_missing}"})
        del want["clang18v3"]

    doc = {"schema": "siblings-1", "part": a.part, "sample": False,
           "run": {"id": os.environ.get("GITHUB_RUN_ID"), "commit": os.environ.get("GITHUB_SHA"),
                   "job": os.environ.get("SIBLINGS_JOB"),
                   "workflow_run_url": (f"{os.environ.get('GITHUB_SERVER_URL')}/{os.environ.get('GITHUB_REPOSITORY')}"
                                        f"/actions/runs/{os.environ.get('GITHUB_RUN_ID')}")
                   if os.environ.get("GITHUB_RUN_ID") else None,
                   "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
           "runner": runner, "lscpu": lscpu, "cache_bytes": cache, "size_targets_bytes": targets,
           "method": {"reps_per_side": a.reps, "order": "ABBA", "pinned_cpu": a.cpu, "target_ns_per_process": TARGET_NS,
                      "ratio": "median(hardened)/median(unhardened)", "interval": "percentile bootstrap 95%, "
                      f"{stats.RESAMPLES} resamples, seed {stats.SEED}", "align_flag": " ".join(ALIGN),
                      "sizes": sizes, "time_budget_s": TIME_BUDGET_S},
           "toolchains": {}, "builds": {}, "aa": {}, "layout_aa": {}, "cells": [], "skipped": skipped}

    if a.packages and os.path.exists(a.packages):
        with open(a.packages) as f:
            doc["packages"] = [ln.strip() for ln in f if ln.strip()]

    # ---- build
    built = {}  # (tc_id, kernel) -> {mode: record}
    for tc_id in list(want):
        tc = tcs[tc_id]
        ver = sh([tc["cxx"], "--version"]).stdout.splitlines()
        doc["toolchains"][tc_id] = {"cxx": tc["cxx"], "version": ver[0] if ver else None,
                                    "common": " ".join(tc["common"]), "none": " ".join(tc["none"]),
                                    "hard": {v: " ".join(tc["hard"][v]) for v in want[tc_id]},
                                    "library": tc["libcxx_package"]}
        print(f"[toolchain] {tc_id}: {doc['toolchains'][tc_id]['version']}  common {' '.join(tc['common'])}", flush=True)
        modes = {"none": tc["none"], "none_a64": tc["none"] + ALIGN}
        for v in want[tc_id]:
            modes[v] = tc["hard"][v]
            modes[v + "_a64"] = tc["hard"][v] + ALIGN
        for k in sorted(set(kernels) | {AA_KERNEL}, key=ALL_KERNELS.index):
            with open(os.path.join(REPO, "kernels", k + ".cpp"), encoding="utf-8") as f:
                line = remarks.loop_line(f.read())
            recs = {md: build(tc_id, tc, k, md, fl, build_dir, out_dir, line) for md, fl in modes.items()}
            built[(tc_id, k)] = recs
            for v in want[tc_id]:
                if not recs.get(v, {}).get("failed") and not recs["none"].get("failed"):
                    for sfx in ("", "_a64"):
                        d = asm.unified_diff(recs["none" + sfx]["body"], recs[v + sfx]["body"],
                                             f"{k}.{tc_id}.none{sfx}.s", f"{k}.{tc_id}.{v}{sfx}.s")
                        with open(os.path.join(out_dir, "asm", f"{k}.{v}{sfx}.diff"), "w", encoding="utf-8") as f:
                            f.write(d)
            doc["builds"].setdefault(tc_id, {})[k] = {
                "loop_line": line,
                **{md: ({kk: vv for kk, vv in r.items() if kk not in ("body", "binary")}) for md, r in recs.items()}}
            msg = "  ".join(
                f"{md}:" + ("FAILED" if r.get("failed") else
                            f"vec={r['vectorization']['vectorized']}/w{r['vectorization']['width'] or r['vectorization']['vector_bytes']}"
                            f"/traps{r['traps']['total']}")
                for md, r in recs.items() if not md.endswith("_a64"))
            print(f"[build] {tc_id} {k}: {msg}", flush=True)
        # a hardened mode that did not compile for any kernel is dropped and recorded
        for v in list(want[tc_id]):
            fails = [k for k in kernels if built[(tc_id, k)][v].get("failed") or built[(tc_id, k)][v + "_a64"].get("failed")]
            if fails:
                skipped.append({"what": f"{v} on {', '.join(fails)}", "why": "did not compile",
                                "stderr_tail": built[(tc_id, fails[0])][v].get("stderr_tail")})
        if any(built[(tc_id, k)]["none"].get("failed") for k in kernels):
            skipped.append({"what": tc_id, "why": "unhardened build did not compile"})
            del want[tc_id]

    # ---- A/A and layout A/A per toolchain
    for tc_id in want:
        b = built[(tc_id, AA_KERNEL)]
        none_bin = b["none"]["binary"]
        copy = none_bin + ".copy"
        shutil.copyfile(none_bin, copy)
        shutil.copymode(none_bin, copy)
        if sha256(copy) != sha256(none_bin):
            raise SystemExit("A/A copy is not byte-identical")
        n = n_for(AA_KERNEL, targets[AA_SIZE])
        iters, _ = calibrate(none_bin, n, a.cpu)
        p = pair(none_bin, copy, [n, iters], a.reps, a.cpu)
        doc["aa"][tc_id] = {"cell": f"{AA_KERNEL}.{AA_SIZE}", "n": n, "iters": iters,
                            "binary_sha256": b["none"]["sha256"], **p}
        lp = pair(none_bin, b["none_a64"]["binary"], [n, iters], a.reps, a.cpu)
        doc["layout_aa"][tc_id] = {"cell": f"{AA_KERNEL}.{AA_SIZE}", "n": n, "iters": iters, **lp}
        print(f"[aa] {tc_id}: A/A {p['ratio']:.4f} half-width {p['half_width_pct']:.3f}%   "
              f"layout A/A {lp['ratio']:.4f} half-width {lp['half_width_pct']:.3f}%", flush=True)

    # ---- cells
    for k in kernels:
        for sc in sizes:
            for tc_id in want:
                recs = built[(tc_id, k)]
                n = n_for(k, targets[sc])
                todo = [v for v in want[tc_id] if not recs[v].get("failed") and not recs[v + "_a64"].get("failed")]
                if not todo:
                    continue
                if time.time() - t0 > TIME_BUDGET_S:
                    skipped.append({"what": f"{k}.{sc} {tc_id} {todo}", "why": "time budget reached"})
                    continue
                iters, one = calibrate(recs["none"]["binary"], n, a.cpu)
                for v in todo:
                    t = time.time()
                    fp = pair(recs["none"]["binary"], recs[v]["binary"], [n, iters], a.reps, a.cpu)
                    al = pair(recs["none_a64"]["binary"], recs[v + "_a64"]["binary"], [n, iters], a.reps, a.cpu)
                    ck_ok = fp["checksum_match"] and al["checksum_match"] and fp["a_checksums"] == al["a_checksums"]
                    vn, vh = recs["none"]["vectorization"], recs[v]["vectorization"]
                    cell = {"toolchain": tc_id, "variant": v, "kernel": k, "size_class": sc, "n": n,
                            "working_set_bytes": working_set(k, n), "iters": iters, "calibration_ns_one_call": one,
                            "checksum": fp["a_checksums"], "checksum_ok": ck_ok,
                            "vectorized_none": {x: vn[x] for x in ("vectorized", "width", "vector_bytes")},
                            "vectorized_hard": {x: vh[x] for x in ("vectorized", "width", "vector_bytes")},
                            "vectorized_none_a64": recs["none_a64"]["vectorization"]["vectorized"],
                            "vectorized_hard_a64": recs[v + "_a64"]["vectorization"]["vectorized"],
                            "traps_none": recs["none"]["traps"]["total"], "traps_hard": recs[v]["traps"]["total"],
                            "none_sha256": recs["none"]["sha256"], "hard_sha256": recs[v]["sha256"],
                            "commands": [recs["none"]["command"], recs[v]["command"],
                                         recs["none_a64"]["command"], recs[v + "_a64"]["command"],
                                         f"taskset -c {a.cpu} <binary> {n} {iters}"],
                            "as_compiled": {kk: fp[kk] for kk in ("ratio", "ci95", "half_width_pct", "a_ns", "b_ns",
                                                                  "order", "checksum_match")},
                            "aligned": {kk: al[kk] for kk in ("ratio", "ci95", "half_width_pct", "a_ns", "b_ns",
                                                              "order", "checksum_match")},
                            "seconds": round(time.time() - t, 1)}
                    doc["cells"].append(cell)
                    print(f"[time] {v:18s} {k}.{sc} n={n} it={iters} vec {vn['vectorized']}->{vh['vectorized']} "
                          f"as-compiled {fp['ratio']:.3f} [{fp['ci95'][0]:.3f},{fp['ci95'][1]:.3f}] "
                          f"aligned {al['ratio']:.3f} [{al['ci95'][0]:.3f},{al['ci95'][1]:.3f}] ck={ck_ok} "
                          f"{cell['seconds']}s", flush=True)

    # checksums must agree across toolchains too (same source, same input)
    by_cell = {}
    for c in doc["cells"]:
        by_cell.setdefault(f"{c['kernel']}.{c['size_class']}", set()).update(c["checksum"])
    doc["checksum_agreement_across_toolchains"] = {cid: len(v) == 1 for cid, v in by_cell.items()}
    doc["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(out_dir, "siblings.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print(f"[done] {doc['seconds']}s, {len(doc['cells'])} cells, skipped: {[s['what'] for s in skipped]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
