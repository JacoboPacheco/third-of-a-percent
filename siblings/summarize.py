#!/usr/bin/env python3
"""Reads every siblings.json of one run and prints the tables of siblings/README.md.

Usage: python siblings/summarize.py results/siblings-run-<id> [more run dirs ...] [> table.md]
Writes summary.json (the same numbers, machine-readable) into the run dir when given one dir, or into
siblings/summary.json when given several (the jobs of all the runs pooled per CPU model).

Rules (fixed before the full run was read):
- A job's cells for a toolchain are used only when that toolchain's A/A half-width in that job is at
  most 2.0 % (the project's aa_half_width_max_pct, harness/criteria-v2.json). Excluded jobs are listed.
- The headline is the aligned pair (-falign-loops=64 on both sides). Per CPU model: the median of the
  usable jobs' ratios, then in brackets the lowest interval bound and the highest interval bound over
  those jobs, then the number of jobs. With one job the brackets are that job's 95 % interval.
- "lost" = the compiler reports the marked loop vectorized in the unhardened build and not in the
  hardened build (the classifier of harness/verdict.py, applied to the sibling's own remarks).
"""
import glob
import json
import os
import statistics
import sys

AA_MAX = 2.0
REFERENCE = "clang18-fast"
ORDER = ["clang18-fast", "clang18-extensive", "clang18-debug", "clang18v3-fast",
         "gcc14-O2-assert", "gcc14-O3-assert"]
SHORT = {"AMD EPYC 7763 64-Core Processor": "EPYC 7763", "AMD EPYC 9V74 80-Core Processor": "EPYC 9V74",
         "INTEL(R) XEON(R) PLATINUM 8573C": "Xeon Platinum 8573C"}


def short(cpu):
    if cpu in SHORT:
        return SHORT[cpu]
    return cpu.replace("Intel(R) Xeon(R) ", "Xeon ").replace(" CPU", "").replace(" Processor", "") \
        .replace("AMD ", "").replace(" 64-Core", "").replace(" 96-Core", "").replace(" 80-Core", "")


def vec_str(v):
    if v["vectorized"] is True:
        return f"yes (w{v['width']})" if v.get("width") else f"yes ({v['vector_bytes']} B)"
    return "no" if v["vectorized"] is False else "no remark"


def main(dirs):
    docs = []
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "*", "siblings.json"))):
            with open(p, encoding="utf-8") as f:
                x = json.load(f)
            x["_file"] = (os.path.relpath(p, os.path.dirname(os.path.normpath(d))) if len(dirs) > 1
                          else os.path.relpath(p, d)).replace("\\", "/")
            docs.append(x)
    if not docs:
        raise SystemExit(f"no siblings.json under {dirs}")
    cpus = sorted({short(x["runner"]["cpu_model"]) for x in docs})
    variants = sorted({c["variant"] for x in docs for c in x["cells"]},
                      key=lambda v: (ORDER.index(v) if v in ORDER else 99, v))
    excluded, jobs = [], []
    usable = {}  # (variant, kernel, size, cpu) -> [cells]
    builds = {}  # variant -> kernel -> set of (vec_none, vec_hard, traps_none, traps_hard, hard sha)
    for x in docs:
        cpu = short(x["runner"]["cpu_model"])
        jobs.append({"file": x["_file"], "part": x["part"], "cpu": x["runner"]["cpu_model"],
                     "aa_half_width_pct": {t: round(a["half_width_pct"], 3) for t, a in x["aa"].items()},
                     "layout_aa": {t: [round(a["ratio"], 4), round(a["half_width_pct"], 3)]
                                   for t, a in x["layout_aa"].items()},
                     "skipped": x["skipped"], "seconds": x["seconds"]})
        for t, a in x["aa"].items():
            if a["half_width_pct"] > AA_MAX:
                excluded.append(f"{x['_file']} {t} (A/A half-width {a['half_width_pct']:.2f}%)")
        for c in x["cells"]:
            builds.setdefault(c["variant"], {}).setdefault(c["kernel"], set()).add(
                (c["vectorized_none"]["vectorized"], c["vectorized_hard"]["vectorized"],
                 c["traps_none"], c["traps_hard"], c["hard_sha256"]))
            if x["aa"][c["toolchain"]]["half_width_pct"] > AA_MAX or not c["checksum_ok"]:
                continue
            usable.setdefault((c["variant"], c["kernel"], c["size_class"], cpu), []).append(c)

    # classification per variant, from the remarks (identical across jobs: same compiler, same source)
    first = {}
    for x in docs:
        for c in x["cells"]:
            first.setdefault((c["variant"], c["kernel"]), c)
    lost = {}
    for v in variants:
        lost[v] = sorted(k for (vv, k), c in first.items() if vv == v and c["vectorized_none"]["vectorized"] is True
                         and c["vectorized_hard"]["vectorized"] is not True)
    out = []
    out.append(f"Jobs read: {len(docs)} ({', '.join(sorted({j['cpu'] for j in jobs}))}).  ")
    out.append("Excluded (A/A half-width above 2%): " + ("; ".join(excluded) if excluded else "none") + ".\n")
    out.append("### Which loops lose vectorization\n")
    out.append("| variant | compiler | lost (vectorized unhardened, not hardened) | same set as the reference? |")
    out.append("|---|---|---|---|")
    for v in variants:
        tc = next(c["toolchain"] for (vv, k), c in first.items() if vv == v)
        ver = next(x["toolchains"][tc]["version"] for x in docs if tc in x["toolchains"])
        same = "reference" if v == REFERENCE else ("yes" if lost[v] == lost.get(REFERENCE) else "**no**")
        out.append(f"| {v} | {ver} | {', '.join(lost[v]) or 'none'} | {same} |")
    for size in ("L1", "L2"):
        out.append(f"\n### Aligned hardened/unhardened ratio, {size} size\n")
        out.append("Per CPU model: median of the usable jobs' ratios [lowest 95% bound, highest 95% bound] x jobs.\n")
        out.append("| variant | kernel | vectorized unhardened | vectorized hardened | traps | " +
                   " | ".join(cpus) + " |")
        out.append("|---|---|---|---|---|" + "---|" * len(cpus))
        for v in variants:
            for k in sorted({k for (vv, k) in first if vv == v}):
                c0 = first[(v, k)]
                cols = []
                for cpu in cpus:
                    cs = usable.get((v, k, size, cpu), [])
                    if not cs:
                        cols.append("-")
                        continue
                    r = statistics.median(c["aligned"]["ratio"] for c in cs)
                    lo = min(c["aligned"]["ci95"][0] for c in cs)
                    hi = max(c["aligned"]["ci95"][1] for c in cs)
                    cols.append(f"{r:.2f} [{lo:.2f}, {hi:.2f}] x{len(cs)}")
                out.append(f"| {v} | {k} | {vec_str(c0['vectorized_none'])} | {vec_str(c0['vectorized_hard'])} | "
                           f"{c0['traps_none']} -> {c0['traps_hard']} | " + " | ".join(cols) + " |")
    out.append("\n### Controls per job\n")
    out.append("| file | A/A half-width per toolchain | layout A/A (ratio, half-width) |\n|---|---|---|")
    for j in jobs:
        out.append(f"| {j['file']} | " + ", ".join(f"{t} {h:.2f}%" for t, h in j["aa_half_width_pct"].items()) +
                   " | " + ", ".join(f"{t} {r:.3f} / {h:.2f}%" for t, (r, h) in j["layout_aa"].items()) + " |")
    skipped = [f"{j['file']}: {s['what']} ({s['why']})" for j in jobs for s in j["skipped"]]
    out.append("\nSkipped: " + ("; ".join(skipped) if skipped else "nothing") + ".")
    incons = [f"{v} {k}" for v, ks in builds.items() for k, s in ks.items() if len({t[:4] for t in s}) > 1]
    out.append("Build records that differ between jobs (vectorization or traps): " + (", ".join(incons) or "none") + ".")

    # remarks for every loop whose classification differs from the reference
    ref = set(lost.get(REFERENCE, []))
    diffs = []
    for v in variants:
        if v == REFERENCE:
            continue
        for k in sorted(set(lost[v]) ^ ref):
            x = next(x for x in docs if any(c["variant"] == v for c in x["cells"]))
            tc = first[(v, k)]["toolchain"]
            b = x["builds"][tc][k]
            diffs.append({"variant": v, "kernel": k, "lost_here": k in lost[v], "lost_in_reference": k in ref,
                          "remarks_unhardened": b["none"]["vectorization"]["remarks"][:4],
                          "remarks_hardened": b[v]["vectorization"]["remarks"][:4]})
    if diffs:
        out.append("\n### Where the lost set differs from the reference, the compiler's own words\n")
        for df in diffs:
            out.append(f"- **{df['variant']} {df['kernel']}** (lost here: {df['lost_here']}, lost in reference: "
                       f"{df['lost_in_reference']}). Unhardened: `{' / '.join(df['remarks_unhardened']) or 'no remark'}`. "
                       f"Hardened: `{' / '.join(df['remarks_hardened']) or 'no remark'}`.")
    print("\n".join(out))
    summary = {"jobs": jobs, "excluded": excluded, "lost": lost, "cpus": cpus, "differs_from_reference": diffs,
               "cells": {f"{v}|{k}|{s}|{cpu}": [{"job_file_part": c["variant"], "ratio": c["aligned"]["ratio"],
                                                 "ci95": c["aligned"]["ci95"], "as_compiled": c["as_compiled"]["ratio"]}
                                                for c in cs] for (v, k, s, cpu), cs in usable.items()}}
    target = os.path.join(dirs[0], "summary.json") if len(dirs) == 1 else os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "summary.json")
    with open(target, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
