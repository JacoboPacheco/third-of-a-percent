# Variants: does the lost SIMD depend on the loop using two vectors?

Compile-only. No timing was done. Nothing here says anything about speed; it says what clang 18.1.0 did.

Reproduce: `python variants/run.py` (Python stdlib only; reads `cache/` when its request hash matches,
otherwise calls the Compiler Explorer public API; `--refresh` re-fetches). Sources: `source.cpp`.
It reuses `ce-sweep/cesweep.py` for the request body, the remark parser and the asm counters.
Setup: Compiler Explorer id `clang1810` (the only 18.x release it lists; the studies in
`investigate/vectorizer/` saved its version line, `clang version 18.1.0rc`: a release candidate, not the
Ubuntu 18.1.3 that was timed), x86-64 baseline (SSE2),
`-O2 -std=c++20 -stdlib=libc++`, `_LIBCPP_HARDENING_MODE` NONE vs FAST, loop-vectorize remarks on.
"Packed SSE" counts paddd, pmulld, pshufd, movdqu, punpck and similar in the whole function; the
three `same_scope` rows also include their initialisation loop, so for those the remark decides,
not the count. `ud2/abort` counts traps in the function: it shows whether any check is left in it.
Pipeline control: each `*_ctrl` row is the project's kernel verbatim and reproduces the main study
(reverse, stride-2, matmul LOST; packed counts 6 to 0, 10 to 0, 22 to 0 on this build line).

## Answer

| shape | (a) one vector, same one read and written | (b) iterator form | (c) two vectors, same size, same scope |
|---|---|---|---|
| reverse | kept, but the check is gone (0 traps in FAST): the bound is that vector's own size | kept; 0 traps (iterators are not checked in libc++ 18) | LOST |
| stride-2 | not testable: scalar in NONE too (dependence) | kept; 0 traps | LOST |
| matmul | in place (c=a=b=m): LOST. Regions of one vector: LOST | kept; the inner loop has no check, 1 trap sits outside it | LOST |

## What is SHOWN (remarks and assembly)

- The "two different vectors" explanation is not the cause. Making both vectors the same size by
  construction in one scope (c) does not restore vectorization for any of the three shapes: all LOST
  with the same remark as the control. The compiler sees `n` for both and still gives up on the
  loop count (reverse, stride-2: "could not determine number of loop iterations"; matmul: "cost-model
  indicates that vectorization is not beneficial").
- Matmul stays LOST with a single vector, both for three disjoint regions of one vector and for a
  truly in-place update, so a second vector is not needed for the loss there.
- Reverse in place (a) stays vectorized, but the FAST build contains no check at all (0 traps,
  identical instruction count 34 vs 34): `a[i]` with `i < a.size()` of the same vector is proved in
  range and the check is removed. That is the check disappearing, not SIMD surviving a check.
- The iterator forms (b) are vectorized in both builds, also because there is no per-element check:
  the FAST reverse and stride-2 iterator functions have 0 traps. Matmul iterator forms have one trap,
  outside the inner loop (the scalar `a[i*d+k]`). So (b) shows that the loss comes with the
  `operator[]` check on an index that is not tied to the loop bound, not with the loop shape alone.
- Net reading for reverse and stride-2: the loss needs a check inside the loop whose bound the compiler
  cannot connect to the trip count (the remark is "could not determine number of loop iterations").
  Two vectors is one way to get that; same-size vectors in one scope do not help.
- Matmul on clang 18 is a different case. The vectorizer's plan already has the trip count with both
  size checks folded in as a clamp, and the loop is rejected on cost (the cost-model remark above; each
  of the two compares is priced at 14 units), as the later compile-only study finds
  ([investigate/vectorizer/matmul](../investigate/vectorizer/matmul/README.md), finding F2 and short
  answer 2). A single vector with an index that is not the loop variable of its own size loses it as well
  (`matmul_inplace`, `matmul_onevec_regions`).

## What is NOT shown

- Any timing. No run time, no ratio, no cache effect.
- Stride-2 in place: both single-vector variants (`inplace`, `onevec_halves`) are refused in NONE
  too ("unsafe dependent memory operations", the compiler cannot prove the halves disjoint), so
  they do not test the hypothesis. A single-vector stride-2 loop that vectorizes unchecked was not found.
- Only clang 18.1.0, x86-64 baseline, -O2, libc++ FAST, int32 elements. Not newer compilers, not
  -O3, not AVX2, not GCC. The same-scope functions allocate their vectors, which adds an allocation
  path; the remark at the loop line is what is compared.
- Whether (a) or (b) forms are "the same loop" for a user: they drop the check, so they are a
  workaround, not the same program.

## Generated table

Compile-only. Compiler Explorer `clang1810` (clang 18.1.0, x86-64 baseline SSE2), `-O2 -std=c++20 -march=x86-64 -stdlib=libc++`.
NONE = `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE`, FAST = `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST`.

### reverse

| variant | build | loop-vectorize remark | packed SSE | ud2/abort | NONE to FAST |
|---|---|---|---|---|---|
| `rev_ctrl` | NONE | vectorized (width 4, interleave 2) | 6 | 0 |  |
| `rev_ctrl` | FAST | NOT vectorized: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]; loop not vectorized [-Rpass-missed=loop-vectorize] | 0 | 1 | LOST |
| `rev_inplace` | NONE | vectorized (width 4, interleave 2) | 6 | 0 |  |
| `rev_inplace` | FAST | vectorized (width 4, interleave 2) | 6 | 0 | kept |
| `rev_iter` | NONE | vectorized (width 4, interleave 2) | 6 | 0 |  |
| `rev_iter` | FAST | vectorized (width 4, interleave 2) | 6 | 0 | kept |
| `rev_iter_two` | NONE | vectorized (width 4, interleave 2) | 6 | 0 |  |
| `rev_iter_two` | FAST | vectorized (width 4, interleave 2) | 6 | 0 | kept |
| `rev_same_scope` | NONE | vectorized (width 4, interleave 2) | 16 | 0 |  |
| `rev_same_scope` | FAST | NOT vectorized: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]; loop not vectorized [-Rpass-missed=loop-vectorize] | 10 | 1 | LOST |

### stride-2

| variant | build | loop-vectorize remark | packed SSE | ud2/abort | NONE to FAST |
|---|---|---|---|---|---|
| `stride2_ctrl` | NONE | vectorized (width 4, interleave 2) | 10 | 0 |  |
| `stride2_ctrl` | FAST | NOT vectorized: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]; loop not vectorized [-Rpass-missed=loop-vectorize] | 0 | 1 | LOST |
| `stride2_inplace` | NONE | NOT vectorized: loop not vectorized: unsafe dependent memory operations in loop. Use #pragma clang loop distribute(enable) to ; loop not vectorized [-Rpass-missed=loop-vectorize] | 0 | 0 |  |
| `stride2_inplace` | FAST | NOT vectorized: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]; loop not vectorized [-Rpass-missed=loop-vectorize] | 0 | 1 | scalar in both |
| `stride2_iter` | NONE | vectorized (width 4, interleave 2) | 10 | 0 |  |
| `stride2_iter` | FAST | vectorized (width 4, interleave 2) | 10 | 0 | kept |
| `stride2_onevec_halves` | NONE | NOT vectorized: loop not vectorized: unsafe dependent memory operations in loop. Use #pragma clang loop distribute(enable) to ; loop not vectorized [-Rpass-missed=loop-vectorize] | 0 | 0 |  |
| `stride2_onevec_halves` | FAST | NOT vectorized: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]; loop not vectorized [-Rpass-missed=loop-vectorize] | 0 | 1 | scalar in both |
| `stride2_same_scope` | NONE | vectorized (width 4, interleave 2) | 22 | 0 |  |
| `stride2_same_scope` | FAST | NOT vectorized: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]; loop not vectorized [-Rpass-missed=loop-vectorize] | 12 | 1 | LOST |

### matrix multiply (inner loop)

| variant | build | loop-vectorize remark | packed SSE | ud2/abort | NONE to FAST |
|---|---|---|---|---|---|
| `matmul_ctrl` | NONE | vectorized (width 4, interleave 2) | 22 | 0 |  |
| `matmul_ctrl` | FAST | NOT vectorized: the cost-model indicates that vectorization is not beneficial [-Rpass-missed=loop-vectorize]; the cost-model indicates that interleaving is not beneficial [-Rpass-missed=loop-vectorize] | 0 | 1 | LOST |
| `matmul_inplace` | NONE | vectorized (width 4, interleave 2) | 22 | 0 |  |
| `matmul_inplace` | FAST | NOT vectorized: the cost-model indicates that vectorization is not beneficial [-Rpass-missed=loop-vectorize]; the cost-model indicates that interleaving is not beneficial [-Rpass-missed=loop-vectorize] | 0 | 1 | LOST |
| `matmul_iter` | NONE | vectorized (width 4, interleave 2) | 22 | 0 |  |
| `matmul_iter` | FAST | vectorized (width 4, interleave 2) | 22 | 1 | kept |
| `matmul_iter_range` | NONE | vectorized (width 4, interleave 2) | 22 | 0 |  |
| `matmul_iter_range` | FAST | vectorized (width 4, interleave 2) | 22 | 1 | kept |
| `matmul_onevec_regions` | NONE | vectorized (width 4, interleave 2) | 22 | 0 |  |
| `matmul_onevec_regions` | FAST | NOT vectorized: the cost-model indicates that vectorization is not beneficial [-Rpass-missed=loop-vectorize]; the cost-model indicates that interleaving is not beneficial [-Rpass-missed=loop-vectorize] | 0 | 1 | LOST |
| `matmul_same_scope` | NONE | vectorized (width 4, interleave 2) | 39 | 0 |  |
| `matmul_same_scope` | FAST | NOT vectorized: the cost-model indicates that vectorization is not beneficial [-Rpass-missed=loop-vectorize]; the cost-model indicates that interleaving is not beneficial [-Rpass-missed=loop-vectorize] | 13 | 1 | LOST |
