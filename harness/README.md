# harness/

The measurement code and the rule files it reads. A job on a GitHub Actions runner calls `run.py`, which builds and times the
kernels and writes one `results.json`; `pool.py` then pools the jobs of one CPU model into a `pooled.json`, and the page, the
checks and the notes read that file. The Python here is standard library only, except `pool.py`, which uses numpy.

## Modules

| file | what it does |
|---|---|
| `run.py` | The measurement. Builds every kernel and program with the check off (NONE), on (FAST) and with `-fno-vectorize` (NOVEC), plus a `-falign-loops=64` copy of NONE and FAST; times the pairs in alternating order, one process per repetition pinned to one CPU; records binary hashes, trap counts, clang's vectorization remark, the assembly, the loop placement and Cachegrind instruction counts; writes `results.json` and `details.json`. |
| `pool.py` | The v3 verdict. Pools every job of one CPU model (across runs) with a two-level bootstrap and applies the written rules per CPU model; writes `pooled.json`. |
| `pool_check.py` | An independent recomputation of a sample of the numbers in a `pooled.json`, in plain Python without numpy and without importing `pool.py` or `stats.py`. It samples only CPU models with at least the minimum number of jobs. |
| `stats.py` | The ratio of two medians and its percentile-bootstrap 95% interval, and the half-width of an interval in percent. `pool.py` uses its percentile rule. |
| `placement.py` | Reads `objdump` output and records where each loop of a kernel sits: start, length, offset in a 64-byte line, number of 64-byte windows touched, whether it holds a vector instruction. |
| `asm.py` | Cuts one function out of `objdump` output, counts its check traps (`ud2` on x86-64, `brk` on AArch64) and diffs the NONE and FAST assembly. |
| `remarks.py` | Reads clang's loop-vectorize remarks for the one loop each kernel marks. |
| `cachegrind.py` | Reads a Cachegrind output file and returns the instruction count (`Ir`) of one kernel function: instructions, not time. |
| `programs.py` | The two real programs (what they are, how they are pinned) and the arithmetic of their rows, such as the "consistent with at most X%" bound and the per-iteration instruction count. |
| `schema.py` | Checks a `results.json`, a `combined.json` or a `pooled.json` against its schema, key by key, with no third-party library. |
| `verdict.py` | The per-job verdict: its form (MAP, HOLDS_EVERYWHERE or INCONCLUSIVE) and its one-line sentence, from a `results.json` and a criteria file. Under `criteria-v3.json` this is the informational per-job reading, not the verdict. |
| `combine.py` | The earlier page-level line across the jobs of one workflow run (the criteria-v2 reading), kept for the runs that were made under it. |

## Rule files

| file | what it holds |
|---|---|
| `criteria.json` | Version 1: the A/A ceiling, the forward-loop limit, the lost-loop minimum, 20 repetitions per side. |
| `criteria-v2.json` | Version 2: the same limits, plus the second pair built with `-falign-loops=64`, the layout A/A, and the per-job placement-sensitive rule. |
| `criteria-v3.json` | Version 3: 40 repetitions per side, pooling per CPU model, the two-level bootstrap, the placement-sensitive rule on the pooled interval, and the per-CPU-model verdict. Its changelog says why it differs from version 2. |

## Which interval is which

Three intervals appear in the stored files and in the notes. They share a name ("95% interval") and a half-width formula
(`(hi - lo) / 2 * 100`), and differ in what they resample.

| | where it is stored | resamples | what varies | what it leaves out |
|---|---|---|---|---|
| per-job `ci95` | `controls`, `cells[]`, `cells[].aligned`, `programs[]` in each job's `results.json` | 10,000, each side drawn independently; positions 250 and 9,749 of the sorted ratios; seed 20261011 (`stats.py`) | the repetitions of one job | job-to-job spread: every repetition comes from one machine in one job |
| pooled `ci95` | each statistic in `pooled.json` | 2,000; positions 50 and 1,949 of the sorted ratios; a seed per statistic and stream, taken from a hash of the CPU model and the statistic's id (`pool.py`) | first the jobs of the CPU model (drawn with replacement), then, inside each drawn job, the repetitions of each side | nothing it can see: it contains both levels |
| check interval | printed by `pool_check.py`, never stored | 4,000, Python's `random.Random(7)` | the same two levels, in a separate implementation | it is a cross-check; it must agree with the pooled interval to within the tolerance named in that file |

The pooled ratio is the geometric mean over jobs of each job's ratio of medians (`median(FAST) / median(NONE)` inside the job).
The verdict words and the placement-sensitive rule read the pooled statistics, and so do the ratios the page quotes; the
per-job `ci95` is kept as the record of one job, and its job-level `verdict` is informational under `criteria-v3.json`.

Repetitions per side come from the criteria file the run names: `reps_per_side` is 20 in `criteria.json` and
`criteria-v2.json` and 40 under `v3.timing` in `criteria-v3.json`. `run.py` reads it and stores the value it used as
`reps_per_side` in `details.json`. The docstrings of `stats.py` (20 timings per side), `run.py` and `programs.py` (20 processes
per side) describe the original design; for a run under `criteria-v3.json`, `v3.timing` and `v3.pooling` govern, and the
`design.timing` block of that file still lists the earlier 20 and 10,000. The 10,000 resamples of `stats.py` are still what
produces the per-job interval; the pooled interval uses 2,000.

## Commands

```
python harness/pool.py <out.json> <results.json | dir> [...]   # pool jobs into a pooled.json
python harness/pool_check.py <pooled.json>                     # independent recomputation of a sample
python harness/schema.py <results.json> [...]                  # validate against the schema
python harness/verdict.py [results.json]                       # print the per-job form and line
python harness/combine.py <dir>                                # the earlier page-level line for one run
```

`run.py` needs clang 18, libc++ 18 and valgrind, so it runs on the Actions runner (`.github/workflows/measure.yml`); its
docstring lists the options.
