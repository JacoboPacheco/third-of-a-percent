#!/usr/bin/env python3
"""Times every k02 variant built by build.sh, interleaved, and writes one JSON file per runner.

Each round runs every (variant, size, allocation) configuration once, in an order shuffled with a
fixed seed per round, pinned to CPU 1; ROUNDS rounds. Reported per configuration: the median and
minimum ns per call, and the address of a, b, c mod 4096 for the probe builds.
Usage: python3 bench.py <build dir> <out.json> [rounds]
"""
import json
import os
import random
import statistics
import subprocess
import sys

BUILD, OUT = sys.argv[1], sys.argv[2]
ROUNDS = int(sys.argv[3]) if len(sys.argv) > 3 else 15
CPU = os.environ.get("BENCH_CPU", "1")

# n: 1365 = the L1 cell on a 32 KiB L1d runner (EPYC 9V74 / 7763), 2048 = the L1 cell on the 48 KiB
# L1d runner (EPYC 9V45), 43690 = the L2 cell on all three. iters keep each process near 50 ms.
SIZES = [(1365, 300000), (2048, 250000), (43690, 10000)]
PLAIN = ["none", "fast", "none_a64", "fast_a64", "none_il1", "fast_il2"]
PROBE = ["probe_none", "probe_fast"]
ALLOCS = {"natural": None, "offs_0_0_0": "0,0,0", "offs_0_16_32": "0,16,32",
          "offs_0_64_128": "0,64,128", "offs_0_1376_2752": "0,1376,2752", "offs_0_2048_1024": "0,2048,1024"}

configs = []
for n, it in SIZES:
    for v in PLAIN:
        configs.append({"variant": v, "alloc": "natural", "n": n, "iters": it, "env": None})
    for v in PROBE:
        for name, offs in ALLOCS.items():
            configs.append({"variant": v, "alloc": name, "n": n, "iters": it, "env": offs})


def run(c):
    env = dict(os.environ)
    env.pop("PROBE_OFFS", None)
    if c["env"]:
        env["PROBE_OFFS"] = c["env"]
    r = subprocess.run(["taskset", "-c", CPU, os.path.join(BUILD, c["variant"]), str(c["n"]), str(c["iters"])],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return None, None, r.stderr[-300:]
    d = dict(kv.split("=", 1) for kv in r.stdout.split())
    addrs = {k: int(d[k]) for k in ("a", "b", "c") if k in d}
    return float(d["ns"]), d["checksum"], addrs


samples = {i: [] for i in range(len(configs))}
meta = {i: {} for i in range(len(configs))}
for rnd in range(ROUNDS):
    order = list(range(len(configs)))
    random.Random(1000 + rnd).shuffle(order)
    for i in order:
        ns, ck, extra = run(configs[i])
        if ns is None:
            meta[i]["error"] = extra
            continue
        samples[i].append(ns)
        meta[i]["checksum"] = ck
        if extra:
            meta[i]["addr_mod4096"] = extra

rows = []
for i, c in enumerate(configs):
    s = samples[i]
    rows.append({"variant": c["variant"], "alloc": c["alloc"], "n": c["n"], "iters": c["iters"],
                 "median_ns": statistics.median(s) if s else None, "min_ns": min(s) if s else None,
                 "reps": len(s), "ns": s, **meta[i]})

cpu = "?"
for ln in open("/proc/cpuinfo"):
    if ln.startswith("model name"):
        cpu = ln.split(":", 1)[1].strip()
        break
json.dump({"cpu": cpu, "rounds": ROUNDS, "pinned_cpu": CPU, "rows": rows}, open(OUT, "w"), indent=1)

# a short table in the log
med = {(r["variant"], r["alloc"], r["n"]): r["median_ns"] for r in rows}
print(f"CPU: {cpu}")
for n, _ in SIZES:
    def ratio(a, b):
        x, y = med.get((a, "natural", n)), med.get((b, "natural", n))
        return f"{x / y:.3f}" if x and y else "?"
    print(f"n={n}: fast/none {ratio('fast', 'none')}  fast_a64/none_a64 {ratio('fast_a64', 'none_a64')}  "
          f"fast_il2/none {ratio('fast_il2', 'none')}  fast/none_il1 {ratio('fast', 'none_il1')}  "
          f"fast_a64/fast {ratio('fast_a64', 'fast')}  none_a64/none {ratio('none_a64', 'none')}")
    for v in ["none", "fast", "none_a64", "fast_a64", "none_il1", "fast_il2"]:
        print(f"   {v:10s} {med.get((v, 'natural', n)) or 0:10.1f} ns")
    for v in PROBE:
        print("   " + v + ": " + "  ".join(f"{a}={med.get((v, a, n)) or 0:.1f}" for a in ALLOCS))
