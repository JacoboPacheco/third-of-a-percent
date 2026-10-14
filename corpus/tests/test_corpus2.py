"""Census 2 additions: trip counts, the trap-tracing evidence, shard merging, the project list."""
import json
import os
import shutil
import tarfile
import tempfile

import _path  # noqa: F401
import census
import classify
import merge
import schema

DUMP = """
x.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000 <_Z4kernRNSt3__16vectorIiNS_9allocatorIiEEEE>:
_Z4kernRNSt3__16vectorIiNS_9allocatorIiEEEE():
/r/k.cpp:4
   0:\tmov    (%rdi),%rax
/usr/lib/llvm-18/bin/../include/c++/v1/vector:1393 (discriminator 1)
inlined by /r/k.cpp:5
  10:\tcmp    %rcx,%rdx
  13:\tud2
/r/k.cpp:9
  20:\tud2

0000000000000000 <_Z5checkv>:
/r/c.cpp:3
   0:	mov    %rdi,%rax
/usr/lib/llvm-18/bin/../include/c++/v1/vector:1393
inlined by /r/c.cpp:4
   4:	call   9 <_Z5checkv+0x9>
			5: R_X86_64_PLT32	__census_trap-0x4
   9:	ret

0000000000000000 <_Z5otherv>:
_Z5otherv():
/r/k.cpp:20
   0:\tret
"""

LIBCXX_VECTOR = ["x"] * 1392 + ['    _LIBCPP_ASSERT_VALID_ELEMENT_ACCESS(__n < size(), "vector[] index out of bounds");']


def test_parse_objdump_lines_chains():
    d = census.parse_objdump_lines(DUMP)
    k = d["_Z4kernRNSt3__16vectorIiNS_9allocatorIiEEEE"]
    ud2 = [c for mn, c in k if mn == "ud2"]
    assert ud2[0] == (("/usr/lib/llvm-18/bin/../include/c++/v1/vector", 1393), ("/r/k.cpp", 5))
    assert ud2[1] == (("/r/k.cpp", 9),)
    assert [mn for mn, _ in d["_Z5otherv"]] == ["ret"]


def test_libcxx_assertion_message():
    assert census.libcxx_assertion(LIBCXX_VECTOR, 1393) == "vector[] index out of bounds"
    assert census.libcxx_assertion(["int x;"] * 10, 5) is None
    assert census.container_of("vector[] index out of bounds") == "std::vector"
    assert census.container_of("span<T>::operator[](index): index out of range") == "std::span"


def test_evidence_for_attributes_trap_in_loop(monkeypatch=None):
    orig = census.source_lines
    src = ["#include <vector>", "", "", "int kern(std::vector<int>& a) {",
           "  for (size_t i = a.size(); i-- > 0;)", "    a[i] += 1;", "  return 0;", "}", "  x;"]

    def fake(path):
        return LIBCXX_VECTOR if path.replace("\\", "/").endswith("c++/v1/vector") else src
    census.source_lines = fake
    try:
        d = census.parse_objdump_lines(DUMP)
        chains = census.trap_chains(d, "_Z4kernRNSt3__16vectorIiNS_9allocatorIiEEEE")
        e = {"file": "k.cpp", "origin": "project", "line": 5, "column": 3}
        ev = census.evidence_for(e, chains, "/r", True)
    finally:
        census.source_lines = orig
    assert ev["status"] == "checked container access in the loop"
    assert ev["messages"] == ["vector[] index out of bounds"] and ev["containers"] == ["std::vector"]
    assert ev["attributed_traps"] == 1 and ev["traps_in_function"] == 2
    assert ev["example_chain"] == ["libc++/vector:1393", "k.cpp:5"]


def test_evidence_for_no_trap_in_loop():
    orig = census.source_lines
    census.source_lines = lambda path: ["for (int i = 0; i < n; ++i) a[i] = b[i];"] * 30
    try:
        ev = census.evidence_for({"file": "k.cpp", "origin": "project", "line": 3, "column": 1},
                                 [(("/r/k.cpp", 20),)], "/r", True)
    finally:
        census.source_lines = orig
    assert ev["status"] == "no trap attributed to this loop" and ev["traps_in_function"] == 1


def test_trip_count_kinds():
    assert classify.trip_count(["for (size_t i = 0; i < v.size(); ++i)"])["kind"] == "container size()"
    assert classify.trip_count(["for (int i = 0; i < n; i++) {"])["kind"] == "other bound"
    assert classify.trip_count(["for (int i = 0; i < n; i++) {"])["bound"] == "i < n"
    assert classify.trip_count(["for (auto& x : v) s += x;"])["kind"] == "range or iterator loop"
    assert classify.trip_count(["for (auto it = v.begin(); it != v.end(); ++it)"])["kind"] == "range or iterator loop"
    assert classify.trip_count(["while (p < end) *p++ = 0;"])["kind"] == "other bound"
    assert classify.trip_count(["  x += a[i];"])["kind"] == "not a for/while header"


def test_kernel_avx2_expectations():
    assert census.KERNEL_EXPECT_AVX2["k06_gather"] == {"neither", "lost"}
    assert census.KERNEL_EXPECT_AVX2["k04_rev"] == {"lost"}
    assert census.TARGETS["avx2"] == ["-march=x86-64-v3"] and census.TARGETS["baseline"] == []


def test_compile_cmd_target():
    p = {"includes": ["inc"], "defines": ["A=1"]}
    census.TARGET = "avx2"
    try:
        cmd = census.compile_cmd(p, "a.cpp", "fast", "a.o", "a.yaml")
    finally:
        census.TARGET = "baseline"
    assert "-march=x86-64-v3" in cmd and cmd[-4:] == ["-c", "a.cpp", "-o", "a.o"]
    assert "-march=x86-64-v3" not in census.compile_cmd(p, "a.cpp", "fast", "a.o", "a.yaml")


def test_projects2_is_pinned_and_sharded():
    projects = census.load_projects(file="projects2.json")
    names = [p["name"] for p in projects]
    assert len(names) == len(set(names)) and 20 <= len(names) <= 30
    for p in projects:
        assert p["category"] and p["why"] and p.get("shard") in (1, 2, 3, 4, 5), p["name"]
        for d in p["downloads"]:
            assert schema.HEX64.match(d["sha256"]) and d["url"].startswith("https://") and d["bytes"] > 0
        if p.get("driver"):
            assert os.path.exists(os.path.join(_path.CORPUS, "drivers", p["driver"])), p["driver"]
    files = [d["file"] for p in projects for d in p["downloads"]]
    by_file = {}
    for p in projects:
        for d in p["downloads"]:
            assert by_file.setdefault(d["file"], d["sha256"]) == d["sha256"], d["file"]
    assert sum(len(census.load_projects(file="projects2.json", shard=k)) for k in (1, 2, 3, 4, 5)) == len(projects)
    assert files


def test_generate_cmakedefine():
    tmp = tempfile.mkdtemp()
    try:
        root = os.path.join(tmp, "src", "p")
        os.makedirs(root)
        with open(os.path.join(root, "c.h.in"), "w") as f:
            f.write("#cmakedefine A\n#cmakedefine B\n#cmakedefine01 C\n#define V @V@\n")
        p = {"name": "p", "root": "p", "downloads": [], "generate": {
            "gen/c.h": {"from": "c.h.in", "replace": {"@V@": "3"}, "cmakedefine": {"A": 1},
                        "cmakedefine01": {"C": 1}},
            "gen/d.h": {"content": "#define D 1\n"}}}
        census.fetch([p], tmp)
        with open(os.path.join(root, "gen", "c.h")) as f:
            assert f.read() == "#define A\n/* #undef B */\n#define C 1\n#define V 3\n"
        with open(os.path.join(root, "gen", "d.h")) as f:
            assert f.read() == "#define D 1\n"
    finally:
        shutil.rmtree(tmp)


def _shard(tmp, name, project, lost_count, kernels):
    d = os.path.join(tmp, name)
    os.makedirs(d)
    mode = {"vectorized": 10, "vectorized_unique": 9, "loops_reported": 20, "ud2": 1, "text_bytes": 100,
            "stderr_vectorized": 10, "vectorized_by_origin": {o: 0 for o in census.ORIGINS}}
    fast = dict(mode, vectorized=10 - lost_count, stderr_vectorized=10 - lost_count, ud2=3, text_bytes=110)
    lost = [{"project": project, "tu": "a.cpp", "function": "_Z1fv", "function_name": "f()", "file": "a.cpp",
             "line": 3, "column": 3, "origin": "project", "count": 1, "none_remark": "v", "fast_remarks": [],
             "class": "reverse", "detail": "d", "source_line": "for", "context": ["for"],
             "trip_count": {"kind": "other bound", "bound": "i"},
             "index_evidence": {"status": "checked container access in the loop"}}] * lost_count
    s = {"name": project, "category": "c", "kind": "k", "version": "1", "commit": "c", "repo": "r",
         "downloads": [{"url": "https://x", "sha256": "0" * 64, "bytes": 1}], "translation_units": 1,
         "compiled": 1, "failed": [], "none": mode, "fast": fast, "lost": lost_count, "moved": 0, "gained": 0,
         "lost_pct_of_vectorized": census.pct(lost_count, 10), "ud2_added": 2, "text_bytes_change_pct": 10.0,
         "lost_by_class": dict({c: 0 for c in classify.CLASSES}, reverse=lost_count),
         "lost_by_origin": dict({o: 0 for o in census.ORIGINS}, project=lost_count),
         "lost_with_index_evidence": lost_count}
    c = {"schema": "corpus-2", "projects_file": "projects2.json", "shards": [int(name[-1])], "target": "baseline",
         "toolchain": {}, "source": {}, "projects": [s], "dropped": [], "totals": {}, "patterns": [],
         "controls": {"kernels": kernels, "remark_crosscheck": {"rule": "r", "pass": True, "per_project": {
             project: {"none": [10, 10], "fast": [10 - lost_count, 10 - lost_count]},
             "kernels": {"none": [5, 5], "fast": [2, 2]}}}}, "limits": []}
    with open(os.path.join(d, "census.json"), "w") as f:
        json.dump(c, f)
    with open(os.path.join(d, "lost_loops.json"), "w") as f:
        json.dump({"schema": "corpus-lost-2", "lost": lost, "moved": [], "gained": [], "kernels_lost": []}, f)
    with open(os.path.join(d, "objects.sha256"), "w") as f:
        f.write("%s  %s/none/a.o\n%s  kernels/none/k.o\n" % ("1" * 64, project, "2" * 64))
    src = os.path.join(d, "r.txt")
    with open(src, "w") as f:
        f.write(project)
    census.deterministic_targz(os.path.join(d, "remarks.tar.gz"), [(project + "/r.txt", src)])
    return d


def test_merge_shards():
    tmp = tempfile.mkdtemp()
    try:
        k = {"pass": True, "kernels": [{}] * 8}
        names = [p["name"] for p in census.load_projects(file="projects2.json")]
        a = _shard(tmp, "s-2", names[1], 2, k)
        b = _shard(tmp, "s-1", names[0], 1, k)
        out = os.path.join(tmp, "out")
        assert merge.merge([a, b], out) == []
        c = json.load(open(os.path.join(out, "census.json")))
        assert [p["name"] for p in c["projects"]] == names[:2] and c["shards"] == [1, 2]
        assert c["totals"]["lost"] == 3 and c["totals"]["none"]["vectorized"] == 20
        assert c["totals"]["lost_with_index_evidence"] == 3
        c["controls"]["determinism"] = {"pass": True}
        lost = json.load(open(os.path.join(out, "lost_loops.json")))
        assert schema.check_corpus(c, lost) == []
        lines = open(os.path.join(out, "objects.sha256")).read().splitlines()
        assert len(lines) == 3 and lines == sorted(lines, key=lambda x: x.split("  ")[1])
        with tarfile.open(os.path.join(out, "remarks.tar.gz")) as t:
            assert sorted(t.getnames()) == sorted([names[0] + "/r.txt", names[1] + "/r.txt"])
        k2 = {"pass": False, "kernels": []}
        c3 = _shard(tmp, "s-3", names[2], 0, k2)
        assert merge.merge([a, b, c3], os.path.join(tmp, "out2"))  # kernel controls disagree
    finally:
        shutil.rmtree(tmp)


def test_parse_objdump_census_trap_call():
    d = census.parse_objdump_lines(DUMP)
    assert [mn for mn, _ in d["_Z5checkv"]] == ["mov", "check", "ret"]
    assert census.trap_chains(d, "_Z5checkv") == [(("/usr/lib/llvm-18/bin/../include/c++/v1/vector", 1393),
                                                  ("/r/c.cpp", 4))]


def test_project_std_override():
    p = {"includes": [], "defines": [], "std": "c++17"}
    cmd = census.compile_cmd(p, "a.cpp", "none", "a.o", "a.yaml")
    assert "-std=c++17" in cmd and "-std=c++20" not in cmd


LINKED = """
0000000000001100 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1100:\tmov    (%rsi),%rax
    1110:\tcall   1030 <__census_trap@plt>
    1115:\tud2
    1117:\tret
"""

SYMB = """_ZNSt3__16vectorIiNS_9allocatorIiEEEixB8fe180100Em
/usr/lib/llvm-18/bin/../include/c++/v1/vector:1393:5
_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_
/r/k04_rev.cpp:5:53

_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_
??:0:0

"""


def test_parse_linked_checks_and_symbolizer():
    d = census.parse_objdump_checks(LINKED)
    assert d["_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_"] == [0x1110, 0x1115]
    ch = census.parse_symbolizer(SYMB)
    assert ch == [(("/usr/lib/llvm-18/bin/../include/c++/v1/vector", 1393), ("/r/k04_rev.cpp", 5)), ()]
