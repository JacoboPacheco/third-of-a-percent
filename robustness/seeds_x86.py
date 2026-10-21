#!/usr/bin/env python3
"""Seed sensitivity of the x86-64 pool's borderline verdicts (robustness/README-seeds-x86.md).

The pooled verdicts of results/s7-pooled/pooled.json (95 jobs) rest on 95 % bootstrap intervals whose random draws are
fixed by a seed (harness/pool.py, SEED_PREFIX "20261011", 2000 resamples). Where an interval end sits close to the line a
rule draws, the verdict can depend on the seed. This script asks, for every such cell, what the end would have been under
other seeds. The Arm pool got the same reading (arm64/seeds.py -> arm64/seed-sensitivity.json); this is the x86-64 version,
written to the same pattern and run with the pool's own code (harness/pool.py, imported, unchanged), the same data, the same
number of resamples and the same two-level resampling.

It is a SENSITIVITY READING beside the stored verdicts. It changes no rule, threshold, seed or resample count, and the stored
verdicts stay the ones in pooled.json.

WHICH CELLS (the selection rule; recomputed from pooled.json, stored in the output under "selection")
  Models: every CPU model of the pool with at least harness/criteria-v3.json v3.pooling.minimum_jobs (3) jobs. The model with
  one job has no verdict to test and is listed under "skipped_models".
  The forward rule (criteria-v3): an in-cache cell of a loop that kept its vectorization is judged on its aligned column; it
  passes when its point ratio is at most forward_point_max_ratio and its 95 % upper end is at most the model's forward limit
  (1 + max(2 %, 2 x the pooled A/A half-width); 1.02 for every model here). The placement exemption takes a cell out of that
  rule when its placement statistic D (the pooled ratio of the as-compiled to the aligned FAST/NONE ratio) has an interval that
  excludes 1 AND the hot loops of NONE and FAST sit differently against 64-byte windows (the second part is read from the
  listings; no seed enters it).
  F  "forward": every in-cache kept cell whose aligned upper end lies within NEAR (0.01) of the forward limit, on either side,
     whether the stored verdict judges it or has it exempt (an exempt cell is judged under the seeds where its exemption
     fails). The drawn statistic is the aligned upper end; the line is the forward limit.
  P  "placement": every in-cache kept cell whose hot loops sit differently (so the exemption is possible), whose aligned
     reading is within reach of the forward rule (upper end at or above limit - NEAR, or point ratio above the point maximum;
     so the exemption decides whether a cell that matters is judged), and whose D interval has an end within NEAR of 1. The
     drawn statistic is both ends of D; the line is 1.
  The A/A control, the lost-vectorization cells (lower ends of 4.7 and above against a minimum of 1.5) and the positive
  controls are far from their lines; they are not selected, and the whole analyses below re-draw them anyway.

WHAT IS DRAWN
  For each selected cell: the statistic under ALT_COUNT (400) other seed prefixes (SEED_PATTERN), each with the pool's 2000
  resamples; the stored seed's rank among them; and a converged reading from CONVERGED_CHUNKS x 2000 = 100 000 draws under the
  stored prefix (independent streams), with its Monte Carlo sd. Then, for each model that has a selected cell, the whole of
  harness/pool.py analyse_cpu (every statistic and the verdict form) under the first WHOLE_COUNT (60) of the other seeds.
  For seeds 1 to 60 the whole analysis and the single-cell draw are the same draw; the script asserts that they agree.

Usage (single process; one BLAS thread)
  python robustness/seeds_x86.py                 same as --verify
  python robustness/seeds_x86.py --verify        recompute a sample and compare it with the stored file (about five minutes):
                                                 the selection, the stored seed's numbers, every F cell under all 400 seeds,
                                                 every P cell under the first 100 seeds, the F cells' converged readings, the
                                                 first 10 whole analyses of the models with 10 jobs or fewer and the first 3 of
                                                 the larger ones, and the summaries derived from the stored lists
  python robustness/seeds_x86.py --verify --all  recompute everything and compare (about twenty minutes)
  python robustness/seeds_x86.py --full          regenerate robustness/seed-sensitivity-x86.json (about twenty minutes)
  python robustness/seeds_x86.py --tables       print the tables of robustness/README-seeds-x86.md from the stored file (instant)
  --model SUBSTR   only the models whose name contains SUBSTR        --seeds N   alternative seeds per cell to recompute
                   (a sample run: the converged readings are skipped when --seeds is given, unless --all)
  --whole N        whole analyses per model to recompute             --file PATH   the stored file to compare with / write
Exit code 0 when equal, 1 on any difference. The output is deterministic: the same pool gives the same file (floats equal
to 1e-9 relative across platforms).
"""
import hashlib
import json
import math
import os
import re
import sys
import time

# one BLAS thread: nothing here needs more, and the verifying test suite runs beside other processes
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402
import stats  # noqa: E402

POOLED = "results/s7-pooled/pooled.json"
OUT = os.path.join(HERE, "seed-sensitivity-x86.json")
STORED_PREFIX = pool.SEED_PREFIX            # "20261011"
RESAMPLES = pool.RESAMPLES                  # 2000
SEED_PATTERN = "seedsens-{:03d}"            # the alternative seed prefixes: seedsens-001 ... seedsens-400
ALT_COUNT = 400
WHOLE_COUNT = 60                            # the first 60 of them also run the whole analyse_cpu
CONVERGED_CHUNKS = 50                       # 50 x 2000 = 100 000 draws for the converged reading
CONVERGED_BATCHES = 10                      # the second Monte Carlo estimate: 10 batches of 10 000 draws
NEAR = 0.01                                 # "close to the line"
VERIFY_ALT_P = 100                          # --verify: alternative seeds recomputed for a P cell (an F cell: all of them)
VERIFY_WHOLE_SMALL = 10                     # --verify: whole analyses per model with at most SMALL_JOBS jobs
VERIFY_WHOLE_LARGE = 3                      # ... and per larger model (each one costs about ten seconds)
SMALL_JOBS = 10

RATIO = lambda ma, mb: mb / ma  # noqa: E731
PLACEMENT = lambda n, f, na, fa: (f / n) / (fa / na)  # noqa: E731


def seed_prefixes(n=ALT_COUNT):
    return [SEED_PATTERN.format(i) for i in range(1, n + 1)]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(bytes([13, 10]), bytes([10]))).hexdigest()


# ---------------------------------------------------------------- the data

class Model:
    """One CPU model of the pool: its job documents in the order the pool used, and its stored block."""

    def __init__(self, block, docs, criteria):
        self.cpu = block["cpu_model"]
        self.block = block
        self.docs = docs
        self.by_id = [{c["cell_id"]: c for c in d["cells"]} for d in docs]
        self.crit = criteria["verdict"]
        v = block["verdict"]
        self.limit = 1.0 + v["forward_limit_pct"] / 100.0
        self.exempt = {p["cell_id"] for p in v["placement_sensitive"]}
        self.cells = {c["cell_id"]: c for c in block["cells"]}


class Data:
    def __init__(self, path=None):
        path = path or os.path.join(REPO, *POOLED.split("/"))
        with open(path, encoding="utf-8") as f:
            self.pooled = json.load(f)
        self.criteria, self.criteria_sha = pool.criteria_and_sha()
        assert self.criteria_sha == self.pooled["criteria_sha256"], "criteria-v3.json is not the file the pool was made with"
        assert self.pooled["resamples"] == RESAMPLES
        self.sha = sha(path)
        self.min_jobs = self.criteria["v3"]["pooling"]["minimum_jobs"]
        base = os.path.dirname(path)
        inputs = self.pooled["inputs"]
        paths = [i["path"] for i in inputs]
        assert paths == sorted(paths), "pool.py sorts its inputs; the bootstrap's job indices refer to that order"
        self.models = []
        self.skipped = []
        for block in self.pooled["cpus"]:
            if block["jobs"] < self.min_jobs:
                self.skipped.append({"cpu_model": block["cpu_model"], "jobs": block["jobs"]})
                continue
            docs = []
            for i in inputs:
                if i["cpu_model"] == block["cpu_model"]:
                    with open(os.path.join(base, i["path"]), encoding="utf-8") as f:
                        docs.append(json.load(f))
            assert len(docs) == block["jobs"], block["cpu_model"]
            self.models.append(Model(block, docs, self.criteria))

    def model(self, cpu):
        return next(m for m in self.models if m.cpu == cpu)


_DATA = None


def data():
    global _DATA
    if _DATA is None:
        _DATA = Data()
    return _DATA


# ---------------------------------------------------------------- the selection

def stat_name(kind):
    return "aligned" if kind == "forward" else "placement"


def cell_sides(model, kind, cid):
    """The per-job sample lists of one statistic: [[side0, side1, ...] per job]."""
    cells = [b[cid] for b in model.by_id]
    if kind == "forward":
        return [[c["aligned"]["none_ns"], c["aligned"]["fast_ns"]] for c in cells]
    return [[c["none_ns"], c["fast_ns"], c["aligned"]["none_ns"], c["aligned"]["fast_ns"]] for c in cells]


def screen_model(model):
    """One row per in-cache kept cell: the numbers the selection rule reads, and whether the rule selects it."""
    crit = model.crit
    rows = []
    for c in model.block["cells"]:
        if c["size_class"] not in pool.IN_CACHE or c["class"] != "kept":
            continue
        a, p = c["aligned"], c["placement"]
        gap = a["ci95"][1] - model.limit
        near1 = min(abs(e - 1.0) for e in p["d"]["ci95"])
        in_reach = a["ci95"][1] >= model.limit - NEAR or a["ratio"] > crit["forward_point_max_ratio"]
        pick_f = abs(gap) <= NEAR
        pick_p = bool(p["mechanical"]) and in_reach and near1 <= NEAR
        rows.append({"cell_id": c["cell_id"], "judged": c["cell_id"] not in model.exempt,
                     "aligned_ratio": a["ratio"], "aligned_hi": a["ci95"][1], "gap_to_limit": gap,
                     "d_ci95": p["d"]["ci95"], "d_nearest_end_gap_to_1": near1,
                     "hot_loops_differ": bool(p["mechanical"]), "stored_exempt": bool(p["sensitive"]),
                     "selected": [k for k, ok in (("forward", pick_f), ("placement", pick_p)) if ok]})
    return rows


def select(d):
    """[(model, kind, cell_id)] in a fixed order, and the screen rows per model."""
    specs = []
    screen = {}
    for m in d.models:
        rows = screen_model(m)
        screen[m.cpu] = rows
        for r in rows:
            for kind in r["selected"]:
                specs.append((m, kind, r["cell_id"]))
    return specs, screen


def spec_id(m, kind, cid):
    return f"{m.cpu}|{kind}|{cid}"


# ---------------------------------------------------------------- the draws

def combine_for(kind):
    return RATIO if kind == "forward" else PLACEMENT


def stat_under(m, kind, cid, prefix, resamples=RESAMPLES):
    """pool.pooled_stat of one statistic under another seed prefix (the pool's own function; only the prefix differs)."""
    old = pool.SEED_PREFIX
    pool.SEED_PREFIX = prefix
    try:
        return pool.pooled_stat(m.cpu, f"{cid}|{stat_name(kind)}", cell_sides(m, kind, cid), combine_for(kind), resamples)
    finally:
        pool.SEED_PREFIX = old


def rstar(m, kind, cid, prefix, stat_id, resamples):
    """The resampled pooled ratios behind one interval: the body of pool.pooled_stat, returning the draws themselves.
    With the stored prefix, the stored stat id and 2000 resamples it gives the stored interval exactly (replica_matches)."""
    sbj = cell_sides(m, kind, cid)
    comb = combine_for(kind)
    old = pool.SEED_PREFIX
    pool.SEED_PREFIX = prefix
    try:
        J = len(sbj)
        job_idx = pool.draws(pool.seed_for(m.cpu, stat_id, "jobs"), (resamples, J), J)
        meds = [pool._side_medians(m.cpu, stat_id, k, job_idx, [s[k] for s in sbj]) for k in range(len(sbj[0]))]
        return np.exp(np.mean(np.log(comb(*meds)), axis=1))
    finally:
        pool.SEED_PREFIX = old


def alt_draws(m, kind, cid, n, first=1):
    """[(lo, hi)] under seeds first .. first + n - 1 of SEED_PATTERN."""
    out = []
    for i in range(first, first + n):
        s = stat_under(m, kind, cid, SEED_PATTERN.format(i))
        out.append((s["ci95"][0], s["ci95"][1]))
    return out


def converged(m, kind, cid):
    """The statistic from CONVERGED_CHUNKS x 2000 draws under the stored prefix (stat id suffix |conv000 ...), its Monte Carlo
    sd from the chunks and, as a check, from CONVERGED_BATCHES batches."""
    sid = f"{cid}|{stat_name(kind)}"
    chunks = [rstar(m, kind, cid, STORED_PREFIX, f"{sid}|conv{n:03d}", RESAMPLES) for n in range(CONVERGED_CHUNKS)]
    ends = [stats.percentile_interval(sorted(float(x) for x in c)) for c in chunks]
    allr = np.concatenate(chunks)
    lo, hi = stats.percentile_interval(sorted(float(x) for x in allr))
    per = len(chunks) // CONVERGED_BATCHES
    bends = [stats.percentile_interval(sorted(float(x) for x in np.concatenate(chunks[b * per:(b + 1) * per])))
             for b in range(CONVERGED_BATCHES)]
    sd = lambda xs, k: float(np.std(xs, ddof=1) / math.sqrt(k))  # noqa: E731
    out = {"resamples": int(len(allr)), "lo": lo, "hi": hi,
           "mc_sd_lo": sd([e[0] for e in ends], CONVERGED_CHUNKS), "mc_sd_hi": sd([e[1] for e in ends], CONVERGED_CHUNKS),
           "mc_sd_hi_from_batches": sd([e[1] for e in bends], CONVERGED_BATCHES),
           "chunk_sd_hi": float(np.std([e[1] for e in ends], ddof=1))}
    if kind == "placement":
        out["excludes_1"] = bool(lo > 1.0 or hi < 1.0)
    else:
        out["margin_to_limit"] = hi - m.limit
        out["above_limit"] = bool(hi > m.limit)
    return out


def reproduce(d, specs):
    """Does the code of this file give the stored numbers under the stored prefix, and is rstar() the pool's own draw?"""
    worst, checked, replica_ok = 0.0, 0, True
    for m, kind, cid in specs:
        c = m.cells[cid]
        st = c["aligned"] if kind == "forward" else c["placement"]["d"]
        s = stat_under(m, kind, cid, STORED_PREFIX)
        for a, b in ((s["ratio"], st["ratio"]), (s["ci95"][0], st["ci95"][0]), (s["ci95"][1], st["ci95"][1])):
            worst = max(worst, abs(a - b) / abs(b))
            checked += 1
        r = rstar(m, kind, cid, STORED_PREFIX, f"{cid}|{stat_name(kind)}", RESAMPLES)
        lo, hi = stats.percentile_interval(sorted(float(x) for x in r))
        replica_ok &= math.isclose(lo, st["ci95"][0], rel_tol=1e-12) and math.isclose(hi, st["ci95"][1], rel_tol=1e-12)
    return {"numbers_checked": checked, "max_rel_diff": worst}, bool(replica_ok)


# ---------------------------------------------------------------- the whole analysis

def whole_analysis(d, m, prefix, selected):
    """pool.analyse_cpu of one model under another seed prefix, reduced to what the verdict reads, plus the selected cells'
    statistics (selected: [(kind, cell_id)])."""
    crit = d.criteria["verdict"]
    old = pool.SEED_PREFIX
    pool.SEED_PREFIX = prefix
    try:
        blk = pool.analyse_cpu(m.cpu, m.docs, d.criteria, full=False)
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
    by = {c["cell_id"]: c for c in blk["cells"]}
    sel = {}
    for kind, cid in selected:
        if kind == "forward":
            sel[f"{cid}|forward"] = by[cid]["aligned"]["ci95"][1]
        else:
            sel[f"{cid}|placement"] = list(by[cid]["placement"]["d"]["ci95"])
    return {"prefix": prefix, "form": v["form"], "forward_missed": fwd_missed, "lost_missed": lost_missed,
            "placement_sensitive": ps, "aa_half_width_pct": blk["aa"]["half_width_pct"],
            "forward_limit_pct": v["forward_limit_pct"], "selected": sel}


# ---------------------------------------------------------------- summaries (pure functions of the stored lists)

def summ(values):
    a = np.asarray(values, dtype=np.float64)
    p05, p10, med, p90, p95 = (float(x) for x in np.percentile(a, [5, 10, 50, 90, 95]))
    return {"n": int(a.size), "median": med, "mean": float(a.mean()), "sd": float(a.std(ddof=1)), "min": float(a.min()),
            "max": float(a.max()), "p05": p05, "p10": p10, "p90": p90, "p95": p95}


def rank_pct(values, x):
    """Percent of the values below x (values equal to x count half): the percentile of x among them."""
    a = np.asarray(values, dtype=np.float64)
    return 100.0 * (float(np.sum(a < x)) + 0.5 * float(np.sum(a == x))) / a.size


def cell_summary(m, kind, cid, his, los):
    """The numbers derived from the stored per-seed lists of one cell (his, los: lists of 400 interval ends)."""
    c = m.cells[cid]
    if kind == "forward":
        st = c["aligned"]
        n = len(his)
        return {"hi": summ(his), "stored_hi_percentile": rank_pct(his, st["ci95"][1]), "limit": m.limit,
                "at_or_above_limit": sum(1 for h in his if h >= m.limit), "above_limit": sum(1 for h in his if h > m.limit),
                "share_at_or_above_limit": sum(1 for h in his if h >= m.limit) / n,
                "above_stored": sum(1 for h in his if h > st["ci95"][1])}
    st = c["placement"]["d"]
    n = len(his)
    above = sum(1 for lo in los if lo > 1.0)
    below = sum(1 for hi in his if hi < 1.0)
    excl = sum(1 for lo, hi in zip(los, his) if lo > 1.0 or hi < 1.0)
    return {"lo": summ(los), "hi": summ(his), "stored_lo_percentile": rank_pct(los, st["ci95"][0]),
            "stored_hi_percentile": rank_pct(his, st["ci95"][1]), "line": 1.0,
            "excludes_1_above": above, "excludes_1_below": below, "excludes_1": excl, "share_excludes_1": excl / n}


def tally(items):
    forms, miss, sets = {}, {}, {}
    for f in items:
        forms[f["form"]] = forms.get(f["form"], 0) + 1
        for cid in f["forward_missed"]:
            miss[cid] = miss.get(cid, 0) + 1
        key = ", ".join(f["placement_sensitive"])
        sets[key] = sets.get(key, 0) + 1
    n = len(items)
    return {"count": n, "forms": forms, "form_shares": {k: v / n for k, v in forms.items()},
            "forward_missed_counts": miss,
            "lost_missed_any": any(f["lost_missed"] for f in items),
            "placement_sets": [{"cells": k.split(", ") if k else [], "seeds": v} for k, v in sorted(sets.items())],
            "aa_half_width_pct": summ([f["aa_half_width_pct"] for f in items]),
            "forward_limit_pct": sorted({f["forward_limit_pct"] for f in items})}


# ---------------------------------------------------------------- build the whole file

def log(*a):
    print(*a, file=sys.stderr, flush=True)


def build():
    d = data()
    specs, screen = select(d)
    t0 = time.time()
    reproduced, replica_ok = reproduce(d, specs)
    log(f"stored seed reproduced: max rel diff {reproduced['max_rel_diff']:.2e}, replica {replica_ok} ({time.time() - t0:.0f} s)")
    prefixes = seed_prefixes()
    cells = []
    for m, kind, cid in specs:
        t = time.time()
        pairs = alt_draws(m, kind, cid, ALT_COUNT)
        los, his = [p[0] for p in pairs], [p[1] for p in pairs]
        cv = converged(m, kind, cid)
        c = m.cells[cid]
        st = c["aligned"] if kind == "forward" else c["placement"]["d"]
        row = {"id": spec_id(m, kind, cid), "cpu_model": m.cpu, "jobs": len(m.docs), "kind": kind, "cell_id": cid,
               "column": "aligned" if kind == "forward" else "placement D",
               "stored": {"ratio": st["ratio"], "lo": st["ci95"][0], "hi": st["ci95"][1], "half_width_pct": st["half_width_pct"],
                          "judged": cid not in m.exempt, "exempt": cid in m.exempt,
                          "hot_loops_differ": bool(c["placement"]["mechanical"]),
                          "d_excludes_1": bool(c["placement"]["statistical"])},
               "alt": {"draws": len(his), "hi_list": his, "summary": cell_summary(m, kind, cid, his, los)},
               "converged": cv}
        if kind == "placement":
            row["alt"]["lo_list"] = los
        else:
            row["stored"]["point_ratio_ok"] = st["ratio"] <= d.criteria["verdict"]["forward_point_max_ratio"]
        cells.append(row)
        log(f"{row['id']}: {time.time() - t:.0f} s")

    whole = {}
    for m in d.models:
        sel = [(k, cid) for mm, k, cid in specs if mm is m]
        if not sel:
            continue
        t = time.time()
        stored_seed = whole_analysis(d, m, STORED_PREFIX, sel)
        assert stored_seed["form"] == m.block["verdict"]["form"], f"{m.cpu}: the stored seed does not give the stored form"
        per_seed = [whole_analysis(d, m, p, sel) for p in prefixes[:WHOLE_COUNT]]
        # seeds 1..60: the whole analysis and the single-cell draws are the same draw
        for row in cells:
            if row["cpu_model"] != m.cpu:
                continue
            key = f"{row['cell_id']}|{row['kind']}"
            for i, ps in enumerate(per_seed):
                got = ps["selected"][key]
                want = row["alt"]["hi_list"][i] if row["kind"] == "forward" else [row["alt"]["lo_list"][i], row["alt"]["hi_list"][i]]
                assert same(got, want, key) is None, (key, i, got, want)
        whole[m.cpu] = {"jobs": len(m.docs), "stored_form": m.block["verdict"]["form"], "stored_seed_form": stored_seed["form"],
                        "stored_placement_sensitive": sorted(m.exempt),
                        "tally": tally(per_seed), "per_seed": per_seed}
        log(f"whole analyses of {m.cpu}: {time.time() - t:.0f} s: {whole[m.cpu]['tally']['forms']}")

    return {
        "kind": "seed-sensitivity-x86",
        "what": "The x86-64 pool's bootstrap intervals re-drawn under seeds other than the stored one, for the cells whose "
                "interval end lies close to the line a rule draws: same data, same code (harness/pool.py unchanged), same "
                "number of resamples. A sensitivity reading beside the stored verdicts; it changes no rule, threshold, seed or "
                "resample count, and the stored verdicts are the ones in the pool file.",
        "pool": {"path": POOLED, "sha256": d.sha, "criteria_sha256": d.criteria_sha, "resamples": RESAMPLES,
                 "jobs": len(d.pooled["inputs"]), "runs": d.pooled["runs"],
                 "models": [{"cpu_model": m.cpu, "jobs": len(m.docs), "stored_form": m.block["verdict"]["form"],
                             "forward_limit": m.limit} for m in d.models]},
        "selection": {"near": NEAR, "minimum_jobs": d.min_jobs, "screen": screen, "skipped_models": d.skipped,
                      "rule": "see the header of robustness/seeds_x86.py: F = an in-cache kept cell whose aligned upper end is "
                              "within near of the forward limit; P = an in-cache kept cell whose hot loops sit differently, "
                              "whose aligned reading is at or above limit - near (or whose point ratio is above the maximum) "
                              "and whose placement statistic D has an end within near of 1"},
        "stored_seed": {"prefix": STORED_PREFIX, "resamples": RESAMPLES, "reproduced": reproduced, "replica_matches": replica_ok},
        "alt_seeds": {"pattern": SEED_PATTERN, "first": 1, "count": ALT_COUNT, "resamples": RESAMPLES,
                      "seed_list": prefixes,
                      "sd": "sample standard deviation (ddof 1) of the 400 interval ends",
                      "percentiles": "median, 5th, 10th, 90th and 95th by linear interpolation (numpy.percentile); the stored "
                                     "seed's percentile is the percent of the 400 ends below its end, ties counting half"},
        "converged": {"chunks": CONVERGED_CHUNKS, "resamples_per_chunk": RESAMPLES, "resamples": CONVERGED_CHUNKS * RESAMPLES,
                      "batches": CONVERGED_BATCHES, "seed_prefix": STORED_PREFIX, "stat_id_suffix": "|conv{n:03d}",
                      "mc_sd": "sd of the interval end over the chunks (each an independent 2000-draw stream under the "
                               "stored prefix) divided by sqrt(chunks): a quantile's sd falls as 1/sqrt(draws); "
                               "mc_sd_hi_from_batches is the same from 10 batches of 10 000 draws, as a check"},
        "cells": cells,
        "whole": {"count": WHOLE_COUNT, "prefixes": prefixes[:WHOLE_COUNT], "models": whole},
    }


# ---------------------------------------------------------------- compare and verify

def same(x, y, path=""):
    """Equal up to relative 1e-9 on floats; returns the first difference or None."""
    if isinstance(x, dict) and isinstance(y, dict):
        if x.keys() != y.keys():
            return f"{path}: keys differ ({sorted(set(x) ^ set(y))[:4]})"
        for k in x:
            r = same(x[k], y[k], f"{path}/{k}")
            if r:
                return r
        return None
    if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
        if len(x) != len(y):
            return f"{path}: length {len(x)} != {len(y)}"
        for i, (p, q) in enumerate(zip(x, y)):
            r = same(p, q, f"{path}[{i}]")
            if r:
                return r
        return None
    if isinstance(x, float) or isinstance(y, float):
        if x is None or y is None or not math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12):
            return f"{path}: {x} != {y}"
        return None
    return None if x == y else f"{path}: {x!r} != {y!r}"


def derived_from_lists(d, st):
    """Recompute, from the stored per-seed lists alone, every summary and tally the file prints. Returns the differences."""
    bad = []
    specs, _ = select(d)
    by_id = {spec_id(m, k, c): (m, k, c) for m, k, c in specs}
    for row in st["cells"]:
        m, kind, cid = by_id[row["id"]]
        his = row["alt"]["hi_list"]
        los = row["alt"].get("lo_list", [])
        r = same(row["alt"]["summary"], json.loads(json.dumps(cell_summary(m, kind, cid, his, los))), row["id"] + "/summary")
        if r:
            bad.append(r)
    for cpu, w in st["whole"]["models"].items():
        r = same(w["tally"], json.loads(json.dumps(tally(w["per_seed"]))), cpu + "/tally")
        if r:
            bad.append(r)
    return bad


# ---------------------------------------------------------------- the tables of robustness/README-seeds-x86.md

def short_name(cpu):
    """'AMD EPYC 9V45 96-Core Processor' -> 'EPYC 9V45'; 'Intel(R) Xeon(R) 6973P-C' -> 'Xeon 6973P-C'."""
    m = re.search(r"EPYC (\w+)", cpu, re.I)
    if m:
        return "EPYC " + m.group(1)
    m = re.search(r"(\d{4}[A-Z]?(?:-[A-Z])?)\s*$", cpu)
    return "Xeon " + m.group(1) if m else cpu


def tables(st):
    """The three markdown tables of robustness/README-seeds-x86.md, built from a stored file: {name: [lines]}. The README
    carries these lines verbatim and tests/test_seeds_x86.py compares them, so no number in them is typed by hand."""
    fwd = ["| Model (jobs) | Cell | Stored verdict | Stored end | Rank of the stored end among the 400 (%) | Median of the 400 | sd of the 400 "
           "| Smallest to largest | Seeds at or above the limit | Converged end (sd of that estimate) | Converged end minus the limit |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    plc = ["| Model (jobs) | Cell | Stored interval of D | Smallest low end to largest high end of the 400 | Seeds whose interval excludes 1 "
           "| Converged interval of D | Converged interval excludes 1 |",
           "|---|---|---|---|---|---|---|"]
    for r in st["cells"]:
        who = f"{short_name(r['cpu_model'])} ({r['jobs']})"
        sm, cv, s0 = r["alt"]["summary"], r["converged"], r["stored"]
        if r["kind"] == "forward":
            fwd.append(f"| {who} | `{r['cell_id']}` | {'judged' if s0['judged'] else 'left out'} | {s0['hi']:.4f} | "
                       f"{sm['stored_hi_percentile']:.1f} | {sm['hi']['median']:.4f} | {sm['hi']['sd']:.4f} | "
                       f"{sm['hi']['min']:.4f} to {sm['hi']['max']:.4f} | {sm['at_or_above_limit']} | "
                       f"{cv['hi']:.4f} ({cv['mc_sd_hi']:.5f}) | {cv['margin_to_limit']:+.4f} |")
        else:
            plc.append(f"| {who} | `{r['cell_id']}` | {s0['lo']:.4f} to {s0['hi']:.4f} | "
                       f"{sm['lo']['min']:.4f} to {sm['hi']['max']:.4f} | {sm['excludes_1']} of {sm['hi']['n']} | "
                       f"{cv['lo']:.4f} to {cv['hi']:.4f} | {'yes' if cv['excludes_1'] else 'no'} |")
    whole = ["| Model (jobs) | Stored word | Words under the first 60 other seeds | Cells that miss the forward rule (seeds) "
             "| Cells left out as placement-sensitive (seeds) |",
             "|---|---|---|---|---|"]
    for cpu, w in st["whole"]["models"].items():
        t = w["tally"]
        words = ", ".join(f"{f.upper()} {t['forms'][f]}" for f in sorted(t["forms"], key=lambda f: (f != "map", f)))
        miss = "; ".join(f"`{c}` ({n})" for c, n in sorted(t["forward_missed_counts"].items())) or "none"
        left = "; ".join(", ".join(f"`{c}`" for c in x["cells"]) + f" ({x['seeds']})" for x in t["placement_sets"]) or "none"
        whole.append(f"| {short_name(cpu)} ({w['jobs']}) | {w['stored_form'].upper()} | {words} | {miss} | {left} |")
    return {"forward": fwd, "placement": plc, "whole": whole}


def verify(file=None, all_=False, model=None, seeds=None, whole=None):
    """Recompute a sample (or everything) and compare it with the stored file. Returns the list of differences."""
    d = data()
    with open(file or OUT, encoding="utf-8") as f:
        st = json.load(f)
    bad = []

    def cmp(label, a, b):
        r = same(a, b, label)
        if r:
            bad.append(r)

    cmp("pool/sha256", st["pool"]["sha256"], d.sha)
    cmp("pool/criteria_sha256", st["pool"]["criteria_sha256"], d.criteria_sha)
    specs, screen = select(d)
    cmp("selection/screen", st["selection"]["screen"], json.loads(json.dumps(screen)))
    cmp("selection/skipped_models", st["selection"]["skipped_models"], d.skipped)
    cmp("cells/ids", [r["id"] for r in st["cells"]], [spec_id(*s) for s in specs])
    if bad:
        return bad
    bad += derived_from_lists(d, st)
    pick = [s for s in specs if model is None or model in s[0].cpu]
    reproduced, replica_ok = reproduce(d, pick)
    if model is None:
        cmp("stored_seed/reproduced/numbers_checked", st["stored_seed"]["reproduced"]["numbers_checked"], reproduced["numbers_checked"])
        cmp("stored_seed/replica_matches", st["stored_seed"]["replica_matches"], replica_ok)
    if reproduced["max_rel_diff"] > 1e-9 or not replica_ok:
        bad.append(f"stored seed: the code does not reproduce pooled.json (max rel diff {reproduced['max_rel_diff']:.2e})")
    rows = {r["id"]: r for r in st["cells"]}
    for m, kind, cid in pick:
        row = rows[spec_id(m, kind, cid)]
        n = ALT_COUNT if all_ else (seeds or (ALT_COUNT if kind == "forward" else VERIFY_ALT_P))
        pairs = alt_draws(m, kind, cid, n)
        cmp(row["id"] + "/alt/hi_list", row["alt"]["hi_list"][:n], [p[1] for p in pairs])
        if kind == "placement":
            cmp(row["id"] + "/alt/lo_list", row["alt"]["lo_list"][:n], [p[0] for p in pairs])
        if all_ or (kind == "forward" and seeds is None):      # --seeds N asks for a quick sample: no converged reading then
            cmp(row["id"] + "/converged", row["converged"], converged(m, kind, cid))
    for m in d.models:
        if model is not None and model not in m.cpu:
            continue
        sel = [(k, cid) for mm, k, cid in specs if mm is m]
        if not sel:
            continue
        w = st["whole"]["models"][m.cpu]
        n = WHOLE_COUNT if all_ else (whole if whole is not None else (VERIFY_WHOLE_SMALL if len(m.docs) <= SMALL_JOBS else VERIFY_WHOLE_LARGE))
        got = [whole_analysis(d, m, p, sel) for p in seed_prefixes(n)]
        cmp(m.cpu + "/whole/per_seed", w["per_seed"][:n], json.loads(json.dumps(got)))
        if all_:
            cmp(m.cpu + "/whole/stored_seed_form", w["stored_seed_form"], whole_analysis(d, m, STORED_PREFIX, sel)["form"])
    return bad


def main(argv):
    def opt(name, cast=str):
        return cast(argv[argv.index(name) + 1]) if name in argv else None

    file = opt("--file")
    t0 = time.time()
    if "--tables" in argv:                      # print the README's tables from the stored file (nothing is recomputed)
        with open(file or OUT, encoding="utf-8") as f:
            for name, lines in tables(json.load(f)).items():
                print(f"\n[{name}]\n" + "\n".join(lines))
        return 0
    if "--full" in argv:
        out = build()
        with open(file or OUT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote {file or OUT} in {(time.time() - t0) / 60:.1f} min")
        return 0
    bad = verify(file, all_="--all" in argv, model=opt("--model"), seeds=opt("--seeds", int), whole=opt("--whole", int))
    name = os.path.relpath(file or OUT, REPO) if os.path.exists(file or OUT) else (file or OUT)
    if bad:
        print(f"FAIL {name}: {bad[0]}" + (f" (and {len(bad) - 1} more)" if len(bad) > 1 else ""))
        return 1
    what = "the full recomputation" if "--all" in argv else "the recomputation of its sample"
    print(f"{name} equals {what} ({(time.time() - t0) / 60:.1f} min)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
