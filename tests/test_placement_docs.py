"""The sentences about the placement exemption, tied to the stored pools.

README.md and readme-parts/DETAILS.md say what the second test of the exemption (the mechanical one: the two builds' hot loops sit differently
relative to 64-byte windows) can and cannot rule out, and how large the exemption is. Every figure in those sentences is read from the placement
blocks of results/s7-pooled/pooled.json (x86-64) and results/s8-arm-pooled/pooled.json (Arm) and from investigate/FINDINGS.md; nothing is
re-measured and nothing is written.

Each check comes with a tamper test: the broken sentence is built in memory and the check has to name it.

Runs with or without pytest (scripts/check.py's built-in runner, which CI uses, has none).
"""

import os
import re
import sys

try:
    import pytest  # noqa: F401  (only to learn whether it is installed)
except ImportError:  # scripts/check.py falls back to its own runner when pytest is missing
    pytest = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_readme_numbers as T  # noqa: E402

POOLS = (("x86-64", "results/s7-pooled/pooled.json"), ("Arm", "results/s8-arm-pooled/pooled.json"))
LAYOUT_KEYS = ("start_mod64", "bytes", "windows64", "extra_window")


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


def placement_cells():
    """Every kept in-cache cell of the two stored pools that has a placement block: pool, CPU model, jobs, cell id, both ratios and the block."""
    found = []
    for pool, rel in POOLS:
        for cpu in T.J(rel)["cpus"]:
            for cell in cpu["cells"]:
                if cell.get("placement"):
                    found.append({"pool": pool, "cpu": cpu["cpu_model"], "jobs": cpu["jobs"], "id": cell["cell_id"],
                                  "as_compiled": cell["as_compiled"]["ratio"], "aligned": cell["aligned"]["ratio"], "p": cell["placement"]})
    assert len(found) >= 40, f"the two pools hold only {len(found)} placement blocks: the file layout changed"
    return found


def findings_interleave():
    """(FAST's interleave count, NONE's) as investigate/FINDINGS.md gives them: 'clang picks interleave 1, not 2' under FAST."""
    with open(os.path.join(T.REPO, "investigate", "FINDINGS.md"), encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"Under FAST, clang picks interleave (\d+), not (\d+)", text)
    assert m, "investigate/FINDINGS.md no longer says which interleave count FAST picks and which NONE picks"
    return m.group(1), m.group(2)


# ---- F12: what the second test can rule out ----------------------------------------------------------

SECOND_TEST = re.compile(
    r"The second test \(the hot loop's start within its 64-byte window, its size in bytes, the number of 64-byte windows it spans, and whether it "
    r"needs an extra one\) only rules out pairs that are alike in all four, such as the forward sum's: the first test flags (?P<flagged>\d+) cells "
    r"in the x86-64 and Arm pools and the second removes none of them, because the hot loop's start within its window differs between the two "
    r"builds in all (?P<start_n>\d+)\. For the forward add the two x86-64 builds' hot loops also differ in size "
    r"\((?P<none_bytes>\d+) and (?P<fast_bytes>\d+) bytes\), so \"placement-sensitive\" there covers the loops' layout and their code together, "
    r"and aligning removes the layout part only; the cause was examined on (?P<models>EPYC \w+, EPYC \w+ and EPYC \w+) only "
    r"\(`investigate/FINDINGS\.md` records FAST choosing interleave count (?P<fast_il>\d+) where NONE chooses (?P<none_il>\d+)\), so for the Intel "
    r"and Arm cells, and for the stencil on every model, the test shows that the layouts differ, not why\. "
    r"On Arm the matmul pair has the same size \((?P<arm_bytes>\d+) bytes\) and differs in start offset, windows spanned and extra window\.")


def findings_models():
    """The CPU models investigate/FINDINGS.md examined, as 'EPYC xxxx' names, and the count its Limits line gives ('three CPU models')."""
    with open(os.path.join(T.REPO, "investigate", "FINDINGS.md"), encoding="utf-8") as f:
        text = f.read()
    limit = re.search(r"Limits: one run, (\w+) CPU models", text)
    assert limit, "investigate/FINDINGS.md no longer gives the number of CPU models it examined in its Limits line"
    return {f"EPYC {m}" for m in re.findall(r"EPYC (\w+)", text)}, {"three": 3}.get(limit.group(1), limit.group(1))


def second_test_facts():
    """What the pools say about the second test, for comparison with the sentence."""
    cells = placement_cells()
    flagged = [c for c in cells if c["p"]["statistical"]]
    exempt = [c for c in cells if c["p"]["sensitive"]]
    start_differs = [c for c in exempt if c["p"]["hot_none"]["start_mod64"] != c["p"]["hot_fast"]["start_mod64"]]
    models, models_n = findings_models()
    vetoed = [c for c in flagged if not c["p"]["mechanical"]]
    sums = [c for c in cells if c["id"].startswith("k01_sum_fwd.")]
    adds = [c for c in cells if c["pool"] == "x86-64" and c["id"].startswith("k02_add_fwd.")]
    matmuls = [c for c in cells if c["pool"] == "Arm" and c["id"].startswith("k08_matmul.")]
    fast_il, none_il = findings_interleave()
    return {"flagged": len(flagged), "exempt": len(exempt), "vetoed": len(vetoed), "start_differs": len(start_differs),
            "findings_models": models, "findings_models_n": models_n,
            "sums_alike": all(all(c["p"]["hot_none"][k] == c["p"]["hot_fast"][k] for k in LAYOUT_KEYS) for c in sums) and len(sums) >= 14,
            "add_bytes": {(c["p"]["hot_none"]["bytes"], c["p"]["hot_fast"]["bytes"]) for c in adds},
            "matmul_bytes": {(c["p"]["hot_none"]["bytes"], c["p"]["hot_fast"]["bytes"]) for c in matmuls},
            "matmul_differs": all(all(c["p"]["hot_none"][k] != c["p"]["hot_fast"][k] for k in ("start_mod64", "windows64", "extra_window")) for c in matmuls) and len(matmuls) == 2,
            "fast_il": fast_il, "none_il": none_il}


def check_second_test_sentence(text, doc):
    m = SECOND_TEST.search(T.squash(text))
    assert m, f"{doc} no longer holds the sentence about what the second test of the exemption rules out (or its wording changed)"
    g, facts = m.groupdict(), second_test_facts()
    assert int(g["flagged"]) == facts["flagged"] == facts["exempt"], f"{doc}: the first test flags {facts['flagged']} cells and {facts['exempt']} are exempt; the sentence says {g['flagged']}"
    assert facts["vetoed"] == 0, f"the second test removed {facts['vetoed']} cells the first test flagged; the sentence says none"
    assert int(g["start_n"]) == facts["start_differs"] == facts["exempt"], \
        f"{doc}: the hot loop's start within its window differs in {facts['start_differs']} of {facts['exempt']} left-out cells; the sentence says all {g['start_n']}"
    named = set(re.findall(r"EPYC \w+", g["models"]))
    assert named == facts["findings_models"] and len(named) == facts["findings_models_n"] == 3, \
        f"{doc}: investigate/FINDINGS.md examined {sorted(facts['findings_models'])} ({facts['findings_models_n']} CPU models); the sentence names {sorted(named)}"
    assert facts["sums_alike"], "the forward sum's two builds no longer have alike hot loops in every pool and model"
    assert facts["add_bytes"] == {(int(g["none_bytes"]), int(g["fast_bytes"]))}, f"{doc}: the forward add's hot loops are {sorted(facts['add_bytes'])} bytes (NONE, FAST); the sentence says {g['none_bytes']} and {g['fast_bytes']}"
    assert facts["matmul_bytes"] == {(int(g["arm_bytes"]), int(g["arm_bytes"]))}, f"{doc}: the Arm matmul pairs are {sorted(facts['matmul_bytes'])} bytes; the sentence says {g['arm_bytes']} for both"
    assert facts["matmul_differs"], "the Arm matmul pair no longer differs in start offset, windows and extra window in both cells"
    assert (g["fast_il"], g["none_il"]) == (facts["fast_il"], facts["none_il"]), f"{doc}: investigate/FINDINGS.md gives interleave {facts['fast_il']} (FAST) and {facts['none_il']} (NONE); the sentence says {g['fast_il']} and {g['none_il']}"
    return g


def test_the_readme_and_details_say_what_the_second_test_rules_out():
    for doc, text in (("README.md", T.readme_text()), ("readme-parts/DETAILS.md", T.details_text())):
        g = check_second_test_sentence(text, doc)
        assert (g["flagged"], g["start_n"], g["none_bytes"], g["fast_bytes"], g["arm_bytes"]) == ("17", "17", "56", "31", "36"), g
        assert set(re.findall(r"EPYC \w+", g["models"])) == {"EPYC 7763", "EPYC 9V74", "EPYC 9V45"}, g


def test_the_two_pools_split_the_exempted_cells_13_and_4():
    cells = [c for c in placement_cells() if c["p"]["sensitive"]]
    assert {pool: sum(1 for c in cells if c["pool"] == pool) for pool, _ in POOLS} == {"x86-64": 13, "Arm": 4}


def test_a_wrong_second_test_sentence_is_caught():
    for doc, text in (("README.md", T.readme_text()), ("readme-parts/DETAILS.md", T.details_text())):
        check_second_test_sentence(text, doc)
        for old, new in (("flags 17 cells", "flags 16 cells"), ("(56 and 31 bytes)", "(56 and 30 bytes)"), ("(56 and 31 bytes)", "(52 and 31 bytes)"),
                         ("same size (36 bytes)", "same size (40 bytes)"), ("interleave count 1 where", "interleave count 2 where"),
                         ("where NONE chooses 2", "where NONE chooses 4"), ("and the second removes none of them", "and the second removes 2 of them"),
                         ("differs between the two builds in all 17", "differs between the two builds in all 16"),
                         ("EPYC 7763, EPYC 9V74 and EPYC 9V45 only", "EPYC 7763, EPYC 9V74 and EPYC 9V74 only"),
                         ("EPYC 7763, EPYC 9V74 and EPYC 9V45 only", "EPYC 7763, EPYC 9V74 and EPYC 9V84 only"),
                         ("the test shows that the layouts differ, not why", "the test shows why the layouts differ"),
                         ("the cause was examined on EPYC 7763, EPYC 9V74 and EPYC 9V45 only", "the cause was examined on all the CPU models")):
            broken = text.replace(old, new)
            assert broken != text, (doc, old)
            assertion_from(lambda b=broken, d=doc: check_second_test_sentence(b, d), f"{doc}: {old!r} -> {new!r}")
        # the sentence deleted
        cut = text.replace("only rules out pairs that are alike in all four", "rules out pairs")
        assert cut != text
        assertion_from(lambda b=cut, d=doc: check_second_test_sentence(b, d), f"{doc}: the sentence reworded")


# ---- F11: the exemption asks whether the columns differ, not by how much -----------------------------------

EFFECT_SIZE = re.compile(
    r"The rule asks whether the two columns differ, not by how much: the 6973P-C's forward add at L1 is left out with a ratio of "
    r"(?P<d>\d\.\d{3}) \[(?P<lo>\d\.\d{3}), (?P<hi>\d\.\d{3})\] between its two columns \((?P<jobs>\d+) jobs\), although it costs "
    r"(?P<aligned>\d\.\d{3}) even when aligned; of the (?P<exempt>\d+) cells left out in the x86-64 and Arm pools, (?P<above>\d+) are above "
    r"(?P<limit>\d\.\d{2}) in the aligned column by the point ratio \(the 6973P-C's forward add at L1, the EPYC 7763's stencil at L1, the Xeon 8370C's forward add "
    r"at L1 from its (?P<jobs8370>\d+) job, and the Arm core's matmul at L1\) and (?P<above_upper>\d+) by the upper end of the interval, the fifth being "
    r"the EPYC 9V45's stencil at L1 \((?P<fifth>\d\.\d{4})\)\.")

MODELS = ("6973P-C", "EPYC 7763", "EPYC 9V45", "8370C", "Neoverse-N2")
# the four cells the sentence names as above the limit by the point ratio: (a part of the CPU model, the cell id)
NAMED_ABOVE = {("6973P-C", "k02_add_fwd.L1"), ("EPYC 7763", "k03_stencil.L1"), ("8370C", "k02_add_fwd.L1"), ("Neoverse-N2", "k08_matmul.L1")}
# the cell the sentence adds when the reading is the interval's upper end
NAMED_EXTRA = {("EPYC 9V45", "k03_stencil.L1")}


def effect_size_facts():
    """The left-out cells and those of them above their own pool's forward limit in the aligned column, read two ways: by the point ratio and by the
    upper end of the interval; plus the 6973P-C's forward add at L1."""
    above, upper, limits, exempt = set(), set(), set(), 0
    upper_end = {}
    for pool, rel in POOLS:
        for cpu in T.J(rel)["cpus"]:
            limit = 1 + cpu["verdict"]["forward_limit_pct"] / 100
            for cell in cpu["cells"]:
                p = cell.get("placement")
                if not (p and p["sensitive"]):
                    continue
                exempt += 1
                key = (cpu["cpu_model"], cell["cell_id"], cpu["jobs"])
                if cell["aligned"]["ratio"] > limit:
                    above.add(key)
                    limits.add(round(limit, 4))
                if cell["aligned"]["ci95"][1] > limit:
                    upper.add(key)
                    upper_end[key] = cell["aligned"]["ci95"][1]
    named = {(next((k for k in MODELS if k in model), model), cell) for model, cell, _ in above}
    named_upper = {(next((k for k in MODELS if k in model), model), cell) for model, cell, _ in upper}
    jobs8370 = {jobs for model, _, jobs in above if "8370C" in model}
    extra_ends = {f"{upper_end[k]:.4f}" for k in upper - above}
    case = next(c for c in placement_cells() if c["pool"] == "x86-64" and "6973P-C" in c["cpu"] and c["id"] == "k02_add_fwd.L1")
    return {"exempt": exempt, "above": len(above), "named": named, "limits": limits, "jobs8370": jobs8370, "case": case,
            "above_upper": len(upper), "named_upper": named_upper, "extra_ends": extra_ends, "point_inside_upper": above <= upper}


def check_effect_size_sentence(text, doc):
    m = EFFECT_SIZE.search(T.squash(text))
    assert m, f"{doc} no longer holds the sentence that says the exemption asks whether the columns differ, not by how much (or its wording changed)"
    g, f = m.groupdict(), effect_size_facts()
    case = f["case"]
    d = case["p"]["d"]
    assert case["p"]["sensitive"], "the 6973P-C's forward add at L1 is no longer left out"
    assert (g["d"], g["lo"], g["hi"]) == (f"{d['ratio']:.3f}", f"{d['ci95'][0]:.3f}", f"{d['ci95'][1]:.3f}"), \
        f"{doc}: the ratio between the columns is {d['ratio']:.3f} {d['ci95']}; the sentence says {g['d']} [{g['lo']}, {g['hi']}]"
    assert int(g["jobs"]) == case["jobs"], f"{doc}: the 6973P-C pool has {case['jobs']} jobs; the sentence says {g['jobs']}"
    assert g["aligned"] == f"{case['aligned']:.3f}", f"{doc}: the aligned ratio is {case['aligned']:.3f}; the sentence says {g['aligned']}"
    assert int(g["exempt"]) == f["exempt"], f"{doc}: {f['exempt']} cells are left out in the two pools; the sentence says {g['exempt']}"
    assert int(g["above"]) == f["above"] == len(NAMED_ABOVE), \
        f"{doc}: {f['above']} left-out cells are above their limit in the aligned column; the sentence says {g['above']} and names {len(NAMED_ABOVE)}"
    assert f["named"] == NAMED_ABOVE, f"{doc}: the left-out cells above the limit are {sorted(f['named'])}; the sentence names {sorted(NAMED_ABOVE)}"
    assert f["point_inside_upper"], "a left-out cell is above the limit by its point ratio but not by the upper end of its interval"
    assert int(g["above_upper"]) == f["above_upper"] == len(NAMED_ABOVE) + len(NAMED_EXTRA), \
        f"{doc}: {f['above_upper']} left-out cells have an aligned interval ending above the limit; the sentence says {g['above_upper']}"
    assert f["named_upper"] == NAMED_ABOVE | NAMED_EXTRA, f"{doc}: the cells whose interval ends above the limit are {sorted(f['named_upper'])}; the sentence names the four and {sorted(NAMED_EXTRA)}"
    assert f["extra_ends"] == {g["fifth"]}, f"{doc}: the fifth cell's interval ends at {sorted(f['extra_ends'])}; the sentence says {g['fifth']}"
    assert f["limits"] == {1.02} and float(g["limit"]) == 1.02, f"{doc}: the forward limits of these models are {sorted(f['limits'])}; the sentence says {g['limit']}"
    assert f["jobs8370"] == {int(g["jobs8370"])}, f"{doc}: the Xeon 8370C pool has {sorted(f['jobs8370'])} jobs; the sentence says {g['jobs8370']}"
    return g


def test_the_readme_and_details_give_the_size_of_what_the_exemption_leaves_out():
    for doc, text in (("README.md", T.readme_text()), ("readme-parts/DETAILS.md", T.details_text())):
        g = check_effect_size_sentence(text, doc)
        assert (g["d"], g["lo"], g["hi"], g["jobs"], g["aligned"], g["exempt"], g["above"], g["jobs8370"], g["above_upper"], g["fifth"]) \
            == ("1.027", "1.021", "1.035", "7", "1.199", "17", "4", "1", "5", "1.0204"), g


def test_a_wrong_effect_size_sentence_is_caught():
    for doc, text in (("README.md", T.readme_text()), ("readme-parts/DETAILS.md", T.details_text())):
        check_effect_size_sentence(text, doc)
        for old, new in (("ratio of 1.027 [", "ratio of 1.037 ["), ("[1.021, 1.035]", "[1.011, 1.035]"), ("[1.021, 1.035]", "[1.021, 1.045]"), ("(7 jobs)", "(6 jobs)"),
                         ("costs 1.199 even", "costs 1.099 even"), ("of the 17 cells", "of the 16 cells"),
                         ("Arm pools, 4 are above", "Arm pools, 3 are above"), ("are above 1.02 in", "are above 1.05 in"),
                         ("the EPYC 7763's stencil at L1", "the EPYC 9V74's stencil at L1"), ("from its 1 job", "from its 3 job"),
                         ("the Arm core's matmul at L1", "the Arm core's matmul at L2"),
                         ("matmul at L1) and 5 by the upper end", "matmul at L1) and 6 by the upper end"),
                         ("the fifth being the EPYC 9V45's stencil", "the fifth being the EPYC 9V74's stencil"),
                         ("stencil at L1 (1.0204)", "stencil at L1 (1.0104)"),
                         ("are above 1.02 in the aligned column by the point ratio", "are above 1.02 in the aligned column")):
            broken = text.replace(old, new)
            assert broken != text, (doc, old)
            assertion_from(lambda b=broken, d=doc: check_effect_size_sentence(b, d), f"{doc}: {old!r} -> {new!r}")
        cut = text.replace("The rule asks whether the two columns differ, not by how much:", "The rule asks:")
        assert cut != text
        assertion_from(lambda b=cut, d=doc: check_effect_size_sentence(b, d), f"{doc}: the sentence reworded")
