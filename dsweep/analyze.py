#!/usr/bin/env python3
"""Analysis of the matrix-multiply d-sweep (the rules are dsweep/PLAN.md; this file applies them mechanically).

    python3 dsweep/analyze.py <dsweep.json | dir> [...] [--out dsweep-pooled.json] [--md table.md] [--verify]
                              [--plan PATH]
        a dir means every dsweep.json under it at any depth (one run folder, a run's job folders, or a
        folder of runs); a file seen twice, by sha256, counts once. --plan PATH hashes that file instead of
        dsweep/PLAN.md (for example `git show <run commit>:dsweep/PLAN.md > plan.md`); the hash must still
        match the one every dsweep.json stores.

Reads the per-job dsweep.json files written by dsweep/sweep.py, groups them by CPU model, and for each model
with at least 3 jobs pools them with the two-level bootstrap of harness/pool.py (jobs, then repetitions; the
same counter-based generator and seed rule), fits the excess that FAST adds per inner call on d over the
L1-resident ladder, and prints the word the written rule gives: H1 (a fixed cost per inner call), H2 (a cost per
element), falls (the excess is smaller at the larger d), neither, or too few jobs. Writes dsweep-pooled.json and a
markdown table when asked. Needs numpy (as harness/pool.py does) and no compiler.

This module also holds the numbers of the rule (RULE), the d ladder (ladder()) and the file schema
(validate_doc()), so that sweep.py, the tests and the analysis cannot drift apart.
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
HARNESS = os.path.join(REPO, "harness")
if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)

import pool  # noqa: E402  (harness/pool.py: the generator, the two-level bootstrap, the placement statistic)
import run as hr  # noqa: E402  (harness/run.py: n_for, the size rule of the study)
import stats  # noqa: E402

KIND = "dsweep"
POOLED_KIND = "dsweep-pooled"
SCHEMA_VERSION = 1
KERNEL = "k08_matmul"
PLAN_FILE = os.path.join(HERE, "PLAN.md")
CRITERIA_FILE = "harness/criteria-v3.json"
MODULUS = 8   # elements per pass of the NEON loop of the Arm listing (PLAN.md, "Why one residue class")
MIN_D = 8     # the smallest d of harness/run.py's n_for
SCAN_WIDTH = MODULUS - 1
BRIDGE_POINTS = 3   # context d values between the study L1 d and the study L2 d (PLAN.md, "The d values")
MODES = ("none", "fast", "none_a64", "fast_a64")
COLUMNS = ("as_compiled", "aligned")
H1, H2, FALLS, NEITHER, TOO_FEW = "H1", "H2", "falls", "neither", "too few jobs"
PARTIAL_NAME = "dsweep.partial.jsonl"

# The numbers of the decision rule, fixed in dsweep/PLAN.md before any run. minimum_jobs and
# aa_half_width_max_pct are the values of harness/criteria-v3.json (tests/test_dsweep.py checks that).
# The words read the fixed share s of the excess that FAST adds per inner call at the study d (PLAN.md,
# "How it is analysed"): s = 1 is a fixed cost per inner call, s = 0 a cost per element, s above 1 an excess
# that is smaller at the larger d.
RULE = {
    "minimum_jobs": 3,
    "aa_half_width_max_pct": 2.0,
    "minimum_fit_points": 4,
    "baseline_max_relative_residual": 0.10,
    "excess_max_relative_residual": 0.15,
    "undefined_resamples_max_fraction": 0.025,
    "h1_share_band": [0.8, 1.2],
    "h2_share_band": [-0.2, 0.2],
    "falls_share_above": 1.2,
}

# The files whose content decides what is timed and how the numbers are made: every dsweep.json stores the
# SHA-256 of each (line endings read as LF). Jobs of one CPU model that ran different code are a file problem;
# files that differ from the tree the analysis runs in are reported beside the verdict (PLAN.md, "Records").
CODE_FILES = ("dsweep/sweep.py", "dsweep/analyze.py", "harness/run.py", "harness/pool.py", "harness/stats.py",
              "harness/placement.py", "harness/asm.py", "harness/remarks.py", "harness/cachegrind.py",
              "kernels/k08_matmul.cpp", "kernels/common.hpp")

# Pooled FAST/NONE ratios already published, as compiled, at the study L1 and L2 size (context for the
# table, never read by the rule). Source: results/s7-pooled/pooled.json (x86-64) and
# results/s8-arm-pooled/pooled.json (Neoverse-N2); tests/test_dsweep.py compares them with those files.
PUBLISHED = {
    "Neoverse-N2": {"L1": 1.548, "L2": 1.016, "source": "results/s8-arm-pooled/pooled.json"},
    "AMD EPYC 7763 64-Core Processor": {"L1": 3.190, "L2": 3.790, "source": "results/s7-pooled/pooled.json"},
    "AMD EPYC 9V45 96-Core Processor": {"L1": 4.836, "L2": 4.118, "source": "results/s7-pooled/pooled.json"},
    "AMD EPYC 9V74 80-Core Processor": {"L1": 4.245, "L2": 4.615, "source": "results/s7-pooled/pooled.json"},
}

TOP_KEYS = ("kind", "schema_version", "plan_sha256", "criteria_sha256", "code_sha256", "criteria_file", "smoke",
            "reps_per_side", "pinned_cpu", "target_ns_per_process", "run", "machine", "ladder", "timing_order",
            "builds", "aa", "points", "seconds")
RUN_KEYS = ("id", "job", "commit", "workflow_run_url", "started_at", "runner", "toolchain")
POINT_KEYS = ("d", "roles", "d_mod_8", "working_set_bytes", "l1_resident", "iters", "calibration_ns_one_call",
              "binary_sha256", "checksums", "checksum_match", "as_compiled", "aligned", "instr", "instr_note")
PAIR_KEYS = ("none_ns", "fast_ns", "order", "checksum_match", "ratio", "ci95", "half_width_pct")
AA_KEYS = ("d", "binary_sha256", "n_per_side", "iters", "a_ns", "b_ns", "ratio", "ci95", "half_width_pct")
BUILD_KEYS = ("sha256", "command", "traps", "asm_lines", "vectorization", "interleave", "elements_per_pass", "loops",
              "inner_loops", "hot_loop")


# ---------------------------------------------------------------- the plan, the criteria, the ladder

def _lf_sha256(path):
    """sha256 of a file with CRLF read as LF (git stores LF; a Windows checkout may hold CRLF)."""
    with open(path, "rb") as f:
        raw = f.read().replace(bytes([13, 10]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


def plan_sha256(path=None):
    return _lf_sha256(path or PLAN_FILE)


def criteria_sha256():
    return _lf_sha256(os.path.join(REPO, CRITERIA_FILE))


def code_sha256():
    """{repo-relative path: sha256 (line endings read as LF)} of CODE_FILES as they stand now; "missing" for a
    file that does not exist."""
    out = {}
    for rel in CODE_FILES:
        p = os.path.join(REPO, rel)
        out[rel] = _lf_sha256(p) if os.path.exists(p) else "missing"
    return out


def criteria():
    with open(os.path.join(REPO, CRITERIA_FILE), encoding="utf-8") as f:
        return json.load(f)


def reps_per_side():
    """40, read from harness/criteria-v3.json (v3.timing.reps_per_side)."""
    return criteria()["v3"]["timing"]["reps_per_side"]


def bridge_ds(d_l1, d_l2, residue):
    """BRIDGE_POINTS context d values strictly between the study L1 d and the study L2 d, in the same residue class
    modulo MODULUS as the study L1 d, evenly spaced on a log scale (Neoverse-N2: 76, 108, 148; EPYC 7763: 52, 76,
    100). They are timed to show where between the two published cells the excess goes; they are not fitted."""
    out = []
    for i in range(1, BRIDGE_POINTS + 1):
        target = d_l1 * (d_l2 / d_l1) ** (i / (BRIDGE_POINTS + 1))
        d = int(round((target - residue) / MODULUS)) * MODULUS + residue
        if d_l1 < d < d_l2 and d not in out:
            out.append(d)
    return out


def ladder(l1d_bytes, l2_bytes):
    """The d values of the sweep, from the runner's cache sizes, by the rule of harness/run.py (n_for) and
    dsweep/PLAN.md: the study L1 d and L2 d; the fit ladder (every d from MIN_D up to the study L1 d that is
    congruent to the study L1 d modulo MODULUS); the residue scan (the MODULUS - 1 values below the study L1 d);
    the bridge (context d values between the study L1 d and L2 d); the middle d (where the A/A is timed)."""
    d_l1 = hr.n_for(KERNEL, l1d_bytes // 2)
    d_l2 = hr.n_for(KERNEL, l2_bytes // 2)
    residue = d_l1 % MODULUS
    fit = [d for d in range(MIN_D, d_l1 + 1) if d % MODULUS == residue]
    scan = list(range(max(MIN_D, d_l1 - SCAN_WIDTH), d_l1))
    return {"kernel": KERNEL, "modulus": MODULUS, "residue": residue, "min_d": MIN_D, "study_l1_d": d_l1,
            "study_l2_d": d_l2, "fit": fit, "scan": scan, "bridge": bridge_ds(d_l1, d_l2, residue),
            "mid_d": fit[len(fit) // 2], "l1_resident_rule": "12*d*d <= l1d/2"}


def roles_of(lad):
    """{d: [roles]}: fit, study_l1, scan, bridge, study_l2."""
    roles = {}
    for d in lad["fit"]:
        roles.setdefault(d, []).append("fit")
    roles.setdefault(lad["study_l1_d"], []).append("study_l1")
    for d in lad["scan"]:
        roles.setdefault(d, []).append("scan")
    for d in lad["bridge"]:
        roles.setdefault(d, []).append("bridge")
    roles.setdefault(lad["study_l2_d"], []).append("study_l2")
    return roles


# ---------------------------------------------------------------- the file schema

def validate_doc(doc, reps=None):
    """Problems found in one dsweep.json by its structure alone (empty list = fine). Never raises."""
    probs = []
    if not isinstance(doc, dict):
        return ["not a JSON object"]
    if doc.get("kind") != KIND:
        return [f"kind is {doc.get('kind')!r}, not {KIND!r}"]
    if doc.get("schema_version") != SCHEMA_VERSION:
        return [f"schema_version is {doc.get('schema_version')!r}, not {SCHEMA_VERSION}"]
    miss = [k for k in TOP_KEYS if k not in doc]
    if miss:
        return ["missing " + ", ".join(miss)]
    try:
        reps = reps_per_side() if reps is None else reps
        if doc["smoke"]:
            probs.append("a smoke file (fewer repetitions than harness/criteria-v3.json): not a result")
        if doc["reps_per_side"] != reps:
            probs.append(f"reps_per_side {doc['reps_per_side']} differs from the {reps} of harness/criteria-v3.json")
        run = doc["run"]
        miss = [k for k in RUN_KEYS if k not in run]
        if miss:
            return probs + ["run: missing " + ", ".join(miss)]
        if not (run["runner"] or {}).get("cpu_model"):
            probs.append("run.runner.cpu_model is missing")
        cache = (doc["machine"] or {}).get("cache_bytes") or {}
        if "l1d" not in cache or "l2" not in cache:
            return probs + ["machine.cache_bytes lacks l1d or l2"]
        lad = ladder(cache["l1d"], cache["l2"])
        if doc["ladder"] != lad:
            probs.append(f"the stored ladder differs from the ladder recomputed from the cache sizes ({lad['fit']})")
        code = doc["code_sha256"]
        if (not isinstance(code, dict) or sorted(code) != sorted(CODE_FILES)
                or not all(isinstance(v, str) and (v == "missing" or len(v) == 64) for v in code.values())):
            probs.append("code_sha256 does not hold one hash for each of the files the plan lists")
        for mode in MODES:
            b = doc["builds"].get(mode)
            if not b or [k for k in BUILD_KEYS if k not in b]:
                probs.append(f"builds.{mode} is missing or incomplete")
        none_build = doc["builds"].get("none") or {}
        step = none_build.get("elements_per_pass")
        if step is not None and (not isinstance(step, int) or step < 1 or MODULUS % step):
            probs.append(f"the NONE loop takes {step} elements per pass (vectorization width times interleave count "
                         f"in clang's remark); a ladder in steps of {MODULUS} does not hold its leftover count fixed")
        aa = doc["aa"]
        miss = [k for k in AA_KEYS if k not in aa]
        if miss:
            probs.append("aa: missing " + ", ".join(miss))
        else:
            if aa["d"] != lad["mid_d"]:
                probs.append(f"the A/A was timed at d = {aa['d']}, not at the middle d {lad['mid_d']}")
            if len(aa["a_ns"]) != reps or len(aa["b_ns"]) != reps:
                probs.append(f"the A/A has {len(aa['a_ns'])} and {len(aa['b_ns'])} samples, not {reps}")
        want = roles_of(lad)
        seen = []
        for p in doc["points"]:
            miss = [k for k in POINT_KEYS if k not in p]
            if miss:
                probs.append(f"a point is missing {', '.join(miss)}")
                continue
            d = p["d"]
            seen.append(d)
            if want.get(d) != p["roles"]:
                probs.append(f"d = {d}: roles {p['roles']} differ from the expected {want.get(d)}")
            if p["binary_sha256"] != {m: doc["builds"][m]["sha256"] for m in MODES if m in doc["builds"]}:
                probs.append(f"d = {d}: the binaries timed are not the binaries in builds")
            if not p["checksum_match"]:
                probs.append(f"d = {d}: the builds printed different checksums")
            for col in COLUMNS:
                pr = p[col]
                miss = [k for k in PAIR_KEYS if k not in pr]
                if miss:
                    probs.append(f"d = {d}, {col}: missing {', '.join(miss)}")
                    continue
                if not pr["checksum_match"]:
                    probs.append(f"d = {d}, {col}: NONE and FAST printed different checksums")
                if len(pr["none_ns"]) != reps or len(pr["fast_ns"]) != reps:
                    probs.append(f"d = {d}, {col}: {len(pr['none_ns'])} and {len(pr['fast_ns'])} samples, not {reps}")
        if sorted(seen) != sorted(want):
            probs.append(f"the points are {sorted(seen)}, expected {sorted(want)}")
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        probs.append(f"the file does not have the expected shape ({type(e).__name__}: {e})")
    return probs


def verify_job(doc, resamples=stats.RESAMPLES):
    """Recomputes every stored ratio, interval and half-width of one dsweep.json from its raw samples
    (harness/stats.py, the within-job bootstrap sweep.py used). Returns the problems found."""
    probs = []

    def same(label, stored, s):
        if stored["ratio"] != s["ratio"]:
            probs.append(f"{label}: stored ratio {stored['ratio']} != recomputed {s['ratio']}")
        elif list(stored["ci95"]) != list(s["ci95"]):
            probs.append(f"{label}: stored ci95 {stored['ci95']} != recomputed {s['ci95']}")
        elif stored["half_width_pct"] != s["half_width_pct"]:
            probs.append(f"{label}: stored half_width_pct differs from the recomputed one")

    def summ(a, b):
        lo, hi = stats.bootstrap_ratio_ci(a, b, resamples=resamples)
        return {"ratio": stats.ratio_of_medians(a, b), "ci95": [lo, hi], "half_width_pct": stats.half_width_pct((lo, hi))}

    aa = doc["aa"]
    same("aa", aa, summ(aa["a_ns"], aa["b_ns"]))
    for p in doc["points"]:
        for col in COLUMNS:
            same(f"d = {p['d']}, {col}", p[col], summ(p[col]["none_ns"], p[col]["fast_ns"]))
    return probs


# ---------------------------------------------------------------- loading

def _file_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def find_files(paths):
    """Every dsweep.json under the given files and folders (any depth), each distinct file (by sha256) once."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += glob.glob(os.path.join(p, "**", "dsweep.json"), recursive=True)
        elif os.path.isfile(p):
            if os.path.basename(p) != PARTIAL_NAME:   # a partial file is listed by find_incomplete, never loaded as a result
                files.append(p)
        else:
            raise SystemExit(f"dsweep: {p} is neither a file nor a folder")
    seen, out = set(), []
    for q in sorted(set(files), key=lambda x: os.path.abspath(x).replace("\\", "/")):
        h = _file_sha256(q)
        if h not in seen:
            seen.add(h)
            out.append(q)
    return out


def _job_key(doc, file_sha):
    """The sort key of a job: (run id, job number, content hash). It does not depend on where the file lies, so the
    job order that the bootstrap's job indices refer to (and so the intervals) is the same for any folder layout,
    on Linux and on Windows."""
    run = doc.get("run") if isinstance(doc, dict) else None
    run = run if isinstance(run, dict) else {}
    job = str(run.get("job"))
    return (str(run.get("id")), len(job), job, file_sha)


def load_entries(paths, base_dir):
    """[(path relative to base_dir with '/', doc)], sorted by (run id, job number, content hash) (see _job_key)."""
    loaded = []
    for x in find_files(paths):
        with open(x, encoding="utf-8") as fh:
            doc = json.load(fh)
        rel = os.path.relpath(os.path.abspath(x), base_dir).replace("\\", "/")
        loaded.append((_job_key(doc, _file_sha256(x)), rel, doc))
    loaded.sort(key=lambda t: t[0])
    return [(rel, doc) for _, rel, doc in loaded]


def find_incomplete(paths, base_dir):
    """The jobs that began a sweep and left a dsweep.partial.jsonl but no dsweep.json next to it (a job that
    aborted or was cancelled after its first timing). They are listed in the output and never pooled."""
    cands = []
    for p in paths:
        if os.path.isdir(p):
            cands += glob.glob(os.path.join(p, "**", PARTIAL_NAME), recursive=True)
        elif os.path.basename(p) == PARTIAL_NAME and os.path.isfile(p):
            cands.append(p)
    out = []
    for c in sorted({os.path.abspath(x) for x in cands}, key=lambda x: x.replace("\\", "/")):
        if os.path.exists(os.path.join(os.path.dirname(c), "dsweep.json")):
            continue
        header, done, starting = {}, [], None
        with open(c, encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                try:
                    rec = json.loads(ln)
                except ValueError:
                    continue   # a line cut short by a killed process
                if not isinstance(rec, dict):
                    continue
                if rec.get("kind") == "dsweep-partial":
                    header = rec
                elif "point" in rec and isinstance(rec["point"], dict):
                    done.append(rec["point"].get("d"))
                elif "starting" in rec:
                    starting = rec["starting"]
        run = header.get("run") or {}
        out.append({"path": os.path.relpath(c, base_dir).replace("\\", "/"), "run_id": str(run.get("id")),
                    "job": str(run.get("job")), "cpu_model": (run.get("runner") or {}).get("cpu_model"),
                    "points_expected": header.get("points_expected"), "points_done": len(done), "d_done": done,
                    "last_d_started": starting})
    return out


# ---------------------------------------------------------------- numerics

def ols(x, y):
    """Ordinary least squares of y (..., n) on x (n,): returns (intercept (...), slope (...)). Equal weights."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    xc = x - x.mean()
    ym = y.mean(axis=-1)
    slope = ((y - ym[..., None]) * xc).sum(axis=-1) / float((xc * xc).sum())
    return ym - slope * x.mean(), slope


def _interval(values):
    """The 95% percentile interval of the finite-or-infinite (not NaN) values, as [lo, hi]."""
    v = np.asarray(values, dtype=np.float64).ravel()
    v = np.sort(v[~np.isnan(v)])
    if v.size == 0:
        return [float("nan"), float("nan")]
    lo, hi = stats.percentile_interval(v.tolist())
    return [float(lo), float(hi)]


def jsonable(x):
    """Recursively turns numpy scalars into numbers and non-finite floats into null."""
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return jsonable(x.tolist())
    if isinstance(x, np.generic):
        x = x.item()
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    return x


def joint_bootstrap(cpu, column, by_d, ds, resamples):
    """Bootstrap medians of both sides at every d in `ds`, with the SAME drawn jobs for every d (so the
    dependence between the d values of one job is kept). by_d[j][d] is the point of job j at d.
    Returns (med_none, med_fast), each of shape (resamples, jobs, len(ds))."""
    J = len(by_d)
    job_idx = pool.draws(pool.seed_for(cpu, f"dsweep|{column}|jobs", "jobs"), (resamples, J), J)
    med_n, med_f = [], []
    for d in ds:
        sid = f"dsweep|{column}|d{d}"
        med_n.append(pool._side_medians(cpu, sid, 0, job_idx, [b[d][column]["none_ns"] for b in by_d]))
        med_f.append(pool._side_medians(cpu, sid, 1, job_idx, [b[d][column]["fast_ns"] for b in by_d]))
    return np.stack(med_n, axis=2), np.stack(med_f, axis=2)


# ---------------------------------------------------------------- one column (as compiled / aligned) of one CPU model

def column_analysis(cpu, docs, column, aa_hw_pct, resamples=pool.RESAMPLES):
    """Everything the rule reads for one column, plus the descriptive views. All floats may be inf or NaN
    here; jsonable() maps them to null when the pooled file is written."""
    lad = docs[0]["ladder"]
    by_d = [{p["d"]: p for p in doc["points"]} for doc in docs]
    all_ds = sorted(by_d[0])
    fit_ds = list(lad["fit"])
    d_min, d_max = fit_ds[0], fit_ds[-1]
    idx = {d: i for i, d in enumerate(all_ds)}
    fit_idx = [idx[d] for d in fit_ds]
    J = len(docs)
    B = resamples

    med_n, med_f = joint_bootstrap(cpu, column, by_d, all_ds, resamples)          # (B, J, nd)
    pn = np.array([[statistics.median(b[d][column]["none_ns"]) for d in all_ds] for b in by_d])   # (J, nd)
    pf = np.array([[statistics.median(b[d][column]["fast_ns"]) for d in all_ds] for b in by_d])
    logs = np.log(pf / pn)                                                        # (J, nd)
    R = np.exp(logs.mean(axis=0))
    Rs = np.exp(np.log(med_f / med_n).mean(axis=1))                               # (B, nd)

    rows = []
    for i, d in enumerate(all_ds):
        lo, hi = _interval(Rs[:, i])
        rows.append({"d": d, "roles": by_d[0][d]["roles"], "d_mod_8": d % MODULUS,
                     "working_set_bytes": by_d[0][d]["working_set_bytes"], "ratio": float(R[i]), "ci95": [lo, hi],
                     "half_width_pct": (hi - lo) / 2.0 * 100.0, "jobs": J,
                     "excess_ns_per_inner": float(np.mean((pf[:, i] - pn[:, i]) / (d * d))),
                     "per_job": [float(math.exp(v)) for v in logs[:, i]],
                     "between_job_sd_pct": (100.0 * float(np.std(logs[:, i], ddof=1)) if J > 1 else None)})

    x = np.array(fit_ds, dtype=np.float64)
    Rf, Rsf = R[fit_idx], Rs[:, fit_idx]

    # condition 5: the cost is seen at every fit d
    threshold = 1.0 + aa_hw_pct / 100.0
    unseen = [r["d"] for r in rows if r["d"] in fit_ds and not r["ci95"][0] > threshold]

    # condition 6: each build's time per inner call is affine in d (per job, then the median over jobs)
    inner = np.array(fit_ds, dtype=np.float64) ** 2
    worst = []
    for j in range(J):
        w = 0.0
        for side in (pn, pf):
            t = side[j, fit_idx] / inner
            a0, s0 = ols(x, t)
            pred = a0 + s0 * x
            with np.errstate(divide="ignore", invalid="ignore"):
                rel = np.abs(t - pred) / np.abs(pred)
            w = max(w, float(np.max(rel)) if np.all(np.isfinite(rel)) else float("inf"))
        worst.append(w)
    baseline = {"median_max_relative_residual": float(statistics.median(worst)), "per_job": worst}

    # The rule's statistic: the excess that FAST adds per inner call, t_F - t_N, in units of that job's t_N per inner
    # call at d_max (so that hosts of different speed pool), averaged over jobs and fitted as fixed + per_element * d
    # over the fit ladder. Its fixed share at the study d, s = fixed / (fixed + per_element * d_max), is 1 for a fixed
    # cost per inner call, 0 for a cost per element, above 1 for an excess that is smaller at the larger d. The same
    # share, as the factor by which the fitted excess grows from d_min to d_max, is g = 1 / (r + s * (1 - r)),
    # r = d_min / d_max.
    dd = np.array(all_ds, dtype=np.float64) ** 2
    scale = (pn[:, idx[d_max]] / dd[idx[d_max]])[:, None]
    delta = (((pf - pn) / dd) / scale).mean(axis=0)[fit_idx]
    k0, l0 = ols(x, delta)
    e_max0, e_min0 = k0 + l0 * d_max, k0 + l0 * d_min
    scale_b = (med_n[:, :, idx[d_max]] / dd[idx[d_max]])[:, :, None]
    delta_b = ((((med_f - med_n) / dd) / scale_b).mean(axis=1))[:, fit_idx]
    kb, lb = ols(x, delta_b)
    e_max_b, e_min_b = kb + lb * d_max, kb + lb * d_min
    good = e_max_b > 0
    n_def = int(good.sum())
    with np.errstate(divide="ignore", invalid="ignore"):
        share0 = k0 / e_max0 if e_max0 > 0 else float("nan")
        shareb = np.where(good, kb / np.where(good, e_max_b, 1.0), np.nan)
        growth0 = float("nan") if not e_max0 > 0 else (e_max0 / e_min0 if e_min0 > 0 else float("inf"))
        growthb = np.where(good, np.where(e_min_b > 0, e_max_b / np.where(e_min_b > 0, e_min_b, 1.0), np.inf), np.nan)

    # per job, the excess in ns per inner call is fitted by a line over the fit ladder; the largest absolute residual
    # divided by the job's mean excess over the fit ladder (the median over jobs is condition 7)
    ex_worst = []
    for j in range(J):
        t = (pf[j, fit_idx] - pn[j, fit_idx]) / inner
        a0, s0 = ols(x, t)
        m = float(np.mean(t))
        ex_worst.append(float(np.max(np.abs(t - (a0 + s0 * x))) / m) if m > 0 else float("inf"))
    excess = {"fixed": float(k0), "per_element_at_d_max": float(l0 * d_max), "fixed_ci95": _interval(kb),
              "per_element_at_d_max_ci95": _interval(lb * d_max), "at_d_min": float(e_min0), "at_d_max": float(e_max0),
              "share": float(share0), "share_ci95": _interval(shareb), "growth": float(growth0),
              "growth_ci95": _interval(growthb),
              "residual": {"median_max_relative_residual": float(statistics.median(ex_worst)), "per_job": ex_worst},
              "resamples": B, "defined_resamples": n_def, "undefined_fraction": 1.0 - n_def / B,
              "meaning": "(t_F - t_N) per inner call / t_N(d_max) = fixed + per_element*d over the fit ladder; "
                         "share = fixed / (fixed + per_element*d_max); growth = fitted excess at d_max over the fitted "
                         "excess at d_min = 1 / (r + share*(1 - r)), r = d_min/d_max"}

    # descriptive y view: y = 1 / (R - 1) on d. Decides nothing: it only says that the excess grows more slowly than
    # the time per inner call, which every shape short of a pure per-element cost does (PLAN.md, "Changes made before any run").
    with np.errstate(divide="ignore", invalid="ignore"):
        if np.all(Rf > 1.0):
            a1, s1 = ols(x, 1.0 / (Rf - 1.0))
            y_lo, y_hi = a1 + s1 * d_min, a1 + s1 * d_max
            q_hat = float("nan") if not y_hi > 0 else (y_hi / y_lo if y_lo > 0 else float("inf"))
        else:
            a1 = s1 = q_hat = float("nan")
        ok = (Rsf > 1.0).all(axis=1)
        ys = 1.0 / (Rsf[ok] - 1.0)
        ab, sb = ols(x, ys) if ys.shape[0] else (np.array([]), np.array([]))
        yb_lo, yb_hi = ab + sb * d_min, ab + sb * d_max
        gy = yb_hi > 0
        qb = np.where(yb_lo > 0, yb_hi / np.where(yb_lo > 0, yb_lo, 1.0), np.inf)
    n_def_y = int(gy.sum())
    y_view = {"alpha": float(a1), "slope": float(s1), "slope_ci95": _interval(sb[gy]), "q": float(q_hat),
              "q_ci95": _interval(qb[gy]), "resamples": B, "defined_resamples": n_def_y,
              "undefined_fraction": 1.0 - n_def_y / B,
              "meaning": "y = 1/(R-1) = alpha + slope*d over the fit ladder; q = y_hat(d_max)/y_hat(d_min); decides nothing"}

    # descriptive inverse view: R - 1 on 1/d
    u = 1.0 / x
    a2, s2 = ols(u, Rf - 1.0)
    a2b, s2b = ols(u, Rsf - 1.0)
    inverse_view = {"intercept": float(a2), "slope": float(s2), "intercept_ci95": _interval(a2b),
                    "slope_ci95": _interval(s2b),
                    "meaning": "R - 1 = intercept + slope/d; a fixed cost with a small a: intercept near 0, slope c/b; "
                               "a cost per element: slope near 0; decides nothing"}

    return {"column": column, "fit_ds": fit_ds, "rows": rows, "aa_half_width_pct": aa_hw_pct,
            "cost_threshold": threshold, "cost_unseen": unseen, "baseline": baseline, "excess": excess,
            "y_view": y_view, "inverse_view": inverse_view}


def _within(point, ci, band):
    """True when the point estimate and the whole 95% interval lie inside [band[0], band[1]]."""
    return bool(band[0] <= point <= band[1] and band[0] <= ci[0] and ci[1] <= band[1])


def decide_column(J, problems, col, rule=RULE):
    """(word, reason) of one column, by the conditions of dsweep/PLAN.md in their order."""
    if J < rule["minimum_jobs"]:
        return TOO_FEW, f"{J} job(s) of this CPU model; the minimum is {rule['minimum_jobs']}"
    if problems:
        return NEITHER, "file problems: " + "; ".join(problems)
    if col["aa_half_width_pct"] > rule["aa_half_width_max_pct"]:
        return NEITHER, (f"the pooled byte-identical A/A has a half-width of {col['aa_half_width_pct']:.2f}%, above "
                         f"{rule['aa_half_width_max_pct']}%")
    if len(col["fit_ds"]) < rule["minimum_fit_points"]:
        return NEITHER, f"{len(col['fit_ds'])} fit d values; the minimum is {rule['minimum_fit_points']}"
    if col["cost_unseen"]:
        return NEITHER, ("the cost is not separated from the A/A noise at d = "
                         + ", ".join(str(d) for d in col["cost_unseen"]))
    resid = col["baseline"]["median_max_relative_residual"]
    if not resid <= rule["baseline_max_relative_residual"]:
        return NEITHER, (f"the time per inner call is not affine in d (median largest relative residual {resid:.3f}, "
                         f"above {rule['baseline_max_relative_residual']})")
    ex = col["excess"]
    resid_ex = ex["residual"]["median_max_relative_residual"]
    if not resid_ex <= rule["excess_max_relative_residual"]:
        return NEITHER, (f"the excess per inner call is not a straight line in d (median largest residual {resid_ex:.3f} "
                         f"of the mean excess, above {rule['excess_max_relative_residual']}), so a fixed part and a "
                         "per-element part do not describe it")
    if not ex["undefined_fraction"] <= rule["undefined_resamples_max_fraction"]:
        return NEITHER, (f"{100 * ex['undefined_fraction']:.1f}% of the resamples have a fitted excess at the study d at "
                         f"or below 0 (no share), above {100 * rule['undefined_resamples_max_fraction']:.1f}%")
    s, ci = ex["share"], ex["share_ci95"]
    if math.isnan(s):
        return NEITHER, "the fitted excess at the study d is at or below 0: no fixed share"
    shown = f"fixed share {_fmt_q(s)} (95% {_fmt_q(ci[0])} to {_fmt_q(ci[1])})"
    h1, h2, up = rule["h1_share_band"], rule["h2_share_band"], rule["falls_share_above"]
    if _within(s, ci, h1):
        return H1, f"{shown}, inside {h1[0]} to {h1[1]}: the excess per inner call is the same at every d"
    if _within(s, ci, h2):
        return H2, f"{shown}, inside {h2[0]} to {h2[1]}: the excess per inner call is proportional to d"
    if s > up and ci[0] > up:
        return FALLS, f"{shown}, above {up}: the excess per inner call is smaller at the larger d"
    return NEITHER, (f"{shown}: not inside the H1 band {h1[0]} to {h1[1]}, the H2 band {h2[0]} to {h2[1]}, "
                     f"or above {up}")


def _fmt_q(q):
    if q is None or (isinstance(q, float) and math.isnan(q)):
        return "undefined"
    return "unbounded" if q == float("inf") else f"{q:.3f}"


def headline(wc, wa):
    """The headline word from the (word, reason) of the as-compiled and the aligned column."""
    if wc[0] == TOO_FEW:
        return {"word": TOO_FEW, "reason": wc[1], "columns_agree": True}
    if wc[0] == wa[0]:
        return {"word": wc[0], "reason": wc[1], "columns_agree": True}
    return {"word": NEITHER, "columns_agree": False,
            "reason": (f"the two columns disagree: as compiled {wc[0]} ({wc[1]}); aligned {wa[0]} ({wa[1]}). "
                       "Moving the loops is the control that was varied, and a word that does not survive it is not claimed")}


# ---------------------------------------------------------------- the other views of one CPU model

def placement_view(cpu, docs, by_d, all_ds, resamples):
    """The criteria-v3 placement statistic for every d: the pooled ratio of the as-compiled to the aligned FAST/NONE
    ratio with its two-level interval, and whether the hot loops of NONE and FAST sit differently against 64-byte
    windows (one yes or no: the binaries are the same for every d)."""
    mech, hn, hf = pool.placement_differs({"loops": {"none": docs[0]["builds"]["none"]["loops"],
                                                     "fast": docs[0]["builds"]["fast"]["loops"]}})
    rows = []
    for d in all_ds:
        quads = [(b[d]["as_compiled"]["none_ns"], b[d]["as_compiled"]["fast_ns"],
                  b[d]["aligned"]["none_ns"], b[d]["aligned"]["fast_ns"]) for b in by_d]
        st = pool.placement_stat(cpu, f"dsweep|placement|d{d}", quads, resamples)
        stat_part = st["ci95"][0] > 1.0 or st["ci95"][1] < 1.0
        rows.append({"d": d, "d_ratio": st["ratio"], "ci95": st["ci95"], "statistical": stat_part, "mechanical": mech,
                     "sensitive": bool(stat_part and mech)})
    return {"hot_none": pool._short(hn), "hot_fast": pool._short(hf), "mechanical": mech, "rows": rows,
            "sensitive_ds": [r["d"] for r in rows if r["sensitive"]]}


def instruction_view(by_d, all_ds, fit_ds):
    """Cachegrind counts: instructions, not time. The counts are deterministic, so the jobs must agree."""
    rows, agree = [], True
    for d in all_ds:
        vals = {json.dumps(b[d].get("instr"), sort_keys=True) for b in by_d}
        if len(vals) > 1:
            agree = False
        ins = by_d[0][d].get("instr")
        if not ins:
            rows.append({"d": d, "none_per_inner": None, "fast_per_inner": None, "ratio": None, "extra_per_inner": None})
            continue
        n_in, f_in = ins["none"] / (d * d), ins["fast"] / (d * d)
        rows.append({"d": d, "none_per_inner": n_in, "fast_per_inner": f_in, "ratio": ins["fast"] / ins["none"],
                     "extra_per_inner": f_in - n_in})
    pts = [r for r in rows if r["d"] in fit_ds and r["extra_per_inner"] is not None]
    fit = None
    if len(pts) >= 2:
        a, s = ols([r["d"] for r in pts], [r["extra_per_inner"] for r in pts])
        fit = {"intercept": float(a), "slope": float(s),
               "meaning": "extra instructions per inner call = intercept + slope*d over the fit ladder: "
                          "H1 predicts slope 0, H2 predicts intercept 0 (instructions, not time)"}
    return {"label": "instructions, not time", "jobs_agree": agree, "rows": rows, "fit": fit}


# ---------------------------------------------------------------- one CPU model, given its jobs

def file_problems(docs, plan_sha, crit_sha):
    """Problems with the files of one CPU model, per file and across files. Empty list = usable."""
    probs = []
    for doc in docs:
        who = f"job {(doc.get('run') or {}).get('job')} of run {(doc.get('run') or {}).get('id')}" if isinstance(doc, dict) else "a file"
        for p in validate_doc(doc):
            probs.append(f"{who}: {p}")
        if isinstance(doc, dict) and doc.get("plan_sha256") != plan_sha:
            probs.append(f"{who}: the stored plan hash is not the hash of dsweep/PLAN.md as it stands")
        if isinstance(doc, dict) and doc.get("criteria_sha256") != crit_sha:
            probs.append(f"{who}: the stored criteria hash is not the hash of {CRITERIA_FILE} as it stands")
    if probs:
        return probs
    if len({json.dumps(d["ladder"], sort_keys=True) for d in docs}) > 1:
        probs.append("the d ladders differ between jobs")
    for mode in MODES:
        if len({d["builds"][mode]["sha256"] for d in docs}) > 1:
            probs.append(f"the {mode} binaries differ between jobs")
    if len({json.dumps(d["code_sha256"], sort_keys=True) for d in docs}) > 1:
        differing = sorted({p for d in docs for p in CODE_FILES if d["code_sha256"][p] != docs[0]["code_sha256"][p]})
        probs.append("jobs of this CPU model ran different code (" + ", ".join(differing) + "): pool runs started from "
                     "one commit")
    return probs


def analyse_cpu(cpu, items, plan_sha, crit_sha, resamples=pool.RESAMPLES, code_now=None):
    docs = [d for _, d in items]
    J = len(docs)
    block = {"cpu_model": cpu, "jobs": J,
             "runs": sorted({str((d.get("run") or {}).get("id")) for d in docs if isinstance(d, dict)}),
             "inputs": [rel for rel, _ in items]}
    problems = file_problems(docs, plan_sha, crit_sha)
    block["problems"] = problems
    cols = {c: None for c in COLUMNS}
    block["code_changed_since_run"] = []
    if not problems:
        now = code_sha256() if code_now is None else code_now
        block["code_changed_since_run"] = sorted(p for p in CODE_FILES if docs[0]["code_sha256"][p] != now.get(p))
        by_d = [{p["d"]: p for p in doc["points"]} for doc in docs]
        all_ds = sorted(by_d[0])
        block["ladder"] = docs[0]["ladder"]
        block["builds"] = {m: {k: docs[0]["builds"][m][k]
                               for k in ("sha256", "traps", "vectorization", "elements_per_pass", "hot_loop", "inner_loops")}
                           for m in MODES}
        aa = pool.pair_stat(cpu, "dsweep|aa", [(d["aa"]["a_ns"], d["aa"]["b_ns"]) for d in docs], resamples)
        block["aa"] = {"d": docs[0]["aa"]["d"], **{k: aa[k] for k in ("ratio", "ci95", "half_width_pct", "per_job")}}
        for c in COLUMNS:
            cols[c] = column_analysis(cpu, docs, c, aa["half_width_pct"], resamples)
        block["placement"] = placement_view(cpu, docs, by_d, all_ds, resamples)
        block["instructions"] = instruction_view(by_d, all_ds, docs[0]["ladder"]["fit"])
        pub = PUBLISHED.get(cpu)
        if pub:
            block["published"] = pub
    block["columns"] = cols
    words = {c: decide_column(J, problems, cols[c]) for c in COLUMNS}
    block["words"] = {c: {"word": w, "reason": r} for c, (w, r) in words.items()}
    block["verdict"] = headline(words["as_compiled"], words["aligned"])
    nr = len(block["runs"])
    block["line"] = (f"On {cpu} ({J} job{'s' if J != 1 else ''}, {nr} run{'s' if nr != 1 else ''} pooled): "
                     f"{block['verdict']['word']}.")
    return block


def analyse(entries, resamples=pool.RESAMPLES, plan_path=None, incomplete=None):
    """entries: [(relative path, dsweep doc)] -> the pooled document. `incomplete` is find_incomplete()'s list of
    jobs that left a partial file and no result; they are listed, never pooled."""
    plan_sha, crit_sha, code_now = plan_sha256(plan_path), criteria_sha256(), code_sha256()
    by_cpu = {}
    for rel, d in entries:
        cpu = ((d.get("run") or {}).get("runner") or {}).get("cpu_model") if isinstance(d, dict) else None
        by_cpu.setdefault(cpu or "unknown", []).append((rel, d))
    cpus = [analyse_cpu(m, items, plan_sha, crit_sha, resamples, code_now) for m, items in sorted(by_cpu.items())]
    return {"kind": POOLED_KIND, "schema_version": SCHEMA_VERSION, "plan_sha256": plan_sha,
            "plan_file": str(plan_path).replace("\\", "/") if plan_path else "dsweep/PLAN.md",
            "criteria_sha256": crit_sha, "criteria_file": CRITERIA_FILE, "code_sha256": code_now, "rule": RULE,
            "resamples": resamples, "seed_prefix": pool.SEED_PREFIX,
            "inputs": [{"path": rel, "run_id": str((d.get("run") or {}).get("id")), "job": str((d.get("run") or {}).get("job")),
                        "cpu_model": ((d.get("run") or {}).get("runner") or {}).get("cpu_model") or "unknown"}
                       for rel, d in entries if isinstance(d, dict)],
            "incomplete_jobs": list(incomplete or []),
            "cpus": cpus,
            "line": "; ".join(b["line"] for b in cpus) or "no jobs"}


# ---------------------------------------------------------------- printing

def _ci(x, fmt="{:.3f}"):
    lo, hi = x["ci95"]
    return f"{fmt.format(x['ratio'])} [{fmt.format(lo)}, {fmt.format(hi)}]"


def render_markdown(an):
    out = []
    for b in an["cpus"]:
        out.append(f"### {b['cpu_model']}: {b['verdict']['word']}")
        out.append("")
        out.append(f"{b['line']} {b['verdict']['reason']}")
        out.append("")
        out.append(f"- jobs {b['jobs']}, runs {', '.join(b['runs'])}")
        for c in COLUMNS:
            w = b["words"][c]
            out.append(f"- {c.replace('_', ' ')}: {w['word']} ({w['reason']})")
        if b["problems"]:
            out.append("- file problems:")
            out += [f"  - {p}" for p in b["problems"]]
        if b.get("code_changed_since_run"):
            out.append("- NOTE: these files differ from the ones the jobs ran with (see git): "
                       + ", ".join(b["code_changed_since_run"]))
        if b["columns"]["as_compiled"] is not None:
            c = b["columns"]["as_compiled"]
            ex, y1, v2 = c["excess"], c["y_view"], c["inverse_view"]
            out.append(f"- A/A (the same binary against a copy, d = {b['aa']['d']}): ratio {b['aa']['ratio']:.4f}, "
                       f"half-width {b['aa']['half_width_pct']:.3f}%")
            out.append(f"- the rule's statistic, the excess per inner call in units of t_N(d_max) over the fit ladder "
                       f"{c['fit_ds']}: fixed {ex['fixed']:.4g} [{ex['fixed_ci95'][0]:.4g}, {ex['fixed_ci95'][1]:.4g}], "
                       f"per-element part at d_max {ex['per_element_at_d_max']:.4g} [{ex['per_element_at_d_max_ci95'][0]:.4g}, "
                       f"{ex['per_element_at_d_max_ci95'][1]:.4g}]; fixed share {_fmt_q(ex['share'])} "
                       f"[{_fmt_q(ex['share_ci95'][0])}, {_fmt_q(ex['share_ci95'][1])}]; growth of the fitted excess from "
                       f"d_min to d_max {_fmt_q(ex['growth'])} [{_fmt_q(ex['growth_ci95'][0])}, "
                       f"{_fmt_q(ex['growth_ci95'][1])}]; undefined resamples {100 * ex['undefined_fraction']:.1f}%")
            out.append(f"- time per inner call affine in d: median largest relative residual "
                       f"{c['baseline']['median_max_relative_residual']:.4f} (limit {RULE['baseline_max_relative_residual']}); "
                       f"excess affine in d: {ex['residual']['median_max_relative_residual']:.4f} "
                       f"(limit {RULE['excess_max_relative_residual']})")
            out.append(f"- y view (decides nothing), 1/(R-1) = {y1['alpha']:.4g} + {y1['slope']:.4g} d, slope 95% "
                       f"[{y1['slope_ci95'][0]:.4g}, {y1['slope_ci95'][1]:.4g}]; dilution Q = {_fmt_q(y1['q'])} "
                       f"[{_fmt_q(y1['q_ci95'][0])}, {_fmt_q(y1['q_ci95'][1])}]")
            out.append(f"- inverse view (decides nothing), R - 1 = {v2['intercept']:.4g} + {v2['slope']:.4g}/d (slope 95% "
                       f"[{v2['slope_ci95'][0]:.4g}, {v2['slope_ci95'][1]:.4g}])")
            out.append("")
            out.append("| d | role | d mod 8 | FAST/NONE as compiled [95%] | aligned [95%] | excess ns per inner call | "
                       "placement D | extra instr per inner call (not time) | published |")
            out.append("|---|---|---|---|---|---|---|---|---|")
            al = {r["d"]: r for r in b["columns"]["aligned"]["rows"]}
            pl = {r["d"]: r for r in b["placement"]["rows"]}
            ir = {r["d"]: r for r in b["instructions"]["rows"]}
            pub = b.get("published") or {}
            for r in c["rows"]:
                d = r["d"]
                role = "+".join(r["roles"])
                extra = ir[d]["extra_per_inner"]
                p = pub.get("L1") if "study_l1" in r["roles"] else pub.get("L2") if "study_l2" in r["roles"] else None
                out.append(f"| {d} | {role} | {r['d_mod_8']} | {_ci(r)} | {_ci(al[d])} | {r['excess_ns_per_inner']:.3f} | "
                           f"{pl[d]['d_ratio']:.3f}{' *' if pl[d]['sensitive'] else ''} | "
                           f"{'-' if extra is None else format(extra, '.2f')} | {'-' if p is None else format(p, '.3f')} |")
            out.append("")
            out.append("Rows with role fit enter the fit; scan, bridge and study_l2 are context. `*` marks a "
                       "placement-sensitive d (criteria-v3 rule). Published = the pooled as-compiled ratio already "
                       "published for this CPU model (a sanity reading, not a criterion).")
        out.append("")
    if not an["cpus"]:
        out.append("no jobs")
    if an.get("incomplete_jobs"):
        out.append("### Jobs that began a sweep and left no result (listed, not pooled, not replaced)")
        out.append("")
        for j in an["incomplete_jobs"]:
            out.append(f"- {j['path']}: run {j['run_id']}, job {j['job']}, {j['points_done']} of {j['points_expected']} d "
                       f"values timed (done: {j['d_done']}; last started: {j['last_d_started']})")
        out.append("")
    return "\n".join(out) + "\n"


def report(an):
    lines = []
    for b in an["cpus"]:
        lines.append(f"[cpu] {b['cpu_model']}: {b['verdict']['word']} ({b['jobs']} jobs, runs {', '.join(b['runs'])})")
        lines.append(f"      {b['verdict']['reason']}")
        for p in b["problems"]:
            lines.append(f"      problem: {p}")
        if b.get("code_changed_since_run"):
            lines.append("      note: these files differ from the ones the jobs ran with: "
                         + ", ".join(b["code_changed_since_run"]))
    if not an["cpus"]:
        lines.append("no jobs")
    for j in an.get("incomplete_jobs") or []:
        lines.append(f"[incomplete] {j['path']}: {j['points_done']} of {j['points_expected']} d values timed, not pooled")
    return "\n".join(lines)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    def take(flag):
        if flag in argv:
            i = argv.index(flag)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return None

    out, md, plan = take("--out"), take("--md"), take("--plan")
    verify = "--verify" in argv
    if verify:
        argv.remove("--verify")
    if not argv:
        print(__doc__)
        return 2
    if plan is not None and not os.path.isfile(plan):
        raise SystemExit(f"dsweep: --plan {plan} is not a file")
    base = os.path.dirname(os.path.abspath(out)) if out else os.getcwd()
    entries = load_entries(argv, base)
    incomplete = find_incomplete(argv, base)
    if not entries:
        print("no dsweep.json found")
        for j in incomplete:
            print(f"[incomplete] {j['path']}: run {j['run_id']}, job {j['job']}, {j['points_done']} of "
                  f"{j['points_expected']} d values timed (last started: {j['last_d_started']}); not pooled")
        return 1
    if verify:
        bad = 0
        for rel, d in entries:
            probs = validate_doc(d) or verify_job(d)
            for p in probs:
                print(f"{rel}: {p}")
            bad += bool(probs)
        print(f"verified {len(entries)} file(s): {bad} with problems")
        return 1 if bad else 0
    an = analyse(entries, plan_path=plan, incomplete=incomplete)
    print(report(an))
    table = render_markdown(an)
    print()
    print(table)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(jsonable(an), f, indent=1)
            f.write("\n")
        print(f"wrote {out}")
    if md:
        with open(md, "w", encoding="utf-8") as f:
            f.write(table)
        print(f"wrote {md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
