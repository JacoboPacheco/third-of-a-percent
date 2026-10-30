"""The measured and counted numbers typed into README.md, readme-parts/DETAILS.md and the Arm column's text must match the stored data.

Each row of ROWS (README.md), DETAILS_ROWS (readme-parts/DETAILS.md), SIBLINGS_ROWS (siblings/README.md), CESWEEP_ROWS
(ce-sweep/README.md), ARM64_ROWS (arm64/README.md), REPLICATION_ROWS (replication/README.md), DSWEEP_ROWS
(dsweep/README.md) and MITIGATE_ROWS (mitigate/README.md) ties one sentence to its source:

    (label, where the value comes from, a function giving the expected text, a regex anchored on
     the words around the number)

The regex has one named group per typed number. The test finds every sentence that matches the
anchor, reads the typed text out of the groups and compares it with the text computed from the
data, rounded the way the README rounds (ratios to one or two decimals, percentages to one).
A new claim in the README is one more row.

Failures say which sentence, what the README types, what the data gives and where the data is.
Two kinds of failure: the anchor no longer matches (the sentence was reworded: update the row or
the sentence) and the typed number differs from the data (fix the README, or the data is stale).

Read-only and offline: only the documents above and the stored files are read.
README_PATH, DETAILS_PATH, SIBLINGS_PATH, CESWEEP_PATH, ARM64_PATH, REPLICATION_PATH, DSWEEP_PATH and MITIGATE_PATH point the test
at other copies (the proof that the guard bites uses a tampered copy).

What this file does NOT tie to data, so that the sentence above is not read as a promise about every number: (1) a sentence
listed in tests/data/guarded_sentences.json is pinned word for word (a caveat, a rule, an order of events, a verdict word), which
catches a rewording or a reversal but says nothing about whether it is true; (2) fewer than half of the digit groups in the prose of
readme-parts/DETAILS.md sit inside a captured group of a row (counted against the rows' spans on Oct 18; many of the others are
in paths, hashes and run ids), and the untied numbers are mostly in these paragraphs: the rule files and their commit hashes, the
Arm paragraph's secondary figures, the ten later runs' timings, Machine state, the first bullets' siblings and Compiler Explorer
sweep counts, the forward-verdict and independence paragraphs' secondary figures, and the d-sweep ladder prose; (3) the typed hashes, run ids and commit times that come from the author's unpublished development history are tied only
where tests/data/*.json records what was read (the history itself is not in this repository); (4) siblings/README.md,
ce-sweep/README.md, variants/RESULTS.md, corpus/README.md, robustness/report.md, realworld/README.md, investigate/FINDINGS.md and
docs/dayone-results.md are covered only by their own checkers (corpus/run_tests.py, robustness/check.py, ...), which recompute
data but not the prose around it; the one check on their prose is test_order_statements_name_the_unpublished_history, which reads every
Markdown file under the folders of ORDER_FOLDERS (the plans, which are the records, left out) and the day-one results note, and fails on a
statement of the order of events that does not name the author's unpublished development history.

Under pytest every row is its own test. Without pytest (scripts/check.py's built-in runner) one
plain test goes through all rows.

The sentences about the jobs of the ten later runs that returned nothing rest on tests/data/s6_job_steps.json,
a copy of the Actions step records of those runs (the run pages are public; the file says how it was read).
The sentences about the two newest runs, which returned every job, rest on tests/data/s7_job_steps.json in the same way.
The sentences about the Xeon 6973P-C's verdict with each of its jobs left out in turn are recomputed here with
harness/pool.py (in memory, nothing is written; about 20 seconds).
The Arm column's sentences (arm64/README.md, and the Arm sentences of README.md, readme-parts/DETAILS.md, siblings/README.md
and ce-sweep/README.md) rest on results/s8-arm-pooled/pooled.json and on the per-job files of results/s8-arm-run-*/: the
NEON, trap, csel and line counts are read again from the 30 jobs' saved listings (asm/*.s) with a pattern written here, the
matrix-multiply loop and the branches to its trap from the listing and details.json, the machine from results.json and
details.json. The times of the smoke run, the dispatch, the first finished job and the plan's commit rest on
tests/data/s8_arm_timeline.json (the file says how it was read; the plan's commit time is read from a repository that is not
published, so the file is a record of what was read and not a proof), and the plan's own words on arm64/PLAN.md.
The Arm column's sentences about the L2 noise, the placement statistic, the interval methods and the other bootstrap seeds
rest on site/data/arm64.json (built by scripts/build_site_data.py; tests/test_arm64_data.py derives it again from the raw
samples) and arm64/seed-sensitivity.json (arm64/seeds.py). Both are used only after their recorded hash of results/s8-arm-pooled/
pooled.json is checked against the pool as it is now. The seed's own constants are read from harness/pool.py, and the
runner wiring from .github/workflows/measure.yml with PyYAML (a missing PyYAML is a failure, not a skip).
The replication sentences (set B and set C against the pools they replicate) rest on replication/results.json, which
replication/compare.py derives from the six pooled files; the job counts, the run ids, the commit and the start times are read
again from the per-job records of results/s9-*/. The d-sweep sentences rest on results/s10-dsweep-pooled/dsweep-pooled.json,
the plan's illustrative table on dsweep/PLAN.md (read, never written), the instruction and time columns on the same pooled
file, the leave-one-job-out figures on dsweep/analyze.py run in memory on results/s10-dsweep-run-* (40 resamples, nothing
written), and the temporary branch's commit on the per-job records of those runs. The three tables of readme-parts/DETAILS.md
(replication, words, sizes) and the two tables of replication/README.md and dsweep/README.md are compared line for line with
rows built from the same files.
test_cited_paths_exist checks that every repository path named in backticks, and every relative Markdown link, in
README.md, readme-parts/DETAILS.md, siblings/README.md, variants/RESULTS.md, arm64/README.md, ce-sweep/README.md,
replication/README.md and dsweep/README.md exists.
"""

import datetime
import glob
import gzip
import hashlib
import json
import math
import os
import re
import statistics
from functools import lru_cache

try:
    import pytest
except ImportError:  # scripts/check.py falls back to its own runner when pytest is missing
    pytest = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
         11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen"}
ORDINALS = {2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth"}

EPYC_7763 = "AMD EPYC 7763 64-Core Processor"


# ---- reading the files ---------------------------------------------------------------------

def readme_text():
    path = os.environ.get("README_PATH") or os.path.join(REPO, "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def details_text():
    path = os.environ.get("DETAILS_PATH") or os.path.join(REPO, "readme-parts", "DETAILS.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def siblings_text():
    path = os.environ.get("SIBLINGS_PATH") or os.path.join(REPO, "siblings", "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def arm64_text():
    path = os.environ.get("ARM64_PATH") or os.path.join(REPO, "arm64", "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def cesweep_text():
    path = os.environ.get("CESWEEP_PATH") or os.path.join(REPO, "ce-sweep", "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def replication_text():
    path = os.environ.get("REPLICATION_PATH") or os.path.join(REPO, "replication", "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def dsweep_text():
    path = os.environ.get("DSWEEP_PATH") or os.path.join(REPO, "dsweep", "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def mitigate_text():
    path = os.environ.get("MITIGATE_PATH") or os.path.join(REPO, "mitigate", "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def gaps_text():
    path = os.environ.get("GAPS_PATH") or os.path.join(REPO, "gaps", "GAPS.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


@lru_cache(maxsize=None)
def J(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


def f1(x):
    return f"{x:.1f}"


def f2(x):
    return f"{x:.2f}"


def f3(x):
    return f"{x:.3f}"


def f4(x):
    return f"{x:.4f}"


def f0(x):
    return f"{x:.0f}"


def pct1(ratio):
    """A ratio as the README's percent over 1, one decimal."""
    return f"{(ratio - 1) * 100:.1f}"


def thousands(n):
    return f"{n:,}"


def word(n):
    return WORDS[n]


def amd_cpus():
    """The AMD models of the page that have enough jobs for a verdict."""
    return [c for c in J("site/data/index.json")["cpus"] if c["cpu_short"].startswith("EPYC") and c["enough"]]


# The kernel pool the page and the README read: the original 30 jobs, the 45 of the ten later runs and the 20 of
# the two newest runs (95 jobs). The two earlier pools stay on disk: the original one (the holdout is compared
# against it) and the 75-job one (the step before the two newest runs). They are read only where a sentence
# says "original" or "75-job".
POOLED = "results/s7-pooled/pooled.json"
POOLED_S6 = "results/s6-pooled/pooled.json"
POOLED_ORIGINAL = "results/s4-pooled/pooled.json"
FORWARD = ("k01_sum_fwd", "k02_add_fwd", "k03_stencil")


def pool_path(original=False, pool=None):
    return pool or (POOLED_ORIGINAL if original else POOLED)


def pooled_cpu(model):
    return next(c for c in J(POOLED)["cpus"] if c["cpu_model"] == model)


def cpu_like(key, original=False, pool=None):
    """The pooled entry of the CPU model whose name contains key ('7763', '9V45', '8573C', ...)."""
    return next(c for c in J(pool_path(original, pool))["cpus"] if key in c["cpu_model"])


def is_intel(model):
    return "intel" in model.lower()


def enough_cpus(pool=None):
    """The pooled entries with at least the minimum number of jobs for a verdict (the page shows these)."""
    minimum = J("site/data/index.json")["criteria"]["minimum_jobs"]
    return [c for c in J(pool_path(pool=pool))["cpus"] if c["jobs"] >= minimum]


def kernel_pool_source(source):
    """True for a job folder that belongs to the kernel pool (the original runs and the later ones)."""
    return source.startswith(("results/s4-run-", "results/s6-run-", "results/s7-run-"))


def cell_of(cpu, cell_id):
    return next(c for c in cpu["cells"] if c["cell_id"] == cell_id)


def lost_values(cpu):
    """Every in-cache cell of the lost loops, both columns."""
    return [c[col]["ratio"] for c in cpu["cells"] if c["class"] == "lost" for col in ("as_compiled", "aligned")]


def forward_aligned(cpu):
    return [c["aligned"]["ratio"] for c in cpu["cells"] if c["kernel"] in FORWARD]


def intel_pooled():
    """The Intel models of the page with enough jobs for a pooled reading."""
    return [c for c in J("site/data/index.json")["cpus"] if c["cpu_short"].startswith("Xeon") and c["enough"]]


def runs_with_verdict(cpu):
    return [r for r in cpu["per_run"] if r["form"] is not None]


def pooled_cell(model, cell_id):
    return next(c for c in pooled_cpu(model)["cells"] if c["cell_id"] == cell_id)


def sibling_row(variant):
    return next(r for r in J("site/data/siblings.json")["rows"] if r["variant"] == variant)


def sibling_values(variant, kernel, sizes=("L1", "L2"), cpus=None):
    """Every per-CPU min and max of one kernel in one sibling setup, as (value, cpu, size, jobs)."""
    out = []
    for cpu, per in sibling_row(variant)["cells"][kernel]["per_cpu"].items():
        if cpus is not None and cpu not in cpus:
            continue
        for size in sizes:
            if size in per:
                out.append((per[size]["min"], cpu, size, per["jobs"]))
                out.append((per[size]["max"], cpu, size, per["jobs"]))
    return out


def corpus_total_label(census):
    return next(c for c in J("site/data/corpus.json")["categories"] if c["label"] == f"census {census} total")


def realworld():
    d = J("site/data/realworld.json")
    rows = {r["row"]: r for r in d["rows"]}
    groups = {g["cpu_short"]: g for g in d["timing"]["groups"]}
    return d, rows, groups


def slower_rows(cpu_short):
    """The non-control programs the page reads as detectably slower on one CPU model."""
    _, rows, groups = realworld()
    return [name for name, v in groups[cpu_short]["rows"].items()
            if not rows[name]["control"] and v["reading"] == "detectably slower"]


def reps_per_side_values():
    """Every reps_per_side the written rule files give for the timing."""
    out = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "reps_per_side" and isinstance(v, int):
                    out.add(v)
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    for path in sorted(glob.glob(os.path.join(REPO, "harness", "criteria*.json"))):
        walk(J(os.path.relpath(path, REPO).replace("\\", "/")))
    return out


# ---- expected values -------------------------------------------------------------------------

def exp_google_pct():
    return {"v": f2(J("site/data/index.json")["claim"]["google_pct"])}


def exp_hero_reverse():
    return {"v": f1(pooled_cell(EPYC_7763, "k04_rev.L1")["aligned"]["ratio"])}


def exp_reps():
    v = reps_per_side_values()
    return {"lo": str(min(v)), "hi": str(max(v))}


def exp_lost_range():
    p = J("site/data/index.json")["page"]["lost"]
    return {"lo": f1(p["min"]), "hi": f1(p["max"])}


def exp_forward_sentence():
    index = J("site/data/index.json")
    aligned = index["page"]["forward"]["aligned"]
    assert aligned["min"] < 1, "the README says that below 1x the checked loop runs faster; no aligned forward cell is below 1x"
    two_of_three = [c for c in amd_cpus() if c["forward_compiled_max_cell"]["ratio"] >= 1.5]
    # the AVX2 exception: the largest forward-kernel cell on the AMD models in the AVX2 setup
    avx2 = max(v for k in ("k01_sum_fwd", "k02_add_fwd", "k03_stencil")
               for v, _, _, _ in sibling_values("clang18v3-fast", k, cpus={c["cpu_short"] for c in amd_cpus()}))
    return {
        "lo": f2(aligned["min"]), "hi": f2(aligned["max"]), "avx": f2(avx2),
        "n": word(len(two_of_three)), "of": word(len(amd_cpus())),
        "x": f1(index["page"]["forward"]["compiled"]["max"]),
    }


def intel_set_c_jobs():
    """The Intel jobs of replication set C (results/s9-run-*/*/results.json): (cpu_short, k02_add_fwd.L1 aligned ratio, source) per job.
    The page's intel_forward rows hold the S3 runs, the S4 smoke run and the pooled jobs; set C is counted here from its own job files."""
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, S9_X86_JOBS))):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        model = d["run"]["runner"]["cpu_model"]
        if "intel" in model.lower():
            key = next(k for k in MODEL_KEYS if k in model)
            cell = next(c for c in d["cells"] if c["cell_id"] == "k02_add_fwd.L1")
            out.append(("Xeon " + key, cell["aligned"]["ratio"], os.path.relpath(os.path.dirname(f), REPO).replace("\\", "/")))
    return out


def intel_all_jobs():
    """Every Intel job seen: [(cpu_short, aligned forward add at L1, source)] over the page's rows and the Intel jobs of set C."""
    page = [(r["cpu_short"], r["aligned"], r["source"]) for r in J("site/data/index.json")["intel_forward"]["jobs"]]
    out = page + intel_set_c_jobs()
    assert len({src for _, _, src in out}) == len(out), "an Intel job is counted twice (a set C job is also one of the page's rows)"
    return out


# ---- the three stored robustness readings: seed re-draws (x86-64), the A/A at L2, the calibration baseline ----------

SEED_X86 = "robustness/seed-sensitivity-x86.json"
AA_L2 = "robustness/aa-l2.json"
CALIBRATION = "robustness/calibration.json"
X6973_MODEL = "Intel(R) Xeon(R) 6973P-C"
AMD_9V45_MODEL = "AMD EPYC 9V45 96-Core Processor"


def seed_cell(cell_id):
    """One record of robustness/seed-sensitivity-x86.json (id '<cpu model>|<forward or placement>|<cell>')."""
    found = [c for c in J(SEED_X86)["cells"] if c["id"] == cell_id]
    assert len(found) == 1, f"{SEED_X86} holds {len(found)} records for {cell_id}"
    return found[0]


def seed_facts():
    """What the Xeon 6973P-C and EPYC 9V45 statements quote from the seed re-draws, tied to the stored pooled file:
    the stored interval end of each cell must be the pooled file's, so a changed pool fails here before a number can drift."""
    seeds = J(SEED_X86)
    limit = 1 + cpu_like("6973P-C")["verdict"]["forward_limit_pct"] / 100
    s6 = seed_cell(X6973_MODEL + "|forward|k03_stencil.L2")
    assert abs(s6["stored"]["hi"] - cell_of(cpu_like("6973P-C"), "k03_stencil.L2")["aligned"]["ci95"][1]) < 1e-6, \
        "the seed file's stored end of the Xeon 6973P-C stencil at L2 is not the pooled file's"
    assert s6["alt"]["summary"]["limit"] == limit and s6["alt"]["draws"] == seeds["alt_seeds"]["count"]
    n9 = seed_cell(AMD_9V45_MODEL + "|forward|k03_stencil.L1")
    assert abs(n9["stored"]["hi"] - cell_of(cpu_like("9V45"), "k03_stencil.L1")["aligned"]["ci95"][1]) < 1e-6, \
        "the seed file's stored end of the EPYC 9V45 stencil at L1 is not the pooled file's"
    p9 = seed_cell(AMD_9V45_MODEL + "|placement|k03_stencil.L1")
    assert p9["converged"]["excludes_1"] is True and p9["alt"]["draws"] == seeds["alt_seeds"]["count"]
    whole = seeds["whole"]["models"][X6973_MODEL]
    forms = whole["tally"]["forms"]
    assert whole["stored_form"] == "map" and sum(forms.values()) == whole["tally"]["count"] == seeds["whole"]["count"], "the whole-analysis tally is not over the stored 60 seeds"
    conv = s6["converged"]
    assert conv["hi"] < limit and abs(limit - conv["hi"] - (-conv["margin_to_limit"])) < 1e-9
    assert limit - conv["hi"] < s6["alt"]["summary"]["hi"]["sd"], "the converged margin is no longer smaller than the sd of one draw's end"
    return {"alt": seeds["alt_seeds"]["count"], "res": conv["resamples"], "conv": conv["hi"], "convm": limit - conv["hi"],
            "sd": s6["alt"]["summary"]["hi"]["sd"], "hits": s6["alt"]["summary"]["at_or_above_limit"], "stored": s6["stored"]["hi"],
            "inc": forms["inconclusive"], "map": forms["map"], "total": whole["tally"]["count"],
            "conv9": n9["converged"]["hi"], "conv9m": n9["converged"]["hi"] - limit, "kept9": p9["alt"]["summary"]["excludes_1"], "draws9": p9["alt"]["draws"],
            "limit": limit}


def aa_l2_pool(pool_id):
    found = [p for p in J(AA_L2)["pools"] if p["id"] == pool_id]
    assert len(found) == 1, f"{AA_L2} holds {len(found)} pools called {pool_id}"
    return found[0]


def aa_l2_model(pool_id, key):
    found = [m for m in aa_l2_pool(pool_id)["models"] if key in m["cpu_model"]]
    assert len(found) == 1, f"{AA_L2} pool {pool_id} holds {len(found)} models containing {key}"
    return found[0]


def aa_l2_facts():
    """The pooled identical-binary A/A at L1 and L2 that the README and the details quote (pool s7 for the x86-64 models, s8-arm for the Arm core)."""
    s7 = aa_l2_pool("s7")
    enough = [m for m in s7["models"] if m["jobs"] >= J("site/data/index.json")["criteria"]["minimum_jobs"]]
    others = [m for m in enough if X6973_MODEL not in m["cpu_model"]]
    x, a = aa_l2_model("s7", "6973P-C"), aa_l2_model("s8-arm", "Neoverse-N2")
    ceiling = J(AA_L2)["criteria"]["aa_half_width_max_pct"]
    assert len(enough) == 5 and len(others) == 4, "the s7 pool no longer has five models with a verdict-sized job count"
    assert len(J(AA_L2)["pools"]) == 4, "robustness/aa-l2.json no longer covers four pools, which the README and the details say"
    assert x["l2"]["half_width_pct"] > ceiling and a["l2"]["half_width_pct"] > ceiling and all(m["l2"]["half_width_pct"] < ceiling for m in others), \
        "the models above the 2% ceiling at L2 are no longer the Xeon 6973P-C and the Arm core alone"
    assert J(AA_L2)["rule_at_l2"]["stored_words_that_would_change"] == ["s7: " + X6973_MODEL], \
        "read at L2, the ceiling clause no longer changes the Xeon 6973P-C's word alone"
    assert x["jobs"] == cpu_like("6973P-C")["jobs"] and a["jobs"] == arm_cpu()["jobs"], "the A/A pools are not over the pooled files' jobs"
    return {"max_others": max(m["l2"]["half_width_pct"] for m in others), "n_others": len(others), "x1": x["l1"]["half_width_pct"],
            "x2": x["l2"]["half_width_pct"], "a1": a["l1"]["half_width_pct"], "a2": a["l2"]["half_width_pct"], "ceil": ceiling}


def aa_l2_as_wide_as_the_deciding_cells():
    """'About as wide as' means within a quarter either way: the A/A half-width at L2 against the half-width of the interval of the cell that decides the word."""
    f = aa_l2_facts()
    wide_x = seed_cell(X6973_MODEL + "|forward|k03_stencil.L2")["stored"]["half_width_pct"]
    iv = arm_cell("k02_add_fwd.L2")["aligned"]["ci95"]
    wide_a = (iv[1] - iv[0]) / 2 / arm_cell("k02_add_fwd.L2")["aligned"]["ratio"] * 100
    for name, aa, cell in (("Xeon 6973P-C stencil at L2", f["x2"], wide_x), ("Arm forward add at L2", f["a2"], wide_a)):
        assert 0.75 <= aa / cell <= 1.25, f"the A/A at L2 ({aa:.2f}%) is no longer about as wide as the interval of the {name} ({cell:.2f}%)"
    return {}


def calib_model(pool, key):
    found = [m for m in J(CALIBRATION)["run_to_run"][pool]["models"] if key in m["cpu_model"]]
    assert len(found) == 1, f"{CALIBRATION} pool {pool} holds {len(found)} models containing {key}"
    return found[0]


def calib_family(model, kernels):
    """(outside, pairs, expected outside) over the cells of the given kernels (the kernel id is the part of the cell id before the first underscore)."""
    cells = [c for c in model["by_cell"] if c["cell_id"].split("_")[0] in kernels]
    return sum(c["outside"] for c in cells), sum(c["pairs"] for c in cells), sum(c["expected_outside"] for c in cells)


def calib_facts():
    """The calibrated run-to-run counts that the README and the details quote, tied to the pooled files' own reproduction counts."""
    m7, m9, m6 = calib_model("s7", "7763"), calib_model("s7", "9V74"), calib_model("s6", "7763")
    assert (m7["outside"], m7["checked"]) == (cpu_like("7763")["reproduction"]["outside"], cpu_like("7763")["reproduction"]["checked"]), \
        "the calibration file's EPYC 7763 count is not the pooled file's reproduction count"
    assert (m9["outside"], m9["checked"]) == (cpu_like("9V74")["reproduction"]["outside"], cpu_like("9V74")["reproduction"]["checked"])
    lost, fwd = calib_family(m7, ("k04", "k05", "k08")), calib_family(m7, ("k01", "k02", "k03"))
    s7, s9, s6s = m7["simulation"]["independent"], m9["simulation"]["independent"], m6["simulation"]["independent"]
    assert s7["p025"] <= m7["outside"] <= s7["p975"] and m9["outside"] < s9["p025"] and s6s["p025"] <= m6["outside"] <= s6s["p975"], \
        "the totals are no longer inside (EPYC 7763) and below (EPYC 9V74) the range of independent comparisons"
    assert lost[0] > lost[2] and fwd[0] < fwd[2], "the excess on EPYC 7763 is no longer in the lost-loop cells and absent from the forward ones"
    return {"m7": m7, "m9": m9, "m6": m6, "lost": lost, "fwd": fwd, "r7": (s7["p025"], s7["p975"]), "r9": (s9["p025"], s9["p975"]), "r6": (s6s["p025"], s6s["p975"])}


def calib_subsets(key="6973P-C"):
    """{J: (INCONCLUSIVE, draws)} for the subset sizes that were run, and whether the 5-job subsets are every possible one."""
    d = J(CALIBRATION)
    model = next(m for m in d["subsets"] if key in m)
    out = {}
    for j in (3, 5):
        e = d["subsets"][model]["by_j"][str(j)]
        out[j] = (e["forms"]["inconclusive"], e["count"], e["exhaustive"])
        assert e["forms"]["inconclusive"] + e["forms"].get("map", 0) == e["count"]
    assert out[5][2] is True and out[3][2] is False and "count" not in d["subsets"][model]["by_j"]["10"], "the subset draws are no longer 30 of 3 and all of 5"
    assert d["constants"]["subset_js"][:2] == [3, 5] and d["constants"]["subsets_per_j"] == out[3][1]
    return out


def exp_intel_sentence():
    index = J("site/data/index.json")
    intel = index["intel_forward"]
    rows = intel["jobs"]
    every = intel_all_jobs()
    set_c = intel_set_c_jobs()
    assert {s for s, _, _ in every} == set(intel["cpus"]), "set C drew an Intel model the page's rows do not have"
    assert intel["aligned"]["min"] == min(r["aligned"] for r in rows) and intel["aligned"]["max"] == max(r["aligned"] for r in rows)
    pooled = intel_pooled()
    forms = {c["cpu_short"]: c["form"] for c in pooled}
    assert forms == {"Xeon 8573C": "inconclusive", "Xeon 6973P-C": "map"}, \
        "the README says the Xeon 8573C is INCONCLUSIVE and the Xeon 6973P-C is MAP; the data now gives " + str(forms)
    jobs = {c["cpu_short"]: c["jobs"] for c in pooled}
    amd = [cell_of(cpu_like(c["cpu_short"].split()[1]), "k02_add_fwd.L1")["aligned"]["ratio"] for c in amd_cpus()]
    by = {c["cpu_short"]: cell_of(cpu_like(c["cpu_short"].split()[1]), "k02_add_fwd.L1")["aligned"]["ratio"] for c in pooled}
    # the Intel jobs that are in the kernel pool (all three models), and the model that has too few jobs to judge
    in_pool = [r for r in rows if kernel_pool_source(r["source"])]
    assert len(in_pool) == sum(c["jobs"] for c in J(POOLED)["cpus"] if is_intel(c["cpu_model"])), "the Intel rows and the pooled file disagree on the Intel jobs in the pool"
    few = index["page"]["cpus_few"]
    assert [c["cpu_short"] for c in few] == ["Xeon 8370C"], f"models with too few jobs to judge: {few}"
    # why the 8573C has no verdict and how the 6973P-C passes, as the README gives it
    a, b = cpu_like("8573C"), cpu_like("6973P-C")
    limit = a["verdict"]["forward_limit_pct"]
    assert limit == b["verdict"]["forward_limit_pct"] and limit == int(limit), f"forward limit {limit}"
    first = cell_of(a, "k02_add_fwd.L1")
    assert "missed by k02_add_fwd.L1" in a["verdict"]["why"] and not first["placement"]["sensitive"] and first["aligned"]["ci95"][0] > 1 + limit / 100, \
        "the Xeon 8573C's forward add no longer sits wholly over the forward limit"
    stencil = cell_of(b, "k03_stencil.L2")["aligned"]
    assert b["verdict"]["form"] == "map" and stencil["ci95"][1] < 1 + limit / 100 and cell_of(b, "k02_add_fwd.L1")["placement"]["sensitive"], \
        "the Xeon 6973P-C no longer passes on its stencil at L2 with the forward add left out as placement-sensitive"
    b6 = cpu_like("6973P-C", pool=POOLED_S6)
    stencil6 = cell_of(b6, "k03_stencil.L2")["aligned"]
    assert b6["verdict"]["form"] == "inconclusive" and "missed by k03_stencil.L2" in b6["verdict"]["why"] and stencil6["ci95"][1] > 1 + limit / 100, \
        "the 75-job pool no longer has the Xeon 6973P-C INCONCLUSIVE on its stencil at L2"
    assert b["jobs"] == b6["jobs"] + 1, f"the README says one job was added to the Xeon 6973P-C; it has {b6['jobs']} jobs in the 75-job pool and {b['jobs']} now"
    sf = seed_facts()
    assert sf["inc"] > 0 and sf["map"] > sf["inc"], "the Xeon 6973P-C's whole analysis is no longer MAP in most and INCONCLUSIVE in some of the other seeds"
    return {"jobs": str(len(every)), "n": word(len(intel["cpus"])), "setc": str(len(set_c)),
            "pool": str(len(in_pool)), "early": str(len(rows) - len(in_pool)), "pooljobs": str(pooled_jobs()),
            "lo": f2(min(v for _, v, _ in every)), "hi": f2(max(v for _, v, _ in every)),
            "alo": f2(min(amd)), "ahi": f2(max(amd)),
            "j1": str(jobs["Xeon 8573C"]), "j2": str(jobs["Xeon 6973P-C"]), "j2s6": str(b6["jobs"]), "ord": ORDINALS[b["jobs"]],
            "lim": str(int(limit)), "x8573": f2(by["Xeon 8573C"]), "x6973": f2(by["Xeon 6973P-C"]),
            "end6": f3(stencil6["ci95"][1]), "end7": f3(stencil["ci95"][1]), "j3": str(few[0]["jobs"]),
            "conv": f4(sf["conv"]), "convm": f4(sf["convm"]), "seedinc": str(sf["inc"]), "seedtot": str(sf["total"])}


def exp_lost_bullet():
    index = J("site/data/index.json")
    maps = sorted(c["cpu_short"] for c in index["cpus"] if c["form"] == "map")
    assert maps == ["EPYC 7763", "EPYC 9V45", "EPYC 9V74", "Xeon 6973P-C"], \
        f"the README names the CPU models with a verdict (three AMD and the Xeon 6973P-C); the data gives {maps}"
    p = index["page"]["lost"]
    every_l1 = [v for row in J("site/data/siblings.json")["rows"] for k in row["cells"]
                for v, _, size, _ in sibling_values(row["variant"], k, sizes=("L1",))]
    cpu = pooled_cpu(EPYC_7763)
    out = {"lo": f1(p["min"]), "hi": f1(p["max"]), "n": word(len(maps)), "sib": f1(max(every_l1))}
    intel = intel_pooled()
    jobs = {c["jobs"] for c in intel}
    assert len(jobs) == 1, f"the README says '7 jobs each' for the two Xeon models; they have {sorted(jobs)}"
    out["ij"] = str(jobs.pop())
    out["ilo"] = f1(min(c["lost"]["min"] for c in intel))
    out["ihi"] = f1(max(c["lost"]["max"] for c in intel))
    for key, cell in (("rev", "k04_rev.L1"), ("s2", "k05_stride2.L1"), ("mm", "k08_matmul.L1")):
        out[key + "_novec"] = f1(cpu["positive"][cell]["ratio"])
        out[key + "_on"] = f1(pooled_cell(EPYC_7763, cell)["as_compiled"]["ratio"])
    return out


def census_driver_loops():
    """Vectorized loops (NONE build) in the census's own driver files in census 2; the "project code" column of the table is project + driver, census 1 has none."""
    c = J("site/data/corpus.json")
    c1, c2 = c["census1"]["totals"]["none"]["vectorized_by_origin"], c["census2"]["totals"]["none"]["vectorized_by_origin"]
    assert c1["driver"] == 0, "census 1 now has driver loops: the README says 1 of 150 for project code"
    assert c2["project"] + c2["driver"] == corpus_total_label(2)["vectorized_project_code"], "the 'project code' column is no longer project plus driver"
    assert c1["project"] == corpus_total_label(1)["vectorized_project_code"]
    return c2["driver"]


def exp_census_bullet():
    c = J("site/data/corpus.json")
    c1, c2 = c["census1"]["totals"], c["census2"]["totals"]
    return {
        "lost1": str(c1["lost"]), "vec1": thousands(c1["none"]["vectorized"]), "libs": str(c1["projects"]),
        "lost2": str(c2["lost"]), "vec2": thousands(c2["none"]["vectorized"]), "projs": str(c2["projects"]),
        "vec1b": thousands(c1["none"]["vectorized"]),
        "libcxx": str(c1["none"]["vectorized_by_origin"]["libc++"]),
        "p1": str(corpus_total_label(1)["vectorized_project_code"]),
        "p1lost": str(c1["lost_by_origin"]["project"]),
        "p2lost": str(c2["lost_by_origin"]["project"]),
        "p2": thousands(corpus_total_label(2)["vectorized_project_code"]),
        "drv": word(census_driver_loops()),
        "with": str(c2["projects_with_a_lost_loop"]), "of": str(c2["projects"]),
        "lgbm": str(next(p for p in c["census2"]["projects"] if p["name"] == "lightgbm")["lost"]),
        "of444": str(c2["lost"]),
    }


def exp_realworld_bullet():
    d, rows, groups = realworld()
    workloads = [n for n, r in rows.items() if not r["control"]]
    projects = {rows[n]["project"] for n in workloads}
    lgbm = [n for n in workloads if rows[n]["project"] == "LightGBM"]
    slow7763 = slower_rows("EPYC 7763")
    ratios = [min(groups["EPYC 7763"]["rows"][n][col]["ratio"] for col in ("fast", "aligned")) for n in slow7763] + \
             [max(groups["EPYC 7763"]["rows"][n][col]["ratio"] for col in ("fast", "aligned")) for n in slow7763]
    controls = [n for n, r in rows.items() if r["control"]]
    return {
        "six": word(len(workloads)), "four": word(len(projects)), "lgbm": word(len(lgbm)),
        "n7": word(len(slow7763)), "lo": pct1(min(ratios)), "hi": pct1(max(ratios)),
        "j7": str(groups["EPYC 7763"]["jobs"]),
        "p": word(len({rows[n]["project"] for n in slow7763})),
        "n74": word(len(slower_rows("EPYC 9V74"))), "j74": str(groups["EPYC 9V74"]["jobs"]),
        "n45": word(len(slower_rows("EPYC 9V45"))), "j45": str(groups["EPYC 9V45"]["jobs"]),
        "ctl": word(len(controls)),
    }


def exp_placement_bullet():
    layout = J("site/data/layout.json")
    index = J("site/data/index.json")
    mixed = [c for c in layout["cpus"] if c["enough"] and any(
        r["kernel"] == "k02_add_fwd" and r["size"] == "L1" and r["verdict"] == "MIXED" for r in c["rows"])]
    by = {c["cpu_short"]: c["forward_compiled_max_cell"]["ratio"] for c in index["cpus"]}
    return {
        "n": str(layout["placements"]),
        "rlo": f1(layout["reverse"]["min"]), "rhi": f1(layout["reverse"]["max"]),
        "alo": f2(layout["kernels"]["k02_add_fwd"]["min"]), "ahi": f2(layout["kernels"]["k02_add_fwd"]["max"]),
        "models": word(len(mixed)),
        "c7763": f2(by["EPYC 7763"]), "c9v74": f2(by["EPYC 9V74"]),
    }


def exp_mitigation():
    shape = next(s for s in J("site/data/mitigate.json")["shapes"] if s["shape"] == "reverse")
    pre = next(v for v in shape["variants"] if v["variant"] == "pre")
    ratios = [r["ratio"] for per in pre["per_cpu"].values() for rows in per.values() for r in rows]
    return {"lo": f2(min(ratios)), "hi": f2(max(ratios))}


def exp_gcc():
    values = [v for v, _, _, _ in sibling_values("gcc14-O3-assert", "k02_add_fwd")]
    row = sibling_row("gcc14-O3-assert")
    assert "libstdc++ _GLIBCXX_ASSERTIONS" in row["note"], f"the GCC row no longer says it is libstdc++'s assertions: {row['note']!r}"
    cell = row["cells"]["k02_add_fwd"]
    per_cpu = cell["per_cpu"]
    # "the low end is one job": the lowest value comes from a CPU model that has a single job
    low_cpu = next(cpu for v, cpu, _, _ in sibling_values("gcc14-O3-assert", "k02_add_fwd") if v == min(values))
    assert per_cpu[low_cpu]["jobs"] == 1 and low_cpu in cell["single_job_cpus"], f"the lowest value is from {low_cpu}, {per_cpu[low_cpu]['jobs']} jobs"
    return {"lo": f1(min(values)), "hi": f1(max(values)),
            "jobs": str(sum(p["jobs"] for p in per_cpu.values())), "n": str(len(per_cpu))}


def exp_why_1_6():
    return {"v": f1(J("site/data/index.json")["page"]["forward"]["compiled"]["max"])}


def exp_versions():
    v = J("site/data/versions.json")
    majors = sorted(int(t["clang"].split(".")[0]) for t in v["toolchains"])
    enough_models = {e["cpu_short"] for e in v["summary"]["enough"]}
    main = v["summary"]["matmul_main"]
    novec = pooled_cpu(EPYC_7763)["positive"]["k08_matmul.L1"]["ratio"]
    # the README types one number for each size, so the job-to-job range must round to one number
    assert f1(main["L1"]["min"]) == f1(main["L1"]["max"]), f"matmul at L1 on EPYC 7763 ranges {main['L1']}"
    assert f2(main["L2"]["min"]) == f2(main["L2"]["max"]), f"matmul at L2 on EPYC 7763 ranges {main['L2']}"
    # "as slow as a build with no vectorization at all": the pooled no-vectorize build rounds to the same number
    assert f1(novec) == f1(main["L1"]["max"]), f"no-vectorize matmul at L1 is {novec:.2f}, versions give {main['L1']['max']:.2f}"
    return {
        "a": str(majors[0]), "b": str(majors[-1]), "models": word(len(enough_models)),
        "l1": f1(main["L1"]["max"]), "l2": f2(main["L2"]["max"]),
    }


def exp_cesweep():
    rows = [r for r in J("site/data/cesweep.json")["rows"]
            if r["family"] == "clang" and r["target"] == "x86-64" and r["opt"] == "-O2"
            and r["macro_effective"]]
    numbered = [r for r in rows if r["major"]]
    kept = sorted(r["major"] for r in numbered if "k08_matmul" not in r["lost"])
    lost_before = sorted(r["major"] for r in numbered if "k08_matmul" in r["lost"] and r["major"] < kept[0])
    lost_after = [r for r in numbered if "k08_matmul" in r["lost"] and r["major"] > kept[-1]]
    trunk = [r for r in rows if not r["major"]]
    assert trunk and all("k08_matmul" in r["lost"] for r in trunk), "trunk no longer loses matrix multiply"
    return {"a": str(lost_before[0]), "b": str(lost_before[-1]), "c": str(kept[0]), "d": str(kept[-1]),
            "e": ".".join(lost_after[0]["version"].split(".")[:2]), "date": cesweep_trunk_date()}


def cesweep_trunk_date():
    """The one day on which the sweep's cached x86-64 trunk answers were fetched (trunk moves daily)."""
    days = set()
    for path in glob.glob(os.path.join(REPO, "ce-sweep", "cache", "clang_trunk__x86-64__*.json.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            days.add(json.load(f)["fetched_at"][:10])
    assert len(days) == 1, f"the cached trunk answers of the sweep were fetched on {sorted(days)}"
    return days.pop()


def vectorizer_trunk_days():
    """The days on which the reverse and stride-2 study sent its requests to Compiler Explorer's trunk compilers."""
    with open(os.path.join(REPO, "investigate", "vectorizer", "reverse-stride2", "extracted", "trunk-versions.txt"), encoding="utf-8") as f:
        text = f.read()
    part = text.split("requests to trunk compilers, by time (UTC):")[1]
    return set(re.findall(r"^\s+(\d{4}-\d{2}-\d{2})T", part, flags=re.M))


def matmul_revision(build):
    """The first ten characters of the LLVM revision in the `-v` version line saved for one compiler build."""
    with open(os.path.join(REPO, "investigate", "vectorizer", "matmul", "derived", "revisions.txt"), encoding="utf-8") as f:
        text = f.read()
    m = re.search(rf"^{build}\s.*\n\s+clang version ([^\n]*?) \(https://github\.com/llvm/llvm-project\.git ([0-9a-f]{{40}})\)", text, flags=re.M)
    assert m, f"no version line for {build} in investigate/vectorizer/matmul/derived/revisions.txt"
    return m.group(1), m.group(2)[:10]


def timed_clang():
    """The one Ubuntu clang version the timed runs of the kernel pool recorded."""
    versions = set()
    for path in glob.glob(os.path.join(REPO, "results", "s4-run-*", "results-*", "results.json")) + \
            glob.glob(os.path.join(REPO, "results", "s6-run-*", "results-*", "results.json")) + \
            glob.glob(os.path.join(REPO, "results", "s7-run-*", "results-*", "results.json")):
        m = re.search(r"Ubuntu clang version ([\d.]+)", J(os.path.relpath(path, REPO).replace("\\", "/"))["run"]["toolchain"]["clang"])
        versions.add(m.group(1))
    assert len(versions) == 1, f"the timed runs recorded clang {sorted(versions)}"
    return versions.pop()


def exp_rc_and_same_remark():
    """Compiler Explorer's clang 18.1.0 is a release candidate; the timed Ubuntu build gave the same remark for the two loops."""
    version, _ = matmul_revision("paths_c18")
    assert version.endswith("rc"), f"Compiler Explorer's clang1810 now reports clang version {version}"
    for kernel in ("k04_rev", "k05_stride2"):
        path = os.path.join(REPO, "dayone", "results", "run-38116223923", f"remarks.{kernel}.fast.txt")
        with open(path, encoding="utf-8") as f:
            assert "loop not vectorized: could not determine number of loop iterations" in f.read(), f"{path}: the remark is not there"
    return {"ce": version[:-2], "timed": timed_clang()}


def exp_ubuntu_clang_20():
    """The apt clang 20 version string recorded by the siblings run."""
    versions = set()
    for path in glob.glob(os.path.join(REPO, "results", "siblings-run-*", "*", "siblings.json")):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        versions.update(re.findall(r"Ubuntu clang version (20\.[0-9.]+)", text))
    assert versions, "no Ubuntu clang 20 version string in results/siblings-run-*/*/siblings.json"
    return {"v": sorted(versions)[0]}


def exp_environment():
    s = J("site/data/environment.json")["summary"]
    return {"jobs": str(s["jobs"]), "steal": f"{s['steal_max_pct']:g}", "drift": f2(s["half_drift_max_pct"]),
            "share": str(s["jobs_sharing_core"])}


def exp_counts_not_time():
    c = J("site/data/corpus.json")
    return {"a": thousands(c["census1"]["totals"]["none"]["vectorized"]),
            "b": thousands(c["census2"]["totals"]["none"]["vectorized"])}


def exp_four_projects():
    _, rows, _ = realworld()
    return {"n": word(len({r["project"] for r in rows.values() if not r["control"]}))}


def exp_dayone_runs():
    runs = [p for p in glob.glob(os.path.join(REPO, "dayone", "results", "run-*")) if os.path.isdir(p)]
    return {"n": word(len(runs))}


def exp_v3_reps():
    return {"v": str(J("harness/criteria-v3.json")["v3"]["timing"]["reps_per_side"])}


def exp_independence_holdout():
    rows = J("site/data/holdout.json")["rows"]
    yes = [r["cpu_short"] for r in rows if r["reproduced"] is True]
    no = [r["cpu_short"] for r in rows if r["reproduced"] is False]  # None: too few jobs to compare
    original = J(POOLED_ORIGINAL)
    # the robustness analysis of the 95-job pool: the forms of every CPU model under every interval method
    rb = J("robustness/results.json")["datasets"]["s7"]["cpus"]
    assert len(rb) == 5, f"the robustness analysis covers {sorted(rb)}"
    amd = [c for name, c in rb.items() if "EPYC" in name]
    x8573 = next(c for name, c in rb.items() if "8573C" in name)
    x6973 = next(c for name, c in rb.items() if "6973P-C" in name)
    same = len(amd) == 3 and all(all(m["form"] == "map" for m in c["methods"].values()) for c in amd) and \
        all(m["form"] == "inconclusive" for m in x8573["methods"].values())
    k = sum(1 for m in x6973["methods"].values() if m["form"] == "map")
    loo = leave_one_job_out()
    r, r6 = cpu_like("7763")["reproduction"], cpu_like("7763", pool=POOLED_S6)["reproduction"]
    # the README names the holdout family once: "EPYC 7763 and 9V74, not 9V45"
    cf = calib_facts()
    assert cf["m6"]["checked"] == r6["checked"] and cf["m6"]["outside"] == r6["outside"], "the calibration file's 75-job EPYC 7763 count is not the pooled file's"
    return {"n": str(pooled_jobs()), "o": str(sum(c["jobs"] for c in original["cpus"])),
            "exp": f1(cf["m7"]["expected_outside"]),
            "fo": str(cf["lost"][0]), "fn": str(cf["lost"][1]), "fe": f1(cf["lost"][2]),
            "go": str(cf["fwd"][0]), "gn": str(cf["fwd"][1]), "ge": f1(cf["fwd"][2]),
            "vo": str(cf["m9"]["outside"]), "vn": str(cf["m9"]["checked"]), "ve": f1(cf["m9"]["expected_outside"]),
            "same": "no verdict form" if same else "a verdict form",
            "k": word(k), "m": word(len(x6973["methods"])),
            "inc": str(sum(1 for _, form in loo if form == "inconclusive")), "tot": str(len(loo)),
            "yes": " and ".join([yes[0]] + [c.replace("EPYC ", "") for c in yes[1:]]),
            "no": " and ".join(c.replace("EPYC ", "") for c in no),
            "out": str(r["outside"]), "chk": str(r["checked"]), "pct": f"{100 * r['outside'] / r['checked']:.0f}",
            "pct6": f"{100 * r6['outside'] / r6['checked']:.0f}", "n6": str(pooled_jobs(pool=POOLED_S6))}


def exp_eight_loops():
    return {"n": str(len(J("site/data/index.json")["criteria"]["kernels"]))}


# ---- the ten later runs, the compile-only studies ------------------------------------------------

def pooled_jobs(original=False, pool=None):
    return sum(c["jobs"] for c in J(pool_path(original, pool))["cpus"])


@lru_cache(maxsize=None)
def leave_one_job_out(key="6973P-C"):
    """[(job file, verdict form)]: one CPU model of the 95-job pool pooled again with each of its jobs left out in turn.

    Pools in memory with harness/pool.py (the same function that wrote the pooled file); nothing is written. The pool of
    all the model's jobs must give the stored form first, so a change to the pooling shows up as a failure here.
    """
    import sys
    harness = os.path.join(REPO, "harness")
    if harness not in sys.path:
        sys.path.insert(0, harness)
    import pool
    criteria, _ = pool.criteria_and_sha()
    pooled = J(POOLED)
    base = os.path.dirname(os.path.join(REPO, POOLED))
    inputs = [i for i in pooled["inputs"] if key in i["cpu_model"]]
    model = inputs[0]["cpu_model"]
    docs = []
    for i in inputs:
        with open(os.path.normpath(os.path.join(base, i["path"])), encoding="utf-8") as f:
            docs.append(json.load(f))
    whole = pool.analyse_cpu(model, docs, criteria)["verdict"]["form"]
    assert whole == cpu_like(key)["verdict"]["form"], f"{model}: pooling its {len(docs)} jobs again gives {whole}, the pooled file {cpu_like(key)['verdict']['form']}"
    return [(i["path"], pool.analyse_cpu(model, docs[:n] + docs[n + 1:], criteria)["verdict"]["form"]) for n, i in enumerate(inputs)]


def jobs_per_run():
    """How many matrix jobs one full run of measure.yml dispatches (the default of its `jobs` input)."""
    with open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        wf = f.read()
    return len(json.loads(re.search(r'jobs:\s*\n\s*description:[^\n]*\n\s*default: "(\[[^"]*\])"', wf).group(1)))


def job_limit_now():
    with open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        wf = f.read()
    now = re.search(r"measure:\s*\n\s*runs-on:[^\n]*\n(?:\s*#[^\n]*\n)*\s*timeout-minutes: (\d+)", wf)
    assert now, "measure.yml no longer names the job limit of the measure job"
    return int(now.group(1))


def later_runs():
    """The ten later runs (s6): result folders, returned jobs, the dispatch size and the limit the workflow names."""
    dirs = sorted(glob.glob(os.path.join(REPO, "results", "s6-run-*")))
    returned = sum(len(glob.glob(os.path.join(d, "results-*", "results.json"))) for d in dirs)
    with open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        wf = f.read()
    # the comment on timeout-minutes wraps over several lines: join them before reading it
    flat = re.sub(r"\s*\n\s*#\s*", " ", wf)
    note = re.search(r"(\d+) of (\d+) jobs in (\w+) runs were cancelled at the old (\d+)-minute limit before they uploaded", flat)
    assert note, "measure.yml no longer says how many jobs were cancelled at the old limit"
    dispatched = len(dirs) * jobs_per_run()
    assert pooled_jobs(pool=POOLED_S6) - pooled_jobs(original=True) == returned, \
        f"the 75-job pool has {pooled_jobs(pool=POOLED_S6)} jobs, the original {pooled_jobs(original=True)}, the later result folders {returned}"
    assert (int(note.group(1)), int(note.group(2)), note.group(3)) == (dispatched - returned, dispatched, word(len(dirs))), (
        f"measure.yml says {note.group(1)} of {note.group(2)} jobs in {note.group(3)} runs were cancelled; the result folders give "
        f"{dispatched - returned} of {dispatched} in {word(len(dirs))} runs")
    return {"runs": len(dirs), "returned": returned, "dispatched": dispatched,
            "limit": int(note.group(4)), "now": job_limit_now()}


MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def newest_runs():
    """The two newest runs (s7): result folders, returned jobs, the dispatch size, the limit now and the day they started."""
    dirs = sorted(glob.glob(os.path.join(REPO, "results", "s7-run-*")))
    files = [p for d in dirs for p in glob.glob(os.path.join(d, "results-*", "results.json"))]
    assert pooled_jobs() - pooled_jobs(pool=POOLED_S6) == len(files), \
        f"the 95-job pool has {pooled_jobs()} jobs, the 75-job pool {pooled_jobs(pool=POOLED_S6)}, the newest result folders {len(files)}"
    days = {J(os.path.relpath(p, REPO).replace("\\", "/"))["run"]["started_at"][:10] for p in files}
    assert len(days) == 1, f"the newest runs started on {sorted(days)}"
    _, month, day = (int(x) for x in days.pop().split("-"))
    return {"runs": len(dirs), "returned": len(files), "dispatched": len(dirs) * jobs_per_run(),
            "now": job_limit_now(), "day": f"{MONTHS[month - 1]} {day}"}


STEP_RECORDS = "tests/data/s6_job_steps.json"
STEP_RECORDS_S7 = "tests/data/s7_job_steps.json"
PUBLIC_RUN_PREFIX = "https://github.com/JacoboPacheco/third-of-a-percent/actions/runs/"


def later_job_records(prefix="s6", steps=STEP_RECORDS):
    """The measure jobs of the later runs (s6: ten runs, 100 jobs; s7: two runs, 20 jobs): their stored step records, and the CPU
    model of each one that returned results.

    The step records are a copy of what the Actions API gave for the runs (tests/data/s6_job_steps.json, s7_job_steps.json).
    A job has a result folder in results/<prefix>-run-<id>/ exactly when its upload step succeeded; that is checked here.
    """
    out = []
    for run in J(steps)["runs"]:
        for job in run["jobs"]:
            hits = glob.glob(os.path.join(REPO, "results", f"{prefix}-run-{run['run']}", f"results-*-j{job['job']}", "results.json"))
            assert len(hits) <= 1, f"run {run['run']} job {job['job']}: {len(hits)} result folders"
            cpu = None
            if hits:
                record = J(os.path.relpath(hits[0], REPO).replace("\\", "/"))
                cpu = record["run"]["runner"]["cpu_model"]
                assert record["run"]["workflow_run_url"] == PUBLIC_RUN_PREFIX + str(run["run"]), \
                    f"run {run['run']} job {job['job']}: the record links to {record['run']['workflow_run_url']}"
            assert (cpu is not None) == (job["upload"] == "success"), \
                f"run {run['run']} job {job['job']}: upload step {job['upload']!r} but a result folder {'exists' if hits else 'is missing'}"
            out.append(dict(job, run=run["run"], cpu=cpu))
    return out


MODEL_KEYS = ("9V74", "9V45", "6973P-C", "8573C", "7763", "8370C")


def later_losses():
    """What the stored step records say about the 100 jobs of the ten later runs, as the README and DETAILS.md type it."""
    jobs = later_job_records()
    lr = later_runs()
    assert len(jobs) == lr["dispatched"], f"{len(jobs)} step records, {lr['dispatched']} jobs dispatched"
    returned = [j for j in jobs if j["cpu"] is not None]
    lost = [j for j in jobs if j["cpu"] is None]
    assert len(returned) == lr["returned"]
    assert all(j["timing"] == "success" for j in jobs), "a job did not finish its timing step"
    assert all(j["check"] != "success" and j["upload"] != "success" for j in lost), "a lost job finished the check step or uploaded"
    in_progress = [j for j in lost if j["check"] == "in_progress"]
    failed = [j for j in lost if j["check"] == "failure"]
    assert len(in_progress) + len(failed) == len(lost), f"lost jobs by check step: {sorted({j['check'] for j in lost})}"
    models = {}
    for j in returned:
        models[j["cpu"]] = models.get(j["cpu"], 0) + 1
    # the returned jobs per CPU model must agree with what the 75-job pool adds to the original pool
    pooled = {c["cpu_model"]: c["jobs"] for c in J(POOLED_S6)["cpus"]}
    original = {c["cpu_model"]: c["jobs"] for c in J(POOLED_ORIGINAL)["cpus"]}
    for model, n in pooled.items():
        assert models.get(model, 0) == n - original.get(model, 0), f"{model}: {models.get(model, 0)} returned jobs, the pools differ by {n - original.get(model, 0)}"
    only_7763 = [j for j in returned if "7763" in j["cpu"]]
    others = [j for j in returned if "7763" not in j["cpu"]]
    assert len(only_7763) == 1, f"the sentence names one returned EPYC 7763 job; there are {len(only_7763)}"
    by_model = {key: sum(n for model, n in models.items() if key in model) for key in MODEL_KEYS}
    assert sum(by_model.values()) == len(returned), f"returned jobs by CPU model: {models}"
    return {
        "jobs": jobs, "returned": returned, "lost": lost,
        "finished": len(jobs),
        "t_lo": f1(min(j["timing_min"] for j in jobs)), "t_hi": f1(max(j["timing_min"] for j in jobs)),
        "t_lost": f1(statistics.mean(j["timing_min"] for j in lost)),
        "t_ret": f1(statistics.mean(j["timing_min"] for j in returned)),
        "in_progress": len(in_progress), "failed": len(failed),
        "f_lo": f1(min(j["check_min"] for j in failed)), "f_hi": f1(max(j["check_min"] for j in failed)),
        "r_lo": f1(min(j["check_min"] for j in others)), "r_hi": f1(max(j["check_min"] for j in others)),
        "r7763": f1(only_7763[0]["check_min"]),
        "cancelled_back": len([j for j in returned if j["conclusion"] == "cancelled"]),
        "by_model": by_model,
    }


def newest_losses():
    """What the stored step records say about the 20 jobs of the two newest runs, which all returned results."""
    jobs = later_job_records("s7", STEP_RECORDS_S7)
    nr, lr, ll = newest_runs(), later_runs(), later_losses()
    assert len(jobs) == nr["dispatched"], f"{len(jobs)} step records, {nr['dispatched']} jobs dispatched"
    assert all(j["cpu"] is not None for j in jobs), "a job of the two newest runs returned nothing"
    assert all(j["conclusion"] == j["timing"] == j["check"] == j["upload"] == "success" for j in jobs), "a step of a newest job did not succeed"
    totals = [j["timing_min"] + j["check_min"] for j in jobs]
    assert min(totals) > lr["limit"], f"a newest job finished its timing and check steps within the old {lr['limit']}-minute limit"
    assert max(totals) < nr["now"], f"a newest job took {max(totals):.1f} minutes in two steps, over the {nr['now']}-minute limit"
    models = {}
    for j in jobs:
        models[j["cpu"]] = models.get(j["cpu"], 0) + 1
    by_model = {key: sum(n for model, n in models.items() if key in model) for key in MODEL_KEYS}
    assert sum(by_model.values()) == len(jobs), f"newest jobs by CPU model: {models}"
    prev = [j["check_min"] for j in ll["returned"]]
    return {
        "jobs": jobs, "by_model": by_model,
        "t_lo": f1(min(j["timing_min"] for j in jobs)), "t_hi": f1(max(j["timing_min"] for j in jobs)),
        "c_lo": f1(min(j["check_min"] for j in jobs)), "c_hi": f1(max(j["check_min"] for j in jobs)),
        "tot_lo": f1(min(totals)), "tot_hi": f1(max(totals)), "margin": f1(nr["now"] - max(totals)),
        "prev_lo": f1(min(prev)), "prev_hi": f1(max(prev)),
    }


def upload_comes_first():
    """True when measure.yml uploads the results before its check step."""
    with open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        wf = f.read()
    job = wf.split("\n  combine:")[0]
    up, check = job.find("- name: Upload results"), job.find("- name: Check the results without a compiler")
    return 0 <= up < check


def scev_tally():
    """Clang 18.1.0 FAST: loops with a count for every exit (all vectorized), loops without (none vectorized), mismatches."""
    with open(os.path.join(REPO, "investigate", "vectorizer", "reverse-stride2", "extracted", "scalar-evolution.txt"),
              encoding="utf-8") as f:
        text = f.read()
    yes = no = bad = 0
    for sec in re.split(r"^## ", text, flags=re.M)[1:]:
        if sec.startswith("c18,") and "hardening FAST" in sec.split("\n", 1)[0]:
            m = re.search(r"tally: computable and vectorized (\d+), not computable and not vectorized (\d+), mismatch (\d+)", sec)
            yes, no, bad = yes + int(m.group(1)), no + int(m.group(2)), bad + int(m.group(3))
    assert bad == 0, f"{bad} loops are counted and not vectorized, or the reverse"
    return yes, no


def handwritten_bound():
    """The 14 hand-written stride-2 functions: how many got a count, how many were vectorized (the same ones)."""
    with open(os.path.join(REPO, "investigate", "vectorizer", "reverse-stride2", "extracted", "handwritten-bound.txt"),
              encoding="utf-8") as f:
        rows = [l.split() for l in f if re.match(r"^(full|ashr2|lshr1|and62|umin40|ptr_ashr|ptr_lshr)\s", l)]
    counted = [r for r in rows if r[2] == "count"]
    assert all((r[2] == "count") == (r[5] == "yes") for r in rows), "the vectorizer's decision no longer follows the count"
    return len(rows), len(counted)


def vectorizer_raw_answers():
    return len(os.listdir(os.path.join(REPO, "investigate", "vectorizer", "reverse-stride2", "raw")))


def matmul_compare_cost(name, vf=4):
    """The cost the loop vectorizer logged for each bounds-check compare in one saved Compiler Explorer answer."""
    d = J(f"investigate/vectorizer/matmul/raw/{name}.json")
    found = re.findall(rf"Found an estimated cost of (\d+) for VF {vf} For instruction:\s+%cmp\.i\d+ = icmp (?:ugt|ult)",
                       json.dumps(d["response"]))
    assert len(found) == 2 and len(set(found)) == 1, f"{name}: expected the same cost for the two compares, got {found}"
    return int(found[0])


def matmul_sums(title):
    """(scalar loop cost, width-4 vector loop cost) printed in the per-instruction table of one compiler."""
    with open(os.path.join(REPO, "investigate", "vectorizer", "matmul", "derived", "cost-table.md"), encoding="utf-8") as f:
        sections = f.read().split("\n## ")
    sec = next(s for s in sections if s.startswith(title))
    m = re.search(r"\| \*\*sum\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|", sec)
    return int(m.group(1)), int(m.group(2))


def matmul_requests():
    with open(os.path.join(REPO, "investigate", "vectorizer", "matmul", "requests.tsv"), encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip()]
    assert all(r[1] == "compile" and r[3] == "200" for r in rows), "a logged request was not a compile answered with HTTP 200"
    return len(rows)


def llvm_commit():
    sha = J("investigate/vectorizer/matmul/llvm-src/commit_b6a8f5486b.json")["sha"]
    tags = {r["tag"]: r["status"] for r in J("investigate/vectorizer/matmul/llvm-src/commit_in_tag.json")["rows"]
            if r["commit"] == sha}
    return sha[:10], tags


def exp_shared_machines():
    pooled = J(POOLED)
    amd = [c["jobs"] for c in pooled["cpus"] if "AMD" in c["cpu_model"]]
    main_xeon = {c["jobs"] for c in enough_cpus() if is_intel(c["cpu_model"])}
    assert len(main_xeon) == 1, f"the README says '7 for each of the two main Xeon models'; they have {sorted(main_xeon)}"
    third = [c["jobs"] for c in pooled["cpus"] if is_intel(c["cpu_model"]) and c["jobs"] < J("site/data/index.json")["criteria"]["minimum_jobs"]]
    assert len(third) == 1, f"the README names one Xeon model with too few jobs; the pool has {third}"
    lr, nr = later_runs(), newest_runs()
    ll = later_losses()
    assert upload_comes_first(), "the README says the workflow now uploads first; measure.yml still checks before it uploads"
    by = ll["by_model"]
    old_7763 = cpu_like("7763", original=True)["jobs"]
    later = pooled_jobs() - pooled_jobs(original=True)
    assert later == lr["returned"] + nr["returned"], f"{later} later jobs in the pool, {lr['returned']} + {nr['returned']} in the result folders"
    return {"jobs": str(pooled_jobs()), "runs": str(len(pooled["runs"])), "lo": str(min(amd)), "hi": str(max(amd)),
            "x": str(main_xeon.pop()), "third": str(third[0]), "new": str(later), "twelve": word(lr["runs"] + nr["runs"]),
            "ten": word(lr["runs"]), "ret": str(lr["returned"]), "disp": str(lr["dispatched"]),
            "fin": str(ll["finished"]), "lost": str(len(ll["lost"])), "limit": str(lr["limit"]), "ret2": str(lr["returned"]),
            "e": str(by["7763"]), "f": str(old_7763), "g": str(pooled_jobs(original=True))}


def exp_newest_runs_readme():
    nr, lr, nl = newest_runs(), later_runs(), newest_losses()
    return {"two": word(nr["runs"]), "now": str(nr["now"]), "ret": str(nr["returned"]), "disp": str(nr["dispatched"]),
            "n7763": str(nl["by_model"]["7763"]), "old": str(lr["limit"])}


def exp_compile_only_counts():
    yes, no = scev_tally()
    return {"n": str(yes + no), "yes": str(yes), "no": str(no)}


def exp_matmul_units_readme():
    scalar, vector = matmul_sums("clang 18.1.0 (assertions), FAST")
    return {"u": str(matmul_compare_cost("dbg_a18_fast")), "v": str(vector), "s": str(4 * scalar)}


def exp_cost_units_across_versions():
    new = {matmul_compare_cost(f"dbg_a{v}_fast") for v in (19, 20, 21)}
    assert len(new) == 1, f"clang 19, 20 and 21 price the compares differently: {new}"
    return {"new": str(new.pop()), "old": str(matmul_compare_cost("dbg_a18_fast"))}


def exp_commit_readme():
    sha, tags = llvm_commit()
    assert tags["llvmorg-19.1.0"] == "ahead" and tags["llvmorg-18.1.0"] != "ahead", "the commit is not between clang 18 and 19"
    return {"sha": sha}


def exp_kernel_pool_folders():
    return {"o": str(len(glob.glob(os.path.join(REPO, "results", "s4-run-*", "results-*", "results.json")))),
            "n": str(later_runs()["returned"]), "m": str(newest_runs()["returned"]),
            "s6": str(pooled_jobs(pool=POOLED_S6))}


# ---- the Arm column (results/s8-arm-pooled and the per-job files of results/s8-arm-run-*) ------------
# One CPU model (Neoverse-N2), pooled apart from the x86-64 jobs. Nothing here reads or changes an x86-64 pool, except the
# sentences that set an x86-64 number beside an Arm one: those reuse the x86-64 expectations above.

ARM_POOLED = "results/s8-arm-pooled/pooled.json"
ARM_TIMELINE = "tests/data/s8_arm_timeline.json"
ARM_KERNELS = {"k01_sum_fwd": "forward sum", "k02_add_fwd": "forward add", "k03_stencil": "stencil", "k04_rev": "reverse",
               "k05_stride2": "stride-2", "k06_gather": "gather", "k07_hist": "histogram", "k08_matmul": "matrix multiply"}
ARM_BUILDS = ("none", "fast", "novec", "none_a64", "fast_a64")
ARM_COLUMNS = ("as_compiled", "aligned")
# written again here on purpose (the same pattern as harness/placement.py's _NEON); an SVE register is a z or p register
ARM_NEON = re.compile(r"\bv\d+\.\d*[bhsd]\b|\bq\d+\b")
ARM_SVE = re.compile(r"\bz\d+(?:\.[bhsdq])?\b|\bp\d+(?:\.[bhsd]|/[zm])")
ARM_INSN = re.compile(r"^\s*([0-9a-f]+):\t(.*)$")
ARM_BRANCH = re.compile(r"^(?:b\.[a-z]+|cbn?z|tbn?z|b)$")
TRAP_REMARK = "could not determine number of loop iterations"


def arm_pool():
    d = J(ARM_POOLED)
    assert len(d["cpus"]) == 1, f"the Arm pool has {len(d['cpus'])} CPU models; the text says one"
    return d


def arm_cpu():
    return arm_pool()["cpus"][0]


def arm_cell(cid):
    return cell_of(arm_cpu(), cid)


def arm_ratio(cid, column="as_compiled"):
    return arm_cell(cid)[column]["ratio"]


def pct1z(ratio):
    """pct1 without a minus sign on a zero."""
    s = pct1(ratio)
    return "0.0" if s == "-0.0" else s


def rel_hw(stat):
    """The half-width of an interval as a percent of its ratio."""
    return (stat["ci95"][1] - stat["ci95"][0]) / 2 / stat["ratio"] * 100


def arm_label(cell, column):
    return f"{ARM_KERNELS[cell['kernel']]}, {'aligned' if column == 'aligned' else 'as compiled'}"


@lru_cache(maxsize=None)
def arm_jobs():
    """[(job folder, results.json, details.json)] for every job the Arm pool lists."""
    base = os.path.dirname(os.path.join(REPO, ARM_POOLED))
    out = []
    for i in arm_pool()["inputs"]:
        rel = os.path.relpath(os.path.normpath(os.path.join(base, os.path.dirname(i["path"]))), REPO).replace("\\", "/")
        out.append((rel, J(rel + "/results.json"), J(rel + "/details.json")))
    return out


def arm_insns(rel, name):
    """(all lines, [(address, text)] of the instruction lines) of one saved listing."""
    with open(os.path.join(REPO, rel, "asm", name), encoding="utf-8") as f:
        lines = f.read().splitlines()
    return lines, [(int(m.group(1), 16), m.group(2)) for m in map(ARM_INSN.match, lines) if m]


def mnemonic(text):
    return text.split("\t")[0]


@lru_cache(maxsize=None)
def arm_build_facts():
    """{(kernel, build): NEON instructions, traps (brk #0x1), listing lines, SVE instructions, csel instructions}; every job must agree."""
    facts = {}
    for rel, _, _ in arm_jobs():
        for k in ARM_KERNELS:
            for b in ARM_BUILDS:
                lines, insns = arm_insns(rel, f"{k}.{b}.s")
                got = {"neon": sum(1 for _, t in insns if ARM_NEON.search(t)),
                       "traps": sum(1 for _, t in insns if t.startswith("brk\t#0x1")),
                       "brk_forms": sorted({t.split("\t", 1)[1] for _, t in insns if mnemonic(t) == "brk"}),
                       "lines": len(lines), "sve": sum(1 for _, t in insns if ARM_SVE.search(t)),
                       "csel": sum(1 for _, t in insns if mnemonic(t) == "csel")}
                if (k, b) in facts:
                    assert facts[(k, b)] == got, f"{rel}/asm/{k}.{b}.s gives {got}, the first job's gives {facts[(k, b)]}"
                else:
                    facts[(k, b)] = got
    return facts


@lru_cache(maxsize=None)
def arm_vectorization():
    """{(kernel, build): vectorized, width, interleave, the first remark} for NONE and FAST; every job must agree."""
    out = {}
    for rel, _, det in arm_jobs():
        for k in ARM_KERNELS:
            for b in ("none", "fast"):
                v = det["kernels"][k][b]["vectorization"]
                m = re.search(r"vectorization width: (\d+), interleaved count: (\d+)", " ".join(v["remarks"]))
                got = {"vectorized": v["vectorized"], "width": int(m.group(1)) if m else None,
                       "interleave": int(m.group(2)) if m else None, "remark": v["remarks"][0] if v["remarks"] else ""}
                if (k, b) in out:
                    assert out[(k, b)] == got, f"{rel}: {k} {b} vectorization {got}, the first job's {out[(k, b)]}"
                else:
                    out[(k, b)] = got
    return out


@lru_cache(maxsize=None)
def arm_matmul():
    """The matrix-multiply listings read for the sentences about them: line counts, the NEON loop of each build and where the
    branches to the trap are in the FAST build. Every job must agree."""
    out = None
    for rel, _, det in arm_jobs():
        got = {}
        spans = {}
        for b in ("none", "fast"):
            lines, insns = arm_insns(rel, f"k08_matmul.{b}.s")
            loops = det["kernels"]["k08_matmul"][b]["loops"]
            neon = [l for l in loops if l["simd"] and l["innermost"]]
            scalar = [l for l in loops if not l["simd"] and l["innermost"]]
            assert len(neon) == 1, f"{rel}: {len(neon)} innermost NEON loops in the {b} build"
            spans[b] = (neon[0], scalar)
            lo, hi = int(neon[0]["start"], 16), int(neon[0]["end"], 16)
            texts = [t for a, t in insns if lo <= a < hi]
            body = [mnemonic(t) for t in texts]
            assert len(body) == neon[0]["insns"], f"{rel}: the NEON loop of the {b} build has {len(body)} instructions, the record says {neon[0]['insns']}"
            got[b] = {"lines": len(lines), "loop": body,
                      "mla_4s": sum(1 for t in texts if mnemonic(t) == "mla" and re.search(r"\bv\d+\.4s\b", t))}
        _, insns = arm_insns(rel, "k08_matmul.fast.s")
        traps = [a for a, t in insns if t.startswith("brk\t#0x1")]
        assert len(traps) == 1, f"{rel}: {len(traps)} traps in the FAST matrix multiply"
        branches = [(a, mnemonic(t)) for a, t in insns if ARM_BRANCH.match(mnemonic(t)) and re.search(rf"\b{traps[0]:x} <", t)]
        to_trap = [a for a, _ in branches]
        neon, scalar = spans["fast"]
        assert len(scalar) == 1, f"{rel}: {len(scalar)} innermost scalar loops in the FAST build"
        inside = lambda l: sum(1 for a in to_trap if int(l["start"], 16) <= a < int(l["end"], 16))
        got["to_trap"], got["in_neon_loop"], got["in_scalar_loop"] = len(to_trap), inside(neon), inside(scalar[0])
        # the sentences call them conditional branches: no plain `b` may lead to the trap
        got["to_trap_plain_b"] = sum(1 for _, mn in branches if mn == "b")
        # the select-type instructions of the two listings, counted by mnemonic
        for b in ("none", "fast"):
            _, ins = arm_insns(rel, f"k08_matmul.{b}.s")
            got[b]["selects"] = {name: sum(1 for _, t in ins if mnemonic(t) == name) for name in ("csel", "cset", "csinc")}
        if out is None:
            out = got
        else:
            assert out == got, f"{rel}: the matrix-multiply listings differ from the first job's"
    return out


@lru_cache(maxsize=None)
def arm_matmul_d():
    """The matrix size d of the two matrix-multiply cells (every job must use the same)."""
    seen = {size: {det["cells"][f"k08_matmul.{size}"]["n"] for _, _, det in arm_jobs()} for size in ("L1", "L2")}
    assert all(len(v) == 1 for v in seen.values()), f"jobs use different matrix sizes: {seen}"
    return {size: v.pop() for size, v in seen.items()}


@lru_cache(maxsize=None)
def arm_forward_sum_identical():
    """True when the forward sum's listing is the same line for line in the NONE and FAST builds in every job."""
    return all(arm_insns(rel, "k01_sum_fwd.none.s")[0] == arm_insns(rel, "k01_sum_fwd.fast.s")[0] for rel, _, _ in arm_jobs())


def arm_toolchain():
    seen = {(res["run"]["toolchain"]["clang"], res["run"]["toolchain"]["libcxx_package"]) for _, res, _ in arm_jobs()}
    assert len(seen) == 1, f"the Arm jobs recorded {seen}"
    clang, lib = seen.pop()
    return {"clang": re.search(r"Ubuntu clang version ([\d.]+)", clang).group(1), "clang_full": clang.replace("Ubuntu clang version ", ""),
            "lib_major": re.search(r"libc\+\+-(\d+)-dev", lib).group(1), "lib_version": lib.split(" ", 1)[1]}


def arm_start_window():
    starts = sorted(res["run"]["started_at"] for _, res, _ in arm_jobs())
    parse = lambda s: datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    days = {s[:10] for s in starts}
    assert len(days) == 1, f"the Arm jobs started on {sorted(days)}"
    year, month, day = (int(x) for x in days.pop().split("-"))
    return {"first": starts[0][11:16], "last": starts[-1][11:16], "day": f"{MONTHS[month - 1]} {day}", "month": MONTHS[month - 1], "year": str(year),
            "within": math.ceil((parse(starts[-1]) - parse(starts[0])).total_seconds() / 60)}


def arm_plan_text():
    with open(os.path.join(REPO, "arm64", "PLAN.md"), encoding="utf-8") as f:
        return " ".join(f.read().split())


def arm_timeline():
    t = J(ARM_TIMELINE)
    hhmm = lambda s: s[11:16]
    utc = datetime.datetime.fromisoformat(t["plan_commit"]["author_date"]).astimezone(datetime.timezone.utc)
    local = datetime.datetime.fromisoformat(t["plan_commit"]["author_date"])
    return {"smoke": str(t["smoke"]["run"]), "smoke_at": hhmm(t["smoke"]["created_at"]), "smoke_date": t["smoke"]["created_at"][:10],
            "dispatched": {hhmm(r["created_at"]) for r in t["full_runs"]},
            "first_done": hhmm(min(r["first_job_completed_at"] for r in t["full_runs"])),
            "plan_utc": utc.strftime("%H:%M"), "plan_local": local.strftime("%H:%M")}


# ---- expected values: arm64/README.md, README.md and readme-parts/DETAILS.md ----------------------------------

def exp_arm_table_row(kernel):
    def fn():
        facts = arm_build_facts()
        return {"n0": str(facts[(kernel, "none")]["neon"]), "n1": str(facts[(kernel, "fast")]["neon"]),
                "c1": f3(arm_ratio(kernel + ".L1")), "a1": f3(arm_ratio(kernel + ".L1", "aligned")),
                "c2": f3(arm_ratio(kernel + ".L2")), "a2": f3(arm_ratio(kernel + ".L2", "aligned"))}
    return fn


def arm_table_pattern(label):
    return (r"\| " + re.escape(label) + r" \| (?P<n0>\d+) / (?P<n1>\d+) \| (?P<c1>[\d.]+) \((?P<a1>[\d.]+)\) \| "
            r"(?P<c2>[\d.]+) \((?P<a2>[\d.]+)\) \|")


def arm_counts():
    c = arm_cpu()
    assert c["jobs"] == len(arm_jobs()) == len(arm_pool()["inputs"]), "the Arm pool and its job folders disagree on the job count"
    return {"jobs": c["jobs"], "runs": len(c["runs"])}


def exp_arm_counts_digits():
    n = arm_counts()
    return {"jobs": str(n["jobs"]), "runs": str(n["runs"]), "model": arm_cpu()["cpu_model"]}


def exp_arm_short_reverse():
    facts, vec = arm_build_facts(), arm_vectorization()
    for k in ("k04_rev", "k05_stride2"):
        assert not vec[(k, "fast")]["vectorized"] and TRAP_REMARK in vec[(k, "fast")]["remark"], f"{k} FAST: {vec[(k, 'fast')]}"
        assert facts[(k, "fast")]["neon"] == 0 and facts[(k, "none")]["neon"] > 0
    lost = {x["kernel"] for x in arm_cpu()["cells"] if x["class"] == "lost"}
    return {"r1": f2(arm_ratio("k04_rev.L1")), "s1": f2(arm_ratio("k05_stride2.L1")),
            "r2": f2(arm_ratio("k04_rev.L2")), "s2": f2(arm_ratio("k05_stride2.L2")),
            "rn": str(facts[("k04_rev", "none")]["neon"]), "sn": str(facts[("k05_stride2", "none")]["neon"]), "two": word(len(lost))}


def exp_arm_short_matmul():
    v = exp_details_versions()
    assert arm_vectorization()[("k08_matmul", "none")]["vectorized"] and arm_vectorization()[("k08_matmul", "fast")]["vectorized"]
    return {"m1": f2(arm_ratio("k08_matmul.L1")), "m2": f2(arm_ratio("k08_matmul.L2")), "xlo": v["lo"], "xhi": v["hi"],
            "ca": arm_toolchain()["clang"].split(".")[0], "cx": exp_x86_clang_major()["c"]}


def forward_cells(size):
    return [f"{k}.{size}" for k in FORWARD]


def exp_arm_short_forward():
    v = [arm_ratio(c) for c in forward_cells("L1")]
    return {"lo": f3(min(v)), "hi": f3(max(v)), "aa": f3(arm_cpu()["aa"]["half_width_pct"])}


def exp_arm_short_gather():
    return {"g": f2(arm_ratio("k06_gather.L1")), "h": f2(arm_ratio("k07_hist.L1"))}


def arm_forward_limit():
    return 1 + arm_cpu()["verdict"]["forward_limit_pct"] / 100


def exp_arm_short_verdict():
    c = arm_cpu()
    assert c["verdict"]["form"] == "inconclusive" and "missed by k02_add_fwd.L2;" in c["verdict"]["why"], c["verdict"]["why"]
    return {"hi": f3(arm_cell("k02_add_fwd.L2")["aligned"]["ci95"][1]), "lim": f2(arm_forward_limit())}


def exp_arm_runner():
    seen = {json.dumps(res["run"]["runner"], sort_keys=True) for _, res, _ in arm_jobs()}
    assert len(seen) == 1, f"the Arm jobs ran on {len(seen)} different machines"
    r = arm_jobs()[0][1]["run"]["runner"]
    lscpu = {k.strip(): v.strip() for k, _, v in (ln.partition(":") for ln in arm_jobs()[0][2]["lscpu"].splitlines())}
    assert lscpu["Thread(s) per core"] == "1" and lscpu["Model name"] == r["cpu_model"] == arm_cpu()["cpu_model"]
    flags = lscpu["Flags"].split()
    assert "sve" in flags and "sve2" in flags, "lscpu no longer lists SVE and SVE2"
    assert all(f["sve"] == 0 for f in arm_build_facts().values()), "a listing contains an SVE instruction"
    return {"cpus": str(r["cores"]), "l1": str(r["l1d_kib"]), "l2": str(r["l2_kib"]), "l3": str(r["l3_kib"]),
            "os": r["os"], "kernel": r["kernel"]}


def exp_arm_toolchain():
    t = arm_toolchain()
    flags = arm_jobs()[0][1]["run"]["flags"]
    commands = [bd["command"] for _, _, det in arm_jobs() for kd in det["kernels"].values() for bd in kd.values() if isinstance(bd, dict) and "command" in bd]
    assert not any("-march" in x or "-mcpu" in x for x in commands), "a build command names -march or -mcpu"
    assert "-fno-vectorize" in flags["novec"] and "-falign-loops=64" in flags["align"]
    return {"clang": t["clang_full"], "lm": t["lib_major"], "lib": t["lib_version"], "common": flags["common"], "align": flags["align"]}


def exp_arm_sizes():
    det = arm_jobs()[0][2]
    assert all(d["sizes_requested"] == ["L1", "L2"] for _, _, d in arm_jobs()), "a job timed a size other than L1 and L2"
    assert all(d["size_targets_bytes"] == det["size_targets_bytes"] and d["cache_bytes"] == det["cache_bytes"] for _, _, d in arm_jobs())
    t, c = det["size_targets_bytes"], det["cache_bytes"]
    assert 2 * t["L1"] == c["l1d"] and 2 * t["L2"] == c["l2"], "the working sets are no longer half of the per-core caches"
    d = arm_matmul_d()
    return {"k": word(len(ARM_KERNELS)), "l1": str(t["L1"] // 1024), "l2": str(t["L2"] // 1024), "d1": str(d["L1"]), "d2": str(d["L2"])}


def exp_arm_timing():
    reps = {d["reps_per_side"] for _, _, d in arm_jobs()}
    assert len(reps) == 1
    assert all(re.fullmatch(r"\d+", str(d["pinned_cpu"])) for _, _, d in arm_jobs()), "a job pinned more than one vCPU"
    return {"reps": str(reps.pop()), "one": word(1)}


def exp_arm_align_flag():
    flag = arm_jobs()[0][1]["run"]["flags"]["align"]
    return {"a": flag, "b": flag}


def exp_arm_runs():
    c = arm_cpu()
    w = arm_start_window()
    per = {jobs_per_run()}
    by_run = {rid: sum(1 for i in arm_pool()["inputs"] if i["run_id"] == rid) for rid in c["runs"]}
    assert set(by_run.values()) == per, f"jobs per run {by_run}, the workflow dispatches {per}"
    a, b, cc = c["runs"]
    return {"three": word(len(c["runs"])), "a": a, "b": b, "c": cc, "per": str(per.pop()), "n": str(c["jobs"]), "n2": str(c["jobs"]),
            "t1": w["first"], "t2": w["last"], "day": w["day"], "n3": str(c["jobs"])}


def exp_arm_min_jobs():
    return {"min": str(J("harness/criteria-v3.json")["v3"]["pooling"]["minimum_jobs"])}


def exp_arm_intervals():
    c = arm_cpu()
    out = {}
    for size, tag in (("L1", "1"), ("L2", "2")):
        cells = [(x, col) for x in c["cells"] if x["size_class"] == size for col in ARM_COLUMNS]
        w = max(cells, key=lambda t: rel_hw(t[0][t[1]]))
        s = max(cells, key=lambda t: t[0][t[1]]["between_job_sd_pct"])
        out["w" + tag], out["c" + tag] = f2(rel_hw(w[0][w[1]])), arm_label(*w)
        out["s" + tag], out["d" + tag] = f2(s[0][s[1]]["between_job_sd_pct"]), arm_label(*s)
    return out


def exp_arm_rev_stride2_prose():
    v, facts = arm_vectorization(), arm_build_facts()
    for k in ("k04_rev", "k05_stride2"):
        assert (v[(k, "none")]["width"], v[(k, "none")]["interleave"]) == (4, 2), f"{k} NONE: {v[(k, 'none')]}"
        assert facts[(k, "fast")]["traps"] == 1 and facts[(k, "fast")]["neon"] == 0
    pos = arm_cpu()["positive"]
    return {"w": "4", "i": "2", "trap": word(facts[("k04_rev", "fast")]["traps"]),
            "ir": f2(arm_cell("k04_rev.L1")["instr"]["ratio"]), "is": f2(arm_cell("k05_stride2.L1")["instr"]["ratio"]),
            "nr": f2(pos["k04_rev.L1"]["ratio"]), "ns": f2(pos["k05_stride2.L1"]["ratio"]),
            "r": f2(arm_ratio("k04_rev.L1")), "nr2": f2(pos["k04_rev.L1"]["ratio"]),
            "s": f2(arm_ratio("k05_stride2.L1")), "ns2": f2(pos["k05_stride2.L1"]["ratio"])}


def exp_arm_cesweep():
    rows = [r for r in J("site/data/cesweep.json")["rows"]
            if r["family"] == "clang" and r["target"] == "aarch64" and r["opt"] == "-O2" and r["macro_effective"] and r["version"] == "18.1.0"]
    assert len(rows) == 1, f"{len(rows)} AArch64 rows for clang 18.1.0 at -O2 in the sweep"
    timed_lost = sorted(c["kernel"] for c in arm_cpu()["cells"] if c["class"] == "lost" and c["size_class"] == "L1")
    assert sorted(rows[0]["lost"]) == timed_lost == ["k04_rev", "k05_stride2"], f"sweep {rows[0]['lost']}, timed {timed_lost}"
    kept = {c["kernel"] for c in arm_cpu()["cells"] if c["class"] == "kept"}
    assert kept == {"k01_sum_fwd", "k02_add_fwd", "k03_stencil", "k08_matmul"}, kept
    return {"v": rows[0]["version"]}


def exp_arm_matmul_observed():
    """The NEON loop and the line counts: what is read straight from the two listings."""
    m = arm_matmul()
    assert m["none"]["loop"] == m["fast"]["loop"], "the NEON loop differs between the NONE and FAST builds"
    assert m["none"]["mla_4s"] == m["fast"]["mla_4s"] == m["none"]["loop"].count("mla"), "an mla in the NEON loop is not a v.4s one"
    return {"nine": word(len(m["none"]["loop"])), "two": word(m["none"]["mla_4s"]),
            "fl": str(m["fast"]["lines"]), "nl": str(m["none"]["lines"]), "extra": str(m["fast"]["lines"] - m["none"]["lines"])}


def exp_arm_matmul_listing():
    """The select instructions and the branches to the trap, read from the listings of every job."""
    m, facts = arm_matmul(), arm_build_facts()
    sel_none, sel_fast = m["none"]["selects"], m["fast"]["selects"]
    assert sel_none["csel"] == 0 and facts[("k08_matmul", "none")]["csel"] == 0, "the NONE matrix multiply now contains csel"
    assert sel_fast["csel"] == facts[("k08_matmul", "fast")]["csel"], "two counts of csel in the FAST listing disagree"
    assert m["in_neon_loop"] == 0, "a branch to the trap is inside the NEON loop"
    assert m["to_trap_plain_b"] == 0, "an unconditional branch leads to the trap, so the sentences must not call them all conditional"
    example = f"{arm_jobs()[0][0]}/asm/k08_matmul.fast.s"
    assert os.path.exists(os.path.join(REPO, example)), f"{example} does not exist"
    return {"csel": str(sel_fast["csel"]), "cset": word(sel_none["cset"]), "csinc": word(sel_none["csinc"]),
            "three": word(m["to_trap"]), "path": example, "two": word(m["in_scalar_loop"]), "two2": word(m["in_scalar_loop"])}


def arm_matmul_log_share(size):
    """log(time ratio) / log(instruction ratio) of a matrix-multiply cell, as compiled."""
    c = arm_cell(f"k08_matmul.{size}")
    return math.log(c["as_compiled"]["ratio"]) / math.log(c["instr"]["ratio"])


def exp_arm_matmul_time_vs_instr():
    c1, c2 = arm_cell("k08_matmul.L1"), arm_cell("k08_matmul.L2")
    return {"i1": f2(c1["instr"]["ratio"]), "i2": f2(c2["instr"]["ratio"]), "t1": f2(c1["as_compiled"]["ratio"]), "t2": f2(c2["as_compiled"]["ratio"]),
            "l1": f2(arm_matmul_log_share("L1")), "l2": f2(arm_matmul_log_share("L2")),
            "rise": f0((c2["instr"]["ratio"] - 1) * 100), "tr": f1((c2["as_compiled"]["ratio"] - 1) * 100)}


def exp_arm_matmul_inferred():
    """The arithmetic of the inferred reading: passes of the NEON loop and the scalar remainder at the two d."""
    d, v = arm_matmul_d(), arm_vectorization()[("k08_matmul", "none")]
    per = v["width"] * v["interleave"]
    cost = arm_site()["matmul_cost"]
    assert (cost["vector_pass_elements"], cost["sizes"]["L1"]["whole_passes"], cost["sizes"]["L1"]["d_mod_pass"]) == (per, d["L1"] // per, d["L1"] % per)
    assert (cost["sizes"]["L2"]["whole_passes"], cost["sizes"]["L2"]["d_mod_pass"]) == (d["L2"] // per, d["L2"] % per)
    return {"d1": str(d["L1"]), "p1": str(d["L1"] // per), "e": str(per), "r1": str(d["L1"] % per),
            "d2": str(d["L2"]), "p2": str(d["L2"] // per), "r2": str(d["L2"] % per),
            "i1": f2(arm_cell("k08_matmul.L1")["instr"]["ratio"]), "i2": f2(arm_cell("k08_matmul.L2")["instr"]["ratio"])}


# the d values the plan for the cheap check names; the properties the sentence gives them are checked against the data here
ARM_D_SWEEP = {"inside": (28, 44, 52, 60, 68), "beyond": (76, 100, 148, 212, 276), "multiple_of_pass": (48, 56, 208)}


def exp_arm_matmul_d_sweep():
    d, v = arm_matmul_d(), arm_vectorization()[("k08_matmul", "none")]
    per = v["width"] * v["interleave"]
    l1d = arm_jobs()[0][2]["cache_bytes"]["l1d"]
    fits = lambda n: 3 * n * n * 4 <= l1d  # three d x d int32 matrices
    biggest = max(n for n in range(1, 400) if fits(n))
    s = ARM_D_SWEEP
    assert all(n % per == d["L1"] % per and fits(n) for n in s["inside"]), "a d inside L1d is not at the L1 remainder or does not fit"
    assert d["L1"] in s["inside"], "the measured L1 d is not among the d inside L1d"
    assert all(n % per == d["L1"] % per and not fits(n) for n in s["beyond"]), "a d beyond L1d is not at the L1 remainder or fits"
    assert all(n % per == 0 for n in s["multiple_of_pass"]), "a d is not a multiple of the elements per pass"
    j = lambda xs: ", ".join(str(x) for x in xs)
    return {"rem": str(d["L1"] % per), "per": str(per), "per2": str(per), "inside": j(s["inside"]), "kib": str(l1d // 1024), "max": str(biggest),
            "beyond": j(s["beyond"]), "zero": j(s["multiple_of_pass"])}


def exp_arm_vs_x86_matmul():
    v = exp_versions()
    return {"a": v["a"], "b": v["b"], "l1": v["l1"], "l2": v["l2"]}


def exp_arm_gather_hist():
    return {"g": f2(arm_ratio("k06_gather.L1")), "ga": f2(arm_ratio("k06_gather.L1", "aligned")), "h": f2(arm_ratio("k07_hist.L1")),
            "g2": f2(arm_ratio("k06_gather.L2")), "h2": f2(arm_ratio("k07_hist.L2")),
            "gi": f2(arm_cell("k06_gather.L1")["instr"]["ratio"]), "hi": f2(arm_cell("k07_hist.L1")["instr"]["ratio"])}


def arm_plan_aa_floor():
    m = re.search(r"If the A/A half-width is below ([\d.]+)%", arm_plan_text())
    assert m, "arm64/PLAN.md no longer gives the A/A half-width below which the forward loops are reported against it"
    return m.group(1)


def exp_arm_aa_floor():
    hws = [res["controls"]["aa"]["half_width_pct"] for _, res, _ in arm_jobs()]
    return {"plan": arm_plan_aa_floor(), "aa": f3(arm_cpu()["aa"]["half_width_pct"]), "j1": f3(min(hws)), "j2": f3(max(hws))}


def exp_arm_forward_bullets():
    c = {k: arm_cell(k + ".L1") for k in FORWARD}
    s, a, t = c["k01_sum_fwd"], c["k02_add_fwd"], c["k03_stencil"]
    return {"s1": pct1z(s["as_compiled"]["ratio"]), "sr": f3(s["as_compiled"]["ratio"]), "slo": f4(s["as_compiled"]["ci95"][0]),
            "shi": f4(s["as_compiled"]["ci95"][1]), "s2": pct1z(s["aligned"]["ratio"]),
            "a1": pct1z(a["as_compiled"]["ratio"]), "a2": pct1z(a["aligned"]["ratio"]),
            "t1": pct1z(t["as_compiled"]["ratio"]), "t2": pct1z(t["aligned"]["ratio"])}


def arm_forward_instr(kernel, size):
    """The instructions Cachegrind counts per call of a forward kernel in the NONE and FAST builds (site/data/arm64.json)."""
    rows = [c for c in arm_site()["forward_instr"]["cells"] if c["cell_id"] == f"{kernel}.{size}"]
    assert len(rows) == 1, f"{ARM_SITE} forward_instr has {len(rows)} rows for {kernel}.{size}"
    r = rows[0]
    for col in ARM_COLUMNS:
        assert r[col]["fast"] - r[col]["none"] == r[col]["added"], f"{kernel}.{size} {col}: added is not fast minus none"
        assert abs(r[col]["time_ratio"] - arm_cell(f"{kernel}.{size}")[col]["ratio"]) < 1e-12, f"{kernel}.{size} {col}: time ratio is not the pool's"
    return r


def exp_arm_short_add():
    a1, a2 = arm_forward_instr("k02_add_fwd", "L1"), arm_forward_instr("k02_add_fwd", "L2")
    assert a1["as_compiled"]["added"] == a2["as_compiled"]["added"], "the forward add adds a different number of instructions at L2"
    return {"pct": pct1z(arm_ratio("k02_add_fwd.L1")), "n": str(a1["as_compiled"]["added"]), "aa": f2(arm_noise()["identical_binary_aa"]["L2"]["pooled"]["half_width_pct"])}


def exp_arm_add_instructions():
    a1, a2 = arm_forward_instr("k02_add_fwd", "L1"), arm_forward_instr("k02_add_fwd", "L2")
    c1, c2 = a1["as_compiled"], a2["as_compiled"]
    assert c1["added"] == c2["added"] and a1["aligned"]["added"] == a2["aligned"]["added"], "the forward add adds a different number of instructions at L2"
    return {"n1": thousands(c1["none"]), "f1": thousands(c1["fast"]), "e1": thousands(a1["elements"]), "c1": str(c1["added"]),
            "al": str(a1["aligned"]["added"]), "n2": thousands(c2["none"]), "f2": thousands(c2["fast"]), "e2": thousands(a2["elements"]),
            "c2": str(c2["added"]), "p1": f2(c1["added"] / c1["none"] * 100), "p2": f2(c2["added"] / c2["none"] * 100)}


def exp_arm_stencil_instructions():
    s1, s2 = arm_forward_instr("k03_stencil", "L1"), arm_forward_instr("k03_stencil", "L2")
    assert all(s1[col]["added"] == s2[col]["added"] for col in ARM_COLUMNS), "the stencil adds a different number of instructions at L2"
    tc, ta = arm_ratio("k03_stencil.L1"), arm_ratio("k03_stencil.L1", "aligned")
    assert tc > 1 > ta, "the stencil's time ratio no longer changes sign with loop alignment"
    row = arm_lvp_row("k03_stencil.L1")
    return {"c": str(s1["as_compiled"]["added"]), "al": str(s1["aligned"]["added"]), "tc": pct1(tc), "ta": f1((1 - ta) * 100),
            "d": f3(row["d"]["ratio"]), "dp": f1(row["d_shift_pct"])}


def exp_arm_forward_l2():
    cells = [arm_cell(c) for c in forward_cells("L2")]
    ac, al = [x["as_compiled"]["ratio"] for x in cells], [x["aligned"]["ratio"] for x in cells]
    both = [x[col] for x in cells for col in ARM_COLUMNS]
    return {"alo": f3(min(ac)), "ahi": f3(max(ac)), "blo": f3(min(al)), "bhi": f3(max(al)),
            "w": f1(max(rel_hw(s) for s in both)), "s": exp_arm_limits_spread()["s"]}


def exp_arm_aa_control():
    cells = {det["aa"]["cell"] for _, _, det in arm_jobs()}
    assert cells == {"k02_add_fwd.L1"}, f"the A/A control timed {cells}"
    aa = arm_cpu()["aa"]
    return {"r": f4(aa["ratio"]), "hw": f3(aa["half_width_pct"])}


def exp_arm_layout():
    la = arm_cpu()["layout_aa"]
    lo, hi = min(la, key=lambda k: la[k]["half_width_pct"]), max(la, key=lambda k: la[k]["half_width_pct"])
    assert lo.endswith(".L1"), f"the quietest layout A/A cell is {lo}"
    moves = {k: abs(v["ratio"] - 1) * 100 for k, v in la.items() if k.endswith(".L1")}
    top = max(moves, key=moves.get)
    assert top == "k08_matmul.L1", f"the largest layout effect at L1 is {top}"
    other = max(v for k, v in moves.items() if k != top)
    kernel, size = hi.split(".")
    return {"lo": f3(la[lo]["half_width_pct"]), "hi": f1(la[hi]["half_width_pct"]), "c": f"{ARM_KERNELS[kernel]}, {size}",
            "m": f1(moves[top]), "r": f3(la[top]["ratio"]), "o": f2(math.ceil(other * 100) / 100)}


def exp_arm_negative():
    f = arm_build_facts()
    assert arm_forward_sum_identical() and f[("k01_sum_fwd", "fast")]["traps"] == 0, "the forward sum differs between the builds or has a trap"
    for k in FORWARD:
        assert f[(k, "none")]["neon"] == f[(k, "fast")]["neon"] > 0
    return {"a": str(f[("k01_sum_fwd", "none")]["neon"]), "b": str(f[("k02_add_fwd", "none")]["neon"]), "c": str(f[("k03_stencil", "none")]["neon"])}


def exp_arm_positive():
    pos = arm_cpu()["positive"]
    order = ("k01_sum_fwd", "k02_add_fwd", "k03_stencil", "k04_rev", "k05_stride2", "k08_matmul")
    v = [pos[k + ".L1"]["ratio"] for k in order]
    return {**{key: f2(x) for key, x in zip("abcdef", v)}, "lo": f1(min(v)), "hi": f1(max(v))}


def exp_arm_placement():
    c = arm_cpu()
    ids = sorted(p["cell_id"] for p in c["verdict"]["placement_sensitive"])
    assert ids == ["k02_add_fwd.L1", "k03_stencil.L1", "k08_matmul.L1", "k08_matmul.L2"], ids
    d = {cid: arm_cell(cid)["placement"]["d"] for cid in ids}
    assert d["k02_add_fwd.L1"]["ci95"][1] < 1, "the add's placement interval no longer excludes 1"
    return {"n": word(len(ids)), "a": f3(d["k02_add_fwd.L1"]["ratio"]), "b": f3(d["k03_stencil.L1"]["ratio"]),
            "c": f3(d["k08_matmul.L1"]["ratio"]), "d": f3(d["k08_matmul.L2"]["ratio"]),
            "e": f1((1 - d["k02_add_fwd.L1"]["ratio"]) * 100)}


def exp_arm_verdict_form():
    c = arm_cpu()
    assert c["verdict"]["form"] == "inconclusive" and "a mixed picture" in c["verdict"]["line"]
    assert all(r["form"] == "inconclusive" for r in c["per_run"]), "a run on its own is no longer INCONCLUSIVE"
    return {"three": word(len(c["per_run"]))}


def exp_arm_lost_floor():
    lost = [arm_cell(c)[col]["ci95"][0] for c in ("k04_rev.L1", "k04_rev.L2", "k05_stride2.L1", "k05_stride2.L2") for col in ARM_COLUMNS]
    assert {x["kernel"] for x in arm_cpu()["cells"] if x["class"] == "lost"} == {"k04_rev", "k05_stride2"}
    return {"lo": f2(math.floor(min(lost) * 100) / 100), "min": f1(J("site/data/index.json")["criteria"]["lost_ci_lo_min_ratio"])}


def exp_arm_judged():
    c = arm_cpu()
    kept = [x["cell_id"] for x in c["cells"] if x["class"] == "kept"]
    ps = {p["cell_id"] for p in c["verdict"]["placement_sensitive"]}
    judged = sorted(set(kept) - ps)
    assert judged == ["k01_sum_fwd.L1", "k01_sum_fwd.L2", "k02_add_fwd.L2", "k03_stencil.L2"], judged
    return {"four": word(len(judged)), "eight": word(len(kept)), "four2": word(len(ps))}


def exp_arm_add_l2():
    x = arm_cell("k02_add_fwd.L2")["aligned"]
    lim = arm_forward_limit()
    runs = arm_cpu()["per_run"]
    for r in runs:
        assert "k01_sum_fwd.L2" in r["line"] and "k02_add_fwd.L2" in r["line"] and "missed by" in r["line"], f"run {r['run_id']}: {r['line']}"
    return {"r": f3(x["ratio"]), "lo": f3(x["ci95"][0]), "hi": f3(x["ci95"][1]), "over": f4(x["ci95"][1] - lim), "lim": f2(lim),
            "sd": f1(x["between_job_sd_pct"])}


def exp_arm_matmul_counted():
    lim = arm_forward_limit()
    l1, l2 = arm_cell("k08_matmul.L1")["aligned"], arm_cell("k08_matmul.L2")["aligned"]
    assert l1["ci95"][1] > lim >= l2["ci95"][1], "counted, the matrix-multiply cells no longer split around the forward limit"
    return {"m1": f2(l1["ratio"]), "m2": f3(l2["ratio"]), "m3": f3(l2["ci95"][1])}


def arm_reproduction():
    r = arm_cpu()["reproduction"]
    stride = [m for m in r["misses"] if m["cell_id"] == "k05_stride2.L2"]
    others = [m for m in r["misses"] if m["cell_id"] != "k05_stride2.L2"]
    assert len(stride) + len(others) == r["outside"]
    return r, stride, others


def exp_arm_run_to_run():
    r, stride, others = arm_reproduction()
    c = arm_cpu()
    n = len(c["runs"])
    assert r["checked"] == len(c["cells"]) * len(ARM_COLUMNS) * n * (n - 1)
    assert all(m["gap_pct"] < 0.01 for m in others), "a miss outside stride-2 at L2 has a gap of 0.01% or more"
    points = [f2(run["cells"]["k05_stride2.L2"]["as_compiled"][0]) for run in c["per_run"]]
    return {"chk": str(r["checked"]), "cells": str(len(c["cells"])), "cols": str(len(ARM_COLUMNS)), "pairs": str(n * (n - 1)),
            "out": str(r["outside"]), "gap": f2(max(m["gap_pct"] for m in r["misses"])), "eight": word(len(stride)), "out2": str(r["outside"]),
            "g1": f2(min(m["gap_pct"] for m in stride)), "g2": f2(max(m["gap_pct"] for m in stride)),
            "p1": points[0], "p2": points[1], "p3": points[2], "five": word(len(others)), "u": "0.01"}


def exp_arm_held():
    f = arm_build_facts()
    return {"a": str(f[("k01_sum_fwd", "none")]["neon"]), "a2": str(f[("k01_sum_fwd", "fast")]["neon"]),
            "b": str(f[("k02_add_fwd", "none")]["neon"]), "b2": str(f[("k02_add_fwd", "fast")]["neon"]),
            "c": str(f[("k03_stencil", "none")]["neon"]), "c2": str(f[("k03_stencil", "fast")]["neon"])}


def exp_arm_held_jobs():
    return {"ret": str(arm_counts()["jobs"]), "disp": str(arm_counts()["runs"] * jobs_per_run())}


def exp_siblings_setup():
    return {"c": timed_clang(), "l": timed_clang().split(".")[0]}


def exp_siblings_arm():
    return {"model": arm_cpu()["cpu_model"], "c": arm_toolchain()["clang"].split(".")[0]}


def exp_cesweep_arm():
    return {"c": timed_clang().split(".")[0], "t": arm_toolchain()["clang"], "model": arm_cpu()["cpu_model"], "v": exp_arm_cesweep()["v"]}


def exp_arm_limits_spread():
    """The largest spread between jobs in a forward cell at L2, either column; the sentences say it is the add's."""
    top = max(((arm_cell(c), col) for c in forward_cells("L2") for col in ARM_COLUMNS), key=lambda t: t[0][t[1]]["between_job_sd_pct"])
    assert top[0]["kernel"] == "k02_add_fwd", f"the largest spread between jobs in a forward cell at L2 is the {top[0]['cell_id']}'s"
    return {"s": f1(top[0][top[1]]["between_job_sd_pct"])}


def exp_arm_limits_window():
    return {"n": str(arm_counts()["jobs"]), "three": word(arm_counts()["runs"]), "m": str(arm_start_window()["within"])}


def exp_arm_limits_compiler():
    t = arm_toolchain()
    return {"c": t["clang"], "l": t["lib_major"]}


def exp_arm_limits_core():
    """One core type: one pooled CPU model, one runner image in all the jobs, and a core name the sentence spells the same."""
    pool = arm_pool()
    assert len(pool["cpus"]) == 1, "the Arm pool holds more than one CPU model"
    images = {json.dumps(res["run"]["runner"], sort_keys=True) for _, res, _ in arm_jobs()}
    assert len(images) == 1, "the Arm jobs ran on more than one machine image"
    assert "Neoverse-N2" in arm_cpu()["cpu_model"], arm_cpu()["cpu_model"]
    return {"core": "Neoverse-N2", "one": word(1), "one2": word(len(images))}


def exp_arm_limits_one_cell():
    """The INCONCLUSIVE form rests on one forward cell (the add at L2), as the verdict's own reason lists it."""
    verdict = arm_cpu()["verdict"]
    assert verdict["form"].upper() == "INCONCLUSIVE", verdict["form"]
    assert verdict["why"].count("missed by k02_add_fwd.L2;") == 1, verdict["why"]
    return {"one": word(1)}


def exp_arm_three_runs():
    return {"three": word(arm_counts()["runs"])}


def exp_arm_pooled_over():
    return {"n": str(arm_counts()["jobs"])}


def exp_arm_title():
    return {"k": word(len(ARM_KERNELS))}


def exp_arm_status_date():
    w = arm_start_window()
    return {"m": w["month"], "y": w["year"]}


def exp_arm_pool_entries():
    return {"one": word(len(arm_pool()["cpus"]))}


def interval_level():
    """The confidence level of the intervals, as the written rules give it (percentile bootstrap, <resamples>, ..., 95 %)."""
    m = re.search(r"percentile bootstrap, \d+ resamples[^\"]*?, (\d+) %", json.dumps(J("harness/criteria-v3.json")))
    assert m, "harness/criteria-v3.json no longer states the level of the intervals"
    assert all("ci95" in x["as_compiled"] for x in arm_cpu()["cells"]), "the pooled cells no longer carry ci95"
    return m.group(1)


def exp_arm_interval_level():
    return {"p": interval_level()}


def exp_arm_forward_rule_percent():
    limit = arm_cpu()["verdict"]["forward_limit_pct"]
    assert limit == int(limit)
    return {"p": str(int(limit))}


def placement_window_bytes():
    with open(os.path.join(REPO, "harness", "placement.py"), encoding="utf-8") as f:
        m = re.search(r"windows = \(end - 1\) // (\d+) - tgt // (\d+) \+ 1", f.read())
    assert m and m.group(1) == m.group(2), "harness/placement.py no longer counts fetch windows of one size"
    return m.group(1)


def exp_arm_window():
    w = placement_window_bytes()
    return {"w1": w, "w2": w, "w3": w, "w4": w}


# ---- the derived files the noise, placement, interval-method and seed sentences rest on ---------------------------

ARM_SITE = "site/data/arm64.json"
ARM_SEEDS = "arm64/seed-sensitivity.json"
# the pattern harness/asm.py normalize() used before it was changed to strip three-digit AArch64 branch targets (four or more hex
# digits); it is history that the file no longer holds, and the stored .diff files were written with it
ASM_NORMALIZE_BEFORE = 4


def pool_sha256():
    with open(os.path.join(REPO, ARM_POOLED), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def arm_site():
    """site/data/arm64.json, after checking that it was built from the Arm pool as it is now."""
    d = J(ARM_SITE)
    assert d["source"] == ARM_POOLED and d["source_sha256"] == pool_sha256(), f"{ARM_SITE} was built from another version of {ARM_POOLED}"
    return d


def arm_seeds():
    """arm64/seed-sensitivity.json, after checking that it was made from the Arm pool as it is now."""
    d = J(ARM_SEEDS)
    assert d["pool"]["path"] == ARM_POOLED and d["pool"]["sha256"] == pool_sha256(), f"{ARM_SEEDS} was made from another version of {ARM_POOLED}"
    return d


def arm_noise():
    n = arm_site()["noise"]
    aa = n["identical_binary_aa"]
    assert aa["L1"]["cell_id"] == "k02_add_fwd.L1" and aa["L2"]["cell_id"] == "k02_add_fwd.L2" and n["same_cell_l2"]["cell_id"] == "k02_add_fwd.L2"
    assert abs(aa["L1"]["pooled"]["half_width_pct"] - arm_cpu()["aa"]["half_width_pct"]) < 1e-12, "the L1 A/A of the noise block is not the pool's"
    return n


def arm_lvp_row(cid):
    rows = [r for r in arm_site()["layout_vs_placement"]["rows"] if r["cell_id"] == cid]
    assert len(rows) == 1, f"{ARM_SITE} layout_vs_placement has {len(rows)} rows for {cid}"
    return rows[0]


def pool_py_constants():
    """(SEED_PREFIX, RESAMPLES) as harness/pool.py defines them."""
    with open(os.path.join(REPO, "harness", "pool.py"), encoding="utf-8") as f:
        src = f.read()
    seed, res = re.search(r'^SEED_PREFIX = "(\d+)"', src, re.M), re.search(r"^RESAMPLES = (\d+)", src, re.M)
    assert seed and res, "harness/pool.py no longer defines SEED_PREFIX and RESAMPLES in the form this test reads"
    return seed.group(1), res.group(1)


def rule_aa_ceiling():
    """The A/A half-width above which the written rules end at INCONCLUSIVE (harness/criteria-v3.json)."""
    with open(os.path.join(REPO, "harness", "criteria-v3.json"), encoding="utf-8") as f:
        found = set(re.findall(r'"aa_half_width_max_pct": ([\d.]+)', f.read()))
    assert len(found) == 1, f"harness/criteria-v3.json gives the A/A ceiling as {sorted(found)}"
    return float(found.pop())


@lru_cache(maxsize=None)
def x86_7763_sizes():
    """(L1 bytes, L2 bytes, matrix-multiply d at L1, d at L2) of the EPYC 7763 jobs of results/s7-run-*; every job must agree."""
    seen = set()
    for p in sorted(glob.glob(os.path.join(REPO, "results", "s7-run-*", "results-amd-epyc-7763-*", "details.json"))):
        with open(p, encoding="utf-8") as f:
            det = json.load(f)
        t, c = det["size_targets_bytes"], det["cache_bytes"]
        assert 2 * t["L1"] == c["l1d"] and 2 * t["L2"] == c["l2"], f"{p}: the working sets are no longer half of the per-core caches"
        seen.add((t["L1"], t["L2"], det["cells"]["k08_matmul.L1"]["n"], det["cells"]["k08_matmul.L2"]["n"]))
    assert len(seen) == 1, f"the EPYC 7763 jobs of results/s7-run-* differ in working-set or matrix sizes: {sorted(seen)}"
    return seen.pop()


@lru_cache(maxsize=None)
def arm_matmul_windows():
    """{build: (offset of the innermost NEON loop in its 64-byte window, windows it spans)} for NONE and NONE aligned; every job must agree."""
    out = None
    for rel, _, det in arm_jobs():
        got = {}
        for b in ("none", "none_a64"):
            loops = [l for l in det["kernels"]["k08_matmul"][b]["loops"] if l["simd"] and l["innermost"]]
            assert len(loops) == 1, f"{rel}: {len(loops)} innermost NEON loops in the {b} matrix multiply"
            got[b] = (loops[0]["start_mod64"], loops[0]["windows64"])
        if out is None:
            out = got
        else:
            assert out == got, f"{rel}: the matrix-multiply loop placement differs from the first job's"
    return out


def asm_normalize_digits():
    """The number of hex digits from which harness/asm.py normalize() strips a branch target."""
    with open(os.path.join(REPO, "harness", "asm.py"), encoding="utf-8") as f:
        m = re.search(r'ln = re\.sub\(r"\\b\[0-9a-f\]\{(\d+),\} <", "<", ln\)', f.read())
    assert m, "harness/asm.py normalize() no longer strips branch targets in the form this test reads"
    return int(m.group(1))


def none_or_word(n):
    return "none" if n == 0 else word(n)


def measure_workflow():
    """.github/workflows/measure.yml parsed with PyYAML. A missing PyYAML fails the test (CI installs it): skipping would leave the
    runner wiring unchecked without anyone seeing it."""
    try:
        import yaml
    except ImportError as e:
        raise AssertionError("PyYAML is needed to read .github/workflows/measure.yml (pip install pyyaml)") from e
    with open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def measure_runner_labels():
    """(x86-64 label, Arm label, Arm CPU name) from the `runner` input of measure.yml, read as YAML: a choice of two labels whose
    default is the x86-64 one, the job's runs-on taking that input, and a description that names the Arm core."""
    wf = measure_workflow()
    on = wf.get("on", wf.get(True))  # PyYAML reads the key `on` as the boolean True
    assert isinstance(on, dict) and "workflow_dispatch" in on, "measure.yml no longer starts on workflow_dispatch"
    runner = (on["workflow_dispatch"].get("inputs") or {}).get("runner")
    assert isinstance(runner, dict), "measure.yml has no `runner` input"
    options = runner.get("options")
    assert runner.get("type") == "choice" and isinstance(options, list) and len(options) == 2, f"the runner input is not a choice of two labels: {runner}"
    x86, arm = options
    assert runner.get("default") == x86, f"the runner input defaults to {runner.get('default')}, the x86-64 label is {x86}"
    assert arm == x86 + "-arm", f"the Arm label {arm} is not the x86-64 label {x86} plus -arm"
    runs_on = wf["jobs"]["measure"]["runs-on"]
    assert runs_on == "${{ inputs.runner }}", f"the measure job runs on {runs_on!r}, not on the runner input"
    m = re.match(r"GitHub-hosted runner label: (ubuntu-[\d.]+) \(x86-64, the default\) or (ubuntu-[\d.]+-arm) \(AArch64, ([\w-]+)\)", runner.get("description", ""))
    assert m, "the runner input no longer describes itself as an x86-64 label and an AArch64 one"
    assert (m.group(1), m.group(2)) == (x86, arm), f"the description names {m.group(1)} and {m.group(2)}, the options are {x86} and {arm}"
    assert m.group(3) == arm_cpu()["cpu_model"], f"measure.yml names {m.group(3)}, the Arm jobs ran on {arm_cpu()['cpu_model']}"
    return x86, arm, m.group(3)


def exp_arm_labels():
    arm = measure_runner_labels()[1]
    return {"a": arm, "b": arm, "c": arm}


def exp_readme_runner_label():
    return {"label": measure_runner_labels()[1]}


def exp_details_runners():
    x, a, model = measure_runner_labels()
    return {"x": x, "a": a, "model": model}


def exp_arm_trap_form():
    forms = {x for f in arm_build_facts().values() for x in f["brk_forms"]}
    assert forms == {"#0x1"}, f"the Arm listings contain brk forms {sorted(forms)}"
    return {"t": "brk #0x1"}


def exp_arm_stable_runs():
    return exp_arm_verdict_form()


def exp_arm_cesweep_only():
    exp_arm_cesweep()
    return {}


def arm_plan_smoke_kernels():
    m = re.search(r"after one (\w+)-kernel smoke run", arm_plan_text())
    assert m, "arm64/PLAN.md no longer says how many kernels the smoke run timed"
    return m.group(1)


def exp_arm_smoke_kernels():
    return {"k": arm_plan_smoke_kernels()}


def exp_arm_timeline():
    t = arm_timeline()
    plan = arm_plan_text()
    m = re.search(r"Written \w+ \w+ \d+, ([\d:]+) EDT", plan)
    assert m, "arm64/PLAN.md no longer gives the time it was written"
    assert plan.count(f"run {t['smoke']}") == 1, "arm64/PLAN.md no longer names the smoke run"
    assert len(t["dispatched"]) == 1, f"the runs were dispatched at {sorted(t['dispatched'])}"
    month, day = (int(x) for x in t["smoke_date"].split("-")[1:])
    return {"k": arm_plan_smoke_kernels(), "smoke": t["smoke"], "t0": t["smoke_at"], "day": f"{MONTHS[month - 1]} {day}",
            "three": word(len(arm_cpu()["runs"])), "t1": next(iter(t["dispatched"])), "t2": t["plan_utc"], "t2e": t["plan_local"],
            "t3": t["first_done"], "h": m.group(1), "c": t["plan_local"]}


def arm_plan_smoke_numbers():
    """(reverse ratio, forward-add ratio, A/A half-width) as arm64/PLAN.md quotes them from the smoke run."""
    m = re.search(r"k04_rev \(reverse\) ([\d.]+)x and k02_add_fwd ([\d.]+)x, with an A/A half-width of ([\d.]+)%", arm_plan_text())
    assert m, "arm64/PLAN.md no longer quotes the smoke run's reverse, forward-add and A/A figures in this form"
    return m.groups()


def exp_arm_smoke_quote():
    t = J(ARM_TIMELINE)["smoke"]
    m = re.fullmatch(r"(\w+) kernels, (L\d)", t["timing_step"])
    assert m, f"the timeline's name of the smoke run's timing step is {t['timing_step']!r}"
    assert m.group(1).lower() == arm_plan_smoke_kernels(), "the smoke run's timing step and arm64/PLAN.md disagree on the number of kernels"
    assert f"run {t['run']}" in arm_plan_text(), "arm64/PLAN.md does not name the smoke run of the timeline"
    r, a, aa = arm_plan_smoke_numbers()
    return {"run": str(t["run"]), "k": m.group(1).lower(), "sz": m.group(2), "r": r, "a": a, "aa": aa}


def exp_arm_smoke_add_known():
    return {"a": arm_plan_smoke_numbers()[1]}


def exp_arm_timeline_source():
    t = J(ARM_TIMELINE)
    m = re.search(r"\) on (\d{4})-(\d\d)-(\d\d)", t["what"])
    assert m, "tests/data/s8_arm_timeline.json no longer says on which day the Actions API was read"
    assert "not published" in t["plan_commit"]["source"], "the timeline no longer says that the plan's commit is read from a repository that is not published"
    return {"d": f"{MONTHS[int(m.group(2)) - 1]} {int(m.group(3))}", "np": "not published"}


def exp_arm_short_margin():
    s, dc = arm_deciding()
    return {"over": f4(dc["stored_hi"] - dc["limit"]), "n": str(dc["alt_draws"]), "lim": f2(dc["limit"]),
            "k": str(dc["alt_at_or_above_limit"]), "m": str(s["derived"]["forms"]["map"])}


def arm_deciding():
    """The seed file and its deciding cell (the forward add at L2, aligned), checked against the pool."""
    s = arm_seeds()
    dc = s["deciding_cell"]
    stored = arm_cell("k02_add_fwd.L2")["aligned"]["ci95"][1]
    assert dc["cell_id"] == "k02_add_fwd.L2" and dc["column"] == "aligned", f"the seed file's deciding cell is {dc['cell_id']} {dc['column']}"
    assert abs(dc["stored_hi"] - stored) < 1e-12 and abs(dc["limit"] - arm_forward_limit()) < 1e-12, "the seed file's deciding cell is not the pool's"
    assert abs(dc["margin_over_limit"] - (stored - dc["limit"])) < 1e-12
    assert dc["alt_draws"] == s["alt_seeds"]["count"] == s["derived"]["seeds"], "the seed counts of the seed file disagree"
    assert s["derived"]["forms"]["inconclusive"] == dc["alt_at_or_above_limit"] == len(dc["seeds_at_or_above_limit"]), \
        "the seeds that end at or above the limit and the seeds with an INCONCLUSIVE form are no longer the same number"
    assert stored > dc["limit"] and dc["margin_over_limit"] < dc["alt_hi"]["max"] - dc["alt_hi"]["min"], "the margin is no longer smaller than the spread over the other seeds"
    return s, dc


def exp_arm_seed_origin():
    s = arm_seeds()
    prefix, resamples = pool_py_constants()
    ss = s["stored_seed"]
    assert ss["prefix"] == prefix and str(ss["resamples"]) == resamples and str(s["alt_seeds"]["resamples"]) == resamples, \
        "the seed file and harness/pool.py disagree on the prefix or the number of resamples"
    fixed = datetime.datetime.fromisoformat(ss["fixed_on"])
    first = min(res["run"]["started_at"] for _, res, _ in arm_jobs())
    days = (datetime.datetime.strptime(first[:10], "%Y-%m-%d").date() - fixed.date()).days
    return {"res": resamples, "pre": prefix, "day": f"{MONTHS[fixed.month - 1]} {fixed.day}", "iso": ss["fixed_on"], "days": word(days)}


def exp_arm_seed_distribution():
    s, dc = arm_deciding()
    alt = dc["alt_hi"]
    assert dc["stored_rank_from_top"] == 1 and dc["stored_hi"] > alt["max"], "the stored upper end is no longer above those of all the other seeds"
    conv = dc["converged"]
    assert conv["above_limit"] is False and conv["hi"] < dc["limit"], "with many resamples the end is no longer below the limit"
    assert str(s["alt_seeds"]["resamples"]) == pool_py_constants()[1], "the other seeds use another number of resamples than harness/pool.py"
    return {"res2": str(s["alt_seeds"]["resamples"]), "n": str(dc["alt_draws"]), "med": f4(alt["median"]), "p05": f4(alt["p05"]), "p95": f4(alt["p95"]), "mn": f4(alt["min"]), "mx": f4(alt["max"]),
            "k": str(dc["alt_at_or_above_limit"]), "n2": str(dc["alt_draws"]), "lim": f2(dc["limit"]), "st": f4(dc["stored_hi"]), "n3": str(dc["alt_draws"]),
            "conv": thousands(conv["resamples"]), "ch": f4(conv["hi"])}


def exp_arm_seed_whole():
    s, dc = arm_deciding()
    full, der = s["full"], s["derived"]
    placement = sorted(p["cell_id"] for p in arm_cpu()["verdict"]["placement_sensitive"])
    for part in (full, der):
        assert not part["lost_missed_any"], "a seed lets a lost-loop cell miss its rule"
        assert len(part["placement_sets"]) == 1 and sorted(part["placement_sets"][0]["cells"]) == placement, "the placement-sensitive set changes with the seed"
    assert der["forward_missed_counts"] == {"k02_add_fwd.L2": der["forms"]["inconclusive"]}, f"the 8 INCONCLUSIVE seeds miss on {der['forward_missed_counts']}"
    assert der["equals_analyse_cpu_on_first"] == full["count"], "the whole-analysis seeds are no longer the first of the derived ones"
    assert der["positive_seen_in_all"], "a seed loses the positive control"
    aa = next(r for r in s["rows"] if r["kind"] == "aa")["alt"]
    assert aa["draws"] == der["seeds"]
    return {"n": str(full["count"]), "map": str(full["forms"]["map"]), "inc": str(full["forms"]["inconclusive"]), "all": str(der["seeds"]),
            "m2": str(der["forms"]["map"]), "i2": str(der["forms"]["inconclusive"]), "i3": str(der["forms"]["inconclusive"]), "four": word(len(placement)),
            "alo": f4(aa["half_width_pct"]["min"]), "ahi": f4(aa["half_width_pct"]["max"])}


def exp_arm_interval_methods():
    m = arm_site()["interval_methods"]
    by = {x["id"]: x for x in m["methods"]}
    assert m["inconclusive_methods"] == ["a"] and sorted(m["map_methods"]) == sorted(set(by) - {"a"}), \
        f"the methods that give INCONCLUSIVE: {m['inconclusive_methods']}, MAP: {m['map_methods']}"
    assert m["self_test"]["exact"] == m["self_test"]["numbers_checked"] and m["self_test"]["forms_equal"], "the robustness self-test no longer reproduces the pool exactly"
    for i, x in by.items():
        assert x["deciding_cell"]["cell_id"] == "k02_add_fwd.L2" and x["deciding_cell"]["column"] == "aligned", f"method {i} reports another deciding cell"
    hi = lambda i: by[i]["deciding_cell"]["ci95"][1]
    assert abs(hi("a") - arm_cell("k02_add_fwd.L2")["aligned"]["ci95"][1]) < 1e-12, "method a is no longer the pool's own interval"
    assert f3(hi("d")) == f3(hi("d0")), "the two lag-1 corrections no longer give the same end"
    block = [hi(i) for i in ("b", "b2", "b5")]
    return {"k": word(len(by)), "ex": str(m["self_test"]["exact"]), "b1": f3(min(block)), "b2": f3(max(block)), "c1": f3(hi("c")), "c2": f3(hi("ct")),
            "d": f3(hi("d")), "a": f3(hi("a"))}


def exp_arm_seed_l2aa():
    n = arm_noise()
    p = n["identical_binary_aa"]["L2"]["pooled"]
    assert p["half_width_pct"] > rule_aa_ceiling(), "the L2 A/A is no longer above the rule's ceiling"
    return {"aa": f2(p["half_width_pct"]), "c": f0(rule_aa_ceiling())}


def pool_check_constants(src=None):
    """harness/pool_check.py's sample and tolerance, read from the text of the file (not imported; `src` stands in for the file in the tamper tests)."""
    if src is None:
        with open(os.path.join(REPO, "harness", "pool_check.py"), encoding="utf-8") as f:
            src = f.read()
    cells = re.search(r"^SAMPLE_CELLS = \((.*?)\)", src, re.M | re.S)
    placement = re.search(r"^PLACEMENT_CELLS = \((.*?)\)", src, re.M | re.S)
    nums = {n: re.search(rf"^{n} = ([\d.]+)", src, re.M) for n in ("B", "BOUND_TOL_WIDTH", "BOUND_TOL_RATIO")}
    assert cells and placement and all(nums.values()), "harness/pool_check.py no longer defines its constants in the form this test reads"
    return {"cells": re.findall(r'"([^"]+)"', cells.group(1)), "placement": re.findall(r'"([^"]+)"', placement.group(1)),
            "b": int(nums["B"].group(1)), "width": float(nums["BOUND_TOL_WIDTH"].group(1)), "ratio": float(nums["BOUND_TOL_RATIO"].group(1))}


def pool_check_narrow(doc=None, constants=None):
    """The statistics harness/pool_check.py samples in a pooled file (the CPU models with at least the minimum number of jobs, counted the way its
    check() lists them: the A/A, the layout A/A of k02_add_fwd.L1, both columns of each sampled cell, the placement statistic of the placement cells),
    and which of them have a tolerance at least as wide as the stored interval: (statistics sampled, [(CPU model, interval width) of the narrow ones])."""
    k = constants or pool_check_constants()
    doc = J(POOLED) if doc is None else doc
    minimum = J(doc["criteria_file"])["v3"]["pooling"]["minimum_jobs"]
    sampled, narrow = 0, []
    for blk in doc["cpus"]:
        if blk["jobs"] < minimum:
            continue
        stats = [blk["aa"]]
        if "k02_add_fwd.L1" in blk["layout_aa"]:
            stats.append(blk["layout_aa"]["k02_add_fwd.L1"])
        by_id = {c["cell_id"]: c for c in blk["cells"]}
        for cid in k["cells"]:
            if cid in by_id:
                stats += [by_id[cid]["as_compiled"], by_id[cid]["aligned"]]
                if cid in k["placement"] and "placement" in by_id[cid]:
                    stats.append(by_id[cid]["placement"]["d"])
        for st in stats:
            sampled += 1
            width = st["ci95"][1] - st["ci95"][0]
            if k["width"] * width + k["ratio"] * st["ratio"] >= width:
                narrow.append((blk["cpu_model"], width))
    return sampled, narrow


# The three cells the written conclusions rest on, which harness/pool_check.py samples: the stencil at L2 (decides the Xeon 6973P-C's word), the
# forward add at L2 (decides the Arm core's word) and stride-2 at L1 (the lowest lost-loop cost over the models with a verdict).
POOL_CHECK_LEAD_CELLS = ("k03_stencil.L2", "k02_add_fwd.L2", "k05_stride2.L1")


def check_pool_check_lead_cells(constants=None):
    """The sample holds the three cells, and each one is what the sentence says it is, tied to the pooled files."""
    k = constants or pool_check_constants()
    for cid in POOL_CHECK_LEAD_CELLS:
        assert cid in k["cells"], f"harness/pool_check.py no longer samples {cid}, one of the three cells the written conclusions rest on"
    x = cpu_like("6973P-C")
    ps = {p["cell_id"] for p in x["verdict"]["placement_sensitive"]}
    counted = [c for c in x["cells"] if c["kernel"] in FORWARD and c["cell_id"] not in ps]
    top = max(counted, key=lambda c: c["aligned"]["ci95"][1])["cell_id"]
    assert top == "k03_stencil.L2", f"the counted forward cell of the Xeon 6973P-C with the highest aligned upper end is {top}, not the stencil at L2"
    dc = arm_deciding()[1]
    assert (dc["cell_id"], dc["column"]) == ("k02_add_fwd.L2", "aligned"), "the cell that decides the Arm word is no longer the forward add at L2"
    low = min((c[col]["ratio"], c["cell_id"]) for cpu in enough_cpus() for c in cpu["cells"] if c["class"] == "lost" for col in ("as_compiled", "aligned"))
    assert low[1] == "k05_stride2.L1", f"the lowest lost-loop cell over the models with a verdict is {low[1]}, not stride-2 at L1"


def exp_arm_seed_pool_check():
    k = pool_check_constants()
    assert "k02_add_fwd.L2" in k["cells"], "harness/pool_check.py no longer samples the cell that decides the Arm verdict"
    x = arm_cell("k02_add_fwd.L2")["aligned"]
    tol = k["width"] * (x["ci95"][1] - x["ci95"][0]) + k["ratio"] * x["ratio"]
    margin = x["ci95"][1] - arm_forward_limit()
    assert tol > margin > 0, "the check's tolerance is no longer larger than the margin"
    floor = 1 + J("harness/criteria-v3.json")["verdict"]["forward_ci_hi_floor_pct"] / 100
    assert abs(floor - arm_forward_limit()) < 1e-12, "the limit pool_check.py prints the margin against is not the Arm core's limit"
    return {"lim": f2(floor), "tol": f3(tol), "over": f4(margin)}


def exp_pool_check_sample():
    """What harness/pool_check.py samples and how closely its interval has to agree: read from its constants and from the minimum-jobs rule;
    the count of narrow intervals is recomputed here from the stored pooled file with the same tolerance formula."""
    k = pool_check_constants()
    assert len(set(k["cells"])) == len(k["cells"]), "harness/pool_check.py lists a sampled cell twice"
    check_pool_check_lead_cells(k)
    sampled, narrow = pool_check_narrow(constants=k)
    models = {m for m, _ in narrow}
    assert len(models) == 1 and "EPYC" in next(iter(models)), f"the narrow statistics are on {sorted(models)}: the sentence says all of them are on one EPYC model"
    assert 0 < len(narrow) * 10 <= sampled, f"{len(narrow)} narrow statistics of {sampled} are no longer 'a few'"
    assert max(w for _, w in narrow) < 0.005, "a narrow interval is no longer 'very narrow' (under half a percent)"
    jobs = len(J(POOLED)["inputs"])
    assert jobs == sum(c["jobs"] for c in J(POOLED)["cpus"]), "the pooled file's inputs and its per-model job counts disagree"
    return {"mn": str(J("harness/criteria-v3.json")["v3"]["pooling"]["minimum_jobs"]), "cells": word(len(k["cells"])), "pl": word(len(k["placement"])),
            "b": f"{k['b']:,}", "w": f"{round(k['width'] * 100):d}", "r": f"{k['ratio'] * 100:g}",
            "nk": str(len(narrow)), "nm": str(sampled), "jobs": str(jobs), "cpu": next(iter(models)).split("EPYC ")[1].split()[0]}


def tampered_sentence_copies(row_label, rows, text, names=None):
    """Copies of `text` in which one typed value of the row's sentence is replaced (by the value with a 9 appended, which the anchor still reads), one
    value per copy: [(name, copy)]. All the row's captured values unless `names` lists some."""
    found = [r for r in rows if r[0] == row_label]
    assert len(found) == 1, f"{len(found)} rows are called {row_label!r}"
    m = re.search(found[0][3], text, re.S)
    assert m, f"the row {row_label!r} matches no sentence of the text it is tested on"
    out = []
    for name in names or m.re.groupindex:
        s, e = m.span(name)
        out.append((name, text[:s] + text[s:e] + "9" + text[e:]))
    return found[0], out


def failure_of(row, text, doc):
    """The message of the AssertionError check_row raises for `text`, or None when the row passes."""
    try:
        check_row(row, text, doc)
    except AssertionError as e:
        return str(e)
    return None


def test_the_pool_check_sentence_fails_on_each_changed_number():
    """Every number typed in the pool_check sentence of the details page is changed in turn: the row must name the value as wrong, and pass on the text as it is."""
    text = details_text()
    row, copies = tampered_sentence_copies("details: what pool_check.py recomputes and how closely", DETAILS_ROWS, text)
    assert failure_of(row, text, "readme-parts/DETAILS.md") is None
    assert {n for n, _ in copies} == {"mn", "cells", "pl", "b", "w", "r", "nk", "nm", "jobs", "cpu"}, "the sentence's typed values changed: add the new ones to the guard"
    for name, bad in copies:
        why = failure_of(row, bad, "readme-parts/DETAILS.md")
        assert why and "types" in why and f"'{name}'" in why, f"changing {name!r} was not caught: {why}"


def test_the_arm_pool_check_sentence_fails_on_each_changed_number():
    text = arm64_text()
    row, copies = tampered_sentence_copies("arm64: verdict, the independent check", ARM64_ROWS, text)
    assert failure_of(row, text, "arm64/README.md") is None
    assert {n for n, _ in copies} == {"lim", "tol", "over"}
    for name, bad in copies:
        why = failure_of(row, bad, "arm64/README.md")
        assert why and "types" in why and f"'{name}'" in why, f"changing {name!r} was not caught: {why}"


def test_a_pool_check_sample_without_a_lead_cell_is_caught():
    """The constants are read from a copy of pool_check.py's text with one of the three cells taken out: the guard must fail on each."""
    with open(os.path.join(REPO, "harness", "pool_check.py"), encoding="utf-8") as f:
        src = f.read()
    check_pool_check_lead_cells(pool_check_constants(src))
    for cid in POOL_CHECK_LEAD_CELLS:
        cut = pool_check_constants(src.replace(f'"{cid}", ', "", 1).replace(f', "{cid}"', "", 1))
        assert cid not in cut["cells"], f"the copy still samples {cid}"
        try:
            check_pool_check_lead_cells(cut)
        except AssertionError as e:
            assert cid in str(e), f"the failure for {cid} does not name it: {e}"
        else:
            raise AssertionError(f"a sample without {cid} was not caught")


def test_the_count_of_narrow_pool_check_intervals_follows_the_data():
    """The same counting run on a copy of the pooled file in which one interval is made as narrow as a hair: exactly one more narrow statistic, same total."""
    doc = json.loads(json.dumps(J(POOLED)))
    sampled, narrow = pool_check_narrow(doc)
    stored = pool_check_narrow()
    assert (sampled, len(narrow)) == (stored[0], len(stored[1])), "the copy does not count like the stored file"
    blk = next(c for c in doc["cpus"] if "7763" in c["cpu_model"])
    blk["aa"]["ci95"] = [blk["aa"]["ratio"] - 1e-7, blk["aa"]["ratio"] + 1e-7]
    sampled2, narrow2 = pool_check_narrow(doc)
    assert sampled2 == sampled and len(narrow2) == len(narrow) + 1, f"{len(narrow)} narrow, then {len(narrow2)} after one interval was made a hair wide"
    blk["aa"]["ci95"] = [blk["aa"]["ratio"] - 1.0, blk["aa"]["ratio"] + 1.0]
    assert len(pool_check_narrow(doc)[1]) == len(narrow), "an interval made wide still counts as narrow"
    doc["cpus"].append(dict(blk, jobs=J(doc["criteria_file"])["v3"]["pooling"]["minimum_jobs"] - 1))
    assert pool_check_narrow(doc)[0] == sampled, "a model with too few jobs was sampled"


def exp_arm_seed_summary():
    x = arm_cell("k02_add_fwd.L2")["aligned"]
    s, dc = arm_deciding()
    return {"hw": f1(rel_hw(x)), "over": f4(dc["stored_hi"] - dc["limit"])}


def exp_arm_l2_aa_control():
    n = arm_noise()
    p = n["identical_binary_aa"]["L2"]["pooled"]
    assert "aa_extra" not in json.dumps(arm_cpu()), "pooled.json now holds the L2 A/A"
    return {"r": f4(p["ratio"]), "hw": f2(p["half_width_pct"])}


def exp_arm_noise_l2_aa():
    n = arm_noise()
    aa = n["identical_binary_aa"]
    p, s = aa["L2"]["pooled"], n["same_cell_l2"]
    cell = arm_cell("k02_add_fwd.L2")
    assert abs(s["identical_binary_aa"]["half_width_pct"] - p["half_width_pct"]) < 1e-12
    assert abs(s["as_compiled"]["half_width_pct"] - cell["as_compiled"]["half_width_pct"]) < 1e-12 and abs(s["aligned"]["half_width_pct"] - cell["aligned"]["half_width_pct"]) < 1e-12, \
        "the half-widths of the add at L2 in the noise block are not the pool's"
    assert abs(s["layout_aa"]["half_width_pct"] - arm_cpu()["layout_aa"]["k02_add_fwd.L2"]["half_width_pct"]) < 1e-12, "the layout A/A of the add at L2 is not the pool's"
    lo, hi = aa["L2"]["job_ratio_range"]
    return {"r": f4(p["ratio"]), "lo": f3(p["ci95"][0]), "hi": f3(p["ci95"][1]), "hw": f2(p["half_width_pct"]), "sd": f2(p["between_job_sd_pct"]),
            "jlo": f3(lo), "jhi": f3(hi), "l1": f3(aa["L1"]["pooled"]["half_width_pct"]),
            "h1": f2(s["as_compiled"]["half_width_pct"]), "h2": f2(s["aligned"]["half_width_pct"]), "h3": f2(s["layout_aa"]["half_width_pct"])}


def exp_arm_noise_ceiling():
    n, ceiling = arm_noise(), rule_aa_ceiling()
    l1, l2 = n["identical_binary_aa"]["L1"], n["identical_binary_aa"]["L2"]
    assert n["rule_aa_half_width_max_pct"] == ceiling, "the noise block and the criteria file disagree on the A/A ceiling"
    assert l2["pooled"]["half_width_pct"] > ceiling >= l1["pooled"]["half_width_pct"] and l2["above_rule_max"] and not l1["above_rule_max"]
    return {"ceil": f0(ceiling), "jobs": str(l2["jobs_above_rule_max"]), "of": str(l2["jobs"]), "l1": none_or_word(l1["jobs_above_rule_max"])}


def exp_arm_noise_slow():
    n = arm_noise()
    bs, aa = n["mixture"]["by_size"], n["identical_binary_aa"]
    a2, b2, a1, b1 = (aa[size]["mixture"][side] for size in ("L2", "L1") for side in ("a", "b"))
    assert f0(a2["p_slow_after_ok"] * 100) == f0(b2["p_slow_after_ok"] * 100), "the chance of a slow process after an ordinary one differs between the two sides"
    return {"th": f0(n["slow_share"] * 100), "n1": f1(bs["L1"]["none"]["share_slow"] * 100), "f1": f1(bs["L1"]["fast"]["share_slow"] * 100),
            "n2": f1(bs["L2"]["none"]["share_slow"] * 100), "f2": f1(bs["L2"]["fast"]["share_slow"] * 100),
            "mn": f0(bs["L2"]["none"]["cell_share_max"] * 100), "mf": f0(bs["L2"]["fast"]["cell_share_max"] * 100),
            "cva": f1(a2["cv_pct"]["median"]), "cvb": f1(b2["cv_pct"]["median"]), "c1a": f2(a1["cv_pct"]["median"]), "c1b": f2(b1["cv_pct"]["median"]),
            "s1": f0(a2["p_slow_after_slow"] * 100), "s2": f0(b2["p_slow_after_slow"] * 100), "o1": f0(a2["p_slow_after_ok"] * 100)}


def exp_arm_noise_medians():
    cells = {c["cell_id"]: c for c in arm_noise()["mixture"]["cells"]}
    r, s, a = cells["k04_rev.L2"], cells["k05_stride2.L2"], cells["k02_add_fwd.L2"]
    for c in (r, s):
        assert c["fast"]["share_slow"] == 0 and c["none"]["share_slow"] > 0, f"{c['cell_id']}: the slow processes are no longer only on the NONE side"
    p10 = lambda c: c["floor_ratio"]["as_compiled"]["p10_ratio"]
    return {"r": f0(r["none"]["share_slow"] * 100), "s": f0(s["none"]["share_slow"] * 100), "p1": f2(p10(r)), "p2": f2(p10(s)),
            "m1": f2(arm_ratio("k04_rev.L2")), "m2": f2(arm_ratio("k05_stride2.L2")), "fa": f3(p10(a)), "fm": f3(arm_ratio("k02_add_fwd.L2")),
            "fw": f1(rel_hw(arm_cell("k02_add_fwd.L2")["as_compiled"]))}


def exp_arm_layout_vs_d():
    lvp = arm_site()["layout_vs_placement"]
    st, s2, ga, mm = (arm_lvp_row(c) for c in ("k03_stencil.L1", "k05_stride2.L1", "k06_gather.L1", "k08_matmul.L1"))
    assert lvp["d_excludes_1_layout_aa_includes_1"] == ["k03_stencil.L1", "k06_gather.L2"], f"cells where D excludes 1 and the layout A/A does not: {lvp['d_excludes_1_layout_aa_includes_1']}"
    top = lvp["largest_d_shift_l1"]
    assert top["cell_id"] == "k06_gather.L1" and abs(top["d_shift_pct"] - ga["d_shift_pct"]) < 1e-12, f"the largest D shift at L1 is {top['cell_id']}"
    for cid in ("k03_stencil.L1", "k08_matmul.L1"):  # the pool itself holds D and the layout A/A for these
        row = arm_lvp_row(cid)
        assert abs(row["d"]["ratio"] - arm_cell(cid)["placement"]["d"]["ratio"]) < 1e-12 and abs(row["layout_aa"]["ratio"] - arm_cpu()["layout_aa"][cid]["ratio"]) < 1e-12
    return {"ds": f3(st["d"]["ratio"]), "d2": f3(s2["d"]["ratio"]), "dg": f3(ga["d"]["ratio"]), "ls": f2(st["layout_aa_shift_pct"]),
            "l2": f2(s2["layout_aa_shift_pct"]), "lg": f2(ga["layout_aa_shift_pct"]), "lm": f2(mm["layout_aa_shift_pct"]), "dm": f2(mm["d_shift_pct"]),
            "mx": f1(top["d_shift_pct"])}


def exp_arm_matmul_windows():
    w = arm_matmul_windows()
    la = arm_cpu()["layout_aa"]["k08_matmul.L1"]
    assert la["ratio"] > 1, "the aligned NONE matrix multiply is no longer the slower one"
    return {"off": str(w["none"][0]), "w": placement_window_bytes(), "n1": str(w["none"][1]), "n2": str(w["none_a64"][1]),
            "pct": f1((la["ratio"] - 1) * 100), "r": f3(la["ratio"])}


def exp_arm_limits_placement():
    return {"st": f1(arm_lvp_row("k03_stencil.L1")["d_shift_pct"]), "ga": f1(arm_lvp_row("k06_gather.L1")["d_shift_pct"])}


def exp_arm_limits_floor():
    aa = arm_cpu()["aa"]["half_width_pct"]
    cells = [(x, col) for x in arm_cpu()["cells"] for col in ARM_COLUMNS]
    widest = {}
    for size in ("L1", "L2"):
        widest[size] = max((t for t in cells if t[0]["size_class"] == size), key=lambda t: rel_hw(t[0][t[1]]))
    assert widest["L1"][0]["kernel"] == "k03_stencil" and widest["L2"][0]["kernel"] == "k05_stride2", \
        f"the widest intervals are the {widest['L1'][0]['kernel']}'s at L1 and the {widest['L2'][0]['kernel']}'s at L2"
    return {"aa": f3(aa), "w1": f2(rel_hw(widest["L1"][0][widest["L1"][1]])), "w2": f2(rel_hw(widest["L2"][0][widest["L2"][1]]))}


def exp_arm_limits_aa_l2():
    return {"aa": f1(arm_noise()["identical_binary_aa"]["L2"]["pooled"]["half_width_pct"])}


def exp_arm_limits_identical_spread():
    return {"sd": f3(arm_cpu()["aa"]["between_job_sd_pct"])}


def exp_arm_normalize():
    new = asm_normalize_digits()
    d = next(k for k in arm_site()["stored_diffs"]["kernels"] if k["kernel"] == "k02_add_fwd")["L1"]
    assert d["added"] != d["added_after_fix"] or d["removed"] != d["removed_after_fix"], "the stored diff of the add at L1 is no longer changed by the fix"
    return {"new": word(new), "old": word(ASM_NORMALIZE_BEFORE), "dig": word(new), "a": str(d["added"]), "r": str(d["removed"]),
            "a2": str(d["added_after_fix"]), "r2": str(d["removed_after_fix"])}


def exp_arm_setup_x86_sizes():
    l1, l2, d1, d2 = x86_7763_sizes()
    return {"l1": str(l1 // 1024), "l2": str(l2 // 1024), "d1": str(d1), "d2": str(d2)}


def exp_arm_setup_x86_d():
    _, _, d1, d2 = x86_7763_sizes()
    return {"d1": str(d1), "d2": str(d2)}


def exp_arm_seeds_reproduce():
    return {"n": str(arm_seeds()["alt_seeds"]["count"])}


def exp_arm_readme_bullet():
    s, r = exp_arm_short_reverse(), exp_arm_short_matmul()
    f = exp_arm_short_forward()
    v = exp_arm_short_verdict()
    n = exp_arm_counts_digits()
    m = exp_arm_short_margin()
    exp_arm_placement()  # the add and the stencil at L1 are among the placement-sensitive cells, as the bullet says
    return {"model": n["model"], "jobs": n["jobs"], "runs": n["runs"], "r": s["r1"], "s": s["s1"], "m1": r["m1"], "m2": r["m2"],
            "lo": f["lo"], "hi": f["hi"], "aa": f["aa"], "end": v["hi"], "lim": v["lim"],
            "over": m["over"], "k": m["k"], "n": m["n"], "lim2": m["lim"], "l2aa": f1(arm_noise()["identical_binary_aa"]["L2"]["pooled"]["half_width_pct"])}


def exp_arm_readme_trust():
    n = exp_arm_counts_digits()
    return {"model": n["model"], "jobs": n["jobs"], "runs": n["runs"], "c": arm_toolchain()["clang"].split(".")[0]}


def exp_arm_readme_folder():
    return {"jobs": str(arm_counts()["jobs"])}


def exp_x86_clang_major():
    return {"c": timed_clang().split(".")[0]}


def exp_details_arm_intro():
    return {"n": str(arm_counts()["jobs"]), "m": str(pooled_jobs())}


def exp_details_arm_runs():
    n, t = exp_arm_counts_digits(), arm_toolchain()
    return {"model": n["model"], "three": word(arm_counts()["runs"]), "jobs": n["jobs"], "clang": t["clang"], "lib": t["lib_major"]}


def exp_details_arm_reverse():
    s = exp_arm_short_reverse()
    return {"r1": s["r1"], "s1": s["s1"], "r2": s["r2"], "s2": s["s2"], "a": s["rn"], "b": s["sn"]}


def exp_details_arm_matmul():
    o, t = exp_arm_matmul_observed(), exp_arm_matmul_time_vs_instr()
    return {"m1": t["t1"], "m2": t["t2"], "i1": t["i1"], "i2": t["i2"], "fl": o["fl"], "nl": o["nl"], "nine": o["nine"]}


def exp_details_arm_forward():
    f, g, a = exp_arm_short_forward(), exp_arm_short_gather(), exp_arm_short_add()
    return {"lo": f["lo"], "hi": f["hi"], "aa": f["aa"], "pct": a["pct"], "n": a["n"], "g": g["g"], "h": g["h"]}


def exp_details_arm_seeds():
    m = exp_arm_short_margin()
    return {"n": m["n"], "lim": m["lim"], "k": m["k"], "m": m["m"], "aa": f1(arm_noise()["identical_binary_aa"]["L2"]["pooled"]["half_width_pct"])}


def exp_details_arm_time_vs_instr():
    o = exp_arm_matmul_time_vs_instr()
    return {k: o[k] for k in ("t1", "t2", "i1", "i2", "l1", "l2")}


def exp_details_arm_verdict():
    v, a = exp_arm_add_l2(), exp_arm_run_to_run()
    exp_arm_verdict_form()
    return {"lo": v["lo"], "hi": v["hi"], "lim": v["lim"], "over": v["over"], "sd": v["sd"], "three": word(len(arm_cpu()["per_run"])),
            "out": a["out"], "chk": a["chk"], "eight": str(len(arm_reproduction()[1])), "gap": a["gap"]}


def exp_details_arm_sensitive():
    exp_arm_placement()
    return {}


def exp_details_arm_limits():
    c = arm_cpu()
    w = arm_start_window()
    exp_arm_runs()
    t = arm_toolchain()
    assert len({json.dumps(res["run"]["runner"], sort_keys=True) for _, res, _ in arm_jobs()}) == 1, "the Arm jobs ran on more than one machine image"
    one_cell = c["verdict"]["why"].count("missed by k02_add_fwd.L2;") == 1
    assert one_cell, f"the INCONCLUSIVE form no longer rests on the forward add at L2 alone: {c['verdict']['why']}"
    return {"a": c["runs"][0], "b": c["runs"][1], "c": c["runs"][2], "n": str(c["jobs"]), "runs": str(len(c["runs"])),
            "per": str(jobs_per_run()), "lim": str(job_limit_now()), "m": str(w["within"]), "sd": exp_arm_limits_spread()["s"],
            "o1": word(1), "o2": word(1), "three": word(len(c["runs"])), "clang": t["clang"], "lib": t["lib_major"],
            "w": placement_window_bytes(), "cell": word(1), **exp_arm_limits_placement(), "aa": exp_arm_limits_aa_l2()["aa"]}


def exp_details_arm_links():
    dirs = sorted(glob.glob(os.path.join(REPO, "results", "s8-arm-run-*")))
    for rel, res, _ in arm_jobs():
        run = re.search(r"s8-arm-run-(\d+)/", rel).group(1)
        assert res["run"]["workflow_run_url"] == PUBLIC_RUN_PREFIX + run, f"{rel}: the record links to {res['run']['workflow_run_url']}"
    return {"three": word(len(dirs))}


def exp_details_arm_other_arch():
    return {"c": arm_toolchain()["clang"], "model": arm_cpu()["cpu_model"]}


def exp_details_arm_followup():
    return {"k": str(len(ARM_KERNELS)), "model": arm_cpu()["cpu_model"], "n": str(arm_counts()["runs"])}


def exp_details_arm_stage():
    n = exp_arm_counts_digits()
    return {"three": word(arm_counts()["runs"]), "disp": str(arm_counts()["runs"] * jobs_per_run()), "ret": n["jobs"],
            "lim": str(job_limit_now()), "model": n["model"], "pool": n["jobs"], "runs": n["runs"]}


# ---- the table -------------------------------------------------------------------------------
# (label, source of the value, expected-value function, regex with one named group per typed value)

ROWS = [
    ("claim: Google's average in the opening paragraph", "site/data/index.json claim.google_pct",
     exp_google_pct, r"Google reported that this costs (?P<v>[\d.]+)% on average across its services, a third of a percent"),
    ("opening paragraph: lost-loop range", "site/data/index.json page.lost",
     exp_lost_range, r"the same checks make some loops \(reverse, stride-2, matrix multiply\) take (?P<lo>[\d.]+) to (?P<hi>[\d.]+) times as long as the same loop without them, at the study's sizes \(x86-64, one compiler version, data that fits in the CPU cache\)"),
    ("claim: Google's average in sentence 1", "site/data/index.json claim.google_pct",
     exp_google_pct, r"cost its services (?P<v>[\d.]+)% on average"),
    ("caption: reverse loop as long in the image alt text", "results/s7-pooled/pooled.json EPYC 7763 k04_rev.L1 aligned",
     exp_hero_reverse, r"the reverse loop with the check on drawn as (?P<v>[\d.]+) times as long"),
    ("caption: reverse loop as long under the image", "results/s7-pooled/pooled.json EPYC 7763 k04_rev.L1 aligned",
     exp_hero_reverse, r"The reverse loop takes (?P<v>[\d.]+)x as long as with the check off"),
    ("sentence 2: repetitions per side", "harness/criteria*.json reps_per_side",
     exp_reps, r"timed each pair (?P<lo>\d+) to (?P<hi>\d+) times per side"),
    ("sentence 3: lost-loop range", "site/data/index.json page.lost",
     exp_lost_range, r"took (?P<lo>[\d.]+) to (?P<hi>[\d.]+) times as long in cache at the study's sizes "
                     r"\(the smallest as compiled, the largest with the loops aligned\)\."),
    ("sentence 3: forward range, AVX2 exception, as-compiled forward add",
     "site/data/index.json page.forward and cpus; site/data/siblings.json clang18v3-fast",
     exp_forward_sentence,
     r"\((?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x aligned, one AVX2 exception, (?P<avx>[\d.]+)x\); "
     r"below 1x the checked loop ran faster \(cause inferred: loop layout\)\. "
     r"As compiled, the forward add cost about (?P<x>[\d.]+)x on (?P<n>\w+) of the (?P<of>\w+) AMD models"),
    ("sentence 3: Intel forward add", "site/data/index.json intel_forward and cpus; results/s7-pooled/pooled.json Xeon k02_add_fwd.L1 and k03_stencil.L2 aligned; robustness/seed-sensitivity-x86.json",
     exp_intel_sentence,
     r"Intel: in all (?P<jobs>\d+) Intel jobs seen \((?P<n>\w+) models; (?P<pool>\d+) are in the (?P<pooljobs>\d+)-job pool, (?P<early>\d+) in earlier runs, (?P<setc>\d+) more in set C\) "
     r"the forward add \(bounded by `size\(\)`\) at L1 cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x aligned, "
     r"against (?P<alo>[\d.]+)x to (?P<ahi>[\d.]+)x on the AMD models\. "
     r"The Xeon 8573C \((?P<j1>\d+) jobs\) has no verdict \(INCONCLUSIVE under the written rules\): "
     r"its forward add costs a measured (?P<x8573>[\d.]+)x, over the (?P<lim>\d+)% forward limit\. "
     r"The Xeon 6973P-C \((?P<j2>\d+) jobs\) has a verdict \(MAP\) that is borderline: with (?P<j2s6>\d+) jobs it was INCONCLUSIVE, "
     r"its stencil at L2 ending at (?P<end6>[\d.]+), over the same limit, and the (?P<ord>\w+) job moved that end to (?P<end7>[\d.]+); "
     r"with the bootstrap's draw no longer mattering that end is (?P<conv>[\d.]+), under the limit by (?P<convm>[\d.]+), "
     r"and the whole analysis gives INCONCLUSIVE under (?P<seedinc>\d+) of (?P<seedtot>\d+) other seeds, so the word is best read as undecided; "
     r"its forward add of (?P<x6973>[\d.]+)x is left out as placement-sensitive\. "
     r"A third model, the Xeon 8370C, drew (?P<j3>\d+) job, too few to judge\."),
    ("found: lost-loop range, models, siblings, no-vectorize controls",
     "site/data/index.json page.lost and cpus; site/data/siblings.json; results/s7-pooled/pooled.json EPYC 7763 positive and cells",
     exp_lost_bullet,
     r"\*\*(?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x slower\*\* in cache, at the study's sizes, for loops that lose SIMD .*?"
     r"on all (?P<n>\w+) CPU models with a verdict \(three AMD, and the Xeon 6973P-C, borderline\); the Xeon 8573C \(no verdict\) lost the same loops, "
     r"and the two Xeon models \((?P<ij>\d+) jobs each\) range (?P<ilo>[\d.]+)x to (?P<ihi>[\d.]+)x\. .*?reached about (?P<sib>[\d.]+)x at L1\. .*?"
     r"takes (?P<rev_novec>[\d.]+)x as long for reverse \((?P<rev_on>[\d.]+)x with the checks on, as compiled\), "
     r"(?P<s2_novec>[\d.]+)x for stride-2 \((?P<s2_on>[\d.]+)x\) and (?P<mm_novec>[\d.]+)x for matrix multiply \((?P<mm_on>[\d.]+)x\)"),
    ("found: loop census counts", "site/data/corpus.json census1, census2, categories",
     exp_census_bullet,
     r"\*\*(?P<lost1>\d+) of (?P<vec1>[\d,]+)\*\* vectorized loops in (?P<libs>\d+) general libraries lose SIMD, "
     r"against (?P<lost2>\d+) of (?P<vec2>[\d,]+) in (?P<projs>\d+) numeric projects\. Counted, not timed\. "
     r"Of the (?P<vec1b>[\d,]+), (?P<libcxx>\d+) are inside libc\+\+'s own headers and none of those was lost; "
     r"counting project code and the census's own driver files, it is (?P<p1lost>\d+) of (?P<p1>\d+) against (?P<p2lost>\d+) of (?P<p2>[\d,]+) "
     r"\((?P<drv>\w+) of those (?P=p2) is a driver loop\)\. "
     r"In the numeric set (?P<with>\d+) of (?P<of>\d+) projects have any lost loop, and LightGBM holds (?P<lgbm>\d+) of the (?P<of444>\d+)\."),
    ("found: real programs timed whole", "site/data/realworld.json rows and timing.groups",
     exp_realworld_bullet,
     r"\((?P<six>\w+) workloads from (?P<four>\w+) projects picked for their lost loops: LightGBM with (?P<lgbm>\w+) option sets.*?"
     r"detectably slower for (?P<n7>\w+) of the \w+ on EPYC 7763 \((?P<lo>[\d.]+)% to (?P<hi>[\d.]+)% across the two columns, (?P<j7>\d+) jobs; "
     r"(?P<p>\w+) of the \w+ projects\), (?P<n74>\w+) on EPYC 9V74 \((?P<j74>\d+) jobs\), "
     r"(?P<n45>\w+) on EPYC 9V45 \((?P<j45>\d+) jobs\); the rest were not detectable\. "
     r"(?P<ctl>\w+) control programs"),
    ("found: code placement", "site/data/layout.json; site/data/index.json cpus forward_compiled_max_cell",
     exp_placement_bullet,
     r"Across (?P<n>\d+) placements the reverse loop stays at (?P<rlo>[\d.]+)x to (?P<rhi>[\d.]+)x and the forward sum \(bounded by `size\(\)`\) near 1x; "
     r"the forward add \(bounded by `size\(\)`\) swings (?P<alo>[\d.]+)x to (?P<ahi>[\d.]+)x on (?P<models>\w+) models "
     r"\(as compiled (?P<c7763>[\d.]+)x on EPYC 7763 and (?P<c9v74>[\d.]+)x on 9V74"),
    ("found: one added size check", "site/data/mitigate.json reverse shape, variant pre",
     exp_mitigation, r"\*\*(?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x\*\* for the reverse loop after one added size check"),
    ("found: GCC", "site/data/siblings.json gcc14-O3-assert k02_add_fwd",
     exp_gcc,
     r"GCC 14 and libstdc\+\+'s own `_GLIBCXX_ASSERTIONS` \(a different library, different checks\) at `-O3`, "
     r"even the forward add loses SIMD and runs (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x slower "
     r"\((?P<jobs>\d+) jobs on (?P<n>\d+) CPU models; the low end is one job\)"),
    ("folders: why the forward add cost", "site/data/index.json page.forward.compiled",
     exp_why_1_6, r"why the forward add cost (?P<v>[\d.]+)x"),
    ("trust: newer clang timed", "site/data/versions.json; results/s7-pooled/pooled.json EPYC 7763 positive",
     exp_versions,
     r"Clang and libc\+\+ (?P<a>\d+) to (?P<b>\d+), timed on the eight loops \((?P<models>\w+) CPU model with enough jobs\).*?"
     r"\((?P<l1>[\d.]+)x at L1 on EPYC 7763, as slow as a build with no vectorization at all, and (?P<l2>[\d.]+)x at L2\)"),
    ("trust: matrix multiply lost per clang version", "site/data/cesweep.json rows (clang, x86-64, -O2, hardening macro in effect)",
     exp_cesweep,
     r"finds matrix multiply lost on clang (?P<a>\d+) to (?P<b>\d+) at baseline x86-64, kept on (?P<c>\d+) to (?P<d>\d+) "
     r"\(.*?\), and lost again on clang (?P<e>[\d.]+) and trunk \(as served on (?P<date>[\d-]+)\)"),
    ("trust: Ubuntu's clang 20", "results/siblings-run-*/*/siblings.json version string",
     exp_ubuntu_clang_20, r"Ubuntu's own clang (?P<v>[\d.]+) and libc\+\+ 20"),
    ("trust: machine state", "site/data/environment.json summary",
     exp_environment,
     r"Over (?P<jobs>\d+) jobs, steal was (?P<steal>[\d.]+)%, .*?drifted at most (?P<drift>[\d.]+)%\. "
     r"The driver was seen on the timed core's hyperthread sibling in (?P<share>\d+) jobs"),
    ("trust: counts are not time", "site/data/corpus.json",
     exp_counts_not_time, r"The (?P<a>[\d,]+) and (?P<b>[\d,]+) are loops, not hotness"),
    ("trust: real programs, projects", "site/data/realworld.json rows",
     exp_four_projects, r"\*\*Real programs\*\* \((?P<n>\w+) projects\)"),
    ("trust: day-one runs", "dayone/results/run-*",
     exp_dayone_runs, r"The day-one test \(the first (?P<n>\w+) runs\)"),
    ("trust: repetitions in the later rule versions", "harness/criteria-v3.json",
     exp_v3_reps, r"(?P<v>\d+) repetitions per side\) after earlier results"),
    ("trust: independence and holdout",
     "results/s7-pooled and s6-pooled and s4-pooled job counts and reproduction; robustness/results.json s7 forms; harness/pool.py with each Xeon 6973P-C job left out; site/data/holdout.json rows reproduced; robustness/calibration.json run_to_run s7 and s6",
     exp_independence_holdout,
     r"On the (?P<n>\d+)-job pool a block bootstrap and the other interval methods tried \(exploratory, \[report\]\(robustness/report\.md\)\) "
     r"change (?P<same>no verdict form) on EPYC 7763, 9V74, 9V45 or the Xeon 8573C; the Xeon 6973P-C stays MAP under (?P<k>\w+) of the (?P<m>\w+), "
     r"and changes with the set of jobs more than with the method \(leaving one job out, in turn, gives INCONCLUSIVE in (?P<inc>\d+) of its (?P<tot>\d+) cases\)\. "
     r"A fresh run, planned in writing \(the records do not show the order\), matched the original (?P<o>\d+)-job pool on (?P<yes>EPYC 7763 and 9V74), not (?P<no>9V45)\. "
     r"Run to run, a run's point fell outside another run's interval on EPYC 7763 in (?P<out>\d+) of (?P<chk>\d+) comparisons "
     r"\((?P<pct>\d+)%; (?P<pct6>\d+)% in the (?P<n6>\d+)-job pool\), against (?P<exp>[\d.]+) expected if the intervals were exactly calibrated; "
     r"the excess lies in the reverse, stride-2 and matrix-multiply cells \((?P<fo>\d+) of (?P<fn>\d+), against (?P<fe>[\d.]+) expected\), "
     r"not in the forward ones \((?P<go>\d+) of (?P<gn>\d+), against (?P<ge>[\d.]+)\), "
     r"and on EPYC 9V74 the count is (?P<vo>\d+) of (?P<vn>\d+) against (?P<ve>[\d.]+) expected "
     r"\(\[calibration baseline\]\(robustness/README-calibration\.md\)\)\."),
    ("folders: the eight loops", "site/data/index.json criteria.kernels",
     exp_eight_loops, r"`kernels/` the (?P<n>\d+) loops"),
    ("folders: the kernel pool", "results/s4-run-*/, results/s6-run-*/ and results/s7-run-*/ result files; results/s6-pooled/pooled.json",
     exp_kernel_pool_folders,
     r"the kernel pool is `s7-pooled`: the (?P<o>\d+) jobs of `s4-run-\*`, also pooled alone in `s4-pooled`, plus the (?P<n>\d+) of `s6-run-\*` "
     r"and the (?P<m>\d+) of `s7-run-\*`; `s6-pooled` is the (?P<s6>\d+)-job pool before the last two runs"),
    ("found: reverse and stride-2, loops with and without an exit count",
     "investigate/vectorizer/reverse-stride2/extracted/scalar-evolution.txt tally lines, clang 18 FAST",
     exp_compile_only_counts,
     r"of (?P<n>\d+) loops compiled with FAST, all (?P<yes>\d+) with an iteration count for every exit in the compiler's analysis "
     r"were vectorized and none of the (?P<no>\d+) with an uncounted exit"),
    ("found: compile-only tests, Compiler Explorer's release candidate and the timed build",
     "investigate/vectorizer/matmul/derived/revisions.txt; dayone/results/run-38116223923/remarks.*.fast.txt; results/s4-run-*/ and s6-run-*/ toolchain",
     exp_rc_and_same_remark,
     r"run on Compiler Explorer's clang (?P<ce>[\d.]+) release candidate, not the timed Ubuntu (?P<timed>[\d.]+)\)"),
    ("found: matrix multiply, the price of the checks", "investigate/vectorizer/matmul/raw/dbg_a18_fast.json; derived/cost-table.md",
     exp_matmul_units_readme,
     r"prices each of the two checks at (?P<u>\d+) units, so a width-4 vector iteration costs (?P<v>\d+) against (?P<s>\d+) for four scalar ones"),
    ("trust: shared machines", "results/s7-pooled/pooled.json, s6-pooled and s4-pooled; results/s6-run-*/ and s7-run-*/; tests/data/s6_job_steps.json; .github/workflows/measure.yml",
     exp_shared_machines,
     r"The kernel pool is (?P<jobs>\d+) jobs in (?P<runs>\d+) runs \((?P<lo>\d+) to (?P<hi>\d+) jobs for each AMD model, (?P<x>\d+) for each "
     r"of the two main Xeon models, (?P<third>\d+) for a third Xeon model\); (?P<new>\d+) of them come from (?P<twelve>\w+) later runs\. "
     r"(?P<ten>\w+) of those runs dispatched (?P<disp>\d+) jobs and (?P<ret>\d+) returned results: "
     r"all (?P<fin>\d+) finished their timing step, and the other (?P<lost>\d+) were cancelled at the (?P<limit>\d+)-minute limit "
     r"during the whole-repository check the workflow then ran, before the upload, and returned nothing \(the workflow now uploads first\)\. "
     r"The cut fell unevenly by CPU model \(EPYC 7763: (?P<e>\d+) of the (?P<ret2>\d+) that returned, against (?P<f>\d+) of the first (?P<g>\d+) jobs\), "
     r"and the effect of that mix on the ratios was not tested\."),
    ("trust: the two newest runs", "results/s7-run-*/; tests/data/s7_job_steps.json; .github/workflows/measure.yml",
     exp_newest_runs_readme,
     r"(?P<two>\w+) more runs, dispatched with the limit raised to (?P<now>\d+) minutes to check that jobs return \(not chosen on their results\), "
     r"returned (?P<ret>\d+) of (?P<disp>\d+) jobs, (?P<n7763>\d+) of them on EPYC 7763; every one ran past (?P<old>\d+) minutes, "
     r"which supports the account that the old limit, not the timing, cut the others\."),
    ("trust: the price of the checks by clang version", "investigate/vectorizer/matmul/raw/dbg_a18_fast.json, dbg_a19..21_fast.json",
     exp_cost_units_across_versions,
     r"clang 19 to 21 price each of the two checks at (?P<new>\d+) cost unit where clang 18 prices them at (?P<old>\d+)"),
    ("trust: the LLVM commit", "investigate/vectorizer/matmul/llvm-src/commit_b6a8f5486b.json and commit_in_tag.json",
     exp_commit_readme, r"LLVM commit `(?P<sha>[0-9a-f]{10})` caused it is inferred"),
    ("found: the lost loops are measured with clang 18", "results/s4-run-*/ toolchain",
     exp_x86_clang_major, r"reverse, stride-2, matrix multiply on x86-64 with clang (?P<c>\d+)\)"),
    ("try it: the Arm runner label", ".github/workflows/measure.yml runner input", exp_readme_runner_label,
     r"add `-f runner=(?P<label>ubuntu-[\d.]+-arm)` for the Arm column"),
    ("found: Arm column", "results/s8-arm-pooled/pooled.json cells, aa and verdict; per-job listings of results/s8-arm-run-*/; arm64/seed-sensitivity.json; site/data/arm64.json noise",
     exp_arm_readme_bullet,
     r"Arm \(a separate column; the figures above are x86-64\): on one Arm core type \((?P<model>[\w-]+), (?P<jobs>\d+) jobs in (?P<runs>\d+) runs, "
     r"the same compiler, flags and rules\) reverse and stride-2 lose their NEON loops and cost (?P<r>[\d.]+)x and (?P<s>[\d.]+)x at L1 "
     r"\(all ratios here as compiled\); matrix multiply keeps its NEON loop and still costs (?P<m1>[\d.]+)x at L1 \((?P<m2>[\d.]+)x at L2\); "
     r"forward loops bounded by `size\(\)` cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x at L1 \(the add and the stencil are placement-sensitive and not judged\), "
     r"against an A/A floor of (?P<aa>[\d.]+)% that belongs to one L1 cell\. "
     r"The verdict is INCONCLUSIVE under the written rules, which stay as written: the forward add at L2, aligned, has an interval ending at (?P<end>[\d.]+), "
     r"over the (?P<lim>[\d.]+) limit by (?P<over>[\d.]+), a margin inside the bootstrap's own seed noise \((?P<k>\d+) of (?P<n>\d+) other seeds end at or above (?P<lim2>[\d.]+)\) "
     r"in a cell where an identical binary is as noisy \(A/A half-width (?P<l2aa>[\d.]+)%\), so the data cannot separate INCONCLUSIVE from MAP there\."),
    ("trust: mostly x86-64", "results/s8-arm-pooled/pooled.json; per-job toolchain",
     exp_arm_readme_trust,
     r"\*\*Mostly x86-64\.\*\* Every figure outside the Arm bullet is x86-64 \(AMD and Intel\)\. The Arm column is one core type \((?P<model>[\w-]+)\) "
     r"on shared machines, (?P<jobs>\d+) jobs in (?P<runs>\d+) runs, clang (?P<c>\d+) only; its verdict is INCONCLUSIVE"),
    ("folders: the Arm runs", "results/s8-arm-pooled/pooled.json jobs",
     exp_arm_readme_folder, r"the Arm column is the (?P<jobs>\d+) jobs of `s8-arm-run-\*`, pooled apart in `s8-arm-pooled`"),
]

# ---- the same for readme-parts/DETAILS.md ------------------------------------------------------------

# the model names as the per-CPU table of DETAILS.md writes them, and the key that finds the pooled entry
TABLE_MODELS = (("AMD EPYC 7763", "7763"), ("AMD EPYC 9V74", "9V74"), ("AMD EPYC 9V45", "9V45"),
                ("Intel Xeon Platinum 8573C", "8573C"), ("Intel Xeon 6973P-C", "6973P-C"))


def exp_details_method():
    pooled, original = J(POOLED), J(POOLED_ORIGINAL)
    return {"jobs": str(pooled_jobs()), "runs": str(len(pooled["runs"])), "oj": str(pooled_jobs(original=True)),
            "orr": str(len(original["runs"])), "nj": str(pooled_jobs(pool=POOLED_S6) - pooled_jobs(original=True)),
            "later": word(later_runs()["runs"]), "nk": str(pooled_jobs() - pooled_jobs(pool=POOLED_S6)),
            "further": word(newest_runs()["runs"])}


def exp_table_row(key):
    def fn():
        c = cpu_like(key)
        lost, fwd = lost_values(c), forward_aligned(c)
        return {"jobs": str(c["jobs"]), "runs": str(len(c["runs"])), "aa": f3(c["aa"]["half_width_pct"]),
                "llo": f1(min(lost)), "lhi": f1(max(lost)), "flo": f2(min(fwd)), "fhi": f2(max(fwd))}
    return fn


def table_row_pattern(name):
    return (r"\| " + re.escape(name) + r" \| (?P<jobs>\d+) \((?P<runs>\d+)\) \| (?P<aa>[\d.]+)% \| [^|\n]* \| "
            r"(?P<llo>[\d.]+)x to (?P<lhi>[\d.]+)x \| (?P<flo>[\d.]+)x to (?P<fhi>[\d.]+)x \|")


def exp_table_stability_7763_9v74():
    out = {}
    for key, name in (("7763", "a"), ("9V74", "b")):
        c = cpu_like(key)
        assert c["stability"] == "stable", f"{key} is no longer 'stable'"
        out[name] = str(len(runs_with_verdict(c)))
        out[name + "o"] = str(len(c["runs"]) - len(runs_with_verdict(c)))
    return out


def exp_table_9v45():
    c = cpu_like("9V45")
    three = [r for r in c["per_run"] if r["jobs"] >= 3]
    assert len(three) == 1 and three[0]["form"] == "inconclusive", f"9V45 runs with 3 or more jobs: {three}"
    x = cell_of(c, "k03_stencil.L1")
    assert x["placement"]["sensitive"], "9V45 k03_stencil.L1 is no longer placement-sensitive"
    limit = 1 + c["verdict"]["forward_limit_pct"] / 100
    over = x["aligned"]["ci95"][1] - limit
    assert over > 0, "counted, 9V45 k03_stencil.L1 would no longer miss the forward limit"
    sf = seed_facts()
    assert sf["conv9m"] > 0 and sf["kept9"] == sf["draws9"], "the EPYC 9V45 stencil at L1 is no longer over the limit at the converged end and left out under every other seed"
    return {"one": str(len(three)), "n": str(len(c["per_run"])), "m": f4(over), "cm": f4(sf["conv9m"]), "keep": str(sf["kept9"]), "tot4": str(sf["draws9"])}


def exp_table_8573c():
    c = cpu_like("8573C")
    x = cell_of(c, "k02_add_fwd.L1")["aligned"]
    assert c["verdict"]["form"] == "inconclusive" and "missed by k02_add_fwd.L1" in c["verdict"]["why"]
    return {"r": f3(x["ratio"]), "lo": f3(x["ci95"][0]), "hi": f3(x["ci95"][1])}


def exp_table_6973pc():
    c, c6 = cpu_like("6973P-C"), cpu_like("6973P-C", pool=POOLED_S6)
    x = cell_of(c, "k03_stencil.L2")["aligned"]
    limit = 1 + c["verdict"]["forward_limit_pct"] / 100
    assert c["verdict"]["form"] == "map" and c6["verdict"]["form"] == "inconclusive" and x["ci95"][1] < limit, \
        "the Xeon 6973P-C is no longer MAP now and INCONCLUSIVE in the 75-job pool, with the stencil at L2 under the limit"
    sf = seed_facts()
    return {"j6": str(c6["jobs"]), "r": f3(x["ratio"]), "lo": f3(x["ci95"][0]), "hi": f3(x["ci95"][1]), "lim": f2(limit),
            "si": str(sf["inc"]), "st": str(sf["total"])}


def exp_table_note():
    a, b = cpu_like("8573C"), cpu_like("6973P-C")
    b6 = cpu_like("6973P-C", pool=POOLED_S6)
    index = J("site/data/index.json")
    assert not cell_of(a, "k02_add_fwd.L1")["placement"]["sensitive"]
    assert cell_of(b, "k02_add_fwd.L1")["placement"]["sensitive"]
    runs = {len(a["per_run"]), len(b["per_run"])}
    per = max(r["jobs"] for c in (a, b) for r in c["per_run"])
    assert len(runs) == 1 and per < 3 and a["stability"] == b["stability"] == "not assessable"
    limit = 1 + a["verdict"]["forward_limit_pct"] / 100
    stencil = cell_of(b, "k03_stencil.L2")["aligned"]
    # the newest job of the Xeon 6973P-C is the last of its inputs (they are sorted by path): from a noisy machine, lowest stencil ratio
    inputs = [i for i in J(POOLED)["inputs"] if "6973P-C" in i["cpu_model"]]
    assert "s7-run-" in inputs[-1]["path"] and len(inputs) == len(stencil["per_job"]), "the last 6973P-C input is not a job of the newest runs"
    newest = J(os.path.normpath(os.path.join(os.path.dirname(POOLED), inputs[-1]["path"])).replace("\\", "/"))
    aa7 = newest["controls"]["aa"]["half_width_pct"]
    aamax = index["criteria"]["aa_half_width_max_pct"]
    assert aa7 > aamax, f"the newest 6973P-C job's own A/A half-width {aa7:.2f}% is no longer above the {aamax}% limit"
    assert stencil["per_job"][-1] == min(stencil["per_job"]), "the newest 6973P-C job no longer has the lowest stencil ratio at L2"
    assert "no job is excluded on its own A/A half-width" in json.dumps(J("harness/criteria-v3.json")), \
        "harness/criteria-v3.json no longer says that no job is excluded on its own A/A control"
    # leaving each job out in turn
    loo = leave_one_job_out()
    maps = [path for path, form in loo if form == "map"]
    assert len(maps) == 1, f"the sentence names the one job whose absence gives MAP; the data gives {len(maps)}: {maps}"
    run_id, job = re.search(r"s6-run-(\d+)/results-[a-z0-9-]*-j(\d+)/", maps[0]).groups()
    # the interval methods of the robustness analysis
    methods = J("robustness/results.json")["datasets"]["s7"]["cpus"]["Intel(R) Xeon(R) 6973P-C"]["methods"]
    assert [m for m, v in methods.items() if v["form"] == "inconclusive"] == ["d0"], "the 6973P-C is no longer INCONCLUSIVE under the first form of the lag-1 correction only"
    few = index["page"]["cpus_few"]
    sf, af, sub = seed_facts(), aa_l2_facts(), calib_subsets()
    assert abs(sf["stored"] - stencil["ci95"][1]) < 1e-6
    return {"p": f3(cell_of(a, "k02_add_fwd.L1")["aligned"]["ratio"]),
            "lim": f2(limit),
            "res": thousands(sf["res"]), "conv": f4(sf["conv"]), "convm": f4(sf["convm"]), "sd": f4(sf["sd"]), "alt": str(sf["alt"]),
            "hits": str(sf["hits"]), "lim2": f2(sf["limit"]), "si": str(sf["inc"]), "st": str(sf["total"]), "sm": str(sf["map"]),
            "seven3": word(b["jobs"]), "sj3": "3", "sj5": "5", "s3i": str(sub[3][0]), "s3n": str(sub[3][1]), "s5i": str(sub[5][0]), "s5n": str(sub[5][1]),
            "aa2l": f2(af["x2"]), "aa1l": f2(af["x1"]), "ceil": f"{af['ceil']:g}",
            "al": f3(cell_of(b, "k02_add_fwd.L1")["aligned"]["ratio"]),
            "ac": f3(cell_of(b, "k02_add_fwd.L1")["as_compiled"]["ratio"]),
            "end": f3(stencil["ci95"][1]), "margin": f4(limit - stencil["ci95"][1]),
            "j6": str(b6["jobs"]), "n6": str(pooled_jobs(pool=POOLED_S6)),
            "end6": f3(cell_of(b6, "k03_stencil.L2")["aligned"]["ci95"][1]),
            "ord": ORDINALS[b["jobs"]], "aa7": f1(aa7), "aamax": f"{aamax:g}", "s7": f3(stencil["per_job"][-1]),
            "seven": word(b["jobs"]), "seven2": word(b["jobs"]),
            "inc": str(sum(1 for _, form in loo if form == "inconclusive")), "tot": str(len(loo)), "mj": job, "mr": run_id,
            "k": str(sum(1 for v in methods.values() if v["form"] == "map")), "m": str(len(methods)),
            "runs": str(runs.pop()), "per": str(per), "j8370": str(few[0]["jobs"]), "need": str(index["criteria"]["minimum_jobs"])}


def exp_details_forward():
    index = J("site/data/index.json")
    aligned = index["page"]["forward"]["aligned"]
    judged = []
    for key in ("7763", "9V45", "9V74"):
        c = cpu_like(key)
        ps = {x["cell_id"] for x in c["verdict"]["placement_sensitive"]}
        judged += [x["aligned"]["ratio"] for x in c["cells"] if x["kernel"] in FORWARD and x["cell_id"] not in ps]
    intel = index["intel_forward"]
    rows = intel_all_jobs()  # the page's rows (S3 runs, S4 smoke run, pooled jobs) and the Intel jobs of set C

    def of(short):
        return [v for s, v, _ in rows if s == short]

    def in_pool(short):
        return [v for s, v, src in rows if s == short and kernel_pool_source(src)]

    def in_set_c(short):
        return [v for s, v, src in rows if s == short and src.startswith("results/s9-run-")]

    x8370, x8573, x6973 = of("Xeon 8370C"), of("Xeon 8573C"), of("Xeon 6973P-C")
    pooled_8573, pooled_6973 = in_pool("Xeon 8573C"), in_pool("Xeon 6973P-C")
    a = cell_of(cpu_like("8573C"), "k02_add_fwd.L1")["aligned"]
    b = cell_of(cpu_like("6973P-C"), "k02_add_fwd.L1")["aligned"]
    return {"lo": f2(aligned["min"]), "hi": f2(aligned["max"]), "jlo": f3(min(judged)), "jhi": f3(max(judged)),
            "n": str(len(rows)), "m": word(len(intel["cpus"])), "pj": str(sum(len(in_pool(s)) for s in intel["cpus"])),
            "sc": str(sum(len(in_set_c(s)) for s in intel["cpus"])),
            "ea": str(len(rows) - sum(len(in_pool(s)) for s in intel["cpus"]) - sum(len(in_set_c(s)) for s in intel["cpus"])),
            "ilo": f2(min(v for _, v, _ in rows)), "ihi": f2(max(v for _, v, _ in rows)),
            "a1": f2(min(x8370)), "a2": f2(max(x8370)), "an": str(len(x8370)), "ap": str(len(in_pool("Xeon 8370C"))),
            "as": str(len(in_set_c("Xeon 8370C"))),
            "b1": f2(min(x8573)), "b2": f2(max(x8573)), "bn": str(len(x8573)), "bp": str(len(pooled_8573)),
            "bp1": f3(min(pooled_8573)), "bp2": f3(max(pooled_8573)), "bs": str(len(in_set_c("Xeon 8573C"))),
            "bpool": f3(a["ratio"]), "bl": f3(a["ci95"][0]), "bh": f3(a["ci95"][1]),
            "c1": f2(min(x6973)), "c1b": f2(max(x6973)), "cn": str(len(x6973)), "c2": f3(min(x6973)), "c3": f3(max(x6973)),
            "cp": str(len(pooled_6973)), "cp1": f3(min(pooled_6973)), "cp2": f3(max(pooled_6973)), "cs": str(len(in_set_c("Xeon 6973P-C"))),
            "cpool": f3(b["ratio"]), "cl": f3(b["ci95"][0]), "ch": f3(b["ci95"][1])}


def exp_details_positive():
    c = cpu_like("7763")

    def pos(k):
        return f2(c["positive"][k]["ratio"])

    def on(k):
        return f2(cell_of(c, k)["as_compiled"]["ratio"])

    return {"p": str(c["jobs"]), "a": pos("k08_matmul.L1"), "b": pos("k08_matmul.L2"), "jobs": str(c["jobs"]),
            "r1": pos("k04_rev.L1"), "r2": pos("k04_rev.L2"), "R1": on("k04_rev.L1"), "R2": on("k04_rev.L2"),
            "s1": pos("k05_stride2.L1"), "s2": pos("k05_stride2.L2"), "S1": on("k05_stride2.L1"), "S2": on("k05_stride2.L2"),
            "m1": pos("k08_matmul.L1"), "m2": pos("k08_matmul.L2"), "M1": on("k08_matmul.L1"), "M2": on("k08_matmul.L2")}


def exp_details_novec_range():
    """The no-vectorize build against the checks-on build at L1 on the four models the sentence names (all but EPYC 7763
    among the models with enough jobs; the Xeon 8370C, with one job, is not shown)."""
    others = [c for c in enough_cpus() if "7763" not in c["cpu_model"]]
    assert len(others) == 4, f"the sentence lists four models; the pool has {len(others)} besides EPYC 7763 with enough jobs"
    nv, on = [], []
    for c in others:
        for k in ("k04_rev.L1", "k05_stride2.L1", "k08_matmul.L1"):
            nv.append(c["positive"][k]["ratio"])
            on.append(cell_of(c, k)["as_compiled"]["ratio"])
    return {"nlo": f1(min(nv)), "nhi": f1(max(nv)), "olo": f1(min(on)), "ohi": f1(max(on))}


def exp_details_instr_bullet():
    a, b = cpu_like("8573C"), cpu_like("6973P-C")
    assert a["jobs"] == b["jobs"]
    return {"a": f2(cell_of(a, "k02_add_fwd.L1")["aligned"]["ratio"]), "b": f2(cell_of(b, "k02_add_fwd.L1")["aligned"]["ratio"]),
            "j": str(a["jobs"])}


def exp_details_versions():
    cpus = enough_cpus()
    mm = [cell_of(c, k)[col]["ratio"] for c in cpus for k in ("k08_matmul.L1", "k08_matmul.L2") for col in ("as_compiled", "aligned")]
    c7763, c9v45 = cpu_like("7763"), cpu_like("9V45")
    return {"lo": f1(min(mm)), "hi": f1(max(mm)), "five": word(len(cpus)),
            "a": f1(cell_of(c7763, "k08_matmul.L1")["as_compiled"]["ratio"]),
            "b": f1(cell_of(c7763, "k08_matmul.L2")["as_compiled"]["ratio"]),
            "c": f1(max(cell_of(c9v45, k)["as_compiled"]["ratio"] for k in ("k08_matmul.L1", "k08_matmul.L2")))}


def exp_details_shared():
    pooled = J(POOLED)
    out = {"jobs": str(pooled_jobs()), "runs": str(len(pooled["runs"]))}
    for tag, key in (("a", "7763"), ("b", "9V45"), ("c", "9V74"), ("d", "8573C"), ("e", "6973P-C"), ("f", "8370C")):
        c = cpu_like(key)
        out[tag], out[tag + "r"] = str(c["jobs"]), str(len(c["runs"]))
    c7763, c9v74, c9v45 = cpu_like("7763"), cpu_like("9V74"), cpu_like("9V45")
    assert c7763["stability"] == c9v74["stability"] == "stable" and c9v45["stability"] == "not assessable"
    out.update({"need": str(J("site/data/index.json")["criteria"]["minimum_jobs"]),
                "s1": str(len(runs_with_verdict(c7763))), "s1n": str(len(c7763["runs"])),
                "s2": str(len(runs_with_verdict(c9v74))), "s2n": str(len(c9v74["runs"])),
                "n45": str(max(r["jobs"] for r in c9v45["per_run"]))})
    return out


def lost_cells(pooled, enough_only=False):
    minimum = J("site/data/index.json")["criteria"]["minimum_jobs"]
    return [c[col]["ratio"] for cpu in pooled["cpus"] if not enough_only or cpu["jobs"] >= minimum
            for c in cpu["cells"] if c["class"] == "lost" for col in ("as_compiled", "aligned")]


def amd_shift_from_original(pool):
    """The largest move of a lost-loop cell on an AMD model, either column, between the original pool and another pool."""
    original = J(POOLED_ORIGINAL)
    shift = 0.0
    for c in J(pool)["cpus"]:
        if "AMD" not in c["cpu_model"]:
            continue
        old = next(o for o in original["cpus"] if o["cpu_model"] == c["cpu_model"])
        for x in c["cells"]:
            if x["class"] == "lost":
                y = cell_of(old, x["cell_id"])
                shift = max(shift, *(abs(x[col]["ratio"] - y[col]["ratio"]) for col in ("as_compiled", "aligned")))
    bound = int(shift * 100) / 100 + 0.01  # the next hundredth above the largest shift
    assert 0 < bound - shift <= 0.01
    return shift, bound


def exp_details_later_runs():
    lr = later_runs()
    original = J(POOLED_ORIGINAL)
    assert not any("6973P-C" in c["cpu_model"] for c in original["cpus"]), "the Xeon 6973P-C is now in the original pool"
    shift, bound = amd_shift_from_original(POOLED_S6)
    s6_lost = lost_cells(J(POOLED_S6), enough_only=True)
    ll = later_losses()
    by = ll["by_model"]
    ret, miss = str(lr["returned"]), str(lr["dispatched"] - lr["returned"])
    return {"disp": str(lr["dispatched"]), "ret": ret, "miss": miss, "miss2": miss, "miss3": miss, "ret2": ret, "ret3": ret, "ret4": ret, "ret5": ret,
            "fin": str(ll["finished"]), "tlo": ll["t_lo"], "thi": ll["t_hi"], "tl": ll["t_lost"], "tr": ll["t_ret"],
            "lim": str(lr["limit"]), "inp": str(ll["in_progress"]), "failed": str(ll["failed"]), "flo": ll["f_lo"], "fhi": ll["f_hi"],
            "rlo": ll["r_lo"], "rhi": ll["r_hi"], "r7": ll["r7763"], "canc": str(ll["cancelled_back"]),
            "now": str(lr["now"]), "a": str(by["9V74"]), "b": str(by["9V45"]), "c": str(by["6973P-C"]), "d": str(by["8573C"]), "e": str(by["7763"]),
            "f": str(cpu_like("7763", original=True)["jobs"]), "g": str(pooled_jobs(original=True)),
            "o": str(pooled_jobs(original=True)), "n75": str(pooled_jobs(pool=POOLED_S6)), "mv": f2(bound),
            "lo": f3(min(s6_lost)), "hi": f3(max(s6_lost)), "olo": f3(min(lost_cells(original))), "ohi": f3(max(lost_cells(original))),
            "g7763": word(by["7763"]),
            "w": str(cpu_like("8573C", original=True)["jobs"]), "x": str(cpu_like("8573C", pool=POOLED_S6)["jobs"]),
            "y": str(cpu_like("6973P-C", pool=POOLED_S6)["jobs"])}


def exp_details_newest_runs():
    nr, lr, nl = newest_runs(), later_runs(), newest_losses()
    s6, s7 = J(POOLED_S6), J(POOLED)
    shift, bound = amd_shift_from_original(POOLED)
    assert shift < 0.05, f"a lost-loop cell on an AMD model moved by {shift:.3f} from the original pool"
    forms6 = {c["cpu_model"]: c["verdict"]["form"] for c in s6["cpus"]}
    forms7 = {c["cpu_model"]: c["verdict"]["form"] for c in s7["cpus"] if c["cpu_model"] in forms6}
    changed = sorted(m for m in forms6 if forms6[m] != forms7[m])
    assert changed == ["Intel(R) Xeon(R) 6973P-C"] and forms6[changed[0]] == "inconclusive" and forms7[changed[0]] == "map", \
        f"the sentence says the two newest runs changed one verdict, the Xeon 6973P-C's, from INCONCLUSIVE to MAP; the data gives {changed}"
    s7_lost = lost_cells(s7, enough_only=True)
    by = nl["by_model"]
    return {"two": word(nr["runs"]), "day": nr["day"], "now": str(nr["now"]), "disp": str(nr["dispatched"]), "ret": str(nr["returned"]),
            "e7763": str(by["7763"]), "e9v74": str(by["9V74"]), "e9v45": str(by["9V45"]), "c": str(by["6973P-C"]), "d": str(by["8573C"]), "t": str(by["8370C"]),
            "tlo": nl["t_lo"], "thi": nl["t_hi"], "ptlo": later_losses()["t_lo"], "pthi": later_losses()["t_hi"],
            "clo": nl["c_lo"], "chi": nl["c_hi"], "pclo": nl["prev_lo"], "pchi": nl["prev_hi"],
            "totlo": nl["tot_lo"], "tothi": nl["tot_hi"], "old": str(lr["limit"]), "margin": nl["margin"], "limit": str(nr["now"]),
            "n95": str(pooled_jobs()), "lo": f3(min(s7_lost)), "hi": f3(max(s7_lost)), "mv": f2(bound), "shift": f3(shift)}


def exp_details_holdout_later():
    return {"n": str(pooled_jobs() - pooled_jobs(original=True))}


def exp_details_robustness():
    rb = J("robustness/results.json")["datasets"]
    rho = [c["autocorr"]["rho_e_median"] for ds in rb.values() for c in ds["cpus"].values()]
    s7 = rb["s7"]["cpus"]
    amd = [c for name, c in s7.items() if "EPYC" in name]
    x8573 = next(c for name, c in s7.items() if "8573C" in name)
    x6973 = next(c for name, c in s7.items() if "6973P-C" in name)
    assert len(amd) == 3 and all(all(m["form"] == "map" for m in c["methods"].values()) for c in amd), "an AMD model is no longer MAP under every method"
    assert all(m["form"] == "inconclusive" for m in x8573["methods"].values()), "the Xeon 8573C is no longer INCONCLUSIVE under every method"
    assert [m for m, v in x6973["methods"].items() if v["form"] == "inconclusive"] == ["d0"]
    for name, c in s7.items():  # the block bootstrap (b) changes no classification, no placement flag and no form against the harness's (a)
        a, b = c["methods"]["a"], c["methods"]["b"]
        assert a["form"] == b["form"], f"{name}: the form changes under the block bootstrap"
        for cid, ca in a["cells"].items():
            cb = b["cells"][cid]
            assert ca["class"] == cb["class"] and ca.get("ps") == cb.get("ps"), f"{name} {cid}: the class or the placement flag changes under the block bootstrap"
    s4 = next(c for name, c in rb["s4"]["cpus"].items() if "9V45" in name)
    stencil = x6973["methods"]
    limit = 1 + cpu_like("6973P-C")["verdict"]["forward_limit_pct"] / 100
    return {"n6": str(pooled_jobs(pool=POOLED_S6)), "n7": str(pooled_jobs()), "n7b": str(pooled_jobs()),
            "lo": f2(min(rho)), "hi": f2(max(rho)), "five": word(len(s7)),
            "eight": word(len(x6973["methods"])), "eight2": word(len(x8573["methods"])), "eight3": word(len(x6973["methods"])),
            "three": word(sum(1 for v in s4["methods"].values() if v["form"] == "inconclusive")),
            "k": word(sum(1 for v in x6973["methods"].values() if v["form"] == "map")),
            "pooled": f3(stencil["a"]["cells"]["k03_stencil.L2"]["al"][2]), "blk": f3(stencil["b"]["cells"]["k03_stencil.L2"]["al"][2]),
            "lim": f2(limit)}


def exp_details_9v45_call():
    new, old = cpu_like("9V45"), cpu_like("9V45", original=True)
    mid = cpu_like("9V45", pool=POOLED_S6)
    a, b = cell_of(new, "k03_stencil.L1"), cell_of(old, "k03_stencil.L1")
    limit = 1 + new["verdict"]["forward_limit_pct"] / 100
    ps = lambda c: sorted(x["cell_id"] for x in c["verdict"]["placement_sensitive"])
    assert ps(new) == ps(mid), "the placement-sensitive set of EPYC 9V45 changed between the 75-job and the 95-job pool"
    assert "k02_add_fwd.L2" in ps(new) and "k02_add_fwd.L2" not in ps(old), "k02_add_fwd.L2 did not join the placement-sensitive set after the original pool"
    return {"pj": str(pooled_jobs()), "last": str(pooled_jobs() - pooled_jobs(pool=POOLED_S6)),
            "a": f4(a["placement"]["d"]["ci95"][1]), "b": f4(b["placement"]["d"]["ci95"][1]),
            "n": str(pooled_jobs(original=True)), "c": f4(a["aligned"]["ci95"][1]), "lim": f4(limit),
            "d": f4(a["aligned"]["ci95"][1] - limit), "e": f3(b["aligned"]["ci95"][1])}


def exp_details_reproduction():
    a, b = cpu_like("7763")["reproduction"], cpu_like("9V74")["reproduction"]
    a6, b6 = cpu_like("7763", pool=POOLED_S6)["reproduction"], cpu_like("9V74", pool=POOLED_S6)["reproduction"]

    def gap(r):
        return f2(max(m["gap_pct"] for m in r["misses"]))

    def pct(r):
        return f"{100 * r['outside'] / r['checked']:.0f}"

    assert a["outside"] / a["checked"] > a6["outside"] / a6["checked"] and b["outside"] / b["checked"] > b6["outside"] / b6["checked"], \
        "the share of comparisons outside another run's interval did not rise from the 75-job to the 95-job pool"
    return {"a": str(a["outside"]), "b": str(a["checked"]), "ap": pct(a), "c": gap(a),
            "d": str(b["outside"]), "e": str(b["checked"]), "dp": pct(b), "f": gap(b),
            "n6": str(pooled_jobs(pool=POOLED_S6)),
            "a6": str(a6["outside"]), "b6": str(a6["checked"]), "ap6": pct(a6), "c6": gap(a6),
            "d6": str(b6["outside"]), "e6": str(b6["checked"]), "dp6": pct(b6), "f6": gap(b6)}


def exp_details_aa():
    c = cpu_like("7763")
    return {"j": str(c["jobs"]), "a": f2(c["aa"]["half_width_pct"]), "b": f3(c["aa"]["half_width_pct"])}


def exp_details_stage_s6():
    lr = later_runs()
    return {"disp": str(lr["dispatched"]), "ret": str(lr["returned"]), "miss": str(lr["dispatched"] - lr["returned"]),
            "lim": str(lr["limit"]), "o": str(pooled_jobs(original=True)), "n75": str(pooled_jobs(pool=POOLED_S6)),
            "j6": str(cpu_like("6973P-C", pool=POOLED_S6)["jobs"])}


def exp_details_stage_s7():
    nr = newest_runs()
    return {"disp": str(nr["dispatched"]), "ret": str(nr["returned"]), "lim": str(nr["now"]), "n75": str(pooled_jobs(pool=POOLED_S6)),
            "n95": str(pooled_jobs()), "j7": str(cpu_like("6973P-C")["jobs"]), "two": str(nr["runs"])}


def exp_details_reverse_stride2():
    yes, no = scev_tally()
    functions, counted = handwritten_bound()
    return {"ans": str(vectorizer_raw_answers()), "n": str(yes + no), "yes": str(yes), "yes2": str(yes),
            "no": str(no), "hv": str(counted), "hn": str(functions)}


def exp_details_matmul():
    scalar, vector = matmul_sums("clang 18.1.0 (assertions), FAST")
    new = {matmul_compare_cost(f"dbg_a{v}_fast") for v in (19, 20, 21)}
    assert len(new) == 1
    return {"req": str(matmul_requests()), "c18": str(matmul_compare_cost("dbg_a18_fast")),
            "c42": str(matmul_compare_cost("dbg_a18_fast_v2")), "c3": str(matmul_compare_cost("dbg_a18_fast_v3")),
            "vec": str(vector), "sc": str(4 * scalar), "c19": str(new.pop())}


def exp_details_layout():
    layout = J("site/data/layout.json")

    def row(short):
        c = next(c for c in layout["cpus"] if c["cpu_short"] == short)
        return next(r for r in c["rows"] if r["kernel"] == "k02_add_fwd" and r["size"] == "L1")

    a, b, c = row("EPYC 7763"), row("EPYC 9V74"), row("EPYC 9V45")
    assert a["verdict"] == b["verdict"] == "MIXED" and c["verdict"] == "ROBUST", (a["verdict"], b["verdict"], c["verdict"])
    assert a["as_compiled"] > 1.5 and b["as_compiled"] > 1.5, "the as-compiled placement is no longer the slow one on 7763 and 9V74"
    return {"lo7": f3(a["min"]), "hi7": f3(a["max"]), "lo74": f3(b["min"]), "hi74": f3(b["max"]),
            "a7": f3(a["aligned"]), "a74": f3(b["aligned"]), "m45": f3(c["median"]), "p45": str(c["n_pass"]), "n45": str(c["n_placements"])}


def exp_details_links():
    later_job_records()  # asserts that every returned record of the ten runs links to this repository's run pages
    later_job_records("s7", STEP_RECORDS_S7)  # and so does every record of the two newest runs
    return {"twelve": word(len(glob.glob(os.path.join(REPO, "results", "s6-run-*"))) + len(glob.glob(os.path.join(REPO, "results", "s7-run-*"))))}


def exp_details_trunk_vectorizer():
    days = vectorizer_trunk_days()
    assert len(days) == 1, f"the reverse and stride-2 study sent its trunk requests on {sorted(days)}"
    return {"d": days.pop()}


def exp_details_trunk_sweep():
    return {"d": cesweep_trunk_date()}


def exp_details_trunk_revision():
    version, sha = matmul_revision("pipe_ctrunk_fast")
    return {"sha": sha}


def exp_details_same_remark():
    return {"timed": exp_rc_and_same_remark()["timed"]}


def exp_details_commit():
    sha, tags = llvm_commit()
    assert tags["llvmorg-19.1.0"] == "ahead"
    assert all(tags[f"llvmorg-{v}"] != "ahead" for v in ("18.1.0", "18.1.3", "18.1.8"))
    return {"sha": sha, "in": "19.1.0", "n1": "18.1.0", "n2": "18.1.3", "n3": "18.1.8"}


DETAILS_ROWS = [
    ("details: the method, jobs and runs", "results/s7-pooled/pooled.json; results/s4-pooled/pooled.json; results/s6-run-*/",
     exp_details_method,
     r"(?P<jobs>\d+) jobs over (?P<runs>\d+) runs \(the original (?P<oj>\d+) jobs in (?P<orr>\d+) runs, then (?P<nj>\d+) more from "
     r"(?P<later>\w+) later runs and (?P<nk>\d+) more from (?P<further>\w+) further runs\)"),
] + [
    (f"details: table row, {name}", "results/s7-pooled/pooled.json cells, aa and runs", exp_table_row(key), table_row_pattern(name))
    for name, key in TABLE_MODELS
] + [
    ("details: table, stability of EPYC 7763 and 9V74", "results/s7-pooled/pooled.json per_run", exp_table_stability_7763_9v74,
     r"\| AMD EPYC 7763 \|[^|\n]*\|[^|\n]*\| MAP, the same in each of the (?P<a>\d+) runs with 3 or more jobs \(the other run has (?P<ao>\d+)\)"
     r".*?\| AMD EPYC 9V74 \|[^|\n]*\|[^|\n]*\| MAP, the same in each of the (?P<b>\d+) runs with 3 or more jobs \(the other (?P<bo>\d+) have fewer\)"),
    ("details: table, EPYC 9V45 borderline", "results/s7-pooled/pooled.json EPYC 9V45 per_run and k03_stencil.L1", exp_table_9v45,
     r"MAP; stability not assessable \((?P<one>\d+) of (?P<n>\d+) runs has 3 or more jobs, and that run alone is INCONCLUSIVE\); "
     r"borderline: counted, one left-out cell would miss the forward limit by (?P<m>[\d.]+) \((?P<cm>[\d.]+) at the converged end of its interval; "
     r"that cell stays left out under (?P<keep>\d+) of (?P<tot4>\d+) other seeds\) \|"),
    ("details: table, Xeon 8573C verdict", "results/s7-pooled/pooled.json Xeon 8573C k02_add_fwd.L1 aligned", exp_table_8573c,
     r"INCONCLUSIVE: the forward add at L1, aligned (?P<r>[\d.]+) \[(?P<lo>[\d.]+), (?P<hi>[\d.]+)\], misses the 2% forward rule"),
    ("details: table, Xeon 6973P-C verdict", "results/s7-pooled/pooled.json Xeon 6973P-C k03_stencil.L2 aligned", exp_table_6973pc,
     r"MAP, borderline: INCONCLUSIVE with (?P<j6>\d+) jobs; the stencil at L2, aligned (?P<r>[\d.]+) \[(?P<lo>[\d.]+), (?P<hi>[\d.]+)\], "
     r"now ends under the (?P<lim>[\d.]+) limit; the forward add at L1 is placement-sensitive and left out; "
     r"INCONCLUSIVE in (?P<si>\d+) of (?P<st>\d+) whole analyses under other seeds, so best read as undecided \|"),
    ("details: table, the note on the Intel rows",
     "results/s7-pooled and s6-pooled Xeon cells and per_run; the newest 6973P-C job's results.json; robustness/results.json s7; harness/pool.py with each 6973P-C job left out; "
     "robustness/seed-sensitivity-x86.json, aa-l2.json and calibration.json",
     exp_table_note,
     r"fails the rule \(point (?P<p>[\d.]+), limit (?P<lim>[\d.]+)\)\. For the Xeon 6973P-C the forward add at L1 \(aligned (?P<al>[\d.]+), "
     r"as compiled (?P<ac>[\d.]+)\) is placement-sensitive and left out, and the verdict passes on the stencil at L2, whose interval ends at "
     r"(?P<end>[\d.]+) under the stored seed, a margin of (?P<margin>[\d.]+) under the limit that belongs to that seed alone: "
     r"with the bootstrap's draw no longer mattering \((?P<res>[\d,]+) resamples\) the end is (?P<conv>[\d.]+), under the limit by (?P<convm>[\d.]+), "
     r"which is less than the (?P<sd>[\d.]+) \(sd\) by which one draw's end varies over (?P<alt>\d+) other seeds, in (?P<hits>\d+) of which it is at or above (?P<lim2>[\d.]+), "
     r"and the whole analysis is INCONCLUSIVE in (?P<si>\d+) of (?P<st>\d+) other seeds \(MAP in (?P<sm>\d+)\)\. "
     r"With the (?P<j6>\d+) jobs of the (?P<n6>\d+)-job pool the same cell ended at "
     r"(?P<end6>[\d.]+) and the model was INCONCLUSIVE\. The (?P<ord>\w+) job came from a noisy machine \(its own A/A control (?P<aa7>[\d.]+)%, "
     r"above the (?P<aamax>\d+)% limit for a single job's own verdict, and a stencil ratio of (?P<s7>[\d.]+), the lowest of the (?P<seven>\w+)\) "
     r"and moved the end under the limit; the pooled rules exclude no job on its own A/A control \(`harness/criteria-v3\.json`\)\. "
     r"Pooling the (?P<seven2>\w+) jobs again with each one left out in turn gives INCONCLUSIVE in (?P<inc>\d+) of the (?P<tot>\d+) cases "
     r"\(MAP only without job (?P<mj>\d+) of run (?P<mr>\d+); `tests/test_readme_numbers\.py` repeats this\), "
     r"and the model is MAP under (?P<k>\d+) of the (?P<m>\d+) interval methods of the robustness analysis "
     r"\(INCONCLUSIVE only under the first form of the lag-1 correction\)\. "
     r"The form depends on which jobs were drawn more than on the interval method, and the verdict is borderline and best read as undecided: "
     r"drawing (?P<sj3>\d+) of the (?P<seven3>\w+) jobs at random gives INCONCLUSIVE in (?P<s3i>\d+) of (?P<s3n>\d+) draws and all (?P<sj5>\d+)-job subsets in (?P<s5i>\d+) of (?P<s5n>\d+) "
     r"\(`robustness/README-calibration\.md`\), and an identical binary timed at L2 has a pooled half-width of (?P<aa2l>[\d.]+)% on this model against (?P<aa1l>[\d.]+)% at L1, "
     r"above the rule's (?P<ceil>\d+)% ceiling, which the rule reads at L1 only \(read at L2, the ceiling clause would end this verdict at INCONCLUSIVE; the rule is not changed\)\. "
     r"Neither Xeon model has a run with 3 jobs, so stability is not assessable, and the jobs of each came from (?P<runs>\d+) runs "
     r"\(at most (?P<per>\d+) per run\)\. The Xeon Platinum 8370C drew (?P<j8370>\d+) job \((?P<need>\d+) are needed\): no verdict and no numbers shown\."),
    ("details: forward loops, AMD and Intel", "site/data/index.json page.forward and intel_forward; results/s7-pooled/pooled.json",
     exp_details_forward,
     r"forward loops bounded by `size\(\)` ran (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x of the unchecked time there; .*?judges ran (?P<jlo>[\d.]+)x to (?P<jhi>[\d.]+)x\. "
     r"The Intel models differ\. In each of (?P<n>\d+) Intel jobs seen \((?P<m>\w+) models; (?P<pj>\d+) of them in the kernel pool, (?P<ea>\d+) in earlier runs and (?P<sc>\d+) more in set C\) "
     r"the forward add at L1, aligned, cost "
     r"(?P<ilo>[\d.]+)x to (?P<ihi>[\d.]+)x: Xeon 8370C (?P<a1>[\d.]+)x to (?P<a2>[\d.]+)x \((?P<an>\d+) jobs, (?P<ap>\d+) in the kernel pool, (?P<as>\d+) in set C\), "
     r"Xeon 8573C (?P<b1>[\d.]+)x to (?P<b2>[\d.]+)x \((?P<bn>\d+) jobs; the (?P<bp>\d+) pooled ones (?P<bp1>[\d.]+) to (?P<bp2>[\d.]+), "
     r"pooled (?P<bpool>[\d.]+) \[(?P<bl>[\d.]+), (?P<bh>[\d.]+)\]; (?P<bs>\d+) in set C\) and Xeon 6973P-C (?P<c1>[\d.]+)x to (?P<c1b>[\d.]+)x \((?P<cn>\d+) jobs, "
     r"(?P<c2>[\d.]+) to (?P<c3>[\d.]+); the (?P<cp>\d+) pooled ones (?P<cp1>[\d.]+) to (?P<cp2>[\d.]+), pooled (?P<cpool>[\d.]+) \[(?P<cl>[\d.]+), (?P<ch>[\d.]+)\]; "
     r"(?P<cs>\d+) in set C\)"),
    ("details: positive control on EPYC 7763", "results/s7-pooled/pooled.json EPYC 7763 positive and cells", exp_details_positive,
     r"the (?P<p>\d+)-job pool in `results/s7-pooled/pooled.json` gives (?P<a>[\d.]+)x and (?P<b>[\d.]+)x\).*?"
     r"Pooled EPYC 7763 positive control \((?P<jobs>\d+) jobs, .*?reverse (?P<r1>[\d.]+)x at L1 and (?P<r2>[\d.]+)x at L2 against "
     r"(?P<R1>[\d.]+)x and (?P<R2>[\d.]+)x; stride-2 (?P<s1>[\d.]+)x and (?P<s2>[\d.]+)x against (?P<S1>[\d.]+)x and (?P<S2>[\d.]+)x; "
     r"matrix multiply (?P<m1>[\d.]+)x and (?P<m2>[\d.]+)x against (?P<M1>[\d.]+)x and (?P<M2>[\d.]+)x\."),
    ("details: no-vectorize build on the other models", "results/s7-pooled/pooled.json positive and cells, the other four models",
     exp_details_novec_range,
     r"the no-vectorize build at (?P<nlo>[\d.]+)x to (?P<nhi>[\d.]+)x at L1 against (?P<olo>[\d.]+)x to (?P<ohi>[\d.]+)x with the checks on "
     r"\(EPYC 9V45, EPYC 9V74, Xeon 8573C and Xeon 6973P-C\)"),
    ("details: forward add instructions bullet", "results/s7-pooled/pooled.json Xeon k02_add_fwd.L1 aligned", exp_details_instr_bullet,
     r"on the Intel models it is (?P<a>[\d.]+)x at L1 on the Xeon 8573C and (?P<b>[\d.]+)x on the Xeon 6973P-C \((?P<j>\d+) pooled jobs each\)"),
    ("details: matrix multiply across the CPU models", "results/s7-pooled/pooled.json k08_matmul cells", exp_details_versions,
     r"at (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x across the (?P<five>\w+) CPU models: (?P<a>[\d.]+)x at L1 and (?P<b>[\d.]+)x at L2 on EPYC 7763, "
     r"up to (?P<c>[\d.]+)x on EPYC 9V45 as compiled"),
    ("details: shared runners, jobs per model", "results/s7-pooled/pooled.json cpus, per_run, stability", exp_details_shared,
     r"The kernel pool has (?P<jobs>\d+) jobs in (?P<runs>\d+) runs: EPYC 7763 (?P<a>\d+) jobs \((?P<ar>\d+) runs\), EPYC 9V45 (?P<b>\d+) "
     r"\((?P<br>\d+)\), EPYC 9V74 (?P<c>\d+) \((?P<cr>\d+)\), Xeon Platinum 8573C (?P<d>\d+) \((?P<dr>\d+)\), Xeon 6973P-C (?P<e>\d+) "
     r"\((?P<er>\d+)\) and Xeon Platinum 8370C (?P<f>\d+) \((?P<fr>\d+)\)\. A run needs (?P<need>\d+) jobs .*?only EPYC 7763 \((?P<s1>\d+) of its (?P<s1n>\d+) runs\) and EPYC 9V74 "
     r"\((?P<s2>\d+) of (?P<s2n>\d+)\) could be tested.*?EPYC 9V45 has one run with (?P<n45>\d+) jobs"),
    ("details: the ten later runs", "tests/data/s6_job_steps.json; results/s6-run-*/; .github/workflows/measure.yml; results/s4-pooled and s6-pooled", exp_details_later_runs,
     r"added jobs: (?P<disp>\d+) dispatched, (?P<ret>\d+) returned results, and the other (?P<miss>\d+) returned nothing\. "
     r"The step records of the runs .*? show where they were lost\. "
     r"All (?P<fin>\d+) jobs finished the timing step, in (?P<tlo>[\d.]+) to (?P<thi>[\d.]+) minutes "
     r"\((?P<tl>[\d.]+) minutes on average in the (?P<miss2>\d+) lost jobs, (?P<tr>[\d.]+) in the (?P<ret2>\d+) that returned\)\. "
     r"The (?P<miss3>\d+) were cancelled at the workflow's (?P<lim>\d+)-minute job limit during the next step, which ran the whole-repository check "
     r"\(`scripts/check\.py`\) before the upload: (?P<inp>\d+) were still in that step and (?P<failed>\d+) had it recorded as failed, "
     r"after (?P<flo>[\d.]+) to (?P<fhi>[\d.]+) minutes\. In the (?P<ret3>\d+) that returned, that step took (?P<rlo>[\d.]+) to (?P<rhi>[\d.]+) minutes, "
     r"except in the one EPYC 7763 job, which took (?P<r7>[\d.]+)\. (?P<canc>\d+) of the (?P<ret4>\d+) are also marked cancelled on the run pages: "
     r".*?The limit is (?P<now>\d+) minutes now, the upload comes first and the job checks only its own file\. "
     r"The cut fell unevenly by CPU model: the (?P<ret5>\d+) returned jobs are EPYC 9V74 (?P<a>\d+), EPYC 9V45 (?P<b>\d+), Xeon 6973P-C (?P<c>\d+), "
     r"Xeon 8573C (?P<d>\d+) and EPYC 7763 (?P<e>\d+), against (?P<f>\d+) of the first (?P<g>\d+) jobs on EPYC 7763\. "
     r".*?Pooled with the original (?P<o>\d+) jobs into the (?P<n75>\d+)-job pool \(`results/s6-pooled/`\), no lost-loop cell on an AMD model "
     r"moved by more than (?P<mv>[\d.]+) \(the lowest and highest cells are (?P<lo>[\d.]+) and (?P<hi>[\d.]+) against (?P<olo>[\d.]+) and "
     r"(?P<ohi>[\d.]+) in the original pool; EPYC 7763 gained (?P<g7763>\w+) jobs?, so for it this comparison says almost nothing\); "
     r"the Xeon 8573C went from (?P<w>\d+) job to (?P<x>\d+), and the Xeon 6973P-C, absent "
     r"before, had (?P<y>\d+)\."),
    ("details: the two newest runs",
     "tests/data/s7_job_steps.json; results/s7-run-*/; .github/workflows/measure.yml; results/s7-pooled, s6-pooled and s4-pooled; tests/data/s6_job_steps.json for the ten earlier runs",
     exp_details_newest_runs,
     r"\*\*The two newest runs \(`results/s7-run-\*/`\)\.\*\* (?P<two>\w+) further runs of the same workflow were dispatched on (?P<day>[A-Z][a-z]{2} \d+) "
     r"with the job limit raised to (?P<now>\d+) minutes, to check that jobs return after the change; they were not chosen on their results\. "
     r"All (?P<disp>\d+) jobs dispatched returned results \(step records in `tests/data/s7_job_steps\.json`, same format as for the ten runs\): "
     r"EPYC 7763 (?P<e7763>\d+), EPYC 9V74 (?P<e9v74>\d+), EPYC 9V45 (?P<e9v45>\d+), Xeon 6973P-C (?P<c>\d+), Xeon 8573C (?P<d>\d+) and Xeon 8370C (?P<t>\d+)\. "
     r"The timing step took (?P<tlo>[\d.]+) to (?P<thi>[\d.]+) minutes \((?P<ptlo>[\d.]+) to (?P<pthi>[\d.]+) in the ten earlier runs\) and the whole-repository check, "
     r"which still ran before the upload in those runs \(the workflow has since been changed to upload first\), (?P<clo>[\d.]+) to (?P<chi>[\d.]+) minutes "
     r"\((?P<pclo>[\d.]+) to (?P<pchi>[\d.]+) in the jobs of the ten earlier runs that returned\)\. "
     r"The two steps together took (?P<totlo>[\d.]+) to (?P<tothi>[\d.]+) minutes, setup not counted, so every job ran past the old (?P<old>\d+)-minute limit and returned, "
     r"and the slowest left (?P<margin>[\d.]+) minutes of the (?P<limit>\d+)\. .*?"
     r"With these (?P<ret>\d+) jobs added \((?P<n95>\d+) jobs\) the lowest and highest lost-loop cells are (?P<lo>[\d.]+) and (?P<hi>[\d.]+), "
     r"and no lost-loop cell on an AMD model is more than (?P<mv>[\d.]+) from its value in the original pool \(the largest move is (?P<shift>[\d.]+)\)\. "
     r"The runs changed one verdict, the Xeon 6973P-C's, from INCONCLUSIVE to MAP \(above\); the verdicts of the three AMD models and of the Xeon 8573C did not change\."),
    ("details: holdout, later jobs", "results/s7-pooled/pooled.json and results/s4-pooled/pooled.json job counts", exp_details_holdout_later,
     r"\(the (?P<n>\d+) later jobs came after the holdout and are not part of it\)"),
    ("details: independence of repetitions", "robustness/results.json s4 to s7", exp_details_robustness,
     r"on the original 30-job pool, the holdout, the (?P<n6>\d+)-job pool and the (?P<n7>\d+)-job pool: lag-1 autocorrelation of the per-repetition log ratio "
     r"has a median of (?P<lo>-?[\d.]+) to \+(?P<hi>[\d.]+), and the median block-bootstrap interval is 0\.75 to 1\.00 times the harness's width\. "
     r"On the (?P<n7b>\d+)-job pool a block bootstrap over ABBA quartets changes no lost-loop classification, no placement flag and no verdict form "
     r"on any of the (?P<five>\w+) models; EPYC 7763, 9V74 and 9V45 are MAP under all (?P<eight>\w+) interval methods tried "
     r"\(on the original 30-job pool EPYC 9V45 was inconclusive under (?P<three>\w+)\) and the Xeon 8573C is INCONCLUSIVE under all (?P<eight2>\w+)\. "
     r"The Xeon 6973P-C is MAP under (?P<k>\w+) of the (?P<eight3>\w+) and INCONCLUSIVE only under the first form of the lag-1 correction, "
     r"whose widths the report calls an artefact; its decisive cell \(stencil at L2\) has an upper end of (?P<pooled>[\d.]+) as pooled "
     r"and (?P<blk>[\d.]+) under the block bootstrap, against the (?P<lim>[\d.]+) limit\."),
    ("details: EPYC 9V45 borderline call", "results/s7-pooled/pooled.json and results/s4-pooled/pooled.json EPYC 9V45 k03_stencil.L1",
     exp_details_9v45_call,
     r"In the (?P<pj>\d+)-job pool the verdict leaves out `k02_add_fwd\.L1`, `k02_add_fwd\.L2` and `k03_stencil\.L1` as placement-sensitive "
     r"\(`k02_add_fwd\.L2` joined the set with the jobs added after the original pool, and the set did not change with the last (?P<last>\d+)\)\. "
     r"For `k03_stencil\.L1` the interval of the placement statistic ends at (?P<a>[\d.]+), under 1 \((?P<b>[\d.]+) in the original (?P<n>\d+)-job pool\)\. "
     r"Counted as a judged forward cell, its aligned interval would reach (?P<c>[\d.]+), above the (?P<lim>[\d.]+) limit by (?P<d>[\d.]+) "
     r"\((?P<e>[\d.]+) in the original pool\)"),
    ("details: reproduction across runs", "results/s7-pooled/pooled.json reproduction", exp_details_reproduction,
     r"outside another run's interval (?P<a>\d+) times out of (?P<b>\d+) on EPYC 7763 \((?P<ap>\d+)%, largest gap (?P<c>[\d.]+)%\) and (?P<d>\d+) times out "
     r"of (?P<e>\d+) on EPYC 9V74 \((?P<dp>\d+)%, largest gap (?P<f>[\d.]+)%\); .*?"
     r"In the (?P<n6>\d+)-job pool the counts were (?P<a6>\d+) of (?P<b6>\d+) \((?P<ap6>\d+)%, largest gap (?P<c6>[\d.]+)%\) and "
     r"(?P<d6>\d+) of (?P<e6>\d+) \((?P<dp6>\d+)%, largest gap (?P<f6>[\d.]+)%\): the share outside rose as runs were added"),
    ("details: kernel A/A floor on EPYC 7763", "results/s7-pooled/pooled.json EPYC 7763 aa", exp_details_aa,
     r"pooled over (?P<j>\d+) jobs, the kernel A/A floor on EPYC 7763 is about (?P<a>[\d.]+)% \((?P<b>[\d.]+)%\)"),
    ("details: stage S6", "results/s6-run-*/; .github/workflows/measure.yml", exp_details_stage_s6,
     r"\| S6 \| More jobs: ten further runs of `measure.yml`, (?P<disp>\d+) jobs dispatched, (?P<ret>\d+) returned results, the other "
     r"(?P<miss>\d+) cancelled at the (?P<lim>\d+)-minute job limit .*?pooled with the (?P<o>\d+) S4 jobs into the (?P<n75>\d+)-job kernel pool "
     r"\(in it the Xeon 6973P-C, (?P<j6>\d+) jobs, was INCONCLUSIVE\)"),
    ("details: stage S7", "results/s7-run-*/; .github/workflows/measure.yml; results/s7-pooled/pooled.json", exp_details_stage_s7,
     r"\| S7 \| More jobs: two further runs of `measure\.yml`, (?P<disp>\d+) jobs dispatched, (?P<ret>\d+) returned results \(job limit (?P<lim>\d+) minutes; "
     r"dispatched to check that jobs return after the limit was raised, not chosen on results\); `harness/criteria-v3\.json` unchanged; "
     r"pooled with the (?P<n75>\d+) jobs into the (?P<n95>\d+)-job kernel pool, in which the Xeon 6973P-C \((?P<j7>\d+) jobs\) is MAP, borderline "
     r"\| `results/s7-run-\*/` \((?P<two>\d+) runs\)"),
    ("details: reverse and stride-2 study", "investigate/vectorizer/reverse-stride2/ extracted/ and raw/", exp_details_reverse_stride2,
     r"reverse-stride2/README\.md\), (?P<ans>\d+) saved answers\)\. Observed: .*?over (?P<n>\d+) loops compiled with FAST on clang 18\.1\.0, "
     r".*?\((?P<yes>\d+) of (?P<yes2>\d+) loops with a count for every exit vectorized, none of the (?P<no>\d+) with an uncounted exit\); "
     r".*?vectorized exactly the (?P<hv>\d+) of (?P<hn>\d+) functions whose exit got a count"),
    ("details: matrix multiply study", "investigate/vectorizer/matmul/ raw/, derived/cost-table.md, requests.tsv", exp_details_matmul,
     r"matmul/README\.md\), (?P<req>\d+) compile requests, all answered and saved\)\. Observed on clang 18\.1\.0 at baseline x86-64 \(SSE2\): "
     r"legality passes, and the cost model prices each of the two bounds-check compares at (?P<c18>\d+) units at width 4 "
     r"\((?P<c42>\d+) on SSE4\.2, (?P<c3>\d+) on AVX2, where clang 18 vectorizes the loop\), so the width-4 loop sums to (?P<vec>\d+) against "
     r"(?P<sc>\d+) for four scalar iterations.*?Clang 19 to 21 find the two compares uniform and price them at (?P<c19>\d+) each"),
    ("details: layout sweep, the forward add at L1", "site/data/layout.json rows k02_add_fwd L1 (min, max, aligned, median, n_pass)",
     exp_details_layout,
     r"The forward add is MIXED on 7763 and 9V74: (?P<lo7>[\d.]+) to (?P<hi7>[\d.]+) on 7763 and (?P<lo74>[\d.]+) to (?P<hi74>[\d.]+) on 9V74 at L1, "
     r"where the as-compiled placement is the slow one and the aligned build is (?P<a7>[\d.]+) and (?P<a74>[\d.]+); "
     r"on 9V45 it is ROBUST at L1 \(median (?P<m45>[\d.]+), (?P<p45>\d+) of (?P<n45>\d+) placements pass\)"),
    ("details: links to the twelve later runs", "results/s6-run-*/*/results.json and results/s7-run-*/*/results.json run.workflow_run_url",
     exp_details_links,
     r"The links work for the records in `results/s6-run-\*/` and `results/s7-run-\*/` \((?P<twelve>\w+) runs\), .*? they link to runs of this repository, "
     r"whose run pages are public"),
    ("details: Compiler Explorer's clang 18.1.0 is a release candidate", "investigate/vectorizer/matmul/derived/revisions.txt; results/s4-run-*/ and s6-run-*/ toolchain",
     exp_rc_and_same_remark,
     r"its clang (?P<ce>[\d.]+) is a release-candidate build, not the Ubuntu (?P<timed>[\d.]+) that was timed"),
    ("details: the timed build gave the same remark", "dayone/results/run-38116223923/remarks.*.fast.txt; results/s4-run-*/ toolchain",
     exp_details_same_remark,
     r"The timed Ubuntu (?P<timed>[\d.]+) printed the same \"could not determine number of loop iterations\" remark for both loops"),
    ("details: trunk date, reverse and stride-2 study", "investigate/vectorizer/reverse-stride2/extracted/trunk-versions.txt",
     exp_details_trunk_vectorizer,
     r"clang 20, 21 and trunk \(as served on (?P<d>[\d-]+)\) print early-exit wording"),
    ("details: trunk date, compile-only sweep", "ce-sweep/cache/clang_trunk__x86-64__*.json.gz fetched_at",
     exp_details_trunk_sweep,
     r"and lost again on clang 23\.1 and trunk \(as served on (?P<d>[\d-]+); clang 22, 23\.1 and trunk were not timed\)"),
    ("details: trunk revision, matrix multiply study", "investigate/vectorizer/matmul/derived/revisions.txt pipe_ctrunk_fast",
     exp_details_trunk_revision,
     r"clang 23\.1 and trunk \(revision `(?P<sha>[0-9a-f]{10})`\) reject the loop again"),
    ("details: the LLVM commit and the tags", "investigate/vectorizer/matmul/llvm-src/commit_b6a8f5486b.json and commit_in_tag.json",
     exp_details_commit,
     r"LLVM commit `(?P<sha>[0-9a-f]{10})` .*? is in `llvmorg-(?P<in>[\d.]+)` and not in `llvmorg-(?P<n1>[\d.]+)`, `(?P<n2>[\d.]+)` or `(?P<n3>[\d.]+)`"),
    ("details: the matrix multiply that is lost is the x86-64 one", "results/s4-run-*/ toolchain",
     exp_x86_clang_major, r"\(under clang (?P<c>\d+) on x86-64\) matrix multiply"),
    ("details: the runner labels", ".github/workflows/measure.yml runner input; results/s8-arm-pooled/pooled.json cpu_model", exp_details_runners,
     r"`measure\.yml` takes one `runner` label per run, `(?P<x>ubuntu-[\d.]+)` \(x86-64, the default\) or `(?P<a>ubuntu-[\d.]+-arm)` \(AArch64, (?P<model>[\w-]+)\)"),
    ("details: the trap instructions", "per-job listings of results/s8-arm-run-*/", exp_arm_trap_form,
     r"\(`ud2` on x86-64, `(?P<t>brk #0x1)` on AArch64\)"),
    ("details: the Arm jobs beside the 95", "results/s8-arm-pooled/pooled.json jobs; results/s7-pooled/pooled.json jobs",
     exp_details_arm_intro,
     r"A further (?P<n>\d+) jobs on GitHub's arm64 runner \(one core type\) are pooled apart from these (?P<m>\d+) and reported in their own column below"),
    ("details: Arm, runs and toolchain", "results/s8-arm-pooled/pooled.json; per-job toolchain in results/s8-arm-run-*/",
     exp_details_arm_runs,
     r"\*\*Arm \((?P<model>[\w-]+)\), a separate column\*\* \(\[arm64/README\.md\]\(\.\./arm64/README\.md\); `results/s8-arm-run-\*/`, "
     r"pooled in `results/s8-arm-pooled/pooled\.json`\)\. (?P<three>\w+) full runs of `measure\.yml` on GitHub's `ubuntu-24\.04-arm` runner, "
     r"(?P<jobs>\d+) jobs on one core type, with the same clang (?P<clang>[\d.]+) and libc\+\+ (?P<lib>\d+), flags, harness and rules"),
    ("details: Arm, reverse and stride-2", "results/s8-arm-pooled/pooled.json cells; per-job listings",
     exp_details_arm_reverse,
     r"In cache, as compiled: reverse (?P<r1>[\d.]+)x and stride-2 (?P<s1>[\d.]+)x at L1 \((?P<r2>[\d.]+)x and (?P<s2>[\d.]+)x at L2\)\. "
     r"Both lose their NEON loops under FAST \((?P<a>\d+) and (?P<b>\d+) NEON instructions with the checks off, none with them on\)"),
    ("details: Arm, matrix multiply", "results/s8-arm-pooled/pooled.json cells; per-job listings",
     exp_details_arm_matmul,
     r"and still costs (?P<m1>[\d.]+)x at L1 and (?P<m2>[\d.]+)x at L2 \(Cachegrind counts (?P<i1>[\d.]+)x and (?P<i2>[\d.]+)x the instructions\): "
     r"the FAST listing has (?P<fl>\d+) lines against (?P<nl>\d+), and the extra lines lie outside the NEON loop, "
     r"which is the same (?P<nine>\w+) instructions in both builds"),
    ("details: Arm, matrix multiply, time against instructions", "results/s8-arm-pooled/pooled.json cells (time ratio and Cachegrind instruction ratio, as compiled)",
     exp_details_arm_time_vs_instr,
     r"the time ratio falls from (?P<t1>[\d.]+)x to (?P<t2>[\d.]+)x while the instruction ratio falls from (?P<i1>[\d.]+)x to (?P<i2>[\d.]+)x, "
     r"so in log terms the time ratio is (?P<l1>[\d.]+) of the instruction ratio at L1 and (?P<l2>[\d.]+) at L2"),
    ("details: Arm, forward loops, gather and histogram", "results/s8-arm-pooled/pooled.json cells and aa; site/data/arm64.json forward_instr; noise",
     exp_details_arm_forward,
     r"Forward loops bounded by `size\(\)` keep their NEON loops and cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x at L1, against a pooled A/A half-width of (?P<aa>[\d.]+)% "
     r"\(that of one L1 cell, the add's; the add's (?P<pct>[\d.]+)% is (?P<n>\d+) extra instructions in each call, the same at L2, "
     r"and the add and the stencil at L1 are placement-sensitive and not judged\); "
     r"gather and histogram, never vectorized, pay (?P<g>[\d.]+)x and (?P<h>[\d.]+)x at L1"),
    ("details: Arm, the margin against the bootstrap's seeds", "arm64/seed-sensitivity.json; site/data/arm64.json noise (L2 A/A)",
     exp_details_arm_seeds,
     r"re-drawn under (?P<n>\d+) other seeds \(`arm64/seed-sensitivity\.json`, a sensitivity reading beside the stored verdict, which is unchanged\) "
     r"the interval ends at or above (?P<lim>[\d.]+) in (?P<k>\d+) and the whole verdict is MAP in (?P<m>\d+), "
     r"and an identical binary timed against itself at that L2 cell has a half-width of (?P<aa>[\d.]+)%"),
    ("details: Arm, the verdict", "results/s8-arm-pooled/pooled.json verdict, per_run, reproduction",
     exp_details_arm_verdict,
     r"the forward add at L2, aligned, has an interval of (?P<lo>[\d.]+) to (?P<hi>[\d.]+), over the (?P<lim>[\d.]+) limit by (?P<over>[\d.]+), "
     r"in a cell whose spread between jobs is (?P<sd>[\d.]+)%\. Each of the (?P<three>\w+) runs alone is INCONCLUSIVE too, and (?P<out>\d+) of (?P<chk>\d+) "
     r"comparisons of one run's point against another run's interval fall outside \((?P<eight>\d+) of them stride-2 at L2; largest gap (?P<gap>[\d.]+)%\)"),
    ("details: Arm, the compile-only sweep said so", "site/data/cesweep.json aarch64 rows; results/s8-arm-pooled/pooled.json classes",
     exp_arm_cesweep_only,
     r"as the compile-only sweep said it would on AArch64"),
    ("details: Arm, the placement-sensitive cells", "results/s8-arm-pooled/pooled.json verdict.placement_sensitive",
     exp_details_arm_sensitive,
     r"Matrix multiply at both sizes and the add and the stencil at L1 are placement-sensitive under the written rule and not judged"),
    ("details: Arm, links to the runs", "results/s8-arm-run-*/*/results.json run.workflow_run_url",
     exp_details_arm_links,
     r"`results/s8-arm-run-\*/` \((?P<three>\w+)\), `results/s9-arm-run-\*/` and `results/s9-run-\*/` \(\w+\), `results/s10-dsweep-run-\*/` \(\w+\) "
     r"and `results/s11-forwardt-run-\*/` \(\w+\): they link to runs of this repository"),
    ("details: Arm, the one other architecture", "results/s8-arm-run-*/*/results.json toolchain; results/s8-arm-pooled/pooled.json",
     exp_details_arm_other_arch,
     r"The Arm column \(above\) is the one other architecture, and only with clang (?P<c>[\d.]+) on one core type \((?P<model>[\w-]+)\)"),
    ("details: Arm, limits", "results/s8-arm-pooled/pooled.json; results/s8-arm-run-*/ start times; .github/workflows/measure.yml",
     exp_details_arm_limits,
     r"\*\*The Arm column's own limits \(`arm64/`, runs (?P<a>\d+), (?P<b>\d+) and (?P<c>\d+)\)\.\*\* All (?P<n>\d+) jobs dispatched returned results "
     r"\((?P<runs>\d+) runs of (?P<per>\d+), job limit (?P<lim>\d+) minutes\) and none was dropped, .*?"
     r"but they came from (?P<o1>\w+) core type in (?P<o2>\w+) runner image, drawn without choice, and the (?P<three>\w+) runs were launched together "
     r"\(every job started within (?P<m>\d+) minutes of the others\), .*? It is clang (?P<clang>[\d.]+) with libc\+\+ (?P<lib>\d+) only, .*? "
     r"The placement fields \((?P<w>\d+)-byte windows\) were defined for x86 fetch windows, and the layout A/A \(which moves only the unchecked build's loops\) "
     r"did not see the placement shifts of the FAST/NONE ratio that the compiled-over-aligned ratio showed "
     r"\((?P<st>[\d.]+)% for the stencil and (?P<ga>[\d.]+)% for gather at L1\)\. "
     r"The L2 forward cells are noisy \(spread between jobs up to (?P<sd>[\d.]+)% for the add\), an identical binary is as noisy at the add's L2 cell "
     r"\(A/A half-width (?P<aa>[\d.]+)%\), and the INCONCLUSIVE form rests on (?P<cell>\w+) of them"),
    ("details: the follow-up list, arm64", "results/s8-arm-pooled/pooled.json",
     exp_details_arm_followup,
     r"`arm64/`: the same (?P<k>\d+) kernels timed on GitHub's arm64 runner \((?P<model>[\w-]+)\), (?P<n>\d+) full runs pooled apart"),
    ("details: stage S8", "results/s8-arm-run-*/; results/s8-arm-pooled/pooled.json; .github/workflows/measure.yml",
     exp_details_arm_stage,
     r"\| S8 \| The Arm column: (?P<three>\w+) further full runs of `measure\.yml` with `runner=ubuntu-24\.04-arm`, (?P<disp>\d+) jobs dispatched, "
     r"(?P<ret>\d+) returned results \(job limit (?P<lim>\d+) minutes\), all on (?P<model>[\w-]+); `harness/criteria-v3\.json` unchanged; "
     r"pooled apart from the x86-64 jobs into the (?P<pool>\d+)-job Arm pool, whose form is INCONCLUSIVE under the written rules; "
     r"its plan was written before the full results, in the author's unpublished development history \| `arm64/`, `results/s8-arm-run-\*/` \((?P<runs>\d+) runs\)"),
]

# ---- the same for siblings/README.md ------------------------------------------------------------------

def exp_siblings_intel():
    a, b = cell_of(cpu_like("6973P-C"), "k02_add_fwd.L1")["aligned"], cell_of(cpu_like("8573C"), "k02_add_fwd.L1")["aligned"]
    assert cpu_like("6973P-C")["jobs"] == cpu_like("8573C")["jobs"], "the siblings note says '7 jobs each' for the two Xeon models"
    return {"pool": str(pooled_jobs()), "j": str(cpu_like("8573C")["jobs"]),
            "alo": f2(min(a["per_job"])), "ahi": f2(max(a["per_job"])), "blo": f2(min(b["per_job"])), "bhi": f2(max(b["per_job"]))}


SIBLINGS_ROWS = [
    ("siblings: the Intel forward add in the main pool", "results/s7-pooled/pooled.json Xeon k02_add_fwd.L1 aligned per_job", exp_siblings_intel,
     r"the main (?P<pool>\d+)-job pool has since drawn it and the 8573C, (?P<j>\d+) jobs each, with the same forward add at "
     r"(?P<alo>[\d.]+)x to (?P<ahi>[\d.]+)x and (?P<blo>[\d.]+)x to (?P<bhi>[\d.]+)x aligned"),
    ("siblings: the main setup", "results/s4-run-*/, s6-run-*/ and s7-run-*/ toolchain", exp_siblings_setup,
     r"Ubuntu clang (?P<c>[\d.]+), libc\+\+ (?P<l>\d+) in FAST mode"),
    ("siblings: the Arm column's compiler", "results/s8-arm-run-*/*/results.json toolchain; results/s8-arm-pooled/pooled.json", exp_siblings_arm,
     r"the main kernels were timed on one Arm core type, (?P<model>[\w-]+), with clang (?P<c>\d+) only, in `arm64/`"),
]

# ---- the same for ce-sweep/README.md ------------------------------------------------------------------

CESWEEP_ROWS = [
    ("ce-sweep: what the timed builds cover", "results/s4-run-*/ and results/s8-arm-run-*/ toolchain; site/data/cesweep.json aarch64 rows",
     exp_cesweep_arm,
     # the sentence wraps over several lines in the file: every space of the anchor matches any run of white space
     (r"measured only for clang (?P<c>\d+) \(and the `siblings/` and `versions/` toolchains, all on x86-64\) in the main study, and for the Ubuntu "
      r"clang (?P<t>[\d.]+) build on one Arm core type, (?P<model>[\w-]+), in `arm64/`\. There the timed builds agree with this sweep's "
      r"AArch64 rows for clang (?P<v>[\d.]+): reverse and stride-2 are lost and matrix multiply is kept").replace(" ", r"\s+")),
]

# ---- the same for arm64/README.md ----------------------------------------------------------------------

ARM64_ROWS = [
    ("arm64: title", "arm kernels in results/s8-arm-pooled/pooled.json", exp_arm_title,
     r"# Arm column: the same (?P<k>\w+) loops on an AArch64 runner"),
    ("arm64: status date", "results/s8-arm-run-*/*/results.json run.started_at", exp_arm_status_date,
     r"Status: work in progress \((?P<m>[A-Z][a-z]{2}) (?P<y>\d{4})\)"),
    ("arm64: status line", "results/s8-arm-pooled/pooled.json jobs", exp_arm_pooled_over,
     r"One core type, one compiler and (?P<n>\d+) jobs make this a first reading"),
    ("arm64: question, the x86-64 range", "site/data/index.json page.lost", exp_lost_range,
     r"pay (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x in cache, and that forward loops bounded by `size\(\)` pay little on the AMD models"),
    ("arm64: short answer, runs and machine", "results/s8-arm-pooled/pooled.json", exp_arm_counts_digits,
     r"`ubuntu-24\.04-arm` runner, (?P<jobs>\d+) jobs in (?P<runs>\d+) runs, every job on a (?P<model>[\w-]+) core"),
    ("arm64: short answer, reverse and stride-2", "results/s8-arm-pooled/pooled.json cells; per-job listings", exp_arm_short_reverse,
     r"\*\*Reverse and stride-2 lose their NEON loops under FAST and pay\.\*\* (?P<r1>[\d.]+)x and (?P<s1>[\d.]+)x at L1, "
     r"(?P<r2>[\d.]+)x and (?P<s2>[\d.]+)x at L2 \(as compiled\)\. Their functions go from (?P<rn>\d+) and (?P<sn>\d+) NEON instructions to none.*?"
     r"the remark the x86-64 builds print for the same (?P<two>\w+) loops"),
    ("arm64: short answer, matrix multiply", "results/s8-arm-pooled/pooled.json cells; site/data/versions.json and index.json for the x86-64 range",
     exp_arm_short_matmul,
     r"said it would be on AArch64 for clang (?P<ca>\d+)\. FAST costs (?P<m1>[\d.]+)x at L1 and (?P<m2>[\d.]+)x at L2\. "
     r"On x86-64 the same loop is lost under clang (?P<cx>\d+) and costs (?P<xlo>[\d.]+)x to (?P<xhi>[\d.]+)x\."),
    ("arm64: short answer, forward loops", "results/s8-arm-pooled/pooled.json cells and aa", exp_arm_short_forward,
     r"\*\*Forward loops bounded by `size\(\)` keep NEON and cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x at L1\*\* \(as compiled\), against a pooled A/A floor of (?P<aa>[\d.]+)%"),
    ("arm64: short answer, the forward add", "results/s8-arm-pooled/pooled.json cells; site/data/arm64.json forward_instr and noise (L2 A/A)", exp_arm_short_add,
     r"the add's (?P<pct>[\d.]+)% is (?P<n>\d+) extra instructions in each call, a count that is the same at L2\. "
     r"At L2 the forward cells are noisy, and so is an identical binary timed against itself there \(A/A half-width (?P<aa>[\d.]+)%\)"),
    ("arm64: short answer, gather and histogram", "results/s8-arm-pooled/pooled.json cells", exp_arm_short_gather,
     r"pay for the check itself: (?P<g>[\d.]+)x and (?P<h>[\d.]+)x at L1\."),
    ("arm64: short answer, the verdict", "results/s8-arm-pooled/pooled.json verdict and cells", exp_arm_short_verdict,
     r"One forward cell misses the rule: the forward add at L2, aligned, has an interval that ends at (?P<hi>[\d.]+), against a limit of (?P<lim>[\d.]+)\."),
    ("arm64: short answer, the margin", "arm64/seed-sensitivity.json deciding_cell and derived; results/s8-arm-pooled/pooled.json", exp_arm_short_margin,
     r"The margin, (?P<over>[\d.]+), is inside the bootstrap's own seed noise: the same data under (?P<n>\d+) other seeds gives an end at or above (?P<lim>[\d.]+) "
     r"in (?P<k>\d+), and a whole verdict of MAP in (?P<m>\d+)\."),
    ("arm64: setup, the machine", "results/s8-arm-run-*/*/results.json run.runner; details.json lscpu; per-job listings", exp_arm_runner,
     r"`lscpu` reports `[\w-]+`, (?P<cpus>\d+) vCPUs with one thread each, (?P<l1>\d+) KiB of L1d and (?P<l2>\d+) KiB of L2 per core "
     r"and a (?P<l3>\d+) KiB L3; (?P<os>Ubuntu [\d.]+ LTS), kernel (?P<kernel>[\w.-]+)\."),
    ("arm64: setup, the toolchain", "results/s8-arm-run-*/*/results.json run.toolchain and flags; details.json build commands", exp_arm_toolchain,
     r"Ubuntu clang version (?P<clang>[\d.]+ \(1ubuntu1\)) and libc\+\+-(?P<lm>\d+)-dev (?P<lib>[\d:.]+-1ubuntu1) from apt, `(?P<common>[^`]+)`; "
     r".*?the aligned pair \(`(?P<align>[^`]+)`\)"),
    ("arm64: setup, loops and sizes", "results/s8-arm-run-*/*/details.json size_targets_bytes, cache_bytes, cells", exp_arm_sizes,
     r"The same (?P<k>\w+) kernels \(`kernels/`\)\. Working sets of (?P<l1>\d+) KiB \(L1\) and (?P<l2>\d+) KiB \(L2\), half of the per-core caches; "
     r"matrix multiply uses d = (?P<d1>\d+) and d = (?P<d2>\d+)\. There are no RAM cells"),
    ("arm64: setup, the sizes beside the x86-64 ones", "results/s7-run-*/results-amd-epyc-7763-*/details.json size_targets_bytes and cells", exp_arm_setup_x86_sizes,
     r"On EPYC 7763 the same rule gives working sets of (?P<l1>\d+) KiB and (?P<l2>\d+) KiB and d = (?P<d1>\d+) and d = (?P<d2>\d+), "
     r"so an \"L1\" or \"L2\" cell here and one in the x86-64 column share the name of a cache level"),
    ("arm64: setup, repetitions", "results/s8-arm-run-*/*/details.json reps_per_side", exp_arm_timing,
     r"\*\*Timing\.\*\* (?P<reps>\d+) repetitions per side in ABBA order, pinned to (?P<one>\w+) vCPU"),
    ("arm64: the aligned flag", "results/s8-arm-run-*/*/results.json run.flags.align", exp_arm_align_flag,
     r"the aligned build \(`(?P<a>-falign-loops=\d+)`\) in parentheses.*?\(NONE against NONE built with `(?P<b>-falign-loops=\d+)`\)"),
    ("arm64: setup, the runs", "results/s8-arm-pooled/pooled.json runs and inputs; results/s8-arm-run-*/*/results.json run.started_at; .github/workflows/measure.yml",
     exp_arm_runs,
     r"(?P<three>\w+) runs of `measure\.yml` with `runner=ubuntu-24\.04-arm` \((?P<a>\d+), (?P<b>\d+) and (?P<c>\d+)\), (?P<per>\d+) jobs each, "
     r"dispatched together\. All (?P<n>\d+) jobs returned results and all (?P<n2>\d+) are pooled; none was dropped\. "
     r"The harness started between (?P<t1>[\d:]+) and (?P<t2>[\d:]+) UTC on (?P<day>Oct \d+)\. All (?P<n3>\d+) are the same CPU model"),
    ("arm64: setup, one entry in the pool", "results/s8-arm-pooled/pooled.json cpus", exp_arm_pool_entries,
     r"so the pool \(`results/s8-arm-pooled/pooled\.json`\) has (?P<one>\w+) entry"),
    ("arm64: setup, the runner label in the three places it appears", ".github/workflows/measure.yml runner input", exp_arm_labels,
     r"\*\*Runner\.\*\* `(?P<a>ubuntu-[\d.]+-arm)` \(GitHub-hosted\)\..*?The `(?P<b>ubuntu-[\d.]+-arm)` label could map to other core types later.*?"
     r"gh workflow run measure\.yml -R <you>/third-of-a-percent -f runner=(?P<c>ubuntu-[\d.]+-arm)"),
    ("arm64: setup, the trap instruction", "harness/asm.py; per-job listings", exp_arm_trap_form,
     r"`(?P<t>brk #0x1)` is a trap"),
    ("arm64: setup, the fetch window", "harness/placement.py", exp_arm_window,
     r"The (?P<w1>\d+)-byte-window placement fields .*? whether (?P<w2>\d+) bytes is the right unit on this core was not examined.*?"
     r"against (?P<w3>\d+)-byte windows\. .*?\*\*Placement fields were defined for x86 fetch windows\*\* \((?P<w4>\d+)-byte windows\)"),
    ("arm64: setup, the change to normalize()", "harness/asm.py normalize(); site/data/arm64.json stored_diffs", exp_arm_normalize,
     r"`normalize\(\)` in `harness/asm\.py` was changed to strip branch targets of (?P<new>\w+) or more hex digits \(it stripped (?P<old>\w+) or more, "
     r"which left AArch64's (?P<dig>\w+)-digit targets in the diffs\).*?"
     r"\(for the forward add at L1: (?P<a>\d+) added and (?P<r>\d+) removed lines as stored, (?P<a2>\d+) and (?P<r2>\d+) after the change\)"),
    ("arm64: setup, the rules", "harness/criteria-v3.json v3.pooling.minimum_jobs", exp_arm_min_jobs,
     r"and at least (?P<min>\d+) jobs for a verdict"),
    ("arm64: the level of the intervals", "harness/criteria-v3.json; results/s8-arm-pooled/pooled.json ci95", exp_arm_interval_level,
     r"The (?P<p>\d+)% intervals \(a bootstrap over jobs and repetitions\)"),
    ("arm64: Google's average, forward loops", "site/data/index.json claim.google_pct", exp_google_pct,
     r"neither confirm nor contradict Google's (?P<v>[\d.]+)%"),
    ("arm64: Google's average, limits", "site/data/index.json claim.google_pct", exp_google_pct,
     r"\*\*Nothing about Google's services\*\* or its (?P<v>[\d.]+)% average"),
    ("arm64: the forward rule, at L2", "results/s8-arm-pooled/pooled.json verdict.forward_limit_pct", exp_arm_forward_rule_percent,
     r"too noisy on this core for the (?P<p>\d+)% forward rule to settle"),
    ("arm64: stable across the runs", "results/s8-arm-pooled/pooled.json per_run", exp_arm_stable_runs,
     r"The form is stable across the (?P<three>\w+) runs in the sense that each is INCONCLUSIVE"),
    ("arm64: pooled over", "results/s8-arm-pooled/pooled.json jobs", exp_arm_pooled_over,
     r"Pooled over the (?P<n>\d+) jobs\."),
] + [
    (f"arm64: table row, {label}", "results/s8-arm-pooled/pooled.json cells; per-job listings", exp_arm_table_row(kernel), arm_table_pattern(label))
    for kernel, label in ARM_KERNELS.items()
] + [
    ("arm64: table notes, widest intervals and spreads", "results/s8-arm-pooled/pooled.json cells ci95 and between_job_sd_pct", exp_arm_intervals,
     r"The widest at L1 is (?P<w1>[\d.]+)% either side of its ratio \((?:the )?(?P<c1>[a-z0-9 -]+, (?:aligned|as compiled))\) and the widest at L2 is "
     r"(?P<w2>[\d.]+)% \((?:the )?(?P<c2>[a-z0-9 -]+, (?:aligned|as compiled))\)\. The spread between jobs \(the standard deviation of the log ratio\) "
     r"is largest at (?P<s1>[\d.]+)% at L1 \((?:the )?(?P<d1>[a-z0-9 -]+, (?:aligned|as compiled))\) and (?P<s2>[\d.]+)% at L2 "
     r"\((?:the )?(?P<d2>[a-z0-9 -]+, (?:aligned|as compiled))\)"),
    ("arm64: reverse and stride-2, remarks, instructions and the no-vectorize build", "results/s8-arm-pooled/pooled.json cells and positive; details.json remarks; per-job listings",
     exp_arm_rev_stride2_prose,
     r"vectorize both loops \(width (?P<w>\d+), interleaved count (?P<i>\d+)\)\. .*?the functions contain no NEON instruction and (?P<trap>\w+) `brk #0x1` each, .*?"
     r"Cachegrind counts (?P<ir>[\d.]+)x and (?P<is>[\d.]+)x the instructions at L1 \(instructions, not time\)\. "
     r"The no-vectorize build over NONE, at L1, costs (?P<nr>[\d.]+)x for reverse and (?P<ns>[\d.]+)x for stride-2, "
     r"so the checked scalar loops cost more than plain scalar loops do: (?P<r>[\d.]+)x against (?P<nr2>[\d.]+)x, and (?P<s>[\d.]+)x against (?P<ns2>[\d.]+)x\."),
    ("arm64: the sweep's AArch64 rows", "site/data/cesweep.json rows (clang 18.1.0, aarch64, -O2); results/s8-arm-pooled/pooled.json classes", exp_arm_cesweep,
     r"Compiler Explorer's clang (?P<v>[\d.]+) for AArch64\)"),
    ("arm64: matrix multiply, observed: the NEON loop and the line counts", "results/s8-arm-run-*/*/asm/k08_matmul.*.s; details.json loops", exp_arm_matmul_observed,
     r"\*\*Observed\.\*\* Both builds contain the same NEON loop: (?P<nine>\w+) instructions, the same opcodes, with (?P<two>\w+) `mla v\.4s` in it\. "
     r"The FAST listing has (?P<fl>\d+) lines against (?P<nl>\d+) \(function header included\), so its (?P<extra>\d+) extra lines lie outside that loop\."),
    ("arm64: matrix multiply, observed: selects and branches to the trap", "results/s8-arm-run-*/*/asm/k08_matmul.*.s; details.json loops", exp_arm_matmul_listing,
     r"The FAST listing has (?P<csel>\d+) `csel` instructions; the NONE listing has no `csel`, but (?P<cset>\w+) `cset` and (?P<csinc>\w+) `csinc`\. "
     r"(?P<three>\w+) conditional branches in the function lead to its single `brk #0x1` \(their targets are in the saved listing, for example "
     r"`(?P<path>results/[^`]+)`; the `\.diff` files normalise targets away\); none is inside the NEON loop, "
     r"and (?P<two>\w+) are inside the scalar remainder loop, so that loop runs (?P<two2>\w+) checks for every element it handles\."),
    ("arm64: matrix multiply, observed: time against instructions", "results/s8-arm-pooled/pooled.json cells (time ratio, Cachegrind instruction ratio)", exp_arm_matmul_time_vs_instr,
     r"Cachegrind counts (?P<i1>[\d.]+)x the instructions at L1 and (?P<i2>[\d.]+)x at L2 \(instructions, not time\), "
     r"and the time ratio is (?P<t1>[\d.]+)x at L1 and (?P<t2>[\d.]+)x at L2\. "
     r"In log terms the time ratio is (?P<l1>[\d.]+) of the instruction ratio at L1 and (?P<l2>[\d.]+) at L2: "
     r"at L2 a rise of (?P<rise>\d+)% in instructions comes with a rise of (?P<tr>[\d.]+)% in time\."),
    ("arm64: matrix multiply, inferred: the arithmetic", "results/s8-arm-pooled/pooled.json cells; site/data/arm64.json matmul_cost; harness remarks (width and interleave)", exp_arm_matmul_inferred,
     r"At d = (?P<d1>\d+) each inner call runs the NEON loop (?P<p1>\d+) times \((?P<e>\d+) elements per pass\) and the scalar loop for (?P<r1>\d+) elements; "
     r"at d = (?P<d2>\d+) it runs the NEON loop (?P<p2>\d+) times and the scalar loop for (?P<r2>\d+) element, .*?"
     r"the instruction ratio, which falls from (?P<i1>[\d.]+)x to (?P<i2>[\d.]+)x\."),
    ("arm64: matrix multiply, the check not run", "results/s8-arm-run-*/*/details.json cache_bytes; results/s8-arm-pooled/pooled.json cells", exp_arm_matmul_d_sweep,
     r"with d mod (?P<per>\d+) = (?P<rem>\d+) inside L1d \(d = (?P<inside>[\d, ]+?); three d x d int32 matrices fit in the (?P<kib>\d+) KiB of L1d up to d = (?P<max>\d+)\) "
     r"and beyond it \(d = (?P<beyond>[\d, ]+?)\), and at d mod (?P<per2>\d+) = 0 \(d = (?P<zero>[\d, ]+?), where no element is left for the scalar loop\)"),
    ("arm64: matrix multiply beside the x86-64 versions run", "site/data/versions.json summary.matmul_main", exp_arm_vs_x86_matmul,
     r"on x86-64 with clang and libc\+\+ (?P<a>\d+) to (?P<b>\d+), which also keep matrix multiply vectorized, the cost is (?P<l1>[\d.]+)x at L1 "
     r"and (?P<l2>[\d.]+)x at L2 on EPYC 7763"),
    ("arm64: matrix multiply beside the x86-64 versions run, sizes", "results/s7-run-*/results-amd-epyc-7763-*/details.json cells", exp_arm_setup_x86_d,
     r"other cache and matrix sizes \(d = (?P<d1>\d+) and d = (?P<d2>\d+) on EPYC 7763\)"),
    ("arm64: gather and histogram", "results/s8-arm-pooled/pooled.json cells", exp_arm_gather_hist,
     r"gather (?P<g>[\d.]+)x \(aligned (?P<ga>[\d.]+)x\) and histogram (?P<h>[\d.]+)x at L1, (?P<g2>[\d.]+)x and (?P<h2>[\d.]+)x at L2\. "
     r"Their instruction counts rise (?P<gi>[\d.]+)x and (?P<hi>[\d.]+)x\."),
    ("arm64: the A/A floor", "results/s8-arm-pooled/pooled.json aa; results/s8-arm-run-*/*/results.json controls.aa; arm64/PLAN.md", exp_arm_aa_floor,
     r"if the A/A half-width is below (?P<plan>[\d.]+)%, the forward loops would be reported against it as a description\. "
     r"The pooled A/A half-width is (?P<aa>[\d.]+)% \(per job, (?P<j1>[\d.]+)% to (?P<j2>[\d.]+)%\)"),
    ("arm64: forward loops at L1, in percent", "results/s8-arm-pooled/pooled.json cells", exp_arm_forward_bullets,
     r"the forward sum costs (?P<s1>-?[\d.]+)% as compiled \(ratio (?P<sr>[\d.]+), interval (?P<slo>[\d.]+) to (?P<shi>[\d.]+)\) and (?P<s2>-?[\d.]+)% aligned;.*?"
     r"the forward add costs (?P<a1>-?[\d.]+)% as compiled and (?P<a2>-?[\d.]+)% aligned;.*?"
     r"the stencil costs (?P<t1>-?[\d.]+)% as compiled and (?P<t2>-?[\d.]+)% aligned\."),
    ("arm64: forward loops, the add's instructions", "site/data/arm64.json forward_instr (Cachegrind counts per call, NONE and FAST)", exp_arm_add_instructions,
     r"Cachegrind counts (?P<n1>[\d,]+) instructions per call in NONE and (?P<f1>[\d,]+) in FAST at L1 \((?P<e1>[\d,]+) elements\), "
     r"(?P<c1>\d+) more as compiled \((?P<al>\d+) more aligned\), and (?P<n2>[\d,]+) and (?P<f2>[\d,]+) at L2 \((?P<e2>[\d,]+) elements\), "
     r"the same (?P<c2>\d+) more\. The cost is a constant per call, not a cost per element: (?P<p1>[\d.]+)% of the instructions of an L1 call "
     r"and (?P<p2>[\d.]+)% of an L2 call\."),
    ("arm64: forward loops, the stencil's instructions", "site/data/arm64.json forward_instr and layout_vs_placement; results/s8-arm-pooled/pooled.json cells",
     exp_arm_stencil_instructions,
     r"(?P<c>\d+) more instructions per call as compiled \((?P<al>\d+) aligned\), at both sizes\. "
     r"Its time ratio changes sign with loop alignment \(\+(?P<tc>[\d.]+)% as compiled, -(?P<ta>[\d.]+)% aligned\): "
     r"the yardstick for it is the compiled-over-aligned ratio, (?P<d>[\d.]+) \((?P<dp>[\d.]+)%\), not the A/A floor"),
    ("arm64: limits, the A/A floor is the floor of one cell", "results/s8-arm-pooled/pooled.json aa and cells", exp_arm_limits_floor,
     r"\*\*The A/A floor is the floor of one cell\*\*, the forward add at L1 \((?P<aa>[\d.]+)%\)\. "
     r"The widest interval at L1 is the stencil's, (?P<w1>[\d.]+)% either side of its ratio, and at L2 stride-2's, (?P<w2>[\d.]+)%\."),
    ("arm64: forward loops at L2", "results/s8-arm-pooled/pooled.json cells", exp_arm_forward_l2,
     r"At L2 the forward cells are (?P<alo>[\d.]+) to (?P<ahi>[\d.]+) as compiled \((?P<blo>[\d.]+) to (?P<bhi>[\d.]+) aligned\), "
     r"but with intervals reaching (?P<w>[\d.]+)% either side of the ratio and a spread between jobs of up to (?P<s>[\d.]+)%"),
    ("arm64: control, A/A", "results/s8-arm-pooled/pooled.json aa; details.json aa.cell", exp_arm_aa_control,
     r"one binary against a byte-identical copy\): pooled (?P<r>[\d.]+), half-width (?P<hw>[\d.]+)%\."),
    ("arm64: control, A/A at the add's L2 cell", "site/data/arm64.json noise.identical_binary_aa.L2 (details.json aa_extra, pooled with harness/pool.py)", exp_arm_l2_aa_control,
     r"Every job also timed the same A/A at the add's L2 cell \(`details\.json`, `aa_extra`; `pooled\.json` does not hold it\): "
     r"pooled (?P<r>[\d.]+), half-width (?P<hw>[\d.]+)%\."),
    ("arm64: control, layout A/A", "results/s8-arm-pooled/pooled.json layout_aa", exp_arm_layout,
     r"the half-width runs from (?P<lo>[\d.]+)% at the quietest L1 cells to (?P<hi>[\d.]+)% \((?P<c>[a-z0-9 -]+, L2)\)\. "
     r"Moving the loops alone changes matrix multiply at L1 by (?P<m>[\d.]+)% \(ratio (?P<r>[\d.]+)\), the largest layout effect at L1; "
     r"the other L1 cells move by at most (?P<o>[\d.]+)%"),
    ("arm64: control, negative", "per-job listings k01..k03 none and fast", exp_arm_negative,
     r"the NEON instructions stay at (?P<a>\d+), (?P<b>\d+) and (?P<c>\d+); the forward sum's function is identical line for line in both builds and has no trap"),
    ("arm64: control, positive", "results/s8-arm-pooled/pooled.json positive", exp_arm_positive,
     r"at L1 it costs (?P<a>[\d.]+)x for the sum, (?P<b>[\d.]+)x for the add, (?P<c>[\d.]+)x for the stencil, (?P<d>[\d.]+)x for reverse, "
     r"(?P<e>[\d.]+)x for stride-2 and (?P<f>[\d.]+)x for matrix multiply \((?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x\)"),
    ("arm64: noise at L2, the identical binary", "site/data/arm64.json noise.identical_binary_aa and same_cell_l2; results/s8-arm-pooled/pooled.json cells and layout_aa",
     exp_arm_noise_l2_aa,
     r"The A/A at the forward add's L2 cell, pooled by the same method \(`harness/pool\.py`\), is (?P<r>[\d.]+) with an interval of (?P<lo>[\d.]+) to (?P<hi>[\d.]+), "
     r"a half-width of (?P<hw>[\d.]+)%, a spread between jobs of (?P<sd>[\d.]+)% and per-job ratios from (?P<jlo>[\d.]+) to (?P<jhi>[\d.]+)\. "
     r"At L1 the A/A is (?P<l1>[\d.]+)%\. The forward add at L2 has half-widths of (?P<h1>[\d.]+)% \(as compiled\), (?P<h2>[\d.]+)% \(aligned\) "
     r"and (?P<h3>[\d.]+)% \(the layout A/A\) in the same cell\."),
    ("arm64: noise at L2, the rule's ceiling", "site/data/arm64.json noise.identical_binary_aa; harness/criteria-v3.json aa_half_width_max_pct", exp_arm_noise_ceiling,
     r"The L2 A/A is above the rule's own ceiling of (?P<ceil>\d+)% in the pool and in (?P<jobs>\d+) of the (?P<of>\d+) jobs \(in (?P<l1>\w+) at L1\)"),
    ("arm64: noise at L2, slow processes", "site/data/arm64.json noise.mixture and noise.identical_binary_aa (per-process samples of every job)", exp_arm_noise_slow,
     r"A process is slow when it takes more than (?P<th>\d+)% longer than the fastest process of the same series \(one side of one cell in one job\)\. "
     r"At L1, (?P<n1>[\d.]+)% of NONE processes and (?P<f1>[\d.]+)% of FAST processes are slow; at L2, (?P<n2>[\d.]+)% and (?P<f2>[\d.]+)%, "
     r"and single cells reach (?P<mn>\d+)% \(NONE\) and (?P<mf>\d+)% \(FAST\)\. In the L2 A/A series the coefficient of variation of one side's 40 processes is "
     r"(?P<cva>[\d.]+)% and (?P<cvb>[\d.]+)% on the two sides of the pair \(median over jobs\), against (?P<c1a>[\d.]+)% and (?P<c1b>[\d.]+)% at L1, "
     r"and the slow processes come in runs: after a slow process the next one on that side is slow (?P<s1>\d+)% and (?P<s2>\d+)% of the time on the two sides of the pair, "
     r"after an ordinary one (?P<o1>\d+)%\."),
    ("arm64: noise at L2, the medians", "site/data/arm64.json noise.mixture cells; results/s8-arm-pooled/pooled.json cells", exp_arm_noise_medians,
     r"In the reverse and stride-2 cells at L2 only the NONE side has slow processes \((?P<r>\d+)% and (?P<s>\d+)% of them, none on the FAST side\)\. "
     r"Taken at the fast end of the timings .*? the two ratios are (?P<p1>[\d.]+)x and (?P<p2>[\d.]+)x, against the medians' (?P<m1>[\d.]+)x and (?P<m2>[\d.]+)x\. "
     r"For the forward add at L2 the same ratio is (?P<fa>[\d.]+), against a median ratio of (?P<fm>[\d.]+) whose interval is (?P<fw>[\d.]+)% either side\."),
    ("arm64: placement", "results/s8-arm-pooled/pooled.json verdict.placement_sensitive and cells placement.d", exp_arm_placement,
     r"(?P<n>\w+) cells are flagged: the add at L1 \(ratio of the two (?P<a>[\d.]+)\), the stencil at L1 \((?P<b>[\d.]+)\), "
     r"and matrix multiply at L1 \((?P<c>[\d.]+)\) and L2 \((?P<d>[\d.]+)\)\. On this quiet core the interval excludes 1 for a difference as small as "
     r"the add's (?P<e>[\d.]+)%"),
    ("arm64: placement, D against the layout A/A", "site/data/arm64.json layout_vs_placement; results/s8-arm-pooled/pooled.json placement.d and layout_aa", exp_arm_layout_vs_d,
     r"D, which moves the loops of both builds, is (?P<ds>[\d.]+) for the stencil at L1, (?P<d2>[\d.]+) for stride-2 at L1 and (?P<dg>[\d.]+) for gather at L1, "
     r"where the layout A/A moves (?P<ls>[\d.]+)%, (?P<l2>[\d.]+)% and (?P<lg>[\d.]+)%; for matrix multiply at L1 the layout A/A moves (?P<lm>[\d.]+)% and D (?P<dm>-?[\d.]+)%\. "
     r"D's interval excludes 1 and the layout A/A's includes it for the stencil at L1 and for gather at L2\..*?"
     r"on this core it moves by up to (?P<mx>[\d.]+)% at L1 \(gather\)"),
    ("arm64: placement, the matrix-multiply loop against its window", "results/s8-arm-run-*/*/details.json k08_matmul loops start_mod64 and windows64; results/s8-arm-pooled/pooled.json layout_aa",
     exp_arm_matmul_windows,
     r"as compiled the NONE NEON loop starts at offset (?P<off>\d+) of a (?P<w>\d+)-byte window and spans (?P<n1>\d+) windows, aligned it sits in (?P<n2>\d+), "
     r"and the aligned NONE build is (?P<pct>[\d.]+)% slower \(layout A/A ratio (?P<r>[\d.]+)\)"),
    ("arm64: verdict, form in the pool and in each run", "results/s8-arm-pooled/pooled.json verdict and per_run", exp_arm_verdict_form,
     r"in the pool and in each of the (?P<three>\w+) runs on their own"),
    ("arm64: verdict, the lost loops", "results/s8-arm-pooled/pooled.json cells; site/data/index.json criteria.lost_ci_lo_min_ratio", exp_arm_lost_floor,
     r"starts at (?P<lo>[\d.]+) or higher, against a minimum of (?P<min>[\d.]+)\."),
    ("arm64: verdict, the judged cells", "results/s8-arm-pooled/pooled.json cells and verdict.placement_sensitive", exp_arm_judged,
     r"(?P<four>\w+) of the (?P<eight>\w+) kept cells are judged \(the sum at L1 and L2, the add at L2, the stencil at L2\); the other (?P<four2>\w+) are the placement-sensitive ones"),
    ("arm64: verdict, the forward add at L2", "results/s8-arm-pooled/pooled.json cells and per_run", exp_arm_add_l2,
     r"The forward add at L2, aligned, has a ratio of (?P<r>[\d.]+) and an interval of (?P<lo>[\d.]+) to (?P<hi>[\d.]+); its upper end is "
     r"(?P<over>[\d.]+) over the limit of (?P<lim>[\d.]+), and the spread between jobs in that cell is (?P<sd>[\d.]+)%\. "
     r"In each run on its own both the forward sum and the forward add at L2 miss the rule"),
    ("arm64: verdict, counting the matrix-multiply cells", "results/s8-arm-pooled/pooled.json cells", exp_arm_matmul_counted,
     r"The one at L1 would miss the forward limit as well \((?P<m1>[\d.]+)x aligned\); the one at L2 \((?P<m2>[\d.]+)x aligned, interval ending at (?P<m3>[\d.]+)\) would pass it"),
    ("arm64: verdict, where the seed comes from", "harness/pool.py SEED_PREFIX and RESAMPLES; arm64/seed-sensitivity.json stored_seed; results/s8-arm-run-*/*/results.json run.started_at",
     exp_arm_seed_origin,
     r"bootstrap of (?P<res>\d+) resamples whose draws are fixed by a seed \(`harness/pool\.py`, prefix (?P<pre>\d+)\)\. "
     r"The seed was set on (?P<day>Oct \d+) \((?P<iso>[\d:T+-]+) in the development history, which this repository does not contain\), "
     r"(?P<days>\w+) days before the first Arm run"),
    ("arm64: verdict, the add's upper end under other seeds", "arm64/seed-sensitivity.json deciding_cell", exp_arm_seed_distribution,
     r"from the same data with the same code and the same (?P<res2>\d+) resamples, under (?P<n>\d+) other seeds \(`arm64/seed-sensitivity\.json`\): "
     r"the upper end has a median of (?P<med>[\d.]+) \(5th to 95th percentile (?P<p05>[\d.]+) to (?P<p95>[\d.]+), range (?P<mn>[\d.]+) to (?P<mx>[\d.]+)\), "
     r"(?P<k>\d+) of the (?P<n2>\d+) are at or above (?P<lim>[\d.]+), and the stored (?P<st>[\d.]+) is higher than all (?P<n3>\d+)\. "
     r"With (?P<conv>[\d,]+) resamples under the stored prefix the end converges to (?P<ch>[\d.]+), below the limit"),
    ("arm64: verdict, the whole analysis under other seeds", "arm64/seed-sensitivity.json full and derived; results/s8-arm-pooled/pooled.json verdict", exp_arm_seed_whole,
     r"`analyse_cpu` run under (?P<n>\d+) of those seeds gives (?P<map>\d+) MAP and (?P<inc>\d+) INCONCLUSIVE\. "
     r"The verdict form derived from the re-drawn statistics \(forward, lost, placement, A/A and positive-control rules\) for all (?P<all>\d+) is "
     r"(?P<m2>\d+) MAP and (?P<i2>\d+) INCONCLUSIVE, each of the (?P<i3>\d+) because of the same cell\. "
     r"Under every seed the lost loops pass, the placement-sensitive set is the same (?P<four>\w+) cells and the A/A half-width stays between (?P<alo>[\d.]+)% and (?P<ahi>[\d.]+)%\."),
    ("arm64: verdict, the other interval methods", "site/data/arm64.json interval_methods (robustness/results-arm.json)", exp_arm_interval_methods,
     r"`robustness/` applies (?P<k>\w+) interval methods to this pool \(.*?its self-test reproduces (?P<ex>\d+) of the pool's own numbers exactly\)\. "
     r"Only the pool's own method gives INCONCLUSIVE; .*? all give MAP, with the add's upper end at (?P<b1>[\d.]+) to (?P<b2>[\d.]+) \(block\), "
     r"(?P<c1>[\d.]+) and (?P<c2>[\d.]+) \(jobs only\) and (?P<d>[\d.]+) \(lag-1\), against the pool's (?P<a>[\d.]+)\."),
    ("arm64: verdict, the L2 A/A reading", "site/data/arm64.json noise.identical_binary_aa.L2; harness/criteria-v3.json aa_half_width_max_pct", exp_arm_seed_l2aa,
     r"\*\*The L2 A/A\.\*\* Read at the L2 cell the A/A is (?P<aa>[\d.]+)%, above the rule's (?P<c>\d+)% ceiling"),
    ("arm64: verdict, the independent check", "harness/pool_check.py SAMPLE_CELLS, BOUND_TOL_WIDTH and BOUND_TOL_RATIO; harness/criteria-v3.json verdict; results/s8-arm-pooled/pooled.json cells", exp_arm_seed_pool_check,
     r"`harness/pool_check\.py`, the recomputation that `scripts/check\.py` runs, samples this cell and prints how far its recomputed upper end lies from "
     r"(?P<lim>[\d.]+), for information only: its tolerance \(a share of the interval's width, about (?P<tol>[\d.]+) here\) is larger than the margin of "
     r"(?P<over>[\d.]+), so it could not flag a change of this size"),
    ("arm64: verdict, what this says", "results/s8-arm-pooled/pooled.json cells; arm64/seed-sensitivity.json deciding_cell", exp_arm_seed_summary,
     r"that cell's interval is (?P<hw>[\d.]+)% either side because L2 timings on this machine are that noisy, even for an identical binary, "
     r"and a margin of (?P<over>[\d.]+) is smaller than the bootstrap's seed noise"),
    ("arm64: run to run", "results/s8-arm-pooled/pooled.json reproduction and per_run", exp_arm_run_to_run,
     r"Of the (?P<chk>\d+) comparisons of one run's point against another run's interval \((?P<cells>\d+) cells, (?P<cols>\d+) columns, "
     r"(?P<pairs>\d+) ordered pairs of runs\), (?P<out>\d+) fall outside, with a largest gap of (?P<gap>[\d.]+)%\. "
     r"(?P<eight>\w+) of the (?P<out2>\d+) are stride-2 at L2 \(gaps of (?P<g1>[\d.]+)% to (?P<g2>[\d.]+)%\), where the runs' points are "
     r"(?P<p1>[\d.]+)x, (?P<p2>[\d.]+)x and (?P<p3>[\d.]+)x as compiled; the other (?P<five>\w+) have gaps under (?P<u>[\d.]+)%"),
    ("arm64: the smoke run", "arm64/PLAN.md", exp_arm_smoke_kernels,
     r"reverse was already seen in a (?P<k>\w+)-kernel smoke run"),
    ("arm64: written first, the forward loops", "per-job listings k01..k03", exp_arm_held,
     r"The first part held \((?P<a>\d+) / (?P<a2>\d+), (?P<b>\d+) / (?P<b2>\d+) and (?P<c>\d+) / (?P<c2>\d+) NEON instructions\)"),
    ("arm64: written first, every job pooled", "results/s8-arm-pooled/pooled.json; .github/workflows/measure.yml", exp_arm_held_jobs,
     r"none dropped:\*\* (?P<ret>\d+) of (?P<disp>\d+) returned and all are pooled"),
    ("arm64: limits, the time window", "results/s8-arm-run-*/*/results.json run.started_at", exp_arm_limits_window,
     r"\*\*Shared machines, (?P<n>\d+) jobs, one time window\.\*\* The (?P<three>\w+) runs were launched together and the jobs started within "
     r"(?P<m>\d+) minutes of each other"),
    ("arm64: limits, one compiler", "results/s8-arm-run-*/*/results.json run.toolchain", exp_arm_limits_compiler,
     r"\*\*One compiler\.\*\* clang (?P<c>[\d.]+) with libc\+\+ (?P<l>\d+) only"),
    ("arm64: limits, one core type", "results/s8-arm-pooled/pooled.json cpus; results/s8-arm-run-*/*/results.json run.runner", exp_arm_limits_core,
     r"\*\*(?P<one>\w+) core type\.\*\* (?P<core>Neoverse-N2), in (?P<one2>\w+) runner image"),
    ("arm64: limits, the L2 forward cells", "results/s8-arm-pooled/pooled.json cells", exp_arm_limits_spread,
     r"\*\*L2 forward cells are noisy\*\* \(spread between jobs up to (?P<s>[\d.]+)% for the add\)"),
    ("arm64: limits, the L2 identical binary", "site/data/arm64.json noise.identical_binary_aa.L2", exp_arm_limits_aa_l2,
     r"an identical binary is as noisy at the add's L2 cell \(A/A half-width (?P<aa>[\d.]+)%\), and the INCONCLUSIVE form rests on one of them, "
     r"by a margin inside the bootstrap's seed noise"),
    ("arm64: limits, the spread of the identical binary at L1", "results/s8-arm-pooled/pooled.json aa", exp_arm_limits_identical_spread,
     r"\(the identical-binary A/A at L1 has a spread between jobs of (?P<sd>[\d.]+)%\)"),
    ("arm64: limits, the placement shifts the layout A/A did not see", "site/data/arm64.json layout_vs_placement", exp_arm_limits_placement,
     r"did not see the placement shifts of the FAST/NONE ratio \((?P<st>[\d.]+)% for the stencil and (?P<ga>[\d.]+)% for gather at L1\)"),
    ("arm64: reproduce, the runs", "results/s8-arm-pooled/pooled.json runs", exp_arm_three_runs,
     r"\(the (?P<three>\w+) runs here were dispatched together\)"),
    ("arm64: reproduce, the seeds", "arm64/seed-sensitivity.json alt_seeds", exp_arm_seeds_reproduce,
     r"`python arm64/seeds\.py` rewrites `arm64/seed-sensitivity\.json` \(it re-draws (?P<n>\d+) seeds, so it takes a while\)"),
    ("arm64: written first, what the smoke run had given", "tests/data/s8_arm_timeline.json smoke; arm64/PLAN.md", exp_arm_smoke_quote,
     r"The smoke run \((?P<run>\d+)\) timed (?P<k>\w+) kernels at the (?P<sz>L\d) size and had given reverse (?P<r>[\d.]+)x, "
     r"the forward add (?P<a>[\d.]+)x and an A/A half-width of (?P<aa>[\d.]+)%; the plan quotes all three"),
    ("arm64: written first, the add's time ratio was known", "arm64/PLAN.md", exp_arm_smoke_add_known,
     r"for the add the time ratio at L1 \((?P<a>[\d.]+)x\) was known"),
    ("arm64: what was written first", "tests/data/s8_arm_timeline.json; arm64/PLAN.md", exp_arm_timeline,
     r"The (?P<k>\w+)-kernel smoke run \((?P<smoke>\d+)\) started at (?P<t0>[\d:]+) UTC on (?P<day>Oct \d+), the (?P<three>\w+) full runs were dispatched at "
     r"(?P<t1>[\d:]+) UTC, the plan was committed at (?P<t2>[\d:]+) UTC \((?P<t2e>[\d:]+) EDT\) and the first full-run job finished at (?P<t3>[\d:]+) UTC\..*?"
     r"The plan's own heading gives the time as (?P<h>[\d:]+) EDT, which is wrong \(the author date of the commit that added the file says (?P<c>[\d:]+)\)"),
    ("arm64: what was written first, what a reader can check", "tests/data/s8_arm_timeline.json", exp_arm_timeline_source,
     r"\(the run's creation time and the first measure job's completion time, read from the Actions API on (?P<d>Oct \d+)\)\. "
     r"The plan's commit time is not: it comes from the git log of the working repository in which the project is developed, which is (?P<np>not published),"),
]

# ---- replication sets B and C, and the d-sweep --------------------------------------------------------------------
# The sentences about the two replication sets (README.md, readme-parts/DETAILS.md, replication/README.md, arm64/README.md) rest on
# replication/results.json, which replication/compare.py derives from six pooled files (`python replication/compare.py --verify`
# recomputes it), and on the job records of results/s9-*. The sentences about the d-sweep (the same four documents and dsweep/README.md)
# rest on results/s10-dsweep-pooled/dsweep-pooled.json, which dsweep/analyze.py derives from the job files of results/s10-dsweep-run-*
# (`python dsweep/analyze.py --verify` recomputes those), on dsweep/PLAN.md for the plan's own table, and on dsweep/analyze.py, run
# here in memory with nothing written, for the one pool with a job left out. A table of the new sections is checked as a whole
# block against the same data (check_table_rows): the header, a separator and exactly the data's rows in order, so a changed number,
# an invented row, a repeated row, a deleted row and two swapped rows each fail.

REPL = "replication/results.json"
DSWEEP_POOL = "results/s10-dsweep-pooled/dsweep-pooled.json"
DSWEEP_PLAN = "dsweep/PLAN.md"
N2 = "Neoverse-N2"
V3 = "Neoverse-V3"
EPYC_9V45 = "AMD EPYC 9V45 96-Core Processor"
EPYC_9V74 = "AMD EPYC 9V74 80-Core Processor"
XEON_8573C = "INTEL(R) XEON(R) PLATINUM 8573C"
COLS = ("as_compiled", "aligned")
# the model names as the tables of the prose write them
REPL_NAME = {N2: "Neoverse-N2 (Arm)", V3: "Neoverse-V3 (Arm)", EPYC_7763: "AMD EPYC 7763", EPYC_9V45: "AMD EPYC 9V45",
             EPYC_9V74: "AMD EPYC 9V74", XEON_8573C: "Intel Xeon Platinum 8573C", "Intel(R) Xeon(R) 6973P-C": "Intel Xeon 6973P-C",
             "Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz": "Intel Xeon Platinum 8370C"}
DS_NAME = {N2: "Neoverse-N2", EPYC_7763: "AMD EPYC 7763", EPYC_9V45: "AMD EPYC 9V45", XEON_8573C: "Intel Xeon Platinum 8573C"}
DS_ROLE = {("fit",): "fit", ("scan",): "scan", ("bridge",): "bridge", ("fit", "study_l1"): "fit, study L1", ("study_l2",): "study L2"}


def row(label, source, fn, pattern):
    """A row whose expected values are the entries of fn() for the groups the pattern captures (fn may return more)."""
    names = tuple(re.compile(pattern, re.S).groupindex)

    def expected():
        full = fn()
        missing = [n for n in names if n not in full]
        assert not missing, f"{label}: the expected values do not include {missing}"
        return {n: full[n] for n in names}
    return (label, source, expected, pattern)


def repl():
    return J(REPL)


def repl_model(arch, key):
    return next(m for m in repl()[arch]["models"] if key in m["cpu_model"])


def repl_arm_cell(cell_id, which):
    return next(c for c in repl()["arm"]["named_cells"] if c["cell_id"] == cell_id)[which]


def repl_flip(key):
    return next(f for f in repl()["x86"]["flips"] if key in f["cpu_model"])


def repl_flip_cell(key, cell_id):
    return next(c for c in repl_flip(key)["cells"] if c["cell_id"] == cell_id)


def form_word(rec):
    return rec["form"].upper()


def job_records(pattern):
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, pattern))):
        with open(f, encoding="utf-8") as fh:
            out.append(json.load(fh))
    return out


S9_ARM_JOBS = "results/s9-arm-run-*/results-*/results.json"
S9_X86_JOBS = "results/s9-run-*/results-*/results.json"
S10_JOBS = "results/s10-dsweep-run-*/dsweep-job-*/dsweep.json"


def start_times(*patterns):
    return [datetime.datetime.strptime(d["run"]["started_at"], "%Y-%m-%dT%H:%M:%SZ") for p in patterns for d in job_records(p)]


def short_commit(*patterns):
    commits = {d["run"]["commit"][:7] for p in patterns for d in job_records(p)}
    assert len(commits) == 1, f"the jobs name {len(commits)} commits: {sorted(commits)}"
    return commits.pop()


S8_ARM_JOBS = "results/s8-arm-run-*/results-*/results.json"
RUN_LINKS = "tests/data/run_links_and_commits.json"
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def exp_start_lag():
    """The lag between creating a run and the first recorded start of its harness, from the three Arm runs of Oct 16 (the creation times in
    tests/data/s8_arm_timeline.json, the starts in the s8 job records): two runs started at once, the third waited for a runner."""
    lags = {}
    for r in J(ARM_TIMELINE)["full_runs"]:
        starts = [d["run"]["started_at"] for d in job_records(f"results/s8-arm-run-{r['run']}/results-*/results.json")]
        assert len(starts) == r["measure_jobs"], f"run {r['run']}: {len(starts)} job records, the timeline says {r['measure_jobs']}"
        lags[r["run"]] = (datetime.datetime.strptime(min(starts), TS_FORMAT) - datetime.datetime.strptime(r["created_at"], TS_FORMAT)).total_seconds()
    prompt = sorted(v for v in lags.values() if v < 60)
    queued = sorted(v for v in lags.values() if v >= 60)
    assert len(prompt) == 2 and len(queued) == 1, f"the lags of the three Arm runs are {sorted(lags.values())}; the texts say two that started at once and one that queued"
    assert all(v == int(v) for v in prompt + queued)
    return {"lo": str(int(prompt[0])), "hi": str(int(prompt[1])), "wait": str(int(queued[0]))}


def exp_holdout_order():
    """The holdout's plan commit time against the first recorded job start, and the rule file's hash in every holdout job."""
    recs = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(REPO, "results", "s5-holdout", "**", "results.json"), recursive=True))]
    assert len(recs) == 30, f"the holdout holds {len(recs)} job records"
    first = min(datetime.datetime.strptime(d["run"]["started_at"], TS_FORMAT) for d in recs)
    commit = datetime.datetime.strptime(J("site/data/holdout.json")["preregistration_committed_utc"], TS_FORMAT)
    gap = (commit - first).total_seconds()
    assert gap == 2, f"the holdout plan's commit time is {gap} s after the first recorded job start; the texts say 2 s after"
    assert {d["run"]["criteria_sha256"] for d in recs} == {lf_sha("harness/criteria-v3.json")}, "a holdout job records another rule-file hash than harness/criteria-v3.json"
    return {"tc": commit.strftime("%H:%M:%S"), "ts": first.strftime("%H:%M:%S"), "s": str(int(gap)), "n": str(len(recs))}


CURRENT_RUN_LINK = "github.com/JacoboPacheco/third-of-a-percent/actions/runs/"
LINKED_GROUPS = ("s6-run", "s7-run", "s8-arm-run", "s9-arm-run", "s9-run", "s10-dsweep-run", "s11-forwardt-run")


def record_commits(doc, top_level_commit=False):
    """The repository commit a record says its run was dispatched from: run.commit, source.repo_sha in the census records and, in the
    day-one records only, the top-level commit. Other commit fields (the upstream projects' pins in the census and in
    results/lostloops-live-*) are not these."""
    found = set()

    def walk(node, top):
        if isinstance(node, list):
            for x in node:
                walk(x, top)
        elif isinstance(node, dict):
            run, source = node.get("run"), node.get("source")
            if isinstance(run, dict) and isinstance(run.get("commit"), str):
                found.add(run["commit"][:7])
            if isinstance(source, dict) and isinstance(source.get("repo_sha"), str):
                found.add(source["repo_sha"][:7])
            if top and top_level_commit and isinstance(node.get("commit"), str) and re.fullmatch(r"[0-9a-f]{40}", node["commit"]):
                found.add(node["commit"][:7])
            for v in node.values():
                walk(v, False)
    walk(doc, True)
    return found


def result_groups():
    """Group -> the run ids its records link and the repository commits they name. The groups are the folders of results/ without their run id,
    plus "dayone" (dayone/results/) and "versions" (versions/results/)."""
    groups = {}
    for root, label in (("results", None), (os.path.join("dayone", "results"), "dayone"), (os.path.join("versions", "results"), "versions")):
        for dp, _, fns in os.walk(os.path.join(REPO, root)):
            for fn in fns:
                if not fn.endswith(".json"):
                    continue
                rel = os.path.relpath(os.path.join(dp, fn), os.path.join(REPO, root)).replace("\\", "/")
                if "/" not in rel:
                    continue  # results/fixture.json, the made-up sample, carries no run links or commits
                g = label or re.sub(r"-\d{8,}.*", "", rel.split("/")[0])
                with open(os.path.join(dp, fn), encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                e = groups.setdefault(g, {"runs": set(), "commits": set(), "current_name": set()})
                for m in re.finditer(r"github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/actions/runs/(\d+)", text):
                    e["runs"].add(m.group(1))
                    e["current_name"].add(CURRENT_RUN_LINK + m.group(1) in text)
                try:
                    e["commits"] |= record_commits(json.loads(text), top_level_commit=(label == "dayone"))
                except ValueError:
                    pass
    return groups


def exp_run_links():
    """Which run links work and which commits the records name (tests/data/run_links_and_commits.json, a record of what the GitHub API said),
    checked against the records themselves: the ids and commits of results/ are the ones the record lists, the seven linked groups are the ones that
    resolve and carry this repository's name in their links, every other group's ids returned 404 and its commits are not in the repository."""
    rec = J(RUN_LINKS)
    groups = result_groups()
    for g, e in groups.items():
        if not e["runs"] and not e["commits"]:
            continue  # pooled folders and the like: no run link and no commit of their own
        if g in LINKED_GROUPS:
            assert e["runs"] == set(rec["runs"][g]["resolve"]) and not rec["runs"][g]["not_found"], f"{g}: the run ids of the records are not the ones read as existing"
            assert e["current_name"] == {True}, f"{g}: a run link does not carry this repository's name"
        elif e["runs"]:
            assert e["runs"] == set(rec["runs"][g]["not_found"]) and not rec["runs"][g]["resolve"], f"{g}: its run links were read as existing, or are not the ones read"
        listed = {c["commit"]: c for c in rec["commits"].get(g, [])}
        assert e["commits"] == set(listed), f"{g}: the commits of the records are not the ones the record lists"
        if g in LINKED_GROUPS:
            assert all(c["in_repository"] for c in listed.values()), f"{g}: a commit the records name is not in the repository"
        elif g.startswith(("s1-", "s2-", "s3-", "s4-", "s5-", "mitigate", "siblings", "corpus", "realworld", "pgo")) or g in ("dayone", "versions"):
            assert not any(c["in_repository"] for c in listed.values()), f"{g}: a commit the records name is in the repository, the texts say it is not"
        else:
            raise AssertionError(f"{g}: a results folder group the texts do not place")
    assert set(rec["runs"]) <= set(groups), "the record lists a run group that results/ no longer has"
    arm, ds_ = rec["commits"]["s8-arm-run"], rec["commits"]["s10-dsweep-run"]
    assert [(c["commit"], c["vs_main"]) for c in arm] == [("6176991", "diverged")] and [(c["commit"], c["vs_main"]) for c in ds_] == [("8c874ec", "diverged")]
    for g in ("s6-run", "s7-run", "s9-arm-run", "s9-run"):
        assert {c["vs_main"] for c in rec["commits"][g]} == {"ahead"}, f"{g}: its commit is no longer an ancestor of the default branch"
    assert {c["vs_main"] for c in rec["commits"]["s11-forwardt-run"]} == {"identical"}, "the forwardt runs name a commit that was not the default branch's head when it was read"
    smoke = rec["arm_smoke"]
    assert smoke["head"].startswith("6176991") and smoke["measure_yml_sha256_at_head"] == smoke["measure_yml_sha256_on_main_at_bbcee23"], (
        "the measure.yml on arm-smoke is not recorded as the default branch's")
    assert rec["public_main_at_the_time"].startswith("bbcee23")
    s4 = len(job_records("results/s4-run-*/results-*/results.json"))
    return {"n4": str(s4), "p95": str(repl()["pools"]["x86"]["earlier"]["jobs"]), "nh": str(len(job_records("results/s5-holdout/runs/*/results-*/results.json"))),
            "n8": str(len(job_records(S8_ARM_JOBS))), "c8": "6176991", "b8": "arm-smoke", "base": "bbcee23",
            "r67": word(sum(1 for g in ("s6-run", "s7-run") for _ in rec["runs"][g]["resolve"])), "r8": word(len(rec["runs"]["s8-arm-run"]["resolve"])),
            "r9": word(len(rec["runs"]["s9-arm-run"]["resolve"]) + len(rec["runs"]["s9-run"]["resolve"])), "r10": word(len(rec["runs"]["s10-dsweep-run"]["resolve"])), "r11": word(len(rec["runs"]["s11-forwardt-run"]["resolve"])),
            "c10": "8c874ec", "b10": "dsweep-smoke"}


def exp_runner_cores():
    """run.runner.cores of every result record: 2 for the early runs (s1 to s4), 4 for the holdout and every later run."""
    cores = {}
    for dp, _, fns in os.walk(os.path.join(REPO, "results")):
        for fn in fns:
            if fn not in ("results.json", "dsweep.json"):
                continue
            with open(os.path.join(dp, fn), encoding="utf-8") as f:
                d = json.load(f)
            c = ((d.get("run") or {}).get("runner") or {}).get("cores")
            if c is not None:
                g = re.sub(r"-\d{8,}.*", "", os.path.relpath(dp, os.path.join(REPO, "results")).replace("\\", "/").split("/")[0])
                cores.setdefault(g, set()).add(c)
    early = {g: v for g, v in cores.items() if g.startswith(("s1-", "s2-", "s3-", "s4-"))}
    later = {g: v for g, v in cores.items() if g not in early}
    assert early and all(v == {2} for v in early.values()), f"the early runs report these core counts: {early}"
    assert later and all(v == {4} for v in later.values()), f"the later runs report these core counts: {later}"
    assert {"s5-holdout", "s6-run", "s7-run", "s8-arm-run", "s9-arm-run", "s9-run"} <= set(later)
    return {"e": "2", "l": "4"}


def exp_repl_sets():
    pools = repl()["pools"]
    a, x = pools["arm"]["replication"], pools["x86"]["replication"]
    assert a["models_drawn"] == {N2: 29, V3: 1}, f"set B drew {a['models_drawn']}; the text says 29 on Neoverse-N2 and 1 on Neoverse-V3"
    assert repl_model("arm", V3)["replication"]["enough"] is False, "the Neoverse-V3 job now has enough jobs for a verdict"
    assert {d["run"]["runner"]["arch"] for d in job_records(S9_ARM_JOBS)} == {"aarch64"}, "a set B job did not run on AArch64"
    assert {d["run"]["runner"]["arch"] for d in job_records(S9_X86_JOBS)} == {"x86_64"}, "a set C job did not run on x86-64"
    assert len(job_records(S9_ARM_JOBS)) == a["jobs"] and len(job_records(S9_X86_JOBS)) == x["jobs"], "the s9 job records and the pooled files disagree on the job count"
    labels = measure_runner_labels()
    return {"bj": str(a["jobs"]), "br": str(len(a["runs"])), "n2": str(a["models_drawn"][N2]), "v3": str(a["models_drawn"][V3]),
            "cj": str(x["jobs"]), "cr": str(len(x["runs"])), "ab": str(pools["arm"]["secondary"]["jobs"]),
            "ac": str(pools["x86"]["secondary"]["jobs"]), "p95": str(pools["x86"]["earlier"]["jobs"]),
            "bd": str(len(a["runs"]) * jobs_per_run()), "bq": str(a["jobs"]), "cd": str(len(x["runs"]) * jobs_per_run()), "cq": str(x["jobs"]),
            "a": str(a["jobs"]), "x": str(x["jobs"]), "xl": labels[0], "al": labels[1], "mn": str(repl()["criteria"]["minimum_jobs"])}


def exp_repl_arm():
    m = repl_model("arm", N2)
    cell = "k02_add_fwd.L2"
    ea, rb, sab = (repl_arm_cell(cell, w) for w in ("earlier", "replication", "secondary"))
    for who in ("earlier", "replication"):
        missed = [x["cell_id"] for x in m[who]["cause"]["forward_missed"]]
        assert missed == [cell], f"{who}: the verdict is decided by {missed}, the text says {cell} alone"
    assert ea["aligned"]["ratio"] < 1 and rb["aligned"]["ratio"] < 1, "a point estimate of the cell is not below 1"
    runs = m["secondary"]["per_run"]
    assert len(runs) == 6 and {r["form"] for r in runs} == {"inconclusive"}, "not every one of the six runs alone is INCONCLUSIVE"
    assert ea["limit"] == rb["limit"] == sab["limit"], "the sets name different limits"
    return {"n": str(m["replication"]["jobs"]), "fb": form_word(m["replication"]), "ha": f4(ea["aligned"]["ci95"][1]),
            "hb": f4(rb["aligned"]["ci95"][1]), "lim": str(ea["limit"]), "pa": f3(ea["aligned"]["ratio"]), "pb": f3(rb["aligned"]["ratio"]),
            "nab": str(m["secondary"]["jobs"]), "fab": form_word(m["secondary"]), "hab": f4(sab["aligned"]["ci95"][1]),
            "stab": m["secondary"]["stability"], "six": word(len(runs)), "fr": runs[0]["form"].upper(), "fa": form_word(m["earlier"])}


def exp_repl_x86():
    r = repl()["x86"]
    t = r["totals"]
    same = sorted(m["cpu_model"] for m in r["models"] if m["testable"] and m["same_form"])
    assert same == sorted([EPYC_7763, EPYC_9V74]), f"the models with the same word as the 95-job pool: {same}"
    assert all(repl_model("x86", k)["earlier"]["form"] == "map" for k in ("7763", "9V74")), "the 7763 and 9V74 pools are no longer MAP"
    assert sorted(f["cpu_model"] for f in r["flips"]) == sorted([EPYC_9V45, XEON_8573C]), "the models whose word changed are no longer 9V45 and 8573C"
    m45, m85 = repl_model("x86", "9V45"), repl_model("x86", "8573C")
    c45, c85 = repl_flip_cell("9V45", "k03_stencil.L1"), repl_flip_cell("8573C", "k02_add_fwd.L1")
    assert len(repl_flip("9V45")["cells"]) == 1 and len(repl_flip("8573C")["cells"]) == 1, "a flip is decided by more than one cell"
    assert (c45["earlier"]["role"], c45["replication"]["role"]) == ("exempt_placement_sensitive", "judged_forward"), "the 9V45 stencil changed roles the other way"
    assert (c85["earlier"]["role"], c85["replication"]["role"]) == ("judged_forward", "exempt_placement_sensitive"), "the 8573C add changed roles the other way"
    h45 = [c45[w]["aligned"]["ci95"][1] for w in ("earlier", "replication")]
    a85 = [c85[w]["aligned"]["ratio"] for w in ("earlier", "replication")]
    assert abs(h45[0] - h45[1]) < 0.001 and abs(a85[0] - a85[1]) < 0.005, "the measured cost of a flipped cell is no longer about the same"
    assert c45["earlier"]["limit"] == c45["replication"]["limit"] == c85["replication"]["limit"]
    return {"four": word(t["testable_models"]), "mn": str(repl()["criteria"]["minimum_jobs"]), "two": word(t["same_form"]),
            "two2": word(t["flipped"]), "p95": str(repl()["pools"]["x86"]["earlier"]["jobs"]),
            "e45": str(m45["earlier"]["jobs"]), "r45": str(m45["replication"]["jobs"]), "fe45": form_word(m45["earlier"]),
            "fr45": form_word(m45["replication"]), "u1": f4(h45[0]), "u2": f4(h45[1]), "lim": str(c45["earlier"]["limit"]),
            "d1": f4(c45["earlier"]["placement"]["d_ci95"][1]), "d2": f4(c45["replication"]["placement"]["d_ci95"][1]),
            "e85": str(m85["earlier"]["jobs"]), "r85": str(m85["replication"]["jobs"]), "fe85": form_word(m85["earlier"]),
            "fr85": form_word(m85["replication"]), "c1": f3(a85[0]), "c2": f3(a85[1]),
            "ac": f3(c85["replication"]["as_compiled"]["ratio"]), "al": f3(c85["replication"]["aligned"]["ratio"]),
            "lo": f3(c85["earlier"]["aligned"]["ci95"][0]), "hi": f3(c85["earlier"]["aligned"]["ci95"][1]),
            "d3": f4(c85["replication"]["placement"]["d_ci95"][1])}


def exp_repl_untested():
    m = repl_model("x86", "6973P-C")
    q = repl()["questions"]["xeon_6973pc"]
    assert m["testable"] is False and q["testable"] is False
    miss = m["secondary"]["cause"]["forward_missed"]
    assert [x["cell_id"] for x in miss] == ["k03_stencil.L1"], f"the 8-job form is decided by {[x['cell_id'] for x in miss]}"
    assert "k03_stencil.L1" in m["earlier"]["placement_sensitive"] and "k03_stencil.L1" not in m["secondary"]["placement_sensitive"], (
        "the stencil at L1 no longer changes from left out to judged between the 7-job and the 8-job pool")
    return {"rj": str(m["replication"]["jobs"]), "mn": str(q["minimum_jobs"]), "ej": str(m["earlier"]["jobs"]), "ej2": str(m["earlier"]["jobs"]),
            "sj": str(m["secondary"]["jobs"]), "sf": form_word(m["secondary"]), "hi": f4(miss[0]["aligned_ci95"][1])}


def repl_points(arch):
    return [(m, p) for m in repl()[arch]["models"] if m["inside"] for p in m["inside"]["points"]]


def exp_repl_reproduction():
    out = {}
    for tag, arch in (("a", "arm"), ("x", "x86")):
        pts = repl_points(arch)
        t = repl()[arch]["totals"]
        assert t["points_checked"] == len(pts) and t["points_inside"] == sum(1 for _, p in pts if p["inside"])
        al = [p for _, p in pts if p["column"] == "aligned"]
        narrow = sum(1 for _, p in pts if (p["earlier_ci95"][1] - p["earlier_ci95"][0]) / 2 / p["earlier"] < 0.001)
        big_m, big_p = max(pts, key=lambda mp: abs(mp[1]["point_diff_pct"]))
        gaps = [m["inside"]["max_gap_pct"] for m, _ in {id(m): (m, p) for m, p in pts}.values() if m["inside"]["max_gap_pct"] is not None]
        out.update({tag + "i": str(t["points_inside"]), tag + "c": str(t["points_checked"]), tag + "c2": str(t["points_checked"]),
                    tag + "al": str(sum(1 for p in al if p["inside"])), tag + "alc": str(len(al)),
                    tag + "u": str(t["point_diff_under_1pct"]), tag + "uc": str(t["points_checked"]),
                    tag + "d": f2(abs(big_p["point_diff_pct"])), tag + "n": str(narrow), tag + "nc": str(t["points_checked"]),
                    tag + "g": f2(max(gaps)), tag + "big": (big_p["cell_id"], big_p["column"], big_m["cpu_model"])})
    assert out["abig"][:2] == ("k05_stride2.L2", "aligned"), f"the largest Arm difference is {out['abig']}"
    assert out["xbig"] == ("k05_stride2.L2", "as_compiled", XEON_8573C), f"the largest x86-64 difference is {out['xbig']}"
    return out


def exp_repl_headline():
    h = repl()["x86"]["headline"]
    r, pr = h["replication_enough_range"], h["page_range"]
    enough = [x for x in h["replication"] if x["enough"]]
    assert len(h["outside_printed_range"]) == 0 and len(h["outside_stored_range"]) == 1, "the cells outside the printed or the stored range changed"
    o = h["outside_stored_range"][0]
    assert "9V45" in o["cpu_model"] and o["jobs"] == 5 and (o["cell_id"], o["column"]) == ("k05_stride2.L1", "as_compiled") and o["ratio"] < pr["min"]
    assert o["ratio"] == r["min"], "the cell outside the stored range is not the lowest cell of set C"
    assert f1(o["ratio"]) == pr["printed_min"], "the cell outside the stored range no longer prints as the page's lowest end"
    return {"lo": f3(r["min"]), "hi": f3(r["max"]), "four": word(len(enough)), "mn": str(repl()["criteria"]["minimum_jobs"]),
            "plo": pr["printed_min"], "phi": pr["printed_max"], "oj": str(o["jobs"]), "ov": f4(o["ratio"]),
            "gap": f4(pr["min"] - o["ratio"]), "smin": f4(pr["min"]), "pm": f1(o["ratio"])}


def exp_repl_window():
    ts = start_times(S9_ARM_JOBS, S9_X86_JOBS)
    ds_ts = start_times(S10_JOBS)
    assert len({t.date() for t in ts + ds_ts}) == 1, "the jobs did not all start on one day"
    assert (max(ds_ts) - min(ds_ts)).total_seconds() < 60, "the d-sweep jobs did not all start within one minute"
    reps = [repl_model("x86", k)["replication"] for k in ("9V45", "9V74", "8573C")]
    assert all(x["stability"] == "not assessable" for x in reps), "stability became assessable for a model of set C"
    d = ts[0]
    return {"n": str(len(ts)), "t0": min(ts).strftime("%H:%M"), "t1": max(ts).strftime("%H:%M"), "day": f"{MONTHS[d.month - 1]} {d.day}",
            "dn": str(len(ds_ts)), "j": str(max(x["jobs"] for x in reps)), "r0": str(min(x["runs"] for x in reps)),
            "r1": str(max(x["runs"] for x in reps)), "c1": short_commit(S9_ARM_JOBS, S9_X86_JOBS), "c2": short_commit(S10_JOBS)}


# the d-sweep

def ds():
    return J(DSWEEP_POOL)


def ds_cpu(key):
    return next(c for c in ds()["cpus"] if key in c["cpu_model"])


def ds_rows(c, column):
    return {r["d"]: r for r in c["columns"][column]["rows"]}


def ds_instr(c):
    return {r["d"]: r for r in c["instructions"]["rows"]}


def ds_plan_r12():
    with open(os.path.join(REPO, DSWEEP_PLAN), encoding="utf-8") as f:
        m = re.search(r"^\| 12 \| ([\d.]+) \| ([\d.]+) \|$", f.read(), re.M)
    assert m, "dsweep/PLAN.md no longer has the illustrative table row for d = 12"
    return m.group(1)


@lru_cache(maxsize=None)
def ds_leave_one_out():
    """The EPYC 7763 d-sweep pooled again without job 4 of run 39018974239: {column: (share with all, share without, word without)}.

    Run in memory with dsweep/analyze.py (40 resamples: the share is a point estimate and does not depend on them, the word is the
    same as with 2000); nothing is written. The pool of all the model's jobs must give the stored share first."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("dsweep_analyze_for_the_readme_test", os.path.join(REPO, "dsweep", "analyze.py"))
    an = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(an)
    entries = an.load_entries(sorted(glob.glob(os.path.join(REPO, "results", "s10-dsweep-run-*"))), os.path.join(REPO, "results", "s10-dsweep-pooled"))
    items = [(r, d) for r, d in entries if EPYC_7763 == d["run"]["runner"]["cpu_model"]]
    kept = [(r, d) for r, d in items if not (str(d["run"]["id"]) == "39018974239" and str(d["run"]["job"]) == "4")]
    assert len(items) == ds_cpu("7763")["jobs"] and len(kept) == len(items) - 1, "job 4 of run 39018974239 is not one of the 7763 jobs"
    plan, crit = an.plan_sha256(), an.criteria_sha256()
    whole = an.analyse_cpu(EPYC_7763, items, plan, crit, resamples=40)
    part = an.analyse_cpu(EPYC_7763, kept, plan, crit, resamples=40)
    out = {}
    for col in COLS:
        stored = ds_cpu("7763")["columns"][col]["excess"]["share"]
        assert abs(whole["columns"][col]["excess"]["share"] - stored) < 1e-9, f"pooling the 7763 jobs again gives another {col} share than the pooled file"
        out[col] = (stored, part["columns"][col]["excess"]["share"], part["words"][col]["word"])
    return out


def exp_ds_overview():
    d = ds()
    assert not d["incomplete_jobs"] and len(d["inputs"]) == sum(c["jobs"] for c in d["cpus"]), "the pooled file does not list every job"
    arm = ds_cpu(N2)
    others = [c for c in d["cpus"] if c is not arm]
    x_runs = sorted({r for c in others for r in c["runs"]})
    all_runs = sorted({r for c in d["cpus"] for r in c["runs"]})
    sizes = [len(c["columns"]["as_compiled"]["rows"]) for c in d["cpus"]]
    assert len(arm["runs"]) == 1 and len(x_runs) == 2 and len(job_records(S10_JOBS)) == len(d["inputs"])
    return {"three": word(len(all_runs)), "jobs": str(len(d["inputs"])), "arm": str(arm["jobs"]), "ar": word(len(arm["runs"])),
            "x": str(sum(c["jobs"] for c in others)), "xr": word(len(x_runs)), "lo": str(min(sizes)), "hi": str(max(sizes)),
            "ra": arm["runs"][0], "rb": x_runs[0], "rc": x_runs[1], "dj": str(len(d["inputs"])),
            "r": f2(ds_rows(arm, "as_compiled")[arm["ladder"]["study_l1_d"]]["ratio"]), "d": str(arm["ladder"]["study_l1_d"]),
            "res": str(arm["ladder"]["residue"]), "m": str(arm["ladder"]["modulus"]),
            "a0": str(arm["ladder"]["fit"][0]), "a1": str(arm["ladder"]["fit"][-1]),
            "b0": str(ds_cpu("7763")["ladder"]["fit"][0]), "b1": str(ds_cpu("7763")["ladder"]["fit"][-1]),
            "h1lo": str(d["rule"]["h1_share_band"][0]), "h1hi": str(d["rule"]["h1_share_band"][1]), "h2lo": str(d["rule"]["h2_share_band"][0]),
            "h2hi": str(d["rule"]["h2_share_band"][1]), "fl": str(d["rule"]["falls_share_above"]), "mn": str(d["rule"]["minimum_jobs"]),
            "reps": str(J("harness/criteria-v3.json")["v3"]["timing"]["reps_per_side"]), "nsz": str(len(ds_rows(arm, "as_compiled"))),
            "step": str(arm["ladder"]["modulus"]), "g0": str(arm["ladder"]["bridge"][0]), "g1": str(arm["ladder"]["bridge"][1]),
            "g2": str(arm["ladder"]["bridge"][2]), "sc0": str(arm["ladder"]["scan"][0]), "sc1": str(arm["ladder"]["scan"][-1])}


def exp_ds_words():
    arm, x7, x9, x8 = ds_cpu(N2), ds_cpu("7763"), ds_cpu("9V45"), ds_cpu("8573C")
    assert arm["verdict"]["word"] == "neither" and arm["verdict"]["columns_agree"] is False, "the Neoverse-N2 word is no longer 'neither' with disagreeing columns"
    assert x7["verdict"]["word"] == "H2" and x7["verdict"]["columns_agree"] is True
    assert x9["verdict"]["word"] == x8["verdict"]["word"] == "too few jobs"
    sac, sal = (arm["columns"][c]["excess"]["share"] for c in COLS)
    assert sac > 1 and sal > 1, "a Neoverse-N2 fixed share is not above 1"
    return {"j7": str(x7["jobs"]), "r7": str(len(x7["runs"])), "w7": x7["verdict"]["word"], "jn": str(arm["jobs"]), "rn": str(len(arm["runs"])),
            "wn": arm["verdict"]["word"], "wac": arm["words"]["as_compiled"]["word"], "sac": f3(sac), "wal": arm["words"]["aligned"]["word"],
            "sal": f3(sal), "j9": str(x9["jobs"]), "j8": str(x8["jobs"]), "pr": ds_plan_r12(),
            "obs": f2(ds_rows(arm, "as_compiled")[arm["ladder"]["fit"][0]]["ratio"]),
            "rac": f3(sac), "ral": f3(sal)}


def exp_ds_numbers():
    c = ds_cpu(N2)
    ac, al, ins = ds_rows(c, "as_compiled"), ds_rows(c, "aligned"), ds_instr(c)
    lad = c["ladder"]
    assert lad["fit"][:2] == [12, 20] and lad["bridge"] == [76, 108, 148] and lad["study_l2_d"] == 209 and lad["study_l1_d"] == 52
    four = [d for d in ac if d % 8 == 4 and d <= 148]
    assert four == [12, 20, 28, 36, 44, 52, 76, 108, 148], four
    extra = [ins[d]["extra_per_inner"] for d in four]
    assert round(min(extra)) == round(max(extra)), "the extra instructions per inner call differ by more than a rounding at d = 4 mod 8"
    for d, r in ins.items():
        if d % 8:
            assert abs(r["extra_per_inner"] - (45 + 8 * (d % 8))) < 0.25, f"d = {d}: {r['extra_per_inner']} extra instructions, not 45 + 8r"
    assert {d % 8 for d in ins} == set(range(8))
    mids = [28, 36, 44, 52, 76, 108]
    flat = [ac[d]["excess_ns_per_inner"] for d in lad["fit"][2:]]
    assert max(flat) - min(flat) < 0.2 and min(ac[d]["excess_ns_per_inner"] for d in lad["fit"][:2]) > max(flat), "the as-compiled excess is not flat from d = 28 after two larger ones"
    ex = lambda col, ds_: [col[d]["excess_ns_per_inner"] for d in ds_]  # noqa: E731
    return {"ex": str(round(ins[52]["extra_per_inner"])), "lo": f1(min(extra)), "hi": f1(max(extra)), "r": str(lad["residue"]), "m": str(lad["modulus"]),
            "d0": str(four[0]), "d1": str(four[-1]), "a12": f1(ac[12]["excess_ns_per_inner"]), "alo": f1(min(ex(ac, mids))),
            "ahi": f1(max(ex(ac, mids))), "a148": f1(ac[148]["excess_ns_per_inner"]), "a209": f2(ac[209]["excess_ns_per_inner"]),
            "b12": f1(al[12]["excess_ns_per_inner"]), "blo": f1(min(ex(al, mids))), "bhi": f1(max(ex(al, mids))),
            "b148": f1(al[148]["excess_ns_per_inner"]), "b209": f2(al[209]["excess_ns_per_inner"]), "s1": str(lad["fit"][0]),
            "s2": str(lad["fit"][1]), "fl": str(lad["fit"][2]),
            "c0": "45", "c1": "8", "mod": str(lad["modulus"]), "r0": "1", "r1": "7", "i4": str(round(ins[52]["extra_per_inner"])),
            "rr": str(lad["residue"]), "i209": str(round(ins[209]["extra_per_inner"])), "dl2": str(lad["study_l2_d"]), "r209": str(209 % 8),
            "d48": "48", "r48": str(48 % 8), "i48": str(round(ins[48]["extra_per_inner"]))}


def exp_ds_caveats():
    c = ds_cpu(N2)
    ac, al = ds_rows(c, "as_compiled"), ds_rows(c, "aligned")
    sens = {r["d"]: r["sensitive"] for r in c["placement"]["rows"]}
    assert [d for d, s in sens.items() if not s] == [48], "the unflagged size is no longer d = 48 alone"
    l1 = c["ladder"]["study_l1_d"]
    scan = [d for d in c["ladder"]["scan"] if d != 48]
    assert scan == [45, 46, 47, 49, 50, 51] and 48 in c["ladder"]["scan"] and 48 % 8 == 0
    return {"s": str(sum(sens.values())), "n": str(len(sens)), "d48": "48", "m": "8", "m2": "8", "r48": f2(ac[48]["ratio"]), "r48b": f3(ac[48]["ratio"]),
            "n49": f2(ac[49]["ratio"]), "n47": f2(ac[47]["ratio"]), "st": f2(ac[l1]["ratio"]), "res": str(l1 % 8),
            "slo": f2(min(ac[d]["ratio"] for d in scan)), "shi": f2(max(ac[d]["ratio"] for d in scan)), "r48c": f3(al[48]["ratio"]),
            "blo": f2(min(al[d]["ratio"] for d in scan)), "bhi": f2(max(al[d]["ratio"] for d in scan)), "d": "48",
            "ac": f3(ac[l1]["ratio"]), "al": f3(al[l1]["ratio"]), "l1": str(l1)}


def exp_ds_loo():
    got = ds_leave_one_out()
    assert got["as_compiled"][2] == got["aligned"][2] == "H2", "the 7763 word without the job is no longer H2 in both columns"
    return {"job": "4", "run": "39018974239", "a0": f3(got["as_compiled"][0]), "a1": f3(got["as_compiled"][1]), "b0": f3(got["aligned"][0]),
            "b1": f3(got["aligned"][1]), "w": got["as_compiled"][2]}


def exp_ds_boundary():
    """Neoverse-N2: d = 76 and 108 are past the core's L1d, the excess per inner call is flat from d = 28 to d = 108 in both columns
    and smaller only at d = 148 and d = 209 (the sentences that replace 'the same at every d')."""
    c = ds_cpu(N2)
    ac, al = ds_rows(c, "as_compiled"), ds_rows(c, "aligned")
    sizes = {j["run"]["runner"]["l1d_kib"] for j in job_records(S10_JOBS) if j["run"]["runner"]["cpu_model"] == N2}
    assert len(sizes) == 1, f"the Neoverse-N2 jobs report these L1d sizes: {sorted(sizes)}"
    l1 = sizes.pop()
    lad = c["ladder"]
    assert lad["bridge"] == [76, 108, 148] and lad["fit"][2] == 28 and lad["study_l2_d"] == 209
    for d in ac:
        assert ac[d]["working_set_bytes"] == 12 * d * d, f"d = {d}: the working set is not three d x d int32 matrices"
    assert all(ac[d]["working_set_bytes"] > l1 * 1024 for d in (76, 108, 148, 209)), "a size the text puts past the L1d is not past it"
    mids = [28, 36, 44, 52, 76, 108]
    for col in (ac, al):
        flat = [col[d]["excess_ns_per_inner"] for d in mids]
        assert max(flat) - min(flat) < 0.25, f"the excess is not flat from d = 28 to d = 108: {flat}"
        assert col[148]["excess_ns_per_inner"] < min(flat) - 0.1 and col[209]["excess_ns_per_inner"] < col[148]["excess_ns_per_inner"], \
            "the excess is no longer smaller at d = 148 and smaller still at d = 209"
    return {"fl": str(lad["fit"][2]), "last": str(mids[-1]), "p1": str(lad["bridge"][0]), "p2": str(lad["bridge"][1]), "l1": str(l1),
            "q1": str(lad["bridge"][2]), "q2": str(lad["study_l2_d"]), "q1b": str(lad["bridge"][2]), "q2b": str(lad["study_l2_d"]),
            "w76": thousands(ac[76]["working_set_bytes"]), "w108": thousands(ac[108]["working_set_bytes"]),
            "p1b": str(lad["bridge"][0]), "p2b": str(lad["bridge"][1])}


def exp_ds_reason():
    """The stored reason of the aligned Neoverse-N2 column ends in a phrase that means 'inside the H1 band', not 'constant'."""
    c = ds_cpu(N2)
    reason = c["words"]["aligned"]["reason"]
    m = re.search(r"the excess per inner call is (the same at every d)$", reason)
    assert m, f"the stored reason of the aligned column no longer ends 'the same at every d': {reason}"
    assert c["words"]["aligned"]["word"] == "H1"
    al = ds_rows(c, "aligned")
    lad = c["ladder"]
    upto = [d for d in al if d in lad["fit"] or d in lad["bridge"][:2]]
    vals = [al[d]["excess_ns_per_inner"] for d in upto]
    return {"ph": m.group(1), "h1lo": str(ds()["rule"]["h1_share_band"][0]), "h1hi": str(ds()["rule"]["h1_share_band"][1]), "wal": c["words"]["aligned"]["word"],
            "sal": f3(c["columns"]["aligned"]["excess"]["share"]), "blo": f1(min(vals)), "bhi": f1(max(vals)), "d0": str(lad["fit"][0]),
            "d1": str(lad["bridge"][1]), "b148": f1(al[lad["bridge"][2]]["excess_ns_per_inner"]), "b209": f2(al[lad["study_l2_d"]]["excess_ns_per_inner"])}


def exp_workflow_count():
    return {"n": str(len(glob.glob(os.path.join(REPO, ".github", "workflows", "*.yml"))))}


def exp_repl_intro():
    q = repl()["questions"]
    arm = q["arm_cell"]
    x = q["xeon_6973pc"]
    ea = repl_arm_cell(arm["decides_earlier"][0], "earlier")
    assert arm["decides_earlier"] == ["k02_add_fwd.L2"]
    return {"fa": arm["earlier_form"].upper(), "ha": f4(ea["aligned"]["ci95"][1]), "lim": str(ea["limit"]), "fx": x["earlier_form"].upper(),
            "hx": f4(x["earlier_closest_forward"]["aligned_hi"]), "pts": str(repl_model("arm", N2)["inside"]["checked"]),
            "cells": str(repl_model("arm", N2)["inside"]["checked"] // 2),
            "plo": repl()["x86"]["headline"]["page_range"]["printed_min"], "phi": repl()["x86"]["headline"]["page_range"]["printed_max"]}


def exp_smoke_branch():
    return {"c": short_commit(S10_JOBS)}


def exp_s9_commit():
    return {"commit": short_commit(S9_ARM_JOBS, S9_X86_JOBS)}


def exp_repl_runs():
    pools = repl()["pools"]
    a, x = sorted(pools["arm"]["replication"]["runs"]), sorted(pools["x86"]["replication"]["runs"])
    return {"a1": a[0], "a2": a[1], "a3": a[2], "c1": x[0], "c2": x[1], "c3": x[2], "c4": x[3], "commit": short_commit(S9_ARM_JOBS, S9_X86_JOBS)}


def exp_ds_replication_pointer():
    return {"stab": exp_repl_arm()["stab"]}


# the line-by-line tables

def repl_table_rows():
    r = repl()

    def cell(rec):
        if rec is None:
            return "-"
        if not rec["enough"]:
            return f"too few jobs ({rec['jobs']})"
        return f"{form_word(rec)} ({rec['jobs']})"
    models = [("arm", N2)] + [("x86", m["cpu_model"]) for m in r["x86"]["models"]] + [("arm", V3)]
    rows = []
    for arch, name in models:
        m = next(x for x in r[arch]["models"] if x["cpu_model"] == name)
        same = "not tested" if not m["testable"] else ("yes" if m["same_form"] else "no")
        inside = "-" if not m["inside"] else f"{m['inside']['inside']} of {m['inside']['checked']}"
        rows.append(f"| {REPL_NAME[name]} | {cell(m['earlier'])} | {cell(m['replication'])} | {same} | {inside} | {cell(m['secondary'])} |")
    return rows


def ds_words_table_rows():
    rows = []
    for name in (N2, EPYC_7763, EPYC_9V45, XEON_8573C):
        c = next(x for x in ds()["cpus"] if x["cpu_model"] == name)

        def col(column, c=c):
            w = c["words"][column]["word"]
            if w == "too few jobs":
                return w
            e = c["columns"][column]["excess"]
            return f"{w} ({f3(e['share'])} [{f3(e['share_ci95'][0])}, {f3(e['share_ci95'][1])}])"
        rows.append(f"| {DS_NAME[name]} | {c['jobs']} ({len(c['runs'])}) | {col('as_compiled')} | {col('aligned')} | {c['verdict']['word']} |")
    assert {c["cpu_model"] for c in ds()["cpus"]} == set(DS_NAME), "the d-sweep has a CPU model the tables do not name"
    return rows


def ds_sizes_table_rows():
    c = ds_cpu(N2)
    ac, al, ins = ds_rows(c, "as_compiled"), ds_rows(c, "aligned"), ds_instr(c)
    return [f"| {d} | {ac[d]['d_mod_8']} | {DS_ROLE[tuple(ac[d]['roles'])]} | {f3(ac[d]['ratio'])} | {f3(al[d]['ratio'])} | "
            f"{f2(ac[d]['excess_ns_per_inner'])} | {f2(al[d]['excess_ns_per_inner'])} | {f1(ins[d]['extra_per_inner'])} |" for d in sorted(ac)]


def repl_files_table_rows():
    pools = repl()["pools"]
    folder = lambda p: f"`{p['path'].split('/')[1]}`"  # noqa: E731
    a, x = pools["arm"], pools["x86"]
    b = a["replication"]["models_drawn"]
    return [f"| Arm, set A (the original column) | {a['earlier']['jobs']} | {folder(a['earlier'])} | read by the page |",
            f"| Arm, set B | {a['replication']['jobs']} ({b[N2]} Neoverse-N2, {b[V3]} Neoverse-V3) | {folder(a['replication'])} | the replication of set A |",
            f"| Arm, sets A and B | {a['secondary']['jobs']} | {folder(a['secondary'])} | secondary |",
            f"| x86-64, the first pool | {x['earlier']['jobs']} | {folder(x['earlier'])} | read by the page |",
            f"| x86-64, set C | {x['replication']['jobs']} | {folder(x['replication'])} | the replication of the first pool |",
            f"| x86-64, the first pool and set C | {x['secondary']['jobs']} | {folder(x['secondary'])} | secondary |"]


def ds_readme_words_rows():
    rows = []
    for name in (N2, EPYC_7763, EPYC_9V45, XEON_8573C):
        c = next(x for x in ds()["cpus"] if x["cpu_model"] == name)
        v = c["verdict"]
        if v["word"] == "too few jobs":
            what = "too few jobs"
        elif v["columns_agree"]:
            what = f"{v['word']} in both columns"
        else:
            what = f"{v['word']}: the two columns disagree (as compiled \"{c['words']['as_compiled']['word']}\", aligned {c['words']['aligned']['word']})"
        rows.append(f"| {DS_NAME[name]} | {c['jobs']} ({len(c['runs'])}) | {what} |")
    return rows


def table_block(text, header):
    """The contiguous run of lines starting with '|' that begins at the line `header` (the header, the separator and every data row)."""
    lines = [ln.rstrip() for ln in text.splitlines()]
    starts = [i for i, ln in enumerate(lines) if ln == header]
    assert len(starts) == 1, f"the header line occurs {len(starts)} times (once expected): {header}"
    block = []
    for ln in lines[starts[0]:]:
        if not ln.startswith("|"):
            break
        block.append(ln)
    return block


def check_table_rows(label, rows, text, doc):
    """rows[0] is the header line, the rest are the data rows in order. The whole table block of the document must equal them:
    the header, a separator line, then exactly these rows, no more, no fewer, none repeated or out of order."""
    header, expected = rows[0], rows[1:]
    block = table_block(text, header)
    assert len(block) >= 2 and re.fullmatch(r"\|(?:\s*:?-{3,}:?\s*\|)+", block[1]), f"{label}: {doc} has no separator line under the header {header}"
    got = block[2:]
    extra = [r for r in got if r not in expected]
    missing = [r for r in expected if r not in got]
    assert not extra and not missing, (f"{label}: {doc} differs from the data's rows.\n  rows the data does not give:\n    " + "\n    ".join(extra or ["(none)"])
                                       + "\n  data rows the document lacks:\n    " + "\n    ".join(missing or ["(none)"]))
    assert len(got) == len(expected), f"{label}: {doc} has {len(got)} data rows, the data gives {len(expected)} (a row is repeated)"
    assert got == expected, f"{label}: {doc} lists the rows in another order than the data:\n  " + "\n  ".join(got)


# the typed sentences

README_NEW_ROWS = [
    row("replication: the two sets", "replication/results.json pools; results/s9-*/results-*/results.json arch", exp_repl_sets,
        r"set B, (?P<bj>\d+) more Arm jobs in (?P<br>\d+) runs \((?P<n2>\d+) on Neoverse-N2 and (?P<v3>\d+) on a Neoverse-V3 core, which has no verdict\), "
        r"and set C, (?P<cj>\d+) more x86-64 jobs in (?P<cr>\d+) runs"),
    row("replication: Arm", "replication/results.json arm models, named_cells k02_add_fwd.L2", exp_repl_arm,
        r"Set B alone \((?P<n>\d+) Neoverse-N2 jobs\) is (?P<fb>[A-Z]+) again, on the same cell: the forward add at L2, aligned, ends at (?P<ha>[\d.]+) in set A "
        r"and (?P<hb>[\d.]+) in set B against the (?P<lim>[\d.]+) limit, with a point estimate below 1 in both \((?P<pa>[\d.]+) and (?P<pb>[\d.]+)\)\. "
        r"The cell sits close to the [\d.]+ limit in both sets, so a second [A-Z]+ is a weak repeat of the word and not strong evidence for it\. "
        r"Sets A and B pooled \((?P<nab>\d+) Neoverse-N2 jobs\) give (?P<fab>[A-Z]+), with that end at (?P<hab>[\d.]+); the harness labels that form (?P<stab>\w+), "
        r"because each of the (?P<six>\w+) runs alone is (?P<fr>[A-Z]+)\. The stored Arm verdict stays (?P<fa>[A-Z]+)\."),
    row("replication: x86-64, the four models", "replication/results.json x86 totals and models", exp_repl_x86,
        r"(?P<four>\w+) models had (?P<mn>\d+) or more jobs in set C\. (?P<two>\w+) gave the same verdict word as the (?P<p95>\d+)-job pool "
        r"\(EPYC 7763 and 9V74, MAP\) and (?P<two2>\w+) a different one\."),
    row("replication: x86-64, EPYC 9V45", "replication/results.json x86 flips (9V45, k03_stencil.L1)", exp_repl_x86,
        r"On EPYC 9V45 \((?P<e45>\d+) jobs (?P<fe45>[A-Z]+), then (?P<r45>\d+) jobs (?P<fr45>[A-Z]+)\) the stencil at L1 is left out as placement-sensitive "
        r"in the (?P<p95>\d+)-job pool and judged in set C; its aligned upper end is (?P<u1>[\d.]+) and (?P<u2>[\d.]+) against the (?P<lim>[\d.]+) limit\."),
    row("replication: x86-64, Xeon 8573C", "replication/results.json x86 flips (8573C, k02_add_fwd.L1)", exp_repl_x86,
        r"On the Xeon 8573C \((?P<e85>\d+) jobs (?P<fe85>[A-Z]+), then (?P<r85>\d+) jobs (?P<fr85>[A-Z]+)\) the forward add at L1 is judged in the "
        r"(?P<p95>\d+)-job pool and left out in set C; it costs (?P<c1>[\d.]+) and (?P<c2>[\d.]+) aligned\. In both, the word changed because the written rule "
        r"treated one cell differently, while the measured cost of the cell is about the same\. The 8573C's MAP in set C is not the cost going away: "
        r"the exempt forward add still costs (?P<ac>[\d.]+) as compiled and (?P<al>[\d.]+) aligned\."),
    row("replication: not tested", "replication/results.json x86 models (6973P-C) and questions.xeon_6973pc", exp_repl_untested,
        r"Set C drew (?P<rj>\d+) job of the Xeon 6973P-C \((?P<mn>\d+) are the minimum\), so the question of its borderline MAP has no answer from these sets\. "
        r"Pooled with its (?P<ej>\d+) earlier jobs \((?P<sj>\d+) jobs, a secondary form\) it is (?P<sf>[A-Z]+), because the stencil at L1, left out as "
        r"placement-sensitive in the (?P<ej2>\d+)-job pool, is judged and ends at (?P<hi>[\d.]+); one added job"),
    row("replication: reproduction", "replication/results.json arm and x86 models inside.points", exp_repl_reproduction,
        r"(?P<ai>\d+) of (?P<ac>\d+) Arm points and (?P<xi>\d+) of (?P<xc>\d+) x86-64 points lie inside the earlier pool's interval, counting the as-compiled "
        r"and the aligned column \(aligned alone: (?P<aal>\d+) of (?P<aalc>\d+) and (?P<xal>\d+) of (?P<xalc>\d+), the form the plan asked for; "
        r"the both-column count was chosen after the data were in\); (?P<au>\d+) of (?P<auc>\d+) and "
        r"(?P<xu>\d+) of (?P<xuc>\d+) differ from the earlier point by under 1%, and the largest differences are (?P<ad>[\d.]+)% \(Arm stride-2 at L2, aligned\) "
        r"and (?P<xd>[\d.]+)% \(Xeon 8573C stride-2 at L2, as compiled\)\. The inside test is strict where the earlier interval is very narrow "
        r"\(a half-width under 0\.1% of the ratio for (?P<an>\d+) of the (?P<anc>\d+) Arm points and (?P<xn>\d+) of the (?P<xnc>\d+) x86-64 points\); "
        r"the farthest missed point is (?P<ag>[\d.]+)% \(Arm\) and (?P<xg>[\d.]+)% \(x86-64\) from the interval\."),
    row("replication: the headline range", "replication/results.json x86 headline", exp_repl_headline,
        r"set C ranges from (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x over the (?P<four>\w+) models with (?P<mn>\d+) or more jobs, so the printed "
        r"(?P<plo>[\d.]+)x to (?P<phi>[\d.]+)x stands; one cell, the EPYC 9V45 stride-2 at L1 as compiled \((?P<oj>\d+) jobs, (?P<ov>[\d.]+)x\), "
        r"lies (?P<gap>[\d.]+)x under the stored minimum of (?P<smin>[\d.]+)x and prints as (?P<pm>[\d.]+)x\."),
    row("d-sweep: the three runs", "results/s10-dsweep-pooled/dsweep-pooled.json inputs, cpus", exp_ds_overview,
        r"Three runs \((?P<jobs>\d+) jobs: (?P<arm>\d+) on Arm in (?P<ar>\w+) run, (?P<x>\d+) on x86-64 in (?P<xr>\w+)\) timed matrix multiply at "
        r"(?P<lo>\d+) to (?P<hi>\d+) sizes for each CPU model"),
    row("d-sweep: the registered words", "results/s10-dsweep-pooled/dsweep-pooled.json words, verdict, excess shares; dsweep/PLAN.md table", exp_ds_words,
        r"EPYC 7763 \((?P<j7>\d+) jobs, (?P<r7>\d+) runs\): (?P<w7>H\d), a cost per element, which the plan expected where the loop loses SIMD\. "
        r"Neoverse-N2 \((?P<jn>\d+) jobs, (?P<rn>\d+) run\): \"(?P<wn>\w+)\", because the two columns disagree: as compiled the excess \"(?P<wac>\w+)\" "
        r"\(fixed share (?P<sac>[\d.]+)\), aligned it is (?P<wal>H\d) \((?P<sal>[\d.]+)\)\. Both shares are above 1, so it is not a mixture\. "
        r"EPYC 9V45 \((?P<j9>\d+) jobs\) and Xeon 8573C \((?P<j8>\d+) job\) were too few for a word\. The plan's illustrative table gave R\(12\) = (?P<pr>[\d.]+) "
        r"under H1 and (?P<obs>[\d.]+) was observed"),
    row("d-sweep: instructions and times", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns and instructions", exp_ds_numbers,
        r"FAST adds (?P<ex>\d+) extra instructions per inner call \((?P<lo>[\d.]+) to (?P<hi>[\d.]+)\) at every size with d = (?P<r>\d) mod (?P<m>\d) from "
        r"(?P<d0>\d+) to (?P<d1>\d+) \(instruction counts, a secondary column, not times\)\. As compiled, the excess time per inner call is (?P<a12>[\d.]+) ns "
        r"at d = 12, (?P<alo>[\d.]+) to (?P<ahi>[\d.]+) ns at d = 28, 36, 44, 52, 76 and 108, (?P<a148>[\d.]+) ns at d = 148 and (?P<a209>[\d.]+) ns at d = 209; "
        r"aligned, (?P<b12>[\d.]+) ns, (?P<blo>[\d.]+) to (?P<bhi>[\d.]+) ns, (?P<b148>[\d.]+) ns and (?P<b209>[\d.]+) ns\. The word \"falls\" as compiled "
        r"rests on the two smallest sizes, (?P<s1>\d+) and (?P<s2>\d+), with the excess flat, at the sizes with d = 4 mod 8, from d = (?P<fl>\d+)"),
    row("d-sweep: caveats and d = 48", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 placement and columns", exp_ds_caveats,
        r"\((?P<s>\d+) of the (?P<n>\d+) sizes are flagged placement-sensitive\).*?d = (?P<d48>\d+), a multiple of (?P<m>\d+), costs (?P<r48>[\d.]+)x as compiled "
        r"against (?P<n49>[\d.]+)x and (?P<n47>[\d.]+)x at 49 and 47, so the (?P<st>[\d.]+)x belongs to the study size, which is (?P<res>\d+) mod (?P<m2>\d+)\."),
    row("d-sweep: the temporary branch", "results/s10-dsweep-run-*/dsweep-job-*/dsweep.json run.commit", exp_smoke_branch,
        r"the temporary public branch `dsweep-smoke` \(commit (?P<c>[0-9a-f]+)\)"),
]

DETAILS_NEW_ROWS = [
    row("details: replication, the line in the method", "replication/results.json pools; results/s10-dsweep-pooled/dsweep-pooled.json inputs",
        lambda: {"bj": exp_repl_sets()["bj"], "cj": exp_repl_sets()["cj"], "dj": exp_ds_overview()["dj"]},
        r"Two replication sets \((?P<bj>\d+) more Arm jobs and (?P<cj>\d+) more x86-64 jobs\) and a matrix-multiply size sweep \((?P<dj>\d+) jobs\) followed"),
    row("details: replication, why", "replication/results.json questions; robustness/seed-sensitivity-x86.json converged end",
        lambda: exp_repl_why_with_seeds(),
        r"the Arm pool's (?P<fa>[A-Z]+) \(the forward add at L2, aligned, ends at (?P<ha>[\d.]+) against the (?P<lim>[\d.]+) limit\) and the Xeon 6973P-C's "
        r"(?P<fx>[A-Z]+) \(its stencil at L2 ends at (?P<hx>[\d.]+) under the stored seed and at (?P<conv>[\d.]+) once the draw no longer matters\)"),
    row("details: replication, the two sets", "replication/results.json pools; results/s9-*/ job records", exp_repl_sets,
        r"set B, (?P<bj>\d+) jobs on the arm64 runner in (?P<br>\d+) runs \(`results/s9-arm-run-\*/`; (?P<n2>\d+) on Neoverse-N2 and (?P<v3>\d+) on Neoverse-V3\), "
        r"and set C, (?P<cj>\d+) jobs on the x86-64 runner in (?P<cr>\d+) runs"),
    row("details: replication, the secondary pools", "replication/results.json pools", exp_repl_sets,
        r"`results/s9-arm-ab-pooled/`, (?P<ab>\d+) jobs; `results/s9-x86-ac-pooled/`, (?P<ac>\d+) jobs"),
    row("details: replication, what the counts are", "replication/results.json arm models inside", exp_repl_intro,
        r"how many of the earlier pool's (?P<pts>\d+) points \((?P<cells>\d+) in-cache cells, as compiled and aligned\)"),
    row("details: replication, Arm", "replication/results.json arm models, named_cells k02_add_fwd.L2", exp_repl_arm,
        r"Set B alone is (?P<fb>[A-Z]+) again, on the same cell as set A: the forward add at L2, aligned, ends at (?P<ha>[\d.]+) in set A and (?P<hb>[\d.]+) in set B "
        r"against the (?P<lim>[\d.]+) limit, and its point estimate is below 1 in both \((?P<pa>[\d.]+) and (?P<pb>[\d.]+)\)\. "
        r"The cell sits close to the [\d.]+ limit in both sets, so a second [A-Z]+ is a weak repeat of the word and not strong evidence for it\. The pooled sets A and B give "
        r"(?P<fab>[A-Z]+), with that end at (?P<hab>[\d.]+); each of the (?P<six>\w+) runs alone is (?P<fr>[A-Z]+), so the harness labels the pooled form "
        r"(?P<stab>\w+)\. The stored Arm verdict stays (?P<fa>[A-Z]+)\."),
    row("details: replication, x86-64", "replication/results.json x86 totals", exp_repl_x86,
        r"(?P<four>\w+) models had (?P<mn>\d+) or more jobs in set C\. (?P<two>\w+) gave the same word as the (?P<p95>\d+)-job pool and (?P<two2>\w+) a different one"),
    row("details: replication, EPYC 9V45", "replication/results.json x86 flips (9V45, k03_stencil.L1)", exp_repl_x86,
        r"EPYC 9V45: the stencil at L1 is left out as placement-sensitive in the (?P<p95>\d+)-job pool \(its placement statistic's interval ends at (?P<d1>[\d.]+)\) "
        r"and judged in set C \(the interval ends at (?P<d2>[\d.]+)\); its aligned upper end is (?P<u1>[\d.]+) and (?P<u2>[\d.]+) against the (?P<lim>[\d.]+) limit\."),
    row("details: replication, Xeon 8573C", "replication/results.json x86 flips (8573C, k02_add_fwd.L1)", exp_repl_x86,
        r"Xeon 8573C: the forward add at L1 is judged in the (?P<p95>\d+)-job pool \(aligned (?P<c1>[\d.]+) \[(?P<lo>[\d.]+), (?P<hi>[\d.]+)\]\) and left out in set C "
        r"\(the interval of its placement statistic ends at (?P<d3>[\d.]+), aligned (?P<c2>[\d.]+)\)\. The 8573C's MAP in set C is not the cost going away: "
        r"the exempt forward add costs (?P<ac>[\d.]+) as compiled and (?P<al>[\d.]+) aligned, over the (?P<lim>[\d.]+) limit\."),
    row("details: replication, not tested", "replication/results.json x86 models (6973P-C)", exp_repl_untested,
        r"Set C drew (?P<rj>\d+) job of the Xeon 6973P-C, so whether its borderline MAP repeats has no answer from these sets\. Pooled with its (?P<ej>\d+) earlier jobs "
        r"\((?P<sj>\d+) jobs, a secondary form\) it is (?P<sf>[A-Z]+), because the stencil at L1, left out as placement-sensitive in the (?P<ej2>\d+)-job pool, "
        r"is judged and its aligned interval ends at (?P<hi>[\d.]+)\."),
    row("details: replication, reproduction", "replication/results.json arm and x86 models inside.points", exp_repl_reproduction,
        r"\(aligned alone: (?P<aal>\d+) of (?P<aalc>\d+) on Arm and (?P<xal>\d+) of (?P<xalc>\d+) on x86-64\)\. (?P<au>\d+) of (?P<auc>\d+) Arm points and "
        r"(?P<xu>\d+) of (?P<xuc>\d+) x86-64 points differ from the earlier point by under 1%; the largest differences are (?P<ad>[\d.]+)% "
        r"\(Arm stride-2 at L2, aligned\) and (?P<xd>[\d.]+)% \(Xeon 8573C stride-2 at L2, as compiled\)\. The test is strict where the earlier interval is "
        r"very narrow \(a half-width under 0\.1% of the ratio for (?P<an>\d+) of the (?P<anc>\d+) Arm points and (?P<xn>\d+) of the (?P<xnc>\d+) x86-64 points\); "
        r"the farthest missed point is (?P<ag>[\d.]+)% \(Arm\) and (?P<xg>[\d.]+)% \(x86-64\) from the interval\."),
    row("details: replication, the headline", "replication/results.json x86 headline", exp_repl_headline,
        r"the cells of reverse, stride-2 and matrix multiply range from (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x in set C over the (?P<four>\w+) models with "
        r"(?P<mn>\d+) or more jobs, so the (?P<plo>[\d.]+)x to (?P<phi>[\d.]+)x printed holds at the study's sizes\. One cell, the EPYC 9V45 stride-2 at L1 as compiled "
        r"\((?P<oj>\d+) jobs, (?P<ov>[\d.]+)x\), is (?P<gap>[\d.]+)x under the stored minimum of (?P<smin>[\d.]+)x and prints as (?P<pm>[\d.]+)x\."),
    row("details: d-sweep, the question", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns", exp_ds_overview,
        r"On Neoverse-N2 matrix multiply keeps its NEON loop under FAST and costs (?P<r>[\d.]+)x at L1;"),
    row("details: d-sweep, the rule", "results/s10-dsweep-pooled/dsweep-pooled.json rule, ladders", exp_ds_overview,
        r"sizes with d = (?P<res>\d) mod (?P<m>\d) \((?P<a0>\d+) to (?P<a1>\d+) on Neoverse-N2, (?P<b0>\d+) to (?P<b1>\d+) on EPYC 7763\): H1 if its point and "
        r"95% interval lie inside (?P<h1lo>[\d.]+) to (?P<h1hi>[\d.]+), H2 inside (?P<h2lo>-?[\d.]+) to (?P<h2hi>[\d.]+), \"falls\" above (?P<fl>[\d.]+), "
        r"otherwise \"neither\"; a CPU model needs (?P<mn>\d+) jobs"),
    row("details: d-sweep, the runs", "results/s10-dsweep-pooled/dsweep-pooled.json inputs, cpus", exp_ds_overview,
        r"Three runs of the d-sweep workflow \((?P<ra>\d+) on Arm, (?P<rb>\d+) and (?P<rc>\d+) on x86-64; `results/s10-dsweep-run-\*/`, pooled in "
        r"`results/s10-dsweep-pooled/`\) timed (?P<jobs>\d+) jobs at (?P<lo>\d+) to (?P<hi>\d+) sizes per CPU model"),
    row("details: d-sweep, reading", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns", exp_ds_numbers,
        r"rests on the two smallest fit sizes, (?P<s1>\d+) and (?P<s2>\d+); at the sizes with d = 4 mod 8 the excess is flat from d = (?P<fl>\d+)"),
    row("details: d-sweep, instructions", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 instructions", exp_ds_numbers,
        r"FAST adds (?P<c0>\d+) \+ (?P<c1>\d+)r instructions per inner call, r = d mod (?P<mod>\d+), for r = (?P<r0>\d) to (?P<r1>\d): (?P<i4>\d+) for every size "
        r"with r = (?P<rr>\d) from d = (?P<d0>\d+) to (?P<d1>\d+), and (?P<i209>\d+) at d = (?P<dl2>\d+) \(r = (?P<r209>\d)\)\. At d = (?P<d48>\d+) "
        r"\(r = (?P<r48>\d)\) it adds (?P<i48>\d+)\."),
    row("details: d-sweep, times", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns", exp_ds_numbers,
        r"As compiled: (?P<a12>[\d.]+) ns at d = 12, (?P<alo>[\d.]+) to (?P<ahi>[\d.]+) ns at d = 28, 36, 44, 52, 76 and 108, (?P<a148>[\d.]+) ns at d = 148 "
        r"and (?P<a209>[\d.]+) ns at d = 209\. Aligned: (?P<b12>[\d.]+) ns at d = 12, (?P<blo>[\d.]+) to (?P<bhi>[\d.]+) ns at d = 28, 36, 44, 52, 76 and 108, "
        r"(?P<b148>[\d.]+) ns at d = 148 and (?P<b209>[\d.]+) ns at d = 209\."),
    row("details: d-sweep, d = 48", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns", exp_ds_caveats,
        r"d = (?P<d48>\d+), a multiple of (?P<m>\d+), costs (?P<r48b>[\d.]+)x as compiled against (?P<slo>[\d.]+)x to (?P<shi>[\d.]+)x at 45, 46, 47, 49, 50 and 51 "
        r"\(aligned: (?P<r48c>[\d.]+)x against (?P<blo>[\d.]+)x to (?P<bhi>[\d.]+)x\), so the (?P<st>[\d.]+)x belongs to the study size, d = (?P<l1>\d+), "
        r"which is (?P<res>\d+) mod (?P<m2>\d+)\."),
    row("details: d-sweep, the plan's table", "dsweep/PLAN.md illustrative table; results/s10-dsweep-pooled/dsweep-pooled.json", exp_ds_words,
        r"it gave R\(12\) = (?P<pr>[\d.]+) under H1 on Neoverse-N2; (?P<obs>[\d.]+) was observed as compiled"),
    row("details: d-sweep, caveats", "results/s10-dsweep-pooled/dsweep-pooled.json placement and columns", exp_ds_caveats,
        r"(?P<s>\d+) of the (?P<n>\d+) sizes are flagged placement-sensitive \(all but d = (?P<d>\d+)\) and the ratio at the study size moves from "
        r"(?P<ac>[\d.]+) as compiled to (?P<al>[\d.]+) aligned"),
    row("details: d-sweep, the job left out", "dsweep/analyze.py run in memory on results/s10-dsweep-run-*", exp_ds_loo,
        r"Leaving out one EPYC 7763 job \(job (?P<job>\d+) of run (?P<run>\d+)\) moves its as-compiled share from (?P<a0>[\d.]+) to (?P<a1>[\d.]+) and its aligned "
        r"share from (?P<b0>[\d.]+) to (?P<b1>[\d.]+), and the word stays (?P<w>H\d) in both columns"),
    row("details: what the new sets do not test, the window", "results/s9-*/ and results/s10-dsweep-run-*/ job records run.started_at, run.commit; replication/results.json", exp_repl_window,
        r"All (?P<n>\d+) jobs of the two sets started between (?P<t0>[\d:]+) and (?P<t1>[\d:]+) UTC on (?P<day>Oct \d+), and the (?P<dn>\d+) jobs of the d-sweep "
        r"within one minute of each other"),
    row("details: what the new sets do not test, the stability", "replication/results.json x86 models", exp_repl_window,
        r"\(at most (?P<j>\d+) jobs, in (?P<r0>\d+) to (?P<r1>\d+) runs\)"),
    row("details: what the new sets do not test, the commits", "results/s9-*/ and results/s10-dsweep-run-*/ job records run.commit", exp_repl_window,
        r"`results/s9-\*` name commit (?P<c1>[0-9a-f]+) of the default branch, and those of `results/s10-dsweep-run-\*/` name commit (?P<c2>[0-9a-f]+) of the temporary branch"),
    row("details: stage S9", "results/s9-*/ and replication/results.json pools; .github/workflows/measure.yml", exp_repl_sets,
        r"\| S9 \| Replication: two further sets of `measure\.yml` runs, planned in writing \(`replication/PLAN\.md`, committed in the author's unpublished development "
        r"history \d+ seconds before the first job's recorded start; the order of plan and dispatch cannot be established from the records\): set B on "
        r"`(?P<al>[\w.-]+)` \((?P<br>\d+) runs, (?P<bd>\d+) jobs dispatched, (?P<bq>\d+) returned results; (?P<n2>\d+) on Neoverse-N2, (?P<v3>\d+) on Neoverse-V3\) "
        r"and set C on `(?P<xl>[\w.-]+)` \((?P<cr>\d+) runs, (?P<cd>\d+) jobs dispatched, (?P<cq>\d+) returned\)"),
    row("details: stage S10", "results/s10-dsweep-pooled/dsweep-pooled.json inputs, cpus, ladders", exp_ds_overview,
        r"\| S10 \| The d-sweep: matrix multiply timed at (?P<lo>\d+) to (?P<hi>\d+) sizes per CPU model; .*? three runs of the d-sweep workflow "
        r"\((?P<jobs>\d+) jobs: (?P<arm>\d+) on Neoverse-N2, (?P<x>\d+) on x86-64\), dispatched from the temporary public branch `dsweep-smoke`"),
    row("details: stage S10, the words", "results/s10-dsweep-pooled/dsweep-pooled.json words", exp_ds_words,
        r"registered words H2 on EPYC 7763 \((?P<j7>\d+) jobs\) and \"neither\" on Neoverse-N2 \((?P<jn>\d+) jobs\)"),
    row("details: layout, the workflows", ".github/workflows/*.yml", exp_workflow_count,
        r"\.github/workflows/  (?P<n>\d+) workflows;"),
    row("details: the follow-up list, replication", "replication/results.json pools", exp_repl_sets,
        r"`replication/`: two further sets of full runs \((?P<a>\d+) Arm jobs, (?P<x>\d+) x86-64 jobs\)"),
    row("details: the follow-up list, dsweep", "results/s10-dsweep-pooled/dsweep-pooled.json cpus", exp_ds_overview,
        r"`dsweep/`: matrix multiply timed at (?P<lo>\d+) to (?P<hi>\d+) sizes per CPU model"),
]

ARM64_NEW_ROWS = [
    row("arm64: the d-sweep that was run", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 ladder, words and columns",
        lambda: {**exp_ds_overview(), **exp_ds_numbers(), **exp_ds_words(), **exp_ds_boundary(), "w": ds_cpu(N2)["verdict"]["word"]},
        r"\(d = (?P<a0>\d+) to (?P<a1>\d+) in steps of (?P<step>\d+) and (?P<g0>\d+), (?P<g1>\d+) and (?P<g2>\d+), all at d mod (?P<m>\d+) = (?P<res>\d+), "
        r"a scan of (?P<sc0>\d+) to (?P<sc1>\d+), and (?P<dl2>\d+)\) and timed matrix multiply at (?P<nsz>\d+) sizes in (?P<ar>\w+) run of (?P<arm>\d+) jobs "
        r"on this core\. The registered word for Neoverse-N2 is \"(?P<w>\w+)\": as compiled the excess time per inner call falls with d "
        r"\(fixed share (?P<sac>[\d.]+), the rule's word \"(?P<wac>\w+)\"; (?P<a148>[\d.]+) ns at d = 148 and (?P<a209>[\d.]+) ns at d = 209\); aligned the fixed share is "
        r"(?P<sal>[\d.]+), inside the registered H1 band \((?P<h1lo>[\d.]+) to (?P<h1hi>[\d.]+)\), yet the aligned excess also falls at d = (?P<q1>\d+) "
        r"\((?P<b148>[\d.]+) ns\) and at d = (?P<q2>\d+) \((?P<b209>[\d.]+) ns\)\. At the sizes with d = 4 mod 8, from d = (?P<fl>\d+) to d = (?P<last>\d+), the excess is flat "
        r"\((?P<alo>[\d.]+) to (?P<ahi>[\d.]+) ns as compiled, (?P<blo>[\d.]+) to (?P<bhi>[\d.]+) ns aligned\), and d = (?P<p1>\d+) and d = (?P<p2>\d+) are past the "
        r"L1 size of this core \((?P<l1>\d+) KiB L1d: (?P<w76>[\d,]+) B and (?P<w108>[\d,]+) B\), so the excess is flat across the L1 boundary and smaller only at "
        r"d = (?P<q1b>\d+) and d = (?P<q2b>\d+)"),
    row("arm64: the replication of set A", "replication/results.json arm models",
        lambda: {**exp_repl_arm(), "bj": exp_repl_sets()["bj"], "n2": exp_repl_sets()["n2"]},
        r"A replication of (?P<bj>\d+) more jobs \(set B, (?P<n2>\d+) of them Neoverse-N2\), planned in writing \(the records do not show the order\), was run afterwards; alone it is (?P<fb>[A-Z]+) on the same cell, "
        r"with the aligned interval ending at (?P<hb>[\d.]+), and pooled with this column \((?P<nab>\d+) Neoverse-N2 jobs\) it gives (?P<fab>[A-Z]+), "
        r"which the harness labels (?P<stab>\w+)\."),
]

REPLICATION_ROWS = [
    row("replication/README: why", "replication/results.json questions", exp_repl_intro,
        r"the forward add at L2, aligned, ends at (?P<ha>[\d.]+) against a limit of (?P<lim>[\d.]+), and the Xeon 6973P-C is (?P<fx>[A-Z]+) with its stencil at L2 "
        r"ending at (?P<hx>[\d.]+), just under the same limit"),
    row("replication/README: the sets", "replication/results.json pools", exp_repl_sets,
        r"\(B: (?P<bj>\d+) Arm jobs in (?P<br>\d+) runs; C: (?P<cj>\d+) x86-64 jobs in (?P<cr>\d+) runs\)"),
    row("replication/README: the runs", "replication/results.json pools runs; results/s9-*/ job records run.commit", exp_repl_runs,
        r"`results/s9-arm-run-\*` \(runs (?P<a1>\d+), (?P<a2>\d+) and (?P<a3>\d+)\) and `results/s9-run-\*` \(runs (?P<c1>\d+), (?P<c2>\d+), (?P<c3>\d+) and (?P<c4>\d+)\)\. "
        r"Every job record names commit (?P<commit>[0-9a-f]+) of the default branch"),
    row("replication/README: what came out", "replication/results.json arm models and x86 totals, headline", lambda: {**exp_repl_arm(), **exp_repl_x86(), **exp_repl_untested(), **exp_repl_headline()},
        r"Set B alone is (?P<fb>[A-Z]+) again, on the same cell \(the forward add at L2, aligned: (?P<ha>[\d.]+) in set A, (?P<hb>[\d.]+) in set B, limit (?P<lim>[\d.]+)\)\. "
        r"The cell sits close to the limit in both sets, so a second [A-Z]+ is a weak repeat of the word and not strong evidence for it\. "
        r"Of the (?P<four>\w+) x86-64 models with (?P<mn>\d+) or more jobs in set C, (?P<two>\w+) gave the same verdict word as the first pool and (?P<two2>\w+) a different one; "
        r".*? The Xeon 6973P-C had (?P<rj>\d+) job in set C and could not be tested\. The headline range of (?P<plo>[\d.]+)x to (?P<phi>[\d.]+)x holds\."),
]

DSWEEP_ROWS = [
    row("dsweep/README: status", "results/s10-dsweep-pooled/dsweep-pooled.json inputs", exp_ds_overview,
        r"three runs \((?P<jobs>\d+) jobs\); no further runs are planned"),
    row("dsweep/README: the question", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 ladder and columns", exp_ds_overview,
        r"still costs (?P<r>[\d.]+)x at the L1 size \(d = (?P<d>\d+)\)"),
    row("dsweep/README: the runs", "results/s10-dsweep-pooled/dsweep-pooled.json cpus runs", exp_ds_overview,
        r"\((?P<ra>\d+) on Arm, (?P<rb>\d+) and (?P<rc>\d+) on x86-64\)"),
    row("dsweep/README: the shares and the plan's table", "results/s10-dsweep-pooled/dsweep-pooled.json; dsweep/PLAN.md",
        lambda: {**exp_ds_words(), **exp_ds_numbers()},
        r"the fixed share is (?P<sac>[\d.]+) as compiled and (?P<sal>[\d.]+) aligned, both above 1, so the result is not a mixture\. FAST adds (?P<ex>\d+) extra "
        r"instructions per inner call at every size with d = (?P<r>\d) mod (?P<m>\d) from (?P<d0>\d+) to (?P<d1>\d+) .*? "
        r"\(R\(12\) = (?P<pr>[\d.]+) under H1; (?P<obs>[\d.]+) observed\)"),
    row("dsweep/README: the temporary branch", "results/s10-dsweep-run-*/dsweep-job-*/dsweep.json run.commit", exp_smoke_branch,
        r"`dsweep-smoke` \(commit (?P<c>[0-9a-f]+)\)"),
    row("dsweep/README: the smoke runs", "harness/criteria-v3.json timing.reps_per_side", exp_ds_overview,
        r"fewer repetitions per side than the (?P<reps>\d+) of `harness/criteria-v3\.json`"),
]

# ---- the provenance, caveat and verdict sentences ----------------------------------------------------
# A caveat or a verdict word is not a measured number, so the rows below do two things. Where the sentence states something the
# data hold (a count, a verdict word, a model, a run id) its groups are compared with the data like any other row. Where it states
# a limit or an order of events, the row has no group and fixes that the sentence is still there in these words: reworded,
# reversed or deleted, it fails here by name. The verdict words come from replication/results.json and site/data/dsweep.json.

def prov():
    """tests/data/s9_s10_provenance.json: the commit times and branch facts the provenance sentences rest on (a record of what was read)."""
    path = os.environ.get("PROVENANCE_PATH")  # redirected only by the tamper tests
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return J("tests/data/s9_s10_provenance.json")


def utc(iso):
    return datetime.datetime.fromisoformat(iso).astimezone(datetime.timezone.utc).replace(tzinfo=None)


def pick(values, *keys):
    return {k: values[k] for k in keys}


def lf_sha(rel):
    with open(os.path.join(REPO, rel), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def exp_prov_dsweep():
    """What the d-sweep sentences say about order and dispatch, checked against the provenance record and the stored run records."""
    p = prov()
    plan, code, pub, br = p["dsweep_plan"], p["dsweep_code"], p["dsweep_public"], p["dsweep_branch"]
    first = min(start_times(S10_JOBS))
    assert plan["files"] == ["dsweep/PLAN.md"], "the plan commit is no longer recorded as holding the plan alone"
    assert utc(plan["author_date"]) < utc(code["author_date"]), "the record puts the plan commit after the code commit"
    assert utc(code["author_date"]) < first, "the record puts the code commit after the first d-sweep job started"
    assert "dsweep/PLAN.md" not in code["added"], "the code commit is recorded as holding the plan"
    assert {"dsweep/PLAN.md", "dsweep/analyze.py", "dsweep/sweep.py", ".github/workflows/dsweep.yml"} <= set(pub["paths_in_that_commit"]), (
        "the record no longer shows the plan arriving in the same public commit as the code")
    assert utc(pub["date"]) <= first, "the first public commit of the plan and code is recorded after the first job started"
    public_plan = J(RUN_LINKS)["dsweep_plan_in_public_commit"]
    assert public_plan["commit"] == pub["first_commit_with_plan_and_code"], "the public commit with the plan is not the one the record names"
    assert public_plan["plan_sha256"] == ds()["plan_sha256"] == lf_sha("dsweep/PLAN.md"), (
        "the plan in the public commit, the plan the result files store and dsweep/PLAN.md are not the same file")
    minutes = (first - utc(pub["date"])).total_seconds() / 60
    assert 8.5 <= minutes < 9.5, f"the public plan is dated {minutes:.1f} minutes before the first job start; the texts say about 9"
    assert ds()["plan_sha256"] == lf_sha("dsweep/PLAN.md"), "dsweep/PLAN.md differs from the plan the pooled d-sweep file was made under"
    commit = short_commit(S10_JOBS)
    assert br["commit"].startswith(commit), f"the d-sweep job records name {commit}, the record names {br['commit'][:7]}"
    assert sorted(br["workflow_files"]) == ["ci.yml", "dsweep.yml"], f"the branch holds {br['workflow_files']}"
    path = os.path.join(REPO, ".github", "workflows", "dsweep.yml")
    assert os.path.exists(path), "the tree has no .github/workflows/dsweep.yml"
    with open(path, encoding="utf-8") as f:
        assert f.readline().strip() == "name: " + br["ci_yml_workflow_name"], "the d-sweep workflow in this tree has another name than the one run as ci.yml"
    return {"br": br["branch"], "c": commit, "f": "ci.yml", "g": "dsweep.yml", "pub": pub["first_commit_with_plan_and_code"],
            "t1": utc(pub["date"]).strftime("%H:%M"), "t2": first.strftime("%H:%M"), "m": str(round(minutes))}


def exp_prov_dsweep_none():
    exp_prov_dsweep()
    return {}


LONG_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
RECORDS_BEFORE_PUBLIC_HISTORY = ("results/s1-run-*/results.json", "results/s2-run-*/results.json", "results/s3-run-*/results-*/results.json",
                                 "results/s3-audit-run-*/results-*/results.json", "results/s4-run-*/results-*/results.json",
                                 "results/s4-smoke-*/results-*/results.json", "results/s5-holdout/runs/*/results-*/results.json",
                                 "results/mitigate-run-*/mitigate-*/results.json")
RECORDS_AFTER_PUBLIC_HISTORY = ("results/s6-run-*/results-*/results.json", "results/s7-run-*/results-*/results.json", S8_ARM_JOBS, S9_ARM_JOBS, S9_X86_JOBS)


def record_start(doc):
    return (doc["run"] if isinstance(doc.get("run"), dict) else doc)["started_at"]


def exp_public_history():
    """The date the public history begins (tests/data/s9_s10_provenance.json, read from the GitHub API), checked against the records: every record of s1 to s4,
    the holdout and the rewrite started before the first public commit and every record of s6 to s10 after it; and the public commits that the records of s6,
    s7 and s9 name hold the rule file as it is now (the blob hash in the fixture is the hash of harness/criteria-v3.json)."""
    ph, rf = prov()["public_history"], prov()["rule_file_in_public_commits"]
    begin = ph["author_date"]
    before = [record_start(d) for pat in RECORDS_BEFORE_PUBLIC_HISTORY for d in job_records(pat)]
    after = [record_start(d) for pat in RECORDS_AFTER_PUBLIC_HISTORY for d in job_records(pat)] + [record_start(d) for d in job_records(S10_JOBS)]
    assert len(before) == 92 and max(before) < begin < min(after), (
        f"the public history begins at {begin}; the records of the earlier runs ({len(before)}) end {max(before)}, those of the later runs start {min(after)}")
    with open(os.path.join(REPO, rf["file"]), "rb") as f:
        raw = f.read().replace(b"\r\n", b"\n")
    assert hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == rf["git_blob_sha1"], f"{rf['file']} is not the file the public commits hold"
    stamped = {d["run"]["commit"][:7] for pat in (RECORDS_AFTER_PUBLIC_HISTORY[0], RECORDS_AFTER_PUBLIC_HISTORY[1], S9_ARM_JOBS, S9_X86_JOBS) for d in job_records(pat)}
    assert stamped and stamped <= set(rf["commits"]), f"the records of s6, s7 and s9 name {sorted(stamped)}; the fixture lists the public commits {rf['commits']}"
    day = ph["author_date"]
    return {"d": f"{int(day[8:10])} {LONG_MONTHS[int(day[5:7]) - 1]} {day[:4]}"}


def exp_prov_replication():
    """What the replication sentences say about the plan's order and the dispatch: the gap between the plan commit and the earliest
    recorded job start, the commit the runs name, and that no public record or run-time record carries the plan."""
    p = prov()
    plan, disp = p["replication_plan"], p["replication_dispatch"]
    ts = start_times(S9_ARM_JOBS, S9_X86_JOBS)
    gap = (min(ts) - utc(plan["author_date"])).total_seconds()
    assert plan["files"] == ["replication/PLAN.md"], "the replication plan commit is no longer recorded as holding the plan alone"
    assert 0 < gap < 60 and gap == int(gap), f"the plan commit is {gap} s before the earliest job start; the text says a whole number of seconds under a minute"
    lag = exp_start_lag()
    assert int(lag["lo"]) <= gap <= int(lag["hi"]), (
        f"the plan commit is {gap} s before the earliest job start, outside the {lag['lo']} to {lag['hi']} s the Arm runs took from creation to first start: "
        "the texts say the margin lies inside that lag")
    commit = short_commit(S9_ARM_JOBS, S9_X86_JOBS)
    assert disp["commit"].startswith(commit), f"the s9 job records name {commit}, the record names {disp['commit']}"
    assert disp["plan_in_public_history_at_that_commit"] is False, "the record says the plan was public at the commit the runs were dispatched from"
    assert lf_sha("replication/PLAN.md") == repl()["plan_sha256"], "replication/PLAN.md differs from the plan the comparison was built with"
    for d in job_records(S9_ARM_JOBS) + job_records(S9_X86_JOBS):
        assert "plan_sha256" not in d and "plan_sha256" not in d["run"], "a replication job record now carries the plan hash"
    dsj = job_records(S10_JOBS)
    assert len(dsj) == 18 and all(d["plan_sha256"] == lf_sha("dsweep/PLAN.md") for d in dsj), "not every d-sweep result file stores the hash of its plan"
    return {"sec": str(int(gap)), "n": str(len(ts)), "c": commit, **lag}


def exp_sweep_floor():
    """The d-sweep on EPYC 7763, as compiled: matrix multiply costs less than the headline's lower end at the smallest sizes, so 2.8x is not a floor
    for these loops; the sizes quoted and the 7763's L1d come from the pooled file and the job records."""
    c = ds_cpu("7763")
    ac = ds_rows(c, "as_compiled")
    page = repl()["x86"]["headline"]["page_range"]
    kib = {j["run"]["runner"]["l1d_kib"] for j in job_records(S10_JOBS) if "7763" in j["run"]["runner"]["cpu_model"]}
    assert len(kib) == 1, f"the EPYC 7763 d-sweep jobs report these L1d sizes: {sorted(kib)}"
    kib = kib.pop()
    l1_d = c["ladder"]["study_l1_d"]
    assert (l1_d, 12, 76) == (36, 12, 76) and all(d in ac for d in (12, 20, 36, 76)), "the d-sweep rows of EPYC 7763 changed"
    assert ac[12]["ratio"] < page["min"] and ac[20]["ratio"] < page["min"], "the smallest d-sweep sizes are no longer under the headline's lower end"
    assert ac[l1_d]["working_set_bytes"] <= kib * 1024 < ac[76]["working_set_bytes"], "d = 76 is no longer the first size past the 7763's L1d"
    return {"d12": "12", "r12": f1(ac[12]["ratio"]), "d36": str(l1_d), "r36": f1(ac[l1_d]["ratio"]), "d76": "76", "r76": f1(ac[76]["ratio"]), "kib": str(kib),
            "pm": page["printed_min"], "ph": page["printed_max"]}


def set_model_jobs(pattern):
    """CPU model -> jobs, counted from the job records of one replication set (run.runner.cpu_model)."""
    out = {}
    for d in job_records(pattern):
        m = d["run"]["runner"]["cpu_model"]
        out[m] = out.get(m, 0) + 1
    return out


def exp_model_job_counts():
    """The per-model job counts the limits paragraph of DETAILS.md types, from the job records of both sets, checked against the
    comparison file; plus the sizes of the pools and the 6973P-C counts."""
    b, c = set_model_jobs(S9_ARM_JOBS), set_model_jobs(S9_X86_JOBS)
    for arch, counts in (("arm", b), ("x86", c)):
        for m in repl()[arch]["models"]:
            assert m["replication"]["jobs"] == counts.get(m["cpu_model"], 0), f"{m['cpu_model']}: the comparison file and the job records disagree on its jobs in the set"
        assert sum(counts.values()) == repl()["pools"][arch]["replication"]["jobs"]
    c8370 = next(v for k, v in c.items() if "8370C" in k)
    v3 = next(v for k, v in b.items() if "Neoverse-V3" in k)
    assert not any("Neoverse" in k for k in c), "set C now has an Arm job"
    assert not any("8370C" in k for k in b), "set B now has a Xeon job"
    u = exp_repl_untested()
    return {"rj": u["rj"], "mn": u["mn"], "p95": exp_repl_sets()["p95"], "sj": u["sj"], "sf": u["sf"], "j8": str(c8370), "jv": str(v3)}


def exp_ds_flags_none():
    exp_ds_flags()
    return {}


def exp_h2_rejected():
    """On Neoverse-N2 the fixed share of both columns lies, interval and all, above the H2 band: H2 is rejected in both."""
    c = ds_cpu(N2)
    band = ds()["rule"]["h2_share_band"]
    for column in ("as_compiled", "aligned"):
        lo, hi = c["columns"][column]["excess"]["share_ci95"]
        assert lo > band[1], f"{column}: the fixed share's interval [{lo}, {hi}] is no longer wholly above the H2 band {band}"
    return {"h": "H2"}


def exp_registered_word_neither():
    c = ds_cpu(N2)
    assert c["verdict"]["columns_agree"] is False
    return {"w": c["verdict"]["word"]}


def exp_arm_majority_word():
    """The word the whole Arm analysis gives under most of the 400 other seeds (arm64/seed-sensitivity.json): MAP."""
    s = exp_arm_seed_whole()
    assert int(s["map"]) > int(s["inc"]), "most of the other seeds no longer give MAP"
    return "MAP"


def exp_ds_flags():
    """What every d-sweep job record says about the toolchain and the flags: one clang, one libc++, -O2, FAST against NONE, and the
    alignment flag of the aligned pair; the numbers are returned as the docs type them."""
    recs = job_records(S10_JOBS)
    assert len(recs) == 18
    aligned = set()
    for d in recs:
        b = d["builds"]
        assert sorted(b) == ["fast", "fast_a64", "none", "none_a64"], f"a d-sweep job builds {sorted(b)}"
        for k, v in b.items():
            cmd = v["command"]
            assert cmd.startswith("clang++-18 -O2 ") and "-stdlib=libc++" in cmd, f"{k}: {cmd}"
            assert ("_LIBCPP_HARDENING_MODE_FAST" if k.startswith("fast") else "_LIBCPP_HARDENING_MODE_NONE") in cmd
            m = re.search(r"-falign-loops=(\d+)", cmd)
            assert bool(m) == k.endswith("_a64"), f"{k}: the alignment flag is on the wrong builds"
            if m:
                aligned.add(m.group(1))
    clang = {d["run"]["toolchain"]["clang"] for d in recs}
    lib = {d["run"]["toolchain"]["libcxx_package"] for d in recs}
    assert len(aligned) == len(clang) == len(lib) == 1, "the d-sweep jobs name more than one toolchain or alignment"
    cv = re.search(r"clang version ([\d.]+)", clang.pop()).group(1)
    lv = re.search(r"libc\+\+-(\d+)-dev", lib.pop()).group(1)
    arm_jobs_n = sum(1 for d in recs if d["run"]["runner"]["cpu_model"] == N2)
    return {"al": aligned.pop(), "cl": cv, "lc": lv, "four": word(len(recs[0]["builds"])), "six": word(arm_jobs_n), "one": word(len(ds_cpu(N2)["runs"])),
            "mn": str(ds()["rule"]["minimum_jobs"]), "w7": ds_cpu("7763")["verdict"]["word"]}


def test_the_job_counts_of_set_b_and_set_c_by_model():
    """Set B drew 29 Neoverse-N2 and 1 Neoverse-V3 jobs; set C drew 19 EPYC 7763, 5 EPYC 9V45, 7 EPYC 9V74, 7 Xeon Platinum 8573C and 1
    each of the Xeon 6973P-C and the Xeon Platinum 8370C (DETAILS.md types the one-job models and the README the 29 and the 1)."""
    b, c = set_model_jobs(S9_ARM_JOBS), set_model_jobs(S9_X86_JOBS)
    assert b == {N2: 29, V3: 1}, b
    assert c == {"AMD EPYC 7763 64-Core Processor": 19, "AMD EPYC 9V45 96-Core Processor": 5, "AMD EPYC 9V74 80-Core Processor": 7,
                 "INTEL(R) XEON(R) PLATINUM 8573C": 7, "Intel(R) Xeon(R) 6973P-C": 1, "Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz": 1}, c
    assert sum(b.values()) == 30 and sum(c.values()) == 40


def exp_prov_replication_pick(*keys):
    return lambda: pick(exp_prov_replication(), *keys)


def exp_pool_check():
    """The two red set-C combine runs and the rule that replaced the sampling of one-job models, from the provenance record, the
    pooled files of the red runs and harness/criteria-v3.json."""
    p = prov()["replication_combine_runs"]
    runs = repl()["pools"]["x86"]["replication"]["runs"]
    assert sorted(p["red"] + p["green"]) == sorted(runs) and len(p["red"]) == 2 and len(runs) == 4, "the record does not split the four set-C runs two and two"
    mn = J("harness/criteria-v3.json")["v3"]["pooling"]["minimum_jobs"]
    assert mn == repl()["criteria"]["minimum_jobs"], "the comparison and the criteria name different minimums"
    cells = p["failing_cells"]
    assert [c["run"] for c in cells] == p["red"], "the failing cells are not those of the two red runs"
    assert [(c["cell_id"], c["column"]) for c in cells] == [("k08_matmul.L1", "as_compiled"), ("k03_stencil.L1", "as_compiled")]
    assert "6973P-C" in cells[0]["cpu_model"] and "9V74" in cells[1]["cpu_model"], "the failing models are no longer the Xeon 6973P-C and the EPYC 9V74"
    jobs = []
    for c in cells:
        b = next(b for b in J(f"results/s9-run-{c['run']}/pooled.json")["cpus"] if b["cpu_model"] == c["cpu_model"])
        cell = next(x for x in b["cells"] if x["cell_id"] == c["cell_id"])
        assert b["jobs"] == c["jobs"] < mn and cell[c["column"]]["jobs"] == c["jobs"], (
            f"run {c['run']}: {c['cpu_model']} does not have {c['jobs']} job(s), fewer than the minimum of {mn}, in its pooled file")
        jobs.append(c["jobs"])
    assert jobs == [1, 2], "the two failing models no longer have one and two jobs"
    return {"two": word(len(p["red"])), "four": word(len(runs)), "r1": p["red"][0], "r2": p["red"][1], "mn": str(mn), "j1": str(jobs[0]), "j2": str(jobs[1]),
            "o1": word(jobs[0]), "o2": word(jobs[1])}


def exp_plan_item(startswith, must_contain):
    """The number of the plan item whose text starts with `startswith` (replication/PLAN.md), after checking it says `must_contain`."""
    with open(os.path.join(REPO, "replication", "PLAN.md"), encoding="utf-8") as f:
        items = re.findall(r"^(\d+)\. (.*)$", f.read(), re.M)
    hits = [(n, t) for n, t in items if t.startswith(startswith)]
    assert len(hits) == 1 and must_contain in hits[0][1], f"the plan has no single item that starts '{startswith}' and says '{must_contain}'"
    return hits[0][0]


def exp_repl_arm_close():
    """The Arm replication cell sits close to its limit in both sets, and the word repeated."""
    a = exp_repl_arm()
    lim = float(a["lim"])
    assert abs(float(a["ha"]) - lim) < 0.01 and abs(float(a["hb"]) - lim) < 0.01, "the Arm cell is no longer within 0.01 of the limit in both sets"
    assert a["fa"].upper() == a["fb"].upper(), "set B and set A no longer give the same word"
    return {"lim": a["lim"], "fb": a["fb"]}


README_GUARD_ROWS = [
    row("d-sweep: H2 is rejected in both Arm columns (README)", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns share_ci95; rule.h2_share_band", exp_h2_rejected,
        r"On Arm (?P<h>H2) is rejected in both columns\."),
    row("d-sweep: the registered word stays and no further runs will be made (README)", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 verdict", exp_registered_word_neither,
        r"A setup cost before the NEON loop is consistent with this; the registered word is still \"(?P<w>\w+)\", and no further runs will be made\."),
    row("d-sweep: caveats, one Arm run and the alignment flag (README)", "results/s10-dsweep-pooled/dsweep-pooled.json placement; the s10 job records builds and run.toolchain",
        lambda: {**pick(exp_ds_flags(), "one", "six", "al"), **pick(exp_ds_caveats(), "s", "n")},
        r"\*\*Caveats\.\*\* Arm is (?P<one>one) run of (?P<six>six) near-identical jobs, so its intervals cannot show run-to-run or host-to-host spread; "
        r"`-falign-loops=(?P<al>\d+)` moves every loop on Arm \((?P<s>\d+) of the (?P<n>\d+) sizes are flagged placement-sensitive\), so the aligned column is not a "
        r"pure placement control; no hardware counters were read\."),
    row("sizes: the headline range is for the study's sizes and 2.8x is not a floor (README)", "results/s10-dsweep-pooled/dsweep-pooled.json EPYC 7763 as_compiled rows; replication/results.json x86 headline; job records run.runner.l1d_kib",
        exp_sweep_floor,
        r"\*\*Sizes\.\*\* The (?P<pm>[\d.]+)x to (?P<ph>[\d.]+)x is for the study's sizes\. On EPYC 7763 the matrix-multiply sweep gives, as compiled, (?P<r12>[\d.]+)x at "
        r"d = (?P<d12>\d+), (?P<r36>[\d.]+)x at d = (?P<d36>\d+) \(the study's L1 size\) and (?P<r76>[\d.]+)x at d = (?P<d76>\d+) \(past its (?P<kib>\d+) KiB L1d\), "
        r"so (?P=pm)x is not a floor for these loops\."),
    row("replication: the plan's order rests on an unpublished commit time (README)", "tests/data/s9_s10_provenance.json; the s9 job records run.started_at, run.commit; replication/results.json plan_sha256",
        exp_prov_replication_pick("sec", "lo", "hi", "c"),
        r"so two replication sets were planned in \[replication/PLAN\.md\]\(replication/PLAN\.md\) \(the plan's commit time in the author's unpublished development "
        r"history is (?P<sec>\d+) seconds before the first job's recorded start, and the harness started (?P<lo>\d+) and (?P<hi>\d+) seconds after dispatch in the two "
        r"Arm runs of Oct 16 that did not queue, so that margin lies inside the lag and the order of plan and dispatch cannot be established from the records; no "
        r"public record shows it, and the plan's hash in `replication/results\.json` is computed when the comparison is built, so it shows the file is unchanged, not "
        r"when it was written\): set B, .*? both dispatched from the default branch at commit (?P<c>[0-9a-f]+)\."),
    row("replication: the two red combine jobs and the checker's sampling rule (README)", "tests/data/s9_s10_provenance.json; the pooled files of the red runs; harness/criteria-v3.json",
        lambda: pick(exp_pool_check(), "two", "four", "mn", "o1", "o2"),
        r"(?P<two>Two) of the (?P<four>four) set-C combine jobs ended red on `harness/pool_check\.py`, on a model with fewer than (?P<mn>\d+) jobs "
        r"\((?P<o1>one) job in one run, (?P<o2>two) in the other\); the checker now samples only models with (?P=mn) or more jobs \(the minimum for a verdict\), "
        r"no verdict uses a model with fewer, and the pooled files and the rules are unchanged: only that check's sampling rule changed\."),
    row("replication: a second INCONCLUSIVE on a cell close to its limit is a weak repeat (README)", "replication/results.json arm models",
        exp_repl_arm_close,
        r"The cell sits close to the (?P<lim>[\d.]+) limit in both sets, so a second (?P<fb>[A-Z]+) is a weak repeat of the word and not strong evidence for it\."),
    row("d-sweep: the plan's history and what it does not show (README)",
        "tests/data/s9_s10_provenance.json; tests/data/run_links_and_commits.json; the s10 records; the stored plan hash",
        lambda: pick(exp_prov_dsweep(), "pub", "br", "t1", "m", "t2"),
        r"It was drafted before the sweep code, revised while the code was written and once more after a review that changed the deciding statistic, and committed "
        r"alone, before the code commit and the first run, in the author's unpublished development history; its hash, stored in every result file, shows that it did "
        r"not change after the runs\. That order cannot be checked from public records; what the public repository holds is the plan file, byte for byte the one "
        r"here, in commit (?P<pub>[0-9a-f]+) on the temporary public branch `(?P<br>dsweep-smoke)`, dated (?P<t1>\d\d:\d\d) UTC, about (?P<m>\d+) minutes before the "
        r"first job's recorded start \((?P<t2>\d\d:\d\d) UTC\) and together with the code, so whether the plan was written before the code is not observable there\."),
    row("d-sweep: where the runs were dispatched from, in the folder map", "tests/data/s9_s10_provenance.json; the s10 records run.commit; the stored plan hash",
        lambda: pick(exp_prov_dsweep(), "br", "c", "f"),
        r"its plan \(committed alone before the code and any run, in the author's unpublished development history, and unchanged since\), code and workflow \(runs `s10-dsweep-run-\*`, "
        r"pooled in `s10-dsweep-pooled`\), dispatched from the temporary public branch `(?P<br>dsweep-smoke)` \(commit (?P<c>[0-9a-f]+)\), where the d-sweep workflow "
        r"is the file `(?P<f>ci\.yml)` \(only a workflow already on the default branch can be dispatched\); the branch is kept because the run records name that commit\."),
    row("replication: the inside count is descriptive", "the sentence, as worded", lambda: {},
        r"The count is descriptive: a new pooled point carries its own noise, so fewer than 95% of points are expected inside even when nothing has changed\."),
    row("d-sweep: the excess is flat across the L1 boundary and smaller only at the two largest sizes",
        "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns and working sets; job records run.runner.l1d_kib", exp_ds_boundary,
        r"with the excess flat, at the sizes with d = 4 mod 8, from d = (?P<fl>\d+) to d = (?P<last>\d+), across the L1 boundary of the core \(d = (?P<p1>\d+) and (?P<p2>\d+) are past its "
        r"(?P<l1>\d+) KiB L1d\), and smaller again only at d = (?P<q1>\d+) and d = (?P<q2>\d+), which are context and not fitted"),
]

DETAILS_GUARD_ROWS = [
    row("details: d-sweep, H2 is rejected in both Arm columns", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns share_ci95; rule.h2_share_band", exp_h2_rejected,
        r"so the result is not a mixture of the two accounts; (?P<h>H2) is rejected there in both columns\."),
    row("details: d-sweep, the registered word stays and no further runs are planned", "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 verdict", exp_registered_word_neither,
        r"A setup cost before the NEON loop is consistent with the Arm points, and the registered word is \"(?P<w>\w+)\"\. No further runs are planned\."),
    row("details: the limits of the sets, the 6973P-C and the one-job models", "the s9 job records run.runner.cpu_model; replication/results.json; harness/criteria-v3.json",
        exp_model_job_counts,
        r"The Xeon 6973P-C was not tested: set C drew (?P<rj>\d+) job of it \((?P<mn>\d+) are the minimum\), so its borderline MAP in the (?P<p95>\d+)-job pool stands "
        r"or falls with which jobs were drawn, and the (?P<sj>\d+)-job pooled form, (?P<sf>[A-Z]+), answers the question neither way\. The Xeon Platinum 8370C drew "
        r"(?P<j8>\d+) job in set C, and the Neoverse-V3 core (?P<jv>\d+) job in set B\."),
    row("details: stage S9, the run folders", "replication/results.json pools runs", lambda: {"ra": exp_repl_sets()["br"], "rc": exp_repl_sets()["cr"]},
        r"\| `replication/`, `results/s9-arm-run-\*/` \((?P<ra>\d+) runs\), `results/s9-run-\*/` \((?P<rc>\d+) runs\), `results/s9-arm-b-pooled/`"),
    row("details: stage S10, the run folders", "results/s10-dsweep-pooled/dsweep-pooled.json cpus runs",
        lambda: {"n": str(len({r for c in ds()["cpus"] for r in c["runs"]}))},
        r"\| `dsweep/`, `results/s10-dsweep-run-\*/` \((?P<n>\d+) runs\), `results/s10-dsweep-pooled/` \|"),
    row("details: d-sweep, caveats, one Arm run and the alignment flag", "results/s10-dsweep-pooled/dsweep-pooled.json; the s10 job records builds",
        lambda: pick(exp_ds_flags(), "one", "six", "al"),
        r"Neoverse-N2 is (?P<one>one) run of (?P<six>six) near-identical jobs, so its intervals cannot show run-to-run or host-to-host spread\. "
        r"`-falign-loops=(?P<al>\d+)` moves every loop on Arm: "),
    row("details: d-sweep, caveats, counters and compiler", "the s10 job records builds and run.toolchain", exp_ds_flags_none,
        r"No hardware counters were read\. The sweep is one kernel, one compiler and `-O2`\."),
    row("details: the lost-loop range is for the study's sizes", "site/data/index.json page.lost", exp_lost_range,
        r"In cache, at the study's sizes, they ran \*\*(?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x slower\*\* on every x86-64 CPU model drawn"),
    row("details: the d-sweep bears on the headline range; 2.8x is not a floor", "results/s10-dsweep-pooled/dsweep-pooled.json EPYC 7763 as_compiled rows; replication/results.json x86 headline; job records run.runner.l1d_kib",
        lambda: pick(exp_sweep_floor(), "r12", "d12", "r36", "d36", "r76", "d76", "kib", "pm"),
        r"It also bears on the headline range: on EPYC 7763, as compiled, matrix multiply costs (?P<r12>[\d.]+)x at d = (?P<d12>\d+), (?P<r36>[\d.]+)x at d = (?P<d36>\d+) "
        r"\(the study's L1 size\) and (?P<r76>[\d.]+)x at d = (?P<d76>\d+) \(past its (?P<kib>\d+) KiB L1d\), so (?P<pm>[\d.]+)x is not a floor for these loops and the "
        r"range holds at the study's sizes\."),
    row("details: replication, the plan's order rests on an unpublished commit time", "tests/data/s9_s10_provenance.json; the s9 job records run.started_at; replication/results.json plan_sha256",
        exp_prov_replication_pick("sec", "lo", "hi", "wait"),
        r"committed in the author's unpublished development history (?P<sec>\d+) seconds before the first job's recorded start; the harness started (?P<lo>\d+) and "
        r"(?P<hi>\d+) seconds after dispatch in the two Arm runs of Oct 16 that did not queue \(the third waited (?P<wait>\d+) seconds\), so that margin lies inside the "
        r"lag and the order of plan and dispatch cannot be established from the records, and no public record shows it; the plan's hash in `replication/results\.json` "
        r"is computed when the comparison is built, so it shows the file is unchanged, not when it was written;"),
    row("details: replication, the sets were dispatched from the default branch", "the s9 job records run.commit", exp_prov_replication_pick("c"),
        r"all dispatched from the default branch at commit (?P<c>[0-9a-f]+)\. Each is pooled alone"),
    row("details: replication, a second INCONCLUSIVE on a cell close to its limit is a weak repeat", "replication/results.json arm models", exp_repl_arm_close,
        r"The cell sits close to the (?P<lim>[\d.]+) limit in both sets, so a second (?P<fb>[A-Z]+) is a weak repeat of the word and not strong evidence for it\."),
    row("details: replication, the two red combine jobs and the checker's sampling rule", "tests/data/s9_s10_provenance.json; the pooled files of the red runs; harness/criteria-v3.json",
        lambda: pick(exp_pool_check(), "two", "four", "r1", "r2", "mn", "j1", "j2"),
        r"\*\*The combine step\.\*\* (?P<two>Two) of the (?P<four>four) set-C combine jobs \(runs (?P<r1>\d+) and (?P<r2>\d+)\) ended red on `harness/pool_check\.py`, which "
        r"disagreed with the pooled file on a model with fewer than (?P<mn>\d+) jobs \(run (?P=r1): the Xeon 6973P-C, (?P<j1>\d+) job, matrix multiply at L1, as compiled; "
        r"run (?P=r2): the EPYC 9V74, (?P<j2>\d+) jobs, the stencil at L1, as compiled\)\. The checker now samples only models with (?P=mn) or more jobs, the minimum "
        r"for a verdict; no verdict uses a model with fewer, the pooled files and the rules are unchanged, and only that check's sampling rule changed\."),
    row("details: stage S9, the plan's commit time and the dispatch commit", "tests/data/s9_s10_provenance.json; the s9 job records run.commit, run.started_at",
        exp_prov_replication_pick("sec", "c"),
        r"planned in writing \(`replication/PLAN\.md`, committed in the author's unpublished development history (?P<sec>\d+) seconds before the first job's recorded "
        r"start; the order of plan and dispatch cannot be established from the records\): set B .*? both dispatched from the default branch at commit (?P<c>[0-9a-f]+); "),
    row("details: the follow-up list calls the replication order unestablished", "tests/data/s9_s10_provenance.json; the s9 job records run.started_at",
        exp_prov_replication_pick("sec"),
        r"planned in writing \(the plan's commit time, in the author's unpublished development history, is (?P<sec>\d+) seconds before the first job's recorded start, inside the dispatch lag, so "
        r"the order cannot be established\), pooled alone"),
    row("details: the folder map, the replication plan is in the author's unpublished development history", "tests/data/s9_s10_provenance.json; the s9 job records run.started_at",
        exp_prov_replication_pick("sec"),
        r"replication/ +the plan for replication sets B and C \(committed in the author's unpublished development history, (?P<sec>\d+) seconds before the first job's recorded start\), compare\.py"),
    row("details: d-sweep, the plan's history and what it does not show",
        "tests/data/s9_s10_provenance.json; tests/data/run_links_and_commits.json; the s10 records; the stored plan hash",
        lambda: pick(exp_prov_dsweep(), "pub", "br", "t1", "m", "t2"),
        r"plan `dsweep/PLAN\.md`, drafted before the sweep code, revised while the code was written and tested and once more after a review of the plan and the code "
        r"\(the review changed the deciding statistic\), and committed alone, before the code commit and before the first run, in the author's unpublished development "
        r"history: its sha256 is stored in every result file, which shows that it did not change after the runs, and `dsweep/analyze\.py` treats a file with another "
        r"hash as a file problem\. That order cannot be checked from that history, which is not published\. What the public repository holds is the plan file, byte for "
        r"byte the one here, in commit (?P<pub>[0-9a-f]+) on the temporary branch `(?P<br>dsweep-smoke)`, dated (?P<t1>\d\d:\d\d) UTC, about (?P<m>\d+) minutes before the "
        r"first job's recorded start \((?P<t2>\d\d:\d\d) UTC\) and in the same commit as the code, so whether the plan was written before the code is not observable there\)"),
    row("details: d-sweep, where the runs were dispatched from", "tests/data/s9_s10_provenance.json; the s10 records run.commit; .github/workflows/dsweep.yml",
        lambda: pick(exp_prov_dsweep(), "br", "c", "f", "g"),
        r"They were dispatched from the temporary public branch `(?P<br>dsweep-smoke)` at commit (?P<c>[0-9a-f]+), where the workflow file is named `(?P<f>ci\.yml)` "
        r"\(a dispatchable workflow must already exist on the default branch; in this tree it is `\.github/workflows/(?P<g>dsweep\.yml)`\); the branch is kept because "
        r"the run records name that commit:"),
    row("details: stage S10, the plan's history and the branch", "tests/data/s9_s10_provenance.json; the s10 records run.commit",
        lambda: pick(exp_prov_dsweep(), "c", "f"),
        r"`dsweep/PLAN\.md` committed alone before the sweep code and before any run, in the author's unpublished development history \(it reached this repository "
        r"in one commit with the code\); .*?dispatched from the temporary public branch `dsweep-smoke` \(commit (?P<c>[0-9a-f]+), where the workflow file is named "
        r"`(?P<f>ci\.yml)`\)"),
    row("details: replication, the inside count is the pool.py test, in both columns", "harness/pool.py reproduction(); replication/compare.py", lambda: {},
        r"The plan asked whether the new pooled aligned ratio lies inside the earlier interval\. The counts above compare each new pooled ratio, in both columns "
        r"\(as compiled and aligned\), with the earlier pool's 95% interval: the point-inside-interval test of `harness/pool\.py` `reproduction\(\)`, which the page "
        r"already applies run against run\. That form was written into `replication/compare\.py` after the sets' data were in, so aligned alone is printed beside it"),
    row("details: replication, the inside count is descriptive and prints no null", "the sentence, as worded", lambda: {},
        r"The count is descriptive: a new pooled point carries its own noise, so fewer than 95% of points are expected inside even when nothing has changed, "
        r"and the share mostly follows interval width and set size\. No expectation under \"no change\" is printed or claimed\."),
    row("details: d-sweep, the aligned column is H1 and still falls at the two largest sizes; flat across the L1 boundary",
        "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 columns, working sets and rule; job records run.runner.l1d_kib",
        lambda: {**exp_ds_boundary(), **exp_ds_words(), **exp_ds_overview()},
        r"The aligned column is H1 by the rule \(fixed share (?P<sal>[\d.]+), inside (?P<h1lo>[\d.]+) to (?P<h1hi>[\d.]+)\), yet its excess also falls at "
        r"d = (?P<q1>\d+) and d = (?P<q2>\d+)\. d = (?P<p1>\d+) and d = (?P<p2>\d+) are past the L1 size of the core \((?P<l1>\d+) KiB L1d: (?P<w76>[\d,]+) B and "
        r"(?P<w108>[\d,]+) B\), so the excess is flat across the L1 boundary and smaller only at d = (?P<q1b>\d+) and d = (?P<q2b>\d+), which are context and not fitted"),
]

REPLICATION_GUARD_ROWS = [
    row("replication/README: the plan was committed in the author's unpublished development history and its hash is not a time", "tests/data/s9_s10_provenance.json; the s9 and s10 job records; replication/results.json plan_sha256",
        exp_prov_replication_pick("sec", "n", "lo", "hi", "wait", "c"),
        r"committed in the author's unpublished development history (?P<sec>\d+) seconds before the earliest job start recorded in the (?P<n>\d+) job records "
        r"\(`run\.started_at`; the commit time is from the author's machine and the start time from the runner, and the two clocks were not compared\)\. A run's first "
        r"recorded start comes some seconds after the run is dispatched: in the two Arm runs of Oct 16 that started at once it was (?P<lo>\d+) and (?P<hi>\d+) seconds "
        r"after the run was created \(`tests/data/s8_arm_timeline\.json`\), and the third waited (?P<wait>\d+) seconds\. The (?P=sec)-second margin lies inside that lag, "
        r"so the order of the plan commit and the dispatch cannot be established from the records\. The public "
        r"repository did not hold the file at commit (?P<c>[0-9a-f]+), the commit the runs were dispatched from, and no public record shows the order\. A hash shows "
        r"that a file is unchanged, not when it was written: the hash in `results\.json` is computed by `compare\.py` when the comparison is built, after the data "
        r"were in, and the per-job records do not carry it\. So the sets are described as planned, with the order unestablished, on commit times a reader of this "
        r"repository cannot check, and not as a pre-registration\. The d-sweep is better placed: every one of its result files stores the hash of its plan\."),
    row("replication/README: the status line and the plan bullet name the unpublished history", "the sentences, as worded", lambda: {},
        r"planned in writing \(the order of plan and dispatch cannot be established from the records; see \"What the plan does and does not show\"\)"),
    row("replication/README: the plan bullet", "the sentence, as worded", lambda: {},
        r"`PLAN\.md`: the plan, committed in the author's unpublished development history within seconds of the dispatch\. It fixes .*? Its sha256 is stored in "
        r"`results\.json`, where `compare\.py` computes it when it builds that file\."),
    row("replication/README: the two red combine jobs and the checker's sampling rule", "tests/data/s9_s10_provenance.json; the pooled files of the red runs; harness/criteria-v3.json",
        lambda: pick(exp_pool_check(), "two", "four", "r1", "r2", "mn", "j1", "j2"),
        r"(?P<two>Two) of the (?P<four>four) set-C combine jobs \(runs (?P<r1>\d+) and (?P<r2>\d+)\) ended red on `harness/pool_check\.py`, which disagreed with the "
        r"pooled file on a model with fewer than (?P<mn>\d+) jobs \(run (?P=r1): the Xeon 6973P-C, (?P<j1>\d+) job, matrix multiply at L1, as compiled; run (?P=r2): "
        r"the EPYC 9V74, (?P<j2>\d+) jobs, the stencil at L1, as compiled; the two other combine jobs passed\)\. The checker now samples only models with (?P=mn) or "
        r"more jobs, the minimum for a verdict, and lists the others as skipped\. No verdict uses a model with fewer, the pooled files and the rules are unchanged, and "
        r"only that check's sampling rule changed \(`tests/test_replication\.py` runs the two pooled files through it\)\."),
    row("replication/README: a second INCONCLUSIVE on a cell close to its limit is a weak repeat", "replication/results.json arm models",
        lambda: pick(exp_repl_arm_close(), "fb"),
        r"The cell sits close to the limit in both sets, so a second (?P<fb>[A-Z]+) is a weak repeat of the word and not strong evidence for it\."),
    row("replication/README: the pooled forms are secondary (plan item)", "replication/PLAN.md items", lambda: {"i": exp_plan_item("Pooled forms", "They are secondary because the sets were requested after a borderline reading")},
        r"so the stopping point depended on the data \(plan, item (?P<i>\d+)\)\."),
    row("replication/README: the inside count", "replication/results.json arm and x86 models inside.points", exp_repl_reproduction,
        r"Arm (?P<aal>\d+) of (?P<aalc>\d+) against (?P<ai>\d+) of (?P<ac>\d+) in both columns, x86-64 (?P<xal>\d+) of (?P<xalc>\d+) against "
        r"(?P<xi>\d+) of (?P<xc>\d+)\. The count is descriptive: a new pooled point carries its own noise, so fewer than 95% of points are expected inside even "
        r"when nothing has changed, and the share mostly follows interval width and set size\. No expectation under \"no change\" is printed or claimed\."),
    row("replication/README: the plan's description of the inside count was wrong", "the sentence, as worded; replication/PLAN.md item 2; site/data/holdout.json", lambda: {},
        r"Plan item 2 asked for the new set's pooled aligned ratio alone, and described the share as \"as in the holdout column of the page\"\. That description is "
        r"wrong: the holdout table's \"Reproduced\" column compares verdict words only\."),
]

DSWEEP_GUARD_ROWS = [
    row("dsweep/README: sweep.py builds four ways", "the s10 job records builds", lambda: pick(exp_ds_flags(), "four", "al"),
        r"`sweep\.py`: builds `kernels/k08_matmul\.cpp` (?P<four>four) ways \(NONE and FAST, each as compiled and with `-falign-loops=(?P<al>\d+)`\)"),
    row("dsweep/README: the minimum number of jobs", "results/s10-dsweep-pooled/dsweep-pooled.json rule.minimum_jobs", lambda: pick(exp_ds_flags(), "mn"),
        r"per CPU model \((?P<mn>\d+) jobs at least\)"),
    row("dsweep/README: the EPYC 7763 word is the one the plan expected", "results/s10-dsweep-pooled/dsweep-pooled.json EPYC 7763 verdict", lambda: pick(exp_ds_flags(), "w7"),
        r"EPYC 7763, where the checked loop loses SIMD, gave (?P<w7>H\d), which the plan expected there; that is all that control says\."),
    row("dsweep/README: what the sweep cannot show", "the s10 job records builds and run.toolchain; results/s10-dsweep-pooled/dsweep-pooled.json",
        lambda: pick(exp_ds_flags(), "cl", "lc", "six", "al"),
        r"One kernel, one compiler \(clang (?P<cl>[\d.]+) with libc\+\+ (?P<lc>\d+), FAST mode\) and `-O2`\. The Arm result is one run of (?P<six>six) jobs on one core "
        r"type that agree closely, so its intervals show no run-to-run or host-to-host spread\. `-falign-loops=(?P<al>\d+)` moves every loop, not only the hot one, "
        r"so the aligned column is not a pure placement control\."),
    row("dsweep/README: the sweep bears on the headline range; 2.8x is not a floor", "results/s10-dsweep-pooled/dsweep-pooled.json EPYC 7763 as_compiled rows; replication/results.json x86 headline; job records run.runner.l1d_kib",
        exp_sweep_floor,
        r"On EPYC 7763, as compiled, matrix multiply costs (?P<r12>[\d.]+)x at d = (?P<d12>\d+), (?P<r36>[\d.]+)x at d = (?P<d36>\d+) \(the study's L1 size\) and "
        r"(?P<r76>[\d.]+)x at d = (?P<d76>\d+) \(past its (?P<kib>\d+) KiB L1d\), so the (?P<pm>[\d.]+)x of \"(?P=pm)x to (?P<ph>[\d.]+)x\" is not a floor for these loops "
        r"and the range holds at the study's sizes\."),
    row("dsweep/README: the plan's history and what it does not show",
        "tests/data/s9_s10_provenance.json; tests/data/run_links_and_commits.json; the s10 records; the stored plan hash",
        lambda: pick(exp_prov_dsweep(), "pub", "br", "t1", "m", "t2"),
        r"drafted before the sweep code, revised while the code was written and tested and once more after a review of the plan and the code \(the review changed "
        r"the deciding statistic; the plan's own \"Changes made before any run\" lists every change\), and committed alone, before the code commit and before the "
        r"first run, in the author's unpublished development history\. .*? The order before the runs cannot be checked from that history, which is not published\. "
        r"What the public repository holds is the plan file, byte for byte the one here, in commit (?P<pub>[0-9a-f]+) on the temporary branch `(?P<br>dsweep-smoke)`, "
        r"dated (?P<t1>\d\d:\d\d) UTC, about (?P<m>\d+) minutes before the first job's recorded start \((?P<t2>\d\d:\d\d) UTC\) and in the same commit as the code, so "
        r"whether the plan was written before the code is not observable there\."),
    row("dsweep/README: where the runs were dispatched from", "tests/data/s9_s10_provenance.json; the s10 records run.commit; .github/workflows/dsweep.yml",
        lambda: pick(exp_prov_dsweep(), "br", "c", "f", "g"),
        r"dispatched from a temporary branch of the public repository, `(?P<br>dsweep-smoke)` \(commit (?P<c>[0-9a-f]+)\).*?On that branch the d-sweep workflow file is "
        r"named `(?P<f>ci\.yml)` \(a dispatchable workflow must already exist on the default branch\); in this tree it is `\.github/workflows/(?P<g>dsweep\.yml)`\. "
        r"The branch is kept because the run records name that commit\."),
    row("dsweep/README: the stored phrase 'the same at every d' means inside the H1 band, not constant",
        "results/s10-dsweep-pooled/dsweep-pooled.json Neoverse-N2 words.aligned.reason and columns", exp_ds_reason,
        r"The stored `reason` of an H1 column ends \"the excess per inner call is (?P<ph>the same at every d)\"\. That phrase is the registered code's wording for "
        r"\"inside the H1 band\" \(a fixed share of (?P<h1lo>[\d.]+) to (?P<h1hi>[\d.]+)\), not a statement that the excess is constant: on Neoverse-N2 the aligned "
        r"column is (?P<wal>H\d) \(fixed share (?P<sal>[\d.]+)\), and its excess, at the sizes with d = 4 mod 8, is (?P<blo>[\d.]+) to (?P<bhi>[\d.]+) ns from d = (?P<d0>\d+) to d = (?P<d1>\d+), "
        r"(?P<b148>[\d.]+) ns at d = 148 and (?P<b209>[\d.]+) ns at d = 209\. `analyze\.py` and the stored files are not changed\."),
]
ARM64_GUARD_ROWS = [
    row("arm64: what this says, the stored verdict and the 2% limit", "replication/results.json arm models; harness/criteria-v3.json forward ceiling",
        lambda: {"fa": exp_repl_arm()["fa"], "pct": f0(round((arm_forward_limit() - 1) * 100))},
        r"The stored verdict is (?P<fa>[A-Z]+) and is kept\. It is not a finding that the forward add costs more than (?P<pct>\d+)% at L2: that cell's interval is "
        r"[\d.]+% either side"),
    row("arm64: what this says, the data cannot separate the two words", "arm64/seed-sensitivity.json full forms; replication/results.json arm models",
        lambda: {"v1": exp_repl_arm()["fa"], "v2": exp_arm_majority_word()},
        r"The data cannot separate (?P<v1>[A-Z]+) from (?P<v2>[A-Z]+) at this cell\."),
    row("arm64: the d-sweep plan was committed before its code and the runs", "tests/data/s9_s10_provenance.json; the s10 records; the stored plan hash",
        exp_prov_dsweep_none,
        r"It chose its own sizes under a plan committed before its code and the runs \(d = "),
]

# ---- order of events, commits, run links and how to rerun -------------------------------------------

def exp_pool_growth():
    """The Xeon 6973P-C through the three kernel pools: absent from the 30-job pool, INCONCLUSIVE with 6 jobs, MAP with 7."""
    pools = {p: {c["cpu_model"]: c for c in J(p)["cpus"]} for p in (POOLED_ORIGINAL, POOLED_S6, POOLED)}
    key = next(k for k in pools[POOLED] if "6973P-C" in k)
    assert key not in pools[POOLED_ORIGINAL], "the 30-job pool now holds the Xeon 6973P-C"
    a, b = pools[POOLED_S6][key], pools[POOLED][key]
    assert (a["jobs"], a["verdict"]["form"], b["jobs"], b["verdict"]["form"]) == (6, "inconclusive", 7, "map"), "the Xeon 6973P-C verdicts of the pools changed"
    original = sum(c["jobs"] for c in pools[POOLED_ORIGINAL].values())
    assert original == len(job_records("results/s4-run-*/results-*/results.json")), "the original pool and the s4 job records disagree on the job count"
    return {"j6": str(a["jobs"]), "f6": a["verdict"]["form"].upper(), "j7": str(b["jobs"]), "f7": b["verdict"]["form"].upper(), "s4": str(original)}


def exp_versions_range():
    """The clang versions of the newer-compiler runs (versions/results/<run>/versions-<N>-*): the lowest and the highest."""
    found = set()
    for d in glob.glob(os.path.join(REPO, "versions", "results", "*", "versions-*")):
        m = re.match(r"versions-(\d+)-", os.path.basename(d))
        if m:
            found.add(int(m.group(1)))
    assert found == {19, 20, 21}, f"the newer-compiler runs hold clang {sorted(found)}; the texts say 19 to 21"
    return {"lo": str(min(found)), "hi": str(max(found))}


def exp_check_exit():
    """README and DETAILS name the final line and the exit code of a run whose page step was skipped; scripts/check.py must say the same."""
    with open(os.path.join(REPO, "scripts", "check.py"), encoding="utf-8") as f:
        src = f.read()
    line = re.search(r'^PASSED_WITH_SKIPS = "([^"]+)"$', src, re.M)
    code = re.search(r"^EXIT_PASSED_WITH_SKIPS = (\d+)$", src, re.M)
    assert line and code, "scripts/check.py no longer defines PASSED_WITH_SKIPS and EXIT_PASSED_WITH_SKIPS"
    assert "ALL CHECKS PASSED" in src and line.group(1) != "ALL CHECKS PASSED"
    return {"line": line.group(1), "code": code.group(1)}


HALF_HOURS_LO = {1: "half an hour", 2: "one", 3: "an hour and a half", 4: "two", 5: "two and a half", 6: "three"}  # the first word of "one to two hours"
HALF_HOURS_HI = {1: "half an hour", 2: "one hour", 3: "an hour and a half", 4: "two hours", 5: "two and a half hours", 6: "three hours",
                 7: "three and a half hours", 8: "four hours"}


def exp_ci_check_duration():
    """README says how long `python scripts/check.py` takes on a CI runner. The typed range must cover the shortest and the longest scripts/check.py step of
    the three most recent successful push runs of the ci workflow (tests/data/ci_check_step.json, read from the GitHub API) and be no wider than the
    half-hour rounding of them: the shortest step to the nearest half hour (55 minutes is "one"), the longest up to the next half hour (95 minutes is
    "two hours"). A range that stops at "one hour" does not cover a 95-minute step; one that runs to "three hours" is wider than any step read."""
    runs = J("tests/data/ci_check_step.json")["runs"]
    assert len(runs) == 3 and len({r["run_id"] for r in runs}) == 3, "the fixture holds three distinct runs"
    when = lambda s: datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))  # noqa: E731
    minutes = [(when(r["completed_at"]) - when(r["started_at"])).total_seconds() / 60 for r in runs]
    assert all(m > 0 for m in minutes), f"step times: {minutes}"
    lo, hi = round(min(minutes) / 30), math.ceil(max(minutes) / 30)
    assert lo in HALF_HOURS_LO and hi in HALF_HOURS_HI, f"steps of {min(minutes):.0f} to {max(minutes):.0f} minutes are outside the words the README can use"
    return {"lo": HALF_HOURS_LO[lo], "hi": HALF_HOURS_HI[hi]}


def exp_font_dependent():
    """README and DETAILS say how many page checks need the web fonts; scripts/check_site.py names them in FONT_DEPENDENT_CHECKS and in its
    docstring, and each name is the start of a check message the script can print."""
    with open(os.path.join(REPO, "scripts", "check_site.py"), encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"^FONT_DEPENDENT_CHECKS = \(([^)\n]*)\)$", src, re.M)
    assert m, "scripts/check_site.py no longer defines FONT_DEPENDENT_CHECKS as a one-line tuple"
    names = re.findall(r'"([^"]+)"', m.group(1))
    assert len(names) == len(set(names)) >= 1, f"FONT_DEPENDENT_CHECKS holds {names}"
    docstring = squash(src.split('"""', 2)[1])
    for n in names:
        assert f'"{n}"' in docstring, f"the docstring of scripts/check_site.py does not name the font-dependent check {n!r} in quotation marks"
    assert "first view" in src and all(n.split(": ", 1)[1] in src for n in names), "a font-dependent check name is no longer in the script"
    return {"two": word(len(names))}


def exp_pages_trigger():
    """DETAILS says pages.yml publishes after the ci workflow succeeds on a push to main, or by hand; .github/workflows/pages.yml must say the same
    (a workflow_run trigger on ci for the main branch, a manual trigger, no push trigger of its own and a success condition)."""
    with open(os.path.join(REPO, ".github", "workflows", "pages.yml"), encoding="utf-8") as f:
        text = f.read()
    on = re.search(r"^on:\n((?:[ \t]+.*\n|\n)+)", text, re.M)
    assert on, ".github/workflows/pages.yml has no `on:` block"
    block = on.group(1)
    assert re.search(r"^  workflow_run:\n(?:    .*\n)*?    workflows: \[(?P<w>[\w.-]+)\]", block, re.M), "pages.yml no longer runs after another workflow"
    w = re.search(r"workflows: \[([\w.-]+)\]", block).group(1)
    assert re.search(r"types: \[completed\]", block) and re.search(r"branches: \[main\]", block), "pages.yml no longer waits for a completed run on main"
    assert re.search(r"^  workflow_dispatch:", block, re.M), "pages.yml can no longer be run by hand"
    assert not re.search(r"^  push:", block, re.M), "pages.yml has a push trigger of its own again"
    assert "github.event.workflow_run.conclusion == 'success'" in text, "pages.yml no longer publishes only after a successful run"
    return {"w": w}


def exp_holdout_run_ids():
    """The run IDs PREREGISTRATION.md lists against the runs of the holdout records (the DETAILS paragraph says how many it lists)."""
    with open(os.path.join(REPO, "results", "s5-holdout", "PREREGISTRATION.md"), encoding="utf-8") as f:
        m = re.search(r"^Run IDs \([^)]*\): ([\d, ]+)\.\s*$", f.read(), re.M)
    assert m, "PREREGISTRATION.md no longer has a `Run IDs (...): a, b, c.` line"
    listed = sorted(x.strip() for x in m.group(1).split(","))
    recorded = sorted({str(d["run"]["id"]) for d in job_records("results/s5-holdout/runs/*/results-*/results.json")})
    assert listed == recorded, f"the plan lists {listed}, the holdout records come from runs {recorded}"
    return {"k": word(len(listed))}


def exp_runner_cores_rows():
    c = exp_runner_cores()
    return {**c, "n": exp_pool_growth()["s4"]}


def exp_workflow_pins():
    """Which workflows pin every action they use to a full commit, and how many still use a moving tag (read from .github/workflows)."""
    pinned, moving = [], []
    for path in sorted(glob.glob(os.path.join(REPO, ".github", "workflows", "*.yml"))):
        with open(path, encoding="utf-8") as f:
            refs = re.findall(r"^\s*(?:-\s*)?uses:\s*(?!\./)([^\s#]+)", f.read(), flags=re.M)
        assert refs, f"{os.path.basename(path)}: no action found"
        all_commits = all(re.fullmatch(r"[0-9a-f]{40}", r.partition("@")[2]) for r in refs)
        (pinned if all_commits else moving).append(os.path.basename(path))
    names = [f"`{n}`" for n in pinned]
    return {"names": ", ".join(names[:-1]) + " and " + names[-1], "n": str(len(moving))}


README_PROV_ROWS = [
    row("README: which workflows pin their actions to a commit", ".github/workflows/*.yml uses: lines", exp_workflow_pins,
        r"The workflows pin the GitHub actions they use to a commit in (?P<names>`[\w.-]+`(?:, `[\w.-]+`)* and `[\w.-]+`); the runs under `results/` ran before the pins "
        r"and used the moving `v4` tags of `actions/checkout`, `actions/upload-artifact` and `actions/download-artifact`, and the other (?P<n>\d+) workflows still do\."),
    row("README: the order of rule files, plans and expectations, and what the hashes show", "results/s5-holdout job records; site/data/holdout.json; tests/data/s9_s10_provenance.json",
        lambda: {**pick(exp_holdout_order(), "s"), **exp_public_history()},
        r"The rule files, plans and expectations were committed in the author's unpublished development history before the runs they govern, except the Arm plan "
        r"\(committed after its runs were dispatched\), the holdout plan \((?P<s>\d+) seconds after the first recorded job start\) and the replication plan \(see the "
        r"replication section below\)\. The public history begins on (?P<d>\d+ [A-Z][a-z]+ \d{4}), after the runs of `s1` to `s4`, the holdout and the rewrite, so for those "
        r"that order cannot be checked from public records; the records of `s6`, `s7` and `s9` name public commits that hold the rule file as it is now\. "
        r"The hashes stored in the result files show that the rule files did not change after the runs\. All versions are kept\."),
    row("README: commits and run links in the records", "tests/data/run_links_and_commits.json; results/ run.commit and workflow_run_url fields; replication/results.json pools",
        exp_run_links,
        r"The `commit` field of a result record \(`run\.commit`; `source\.repo_sha` in the census records\) names the commit the run was dispatched from\. "
        r"For `s1` to `s5` \(including the (?P<n4>\d+) `s4-run-\*` jobs, (?P=n4) of the (?P<p95>\d+) pooled jobs, and the (?P<nh>\d+) holdout jobs\), `mitigate`, `siblings`, "
        r"`corpus`, `realworld`, `pgo`, the day-one runs and `versions` these are commits of the author's unpublished development history that this repository does not "
        r"hold, so the code of those runs cannot be recovered from here\. The (?P<n8>\d+) Arm jobs \(`s8-arm-run-\*`\) name (?P<c8>[0-9a-f]+) on the temporary public "
        r"branch `(?P<b8>arm-smoke)`, because the `runner` input they needed was not yet on the default branch \(its `measure\.yml` was byte for byte the default "
        r"branch's at commit (?P<base>[0-9a-f]+), which has the `runner` input\); that branch is kept because the records name its commit\. "
        r"The forwardt runs \(the \w+ of `forwardt/runs\.json`: \w+ measurement runs, stored, and \w+ code tests, not stored\) were dispatched from the public branch "
        r"`[a-z-]+` at commit [0-9a-f]+, which the default branch holds, so that branch is not needed to recover their code\. "
        r"The run links inside the records work for `s6` to `s11` \(their runs are in this repository's Actions list\) and return 404 for every older folder"),
    row("README: how to rerun, the minimum number of jobs, the runner sizes and the compilers", "harness/criteria-v3.json minimum_jobs; run.runner.cores of every record; results/ run.toolchain; versions/install.sh",
        lambda: {**pick(exp_repl_sets(), "mn"), "cl": timed_clang(), **pick(exp_runner_cores_rows(), "e", "l", "n"), **exp_versions_range()},
        r"a verdict needs (?P<mn>\d+) or more jobs of one model, so one rerun will not reproduce the per-model verdicts by itself.*?The early runs \(`s1` to `s4`, including "
        r"the original (?P<n>\d+)-job pool\) ran on (?P<e>\d)-vCPU runners and every later run, a rerun today, on (?P<l>\d) vCPUs.*?\(clang (?P<cl>[\d.]+) from Ubuntu's "
        r"archive; `versions/install\.sh` takes whatever clang (?P<lo>\d+) to (?P<hi>\d+) apt\.llvm\.org then serves\)"),
    row("README: the final line and the exit code of a check whose page step was skipped", "scripts/check.py PASSED_WITH_SKIPS and EXIT_PASSED_WITH_SKIPS", exp_check_exit,
        r"the run ends `(?P<line>CHECKS PASSED, WITH SKIPPED STEPS)` with exit code (?P<code>\d+), not `ALL CHECKS PASSED`\."),
    row("README: how long the check takes on a CI runner", "tests/data/ci_check_step.json (the scripts/check.py step of the three most recent successful push runs of ci, from the GitHub API)",
        exp_ci_check_duration,
        r"and takes roughly (?P<lo>[a-z ]+?) to (?P<hi>[a-z ]+?) on a CI runner \("),
    row("README: which page checks need the web fonts", "scripts/check_site.py FONT_DEPENDENT_CHECKS and its docstring", exp_font_dependent,
        r"without that access it answers those requests itself and runs on the system fonts; on the Windows system fonts it was tried with, every check passes except the (?P<two>two) "
        r"\(`FONT_DEPENDENT_CHECKS` in `scripts/check_site\.py`\) that measure the hero's first view against the web fonts, so the run then fails instead of ending `ALL CHECKS PASSED` "
        r"\(other systems' fonts were not tried\)"),
    row("README: the replication plan's margin in the folder map", "the s9 job records' run.started_at; tests/data/s9_s10_provenance.json replication_plan",
        exp_prov_replication_pick("sec"),
        r"`replication/` the plan for the two replication sets \(committed in the author's unpublished development history, (?P<sec>\d+) seconds before the first job's recorded start: "
        r"see the replication section above\)"),
]

DETAILS_PROV_ROWS = [
    row("details: the holdout's plan commit time against the first job start, the run IDs the plan lists, and the rule-file hash",
        "results/s5-holdout job records run.started_at, run.id, run.criteria_sha256; results/s5-holdout/PREREGISTRATION.md run IDs; site/data/holdout.json",
        lambda: {**exp_holdout_order(), **exp_holdout_run_ids()},
        r"commit time in the author's unpublished development history \((?P<tc>[\d:]+) UTC on the author's clock\) is (?P<s>\d+) seconds after the first recorded job start "
        r"\((?P<ts>[\d:]+) UTC\), so the records do not show that order\. The file lists the (?P<k>\w+) run IDs, so the commit that holds this version came after those runs "
        r"were created\. What can be checked is the rule file: all (?P<n>\d+) holdout jobs record a `criteria_sha256` equal "
        r"to the sha256 of `harness/criteria-v3\.json`; that `harness/pool\.py` was unchanged cannot be checked from the records\."),
    row("details: when the public history begins, what the hashes show and which public commits hold the rule file", "tests/data/s9_s10_provenance.json public_history and rule_file_in_public_commits; the records' run.started_at and run.commit",
        exp_public_history,
        r"the public history begins on (?P<d>\d+ [A-Z][a-z]+ \d{4}), after the runs of `s1` to `s4`, the holdout and the rewrite, so for those that order cannot be checked "
        r"from public records, and what can be checked is the hash: every result file stores the sha256 of the rule file it was judged under, which shows that the file did "
        r"not change after the runs\. The records of `s6`, `s7` and `s9` name public commits that hold the rule file as it is now\."),
    row("details: the run links that work and the commits the records name", "tests/data/run_links_and_commits.json; results/ records",
        exp_run_links,
        r"The links work for the records in `results/s6-run-\*/` and `results/s7-run-\*/` \((?P<r67>\w+) runs\), `results/s8-arm-run-\*/` \((?P<r8>\w+)\), "
        r"`results/s9-arm-run-\*/` and `results/s9-run-\*/` \((?P<r9>\w+)\), `results/s10-dsweep-run-\*/` \((?P<r10>\w+)\) and `results/s11-forwardt-run-\*/` \((?P<r11>\w+)\).*?the code that produced the (?P<n4>\d+) "
        r"`s4-run-\*` jobs, (?P=n4) of the (?P<p95>\d+) pooled jobs, and the (?P<nh>\d+) holdout jobs cannot be recovered from here\. The (?P<n8>\d+) Arm jobs "
        r"\(`results/s8-arm-run-\*/`\) name (?P<c8>[0-9a-f]+) on the temporary public branch `(?P<b8>arm-smoke)`.*?at commit (?P<base>[0-9a-f]+)\)\. The d-sweep jobs name "
        r"(?P<c10>[0-9a-f]+) on `(?P<b10>dsweep-smoke)`"),
    row("details: the pool grew after the verdicts of the smaller pool were known", "results/s4-pooled, s6-pooled, s7-pooled pooled.json (Xeon 6973P-C entries)", exp_pool_growth,
        r"they differ for the Xeon 6973P-C \(no verdict with the (?P<s4>\d+) jobs, (?P<f6>[A-Z]+) with (?P<j6>\d+) jobs in the 75-job pool, (?P<f7>[A-Z]+) with (?P<j7>\d+) "
        r"jobs in the 95-job pool\)"),
    row("details: the runner size changed once", "run.runner.cores of every result record; results/s4-pooled", exp_runner_cores_rows,
        r"the early runs \(`s1` to `s4`, with the original (?P<n>\d+)-job pool\) ran on (?P<e>\d) vCPUs and the holdout and every later run, Arm runs and reruns included, on "
        r"(?P<l>\d) \(`run\.runner\.cores` in every result file\)"),
    row("details: the final line and the exit code of a check whose page step was skipped", "scripts/check.py PASSED_WITH_SKIPS and EXIT_PASSED_WITH_SKIPS", exp_check_exit,
        r"the run ends `(?P<line>CHECKS PASSED, WITH SKIPPED STEPS)` with exit code (?P<code>\d+), not `ALL CHECKS PASSED`"),
    row("details: which page checks need the web fonts", "scripts/check_site.py FONT_DEPENDENT_CHECKS and its docstring", exp_font_dependent,
        r"without that access it answers those requests itself and runs on the system fonts; on the Windows system fonts it was tried with, every check passes except the (?P<two>two) "
        r"\(`FONT_DEPENDENT_CHECKS` in `scripts/check_site\.py`\) that measure the hero's first view against the web fonts, so the run then fails instead of ending `ALL CHECKS PASSED` "
        r"\(other systems' fonts were not tried\)"),
    row("details: the margins of the holdout and replication plans in the list of exceptions", "the holdout and s9 job records' run.started_at; tests/data/s9_s10_provenance.json",
        lambda: {"s": exp_holdout_order()["s"], **{"r": exp_prov_replication_pick("sec")()["sec"]}},
        r"the holdout plan \((?P<s>\d+) seconds after the first recorded job start\) and the replication plan \((?P<r>\d+) seconds before it, inside the dispatch lag\)"),
    row("details: when the page is published", ".github/workflows/pages.yml on: block", exp_pages_trigger,
        r"`\.github/workflows/pages\.yml` publishes `site/` after the `(?P<w>ci)` workflow succeeds on a push to `main`, or when it is run by hand"),
]

ARM64_PROV_ROWS = [
    row("arm64: the runs, the temporary branch and the commit the records name", "tests/data/run_links_and_commits.json; results/s8-arm-run-*/ run.commit; the arm-smoke measure.yml hash",
        exp_run_links,
        r"The (?P<n8>\d+) result records \(`results/s8-arm-run-\*/`\) name its commit, (?P<c8>[0-9a-f]+), in `run\.commit`; no other public branch holds that commit\. "
        r"The `measure\.yml` there was byte for byte the default branch's file at commit (?P<base>[0-9a-f]+), which has the `runner` input\."),
    row("arm64: the temporary branch is named in the section", "tests/data/run_links_and_commits.json arm_smoke", exp_run_links,
        r"dispatched from a temporary branch of the public repository, `(?P<b8>arm-smoke)`, because the `runner` input they needed was not yet in `measure\.yml` "
        r"on the default branch\."),
]

# ---- limits, columns and the PGO paragraph ----------------------------------------------

NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}


def pgo_cpu(d, key):
    return next(c for c in d["cpus"] if key in c["cpu_model"])


def pgo_report_counts(cpu_full):
    """(higher, lower, same) rows of the PGO against non-PGO comparison, from the summary lines of pgo/report.md."""
    with open(os.path.join(REPO, "pgo", "report.md"), encoding="utf-8") as f:
        text = f.read()
    m = re.search(rf"^- {re.escape(cpu_full)}: PGO higher: (\d+) \(.*?\); PGO lower: (\d+) \(.*?\); no difference detected: (\d+) \(", text, re.M)
    assert m, f"pgo/report.md has no comparison summary line for {cpu_full}"
    return tuple(int(x) for x in m.groups())


def pgo_not_compared(cpu_full):
    with open(os.path.join(REPO, "pgo", "report.md"), encoding="utf-8") as f:
        return re.search(rf"^- {re.escape(cpu_full)}: not compared: (\d+) \(", f.read(), re.M) is not None


def pgo_nonpgo_readings(cpu_full):
    """{row: non-PGO reading} from the first table of the CPU model's section of pgo/report.md."""
    with open(os.path.join(REPO, "pgo", "report.md"), encoding="utf-8") as f:
        text = f.read()
    sec = text.split(f"### {cpu_full}", 1)[1].split("\n### ", 1)[0]
    out = {}
    for ln in sec.splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) == 8 and cells[0] not in ("row", "---"):
            out[cells[0]] = cells[3]
    return out


def exp_pgo_head():
    d = J("results/pgo-pooled/pgo.json")
    rw = J("results/realworld-pooled/realworld.json")
    non = {k: next(c for c in rw["cpus"] if k in c["cpu_model"])["jobs"] for k in ("7763", "9V74")}
    assert non["9V74"] == d["minimum_jobs"], "the EPYC 9V74 non-PGO pool is no longer at the minimum number of jobs"
    assert all(len(c["rows"]) == 8 for c in d["cpus"]), "a CPU model of the PGO file does not hold the eight rows"
    jobs = {k: pgo_cpu(d, k)["jobs"] for k in ("7763", "9V74", "8573C", "8370C")}
    assert len(d["cpus"]) == 4 and len(d["inputs"]) == sum(jobs.values()), "the PGO file's inputs and per-model jobs disagree"
    runs = d["runs"]
    return {"ids": ", ".join(runs[:-1]) + " and " + runs[-1], "tot": str(sum(jobs.values())), "a": str(jobs["7763"]), "b": str(jobs["9V74"]),
            "c": str(jobs["8573C"]), "e": str(jobs["8370C"]), "n7": str(non["7763"]), "n9": str(non["9V74"])}


def exp_pgo_rows():
    d = J("results/pgo-pooled/pgo.json")
    c7, c9 = pgo_cpu(d, "7763"), pgo_cpu(d, "9V74")
    r7, r9 = ({r["row"]: r for r in c["rows"]} for c in (c7, c9))
    fast = lambda r: r["pairs"]["fast"]["time"]["ratio"]  # noqa: E731
    rd = lambda r: r["reading"]["reading"]  # noqa: E731
    assert rd(r7["lightgbm_default"]) == "not detectable" and rd(r7["fmt"]) == "detectably faster", "the 7763 readings of the first and last row changed"
    assert all(rd(r7[n]) == "detectably slower" for n in ("lightgbm_multiclass", "lightgbm_linear", "draco", "tinydnn")), "a 7763 row is no longer detectably slower"
    assert all(rd(r7[n]) == "not detectable" for n in ("spectra", "meshopt")), "Spectra or meshoptimizer is detectable on the 7763"
    slower9 = sorted(n for n, r in r9.items() if rd(r) == "detectably slower")
    assert slower9 == ["draco", "lightgbm_linear", "lightgbm_multiclass"], f"the 9V74 rows that are detectably slower changed: {slower9}"
    both = [r9[n]["pairs"][col]["time"]["ratio"] for n in slower9 for col in ("fast", "aligned")]
    asc = [fast(r9[n]) for n in slower9]
    h7, l7, s7 = pgo_report_counts(c7["cpu_model"])
    h9, l9, s9 = pgo_report_counts(c9["cpu_model"])
    return {"dflt": f"{fast(r7['lightgbm_default']):.3f}", "amp": f"{r7['lightgbm_default']['reading']['at_most_pct']:.2f}",
            "mc": f"{fast(r7['lightgbm_multiclass']):.3f}", "ln": f"{fast(r7['lightgbm_linear']):.3f}", "dr": f"{fast(r7['draco']):.3f}",
            "td": f"{fast(r7['tinydnn']):.3f}", "l7": NUMBER_WORDS[l7], "h7": NUMBER_WORDS[h7], "s7": NUMBER_WORDS[s7],
            "n3": NUMBER_WORDS[len(slower9)], "lo": f"{min(both):.3f}", "hi": f"{max(both):.3f}", "clo": f"{min(asc):.3f}", "chi": f"{max(asc):.3f}",
            "l9": NUMBER_WORDS[l9], "h9": NUMBER_WORDS[h9], "s9": NUMBER_WORDS[s9]}


def exp_pgo_tail():
    d = J("results/pgo-pooled/pgo.json")
    for key in ("7763", "9V74"):
        c = pgo_cpu(d, key)
        dflt = next(r for r in c["rows"] if r["row"] == "lightgbm_default")
        assert dflt["reading"]["reading"] == "not detectable", f"LightGBM default is detectable under PGO on {key}"
        assert pgo_nonpgo_readings(c["cpu_model"])["lightgbm_default"] == "slower", f"LightGBM default was not detectably slower without PGO on {key}"
    for key in ("8573C", "8370C"):
        assert pgo_not_compared(pgo_cpu(d, key)["cpu_model"]), f"the Xeon {key} now has a non-PGO counterpart"
    vn = vf = total = 0
    for prog, modes in d["pgo_context"].items():
        nl = {x["location"]: x["vectorized"] for x in modes["none"]["census_lost_locations"]}
        fl = {x["location"]: x["vectorized"] for x in modes["fast"]["census_lost_locations"]}
        vn += sum(1 for k in nl if nl[k] > 0)
        vf += sum(1 for k in nl if fl.get(k, 0) > 0)
        total += len(nl)
    return {"vn": str(vn), "lt": str(total), "vf": str(vf)}


@lru_cache(maxsize=None)
def x86_pool_dirs():
    """The job folders the 95-job kernel pool lists (results.json, details.json and asm/ sit in each)."""
    base = os.path.dirname(os.path.join(REPO, POOLED))
    return [os.path.normpath(os.path.join(base, os.path.dirname(i["path"]))) for i in J(POOLED)["inputs"]]


def read_text_file(path):
    with open(path, "rb") as f:
        return f.read()


@lru_cache(maxsize=None)
def x86_k01_identical():
    """The number of jobs whose forward-sum listings (default and aligned build) are byte for byte the same in NONE and FAST; every job must agree."""
    n = 0
    for d in x86_pool_dirs():
        for suffix in ("", "_a64"):
            a = read_text_file(os.path.join(d, "asm", f"k01_sum_fwd.none{suffix}.s"))
            b = read_text_file(os.path.join(d, "asm", f"k01_sum_fwd.fast{suffix}.s"))
            assert a == b, f"the forward sum is not the same machine code in NONE and FAST in {d} ({suffix or 'default'} build)"
        n += 1
    assert n == len(J(POOLED)["inputs"])
    return n


def element_loads(text):
    return len(re.findall(r"^\s*[0-9a-f]+:\s+mov\s+-0x[0-9a-f]+\(%rax,%\w+,4\),%", text, re.M | re.I))


@lru_cache(maxsize=None)
def x86_reverse_unrolling():
    """(element loads in the no-vectorize listing, in the FAST listing) of the reverse loop: the same in every job."""
    seen = set()
    for d in x86_pool_dirs():
        nv = element_loads(read_text_file(os.path.join(d, "asm", "k04_rev.novec.s")).decode("utf-8"))
        fa = element_loads(read_text_file(os.path.join(d, "asm", "k04_rev.fast.s")).decode("utf-8"))
        seen.add((nv, fa))
    assert len(seen) == 1, f"the reverse listings differ between jobs: {seen}"
    return seen.pop()


def exp_gather():
    mn = J("harness/criteria-v3.json")["v3"]["pooling"]["minimum_jobs"]
    models = [c for c in J(POOLED)["cpus"] if c["jobs"] >= mn]
    assert len(models) == 5, f"{len(models)} CPU models have {mn} or more jobs; the README says five"
    vals = []
    for c in models:
        g = next(x for x in c["cells"] if x["cell_id"] == "k06_gather.L1")
        assert g["class"] == "off_axis", "the gather cell is no longer off the SIMD axis"
        vals += [g["as_compiled"]["ratio"], g["aligned"]["ratio"]]
    for d in x86_pool_dirs():
        rec = json.loads(read_text_file(os.path.join(d, "results.json")))
        for cell in rec["cells"]:
            if cell["kernel"] == "k06_gather":
                assert not cell["vectorized_none"]["vectorized"] and not cell["vectorized_fast"]["vectorized"], f"the gather is vectorized in {d}"
    return {"glo": f1(min(vals)), "ghi": f1(max(vals))}


def exp_decomposition():
    nv, fa = x86_reverse_unrolling()
    assert fa == 1 and nv > 4 * fa, f"the reverse listings no longer show the four-fold unrolling of the scalar loop (no-vectorize loads {nv}, FAST loads {fa})"
    return {"an": f1(arm_cpu()["positive"]["k04_rev.L1"]["ratio"]), "af": f1(arm_ratio("k04_rev.L1"))}


def exp_cover_numbers():
    """What the placement exemption left out and what is left, from the 95-job pool's verdicts, and the margins of the two words nearest the limit."""
    mn = J("harness/criteria-v3.json")["v3"]["pooling"]["minimum_jobs"]
    cpus = [c for c in J(POOLED)["cpus"] if c["jobs"] >= mn]
    by = {k: next(c for c in cpus if k in c["cpu_model"]) for k in ("7763", "9V45", "9V74", "8573C", "6973P-C")}

    def exempt(c):
        return sorted(p["cell_id"] for p in c["verdict"]["placement_sensitive"])

    def judged(c):
        fw = [x["cell_id"] for x in c["cells"] if x["kernel"] in FORWARD and x["size_class"] in ("L1", "L2")]
        return [cid for cid in fw if cid not in exempt(c)]
    amd = [by[k] for k in ("7763", "9V45", "9V74")]
    assert {len(exempt(c)) for c in amd} == {3} and {tuple(judged(c)) for c in amd} == {("k01_sum_fwd.L1", "k01_sum_fwd.L2", "k03_stencil.L2")}, "the AMD exemptions changed"
    assert exempt(by["6973P-C"]) == ["k02_add_fwd.L1", "k03_stencil.L1"] and exempt(by["8573C"]) == ["k02_add_fwd.L2"], "the Intel exemptions changed"
    assert all(len([x for x in c["cells"] if x["kernel"] in FORWARD and x["size_class"] in ("L1", "L2")]) == 6 for c in cpus)
    sten = next(p for p in by["7763"]["verdict"]["placement_sensitive"] if p["cell_id"] == "k03_stencil.L1")
    add69 = next(p for p in by["6973P-C"]["verdict"]["placement_sensitive"] if p["cell_id"] == "k02_add_fwd.L1")
    add85 = next(x for x in by["8573C"]["cells"] if x["cell_id"] == "k02_add_fwd.L1")
    assert "k02_add_fwd.L1" not in exempt(by["8573C"]) and f2(add85["as_compiled"]["ratio"]) == f2(add85["aligned"]["ratio"]), "the Xeon 8573C add changed"
    sten69 = next(x for x in by["6973P-C"]["cells"] if x["cell_id"] == "k03_stencil.L2")["aligned"]["ci95"][1]
    arm_hi = arm_cell("k02_add_fwd.L2")["aligned"]["ci95"][1]
    limit = 1 + by["6973P-C"]["verdict"]["forward_limit_pct"] / 100
    assert max(abs(sten69 - limit), abs(arm_hi - limit)) < 0.002, "the two words nearest the limit are no longer within 0.002 of it"
    jobs = x86_k01_identical()
    assert jobs == len(J(POOLED)["inputs"])
    return {"amd": "3", "six": "6", "x69": str(len(exempt(by["6973P-C"]))), "x85": str(len(exempt(by["8573C"]))), "jd": "3", "jobs": str(jobs),
            "sc": f3(sten["ratio"]), "sa": f3(sten["aligned_ratio"]), "ac2": f2(add69["ratio"]), "aa2": f2(add69["aligned_ratio"]),
            "ac3": f3(add69["ratio"]), "aa3": f3(add69["aligned_ratio"]), "xc2": f2(add85["as_compiled"]["ratio"]),
            "xc3": f3(add85["as_compiled"]["ratio"]), "xa3": f3(add85["aligned"]["ratio"]), "tol": "0.002", "lim": f2(limit), "h1": f3(sten69), "h2": f3(arm_hi)}


@lru_cache(maxsize=None)
def early_ram_cells():
    """{cell: [ratio per job]} of the RAM-sized cells, which exist only in the early runs; and the number of jobs and runs that hold them."""
    out = {"k04_rev.RAM": [], "k05_stride2.RAM": []}
    jobs, runs = 0, set()
    early = ("s2-run-", "s3-run-", "s3-audit-run-")
    for p in sorted(glob.glob(os.path.join(REPO, "results", "*", "**", "results.json"), recursive=True)):
        run = os.path.relpath(p, os.path.join(REPO, "results")).replace("\\", "/").split("/")[0]
        raw = read_text_file(p)
        if not run.startswith(early):
            assert b".RAM" not in raw, f"{p} holds a RAM-sized cell: the texts say they exist only in the early runs"
            continue
        rec = json.loads(raw)
        ram = [c for c in rec.get("cells", []) if str(c.get("cell_id", "")).endswith(".RAM")]
        if ram:
            jobs += 1
            runs.add(run)
            for c in ram:
                if c["cell_id"] in out:
                    out[c["cell_id"]].append(c["ratio"])
    return out, jobs, len(runs)


def exp_ram():
    out, jobs, runs = early_ram_cells()
    assert jobs == 13 and runs == 4 and all(len(v) == 13 for v in out.values()), f"RAM cells in {jobs} jobs, {runs} runs"
    lost = exp_lost_bullet()
    return {"rj": str(jobs), "rr": "four", "rl": f1(min(out["k04_rev.RAM"])), "rh": f1(max(out["k04_rev.RAM"])), "sl": f1(min(out["k05_stride2.RAM"])),
            "sh": f1(max(out["k05_stride2.RAM"])), "lo": lost["lo"], "hi": lost["hi"]}


def exp_program_floor():
    rw = J("results/realworld-pooled/realworld.json")
    c7 = next(c for c in rw["cpus"] if "7763" in c["cpu_model"])
    c45 = next(c for c in rw["cpus"] if "9V45" in c["cpu_model"])
    row_ = lambda c, n: next(r for r in c["rows"] if r["row"] == n)  # noqa: E731
    for name in ("realworld/build.py", "pgo/build_pgo.py"):
        src = read_text_file(os.path.join(REPO, name)).decode("utf-8")
        hits = [m.start() for m in re.finditer(r"-DNDEBUG", src)]
        assert hits and all(src[max(0, h - 3):h] == "no " for h in hits), f"{name} no longer says the programs are built without -DNDEBUG"
    return {"aamax": f2(max(r["pairs"]["aa"]["time"]["half_width_pct"] for r in c7["rows"])),
            "fmt": pct1(row_(c7, "fmt")["pairs"]["layout"]["time"]["ratio"]), "sp": pct1(row_(c45, "spectra")["pairs"]["layout"]["time"]["ratio"])}


def exp_aa_extra():
    """README, 'Floors, sizes and builds': the A/A at L2 is timed in every job (details.json aa_extra) and pooled per CPU model in robustness/aa-l2.json."""
    for d in x86_pool_dirs():
        det = json.loads(read_text_file(os.path.join(d, "details.json")))
        assert "k02_add_fwd.L2" in det["aa_extra"], f"{d} holds no L2 A/A"
    af = aa_l2_facts()
    aa_l2_as_wide_as_the_deciding_cells()
    return {"mx": f2(af["max_others"]), "nf": word(af["n_others"]), "x2": f2(af["x2"]), "x1": f2(af["x1"]),
            "a2": f2(af["a2"]), "a1": f3(af["a1"]), "ceil": f"{af['ceil']:g}"}


def exp_aa_l2_tail():
    """README, 'What MAP and INCONCLUSIVE cover': the closing sentence on the seed re-draws, the 3-job subsets and the A/A at L2."""
    sf, af, sub = seed_facts(), aa_l2_facts(), calib_subsets()
    aa_l2_as_wide_as_the_deciding_cells()
    return {"si": str(sf["inc"]), "st": str(sf["total"]), "sj": "3", "s3i": str(sub[3][0]), "s3n": str(sub[3][1]),
            "x2": f2(af["x2"]), "a2": f2(af["a2"]), "ceil": f"{af['ceil']:g}"}


def exp_robustness_folder_seeds():
    return {"n": str(J(SEED_X86)["alt_seeds"]["count"])}


def exp_details_calibrated():
    cf = calib_facts()
    return {"e7": f1(cf["m7"]["expected_outside"]), "e9": f1(cf["m9"]["expected_outside"]),
            "l7": f0(cf["r7"][0]), "h7": f0(cf["r7"][1]), "l9": f0(cf["r9"][0]), "h9": f0(cf["r9"][1]),
            "o7": str(cf["m7"]["outside"]), "o9": str(cf["m9"]["outside"]),
            "fo": str(cf["lost"][0]), "fn": str(cf["lost"][1]), "fe": f1(cf["lost"][2]),
            "go": str(cf["fwd"][0]), "gn": str(cf["fwd"][1]), "ge": f1(cf["fwd"][2]),
            "l6": f0(cf["r6"][0]), "h6": f0(cf["r6"][1]), "n6": str(cf["m6"]["checked"])}


def exp_repl_why_with_seeds():
    """DETAILS, the replication entry: the two thin margins. The Xeon 6973P-C's end under the stored seed is the replication file's and the seed file's;
    the end once the draw no longer matters is the seed file's converged end."""
    sf = seed_facts()
    out = {k: v for k, v in exp_repl_intro().items() if k in ("fa", "ha", "lim", "fx", "hx")}
    assert out["hx"] == f4(sf["stored"]), "the replication file's and the seed file's stored end of the Xeon 6973P-C stencil at L2 differ"
    out["conv"] = f4(sf["conv"])
    return out


def exp_details_aa_l2_intro():
    return {"ceil": f"{aa_l2_facts()['ceil']:g}"}


def exp_details_aa_l2_paragraph():
    af = aa_l2_facts()
    aa_l2_as_wide_as_the_deciding_cells()
    return {"mx": f2(af["max_others"]), "nf": word(af["n_others"]), "ceil": f"{af['ceil']:g}", "x2": f2(af["x2"]), "a2": f2(af["a2"])}


def exp_arm_calibrated():
    """arm64/README, run-to-run comparisons: the stride-2 cells at L2 and all in-cache cells, in the Arm pool and in sets A and B pooled."""
    arm = calib_model("s8-arm", "Neoverse-N2")
    ab = calib_model("s9-arm-ab", "Neoverse-N2")
    def stride2(model):
        """The stride-2 cell at L2, summed over its two columns (as compiled and aligned)."""
        cells = [c for c in model["by_cell"] if c["cell_id"] == "k05_stride2.L2"]
        assert len(cells) == 2, "the stride-2 cell at L2 no longer has two columns in the calibration file"
        return {k: sum(c[k] for c in cells) for k in ("outside", "pairs", "expected_outside")}
    s2, s2ab = stride2(arm), stride2(ab)
    assert (arm["outside"], arm["checked"]) == (arm_cpu()["reproduction"]["outside"], arm_cpu()["reproduction"]["checked"]), "the calibration file's Arm count is not the pooled file's"
    assert arm["outside"] < arm["expected_outside"] and ab["outside"] < ab["expected_outside"] and s2["outside"] > s2["expected_outside"], \
        "the Arm counts are no longer below the calibrated expectation overall and above it in the stride-2 cells at L2"
    return {"so": str(s2["outside"]), "sn": str(s2["pairs"]), "se": f1(s2["expected_outside"]), "ao": str(arm["outside"]), "an": str(arm["checked"]),
            "ae": f1(arm["expected_outside"]), "bo": str(s2ab["outside"]), "bn": str(s2ab["pairs"]), "be": f1(s2ab["expected_outside"]),
            "co": str(ab["outside"]), "cn": str(ab["checked"]), "ce": f1(ab["expected_outside"])}


def exp_google_quote():
    """The words in quotation marks are the stored quotation (checked by hand against the cited post on Oct 18 2026: it is the start of the sentence there); under 15 words."""
    claim = J("site/data/index.json")["claim"]
    assert len(claim["quote"].split()) < 15, "the quotation is 15 words or longer"
    assert claim["quote"] == f"Hardening libc++ resulted in an average {f2(claim['google_pct'])}% performance impact", "claim.quote and claim.google_pct disagree"
    return {"q": claim["quote"], "v": f2(claim["google_pct"])}


GROUP2_README_ROWS = [
    row("question: the quotation from Google's post", "site/data/index.json claim.quote and claim.google_pct", exp_google_quote,
        r"Google wrote that \"(?P<q>Hardening libc\+\+ resulted in an average (?P<v>[\d.]+)% performance impact)\" across its services"),
    row("README top: the gather clause", "results/s7-pooled/pooled.json k06_gather.L1 (models with 3 or more jobs); the job records' vectorization flags", exp_gather,
        r"A gather through an index, which neither build vectorizes, costs (?P<glo>[\d.]+)x to (?P<ghi>[\d.]+)x at L1 depending on the CPU model, so the cost is not only a SIMD effect\."),
    row("found: the rest of the reverse cost, the unrolling and the Arm split", "asm/k04_rev.novec.s and k04_rev.fast.s of the 95 jobs; results/s8-arm-pooled k04_rev.L1 positive and as compiled",
        exp_decomposition,
        r"and also the four-fold unrolling that the scalar loop without the check has and the checked one lacks \(read from the listings; inferred, not separated, and not a stable "
        r"share: on Neoverse-N2 the no-vectorize build takes (?P<an>[\d.]+)x and the checked build (?P<af>[\d.]+)x for reverse\)\."),
    row("trust: what MAP and INCONCLUSIVE cover", "results/s7-pooled/pooled.json verdict.placement_sensitive and cells; asm/k01_sum_fwd.* of the 95 jobs; results/s8-arm-pooled", exp_cover_numbers,
        r"\*\*What MAP and INCONCLUSIVE cover\.\*\* Each word is a statement about the forward in-cache cells \(loops bounded by `size\(\)`\) left after one exemption that the rule file "
        r"`harness/criteria-v3\.json` sets \(it was fixed before the first pooled run, in the author's unpublished development history, though after the earlier runs were known\): a cell is "
        r"left out when the hot loops of the two builds sit differently in memory and the ratio between its as-compiled and aligned results has an interval that excludes 1\. "
        r"The rule has no minimum size for that difference and does not ask whether the cost goes away when the loops are aligned; aligning to 64 bytes removes one source of "
        r"placement variation, not all of it \(the stencil at L1 on EPYC 7763 is (?P<sc>[\d.]+)x as compiled and (?P<sa>[\d.]+)x aligned\)\. "
        r"The second test .{0,1200}? extra window\. "  # its figures are tied to the pools in tests/test_placement_docs.py
        r"The exemption left out (?P<amd>\d) of "
        r"the (?P<six>\d) forward cells on each AMD model, (?P<x69>\d) on the Xeon 6973P-C and (?P<x85>\d) on the Xeon 8573C, each listed with its ratios in the model's verdict "
        r"line in `results/s7-pooled/pooled\.json`\. On each AMD model the (?P<jd>\d) judged cells are the forward sum at L1 and L2, which compiles to identical machine code in "
        r"both builds \(the same in all (?P<jobs>\d+) jobs, so it measures noise, not the check\), and the stencil at L2\. The Xeon 6973P-C's forward add at L1 "
        r"\((?P<ac2>[\d.]+)x as compiled, (?P<aa2>[\d.]+)x aligned\) is among the cells left out, and the Xeon 8573C's \((?P<xc2>[\d.]+)x in both columns\) is judged, so the two "
        r"Intel words do not rank those models by cost\. "
        r"The rule asks whether the two columns differ, not by how much: .{0,1100}? the fifth being the EPYC 9V45's stencil at L1 \(\d\.\d{4}\)\. "  # tied to the pools in tests/test_placement_docs.py
        r"The 6973P-C's MAP and the Arm INCONCLUSIVE each rest on one cell within (?P<tol>[\d.]+) of the (?P<lim>[\d.]+) limit "
        r"\((?P<h1>[\d.]+) and (?P<h2>[\d.]+)\)"),
    row("trust: floors, sizes and builds, the A/A at L2", "details.json aa_extra of the 95 jobs; robustness/aa-l2.json pools s7 and s8-arm; the seed file's stencil interval and the Arm pool's forward add interval at L2",
        exp_aa_extra,
        r"The same A/A at L2 is timed in every job \(stored as `aa_extra` in each job's `details\.json`\) and pooled per CPU model in `robustness/aa-l2\.json` "
        r"\(table in the \[details\]\(readme-parts/DETAILS\.md\)\): its pooled half-width is at most (?P<mx>[\d.]+)% on (?P<nf>\w+) x86-64 models, (?P<x2>[\d.]+)% on the Xeon 6973P-C "
        r"\((?P<x1>[\d.]+)% at L1\) and (?P<a2>[\d.]+)% on the Arm core \((?P<a1>[\d.]+)% at L1\), the last two above the (?P<ceil>\d+)% ceiling; "
        r"on the Arm core that A/A is as wide as the cells it would judge \(above\)\. Read at L2, the ceiling clause would turn the 6973P-C's MAP into INCONCLUSIVE "
        r"and change no other stored word in the four pools that file covers; the rule reads L1 only and is not changed\."),
    row("trust: what MAP and INCONCLUSIVE cover, the closing sentence (seeds, subsets, the A/A at L2)",
        "robustness/seed-sensitivity-x86.json whole; robustness/calibration.json subsets; robustness/aa-l2.json s7 and s8-arm", exp_aa_l2_tail,
        r"those are the stored seed's ends: re-drawn under other seeds the 6973P-C's whole analysis is INCONCLUSIVE in (?P<si>\d+) of (?P<st>\d+) and (?P<sj>\d+)-job subsets of its own jobs "
        r"are INCONCLUSIVE in (?P<s3i>\d+) of (?P<s3n>\d+) \(\[calibration\]\(robustness/README-calibration\.md\)\), and an identical binary timed at L2 is about as wide as the intervals "
        r"of the cells the two words rest on \((?P<x2>[\d.]+)% pooled on the 6973P-C and (?P<a2>[\d.]+)% on the Arm core, against the (?P<ceil>\d+)% ceiling the rule reads at L1; "
        r"see \"Floors, sizes and builds\"\), so a word that close is better read as undecided at this sampling\."),
    row("folders: the seed re-draws in robustness/", "robustness/seed-sensitivity-x86.json alt_seeds.count", exp_robustness_folder_seeds,
        r"\(interval ends re-drawn under (?P<n>\d+) other seeds\)"),
    row("trust: floors, sizes and builds, programs, RAM and NDEBUG", "results/realworld-pooled/realworld.json pairs.aa and pairs.layout; early results.json RAM cells; realworld/build.py, pgo/build_pgo.py",
        lambda: {**exp_program_floor(), **exp_ram()},
        r"is at most (?P<aamax>[\d.]+)% on EPYC 7763, while building the same program without checks at `-falign-loops=64` moves it by (?P<fmt>[\d.]+)% for \{fmt\} on EPYC 7763 "
        r"and by (?P<sp>[\d.]+)% for Spectra on EPYC 9V45, so a program effect smaller than that is not separated from code placement\. RAM-sized working sets were timed in "
        r"(?P<rj>\d+) early jobs only: there reverse took (?P<rl>[\d.]+)x to (?P<rh>[\d.]+)x and stride-2 (?P<sl>[\d.]+)x to (?P<sh>[\d.]+)x, far less than in cache, and they were "
        r"not re-timed in the pooled runs, so the (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x is for data that fits in the cache\. The programs were built without `-DNDEBUG`"),
]

GROUP2_DETAILS_ROWS = [
    row("details: the placement exemption, what it left out and what is left", "results/s7-pooled/pooled.json verdict.placement_sensitive and cells; asm/k01_sum_fwd.* of the 95 jobs; results/s8-arm-pooled",
        exp_cover_numbers,
        r"That is (?P<amd>\d) of the (?P<six>\d) forward in-cache cells on each AMD model, (?P<x69>\d) on the Xeon 6973P-C and (?P<x85>\d) on the Xeon 8573C in the (?P<jobs>\d+)-job pool, "
        r"each listed with its ratios in the model's verdict line in `results/s7-pooled/pooled\.json` \(`harness/criteria-v3\.json`, `placement_sensitive`\)\. MAP or INCONCLUSIVE is a "
        r"statement about the cells that are left\. The rule has no minimum size for the difference and does not ask whether the cost goes away when the loops are aligned\. "
        r"The second test .{0,1200}? extra window\. "  # its figures are tied to the pools in tests/test_placement_docs.py
        r"The cells left are, on each AMD model, the forward sum at L1 and L2, whose machine code is identical in the two builds in all (?P=jobs) jobs \(so they measure noise, not the "
        r"check\), and the stencil at L2\. The Xeon 6973P-C's forward add at L1 \((?P<ac3>[\d.]+) as compiled, (?P<aa3>[\d.]+) aligned\) is left out, while the Xeon 8573C's "
        r"\((?P<xc3>[\d.]+) as compiled, (?P<xa3>[\d.]+) aligned\) is judged; that is why only one of the two has a verdict, and the two Intel words do not rank the models by cost\. "
        r"The rule asks whether the two columns differ, not by how much: .{0,1100}? the fifth being the EPYC 9V45's stencil at L1 \(\d\.\d{4}\)\. "  # tied to the pools in tests/test_placement_docs.py
        r"Aligning loops to 64 bytes removes one source of placement variation, not all of it: the stencil at L1 on EPYC 7763 is (?P<sc>[\d.]+) as compiled and (?P<sa>[\d.]+) aligned\. "
        r"Several words rest on margins of a few thousandths against the (?P<lim>[\d.]+) limit \(the Xeon 6973P-C's stencil at L2 ends at (?P<h1>[\d.]+), the Arm forward add at L2 at "
        r"(?P<h2>[\d.]+);"),
    row("details: RAM-sized cells exist in 13 early jobs only", "early results.json RAM cells (results/s2-run-*, s3-run-*, s3-audit-run-*); no other results.json holds one", exp_ram,
        r"RAM-size cells exist only in (?P<rj>\d+) early jobs \((?P<rr>\w+) runs, in `results/s2-run-\*`, `results/s3-run-\*` and `results/s3-audit-run-\*`\): there the reverse "
        r"loop cost (?P<rl>[\d.]+)x to (?P<rh>[\d.]+)x and stride-2 (?P<sl>[\d.]+)x to (?P<sh>[\d.]+)x, far less than in cache and different by CPU model, and the cells were not "
        r"re-timed in the pooled runs, so the (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x is for data that fits in the cache\."),
    row("details: the real-program floor, layout shifts and NDEBUG", "results/realworld-pooled/realworld.json pairs.aa and pairs.layout; realworld/build.py, pgo/build_pgo.py", exp_program_floor,
        r"built without `-DNDEBUG` \(the programs' own `assert` checks are active in both builds; release builds differ, and the size of that difference was not tested\).*?"
        r"The A/A floor of these readings is that of an identical binary \(at most (?P<aamax>[\d.]+)% on EPYC 7763\), while the same program built without checks at "
        r"`-falign-loops=64` differs from the default build by (?P<fmt>[\d.]+)% for \{fmt\} on EPYC 7763 and by (?P<sp>[\d.]+)% for Spectra on EPYC 9V45 "
        r"\(`pairs\.layout` in `results/realworld-pooled/realworld\.json`\)"),
    row("details: what pool_check.py recomputes and how closely", "harness/pool_check.py SAMPLE_CELLS, PLACEMENT_CELLS, B, BOUND_TOL_WIDTH, BOUND_TOL_RATIO; harness/criteria-v3.json minimum_jobs; results/s7-pooled/pooled.json intervals and inputs",
        exp_pool_check_sample,
        r"`harness/pool_check\.py` independently recomputes a sample of the pooled numbers, not all of them: for each CPU model with (?P<mn>\d+) or more jobs, the A/A, "
        r"the layout A/A, (?P<cells>\w+) named cells and (?P<pl>\w+) placement statistics\. They include the three cells the written conclusions rest on "
        r"\(the stencil and the forward add at L2, which decide the words of the Xeon 6973P-C and of the Arm core, and stride-2 at L1, where the range of "
        r"lost-loop costs starts\)\. It uses its own code, generator and (?P<b>[\d,]+) resamples, so its interval "
        r"bounds only have to agree with the stored ones within a Monte Carlo tolerance \((?P<w>\d+)% of the interval's width plus (?P<r>[\d.]+)% of the ratio\); "
        r"for a few very narrow intervals \((?P<nk>\d+) of the (?P<nm>\d+) statistics sampled in the (?P<jobs>\d+)-job x86-64 pool, all EPYC (?P<cpu>\w+)\) "
        r"the tolerance is as wide as the interval, so there the check confirms the point estimate and the order of the width, not the bound\. "
        r"`scripts/check\.py` re-runs `harness/pool\.py` for all the rest"),
    row("details: the PGO column, runs and jobs", "results/pgo-pooled/pgo.json runs, cpus, inputs; results/realworld-pooled/realworld.json jobs", exp_pgo_head,
        r"\*\*PGO column \(`pgo/`, six runs: (?P<ids>[\d, and]+), on build run \d+\)\.\*\* All eight rows \(six workloads and two controls\) rebuilt with clang "
        r"instrumented profile-guided optimization, each mode profiled separately, (?P<tot>\d+) distinct jobs pooled per CPU model \(EPYC 7763 (?P<a>\d+), EPYC 9V74 "
        r"(?P<b>\d+), Xeon 8573C (?P<c>\d+), Xeon 8370C (?P<e>\d+)\)\. EPYC 7763 \(non-PGO (?P<n7>\d+) jobs\) and EPYC 9V74 \(non-PGO (?P<n9>\d+) jobs, the minimum\) "
        r"have a reading on both sides"),
    row("details: the PGO ratios and the comparison with the non-PGO pool", "results/pgo-pooled/pgo.json cpus[].rows[].pairs and reading; pgo/report.md summary lines", exp_pgo_rows,
        r"On EPYC 7763, PGO FAST/NONE as compiled: LightGBM default (?P<dflt>[\d.]+) \(not detectable, at most (?P<amp>[\d.]+)%\), multiclass (?P<mc>[\d.]+), linear "
        r"(?P<ln>[\d.]+), Draco (?P<dr>[\d.]+), tiny-dnn (?P<td>[\d.]+) \(the last four detectably slower\), Spectra and meshoptimizer not detectable, \{fmt\} faster; "
        r"against the non-PGO ratios PGO was lower in (?P<l7>\w+) row, higher in (?P<h7>\w+) and not detectably different in (?P<s7>\w+)\. On EPYC 9V74, (?P<n3>\w+) rows "
        r"with lost loops stay detectably slower under PGO \((?P<lo>[\d.]+) to (?P<hi>[\d.]+) across the two columns; as compiled (?P<clo>[\d.]+) to (?P<chi>[\d.]+)\); "
        r"PGO was lower in (?P<l9>\w+) row, higher in (?P<h9>\w+) and not different in (?P<s9>\w+)\."),
    row("details: what PGO leaves, the census locations and the Xeons", "results/pgo-pooled/pgo.json pgo_context census_lost_locations; pgo/report.md", exp_pgo_tail,
        r"\(LightGBM default dropped to not detectable on both models\), and almost all of the census's lost loops stay lost \((?P<vn>\d+) of (?P<lt>\d+) locations "
        r"vectorized with checks off, (?P<vf>\d+) with checks on\)\. Limits: the training input is the timed input, which flatters PGO; instrumented profiles only, no "
        r"sampling profiles, no link-time optimization; the two Xeon models have no non-PGO counterpart, so neither is read\."),
]

# ---- DETAILS prose tied to data: census, mitigation, versions, holdout, layout, lostloops --------

def mit_shape(shape):
    return next(s for s in J("site/data/mitigate.json")["shapes"] if s["shape"] == shape)


def mit_ratios(shape, variants, cpus=None, sizes=("L1", "L2")):
    """Every job's FAST/original-aligned ratio of the named rewrites (the stored per-CPU, per-size lists)."""
    out = []
    for v in mit_shape(shape)["variants"]:
        if v["variant"] in variants:
            for cpu, per in v["per_cpu"].items():
                if cpus is None or cpu in cpus:
                    for size in sizes:
                        out.extend(r["ratio"] for r in per.get(size, []))
    assert out, f"no ratios for {shape} {variants} {cpus} {sizes}"
    return out


def mit_pair(values):
    return {"lo": f2(min(values)), "hi": f2(max(values))}


def exp_mitigation_summary():
    """The rewrite figures that DETAILS.md and mitigate/README.md type, from site/data/mitigate.json (per-job ratios)."""
    m = J("site/data/mitigate.json")
    assert [s["shape"] for s in m["shapes"]] == ["reverse", "stride-2", "gather", "matrix multiply"], "the four kernels changed"
    rev_one = statistics.median(mit_ratios("reverse", ("pre", "span"), ("EPYC 7763", "EPYC 9V74")))
    rev45 = mit_ratios("reverse", ("pre", "span"), ("EPYC 9V45",))
    row_ptr = mit_ratios("matrix multiply", ("rowptr",))
    spans1 = mit_ratios("matrix multiply", ("span", "transform"), None, ("L1",))
    spans2 = mit_ratios("matrix multiply", ("span", "transform"), None, ("L2",))
    il2 = mit_ratios("stride-2", ("span_il2",))
    raw2 = mit_ratios("stride-2", ("raw",))
    s2pre = statistics.median(mit_ratios("stride-2", ("pre",), ("EPYC 7763", "EPYC 9V74")))
    tr1 = mit_ratios("matrix multiply", ("transform",), None, ("L1",))
    tr2 = mit_ratios("matrix multiply", ("transform",), None, ("L2",))
    g_orig = mit_ratios("gather", ("orig",), None, ("L1",))
    g1 = mit_ratios("gather", ("pre", "span"), None, ("L1",))
    g2 = mit_ratios("gather", ("pre", "span"), None, ("L2",))
    jobs = m["jobs"]
    usable = [j for j in jobs if j["usable"]]
    assert m["usable_cpus"] == ["EPYC 7763"] and len(usable) == m["usable_jobs"] and len(jobs) == m["job_count"]
    return {
        "one": f2(rev_one), "lo45": f2(min(rev45)), "hi45": f2(max(rev45)),
        "rpl": f2(min(row_ptr)), "rph": f2(max(row_ptr)), "rp1": f2(statistics.median(row_ptr)),
        "sp1l": f2(min(spans1)), "sp1h": f2(max(spans1)), "sp2l": f2(min(spans2)), "sp2h": f2(max(spans2)),
        "ill": f2(min(il2)), "ilh": f2(max(il2)), "rawl": f2(min(raw2)), "rawh": f2(max(raw2)),
        "five": f0(s2pre),
        "tr1l": f2(min(tr1)), "tr1h": f2(max(tr1)), "tr2l": f2(min(tr2)), "tr2h": f2(max(tr2)),
        "gol": f2(min(g_orig)), "goh": f2(max(g_orig)), "g1l": f2(min(g1)), "g1h": f2(max(g1)),
        "g2l": f2(min(g2)), "g2h": f2(max(g2)),
        "go1": f1(min(g_orig)), "go2": f1(max(g_orig)), "g1m": f1(statistics.median(g1)), "g21": f1(min(g2)), "g22": f1(max(g2)),
        "clamp": f1(max(mit_ratios("gather", ("clamp",)))), "valid": f1(max(mit_ratios("gather", ("validate",)))),
        "k": str(len(m["shapes"])), "eight": str(len(m["shapes"]) * 2), "aa": f"{m['aa_max_pct']:.0f}",
        "u": str(m["usable_jobs"]), "n": str(m["job_count"]),
        "pct_lo": f0((min(rev45) - 1) * 100), "pct_hi": f0((max(rev45) - 1) * 100),
        "models": "EPYC 7763, 9V45 and 9V74" if m["cpus"] == ["EPYC 7763", "EPYC 9V74", "EPYC 9V45"] else "?",
        "intel": str(len(jobs) - sum(1 for j in jobs if j["cpu_short"].startswith("EPYC"))),
    }


def mitigate_raw_jobs():
    """The twelve raw job records of the mitigation runs: (run id, job, CPU, usable, stride-2 L1 A/A half-width in %)."""
    out = []
    for path in sorted(glob.glob(os.path.join(REPO, "results", "mitigate-run-*", "*", "results.json"))):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        aa = {k: {sc: v["half_width_pct"] for sc, v in kk["aa"].items()} for k, kk in d["kernels"].items()}
        out.append((d["run"]["id"], d["run"]["job"], d["run"]["cpu_model"], all(x <= 2.0 for k in aa.values() for x in k.values()),
                    aa["m05_stride2"]["L1"]))
    return out


def exp_mitigation_jobs():
    raw = mitigate_raw_jobs()
    usable = [r for r in raw if r[3]]
    assert len(raw) == J("site/data/mitigate.json")["job_count"], "the raw job records and the summary disagree on the job count"
    assert len({r[0] for r in usable}) == 1 and all("7763" in r[2] for r in usable), "the usable jobs are no longer one run on EPYC 7763"
    above = [r for r in raw if r[4] > 2.0]
    return {"u": str(len(usable)), "n": str(len(raw)), "run": usable[0][0], "j1": usable[0][1], "j2": usable[1][1],
            "five": str(len(above)), "mx": f2(max(r[4] for r in raw))}


def exp_details_mitigation():
    s = exp_mitigation_summary()
    return {k: s[k] for k in ("k", "one", "lo45", "hi45", "rpl", "rph", "sp1l", "sp1h", "ill", "ilh")}


def exp_details_mitigate_rule():
    s = exp_mitigation_summary()
    assert s["intel"] == "0", f"{s['intel']} of the mitigation jobs ran on a CPU that is not an EPYC; the text says no Intel model was drawn"
    return {"eight": s["eight"], "aa": s["aa"], "u": s["u"], "n": s["n"], "models": s["models"],
            "pl": s["pct_lo"], "ph": s["pct_hi"]}


def summary_of(*keys):
    return lambda: pick(exp_mitigation_summary(), *keys)


def exp_details_census():
    c = J("site/data/corpus.json")
    c1, c2 = c["census1"]["totals"], c["census2"]["totals"]
    projects = c["census2"]["projects"]
    names = {p["name"] for p in projects}
    assert {"stockfish", "entt"} <= names, f"the numeric census no longer includes Stockfish and EnTT: {sorted(names)}"
    assert c2["projects_with_a_lost_loop"] == sum(1 for p in projects if p["lost"] > 0), "projects_with_a_lost_loop disagrees with the project rows"
    assert c2["lost"] == sum(p["lost"] for p in projects) and c2["none"]["vectorized"] == sum(p["vectorized"] for p in projects)
    lgbm = next(p for p in projects if p["name"] == "lightgbm")
    return {
        "libs": str(c1["projects"]), "lost1": str(c1["lost"]), "vec1": thousands(c1["none"]["vectorized"]),
        "projs": str(c2["projects"]), "lost2": str(c2["lost"]), "vec2": thousands(c2["none"]["vectorized"]),
        "loc": str(c2["lost_unique_locations"]), "locof": str(c2["none"]["vectorized_unique"]),
        "lgbm": str(lgbm["lost"]), "rest": str(c2["lost"] - lgbm["lost"]),
        "restof": thousands(c2["none"]["vectorized"] - lgbm["vectorized"]),
        "none": str(c2["projects"] - c2["projects_with_a_lost_loop"]),
    }


def exp_details_versions_timed():
    v = J("site/data/versions.json")
    tcs = sorted(v["toolchains"], key=lambda t: t["version"])
    assert [t["version"] for t in tcs] == [19, 20, 21] and all(t["form"] == "INCONCLUSIVE" for t in tcs), "the timed toolchains or their forms changed"
    assert v["summary"]["matmul_vectorized_both_all"] is True and v["summary"]["reverse_holds_all"] and v["summary"]["stride2_holds_all"]
    cells = [(t["version"], c["cpu_short"], x) for t in tcs for c in t["cpus"] for x in c["cells"]]
    rev = [x["ratio"] for _, _, x in cells if x["kernel"] == "k04_rev"]
    s2 = [x["ratio"] for _, _, x in cells if x["kernel"] == "k05_stride2"]
    assert (min(rev), max(rev)) == (v["summary"]["reverse_all"]["min"], v["summary"]["reverse_all"]["max"]), "the summary's reverse range is not the cells' range"
    assert (min(s2), max(s2)) == (v["summary"]["stride2_all"]["min"], v["summary"]["stride2_all"]["max"])
    enough = [e["cpu_short"] for e in v["summary"]["enough"]]
    assert enough == ["EPYC 7763"] * 3, f"models with 3 or more jobs on each toolchain (one entry per toolchain): {enough}"
    jobs7763 = [next(c["jobs"] for c in t["cpus"] if c["cpu_short"] == "EPYC 7763") for t in tcs]
    others = {c["jobs"] for t in tcs for c in t["cpus"] if c["cpu_short"] != "EPYC 7763"}
    assert others <= {1, 2}, f"the other models drew {sorted(others)} jobs"
    m7 = [(ver, x) for ver, cpu, x in cells if cpu == "EPYC 7763"]
    rev7 = [x["ratio"] for _, x in m7 if x["kernel"] == "k04_rev"]
    rev21 = [x["ratio"] for ver, x in m7 if x["kernel"] == "k04_rev" and ver == 21]
    s27 = [x["ratio"] for _, x in m7 if x["kernel"] == "k05_stride2"]
    mm = {x["size"]: x["ratio"] for ver, x in m7 if x["kernel"] == "k08_matmul" and ver == 19}
    return {
        "run": v["run_id"], "v1": tcs[0]["clang"], "v2": tcs[1]["clang"], "v3": tcs[2]["clang"], "jobs": str(v["summary"]["jobs"]),
        "rlo": f1(min(rev)), "rhi": f1(max(rev)), "slo": f1(min(s2)), "shi": f1(max(s2)),
        "j1": str(jobs7763[0]), "j2": str(jobs7763[1]), "j3": str(jobs7763[2]),
        "mlo": f1(min(rev7)), "mhi": f1(max(rev7)), "c21lo": f1(min(rev21)), "c21hi": f1(max(rev21)),
        "mslo": f1(min(s27)), "mshi": f1(max(s27)), "m1": f2(mm["L1"]), "m2": f2(mm["L2"]),
        "add": f2(next(x["ratio"] for ver, x in m7 if x["cell_id"] == "k02_add_fwd.L1" and ver == 19)),
        "a18": f1(next(x["clang18"] for ver, x in m7 if x["cell_id"] == "k02_add_fwd.L1" and ver == 19)),
        "mod": str(len(v["toolchains"])),
    }


def exp_details_holdout_compare():
    rows = {r["cpu_short"]: r for r in J("site/data/holdout.json")["rows"]}
    r7, r9, r45, rx = rows["EPYC 7763"], rows["EPYC 9V74"], rows["EPYC 9V45"], rows["Xeon 8573C"]
    assert r7["original"]["jobs"] == r7["holdout"]["jobs"], "7763 no longer has the same job count on both sides"
    assert r7["original"]["form"] == r7["holdout"]["form"] == r9["original"]["form"] == r9["holdout"]["form"] == "map"
    assert (r45["original"]["form"], r45["holdout"]["form"]) == ("map", "inconclusive")
    assert not rx["original"]["enough"] and not rx["holdout"]["enough"], "the Xeon 8573C has enough jobs on a side now"
    return {"j7": str(r7["original"]["jobs"]), "o9": str(r9["original"]["jobs"]), "h9": str(r9["holdout"]["jobs"]),
            "mo": f2(r7["original"]["lost"]["median"]), "mh": f2(r7["holdout"]["lost"]["median"]),
            "o45": str(r45["original"]["jobs"]), "h45": str(r45["holdout"]["jobs"])}


def layout_cpu(short):
    return next(c for c in J("site/data/layout.json")["cpus"] if c["cpu_short"] == short)


def layout_row(short, kernel, size):
    return next(r for r in layout_cpu(short)["rows"] if r["kernel"] == kernel and r["size"] == size)


def exp_details_layout_frame():
    L = J("site/data/layout.json")
    assert L["residues"] == [0, 16, 32, 48] and L["mode"] == "coarse" and L["rules"]["min_jobs"] == 3
    assert sorted(c["cpu_short"] for c in L["cpus"] if not c["enough"]) == ["Xeon 6973P-C", "Xeon 8573C"], "the models below the minimum changed"
    assert all(c["jobs"] < L["rules"]["min_jobs"] for c in L["cpus"] if not c["enough"])
    sums = [r for c in L["cpus"] if c["enough"] for r in c["rows"] if r["kernel"] == "k01_sum_fwd"]
    assert all(r["verdict"] == "ROBUST" for r in sums), "the forward sum is not robust on every model with enough jobs"

    def rev(short):
        rows = [r for r in layout_cpu(short)["rows"] if r["kernel"] == "k04_rev"]
        return f1(min(r["min"] for r in rows)), f1(max(r["max"] for r in rows))

    out = {"p": str(L["placements"]), "a": str(layout_cpu("EPYC 7763")["jobs"]), "b": str(layout_cpu("EPYC 9V74")["jobs"]),
           "c": str(layout_cpu("EPYC 9V45")["jobs"]), "d": str(layout_cpu("Xeon 8573C")["jobs"]), "e": str(layout_cpu("Xeon 6973P-C")["jobs"]),
           "rlo": f1(L["reverse"]["min"]), "rhi": f1(L["reverse"]["max"]),
           "flo": f3(min(r["min"] for r in sums)), "fhi": f3(max(r["max"] for r in sums))}
    out["a1"], out["a2"] = rev("EPYC 7763")
    out["b1"], out["b2"] = rev("EPYC 9V74")
    out["c1"], out["c2"] = rev("EPYC 9V45")
    assert (out["rlo"], out["rhi"]) == (min(out["a1"], out["b1"], out["c1"]), max(out["a2"], out["b2"], out["c2"])), "the reverse range is not the three models' union"
    return out


def exp_details_layout_stencil():
    L = J("site/data/layout.json")
    s7 = layout_row("EPYC 7763", "k03_stencil", "L1")
    s45 = layout_row("EPYC 9V45", "k03_stencil", "L1")
    s74 = layout_row("EPYC 9V74", "k03_stencil", "L2")
    inconclusive = [(c["cpu_short"], r["kernel"], r["size"]) for c in L["cpus"] if c["cpu_short"].startswith("EPYC") for r in c["rows"] if r["verdict"] == "INCONCLUSIVE"]
    assert inconclusive == [("EPYC 9V45", "k03_stencil", "L1")], f"the inconclusive EPYC cells are {inconclusive}"
    assert s7["verdict"] == "PLACEMENT_DEPENDENT" and s74["verdict"] == "MIXED" and s74["n_cost"] == 1
    return {"med": f3(s7["median"]), "nc": str(s7["n_cost"]), "np": str(s7["n_placements"]), "ps": str(s7["n_pass"]),
            "aa": f2(s45["aa_half_width_pct"]), "lim": f"{L['rules']['aa_half_width_max_pct']:.1f}", "mx": f3(s74["max"])}


def exp_details_lostloops():
    base = os.path.join(REPO, "results")
    runs = sorted(glob.glob(os.path.join(base, "lostloops-live-*")))
    assert len(runs) == 1, f"the live-test result folders are {runs}"
    outs = sorted(glob.glob(os.path.join(runs[0], "lostloops-live-*", "out-*", "comparison.json")))
    names = []
    for path in outs:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        assert c["pass"] is True, f"{path}: the comparison with the census lists does not pass"
        names.append(c["project"])
    assert sorted(names) == ["leveldb", "lightgbm", "spectra"], f"projects of the live test: {names}"
    return {"run": os.path.basename(runs[0]).split("-")[-1], "n": word(len(names)), "clang": timed_clang()}


def exp_details_realworld():
    d, rows, groups = realworld()
    t = d["timing"]
    workloads = [n for n, r in rows.items() if not r["control"]]
    projects = {rows[n]["project"] for n in workloads}
    lgbm = [n for n in workloads if rows[n]["project"] == "LightGBM"]
    assert t["jobs"] == sum(groups[c]["jobs"] for c in groups), "the model groups do not add up to the distinct jobs"
    assert [g["cpu_short"] for g in t["groups"]] == ["EPYC 7763", "EPYC 9V45", "EPYC 9V74"] and d["minimum_jobs"] == 3

    def cols(cpu, name):
        v = groups[cpu]["rows"][name]
        return v["fast"]["ratio"], v["aligned"]["ratio"]

    def slower_pct(cpu):
        values = [r for n in slower_rows(cpu) for r in cols(cpu, n)]
        return pct1(min(values)), pct1(max(values))

    def at_most(cpu, name):
        v = groups[cpu]["rows"][name]
        assert v["reading"] == "not detectable", f"{cpu} {name} is {v['reading']}"
        return f1(v["at_most_pct"])

    s74, s45 = sorted(slower_rows("EPYC 9V74")), sorted(slower_rows("EPYC 9V45"))
    assert s74 == ["draco", "lightgbm_default", "lightgbm_linear", "lightgbm_multiclass"], f"EPYC 9V74 slower rows: {s74}"
    assert s45 == ["draco", "lightgbm_default", "lightgbm_multiclass"], f"EPYC 9V45 slower rows: {s45}"
    assert sorted(slower_rows("EPYC 7763")) == ["draco", "lightgbm_default", "lightgbm_linear", "lightgbm_multiclass", "tinydnn"]
    for cpu in groups:
        for c in ("meshopt",):
            assert groups[cpu]["rows"][c]["reading"] == "not detectable", f"{cpu}: the meshoptimizer control is {groups[cpu]['rows'][c]['reading']}"
        assert groups[cpu]["rows"]["fmt"]["reading"] in ("not detectable", "detectably faster"), f"{cpu}: the {{fmt}} control is slower"
    lines = {n: rows[n]["lines_none"] for n in workloads}
    for n in ("lightgbm_default", "lightgbm_multiclass", "draco", "tinydnn"):
        assert rows[n]["lines_none"] < 1 and rows[n]["lines_fast"] < 1, f"{n}: the lost loops' lines are no longer under 1% of the instructions"
    fmt7 = cols("EPYC 7763", "fmt")
    out = {
        "jobs": str(t["jobs"]), "runs": str(len(d["runs"])), "j7": str(groups["EPYC 7763"]["jobs"]), "j45": str(groups["EPYC 9V45"]["jobs"]),
        "j74": str(groups["EPYC 9V74"]["jobs"]), "min": str(d["minimum_jobs"]), "w3": word(len(lgbm)), "six": word(len(workloads)), "four": word(len(projects)),
        "n7": word(len(slower_rows("EPYC 7763"))), "p7": word(len({rows[n]["project"] for n in slower_rows("EPYC 7763")})),
        "n74": word(len(s74)), "n45": word(len(s45)),
        "sp7": at_most("EPYC 7763", "spectra"), "td74": at_most("EPYC 9V74", "tinydnn"), "sp74": at_most("EPYC 9V74", "spectra"),
        "ln45": at_most("EPYC 9V45", "lightgbm_linear"), "td45": at_most("EPYC 9V45", "tinydnn"), "sp45": at_most("EPYC 9V45", "spectra"),
        "ln1": f3(cols("EPYC 9V45", "lightgbm_linear")[0]), "ln2": f3(cols("EPYC 9V45", "lightgbm_linear")[1]),
        "td1": f2(cols("EPYC 9V45", "tinydnn")[0]), "td2": f2(cols("EPYC 9V45", "tinydnn")[1]),
        "fl": pct1(2 - max(fmt7)), "fh": pct1(2 - min(fmt7)),
        "cl": f4(min(lines.values())), "ch": f1(max(lines.values())), "tf": f0(rows["tinydnn"]["funcs_none"]),
        "ne": str(len(t["expect"])), "nh": str(sum(1 for e in t["expect"] if e["held"])),
    }
    out["lo7"], out["hi7"] = slower_pct("EPYC 7763")
    out["lo74"], out["hi74"] = slower_pct("EPYC 9V74")
    out["lo45"], out["hi45"] = slower_pct("EPYC 9V45")
    return out


def exp_details_programs():
    p = J("site/data/index.json")["programs"]
    rows = p["rows"]
    assert len(rows) == 9
    j = [(r["cpu_short"], r["run_label"], r["programs"]["json"]) for r in rows]
    above = [x for x in j if x[2]["ci95"][0] > 1]
    assert [(a[0], a[1]) for a in above] == [("EPYC 7763", "S3 full run"), ("EPYC 7763", "S3 full run"), ("Xeon 8370C", "S3 audit run")], \
        "the json rows with an interval wholly above 1 are not the two 7763 rows of the full run and the 8370C row of the audit run"
    assert all(r["programs"]["fmt"]["ci95"][0] <= 1 for r in rows) and all(r["programs"]["fmt"]["ci95"][1] <= 1.05 for r in rows)
    first, second, third = (a[2] for a in above)
    assert pct1(second["ci95"][0]) == pct1(third["ci95"][0]), "the second and third lower ends no longer round to the same percent"
    repro = next(x for x in j if x[0] == "EPYC 7763" and x[1] == "S3 reproduction run")[2]
    return {
        "alo": f1(p["at_most_pct"]["min"]), "ahi": f1(p["at_most_pct"]["max"]), "flo": f1(p["aa_pct"]["min"]), "fhi": f1(p["aa_pct"]["max"]),
        "k": str(len(above)), "n": str(len(rows)), "six": word(len(rows) - len(above)),
        "l1": pct1(first["ci95"][0]), "a1": f2(first["aa_pct"]), "l2": pct1(second["ci95"][0]), "a2": f2(second["aa_pct"]), "a3": f2(third["aa_pct"]),
        "p1": f3(first["ratio"]), "p2": f3(second["ratio"]), "i1l": f3(first["ci95"][0]), "i1h": f3(first["ci95"][1]),
        "i2l": f3(second["ci95"][0]), "i2h": f3(second["ci95"][1]), "b1": f2(first["aa_pct"]), "b2": f2(second["aa_pct"]),
        "p3": f3(third["ratio"]), "i3l": f3(third["ci95"][0]), "i3h": f3(third["ci95"][1]), "b3": f2(third["aa_pct"]),
        "rp": f3(repro["ratio"]), "rl": f3(repro["ci95"][0]), "rh": f3(repro["ci95"][1]),
    }


GROUP3_DETAILS_ROWS = [
    row("details: the real-program paragraph, jobs and readings per model", "site/data/realworld.json timing.groups (every workload and CPU model), rows (Cachegrind lines and functions), timing.expect", exp_details_realworld,
        r"The workloads are LightGBM with (?P<w3>\w+) option sets \(default, multiclass, linear\), Draco, tiny-dnn and Spectra, picked because they contain lost loops; "
        r"meshoptimizer and \{fmt\} are controls without any\. Pooled per CPU model over (?P<jobs>\d+) distinct jobs in (?P<runs>\d+) runs: AMD EPYC 7763 (?P<j7>\d+) jobs, "
        r"EPYC 9V45 (?P<j45>\d+) jobs, EPYC 9V74 (?P<j74>\d+) jobs \((?P<min>\d+) is the minimum for a reading\)\. The result differs by model\. "
        r"On EPYC 7763, (?P<n7>\w+) of the (?P<six>\w+) workloads \((?P<p7>\w+) of the (?P<four>\w+) projects\) ran detectably slower with the checks on, by "
        r"(?P<lo7>[\d.]+)% to (?P<hi7>[\d.]+)% across the as-compiled and aligned columns; Spectra was not detectable \(at most (?P<sp7>[\d.]+)%\)\. "
        r"On EPYC 9V74, (?P<n74>\w+) of six workloads \(LightGBM default, multiclass and linear, Draco\) were detectable, (?P<lo74>[\d.]+)% to (?P<hi74>[\d.]+)%; "
        r"tiny-dnn \(at most (?P<td74>[\d.]+)%\) and Spectra \(at most (?P<sp74>[\d.]+)%\) were not\. "
        r"On EPYC 9V45, (?P<n45>\w+) of six workloads \(LightGBM default and multiclass, Draco\) were detectable, (?P<lo45>[\d.]+)% to (?P<hi45>[\d.]+)%; "
        r"LightGBM linear \(at most (?P<ln45>[\d.]+)%, and its two columns disagree: (?P<ln1>[\d.]+) as compiled, (?P<ln2>[\d.]+) aligned\), "
        r"tiny-dnn \(at most (?P<td45>[\d.]+)%, and its two columns disagree: (?P<td1>[\d.]+) as compiled, (?P<td2>[\d.]+) aligned\) and Spectra \(at most (?P<sp45>[\d.]+)%\) were not\. "
        r"So \"five of six workloads\" holds on EPYC 7763 only\. On every model the meshoptimizer control was not detectable and the \{fmt\} control was faster or not detectable "
        r"\(on 7763 (?P<fl>[\d.]+)% to (?P<fh>[\d.]+)% faster, a placement effect that was not explained\)\. "
        r"Cachegrind puts the lost loops' own lines at (?P<cl>[\d.]+)% to (?P<ch>[\d.]+)% of executed instructions, so for LightGBM \(default and multiclass\), Draco and tiny-dnn "
        r"\(under 1% on the lines; tiny-dnn's functions hold (?P<tf>\d+)%, so for it this is weaker\).*?"
        r"three AMD CPU models only \((?P=j7), (?P=j45) and (?P=j74) jobs\).*?"
        r"Of the (?P<ne>\d+) expectations written before any run, in the author's unpublished development history, (?P<nh>\d+) held"),
    row("details: the whole-program columns, json and fmt", "site/data/index.json programs (rows, at_most_pct, aa_pct)", exp_details_programs,
        r"json and fmt \(earlier runs, S3\) are \"consistent with at most (?P<alo>[\d.]+)% to (?P<ahi>[\d.]+)%\" over the [\d]+ of [\d]+ jobs whose kernel A/A \(the forward add timed against an identical copy of itself, in the same job\) was at most [\d.]+%; "
        r"the [\d]+ others had a kernel A/A of [\d.]+% to [\d.]+% and bounds up to [\d.]+%\. Each bound is given next to the program's own A/A floor "
        r"\((?P<flo>[\d.]+)% to (?P<fhi>[\d.]+)%, a separate control that can exceed [\d.]+%\); that wording is an upper bound only where the interval includes 1\. "
        r"In (?P<k>\d+) of the (?P<n>\d+) json job rows the interval lies wholly above 1, so a small slowdown is indicated in those rows, not only an upper bound "
        r"\(only for the first does the lower end of the interval, (?P<l1>[\d.]+)% above 1, also clear that job's own A/A floor of (?P<a1>[\d.]+)%; "
        r"for the second and third the lower end, (?P<l2>[\d.]+)% above 1, lies below their floors of (?P<a2>[\d.]+)% and (?P<a3>[\d.]+)%\): "
        r"EPYC 7763 twice in the S3 full run \(point ratios (?P<p1>[\d.]+) and (?P<p2>[\d.]+), intervals (?P<i1l>[\d.]+) to (?P<i1h>[\d.]+) and (?P<i2l>[\d.]+) to (?P<i2h>[\d.]+), "
        r"A/A (?P<b1>[\d.]+)% and (?P<b2>[\d.]+)%\) and Xeon 8370C once in the audit run \((?P<p3>[\d.]+), (?P<i3l>[\d.]+) to (?P<i3h>[\d.]+), A/A (?P<b3>[\d.]+)%\)\. "
        r"The other (?P<six>\w+) json rows, including the 7763 reproduction run \((?P<rp>[\d.]+), (?P<rl>[\d.]+) to (?P<rh>[\d.]+)\), and no fmt row have an interval wholly above 1\."),
    row("details: the census bullet", "site/data/corpus.json census1 and census2 totals and projects", exp_details_census,
        r"In (?P<libs>\d+) libraries \(parsers, JSON/YAML/XML, compression, logging and a few others\): (?P<lost1>\d+) of (?P<vec1>[\d,]+) vectorized loops lost under FAST\. "
        r"In (?P<projs>\d+) numeric, physics, graphics, machine-learning and compression projects \(including Stockfish and EnTT\), listed before compiling, in the author's unpublished development history "
        r"\(\[corpus/PLAN2\.md\]\(\.\./corpus/PLAN2\.md\)\): (?P<lost2>\d+) of (?P<vec2>[\d,]+) lost, at (?P<loc>\d+) of (?P<locof>\d+) distinct source locations\. "
        r"(?P<lgbm>\d+) of the (?P=lost2) are in LightGBM \(without it, (?P<rest>\d+) of (?P<restof>[\d,]+)\), and (?P<none>\d+) of the (?P=projs) projects lose none\."),
    row("details: what to change, the four rewrites", "site/data/mitigate.json shapes[].variants[].per_cpu (every job's ratio)", exp_details_mitigation,
        r"\(measured on (?P<k>\d+) kernels; \[mitigate/README\.md\]\(\.\./mitigate/README\.md\)\):\s+"
        r"- Reverse loop: one up-front size check, or a `std::span` taken once with `first\(n\)`, brings back SIMD with hardening still on: "
        r"(?P<one>[\d.]+)x on EPYC 7763 and 9V74, (?P<lo45>[\d.]+)x to (?P<hi45>[\d.]+)x on 9V45\.\s+"
        r"- Matrix multiply: raw row pointers behind one up-front size check: (?P<rpl>[\d.]+)x to (?P<rph>[\d.]+)x\. "
        r"Row spans keep every access checked and cost (?P<sp1l>[\d.]+)x to (?P<sp1h>[\d.]+)x at L1\.\s+"
        r"- Stride-2: a span plus `#pragma clang loop interleave_count\(2\)`, (?P<ill>[\d.]+)x to (?P<ilh>[\d.]+)x\."),
    row("details: no rewrite is called better, the rule and the jobs", "site/data/mitigate.json (jobs, usable_jobs, aa_max_pct, cpus); the 9V45 reverse ratios", exp_details_mitigate_rule,
        r"a job counts only if all (?P<eight>\d+) of its A/A controls are at most (?P<aa>\d+)%, and only (?P<u>\d+) of (?P<n>\d+) jobs met that \(both on EPYC 7763\)\. "
        r"The mitigation timings are measurements on AMD only \((?P<models>EPYC 7763, 9V45 and 9V74); no Intel model was drawn in (?P=n) jobs\), "
        r"and EPYC 9V45 charges the reverse rewrites (?P<pl>\d+)% to (?P<ph>\d+)% for a reason not found"),
    row("details: the timed newer toolchains", "site/data/versions.json toolchains and summary; tests recompute the ranges from the cells",
        lambda: pick(exp_details_versions_timed(), "run", "v1", "v2", "v3", "jobs", "rlo", "rhi", "slo", "shi", "j1", "j2", "j3", "mlo", "mhi",
                     "c21lo", "c21hi", "mslo", "mshi", "m1", "m2"),
        r"\*\*Newer clang and libc\+\+, timed\*\* \(`versions/`, run (?P<run>\d+)\)\. Clang and libc\+\+ (?P<v1>[\d.]+), (?P<v2>[\d.]+) and (?P<v3>[\d.]+) from apt\.llvm\.org, "
        r"the same harness and eight loops, (?P<jobs>\d+) jobs in one run\. The reverse and stride-2 loops lose SIMD under FAST on every toolchain and CPU model that ran: "
        r"reverse (?P<rlo>[\d.]+)x to (?P<rhi>[\d.]+)x and stride-2 (?P<slo>[\d.]+)x to (?P<shi>[\d.]+)x over all rows; on EPYC 7763, the one model with 3 or more jobs "
        r"on each toolchain \((?P<j1>\d+), (?P<j2>\d+) and (?P<j3>\d+)\), reverse (?P<mlo>[\d.]+)x to (?P<mhi>[\d.]+)x \((?P<c21lo>[\d.]+)x to (?P<c21hi>[\d.]+)x under clang 21\) "
        r"and stride-2 (?P<mslo>[\d.]+)x to (?P<mshi>[\d.]+)x\. Matrix multiply is vectorized in both builds on all three and costs (?P<m1>[\d.]+)x at L1 and (?P<m2>[\d.]+)x at L2 on EPYC 7763"),
    row("details: the timed newer toolchains, the forward add and the forms", "site/data/versions.json EPYC 7763 k02_add_fwd.L1 (clang 19 and clang 18 columns); toolchain forms; other models' job counts",
        lambda: pick(exp_details_versions_timed(), "a18", "add"),
        r"The forward add's (?P<a18>[\d.]+)x as-compiled cost on EPYC 7763 under clang 18 is not seen \((?P<add>[\d.]+)x\)\. "
        r"Every toolchain's form is INCONCLUSIVE under the written rule \(`versions/PLAN\.md`, committed before the run, in the author's unpublished development history\): matrix multiply misses the forward limit, "
        r"and the other CPU models drew 1 or 2 jobs\."),
    row("details: holdout against the original pool", "site/data/holdout.json rows (jobs, forms, medians)", exp_details_holdout_compare,
        r"EPYC 7763 \((?P<j7>\d+) jobs both times\) and 9V74 \((?P<o9>\d+) vs (?P<h9>\d+)\) gave MAP both times with nearly the same costs "
        r"\(7763: median (?P<mo>[\d.]+)x vs (?P<mh>[\d.]+)x\); EPYC 9V45 was MAP with (?P<o45>\d+) jobs and INCONCLUSIVE with (?P<h45>\d+); "
        r"the Xeon 8573C drew too few jobs both times\."),
    row("details: layout sweep, placements, jobs and the reverse loop", "site/data/layout.json cpus, rows, reverse, kernels", exp_details_layout_frame,
        r"Coarse mode: (?P<p>\d+) placements \(the kernel function moved by 0, 16, 32 and 48 bytes, so the hot loop starts at those offsets modulo 64\), "
        r"the placements the compiler can produce itself, not a full sweep\. Four kernels \(forward sum, forward add, stencil, reverse\), sizes L1 and L2, pooled per CPU model: "
        r"EPYC 7763 (?P<a>\d+) jobs, EPYC 9V74 (?P<b>\d+), EPYC 9V45 (?P<c>\d+), Xeon 8573C (?P<d>\d+) and Xeon 6973P-C (?P<e>\d+) "
        r"\(the two Xeon models are below the minimum of 3 jobs: inconclusive\)\. The reverse loop stays (?P<rlo>[\d.]+)x to (?P<rhi>[\d.]+)x at every placement "
        r"on the three EPYC models \(7763: (?P<a1>[\d.]+)x to (?P<a2>[\d.]+)x; 9V74: (?P<b1>[\d.]+)x to (?P<b2>[\d.]+)x; 9V45: (?P<c1>[\d.]+)x to (?P<c2>[\d.]+)x\)\. "
        r"The forward sum is robust everywhere \((?P<flo>[\d.]+) to (?P<fhi>[\d.]+)\)\."),
    row("details: layout sweep, the stencil", "site/data/layout.json rows k03_stencil (EPYC 7763 L1, EPYC 9V45 L1, EPYC 9V74 L2); rules.aa_half_width_max_pct", exp_details_layout_stencil,
        r"The stencil at L1 on 7763 is placement-dependent \(median (?P<med>[\d.]+), (?P<nc>\d+) of (?P<np>\d+) placements cost, (?P<ps>\d+) pass\); "
        r"on 9V45 its L1 cell is the only inconclusive EPYC cell \(A/A half-width (?P<aa>[\d.]+)%, above the (?P<lim>[\d.]+)% limit\); "
        r"on 9V74 its L2 cell is MIXED \(one placement at (?P<mx>[\d.]+)\)\."),
    row("details: the lostloops tool, run live", "results/lostloops-live-*/ comparison.json (pass, project); the timed clang version", exp_details_lostloops,
        r"\*\*The lostloops tool, run live \(`tools/lostloops/`, run (?P<run>\d+), Ubuntu clang (?P<clang>[\d.]+)\)\.\*\* On leveldb, Spectra and LightGBM at the census's pinned commits "
        r"its lists matched the census exactly\. One run on (?P<n>three) projects, not a general guarantee\."),
]

MITIGATE_ROWS = [
    row("mitigate: reverse", "site/data/mitigate.json reverse pre and span (every job)", summary_of("one", "lo45", "hi45"),
        r"\*\*Reverse: yes\.\*\*.*?\*\*(?P<one>[\d.]+)x\*\* of the\s+unchecked original on EPYC 7763 and 9V74, and \*\*(?P<lo45>[\d.]+)x to (?P<hi45>[\d.]+)x\*\* on EPYC 9V45"),
    row("mitigate: stride-2", "site/data/mitigate.json stride-2 pre, span_il2, raw", summary_of("five", "ill", "ilh", "rawl", "rawh"),
        r"`REQUIRE\(a\.size\(\)/2 >= n\)` changes nothing \((?P<five>\d+)x\)\..*?brings it to \*\*(?P<ill>[\d.]+)x to (?P<ilh>[\d.]+)x\*\*\. "
        r"Raw `data\(\)` pointers behind one check: \*\*(?P<rawl>[\d.]+)x to (?P<rawh>[\d.]+)x\*\*"),
    row("mitigate: matrix multiply headline", "site/data/mitigate.json matrix multiply rowptr, span, transform",
        lambda: {**pick(exp_mitigation_summary(), "sp1l", "sp1h", "sp2l", "sp2h"), "rp1": exp_mitigation_summary()["rp1"]},
        r"\*\*Matrix multiply: only with raw row pointers behind one check \((?P<rp1>[\d.]+)x everywhere\)\.\*\* The rewrites that keep\s+every access under hardening "
        r"\(row spans\) stay at \*\*(?P<sp1l>[\d.]+)x to (?P<sp1h>[\d.]+)x at L1\*\* and \*\*(?P<sp2l>[\d.]+)x to (?P<sp2h>[\d.]+)x at L2\*\*"),
    row("mitigate: gather", "site/data/mitigate.json gather orig, pre, span", summary_of("gol", "goh", "g1l", "g1h", "g2l", "g2h"),
        r"Moving only `c\[i\]`'s check up front cuts\s+(?P<gol>[\d.]+)x to (?P<goh>[\d.]+)x down to \*\*(?P<g1l>[\d.]+)x to (?P<g1h>[\d.]+)x at L1\*\* "
        r"\((?P<g2l>[\d.]+)x to (?P<g2h>[\d.]+)x at L2\)"),
    row("mitigate: the rule applied", "site/data/mitigate.json usable_jobs, job_count; the 9V45 reverse ratios", summary_of("u", "n", "lo45", "hi45"),
        r"jobs usable under the whole-job A/A rule \((?P<u>\d+) of (?P<n>\d+) jobs\)\. On EPYC 9V45 the reverse rewrites sit at (?P<lo45>[\d.]+)x to (?P<hi45>[\d.]+)x with"),
    row("mitigate: advice, gather and matrix multiply", "site/data/mitigate.json gather orig, pre, span, clamp, validate; matrix multiply rowptr, transform",
        summary_of("go1", "go2", "g1m", "g21", "g22", "clamp", "valid", "rpl", "rph", "tr1l", "tr1h", "tr2l", "tr2h"),
        r"cuts the cost from (?P<go1>[\d.]+)x to (?P<go2>[\d.]+)x down to (?P<g1m>[\d.]+)x at L1, about (?P<g21>[\d.]+)x to (?P<g22>[\d.]+)x at L2\. .*?a branch-free clamp is slower\s+than the check "
        r"\(up to (?P<clamp>[\d.]+)x\), and a validation pass costs a second read \(up to (?P<valid>[\d.]+)x\)\..*?"
        r"\(overflow-checked\): (?P<rpl>[\d.]+)x to (?P<rph>[\d.]+)x on every CPU drawn\..*?"
        r"`std::transform` over the row, (?P<tr1l>[\d.]+)x to (?P<tr1h>[\d.]+)x at L1 and (?P<tr2l>[\d.]+)x to\s+(?P<tr2h>[\d.]+)x at L2\."),
    row("mitigate: the usable jobs and the stride-2 A/A", "results/mitigate-run-*/*/results.json (kernels[].aa half_width_pct)", exp_mitigation_jobs,
        r"A job is usable only if \*\*all 8\*\* of its A/A half-widths \(4 kernels x 2 sizes\) are at most 2%\. That held in\s+\*\*(?P<u>\d+) of (?P<n>\d+) jobs\*\*, "
        r"both on EPYC 7763 \(run (?P<run>\d+), jobs (?P<j1>\d+) and (?P<j2>\d+)\)\. The stride-2 L1 A/A was above 2% in (?P<five>\d+) of (?P=n)\s+jobs, up to (?P<mx>[\d.]+)%"),
]

ROWS.extend(README_PROV_ROWS)
ROWS.extend(GROUP2_README_ROWS)
DETAILS_ROWS.extend(GROUP3_DETAILS_ROWS)
DETAILS_ROWS.extend(DETAILS_PROV_ROWS)
DETAILS_ROWS.extend(GROUP2_DETAILS_ROWS)
ARM64_ROWS.extend(ARM64_PROV_ROWS)
ROWS.extend(README_NEW_ROWS)
ROWS.extend(README_GUARD_ROWS)
DETAILS_ROWS.extend(DETAILS_NEW_ROWS)
DETAILS_ROWS.extend(DETAILS_GUARD_ROWS)
ARM64_ROWS.extend(ARM64_NEW_ROWS)
ARM64_ROWS.extend(ARM64_GUARD_ROWS)
REPLICATION_ROWS.extend(REPLICATION_GUARD_ROWS)
DSWEEP_ROWS.extend(DSWEEP_GUARD_ROWS)


def exp_dsweep_records_claim():
    """dsweep/PLAN.md (never edited) says its public repository's history is one squashed sync commit and that the first public push should hold the plan
    alone; the provenance record shows more than one public commit and the plan arriving in the same public commit as the code."""
    with open(os.path.join(REPO, "dsweep", "PLAN.md"), encoding="utf-8") as f:
        plan = squash(f.read())
    assert "whose history is one squashed sync commit" in plan and "The first public push should contain this file alone, before the workflow and the code" in plan, (
        "dsweep/PLAN.md no longer says what the README says it says")
    p = prov()
    assert p["public_history"]["commits_on_main_when_read"] > 1, "the provenance record no longer shows a public history of more than one commit"
    assert {"dsweep/PLAN.md", "dsweep/sweep.py", "dsweep/analyze.py"} <= set(p["dsweep_public"]["paths_in_that_commit"]), "the plan no longer reaches the public history with the code"
    return {}


def exp_pool_steps_typed():
    """site/data/index.json pooled.steps: the three sizes of the kernel pool (original, plus the ten later runs, plus the two newest) against the pooled files, and
    the jobs of the last two runs (the step from the second to the third)."""
    steps = J("site/data/index.json")["pooled"]["steps"]
    jobs = [s["jobs"] for s in steps]
    assert len(jobs) == 3, f"index.json pooled.steps holds {len(jobs)} pools"
    assert jobs == [pooled_jobs(original=True), pooled_jobs(pool=POOLED_S6), pooled_jobs()], f"index.json pooled.steps {jobs} against the pooled files"
    newest = newest_runs()
    assert newest["runs"] == 2 and jobs[2] - jobs[1] == newest["returned"], f"the last two runs returned {newest['returned']} jobs; the pool grew by {jobs[2] - jobs[1]}"
    return {"a": str(jobs[0]), "b": str(jobs[1]), "c": str(jobs[2]), "last": str(newest["returned"])}


def exp_pool_size_now():
    """The size of the pool that the README says a laptop was not re-timed with: the last step of index.json pooled.steps, which is the pool the page uses."""
    jobs = J("site/data/index.json")["pooled"]["steps"][-1]["jobs"]
    assert jobs == pooled_jobs(), f"index.json pooled.steps ends at {jobs}, the pooled file has {pooled_jobs()}"
    return {"n": str(jobs)}


DETAILS_ROWS.append(row("details: the pool grew from 30 to 75 to 95 jobs, and the jobs of the last two runs", "site/data/index.json pooled.steps; results/s4-pooled, s6-pooled and s7-pooled pooled.json; results/s7-run-* folders",
                        exp_pool_steps_typed,
                        r"The kernel pool also grew from (?P<a>\d+) to (?P<b>\d+) to (?P<c>\d+) jobs by further runs requested after the verdicts of the smaller pool were known, "
                        r"with no stopping rule written beforehand \(the (?P<last>\d+) jobs of the last two runs were dispatched"))
ROWS.append(row("README: the pool a laptop was not re-timed with", "site/data/index.json pooled.steps (the last step); results/s7-pooled/pooled.json",
                exp_pool_size_now, r"\(a laptop was not re-timed with the (?P<n>\d+)-job pool\)"))
DSWEEP_ROWS.append(row("dsweep/README: the plan's Records section calls the public history one squashed commit with a plan-first push; neither was so",
                       "dsweep/PLAN.md (read); tests/data/s9_s10_provenance.json public_history and dsweep_public", exp_dsweep_records_claim,
                       r"The plan's own \"Records\" section describes the public history as one squashed sync commit and says the first public push should hold the plan alone; "
                       r"neither was so, since the public history has more than one commit and the plan reached it together with the code\. "
                       r"The plan is not edited, because its hash is stored in every result file\."))
DETAILS_ROWS.append(row("details: the d-sweep plan's Records section calls the public history one squashed commit with a plan-first push; neither was so",
                        "dsweep/PLAN.md (read); tests/data/s9_s10_provenance.json public_history and dsweep_public", exp_dsweep_records_claim,
                        r"The plan's own \"Records\" section calls the public history one squashed sync commit with the plan pushed alone first; neither was so\."))

ROBUSTNESS_DETAILS_ROWS = [
    row("details: run to run, against exactly calibrated intervals", "robustness/calibration.json run_to_run s7 (EPYC 7763, 9V74) and s6 (EPYC 7763), families of cells",
        exp_details_calibrated,
        r"Exactly calibrated intervals would put (?P<e7>[\d.]+) and (?P<e9>[\d.]+) of those outside \(95% range for independent comparisons: (?P<l7>\d+) to (?P<h7>\d+) and (?P<l9>\d+) to (?P<h9>\d+)\), "
        r"so the totals alone do not show intervals that are too narrow: EPYC 7763's (?P<o7>\d+) lie inside that range, EPYC 9V74's (?P<o9>\d+) below it\. "
        r"The excess on EPYC 7763 is in the reverse, stride-2 and matrix-multiply cells \((?P<fo>\d+) of (?P<fn>\d+) outside against (?P<fe>[\d.]+) expected\), "
        r"not in the forward ones \((?P<go>\d+) of (?P<gn>\d+) against (?P<ge>[\d.]+)\)\..*?"
        r"EPYC 7763's counts in both pools lie inside the calibrated range \((?P<l6>\d+) to (?P<h6>\d+) of (?P<n6>\d+) in the 75-job pool\), so the rise is not shown to be more than chance"),
    row("details: the rule reads the A/A at L1 only", "robustness/aa-l2.json criteria.aa_half_width_max_pct", exp_details_aa_l2_intro,
        r"The rules read the identical-binary A/A of the forward add at L1 only \(ceiling (?P<ceil>\d+)%\)"),
    row("details: the A/A at L2, what the table shows", "robustness/aa-l2.json s7 and s8-arm; the seed file's stencil interval and the Arm pool's forward add interval at L2",
        exp_details_aa_l2_paragraph,
        r"The pooled L2 half-width is at most (?P<mx>[\d.]+)% on (?P<nf>\w+) x86-64 models and above the (?P<ceil>\d+)% ceiling on the Xeon 6973P-C \((?P<x2>[\d.]+)%\) "
        r"and the Arm core \((?P<a2>[\d.]+)%\); in both, the A/A is about as wide as the interval of the cell that decides the word "
        r"\(the stencil at L2 for the 6973P-C, the forward add at L2 for the Arm core\), so for those two words the noise of an unchanged binary at that size is "
        r"about the size of what the deciding cell's interval can resolve\."),
]

ARM64_ROBUSTNESS_ROWS = [
    row("arm64: run to run, against exactly calibrated intervals", "robustness/calibration.json run_to_run s8-arm and s9-arm-ab (k05_stride2.L2, all cells)", exp_arm_calibrated,
        r"In those stride-2 cells (?P<so>\d+) of (?P<sn>\d+) comparisons fall outside, against (?P<se>[\d.]+) expected if the intervals were exactly calibrated; over all 16 cells "
        r"the count is below that expectation \((?P<ao>\d+) of (?P<an>\d+), against (?P<ae>[\d.]+)\)\. With the six runs of sets A and B pooled together \(secondary\) "
        r"the stride-2 cells at L2 have (?P<bo>\d+) of (?P<bn>\d+) outside against (?P<be>[\d.]+) expected, and all in-cache cells (?P<co>\d+) of (?P<cn>\d+) against (?P<ce>[\d.]+) "
        r"\(\[calibration baseline\]\(\.\./robustness/README-calibration\.md\)\)\."),
]

DETAILS_ROWS.extend(ROBUSTNESS_DETAILS_ROWS)
ARM64_ROWS.extend(ARM64_ROBUSTNESS_ROWS)

AA_L2_TABLE_HEADER = ("| CPU model | jobs | pooled A/A half-width at L1 | pooled A/A half-width at L2 | jobs with their own half-width above 2% at L2 |")
AA_L2_TABLE_ROWS = (("AMD EPYC 7763", "s7", "7763"), ("AMD EPYC 9V74", "s7", "9V74"), ("AMD EPYC 9V45", "s7", "9V45"),
                    ("Intel Xeon Platinum 8573C", "s7", "8573C"), ("Intel Xeon 6973P-C", "s7", "6973P-C"), ("Arm Neoverse-N2", "s8-arm", "Neoverse-N2"))


def aa_l2_table_rows():
    """The details table of the identical-binary A/A at L1 and L2, line by line, from robustness/aa-l2.json (header, separator not included, then one row per model)."""
    out = [AA_L2_TABLE_HEADER]
    for label, pool, key in AA_L2_TABLE_ROWS:
        m = aa_l2_model(pool, key)
        out.append(f"| {label} | {m['jobs']} | {m['l1']['half_width_pct']:.3f}% | {m['l2']['half_width_pct']:.3f}% | {m['l2']['jobs_above_ceiling']} of {m['jobs']} |")
    return out


def test_details_aa_l2_table_matches_the_data():
    check_table_rows("details: the A/A at L1 and L2", aa_l2_table_rows(), details_text(), "readme-parts/DETAILS.md")


# Rows whose typed number is wrong against the data: label -> reason. None at the time of writing.
# Add a row here (the test then needs to keep failing, strict) instead of editing the data to fit.
XFAIL = {}


# ---- the checks --------------------------------------------------------------------------------

def check_row(row, text=None, doc="README.md"):
    label, source, expected_fn, pattern = row
    text = readme_text() if text is None else text
    matches = list(re.finditer(pattern, text, re.S))
    assert matches, (f"{label}: no sentence of {doc} matches the anchor, so the sentence was reworded "
                     f"or removed; update this row (tests/test_readme_numbers.py) or the text.\n  anchor: {pattern}")
    expected = expected_fn()
    for m in matches:
        for name, want in expected.items():
            got = m.group(name) if name in m.re.groupindex else None
            assert got is not None, f"{label}: the row expects a value '{name}' that the anchor does not capture"
            assert got.lower() == want.lower(), (
                f"{label}: {doc} types '{got}' for '{name}' but the data gives '{want}' "
                f"(source: {source}).\n  sentence: {m.group(0)[:300]}")
        for name in m.re.groupindex:
            assert name in expected, f"{label}: the anchor captures '{name}' but the row has no expected value for it"


if pytest is not None:
    def _param(row):
        marks = []
        if row[0] in XFAIL:
            marks.append(pytest.mark.xfail(strict=True, reason=XFAIL[row[0]]))
        return pytest.param(row, id=row[0], marks=marks)

    @pytest.mark.parametrize("row", [_param(r) for r in ROWS])
    def test_readme_number(row):
        check_row(row)

    @pytest.mark.parametrize("row", [_param(r) for r in DETAILS_ROWS])
    def test_details_number(row):
        check_row(row, details_text(), "readme-parts/DETAILS.md")

    @pytest.mark.parametrize("row", [_param(r) for r in SIBLINGS_ROWS])
    def test_siblings_number(row):
        check_row(row, siblings_text(), "siblings/README.md")

    @pytest.mark.parametrize("row", [_param(r) for r in CESWEEP_ROWS])
    def test_cesweep_number(row):
        check_row(row, cesweep_text(), "ce-sweep/README.md")

    @pytest.mark.parametrize("row", [_param(r) for r in ARM64_ROWS])
    def test_arm64_number(row):
        check_row(row, arm64_text(), "arm64/README.md")

    @pytest.mark.parametrize("row", [_param(r) for r in REPLICATION_ROWS])
    def test_replication_number(row):
        check_row(row, replication_text(), "replication/README.md")

    @pytest.mark.parametrize("row", [_param(r) for r in DSWEEP_ROWS])
    def test_dsweep_number(row):
        check_row(row, dsweep_text(), "dsweep/README.md")

    @pytest.mark.parametrize("row", [_param(r) for r in MITIGATE_ROWS])
    def test_mitigate_number(row):
        check_row(row, mitigate_text(), "mitigate/README.md")
else:
    def test_readme_numbers_all_rows():
        failures = []
        for rows, text, doc in ((ROWS, readme_text(), "README.md"), (DETAILS_ROWS, details_text(), "readme-parts/DETAILS.md"),
                                (SIBLINGS_ROWS, siblings_text(), "siblings/README.md"), (CESWEEP_ROWS, cesweep_text(), "ce-sweep/README.md"),
                                (ARM64_ROWS, arm64_text(), "arm64/README.md"), (REPLICATION_ROWS, replication_text(), "replication/README.md"),
                                (DSWEEP_ROWS, dsweep_text(), "dsweep/README.md"), (MITIGATE_ROWS, mitigate_text(), "mitigate/README.md")):
            for row in rows:
                try:
                    check_row(row, text, doc)
                    if row[0] in XFAIL:
                        failures.append(f"{row[0]}: expected to fail ({XFAIL[row[0]]}) but passed")
                except AssertionError as e:
                    if row[0] not in XFAIL:
                        failures.append(str(e))
        assert not failures, "\n".join(failures)


# ---- the tables of the replication and d-sweep sections, line by line --------------------------------

REPL_HEADER = "| CPU model | earlier pool | replication set | same word | points inside | both pooled (secondary) |"
DS_WORDS_HEADER = ("| CPU model | jobs (runs) | as compiled: word (fixed share [95%]) | aligned: word (fixed share [95%]) | registered word |")
DS_SIZES_HEADER = "| d | d mod 8 | role | as compiled | aligned | excess ns, as compiled | excess ns, aligned | extra instructions |"
REPL_FILES_HEADER = "| Pool | Jobs | Folder | Role |"
DS_README_HEADER = "| CPU model | Jobs (runs) | Word |"


def test_details_replication_table_matches_the_data():
    text = details_text()
    check_table_rows("details: replication table", [REPL_HEADER] + repl_table_rows(), text, "readme-parts/DETAILS.md")


def test_details_dsweep_tables_match_the_data():
    text = details_text()
    check_table_rows("details: d-sweep words table", [DS_WORDS_HEADER] + ds_words_table_rows(), text, "readme-parts/DETAILS.md")
    check_table_rows("details: d-sweep sizes table", [DS_SIZES_HEADER] + ds_sizes_table_rows(), text, "readme-parts/DETAILS.md")


def test_replication_readme_files_table_matches_the_data():
    check_table_rows("replication/README: pools table", [REPL_FILES_HEADER] + repl_files_table_rows(), replication_text(), "replication/README.md")


def test_dsweep_readme_words_table_matches_the_data():
    check_table_rows("dsweep/README: words table", [DS_README_HEADER] + ds_readme_words_rows(), dsweep_text(), "dsweep/README.md")


GUARDED_DOCS = {"README.md": readme_text, "readme-parts/DETAILS.md": details_text, "arm64/README.md": arm64_text,
                "replication/README.md": replication_text, "dsweep/README.md": dsweep_text, "gaps/GAPS.md": gaps_text}


def guarded_sentences():
    return J("tests/data/guarded_sentences.json")["sentences"]


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


def check_guarded_sentence(entry):
    assert entry["doc"] in GUARDED_DOCS, f"{entry['doc']} is not one of the documents this test reads"
    assert squash(entry["sentence"]) in squash(GUARDED_DOCS[entry["doc"]]()), (
        f"{entry['doc']} no longer holds this sentence word for word (reworded, reversed or deleted); it states a caveat, a rule, an order of events "
        f"or a verdict word that no row ties to data. Update the document back, or the list tests/data/guarded_sentences.json on purpose:\n  {entry['sentence']}")


if pytest is not None:
    @pytest.mark.parametrize("entry", [pytest.param(e, id=f"{e['doc']}: {e['sentence'][:70]}") for e in guarded_sentences()])
    def test_guarded_sentence_is_present(entry):
        check_guarded_sentence(entry)
else:
    def test_guarded_sentences_are_present():
        for e in guarded_sentences():
            check_guarded_sentence(e)


def test_the_guarded_sentence_list_covers_the_listed_caveats():
    """At least one guarded sentence for each of the five documents, and each sentence listed once."""
    entries = guarded_sentences()
    assert {e["doc"] for e in entries} == set(GUARDED_DOCS), "a document has no guarded sentence"
    assert len({(e["doc"], e["sentence"]) for e in entries}) == len(entries), "a sentence is listed twice"


NIST_SETUP_WORDS = ("Dell Precision T5400", "Xeon X5450", "Linux", "Turbo Boost", "SpeedStep", "frequency scaling", "63 runs per cell")


def test_the_related_work_table_does_not_call_the_nist_study_bare_metal():
    """The NIST paper's Table 1 names a Dell Precision T5400 PC with two Xeon X5450 CPUs under Linux, and the paper uses "bare metal" only for
    a measurement it proposes as future work. It calls the machine neither a server nor a workstation."""
    row = next(ln for ln in gaps_text().splitlines() if ln.startswith("| Flater and Guthrie (NIST)"))
    assert all(w in row for w in NIST_SETUP_WORDS), f"the NIST row no longer names the setup: {[w for w in NIST_SETUP_WORDS if w not in row]}"
    assert "bare" not in row.lower(), "the NIST row calls its setup bare metal"
    assert not re.search(r"\b(?:server|workstation)\b", row, re.I), "the NIST row calls the machine a server or a workstation; the paper's Table 1 says PC"


def test_the_nist_setup_reads_the_same_in_gaps_and_in_the_page_data():
    """gaps/GAPS.md (the reading notes) and site/data/related.json (what the page prints) describe the NIST machine in the same words: the model,
    the CPUs, Linux, no Turbo Boost, no frequency scaling, SpeedStep off, 63 runs per cell, and neither says server, workstation or bare metal."""
    row = next(ln for ln in gaps_text().splitlines() if ln.startswith("| Flater and Guthrie (NIST)"))
    nist = next(s for s in J("site/data/related.json")["sources"] if s["id"] == "nist")
    for name, text in (("gaps/GAPS.md", row), ("site/data/related.json", nist["measured"] + " " + nist["m_short"])):
        assert all(w in text for w in NIST_SETUP_WORDS), f"{name} no longer names the NIST setup: {[w for w in NIST_SETUP_WORDS if w not in text]}"
        assert not re.search(r"\b(?:server|workstation)\b|bare[\s-]*metal|dual[\s-]*(?:socket|die|processor|cpu)", text, re.I), (
            f"{name} calls the NIST machine a server, a workstation, bare metal or dual-socket (the paper's Table 1 says 2 x Xeon X5450 in a Dell Precision T5400 PC)")
        assert "a PC with two Xeon X5450 CPUs" in text or name == "gaps/GAPS.md", f"{name} no longer says 'a PC with two Xeon X5450 CPUs'"


def test_the_acm_queue_row_says_it_could_not_be_rechecked():
    row = next(ln for ln in gaps_text().splitlines() if ln.startswith("| Dionne, Rebert"))
    read = row.split("|")[3]  # the "what was read" cell
    assert "HTTP 403" in read and "unconfirmed" in read
    assert '"' not in read, "the cell quotes the article in quotation marks; it paraphrases (the figures are unconfirmed)"


LICENCE_FILE_NAMES = re.compile(r"^(licen[cs]e|copying|unlicense|notice)(\.[a-z]+)?$", re.IGNORECASE)


def licence_files():
    """Licence-looking files in the repository root and in tools/lostloops/ (the places a reader would look for one)."""
    found = []
    for folder in ("", "tools/lostloops"):
        base = os.path.join(REPO, folder)
        found += [os.path.join(folder, n) for n in os.listdir(base) if LICENCE_FILE_NAMES.match(n) and os.path.isfile(os.path.join(base, n))]
    return sorted(found)


def test_the_licence_file_is_the_mit_licence_and_the_readme_says_so():
    """The README's last section names the MIT licence and the file LICENSE, and says the LLVM excerpts are not covered; the file is the standard
    MIT text for the author, and no other licence-looking file sits in the root or in tools/lostloops/ (the places a reader would look)."""
    assert licence_files() == ["LICENSE"], f"expected exactly the file LICENSE, found: {licence_files()}"
    with open(os.path.join(REPO, "LICENSE"), encoding="utf-8") as f:
        text = f.read()
    assert text.startswith("MIT License\n\nCopyright (c) 2026 Jacobo Pacheco\n\nPermission is hereby granted, free of charge"), text[:120]
    assert "THE SOFTWARE IS PROVIDED \"AS IS\"" in text and text.rstrip().endswith("DEALINGS IN THE\nSOFTWARE.")
    readme = squash(readme_text())
    assert "are under the MIT licence (the file `LICENSE`)" in readme and "no licence file" not in readme
    assert "llvm-src/` are not covered by it" in readme


def test_the_llvm_excerpts_carry_a_notice_that_matches_the_folder():
    """investigate/vectorizer/matmul/llvm-src/NOTICE says what the 19 files are: 14 excerpts that each start with the licence header line, 3 GitHub API
    answers, one list of matching lines and one list of hashes. The counts and the licence name are checked against the folder."""
    folder = os.path.join(REPO, "investigate", "vectorizer", "matmul", "llvm-src")
    with open(os.path.join(folder, "NOTICE"), encoding="utf-8") as f:
        notice = squash(f.read())
    names = sorted(n for n in os.listdir(folder) if n != "NOTICE")
    header = "// LLVM is licensed under Apache-2.0 with LLVM exceptions."
    excerpts = []
    for n in names:
        with open(os.path.join(folder, n), encoding="utf-8") as f:
            if f.readline().startswith(header):
                excerpts.append(n)
    assert len(names) == 19 and "What the 19 files are" in notice, f"{len(names)} files in llvm-src/ (NOTICE says 19): {names}"
    assert len(excerpts) == 14 and "14 files (" in notice, f"{len(excerpts)} files start with the licence header (NOTICE says 14)"
    api = [n for n in names if n.endswith(".json")]
    assert len(api) == 3 and "3 files (commit_39b0cbe69c.json, commit_b6a8f5486b.json and commit_in_tag.json)" in notice
    assert "Apache License 2.0 with LLVM Exceptions" in notice and "https://github.com/llvm/llvm-project" in notice
    assert "indvars_predicate_traps.txt" in notice and "collectLoopUniforms_sha256.txt" in notice
    for n in excerpts:  # the 14 are exactly the files the NOTICE describes by pattern
        assert n.endswith(".cpp.txt") or n.startswith(("legality_", "x86_")), f"{n} starts with the LLVM header but the NOTICE does not describe it"


def test_the_replication_pooled_files_list_every_job_of_their_runs():
    """The s9 pooled files name the runs they pool; each run's job folders must all be in the pooled file (a job left out would change the counts typed above)."""
    pools = repl()["pools"]
    for arch, folder_glob in (("arm", "results/s9-arm-run-"), ("x86", "results/s9-run-")):
        runs = {r: len(glob.glob(os.path.join(REPO, folder_glob + r, "results-*", "results.json"))) for r in pools[arch]["replication"]["runs"]}
        assert sum(runs.values()) == pools[arch]["replication"]["jobs"], f"{arch}: the run folders hold {sum(runs.values())} jobs, the pooled file {pools[arch]['replication']['jobs']}"


def test_the_replication_plan_is_the_one_the_comparison_was_made_against():
    """The comparison file stores the plan's hash (the order in which the plan and the runs were made cannot be shown by a hash)."""
    with open(os.path.join(REPO, "replication", "PLAN.md"), "rb") as f:
        digest = hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    assert digest == repl()["plan_sha256"], "replication/PLAN.md differs from the plan the comparison was made against"


def test_the_holdout_column_compares_verdict_words_only():
    """replication/README.md says the holdout table's "Reproduced" column compares verdict words only, so it is no precedent for the
    count of points inside an interval (the plan's description "as in the holdout column of the page" was wrong)."""
    rows = J("site/data/holdout.json")["rows"]
    assert rows, "the holdout data has no rows"
    for r in rows:
        assert set(r) == {"cpu_model", "cpu_short", "original", "holdout", "reproduced"}, f"{r['cpu_short']}: the holdout row has other fields: {sorted(r)}"
        o, h = r["original"], r["holdout"]
        both = bool(o and h and o["enough"] and h["enough"])
        assert r["reproduced"] == ((o["form"] == h["form"]) if both else None), f"{r['cpu_short']}: 'reproduced' is not verdict-word equality"
        for side in (o, h):
            if side:
                assert not ({"inside", "points", "points_inside", "interval"} & set(side)), f"{r['cpu_short']}: a holdout side now holds a count of points inside an interval"


def test_the_plan_describes_the_share_as_the_holdout_columns():
    """The sentence replication/README.md calls wrong is in the plan, in these words (the plan itself is never edited)."""
    with open(os.path.join(REPO, "replication", "PLAN.md"), encoding="utf-8") as f:
        text = f.read()
    assert "whether the new set's pooled aligned ratio lies inside the earlier pool's interval, reported as a share, as in the holdout column of the page" in text


# ---- the data behind a few rows, cross-checked against the raw pooled file -----------------------

def test_page_lost_range_matches_the_pooled_file():
    """index.json's page.lost (typed into the README) against the pooled file it was derived from."""
    index = J("site/data/index.json")
    pooled = J(POOLED)
    minimum = index["criteria"]["minimum_jobs"]
    values = [c[column]["ratio"] for cpu in pooled["cpus"] if cpu["jobs"] >= minimum
              for c in cpu["cells"] if c["class"] == "lost" for column in ("as_compiled", "aligned")]
    page = index["page"]["lost"]
    assert abs(min(values) - page["min"]) < 1e-9, f"lowest lost-loop ratio: pooled file {min(values)}, page {page['min']}"
    assert abs(max(values) - page["max"]) < 1e-9, f"highest lost-loop ratio: pooled file {max(values)}, page {page['max']}"


def test_realworld_slow_range_matches_the_timing_summary():
    d, _, _ = realworld()
    expected = exp_realworld_bullet()
    slow = d["timing"]
    assert pct1(slow["slow_min"]) == expected["lo"] and pct1(slow["slow_max"]) == expected["hi"], (
        f"timing.slow_min/slow_max give {pct1(slow['slow_min'])}% to {pct1(slow['slow_max'])}%, "
        f"the rows give {expected['lo']}% to {expected['hi']}%")


def test_no_lost_loop_among_the_libcxx_headers():
    totals = J("site/data/corpus.json")["census1"]["totals"]
    assert totals["lost_by_origin"]["libc++"] == 0, "the README says none of the libc++ loops was lost"


def test_controls_show_no_detectable_slowdown():
    _, rows, groups = realworld()
    for cpu, g in groups.items():
        for name, v in g["rows"].items():
            if rows[name]["control"]:
                assert v["reading"] != "detectably slower", f"{name} on {cpu} reads detectably slower; the README says no control did"


def test_the_one_avx2_exception_is_alone():
    """The README says one AVX2 exception above the forward range on the AMD models."""
    amd = {c["cpu_short"] for c in amd_cpus()}
    top = J("site/data/index.json")["page"]["forward"]["aligned"]["max"]
    above = [(k, cpu, size) for k in ("k01_sum_fwd", "k02_add_fwd", "k03_stencil")
             for v, cpu, size, _ in sibling_values("clang18v3-fast", k, cpus=amd) if v > top + 0.005]
    assert len(set(above)) == 1, f"forward cells above {top:.3f} on the AMD models in the AVX2 setup: {sorted(set(above))}"


def test_default_hero_is_epyc_7763():
    assert J("site/data/index.json")["default_cpu"] == "epyc-7763", "the caption under the image names EPYC 7763"


def test_every_intel_model_loses_the_same_loops():
    """README: the Intel CPUs lost the same loops."""
    index = J("site/data/index.json")
    floor = index["criteria"]["lost_ci_lo_min_ratio"]
    for c in index["cpus"]:
        if c["cpu_short"].startswith("Xeon"):
            assert c["lost"]["min"] >= floor, f"{c['cpu_short']}: a lost loop costs only {c['lost']['min']:.2f}x"


# ---- every repository path the prose cites must exist -----------------------------------------------

CITING = ("README.md", "readme-parts/DETAILS.md", "siblings/README.md", "variants/RESULTS.md", "arm64/README.md", "ce-sweep/README.md",
          "replication/README.md", "dsweep/README.md", "forwardt/README.md", "corpus/README.md", "mitigate/README.md", "realworld/README.md",
          "investigate/vectorizer/matmul/README.md", "investigate/vectorizer/reverse-stride2/README.md", "gaps/GAPS.md", "gaps/GAPS-2.md",
          "tools/lostloops/README.md")
# Documents that also name their own files by a bare name, relative to the document's folder (`lostloops.py`, `evidence/`): a span that is only a
# Python file name or a folder name is resolved there. Other bare names in these documents are outputs of the tool (report.md, compile_commands.json).
FOLDER_RELATIVE = ("tools/lostloops/README.md",)
# A document that is not in the public export (the export removes it). It is checked wherever it exists; any other document of CITING that is
# missing is a failure.
CITING_NOT_EXPORTED = ("gaps/GAPS-2.md",)


def citing_present():
    return [d for d in CITING if os.path.exists(os.path.join(REPO, d)) or d not in CITING_NOT_EXPORTED]
# Planning documents that are not published. The note appended to DETAILS.md in the public export names them on purpose,
# saying that they do not exist in the repository, so they are not counted as broken citations.
UNPUBLISHED = {"docs/PLAN.md", "docs/SPEC.md", "docs/skeptic.md"}
CITED_ROOTS = ("results/", "dayone/", "investigate/", "tests/", "harness/", "siblings/", "variants/", "ce-sweep/", "layout-sweep/",
               "pgo/", "versions/", "environment/", "robustness/", "mitigate/", "corpus/", "realworld/", "audit/", "kernels/",
               "programs/", "scripts/", "site/", "tools/", "docs/", "gaps/", "claims-audit/", ".github/", "arm64/", "replication/", "dsweep/", "forwardt/")


GH_WORKFLOW_RUN = re.compile(r"gh workflow run ([\w.-]+\.ya?ml)")
PYTHON_IN_FOLDER = re.compile(r"`python3? ([\w./-]+\.py)(?: [^`]*)?` in `([^`]+/)`")
FENCE = re.compile(r"^```[^\n]*\n(.*?)^```[ \t]*$", re.S | re.M)


def tokens_that_name_paths(span):
    """The whitespace-separated pieces of a command or code span that start at a folder of the repository. A piece with a placeholder
    (<>{}|$=) is not a path; one with a * is a pattern that must match something."""
    for tok in span.split():
        tok = tok.strip("\"'(),;:").rstrip("\"'),;:.")  # "corpus/projects.json)." in a comment names corpus/projects.json
        if tok.startswith(CITED_ROOTS) and tok not in UNPUBLISHED and not re.search(r"[<>{}|$=]", tok):
            yield tok


def cited_paths_in(text, doc):
    """(shown, repository-relative path) for every path a text names: in backticked spans and in fenced blocks, command words included
    (split on whitespace); `gh workflow run X.yml` names a workflow file; `python X.py` in `folder/` names folder/X.py; and the files its
    Markdown links point at (relative to doc, which is the document's own path)."""
    out = []
    spans = []
    for block in FENCE.findall(text):
        spans.append(block)
    prose = FENCE.sub("", text)
    spans += re.findall(r"`([^`\n]+)`", prose)
    for span in spans:
        for tok in tokens_that_name_paths(span):
            if "*" in tok or "?" in tok:
                # "NN" in a pattern stands for a two-digit number (kernels/kNN_*.cpp)
                hit = sorted(glob.glob(os.path.join(REPO, tok.replace("NN", "[0-9][0-9]"))))
                out.append((tok, os.path.relpath(hit[0], REPO).replace("\\", "/") if hit else tok))
            else:
                out.append((tok, tok))
        for wf in GH_WORKFLOW_RUN.findall(span):
            out.append((f"gh workflow run {wf}", f".github/workflows/{wf}"))
    for script, folder in PYTHON_IN_FOLDER.findall(prose):
        out.append((f"{folder}{script}", f"{folder}{script}"))
    if doc in FOLDER_RELATIVE:
        for span in re.findall(r"`([^`\n]+)`", prose):
            if re.fullmatch(r"[\w-]+(?:\.py|/)", span):
                out.append((span, os.path.join(os.path.dirname(doc), span).replace("\\", "/")))
    for target in re.findall(r"\]\(([^)\s#]+)(?:#[^)\s]*)?\)", prose):
        if not re.match(r"[a-z]+:", target):
            out.append((target, os.path.normpath(os.path.join(os.path.dirname(doc), target)).replace("\\", "/")))
    return out


def cited_paths(doc):
    with open(os.path.join(REPO, doc), encoding="utf-8") as f:
        return cited_paths_in(f.read(), doc)


def cited_exists(doc, rel):
    """A cited path exists relative to the repository root or, for the documents in FOLDER_RELATIVE (a tool's README that mixes both
    styles: `tests/fake_clang.py` is in the tool's folder, `corpus/projects.json` at the root), relative to the document's folder."""
    return os.path.exists(os.path.join(REPO, rel)) or (doc in FOLDER_RELATIVE and os.path.exists(os.path.join(REPO, os.path.dirname(doc), rel)))


def missing_cited(text, doc="README.md"):
    return sorted({shown for shown, rel in cited_paths_in(text, doc) if not cited_exists(doc, rel)})


def test_cited_paths_sees_commands_with_spaces_and_fenced_blocks():
    """A path that sits inside a command is checked: the old guard skipped any span that contained a space."""
    assert missing_cited("`python replication/compare.py --verify`") == []
    assert missing_cited("`python replication/compare.pyy --verify`") == ["replication/compare.pyy"]
    assert missing_cited("```\npython dsweep/analize.py --verify results/s10-dsweep-run-*\n```\n") == ["dsweep/analize.py"]
    assert missing_cited("```\npython dsweep/analyze.py --verify results/s10-dsweep-run-*\n```\n") == []
    assert missing_cited("`python harness/pool.py <out.json> <run folders>`") == []


def test_cited_paths_sees_workflow_names_and_patterns():
    assert missing_cited("```\ngh workflow run measure.yml -R <you>/third-of-a-percent\n```\n") == []
    assert missing_cited("```\ngh workflow run measur.yml -R <you>/third-of-a-percent\n```\n") == ["gh workflow run measur.yml"]
    assert missing_cited("`results/s10-dsweep-run-*`") == []
    assert missing_cited("`results/s99-dsweep-run-*`") == ["results/s99-dsweep-run-*"]


def test_cited_paths_resolves_bare_names_in_a_tool_folder():
    """tools/lostloops/README.md names its own files by a bare name; they are looked up in its folder, and an output file name is not a path."""
    doc = "tools/lostloops/README.md"
    assert missing_cited("(`lostloops.py`, `ll_optrecord.py`, `ll_classify.py` and `evidence/` stay together); it writes `report.md`", doc) == []
    assert missing_cited("`tests/fake_clang.py` and `corpus/projects.json` and `mitigate/README.md`", doc) == [], "both styles of path resolve for this document"
    assert missing_cited("`tests/fake_claang.py`", doc) == ["tests/fake_claang.py"]
    assert missing_cited("`tests/fake_clang.py`", "README.md") == ["tests/fake_clang.py"], "the folder-relative style is for the listed documents only"
    assert missing_cited("```\n# the pin is in corpus/projects.json).\n```\n", doc) == []
    assert missing_cited("(`lostloop.py` and `evidence/`)", doc) == ["lostloop.py"]
    assert missing_cited("(`lostloops.py` and `evidance/`)", doc) == ["evidance/"]
    assert missing_cited("`lostloops.py`", "README.md") == [], "a bare name is resolved only in the documents listed in FOLDER_RELATIVE"


def test_cited_paths_sees_a_script_named_for_a_folder():
    assert missing_cited("(`python check.py` in `investigate/vectorizer/matmul/`)") == []
    assert missing_cited("(`python chek.py` in `investigate/vectorizer/matmul/`)") == ["investigate/vectorizer/matmul/chek.py"]


# A path a document names only to say that the file was never created (the sentence has to keep saying so, in these words).
NOT_CREATED = {("gaps/GAPS.md", "harness/criteria-v4-confirm.json"): "no separate v4 file was created"}


def missing_in_doc(doc):
    """The paths a document names that do not exist, apart from the ones it names to say they were not created."""
    missing = sorted({shown for shown, rel in cited_paths(doc) if not cited_exists(doc, rel)})
    with open(os.path.join(REPO, doc), encoding="utf-8") as f:
        text = squash(f.read())
    for (d, path), phrase in NOT_CREATED.items():
        if d == doc and path in missing:
            assert phrase in text, f"{doc} names {path} but no longer says '{phrase}'"
            missing.remove(path)
    return missing


def test_the_not_created_files_are_not_there():
    """If a file the documents say was never created appears, the sentence that says so has to change."""
    for (d, path), phrase in NOT_CREATED.items():
        assert not os.path.exists(os.path.join(REPO, path)), f"{path} exists now; {d} says: {phrase}"


if pytest is not None:
    @pytest.mark.parametrize("doc", citing_present())
    def test_cited_paths_exist(doc):
        missing = missing_in_doc(doc)
        assert not missing, f"{doc} names paths that do not exist in the repository: {missing}"
else:
    def test_cited_paths_exist_all():
        missing = {doc: missing_in_doc(doc) for doc in citing_present()}
        assert not any(missing.values()), f"documents name paths that do not exist: { {d: m for d, m in missing.items() if m} }"


def test_the_lostloops_pointers_cite_the_tool_and_its_example_workflow():
    """README.md and the details point at tools/lostloops/ and its example workflow; the guard above sees both paths, so a renamed file fails it."""
    for doc, getter in (("README.md", readme_text), ("readme-parts/DETAILS.md", details_text)):
        cited = {rel for _, rel in cited_paths_in(getter(), doc)}
        assert "tools/lostloops/" in cited and "tools/lostloops/example-workflow.yml" in cited, f"{doc} no longer names the tool and its example workflow"
    assert missing_cited("`tools/lostloops/example-workflow.yml`") == []
    assert missing_cited("`tools/lostloops/example-workflow.ymll`") == ["tools/lostloops/example-workflow.ymll"]
    assert missing_cited("`tools/lostloop/`") == ["tools/lostloop/"]


def test_the_repository_files_the_page_links_to_exist():
    """site/app.js maps the data-href keys of the page to repository files (repoPath); every literal path in the map must exist, and the two
    keys of the lostloops pointer must map to the tool's README and its example workflow, which site/index.html must use."""
    with open(os.path.join(REPO, "site", "app.js"), encoding="utf-8") as f:
        js = f.read()
    m = re.search(r"const repoPath = \{(.*?)\};", js, re.S)
    assert m, "site/app.js has no repoPath map"
    literal = dict(re.findall(r"(\w+): '([^']+)'", m.group(1)))
    assert literal, "no literal paths found in repoPath"
    missing = sorted(p for p in literal.values() if not os.path.exists(os.path.join(REPO, p)))
    assert not missing, f"site/app.js links to repository files that do not exist: {missing}"
    assert literal.get("lostloopsUrl") == "tools/lostloops/README.md" and literal.get("llWorkflowUrl") == "tools/lostloops/example-workflow.yml"
    with open(os.path.join(REPO, "site", "index.html"), encoding="utf-8") as f:
        page = f.read()
    for key in ("lostloopsUrl", "llWorkflowUrl"):
        assert f'data-href="{key}"' in page, f"site/index.html does not use {key}"


# ---- statements about the order of events: each names the unpublished history or links to the account of it ---------------------

# Something committed, written, fixed, registered, listed, set or planned before something else (or beforehand), "in advance", or pre-registered.
# The file name PREREGISTRATION.md is a name and not a claim. The page has the same scan in scripts/check_site.py (ORDER_CLAIMS_JS).
# A full stop inside a file name or a number (PLAN2.md, 1.02) does not end the stretch between the verb and "before": "committed in PLAN2.md before
# the first compile" is a claim. A full stop followed by a space does.
ORDER_CLAIM = re.compile(r"\b(?:committed|written|fixed|registered|listed|set|planned)\b(?:[^.]|\.(?=\w)){0,40}\bbefore(?:hand)?\b|\bin advance\b|pre-?regist(?!ration\.md)", re.I)
ORDER_QUALIFIER = re.compile(r"the author(?:'|’)s unpublished development history|#prov-full", re.I)
ORDER_DOCS = {"README.md": readme_text, "readme-parts/DETAILS.md": details_text}
# The folder documents are scanned too: every Markdown file under these folders (not under a results/ folder, which holds the records) and
# the exported day-one results note. What is left out is the plans: PLAN.md, PLAN2.md and the like are the records themselves, may not be edited
# (the result files store the hash of several of them) and say in their own words when they were written; the folder documents, README.md and
# the details page are where the order is attributed. The list is built from the tree, so a new document is scanned without being added here,
# and the export (which drops a few private notes and cuts gaps/GAPS.md after its first section) is scanned the same way.
ORDER_FOLDERS = ("arm64", "ce-sweep", "corpus", "dsweep", "environment", "forwardt", "gaps", "investigate", "layout-sweep", "mitigate", "pgo", "realworld",
                 "replication", "robustness", "siblings", "tools", "variants", "versions")
ORDER_EXTRA_DOCS = ("docs/dayone-results.md",)
ORDER_RECORD_NAME = re.compile(r"^PLAN[\w.\-]*\.md$")
ORDER_SKIP_DIRS = ("results", ".git", "node_modules", "__pycache__")


def order_folder_docs():
    """(scanned, left out): the folder documents under ORDER_FOLDERS that are scanned, and the plan files that are left out, as repository paths."""
    scanned, left_out = [], []
    for folder in ORDER_FOLDERS:
        for base, dirs, names in os.walk(os.path.join(REPO, folder)):
            dirs[:] = [d for d in dirs if d not in ORDER_SKIP_DIRS]
            for n in names:
                if n.lower().endswith(".md"):
                    rel = os.path.relpath(os.path.join(base, n), REPO).replace(os.sep, "/")
                    (left_out if ORDER_RECORD_NAME.match(n) else scanned).append(rel)
    scanned += [d for d in ORDER_EXTRA_DOCS if os.path.exists(os.path.join(REPO, d))]
    return sorted(scanned), sorted(left_out)


ORDER_FOLDER_DOCS, ORDER_PLAN_FILES = order_folder_docs()


def order_doc_text(doc):
    """The text of a scanned document: README.md and the details page through the readers that honour README_PATH and DETAILS_PATH, the others from the tree."""
    if doc in ORDER_DOCS:
        return ORDER_DOCS[doc]()
    with open(os.path.join(REPO, *doc.split("/")), encoding="utf-8") as f:
        return f.read()


# A unit that states an order without the qualifier and is allowed to: (document, words of the unit) -> why. Each entry must still be needed.
ORDER_CLAIM_EXCEPTIONS = {
    ("forwardt/README.md", "was committed on its own, before the code and before any run"):
        "the same sentence says what the order rests on (the author's clock, and the public history in which the plan is the only file of its commit), "
        "so the reader is told what can and cannot be checked; the plan itself lists the part that cannot",
    ("readme-parts/DETAILS.md", "so this later data is not a pre-registered test either"):
        "a negation: it says the later runs were not planned before the data was known, so it states no order that needs a source",
    ("investigate/vectorizer/reverse-stride2/README.md", "is set once, before the label"):
        "assembly: a register is set once before a loop label; no order of events in the project is stated",
    ("gaps/GAPS.md", "must be written as a pre-registered rule file before any run"):
        "a requirement in the table of proposed steps, written before the step was taken; it states what the step needs, not that an order happened",
    ("gaps/GAPS.md", "Pre-registration practice; NIST's fixed design"):
        "names a research practice as the source of a gap; it is a title, not an order of events in this project",
    ("gaps/GAPS.md", "say so in advance"):
        "an instruction for a later report, in the table of proposed steps; it states no order that happened",
    ("gaps/GAPS.md", "written before the run; training on the test input flatters PGO"):
        "an item of the next steps 'as planned when this file was written': the expectation was still to be written when the note was made",
    ("gaps/GAPS.md", "the rule registered before the run."):
        "an item of the next steps 'as planned when this file was written': the rule was still to be registered when the note was made",
}
# Entries whose text is in a section that the exported copy of gaps/GAPS.md does not have (it keeps the related-work section only): in that copy
# the unit is absent and the entry is not needed there; in a tree that has the section the entry must still be needed.
ORDER_EXCEPTIONS_NOT_EXPORTED = {
    ("gaps/GAPS.md", "must be written as a pre-registered rule file before any run"),
    ("gaps/GAPS.md", "Pre-registration practice; NIST's fixed design"),
    ("gaps/GAPS.md", "say so in advance"),
    ("gaps/GAPS.md", "written before the run; training on the test input flatters PGO"),
    ("gaps/GAPS.md", "the rule registered before the run."),
}


def order_units(text):
    """The paragraphs, list items (each bullet and sub-bullet), table rows and headings of a Markdown text, one string each."""
    cur, out = [], []
    for line in text.replace("\r\n", "\n").split("\n"):
        if not line.strip():
            if cur:
                out.append("\n".join(cur))
            cur = []
        elif re.match(r"\s*(?:[-*]|\d+\.)\s", line) or line.startswith(("|", "#")):
            if cur:
                out.append("\n".join(cur))
            cur = [line]
        else:
            cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return [squash(u) for u in out]


def bare_order_claims(doc, text):
    """The units of a text that state an order and name neither the author's unpublished development history nor the account of it (#prov-full)."""
    found = []
    for unit in order_units(text):
        m = ORDER_CLAIM.search(unit)
        if m and not ORDER_QUALIFIER.search(unit):
            if any(d == doc and snippet in unit for (d, snippet) in ORDER_CLAIM_EXCEPTIONS):
                continue
            found.append(unit[max(0, m.start() - 60):m.end() + 60])
    return found


if pytest is not None:
    @pytest.mark.parametrize("doc", sorted(ORDER_DOCS) + ORDER_FOLDER_DOCS)
    def test_order_statements_name_the_unpublished_history(doc):
        bare = bare_order_claims(doc, order_doc_text(doc))
        assert not bare, (f"{doc} states that something was committed, written, fixed, registered, listed, set or planned before something else, "
                          f"in advance or pre-registered, without naming the author's unpublished development history in the same paragraph or bullet "
                          f"(the order cannot be checked from this repository's records); name it, link #prov-full, say what the records show, or list the unit "
                          f"in ORDER_CLAIM_EXCEPTIONS with a reason: {bare}")
else:
    def test_order_statements_name_the_unpublished_history():
        bare = {doc: bare_order_claims(doc, order_doc_text(doc)) for doc in sorted(ORDER_DOCS) + ORDER_FOLDER_DOCS}
        assert not any(bare.values()), f"order statements without the unpublished history named: {bare}"


def test_the_order_scan_reaches_the_folder_documents_and_leaves_out_only_the_plans():
    """The folder documents that state results are in the scan (the list is read from the tree, so this fails if a walk or a skip rule drops them),
    and the only files left out are the plans, whose names start with PLAN."""
    must_scan = {"arm64/README.md", "ce-sweep/README.md", "corpus/README.md", "docs/dayone-results.md", "dsweep/README.md", "forwardt/README.md", "gaps/GAPS.md",
                 "investigate/FINDINGS.md", "mitigate/README.md", "pgo/report.md", "realworld/README.md", "replication/README.md",
                 "robustness/report.md", "siblings/README.md", "tools/lostloops/README.md", "variants/RESULTS.md",
                 "investigate/vectorizer/reverse-stride2/README.md"}
    assert must_scan <= set(ORDER_FOLDER_DOCS), f"the order scan lost: {sorted(must_scan - set(ORDER_FOLDER_DOCS))}"
    assert ORDER_PLAN_FILES and all(ORDER_RECORD_NAME.match(os.path.basename(p)) for p in ORDER_PLAN_FILES), f"the left-out files are not all plans: {ORDER_PLAN_FILES}"
    assert not [p for p in ORDER_FOLDER_DOCS if ORDER_RECORD_NAME.match(os.path.basename(p))], "a plan is in the scan"
    assert not any(p.split("/")[0] in ("results", "learn", "site") or "results" in p.split("/")[:-1] for p in ORDER_FOLDER_DOCS), "the records are in the scan"
    for name in ("PLAN.md", "PLAN2.md", "PLAN-arm.md"):
        assert ORDER_RECORD_NAME.match(name), f"{name} is a plan"
    for name in ("README.md", "MATMUL-EXPLAINED.md", "report.md", "RESULTS.md", "MYPLAN.md", "PLAN.txt"):
        assert not ORDER_RECORD_NAME.match(name), f"{name} is not a plan file"


def test_the_order_scan_sees_the_claim_class_and_the_exceptions_are_still_needed():
    """The scan flags each wording of the class, accepts the qualifier or the link to the account, and does not read a file name as a claim;
    each listed exception still sits in a unit that needs it."""
    q = "in the author's unpublished development history"
    for claim in ("the plan was committed before the first run", "rules written before the runs", "fixed in advance", "registered in advance", "set beforehand",
                  "listed in its plan before the first compile", "it is pre-registered", "the plan was planned before it", "a preregistration"):
        assert bare_order_claims("README.md", f"- The test: {claim}.\n"), f"not flagged: {claim}"
        assert not bare_order_claims("README.md", f"- The test: {claim}, {q}.\n"), f"qualifier not accepted: {claim}"
        assert not bare_order_claims("README.md", f"- The test: {claim} ([account](details.html#prov-full)).\n"), f"link not accepted: {claim}"
        assert bare_order_claims("README.md", f"- The test: {claim}.\n- Another bullet {q}.\n"), f"a qualifier in the next bullet counts: {claim}"
    assert not bare_order_claims("README.md", "plan: results/s5-holdout/PREREGISTRATION.md\n"), "a file name is read as a claim"
    # a full stop inside a file name does not end the stretch between the verb and "before"; one followed by a space does
    assert bare_order_claims("corpus/README.md", "- Its list was committed in [PLAN2.md](PLAN2.md) before the first compile.\n"), "a dotted file name hides the claim"
    assert bare_order_claims("corpus/README.md", "- The threshold 1.02 was fixed in v1.0 before the runs.\n"), "a dotted number hides the claim"
    assert not bare_order_claims("corpus/README.md", "- The list was committed. Before the first compile nothing ran.\n"), "a sentence end is crossed"
    for (doc, snippet), why in ORDER_CLAIM_EXCEPTIONS.items():
        assert why.strip() and len(why) > 20, f"the exception {snippet!r} has no reason"
        assert doc in ORDER_DOCS or doc in ORDER_FOLDER_DOCS, f"the exception {snippet!r} names a document that is not scanned: {doc}"
        units = [u for u in order_units(order_doc_text(doc)) if snippet in u]
        if not units and (doc, snippet) in ORDER_EXCEPTIONS_NOT_EXPORTED:
            assert doc == "gaps/GAPS.md" and "## 1. Gaps" not in order_doc_text(doc), f"the exception {snippet!r} is missing from a tree that has the section it belongs to"
            continue
        assert units and all(ORDER_CLAIM.search(u) and not ORDER_QUALIFIER.search(u) for u in units), f"the exception {snippet!r} ({why}) is not needed any more: remove it"
    assert ORDER_EXCEPTIONS_NOT_EXPORTED <= set(ORDER_CLAIM_EXCEPTIONS), "a not-exported entry is not an exception"


# Folder documents whose real text is used to show that the scan bites: the qualifier is taken out of every order statement that carries it, and
# the statements must then be flagged. gaps/GAPS.md is among them in a tree that has its notes (the exported copy has none that state an order).
ORDER_TAMPER_DOCS = ("arm64/README.md", "corpus/README.md", "gaps/GAPS.md", "mitigate/README.md", "dsweep/README.md", "realworld/README.md",
                     "docs/dayone-results.md", "robustness/report.md", "pgo/report.md")


def without_the_qualifier(text):
    """The text with the unpublished history left out of each unit (units are rejoined with blank lines, so each stays its own unit)."""
    return "\n\n".join(ORDER_QUALIFIER.sub("", unit) for unit in order_units(text))


def test_taking_the_qualifier_out_of_a_folder_document_is_caught():
    """Each folder document that qualifies an order statement is flagged once the qualifier is taken out, and is clean as it stands."""
    bitten = []
    for doc in ORDER_TAMPER_DOCS:
        if doc not in ORDER_FOLDER_DOCS:
            continue
        text = order_doc_text(doc)
        qualified = [u for u in order_units(text) if ORDER_CLAIM.search(u) and ORDER_QUALIFIER.search(u)]
        if not qualified:
            continue
        assert not bare_order_claims(doc, text), f"{doc} is not clean as it stands: {bare_order_claims(doc, text)}"
        flagged = bare_order_claims(doc, without_the_qualifier(text))
        assert len(flagged) >= len(qualified), f"{doc}: {len(qualified)} qualified order statements, only {len(flagged)} flagged without the qualifier"
        bitten.append(doc)
    assert len(bitten) >= 3, f"the tamper reached only {bitten}"
    if "gaps/GAPS.md" in ORDER_FOLDER_DOCS and "## 1. Gaps" in order_doc_text("gaps/GAPS.md"):
        assert "gaps/GAPS.md" in bitten, "gaps/GAPS.md has no qualified order statement to take out"


def test_an_order_statement_added_to_a_folder_document_is_caught():
    """'registered in advance' (and the other wordings of the class) appended to a real folder document is flagged, and only the added unit is."""
    for doc in ("mitigate/README.md", "arm64/README.md", "gaps/GAPS.md", "robustness/report.md"):
        if doc not in ORDER_FOLDER_DOCS:
            continue
        text = order_doc_text(doc)
        assert not bare_order_claims(doc, text), f"{doc} is not clean as it stands"
        for added in ("A later rule was registered in advance.", "The list was committed before the first compile.", "It is pre-registered."):
            flagged = bare_order_claims(doc, text.rstrip("\n") + "\n\n- " + added + "\n")
            assert len(flagged) == 1 and added.rstrip(".") in flagged[0], f"{doc}: {added!r} gave {flagged}"


PRE_PLANNED = re.compile(r"pre[-\s]?planned", re.I)


def pre_planned_files():
    """Every text file under site/, README.md, readme-parts/ and every README*.md or RESULTS.md of a folder (the top-level results/ is left out: those files are the records)."""
    found = []
    for base, dirs, names in os.walk(REPO):
        rel_base = os.path.relpath(base, REPO)
        dirs[:] = [d for d in dirs if d not in (".git", ".claude", "learn", "node_modules", "__pycache__") and not (rel_base == "." and d == "results")]
        for n in names:
            rel = os.path.normpath(os.path.join(rel_base, n))
            in_site = rel.startswith("site" + os.sep) and n.lower().endswith((".html", ".js", ".css", ".json", ".md", ".svg", ".txt"))
            doc = n.lower().startswith("readme") and n.lower().endswith(".md") or n == "RESULTS.md" or rel.startswith("readme-parts" + os.sep)
            if in_site or doc:
                found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def test_no_document_or_page_text_calls_a_plan_pre_planned():
    """The holdout's plan was committed 2 s after its first job started (see the details page), so no text under site/ and no README may call the run
    pre-planned; the glossary says 'a fresh run, planned in writing'."""
    files = pre_planned_files()
    assert "site/index.html" in files and "README.md" in files and "readme-parts/DETAILS.md" in files and "arm64/README.md" in files, f"the scan lost files: {files[:8]}"
    hits = []
    for rel in files:
        with open(os.path.join(REPO, rel), encoding="utf-8", errors="replace") as f:
            hits += [f"{rel}: {m.group(0)}" for m in PRE_PLANNED.finditer(f.read())]
    assert not hits, f"'pre-planned' appears: {hits[:5]}"
    for text in ("a pre-planned run", "Pre-Planned", "a preplanned run", "a pre planned run"):
        assert PRE_PLANNED.search(text), f"the pattern misses {text!r}"
    assert not PRE_PLANNED.search("planned in writing"), "the pattern reads the glossary's own wording as a hit"


def test_every_arm_record_stores_the_hash_of_the_rule_file():
    """readme-parts/DETAILS.md says of the Arm runs: every record stores the sha256 of harness/criteria-v3.json as it is now, so no threshold was changed after them."""
    with open(os.path.join(REPO, "harness", "criteria-v3.json"), "rb") as f:
        digest = hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    files = sorted(glob.glob(os.path.join(REPO, "results", "s8-arm-run-*", "results-*", "results.json")))
    assert len(files) == 30, f"{len(files)} Arm records"
    wrong = []
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            d = json.load(f)
        got = (d.get("run") or {}).get("criteria_sha256") or d.get("criteria_sha256")
        if got != digest:
            wrong.append(os.path.relpath(fp, REPO))
    assert not wrong, f"records that do not store the hash of harness/criteria-v3.json as it is now: {wrong[:3]}"
