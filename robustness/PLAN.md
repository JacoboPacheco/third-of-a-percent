# Robustness of the intervals to autocorrelated repetitions (exploratory)

Written Tue Oct 13 2026 about 15:06 EDT (the first commit message said 15:20 in an earlier draft of this line, which was wrong), before any number of this analysis existed.

## Status of this analysis
Exploratory sensitivity analysis. NOT a rule change. The verdicts in `results/s4-pooled/pooled.json` and
`results/s5-holdout/pooled.json` (harness/criteria-v3.json, harness/pool.py) stay the reading of record. Nothing in
harness/, the criteria files, site/, README or scripts/check.py is edited by this folder. No new runs: only the stored
raw samples are used.

## The objection (a limitation noted before this column, H1)
The harness resamples the repetitions of a side independently. The repetitions are consecutive processes on one shared VM
in ABBA order, so drift and noisy neighbours make them autocorrelated; the intervals may then be too narrow.

## Data
Every job `results.json` named in the `inputs` of results/s4-pooled/pooled.json (30 jobs) and
results/s5-holdout/pooled.json (30 jobs). The two datasets are analysed separately, as the harness pools them.
CPU models with at least 3 jobs in a dataset are analysed. Cells: every in-cache (L1, L2) cell, both columns (as compiled,
aligned), plus the controls the verdict reads (byte-identical A/A, layout A/A, NOVEC/NONE) and the placement statistic D.

## Four ways to compute a pooled ratio and its 95 % interval
(a) The harness's own two-level bootstrap (harness/pool.py unchanged, its splitmix64 helper imported unchanged).
    Self-test: it must reproduce the stored ratios and intervals (to 1e-12 relative; exact matches counted and printed).
(b) Block bootstrap inside jobs. The stored order is ABBA: repetition k=2m runs A then B, k=2m+1 runs B then A, so the
    process sequence is A B B A A B B A ... Block m = repetitions 2m and 2m+1 = four consecutive processes (ABBA) and
    keeps the A and B values of both repetitions together. Per resample: draw jobs with replacement as in (a), then inside
    each job draw whole blocks with replacement (20 blocks of 4 processes for 40 reps), take the median of each side over
    the drawn blocks, ratio, geometric mean over jobs. Same B=2000, same percentiles. Sensitivity: blocks of 2 and 5
    ABBA quartets (8 and 20 processes), reported only as interval widths. For the placement statistic D (two pairs
    measured one after another) blocks are drawn independently for the two pairs.
(c) Jobs-only bootstrap: each job's ratio of medians is one observation; resample jobs only (B=2000), geometric mean,
    percentiles. Because percentiles of 3 to 6 observations are coarse, a t interval on ln r_j (J-1 degrees of freedom) is
    also computed, labelled (c-t). Both are between-job spread only.
(d) Lag-1 autocorrelation per job series with an effective-sample-size correction (a lower bound on trust, normal
    approximation): the series is e_k = ln(b_k / a_k) over k = 0..39 (adjacent processes). rho_j = lag-1 autocorrelation
    (negative values clipped to 0, upper clip 0.95), n_eff = n (1 - rho) / (1 + rho). The within-job part of the variance of
    the pooled log ratio, (1/J^2) sum_j var(e)/n, is replaced by the same with n_eff, inside the (a) interval:
    half-width_d^2 = half-width_a^2 - within_iid + within_corrected (log scale, symmetric about the (a) point).

## What is compared
For every dataset and CPU model: (1) cells whose classification changes under (b), (c), (c-t), (d) versus (a):
forward cell passes the forward rule on the aligned column (ratio <= 1.02 and ci95_hi <= 1 + max(2 %, 2 x pooled A/A
half-width of that method)); lost cell has ci95_lo >= 1.5 in both columns; cell is placement-sensitive; (2) the ratio of
interval widths versus (a), median and max, over in-cache cells and both columns; (3) the per-CPU verdict form (MAP,
HOLDS_EVERYWHERE, INCONCLUSIVE) from the harness's own harness/pool.py analyse_cpu with the interval functions swapped
(monkey-patched in memory only), so the verdict logic is the harness's and only the intervals differ.

## What would change the page text (fixed now)
- If every CPU model keeps its verdict form under (b) and (c-t) and every lost cell keeps ci95_lo >= 1.5: no change to the
  verdict text. If the (b) intervals are on median more than 1.5 times wider than (a), one sentence is added to the page's
  limits box: the intervals assume independent repetitions, a block bootstrap gives about N times wider intervals, same
  verdicts.
- If a CPU model's form changes under (b) AND under (c-t): the page's per-CPU verdict for that model is reworded to say it
  does not survive an interval that allows autocorrelation (the harness verdict stays shown as the registered one).
- If it changes under only one of them, or only under the lower-bound (d): reported in report.md, no page change.
- No threshold of the harness is touched in any case.

## Not claimed
Block bootstrap is itself an approximation with 20 blocks per job. (d) uses a lag-1 AR(1) model and 40-point series
(the lag-1 estimate is biased low by about 1/n). Dataset s5 was a holdout run under frozen rules; this analysis does not
change that status.

## Change log (written after the first run of analyze.py, Tue Oct 13 2026 15:11 EDT)
- The first full run (method (d) exactly as written above) gave max width ratios of 5 to 11 on a few cells while the median
  lag-1 autocorrelation was about 0 and the block bootstrap widened by at most 1.6. Cause: W_iid is a variance of MEANS of
  log ratios; the harness bootstraps MEDIANS, so on heavy-tailed series W_iid exceeds the median's variance and the formula
  `sd_a^2 - W_iid + W_cor` subtracts too little. That is a flaw of the formula, not autocorrelation. The first form is kept
  as method (d0) and reported; the final (d) multiplies the within-job share of sd_a^2 by W_cor / W_iid (the pure
  autocorrelation inflation, in which the mean-versus-median mismatch cancels): var_d = sd_a^2 x ((1 - s) + s x W_cor / W_iid),
  s = min(1, W_iid / sd_a^2). No other change; the pre-announced page-text rules above are unchanged and were not edited.
