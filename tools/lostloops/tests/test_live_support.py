"""Offline tests for the things found by reading the tool for a first live run with real clang
(tools/lostloops-live/PLAN.md), and for the live comparison (tools/lostloops-live/compare.py).
Each test names the bug it pins."""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import shutil

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.dirname(TESTS)
REPO = os.path.dirname(os.path.dirname(TOOL))
LIVE = os.path.join(REPO, "tools", "lostloops-live")
if TOOL not in sys.path:
    sys.path.insert(0, TOOL)

import lostloops as ll  # noqa: E402
from test_lostloops import patched, quiet, _R  # noqa: E402


def load_compare():
    spec = importlib.util.spec_from_file_location("ll_live_compare", os.path.join(LIVE, "compare.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- bugs found by reading the code

def test_lto_flags_are_dropped():
    """With -flto clang writes bitcode and the loop vectorizer runs at link time: a compile-only run
    would report no vectorized loop and no lost loop, silently. The flags are removed and reported."""
    kept, removed = ll.clean_args(["-O2", "-flto=thin", "-flto", "-flto-jobs=4", "-fwhole-program-vtables",
                                   "-fno-lto", "-c", "a.cpp"])
    assert kept == ["-O2", "-fno-lto", "a.cpp"]
    assert "-flto=thin" in removed and "-fwhole-program-vtables" in removed


def test_newest_clang_without_libcxx_does_not_hide_a_working_one():
    """GitHub's Ubuntu images have several clang++-NN; the newest may lack libc++-NN-dev. Before the fix
    the newest was taken and the run stopped with exit 2."""
    def fake_check(clang):
        if clang == ["/usr/bin/clang++-19"]:
            raise ll.ToolMissing("libc++ 18 or newer is not usable with clang++-19")
        return "clang version 18.1.3", "18"

    class A:
        clang = None
        objdump = "none"
    old = os.environ.pop("LOSTLOOPS_CLANG", None)
    try:
        with patched(ll, "clang_candidates", lambda: [["/usr/bin/clang++-19"], ["/usr/bin/clang++-18"]]), \
                patched(ll, "check_toolchain", fake_check):
            t = ll.find_tools(A())
            assert t.clang == ["/usr/bin/clang++-18"] and t.version.startswith("clang version 18")

            def all_bad(clang):
                raise ll.ToolMissing("bad " + clang[0])
            with patched(ll, "check_toolchain", all_bad):
                try:
                    ll.find_tools(A())
                    raise AssertionError("expected ToolMissing")
                except ll.ToolMissing as e:
                    assert "clang++-19" in str(e)  # the first (newest) failure is the one reported
    finally:
        if old is not None:
            os.environ["LOSTLOOPS_CLANG"] = old


def test_trace_timeout_or_missing_tool_does_not_abort_the_report():
    """Before the fix a timeout (or an OSError) in the traced rebuild escaped trace_unit and ended the
    run with exit 1 after every file had been compiled."""
    def boom(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd, 5)
    e = {"function": "f", "file": "k.cpp", "line": 5, "column": 3, "origin": "project"}
    tmp = tempfile.mkdtemp()
    try:
        t = ll.Tools(["clang++-18"], objdump="objdump", symbolizer="llvm-symbolizer-18")
        with patched(ll, "run", boom):
            ll.trace_unit(t, {"directory": "/r", "file": "/r/k.cpp", "args": ["-O2"]}, 0, "fast", tmp, [e], "/r", {})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    assert e["check"]["status"].startswith("not traced (")


def test_compile_timeout_is_a_failed_file_not_a_crash():
    """compile_all takes the timeout from --timeout (default 1800) and records an expired compile as a
    failed file."""
    seen = {}

    def slow(cmd, **kw):
        seen["timeout"] = kw.get("timeout")
        raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
    tmp = tempfile.mkdtemp()
    try:
        u = {"directory": tmp, "file": tmp + "/a.cpp", "args": ["-O2", "a.cpp"]}
        with patched(ll, "run", slow):
            res = ll.compile_all(ll.Tools(["clang++-18"]), [u], ["none"], tmp, 1, (), 7)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    assert seen["timeout"] == 7 and res[(0, "none")]["rc"] == -1 and "error" in res[(0, "none")]["stderr"]
    assert ll.parse_args(["--files", "a.cpp"]).timeout == 1800 and \
        ll.parse_args(["--files", "a.cpp", "--timeout", "60"]).timeout == 60


# ---------------------------------------------------------------- the live comparison

def tool_report_from(expected):
    """What a perfect tool run would write for the expected census lists (in the tool's naming)."""
    def conv(e, kind):
        o = dict(e)
        if kind != "gained":
            o["hardened_remarks"] = e["hardened_remarks"]
        if "check" in e:
            st = {"checked container access in the loop": "check traced to the loop",
                  "no trap attributed to this loop": "no check traced to the loop"}[e["check"]["status"]]
            o["check"] = {"status": st, "messages": e["check"]["messages"], "attributed_checks": e["check"]["attributed"]}
        if o["origin"] == "driver":
            o["origin"] = "project"
        return o
    return {"totals": {"files_in_input": expected["translation_units"], "files_compiled": expected["compiled"],
                       "vectorized_none": expected["vectorized_none"],
                       "vectorized_hardened": expected["vectorized_hardened"], "traps_added": expected["traps_added"],
                       "text_bytes_none": expected["text_bytes_none"],
                       "text_bytes_hardened": expected["text_bytes_hardened"]},
            **{k: [conv(e, k) for e in expected[k]] for k in ("lost", "moved", "gained")}}


def load_expected(name):
    with open(os.path.join(LIVE, "expected", name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def test_compare_equal_lists_pass_and_every_kind_of_difference_fails():
    cmp = load_compare()
    for name in ("leveldb", "spectra", "lightgbm"):
        ex = load_expected(name)
        assert ex["lost"] and sum(e["count"] for e in ex["lost"]) > 0
        rep = tool_report_from(ex)
        assert cmp.compare(rep, ex, "/deps/src/x", ["/deps/src"])["pass"], name
    ex = load_expected("spectra")
    base = tool_report_from(ex)

    def fails(mutate, part):
        r = copy.deepcopy(base)
        mutate(r)
        res = cmp.compare(r, ex, "/deps/src/x", ["/deps/src"])
        assert not res["pass"] and res[part], (part, res)
    fails(lambda r: r["lost"].pop(), "lists")                                   # a lost loop missing
    fails(lambda r: r["lost"][0].__setitem__("count", r["lost"][0]["count"] + 1), "lists")  # one more copy
    fails(lambda r: r["gained"].append(dict(r["lost"][0])), "lists")            # an extra gained loop
    fails(lambda r: r["lost"][0].__setitem__("line", r["lost"][0]["line"] + 1), "lists")
    fails(lambda r: r["totals"].__setitem__("vectorized_none", 1), "totals")
    fails(lambda r: r["lost"][0].__setitem__("class", "reverse"), "details")
    fails(lambda r: r["lost"][0]["check"].__setitem__("status", "not traced (--no-trace)"), "checks")
    fails(lambda r: r["lost"][0]["check"].__setitem__("attributed_checks", 99), "checks")


def test_compare_maps_origin_naming_between_census_and_tool():
    """The census calls ../fmt-x/include/f.h 'project' (root-relative) and _census_driver/ 'driver'; the
    tool sees an absolute 'system' path and a 'project' file. The comparison maps exactly these."""
    cmp = load_compare()
    root, outside = "/w/deps/src/lightgbm", ["/w/deps/src"]
    e = {"tu": "src/a.cpp", "function": "_Zf", "line": 3, "column": 5, "count": 1}
    assert cmp.canon(dict(e, file="/w/deps/src/fmt-1/include/fmt/f.h", origin="system"), root, outside) == \
        ("src/a.cpp", "_Zf", "../fmt-1/include/fmt/f.h", 3, 5, "project")
    assert cmp.canon(dict(e, file="/usr/include/x.h", origin="system"), root, outside)[5] == "system"
    assert cmp.canon(dict(e, file="_census_driver/s.cpp", origin="project"), root, outside)[5] == "driver"
    assert cmp.canon(dict(e, file="libc++/vector", origin="libc++"), root, outside)[5] == "libc++"


def test_expected_files_match_the_stored_census():
    """expected/*.json is exactly what make_expected.py derives from results/ (no hand edits)."""
    spec = importlib.util.spec_from_file_location("ll_make_expected", os.path.join(LIVE, "make_expected.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for name, (plist, run) in m.SOURCES.items():
        d = os.path.join(REPO, run)
        if not os.path.exists(os.path.join(d, "lost_loops.json")):
            continue  # a clone without results/: nothing to compare against
        lost = json.load(open(os.path.join(d, "lost_loops.json"), encoding="utf-8"))
        ex = load_expected(name)
        for kind in ("lost", "moved", "gained"):
            census = [e for e in lost[kind] if e["project"] == name]
            assert sorted((e["tu"], e["function"], e["file"], e["line"], e["column"], e["count"]) for e in census) == \
                sorted((e["tu"], e["function"], e["file"], e["line"], e["column"], e["count"]) for e in ex[kind]), \
                (name, kind)
