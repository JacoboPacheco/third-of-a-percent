#!/usr/bin/env python3
"""Offline analysis of the layout sweep (rules: layout-sweep/PLAN.md, numbers: layout-sweep/criteria.json).

    python layout-sweep/analyze.py <results.json | dir> [...] [--out analysis.json]
        a dir means every results.json under it at any depth (a run, or the whole results/ folder; the
        nested layout-sweep-analysis copies are skipped and a file seen twice, by sha256, counts once)

Reads the per-job results.json files written by layout-sweep/sweep.py, pools every job of a CPU
model with harness/pool.py (unchanged), and prints, per CPU model, kernel and size: the min, median
and max of the FAST/NONE ratio over the 16 placements, how many placements pass the forward rule,
and the verdict. Needs numpy (as harness/pool.py does) and no compiler.
"""
import glob
import hashlib
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402
import stats  # noqa: E402

CRITERIA_FILE = os.path.join(HERE, "criteria.json")
REFS = ["ref", "a64"]
MODES = ("fine", "coarse")  # fine: 16 placements, 4-byte steps; coarse: 4 placements, 16-byte steps (PLAN.md amendment)


def pad_ids(n):
    return [f"p{i:02d}" for i in range(n)]


def pad_bytes(pad_id, step):
    return step * int(pad_id[1:])


def mode_cfg(crit, mode):
    """The mode's placement count, step and thresholds merged over the shared rules."""
    return {**crit["rules"], **crit["modes"][mode], "mode": mode}


def doc_mode(doc):
    return (doc.get("mechanism") or {}).get("mode", "fine")


def load_criteria(path=CRITERIA_FILE):
    with open(path, "rb") as f:
        raw = f.read()
    # the hash is of the LF form (git stores LF; a Windows checkout with autocrlf holds CRLF)
    raw = raw.replace(bytes([13, 10]), bytes([10]))
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------- the placement mechanism

def probe_ok(points):
    """points: [(pad_bytes, fn_addr, hot_loop_start)] of the same build at several pads, the first
    at pad_bytes 0. True when both the function and the hot loop moved by exactly pad_bytes."""
    if len(points) < 2 or points[0][0] != 0:
        return False
    _, fn0, lp0 = points[0]
    return all(fn - fn0 == b and lp - lp0 == b for b, fn, lp in points[1:])


def check_mechanism(placements, cfg):
    """placements: {pad_id: {"pad_bytes", "none": build, "fast": build}} for one kernel (builds as
    stored by sweep.py). Returns a list of problems, empty when the 16 placements are verified from
    the stored disassembly facts. cfg: mode_cfg()."""
    problems = []
    pads = pad_ids(cfg["placements"])
    crit_rules = cfg
    missing = [p for p in pads if p not in placements]
    if missing:
        return [f"placements missing: {', '.join(missing)}"]
    for mode in ("none", "fast"):
        b0 = placements["p00"][mode]
        if b0.get("hot") is None:
            problems.append(f"{mode}: no hot loop found at p00")
            continue
        off0 = b0["hot"]["start"] - b0["fn_addr"]
        starts = set()
        for p in pads:
            b = placements[p][mode]
            if b.get("hot") is None:
                problems.append(f"{mode} {p}: no hot loop found")
                continue
            if b["fn_addr"] - b0["fn_addr"] != pad_bytes(p, cfg["step"]):
                problems.append(f"{mode} {p}: function moved by {b['fn_addr'] - b0['fn_addr']}, expected {pad_bytes(p, cfg['step'])}")
            if b["hot"]["start"] - b["fn_addr"] != off0:
                problems.append(f"{mode} {p}: loop offset inside the function changed")
            starts.add(b["hot"]["start"] % 64)
        if len(starts) < crit_rules["distinct_start_mod64_required"]:
            problems.append(f"{mode}: only {len(starts)} distinct hot-loop start residues mod 64, "
                            f"need {crit_rules['distinct_start_mod64_required']}")
    return problems


# ---------------------------------------------------------------- per-job verification (recompute)

def verify_job(doc, crit, crit_sha):
    """Problems found recomputing one job's stored numbers from its raw samples (empty list = fine)."""
    problems = []
    if doc.get("kind") != "layout-sweep":
        return ["kind is not layout-sweep"]
    if doc.get("criteria_sha256") != crit_sha:
        problems.append("criteria_sha256 does not match layout-sweep/criteria.json")
    resamples = crit["design"]["per_job_resamples"]
    for c in doc["cells"]:
        for pid, p in c["placements"].items():
            where = f"{c['cell_id']} {pid}"
            r = stats.ratio_of_medians(p["none_ns"], p["fast_ns"])
            if r != p["ratio"]:
                problems.append(f"{where}: stored ratio {p['ratio']} != recomputed {r}")
                continue
            lo, hi = stats.bootstrap_ratio_ci(p["none_ns"], p["fast_ns"], resamples=resamples)
            if [lo, hi] != p["ci95"]:
                problems.append(f"{where}: stored ci95 {p['ci95']} != recomputed {[lo, hi]}")
    return problems


# ---------------------------------------------------------------- one CPU model

def _limit(aa_hw, rules):
    return 1.0 + max(rules["forward_ci_hi_floor_pct"], rules["forward_ci_hi_aa_multiplier"] * aa_hw) / 100.0


def _compact(s):
    return {"ratio": s["ratio"], "ci95": s["ci95"], "half_width_pct": s["half_width_pct"]}


def class_of(none_vec, fast_vec):
    if none_vec and fast_vec:
        return "kept"
    if none_vec and fast_vec is False:
        return "lost"
    return "off_axis"


def analyse_cell(cpu, cid, docs_cells, builds0, rules):
    PADS = pad_ids(rules["placements"])
    N_PADS = len(PADS)
    """One cell (kernel x size) of one CPU model. docs_cells: the cell dict of every job."""
    kernel = docs_cells[0]["kernel"]
    p00 = builds0["placements"]["p00"]
    klass = class_of(p00["none"].get("vectorized"), p00["fast"].get("vectorized"))
    out = {"cell_id": cid, "kernel": kernel, "size_class": docs_cells[0]["size_class"], "class": klass,
           "vectorized_none": p00["none"].get("vectorized"), "vectorized_fast": p00["fast"].get("vectorized"),
           "inconclusive": []}
    aa = pool.pair_stat(cpu, f"ls|{cid}|aa", [(c["aa"]["a_ns"], c["aa"]["b_ns"]) for c in docs_cells])
    out["aa"] = _compact(aa)
    aa_hw = aa["half_width_pct"]
    limit = _limit(aa_hw, rules)
    out["forward_limit"] = limit
    if aa_hw > rules["aa_half_width_max_pct"]:
        out["inconclusive"].append(f"A/A half-width {aa_hw:.2f}% above {rules['aa_half_width_max_pct']}%")
    rows = {}
    for pid in PADS + REFS:
        if not all(pid in c["placements"] for c in docs_cells):
            if pid in PADS:
                out["inconclusive"].append(f"placement {pid} missing in some job")
            continue
        prs = [c["placements"][pid] for c in docs_cells]
        if not all(p["checksum_match"] for p in prs):
            out["inconclusive"].append(f"checksum mismatch at {pid}")
        s = pool.pair_stat(cpu, f"ls|{cid}|{pid}", [(p["none_ns"], p["fast_ns"]) for p in prs])
        row = _compact(s)
        row["between_job_sd_pct"] = s["between_job_sd_pct"]
        row["per_job"] = s["per_job"]
        row["passes"] = s["ratio"] <= rules["forward_point_max_ratio"] and s["ci95"][1] <= limit
        row["costs"] = s["ci95"][0] > limit
        row["holds"] = s["ci95"][0] >= rules["lost_ci_lo_min_ratio"]
        pl = builds0["placements"].get(pid)
        if pl:
            hn, hf = pl["none"].get("hot"), pl["fast"].get("hot")
            row["none_start_mod64"] = hn["start_mod64"] if hn else None
            row["fast_start_mod64"] = hf["start_mod64"] if hf else None
            row["none_extra_window"] = hn["extra_window"] if hn else None
            row["fast_extra_window"] = hf["extra_window"] if hf else None
        rows[pid] = row
    out["placements"] = {pid: rows[pid] for pid in PADS if pid in rows}
    out["refs"] = {pid: rows[pid] for pid in REFS if pid in rows}
    sweep = [rows[p] for p in PADS if p in rows]
    ratios = sorted(r["ratio"] for r in sweep)
    if ratios:
        out["ratio_min"], out["ratio_median"], out["ratio_max"] = ratios[0], statistics.median(ratios), ratios[-1]
    out["n_placements"] = len(sweep)
    out["n_pass"] = sum(r["passes"] for r in sweep)
    out["n_cost"] = sum(r["costs"] for r in sweep)
    out["n_hold"] = sum(r["holds"] for r in sweep)
    # no-rule split: FAST's loop wastes a fetch window that NONE's does not
    split = {"fast_extra_window_only": [], "other": []}
    for r in sweep:
        key = "fast_extra_window_only" if (r.get("fast_extra_window") and not r.get("none_extra_window")) else "other"
        split[key].append(r["ratio"])
    out["median_by_window"] = {k: {"n": len(v), "median": (statistics.median(v) if v else None)} for k, v in split.items()}
    # verdict of the cell
    if out["inconclusive"] or len(sweep) < N_PADS:
        out["verdict"] = "INCONCLUSIVE"
    elif klass == "kept":
        out["verdict"] = ("ROBUST" if out["n_pass"] >= rules["robust_min_pass"]
                          else "PLACEMENT_DEPENDENT" if out["n_pass"] <= rules["dependent_max_pass"] else "MIXED")
    elif klass == "lost":
        out["verdict"] = "HOLDS" if out["n_hold"] >= rules["lost_holds_min_pass"] else "NOT_STABLE"
    else:
        out["verdict"] = "OFF_AXIS"
    return out


def analyse_cpu(cpu, docs, crit):
    mode = doc_mode(docs[0])
    rules = mode_cfg(crit, mode)
    block = {"cpu_model": cpu, "jobs": len(docs), "runs": sorted({d["run"]["id"] for d in docs}), "problems": [],
             "mode": mode, "placements": rules["placements"], "step_bytes": rules["step"]}
    if len({doc_mode(d) for d in docs}) != 1:
        block["problems"].append("jobs ran different placement modes (fine and coarse)")
    if len(docs) < crit["design"]["min_jobs_per_cpu"]:
        block["problems"].append(f"too few jobs ({len(docs)}, minimum {crit['design']['min_jobs_per_cpu']})")
    ids = [[c["cell_id"] for c in d["cells"]] for d in docs]
    common = [i for i in ids[0] if all(i in x for x in ids)]
    for i in sorted({i for x in ids for i in x} - set(common)):
        block["problems"].append(f"cell {i} missing in some jobs")
    # the binaries are the same in every job of one CPU model (and anywhere): same sha256
    shas = [json.dumps({k: {p: [b["none"]["sha256"], b["fast"]["sha256"]] for p, b in v["placements"].items()}
                        for k, v in d["builds"].items()}, sort_keys=True) for d in docs]
    if len(set(shas)) != 1:
        block["problems"].append("build sha256 differ between jobs")
    mech = {}
    for k, v in docs[0]["builds"].items():
        pr = check_mechanism(v["placements"], rules)
        if pr:
            mech[k] = pr
            block["problems"].append(f"{k}: placement mechanism not verified: " + "; ".join(pr[:3]))
    block["mechanism_problems"] = mech
    by_id = [{c["cell_id"]: c for c in d["cells"]} for d in docs]
    cells = []
    for cid in common:
        cs = [b[cid] for b in by_id]
        cell = analyse_cell(cpu, cid, cs, docs[0]["builds"][cs[0]["kernel"]], rules)
        if block["problems"]:
            cell["inconclusive"] = block["problems"] + cell["inconclusive"]
            cell["verdict"] = "INCONCLUSIVE"
        cells.append(cell)
    block["cells"] = cells
    kept = [c for c in cells if c["class"] == "kept"]
    lost = [c for c in cells if c["class"] == "lost"]
    if not kept or any(c["verdict"] == "INCONCLUSIVE" for c in kept):
        fwd = "INCONCLUSIVE"
    elif all(c["verdict"] == "ROBUST" for c in kept):
        fwd = "ROBUST"
    elif any(c["verdict"] == "PLACEMENT_DEPENDENT" for c in kept):
        fwd = "PLACEMENT_DEPENDENT"
    else:
        fwd = "MIXED"
    if not lost or any(c["verdict"] == "INCONCLUSIVE" for c in lost):
        ctl = "INCONCLUSIVE"
    else:
        ctl = "HOLDS" if all(c["verdict"] == "HOLDS" for c in lost) else "NOT_STABLE"
    block["forward_claim"] = fwd
    block["lost_control"] = ctl
    # per kernel over both sizes (no rule): min, median, max of the pooled ratios of all placements
    per_kernel = {}
    for k in sorted({c["kernel"] for c in cells}):
        rs = sorted(r["ratio"] for c in cells if c["kernel"] == k for r in c["placements"].values())
        if rs:
            per_kernel[k] = {"n": len(rs), "min": rs[0], "median": statistics.median(rs), "max": rs[-1],
                             "n_pass": sum(c["n_pass"] for c in cells if c["kernel"] == k),
                             "n_cost": sum(c["n_cost"] for c in cells if c["kernel"] == k)}
    block["per_kernel"] = per_kernel
    block["line"] = (f"On {cpu} ({len(docs)} job{'s' if len(docs) != 1 else ''}): forward claim over "
                     f"{rules['placements']} code placements ({mode}, {rules['step']}-byte steps): {fwd}; lost-loop control: {ctl}.")
    return block


def analyse(entries, crit, crit_sha):
    """entries: [(relative path, results doc)] -> the analysis document."""
    by_cpu = {}
    for rel, d in entries:
        by_cpu.setdefault(d["run"]["runner"]["cpu_model"] or "unknown", []).append(d)
    return {"kind": "layout-sweep-analysis", "schema": 1, "criteria_sha256": crit_sha,
            "inputs": [{"path": rel, "run_id": d["run"]["id"], "job": d["run"].get("job"),
                        "cpu_model": d["run"]["runner"]["cpu_model"] or "unknown"} for rel, d in entries],
            "cpus": [analyse_cpu(m, ds, crit) for m, ds in sorted(by_cpu.items())]}


# ---------------------------------------------------------------- loading and printing

def file_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def find_results(paths):
    """Every results.json under the given files and folders (any depth: one run folder, a run's
    job folders, or the whole results/ parent), without the nested 'layout-sweep-analysis' copies
    that a downloaded run carries, and with each distinct file (by sha256) counted once."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            for q in glob.glob(os.path.join(p, "**", "results.json"), recursive=True):
                if "layout-sweep-analysis" not in q.replace("\\", "/").split("/"):
                    files.append(q)
        else:
            files.append(p)
    seen, out = set(), []
    for q in sorted(set(files), key=lambda x: os.path.abspath(x).replace("\\", "/")):
        h = file_sha256(q)
        if h not in seen:
            seen.add(h)
            out.append(q)
    return out


def load_entries(paths, base_dir):
    """[(path relative to base_dir with '/', results doc)], sorted by that path (the job order the
    bootstrap's job indices refer to), each distinct file once."""
    rels = sorted({os.path.relpath(os.path.abspath(x), base_dir).replace("\\", "/") for x in find_results(paths)})
    out = []
    for r in rels:
        with open(os.path.join(base_dir, r), encoding="utf-8") as fh:
            out.append((r, json.load(fh)))
    return out


def add_input_hashes(an, base_dir):
    """Stores each input file's sha256 in analysis['inputs'] (main only; analyse() output stays as before)."""
    for i in an["inputs"]:
        i["sha256"] = file_sha256(os.path.join(base_dir, i["path"]))
    return an


def report(an):
    lines = []
    for b in an["cpus"]:
        lines.append(b["line"])
        for p in b["problems"]:
            lines.append(f"  problem: {p}")
        lines.append(f"  {'cell':<20}{'class':<9}{'min':>7}{'median':>8}{'max':>7}  pass  cost  {'ref':>6}{'a64':>7}  verdict")
        for c in b["cells"]:
            if "ratio_min" not in c:
                lines.append(f"  {c['cell_id']:<20}{c['class']:<9} no data  {c['verdict']}")
                continue
            ref = c["refs"].get("ref", {}).get("ratio")
            a64 = c["refs"].get("a64", {}).get("ratio")
            f = lambda x: f"{x:.3f}" if x is not None else "-"  # noqa: E731
            lines.append(f"  {c['cell_id']:<20}{c['class']:<9}{c['ratio_min']:>7.3f}{c['ratio_median']:>8.3f}{c['ratio_max']:>7.3f}"
                         f"  {c['n_pass']:>2}/{c['n_placements']:<2} {c['n_cost']:>2}/{c['n_placements']:<2} {f(ref):>6}{f(a64):>7}  {c['verdict']}")
        for k, v in b["per_kernel"].items():
            lines.append(f"  {k}: over {v['n']} pooled ratios (both sizes) min {v['min']:.3f} median {v['median']:.3f} "
                         f"max {v['max']:.3f}; pass {v['n_pass']}, cost {v['n_cost']}")
        lines.append("")
    if not an["cpus"]:
        lines.append("no results")
    return "\n".join(lines)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out = None
    if "--out" in argv:
        i = argv.index("--out")
        out = os.path.abspath(argv[i + 1])
        del argv[i:i + 2]
    if not argv:
        print(__doc__)
        return 2
    crit, sha = load_criteria()
    base = os.path.dirname(out) if out else os.getcwd()
    entries = load_entries(argv, base)
    if not entries:
        print("no results.json found")
        return 1
    an = add_input_hashes(analyse(entries, crit, sha), base)
    print(report(an))
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(an, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
