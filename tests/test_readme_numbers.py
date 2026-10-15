"""The measured and counted numbers typed into README.md must match the stored data.

Each row of ROWS ties one sentence of README.md to its source:

    (label, where the value comes from, a function giving the expected text, a regex anchored on
     the words around the number)

The regex has one named group per typed number. The test finds every sentence that matches the
anchor, reads the typed text out of the groups and compares it with the text computed from the
data, rounded the way the README rounds (ratios to one or two decimals, percentages to one).
A new claim in the README is one more row.

Failures say which sentence, what the README types, what the data gives and where the data is.
Two kinds of failure: the anchor no longer matches (the sentence was reworded: update the row or
the sentence) and the typed number differs from the data (fix the README, or the data is stale).

Read-only and offline: only README.md and the stored json files are read. README_PATH points the
test at another copy of the README (the proof that the guard bites uses a tampered copy).

Under pytest every row is its own test. Without pytest (scripts/check.py's built-in runner) one
plain test goes through all rows.
"""

import glob
import json
import os
import re
from functools import lru_cache

try:
    import pytest
except ImportError:  # scripts/check.py falls back to its own runner when pytest is missing
    pytest = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}

EPYC_7763 = "AMD EPYC 7763 64-Core Processor"


# ---- reading the files ---------------------------------------------------------------------

def readme_text():
    path = os.environ.get("README_PATH") or os.path.join(REPO, "README.md")
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


def pooled_cpu(model):
    return next(c for c in J("results/s4-pooled/pooled.json")["cpus"] if c["cpu_model"] == model)


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
    intel = J("site/data/index.json")["intel_forward"]
    def model_number(name):
        return re.search(r"\d{4}\w*", name).group(0)

    two = {model_number(c) for c in intel["cpus"]}
    third = {(v, cpu, jobs) for v, cpu, size, jobs in sibling_values("clang18-fast", "k02_add_fwd", sizes=("L1",))
             if cpu.startswith("Xeon") and model_number(cpu) not in two}
    assert len({cpu for _, cpu, _ in third}) == 1, f"expected one further Intel model in the siblings run, got {sorted(third)}"
    value, _, jobs = sorted(third)[0]
    return {"n": word(len(intel["cpus"])), "lo": f2(intel["aligned"]["min"]), "hi": f2(intel["aligned"]["max"]),
            "third": f1(value), "jobs": word(jobs)}


def exp_lost_bullet():
    ncpu = len([c for c in J("site/data/index.json")["cpus"] if c["form"] == "map"])
    p = J("site/data/index.json")["page"]["lost"]
    every_l1 = [v for row in J("site/data/siblings.json")["rows"] for k in row["cells"]
                for v, _, size, _ in sibling_values(row["variant"], k, sizes=("L1",))]
    cpu = pooled_cpu(EPYC_7763)
    out = {"lo": f1(p["min"]), "hi": f1(p["max"]), "n": word(ncpu), "sib": f1(max(every_l1))}
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
    return {"lo": f1(min(values)), "hi": f1(max(values))}


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
            "e": ".".join(lost_after[0]["version"].split(".")[:2])}


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


def exp_holdout():
    rows = J("site/data/holdout.json")["rows"]
    yes = [r["cpu_short"] for r in rows if r["reproduced"] is True]
    no = [r["cpu_short"] for r in rows if r["reproduced"] is False]  # None: too few jobs to compare
    # the README names the family once: "EPYC 7763 and 9V74, not 9V45"
    return {"yes": " and ".join([yes[0]] + [c.replace("EPYC ", "") for c in yes[1:]]),
            "no": " and ".join(c.replace("EPYC ", "") for c in no)}


def exp_eight_loops():
    return {"n": str(len(J("site/data/index.json")["criteria"]["kernels"]))}


# ---- the table -------------------------------------------------------------------------------
# (label, source of the value, expected-value function, regex with one named group per typed value)

ROWS = [
    ("claim: Google's average in the one-line pitch", "site/data/index.json claim.google_pct",
     exp_google_pct, r"Google's (?P<v>[\d.]+)% average"),
    ("claim: Google's average in sentence 1", "site/data/index.json claim.google_pct",
     exp_google_pct, r"cost its services (?P<v>[\d.]+)% on average"),
    ("caption: reverse loop as long in the image alt text", "results/s4-pooled/pooled.json EPYC 7763 k04_rev.L1 aligned",
     exp_hero_reverse, r"the reverse loop with the check on drawn as (?P<v>[\d.]+) times as long"),
    ("caption: reverse loop as long under the image", "results/s4-pooled/pooled.json EPYC 7763 k04_rev.L1 aligned",
     exp_hero_reverse, r"The reverse loop takes (?P<v>[\d.]+)x as long as with the check off"),
    ("sentence 2: repetitions per side", "harness/criteria*.json reps_per_side",
     exp_reps, r"timed each pair (?P<lo>\d+) to (?P<hi>\d+) times per side"),
    ("sentence 3: lost-loop range", "site/data/index.json page.lost",
     exp_lost_range, r"took (?P<lo>[\d.]+) to (?P<hi>[\d.]+) times as long in cache"),
    ("sentence 3: forward range, AVX2 exception, as-compiled forward add",
     "site/data/index.json page.forward and cpus; site/data/siblings.json clang18v3-fast",
     exp_forward_sentence,
     r"\((?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x aligned, one AVX2 exception, (?P<avx>[\d.]+)x\)\. "
     r"As compiled, the forward add cost about (?P<x>[\d.]+)x on (?P<n>\w+) of the (?P<of>\w+) AMD models"),
    ("sentence 3: Intel forward add", "site/data/index.json intel_forward; site/data/siblings.json clang18-fast Xeon 6973P-C",
     exp_intel_sentence,
     r"On (?P<n>\w+) Intel models the forward add cost about (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x aligned, "
     r"and (?P<third>[\d.]+)x on a third \((?P<jobs>\w+) job\)"),
    ("found: lost-loop range, models, siblings, no-vectorize controls",
     "site/data/index.json page.lost and cpus; site/data/siblings.json; results/s4-pooled/pooled.json EPYC 7763 positive and cells",
     exp_lost_bullet,
     r"\*\*(?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x slower\*\* in cache for loops that lose SIMD .*?"
     r"on all (?P<n>\w+) AMD models with a verdict; .*?reached about (?P<sib>[\d.]+)x at L1\. .*?"
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
     exp_gcc, r"even the forward add loses SIMD and runs (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x slower"),
    ("folders: why the forward add cost", "site/data/index.json page.forward.compiled",
     exp_why_1_6, r"why the forward add cost (?P<v>[\d.]+)x"),
    ("trust: newer clang timed", "site/data/versions.json; results/s4-pooled/pooled.json EPYC 7763 positive",
     exp_versions,
     r"Clang and libc\+\+ (?P<a>\d+) to (?P<b>\d+), timed on the eight loops \((?P<models>\w+) CPU model with enough jobs\).*?"
     r"\((?P<l1>[\d.]+)x at L1 on EPYC 7763, as slow as a build with no vectorization at all, and (?P<l2>[\d.]+)x at L2\)"),
    ("trust: matrix multiply lost per clang version", "site/data/cesweep.json rows (clang, x86-64, -O2, hardening macro in effect)",
     exp_cesweep,
     r"finds it lost on clang (?P<a>\d+) to (?P<b>\d+) at baseline x86-64, kept on (?P<c>\d+) to (?P<d>\d+), "
     r"and lost again on clang (?P<e>[\d.]+) and trunk"),
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
    ("trust: holdout", "site/data/holdout.json rows reproduced",
     exp_holdout, r"A fresh, pre-planned run matched on (?P<yes>EPYC 7763 and 9V74), not (?P<no>9V45)"),
    ("folders: the eight loops", "site/data/index.json criteria.kernels",
     exp_eight_loops, r"`kernels/` the (?P<n>\d+) loops"),
]

# Rows whose typed number is wrong against the data: label -> reason. None at the time of writing.
# Add a row here (the test then needs to keep failing, strict) instead of editing the data to fit.
XFAIL = {}


# ---- the checks --------------------------------------------------------------------------------

def check_row(row, text=None):
    label, source, expected_fn, pattern = row
    text = readme_text() if text is None else text
    matches = list(re.finditer(pattern, text, re.S))
    assert matches, (f"{label}: no sentence of README.md matches the anchor, so the sentence was reworded "
                     f"or removed; update this row (tests/test_readme_numbers.py) or the README.\n  anchor: {pattern}")
    expected = expected_fn()
    for m in matches:
        for name, want in expected.items():
            got = m.group(name) if name in m.re.groupindex else None
            assert got is not None, f"{label}: the row expects a value '{name}' that the anchor does not capture"
            assert got.lower() == want.lower(), (
                f"{label}: README.md types '{got}' for '{name}' but the data gives '{want}' "
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
else:
    def test_readme_numbers_all_rows():
        text = readme_text()
        failures = []
        for row in ROWS:
            try:
                check_row(row, text)
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
    pooled = J("results/s4-pooled/pooled.json")
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
