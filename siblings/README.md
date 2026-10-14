# Siblings: does the finding hold beyond clang 18 + libc++ 18 FAST?

Every number on the main page comes from one setup: Ubuntu clang 18.1.3, libc++ 18 in FAST mode, `-O2`, baseline x86-64 (SSE2). This folder runs the same 8 kernels (`kernels/*.cpp`, unchanged) with the same method next to six other setups, so a reader can see what changes when the setup changes.

## Short answer

**It depends on the compiler, and the forward-loop part holds only under clang.**
- **Holds:** a check that keeps a loop from vectorizing costs several times; on the AMD models, a check that stays out of the vector loop costs about nothing (0.82x to 1.02x for the forward add; the exception is `-march=x86-64-v3`, where it reached 1.11x on one EPYC 9V45 job).
- **clang (18 and 20, every libc++ mode tried):** forward loops keep their vectorization. On the AMD models the forward add costs 0.82x to 1.02x aligned (0.95x to 1.11x with `-march=x86-64-v3`); on the Intel models drawn it costs up to 1.20x at L1 under clang 18 FAST (Xeon 6973P-C, 1 job; 1.06x on the Xeon Platinum 8573C, 1 job). Reverse and stride-2 loops lose vectorization and cost 1.6x to 9.7x (2.9x and up outside one AVX2 cell, reverse at L2 on the 8573C).
- **GCC 14 with libstdc++ `_GLIBCXX_ASSERTIONS`:** forward loops pay too. At `-O3` the checks stop the forward add and the stencil from vectorizing (forward add 4.9x to 8.5x; the forward sum stays vectorized at 1.00x). At `-O2` nothing vectorizes in either build, and the checks still cost up to 2.2x (2.4x for the gather, one job on the Xeon 6973P-C).
- **Matrix multiply depends on the setup:** clang 20, or `-march=x86-64-v3`, keeps it vectorized under FAST. It still costs 1.5x to 2.3x at L1.

## How to run it

One click: Actions, **siblings**, Run workflow (`.github/workflows/siblings.yml`). It runs 3 parts x 4 jobs on `ubuntu-24.04` x64, about 12 minutes per job. Each job uploads `siblings-<part>-<cpu>-j<N>`, which holds `siblings.json` (every raw sample), the assembly of every build, the compiler remarks and the installed package versions. To get the tables below from downloaded runs:

    python siblings/summarize.py results/siblings-run-38256975670 results/siblings-run-38259634798

| part | variants (hardened build vs that toolchain's own unhardened build) |
|---|---|
| A | `clang18-fast` (the reference row), `clang18-extensive`, `clang18-debug`, `clang18v3-fast` (all builds `-march=x86-64-v3`, timed only when `/proc/cpuinfo` has every x86-64-v3 flag; every runner drawn had them) |
| B | `clang18-fast` (the reference again), `gcc14-O2-assert`, `gcc14-O3-assert` |
| C | `clang20-fast` (clang 20 with libc++ 20). It runs alone because `libc++-20-dev` and `libc++-18-dev` cannot be installed together (apt: "held broken packages", run 38256448953). Read it against the A and B jobs on the same CPU model. |

**Packages (Ubuntu noble apt only, versions as installed):** `clang-18 1:18.1.3-1ubuntu1`, `libc++-18-dev` and `libc++abi-18-dev 1:18.1.3-1ubuntu1`, `g++-14 14.2.0-4ubuntu2~24.04.1`, `clang-20 1:20.1.2-0ubuntu1~24.04.3`, `libc++-20-dev` and `libc++abi-20-dev 1:20.1.2-0ubuntu1~24.04.3` (noble-updates/universe). apt offered clang 19 and 20 and no clang 21, so clang 20 is the newest used.

**Flags.**

| toolchain | common flags | unhardened | hardened |
|---|---|---|---|
| clang (18 or 20) | `-O2 -std=c++20 -stdlib=libc++` | `-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE` | `..._FAST`, `..._EXTENSIVE` or `..._DEBUG` |
| GCC 14 | `g++-14 -O2` (or `-O3`) `-std=c++20` | `-U_GLIBCXX_ASSERTIONS` | `-D_GLIBCXX_ASSERTIONS` |

Every build is also made with `-falign-loops=64`, which gives the "aligned" pair.

**Remarks.** clang: `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize`. GCC: `-fopt-info-vec-optimized -fopt-info-vec-missed`. Only remarks at the kernel's `// LOOP` line are read (`siblings/remarks.py`).

**Traps.** These are counted in `kern_<id>` and its `.cold` part: `ud2`, plus calls to `__libcpp_verbose_abort` or `std::__glibcxx_assert_fail` (`siblings/asm.py`).

**Method:** the same as `harness/run.py`:
- **Timing:** 20 processes per side, in ABBA order, pinned with `taskset -c 1`. The inner iterations are calibrated to about 75 ms per process on each toolchain's own unhardened build.
- **Ratio and interval:** the ratio is median(hardened) / median(unhardened). The 95% interval is a percentile bootstrap with 10,000 resamples and seed 20261011 (`siblings/stats.py` is a verbatim copy of `harness/stats.py`).
- **Controls per toolchain, in every job:**
  - an A/A: unhardened `k02_add_fwd` at L1 against a byte-identical copy;
  - a layout A/A: unhardened against unhardened built with `-falign-loops=64`.
- **Sizes:** L1 (half of L1d) and L2 (half of L2) only.
- **Exclusion rule:** a job's cells for one toolchain are dropped when that toolchain's A/A half-width in that job is above 2.0%. This is the project's `aa_half_width_max_pct`.
- **Checks:**
  - every pair's checksums matched (hardened against its own toolchain's unhardened build). Across toolchains they agree for the six kernels whose output does not depend on the iteration count; k07_hist and k08_matmul accumulate over a per-toolchain calibrated iteration count, so their checksums are compared within one toolchain only;
  - all 192 binaries are byte-identical across all 23 jobs of both runs, so the vectorization and trap columns are the same in every job.

**Runs:**
- run 38256975670: 11 jobs. Job C3 hung in apt until the job timeout, so its job was cancelled and it has no data.
- run 38259634798: 12 jobs.

Both are in `results/siblings-run-<id>/`. Every binary is byte-identical across jobs, so the `asm/` and `remarks/` folders are kept once per part per run.

## Results (both runs pooled per CPU model)

Jobs read: 23, on 5 CPU models: AMD EPYC 7763, 9V45 and 9V74; Intel Xeon 6973P-C; Intel Xeon Platinum 8573C.

Excluded (A/A half-width above 2%), 7 toolchain-job pairs:
- run 38256975670, A on EPYC 9V45 j2: clang18 4.34%, clang18v3 3.22%
- run 38256975670, B on EPYC 9V45 j3: clang18 2.01%, gcc14O2 2.94%, gcc14O3 2.14%
- run 38259634798, A on Xeon Platinum 8573C j1: clang18 2.76%, clang18v3 3.12%

### Which loops lose vectorization (from the compiler's own remarks)

| variant | compiler | lost (vectorized unhardened, not hardened) | same set as the reference? |
|---|---|---|---|
| clang18-fast | Ubuntu clang 18.1.3 | k04_rev, k05_stride2, k08_matmul | reference |
| clang18-extensive | Ubuntu clang 18.1.3 | k04_rev, k05_stride2, k08_matmul | yes |
| clang18-debug | Ubuntu clang 18.1.3 | k04_rev, k05_stride2, k08_matmul | yes |
| clang18v3-fast | Ubuntu clang 18.1.3, `-march=x86-64-v3` | k04_rev, k05_stride2 | **no**: k08_matmul stays vectorized |
| clang20-fast | Ubuntu clang 20.1.2, libc++ 20 | k04_rev, k05_stride2 | **no**: k08_matmul stays vectorized |
| gcc14-O2-assert | g++-14 14.2.0 | none | **no**: no loop is vectorized in either build |
| gcc14-O3-assert | g++-14 14.2.0 | k02_add_fwd, k03_stencil, k04_rev, k05_stride2, k08_matmul | **no**: the forward loops k02 and k03 are lost too |

**Control:** the classifier marks reverse, stride-2 and matmul as lost under libc++ FAST on clang 18 (the reference row), as on the main page.

Where the set differs, in the compiler's own words:
- **clang18v3-fast, k08_matmul.** Unhardened: `vectorized loop (vectorization width: 8, interleaved count: 4)`. Hardened: `vectorized loop (vectorization width: 8, interleaved count: 1)` plus `the cost-model indicates that interleaving is not beneficial`.
- **clang20-fast, k08_matmul.** Unhardened and hardened both: `vectorized loop (vectorization width: 4, interleaved count: 2)`.
- **gcc14-O3-assert, k02_add_fwd and k03_stencil.**
  - Unhardened: `loop vectorized using 16 byte vectors`, `loop versioned for vectorization because of possible aliasing`.
  - Hardened: `couldn't vectorize loop`. The reason GCC gives is `not vectorized: no vectype for stmt: _20 = MEM[(int * *)c_15(D)]` for k02 (the same message names `c` for k04 and k08) and `unsupported data-type long unsigned int` for k03.
  - The `-O2` assembly shows the same pattern: the hardened loop reloads `c`'s data pointer and end pointer on every iteration (`results/siblings-run-38256975670/siblings-B-amd-epyc-9v74-80-core-processor-j1/asm/k02_add_fwd.gcc14-O2-assert_a64.diff`).
- **gcc14-O2-assert, every kernel.** Unhardened: `couldn't vectorize loop` / `not vectorized: unsupported data-type`. With nothing vectorized in either build, there is nothing to lose. The three "differs" lines for k04, k05 and k08 in `summarize.py`'s output mean exactly this.

### Aligned hardened/unhardened ratio, L1 size

**How to read a cell:** for each CPU model, the median of the usable jobs' ratios, then [lowest 95% bound, highest 95% bound] over those jobs, then the number of jobs. A dash means that variant was not drawn on that CPU model. Traps count `kern_<id>` in the unhardened build, then in the hardened build.

| variant | kernel | vectorized unhardened | vectorized hardened | traps | EPYC 7763 | EPYC 9V45 | EPYC 9V74 | Xeon 6973P-C | Xeon Platinum 8573C |
|---|---|---|---|---|---|---|---|---|---|
| clang18-fast | k01_sum_fwd | yes (w2) | yes (w2) | 0 -> 0 | 1.00 [0.98, 1.02] x6 | 1.00 [1.00, 1.01] x1 | 1.00 [1.00, 1.01] x4 | 1.00 [0.97, 1.03] x1 | 1.00 [1.00, 1.00] x1 |
| clang18-fast | k02_add_fwd | yes (w4) | yes (w4) | 0 -> 1 | 0.83 [0.83, 0.84] x6 | 0.84 [0.83, 0.85] x1 | 0.83 [0.82, 0.83] x4 | 1.20 [1.19, 1.21] x1 | 1.06 [1.05, 1.06] x1 |
| clang18-fast | k03_stencil | yes (w4) | yes (w4) | 0 -> 1 | 1.06 [0.90, 1.07] x6 | 1.02 [1.00, 1.03] x1 | 1.00 [0.98, 1.01] x4 | 1.01 [1.01, 1.01] x1 | 1.01 [1.01, 1.02] x1 |
| clang18-fast | k04_rev | yes (w4) | no | 0 -> 1 | 8.00 [7.96, 8.03] x6 | 5.60 [5.54, 5.63] x1 | 5.38 [5.35, 5.40] x4 | 6.52 [6.44, 6.61] x1 | 6.64 [6.59, 6.66] x1 |
| clang18-fast | k05_stride2 | yes (w4) | no | 0 -> 1 | 5.08 [5.05, 5.09] x6 | 2.86 [2.83, 2.88] x1 | 5.10 [5.08, 5.12] x4 | 4.97 [4.97, 4.98] x1 | 4.35 [4.32, 4.37] x1 |
| clang18-fast | k06_gather | no | no | 0 -> 1 | 1.84 [1.83, 1.87] x6 | 1.73 [1.70, 1.75] x1 | 1.58 [1.57, 1.59] x4 | 2.16 [2.13, 2.16] x1 | 2.18 [2.15, 2.19] x1 |
| clang18-fast | k07_hist | no | no | 0 -> 1 | 1.09 [1.00, 1.13] x6 | 1.24 [1.22, 1.25] x1 | 1.10 [0.97, 1.43] x4 | 1.29 [1.13, 1.37] x1 | 1.11 [1.05, 1.24] x1 |
| clang18-fast | k08_matmul | yes (w4) | no | 0 -> 1 | 3.19 [3.18, 3.19] x6 | 3.81 [3.78, 3.84] x1 | 4.05 [4.03, 4.06] x4 | 4.01 [3.95, 4.02] x1 | 3.12 [3.10, 3.23] x1 |
| clang18-extensive | k01_sum_fwd | yes (w2) | yes (w2) | 0 -> 0 | 1.00 [0.99, 1.00] x3 | 1.00 [1.00, 1.00] x1 | 1.00 [1.00, 1.00] x1 | - | 1.00 [1.00, 1.00] x1 |
| clang18-extensive | k02_add_fwd | yes (w4) | yes (w4) | 0 -> 1 | 0.84 [0.83, 0.84] x3 | 0.83 [0.83, 0.84] x1 | 0.83 [0.83, 0.86] x1 | - | 1.06 [1.05, 1.06] x1 |
| clang18-extensive | k03_stencil | yes (w4) | yes (w4) | 0 -> 1 | 1.05 [1.03, 1.08] x3 | 1.02 [0.92, 1.02] x1 | 1.01 [0.98, 1.22] x1 | - | 1.01 [1.00, 1.01] x1 |
| clang18-extensive | k04_rev | yes (w4) | no | 0 -> 1 | 7.98 [7.96, 8.17] x3 | 5.52 [5.47, 5.61] x1 | 5.60 [5.51, 5.64] x1 | - | 6.64 [6.61, 6.66] x1 |
| clang18-extensive | k05_stride2 | yes (w4) | no | 0 -> 1 | 5.07 [5.06, 5.09] x3 | 2.87 [2.84, 2.90] x1 | 5.10 [5.09, 5.11] x1 | - | 4.36 [4.34, 4.38] x1 |
| clang18-extensive | k06_gather | no | no | 0 -> 1 | 1.86 [1.84, 1.89] x3 | 1.70 [1.68, 1.74] x1 | 1.58 [1.58, 1.59] x1 | - | 2.18 [2.17, 2.19] x1 |
| clang18-extensive | k07_hist | no | no | 0 -> 1 | 1.10 [1.09, 1.17] x3 | 1.24 [1.21, 1.26] x1 | 1.11 [1.10, 1.20] x1 | - | 1.21 [1.16, 1.42] x1 |
| clang18-extensive | k08_matmul | yes (w4) | no | 0 -> 1 | 3.19 [3.18, 3.21] x3 | 3.78 [3.71, 3.85] x1 | 4.05 [4.05, 4.06] x1 | - | 3.15 [3.10, 3.35] x1 |
| clang18-debug | k01_sum_fwd | yes (w2) | yes (w2) | 0 -> 0 | 1.00 [1.00, 1.00] x3 | 1.00 [0.99, 1.01] x1 | 1.00 [1.00, 1.00] x1 | - | 1.00 [1.00, 1.00] x1 |
| clang18-debug | k02_add_fwd | yes (w4) | yes (w4) | 0 -> 2 | 0.83 [0.83, 0.83] x3 | 0.83 [0.83, 0.84] x1 | 0.83 [0.83, 0.84] x1 | - | 1.05 [1.05, 1.06] x1 |
| clang18-debug | k03_stencil | yes (w4) | yes (w4) | 0 -> 1 | 1.05 [0.84, 1.06] x3 | 1.02 [1.00, 1.04] x1 | 1.00 [0.98, 1.00] x1 | - | 1.01 [1.00, 1.01] x1 |
| clang18-debug | k04_rev | yes (w4) | no | 0 -> 1 | 8.00 [7.98, 8.11] x3 | 5.57 [5.51, 5.63] x1 | 5.38 [5.38, 5.39] x1 | - | 6.71 [6.46, 6.80] x1 |
| clang18-debug | k05_stride2 | yes (w4) | no | 0 -> 2 | 5.07 [5.03, 5.09] x3 | 2.85 [2.82, 2.88] x1 | 5.10 [5.09, 5.11] x1 | - | 4.36 [4.33, 4.41] x1 |
| clang18-debug | k06_gather | no | no | 0 -> 2 | 1.84 [1.84, 1.88] x3 | 1.71 [1.70, 1.75] x1 | 1.59 [1.58, 1.59] x1 | - | 2.18 [2.16, 2.20] x1 |
| clang18-debug | k07_hist | no | no | 0 -> 1 | 1.07 [0.91, 1.12] x3 | 1.23 [1.20, 1.26] x1 | 1.11 [1.10, 1.16] x1 | - | 1.20 [1.17, 1.38] x1 |
| clang18-debug | k08_matmul | yes (w4) | no | 0 -> 3 | 3.20 [3.18, 3.21] x3 | 3.91 [3.86, 3.95] x1 | 4.05 [4.04, 4.05] x1 | - | 3.11 [3.08, 3.19] x1 |
| clang18v3-fast | k01_sum_fwd | yes (w4) | yes (w4) | 0 -> 0 | 1.00 [0.99, 1.00] x3 | 1.00 [0.99, 1.00] x1 | 1.00 [1.00, 1.00] x1 | - | 1.00 [1.00, 1.00] x1 |
| clang18v3-fast | k02_add_fwd | yes (w8) | yes (w8) | 0 -> 1 | 0.95 [0.95, 0.95] x3 | 1.11 [1.10, 1.12] x1 | 0.95 [0.95, 0.95] x1 | - | 1.09 [1.09, 1.10] x1 |
| clang18v3-fast | k03_stencil | yes (w8) | yes (w8) | 0 -> 1 | 1.01 [0.99, 1.01] x3 | 1.00 [0.99, 1.01] x1 | 1.01 [0.98, 1.04] x1 | - | 1.01 [1.01, 1.02] x1 |
| clang18v3-fast | k04_rev | yes (w8) | no | 0 -> 1 | 7.35 [7.34, 7.36] x3 | 9.65 [9.53, 9.75] x1 | 4.88 [4.87, 4.91] x1 | - | 5.62 [5.57, 5.66] x1 |
| clang18v3-fast | k05_stride2 | yes (w8) | no | 0 -> 1 | 7.09 [7.04, 7.11] x3 | 5.86 [5.81, 5.93] x1 | 7.49 [7.46, 7.50] x1 | - | 5.75 [5.75, 5.77] x1 |
| clang18v3-fast | k06_gather | no | no | 0 -> 1 | 1.78 [1.77, 1.79] x3 | 1.79 [1.77, 1.80] x1 | 1.57 [1.57, 1.57] x1 | - | 2.16 [2.14, 2.17] x1 |
| clang18v3-fast | k07_hist | no | no | 0 -> 1 | 1.12 [1.10, 1.33] x3 | 1.27 [1.25, 1.30] x1 | 1.18 [1.14, 1.55] x1 | - | 1.32 [1.26, 1.51] x1 |
| clang18v3-fast | k08_matmul | yes (w8) | yes (w8) | 0 -> 1 | 2.33 [2.21, 2.38] x3 | 1.72 [1.70, 1.75] x1 | 2.16 [2.15, 2.16] x1 | - | 1.49 [1.48, 1.49] x1 |
| gcc14-O2-assert | k01_sum_fwd | no | no | 0 -> 0 | 1.00 [0.99, 1.03] x3 | - | 1.00 [0.99, 1.00] x3 | 1.00 [0.99, 1.02] x1 | - |
| gcc14-O2-assert | k02_add_fwd | no | no | 0 -> 2 | 2.24 [2.23, 2.26] x3 | - | 1.63 [1.60, 1.64] x3 | 2.24 [2.14, 2.33] x1 | - |
| gcc14-O2-assert | k03_stencil | no | no | 0 -> 1 | 1.01 [1.00, 1.01] x3 | - | 1.21 [1.17, 1.22] x3 | 1.12 [1.11, 1.13] x1 | - |
| gcc14-O2-assert | k04_rev | no | no | 0 -> 1 | 1.98 [1.97, 1.99] x3 | - | 1.98 [1.97, 1.99] x3 | 1.16 [1.11, 1.20] x1 | - |
| gcc14-O2-assert | k05_stride2 | no | no | 0 -> 1 | 1.54 [1.54, 1.55] x3 | - | 1.53 [1.53, 1.54] x3 | 1.66 [1.62, 1.70] x1 | - |
| gcc14-O2-assert | k06_gather | no | no | 0 -> 2 | 1.71 [1.70, 1.73] x3 | - | 1.67 [1.66, 1.67] x3 | 2.36 [2.33, 2.40] x1 | - |
| gcc14-O2-assert | k07_hist | no | no | 0 -> 1 | 1.25 [1.19, 1.30] x3 | - | 1.24 [0.97, 1.30] x3 | 1.31 [1.22, 1.38] x1 | - |
| gcc14-O2-assert | k08_matmul | no | no | 0 -> 2 | 1.68 [1.68, 1.70] x3 | - | 1.67 [1.67, 1.68] x3 | 1.89 [1.85, 1.93] x1 | - |
| gcc14-O3-assert | k01_sum_fwd | yes (16 B) | yes (16 B) | 0 -> 0 | 1.00 [0.98, 1.03] x3 | - | 1.00 [1.00, 1.00] x3 | 1.00 [1.00, 1.00] x1 | - |
| gcc14-O3-assert | k02_add_fwd | yes (16 B) | no | 0 -> 2 | 8.51 [8.47, 8.62] x3 | - | 8.41 [8.36, 8.48] x3 | 7.01 [6.98, 7.43] x1 | - |
| gcc14-O3-assert | k03_stencil | yes (16 B) | no | 0 -> 1 | 3.88 [3.86, 4.49] x3 | - | 3.97 [3.86, 4.07] x3 | 3.83 [3.82, 3.83] x1 | - |
| gcc14-O3-assert | k04_rev | yes (16 B) | no | 0 -> 1 | 3.54 [3.49, 3.58] x3 | - | 4.45 [4.34, 4.52] x3 | 3.85 [3.79, 3.86] x1 | - |
| gcc14-O3-assert | k05_stride2 | yes (16 B) | no | 0 -> 1 | 3.87 [3.87, 3.88] x3 | - | 5.29 [5.27, 5.29] x3 | 3.84 [3.84, 3.85] x1 | - |
| gcc14-O3-assert | k06_gather | no | no | 0 -> 2 | 1.70 [1.70, 1.71] x3 | - | 1.66 [1.66, 1.67] x3 | 2.38 [2.37, 2.38] x1 | - |
| gcc14-O3-assert | k07_hist | no | no | 0 -> 1 | 1.26 [1.05, 1.38] x3 | - | 1.24 [1.06, 1.35] x3 | 1.26 [1.14, 1.37] x1 | - |
| gcc14-O3-assert | k08_matmul | yes (16 B) | no | 0 -> 2 | 4.30 [4.28, 4.61] x3 | - | 4.46 [4.45, 4.46] x3 | 4.71 [4.70, 4.75] x1 | - |
| clang20-fast | k01_sum_fwd | yes (w2) | yes (w2) | 0 -> 0 | 1.00 [0.99, 1.00] x3 | 1.00 [0.99, 1.03] x1 | 1.00 [1.00, 1.00] x2 | 1.00 [1.00, 1.00] x1 | - |
| clang20-fast | k02_add_fwd | yes (w4) | yes (w4) | 0 -> 1 | 1.01 [1.00, 1.01] x3 | 1.01 [1.00, 1.03] x1 | 1.00 [1.00, 1.01] x2 | 1.03 [1.03, 1.03] x1 | - |
| clang20-fast | k03_stencil | yes (w4) | yes (w4) | 0 -> 1 | 1.01 [0.99, 1.02] x3 | 1.01 [0.98, 1.04] x1 | 1.01 [0.98, 1.05] x2 | 1.01 [0.94, 1.11] x1 | - |
| clang20-fast | k04_rev | yes (w4) | no | 0 -> 1 | 8.01 [8.00, 8.02] x3 | 5.38 [5.35, 5.41] x1 | 5.44 [5.38, 5.50] x2 | 6.53 [6.52, 6.56] x1 | - |
| clang20-fast | k05_stride2 | yes (w4) | no | 0 -> 1 | 5.07 [5.05, 5.08] x3 | 2.86 [2.82, 2.90] x1 | 5.08 [5.07, 5.10] x2 | 4.96 [4.95, 4.97] x1 | - |
| clang20-fast | k06_gather | no | no | 0 -> 1 | 1.84 [1.83, 1.84] x3 | 1.73 [1.72, 1.73] x1 | 1.58 [1.58, 1.59] x2 | 2.16 [2.07, 2.23] x1 | - |
| clang20-fast | k07_hist | no | no | 0 -> 1 | 1.09 [0.98, 1.22] x3 | 1.24 [1.23, 1.25] x1 | 1.12 [1.04, 1.27] x2 | 1.25 [1.17, 1.30] x1 | - |
| clang20-fast | k08_matmul | yes (w4) | yes (w4) | 0 -> 1 | 1.65 [1.64, 1.68] x3 | 1.71 [1.69, 1.75] x1 | 1.65 [1.65, 1.66] x2 | 1.49 [1.49, 1.50] x1 | - |

### Aligned hardened/unhardened ratio, L2 size

Read each cell the same way as in the L1 table.

| variant | kernel | vectorized unhardened | vectorized hardened | traps | EPYC 7763 | EPYC 9V45 | EPYC 9V74 | Xeon 6973P-C | Xeon Platinum 8573C |
|---|---|---|---|---|---|---|---|---|---|
| clang18-fast | k01_sum_fwd | yes (w2) | yes (w2) | 0 -> 0 | 1.00 [1.00, 1.01] x6 | 1.01 [1.00, 1.04] x1 | 1.00 [1.00, 1.01] x4 | 1.00 [1.00, 1.00] x1 | 1.00 [1.00, 1.00] x1 |
| clang18-fast | k02_add_fwd | yes (w4) | yes (w4) | 0 -> 1 | 1.00 [0.97, 1.04] x6 | 0.90 [0.90, 0.91] x1 | 1.00 [0.97, 1.03] x4 | 0.97 [0.97, 0.97] x1 | 0.97 [0.97, 0.97] x1 |
| clang18-fast | k03_stencil | yes (w4) | yes (w4) | 0 -> 1 | 1.00 [0.97, 1.01] x6 | 1.00 [1.00, 1.01] x1 | 1.00 [0.98, 1.02] x4 | 1.02 [0.99, 1.03] x1 | 1.00 [0.98, 1.00] x1 |
| clang18-fast | k04_rev | yes (w4) | no | 0 -> 1 | 7.81 [7.60, 7.98] x6 | 5.80 [5.73, 5.94] x1 | 5.85 [5.59, 5.89] x4 | 3.58 [3.51, 3.83] x1 | 4.11 [3.84, 4.13] x1 |
| clang18-fast | k05_stride2 | yes (w4) | no | 0 -> 1 | 5.04 [4.82, 5.10] x6 | 3.06 [3.00, 3.09] x1 | 5.12 [4.97, 5.29] x4 | 4.10 [4.05, 4.11] x1 | 3.78 [3.76, 3.82] x1 |
| clang18-fast | k06_gather | no | no | 0 -> 1 | 1.18 [1.17, 1.19] x6 | 1.30 [1.29, 1.31] x1 | 1.01 [1.00, 1.01] x4 | 1.03 [1.03, 1.03] x1 | 1.04 [1.04, 1.05] x1 |
| clang18-fast | k07_hist | no | no | 0 -> 1 | 1.11 [1.07, 1.18] x6 | 1.21 [1.18, 1.24] x1 | 1.12 [1.09, 1.16] x4 | 1.15 [1.12, 1.17] x1 | 1.07 [1.05, 1.10] x1 |
| clang18-fast | k08_matmul | yes (w4) | no | 0 -> 1 | 3.80 [3.80, 3.82] x6 | 4.08 [4.04, 4.10] x1 | 4.70 [4.60, 4.78] x4 | 3.39 [3.31, 3.40] x1 | 3.49 [3.48, 3.50] x1 |
| clang18-extensive | k01_sum_fwd | yes (w2) | yes (w2) | 0 -> 0 | 1.00 [1.00, 1.01] x3 | 1.00 [0.99, 1.00] x1 | 1.00 [1.00, 1.00] x1 | - | 1.00 [1.00, 1.00] x1 |
| clang18-extensive | k02_add_fwd | yes (w4) | yes (w4) | 0 -> 1 | 1.00 [0.99, 1.03] x3 | 0.90 [0.89, 0.91] x1 | 1.00 [0.99, 1.01] x1 | - | 0.97 [0.97, 0.97] x1 |
| clang18-extensive | k03_stencil | yes (w4) | yes (w4) | 0 -> 1 | 1.00 [0.99, 1.02] x3 | 1.00 [1.00, 1.01] x1 | 0.98 [0.97, 0.99] x1 | - | 0.99 [0.96, 1.02] x1 |
| clang18-extensive | k04_rev | yes (w4) | no | 0 -> 1 | 7.73 [7.58, 7.85] x3 | 5.84 [5.78, 5.90] x1 | 5.87 [5.85, 5.88] x1 | - | 4.15 [4.11, 4.20] x1 |
| clang18-extensive | k05_stride2 | yes (w4) | no | 0 -> 1 | 5.02 [4.82, 5.12] x3 | 3.01 [2.98, 3.04] x1 | 5.27 [5.15, 5.29] x1 | - | 3.79 [3.76, 3.82] x1 |
| clang18-extensive | k06_gather | no | no | 0 -> 1 | 1.18 [1.17, 1.20] x3 | 1.31 [1.30, 1.33] x1 | 1.01 [1.00, 1.01] x1 | - | 1.05 [1.03, 1.06] x1 |
| clang18-extensive | k07_hist | no | no | 0 -> 1 | 1.08 [1.06, 1.15] x3 | 1.22 [1.19, 1.24] x1 | 1.10 [1.09, 1.12] x1 | - | 1.09 [1.06, 1.13] x1 |
| clang18-extensive | k08_matmul | yes (w4) | no | 0 -> 1 | 3.81 [3.80, 3.82] x3 | 4.08 [4.00, 4.10] x1 | 4.76 [4.75, 4.78] x1 | - | 3.48 [3.48, 3.49] x1 |
| clang18-debug | k01_sum_fwd | yes (w2) | yes (w2) | 0 -> 0 | 1.00 [1.00, 1.00] x3 | 1.00 [1.00, 1.01] x1 | 1.00 [1.00, 1.00] x1 | - | 1.00 [1.00, 1.00] x1 |
| clang18-debug | k02_add_fwd | yes (w4) | yes (w4) | 0 -> 2 | 1.00 [0.97, 1.04] x3 | 0.90 [0.89, 0.92] x1 | 1.02 [0.98, 1.03] x1 | - | 0.97 [0.97, 0.97] x1 |
| clang18-debug | k03_stencil | yes (w4) | yes (w4) | 0 -> 1 | 1.00 [0.99, 1.01] x3 | 1.00 [0.99, 1.01] x1 | 0.99 [0.97, 1.00] x1 | - | 1.02 [1.00, 1.04] x1 |
| clang18-debug | k04_rev | yes (w4) | no | 0 -> 1 | 7.77 [7.64, 7.86] x3 | 5.82 [5.75, 5.91] x1 | 5.87 [5.85, 5.88] x1 | - | 4.13 [4.09, 4.17] x1 |
| clang18-debug | k05_stride2 | yes (w4) | no | 0 -> 2 | 5.07 [4.80, 5.13] x3 | 2.95 [2.92, 2.98] x1 | 5.29 [5.24, 5.29] x1 | - | 3.83 [3.75, 3.86] x1 |
| clang18-debug | k06_gather | no | no | 0 -> 2 | 1.18 [1.17, 1.19] x3 | 1.30 [1.29, 1.33] x1 | 1.00 [1.00, 1.01] x1 | - | 1.04 [1.04, 1.05] x1 |
| clang18-debug | k07_hist | no | no | 0 -> 1 | 1.11 [1.07, 1.14] x3 | 1.22 [1.21, 1.24] x1 | 1.13 [1.10, 1.15] x1 | - | 1.07 [1.05, 1.09] x1 |
| clang18-debug | k08_matmul | yes (w4) | no | 0 -> 3 | 3.80 [3.79, 3.81] x3 | 4.10 [4.04, 4.14] x1 | 4.76 [4.74, 4.78] x1 | - | 3.48 [3.47, 3.49] x1 |
| clang18v3-fast | k01_sum_fwd | yes (w4) | yes (w4) | 0 -> 0 | 1.00 [0.93, 1.05] x3 | 1.00 [0.99, 1.01] x1 | 1.00 [1.00, 1.00] x1 | - | 1.00 [1.00, 1.00] x1 |
| clang18v3-fast | k02_add_fwd | yes (w8) | yes (w8) | 0 -> 1 | 1.00 [0.97, 1.02] x3 | 1.00 [0.99, 1.02] x1 | 1.02 [1.00, 1.02] x1 | - | 1.01 [1.00, 1.01] x1 |
| clang18v3-fast | k03_stencil | yes (w8) | yes (w8) | 0 -> 1 | 1.00 [0.98, 1.02] x3 | 1.00 [0.99, 1.00] x1 | 1.00 [1.00, 1.00] x1 | - | 1.00 [1.00, 1.00] x1 |
| clang18v3-fast | k04_rev | yes (w8) | no | 0 -> 1 | 6.38 [6.09, 6.40] x3 | 4.56 [4.45, 4.63] x1 | 4.82 [4.81, 4.82] x1 | - | 1.57 [1.56, 1.57] x1 |
| clang18v3-fast | k05_stride2 | yes (w8) | no | 0 -> 1 | 4.35 [4.27, 4.42] x3 | 5.85 [5.77, 6.04] x1 | 4.66 [4.45, 4.81] x1 | - | 3.20 [3.17, 3.25] x1 |
| clang18v3-fast | k06_gather | no | no | 0 -> 1 | 1.19 [1.18, 1.20] x3 | 1.29 [1.29, 1.31] x1 | 1.01 [1.01, 1.01] x1 | - | 1.05 [1.04, 1.05] x1 |
| clang18v3-fast | k07_hist | no | no | 0 -> 1 | 1.14 [1.09, 1.17] x3 | 1.26 [1.24, 1.27] x1 | 1.17 [1.15, 1.19] x1 | - | 1.10 [1.08, 1.13] x1 |
| clang18v3-fast | k08_matmul | yes (w8) | yes (w8) | 0 -> 1 | 1.01 [1.01, 1.02] x3 | 1.02 [1.01, 1.04] x1 | 1.08 [1.08, 1.09] x1 | - | 1.20 [1.20, 1.21] x1 |
| gcc14-O2-assert | k01_sum_fwd | no | no | 0 -> 0 | 1.00 [1.00, 1.01] x3 | - | 1.00 [1.00, 1.00] x3 | 1.00 [1.00, 1.01] x1 | - |
| gcc14-O2-assert | k02_add_fwd | no | no | 0 -> 2 | 2.23 [2.22, 2.24] x3 | - | 1.65 [1.65, 1.66] x3 | 1.89 [1.88, 1.90] x1 | - |
| gcc14-O2-assert | k03_stencil | no | no | 0 -> 1 | 1.18 [1.17, 1.19] x3 | - | 1.27 [1.25, 1.28] x3 | 1.01 [0.99, 1.21] x1 | - |
| gcc14-O2-assert | k04_rev | no | no | 0 -> 1 | 1.99 [1.92, 2.00] x3 | - | 2.00 [1.99, 2.00] x3 | 1.14 [1.13, 1.20] x1 | - |
| gcc14-O2-assert | k05_stride2 | no | no | 0 -> 1 | 1.47 [1.46, 1.48] x3 | - | 1.46 [1.46, 1.47] x3 | 1.19 [1.18, 1.22] x1 | - |
| gcc14-O2-assert | k06_gather | no | no | 0 -> 2 | 1.47 [1.46, 1.48] x3 | - | 1.25 [1.24, 1.25] x3 | 1.32 [1.26, 1.33] x1 | - |
| gcc14-O2-assert | k07_hist | no | no | 0 -> 1 | 1.19 [1.13, 1.26] x3 | - | 1.18 [1.14, 1.22] x3 | 1.28 [1.26, 1.30] x1 | - |
| gcc14-O2-assert | k08_matmul | no | no | 0 -> 2 | 1.67 [1.66, 1.67] x3 | - | 1.68 [1.68, 1.69] x3 | 2.19 [2.14, 2.24] x1 | - |
| gcc14-O3-assert | k01_sum_fwd | yes (16 B) | yes (16 B) | 0 -> 0 | 1.00 [1.00, 1.00] x3 | - | 1.00 [1.00, 1.00] x3 | 1.00 [1.00, 1.01] x1 | - |
| gcc14-O3-assert | k02_add_fwd | yes (16 B) | no | 0 -> 2 | 6.43 [6.37, 6.49] x3 | - | 5.86 [5.64, 5.97] x3 | 4.87 [4.70, 4.98] x1 | - |
| gcc14-O3-assert | k03_stencil | yes (16 B) | no | 0 -> 1 | 4.03 [3.98, 4.08] x3 | - | 4.22 [4.15, 4.36] x3 | 3.12 [2.85, 3.19] x1 | - |
| gcc14-O3-assert | k04_rev | yes (16 B) | no | 0 -> 1 | 3.55 [3.51, 3.56] x3 | - | 4.28 [4.21, 4.35] x3 | 3.55 [3.54, 3.61] x1 | - |
| gcc14-O3-assert | k05_stride2 | yes (16 B) | no | 0 -> 1 | 3.96 [3.93, 3.98] x3 | - | 5.02 [4.92, 5.12] x3 | 3.89 [3.87, 3.96] x1 | - |
| gcc14-O3-assert | k06_gather | no | no | 0 -> 2 | 1.47 [1.46, 1.48] x3 | - | 1.25 [1.24, 1.26] x3 | 1.31 [1.31, 1.31] x1 | - |
| gcc14-O3-assert | k07_hist | no | no | 0 -> 1 | 1.19 [1.14, 1.26] x3 | - | 1.18 [1.15, 1.22] x3 | 1.27 [1.25, 1.28] x1 | - |
| gcc14-O3-assert | k08_matmul | yes (16 B) | no | 0 -> 2 | 4.90 [4.88, 4.94] x3 | - | 4.75 [4.72, 4.82] x3 | 4.22 [4.21, 4.24] x1 | - |
| clang20-fast | k01_sum_fwd | yes (w2) | yes (w2) | 0 -> 0 | 1.00 [1.00, 1.01] x3 | 1.00 [0.99, 1.02] x1 | 1.00 [1.00, 1.00] x2 | 1.00 [0.99, 1.00] x1 | - |
| clang20-fast | k02_add_fwd | yes (w4) | yes (w4) | 0 -> 1 | 1.00 [0.97, 1.02] x3 | 1.00 [0.98, 1.01] x1 | 1.00 [0.99, 1.01] x2 | 1.00 [0.90, 1.10] x1 | - |
| clang20-fast | k03_stencil | yes (w4) | yes (w4) | 0 -> 1 | 1.00 [0.98, 1.01] x3 | 0.99 [0.98, 1.02] x1 | 1.00 [1.00, 1.00] x2 | 1.00 [0.98, 1.03] x1 | - |
| clang20-fast | k04_rev | yes (w4) | no | 0 -> 1 | 7.85 [7.76, 7.89] x3 | 5.85 [5.80, 5.88] x1 | 5.81 [5.71, 5.87] x2 | 3.71 [3.70, 3.74] x1 | - |
| clang20-fast | k05_stride2 | yes (w4) | no | 0 -> 1 | 5.10 [4.98, 5.13] x3 | 3.07 [3.02, 3.10] x1 | 5.16 [5.06, 5.29] x2 | 4.07 [3.94, 4.16] x1 | - |
| clang20-fast | k06_gather | no | no | 0 -> 1 | 1.19 [1.18, 1.19] x3 | 1.30 [1.29, 1.31] x1 | 1.00 [1.00, 1.01] x2 | 1.03 [1.00, 1.06] x1 | - |
| clang20-fast | k07_hist | no | no | 0 -> 1 | 1.10 [1.06, 1.14] x3 | 1.22 [1.20, 1.24] x1 | 1.12 [1.09, 1.16] x2 | 1.13 [1.11, 1.18] x1 | - |
| clang20-fast | k08_matmul | yes (w4) | yes (w4) | 0 -> 1 | 1.15 [1.15, 1.15] x3 | 1.17 [1.12, 1.20] x1 | 1.10 [1.10, 1.11] x2 | 1.15 [1.14, 1.15] x1 | - |

**Notes on the columns:**
- Width: "w4" is clang's vectorization factor; "16 B" is GCC's vector size, since GCC does not print the factor.
- Every number above is the aligned pair. The as-compiled pair is in every `siblings.json` (`cells[].as_compiled`). The per-job A/A and layout A/A are in `summarize.py`'s output and in `siblings/summary.json`.

## Does the finding generalize?

**What the table shows: partly.**

**What carries over:**
- **The mechanism.** On every toolchain where a check stops a loop from vectorizing, that loop costs about 2.9x to 9.7x at L1. A vectorized loop whose check stays out of the vector body costs about 1.00x on the AMD models (up to 1.11x with `-march=x86-64-v3`, one EPYC 9V45 job); on the Intel models drawn the forward add still cost 1.06x to 1.20x at L1 (one job each).
- **The class lines under libc++.** They are the same in all three hardening modes on clang 18. EXTENSIVE and DEBUG lose the same three loops as FAST, at ratios within a few percent of FAST on each CPU model; the exception is the noisy k07_hist, whose intervals are wide in every variant. DEBUG adds traps (k02 2, k05 2, k06 2, k08 3) but no measurable time over FAST on these kernels.
- **The same lines on clang 20 with libc++ 20:**
  - forward loops: about 1.00x;
  - reverse and stride-2: lost, at the same sizes as clang 18 (5.4x to 8.0x and 2.9x to 5.1x at L1).

**What does not carry over:**
- **Matrix multiply is not always lost.**
  - clang 20 keeps it vectorized under FAST, at 1.49x to 1.71x at L1 and 1.10x to 1.17x at L2. The reference costs 3.1x to 4.1x.
  - clang 18 with `-march=x86-64-v3` keeps it vectorized at width 8 with interleave 1 instead of 4. It costs 1.49x to 2.33x at L1 and 1.01x to 1.20x at L2.
- **AVX2 changes the size of the gap, not its direction.** Under x86-64-v3:
  - reverse costs 4.9x to 9.7x at L1, against 5.4x to 8.0x at SSE2;
  - stride-2 costs 5.8x to 7.5x, against 2.9x to 5.1x;
  - the change differs per CPU model, and at L2 on the Xeon Platinum 8573C reverse falls to 1.57x.
- **GCC 14 with libstdc++ `_GLIBCXX_ASSERTIONS` breaks the forward-loop rule.**
  - At `-O3`, the forward loops k02 and k03 lose vectorization, like reverse, stride-2 and matmul. They cost 7.0x to 8.5x (k02) and 3.8x to 4.0x (k03) at L1.
  - At `-O2`, GCC vectorizes none of these loops in either build, yet assertions still cost 1.6x to 2.2x on the forward k02, 1.1x to 2.0x on reverse and 1.7x to 2.2x on matmul (L1 and L2). In k02, whose assembly diff was read, the hardened loop reloads `c`'s pointers on every iteration.
  - The only loop that pays nothing under GCC is k01_sum_fwd. Its check is removed entirely (0 traps), as under clang.

**In one line:** "forward loops pay about nothing" is a property of clang with libc++ on these kernels on the AMD models (with the one AVX2 exception above), not of bounds checking in general.

## Surprises worth a second look

- **The forward kernel k02_add_fwd at L1 is not about 1.00x on Intel**, even with loops aligned. Under clang18-fast it is 1.20x on the Xeon 6973P-C (1 job) and 1.06x on the Xeon Platinum 8573C (1 job). On every AMD model it is 0.83x to 0.84x. clang 20 shows 1.03x on the Xeon 6973P-C. These are single jobs on CPU models the main runs have not drawn (6973P-C) or have drawn rarely.
- **EPYC 9V45 makes stride-2 cheap:** 2.9x to 3.1x under every clang variant, against about 5x on the other CPU models.
- **GCC's `-O2` vectorizes none of the kernel loops** (`unsupported data-type`, with the "very cheap" cost model GCC uses at `-O2`). A GCC user at `-O2` therefore never sees the vectorization loss. But the scalar checks are not free there, unlike under clang.

## What this does not show

- **Not arm64**, not AVX-512 (`-march=x86-64-v4`), not MSVC, not clang 19 or 21. apt had no clang 21; clang 19 was skipped as older than 20.
- **Not libstdc++ under clang**, not `_GLIBCXX_DEBUG`, not libc++ EXTENSIVE or DEBUG on clang 20 or at x86-64-v3, not GCC with `-march=x86-64-v3`, not GCC `-O2 -fvect-cost-model=dynamic`.
- **DEBUG mode's extra checks are mostly beside the point here.** These kernels only call `operator[]` and `size()`, so iterator-heavy code may pay more under EXTENSIVE or DEBUG than these 8 loops do.
- **No RAM sizes, no real programs, no Cachegrind, no `-fno-vectorize` control.** RAM cells did not reproduce on the main page. The json and fmt programs were not rebuilt with the sibling toolchains.
- **Uneven CPU coverage.**
  - Each part runs on whatever CPU GitHub assigns.
  - Several cells rest on one job (the "x1" entries), and some variant x CPU pairs are empty.
  - GCC never ran on an EPYC 9V45 that passed the A/A, nor on the Xeon Platinum 8573C.
  - clang 20 never ran on the Xeon Platinum 8573C.
  - EXTENSIVE, DEBUG and x86-64-v3 never ran on the Xeon 6973P-C.
- **Within-job intervals understate run-to-run spread** (see the main README). The brackets above pool several jobs but still come from 2 runs on one day.
- **Nothing about Google's services, the 0.30% figure, or whole programs.** These are 8 synthetic loops.
