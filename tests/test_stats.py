"""Known answers for harness/stats.py."""
import json
import os

import stats

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_median_odd_and_even():
    assert stats.median([3, 1, 2]) == 2
    assert stats.median([4, 1, 3, 2]) == 2.5


def test_median_ignores_one_outlier():
    assert stats.median([10, 10, 10, 10, 1000]) == 10


def test_ratio_of_medians():
    assert stats.ratio_of_medians([100, 100, 100], [150, 150, 150]) == 1.5
    assert stats.ratio_of_medians([1, 2, 3], [2, 4, 6]) == 2.0


def test_percentile_positions_for_10000_values():
    # 250 values below lo and 250 above hi
    assert stats.percentile_interval(list(range(10000))) == (250, 9749)


def test_percentile_positions_for_other_levels():
    assert stats.percentile_interval(list(range(1000)), level=0.90) == (50, 949)
    assert stats.percentile_interval([7]) == (7, 7)


def test_constant_samples_give_a_zero_width_interval():
    lo, hi = stats.bootstrap_ratio_ci([100.0] * 20, [200.0] * 20)
    assert lo == hi == 2.0


def test_same_seed_same_interval():
    a = [100 + (i * 7) % 13 for i in range(20)]
    b = [110 + (i * 5) % 11 for i in range(20)]
    assert stats.bootstrap_ratio_ci(a, b) == stats.bootstrap_ratio_ci(a, b)
    assert stats.bootstrap_ratio_ci(a, b, seed=1) != stats.bootstrap_ratio_ci(a, b, seed=2)


def test_interval_contains_the_point_estimate():
    a = [100 + (i * 7) % 13 for i in range(20)]
    b = [110 + (i * 5) % 11 for i in range(20)]
    lo, hi = stats.bootstrap_ratio_ci(a, b)
    assert lo <= stats.ratio_of_medians(a, b) <= hi


def test_aa_of_identical_lists_contains_one():
    a = [100 + (i * 7) % 13 for i in range(20)]
    lo, hi = stats.bootstrap_ratio_ci(a, list(a))
    assert lo <= 1.0 <= hi


def test_half_width_pct():
    assert abs(stats.half_width_pct([0.99, 1.01]) - 1.0) < 1e-12
    assert stats.half_width_pct([2.0, 2.0]) == 0.0


def test_summarize_keys():
    s = stats.summarize([100.0] * 20, [150.0] * 20)
    assert s == {"ratio": 1.5, "ci95": [1.5, 1.5], "half_width_pct": 0.0}


def test_reproduces_the_day_one_intervals_exactly():
    """Real samples from day-one run 38116223923: the same method must give the same numbers
    that dayone/evaluate.py stored, to the last digit."""
    with open(os.path.join(DATA, "dayone_samples.json"), encoding="utf-8") as f:
        cells = json.load(f)
    for cid in ("k03_stencil.L1", "k04_rev.L1"):
        c = cells[cid]
        s = stats.summarize(c["none_ns"], c["fast_ns"])
        assert s["ratio"] == c["dayone_ratio"], cid
        assert s["ci95"] == c["dayone_ci95"], cid
