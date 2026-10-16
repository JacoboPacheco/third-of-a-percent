# Do the intervals survive autocorrelated repetitions? (exploratory)

Tue Oct 13 2026 (s4 and s5); the s6 dataset was added Thu Oct 15 2026. Method and pre-announced consequences: `PLAN.md`.
This is a sensitivity analysis from the stored raw samples only; the harness verdicts stay the reading of record, it is
not a rule change, and nothing in harness/, site/ or the criteria was touched.
Datasets, each analysed on its own: the 30 jobs of results/s4-pooled (the original pool), the 30 jobs of
results/s5-holdout, and the 75 jobs of results/s6-pooled (the 30 jobs of s4 plus 45 jobs of ten later runs, pooled under
the same harness/criteria-v3.json; s5 is not part of it). CPU models with at least 3 jobs: in s4 and s5 EPYC 7763: 19 jobs;
9V45: 5 and 3; 9V74: 5 and 6 (the one or two Xeon jobs are too few); in s6 EPYC 7763: 20 jobs, 9V45: 20, 9V74: 23, Xeon
Platinum 8573C: 6, Xeon 6973P-C: 6. Methods: (a) the harness bootstrap, (b) block bootstrap over ABBA quartets (b2, b5:
longer blocks), (c) jobs only (bootstrap, and t), (d) lag-1 n_eff correction (d0 is its first form, kept; see the change
log in PLAN.md). The sections "In plain words (s4 and s5)" and "Conclusion (s4 and s5)" are the original text; the s6
sections follow them.

## In plain words (s4 and s5)
- The repetitions are barely autocorrelated. The median lag-1 autocorrelation of the per-repetition log ratio is between
  -0.02 and +0.03 on every CPU model (an independent series of 40 would average about -0.025); about 12 to 23 % of the
  series have rho above 0.2; the median effective sample size is 94 to 100 % of the nominal one. The NONE-time series alone
  is slightly more autocorrelated on 9V45 (0.12 and 0.15), the model with only 3 to 5 jobs.
- Method (a) reproduces all 396 stored numbers of each dataset to within 1e-12 relative (self-test passed).
- Block bootstrap (b), the direct answer to the objection: median interval width 0.87 to 1.00 times the harness's, maximum
  1.02 to 1.15. Longer blocks (b2, b5) reach at most 1.6 on single cells. No cell changes classification under (b): 0 of 6
  forward cells, 0 of 6 lost cells and 0 of 6 placement flags per CPU model, in both datasets. The verdict form is unchanged
  under (b) for every CPU model in both datasets (MAP on 7763 and 9V74, MAP on 9V45 in s4, INCONCLUSIVE on 9V45 in s5, as
  stored).
- Lag-1 correction (d), the lower bound on trust: median width 1.02 to 1.07, maximum 1.13 to 1.44. Its first form (d0)
  shows maximum widths of 5 to 11 on a few cells; that is a mean-versus-median artefact of the formula (see PLAN.md), not
  autocorrelation, and is listed only so the first number is not hidden.
- Jobs only (c, c-t): not wider than the harness on the 19-job and 5 to 6-job models (median 0.6 to 1.0); wider on 9V45 in s5
  (3 jobs, t interval median 1.57, max 2.67), which is what 3 jobs deserve.
- The lost-loop minimum is not close: the smallest lost-cell ci95_lo is 2.78 to 4.05 under every method, against the rule of
  1.5. The largest forward ci95_hi is 1.000 to 1.005 on 7763 and 9V74 under every method (limit 1.02).
- Where verdicts do move: only the thin model, EPYC 9V45. In s4 (5 jobs) MAP becomes INCONCLUSIVE under (b2) (blocks of 8
  processes; one forward cell reaches ci95_hi 1.024 against the 1.02 limit) and under (d); it stays MAP under (b), (b5), (c),
  (c-t). In s5 (3 jobs) it is INCONCLUSIVE as stored and under (b), (b2), (b5), (c-t), (d), and MAP only under the jobs-only
  percentile bootstrap, whose percentiles of 3 observations are degenerate.

## In plain words (s6: 75 jobs, five CPU models)
- Method (a) reproduces all 495 stored numbers of the 75-job pool to within 1e-12 relative (self-test passed), and the
  stored verdict form of all five CPU models: MAP on EPYC 7763 (20 jobs), 9V45 (20) and 9V74 (23); INCONCLUSIVE on the Xeon
  Platinum 8573C (6 jobs) and the Xeon 6973P-C (6 jobs).
- The repetitions are again barely autocorrelated. The median lag-1 autocorrelation of the per-repetition log ratio is
  between -0.010 and +0.049 on every CPU model; 14 to 21 % of the series have rho above 0.2; the median effective sample
  size is 91 to 100 % of the nominal one. The NONE-time series alone is more autocorrelated on EPYC 9V45 (0.161), the Xeon
  8573C (0.169) and the Xeon 6973P-C (0.386), while the ratio series on the same models stays at 0.048, 0.049 and 0.037,
  which is what a drift shared by both sides of a repetition would give.
- Block bootstrap (b): median interval width 0.75 to 1.00 times the harness's (0.91 to 1.00 on the three AMD models), maximum
  1.01 to 1.35. Longer blocks (b2, b5) reach at most 1.78 on single cells of the AMD models, and 2.58 (b2) and 4.03 (b5) on
  single cells of the Xeon 6973P-C. The Xeon median is below 1 because (b) keeps both sides of a repetition together,
  while the harness resamples each side separately; the A/A half-width of the Xeon 6973P-C falls from 0.41 % under (a) to
  0.32 % under (b).
- Lag-1 correction (d), the lower bound on trust: median width 1.01 to 1.08, maximum 1.22 to 1.44. Its first form (d0) shows
  maximum widths of 6.04 to 13.62 on four of the five models (1.97 on 9V45) and A/A half-widths of 2.70 % (Xeon 8573C) and
  5.09 % (Xeon 6973P-C); as in s4 and s5 that is the mean-versus-median artefact of the formula (see PLAN.md), listed so
  the first number is not hidden.
- Jobs only (c, c-t): median width 0.32 to 0.90 (c) and 0.49 to 1.01 (c-t); the largest single-cell widths are 1.55
  (c-t, Xeon 8573C) and 1.38 (c-t, Xeon 6973P-C).
- The lost-loop minimum is not close: the smallest lost-cell ci95_lo is 2.80 to 4.05 under every method and model, against
  the rule of 1.5. The largest counted forward ci95_hi on the three AMD models is 1.001 to 1.008 under every method (limit
  1.02).
- Classification changes against (a), in-cache cells (6 forward, 6 lost, 6 placement flags per model): no lost cell changes
  under any method on any model. Under (b): 0 forward, 0 lost and 0 placement changes on the four models other than the
  Xeon 6973P-C, and one forward change on the Xeon 6973P-C (stencil L2, below). Forward changes under the other methods:
  EPYC 9V45 1 of 6 under (c) and (c-t) (the left-out stencil L1 cell, below); Xeon 6973P-C 1 of 6 under (b2), (b5), (c),
  (c-t) and (d0). Placement-flag changes: Xeon 8573C 3 of 6 under (c) and 1 of 6 under (c-t); Xeon 6973P-C 1 of 6 under (c)
  and 2 of 6 under (d0); EPYC 9V74 1 of 6 under (d0); none under (a), (b), (b2), (b5) and (d) on any model.
- Where verdict forms move, with the reason:
  - EPYC 7763, 9V45 and 9V74: MAP under all eight methods (a, b, b2, b5, c, c-t, d, d0). On 9V45 the 30-job pool of s4 was
    INCONCLUSIVE under b2, d and d0; with 20 jobs it is MAP under every method. The same three cells (forward add at L1 and
    L2, stencil at L1) are placement-sensitive and left out of the forward rule under every method. The left-out stencil L1
    cell (aligned ratio 1.0156) has an aligned ci95_hi of 1.0203 under (a), 1.0221 under (b), 1.0208 under (d), 1.0176 under
    (c) and 1.0180 under (c-t), against the limit of 1.02; it does not enter the verdict under any of them.
  - Xeon Platinum 8573C (6 jobs): INCONCLUSIVE under (a), (b), (b2), (b5), (d) and (d0); MAP only under the two jobs-only
    methods (c) and (c-t). The forward rule fails under (a) on the forward add at L1, whose pooled aligned ratio is 1.0567
    (as compiled 1.0531) with an aligned ci95_hi of 1.0608, and these two ratios are the same under every method. Under (c)
    and (c-t) the interval of the placement statistic D (point value 0.9966) no longer covers 1, the cell is flagged
    placement-sensitive and leaves the forward set, so the rule is satisfied by the cells that remain. The cost of the
    cell does not change; its classification does. (Under (c) the stencil cells L1 and L2 are flagged as well.)
  - Xeon 6973P-C (6 jobs): INCONCLUSIVE under (a), (d) and (d0); MAP under (b), (b2), (b5), (c) and (c-t) (5 of the 7
    methods other than d0, 5 of 8 with it). The forward rule fails under (a) on one cell only, the stencil at L2: pooled
    aligned ratio 1.0000, aligned ci95_hi 1.0258 against the limit of 1.02. Its aligned ci95_hi is 1.0129 under (b), 1.0112
    under (b2), 1.0105 under (b5) and 1.0093 under (c-t); under (c) the cell is flagged placement-sensitive instead; under
    (d) it stays at 1.0252. The forward add at L1 (aligned 1.1992, as compiled 1.2301) and the stencil at L1 are
    placement-sensitive and left out of the forward rule under every method except (d0), where the A/A noise rule
    (half-width above 2 %) decides the form.

## Conclusion (s6)
Autocorrelation is again close to nil in the ratio series, the block bootstrap gives intervals of the same width or
narrower than the harness's (median 0.75 to 1.00), and every classification of the lost loops (smallest ci95_lo 2.80) and of
the counted forward loops on the three AMD models survives all methods. EPYC 7763, 9V45 and 9V74 keep the form MAP under all
eight methods; the fragility seen for 9V45 in the 30-job pool is not present in the 20-job pool. The two Xeon models (6 jobs
each) are different: their form depends on the interval method. For the Xeon 8573C the harness reading INCONCLUSIVE rests on
a forward add that costs 1.057x under every method, and the MAP under (c) and (c-t) comes from a placement flag, not from a
smaller cost. For the Xeon 6973P-C the harness reading INCONCLUSIVE rests on one forward cell near the limit (stencil at L2,
upper end 1.026 against 1.02); it becomes MAP under the block bootstrap and the jobs-only intervals and stays INCONCLUSIVE
under the lag-1 correction.
Under the rule fixed in PLAN.md: the median (b) width is below 1.5 times the harness's on every model, so the limits box
gets no added sentence; EPYC 7763, 9V45 and 9V74 keep their form under (b) and (c-t), so no change; the form of the Xeon
8573C changes under (c-t) only, which is reported here and not on the page; the form of the Xeon 6973P-C changes under (b)
and under (c-t) (from INCONCLUSIVE to MAP), which meets the condition of the second rule in the direction opposite to the
one it was written for. The harness readings stay the readings of record; this section is exploratory and changes no
threshold, no criteria file and no verdict. Not shown: independence at other time scales than the 40-repetition window,
anything about runs not stored, and an interval for 6 jobs better than the coarse percentiles and t values used here.

## Conclusion (s4 and s5)
The harness intervals are not visibly too narrow because of autocorrelation: its size is close to nil in these data, the
direct block bootstrap gives intervals of the same width (up to 15 % wider on single cells), and every classification and
every verdict form on EPYC 7763 and 9V74 survives all methods. EPYC 9V45 is fragile (already INCONCLUSIVE in the holdout
and borderline in s4), as the project already says. Under the rule fixed in PLAN.md: no verdict changes under (b) together
with (c-t), the median (b) width is below 1.5 times the harness's, so there is no page change; the 9V45 sensitivity to (b2)
and (d) is reported here only. The between-job spread, not repetition independence, is what limits these intervals. Not
shown: that the shared-VM noise has no autocorrelation at other time scales than the 40-repetition window (lag-1 and blocks
of up to 40 processes only), nor anything about runs not stored.

## Tables (generated by `python robustness/analyze.py --report`, recomputed by `python robustness/check.py`)

<!-- tables:begin -->
### Dataset s4

Self-test of (a) against the stored pooled.json: 396 of 396 stored numbers reproduced to within 1e-12 relative, largest relative difference below 1e-12, verdict forms equal.

Lag-1 autocorrelation of the per-repetition log ratio (every in-cache as-compiled series, 40 points; an independent series would average about -0.025):

| CPU model | jobs | series | median rho (ratio) | mean rho (ratio) | median rho (NONE time) | share rho>0.2 | median n_eff/n |
|---|---|---|---|---|---|---|---|
| AMD EPYC 7763 | 19 | 304 | -0.007 | 0.010 | -0.023 | 0.14 | 1.00 |
| AMD EPYC 9V45 | 5 | 80 | 0.031 | 0.036 | 0.120 | 0.12 | 0.94 |
| AMD EPYC 9V74 | 5 | 80 | -0.019 | -0.001 | 0.017 | 0.12 | 1.00 |

Changes against (a), in-cache cells. fwd = forward cells passing the forward rule (aligned column), lost = lost cells with ci95_lo >= 1.5 in both columns, ps = placement-sensitive flag; each shows flips/cells. Width = interval width over the width of (a), median and max over cells and both columns.

| CPU model | method | verdict form | fwd flips | lost flips | ps flips | width median | width max | A/A half-width % |
|---|---|---|---|---|---|---|---|---|
| AMD EPYC 7763 | (a) harness | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.10 |
| AMD EPYC 7763 | (b) block, 1 ABBA | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.13 | 0.10 |
| AMD EPYC 7763 | (b2) block, 2 ABBA | map | 0/6 | 0/6 | 0/6 | 0.99 | 1.09 | 0.10 |
| AMD EPYC 7763 | (b5) block, 5 ABBA | map | 0/6 | 0/6 | 0/6 | 0.97 | 1.61 | 0.10 |
| AMD EPYC 7763 | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 0/6 | 0.84 | 1.02 | 0.07 |
| AMD EPYC 7763 | (c-t) jobs only, t | map | 0/6 | 0/6 | 0/6 | 0.97 | 1.19 | 0.08 |
| AMD EPYC 7763 | (d) lag-1 n_eff | map | 0/6 | 0/6 | 0/6 | 1.05 | 1.37 | 0.10 |
| AMD EPYC 7763 | (d0) first form of (d) | map | 0/6 | 0/6 | 0/6 | 1.14 | 7.34 | 0.27 |
| AMD EPYC 9V45 | (a) harness | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.45 |
| AMD EPYC 9V45 | (b) block, 1 ABBA | map | 0/6 | 0/6 | 0/6 | 0.87 | 1.02 | 0.34 |
| AMD EPYC 9V45 | (b2) block, 2 ABBA | inconclusive | 0/6 | 0/6 | 1/6 | 0.88 | 1.07 | 0.35 |
| AMD EPYC 9V45 | (b5) block, 5 ABBA | map | 0/6 | 0/6 | 0/6 | 0.82 | 1.11 | 0.31 |
| AMD EPYC 9V45 | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 1/6 | 0.52 | 0.98 | 0.22 |
| AMD EPYC 9V45 | (c-t) jobs only, t | map | 0/6 | 0/6 | 0/6 | 0.82 | 1.62 | 0.35 |
| AMD EPYC 9V45 | (d) lag-1 n_eff | inconclusive | 0/6 | 0/6 | 1/6 | 1.07 | 1.29 | 0.45 |
| AMD EPYC 9V45 | (d0) first form of (d) | inconclusive | 0/6 | 0/6 | 1/6 | 1.17 | 2.22 | 0.65 |
| AMD EPYC 9V74 | (a) harness | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.14 |
| AMD EPYC 9V74 | (b) block, 1 ABBA | map | 0/6 | 0/6 | 0/6 | 0.98 | 1.07 | 0.15 |
| AMD EPYC 9V74 | (b2) block, 2 ABBA | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.50 | 0.14 |
| AMD EPYC 9V74 | (b5) block, 5 ABBA | map | 0/6 | 0/6 | 0/6 | 0.95 | 1.59 | 0.15 |
| AMD EPYC 9V74 | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 0/6 | 0.60 | 0.99 | 0.11 |
| AMD EPYC 9V74 | (c-t) jobs only, t | map | 0/6 | 0/6 | 0/6 | 0.98 | 1.67 | 0.18 |
| AMD EPYC 9V74 | (d) lag-1 n_eff | map | 0/6 | 0/6 | 0/6 | 1.02 | 1.13 | 0.18 |
| AMD EPYC 9V74 | (d0) first form of (d) | map | 0/6 | 0/6 | 1/6 | 1.46 | 10.78 | 0.63 |

Margins under each method: smallest lost-cell ci95_lo (rule: at least 1.5) and largest counted forward aligned ci95_hi (rule: at most the forward limit, 1 + max(2 %, 2 x A/A half-width)).

| CPU model | method | min lost ci95_lo | max forward ci95_hi | forward limit (x) |
|---|---|---|---|---|
| AMD EPYC 7763 | (a) harness | 3.176 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (b) block, 1 ABBA | 3.176 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (b2) block, 2 ABBA | 3.177 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (b5) block, 5 ABBA | 3.177 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (c) jobs only, bootstrap | 3.176 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (c-t) jobs only, t | 3.173 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (d) lag-1 n_eff | 3.174 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (d0) first form of (d) | 3.174 | 1.003 | 1.0200 |
| AMD EPYC 9V45 | (a) harness | 2.784 | 1.006 | 1.0200 |
| AMD EPYC 9V45 | (b) block, 1 ABBA | 2.784 | 1.005 | 1.0200 |
| AMD EPYC 9V45 | (b2) block, 2 ABBA | 2.784 | 1.024 | 1.0200 |
| AMD EPYC 9V45 | (b5) block, 5 ABBA | 2.782 | 1.005 | 1.0200 |
| AMD EPYC 9V45 | (c) jobs only, bootstrap | 2.792 | 1.002 | 1.0200 |
| AMD EPYC 9V45 | (c-t) jobs only, t | 2.788 | 1.005 | 1.0200 |
| AMD EPYC 9V45 | (d) lag-1 n_eff | 2.785 | 1.024 | 1.0200 |
| AMD EPYC 9V45 | (d0) first form of (d) | 2.784 | 1.031 | 1.0200 |
| AMD EPYC 9V74 | (a) harness | 4.049 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (b) block, 1 ABBA | 4.049 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (b2) block, 2 ABBA | 4.049 | 1.000 | 1.0200 |
| AMD EPYC 9V74 | (b5) block, 5 ABBA | 4.050 | 1.000 | 1.0200 |
| AMD EPYC 9V74 | (c) jobs only, bootstrap | 4.050 | 1.000 | 1.0200 |
| AMD EPYC 9V74 | (c-t) jobs only, t | 4.049 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (d) lag-1 n_eff | 4.050 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (d0) first form of (d) | 4.049 | 1.017 | 1.0200 |

### Dataset s5

Self-test of (a) against the stored pooled.json: 396 of 396 stored numbers reproduced to within 1e-12 relative, largest relative difference below 1e-12, verdict forms equal.

Lag-1 autocorrelation of the per-repetition log ratio (every in-cache as-compiled series, 40 points; an independent series would average about -0.025):

| CPU model | jobs | series | median rho (ratio) | mean rho (ratio) | median rho (NONE time) | share rho>0.2 | median n_eff/n |
|---|---|---|---|---|---|---|---|
| AMD EPYC 7763 | 19 | 304 | 0.014 | 0.029 | 0.040 | 0.14 | 0.97 |
| AMD EPYC 9V45 | 3 | 48 | 0.008 | 0.060 | 0.151 | 0.23 | 0.98 |
| AMD EPYC 9V74 | 6 | 96 | 0.032 | 0.041 | 0.024 | 0.17 | 0.94 |

Changes against (a), in-cache cells. fwd = forward cells passing the forward rule (aligned column), lost = lost cells with ci95_lo >= 1.5 in both columns, ps = placement-sensitive flag; each shows flips/cells. Width = interval width over the width of (a), median and max over cells and both columns.

| CPU model | method | verdict form | fwd flips | lost flips | ps flips | width median | width max | A/A half-width % |
|---|---|---|---|---|---|---|---|---|
| AMD EPYC 7763 | (a) harness | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.06 |
| AMD EPYC 7763 | (b) block, 1 ABBA | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.06 | 0.06 |
| AMD EPYC 7763 | (b2) block, 2 ABBA | map | 0/6 | 0/6 | 0/6 | 0.99 | 1.17 | 0.06 |
| AMD EPYC 7763 | (b5) block, 5 ABBA | map | 0/6 | 0/6 | 0/6 | 0.99 | 1.23 | 0.06 |
| AMD EPYC 7763 | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 0/6 | 0.82 | 1.02 | 0.05 |
| AMD EPYC 7763 | (c-t) jobs only, t | map | 0/6 | 0/6 | 0/6 | 0.90 | 1.31 | 0.05 |
| AMD EPYC 7763 | (d) lag-1 n_eff | map | 0/6 | 0/6 | 0/6 | 1.03 | 1.23 | 0.06 |
| AMD EPYC 7763 | (d0) first form of (d) | map | 0/6 | 0/6 | 0/6 | 1.04 | 5.58 | 0.17 |
| AMD EPYC 9V45 | (a) harness | inconclusive | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.50 |
| AMD EPYC 9V45 | (b) block, 1 ABBA | inconclusive | 0/6 | 0/6 | 0/6 | 0.88 | 1.03 | 0.47 |
| AMD EPYC 9V45 | (b2) block, 2 ABBA | inconclusive | 0/6 | 0/6 | 0/6 | 0.88 | 1.13 | 0.45 |
| AMD EPYC 9V45 | (b5) block, 5 ABBA | inconclusive | 0/6 | 0/6 | 0/6 | 0.82 | 1.16 | 0.42 |
| AMD EPYC 9V45 | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 1/6 | 0.61 | 0.97 | 0.29 |
| AMD EPYC 9V45 | (c-t) jobs only, t | inconclusive | 0/6 | 0/6 | 1/6 | 1.57 | 2.67 | 0.76 |
| AMD EPYC 9V45 | (d) lag-1 n_eff | inconclusive | 0/6 | 0/6 | 1/6 | 1.06 | 1.44 | 0.51 |
| AMD EPYC 9V45 | (d0) first form of (d) | inconclusive | 0/6 | 0/6 | 1/6 | 1.30 | 2.24 | 1.20 |
| AMD EPYC 9V74 | (a) harness | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.17 |
| AMD EPYC 9V74 | (b) block, 1 ABBA | map | 0/6 | 0/6 | 0/6 | 0.96 | 1.15 | 0.13 |
| AMD EPYC 9V74 | (b2) block, 2 ABBA | map | 0/6 | 0/6 | 0/6 | 0.99 | 1.24 | 0.13 |
| AMD EPYC 9V74 | (b5) block, 5 ABBA | map | 0/6 | 0/6 | 0/6 | 0.95 | 1.54 | 0.15 |
| AMD EPYC 9V74 | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 0/6 | 0.67 | 1.11 | 0.03 |
| AMD EPYC 9V74 | (c-t) jobs only, t | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.56 | 0.04 |
| AMD EPYC 9V74 | (d) lag-1 n_eff | map | 0/6 | 0/6 | 0/6 | 1.02 | 1.21 | 0.18 |
| AMD EPYC 9V74 | (d0) first form of (d) | map | 0/6 | 0/6 | 1/6 | 1.14 | 4.09 | 0.29 |

Margins under each method: smallest lost-cell ci95_lo (rule: at least 1.5) and largest counted forward aligned ci95_hi (rule: at most the forward limit, 1 + max(2 %, 2 x A/A half-width)).

| CPU model | method | min lost ci95_lo | max forward ci95_hi | forward limit (x) |
|---|---|---|---|---|
| AMD EPYC 7763 | (a) harness | 3.168 | 1.004 | 1.0200 |
| AMD EPYC 7763 | (b) block, 1 ABBA | 3.168 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (b2) block, 2 ABBA | 3.168 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (b5) block, 5 ABBA | 3.168 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (c) jobs only, bootstrap | 3.168 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (c-t) jobs only, t | 3.164 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (d) lag-1 n_eff | 3.165 | 1.004 | 1.0200 |
| AMD EPYC 7763 | (d0) first form of (d) | 3.165 | 1.004 | 1.0200 |
| AMD EPYC 9V45 | (a) harness | 2.793 | 1.028 | 1.0200 |
| AMD EPYC 9V45 | (b) block, 1 ABBA | 2.794 | 1.024 | 1.0200 |
| AMD EPYC 9V45 | (b2) block, 2 ABBA | 2.791 | 1.025 | 1.0200 |
| AMD EPYC 9V45 | (b5) block, 5 ABBA | 2.787 | 1.024 | 1.0200 |
| AMD EPYC 9V45 | (c) jobs only, bootstrap | 2.798 | 1.007 | 1.0200 |
| AMD EPYC 9V45 | (c-t) jobs only, t | 2.784 | 1.041 | 1.0200 |
| AMD EPYC 9V45 | (d) lag-1 n_eff | 2.793 | 1.027 | 1.0200 |
| AMD EPYC 9V45 | (d0) first form of (d) | 2.785 | 1.031 | 1.0240 |
| AMD EPYC 9V74 | (a) harness | 4.043 | 1.003 | 1.0200 |
| AMD EPYC 9V74 | (b) block, 1 ABBA | 4.044 | 1.003 | 1.0200 |
| AMD EPYC 9V74 | (b2) block, 2 ABBA | 4.044 | 1.003 | 1.0200 |
| AMD EPYC 9V74 | (b5) block, 5 ABBA | 4.046 | 1.003 | 1.0200 |
| AMD EPYC 9V74 | (c) jobs only, bootstrap | 4.046 | 1.002 | 1.0200 |
| AMD EPYC 9V74 | (c-t) jobs only, t | 4.044 | 1.003 | 1.0200 |
| AMD EPYC 9V74 | (d) lag-1 n_eff | 4.043 | 1.002 | 1.0200 |
| AMD EPYC 9V74 | (d0) first form of (d) | 4.039 | 1.015 | 1.0200 |

### Dataset s6

Self-test of (a) against the stored pooled.json: 495 of 495 stored numbers reproduced to within 1e-12 relative, largest relative difference below 1e-12, verdict forms equal.

Lag-1 autocorrelation of the per-repetition log ratio (every in-cache as-compiled series, 40 points; an independent series would average about -0.025):

| CPU model | jobs | series | median rho (ratio) | mean rho (ratio) | median rho (NONE time) | share rho>0.2 | median n_eff/n |
|---|---|---|---|---|---|---|---|
| AMD EPYC 7763 | 20 | 320 | -0.010 | -0.002 | -0.023 | 0.14 | 1.00 |
| AMD EPYC 9V45 | 20 | 320 | 0.048 | 0.073 | 0.161 | 0.21 | 0.91 |
| AMD EPYC 9V74 | 23 | 368 | 0.017 | 0.034 | 0.039 | 0.15 | 0.97 |
| Intel Xeon Platinum 8573C | 6 | 96 | 0.049 | 0.060 | 0.169 | 0.17 | 0.91 |
| Intel Xeon 6973P-C | 6 | 96 | 0.037 | 0.045 | 0.386 | 0.18 | 0.93 |

Changes against (a), in-cache cells. fwd = forward cells passing the forward rule (aligned column), lost = lost cells with ci95_lo >= 1.5 in both columns, ps = placement-sensitive flag; each shows flips/cells. Width = interval width over the width of (a), median and max over cells and both columns.

| CPU model | method | verdict form | fwd flips | lost flips | ps flips | width median | width max | A/A half-width % |
|---|---|---|---|---|---|---|---|---|
| AMD EPYC 7763 | (a) harness | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.09 |
| AMD EPYC 7763 | (b) block, 1 ABBA | map | 0/6 | 0/6 | 0/6 | 0.98 | 1.04 | 0.10 |
| AMD EPYC 7763 | (b2) block, 2 ABBA | map | 0/6 | 0/6 | 0/6 | 0.99 | 1.09 | 0.09 |
| AMD EPYC 7763 | (b5) block, 5 ABBA | map | 0/6 | 0/6 | 0/6 | 0.98 | 1.44 | 0.09 |
| AMD EPYC 7763 | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 0/6 | 0.90 | 1.11 | 0.07 |
| AMD EPYC 7763 | (c-t) jobs only, t | map | 0/6 | 0/6 | 0/6 | 1.01 | 1.20 | 0.07 |
| AMD EPYC 7763 | (d) lag-1 n_eff | map | 0/6 | 0/6 | 0/6 | 1.04 | 1.37 | 0.10 |
| AMD EPYC 7763 | (d0) first form of (d) | map | 0/6 | 0/6 | 0/6 | 1.04 | 6.80 | 0.27 |
| AMD EPYC 9V45 | (a) harness | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.22 |
| AMD EPYC 9V45 | (b) block, 1 ABBA | map | 0/6 | 0/6 | 0/6 | 0.91 | 1.19 | 0.18 |
| AMD EPYC 9V45 | (b2) block, 2 ABBA | map | 0/6 | 0/6 | 0/6 | 0.92 | 1.24 | 0.19 |
| AMD EPYC 9V45 | (b5) block, 5 ABBA | map | 0/6 | 0/6 | 0/6 | 0.89 | 1.78 | 0.17 |
| AMD EPYC 9V45 | (c) jobs only, bootstrap | map | 1/6 | 0/6 | 0/6 | 0.63 | 0.95 | 0.11 |
| AMD EPYC 9V45 | (c-t) jobs only, t | map | 1/6 | 0/6 | 0/6 | 0.69 | 1.03 | 0.12 |
| AMD EPYC 9V45 | (d) lag-1 n_eff | map | 0/6 | 0/6 | 0/6 | 1.08 | 1.44 | 0.27 |
| AMD EPYC 9V45 | (d0) first form of (d) | map | 0/6 | 0/6 | 0/6 | 1.15 | 1.97 | 0.42 |
| AMD EPYC 9V74 | (a) harness | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.07 |
| AMD EPYC 9V74 | (b) block, 1 ABBA | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.08 | 0.06 |
| AMD EPYC 9V74 | (b2) block, 2 ABBA | map | 0/6 | 0/6 | 0/6 | 1.00 | 1.17 | 0.07 |
| AMD EPYC 9V74 | (b5) block, 5 ABBA | map | 0/6 | 0/6 | 0/6 | 0.97 | 1.19 | 0.06 |
| AMD EPYC 9V74 | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 0/6 | 0.77 | 1.00 | 0.03 |
| AMD EPYC 9V74 | (c-t) jobs only, t | map | 0/6 | 0/6 | 0/6 | 0.83 | 1.12 | 0.03 |
| AMD EPYC 9V74 | (d) lag-1 n_eff | map | 0/6 | 0/6 | 0/6 | 1.05 | 1.24 | 0.08 |
| AMD EPYC 9V74 | (d0) first form of (d) | map | 0/6 | 0/6 | 1/6 | 1.97 | 6.04 | 0.17 |
| Intel Xeon Platinum 8573C | (a) harness | inconclusive | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.63 |
| Intel Xeon Platinum 8573C | (b) block, 1 ABBA | inconclusive | 0/6 | 0/6 | 0/6 | 0.94 | 1.01 | 0.63 |
| Intel Xeon Platinum 8573C | (b2) block, 2 ABBA | inconclusive | 0/6 | 0/6 | 0/6 | 0.92 | 1.08 | 0.60 |
| Intel Xeon Platinum 8573C | (b5) block, 5 ABBA | inconclusive | 0/6 | 0/6 | 0/6 | 0.91 | 1.17 | 0.59 |
| Intel Xeon Platinum 8573C | (c) jobs only, bootstrap | map | 0/6 | 0/6 | 3/6 | 0.61 | 1.01 | 0.38 |
| Intel Xeon Platinum 8573C | (c-t) jobs only, t | map | 0/6 | 0/6 | 1/6 | 0.88 | 1.55 | 0.57 |
| Intel Xeon Platinum 8573C | (d) lag-1 n_eff | inconclusive | 0/6 | 0/6 | 0/6 | 1.02 | 1.23 | 0.64 |
| Intel Xeon Platinum 8573C | (d0) first form of (d) | inconclusive | 0/6 | 0/6 | 0/6 | 1.05 | 8.31 | 2.70 |
| Intel Xeon 6973P-C | (a) harness | inconclusive | 0/6 | 0/6 | 0/6 | 1.00 | 1.00 | 0.41 |
| Intel Xeon 6973P-C | (b) block, 1 ABBA | map | 1/6 | 0/6 | 0/6 | 0.75 | 1.35 | 0.32 |
| Intel Xeon 6973P-C | (b2) block, 2 ABBA | map | 1/6 | 0/6 | 0/6 | 0.76 | 2.58 | 0.42 |
| Intel Xeon 6973P-C | (b5) block, 5 ABBA | map | 1/6 | 0/6 | 0/6 | 0.72 | 4.03 | 0.34 |
| Intel Xeon 6973P-C | (c) jobs only, bootstrap | map | 1/6 | 0/6 | 1/6 | 0.32 | 1.03 | 0.25 |
| Intel Xeon 6973P-C | (c-t) jobs only, t | map | 1/6 | 0/6 | 0/6 | 0.49 | 1.38 | 0.36 |
| Intel Xeon 6973P-C | (d) lag-1 n_eff | inconclusive | 0/6 | 0/6 | 0/6 | 1.01 | 1.22 | 0.55 |
| Intel Xeon 6973P-C | (d0) first form of (d) | inconclusive | 1/6 | 0/6 | 2/6 | 1.01 | 13.62 | 5.09 |

Margins under each method: smallest lost-cell ci95_lo (rule: at least 1.5) and largest counted forward aligned ci95_hi (rule: at most the forward limit, 1 + max(2 %, 2 x A/A half-width)).

| CPU model | method | min lost ci95_lo | max forward ci95_hi | forward limit (x) |
|---|---|---|---|---|
| AMD EPYC 7763 | (a) harness | 3.179 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (b) block, 1 ABBA | 3.179 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (b2) block, 2 ABBA | 3.179 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (b5) block, 5 ABBA | 3.179 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (c) jobs only, bootstrap | 3.180 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (c-t) jobs only, t | 3.176 | 1.002 | 1.0200 |
| AMD EPYC 7763 | (d) lag-1 n_eff | 3.177 | 1.003 | 1.0200 |
| AMD EPYC 7763 | (d0) first form of (d) | 3.177 | 1.003 | 1.0200 |
| AMD EPYC 9V45 | (a) harness | 2.798 | 1.005 | 1.0200 |
| AMD EPYC 9V45 | (b) block, 1 ABBA | 2.799 | 1.004 | 1.0200 |
| AMD EPYC 9V45 | (b2) block, 2 ABBA | 2.799 | 1.005 | 1.0200 |
| AMD EPYC 9V45 | (b5) block, 5 ABBA | 2.799 | 1.005 | 1.0200 |
| AMD EPYC 9V45 | (c) jobs only, bootstrap | 2.801 | 1.003 | 1.0200 |
| AMD EPYC 9V45 | (c-t) jobs only, t | 2.801 | 1.003 | 1.0200 |
| AMD EPYC 9V45 | (d) lag-1 n_eff | 2.797 | 1.005 | 1.0200 |
| AMD EPYC 9V45 | (d0) first form of (d) | 2.797 | 1.006 | 1.0200 |
| AMD EPYC 9V74 | (a) harness | 4.051 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (b) block, 1 ABBA | 4.051 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (b2) block, 2 ABBA | 4.051 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (b5) block, 5 ABBA | 4.051 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (c) jobs only, bootstrap | 4.052 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (c-t) jobs only, t | 4.052 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (d) lag-1 n_eff | 4.051 | 1.001 | 1.0200 |
| AMD EPYC 9V74 | (d0) first form of (d) | 4.050 | 1.008 | 1.0200 |
| Intel Xeon Platinum 8573C | (a) harness | 3.110 | 1.061 | 1.0200 |
| Intel Xeon Platinum 8573C | (b) block, 1 ABBA | 3.113 | 1.060 | 1.0200 |
| Intel Xeon Platinum 8573C | (b2) block, 2 ABBA | 3.111 | 1.061 | 1.0200 |
| Intel Xeon Platinum 8573C | (b5) block, 5 ABBA | 3.113 | 1.061 | 1.0200 |
| Intel Xeon Platinum 8573C | (c) jobs only, bootstrap | 3.118 | 1.014 | 1.0200 |
| Intel Xeon Platinum 8573C | (c-t) jobs only, t | 3.102 | 1.018 | 1.0200 |
| Intel Xeon Platinum 8573C | (d) lag-1 n_eff | 3.104 | 1.061 | 1.0200 |
| Intel Xeon Platinum 8573C | (d0) first form of (d) | 3.104 | 1.093 | 1.0541 |
| Intel Xeon 6973P-C | (a) harness | 3.228 | 1.026 | 1.0200 |
| Intel Xeon 6973P-C | (b) block, 1 ABBA | 3.268 | 1.017 | 1.0200 |
| Intel Xeon 6973P-C | (b2) block, 2 ABBA | 3.265 | 1.014 | 1.0200 |
| Intel Xeon 6973P-C | (b5) block, 5 ABBA | 3.266 | 1.014 | 1.0200 |
| Intel Xeon 6973P-C | (c) jobs only, bootstrap | 3.274 | 1.003 | 1.0200 |
| Intel Xeon 6973P-C | (c-t) jobs only, t | 3.271 | 1.009 | 1.0200 |
| Intel Xeon 6973P-C | (d) lag-1 n_eff | 3.223 | 1.025 | 1.0200 |
| Intel Xeon 6973P-C | (d0) first form of (d) | 3.223 | 1.247 | 1.1018 |

<!-- tables:end -->
