# PGO column for the real programs: plan, written before any PGO build or run

Written Tue Oct 13 2026, 13:3x EDT, committed before the first run of
`.github/workflows/pgo.yml`. No PGO number from this study exists when this file is committed. Every
later change is logged at the bottom with its time and whether any PGO timing existed.

## The question

The expected attack: "Google deploys with profile-guided optimization (PGO); your real-program numbers
are without it." Google's sequel (ACM Queue 2025; see `gaps/GAPS.md`) calls PGO critical because it lets the
compiler move checks out of hot paths. The real-program study (`realworld/`) timed FAST against NONE
with no PGO. This column asks: **with PGO on both sides, does the FAST/NONE cost of the same programs
change?** Answer in either direction is published.

It does not say anything about Google's 0.30 % (a fleet average over services that cannot be inspected from outside), and it
is a different thing from Google's PGO: their profiles come from production traffic; here they come from
the same fixed input that is timed.

## What is built

Per program and per mode (NONE, FAST) separately, in one job:

1. an **instrumented** build (`-fprofile-instr-generate`, mode flag, `-O2`, the census flags of
   `realworld/programs.json`), clang-18 + libc++-18;
2. **training**: the instrumented binary is run once per row of that program with the row's own
   arguments and iteration count 1 (the driver runs its workload once untimed and once timed: two
   passes), one `.profraw` per run, so LightGBM's three rows all train its single binary;
3. `llvm-profdata-18 merge` into one `.profdata` for that program and mode. NONE and FAST each get their
   OWN profile from their OWN instrumented build (the hardening mode changes the control-flow graph, so
   a shared profile would not match);
4. the **PGO build**: the same flags again plus `-fprofile-instr-use=<that profdata>`; and the aligned
   build (the same plus `-falign-loops=64`, using the same profile: alignment does not change the CFG).

Binaries are stored under the names `realworld/measure.py` expects (`<program>.none`, `.fast`,
`.none_a64`, `.fast_a64`), in their own artifact, so the timing is `realworld/measure.py` unchanged:
ABBA, 40 processes per side, `taskset -c 1`, iterations calibrated on the PGO NONE binary, four pairs
(FAST/NONE, the byte-identical A/A copy, the aligned pair, the layout A/A). Pooled per CPU model with
`realworld/pool_rw.py`'s logic, imported unchanged (`harness/pool.py`'s two-level bootstrap).

Rows: the same eight as `realworld/programs.json` (draco, lightgbm_default, lightgbm_multiclass,
lightgbm_linear, tinydnn, spectra, and the controls meshopt and fmt). Same checksums are required:
if outputs differ between PGO NONE and PGO FAST the row gets no ratio (the realworld rule).

Recorded per build: sha256, `.text` sha256, `ud2` count, compile time; per mode: training checksums,
profile size, the clang "profile out of date" and "no profile data" warning counts (a sign that a
profile did not match its source), and the number of census lost locations still vectorized in the PGO
build (so "PGO does not restore SIMD in the lost loops" is shown, not assumed).

## Rules for the claims (fixed now; the same as `realworld/PLAN.md`)

A CPU model needs at least 3 jobs for a reading. With h = the pooled half-width, in percent, of that
row's own byte-identical A/A in the PGO runs:

- **PGO FAST cost detectable (slower)**: the pooled PGO FAST/NONE interval's lower end is above
  1 + h/100 in BOTH columns (as compiled and aligned). **Detectably faster**: the upper end is below
  1 - h/100 in both. Otherwise **not detectable**, "at most X %", X = max(0, 100 x (upper end - 1) over
  the two columns, h). One column only: not detectable, with the column named. This is
  `realworld/common.verdict_row`, imported.

## What the result is compared to

The non-PGO pooled numbers in `results/realworld-pooled/realworld.json` for the SAME CPU model and
the same row (both columns, as compiled and aligned). Each interval is widened by its own row's A/A
half-width before comparing, because the two pools come from different runner draws on different days
and the within-job intervals understate run-to-run spread (audit of S3). Then, per row:

- **PGO lower**: both PGO intervals lie entirely below both non-PGO intervals (cost reduced);
- **PGO higher**: both lie entirely above;
- **no difference detected**: anything else.

Only rows with a reading on both sides, on a CPU model with at least 3 jobs on both sides, are
compared; the others are listed as "not compared" with the reason. `pgo/analyze.py` writes the
tables to `pgo/report.md`. Whatever comes out is published as it is: if PGO removes the cost, the
page says the real-program cost shrinks under PGO on these programs; if it does not, it says that.

## Expectations (written before any build or run; labelled as such, not read as results)

- PGO does not restore SIMD in lost loops (the trap stays inside the loop body: the block is cold,
  the vector loop still needs a bounds-proof it cannot get). Expected: census lost locations stay lost.
- The whole-program cost is expected to shrink or stay about the same where it comes from scalar
  checks outside the lost loops (draco, tinydnn, lightgbm_multiclass), because PGO lays out the trap
  paths cold and removes redundant checks on hot paths; it is not expected to vanish.
- Programs with no detectable cost without PGO (spectra, meshopt) are expected to stay not detectable.
- These are guesses from the compiler's behaviour, not from any measurement.

## Limits (stated now)

- **Training input equals test input** (same fixed seeds, same sizes). That flatters PGO: real PGO
  profiles come from different traffic. A result "PGO removes the cost" is an upper bound on what PGO
  could do; a result "PGO does not remove it" is stronger.
- PGO builds change code layout and inlining; the aligned column and the layout A/A are kept for that
  reason, and the layout A/A (PGO NONE aligned against PGO NONE) is printed beside every row.
- One toolchain (clang 18, libc++ 18), clang's IR-level instrumentation (`-fprofile-instr-generate`),
  not sampling profiles (AutoFDO), no ThinLTO, no BOLT; Google's pipeline uses more than this.
- Shared runners; the CPU model is drawn by luck; non-PGO and PGO runs are not in the same jobs.
- Whole-program wall time stays a labelled sanity measurement, never compared to 0.30 %.

## Budget

At most one build run and as many measure runs of four jobs as the realworld study used (six) if runner
time allows; reported per CPU model with the job count.

## Changes after this file was committed

- Tue Oct 13 2026, 13:5x EDT, no PGO timing or build existed: the header above says 13:3x; the clock read 13:22 when this file was first committed. Build script, workflow, analysis, check and tests were added after it; none changes a rule.
