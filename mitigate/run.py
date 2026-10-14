#!/usr/bin/env python3
"""The mitigation experiment: can a rewrite keep libc++ FAST hardening ON and not pay?

For four loop shapes that pay under FAST in the main study (reverse, stride-2, gather, matrix
multiply), mitigate/src/mNN_*.cpp holds the original kernel and semantically equivalent rewrites,
one per -DV_<name>. For every variant this builds NONE, FAST and both again with -falign-loops=64,
and records the compiler's vectorization remark at the variant's marked loop, the check traps (ud2)
in the kernel function, its loops, its assembly and the diffs; runs the SAFETY test (an input one
element too short: must the program stop?); and times the variant against the original's NONE
build and against its own NONE build, as compiled and aligned, at the L1 and L2 sizes.
The rules for reading the numbers are in mitigate/criteria.json, committed before the first timed run.

Usage (on an ubuntu-24.04 runner with clang-18 and libc++-18-dev from apt):
  python3 mitigate/run.py --out out                  # everything
  python3 mitigate/run.py --out out --no-timing      # builds, remarks, safety only (a probe)
  python3 mitigate/run.py --kernels m04_rev --sizes L1
Writes <out>/results.json (raw samples included), <out>/asm/ and <out>/remarks/.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import asm  # noqa: E402  (copies of the harness modules, so this folder stands on its own)
import placement  # noqa: E402
import remarks  # noqa: E402
import stats  # noqa: E402

CXX = os.environ.get("MITIGATE_CXX", "clang++-18")
OBJDUMP = os.environ.get("MITIGATE_OBJDUMP", "objdump")
COMMON = ["-O2", "-std=c++20", "-stdlib=libc++"]
MODE = {"none": ["-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE"],
        "fast": ["-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"]}
ALIGN = ["-falign-loops=64"]
BUILD_FLAGS = {"none": MODE["none"], "fast": MODE["fast"],
               "none_a64": MODE["none"] + ALIGN, "fast_a64": MODE["fast"] + ALIGN}
REMARK_FLAGS = ["-Rpass=loop-vectorize", "-Rpass-missed=loop-vectorize", "-Rpass-analysis=loop-vectorize"]
TARGET_NS = 75e6
SIZES = ("L1", "L2")
SAFETY_N = {"m04_rev": 1000, "m05_stride2": 1000, "m06_gather": 1000, "m08_matmul": 16}

# Every variant: what it is, the claim it makes about safety, and its readability cost in one phrase.
KERNELS = {
    "m04_rev": {
        "original": "k04_rev", "shape": "reverse", "bytes_per_n": 8,
        "variants": {
            "orig": ("the original operator[] loop", "hardening", "none (the original)"),
            "pre": ("one up-front size check, then the same operator[] loop", "hardening + REQUIRE", "one line added"),
            "span": ("std::span, c taken as first(n) once", "hardening (span::first)", "two lines added, indexes a span"),
            "raw": ("data() pointers behind one up-front check", "REQUIRE only", "raw pointers: safety rests on one line"),
            "fwd": ("the same loop counting up", "hardening", "loop header changed, element order not kept"),
            "rtransform": ("std::transform over rbegin/rend", "none claimed (iterators are unchecked)", "one-line algorithm"),
            "pragma": ("the original plus #pragma clang loop vectorize(enable)", "hardening", "one pragma line"),
        }},
    "m05_stride2": {
        "original": "k05_stride2", "shape": "stride-2", "bytes_per_n": 12,
        "variants": {
            "orig": ("the original operator[] loop", "hardening", "none (the original)"),
            "pre": ("one up-front size check, then the same operator[] loop", "hardening + REQUIRE", "one line added"),
            "span": ("std::span, a taken as first(2n) once", "hardening (span::first)", "three lines added, indexes a span"),
            "span_il2": ("the span variant plus #pragma clang loop interleave_count(2)", "hardening (span::first)",
                         "span lines plus one pragma"),
            "raw": ("data() pointers behind one up-front check", "REQUIRE only", "raw pointers: safety rests on one line"),
            "pairs": ("one index j = 2i walking a in pairs, after one up-front check", "hardening + REQUIRE",
                      "second induction variable"),
        }},
    "m06_gather": {
        "original": "k06_gather", "shape": "gather", "bytes_per_n": 12,
        "variants": {
            "orig": ("the original operator[] loop", "hardening", "none (the original)"),
            "pre": ("one up-front size check on c; a[idx[i]] still checked", "hardening + REQUIRE", "one line added"),
            "span": ("std::span for c and idx; a[idx[i]] still checked", "hardening (span)", "three lines added"),
            "clamp": ("clamped index (every load in range), one flag, trap after the loop", "clamp + REQUIRE",
                      "a loop body of three lines and raw pointers"),
            "validate": ("a first pass takes max(idx) and checks it once, then raw pointers", "REQUIRE only",
                         "a second loop and raw pointers: safety rests on the max pass"),
            "raw": ("raw pointers behind the size check on c; index values unchecked", "none claimed (index values unchecked)",
                    "raw pointers"),
        }},
    "m08_matmul": {
        "original": "k08_matmul", "shape": "matrix multiply", "bytes_per_n": None,
        "variants": {
            "orig": ("the original operator[] loops", "hardening", "none (the original)"),
            "pre": ("one up-front size check, then the same operator[] loops", "hardening + REQUIRE", "one line added"),
            "span": ("local row spans, subspan(row*d, d) checked once per row", "hardening (span::subspan)",
                     "three lines added, rows as spans"),
            "span_il2": ("the span variant plus #pragma clang loop interleave_count(2)", "hardening (span::subspan)",
                         "row spans plus one pragma"),
            "rowptr": ("raw local row pointers behind one up-front check", "REQUIRE only",
                       "raw pointers: safety rests on one line"),
            "transform": ("std::transform over checked row spans", "hardening (span::subspan)",
                          "row spans plus an algorithm call with a lambda"),
        }},
}


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
    mult = {"K": 1024, "M": 1024 ** 2, "G": 1024 ** 3}
    return int(s[:-1]) * mult[s[-1]] if s[-1] in mult else int(s)


def caches():
    base = "/sys/devices/system/cpu/cpu0/cache"
    found = {}
    for d in sorted(os.listdir(base)):
        if not d.startswith("index"):
            continue
        rd = lambda f: open(os.path.join(base, d, f)).read().strip()  # noqa: E731
        if rd("type") == "Instruction":
            continue
        found[int(rd("level"))] = parse_size(rd("size"))
    return {"l1d": found[1], "l2": found[2], "l3": found.get(3)}


def n_for(kernel, target_bytes):
    if kernel == "m08_matmul":
        return max(8, int((target_bytes / 12) ** 0.5))
    return max(64, target_bytes // KERNELS[kernel]["bytes_per_n"])


def working_set(kernel, n):
    return 12 * n * n if kernel == "m08_matmul" else KERNELS[kernel]["bytes_per_n"] * n


# ---------------------------------------------------------------- build

def variant_loop_line(source_text, variant):
    """The line of the "// LOOP" marker inside the #if / #elif block of defined(V_<variant>)."""
    inside = False
    for i, line in enumerate(source_text.splitlines(), 1):
        s = line.strip()
        if s.startswith(("#if", "#elif", "#else", "#endif")):
            inside = f"defined(V_{variant})" in s
            continue
        if inside and "// LOOP" in line:
            return i
    raise SystemExit(f"no // LOOP marker for V_{variant}")


PACKED = re.compile(r"\b(movdq[au]|movup[sd]|movap[sd]|padd\w|psub\w|pmul\w+|pshufd|punpck\w+|shufps)\b")


def simd_loops(loop_list):
    """Innermost loops of the function whose body holds a packed SIMD instruction."""
    return [lp for lp in placement.hot(loop_list) if lp.get("packed")]


def mark_packed(lines, loop_list):
    insns = placement.instructions(lines)
    for lp in loop_list:
        s, e = int(lp["start"], 16), int(lp["end"], 16)
        lp["packed"] = any(PACKED.search(t) for a, t in insns if s <= a < e)
    return loop_list


def build(kernel, variant, build_dir, out_dir, src_text):
    src = f"mitigate/src/{kernel}.cpp"
    line = variant_loop_line(src_text, variant)
    info = {"loop_line": line, "builds": {}}
    fn = {}
    for mode, flags in BUILD_FLAGS.items():
        out = os.path.join(build_dir, f"{kernel}.{variant}.{mode}")
        cmd = [CXX] + COMMON + flags + [f"-DV_{variant}"] + REMARK_FLAGS + ["-o", rel(out), src]
        r = sh(cmd)
        if r.returncode != 0:
            raise SystemExit(f"build failed {kernel} {variant} {mode}:\n{r.stderr[-3000:]}")
        with open(os.path.join(out_dir, "remarks", f"{kernel}.{variant}.{mode}.txt"), "w") as f:
            f.write(r.stderr)
        dump = sh([OBJDUMP, "-d", "--no-show-raw-insn", out]).stdout
        lines = asm.function_lines(dump, "kern_" + kernel)
        if not lines:
            raise SystemExit(f"kern_{kernel} not found in {out}")
        fn[mode] = lines
        with open(os.path.join(out_dir, "asm", f"{kernel}.{variant}.{mode}.s"), "w") as f:
            f.write("\n".join(lines) + "\n")
        lps = mark_packed(lines, placement.loops(lines))
        vec = remarks.vectorization(r.stderr, src, line)
        # remarks clang printed inside library headers (std::transform's loop lives there)
        hdr = sorted({re.sub(r"^.*?remark: ", "", x).strip() for x in r.stderr.splitlines()
                      if "remark:" in x and "/include/" in x and "vectorized loop" in x})
        info["builds"][mode] = {
            "binary": out, "sha256": sha256(out), "command": " ".join(cmd), "vectorization": vec,
            "header_vectorized_remarks": hdr, "traps": asm.count_traps(lines), "asm_lines": len(lines),
            "simd_innermost_loops": len(simd_loops(lps)), "loops": lps}
    for a, b in (("none", "fast"), ("none_a64", "fast_a64")):
        d = asm.unified_diff(fn[a], fn[b], f"{kernel}.{variant}.{a}.s", f"{kernel}.{variant}.{b}.s")
        with open(os.path.join(out_dir, "asm", f"{kernel}.{variant}.{a}-vs-{b}.diff"), "w") as f:
            f.write(d)
    return info, fn


# ---------------------------------------------------------------- safety

def safety_run(binary, n):
    r = subprocess.run(["taskset", "-c", "1", binary, str(n), "1", "short"], capture_output=True, text=True,
                       timeout=60)
    returned = "KERNEL_RETURNED" in r.stderr
    if r.returncode == -signal.SIGILL and not returned:
        outcome = "trapped"
    elif r.returncode == 0 and returned:
        outcome = "returned"
    else:
        outcome = f"crashed (exit {r.returncode})"
    return {"outcome": outcome, "exit": r.returncode, "stderr_tail": r.stderr[-200:]}


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
    """ABBA order: A B B A A B B A ... `reps` processes per side (harness/run.py, copied)."""
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
    ap.add_argument("--kernels", default="all")
    ap.add_argument("--variants", default="all", help="comma-separated variant names, or all")
    ap.add_argument("--sizes", default="L1,L2")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--cpu", default="1")
    ap.add_argument("--out", default=os.path.join(REPO, "out"))
    ap.add_argument("--build", default=os.path.join(REPO, "build", "mitigate"))
    ap.add_argument("--no-timing", action="store_true")
    a = ap.parse_args(argv)
    kernels = list(KERNELS) if a.kernels == "all" else [k.strip() for k in a.kernels.split(",")]
    sizes = [s.strip() for s in a.sizes.split(",")]
    out_dir, build_dir = os.path.abspath(a.out), os.path.abspath(a.build)
    for d in (out_dir, build_dir, os.path.join(out_dir, "asm"), os.path.join(out_dir, "remarks")):
        os.makedirs(d, exist_ok=True)

    t0 = time.time()
    cache = caches()
    lscpu = sh(["lscpu"]).stdout
    m = re.search(r"Model name:\s*(.*)", lscpu)
    cpu_model = m.group(1).strip() if m else None
    print(f"[runner] {cpu_model}  L1d {cache['l1d'] // 1024} KiB  L2 {cache['l2'] // 1024} KiB", flush=True)
    targets = {"L1": cache["l1d"] // 2, "L2": cache["l2"] // 2}
    with open(os.path.join(HERE, "criteria.json"), "rb") as f:
        criteria_sha = hashlib.sha256(f.read()).hexdigest()
    clang = sh([CXX, "--version"]).stdout.splitlines()
    pkg = sh(["dpkg-query", "-W", "-f=${Version}", "libc++-18-dev"]).stdout.strip()
    server, repo, run_id = (os.environ.get(x) for x in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"))
    res = {"what": "mitigation experiment, one job (mitigate/run.py; rules mitigate/criteria.json)",
           "run": {"id": run_id, "commit": os.environ.get("GITHUB_SHA"),
                   "url": f"{server}/{repo}/actions/runs/{run_id}" if run_id else None,
                   "job": os.environ.get("MITIGATE_JOB"),
                   "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "cpu_model": cpu_model, "cores": os.cpu_count(), "cache_bytes": cache,
                   "size_targets_bytes": targets, "clang": clang[0] if clang else None,
                   "libcxx_package": pkg or None, "flags": {"common": " ".join(COMMON),
                   **{k: " ".join(v) for k, v in BUILD_FLAGS.items()}}, "reps_per_side": a.reps,
                   "pinned_cpu": a.cpu, "target_ns_per_process": TARGET_NS, "criteria_sha256": criteria_sha,
                   "timing": not a.no_timing},
           "kernels": {}}

    for k in kernels:
        spec = KERNELS[k]
        src_text = open(os.path.join(HERE, "src", k + ".cpp"), encoding="utf-8").read()
        variants = [v for v in spec["variants"] if a.variants == "all" or v in a.variants.split(",") or v == "orig"]
        kres = {"original_kernel": spec["original"], "shape": spec["shape"], "source": f"mitigate/src/{k}.cpp",
                "variants": {}, "aa": {}}
        fns = {}
        for v in variants:
            info, fn = build(k, v, build_dir, out_dir, src_text)
            fns[v] = fn
            what, claim, cost = spec["variants"][v]
            sn = SAFETY_N[k]
            safety = {mode: safety_run(info["builds"][mode]["binary"], sn) for mode in ("none", "fast")}
            info.update({"what": what, "safety_claim": claim, "readability_cost": cost, "safety_n": sn,
                         "safety": safety, "keeps_safety": safety["fast"]["outcome"] == "trapped"})
            b = info["builds"]
            print(f"[build] {k}.{v}: vec none/fast {b['none']['vectorization']['vectorized']}/"
                  f"{b['fast']['vectorization']['vectorized']} simd-loops {b['none']['simd_innermost_loops']}/"
                  f"{b['fast']['simd_innermost_loops']} ud2 {b['none']['traps']}/{b['fast']['traps']} "
                  f"safety none={safety['none']['outcome']} fast={safety['fast']['outcome']}", flush=True)
            kres["variants"][v] = info
        if "orig" in fns:
            for v in variants:
                if v == "orig":
                    continue
                for mode in ("fast", "fast_a64"):
                    d = asm.unified_diff(fns["orig"][mode], fns[v][mode], f"{k}.orig.{mode}.s", f"{k}.{v}.{mode}.s")
                    with open(os.path.join(out_dir, "asm", f"{k}.orig-vs-{v}.{mode}.diff"), "w") as f:
                        f.write(d)
        if kres["variants"]["orig"]["safety"]["none"]["outcome"] != "returned":
            print(f"[warn] {k}: the original NONE build did not return on the short input; "
                  "the safety test may not exercise an out-of-range access", flush=True)

        if not a.no_timing:
            ob = kres["variants"]["orig"]["builds"]
            copy = os.path.join(build_dir, f"{k}.orig.none_copy")
            shutil.copyfile(ob["none"]["binary"], copy)
            shutil.copymode(ob["none"]["binary"], copy)
            if sha256(copy) != ob["none"]["sha256"]:
                raise SystemExit("A/A copy is not byte-identical")
            for sc in sizes:
                n = n_for(k, targets[sc])
                iters, one = calibrate(ob["none"]["binary"], n, a.cpu)
                args = [n, iters]
                aa = pair(ob["none"]["binary"], copy, args, a.reps, a.cpu)
                kres["aa"][sc] = {"n": n, "iters": iters, "working_set_bytes": working_set(k, n), **aa}
                print(f"[aa] {k}.{sc} n={n} iters={iters} ratio {aa['ratio']:.4f} "
                      f"half-width {aa['half_width_pct']:.3f}%", flush=True)
                ref_ck = aa["a_checksums"]
                for v in variants:
                    vb = kres["variants"][v]["builds"]
                    t = time.time()
                    timing = {"n": n, "iters": iters}
                    if v == "orig":
                        p = pair(ob["none"]["binary"], vb["fast"]["binary"], args, a.reps, a.cpu)
                        pa = pair(ob["none_a64"]["binary"], vb["fast_a64"]["binary"], args, a.reps, a.cpu)
                        timing.update({"vs_original": p, "vs_own": "same as vs_original",
                                       "vs_original_aligned": pa, "vs_own_aligned": "same as vs_original_aligned"})
                        all_pairs = [p, pa]
                    else:
                        p = pair(ob["none"]["binary"], vb["fast"]["binary"], args, a.reps, a.cpu)
                        po = pair(vb["none"]["binary"], vb["fast"]["binary"], args, a.reps, a.cpu)
                        pa = pair(ob["none_a64"]["binary"], vb["fast_a64"]["binary"], args, a.reps, a.cpu)
                        poa = pair(vb["none_a64"]["binary"], vb["fast_a64"]["binary"], args, a.reps, a.cpu)
                        timing.update({"vs_original": p, "vs_own": po, "vs_original_aligned": pa,
                                       "vs_own_aligned": poa})
                        all_pairs = [p, po, pa, poa]
                    for pr in all_pairs:
                        if pr["a_checksums"] != ref_ck or pr["b_checksums"] != ref_ck:
                            raise SystemExit(f"{k}.{v}.{sc}: checksum differs from the original NONE build: "
                                             f"{pr['a_checksums']} {pr['b_checksums']} vs {ref_ck}")
                    timing["checksum_equals_original"] = True
                    timing["seconds"] = round(time.time() - t, 1)
                    kres["variants"][v].setdefault("timing", {})[sc] = timing
                    own = timing["vs_own_aligned"] if isinstance(timing["vs_own_aligned"], dict) else pa
                    print(f"[time] {k}.{v}.{sc}: fast/orig-none {p['ratio']:.3f} aligned {pa['ratio']:.3f} "
                          f"[{pa['ci95'][0]:.3f}, {pa['ci95'][1]:.3f}]  fast/own-none aligned {own['ratio']:.3f} "
                          f"{timing['seconds']}s", flush=True)
        for v in kres["variants"].values():
            for b in v["builds"].values():
                b["binary"] = rel(b["binary"])
        res["kernels"][k] = kres

    res["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(f"[done] {res['seconds']}s -> {rel(out_dir)}/results.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
