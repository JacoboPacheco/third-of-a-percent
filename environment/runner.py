#!/usr/bin/env python3
"""One job of the environment column: time the harness's eight kernels NONE vs FAST while sampling the machine.

    python3 environment/runner.py --out out --job 3

Reuses harness/run.py unchanged (imported): build_kernel, n_for, caches, calibrate, run_bin and the pinning
(`taskset -c <cpu>`). The only new thing is the loop around run_bin, which is the harness's `pair` with
a /proc/stat snapshot before and after each process and a frequency reading after it. Writes
<out>/environment.json (facts, per-process samples, per-cell checksum check).
Nothing here looks at a ratio to decide anything.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, HERE)

import envlib  # noqa: E402
import run  # noqa: E402  (harness/run.py, unchanged)

SIZES = ("L1", "L2")
CPU_BASE = "/sys/devices/system/cpu"


def snapshot(pinned):
    """/proc/stat, the pinned vCPU's MHz (cpuinfo and cpufreq), the CPU the driver last ran on."""
    st = envlib.parse_proc_stat(envlib.read_text("/proc/stat") or "")
    mhz = envlib.mhz_of(envlib.read_text("/proc/cpuinfo") or "", pinned)
    sf = envlib.read_text(f"{CPU_BASE}/cpu{pinned}/cpufreq/scaling_cur_freq")
    try:
        sf = int(sf) / 1000.0 if sf is not None else None
    except ValueError:
        sf = None
    try:
        dc = envlib.driver_cpu(envlib.read_text("/proc/self/stat") or "")
    except (ValueError, IndexError):
        dc = None
    return st, mhz, sf, dc


def timed(binary, args, pinned, cpu):
    before, _, _, _ = snapshot(pinned)
    ns, ck = run.run_bin(binary, args, cpu)
    after, mhz, sf, dc = snapshot(pinned)
    d_pin = envlib.stat_delta(before[f"cpu{pinned}"], after[f"cpu{pinned}"])
    d_all = envlib.stat_delta(before["cpu"], after["cpu"])
    return {"ns": ns, "checksum": ck, "steal": d_pin["steal"], "iowait": d_pin["iowait"], "total": d_pin["total"],
            "steal_all": d_all["steal"], "total_all": d_all["total"], "mhz": mhz, "scaling_cur_mhz": sf,
            "driver_cpu": dc}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(REPO, "out"))
    ap.add_argument("--build", default=os.path.join(REPO, "build", "environment"))
    ap.add_argument("--reps", type=int, default=20, help="processes per side per cell")
    ap.add_argument("--cpu", default=os.environ.get("HARNESS_CPU", "1"))
    ap.add_argument("--job", default="0")
    ap.add_argument("--kernels", default="all")
    a = ap.parse_args(argv)
    pinned = int(a.cpu)
    out_dir, build_dir = os.path.abspath(a.out), os.path.abspath(a.build)
    for d in (out_dir, build_dir, os.path.join(out_dir, "asm"), os.path.join(out_dir, "remarks")):
        os.makedirs(d, exist_ok=True)
    kernels = run.ALL_KERNELS if a.kernels == "all" else [k.strip() for k in a.kernels.split(",")]

    cache = run.caches()
    runner, lscpu = run.runner_info(cache)
    targets = {"L1": cache["l1d"] // 2, "L2": cache["l2"] // 2}
    facts = envlib.job_facts(pinned)
    facts.update({"job": a.job, "lscpu": lscpu, "runner": runner, "pinned_cpu": pinned, "reps_per_side": a.reps,
                  "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    sib = envlib.parse_cpu_list((facts["topology"].get(str(pinned)) or {}).get("thread_siblings_list") or "")
    print(f"[runner] cpu_model: {runner['cpu_model']} cores {runner['cores']} online {facts['online']} "
          f"siblings of vCPU {pinned}: {sib}  cgroup cpu.max {facts['cgroup_cpu_max']}", flush=True)

    built = {k: run.build_kernel(k, build_dir, out_dir) for k in kernels}
    samples, cells, idx = [], [], 0
    for k in kernels:
        b = built[k]["builds"]
        for sc in SIZES:
            n = run.n_for(k, targets[sc])
            iters, _ = run.calibrate(b["none"]["binary"], n, a.cpu)
            cid = f"{k}.{sc}"
            order, cks = [], {"none": set(), "fast": set()}
            for rep in range(a.reps):
                for side in (("none", "fast") if rep % 2 == 0 else ("fast", "none")):  # ABBA, as harness `pair`
                    s = timed(b[side]["binary"], [n, iters], pinned, a.cpu)
                    cks[side].add(s.pop("checksum"))
                    s.update({"i": idx, "cell": cid, "side": side, "rep": rep})
                    samples.append(s)
                    order.append("A" if side == "none" else "B")
                    idx += 1
            cells.append({"cell_id": cid, "n": n, "iters": iters, "order": "".join(order),
                          "checksum_match": len(cks["none"]) == 1 and cks["none"] == cks["fast"]})
            print(f"[cell] {cid} done, checksum_match {cells[-1]['checksum_match']}", flush=True)
    facts["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    facts["cpuinfo_mhz_after"] = [b["cpu MHz"] for b in envlib.parse_cpuinfo(envlib.read_text("/proc/cpuinfo") or "")]
    doc = {"schema": 1, "job": a.job, "cpu_model": runner["cpu_model"], "facts": facts, "cells": cells,
           "samples": samples}
    with open(os.path.join(out_dir, "environment.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f)
    print(f"[done] {len(samples)} timed processes -> {os.path.join(out_dir, 'environment.json')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
