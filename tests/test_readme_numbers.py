"""The measured and counted numbers typed into README.md and readme-parts/DETAILS.md must match the stored data.

Each row of ROWS (README.md) and DETAILS_ROWS (readme-parts/DETAILS.md) ties one sentence to its source:

    (label, where the value comes from, a function giving the expected text, a regex anchored on
     the words around the number)

The regex has one named group per typed number. The test finds every sentence that matches the
anchor, reads the typed text out of the groups and compares it with the text computed from the
data, rounded the way the README rounds (ratios to one or two decimals, percentages to one).
A new claim in the README is one more row.

Failures say which sentence, what the README types, what the data gives and where the data is.
Two kinds of failure: the anchor no longer matches (the sentence was reworded: update the row or
the sentence) and the typed number differs from the data (fix the README, or the data is stale).

Read-only and offline: only README.md, readme-parts/DETAILS.md and the stored files are read.
README_PATH and DETAILS_PATH point the test at other copies (the proof that the guard bites uses a
tampered copy).

Under pytest every row is its own test. Without pytest (scripts/check.py's built-in runner) one
plain test goes through all rows.

The sentences about the jobs of the ten later runs that returned nothing rest on tests/data/s6_job_steps.json,
a copy of the Actions step records of those runs (the run pages are public; the file says how it was read).
The sentences about the two newest runs, which returned every job, rest on tests/data/s7_job_steps.json in the same way.
The sentences about the Xeon 6973P-C's verdict with each of its jobs left out in turn are recomputed here with
harness/pool.py (in memory, nothing is written; about 20 seconds).
test_cited_paths_exist checks that every repository path named in backticks, and every relative Markdown link, in
README.md, readme-parts/DETAILS.md, siblings/README.md and variants/RESULTS.md exists.
"""

import glob
import gzip
import json
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
else:
    def test_readme_numbers_all_rows():
        failures = []
        for rows, text, doc in ((ROWS, readme_text(), "README.md"), (DETAILS_ROWS, details_text(), "readme-parts/DETAILS.md"),
                                (SIBLINGS_ROWS, siblings_text(), "siblings/README.md")):
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

CITING = ("README.md", "readme-parts/DETAILS.md", "siblings/README.md", "variants/RESULTS.md")
# Planning documents that are not published. The note appended to DETAILS.md in the public export names them on purpose,
# saying that they do not exist in the repository, so they are not counted as broken citations.
UNPUBLISHED = {"docs/PLAN.md", "docs/SPEC.md", "docs/skeptic.md"}
CITED_ROOTS = ("results/", "dayone/", "investigate/", "tests/", "harness/", "siblings/", "variants/", "ce-sweep/", "layout-sweep/",
               "pgo/", "versions/", "environment/", "robustness/", "mitigate/", "corpus/", "realworld/", "audit/", "kernels/",
               "programs/", "scripts/", "site/", "tools/", "docs/", "gaps/", "claims-audit/", ".github/")


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
