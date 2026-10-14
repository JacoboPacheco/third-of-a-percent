# Compiler Explorer sweep: which loops lose SIMD under library bounds checks, across compilers

**Compile-only. No timing.** This folder asks one question of many compilers: when the standard
library's bounds checks are turned on, which of the project's 8 loops stop being vectorized? The
main study answered it with clang 18 at x86-64 baseline (plus clang 20 and GCC 14 in `siblings/`).
Here the same 8 loop functions go through 28 compilers on Compiler Explorer's public API.

## What was compiled

- **Source:** `source.cpp`, the 8 `kern_*` functions copied verbatim from `kernels/kNN_*.cpp` into
  one file (no `main`, `#include <vector>` only). Each function is `noinline` and independent.
- **Compilers (Compiler Explorer ids in `cesweep.py`):**
  - clang 16.0.0, 17.0.1, 18.1.0, 19.1.0, 20.1.0, 21.1.0, 22.1.0, 23.1.0 and trunk, each with
    `-stdlib=libc++`, for x86-64 and for AArch64 (the "armv8-a clang" builds);
  - GCC 12.5, 13.4, 14.4, 15.3, 16.2 (x86-64) and 12.5.0, 13.4.0, 14.3.0, 15.2.0, 16.1.0 (ARM64), with libstdc++.
    GCC 16 is one more than asked for.
- **Targets:** `-march=x86-64` (SSE2 baseline), `-march=x86-64-v3` (AVX2), AArch64 default (armv8-a, NEON).
- **Optimization:** `-O2` and `-O3`.
- **Checks off / on**, with the macro that fits each library version:

  | library | off | on |
  |---|---|---|
  | libc++ 18 and later | `_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE` | `..._FAST` |
  | libc++ 17 | `_LIBCPP_ENABLE_HARDENED_MODE=0` | `=1` |
  | libc++ 16 | `_LIBCPP_ENABLE_ASSERTIONS=0` | `=1` (libc++ 16 has no separate fast mode) |
  | libstdc++ | (none) | `_GLIBCXX_ASSERTIONS` |

  In all 84 pairs, the checked build has more check sites in the 8 functions than the unchecked
  build, so the macro took effect every time. Check sites are traps plus calls to a failure handler;
  the `macro_effective` column is in `results.json`.
- **Remarks:** clang `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize`;
  GCC `-fopt-info-vec-optimized`.

That makes 168 compiles (84 off/on pairs) and 672 cells of (compiler, target, opt level, loop).

**"Lost"** uses the project's definition: vectorized in the unchecked build and not in the checked
build. The answer comes from the compiler's own remark at the loop's `// LOOP` line (the rule in
`harness/remarks.py`). As a cross-check, every function's assembly was also searched for
vector-register instructions. The remark and the assembly agree on all 1,344 build sides
(672 cells × off/on); the `remark_asm_disagree` lists in `results.json` are all empty.

## Control

clang 18.1.0, x86-64, -O2, libc++ FAST against NONE loses exactly **reverse, stride2, matmul**, as
in the main study (`audit/out-asm.txt`). The packed-instruction counts are the same too (reverse
6 to 0, stride2 14 to 0, matmul 22 to 0, add_fwd 8 to 4), with one `ud2` per checked function.
`check.py` fails if this row changes.

## The matrix

<!-- matrix:begin (written by build_results.py) -->
| compiler | target | opt | hardening macro | lost under hardening | vectorized unhardened |
|---|---|---|---|---|---|
| clang 16.0.0 | x86-64 | -O2 | `_LIBCPP_ENABLE_ASSERTIONS=1` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 16.0.0 | x86-64 | -O3 | `_LIBCPP_ENABLE_ASSERTIONS=1` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 16.0.0 | x86-64-v3 | -O2 | `_LIBCPP_ENABLE_ASSERTIONS=1` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 16.0.0 | x86-64-v3 | -O3 | `_LIBCPP_ENABLE_ASSERTIONS=1` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 17.0.1 | x86-64 | -O2 | `_LIBCPP_ENABLE_HARDENED_MODE=1` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 17.0.1 | x86-64 | -O3 | `_LIBCPP_ENABLE_HARDENED_MODE=1` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 17.0.1 | x86-64-v3 | -O2 | `_LIBCPP_ENABLE_HARDENED_MODE=1` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 17.0.1 | x86-64-v3 | -O3 | `_LIBCPP_ENABLE_HARDENED_MODE=1` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 18.1.0 | x86-64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 18.1.0 | x86-64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 18.1.0 | x86-64-v3 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 18.1.0 | x86-64-v3 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 19.1.0 | x86-64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 19.1.0 | x86-64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 19.1.0 | x86-64-v3 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 19.1.0 | x86-64-v3 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 20.1.0 | x86-64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 20.1.0 | x86-64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 20.1.0 | x86-64-v3 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 20.1.0 | x86-64-v3 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 21.1.0 | x86-64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 21.1.0 | x86-64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 21.1.0 | x86-64-v3 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 21.1.0 | x86-64-v3 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 22.1.0 | x86-64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 22.1.0 | x86-64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 22.1.0 | x86-64-v3 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 22.1.0 | x86-64-v3 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 23.1.0 | x86-64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 23.1.0 | x86-64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 23.1.0 | x86-64-v3 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 23.1.0 | x86-64-v3 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang trunk | x86-64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang trunk | x86-64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang trunk | x86-64-v3 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang trunk | x86-64-v3 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 16.0.0 | aarch64 | -O2 | `_LIBCPP_ENABLE_ASSERTIONS=1` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 16.0.0 | aarch64 | -O3 | `_LIBCPP_ENABLE_ASSERTIONS=1` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 17.0.1 | aarch64 | -O2 | `_LIBCPP_ENABLE_HARDENED_MODE=1` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 17.0.1 | aarch64 | -O3 | `_LIBCPP_ENABLE_HARDENED_MODE=1` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 18.1.0 | aarch64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 18.1.0 | aarch64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 19.1.0 | aarch64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 19.1.0 | aarch64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 20.1.0 | aarch64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 20.1.0 | aarch64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 21.1.0 | aarch64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 21.1.0 | aarch64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 22.1.0 | aarch64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 22.1.0 | aarch64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 23.1.0 | aarch64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang 23.1.0 | aarch64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang trunk | aarch64 | -O2 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| clang trunk | aarch64 | -O3 | `_LIBCPP_HARDENING_MODE_FAST` | **rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 12.5 | x86-64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 12.5 | x86-64 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, stencil, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 12.5 | x86-64-v3 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 12.5 | x86-64-v3 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, stencil, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 13.4 | x86-64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 13.4 | x86-64 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, stencil, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 13.4 | x86-64-v3 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 13.4 | x86-64-v3 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, stencil, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 14.4 | x86-64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 14.4 | x86-64 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, stencil, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 14.4 | x86-64-v3 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 14.4 | x86-64-v3 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 15.3 | x86-64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 15.3 | x86-64 | -O3 | `_GLIBCXX_ASSERTIONS` | **rev, matmul** | sum_fwd, rev, matmul |
| GCC 15.3 | x86-64-v3 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | sum_fwd |
| GCC 15.3 | x86-64-v3 | -O3 | `_GLIBCXX_ASSERTIONS` | **rev, matmul** | sum_fwd, rev, matmul |
| GCC 16.2 | x86-64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 16.2 | x86-64 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, stencil, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 16.2 | x86-64-v3 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | sum_fwd |
| GCC 16.2 | x86-64-v3 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 12.5.0 | aarch64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 12.5.0 | aarch64 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, stencil, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 13.4.0 | aarch64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 13.4.0 | aarch64 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, stencil, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 14.3.0 | aarch64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 14.3.0 | aarch64 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, rev, stride2, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |
| GCC 15.2.0 | aarch64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 15.2.0 | aarch64 | -O3 | `_GLIBCXX_ASSERTIONS` | **rev, matmul** | sum_fwd, rev, matmul |
| GCC 16.1.0 | aarch64 | -O2 | `_GLIBCXX_ASSERTIONS` | **none** | none |
| GCC 16.1.0 | aarch64 | -O3 | `_GLIBCXX_ASSERTIONS` | **add_fwd, rev, matmul** | sum_fwd, add_fwd, stencil, rev, stride2, matmul |

Compact view, the three loops of the finding (R = reverse, S = stride2, M = matmul; a letter means lost, `.` kept vectorized, `x` not vectorized even unhardened), cells are -O2 / -O3:

| compiler | x86-64 | x86-64-v3 | aarch64 |
|---|---|---|---|
| clang 16.0.0 | RSM / RSM | RS. / RS. | RS. / RS. |
| clang 17.0.1 | RSM / RSM | RS. / RS. | RS. / RS. |
| clang 18.1.0 | RSM / RSM | RS. / RS. | RS. / RS. |
| clang 19.1.0 | RS. / RS. | RS. / RS. | RS. / RS. |
| clang 20.1.0 | RS. / RS. | RS. / RS. | RS. / RS. |
| clang 21.1.0 | RS. / RS. | RS. / RS. | RS. / RS. |
| clang 22.1.0 | RS. / RS. | RS. / RS. | RS. / RS. |
| clang 23.1.0 | RSM / RSM | RSM / RSM | RSM / RSM |
| clang trunk | RSM / RSM | RSM / RSM | RSM / RSM |
| GCC 12.5 / 12.5.0 | xxx / RSM | xxx / RSM | xxx / RSM |
| GCC 13.4 / 13.4.0 | xxx / RSM | xxx / RSM | xxx / RSM |
| GCC 14.4 / 14.3.0 | xxx / RSM | xxx / RSM | xxx / RSM |
| GCC 15.3 / 15.2.0 | xxx / RxM | xxx / RxM | xxx / RxM |
| GCC 16.2 / 16.1.0 | xxx / RSM | xxx / RSM | xxx / R.M |
<!-- matrix:end -->

## Does the finding generalize?

The matrix shows the following, and nothing more. **Reverse and stride-2** lose vectorization under
libc++ checks in every clang row: 54 of 54 (versions 16 to trunk; x86-64, x86-64-v3 and AArch64;
-O2 and -O3). No clang row loses a forward loop (sum, add, stencil). Gather and histogram are never
vectorized, with or without checks. **Matrix multiply is the loop that depends on the toolchain.**
clang 16 to 18 lose it at x86-64 baseline only; at x86-64-v3 and on AArch64 they keep it. clang 19
to 22 keep it on every target. clang 23.1 and trunk lose it on every target, AArch64 included;
their remark names a new reason, "Early exit loop with store but no supported condition load". So
"reverse and stride-2 lose SIMD under libc++ hardening" holds across every clang and target tried
here. "Matrix multiply loses SIMD" holds only for some clang versions and targets.
**GCC with `_GLIBCXX_ASSERTIONS` behaves differently.** At -O2 it vectorizes none of these loops even
without checks; GCC 15 and 16 at x86-64-v3 vectorize only the sum. So at -O2 nothing can be lost.
At -O3 it loses reverse and matmul in every version. It also loses stride-2 in every version except
GCC 15, which does not vectorize stride-2 even without checks, and GCC 16.1 on ARM64, which keeps it.
Unlike clang, it also loses the forward add loop in most versions, and the stencil in some.

Surprises:
- clang 19 to 22 keep matmul vectorized under FAST even at SSE2. clang 23.1 and trunk lose it again,
  even at AVX2 and on AArch64.
- In clang 16 to 22, AArch64 behaves like x86-64-v3: matmul is kept. No loop is lost on AArch64 only.
- GCC 15 (15.3 on x86-64, 15.2.0 on ARM64) does not vectorize add_fwd, stencil or stride2 at -O3
  even with checks off. The assembly confirms it: no vector instructions in those functions. GCC 14
  and GCC 16 do vectorize them.
- In clang 18 and later, `k01_sum_fwd` has no trap at all in the checked build: the compiler proves
  the check redundant. Every other function has exactly one trap (`ud2` on x86-64, `brk #0x1` on AArch64).

## Compiler Explorer links (clang 18.1.0, x86-64, -O2, libc++, panes NONE and FAST side by side)

Made with the public `POST /api/shortener` (no account or key), then read back with
`/api/shortlinkinfo/<id>`. All 8 were checked: the stored source and both option strings match
what was sent (`permalinks.json`). Each link holds one loop function and two compiler panes. A
diff pane is not included, because the API's simple state format has no way to describe one.

- k01_sum_fwd: https://godbolt.org/z/655efP99r
- k02_add_fwd: https://godbolt.org/z/aqh4c3EM8
- k03_stencil: https://godbolt.org/z/MosWGxaeo
- k04_rev: https://godbolt.org/z/EGPjvWTP5
- k05_stride2: https://godbolt.org/z/d1eYx5hPj
- k06_gather: https://godbolt.org/z/W7h1GEMvj
- k07_hist: https://godbolt.org/z/MT3Th6drT
- k08_matmul: https://godbolt.org/z/zdnz5j3Ga

## What this does not show

- **No timing.** "Lost" is a compile-time fact. What it costs is measured only for clang 18 (and the
  `siblings/` toolchains) in the main study.
- **Compiler Explorer's builds** of each compiler and library. The libc++ used with clang N is
  taken to be libc++ N; it was not checked beyond the macro having its expected effect.
  "trunk" means trunk as Compiler Explorer served it on 2026-10-12 (`fetched_at` in each cached answer).
- **The AArch64 rows use the default armv8-a target.** That means NEON only: no SVE, no `-mcpu` tuning.
- **Check-site counts for GCC and for libc++ 16/17** count only the failure calls inside the
  function's own text. When GCC merges failure paths across functions, which happens at -O3 in
  GCC 15 and 16, a function can show 0. Treat those counts as a lower bound. The vectorization
  verdict does not depend on them.
- Only these 8 loops; no Apple clang, MSVC, PGO or LTO.

## Requests and cache

About 190 requests in total, one at a time and at least 1.2 s apart:
- 168 compiles;
- 1 compiler list;
- 8 short links and 8 read-backs;
- a few retries after one HTTP 504.

The requests carried a User-Agent naming this project. No 429 and no key was needed. Every compile
answer is in `cache/<compiler>__<target>__<opt>__<mode>.json.gz`, together with:
- the request's SHA-256, which `results.json` also records for each cell;
- the URL it was sent to;
- the time it was fetched.

Since 2026-10-12 21:57 UTC, each request is also logged in `cache/requests.log`. That file stays on the machine that ran the sweep: `*.log` is gitignored.

## Files and commands

- `cesweep.py`: source extraction, build matrix, request, parsers (no network).
- `sweep.py`: sends the missing compiles (polite; stops on 429/403/401; resumes from the cache).
- `make_links.py`: the 8 short links.
- `build_results.py`: cache to `results.json` and the matrix above (offline). Use `--check` to compare
  without writing.
- `check.py`: offline. Runs the unit tests, then checks that:
  - `source.cpp` matches `kernels/`;
  - every cached request hash matches today's request;
  - the schema of `results.json` is as expected;
  - a fresh recomputation equals `results.json` and the matrix;
  - the control holds.
- `test_cesweep.py`: parser and pairing tests, plus the control from the cache.

```
python ce-sweep/check.py                 # offline, a few seconds
python ce-sweep/sweep.py && python ce-sweep/build_results.py   # refetch (only what is not cached)
```

**Hooking it into `scripts/check.py`** (not done here): add a block in the same shape as the
lostloops one, before the page block:

```python
    print("== Compiler Explorer sweep (ce-sweep/check.py: offline, recomputed from cached compiles)")
    if os.path.exists(os.path.join(REPO, "ce-sweep", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "ce-sweep", "check.py")]) == 0
    else:
        print("   none yet")
```
