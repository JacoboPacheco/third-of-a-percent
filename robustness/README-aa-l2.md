# The identical-binary A/A at L2, pooled per CPU model

Every number in this document sits in a block that `robustness/aa_l2.py --report` writes from the stored files. The
prose around the block states no number; `tests/test_aa_l2.py` checks that, and checks each qualitative sentence below
against `robustness/aa-l2.json`.

## What was computed

`harness/run.py` times one identical-binary A/A pair per job: the unchecked `k02_add_fwd` binary against a byte-identical
copy of itself. The pair at the L1 size is `controls.aa` in each job's `results.json`; `harness/pool.py` pools it per CPU
model, and `harness/criteria-v3.json` reads it: an A/A half-width above the ceiling ends a verdict at INCONCLUSIVE, and
twice that half-width sets the forward limit. The same identical-binary pair is also timed at the L2 size and kept in
each job's `details.json` under `aa_extra`. No rule, table or figure read it.

`aa_l2.py` pools that second pair per CPU model with `harness/pool.py`'s `pair_stat` (read-only use: the same two-level
bootstrap over jobs and repetitions, the same generator), beside the L1 pair, for four stored pools: the x86-64 pool the
page reads (`s7`), the x86-64 replication set (`s9-x86-c`), the Arm pool (`s8-arm`) and the Arm replication set
(`s9-arm-b`). It also lists every `aa_extra` key found under `results/` and `versions/results/`, and pools the one other
key that exists (a RAM pair in some early-stage jobs outside every pool) per CPU model, for description only.

How the numbers are made:

- The L1 pair is pooled under the statistic id `aa`, as `harness/pool.py` pools it; the recomputed block must equal the
  stored `aa` block of the pooled file for every model (`l1_matches_pool`), which also shows that the job set read here is
  the pool's.
- The L2 pair is pooled under `aa_extra|k02_add_fwd.L2`, the id `scripts/build_site_data.py` already uses for the Arm
  pool's L2 pair, so the Arm figures here are the ones `arm64/README.md` prints.
- A row whose pooled L2 half-width lies within a factor of two of the ceiling is pooled again under other seeds
  (`l2_seed_sensitivity` in the data) to show how far the number moves with the random draws alone.
- Per-job half-widths are the stored ones (`stats.summarize`, written by the harness); `--verify --deep` re-bootstraps them
  all.
- "Jobs above the ceiling" counts per-job half-widths strictly above the ceiling, the comparison the rule makes. The rule
  itself reads the pooled half-width of a CPU model, not a per-job one, and no job is excluded on its own A/A.
- A model with fewer than the minimum number of jobs is listed and flagged; its numbers decide nothing.

## The numbers (generated)

<!-- aa-l2:begin -->
### Noise of an identical binary, L1 against L2 (generated)

The pooled A/A half-width is the half-width of the 95% interval of the pooled ratio of a binary to a byte-identical copy of itself (`harness/pool.py`, two-level bootstrap). The ceiling the written rule reads at L1 is 2%.

| pool | CPU model | jobs | L1 pooled half-width % | L2 pooled half-width % | L2 / L1 | L2 pooled ratio [95% interval] | L2 per-job half-width % median / max | jobs above 2% at L1 / L2 | L2 between-job sd % |
|---|---|---:|---:|---:|---:|---|---|---|---:|
| s7 | AMD EPYC 7763 64-Core Processor | 29 | 0.070 | 0.361 | 5.2 | 0.9982 [0.9948, 1.0021] | 0.43 / 3.39 | 0 / 6 | 0.79 |
| s7 | AMD EPYC 9V45 96-Core Processor | 23 | 0.200 | 0.214 | 1.1 | 0.9994 [0.9972, 1.0015] | 0.67 / 1.84 | 0 / 0 | 0.27 |
| s7 | AMD EPYC 9V74 80-Core Processor | 28 | 0.055 | 0.338 | 6.2 | 0.9994 [0.9961, 1.0028] | 1.14 / 1.91 | 0 / 0 | 0.76 |
| s7 | INTEL(R) XEON(R) PLATINUM 8573C | 7 | 0.691 | 0.376 | 0.5 | 1.0002 [0.9966, 1.0041] | 0.70 / 1.38 | 1 / 0 | 0.32 |
| s7 | Intel(R) Xeon(R) 6973P-C | 7 | 0.543 | 2.341 | 4.3 | 1.0099 [0.9856, 1.0325] | 1.75 / 15.44 | 2 / 3 | 2.35 |
| s7 | Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz (too few jobs) | 1 | 0.155 | 0.037 | 0.2 | 0.9999 [0.9995, 1.0003] | 0.04 / 0.04 | 0 / 0 | n/a |
| s9-x86-c | AMD EPYC 7763 64-Core Processor | 19 | 0.050 | 0.478 | 9.5 | 0.9981 [0.9931, 1.0026] | 0.69 / 3.16 | 0 / 5 | 0.71 |
| s9-x86-c | AMD EPYC 9V45 96-Core Processor | 5 | 0.530 | 0.539 | 1.0 | 0.9996 [0.9944, 1.0052] | 0.90 / 1.62 | 0 / 0 | 0.35 |
| s9-x86-c | AMD EPYC 9V74 80-Core Processor | 7 | 0.052 | 0.452 | 8.7 | 0.9984 [0.9940, 1.0030] | 0.88 / 1.09 | 0 / 0 | 0.53 |
| s9-x86-c | INTEL(R) XEON(R) PLATINUM 8573C | 7 | 0.322 | 0.293 | 0.9 | 0.9999 [0.9977, 1.0036] | 0.37 / 1.44 | 0 / 0 | 0.22 |
| s9-x86-c | Intel(R) Xeon(R) 6973P-C (too few jobs) | 1 | 0.781 | 0.654 | 0.8 | 1.0056 [0.9983, 1.0114] | 0.62 / 0.62 | 0 / 0 | n/a |
| s9-x86-c | Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz (too few jobs) | 1 | 0.326 | 0.038 | 0.1 | 1.0000 [0.9996, 1.0003] | 0.04 / 0.04 | 0 / 0 | n/a |
| s8-arm | Neoverse-N2 | 30 | 0.009 | 2.621 | 292.6 | 1.0014 [0.9751, 1.0275] | 11.69 / 16.73 | 0 / 24 | 4.94 |
| s9-arm-b | Neoverse-N2 | 29 | 0.009 | 2.897 | 318.4 | 0.9862 [0.9607, 1.0186] | 12.70 / 17.82 | 0 / 27 | 6.63 |
| s9-arm-b | Neoverse-V3 (too few jobs) | 1 | 0.043 | 0.938 | 21.8 | 1.0088 [0.9952, 1.0139] | 0.98 / 0.98 | 0 / 0 | n/a |

### The written A/A clause read at L2 (generated)

| pool | CPU model | jobs | stored word | L2 pooled half-width % | above the 2% ceiling | effect if the rule read L2 |
|---|---|---:|---|---:|---|---|
| s7 | AMD EPYC 7763 64-Core Processor | 29 | map | 0.361 | no | none: below the ceiling, forward limit unchanged |
| s7 | AMD EPYC 9V45 96-Core Processor | 23 | map | 0.214 | no | none: below the ceiling, forward limit unchanged |
| s7 | AMD EPYC 9V74 80-Core Processor | 28 | map | 0.338 | no | none: below the ceiling, forward limit unchanged |
| s7 | INTEL(R) XEON(R) PLATINUM 8573C | 7 | inconclusive | 0.376 | no | none: below the ceiling, forward limit unchanged |
| s7 | Intel(R) Xeon(R) 6973P-C | 7 | map | 2.341 | yes | map would become inconclusive |
| s7 | Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz | 1 | inconclusive | 0.037 | no | none: too few jobs for a verdict |
| s9-x86-c | AMD EPYC 7763 64-Core Processor | 19 | map | 0.478 | no | none: below the ceiling, forward limit unchanged |
| s9-x86-c | AMD EPYC 9V45 96-Core Processor | 5 | inconclusive | 0.539 | no | none: below the ceiling, forward limit unchanged |
| s9-x86-c | AMD EPYC 9V74 80-Core Processor | 7 | map | 0.452 | no | none: below the ceiling, forward limit unchanged |
| s9-x86-c | INTEL(R) XEON(R) PLATINUM 8573C | 7 | map | 0.293 | no | none: below the ceiling, forward limit unchanged |
| s9-x86-c | Intel(R) Xeon(R) 6973P-C | 1 | inconclusive | 0.654 | no | none: too few jobs for a verdict |
| s9-x86-c | Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz | 1 | inconclusive | 0.038 | no | none: too few jobs for a verdict |
| s8-arm | Neoverse-N2 | 30 | inconclusive | 2.621 | yes | none: stored word already inconclusive |
| s9-arm-b | Neoverse-N2 | 29 | inconclusive | 2.897 | yes | none: stored word already inconclusive |
| s9-arm-b | Neoverse-V3 | 1 | inconclusive | 0.938 | no | none: too few jobs for a verdict |

### Facts read from the data (generated)

- Read at L2, the ceiling clause would change the stored word of 1 CPU model row(s) with at least 3 jobs: s7: Intel(R) Xeon(R) 6973P-C.
- 3 of 11 such rows have a pooled L2 half-width above the ceiling: s7: Intel(R) Xeon(R) 6973P-C; s8-arm: Neoverse-N2; s9-arm-b: Neoverse-N2.
- s7: 95 jobs in 15 run(s); jobs above the ceiling at L1 / L2: 3 / 9; `aa_extra` keys present in the jobs: `k02_add_fwd.L2`.
- s9-x86-c: 40 jobs in 4 run(s); jobs above the ceiling at L1 / L2: 0 / 5; `aa_extra` keys present in the jobs: `k02_add_fwd.L2`.
- s8-arm: 30 jobs in 3 run(s); jobs above the ceiling at L1 / L2: 0 / 24; `aa_extra` keys present in the jobs: `k02_add_fwd.L2`.
- s9-arm-b: 30 jobs in 3 run(s); jobs above the ceiling at L1 / L2: 0 / 27; `aa_extra` keys present in the jobs: `k02_add_fwd.L2`.
- Under `results/` and `versions/results/` there are 275 `details.json` files; the distinct `aa_extra` keys are `k02_add_fwd.L2`, `k02_add_fwd.RAM` (kernel: k02_add_fwd; sizes: L2, RAM). Folders whose jobs hold no `aa_extra`: `s1-run-38119008371`.
- The RAM pair (`k02_add_fwd.RAM`) exists only in 13 early-stage jobs outside every pool (20 repetitions per side). Pooled per CPU model: AMD EPYC 7763 64-Core Processor 4 job(s), half-width 1.23%, 3 above the ceiling; AMD EPYC 9V45 96-Core Processor 4 job(s), half-width 0.69%, 0 above the ceiling; INTEL(R) XEON(R) PLATINUM 8573C 3 job(s), half-width 3.46%, 2 above the ceiling; Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz 2 job(s), half-width 0.85%, 0 above the ceiling.
<!-- aa-l2:end -->

## What it means, in plain words

- **For most models the L2 pair is much wider than the L1 pair.** On the Neoverse-N2 and on the x86-64 AMD models EPYC 7763
  and 9V74 the identical binary is several times noisier at L2 than at L1, and on the Xeon 6973P-C too. On the EPYC 9V45 and
  the Xeon 8573C the L2 pair is about as wide as the L1 pair or narrower, so for those two models the L1 A/A does not
  understate the L2 noise. The A/A the rules read stands for the forward add at L1 only.
- **Below and above the written ceiling.** The AMD rows and the Xeon 8573C rows stay below it at L2. The Neoverse-N2 rows
  and the Xeon 6973P-C row of the first x86-64 pool are above it, and stay above it under every alternative seed tried.
- **Read at L2, the written ceiling clause would change one stored word.** It is the Xeon 6973P-C row of the first x86-64
  pool, which would go from MAP to INCONCLUSIVE. The Arm rows are INCONCLUSIVE already, for another reason; the AMD rows and
  the Xeon 8573C rows would not move. This is a statement about the rule: no stored verdict, pool or rule file was changed,
  and the verdicts stay what the written rules gave.
- **What this does not show.** It does not say why the L2 pair is noisier on these machines: no hardware counter was read
  and the machines are shared. The pair involves no bounds check, so it measures the machine at that size, not the check.
  It is one kernel (the forward add), one copy of one binary, at one size. A row with few jobs is a coarse estimate of the
  spread between jobs.
- **Where this matters.** An L2 cell on the Neoverse-N2 or the Xeon 6973P-C that is set against the L1 A/A floor is set
  against a floor narrower than the noise an identical binary shows at that size.

## Reproduce

```
python robustness/aa_l2.py             # writes robustness/aa-l2.json
python robustness/aa_l2.py --report    # also rewrites the generated block above
python robustness/aa_l2.py --verify    # recomputes everything; fails on any difference (the file, the README block, the input hashes)
python robustness/aa_l2.py --verify --deep   # also re-bootstraps every stored per-job half-width
```

Nothing here changes `harness/pool.py`, `harness/criteria-v3.json` or any file under `results/`.
