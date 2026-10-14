# Claims audit 4 (input: CLAIMS-4-input.md)

Classes: S supported, O overstated, C contradicted, T stale. Recomputed with separate code (no numpy: per-job median ratio, geometric mean) from the raw files.

## Recomputation
- Layout sweep, raw results.json of run 38440485436: EPYC 7763 k04_rev.L1 placements 7.637, 8.009, 8.009, 7.621 (analysis: 7.621 to 8.009); k02_add_fwd.L1 1.585, 0.834, 0.825, 0.831 (median 0.833); k03_stencil.L1 1.006, 1.053, 1.056, 1.055 (median 1.054); k01 L2 0.998 to 1.001. EPYC 9V74 k04_rev.L1 6.555, 5.377, 8.032, 6.560; k02 L1 1.596, 0.824, 0.824, 0.825. All equal analysis.json. Job counts 3 / 4 / 1 confirmed.
- PGO, raw job files, EPYC 7763 (7 jobs): draco 1.086 (aligned 1.092), lightgbm_linear 1.050 (1.049), spectra 0.997, fmt 0.949 (0.996), lightgbm_default 1.000 (1.006); Xeon 8573C (4 jobs) linear 1.096. All equal pgo.json / report.md. Lost-loop locations: 12+0+38+0+1+2 = 53; vectorized with checks off 8+11 = 19, with checks on 0+1 = 1.
- lostloops live: comparison.json of leveldb, Spectra, LightGBM: pass true, lists/details/checks/totals all empty (equal), clang 18.1.3; logs end RESULT ... PASS.

## Classified
| Claim | Class | Note |
|---|---|---|
| Job counts, placements, step, residues, reps, rule thresholds, earlier 16-placement attempt (run 38439008261, amendment 1 committed 13:39 before the run) | S | PLAN.md amendment and git log agree |
| Reverse loop 7.62 to 8.01 (7763), 5.38 to 8.03 (9V74); forward sum 0.998 to 1.001; forward add 0.82 to 1.60, 1.585/0.833, 1.596/0.826; stencil L1 1.054, 1 of 4 pass, aligned 1.056; Xeon 1 job, 1.166 to 1.231, A/A up to 8.63% | S | recomputed |
| "the reverse loop ... so that side of the result does not depend on placement" (page 3b) | O | the loss holds at every placement but its size ranges 5.4 to 8.0x on 9V74; reworded to "the loss itself ... (the size of the cost does, within that range)" |
| README "the stencil 1.05x at one placement" | C | the stencil costs 1.05x at three of four placements (1.053, 1.056, 1.055), only p00 passes (1.006); fixed to "three of four" |
| Page, README, DETAILS: only the forward sum is robust (kernels over all cells) | S | stencil L2 on 7763 and L1 on 9V74 are ROBUST; the input list already notes it |
| Per-model forward claim (7763 placement-dependent, 9V74 mixed, Xeon inconclusive) | S | analysis.json |
| PGO table values P1, runs and jobs (12 jobs, 7/1/4; non-PGO 16/3/none), 8 rows, 6 programs, traps, builds line, 19 and 1 of 53 | S | recomputed; report.md |
| PGO vs non-PGO on 7763: lower 1, higher 2, none 5 | S | rule in pgo/PLAN.md (intervals widened by A/A); lightgbm_default 1.018 vs 1.000 reads "no difference" because of that widening, which the plan states |
| "PGO does not remove the cost" (DETAILS 51), "did not make the cost vanish" (README, page 215 and rwLimits, realworld/README, related rows) | O | LightGBM default fell from 1.018 to 1.000 (not detectable); four of the five rows with a detectable cost kept it. Reworded "in most rows" / "four of the five rows" |
| "PGO did not bring SIMD back" / "lost loops stay lost" | O | 1 of 19 locations vectorized with checks on (LightGBM); reworded "almost everywhere / almost all" |
| Training input equals timed input, flatters PGO; instrumented profiles, no sampling, no LTO (PLAN.md line 94 says no ThinLTO, no BOLT) | S | caveat present on page 7c limits, README ("trained on the timed input"), DETAILS, realworld/README, related rows |
| Related row "samples only two layouts, not many" (build_site_data.py, related.json) | T | section 3b now adds four placements; reworded |
| lostloops live test: 3 projects, run 38438713384, clang 18.1.3, lists equal to the census; "one run, not a guarantee" | S | recomputed; README, DETAILS, tools/lostloops/README agree. Its other README sentences ("tested on saved real compiler output") still hold |
| Front matter: title, date line "Oct 2026", author JacoboPacheco, "Code written by AI coding agents directed by the author" | S | same disclosure as the README status line |
| BibTeX @misc | S | braces balanced, fields comma separated, year 2026; its url pointed at a repository that answered 404 at the time (flagged, not edited) |
| Ref [1] Google Security Blog, Nov 15 2024 | S (title, date) | loaded: title "Retrofitting spatial safety to hundreds of millions of lines of C++", Nov 15 2024. The article body did not load, so the 0.30% sentence and "PGO further improved" were NOT re-verified here |
| Ref [2] ACM Queue id 3773097 | not verified | HTTP 403; authors, volume and the "five services" figures unchecked |
| Ref [3] NADER PDF | not verified | PDF is compressed, text unreadable by the fetcher; only the DOI 10.1145/3485480 (ACM) showed; 76.4% unchecked |
| Ref [4] NIST PMC4487316 | not verified | page showed a bot check; not bypassed |
| Ref [5] Readyset blog | S | title matches; 1,227 checks per warm read and "within the noise threshold" confirmed (the author also reports a small slowdown, noise or a real few percent, when 37 indexings were replaced by hand: the row says "every check removed", which holds) |
| Mechanism claims | S | page says the placement mechanism is inferred (section 3, 3b limits, DETAILS); the SIMD mechanism is labelled inferred in the README |
| README 820 words (limit 820), main page phone height | S | check_site --quick passed |

## Stale statements elsewhere (not edited, outside the named files)
- `.github/workflows/layout-sweep.yml` header comment still says 16 placements and "two layouts only"; the run used 4 (coarse).
- Everything else grep found ("not timed", "never run") is correct in context (real-program timing labels, counted-not-timed).

Counts: S 21 (incl. 3 not-verified refs listed separately), O 3, C 1, T 1.
