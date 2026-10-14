# Claims audit 4: input (every new number and where it appears)

Sources: `layout-sweep/results/38440485436/analysis.json` (rules `layout-sweep/criteria.json`, `layout-sweep/PLAN.md` amendment 1), `results/pgo-pooled/pgo.json` (with `results/realworld-pooled/realworld.json` as the non-PGO baseline; rendering `pgo/report.md`), `results/lostloops-live-38438713384/`. Page numbers are built into `site/data/layout.json` and `site/data/pgo.json` by `scripts/build_site_data.py`; the page prints them from there. "Page" = `site/details.html` (sections 3b and 7c), "README" = `README.md`, "DETAILS" = `readme-parts/DETAILS.md`.

## Layout sweep

| Number | Value (source) | Appears in |
|---|---|---|
| Job counts per CPU model | EPYC 7763 3, EPYC 9V74 4, Xeon 6973P-C 1 (minimum 3, so Xeon inconclusive) | Page 3b (intro, limits, tables); DETAILS |
| Placements, step, residues | 4 placements, 16-byte steps, loop start at 0, 16, 32, 48 modulo 64 (coarse mode) | Page 3b; README ("4-placement sweep"); DETAILS |
| Repetitions, sizes | 20 per side, L1 and L2, 4 kernels | Page 3b |
| Rule thresholds | point ratio at most 1.02; interval ceiling 1.02 or 2 x A/A half-width; robust = 4 of 4, placement-dependent = at most 1 of 4; lost control = 4 of 4 with lower bound at least 1.5 | Page 3b (intro) |
| Earlier attempt | 16 placements, probe aborted (run 38439008261), no timing; amended to 4 before any timing | Page 3b (intro); DETAILS (indirectly: coarse mode) |
| Reverse loop, all placements | EPYC 7763 7.62 to 8.01, EPYC 9V74 5.38 to 8.03 (both sizes) | Page 3b ("5.4 to 8.0x", tables L1, L2); README ("5.4x to 8.0x"); DETAILS ("7.6x to 8.0x", "5.4x to 8.0x") |
| Forward sum | min 0.998, max 1.001, ROBUST in all four cells with enough jobs | Page 3b; DETAILS ("0.998 to 1.001"); README ("only the forward sum is robust") |
| Forward add | min 0.824, max 1.596 over both models and sizes (MIXED); README and DETAILS round to 0.82 and 1.60 | Page 3b; README ("0.82x to 1.60x"); DETAILS |
| Forward add at L1, as compiled and aligned | 7763: 1.585 and 0.833; 9V74: 1.596 and 0.826 (refs `ref` and `a64`) | Page 3b (finding, tables); DETAILS |
| Stencil at L1 on 7763 | median 1.054, 1 of 4 placements pass, aligned 1.056, PLACEMENT_DEPENDENT | Page 3b (finding, table L1); README ("1.05x"); DETAILS |
| Other stencil cells | 7763 L2 ROBUST; 9V74 L1 ROBUST, L2 MIXED (max 1.047) | Page 3b tables only |
| Xeon 6973P-C | 1 job; forward add L1 1.166 to 1.231; A/A half-widths up to 8.63 % | Page 3b table L3 (rows), limits sentence names the 1 job |
| Per-model forward claim | 7763 placement-dependent, 9V74 mixed, Xeon inconclusive; reverse control holds on both EPYC | Page 3b table captions |

## PGO column

| Number | Value (source) | Appears in |
|---|---|---|
| Runs and jobs | 12 distinct jobs in 3 runs (38440131645, 38440143122, 38440153847), build run 38438892253; 7763 7 jobs, 9V74 1, Xeon 8573C 4; non-PGO pool 7763 16, 9V74 3, none for the Xeon | Page 7c (intro, limits, captions); DETAILS |
| Rows and programs | 8 rows, 6 programs, all built with PGO (`pgo/PLAN.md`), each mode profiled separately | Page 7c intro; DETAILS |
| EPYC 7763 PGO FAST/NONE, as compiled | LightGBM default 1.000 (not detectable, at most 0.92 %), multiclass 1.022, linear 1.050, Draco 1.086, tiny-dnn 1.031, Spectra 0.997, meshoptimizer 1.007, {fmt} 0.949 (faster) | Page 7c table P1; DETAILS |
| EPYC 7763 PGO, range of the four detectable rows | 1.016 to 1.092 across both columns | Page 7c finding; README ("did not remove the cost") |
| PGO against non-PGO on 7763 | lower in 1 row, higher in 2, no difference detected in 5 | Page 7c finding; DETAILS |
| Lost-loop locations | 53 listed; 19 vectorized in PGO NONE builds, 1 in PGO FAST builds | Page 7c finding and builds line; DETAILS |
| PGO build traps | draco 32 and 457, fmt 0 and 5, lightgbm 3 and 1337, meshopt 0 and 2, spectra 0 and 27, tinydnn 3 and 151 (PGO NONE and FAST) | Page 7c builds line |
| EPYC 9V74 and Xeon 8573C | 1 PGO job (9V74) and no non-PGO counterpart (Xeon): shown, not read | Page 7c limits, tables P2, P3 |
| Training input | equals the timed input (flatters PGO); instrumented profiles, no sampling profiles, no link-time optimization | Page 7c limits; README; DETAILS; `site/data` related-work rows |

## Other

| Number | Value (source) | Appears in |
|---|---|---|
| lostloops live test | 3 projects (leveldb, Spectra, LightGBM), run 38438713384, Ubuntu clang 18.1.3, lists equal to the census; offline recomputation `tools/lostloops-live/check.py` | README; DETAILS; `tools/lostloops/README.md` |
| profdata removal | 36 files, 12 distinct sha256, about 161 MB removed from `results/pgo-pooled/`; hashes in `results/pgo-pooled/profdata.sha256.txt` | commit message only |
| README length | 818 words (limit 820) | `README.md` |
| Main page length at 390 px | 13191 px (limit 13228) | `scripts/check_site.py` |

## Claims in prose to check against the above

- "The reverse loop does not depend on placement" (Page 3b, README): holds on the two EPYC models only; the Xeon (1 job) is inconclusive, with 3.7 to 6.8x.
- "Only the forward sum is robust" (README, Page 3b): the forward add and the stencil are MIXED or PLACEMENT_DEPENDENT; the stencil at L2 on 7763 and at L1 on 9V74 is ROBUST, so the statement is about the kernels over all cells, not every cell.
- "PGO did not remove the cost" (Page 7c, README, related-work rows): one CPU model with a reading; LightGBM default is the exception (not detectable).
- "The brief said only some rows were built with PGO": `pgo/PLAN.md` and `pgo/report.md` show all eight rows (six programs) were built and timed with PGO; the page says eight rows.
- "Aligned is not the cheap placement for the stencil" is stated through the table values (aligned 1.056 against median 1.054 on 7763 L1), not as a mechanism.
