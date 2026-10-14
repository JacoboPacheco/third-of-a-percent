# Census 2: pre-registration

Written and committed before the first census-2 compile. Anything changed after the first run is
listed at the bottom under "Changes after the first run", with the reason.

## Why a second census

Census 1 (run 38259934735, 19 libraries: parsers, JSON/YAML/XML, compression, containers,
logging) found 1 of 593 vectorized loops (0.17%) lost under libc++ FAST hardening. The kernels
lose 3 to 8x in cache on reverse, stride-2 and matrix-multiply loops that index a `std::vector`
with `operator[]`. Library code of the census-1 kind rarely has such loops. The question for
census 2: **in code whose main work is numeric loops, how many vectorized loops are lost under
FAST?** The list below is chosen for where such loops are likely to live; it is fixed here,
before compiling, so the result cannot steer the selection.

## Selection rule

A project is in when all of these hold:

1. Its main work is numeric or array loops, in one of: physics and game code; graphics and
   geometry; numeric, scientific, image and signal processing; machine learning (training,
   inference, vector search); compression written with C++ containers.
2. It is C++ (not C), open source, and builds from one pinned archive (plus pinned archives of
   its own submodules) with the apt toolchain only: no CUDA, no GPU SDK, no system libraries.
3. Its library translation units (tests, tools, examples, other platforms excluded) fit the
   compile budget (about 560 translation units in total, three shards).

Header-only libraries are compiled through a small driver in `corpus/drivers/` that calls the
operations their README shows. Drivers are written before the first run and changed afterwards
only to fix a compile error.

## The list (25 projects)

Each is pinned by commit, with the sha256 and size of every download, in `corpus/projects2.json`.

| # | project | version | category | why it is in | compiled |
|---|---|---|---|---|---|
| 1 | Box2D | 2.4.2 | physics and game | last C++ Box2D (v3 is C); contact solver loops | 45 TUs |
| 2 | JoltPhysics | 5.6.0 | physics and game | production 3D physics: broad/narrow phase, solver | 137 TUs |
| 3 | Recast/Detour | 1.6.0 | physics and game | navmesh voxelization over grids and spans, crowds | 26 TUs |
| 4 | ozz-animation | 0.17.0 | physics and game | skeletal sampling and blending; offline builders on std::vector | 40 TUs |
| 5 | EnTT | 3.16.0 | physics and game | entity-component system, sparse sets indexed by entity | driver |
| 6 | Stockfish | sf_19 | physics and game | chess engine: move generation and NNUE over arrays | 26 TUs |
| 7 | meshoptimizer | 1.3 | graphics and geometry | vertex/index buffer optimization and simplification | 21 TUs |
| 8 | earcut.hpp | 3.2.4 | graphics and geometry | polygon triangulation over std::vector | driver |
| 9 | delaunator-cpp | 0.4.0 | graphics and geometry | Delaunay over std::vector<double>, computed indices | driver |
| 10 | nanoflann | 1.10.0 | graphics and geometry | k-d tree, distance loops over dimensions | driver |
| 11 | nanort | release 2024-11-10 | graphics and geometry | ray-tracing BVH build and traversal | driver |
| 12 | Draco | 1.5.7 | graphics and geometry | mesh compression: quantization, prediction, entropy coding | 129 TUs |
| 13 | Imath | 3.2.3 | graphics and geometry | OpenEXR's math: matrix algorithms, half floats | 6 TUs |
| 14 | tinyrenderer | master 2026-07-29 | graphics and geometry | application code: rasterizer over a std::vector depth buffer | 4 TUs |
| 15 | xtensor (+ xtl) | 0.27.1 | numeric, image and signal | n-dimensional arrays, element-wise and reductions | driver |
| 16 | Spectra (+ Eigen 3.4.0) | 1.2.0 | numeric, image and signal | Eigen-based eigenvalue solver | driver |
| 17 | pocketfft | cpp 2026-06-30 | numeric, image and signal | the FFT used by NumPy/SciPy | driver |
| 18 | CImg | 3.7.6 | numeric, image and signal | image filters, convolution, resizing | driver |
| 19 | LightGBM (+ fmt, fast_double_parser, Eigen, nanoarrow at its submodule commits) | 4.7.0 | machine learning | histogram and split loops over std::vector | 35 TUs |
| 20 | tiny-dnn | master 2018-10-23 | machine learning | conv and dense layers over std::vector<float> | driver |
| 21 | llama.cpp (C++ `src/*.cpp` only) | v0.6.0 | machine learning | sampling, tokenizer, KV cache, loading | 32 TUs |
| 22 | whisper.cpp (C++ `src/` only) | v1.9.5 | machine learning | mel spectrogram, FFT, decoding over std::vector<float> | 2 TUs |
| 23 | hnswlib | 0.9.0 | machine learning | vector search: distance loops, graph walks | driver |
| 24 | Annoy | 1.17.3 | machine learning | vector search: split and distance loops | driver |
| 25 | kanzi-cpp | 2.6.0 | compression | BWT, LZ, ROLZ, ANS, Huffman over buffers | 42 TUs |

Considered and not selected (reason fixed now):

- xgboost core: needs the dmlc-core submodule and generated build configuration; LightGBM stands
  in for tree-based ML.
- Armadillo: no pinned archive the fetcher can use (its GitHub mirror is empty; releases are
  `.tar.xz` on SourceForge). Blaze: hosted on Bitbucket. xtensor stands in for array libraries.
- dlib: its library is one translation unit (`dlib/all/source.cpp`) that pulls in GUI,
  networking and image I/O; libigl: header-only and very heavy to compile. Spectra stands in for
  Eigen-based solvers.
- stb, h3, zstd, lz4: C, not C++. Box2D v3: C.
- Bullet: over 300 library translation units; JoltPhysics and Box2D cover physics.
- OpenEXR: needs libdeflate and generated configuration; its math library Imath is in.
- llama.cpp `src/models/*.cpp` (157 per-architecture graph builders) and ggml (C): compile
  budget and language; the 32 core C++ files are in.
- Kernels of census 1 are not repeated as projects; they stay the control.

## Configurations

Each configuration builds every translation unit twice, libc++ hardening NONE and FAST:

- **baseline** (primary): exactly census 1's command, `clang++-18 -O2 -std=c++20 -stdlib=libc++`
  with the loop-vectorize remarks and optimization records, baseline x86-64 (SSE2). Census 1 and
  census 2 baseline are combined into one table.
- **avx2** (sensitivity, labelled as such): the same plus `-march=x86-64-v3`. Project defines
  stay the same (for example Stockfish keeps `USE_SSE2`), so only the compiler's target changes.

`NDEBUG` is not defined, as in census 1. Release builds usually define it; with `assert()` on, a
loop with an assert in its body cannot vectorize in either build, so this choice can only hide
lost loops, not add them. Stated as a limit.

## Metrics (same as census 1, plus two columns per lost loop)

Per project and in total, per configuration: translation units compiled; vectorized loops in NONE
and FAST (by origin: project, driver, libc++); lost, moved and gained loops (matching as in
census 1); `ud2` trap sites added; `.text` bytes and change.

For every lost loop: file, line, function, the source line, the class (`classify.py`: reverse,
strided, indirect, other with a detail), NONE's and FAST's remarks, and two new columns:

- **operator[] evidence**: the loop's translation unit is rebuilt in FAST with
  `-gline-tables-only` (its `.text` size and `ud2` count must equal the plain build; recorded),
  and every `ud2` in the loop's function is traced with `objdump -d -l --inlines` to its inline
  chain. The loop indexes a checked container when a trap's innermost frame is a libc++
  assertion (its message is quoted, e.g. "vector[] index out of bounds") and a frame of the chain
  lies within the loop's source lines. Otherwise: "no trap attributed to this loop", with the
  traps found in the function listed.
- **trip count**: from the loop header's text, a heuristic: `size()` of a container, an
  iterator/range loop, or another bound (the expression is quoted).

## Controls

- **Determinism**: each configuration runs on two separate runners; every census output and the
  sha256 of every object, record and stderr file must be byte-identical.
- **Kernels**: the 8 kernels go through the pipeline in every shard. Baseline: exactly k04_rev,
  k05_stride2 and k08_matmul LOST at their `// LOOP` line (reverse, strided, strided), k06 and
  k07 in neither build, k01 to k03 in both. avx2: k01 to k03 both; k04, k05, k08 lost; k06 and
  k07 either neither or lost (AVX2 has gathers, so the gather kernel may vectorize under NONE),
  reported as found.
- **Evidence method**: each lost kernel loop must show the vector `operator[]` assertion at its
  `// LOOP` line. If this fails, the evidence column is reported as not working, not dropped.
- **Remark cross-check**: vectorized records in the YAML equal the `vectorized loop` lines on
  stderr, per project and mode.

## Failure rule

A project with any translation unit that fails to compile in either mode is excluded from the
totals. After a failure **one** fix may be made (an include path, a define, a configured header, a
driver bug, or excluding a translation unit that is specific to another platform or to an
optional dependency, each listed with its reason). If it fails again it is **dropped** and listed
with the compiler's error in `corpus.json` ("dropped") and in `corpus/README.md`. No project is
removed silently, and no project is added after the first run.

## Budget

At most 12 workflow runs, each at most 25 minutes (three shards per configuration, two copies).
If budget remains after census 2 is complete, census 1's list is also run at avx2, labelled.

## What will be reported, and what will not

Reported: per project and total for baseline and avx2; every lost loop with its source line,
class, evidence and trip count; which categories had any; the combined census 1 + census 2
baseline table by category.

Not claimed: any runtime cost (loops are counted, not timed; hotness is unknown); that hardening
is cheap or expensive in general; anything about code outside these projects. The selection is
mine, written here before compiling; it is not a random sample of C++.

## Changes after the first run

Run 1 (38264388761) did not finish: shard 2 stopped while writing `remarks.tar.gz` (Draco's
object paths are longer than the old tar header allows) and shard 3 hit its 22-minute limit in
three of four copies. Its one complete shard-3 copy showed the following; no project was added or
removed because of it.

1. **Tar format** (pipeline bug): PAX headers, so long paths fit. Same bytes for short names.
2. **Shards**: four instead of three (LightGBM, Stockfish, ozz-animation and kanzi move to a new
   shard 4), so every job ends inside its time limit. The project list is unchanged.
3. **Evidence method** (the evidence control failed, 1 of 3 kernels): in the FAST build LLVM
   merges all of a function's `__builtin_trap()` checks into one `ud2`, whose location no longer
   says which check it was (k04_rev's merged trap points into libc++ only, k08_matmul's at the
   wrong line). The evidence rebuild now also puts `corpus/evidence/` first on the include path:
   its `<__assertion_handler>` turns each libc++ check into a separate, never-merged call to an
   external function, so every check keeps its own inline chain. Because this rebuild's code is
   no longer the measured FAST code, the record says whether the loop is still not vectorized in
   the evidence rebuild (`evidence_build_loop_not_vectorized`) instead of "codegen identical".
4. **LightGBM, its one fix**: `src/io/tree.cpp` failed on `fmt`'s `consteval` format strings under
   `-std=c++20`, and `linear_tree_learner.cpp` on `_mm_malloc` being redefined. LightGBM's own
   CMake builds with `CMAKE_CXX_STANDARD 17` and defines `MM_MALLOC` on x86-64; the census now
   does the same for LightGBM (`"std": "c++17"`, `MM_MALLOC`).
5. **tiny-dnn, its one fix**: the driver failed because C++20 removed `std::allocator::pointer`
   and friends, which tiny-dnn's bundled xtensor uses. tiny-dnn's CMake builds with
   `CMAKE_CXX_STANDARD 14`; the census now does the same for tiny-dnn (`"std": "c++14"`).

Run 2 (38267418498): all 25 projects compiled in both modes at baseline (no project dropped).
It still did not produce a results folder:

6. **Determinism**: every census output was byte-identical between the copies except the two
   CImg objects, because CImg puts `__DATE__` and `__TIME__` into its code. The census jobs now
   set `SOURCE_DATE_EPOCH=0`, so clang uses a fixed date and time for those macros. Nothing else
   changes.
7. **Evidence tracing**: with separate checks, every check was found and its libc++ message was
   read ("vector[] index out of bounds"), but `objdump --inlines` on the unlinked object returned
   no caller frames, so no check could be placed inside a loop (the evidence control failed, 0
   of 3 kernels). The evidence rebuild is now linked without libraries (`-pie -nostdlib`,
   unresolved symbols ignored; nothing is run), checks are located with `objdump -d` and their
   inline chains are read with `llvm-symbolizer-18 --inlining` (llvm-18 is already installed).
8. **Shards**: the avx2 copies of shard 4 hit the time limit; LightGBM now has shard 4 to itself
   and Stockfish, ozz-animation and kanzi move to shard 5.

Run 3 (38270737004): complete for both targets, determinism PASS for both, all 25 projects
compiled at baseline and avx2. Two controls failed:

9. **Kernel control at avx2 (pre-registered rule, kept as is)**: k08_matmul is vectorized in
   both builds at `-march=x86-64-v3`, so only k04_rev and k05_stride2 are lost there. My avx2
   expectation was wrong; the rule is not changed after the fact and the avx2 kernel control is
   reported as FAIL with this reason.
10. **Evidence**: the linked rebuild found no checks, because the external check function had no
   definition and the linked calls did not carry its name. The evidence header now defines the
   function (weak, never inlined). A kernels-only run (38272963550, `only=box2d`, baseline) then
   passed the evidence control: each of the three lost kernel loops shows the
   "vector[] index out of bounds" check inside its loop line. The final census is the full run
   after that one; run 3's loop counts are the same, since only the evidence rebuild changed.

Run 5 (38273183229) is the census-2 result, both targets, all controls as reported in
corpus/README.md (determinism PASS both; kernels PASS baseline, FAIL avx2 per change 9; evidence
PASS both; remark cross-check PASS both; no project dropped). Run 6 (38273218567) is census 1's
list at avx2 (budget allowed it): determinism PASS, kernel control FAIL for the same k08_matmul
reason, and snappy dropped (its configured header does not enable the AVX2 intrinsics `snappy.cc`
uses under `__AVX2__`); it was not retried. Six of the twelve allowed runs were used.

A per-project language standard is not in the failure rule's list of fixes above; it is added
here because it is the project's own build setting, not a change to the code measured. If either
project fails again it is dropped.
