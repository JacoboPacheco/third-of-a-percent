# Real programs that contain lost loops

**Status (Tue Oct 13 2026): built, profiled and timed.** Build run 38402534350; six measure runs (38405426737, 38405438115, 38405450413, 38410903032, 38410918561, 38410932862), 24 distinct jobs, pooled per CPU model (`results/realworld-pooled/realworld.json`): AMD EPYC 7763 16 jobs, AMD EPYC 9V45 5 jobs, AMD EPYC 9V74 3 jobs; each has the 3 jobs a reading needs. Detectably slower with the checks on (as compiled and aligned columns): on 7763, 5 of the 6 workloads with lost loops (1.2% to 7.5%); on 9V74, 4 of 6 (0.7% to 7.1%); on 9V45, 3 of 6 (2.3% to 5.4%). The rest were not detectable above that model's own noise floor (details: `claims-audit/CLAIMS-3-recheck.md`). The plan's expectations are checked against EPYC 7763 and held for 5 of 8 rows (verdict page, details, Table 11).

Pooling note: an earlier pooling counted each job twice (every job's result sat in the repository in two download copies), which doubled the job counts and narrowed the intervals; `pool_rw.py` now counts each distinct file once. Point ratios did not change.

The plan, the rules for every claim and the expectations were committed before the first run:
[PLAN.md](PLAN.md) (changes after that are logged at its bottom).

## What is here

Six workloads from four projects on the census lists (the first six rows) and two controls, each driven by a small driver in [drivers/](drivers/) that calls
the project's own code on a fixed-seed input (no download at run time):

| row | project | lost loops it reaches (census 2) |
|---|---|---|
| `lightgbm_default` | LightGBM 4.7.0, binary classification, defaults | dataset construction only |
| `lightgbm_multiclass` | LightGBM, 8 classes, categorical features, bagging, row-wise (options chosen by the author to run lost loops) | gradients, categorical splits, row-wise bins |
| `lightgbm_linear` | LightGBM, `linear_tree=true` (chosen to run lost loops) | the leaf normal-equation accumulation |
| `draco` | Draco 1.5.7, mesh and point-cloud encode and decode with `draco_encoder` defaults | 12 locations |
| `tinydnn` | tiny-dnn, train a 64-256-256-10 MLP one epoch | bias gradient in every fully connected layer |
| `spectra` | Spectra 1.2.0 on Eigen 3.4.0, top-8 eigenvalues, dense and sparse | Ritz-value sorting |
| `meshopt` (control) | meshoptimizer 1.3, the usual optimization pipeline | none |
| `fmt` (control) | {fmt} 11.0.2, the S2/S3 program | none |

Stockfish (98.5 MB network, lost loops outside `bench`), whisper.cpp and llama.cpp (model files,
seconds per inference) were dropped before any build; PLAN.md says why.

## What the build and profile runs show (instructions, not time)

Probe records: [results/realworld-probe-38300799193/](../results/realworld-probe-38300799193/)
(Draco and the small programs, build run 38300799193, the current workloads) and
`lightgbm-run-38297816088.log.txt` there (LightGBM, build run 38297816088, whose job finished its
profile but hit the time limit before uploading; its `lightgbm_default` and `lightgbm_multiclass`
rows used twice the rows of the current plan).

| row | instructions FAST/NONE per iteration | instructions on the lost loops' own lines, NONE / FAST | in the functions holding a lost loop, NONE / FAST | ud2 traps NONE / FAST | census lost locations also lost in these builds |
|---|---|---|---|---|---|
| `lightgbm_default` | 1.117 | 0.001% / 0.003% | 0.82% / 1.21% | 3 / 1148 | 38 of 38 (LightGBM) |
| `lightgbm_multiclass` | 1.157 | 0.72% / 0.64% | 3.30% / 3.38% | same binary | |
| `lightgbm_linear` | 1.264 | 6.25% / 5.03% | 15.41% / 23.39% | same binary | |
| `draco` | 1.158 | 0.24% / 0.49% | 3.98% / 3.85% | 20 / 440 | 12 of 12 |
| `tinydnn` | 1.721 | 0.03% / 0.07% | 16.36% / 9.96% | 3 / 159 | 2 of 2 |
| `spectra` | 1.000 | 0.0002% / 0.0003% | 0.0006% / 0.0009% | 0 / 27 | 1 of 1 |
| `meshopt` (control) | 1.000 | no lost loop | no lost loop | 0 / 2 | none listed |
| `fmt` (control) | 1.001 | no lost loop | no lost loop | 0 / 7 | none listed |

What these numbers say, and only that:

- Every census lost loop in these programs also loses vectorization in these builds (clang's own
  remarks, NONE against FAST), and every program's outputs are identical between NONE and FAST
  (exact checksums).
- In the default workloads the lost loops carry a tiny share of the executed instructions (about
  0.5 % or less on their own lines, Spectra and `lightgbm_default` near zero). Only `lightgbm_linear`, an
  option chosen to run them, puts about 5 to 6 % of the instructions on lost-loop lines.
- The extra instructions FAST executes mostly come from checks elsewhere, not from the lost loops, in every program except possibly `lightgbm_linear`, where the functions that hold its lost loops take up to 53.7 % of the extra instructions (by the functions share; 0.4 % by the lines share):
  tiny-dnn runs 1.72x the instructions while 0.03 % (NONE) sit on its lost loop's lines; its checks sit in
  scalar loops that were never vectorized. The kernels showed that instruction ratios and time
  ratios can differ a lot, so none of this predicts the time cost.
- The "functions" share is probably an upper bound (everything else those functions do counts too), but only some of the functions were matched in the profile (LightGBM 3, 6 and 4 of 165, Draco 13 of 64, tiny-dnn 1 of 2, Spectra 1 of 4), so a lost loop inlined elsewhere is missed on that side; the
  "lines" share is a lower bound (code inlined into the loop from libc++ headers is attributed to
  the header). For LightGBM the `-gline-tables-only` profile builds do not have the same `.text`
  bytes as the timed builds, so its shares are approximate; for Draco and the small programs they do.

## What is NOT shown

- Which checks cost the time. The tables show that the lost loops hold little of the executed instructions in most programs and that FAST still costs 1.2% to 7.5% in five of them on EPYC 7763 (fewer programs are detectable on the other two models); that is consistent with the cost sitting in checks elsewhere, not a measured decomposition.
- Profile-guided optimization (none was used in this timing; the separate `pgo/` column, trained on the timed input, did not make the cost vanish in most rows on EPYC 7763), a representative sample (the programs were picked because they contain lost loops), agreement across CPU models (the five-of-six result holds on EPYC 7763 only; see the status line).
- Anything about Google's 0.30 %: a fleet average over services that cannot be inspected from outside.
- One toolchain (clang 18, libc++ 18, `-O2`, baseline x86-64, no `-DNDEBUG`: the census flags;
  release builds of these projects usually define `NDEBUG`, which removes their own `assert`s,
  Eigen's among them, from both builds).
- Inputs chosen by the author (fixed seeds, sizes picked so one iteration takes about 100 to 200 ms);
  two LightGBM rows use options picked to run the lost loops and are labelled so.
- Shared GitHub runners whose CPU model is drawn by luck (the timing pools per CPU model).

## Checking it

`python realworld/check.py` runs on a laptop without a compiler: the pins against the census, every
job's raw samples (counts, ABBA order, checksums, the A/A copy), the pooled file recomputed from the
raw samples with `harness/pool.py`'s two-level bootstrap (exact match), the README tables against
`realworld/report.py`, and the tests in `realworld/tests/` (24). With no pooled file yet it checks
the pins and runs the tests.

<!-- realworld:tables:start -->
**AMD EPYC 7763 64-Core Processor (16 jobs, 6 runs)**

| row | FAST/NONE, time [95%] | loops aligned [95%] | own A/A half-width | layout A/A (NONE aligned / NONE) | process wall time FAST/NONE | reading |
|---|---|---|---|---|---|---|
| lightgbm_default | 1.018 [1.017, 1.018] | 1.012 [1.011, 1.012] | 0.09% | 1.005 [1.003, 1.006] | 1.018 [1.017, 1.018] | FAST detectably slower in both columns (as compiled 1.0176, aligned 1.0115; A/A half-width 0.09%) |
| lightgbm_multiclass (options chosen to run lost loops) | 1.034 [1.032, 1.036] | 1.034 [1.032, 1.035] | 0.11% | 1.002 [1.001, 1.003] | 1.033 [1.032, 1.036] | FAST detectably slower in both columns (as compiled 1.0336, aligned 1.0336; A/A half-width 0.11%) |
| lightgbm_linear (options chosen to run lost loops) | 1.037 [1.036, 1.038] | 1.045 [1.044, 1.045] | 0.06% | 0.996 [0.995, 0.996] | 1.036 [1.035, 1.037] | FAST detectably slower in both columns (as compiled 1.0368, aligned 1.0446; A/A half-width 0.06%) |
| draco | 1.075 [1.074, 1.077] | 1.068 [1.066, 1.069] | 0.14% | 0.996 [0.995, 0.997] | 1.070 [1.068, 1.071] | FAST detectably slower in both columns (as compiled 1.0754, aligned 1.0678; A/A half-width 0.14%) |
| tinydnn | 1.029 [1.028, 1.030] | 1.036 [1.033, 1.037] | 0.16% | 1.001 [0.999, 1.002] | 1.029 [1.028, 1.031] | FAST detectably slower in both columns (as compiled 1.0291, aligned 1.0358; A/A half-width 0.16%) |
| spectra | 1.003 [1.002, 1.005] | 1.000 [0.999, 1.000] | 0.14% | 1.004 [1.003, 1.005] | 1.003 [1.002, 1.005] | not detectable: at most 0.48% (only the as compiled column crossed the A/A floor) |
| meshopt (control) | 1.000 [0.995, 1.004] | 0.998 [0.993, 1.002] | 0.37% | 1.001 [0.997, 1.004] | 1.000 [0.996, 1.003] | not detectable: at most 0.39% |
| fmt (control) | 0.985 [0.982, 0.987] | 0.944 [0.937, 0.955] | 0.16% | 1.023 [1.011, 1.033] | 0.985 [0.983, 0.988] | FAST detectably faster in both columns (as compiled 0.9846, aligned 0.9439; A/A half-width 0.16%) |

**AMD EPYC 9V45 96-Core Processor (5 jobs, 3 runs)**

| row | FAST/NONE, time [95%] | loops aligned [95%] | own A/A half-width | layout A/A (NONE aligned / NONE) | process wall time FAST/NONE | reading |
|---|---|---|---|---|---|---|
| lightgbm_default | 1.023 [1.017, 1.030] | 1.053 [1.043, 1.063] | 0.67% | 0.997 [0.993, 1.001] | 1.024 [1.019, 1.031] | FAST detectably slower in both columns (as compiled 1.0233, aligned 1.0529; A/A half-width 0.67%) |
| lightgbm_multiclass (options chosen to run lost loops) | 1.043 [1.038, 1.049] | 1.041 [1.035, 1.048] | 0.85% | 1.011 [1.004, 1.019] | 1.042 [1.038, 1.046] | FAST detectably slower in both columns (as compiled 1.0426, aligned 1.0407; A/A half-width 0.85%) |
| lightgbm_linear (options chosen to run lost loops) | 1.007 [1.002, 1.011] | 1.078 [1.074, 1.084] | 0.85% | 1.009 [1.005, 1.013] | 1.006 [1.002, 1.011] | not detectable: at most 8.38% (only the aligned column crossed the A/A floor) |
| draco | 1.053 [1.047, 1.058] | 1.054 [1.048, 1.060] | 0.54% | 1.000 [0.993, 1.007] | 1.049 [1.043, 1.054] | FAST detectably slower in both columns (as compiled 1.0529, aligned 1.0540; A/A half-width 0.54%) |
| tinydnn | 0.934 [0.925, 0.941] | 1.186 [1.176, 1.193] | 0.56% | 1.025 [1.017, 1.034] | 0.939 [0.931, 0.947] | not detectable: at most 19.33% (only the as compiled column crossed the A/A floor) |
| spectra | 1.013 [1.006, 1.021] | 1.001 [0.993, 1.007] | 0.39% | 1.063 [1.057, 1.067] | 1.013 [1.005, 1.020] | not detectable: at most 2.08% (only the as compiled column crossed the A/A floor) |
| meshopt (control) | 1.001 [0.985, 1.014] | 1.000 [0.988, 1.013] | 1.14% | 0.997 [0.984, 1.015] | 1.001 [0.988, 1.012] | not detectable: at most 1.39% |
| fmt (control) | 0.983 [0.978, 0.991] | 0.994 [0.988, 1.000] | 0.61% | 0.998 [0.992, 1.005] | 0.984 [0.979, 0.991] | not detectable: at most 0.61% (only the as compiled column crossed the A/A floor) |

**AMD EPYC 9V74 80-Core Processor (3 jobs, 3 runs)**

| row | FAST/NONE, time [95%] | loops aligned [95%] | own A/A half-width | layout A/A (NONE aligned / NONE) | process wall time FAST/NONE | reading |
|---|---|---|---|---|---|---|
| lightgbm_default | 1.010 [1.007, 1.013] | 1.007 [1.005, 1.009] | 0.13% | 1.001 [1.000, 1.003] | 1.009 [1.007, 1.011] | FAST detectably slower in both columns (as compiled 1.0095, aligned 1.0073; A/A half-width 0.13%) |
| lightgbm_multiclass (options chosen to run lost loops) | 1.036 [1.034, 1.038] | 1.038 [1.036, 1.039] | 0.17% | 0.996 [0.995, 0.998] | 1.035 [1.034, 1.036] | FAST detectably slower in both columns (as compiled 1.0357, aligned 1.0375; A/A half-width 0.17%) |
| lightgbm_linear (options chosen to run lost loops) | 1.031 [1.030, 1.032] | 1.026 [1.025, 1.026] | 0.08% | 1.002 [1.001, 1.002] | 1.030 [1.030, 1.031] | FAST detectably slower in both columns (as compiled 1.0308, aligned 1.0256; A/A half-width 0.08%) |
| draco | 1.071 [1.070, 1.073] | 1.068 [1.065, 1.072] | 0.13% | 0.999 [0.997, 1.002] | 1.066 [1.065, 1.068] | FAST detectably slower in both columns (as compiled 1.0713, aligned 1.0682; A/A half-width 0.13%) |
| tinydnn | 0.994 [0.980, 1.012] | 0.999 [0.989, 1.009] | 0.57% | 1.002 [0.997, 1.008] | 0.996 [0.988, 1.006] | not detectable: at most 1.23% |
| spectra | 1.015 [1.014, 1.016] | 1.001 [0.998, 1.003] | 0.15% | 1.015 [1.014, 1.017] | 1.014 [1.012, 1.016] | not detectable: at most 1.63% (only the as compiled column crossed the A/A floor) |
| meshopt (control) | 1.003 [1.000, 1.005] | 0.999 [0.995, 1.002] | 0.37% | 0.996 [0.994, 0.999] | 1.003 [1.001, 1.005] | not detectable: at most 0.50% |
| fmt (control) | 0.981 [0.977, 0.984] | 0.993 [0.991, 0.995] | 0.25% | 0.985 [0.982, 0.988] | 0.981 [0.978, 0.984] | FAST detectably faster in both columns (as compiled 0.9807, aligned 0.9928; A/A half-width 0.25%) |

**All runners pooled (24 jobs; descriptive, mixes CPU models, no reading)**

| row | FAST/NONE, time [95%] | loops aligned [95%] | own A/A half-width | layout A/A (NONE aligned / NONE) | process wall time FAST/NONE | reading |
|---|---|---|---|---|---|---|
| lightgbm_default | 1.018 [1.016, 1.020] | 1.019 [1.013, 1.027] | 0.16% | 1.003 [1.001, 1.004] | 1.018 [1.016, 1.020] | - |
| lightgbm_multiclass (options chosen to run lost loops) | 1.036 [1.034, 1.038] | 1.036 [1.034, 1.038] | 0.20% | 1.003 [1.001, 1.006] | 1.035 [1.033, 1.037] | - |
| lightgbm_linear (options chosen to run lost loops) | 1.030 [1.024, 1.034] | 1.049 [1.043, 1.056] | 0.18% | 0.999 [0.997, 1.002] | 1.029 [1.024, 1.034] | - |
| draco | 1.070 [1.066, 1.074] | 1.065 [1.062, 1.068] | 0.14% | 0.997 [0.995, 0.999] | 1.065 [1.061, 1.069] | - |
| tinydnn | 1.004 [0.987, 1.019] | 1.061 [1.038, 1.088] | 0.20% | 1.006 [1.002, 1.010] | 1.006 [0.990, 1.020] | - |
| spectra | 1.007 [1.004, 1.010] | 1.000 [0.998, 1.002] | 0.12% | 1.017 [1.008, 1.027] | 1.007 [1.004, 1.009] | - |
| meshopt (control) | 1.000 [0.996, 1.004] | 0.998 [0.994, 1.003] | 0.34% | 0.999 [0.996, 1.004] | 1.001 [0.997, 1.004] | - |
| fmt (control) | 0.984 [0.982, 0.986] | 0.960 [0.951, 0.973] | 0.18% | 1.013 [1.004, 1.021] | 0.984 [0.982, 0.987] | - |

**Instructions and where the lost loops sit** (Cachegrind, one workload iteration, the build run's binaries; instructions, not time)

| row | instructions FAST/NONE | lost-loop lines, share of NONE / FAST | functions holding a lost loop, share of NONE / FAST | functions found / listed | ud2 traps NONE / FAST | census lost locations lost here too |
|---|---|---|---|---|---|---|
| lightgbm_default | 1.0898 | 0.001% / 0.002% | 0.621% / 0.937% | 3 / 165 | 3 / 1148 | 38 of 38 |
| lightgbm_multiclass | 1.1114 | 0.507% / 0.467% | 2.476% / 2.620% | 6 / 165 | 3 / 1148 | 38 of 38 |
| lightgbm_linear | 1.2638 | 6.252% / 5.033% | 15.410% / 23.393% | 4 / 165 | 3 / 1148 | 38 of 38 |
| draco | 1.1581 | 0.242% / 0.493% | 3.976% / 3.849% | 13 / 64 | 20 / 440 | 12 of 12 |
| tinydnn | 1.7211 | 0.030% / 0.069% | 16.356% / 9.963% | 1 / 2 | 3 / 159 | 2 of 2 |
| spectra | 1.0000 | 0.000% / 0.000% | 0.001% / 0.001% | 1 / 4 | 0 / 27 | 1 of 1 |
| meshopt | 1.0000 | 0.000% / 0.000% | 0.000% / 0.000% | 0 / 0 | 0 / 2 | 0 of 0 |
| fmt | 1.0008 | 0.000% / 0.000% | 0.000% / 0.000% | 0 / 0 | 0 / 7 | 0 of 0 |

<!-- realworld:tables:end -->
