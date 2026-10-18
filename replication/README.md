# Replication sets B and C

Status: work in progress (Oct 2026). Two sets of extra runs, planned in writing before any of them was dispatched (the order rests on commit times in unpublished history; see "What the plan does and does not show"), and the comparison with the pools they replicate. The pools the page and the README read are unchanged; the sets are reported beside them.

## Why

Two published verdicts rested on a thin margin: the Arm pool is INCONCLUSIVE because the forward add at L2, aligned, ends at 1.0211 against a limit of 1.02, and the Xeon 6973P-C is MAP with its stencil at L2 ending at 1.0184, just under the same limit. The question for both was whether the reading repeats on jobs that were not used to form it.

## What is here

- `PLAN.md`: the plan, committed before the runs in the author's unpublished development history. It fixes the two sets (B: 30 Arm jobs in 3 runs; C: 40 x86-64 jobs in 4 runs), how each is analysed (the same `harness/pool.py`, the unchanged `harness/criteria-v3.json`) and what is reported. Its sha256 is stored in `results.json`, where `compare.py` computes it when it builds that file.
- `compare.py`: reads six pooled files and writes `results.json` (standard library only).
- `results.json`: the comparison, never edited by hand. Per CPU model it holds the verdict form of the three pools and the cell behind a non-MAP form, the new points that lie inside the earlier interval, the named cells, the x86-64 headline range against set C and the models that could not be tested.

## The runs and the pooled files (under `results/`)

| Pool | Jobs | Folder | Role |
|---|---|---|---|
| Arm, set A (the original column) | 30 | `s8-arm-pooled` | read by the page |
| Arm, set B | 30 (29 Neoverse-N2, 1 Neoverse-V3) | `s9-arm-b-pooled` | the replication of set A |
| Arm, sets A and B | 60 | `s9-arm-ab-pooled` | secondary |
| x86-64, the first pool | 95 | `s7-pooled` | read by the page |
| x86-64, set C | 40 | `s9-x86-c-pooled` | the replication of the first pool |
| x86-64, the first pool and set C | 135 | `s9-x86-ac-pooled` | secondary |

The run folders are `results/s9-arm-run-*` (runs 39012918474, 39012932739 and 39012948541) and `results/s9-run-*` (runs 39012961317, 39012973892, 39012986182 and 39013000285). Every job record names commit 32ab03c of the default branch as the code it ran. Each pooled file is made by `python harness/pool.py <out.json> <run folders>` from the run folders it lists under `inputs`.

The separate sets are the result. The pooled forms are secondary because the sets were requested after a borderline reading, so the stopping point depended on the data (plan, item 3).

## To check

```
python replication/compare.py --verify
```

recomputes `results.json` from the six pooled files and fails on any difference, including a changed plan. `python scripts/check.py` runs it, and also checks that each s9 pooled file lists every job of the run folders it names.

## What the plan does and does not show

`PLAN.md` was committed in the author's unpublished development history 27 seconds before the earliest job start recorded in the 70 job records (`run.started_at`; the commit time is from the author's machine and the start time from the runner, and the two clocks were not compared). The public repository did not hold the file at commit 32ab03c, the commit the runs were dispatched from, and no public record shows the order. A hash shows that a file is unchanged, not when it was written: the hash in `results.json` is computed by `compare.py` when the comparison is built, after the data were in, and the per-job records do not carry it. So the sets are described as planned before they were dispatched, on commit times a reader of this repository cannot check, and not as a pre-registration. The d-sweep is better placed: every one of its result files stores the hash of its plan.

## The combine step

Two of the four set-C combine jobs (runs 39012986182 and 39013000285) ended red on `harness/pool_check.py`, which disagreed with the pooled file on a model with fewer than 3 jobs (run 39012986182: the Xeon 6973P-C, 1 job, matrix multiply at L1, as compiled; run 39013000285: the EPYC 9V74, 2 jobs, the stencil at L1, as compiled; the two other combine jobs passed). The checker now samples only models with 3 or more jobs, the minimum for a verdict, and lists the others as skipped. No verdict uses a model with fewer, the pooled files and the rules are unchanged, and only that check's sampling rule changed (`tests/test_replication.py` runs the two pooled files through it).

## What came out

Set B alone is INCONCLUSIVE again, on the same cell (the forward add at L2, aligned: 1.0211 in set A, 1.0247 in set B, limit 1.02). The cell sits close to the limit in both sets, so a second INCONCLUSIVE is a weak repeat of the word and not strong evidence for it. Of the four x86-64 models with 3 or more jobs in set C, two gave the same verdict word as the first pool and two a different one; both changes are the rule's placement exemption switching at a cell whose measured cost is about the same. The Xeon 6973P-C had 1 job in set C and could not be tested. The headline range of 2.8x to 8.0x holds. The account with the numbers is in the [README](../README.md) and in [readme-parts/DETAILS.md](../readme-parts/DETAILS.md).

## What the inside count is

Plan item 2 asked for the new set's pooled aligned ratio alone, and described the share as "as in the holdout column of the page". That description is wrong: the holdout table's "Reproduced" column compares verdict words only. The stored count (`results.json`) compares each new pooled ratio, in both columns (as compiled and aligned), with the earlier pool's 95% interval: the point-inside-interval test of `harness/pool.py` `reproduction()`, which the page already applies run against run. That form was written into `compare.py` after the sets' data were in, so aligned alone is printed beside it: Arm 11 of 16 against 26 of 32 in both columns, x86-64 48 of 64 against 101 of 128. The count is descriptive: a new pooled point carries its own noise, so fewer than 95% of points are expected inside even when nothing has changed, and the share mostly follows interval width and set size. No expectation under "no change" is printed or claimed.
