# Matrix-multiply d-sweep: plan, fixed before any run

First written Sat Oct 17, 2026, 03:30 EDT (by `date`), before `dsweep/sweep.py`, `dsweep/analyze.py`,
`.github/workflows/dsweep.yml` and `tests/test_dsweep.py` existed. It was edited while that code was written and
tested, and again after an independent review of this plan and that code (last edit Sat Oct 17, 2026, 04:29 EDT
by `date`). Every change of a rule or of a number that was made after the first draft is listed under "Changes made
before any run". No run of `dsweep.yml` had been started when the last edit was made.

This file is to be committed on its own, before any run, and not edited afterwards, not even in wording. Every
`dsweep.json` stores the SHA-256 of this file (line endings read as LF), and `dsweep/analyze.py` treats a file whose
stored hash differs from the hash of this file as it stands as a file problem (verdict "neither"). An edit after the
first run therefore makes the data unusable. That is intended. If only the wording of this file is changed later by
mistake, `git show <run commit>:dsweep/PLAN.md > plan.md` restores the text the runs saw and
`python3 dsweep/analyze.py <runs> --plan plan.md` analyses against it (the hash must still match).

No result of this sweep exists. Nothing below was fitted to one. The rule was exercised only on generated data
(`tests/test_dsweep.py`: simulated jobs with a fixed cost, with a cost per element, with mixtures, with a cost that
shrinks as d grows, with noise and with a baseline that is not affine), to see that it answers H1, H2, falls and
"neither" as written. The thresholds were not tuned on any measurement.

## Changes made before any run

1. While the code was written and tested (the same morning, before the review): a check that each build's time per
   inner call is affine in d was added to the rule (now condition 6), and its limit on the relative residual was
   raised from 0.05 to 0.10. This is a judgement, not an observation: no measurement of a short loop was looked at.
   The reasoning is that a loop of 12 elements (one vector pass and some leftover elements) may leave a straight line
   by several percent for reasons that are not a change of regime, and a limit of 0.05 might then stop the rule for
   the wrong reason. The intent of the condition is to catch a changed regime (a vector loop that is not entered at a
   small d), not the irregularity of a short loop. If real data show a baseline residual between 0.05 and 0.10, that
   is reported beside the word.
2. After the independent review (this is a change of the decision rule):
   - **The deciding statistic.** The first draft decided on the slope of `y = 1 / (R - 1)` on d and on the dilution
     `Q = y_hat(d_max) / y_hat(d_min)`: "H1" when the slope interval was above 0 and `Q` was at least 1.5, "H2" when
     the upper end of the `Q` interval was below 1.25. The review showed that this called "H1" for any excess that
     grows more slowly than the time per inner call, which is nearly every shape. On generated data (a time per
     inner call of `0.02 + 0.1357 d` ns and an excess of 3.88 ns at d = 52) the draft rule answered "H1" for an
     excess whose fixed share at d = 52 was only 75%, 50%, 35% or 25% (the rest per element), for an excess that
     falls as `d^-0.1` to `d^-0.6` (with `Q` from 5 to 20, above the 4.33 that any fixed cost can give on the
     Neoverse-N2 ladder), for an excess that falls as an affine function of d, and for an excess that grows as the
     square root of d. A word that means "a fixed cost per inner call" has to be decided on the excess itself, so the
     rule now reads the fixed share of the excess per inner call (below). The `y` view and the inverse view are still
     computed and printed; they decide nothing. The thresholds 1.5 and 1.25 are gone.
   - **A third word.** "falls" (the excess per inner call is smaller at the larger d) is declared now, because the
     stored data already show that shape between d = 52 and d = 209 (see "Published numbers").
   - **A new condition 7**: the excess per inner call must be a straight line in d (median over jobs of the largest
     absolute residual divided by the job's mean excess, limit 0.15). A fixed part and a per-element part only
     describe a straight line. The limit is a judgement, made without a measurement of a short loop; it is looser
     than the 0.10 of condition 6 because the excess is a difference of two timings and a short loop is irregular.
     A strongly curved excess therefore ends as "neither" with that reason (on generated data a fall as `d^-0.6` fails
     condition 7, a steeper one condition 6), and its pooled values are reported.
   - **The undefined-resamples condition (now 8)** refers to the share, not to the old `Q`.
3. **Bridge points.** Three context d values between the study L1 d and the study L2 d, in the same residue class,
   were added (Neoverse-N2: 76, 108, 148). The part of the observation that is least understood lies between d = 52
   and d = 209 (see "Published numbers"), and nothing in the first draft was timed there. They are not fitted and
   decide nothing.
4. **The paragraph on the L2 figure was corrected.** The first draft said that the published L2 ratio of 1.016 needed
   `a` or `b` to be larger at the L2 size. That is false by the stored data and left out the account that `c` is
   smaller at d = 209. The stored data are now stated, and H2 is stated as the account the listing makes least likely.
5. **The x86-64 control is stated as weak** (see "What the sweep cannot show").
6. **Records, not rules**, added after the review: the SHA-256 of each code file (`CODE_FILES` in `dsweep/analyze.py`)
   in every file; clang's interleave count and the elements per pass of the NONE loop in every file; a partial file
   per job; the job order of the bootstrap fixed by (run id, job number) instead of by path; the `--plan` option; the
   rerun clause defined by artifact. See "Records".

Not changed by the review: the d ladder and its residue class, the timing, the A/A, the bootstrap and the seeds, and
conditions 1 to 6 with their numbers (3 jobs, 2.0%, 4 fit d values, 0.10).

## Question

On the Neoverse-N2 runner, matrix multiply (`kernels/k08_matmul.cpp`) is NEON-vectorized in both the NONE and the
FAST build, and FAST still costs 1.548x at the L1 size (d = 52). The listing shows compares and selects before the
NEON loop, and a checked scalar loop for the elements that are left over. `arm64/README.md` reads these as a setup
cost paid once per inner call and says so as "inferred, not tested". This sweep tests that account: is the excess
time that FAST adds per inner call the same when the inner loop gets longer (a fixed cost, H1), does it grow in
proportion to the number of elements (a cost per element, H2), or is it smaller when the inner loop is longer
(falls)?

## Published numbers this relates to (context, not new data)

- Neoverse-N2, 30 jobs, `results/s8-arm-pooled/pooled.json`, as compiled: 1.548 at d = 52 (L1 size), 1.016 at
  d = 209 (L2 size); with loops aligned 1.589 and 1.018. Cachegrind counts 1.78x the instructions at L1 and 1.20x at L2.
- The same 30 jobs, per inner call (the time of one kernel call divided by d*d; `results/s8-arm-run-*/*/results.json`):

  | | d = 52 | d = 209 |
  |---|---|---|
  | NONE, ns per inner call | 7.080 | 28.392 |
  | NONE, ns per element | 0.1362 | 0.1358 |
  | FAST - NONE, ns per inner call | 3.878 | 0.462 |
  | extra Cachegrind instructions per inner call (not time) | 77.0 | 53.0 |

  The NONE time per element does not change between the two sizes (the ratio of the two is between 0.993 and 0.999 in
  every one of the 30 jobs). The excess per inner call falls by a factor of 8.2 to 8.6 (in every job) while d grows by
  a factor of 4.02. So the stored data already say that the excess per inner call is not the same at the two sizes,
  and that this is not because the time per element is larger at L2. What the sweep adds is the shape inside L1,
  where the leftover count of the scalar loop is held fixed, and, with the bridge points and the residue scan, where
  between d = 52 and d = 209 the excess goes.
- x86-64, clang 18, where the loop loses SIMD under FAST: 3.19 (EPYC 7763, d = 36) to 4.84 (EPYC 9V45) at L1 as
  compiled, pooled in `results/s7-pooled/pooled.json` (95 jobs); 4.25 on EPYC 9V74.
- clang and libc++ 19 to 21 on EPYC 7763, where matrix multiply keeps its SIMD: 1.6x at L1 and 1.15x at L2
  (`versions/`).

## The three accounts

Definitions. An inner call is one run of the innermost loop over j: d iterations. One call of the kernel makes d*d
inner calls. `t_N(d)` and `t_F(d)` are the times per inner call of the NONE and the FAST build, in ns. The ratio
the harness reports is `R(d) = median(FAST) / median(NONE)` of the process times of one pair; the division by d*d
cancels. The excess is `E(d) = t_F(d) - t_N(d)`, in ns per inner call. The NONE build is modelled as

    t_N(d) = a + b*d

where `a` is what an inner call costs whatever d is (entering the loop, the guard in front of the vector loop, the
loads of `aik`, the leftover elements) and `b` is what each element costs. The words describe `E(d)` over the fit
ladder (d = 12 to 52 on Neoverse-N2) and say nothing outside it.

**H1, a fixed cost c per inner call.** `E(d) = c` whatever d is. Then `R(d) = 1 + c / (a + b*d)`: the ratio falls with
d, and the smaller matrix pays the larger ratio. A corollary that needs no fit: `R(d) > R(52)` for every d < 52 on
the Arm ladder.

**H2, a cost c2 per element.** `E(d) = c2*d`. Then `R(d) = 1 + c2*d / (a + b*d)`: with `a` = 0 the ratio is constant
in d, with `a` > 0 it rises with d towards `1 + c2/b`.

**Falls.** `E(d)` is smaller at the larger d. Neither H1 nor H2 predicts this. One way it could arise is that the extra
instructions are hidden under the loads of a loop that is bound by the cache or the load ports, more so when the
loop is longer; the stored comparison of d = 52 with d = 209 shows an excess that falls like this between those two
sizes. This plan makes no prediction of its size.

**A mixture** is `E(d) = c + c2*d`. The fixed share of the excess at the study size, `s = c / (c + c2*d_max)`, is 1
for H1, 0 for H2, between the two for a mixture, and above 1 when the excess falls. The rule is written on `s`.

**What the stored data and the listing say beforehand (an expectation, not a criterion).** The listing
(`arm64/README.md`) shows the same nine-instruction NEON loop in both builds with no check inside it; the checks lie
in the setup before the loop and in the scalar loop for the leftover elements (4 at every fit d, because the ladder
holds the leftover count fixed). That makes H1 the account the listing points to, and H2 the account it makes least
likely: a cost per element would have to come from the NEON loop running slower for a reason that the listing does
not show. The sweep exists to test that reading, not to confirm it, so H2 stays an outcome. The stored fall of the
excess between d = 52 and d = 209 (above) makes "falls" a real possibility.

With the stored numbers of the table above (`a` = 0.0218 ns, `b` = 0.13574 ns, from the two NONE times; `c` = 3.878 ns
from d = 52), the ratios the two accounts would give at the fit ladder of Neoverse-N2 are:

| d | R under H1 (c unchanged) | R under H2 (c2 = c/52) |
|---|---|---|
| 12 | 3.35 | 1.54 |
| 20 | 2.42 | 1.55 |
| 28 | 2.01 | 1.55 |
| 36 | 1.79 | 1.55 |
| 44 | 1.65 | 1.55 |
| 52 | 1.55 | 1.55 |

These come from the stored d = 52 and d = 209 measurements, not from any sweep timing. An outcome in which the ratio at
d = 12 is far from both columns is "falls" or "neither" by the rule below.

## What is timed

**Kernel and builds.** `kernels/k08_matmul.cpp`, unchanged. Four builds are timed, each compiled once with `clang++-18
-O2 -std=c++20 -stdlib=libc++` and the flags of `harness/run.py` (`none`, `fast`, and the same two with
`-falign-loops=64`: `none_a64`, `fast_a64`). d is a run-time argument, so every d runs the same machine code and
the loop sits at the same address for all d. `harness/run.py`'s `build_kernel` is used as it stands; it also builds
a fifth, no-vectorize build, which this sweep does not time.

**L1-resident.** A d is L1-resident when the three d x d int32 matrices fit in half of L1d: `12*d*d <= L1d/2` (the
harness's rule for the L1 size). L1 to L2 changes `b`, so only L1-resident points enter the fit.

**The d values, derived at run time from the runner's cache sizes** (`/sys/devices/system/cpu/cpu0/cache`, read by
`harness/run.py`'s `caches()`), by the rule of `harness/run.py`'s `n_for`: the study L1 d is
`max(8, int(sqrt((L1d/2)/12)))` and the study L2 d is the same with L2.

- *Fit ladder.* Every d with 8 <= d <= (study L1 d) and d congruent to (study L1 d) modulo 8. Neoverse-N2 (L1d 64
  KiB, L2 1 MiB): study d 52 and 209, fit ladder 12, 20, 28, 36, 44, 52. EPYC 7763 (32 KiB, 512 KiB): 36 and 147,
  fit ladder 12, 20, 28, 36. The study L1 d is the top of the ladder and is fitted.
- *Why one residue class and not a geometric ladder.* The NEON loop of the Arm listing handles 8 elements per pass
  (6 passes and 4 leftover elements at d = 52, per `arm64/README.md`; clang's remark says vectorization width 4,
  interleaved count 2) and a scalar loop with two checks per element handles the d mod 8 leftover elements. If d is
  varied freely, the number of leftover elements jumps between 0 and 7 from one point to the next, and the cost of
  the check moves with it. Keeping d congruent to the study d modulo 8 holds the leftover count at the study's own
  value (4 on Neoverse-N2), so everything that is independent of d, the leftover elements included, falls into `c`
  (H1) or `a`. A geometric ladder cannot do that at this size (it would also give fewer distinct points). The
  consequence is a ladder of 4 to 6 evenly spaced points instead of about 8 geometric ones. On x86-64 the stored
  remarks for the NONE loop (for example `results/s6-run-38674961339/results-amd-epyc-9v45-96-core-processor-j10/remarks/`)
  also say width 4, interleaved count 2, so 8 elements per pass. Every file stores the elements per pass of its NONE
  loop, and a pass size that does not divide 8 is a file problem (the argument above would not hold).
- *Residue scan (context, not fitted).* The 7 values (study L1 d - 7) to (study L1 d - 1), which together with the
  study L1 d cover every residue modulo 8. It shows whether the leftover count moves the ratio. No prediction is
  made for it and no rule reads it.
- *Bridge (context, not fitted).* Three d values strictly between the study L1 d and the study L2 d, in the same
  residue class as the study L1 d, evenly spaced on a log scale and rounded to that class: Neoverse-N2 76, 108, 148;
  EPYC 7763 52, 76, 100. They are not L1-resident. They show whether the excess falls smoothly from the L1 figure to
  the L2 figure or steps down at the L1 to L2 boundary. No prediction is made and no rule reads them.
- *Study L2 d (context, not fitted).* Timed once, to place the published L2 figure next to the sweep.
- *Middle d.* The element with index `len(fit) // 2` of the fit ladder (36 on Neoverse-N2); the byte-identical A/A is
  timed there.

**Timing, copied from `harness/criteria-v3.json`.** 40 processes per side (`v3.timing.reps_per_side`, read from the
file), ABBA order (A B B A A B B A ...), each process pinned with `taskset -c` to one CPU (`HARNESS_CPU`, default 1),
the iteration count calibrated once per d on the NONE build as compiled to about 75 ms per process
(`harness/run.py`'s `calibrate`) and reused for every build at that d. For every d two pairs: FAST against NONE as
compiled, and FAST against NONE with `-falign-loops=64` (the aligned pair). The two sides of each pair must print
the same checksum, and the four builds the same checksum as each other at the same d; a difference stops the job (the
d values timed so far are kept, see "Records"). The order in which the d values are timed is shuffled per job with
`random.Random("dsweep|<job>")` and stored, so a drift over the minutes of a job cannot line up with d. Controls: one
byte-identical A/A per job (the NONE binary against a copy of itself, hash checked before timing) at the middle d.

**Secondary, labelled instructions, not time.** Cachegrind instruction counts (`harness/run.py`'s `instr_count`,
20 inner iterations) for NONE and FAST as compiled at every d, divided by d*d. The counts are deterministic, so
they show the same test without noise: H1 predicts that the difference FAST - NONE per inner call is the same at
every fit d; H2 predicts that it grows in proportion to d. They decide nothing. Also recorded per build, from
`harness/placement.py` and `harness/asm.py`: the loops of `kern_k08_matmul` with their instruction counts, SIMD flag
and placement against 64-byte windows, and the trap count.

## How it is analysed (fixed now)

One CPU model is the unit, as in `harness/pool.py`: every `dsweep.json` of a model, across the planned runs, is
pooled. At least 3 jobs are needed (`harness/criteria-v3.json`, `v3.pooling.minimum_jobs`). The pooled ratio of a
d is the geometric mean over jobs of the per-job ratio of medians. Intervals come from the two-level bootstrap of
`harness/pool.py`: 2000 resamples, each draws the jobs with replacement and then redraws the repetitions of each side
inside each drawn job, with the counter-based generator and the seed rule of `harness/pool.py` (prefix 20261011,
statistic ids `dsweep|<column>|jobs` and `dsweep|<column>|d<d>`, one stream per side). The same drawn jobs are used for every d, so the
dependence between the d values of one job is kept. The jobs are taken in the order of (run id, job number, hash of
the file), whatever folder they lie in, so that the draws do not depend on the layout. Two columns are analysed the
same way: *as compiled* (primary: the figures, the fit and the headline are its) and *aligned*.

**The statistic of the rule.** Per column, with `d_min` and `d_max` the smallest and the largest fit d:

1. For each job and each d, the excess per inner call `(median FAST - median NONE) / d^2`, divided by that job's NONE
   time per inner call at `d_max` (so that hosts of different speed pool). The mean over jobs is the pooled excess.
2. The ordinary least-squares line `E_fit(d) = kappa + lambda*d` of the pooled excess over the fit ladder, equal
   weights. `kappa` is the fixed part, `lambda*d_max` the per-element part at the study size.
3. The fixed share `s = kappa / (kappa + lambda*d_max) = kappa / E_fit(d_max)`. The same quantity as a growth:
   `G = E_fit(d_max) / E_fit(d_min) = 1 / (r + s*(1 - r))` with `r = d_min / d_max`: 1 for `s` = 1, `d_max/d_min`
   (4.33 on the Neoverse-N2 ladder, 3 on the EPYC 7763 ladder) for `s` = 0, below 1 for `s` above 1.
4. The 95% percentile interval of `s` (and of `G`) over the resamples. A resample is undefined if `E_fit(d_max) <= 0`;
   the intervals are taken over the defined resamples.

**Conditions, in this order.** The first one that applies decides the word of the column.

1. Fewer than 3 jobs of the CPU model: "too few jobs".
2. A file problem in any job of the model: "neither". File problems: a smoke file (fewer repetitions than the
   criteria file), a stored plan hash that is not this file's hash, a different criteria hash or ladder from job to
   job or from the ladder recomputed from the stored cache sizes, jobs of the model that ran different code (the
   SHA-256 of a code file differs between them), a checksum mismatch, binaries that differ between jobs, unequal
   repetition counts for the same d, a missing fit d, a NONE loop whose elements per pass do not divide 8, a wrong
   schema.
3. The pooled byte-identical A/A has a half-width above 2.0% (`verdict.aa_half_width_max_pct`): "neither".
4. Fewer than 4 fit d values: "neither".
5. The cost is not seen at some fit d, that is, the pooled `ci95_lo` of `R(d)` is not above 1 plus the pooled A/A
   half-width: "neither".
6. The NONE or the FAST time per inner call is not affine in d. Per job, each build's time per inner call at the
   fit d is fitted by a line, and the largest relative residual (the absolute residual divided by the fitted value)
   is taken, over the fit d values and the two builds; if the median over jobs of that number is above 0.10:
   "neither". (This is the check on the model `a + b*d`; a regime change at a small d, for example a vector loop that
   is not entered, would fail it.)
7. The excess per inner call is not a straight line in d. Per job, the excess in ns per inner call at the fit d is
   fitted by a line, and the largest absolute residual is divided by the job's mean excess over the fit d values; if
   the median over jobs of that number is above 0.15: "neither".
8. More than 2.5% of the resamples are undefined: "neither".
9. "H1" if the point estimate and the whole 95% interval of `s` lie inside 0.8 to 1.2.
10. Otherwise "H2" if the point estimate and the whole 95% interval of `s` lie inside -0.2 to 0.2.
11. Otherwise "falls" if the point estimate and the whole 95% interval of `s` lie above 1.2.
12. Otherwise "neither", with the point estimate and the interval of `s` stated (a mixture has `s` between 0.2 and 0.8).

Why these numbers, fixed before any sweep result: a pure fixed cost has `s` = 1 and a pure per-element cost `s` = 0.
The bands extend 0.2 to each side, so that up to a fifth of the excess at the study size may be of the other kind.
On the Neoverse-N2 ladder `s` = 0.8 is a growth `G` of 1.18 and `s` = 1.2 a growth of 0.87: a fitted excess at d = 52
between 13% below and 18% above the fitted excess at d = 12 is "the same". These are round numbers that keep the three words apart; they
were not tuned on a measurement. "falls" starts where the fitted excess at d = 52 is more than about 13% below the one
at d = 12. A result between the bands is "neither" and is reported as a mixture (`s` between 0.2 and 0.8) or as a
failure of the model. The 0.10 of condition 6 is ten percent of a build's time per inner call, far above the few
tenths of a percent by which the harness's timings spread at L1, and chosen to leave room for the irregularity of a
short loop (see "Changes made before any run"), so a failure of that condition means the model `a + b*d` does not
describe the build (a regime change), not that the timings are noisy.

**Headline word.** The word of the as-compiled column, if the aligned column gives the same word. If the two
columns give different words, the headline is "neither" and both words are stated: moving the loops is the control
that was varied, and a word that does not survive it is not claimed. A headline of "too few jobs" needs no second
column.

**Placement, as in `criteria-v3`.** For every d the statistic of `v3.placement_sensitive` is computed: the pooled
`D = exp(mean ln(r_compiled / r_aligned))` with its two-level interval, and whether the hot loops of NONE and FAST
sit differently against 64-byte windows (from the recorded loops; the binaries are the same for every d, so this
part is one yes or no for the sweep). A d for which both hold is listed as placement-sensitive. Two limits of this statistic: the placement fields of the
harness were defined for x86 fetch windows, and 64-byte windows were not examined on Neoverse-N2; and the layout A/A
(NONE against NONE at another loop alignment) is not timed here, because `arm64/README.md` found that it does not see
the shifts that the statistic D shows. Unlike a forward
cell in `criteria-v3`, it is not excluded from the fit: the fit is about the shape in d, not about a level, and the
agreement of the aligned column is the check.

**Reported, and deciding nothing.** The pooled ratio and interval of every timed d in both columns, the pooled excess
in ns per inner call at every d, the between-job spread; the growth `G` and the parts `kappa` and `lambda*d_max` with
intervals; the `y` view (`1 / (R - 1)` on d with its slope and dilution `Q`, the statistic of the first draft) and the
inverse view (`R - 1` on `1/d`); the residue scan; the bridge; the study L2 point; the Cachegrind difference per
inner call and its fit; the placement list; the ratio at the study L1 d next to the published 1.548 (a sanity
reading, not a criterion). Whichever of these disagrees with the headline word is stated beside it.

## Records

- Every `dsweep.json` stores the SHA-256 of this plan, of `harness/criteria-v3.json`, and of each file in
  `CODE_FILES` of `dsweep/analyze.py` (the sweep and analysis code, the harness modules it uses, the kernel and
  `kernels/common.hpp`), line endings read as LF, together with the commit (`run.commit`, the workflow's `GITHUB_SHA`).
  Jobs of one CPU model that ran different code are a file problem, so both x86-64 runs are started from one commit.
  The pooled output records the hashes of the files as they stand when the analysis runs and prints a note when they
  differ from those of the jobs; that is not a file problem, but it is shown beside the verdict.
- While a job runs it appends every finished d to `dsweep.partial.jsonl` (removed when `dsweep.json` is written). A job
  that stops or is cancelled after its first timing leaves that file in its artifact; the analysis lists it and does
  not pool it.
- The order of events can be checked in two places. In the private working repository, the commit of this file
  precedes every Actions run and the commits of the code. In the public repository, whose history is one squashed sync
  commit, only the creation time of each Actions run and the plan hash stored in each file remain; the hash shows
  which text the run saw. The first public push should contain this file alone, before the workflow and the code.
- Nothing about a run is edited after the fact: the numbers of the rule are in this file (below) and in `RULE` in
  `dsweep/analyze.py`, and `tests/test_dsweep.py` checks that the two agree.

## Runs

- A test of the code comes first and is never pooled: `jobs = [1]` on each runner, and a smoke run
  (`-f reps=4`, which marks every file as a smoke file; the analysis refuses it).
- Neoverse-N2: `gh workflow run dsweep.yml -f runner=ubuntu-24.04-arm`, once, 6 jobs.
- x86-64: `gh workflow run dsweep.yml`, twice, 6 jobs each, from one commit, pooled per CPU model across the two runs
  (`python3 dsweep/analyze.py <run folders>`); a model with fewer than 3 jobs is listed as "too few jobs".
- A job that fails or is cancelled is listed and not replaced. If, in a run, no job's artifact holds a `dsweep.json`
  (every job stopped before it finished; the artifacts hold at most `dsweep.partial.jsonl`), that run is a failed test
  of the code and not a measurement: the defect is fixed, the fix is committed with this plan unchanged, and the run
  is started again. The partial files are kept and listed in the report; they may be read to find the defect and for
  nothing else, and no rule, number or ladder is changed because of them. Once any job of a run has produced a
  `dsweep.json`, that run is a measurement and is not repeated.
- Every job that returns a `dsweep.json` is pooled, whatever it says. No run is started, repeated or added to change
  a verdict. If a CPU model's headline is "neither" or "too few jobs", that is the result.

## What the sweep cannot show

- It reads no hardware counters. It cannot say where the cycles go; the Cachegrind counts are instructions, not time.
- One kernel (i-k-j matrix multiply, int32), one compiler (clang 18.1.3 with libc++ 18, hardening mode FAST) and
  one flag set (`-O2`, no `-march`). Nothing here is said about other compilers, libraries or cores.
- Runners are shared. The machine a job lands on is drawn by GitHub; the pinned CPU shared a core with the driver
  in 8 of the 10 jobs of the environment recording (`environment/`); no steal time or frequency is recorded per timing.
- The fit covers a d range of a factor of 3 to 4.3 inside L1. A mixture is placed by its share `s` and called
  "neither" between the bands; a fixed part that is small next to the excess is not told from a per-element cost,
  which is what `s` near 0 means.
- It does not time the study L2 size more than once and fits nothing outside L1. The bridge and the residue scan
  show where the excess goes between the two published cells; they do not explain why.
- "falls" is only called for a fall that a straight line describes. On generated data a fall as `d^-0.2` to `d^-0.5`
  over the fit ladder is "falls", and a steeper one is curved enough to fail condition 6 or 7 and end as "neither".
  The stored fall between d = 52 and d = 209 is much steeper than that (about `d^-1.5`), but it spans the L1 to L2
  boundary, which the fit does not. If the excess falls steeply inside L1, the result is "neither" with its reason and
  the pooled excess per d, which is the thing to read.
- The per-call overhead that is the same in both builds (the call, the timer reads) is in every measured time. At
  d = 12 a kernel call makes only 144 inner calls, so this overhead weighs more there than at d = 52 and slightly
  lowers the ratio at the small d.
- **The x86-64 runs are a weak control.** There the loop loses SIMD under FAST: the NONE loop is vectorized (8
  elements per pass) and the FAST loop is scalar, so neither the fixed-cost account nor the per-element account is
  written for it. The runs apply the same rule. Expectation, not a criterion: "H2" (a loop that lost its SIMD pays on
  every element) and not "H1". The control is weak for three reasons. A per-element loss reads as "not H1" under almost
  any rule. A shared runner's A/A (0.3% to 3% at other cells) may end a model's word at condition 3 before the shape is
  read. A NONE vector loop that is not entered at the smallest d (12 or 13: one pass and the leftover elements) is a
  change of regime that condition 6 reports as "neither", whatever the check does. If the rule returned "H1" for a loop
  that lost its SIMD, that would be reported as a failure of the rule to tell a lost vector loop from a fixed cost,
  not as a finding about the check.
- The result is the result of these runs; it is not an average over Arm cores or a statement about Apple silicon or
  Graviton.

## The numbers of the rule, as the code reads them

`tests/test_dsweep.py` compares this block with `RULE` in `dsweep/analyze.py`.

```json
{"minimum_jobs": 3, "aa_half_width_max_pct": 2.0, "minimum_fit_points": 4, "baseline_max_relative_residual": 0.10,
 "excess_max_relative_residual": 0.15, "undefined_resamples_max_fraction": 0.025, "h1_share_band": [0.8, 1.2],
 "h2_share_band": [-0.2, 0.2], "falls_share_above": 1.2}
```
