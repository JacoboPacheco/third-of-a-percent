import contextlib
import io
import json
import os

import analyze as an
import run_version as rv

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_PATH = os.path.join(REPO, "results", "s4-pooled", "pooled.json")
CRIT = an.load_criteria()
HAVE_BASE = os.path.exists(BASE_PATH)


def base():
    with open(BASE_PATH, encoding="utf-8") as f:
        return json.load(f)


def block(jobs=5, aa=0.1, rev=7.0, stride=5.0, mat=3.0, cls_rev="lost", fwd=1.0):
    """A synthetic pooled CPU block with the 8 kernels at L1 and L2."""
    def pair(r, w=0.01):
        return {"ratio": r, "ci95": [r * (1 - w), r * (1 + w)], "half_width_pct": 100 * w, "jobs": jobs}
    cells = []
    spec = {"k01_sum_fwd": ("kept", fwd), "k02_add_fwd": ("kept", fwd), "k03_stencil": ("kept", fwd),
            "k04_rev": (cls_rev, rev), "k05_stride2": ("lost", stride), "k06_gather": ("off_axis", 1.5),
            "k07_hist": ("off_axis", 1.1), "k08_matmul": ("lost", mat)}
    for k, (cls, r) in spec.items():
        for s in ("L1", "L2"):
            cells.append({"cell_id": f"{k}.{s}", "kernel": k, "size_class": s, "class": cls,
                          "as_compiled": pair(r), "aligned": pair(r)})
    return {"cpu_model": "FAKE CPU", "jobs": jobs, "runs": ["1"], "aa": {"half_width_pct": aa},
            "verdict": {"form": "map", "why": "x"}, "cells": cells}


def one(b, probe=None):
    return an.judge_cpu(b, CRIT[0], an.numbers(CRIT[1]), probe)


def test_criteria_reference_matches_file_and_numbers():
    mine, v3, problems = CRIT
    assert problems == []
    n = an.numbers(v3)
    assert n["lost_lo"] == 1.5 and n["fwd_point"] == 1.02 and n["aa_max"] == 2.0 and n["min_jobs"] == 3
    assert mine["judged_kernels"] == ["k04_rev", "k05_stride2", "k08_matmul"]


def test_generalises_when_all_three_hold():
    r = one(block())
    assert r["form"] == "GENERALISES" and r["n_hold"] == 3


def test_does_not_generalise_is_a_form_with_equal_standing():
    b = block(rev=1.05, stride=1.04, mat=1.0, cls_rev="kept")
    for c in b["cells"]:
        if c["kernel"] in ("k05_stride2", "k08_matmul"):
            c["class"] = "kept"
    r = one(b)
    assert r["form"] == "DOES_NOT_GENERALISE" and r["n_hold"] == 0
    assert "not lost" in r["kernels"]["k04_rev"]["reason"]


def test_partial_names_the_kernel_that_does_not_hold():
    r = one(block(mat=1.2))  # still class lost but ci95_lo below 1.5
    assert r["form"] == "PARTIAL" and not r["kernels"]["k08_matmul"]["holds"]
    assert "below 1.5" in r["kernels"]["k08_matmul"]["reason"]


def test_one_column_below_threshold_is_enough_to_fail():
    b = block()
    cell = next(c for c in b["cells"] if c["cell_id"] == "k05_stride2.L2")
    cell["aligned"]["ci95"][0] = 1.49
    assert not one(b)["kernels"]["k05_stride2"]["holds"]


def test_inconclusive_rules():
    assert one(block(jobs=2))["form"] == "INCONCLUSIVE"
    assert one(block(aa=2.5))["form"] == "INCONCLUSIVE"
    b = block()
    b["verdict"]["form"] = "inconclusive"
    assert one(b)["form"] == "INCONCLUSIVE"
    assert one(block(), {"fast_traps": False, "none_runs_clean": True})["form"] == "INCONCLUSIVE"
    assert one(block(), {"fast_traps": True, "none_runs_clean": True})["form"] == "GENERALISES"


def test_forward_rule_is_descriptive_and_uses_aa_limit():
    r = one(block(fwd=1.0, aa=0.1))
    assert all(f["passes"] for f in r["forward"]) and len(r["forward"]) == 6
    r2 = one(block(fwd=1.5))
    assert not any(f["passes"] for f in r2["forward"]) and r2["form"] == "GENERALISES"
    assert abs(an.forward_limit(1.5, an.numbers(CRIT[1])) - 1.03) < 1e-12
    assert an.forward_limit(0.1, an.numbers(CRIT[1])) == 1.02


def test_toolchain_form():
    f = an.toolchain_form
    assert f({"a": "GENERALISES", "b": "INCONCLUSIVE"}) == "GENERALISES"
    assert f({"a": "GENERALISES", "b": "PARTIAL"}) == "MIXED_BY_CPU_MODEL"
    assert f({"a": "INCONCLUSIVE"}) == "INCONCLUSIVE" and f({}) == "INCONCLUSIVE"


def test_vs_baseline_ratio_and_report():
    b = block(rev=14.0)
    ref = block(rev=7.0)
    tc = {"20": {"clang": "clang version 20", "probe": {"fast_traps": True, "none_runs_clean": True}}}
    doc = an.analyse({"20": {"cpus": [b]}}, {"cpus": [ref]}, tc, CRIT)
    cpu = doc["versions"]["20"]["cpus"]["FAKE CPU"]
    assert abs(cpu["vs_clang18"]["k04_rev.L1"]["this_over_clang18"] - 2.0) < 1e-9
    text = an.report(doc)
    assert "clang/libc++ 20: GENERALISES" in text and "k04_rev: HOLDS" in text
    json.dumps(doc)


def test_unknown_cpu_has_no_baseline_but_is_judged():
    doc = an.analyse({"21": {"cpus": [block()]}}, {"cpus": []}, {}, CRIT)
    c = doc["versions"]["21"]["cpus"]["FAKE CPU"]
    assert c["vs_clang18"] == {} and c["in_clang18_pool"] is False and c["form"] == "GENERALISES"


def test_clang18_pool_judged_by_the_same_rules():
    if not HAVE_BASE:
        return
    b = base()
    doc = an.analyse({"18": b}, b, {}, CRIT)
    forms = {c: v["form"] for c, v in doc["versions"]["18"]["cpus"].items()}
    assert forms["AMD EPYC 7763 64-Core Processor"] == "GENERALISES"
    assert forms["INTEL(R) XEON(R) PLATINUM 8573C"] == "INCONCLUSIVE"  # one job


def test_probe_verdict():
    assert rv.probe_verdict(0, -4) == {"none_exit": 0, "fast_exit": -4, "none_runs_clean": True, "fast_traps": True}
    assert rv.probe_verdict(0, 0)["fast_traps"] is False
    assert rv.probe_verdict(None, None)["fast_traps"] is False


def test_vectorization_map_prefers_l1():
    res = {"cells": [
        {"kernel": "k", "size_class": "L2", "vectorized_none": {"vectorized": True, "width": 4},
         "vectorized_fast": {"vectorized": False}},
        {"kernel": "k", "size_class": "L1", "vectorized_none": {"vectorized": True, "width": 2},
         "vectorized_fast": {"vectorized": False}}]}
    m = rv.vectorization_map(res)
    assert m["k"]["none"]["width"] == 2 and m["k"]["fast"]["vectorized"] is False


def test_dry_run_uses_harness_unchanged():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert rv.main(["--version", "20", "--dry-run", "--out", os.path.join(REPO, "build", "versions-test")]) == 0
    s = buf.getvalue()
    assert "HARNESS_CXX=clang++-20" in s and "harness/run.py" in s and "criteria-v3.json" in s
    assert "--programs none" in s
