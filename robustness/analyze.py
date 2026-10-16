"""Sensitivity of the pooled 95 % intervals to autocorrelated repetitions (see robustness/PLAN.md).

Exploratory. Reads only stored raw samples; the harness verdicts stay the reading of record.
Four interval methods per pooled statistic: (a) harness two-level bootstrap, (b) block bootstrap inside jobs
(blocks of 1, 2, 5 ABBA quartets; 1 is the primary), (c) jobs-only bootstrap and t interval, (d) lag-1
autocorrelation / effective-sample-size correction. The verdict logic is harness/pool.py analyse_cpu with the interval
functions swapped in memory.

    python robustness/analyze.py [--report]  writes robustness/results.json, prints the tables
                                            (--report also rewrites the tables block of robustness/report.md)
"""
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402
import stats  # noqa: E402

DATASETS = {"s4": "results/s4-pooled/pooled.json", "s5": "results/s5-holdout/pooled.json",
            "s6": "results/s6-pooled/pooled.json", "s7": "results/s7-pooled/pooled.json"}
METHODS = ["a", "b", "b2", "b5", "c", "ct", "d", "d0"]
MIN_JOBS = 3
B = pool.RESAMPLES
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
        20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048,
        29: 2.045, 30: 2.042}
ORIG_PAIR = pool.pair_stat
ORIG_PLACEMENT = pool.placement_stat


# ---------------------------------------------------------------- helpers

def _per_job(sides_by_job, combine):
    return [combine(*[statistics.median(s) for s in sides]) for sides in sides_by_job]


def _result(ratio, lo, hi, J, per_job):
    logs = [math.log(r) for r in per_job]
    return {"ratio": ratio, "ci95": [lo, hi], "half_width_pct": stats.half_width_pct((lo, hi)), "jobs": J,
            "per_job": per_job, "between_job_sd_pct": 100.0 * statistics.stdev(logs) if J > 1 else None}


def lag1(x):
    """Lag-1 autocorrelation (the usual biased estimator); 0 for a constant series."""
    x = np.asarray(x, dtype=np.float64)
    d = x - x.mean()
    den = float(np.dot(d, d))
    if den == 0.0 or len(x) < 3:
        return 0.0
    return float(np.dot(d[:-1], d[1:]) / den)


def n_eff(n, rho):
    rho = min(max(rho, 0.0), 0.95)
    return n * (1.0 - rho) / (1.0 + rho)


def log_ratio_series(a, b):
    return np.log(np.asarray(b, dtype=np.float64)) - np.log(np.asarray(a, dtype=np.float64))


# ---------------------------------------------------------------- (b) block bootstrap

def block_stat(cpu, stat_id, sides_by_job, combine, bs=1, resamples=B):
    """Jobs drawn with replacement; inside each job whole blocks of `bs` ABBA quartets (2*bs consecutive repetitions,
    both sides together) drawn with replacement. Sides come in pairs (0,1), (2,3); each pair has its own block draws."""
    J = len(sides_by_job)
    per_job = _per_job(sides_by_job, combine)
    ratio = math.exp(math.fsum(math.log(r) for r in per_job) / J)
    L = len(sides_by_job[0][0])
    blk = 2 * bs
    nb = L // blk
    if nb < 2:
        raise ValueError("fewer than 2 blocks")
    job_idx = pool.draws(pool.seed_for(cpu, stat_id, "bjobs"), (resamples, J), J)
    nsides = len(sides_by_job[0])
    meds = []
    for k in range(nsides):
        p = k // 2
        t = pool.draws(pool.seed_for(cpu, stat_id, f"bblk{p}"), (resamples, J, nb), nb)
        reps = (t[:, :, :, None] * blk + np.arange(blk)[None, None, None, :]).reshape(resamples, J, nb * blk)
        arr = np.asarray([s[k] for s in sides_by_job], dtype=np.float64)
        picked = arr[job_idx[:, :, None], reps]
        meds.append(np.median(picked, axis=2))
    rstar = np.exp(np.mean(np.log(combine(*meds)), axis=1))
    lo, hi = stats.percentile_interval(sorted(float(x) for x in rstar))
    return _result(ratio, lo, hi, J, per_job)


# ---------------------------------------------------------------- (c) jobs only

def jobs_only_stat(cpu, stat_id, sides_by_job, combine, resamples=B, t_interval=False):
    J = len(sides_by_job)
    per_job = _per_job(sides_by_job, combine)
    logs = np.log(np.asarray(per_job))
    ratio = math.exp(math.fsum(logs.tolist()) / J)
    if t_interval:
        sd = float(np.std(logs, ddof=1))
        h = T975.get(J - 1, 1.96) * sd / math.sqrt(J)
        m = float(np.mean(logs))
        return _result(ratio, math.exp(m - h), math.exp(m + h), J, per_job)
    idx = pool.draws(pool.seed_for(cpu, stat_id, "cjobs"), (resamples, J), J)
    rstar = np.exp(logs[idx].mean(axis=1))
    lo, hi = stats.percentile_interval(sorted(float(x) for x in rstar))
    return _result(ratio, lo, hi, J, per_job)


# ---------------------------------------------------------------- (d) effective sample size

def _within(sides_by_job):
    """(sum of var(e)/n, sum of var(e)/n_eff) over jobs and pairs, divided by J^2: the within-job variance of the pooled
    log ratio under independence and under the lag-1 n_eff correction (means of per-repetition log ratios)."""
    J = len(sides_by_job)
    w_iid = w_cor = 0.0
    for sides in sides_by_job:
        for p in range(0, len(sides), 2):
            e = log_ratio_series(sides[p], sides[p + 1])
            n = len(e)
            v = float(np.var(e, ddof=1))
            w_iid += v / n
            w_cor += v / n_eff(n, lag1(e))
    return w_iid / (J * J), w_cor / (J * J)


def _widen(base, var):
    h = 1.96 * math.sqrt(var)
    r = base["ratio"]
    out = dict(base)
    out["ci95"] = [r * math.exp(-h), r * math.exp(h)]
    out["half_width_pct"] = stats.half_width_pct(tuple(out["ci95"]))
    return out


def autocorr_stat(cpu, stat_id, sides_by_job, combine, resamples=B):
    """(d), final form. The harness interval's log-scale variance sd_a^2 is split into a within-job share s and the rest;
    the within share is multiplied by W_cor / W_iid, the pure autocorrelation inflation (outliers cancel in the ratio).
    s = min(1, W_iid / sd_a^2), so the result is at most sd_a^2 x W_cor / W_iid. Lower bound on trust."""
    base = pool.pooled_stat(cpu, stat_id, sides_by_job, combine, resamples)
    w_iid, w_cor = _within(sides_by_job)
    lo, hi = base["ci95"]
    var_a = ((math.log(hi) - math.log(lo)) / 2.0 / 1.96) ** 2
    if var_a == 0.0 or w_iid == 0.0:
        return base
    s = min(1.0, w_iid / var_a)
    return _widen(base, var_a * ((1.0 - s) + s * w_cor / w_iid))


def autocorr_stat_v0(cpu, stat_id, sides_by_job, combine, resamples=B):
    """(d0), the first form written in PLAN.md: sd_a^2 - W_iid + W_cor. Kept and reported because it is what the plan
    said; it inflates widths by more than autocorrelation, because W_iid is a variance of MEANS of log ratios and the
    harness bootstraps MEDIANS (heavy-tailed series make W_iid larger than the median's variance)."""
    base = pool.pooled_stat(cpu, stat_id, sides_by_job, combine, resamples)
    w_iid, w_cor = _within(sides_by_job)
    lo, hi = base["ci95"]
    var_a = ((math.log(hi) - math.log(lo)) / 2.0 / 1.96) ** 2
    return _widen(base, max(var_a - w_iid, 0.0) + w_cor)


# ---------------------------------------------------------------- swapping the harness's interval functions

def stat_fn(method):
    if method == "a":
        return pool.pooled_stat
    if method in ("b", "b2", "b5"):
        bs = {"b": 1, "b2": 2, "b5": 5}[method]
        return lambda cpu, sid, sbj, comb, resamples=B: block_stat(cpu, sid, sbj, comb, bs, resamples)
    if method == "c":
        return lambda cpu, sid, sbj, comb, resamples=B: jobs_only_stat(cpu, sid, sbj, comb, resamples, False)
    if method == "ct":
        return lambda cpu, sid, sbj, comb, resamples=B: jobs_only_stat(cpu, sid, sbj, comb, resamples, True)
    if method == "d":
        return autocorr_stat
    if method == "d0":
        return autocorr_stat_v0
    raise ValueError(method)


def install(method):
    fn = stat_fn(method)
    pool.pair_stat = lambda cpu, sid, pairs, resamples=B: fn(cpu, sid, [[a, b] for a, b in pairs],
                                                           lambda ma, mb: mb / ma, resamples)
    pool.placement_stat = lambda cpu, sid, quads, resamples=B: fn(
        cpu, sid, [list(q) for q in quads], lambda n, f, na, fa: (f / n) / (fa / na), resamples)


def restore():
    pool.pair_stat = ORIG_PAIR
    pool.placement_stat = ORIG_PLACEMENT


# ---------------------------------------------------------------- loading

def load_dataset(pooled_rel):
    path = os.path.join(REPO, pooled_rel)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        stored = json.load(f)
    base = os.path.dirname(path)
    docs = []
    for i in stored["inputs"]:
        p = os.path.join(base, i["path"])
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            docs.append((i["path"], json.load(f)))
    return stored, docs


def by_cpu(docs):
    out = {}
    for p, d in docs:
        out.setdefault(d["run"]["runner"]["cpu_model"] or "unknown", []).append((p, d))
    return out


# ---------------------------------------------------------------- one block, compacted

def compact_block(block, crit):
    limit = 1.0 + block["verdict"]["forward_limit_pct"] / 100.0
    cells = {}
    for c in block["cells"]:
        if c["size_class"] not in pool.IN_CACHE:
            continue
        r = {"class": c["class"], "ac": [c["as_compiled"]["ratio"], *c["as_compiled"]["ci95"]],
             "al": [c["aligned"]["ratio"], *c["aligned"]["ci95"]]}
        ps = c.get("placement")
        if ps:
            r["ps"] = bool(ps["sensitive"])
        if c["class"] == "kept":
            r["fwd_pass"] = bool(c["aligned"]["ratio"] <= crit["forward_point_max_ratio"]
                                 and c["aligned"]["ci95"][1] <= limit)
        if c["class"] == "lost":
            r["lost_ok"] = bool(c["as_compiled"]["ci95"][0] >= crit["lost_ci_lo_min_ratio"]
                                and c["aligned"]["ci95"][0] >= crit["lost_ci_lo_min_ratio"])
        cells[c["cell_id"]] = r
    return {"form": block["verdict"]["form"], "aa": [block["aa"]["ratio"], *block["aa"]["ci95"]],
            "aa_hw_pct": block["aa"]["half_width_pct"], "limit_pct": block["verdict"]["forward_limit_pct"],
            "cells": cells}


def autocorr_summary(docs):
    """Lag-1 autocorrelation of the per-repetition log ratio and of the A series, over every in-cache as-compiled pair
    of every job."""
    rho_e, rho_a, neff_frac = [], [], []
    for _, d in docs:
        for c in d["cells"]:
            if c["size_class"] not in pool.IN_CACHE:
                continue
            e = log_ratio_series(c["none_ns"], c["fast_ns"])
            re_ = lag1(e)
            rho_e.append(re_)
            rho_a.append(lag1(np.log(c["none_ns"])))
            neff_frac.append(n_eff(len(e), re_) / len(e))
    return {"series": len(rho_e), "rho_e_median": statistics.median(rho_e), "rho_e_mean": statistics.fmean(rho_e),
            "rho_a_median": statistics.median(rho_a),
            "share_rho_e_above_0.2": sum(r > 0.2 for r in rho_e) / len(rho_e),
            "neff_over_n_median": statistics.median(neff_frac), "neff_over_n_min": min(neff_frac)}


# ---------------------------------------------------------------- self-test of method (a)

def self_test(stored, docs, criteria):
    """Recompute every cpu model with method (a) and compare with the stored pooled.json: ratios and intervals of every
    cell and column, the A/A, the verdict form."""
    restore()
    checked = exact = 0
    worst = 0.0
    form_ok = True
    for cpu, entries in by_cpu(docs).items():
        blk = pool.analyse_cpu(cpu, [d for _, d in entries], criteria)
        st = next(b for b in stored["cpus"] if b["cpu_model"] == cpu)
        form_ok &= blk["verdict"]["form"] == st["verdict"]["form"]
        pairs = [(blk["aa"], st["aa"])]
        sc = {c["cell_id"]: c for c in st["cells"]}
        for c in blk["cells"]:
            for col in ("as_compiled", "aligned"):
                pairs.append((c[col], sc[c["cell_id"]][col]))
        for mine, theirs in pairs:
            for x, y in [(mine["ratio"], theirs["ratio"]), (mine["ci95"][0], theirs["ci95"][0]),
                         (mine["ci95"][1], theirs["ci95"][1])]:
                checked += 1
                # a number counts as reproduced when it agrees to 1e-12 relative: the last bit of a log/exp/quantile
                # differs between platforms (Windows vs Linux libm), and the count must not depend on that
                exact += abs(x - y) <= 1e-12 * abs(y)
                worst = max(worst, abs(x - y) / abs(y))
    return {"numbers_checked": checked, "exact": exact, "max_rel_diff": worst, "forms_equal": bool(form_ok)}


# ---------------------------------------------------------------- everything

def run_all(datasets=None):
    criteria, _ = pool.criteria_and_sha()
    crit = criteria["verdict"]
    out = {"methods": METHODS, "datasets": {}}
    for name, rel in (datasets or DATASETS).items():
        loaded = load_dataset(rel)
        if loaded is None:
            continue
        stored, docs = loaded
        ds = {"self_test": self_test(stored, docs, criteria), "cpus": {}}
        try:
            for cpu, entries in sorted(by_cpu(docs).items()):
                dd = [d for _, d in entries]
                if len(dd) < MIN_JOBS:
                    continue
                res = {"jobs": len(dd), "autocorr": autocorr_summary(entries), "methods": {}}
                for m in METHODS:
                    install(m)
                    blk = pool.analyse_cpu(cpu, dd, criteria, full=False)
                    res["methods"][m] = compact_block(blk, crit)
                restore()
                ds["cpus"][cpu] = res
        finally:
            restore()
        out["datasets"][name] = ds
    return out


# ---------------------------------------------------------------- comparisons

def compare(res, m):
    """Classification changes and width ratios of method m versus (a) for one cpu's result."""
    a, x = res["methods"]["a"], res["methods"][m]
    flips = {"fwd_pass": [], "lost_ok": [], "placement_sensitive": []}
    widths = []
    for cid, ca in a["cells"].items():
        cx = x["cells"][cid]
        for key, fk in (("fwd_pass", "fwd_pass"), ("lost_ok", "lost_ok"), ("ps", "placement_sensitive")):
            if key in ca and ca[key] != cx[key]:
                flips[fk].append(cid)
        for col in ("ac", "al"):
            wa, wx = ca[col][2] - ca[col][1], cx[col][2] - cx[col][1]
            widths.append(wx / wa)
    counts = {"fwd_pass": sum("fwd_pass" in c for c in a["cells"].values()),
              "lost_ok": sum("lost_ok" in c for c in a["cells"].values()),
              "placement_sensitive": sum("ps" in c for c in a["cells"].values())}
    return {"flips": flips, "counts": counts, "width_median": statistics.median(widths), "width_max": max(widths),
            "form": x["form"], "form_a": a["form"], "aa_hw_pct": x["aa_hw_pct"]}


def margins(res, m):
    """Smallest lost-cell ci95_lo (both columns) and largest forward aligned ci95_hi under method m."""
    cells = res["methods"][m]["cells"]
    lost = [min(c["ac"][1], c["al"][1]) for c in cells.values() if c["class"] == "lost"]
    fwd = [c["al"][2] for c in cells.values() if c["class"] == "kept" and not c.get("ps")]
    return (min(lost) if lost else None), (max(fwd) if fwd else None)


NAMES = {"a": "(a) harness", "b": "(b) block, 1 ABBA", "b2": "(b2) block, 2 ABBA", "b5": "(b5) block, 5 ABBA",
         "c": "(c) jobs only, bootstrap", "ct": "(c-t) jobs only, t", "d": "(d) lag-1 n_eff", "d0": "(d0) first form of (d)"}


def short(cpu):
    if "(R)" in cpu:                       # "INTEL(R) XEON(R) PLATINUM 8573C" -> "Intel Xeon Platinum 8573C"
        cpu = cpu.replace("(R)", "").title()
    return cpu.replace(" Processor", "").replace(" 64-Core", "").replace(" 96-Core", "").replace(" 80-Core", "")


def tables_md(out):
    L = []
    for name, ds in out["datasets"].items():
        st = ds["self_test"]
        L.append(f"### Dataset {name}")
        L.append("")
        L.append(f"Self-test of (a) against the stored pooled.json: {st['exact']} of {st['numbers_checked']} stored "
                 f"numbers reproduced to within 1e-12 relative, largest relative difference "
                 f"{'below 1e-12' if st['max_rel_diff'] <= 1e-12 else format(st['max_rel_diff'], '.1e')}, verdict forms "
                 f"{'equal' if st['forms_equal'] else 'DIFFER'}.")
        L.append("")
        L.append("Lag-1 autocorrelation of the per-repetition log ratio (every in-cache as-compiled series, 40 points; "
                 "an independent series would average about -0.025):")
        L.append("")
        L.append("| CPU model | jobs | series | median rho (ratio) | mean rho (ratio) | median rho (NONE time) "
                 "| share rho>0.2 | median n_eff/n |")
        L.append("|---|---|---|---|---|---|---|---|")
        for cpu, r in ds["cpus"].items():
            ac = r["autocorr"]
            L.append(f"| {short(cpu)} | {r['jobs']} | {ac['series']} | {ac['rho_e_median']:.3f} | "
                     f"{ac['rho_e_mean']:.3f} | {ac['rho_a_median']:.3f} | {ac['share_rho_e_above_0.2']:.2f} | "
                     f"{ac['neff_over_n_median']:.2f} |")
        L.append("")
        L.append("Changes against (a), in-cache cells. fwd = forward cells passing the forward rule (aligned column), "
                 "lost = lost cells with ci95_lo >= 1.5 in both columns, ps = placement-sensitive flag; each shows "
                 "flips/cells. Width = interval width over the width of (a), median and max over cells and both "
                 "columns.")
        L.append("")
        L.append("| CPU model | method | verdict form | fwd flips | lost flips | ps flips | width median "
                 "| width max | A/A half-width % |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for cpu, r in ds["cpus"].items():
            for m in METHODS:
                c = compare(r, m)
                f = c["flips"]
                n = c["counts"]
                L.append(f"| {short(cpu)} | {NAMES[m]} | {c['form']} | {len(f['fwd_pass'])}/{n['fwd_pass']} | "
                         f"{len(f['lost_ok'])}/{n['lost_ok']} | "
                         f"{len(f['placement_sensitive'])}/{n['placement_sensitive']} | "
                         f"{c['width_median']:.2f} | {c['width_max']:.2f} | {c['aa_hw_pct']:.2f} |")
        L.append("")
        L.append("Margins under each method: smallest lost-cell ci95_lo (rule: at least 1.5) and largest counted "
                 "forward aligned ci95_hi (rule: at most the forward limit, 1 + max(2 %, 2 x A/A half-width)).")
        L.append("")
        L.append("| CPU model | method | min lost ci95_lo | max forward ci95_hi | forward limit (x) |")
        L.append("|---|---|---|---|---|")
        for cpu, r in ds["cpus"].items():
            for m in METHODS:
                lo, hi = margins(r, m)
                lim = 1.0 + r["methods"][m]["limit_pct"] / 100.0
                L.append(f"| {short(cpu)} | {NAMES[m]} | {lo:.3f} | {hi:.3f} | {lim:.4f} |")
        L.append("")
    return "\n".join(L)


def main():
    out = run_all()
    if not out["datasets"]:
        print("SKIP: no pooled inputs found")
        return 0
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    tables = tables_md(out)
    print(tables)
    if "--report" in sys.argv:
        rp = os.path.join(HERE, "report.md")
        with open(rp, encoding="utf-8") as f:
            text = f.read()
        head, rest = text.split("<!-- tables:begin -->", 1)
        tail = rest.split("<!-- tables:end -->", 1)[1]
        nl = chr(10)
        with open(rp, "w", encoding="utf-8", newline=nl) as f:
            f.write(head + "<!-- tables:begin -->" + nl + tables + nl + "<!-- tables:end -->" + tail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
