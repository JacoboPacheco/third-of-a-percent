#!/usr/bin/env python3
"""Seed sensitivity of the Arm pool's bootstrap intervals (arm64/README.md, "The verdict, and exactly why").

The pooled verdict of the Arm column (results/s8-arm-pooled/pooled.json) is INCONCLUSIVE because one interval, the
forward add at L2 in the aligned column, ends at 1.02106 against a limit of 1.02. The interval comes from a bootstrap
whose random draws are fixed by a seed (harness/pool.py, SEED_PREFIX "20261011", set on Oct 12 2026, before the Arm runs
existed). This script asks how much of that margin is the seed: it re-draws the same bootstrap, with the same data, the
same 2000 resamples and the same code (harness/pool.py, unchanged), under other seeds.

It is a SENSITIVITY READING beside the stored verdict. It does not change the rule, a threshold, the seed or the
resample count of the pool, and the stored verdict stays the one in pooled.json.

What is re-drawn
  every statistic that enters the verdict rules of harness/criteria-v3.json for an in-cache cell:
    forward   the aligned column of every kept-SIMD cell (the rule: ci95_hi <= the forward limit)
    lost      both columns of every lost-SIMD cell (the rule: ci95_lo >= 1.5)
    placement the placement statistic D of every kept-SIMD cell (the rule: its interval excludes 1, and the loops sit
              differently against 64-byte windows; the second part is read from the listings and does not depend on a seed)
    aa        the pooled A/A control (the rule: half-width <= 2 %; it also sets the forward limit, max(2 %, 2 x half-width))
    positive  the pooled NOVEC/NONE control of every positive-control cell (the rule: ci95_lo above 1 + the A/A half-width)
  under ALT_COUNT other seeds (SEED_PATTERN), each with RESAMPLES draws, and for the first FULL_COUNT of them also the
  whole of harness/pool.py analyse_cpu (every statistic and the verdict form).
  The verdict form under each of the ALT_COUNT seeds is also derived from those statistics with the rules of
  harness/pool.py cpu_verdict, and that derivation is compared with analyse_cpu on the first FULL_COUNT seeds.
  A converged reading: the forward cells' aligned interval from CONVERGED_CHUNKS x RESAMPLES draws under the stored seed
  prefix (independent streams), so the interval ends carry no Monte-Carlo noise worth speaking of.

Usage
  python arm64/seeds.py              writes arm64/seed-sensitivity.json (about ten minutes on a 12-core machine)
  python arm64/seeds.py --check      recomputes a sample (the stored seed's own numbers, the first SAMPLE_SEEDS alternative
                                     seeds, the first CHECK_FULL whole analyses, the deciding cell's converged reading) and
                                     compares it with the stored file; about a minute (exit 0 when equal)
  python arm64/seeds.py --check --all  recomputes everything and compares with the stored file
  python arm64/seeds.py --workers N  processes to use (default: the machine's CPUs, at most 12)
The output is deterministic: the same pool gives the same file (floats equal to 1e-9 relative across platforms).
"""
import concurrent.futures
import hashlib
import json
import math
import os
import sys

# one BLAS thread per process: a pool of workers each starting a thread per core runs out of memory on a many-core machine
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402
import stats  # noqa: E402

POOLED = "results/s8-arm-pooled/pooled.json"
OUT = os.path.join(HERE, "seed-sensitivity.json")
STORED_PREFIX = pool.SEED_PREFIX            # "20261011"
RESAMPLES = pool.RESAMPLES                  # 2000
SEED_PATTERN = "seedsens-{:03d}"            # the alternative seed prefixes: seedsens-001 ... seedsens-400
ALT_COUNT = 400
FULL_COUNT = 40                             # the first 40 of them also run the whole analyse_cpu
SAMPLE_SEEDS = 8                            # per-seed interval ends of the first 8 seeds are stored for every statistic (--check)
CHECK_FULL = 2                              # --check reruns the whole analyse_cpu for this many seeds
CONVERGED_CHUNKS = 50                       # 50 x 2000 = 100 000 draws for the converged reading
DECIDING = ("k02_add_fwd.L2", "aligned")    # the cell that makes the stored form INCONCLUSIVE instead of MAP
FIXED_ON = "2026-10-12T09:41:36-04:00"      # the commit that set SEED_PREFIX in harness/pool.py (unpublished development history)


def seed_prefixes(n=ALT_COUNT):
    return [SEED_PATTERN.format(i) for i in range(1, n + 1)]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(bytes([13, 10]), bytes([10]))).hexdigest()


# ---------------------------------------------------------------- the data

class Data:
    """The pooled file, its job documents in the order the pool used, and the statistics that enter the rules."""

    def __init__(self):
        path = os.path.join(REPO, *POOLED.split("/"))
        with open(path, encoding="utf-8") as f:
            self.pooled = json.load(f)
        assert len(self.pooled["cpus"]) == 1, "the Arm pool is one CPU model"
        self.block = self.pooled["cpus"][0]
        self.cpu = self.block["cpu_model"]
        self.criteria, self.criteria_sha = pool.criteria_and_sha()
        assert self.criteria_sha == self.pooled["criteria_sha256"], "criteria-v3.json is not the file the pool was made with"
        base = os.path.dirname(path)
        paths = [i["path"] for i in self.pooled["inputs"]]
        assert paths == sorted(paths), "pool.py sorts its inputs; the bootstrap's job indices refer to that order"
        self.docs = []
        for p in paths:
            with open(os.path.join(base, p), encoding="utf-8") as f:
                self.docs.append(json.load(f))
        self.by_id = [{c["cell_id"]: c for c in d["cells"]} for d in self.docs]
        self.sha = sha(path)
        self.specs = self._specs()

    def _specs(self):
        """[(kind, cell_id, column, stat_id)] in a fixed order; the stat ids are the ones harness/pool.py analyse_cpu uses."""
        out = []
        for c in self.block["cells"]:
            if c["size_class"] not in pool.IN_CACHE:
                continue
            cid = c["cell_id"]
            if c["class"] == "kept":
                out.append(("forward", cid, "aligned", f"{cid}|aligned"))
                out.append(("placement", cid, "d", f"{cid}|placement"))
            elif c["class"] == "lost":
                out.append(("lost", cid, "as_compiled", f"{cid}|as_compiled"))
                out.append(("lost", cid, "aligned", f"{cid}|aligned"))
        out.append(("aa", "aa", "aa", "aa"))
        for pid in self.block["positive"]:
            out.append(("positive", pid, "novec", f"novec|{pid}"))
        return out

    def sides(self, kind, cid, col):
        """The per-job sample lists of one statistic: [[side0, side1, ...] per job]."""
        if kind == "aa":
            return [[d["controls"]["aa"]["a_ns"], d["controls"]["aa"]["b_ns"]] for d in self.docs]
        if kind == "positive":
            prs = [next(p for p in d["controls"]["positive"] if p["cell_id"] == cid) for d in self.docs]
            return [[p["none_ns"], p["novec_ns"]] for p in prs]
        cells = [b[cid] for b in self.by_id]
        if kind == "placement":
            return [[c["none_ns"], c["fast_ns"], c["aligned"]["none_ns"], c["aligned"]["fast_ns"]] for c in cells]
        if col == "aligned":
            return [[c["aligned"]["none_ns"], c["aligned"]["fast_ns"]] for c in cells]
        return [[c["none_ns"], c["fast_ns"]] for c in cells]

    def stored(self, kind, cid, col):
        if kind == "aa":
            return self.block["aa"]
        if kind == "positive":
            return self.block["positive"][cid]
        c = next(x for x in self.block["cells"] if x["cell_id"] == cid)
        if kind == "placement":
            return c["placement"]["d"]
        return c[col]

    def index_of(self, kind, cid, col):
        return next(i for i, s in enumerate(self.specs) if s[:3] == (kind, cid, col))


_DATA = None


def data():
    global _DATA
    if _DATA is None:
        _DATA = Data()
    return _DATA


RATIO = lambda ma, mb: mb / ma  # noqa: E731
PLACEMENT = lambda n, f, na, fa: (f / n) / (fa / na)  # noqa: E731


def combine_for(kind):
    return PLACEMENT if kind == "placement" else RATIO


def row_id(spec):
    kind, cid, col, _ = spec
    return "aa" if kind == "aa" else f"{cid}|{col}"


def stat_under(prefix, spec, resamples=RESAMPLES):
    """pool.pooled_stat of one statistic under another seed prefix (the pool's own function; only the prefix differs)."""
    kind, cid, col, sid = spec
    D = data()
    old = pool.SEED_PREFIX
    pool.SEED_PREFIX = prefix
    try:
        return pool.pooled_stat(D.cpu, sid, D.sides(kind, cid, col), combine_for(kind), resamples)
    finally:
        pool.SEED_PREFIX = old


def rstar(prefix, spec, stat_id, resamples):
    """The resampled pooled ratios behind one interval: the body of pool.pooled_stat, returning the draws themselves.
    With the stored prefix, the stored stat id and 2000 resamples it gives the stored interval exactly (replica_matches)."""
    kind, cid, col, _ = spec
    D = data()
    sbj = D.sides(kind, cid, col)
    comb = combine_for(kind)
    old = pool.SEED_PREFIX
    pool.SEED_PREFIX = prefix
    try:
        J = len(sbj)
        job_idx = pool.draws(pool.seed_for(D.cpu, stat_id, "jobs"), (resamples, J), J)
        meds = [pool._side_medians(D.cpu, stat_id, k, job_idx, [s[k] for s in sbj]) for k in range(len(sbj[0]))]
        return np.exp(np.mean(np.log(comb(*meds)), axis=1))
    finally:
        pool.SEED_PREFIX = old


# ---------------------------------------------------------------- tasks (module-level: run in worker processes)

def task_alt(prefix):
    """All rule statistics under one alternative prefix: [(ratio, lo, hi, half_width_pct)] in spec order."""
    out = []
    for spec in data().specs:
        s = stat_under(prefix, spec)
        out.append((s["ratio"], s["ci95"][0], s["ci95"][1], s["half_width_pct"]))
    return out


def task_full(prefix):
    """The whole of pool.analyse_cpu under one alternative prefix, reduced to what the verdict reads."""
    D = data()
    crit = D.criteria["verdict"]
    old = pool.SEED_PREFIX
    pool.SEED_PREFIX = prefix
    try:
        blk = pool.analyse_cpu(D.cpu, D.docs, D.criteria, full=False)
    finally:
        pool.SEED_PREFIX = old
    v = blk["verdict"]
    limit = 1.0 + v["forward_limit_pct"] / 100.0
    ps = sorted(p["cell_id"] for p in v["placement_sensitive"])
    in_cache = [c for c in blk["cells"] if c["size_class"] in pool.IN_CACHE]
    fwd = [c for c in in_cache if c["class"] == "kept" and c["cell_id"] not in ps]
    fwd_missed = [c["cell_id"] for c in fwd
                  if not (c["aligned"]["ratio"] <= crit["forward_point_max_ratio"] and c["aligned"]["ci95"][1] <= limit)]
    lost_missed = [c["cell_id"] + col for c in in_cache if c["class"] == "lost"
                   for col, key in (("", "as_compiled"), (" (aligned)", "aligned"))
                   if not c[key]["ci95"][0] >= crit["lost_ci_lo_min_ratio"]]
    dec = next(c for c in blk["cells"] if c["cell_id"] == DECIDING[0])[DECIDING[1]]
    return {"prefix": prefix, "form": v["form"], "forward_missed": fwd_missed, "lost_missed": lost_missed,
            "placement_sensitive": ps, "aa_half_width_pct": blk["aa"]["half_width_pct"],
            "forward_limit_pct": v["forward_limit_pct"], "deciding_ratio": dec["ratio"], "deciding_lo": dec["ci95"][0],
            "deciding_hi": dec["ci95"][1]}


def task_converged(index):
    """One forward statistic from CONVERGED_CHUNKS x RESAMPLES draws (independent streams under the stored prefix)."""
    spec = data().specs[index]
    kind, cid, col, sid = spec
    r = np.concatenate([rstar(STORED_PREFIX, spec, f"{sid}|conv{n:03d}", RESAMPLES) for n in range(CONVERGED_CHUNKS)])
    lo, hi = stats.percentile_interval(sorted(float(x) for x in r))
    return {"resamples": int(len(r)), "lo": lo, "hi": hi}


# ---------------------------------------------------------------- the verdict form, derived from the rule statistics

def derive_context():
    """Where each rule statistic sits in the spec order, and which kept cells have loops that sit differently (read from the
    listings by harness/pool.py, not drawn)."""
    D = data()
    ctx = {"crit": D.criteria["verdict"], "aa": None, "forward": [], "placement": [], "lost": [], "positive": [], "mech": {}}
    for i, (kind, cid, col, _) in enumerate(D.specs):
        if kind == "aa":
            ctx["aa"] = i
        elif kind == "positive":
            ctx["positive"].append(i)
        elif kind == "lost":
            ctx["lost"].append((i, cid + ("" if col == "as_compiled" else " (aligned)")))
        else:
            ctx[kind].append((i, cid))
    for c in D.block["cells"]:
        if c.get("placement"):
            ctx["mech"][c["cell_id"]] = bool(c["placement"]["mechanical"])
    return ctx


def derive(vals, ctx):
    """The verdict form that harness/pool.py cpu_verdict reaches from the statistics of one seed (vals = task_alt output).
    The checks it does not re-draw (checksums, builds, the layout A/A pairs being present, the job count) do not depend on a
    seed. The holds-everywhere branch needs every on-axis cell below the forward limit, and the lost cells' lower ends are
    4.7 and above, so it cannot be reached; that is asserted instead of assumed."""
    crit = ctx["crit"]
    aa_hw = vals[ctx["aa"]][3]
    limit = 1.0 + max(crit["forward_ci_hi_floor_pct"], crit["forward_ci_hi_aa_multiplier"] * aa_hw) / 100.0
    ps = sorted(cid for i, cid in ctx["placement"] if (vals[i][1] > 1.0 or vals[i][2] < 1.0) and ctx["mech"][cid])
    fwd = [(i, cid) for i, cid in ctx["forward"] if cid not in ps]
    fwd_missed = [cid for i, cid in fwd if not (vals[i][0] <= crit["forward_point_max_ratio"] and vals[i][2] <= limit)]
    lost_missed = [name for i, name in ctx["lost"] if not vals[i][1] >= crit["lost_ci_lo_min_ratio"]]
    positive_seen = any(vals[i][1] > 1.0 + aa_hw / 100.0 for i in ctx["positive"])
    if aa_hw > crit["aa_half_width_max_pct"] or not positive_seen:
        form = "inconclusive"
    elif ctx["lost"] and fwd and not fwd_missed and not lost_missed:
        form = "map"
    else:
        assert any(vals[i][1] > limit for i, _ in ctx["lost"]), "holds-everywhere branch not excluded"
        form = "inconclusive"
    return {"form": form, "forward_missed": fwd_missed, "lost_missed": lost_missed, "placement_sensitive": ps,
            "positive_seen": positive_seen}


# ---------------------------------------------------------------- summaries

def summ(values):
    """median, 5th and 95th percentile (linear interpolation), minimum and maximum of a list."""
    a = np.asarray(values, dtype=np.float64)
    p05, med, p95 = (float(x) for x in np.percentile(a, [5, 50, 95]))
    return {"median": med, "p05": p05, "p95": p95, "min": float(a.min()), "max": float(a.max())}


def workers_default():
    return max(1, min(12, os.cpu_count() or 1))


def reproduce():
    """Does the code of this file give the stored numbers under the stored prefix, and is rstar() the pool's own draw?"""
    D = data()
    worst = 0.0
    checked = 0
    for spec in D.specs:
        kind, cid, col, sid = spec
        s = stat_under(STORED_PREFIX, spec)
        st = D.stored(kind, cid, col)
        for a, b in ((s["ratio"], st["ratio"]), (s["ci95"][0], st["ci95"][0]), (s["ci95"][1], st["ci95"][1])):
            worst = max(worst, abs(a - b) / abs(b))
            checked += 1
    spec = D.specs[D.index_of("forward", *DECIDING)]
    r = rstar(STORED_PREFIX, spec, spec[3], RESAMPLES)
    lo, hi = stats.percentile_interval(sorted(float(x) for x in r))
    st = D.stored(*spec[:3])
    replica_ok = math.isclose(lo, st["ci95"][0], rel_tol=1e-12) and math.isclose(hi, st["ci95"][1], rel_tol=1e-12)
    return {"numbers_checked": checked, "max_rel_diff": worst}, replica_ok


def run(workers):
    D = data()
    crit = D.criteria["verdict"]
    limit = 1.0 + D.block["verdict"]["forward_limit_pct"] / 100.0
    lost_min = crit["lost_ci_lo_min_ratio"]
    aa_max = crit["aa_half_width_max_pct"]
    ps_stored = {p["cell_id"] for p in D.block["verdict"]["placement_sensitive"]}
    prefixes = seed_prefixes()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        alt = list(ex.map(task_alt, prefixes, chunksize=4))
        full = list(ex.map(task_full, prefixes[:FULL_COUNT], chunksize=1))
        fwd_idx = [i for i, s in enumerate(D.specs) if s[0] == "forward"]
        conv = dict(zip(fwd_idx, ex.map(task_converged, fwd_idx)))

    reproduced, replica_ok = reproduce()

    # the form under every seed, derived from the rule statistics, and checked against the whole analysis where that was run
    ctx = derive_context()
    derived = [derive(a, ctx) for a in alt]
    for d, f in zip(derived, full):
        assert (d["form"], sorted(d["forward_missed"]), sorted(d["lost_missed"]), d["placement_sensitive"]) == \
               (f["form"], sorted(f["forward_missed"]), sorted(f["lost_missed"]), f["placement_sensitive"]), (d, f)

    aa_i = D.index_of("aa", "aa", "aa")
    rows = []
    for i, spec in enumerate(D.specs):
        kind, cid, col, sid = spec
        st = D.stored(kind, cid, col)
        col_vals = [a[i] for a in alt]
        ratio, los, his, hws = ([c[j] for c in col_vals] for j in range(4))
        row = {"id": row_id(spec), "kind": kind, "cell_id": cid if kind != "aa" else None,
               "column": col,
               "stored": {"ratio": st["ratio"], "lo": st["ci95"][0], "hi": st["ci95"][1], "half_width_pct": st["half_width_pct"]},
               "alt": {"draws": len(alt), "ratio": ratio[0], "lo": summ(los), "hi": summ(his), "half_width_pct": summ(hws),
                       "first": [[lo_, hi_, hw_] for lo_, hi_, hw_ in zip(los[:SAMPLE_SEEDS], his[:SAMPLE_SEEDS], hws[:SAMPLE_SEEDS])]}}
        if kind == "forward":
            judged = cid not in ps_stored
            row.update({"judged": judged, "rule": "ci95_hi <= forward limit (ratio also <= forward_point_max_ratio)", "limit": limit,
                        "stored_misses_rule": not (st["ratio"] <= crit["forward_point_max_ratio"] and st["ci95"][1] <= limit)})
            row["alt"].update({"at_or_above_limit": sum(1 for h in his if h >= limit),
                               "above_limit": sum(1 for h in his if h > limit),
                               "stored_hi_at_or_below_share": sum(1 for h in his if h <= st["ci95"][1]) / len(his),
                               "above_stored": sum(1 for h in his if h > st["ci95"][1]),
                               "ratio_above_point_max": ratio[0] > crit["forward_point_max_ratio"]})
            row["converged"] = {**conv[i], "above_limit": conv[i]["hi"] > limit,
                                "ratio_check": math.isclose(ratio[0], st["ratio"], rel_tol=1e-12)}
        elif kind == "lost":
            row.update({"rule": "ci95_lo >= lost_ci_lo_min_ratio", "limit": lost_min})
            row["alt"].update({"below_limit": sum(1 for x in los if x < lost_min)})
        elif kind == "placement":
            c = next(x for x in D.block["cells"] if x["cell_id"] == cid)
            mech = c["placement"]["mechanical"]
            excl = sum(1 for lo_, hi_ in zip(los, his) if lo_ > 1.0 or hi_ < 1.0)
            row.update({"rule": "interval of D excludes 1 (and the hot loops sit differently: read from the listings)",
                        "mechanical": mech, "stored_excludes_1": c["placement"]["statistical"],
                        "stored_sensitive": c["placement"]["sensitive"]})
            row["alt"].update({"excludes_1": excl, "sensitive": excl if mech else 0})
        elif kind == "aa":
            row.update({"rule": "half-width <= aa_half_width_max_pct; forward limit = 1 + max(2 %, 2 x half-width)",
                        "limit": aa_max})
            row["alt"].update({"above_limit": sum(1 for h in hws if h > aa_max),
                               "forward_limit_above_floor": sum(1 for h in hws if 2.0 * h > crit["forward_ci_hi_floor_pct"])})
        else:
            row.update({"rule": "ci95_lo > 1 + (pooled A/A half-width) / 100 in at least one positive-control cell"})
            row["alt"].update({"seen": sum(1 for k, a in enumerate(alt) if los[k] > 1.0 + a[aa_i][3] / 100.0)})
        rows.append(row)

    dec = next(r for r in rows if r["id"] == f"{DECIDING[0]}|{DECIDING[1]}")
    di = D.index_of("forward", *DECIDING)
    upper = [a[di][2] for a in alt]
    deciding = {"cell_id": DECIDING[0], "column": DECIDING[1], "limit": limit, "stored_hi": dec["stored"]["hi"],
                "margin_over_limit": dec["stored"]["hi"] - limit,
                "alt_hi": dec["alt"]["hi"], "alt_draws": len(upper), "alt_at_or_above_limit": dec["alt"]["at_or_above_limit"],
                "alt_above_limit": dec["alt"]["above_limit"],
                "alt_share_at_or_above_limit": dec["alt"]["at_or_above_limit"] / len(upper),
                "stored_hi_at_or_below_share": dec["alt"]["stored_hi_at_or_below_share"],
                "stored_rank_from_top": 1 + dec["alt"]["above_stored"],
                "converged": dec["converged"],
                "seeds_at_or_above_limit": [prefixes[k] for k, h in enumerate(upper) if h >= limit],
                "upper_ends": upper}

    def tally(items):
        forms, miss, sets = {}, {}, {}
        for f in items:
            forms[f["form"]] = forms.get(f["form"], 0) + 1
            for cid in f["forward_missed"]:
                miss[cid] = miss.get(cid, 0) + 1
            key = ", ".join(f["placement_sensitive"])
            sets[key] = sets.get(key, 0) + 1
        return forms, miss, [{"cells": k.split(", ") if k else [], "seeds": n} for k, n in sorted(sets.items())]

    forms, miss_counts, ps_sets = tally(full)
    full_block = {"count": len(full), "prefixes": [f["prefix"] for f in full], "forms": forms,
                  "forward_missed_counts": miss_counts,
                  "lost_missed_any": any(f["lost_missed"] for f in full),
                  "placement_sets": ps_sets,
                  "aa_half_width_pct": summ([f["aa_half_width_pct"] for f in full]),
                  "forward_limit_pct": sorted({f["forward_limit_pct"] for f in full}),
                  "deciding_hi": summ([f["deciding_hi"] for f in full]),
                  "per_seed": full}
    d_forms, d_miss, d_sets = tally(derived)
    derived_block = {"basis": "the verdict form of harness/pool.py cpu_verdict applied to the statistics re-drawn under each of the "
                              "seeds (forward, lost, placement, A/A, positive control); the checks that do not depend on a seed "
                              "(checksums, builds, layout A/A pairs present, job count) are taken as they are",
                     "seeds": len(derived), "equals_analyse_cpu_on_first": len(full),
                     "forms": d_forms, "forward_missed_counts": d_miss,
                     "lost_missed_any": any(d["lost_missed"] for d in derived), "placement_sets": d_sets,
                     "positive_seen_in_all": all(d["positive_seen"] for d in derived),
                     "not_map_seeds": [prefixes[k] for k, d in enumerate(derived) if d["form"] != "map"]}

    return {
        "kind": "seed-sensitivity",
        "what": "The Arm pool's bootstrap re-drawn under seeds other than the stored one: same data, same code (harness/pool.py "
                "unchanged), same number of resamples. A sensitivity reading beside the stored verdict; it changes no rule, "
                "threshold, seed or resample count, and the stored verdict is the one in the pool file.",
        "pool": {"path": POOLED, "sha256": D.sha, "cpu_model": D.cpu, "jobs": len(D.docs), "runs": D.pooled["runs"],
                 "criteria_sha256": D.criteria_sha, "stored_form": D.block["verdict"]["form"],
                 "stored_forward_missed": sorted(r["cell_id"] for r in rows if r["kind"] == "forward" and r["judged"]
                                                 and r["stored_misses_rule"])},
        "stored_seed": {"prefix": STORED_PREFIX, "resamples": RESAMPLES, "fixed_on": FIXED_ON,
                        "fixed_in": "harness/pool.py SEED_PREFIX, unpublished development history (the public repository's "
                                    "history is a different one and cannot show the date)",
                        "reproduced": reproduced, "replica_matches": replica_ok},
        "alt_seeds": {"pattern": SEED_PATTERN, "first": 1, "count": ALT_COUNT, "resamples": RESAMPLES,
                      "percentiles": "median, 5th and 95th by linear interpolation (numpy.percentile)",
                      "sample_seeds": SAMPLE_SEEDS},
        "converged": {"chunks": CONVERGED_CHUNKS, "resamples_per_chunk": RESAMPLES, "resamples": CONVERGED_CHUNKS * RESAMPLES,
                      "seed_prefix": STORED_PREFIX, "stat_id_suffix": "|conv{n:03d}"},
        "rows": rows, "deciding_cell": deciding, "full": full_block, "derived": derived_block,
    }


# ---------------------------------------------------------------- compare and write

def same(x, y, path=""):
    """Equal up to relative 1e-9 on floats; returns the first difference or None."""
    if isinstance(x, dict) and isinstance(y, dict):
        if x.keys() != y.keys():
            return f"{path}: keys differ"
        for k in x:
            d = same(x[k], y[k], f"{path}/{k}")
            if d:
                return d
        return None
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return f"{path}: length differs"
        for i, (p, q) in enumerate(zip(x, y)):
            d = same(p, q, f"{path}[{i}]")
            if d:
                return d
        return None
    if isinstance(x, float) or isinstance(y, float):
        if x is None or y is None or not math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12):
            return f"{path}: {x} != {y}"
        return None
    return None if x == y else f"{path}: {x!r} != {y!r}"


def sample_check(workers):
    """Recompute a sample and compare it with the stored file: the stored seed's own numbers, the first SAMPLE_SEEDS
    alternative seeds for every statistic, the first CHECK_FULL whole analyses, the deciding cell's converged reading.
    Returns the list of differences."""
    D = data()
    with open(OUT, encoding="utf-8") as f:
        st = json.load(f)
    bad = []

    def cmp(label, a, b):
        d = same(a, b, label)
        if d:
            bad.append(d)

    cmp("pool/sha256", st["pool"]["sha256"], D.sha)
    cmp("pool/criteria_sha256", st["pool"]["criteria_sha256"], D.criteria_sha)
    reproduced, replica_ok = reproduce()
    cmp("stored_seed/reproduced", st["stored_seed"]["reproduced"], reproduced)
    cmp("stored_seed/replica_matches", st["stored_seed"]["replica_matches"], replica_ok)
    cmp("rows/ids", [r["id"] for r in st["rows"]], [row_id(s) for s in D.specs])
    prefixes = seed_prefixes(SAMPLE_SEEDS)
    di = D.index_of("forward", *DECIDING)
    with concurrent.futures.ProcessPoolExecutor(max_workers=max(1, min(workers, 8))) as ex:
        f_alt = ex.map(task_alt, prefixes)
        f_full = ex.map(task_full, prefixes[:CHECK_FULL])
        f_conv = ex.submit(task_converged, di)
        alt, full, conv = list(f_alt), list(f_full), f_conv.result()
    if not bad:
        for i, row in enumerate(st["rows"]):
            cmp(f"rows[{row['id']}]/alt/first", row["alt"]["first"], [[a[i][1], a[i][2], a[i][3]] for a in alt])
        cmp("full/per_seed", st["full"]["per_seed"][:CHECK_FULL], full)
        cmp("deciding_cell/converged", {k: st["deciding_cell"]["converged"][k] for k in ("resamples", "lo", "hi")}, conv)
        cmp("deciding_cell/upper_ends", st["deciding_cell"]["upper_ends"][:SAMPLE_SEEDS], [a[di][2] for a in alt])
        ctx = derive_context()
        for k, a in enumerate(alt):
            d = derive(a, ctx)
            cmp(f"derived/{prefixes[k]}", prefixes[k] in st["derived"]["not_map_seeds"], d["form"] != "map")
            if k < CHECK_FULL:
                cmp(f"derived/{prefixes[k]}/form_vs_analyse_cpu", d["form"], full[k]["form"])
    return bad


def main(argv):
    workers = workers_default()
    if "--workers" in argv:
        workers = int(argv[argv.index("--workers") + 1])
    if "--check" in argv:
        if not os.path.exists(OUT):
            print("FAIL arm64/seed-sensitivity.json is missing")
            return 1
        if "--all" in argv:
            out = run(workers)
            with open(OUT, encoding="utf-8") as f:
                stored = json.load(f)
            d = same(stored, json.loads(json.dumps(out)))
            what = "equals the full recomputation"
        else:
            bad = sample_check(workers)
            d = bad[0] if bad else None
            what = (f"equals the recomputation of its sample (the stored seed's numbers, {SAMPLE_SEEDS} alternative seeds, "
                    f"{CHECK_FULL} whole analyses, the deciding cell's converged reading)")
        print(f"arm64/seed-sensitivity.json {what}" if d is None else f"FAIL arm64/seed-sensitivity.json: {d}")
        return 0 if d is None else 1
    out = run(workers)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    dc = out["deciding_cell"]
    print(f"wrote {OUT}: stored hi {dc['stored_hi']:.5f} against {dc['limit']}; {dc['alt_at_or_above_limit']} of {dc['alt_draws']} "
          f"alternative draws at or above the limit; converged hi {dc['converged']['hi']:.5f}; "
          f"forms under the first {out['full']['count']} seeds: {out['full']['forms']}; "
          f"derived forms under all {out['derived']['seeds']}: {out['derived']['forms']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
