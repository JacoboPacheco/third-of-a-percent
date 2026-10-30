# forwardt: the time cost of six forward loops with a variable bound

Status: work in progress (Oct 2026). The plan, the six loops, the measurement code, the analysis and the recorded runs are in this folder. The result is under [Result](#result); `runs.json` lists the runs it rests on.

## Question

The compile-only sweep in [forwardn/README.md](../forwardn/README.md) found that with clang 16.0.0 to 18.1.0 and the libc++ hardening macro on, a forward loop whose bound is a variable and not `size()` stops being vectorized on x86-64 at `-O2` (the sums, a fill loop and an offset copy are lost; a scaled copy is narrower). It looked at the compiler's remarks and did not time anything. This folder times six such loops: for each CPU model, what is the ratio of the run time under FAST to the run time under NONE, with its 95 % interval, with the working set in L1 and in L2, as compiled and with `-falign-loops=64`? Two of the six are controls: `t01_sum_size` and `t03_scale_size` differ from `t02_sum_n` and `t04_scale_n` in the bound alone. The fill loop and the offset copy have no control, so what their cost owes to the bound is not separated.

## Read the folder in this order

- `PLAN.md`: the plan. `forwardt/PLAN.md` was committed on its own, before the code and before any run; that order rests on the author's clock and on the public history, in which the plan is the only file of its commit. It fixes the question, the six loops, the builds, the sizes, the statistic, the words per loop, the predictions with their bands, the rules for what a model can be read on, the outcome letters and the rules for the runs. Every result file stores its sha256 (line endings read as LF) and `analyze.py` treats a measurement file whose stored hash differs as a file problem, so a change made in a later commit than the one a run started from shows as a file problem in that run's files; a change made in or before that commit does not show. The plan is not edited. It lists its own changes after the first commit (none so far) and what its hashes cannot show.
- `kernels/`: the six sources, one per loop, in the shape of the repository's `kernels/k02_add_fwd.cpp`, including its driver and checksum from the repository's `kernels/common.hpp` (not a file of this folder):

| Loop | Source | Bound | Word on clang 18, x86-64, `-O2` (forwardn) |
|---|---|---|---|
| `s += a[i]` | `forwardt/kernels/t01_sum_size.cpp` | `a.size()` | kept (control) |
| `s += a[i]` | `forwardt/kernels/t02_sum_n.cpp` | `n` | lost |
| `c[i] = a[i] * 2` | `forwardt/kernels/t03_scale_size.cpp` | `a.size()` | kept (control) |
| `c[i] = a[i] * 2` | `forwardt/kernels/t04_scale_n.cpp` | `n` | narrower |
| `c[i] = i * 3` | `forwardt/kernels/t05_fill_n.cpp` | `n` | lost |
| `c[i + off] = a[i]` | `forwardt/kernels/t06_offset.cpp` | `n` and `off` | lost |

  In every run `n` equals the length of the vectors, so no check fires; the loops are `noinline` functions called from a driver.
- `sweep.py`: one job. It builds each loop five ways (NONE and FAST as compiled, NONE and FAST with `-falign-loops=64`, and a build with vectorization switched off), times FAST against NONE in ABBA order on one pinned CPU, with 40 processes per side as in `harness/criteria-v3.json`, at an L1-sized and an L2-sized working set, together with a byte-identical A/A for every cell and, for the four loops with a variable bound (`t02_sum_n`, `t04_scale_n`, `t05_fill_n`, `t06_offset`), when their NONE loop is vectorized, the no-vectorize build against NONE. It also stores the compiler's remarks, the trap counts, the assembly and the hot loop's placement, and Cachegrind instruction counts as a labelled secondary column. It writes `forwardt.json` per job (the schema is in its header) and keeps a `forwardt.partial.jsonl` while it runs. `python3 forwardt/sweep.py --assume-caches 64,1024` prints the sizes for a 64 KiB L1d and a 1 MiB L2 and needs no Linux.
- `analyze.py`: applies the plan mechanically. It reads `runs.json` and nothing else, pools the `forwardt.json` files per CPU model (3 jobs at least) with the two-level bootstrap of `harness/pool.py`, applies the words, the predictions P0 to P6 and the outcome letters, writes `results.json` beside the manifest and prints a report. With no run in the manifest it says so and writes a file in which every prediction is "not testable". A bare `python forwardt/analyze.py` writes `results.json` beside the manifest (and replaces the one that is there); `--no-write` only prints the report and writes nothing, so it is the call for looking at a result; `--verify` recomputes from the stored files, compares with the stored `results.json` and writes nothing, so it is the call for checking one.
- `runs.json`: the manifest of the Actions runs, one entry per run (see below). It lists five: two code tests and three measurement runs (see Result).
- `.github/workflows/forwardt.yml`: the workflow, started by hand only, with the inputs `runner` (`ubuntu-24.04` or `ubuntu-24.04-arm`), `jobs`, `reps` and `time_limit` (the time limit of a job in minutes, as text, default `45`). It runs the offline self-test, the sweep and uploads the job's `out/` folder before anything is checked.
- `tests/test_forwardt.py` (the sweep, on generated data; the workflow also runs it as `python3 tests/test_forwardt.py`), `tests/test_forwardt_analyze.py` (the analysis, on generated data) and `tests/test_forwardt_registration.py` (the step of `scripts/check.py` that checks this folder) and `tests/test_forwardt_docs.py` (ties every number of the Result section below, and the forwardt sentences of `README.md` and `readme-parts/DETAILS.md`, to `results.json`).

## How a run is dispatched and recorded

The plan called for a code test on each runner (`jobs` = `[1]` and `reps` = 4, so that the files are marked as smoke files, which the analysis sets aside and never pools), then three measurement runs of 6 jobs: one on `ubuntu-24.04-arm` (Neoverse-N2) and two on `ubuntu-24.04`, the two x86-64 runs from one commit. The five runs were dispatched from a temporary branch of the public repository, `forwardt-run` (manifest key `branch`), as the `dsweep` runs were; each file records its commit. The branch is kept for as long as the runs record its commits.

Every Actions run that executes `sweep.py` to time anything is an entry of `runs.json`, whatever its outcome: tests, failed and cancelled runs included. An entry gives the run id, the runner, the commit, the creation time (UTC), the class (`test` or `measurement`), the clause of the plan that called for it (or the words `not in the plan` with a reason), the jobs started and returned, the reason for each job that did not return, and the folder under `results/` that holds its downloaded files (null for a run that is not stored). The analysis stops, and writes nothing, when a folder named by the manifest is missing, when a file carries a run id that the manifest does not list, or when the number of files in a folder differs from the entry's count of returned jobs. A job that fails is listed and not replaced; no run is started to change a word.

## Recording a run

`runs.json` is edited by hand after the runs, one entry per Actions run, in the order of their creation times (a different order is printed as a note and does not stop the analysis). The first entry of the manifest, a code test included, comes together with five top-level keys; if one of them is missing, `analyze.py` stops with exit code 3 and writes nothing, and the check step fails.

| Top-level key | Content |
|---|---|
| `branch` | the temporary branch the runs were dispatched from |
| `workflow_file` | the workflow file those runs used: `.github/workflows/forwardt.yml`, or the path it had on the branch if that differs |
| `time_limit_minutes` | the time limit of a job in minutes (a positive number), the dispatch input `time_limit` |
| `query` | the command `gh run list -R <repository> --branch <branch> --limit 200`, which lists the same runs |
| `test_ratios_read` | `true` when any ratio of a test run was read, otherwise `false`; the report says which runs |

`repository` and `note` are optional. An entry has the fields `run_id` (the Actions run id, digits, as text), `runner` (`ubuntu-24.04` or `ubuntu-24.04-arm`), `head_sha` (the 40-character commit the run started from), `created_at` (UTC, as the Actions API gives it), `class` (`test` or `measurement`), `clause` (one of `code test`, `Neoverse-N2 run`, `x86-64 run 1`, `x86-64 run 2`, `restart after a code fix`, `restart after a platform failure`, `restart after the time limit` or `not in the plan`), `reason` (required, and not empty, when the clause is `not in the plan`), `jobs_started`, `jobs_returned` (not above `jobs_started`), `not_returned` (a list of `{"job": "4", "reason": "..."}` with exactly `jobs_started` minus `jobs_returned` items) and `folder` (the folder that holds the downloaded files, `results/<name>`, relative to the repository root and used literally, or `null` for a run that is not stored), and optionally `note` and `time_limit_minutes`. An entry's own `time_limit_minutes` replaces the top-level value for that run, so a restart under a raised limit states the limit it ran under.

What the analysis requires of the stored files, each stop naming the file and ending in exit code 3:

- The architecture recorded in a file matches the runner of its entry (`aarch64` for `ubuntu-24.04-arm`, `x86_64` for `ubuntu-24.04`), and the commit recorded in it equals the entry's `head_sha`.
- Every `forwardt.json`, and the header of every `forwardt.partial.jsonl`, records `run.attempt`, a whole number from 1. A file from a second or later attempt (`run.attempt` above 1) stops the analysis. The plan lists a job that failed and does not replace it, and "Re-run failed jobs" on the Actions page makes a second attempt of the same run id, so the files of that attempt carry the run id of the first. To go on, the file of the later attempt is removed from the folder and the job is recorded as not returned, with the reason, in the entry's `not_returned`.
- Two `forwardt.json` files in one folder that carry the same run id and job stop the analysis, whether they are byte-identical (an artifact downloaded twice into it) or differ in content; the stop names both paths, and the wrong one is removed.

## State

The plan is public, the code was tested on generated data, and `runs.json` lists five runs: two code tests and three measurement runs, 18 of 18 measurement jobs returned. `results.json` holds the analysis of the manifest, and `python forwardt/analyze.py --verify` recomputes it from the stored files. The sha256 of the plan stored in every result file equals that of `PLAN.md` in this folder, which `scripts/check.py` checks. The result is below.

## Result

All five runs started from commit 595e061 of the public repository.

- Code tests (2), started with `jobs` = `[1]` and `reps` = 4, so their files are smoke files that the analysis sets aside: run 40181023212 on `ubuntu-24.04` and run 40181028100 on `ubuntu-24.04-arm`. They were not stored or pooled, and no ratio of either was read.
- Measurement runs (3), 18 of 18 jobs returned: run 40861186704 on `ubuntu-24.04-arm` (6 of 6 jobs, `results/s11-forwardt-run-40861186704`), run 40861190251 on `ubuntu-24.04` (6 of 6 jobs, `results/s11-forwardt-run-40861190251`), run 40861193559 on `ubuntu-24.04` (6 of 6 jobs, `results/s11-forwardt-run-40861193559`).
- CPU models that GitHub drew: EPYC 7763 for 7 jobs, EPYC 9V45 for 2 jobs, EPYC 9V74 for 3 jobs, Neoverse-N2 for 6 jobs.

A CPU model is read only when at least 3 jobs of it returned (rule 1 of the plan). EPYC 7763 has 7 jobs from runs 40861190251 and 40861193559. EPYC 9V45 has 2 jobs and is not read: its numbers are in `results.json`, marked as not read, and it enters no table, word or prediction below. EPYC 9V74 has 3 jobs from run 40861193559, so its intervals are coarse and understate the spread between jobs. Neoverse-N2 has 6 jobs from run 40861186704.

### x86-64: outcome letter D

The outcome table of the plan gives letter D for x86-64, read on EPYC 7763 and EPYC 9V74: prediction P2 failed above its band and P3 held. P2 said that the sum with a variable bound, `t02_sum_n`, takes between 0.97 and 1.35 times as long under FAST as under NONE. Both columns of every `t02_sum_n` pair on both models lie wholly above 1.35 (the lower end of each interval is above it):

| Model | Size | Column | FAST over NONE (95 % interval) |
|---|---|---|---|
| EPYC 7763 (7 jobs) | L1 | compiled | 2.038 (1.996 to 2.084) |
| EPYC 7763 (7 jobs) | L1 | aligned | 2.043 (2.003 to 2.085) |
| EPYC 7763 (7 jobs) | L2 | compiled | 2.015 (1.975 to 2.061) |
| EPYC 7763 (7 jobs) | L2 | aligned | 2.039 (2.001 to 2.086) |
| EPYC 9V74 (3 jobs) | L1 | compiled | 1.986 (1.985 to 1.987) |
| EPYC 9V74 (3 jobs) | L1 | aligned | 1.985 (1.984 to 1.986) |
| EPYC 9V74 (3 jobs) | L2 | compiled | 1.997 (1.994 to 1.999) |
| EPYC 9V74 (3 jobs) | L2 | aligned | 1.999 (1.997 to 2.000) |

The sum cells are given as measured; under letter D the plan states no limit and no forward-range word for them. The other predictions on the two models (a combination is one loop at one size in one column):

| Prediction | Band | EPYC 7763 (7 jobs) | EPYC 9V74 (3 jobs) |
|---|---|---|---|
| P0 | the six words; one or more FAST traps in each variable-bound loop | holds on 6 of 6 loops | holds on 6 of 6 loops |
| P1 | controls: `t01_sum_size` 0.97 to 1.03, `t03_scale_size` aligned 0.79 to 1.23 | holds | holds |
| P2 | `t02_sum_n`, both columns: 0.97 to 1.35 | fails: 2 above | fails: 2 above |
| P2n | `t02_sum_n`, no-vectorize build: 0.90 to 1.35 | holds | holds |
| P3 | `t05_fill_n`, `t06_offset` at L1, both columns: above 1.5 | holds | holds |
| P4 | `t04_scale_n`, aligned: at most 1.30 | holds | holds |
| P5 | L2 ratio over L1 ratio of each lost loop: 0.80 to 1.25 | holds | holds |

P3 held: at L1 the intervals of `t05_fill_n` and `t06_offset` lie above 1.5 in both columns on both models. For a write cell the plan allows the words "at or above 1.5x" and no other limit. The two columns of `t05_fill_n` differ: on EPYC 7763 at L1 it is 7.790 (7.785 to 7.795) as compiled and 3.970 (3.914 to 4.042) aligned, and the plan's placement statistic (the as-compiled ratio over the aligned one) is 1.962 (1.926 to 1.990). A single cost for that loop is not read from the two columns.

The tables give every cell, the six loops at L1 and L2. "As compiled" and "Aligned" are the FAST over NONE ratio of the median run times in the two builds; "No-vectorize build" is the build with vectorization switched off over NONE, timed for the four loops with a variable bound where NONE is vectorized; "A/A half-width" is the half-width of the interval of NONE timed against a byte-identical copy of itself, and a cell above 2.0 % is not decidable. `t01_sum_size` and `t03_scale_size` are bounded by `size()`; `t02_sum_n`, `t04_scale_n`, `t05_fill_n` and `t06_offset` by a variable `n` (`t06_offset` also by `off`).

#### EPYC 7763 (7 jobs)

| Loop | Word | Size | As compiled | Aligned (`-falign-loops=64`) | No-vectorize build | A/A half-width |
|---|---|---|---|---|---|---|
| `t01_sum_size` | kept | L1 | 1.000 (0.999 to 1.000) | 1.000 (0.999 to 1.000) | - | 0.09 % |
| `t01_sum_size` | kept | L2 | 1.001 (0.998 to 1.003) | 1.000 (0.999 to 1.001) | - | 0.23 % |
| `t02_sum_n` | lost | L1 | 2.038 (1.996 to 2.084) | 2.043 (2.003 to 2.085) | 1.282 (1.281 to 1.282) | 0.07 % |
| `t02_sum_n` | lost | L2 | 2.015 (1.975 to 2.061) | 2.039 (2.001 to 2.086) | 1.270 (1.269 to 1.271) | 0.17 % |
| `t03_scale_size` | kept | L1 | 0.949 (0.948 to 0.950) | 0.997 (0.996 to 0.998) | - | 0.08 % |
| `t03_scale_size` | kept | L2 | 0.998 (0.989 to 1.004) | 0.996 (0.987 to 1.002) | - | 1.16 % |
| `t04_scale_n` | narrower | L1 | 1.071 (1.070 to 1.072) | 1.064 (1.063 to 1.065) | 3.041 (3.039 to 3.089) | 0.05 % |
| `t04_scale_n` | narrower | L2 | 1.005 (0.998 to 1.015) | 1.014 (1.004 to 1.025) | 3.313 (3.292 to 3.321) | 0.91 % |
| `t05_fill_n` | lost | L1 | 7.790 (7.785 to 7.795) | 3.970 (3.914 to 4.042) | 2.452 (2.451 to 2.454) | 0.06 % |
| `t05_fill_n` | lost | L2 | 7.935 (7.924 to 7.949) | 4.025 (3.986 to 4.092) | 2.490 (2.485 to 2.494) | 0.08 % |
| `t06_offset` | lost | L1 | 7.626 (7.614 to 7.641) | 7.997 (7.990 to 8.003) | 2.898 (2.894 to 2.943) | 0.10 % |
| `t06_offset` | lost | L2 | 7.702 (7.604 to 7.762) | 7.794 (7.724 to 7.845) | 3.289 (3.278 to 3.301) | 1.17 % |

#### EPYC 9V74 (3 jobs)

| Loop | Word | Size | As compiled | Aligned (`-falign-loops=64`) | No-vectorize build | A/A half-width |
|---|---|---|---|---|---|---|
| `t01_sum_size` | kept | L1 | 1.000 (0.999 to 1.001) | 1.000 (1.000 to 1.001) | - | 0.07 % |
| `t01_sum_size` | kept | L2 | 1.000 (0.998 to 1.001) | 1.000 (1.000 to 1.001) | - | 0.10 % |
| `t02_sum_n` | lost | L1 | 1.986 (1.985 to 1.987) | 1.985 (1.984 to 1.986) | 1.289 (1.288 to 1.290) | 0.07 % |
| `t02_sum_n` | lost | L2 | 1.997 (1.994 to 1.999) | 1.999 (1.997 to 2.000) | 1.291 (1.290 to 1.292) | 0.13 % |
| `t03_scale_size` | kept | L1 | 0.984 (0.982 to 0.985) | 0.998 (0.998 to 1.000) | - | 0.08 % |
| `t03_scale_size` | kept | L2 | 0.999 (0.988 to 1.010) | 1.001 (0.994 to 1.005) | - | 0.31 % |
| `t04_scale_n` | narrower | L1 | 1.070 (1.069 to 1.071) | 1.088 (1.087 to 1.089) | 3.047 (3.045 to 3.072) | 0.04 % |
| `t04_scale_n` | narrower | L2 | 0.999 (0.984 to 1.016) | 1.007 (0.993 to 1.014) | 3.234 (3.186 to 3.261) | 0.73 % |
| `t05_fill_n` | lost | L1 | 7.814 (7.808 to 7.818) | 4.024 (4.022 to 4.027) | 2.461 (2.459 to 2.471) | 0.06 % |
| `t05_fill_n` | lost | L2 | 7.974 (7.958 to 8.024) | 3.977 (3.964 to 3.998) | 2.495 (2.491 to 2.499) | 0.06 % |
| `t06_offset` | lost | L1 | 6.908 (6.899 to 6.916) | 7.104 (7.098 to 7.112) | 2.991 (2.988 to 2.993) | 0.10 % |
| `t06_offset` | lost | L2 | 6.951 (6.902 to 6.968) | 6.892 (6.807 to 6.937) | 3.313 (3.283 to 3.354) | 1.67 % |

### Neoverse-N2

One run of six jobs on one core type. Prediction P6 failed.

| Prediction | Band | Neoverse-N2 (6 jobs) |
|---|---|---|
| P0 | the six words; one or more FAST traps in each variable-bound loop | holds on 6 of 6 loops |
| P1 | controls, both columns: 0.97 to 1.03 | holds: 4 of 8 combinations judged, 4 not decidable |
| P6 | `t05_fill_n`, `t06_offset`, both columns: 0.95 to 1.15 | fails: 1 below; 1 straddle; 6 of 8 combinations judged, 2 not decidable |

| Loop | Word | Size | As compiled | Aligned (`-falign-loops=64`) | No-vectorize build | A/A half-width |
|---|---|---|---|---|---|---|
| `t01_sum_size` | kept | L1 | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | - | 0.01 % |
| `t01_sum_size` | kept | L2 | 1.005 (0.978 to 1.034) | 1.002 (0.978 to 1.021) | - | 2.39 % (not decidable) |
| `t02_sum_n` | lost | L1 | 5.854 (5.852 to 5.855) | 5.829 (5.755 to 5.839) | 4.820 (4.819 to 4.821) | 0.01 % |
| `t02_sum_n` | lost | L2 | 5.778 (5.554 to 5.894) | 5.743 (5.593 to 5.879) | 4.837 (4.699 to 4.972) | 2.06 % (not decidable) |
| `t03_scale_size` | kept | L1 | 1.013 (1.013 to 1.013) | 1.013 (1.013 to 1.013) | - | 0.01 % |
| `t03_scale_size` | kept | L2 | 0.984 (0.925 to 1.037) | 0.996 (0.949 to 1.042) | - | 5.88 % (not decidable) |
| `t04_scale_n` | kept | L1 | 1.018 (1.018 to 1.018) | 1.018 (1.018 to 1.018) | 6.826 (6.826 to 6.827) | 0.01 % |
| `t04_scale_n` | kept | L2 | 0.981 (0.945 to 1.036) | 0.985 (0.936 to 1.040) | 6.648 (6.310 to 6.865) | 4.15 % (not decidable) |
| `t05_fill_n` | kept | L1 | 0.883 (0.880 to 0.886) | 1.022 (1.019 to 1.024) | 2.878 (2.875 to 2.882) | 0.16 % |
| `t05_fill_n` | kept | L2 | 0.969 (0.967 to 0.971) | 0.949 (0.947 to 0.952) | 2.842 (2.841 to 2.843) | 0.04 % |
| `t06_offset` | kept | L1 | 1.023 (1.020 to 1.025) | 1.020 (1.018 to 1.022) | 5.862 (5.850 to 5.878) | 0.29 % |
| `t06_offset` | kept | L2 | 1.025 (0.955 to 1.083) | 0.993 (0.943 to 1.034) | 4.238 (3.924 to 4.546) | 5.98 % (not decidable) |

- One run: the intervals cannot show run-to-run or host-to-host spread.
- The cells of five of the six loops at L2 are not decidable: the A/A half-width there is 2.06 to 5.98 %, above the 2.0 % ceiling of the plan's rule 4. Such a cell is reported with its numbers and neither holds nor fails a prediction. Every cell at L1 is decidable; at L2 only `t05_fill_n` is.
- `t02_sum_n` is lost on this core: 5.854 (5.852 to 5.855) as compiled and 5.829 (5.755 to 5.839) aligned at L1. The plan gives it no band here, so the numbers are reported without one.
- P6 failed on one cell: `t05_fill_n` at L1 as compiled is 0.883 (0.880 to 0.886), wholly below the lower edge 0.95. The same loop aligned at L1 is 1.022 (1.019 to 1.024), inside the band, and the plan's placement statistic for that cell is 0.864 (0.861 to 0.867). At L2 the aligned cell is 0.949 (0.947 to 0.952), whose interval contains the lower edge, so it is neither inside nor outside the band. The two columns of this loop differ, and nothing here says which of them is the cost of the loop on this core.

### What the result does not say

- P1 held on both x86-64 models: `t01_sum_size` is inside 0.97 to 1.03 and `t03_scale_size` aligned inside 0.79 to 1.23. That is a result for these two loops, which are bounded by `size()`. It is not a result for forward loops with another bound; the cells of those are in the tables above.
- The loop census (`corpus/README.md`, clang 18) counts 444 lost loops, one per function a loop was compiled into; 228 of them, at 38 source locations, fall in its class "forward loop bounded by a variable", assigned by a text pattern on the loop header and body. The census does not know how often any of them runs, and how many of the 228 have one of the six shapes timed here is not counted. The ratios above are for six hand-written loops: they are not a cost for those 228 loops and not a share of a program's run time.
- One compiler (clang 18.1.3 with libc++ 18), `-O2`, `int32` data, L1 and L2 only; the limits are listed under "What it cannot show".

## To check

```
python forwardt/analyze.py --verify
python forwardt/analyze.py --no-write      # prints the report and writes nothing
python3 tests/test_forwardt.py
```

`--verify` validates every stored `forwardt.json`, recomputes its ratios and intervals from the raw samples and recomputes the results file from the manifest; a manifest that lists no run has nothing to verify and passes. `python scripts/check.py` runs it as a step, together with a guard on the plan: the sha256 of `forwardt/PLAN.md` must equal the one recorded in `scripts/check.py` and in `forwardt/analyze.py` and be the plan hash stored in every `forwardt.json` and result file, and every stored `forwardt.json` must lie in a folder that the manifest names. A missing analysis script, plan or manifest, an unreadable results file, or a results file missing while the manifest lists a run, fails the step.

## What it cannot show

Six hand-written loops, `int32` data, one compiler (clang 18.1.3 with libc++ 18, hardening mode FAST) at `-O2`, baseline x86-64 and AArch64: nothing about other compilers or flags, or about how often such a loop is hot in a real program. The compile-only sweep finds the functions these loops come from vectorized under FAST from clang 19.1.0 on; this folder times 18.1.3 only and says nothing about what a later compiler pays. In cache only (L1 and L2, no RAM). The runners are shared and GitHub draws each job's CPU model, so which models reach 3 jobs is not controlled; the Neoverse-N2 column is one run of six jobs, whose intervals cannot show run-to-run spread, and EPYC 9V74 is three jobs of one run. No hardware counters are read. The list of runs is kept by the author; the independent record is the Actions run list of the public repository.
