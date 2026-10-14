"""harness/verdict.py: all three forms and every INCONCLUSIVE reason, on made-up cells."""
import copy

import verdict

KEPT = ("k02_add_fwd", "k03_stencil")
LOST = ("k04_rev", "k05_stride2")


def cell(kernel, size, ratio, lo, hi, vec_none=True, vec_fast=True, ck=True):
    return {"cell_id": f"{kernel}.{size}", "kernel": kernel, "size_class": size,
            "vectorized_none": {"vectorized": vec_none, "width": 4 if vec_none else None},
            "vectorized_fast": {"vectorized": vec_fast, "width": 4 if vec_fast else None},
            "checksum_match": ck, "ratio": ratio, "ci95": [lo, hi]}


def base(aa_hw=0.45):
    cells = []
    for k in KEPT:
        for s in ("L1", "L2"):
            cells.append(cell(k, s, 1.002, 0.99, 1.015))
        cells.append(cell(k, "RAM", 1.10, 1.05, 1.20))  # RAM never counts
    for k, r in zip(LOST, (5.5, 2.8)):
        for s in ("L1", "L2"):
            cells.append(cell(k, s, r, r - 0.05, r + 0.05, vec_fast=False))
        cells.append(cell(k, "RAM", 1.2, 1.1, 1.3, vec_fast=False))
    cells.append(cell("k06_gather", "L1", 1.4, 1.3, 1.5, vec_none=False, vec_fast=False))  # off axis
    return {"cells": cells,
            "controls": {"aa": {"half_width_pct": aa_hw},
                         "positive": [{"cell_id": "k02_add_fwd.L1", "novec_ratio": 2.5, "ci95": [2.4, 2.6]}]}}


def set_cell(r, cid, ratio, lo, hi):
    for c in r["cells"]:
        if c["cell_id"] == cid:
            c["ratio"], c["ci95"] = ratio, [lo, hi]


def test_classes():
    cls = verdict.classes(base()["cells"])
    assert cls == {"on_axis": ["k02_add_fwd", "k03_stencil", "k04_rev", "k05_stride2"],
                   "kept": ["k02_add_fwd", "k03_stencil"], "lost": ["k04_rev", "k05_stride2"],
                   "off_axis": ["k06_gather"]}


def test_map():
    v = verdict.compute(base())
    assert v["form"] == "map"
    assert v["n"] == {"median": (5.5 + 2.8) / 2, "min": 2.8, "max": 5.5}
    assert v["forward_limit_pct"] == 2.0
    assert v["line"] == ("Loops that lose SIMD under the check (k04_rev, k05_stride2) cost 2.80 to 5.50 times as "
                         "long in cache (median 4.15); judged forward loops (k02_add_fwd, k03_stencil) cost at most "
                         "1.5% more.")
    assert "Google" not in v["line"]


def test_map_ignores_ram_and_off_axis():
    r = base()
    set_cell(r, "k02_add_fwd.RAM", 3.0, 2.9, 3.1)
    set_cell(r, "k04_rev.RAM", 1.0, 0.9, 1.1)
    set_cell(r, "k06_gather.L1", 9.0, 8.0, 10.0)
    assert verdict.compute(r)["form"] == "map"


def test_forward_point_estimate_above_1_02_breaks_map():
    r = base()
    set_cell(r, "k03_stencil.L1", 1.021, 1.0, 1.019)
    v = verdict.compute(r)
    assert v["form"] == "inconclusive"
    assert "forward rule missed by k03_stencil.L1" in v["why"]


def test_day_one_stencil_cell_passes_the_new_rule():
    # day-one k03_stencil.L1: 1.002 [0.969, 1.0201] missed "ci_hi < 1.02"; the S1 rule is "<= 1.02 point
    # and ci_hi <= 1 + max(0.02, 2 x A/A half-width)": with the day-one A/A of 0.45 % the limit is 1.02
    r = base(aa_hw=0.45)
    set_cell(r, "k03_stencil.L1", 1.002, 0.969, 1.0201)
    assert verdict.compute(r)["form"] != "map"  # 1.0201 > 1.02: still a miss at this A/A
    r = base(aa_hw=1.2)  # a noisier same-run A/A widens the limit to 2.4 %
    set_cell(r, "k03_stencil.L1", 1.002, 0.969, 1.0201)
    v = verdict.compute(r)
    assert v["form"] == "map" and v["forward_limit_pct"] == 2.4


def test_forward_ci_limit_scales_with_aa():
    r = base(aa_hw=1.5)
    set_cell(r, "k02_add_fwd.L2", 1.01, 0.98, 1.029)
    v = verdict.compute(r)
    assert v["form"] == "map" and v["forward_limit_pct"] == 3.0
    set_cell(r, "k02_add_fwd.L2", 1.01, 0.98, 1.031)
    assert verdict.compute(r)["form"] == "inconclusive"


def test_lost_below_minimum_breaks_map():
    r = base()
    set_cell(r, "k05_stride2.L2", 1.6, 1.49, 1.7)
    v = verdict.compute(r)
    assert v["form"] == "inconclusive"
    assert "lost-vectorization minimum missed by k05_stride2.L2" in v["why"]


def test_holds_everywhere():
    r = base()
    for k in LOST:
        for s in ("L1", "L2"):
            set_cell(r, f"{k}.{s}", 1.005, 0.995, 1.012)
    v = verdict.compute(r)
    assert v["form"] == "holds_everywhere"
    assert v["n"] is None
    assert v["line"] == "On this toolchain and runner, no loop shape we tried paid more than 1.5%."


def test_holds_everywhere_when_nothing_lost_vectorization():
    r = base()
    r["cells"] = [c for c in r["cells"] if c["kernel"] not in LOST]
    assert verdict.compute(r)["form"] == "holds_everywhere"


def test_inconclusive_aa_too_noisy():
    v = verdict.compute(base(aa_hw=2.01))
    assert v["form"] == "inconclusive" and v["n"] is None
    assert v["why"].startswith("A/A control")
    assert "2.01%" in v["line"]


def test_aa_exactly_two_percent_is_allowed():
    assert verdict.compute(base(aa_hw=2.0))["form"] == "map"


def test_inconclusive_checksum():
    r = base()
    r["cells"][-2]["checksum_match"] = False  # a RAM cell: any mismatch is a bug
    v = verdict.compute(r)
    assert v["form"] == "inconclusive" and v["why"].startswith("checksum control")
    assert "k05_stride2.RAM" in v["line"]


def test_inconclusive_positive_control_not_seen():
    r = base(aa_hw=1.0)
    r["controls"]["positive"] = [{"cell_id": "k02_add_fwd.L1", "novec_ratio": 1.01, "ci95": [1.005, 1.02]}]
    v = verdict.compute(r)
    assert v["form"] == "inconclusive" and v["why"].startswith("positive control")


def test_inconclusive_no_negative_control():
    r = base()
    r["cells"] = [c for c in r["cells"] if c["kernel"] not in KEPT]
    v = verdict.compute(r)
    assert v["form"] == "inconclusive" and v["why"].startswith("negative control")


def test_mixed_picture():
    r = base()
    set_cell(r, "k02_add_fwd.L1", 1.10, 1.08, 1.12)  # a kept kernel that pays: neither line fits
    v = verdict.compute(r)
    assert v["form"] == "inconclusive"
    assert v["why"].startswith("mixed picture")
    assert "no headline number" in v["line"]


def test_line_wording_when_a_non_reverse_kernel_loses_vectorization():
    r = base()
    for s in ("L1", "L2"):
        r["cells"].append(cell("k08_matmul", s, 2.0, 1.9, 2.1, vec_fast=False))
    v = verdict.compute(r)
    assert v["form"] == "map"
    assert "Loops that lose SIMD under the check (k04_rev, k05_stride2, k08_matmul)" in v["line"]


def test_compute_does_not_change_its_input():
    r = base()
    before = copy.deepcopy(r)
    verdict.compute(r)
    assert r == before
