"""Tests for tools/lostloops without a compiler: saved real optimization records from the census runs
(tests/data/records, copied from results/corpus-*/remarks.tar.gz), a fake clang that returns them
(tests/fake_clang.py), and the census's own lost_loops.json entries as the expected answers
(tests/data/expected_census.json)."""
import contextlib
import gzip
import io
import json
import os
import shutil
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.dirname(TESTS)
REPO = os.path.dirname(os.path.dirname(TOOL))
DATA = os.path.join(TESTS, "data")
RECORDS = os.path.join(DATA, "records")
KERNELS = os.path.join(REPO, "kernels")
FAKE = os.path.join(TESTS, "fake_clang.py")
if TOOL not in sys.path:
    sys.path.insert(0, TOOL)

import lostloops as ll  # noqa: E402

EXPECTED = json.load(open(os.path.join(DATA, "expected_census.json"), encoding="utf-8"))


def slash(p):
    return p.replace("\\", "/")


def read_record(name):
    p = os.path.join(RECORDS, name)
    if os.path.exists(p + ".gz"):
        with gzip.open(p + ".gz", "rb") as f:
            return f.read().decode("utf-8")
    with open(p, encoding="utf-8") as f:
        return f.read()


@contextlib.contextmanager
def patched(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)


@contextlib.contextmanager
def env(**kw):
    old = {k: os.environ.get(k) for k in kw}
    for k, v in kw.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@contextlib.contextmanager
def quiet():
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        yield out, err


def fake_clang_arg():
    return '"%s" "%s"' % (slash(sys.executable), slash(FAKE))


def match_saved(stem, directory, root, tu):
    paths = {}
    none = ll.read_records(read_record(stem + ".none.opt.yaml"), directory, root, paths)
    fast = ll.read_records(read_record(stem + ".fast.opt.yaml"), directory, root, paths)
    lost, moved, gained = ll.match_unit(tu, none, fast)
    ll.describe(lost + moved + gained, paths)
    return none, fast, lost, moved, gained


SAME = ("tu", "function", "file", "line", "column", "origin", "count", "none_remark", "class", "detail")


def assert_same_as_census(mine, census):
    assert len(mine) == len(census), (len(mine), len(census))
    key = lambda e: (e["function"], e["file"], e["line"], e["column"])  # noqa: E731
    for m, c in zip(sorted(mine, key=key), sorted(census, key=key)):
        for k in SAME:
            assert m[k] == c[k], (k, m[k], c[k])
        assert m["hardened_remarks"] == c["fast_remarks"]
        assert m["source_line"] == c["source_line"] and m["context"] == c["context"]
        if "trip_count" in c:
            assert m["trip_count"] == c["trip_count"]


# ---------------------------------------------------------------- records, matching, the ABI tag

def test_saved_record_parses():
    recs = ll.optrecord.loop_vectorize(ll.optrecord.parse(read_record("k04_rev.cpp.none.opt.yaml")))
    vec = [r for r in recs if ll.optrecord.is_vectorized(r)]
    assert [(r["loc"]["file"], r["loc"]["line"], r["loc"]["column"]) for r in vec
            if r["function"].startswith("_Z12kern_k04_rev")] == [("k04_rev.cpp", 5, 3)]


def test_abi_tag_mapping():
    none = "_ZNSt3__16vectorIiNS_9allocatorIiEEEixB8ne180100Em"
    for tag in ("fe180100", "se180100", "de180100", "ne180100"):
        assert ll.norm_function(none.replace("ne180100", tag)) == none
    assert ll.norm_function("_Z3foov") == "_Z3foov"
    assert ll.norm_function("_ZNSt3__14spanIiLm18446744073709551615EEixB8fe190000Em").endswith("B8ne190000Em")


def test_abi_tag_mapping_matters_on_real_records():
    """ninja's src/dyndep.cc (census 1, run 38259934735; ninja lost nothing) has 2 loops vectorized in
    libc++ functions whose name carries the mode ([abi:ne180100] / [abi:fe180100]). With the mapping
    nothing is lost, moved or gained; without it both would count as moved and gained (the same source
    location, a "different" function)."""
    root = "/ninja"
    assert "B8fe180100" in read_record("dyndep.cc.fast.opt.yaml")
    _, _, lost, moved, gained = match_saved("dyndep.cc", root, root, "src/dyndep.cc")
    assert (lost, moved, gained) == ([], [], [])
    with patched(ll, "norm_function", lambda m: m):
        _, _, lost_raw, moved_raw, gained_raw = match_saved("dyndep.cc", root, root, "src/dyndep.cc")
    assert lost_raw == []
    assert sum(e["count"] for e in moved_raw) == 2 and sum(e["count"] for e in gained_raw) == 2
    assert all("B8ne180100" in e["function"] for e in moved_raw)
    assert all("B8fe180100" in e["function"] for e in gained_raw)


def test_spectra_equals_census():
    """Census 2 (run 38273183229, baseline): spectra, 79 vectorized NONE, 75 FAST, 4 lost, 0 moved,
    0 gained; each lost entry equal field by field to lost_loops.json."""
    root = slash(os.path.join(DATA, "src", "spectra"))
    none, fast, lost, moved, gained = match_saved("spectra.cpp", root, root, "_census_driver/spectra.cpp")
    s = EXPECTED["spectra"]["summary"]
    assert sum(none[0].values()) == s["none_vectorized"] == 79
    assert sum(fast[0].values()) == s["fast_vectorized"] == 75
    assert len({k[1:4] for k in none[0]}) == s["none_vectorized_unique"]
    assert (len(moved), len(gained)) == (s["moved"], s["gained"]) == (0, 0)
    assert_same_as_census(lost, EXPECTED["spectra"]["lost"])
    assert {e["shape"] for e in lost} == {"forward, bounded by a variable"}


def test_leveldb_equals_census():
    """Census 1 (run 38259934735): leveldb's one lost loop, db/c.cc:117."""
    root = slash(os.path.join(DATA, "src", "leveldb"))
    _, _, lost, moved, gained = match_saved("c.cc", root, root, "db/c.cc")
    assert not moved and not gained
    assert_same_as_census(lost, EXPECTED["leveldb_db_c"]["lost"])


def test_kernels_equal_census_from_records():
    root = slash(KERNELS)
    lost = []
    for k in ("k01_sum_fwd", "k02_add_fwd", "k03_stencil", "k04_rev", "k05_stride2", "k06_gather",
              "k07_hist", "k08_matmul"):
        _, _, lo, _, _ = match_saved(k + ".cpp", root, root, k + ".cpp")
        lost += lo
    assert_same_as_census(lost, EXPECTED["kernels"]["lost"])
    assert sorted((e["file"], e["shape"]) for e in lost) == [
        ("k04_rev.cpp", "reverse index"), ("k05_stride2.cpp", "strided"), ("k08_matmul.cpp", "strided")]


def test_norm_file_origins():
    assert ll.norm_file("/usr/lib/llvm-18/bin/../include/c++/v1/vector", "/p") == ("libc++/vector", "libc++")
    assert ll.norm_file("/p/src/a.cpp", "/p") == ("src/a.cpp", "project")
    assert ll.norm_file("/pp/a.cpp", "/p") == ("/pp/a.cpp", "system")
    assert ll.resolve("../eigen/x.h", "/p/build") == "/p/eigen/x.h"
    assert ll.resolve("C:\\p\\a.cpp", "/x") == "C:/p/a.cpp"


# ---------------------------------------------------------------- flags

def test_clean_args_keeps_flags_as_given():
    args = ["-O3", "-DNDEBUG", "-Iinclude", "-std=c++20", "-stdlib=libstdc++", "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST",
            "-D", "_LIBCPP_HARDENING_MODE=1", "-MD", "-MT", "x.o", "-MF", "x.d", "-o", "x.o", "-c", "src/a.cpp",
            "-march=native", "-fsave-optimization-record", "-foptimization-record-file=y"]
    kept, removed = ll.clean_args(args)
    assert kept == ["-O3", "-DNDEBUG", "-Iinclude", "-std=c++20", "src/a.cpp", "-march=native"]
    assert "-stdlib=libstdc++" in removed and "x.d" in removed
    assert ll.has_opt_level(kept) and not ll.has_opt_level(["-std=c++20"])
    assert ll.strip_compiler(["/usr/bin/ccache", "g++", "-O2", "a.cpp"]) == ["-O2", "a.cpp"]
    assert ll.is_cxx("/p/a.cpp", []) and not ll.is_cxx("/p/a.c", []) and ll.is_cxx("/p/a.h", ["-x", "c++"])


def test_build_cmd_adds_only_the_allowed_flags():
    t = ll.Tools(["clang++-18"])
    u = {"directory": "/p", "file": "/p/a.cpp", "args": ["-O2", "-c", "a.cpp", "-o", "a.o", "--", "b"]}
    cmd = ll.build_cmd(t, u, "extensive", "/t/a.o", "/t/a.yaml")
    assert cmd == ["clang++-18", "-stdlib=libc++", "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_EXTENSIVE",
                   "-fsave-optimization-record", "-foptimization-record-passes=loop-vectorize",
                   "-foptimization-record-file=/t/a.yaml", "-c", "-o", "/t/a.o", "-O2", "a.cpp", "--", "b"]


# ---------------------------------------------------------------- the whole tool, with the fake clang

def write_kernel_db(tmp, flags=("-O2", "-std=c++20", "-I.")):
    db = []
    for k in sorted(os.listdir(KERNELS)):
        if k.startswith("k0") and k.endswith(".cpp"):
            db.append({"directory": slash(KERNELS), "file": k,
                       "arguments": ["/usr/bin/clang++"] + list(flags) + ["-o", "CMakeFiles/" + k + ".o", "-c", k]})
    db.append({"directory": slash(KERNELS), "file": "common.c", "command": "cc -O2 -c common.c"})  # C: skipped
    path = os.path.join(tmp, "compile_commands.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f)
    return path


def test_end_to_end_with_fake_clang_matches_census():
    tmp = tempfile.mkdtemp()
    try:
        cc = write_kernel_db(tmp)
        out = os.path.join(tmp, "report")
        log = os.path.join(tmp, "calls")
        os.makedirs(log)
        with env(FAKE_CLANG_DATA=RECORDS, FAKE_CLANG_LOG=log, FAKE_CLANG_NO_LIBCXX=None), quiet() as (so, _):
            rc = ll.main(["--compile-commands", cc, "--clang", fake_clang_arg(), "--objdump", "none",
                          "--out", out, "--jobs", "2", "--root", KERNELS])
        assert rc == 0
        rep = json.load(open(os.path.join(out, "report.json"), encoding="utf-8"))
        t = rep["totals"]
        assert (t["files_in_input"], t["files_compiled"], t["files_failed"]) == (8, 8, 0)
        assert t["lost"] == 3 and t["lost_locations"] == 3 and t["lost_locations_in_project"] == 3
        assert t["traps_added"] is None and t["text_change_pct"] is None
        assert t["lost_by_shape"]["reverse index"] == 1 and t["lost_by_shape"]["strided"] == 2
        assert [r["where"] for r in rep["lost_by_location"]] == ["k04_rev.cpp:5:3", "k05_stride2.cpp:5:3",
                                                                 "k08_matmul.cpp:11:7"]
        assert all(e["check"]["status"] == "not traced (objdump not found)" for e in rep["lost"])
        assert all(r["what_to_try"] for r in rep["lost_by_location"])
        assert "rbegin()/rend()" in rep["lost_by_location"][0]["what_to_try"]
        assert "row" in rep["lost_by_location"][2]["what_to_try"]
        assert rep["no_opt_level"] == []
        assert_same_as_census(rep["lost"], EXPECTED["kernels"]["lost"])
        # the flags: each compile is the user's flags as given, with only the allowed additions
        calls = [json.load(open(os.path.join(log, x), encoding="utf-8")) for x in os.listdir(log)]
        compiles = [c["args"] for c in calls if "-fsyntax-only" not in c["args"] and "--version" not in c["args"]]
        assert len(compiles) == 16
        for a in compiles:  # the fake logs its arguments without the compiler itself
            assert a[0] == "-stdlib=libc++" and a[2:4] == ["-fsave-optimization-record",
                                                           "-foptimization-record-passes=loop-vectorize"]
            assert a[1] in ("-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE",
                            "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST")
            assert a[4].startswith("-foptimization-record-file=") and a[5:7] == ["-c", "-o"]
            assert a[8:] == ["-O2", "-std=c++20", "-I.", a[-1]] and a[-1].startswith("k0")
        text = so.getvalue()
        assert "LOST under FAST: 3" in text and ll.DISCLAIMER in text
        md = open(os.path.join(out, "report.md"), encoding="utf-8").read()
        assert ll.DISCLAIMER in md and "k04_rev.cpp:5:3" in md and "not measured" in md
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_files_mode_notes_missing_opt_level_and_failures():
    tmp = tempfile.mkdtemp()
    cwd = os.getcwd()
    try:
        bad = os.path.join(tmp, "nocanned.cpp")
        open(bad, "w").write("int x;\n")
        os.chdir(KERNELS)
        with env(FAKE_CLANG_DATA=RECORDS, FAKE_CLANG_LOG=None), quiet() as (so, _):
            rc = ll.main(["--files", "k04_rev.cpp", slash(bad), "--clang", fake_clang_arg(), "--objdump", "none",
                          "--out", os.path.join(tmp, "r"), "--root", KERNELS, "--", "-std=c++20"])
        assert rc == 0
        rep = json.load(open(os.path.join(tmp, "r", "report.json"), encoding="utf-8"))
        assert rep["no_opt_level"] and rep["no_opt_level"][0] == "k04_rev.cpp"
        assert rep["totals"]["files_failed"] == 1 and "no canned record" in rep["failed"][0]["error"]
        assert rep["totals"]["lost"] == 1 and rep["lost"][0]["shape"] == "reverse index"
        assert "no -O level" in so.getvalue()
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmp, ignore_errors=True)


def test_missing_clang_or_libcxx_exits_2():
    tmp = tempfile.mkdtemp()
    try:
        cc = write_kernel_db(tmp)
        with quiet() as (_, err):
            rc = ll.main(["--compile-commands", cc, "--clang", "no-such-clang-xyz", "--out", os.path.join(tmp, "r")])
        assert rc == 2 and "clang not found" in err.getvalue()
        with env(PATH=tmp, LOSTLOOPS_CLANG=None), quiet() as (_, err):
            rc = ll.main(["--compile-commands", cc, "--out", os.path.join(tmp, "r")])
        assert rc == 2 and "clang++ not found" in err.getvalue()
        with env(FAKE_CLANG_DATA=RECORDS, FAKE_CLANG_NO_LIBCXX="1"), quiet() as (_, err):
            rc = ll.main(["--compile-commands", cc, "--clang", fake_clang_arg(), "--out", os.path.join(tmp, "r")])
        assert rc == 2 and "libc++" in err.getvalue()
        with quiet() as (_, err):
            rc = ll.main(["--compile-commands", os.path.join(tmp, "missing.json"), "--out", os.path.join(tmp, "r")])
        assert rc == 2 and "cannot read" in err.getvalue()
        assert not os.path.exists(os.path.join(tmp, "r"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- objdump and trap tracing (canned output)

OBJDUMP_D = """
x.o:     file format elf64-x86-64

Disassembly of section .text:

0000000000000000 <_Z4kernv>:
   0:\tmov    (%rdi),%rax
  13:\tud2
  20:\tud2
"""
OBJDUMP_H = """
x.o:     file format elf64-x86-64

Sections:
Idx Name          Size      VMA               LMA               File off  Algn
  0 .text         00000040  0000000000000000  0000000000000000  00000040  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  1 .text._Z4kernv 00000010  0000000000000000  0000000000000000  00000080  2**4
  2 .data         00000008  0000000000000000  0000000000000000  00000090  2**3
"""

# The census's own test fixture (corpus/tests/test_corpus2.py): objdump -l --inlines of an evidence object.
DUMP_L = """
0000000000000000 <_Z4kernRNSt3__16vectorIiNS_9allocatorIiEEEE>:
_Z4kernRNSt3__16vectorIiNS_9allocatorIiEEEE():
/r/k.cpp:4
   0:\tmov    (%rdi),%rax
/usr/lib/llvm-18/bin/../include/c++/v1/vector:1393 (discriminator 1)
inlined by /r/k.cpp:5
  10:\tcmp    %rcx,%rdx
  13:\tcall   18 <_Z4kernRNSt3__16vectorIiNS_9allocatorIiEEEE+0x18>
\t\t\t14: R_X86_64_PLT32\t__census_trap-0x4
/r/k.cpp:9
  20:\tud2
"""
LIBCXX_VECTOR = ["x"] * 1392 + ['    _LIBCPP_ASSERT_VALID_ELEMENT_ACCESS(__n < size(), "vector[] index out of bounds");']
SRC = ["#include <vector>", "", "", "int kern(std::vector<int>& a) {",
       "  for (size_t i = a.size(); i-- > 0;)", "    a[i] += 1;", "  return 0;", "}", "  x;"]


def test_objdump_parsers():
    assert ll.parse_ud2(OBJDUMP_D) == 2
    assert ll.parse_text_bytes(OBJDUMP_H) == 0x50


class _R:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def test_trace_unit_finds_the_vector_check():
    """The trap tracing with canned tool output: the link fails, so objdump -l --inlines on the object
    is used (the census's fallback); the vector[] check inlined at k.cpp:5 is inside the loop."""
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        if "-fuse-ld=bfd" in cmd:
            return _R(1, err="ld: cannot link")
        if cmd[0] == "objdump":
            return _R(0, DUMP_L)
        return _R(0)  # the traced rebuild
    lines = {"/usr/lib/llvm-18/bin/../include/c++/v1/vector": LIBCXX_VECTOR, "/r/k.cpp": SRC}
    tmp = tempfile.mkdtemp()
    try:
        with patched(ll, "run", fake_run), patched(ll, "source_lines", lambda p: lines.get(p, [])):
            e = {"function": "_Z4kernRNSt3__16vectorIiNS_9allocatorIiEEEE", "file": "k.cpp", "line": 5, "column": 3,
                 "origin": "project"}
            t = ll.Tools(["clang++-18"], objdump="objdump", symbolizer="llvm-symbolizer-18")
            ll.trace_unit(t, {"directory": "/r", "file": "/r/k.cpp", "args": ["-O2", "k.cpp"]}, 0, "fast", tmp, [e],
                          "/r", {"k.cpp": "/r/k.cpp"})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    assert e["check"]["status"] == "check traced to the loop"
    assert e["check"]["messages"] == ["vector[] index out of bounds"]
    assert e["check"]["example_chain"] == ["libc++/vector:1393", "k.cpp:5"]
    assert e["check"]["checks_in_function"] == 2 and e["check"]["attributed_checks"] == 1
    rebuild = calls[0]
    assert "-gline-tables-only" in rebuild and any(a.startswith("-I") and a.endswith("evidence") for a in rebuild)


def test_shapes_and_what_to_try():
    assert ll.shape_of("reverse", "counter counts down (i--, --i)") == "reverse index"
    assert ll.shape_of("other", "forward loop bounded by a variable, not the container's size()") == \
        "forward, bounded by a variable"
    assert ll.shape_of("other", "early exit (break/return or a compound condition)") == "other"
    assert ll.what_to_try("strided", "multiplied index ([2 * i], [i * n + j])") == ll.TRY["strided-matrix"]
    assert ll.what_to_try("strided", "step other than 1 (i += k)") == ll.TRY["strided"]
    for s in ll.SHAPES:
        assert ll.TRY[s]


def test_example_workflow_is_documentation_only():
    wf = os.path.join(TOOL, "example-workflow.yml")
    text = open(wf, encoding="utf-8").read()
    assert "lostloops.py" in text and "compile_commands.json" in text
    assert not os.path.exists(os.path.join(REPO, ".github", "workflows", "example-workflow.yml"))
    readme = open(os.path.join(TOOL, "README.md"), encoding="utf-8").read()
    assert "tested live once" in readme and "one run on three projects" in readme
