"""harness/verdict.py under harness/criteria-v2.json: the loops-aligned column, the placement-sensitive
label, the layout A/A and the build controls, on made-up cells. The v1 rules are tested in test_verdict.py."""
import copy
import json
import os

import verdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = verdict.load_criteria(os.path.join(REPO, "harness", "criteria-v2.json"))
V1 = verdict.load_criteria(os.path.join(REPO, "harness", "criteria.json"))
KEPT = ("k02_add_fwd", "k03_stencil")
LOST = ("k04_rev", "k05_stride2")


def cell(kernel, size, ratio, lo, hi, vec_none=True, vec_fast=True, aligned=None):
    a = aligned or (ratio, lo, hi)
    vn = {"vectorized": vec_none, "width": 4 if vec_none else None}
    vf = {"vectorized": vec_fast, "width": 4 if vec_fast else None}
    return {"cell_id": f"{kernel}.{size}", "kernel": kernel, "size_class": size,
            "vectorized_none": vn, "vectorized_fast": vf, "checksum_match": True, "ratio": ratio, "ci95": [lo, hi],
            "aligned": {"vectorized_none": dict(vn), "vectorized_fast": dict(vf), "checksum_match": True,
                        "ratio": a[0], "ci95": [a[1], a[2]]}}


def base(aa_hw=0.45, lay_hw=0.8, cpu="AMD EPYC 7763 64-Core Processor"):
    cells = []
    for k in KEPT:
        for s in ("L1", "L2"):
            cells.append(cell(k, s, 1.002, 0.99, 1.015))
        cells.append(cell(k, "RAM", 1.10, 1.05, 1.20))
    for k, r in zip(LOST, (5.5, 2.8)):
        for s in ("L1", "L2"):
            cells.append(cell(k, s, r, r - 0.05, r + 0.05, vec_fast=False, aligned=(r + 0.1, r + 0.05, r + 0.15)))
        cells.append(cell(k, "RAM", 1.2, 1.1, 1.3, vec_fast=False))
    cells.append(cell("k06_gather", "L1", 2.86, 2.84, 2.89, vec_none=False, vec_fast=False))
    return {"run": {"runner": {"cpu_model": cpu}, "criteria_file": "harness/criteria-v2.json"},
            "cells": cells,
            "controls": {"aa": {"half_width_pct": aa_hw},
                         "positive": [{"cell_id": "k02_add_fwd.L1", "novec_ratio": 2.5, "ci95": [2.4, 2.6]}],
                         "layout_aa": [{"id": "k02_add_fwd.L1", "half_width_pct": lay_hw},
                                       {"id": "k02_add_fwd.L2", "half_width_pct": lay_hw / 2},
                                       {"id": "k06_gather.L1", "half_width_pct": 9.0}]}}


def get(r, cid):
    return next(c for c in r["cells"] if c["cell_id"] == cid)


def test_dispatch_by_version():
    r = base()
    assert verdict.compute(r, V2)["criteria_version"] == 2
    assert "criteria_version" not in verdict.compute(r, V1)
    assert verdict.criteria_path(r) == "harness/criteria-v2.json"
    assert verdict.criteria_path({"run": {}}) == "harness/criteria.json"


def test_v2_file_keeps_every_v1_rule():
    for k in ("design", "classes_from_remarks", "verdict"):
        assert V2[k] == V1[k]
    assert V2["version"] == 2 and "changelog" in V2
    assert "after S1 and S2 results existed" in V2["changelog"][0]


def test_map_reads_the_aligned_column():
    v = verdict.compute(base(), V2)
    assert v["form"] == "map"
    assert v["n"] == {"median": (5.6 + 2.9) / 2, "min": 2.9, "max": 5.6}
    assert v["n_as_compiled"] == {"median": (5.5 + 2.8) / 2, "min": 2.8, "max": 5.5}
    assert v["line"].startswith("On AMD EPYC 7763 64-Core Processor: loops that lose SIMD under the check "
                                "(k04_rev, k05_stride2) cost 2.90 to 5.60 times as long in cache "
                                "(median 4.25; as compiled, median 4.15)")
    assert v["line"].endswith("judged forward loops (k02_add_fwd, k03_stencil) cost at most 1.5% more with loops aligned.")
    assert "Google" not in v["line"]
    assert v["layout_aa_half_width_pct"] == 0.8  # the designated pairs only, not k06's 9 %
    assert v["placement_sensitive"] == []
    assert abs(v["x_pct"] - 1.5) < 1e-9


def test_placement_sensitive_cell_is_listed_and_not_counted():
    # the investigation's k02 on EPYC 7763: as compiled 1.58, aligned 0.85
    r = base()
    c = get(r, "k02_add_fwd.L1")
    c["ratio"], c["ci95"] = 1.58, [1.55, 1.62]
    c["aligned"]["ratio"], c["aligned"]["ci95"] = 0.85, [0.84, 0.86]
    v = verdict.compute(r, V2)
    assert v["form"] == "map"
    assert [p["cell_id"] for p in v["placement_sensitive"]] == ["k02_add_fwd.L1"]
    assert "Placement-sensitive cells, listed separately and not judged: k02_add_fwd.L1 (as compiled 1.58, aligned 0.85)." in v["line"]
    assert verdict.compute(r, V1)["form"] == "inconclusive"  # the v1 rule on the as-compiled column misses


def test_gap_within_layout_half_width_is_not_placement_sensitive_and_aligned_rule_applies():
    r = base(lay_hw=0.8)
    c = get(r, "k03_stencil.L2")
    c["ratio"] = 1.002 + 0.0079  # 0.79 % apart: within the layout A/A half-width
    assert verdict.compute(r, V2)["placement_sensitive"] == []
    c["aligned"]["ratio"], c["aligned"]["ci95"] = 1.03, [1.02, 1.04]  # now 2.0 % apart: sensitive
    c["ratio"] = 1.01
    v = verdict.compute(r, V2)
    assert [p["cell_id"] for p in v["placement_sensitive"]] == ["k03_stencil.L2"]
    assert v["form"] == "map"


def test_forward_cell_that_pays_in_both_columns_breaks_map():
    r = base()
    c = get(r, "k03_stencil.L1")
    c["ratio"], c["ci95"] = 1.10, [1.08, 1.12]
    c["aligned"]["ratio"], c["aligned"]["ci95"] = 1.10, [1.08, 1.12]
    v = verdict.compute(r, V2)
    assert v["form"] == "inconclusive"
    assert "forward rule (aligned) missed by k03_stencil.L1" in v["why"]


def test_lost_minimum_needs_both_columns():
    r = base()
    get(r, "k05_stride2.L2")["aligned"]["ci95"] = [1.4, 1.7]
    v = verdict.compute(r, V2)
    assert v["form"] == "inconclusive"
    assert "lost-vectorization minimum missed by k05_stride2.L2 (aligned)" in v["why"]


def test_all_forward_cells_placement_sensitive_is_not_a_map():
    r = base()
    for k in KEPT:
        for s in ("L1", "L2"):
            get(r, f"{k}.{s}")["aligned"]["ratio"] = 0.9
    v = verdict.compute(r, V2)
    assert v["form"] == "inconclusive"
    assert "no forward cell left" in v["why"]


def test_aa_over_two_percent_is_inconclusive_for_that_cpu():
    v = verdict.compute(base(aa_hw=2.1, cpu="INTEL(R) XEON(R) PLATINUM 8573C"), V2)
    assert v["form"] == "inconclusive" and v["why"].startswith("A/A control")
    assert v["line"].startswith("On INTEL(R) XEON(R) PLATINUM 8573C: INCONCLUSIVE")


def test_missing_layout_aa_is_inconclusive():
    r = base()
    r["controls"]["layout_aa"] = [p for p in r["controls"]["layout_aa"] if not p["id"].startswith("k02")]
    v = verdict.compute(r, V2)
    assert v["form"] == "inconclusive" and v["why"].startswith("layout control")


def test_missing_aligned_pair_or_remark_drift_is_inconclusive():
    r = base()
    del get(r, "k04_rev.L1")["aligned"]
    assert verdict.compute(r, V2)["why"].startswith("build control: no aligned pair for k04_rev.L1")
    r = base()
    get(r, "k04_rev.L1")["aligned"]["vectorized_fast"]["vectorized"] = True
    assert "remarks differ for k04_rev.L1" in verdict.compute(r, V2)["why"]


def test_aligned_checksum_mismatch_is_inconclusive():
    r = base()
    get(r, "k04_rev.RAM")["aligned"]["checksum_match"] = False
    v = verdict.compute(r, V2)
    assert v["why"].startswith("checksum control") and "k04_rev.RAM (aligned)" in v["line"]


def test_off_axis_cell_pays_only_if_both_columns_show_it():
    r = base()
    v = verdict.compute(r, V2)
    assert v["off_axis"] == [{"cell_id": "k06_gather.L1", "ratio": 2.86, "aligned_ratio": 2.86,
                              "pays_in_both_columns": True}]
    get(r, "k06_gather.L1")["aligned"]["ci95"] = [0.99, 1.01]
    assert verdict.compute(r, V2)["off_axis"][0]["pays_in_both_columns"] is False


def test_holds_everywhere_in_either_column():
    r = base()
    for k in LOST:
        for s in ("L1", "L2"):
            c = get(r, f"{k}.{s}")
            c["ratio"], c["ci95"] = 1.005, [0.995, 1.012]
            c["aligned"]["ratio"], c["aligned"]["ci95"] = 1.004, [0.99, 1.018]
    v = verdict.compute(r, V2)
    assert v["form"] == "holds_everywhere" and v["n"] is None
    assert v["line"].endswith("no loop shape we tried paid more than 1.8% (as compiled or with loops aligned).")


def test_compute_v2_does_not_change_its_input():
    r = base()
    before = copy.deepcopy(r)
    verdict.compute(r, V2)
    assert r == before
    json.dumps(verdict.compute(r, V2))  # serializable
