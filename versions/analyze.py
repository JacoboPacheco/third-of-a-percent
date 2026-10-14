#!/usr/bin/env python3
"""Per toolchain, per CPU model: does the loop-shape finding hold? (versions/PLAN.md, versions/criteria.json)

    python3 versions/analyze.py <matrix dir> [--baseline results/s4-pooled/pooled.json] --out analysis.json

<matrix dir> holds pooled-<N>.json (harness/pool.py output, one per version) and, optionally,
versions-<N>-*/toolchain.json (run_version.py). Needs only the standard library: every number is
read from the pooled files; nothing is recomputed from timings and no compiler is involved.
Rules are in criteria.json; the numeric thresholds are read from harness/criteria-v3.json.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
COLUMNS = ("as_compiled", "aligned")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_criteria():
    """(this column's criteria, v3 verdict numbers, problems). Problems: sha of criteria-v3 differs."""
    mine = load_json(os.path.join(HERE, "criteria.json"))
    path = os.path.join(REPO, mine["reference"]["file"])
    with open(path, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    v3 = json.loads(raw.decode("utf-8"))
    problems = [] if sha == mine["reference"]["sha256"] else [
        f"{mine['reference']['file']} sha256 {sha[:12]} differs from the one in versions/criteria.json"]
    return mine, v3, problems


def numbers(v3):
    v = v3["verdict"]
    return {"fwd_point": v["forward_point_max_ratio"], "fwd_floor": v["forward_ci_hi_floor_pct"] / 100.0,
            "fwd_mult": v["forward_ci_hi_aa_multiplier"], "lost_lo": v["lost_ci_lo_min_ratio"],
            "aa_max": v["aa_half_width_max_pct"], "min_jobs": v3["v3"]["pooling"]["minimum_jobs"]}


def forward_limit(aa_hw_pct, nums):
    return 1.0 + max(nums["fwd_floor"], nums["fwd_mult"] * aa_hw_pct / 100.0)


def cell_of(block, cell_id):
    return next((c for c in block["cells"] if c["cell_id"] == cell_id), None)


def kernel_holds(block, kernel, sizes, nums):
    """(holds, reason) for one judged kernel on one CPU model's pooled block."""
    cells = [cell_of(block, f"{kernel}.{s}") for s in sizes]
    if any(c is None for c in cells):
        return False, "cell missing"
    klass = {c["class"] for c in cells}
    if klass != {"lost"}:
        return False, "class " + "/".join(sorted(klass)) + " (not lost)"
    weak = [f"{c['cell_id']} {col} ci95_lo {c[col]['ci95'][0]:.3f}" for c in cells for col in COLUMNS
            if not c[col]["ci95"][0] >= nums["lost_lo"]]
    if weak:
        return False, "lost but below " + str(nums["lost_lo"]) + ": " + "; ".join(weak)
    return True, "lost, ci95_lo at least " + str(nums["lost_lo"]) + " in both columns at " + " and ".join(sizes)


def form_of(n_hold, n_judged):
    return "GENERALISES" if n_hold == n_judged else "DOES_NOT_GENERALISE" if n_hold == 0 else "PARTIAL"


def forward_cells(block, nums):
    aa = block["aa"]["half_width_pct"]
    lim = forward_limit(aa, nums)
    out = []
    for c in block["cells"]:
        if c["class"] != "kept" or c["size_class"] not in ("L1", "L2"):
            continue
        a = c["aligned"]
        out.append({"cell_id": c["cell_id"], "as_compiled": c["as_compiled"]["ratio"], "aligned": a["ratio"],
                    "aligned_ci95": a["ci95"], "limit": lim,
                    "passes": bool(a["ratio"] <= nums["fwd_point"] and a["ci95"][1] <= lim)})
    return out


def judge_cpu(block, mine, nums, probe=None):
    """The form of one CPU model on one toolchain, with every judged kernel's reason."""
    why_inc = []
    pv = block.get("verdict", {})
    if pv.get("form") == "inconclusive":
        why_inc.append("pooled verdict inconclusive: " + str(pv.get("why")))
    if block["jobs"] < nums["min_jobs"]:
        why_inc.append(f"{block['jobs']} jobs (minimum {nums['min_jobs']})")
    if block["aa"]["half_width_pct"] > nums["aa_max"]:
        why_inc.append(f"pooled A/A half-width {block['aa']['half_width_pct']:.2f}% above {nums['aa_max']}%")
    if probe is not None and not (probe.get("fast_traps") and probe.get("none_runs_clean")):
        why_inc.append("macro probe: FAST did not trap or NONE did not run clean")
    kernels = {}
    for k in mine["judged_kernels"]:
        holds, reason = kernel_holds(block, k, mine["sizes"], nums)
        kernels[k] = {"holds": holds, "reason": reason}
    n_hold = sum(1 for v in kernels.values() if v["holds"])
    form = "INCONCLUSIVE" if why_inc else form_of(n_hold, len(kernels))
    return {"form": form, "inconclusive_because": why_inc, "jobs": block["jobs"], "runs": block.get("runs", []),
            "aa_half_width_pct": block["aa"]["half_width_pct"], "kernels": kernels, "n_hold": n_hold,
            "forward": forward_cells(block, nums)}


def toolchain_form(cpu_forms):
    usable = {c: f for c, f in cpu_forms.items() if f != "INCONCLUSIVE"}
    if not usable:
        return "INCONCLUSIVE"
    forms = set(usable.values())
    return forms.pop() if len(forms) == 1 else "MIXED_BY_CPU_MODEL"


def vs_baseline(block, base_block):
    """Per cell: ratio on this toolchain divided by the clang 18 ratio on the same CPU model (points, as compiled)."""
    out = {}
    if base_block is None:
        return out
    for c in block["cells"]:
        b = cell_of(base_block, c["cell_id"])
        if b is None:
            continue
        out[c["cell_id"]] = {"this": c["as_compiled"]["ratio"], "clang18": b["as_compiled"]["ratio"],
                             "this_over_clang18": c["as_compiled"]["ratio"] / b["as_compiled"]["ratio"],
                             "class_this": c["class"], "class_clang18": b["class"]}
    return out


def analyse(pooled_by_version, baseline, toolchains=None, criteria=None):
    mine, v3, problems = criteria or load_criteria()
    nums = numbers(v3)
    toolchains = toolchains or {}
    base_cpus = {b["cpu_model"]: b for b in baseline["cpus"]} if baseline else {}
    doc = {"kind": "versions", "criteria_problems": problems, "baseline_file": mine["baseline"]["pooled_file"],
           "numbers_from_criteria_v3": nums, "versions": {}}
    for n in sorted(pooled_by_version, key=int):
        pooled = pooled_by_version[n]
        tc = toolchains.get(n, {})
        cpus = {}
        for b in pooled["cpus"]:
            j = judge_cpu(b, mine, nums, tc.get("probe"))
            j["cells"] = [{"cell_id": c["cell_id"], "class": c["class"], "as_compiled": c["as_compiled"]["ratio"],
                           "as_compiled_ci95": c["as_compiled"]["ci95"], "aligned": c["aligned"]["ratio"],
                           "aligned_ci95": c["aligned"]["ci95"]} for c in b["cells"]]
            j["vs_clang18"] = vs_baseline(b, base_cpus.get(b["cpu_model"]))
            j["in_clang18_pool"] = b["cpu_model"] in base_cpus
            cpus[b["cpu_model"]] = j
        doc["versions"][str(n)] = {"toolchain": tc, "form": toolchain_form({c: v["form"] for c, v in cpus.items()}),
                                   "cpus": cpus, "pooled_runs": sorted({r for b in pooled["cpus"] for r in b.get("runs", [])})}
    return doc


def report(doc):
    lines = ["Versions column (versions/PLAN.md). One pooled result per toolchain and CPU model; no number is dropped.",
             "Judged kernels: " + ", ".join(load_criteria()[0]["judged_kernels"]) + ".", ""]
    for p in doc["criteria_problems"]:
        lines.append("PROBLEM: " + p)
    for n, v in doc["versions"].items():
        tc = v["toolchain"]
        lines.append(f"== clang/libc++ {n}: {v['form']}   ({tc.get('clang') or 'toolchain not recorded'})")
        if tc.get("packages"):
            lines.append("   packages: " + ", ".join(f"{k} {x}" for k, x in tc["packages"].items()))
        pr = tc.get("probe")
        if pr:
            lines.append(f"   macro probe: NONE clean {pr.get('none_runs_clean')}, FAST traps {pr.get('fast_traps')} "
                         f"(exit codes {pr.get('none_exit')}/{pr.get('fast_exit')})")
        vec = tc.get("vectorization", {})
        for cpu, c in v["cpus"].items():
            lines.append(f"-- {cpu}: {c['form']}  ({c['jobs']} jobs, {len(c['runs'])} run(s), A/A half-width {c['aa_half_width_pct']:.3f}%)")
            for why in c["inconclusive_because"]:
                lines.append("   inconclusive: " + why)
            for k, r in c["kernels"].items():
                lines.append(f"   {k}: {'HOLDS' if r['holds'] else 'does not hold'} - {r['reason']}")
            lines.append("   cell            class     FAST/NONE as compiled [CI]     aligned     this/clang18")
            for x in c["cells"]:
                vb = c["vs_clang18"].get(x["cell_id"])
                lines.append(f"   {x['cell_id']:<16}{x['class']:<10}{x['as_compiled']:.3f} [{x['as_compiled_ci95'][0]:.3f}, "
                             f"{x['as_compiled_ci95'][1]:.3f}]   {x['aligned']:.3f}   "
                             + (f"{vb['this_over_clang18']:.2f} (18: {vb['clang18']:.3f}, class18 {vb['class_clang18']})" if vb
                                else "no clang 18 pool for this CPU model"))
            for f in c["forward"]:
                lines.append(f"   forward {f['cell_id']}: aligned {f['aligned']:.3f} ci_hi {f['aligned_ci95'][1]:.3f} "
                             f"limit {f['limit']:.3f} -> {'passes' if f['passes'] else 'does not pass'} (description only)")
        if vec:
            lines.append("   vectorization (remarks, first job): " + "; ".join(
                f"{k} none {'w' + str(x['none']['width']) if x['none']['vectorized'] else ('no' if x['none']['vectorized'] is False else '?')}"
                f" fast {'w' + str(x['fast']['width']) if x['fast']['vectorized'] else ('no' if x['fast']['vectorized'] is False else '?')}"
                for k, x in sorted(vec.items())))
        lines.append("")
    return "\n".join(lines)


def load_matrix(matrix):
    pooled, tcs = {}, {}
    for p in glob.glob(os.path.join(matrix, "pooled-*.json")):
        m = re.fullmatch(r"pooled-(\d+)\.json", os.path.basename(p))
        if m:
            pooled[m.group(1)] = load_json(p)
    for p in sorted(glob.glob(os.path.join(matrix, "versions-*", "toolchain.json"))):
        m = re.match(r"versions-(\d+)-", os.path.basename(os.path.dirname(p)))
        if m and m.group(1) not in tcs:
            tcs[m.group(1)] = load_json(p)
    return pooled, tcs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("matrix")
    ap.add_argument("--baseline", default=os.path.join(REPO, "results", "s4-pooled", "pooled.json"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    pooled, tcs = load_matrix(a.matrix)
    if not pooled:
        print("no pooled-<N>.json in", a.matrix)
        return 1
    base = load_json(a.baseline) if os.path.exists(a.baseline) else None
    doc = analyse(pooled, base, tcs)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1)
    print(report(doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
