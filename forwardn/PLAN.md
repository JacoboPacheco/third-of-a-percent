# Forward loops with a variable bound: plan, written before the sweep

Written Wed Oct 21, 2026, about 10:35 EDT (by `date`), before `forwardn/source.cpp` and `forwardn/run.py` existed
and before any of this folder's compile requests were sent. It is committed on its own, before that code.

## The question

The loop census (`corpus/README.md`) counts 444 lost loops in 25 projects, built with clang 18. By the header-text
heuristic 228 of them (38 distinct locations) are forward loops whose bound is a variable that is not the
container's `size()`: `for (i = 0; i < n; ++i) s += a[i];` with `n` a parameter or a member. None of the eight timed
kernels has that shape: every forward kernel is bounded by `a.size()`. The details page says that for such a loop the
check stays in the loop "and the vectorizer gives up". That sentence is a claim about every compiler. This folder
asks, compile-only: for which compiler versions and targets does libc++ FAST stop the vectorizer on a forward loop
with a variable bound?

## What was seen before this plan

During a review round a scratch probe compiled about a dozen small functions on Compiler Explorer with clang 18.1.0, 19.1.0,
20.1.0 and 21.1.0 (`-O2`, x86-64 baseline, `-stdlib=libc++`, NONE against FAST). It was not kept in the repository.
Its result, as far as the author recorded it, before this plan was written:

- a reduction `s += a[i]` with `n` a parameter (counter types `size_t`, `int`, `uint32_t`, `int64_t`, and
  `i < (int)a.size()`) is vectorized with checks off and not with them on, on clang 18.1.0 only, with the remark
  "could not determine number of loop iterations"; on clang 19.1.0, 20.1.0 and 21.1.0 it stays vectorized;
- a forward write `c[i] = a[i] * 2` bounded by `n` stays vectorized on all four, with interleave 1 against 2 on 18;
- `c[i + off] = a[i]` is not vectorized with checks on, on clang 18, with a cost-model remark;
- loops bounded by a struct member or through a pointer to a struct were not vectorized in either build.

So the part of this sweep that covers those functions on clang 18 to 21 at x86-64 `-O2` is a repeat, not a
prediction. What was **not** seen: clang 16.0.0, 17.0.1, 22.1.0, 23.1.0 and trunk; AArch64; `-O3`; and the shapes
below that were not in the probe (the two-source dot product, the in-place update, the fill, the member-bound write).

## What will be compiled

`forwardn/source.cpp`, one file of `noinline` functions, each with a `// LOOP` comment on the loop line:

- reductions over one `std::vector<int32_t>`: bound `a.size()` (control), bound `n` as `size_t`, `int`, `uint32_t` and
  `int64_t`, bound `(int)a.size()`, bound a member of a struct that also holds the vector, bound through a pointer to
  a struct, and a two-vector dot product with bound `n`;
- writes: `c[i] = a[i] * 2` bounded by `a.size()` (control), by `n` as `size_t` and as `int`, `c[i + off] = a[i]`,
  two stores per iteration, a member-bound write, an in-place `c[i] *= 2` and a fill `c[i] = i * 3`, all bounded by `n`;
- a range-for over `c` (a second control: no per-element check, so no change expected).

Compiler Explorer compilers (the ids in `ce-sweep/cesweep.py`): clang 16.0.0, 17.0.1, 18.1.0, 19.1.0, 20.1.0,
21.1.0, 22.1.0, 23.1.0 and trunk, each for x86-64 and for AArch64; flags as in `ce-sweep/` (`-stdlib=libc++`, the
hardening macro that fits the library version, the loop-vectorize remarks); x86-64 baseline at `-O2` and `-O3`,
AArch64 at `-O2`. That is 54 requests, one at a time with the spacing `ce-sweep/sweep.py` uses.

A cell is **lost** when the loop is vectorized in the unchecked build and not in the checked build, by the rule in
`ce-sweep/cesweep.py` (`vectorization`): the compiler's own remark at the loop's line. A cell is **narrower** when it
is vectorized in both builds but the width or the interleave count differs. Both builds scalar is **scalar in both**.

## Predictions (written now; not held with equal confidence)

1. The reductions with a variable bound and the `(int)a.size()` spelling follow the compiler version and not the
   counter type: lost on clang 16.0.0 and 17.0.1 as on 18.1.0, kept on 22.1.0, 23.1.0 and trunk as on 19 to 21.
   This is the weakest prediction: libc++ 16 and 17 check with a call to a function that does not return, libc++ 18
   with a trap, and that may change what the vectorizer sees.
2. AArch64 gives the same word as x86-64 for the same compiler version and function in at least 90% of the cells
   (the stop is a trip-count analysis, which does not depend on the target). `-O3` gives the same word as `-O2` for
   at least 90% of the x86-64 cells.
3. The forward writes bounded by `n` (`scale_n_*`, `inplace_n`, `fill_n`, `dot_n`) are never lost on a compiler for
   which the control `scale_size` is kept; some of them are narrower (lower interleave) on clang 18.
4. The member-bound and pointer-bound loops are scalar in both builds on every compiler.
5. The range-for control is vectorized in both builds on every compiler, with the same width and interleave.
6. The controls `sum_size` and `scale_size` are kept on every compiler.

## What the result decides

- If the variable-bound reductions are lost on clang 18 and earlier and kept on 19 and later: the sentence on the
  details page is scoped to those versions, the folder README carries the table, and a timing of this shape on
  clang 18 (a pair of kernels with a variable bound, same harness as the main study) and a census rebuild with clang 20
  become the next steps. They need their own plan; this plan does not time anything.
- If they are kept on every version: the sentence is wrong for them and is replaced by the narrower statement that the
  table supports.
- If a prediction above fails, it is reported as failed, next to the table.

## What this cannot show

It is compile-only. Nothing in it says how fast any loop runs, how often such a loop is hot, or what it costs when
it is lost: in the main study the lost forward reduction built with `-fno-vectorize` costs only 1.09x on one kernel
(`docs/dayone-results.md`), so a lost reduction may be cheap. Compiler Explorer's compilers are its own builds
(its `clang1810` is a release candidate of 18.1.0, not the Ubuntu 18.1.3 that was timed), with its own libc++.
Several of the functions are the ones in the probe described above, which the author had seen; for them the 18-to-21 part is a repeat.
The order of events (this file before the code, the code before the requests) rests on the author's clock and on
commit order in the author's development history.
