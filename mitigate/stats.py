"""The statistics of the study: a ratio of medians and its percentile-bootstrap 95 % interval.

Plain standard-library Python, so it runs on the Actions runner and on a Windows laptop alike.

The question every timed cell asks: how much slower is the FAST build than the NONE build?
We time each build 20 times (one process per repetition) and compare their medians:

    ratio = median(fast samples) / median(none samples)

A ratio of 1.00 means no cost; 1.50 means FAST takes 50 % longer.

Twenty samples per side is not much, so the ratio comes with an interval that says how far it
could move if we had drawn a different 20. We get that interval with the percentile bootstrap:

1. Draw 20 values from the NONE samples *with replacement* (some repeat, some are left out),
   and 20 from the FAST samples the same way, each side on its own.
2. Compute the ratio of the two medians for that draw.
3. Repeat 10 000 times, sort the 10 000 ratios, and read off the values 2.5 % and 97.5 % of
   the way through the sorted list. Those two values are the 95 % interval.

The random draws use a fixed seed, so the same samples always give exactly the same interval,
on any machine. That is what lets scripts/check.py recompute every interval in results.json
and demand an exact match.
"""
import random
import statistics

SEED = 20261011
RESAMPLES = 10000
LEVEL = 0.95


def median(values):
    """The middle value of the samples (the mean of the two middle values for an even count).

    The median is used instead of the mean because a shared runner throws occasional slow
    outliers (another tenant, an interrupt); one outlier moves the mean but barely moves the median.
    """
    if not values:
        raise ValueError("median of an empty list")
    return statistics.median(values)


def ratio_of_medians(none_ns, fast_ns):
    """median(fast_ns) / median(none_ns): how many times longer the FAST build takes."""
    return median(fast_ns) / median(none_ns)


def percentile_interval(sorted_values, level=LEVEL):
    """The (lo, hi) values that cut off (1 - level) / 2 at each end of an already sorted list.

    With 10 000 values and level 0.95 this returns the values at positions 250 and 9749
    (counting from 0): 250 values lie below lo and 250 above hi.
    """
    n = len(sorted_values)
    if n == 0:
        raise ValueError("interval of an empty list")
    tail = (1.0 - level) / 2.0
    # round(..., 9) first, so float error such as 0.975 * 10000 = 9749.9999999 cannot shift a position
    lo_index = int(round(tail * n, 9))
    hi_index = int(round((1.0 - tail) * n, 9)) - 1
    hi_index = max(lo_index, min(n - 1, hi_index))
    return sorted_values[lo_index], sorted_values[hi_index]


def bootstrap_ratio_ci(none_ns, fast_ns, resamples=RESAMPLES, seed=SEED, level=LEVEL):
    """Percentile-bootstrap interval for ratio_of_medians(none_ns, fast_ns).

    Each resample draws len(fast_ns) values from fast_ns and len(none_ns) values from none_ns,
    with replacement and independently, and records the ratio of their medians.
    Returns (lo, hi). The same inputs and seed always return the same (lo, hi).
    """
    if len(none_ns) == 0 or len(fast_ns) == 0:
        raise ValueError("both sides need at least one sample")
    rng = random.Random(seed)
    n_none, n_fast = len(none_ns), len(fast_ns)
    ratios = []
    for _ in range(resamples):
        fast_draw = rng.choices(fast_ns, k=n_fast)
        none_draw = rng.choices(none_ns, k=n_none)
        ratios.append(statistics.median(fast_draw) / statistics.median(none_draw))
    ratios.sort()
    return percentile_interval(ratios, level)


def half_width_pct(ci95):
    """Half the width of an interval on a ratio, in percent: (hi - lo) / 2 * 100.

    For the A/A control (a binary timed against a byte-identical copy of itself) this is the
    noise floor: an effect smaller than it cannot be told apart from noise.
    """
    lo, hi = ci95
    return (hi - lo) / 2.0 * 100.0


def summarize(none_ns, fast_ns):
    """The three numbers results.json stores for a pair: ratio, ci95 [lo, hi] and half_width_pct."""
    lo, hi = bootstrap_ratio_ci(none_ns, fast_ns)
    return {"ratio": ratio_of_medians(none_ns, fast_ns), "ci95": [lo, hi],
            "half_width_pct": half_width_pct((lo, hi))}
