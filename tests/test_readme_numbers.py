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


def details_text():
    path = os.environ.get("DETAILS_PATH") or os.path.join(REPO, "readme-parts", "DETAILS.md")
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


# The kernel pool the page and the README read: the original 30 jobs plus the 45 of the ten later runs.
# The original pool stays on disk (the holdout is compared against it) and is read only where a sentence
# says "original".
POOLED = "results/s6-pooled/pooled.json"
POOLED_ORIGINAL = "results/s4-pooled/pooled.json"
FORWARD = ("k01_sum_fwd", "k02_add_fwd", "k03_stencil")


def pooled_cpu(model):
    return next(c for c in J(POOLED)["cpus"] if c["cpu_model"] == model)


def cpu_like(key, original=False):
    """The pooled entry of the CPU model whose name contains key ('7763', '9V45', '8573C', ...)."""
    return next(c for c in J(POOLED_ORIGINAL if original else POOLED)["cpus"] if key in c["cpu_model"])


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
    assert len(pooled) == 2 and all(c["form"] == "inconclusive" for c in pooled),         "the README says the two pooled Intel models are INCONCLUSIVE; the data now gives " + str([(c["cpu_short"], c["form"]) for c in pooled])
    jobs = {c["jobs"] for c in pooled}
    assert len(jobs) == 1, f"the README says '6 jobs each'; the two models have {sorted(jobs)}"
    amd = [cell_of(cpu_like(c["cpu_short"].split()[1]), "k02_add_fwd.L1")["aligned"]["ratio"] for c in amd_cpus()]
    by = {c["cpu_short"]: cell_of(cpu_like(c["cpu_short"].split()[1]), "k02_add_fwd.L1")["aligned"]["ratio"] for c in pooled}
    return {"jobs": str(len(rows)), "n": word(len(intel["cpus"])),
            "lo": f2(intel["aligned"]["min"]), "hi": f2(intel["aligned"]["max"]),
            "alo": f2(min(amd)), "ahi": f2(max(amd)),
            "j": str(jobs.pop()), "x8573": f2(by["Xeon 8573C"]), "x6973": f2(by["Xeon 6973P-C"])}


def exp_lost_bullet():
    ncpu = len([c for c in J("site/data/index.json")["cpus"] if c["form"] == "map"])
    p = J("site/data/index.json")["page"]["lost"]
    every_l1 = [v for row in J("site/data/siblings.json")["rows"] for k in row["cells"]
                for v, _, size, _ in sibling_values(row["variant"], k, sizes=("L1",))]
    cpu = pooled_cpu(EPYC_7763)
    out = {"lo": f1(p["min"]), "hi": f1(p["max"]), "n": word(ncpu), "sib": f1(max(every_l1))}
    intel = intel_pooled()
    jobs = {c["jobs"] for c in intel}
    assert len(jobs) == 1, f"the README says '6 jobs each' for the two Intel models; they have {sorted(jobs)}"
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


def exp_independence_holdout():
    rows = J("site/data/holdout.json")["rows"]
    yes = [r["cpu_short"] for r in rows if r["reproduced"] is True]
    no = [r["cpu_short"] for r in rows if r["reproduced"] is False]  # None: too few jobs to compare
    original = J(POOLED_ORIGINAL)
    # the robustness analysis of the 75-job pool: the forms of every CPU model under every interval method
    rb = J("robustness/results.json")["datasets"]["s6"]["cpus"]
    amd = [c for name, c in rb.items() if "EPYC" in name]
    xeon = [c for name, c in rb.items() if "EPYC" not in name]
    same = all(len({m["form"] for m in c["methods"].values()}) == 1 for c in amd) and         all(c["methods"]["a"]["form"] == "map" for c in amd)
    flips = all(c["methods"]["a"]["form"] == "inconclusive" and any(m["form"] == "map" for m in c["methods"].values())
                for c in xeon) and len(xeon) == 2
    # the README names the holdout family once: "EPYC 7763 and 9V74, not 9V45"
    return {"n": str(pooled_jobs()), "o": str(sum(c["jobs"] for c in original["cpus"])),
            "same": "no verdict form" if same else "a verdict form",
            "flips": "become MAP under some of them" if flips else "stay inconclusive",
            "yes": " and ".join([yes[0]] + [c.replace("EPYC ", "") for c in yes[1:]]),
            "no": " and ".join(c.replace("EPYC ", "") for c in no)}


def exp_eight_loops():
    return {"n": str(len(J("site/data/index.json")["criteria"]["kernels"]))}


# ---- the ten later runs, the compile-only studies ------------------------------------------------

def pooled_jobs(original=False):
    return sum(c["jobs"] for c in J(POOLED_ORIGINAL if original else POOLED)["cpus"])


def later_runs():
    """The ten later runs: result folders, returned jobs, the dispatch size and the limit the workflow names."""
    dirs = sorted(glob.glob(os.path.join(REPO, "results", "s6-run-*")))
    returned = sum(len(glob.glob(os.path.join(d, "results-*", "results.json"))) for d in dirs)
    with open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        wf = f.read()
    per_run = len(json.loads(re.search(r'jobs:\s*\n\s*description:[^\n]*\n\s*default: "(\[[^"]*\])"', wf).group(1)))
    note = re.search(r"at (\d+), (\d+) of (\d+) jobs in (\w+) runs", wf)  # the comment on timeout-minutes
    now = re.search(r"measure:\s*\n\s*runs-on:[^\n]*\n(?:\s*#[^\n]*\n)*\s*timeout-minutes: (\d+)", wf)
    assert note and now, "measure.yml no longer says why timeout-minutes was raised"
    assert pooled_jobs() - pooled_jobs(original=True) == returned, \
        f"the 75-job pool has {pooled_jobs()} jobs, the original {pooled_jobs(original=True)}, the later result folders {returned}"
    return {"runs": len(dirs), "returned": returned, "dispatched": len(dirs) * per_run,
            "limit": int(note.group(1)), "now": int(now.group(1))}


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
    xeon = {c["jobs"] for c in intel_pooled()}
    assert len(xeon) == 1, f"the README says '6 each' for the two Xeon models; they have {sorted(xeon)}"
    lr = later_runs()
    return {"jobs": str(pooled_jobs()), "runs": str(len(pooled["runs"])), "lo": str(min(amd)), "hi": str(max(amd)),
            "x": str(xeon.pop()), "new": str(pooled_jobs() - pooled_jobs(original=True)),
            "ten": word(lr["runs"]), "ret": str(lr["returned"]), "disp": str(lr["dispatched"]), "limit": str(lr["limit"])}


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
            "n": str(later_runs()["returned"])}


# ---- the table -------------------------------------------------------------------------------
# (label, source of the value, expected-value function, regex with one named group per typed value)

ROWS = [
    ("claim: Google's average in the one-line pitch", "site/data/index.json claim.google_pct",
     exp_google_pct, r"Google's (?P<v>[\d.]+)% average"),
    ("claim: Google's average in sentence 1", "site/data/index.json claim.google_pct",
     exp_google_pct, r"cost its services (?P<v>[\d.]+)% on average"),
    ("caption: reverse loop as long in the image alt text", "results/s6-pooled/pooled.json EPYC 7763 k04_rev.L1 aligned",
     exp_hero_reverse, r"the reverse loop with the check on drawn as (?P<v>[\d.]+) times as long"),
    ("caption: reverse loop as long under the image", "results/s6-pooled/pooled.json EPYC 7763 k04_rev.L1 aligned",
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
    ("sentence 3: Intel forward add", "site/data/index.json intel_forward and cpus; results/s6-pooled/pooled.json k02_add_fwd.L1 aligned",
     exp_intel_sentence,
     r"In each of (?P<jobs>\d+) Intel jobs of the main runs \((?P<n>\w+) models\) the forward add at L1 cost (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x aligned, "
     r"against (?P<alo>[\d.]+)x to (?P<ahi>[\d.]+)x on the AMD models; the two Intel models pooled over (?P<j>\d+) jobs each "
     r"\(Xeon 8573C (?P<x8573>[\d.]+)x, Xeon 6973P-C (?P<x6973>[\d.]+)x\) are INCONCLUSIVE"),
    ("found: lost-loop range, models, siblings, no-vectorize controls",
     "site/data/index.json page.lost and cpus; site/data/siblings.json; results/s6-pooled/pooled.json EPYC 7763 positive and cells",
     exp_lost_bullet,
     r"\*\*(?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x slower\*\* in cache for loops that lose SIMD .*?"
     r"on all (?P<n>\w+) AMD models with a verdict; the two Intel models \((?P<ij>\d+) jobs each, no verdict\) lost the same loops, "
     r"(?P<ilo>[\d.]+)x to (?P<ihi>[\d.]+)x\. .*?reached about (?P<sib>[\d.]+)x at L1\. .*?"
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
    ("trust: newer clang timed", "site/data/versions.json; results/s6-pooled/pooled.json EPYC 7763 positive",
     exp_versions,
     r"Clang and libc\+\+ (?P<a>\d+) to (?P<b>\d+), timed on the eight loops \((?P<models>\w+) CPU model with enough jobs\).*?"
     r"\((?P<l1>[\d.]+)x at L1 on EPYC 7763, as slow as a build with no vectorization at all, and (?P<l2>[\d.]+)x at L2\)"),
    ("trust: matrix multiply lost per clang version", "site/data/cesweep.json rows (clang, x86-64, -O2, hardening macro in effect)",
     exp_cesweep,
     r"finds matrix multiply lost on clang (?P<a>\d+) to (?P<b>\d+) at baseline x86-64, kept on (?P<c>\d+) to (?P<d>\d+) "
     r"\(.*?\), and lost again on clang (?P<e>[\d.]+) and trunk"),
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
    ("trust: independence and holdout", "results/s6-pooled/pooled.json and results/s4-pooled/pooled.json job counts; robustness/results.json s6 forms; site/data/holdout.json rows reproduced",
     exp_independence_holdout,
     r"On the (?P<n>\d+)-job pool a block bootstrap and the other interval methods tried \(exploratory, \[report\]\(robustness/report\.md\)\) "
     r"change (?P<same>no verdict form) on EPYC 7763, 9V74 or 9V45; the two Xeon models \(inconclusive as pooled\) (?P<flips>become MAP under some of them)\. "
     r"A fresh, pre-planned run matched the original (?P<o>\d+)-job pool on (?P<yes>EPYC 7763 and 9V74), not (?P<no>9V45)\."),
    ("folders: the eight loops", "site/data/index.json criteria.kernels",
     exp_eight_loops, r"`kernels/` the (?P<n>\d+) loops"),
    ("folders: the kernel pool", "results/s4-run-*/ and results/s6-run-*/ result files",
     exp_kernel_pool_folders,
     r"the (?P<o>\d+) jobs of `s4-run-\*`, also pooled alone in `s4-pooled`, plus the (?P<n>\d+) of `s6-run-\*`"),
    ("found: reverse and stride-2, loops with and without an exit count",
     "investigate/vectorizer/reverse-stride2/extracted/scalar-evolution.txt tally lines, clang 18 FAST",
     exp_compile_only_counts,
     r"of (?P<n>\d+) loops compiled with FAST, all (?P<yes>\d+) with an iteration count for every exit in the compiler's analysis "
     r"were vectorized and none of the (?P<no>\d+) with an uncounted exit"),
    ("found: matrix multiply, the price of the checks", "investigate/vectorizer/matmul/raw/dbg_a18_fast.json; derived/cost-table.md",
     exp_matmul_units_readme,
     r"prices each of the two checks at (?P<u>\d+) units, so a width-4 vector iteration costs (?P<v>\d+) against (?P<s>\d+) for four scalar ones"),
    ("trust: shared machines", "results/s6-pooled/pooled.json; results/s6-run-*/; .github/workflows/measure.yml",
     exp_shared_machines,
     r"The kernel pool is (?P<jobs>\d+) jobs in (?P<runs>\d+) runs \((?P<lo>\d+) to (?P<hi>\d+) jobs for each AMD model, (?P<x>\d+) for each "
     r"Xeon model\); (?P<new>\d+) of them come from (?P<ten>\w+) later runs in which (?P<ret>\d+) of (?P<disp>\d+) dispatched jobs returned "
     r"results and the rest hit the (?P<limit>\d+)-minute limit"),
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
            "orr": str(len(original["runs"])), "nj": str(pooled_jobs() - pooled_jobs(original=True)),
            "later": word(later_runs()["runs"])}


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
    c = cpu_like("6973P-C")
    x = cell_of(c, "k03_stencil.L2")["aligned"]
    assert c["verdict"]["form"] == "inconclusive" and "missed by k03_stencil.L2" in c["verdict"]["why"]
    return {"r": f3(x["ratio"]), "lo": f3(x["ci95"][0]), "hi": f3(x["ci95"][1])}


def exp_table_note():
    a, b = cpu_like("8573C"), cpu_like("6973P-C")
    assert not cell_of(a, "k02_add_fwd.L1")["placement"]["sensitive"]
    assert cell_of(b, "k02_add_fwd.L1")["placement"]["sensitive"]
    runs = {len(a["per_run"]), len(b["per_run"])}
    per = max(r["jobs"] for c in (a, b) for r in c["per_run"])
    assert len(runs) == 1 and per < 3 and a["stability"] == b["stability"] == "not assessable"
    return {"p": f3(cell_of(a, "k02_add_fwd.L1")["aligned"]["ratio"]),
            "lim": f2(1 + a["verdict"]["forward_limit_pct"] / 100),
            "al": f3(cell_of(b, "k02_add_fwd.L1")["aligned"]["ratio"]),
            "ac": f3(cell_of(b, "k02_add_fwd.L1")["as_compiled"]["ratio"]),
            "end": f3(cell_of(b, "k03_stencil.L2")["aligned"]["ci95"][1]),
            "runs": str(runs.pop()), "per": str(per)}


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

    x8370, x8573, x6973 = of("Xeon 8370C"), of("Xeon 8573C"), of("Xeon 6973P-C")
    pooled_8573 = [r["aligned"] for r in rows if r["cpu_short"] == "Xeon 8573C" and "/results/s3-" not in "/" + r["source"]]
    assert f2(min(x6973)) == f2(max(x6973)), "the six 6973P-C jobs no longer round to one number"
    a = cell_of(cpu_like("8573C"), "k02_add_fwd.L1")["aligned"]
    b = cell_of(cpu_like("6973P-C"), "k02_add_fwd.L1")["aligned"]
    return {"lo": f2(aligned["min"]), "hi": f2(aligned["max"]), "jlo": f3(min(judged)), "jhi": f3(max(judged)),
            "n": str(len(rows)), "m": word(len(intel["cpus"])), "ilo": f2(intel["aligned"]["min"]), "ihi": f2(intel["aligned"]["max"]),
            "a1": f2(min(x8370)), "a2": f2(max(x8370)), "an": str(len(x8370)),
            "b1": f2(min(x8573)), "b2": f2(max(x8573)), "bn": str(len(x8573)), "bp": str(len(pooled_8573)),
            "bp1": f3(min(pooled_8573)), "bp2": f3(max(pooled_8573)),
            "bpool": f3(a["ratio"]), "bl": f3(a["ci95"][0]), "bh": f3(a["ci95"][1]),
            "c1": f2(min(x6973)), "cn": str(len(x6973)), "c2": f3(min(x6973)), "c3": f3(max(x6973)),
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
    """The no-vectorize build against the checks-on build at L1 on the four models the sentence names (all but EPYC 7763)."""
    others = [c for c in J(POOLED)["cpus"] if "7763" not in c["cpu_model"]]
    assert len(others) == 4, f"the sentence lists four models; the pool has {len(others)} besides EPYC 7763"
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
    cpus = J(POOLED)["cpus"]
    mm = [cell_of(c, k)[col]["ratio"] for c in cpus for k in ("k08_matmul.L1", "k08_matmul.L2") for col in ("as_compiled", "aligned")]
    c7763, c9v45 = cpu_like("7763"), cpu_like("9V45")
    return {"lo": f1(min(mm)), "hi": f1(max(mm)), "five": word(len(cpus)),
            "a": f1(cell_of(c7763, "k08_matmul.L1")["as_compiled"]["ratio"]),
            "b": f1(cell_of(c7763, "k08_matmul.L2")["as_compiled"]["ratio"]),
            "c": f1(max(cell_of(c9v45, k)["as_compiled"]["ratio"] for k in ("k08_matmul.L1", "k08_matmul.L2")))}


def exp_details_shared():
    pooled = J(POOLED)
    out = {"jobs": str(pooled_jobs()), "runs": str(len(pooled["runs"]))}
    for tag, key in (("a", "7763"), ("b", "9V45"), ("c", "9V74"), ("d", "8573C"), ("e", "6973P-C")):
        c = cpu_like(key)
        out[tag], out[tag + "r"] = str(c["jobs"]), str(len(c["runs"]))
    c7763, c9v74, c9v45 = cpu_like("7763"), cpu_like("9V74"), cpu_like("9V45")
    assert c7763["stability"] == c9v74["stability"] == "stable" and c9v45["stability"] == "not assessable"
    out.update({"need": str(J("site/data/index.json")["criteria"]["minimum_jobs"]),
                "s1": str(len(runs_with_verdict(c7763))), "s1n": str(len(c7763["runs"])),
                "s2": str(len(runs_with_verdict(c9v74))), "s2n": str(len(c9v74["runs"])),
                "n45": str(max(r["jobs"] for r in c9v45["per_run"]))})
    return out


def lost_cells(pooled):
    return [c[col]["ratio"] for cpu in pooled["cpus"] for c in cpu["cells"] if c["class"] == "lost" for col in ("as_compiled", "aligned")]


def exp_details_later_runs():
    lr = later_runs()
    original, new = J(POOLED_ORIGINAL), J(POOLED)
    assert not any("6973P-C" in c["cpu_model"] for c in original["cpus"]), "the Xeon 6973P-C is now in the original pool"
    shift = 0.0
    for c in new["cpus"]:
        if "AMD" not in c["cpu_model"]:
            continue
        old = next(o for o in original["cpus"] if o["cpu_model"] == c["cpu_model"])
        for x in c["cells"]:
            if x["class"] == "lost":
                y = cell_of(old, x["cell_id"])
                shift = max(shift, *(abs(x[col]["ratio"] - y[col]["ratio"]) for col in ("as_compiled", "aligned")))
    bound = int(shift * 100) / 100 + 0.01  # the next hundredth above the largest shift
    assert 0 < bound - shift <= 0.01
    page = J("site/data/index.json")["page"]["lost"]
    return {"disp": str(lr["dispatched"]), "ret": str(lr["returned"]), "miss": str(lr["dispatched"] - lr["returned"]),
            "lim": str(lr["limit"]), "now": str(lr["now"]), "o": str(pooled_jobs(original=True)), "mv": f2(bound),
            "lo": f3(page["min"]), "hi": f3(page["max"]), "olo": f3(min(lost_cells(original))), "ohi": f3(max(lost_cells(original))),
            "w": str(cpu_like("8573C", original=True)["jobs"]), "x": str(cpu_like("8573C")["jobs"]), "y": str(cpu_like("6973P-C")["jobs"])}


def exp_details_9v45_call():
    new, old = cpu_like("9V45"), cpu_like("9V45", original=True)
    a, b = cell_of(new, "k03_stencil.L1"), cell_of(old, "k03_stencil.L1")
    limit = 1 + new["verdict"]["forward_limit_pct"] / 100
    return {"a": f4(a["placement"]["d"]["ci95"][1]), "b": f4(b["placement"]["d"]["ci95"][1]),
            "n": str(pooled_jobs(original=True)), "c": f4(a["aligned"]["ci95"][1]), "lim": f4(limit),
            "d": f4(a["aligned"]["ci95"][1] - limit), "e": f3(b["aligned"]["ci95"][1])}


def exp_details_reproduction():
    a, b = cpu_like("7763")["reproduction"], cpu_like("9V74")["reproduction"]

    def gap(r):
        return f2(max(m["gap_pct"] for m in r["misses"]))

    return {"a": str(a["outside"]), "b": str(a["checked"]), "c": gap(a), "d": str(b["outside"]), "e": str(b["checked"]), "f": gap(b)}


def exp_details_aa():
    c = cpu_like("7763")
    return {"j": str(c["jobs"]), "a": f1(c["aa"]["half_width_pct"]), "b": f3(c["aa"]["half_width_pct"])}


def exp_details_stage_s6():
    lr = later_runs()
    return {"disp": str(lr["dispatched"]), "ret": str(lr["returned"]), "miss": str(lr["dispatched"] - lr["returned"]),
            "lim": str(lr["limit"]), "o": str(pooled_jobs(original=True))}


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


def exp_details_commit():
    sha, tags = llvm_commit()
    assert tags["llvmorg-19.1.0"] == "ahead"
    assert all(tags[f"llvmorg-{v}"] != "ahead" for v in ("18.1.0", "18.1.3", "18.1.8"))
    return {"sha": sha, "in": "19.1.0", "n1": "18.1.0", "n2": "18.1.3", "n3": "18.1.8"}


DETAILS_ROWS = [
    ("details: the method, jobs and runs", "results/s6-pooled/pooled.json; results/s4-pooled/pooled.json; results/s6-run-*/",
     exp_details_method,
     r"(?P<jobs>\d+) jobs over (?P<runs>\d+) runs \(the original (?P<oj>\d+) jobs in (?P<orr>\d+) runs, then (?P<nj>\d+) more from "
     r"(?P<later>\w+) later runs\)"),
] + [
    (f"details: table row, {name}", "results/s6-pooled/pooled.json cells, aa and runs", exp_table_row(key), table_row_pattern(name))
    for name, key in TABLE_MODELS
] + [
    ("details: table, stability of EPYC 7763 and 9V74", "results/s6-pooled/pooled.json per_run", exp_table_stability_7763_9v74,
     r"\| AMD EPYC 7763 \|[^|\n]*\|[^|\n]*\| MAP, the same in each of the (?P<a>\d+) runs with 3 or more jobs \(the other run has (?P<ao>\d+)\)"
     r".*?\| AMD EPYC 9V74 \|[^|\n]*\|[^|\n]*\| MAP, the same in each of the (?P<b>\d+) runs with 3 or more jobs \(the other (?P<bo>\d+) have fewer\)"),
    ("details: table, EPYC 9V45 borderline", "results/s6-pooled/pooled.json EPYC 9V45 per_run and k03_stencil.L1", exp_table_9v45,
     r"MAP; stability not assessable \((?P<one>\d+) of (?P<n>\d+) runs has 3 or more jobs, and that run alone is INCONCLUSIVE\); "
     r"borderline: counted, one left-out cell would miss the forward limit by (?P<m>[\d.]+) \|"),
    ("details: table, Xeon 8573C verdict", "results/s6-pooled/pooled.json Xeon 8573C k02_add_fwd.L1 aligned", exp_table_8573c,
     r"INCONCLUSIVE: the forward add at L1, aligned (?P<r>[\d.]+) \[(?P<lo>[\d.]+), (?P<hi>[\d.]+)\], misses the 2% forward rule"),
    ("details: table, Xeon 6973P-C verdict", "results/s6-pooled/pooled.json Xeon 6973P-C k03_stencil.L2 aligned", exp_table_6973pc,
     r"INCONCLUSIVE: the stencil at L2, aligned (?P<r>[\d.]+) \[(?P<lo>[\d.]+), (?P<hi>[\d.]+)\], misses the forward rule"),
    ("details: table, the note on the Intel rows", "results/s6-pooled/pooled.json Xeon cells and per_run", exp_table_note,
     r"fails the rule \(point (?P<p>[\d.]+), limit (?P<lim>[\d.]+)\)\. For the Xeon 6973P-C the forward add at L1 \(aligned (?P<al>[\d.]+), "
     r"as compiled (?P<ac>[\d.]+)\) is placement-sensitive and left out, and the verdict fails on the stencil at L2, whose interval ends at "
     r"(?P<end>[\d.]+)\. Neither model has a run with 3 jobs, so stability is not assessable, and the jobs of each came from (?P<runs>\d+) runs "
     r"\(at most (?P<per>\d+) per run\)"),
    ("details: forward loops, AMD and Intel", "site/data/index.json page.forward and intel_forward; results/s6-pooled/pooled.json",
     exp_details_forward,
     r"forward loops ran (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x of the unchecked time there; .*?judges ran (?P<jlo>[\d.]+)x to (?P<jhi>[\d.]+)x\. "
     r"The Intel models differ\. In each of (?P<n>\d+) Intel jobs of the main runs \((?P<m>\w+) models\) the forward add at L1, aligned, cost "
     r"(?P<ilo>[\d.]+)x to (?P<ihi>[\d.]+)x: Xeon 8370C (?P<a1>[\d.]+)x to (?P<a2>[\d.]+)x \((?P<an>\d+) early jobs, not in the kernel pool\), "
     r"Xeon 8573C (?P<b1>[\d.]+)x to (?P<b2>[\d.]+)x \((?P<bn>\d+) jobs; the (?P<bp>\d+) pooled ones (?P<bp1>[\d.]+) to (?P<bp2>[\d.]+), "
     r"pooled (?P<bpool>[\d.]+) \[(?P<bl>[\d.]+), (?P<bh>[\d.]+)\]\) and Xeon 6973P-C (?P<c1>[\d.]+)x \((?P<cn>\d+) jobs, "
     r"(?P<c2>[\d.]+) to (?P<c3>[\d.]+), pooled (?P<cpool>[\d.]+) \[(?P<cl>[\d.]+), (?P<ch>[\d.]+)\]\)"),
    ("details: positive control on EPYC 7763", "results/s6-pooled/pooled.json EPYC 7763 positive and cells", exp_details_positive,
     r"the (?P<p>\d+)-job pool in `results/s6-pooled/pooled.json` gives (?P<a>[\d.]+)x and (?P<b>[\d.]+)x\).*?"
     r"Pooled EPYC 7763 positive control \((?P<jobs>\d+) jobs, .*?reverse (?P<r1>[\d.]+)x at L1 and (?P<r2>[\d.]+)x at L2 against "
     r"(?P<R1>[\d.]+)x and (?P<R2>[\d.]+)x; stride-2 (?P<s1>[\d.]+)x and (?P<s2>[\d.]+)x against (?P<S1>[\d.]+)x and (?P<S2>[\d.]+)x; "
     r"matrix multiply (?P<m1>[\d.]+)x and (?P<m2>[\d.]+)x against (?P<M1>[\d.]+)x and (?P<M2>[\d.]+)x\."),
    ("details: no-vectorize build on the other models", "results/s6-pooled/pooled.json positive and cells, the other four models",
     exp_details_novec_range,
     r"the no-vectorize build at (?P<nlo>[\d.]+)x to (?P<nhi>[\d.]+)x at L1 against (?P<olo>[\d.]+)x to (?P<ohi>[\d.]+)x with the checks on "
     r"\(EPYC 9V45, EPYC 9V74, Xeon 8573C and Xeon 6973P-C\)"),
    ("details: forward add instructions bullet", "results/s6-pooled/pooled.json Xeon k02_add_fwd.L1 aligned", exp_details_instr_bullet,
     r"on the Intel models it is (?P<a>[\d.]+)x at L1 on the Xeon 8573C and (?P<b>[\d.]+)x on the Xeon 6973P-C \((?P<j>\d+) pooled jobs each\)"),
    ("details: matrix multiply across the CPU models", "results/s6-pooled/pooled.json k08_matmul cells", exp_details_versions,
     r"at (?P<lo>[\d.]+)x to (?P<hi>[\d.]+)x across the (?P<five>\w+) CPU models: (?P<a>[\d.]+)x at L1 and (?P<b>[\d.]+)x at L2 on EPYC 7763, "
     r"up to (?P<c>[\d.]+)x on EPYC 9V45 as compiled"),
    ("details: shared runners, jobs per model", "results/s6-pooled/pooled.json cpus, per_run, stability", exp_details_shared,
     r"The kernel pool has (?P<jobs>\d+) jobs in (?P<runs>\d+) runs: EPYC 7763 (?P<a>\d+) jobs \((?P<ar>\d+) runs\), EPYC 9V45 (?P<b>\d+) "
     r"\((?P<br>\d+)\), EPYC 9V74 (?P<c>\d+) \((?P<cr>\d+)\), Xeon Platinum 8573C (?P<d>\d+) \((?P<dr>\d+)\) and Xeon 6973P-C (?P<e>\d+) "
     r"\((?P<er>\d+)\)\. A run needs (?P<need>\d+) jobs .*?only EPYC 7763 \((?P<s1>\d+) of its (?P<s1n>\d+) runs\) and EPYC 9V74 "
     r"\((?P<s2>\d+) of (?P<s2n>\d+)\) could be tested.*?EPYC 9V45 has one run with (?P<n45>\d+) jobs"),
    ("details: the ten later runs", "results/s6-run-*/; .github/workflows/measure.yml; results/s4-pooled and s6-pooled", exp_details_later_runs,
     r"added jobs: (?P<disp>\d+) dispatched, (?P<ret>\d+) returned results, and the other (?P<miss>\d+) ran past the workflow's (?P<lim>\d+)-minute "
     r"job limit .*?\(the limit is (?P<now>\d+) minutes now\)\..*?Pooled with the original (?P<o>\d+) jobs, no lost-loop cell on an AMD model "
     r"moved by more than (?P<mv>[\d.]+) \(the lowest and highest cells are (?P<lo>[\d.]+) and (?P<hi>[\d.]+) against (?P<olo>[\d.]+) and "
     r"(?P<ohi>[\d.]+) in the original pool\); the Xeon 8573C went from (?P<w>\d+) job to (?P<x>\d+), and the Xeon 6973P-C, absent "
     r"before, has (?P<y>\d+)\."),
    ("details: EPYC 9V45 borderline call", "results/s6-pooled/pooled.json and results/s4-pooled/pooled.json EPYC 9V45 k03_stencil.L1",
     exp_details_9v45_call,
     r"the interval of the placement statistic ends at (?P<a>[\d.]+), under 1 \((?P<b>[\d.]+) in the original (?P<n>\d+)-job pool\)\. "
     r"Counted as a judged forward cell, its aligned interval would reach (?P<c>[\d.]+), above the (?P<lim>[\d.]+) limit by (?P<d>[\d.]+) "
     r"\((?P<e>[\d.]+) in the original pool\)"),
    ("details: reproduction across runs", "results/s6-pooled/pooled.json reproduction", exp_details_reproduction,
     r"outside another run's interval (?P<a>\d+) times out of (?P<b>\d+) on EPYC 7763 \(largest gap (?P<c>[\d.]+)%\) and (?P<d>\d+) times out "
     r"of (?P<e>\d+) on EPYC 9V74 \(largest gap (?P<f>[\d.]+)%\)"),
    ("details: kernel A/A floor on EPYC 7763", "results/s6-pooled/pooled.json EPYC 7763 aa", exp_details_aa,
     r"pooled over (?P<j>\d+) jobs, the kernel A/A floor on EPYC 7763 is about (?P<a>[\d.]+)% \((?P<b>[\d.]+)%\)"),
    ("details: stage S6", "results/s6-run-*/; .github/workflows/measure.yml", exp_details_stage_s6,
     r"\| S6 \| More jobs: ten further runs of `measure.yml`, (?P<disp>\d+) jobs dispatched, (?P<ret>\d+) returned results, the other "
     r"(?P<miss>\d+) cancelled at the (?P<lim>\d+)-minute job limit .*?pooled with the (?P<o>\d+) S4 jobs"),
    ("details: reverse and stride-2 study", "investigate/vectorizer/reverse-stride2/ extracted/ and raw/", exp_details_reverse_stride2,
     r"reverse-stride2/README\.md\), (?P<ans>\d+) saved answers\)\. Observed: .*?over (?P<n>\d+) loops compiled with FAST on clang 18\.1\.0, "
     r".*?\((?P<yes>\d+) of (?P<yes2>\d+) loops with a count for every exit vectorized, none of the (?P<no>\d+) with an uncounted exit\); "
     r".*?vectorized exactly the (?P<hv>\d+) of (?P<hn>\d+) functions whose exit got a count"),
    ("details: matrix multiply study", "investigate/vectorizer/matmul/ raw/, derived/cost-table.md, requests.tsv", exp_details_matmul,
     r"matmul/README\.md\), (?P<req>\d+) compile requests, all answered and saved\)\. Observed on clang 18\.1\.0 at baseline x86-64 \(SSE2\): "
     r"legality passes, and the cost model prices each of the two bounds-check compares at (?P<c18>\d+) units at width 4 "
     r"\((?P<c42>\d+) on SSE4\.2, (?P<c3>\d+) on AVX2, where clang 18 vectorizes the loop\), so the width-4 loop sums to (?P<vec>\d+) against "
     r"(?P<sc>\d+) for four scalar iterations.*?Clang 19 to 21 find the two compares uniform and price them at (?P<c19>\d+) each"),
    ("details: the LLVM commit and the tags", "investigate/vectorizer/matmul/llvm-src/commit_b6a8f5486b.json and commit_in_tag.json",
     exp_details_commit,
     r"LLVM commit `(?P<sha>[0-9a-f]{10})` .*? is in `llvmorg-(?P<in>[\d.]+)` and not in `llvmorg-(?P<n1>[\d.]+)`, `(?P<n2>[\d.]+)` or `(?P<n3>[\d.]+)`"),
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

    @pytest.mark.parametrize("row", [_param(r) for r in DETAILS_ROWS])
    def test_details_number(row):
        check_row(row, details_text())
else:
    def test_readme_numbers_all_rows():
        failures = []
        for rows, text in ((ROWS, readme_text()), (DETAILS_ROWS, details_text())):
            for row in rows:
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
