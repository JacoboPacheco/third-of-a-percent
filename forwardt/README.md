# forwardt: the time cost of six forward loops with a variable bound

Status: work in progress (Oct 2026). The plan, the six loops, the measurement code and the analysis are in this folder. No run of the sweep exists, `runs.json` lists none, and no result is claimed here or anywhere else in the repository.

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
- `runs.json`: the manifest of the Actions runs, one entry per run (see below). It is empty.
- `.github/workflows/forwardt.yml`: the workflow, started by hand only, with the inputs `runner` (`ubuntu-24.04` or `ubuntu-24.04-arm`), `jobs`, `reps` and `time_limit` (the time limit of a job in minutes, as text, default `45`). It runs the offline self-test, the sweep and uploads the job's `out/` folder before anything is checked.
- `tests/test_forwardt.py` (the sweep, on generated data; the workflow also runs it as `python3 tests/test_forwardt.py`), `tests/test_forwardt_analyze.py` (the analysis, on generated data) and `tests/test_forwardt_registration.py` (the step of `scripts/check.py` that checks this folder).

## How a run is dispatched and recorded

The plan calls for a code test on each runner (`jobs` = `[1]` and `reps` = 4, so that the files are marked as smoke files, which the analysis sets aside and never pools), then three measurement runs of 6 jobs: one on `ubuntu-24.04-arm` (Neoverse-N2) and two on `ubuntu-24.04`, the two x86-64 runs from one commit. A dispatchable workflow must already exist on the default branch, so the runs are to be dispatched from a temporary branch of the public repository, as the `dsweep` runs were; each file records its commit. The branch the runs were dispatched from is named in the report (manifest key `branch`) and is kept for as long as the runs record its commits.

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

The plan is public, the code is written and tested on generated data, and the manifest is empty. `python forwardt/analyze.py` on the empty manifest reports that no run exists. Called without `--no-write`, it also writes `results.json` beside the manifest. Until a run is recorded, nothing here says what FAST costs on these loops.

## To check

```
python forwardt/analyze.py --verify
python forwardt/analyze.py --no-write      # prints the report and writes nothing
python3 tests/test_forwardt.py
```

`--verify` validates every stored `forwardt.json`, recomputes its ratios and intervals from the raw samples and recomputes the results file from the manifest; with an empty manifest it has nothing to verify and passes. `python scripts/check.py` runs it as a step, together with a guard on the plan: the sha256 of `forwardt/PLAN.md` must equal the one recorded in `scripts/check.py` and in `forwardt/analyze.py` and be the plan hash stored in every `forwardt.json` and result file, and every stored `forwardt.json` must lie in a folder that the manifest names. A missing analysis script, plan or manifest, an unreadable results file, or a results file missing while the manifest lists a run, fails the step.

## What it cannot show

Six hand-written loops, `int32` data, one compiler (clang 18.1.3 with libc++ 18, hardening mode FAST) at `-O2`, baseline x86-64 and AArch64: nothing about other compilers or flags, or about how often such a loop is hot in a real program. The compile-only sweep finds the functions these loops come from vectorized under FAST from clang 19.1.0 on; this folder times 18.1.3 only and says nothing about what a later compiler pays. In cache only (L1 and L2, no RAM). The runners are shared and GitHub draws each job's CPU model, so which models reach 3 jobs is not controlled; the Neoverse-N2 column would be one run of six jobs, whose intervals cannot show run-to-run spread. No hardware counters are read. The list of runs is kept by the author; the independent record is the Actions run list of the public repository.
