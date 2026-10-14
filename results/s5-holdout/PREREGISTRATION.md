# Holdout run: written before it starts

Written Tue Oct 13 2026 (by `date` on the author's machine), after every earlier run and before the first run listed below was started.

**What this is.** A confirmation of the pooled per-CPU verdicts on fresh runner draws. Nothing is changed for it:
`harness/criteria-v3.json` and `harness/pool.py` are used exactly as committed (this commit). Its thresholds and rules
cannot be edited for this run, and whatever comes out is published.

**What will be run.** `gh workflow run measure.yml` three times with its default inputs (10 jobs each, sizes L1 and L2,
no programs, 40 processes per side). The three run IDs are written next to this file as soon as they are started.

**What will be reported, per CPU model with enough jobs.** The verdict (and the reverse, stride-2 and matmul cost
intervals) in the original pooled runs against the holdout, side by side, unedited, in `results/s5-holdout/` and on the
page. A verdict that flips, or a CPU model that does not reproduce (EPYC 9V45 is the expected one), is reported as such in
the README limits. A CPU model that was too thin before and is enough now is reported as new, not as a confirmation.

Run IDs (started right after this file was pushed): 38408152157, 38408166458, 38408179322.
