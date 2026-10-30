"""robustness/placement_floor.py, robustness/placement-floor.json and robustness/README-placement-floor.md: what the placement
exemption would change if it also required a minimum size of D.

Stored data. The schema of the stored file; its nine input files against the files on disk; the stored exemption flag of every
cell of the eight pooled files recomputed here from the stored interval of D and the two stored hot loops; the exempt cells
and the stored words recomputed here from those pooled files (the words only through harness/pool.py, read-only); the four
rows whose word changes, the cells they hinge on and the cells with an aligned ratio above the point limit, against the
sentences of the README that say so.

Logic. The exemption rules on made-up numbers; a real CPU-model block with one cell judged and then with its interval moved;
a changed number, a changed input hash, a reordered key or a missing pool is reported by the verification; a changed or missing
generated README block is reported; the command verifies the stored file and refuses an unknown flag.

Offline and read-only (the tamper tests write to temporary folders). No fixtures, so scripts/check.py's built-in runner
runs it."""
import copy
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402


def _load(key, rel):
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


pf = _load("placement_floor_script", os.path.join("robustness", "placement_floor.py"))

POOL_IDS = ["s4", "s6", "s7", "s9-x86-c", "s9-x86-ac", "s8-arm", "s9-arm-b", "s9-arm-ab"]
ALT = ["d_floor_2pct", "d_floor_layout_aa", "d_floor_both"]
STENCIL, ADD_L1, MATMUL = "k03_stencil.L1", "k02_add_fwd.L1", "k08_matmul.L1"
MECH_KEYS = ("start_mod64", "bytes", "windows64", "extra_window")


def read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return f.read()


def readj(rel):
    return json.loads(read(*rel.split("/")))


@lru_cache(maxsize=None)
def stored():
    return readj("robustness/placement-floor.json")


@lru_cache(maxsize=None)
def fresh():
    """The document built again from the stored files."""
    return pf.build()


@lru_cache(maxsize=None)
def crit_v2():
    return readj("harness/criteria-v2.json")


@lru_cache(maxsize=None)
def crit_v3():
    return readj("harness/criteria-v3.json")


@lru_cache(maxsize=None)
def pooled_file(pid):
    (spec,) = [s for s in pf.POOLS if s["id"] == pid]
    return readj(spec["pooled"])


def readme():
    return read("robustness", "README-placement-floor.md")


TOKENS = ("7763", "9V45", "9V74", "8573C", "6973P-C", "8370C", "Neoverse-N2", "Neoverse-V3")


def token(cpu_model):
    """The short name of a CPU model: the one of TOKENS that its stored name contains."""
    (t,) = [t for t in TOKENS if t in cpu_model]
    return t


def cpu_name(pid, needle):
    (name,) = [r["cpu_model"] for p in stored()["pools"] if p["id"] == pid for r in p["models"] if needle in r["cpu_model"]]
    return name


def srow(pid, needle):
    (p,) = [p for p in stored()["pools"] if p["id"] == pid]
    (r,) = [r for r in p["models"] if needle in r["cpu_model"]]
    return r


def pblock(pid, needle):
    (b,) = [b for b in pooled_file(pid)["cpus"] if needle in b["cpu_model"]]
    return b


def cell(block, cell_id):
    (c,) = [c for c in block["cells"] if c["cell_id"] == cell_id]
    return c


def exempt(row, cell_id):
    return [e for e in row["exempt_cells"] if e["cell_id"] == cell_id]


def layout_floor(block):
    return max(block["layout_aa"][i]["half_width_pct"] for i in crit_v2()["v2"]["layout_aa_designated"])


def all_blocks():
    return [(pid, b) for pid in POOL_IDS for b in pooled_file(pid)["cpus"]]


# ------------------------------------------------------------------ the stored file

def test_the_stored_file_has_the_schema_and_sorted_keys():
    doc = stored()
    assert doc["kind"] == "placement-floor" and doc["script"] == "robustness/placement_floor.py"
    assert "not a verdict" in doc["label"]
    assert set(doc) == {"kind", "script", "label", "method", "rules", "criteria", "pools", "summary", "checks", "inputs"}
    assert [r["id"] for r in doc["rules"]] == ["written"] + ALT
    assert [p["id"] for p in doc["pools"]] == POOL_IDS
    for p in doc["pools"]:
        assert set(p) == {"id", "arch", "what", "pooled_file", "jobs", "runs", "models"}, p["id"]
        assert p["arch"] in ("x86-64", "arm64") and p["models"]
        for r in p["models"]:
            assert set(r) == {"cpu_model", "jobs", "runs", "testable", "stored_form", "stored_why", "aa_half_width_pct",
                              "forward_limit_pct", "layout_aa_pairs_half_width_pct", "layout_aa_half_width_pct",
                              "reproduces_stored_verdict", "exempt_cells", "rules", "words_that_change"}, r["cpu_model"]
            assert sorted(r["rules"]) == sorted(["written"] + ALT) and r["reproduces_stored_verdict"] is True
            for x in r["rules"].values():
                assert set(x) == {"word", "why", "exempt_cell_ids"}
            assert r["words_that_change"] == [a for a in ALT if r["rules"][a]["word"] != r["rules"]["written"]["word"]]
            for e in r["exempt_cells"]:
                assert set(e["stays_exempt"]) == set(ALT)
    assert doc["checks"] == {"problems": []}
    assert list(doc["inputs"]) == sorted(doc["inputs"]) and all(re.fullmatch(r"[0-9a-f]{64}", h) for h in doc["inputs"].values())
    with open(os.path.join(REPO, "robustness", "placement-floor.json"), "rb") as fh:
        text = fh.read().decode("utf-8")                                  # bytes, so that a CRLF checkout is seen
    assert text.endswith("\n") and "\r" not in text
    assert text == json.dumps(json.loads(text), indent=1, sort_keys=True) + "\n", "the file is not the sorted-key dump of its own content"


def test_the_rule_texts_and_the_criteria_it_quotes_are_the_ones_in_the_rule_files():
    c = stored()["criteria"]
    v3, v2 = crit_v3(), crit_v2()
    assert c["file"] == "harness/criteria-v3.json"
    assert c["forward_point_max_ratio"] == v3["verdict"]["forward_point_max_ratio"] == 1.02
    assert c["forward_ci_hi_floor_pct"] == v3["verdict"]["forward_ci_hi_floor_pct"]
    assert c["forward_ci_hi_aa_multiplier"] == v3["verdict"]["forward_ci_hi_aa_multiplier"]
    assert c["minimum_jobs"] == v3["v3"]["pooling"]["minimum_jobs"] == 3
    assert c["layout_aa_designated"] == v2["v2"]["layout_aa_designated"] == ["k02_add_fwd.L1", "k02_add_fwd.L2"]
    assert stored()["method"]["d_floor_pct"] == pf.D_FLOOR_PCT == 2.0
    # the rule as the stored file describes it is the one of criteria-v3, and its two parts are the ones of harness/pool.py
    assert "excluded from the forward rule and from X" in v3["v3"]["placement_sensitive"]["effect"] or "excluded from the forward rule and from X" in json.dumps(v3)
    pool_text = read("harness", "pool.py")
    assert 'stat_part = d["ci95"][0] > 1.0 or d["ci95"][1] < 1.0' in pool_text
    assert '"sensitive": stat_part and mech' in pool_text
    assert 'keys = ("start_mod64", "bytes", "windows64", "extra_window")' in pool_text


def test_the_inputs_are_the_nine_files_on_disk_with_their_hashes():
    doc = stored()
    expect = sorted(["harness/criteria-v3.json"] + [s["pooled"] for s in pf.POOLS])
    assert sorted(doc["inputs"]) == expect and len(expect) == 9
    for rel, h in doc["inputs"].items():
        with open(os.path.join(REPO, rel), "rb") as f:
            assert hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest() == h, rel
    for p in doc["pools"]:
        pooled = pooled_file(p["id"])
        assert p["pooled_file"] == [s["pooled"] for s in pf.POOLS if s["id"] == p["id"]][0]
        assert p["jobs"] == len(pooled["inputs"]) == sum(b["jobs"] for b in pooled["cpus"]) and p["runs"] == len(pooled["runs"])
        assert pooled["criteria_file"] == "harness/criteria-v3.json"
        assert [r["cpu_model"] for r in p["models"]] == [b["cpu_model"] for b in pooled["cpus"]], p["id"]


# ------------------------------------------------------------------ the stored exemption and the stored words

def test_the_stored_flag_of_every_cell_is_its_two_parts_recomputed_here():
    n = 0
    for pid, b in all_blocks():
        for c in b["cells"]:
            if "placement" not in c:
                continue
            n += 1
            pl = c["placement"]
            lo, hi = pl["d"]["ci95"]
            assert pl["statistical"] is (lo > 1.0 or hi < 1.0), (pid, b["cpu_model"], c["cell_id"])
            hn, hf = pl["hot_none"], pl["hot_fast"]
            mech = hn is not None and hf is not None and any(hn[k] != hf[k] for k in MECH_KEYS)
            assert pl["mechanical"] is mech, (pid, b["cpu_model"], c["cell_id"])
            assert pl["sensitive"] is (pl["statistical"] and pl["mechanical"]), (pid, b["cpu_model"], c["cell_id"])
    assert n > 150, "the eight pooled files hold fewer in-cache cells than expected"


def test_the_stored_rule_reproduces_every_stored_word_and_exempt_cell_set():
    n = 0
    for p in stored()["pools"]:
        for r, b in zip(p["models"], pooled_file(p["id"])["cpus"]):
            assert r["cpu_model"] == b["cpu_model"]
            assert r["stored_form"] == b["verdict"]["form"] == r["rules"]["written"]["word"], (p["id"], r["cpu_model"])
            assert r["stored_why"] == b["verdict"]["why"] and r["rules"]["written"]["why"] == b["verdict"]["why"]
            on_disk = [c["cell_id"] for c in b["cells"] if "placement" in c and c["placement"]["sensitive"]]
            assert r["rules"]["written"]["exempt_cell_ids"] == on_disk == [e["cell_id"] for e in r["exempt_cells"]]
            assert r["testable"] is (b["jobs"] >= 3) and r["jobs"] == b["jobs"]
            n += 1
    assert n == 32 and stored()["summary"]["testable_rows"] == 25


def test_the_exempt_cells_under_each_rule_are_recomputed_by_hand():
    for p in stored()["pools"]:
        for r, b in zip(p["models"], pooled_file(p["id"])["cpus"]):
            floor = layout_floor(b)
            assert r["layout_aa_half_width_pct"] == floor, (p["id"], r["cpu_model"])
            assert r["layout_aa_pairs_half_width_pct"] == {i: b["layout_aa"][i]["half_width_pct"] for i in ("k02_add_fwd.L1", "k02_add_fwd.L2")}
            base = [c for c in b["cells"] if "placement" in c and c["placement"]["sensitive"]]
            dev = {c["cell_id"]: abs(c["placement"]["d"]["ratio"] - 1.0) * 100.0 for c in base}
            want = {"written": [c["cell_id"] for c in base],
                    "d_floor_2pct": [i for i in dev if dev[i] >= 2.0],
                    "d_floor_layout_aa": [i for i in dev if dev[i] >= floor],
                    "d_floor_both": [i for i in dev if dev[i] >= max(2.0, floor)]}
            for rule, ids in want.items():
                assert r["rules"][rule]["exempt_cell_ids"] == ids, (p["id"], r["cpu_model"], rule)
            for e in r["exempt_cells"]:
                assert e["stays_exempt"] == {"d_floor_2pct": dev[e["cell_id"]] >= 2.0, "d_floor_layout_aa": dev[e["cell_id"]] >= floor,
                                             "d_floor_both": dev[e["cell_id"]] >= max(2.0, floor)}


# ------------------------------------------------------------------ the findings

def changed_rows(rule):
    return [(p["id"], r["cpu_model"], r["rules"]["written"]["word"], r["rules"][rule]["word"])
            for p in stored()["pools"] for r in p["models"] if r["testable"] and r["rules"][rule]["word"] != r["rules"]["written"]["word"]]


def test_four_rows_change_word_under_the_two_percent_floor_and_the_larger_floor_and_none_under_the_layout_floor():
    v9v45, x8573 = "9V45", "8573C"
    want = [("s4", cpu_name("s4", v9v45), "map", "inconclusive"), ("s6", cpu_name("s6", v9v45), "map", "inconclusive"),
            ("s7", cpu_name("s7", v9v45), "map", "inconclusive"), ("s9-x86-c", cpu_name("s9-x86-c", x8573), "map", "inconclusive")]
    assert changed_rows("d_floor_2pct") == want
    assert changed_rows("d_floor_both") == want
    assert changed_rows("d_floor_layout_aa") == []
    s = stored()["summary"]
    assert [(c["pool"], c["cpu_model"]) for c in s["word_changes"]["d_floor_2pct"]] == [(w[0], w[1]) for w in want]
    assert [(c["pool"], c["cpu_model"]) for c in s["word_changes"]["d_floor_both"]] == [(w[0], w[1]) for w in want]
    assert s["word_changes"]["d_floor_layout_aa"] == []
    for c in s["word_changes"]["d_floor_2pct"]:
        assert c["of_which_missing_the_forward_rule"] and c["from"] == "map" and c["to"] == "inconclusive"
    # the rows below have no verdict (fewer than three jobs): their words are not part of the findings
    assert all(not r["testable"] for p in stored()["pools"] for r in p["models"] if r["words_that_change"] and (p["id"], r["cpu_model"]) not in [(w[0], w[1]) for w in want])


def test_the_epyc_9v45_rows_hinge_on_the_stencil_at_l1():
    for pid in ("s4", "s6", "s7"):
        r, b = srow(pid, "9V45"), pblock(pid, "9V45")
        (e,) = exempt(r, STENCIL)
        limit = 1.0 + r["forward_limit_pct"] / 100.0
        assert e["aligned_ratio"] <= 1.02 and e["aligned_ci95"][1] > limit, pid              # point under the limit, interval end above it
        assert e["d_deviation_pct"] < 2.0 and e["passes_forward_rule_if_judged"] is False
        assert e["stays_exempt"] == {"d_floor_2pct": False, "d_floor_layout_aa": True, "d_floor_both": False}
        assert r["rules"]["written"]["word"] == "map" and r["rules"]["d_floor_2pct"]["word"] == "inconclusive"
        assert STENCIL in r["rules"]["d_floor_2pct"]["why"], pid
        assert cell(b, STENCIL)["placement"]["sensitive"] is True
    r = srow("s9-x86-c", "9V45")
    assert exempt(r, STENCIL) == [] and cell(pblock("s9-x86-c", "9V45"), STENCIL)["placement"]["sensitive"] is False
    assert r["stored_form"] == "inconclusive" and r["words_that_change"] == []
    assert STENCIL in r["stored_why"]
    r = srow("s9-x86-ac", "9V45")
    (e,) = exempt(r, STENCIL)
    assert e["aligned_ci95"][1] <= 1.0 + r["forward_limit_pct"] / 100.0 and e["passes_forward_rule_if_judged"] is True
    assert r["stored_form"] == "map" and r["words_that_change"] == []


def test_the_xeon_8573c_row_of_the_replication_set_hinges_on_the_forward_add_at_l1():
    r = srow("s9-x86-c", "8573C")
    (e,) = exempt(r, ADD_L1)
    assert e["d_deviation_pct"] < 1.0 and e["aligned_ratio"] > 1.02 and e["passes_forward_rule_if_judged"] is False
    assert e["stays_exempt"] == {"d_floor_2pct": False, "d_floor_layout_aa": True, "d_floor_both": False}
    assert r["stored_form"] == "map" and r["rules"]["d_floor_2pct"]["word"] == "inconclusive" and ADD_L1 in r["rules"]["d_floor_2pct"]["why"]
    for pid in ("s7", "s9-x86-ac"):
        r = srow(pid, "8573C")
        assert exempt(r, ADD_L1) == [] and cell(pblock(pid, "8573C"), ADD_L1)["placement"]["sensitive"] is False
        assert r["stored_form"] == "inconclusive" and ADD_L1 in r["stored_why"] and r["words_that_change"] == []


def test_the_other_cells_that_would_miss_the_forward_rule():
    d = stored()["summary"]["distinct_exempt_cells_not_passing_forward_rule"]
    names = sorted((x["cpu_model"], x["cell_id"]) for x in d)
    want = sorted([(cpu_name("s4", "7763"), STENCIL), (cpu_name("s4", "9V45"), STENCIL), (cpu_name("s9-x86-c", "8573C"), ADD_L1),
                   (cpu_name("s6", "6973P-C"), ADD_L1), (cpu_name("s7", "8370C"), ADD_L1), (cpu_name("s8-arm", "Neoverse-N2"), MATMUL),
                   (cpu_name("s9-arm-b", "Neoverse-V3"), MATMUL)])
    assert names == want
    by = {(token(x["cpu_model"]), x["cell_id"]): x["occurrences"] for x in d}
    for key, occ in by.items():
        cpu = key[0]
        if cpu in ("7763", "6973P-C", "Neoverse-V3"):
            assert all(all(o["stays_exempt"].values()) and o["d_deviation_pct"] >= 2.0 for o in occ), key       # exempt under every rule
        elif cpu == "8370C":
            assert all(o["d_deviation_pct"] < 2.0 and not o["testable"] and o["jobs"] <= 2 for o in occ), key
            assert all(o["stays_exempt"] == {"d_floor_2pct": False, "d_floor_layout_aa": True, "d_floor_both": False} for o in occ)
        elif cpu == "Neoverse-N2":
            assert [(o["pool"], o["stays_exempt"]["d_floor_layout_aa"]) for o in occ] == [("s8-arm", True), ("s9-arm-b", False), ("s9-arm-ab", True)]
            assert all(o["stays_exempt"]["d_floor_2pct"] and o["d_deviation_pct"] >= 2.0 for o in occ)
    # the Arm replication set: the matmul is judged under the layout floor and the word stays inconclusive
    r = srow("s9-arm-b", "Neoverse-N2")
    assert r["stored_form"] == r["rules"]["d_floor_layout_aa"]["word"] == "inconclusive" and r["words_that_change"] == []
    assert MATMUL in r["rules"]["written"]["exempt_cell_ids"] and MATMUL not in r["rules"]["d_floor_layout_aa"]["exempt_cell_ids"]
    un = stored()["summary"]["word_unchanged_though_a_missing_cell_is_judged"]
    assert [(u["pool"], u["word"], u["of_which_missing_the_forward_rule"]) for u in un["d_floor_layout_aa"]] == [("s9-arm-b", "inconclusive", [MATMUL])]


def test_the_exempt_cells_with_an_aligned_ratio_above_the_limit_are_six_cells_found_in_the_files():
    s = stored()["summary"]
    above = s["exempt_cells_with_aligned_ratio_above_point_limit"]
    names = sorted({(o["cpu_model"], o["cell_id"]) for o in above})
    assert len(names) == 6 and len(above) == 18
    ranges = {}
    for o in above:
        ranges.setdefault((o["cpu_model"], o["cell_id"]), []).append(o["aligned_ratio"])
        b = pblock(o["pool"], o["cpu_model"])                                   # the ratio is the one in the pooled file
        assert cell(b, o["cell_id"])["aligned"]["ratio"] == o["aligned_ratio"] > 1.02 and cell(b, o["cell_id"])["placement"]["sensitive"] is True
    low_high = {k[1] + "|" + token(k[0]): (min(v), max(v)) for k, v in ranges.items()}
    # the six cells, by CPU model (the ratio ranges are those of the pooled files)
    lo, hi = low_high[ADD_L1 + "|6973P-C"]
    assert 1.19 < lo <= hi < 1.21
    lo, hi = low_high[STENCIL + "|7763"]
    assert 1.05 < lo <= hi < 1.06
    lo, hi = low_high[ADD_L1 + "|8370C"]
    assert 1.05 < lo <= hi < 1.06
    lo, hi = low_high[MATMUL + "|Neoverse-N2"]
    assert 1.58 < lo <= hi < 1.60
    lo, hi = low_high[ADD_L1 + "|8573C"]
    assert 1.05 < lo == hi < 1.07
    lo, hi = low_high[MATMUL + "|Neoverse-V3"]
    assert 1.6 < lo == hi < 1.7
    # all other exempt cells have an aligned ratio at or under the limit
    above_ids = {(o["pool"], o["cpu_model"], o["cell_id"]) for o in above}
    for p in stored()["pools"]:
        for r in p["models"]:
            for e in r["exempt_cells"]:
                assert ((p["id"], r["cpu_model"], e["cell_id"]) in above_ids) == (e["aligned_ratio"] > 1.02), (p["id"], r["cpu_model"], e["cell_id"])


def test_the_summary_counts_are_recomputed_from_the_pooled_files():
    n, devs, below2, below_layout = 0, [], 0, 0
    for pid, b in all_blocks():
        floor = layout_floor(b)
        for c in b["cells"]:
            if "placement" in c and c["placement"]["sensitive"]:
                dv = abs(c["placement"]["d"]["ratio"] - 1.0) * 100.0
                n += 1
                devs.append(dv)
                below2 += dv < 2.0
                below_layout += dv < floor
    s = stored()["summary"]
    assert s["exempt_cell_records"] == n and s["exempt_cell_records_below_2pct"] == below2 and s["exempt_cell_records_below_layout_floor"] == below_layout
    assert math.isclose(s["d_deviation_pct_min"], min(devs), rel_tol=1e-12) and math.isclose(s["d_deviation_pct_max"], max(devs), rel_tol=1e-12)
    assert s["forward_point_max_ratio"] == 1.02


# ------------------------------------------------------------------ the logic

def test_judging_the_one_cell_changes_the_word_on_a_real_block_and_moving_its_interval_restores_it():
    crit_doc = crit_v3()
    b = copy.deepcopy(pblock("s7", "9V45"))
    cls = pf.classes_of(b["cells"])
    problems = {"checksum": [], "build": [], "layout": []}
    floor = layout_floor(b)
    assert pf.verdict_under(b, "written", floor, cls, problems, crit_doc) == b["verdict"]
    v = pf.verdict_under(b, "d_floor_2pct", floor, cls, problems, crit_doc)
    assert v["form"] == "inconclusive" and STENCIL in v["why"]
    assert pf.verdict_under(b, "d_floor_layout_aa", floor, cls, problems, crit_doc)["form"] == "map"
    moved = copy.deepcopy(b)
    cell(moved, STENCIL)["aligned"]["ci95"][1] = 1.0100                          # the interval end now under the limit
    assert pf.verdict_under(moved, "d_floor_2pct", floor, cls, problems, crit_doc)["form"] == "map"
    # the block that was passed in is not changed by the rules
    assert b == pblock("s7", "9V45")


def test_the_exemption_rules_on_made_up_numbers():
    def pl(ratio, stat=True, mech=True):
        return {"statistical": stat, "mechanical": mech, "d": {"ratio": ratio}}
    f = pf.exempt_flag
    assert [f(r, pl(1.015), 1.0) for r in ["written"] + ALT] == [True, False, True, False]
    assert [f(r, pl(1.015), 0.5) for r in ["written"] + ALT] == [True, False, True, False]
    assert [f(r, pl(1.05), 1.0) for r in ["written"] + ALT] == [True, True, True, True]
    assert [f(r, pl(1.05), 6.0) for r in ["written"] + ALT] == [True, True, False, False]
    assert [f(r, pl(1.03), 2.5) for r in ["written"] + ALT] == [True, True, True, True]
    assert [f(r, pl(1.03), 3.5) for r in ["written"] + ALT] == [True, True, False, False]
    assert [f(r, pl(0.97), 1.0) for r in ["written"] + ALT] == [True, True, True, True]         # a ratio under 1 counts by its distance
    for r in ["written"] + ALT:
        assert f(r, pl(1.5, stat=False), 0.1) is False and f(r, pl(1.5, mech=False), 0.1) is False
    try:
        f("nope", pl(1.5), 1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("an unknown rule was accepted")
    assert math.isclose(pf.d_deviation_pct(pl(0.97)), 3.0, rel_tol=1e-9) and math.isclose(pf.d_deviation_pct(pl(1.25)), 25.0, rel_tol=1e-9)


def test_classes_and_the_deep_comparison_on_made_up_input():
    cells = [{"kernel": "a", "class": "kept"}, {"kernel": "b", "class": "lost"}, {"kernel": "c", "class": "off_axis"}, {"kernel": "a", "class": "kept"}]
    assert pf.classes_of(cells) == {"on_axis": ["a", "b"], "kept": ["a"], "lost": ["b"], "off_axis": ["c"]}
    same = pf.same
    assert same({"a": [1.0, 2], "b": "x"}, {"a": [1.0 + 1e-14, 2], "b": "x"}) == []
    assert same({"a": 1.0}, {"a": 1.001}) and same({"a": [1]}, {"a": [1, 2]}) and same({"a": 1, "b": 2}, {"b": 2, "a": 1})
    assert same({"a": True}, {"a": 1}) and same({"a": 1}, {"a": 1.0}) == []
    assert same({"a": 1.0}, {"a": True}), "a float and a bool are not the same stored value"


# ------------------------------------------------------------------ the sentences of the README

README_SENTENCES = (
    "Under the layout A/A floor alone no row changes word.",
    "Every other row keeps its word under all four rules.",
    "The EPYC 9V45 rows hinge on one cell.",
    "its D is less than `2%` from `1`.",
    "In the replication set the cell is not exempt at all and the 9V45 word is INCONCLUSIVE already;",
    "in the pool of both x86-64 sets the upper end is under the limit, so the word holds under every rule.",
    "The Xeon 8573C row of the replication set hinges on the forward add at L1.",
    "its D is less than `1%` from `1`, and its aligned ratio is above the point limit.",
    "In the pools `s7` and `s9-x86-ac` the same cell is not exempt, it is judged, it misses the forward rule, and the word is INCONCLUSIVE.",
    "The MAP of the replication set for this model therefore rests on the exemption of that one cell.",
    "that row is INCONCLUSIVE with or without it.",
    "stay exempt under every rule.",
    "the pooled `95%` interval of D",
)


def test_the_readme_sentences_are_present_and_the_findings_they_state_are_tested_above():
    flat = re.sub(r"\s+", " ", readme())
    for s in README_SENTENCES:
        assert s in flat, f"README-placement-floor.md no longer says: {s!r} (change this test with the sentence)"
    # the claims of those sentences, in one place each: the layout floor changes nothing; the other rows keep their words
    assert changed_rows("d_floor_layout_aa") == []
    names_changed = {(w[0], w[1]) for w in changed_rows("d_floor_2pct")}
    for p in stored()["pools"]:
        for r in p["models"]:
            if r["testable"] and (p["id"], r["cpu_model"]) not in names_changed:
                assert r["words_that_change"] == [], (p["id"], r["cpu_model"])
    # "the Xeon 6973P-C, the EPYC 7763 stencil and the Neoverse-V3 matmul stay exempt under every rule"
    for pid, needle, cid in (("s7", "6973P-C", ADD_L1), ("s7", "7763", STENCIL), ("s9-arm-ab", "Neoverse-V3", MATMUL)):
        (e,) = exempt(srow(pid, needle), cid)
        assert all(e["stays_exempt"].values()), (pid, needle)
    # the pools the README names exist and the page reads the one it says
    assert [p["id"] for p in stored()["pools"]] == POOL_IDS
    assert 'POOLED = "results/s7-pooled/pooled.json"' in read("scripts", "build_site_data.py")
    # the README names the stored rule, the two floors and what the numbers are read from
    for needle in ("`harness/criteria-v3.json`", "`v3.placement_sensitive`", "`pool.cpu_verdict`", "`harness/criteria-v2.json`",
                   "`k02_add_fwd.L1` and `k02_add_fwd.L2`", "`robustness/placement_floor.py --report`", "no stored verdict, pool or rule file was changed"):
        assert needle in re.sub(r"\s+", " ", readme()), needle


def test_the_readme_has_no_standalone_number_outside_the_generated_block_and_code():
    text = readme()
    a, b = pf.block_of(text)
    prose = text[:a] + text[b + len(pf.MARKS[1]):]
    prose = re.sub(r"```.*?```", " ", prose, flags=re.S)
    prose = re.sub(r"`[^`\n]*`", " ", prose)
    prose = prose.replace("EPYC 7763", "EPYC").replace("EPYC 9V45", "EPYC")
    found = re.findall(r"(?<![\w.#/\-])\d+(?:[.,]\d+)?%?(?![\w.]*\w)", prose)
    assert not found, f"numbers in the prose of robustness/README-placement-floor.md that no code reads from a stored file: {found}"


def test_the_readme_block_is_the_rendering_of_the_stored_file_and_the_prose_names_its_own_guard():
    text = readme()
    assert pf.readme_block_ok(REPO, stored()) == []
    assert "tests/test_placement_floor.py" in text and "robustness/placement_floor.py --report" in text
    assert "not a verdict" in text and "no stored verdict, pool or rule file was changed" in text
    assert "Nothing here changes `harness/pool.py`, `harness/criteria-v3.json` or any file under `results/`." in text


# ------------------------------------------------------------------ the verification

def test_a_fresh_build_equals_the_stored_file_and_the_readme_block():
    doc = fresh()
    assert pf.verify_file(os.path.join(REPO, pf.OUT), doc) == []
    assert pf.readme_block_ok(REPO, doc) == []
    assert doc["checks"]["problems"] == []


def _verify_tampered(mutate):
    t = copy.deepcopy(stored())
    mutate(t)
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "placement-floor.json")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(pf.dumps(t))
        return pf.verify_file(p, fresh())


def test_verification_reports_a_changed_number_word_hash_pool_and_key_order():
    assert _verify_tampered(lambda t: None) == []
    d = _verify_tampered(lambda t: t["pools"][1]["models"][1]["exempt_cells"][0].__setitem__(
        "d_ratio", t["pools"][1]["models"][1]["exempt_cells"][0]["d_ratio"] * 1.001))
    assert d and "d_ratio" in d[0]
    d = _verify_tampered(lambda t: t["pools"][3]["models"][3]["rules"]["d_floor_2pct"].__setitem__("word", "map"))
    assert d and "word" in d[0]
    d = _verify_tampered(lambda t: t["summary"]["word_changes"]["d_floor_2pct"].pop())
    assert d and "word_changes" in d[0]
    d = _verify_tampered(lambda t: t["inputs"].__setitem__(next(iter(t["inputs"])), "0" * 64))
    assert d and "inputs" in d[0]
    d = _verify_tampered(lambda t: t["pools"].pop())
    assert d and "length" in d[0]
    d = _verify_tampered(lambda t: t["pools"][0]["models"][0].__setitem__("testable", 1))              # True and 1 are not the same stored value
    assert d
    d = _verify_tampered(lambda t: t.__setitem__("pools", [t["pools"][1], t["pools"][0]] + t["pools"][2:]))
    assert d
    with tempfile.TemporaryDirectory() as tmp:
        assert "missing" in pf.verify_file(os.path.join(tmp, "nope.json"), fresh())[0]
        p = os.path.join(tmp, "unsorted.json")                                                          # same content, top-level keys reversed
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(dict(reversed(list(stored().items()))), indent=1, sort_keys=False) + "\n")
        d = pf.verify_file(p, fresh())
        assert d and "keys" in d[0]


def test_a_changed_or_missing_generated_block_in_the_readme_is_reported():
    doc = fresh()
    text = readme()
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "robustness"))
        p = os.path.join(tmp, "robustness", "README-placement-floor.md")
        assert pf.readme_block_ok(tmp, doc) == [f"{pf.README} is missing"]
        a, b = pf.block_of(text)
        block = text[a:b]
        digit = re.search(r"\d", block[block.index("| s7 |"):]).start() + block.index("| s7 |")
        for label, new in (("a digit in the table", text[:a] + block[:digit] + str((int(block[digit]) + 1) % 10) + block[digit + 1:] + text[b:]),
                           ("a changed word", text[:a] + block.replace("inconclusive (changed)", "map", 1) + text[b:]),
                           ("a missing end marker", text.replace(pf.MARKS[1], ""))):
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            assert pf.readme_block_ok(tmp, doc), f"not reported: {label}"
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text.replace("\n", "\r\n"))                                                         # a CRLF checkout of the same text is the same block
        assert pf.readme_block_ok(tmp, doc) == []
        # writing the block into a README whose block is empty gives the rendering
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text[:a + len(pf.MARKS[0])] + "\n" + text[b:])
        assert pf.readme_block_ok(tmp, doc)
        pf.write_readme_block(tmp, doc)
        assert pf.readme_block_ok(tmp, doc) == []


def test_the_command_verifies_the_stored_file_and_refuses_an_unknown_flag():
    cmd = [sys.executable, "-I", os.path.join(REPO, "robustness", "placement_floor.py")]
    r = subprocess.run(cmd + ["--verify"], capture_output=True, text=True, timeout=300, cwd=tempfile.gettempdir())
    assert r.returncode == 0, r.stdout + r.stderr
    s = stored()["summary"]
    assert "equals a recomputation" in r.stdout and f"{s['testable_rows']} verdict rows in {len(stored()['pools'])} pools" in r.stdout
    for bad in (["--bogus"], ["--deep"]):
        r = subprocess.run(cmd + bad, capture_output=True, text=True, timeout=60, cwd=tempfile.gettempdir())
        assert r.returncode == 2, (bad, r.stdout + r.stderr)


def test_scripts_check_runs_the_placement_floor_verification_and_fails_when_it_is_absent():
    src = read("scripts", "check.py")
    # the call itself, not the docstring that names it
    m = re.search(r"subprocess\.call\(\[sys\.executable, os\.path\.join\(REPO, \"robustness\", \"placement_floor\.py\"\), \"--verify\"\]\)", src)
    assert m, "scripts/check.py does not run robustness/placement_floor.py --verify"
    assert "missing_step" in src[m.start():m.start() + 400], "scripts/check.py does not report a missing robustness/placement_floor.py as a failed step"
    for rel in ("robustness/placement_floor.py", "robustness/placement-floor.json", "robustness/README-placement-floor.md"):
        assert os.path.exists(os.path.join(REPO, *rel.split("/"))), rel


# ---- the README's folder map names the harness note and the three placement-floor files ----------------------------------------

FOLDER_MAP_FLOOR_FILES = ("robustness/placement_floor.py", "robustness/placement-floor.json", "robustness/README-placement-floor.md")
FOLDER_MAP_READINGS = ("seeds_x86.py", "aa_l2.py", "calibration.py", "placement_floor.py")
FOLDER_MAP_FLOOR_WORDS = "(the stored words re-read with a minimum size added to the placement exemption)"  # what the entry says the reading is


def folder_map_bullet(text, label):
    """The one folder-map bullet of the README that begins with `- **label:**`."""
    found = [line for line in text.splitlines() if line.startswith(f"- **{label}:**")]
    assert len(found) == 1, f"the README has {len(found)} folder-map bullets labelled {label}, not one"
    return found[0]


def check_folder_map(text):
    """The Study bullet points at harness/README.md; the Runs bullet names the three files of the placement-floor reading and counts its
    stored readings by the scripts it names (four: seeds_x86, aa_l2, calibration, placement_floor) and says in the parenthesis after the
    placement-floor files what that reading is."""
    study = folder_map_bullet(text, "Study")
    assert "`harness/` times and judges (see `harness/README.md`)" in study, "the folder map's harness entry does not point at harness/README.md"
    runs = folder_map_bullet(text, "Runs")
    for rel in FOLDER_MAP_FLOOR_FILES:
        assert f"`{rel}`" in runs, f"the folder map's robustness entry does not name {rel}"
    clause = runs[runs.index("`robustness/` also holds"):]
    clause = clause[:clause.index("; `siblings/`")]
    named = re.findall(r"`robustness/(\w+\.py)`", clause)
    assert named == list(FOLDER_MAP_READINGS), f"the robustness entry names the scripts {named}, not {list(FOLDER_MAP_READINGS)}"
    assert f"holds {['zero', 'one', 'two', 'three', 'four', 'five'][len(named)]} stored readings" in clause, "the robustness entry's count of stored readings is not the number of scripts it names"
    assert clause.endswith(f"`robustness/README-placement-floor.md` {FOLDER_MAP_FLOOR_WORDS}"), "the robustness entry no longer ends with the placement-floor reading described as " + FOLDER_MAP_FLOOR_WORDS


def test_the_folder_map_names_the_harness_note_and_the_placement_floor_files():
    text = read("README.md")
    check_folder_map(text)
    for rel in ("harness/README.md",) + FOLDER_MAP_FLOOR_FILES:
        assert os.path.exists(os.path.join(REPO, *rel.split("/"))), rel


def assertion_from(fn, what):
    """The AssertionError fn raises, as text; a failed test if it raises none (the built-in runner has no pytest.raises)."""
    try:
        fn()
    except AssertionError as e:
        return str(e)
    raise AssertionError(f"not reported: {what}")


def test_a_folder_map_without_these_names_or_with_a_wrong_count_is_reported():
    text = read("README.md")
    for old, new, what in (
            ("`harness/` times and judges (see `harness/README.md`)", "`harness/` times and judges", "the pointer to harness/README.md removed"),
            ("`robustness/placement_floor.py` with", "`robustness/placement_flor.py` with", "the script's name misspelled"),
            ("`robustness/placement-floor.json`", "`robustness/placement-floor.jsn`", "the stored file's name misspelled"),
            ("`robustness/README-placement-floor.md`", "the placement-floor note", "the note's name replaced by words"),
            ("holds four stored readings", "holds three stored readings", "the count left at three"),
            ("holds four stored readings", "holds five stored readings", "the count raised without a script"),
            (FOLDER_MAP_FLOOR_WORDS, "(the stored words re-read under a stricter exemption)", "the description replaced by another"),
            (FOLDER_MAP_FLOOR_WORDS, "(the stored words re-read with a minimum size added to the exemption)", "a word dropped from the description"),
            (FOLDER_MAP_FLOOR_WORDS, FOLDER_MAP_FLOOR_WORDS[1:-1], "the parenthesis removed"),
            (FOLDER_MAP_FLOOR_WORDS, FOLDER_MAP_FLOOR_WORDS + " and is the right rule", "a clause appended after the description"),
            (" " + FOLDER_MAP_FLOOR_WORDS, "", "the description removed")):
        assert old in text, f"the tamper test no longer matches the README: {old}"
        assert assertion_from(lambda: check_folder_map(text.replace(old, new, 1)), what)
    assert assertion_from(lambda: check_folder_map(text.replace("- **Runs:**", "- **Runs and more:**", 1)), "the Runs bullet renamed")
