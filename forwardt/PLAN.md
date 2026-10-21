# forwardt: what a lost forward loop with a variable bound costs in time (plan, fixed before any code and any run)

This text was fixed at 15:30 EDT on Wed Oct 21, 2026 (the author's machine clock, read just before the commit),
before `forwardt/` held any other file and before any run of any kind, a code test and a smoke run included. In the
author's unpublished development history it is committed on its own.

Every `forwardt.json` stores the SHA-256 of this file as the job's checkout held it, that is, in the commit stored as
`run.commit` (line endings read as LF). `forwardt/analyze.py` treats a measurement file (one whose `smoke` field is
false) whose stored hash differs from the hash of this file as it stands as a file problem (rule 7). The data therefore
show a change to this file made in a commit after the one a measurement run was started from, as a file problem in the
files of that run. They do not show a change made in or before the commit the earliest measurement run was started from,
including a change made after a code test or a smoke run, because the stored and the compared hash then change together.
Every change to this file made after the first commit, up to and including the commit the earliest measurement run is
started from, is listed, with date and reason, under "Changes made after the first commit". A smoke file whose stored
hash differs is listed with a note (rule 13) and decides nothing. As a cross-check, `forwardt/analyze.py` holds the
SHA-256 of the first-commit text (`FIRST_COMMIT_PLAN_SHA256`, set in a commit after the one that holds this file) and
prints a note beside every word and outcome when a stored hash differs from it. The note flags a mismatch and does not
show when a change was made; because the constant sits in code the author can edit, it is a record the author keeps and
not independent evidence.

The order of events (this file committed alone, then the code, then the first run of any kind) is in the author's
unpublished development history. It rests on the author's clock and cannot be checked from this repository unless the
first public commit that holds this file holds none of the other files of `forwardt/`; the report names that commit and
lists what else it holds. What a reader can check is this: each result file stores the SHA-256 of this file and the
commit of its run, that commit holds this file, and GitHub records the creation time of the run, so the text hashed in a
file existed no later than the creation of that run. The report lists that creation time, in UTC, for every Actions run
of this question, code tests and restarted runs included (see "Runs"), beside the time stamped above converted to UTC,
and says that these times fix when each run began and not when this file was written.

No timing of the six functions below exists, with two near-exceptions that the bands use: `t01_sum_size` has the loop
and bound of `k01_sum_fwd`, and `t03_scale_size` has the loop of `k02_add_fwd` with one input array fewer and a multiply
for the add; P1 is therefore close to a repeat of those kernels' timings with another driver. Every band is derived from
a stored number, with the derivation beside it, or is marked as a guess. The plan follows `harness/criteria-v3.json` and
`dsweep/` (statistic, seed rule, pooling per CPU model, 2.0 % ceiling, 3-job minimum, plan hash in every result file)
and names each departure. Two of them: a smoke file is set aside and is not a file problem (rule 1), where
`dsweep/analyze.py` makes it a file problem of its model; and two files of one model from different commits are a file
problem (rule 7), where `dsweep/analyze.py` compares code hashes only.

## Changes made after the first commit

None. This list is empty when this file is first committed.

## Question

`forwardn/README.md` compiled 18 small functions with nine clang versions, each with the hardening macro its libc++
offers (`_LIBCPP_ENABLE_ASSERTIONS` on 16.0.0, which turns on all assertions and has no separate fast mode;
`_LIBCPP_ENABLE_HARDENED_MODE` on 17.0.1; FAST on 18.1.0 and later). On clang 16.0.0 to 18.1.0, with that macro on, a
forward loop whose bound is a variable and not `size()` stops being vectorized on x86-64 at `-O2`: the sums (`s += a[i]`
in four counter types, and with the bound in a struct member), `c[i] = i * 3` and `c[i + off] = a[i]` are **lost**;
`c[i] = a[i] * 2` with bound `n` is only **narrower**. `size()`-bounded twins exist for the sum and the scale (both
**kept**) and not for the other two. The loop census (`corpus/README.md`, clang 18) counts 444 lost loops, one per
function a loop was compiled into (331 of them template instances from one project, LightGBM); 228 of them, at 38 source
locations, fall in its class "forward loop bounded by a variable", assigned by a text pattern on the loop header and
body. `forwardn` is compile-only; this plan times six functions.

**What is the pooled FAST/NONE ratio, with its 95 % interval, of each of the six loops on the Ubuntu clang 18.1.3, in
cache (L1 and L2; as compiled and aligned), for each CPU model?** The answer is those ratios and the outcome of P0 to P6
below; each loop is read against those bands and no others. `t02_sum_n` and `t04_scale_n` are shown beside their
`size()`-bounded controls `t01_sum_size` and `t03_scale_size`, which differ in the bound alone; `t05_fill_n` and
`t06_offset` have no control and are read against P3, P5 and P6 only. The study's reference ranges (about 1.0x for
forward loops, 2.8x to 8.0x for loops that lose SIMD) are context and not thresholds; wherever the write-up uses a word
such as "cheap" or "close to", it gives the ratio and interval beside it.

## Published numbers this relates to (context, not new data)

- `kernels/k01_sum_fwd.cpp`: a sum over `int32` into `int64`, bound `a.size()`; vectorized in both builds (width 2), the
  assembly of `kern_k01_sum_fwd` identical in FAST and NONE (0 traps). Built with vectorization switched off by hand it
  takes, as NOVEC against NONE pooled per CPU model (`results/s7-pooled/pooled.json`, `positive` blocks, L1 / L2):
  1.281 / 1.271 as long on EPYC 7763 (29 jobs), 1.291 / 1.290 on EPYC 9V74 (28 jobs), 1.089 / 1.088 on EPYC 9V45 (23
  jobs; the single job of `docs/dayone-results.md`, run 38116223923, gave 1.087 and 1.090), 0.976 / 0.972 on the Xeon
  8573C (7 jobs) and 0.978 / 0.945 on the Xeon 6973P-C (7 jobs; the interval at L2 is 0.929 to 0.968). On each of the
  five x86-64 CPU models with 7 or more jobs its FAST/NONE is 0.996 to 1.003 as a point value in both columns at L1 and
  L2.
- `kernels/k02_add_fwd.cpp`: `c[i] = a[i] + b[i]`, bound `a.size()`, width 4; FAST differs from NONE only in the
  interleave count (`investigate/FINDINGS.md`). With vectorization off it takes 2.585x (L1) and 2.609x (L2) as long as
  NONE (the same EPYC 9V45 job). Aligned column (point values, `results/s7-pooled/pooled.json`, models with 7 or more
  jobs): at L1 0.825 (EPYC 9V74), 0.837 (EPYC 7763), 0.845 (EPYC 9V45), 1.058 (Xeon 8573C), 1.199 (Xeon 6973P-C;
  interval 1.188 to 1.204); at L2 0.904 (EPYC 9V45), 0.961 (Xeon 6973P-C), 0.974 (Xeon 8573C), 0.999 (EPYC 9V74), 1.003
  (EPYC 7763); a single earlier run gave 0.82 to 0.86 at L1 on the three AMD models (`investigate/FINDINGS.md`); as
  compiled it was 1.585 and 1.597 on EPYC 7763 and 9V74 at L1 through code placement alone; on Neoverse-N2 0.986 to
  1.007 (`results/s8-arm-pooled/pooled.json`).
- `kernels/k08_matmul.cpp`, the one timed kernel of the main study with a run-time bound that is not `size()`: the inner
  loop `for (j = 0; j < d; ++j) c[i*d+j] += aik * b[k*d+j]` sits in a three-deep nest timed as a whole. Under FAST on
  x86-64 with clang 18.1.3 it is not vectorized ("the cost-model indicates that vectorization is not beneficial"); on
  EPYC 7763 at L1 (d = 36) it takes 3.190x as long as NONE as compiled (interval 3.176 to 3.205; 29 jobs,
  `results/s7-pooled/pooled.json`). On Neoverse-N2 it keeps NEON in both builds and still takes 1.548x at L1
  (`arm64/README.md`). Its cause of loss is not tested here.
- Loops that lose SIMD under FAST in the main study (reverse, stride-2, matrix multiply on x86-64): 2.8x to 8.0x in
  cache. On EPYC 7763 at L1, vectorization switched off by hand against the checked build as compiled: reverse 3.3x
  against 7.6x, stride-2 2.6x against 5.1x, matrix multiply 1.6x against 3.2x (`README.md`); the check roughly doubles
  the cost of the scalar loop (2.0 to 2.3).

## What is timed

**Loops.** Six functions, one source file each in `forwardt/kernels/`, in the shape of `kernels/k02_add_fwd.cpp`: a
`noinline` function `kern_<name>`, one `// LOOP` comment on the loop line, and the driver and checksum of
`kernels/common.hpp`, included from `../../kernels/common.hpp` as it stands (not edited). Each `kern_<name>` has the
parameters and loop of one function of `forwardn/source.cpp` (table); the counter has the type of the bound; a sum is
stored through an `int64_t* out` parameter and not returned. Data are `int32_t` vectors; sums accumulate into `int64_t`.

| name | loop | bound | = `forwardn` function | word on clang 18, x86-64 `-O2` (`forwardn`) |
|---|---|---|---|---|
| `t01_sum_size` | `s += a[i]` | `a.size()` (no `n`) | `fwn_sum_size` | kept (control) |
| `t02_sum_n` | `s += a[i]` | `n` (`size_t`) | `fwn_sum_n_size_t` | **lost** |
| `t03_scale_size` | `c[i] = a[i] * 2` | `a.size()` (no `n`) | `fwn_scale_size` | kept (control) |
| `t04_scale_n` | `c[i] = a[i] * 2` | `n` (`size_t`) | `fwn_scale_n_size_t` | narrower |
| `t05_fill_n` | `c[i] = i * 3` | `n` (`int`), only `c` | `fwn_fill_n` | **lost** |
| `t06_offset` | `c[i + off] = a[i]` | `n` and `off` (`int`) | `fwn_scale_offset` | **lost** |

For `t02`, `t04`, `t05`, `t06` the bound `n` is a parameter equal at run time to the length of the vectors (for `t05`,
of `c`, its only vector), so the compiler cannot use the equality; the driver allocates exactly the vectors the function
takes, each of `n` elements (`c` of `t06` has `n + off` elements). The command line is `<n> <iterations>` for `t01` to
`t05` and `<n> <iterations> <off>` for `t06`; `off` is read as an `int` from argv[3] in `t06`'s own `main`
(`common.hpp`'s `parse_args` reads two arguments), is 0 in every run, and comes from argv so that the compiler cannot see
it. The driver parses `n` as `size_t` and converts it with `static_cast` at the call.

`harness/run.py`'s `calibrate`, `calibrate_args` and `instr_count` cannot carry a third argument: `calibrate` runs the
binary with `<n> 1`, `instr_count` with `<n> 20`, and `calibrate_args` puts the iteration count last.
`forwardt/sweep.py` therefore carries its own `calibrate` and `instr_count`, used for all six loops, with the method of
the harness's (best of three runs at one iteration; iteration count `int(round(TARGET_NS / best))` clamped to 1 to
10,000,000, with `TARGET_NS` and `CG_ITERS` read from `harness/run.py` and not restated; Cachegrind instructions of
`kern_<name>` divided by `CG_ITERS + 1` calls, the one untimed warm-up call that every `main` makes, as in
`kernels/k02_add_fwd.cpp`, included). It builds each argument list itself: `[n, iterations]` for `t01` to `t05` and
`[n, iterations, off]` for `t06`, with `off` = 0, in the calibration call (iterations = 1), the Cachegrind call
(iterations = `CG_ITERS`) and every timed call. `harness/run.py`'s `pair` is used as it stands with the full list. A unit
test, with a stub in place of the binary, checks the exact lists of the three calls for `t06` (`[n, 1, 0]`, `[n, 20, 0]`,
`[n, iterations, 0]`) and the two-entry lists for one of `t01` to `t05`.

**Builds.** The four builds of the main study, each compiled once per loop with `clang++-18 -O2 -std=c++20
-stdlib=libc++` and the flags of `harness/run.py`: `none`, `fast`, and the same two with `-falign-loops=64` (`none_a64`,
`fast_a64`); plus `novec` (the `none` flags plus `-fno-vectorize`, without `-falign-loops`). `harness/run.py`'s
`build_kernel` hard-codes `kernels/<name>.cpp`, so `forwardt/sweep.py` carries its own `build_kernel` with the flag
tables imported from `harness/run.py`; the harness is not edited. Loop-vectorize remarks, the trap count
(`harness/asm.py`), the assembly of `kern_<name>` and the hot-loop placement (`harness/placement.py`) are stored for
every build, as in the main study.

**Sizes.** L1 and L2 by the rule of `harness/run.py`'s `n_for` and `working_set`: `n = max(64, target_bytes //
bytes_per_element)`, `target_bytes` being half of L1d or half of L2 from `/sys/devices/system/cpu/cpu0/cache`, counting
every array the function takes. The table of bytes per element is in `forwardt/sweep.py`: `t01` 4 (a), `t02` 4 (a),
`t03` 8 (a, c), `t04` 8 (a, c), `t05` 4 (c only), `t06` 8 (a, c); `t01` and `t02` share one `n` per size, so do `t03`
and `t04`. Examples: Neoverse-N2 (L1d 64 KiB, L2 1024 KiB per core, `arm64/README.md`): L1 `n` = 8192 for `t01`, `t02`,
`t05` and 4096 for `t03`, `t04`, `t06`; L2 131072 and 65536. Each file stores the cache sizes it read and its `n`; the
analysis recomputes `n` from them. RAM is not timed.

**Timing**, from `harness/criteria-v3.json` (read at run time): `v3.timing.reps_per_side` = 40 processes per side, ABBA
order, each process pinned with `taskset -c` to one CPU (`HARNESS_CPU`, default 1), the iteration count calibrated once
per cell on `none` as compiled to about 75 ms per process and reused for every build of that cell. A cell is one loop at
one size. Pairs per cell: FAST against NONE as compiled (`compiled`); FAST against NONE aligned (`aligned`); an
identical-binary A/A (`aa`: `none` against a byte-identical copy, hash checked before timing); and, for the loops among
`t02`, `t04`, `t05`, `t06` whose `none` loop is vectorized, NOVEC against NONE (`novec`: A = `none`, B = `novec`; one
column, no aligned counterpart). The two sides of every pair print the same checksum, `novec` that of `none`, or the job
stops. A job appends every finished cell to `forwardt.partial.jsonl`, removed when `forwardt.json` is written. Two
departures from criteria-v3, which times one A/A per job at `k02_add_fwd` L1 and the `novec` build only inside the
main kernels: the A/A is timed per cell, and the `novec` pair is timed for these four loops. Secondary,
labelled instructions and not time: Cachegrind counts (`forwardt/sweep.py`'s own `instr_count`, the method of
`harness/run.py`'s with `off` appended for `t06`) of `none` and `fast` at L1 for each loop.

## Words per loop

Every job stores, for the loop line of each of the four builds, the last remark `vectorized loop (vectorization width:
W, interleaved count: I)` clang printed at the `// LOOP` line, with W and I parsed from its text (the harness's
`remarks.vectorization()` parses only the width W from the last "vectorized loop" remark and returns it with the remark
messages; `forwardt` parses I from the text of that same last remark). A build is "vectorized" only if that remark
exists at the loop line. The word of a loop in a job is computed from `none` and `fast` as compiled and from nothing
else: **lost** = vectorized in `none` and not in `fast`; **narrower** = vectorized in both with (W, I) different;
**kept** = vectorized in both with the same (W, I); **scalar in both** = vectorized in neither; **gained** = vectorized
in `fast` and not in `none`. `forwardt`'s code carries this rule (it does not import `forwardn/run.py`), and a test
checks that it returns `forwardn`'s word on one case of each of the five. The direction of a "narrower" (smaller or
larger W*I in FAST) is stored and printed. The words of the aligned pair are stored, must agree with the as-compiled
ones or the model has a file problem (rule 7), and do not set the loop's word. Words are read from complete
`forwardt.json` files that are not smoke files only. On a CPU model without a file problem every job stores the same
remark for `none` and for `fast` of each loop (its (W, I) or its absence) and the same binaries (rule 7), so the jobs
give a loop the same word, which is the word of the loop on that model. Trap counts (`asm.count_traps` of
`kern_<name>`) are stored for all builds; the controls' counts are reported and nothing is predicted for them.

## Predictions

Written now, from the stored numbers above, the compile-only results of `forwardn/` and the loops as written in the
table; not from a timing of these loops and not from any code of `forwardt/`. Except P0, which its own paragraph
governs, they are read by rules 1 and 4 and 7 to 11 below: a prediction is judged on the decidable cells it names, in the
columns it names, against a closed band. A band "at most X" is 0 to X; "above X" is X to infinity; no band has an edge at
1.00. Unless a prediction names a column it names both `compiled` and `aligned`; for P2, P3 and P5 the two columns are
read as a pair (rule 9). The targets named below ("x86-64", "Neoverse-N2") are assigned to CPU models by rule 1.

A loop has its predicted word on a CPU model when its word there ("Words per loop") is the word the P0 line predicts for
that target; P0's trap clause does not decide this. A prediction that names one or more loops is judged, on each CPU
model, only on the loops that have their predicted word there. A loop that does not is left out of that prediction on
that model: its combinations are not combinations the prediction names there, and it is printed with its word and its
ratios. A prediction is not testable on a model only when no loop it names has its predicted word there. P0 itself is
judged per loop, as its own paragraph says, and is not subject to this rule.

- **P0 (the words).** On x86-64: `t01` and `t03` kept, `t04` narrower, `t02`, `t05` and `t06` lost; each of the four
  loops with bound `n` has at least one trap in FAST. On Neoverse-N2, where `forwardn` found the sums with a variable
  bound lost on 16.0.0 to 18.1.0 and the three single-store writes (`scale_n_size_t`, `fill_n`, `scale_offset`) kept on
  every one of the nine versions at AArch64 `-O2` (the other write loops of `forwardn` are not timed): `t02` lost; `t01`,
  `t03`, `t04`, `t05`, `t06` kept; the same trap clause. (Compiler Explorer's builds are not the Ubuntu 18.1.3 that is
  timed; P0 tests that difference.) P0 is read by this paragraph, rule 1 (the 3-job minimum, counted in complete files
  that are not smoke files), rule 5 (the words), rule 7 (file problems) and rule 11. Rules 4, 8, 9 and 10 do not apply to
  it: it names no cell and no band, and no A/A half-width bears on it. It is twelve predictions, P0.t01 to P0.t06 on each
  target (for example P0.t04 on Neoverse-N2), each with the predicted word listed above. The trap clause belongs to
  P0.t02, P0.t04, P0.t05 and P0.t06 only; P0.t01 and P0.t03 are the word alone. Each is read per CPU model, in this
  order. (1) The model has fewer than 3 complete files, or a file problem (rule 7, including the aligned-word clause):
  not testable. (2) Otherwise the jobs agree on the word (rule 7 makes disagreement a file problem), and the prediction
  holds when that word is the predicted one and, where the trap clause applies, the common FAST trap count of
  `kern_<name>` is at least 1; it fails when either is not so. Each of the twelve is then summarised over the CPU models
  of its target by rule 11, with the loop and the target named. No single word is given for P0 as a whole, for a loop
  across the two targets, or for a model across loops. The page prints the grid of six loops by two targets; each cell
  gives the rule 11 word and, for each CPU model of the target, the observed word and the FAST trap count beside the
  predicted word.
- **P1 (controls stay inside bands set from their relatives in the main study).** `t01_sum_size`, every model of
  either target (rule 1), both columns, L1 and L2: inside 0.97 to 1.03. Derivation: the stored `k01_sum_fwd`, which compiles to the same code in both
  builds, is 0.996 to 1.003 as a point value in both columns; the edges are about 0.03 beyond it (0.97 is 0.026 below
  0.996 and 1.03 is 0.027 above 1.003), a judgement that leaves room for the 2.0 % A/A ceiling. `t03_scale_size` on
  x86-64: **aligned column** only, L1 and L2, inside 0.79 to 1.23. Derivation: the stored aligned point values of
  `k02_add_fwd`, L1 and L2, over the five models with 7 or more jobs (`results/s7-pooled/pooled.json`) run from 0.8250
  (EPYC 9V74, L1) to 1.1985 (Xeon 6973P-C, L1). The edges are those two values moved 0.03 outward (0.7950 and 1.2285)
  and rounded outward to two decimals. The 95 % intervals of both stored extremes (0.8246 to 0.8253 and 1.1879 to 1.2043)
  lie inside the band, so a cell that repeats either one can hold P1. The span is wide because the stored aligned ratio
  of `k02_add_fwd` itself differs that much between models; the plan does not explain it. A `t03` cell inside the band
  holds P1 and is reported as "inside the band set from the stored aligned range of `k02_add_fwd`", with its ratio and
  interval; "near 1" is said only of a cell whose interval is inside 0.97 to 1.03. The as-compiled column is reported
  beside it and carries no word, because `k02_add_fwd` as compiled reached 1.585 and 1.597 through code placement alone.
  `t03_scale_size` on Neoverse-N2: both columns, L1 and L2, inside 0.97 to 1.03 (stored `k02_add_fwd` 0.986 to 1.007).
  P1 is read on single combinations (rule 9): an interval outside the band in either column fails it, so a control does
  not pass with one column outside.
- **P2 (lost sums cost at most 1.35x).** `t02_sum_n`, x86-64, both columns read as a pair, L1 and L2: inside 0.97 to
  1.35. The lower edge is the `t01` band's: an interval around a true ratio of 1.00 in a decidable cell may reach 0.98.
  On the Xeons the stored NOVEC/NONE of `k01` is 0.945 to 0.978, so a ratio below 0.97 is not excluded there; it is
  registered as a failure below 0.97 (row G or K of the outcomes). The upper edge is a guess anchored on the stored
  NOVEC/NONE of `k01`, the width-2 sum loop this loop loses: 1.09 on EPYC 9V45 and 1.28 to 1.29 on EPYC 7763 and 9V74.
  1.35 is 1.24 times the first and 1.05 times the other two, so on 7763 and 9V74 P2 holds only if what FAST adds costs at
  most about 5 % on top of a scalar sum that already takes 1.28x to 1.29x as long, and on 9V45 at most about 24 %
  (arithmetic: 1.35 / 1.29 = 1.05, 1.35 / 1.28 = 1.05, 1.35 / 1.09 = 1.24). The hypothesis, not a stored fact: the
  compare and branch FAST adds sit beside the loop-carried add of a sum and cost little. The three stored lost loops
  point the other way (the check roughly doubles their scalar cost); those loops have independent iterations and a sum
  has a dependency chain, so this prediction bets that the doubling does not carry over. If it did, the ratio would be
  about 2 x 1.09 = 2.2 on 9V45 and about 2 x 1.29 = 2.6 on 7763 and 9V74 (arithmetic). **P2 may well fail.**
  **P2n:** the `novec` column (A = `none`, B = `novec`; rule 3) of `t02_sum_n`, x86-64, L1 and L2: inside 0.90 to 1.35.
  It names the `novec` column only and neither `compiled` nor `aligned`. `k01` is the same sum with a `size()` bound; its
  stored NOVEC/NONE point values over the five models run from 0.945 to 1.291, and the lowest interval end is 0.929
  (Xeon 6973P-C, L2). Both edges are guesses: 0.03 below that interval end (0.899, rounded to 0.90) and 0.06 above the
  highest point value (1.351, rounded to 1.35); the upper edge is P2's. P2n applies on a model only where `t02_sum_n` has
  the word lost (P0); that word needs the `none` loop vectorized in every job of the model, so the `novec` pair was timed
  in every job. Where the word is anything else, P2n is not testable there and the `novec` ratios of the jobs that timed
  the pair are reported and read against no band. Its cells are decidable under rule 4. Decided per model and on its own,
  not part of P2.
- **P3 (lost writes cost above 1.5x).** `t05_fill_n` and `t06_offset`, x86-64, L1, both columns read as a pair: above
  1.5. Derivation: the nearest stored write loop with a variable bound, matrix multiply, takes 1.6x as long with
  vectorization off (EPYC 7763) and `k02_add_fwd` 2.6x (one EPYC 9V45 job); 1.5 sits just below the first, so P3 holds
  if these lost writes pay at least about what switching vectorization off accounts for. The checked matrix multiply
  takes 3.2x, a different loop (a nest with two checked subscripts) that sets no band. `forwardn` reads the stop on
  `fill_n` (clang 18) as the cost model ("the cost-model indicates that vectorization is not beneficial") and gives no
  remark for `scale_offset`; that a lost loop is vectorized without the checks shows only that the cost model found a
  vector loop worth building, not how much faster it runs, which is what P3 measures. **P3 may well fail.**
- **P4 (narrower costs at most 1.30x).** `t04_scale_n`, x86-64, **aligned column**, L1 and L2: at most 1.30. Basis:
  `k02_add_fwd`, whose FAST build differs from NONE only in the interleave count, is at most 1.199 aligned over the five
  models; 1.30 is 0.10 above. The as-compiled column is reported beside it and carries no word.
- **P5 (L2 is about L1 for lost loops).** On each x86-64 CPU model, for each of `t02_sum_n`, `t05_fill_n` and
  `t06_offset` that has the word lost on that model, both columns read as a pair: the quotient (pooled ratio at L2) / (pooled ratio at L1) inside 0.80 to 1.25, tested on a model
  only when both sizes of that loop are decidable; computed as in rule 10. The band is a guess, symmetric in the
  logarithm around 1 (a factor of 1.25 either way, 1 / 1.25 = 0.80), and is not computed from the stored quotients, which
  are context only: in the main study (`results/s7-pooled/pooled.json`, point values, both columns) this quotient for
  reverse, stride-2 and matrix multiply is 0.85 to 1.19 on the three AMD EPYC models and, for reverse, 0.57 to 0.66 on
  the Xeon 8573C and 6973P-C. P5 can fail on Intel. P5 is not tested on Neoverse-N2, whatever the words there; the L1
  and L2 ratios of `t02_sum_n` there are reported without a band.
- **P6 (kept writes on Neoverse-N2 stay near 1).** `t05_fill_n` and `t06_offset`, Neoverse-N2, both columns, L1 and L2:
  inside 0.95 to 1.15. Anchor: the stored forward loops on this core (sum, add, stencil; L1 and L2; as compiled and
  aligned) are 0.974 to 1.007 (`arm64/README.md`, table of FAST over NONE; 0.974 is the stencil, aligned, at L1). Both
  edges are guesses: 0.024 below the lowest and 0.143 above the highest of those values. Matrix multiply on the same core
  keeps NEON and still costs 1.548x at L1, so a "kept" word does not by itself predict a ratio near 1; the prediction
  tests whether it does for these two loops. For `t02_sum_n` on Neoverse-N2 (lost) the numbers are reported without a
  band.

Expectation, not a criterion: the stored identical-binary A/A at L2 on Neoverse-N2 (`robustness/aa-l2.json`, k02 L2) is
above 2 % in 24 of 30 jobs and pooled 2.62 %, so the Neoverse-N2 L2 cells are expected not to be decidable; P1 and P6
there would rest on L1 alone and P5 would not be tested. The A/A of each new cell decides.

## How it is analysed (fixed now)

1. **Unit.** One CPU model, keyed by the exact `run.runner.cpu_model` string; every `forwardt.json` of the model in the
   `measurement` entries of `forwardt/runs.json` (see "Runs") that is neither a smoke file nor a partial file is pooled.
   Before any file is assigned to a CPU model, every file whose top-level `smoke` field is true is set aside. `smoke` is
   true exactly when the repetitions per side the run used differ from `v3.timing.reps_per_side` (as in
   `dsweep/sweep.py`); a run whose `reps` input is empty or equals that number writes `smoke: false`. A smoke file is
   listed as refused with its path; no content of it other than that field, its stored plan hash (rule 13) and its
   repetition count is used; it is not counted toward the 3-job minimum, takes no place in the job order below, and is
   not a file problem of any model. No job is excluded on its own A/A or any other per-job statistic
   (`v3.pooling.no_per_job_exclusion`). At least 3 jobs of a model are needed to read it (`v3.pooling.minimum_jobs`);
   with 3 to 5 jobs the intervals are coarse and understated (`v3.pooling.few_jobs_caveat`), and the job count is
   printed beside every number. Jobs are taken in the order of `dsweep/analyze.py`'s `_job_key` (run id, length of the job
   name, job name, file SHA-256), so the bootstrap draws do not depend on the folder layout.
   **Targets.** The targets named in P0 to P6 and in rule 11 are assigned per CPU model, from the stored
   `run.runner.cpu_model` and `run.runner.arch` of its jobs and from nothing else. A model belongs to the target
   "Neoverse-N2" when its `cpu_model` is exactly the string `Neoverse-N2` and every job of the model stores `arch` equal
   to `aarch64`. A model belongs to the target "x86-64" when every job of the model stores `arch` equal to `x86_64`. Any
   other model, including another Arm model such as `Neoverse-V3` (the Arm runner has returned one, in
   `results/s9-arm-run-39012932739`), belongs to no target: it is read under rules 1 to 7 like any model, listed with its
   numbers and job count, tests no prediction and is not counted in rule 11. A job whose `cpu_model` or `arch` is missing
   or empty, and jobs of one model that store different `arch` values, are a file problem under rule 7. A file with no
   `cpu_model` is a file problem of the key `unknown` only: it is listed, not pooled, and belongs to no target. A
   prediction stated for "x86-64" or for "Neoverse-N2" is read on the models of that target only.
2. **Statistic**, calling the functions of `harness/pool.py`: per job, the ratio of the median of side B to the median of
   side A; the pooled ratio is the geometric mean over the jobs of the model; the interval is the two-level percentile
   bootstrap with `RESAMPLES` = 2000 (draw the jobs with replacement, then redraw each side's repetitions inside each
   drawn job; positions 50 and 1949 of the 2000 sorted values), the splitmix64 generator and the seed rule
   `sha256("20261011|<cpu_model>|<stat_id>|<stream>")` with streams `jobs`, `side0`, `side1` (and `side2`, `side3` for
   the four-sided `placement` statistic). In every pair side A is drawn with stream `side0` and side B with stream
   `side1`. Stat ids are `forwardt|<loop>|<size>|<column>` with `<size>` in `L1`, `L2` and `<column>` in `compiled`,
   `aligned`, `novec`, `aa`, `placement`, and `forwardt|<loop>|<column>|joint` for rule 10. `forwardt/analyze.py` calls
   `pool.py`; its tests recompute a sample with an independent implementation, as `harness/pool_check.py` does for
   `pool.py`.
3. **Pairs.** `compiled`: A = `none`, B = `fast`. `aligned`: A = `none_a64`, B = `fast_a64`. `novec`: A = `none`,
   B = `novec`. `aa`: A = `none`, B = its copy. The `aa` of a cell gates every pair timed in that cell: `compiled`,
   `aligned` and `novec`. The half-width is (ci95_hi - ci95_lo) / 2 * 100. `placement` (rule 12): the four sides `none`
   and `fast` of the `compiled` pair and `none_a64` and `fast_a64` of the `aligned` pair of one cell, in this order as
   sides 0 to 3 (streams `side0` to `side3`); the per-job ratio is (median `fast` / median `none`) / (median `fast_a64` /
   median `none_a64`), computed by `harness/pool.py`'s `placement_stat` with stat id `forwardt|<loop>|<size>|placement`;
   its half-width is not used by any rule.
4. **Decidable cell.** A cell of a model is decidable when at least 3 jobs of the model returned it and its pooled `aa`
   half-width is at most 2.0 % (`verdict.aa_half_width_max_pct`). A cell above the ceiling is reported with its
   numbers, is **not decidable**, and neither holds nor fails any prediction that names it.
5. **Words** are read as under "Words per loop".
6. **Forward test** (used only for the words of the outcomes): a decidable cell is **inside the forward range** when its
   pooled aligned ratio is at most `verdict.forward_point_max_ratio` (1.02) and its aligned ci95_hi is at most 1 +
   max(`verdict.forward_ci_hi_floor_pct`, `verdict.forward_ci_hi_aa_multiplier` x its `aa` half-width) / 100, the clause
   of `v3.verdict_per_cpu_model` for forward cells. Its placement-sensitive exclusion is not applied; the placement
   statistic is reported (rule 12).
7. **File problems.** A complete file that is not a smoke file has a file problem when: its stored plan hash is not the
   hash of this file as it stands; its stored criteria hash is not that of `harness/criteria-v3.json` as it stands; its
   `smoke` field is false and its repetitions per side differ from the number in `harness/criteria-v3.json`; the sizes
   it stores differ from the sizes the rule above gives for the cache sizes stored in the same file; it stores a
   checksum mismatch (a job that meets one stops and writes no `forwardt.json`, so this clause checks the stored values
   on reading); its schema is wrong, which includes a missing `smoke` key and a missing or empty `run.runner.cpu_model`
   or `run.runner.arch`; for any loop, the word of the aligned pair (`none_a64`, `fast_a64`) differs from the word of
   the as-compiled pair; its stored `clang++-18` version string does not contain 18.1.3. Two files of one model also
   have a file problem when their stored `run.commit` differs, or when a stored SHA-256 of a code file or of a binary, a
   stored trap count, the remark stored for a build (its (W, I) or its absence), the stored cache sizes or the stored
   sizes `n` differ between them, or the repetitions of a pair are unequal (comparing `run.commit` goes beyond
   `dsweep/analyze.py`, which compares code hashes only). A plan text in which the line that states the time of fixing
   still holds a double-underscore placeholder in place of a time is a file problem of every model;
   `forwardt/analyze.py` tests this with a regular expression for a double-underscore token in the first five lines. A
   file problem in any file of a CPU model gives every prediction on that model the word **not testable**; nothing from
   that model is pooled and the files and their problems are listed. A partial file (a job that stopped after its first
   timing, a checksum-mismatch stop included) is not a file problem: it is listed with the reason the job stopped, is
   not pooled and is not counted as a job of its model in any rule. A smoke file is treated alike (rule 1).
8. **Bands.** A pooled interval is **inside** a closed band when ci95_lo >= the lower edge and ci95_hi <= the upper edge,
   and **outside** when ci95_hi < the lower edge or ci95_lo > the upper edge. An interval that contains 1.00 is printed
   as such (indistinguishable from no cost at this noise) and decides nothing by itself.
9. **Prediction on a model.** A prediction names combinations of loop, size and column (on a model, those of the loops
   that have their predicted word there). P1, P2n, P4 and P6 are read on single combinations. P2, P3 and P5 are read on
   **pairs**: the two columns of one loop at one size (P2, P3), or of one loop over both sizes (P5, rule 10). The as-
   compiled and the aligned column of a lost loop can differ through placement alone: `k04_rev` at L1 on EPYC 9V74 reads
   6.56 as compiled and 5.37 aligned in one run of 3 jobs (run 38674961339, `results/s7-pooled/pooled.json`), and
   `k02_add_fwd` at L1 on EPYC 7763 reads 1.585 and 0.837. The `aa` of the cell gates both columns (rule 3), so a pair
   is decidable or it is not. A pair is **inside** a band when both columns are inside; **outside** when both columns are
   outside on the same side (both below the lower edge or both above the upper edge); **split** in every other case,
   including one column inside and the other outside, either column straddling an edge, and one column below and the
   other above a two-sided band. A split pair is never counted as inside. On a CPU model a prediction **holds** when it
   names at least one decidable combination (or pair) and every decidable combination (or pair) it names is inside; it
   **fails** (below, above or both, naming every side that occurs) when at least one decidable combination (or pair) is
   outside, whatever the others show; it is **undecided** otherwise; it is **not testable** when no combination it names
   is decidable, when a file problem applies, or when no loop it names has the predicted word there. For every split
   pair the report prints both intervals under the words "columns disagree" and states how many undecided predictions
   rest on one. A word resting on fewer combinations or loops than the prediction names is printed with them ("holds at
   L1; L2 not decidable"; "holds for t05; t06 left out") and the page may use only that part.
10. **P5 quotient.** For a lost loop and a column on a model, the pooled L2 ratio divided by the pooled L1 ratio, over all
    jobs of the model; in each of the 2000 resamples the same drawn jobs serve both sizes (job draws from stat id
    `forwardt|<loop>|<column>|joint`, stream `jobs`; each size redraws its repetitions under its own stat id of rule 2),
    as `dsweep/analyze.py`'s `joint_bootstrap` does. The point value is the quotient on the undrawn jobs; the interval is
    positions 50 and 1949.
11. **Summary for a target** ("x86-64", "Neoverse-N2"). The readable models are those of the target on which the
    prediction is tested (holds, fails or undecided). It **holds on all N readable models** when N >= 1 and it holds on
    every one; it **fails on at least one** when it fails on any (the models are named); it is **undecided** when no model
    fails and at least one is undecided; it is **not testable** when N = 0 and is never reported as holding. The loops
    left out of a prediction, and the models they are left out on, are named beside the word. P0 and P1 are evaluated
    first on every CPU model, P0 from compiler output alone. A CPU model is **marked control failed** when P1 fails on it,
    or when `t01` or `t03` does not have its predicted word on it (P1 leaves that loop out). On a marked model each of
    P2, P2n, P3, P4, P5 and P6 gets the word **not testable (control failed)** in place of the word rule 9 would give; the
    model is then outside N for those predictions, and the N = 0 clause above applies unchanged. P0 is not changed by
    this. A model on which P1 is undecided, or is not testable only because no combination it names is decidable, keeps
    the words of rule 9. The pooled ratios and intervals of a marked model are still printed in full (rule 12), with its
    P1 intervals beside them; as for any not-testable prediction they change no page sentence. A range, count or
    comparison on the page is taken over the unmarked models only and names the models left out.
12. **Reported, deciding nothing.** Every pooled ratio and interval in all four pairs, every `aa`, the between-job spread
    (100 times the sample standard deviation of ln r over jobs), for every loop and size, whether or not the cell is
    decidable, the placement statistic D of `v3.placement_sensitive` (the pooled ratio of rule 3 `placement`, with its
    interval at positions 50 and 1949) and the hot loops of `none` and `fast` as compiled from `harness/placement.py`
    (`start_mod64`, `bytes`, `windows64`, `extra_window`) with whether any of the four differs, as `harness/pool.py`'s
    `placement_differs` computes it (the same for both sizes, the binaries being the same); `v3` applies its placement
    rule to forward cells only, so here no cell is called placement-sensitive and none is excluded (rule 6); the layout
    A/A of criteria-v3 (`none` against `none_a64`) is not timed and takes no part in D. Also the words with (W, I) and
    trap counts, the instruction counts, the model and job counts, and the ratios of `t02` on Neoverse-N2.
13. **Hashes.** `forwardt.json` stores the SHA-256 of this plan, of `harness/criteria-v3.json` and of each file in
    `CODE_FILES` of `forwardt/analyze.py` (sweep and analysis code, the six sources, `kernels/common.hpp`, the harness
    modules the sweep imports), line endings read as LF, with `run.commit` (`GITHUB_SHA`) and the toolchain versions. The
    analysis reads no git history; it prints a note when the hashes of the files as they stand differ from the jobs', and
    for a smoke file it reads the stored plan hash only to print that note.

## Outcomes (fixed now)

A failed prediction is reported as failed, under that word, next to the measured ratio and interval. No result is
described as supporting a prediction it does not fall inside, and no band is changed to change a word. Under every
outcome the numbers of the main study are unchanged: this is a set of six new loops and not a new measurement of the
eight kernels.

Reading. The x86-64 summaries of rule 11 for P2 (rows) and P3 (columns) are made separately, each over the models on
which that prediction is read (rule 11), so the two sets of models can differ. A model marked control failed (rule 11)
is not counted as read for P2 or P3 and appears in no sentence below. "Wholly above X" means that both columns of a pair
have ci95_lo > X and "wholly below X" that both have ci95_hi < X, as "outside" in rules 8 and 9. No letter is chosen and
no sentence is written from a point ratio alone. Every ratio a sentence uses is given with its model, size and column and
is taken from a decidable cell (rule 4). "The lost sum and the lost writes differ" is written only for a model on which
both are read. Each row and column below is a rule 11 summary over models: "holds" means holds on every readable model,
"fails" means fails on at least one, the models being listed; a letter therefore says what was found on some models and
never what holds on all of them.

Row and column choice. A failure has a side per decidable pair: below when both columns have ci95_hi under the lower edge
of the band, above when both have ci95_lo over the upper edge (rule 8). The summaries are:

- P2 row (band 0.97 to 1.35): `holds` if rule 11 gives holds. Otherwise, if rule 11 gives fails, take every failed
  decidable pair of P2 on every model on which P2 is read: `fails above 1.35` if every one of them is above; `fails
  below 0.97` if every one of them is below; `fails on both sides` if at least one is above and at least one is below,
  on one model or on several. Otherwise `undecided or not testable`.
- P3 column (band above 1.5, so its only failure is below the lower edge): `holds`, `fails below 1.5`, `undecided` or
  `not testable`, as rule 11 gives.

The page names, for each model and pair, the ratio, the interval and the side on which each prediction failed. The
x86-64 table:

| P2 \ P3 | holds | fails below 1.5 | undecided | not testable |
|---|---|---|---|---|
| holds | A | B | C | C |
| fails above 1.35 | D | E | F | F |
| fails below 0.97 | G | G | G | G |
| fails on both sides | K | K | K | K |
| undecided or not testable | H | I | J | J |

Under every letter the page states a limit, or a word such as "cheap" or "costs little", only for a cell (loop, size,
column, CPU model) whose own pooled interval meets it, with that interval beside it: "at most 1.35x" where ci95_hi <=
1.35; "less than 1.5x" where ci95_hi < 1.5; "at or above 1.5x" where ci95_lo >= 1.5. A cell whose interval contains the
edge, or that is not decidable, is given with its numbers and no limit.

| letter | condition and what the page does |
|---|---|
| A | P2 holds and P3 holds: on every model where P2 is read, every decidable pair of `t02_sum_n` (L1 and L2) is inside 0.97 to 1.35; on every model where P3 is read, every decidable L1 pair of `t05_fill_n` and `t06_offset` is inside "above 1.5". The page gives each ratio with its model, size and column, and says that on each model where both are read the lost sum and the lost writes differ. It calls a sum cell "inside the forward range" only if that cell passes rule 6. |
| B | P2 holds as in A. P3 fails: at least one decidable L1 write pair is wholly below 1.5. The page gives every write ratio and interval, reports P3 as failed, names the pairs wholly below 1.5, and says for each write cell whether its interval lies below 1.5, contains 1.5 or lies at or above 1.5. It says a write loop costs less than 1.5x only for the cells whose interval lies below 1.5, says nothing of the kind for the write loops as a group, and does not carry any of this to the census loops, which are not these shapes. |
| C | P2 holds as in A; P3 undecided or not testable. The page gives each sum ratio with its model, size and column, and the forward-range statement of A for the sum cells that pass rule 6; it gives each write ratio with its interval and no word, and does not say that the lost sum and the lost writes differ. |
| D | P2 fails above 1.35 on the models and pairs named, none below 0.97, and P3 holds as in A. The page reports P2 as failed and prints the cells wholly above 1.35. It scopes its statements that forward loops cost little or stay vectorized to loops bounded by `size()`: a sentence that names its models, on the models on which the sum failed; a sentence that names none, everywhere. It reports the census count beside the cost, with its unit and method (228 lost loops, a per-function count at 38 source locations, in a class assigned by a text pattern, with no knowledge of how often any of them runs, and with the share that has one of the six shapes not counted), and gives the writes as at or above 1.5x only for the cells whose interval lies at or above 1.5. |
| E | P2 fails above 1.35 as in D and P3 fails as in B (the same model or different ones, each listed). The page gives the ratios and intervals of every cell, reports both as failed, names for each prediction the models and pairs on which it failed, and draws no rule from the shape of the loop. |
| F | P2 fails above 1.35 as in D; P3 undecided or not testable. The page reports P2 as failed, prints the cells wholly above 1.35 and makes the scoping statement of D; it gives each write ratio with its interval and no word. |
| G | P2 fails below 0.97 in the pairs named, none above: the sum is faster under FAST than under NONE by more than the band allows in those cells. The aligned column, the placement list and the `novec` pair are read first. The page reports the cells as measured and as a failed prediction, and gives the writes as measured under the word rule 11 gives for P3, with the cell reading of B for any interval below 1.5. |
| H | P2 undecided or not testable; P3 holds as in A. The page gives each write ratio with its model, size and column and says "at or above 1.5x" for each write cell whose interval lies at or above 1.5; it gives each sum ratio with its interval and no word, and does not say that the lost sum and the lost writes differ. |
| I | P2 undecided or not testable; P3 fails as in B. The page makes the write statements of B (every write ratio and interval, the pairs wholly below 1.5, the cell reading); it gives each sum ratio with its interval and no word. |
| J | Neither is decided. The page gives all ratios with intervals and no word. |
| K | P2 fails on both sides: at least one pair wholly above 1.35 and at least one wholly below 0.97, on different models, sizes or the same. The page gives each failing pair with its model, size, column, side, ratio and interval, says the prediction failed on both sides, and draws no sentence from either side about what a lost sum costs. The writes (P3) are reported as measured under the word rule 11 gives. |

Standing rule for forward-loop sentences, under every letter including J. Each sentence of the README, the main page and
the details page that gives a ratio or a range for forward loops (for example "about 1x" or "0.82 to 1.06x") says, in
the sentence or in the caption of the figure or table beside it, that the loops measured are bounded by the container's
own length, `size()` (the stencil's by `size()` less one). The results section of the details page lists the four
variable-bound loops (`t02_sum_n`, `t04_scale_n`, `t05_fill_n`, `t06_offset`) with, for each decidable aligned cell on
each model, the pooled ratio, its interval and whether the cell is inside the forward range (rule 6). A loop with no
decidable cell on a model is listed as having none. The listing is made whatever the ratios are, so no forward sentence
is left unqualified because an outcome row did not mention the bound.

Other readings:

- P0 fails for a loop on a model because its word there is not the predicted one: the timing is reported under the word
  the compiler gave, `forwardn/README.md` gets a line saying Compiler Explorer's build differs from the Ubuntu 18.1.3
  for that loop, and that loop is left out of every prediction that names it on that model (a prediction that names only
  that loop is not testable there). If only the trap clause fails, the word is the predicted one, the loop stays in
  every prediction that names it, and the trap count is reported beside its ratios.
- P1 fails on a model: P2, P2n, P3, P4, P5 and P6 are not testable there (rule 11). P2n fails above 1.35: the scalar sum
  without checks costs more than the stored `k01` figures suggest, and P2 is not read as a statement about the check
  alone; P2n failing below 0.90 is reported as measured. P4 fails above 1.30: the page does not call a narrower loop
  cheap. P5 fails on a model: the page quotes the L1 and the L2 ratio of that loop on that model separately. P6 fails
  above 1.15: a "kept" word on Neoverse-N2 does not predict a ratio near 1 for these writes either, as for matrix
  multiply; failing below 0.95 is reported as measured.
- A prediction that holds on a model licenses one page sentence on that model, at the sizes and columns it was decided
  on (rule 9) and with the ratio and interval beside it: P1, that the control stayed inside its band; P4, that the
  narrower loop cost at most 1.30x in the aligned column, said of no other narrower loop; P5, that the lost loop's ratio
  at L2 was within 0.80 to 1.25 times its ratio at L1; P6, that the two kept writes stayed inside 0.95 to 1.15 on
  Neoverse-N2, with the matrix-multiply 1.548x beside it.
- A prediction that is undecided or not testable is reported with its intervals and changes no page sentence.

## Runs

- **Accounting.** Every Actions run of the public repository that executes `forwardt/sweep.py` to time anything is an
  entry of `forwardt/runs.json` and of the report, in order of creation time. This covers code tests, smoke runs and
  measurement runs, runs dispatched by hand or started by an event, and every outcome, failed, cancelled and skipped runs
  included; the report names the temporary branch and the workflow file and gives the query that lists the same runs
  (`gh run list -R <repository> --branch <branch> --limit 200`). An entry gives: run id; runner; `head_sha`; creation
  time (`created_at` of the Actions API, UTC); class (`test` when the run's repetitions per side differ from the
  criteria number, so that its files are smoke files, `measurement` otherwise); the clause of this section that called
  for it (`code test`, `Neoverse-N2 run`, `x86-64 run 1`, `x86-64 run 2`, `restart after a code fix`, `restart after a
  platform failure`, `restart after the time limit`) or the words `not in the plan` with the reason; the number of jobs
  started; the number of jobs that returned a `forwardt.json`; the reason for each job that did not; and the folder of
  its downloaded files, or null for a run that is not stored (test runs are not stored). The planned dispatches are one
  code test on each of the two runners and three measurement runs (one Neoverse-N2, two x86-64); a code test repeated
  after a defect, a restart under the clauses below and any other run is an entry of its own. The report states the total
  number of entries and how many are marked `not in the plan`.
  `forwardt/analyze.py` takes its input from `forwardt/runs.json` and from nothing else. It prints every entry. It
  identifies the run of a file by the `run.id` stored in the file, not by the folder. It stops with an error and writes no
  result when: a folder named in the manifest is missing; a file in a named folder carries a run id that the manifest
  does not list; the number of `forwardt.json` files with a run id in its named folder differs from that entry's number
  of returned jobs; or a file's run id is not an Actions run id. The pool of rule 1 is the jobs of the entries of class
  `measurement`; a measurement run marked `not in the plan` is pooled like the others (last bullet of this section), and
  the report prints every prediction's result a second time without such runs.
- A code test comes first and is never pooled: `jobs = [1]` with `reps` set to a value other than the repetition count
  of `harness/criteria-v3.json` (4 is used), on each runner. A run whose repetitions per side differ from that count
  writes `smoke: true` in every file it writes, and the analysis sets such files aside (rule 1). A test run may be read
  to find a defect in the code and for nothing else. No prediction, band, rule, loop, size or word in this file is
  changed because of what a test run shows, and the report says whether any ratio of a test run was read. The code's unit
  tests use generated data only. A run without `reps` set, or with `reps` equal to that count, including one with
  `jobs = [1]`, is a measurement and is never used as a test.
- Neoverse-N2: `gh workflow run <workflow> -f runner=ubuntu-24.04-arm`, once, 6 jobs. x86-64: the same without the
  `runner` input, twice, 6 jobs each, from one commit, pooled per CPU model across the two runs; a model with fewer than
  3 jobs is listed as such and its predictions are not testable.
- A dispatchable workflow must already exist on the default branch of the public repository, so the real runs are
  dispatched from a temporary branch of it whose workflow file carries the `runner`, `jobs` and `reps` inputs and the
  `forwardt` steps, as the `dsweep` runs were. Both x86-64 runs are dispatched from one commit of that branch. Each file
  records its commit (`GITHUB_SHA`); the branch is named in the report and kept while the runs record its commits. The
  analysis compares recorded commits and code hashes (rule 7) and does not look a commit up in git. The report states
  the time limit of the dispatch workflow.
- A job that fails or is cancelled is listed and not replaced. A run in which no job returns a `forwardt.json` is not a
  measurement: if the cause is in the code, the fix is committed with this plan unchanged and every run of that runner
  that holds no `forwardt.json` is started again from the fix commit; if the cause is the platform (no job started, or
  every job cancelled by the platform and not by the workflow's own time limit), it is started again from the same
  commit; a run in which every job reaches the workflow's time limit is started again once, with the limit raised, and
  both runs are listed. When more than one of these causes applies to a run, the clause for a cause in the code governs.
  A run that holds a non-smoke `forwardt.json` is a measurement and is never restarted; non-smoke
  files of one model from different commits are then a file problem (rule 7). Partial files are kept and listed, and may
  be read to find a defect and for nothing else.
- Every job that returns a complete `forwardt.json` that is not a smoke file and has no file problem is pooled, whatever
  its ratios say. No run is started, repeated or added to change a word. If a model has too few jobs or a file problem,
  that is the result.

## What this cannot show

- Six loops, one source shape each, `int32` data, one compiler (clang 18.1.3 with libc++ 18, hardening mode FAST), `-O2`,
  baseline x86-64 (SSE2) and AArch64 (NEON). Nothing is said about other compilers, libraries or flags, or about how
  often such a loop is hot in a real program. Clang 19.1.0 and later vectorize these sources under FAST in the
  compile-only sweep; this plan times 18.1.3 only and says nothing about what a later compiler pays.
- The two targets have their own words (`forwardn`), their own runners (Neoverse-N2: one run of six jobs, so run-to-run
  spread is not in its intervals) and separate statements. The window-crossing account of code placement was not tested
  on AArch64 (`arm64/README.md`), so the aligned column there is a second build with `-falign-loops=64` and not a shown
  removal of placement effects.
- The six functions are hand-written in the shapes of `forwardn/README.md`, not taken from the census, and the plan does
  not count how many of the census's 228 loops have one of these shapes. `t05_fill_n` and `t06_offset` have no
  `size()`-bounded control, so what their cost owes to the bound alone is not separated. No loop with three arrays or two
  stores is timed. The bound is a run-time argument of a `noinline` function and equals `size()` at run time, so no check
  fires in any run; a loop inlined where its bound is known is not this shape.
- Runners are shared and the machine a job lands on is drawn by GitHub. The pinned vCPU shared a core with the driver in
  8 of the 10 jobs of the environment recording (`environment/`); no steal time or frequency is recorded per timing and
  no hardware counters are read, so the plan cannot say where the cycles go. The x86-64 statements rest on whichever CPU
  models return at least 3 jobs from two runs, listed beside each word. In the main study's 95-job pool the jobs per
  model range from 29 (EPYC 7763) to 1 (Xeon 8370C) (`results/s7-pooled/pooled.json`), so which models reach 3 jobs here
  is not controlled. A job that reaches the workflow's time limit is cancelled and not replaced.
- L1 and L2 only (no RAM); loops with different array counts get different `n`; `int32` data only; FAST only. The `novec`
  build is a reference and not a model of a lost loop without the check: in the main study, switching vectorization off
  accounts for 1.6x to 3.3x of the 2.8x to 8.0x (`README.md`).
- The list of runs is written by the author, and the analysis cannot see a run that is in neither `forwardt/runs.json`
  nor a stored folder. The independent record is the Actions run list of the public repository, and a run can be deleted
  from it by anyone with write access to the repository; an omitted run is found by a reader only while it is still
  listed there.
