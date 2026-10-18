"""replication/ (plan: replication/PLAN.md, written before the runs): replication/compare.py, replication/results.json,
site/data/replication.json and the checks that cover the new run folders.

Two kinds of test.

Stored data. The numbers the replication reports are asserted here from the six pooled.json files (read again below by
code written in this file where a count is involved, not through compare.py) and then from replication/results.json and
site/data/replication.json: the counts of jobs and runs, the verdict word of every CPU model in each pool, the cause cell
of every verdict that is not MAP, the share of points inside the earlier interval, the three stories (the Arm cell, the two
knife-edge flips, the Xeon 6973P-C that cannot be tested), the lost-SIMD range against the range the page prints, and the
fact that the two x86-64 combine jobs that ended red pass the independent check now.

Logic. compare.py's functions on made-up pools: the inside test is harness/pool.py reproduction()'s, a cause is rebuilt
from the cells and must equal the stored sentence, the minimum number of jobs decides what is testable, the headline
range reports a cell whose one-decimal form lies outside the printed range, and verification catches a change in any leaf
of the stored file.

Offline and read-only (the site builds go to temporary folders). No fixtures, so scripts/check.py's built-in runner runs it."""
import contextlib
import copy
import glob
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402
import pool_check  # noqa: E402


def _load(key, rel):
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


cmp = _load("replication_compare", os.path.join("replication", "compare.py"))

ARM = {"earlier": "results/s8-arm-pooled/pooled.json", "replication": "results/s9-arm-b-pooled/pooled.json",
       "secondary": "results/s9-arm-ab-pooled/pooled.json"}
X86 = {"earlier": "results/s7-pooled/pooled.json", "replication": "results/s9-x86-c-pooled/pooled.json",
       "secondary": "results/s9-x86-ac-pooled/pooled.json"}
EPYC7763, EPYC9V45, EPYC9V74 = "AMD EPYC 7763 64-Core Processor", "AMD EPYC 9V45 96-Core Processor", "AMD EPYC 9V74 80-Core Processor"
XEON8573C, XEON6973PC, XEON8370C = "INTEL(R) XEON(R) PLATINUM 8573C", "Intel(R) Xeon(R) 6973P-C", "Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz"
N2, V3 = "Neoverse-N2", "Neoverse-V3"
IN_CACHE = ("L1", "L2")


def f1(x):
    return f"{x:.1f}"


def f2(x):
    return f"{x:.2f}"


def f3(x):
    return f"{x:.3f}"


def f4(x):
    return f"{x:.4f}"


def read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def pooled(rel):
    return read(*rel.split("/"))


@lru_cache(maxsize=None)
def results():
    return read("replication", "results.json")


@lru_cache(maxsize=None)
def site():
    return read("site", "data", "replication.json")


@lru_cache(maxsize=None)
def criteria():
    return read("harness", "criteria-v3.json")


def blk(rel, model):
    return next((b for b in pooled(rel)["cpus"] if b["cpu_model"] == model), None)


def cell(b, cid):
    return next(c for c in b["cells"] if c["cell_id"] == cid)


def row(arch, model):
    return next(r for r in results()[arch]["models"] if r["cpu_model"] == model)


def pcell(rel, model, cid):
    return cell(blk(rel, model), cid)


def inside_by_hand(new, old):
    """(checked, inside) of the in-cache points of `new` against the 95% intervals of `old`, written again here (two loops)."""
    checked = inside = 0
    for c in new["cells"]:
        if c["size_class"] not in IN_CACHE:
            continue
        o = next((x for x in old["cells"] if x["cell_id"] == c["cell_id"]), None)
        if o is None:
            continue
        for col in ("as_compiled", "aligned"):
            checked += 1
            if o[col]["ci95"][0] <= c[col]["ratio"] <= o[col]["ci95"][1]:
                inside += 1
    return checked, inside


# ---------------------------------------------------------------- the files are what the plan describes

def test_results_json_equals_a_recomputation_from_the_pooled_files():
    assert cmp.same(results(), cmp.build()) == []


def test_build_is_deterministic():
    assert cmp.dumps(cmp.build()) == cmp.dumps(cmp.build())
    with open(os.path.join(REPO, "replication", "results.json"), encoding="utf-8", newline="") as f:
        assert f.read() == cmp.dumps(cmp.build()), "the stored file is not byte for byte what compare.py writes"


def test_the_sets_are_the_ones_the_plan_names():
    plan = open(os.path.join(REPO, "replication", "PLAN.md"), encoding="utf-8").read()
    assert re.search(r"\| B \(Arm\) \| `ubuntu-24.04-arm` \| 3 \| 30 \|", plan), "the plan no longer says set B is 3 runs and 30 jobs"
    assert re.search(r"\| C \(x86-64\) \| `ubuntu-24.04` \| 4 \| 40 \|", plan), "the plan no longer says set C is 4 runs and 40 jobs"
    p = results()["pools"]
    for arch, files in (("arm", ARM), ("x86", X86)):
        for role, rel in files.items():
            assert p[arch][role]["path"] == rel and p[arch][role]["jobs"] == len(pooled(rel)["inputs"])
            assert p[arch][role]["runs"] == pooled(rel)["runs"]
    assert (p["arm"]["earlier"]["jobs"], len(p["arm"]["earlier"]["runs"])) == (30, 3)
    assert (p["arm"]["replication"]["jobs"], len(p["arm"]["replication"]["runs"])) == (30, 3)
    assert (p["arm"]["secondary"]["jobs"], len(p["arm"]["secondary"]["runs"])) == (60, 6)
    assert (p["x86"]["earlier"]["jobs"], len(p["x86"]["earlier"]["runs"])) == (95, 15)
    assert (p["x86"]["replication"]["jobs"], len(p["x86"]["replication"]["runs"])) == (40, 4)
    assert (p["x86"]["secondary"]["jobs"], len(p["x86"]["secondary"]["runs"])) == (135, 19)
    assert p["arm"]["replication"]["models_drawn"] == {N2: 29, V3: 1}
    assert p["arm"]["secondary"]["models_drawn"] == {N2: 59, V3: 1}
    # the run folders on disk are the runs the new pools name, and the secondary pools are the unions
    arm_b = sorted(os.path.basename(d)[len("s9-arm-run-"):] for d in glob.glob(os.path.join(REPO, "results", "s9-arm-run-*")))
    x86_c = sorted(os.path.basename(d)[len("s9-run-"):] for d in glob.glob(os.path.join(REPO, "results", "s9-run-*")))
    assert arm_b == sorted(p["arm"]["replication"]["runs"]) and x86_c == sorted(p["x86"]["replication"]["runs"])
    assert sorted(p["arm"]["secondary"]["runs"]) == sorted(p["arm"]["earlier"]["runs"] + p["arm"]["replication"]["runs"])
    assert sorted(p["x86"]["secondary"]["runs"]) == sorted(p["x86"]["earlier"]["runs"] + p["x86"]["replication"]["runs"])
    # one criteria file, unchanged, under which all six files were pooled
    assert results()["criteria"]["minimum_jobs"] == criteria()["v3"]["pooling"]["minimum_jobs"] == 3
    assert {pooled(rel)["criteria_sha256"] for files in (ARM, X86) for rel in files.values()} == {results()["criteria"]["pooled_under_sha256"]}


def test_the_plan_names_what_compare_py_types():
    plan = open(os.path.join(REPO, "replication", "PLAN.md"), encoding="utf-8").read()
    assert "6973P-C" in plan and "stencil at L2" in plan and "k02_add_fwd" in plan and "Neoverse-N2" in plan
    assert cmp.PLAN_MODEL_X86.split()[-1] in plan
    assert "Pooled forms (A and B for Arm; the 95 jobs and C for x86-64)" in plan and "secondary" in plan
    assert "A job that fails or is cancelled is listed and not replaced" in plan


# ---------------------------------------------------------------- plan question 1: the Arm cell

def test_arm_set_b_is_inconclusive_again_on_the_same_cell():
    q = results()["questions"]["arm_cell"]
    assert q["model"] == N2
    assert (q["earlier_form"], q["replication_form"], q["secondary_form"]) == ("inconclusive", "inconclusive", "map")
    assert q["decides_earlier"] == ["k02_add_fwd.L2"] and q["replication_names_the_same_cells"] and q["repeated"] is True
    assert q["upper_end_above_limit"] == {"earlier": [True], "replication": [True], "secondary": [False]}
    a, b = row("arm", N2)["earlier"], row("arm", N2)["replication"]
    assert (a["jobs"], b["jobs"]) == (30, 29), "set B: 29 Neoverse-N2 jobs (the 30th drew a Neoverse-V3 core)"
    assert a["cause"]["kind"] == b["cause"]["kind"] == "mixed"
    assert [x["cell_id"] for x in a["cause"]["forward_missed"]] == [x["cell_id"] for x in b["cause"]["forward_missed"]] == ["k02_add_fwd.L2"]
    assert a["cause"]["lost_missed"] == b["cause"]["lost_missed"] == []
    # the cell, from the pooled files themselves: set A, set B, A and B together (limit 1.02)
    for rel, (ratio, lo, hi), jobs in ((ARM["earlier"], ("0.9859", "0.9657", "1.0211"), 30),
                                       (ARM["replication"], ("0.9953", "0.9752", "1.0247"), 29),
                                       (ARM["secondary"], ("0.9905", "0.9771", "1.0150"), 59)):
        c = pcell(rel, N2, "k02_add_fwd.L2")
        assert (f4(c["aligned"]["ratio"]), f4(c["aligned"]["ci95"][0]), f4(c["aligned"]["ci95"][1])) == (ratio, lo, hi), rel
        assert blk(rel, N2)["jobs"] == jobs
        assert blk(rel, N2)["verdict"]["forward_limit_pct"] == 2.0
    named = next(c for c in results()["arm"]["named_cells"] if c["cell_id"] == "k02_add_fwd.L2")
    assert named["decides_earlier_verdict"] is True
    for role, hi in (("earlier", "1.0211"), ("replication", "1.0247"), ("secondary", "1.0150")):
        assert f4(named[role]["aligned"]["ci95"][1]) == hi and named[role]["role"] == "judged_forward"
        assert named[role]["passes_forward_rule"] is (role == "secondary")


def test_arm_matrix_multiply_and_the_a_a_repeat_to_three_decimals():
    named = {c["cell_id"]: c for c in results()["arm"]["named_cells"]}
    assert list(named) == ["k02_add_fwd.L2", "k08_matmul.L1", "k08_matmul.L2"]
    for role in ("earlier", "replication", "secondary"):
        assert f3(named["k08_matmul.L1"][role]["as_compiled"]["ratio"]) == "1.548"
        assert f3(named["k08_matmul.L2"][role]["as_compiled"]["ratio"]) == "1.016"
    r = row("arm", N2)
    assert f3(r["earlier"]["aa_half_width_pct"]) == f3(r["replication"]["aa_half_width_pct"]) == "0.009"


def test_arm_points_inside_the_earlier_interval():
    r = row("arm", N2)
    checked, inside = inside_by_hand(blk(ARM["replication"], N2), blk(ARM["earlier"], N2))
    assert (checked, inside) == (32, 26)
    assert (r["inside"]["checked"], r["inside"]["inside"], r["inside"]["outside"]) == (32, 26, 6)
    assert results()["arm"]["totals"]["points_checked"] == 32 and results()["arm"]["totals"]["points_inside"] == 26
    misses = {(m["cell_id"], m["column"]): m for m in r["inside"]["misses"]}
    assert len(misses) == 6
    stride = misses[("k05_stride2.L2", "aligned")]
    old = pcell(ARM["earlier"], N2, "k05_stride2.L2")["aligned"]["ratio"]
    new = pcell(ARM["replication"], N2, "k05_stride2.L2")["aligned"]["ratio"]
    assert (f2(old), f2(new)) == ("4.91", "4.73"), "stride-2 at L2, aligned: the earlier point and the new one"
    assert stride["new"] == new
    # the other five miss the earlier interval by less than 0.1 % of the point (their points differ by at most 0.3 %)
    others = [m for k, m in misses.items() if k != ("k05_stride2.L2", "aligned")]
    assert len(others) == 5 and max(m["gap_pct"] for m in others) < 0.1 and max(abs(m["point_diff_pct"]) for m in others) < 0.3
    assert stride["gap_pct"] > 0.5 and abs(stride["point_diff_pct"]) > 3.0
    assert r["inside"]["max_gap_pct"] == stride["gap_pct"]


def test_arm_secondary_pool_is_map_while_each_run_alone_is_inconclusive():
    r = row("arm", N2)["secondary"]
    assert (r["jobs"], r["runs"], r["form"]) == (59, 6, "map")
    assert [x["form"] for x in r["per_run"]] == ["inconclusive"] * 6 and len(r["per_run"]) == 6
    assert r["stability"] == "unstable"
    assert row("arm", V3)["testable"] is False and row("arm", V3)["earlier"] is None
    assert [n["cpu_model"] for n in results()["arm"]["not_testable"]] == [V3]


# ---------------------------------------------------------------- the x86-64 comparison, model by model

X86_TABLE = {
    # model: (first pool jobs, form), (set C jobs, form, runs), (first pool and C: jobs, form), points inside of 32
    EPYC7763: ((29, "map"), (19, "map", 4), (48, "map"), 22),
    EPYC9V45: ((23, "map"), (5, "inconclusive", 2), (28, "map"), 27),
    EPYC9V74: ((28, "map"), (7, "map", 3), (35, "map"), 25),
    XEON8573C: ((7, "inconclusive"), (7, "map", 4), (14, "inconclusive"), 27),
    XEON6973PC: ((7, "map"), (1, "inconclusive", 1), (8, "inconclusive"), None),
    XEON8370C: ((1, "inconclusive"), (1, "inconclusive", 1), (2, "inconclusive"), None),
}


def test_x86_verdict_words_and_job_counts_per_model():
    assert sorted(r["cpu_model"] for r in results()["x86"]["models"]) == sorted(X86_TABLE)
    for model, ((ej, ef), (rj, rf, rr), (sj, sf), _) in X86_TABLE.items():
        r = row("x86", model)
        assert (r["earlier"]["jobs"], r["earlier"]["form"]) == (ej, ef), model
        assert (r["replication"]["jobs"], r["replication"]["form"], r["replication"]["runs"]) == (rj, rf, rr), model
        assert (r["secondary"]["jobs"], r["secondary"]["form"]) == (sj, sf), model
        # and the pooled files say the same
        assert (blk(X86["earlier"], model)["jobs"], blk(X86["earlier"], model)["verdict"]["form"]) == (ej, ef)
        assert (blk(X86["replication"], model)["jobs"], blk(X86["replication"], model)["verdict"]["form"]) == (rj, rf)
        assert (blk(X86["secondary"], model)["jobs"], blk(X86["secondary"], model)["verdict"]["form"]) == (sj, sf)
        assert r["earlier"]["enough"] == (ej >= 3) and r["replication"]["enough"] == (rj >= 3)


def test_x86_testable_models_same_word_and_flipped():
    t = results()["x86"]["totals"]
    assert (t["testable_models"], t["same_form"], t["flipped"]) == (4, 2, 2)
    same_forms = sorted(r["cpu_model"] for r in results()["x86"]["models"] if r["same_form"] is True)
    flipped = sorted(r["cpu_model"] for r in results()["x86"]["models"] if r["same_form"] is False)
    assert same_forms == sorted([EPYC7763, EPYC9V74]) and flipped == sorted([EPYC9V45, XEON8573C])
    assert [r["cpu_model"] for r in results()["x86"]["models"] if r["testable"]] == sorted([EPYC7763, EPYC9V45, EPYC9V74, XEON8573C])
    nt = results()["x86"]["not_testable"]
    assert sorted(n["cpu_model"] for n in nt) == sorted([XEON6973PC, XEON8370C]) and all(n["minimum_jobs"] == 3 for n in nt)
    assert {n["cpu_model"]: (n["earlier_jobs"], n["replication_jobs"]) for n in nt} == {XEON6973PC: (7, 1), XEON8370C: (1, 1)}


def test_x86_points_inside_the_earlier_interval():
    total_checked = total_inside = 0
    for model, (_, _, _, inside) in X86_TABLE.items():
        r = row("x86", model)
        if inside is None:
            assert r["inside"] is None and r["testable"] is False
            continue
        checked, ins = inside_by_hand(blk(X86["replication"], model), blk(X86["earlier"], model))
        assert (checked, ins) == (32, inside), model
        assert (r["inside"]["checked"], r["inside"]["inside"]) == (32, inside)
        assert len(r["inside"]["points"]) == 32 and sum(1 for p in r["inside"]["points"] if p["inside"]) == inside
        total_checked += checked
        total_inside += ins
    t = results()["x86"]["totals"]
    assert (total_checked, total_inside) == (128, 101) == (t["points_checked"], t["points_inside"])
    assert t["points_outside"] == 27


def test_x86_most_differences_between_the_points_are_under_one_percent():
    t = results()["x86"]["totals"]
    pts = [p for r in results()["x86"]["models"] if r["inside"] for p in r["inside"]["points"]]
    under = sum(1 for p in pts if abs(p["point_diff_pct"]) < 1.0)
    assert under == t["point_diff_under_1pct"] and under > len(pts) // 2 and len(pts) == 128
    big = sorted(pts, key=lambda p: -abs(p["point_diff_pct"]))[:2]
    assert [(p["cell_id"], p["column"], f1(p["point_diff_pct"])) for p in big] == [
        ("k05_stride2.L2", "as_compiled", "2.1"), ("k02_add_fwd.L2", "as_compiled", "-1.9")]
    r = row("x86", XEON8573C)
    assert [(d["cell_id"], d["column"]) for d in r["inside"]["largest_point_diffs"][:2]] == [
        ("k05_stride2.L2", "as_compiled"), ("k02_add_fwd.L2", "as_compiled")]
    assert f2(t["max_abs_point_diff_pct"]) == "2.14"


# ---------------------------------------------------------------- the two knife-edge flips

def test_xeon_8573c_flips_on_the_forward_add_at_l1_and_the_written_rule_exempts_it_in_set_c():
    flip = next(f for f in results()["x86"]["flips"] if f["cpu_model"] == XEON8573C)
    assert (flip["earlier_form"], flip["replication_form"]) == ("inconclusive", "map")
    assert [c["cell_id"] for c in flip["cells"]] == ["k02_add_fwd.L1"]
    c = flip["cells"][0]
    e, n, s = c["earlier"], c["replication"], c["secondary"]
    assert (e["jobs"], n["jobs"], s["jobs"]) == (7, 7, 14)
    # the same cost in both pools
    assert (f3(e["aligned"]["ratio"]), f4(e["aligned"]["ci95"][0]), f4(e["aligned"]["ci95"][1])) == ("1.058", "1.0532", "1.0635")
    assert (f3(n["aligned"]["ratio"]), f3(n["aligned"]["ci95"][0]), f4(n["aligned"]["ci95"][1])) == ("1.060", "1.057", "1.0633")
    assert (f3(e["as_compiled"]["ratio"]), f3(n["as_compiled"]["ratio"])) == ("1.057", "1.054")
    # the written rule judged it in the first pool and exempted it as placement-sensitive in set C
    assert (e["role"], n["role"], s["role"]) == ("judged_forward", "exempt_placement_sensitive", "judged_forward")
    assert (e["passes_forward_rule"], n["passes_forward_rule"], s["passes_forward_rule"]) == (False, None, False)
    assert (e["form"], n["form"], s["form"]) == ("inconclusive", "map", "inconclusive")
    assert (f4(e["placement"]["d_ci95"][0]), f4(e["placement"]["d_ci95"][1])) == ("0.9907", "1.0059")
    assert (f4(n["placement"]["d_ci95"][0]), f4(n["placement"]["d_ci95"][1])) == ("0.9900", "0.9996")
    assert (e["placement"]["statistical"], n["placement"]["statistical"]) == (False, True)
    assert e["placement"]["mechanical"] and n["placement"]["mechanical"], "the hot loops sit differently against 64-byte windows in both"
    assert (e["placement"]["sensitive"], n["placement"]["sensitive"]) == (False, True)
    assert f4(n["placement"]["d_misses_one_by"]) == "0.0004" and e["placement"]["d_misses_one_by"] == 0.0
    assert n["aligned_hi_over_limit"] > 0.04, "over the limit by 4 points either way: exempt, not under"
    # the pooled files agree
    assert [p["cell_id"] for p in blk(X86["replication"], XEON8573C)["verdict"]["placement_sensitive"]] == [
        "k02_add_fwd.L1", "k02_add_fwd.L2", "k03_stencil.L1"]
    assert [p["cell_id"] for p in blk(X86["earlier"], XEON8573C)["verdict"]["placement_sensitive"]] == ["k02_add_fwd.L2"]
    assert blk(X86["secondary"], XEON8573C)["jobs"] == 14 and row("x86", XEON8573C)["secondary"]["cause"]["forward_missed"][0]["cell_id"] == "k02_add_fwd.L1"


def test_epyc_9v45_flips_on_the_stencil_at_l1_at_the_same_number():
    flip = next(f for f in results()["x86"]["flips"] if f["cpu_model"] == EPYC9V45)
    assert (flip["earlier_form"], flip["replication_form"]) == ("map", "inconclusive")
    assert [c["cell_id"] for c in flip["cells"]] == ["k03_stencil.L1"]
    c = flip["cells"][0]
    e, n, s = c["earlier"], c["replication"], c["secondary"]
    assert (e["jobs"], n["jobs"], s["jobs"]) == (23, 5, 28)
    assert (f4(e["aligned"]["ci95"][1]), f4(n["aligned"]["ci95"][1])) == ("1.0204", "1.0202")
    assert e["limit"] == n["limit"] == 1.02
    assert (e["role"], n["role"]) == ("exempt_placement_sensitive", "judged_forward")
    assert (e["passes_forward_rule"], n["passes_forward_rule"]) == (None, False)
    assert (e["placement"]["statistical"], n["placement"]["statistical"]) == (True, False)
    assert e["placement"]["mechanical"] and n["placement"]["mechanical"]
    assert (e["form"], n["form"], s["form"]) == ("map", "inconclusive", "map")
    cause = row("x86", EPYC9V45)["replication"]["cause"]
    assert [x["cell_id"] for x in cause["forward_missed"]] == ["k03_stencil.L1"] and cause["lost_missed"] == []
    assert 0 < cause["forward_missed"][0]["aligned_hi_over_limit"] < 0.001


def test_a_flip_names_only_cells_that_cause_the_non_map_side():
    for f in results()["x86"]["flips"] + results()["arm"]["flips"]:
        r = row("x86", f["cpu_model"])
        want = []
        for role in ("earlier", "replication"):
            want += [x["cell_id"] for x in ((r[role]["cause"] or {}).get("forward_missed", []))]
        assert sorted(c["cell_id"] for c in f["cells"]) == sorted(set(want))
    assert results()["arm"]["flips"] == []


# ---------------------------------------------------------------- plan question 2: the Xeon 6973P-C

def test_xeon_6973pc_cannot_be_tested_and_the_secondary_pool_misses_the_forward_rule():
    q = results()["questions"]["xeon_6973pc"]
    assert (q["earlier_form"], q["earlier_jobs"], q["replication_jobs"], q["minimum_jobs"], q["testable"]) == ("map", 7, 1, 3, False)
    cf = q["earlier_closest_forward"]
    assert cf["cell_id"] == "k03_stencil.L2" and f4(cf["aligned_hi"]) == "1.0184" and cf["limit"] == 1.02
    assert (q["secondary_jobs"], q["secondary_form"]) == (8, "inconclusive")
    assert [x["cell_id"] for x in q["secondary_cause"]["forward_missed"]] == ["k03_stencil.L1"]
    assert f4(q["secondary_cause"]["forward_missed"][0]["aligned_ci95"][1]) == "1.0216"
    # from the pooled files
    assert blk(X86["replication"], XEON6973PC)["jobs"] == 1 < criteria()["v3"]["pooling"]["minimum_jobs"]
    assert blk(X86["replication"], XEON6973PC)["verdict"]["why"].startswith("too few jobs")
    assert f4(pcell(X86["earlier"], XEON6973PC, "k03_stencil.L2")["aligned"]["ci95"][1]) == "1.0184"
    assert row("x86", XEON6973PC)["inside"] is None and row("x86", XEON6973PC)["same_form"] is None


def test_single_job_models_have_no_closest_cell_and_decide_nothing():
    for arch in ("x86", "arm"):
        for r in results()[arch]["models"]:
            for role in ("earlier", "replication", "secondary"):
                rec = r[role]
                if rec and rec["jobs"] < 3:
                    assert rec["enough"] is False and rec["closest_forward"] is None and rec["form"] == "inconclusive"
                    assert rec["cause"]["kind"] == "too_few_jobs"
                    assert r["testable"] is False or role == "secondary"


# ---------------------------------------------------------------- the headline range against set C

def test_headline_range_is_the_one_the_page_prints_and_no_cell_of_set_c_is_outside_it():
    h = results()["x86"]["headline"]
    ix = read("site", "data", "index.json")
    assert h["page_range"]["min"] == ix["page"]["lost"]["min"] and h["page_range"]["max"] == ix["page"]["lost"]["max"]
    assert (h["page_range"]["printed_min"], h["page_range"]["printed_max"]) == ("2.8", "8.0") == (f1(ix["page"]["lost"]["min"]), f1(ix["page"]["lost"]["max"]))
    assert sorted(h["page_range"]["models"]) == sorted(ix["page"]["judged_cpus"] and [c["cpu_model"] for c in ix["cpus"] if c["cpu_short"] in ix["page"]["judged_cpus"]])
    assert h["outside_printed_range"] == [] and h["outside_printed_range_enough_jobs"] == 0
    # the models of set C with at least 3 jobs whose verdict reached a form
    assert (f2(h["replication_judged_range"]["min"]), f2(h["replication_judged_range"]["max"])) == ("3.12", "7.99")
    by = {r["cpu_model"]: r for r in h["replication"]}
    assert (f2(by[XEON8573C]["range"]["min"]), f2(by[XEON8573C]["range"]["max"])) == ("3.12", "6.60")
    assert (f2(by[EPYC7763]["aligned_range"]["min"]), f2(by[EPYC7763]["aligned_range"]["max"])) == ("3.18", "7.99")
    assert (f2(by[EPYC9V74]["aligned_range"]["min"]), f2(by[EPYC9V74]["aligned_range"]["max"])) == ("4.05", "5.81")
    # 9V45 (5 jobs, inconclusive in set C): in the range too; its lowest cell is the one that sits just under the stored minimum
    assert (f3(by[EPYC9V45]["range"]["min"]), f3(by[EPYC9V45]["range"]["max"])) == ("2.805", "5.817")
    assert by[EPYC9V45]["judged"] is False and by[EPYC9V45]["enough"] is True
    assert (f3(h["replication_enough_range"]["min"]), f3(h["replication_enough_range"]["max"])) == ("2.805", "7.993")
    assert len(h["outside_stored_range"]) == 1
    o = h["outside_stored_range"][0]
    assert (o["cpu_model"], o["cell_id"], o["column"], o["enough"]) == (EPYC9V45, "k05_stride2.L1", "as_compiled", True)
    assert f4(o["ratio"]) == "2.8053" and f4(h["page_range"]["min"]) == "2.8055" and f1(o["ratio"]) == "2.8"
    # every number above, from the pooled files
    lost = [c[col]["ratio"] for rel in (X86["replication"],) for b in pooled(rel)["cpus"] if b["jobs"] >= 3
            for c in b["cells"] if c["class"] == "lost" and c["size_class"] in IN_CACHE for col in ("as_compiled", "aligned")]
    assert min(lost) == h["replication_enough_range"]["min"] and max(lost) == h["replication_enough_range"]["max"]
    assert 2.75 <= min(lost) and max(lost) < 8.05


# ---------------------------------------------------------------- the pooled check and the two red combine runs

def test_the_two_red_combine_runs_pass_the_independent_check_now():
    """Runs 39012986182 and 39013000285 of set C ended red: harness/pool_check.py disagreed with a model of fewer than 3 jobs.
    Run 39012986182: Xeon 6973P-C, k08_matmul.L1 as compiled, 1 job, by 0.0406 against a tolerance of 0.0347. Run 39013000285:
    EPYC 9V74, k03_stencil.L1 as compiled, 2 jobs (lower end 0.97845 independent against 0.98195 stored, tolerance 0.00331).
    A model under the minimum number of jobs is no longer sampled; the same pooled files pass."""
    for run in ("39012986182", "39013000285"):
        rel = f"results/s9-run-{run}/pooled.json"
        small = [b["cpu_model"] for b in pooled(rel)["cpus"] if b["jobs"] < 3]
        assert small, "this run drew no model with fewer than 3 jobs"
        skipped, buf = [], io.StringIO()
        with contextlib.redirect_stdout(buf):
            n, problems = pool_check.check(os.path.join(REPO, *rel.split("/")), skipped)
        assert problems == [] and n > 0, (rel, problems)
        assert sorted(skipped) == sorted(small)
    one_job = blk("results/s9-run-39012986182/pooled.json", XEON6973PC)
    assert one_job["jobs"] == 1 and cell(one_job, "k08_matmul.L1")["as_compiled"]["jobs"] == 1
    two_jobs = blk("results/s9-run-39013000285/pooled.json", "AMD EPYC 9V74 80-Core Processor")
    assert two_jobs["jobs"] == 2 and cell(two_jobs, "k03_stencil.L1")["as_compiled"]["jobs"] == 2


# ---------------------------------------------------------------- scripts/check.py goes through the new folders

def check_module():
    return _load("replication_test_check", os.path.join("scripts", "check.py"))


def complete(base):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        ok = check_module().check_pool_complete(base)
    return ok, out.getvalue()


POOL_DIRS = ("s4-pooled", "s6-pooled", "s7-pooled", "s8-arm-pooled", "s9-arm-b-pooled", "s9-x86-c-pooled", "s9-arm-ab-pooled", "s9-x86-ac-pooled")


def scratch(tmp):
    """The eight pool listings, with an empty results.json for every job they name: check_pool_complete() reads listings and names only."""
    base = os.path.join(tmp, "results")
    for d in POOL_DIRS:
        os.makedirs(os.path.join(base, d))
        shutil.copyfile(os.path.join(REPO, "results", d, "pooled.json"), os.path.join(base, d, "pooled.json"))
    for d in POOL_DIRS:
        for i in pooled(f"results/{d}/pooled.json")["inputs"]:
            job = os.path.normpath(os.path.join(base, d, i["path"]))
            os.makedirs(os.path.dirname(job), exist_ok=True)
            open(job, "w").close()
    return base


def edit(base, pool_dir, fn):
    path = os.path.join(base, pool_dir, "pooled.json")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    fn(doc)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f)


def test_check_py_pool_completeness_covers_the_four_new_pools():
    ok, out = complete(os.path.join(REPO, "results"))
    assert ok, out
    for line in ("results/s9-arm-b-pooled/pooled.json pools all 30 jobs of the s9-arm-run folders once each",
                 "results/s9-x86-c-pooled/pooled.json pools all 40 jobs of the s9-run folders once each",
                 "results/s9-arm-ab-pooled/pooled.json pools all 60 jobs of the s8-arm-run and s9-arm-run folders once each, "
                 "including the 30 of results/s8-arm-pooled and the 30 of results/s9-arm-b-pooled",
                 "results/s9-x86-ac-pooled/pooled.json pools all 135 jobs of the s4-run, s6-run, s7-run and s9-run folders once each, "
                 "including the 95 of results/s7-pooled and the 40 of results/s9-x86-c-pooled"):
        assert line in out, (line, out)
    with tempfile.TemporaryDirectory() as tmp:
        ok, out = complete(scratch(tmp))
        assert ok, out


def test_check_py_pool_completeness_fails_on_a_dropped_stray_or_double_job():
    with tempfile.TemporaryDirectory() as tmp:  # a job dropped from set B's listing
        base = scratch(tmp)
        edit(base, "s9-arm-b-pooled", lambda d: d["inputs"].pop())
        ok, out = complete(base)
        assert not ok and "results/s9-arm-b-pooled/pooled.json: " in out and "is on disk but not pooled" in out, out
    with tempfile.TemporaryDirectory() as tmp:  # an s8 job dropped from the A and B listing
        base = scratch(tmp)
        first = pooled("results/s9-arm-ab-pooled/pooled.json")["inputs"][0]["path"]
        edit(base, "s9-arm-ab-pooled", lambda d: d["inputs"].pop(0))
        ok, out = complete(base)
        assert not ok and "results/s9-arm-ab-pooled/pooled.json: " in out and "is on disk but not pooled" in out, out
        assert "is in the s8-arm pool but not in this one" in out.replace("\\", "/") or "is in the s9-arm-b pool but not in this one" in out, out
        assert os.path.basename(os.path.dirname(first)) in out.replace("\\", "/")
    with tempfile.TemporaryDirectory() as tmp:  # an s9 job dropped from the first-pool-plus-C listing
        base = scratch(tmp)
        edit(base, "s9-x86-ac-pooled", lambda d: d["inputs"].pop())
        ok, out = complete(base)
        assert not ok and "results/s9-x86-ac-pooled/pooled.json: " in out and "pool but not in this one" in out, out
    with tempfile.TemporaryDirectory() as tmp:  # a stray job folder in a set C run: set C and the combined pool both fail
        base = scratch(tmp)
        # an input path reads "../s9-run-<id>/results-<cpu>-jN/results.json": its second component is the run folder
        run_dir = pooled(X86["replication"])["inputs"][0]["path"].split("/")[1]
        assert run_dir.startswith("s9-run-")
        stray_dir = os.path.join(base, run_dir, "results-stray-j99")
        os.makedirs(stray_dir)
        open(os.path.join(stray_dir, "results.json"), "w").close()
        ok, out = complete(base)
        assert not ok and out.count("is on disk but not pooled") == 2, out
        assert "results/s9-x86-c-pooled/pooled.json: " in out and "results/s9-x86-ac-pooled/pooled.json: " in out, out
    with tempfile.TemporaryDirectory() as tmp:  # a job listed twice
        base = scratch(tmp)
        edit(base, "s9-x86-ac-pooled", lambda d: d["inputs"].append(dict(d["inputs"][0])))
        ok, out = complete(base)
        assert not ok and "a job is listed twice" in out, out


def test_check_py_runs_the_replication_and_d_sweep_steps():
    src = open(os.path.join(REPO, "scripts", "check.py"), encoding="utf-8").read()
    assert 'os.path.join(REPO, "replication", "compare.py"), "--verify"' in src
    assert "ok &= check_dsweep()" in src and '[sys.executable, analyze, "--verify"]' in src   # the d-sweep step (tests/test_dsweep_results.py covers it)
    chk = check_module()
    files = {os.path.relpath(p, REPO).replace("\\", "/") for p in chk.pooled_files()}
    for rel in list(ARM.values()) + list(X86.values()):
        assert rel in files, rel
    for d in glob.glob(os.path.join(REPO, "results", "s9-*run-*")):
        assert os.path.relpath(os.path.join(d, "pooled.json"), REPO).replace("\\", "/") in files
    jobs = {os.path.normpath(p) for p in chk.results_files()}
    for rel in (ARM["replication"], X86["replication"]):
        for i in pooled(rel)["inputs"]:
            assert os.path.normpath(os.path.join(REPO, "results", os.path.dirname(rel).split("/")[-1], i["path"])) in jobs


# ---------------------------------------------------------------- site/data/replication.json

def builder():
    return _load("replication_test_build", os.path.join("scripts", "build_site_data.py"))


def test_site_data_is_replication_data_and_equals_the_committed_file():
    mod = builder()
    fresh = json.loads(json.dumps(mod.replication_data(), sort_keys=True))
    assert fresh == site(), "site/data/replication.json differs from a fresh build; run python scripts/build_site_data.py"
    assert site()["source"] == "replication/results.json" and site()["plan"] == "replication/PLAN.md"
    assert site()["source_sha256"] == mod.sha(os.path.join(REPO, "replication", "results.json"))
    assert read("site", "data", "index.json")["sections"]["replication"] == "data/replication.json"


def test_site_data_rows_carry_the_numbers_of_results_json():
    s, r = site(), results()
    # rows: x86-64 then Arm; within an architecture the model with more jobs in the earlier pool first, then by name
    assert [(x["arch"], x["cpu_model"]) for x in s["rows"]] == [
        ("x86", EPYC7763), ("x86", EPYC9V74), ("x86", EPYC9V45), ("x86", XEON8573C), ("x86", XEON6973PC), ("x86", XEON8370C),
        ("arm", N2), ("arm", V3)]
    assert [x["cpu_short"] for x in s["rows"]] == ["EPYC 7763", "EPYC 9V74", "EPYC 9V45", "Xeon 8573C", "Xeon 6973P-C", "Xeon 8370C",
                                                  "Neoverse-N2", "Neoverse-V3"]
    for x in s["rows"]:
        src = row(x["arch"], x["cpu_model"])
        assert x["testable"] == src["testable"] and x["same_form"] == src["same_form"]
        assert x["status"] == ("not testable" if not src["testable"] else "same" if src["same_form"] else "flipped")
        for role in ("earlier", "replication", "secondary"):
            if src[role] is None:
                assert x[role] is None
                continue
            assert (x[role]["jobs"], x[role]["runs"], x[role]["form"]) == (src[role]["jobs"], src[role]["runs"], src[role]["form"])
            assert x[role]["closest_forward"] == src[role]["closest_forward"]
            assert "why" not in (x[role]["cause"] or {}), "the long stored sentence stays in results.json"
            assert (x[role]["cause"] or {}).get("forward_missed") == (src[role]["cause"] or {}).get("forward_missed")
            assert sum(x[role]["run_forms"].values()) == len(src[role]["per_run"])
        if src["inside"]:
            for k in ("checked", "inside", "outside", "max_gap_pct", "misses", "largest_point_diffs"):
                assert x["inside"][k] == src["inside"][k]
            assert "points" not in x["inside"]
        else:
            assert x["inside"] is None
    for arch in ("x86", "arm"):
        assert s["arch"][arch]["totals"] == r[arch]["totals"]
    assert s["arch"]["x86"]["headline"]["page_range"] == r["x86"]["headline"]["page_range"]
    assert s["arch"]["arm"]["named_cells"][0]["cell_id"] == "k02_add_fwd.L2" and s["arch"]["arm"]["model"]["slug"] == "neoverse-n2"
    assert s["questions"]["xeon_6973pc"]["slug"] == "xeon-6973p-c" and s["questions"]["arm_cell"] == r["questions"]["arm_cell"]
    assert len(json.dumps(s)) < 70_000, "the replication data file is no longer small"


def test_site_data_builder_refuses_a_changed_plan_or_criteria():
    mod = builder()
    saved = mod.REPLICATION_PLAN, mod.CRITERIA_FILE
    try:
        mod.REPLICATION_PLAN = "replication/compare.py"
        try:
            mod.replication_data()
            raise AssertionError("a plan with another hash was accepted")
        except AssertionError as e:
            assert "PLAN.md differs" in str(e), e
        mod.REPLICATION_PLAN = saved[0]
        mod.CRITERIA_FILE = "harness/criteria-v2.json"
        try:
            mod.replication_data()
            raise AssertionError("other criteria were accepted")
        except AssertionError as e:
            assert "other criteria" in str(e), e
    finally:
        mod.REPLICATION_PLAN, mod.CRITERIA_FILE = saved


BUILD = """
import importlib.util, sys
script, out, repl = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("build_site_data_copy", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if repl != "replication":
    mod.REPLICATION = "replication/does-not-exist.json"
mod.build(out)
"""


def build_into(out, with_replication):
    r = subprocess.run([sys.executable, "-I", "-c", BUILD, os.path.join(REPO, "scripts", "build_site_data.py"), out,
                        "replication" if with_replication else "none"], capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stderr[-2000:]


def tree(root):
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(dp, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root).replace("\\", "/")] = fh.read().replace(b"\r\n", b"\n")
    return out


def test_adding_the_replication_changes_no_other_file():
    with tempfile.TemporaryDirectory() as with_r, tempfile.TemporaryDirectory() as without:
        build_into(with_r, True)
        build_into(without, False)
        a, b = tree(with_r), tree(without)
        assert "replication.json" in a and "replication.json" not in b
        assert sorted(set(a) - set(b)) == ["replication.json"] and not set(b) - set(a)
        assert sorted(k for k in b if a[k] != b[k]) == ["index.json"], "other site files changed because of the replication"
        ia, ib = json.loads(a["index.json"]), json.loads(b["index.json"])
        assert ia["sections"].pop("replication") == "data/replication.json"
        assert ia == ib, "index.json differs by more than its sections.replication entry"
        committed = tree(os.path.join(REPO, "site", "data"))
        assert committed == a, f"site/data/ differs from a fresh build: {sorted(k for k in set(a) | set(committed) if a.get(k) != committed.get(k))[:5]}"


# ---------------------------------------------------------------- made-up pools: the logic of compare.py

def mkcell(cid, klass, al, ac=None, d=None, sensitive=False, mechanical=True):
    """al and ac are (ratio, lo, hi); d is (ratio, lo, hi) of the placement statistic."""
    ac = ac or al
    c = {"cell_id": cid, "kernel": cid.split(".")[0], "size_class": cid.split(".")[1], "class": klass,
         "as_compiled": {"ratio": ac[0], "ci95": [ac[1], ac[2]]}, "aligned": {"ratio": al[0], "ci95": [al[1], al[2]]}}
    if d:
        stat = d[1] > 1.0 or d[2] < 1.0
        c["placement"] = {"d": {"ratio": d[0], "ci95": [d[1], d[2]]}, "statistical": stat, "mechanical": mechanical, "sensitive": sensitive}
    return c


def around(x, w=0.004):
    return (x, x - w, x + w)


def clean_cells(scale=1.0):
    """Forward cells near 1.0 (kept), reverse and stride-2 far above (lost), no placement effect."""
    cells = []
    for s in ("L1", "L2", "RAM"):
        cells += [mkcell(f"k01_sum_fwd.{s}", "kept", around(1.0 * scale)), mkcell(f"k02_add_fwd.{s}", "kept", around(1.004 * scale)),
                  mkcell(f"k04_rev.{s}", "lost", around(5.0 * scale, 0.05)), mkcell(f"k05_stride2.{s}", "lost", around(3.0 * scale, 0.05))]
    return cells


def mkblock(cpu, jobs, form, cells, why=None, ps=(), limit_pct=2.0, runs=2):
    why = why or ("MAP: made up" if form == "map" else "too few jobs: fewer than minimum_jobs pooled")
    return {"cpu_model": cpu, "jobs": jobs, "runs": [f"r{i}" for i in range(runs)], "stability": "stable",
            "per_run": [{"run_id": f"r{i}", "jobs": max(1, jobs // runs), "form": form} for i in range(runs)],
            "cells": cells,
            "verdict": {"form": form, "why": why, "forward_limit_pct": limit_pct, "aa_half_width_pct": 0.3,
                        "placement_sensitive": [{"cell_id": i} for i in ps]}}


def mkdoc(*blocks):
    return {"cpus": list(blocks), "inputs": [], "runs": [], "criteria_sha256": "x", "resamples": 2000}


def put(cells, new):
    """`cells` with the cell of the same cell_id replaced by `new` (the list is changed in place and returned)."""
    i = next(i for i, c in enumerate(cells) if c["cell_id"] == new["cell_id"])
    cells[i] = new
    return cells


def test_inside_test_is_inclusive_and_uses_the_pool_py_gap():
    old = mkblock("A", 5, "map", [mkcell("k01_sum_fwd.L1", "kept", (0.995, 0.99, 1.01)), mkcell("k02_add_fwd.L1", "kept", (1.0, 0.99, 1.01)),
                                  mkcell("k01_sum_fwd.RAM", "kept", (1.0, 0.99, 1.01)), mkcell("k09_only_old.L1", "kept", (1.0, 0.99, 1.01))])
    new = mkblock("A", 5, "map", [mkcell("k01_sum_fwd.L1", "kept", (0.99, 0.9, 1.1), ac=(1.01, 0.9, 1.1)),     # on the low end / on the high end
                                  mkcell("k02_add_fwd.L1", "kept", (0.98, 0.9, 1.1), ac=(1.02, 0.9, 1.1)),    # both outside
                                  mkcell("k01_sum_fwd.RAM", "kept", (5.0, 0.9, 1.1)),                          # RAM: not counted
                                  mkcell("k10_only_new.L1", "kept", (5.0, 0.9, 1.1))])                         # not in the old pool: not counted
    pts = {(p["cell_id"], p["column"]): p for p in cmp.inside_points(new, old)}
    assert sorted(pts) == [("k01_sum_fwd.L1", "aligned"), ("k01_sum_fwd.L1", "as_compiled"),
                           ("k02_add_fwd.L1", "aligned"), ("k02_add_fwd.L1", "as_compiled")]
    assert pts[("k01_sum_fwd.L1", "aligned")]["inside"] and pts[("k01_sum_fwd.L1", "as_compiled")]["inside"]
    low, high = pts[("k02_add_fwd.L1", "aligned")], pts[("k02_add_fwd.L1", "as_compiled")]
    assert not low["inside"] and not high["inside"]
    assert abs(low["gap_pct"] - 100.0 * (0.99 - 0.98) / 0.98) < 1e-12      # below the interval: (lo - point) / point
    assert abs(high["gap_pct"] - 100.0 * (1.02 - 1.01) / 1.02) < 1e-12     # above it: (point - hi) / point
    assert abs(low["point_diff_pct"] - 100.0 * (0.98 / 1.0 - 1.0)) < 1e-12
    s = cmp.inside_summary(list(pts.values()))
    assert (s["checked"], s["inside"], s["outside"]) == (4, 2, 2) and len(s["misses"]) == 2
    # only the k01 point on the low end (0.99 against an earlier 0.995) differs by less than one percent
    assert s["max_gap_pct"] == max(low["gap_pct"], high["gap_pct"]) and s["point_diff_under_1pct"] == 1


def reproduction_shape(b, run_id):
    return {"run_id": run_id, "cells": {c["cell_id"]: {col: [c[col]["ratio"], c[col]["ci95"][0], c[col]["ci95"][1]]
                                                       for col in ("as_compiled", "aligned")}
                                        for c in b["cells"] if c["size_class"] in IN_CACHE}}


def test_inside_test_is_the_pool_py_reproduction_test():
    """harness/pool.py reproduction() compares every ordered pair of runs; the points of the new pool against the intervals
    of the earlier one are the half of that where the new pool is the point."""
    def same_as_pool(new, old):
        want = pool.reproduction([reproduction_shape(old, "earlier"), reproduction_shape(new, "new")])
        assert want["checked"] % 2 == 0
        half = [m for m in want["misses"] if m["point_run"] == "new"]
        pts = cmp.inside_points(new, old)
        assert len(pts) == want["checked"] // 2
        mine = sorted((p["cell_id"], p["column"], p["gap_pct"]) for p in pts if not p["inside"])
        theirs = sorted((m["cell_id"], m["column"], m["gap_pct"]) for m in half)
        assert len(mine) == len(theirs)
        for x, y in zip(mine, theirs):
            assert x[:2] == y[:2] and abs(x[2] - y[2]) <= 1e-12 * max(1.0, abs(y[2])), (x, y)
        return len(mine)
    old = mkblock("A", 5, "map", clean_cells())
    new = mkblock("A", 5, "map", clean_cells(1.005))
    n_out = same_as_pool(new, old)
    assert 0 < n_out < 16
    assert same_as_pool(old, old) == 0
    # and on the real Arm pools (set B against set A), where the share is 26 of 32
    assert same_as_pool(blk(ARM["replication"], N2), blk(ARM["earlier"], N2)) == 6
    assert same_as_pool(blk(X86["replication"], EPYC7763), blk(X86["earlier"], EPYC7763)) == 10


def test_cause_is_rebuilt_from_the_cells_and_must_equal_the_stored_sentence():
    crit = criteria()
    cells = clean_cells()
    put(cells, mkcell("k02_add_fwd.L2", "kept", (1.015, 1.002, 1.0211)))     # judged forward cell above the 1.02 limit
    put(cells, mkcell("k02_add_fwd.RAM", "kept", (1.5, 1.4, 1.6)))           # RAM: never judged
    # the cells above the limit are named in the order of the block: L1 (k04, k05), then L2 (k04, k05); each as compiled, then aligned
    above = ", ".join(f"{c}{lab}" for c in ("k04_rev.L1", "k05_stride2.L1", "k04_rev.L2", "k05_stride2.L2") for lab in ("", " (aligned)"))
    why = f"mixed picture: forward rule (aligned) missed by k02_add_fwd.L2; cells above the forward limit: {above}"
    b = mkblock("A", 10, "inconclusive", cells, why=why)
    cause = cmp.derive_cause(b, crit)
    assert cause["kind"] == "mixed" and cause["lost_missed"] == [] and cause["above_limit_cells"] == 8
    assert [x["cell_id"] for x in cause["forward_missed"]] == ["k02_add_fwd.L2"]
    assert abs(cause["forward_missed"][0]["aligned_hi_over_limit"] - (1.0211 - 1.02)) < 1e-12 and not cause["no_judged_forward_cell"]
    # a sentence that is not the one the cells give stops the build
    bad = copy.deepcopy(b)
    bad["verdict"]["why"] = why.replace("k02_add_fwd.L2", "k01_sum_fwd.L2", 1)
    try:
        cmp.derive_cause(bad, crit)
        raise AssertionError("a cause that does not rebuild the stored sentence was accepted")
    except ValueError as e:
        assert "not the stored why" in str(e)
    # a MAP has no cause; the other kinds are named from the start of the sentence
    assert cmp.derive_cause(mkblock("A", 10, "map", cells), crit) is None
    assert cmp.derive_cause(mkblock("A", 2, "inconclusive", cells), crit)["kind"] == "too_few_jobs"
    for text, kind in (("A/A control: pooled A/A half-width above aa_half_width_max_pct", "aa_noise"),
                       ("checksum control: a pooled job has a checksum mismatch", "checksum"),
                       ("build control: x", "build"), ("layout control: a designated layout A/A pair is missing", "layout"),
                       ("positive control: no pooled NOVEC/NONE ci95_lo above 1 + pooled A/A half-width", "positive_control"),
                       ("negative control: no kernel in the kept class", "negative_control"), ("something else", "other")):
        c = cmp.derive_cause(mkblock("A", 10, "inconclusive", cells, why=text), crit)
        assert c["kind"] == kind and c["why"] == text and "forward_missed" not in c


def test_a_placement_sensitive_cell_is_exempt_and_never_the_closest_cell():
    crit = criteria()
    cells = clean_cells()
    put(cells, mkcell("k02_add_fwd.L2", "kept", (1.05, 1.04, 1.06), d=(0.98, 0.97, 0.99), sensitive=True))
    b = mkblock("A", 10, "map", cells, ps=["k02_add_fwd.L2"])
    cf = cmp.closest_forward(b)
    assert cf["cell_id"] != "k02_add_fwd.L2"
    assert [c["cell_id"] for c in cmp.judged_forward(b)] == ["k01_sum_fwd.L1", "k02_add_fwd.L1", "k01_sum_fwd.L2"]
    rec = cmp.cell_record(b, "k02_add_fwd.L2", crit, 3)
    assert rec["role"] == "exempt_placement_sensitive" and rec["passes_forward_rule"] is None and rec["placement"]["sensitive"] is True
    assert abs(rec["placement"]["d_misses_one_by"] - 0.01) < 1e-12 and rec["placement"]["statistical"] is True
    judged = cmp.cell_record(b, "k01_sum_fwd.L1", crit, 3)
    assert judged["role"] == "judged_forward" and judged["passes_forward_rule"] is True and judged["placement"] is None
    assert cmp.cell_record(b, "k04_rev.L1", crit, 3)["role"] == "lost" and cmp.cell_record(b, "k04_rev.RAM", crit, 3)["role"] == "not_in_cache"
    assert cmp.cell_record(b, "k99_none.L1", crit, 3) is None and cmp.cell_record(None, "k01_sum_fwd.L1", crit, 3) is None


def test_closest_forward_is_the_smallest_margin_to_the_limit():
    cells = [mkcell("k01_sum_fwd.L1", "kept", (1.0, 0.99, 1.012)), mkcell("k02_add_fwd.L1", "kept", (1.0, 0.99, 1.018)),
             mkcell("k03_stencil.L1", "kept", (1.0, 0.99, 1.005)), mkcell("k04_rev.L1", "lost", (5.0, 4.9, 5.1))]
    cf = cmp.closest_forward(mkblock("A", 10, "map", cells))
    assert cf["cell_id"] == "k02_add_fwd.L1" and abs(cf["margin"] - (1.02 - 1.018)) < 1e-12
    over = cmp.closest_forward(mkblock("A", 10, "map", cells + [mkcell("k05_stride2.L2", "kept", (1.0, 0.99, 1.03))]))
    assert over["cell_id"] == "k05_stride2.L2" and over["margin"] < 0
    assert cmp.closest_forward(mkblock("A", 10, "map", [cells[3]])) is None
    wide = cmp.closest_forward(mkblock("A", 10, "map", cells, limit_pct=4.0))
    assert wide["limit"] == 1.04 and abs(wide["margin"] - (1.04 - 1.018)) < 1e-12


def test_the_minimum_number_of_jobs_decides_what_is_testable():
    crit = criteria()
    docs = {"earlier": mkdoc(mkblock("M3", 3, "map", clean_cells()), mkblock("M2", 5, "map", clean_cells()),
                             mkblock("M9", 9, "map", clean_cells()), mkblock("OLD", 8, "map", clean_cells())),
            "replication": mkdoc(mkblock("M3", 3, "map", clean_cells(1.001)), mkblock("M2", 2, "map", clean_cells()),
                                 mkblock("M9", 9, "inconclusive", clean_cells(),
                                         why="mixed picture: forward rule (aligned) missed by k01_sum_fwd.L1; cells above the forward limit: "
                                             "k04_rev.L1, k04_rev.L1 (aligned), k05_stride2.L1, k05_stride2.L1 (aligned), "
                                             "k04_rev.L2, k04_rev.L2 (aligned), k05_stride2.L2, k05_stride2.L2 (aligned)"),
                                 mkblock("NEW", 4, "map", clean_cells())),
            "secondary": mkdoc(mkblock("M3", 6, "map", clean_cells()), mkblock("M2", 7, "map", clean_cells()),
                               mkblock("M9", 18, "map", clean_cells()), mkblock("OLD", 8, "map", clean_cells()),
                               mkblock("NEW", 4, "map", clean_cells()))}
    # M9's mixed sentence names k01_sum_fwd.L1 as the miss: make that cell fail so the sentence rebuilds
    docs["replication"]["cpus"][2]["cells"][0] = mkcell("k01_sum_fwd.L1", "kept", (1.0, 0.99, 1.03))
    out = cmp.compare("x86", docs, crit, 3)
    rows = {r["cpu_model"]: r for r in out["models"]}
    assert sorted(rows) == ["M2", "M3", "M9", "NEW", "OLD"]
    assert [m for m, r in rows.items() if r["testable"]] == ["M3", "M9"], "exactly the minimum counts; one job fewer does not"
    assert rows["M3"]["same_form"] is True and rows["M9"]["same_form"] is False
    assert rows["M2"]["same_form"] is None and rows["M2"]["inside"] is None and rows["OLD"]["replication"] is None and rows["NEW"]["earlier"] is None
    t = out["totals"]
    assert (t["testable_models"], t["same_form"], t["flipped"]) == (2, 1, 1)
    assert t["points_checked"] == 32 == t["points_inside"] + t["points_outside"]
    assert [f["cpu_model"] for f in out["flips"]] == ["M9"] and [c["cell_id"] for c in out["flips"][0]["cells"]] == ["k01_sum_fwd.L1"]
    fc = out["flips"][0]["cells"][0]
    assert fc["earlier"]["role"] == "judged_forward" and fc["replication"]["passes_forward_rule"] is False and fc["secondary"]["form"] == "map"
    assert {n["cpu_model"]: (n["earlier_jobs"], n["replication_jobs"]) for n in out["not_testable"]} == {"M2": (5, 2), "NEW": (0, 4), "OLD": (8, 0)}
    assert next(n for n in out["not_testable"] if n["cpu_model"] == "M2")["secondary"]["form"] == "map"
    assert out["names"] == cmp.SET_NAMES["x86"]


def test_headline_range_reports_a_cell_whose_printed_form_is_outside_the_printed_range():
    def lost_block(cpu, jobs, form, lo, hi):
        cells = clean_cells()
        cells[2] = mkcell("k04_rev.L1", "lost", around(lo, 0.01))
        cells[3] = mkcell("k05_stride2.L1", "lost", around(hi, 0.01))
        return mkblock(cpu, jobs, form, cells)
    earlier = mkdoc(lost_block("A", 10, "map", 2.80, 8.00), lost_block("B", 10, "inconclusive", 1.0, 20.0), lost_block("C", 1, "map", 1.0, 30.0))
    replication = mkdoc(lost_block("A", 10, "map", 2.76, 8.04),     # prints 2.8 and 8.0: inside the printed range, outside the stored one
                        lost_block("B", 6, "map", 2.74, 8.06),      # prints 2.7 and 8.1: outside the printed range
                        lost_block("C", 2, "inconclusive", 1.0, 30.0))
    h = cmp.headline_block(earlier, replication, 3)
    assert (h["page_range"]["printed_min"], h["page_range"]["printed_max"]) == ("2.8", "8.0")
    assert h["page_range"]["models"] == ["A"], "the range is over the models that have enough jobs and a verdict that reached a form"
    got = sorted((x["cpu_model"], x["cell_id"], x["column"]) for x in h["outside_printed_range"])
    assert got == [("B", "k04_rev.L1", "aligned"), ("B", "k04_rev.L1", "as_compiled"), ("B", "k05_stride2.L1", "aligned"),
                   ("B", "k05_stride2.L1", "as_compiled"), ("C", "k04_rev.L1", "aligned"), ("C", "k04_rev.L1", "as_compiled"),
                   ("C", "k05_stride2.L1", "aligned"), ("C", "k05_stride2.L1", "as_compiled")]
    assert all(x["enough"] for x in h["outside_printed_range"] if x["cpu_model"] == "B")
    assert not any(x["enough"] for x in h["outside_printed_range"] if x["cpu_model"] == "C")
    assert h["outside_printed_range_enough_jobs"] == 4
    assert any(x["cpu_model"] == "A" and x["ratio"] > h["page_range"]["max"] for x in h["outside_stored_range"])
    assert not any(x["cpu_model"] == "A" for x in h["outside_printed_range"])
    assert h["replication_judged_range"]["min"] == 2.74 + 0.0 or abs(h["replication_judged_range"]["min"] - 2.74) < 0.011
    # without a judged model the range falls back to the models with enough jobs (build_site_data.py does the same)
    only_inconclusive = cmp.headline_block(mkdoc(lost_block("B", 10, "inconclusive", 3.0, 7.0)), replication, 3)
    assert only_inconclusive["page_range"]["models"] == ["B"] and only_inconclusive["page_range"]["printed_min"] == "3.0"


def test_verification_catches_a_change_in_any_leaf_of_the_stored_file():
    stored = cmp.build()
    assert cmp.same(stored, copy.deepcopy(stored)) == []

    def leaves(x, path=()):
        if isinstance(x, dict):
            for k, v in x.items():
                yield from leaves(v, path + (k,))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                yield from leaves(v, path + (i,))
        else:
            yield path, x

    def at(doc, path):
        for p in path[:-1]:
            doc = doc[p]
        return doc, path[-1]

    paths = [p for p, v in leaves(stored) if isinstance(v, float)]
    assert len(paths) > 1000
    # a one-part-in-a-million change in a float, a changed string, a changed bool, a dropped key and a changed length each show
    for p in paths[:: max(1, len(paths) // 40)]:
        t = copy.deepcopy(stored)
        d, k = at(t, p)
        d[k] = d[k] * (1 + 1e-6) if d[k] != 0 else 1e-6
        assert cmp.same(stored, t), p
    t = copy.deepcopy(stored)
    t["arm"]["models"][0]["earlier"]["form"] = "map"
    assert cmp.same(stored, t)
    t = copy.deepcopy(stored)
    t["arm"]["models"][0]["testable"] = not t["arm"]["models"][0]["testable"]
    assert cmp.same(stored, t)
    t = copy.deepcopy(stored)
    del t["x86"]["totals"]["points_inside"]
    assert cmp.same(stored, t)
    t = copy.deepcopy(stored)
    t["x86"]["models"].pop()
    assert cmp.same(stored, t)
    t = copy.deepcopy(stored)
    t["x86"]["models"][0]["testable"] = int(t["x86"]["models"][0]["testable"])          # True and 1 are not the same stored value
    assert cmp.same(stored, t)


def test_verify_file_reports_a_missing_or_changed_file_and_accepts_the_stored_one():
    doc = cmp.build()
    assert cmp.verify_file(os.path.join(REPO, "replication", "results.json"), doc) == []
    with tempfile.TemporaryDirectory() as tmp:
        assert cmp.verify_file(os.path.join(tmp, "nope.json"), doc) and "missing" in cmp.verify_file(os.path.join(tmp, "nope.json"), doc)[0]
        t = copy.deepcopy(doc)
        t["x86"]["totals"]["points_inside"] += 1
        p = os.path.join(tmp, "results.json")
        with open(p, "w", encoding="utf-8") as f:
            f.write(cmp.dumps(t))
        diffs = cmp.verify_file(p, doc)
        assert diffs and "points_inside" in diffs[0]


def test_compare_py_runs_as_a_command_and_verifies():
    r = subprocess.run([sys.executable, "-I", os.path.join(REPO, "replication", "compare.py"), "--verify"], capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "equals a recomputation from the six pooled files" in r.stdout and "26 of 32" in r.stdout and "101 of 128" in r.stdout
    r = subprocess.run([sys.executable, "-I", os.path.join(REPO, "replication", "compare.py"), "--bogus"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 2
