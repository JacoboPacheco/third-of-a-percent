# Claims audit 6: the newer-toolchain section (6b), the environment section (6c), and the limits they replace

Written Tue Oct 13 2026, after the text was committed. The numbers were recomputed from the raw per-job files with separate numpy code (not `harness/pool.py`, not `versions/analyze.py`, not `environment/analyze.py`): geometric mean over a CPU model's jobs of median(FAST) over median(NONE), the steal and frequency figures from the raw `samples`, and the topology from `thread_siblings_list` and the recorded driver vCPU. Scripts: `claims-audit/audit6_recompute.py` and `claims-audit/audit6_recompute_b.py` (plain numpy, run with per-user site-packages enabled; they read the raw files under `versions/results/` and `environment/results/` and the site data). Classes: SUPPORTED, OVERSTATED (true but said more strongly than the data), CONTRADICTED, STALE (was true or is now incomplete).

Result: 33 claims, 27 SUPPORTED, 3 OVERSTATED (all fixed), 0 CONTRADICTED, 3 STALE (all fixed).

## Recomputed numbers (5 version ratios and the 3 environment figures, plus extras)

| Number as printed | Own recomputation from `versions/results/38471430657/versions-*/results.json` | Verdict |
|---|---|---|
| clang 19, EPYC 7763, reverse L1, as compiled 8.0x (6 jobs) | 8.0056 (stored 8.0056; per job 7.988 to 8.030) | SUPPORTED |
| clang 21, EPYC 7763, reverse L1, 4.8x (4 jobs) | 4.8325 (stored 4.8325; per job 4.831 to 4.835) | SUPPORTED |
| clang 20, EPYC 7763, matrix multiply L1, 1.61x (5 jobs) | 1.6117 (stored 1.6117) | SUPPORTED |
| clang 21, EPYC 7763, stride-2 L2, aligned, 5.0x | 5.0072 (stored 5.0072; per job 4.876 to 5.081) | SUPPORTED |
| clang 19, EPYC 7763, forward sum L1, 1.00x | 1.0000 (stored 1.0000) | SUPPORTED |
| clang 21, EPYC 7763, matrix multiply L2, 1.15x | 1.1504 (stored 1.1504) | SUPPORTED |
| clang 19, Xeon 6973P-C, reverse L2 (one job, no pooling) | 3.6727 (stored 3.6727) | SUPPORTED |
| Environment: 0 of 6,400 timed processes with a steal tick | 6,400 processes, 0 with steal, 0 of 76,311 pinned-vCPU jiffies | SUPPORTED |
| Environment: frequency drift at most 0.57% (halves) and 0.035% (checks off vs on) | 0.570% (job j4, EPYC 9V45) and 0.035% | SUPPORTED |
| Environment: driver seen on a sibling of the pinned vCPU in 8 of 10 jobs, on the pinned vCPU in 4 | 8 and 4 (own parse of `thread_siblings_list` and per-sample driver vCPU) | SUPPORTED |
| Environment, one cell: EPYC 7763 reverse L1 over 100 and 100 processes | 7.625 (the report prints 7.625) | SUPPORTED |

## Every claim, with its class

| # | Claim (where) | Evidence | Class |
|---|---|---|---|
| 1 | 30 jobs in one run, 6 CPU models, 3 toolchains (6b) | 30 job folders; CPU models 7763, 9V45, 9V74, Xeon 6973P-C, 8370C, 8573C | SUPPORTED |
| 2 | 40 processes a side, as compiled and aligned, one pinned CPU (6b) | `none_ns` has 40 entries per cell; `taskset` in `harness/run.py` | SUPPORTED |
| 3 | Toolchains from apt.llvm.org (6b) | `versions/install.sh` repository line; the package strings carry the apt.llvm.org build suffix | SUPPORTED |
| 4 | The checks trapped on every toolchain; the build without them ran clean (6b) | `toolchain.json` probe: exit 0 and -4 on all 30 jobs' toolchains | SUPPORTED |
| 5 | Reverse and stride-2 lose SIMD on every toolchain; the rule counts them as holding on every row (6b) | remarks record identical across the 10 jobs of each toolchain; all 15 rows HOLDS in `analysis.json` | SUPPORTED |
| 6 | Reverse 3.1 to 8.0x and stride-2 2.8 to 5.3x over all rows and both sizes (6b) | own pooling per toolchain, CPU model and size: reverse 3.120 (Xeon 6973P-C, L2, clang 21, one job) to 8.006; stride-2 2.800 (EPYC 9V45, L1, clang 20, one job) to 5.274 | SUPPORTED |
| 7 | On EPYC 7763: reverse 4.7 to 8.0x, stride-2 4.9 to 5.1x (6b) | site data and own recomputation of the extremes | SUPPORTED |
| 8 | Reverse is cheaper under clang 21 (4.8x against 8.0x), still lost (6b) | rows 1 and 2 above; remarks: reverse not vectorized under FAST on 21 | SUPPORTED |
| 9 | Forward sum 0.99 to 1.00x (6b) | own pooled minimum 0.986 (Xeon 6973P-C, one job), maximum 1.002 | SUPPORTED |
| 10 | Matrix multiply keeps SIMD in both builds on every toolchain (6b) | remarks record: vectorized, width 4, in NONE and FAST, identical across the 10 jobs of each toolchain | SUPPORTED |
| 11 | Under clang 18 the checks made matrix multiply lose SIMD at 3.2 to 4.8x on the same CPU models (6b) | `results/s4-pooled/pooled.json` through `vs_clang18` (3.19 to 4.81) | SUPPORTED |
| 12 | Matrix multiply costs 1.61x (L1) and 1.15x (L2) on EPYC 7763 on every toolchain; 1.49 to 1.72x and 1.02 to 1.15x over all rows (6b) | rows 3 and 6; own pooled extremes L2 1.021 and L1 1.718 | SUPPORTED |
| 13 | Every toolchain is INCONCLUSIVE; only EPYC 7763 has 3 or more jobs on each (6, 5, 4); the others drew 1 or 2; matrix multiply misses the forward limit even aligned (6b) | `analysis.json` forms; aligned 1.615 against a limit of 1.02 | SUPPORTED |
| 14 | The forward add's 1.6x as-compiled cost under clang 18 on EPYC 7763 is not seen (1.01x) (6b, README details) | pooled 1.0087, 1.008, 1.007 at L1 on 7763 | SUPPORTED |
| 15 | One run, so the run-to-run check was not possible; Ubuntu's libc++ 18 against apt.llvm.org's 19 to 21 is a possible confound (6b) | `versions/PLAN.md`, Limits and "Not a perfect like-for-like" | SUPPORTED |
| 16 | "Why it changed is not tested here" (6b) | no experiment separates library and vectorizer | SUPPORTED |
| 17 | The timed loops in the environment run are clang 18, as compiled, 20 processes a side, 10 jobs on 3 CPU models (6c) | `environment.yml` installs clang-18; `reps_per_side` 20 in the job facts; 5, 1 and 4 jobs | SUPPORTED |
| 18 | Steal share 0% everywhere, large would be above 0.5% (6c) | row above; `thresholds` in `analysis.json` | SUPPORTED |
| 19 | Reported MHz drifted at most 0.57% between halves and 0.035% between checks off and on (6c) | rows above | SUPPORTED |
| 20 | Exclusion test left out 0 processes, no cell moved (0 of 48), and could not have moved one (6c) | `excluded` is 0 in all 48 cells; no process had steal | SUPPORTED |
| 21 | The driver was seen on a hyperthread sibling of the pinned vCPU in 8 of 10 jobs and on the pinned vCPU in 4 (6c, README) | rows above | SUPPORTED |
| 22 | No cgroup CPU limit, no cpufreq or governor files, 4 vCPUs online (0-3), one kernel (6c) | raw facts of all 10 jobs: `cgroup_cpu_max` None, `cpufreq` empty, `online` 0-3, kernel 6.17.0-1022-azure | SUPPORTED |
| 23 | The median reported MHz differs between jobs (EPYC 7763 3242 to 3244, 9V45 4316, 9V74 2871 to 3694) (6c) | own medians identical | SUPPORTED |
| 24 | The reading was one constant value in 0 of 10 jobs (6c) | `mhz.constant` false in all 10 jobs | SUPPORTED |
| 25 | A guest may hide real frequency changes; the view is the guest's only (6c) | a limit, not a measurement; `environment/PLAN.md` Limits | SUPPORTED |
| 26 | Steal is counted in 10 ms ticks, coarse against a process of "about 75 ms" (6c, first wording) | the median timed process spans 8 ticks, 80 ms; maximum 54 ticks | OVERSTATED (precision): the figure came from the plan's estimate. Fixed: the page prints the median from the raw samples (80 ms) |
| 27 | A shared core is "a real feature of this setup: the driver and any other process can use the sibling ... while a loop is timed" (6c, first wording) | the driver starts each run with a blocking `subprocess.run` and waits; it is not running while a loop is timed. Other work on the sibling was not recorded | OVERSTATED. Fixed: the page says the driver waits, that only other work on the sibling could matter, and that this was not recorded |
| 28 | Alternating the builds "is why it cancels in an A/A and in a ratio" (6c, first wording) | a mechanism nobody measured here | OVERSTATED. Fixed: "should largely cancel ... this run does not measure how much noise it adds or whether it cancels fully" |
| 29 | Limits item "Mostly one toolchain ... the other setups rest on few jobs" (details, section 8) | the newer toolchains are now timed on the eight loops | STALE. Fixed: "One main toolchain" plus the newer timed toolchains and what held |
| 30 | README: "One main toolchain. Ubuntu clang 18, libc++" | same | STALE. Fixed: names clang and libc++ 19 to 21 and what held; adds a machine-state bullet |
| 31 | `readme-parts/DETAILS.md`: "One main toolchain: clang 18.1.3 ..." | same | STALE. Fixed: three newer ones named; new bullets for `versions/` and `environment/` |
| 32 | README top bullet: loops that lose SIMD "(reverse, stride-2, matrix multiply)" cost 2.8x to 8.0x | true on clang 18; matrix multiply is not lost on 19 to 21 | SUPPORTED as scoped. The bullet now says "matrix multiply on clang 18" |
| 33 | Main page: newer toolchains timed too, reverse and strided loops still lose SIMD, matrix multiply no longer does; limits box names one CPU model with enough jobs (main page) | rows 5 and 10 above, `summary.enough` in `versions.json` | SUPPORTED |

## Statements checked and left alone

- "Compiled only: clang always loses the reverse and strided loops, never a forward one" (abstract, section 6): the timed runs agree on every toolchain; matrix multiply is described there as version-dependent, which the timed runs match.
- `site/app.js` real-programs and PGO limits say "one toolchain": still true, since no program was timed on a newer toolchain.
- The mitigation gist (rewrites recover reverse and matrix multiply): measured on clang 18 only; on 19 to 21 matrix multiply is not lost, so the matrix-multiply rewrite was not re-tested there. Said in the limits item; not changed in the section text.
- An earlier list of known gaps (not published) still lists steal and frequency as never recorded: a historical record; the gap is now closed by `environment/`. Left as written.

## Not checked

The compile remarks themselves (the stored vectorization records were read; nothing was compiled). The apt.llvm.org package contents beyond the version strings in `toolchain.json`. Whether the guest's reported MHz reflects the host.
