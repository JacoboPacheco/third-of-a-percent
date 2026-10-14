#!/usr/bin/env python3
"""Writes results/fixture.json: MADE-UP numbers in the exact shape of results.json schema 1.

The page is built against this file before a real run lands; it carries "sample": true so the
page prints SAMPLE DATA. The samples are drawn from a seeded generator around invented true
ratios, then summarized with harness/stats.py and judged with harness/verdict.py, so the file is
internally consistent and scripts/check.py can recompute every number in it.
Usage: python scripts/make_fixture.py
"""
import hashlib
import json
import os
import random
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "harness"))

import schema  # noqa: E402
import stats  # noqa: E402
import verdict  # noqa: E402

rng = random.Random(7)

# kernel: (vectorized NONE, width NONE, vectorized FAST, width FAST, traps FAST, invented true ratio L1/L2/RAM, NOVEC ratio)
KERNELS = {
    "k01_sum_fwd": (True, 2, True, 2, 0, (1.000, 1.000, 1.004), 1.09),
    "k02_add_fwd": (True, 4, True, 4, 1, (0.995, 0.990, 1.010), 2.6),
    "k03_stencil": (True, 4, True, 4, 1, (1.003, 1.004, 0.985), 2.4),
    "k04_rev": (True, 4, False, None, 1, (5.4, 5.7, 1.65), 3.0),
    "k05_stride2": (True, 4, False, None, 1, (2.8, 2.9, 1.35), 1.6),
    "k06_gather": (False, None, False, None, 3, (1.15, 1.10, 1.02), None),
    "k07_hist": (False, None, False, None, 1, (1.20, 1.18, 1.05), None),
    "k08_matmul": (True, 4, True, 4, 2, (1.010, 1.006, None), 2.2),
}
NS_PER_BYTE = {"L1": 0.02, "L2": 0.025, "RAM": 0.06}
WS = {"L1": 24576, "L2": 524288, "RAM": 134217728}


def fake_sha(text):
    return hashlib.sha256(("SAMPLE " + text).encode()).hexdigest()


def samples(base_ns, noise=0.004):
    out = []
    for _ in range(20):
        x = base_ns * (1 + rng.gauss(0, noise))
        if rng.random() < 0.1:
            x *= 1 + rng.uniform(0.05, 0.2)  # an occasional slow outlier, as on a shared runner
        out.append(round(x, 3))
    return out


def main():
    cells, positive = [], []
    for k, (vn, wn, vf, wf, traps, ratios, novec) in KERNELS.items():
        for sc, r in zip(("L1", "L2", "RAM"), ratios):
            if r is None:
                continue
            cid = f"{k}.{sc}"
            base = WS[sc] * NS_PER_BYTE[sc]
            none_ns, fast_ns = samples(base), samples(base * r)
            s = stats.summarize(none_ns, fast_ns)
            if vn and sc != "RAM":
                nv = stats.summarize(samples(base), samples(base * novec))
                positive.append({"cell_id": cid, "novec_ratio": nv["ratio"], "ci95": nv["ci95"]})
            instr = None
            if sc == "L1":
                ir_none = WS[sc] // 4 * (1 if vn else 3)
                ir_fast = int(ir_none * (r * 1.4 if not vf and vn else 1.0 + 0.002 * traps))
                instr = {"none": ir_none, "fast": ir_fast, "ratio": ir_fast / ir_none}
            cells.append({
                "cell_id": cid, "kernel": k, "size_class": sc, "working_set_bytes": WS[sc],
                "none_sha256": fake_sha(k + "none"), "fast_sha256": fake_sha(k + "fast"), "checksum_match": True,
                "vectorized_none": {"vectorized": vn, "width": wn}, "vectorized_fast": {"vectorized": vf, "width": wf},
                "traps_none": 0, "traps_fast": traps, "none_ns": none_ns, "fast_ns": fast_ns,
                "ratio": s["ratio"], "ci95": s["ci95"], "instr": instr,
                "command": (f"clang++-18 -O2 -std=c++20 -stdlib=libc++ -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE "
                            f"-o build/{k}.none kernels/{k}.cpp\n"
                            f"clang++-18 -O2 -std=c++20 -stdlib=libc++ -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST "
                            f"-o build/{k}.fast kernels/{k}.cpp\n"
                            f"taskset -c 1 build/{k}.none 6144 1000\ntaskset -c 1 build/{k}.fast 6144 1000  (SAMPLE)"),
                "asm_diff_path": f"results/asm/{cid}.diff"})
    aa = stats.summarize(samples(3000.0), samples(3000.0))
    cls = verdict.classes(cells)
    with open(os.path.join(REPO, "harness", "criteria.json"), "rb") as f:
        crit_sha = hashlib.sha256(f.read()).hexdigest()
    pn_line = [{"source": "SAMPLE ENTRY, not a real figure", "figure": "0.00%", "url": "https://example.com/sample",
                "verified": True}]
    doc = {
        "schema": 1, "sample": True,
        "run": {"id": "sample", "commit": None, "workflow_run_url": None, "started_at": "2026-10-11T00:00:00Z",
                "runner": {"os": "Ubuntu 24.04 LTS (SAMPLE)", "kernel": "6.8.0 (SAMPLE)", "arch": "x86_64",
                           "cpu_model": "SAMPLE CPU", "cores": 2, "l1d_kib": 48, "l2_kib": 1024, "l3_kib": 32768},
                "toolchain": {"clang": "Ubuntu clang version 18.1.3 (SAMPLE)", "libcxx_package": "libc++-18-dev (SAMPLE)"},
                "flags": {"common": "-O2 -std=c++20 -stdlib=libc++",
                          "none": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE",
                          "fast": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST",
                          "novec": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE -fno-vectorize"},
                "criteria_sha256": crit_sha},
        "controls": {"aa": {"ratio": aa["ratio"], "ci95": aa["ci95"], "half_width_pct": aa["half_width_pct"],
                            "n_per_side": 20, "binary_sha256": fake_sha("k02_add_fwd" + "none")},
                     "negative": [c["cell_id"] for c in cells if c["kernel"] in cls["kept"] and c["size_class"] != "RAM"],
                     "positive": positive},
        "cells": cells,
        "programs": [],
        "verdict": None,
        "prior_numbers": pn_line,
    }
    for name, r in (("json_parse", 0.996), ("fmt_format", 1.004)):
        none_ns, fast_ns = samples(2.0e6, 0.006), samples(2.0e6 * r, 0.006)
        s = stats.summarize(none_ns, fast_ns)
        doc["programs"].append({
            "name": name, "pin": "SAMPLE pin", "input_sha256": fake_sha(name + "input"),
            "none_sha256": fake_sha(name + "none"), "fast_sha256": fake_sha(name + "fast"),
            "traps_none": 0, "traps_fast": 25 if name == "json_parse" else 7, "ratio": s["ratio"], "ci95": s["ci95"],
            "aa_half_width_pct": 1.1, "consistent_with_at_most_pct": max(0.0, 100 * (s["ci95"][1] - 1)),
            "none_ns": none_ns, "fast_ns": fast_ns, "instr": None})
    doc["verdict"] = verdict.compute(doc)
    schema.validate(doc)
    path = os.path.join(REPO, "results", "fixture.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print(f"wrote {path}: verdict {doc['verdict']['form']}: {doc['verdict']['line']}")


if __name__ == "__main__":
    main()
