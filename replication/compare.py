#!/usr/bin/env python3
"""The replication sets beside the pools they replicate (replication/PLAN.md, written before the runs).

    python replication/compare.py            write replication/results.json
    python replication/compare.py --verify   recompute it from the pooled files and fail on any difference with the stored file

Standard library only. Every number in replication/results.json is read or computed here from six pooled.json files
(each produced by the unchanged harness/pool.py under the unchanged harness/criteria-v3.json) and from the criteria
file; none is typed. The six files, and the comparison each pair makes:

    Arm (Neoverse-N2)      earlier results/s8-arm-pooled        set A, 30 jobs        (the pool the page's Arm column reads)
                           replication results/s9-arm-b-pooled  set B, 30 jobs, pooled alone
                           secondary results/s9-arm-ab-pooled   sets A and B pooled together
    x86-64                 earlier results/s7-pooled            the first pool, 95 jobs (the pool the page reads)
                           replication results/s9-x86-c-pooled  set C, 40 jobs, pooled alone
                           secondary results/s9-x86-ac-pooled   the first pool and set C pooled together

What is computed, per CPU model (a model is "testable" when it has at least v3.pooling.minimum_jobs jobs in both the
earlier pool and the replication set; a pooled statistic of fewer jobs is shown with its job count and never decides anything):
  - the verdict form of each of the three pools and, for a form that is not MAP, the cause: the cells the stored `why`
    names, re-derived here from the stored cells with the rules of harness/pool.py (the result must rebuild the stored
    sentence exactly, or the build stops);
  - how many of the replication set's in-cache points (the pooled ratio of each cell, as compiled and with loops
    aligned) lie inside the 95% interval of the same cell in the earlier pool. This is the definition of
    harness/pool.py reproduction() (the share the page shows for runs of one pool), applied to the replication set as the
    point and the earlier pool as the interval. Each miss carries its gap to the interval, as reproduction() defines it
    (percent of the point), and the relative difference of the two pooled ratios;
  - for the named cells: the Arm cell that decides the earlier Arm verdict, and for each model whose verdict word changed,
    the cells that cause the non-MAP side, with their placement statistic and whether the written rule judged or exempted
    each cell in each pool;
  - the lost-SIMD range (the page's headline) of each x86-64 pool against the range the page prints, from the earlier pool;
  - the models that cannot be tested, with what the secondary pooled form says about them.

The secondary pooled forms are secondary because the sets were requested after a borderline reading, so the stopping
point depended on the data (replication/PLAN.md, item 3). They are shown and never replace the separate sets.
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = "replication/results.json"
PLAN = "replication/PLAN.md"
CRITERIA = "harness/criteria-v3.json"
SCHEMA = "replication-1"
IN_CACHE = ("L1", "L2")
COLUMNS = ("as_compiled", "aligned")
ROLES = ("earlier", "replication", "secondary")

# arch -> role -> pooled file (the files named in the module docstring)
POOLS = {
    "arm": {"earlier": "results/s8-arm-pooled/pooled.json", "replication": "results/s9-arm-b-pooled/pooled.json",
            "secondary": "results/s9-arm-ab-pooled/pooled.json"},
    "x86": {"earlier": "results/s7-pooled/pooled.json", "replication": "results/s9-x86-c-pooled/pooled.json",
            "secondary": "results/s9-x86-ac-pooled/pooled.json"},
}
# The names the plan gives its sets and the two questions it asks (replication/PLAN.md; tests/test_replication.py checks the words)
SET_NAMES = {"arm": {"earlier": "set A", "replication": "set B", "secondary": "sets A and B"},
             "x86": {"earlier": "the first pool", "replication": "set C", "secondary": "the first pool and set C"}}
PLAN_MODEL_X86 = "Intel(R) Xeon(R) 6973P-C"      # plan question 2: the Xeon 6973P-C borderline MAP
# The matrix-multiply cells the Arm section prints beside the cell that decides its verdict (arm64/README.md): context, not a plan question
ARM_CONTEXT_CELLS = ("k08_matmul.L1", "k08_matmul.L2")
# how a stored `why` that is not a mixed picture starts (harness/pool.py cpu_verdict) -> the kind written here
WHY_KINDS = (("too few jobs", "too_few_jobs"), ("A/A control", "aa_noise"), ("checksum control", "checksum"),
             ("build control", "build"), ("layout control", "layout"), ("positive control", "positive_control"),
             ("negative control", "negative_control"), ("mixed picture", "mixed"))
TOP_DIFFS = 3


# ---------------------------------------------------------------- files

def lf_sha(path):
    """sha256 with CRLF read as LF: a Windows checkout and a Linux clone give the same value."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- one pooled block

def forward_limit(block):
    """The forward limit of a pool's block, as harness/pool.py writes it: 1 + max(2%, 2 x the pooled A/A half-width)."""
    return 1.0 + block["verdict"]["forward_limit_pct"] / 100.0


def exempt_ids(block):
    """The in-cache cells the written rule left out of the forward test as placement-sensitive."""
    return {p["cell_id"] for p in block["verdict"]["placement_sensitive"]}


def in_cache_cells(block):
    return [c for c in block["cells"] if c["size_class"] in IN_CACHE]


def cell_of(block, cell_id):
    return next((c for c in block["cells"] if c["cell_id"] == cell_id), None)


def block_of(doc, cpu_model):
    return next((b for b in doc["cpus"] if b["cpu_model"] == cpu_model), None)


def judged_forward(block):
    """The forward cells the verdict tests: kept-SIMD, in cache, not placement-sensitive (harness/pool.py cpu_verdict)."""
    ps = exempt_ids(block)
    return [c for c in in_cache_cells(block) if c["class"] == "kept" and c["cell_id"] not in ps]


def rebuild_mixed_why(block, crit):
    """The sentence harness/pool.py cpu_verdict writes for a mixed picture, rebuilt from the stored cells.
    Returns (sentence, forward_missed cells, lost_missed [(cell, column label)], cells above the limit [(cell, label)])."""
    vc = crit["verdict"]
    limit = forward_limit(block)
    cache = in_cache_cells(block)
    ps = exempt_ids(block)
    fwd = judged_forward(block)
    lost = [c for c in cache if c["class"] == "lost"]
    fwd_fail = [c for c in fwd if not (c["aligned"]["ratio"] <= vc["forward_point_max_ratio"]
                                       and c["aligned"]["ci95"][1] <= limit)]
    cols = (("", "as_compiled"), (" (aligned)", "aligned"))
    lost_fail = [(c, lab) for c in lost for lab, key in cols if not c[key]["ci95"][0] >= vc["lost_ci_lo_min_ratio"]]
    axis = [c for c in cache if c["class"] in ("kept", "lost") and c["cell_id"] not in ps]
    above = [(c, lab) for c in axis for lab, key in cols if c[key]["ci95"][0] > limit]
    reasons = []
    if not fwd:
        reasons.append("no forward cell left after the placement-sensitive exclusions")
    if fwd_fail:
        reasons.append("forward rule (aligned) missed by " + ", ".join(c["cell_id"] for c in fwd_fail))
    if lost_fail:
        reasons.append("lost-vectorization minimum missed by " + ", ".join(c["cell_id"] + lab for c, lab in lost_fail))
    if not any(c["class"] == "lost" for c in block["cells"]):
        reasons.append("no kernel lost vectorization")
    if above:
        reasons.append("cells above the forward limit: " + ", ".join(c["cell_id"] + lab for c, lab in above))
    return "mixed picture: " + "; ".join(reasons), fwd_fail, lost_fail, above


def derive_cause(block, crit):
    """None for a MAP (or holds-everywhere) verdict; otherwise what the stored `why` says, as data. A mixed picture is
    re-derived from the cells and must rebuild the stored sentence exactly; any other `why` is kept as a kind and its text."""
    v = block["verdict"]
    if v["form"] != "inconclusive":
        return None
    why = v["why"]
    kind = next((k for prefix, k in WHY_KINDS if why.startswith(prefix)), "other")
    out = {"kind": kind, "why": why}
    if kind != "mixed":
        return out
    sentence, fwd_fail, lost_fail, above = rebuild_mixed_why(block, crit)
    if sentence != why:
        raise ValueError(f"{block['cpu_model']}: the cause rebuilt from the cells ({sentence!r}) is not the stored why ({why!r})")
    limit = forward_limit(block)
    out["forward_missed"] = [{"cell_id": c["cell_id"], "aligned_ratio": c["aligned"]["ratio"], "aligned_ci95": c["aligned"]["ci95"],
                              "aligned_hi_over_limit": c["aligned"]["ci95"][1] - limit} for c in fwd_fail]
    out["lost_missed"] = [{"cell_id": c["cell_id"], "column": lab.strip(" ()") or "as_compiled"} for c, lab in lost_fail]
    out["above_limit_cells"] = len(above)
    out["no_judged_forward_cell"] = not judged_forward(block)
    return out


def closest_forward(block):
    """The judged forward cell nearest to the forward limit (the smallest limit minus the aligned upper end; negative when over):
    the cell the verdict hangs on. None without a judged forward cell."""
    limit = forward_limit(block)
    fwd = judged_forward(block)
    if not fwd:
        return None
    c = min(fwd, key=lambda x: (limit - x["aligned"]["ci95"][1], x["cell_id"]))
    return {"cell_id": c["cell_id"], "aligned_ratio": c["aligned"]["ratio"], "aligned_hi": c["aligned"]["ci95"][1],
            "limit": limit, "margin": limit - c["aligned"]["ci95"][1]}


def form_record(block, crit, minimum):
    """One pool's reading of one CPU model: jobs, verdict form, the cause of a form that is not MAP, the forward limit and
    the cell the verdict hangs on. Under the minimum number of jobs the form is still the stored one (inconclusive, too few
    jobs) and no closest cell is given."""
    v = block["verdict"]
    enough = block["jobs"] >= minimum
    return {"jobs": block["jobs"], "runs": len(block["runs"]), "enough": enough, "form": v["form"],
            "stability": block["stability"],
            "per_run": [{"run_id": r["run_id"], "jobs": r["jobs"], "form": r["form"]} for r in block["per_run"]],
            "aa_half_width_pct": v["aa_half_width_pct"],
            "forward_limit_pct": v["forward_limit_pct"], "placement_sensitive": sorted(exempt_ids(block)),
            "closest_forward": closest_forward(block) if enough else None, "cause": derive_cause(block, crit)}


def cell_record(block, cell_id, crit, minimum):
    """One cell of one pool: both columns, the class, the role in the verdict (judged forward cell, exempt as
    placement-sensitive, lost, other) and the placement statistic D with the two parts of the written rule.
    None when the pool did not draw the CPU model or lacks the cell."""
    c = cell_of(block, cell_id) if block else None
    if c is None:
        return None
    limit = forward_limit(block)
    ps = exempt_ids(block)
    cache = c["size_class"] in IN_CACHE
    if not cache:
        role = "not_in_cache"
    elif c["class"] == "kept":
        role = "exempt_placement_sensitive" if cell_id in ps else "judged_forward"
    else:
        role = c["class"]
    rec = {"cell_id": cell_id, "class": c["class"], "role": role, "jobs": block["jobs"], "enough": block["jobs"] >= minimum,
           "limit": limit, "form": block["verdict"]["form"],
           "as_compiled": {"ratio": c["as_compiled"]["ratio"], "ci95": c["as_compiled"]["ci95"]},
           "aligned": {"ratio": c["aligned"]["ratio"], "ci95": c["aligned"]["ci95"]},
           "aligned_hi_over_limit": c["aligned"]["ci95"][1] - limit,
           "passes_forward_rule": ((c["aligned"]["ratio"] <= crit["verdict"]["forward_point_max_ratio"]
                                    and c["aligned"]["ci95"][1] <= limit) if role == "judged_forward" else None),
           "placement": None}
    pl = c.get("placement")
    if pl:
        lo, hi = pl["d"]["ci95"]
        rec["placement"] = {"d": pl["d"]["ratio"], "d_ci95": pl["d"]["ci95"],
                            "d_misses_one_by": (1.0 - hi) if hi < 1.0 else (lo - 1.0) if lo > 1.0 else 0.0,
                            "statistical": pl["statistical"], "mechanical": pl["mechanical"], "sensitive": pl["sensitive"]}
    return rec


# ---------------------------------------------------------------- the points of one pool inside another's intervals

def inside_points(new_block, old_block):
    """Every in-cache cell of `new_block` present in `old_block`, both columns: the new pooled ratio against the old 95% interval.
    The test is harness/pool.py reproduction()'s (lo <= point <= hi) and gap_pct is its gap (percent of the point)."""
    old = {c["cell_id"]: c for c in in_cache_cells(old_block)}
    points = []
    for c in in_cache_cells(new_block):
        o = old.get(c["cell_id"])
        if o is None:
            continue
        for col in COLUMNS:
            pt = c[col]["ratio"]
            lo, hi = o[col]["ci95"]
            ok = lo <= pt <= hi
            gap = 0.0 if ok else (100.0 * (lo - pt) / pt if pt < lo else 100.0 * (pt - hi) / pt)
            points.append({"cell_id": c["cell_id"], "column": col, "new": pt, "earlier": o[col]["ratio"], "earlier_ci95": [lo, hi],
                           "inside": ok, "gap_pct": gap, "point_diff_pct": 100.0 * (pt / o[col]["ratio"] - 1.0)})
    return points


def inside_summary(points):
    misses = [p for p in points if not p["inside"]]
    by_diff = sorted(points, key=lambda p: (-abs(p["point_diff_pct"]), p["cell_id"], p["column"]))
    return {"checked": len(points), "inside": len(points) - len(misses), "outside": len(misses),
            "max_gap_pct": max((p["gap_pct"] for p in misses), default=None),
            "max_abs_point_diff_pct": abs(by_diff[0]["point_diff_pct"]) if by_diff else None,
            "point_diff_under_1pct": sum(1 for p in points if abs(p["point_diff_pct"]) < 1.0),
            "largest_point_diffs": [{k: p[k] for k in ("cell_id", "column", "new", "earlier", "point_diff_pct")}
                                    for p in by_diff[:TOP_DIFFS]],
            "misses": [{k: p[k] for k in ("cell_id", "column", "new", "earlier_ci95", "gap_pct", "point_diff_pct")}
                       for p in misses],
            "points": points}


# ---------------------------------------------------------------- the lost-SIMD range (the page's headline)

def lost_values(block):
    """Pooled ratios of the in-cache cells of the kernels that lose SIMD, both columns (the page's cpu_summary 'lost')."""
    return [c[col]["ratio"] for c in in_cache_cells(block) if c["class"] == "lost" for col in COLUMNS]


def printed(x):
    """The one-decimal form the page prints for the ends of the range."""
    return f"{x:.1f}"


def minmax(vals):
    return {"min": min(vals), "max": max(vals)} if vals else None


def headline_rows(doc, minimum):
    rows = []
    for b in doc["cpus"]:
        vals = lost_values(b)
        al = [c["aligned"]["ratio"] for c in in_cache_cells(b) if c["class"] == "lost"]
        co = [c["as_compiled"]["ratio"] for c in in_cache_cells(b) if c["class"] == "lost"]
        rows.append({"cpu_model": b["cpu_model"], "jobs": b["jobs"], "form": b["verdict"]["form"], "enough": b["jobs"] >= minimum,
                     "judged": b["jobs"] >= minimum and b["verdict"]["form"] != "inconclusive",
                     "range": minmax(vals), "aligned_range": minmax(al), "as_compiled_range": minmax(co)})
    return rows


def headline_block(earlier, replication, minimum):
    """The range of the in-cache loops that lose SIMD in the earlier pool (the models whose verdict reached a form, as
    scripts/build_site_data.py takes it) against the same cells of the replication set: any cell whose one-decimal
    form lies outside the printed range is listed. `outside_stored_range` is the same test against the unrounded ends."""
    e_rows, r_rows = headline_rows(earlier, minimum), headline_rows(replication, minimum)
    judged = [r for r in e_rows if r["judged"] and r["range"]] or [r for r in e_rows if r["enough"] and r["range"]]
    lo, hi = min(r["range"]["min"] for r in judged), max(r["range"]["max"] for r in judged)
    plo, phi = float(printed(lo)), float(printed(hi))
    outside_printed, outside_stored = [], []
    for b in replication["cpus"]:
        for c in in_cache_cells(b):
            if c["class"] != "lost":
                continue
            for col in COLUMNS:
                x = c[col]["ratio"]
                rec = {"cpu_model": b["cpu_model"], "jobs": b["jobs"], "enough": b["jobs"] >= minimum,
                       "cell_id": c["cell_id"], "column": col, "ratio": x}
                if not (plo <= float(printed(x)) <= phi):
                    outside_printed.append(rec)
                if not (lo <= x <= hi):
                    outside_stored.append(rec)
    r_judged = [r for r in r_rows if r["judged"] and r["range"]]
    r_enough = [r for r in r_rows if r["enough"] and r["range"]]
    rng = lambda rs: minmax([v for r in rs for v in (r["range"]["min"], r["range"]["max"])]) if rs else None  # noqa: E731
    return {"page_range": {"min": lo, "max": hi, "printed_min": printed(lo), "printed_max": printed(hi),
                           "models": [r["cpu_model"] for r in judged]},
            "earlier": e_rows, "replication": r_rows,
            "replication_judged_range": rng(r_judged), "replication_enough_range": rng(r_enough),
            "outside_printed_range": outside_printed, "outside_stored_range": outside_stored,
            "outside_printed_range_enough_jobs": sum(1 for r in outside_printed if r["enough"])}


# ---------------------------------------------------------------- one comparison (Arm, x86-64)

def model_rows(docs, crit, minimum):
    """One row per CPU model drawn in any of the three pools."""
    names = sorted({b["cpu_model"] for d in docs.values() for b in d["cpus"]})
    rows = []
    for m in names:
        blocks = {r: block_of(docs[r], m) for r in ROLES}
        row = {"cpu_model": m}
        for r in ROLES:
            row[r] = form_record(blocks[r], crit, minimum) if blocks[r] else None
        e, n = blocks["earlier"], blocks["replication"]
        row["testable"] = bool(e and n and e["jobs"] >= minimum and n["jobs"] >= minimum)
        row["same_form"] = (e["verdict"]["form"] == n["verdict"]["form"]) if row["testable"] else None
        row["inside"] = inside_summary(inside_points(n, e)) if row["testable"] else None
        rows.append(row)
    return rows


def flip_cells(docs, row, crit, minimum):
    """For a testable model whose verdict word changed: the cells that cause the non-MAP side, in every pool that has the model,
    with the role each cell played (judged or exempt as placement-sensitive) and its placement statistic."""
    ids = []
    for r in ("earlier", "replication"):
        rec = row[r]
        if rec["form"] == "inconclusive" and rec["cause"] and rec["cause"].get("forward_missed"):
            ids += [x["cell_id"] for x in rec["cause"]["forward_missed"] if x["cell_id"] not in ids]
    out = []
    for cid in ids:
        out.append({"cell_id": cid, **{r: (cell_record(block_of(docs[r], row["cpu_model"]), cid, crit, minimum)
                                           if row[r] else None) for r in ROLES}})
    return out


def compare(arch, docs, crit, minimum):
    rows = model_rows(docs, crit, minimum)
    testable = [r for r in rows if r["testable"]]
    pts = [p for r in testable for p in r["inside"]["points"]]
    block = {"arch": arch, "names": SET_NAMES[arch], "models": rows,
             "totals": {"testable_models": len(testable), "same_form": sum(1 for r in testable if r["same_form"]),
                        "flipped": sum(1 for r in testable if not r["same_form"]),
                        "points_checked": len(pts), "points_inside": sum(1 for p in pts if p["inside"]),
                        "points_outside": sum(1 for p in pts if not p["inside"]),
                        "point_diff_under_1pct": sum(1 for p in pts if abs(p["point_diff_pct"]) < 1.0),
                        "max_abs_point_diff_pct": max((abs(p["point_diff_pct"]) for p in pts), default=None)},
             "flips": [{"cpu_model": r["cpu_model"], "earlier_form": r["earlier"]["form"], "replication_form": r["replication"]["form"],
                        "cells": flip_cells(docs, r, crit, minimum)} for r in testable if not r["same_form"]],
             "not_testable": [{"cpu_model": r["cpu_model"], "earlier_jobs": r["earlier"]["jobs"] if r["earlier"] else 0,
                               "replication_jobs": r["replication"]["jobs"] if r["replication"] else 0, "minimum_jobs": minimum,
                               "earlier_form": r["earlier"]["form"] if r["earlier"] else None,
                               "secondary": r["secondary"]} for r in rows if not r["testable"]]}
    return block


# ---------------------------------------------------------------- the whole file

def pool_info(rel, doc, root):
    models = {}
    for i in doc["inputs"]:
        models[i["cpu_model"]] = models.get(i["cpu_model"], 0) + 1
    return {"path": rel, "sha256": lf_sha(os.path.join(root, rel)), "jobs": len(doc["inputs"]), "runs": doc["runs"],
            "criteria_sha256": doc["criteria_sha256"], "resamples": doc["resamples"], "models_drawn": dict(sorted(models.items()))}


def build(root=REPO):
    crit = load_json(os.path.join(root, CRITERIA))
    minimum = crit["v3"]["pooling"]["minimum_jobs"]
    vc = crit["verdict"]
    out = {"schema": SCHEMA,
           "note": "derived by replication/compare.py from the six pooled.json files named in `pools`; do not edit by hand. "
                   "The separate sets are the result. The pooled forms (secondary) were requested after a borderline "
                   "reading, so their stopping point depended on the data (replication/PLAN.md, item 3).",
           "plan": PLAN, "plan_sha256": lf_sha(os.path.join(root, PLAN)),
           "criteria": {"file": CRITERIA, "sha256": lf_sha(os.path.join(root, CRITERIA)), "minimum_jobs": minimum,
                        "forward_point_max_ratio": vc["forward_point_max_ratio"], "forward_ci_hi_floor_pct": vc["forward_ci_hi_floor_pct"],
                        "forward_ci_hi_aa_multiplier": vc["forward_ci_hi_aa_multiplier"], "lost_ci_lo_min_ratio": vc["lost_ci_lo_min_ratio"],
                        "aa_half_width_max_pct": vc["aa_half_width_max_pct"]},
           "pools": {}, "arm": None, "x86": None}
    docs, pooled_under = {}, set()
    for arch, files in POOLS.items():
        docs[arch] = {}
        out["pools"][arch] = {}
        for role, rel in files.items():
            doc = load_json(os.path.join(root, rel))
            if doc["criteria_file"] != CRITERIA:
                raise ValueError(f"{rel} was not pooled under {CRITERIA}")
            pooled_under.add(doc["criteria_sha256"])
            docs[arch][role] = doc
            out["pools"][arch][role] = pool_info(rel, doc, root)
    if len(pooled_under) != 1:
        raise ValueError(f"the six pooled files were not pooled under one version of {CRITERIA}: {sorted(pooled_under)}")
    out["criteria"]["pooled_under_sha256"] = pooled_under.pop()
    for arch in POOLS:
        out[arch] = compare(arch, docs[arch], crit, minimum)
    arm = out["arm"]
    arm_model = max((r for r in arm["models"] if r["earlier"]), key=lambda r: r["earlier"]["jobs"])["cpu_model"]
    arm["model"] = arm_model
    arm["named_cells"] = arm_named_cells(docs["arm"], arm_model, crit, minimum)
    out["x86"]["headline"] = headline_block(docs["x86"]["earlier"], docs["x86"]["replication"], minimum)
    out["questions"] = plan_questions(out, docs, crit, minimum)
    return out


def arm_named_cells(docs, model, crit, minimum):
    """The cell that decides the earlier Arm verdict (the cells its `why` names) and the matrix-multiply cells, in every pool."""
    e = block_of(docs["earlier"], model)
    cause = derive_cause(e, crit)
    ids = [x["cell_id"] for x in (cause or {}).get("forward_missed", [])]
    ids += [c for c in ARM_CONTEXT_CELLS if c not in ids]
    return [{"cell_id": cid, "decides_earlier_verdict": cid in [x["cell_id"] for x in (cause or {}).get("forward_missed", [])],
             **{r: cell_record(block_of(docs[r], model), cid, crit, minimum) for r in ROLES}} for cid in ids]


def missed_ids(rec):
    """The forward cells a pool's non-MAP verdict names (empty for a MAP or a cause that is not a forward miss)."""
    return [x["cell_id"] for x in ((rec or {}).get("cause") or {}).get("forward_missed", [])]


def plan_questions(out, docs, crit, minimum):
    """The two questions of replication/PLAN.md, with the outcome the data give."""
    arm = next(r for r in out["arm"]["models"] if r["cpu_model"] == out["arm"]["model"])
    named = [c for c in out["arm"]["named_cells"] if c["decides_earlier_verdict"]]
    q1 = {"model": arm["cpu_model"], "earlier_form": arm["earlier"]["form"], "replication_form": arm["replication"]["form"],
          "secondary_form": arm["secondary"]["form"], "decides_earlier": [c["cell_id"] for c in named],
          "replication_names_the_same_cells": missed_ids(arm["earlier"]) == missed_ids(arm["replication"]),
          "repeated": bool(arm["same_form"] and arm["earlier"]["form"] == "inconclusive" and missed_ids(arm["earlier"])
                           and missed_ids(arm["earlier"]) == missed_ids(arm["replication"])),
          "upper_end_above_limit": {r: [c[r]["aligned"]["ci95"][1] > c[r]["limit"] for c in named] for r in ROLES}}
    x = next((r for r in out["x86"]["models"] if r["cpu_model"] == PLAN_MODEL_X86), None)
    q2 = {"model": PLAN_MODEL_X86, "earlier_form": x["earlier"]["form"] if x and x["earlier"] else None,
          "earlier_jobs": x["earlier"]["jobs"] if x and x["earlier"] else 0,
          "earlier_closest_forward": x["earlier"]["closest_forward"] if x and x["earlier"] else None,
          "replication_jobs": x["replication"]["jobs"] if x and x["replication"] else 0,
          "minimum_jobs": minimum, "testable": bool(x and x["testable"]),
          "secondary_jobs": x["secondary"]["jobs"] if x and x["secondary"] else 0,
          "secondary_form": x["secondary"]["form"] if x and x["secondary"] else None,
          "secondary_cause": x["secondary"]["cause"] if x and x["secondary"] else None}
    return {"arm_cell": q1, "xeon_6973pc": q2}


# ---------------------------------------------------------------- verify

def same(a, b, where="", out=None):
    """Deep comparison, floats equal to 1e-12 relative; returns the first few differing paths."""
    out = [] if out is None else out
    if len(out) >= 10:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a) != list(b):
            out.append(f"{where}: keys {list(a)[:6]} vs {list(b)[:6]}")
        for k in a:
            if k in b:
                same(a[k], b[k], f"{where}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{where}: length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, f"{where}[{i}]", out)
    elif isinstance(a, float) or isinstance(b, float):
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool)
                and math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-15)):
            out.append(f"{where}: {a!r} vs {b!r}")
    elif a != b or type(a) is not type(b):
        out.append(f"{where}: {a!r} vs {b!r}")
    return out


def dumps(doc):
    return json.dumps(doc, indent=1) + "\n"


def verify_file(path, doc):
    """The differences between the stored file at `path` and a freshly built document (empty when they are equal)."""
    if not os.path.exists(path):
        return [f"{path} is missing"]
    return same(load_json(path), doc)


def main(argv):
    verify = "--verify" in argv
    if [a for a in argv[1:] if a != "--verify"]:
        print(__doc__)
        return 2
    doc = build()
    path = os.path.join(REPO, OUT)
    if verify:
        diffs = verify_file(path, doc)
        if diffs:
            print(f"FAIL {OUT} differs from a recomputation from the pooled files:")
            for d in diffs:
                print("   " + d)
            return 1
        a, x = doc["arm"]["totals"], doc["x86"]["totals"]
        print(f"   ok   {OUT} equals a recomputation from the six pooled files "
              f"(Arm: {a['points_inside']} of {a['points_checked']} points inside; x86-64: {x['points_inside']} of {x['points_checked']})")
        return 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(dumps(doc))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
