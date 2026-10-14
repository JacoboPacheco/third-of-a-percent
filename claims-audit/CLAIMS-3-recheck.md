# Claims 3, recheck against all three CPU models (Tue Oct 13 2026)

Source: `results/realworld-pooled/realworld.json` (24 distinct jobs in 6 runs: AMD EPYC 7763 16 jobs, EPYC 9V45 5 jobs, EPYC 9V74 3 jobs; minimum for a reading 3). Per-CPU rows, columns "as compiled" (`pairs.fast`) and "aligned" (`pairs.aligned`), reading = the stored `reading.reading` (detectable only if both columns clear that model's A/A floor, rule in `realworld/PLAN.md`). The six programs with lost loops are LightGBM (default, multiclass, linear), Draco, tiny-dnn, Spectra.

## Finding

The claim "1.2% to 7.5% slower for five of six real programs" holds on EPYC 7763 only. The audit was right: on the two other models tiny-dnn and others are not detectable.

| CPU model (jobs) | detectably slower | range, both columns | not detectable (at most) |
|---|---|---|---|
| EPYC 7763 (16) | 5 of 6: LightGBM default, multiclass, linear; Draco; tiny-dnn | 1.2% to 7.5% (1.0115 to 1.0754) | Spectra (0.5%) |
| EPYC 9V74 (3) | 4 of 6: LightGBM default, multiclass, linear; Draco | 0.7% to 7.1% (1.0073 to 1.0713) | tiny-dnn (1.2%), Spectra (1.6%) |
| EPYC 9V45 (5) | 3 of 6: LightGBM default, multiclass; Draco | 2.3% to 5.4% (1.0233 to 1.0540) | LightGBM linear (8.4%; aligned column 1.078), tiny-dnn (19.3%; 0.934 as compiled, 1.186 aligned), Spectra (2.1%) |

Controls: meshoptimizer not detectable on all three models; {fmt} detectably faster on 7763 (1.5% to 5.5%, aligned build moves it by itself, placement effect, not explained) and 9V74, not detectable on 9V45. With 3 and 5 jobs the intervals understate the spread between machines.

## What changed

- `README.md`: the real-programs bullet now states the per-model counts and ranges; "(one CPU model ...)" removed; first-person wording made neutral; status line, "Words used here" and the SIMD-mechanism sentence added.
- `readme-parts/DETAILS.md`: the real-programs bullet rewritten per model ("10 of 12 jobs" and "one CPU model" removed; "five of six holds on EPYC 7763 only"); note that run links in the raw records are dead for outsiders.
- `realworld/README.md`: status line (24 jobs, three models, per-model counts); "a second CPU model with enough jobs" in the not-shown list replaced.
- Page: section 7 status line, finding line ("On AMD EPYC 7763, 5 of the 6 ...") and a new per-model paragraph (`#rw-other`) computed from the data; details page Table 10 (EPYC 9V45), new Table 10c (EPYC 9V74), limits line; the main-page summary says the five is for EPYC 7763.
- `scripts/check_site.py`: recomputes the per-model counts, ranges and at-most bounds from the data and asserts the page text equals them; Table 10c row count.
- Not changed: the 7763 numbers in Table 9, the expectations table (checked against 7763, 5 of 8 held), `harness/criteria*.json`, raw results.

## Not checked

Whether the 9V74 and 9V45 readings would be stable with more jobs (3 and 5 jobs); the cause of the {fmt} speed-up.
