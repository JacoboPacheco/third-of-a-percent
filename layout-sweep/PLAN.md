# Layout sweep: is the forward-loop claim robust to code placement, or only to two layouts?

Written Tue Oct 13 2026 (time in the commit message), BEFORE any run. Numbers live in `criteria.json` (its sha256 is stored in every result); this file says why and how.

## Question
`investigate/FINDINGS.md`: k02_add_fwd FAST/NONE was 1.6x on EPYC 7763 and 9V74 as compiled and 0.82 to 0.86 with `-falign-loops=64`, because one 31-byte SIMD loop crossed a 64-byte boundary. That is two layouts. Gap 5 in `gaps/GAPS.md`: sample many layouts and report the ratio as a distribution over placements, instead of excluding "placement-sensitive" cells by a post-hoc rule.

## What is built
- Kernels `k01_sum_fwd`, `k02_add_fwd`, `k03_stencil` (forward loops, expected to stay vectorized: the claim) and `k04_rev` (expected to lose SIMD under FAST: the control). Sizes L1 and L2 (in-cache; sized as in `harness/run.py`).
- Each kernel in NONE and FAST at 16 placements `p00..p15`, plus two reference placements: `ref` (the harness's own build command) and `a64` (the harness's `-falign-loops=64` pair). The same placement is used on both sides of a ratio.
- Mechanism: `layout-sweep/wrap.cpp` puts `.skip 4*NN, 0x90` at the start of the object's `.text`, then `#include`s the unchanged kernel source. The build adds `-falign-functions=1 -falign-loops=1` (the first of `design.loop_alignment_variants_in_order` that passes the probe below) so the compiler's own 16-byte function and loop alignment does not swallow the padding. Moving the filler by 4 bytes then moves the function, and so the hot loop, by 4 bytes. 16 steps of 4 bytes cover all 16 loop-start residues mod 64 that are multiples of 4 (offset by the loop's fixed position in its function).
- Verification from the disassembly, not from the flags: every build's `kern_<id>` address and hot-loop start (innermost loop, the SIMD one with most bytes, as `harness/pool.py hot_loop`), start mod 64, bytes, windows touched and crossing are stored. Before any timing the runner builds k02 FAST at p00, p01 and p03 for each loop-alignment variant in order and takes the first for which function address and loop start both move by exactly 4*NN bytes; if none does, the run aborts (nothing timed). After building everything it requires, for every kernel and mode, that the function address minus p00's equals 4*NN for all 16 pads and the loop's offset inside the function is constant. Selection uses addresses only, never a timing.
- The sweep's base layout (function and loop alignment 1) is not the compiler's default. `ref` and `a64` are in the run so the sweep can be read against the earlier two-layout result.

## Timing
Per job (one GitHub runner; ubuntu-24.04, clang-18, libc++-18-dev): per cell (kernel x size) the iteration count is calibrated once on the NONE p00 binary to about 75 ms per process and reused for every placement; every placement (16 + 2) is timed NONE against FAST, 20 processes per side, ABBA, `taskset` pinned; a byte-identical A/A (NONE p00 against a copy of itself) is timed per cell. The order of placements within a cell is a shuffle seeded by job and cell (recorded). Checksums of NONE and FAST must match on every pair. 8 jobs per run by default (4 to 10 allowed).

## Statistics
Per job: ratio = median(FAST)/median(NONE), percentile bootstrap (`harness/stats.py`, 2000 resamples). Pooled per CPU model, per cell and placement, with `harness/pool.py pair_stat` unchanged: geometric mean over jobs of the per-job ratios, two-level bootstrap interval (jobs, then repetitions), the same generator on any machine. The CPU model is the unit; no job is dropped on its own numbers.

## Rules (fixed now; numbers in criteria.json)
Let `aa` be the pooled half-width (percent) of that cell's byte-identical A/A. A cell is INCONCLUSIVE if aa is above 2 %, if fewer than 3 jobs of the CPU model exist, if any checksum differs, if a build's sha256 differs between jobs, or if the mechanism check fails (the 16 hot-loop starts of a build do not cover 16 distinct residues mod 64 in 4-byte steps).
- Class of a kernel comes from clang's loop-vectorize remark at the marked line at p00: kept = vectorized in NONE and FAST, lost = vectorized in NONE only, otherwise off-axis (reported, not judged). A kernel whose class differs from the expectation above is reported as such.
- A placement of a kept cell PASSES when the pooled ratio is at most 1.02 and ci95_hi is at most 1 + max(0.02, 2 x aa/100) (the v3 forward rule, same numbers). It COSTS when ci95_lo is above 1 + max(0.02, 2 x aa/100).
- A placement of a lost cell HOLDS when ci95_lo is at least 1.5.
- Kept cell over its 16 placements: ROBUST if at least 15 pass; PLACEMENT_DEPENDENT if at most 7 pass; MIXED otherwise.
- Lost cell: HOLDS if at least 15 of 16 placements hold; else NOT_STABLE.
- Per CPU model, forward claim: ROBUST when every kept in-cache cell is ROBUST; PLACEMENT_DEPENDENT when any is; MIXED otherwise; INCONCLUSIVE when any kept cell is, or when no kernel is kept. Control: HOLDS when every lost cell HOLDS.
- Reported for every cell, no rule attached: min, median, max of the 16 pooled ratios; how many placements pass and how many cost; the same over both sizes (32); the `ref` and `a64` ratios; the median ratio split by whether FAST's hot loop touches more 64-byte windows than its length needs while NONE's does not.

## What this can and cannot show
It shows how much of the FAST/NONE ratio of these loops moves with where the loop sits, on the CPU models the runners draw. It does not show the cause (no hardware counters on these VMs; the front-end explanation stays inferred), does not cover other kernels or arm64, and uses one compiler and one family of layouts (4-byte steps of the function start; the loop's offset inside its function is whatever the compiler emitted). A ROBUST result is a statement about these 16 placements.

## Run
`gh workflow run layout-sweep.yml` (in the public repo), download the artifacts, then `python layout-sweep/analyze.py <dir> --out layout-sweep/results/<run>/analysis.json`. Offline check: `python layout-sweep/check.py`.

## Amendment 1 (Tue Oct 13 13:39 EDT 2026; written BEFORE the next run; no timing number from any layout-sweep run exists)
What happened: run 38439008261 aborted at the mechanism probe, as designed, with no timing. On the runner (clang 18, k02_add_fwd FAST) the hot-loop start stayed 16-byte aligned for padding 0, 4 and 12 bytes (addresses 4640, 4656, 4656), and the variant with `-mllvm -x86-experimental-pref-loop-alignment=0` did not build. So the compiler by default places loops at multiples of 16 bytes: the loop-start residues mod 64 it can produce by itself are 0, 16, 32, 48.
Change (criteria.json version 2, `modes`):
- mode `fine` (unchanged intent): 16 placements, 4-byte steps, with the first loop-alignment variant that passes the probe. Tried first.
- mode `coarse` (fallback, automatic): 4 placements p00..p03, 16-byte steps of function padding (0, 16, 32, 48 bytes), compiler-default function and loop alignment (no alignment flags). The probe builds k02 FAST at pads 0, 16, 32, 48 and requires function and hot loop to move by exactly the pad (so the four loop-start residues mod 64 are distinct); otherwise the run aborts before timing. A run never mixes modes; `mechanism.mode` records which ran, and the analysis refuses to pool jobs of different modes.
- Thresholds scale with the realised count. Fine: unchanged (ROBUST needs at least 15 of 16 passing, PLACEMENT_DEPENDENT at most 7, lost control at least 15 of 16). Coarse: ROBUST needs all 4 of 4 passing; PLACEMENT_DEPENDENT at most 1 of 4; MIXED is 2 or 3 of 4; the lost control holds only if 4 of 4 hold. All other rules (A/A at most 2 %, forward 1.02 and CI limit, lost 1.5, minimum 3 jobs, checksums, sha agreement, INCONCLUSIVE conditions) are unchanged. Coarse mode is a statement about the four placements the compiler can itself produce, which is weaker than 16 and is reported as 4.
- The `ref` and `a64` placements are kept in both modes.
Also: the workflow's analyse job skips with a message when no sweep job produced results.

## Change log
- Tue Oct 13 15:02 EDT 2026: runs 38447223382 and 38447234861 failed before timing because the repository's offline check broke on a checker bug (fixed; no threshold or rule touched). Two reruns (38450563180, 38450575075) succeeded. The reading is the pooling of all three successful runs (38440485436, 38450563180, 38450575075) per CPU model, each distinct results.json once (sha256), in `layout-sweep/results/pooled/analysis.json`. Thresholds unchanged (criteria.json v2).
