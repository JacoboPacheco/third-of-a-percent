# Replication plan, written before the runs

Written on Sat Oct 17, 2026, in the commit that adds this file. No run of set B or set C had been dispatched when it was committed.

## Why

Two published verdicts rest on a thin margin:

- **Arm pool** (30 jobs, runs 38905055834, 38905081930, 38905108936, Neoverse-N2): INCONCLUSIVE under `harness/criteria-v3.json` because the upper end of the aligned interval of `k02_add_fwd` at the L2 size is 1.0211 against a limit of 1.02. Other seeds and other interval methods mostly give MAP (`arm64/seed-sensitivity.json`, `robustness/`).
- **Xeon 6973P-C** (7 jobs of the 95-job x86-64 pool): MAP, borderline: the upper end of the aligned interval of the stencil at L2 is 1.0184 against the same limit, and leaving one job out gives INCONCLUSIVE in 6 of 7 cases.

The question for both: does the reading repeat on jobs that were not used to form it?

## What is run

| Set | Runner label | Runs | Jobs | Workflow |
|---|---|---|---|---|
| B (Arm) | `ubuntu-24.04-arm` | 3 | 30 | `measure.yml` on `main`, default inputs |
| C (x86-64) | `ubuntu-24.04` | 4 | 40 | `measure.yml` on `main`, default inputs |

The jobs a run gets are drawn by GitHub; the CPU models are not chosen.

## How the sets are analysed (fixed now)

1. Each set is pooled on its own by `harness/pool.py` under `harness/criteria-v3.json`, unchanged: the same thresholds, seed prefix (20261011), number of resamples (2000) and exclusion rules. Nothing is changed after a result is read.
2. Reproduction: for each cell, whether the new set's pooled aligned ratio lies inside the earlier pool's interval, reported as a share, as in the holdout column of the page.
3. Pooled forms (A and B for Arm; the 95 jobs and C for x86-64) are shown beside the separate sets and never replace them. They are secondary because the sets were requested after a borderline reading, so the stopping point depended on the data.
4. Whatever comes out is reported. The stored verdicts of the earlier pools stay as they are. If set B is INCONCLUSIVE on the same cell, that is stated; if it gives MAP, the page states that the two sets disagree and shows both.
5. The headline range (reverse, stride-2 and matrix multiply in cache, currently 2.8x to 8.0x on x86-64) is checked against set C, and any cell outside it is reported.
6. No further runs are started for these two questions after any result of B or C has been read. A job that fails or is cancelled is listed and not replaced.
