# Holdout result: original pooled runs vs the holdout (unedited)

Rules: `harness/criteria-v3.json` and `harness/pool.py`, unchanged since before the original runs
(see PREREGISTRATION.md, written before these runs started). Original: `results/s4-pooled/pooled.json`
(30 jobs, 3 runs). Holdout: `results/s5-holdout/pooled.json` (30 jobs, 3 fresh runs 38408152157,
38408166458, 38408179322). The CPU models drawn differ between the two, so the job counts differ.

| CPU model | original verdict (jobs) | holdout verdict (jobs) | loops that lose SIMD, cost in cache (original → holdout) | reproduced? |
|---|---|---|---|---|
| AMD EPYC 7763 | MAP (19) | MAP (19) | 3.19 to 8.01x, median 5.01 → 3.19 to 7.97x, median 5.04 | yes |
| AMD EPYC 9V74 | MAP (5) | MAP (6) | 4.05 to 5.78x, median 5.13 → 4.05 to 5.76x, median 5.15 | yes |
| AMD EPYC 9V45 | MAP (5) | INCONCLUSIVE (3, 2 runs) | 2.86 to 5.80x, median 3.97 → mixed picture: the forward rule (aligned) was missed by k03_stencil.L1, and the loops that lose SIMD still cost far more than the limit | the form did not reproduce (this CPU was already marked fragile) |
| Intel Xeon 8573C | too few jobs (1) | too few jobs (2) | no number printed | no verdict either time |

What this does and does not show: the two CPU models with enough jobs in both sets (EPYC 7763, 9V74)
gave the same verdict and nearly the same numbers on fresh draws. The 9V45 verdict did not reproduce
as MAP; it was already the fragile one, and the holdout had only 3 jobs on it. Nothing here
tests Intel (too few jobs both times) or any toolchain other than the main one.

Note: the workflow's last step (the repository's own check) failed on these three runs because the
checked-in real-program pooled file at that commit double-counted jobs (fixed in a later commit). The
measurement jobs, their uploaded results and the pooling had finished before that step, and the pooled
file here was recomputed from the downloaded artifacts with the unchanged `harness/pool.py`.
