"""Small-fixture tests of robustness/analyze.py (pytest, or robustness/check.py's built-in runner)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import analyze  # noqa: E402
import pool  # noqa: E402


def _jobs(J=4, L=40, ratio=1.5, noise=0.0, seed=1):
    rng = np.random.default_rng(seed)
    out = []
    for j in range(J):
        a = 100.0 * (1 + 0.1 * j) * (1 + noise * rng.standard_normal(L))
        b = a * ratio * (1 + noise * rng.standard_normal(L))
        out.append([a.tolist(), b.tolist()])
    return out


RATIO = lambda ma, mb: mb / ma  # noqa: E731


def test_splitmix_is_the_harnesss():
    assert analyze.pool.splitmix64 is pool.splitmix64
    first = pool.splitmix64(0, 2)
    assert int(first[0]) == 0xE220A8397B1DCDAF  # published splitmix64 output 1 for seed 0
    assert int(first[1]) == 0x6E789E6AA1B965F4


def test_lag1_and_neff():
    x = np.arange(20, dtype=float)
    assert analyze.lag1(x) > 0.8
    assert analyze.lag1(np.ones(10)) == 0.0
    alt = np.array([1.0, -1.0] * 10)
    assert analyze.lag1(alt) < -0.8
    assert analyze.n_eff(40, 0.0) == 40
    assert analyze.n_eff(40, -0.5) == 40            # negative correlation is not rewarded
    assert math.isclose(analyze.n_eff(40, 0.5), 40 / 3)


def test_noiseless_data_gives_degenerate_intervals_in_every_method():
    sbj = _jobs(noise=0.0)
    for m in analyze.METHODS:
        r = analyze.stat_fn(m)("cpu", "x", sbj, RATIO)
        assert math.isclose(r["ratio"], 1.5)
        lo, hi = r["ci95"]
        assert math.isclose(lo, 1.5, rel_tol=1e-9) and math.isclose(hi, 1.5, rel_tol=1e-9), m


def test_method_a_is_the_harness():
    sbj = _jobs(noise=0.02)
    mine = analyze.stat_fn("a")("cpu", "x", sbj, RATIO)
    theirs = pool.pooled_stat("cpu", "x", sbj, RATIO)
    assert mine == theirs


def test_block_picks_consecutive_pairs():
    # a_k = k, so any median reveals which repetitions were picked; with blocks of 1 ABBA (2 reps) a drawn block always
    # contributes reps 2m and 2m+1 together: the multiset of picked values has an even count of each pair member.
    J, L = 1, 8
    a = [float(k) for k in range(L)]
    b = [float(k) for k in range(L)]
    sbj = [[a, b]]
    r = analyze.block_stat("cpu", "t", sbj, RATIO, bs=1, resamples=50)
    assert r["ratio"] == 1.0
    # identical sides and identical block draws: every resample ratio is exactly 1
    assert r["ci95"][0] == 1.0 and r["ci95"][1] == 1.0


def test_block_widens_with_autocorrelated_noise():
    rng = np.random.default_rng(5)
    J, L = 6, 40
    sbj = []
    for j in range(J):
        e = np.zeros(L)
        for k in range(1, L):                       # AR(1), rho 0.8
            e[k] = 0.8 * e[k - 1] + 0.01 * rng.standard_normal()
        a = 100.0 * np.exp(0.002 * rng.standard_normal(L))
        b = 150.0 * np.exp(e)                                    # the drift is in the ratio itself
        sbj.append([a.tolist(), b.tolist()])
    wa = analyze.stat_fn("a")("cpu", "x", sbj, RATIO)["ci95"]
    wd = analyze.stat_fn("d")("cpu", "x", sbj, RATIO)["ci95"]
    assert (wd[1] - wd[0]) > (wa[1] - wa[0])        # the n_eff correction can only widen
    assert wd[0] < 1.5 < wd[1]


def test_jobs_only_t_matches_hand_computation():
    sbj = []
    for r in (1.0, 1.1, 1.2):
        a = [100.0] * 40
        sbj.append([a, [100.0 * r] * 40])
    res = analyze.jobs_only_stat("cpu", "x", sbj, RATIO, t_interval=True)
    logs = np.log([1.0, 1.1, 1.2])
    h = 4.303 * np.std(logs, ddof=1) / math.sqrt(3)
    assert math.isclose(res["ci95"][0], math.exp(logs.mean() - h))
    assert math.isclose(res["ci95"][1], math.exp(logs.mean() + h))
    boot = analyze.jobs_only_stat("cpu", "x", sbj, RATIO)
    assert min(1.0, 1.1, 1.2) <= boot["ci95"][0] <= boot["ci95"][1] <= 1.2


def test_install_and_restore_swap_the_harness_functions():
    analyze.install("b")
    assert pool.pair_stat is not analyze.ORIG_PAIR
    analyze.restore()
    assert pool.pair_stat is analyze.ORIG_PAIR and pool.placement_stat is analyze.ORIG_PLACEMENT


def test_quad_placement_statistic_runs_under_every_method():
    quads = []
    for j in range(3):
        n = [100.0 + j] * 40
        quads.append([n, [150.0 + j] * 40, [100.0 + j] * 40, [149.0 + j] * 40])
    comb = lambda n, f, na, fa: (f / n) / (fa / na)  # noqa: E731
    for m in analyze.METHODS:
        r = analyze.stat_fn(m)("cpu", "q", quads, comb)
        assert 0.99 < r["ratio"] < 1.02, m


def test_compare_flags_a_flip():
    cell_a = {"class": "lost", "ac": [2.0, 1.6, 2.4], "al": [2.0, 1.6, 2.4], "lost_ok": True}
    cell_b = {"class": "lost", "ac": [2.0, 1.4, 2.6], "al": [2.0, 1.6, 2.4], "lost_ok": False}
    mk = lambda c: {"form": "map", "aa_hw_pct": 1.0, "limit_pct": 2.0, "cells": {"x.L1": c}}  # noqa: E731
    res = {"methods": {"a": mk(cell_a), "b": mk(cell_b)}}
    c = analyze.compare(res, "b")
    assert c["flips"]["lost_ok"] == ["x.L1"] and c["counts"]["lost_ok"] == 1
    assert math.isclose(c["width_max"], 1.2 / 0.8) and math.isclose(c["width_median"], (1.5 + 1.0) / 2)
