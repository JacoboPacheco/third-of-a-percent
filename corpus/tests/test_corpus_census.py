"""The census logic on a made-up project: matching, lost/moved/gained, totals, the kernel rule."""
import os
import shutil
import tempfile

import _path  # noqa: F401
import census
import schema


def rec(kind, name, func, file, line, col, msg):
    return ("--- !%s\nPass:            loop-vectorize\nName:            %s\n"
            "DebugLoc:        { File: '%s', Line: %d, Column: %d }\nFunction:        %s\nArgs:\n"
            "  - String:          '%s'\n...\n" % (kind, name, file, line, col, func, msg))


VEC = "vectorized loop (vectorization width: 4, interleaved count: 2)"
NOT = "loop not vectorized: could not determine number of loop iterations"

SOURCE = [
    "void f(int* c, const int* a, int n) {",
    "  for (int i = n; i-- > 0;) c[i] = a[i] * 2;",
    "  for (int i = 0; i < n; ++i) c[i] = a[i];",
    "  for (int i = 0; i < n; ++i) c[i] = a[2 * i];",
    "}",
]


def make(tmp):
    root = os.path.join(tmp, "src", "proj")
    os.makedirs(root)
    with open(os.path.join(root, "a.cpp"), "w") as f:
        f.write("\n".join(SOURCE) + "\n")
    work = os.path.join(tmp, "work")
    none = (rec("Passed", "Vectorized", "_Z1fv", "a.cpp", 2, 3, VEC)
            + rec("Passed", "Vectorized", "_Z1fv", "a.cpp", 3, 3, VEC)
            + rec("Passed", "Vectorized", "_Z1fv", "a.cpp", 4, 3, VEC))
    fast = (rec("Analysis", "CantComputeNumberOfIterations", "_Z1fv", "a.cpp", 2, 3, NOT)
            + rec("Passed", "Vectorized", "_Z1fv", "a.cpp", 3, 3, VEC)
            # line 4's loop now sits in another function (inlining changed): moved, not lost
            + rec("Passed", "Vectorized", "_Z1gv", "a.cpp", 4, 3, VEC))
    for mode, text, stderr in (("none", none, 3), ("fast", fast, 2)):
        d = os.path.join(work, "proj", mode)
        os.makedirs(d)
        base = os.path.join(d, "a.cpp")
        with open(base + ".opt.yaml", "w") as f:
            f.write(text)
        with open(base + ".stderr.txt", "w") as f:
            f.write("a.cpp:1:1: remark: vectorized loop (x)\n" * stderr)
        with open(base + ".rc", "w") as f:
            f.write("0")
        with open(base + ".o", "wb") as f:
            f.write(b"")
    proj = {"name": "proj", "kind": "test", "version": "1", "repo": "x", "commit": "c", "root": "proj",
            "downloads": [{"url": "https://example.invalid/p.tar.gz", "sha256": "0" * 64, "bytes": 1}],
            "sources": ["*.cpp"], "exclude": [], "includes": ["."], "defines": []}
    return proj, tmp, work


def test_analyze_project_lost_moved():
    tmp = tempfile.mkdtemp()
    orig = census.objdump_stats
    census.objdump_stats = lambda obj: (3 if "/fast/" in obj.replace("\\", "/") else 1, 100)
    census.EVIDENCE = False  # the evidence pass needs clang and objdump; tested in test_corpus2.py
    try:
        proj, deps, work = make(tmp)
        s, lost, moved, gained = census.analyze_project(proj, deps, work)
    finally:
        census.objdump_stats = orig
        census.EVIDENCE = True
        shutil.rmtree(tmp)
    assert s["none"]["vectorized"] == 3 and s["fast"]["vectorized"] == 2
    assert s["none"]["stderr_vectorized"] == 3
    assert s["lost"] == 1 and s["moved"] == 1 and s["gained"] == 1
    assert lost[0]["line"] == 2 and lost[0]["class"] == "reverse"
    assert lost[0]["fast_remarks"] == [NOT] and lost[0]["none_remark"] == VEC
    assert lost[0]["source_line"] == SOURCE[1].strip()
    assert moved[0]["line"] == 4 and gained[0]["function"] == "_Z1gv"
    assert s["ud2_added"] == 2 and s["lost_by_class"]["reverse"] == 1
    assert s["lost_pct_of_vectorized"] == round(100 / 3, 3)
    assert lost[0]["trip_count"]["kind"] == "other bound"


def test_norm_file():
    assert census.norm_file("/usr/lib/llvm-18/bin/../include/c++/v1/vector", "/r") == ("libc++/vector", "libc++")
    assert census.norm_file("./include/x.h", "/r") == ("include/x.h", "project")
    assert census.norm_file("_census_driver/d.cpp", "/r") == ("_census_driver/d.cpp", "driver")


def test_patterns_rank_and_examples():
    lost = [{"class": "reverse", "detail": "d1", "count": 2, "project": "a", "file": "f", "line": 1, "column": 1,
             "source_line": "x"},
            {"class": "reverse", "detail": "d1", "count": 1, "project": "b", "file": "g", "line": 5, "column": 1,
             "source_line": "y"},
            {"class": "other", "detail": "d2", "count": 1, "project": "a", "file": "f", "line": 9, "column": 1,
             "source_line": "z"}]
    p = census.patterns(lost)
    assert [x["detail"] for x in p] == ["d1", "d2"]
    assert p[0]["count"] == 3 and len(p[0]["examples"]) == 2


def test_deterministic_targz():
    tmp = tempfile.mkdtemp()
    try:
        src = os.path.join(tmp, "f.txt")
        with open(src, "w") as f:
            f.write("hello")
        a, b = os.path.join(tmp, "a.tgz"), os.path.join(tmp, "b.tgz")
        census.deterministic_targz(a, [("x/f.txt", src)])
        census.deterministic_targz(b, [("x/f.txt", src)])
        with open(a, "rb") as fa, open(b, "rb") as fb:
            assert fa.read() == fb.read()
    finally:
        shutil.rmtree(tmp)


def test_projects_json_is_pinned():
    projects = census.load_projects()
    for p in projects:
        assert p["downloads"], p["name"]
        for d in p["downloads"]:
            assert schema.HEX64.match(d["sha256"]) and d["url"].startswith("https://") and d["bytes"] > 0
        if p.get("driver"):
            assert os.path.exists(os.path.join(_path.CORPUS, "drivers", p["driver"]))
    names = [p["name"] for p in projects]
    assert len(names) == len(set(names)) and 12 <= len(names) <= 20


def test_kernel_expectations_cover_all_kernels():
    kdir = os.path.join(_path.REPO, "kernels")
    if os.path.isdir(kdir):
        ks = sorted(f[:-4] for f in os.listdir(kdir) if f.startswith("k0") and f.endswith(".cpp"))
        assert ks == sorted(census.KERNEL_EXPECT)


def test_abi_tag_of_the_hardening_mode_is_normalized():
    assert census.norm_function("_ZNSt3__14copyB8fe180100EPKiS2_Pi") == "_ZNSt3__14copyB8ne180100EPKiS2_Pi"
    assert census.norm_function("_ZNSt3__14copyB8ne180100EPKiS2_Pi") == "_ZNSt3__14copyB8ne180100EPKiS2_Pi"
    assert census.norm_function("_Z3foov") == "_Z3foov"
