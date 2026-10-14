"""Pooled verdict per CPU model (harness/criteria-v3.json): every job of a CPU model, in one run and
across runs, pooled, with a two-level bootstrap interval that contains between-job spread.

Why this exists: under criteria-v2 each Actions job voted on its own 20-per-side sample, and the
audit of S3 found that the within-job 95 % intervals missed the next run's numbers for 9 to 14 of 32
in-cache cells per CPU model, and that the page-level form flipped with the set of CPU models drawn.
Here the CPU model is the unit:

    r_j  = median(B samples of job j) / median(A samples of job j)       (the v1 ratio, inside one job)
    R    = exp(mean_j ln r_j)                                             (geometric mean over the J jobs)

and the 95 % interval comes from resampling twice: draw J jobs with replacement, and inside each
drawn job redraw each side's repetitions with replacement; 2000 such draws; percentiles 2.5 and 97.5.

The random draws come from a counter-based generator (splitmix64) written out below with numpy
uint64 arithmetic, so they are the same on any machine and any numpy version, and scripts/check.py
can recompute every number in pooled.json. harness/pool_check.py redoes a sample of the intervals
with a separate, plain-Python implementation and a different seed.

Usage:
  python harness/pool.py <out.json> <results.json | dir> [...]
      a dir means every */results.json under it (one Actions run downloaded by the workflow)
Writes <out.json> (kind "pooled"); its "inputs" are stored relative to its own directory.
"""
import glob
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import placement  # noqa: E402
import stats  # noqa: E402
import verdict  # noqa: E402

V3_FILE = "harness/criteria-v3.json"
IN_CACHE = ("L1", "L2")
SEED_PREFIX = "20261011"
RESAMPLES = 2000
MASK = (1 << 64) - 1
GOLDEN = np.uint64(0x9E3779B97F4A7C15)
M1 = np.uint64(0xBF58476D1CE4E5B9)
M2 = np.uint64(0x94D049BB133111EB)


# ---------------------------------------------------------------- the generator

def seed_for(cpu_model, stat_id, stream):
    """64-bit seed of one stream of one statistic: sha256('20261011|cpu|stat_id|stream')[:16]."""
    h = hashlib.sha256(f"{SEED_PREFIX}|{cpu_model}|{stat_id}|{stream}".encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def splitmix64(seed, count):
    """The first `count` outputs of splitmix64 started at `seed`, as a numpy uint64 array.
    Output k is mix(seed + (k + 1) * 0x9E3779B97F4A7C15 mod 2^64)."""
    with np.errstate(over="ignore"):
        k = np.arange(1, count + 1, dtype=np.uint64)
        z = np.uint64(seed) + k * GOLDEN
        z = (z ^ (z >> np.uint64(30))) * M1
        z = (z ^ (z >> np.uint64(27))) * M2
        return z ^ (z >> np.uint64(31))


def draws(seed, shape, n):
    """Indices in 0..n-1 (output mod n), in C order of `shape`."""
    count = int(np.prod(shape))
    return (splitmix64(seed, count) % np.uint64(n)).astype(np.int64).reshape(shape)


# ---------------------------------------------------------------- one pooled statistic

def job_ratio(a, b):
    return statistics.median(b) / statistics.median(a)


def _side_medians(cpu, stat_id, side, job_idx, samples_by_job):
    """Bootstrap medians of one side: shape (B, J). samples_by_job[j] is that job's list for the side."""
    lens = {len(s) for s in samples_by_job}
    if len(lens) != 1:
        raise ValueError(f"{stat_id}: side {side} has unequal sample counts across jobs {sorted(lens)}")
    L = lens.pop()
    arr = np.asarray(samples_by_job, dtype=np.float64)          # (J, L)
    B, J = job_idx.shape
    t = draws(seed_for(cpu, stat_id, f"side{side}"), (B, J, L), L)
    picked = arr[job_idx[:, :, None], t]                         # (B, J, L)
    return np.median(picked, axis=2)


def pooled_stat(cpu, stat_id, sides_by_job, combine, resamples=RESAMPLES):
    """sides_by_job: [[side0 samples, side1 samples, ...] per job]; combine(medians...) -> per-job ratio
    (works on floats and on numpy arrays). Returns the stored statistic."""
    J = len(sides_by_job)
    per_job = [combine(*[statistics.median(s) for s in sides]) for sides in sides_by_job]
    logs = [math.log(r) for r in per_job]
    ratio = math.exp(math.fsum(logs) / J)
    job_idx = draws(seed_for(cpu, stat_id, "jobs"), (resamples, J), J)
    nsides = len(sides_by_job[0])
    meds = [_side_medians(cpu, stat_id, k, job_idx, [s[k] for s in sides_by_job]) for k in range(nsides)]
    rstar = np.exp(np.mean(np.log(combine(*meds)), axis=1))
    lo, hi = stats.percentile_interval(sorted(float(x) for x in rstar))
    return {"ratio": ratio, "ci95": [lo, hi], "half_width_pct": stats.half_width_pct((lo, hi)), "jobs": J,
            "per_job": per_job,
            "between_job_sd_pct": 100.0 * statistics.stdev(logs) if J > 1 else None}


def pair_stat(cpu, stat_id, pairs, resamples=RESAMPLES):
    """pairs: [(A samples, B samples) per job] -> pooled median(B)/median(A)."""
    return pooled_stat(cpu, stat_id, [[a, b] for a, b in pairs], lambda ma, mb: mb / ma, resamples)


def placement_stat(cpu, stat_id, quads, resamples=RESAMPLES):
    """quads: [(none, fast, none_a64, fast_a64) per job] -> pooled (fast/none) / (fast_a64/none_a64)."""
    return pooled_stat(cpu, stat_id, [list(q) for q in quads],
                       lambda n, f, na, fa: (f / n) / (fa / na), resamples)


# ---------------------------------------------------------------- loading

def load_inputs(paths, base_dir):
    """[(path relative to base_dir, doc)] from results.json files or dirs of */results.json."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, "*", "results.json")))
        else:
            files.append(p)
    # sorted by the relative path with '/' separators, so the job order (which the bootstrap's job
    # indices refer to) is the same on Linux and Windows ('\' sorts after digits, '/' before them)
    rels = sorted({os.path.relpath(os.path.abspath(x), base_dir).replace("\\", "/") for x in files})
    out = []
    for r in rels:
        with open(os.path.join(base_dir, r), encoding="utf-8") as fh:
            out.append((r, json.load(fh)))
    return out


def criteria_and_sha():
    with open(os.path.join(REPO, V3_FILE), "rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------- helpers on one CPU model's jobs

def hot_loop(loop_list):
    """The innermost loop with simd and the most bytes (the innermost loop with the most bytes if none has simd)."""
    inner = [lp for lp in loop_list if lp["innermost"]]
    if not inner:
        return None
    simd = [lp for lp in inner if lp["simd"]]
    pool = simd or inner
    return max(pool, key=lambda lp: (lp["bytes"], -int(lp["start"], 16)))


def placement_differs(cell):
    """Part (2) of the v3 placement-sensitive rule: NONE's and FAST's hot loops sit differently
    relative to 64-byte windows (start_mod64, bytes, windows64 or extra_window differ)."""
    loops = cell.get("loops") or {}
    hn, hf = hot_loop(loops.get("none", [])), hot_loop(loops.get("fast", []))
    if hn is None or hf is None:
        return False, hn, hf
    keys = ("start_mod64", "bytes", "windows64", "extra_window")
    return any(hn[k] != hf[k] for k in keys), hn, hf


def _short(lp):
    if lp is None:
        return None
    return {k: lp[k] for k in ("start", "bytes", "start_mod64", "windows64", "extra_window", "crosses64", "simd")}


def _instr_of(cells_by_job, key):
    """The instruction counts of one cell and column across jobs: (value or None, agree flag)."""
    vals = []
    for c in cells_by_job:
        x = c["instr"] if key == "as_compiled" else c.get("aligned", {}).get("instr")
        vals.append(json.dumps(x, sort_keys=True))
    agree = len(set(vals)) == 1
    first = json.loads(vals[0]) if vals else None
    return first, agree


def _compact(s):
    return [s["ratio"], s["ci95"][0], s["ci95"][1]]


# ---------------------------------------------------------------- one CPU model, given its jobs

def analyse_cpu(cpu, docs, criteria, full=True):
    """Pooled statistics and the v3 verdict of one CPU model from its per-job results documents.
    full=False skips what only the all-runs block shows (instructions, per-job lists stay in)."""
    crit = criteria["verdict"]
    v3 = criteria["v3"]
    J = len(docs)
    block = {"cpu_model": cpu, "jobs": J, "runs": sorted({d["run"]["id"] for d in docs})}
    problems = {"checksum": [], "build": [], "layout": []}

    # cells present in every job
    ids_per_job = [[c["cell_id"] for c in d["cells"]] for d in docs]
    all_ids = sorted(set().union(*ids_per_job), key=lambda x: ids_per_job[0].index(x) if x in ids_per_job[0] else 999)
    common = [cid for cid in all_ids if all(cid in ids for ids in ids_per_job)]
    for cid in all_ids:
        if cid not in common:
            problems["build"].append(f"{cid} missing in some jobs")
    by_id = [{c["cell_id"]: c for c in d["cells"]} for d in docs]
    first_cells = [by_id[0][cid] for cid in common]
    cls = verdict.classes(first_cells) if first_cells else {"on_axis": [], "kept": [], "lost": [], "off_axis": []}

    def same(vals):
        return len({json.dumps(v, sort_keys=True) for v in vals}) == 1

    # A/A (byte-identical) pooled
    aa_pairs = [(d["controls"]["aa"].get("a_ns"), d["controls"]["aa"].get("b_ns")) for d in docs]
    if any(a is None or b is None for a, b in aa_pairs):
        raise ValueError(f"{cpu}: a job lacks controls.aa raw samples (a_ns, b_ns); not a criteria-v3 run")
    block["aa"] = pair_stat(cpu, "aa", aa_pairs)
    aa_hw = block["aa"]["half_width_pct"]
    limit_pct = max(crit["forward_ci_hi_floor_pct"], crit["forward_ci_hi_aa_multiplier"] * aa_hw)
    limit = 1.0 + limit_pct / 100.0

    # layout A/A pooled, per id present in every job
    lay_ids = [[p["id"] for p in d["controls"].get("layout_aa", [])] for d in docs]
    lay_common = [i for i in lay_ids[0] if all(i in ids for ids in lay_ids)] if lay_ids else []
    block["layout_aa"] = {}
    for lid in lay_common:
        prs = [next(p for p in d["controls"]["layout_aa"] if p["id"] == lid) for d in docs]
        block["layout_aa"][lid] = pair_stat(cpu, f"layout|{lid}", [(p["a_ns"], p["b_ns"]) for p in prs])
    for want in criteria["v2"]["layout_aa_designated"]:
        if want not in block["layout_aa"]:
            problems["layout"].append(want)

    # positive control pooled
    pos_ids = [[p["cell_id"] for p in d["controls"]["positive"]] for d in docs]
    pos_common = [i for i in pos_ids[0] if all(i in ids for ids in pos_ids)] if pos_ids else []
    block["positive"] = {}
    for pid in pos_common:
        prs = [next(p for p in d["controls"]["positive"] if p["cell_id"] == pid) for d in docs]
        if any("none_ns" not in p for p in prs):
            raise ValueError(f"{cpu}: a job lacks controls.positive raw samples; not a criteria-v3 run")
        block["positive"][pid] = pair_stat(cpu, f"novec|{pid}", [(p["none_ns"], p["novec_ns"]) for p in prs])

    # cells
    cells = []
    for cid in common:
        cs = [b[cid] for b in by_id]
        c0 = cs[0]
        if not all(c["checksum_match"] for c in cs) or not all(c.get("aligned", {}).get("checksum_match") for c in cs):
            problems["checksum"].append(cid)
        if any("aligned" not in c for c in cs):
            problems["build"].append(f"{cid} lacks the aligned pair")
            continue
        sig = [(c["none_sha256"], c["fast_sha256"], c["aligned"]["none_sha256"], c["aligned"]["fast_sha256"],
                c["vectorized_none"]["vectorized"], c["vectorized_fast"]["vectorized"],
                c["aligned"]["vectorized_none"]["vectorized"], c["aligned"]["vectorized_fast"]["vectorized"])
               for c in cs]
        if not same(sig):
            problems["build"].append(f"{cid} binaries or remarks differ between jobs")
        if (c0["aligned"]["vectorized_none"]["vectorized"] != c0["vectorized_none"]["vectorized"]
                or c0["aligned"]["vectorized_fast"]["vectorized"] != c0["vectorized_fast"]["vectorized"]):
            problems["build"].append(f"{cid} aligned builds' remarks differ from the as-compiled ones")
        k = c0["kernel"]
        klass = ("kept" if k in cls["kept"] else "lost" if k in cls["lost"] else "off_axis")
        row = {"cell_id": cid, "kernel": k, "size_class": c0["size_class"], "class": klass,
               "as_compiled": pair_stat(cpu, f"{cid}|as_compiled", [(c["none_ns"], c["fast_ns"]) for c in cs]),
               "aligned": pair_stat(cpu, f"{cid}|aligned",
                                    [(c["aligned"]["none_ns"], c["aligned"]["fast_ns"]) for c in cs])}
        if full:
            ins, ok1 = _instr_of(cs, "as_compiled")
            ins_a, ok2 = _instr_of(cs, "aligned")
            row["instr"] = ins
            row["aligned_instr"] = ins_a
            row["instr_agree"] = ok1 and ok2
            row["instr_label"] = "instructions, not time"
        if klass == "kept" and c0["size_class"] in IN_CACHE:
            d = placement_stat(cpu, f"{cid}|placement",
                               [(c["none_ns"], c["fast_ns"], c["aligned"]["none_ns"], c["aligned"]["fast_ns"])
                                for c in cs])
            mech, hn, hf = placement_differs(c0)
            stat_part = d["ci95"][0] > 1.0 or d["ci95"][1] < 1.0
            row["placement"] = {"d": d, "statistical": stat_part, "mechanical": mech, "hot_none": _short(hn),
                                "hot_fast": _short(hf), "sensitive": stat_part and mech}
        cells.append(row)
    block["cells"] = cells
    block["verdict"] = cpu_verdict(block, cls, problems, crit, v3, limit, limit_pct, aa_hw, criteria)
    return block


def cpu_verdict(block, cls, problems, crit, v3, limit, limit_pct, aa_hw, criteria):
    cpu, J = block["cpu_model"], block["jobs"]
    in_cache = [c for c in block["cells"] if c["size_class"] in IN_CACHE]
    ps = [c for c in in_cache if c.get("placement", {}).get("sensitive")]
    ps_ids = {c["cell_id"] for c in ps}
    ps_list = [{"cell_id": c["cell_id"], "ratio": c["as_compiled"]["ratio"], "aligned_ratio": c["aligned"]["ratio"],
                "d": c["placement"]["d"]["ratio"], "d_ci95": c["placement"]["d"]["ci95"]} for c in ps]
    off = [{"cell_id": c["cell_id"], "ratio": c["as_compiled"]["ratio"], "aligned_ratio": c["aligned"]["ratio"],
            "pays_in_both_columns": c["as_compiled"]["ci95"][0] > limit and c["aligned"]["ci95"][0] > limit}
           for c in in_cache if c["class"] == "off_axis"]
    ps_text = ""
    if ps:
        ps_text = (" " + verdict.PS_LEAD
                   + "; ".join(f"{p['cell_id']} (as compiled {p['ratio']:.3f}, aligned {p['aligned_ratio']:.3f}, "
                               f"ratio of the two {p['d']:.3f} [{p['d_ci95'][0]:.3f}, {p['d_ci95'][1]:.3f}])"
                               for p in ps_list) + ".")
    head = f"On {cpu} ({J} job{'s' if J != 1 else ''}, {len(block['runs'])} run{'s' if len(block['runs']) != 1 else ''} pooled): "

    def out(form, line, why, n=None, n_c=None, x=None):
        return {"form": form, "line": head + line, "why": why, "n": n, "n_as_compiled": n_c, "x_pct": x,
                "forward_limit_pct": limit_pct, "aa_half_width_pct": aa_hw, "placement_sensitive": ps_list,
                "off_axis": off}

    if J < v3["pooling"]["minimum_jobs"]:
        return out("inconclusive", f"INCONCLUSIVE: too few jobs ({J}, the minimum is "
                   f"{v3['pooling']['minimum_jobs']}), so no headline number is printed.",
                   "too few jobs: fewer than minimum_jobs pooled")
    if aa_hw > crit["aa_half_width_max_pct"]:
        return out("inconclusive", f"INCONCLUSIVE: the pooled A/A control is too noisy (half-width {aa_hw:.2f}%, "
                   f"above {crit['aa_half_width_max_pct']:.0f}%), so no headline number is printed.",
                   "A/A control: pooled A/A half-width above aa_half_width_max_pct")
    if problems["checksum"]:
        return out("inconclusive", "INCONCLUSIVE: the NONE and FAST outputs differ in "
                   + ", ".join(problems["checksum"]) + ", so no headline number is printed.",
                   "checksum control: a pooled job has a checksum mismatch")
    if problems["build"]:
        return out("inconclusive", "INCONCLUSIVE: the build control failed (" + "; ".join(problems["build"])
                   + "), so no headline number is printed.", "build control: " + "; ".join(problems["build"]))
    if problems["layout"]:
        return out("inconclusive", "INCONCLUSIVE: the designated layout A/A pairs (" + ", ".join(problems["layout"])
                   + ") are missing from some job, so no headline number is printed.",
                   "layout control: a designated layout A/A pair is missing")
    if not [p for p in block["positive"].values() if p["ci95"][0] > 1.0 + aa_hw / 100.0]:
        return out("inconclusive", "INCONCLUSIVE: the positive control (the same loop built with -fno-vectorize) "
                   "was not seen above the pooled A/A noise; no headline number is printed.",
                   "positive control: no pooled NOVEC/NONE ci95_lo above 1 + pooled A/A half-width")
    if not cls["kept"]:
        return out("inconclusive", "INCONCLUSIVE: no kernel kept its vectorization under FAST, so there is no "
                   "negative control; no headline number is printed.", "negative control: no kernel in the kept class")

    fwd = [c for c in in_cache if c["class"] == "kept" and c["cell_id"] not in ps_ids]
    lost = [c for c in in_cache if c["class"] == "lost"]
    fwd_fail = [c["cell_id"] for c in fwd if not (c["aligned"]["ratio"] <= crit["forward_point_max_ratio"]
                                                  and c["aligned"]["ci95"][1] <= limit)]
    lost_fail = [c["cell_id"] + col for c in lost for col, key in (("", "as_compiled"), (" (aligned)", "aligned"))
                 if not c[key]["ci95"][0] >= crit["lost_ci_lo_min_ratio"]]
    if cls["lost"] and lost and fwd and not fwd_fail and not lost_fail:
        rs = [c["aligned"]["ratio"] for c in lost]
        rc = [c["as_compiled"]["ratio"] for c in lost]
        n = {"median": statistics.median(rs), "min": min(rs), "max": max(rs)}
        n_c = {"median": statistics.median(rc), "min": min(rc), "max": max(rc)}
        x = max(0.0, max(100.0 * (c["aligned"]["ci95"][1] - 1.0) for c in fwd))
        fk = sorted({c["kernel"] for c in fwd})
        line = verdict.map_line(cls["lost"], n, x, fk, n_c, aligned=True) + ps_text
        return out("map", line, f"MAP: every counted forward in-cache cell has pooled aligned ratio <= "
                   f"{crit['forward_point_max_ratio']} and pooled aligned ci95_hi <= {limit:.4f}; every lost in-cache "
                   f"cell has pooled ci95_lo >= {crit['lost_ci_lo_min_ratio']} in both columns", n, n_c, x)

    axis = [c for c in in_cache if c["class"] in ("kept", "lost") and c["cell_id"] not in ps_ids]
    above = [c["cell_id"] + col for c in axis for col, key in (("", "as_compiled"), (" (aligned)", "aligned"))
             if c[key]["ci95"][0] > limit]
    if axis and not above:
        x = max(0.0, max(max(100.0 * (c["as_compiled"]["ci95"][1] - 1), 100.0 * (c["aligned"]["ci95"][1] - 1))
                         for c in axis))
        return out("holds_everywhere", f"no loop shape we tried paid more than {x:.1f}% (as compiled or with loops "
                   "aligned)." + ps_text, f"HOLDS_EVERYWHERE: no pooled in-cache on-axis ci95_lo above {limit:.4f}",
                   x=x)
    reasons = []
    if not fwd:
        reasons.append("no forward cell left after the placement-sensitive exclusions")
    if fwd_fail:
        reasons.append("forward rule (aligned) missed by " + ", ".join(fwd_fail))
    if lost_fail:
        reasons.append("lost-vectorization minimum missed by " + ", ".join(lost_fail))
    if not cls["lost"]:
        reasons.append("no kernel lost vectorization")
    if above:
        reasons.append("cells above the forward limit: " + ", ".join(above))
    return out("inconclusive", "INCONCLUSIVE: a mixed picture that fits neither the map nor holds-everywhere ("
               + "; ".join(reasons) + "); no headline number is printed." + ps_text,
               "mixed picture: " + "; ".join(reasons))


# ---------------------------------------------------------------- the whole file

def pool(entries, criteria, criteria_sha):
    """entries: [(path, results doc)] -> the pooled document."""
    for path, d in entries:
        if d["run"].get("criteria_file") != V3_FILE:
            raise ValueError(f"{path}: not a criteria-v3 run (run.criteria_file {d['run'].get('criteria_file')})")
    minimum = criteria["v3"]["pooling"]["minimum_jobs"]
    inputs = [{"path": p, "run_id": d["run"]["id"], "cpu_model": d["run"]["runner"]["cpu_model"] or "unknown"}
              for p, d in entries]
    runs = sorted({i["run_id"] for i in inputs})
    models = sorted({i["cpu_model"] for i in inputs})
    cpus = []
    for m in models:
        docs = [d for (p, d) in entries if (d["run"]["runner"]["cpu_model"] or "unknown") == m]
        block = analyse_cpu(m, docs, criteria)
        per_run = []
        for rid in runs:
            rd = [d for d in docs if d["run"]["id"] == rid]
            if not rd:
                continue
            if len(rd) < minimum:
                per_run.append({"run_id": rid, "jobs": len(rd), "form": None,
                                "line": f"{len(rd)} job(s): too few for a per-run verdict", "cells": None})
                continue
            if len(runs) == 1:
                rb = block
            else:
                rb = analyse_cpu(m, rd, criteria, full=False)
            per_run.append({"run_id": rid, "jobs": len(rd), "form": rb["verdict"]["form"], "line": rb["verdict"]["line"],
                            "cells": {c["cell_id"]: {"as_compiled": _compact(c["as_compiled"]),
                                                     "aligned": _compact(c["aligned"])}
                                      for c in rb["cells"] if c["size_class"] in IN_CACHE}})
        block["per_run"] = per_run
        assess = [r for r in per_run if r["form"] is not None]
        if len(assess) < 2:
            block["stability"] = "not assessable"
        elif all(r["form"] == block["verdict"]["form"] for r in assess):
            block["stability"] = "stable"
        else:
            block["stability"] = "unstable"
        block["reproduction"] = reproduction(assess)
        cpus.append(block)

    parts = []
    for b in cpus:
        nr = len(b["runs"])
        tag = f"{b['verdict']['form'].upper()} on {b['cpu_model']} ({b['jobs']} jobs, {nr} run{'s' if nr != 1 else ''}"
        if b["stability"] == "stable":
            tag += ", the same in every run with enough jobs)"
        elif b["stability"] == "unstable":
            tag += ", NOT the same in every run: " + ", ".join(
                f"{r['form'] or 'too few jobs'} in {r['run_id']}" for r in b["per_run"]) + ")"
        else:
            tag += ", stability not assessable: fewer than 2 runs with enough jobs)"
        parts.append(tag)
    page = {"form": None,
            "line": "Per CPU model, pooled over jobs and runs (no single page-level form): " + "; ".join(parts) + ".",
            "per_cpu": [{"cpu_model": b["cpu_model"], "form": b["verdict"]["form"], "jobs": b["jobs"],
                         "runs": len(b["runs"]), "stability": b["stability"]} for b in cpus]}
    return {"kind": "pooled", "criteria_file": V3_FILE, "criteria_sha256": criteria_sha, "resamples": RESAMPLES,
            "inputs": inputs, "runs": runs, "cpus": cpus, "page": page}


def reproduction(assess):
    """For every pair of assessable runs, every in-cache cell and column: is run a's point inside run b's interval?"""
    checked = outside = 0
    misses = []
    for a in assess:
        for b in assess:
            if a is b:
                continue
            for cid, cols in a["cells"].items():
                if cid not in b["cells"]:
                    continue
                for col in ("as_compiled", "aligned"):
                    pt = cols[col][0]
                    lo, hi = b["cells"][cid][col][1], b["cells"][cid][col][2]
                    checked += 1
                    if not (lo <= pt <= hi):
                        outside += 1
                        gap = 100.0 * (lo - pt) / pt if pt < lo else 100.0 * (pt - hi) / pt
                        misses.append({"cell_id": cid, "column": col, "point_run": a["run_id"],
                                       "interval_run": b["run_id"], "gap_pct": gap})
    return {"checked": checked, "outside": outside, "misses": misses}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    out = os.path.abspath(argv[1])
    entries = load_inputs(argv[2:], os.path.dirname(out))
    if not entries:
        print("no results.json found")
        return 1
    crit, sha = criteria_and_sha()
    doc = pool(entries, crit, sha)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    for b in doc["cpus"]:
        print(f"[cpu] {b['cpu_model']}: {b['verdict']['form']} ({b['jobs']} jobs, runs {', '.join(b['runs'])}), "
              f"A/A half-width {b['aa']['half_width_pct']:.3f}%, stability {b['stability']}, reproduction "
              f"{b['reproduction']['outside']}/{b['reproduction']['checked']} outside")
        print(f"      {b['verdict']['line']}")
    print(f"[page] {doc['page']['line']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
