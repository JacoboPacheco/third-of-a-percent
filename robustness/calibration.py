#!/usr/bin/env python3
"""Calibration baseline for the sentence "intervals still understate run-to-run spread" (robustness/README-calibration.md).

The README and the details page count how often one run's pooled point falls outside another run's pooled 95% interval
(EPYC 7763: 168 of 640 comparisons, EPYC 9V74: 62 of 384) and call that understatement. A count means nothing without the
count that perfectly calibrated intervals would give, so this script computes that, and then asks three more questions of the
same stored data. It reads files only (numpy, no compiler, no network); it changes no stored number, rule or seed.

PART A  run-to-run counts. The stored counts are reproduced first, from the stored per_run records, by an independent loop and
        by harness/pool.py reproduction(); only then is anything else computed. Calibrated model (stated here, not
        inferred): every run's estimate of one cell is normal around the same true value, with the run's stated interval
        half-width equal to 1.96 standard deviations, s = (ln hi - ln lo) / (2 x 1.96), errors independent between runs.
        Two different questions are then answered, and they are labelled everywhere:
          "outside"  the claim's own count: run A's point lies outside run B's stored interval [lo, hi]. For one ordered pair
                     the difference x = ln pt_A - ln pt_B has variance s_A^2 + s_B^2 and the point is outside when
                     x < -(ln pt_B - ln lo_B) or x > (ln hi_B - ln pt_B). expected_outside uses B's stored offsets (the
                     bootstrap interval is not symmetric); expected_outside_sym replaces both offsets by 1.96 s_B.
          "pair z"   z = x / sqrt(s_A^2 + s_B^2); |z| > 1.96 is expected in 5% of pairs and the root mean square of z is 1.
        Observed against expected is made a real comparison by a fixed-seed simulation of the count (2000 draws): once with
        independent errors in every (run, cell, column), and once with one shared standard-normal draw per run (all cells of
        a run move together, the most dependent case), which brackets the unknown dependence between the 32 cells of a run.
PART B  the replication sets (replication/results.json): the new pooled point inside the earlier pool's interval, the same
        calibrated expectation and simulation per model, using replication/compare.py's own definition of "inside".
PART C  the z distribution (share |z| > 1.96, rms z) is part of A and B, per model, per cell and per column.
PART D  one-way variance decomposition of the per-job ratios of the 95-job pool, per model, in-cache cell and column:
        between-job sd against the mean within-job SE (from each job's own ci95), a one-way analysis of variance by run
        (variance components, F, permutation p), and Cochran's Q.
PART E  a job-exchangeability null (added beyond the normal model): the jobs of the assessed runs of one model are shuffled over the runs
        (same run sizes), every run's pooled point and interval are recomputed with harness/pool.py pair_stat, and the
        outside count is taken again. This keeps the dependence between cells that the simulation has to bracket, and the
        small-J behaviour of the bootstrap interval; if the observed count sits inside the shuffled counts, the excess over the
        calibrated-normal count is not a run effect. The identity shuffle reproduces the stored per_run records first.
PART F  verdict word against the number of jobs: 30 job subsets (fixed seed) at J = 3, 5, 10 per CPU model through the
        unchanged harness/pool.py analyse_cpu (all subsets when there are 30 or fewer), the word each subset gives.

The model, the sizes (2000 simulation draws, the number of shuffles, 30 subsets) and the use of the Xeon models were chosen
while this script was written, with the stored counts already known; none of it was set in advance of the counts.

Usage
  python robustness/calibration.py             print the tables from the stored robustness/calibration.json
  python robustness/calibration.py --full      recompute everything and write robustness/calibration.json (about 20 minutes)
  python robustness/calibration.py --verify    recompute parts A, B, C, D, the identity shuffle plus one shuffle, and the
                                               subsets of one model at one J; compare with the stored file (about 2 minutes)
  python robustness/calibration.py --counts    parts A and B only, printed (seconds), nothing written
Single process on purpose. The output is deterministic: floats equal to 1e-9 relative across platforms, integers exact.
"""
import hashlib
import importlib.util
import itertools
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool as hp  # noqa: E402  (read-only use: pair_stat, analyse_cpu, reproduction, splitmix64)

OUT = os.path.join(HERE, "calibration.json")
SCHEMA = "calibration-1"
SEED_TAG = "calibration-1"          # every random stream of this script is keyed by it; the study's own prefix is not reused
Z = 1.96                            # the stated 95% half-width is Z standard deviations
SQRT2 = math.sqrt(2.0)
COLUMNS = ("as_compiled", "aligned")
IN_CACHE = ("L1", "L2")
SIM_REPS = 2000
PERMS = 60                          # shuffles of jobs over runs per model (part E)
PERM_MODELS = ("AMD EPYC 7763 64-Core Processor", "AMD EPYC 9V74 80-Core Processor")
ANOVA_PERMS = 2000                  # label shuffles for the permutation p of the run effect (part D)
SUBSETS = 30                        # random subsets per (model, J) (part F)
SUBSET_JS = (3, 5, 10)
PRIMARY = "s7"                      # the pool whose counts the README and details page quote
RUN_POOLS = [                       # (key, pooled file, role)
    ("s4", "results/s4-pooled/pooled.json", "the original 30 jobs"),
    ("s6", "results/s6-pooled/pooled.json", "the 75-job pool"),
    ("s7", "results/s7-pooled/pooled.json", "the 95-job pool (the README's and the details page's counts)"),
    ("s8-arm", "results/s8-arm-pooled/pooled.json", "Arm set A"),
    ("s9-arm-b", "results/s9-arm-b-pooled/pooled.json", "Arm set B"),
    ("s9-arm-ab", "results/s9-arm-ab-pooled/pooled.json", "Arm sets A and B pooled (secondary)"),
    ("s9-x86-c", "results/s9-x86-c-pooled/pooled.json", "x86-64 set C"),
    ("s9-x86-ac", "results/s9-x86-ac-pooled/pooled.json", "the 95-job pool and set C pooled (secondary)"),
]
REPLICATION_RESULTS = "replication/results.json"
CRITERIA = "harness/criteria-v3.json"
POOL_PY = "harness/pool.py"
COMPARE_PY = "replication/compare.py"


# ---------------------------------------------------------------- small helpers

def lf_sha(path):
    """sha256 with CRLF read as LF, so a Windows checkout and a Linux clone agree."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def rpath(rel):
    return os.path.join(REPO, *rel.split("/"))


def load_json(rel):
    with open(rpath(rel), encoding="utf-8") as f:
        return json.load(f)


def load_compare():
    spec = importlib.util.spec_from_file_location("replication_compare", rpath(COMPARE_PY))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cal_seed(*parts):
    h = hashlib.sha256("|".join((SEED_TAG,) + tuple(str(p) for p in parts)).encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def uniforms(seed, n):
    """n uniforms in (0, 1) from the study's splitmix64 (53 bits plus a half step, never 0 or 1)."""
    x = hp.splitmix64(seed, n)
    return ((x >> np.uint64(11)).astype(np.float64) + 0.5) / 9007199254740992.0


def normals(seed, shape):
    """Standard normals by Box-Muller from splitmix64 uniforms, in C order of `shape`."""
    n = int(np.prod(shape))
    u = uniforms(seed, 2 * n)
    z = np.sqrt(-2.0 * np.log(u[:n])) * np.cos(2.0 * math.pi * u[n:])
    return z.reshape(shape)


def erfc_array(a):
    return np.array([math.erfc(float(v)) for v in np.asarray(a).ravel()]).reshape(np.shape(a))


def expected_outside(sa, sb, dlo, dhi):
    """P(run A's point is outside run B's interval) under the calibrated model, for scalars: x = ln pt_A - ln pt_B ~ N(0, sa^2 + sb^2);
    outside when x < -dlo or x > dhi (dlo, dhi: B's stored interval offsets below and above its point, in log units)."""
    sigma = math.hypot(sa, sb)
    return 0.5 * math.erfc(dlo / (sigma * SQRT2)) + 0.5 * math.erfc(dhi / (sigma * SQRT2))


def expected_outside_sym(sa, sb):
    """The same with both offsets replaced by Z sb (a symmetric interval)."""
    return math.erfc(Z * sb / (math.hypot(sa, sb) * SQRT2))


def count_summary(counts, observed, reps):
    c = np.sort(np.asarray(counts, dtype=np.int64))
    k = int(0.025 * reps)
    return {"reps": int(reps), "mean": float(c.mean()), "sd": float(c.std(ddof=1)), "p025": int(c[k]), "p975": int(c[reps - 1 - k]),
            "min": int(c[0]), "max": int(c[-1]), "observed": int(observed),
            "p_ge_observed": float(np.mean(c >= observed)), "p_le_observed": float(np.mean(c <= observed))}


def z_summary(z):
    z = np.asarray(z, dtype=np.float64)
    n = int(z.size)
    over = int(np.sum(np.abs(z) > Z))
    return {"n": n, "count_abs_gt_1_96": over, "share_abs_gt_1_96": over / n if n else None,
            "rms": float(math.sqrt(float(np.mean(z * z)))) if n else None, "max_abs": float(np.max(np.abs(z))) if n else None}


def same(x, y, path=""):
    """Equal up to relative 1e-9 on floats, exact on everything else; returns the first difference or None."""
    if isinstance(x, dict) and isinstance(y, dict):
        if x.keys() != y.keys():
            return f"{path}: keys differ ({sorted(set(x) ^ set(y))[:4]})"
        for k in x:
            d = same(x[k], y[k], f"{path}/{k}")
            if d:
                return d
        return None
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return f"{path}: length {len(x)} != {len(y)}"
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


def log(msg):
    sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------- parts A and C: run-to-run counts

class Elements:
    """Every (ordered run pair, in-cache cell, column) that harness/pool.py reproduction() visits, in its order, with the log
    quantities of the calibrated model. runs: the assessable per_run records (form not None) of one CPU model."""

    def __init__(self, runs):
        keys = [(cid, col) for cid in runs[0]["cells"] for col in COLUMNS]
        for r in runs:
            assert [(cid, col) for cid in r["cells"] for col in COLUMNS] == keys, "the runs of one model have the same cells"
        assert all(cid.rsplit(".", 1)[1] in IN_CACHE for cid, _ in keys)
        nr, nk = len(runs), len(keys)
        pt = np.array([[r["cells"][cid][col][0] for cid, col in keys] for r in runs])
        lo = np.array([[r["cells"][cid][col][1] for cid, col in keys] for r in runs])
        hi = np.array([[r["cells"][cid][col][2] for cid, col in keys] for r in runs])
        self.keys, self.nr, self.nk = keys, nr, nk
        lpt, llo, lhi = np.log(pt), np.log(lo), np.log(hi)
        self.s = (lhi - llo) / (2.0 * Z)                         # (nr, nk) standard deviation implied by the stated interval
        self.dlo, self.dhi = lpt - llo, lhi - lpt                # stored offsets of each interval around its own point
        ia, ib, kk = [], [], []
        for a in range(nr):
            for b in range(nr):
                if a == b:
                    continue
                for k in range(nk):
                    ia.append(a)
                    ib.append(b)
                    kk.append(k)
        self.ia, self.ib, self.kk = np.array(ia), np.array(ib), np.array(kk)
        self.n = len(kk)
        self.outside = ~((lo[self.ib, self.kk] <= pt[self.ia, self.kk]) & (pt[self.ia, self.kk] <= hi[self.ib, self.kk]))
        x = lpt[self.ia, self.kk] - lpt[self.ib, self.kk]
        sa, sb = self.s[self.ia, self.kk], self.s[self.ib, self.kk]
        self.sigma = np.hypot(sa, sb)
        self.z = x / self.sigma
        da, db = self.dlo[self.ib, self.kk], self.dhi[self.ib, self.kk]
        self.p_stored = 0.5 * erfc_array(da / (self.sigma * SQRT2)) + 0.5 * erfc_array(db / (self.sigma * SQRT2))
        self.p_sym = erfc_array(Z * sb / (self.sigma * SQRT2))
        lo_b, hi_b = lo[self.ib, self.kk], hi[self.ib, self.kk]
        p = pt[self.ia, self.kk]
        self.gap_pct = np.where(self.outside, np.where(p < lo_b, 100.0 * (lo_b - p) / p, 100.0 * (p - hi_b) / p), 0.0)

    def simulate(self, mode, seed_parts):
        """Outside count over SIM_REPS draws of the calibrated model. mode 'independent': a normal error per (run, cell, column);
        'common': one standard-normal draw per run, scaled by each cell's s (all cells of a run move together)."""
        seed = cal_seed("sim", mode, *seed_parts)
        if mode == "independent":
            e = self.s[None, :, :] * normals(seed, (SIM_REPS, self.nr, self.nk))
        else:
            e = self.s[None, :, :] * normals(seed, (SIM_REPS, self.nr))[:, :, None]
        x = e[:, self.ia, self.kk] - e[:, self.ib, self.kk]
        out = (x < -self.dlo[self.ib, self.kk][None, :]) | (x > self.dhi[self.ib, self.kk][None, :])
        return out.sum(axis=1)

    def by_cell(self):
        rows = []
        for k, (cid, col) in enumerate(self.keys):
            m = self.kk == k
            rows.append({"cell_id": cid, "column": col, "pairs": int(m.sum()), "outside": int(self.outside[m].sum()),
                         "expected_outside": float(self.p_stored[m].sum()), "rms_z": float(math.sqrt(float(np.mean(self.z[m] ** 2))))})
        return rows


def run_to_run(pool_key, doc):
    """Part A and C for one pooled file: one record per CPU model that has at least two assessable runs."""
    out, skipped = [], []
    for b in doc["cpus"]:
        runs = [r for r in b["per_run"] if r["form"] is not None]
        if len(runs) < 2:
            skipped.append({"cpu_model": b["cpu_model"], "jobs": b["jobs"], "jobs_per_run": [r["jobs"] for r in b["per_run"]]})
            continue
        el = Elements(runs)
        own = int(el.outside.sum())
        pr = hp.reproduction(runs)
        stored = b["reproduction"]
        sims = {m: el.simulate(m, (pool_key, b["cpu_model"])) for m in ("independent", "common")}
        rec = {"cpu_model": b["cpu_model"], "jobs": b["jobs"], "runs_assessed": [{"run_id": r["run_id"], "jobs": r["jobs"]} for r in runs],
               "checked": int(el.n), "outside": own,
               "stored_checked": stored["checked"], "stored_outside": stored["outside"],
               "reproduces_stored": bool(el.n == stored["checked"] and own == stored["outside"]
                                         and pr["checked"] == el.n and pr["outside"] == own),
               "max_gap_pct": float(el.gap_pct.max()), "stored_max_gap_pct": max((m["gap_pct"] for m in stored["misses"]), default=None),
               "outside_share": own / el.n,
               "expected_outside": float(el.p_stored.sum()), "expected_outside_sym": float(el.p_sym.sum()),
               "expected_share": float(el.p_stored.mean()), "expected_share_sym": float(el.p_sym.mean()),
               "pair_z": z_summary(el.z),
               "simulation": {m: count_summary(c, own, SIM_REPS) for m, c in sims.items()},
               "by_cell": el.by_cell()}
        out.append(rec)
    return {"pool": pool_key, "models": out, "not_assessable": skipped}


# ---------------------------------------------------------------- part B: the replication sets

def replication(compare, crit_minimum):
    """The new pooled point inside the earlier pool's interval: observed (replication/compare.py inside_points) against the
    calibrated expectation, per model and per architecture."""
    stored = load_json(REPLICATION_RESULTS)
    out = {}
    for arch, files in compare.POOLS.items():
        docs = {role: load_json(rel) for role, rel in files.items() if role in ("earlier", "replication")}
        models = []
        for e in docs["earlier"]["cpus"]:
            n = compare.block_of(docs["replication"], e["cpu_model"])
            if n is None or e["jobs"] < crit_minimum or n["jobs"] < crit_minimum:
                continue
            pts = compare.inside_points(n, e)
            summ = compare.inside_summary(pts)
            sn = np.array([(math.log(compare.cell_of(n, p["cell_id"])[p["column"]]["ci95"][1])
                            - math.log(compare.cell_of(n, p["cell_id"])[p["column"]]["ci95"][0])) / (2.0 * Z) for p in pts])
            so = np.array([(math.log(p["earlier_ci95"][1]) - math.log(p["earlier_ci95"][0])) / (2.0 * Z) for p in pts])
            dlo = np.array([math.log(p["earlier"]) - math.log(p["earlier_ci95"][0]) for p in pts])
            dhi = np.array([math.log(p["earlier_ci95"][1]) - math.log(p["earlier"]) for p in pts])
            sigma = np.hypot(sn, so)
            z = np.array([math.log(p["new"] / p["earlier"]) for p in pts]) / sigma
            p_out = 0.5 * erfc_array(dlo / (sigma * SQRT2)) + 0.5 * erfc_array(dhi / (sigma * SQRT2))
            p_sym = erfc_array(Z * so / (sigma * SQRT2))
            obs = summ["outside"]
            sims = {}
            for mode in ("independent", "common"):
                if mode == "independent":
                    zn = normals(cal_seed("rsim", mode, arch, e["cpu_model"], "new"), (SIM_REPS, len(pts)))
                    zo = normals(cal_seed("rsim", mode, arch, e["cpu_model"], "earlier"), (SIM_REPS, len(pts)))
                    x = sn[None, :] * zn - so[None, :] * zo
                else:
                    zz = normals(cal_seed("rsim", mode, arch, e["cpu_model"]), (SIM_REPS, 2))
                    x = sn[None, :] * zz[:, :1] - so[None, :] * zz[:, 1:]
                sims[mode] = ((x < -dlo[None, :]) | (x > dhi[None, :])).sum(axis=1)
            st = next(m for m in stored[arch]["models"] if m["cpu_model"] == e["cpu_model"])["inside"]
            models.append({"cpu_model": e["cpu_model"], "earlier_jobs": e["jobs"], "replication_jobs": n["jobs"],
                           "checked": summ["checked"], "inside": summ["inside"], "outside": obs,
                           "stored_checked": st["checked"], "stored_outside": st["outside"],
                           "reproduces_stored": bool(summ["checked"] == st["checked"] and obs == st["outside"]),
                           "expected_outside": float(p_out.sum()), "expected_outside_sym": float(p_sym.sum()),
                           "expected_inside": float(summ["checked"] - p_out.sum()),
                           "pair_z": z_summary(z),
                           "simulation": {m: count_summary(c, obs, SIM_REPS) for m, c in sims.items()},
                           "_sims": sims})
        tot_obs = sum(m["outside"] for m in models)
        tot = {"checked": sum(m["checked"] for m in models), "outside": tot_obs,
               "inside": sum(m["inside"] for m in models),
               "expected_outside": sum(m["expected_outside"] for m in models),
               "expected_outside_sym": sum(m["expected_outside_sym"] for m in models),
               "expected_inside": sum(m["expected_inside"] for m in models),
               "stored_points_checked": stored[arch]["totals"]["points_checked"],
               "stored_points_outside": stored[arch]["totals"]["points_outside"],
               "simulation": {mode: count_summary(sum(m["_sims"][mode] for m in models), tot_obs, SIM_REPS)
                              for mode in ("independent", "common")}}
        for m in models:
            del m["_sims"]
        out[arch] = {"models": models, "totals": tot}
    return out


# ---------------------------------------------------------------- the job files of the primary pool

class Jobs:
    """The 95 job documents of the primary pool in the pool's own order (sorted paths), grouped by CPU model."""

    def __init__(self, key=PRIMARY):
        rel = dict((k, p) for k, p, _ in RUN_POOLS)[key]
        self.key, self.rel = key, rel
        self.pooled = load_json(rel)
        base = os.path.dirname(rpath(rel))
        paths = [i["path"] for i in self.pooled["inputs"]]
        assert paths == sorted(paths), "pool.py sorts its inputs; the bootstrap's job indices refer to that order"
        self.docs, self.shas = [], []
        for p in paths:
            fp = os.path.normpath(os.path.join(base, *p.split("/")))
            self.shas.append((p, lf_sha(fp)))
            with open(fp, encoding="utf-8") as f:
                self.docs.append(json.load(f))
        self.models = {}
        for i, inp in enumerate(self.pooled["inputs"]):
            self.models.setdefault(inp["cpu_model"], []).append(i)
        self.run_ids = [i["run_id"] for i in self.pooled["inputs"]]
        self.by_id = [{c["cell_id"]: c for c in d["cells"]} for d in self.docs]

    def files_sha(self):
        return hashlib.sha256("\n".join(f"{p} {s}" for p, s in self.shas).encode("utf-8")).hexdigest()

    def block(self, model):
        return next(b for b in self.pooled["cpus"] if b["cpu_model"] == model)


def ratio_of(cell, col):
    return cell["ratio"] if col == "as_compiled" else cell["aligned"]["ratio"]


def ci_of(cell, col):
    return cell["ci95"] if col == "as_compiled" else cell["aligned"]["ci95"]


# ---------------------------------------------------------------- part D: variance decomposition

def anova_by_run(y, groups, seed_parts):
    """One-way analysis of variance of y (jobs) by run: variance components, F and a permutation p.
    groups: list of lists of indices into y, one per run (runs with enough jobs). None when fewer than two groups."""
    k = len(groups)
    if k < 2:
        return None
    order = [i for g in groups for i in g]
    ys = np.asarray([y[i] for i in order], dtype=np.float64)
    sizes = [len(g) for g in groups]
    N = len(ys)
    bounds = np.cumsum([0] + sizes)

    def parts(v):
        gm = v.mean()
        means = [v[bounds[j]:bounds[j + 1]].mean() for j in range(k)]
        ssb = sum(sizes[j] * (means[j] - gm) ** 2 for j in range(k))
        ssw = sum(float(np.sum((v[bounds[j]:bounds[j + 1]] - means[j]) ** 2)) for j in range(k))
        return ssb, ssw

    ssb, ssw = parts(ys)
    dfb, dfw = k - 1, N - k
    msb, msw = ssb / dfb, ssw / dfw
    n0 = (N - sum(s * s for s in sizes) / N) / (k - 1)
    f_obs = msb / msw if msw > 0 else math.inf
    keys = uniforms(cal_seed("anova", *seed_parts), ANOVA_PERMS * N).reshape(ANOVA_PERMS, N)
    perm = np.argsort(keys, axis=1, kind="stable")
    ys_perm = ys[perm]                                          # (P, N): the same values under shuffled run labels
    means = np.stack([ys_perm[:, bounds[j]:bounds[j + 1]].mean(axis=1) for j in range(k)], axis=1)
    gm = ys_perm.mean(axis=1)
    ssb_p = sum(sizes[j] * (means[:, j] - gm) ** 2 for j in range(k))
    ssw_p = sum(np.sum((ys_perm[:, bounds[j]:bounds[j + 1]] - means[:, [j]]) ** 2, axis=1) for j in range(k))
    f_perm = (ssb_p / dfb) / (ssw_p / dfw)
    return {"runs": k, "jobs": N, "ms_between": msb, "ms_within": msw, "f": f_obs,
            "p_perm": float((1 + int(np.sum(f_perm >= f_obs - 1e-12))) / (ANOVA_PERMS + 1)),
            "sd_within_run_pct": 100.0 * math.sqrt(msw),
            "sd_between_runs_pct": 100.0 * math.sqrt(max(0.0, (msb - msw) / n0))}


def decomposition(jobs, minimum):
    """Part D for every CPU model of the primary pool with at least `minimum` jobs."""
    out = []
    for model, idx in sorted(jobs.models.items()):
        if len(idx) < minimum:
            continue
        blk = jobs.block(model)
        assessed = {r["run_id"] for r in blk["per_run"] if r["form"] is not None}
        cells = [c for c in blk["cells"] if c["size_class"] in IN_CACHE]
        rows = []
        for c in cells:
            cid = c["cell_id"]
            for col in COLUMNS:
                ys, ses = [], []
                for i in idx:
                    jc = jobs.by_id[i][cid]
                    lo, hi = ci_of(jc, col)
                    ys.append(math.log(ratio_of(jc, col)))
                    ses.append((math.log(hi) - math.log(lo)) / (2.0 * Z))
                pj = c[col]["per_job"]
                assert len(pj) == len(ys) and all(math.isclose(math.log(p), v, rel_tol=1e-9, abs_tol=1e-12) for p, v in zip(pj, ys)), \
                    f"{model} {cid} {col}: the job files do not line up with the stored per_job ratios"
                y = np.array(ys)
                se = np.array(ses)
                n = len(y)
                sd_total = float(y.std(ddof=1))
                se_rms = float(math.sqrt(float(np.mean(se ** 2))))
                w = 1.0 / se ** 2
                ybar_w = float(np.sum(w * y) / np.sum(w))
                q = float(np.sum(w * (y - ybar_w) ** 2))
                groups = []
                for rid in sorted(assessed):
                    g = [j for j, i in enumerate(idx) if jobs.run_ids[i] == rid]
                    groups.append(g)
                an = anova_by_run(ys, groups, (model, cid, col)) if len(groups) >= 2 else None
                row = {"cell_id": cid, "column": col, "jobs": n, "mean_ratio": float(math.exp(float(y.mean()))),
                       "sd_between_jobs_pct": 100.0 * sd_total, "within_job_se_rms_pct": 100.0 * se_rms,
                       "within_job_se_mean_pct": 100.0 * float(se.mean()),
                       "ratio_total_to_within": sd_total / se_rms,
                       "cochran_q": q, "cochran_q_per_df": q / (n - 1), "anova_by_run": an}
                if an:
                    row["ratio_within_run_to_within"] = (an["sd_within_run_pct"] / 100.0) / se_rms
                rows.append(row)
        rec = {"cpu_model": model, "jobs": len(idx), "assessed_runs": len(assessed), "rows": rows}
        rt = sorted(r["ratio_total_to_within"] for r in rows)
        rec["summary"] = {"rows": len(rows), "median_ratio_total_to_within": float(rt[len(rt) // 2]),
                          "rows_ratio_above_2": sum(1 for r in rows if r["ratio_total_to_within"] > 2.0),
                          "rows_anova": sum(1 for r in rows if r["anova_by_run"]),
                          "rows_anova_p_below_0_05": sum(1 for r in rows if r["anova_by_run"] and r["anova_by_run"]["p_perm"] < 0.05)}
        out.append(rec)
    return out


# ---------------------------------------------------------------- part E: job-exchangeability null

class PermSetup:
    def __init__(self, jobs, model):
        self.jobs, self.model = jobs, model
        blk = jobs.block(model)
        self.assessed = [r for r in blk["per_run"] if r["form"] is not None]
        self.stored_runs = self.assessed
        self.idx = [i for i in jobs.models[model] if jobs.run_ids[i] in {r["run_id"] for r in self.assessed}]
        self.cell_ids = list(self.assessed[0]["cells"])
        self.sizes = [r["jobs"] for r in self.assessed]
        self.pairs = {}
        for cid in self.cell_ids:
            for col in COLUMNS:
                self.pairs[(cid, col)] = {i: (ratio_samples(jobs.by_id[i][cid], col)) for i in self.idx}

    def true_assignment(self):
        return [[i for i in self.idx if self.jobs.run_ids[i] == r["run_id"]] for r in self.assessed]

    def shuffled(self, p):
        keys = hp.splitmix64(cal_seed("perm", self.model, p), len(self.idx))
        order = np.argsort(keys, kind="stable")
        sh = [self.idx[int(j)] for j in order]
        out, pos = [], 0
        for s in self.sizes:
            out.append(sorted(sh[pos:pos + s]))
            pos += s
        return out

    def run_records(self, assignment):
        runs = []
        for r, members in zip(self.assessed, assignment):
            cells = {}
            for cid in self.cell_ids:
                cells[cid] = {}
                for col in COLUMNS:
                    s = hp.pair_stat(self.model, f"{cid}|{col}", [self.pairs[(cid, col)][i] for i in members])
                    cells[cid][col] = [s["ratio"], s["ci95"][0], s["ci95"][1]]
            runs.append({"run_id": r["run_id"], "jobs": len(members), "form": "x", "cells": cells})
        return runs


def ratio_samples(cell, col):
    return (cell["none_ns"], cell["fast_ns"]) if col == "as_compiled" else (cell["aligned"]["none_ns"], cell["aligned"]["fast_ns"])


def perm_record(runs):
    el = Elements(runs)
    return {"outside": int(el.outside.sum()), "checked": int(el.n), "expected_outside": float(el.p_stored.sum()),
            "pair_z_rms": z_summary(el.z)["rms"], "pair_z_share_abs_gt_1_96": z_summary(el.z)["share_abs_gt_1_96"]}


def permutation_null(jobs, model, perms, only=None):
    """Part E for one model: the identity shuffle (must give the stored per_run records) and `perms` shuffles. only: a list of
    shuffle indices to compute (verify) instead of range(perms)."""
    ps = PermSetup(jobs, model)
    ident_runs = ps.run_records(ps.true_assignment())
    dev = 0.0
    for got, want in zip(ident_runs, ps.stored_runs):
        for cid in ps.cell_ids:
            for col in COLUMNS:
                for a, b in zip(got["cells"][cid][col], want["cells"][cid][col]):
                    dev = max(dev, abs(a - b) / abs(b))
    ident = perm_record(ident_runs)
    ident["max_rel_diff_to_stored_per_run"] = dev
    recs = []
    for p in (range(perms) if only is None else only):
        recs.append(perm_record(ps.run_records(ps.shuffled(p))))
        if only is None and (p + 1) % 10 == 0:
            log(f"  {model}: {p + 1}/{perms} shuffles")
    return {"cpu_model": model, "assessed_runs": ps.sizes, "jobs": len(ps.idx), "identity": ident, "shuffles": recs}


def permutation_summary(block, observed):
    outs = np.array([r["outside"] for r in block["shuffles"]])
    n = len(outs)
    return {"n": n, "observed": observed, "mean": float(outs.mean()), "sd": float(outs.std(ddof=1)), "min": int(outs.min()),
            "median": float(np.median(outs)), "max": int(outs.max()),
            "count_ge_observed": int(np.sum(outs >= observed)), "p_ge_observed": float((1 + np.sum(outs >= observed)) / (n + 1)),
            "mean_expected_outside": float(np.mean([r["expected_outside"] for r in block["shuffles"]])),
            "mean_pair_z_rms": float(np.mean([r["pair_z_rms"] for r in block["shuffles"]]))}


# ---------------------------------------------------------------- part F: verdict word against job count

def subset_list(model, n, j, count):
    total = math.comb(n, j)
    if total <= count:
        return [tuple(c) for c in itertools.combinations(range(n), j)], total
    seen, out, t = set(), [], 0
    while len(out) < count:
        keys = hp.splitmix64(cal_seed("subset", model, j, t), n)
        idx = tuple(sorted(int(i) for i in np.argsort(keys, kind="stable")[:j]))
        t += 1
        if idx not in seen:
            seen.add(idx)
            out.append(idx)
    return out, total


def why_kind(compare, why):
    if why.startswith("MAP"):
        return "map"
    return next((k for pfx, k in compare.WHY_KINDS if why.startswith(pfx)), "other")


def subset_block(jobs, crit, compare, model, j):
    docs = [jobs.docs[i] for i in jobs.models[model]]
    subs, total = subset_list(model, len(docs), j, SUBSETS)
    rows, forms = [], {}
    for idx in subs:
        blk = hp.analyse_cpu(model, [docs[i] for i in idx], crit, full=False)
        v = blk["verdict"]
        rows.append({"jobs": ",".join(str(i) for i in idx), "form": v["form"], "kind": why_kind(compare, v["why"]),
                     "aa_half_width_pct": blk["aa"]["half_width_pct"]})
        forms[v["form"]] = forms.get(v["form"], 0) + 1
    return {"available": len(docs), "distinct_possible": total, "exhaustive": total <= SUBSETS, "count": len(rows),
            "forms": dict(sorted(forms.items())), "rows": rows}


def subsets(jobs, crit, compare, only=None):
    out = {}
    for model, idx in sorted(jobs.models.items()):
        if len(idx) < 3:
            continue
        rec = {"jobs": len(idx), "full_pool_form": jobs.block(model)["verdict"]["form"], "by_j": {}}
        for j in SUBSET_JS:
            if only and (model, j) not in only:
                continue
            if len(idx) <= j:
                rec["by_j"][str(j)] = {"available": len(idx), "note": "not run: the model has no more jobs than J"}
                continue
            t0 = time.time()
            rec["by_j"][str(j)] = subset_block(jobs, crit, compare, model, j)
            log(f"  subsets {model} J={j}: {rec['by_j'][str(j)]['forms']} ({time.time() - t0:.0f} s)")
        out[model] = rec
    return out


# ---------------------------------------------------------------- the whole file

def inputs_block(jobs):
    pools = {}
    for key, rel, role in RUN_POOLS:
        d = load_json(rel)
        pools[key] = {"path": rel, "role": role, "sha256": lf_sha(rpath(rel)), "jobs": len(d["inputs"]), "runs": len(d["runs"]),
                      "criteria_sha256": d["criteria_sha256"]}
    return {"pools": pools,
            "job_files": {"pool": jobs.key, "count": len(jobs.docs), "sha256": jobs.files_sha()},
            "replication_results": {"path": REPLICATION_RESULTS, "sha256": lf_sha(rpath(REPLICATION_RESULTS))},
            "criteria": {"path": CRITERIA, "sha256": lf_sha(rpath(CRITERIA))},
            "harness_pool_py": {"path": POOL_PY, "sha256": lf_sha(rpath(POOL_PY))},
            "replication_compare_py": {"path": COMPARE_PY, "sha256": lf_sha(rpath(COMPARE_PY))}}


MODEL_TEXT = ("Each run's estimate of one cell is normal around the same true value; the run's stated 95% interval half-width is "
              "1.96 standard deviations, s = (ln hi - ln lo) / (2 x 1.96); errors are independent between runs. For an ordered "
              "pair (A, B) the log difference of the two points has variance s_A^2 + s_B^2. 'outside' is the count the README "
              "quotes (A's point outside B's stored [lo, hi]); expected_outside uses B's stored offsets around its point, "
              "expected_outside_sym uses 1.96 s_B on both sides. 'pair z' is the difference over its standard deviation "
              "(|z| > 1.96 in 5% of pairs, rms 1, if calibrated). Simulation: SIM_REPS draws; 'independent' = one error per "
              "(run, cell, column); 'common' = one shared draw per run (all cells of a run move together).")


def build_cheap(jobs, compare, minimum):
    t0 = time.time()
    run_pools = {key: run_to_run(key, load_json(rel)) for key, rel, _ in RUN_POOLS}
    log(f"parts A and C done ({time.time() - t0:.0f} s)")
    rep = replication(compare, minimum)
    log(f"part B done ({time.time() - t0:.0f} s)")
    dec = decomposition(jobs, minimum)
    log(f"part D done ({time.time() - t0:.0f} s)")
    return run_pools, rep, dec


def build(full=True):
    crit = load_json(CRITERIA)
    minimum = crit["v3"]["pooling"]["minimum_jobs"]
    compare = load_compare()
    jobs = Jobs()
    run_pools, rep, dec = build_cheap(jobs, compare, minimum)
    perms = {}
    for model in PERM_MODELS:
        t0 = time.time()
        pb = permutation_null(jobs, model, PERMS)
        obs = next(m for m in run_pools[PRIMARY]["models"] if m["cpu_model"] == model)["outside"]
        pb["summary"] = permutation_summary(pb, obs)
        perms[model] = pb
        log(f"part E {model}: {pb['summary']} ({time.time() - t0:.0f} s)")
    subs = subsets(jobs, crit, compare)
    return {"schema": SCHEMA,
            "what": "A calibration baseline for the sentence that the pooled intervals understate run-to-run spread: what the "
                    "stored counts would be if the stated intervals were exactly right, how wide the job-to-job and run-to-run "
                    "spread is against the within-job SE, and how the verdict word depends on the number of jobs. Derived by "
                    "robustness/calibration.py from the stored pooled files; do not edit by hand.",
            "model": MODEL_TEXT,
            "constants": {"z": Z, "sim_reps": SIM_REPS, "perms": PERMS, "perm_models": list(PERM_MODELS), "anova_perms": ANOVA_PERMS,
                          "subsets_per_j": SUBSETS, "subset_js": list(SUBSET_JS), "primary_pool": PRIMARY,
                          "minimum_jobs": minimum, "seed_tag": SEED_TAG},
            "inputs": inputs_block(jobs),
            "run_to_run": run_pools, "replication": rep, "decomposition": dec, "permutation": perms, "subsets": subs}


def dumps(doc):
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


# ---------------------------------------------------------------- verify

VERIFY_SUBSET = ("AMD EPYC 9V74 80-Core Processor", 3)
VERIFY_PERM_MODEL = "AMD EPYC 9V74 80-Core Processor"


def verify():
    if not os.path.exists(OUT):
        print("FAIL robustness/calibration.json is missing")
        return 1
    with open(OUT, encoding="utf-8") as f:
        st = json.load(f)
    crit = load_json(CRITERIA)
    minimum = crit["v3"]["pooling"]["minimum_jobs"]
    compare = load_compare()
    jobs = Jobs()
    bad = []

    def cmp(label, a, b):
        d = same(a, b, label)
        if d:
            bad.append(d)

    cmp("inputs", st["inputs"], inputs_block(jobs))
    if not bad:
        run_pools, rep, dec = build_cheap(jobs, compare, minimum)
        cmp("run_to_run", st["run_to_run"], run_pools)
        cmp("replication", st["replication"], rep)
        cmp("decomposition", st["decomposition"], dec)
        model, j = VERIFY_SUBSET
        got = {"by_j": {str(j): subset_block(jobs, crit, compare, model, j)}}
        cmp(f"subsets/{model}/{j}", st["subsets"][model]["by_j"][str(j)], got["by_j"][str(j)])
        pb = permutation_null(jobs, VERIFY_PERM_MODEL, 1, only=[0])
        cmp("permutation/identity", st["permutation"][VERIFY_PERM_MODEL]["identity"], pb["identity"])
        cmp("permutation/shuffle0", st["permutation"][VERIFY_PERM_MODEL]["shuffles"][0], pb["shuffles"][0])
        # the stored reproduction of the README's counts
        for m in st["run_to_run"][PRIMARY]["models"]:
            if not m["reproduces_stored"]:
                bad.append(f"{m['cpu_model']}: the recomputed count does not equal the stored reproduction")
    if bad:
        print(f"FAIL robustness/calibration.json: {bad[0]}")
        return 1
    print("robustness/calibration.json equals the recomputation of parts A, B, C, D, the identity and first shuffle of "
          f"{VERIFY_PERM_MODEL}, and the J={VERIFY_SUBSET[1]} subsets of {VERIFY_SUBSET[0]}")
    return 0


# ---------------------------------------------------------------- tables (README-calibration.md embeds them)

def pct(x, d=1):
    return f"{100.0 * x:.{d}f}%"


def short(model):
    for k in ("7763", "9V74", "9V45", "8573C", "6973P-C", "8370C", "Neoverse-N2", "Neoverse-V3"):
        if k in model:
            return k
    return model


def tables(doc):
    """The markdown tables of robustness/README-calibration.md, generated from the stored file."""
    lines = []
    lines.append("Table 1. Run-to-run counts (a run's pooled point outside another run's pooled 95% interval, in-cache cells, both columns) "
                 "against the count that perfectly calibrated intervals would give.")
    lines.append("")
    lines.append("| pool | model | jobs per assessed run | outside / compared | observed | expected, stored offsets | expected, symmetric | "
                 "95% range, independent | 95% range, one draw per run | pair z share above 1.96 | rms z |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for key, _, _ in RUN_POOLS:
        for m in doc["run_to_run"][key]["models"]:
            jr = "+".join(str(r["jobs"]) for r in m["runs_assessed"])
            si, sc = m["simulation"]["independent"], m["simulation"]["common"]
            lines.append(f"| {key} | {short(m['cpu_model'])} | {jr} | {m['outside']} / {m['checked']} | {pct(m['outside_share'])} | "
                         f"{pct(m['expected_share'])} ({m['expected_outside']:.1f}) | {pct(m['expected_share_sym'])} | "
                         f"{si['p025']} to {si['p975']} | {sc['p025']} to {sc['p975']} | "
                         f"{pct(m['pair_z']['share_abs_gt_1_96'])} | {m['pair_z']['rms']:.2f} |")
    lines.append("")
    lines.append("Table 2. Replication sets: the new pooled point outside the earlier pool's interval, observed against expected.")
    lines.append("")
    lines.append("| architecture | model | jobs (earlier, new) | outside / compared | expected outside | 95% range, independent | "
                 "95% range, one draw per pool | pair z share above 1.96 | rms z |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for arch in ("arm", "x86"):
        for m in doc["replication"][arch]["models"]:
            si, sc = m["simulation"]["independent"], m["simulation"]["common"]
            lines.append(f"| {arch} | {short(m['cpu_model'])} | {m['earlier_jobs']}, {m['replication_jobs']} | {m['outside']} / {m['checked']} | "
                         f"{m['expected_outside']:.1f} | {si['p025']} to {si['p975']} | {sc['p025']} to {sc['p975']} | "
                         f"{pct(m['pair_z']['share_abs_gt_1_96'])} | {m['pair_z']['rms']:.2f} |")
        t = doc["replication"][arch]["totals"]
        si, sc = t["simulation"]["independent"], t["simulation"]["common"]
        lines.append(f"| {arch} | all testable models | | {t['outside']} / {t['checked']} | {t['expected_outside']:.1f} | "
                     f"{si['p025']} to {si['p975']} | {sc['p025']} to {sc['p975']} | | |")
    lines.append("")
    lines.append("Table 3. Shuffling jobs over runs (same run sizes, 95-job pool): the outside count when jobs carry no run label.")
    lines.append("")
    lines.append("| model | assessed runs (jobs) | observed outside | shuffles | mean | min to max | shuffles at or above observed | "
                 "mean expected under the calibrated normal | mean rms z |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for model, pb in doc["permutation"].items():
        s = pb["summary"]
        lines.append(f"| {short(model)} | {'+'.join(str(x) for x in pb['assessed_runs'])} | {s['observed']} | {s['n']} | {s['mean']:.1f} | "
                     f"{s['min']} to {s['max']} | {s['count_ge_observed']} of {s['n']} | {s['mean_expected_outside']:.1f} | "
                     f"{s['mean_pair_z_rms']:.2f} |")
    lines.append("")
    lines.append("Table 4. Job-to-job spread against the within-job standard error, 95-job pool, as-compiled column, selected in-cache cells "
                 "(sd of the log ratio over all the model's jobs, in percent; within-job SE is the root mean square of each job's own "
                 "ci95 half-width over 1.96).")
    lines.append("")
    lines.append("| model | cell | jobs | sd between jobs | within-job SE | sd over SE | between-run sd | F | permutation p |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for rec in doc["decomposition"]:
        for r in rec["rows"]:
            if r["column"] != "as_compiled" or r["cell_id"] not in TABLE4_CELLS:
                continue
            an = r["anova_by_run"]
            lines.append(f"| {short(rec['cpu_model'])} | {r['cell_id']} | {r['jobs']} | {r['sd_between_jobs_pct']:.2f}% | "
                         f"{r['within_job_se_rms_pct']:.2f}% | {r['ratio_total_to_within']:.1f} | "
                         + (f"{an['sd_between_runs_pct']:.2f}% | {an['f']:.2f} | {an['p_perm']:.3f} |" if an else "n/a | n/a | n/a |"))
    lines.append("")
    lines.append("Table 5. Verdict word of random job subsets of one CPU model (the unchanged pooling code, 30 subsets, or all of them "
                 "when there are 30 or fewer).")
    lines.append("")
    lines.append("| model | jobs | word with all jobs | J | subsets | words |")
    lines.append("|---|---|---|---|---|---|")
    for model, rec in doc["subsets"].items():
        for j in SUBSET_JS:
            b = rec["by_j"].get(str(j))
            if b is None:
                continue
            if "forms" not in b:
                lines.append(f"| {short(model)} | {rec['jobs']} | {rec['full_pool_form']} | {j} | not run | model has {b['available']} jobs |")
                continue
            words = ", ".join(f"{n} {w}" for w, n in b["forms"].items())
            lines.append(f"| {short(model)} | {rec['jobs']} | {rec['full_pool_form']} | {j} | {b['count']}"
                         f"{' (all)' if b['exhaustive'] else ''} | {words} |")
    lines.append("")
    lines.append("Table 6. The run-to-run counts of Table 1 split by loop family (sums of the stored per-cell counts; the three groups were "
                 "chosen after the per-cell counts had been read). Each entry: outside / compared (expected outside).")
    lines.append("")
    lines.append("| pool | model | " + " | ".join(name for name, _ in FAMILIES) + " |")
    lines.append("|---|---|" + "---|" * len(FAMILIES))
    for key, _, _ in RUN_POOLS:
        for m in doc["run_to_run"][key]["models"]:
            fam = family_sums(m)
            lines.append(f"| {key} | {short(m['cpu_model'])} | "
                         + " | ".join(f"{fam[name]['outside']} / {fam[name]['pairs']} ({fam[name]['expected_outside']:.1f})"
                                      for name, _ in FAMILIES) + " |")
    return "\n".join(lines) + "\n"


FAMILIES = (("forward loops (k01, k02, k03)", ("k01", "k02", "k03")),
            ("reverse, stride-2, matrix multiply (k04, k05, k08)", ("k04", "k05", "k08")),
            ("gather, histogram (k06, k07)", ("k06", "k07")))


def family_sums(model_record):
    """Sum a run_to_run model record's by_cell counts over the loop families of FAMILIES (the kernel id is the part of the cell id
    before the first underscore)."""
    out = {}
    for name, ks in FAMILIES:
        cells = [c for c in model_record["by_cell"] if c["cell_id"].split("_")[0] in ks]
        out[name] = {"pairs": sum(c["pairs"] for c in cells), "outside": sum(c["outside"] for c in cells),
                     "expected_outside": sum(c["expected_outside"] for c in cells)}
    return out


TABLE4_CELLS = ("k05_stride2.L2", "k08_matmul.L1", "k08_matmul.L2", "k04_rev.L2", "k01_sum_fwd.L2", "k06_gather.L2")


def counts_only():
    crit = load_json(CRITERIA)
    minimum = crit["v3"]["pooling"]["minimum_jobs"]
    compare = load_compare()
    for key, rel, role in RUN_POOLS:
        rec = run_to_run(key, load_json(rel))
        for m in rec["models"]:
            si = m["simulation"]["independent"]
            print(f"{key:10s} {short(m['cpu_model']):12s} outside {m['outside']:4d}/{m['checked']:<5d} ({pct(m['outside_share'])}) "
                  f"stored {m['stored_outside']}/{m['stored_checked']} {'OK' if m['reproduces_stored'] else 'DIFFERS'}  expected "
                  f"{m['expected_outside']:.1f} ({pct(m['expected_share'])}; sym {pct(m['expected_share_sym'])})  sim95 {si['p025']}-{si['p975']}  "
                  f"z>1.96 {pct(m['pair_z']['share_abs_gt_1_96'])} rms z {m['pair_z']['rms']:.2f}")
    rep = replication(compare, minimum)
    for arch in ("arm", "x86"):
        for m in rep[arch]["models"]:
            si = m["simulation"]["independent"]
            print(f"replication {arch} {short(m['cpu_model']):12s} outside {m['outside']}/{m['checked']} expected {m['expected_outside']:.1f} "
                  f"sim95 {si['p025']}-{si['p975']} stored {m['stored_outside']} {'OK' if m['reproduces_stored'] else 'DIFFERS'}")
        t = rep[arch]["totals"]
        print(f"replication {arch} total outside {t['outside']}/{t['checked']} expected {t['expected_outside']:.1f}")
    return 0


def main(argv):
    if "--verify" in argv:
        return verify()
    if "--counts" in argv:
        return counts_only()
    if "--full" in argv:
        t0 = time.time()
        doc = build()
        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(doc))
        log(f"wrote {OUT} ({time.time() - t0:.0f} s)")
        print(tables(doc))
        return 0
    if not os.path.exists(OUT):
        print("robustness/calibration.json is missing; run with --full")
        return 1
    with open(OUT, encoding="utf-8") as f:
        print(tables(json.load(f)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
