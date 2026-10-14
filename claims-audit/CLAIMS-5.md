# Claims audit 5: the click-first redesign text

Classes: S supported, O overstated, C contradicted, T stale. Own recomputation from the raw job files (per-job median ratio, geometric mean over jobs; no bootstrap), compared with site/data/*.json and the widgets' sidecar. Every non-S row was fixed with the smallest edit; the fix is in the note.

## Recomputed
- Hero ratios, aligned, L1, from results/s4-run-*/results-*/results.json: EPYC 7763 reverse 8.0141 (19 jobs), EPYC 7763 forward sum 0.99978 (19), EPYC 9V45 forward add 0.83678 (5), EPYC 9V74 reverse 5.37936 (5), Xeon 8573C forward add 1.05867 (1 job). All equal site/data/pooled.json to every digit.
- Programs widget, results/realworld-pooled job files (deduplicated by sha256): EPYC 7763 Draco as compiled 1.07539 (16 jobs), EPYC 7763 LightGBM default aligned 1.01152 (16), EPYC 9V45 LightGBM multiclass as compiled 1.04256 (5), EPYC 9V74 tiny-dnn aligned 0.99865 (3). PGO side, results/pgo-pooled: EPYC 7763 Draco as compiled 1.08655 (12), EPYC 9V74 Draco 1.08970 (5), EPYC 7763 LightGBM linear aligned 1.04845 (12). All equal realworld.json and pgo.json.
- Placement widget, layout-sweep job files: EPYC 7763 forward add L1 p00 1.58477 (8 jobs), EPYC 7763 stencil L1 p01 1.05309 (8), EPYC 9V45 forward add L1 p00 0.97732 (4). All equal placements.json.

## Classified
| # | Claim | Class | Note |
|---|---|---|---|
| 1 | Hero: "Google reported 0.30% on average" | S | claim.google_pct, linked to the blog post |
| 2 | Hero: clang 18.1.3, libc++ 18.1.3 | S | index.json toolchain: clang 18.1.3 (1ubuntu1), libc++-18-dev 1:18.1.3 |
| 3 | Hero: FAST mode, -O2 | S | toolchain common_flags; every build uses the FAST define |
| 4 | Hero: no profile-guided optimization in the main timing | S | PGO only in the separate column |
| 5 | Big ratio, reverse, EPYC 7763: 8.0x | S | recomputed |
| 6 | Big ratio, forward sum, EPYC 7763: 1.00x | S | recomputed |
| 7 | Big ratio, forward add, EPYC 9V45: 0.84x | S | recomputed |
| 8 | Big ratio, reverse, EPYC 9V74: 5.4x | S | recomputed |
| 9 | Intel forward add 1.05 to 1.08 (headline, per job) | S | per-job aligned ratios in index.json intel_forward; Xeon 8573C pooled 1.059 on 1 job |
| 10 | Animation caption: "(aligned build, smallest size)" | O | the hero reads the page's column, which is as compiled when the page opens with that choice or has no aligned data; the caption now names the column in use |
| 11 | Caption: "clamped to stay watchable" | S | ratios outside 0.5 to 4 are clamped and the caption says so |
| 12 | Hero sub-line: "N times as long as with the check off, CPU, J jobs" | S | pooled ratio and job count of the cell |
| 13 | Hero: loop keeps SIMD, check only on the leftover tail; forward sum check removed | S | compiler remarks and assembly, details section 2 |
| 14 | Headline: lost loops 2.8 to 8.0x as long in cache | S | page.lost min 2.797, max 8.014 |
| 15 | Headline: near 1x on AMD, one AVX2 exception, 1.05 to 1.08 on Intel | S | per-model tables; the as-compiled forward add (1.6x) is in the placement section |
| 16 | No-JavaScript text and Result gist: "forward loops that keep it stay near 1x" | O | said nothing about AMD or aligned; Intel is 1.05 to 1.08, as compiled the add is 1.6x on two AMD models; both now say "on the AMD models when aligned" |
| 17 | Gist, placement: slow because of where the code landed, not the check | S | investigate/FINDINGS.md, aligned control, layout sweep |
| 18 | Gist, SIMD | S | definitional |
| 19 | Gist, census: 444 of 4,968 and 1 of 593, counted not timed | S | corpus.json totals |
| 20 | Gist, rewrites: "One up-front size check brings reverse and matrix multiply to 0.99 to 1.09x" | O | the matrix-multiply winner (rowptr) is the check plus raw row pointers behind it; the gist now says so. Range recomputed from the recommended variants: 0.985 to 1.086 |
| 21 | Gist, compilers: clang always loses reverse and strided; GCC differs | S | ce-sweep: 54 of 54 clang rows |
| 22 | Gist, real programs: "1.2 to 7.5% slower with checks on" | O | true for the detectable programs on the model with the most jobs only; reworded |
| 23 | Gists, method, related work, reproduce | S | descriptive |
| 24 | Mitigation widget: "checking the size once before the loop can bring the speed back" | S | "can": recommended variants 0.985 to 1.086; gather has no such rewrite and the widget shows its range |
| 25 | Mitigation widget: "four elements at a time (vectorized)" / "one at a time (not vectorized)" | S | remark width 4 for the int32 kernels; gather is not vectorized in either build |
| 26 | Mitigation belt caption: illustration scaled to the median, yellow marks are checks | S | |
| 27 | Programs widget: EPYC 7763 Draco 1.075 | S | recomputed |
| 28 | Programs widget: EPYC 7763 LightGBM default aligned 1.012 | S | recomputed |
| 29 | Programs widget: EPYC 9V45 LightGBM multiclass 1.043 | S | recomputed |
| 30 | Programs widget: EPYC 9V74 tiny-dnn aligned 0.999, not detectable | S | recomputed |
| 31 | Programs widget with PGO: EPYC 7763 Draco 1.087, EPYC 9V74 Draco 1.090, EPYC 7763 linear aligned 1.048 | S | recomputed (three values) |
| 32 | Programs widget caveats: picked for lost loops, controls contain none, training input is the timed input | S | |
| 33 | Placement widget: "Slide the loop ... how much slower" | O | the widget is four tap targets, and ratios below 1 are faster; the lede now says pick one of four measured positions and reads 1 as no cost |
| 34 | Placement section summary and no-JS line: "placement slider", "slide a loop's start address" | O | same, reworded |
| 35 | Placement widget caption: four measured placements; in-between positions not measured; drawing schematic | S | the bar length is drawn from the extra-window flags, and the widget says so |
| 36 | Placement widget stops: 1.585, 1.053, 0.977 | S | recomputed (three values) |
| 37 | Meta description | S | "recover most of the cost" for the two shapes: 0.985 to 1.086 |
| 38 | OG title and description, twitter card | S | |
| 39 | Page 3b: "its as-compiled placement is the slow one at L1" for the forward add | C | on EPYC 9V45 the as-compiled ratio is 1.002 and every placement passes; the sentence now names the two models where it swings and says 9V45 stays robust |
| 40 | Page 3b: stencil placement-dependent at L1 on 7763, "1 of 4 placements pass" | T | the three-run pool gives 0 of 4 passing and 3 of 4 costing (1.053 to 1.056); the page prints "3 of 4 placements cost" |
| 41 | Page 3b and widget read per-run analysis files next to the pooled one (duplicate CPU rows) | T | build_site_data.py now reads layout-sweep/results/pooled/analysis.json only: one row per CPU model, 8 jobs on 7763 and 9V74, 4 on 9V45, 2 on each Xeon |
| 42 | Page 3b numbers: reverse 5.2 to 8.0x, forward sum 0.999 to 1.007, add 0.824 to 1.596, stencil median 1.054 | S | analysis.json |
| 43 | README, DETAILS layout paragraph: two EPYC models, 3 and 4 jobs, reverse 5.4 to 8.0x | T | rewritten for the pooled analysis |
| 44 | Page 7c: "Only EPYC 7763 has a reading on both sides" | C | EPYC 9V74 has 5 PGO jobs and 3 non-PGO jobs, the minimum; the sentence now covers both models |
| 45 | README, DETAILS PGO paragraph: 12 jobs (7763 7, 9V74 1), "no other model has enough jobs" | T | six runs, 24 jobs: 7763 12, 9V74 5, Xeon 8573C 6, Xeon 8370C 1 |
| 46 | New limits bullet: block bootstrap changes no verdict on 7763 and 9V74; 9V45 fragile | S | robustness/report.md, lag-1 autocorrelation -0.02 to +0.03 |
| 47 | "What this cannot tell you" list | S | |
| 48 | No-JavaScript numbers 2.8 and 8.0 | S | baked from data |

Tally: S 36, O 6, C 2, T 4 (48 claims). All 12 non-S rows fixed.
