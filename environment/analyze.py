#!/usr/bin/env python3
"""Analysis of the environment column, per CPU model (rules: environment/PLAN.md, fixed before any run).

    python3 environment/analyze.py <dir with **/environment.json> [--out analysis.json]

Per CPU model: steal share per job (median / max over jobs), iowait share, share of processes that saw steal;
frequency (median MHz of the first vs the second half of a job's processes, and of its NONE vs FAST
processes; "constant" when every reading is the same value); whether the pinned vCPU is a hyperthread sibling of
the driver's vCPU; online CPUs and cgroup cpu.max; then the FAST/NONE ratio of every cell with all processes
and without steal-affected processes (harness/stats.py), and whether any cell's verdict MOVES.
Descriptive. Nothing here edits the page.
"""
import argparse
import glob
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, HERE)

import envlib  # noqa: E402
import stats  # noqa: E402

# fixed in PLAN.md
STEAL_LARGE_SHARE = 0.005       # job steal share above 0.5 %
DRIFT_LARGE_PCT = 1.0           # relative MHz difference above 1 %
MIN_LEFT_PER_SIDE = 10
LOST_KERNELS = ("k04_rev", "k05_stride2", "k08_matmul")
FORWARD_KERNELS = ("k01_sum_fwd", "k02_add_fwd", "k03_stencil")
LOST_CI_LO_MIN = 1.5            # harness/criteria-v3.json verdict.lost_ci_lo_min_ratio
FORWARD_POINT_MAX = 1.02        # harness/criteria-v3.json verdict.forward_point_max_ratio


def med(v):
    return statistics.median(v) if v else None


def rel_pct(a, b):
    """(b - a) / a in percent; None when a is missing or zero."""
    if a is None or b is None or a == 0:
        return None
    return (b - a) / a * 100.0


def load_matrix(path):
    docs = []
    for p in sorted(glob.glob(os.path.join(path, "**", "environment.json"), recursive=True)):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        d["_path"] = os.path.relpath(p, path).replace("\\", "/")
        docs.append(d)
    return docs


def mhz_series(samples):
    """(values, source): scaling_cur_freq when every process has it, else cpuinfo 'cpu MHz', else (None, None)."""
    sf = [s.get("scaling_cur_mhz") for s in samples]
    if samples and all(v is not None for v in sf):
        return sf, "scaling_cur_freq"
    ci = [s.get("mhz") for s in samples]
    if samples and all(v is not None for v in ci):
        return ci, "cpuinfo"
    return None, None


def job_summary(doc):
    samples = sorted(doc["samples"], key=lambda s: s["i"])
    facts = doc["facts"]
    tot = sum(s["total"] for s in samples)
    steal = sum(s["steal"] for s in samples)
    io = sum(s["iowait"] for s in samples)
    steal_share = steal / tot if tot else None
    affected = sum(1 for s in samples if s["steal"] >= 1)
    out = {"job": doc.get("job"), "path": doc.get("_path"), "n_processes": len(samples),
           "steal_share": steal_share, "iowait_share": io / tot if tot else None,
           "processes_with_steal": affected,
           "steal_large": steal_share is not None and steal_share > STEAL_LARGE_SHARE}
    vals, src = mhz_series(samples)
    if vals is None:
        out["mhz"] = {"source": None}
    else:
        h = len(vals) // 2
        first, second = vals[:h], vals[h:]
        none_v = [v for v, s in zip(vals, samples) if s["side"] == "none"]
        fast_v = [v for v, s in zip(vals, samples) if s["side"] == "fast"]
        constant = len(set(vals)) == 1
        half = rel_pct(med(first), med(second))
        side = rel_pct(med(none_v), med(fast_v))
        out["mhz"] = {"source": src, "median": med(vals), "min": min(vals), "max": max(vals), "constant": constant,
                      "first_half_median": med(first), "second_half_median": med(second), "half_drift_pct": half,
                      "none_median": med(none_v), "fast_median": med(fast_v), "side_drift_pct": side,
                      "drift_large": any(x is not None and abs(x) > DRIFT_LARGE_PCT for x in (half, side))}
    sib = envlib.parse_cpu_list((facts.get("topology", {}).get(str(facts.get("pinned_cpu"))) or {})
                                .get("thread_siblings_list") or "")
    drivers = sorted({s["driver_cpu"] for s in samples if s.get("driver_cpu") is not None})
    pinned = facts.get("pinned_cpu")
    out["topology"] = {"pinned": pinned, "pinned_siblings": sib, "driver_cpus_seen": drivers,
                       "shares_core_with_driver": any(envlib.shares_core(pinned, d, sib) for d in drivers),
                       "driver_on_pinned_vcpu": pinned in drivers}
    cg = facts.get("cgroup_cpu_max")
    out["online"] = facts.get("online")
    out["cgroup_cpus"] = cg.get("cpus") if cg else None
    out["cgroup_cpu_max_present"] = cg is not None
    out["governor"] = facts.get("cpufreq", {}).get("scaling_governor")
    out["boost_files"] = {k: v for k, v in facts.get("cpufreq", {}).items() if "boost" in k or "turbo" in k}
    out["kernel"] = facts.get("kernel")
    out["checksums_ok"] = all(c.get("checksum_match") for c in doc.get("cells", []))
    out["job_large"] = out["steal_large"] or bool(out["mhz"].get("drift_large"))
    return out


def classify(kernel, ratio, ci):
    if kernel in LOST_KERNELS:
        return "lost-holds" if ci[0] >= LOST_CI_LO_MIN else "lost-fails"
    if kernel in FORWARD_KERNELS:
        return "forward-passes" if ratio <= FORWARD_POINT_MAX else "forward-fails"
    return "reported"


def reestimate(docs):
    """Per cell, pooled over the jobs of one CPU model: all processes vs without steal-affected ones."""
    by_cell = {}
    for d in docs:
        for s in d["samples"]:
            by_cell.setdefault(s["cell"], []).append(s)
    rows = []
    for cid in sorted(by_cell):
        ss = by_cell[cid]
        kernel = cid.rsplit(".", 1)[0]
        none = [s["ns"] for s in ss if s["side"] == "none"]
        fast = [s["ns"] for s in ss if s["side"] == "fast"]
        full = stats.summarize(none, fast)
        keep = [s for s in ss if s["steal"] < 1]
        n_k = [s["ns"] for s in keep if s["side"] == "none"]
        f_k = [s["ns"] for s in keep if s["side"] == "fast"]
        row = {"cell_id": cid, "n_none": len(none), "n_fast": len(fast), "excluded": len(ss) - len(keep),
               "ratio": full["ratio"], "ci95": full["ci95"], "class": classify(kernel, full["ratio"], full["ci95"])}
        if row["excluded"] == 0:
            row.update({"ratio_wo_steal": full["ratio"], "ci95_wo_steal": full["ci95"], "class_wo_steal": row["class"],
                        "moves": False, "judged": True})
        elif min(len(n_k), len(f_k)) < MIN_LEFT_PER_SIDE:
            row.update({"ratio_wo_steal": None, "ci95_wo_steal": None, "class_wo_steal": None, "moves": None,
                        "judged": False})
        else:
            r = stats.summarize(n_k, f_k)
            cls = classify(kernel, r["ratio"], r["ci95"])
            outside = not (full["ci95"][0] <= r["ratio"] <= full["ci95"][1])
            row.update({"ratio_wo_steal": r["ratio"], "ci95_wo_steal": r["ci95"], "class_wo_steal": cls,
                        "moves": outside or cls != row["class"], "judged": True,
                        "moves_because": [x for x, f in (("point outside full interval", outside),
                                                         ("class flips", cls != row["class"])) if f]})
        rows.append(row)
    return rows


def model_summary(model, docs):
    jobs = [job_summary(d) for d in docs]
    shares = [j["steal_share"] for j in jobs if j["steal_share"] is not None]
    halves = [abs(j["mhz"]["half_drift_pct"]) for j in jobs if j["mhz"].get("half_drift_pct") is not None]
    sides = [abs(j["mhz"]["side_drift_pct"]) for j in jobs if j["mhz"].get("side_drift_pct") is not None]
    rows = reestimate(docs)
    moved = [r["cell_id"] for r in rows if r["moves"]]
    large_jobs = [j["job"] for j in jobs if j["job_large"]]
    return {"cpu_model": model, "n_jobs": len(jobs), "jobs": jobs,
            "steal_share_median": med(shares), "steal_share_max": max(shares) if shares else None,
            "jobs_steal_large": sum(1 for j in jobs if j["steal_large"]),
            "mhz_constant_in_all_jobs": all(j["mhz"].get("constant") for j in jobs if j["mhz"].get("source")) and
                                        any(j["mhz"].get("source") for j in jobs),
            "mhz_sources": sorted({j["mhz"]["source"] for j in jobs if j["mhz"].get("source")}),
            "half_drift_abs_pct_median": med(halves), "half_drift_abs_pct_max": max(halves) if halves else None,
            "side_drift_abs_pct_median": med(sides), "side_drift_abs_pct_max": max(sides) if sides else None,
            "jobs_drift_large": sum(1 for j in jobs if j["mhz"].get("drift_large")),
            "jobs_sharing_core_with_driver": sum(1 for j in jobs if j["topology"]["shares_core_with_driver"]),
            "jobs_driver_on_pinned_vcpu": sum(1 for j in jobs if j["topology"]["driver_on_pinned_vcpu"]),
            "jobs_with_cgroup_cpu_max": sum(1 for j in jobs if j["cgroup_cpu_max_present"]),
            "cells": rows, "cells_moved": moved, "large_jobs": large_jobs,
            "page_text_may_change": bool(large_jobs) and bool(moved)}


def analyse(docs):
    by_model = {}
    for d in docs:
        by_model.setdefault(d.get("cpu_model") or "unknown", []).append(d)
    models = [model_summary(m, ds) for m, ds in sorted(by_model.items())]
    return {"schema": 1, "plan": "environment/PLAN.md", "n_jobs": len(docs),
            "thresholds": {"steal_large_share": STEAL_LARGE_SHARE, "drift_large_pct": DRIFT_LARGE_PCT,
                           "min_left_per_side": MIN_LEFT_PER_SIDE},
            "models": models, "page_text_may_change": any(m["page_text_may_change"] for m in models)}


def pct(x, digits=3):
    return "n/a" if x is None else f"{x * 100:.{digits}f}%"


def fnum(x, d=2):
    return "n/a" if x is None else f"{x:.{d}f}"


def report(an):
    L = [f"Environment column: {an['n_jobs']} jobs, {len(an['models'])} CPU model(s). Descriptive; rules in environment/PLAN.md."]
    for m in an["models"]:
        L += ["", f"== {m['cpu_model']}  ({m['n_jobs']} jobs)",
              f"steal share of the pinned vCPU: median {pct(m['steal_share_median'])}, max {pct(m['steal_share_max'])}; "
              f"jobs above 0.5%: {m['jobs_steal_large']}",
              f"frequency ({', '.join(m['mhz_sources']) or 'no reading'}): "
              + ("every reading constant in every job (a VM may report a nominal value; not evidence of no drift)"
                 if m["mhz_constant_in_all_jobs"] else
                 f"first-vs-second-half |drift| median {fnum(m['half_drift_abs_pct_median'])}% max {fnum(m['half_drift_abs_pct_max'])}%; "
                 f"NONE-vs-FAST |drift| median {fnum(m['side_drift_abs_pct_median'])}% max {fnum(m['side_drift_abs_pct_max'])}%")
              + f"; jobs above 1%: {m['jobs_drift_large']}",
              f"pinned vCPU shares a core with the driver in {m['jobs_sharing_core_with_driver']} of {m['n_jobs']} jobs "
              f"(driver itself on the pinned vCPU in {m['jobs_driver_on_pinned_vcpu']}); "
              f"cgroup cpu.max present in {m['jobs_with_cgroup_cpu_max']}",
              "FAST/NONE per cell, all processes -> without steal-affected processes:"]
        for r in m["cells"]:
            lo, hi = r["ci95"]
            if r["excluded"] == 0:
                tail = "no steal-affected process, unchanged"
            elif not r["judged"]:
                tail = f"{r['excluded']} excluded, too few left, not judged"
            else:
                lo2, hi2 = r["ci95_wo_steal"]
                tail = (f"{r['ratio_wo_steal']:.3f} [{lo2:.3f}, {hi2:.3f}] ({r['excluded']} excluded)"
                        + ("  MOVES: " + ", ".join(r["moves_because"]) if r["moves"] else ""))
            L.append(f"  {r['cell_id']:<18} {r['ratio']:.3f} [{lo:.3f}, {hi:.3f}] {r['class']:<14} -> {tail}")
        L.append(f"cells that move: {', '.join(m['cells_moved']) or 'none'}; jobs with a LARGE finding: "
                 f"{', '.join(str(j) for j in m['large_jobs']) or 'none'}")
        L.append("page text may change (LARGE finding AND a moved cell): " + ("YES, to be decided by the project owner" if m["page_text_may_change"] else "no"))
    L += ["", "Overall: " + ("a limits line about the environment may be warranted (see models above)."
                              if an["page_text_may_change"] else
                              "nothing in the environment was large enough to move a reported verdict; no page change."),
          "Not shown: bursts inside a process, jiffy-resolution steal, causes. Correlation only."]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    docs = load_matrix(a.dir)
    if not docs:
        print("no environment.json found under", a.dir)
        return 1
    an = analyse(docs)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(an, f, indent=1)
    print(report(an))
    return 0


if __name__ == "__main__":
    sys.exit(main())
