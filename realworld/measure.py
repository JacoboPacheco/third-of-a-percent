#!/usr/bin/env python3
"""Times every row on one runner (one Actions job), realworld/PLAN.md "Timing".

Usage: python3 realworld/measure.py --bin <bin dir> --out <results-job.json> [--reps 40] [--cpu 1]
                                    [--pairs fast,aa,aligned,layout] <row> [<row> ...]

Per row: iterations calibrated on the NONE binary to about TARGET_NS of timed work per process; then
ABBA pairs of `reps` processes per side, one process per repetition, pinned with taskset:
  fast    = NONE (A) against FAST (B)
  aa      = NONE (A) against a byte-identical copy of NONE (B); aborts if the sha256 differ
  aligned = NONE -falign-loops=64 (A) against FAST -falign-loops=64 (B)
  layout  = NONE (A) against NONE -falign-loops=64 (B)
For every process: the in-binary time per iteration (primary) and the process wall time measured
here (secondary), and its checksums.
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
sys.path.insert(0, HERE)
import common  # noqa: E402

TARGET_NS = 200e6
MAX_ITERS = 1000
PAIRS = {"fast": ("none", "fast"), "aa": ("none", "none_copy"), "aligned": ("none_a64", "fast_a64"),
         "layout": ("none", "none_a64")}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_once(binary, args, cpu):
    t = time.perf_counter_ns()
    r = subprocess.run(["taskset", "-c", cpu, binary] + args, capture_output=True, text=True)
    wall = time.perf_counter_ns() - t
    if r.returncode != 0:
        raise RuntimeError(f"{os.path.basename(binary)} {args} exited {r.returncode}: {r.stderr[-600:]}")
    res = common.parse_result(r.stdout)
    res["wall_ns"] = float(wall)
    return res


def pair(a_bin, b_bin, args, reps, cpu):
    """ABBA: A B B A A B B A ..., `reps` processes per side."""
    s = {"a_ns": [], "b_ns": [], "a_wall_ns": [], "b_wall_ns": [], "a_ck": set(), "b_ck": set(),
         "a_ckr": set(), "b_ckr": set()}
    order = []
    for k in range(reps):
        for side in (("a", "b") if k % 2 == 0 else ("b", "a")):
            res = run_once(a_bin if side == "a" else b_bin, args, cpu)
            s[f"{side}_ns"].append(res["ns"])
            s[f"{side}_wall_ns"].append(res["wall_ns"])
            s[f"{side}_ck"].add(res["checksum"])
            s[f"{side}_ckr"].add(res["checksum_r"])
            order.append(side.upper())
    exact = len(s["a_ck"]) == 1 and s["a_ck"] == s["b_ck"]
    rounded = len(s["a_ckr"]) == 1 and s["a_ckr"] == s["b_ckr"]
    return {"a_ns": s["a_ns"], "b_ns": s["b_ns"], "a_wall_ns": s["a_wall_ns"], "b_wall_ns": s["b_wall_ns"],
            "a_checksums": sorted(s["a_ck"]), "b_checksums": sorted(s["b_ck"]),
            "checksum_exact_match": exact, "checksum_rounded_match": rounded, "order": "".join(order)}


def runner_info():
    lscpu = subprocess.run(["lscpu"], capture_output=True, text=True).stdout
    m = re.search(r"Model name:\s*(.*)", lscpu)
    return {"cpu_model": m.group(1).strip() if m else None, "cores": os.cpu_count(),
            "kernel": subprocess.run(["uname", "-r"], capture_output=True, text=True).stdout.strip() or None}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--cpu", default="1")
    ap.add_argument("--pairs", default="fast,aa,aligned,layout")
    ap.add_argument("--job", default=None)
    ap.add_argument("rows", nargs="+")
    a = ap.parse_args(argv)
    pairs = [p.strip() for p in a.pairs.split(",") if p.strip()]
    for p in pairs:
        if p not in PAIRS:
            raise SystemExit(f"unknown pair {p}")
    with open(os.path.join(HERE, "programs.json"), encoding="utf-8") as f:
        doc = json.load(f)
    rows = {r["row"]: r for r in doc["rows"]}
    bindir = os.path.abspath(a.bin)
    runner = runner_info()
    print(f"[runner] {runner['cpu_model']} ({runner['cores']} cores)", flush=True)
    server, repo, run_id = (os.environ.get(x) for x in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"))
    out = {"kind": "realworld-job", "schema": 1, "sample": False,
           "run": {"id": run_id or "local", "job": a.job, "commit": os.environ.get("GITHUB_SHA"),
                   "workflow_run_url": f"{server}/{repo}/actions/runs/{run_id}" if run_id else None,
                   "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "runner": runner,
                   "reps_per_side": a.reps, "pinned_cpu": a.cpu, "target_ns_per_process": TARGET_NS,
                   "pairs": {p: {"a": PAIRS[p][0], "b": PAIRS[p][1]} for p in pairs}},
           "rows": []}
    t_all = time.time()
    for name in a.rows:
        r = rows[name]
        prog = r["program"]
        binp = lambda b: os.path.join(bindir, f"{prog}.{b}")  # noqa: E731
        copy = binp("none_copy")
        if not os.path.exists(copy):
            shutil.copyfile(binp("none"), copy)
            shutil.copymode(binp("none"), copy)
        shas = {b: sha256(binp(b)) for b in ("none", "fast", "none_a64", "fast_a64", "none_copy")}
        if shas["none"] != shas["none_copy"]:
            raise SystemExit(f"{name}: the A/A copy is not byte-identical")
        t = time.time()
        best = min(run_once(binp("none"), r["args"] + ["1"], a.cpu)["ns"] for _ in range(3))
        iters = max(1, min(MAX_ITERS, int(round(TARGET_NS / best))))
        args = r["args"] + [str(iters)]
        row = {"row": name, "program": prog, "args": r["args"], "iters": iters, "calibration_ns_one_iter": best,
               "sha256": shas, "pairs": {}}
        for p in pairs:
            ab, bb = PAIRS[p]
            pr = pair(binp(ab), binp(bb), args, a.reps, a.cpu)
            row["pairs"][p] = pr
            ra = sorted(pr["b_ns"])[len(pr["b_ns"]) // 2] / sorted(pr["a_ns"])[len(pr["a_ns"]) // 2]
            print(f"[time] {name} {p}: {bb}/{ab} about {ra:.4f} (upper medians, this job only) checksums "
                  f"exact {pr['checksum_exact_match']} rounded {pr['checksum_rounded_match']}", flush=True)
        row["seconds"] = round(time.time() - t, 1)
        print(f"[row] {name}: iters {iters}, {row['seconds']} s", flush=True)
        out["rows"].append(row)
    out["run"]["seconds"] = round(time.time() - t_all, 1)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"[done] {out['run']['seconds']} s -> {a.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
