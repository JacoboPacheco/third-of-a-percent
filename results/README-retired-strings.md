# A retired sentence in the older records

Some of the older run records in this folder still contain a sentence that starts "Google's 0.30% holds for forward loops ...". It is in the `verdict.line` (and, in `combined.json`, the page-level `line`) of:

- `fixture.json` (SAMPLE data, not a measurement);
- the S3 runs: `s3-run-38120895740/`, `s3-run-38121166129/`, `s3-run-38121825636/` and `s3-audit-run-38127024171/` (their `combined.json` and the per-job `results.json` whose per-job verdict was MAP).

The S1 and S2 records (`s1-run-38119008371/`, `s2-run-38119607308/`) came from the same harness template, but their verdicts were INCONCLUSIVE, so the sentence was never printed there.

**This sentence is not a claim of this project.** It was the harness's automatic wording for the MAP verdict at the time, and it was retired. The pooled S4 records (`s4-run-*/`, `s4-pooled/`) and the page's data use the current wording, which states only the measured ratios. The project measures single loops on shared GitHub runners; it makes no claim about Google's services or about whether Google's 0.30% average is right or wrong.

The old records are kept exactly as the runs wrote them, because `python scripts/check.py` recomputes each stored verdict from its raw samples and the record must not be edited after the fact. Read their `verdict.line` as "every judged forward cell stayed within the forward limit and every lost-SIMD cell stayed above 1.5x", nothing more.
