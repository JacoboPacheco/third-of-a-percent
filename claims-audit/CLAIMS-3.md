# Claims audit 3: real programs timed

Source recomputed: 24 job files under results/realworld-3840*/ hash to 12 distinct sha256 (10 on EPYC 7763: 4+3+3 per run; 2 on EPYC 9V74), so 12 jobs is right. Per-job median ratios, geometric mean over the 10 EPYC 7763 jobs, matched the pooled file to 4 decimals for all 8 rows x 3 pairs (fast, aligned, aa). Interval widths not re-bootstrapped (pool.py logic reused unchanged).

| Claim | Class |
|---|---|
| 12 jobs, 3 runs, 10 on 7763, 2 on 9V74, 9V74 has no reading (<3 jobs) | SUPPORTED |
| Table 9 ratios, A/A floors, readings (8 rows) | SUPPORTED |
| 5 of 6 detectably slower, 1.2% to 7.5% across both columns | SUPPORTED |
| Spectra and meshoptimizer "at most 0.5%" (0.53, 0.48) | SUPPORTED |
| fmt 1.5% to 5.5% faster; layout A/A 1.029 [1.015, 1.039] | SUPPORTED (labelled placement, "not explained, not interpreted"; the word placement rests on the layout A/A only) |
| 5 of 8 expectations held (rule recomputed from realworld.json) | SUPPORTED |
| Lost-loop line shares 0.0002% to 6.3%, functions up to 16.4% | SUPPORTED |
| Amdahl: linear estimate +44% vs measured 3.7% | SUPPORTED (labelled estimate) |
| realworld/README: extra instructions 53.7% (functions) / 0.4% (lines) for lightgbm_linear | SUPPORTED (recomputed from profile instructions and shares) |
| "on the binaries that were timed" (Table 5 caption, Figure 6 note), no approximate marks | CONTRADICTED: context.builds shows lightgbm none vs none_g and fast vs fast_g text hashes differ; only LightGBM. Fixed: wording and approximate flag restored for LightGBM rows (marked with the approximation sign) |
| README / DETAILS: "the lost loops hold under 1%" for four programs | OVERSTATED for tiny-dnn (lines 0.03%, its functions 16.4%, cost 2.9 to 3.6%). Fixed: says "own lines", names the 16% for tiny-dnn |
| realworld/README: "under 0.5% on their own lines" | OVERSTATED (multiclass 0.507%). Fixed: "about 0.5% or less" |
| realworld/README: tiny-dnn "0.07%" on lost-loop lines | STALE (0.07 is the FAST share; NONE 0.03% used elsewhere). Fixed |
| "no mechanism is claimed" text, "consistent with ... checks elsewhere" | SUPPORTED as hedged (no mechanism for the whole-program cost is asserted; fmt faster is not interpreted) |

Counts: SUPPORTED 10 groups (about 60 numbers), OVERSTATED 2, CONTRADICTED 1, STALE 1.

## Stale statements found elsewhere (outside this audit's files; not edited)
- The project status notes said real-program timing was blocked until a quota reset: stale, timing is done.
- gaps/GAPS.md line 68 ("realworld/ puts lost loops at about 0 to 6 %") fine, line 97 job 9 "Time the real programs (Actions)" is stale (done, on the public repo run).
- The day-one plan and the project gotchas said "real programs not built against libc++ hardening": old, superseded by day-one results.
No remaining "not timed" about the six real programs in README, site, details, DETAILS.md, realworld/README. No "24 jobs", "20 jobs" or 4-job 9V74 statements remain.
