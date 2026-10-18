# Arm column: the same eight loops on an AArch64 runner

Status: work in progress (Oct 2026), like the rest of the project. One core type, one compiler and 30 jobs make this a first reading, not a survey of Arm hardware. The column is pooled and reported on its own; no number of the x86-64 study depends on it.

## Question

The x86-64 results say that loops which lose SIMD under libc++'s FAST hardening mode pay 2.8x to 8.0x in cache, and that forward loops pay little on the AMD models. Do the same loop shapes lose their vector code and pay on an AArch64 core (NEON)? And what do forward loops cost on this machine, where the A/A control of one L1 cell is far below a third of a percent?

## Short answer

On GitHub's `ubuntu-24.04-arm` runner, 30 jobs in 3 runs, every job on a Neoverse-N2 core, with the packages, flags, harness and written rules of the x86-64 study:

- **Reverse and stride-2 lose their NEON loops under FAST and pay.** 6.58x and 5.50x at L1, 5.90x and 5.07x at L2 (as compiled). Their functions go from 4 and 5 NEON instructions to none, and the compiler reports "could not determine number of loop iterations", the remark the x86-64 builds print for the same two loops. The L2 figures are medians of noisier timings than the L1 ones and are the less stable estimates (see "Noise at L2").
- **Matrix multiply keeps its NEON loop and still pays.** The loop is vectorized in both builds, as the compile-only sweep (`ce-sweep/`) said it would be on AArch64 for clang 18. FAST costs 1.55x at L1 and 1.02x at L2. On x86-64 the same loop is lost under clang 18 and costs 3.2x to 4.8x. What in the listing goes with the cost is described below; why the cost falls from L1 to L2 is not established.
- **Forward loops keep NEON and cost 1.000x to 1.007x at L1** (as compiled), against a pooled A/A floor of 0.009%, which is the floor of one cell (the forward add at L1), not of the machine. The add and the stencil are placement-sensitive at L1 and not judged by the rule; the add's 0.5% is 26 extra instructions in each call, a count that is the same at L2. At L2 the forward cells are noisy, and so is an identical binary timed against itself there (A/A half-width 2.62%).
- **Gather and histogram**, which are never vectorized, pay for the check itself: 1.59x and 1.13x at L1.
- **The verdict under the written rules is INCONCLUSIVE, and the data cannot separate it from MAP.** One forward cell misses the rule: the forward add at L2, aligned, has an interval that ends at 1.021, against a limit of 1.02. The margin, 0.0011, is inside the bootstrap's own seed noise: the same data under 400 other seeds gives an end at or above 1.02 in 8, and a whole verdict of MAP in 392. The stored verdict is the one the rule gave under the seed fixed before the Arm runs. It is not changed here, and it is not a finding that the forward add costs more than 2% at L2.

## Setup

Nothing about the method changes.

- **Runner.** `ubuntu-24.04-arm` (GitHub-hosted). `lscpu` reports `Neoverse-N2`, 4 vCPUs with one thread each, 64 KiB of L1d and 1024 KiB of L2 per core and a 131072 KiB L3; Ubuntu 24.04.5 LTS, kernel 6.17.0-1022-azure. The only workflow change is the `runner` input of `measure.yml`; the CPU name is read from `lscpu` when `/proc/cpuinfo` has none.
- **Toolchain.** Ubuntu clang version 18.1.3 (1ubuntu1) and libc++-18-dev 1:18.1.3-1ubuntu1 from apt, `-O2 -std=c++20 -stdlib=libc++`; NONE and FAST (`_LIBCPP_HARDENING_MODE`), the aligned pair (`-falign-loops=64`) and the no-vectorize build, as on x86-64. There is no `-march` or `-mcpu` flag, so the compiler's default AArch64 target is used. The core reports SVE and SVE2; the listings contain no SVE instruction.
- **Loops and sizes.** The same eight kernels (`kernels/`). Working sets of 32 KiB (L1) and 512 KiB (L2), half of the per-core caches; matrix multiply uses d = 52 and d = 209. There are no RAM cells. On EPYC 7763 the same rule gives working sets of 16 KiB and 256 KiB and d = 36 and d = 147, so an "L1" or "L2" cell here and one in the x86-64 column share the name of a cache level, not the number of bytes or the matrix size.
- **Timing.** 40 repetitions per side in ABBA order, pinned to one vCPU, as on x86-64.
- **Runs.** Three runs of `measure.yml` with `runner=ubuntu-24.04-arm` (38905055834, 38905081930 and 38905108936), 10 jobs each, dispatched together. All 30 jobs returned results and all 30 are pooled; none was dropped. The harness started between 13:04 and 13:16 UTC on Oct 16. All 30 are the same CPU model, so the pool (`results/s8-arm-pooled/pooled.json`) has one entry.
- **Rules.** `harness/criteria-v3.json`, the file that judges the x86-64 pool, unchanged. Pooling by `harness/pool.py`: a two-level bootstrap over jobs and then repetitions, and at least 3 jobs for a verdict.
- **Harness change.** `harness/asm.py` and `harness/placement.py` read AArch64 `objdump` text: `brk #0x1` is a trap, `b.cond`, `cbz`/`cbnz` and `tbz`/`tbnz` are loop branches, and NEON operands (`v0.4s`, `q0`) mark SIMD (`tests/test_arm64_asm.py`). The 64-byte-window placement fields are computed for Arm as for x86-64 but were defined for x86 fetch windows; whether 64 bytes is the right unit on this core was not examined. After these runs `normalize()` in `harness/asm.py` was changed to strip branch targets of three or more hex digits (it stripped four or more, which left AArch64's three-digit targets in the diffs); this applies to future runs. The `.diff` files in `results/s8-arm-run-*/` were written before the change and are not regenerated, so a branch whose target moved between two builds shows in them as one removed and one added line (for the forward add at L1: 65 added and 44 removed lines as stored, 64 and 43 after the change).

## Results

### FAST over NONE, per loop

Pooled over the 30 jobs. Each cell is the ratio as compiled, with the aligned build (`-falign-loops=64`) in parentheses. NEON instructions are the ones in the loop function's listing with a vector operand (`v0.4s`, `q0`), checks off then on.

| loop | NEON instructions, NONE / FAST | L1 | L2 |
|---|---|---|---|
| forward sum | 13 / 13 | 1.000 (1.000) | 1.002 (1.007) |
| forward add | 5 / 5 | 1.005 (1.007) | 0.991 (0.986) |
| stencil | 10 / 10 | 1.007 (0.974) | 0.997 (0.996) |
| reverse | 4 / 0 | 6.578 (6.571) | 5.900 (5.893) |
| stride-2 | 5 / 0 | 5.498 (5.236) | 5.072 (4.912) |
| gather | 0 / 0 | 1.590 (1.433) | 1.134 (1.109) |
| histogram | 0 / 0 | 1.132 (1.132) | 1.131 (1.130) |
| matrix multiply | 6 / 6 | 1.548 (1.589) | 1.016 (1.018) |

The 95% intervals (a bootstrap over jobs and repetitions) are narrow at L1 and wide at L2; `results/s8-arm-pooled/pooled.json` has all of them. The widest at L1 is 0.24% either side of its ratio (the stencil, aligned) and the widest at L2 is 2.92% (stride-2, as compiled). The spread between jobs (the standard deviation of the log ratio) is largest at 0.41% at L1 (the stencil, aligned) and 7.80% at L2 (stride-2, as compiled). The L2 columns are medians of timings that are noisy inside every job, even for an identical binary, so they are less stable estimates than the L1 columns (see "Noise at L2").

### Reverse and stride-2

The NONE builds vectorize both loops (width 4, interleaved count 2). Under FAST the compiler reports `loop not vectorized: could not determine number of loop iterations`, the functions contain no NEON instruction and one `brk #0x1` each, and the reverse loop is a scalar loop with a compare and a branch to the trap in every iteration. Cachegrind counts 7.96x and 9.51x the instructions at L1 (instructions, not time). The no-vectorize build over NONE, at L1, costs 5.45x for reverse and 3.46x for stride-2, so the checked scalar loops cost more than plain scalar loops do: 6.58x against 5.45x, and 5.50x against 3.46x. What the remainder is was not isolated; it is presumably the per-element compare and branch, as inferred in the x86-64 study.

The compile-only sweep (`ce-sweep/`, Compiler Explorer's clang 18.1.0 for AArch64) classed the loops the same way as these timed builds: reverse and stride-2 lost, matrix multiply and the forward loops kept.

### Matrix multiply: kept, and 1.55x at L1

**Observed.** Both builds contain the same NEON loop: nine instructions, the same opcodes, with two `mla v.4s` in it. The FAST listing has 138 lines against 76 (function header included), so its 62 extra lines lie outside that loop. The FAST listing has 12 `csel` instructions; the NONE listing has no `csel`, but one `cset` and one `csinc`. Three conditional branches in the function lead to its single `brk #0x1` (their targets are in the saved listing, for example `results/s8-arm-run-38905055834/results-neoverse-n2-j1/asm/k08_matmul.fast.s`; the `.diff` files normalise targets away); none is inside the NEON loop, and two are inside the scalar remainder loop, so that loop runs two checks for every element it handles. Cachegrind counts 1.78x the instructions at L1 and 1.20x at L2 (instructions, not time), and the time ratio is 1.55x at L1 and 1.02x at L2. In log terms the time ratio is 0.76 of the instruction ratio at L1 and 0.09 at L2: at L2 a rise of 20% in instructions comes with a rise of 1.6% in time.

**Inferred from the listing, not tested.** The compares and selects before the NEON loop read as a sequence that works out, before the loop, how many elements stay in bounds, so that the loop itself needs no check. At d = 52 each inner call runs the NEON loop 6 times (8 elements per pass) and the scalar loop for 4 elements; at d = 209 it runs the NEON loop 26 times and the scalar loop for 1 element, so a fixed setup cost and a checked scalar remainder make up more of an inner call at L1 than at L2. That goes the right way for the instruction ratio, which falls from 1.78x to 1.20x.

**What the ratios do not support.** The time ratio does not follow the instruction ratio: in log terms it is 0.76 of it at L1 and 0.09 at L2 (above). A setup cost spread over longer rows does not explain that on its own: the two cells also differ in the cache level, in d and in the remainder at once, and instructions can be hidden while a loop waits for memory. So this section does not say why L1 pays 1.55x and L2 1.02x; it describes the listing and the counts. Not tested: that these instructions, and not something else in the core, account for the time (no hardware counters were read and no variant with the setup removed was built or timed), and why the compiler lays the checks out this way here. The plan (below) said the difference from x86-64 would be reported, not explained, and this section is a description of the listing and the counts, not an explanation of the difference.

**A cheap check, proposed here and since run in another form.** Time the existing kernel at several d with d mod 8 = 4 inside L1d (d = 28, 44, 52, 60, 68; three d x d int32 matrices fit in the 64 KiB of L1d up to d = 73) and beyond it (d = 76, 100, 148, 212, 276), and at d mod 8 = 0 (d = 48, 56, 208, where no element is left for the scalar loop), to see whether the ratio falls smoothly with d across the L1 to L2 boundary or steps down at it. A Cachegrind sweep over the same d needs no timing at all.

**The sweep that was run.** It chose its own sizes under a plan committed before its code and the runs (d = 12 to 52 in steps of 8 and 76, 108 and 148, all at d mod 8 = 4, a scan of 45 to 51, and 209) and timed matrix multiply at 17 sizes in one run of 6 jobs on this core. The registered word for Neoverse-N2 is "neither": as compiled the excess time per inner call falls with d (fixed share 1.332, the rule's word "falls"; 2.8 ns at d = 148 and 0.46 ns at d = 209); aligned the fixed share is 1.090, inside the registered H1 band (0.8 to 1.2), yet the aligned excess also falls at d = 148 (3.7 ns) and at d = 209 (0.50 ns). At the sizes with d = 4 mod 8, from d = 28 to d = 108, the excess is flat (3.8 to 4.0 ns as compiled, 4.2 to 4.3 ns aligned), and d = 76 and d = 108 are past the L1 size of this core (64 KiB L1d: 69,312 B and 139,968 B), so the excess is flat across the L1 boundary and smaller only at d = 148 and d = 209; no hardware counters were read, so what the cost is stays untested. See [dsweep/README.md](../dsweep/README.md).

For scale: on x86-64 with clang and libc++ 19 to 21, which also keep matrix multiply vectorized, the cost is 1.6x at L1 and 1.15x at L2 on EPYC 7763 (`versions/`); another architecture, another compiler and other cache and matrix sizes (d = 36 and d = 147 on EPYC 7763), so not the same experiment.

The verdict does not judge either matrix-multiply cell, because the written rule flags both as placement-sensitive (below). The 1.55x at L1 is therefore not judged by any rule of the verdict.

### Gather and histogram

Neither is vectorized in either build, so nothing is lost; what they pay is the check in a scalar loop: gather 1.59x (aligned 1.43x) and histogram 1.13x at L1, 1.13x and 1.13x at L2. Their instruction counts rise 1.80x and 1.29x.

### Forward loops: what they cost, and against what

The plan said that if the A/A half-width is below 0.30%, the forward loops would be reported against it as a description. The pooled A/A half-width is 0.009% (per job, 0.021% to 0.056%). That is the A/A of one cell, the forward add at L1: the floor of that cell, not of the machine (other cells are noisier; see "Noise at L2"). Against it, at L1:

- the forward sum costs 0.0% as compiled (ratio 1.000, interval 0.9999 to 1.0001) and 0.0% aligned;
- the forward add costs 0.5% as compiled and 0.7% aligned;
- the stencil costs 0.7% as compiled and -2.6% aligned.

What each reading rests on:

- **The sum.** Its FAST listing is the same as the NONE one line for line and has no trap (the negative control, below), so there is no check left and 0.0% is what an identical function gives.
- **The add.** Cachegrind counts 3,452 instructions per call in NONE and 3,478 in FAST at L1 (2,730 elements), 26 more as compiled (38 more aligned), and 54,652 and 54,678 at L2 (43,690 elements), the same 26 more. The cost is a constant per call, not a cost per element: 0.75% of the instructions of an L1 call and 0.05% of an L2 call. Its percentage at L1 is therefore set by the array length chosen for the size, not by the loop shape.
- **The stencil.** 35 more instructions per call as compiled (34 aligned), at both sizes. Its time ratio changes sign with loop alignment (+0.7% as compiled, -2.6% aligned): the yardstick for it is the compiled-over-aligned ratio, 1.034 (3.4%), not the A/A floor.

These are costs of single loops on one core type, not an average over a service: they neither confirm nor contradict Google's 0.30%. The stencil's lower aligned figure is a placement effect (below).

At L2 the forward cells are 0.991 to 1.002 as compiled (0.986 to 1.007 aligned), but with intervals reaching 2.8% either side of the ratio and a spread between jobs of up to 6.0%; they are too noisy on this core for the 2% forward rule to settle (see the verdict). An identical binary is as noisy at the add's L2 cell as the pair of builds (see "Noise at L2"), so that width is a property of the L2 timings on this machine, not evidence about the check.

### Controls

- **A/A** (the forward add at L1, one binary against a byte-identical copy): pooled 1.0000, half-width 0.009%. This is the control the written rules read, and it is the floor of that one cell. Every job also timed the same A/A at the add's L2 cell (`details.json`, `aa_extra`; `pooled.json` does not hold it): pooled 1.0014, half-width 2.62%.
- **Layout A/A** (NONE against NONE built with `-falign-loops=64`): the half-width runs from 0.006% at the quietest L1 cells to 3.0% (stride-2, L2). Moving the loops alone changes matrix multiply at L1 by 3.8% (ratio 1.038), the largest layout effect at L1; the other L1 cells move by at most 0.17%. It moves only the unchecked build's loops (see "Placement").
- **Negative control** (the forward loops stay vectorized in both builds, expected near 1): the NEON instructions stay at 13, 5 and 10; the forward sum's function is identical line for line in both builds and has no trap.
- **Positive control** (the no-vectorize build over NONE): at L1 it costs 5.05x for the sum, 5.89x for the add, 3.87x for the stencil, 5.45x for reverse, 3.46x for stride-2 and 3.66x for matrix multiply (3.5x to 5.9x). Switching vectorization off by hand is a known slowdown of this size on this core.

### Noise at L2

What the stored timings show. No cause is claimed: no hardware counter was read, the machines are shared, and why L2 timings behave like this on this core was not examined.

- **An identical binary is as noisy at L2 as the cell that decides the verdict.** The A/A at the forward add's L2 cell, pooled by the same method (`harness/pool.py`), is 1.0014 with an interval of 0.975 to 1.027, a half-width of 2.62%, a spread between jobs of 4.94% and per-job ratios from 0.912 to 1.150. At L1 the A/A is 0.009%. The forward add at L2 has half-widths of 2.67% (as compiled), 2.77% (aligned) and 2.40% (the layout A/A) in the same cell. So the width of the cell that decides the verdict is the L2 noise floor of this machine at that cell, not a property of the check.
- **The rule's A/A is the L1 one.** `harness/criteria-v3.json` reads the A/A at one cell, the add at L1. The L2 A/A is above the rule's own ceiling of 2% in the pool and in 24 of the 30 jobs (in none at L1); the same clause applied to it would end any verdict at INCONCLUSIVE before the forward rule is read. The rule is not changed here, and the verdict above is the one it gives.
- **The noise is inside each job.** A process is slow when it takes more than 5% longer than the fastest process of the same series (one side of one cell in one job). At L1, 2.2% of NONE processes and 1.5% of FAST processes are slow; at L2, 30.3% and 17.6%, and single cells reach 48% (NONE) and 46% (FAST). In the L2 A/A series the coefficient of variation of one side's 40 processes is 12.4% and 12.8% on the two sides of the pair (median over jobs), against 0.10% and 0.09% at L1, and the slow processes come in runs: after a slow process the next one on that side is slow 61% and 64% of the time on the two sides of the pair, after an ordinary one 32%.
- **What this does to the L2 medians.** The L2 ratios are medians of mixtures, so they are less stable estimates than the L1 ones. In the reverse and stride-2 cells at L2 only the NONE side has slow processes (40% and 48% of them, none on the FAST side). Taken at the fast end of the timings (the geometric mean over jobs of the ratio of each job's 10th percentiles, as compiled; descriptive, the written rules use medians) the two ratios are 6.04x and 5.43x, against the medians' 5.90x and 5.07x. For the forward add at L2 the same ratio is 1.000, against a median ratio of 0.991 whose interval is 2.7% either side.

### Placement

The written rule (`harness/criteria-v3.json`) calls a forward cell placement-sensitive when the interval of the ratio of its as-compiled to its aligned result excludes 1 and the hot loops of NONE and FAST sit differently against 64-byte windows. Four cells are flagged: the add at L1 (ratio of the two 0.998), the stencil at L1 (1.034), and matrix multiply at L1 (0.974) and L2 (0.999). On this quiet core the interval excludes 1 for a difference as small as the add's 0.2%. The plan predicted no placement effect for the forward loops; for the add and the stencil at L1 that did not hold under the rule. They are listed beside the verdict and not judged.

The layout A/A (NONE against NONE with its loops moved) does not see the shifts that the compiled-over-aligned ratio D shows. D, which moves the loops of both builds, is 1.034 for the stencil at L1, 1.050 for stride-2 at L1 and 1.110 for gather at L1, where the layout A/A moves 0.12%, 0.14% and 0.02%; for matrix multiply at L1 the layout A/A moves 3.76% and D -2.62%. D's interval excludes 1 and the layout A/A's includes it for the stencil at L1 and for gather at L2. So the layout A/A is not a control for the placement of the FAST/NONE ratio; D is, and on this core it moves by up to 11.0% at L1 (gather). The window-crossing explanation that the x86-64 study gives for its forward add was not tested on Arm, and matrix multiply at L1 goes against it: as compiled the NONE NEON loop starts at offset 44 of a 64-byte window and spans 2 windows, aligned it sits in 1, and the aligned NONE build is 3.8% slower (layout A/A ratio 1.038).

### The verdict, and exactly why

INCONCLUSIVE ("a mixed picture"), in the pool and in each of the three runs on their own. It is not called a map.

- The rule for lost loops is met: the interval of every in-cache cell of reverse and stride-2, in both columns, starts at 4.76 or higher, against a minimum of 1.5.
- The forward rule is missed. Four of the eight kept cells are judged (the sum at L1 and L2, the add at L2, the stencil at L2); the other four are the placement-sensitive ones. The forward add at L2, aligned, has a ratio of 0.986 and an interval of 0.966 to 1.021; its upper end is 0.0011 over the limit of 1.02, and the spread between jobs in that cell is 5.4%. In each run on its own both the forward sum and the forward add at L2 miss the rule.
- Counting the matrix-multiply cells would not change the form. The one at L1 would miss the forward limit as well (1.59x aligned); the one at L2 (1.018x aligned, interval ending at 1.018) would pass it.

The form is stable across the three runs in the sense that each is INCONCLUSIVE; that is not independent confirmation, because the runs were launched together.

#### How firm the verdict is: sensitivity readings beside it

These readings change no rule, threshold, seed or resample count, and the stored verdict is the one above. Their code is committed and their output is stored in files that the tests read.

- **The seed.** The upper end of the add's interval comes from a bootstrap of 2000 resamples whose draws are fixed by a seed (`harness/pool.py`, prefix 20261011). The seed was set on Oct 12 (2026-10-12T09:41:36-04:00 in the development history, which this repository does not contain), four days before the first Arm run; it was not chosen or changed with Arm data, and the rule was applied as written. `arm64/seeds.py` re-draws the same statistic, from the same data with the same code and the same 2000 resamples, under 400 other seeds (`arm64/seed-sensitivity.json`): the upper end has a median of 1.0181 (5th to 95th percentile 1.0168 to 1.0196, range 1.0152 to 1.0208), 8 of the 400 are at or above 1.02, and the stored 1.0211 is higher than all 400. With 100,000 resamples under the stored prefix the end converges to 1.0183, below the limit.
- **The whole analysis.** `harness/pool.py` `analyse_cpu` run under 40 of those seeds gives 39 MAP and 1 INCONCLUSIVE. The verdict form derived from the re-drawn statistics (forward, lost, placement, A/A and positive-control rules) for all 400 is 392 MAP and 8 INCONCLUSIVE, each of the 8 because of the same cell. Under every seed the lost loops pass, the placement-sensitive set is the same four cells and the A/A half-width stays between 0.0084% and 0.0098%.
- **Other interval methods.** `robustness/` applies eight interval methods to this pool (`robustness/PLAN.md` has a note written before the run, `robustness/results-arm.json` the numbers; its self-test reproduces 99 of the pool's own numbers exactly). Only the pool's own method gives INCONCLUSIVE; the block bootstraps over 1, 2 and 5 ABBA quartets, the jobs-only bootstrap and t interval and the two lag-1 corrections all give MAP, with the add's upper end at 1.016 to 1.017 (block), 1.004 and 1.006 (jobs only) and 1.014 (lag-1), against the pool's 1.021.
- **The L2 A/A.** Read at the L2 cell the A/A is 2.62%, above the rule's 2% ceiling (see "Noise at L2"), and the form would be INCONCLUSIVE whatever the add's interval. Like the seed and method readings above, this is a reading beside the verdict: the written rule reads the A/A at L1 only.
- **The independent check.** `harness/pool_check.py`, the recomputation that `scripts/check.py` runs, does not sample this cell, and its tolerance (a share of the interval's width, about 0.009 here) is larger than the margin of 0.0011, so it could not flag a change of this size. `robustness/` recomputes the cell with the pool's own seed and gets the stored numbers exactly.

What this says. The stored verdict is INCONCLUSIVE and is kept. It is not a finding that the forward add costs more than 2% at L2: that cell's interval is 2.8% either side because L2 timings on this machine are that noisy, even for an identical binary, and a margin of 0.0011 is smaller than the bootstrap's seed noise. The data cannot separate INCONCLUSIVE from MAP at this cell. A pre-planned replication of 30 more jobs (set B, 29 of them Neoverse-N2) was run afterwards; alone it is INCONCLUSIVE on the same cell, with the aligned interval ending at 1.0247, and pooled with this column (59 Neoverse-N2 jobs) it gives MAP, which the harness labels unstable. This column's own verdict is unchanged; see [replication/README.md](../replication/README.md).

### Run to run

Of the 192 comparisons of one run's point against another run's interval (16 cells, 2 columns, 6 ordered pairs of runs), 13 fall outside, with a largest gap of 5.17%. Eight of the 13 are stride-2 at L2 (gaps of 2.06% to 5.17%), where the runs' points are 4.92x, 4.95x and 5.36x as compiled; the other five have gaps under 0.01%. In those stride-2 cells the intervals understate the spread between runs, as they do on x86-64.

## Written first, and whether it held

`PLAN.md` set down the prediction before the full results existed, but not before every Arm number. The smoke run (38904557204) timed two kernels at the L1 size and had given reverse 6.58x, the forward add 1.005x and an A/A half-width of 0.04%; the plan quotes all three. What the full runs gave for stride-2, matrix multiply, the stencil, the sum, gather, histogram, every L2 cell and every listing was not seen. The statements, and which were blind:

- **Reverse and stride-2 lost under FAST.** Held (remarks, NEON counts and time, above). The plan notes that reverse was already seen in a two-kernel smoke run, so it was not a blind prediction; stride-2 was.
- **Matrix multiply not lost on AArch64** (from the compile-only sweep). Held: vectorized in both builds. Blind. The plan said any difference from x86-64 would be reported, not explained.
- **Forward loops vectorized in both builds, no placement effect.** The first part held (13 / 13, 5 / 5 and 10 / 10 NEON instructions); it was blind for the sum and the stencil, and for the add the time ratio at L1 (1.005x) was known. The second part did not hold under the written rule for the add and the stencil at L1 (above).
- **Gather and histogram:** no prediction was written; the results are above.
- **Every job that returns is pooled, none dropped:** 30 of 30 returned and all are pooled.

No count of held predictions is given: the two statements that touch a figure seen beforehand (reverse, and the forward add's vectorization) were not blind, and the one about placement did not hold for two cells.

## Limits

- **One core type.** Neoverse-N2, in one runner image. The `ubuntu-24.04-arm` label could map to other core types later; the pool is per `lscpu` model name. The host and the hypervisor are not recorded. Nothing here is said about Apple silicon, AWS Graviton or any other Arm core.
- **Shared machines, 30 jobs, one time window.** The three runs were launched together and the jobs started within 12 minutes of each other, so agreement between the runs does not cover different days or different hosts. The narrow intervals at L1 are those of byte-identical binaries on one core type in one window: they contain no spread between hosts or days, and none was visible (the identical-binary A/A at L1 has a spread between jobs of 0.019%).
- **One compiler.** clang 18.1.3 with libc++ 18 only, `-O2`, FAST mode, the default AArch64 target (NEON; the core's SVE is unused). No other compiler, library version or flag set was timed on Arm.
- **No hardware counters.** The mechanism statements are readings of the compiler's remarks and of the listings; where one is worded "consistent with" or "inferred" it was not tested.
- **Placement fields were defined for x86 fetch windows** (64-byte windows). The layout A/A moves only the unchecked build's loops and did not see the placement shifts of the FAST/NONE ratio (3.4% for the stencil and 11.0% for gather at L1); the compiled-over-aligned ratio is the control that applies, and the window-crossing explanation is untested on Arm.
- **The A/A floor is the floor of one cell**, the forward add at L1 (0.009%). The widest interval at L1 is the stencil's, 0.24% either side of its ratio, and at L2 stride-2's, 2.92%.
- **L2 forward cells are noisy** (spread between jobs up to 6.0% for the add), an identical binary is as noisy at the add's L2 cell (A/A half-width 2.6%), and the INCONCLUSIVE form rests on one of them, by a margin inside the bootstrap's seed noise.
- **No RAM cells, no real programs, no PGO and no census on Arm.**
- **The rules were written after earlier results** (see the main README); this column added no rule and changed no threshold.
- **Nothing about Google's services** or its 0.30% average.

## Reproduce

```
gh workflow run measure.yml -f runner=ubuntu-24.04-arm
```

Run it more than once for a pool (the three runs here were dispatched together), then `gh run watch` and `gh run download <id>` into one folder per run. The per-job files are the `results-neoverse-n2-jN` artifacts. Then:

```
python harness/pool.py results/s8-arm-pooled/pooled.json results/s8-arm-run-*
python scripts/check.py
```

`python scripts/check.py` recomputes every interval from the raw timings and checks the figures in this file against the data. The sensitivity readings have their own commands: `python arm64/seeds.py` rewrites `arm64/seed-sensitivity.json` (it re-draws 400 seeds, so it takes a while), `python arm64/seeds.py --check` recomputes a sample of it and `--check --all` all of it; `python robustness/check.py` recomputes `robustness/results-arm.json`.

## What was written first

`PLAN.md` in this folder was written first. The two-kernel smoke run (38904557204) started at 13:00 UTC on Oct 16, the three full runs were dispatched at 13:04 UTC, the plan was committed at 13:07 UTC (09:07 EDT) and the first full-run job finished at 13:15 UTC. So the plan came after the dispatch and before any full-run result; it quotes the smoke run's reverse and forward-add figures. The plan's own heading gives the time as 09:30 EDT, which is wrong (the author date of the commit that added the file says 09:07); the plan was left as written and has not been edited since.

What a reader can check. The first, second and fourth times are those of public Actions runs of this repository (the run's creation time and the first measure job's completion time, read from the Actions API on Oct 16). The plan's commit time is not: it comes from the git log of the working repository in which the project is developed, which is not published, and this repository's history does not contain that commit, so `git log -- arm64/PLAN.md` here shows a later date. The order "plan committed after the dispatch and before the first job finished" therefore rests on that log and on the plan's own header, which says it was written before any of the full runs had finished. `tests/data/s8_arm_timeline.json` is a record of what was read from the Actions API and from that log, so that the sentences above are tied to something; it is not a proof of either.
