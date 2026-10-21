"""forwardn/ (compile-only check of forward loops with a variable bound; predictions in forwardn/PLAN.md): the
source file, the build matrix, the word for a cell, the six predictions on made-up cells, and the stored results
against the saved compiler answers.

No network, no compiler: plain functions (scripts/check.py's built-in runner runs them without pytest)."""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FWD = os.path.join(REPO, "forwardn")
sys.path.insert(0, os.path.join(REPO, "ce-sweep"))


def _load():
    key = "forwardn_run"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(FWD, "run.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


fw = _load()


def _side(vectorized, width=4, interleave=2, traps=0):
    return {"vectorized": vectorized, "width": width if vectorized else None,
            "interleave": interleave if vectorized else None, "remarks": [], "traps": traps,
            "simd_instr": 4 if vectorized else 0, "instructions": 20}


def _fn(word_, traps_on=1):
    """A function record whose NONE/hardened sides give the word `word_`."""
    n = {"lost": _side(True), "narrower": _side(True), "kept": _side(True), "scalar in both": _side(False),
         "gained": _side(False)}[word_]
    h = {"lost": _side(False, traps=traps_on), "narrower": _side(True, interleave=1, traps=traps_on),
         "kept": _side(True, traps=traps_on), "scalar in both": _side(False, traps=traps_on),
         "gained": _side(True, traps=traps_on)}[word_]
    return {"none": n, "hardened": h, "word": fw.word(n, h)}


def _cells(old_lost=True, new_kept=True, member_vec=False, rangefor="kept", control="kept", arm_same=True,
           write_lost=False):
    """Made-up cells for the sixteen clang versions' worth of ids the plan names, one per (version, config)."""
    cells = {}
    versions = ["16.0.0", "17.0.1", "18.1.0", "19.1.0", "20.1.0", "21.1.0", "22.1.0", "23.1.0", "trunk"]
    for v in versions:
        lost_here = v in ("16.0.0", "17.0.1", "18.1.0")
        for target, opt in fw.CONFIGS:
            funcs = {}
            for fn in fw.FUNCTION_ORDER:
                w = "kept"
                if fn in fw.REDUCTIONS_N:
                    w = "lost" if (lost_here == old_lost and lost_here) or (not new_kept and not lost_here) else "kept"
                    if old_lost is False and lost_here:
                        w = "kept"
                if fn in fw.MEMBER_BOUND:
                    w = "kept" if member_vec else "scalar in both"
                if fn in fw.CONTROLS:
                    w = control
                if fn == "rangefor":
                    w = rangefor
                if fn in fw.WRITES_N and write_lost:
                    w = "lost"
                if target == "aarch64" and not arm_same and fn in fw.REDUCTIONS_N + fw.WRITES_N:
                    w = "scalar in both"
                funcs[fn] = _fn(w)
            cells[("clang%s" % v, target, opt)] = {"version": v, "compiled": True, "macro_effective": True,
                                                   "functions": funcs}
    return cells


def test_source_has_one_loop_comment_per_function():
    with open(os.path.join(FWD, "source.cpp"), encoding="utf-8") as f:
        src = f.read()
    ll = fw.loop_lines(src)
    assert sorted(fw.short(k) for k in ll) == sorted(fw.FUNCTION_ORDER), "functions in source.cpp and FUNCTION_ORDER differ"
    lines = src.splitlines()
    for fn, line in ll.items():
        assert "// LOOP" in lines[line - 1], fn
    marked = [ln for ln in lines if re.search(r"//\s*LOOP\s*$", ln)]
    assert len(marked) == len(ll), "a function has two LOOP comments, or a LOOP comment sits outside any function"


def test_the_matrix_is_54_builds_in_pairs_with_the_macro_of_each_library_version():
    bs = fw.builds()
    assert len(bs) == 54
    pairs = {}
    for b in bs:
        pairs.setdefault((b["compiler_id"], b["target"], b["opt"]), {})[b["mode"]] = b
    assert len(pairs) == 27 and all(set(p) == {"none", "hardened"} for p in pairs.values())
    for (cid, target, opt), p in pairs.items():
        v = p["none"]["version"]
        major = 99 if v == "trunk" else int(v.split(".")[0])
        want = "_LIBCPP_ENABLE_ASSERTIONS" if major == 16 else "_LIBCPP_ENABLE_HARDENED_MODE" if major == 17 else "_LIBCPP_HARDENING_MODE"
        for mode in ("none", "hardened"):
            assert want in p[mode]["flags"], (cid, mode)
            assert "-stdlib=libc++" in p[mode]["flags"] and opt in p[mode]["flags"].split()
        assert p["none"]["flags"] != p["hardened"]["flags"]
    assert {(t, o) for (_, t, o) in pairs} == set(fw.CONFIGS)


def test_word_names_each_case():
    assert fw.word(_side(True), _side(False)) == "lost"
    assert fw.word(_side(True), _side(True)) == "kept"
    assert fw.word(_side(True, interleave=2), _side(True, interleave=1)) == "narrower"
    assert fw.word(_side(True, width=4), _side(True, width=2)) == "narrower"
    assert fw.word(_side(False), _side(False)) == "scalar in both"
    assert fw.word(_side(False), _side(True)) == "gained"
    none_silent = dict(_side(False), vectorized=None)
    assert fw.word(_side(True), none_silent) == "lost", "no remark at all with the checks on counts as not vectorized"
    assert fw.word(none_silent, none_silent) == "scalar in both"


def test_split_funcs_cuts_at_the_function_labels():
    lines = ['fwn_sum_size(std::__1::vector<int, std::__1::allocator<int> > const&, long*):', "  push rbp",
             "  ud2", ".LBB0_2:", "  ret", "FwnWork::run():", "  paddd xmm0, xmm1",
             'other(int):', "  ret"]
    f = fw.split_funcs(lines)
    assert set(f) == {"fwn_sum_size", "FwnWork::run"}
    assert any("ud2" in x for x in f["fwn_sum_size"]) and not any("paddd" in x for x in f["fwn_sum_size"])
    assert any("paddd" in x for x in f["FwnWork::run"])
    assert fw.short("FwnWork::run") == "member_write" and fw.short("fwn_sum_size") == "sum_size"


def test_predictions_hold_on_cells_made_to_match_them():
    p = fw.evaluate(_cells())
    assert {k: v["holds"] for k, v in p.items()} == {str(i): True for i in range(1, 7)}, p


def test_each_prediction_fails_when_its_cells_contradict_it():
    cases = [("1", dict(old_lost=False)), ("1", dict(new_kept=False)), ("2", dict(arm_same=False)),
             ("3", dict(write_lost=True)), ("4", dict(member_vec=True)), ("5", dict(rangefor="lost")),
             ("6", dict(control="lost"))]
    for n, kw in cases:
        p = fw.evaluate(_cells(**kw))
        assert p[n]["holds"] is False, (n, kw, p[n])


def test_prediction_two_needs_ninety_percent_not_every_cell():
    cells = _cells()
    # 2 of the 18 x 9 aarch64 cells differ from x86-64: still above 90% (160 of 162)
    for k, e in cells.items():
        if k[1] == "aarch64" and e["version"] in ("16.0.0", "17.0.1"):
            e["functions"]["sum_n_int"] = _fn("scalar in both")
    p = fw.evaluate(cells)
    assert p["2"]["holds"] is True, p["2"]
    # many more differences: below 90%
    for k, e in cells.items():
        if k[1] == "aarch64":
            for fn in fw.REDUCTIONS_N:
                e["functions"][fn] = _fn("scalar in both")
    assert fw.evaluate(cells)["2"]["holds"] is False


def _derive():
    """What `run.py --offline` writes, rebuilt from the saved answers in forwardn/cache/."""
    with open(os.path.join(FWD, "source.cpp"), encoding="utf-8") as f:
        ll = fw.loop_lines(f.read())
    cells = fw.collect(fw.builds(), ll)
    preds = fw.evaluate(cells)
    rec = {"plan": "forwardn/PLAN.md", "functions": {fw.short(k): v for k, v in ll.items()},
           "cells": [dict(e, compiler_id=k[0], target=k[1], opt=k[2]) for k, e in sorted(cells.items())],
           "predictions": preds}
    return cells, preds, json.loads(json.dumps(rec, sort_keys=True))


def test_stored_results_are_what_the_saved_answers_give():
    with open(os.path.join(FWD, "results.json"), encoding="utf-8") as f:
        stored = json.load(f)
    cells, preds, rec = _derive()
    assert len(cells) == 27 and len(stored["cells"]) == 27
    assert stored == rec, "forwardn/results.json differs from what the saved answers give: rerun run.py --offline"
    for k, e in cells.items():
        assert e["compiled"], "a build did not compile: " + str(k)
        assert e["macro_effective"], "the hardening macro had no effect on " + str(k)


def test_generated_table_is_what_the_saved_answers_give():
    cells, preds, _ = _derive()
    with open(os.path.join(FWD, "RESULTS.generated.md"), encoding="utf-8", newline="") as f:
        assert f.read().replace("\r\n", "\n") == fw.render(cells, preds)


def test_the_readme_states_the_stored_prediction_outcomes():
    """The README table of predictions says held or failed exactly as the stored evaluation does."""
    with open(os.path.join(FWD, "results.json"), encoding="utf-8") as f:
        preds = json.load(f)["predictions"]
    with open(os.path.join(FWD, "README.md"), encoding="utf-8") as f:
        rows = {m.group(1): m.group(2) for m in re.finditer(r"^\| (\d) \|.*\| ((?:\*\*)?(?:held|failed)(?:\*\*)?)[^|]*\|$",
                                                            f.read(), re.M)}
    assert sorted(rows) == sorted(preds), rows
    for n, word in rows.items():
        assert (word.strip("*") == "held") == preds[n]["holds"], (n, word, preds[n]["holds"])


def test_plan_is_older_than_the_code_in_git_order_is_not_asserted_here():
    # the order (plan, then code, then requests) rests on commit order and is stated in forwardn/README.md, not tested
    with open(os.path.join(FWD, "PLAN.md"), encoding="utf-8") as f:
        text = f.read()
    for fn in ("sum_size", "scale_size", "rangefor"):
        assert re.search(r"\b%s\b|range-for" % fn, text) or fn == "rangefor"


if __name__ == "__main__":
    import traceback
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception:
                failed += 1
                traceback.print_exc()
    sys.exit(1 if failed else 0)
