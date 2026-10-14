# Day-one test results

Run: 38116223923 (Sun Oct 11 2026, 05:52 to 05:56 UTC), commit `5d22102`. This is the first and only run of the day-one test as written; a separate rerun is reported elsewhere.
Thresholds: `dayone/criteria.json`, committed in `176be71` before this run, not changed since.
Raw data, remarks and assembly: `dayone/results/run-38116223923/` (`raw.json` has every sample; `dayone.json` is the evaluation; `asm/` has each kernel's function for NONE, FAST and NOVEC and the NONE-to-FAST diff).
Recompute on Windows, no compiler needed: `python dayone/evaluate.py dayone/results/run-38116223923/raw.json <out.json>`.

Runner: GitHub Actions `ubuntu-24.04`, AMD EPYC 9V45, 2 vCPUs (a private-repo runner), L1d 48 KiB, L2 1 MiB, L3 32 MiB. Toolchain: Ubuntu clang 18.1.3, `libc++-18-dev 1:18.1.3-1ubuntu1`, `-O2 -std=c++20 -stdlib=libc++`, baseline x86-64 (SSE2).

## Verdict as written: NO-GO (C2 missed by one cell, by 0.015 percentage points)

| Criterion | Threshold (from criteria.json) | Measured | Met |
|---|---|---|---|
| C1 A/A floor | every A/A pair byte-identical with 20 reps per side; branch: at most 0.3 % = can test 0.30 %, at least 1 % = sanity check | all 4 pairs byte-identical, 20 + 20 reps each. Largest half-width **1.14 %** (json_parse, whole program). Kernel pairs (k02_add_fwd): 0.45 % L1, 0.44 % L2, 0.31 % RAM. Branch: **sanity_check** | yes |
| C2 loop shape | k04_rev and k05_stride2 at L1 and L2: CI low at least 1.5. k01, k02, k03 at L1 and L2: CI high below 1.02. Checksums equal | reverse 5.54x [5.49, 5.58] L1, 5.81x [5.76, 5.83] L2; stride-2 2.81x [2.81, 2.83] L1, 2.90x [2.88, 2.92] L2. Forward: five of six cells pass; **k03_stencil.L1 is 1.002x [0.969, 1.0201]**, CI high 1.0201 is not below 1.02. All checksums equal | **no** |
| C3 toolchain | json_parse and a second program build NONE and FAST, run, equal checksums, traps recorded | nlohmann/json v3.11.3: builds, runs, checksums equal, traps 0 NONE / 25 FAST. fmt 11.0.2 (first in the SPEC order, built first try): builds, runs, checksums equal, traps 0 NONE / 7 FAST | yes |
| GO rule | C1, C2 and C3 all met | C2 not met | **NO-GO** |

SPEC section 1 verdict (computed by `dayone/evaluate.py`): **INCONCLUSIVE**, reason "mixed picture: neither the MAP nor the HOLDS_EVERYWHERE rule fired". MAP failed on the same k03_stencil.L1 upper bound; HOLDS_EVERYWHERE failed because reverse and stride-2 pay 2.8x to 5.8x. All controls passed (A/A identical; kernel A/A floor 0.45 %, below the 2 % forward limit; the -fno-vectorize positive was seen in all 10 in-cache cells).

What the plan says to do on a C2 NO-GO ("holds everywhere we looked") does not describe this data: the loop-shape effect is large and clean. The miss is the forward side's upper bound in one L1 cell. See problems below; whether to continue was decided separately from this record.

## Every cell (ratio = median FAST / median NONE, and NOVEC / NONE; 95 % bootstrap interval; 20 + 20 reps, ABBA)

| cell | working set (bytes) | NONE ns/call | FAST ns/call | FAST/NONE | NOVEC/NONE |
|---|---|---|---|---|---|
| k01_sum_fwd.L1 | 24576 | 693.5 | 693.0 | 0.999 [0.998, 1.002] | 1.087 [1.076, 1.098] |
| k01_sum_fwd.L2 | 524288 | 14601.9 | 14603.0 | 1.000 [0.999, 1.001] | 1.090 [1.087, 1.094] |
| k01_sum_fwd.RAM | 134217728 | 4326170.1 | 4343924.2 | 1.004 [0.999, 1.011] | 1.051 [1.047, 1.057] |
| k02_add_fwd.L1 | 24576 | 148.2 | 145.8 | 0.983 [0.974, 0.997] | 2.585 [2.529, 2.666] |
| k02_add_fwd.L2 | 524280 | 3053.2 | 2791.8 | 0.914 [0.911, 0.920] | 2.609 [2.603, 2.612] |
| k02_add_fwd.RAM | 134217720 | 2626213.8 | 2670967.1 | 1.017 [1.010, 1.020] | 1.150 [1.141, 1.157] |
| k03_stencil.L1 | 24576 | 383.5 | 384.3 | 1.002 [0.969, 1.020] | 2.333 [2.317, 2.342] |
| k03_stencil.L2 | 524288 | 7754.0 | 7775.2 | 1.003 [1.000, 1.008] | 2.847 [2.824, 2.879] |
| k03_stencil.RAM | 134217728 | 3111947.5 | 3021262.5 | 0.971 [0.952, 0.993] | 1.901 [1.871, 1.936] |
| k04_rev.L1 | 24576 | 137.0 | 758.8 | 5.540 [5.493, 5.579] | 2.927 [2.915, 2.934] |
| k04_rev.L2 | 524288 | 2768.7 | 16072.0 | 5.805 [5.759, 5.834] | 3.278 [3.258, 3.303] |
| k04_rev.RAM | 134217728 | 2778846.3 | 4701226.2 | 1.692 [1.641, 1.729] | 1.176 [1.166, 1.182] |
| k05_stride2.L1 | 24576 | 234.9 | 661.1 | 2.814 [2.810, 2.829] | 1.525 [1.521, 1.530] |
| k05_stride2.L2 | 524280 | 4880.0 | 14172.9 | 2.904 [2.884, 2.919] | 1.665 [1.658, 1.672] |
| k05_stride2.RAM | 134217720 | 2978548.6 | 4024144.9 | 1.351 [1.348, 1.360] | 1.129 [1.121, 1.135] |

Real programs: json_parse (twitter.json, 631,515 bytes) FAST/NONE 0.993 [0.986, 1.003], A/A half-width 1.14 %, so "consistent with at most +0.3 %" against a 1.14 % floor. fmt_format FAST/NONE 0.987 [0.949, 0.993] (FAST faster; unexplained, see problems).

## The machine code (the proof that the check is there)
From clang's own remarks (`-Rpass=loop-vectorize`, files `remarks.<kernel>.<mode>.txt`):
- k01_sum_fwd: vectorized in NONE and FAST, width 2 (the int64 accumulator). The NONE and FAST functions are identical (empty diff, 0 traps): the check is proven redundant and removed.
- k02_add_fwd, k03_stencil: vectorized in NONE and FAST, width 4; interleave 2 is stated here for both builds, but for k02 FAST clang picks interleave 1 (corrected in `investigate/FINDINGS.md`). FAST adds one `ud2` and changes the loop's set-up (the trip count becomes the minimum of the array sizes); the SIMD body stays.
- k04_rev, k05_stride2: vectorized width 4 in NONE; in FAST "loop not vectorized: could not determine number of loop iterations". The FAST function is a one-element scalar loop with a compare and a branch to `ud2` each iteration (`asm/k04_rev.none-vs-fast.diff`: the `movdqu`/`paddd` body is gone, `cmp %rsi,%rdi; jae` and `ud2` are added).
- FAST costs the reverse loop more than switching vectorization off does (5.5x against 2.9x for NOVEC): the NOVEC build is still unrolled four times and has no per-element check; FAST is neither.
- Trap counts in `kern_<id>` (ud2 plus calls to `__libcpp_verbose_abort`): NONE 0 for all; FAST 0 (k01), 1 (k02, k03, k04, k05). The libc++-18 FAST handler compiles to `ud2`; no verbose-abort calls were found.

## Downloads (all on the runner, none on the laptop)
| what | source | bytes | sha256 |
|---|---|---|---|
| clang-18, libc++-18-dev, libc++abi-18-dev | Ubuntu noble apt | (apt) | (apt) |
| nlohmann/json v3.11.3 json.hpp | https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp | 919975 | 9bea4c8066ef4a1c206b2be5a36302f8926f7fdc6087af5d20b417d0cf103ea6 |
| twitter.json | https://raw.githubusercontent.com/simdjson/simdjson/v3.10.1/jsonexamples/twitter.json | 631515 | 30721e496a8d73cfc50658923c34eb2c0fbe15ee6835005e43ee624d8dedf200 |
| fmt 11.0.2 source | https://github.com/fmtlib/fmt/archive/refs/tags/11.0.2.tar.gz | 700956 | 6cb1e6d37bdcb756dbbe59be438790db409cdb4868c66e888d5df9f13f7c027f |
| pugixml 1.14 (fallback, not used: fmt built) | https://github.com/zeux/pugixml/releases/download/v1.14/pugixml-1.14.tar.gz | 391977 | 2f10e276870c64b1db6809050a75e11a897a8d7456c4be5c6b2e35a11168a015 |

## Problems
1. **C2 fails on one cell by a hair, and it is reported as written.** k03_stencil.L1 has a point estimate of 1.002x but an upper bound of 1.0201 against "below 1.02". Its samples have a fast mode near 377 ns and occasional spikes of 450 to 476 ns in BOTH builds (3 or so per side), which widens the bootstrap interval. Objection to the threshold: an upper-bound test on a cell this small (about 380 ns per call) fails whenever the runner throws a few spikes, whatever the true cost is; a test on the point estimate, or with more reps, would pass this cell. The threshold was not loosened and no reps were added; this run was not repeated to get a better draw, since a rerun picked because the first missed would be choosing the answer. A single rerun shows whether this cell reproduces.
2. FAST is measurably faster than NONE in some cells: k02_add_fwd.L2 0.914x [0.911, 0.920], k03_stencil.RAM 0.971x, fmt_format 0.987x. The FAST k02 function has a different loop set-up (trip count from the minimum of the sizes); a code-layout or alignment effect is likely but not shown. The byte-identical A/A cannot catch a layout effect by design, so the A/A floor understates the noise between two DIFFERENT binaries. This matters for the forward limit: a 2 % limit is tighter than the layout effects seen here (up to 9 %).
3. k01_sum_fwd is not a test of the check's cost: the check is optimized away and the two functions are identical. It is an A/A in disguise. V2 ("FAST has more traps") fails for k01 for that reason.
4. The positive control for k01 is small (1.09x) because its vectorization width is 2 (int64 accumulator on SSE2). The other kernels show 1.5x to 3.3x.
5. "Positive control seen" is an operationalization chosen for this test (CI low above 1 + the kernel A/A floor); SPEC section 1 gives no number. It is marked as such in criteria.json.
6. The runner is 2 vCPUs (private repo). Pinning used CPU 1 with the other CPU running the Python driver; no isolation from other tenants on the host.
7. The second program was fmt, which does most of its work in its own buffers; 7 traps over the whole binary. json has 25.

## What these numbers do not show
- Anything about Google's services or its 0.30 % average: these are five synthetic loops and two small programs on one shared runner.
- Whether the whole-program column can test 0.30 %: the json A/A floor is 1.14 %, so it can only say "consistent with at most X %".
- Other compilers, GCC's `_GLIBCXX_ASSERTIONS`, the libc++ extensive mode, AVX2 or arm64: baseline x86-64 SSE2, clang 18.1.3 only.
- Reproducibility across runners: one run; a rerun is the first check.
- Cachegrind instruction counts (not part of the day-one test).
- Step 4 of the day-one test (reading one assembly diff aloud) is not part of these numbers. A good diff for it: `dayone/results/run-38116223923/asm/k04_rev.none-vs-fast.diff` beside `asm/k02_add_fwd.none.s`.
