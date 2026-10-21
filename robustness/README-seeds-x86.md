# Seed sensitivity of the x86-64 verdicts

The pooled x86-64 verdicts (`results/s7-pooled/pooled.json`, 95 jobs) come from a bootstrap that ran under one stored random seed. This note re-draws the interval ends that lie close to a rule's line under other seeds, with the same data, the same code and the same number of resamples, and reports how far the ends move and whether a verdict word depends on the draw. It is a sensitivity reading beside the stored verdicts. It changes no rule, no threshold, no seed and no resample count, and the stored words stay as they are.

The Arm pool has the same reading in `arm64/seeds.py`; this is its x86-64 counterpart and uses the same method. The files:

- `robustness/seeds_x86.py` runs it (`--verify` recomputes a sample and compares it with the stored file, `--full` regenerates the file, `--tables` prints the tables below from the stored file).
- `robustness/seed-sensitivity-x86.json` is the stored result, with the hash of the pool file it reads.
- `tests/test_seeds_x86.py` recomputes what the file derives from its own lists, rebuilds one cell from the jobs' samples, and checks the tables on this page against the file.

## What was run

- Which cells. In every model with at least 3 jobs, every in-cache kept cell whose deciding interval end lies within 0.01 of its line. The forward rule's line is the forward limit (1.02 for every model here); a cell is also taken when it is a candidate for the placement exemption (its hot loops sit differently in the two builds, its aligned reading is at or above the limit minus 0.01, or its point ratio is above the maximum) and the interval of its placement statistic D has an end within 0.01 of 1. The rule is written out in the header of `robustness/seeds_x86.py`. Three models have such a cell: EPYC 9V45 (23 jobs), Xeon 8573C (7 jobs) and Xeon 6973P-C (7 jobs). EPYC 7763 (29 jobs) and EPYC 9V74 (28 jobs) have no cell within 0.01 of a line and were not re-drawn; the Xeon 8370C has 1 job, below the minimum of 3, and gets no verdict.
- Single cells. 400 other seeds (`seedsens-001` to `seedsens-400`), each a full 2000-resample bootstrap with the pool's own function from `harness/pool.py`.
- A converged reading. 100,000 draws (50 independent streams of 2000, under the stored seed prefix) give where the interval end lies when the draw no longer matters; its Monte Carlo sd is the spread over the streams divided by the square root of 50.
- Whole analyses. For each of the three models, the complete analysis (every cell, every rule, the A/A control, the placement exemption) under the first 60 of the other seeds, with the share of each verdict word.
- A reproduction check. The stored seed's own numbers were rebuilt first: 36 numbers matched exactly.

## Forward cells

The interval end is the upper end of the aligned ratio's 95 % interval. "Stored verdict" says whether the cell is judged by the forward rule or left out of it as placement-sensitive.

| Model (jobs) | Cell | Stored verdict | Stored end | Rank of the stored end among the 400 (%) | Median of the 400 | sd of the 400 | Smallest to largest | Seeds at or above the limit | Converged end (sd of that estimate) | Converged end minus the limit |
|---|---|---|---|---|---|---|---|---|---|---|
| EPYC 9V45 (23) | `k03_stencil.L1` | left out | 1.0204 | 71.8 | 1.0203 | 0.0002 | 1.0197 to 1.0211 | 366 | 1.0203 (0.00003) | +0.0003 |
| Xeon 8573C (7) | `k01_sum_fwd.L1` | judged | 1.0166 | 54.0 | 1.0165 | 0.0007 | 1.0142 to 1.0192 | 0 | 1.0165 (0.00011) | -0.0035 |
| Xeon 8573C (7) | `k01_sum_fwd.L2` | judged | 1.0134 | 4.2 | 1.0143 | 0.0005 | 1.0129 to 1.0160 | 0 | 1.0142 (0.00008) | -0.0058 |
| Xeon 8573C (7) | `k03_stencil.L1` | judged | 1.0173 | 95.2 | 1.0169 | 0.0003 | 1.0161 to 1.0176 | 0 | 1.0169 (0.00004) | -0.0031 |
| Xeon 8573C (7) | `k03_stencil.L2` | judged | 1.0166 | 39.2 | 1.0167 | 0.0003 | 1.0157 to 1.0176 | 0 | 1.0167 (0.00004) | -0.0033 |
| Xeon 6973P-C (7) | `k01_sum_fwd.L2` | judged | 1.0167 | 39.5 | 1.0168 | 0.0006 | 1.0154 to 1.0184 | 0 | 1.0169 (0.00009) | -0.0031 |
| Xeon 6973P-C (7) | `k03_stencil.L1` | left out | 1.0112 | 30.5 | 1.0112 | 0.0001 | 1.0109 to 1.0117 | 0 | 1.0112 (0.00002) | -0.0088 |
| Xeon 6973P-C (7) | `k03_stencil.L2` | judged | 1.0184 | 10.2 | 1.0193 | 0.0007 | 1.0172 to 1.0213 | 73 | 1.0196 (0.00011) | -0.0004 |

## Placement statistic

D compares the two builds' placement of the hot loops; a cell is left out of the forward rule when D's interval excludes 1 and the loops differ in the listings. The listings do not change with the seed; the interval does.

| Model (jobs) | Cell | Stored interval of D | Smallest low end to largest high end of the 400 | Seeds whose interval excludes 1 | Converged interval of D | Converged interval excludes 1 |
|---|---|---|---|---|---|---|
| EPYC 9V45 (23) | `k03_stencil.L1` | 0.9791 to 0.9917 | 0.9783 to 0.9926 | 400 of 400 | 0.9791 to 0.9918 | yes |
| Xeon 8573C (7) | `k02_add_fwd.L1` | 0.9907 to 1.0059 | 0.9895 to 1.0064 | 0 of 400 | 0.9902 to 1.0058 | no |
| Xeon 8573C (7) | `k03_stencil.L1` | 0.9959 to 1.0144 | 0.9941 to 1.0157 | 0 of 400 | 0.9957 to 1.0149 | no |
| Xeon 6973P-C (7) | `k03_stencil.L1` | 1.0070 to 1.0189 | 1.0067 to 1.0201 | 400 of 400 | 1.0071 to 1.0191 | yes |

## Whole analyses

The first 60 of the other seeds, each running the complete analysis of the model.

| Model (jobs) | Stored word | Words under the first 60 other seeds | Cells that miss the forward rule (seeds) | Cells left out as placement-sensitive (seeds) |
|---|---|---|---|---|
| EPYC 9V45 (23) | MAP | MAP 60 | none | `k02_add_fwd.L1`, `k02_add_fwd.L2`, `k03_stencil.L1` (60) |
| Xeon 8573C (7) | INCONCLUSIVE | INCONCLUSIVE 60 | `k02_add_fwd.L1` (60) | `k02_add_fwd.L2` (60) |
| Xeon 6973P-C (7) | MAP | MAP 47, INCONCLUSIVE 13 | `k03_stencil.L2` (13) | `k02_add_fwd.L1`, `k03_stencil.L1` (60) |

## What it shows

**Xeon 6973P-C depends on the draw.** The stored word is MAP, and the stored upper end of its stencil L2 cell, 1.0184, sits 0.0016 under the limit. That figure is the stored seed's margin alone: the stored end lies at about the 10th percentile of the ends under the 400 other seeds. Their median is 1.0193, and 73 of the 400 other seeds end at or above 1.02. The whole analysis returns MAP in 47 of the 60 other seeds and INCONCLUSIVE in 13 of the 60, every time through this cell. With 100,000 draws the end settles at 1.0196, which is 0.0004 under the limit (Monte Carlo sd 0.00011). One 2000-resample run spreads by 0.0007 (sd), wider than that margin, so a run of the pool's size lands on either side of the line. The honest word for this model is "borderline, seed-dependent": MAP under the stored seed, MAP under most other seeds, and a converged end that is on the MAP side by less than one run's spread.

**Xeon 8573C does not.** Its word is INCONCLUSIVE under all 60 other seeds. The cause is the forward-add cell `k02_add_fwd.L1`, which misses the forward rule under every seed, and no draw rescues it: the interval of its placement statistic D includes 1 under all 400 seeds, so the cell is never left out as placement-sensitive. None of its judged cells reaches the limit under any seed (the converged ends lie 0.0031 to 0.0058 under it).

**EPYC 9V45's MAP rests on an exemption, not on the draw.** Its stencil L1 cell has an aligned upper end of 1.0204 (stored) and 1.0203 (converged), at or above 1.02 in 366 of the 400 other seeds, so without the exemption it would miss the forward rule. The exemption holds under every seed tried: D's interval lies below 1 in 400 of 400 and the hot loops differ in the listings. All 60 whole analyses return MAP. The word is as stable as the exemption is; the exemption's own justification is a separate question from the seed.

**The Xeon 6973P-C's left-out cells are stable too.** Its stencil L1 cell is left out under all 400 seeds (D's interval excludes 1 in 400 of 400; converged 1.0071 to 1.0191).

## Limits

- Only the bootstrap's random draw varies. The jobs are the same 7 (Xeon) or 23 (EPYC 9V45); how the ends would move with other jobs is not tested here. The stored pool file is not changed and nothing here supersedes it.
- The converged reading is a Monte Carlo estimate with the sd shown; a margin of a few hundredths of a percent is not a precise statement about the cell, only about where the bootstrap puts the end.
- The 400 and 60 seeds are the same for every model (`seedsens-001` onward), so the models' seed results are not independent draws of one another.
