# Calibration baseline for "intervals understate run-to-run spread"

`README.md`, the details page and `site/app.js` said that the pooled intervals understate run-to-run spread, and cited a count; they have since been reworded to what this note supports. The count is how often one run's pooled point falls outside another run's pooled 95% interval: on EPYC 7763, 168 of 640 comparisons; on EPYC 9V74, 62 of 384 (in the 75-job pool, 32 of 192 and 28 of 192). A count like that needs a baseline. Even intervals that are exactly right put one run's point outside another run's interval fairly often, because two noisy estimates differ by more than one interval's half-width quite regularly. This note computes the baseline from the stored files and says, model by model, what the data support. Nothing under `results/` and no verdict is changed.

Files: `calibration.py` (`--full` recomputes everything in about 20 minutes and writes `calibration.json`; `--verify` recomputes the cheap parts and fails on any difference, about a minute; with no flag it prints Tables 1 to 6 from the stored file), `calibration.json` (sorted keys, the sha256 of every input, the seed tag) and `../tests/test_calibration.py`.

## What was computed

- A. The recount: every ordered pair of different runs of one CPU model that have a verdict form (at least 3 jobs of the model in each), every in-cache cell, both columns (as compiled and aligned). A comparison is outside when run A's pooled point is not between run B's interval ends. The counts are the ones `harness/pool.py` stores as `reproduction`; the script recounts them and the test recounts them again in a second loop.
- B. The expected count if the intervals were exactly calibrated, and its 95% range (below).
- C. The same for the replication comparisons of `replication/results.json` (new pooled point against the earlier pool's interval, 32 points per model).
- D. For each model and in-cache cell, the spread of the per-job ratios between jobs against the within-job standard error, and a one-way analysis of variance by run.
- E. A job-shuffling null: the jobs of the assessed runs of one model are redistributed over the runs (same run sizes), the pooled points and intervals are recomputed with the unchanged pooling code, and the outside count is taken again (60 shuffles for EPYC 7763 and 9V74; the smallest p-value it can give is 1/61).
- F. The verdict word of random subsets of one model's jobs (30 subsets, or all of them when there are 30 or fewer) at 3, 5 and 10 jobs, through the unchanged `pool.analyse_cpu`.

## The model of "calibrated"

Each pooled estimate (one run, one cell, one column) is treated as the true value plus a normal error in the log of the ratio, with standard deviation s equal to its stated half-width over 1.96 (half the log distance between the interval ends over 1.96). The difference of two runs' points then has standard deviation sqrt(s_A squared plus s_B squared). Run A's point is outside run B's interval when that difference is further below zero than B's lower offset, or further above zero than B's upper offset; the two tails are added. This is the exact event the README counts and it has a closed form ("expected, stored offsets" in Table 1, using each interval's own, asymmetric offsets; "expected, symmetric" replaces them with plus and minus 1.96 s_B). The pair z (the difference over sqrt(s_A squared plus s_B squared)) is a different, symmetric test: for calibrated intervals 5% of the z values are above 1.96 in size and their root mean square is 1.

The 95% ranges come from 2000 simulated draws with a fixed generator, in two forms. "Independent" draws a fresh error for every run, cell and column; "one draw per run" gives all cells of a run the same normal error, which is the most dependent case and gives a very wide range, so it is a weak test. The truth lies between: cells of one run share jobs, and the comparisons share runs, so the 640 comparisons are not 640 independent chances.

## What the data support

- **The counts reproduce.** 168 of 640 on EPYC 7763 and 62 of 384 on EPYC 9V74 are recounted exactly (32 of 192 and 28 of 192 in the 75-job pool).
- **EPYC 7763: a modest excess, found in the loops that lose vectorisation.** There were 168 of 640 comparisons (26.2%) outside against 148.4 expected (23.2%). The independent 95% range is 115 to 183, and 14.2% of simulated calibrated draws reach 168 or more, so the count by itself does not separate the intervals from calibrated ones. The pair z gives rms 1.13 (differences between runs about 13% larger than the stated intervals imply), and 6.2% of the z values are above 1.96 in size, against 5% for calibrated intervals. When the jobs of the five runs are shuffled over runs, the outside count has mean 127.1 (91 to 168) and 1 of 60 shuffles reached 168, so the run a job came from carries some information. By loop family (Table 6) the excess sits in reverse, stride-2 and matrix multiply: 104 of 240 outside against 61.7 expected, while the forward loops show 42 of 240 against 53.8, fewer than expected. Adding the four later runs of set C (nine runs, 2304 comparisons) gives 537 outside against 540.4 expected overall, and the same split: 361 of 864 against 226.8 in reverse, stride-2 and matrix multiply, 111 of 864 against 196.7 in the forward loops. In the replication comparison (new pool of 19 jobs against the earlier pool of 29) 10 of 32 points were outside against 5.1 expected; that is above the independent range (1 to 9) and inside the one-draw-per-pool range (0 to 31).
- **EPYC 9V74: not supported.** There were 62 of 384 (16.1%) outside against 88.4 expected (23.0%); 1.6% of calibrated draws are as low (independent), the pair z has rms 0.92, and every loop family is at or below its expected count (forward 22 of 144 against 33.2, reverse, stride-2 and matrix multiply 32 of 144 against 33.6). The shuffle null has mean 72.4, and 51 of 60 shuffles reached 62 or more. The pooled intervals are as wide as the run-to-run differences need, or wider.
- **Neoverse-N2 (Arm): not supported overall; supported for stride-2 at L2.** There were 13 of 192 outside against 34.7 expected in the first Arm pool (three runs) and 101 of 960 against 177.7 in the six runs of sets A and B together (pair z rms 0.86). The exception is stride-2 at L2: 28 of 60 comparisons outside against 11.5 expected in the six runs, which is where `arm64/README.md` says the intervals understate the spread between runs. The count is smaller than expected in the forward loops (20 of 360 against 67.1).
- **EPYC 9V45.** The two assessable runs (3 and 4 jobs) of the nine-run pool give 8 of 64 against 14.7 expected: too little to support or refute the claim.
- **Xeon 8573C and 6973P-C.** Neither model has two runs with 3 or more jobs in any of the pools, so there is no run-to-run count. The replication comparison of the 8573C (7 jobs against 7) gives 5 of 32 against 3.9 expected, within the independent range (1 to 8); the 6973P-C has one job in set C and cannot be compared.
- **Replication in total.** 27 of 128 points outside on x86-64 against 27.4 expected, 6 of 32 on Arm against 5.9: the stored replication agreement is what calibrated intervals would give, and EPYC 7763 is the one model above the independent 95% range.

Job-to-job spread (Table 4). A single job's own 95% interval is much narrower than the spread of the per-job ratios between jobs for some cells (matrix multiply at L1 on EPYC 7763: 1.28% between jobs against 0.20% within a job, 6.4 times; at L2 on EPYC 9V74: 0.94% against 0.04%, 26.8 times). That is the reason the pooled interval resamples jobs; it says that within-job intervals alone would understate the spread between jobs, not that the pooled intervals do. The analysis of variance by run finds a run effect (permutation p below 0.05) in 2 of 32 rows for EPYC 7763 and 2 of 32 for EPYC 9V74, about the 1.6 rows expected by chance: jobs of one run are, in most cells, not more alike than jobs of different runs.

Few jobs (Table 5). The verdict word of a subset of one model's jobs: EPYC 7763 and 9V74 give MAP in all 30 subsets even at 3 jobs. EPYC 9V45 gives INCONCLUSIVE in 14 of 30 subsets at 3 jobs and 11 of 30 at 5, and MAP in all 30 at 10. The Xeon 6973P-C, MAP with its 7 jobs, gives INCONCLUSIVE in 27 of 30 subsets at 3 jobs and 19 of 21 (all of them) at 5. The Xeon 8573C gives INCONCLUSIVE in every subset. So "a word can change with the jobs drawn" is supported for 9V45 and the 6973P-C at 5 jobs or fewer, and not for 7763 or 9V74.

## What this does not show

- It does not explain why EPYC 7763's reverse, stride-2 and matrix multiply cells are wider between runs than their intervals say; a mechanism (host mix, code placement of the lost loops) was not tested.
- The normal model is an approximation on the log of the ratio, and the intervals come from a percentile bootstrap. The stored offsets carry the asymmetry; the tails are not modelled.
- Table 6 groups the cells in three families that were chosen with the per-cell counts in view. Cell counts are not tested against simulated ranges, and comparisons share runs.
- Fewer than two runs of 3 or more jobs cannot be compared with each other, so the thin models stay untested here.
- Sixty shuffles is a coarse null (smallest p-value 1/61); a longer run would change only that resolution.

## Tables (generated by `calibration.py` from `calibration.json`; a test compares this block with the script's output)

<!-- tables:begin -->
Table 1. Run-to-run counts (a run's pooled point outside another run's pooled 95% interval, in-cache cells, both columns) against the count that perfectly calibrated intervals would give.

| pool | model | jobs per assessed run | outside / compared | observed | expected, stored offsets | expected, symmetric | 95% range, independent | 95% range, one draw per run | pair z share above 1.96 | rms z |
|---|---|---|---|---|---|---|---|---|---|---|
| s4 | 7763 | 7+6+6 | 32 / 192 | 16.7% | 22.4% (43.0) | 20.8% | 28 to 59 | 1 to 126 | 2.1% | 0.84 |
| s6 | 7763 | 7+6+6 | 32 / 192 | 16.7% | 22.4% (43.0) | 20.8% | 29 to 58 | 0 to 123 | 2.1% | 0.84 |
| s6 | 9V74 | 3+3+5 | 28 / 192 | 14.6% | 21.6% (41.4) | 20.0% | 27 to 58 | 0 to 125 | 5.2% | 0.96 |
| s7 | 7763 | 7+6+6+5+4 | 168 / 640 | 26.2% | 23.2% (148.4) | 21.7% | 115 to 183 | 22 to 335 | 6.2% | 1.13 |
| s7 | 9V74 | 3+3+5+3 | 62 / 384 | 16.1% | 23.0% (88.4) | 21.4% | 65 to 112 | 7 to 217 | 3.6% | 0.92 |
| s8-arm | Neoverse-N2 | 10+10+10 | 13 / 192 | 6.8% | 18.1% (34.7) | 17.3% | 20 to 52 | 0 to 128 | 5.2% | 0.83 |
| s9-arm-b | Neoverse-N2 | 10+9+10 | 20 / 192 | 10.4% | 18.6% (35.7) | 17.8% | 20 to 52 | 0 to 127 | 1.0% | 0.86 |
| s9-arm-ab | Neoverse-N2 | 10+10+10+10+9+10 | 101 / 960 | 10.5% | 18.5% (177.7) | 17.8% | 130 to 226 | 2 to 466 | 3.1% | 0.86 |
| s9-x86-c | 7763 | 5+4+4+6 | 59 / 384 | 15.4% | 23.9% (91.8) | 21.9% | 69 to 116 | 10 to 218 | 0.0% | 0.81 |
| s9-x86-ac | 7763 | 7+6+6+5+4+5+4+4+6 | 537 / 2304 | 23.3% | 23.5% (540.4) | 21.7% | 456 to 626 | 155 to 1000 | 5.6% | 1.04 |
| s9-x86-ac | 9V45 | 3+4 | 8 / 64 | 12.5% | 23.0% (14.7) | 22.4% | 8 to 22 | 0 to 64 | 0.0% | 0.75 |
| s9-x86-ac | 9V74 | 3+3+5+3+3 | 105 / 640 | 16.4% | 22.5% (144.1) | 20.9% | 109 to 181 | 18 to 331 | 4.4% | 0.94 |

Table 2. Replication sets: the new pooled point outside the earlier pool's interval, observed against expected.

| architecture | model | jobs (earlier, new) | outside / compared | expected outside | 95% range, independent | 95% range, one draw per pool | pair z share above 1.96 | rms z |
|---|---|---|---|---|---|---|---|---|
| arm | Neoverse-N2 | 30, 29 | 6 / 32 | 5.9 | 2 to 10 | 0 to 32 | 3.1% | 0.95 |
| arm | all testable models | | 6 / 32 | 5.9 | 2 to 10 | 0 to 32 | | |
| x86 | 7763 | 29, 19 | 10 / 32 | 5.1 | 1 to 9 | 0 to 31 | 9.4% | 1.29 |
| x86 | 9V45 | 23, 5 | 5 / 32 | 8.6 | 4 to 13 | 0 to 32 | 0.0% | 0.74 |
| x86 | 9V74 | 28, 7 | 7 / 32 | 9.8 | 5 to 15 | 0 to 31 | 3.1% | 0.84 |
| x86 | 8573C | 7, 7 | 5 / 32 | 3.9 | 1 to 8 | 0 to 30 | 0.0% | 0.99 |
| x86 | all testable models | | 27 / 128 | 27.4 | 19 to 36 | 0 to 69 | | |

Table 3. Shuffling jobs over runs (same run sizes, 95-job pool): the outside count when jobs carry no run label.

| model | assessed runs (jobs) | observed outside | shuffles | mean | min to max | shuffles at or above observed | mean expected under the calibrated normal | mean rms z |
|---|---|---|---|---|---|---|---|---|
| 7763 | 7+6+6+5+4 | 168 | 60 | 127.1 | 91 to 168 | 1 of 60 | 148.0 | 0.96 |
| 9V74 | 3+3+5+3 | 62 | 60 | 72.4 | 50 to 102 | 51 of 60 | 87.7 | 0.97 |

Table 4. Job-to-job spread against the within-job standard error, 95-job pool, as-compiled column, selected in-cache cells (sd of the log ratio over all the model's jobs, in percent; within-job SE is the root mean square of each job's own ci95 half-width over 1.96).

| model | cell | jobs | sd between jobs | within-job SE | sd over SE | between-run sd | F | permutation p |
|---|---|---|---|---|---|---|---|---|
| 7763 | k01_sum_fwd.L2 | 29 | 0.12% | 0.17% | 0.7 | 0.00% | 0.57 | 0.679 |
| 7763 | k04_rev.L2 | 29 | 2.44% | 0.91% | 2.7 | 0.00% | 0.96 | 0.453 |
| 7763 | k05_stride2.L2 | 29 | 1.91% | 0.67% | 2.9 | 0.00% | 0.94 | 0.457 |
| 7763 | k06_gather.L2 | 29 | 0.59% | 0.16% | 3.7 | 0.02% | 1.01 | 0.439 |
| 7763 | k08_matmul.L1 | 29 | 1.28% | 0.20% | 6.4 | 0.00% | 0.78 | 0.571 |
| 7763 | k08_matmul.L2 | 29 | 1.06% | 0.17% | 6.2 | 0.14% | 1.15 | 0.348 |
| 9V45 | k01_sum_fwd.L2 | 23 | 0.26% | 0.43% | 0.6 | n/a | n/a | n/a |
| 9V45 | k04_rev.L2 | 23 | 0.95% | 0.58% | 1.6 | n/a | n/a | n/a |
| 9V45 | k05_stride2.L2 | 23 | 0.54% | 0.53% | 1.0 | n/a | n/a | n/a |
| 9V45 | k06_gather.L2 | 23 | 0.39% | 0.42% | 0.9 | n/a | n/a | n/a |
| 9V45 | k08_matmul.L1 | 23 | 1.24% | 0.54% | 2.3 | n/a | n/a | n/a |
| 9V45 | k08_matmul.L2 | 23 | 0.73% | 0.52% | 1.4 | n/a | n/a | n/a |
| 9V74 | k01_sum_fwd.L2 | 28 | 0.15% | 0.08% | 2.0 | 0.08% | 1.56 | 0.286 |
| 9V74 | k04_rev.L2 | 28 | 1.49% | 0.64% | 2.3 | 0.00% | 0.62 | 0.656 |
| 9V74 | k05_stride2.L2 | 28 | 2.55% | 0.73% | 3.5 | 0.85% | 1.25 | 0.343 |
| 9V74 | k06_gather.L2 | 28 | 0.12% | 0.08% | 1.5 | 0.08% | 5.72 | 0.019 |
| 9V74 | k08_matmul.L1 | 28 | 0.04% | 0.05% | 0.8 | 0.01% | 1.16 | 0.382 |
| 9V74 | k08_matmul.L2 | 28 | 0.94% | 0.04% | 26.8 | 0.26% | 1.43 | 0.090 |
| 8573C | k01_sum_fwd.L2 | 7 | 1.18% | 0.63% | 1.9 | n/a | n/a | n/a |
| 8573C | k04_rev.L2 | 7 | 0.53% | 0.48% | 1.1 | n/a | n/a | n/a |
| 8573C | k05_stride2.L2 | 7 | 3.10% | 1.17% | 2.6 | n/a | n/a | n/a |
| 8573C | k06_gather.L2 | 7 | 0.34% | 0.61% | 0.6 | n/a | n/a | n/a |
| 8573C | k08_matmul.L1 | 7 | 0.62% | 0.39% | 1.6 | n/a | n/a | n/a |
| 8573C | k08_matmul.L2 | 7 | 0.75% | 0.64% | 1.2 | n/a | n/a | n/a |
| 6973P-C | k01_sum_fwd.L2 | 7 | 0.13% | 0.69% | 0.2 | n/a | n/a | n/a |
| 6973P-C | k04_rev.L2 | 7 | 1.41% | 2.67% | 0.5 | n/a | n/a | n/a |
| 6973P-C | k05_stride2.L2 | 7 | 0.50% | 1.61% | 0.3 | n/a | n/a | n/a |
| 6973P-C | k06_gather.L2 | 7 | 0.48% | 2.46% | 0.2 | n/a | n/a | n/a |
| 6973P-C | k08_matmul.L1 | 7 | 0.25% | 0.55% | 0.4 | n/a | n/a | n/a |
| 6973P-C | k08_matmul.L2 | 7 | 0.29% | 1.83% | 0.2 | n/a | n/a | n/a |

Table 5. Verdict word of random job subsets of one CPU model (the unchanged pooling code, 30 subsets, or all of them when there are 30 or fewer).

| model | jobs | word with all jobs | J | subsets | words |
|---|---|---|---|---|---|
| 7763 | 29 | map | 3 | 30 | 30 map |
| 7763 | 29 | map | 5 | 30 | 30 map |
| 7763 | 29 | map | 10 | 30 | 30 map |
| 9V45 | 23 | map | 3 | 30 | 14 inconclusive, 16 map |
| 9V45 | 23 | map | 5 | 30 | 11 inconclusive, 19 map |
| 9V45 | 23 | map | 10 | 30 | 30 map |
| 9V74 | 28 | map | 3 | 30 | 30 map |
| 9V74 | 28 | map | 5 | 30 | 30 map |
| 9V74 | 28 | map | 10 | 30 | 30 map |
| 8573C | 7 | inconclusive | 3 | 30 | 30 inconclusive |
| 8573C | 7 | inconclusive | 5 | 21 (all) | 21 inconclusive |
| 8573C | 7 | inconclusive | 10 | not run | model has 7 jobs |
| 6973P-C | 7 | map | 3 | 30 | 27 inconclusive, 3 map |
| 6973P-C | 7 | map | 5 | 21 (all) | 19 inconclusive, 2 map |
| 6973P-C | 7 | map | 10 | not run | model has 7 jobs |

Table 6. The run-to-run counts of Table 1 split by loop family (sums of the stored per-cell counts; the three groups were chosen after the per-cell counts had been read). Each entry: outside / compared (expected outside).

| pool | model | forward loops (k01, k02, k03) | reverse, stride-2, matrix multiply (k04, k05, k08) | gather, histogram (k06, k07) |
|---|---|---|---|---|
| s4 | 7763 | 10 / 72 (15.6) | 13 / 72 (17.6) | 9 / 48 (9.8) |
| s6 | 7763 | 10 / 72 (15.6) | 13 / 72 (17.6) | 9 / 48 (9.8) |
| s6 | 9V74 | 12 / 72 (16.8) | 10 / 72 (13.9) | 6 / 48 (10.7) |
| s7 | 7763 | 42 / 240 (53.8) | 104 / 240 (61.7) | 22 / 160 (32.9) |
| s7 | 9V74 | 22 / 144 (33.2) | 32 / 144 (33.6) | 8 / 96 (21.6) |
| s8-arm | Neoverse-N2 | 0 / 72 (12.9) | 12 / 72 (13.0) | 1 / 48 (8.8) |
| s9-arm-b | Neoverse-N2 | 5 / 72 (13.8) | 12 / 72 (12.9) | 3 / 48 (9.0) |
| s9-arm-ab | Neoverse-N2 | 20 / 360 (67.1) | 66 / 360 (65.3) | 15 / 240 (45.3) |
| s9-x86-c | 7763 | 8 / 144 (33.0) | 42 / 144 (39.9) | 9 / 96 (18.9) |
| s9-x86-ac | 7763 | 111 / 864 (196.7) | 361 / 864 (226.8) | 65 / 576 (116.9) |
| s9-x86-ac | 9V45 | 2 / 24 (5.3) | 3 / 24 (5.2) | 3 / 16 (4.2) |
| s9-x86-ac | 9V74 | 34 / 240 (54.8) | 57 / 240 (54.1) | 14 / 160 (35.2) |
<!-- tables:end -->
