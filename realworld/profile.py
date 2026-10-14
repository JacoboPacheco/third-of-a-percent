#!/usr/bin/env python3
"""Probe and profile of every row (realworld/PLAN.md, "Profile weight of the lost loops").

Usage: python3 realworld/profile.py --bin <bin dir> --out <json> [--jobs N] <row> [<row> ...]

Per row:
- smoke: each timed build (none, fast, none_a64, fast_a64) run once natively with iters=1; the
  exact and rounded checksums of every build, and the NONE time per iteration only (used to size
  the workloads; no FAST time is recorded here).
- instructions: Cachegrind on the plain none and fast binaries with iters=1 and iters=2; the
  difference of the two totals is one workload iteration; FAST/NONE of that, labelled instructions.
- profile: Cachegrind with line-level counts on none_g and fast_g, the same two runs; per line the
  difference is one iteration; the shares of that iteration on the census lost loops' own lines
  and in the functions that contain them (common.shares).
"""
import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

VALGRIND = os.environ.get("RW_VALGRIND", "valgrind")


def load():
    with open(os.path.join(HERE, "programs.json"), encoding="utf-8") as f:
        return json.load(f)


def native(binary, args):
    t = time.time()
    r = subprocess.run([binary] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{os.path.basename(binary)} {args} exited {r.returncode}: {r.stderr[-800:]} {r.stdout[-400:]}")
    res = common.parse_result(r.stdout)
    res["wall_s"] = time.time() - t
    return res


def cachegrind(binary, args, outfile):
    cmd = [VALGRIND, "--tool=cachegrind", "--cache-sim=no", "--demangle=no", f"--cachegrind-out-file={outfile}",
           binary] + args
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(outfile):
        raise RuntimeError(f"valgrind {os.path.basename(binary)} exited {r.returncode}: {r.stderr[-800:]}")
    with open(outfile, encoding="utf-8", errors="replace") as f:
        counts, total = common.cachegrind_lines(f.read())
    return counts, total


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cg-dir", default=None)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("rows", nargs="+")
    a = ap.parse_args(argv)
    doc = load()
    rows = {r["row"]: r for r in doc["rows"]}
    cgdir = os.path.abspath(a.cg_dir or os.path.join(os.path.dirname(os.path.abspath(a.out)), "cachegrind"))
    os.makedirs(cgdir, exist_ok=True)
    binp = lambda prog, b: os.path.join(os.path.abspath(a.bin), f"{prog}.{b}")  # noqa: E731
    out = {"method": __doc__.split("\n\n", 2)[2].strip(), "rows": {}}

    # smoke first (fast, and a failure here should stop the run early)
    for name in a.rows:
        r = rows[name]
        sm = {}
        for b in ("none", "fast", "none_a64", "fast_a64"):
            if not os.path.exists(binp(r["program"], b)):
                continue  # built in another job (LightGBM's aligned pair); its checksums are checked when timed
            res = native(binp(r["program"], b), r["args"] + ["1"])
            sm[b] = {"checksum": res["checksum"], "checksum_r": res["checksum_r"]}
            if b == "none":
                sm[b]["ns_per_iteration"] = res["ns"]
                sm[b]["process_wall_s"] = round(res["wall_s"], 3)
        exact = len({v["checksum"] for v in sm.values()}) == 1
        rounded = len({v["checksum_r"] for v in sm.values()}) == 1
        out["rows"][name] = {"row": name, "program": r["program"], "args": r["args"], "smoke": sm,
                             "checksums_exact_match": exact, "checksums_rounded_match": rounded}
        print(f"[smoke] {name}: NONE {sm['none']['ns_per_iteration'] / 1e6:.1f} ms per iteration, process "
              f"{sm['none']['process_wall_s']:.2f} s; checksums exact {exact} rounded {rounded}", flush=True)

    # every valgrind run, in parallel
    jobs = []
    for name in a.rows:
        r = rows[name]
        for b in ("none", "fast", "none_g", "fast_g"):
            for it in (1, 2):
                jobs.append((name, b, it, binp(r["program"], b), r["args"] + [str(it)],
                             os.path.join(cgdir, f"{name}.{b}.i{it}.out")))
    t0 = time.time()
    res = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(cachegrind, j[3], j[4], j[5]): j for j in jobs}
        for fu in concurrent.futures.as_completed(futs):
            j = futs[fu]
            res[(j[0], j[1], j[2])] = fu.result()
    print(f"[cachegrind] {len(jobs)} runs in {time.time() - t0:.0f} s", flush=True)

    for name in a.rows:
        r = rows[name]
        loops = common.lost_loops_for(r["lost_project"])
        row = out["rows"][name]
        tot = {b: (res[(name, b, 2)][1] or 0) - (res[(name, b, 1)][1] or 0) for b in ("none", "fast")}
        row["instructions"] = {"none": tot["none"], "fast": tot["fast"],
                               "ratio": (tot["fast"] / tot["none"]) if tot["none"] > 0 else None,
                               "label": "Cachegrind instructions per workload iteration, not time"}
        row["lost_loops_listed"] = [f"{lp['file']}:{lp['line']} in {lp['function_name'] or lp['function']}"
                                    for lp in loops]
        row["profile"] = {}
        for b, label in (("none_g", "none"), ("fast_g", "fast")):
            it = common.iteration_counts(res[(name, b, 1)][0], res[(name, b, 2)][0])
            row["profile"][label] = common.shares(it, loops)
        p = row["profile"]
        fmt = lambda x: "-" if x is None else f"{100 * x:.3f}%"  # noqa: E731
        print(f"[profile] {name}: instr FAST/NONE {row['instructions']['ratio']}; lost-loop lines "
              f"{fmt(p['none']['loop_lines_share'])} (NONE) {fmt(p['fast']['loop_lines_share'])} (FAST); "
              f"containing functions {fmt(p['none']['functions_share'])} (NONE) "
              f"{fmt(p['fast']['functions_share'])} (FAST); functions matched "
              f"{p['none']['functions_matched']}/{p['none']['functions_listed']}", flush=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
