"""The three round-7 analyses as the page quotes them: robustness/calibration.json (the run-to-run count calibrated intervals would
give), robustness/seed-sensitivity-x86.json (the x86-64 pool under other bootstrap seeds) and robustness/aa-l2.json (the
identical-binary A/A at the L2 size), as scripts/build_site_data.py copies them into site/data/index.json ("robustness") and the
real-world pool's "max_in_a_run" into site/data/realworld.json.

Four kinds of test. (1) Copy: every figure in index.json["robustness"] is read here again from the raw file, with the arithmetic
written again (not imported from the builder), and the stored file hashes equal the files' own. (2) Guards of the builder: each
file is checked against the pool it must have read, against the pool's own counts and against the stored word before one number
is copied, and the builder refuses a file for which any of them fails (each is tampered here in memory). (3) The figures the page
quotes for the Xeon 6973P-C (13 of 60 other seeds inconclusive, an end 0.0004 below the limit, an L2 A/A of 2.34%) and for the
real programs (no run holds three jobs of the other two CPU models). (4) None of these numbers is typed in the page's own files:
they come from site/data, so a change in the stored files reaches the page and is caught by scripts/build_site_data.py --check.

Offline. No fixtures, so scripts/check.py's built-in runner runs it."""
import copy
import hashlib
import importlib.util
import json
import os
import re
import sys
from functools import lru_cache

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
X86_POOLED = "results/s7-pooled/pooled.json"
ARM_POOLED = "results/s8-arm-pooled/pooled.json"
XEON_6973 = "Intel(R) Xeon(R) 6973P-C"
XEON_8573 = "INTEL(R) XEON(R) PLATINUM 8573C"
EPYC_7763 = "AMD EPYC 7763 64-Core Processor"
EPYC_9V74 = "AMD EPYC 9V74 80-Core Processor"
EPYC_9V45 = "AMD EPYC 9V45 96-Core Processor"


def read(rel):
    with open(os.path.join(REPO, *rel.split("/")), encoding="utf-8") as f:
        return json.load(f)


def lf_sha256(rel):
    """Written again here (not imported from the builder): sha256 with CRLF read as LF."""
    with open(os.path.join(REPO, *rel.split("/")), "rb") as f:
        return hashlib.sha256(f.read().replace(bytes([13, 10]), bytes([10]))).hexdigest()


@lru_cache(maxsize=None)
def builder():
    key = "robustness_test_build"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, "scripts", "build_site_data.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


@lru_cache(maxsize=None)
def site_rob():
    return read("site/data/index.json")["robustness"]


# ------------------------------------------------------------------ (1) the copy equals the files
def test_calibration_figures_equal_the_file_and_the_pools_own_counts():
    cal, rob = read("robustness/calibration.json"), site_rob()["calibration"]
    pool = {c["cpu_model"]: c for c in read(X86_POOLED)["cpus"]}
    assert set(rob["x86"]) == {m["cpu_model"] for m in cal["run_to_run"]["s7"]["models"]} == {EPYC_7763, EPYC_9V74}
    for m in cal["run_to_run"]["s7"]["models"]:
        got = rob["x86"][m["cpu_model"]]
        assert (got["checked"], got["outside"]) == (m["checked"], m["outside"]) == (pool[m["cpu_model"]]["reproduction"]["checked"], pool[m["cpu_model"]]["reproduction"]["outside"])
        assert got["expected_outside"] == m["expected_outside"]
        assert got["independent_lo"] == m["simulation"]["independent"]["p025"] and got["independent_hi"] == m["simulation"]["independent"]["p975"]
        assert got["jobs"] == m["jobs"]
    # the Arm column is additive (tests/test_arm64_data.py: it changes no x86-64 file), so its entry is in site/data/arm64.json
    assert "arm" not in rob
    (arm,) = cal["run_to_run"]["s8-arm"]["models"]
    arm_rep = read(ARM_POOLED)["cpus"][0]["reproduction"]
    got = read("site/data/arm64.json")["reproduction_calibration"]
    assert got["source"] == "robustness/calibration.json" and got["source_sha256"] == lf_sha256("robustness/calibration.json")
    assert (got["checked"], got["outside"]) == (arm["checked"], arm["outside"]) == (arm_rep["checked"], arm_rep["outside"]) == (192, 13)
    assert got["expected_outside"] == arm["expected_outside"] and got["jobs"] == arm["jobs"]
    assert got["independent_lo"] == arm["simulation"]["independent"]["p025"] and got["independent_hi"] == arm["simulation"]["independent"]["p975"]
    assert (read("site/data/arm64.json")["reproduction"]["checked"], read("site/data/arm64.json")["reproduction"]["outside"]) == (192, 13)
    # what the page prints: the expectation beside each count
    assert [round(rob["x86"][m]["expected_outside"], 1) for m in (EPYC_7763, EPYC_9V74)] == [148.4, 88.4] and round(got["expected_outside"], 1) == 34.7


def test_seed_figures_equal_the_file():
    seeds, rob = read("robustness/seed-sensitivity-x86.json"), site_rob()["seeds"]
    assert rob["other_seeds"] == seeds["alt_seeds"]["count"] == 400
    for model, w in seeds["whole"]["models"].items():
        got = rob["models"][model]
        assert (got["jobs"], got["stored_form"], got["seeds"]) == (w["jobs"], w["stored_form"], seeds["whole"]["count"])
        assert got["forms"] == {"map": w["tally"]["forms"].get("map", 0), "inconclusive": w["tally"]["forms"].get("inconclusive", 0)}
        assert got["forms"]["map"] + got["forms"]["inconclusive"] == got["seeds"], f"{model}: a form other than map and inconclusive appears under other seeds"
    forward = [e for e in seeds["cells"] if e["kind"] == "forward" and e["column"] == "aligned"]
    assert sum(len(m["cells"]) for m in rob["models"].values()) == len(forward)
    for e in forward:
        got = rob["models"][e["cpu_model"]]["cells"][e["cell_id"]]
        lim = e["alt"]["summary"]["limit"]
        assert got == {"limit": lim, "stored_hi": e["stored"]["hi"], "converged_hi": e["converged"]["hi"], "converged_under": lim - e["converged"]["hi"],
                       "draws": e["converged"]["resamples"], "alt_draws": e["alt"]["draws"], "alt_at_or_above": e["alt"]["summary"]["at_or_above_limit"]}


def test_aa_l2_figures_equal_the_file():
    aal2, rob = read("robustness/aa-l2.json"), site_rob()["aa_l2"]
    pool = next(p for p in aal2["pools"] if p["id"] == "s7")
    assert rob["ceiling_pct"] == aal2["criteria"]["aa_half_width_max_pct"] == 2.0
    assert set(rob["models"]) == {m["cpu_model"] for m in pool["models"]}
    pooled = {c["cpu_model"]: c for c in read(X86_POOLED)["cpus"]}
    for m in pool["models"]:
        got = rob["models"][m["cpu_model"]]
        assert got == {"jobs": m["jobs"], "l1_pct": m["l1"]["half_width_pct"], "l2_pct": m["l2"]["half_width_pct"], "l2_jobs_above": m["l2"]["jobs_above_ceiling"]}
        assert got["l1_pct"] == pooled[m["cpu_model"]]["aa"]["half_width_pct"], f"{m['cpu_model']}: the L1 pair the page calls the A/A band is not the pool's"


def test_stored_source_hashes_equal_the_files():
    rob = site_rob()
    for key, rel in (("calibration", "robustness/calibration.json"), ("seeds", "robustness/seed-sensitivity-x86.json"), ("aa_l2", "robustness/aa-l2.json")):
        assert rob[key]["source"] == rel and rob[key]["source_sha256"] == lf_sha256(rel), f"{rel}: site/data/index.json holds another file's hash"
    assert read("robustness/calibration.json")["inputs"]["pools"]["s7"]["sha256"] == lf_sha256(X86_POOLED)
    assert read("robustness/calibration.json")["inputs"]["pools"]["s8-arm"]["sha256"] == lf_sha256(ARM_POOLED)
    assert read("robustness/seed-sensitivity-x86.json")["pool"]["sha256"] == lf_sha256(X86_POOLED)
    assert read("robustness/aa-l2.json")["inputs"][X86_POOLED] == lf_sha256(X86_POOLED)


def test_builder_gives_what_index_json_holds():
    b = builder()
    assert b.robustness_data(b.load(os.path.join(REPO, X86_POOLED))) == site_rob()


# ------------------------------------------------------------------ (2) the builder refuses a file that fails a guard
def _tampered(edit_path, edit):
    """robustness_data() with one of the three files (or none) edited in memory by `edit`: returns the exception it raises, or None."""
    b = builder()
    real = b.load

    def load(path):
        doc = copy.deepcopy(real(path))
        if os.path.normpath(path).endswith(os.path.normpath(edit_path)):
            edit(doc)
        return doc
    b.load = load
    try:
        b.robustness_data(real(os.path.join(REPO, X86_POOLED)))
        return None
    except AssertionError as e:
        return e
    finally:
        b.load = real


def _first_forward(seeds):
    return next(e for e in seeds["cells"] if e["kind"] == "forward" and e["column"] == "aligned")


GUARDS = [
    ("calibration counts differ from the pool's own", "robustness/calibration.json", lambda d: d["run_to_run"]["s7"]["models"][0].__setitem__("outside", d["run_to_run"]["s7"]["models"][0]["outside"] + 1), "counts"),
    ("calibration read another x86-64 pool", "robustness/calibration.json", lambda d: d["inputs"]["pools"]["s7"].__setitem__("sha256", "0" * 64), "another x86-64 pool"),
    ("seeds file read another pool", "robustness/seed-sensitivity-x86.json", lambda d: d["pool"].__setitem__("sha256", "0" * 64), "another pool"),
    ("seeds file stored word is not the pool's", "robustness/seed-sensitivity-x86.json",
     lambda d: d["whole"]["models"][EPYC_9V45].__setitem__("stored_form", "inconclusive"), "stored word"),
    ("seeds file stored end is not the pool's", "robustness/seed-sensitivity-x86.json",
     lambda d: _first_forward(d)["stored"].__setitem__("hi", _first_forward(d)["stored"]["hi"] + 0.001), "stored end"),
    ("aa-l2 read another pool", "robustness/aa-l2.json", lambda d: d["inputs"].__setitem__(X86_POOLED, "0" * 64), "another x86-64 pool"),
    ("aa-l2 L1 is not the pool's", "robustness/aa-l2.json",
     lambda d: next(p for p in d["pools"] if p["id"] == "s7")["models"][0]["l1"].__setitem__("half_width_pct", next(p for p in d["pools"] if p["id"] == "s7")["models"][0]["l1"]["half_width_pct"] + 0.1), "L1 A/A"),
]


def test_untouched_files_pass_the_guards():
    assert _tampered("robustness/none.json", lambda d: None) is None


def _arm_args():
    b = builder()
    pool = b.load(os.path.join(REPO, ARM_POOLED))
    c = pool["cpus"][0]
    return b, copy.deepcopy(b.load(os.path.join(REPO, "robustness/calibration.json"))), b.sha(os.path.join(REPO, ARM_POOLED)), c["cpu_model"], copy.deepcopy(c["reproduction"])


ARM_GUARDS = [
    ("the calibration file read another Arm pool", lambda cal, rep: cal["inputs"]["pools"]["s8-arm"].__setitem__("sha256", "0" * 64), "another Arm pool"),
    ("the calibration file names another Arm pool path", lambda cal, rep: cal["inputs"]["pools"]["s8-arm"].__setitem__("path", "results/other/pooled.json"), "another Arm pool"),
    ("the calibration count differs from the pool's own", lambda cal, rep: cal["run_to_run"]["s8-arm"]["models"][0].__setitem__("outside", cal["run_to_run"]["s8-arm"]["models"][0]["outside"] + 1), "counts"),
    ("the pool's own count differs from the calibration's", lambda cal, rep: rep.__setitem__("checked", rep["checked"] + 1), "counts"),
    ("the calibration file is about another CPU model", lambda cal, rep: cal["run_to_run"]["s8-arm"]["models"][0].__setitem__("cpu_model", "Other"), "another Arm CPU model"),
]


def test_the_arm_calibration_entry_is_what_arm64_json_holds():
    b, cal, s, model, rep = _arm_args()
    assert b.arm_calibration(cal, s, model, rep) == read("site/data/arm64.json")["reproduction_calibration"]


@pytest.mark.parametrize("name,edit,word", ARM_GUARDS, ids=[g[0] for g in ARM_GUARDS])
def test_builder_refuses_an_arm_calibration_that_fails_a_guard(name, edit, word):
    b, cal, s, model, rep = _arm_args()
    edit(cal, rep)
    with pytest.raises(AssertionError) as e:
        b.arm_calibration(cal, s, model, rep)
    assert word in str(e.value), f"{name}: it failed, but not on that guard ({e.value})"


@pytest.mark.parametrize("name,path,edit,word", GUARDS, ids=[g[0] for g in GUARDS])
def test_builder_refuses_a_file_that_fails_a_guard(name, path, edit, word):
    err = _tampered(path, edit)
    assert err is not None, f"{name}: robustness_data() accepted it"
    assert word in str(err), f"{name}: it failed, but not on that guard ({err})"


# ------------------------------------------------------------------ (3) the figures the page quotes
def test_the_xeon_6973_margin_is_undecided_as_the_page_says():
    seeds, aal2 = read("robustness/seed-sensitivity-x86.json"), read("robustness/aa-l2.json")
    w = seeds["whole"]["models"][XEON_6973]
    cell = next(e for e in seeds["cells"] if e["cpu_model"] == XEON_6973 and e["cell_id"] == "k03_stencil.L2" and e["kind"] == "forward" and e["column"] == "aligned")
    l2 = next(m for m in next(p for p in aal2["pools"] if p["id"] == "s7")["models"] if m["cpu_model"] == XEON_6973)
    pooled = next(c for c in read(X86_POOLED)["cpus"] if c["cpu_model"] == XEON_6973)
    assert pooled["verdict"]["form"] == "map" and w["stored_form"] == "map"
    assert (w["tally"]["forms"]["inconclusive"], seeds["whole"]["count"]) == (13, 60), "13 of 60 other seeds give an inconclusive verdict"
    assert round(cell["alt"]["summary"]["limit"] - cell["converged"]["hi"], 4) == 0.0004 and cell["converged"]["resamples"] == 100000
    assert round(l2["l2"]["half_width_pct"], 2) == 2.34 and l2["l2"]["half_width_pct"] > aal2["criteria"]["aa_half_width_max_pct"] > l2["l1"]["half_width_pct"]
    # the page's own derivation says the same: the clause is added for this model and for no other model the seed file covers
    # (9V45 gives MAP under all 60 seeds; 8573C has no MAP to doubt)
    for model in (XEON_8573, EPYC_9V45):
        assert site_rob()["seeds"]["models"][model]["forms"]["inconclusive"] in (0, 60), f"{model}: a second model now stands on a seed-dependent word; check the page's wording"


def test_no_run_holds_the_minimum_number_of_jobs_of_the_other_two_cpu_models():
    pooled = read("results/realworld-pooled/realworld.json")
    mn = pooled["minimum_jobs"]
    per = {}
    for i in pooled["inputs"]:
        per[(i["cpu_model"], i["run_id"])] = per.get((i["cpu_model"], i["run_id"]), 0) + 1
    main = next(g for g in pooled["cpus"] if g["jobs"] >= mn)
    rest = [g["cpu_model"] for g in pooled["cpus"] if g["cpu_model"] != main["cpu_model"]]
    assert len(rest) == 2 and all(max(n for (m, _), n in per.items() if m == r) < mn for r in rest), \
        "a run now holds enough jobs of an 'other' CPU model: the sentence 'no run holds ... to test it' (site/app.js, rwOtherCap) is no longer true"
    for g in read("site/data/realworld.json")["timing"]["groups"]:
        want = max(n for (m, _), n in per.items() if m == g["cpu_model"])
        assert g["max_in_a_run"] == want


def test_no_xeon_model_has_two_runs_that_can_be_judged_alone():
    pooled = read(X86_POOLED)
    mn = read("harness/criteria-v3.json")["minimum_jobs"] if "minimum_jobs" in read("harness/criteria-v3.json") else read("site/data/index.json")["criteria"]["minimum_jobs"]
    xeon = [c for c in pooled["cpus"] if "xeon" in c["cpu_model"].lower()]
    assert xeon and all(sum(1 for r in c["per_run"] if r["jobs"] >= mn) < 2 for c in xeon), \
        "a Xeon model has two runs of enough jobs: the sentence '(no Xeon model has two runs of 3 or more jobs)' is no longer true"


# ------------------------------------------------------------------ (4) no typed copy of a figure in the page's own files
@pytest.mark.parametrize("fname", ["app.js", "index.html", "details.html"])
def test_the_new_figures_are_not_typed_in_the_page_files(fname):
    with open(os.path.join(REPO, "site", fname), encoding="utf-8") as f:
        text = f.read()
    for lit in ("148.4", "88.4", "34.7", "2.34%", "0.0004", "13 of 60", "100,000", "no run holds 3", "two runs of 3"):
        assert lit not in text, f"site/{fname} types {lit!r}; the figure must come from site/data (scripts/build_site_data.py)"
    assert not re.search(r"understate", text, re.I), f"site/{fname} says the intervals understate the spread: robustness/calibration.json does not show that for every model"
