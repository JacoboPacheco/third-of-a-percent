"""The measured and counted numbers typed into README.md, readme-parts/DETAILS.md and the Arm column's text must match the stored data.

Each row of ROWS (README.md), DETAILS_ROWS (readme-parts/DETAILS.md), SIBLINGS_ROWS (siblings/README.md), CESWEEP_ROWS
(ce-sweep/README.md) and ARM64_ROWS (arm64/README.md) ties one sentence to its source:

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
README_PATH, DETAILS_PATH, SIBLINGS_PATH, CESWEEP_PATH and ARM64_PATH point the test at other copies (the proof that the
guard bites uses a tampered copy).

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
test_cited_paths_exist checks that every repository path named in backticks, and every relative Markdown link, in
README.md, readme-parts/DETAILS.md, siblings/README.md, variants/RESULTS.md, arm64/README.md and ce-sweep/README.md exists.
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


def exp_intel_sentence():
    index = J("site/data/index.json")
    intel = index["intel_forward"]
    rows = intel["jobs"]
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
    return {"jobs": str(len(rows)), "n": word(len(intel["cpus"])),
            "pool": str(len(in_pool)), "pooljobs": str(pooled_jobs()),
            "lo": f2(intel["aligned"]["min"]), "hi": f2(intel["aligned"]["max"]),
            "alo": f2(min(amd)), "ahi": f2(max(amd)),
            "j1": str(jobs["Xeon 8573C"]), "j2": str(jobs["Xeon 6973P-C"]), "j2s6": str(b6["jobs"]), "ord": ORDINALS[b["jobs"]],
            "lim": str(int(limit)), "x8573": f2(by["Xeon 8573C"]), "x6973": f2(by["Xeon 6973P-C"]),
            "end6": f3(stencil6["ci95"][1]), "end7": f3(stencil["ci95"][1]), "j3": str(few[0]["jobs"])}


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
    return {"n": str(pooled_jobs()), "o": str(sum(c["jobs"] for c in original["cpus"])),
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


def exp_arm_seed_pool_check():
    path = os.path.join(REPO, "harness", "pool_check.py")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    cells = re.search(r"^SAMPLE_CELLS = \((.*?)\)", src, re.M | re.S)
    width, ratio = re.search(r"^BOUND_TOL_WIDTH = ([\d.]+)", src, re.M), re.search(r"^BOUND_TOL_RATIO = ([\d.]+)", src, re.M)
    assert cells and width and ratio, "harness/pool_check.py no longer defines SAMPLE_CELLS, BOUND_TOL_WIDTH and BOUND_TOL_RATIO in the form this test reads"
    assert "k02_add_fwd.L2" not in cells.group(1), "harness/pool_check.py now samples the cell that decides the Arm verdict"
    x = arm_cell("k02_add_fwd.L2")["aligned"]
    tol = float(width.group(1)) * (x["ci95"][1] - x["ci95"][0]) + float(ratio.group(1)) * x["ratio"]
    margin = x["ci95"][1] - arm_forward_limit()
    assert tol > margin > 0, "the check's tolerance is no longer larger than the margin"
    return {"tol": f3(tol), "over": f4(margin)}


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
    ("claim: Google's average in the one-line pitch", "site/data/index.json claim.google_pct",
     exp_google_pct, r"Google's (?P<v>[\d.]+)% average"),
    ("claim: Google's average in sentence 1", "site/data/index.json claim.google_pct",
     exp_google_pct, r"cost its services (?P<v>[\d.]+)% on average"),
    ("caption: reverse loop as long in the image alt text", "results/s7-pooled/pooled.json EPYC 7763 k04_rev.L1 aligned",
     exp_hero_reverse, r"the reverse loop with the check on drawn as (?P<v>[\d.]+) times as long"),
    ("caption: reverse loop as long under the image", "results/s7-pooled/pooled.json EPYC 7763 k04_rev.L1 aligned",
     exp_hero_reverse, r"The reverse loop takes (?P<v>[\d.]+)x as long as with the check off"),
    ("sentence 2: repetitions per side", "harness/criteria*.json reps_per_side",
     exp_reps, r"timed each pair (?P<lo>\d+) to (?P<hi>\d+) times per side"),
    ("sentence 3: lost-loop range", "site/data/index.json page.lost",
     exp_lost_range, r"took (?P<lo>[\d.]+) to (?P<hi>[\d.]+) times as long in cache"),
    ("sentence 3: forward range, AVX2 exception, as-compiled forward add",
     "site/data/index.json page.forward and cpus; site/data/siblings.json clang18v3-fast",
     exp_forward_sentence,
     r"\((?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x aligned, one AVX2 exception, (?P<avx>[\d.]+)x\); "
     r"below 1x the checked loop ran faster \(cause inferred: loop layout\)\. "
     r"As compiled, the forward add cost about (?P<x>[\d.]+)x on (?P<n>\w+) of the (?P<of>\w+) AMD models"),
    ("sentence 3: Intel forward add", "site/data/index.json intel_forward and cpus; results/s7-pooled/pooled.json Xeon k02_add_fwd.L1 and k03_stencil.L2 aligned",
     exp_intel_sentence,
     r"Intel: in all (?P<jobs>\d+) Intel jobs seen \((?P<n>\w+) models; (?P<pool>\d+) are in the (?P<pooljobs>\d+)-job pool\) "
     r"the forward add at L1 cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x aligned, "
     r"against (?P<alo>[\d.]+)x to (?P<ahi>[\d.]+)x on the AMD models\. "
     r"The Xeon 8573C \((?P<j1>\d+) jobs\) has no verdict \(INCONCLUSIVE under the written rules\): "
     r"its forward add costs a measured (?P<x8573>[\d.]+)x, over the (?P<lim>\d+)% forward limit\. "
     r"The Xeon 6973P-C \((?P<j2>\d+) jobs\) has a verdict \(MAP\) that is borderline: with (?P<j2s6>\d+) jobs it was INCONCLUSIVE, "
     r"its stencil at L2 ending at (?P<end6>[\d.]+), over the same limit, and the (?P<ord>\w+) job moved that end to (?P<end7>[\d.]+); "
     r"its forward add of (?P<x6973>[\d.]+)x is left out as placement-sensitive\. "
     r"A third model, the Xeon 8370C, drew (?P<j3>\d+) job, too few to judge\."),
    ("found: lost-loop range, models, siblings, no-vectorize controls",
     "site/data/index.json page.lost and cpus; site/data/siblings.json; results/s7-pooled/pooled.json EPYC 7763 positive and cells",
     exp_lost_bullet,
     r"\*\*(?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x slower\*\* in cache for loops that lose SIMD .*?"
     r"on all (?P<n>\w+) CPU models with a verdict \(three AMD, and the Xeon 6973P-C, borderline\); the Xeon 8573C \(no verdict\) lost the same loops, "
     r"and the two Xeon models \((?P<ij>\d+) jobs each\) range (?P<ilo>[\d.]+)x to (?P<ihi>[\d.]+)x\. .*?reached about (?P<sib>[\d.]+)x at L1\. .*?"
     r"takes (?P<rev_novec>[\d.]+)x as long for reverse \((?P<rev_on>[\d.]+)x with the checks on, as compiled\), "
     r"(?P<s2_novec>[\d.]+)x for stride-2 \((?P<s2_on>[\d.]+)x\) and (?P<mm_novec>[\d.]+)x for matrix multiply \((?P<mm_on>[\d.]+)x\)"),
    ("found: loop census counts", "site/data/corpus.json census1, census2, categories",
     exp_census_bullet,
     r"\*\*(?P<lost1>\d+) of (?P<vec1>[\d,]+)\*\* vectorized loops in (?P<libs>\d+) general libraries lose SIMD, "
     r"against (?P<lost2>\d+) of (?P<vec2>[\d,]+) in (?P<projs>\d+) numeric projects\. Counted, not timed\. "
     r"Of the (?P<vec1b>[\d,]+), (?P<libcxx>\d+) are inside libc\+\+'s own headers and none of those was lost; "
     r"counting project code only, it is (?P<p1lost>\d+) of (?P<p1>\d+) against (?P<p2lost>\d+) of (?P<p2>[\d,]+)\. "
     r"In the numeric set (?P<with>\d+) of (?P<of>\d+) projects have any lost loop, and LightGBM holds (?P<lgbm>\d+) of the (?P<of444>\d+)\."),
    ("found: real programs timed whole", "site/data/realworld.json rows and timing.groups",
     exp_realworld_bullet,
     r"\((?P<six>\w+) workloads from (?P<four>\w+) projects picked for their lost loops: LightGBM with (?P<lgbm>\w+) option sets.*?"
     r"detectably slower for (?P<n7>\w+) of the \w+ on EPYC 7763 \((?P<lo>[\d.]+)% to (?P<hi>[\d.]+)%, (?P<j7>\d+) jobs; "
     r"(?P<p>\w+) of the \w+ projects\), (?P<n74>\w+) on EPYC 9V74 \((?P<j74>\d+) jobs\), "
     r"(?P<n45>\w+) on EPYC 9V45 \((?P<j45>\d+) jobs\); the rest were not detectable\. "
     r"(?P<ctl>\w+) control programs"),
    ("found: code placement", "site/data/layout.json; site/data/index.json cpus forward_compiled_max_cell",
     exp_placement_bullet,
     r"Across (?P<n>\d+) placements the reverse loop stays at (?P<rlo>[\d.]+)x to (?P<rhi>[\d.]+)x and the forward sum near 1x; "
     r"the forward add swings (?P<alo>[\d.]+)x to (?P<ahi>[\d.]+)x on (?P<models>\w+) models "
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
     "results/s7-pooled and s6-pooled and s4-pooled job counts and reproduction; robustness/results.json s7 forms; harness/pool.py with each Xeon 6973P-C job left out; site/data/holdout.json rows reproduced",
     exp_independence_holdout,
     r"On the (?P<n>\d+)-job pool a block bootstrap and the other interval methods tried \(exploratory, \[report\]\(robustness/report\.md\)\) "
     r"change (?P<same>no verdict form) on EPYC 7763, 9V74, 9V45 or the Xeon 8573C; the Xeon 6973P-C stays MAP under (?P<k>\w+) of the (?P<m>\w+), "
     r"and changes with the set of jobs more than with the method \(leaving one job out, in turn, gives INCONCLUSIVE in (?P<inc>\d+) of its (?P<tot>\d+) cases\)\. "
     r"A fresh, pre-planned run matched the original (?P<o>\d+)-job pool on (?P<yes>EPYC 7763 and 9V74), not (?P<no>9V45)\. "
     r"Intervals still understate run-to-run spread: on EPYC 7763 a run's point fell outside another run's interval in (?P<out>\d+) of (?P<chk>\d+) comparisons "
     r"\((?P<pct>\d+)%; (?P<pct6>\d+)% in the (?P<n6>\d+)-job pool\)\."),
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
     r"forward loops cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x at L1 \(the add and the stencil are placement-sensitive and not judged\), "
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
    return {"one": str(len(three)), "n": str(len(c["per_run"])), "m": f4(over)}


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
    return {"j6": str(c6["jobs"]), "r": f3(x["ratio"]), "lo": f3(x["ci95"][0]), "hi": f3(x["ci95"][1]), "lim": f2(limit)}


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
    return {"p": f3(cell_of(a, "k02_add_fwd.L1")["aligned"]["ratio"]),
            "lim": f2(limit),
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
    rows = intel["jobs"]

    def of(short):
        return [r["aligned"] for r in rows if r["cpu_short"] == short]

    def in_pool(short):
        return [r["aligned"] for r in rows if r["cpu_short"] == short and kernel_pool_source(r["source"])]

    x8370, x8573, x6973 = of("Xeon 8370C"), of("Xeon 8573C"), of("Xeon 6973P-C")
    pooled_8573 = in_pool("Xeon 8573C")
    a = cell_of(cpu_like("8573C"), "k02_add_fwd.L1")["aligned"]
    b = cell_of(cpu_like("6973P-C"), "k02_add_fwd.L1")["aligned"]
    return {"lo": f2(aligned["min"]), "hi": f2(aligned["max"]), "jlo": f3(min(judged)), "jhi": f3(max(judged)),
            "n": str(len(rows)), "m": word(len(intel["cpus"])), "pj": str(sum(len(in_pool(s)) for s in intel["cpus"])),
            "ilo": f2(intel["aligned"]["min"]), "ihi": f2(intel["aligned"]["max"]),
            "a1": f2(min(x8370)), "a2": f2(max(x8370)), "an": str(len(x8370)), "ap": str(len(in_pool("Xeon 8370C"))),
            "b1": f2(min(x8573)), "b2": f2(max(x8573)), "bn": str(len(x8573)), "bp": str(len(pooled_8573)),
            "bp1": f3(min(pooled_8573)), "bp2": f3(max(pooled_8573)),
            "bpool": f3(a["ratio"]), "bl": f3(a["ci95"][0]), "bh": f3(a["ci95"][1]),
            "c1": f2(min(x6973)), "c1b": f2(max(x6973)), "cn": str(len(x6973)), "c2": f3(min(x6973)), "c3": f3(max(x6973)),
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
     r"borderline: counted, one left-out cell would miss the forward limit by (?P<m>[\d.]+) \|"),
    ("details: table, Xeon 8573C verdict", "results/s7-pooled/pooled.json Xeon 8573C k02_add_fwd.L1 aligned", exp_table_8573c,
     r"INCONCLUSIVE: the forward add at L1, aligned (?P<r>[\d.]+) \[(?P<lo>[\d.]+), (?P<hi>[\d.]+)\], misses the 2% forward rule"),
    ("details: table, Xeon 6973P-C verdict", "results/s7-pooled/pooled.json Xeon 6973P-C k03_stencil.L2 aligned", exp_table_6973pc,
     r"MAP, borderline: INCONCLUSIVE with (?P<j6>\d+) jobs; the stencil at L2, aligned (?P<r>[\d.]+) \[(?P<lo>[\d.]+), (?P<hi>[\d.]+)\], "
     r"now ends under the (?P<lim>[\d.]+) limit;"),
    ("details: table, the note on the Intel rows",
     "results/s7-pooled and s6-pooled Xeon cells and per_run; the newest 6973P-C job's results.json; robustness/results.json s7; harness/pool.py with each 6973P-C job left out",
     exp_table_note,
     r"fails the rule \(point (?P<p>[\d.]+), limit (?P<lim>[\d.]+)\)\. For the Xeon 6973P-C the forward add at L1 \(aligned (?P<al>[\d.]+), "
     r"as compiled (?P<ac>[\d.]+)\) is placement-sensitive and left out, and the verdict passes on the stencil at L2, whose interval ends at "
     r"(?P<end>[\d.]+), a margin of (?P<margin>[\d.]+) under the limit\. With the (?P<j6>\d+) jobs of the (?P<n6>\d+)-job pool the same cell ended at "
     r"(?P<end6>[\d.]+) and the model was INCONCLUSIVE\. The (?P<ord>\w+) job came from a noisy machine \(its own A/A control (?P<aa7>[\d.]+)%, "
     r"above the (?P<aamax>\d+)% limit for a single job's own verdict, and a stencil ratio of (?P<s7>[\d.]+), the lowest of the (?P<seven>\w+)\) "
     r"and moved the end under the limit; the pooled rules exclude no job on its own A/A control \(`harness/criteria-v3\.json`\)\. "
     r"Pooling the (?P<seven2>\w+) jobs again with each one left out in turn gives INCONCLUSIVE in (?P<inc>\d+) of the (?P<tot>\d+) cases "
     r"\(MAP only without job (?P<mj>\d+) of run (?P<mr>\d+); `tests/test_readme_numbers\.py` repeats this\), "
     r"and the model is MAP under (?P<k>\d+) of the (?P<m>\d+) interval methods of the robustness analysis "
     r"\(INCONCLUSIVE only under the first form of the lag-1 correction\)\. "
     r"The form depends on which jobs were drawn more than on the interval method, and the verdict is borderline\. "
     r"Neither Xeon model has a run with 3 jobs, so stability is not assessable, and the jobs of each came from (?P<runs>\d+) runs "
     r"\(at most (?P<per>\d+) per run\)\. The Xeon Platinum 8370C drew (?P<j8370>\d+) job \((?P<need>\d+) are needed\): no verdict and no numbers shown\."),
    ("details: forward loops, AMD and Intel", "site/data/index.json page.forward and intel_forward; results/s7-pooled/pooled.json",
     exp_details_forward,
     r"forward loops ran (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x of the unchecked time there; .*?judges ran (?P<jlo>[\d.]+)x to (?P<jhi>[\d.]+)x\. "
     r"The Intel models differ\. In each of (?P<n>\d+) Intel jobs seen \((?P<m>\w+) models, (?P<pj>\d+) of them in the kernel pool\) the forward add at L1, aligned, cost "
     r"(?P<ilo>[\d.]+)x to (?P<ihi>[\d.]+)x: Xeon 8370C (?P<a1>[\d.]+)x to (?P<a2>[\d.]+)x \((?P<an>\d+) jobs, (?P<ap>\d+) in the kernel pool\), "
     r"Xeon 8573C (?P<b1>[\d.]+)x to (?P<b2>[\d.]+)x \((?P<bn>\d+) jobs; the (?P<bp>\d+) pooled ones (?P<bp1>[\d.]+) to (?P<bp2>[\d.]+), "
     r"pooled (?P<bpool>[\d.]+) \[(?P<bl>[\d.]+), (?P<bh>[\d.]+)\]\) and Xeon 6973P-C (?P<c1>[\d.]+)x to (?P<c1b>[\d.]+)x \((?P<cn>\d+) jobs, "
     r"(?P<c2>[\d.]+) to (?P<c3>[\d.]+), pooled (?P<cpool>[\d.]+) \[(?P<cl>[\d.]+), (?P<ch>[\d.]+)\]\)"),
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
     r"The exception is the (?P<twelve>\w+) records in `results/s6-run-\*/` and `results/s7-run-\*/`: they link to runs of this repository"),
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
     r"Forward loops keep their NEON loops and cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x at L1, against a pooled A/A half-width of (?P<aa>[\d.]+)% "
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
     r"The (?P<three>\w+) records in `results/s8-arm-run-\*/` \(the Arm runs\) link to public runs of this repository"),
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
     r"its plan was written before the full results \| `arm64/`, `results/s8-arm-run-\*/` \((?P<runs>\d+) runs\)"),
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
     r"pay (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x in cache, and that forward loops pay little on the AMD models"),
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
     r"\*\*Forward loops keep NEON and cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x at L1\*\* \(as compiled\), against a pooled A/A floor of (?P<aa>[\d.]+)%"),
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
     r"gh workflow run measure\.yml -f runner=(?P<c>ubuntu-[\d.]+-arm)"),
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
    ("arm64: verdict, the independent check", "harness/pool_check.py SAMPLE_CELLS, BOUND_TOL_WIDTH and BOUND_TOL_RATIO; results/s8-arm-pooled/pooled.json cells", exp_arm_seed_pool_check,
     r"its tolerance \(a share of the interval's width, about (?P<tol>[\d.]+) here\) is larger than the margin of (?P<over>[\d.]+), so it could not flag a change of this size"),
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
else:
    def test_readme_numbers_all_rows():
        failures = []
        for rows, text, doc in ((ROWS, readme_text(), "README.md"), (DETAILS_ROWS, details_text(), "readme-parts/DETAILS.md"),
                                (SIBLINGS_ROWS, siblings_text(), "siblings/README.md"), (CESWEEP_ROWS, cesweep_text(), "ce-sweep/README.md"),
                                (ARM64_ROWS, arm64_text(), "arm64/README.md")):
            for row in rows:
                try:
                    check_row(row, text, doc)
                    if row[0] in XFAIL:
                        failures.append(f"{row[0]}: expected to fail ({XFAIL[row[0]]}) but passed")
                except AssertionError as e:
                    if row[0] not in XFAIL:
                        failures.append(str(e))
        assert not failures, "\n".join(failures)


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

CITING = ("README.md", "readme-parts/DETAILS.md", "siblings/README.md", "variants/RESULTS.md", "arm64/README.md", "ce-sweep/README.md")
# Planning documents that are not published. The note appended to DETAILS.md in the public export names them on purpose,
# saying that they do not exist in the repository, so they are not counted as broken citations.
UNPUBLISHED = {"docs/PLAN.md", "docs/SPEC.md", "docs/skeptic.md"}
CITED_ROOTS = ("results/", "dayone/", "investigate/", "tests/", "harness/", "siblings/", "variants/", "ce-sweep/", "layout-sweep/",
               "pgo/", "versions/", "environment/", "robustness/", "mitigate/", "corpus/", "realworld/", "audit/", "kernels/",
               "programs/", "scripts/", "site/", "tools/", "docs/", "gaps/", "claims-audit/", ".github/", "arm64/")


def cited_paths(doc):
    """Repository-relative paths a document names in backticks, and the files its Markdown links point at (relative to the document)."""
    with open(os.path.join(REPO, doc), encoding="utf-8") as f:
        text = f.read()
    out = []
    for span in re.findall(r"`([^`\n]+)`", text):
        span = span.strip().rstrip(".,;:")
        if span.startswith(CITED_ROOTS) and span not in UNPUBLISHED and not re.search(r"[\s*<>{}|$=]", span):
            out.append((span, span))
    for target in re.findall(r"\]\(([^)\s#]+)(?:#[^)\s]*)?\)", text):
        if not re.match(r"[a-z]+:", target):
            out.append((target, os.path.normpath(os.path.join(os.path.dirname(doc), target)).replace("\\", "/")))
    return out


if pytest is not None:
    @pytest.mark.parametrize("doc", CITING)
    def test_cited_paths_exist(doc):
        missing = [shown for shown, rel in cited_paths(doc) if not os.path.exists(os.path.join(REPO, rel))]
        assert not missing, f"{doc} names paths that do not exist in the repository: {sorted(set(missing))}"
else:
    def test_cited_paths_exist_all():
        missing = {doc: sorted({shown for shown, rel in cited_paths(doc) if not os.path.exists(os.path.join(REPO, rel))}) for doc in CITING}
        assert not any(missing.values()), f"documents name paths that do not exist: { {d: m for d, m in missing.items() if m} }"
