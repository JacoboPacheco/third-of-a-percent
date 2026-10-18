# Keeping hardening on without paying: rewrites of the loops that pay

The main study found that under libc++ FAST hardening the reverse, stride-2 and matrix-multiply loops
run 2.8 to 8 times slower in cache, because the per-element bounds check stops the vectorizer, and
the gather loop runs up to 1.8 times slower. The question a tech lead asks next: **can I keep hardening
on and not pay?** This folder answers it with measurements. For each of the four loops it builds the original and
rewrites that do the same work and still stop the program on an out-of-range access. Every
rewrite gets checked for vectorization, check traps, the original's checksum and a safety test, and gets timed.

## The answer in four lines

- **Reverse: yes.** One up-front size check (`REQUIRE(c.size() >= a.size())`), or a `std::span` taken
  with `first(n)`, lets clang 18 drop the per-element check and vectorize again: **1.00x** of the
  unchecked original on EPYC 7763 and 9V74, and **1.06x to 1.09x** on EPYC 9V45 (see Surprises; the hot loop there is byte-identical to the unchecked original's, the NONE build).
- **Stride-2: yes, but not with a precondition.** `REQUIRE(a.size()/2 >= n)` changes nothing (5x). A span taken with
  `first(2*n)` vectorizes, but with interleave 1. Adding `#pragma clang loop interleave_count(2)`
  brings it to **0.96x to 1.03x**. Raw `data()` pointers behind one check: **0.95x to 1.03x**.
- **Matrix multiply: only with raw row pointers behind one check (1.00x everywhere).** The rewrites that keep
  every access under hardening (row spans) stay at **1.08x to 1.37x at L1** and **0.98x to 1.12x at L2**.
- **Gather: no.** The data-dependent check `a[idx[i]]` cannot be hoisted. Moving only `c[i]`'s check up front cuts
  1.58x to 1.84x down to **1.27x to 1.36x at L1** (1.01x to 1.14x at L2). Every rewrite that removes the last check
  either is slower (a clamp, a validation pass) or is UNSAFE (raw pointers).

**Under the rules committed before the first timed run (`criteria.json`; the order is in the author's unpublished development history), no rewrite is called "better".** That
word needs the aligned interval to sit within A/A noise of 1.0 on every CPU model drawn. Only EPYC 7763 had
jobs usable under the whole-job A/A rule (2 of 12 jobs). On EPYC 9V45 the reverse rewrites sit at 1.06x to 1.09x with
intervals clearly above 1. The numbers below are measurements, not that claim.

## What was run

- **3 timed runs** of `.github/workflows/mitigate.yml`, 4 jobs each (12 job files), plus one build-only
  probe (run 38256579505): runs 38256846461,
  38258944443 and
  38260958390.
  CPU models drawn: **AMD EPYC 7763** (7 jobs), **EPYC 9V45** (3), **EPYC 9V74** (2). No Intel model came up in 12 draws.
- **Toolchain** as in the main study: Ubuntu clang 18.1.3, libc++-18-dev 1:18.1.3 (noble apt), `-O2 -std=c++20
  -stdlib=libc++`, baseline x86-64 (SSE2). Each variant is built NONE, FAST, and both again with `-falign-loops=64`.
- **Sizes** by the harness rule: L1 = half of L1d, L2 = half of L2, counting every array.
- **Timing** by the project's method: 20 processes per side in ABBA order, pinned with `taskset -c 1`,
  ratio of medians, 95% percentile bootstrap (10,000 resamples, seed 20261011; `stats.py` is a copy of
  `harness/stats.py`). Every job also times an **A/A pair** (the original NONE binary against a byte-identical
  copy) for every kernel at every size. Iterations are calibrated on the original's NONE build only.
- **Per variant and size, 4 pairs:** variant FAST against the original NONE, and against the variant's own NONE,
  each as compiled and aligned. **The headline is aligned FAST against the original's aligned NONE.**
- **Safety test:** each variant's NONE and FAST builds run once on an input one element too short
  (reverse: `c` short; stride-2: `a` short; gather: `a` short, so one index points past it; matmul: `b` short).
  *trapped* means SIGILL (`ud2`) before the kernel returned. *returned* means the out-of-range access went
  through unchecked. The original's NONE build returned for all four kernels, which shows the input really is out of range.
- **Checksums:** every timed process of every variant printed the original NONE's checksum (the run stops otherwise).

## Results

Aligned FAST time divided by the **original's** aligned NONE time. Each cell is the range of medians across that CPU
model's jobs, L1 / L2. A cell is left out when that kernel and size had an A/A half-width above 2% in that job, and
"-" means no cell was left (with every cell kept, the stride-2 original on EPYC 9V45 at L1 is 2.86x to 2.89x). "recovers" is `criteria.json` applied per CPU model (n/u = no job usable under its
whole-job rule). "within noise" counts the cells whose upper interval end is at most 1 + that cell's A/A half-width.
`span_il2` and `clamp` were added after the first timed run, so they have fewer cells.

| loop shape | rewrite | keeps safety | EPYC 7763 L1 / L2 | EPYC 9V45 L1 / L2 | EPYC 9V74 L1 / L2 | recovers, per CPU (criteria) | cells within noise | readability cost |
|---|---|---|---|---|---|---|---|---|
| reverse | orig | yes | 8.00-8.02 / 7.55-7.86 | 5.59 / 5.82-5.86 | 5.38 / 5.88 | 7763: no; 9V45: n/u; 9V74: n/u | 0/19 | none (the original) |
| reverse | pre | yes | 1.00 / 0.99-1.00 | 1.06 / 1.09 | 1.00 / 1.00 | 7763: no; 9V45: n/u; 9V74: n/u | 11/19 | one line added |
| reverse | span | yes | 1.00 / 0.99-1.00 | 1.06 / 1.08 | 1.00 / 1.00 | 7763: yes; 9V45: n/u; 9V74: n/u | 11/19 | two lines added, indexes a span |
| reverse | raw | yes (one check) | 1.00 / 1.00-1.02 | 1.06 / 1.08 | 1.00 / 1.00 | 7763: no; 9V45: n/u; 9V74: n/u | 10/19 | raw pointers: safety rests on one line |
| reverse | fwd | yes | 1.00 / 0.99-1.02 | 1.06-1.07 / 1.01-1.07 | 1.00 / 1.00 | 7763: no; 9V45: n/u; 9V74: n/u | 10/19 | loop header changed, element order not kept |
| reverse | rtransform | **NO** | 1.05 / 0.99-1.00 | 0.98-0.99 / 1.00-1.01 | 1.00 / 1.00 | 7763: no; 9V45: n/u; 9V74: n/u | 5/19 | one-line algorithm |
| reverse | pragma | yes | 8.00-8.02 / 7.70-7.84 | 5.56-5.58 / 5.77-5.79 | 5.38 / 5.75 | 7763: no; 9V45: n/u; 9V74: n/u | 0/19 | one pragma line |
| stride-2 | orig | yes | 5.06-5.16 / 4.97-5.11 | - / 3.01-3.05 | 5.08-5.09 / 5.15 | 7763: no; 9V45: n/u; 9V74: n/u | 0/16 | none (the original) |
| stride-2 | pre | yes | 5.07-5.16 / 4.81-5.11 | - / 2.94-2.97 | 5.09 / 5.13 | 7763: no; 9V45: n/u; 9V74: n/u | 0/16 | one line added |
| stride-2 | span | yes | 1.31 / 1.20-1.28 | - / 0.59 | 0.97 / 0.99 | 7763: no; 9V45: n/u; 9V74: n/u | 5/16 | three lines added, indexes a span |
| stride-2 | span_il2 | yes | 1.00 / 0.96-1.03 | - / 1.00-1.01 | 0.98 / - | 7763: no; 9V45: n/u; 9V74: n/u | 2/11 | span lines plus one pragma |
| stride-2 | raw | yes (one check) | 1.00 / 0.95-1.03 | - / 0.99-1.00 | 1.00 / 1.00 | 7763: no; 9V45: n/u; 9V74: n/u | 7/16 | raw pointers: safety rests on one line |
| stride-2 | pairs | yes | 6.35-6.38 / 5.93-6.27 | - / 4.02-4.03 | 5.10-5.11 / 5.50 | 7763: no; 9V45: n/u; 9V74: n/u | 0/16 | second induction variable |
| gather | orig | yes | 1.84 / 1.17-1.19 | 1.71-1.73 / 1.30 | 1.58 / 1.01 | 7763: no; 9V45: n/u; 9V74: n/u | 0/23 | none (the original) |
| gather | pre | yes | 1.32-1.33 / 1.01-1.02 | 1.29 / 1.13-1.14 | 1.35-1.36 / 1.01 | 7763: no; 9V45: n/u; 9V74: n/u | 0/23 | one line added |
| gather | span | yes | 1.32 / 1.01 | 1.27-1.29 / 1.13 | 1.36 / 1.01 | 7763: no; 9V45: n/u; 9V74: n/u | 0/23 | three lines added |
| gather | clamp | yes (clamp + one check) | 1.84 / 1.19 | 2.37-2.38 / 1.61-1.63 | 1.94 / 1.15 | 7763: no; 9V45: n/u; 9V74: n/u | 0/15 | a three-line loop body and raw pointers |
| gather | validate | yes (one check) | 1.50-1.51 / 1.38-1.40 | 2.15-2.17 / 1.84 | 1.61 / 1.33 | 7763: no; 9V45: n/u; 9V74: n/u | 0/23 | a second loop and raw pointers |
| gather | raw | **NO** | 1.00 / 1.00 | 0.99-1.00 / 1.00-1.01 | 1.01 / 1.00 | 7763: no; 9V45: n/u; 9V74: n/u | 4/23 | raw pointers |
| matrix multiply | orig | yes | 3.18-3.19 / 3.79-3.80 | 3.88-3.94 / 4.08-4.11 | 4.03-4.05 / 4.63 | 7763: no; 9V45: n/u; 9V74: n/u | 0/24 | none (the original) |
| matrix multiply | pre | yes | 3.17-3.21 / 3.76 | 4.00-4.10 / 4.04-4.10 | 4.00-4.01 / 4.56-4.57 | 7763: no; 9V45: n/u; 9V74: n/u | 0/24 | one line added |
| matrix multiply | span | yes | 1.37 / 1.12 | 1.14-1.15 / 0.98-1.00 | 1.33 / 1.08 | 7763: no; 9V45: n/u; 9V74: n/u | 2/24 | three lines added, rows as spans |
| matrix multiply | span_il2 | yes | 1.25 / 1.05 | 1.23-1.24 / 1.06-1.07 | 1.23 / 1.03 | 7763: no; 9V45: n/u; 9V74: n/u | 0/16 | row spans plus one pragma |
| matrix multiply | rowptr | yes (one check) | 1.00 / 1.00 | 0.99-1.00 / 0.99-1.00 | 1.00 / 1.00 | 7763: yes; 9V45: n/u; 9V74: n/u | 17/24 | raw pointers: safety rests on one line |
| matrix multiply | transform | yes | 1.13 / 0.99 | 1.09 / 1.00-1.01 | 1.14 / 1.02 | 7763: no; 9V45: n/u; 9V74: n/u | 7/24 | row spans plus an algorithm call with a lambda |

"yes (one check)" means the test trapped, but the rewrite stays safe only through its single up-front
`REQUIRE` (a `__builtin_trap()` on a size test, present in NONE builds too). Raw pointers are not checked after that.
"yes" alone means libc++ hardening itself (for example `span::first`, `span::subspan`, `vector::operator[]`) still
guards every access, with or without an extra `REQUIRE`.

### What the compiler did (identical in every job; `results/mitigate-run-*/*/results.json`)

| loop | variant | vectorized NONE / FAST (clang remark) | short input NONE / FAST |
|---|---|---|---|
| reverse | orig | width 4, interleave 2 / not vectorized: "could not determine number of loop iterations" | returned / trapped |
| reverse | pre, span, raw, fwd | 4x2 / 4x2 | pre, raw: trapped / trapped; span, fwd: returned / trapped |
| reverse | rtransform | 4x2 / 4x2 (no `ud2` in the kernel) | returned / **returned** |
| reverse | pragma | 4x2 / not vectorized "(Force=true)" | returned / trapped |
| stride-2 | orig, pre, pairs | 4x2 / not vectorized: "could not determine number of loop iterations" | orig: returned / trapped; pre, pairs: trapped / trapped |
| stride-2 | span | 4x2 / 4x**1** ("interleaving is not beneficial") | returned / trapped |
| stride-2 | span_il2, raw | 4x2 / 4x2 | span_il2: returned / trapped; raw: trapped / trapped |
| gather | all | not vectorized in either build (SSE2 has no gather); `validate` vectorizes only its max pass | raw: returned / **returned**; pre, span: returned / trapped; clamp, validate: trapped / trapped |
| matmul | orig, pre | 4x2 / not vectorized: "the cost-model indicates that vectorization is not beneficial" | orig: returned / trapped; pre: trapped / trapped |
| matmul | span | 4x2 / 4x**1** | returned / trapped |
| matmul | span_il2, rowptr, transform | 4x2 / 4x2 | rowptr: trapped / trapped; others: returned / trapped |

For the best rewrite of each shape, the assembly against the original is in `asm/` of every job folder:
`<kernel>.orig-vs-<variant>.fast_a64.diff`, and the variant's own NONE-to-FAST diff
`<kernel>.<variant>.none_a64-vs-fast_a64.diff`. For `m04_rev.span` the FAST hot loop is the same
8-element SIMD loop as the original NONE's. Hardening's check became one `cmp`/`jb` to a single `ud2` before the loop.

## What to do, per loop shape

Ranked by: keeps safety, then recovers speed, then small code change.

- **Reverse loop.** (1) Add one precondition before the loop, `REQUIRE(c.size() >= a.size())` (here
  `if (!(cond)) __builtin_trap();`). It is one line, hardening stays on, and the per-element check disappears.
  (2) Or take `std::span(c).first(n)` once and index the span. Hardening checks `first()`, so there is no hand-written check.
  (3) Or count up instead, when the element order does not matter. Do **not** use `#pragma clang loop vectorize(enable)` (it changes nothing)
  or `std::transform` over `rbegin()/rend()`: it is fast but **unsafe**, because libc++ 18 vector iterators are not checked in FAST mode.
- **Stride-2 loop.** (1) Take `std::span(a).first(2*n)` once and add `#pragma clang loop interleave_count(2)`:
  hardening-backed, 0.96x to 1.03x. Without the pragma the span version is 1.2x to 1.3x on EPYC 7763 (and 0.59x on 9V45).
  (2) Or raw `data()` pointers behind one `REQUIRE(a.size() / 2 >= n)`. A precondition with `operator[]` does **not**
  work here: clang 18 does not derive `2*i+1 < a.size()` from it.
- **Gather loop.** Hoist what can be hoisted: `REQUIRE(c.size() >= idx.size())` (or spans for `c` and `idx`) removes
  `c[i]`'s check and cuts the cost from 1.6x to 1.8x down to 1.3x at L1, about 1.0x to 1.1x at L2. Leave
  `a[idx[i]]` checked. Nothing tried removes that last check both safely and cheaply: a branch-free clamp is slower
  than the check (up to 2.4x), and a validation pass costs a second read (up to 2.2x).
- **Matrix multiply.** (1) Raw row pointers behind one `REQUIRE` that all three matrices hold `d*d` elements
  (overflow-checked): 0.99x to 1.00x on every CPU drawn. Safety rests on that one line. (2) If every access must stay under
  hardening: row spans (`subspan(i*d, d)`) with `std::transform` over the row, 1.08x to 1.14x at L1 and 0.98x to
  1.02x at L2. A precondition with `operator[]` does **not** work (clang cannot prove `i*d+j < size`).

## Surprises

- **A precondition helps only when the index is the loop counter itself.** For reverse it works. For stride-2
  (`2*i+1`) and matmul (`i*d+j`) clang 18 keeps every check. On Compiler Explorer (clang 18.1.0) the stride-2 check stayed even with
  `a.size() == 2*n`, `2*n <= a.size()` plus an overflow guard, or `__builtin_assume`. That was checked there only,
  not built on the runner.
- **"Paired" indexing made stride-2 worse:** with a second induction variable `j += 2` it ran 6.4x on EPYC 7763,
  against 5.1x for the original FAST.
- **Interleave choice dominates per CPU.** The stride-2 span rewrite at interleave 1 is 1.31x on EPYC 7763 but
  **0.59x on EPYC 9V45**, faster than the unchecked original.
- **EPYC 9V45 charges the reverse rewrites 6% to 9%**, in NONE and FAST alike for `pre` and `raw` (their own
  FAST/NONE is 1.00). Their aligned hot loop is byte-identical to the original NONE's and at the same address.
  Only the code before the loop differs (one compare, different padding). The cause was not found. With no
  hardware counters on these VMs, it stays unexplained.
- **`std::transform` over reverse iterators** vectorizes in both builds and has no `ud2` at all. It is silently unsafe under FAST.

## Reading against the rules, and the objection

`criteria.json` was committed before the first timed run (commit e0dabd8, in the author's unpublished development history). Run 38256846461 already existed when three
variants (`span_il2` for stride-2 and matmul, `clamp` for gather) were added. They are judged by the same rules,
and that file records the addition. The rules as written:

- A job is usable only if **all 8** of its A/A half-widths (4 kernels x 2 sizes) are at most 2%. That held in
  **2 of 12 jobs**, both on EPYC 7763 (run 38260958390, jobs 2 and 4). The stride-2 L1 A/A was above 2% in 5 of 12
  jobs, up to 6.87%. So 9V45 and 9V74 have no usable job, and no rewrite can meet the headline claim, which needs every CPU model drawn.
- *Objection, written after the results:* the whole-job rule throws away a job for one noisy pair. The
  "cells within noise" column applies the same 2% limit cell by cell instead. Even then the upper-interval rule
  fails many cells whose median is 1.00, because a pair of two different binaries often has a wider interval than
  the A/A pair (for example `rowptr` on EPYC 9V45 at L2: 1.00 [0.97, 1.02] against an A/A half-width of 0.47%, or 0.999 [0.997, 1.002] against 0.21% on EPYC 7763). Under either reading, the 9V45 reverse
  cells (1.06 [1.05, 1.07]) fail on a real difference, not on width.

## What this does NOT show

- **One toolchain:** clang 18.1.3 and libc++ 18.1.3 from Ubuntu noble, `-O2`, FAST mode only. A newer clang may prove
  the stride-2 or matmul bounds by itself. GCC and the libc++ extensive mode were not tried.
- **SSE2 baseline only.** With AVX2 (`-march=x86-64-v3`) the gather has a vector instruction and the costs may differ.
- **4 synthetic kernels on `int32_t`**, at the L1 and L2 sizes only (no RAM size). One loop each, not a program.
- **3 CPU models, all AMD** (EPYC 7763, 9V45, 9V74). No Intel model was drawn in 12 jobs, and only EPYC 7763 had jobs usable under the rules.
- **The safety test is one input per kernel**, one element short. It shows the check fires on that input; it does
  not prove a rewrite safe for every input. The "one check" rewrites are exactly as safe as that one line is correct.
- **Compiler Explorer (clang 18.1.0)** was used to explore rewrites before building. Only what was built on the
  runner (clang 18.1.3) is in the tables.

## Files and how to reproduce

- `src/m04_rev.cpp`, `src/m05_stride2.cpp`, `src/m06_gather.cpp`, `src/m08_matmul.cpp`: every variant, picked with `-DV_<name>`.
  `src/common.hpp` is `kernels/common.hpp` plus `REQUIRE` and the safety mode.
- `run.py`: builds, safety test, timing; one `results.json` per job with raw samples, remarks, traps, loops and diffs.
- `criteria.json`: the reading rules. `summarize.py`: the tables (`--headline` for the one above, `--check` to recompute every ratio and interval from the raw samples).
- `stats.py`, `asm.py`, `placement.py`, `remarks.py`: copies of the harness modules.
- Results: `results/mitigate-run-38256846461/`, `results/mitigate-run-38258944443/`, `results/mitigate-run-38260958390/`.

```
gh workflow run mitigate.yml                                   # 4 jobs, about 15 minutes each
python mitigate/summarize.py --check results/mitigate-run-*    # on a laptop: every interval recomputed
python mitigate/summarize.py --headline results/mitigate-run-*
python mitigate/summarize.py results/mitigate-run-*            # per-job intervals, own-NONE ratios, as-compiled ratios
```
