# Real programs that contain lost loops: plan, written before any run

Written Mon Oct 12 2026, 15:16 EDT, and committed before the first run of
`.github/workflows/realworld.yml`. No real-program number from this study exists when this file is
committed. Every later change is logged at the bottom, with the time, and says whether any timing
existed when it was made.

## The question

The kernels show that a loop which clang vectorizes with libc++ hardening off (NONE) and not with it
on (FAST) runs 2.8x to 8x slower in cache. Census 2 (`corpus/README.md`) shows that such loops exist
in numeric projects (444 of 4,968 vectorized loops in 25 projects; LightGBM, Draco, llama.cpp,
whisper.cpp, Spectra, tiny-dnn, Stockfish). Nobody here has timed a **whole real program that
contains them**. This study does: does the cost of a lost loop survive dilution by everything else a
program does?

What it will NOT say: anything about Google's 0.30% (a fleet average over services we cannot see).
A program's FAST/NONE ratio is reported per CPU model with its interval, never as confirming or
refuting that figure.

## Programs

Chosen from census 2 (projects with at least one lost loop) plus two controls with none. Each must
build from the census pin with clang-18 + libc++-18, run a deterministic fixed-input workload with no
network at run time, and need no model download over about 50 MB. The pins (commit, archive URL,
sha256, bytes) are the census pins in `corpus/projects2.json` and `programs/fmt_format/fetch.sh`,
copied into `realworld/programs.json`; `realworld/check.py` checks they still match.

Each program is a small driver written for this study (`realworld/drivers/`) that calls the
project's own library code. It generates its input from a fixed seed (no download), runs the workload
once untimed, then `iters` times inside a `CLOCK_MONOTONIC` window, and prints
`RESULT ns=<per iteration> iters=<n> checksum=<exact hash of the outputs> checksum_r=<hash of the
outputs rounded to 6 significant digits>`.

| row | project (pin) | workload, per iteration | lost loops it can reach (census 2, file:line) | why it is in |
|---|---|---|---|---|
| `lightgbm_default` | LightGBM 4.7.0 (8f7036f) | build a Dataset from a 20,000 x 28 numeric matrix, train 50 rounds of binary classification with default parameters (plus `num_threads=1 deterministic=true force_col_wise=true`), predict the training rows | dataset construction: `utils/common.h:643, 652` (via `LGBM_DatasetCreateFromMats`), `io/metadata.cpp:469` (labels) | the project with the most lost loops, run the way most users run it |
| `lightgbm_multiclass` | LightGBM, same binary | 8-class objective, 4 of 24 features categorical, bagging 0.8 every round, `force_row_wise=true`, 20 rounds | `objective/multiclass_objective.hpp:98` (every data row, every round), `treelearner/feature_histogram.cpp:373, 378` (categorical splits), `io/multi_val_dense_bin.hpp:47, 283` (row-wise bins, bagging copies) | documented options chosen BY THE AUTHOR to make lost loops run; labelled as such everywhere |
| `lightgbm_linear` | LightGBM, same binary | regression with `linear_tree=true` on 10,000 x 10, 30 rounds | `treelearner/linear_tree_learner.cpp:188, 297, 312, 315, 324` (297 is the per-row accumulation of the leaf's normal equations) | as above: an option chosen to run lost loops |
| `draco` | Draco 1.5.7 (8786740) | build a mesh from an in-memory triangle soup of a 160 x 160 torus (position, normal, texcoord; the builder de-duplicates values as Draco's own loaders do), encode it and the matching point cloud with `draco_encoder`'s defaults (quantization 11/10/8 bits, compression level 7 = speed 3), decode both | `attributes/point_attribute.cc:213` (de-duplication), `prediction_schemes/mesh_prediction_scheme_parallelogram_shared.h:62`, `entropy/ans.h:493`, `entropy/rans_symbol_decoder.h:108`, `kd_tree_attributes_encoder.cc:100, 203`, `kd_tree_attributes_decoder.cc:477`, `sequential_integer_attribute_encoder.cc:175`, `mesh_edgebreaker_traversal_valence_encoder.h:64` | graphics code, 12 distinct lost locations, a typical encode/decode |
| `tinydnn` | tiny-dnn (c0f576f, header-only, `CNN_SINGLE_THREAD`) | train a 64-256-256-10 fully connected network for 1 epoch over 512 fixed-seed samples (adagrad, batch 32, cross-entropy), predict all samples | `core/kernels/fully_connected_op_internal.h:65` (bias gradient, in the backward pass of every fully connected layer) | a lost loop inside the hottest kernel of the program |
| `spectra` | Spectra 1.2.0 (6841bcb) on Eigen 3.4.0 | top 8 eigenvalues of a fixed-seed dense symmetric 400 x 400 matrix and of a 20,000 x 20,000 sparse banded matrix (`SymEigsSolver`) | `Util/SelectionRule.h:215` (index fill when sorting Ritz values) | a lost loop that runs a few times per restart: expected cold |
| `meshopt` (control) | meshoptimizer 1.3 (9e1f07b) | on a 300 x 300 grid mesh with shuffled triangles: vertex remap, vertex-cache, overdraw and vertex-fetch optimization, simplification to 25 %, meshlets, index and vertex codecs | none (census 2: 0 lost, 0 checks added in the library) | numeric control from the same field as Draco |
| `fmt` (control) | {fmt} 11.0.2 (as `programs/fmt_format`) | format 20,000 seeded int64 and double values (the S2/S3 program) | none (census 1: 0 lost) | the existing program, now pooled |

Dropped before any build, and why:
- **Stockfish** (`bench`): its default network `nn-1a298aa575a0.nnue` is 98,511,183 bytes (over the
  ~50 MB limit), and both of its lost loops are outside `bench` (`Skill::pick_best` runs only with
  a skill level below 20; `tbprobe.cpp:1200` only with endgame tablebases).
- **whisper.cpp, llama.cpp**: need a model file (whisper's tiny model is about 75 MB at 16-bit; smaller files are quantized
  variants) and the ggml build, and one inference takes seconds per process; 320 processes per program per job would
  not fit a 25-minute job. Their lost loops (mel spectrogram, logit post-processing, batch setup)
  are named in the README as not timed.

If a program does not build or run after two attempts at the same fix, it is dropped and the reason
recorded here (task rule).

## Builds

clang-18, libc++-18 (Ubuntu noble apt), the project's flags: `-O2 -std=c++20 -stdlib=libc++`
(baseline x86-64, no `-march`; LightGBM `-std=c++17`, tiny-dnn `-std=c++14`, as in the census), the
census defines and include paths per project, `-pthread`. Library sources are compiled to objects,
archived with `ar`, and linked with the driver. Six builds per program:

- `none`: `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE`
- `fast`: `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST`
- `none_a64`, `fast_a64`: the same plus `-falign-loops=64` (the project's aligned pair)
- `none_g`, `fast_g`: the same as `none`/`fast` plus `-gline-tables-only`, used only for the profile.
  Whether their `.text` bytes equal those of `none`/`fast` is checked and reported.
- the A/A copy: the `none` binary copied to a second path; the run aborts if the sha256 differ.

Recorded per build: sha256, whole-binary `ud2` count (traps), compile time; per program: for every
census lost location in the program's sources, the number of "vectorized loop" remarks in NONE and in
FAST (`-Rpass=loop-vectorize`), so the lost loops are shown to be lost in these binaries too.

## Profile weight of the lost loops (run once per workflow run, in the build job)

Cachegrind (`valgrind --tool=cachegrind --cache-sim=no --demangle=no`) on `none_g` and `fast_g`,
once with `iters=1` and once with `iters=2`; every per-line count of the second minus the first is
one workload iteration (process start, input generation and the warm-up cancel). Two shares of the
iteration's executed instructions, in NONE and in FAST:

- **loop lines** (a lower bound): instructions attributed to the source lines of the census lost
  loops (file suffix and the loop's line range from `lost_loops.json`). It misses instructions
  inlined into the loop from elsewhere (for example libc++'s `operator[]`, attributed to `<vector>`).
- **containing functions** (an upper bound): instructions executed in the functions (mangled
  symbols) in which census 2 found a lost loop. It includes everything else those functions do.

Limits: instructions, not time; a vectorized loop executes fewer instructions per element than the
same loop scalar, so the NONE share understates its share of time in FAST; the input is the
author's. Cachegrind on the plain `none` and `fast` binaries (same two-run difference) gives the
instruction ratio FAST/NONE per iteration, printed beside the time ratio, labelled instructions.

## Timing (the project's method, harness/criteria-v3.json)

- Per job, per row: iterations calibrated once on the `none` binary to about 200 ms of timed work
  per process (minimum 1); then four ABBA pairs of 40 processes per side, one process per
  repetition, pinned with `taskset -c 1`, in this order: FAST/NONE, the byte-identical A/A
  (NONE/copy), aligned (`fast_a64`/`none_a64`), layout A/A (`none_a64`/`none`).
- Primary time: the in-binary timed window. Secondary, recorded for every process: its wall time
  measured by the harness (includes process start and input generation), pooled the same way and
  shown as a second column.
- Checksums: the exact checksum must be the same for every process of a row (NONE, FAST, aligned,
  copy). If only the rounded checksum matches, the row is timed and flagged "outputs differ in the
  last digits"; if neither matches, the row is reported as failed and not given a ratio.
- 4 jobs per run, 3 runs (12 jobs), all with the same inputs; a run is replaced only if it produced
  no results at all. If a run is over budget, the layout A/A pair is dropped from all later runs
  (and the change logged here); nothing else is changed after the first timing exists.
- Pooling: per CPU model (exact `lscpu` model string) with `harness/pool.py`'s two-level bootstrap
  (`pair_stat`: geometric mean of per-job median ratios; jobs resampled, then repetitions within each
  job; 2000 resamples; splitmix64 seeded from the CPU model and a statistic id), imported, not edited.
  A CPU model needs at least 3 jobs for a reading (criteria-v3 `minimum_jobs`); models with fewer
  are listed with their job count only. An all-runners pooled line is shown as descriptive.

## Rules for the claims (fixed now)

For a row on a CPU model with at least 3 jobs, with h = the pooled half-width of that row's own
byte-identical A/A, in percent:

- **detectably slower** if the pooled FAST/NONE interval's lower end is above 1 + h/100 in BOTH
  columns (as compiled and aligned);
- **detectably faster** if the upper end is below 1 - h/100 in both columns;
- otherwise **not detectable**: reported as "at most X %", X = max(0, 100 x (upper end - 1) over the
  two columns, h): never a bound below the row's own noise floor;
- one column only: reported as not detectable, with the column that crossed named.

The layout A/A (NONE against NONE aligned) is reported beside every row as the size of a pure
code-placement change; no rule reads it. Whole-program results are never compared to 0.30 %.

## What is expected (written before any build or run)

From the census evidence alone (trip counts and where the loops sit), not from any measurement:

| row | expected FAST/NONE (time) | detectable? | lost-loop share of NONE instructions (containing functions) | reasoning |
|---|---|---|---|---|
| `lightgbm_default` | 0.99 to 1.03 | probably not | under 1 % | its lost loops run once per Dataset (trip count 1 for the matrix list, n for labels); training time is histograms and split finding, which keep their code |
| `lightgbm_multiclass` | 1.00 to 1.06 | maybe | 1 to 10 % | the gradient loop runs for every row and round but its trip count is the class count (8), one vector iteration in NONE; categorical-split loops run only when a split improves |
| `lightgbm_linear` | 1.02 to 1.20 | yes | 10 to 40 % | line 297 accumulates the normal equations for every row in every leaf; its trip count is the leaf's feature count plus one (small), so the loss per call is below the kernels' 2.8x |
| `draco` | 0.99 to 1.04 | probably not | under 2 % | most lost loops run over num_components (2 or 3: too short for a vector iteration even in NONE) or once per attribute; the de-duplication loop is O(points) beside hashing work |
| `tinydnn` | 1.00 to 1.10 | maybe, but not from the lost loop | under 2 % | the bias-gradient loop is O(out) per sample beside the O(in x out) weight gradient; any cost would come from the other checks in tiny-dnn's scalar loops |
| `spectra` | 0.99 to 1.02 | no | under 0.5 % | Ritz-value sorting is O(ncv) per restart; the matrix products run in Eigen, which uses no libc++ containers |
| `meshopt` (control) | 0.99 to 1.01 | no | 0 (no lost loop) | no lost loop and no checks in the library; only the driver's few vector accesses |
| `fmt` (control) | 0.97 to 1.02 | no, or faster from placement | 0 (no lost loop) | S3 measured 0.97 to 1.02 on single jobs, both signs |

Overall expectation: the lost loops exist in these programs but carry a small share of their work,
so whole-program costs stay within a few percent except where an option puts a lost loop on the hot
path (`lightgbm_linear`). An expectation is counted right if the pooled ratio of every CPU model with
at least 3 jobs lies in the stated range and the detectable/not call matches.

## Budget

At most 10 workflow runs, each at most 25 minutes: one probe run (builds, profile, one native run of
each build for checksums; no timing pairs), at most two fix runs, three measurement runs. Downloads:
apt packages (clang-18, libc++-18-dev, libc++abi-18-dev, valgrind, binutils) and the pinned archives
listed in `realworld/programs.json` with their sha256 and sizes.

## Changes after this file was committed

- Mon Oct 12 2026, 15:55 EDT, after build run 38297816088 and BEFORE any timing
  pair existed. (1) LightGBM's six builds took 20.5 minutes to compile and the job hit its 24-minute
  limit before uploading, so LightGBM is now built in two jobs: NONE, FAST and the two profile
  builds in one (with the profile), the aligned pair in another. Same flags, same sources. (2) The
  probe measured one NONE iteration at 377 ms (`lightgbm_default`) and 390 ms
  (`lightgbm_multiclass`); with the untimed warm-up each process took 0.75 s, which would not fit
  320 processes per row in a job. Their row counts are halved (20,000 -> 10,000 and 10,000 -> 5,000
  rows), to about 190 ms per iteration; nothing else in either workload changes. Only NONE times
  were used for this. What was also seen before this change (and is written down so it is not
  hidden): Cachegrind instruction ratios FAST/NONE (LightGBM 1.12 / 1.16 / 1.26, Draco 1.16,
  tiny-dnn 1.72, Spectra 1.00, meshoptimizer 1.00, fmt 1.00) and the profile shares; every census
  lost location of these programs also loses vectorization in these builds (LightGBM 38 of 38,
  Draco 12 of 12, tiny-dnn 2 of 2, Spectra 1 of 1). The expectations table above is NOT changed.
- Mon Oct 12 2026, about 16:21 EDT, after build run 38300799193, still before any timing: the
  `--builds` option never reached `build.py` (a workflow edit that did not apply), so both LightGBM
  jobs built all six ways again and hit the limit. Fixed, and the builds are now six jobs (LightGBM:
  NONE+FAST, the two profile builds, the aligned pair; Draco: four builds, the aligned pair; the small
  programs) followed by one profile job. Same flags, sources and workloads.
- Mon Oct 12 2026, 16:23 EDT: run 38303777600 was not started by GitHub ("recent account payments
  have failed or your spending limit needs to be increased"). Work stops here until the billing is
  fixed; three runs of the ten are used, none of them timed anything.
