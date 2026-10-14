#!/usr/bin/env python3
"""The layout sweep runner (rules: layout-sweep/PLAN.md; numbers: layout-sweep/criteria.json).

Builds kernels k01, k02, k03, k04 NONE and FAST at 16 placements (4 * NN bytes of filler before the
kernel function, layout-sweep/wrap.cpp) plus the harness's own two layouts (ref, a64), checks from the
disassembly that the hot loop really moved, then times every placement NONE against FAST (ABBA,
pinned) at the L1 and L2 sizes, with a byte-identical A/A per cell. Writes <out>/results.json (kind
"layout-sweep"), <out>/asm/. Run on an ubuntu-24.04 x64 runner with clang-18 and libc++-18-dev.

  python3 layout-sweep/sweep.py --job 1 --out out
  python3 layout-sweep/sweep.py --job 1 --kernels k02_add_fwd --sizes L1 --pads 0,5,15 --reps 4 --out out  # smoke
"""
import argparse
import concurrent.futures as cf
import json
import os
import random
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, HERE)

import analyze as an  # noqa: E402
import asm  # noqa: E402
import placement  # noqa: E402
import pool  # noqa: E402
import remarks  # noqa: E402
import run as hr  # noqa: E402  (harness/run.py: unchanged, reused for sizes, calibration and ABBA timing)
import stats  # noqa: E402


def sweep_cmd(kernel, mode, pad_bytes, flags, out):
    return ([hr.CXX] + hr.COMMON + hr.FLAGS[mode] + flags + hr.REMARK_FLAGS
            + [f'-DKERNEL_SRC="kernels/{kernel}.cpp"', f"-DPAD_BYTES={pad_bytes}", "-I", ".",
               "-o", out, "layout-sweep/wrap.cpp"])


def inspect(binary, kernel, stderr, src, line):
    """Facts about kern_<kernel> in a built binary, from objdump and clang's remarks."""
    dump = hr.sh([hr.OBJDUMP, "-d", "--no-show-raw-insn", binary]).stdout
    lines = asm.function_lines(dump, "kern_" + kernel)
    if not lines:
        raise SystemExit(f"kern_{kernel} not found in the objdump of {binary}")
    hot = pool.hot_loop(placement.loops(lines))
    info = {"sha256": hr.sha256(binary), "fn_addr": int(lines[0].split()[0], 16),
            "hot": None, "vectorized": remarks.vectorization(stderr, src, line)["vectorized"],
            "traps": asm.count_traps(lines)}
    if hot:
        info["hot"] = {"start": int(hot["start"], 16), "start_mod64": hot["start_mod64"], "bytes": hot["bytes"],
                       "windows64": hot["windows64"], "min_windows64": hot["min_windows64"],
                       "extra_window": hot["extra_window"], "crosses64": hot["crosses64"], "simd": hot["simd"]}
    return info, lines


def build(kernel, mode, pad_id, pad_bytes, flags, build_dir):
    """One binary. pad_id 'ref' and 'a64' are the harness's own builds (no wrapper, no sweep flags)."""
    out = os.path.join(build_dir, f"{kernel}.{pad_id}.{mode}")
    if pad_id == "ref":
        cmd = hr.compile_cmd(kernel, mode, out)
    elif pad_id == "a64":
        cmd = hr.compile_cmd(kernel, mode + "_a64", out)
    else:
        cmd = sweep_cmd(kernel, mode, pad_bytes, flags, out)
    r = hr.sh(cmd)
    if r.returncode != 0:
        raise SystemExit(f"build failed {kernel} {pad_id} {mode}:\n{' '.join(cmd)}\n{r.stderr[-3000:]}")
    src = f"kernels/{kernel}.cpp"
    with open(os.path.join(REPO, src), encoding="utf-8") as f:
        line = remarks.loop_line(f.read())
    info, lines = inspect(out, kernel, r.stderr, src, line)
    info["command"] = " ".join(cmd)
    return {"kernel": kernel, "mode": mode, "pad_id": pad_id, "binary": out, "info": info, "lines": lines,
            "loop_line": line}


def probe_mechanism(crit, build_dir):
    """Best placement mechanism, from addresses only (no timing): mode fine (4-byte steps) with the first
    loop-alignment variant that moves k02 FAST's function and hot loop by exactly the pad; else mode
    coarse (16-byte steps, compiler-default alignment) if that moves them by exactly the pad at 16, 32, 48.
    Returns (mode, flags, attempts) or (None, None, attempts)."""
    attempts = []
    plans = [("fine", f, (0, 4, 12)) for f in crit["design"]["loop_alignment_variants_in_order"]]
    plans.append(("coarse", crit["modes"]["coarse"]["flags"], (0, 16, 32, 48)))
    for mode, flags, sizes in plans:
        pts, err = [], None
        for nb in sizes:
            try:
                b = build("k02_add_fwd", "fast", f"probe{nb}", nb, flags, build_dir)
            except SystemExit as e:  # a variant the compiler rejects is just a failed variant
                err = str(e).splitlines()[0]
                break
            hot = b["info"]["hot"]
            if hot is None:
                err = "no hot loop"
                break
            pts.append((nb, b["info"]["fn_addr"], hot["start"]))
        ok = err is None and an.probe_ok(pts)
        attempts.append({"mode": mode, "flags": flags, "points": pts, "error": err, "ok": ok})
        print(f"[probe] {mode} {' '.join(flags)}: {'OK' if ok else 'no'} {pts} {err or ''}", flush=True)
        if ok:
            return mode, flags, attempts
    return None, None, attempts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--job", default="0")
    ap.add_argument("--kernels", default=",".join(an.load_criteria()[0]["design"]["kernels"]))
    ap.add_argument("--sizes", default=",".join(an.load_criteria()[0]["design"]["sizes"]))
    ap.add_argument("--pads", default="all", help="all, or comma-separated pad numbers 0..15 (smoke tests only)")
    ap.add_argument("--no-refs", action="store_true")
    ap.add_argument("--reps", type=int, default=None)
    ap.add_argument("--out", default=os.path.join(REPO, "layout-sweep", "out"))
    ap.add_argument("--build", default=os.path.join(REPO, "build", "layout-sweep"))
    ap.add_argument("--cpu", default=os.environ.get("HARNESS_CPU", "1"))
    ap.add_argument("--workers", type=int, default=max(1, os.cpu_count() or 1))
    a = ap.parse_args(argv)
    crit, crit_sha = an.load_criteria()
    design = crit["design"]
    reps = a.reps or design["reps_per_side"]
    kernels = [k.strip() for k in a.kernels.split(",") if k.strip()]
    sizes = [s.strip() for s in a.sizes.split(",") if s.strip()]
    smoke = a.pads != "all" or reps != design["reps_per_side"] or a.no_refs
    refs = [] if a.no_refs else an.REFS
    out_dir, build_dir = os.path.abspath(a.out), os.path.abspath(a.build)
    for d in (out_dir, os.path.join(out_dir, "asm"), build_dir):
        os.makedirs(d, exist_ok=True)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    cache = hr.caches()
    runner, lscpu = hr.runner_info(cache)
    print(f"[runner] {runner['cpu_model']}  cores {runner['cores']}  L1d {runner['l1d_kib']} KiB  L2 {runner['l2_kib']} KiB", flush=True)
    targets = {"L1": cache["l1d"] // 2, "L2": cache["l2"] // 2}

    # 1. the mechanism, from addresses, before any timing
    mode, flags, attempts = probe_mechanism(crit, build_dir)
    if mode is None:
        raise SystemExit("no mechanism moves the hot loop by the pad (4-byte or 16-byte steps); nothing timed (see the [probe] lines)")
    cfg = an.mode_cfg(crit, mode)
    step = cfg["step"]
    all_pads = an.pad_ids(cfg["placements"])
    pads = all_pads if a.pads == "all" else [f"p{int(x):02d}" for x in a.pads.split(",") if int(x) < len(all_pads)]
    mech = {"mode": mode, "step_bytes": step, "placements": cfg["placements"], "flags": flags, "probe": attempts}
    print(f"[mechanism] mode {mode}: {cfg['placements']} placements, {step}-byte steps, flags {flags}", flush=True)

    # 2. every binary
    tasks = [(k, m, p, (an.pad_bytes(p, step) if p in all_pads else None))
             for k in kernels for p in pads + refs for m in ("none", "fast")]
    t0 = time.time()
    built = {}
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(build, k, m, p, pb, flags, build_dir): (k, m, p) for k, m, p, pb in tasks}
        for fu in cf.as_completed(futs):
            b = fu.result()
            built[(b["kernel"], b["mode"], b["pad_id"])] = b
    print(f"[build] {len(built)} binaries in {time.time() - t0:.0f}s", flush=True)
    builds = {}
    for k in kernels:
        pl = {}
        for p in pads + refs:
            pl[p] = {"pad_bytes": an.pad_bytes(p, step) if p in all_pads else None}
            for m in ("none", "fast"):
                b = built[(k, m, p)]
                pl[p][m] = b["info"]
                with open(os.path.join(out_dir, "asm", f"{k}.{p}.{m}.s"), "w", encoding="utf-8") as f:
                    f.write("\n".join(b["lines"]) + "\n")
        builds[k] = {"loop_line": built[(k, "none", pads[0])]["loop_line"], "placements": pl}
        if not smoke:
            problems = an.check_mechanism(pl, cfg)
            if problems:
                raise SystemExit(f"{k}: placement mechanism not verified, nothing timed:\n  " + "\n  ".join(problems))
        print(f"[placement] {k}: FAST hot-loop start mod 64 by pad: "
              f"{[pl[p]['fast']['hot']['start_mod64'] if pl[p]['fast']['hot'] else None for p in pads]}", flush=True)

    # 3. timing
    job = str(a.job)
    cells = []
    for k in kernels:
        for sc in sizes:
            cid = f"{k}.{sc}"
            n = hr.n_for(k, targets[sc])
            nb0 = built[(k, "none", pads[0])]["binary"]
            iters, one = hr.calibrate(nb0, n, a.cpu)
            order = pads + refs + ["aa"]
            random.Random(f"layout-sweep|{job}|{cid}").shuffle(order)
            cell = {"cell_id": cid, "kernel": k, "size_class": sc, "n": n, "iters": iters,
                    "ns_per_call_calibration": one, "order": order, "placements": {}}
            copy = os.path.join(build_dir, f"{k}.aa_copy")
            shutil.copyfile(nb0, copy)
            shutil.copymode(nb0, copy)
            if hr.sha256(copy) != built[(k, "none", pads[0])]["info"]["sha256"]:
                raise SystemExit("A/A copy is not byte-identical")
            for tag in order:
                if tag == "aa":
                    pr = hr.pair(nb0, copy, [n, iters], reps, a.cpu)
                    cell["aa"] = {"a_ns": pr["a_ns"], "b_ns": pr["b_ns"], "checksum_match": pr["checksum_match"],
                                  "order": pr["order"], "half_width_pct": stats.summarize(pr["a_ns"], pr["b_ns"])["half_width_pct"]}
                    continue
                pr = hr.pair(built[(k, "none", tag)]["binary"], built[(k, "fast", tag)]["binary"], [n, iters], reps, a.cpu)
                lo, hi = stats.bootstrap_ratio_ci(pr["a_ns"], pr["b_ns"], resamples=design["per_job_resamples"])
                cell["placements"][tag] = {"none_ns": pr["a_ns"], "fast_ns": pr["b_ns"],
                                           "checksum_match": pr["checksum_match"], "order": pr["order"],
                                           "ratio": stats.ratio_of_medians(pr["a_ns"], pr["b_ns"]), "ci95": [lo, hi]}
            ordered = {p: cell["placements"][p] for p in pads + refs}
            cell["placements"] = ordered
            r = ", ".join(f"{p}:{ordered[p]['ratio']:.2f}" for p in pads)
            print(f"[cell] {cid} n={n} iters={iters} A/A hw {cell['aa']['half_width_pct']:.2f}%  FAST/NONE {r}", flush=True)
            cells.append(cell)

    doc = {"kind": "layout-sweep", "schema": 1, "smoke": smoke, "criteria_sha256": crit_sha,
           "run": {"id": os.environ.get("GITHUB_RUN_ID", "local"), "job": job, "started": started,
                   "runner": runner, "toolchain": hr.toolchain(), "lscpu": lscpu},
           "mechanism": mech, "reps_per_side": reps, "pinned_cpu": a.cpu,
           "size_targets_bytes": targets, "builds": builds, "cells": cells}
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print(f"[done] {os.path.join(out_dir, 'results.json')} in {time.time() - t0:.0f}s since the build", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
