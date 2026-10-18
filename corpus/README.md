# Corpus census: how common are the loops that lose SIMD under libc++ hardening?

The kernels showed that a loop which clang vectorizes with libc++ hardening off (NONE) and not with
it on (FAST) runs 2.8x to 8x slower in cache. This census asks the next question with no timing at
all: **in real C++ code, how many of the loops clang vectorizes are of that kind?** Every number
comes from the compiler's own optimization records and from `objdump`; nothing is timed.

There are two censuses. **Census 1** (19 libraries: parsers, JSON/YAML/XML, compression, logging)
found almost none. **Census 2** (25 numeric, physics, graphics, machine-learning and compression projects,
including Stockfish and EnTT: physics and game code, graphics and geometry,
numeric/image/signal processing, machine learning, compression) was
chosen to look where such loops are likely to live; its list, metrics and failure rule were
committed in [PLAN2.md](PLAN2.md) before the first compile, in the author's unpublished development history,
and every change after that is logged there.

## Census 1 + census 2, by category (baseline target)

Census 1: run 38259934735 (`results/corpus-run-38259934735/`). Census 2: run 38273183229
(`results/corpus2-baseline-run-38273183229/`, `results/corpus2-avx2-run-38273183229/`). Census 1
at avx2: run 38273218567 (`results/corpus1-avx2-run-38273218567/`). The table is
`python corpus/combine.py ...` (`results/corpus-combined-38273183229/combined.json`).

A loop counts once per function it was compiled into, so a template or header loop instantiated
96 times counts 96 times. The "distinct source locations" columns count each file:line:column
once per project; read the two side by side. The column "of which in project code" counts the project's own files plus the
census's own driver files (`corpus/drivers/`, written for header-only libraries); loops inside libc++'s headers are not in it.

**Baseline (x86-64, SSE2), FAST vs NONE**

| category | projects | vectorized loops (NONE) | distinct source locations | of which in project code | lost under FAST | lost % | lost, distinct locations | projects with a lost loop | .text change |
|---|---|---|---|---|---|---|---|---|---|
| census 1: build tool | 1 | 77 | 12 | 1 | 0 | 0.00% | 0 | 0 | +0.47% |
| census 1: compression and storage | 2 | 39 | 8 | 5 | 1 | 2.56% | 1 | 1 | +0.15% |
| census 1: formatting and logging | 2 | 118 | 10 | 31 | 0 | 0.00% | 0 | 0 | +0.13% |
| census 1: geometry | 1 | 28 | 8 | 1 | 0 | 0.00% | 0 | 0 | +1.98% |
| census 1: image codec | 1 | 61 | 50 | 48 | 0 | 0.00% | 0 | 0 | +0.00% |
| census 1: numeric | 2 | 54 | 16 | 54 | 0 | 0.00% | 0 | 0 | +0.00% |
| census 1: parsers | 10 | 216 | 26 | 10 | 0 | 0.00% | 0 | 0 | +0.54% |
| **census 1 total** | 19 | 593 | 130 | 150 | 1 | 0.17% | 1 | 1 | +0.44% |
| census 2: compression | 1 | 130 | 63 | 97 | 0 | 0.00% | 0 | 0 | +0.10% |
| census 2: graphics and geometry | 8 | 897 | 102 | 222 | 82 | 9.14% | 12 | 1 | +2.24% |
| census 2: machine learning | 6 | 3,365 | 313 | 850 | 356 | 10.58% | 62 | 4 | +0.76% |
| census 2: numeric, image and signal | 4 | 237 | 88 | 219 | 4 | 1.69% | 1 | 1 | +0.43% |
| census 2: physics and game | 6 | 339 | 88 | 221 | 2 | 0.59% | 2 | 1 | -0.00% |
| **census 2 total** | 25 | 4,968 | 654 | 1,609 | 444 | 8.94% | 77 | 7 | +0.70% |
| **combined** | 44 | 5,561 | 784 | 1,759 | 445 | 8.00% | 78 | 8 | +0.66% |

**avx2 sensitivity (-march=x86-64-v3), FAST vs NONE**

| category | projects | vectorized loops (NONE) | distinct source locations | of which in project code | lost under FAST | lost % | lost, distinct locations | projects with a lost loop | .text change |
|---|---|---|---|---|---|---|---|---|---|
| **census 1 total (avx2)** | 18 | 664 | 172 | 210 | 2 | 0.30% | 1 | 1 | +0.39% |
| **census 2 total (avx2)** | 25 | 5,186 | 758 | 1,787 | 221 | 4.26% | 61 | 7 | +0.16% |

What the table says, and only that:

- **Census 2 loses far more than census 1**: 444 of 4,968 vectorized loops (8.9%) against 1 of
  593 (0.17%). In distinct source locations: 77 of 654 (11.8%) against 1 of 130.
- **One project dominates the raw count.** LightGBM alone has 331 of the 444 (38 distinct
  locations), mostly from two template functions in `feature_histogram.cpp` instantiated 32 and
  96 times. Without LightGBM, census 2 loses 113 of 2,415 vectorized loops (4.7%), at 39 distinct
  locations.
- **7 of 25 census-2 projects have any lost loop**: LightGBM, Draco, llama.cpp, whisper.cpp,
  Spectra, tiny-dnn and Stockfish. Categories: machine learning 4 of 6 projects, graphics and
  geometry 1 of 8 (Draco), numeric/image/signal 1 of 4 (Spectra), physics and game 1 of 6
  (Stockfish, 2 loops), compression 0 of 1. JoltPhysics, Box2D, Recast, ozz-animation, EnTT,
  meshoptimizer, the geometry headers, pocketfft, xtensor, CImg, hnswlib, Annoy and kanzi lose none.
- **Every census-2 lost loop is in the projects' own code** (none inside libc++), and 401 of 444
  (58 of 77 distinct locations) have a traced libc++ check inside the loop's source lines:
  "vector[] index out of bounds" (391) or the `std::array` check (10). The other 43 (19 locations)
  have no check traced to the loop (for example, the check sits in a helper called from the loop,
  or the evidence rebuild could not be linked); they are listed as such.
- **The trip count is rarely the container's size().** By the header-text heuristic: 407 of 444
  lost loops (63 of 77 locations) are bounded by another value (a member such as
  `num_cat_threshold`, `num_components`, `n_pos`), 27 (10 locations) by a container's `size()`,
  10 (4 locations) are range or iterator loops. A forward loop over `i < n` that indexes a
  `std::vector` cannot be proven in range when `n` is not that vector's size, so the check stays
  in the loop and the vectorizer gives up.
- **Shapes** (per-function count, distinct locations): reverse 129 (3: two `[n - 1 - i]` loops in
  LightGBM, 128 copies, and one counting-down loop in whisper.cpp's `parakeet.cpp`), strided 39
  (14), indirect 11 (5), other 265 (55): forward loops bounded by a variable 228 (38), unclear
  from the text 29 (12), no subscript in the loop text 8 (5).
- **avx2 (sensitivity)**: at `-march=x86-64-v3` census 2 loses 221 of 5,186 (4.3%; 61 distinct
  locations) and census 1 loses 2 of 664 (0.30%; 1 location, leveldb `db/db_impl.cc:1037`) over 18
  projects (snappy did not build at avx2). So census 2 loses fewer at avx2 (221 against 444 at
  baseline), while census 1 loses slightly more (2 of 664 against 1 of 593 at baseline). The same 7 census-2 projects lose loops, plus
  ozz-animation (1) and minus Spectra.
- **The checks are in the code either way**: FAST adds 2,874 trap sites and 0.70% `.text` in
  census 2 (baseline).

**Not claimed.** No runtime cost: loops are counted, not timed, and how hot a lost loop is cannot
be known at compile time (LightGBM's histogram code is hot in training, its metric loops are
not; the census does not say which). Nothing about hardening being cheap or expensive in general,
or about code outside these 44 projects: the selection is mine, written down before compiling (in
the author's unpublished development history), not a random sample of C++.

## Census 2 per project (baseline, FAST vs NONE)

| project | category | TUs | vectorized NONE | vectorized FAST | lost | lost, distinct locations | ud2 added | `.text` change |
|---|---|---|---|---|---|---|---|---|
| box2d | physics and game | 45 | 4 | 4 | 0 | 0 | 0 | +0.00% |
| joltphysics | physics and game | 137 | 107 | 107 | 0 | 0 | 0 | +0.00% |
| recastnavigation | physics and game | 26 | 72 | 72 | 0 | 0 | 0 | +0.00% |
| ozz-animation | physics and game | 40 | 27 | 27 | 0 | 0 | 24 | +0.61% |
| entt | physics and game | 1 | 28 | 28 | 0 | 0 | 72 | -7.63% |
| stockfish | physics and game | 26 | 101 | 99 | 2 | 2 | 139 | +0.43% |
| meshoptimizer | graphics and geometry | 21 | 40 | 40 | 0 | 0 | 0 | +0.00% |
| earcut | graphics and geometry | 1 | 13 | 13 | 0 | 0 | 22 | +2.52% |
| delaunator-cpp | graphics and geometry | 1 | 11 | 11 | 0 | 0 | 17 | +18.59% |
| nanoflann | graphics and geometry | 1 | 4 | 4 | 0 | 0 | 11 | +8.60% |
| nanort | graphics and geometry | 1 | 7 | 7 | 0 | 0 | 6 | +3.79% |
| draco | graphics and geometry | 129 | 817 | 745 | 82 | 12 | 547 | +2.30% |
| imath | graphics and geometry | 6 | 0 | 0 | 0 | 0 | 0 | +0.00% |
| tinyrenderer | graphics and geometry | 4 | 5 | 5 | 0 | 0 | 9 | +1.66% |
| xtensor | numeric, image and signal | 1 | 19 | 19 | 0 | 0 | 10 | +1.46% |
| spectra | numeric, image and signal | 1 | 79 | 75 | 4 | 1 | 27 | +0.99% |
| pocketfft | numeric, image and signal | 1 | 121 | 121 | 0 | 0 | 26 | +0.30% |
| cimg | numeric, image and signal | 1 | 18 | 18 | 0 | 0 | 0 | +0.00% |
| lightgbm | machine learning | 35 | 2,553 | 2,223 | 331 | 38 | 1193 | +0.58% |
| tiny-dnn | machine learning | 1 | 72 | 70 | 2 | 2 | 172 | +0.94% |
| llama.cpp | machine learning | 32 | 578 | 563 | 15 | 14 | 430 | +1.38% |
| whisper.cpp | machine learning | 2 | 110 | 102 | 8 | 8 | 105 | +0.36% |
| hnswlib | machine learning | 1 | 13 | 13 | 0 | 0 | 16 | +1.71% |
| annoy | machine learning | 1 | 39 | 39 | 0 | 0 | 8 | +0.87% |
| kanzi | compression | 42 | 130 | 130 | 0 | 0 | 40 | +0.10% |
| **total** | | 557 | 4,968 | 4,535 | 444 | 77 | 2874 | +0.69% |

At avx2 the projects with lost loops are: LightGBM 180 (31 locations), Draco 17 (7), llama.cpp 14
(13), whisper.cpp 5 (5), Stockfish 2 (2), tiny-dnn 2 (2), ozz-animation 1 (1); the rest 0.

<details><summary>All 77 lost loops of census 2 (baseline): source line, count, class, trip count, traced check</summary>

| project | where | count | class | trip count | libc++ check in the loop | source line |
|---|---|---|---|---|---|---|
| stockfish | `src/search.cpp:2072` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (usize i = 1; i < multiPV; ++i)` |
| stockfish | `src/syzygy/tbprobe.cpp:1200` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (int i = 0; i < base64_size; ++i)` |
| draco | `src/draco/attributes/attribute_quantization_transform.cc:39` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int i = 0; i < attribute.num_components(); ++i) {` |
| draco | `src/draco/attributes/point_attribute.cc:213` | 28 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (uint32_t i = 0; i < num_unique_entries_; ++i) {` |
| draco | `src/draco/compression/attributes/kd_tree_attributes_decoder.cc:477` | 2 | strided | other bound | yes: std::vector | `for (int c = 0; c < att->num_components(); ++c) {` |
| draco | `src/draco/compression/attributes/kd_tree_attributes_encoder.cc:203` | 1 | strided | other bound | yes: std::vector | `for (int c = 0; c < source_att->num_components(); ++c) {` |
| draco | `src/draco/compression/attributes/kd_tree_attributes_encoder.cc:100` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int c = 0; c < att->num_components(); ++c) {` |
| draco | `src/draco/compression/attributes/prediction_schemes/mesh_prediction_scheme_parallelogram_shared.h:62` | 8 | strided | other bound | no check traced in the loop | `for (int c = 0; c < num_components; ++c) {` |
| draco | `src/draco/compression/attributes/prediction_schemes/mesh_prediction_scheme_constrained_multi_parallelogram_decoder.h:164` | 2 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int j = 0; j < num_components; ++j) {` |
| draco | `src/draco/compression/attributes/sequential_integer_attribute_encoder.cc:175` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (uint32_t i = 0; i < static_cast<uint32_t>(num_values); ++i) {` |
| draco | `src/draco/compression/entropy/ans.h:493` | 18 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (uint32_t j = act_prob; j < cum_prob; ++j) {` |
| draco | `src/draco/compression/entropy/rans_symbol_decoder.h:108` | 18 | strided | other bound | yes: std::vector | `for (uint32_t j = 0; j < offset + 1; ++j) {` |
| draco | `src/draco/compression/mesh/mesh_edgebreaker_traversal_valence_encoder.h:64` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (CornerIndex i(0); i < corner_table_->num_corners(); ++i) {` |
| draco | `src/draco/io/ply_decoder.cc:27` | 1 | other: no subscript (iterator, pointer or range loop) | other bound | yes: std::vector | `for (int i = 0; i < face_element.num_entries(); ++i) {` |
| spectra | `include/Spectra/Util/SelectionRule.h:215` | 4 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (Index i = 0; i < size; i++)` |
| lightgbm | `src/boosting/rf.hpp:104` | 1 | strided | other bound | yes: std::vector | `for (data_size_t i = 0; i < num_data_; ++i) {` |
| lightgbm | `include/LightGBM/utils/common.h:643` | 13 | other: unclear from the text | container size() | yes: std::vector | `for (size_t i = 0; i < data->size(); ++i) {` |
| lightgbm | `include/LightGBM/utils/common.h:652` | 6 | other: unclear from the text | container size() | yes: std::vector | `for (size_t i = 0; i < data.size(); ++i) {` |
| lightgbm | `src/io/bin.cpp:657` | 1 | other: unclear from the text | container size() | yes: std::vector | `for (int i = 0; i < static_cast<int>(offsets.size()) - 1; ++i) {` |
| lightgbm | `src/io/multi_val_dense_bin.hpp:283` | 1 | indirect | other bound | no check traced in the loop | `for (int j = 0; j < num_feature_; ++j) {` |
| lightgbm | `src/io/multi_val_dense_bin.hpp:47` | 1 | strided | other bound | yes: std::vector | `for (auto i = 0; i < num_feature_; ++i) {` |
| lightgbm | `src/io/multi_val_sparse_bin.hpp:364` | 6 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (auto j = j_start; j < j_end; ++j) {` |
| lightgbm | `src/io/multi_val_sparse_bin.hpp:62` | 4 | indirect | range or iterator loop | yes: std::vector | `for (auto val : values) {` |
| lightgbm | `src/io/multi_val_sparse_bin.hpp:71` | 4 | indirect | range or iterator loop | yes: std::vector | `for (auto val : values) {` |
| lightgbm | `src/io/dataset.cpp:1179` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int i = 0; i < num_total_features_; ++i) {` |
| lightgbm | `src/io/dataset_loader.cpp:1346` | 1 | strided | other bound | yes: std::vector | `for (int k = 0; k < num_class_; ++k) {` |
| lightgbm | `src/io/dataset_loader.cpp:1424` | 1 | strided | other bound | yes: std::vector | `for (int k = 0; k < num_class_; ++k) {` |
| lightgbm | `src/io/metadata.cpp:469` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (data_size_t i = 0; i < num_data_; ++i) {` |
| lightgbm | `src/io/metadata.cpp:538` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (data_size_t i = 0; i < num_weights_; ++i) {` |
| lightgbm | `src/io/tree.cpp:388` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int i = 0; i < num_leaves_; ++i) {` |
| lightgbm | `src/metric/rank_metric.hpp:110` | 1 | other: unclear from the text | container size() | yes: std::vector | `for (size_t j = 0; j < eval_at_.size(); ++j) {` |
| lightgbm | `src/metric/rank_metric.hpp:130` | 1 | other: unclear from the text | container size() | yes: std::vector | `for (size_t j = 0; j < eval_at_.size(); ++j) {` |
| lightgbm | `src/metric/rank_metric.hpp:138` | 1 | other: unclear from the text | container size() | yes: std::vector | `for (size_t j = 0; j < result.size(); ++j) {` |
| lightgbm | `src/metric/map_metric.hpp:122` | 1 | other: unclear from the text | container size() | yes: std::vector | `for (size_t j = 0; j < eval_at_.size(); ++j) {` |
| lightgbm | `src/metric/map_metric.hpp:132` | 1 | other: unclear from the text | container size() | yes: std::vector | `for (size_t j = 0; j < eval_at_.size(); ++j) {` |
| lightgbm | `src/metric/map_metric.hpp:139` | 1 | other: unclear from the text | container size() | yes: std::vector | `for (size_t j = 0; j < result.size(); ++j) {` |
| lightgbm | `src/network/linker_topo.cpp:114` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int i = 0; i < rest; ++i) {` |
| lightgbm | `src/network/linker_topo.cpp:164` | 1 | indirect | other bound | yes: std::vector | `for (int j = 0; j < distance[i]; ++j) {` |
| lightgbm | `src/network/linker_topo.cpp:173` | 1 | indirect | other bound | yes: std::vector | `for (int j = 0; j < distance[i]; ++j) {` |
| lightgbm | `src/objective/regression_objective.hpp:120` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (data_size_t i = 0; i < num_data; ++i) {` |
| lightgbm | `src/objective/multiclass_objective.hpp:98` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int k = 0; k < num_class_; ++k) {` |
| lightgbm | `src/objective/multiclass_objective.hpp:119` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int k = 0; k < num_class_; ++k) {` |
| lightgbm | `src/treelearner/feature_histogram.cpp:373` | 32 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int i = 0; i < output->num_cat_threshold; ++i) {` |
| lightgbm | `src/treelearner/feature_histogram.cpp:378` | 32 | reverse | other bound | yes: std::vector | `for (int i = 0; i < output->num_cat_threshold; ++i) {` |
| lightgbm | `src/treelearner/feature_histogram.cpp:731` | 96 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int i = 0; i < output->num_cat_threshold; ++i) {` |
| lightgbm | `src/treelearner/feature_histogram.cpp:736` | 96 | reverse | other bound | yes: std::vector | `for (int i = 0; i < output->num_cat_threshold; ++i) {` |
| lightgbm | `src/treelearner/linear_tree_learner.cpp:188` | 4 | other: no subscript (iterator, pointer or range loop) | other bound | yes: std::vector | `for (int leaf_num = 0; leaf_num < num_leaves; ++leaf_num) {` |
| lightgbm | `src/treelearner/linear_tree_learner.cpp:297` | 4 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int feat2 = feat1; feat2 < num_feat + 1; ++feat2) {` |
| lightgbm | `src/treelearner/linear_tree_learner.cpp:312` | 4 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (size_t j = 0; j < (num_feat + 1) * (num_feat + 2) / 2; ++j) {` |
| lightgbm | `src/treelearner/linear_tree_learner.cpp:315` | 4 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (size_t feat1 = 0; feat1 < num_feat + 1; ++feat1) {` |
| lightgbm | `src/treelearner/linear_tree_learner.cpp:324` | 2 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int leaf_num = 0; leaf_num < num_leaves; ++leaf_num) {` |
| lightgbm | `src/treelearner/serial_tree_learner.cpp:956` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int i = 0; i < tree->num_leaves(); ++i) {` |
| lightgbm | `src/treelearner/serial_tree_learner.cpp:961` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (int i = 0; i < tree->num_leaves(); ++i) {` |
| tiny-dnn | `tiny_dnn/layers/layer.h:391` | 1 | other: unclear from the text | range or iterator loop | no check traced in the loop | `for (auto &w : *weight) w = src[idx++];` |
| tiny-dnn | `tiny_dnn/core/kernels/fully_connected_op_internal.h:65` | 1 | other: unclear from the text | range or iterator loop | no check traced in the loop | `for (size_t i = r.begin(); i < r.end(); i++) {` |
| llama.cpp | `src/llama-batch.cpp:1247` | 2 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::array | `for (size_t i = 0; i < n_pos; ++i) {` |
| llama.cpp | `src/llama-batch.cpp:1382` | 1 | strided | other bound | yes: std::array | `for (uint32_t j = 0; j < batch_ext->n_pos_per_embd; ++j) {` |
| llama.cpp | `src/llama-graph.cpp:354` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (int s = 0; s < n_seqs_unq; ++s) {` |
| llama.cpp | `src/llama-hparams.cpp:10` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::array | `for (uint32_t il = 0; il < n_layer(); ++il) {` |
| llama.cpp | `src/llama-hparams.cpp:14` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::array | `for (uint32_t il = 0; il < n_layer(); ++il) {` |
| llama.cpp | `src/llama-hparams.cpp:26` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::array | `for (uint32_t il = 0; il < n_layer(); ++il) {` |
| llama.cpp | `src/llama-hparams.cpp:30` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::array | `for (uint32_t il = 0; il < n_layer(); ++il) {` |
| llama.cpp | `src/llama-hparams.cpp:192` | 1 | other: no subscript (iterator, pointer or range loop) | other bound | yes: std::array | `for (uint32_t il = 0; il < n_layer_all; ++il) {` |
| llama.cpp | `src/llama-hparams.cpp:201` | 1 | other: no subscript (iterator, pointer or range loop) | other bound | yes: std::array | `for (uint32_t il = 0; il < n_layer_all; ++il) {` |
| llama.cpp | `src/llama-hparams.cpp:92` | 1 | other: no subscript (iterator, pointer or range loop) | other bound | yes: std::array | `for (uint32_t il = 0; il < n_layer_all; ++il) {` |
| llama.cpp | `src/llama-kv-cache.cpp:1236` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | yes: std::vector | `for (uint32_t s = 0; s < n_stream; ++s) {` |
| llama.cpp | `src/llama-model-saver.cpp:126` | 1 | other: unclear from the text | container size() | yes: std::vector | `for (size_t i = 0; i < value.size(); ++i) {` |
| llama.cpp | `src/llama-sampler.cpp:3764` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (size_t i = 0; i < cur_p->size; ++i) {` |
| llama.cpp | `src/llama-sampler.cpp:3153` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (int32_t i = 0; i < n_active; ++i) {` |
| whisper.cpp | `src/parakeet.cpp:2034` | 1 | strided | other bound | no check traced in the loop | `for (int k = 0; k < n_k; ++k) {` |
| whisper.cpp | `src/parakeet.cpp:2041` | 1 | strided | other bound | no check traced in the loop | `for (int k = 0; k < n_k; ++k) {` |
| whisper.cpp | `src/parakeet.cpp:2058` | 1 | strided | other bound | no check traced in the loop | `for (int k = 0; k < n_k; ++k) {` |
| whisper.cpp | `src/parakeet.cpp:2698` | 1 | strided | other bound | no check traced in the loop | `for (int k = 0; k < half_N; k++) {` |
| whisper.cpp | `src/parakeet.cpp:2821` | 1 | reverse | other bound | no check traced in the loop | `for (int i = n_samples - 1; i > 0; i--) {` |
| whisper.cpp | `src/whisper.cpp:6545` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (int i = 0; i < n_logits; ++i) {` |
| whisper.cpp | `src/whisper.cpp:6311` | 1 | other: forward loop bounded by a variable, not the container's size() | other bound | no check traced in the loop | `for (int i = 0; i < n_logits; ++i) {` |
| whisper.cpp | `src/whisper.cpp:3226` | 1 | strided | other bound | no check traced in the loop | `for (int j = 0; j < mel.n_mel; j++) {` |

</details>

Every entry, with function, both remarks, the loop's context lines and the full check chain, is
in `lost_loops.json` of each results folder.

## Census 2 controls

- **Determinism**: both targets ran on two separate copies; `census.json`, `lost_loops.json`,
  `remarks.tar.gz` and the sha256 of every object, record and stderr file are byte-identical
  (PASS, baseline and avx2). The census jobs set `SOURCE_DATE_EPOCH=0` (CImg compiles `__DATE__`
  into its code).
- **Kernels, baseline**: exactly k04_rev, k05_stride2 and k08_matmul lost at their `// LOOP` line
  (reverse, strided, strided), k06/k07 in neither build, k01 to k03 in both (PASS).
- **Kernels, avx2**: **FAIL as registered**. The pre-registered avx2 rule (the order rests on
  the author's unpublished development history) expected k08_matmul lost; at `-march=x86-64-v3` it is vectorized in both builds. k04_rev and k05_stride2 are lost,
  k06/k07 in neither, k01 to k03 in both. The rule was not changed after the fact. Census 1 at avx2
  shows the same.
- **Evidence method**: each lost kernel loop shows the "vector[] index out of bounds" check inside
  its `// LOOP` line (PASS, both targets).
- **Remark cross-check**: vectorized records in the YAML equal the `vectorized loop` lines on
  stderr, per project and mode (PASS).
- **Dropped projects**: none in census 2 (LightGBM and tiny-dnn each needed their one allowed fix:
  their own CMake language standard, see PLAN2.md). Census 1 at avx2 dropped snappy:
  `snappy.cc` uses AVX2 intrinsics under `__AVX2__` that its configured header, written for the
  baseline target, does not enable (`unknown type name '__m256i'`); it was not retried.

## Limits (both censuses)

- Counts, not cost. A lost loop is only potentially expensive; hotness is unknown.
- Per-function counts inflate templates and inlined headers; distinct locations are given beside them.
- The selection of projects is mine (PLAN2.md lists the rule and what was left out and why).
  Header-only libraries are measured only through what their driver calls.
- One toolchain: clang 18.1.3 with libc++ 18 (Ubuntu noble), `-O2`, FAST mode only. Baseline
  x86-64 (SSE2) is the primary target; `-march=x86-64-v3` is a sensitivity run.
- `NDEBUG` is not defined (as in census 1). With `assert()` on, a loop with an assert in its body
  cannot vectorize in either build, so this can only hide lost loops.
- `-std=c++20` everywhere except LightGBM (C++17) and tiny-dnn (C++14), their own settings.
- The class and trip-count columns are regular-expression heuristics over the source text. The
  check evidence comes from a separate rebuild (each libc++ check made a separate, never-merged
  call, then linked without libraries and traced with `llvm-symbolizer`); in that rebuild 8 of the
  444 lost loops are vectorized after all, which the record says per loop.

## Census 1 result (run 38259934735, `results/corpus-run-38259934735/`)

| | NONE | FAST |
|---|---|---|
| projects / translation units | 19 / 144 | 19 / 144 |
| vectorized loops (one per function they were compiled into) | 593 | 592 |
| of which inside libc++'s own headers (inlined into project code) | 443 | 443 |
| of which in the projects' own code | 150 | 149 |
| check traps (`ud2`) | 30 | 340 (+310) |
| `.text` bytes | 2,581,019 | 2,592,343 (+0.44%) |

- **Lost: 1 of 593 vectorized loops (0.17%)**, in 1 of 19 projects. Moved 0, gained 0.
- The one lost loop: leveldb `db/c.cc:117`, `for (int i = 0; i < n; i++) {` filling two
  `std::vector`s from an array of `Slice`. A forward loop, but its bound is `n`, not the vectors'
  `size()`, so the compiler cannot prove the check always passes; FAST's remark is "the
  cost-model indicates that vectorization is not beneficial".
- No reverse, strided or indirect `operator[]` loop that NONE vectorized was found in this corpus.
  Most vectorized loops are libc++'s own pointer and iterator loops (`std::move`, uninitialized
  copies, `__split_buffer`), which FAST does not check, and the projects' raw-pointer loops.
- The checks are there: FAST adds 310 trap sites and 0.44% code. They just almost never sit in a
  loop that NONE had vectorized.

**What this does not show.** It counts loops, not time. A lost loop is only *potentially*
expensive: how often it runs is unknown at compile time, so no runtime cost is claimed. It cannot
say what fraction of Google's 0.30% comes from such loops, and it says nothing about code outside
these 19 libraries (application code with numeric `operator[]` loops may look more like the
kernels). One compiler (clang 18.1.3, libc++ 18.1.3, `-O2`, baseline x86-64 SSE2), FAST mode only.

## Census 1 controls (all PASS in the committed run)

- **Kernels.** The project's 8 kernels go through the same pipeline. It must mark exactly
  k04_rev, k05_stride2 and k08_matmul as LOST at their `// LOOP` line (classified reverse,
  strided, strided), k06_gather and k07_hist as vectorized in neither build, k01 to k03 in both.
- **Determinism.** The whole census runs twice, on two separate runners, and `census.json`,
  `lost_loops.json`, `remarks.tar.gz` and the sha256 of every object, record and stderr file
  (912 files) must be byte-identical.
- **Remark cross-check.** Per project and mode, the number of vectorized records parsed from the
  YAML equals the number of `remark: vectorized loop` lines clang printed on stderr.

## How it works

- `projects.json`: the 19 projects, each pinned by commit (or release file) with the sha256 and
  size of every download, the library's own translation units (tests, tools and other platforms
  excluded), include paths, defines, and the configured headers their CMake would write (snappy,
  leveldb). Header-only libraries (nlohmann/json, RapidJSON, CLI11, Eigen) are compiled through a
  small driver in `drivers/` that instantiates common operations.
- `census.py`: fetch (sha256 checked, a mismatch stops the run), then every translation unit is
  compiled twice:
  `clang++-18 -O2 -std=c++20 -stdlib=libc++ -D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_{NONE,FAST} -Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize -fsave-optimization-record -foptimization-record-passes=loop-vectorize -c`.
- **Matching.** A loop is identified by translation unit, function (mangled), file, line and
  column from its optimization record (`optrecord.py`). LOST = vectorized in NONE and not in FAST
  at the same key; GAINED is the reverse; a lost loop whose location gained a vectorized copy in
  another function of the same file is counted as MOVED (an inlining change), not lost. libc++ 18
  writes the hardening mode into the ABI tag of its inline functions (`[abi:ne180100]` vs
  `[abi:fe180100]`); FAST names are mapped to the NONE spelling before matching.
- **Classification** (`classify.py`): reverse, strided/computed index, indirect index, or other
  with a detail, from the loop's source text by regular expressions. A heuristic; every lost loop
  is listed in `lost_loops.json` with its source line, context, function and both remarks.
- `finalize.py`: the determinism comparison, then `corpus.json` with everything. `schema.py`:
  fields, pins, and every total and percentage recomputed from its parts.
- **Census 2 additions.** `projects2.json` (the list in PLAN2.md, with `category`, `why`, `shard`
  and, for two projects, `std`); `census.py --projects projects2.json --target baseline|avx2
  --shard K`; `merge.py` joins the five shards of one copy before the determinism comparison.
  Per lost loop: `trip_count` (`classify.trip_count`, from the header text) and `index_evidence`:
  the translation unit is rebuilt in FAST with `-gline-tables-only` and
  `evidence/__assertion_handler` first on the include path (each libc++ check becomes a separate
  call that is never merged), linked without libraries (nothing is run), each check located with
  `objdump -d` and traced with `llvm-symbolizer-18 --inlining`; the loop counts as indexing a
  checked container when a check's chain has a libc++ assertion (its message is recorded) and a
  frame inside the loop's source lines. `combine.py` makes the census 1 + 2 table.

Outputs per run in `results/corpus-run-<id>/` (census 2: `results/corpus2-<target>-run-<id>/`;
census 1 at avx2: `results/corpus1-avx2-run-<id>/`): `corpus.json` (per project and total numbers,
pinned versions and hashes, toolchain, patterns, controls, limits), `lost_loops.json` (every lost,
moved and gained loop), `objects.sha256`, `remarks.tar.gz` (every stderr remark file and
optimization record).

## Rerun

```
gh workflow run corpus.yml            # census 2, baseline and avx2: 5 shards x 2 copies each, about 20 minutes
gh workflow run corpus.yml -f list=projects.json -f targets=baseline   # census 1
gh run download <run id> -n corpus2-baseline-run-<run id> -D results/corpus2-baseline-run-<run id>
python corpus/run_tests.py            # tests + schema check of every results/corpus*-run-*/ (no compiler)
python corpus/combine.py --c1 results/corpus-run-38259934735 --c2 results/corpus2-baseline-run-38273183229   --c1-avx2 results/corpus1-avx2-run-38273218567 --c2-avx2 results/corpus2-avx2-run-38273183229
```

Locally on Ubuntu 24.04 with the apt packages below: `python3 corpus/census.py all` (outputs in
`build/corpus-out/`; `--only fmt,leveldb` for a subset).

## Downloads and packages

Apt (Ubuntu noble): `clang-18`, `libc++-18-dev`, `libc++abi-18-dev` (1:18.1.3-1ubuntu1), `llvm-18`
(for `llvm-cxxfilt-18` and, in census 2, `llvm-symbolizer-18`), `binutils` (`objdump`, `ld.bfd`,
2.42). Every other download, sha256-checked. Census 1:

| project | version | source | bytes | sha256 |
|---|---|---|---|---|
| fmt | 11.0.2 | https://github.com/fmtlib/fmt/archive/0c9fce2ffefecfdce794e1859584e25877b7b592.tar.gz | 701,333 | f94052c10b611fd374194ca6e0dc4d159459c0b370abfe9002c13058863b7039 |
| nlohmann/json | 3.11.3 | https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp | 919,975 | 9bea4c8066ef4a1c206b2be5a36302f8926f7fdc6087af5d20b417d0cf103ea6 |
| RapidJSON | master 2025-02-05 | https://github.com/Tencent/rapidjson/archive/24b5e7a8b27f42fa16b96fc70aade9106cf7102f.tar.gz | 1,116,703 | 2d2601a82d2d3b7e143a3c8d43ef616671391034bc46891a9816b79cf2d3e7a8 |
| simdjson | 3.10.1 | https://raw.githubusercontent.com/simdjson/simdjson/e341c8b43861b43de29c48ab65f292d997096953/singleheader/simdjson.cpp | 2,352,118 | 3db4c8088b5dd5a1adb6d6b83b271d21f8fb65ecd21c3d9c11509fe60a5c1d7e |
| simdjson | 3.10.1 | https://raw.githubusercontent.com/simdjson/simdjson/e341c8b43861b43de29c48ab65f292d997096953/singleheader/simdjson.h | 5,048,255 | b2d5c39f23b23c91e4849ffdeeb2118ec89968469df0588e20510314886fb6b3 |
| jsoncpp | 1.9.6 | https://github.com/open-source-parsers/jsoncpp/archive/89e2973c754a9c02a49974d839779b151e95afd6.tar.gz | 212,605 | fbdcd9beff428968710f339b15ae3911e295a5a71da0cbadbdd631d7a5aeaaee |
| yaml-cpp | 0.8.0 | https://github.com/jbeder/yaml-cpp/archive/f7320141120f720aecc4c32be25586e7da9eb978.tar.gz | 1,018,426 | 2fd3bf695ccc056835a70dd6d3046312cc1004e8338b8b5c91646918a27b7ef6 |
| pugixml | 1.14 | https://github.com/zeux/pugixml/archive/db78afc2b7d8f043b4bc6b185635d949ea2ed2a8.tar.gz | 577,073 | 56e43bbe2733cc149c7d50a6d11a65b3c4ed080b16bfa6050154e09b1c320ed0 |
| tinyxml2 | 10.0.0 | https://github.com/leethomason/tinyxml2/archive/321ea883b7190d4e85cae5512a12e5eaa8f8731f.tar.gz | 642,826 | d5ae097578717b42b4f05f2c6b2d09f473a1c30d1552ca4e2dcb4eab5b34de84 |
| tinyobjloader | 2.0.0rc13 | https://github.com/tinyobjloader/tinyobjloader/archive/2945a967c5303b2c8c14174117c45f3302591150.tar.gz | 987,433 | 988cc315f69c9319499fcb20e4feb54e058ea99d1b69d18e9a05984ce884f49c |
| muparser | 2.3.4 | https://github.com/beltoforion/muparser/archive/59e0ce1e0d35d42713af67788f19797945d81364.tar.gz | 112,810 | caa36627326cde8339722dfc07f9048e8656f4203c5b8cf0c37357d35885b826 |
| CLI11 | 2.4.2 | https://github.com/CLIUtils/CLI11/archive/6c7b07a878ad834957b98d0f9ce1dbe0cb204fc9.tar.gz | 343,902 | 9ac528f302eb1a775ce790e59fe639b13040d8d58183d90f429a845ea5f6bfc2 |
| double-conversion | 3.3.0 | https://github.com/google/double-conversion/archive/4f7a25d8ced8c7cf6eee6fd09d6788eaa23c9afe.tar.gz | 7,033,334 | 68938ec9e1168e4e5df1123d167f5e110976fde0e8c68c41c1d0e0b9608ec4cb |
| Eigen | 3.4.0 | https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz | 2,705,005 | 8586084f71f9bde545ee7fa6d00288b264a2b7ac3607b974e54d13e7162c1c72 |
| Clipper2 | 1.4.0 | https://github.com/AngusJohnson/Clipper2/archive/736ddb0b53d97fd5f65dd3d9bbf8a0993eaf387c.tar.gz | 600,493 | efb777323a19fca36bd6dad40726415c2823bac24ef6892385385f3432b66112 |
| snappy | 1.2.1 | https://github.com/google/snappy/archive/2c94e11145f0b7b184b831577c93e5a41c4c0346.tar.gz | 1,108,350 | 4af3d161c098b7897dc0c92b39991956eca30e9a3d28e0aabb5587213bfd1329 |
| leveldb | main 2026-10-08 | https://github.com/google/leveldb/archive/bb74ef739973a70ca9f0d90788a1da89b788c0ad.tar.gz | 245,522 | fa5cad533bef27fb0d693c10fe14b40c4b920813340d7c8aeccfa17c4fd2a73d |
| spdlog | 1.14.1 | https://github.com/gabime/spdlog/archive/27cb4c76708608465c413f6d0e6b8d99a4d84302.tar.gz | 269,864 | 7d512b37019b61646cd6fd1e48f52a3cf3e098f36b33ba9c059fe51301ff40b3 |
| ninja | 1.12.1 | https://github.com/ninja-build/ninja/archive/2daa09ba270b0a43e1929d29b073348aa985dfaa.tar.gz | 240,689 | 373bb33a8db2769b825a771e5d25b11d79ef5e41a934b870487257c27b187180 |
| lodepng | master 2026-10-06 | https://github.com/lvandeve/lodepng/archive/e584a8490db1b76b81bf298c11c09d3b55d9c270.tar.gz | 262,771 | c9cc1dcd143bd1365f0ce50cfc14bacab43d7bee5a2be212d6f4b73eefa8626f |


Census 2 (`projects2.json`; commits are in the file):

| project | version | source | bytes | sha256 |
|---|---|---|---|---|
| box2d | 2.4.2 | https://github.com/erincatto/box2d/archive/411acc32eb6d4f2e96fc70ddbdf01fe5f9b16230.tar.gz | 1,237,162 | 853a6141b9f187a9de6a1e9a7864b9394eb70150373af1e185f0d508f533a524 |
| joltphysics | 5.6.0 | https://github.com/jrouwe/JoltPhysics/archive/e77f175595e64cb44218cc9d9d56fc365ad0e36a.tar.gz | 19,392,623 | 1f32328fb763135de10a244568d6ccb2ed9b1e6593fafe6dc6db5b2719d330bd |
| recastnavigation | 1.6.0 | https://github.com/recastnavigation/recastnavigation/archive/6dc1667f580357e8a2154c28b7867bea7e8ad3a7.tar.gz | 1,280,923 | f565cc91b85df95a656cfc672e41c02e8aa44ba2363905aa8277ce20ea87491d |
| ozz-animation | 0.17.0 | https://github.com/guillaumeblanc/ozz-animation/archive/744eb9d99f606eda849acb0b1204f7a3dc20bca1.tar.gz | 43,532,520 | a29a8a014b571487d9a6dabebeed57627fc19bf1f0ebf531b0c76384840c3b74 |
| entt | 3.16.0 | https://github.com/skypjack/entt/archive/b4e58bdd364ad72246c123a0c28538eab3252672.tar.gz | 912,100 | 3e996cf255b09527faf995c7c36e3daf92cefa0fb37540a4b9c359af557e19cd |
| stockfish | sf_19 | https://github.com/official-stockfish/Stockfish/archive/edb0d9db6731067ec50ce619ff372b463bc4dd5d.tar.gz | 291,397 | 4fc20699a5ecf7883b036ce180020f5e57979623ad719fd2a52839209521581b |
| meshoptimizer | 1.3 | https://github.com/zeux/meshoptimizer/archive/9e1f07b159d3cb777f1c67ed31fc11fd117986f4.tar.gz | 610,285 | e753b45fbc410031bd69cb278180ae31fa0d5430d0c3e662e3a3b100467ce0b3 |
| earcut | 3.2.4 | https://github.com/mapbox/earcut.hpp/archive/92acda9e2ed96ff1f910cda35de444727e9da7b0.tar.gz | 97,490 | 799dc5d93478f74ca5331eaba935946efa25772f00dc7274005e07e296d469a8 |
| delaunator-cpp | 0.4.0 | https://github.com/delfrrr/delaunator-cpp/archive/393cfc39c9b1ca268081d5f42062de0d9b33f5a2.tar.gz | 2,289,865 | 61deec54e3e2e64e4fb487890f27f2b94e24e3957b784f22f332f87e594adaa9 |
| nanoflann | 1.10.0 | https://github.com/jlblancoc/nanoflann/archive/57d2d8c83c862b66f4689b082423e31314ad27ec.tar.gz | 550,018 | c84a1cbd90d26813859d87c43f71ca4363e4df777154cb7bbdedf3feb856864d |
| nanort | release 2024-11-10 | https://github.com/lighttransport/nanort/archive/cdf474ae9176b87a9334c858bb06c9e028ed0e0d.tar.gz | 29,506,236 | 99c011d695b8e158ce317ab5d47aa69f6c5ad272062ab26801f15f56b7122e49 |
| draco | 1.5.7 | https://github.com/google/draco/archive/8786740086a9f4d83f44aa83badfbea4dce7a1b5.tar.gz | 60,469,150 | b9c2392dbfcf454aaec68823d832de9d62614054b33807b7c9776799b8e0bbca |
| imath | 3.2.3 | https://github.com/AcademySoftwareFoundation/Imath/archive/5f27ba266d3ea1565e912570c30b5eafc89959f1.tar.gz | 696,698 | b3a8de8b9dfcf4e5387e1ab3ca67c858e7fd05d1faa2e55decc3ee715e034cb8 |
| tinyrenderer | master 2026-07-29 | https://github.com/ssloy/tinyrenderer/archive/97eb7a480e762285899a93c5d21e70a79e60782e.tar.gz | 35,926,909 | 8c809f60fe1869897c6eb70afb13fb43108bcc4169805341e4352cc421348c30 |
| xtensor | 0.27.1 | https://github.com/xtensor-stack/xtensor/archive/f115228a7fc277b9be1bef34572831f8fd53ac73.tar.gz | 1,225,961 | fad3c8e944bb6e1f1909c291aeb6f7bd3859055e2783bca9acd50c3b74d40880 |
| xtensor | 0.27.1 | https://github.com/xtensor-stack/xtl/archive/c52350e283b98e5d69dbc50726925a1f8e16c57c.tar.gz | 138,877 | dc659dacad0edcd263d994027b0e397768d6f951a65991b4357f4dd11414648d |
| spectra | 1.2.0 | https://github.com/yixuan/spectra/archive/6841bcbacaa0f0a8446210314e682057a084be4e.tar.gz | 293,122 | e9a485e5faf6ee3c42a8904b65dd0bf2f809665e28d80b4a52f2d21c7838902b |
| spectra | 1.2.0 | https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz | 2,705,005 | 8586084f71f9bde545ee7fa6d00288b264a2b7ac3607b974e54d13e7162c1c72 |
| pocketfft | cpp 2026-06-30 | https://github.com/mreineck/pocketfft/archive/c90e55b3d529f8efa40ed01a20de22405f45fc65.tar.gz | 28,485 | 2d90016da31a8cc1dd0ac0c89c1f2fb55df8f4ccc3f0386dcfbad09ac6d1c3ba |
| cimg | 3.7.6 | https://github.com/GreycLab/CImg/archive/49b29ef7e3230b05f9924c5f79bf92da1c58c5a8.tar.gz | 12,701,473 | 42b0c5eaee38fe58aadb77aaad2825d6a52363cf0e9631e084c8505182af363d |
| lightgbm | 4.7.0 | https://github.com/microsoft/LightGBM/archive/8f7036f03627054d5a54a6f965b13f4b9ff2cb63.tar.gz | 6,350,136 | 35cb44a8ca923ed696d917c7455563260c54e57e8c1ee6b93d5680ac9d4b4250 |
| lightgbm | 4.7.0 | https://github.com/fmtlib/fmt/archive/8303d140a1a11f19b982a9f664bbe59a1ccda3f4.tar.gz | 702,766 | dca18efa83961de689594ac560108d3e1ed64179fcc058c58e8ecdc124ab92e9 |
| lightgbm | 4.7.0 | https://github.com/lemire/fast_double_parser/archive/252029ddac664370bdda3f0761675785d92a1573.tar.gz | 637,038 | 12c63a935cf261ec12be3357f791cb25a3adc61ae8035406dc6681b89e101447 |
| lightgbm | 4.7.0 | https://gitlab.com/libeigen/eigen/-/archive/3147391d946bb4b6c68edd901f2add6ac1f31f8c/eigen-3147391d946bb4b6c68edd901f2add6ac1f31f8c.tar.gz | 2,710,482 | 0c8c490764f9c2a793133491adca0cd073b73e0bde965c68cbe58d91b5ed4261 |
| lightgbm | 4.7.0 | https://github.com/apache/arrow-nanoarrow/archive/a579fbf5d192e85b6249935e117de7d02a6dc4e9.tar.gz | 1,095,567 | f1826116664ee876a14f0cc0a407b3d1f3bed642b78f9b1ea03d2351fb15a19e |
| tiny-dnn | master 2018-10-23 | https://github.com/tiny-dnn/tiny-dnn/archive/c0f576f5cb7b35893f62127cb7aec18f77a3bcc5.tar.gz | 18,935,508 | 123dabe15b019938e04c7ccdd22c8423ceae091f4bd2fb878f972a2ea031d4b9 |
| llama.cpp | v0.6.0 | https://github.com/ggml-org/llama.cpp/archive/d81235049384534c167caea52b85a694f6103d14.tar.gz | 37,887,730 | 6b58785f0a82898f4c3442417ff962e2d4b231b1bee5d033902ad90b27901e14 |
| whisper.cpp | v1.9.5 | https://github.com/ggml-org/whisper.cpp/archive/d1be6fde11ac6e0407606b4e42fe72d34add8037.tar.gz | 9,631,456 | 645445da884df6dbd52b30f82d7be7c01d1767c938714e477e786b88d529e9f4 |
| hnswlib | 0.9.0 | https://github.com/nmslib/hnswlib/archive/d9b3608c83d83b46c96e25088cb1d729b29dcfe9.tar.gz | 67,545 | d7e12ea0604bd6d6753aab403e8cb177b95697968722e0154e8f68a31278f26e |
| annoy | 1.17.3 | https://github.com/spotify/annoy/archive/75429e5dc930754698f1d37c44ea189a7521c7a3.tar.gz | 673,505 | 262637d7adbf906e955a4ad2d04ce9bb73b630abbb63f2bb1131d9fb412e84cb |
| kanzi | 2.6.0 | https://github.com/flanglet/kanzi-cpp/archive/1330414143be82209e0a0860d2b9f8ab567c94b5.tar.gz | 398,063 | cc429f622947ca43254fa05c662ca2261bc8f8e25e770a1324a36c38580c20ea |

Build notes: leveldb 1.23 (the last release) does not compile as C++20 (`std::memory_order::memory_order_relaxed`
in `util/env_posix.cc`), so leveldb is pinned at a later main commit that fixes it. ninja is
compiled without `-Isrc`, as its CMake does, so `<getopt.h>` is the system one. The GitLab archive
for Eigen is generated on request; if GitLab ever regenerates it with different bytes, the sha256
check stops the run rather than using an unchecked file.

## Census 1 limits (as written for run 38259934735)

- Counts, not cost: no hotness, no runtime claim (see above).
- A loop counts once per function it was compiled into; a header loop inlined into three
  functions counts three times. `vectorized_unique` gives the distinct source locations per project.
- Header-only libraries are measured only through what their driver instantiates.
- The lost-loop classes are a regular-expression heuristic over the source text.
- One toolchain and target (clang 18, libc++ 18, `-O2`, SSE2), FAST mode only; a wider target
  (`-march=x86-64-v3`) vectorizes more loops and could lose more.
- 19 open-source libraries chosen for variety (parsers, numeric, compression, storage, logging,
  a build tool, geometry, an image codec), not a random sample of C++ code.
