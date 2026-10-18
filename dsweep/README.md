# Matrix-multiply d-sweep

Status: work in progress (Oct 2026). One question, a rule committed before the runs, and three runs (18 jobs); no further runs are planned for this question.

## Question

On Neoverse-N2 matrix multiply keeps its NEON loop under FAST and still costs 1.55x at the L1 size (d = 52). Is the time that FAST adds per inner call the same at every matrix size (a fixed cost, H1), proportional to d (a cost per element, H2), or smaller at the larger sizes ("falls")? [arm64/README.md](../arm64/README.md) read the listing as a setup cost before the NEON loop and called that an inference; the sweep tests it.

## Read the folder in this order

- `PLAN.md`: drafted before the sweep code, revised while the code was written and tested and once more after a review of the plan and the code (the review changed the deciding statistic; the plan's own "Changes made before any run" lists every change), and committed alone, before the code commit and before the first run, in the author's unpublished development history. It fixes the question, the sizes, the statistic (the fixed share of the excess per inner call) and the rule that gives a word. Every result file stores its sha256, and `analyze.py` treats a file whose stored hash differs as a file problem, so an edit after the first run would make all the data unusable: the hash shows that the plan did not change after the runs. The order before the runs is not checkable from public records. On this repository the plan arrived in one commit together with the code, on the temporary branch `dsweep-smoke`.
- `sweep.py`: builds `kernels/k08_matmul.cpp` four ways (NONE and FAST, each as compiled and with `-falign-loops=64`) and times FAST against NONE at the sizes the runner's cache sizes decide, with a byte-identical A/A and Cachegrind instruction counts as a labelled secondary column.
- `analyze.py`: applies the rule mechanically. It pools the job files per CPU model (3 jobs at least) with the two-level bootstrap of `harness/pool.py` and writes the pooled file and a table.
- `.github/workflows/dsweep.yml`: the workflow (a `runner` input picks x86-64 or Arm).
- `results/s10-dsweep-run-*`: the three runs as downloaded (39018966032 on Arm, 39018969973 and 39018974239 on x86-64). `results/s10-dsweep-pooled/`: `dsweep-pooled.json`, the pool of all three, and `table.md`.

## What the rule gave

| CPU model | Jobs (runs) | Word |
|---|---|---|
| Neoverse-N2 | 6 (1) | neither: the two columns disagree (as compiled "falls", aligned H1) |
| AMD EPYC 7763 | 9 (2) | H2 in both columns |
| AMD EPYC 9V45 | 2 (1) | too few jobs |
| Intel Xeon Platinum 8573C | 1 (1) | too few jobs |

On Neoverse-N2 the fixed share is 1.332 as compiled and 1.090 aligned, both above 1, so the result is not a mixture. FAST adds 77 extra instructions per inner call at every size with d = 4 mod 8 from 12 to 148 (instruction counts, a secondary column, not times). The plan's illustrative table did not hold in size (R(12) = 3.35 under H1; 2.31 observed), and the rule, not the table, decides. EPYC 7763, where the checked loop loses SIMD, gave H2, which the plan expected there; that is all that control says. The account with the table is in the [README](../README.md) and in [readme-parts/DETAILS.md](../readme-parts/DETAILS.md).

The stored `reason` of an H1 column ends "the excess per inner call is the same at every d". That phrase is the registered code's wording for "inside the H1 band" (a fixed share of 0.8 to 1.2), not a statement that the excess is constant: on Neoverse-N2 the aligned column is H1 (fixed share 1.090), and its excess, at the sizes with d = 4 mod 8, is 4.2 to 4.7 ns from d = 12 to d = 108, 3.7 ns at d = 148 and 0.50 ns at d = 209. `analyze.py` and the stored files are not changed.

The sweep also bears on the study's headline range. On EPYC 7763, as compiled, matrix multiply costs 2.5x at d = 12, 3.2x at d = 36 (the study's L1 size) and 4.2x at d = 76 (past its 32 KiB L1d), so the 2.8x of "2.8x to 8.0x" is not a floor for these loops and the range holds at the study's sizes.

## To check

```
python dsweep/analyze.py --verify results/s10-dsweep-run-*
python dsweep/analyze.py results/s10-dsweep-run-* --out dsweep-pooled.json --md table.md
```

The first validates every `dsweep.json` and recomputes its ratios and intervals from the raw samples; the second pools them again (the result equals the stored file apart from the input paths). `python scripts/check.py` runs both and the plan-hash guard.

## The runs and the temporary branch

The three runs were dispatched from a temporary branch of the public repository, `dsweep-smoke` (commit 8c874ec), which carried the sweep before the default branch did. On that branch the d-sweep workflow file is named `ci.yml` (a dispatchable workflow must already exist on the default branch); in this tree it is `.github/workflows/dsweep.yml`. The branch is kept because the run records name that commit. Each job stored the sha256 of the code files it ran, and the pooled file records that none of them had changed when the jobs were pooled.

Before the three runs, the code path was tested on generated data (`tests/test_dsweep.py`) and in smoke runs, which time fewer repetitions per side than the 40 of `harness/criteria-v3.json`. The analysis refuses smoke files as not a result, so they are never pooled and are not under `results/`.

## What the sweep cannot show

No hardware counters were read, so it cannot say where the cycles go. One kernel, one compiler (clang 18.1.3 with libc++ 18, FAST mode) and `-O2`. The Arm result is one run of six jobs on one core type that agree closely, so its intervals show no run-to-run or host-to-host spread. `-falign-loops=64` moves every loop, not only the hot one, so the aligned column is not a pure placement control.
