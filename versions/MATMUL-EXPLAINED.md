# Why matmul (k08) is a lost loop on clang/libc++ 18 but not on 19, 20, 21

Status: partly shown, partly inferred. The "why" at compiler-source level is NOT shown.

## What was compared
- clang 18 asm and remarks: `results/s3-audit-run-38127024171/results-amd-epyc-9v45-96-core-processor-j2/{asm,remarks}/k08_matmul.{none,fast}`.
- clang 19 asm and remarks: `versions/results/38471430657/versions-19-amd-epyc-7763-64-core-processor-j10/...` (20 and 21: remarks and a grep of the asm only).
- Same source (`kernels/k08_matmul.cpp`), same flags (`-O2 -std=c++20 -stdlib=libc++`, harness/run.py). The two files come from different CPU models; the asm does not depend on the CPU (no -march), but I did not diff a clang-18 build from a 7763 job (no clang is installed on this machine; nothing was recompiled here).

## Shown (read from the files)
1. Clang 18, NONE: inner loop `vectorized loop (vectorization width: 4, interleaved count: 2)`.
2. Clang 18, FAST: remark `the cost-model indicates that vectorization is not beneficial`. The asm is a scalar inner loop of 12 instructions with two bounds checks per element (`cmp; jbe -> ud2` for `b[k*d+j]` and `c[i*d+j]`), no packed instructions (0 matches for padd/pmul/pshuf).
3. Clang 19 (and 20, 21), FAST: the same loop is `vectorized loop (width 4, interleaved count 2)`. The vector body (8 ints per trip, `pmuludq`/`paddd`) contains no `ud2` branch and no bounds check. The checks sit outside it: (a) a check of `a[i*d+k]` once per (i,k); (b) a block of `cmp/cmov` that clamps the trip count to the largest index that passes both size checks (it reads vector end minus begin for b and c); (c) a runtime overlap test (c vs b) that falls back to the scalar loop; (d) a scalar remainder loop that still has both checks and the `ud2` exits. A single `ud2` target remains in the function for 19, 20 and 21 (in the 18-FAST asm also one).
4. Clang 19 NONE and FAST use the same vector body (same instructions; SSE2 only, no AVX2), so FAST adds only the code around it.
5. Measured on EPYC 7763 (versions/results/38471430657, j10): FAST/NONE 1.61 at L1 (d=36 inner trip count, 15,552 B) and 1.15 at L2 (d=147, 259 KB). Clang 18 on 7763: 3.2 (per the task brief).

## Inferred (consistent with the above, not proven)
- Clang 19+ turns the per-element `index < size` checks into a bound on the trip count (check hoisting / loop predication of an invariant-stride check), after which the vectorizer sees a countable loop with no side exits. Clang 18 left the checks in the loop; the remark then says the cost model rejects vectorization. That the exits are the reason for the 18 rejection is my reading: the remark says "cost model", not "legality".
- The remaining 1.61x at L1 is the new overhead around the vector body: about 60 prologue instructions with stack spills per (i,k) pair, amortized over only 36 elements, with 4 elements left to the checked scalar remainder. At L2 (147 elements) the same overhead is spread wider, which fits 1.15x. I did not measure the prologue cost separately (no perf counters, no instruction-level timing), so the split is an estimate.

## NOT shown
- Which LLVM change between 18 and 19 caused the hoisting. I did not bisect LLVM or read its release notes/commits; I cannot name the pass or patch.
- Whether it is a libc++ change (how `operator[]` hardening is written) or an LLVM optimizer change. Both toolchains' libc++ differ (18 vs 19), the compiler too; nothing here separates them. A test that would: compile the clang-19 library headers with clang 18 or the reverse, or the same source on Compiler Explorer with clang 18.1 and 19.1 and `-stdlib=libc++` (not run: no tool for it here).
- Other loops: this says nothing about why reverse and stride-2 stay lost on 19 to 21, only that matmul's inner loop (forward, unit stride, checks on loop-linear indices) is the shape that got the hoist.
