"""Tests of the sweep's parsers and pairing. Offline: synthetic snippets plus the cached clang 18 answers.

    python ce-sweep/check.py      (runs these too)
    python -m pytest ce-sweep     (if pytest is installed)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cesweep as cs  # noqa: E402


def test_clang_remarks_with_colour_codes():
    resp = {"stderr": [
        {"text": "\x1b[1m<source>:9:3: \x1b[0m\x1b[0;1;34mremark: \x1b[0m\x1b[1mvectorized loop (vectorization "
                 "width: 4, interleaved count: 2) [-Rpass=loop-vectorize]\x1b[0m"},
        {"text": "<source>:23:3: remark: loop not vectorized: could not determine number of loop iterations "
                 "[-Rpass-analysis=loop-vectorize]"},
        {"text": "    9 |   for (...)  // LOOP"}]}
    text = cs.stderr_text(resp)
    v = cs.vectorization(text, 9, "clang")
    assert v["vectorized"] is True and v["width"] == 4 and v["interleave"] == 2
    v = cs.vectorization(text, 23, "clang")
    assert v["vectorized"] is False and v["width"] is None
    assert cs.vectorization(text, 44, "clang")["vectorized"] is None  # nothing said about that line


def test_clang_scalable_width_kept_as_text():
    text = "<source>:9:3: remark: vectorized loop (vectorization width: vscale x 4, interleaved count: 1) [-Rpass]"
    v = cs.vectorization(text, 9, "clang")
    assert v["vectorized"] is True and v["width"] == "vscale x 4" and v["interleave"] == 1


def test_gcc_remarks():
    text = ("<source>:23:33: optimized: loop vectorized using 16 byte vectors\n"
            "<source>:23:33: optimized:  loop versioned for vectorization because of possible aliasing\n"
            "<source>:23:33: optimized: loop vectorized using 8 byte vectors\n"
            "<source>:15:3: optimized: basic block part vectorized using 16 byte vectors\n")
    v = cs.vectorization(text, 23, "gcc")
    assert v["vectorized"] is True and v["vector_bytes"] == 16
    assert cs.vectorization(text, 15, "gcc")["vectorized"] is False  # SLP is not loop vectorization
    assert cs.vectorization(text, 99, "gcc")["vectorized"] is False  # GCC reports successes only


def test_split_functions_handles_gcc16_quotes_and_cold_parts():
    lines = ['.LC0:', '        .string "x"',
             'kern_k01_sum_fwd(std::vector<int> const&):', '        ret',
             '"kern_k02_add_fwd(std::vector<int>&)":', '        jnb     .L18', '        ret',
             '"kern_k02_add_fwd(std::vector<int>&) (.cold)":', '.L18:',
             '        call    std::vector<int>::operator[](unsigned long) (.part.0)',
             'main:', '        ud2']
    f = cs.split_functions(lines)
    assert set(f) == {"k01_sum_fwd", "k02_add_fwd"}
    c = cs.asm_counts(f["k02_add_fwd"], "x86")
    assert c["abort_calls"] == 1 and c["traps"] == 0
    assert cs.asm_counts(f["k01_sum_fwd"], "x86")["traps"] == 0  # the ud2 under main is not counted


def test_asm_counts_traps_and_simd():
    x86 = ["        movdqu  xmm0, XMMWORD PTR [rsi]", "        paddd   xmm0, xmm1", "        movd    eax, xmm0",
           "        ud2"]
    c = cs.asm_counts(x86, "x86")
    assert c["traps"] == 1 and c["simd_instr"] == 2
    arm = ["        ldr     q0, [x8]", "        add     v0.4s, v0.4s, v1.4s", "        brk     #0x1",
           "        bl      std::__1::__libcpp_verbose_abort(char const*, ...)"]
    c = cs.asm_counts(arm, "arm")
    assert c["traps"] == 1 and c["simd_instr"] == 2 and c["abort_calls"] == 1


def test_hardening_macro_per_library_version():
    assert cs.hardening_flags("clang", "16.0.0", "hardened")[0] == "-D_LIBCPP_ENABLE_ASSERTIONS=1"
    assert cs.hardening_flags("clang", "17.0.1", "hardened")[0] == "-D_LIBCPP_ENABLE_HARDENED_MODE=1"
    assert cs.hardening_flags("clang", "18.1.0", "hardened")[0] == \
        "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"
    assert cs.hardening_flags("clang", "trunk", "none")[0] == "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE"
    assert cs.hardening_flags("gcc", "14.4", "hardened")[0] == "-D_GLIBCXX_ASSERTIONS"
    assert cs.hardening_flags("gcc", "14.4", "none")[0] == ""


def test_matrix_shape():
    m = cs.matrix()
    assert len(m) == 168
    assert len({cs.cache_name(b) for b in m}) == 168
    assert all("-stdlib=libc++" in b["flags"] for b in m if b["family"] == "clang")
    assert not any("libc++" in b["flags"] for b in m if b["family"] == "gcc")


def test_source_is_the_kernels_verbatim():
    src = cs.build_source()
    lines = cs.loop_lines(src)
    assert list(lines) == cs.KERNELS
    for k in cs.KERNELS:
        with open(os.path.join(cs.REPO, "kernels", k + ".cpp"), encoding="utf-8") as f:
            assert cs.extract_kernel(f.read(), k) in src
    assert "int main" not in src


def _fake(vec_lines, family="clang"):
    if family == "clang":
        err = "\n".join("<source>:%d:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [x]" % ln
                        for ln in vec_lines)
        lines = cs.loop_lines(cs.build_source())
        err += "\n" + "\n".join("<source>:%d:3: remark: loop not vectorized [x]" % ln
                                for ln in lines.values() if ln not in vec_lines)
    asm = []
    for k in cs.KERNELS:
        asm += [{"text": "kern_%s(int):" % k}, {"text": "        ret"}]
    return {"code": 0, "stderr": [{"text": t} for t in err.splitlines()], "asm": asm}


def test_lost_needs_vectorized_unhardened_and_scalar_hardened():
    src = cs.build_source()
    L = cs.loop_lines(src)
    b = [x for x in cs.matrix() if x["compiler_id"] == "clang1810" and x["target"] == "x86-64" and x["opt"] == "-O2"]
    none_b = [x for x in b if x["mode"] == "none"][0]
    hard_b = [x for x in b if x["mode"] == "hardened"][0]
    all_vec = list(L.values())
    hard_vec = [L[k] for k in cs.KERNELS if k not in ("k04_rev", "k06_gather")]
    cells = cs.cells([(none_b, _fake([L[k] for k in cs.KERNELS if k != "k06_gather"])), (hard_b, _fake(hard_vec))], src)
    lost = [c["kernel"] for c in cells if c["lost"]]
    assert lost == ["k04_rev"]  # gather is scalar in both, so not lost
    # A failed compile gives lost = None, never False.
    bad = {"code": 1, "stderr": [], "asm": []}
    cells = cs.cells([(none_b, _fake(all_vec)), (hard_b, bad)], src)
    assert all(c["lost"] is None for c in cells)


def test_control_from_the_cache():
    """The cached clang 18.1 x86-64 -O2 answers reproduce the project's result (audit/out-asm.txt)."""
    src = cs.build_source()
    pairs = []
    for b in cs.matrix():
        if b["compiler_id"] == "clang1810" and b["target"] == "x86-64" and b["opt"] == "-O2":
            pairs.append((b, cs.load_cache(os.path.join(cs.HERE, "cache", cs.cache_name(b)))["response"]))
    cells = {c["kernel"]: c for c in cs.cells(pairs, src)}
    assert [k for k, c in cells.items() if c["lost"]] == cs.CONTROL_LOST
    # The same packed-instruction picture as audit/out-asm.txt: rev 6 -> 0, stride2 14 -> 0, matmul 22 -> 0.
    assert (cells["k04_rev"]["none"]["asm"]["simd_instr"], cells["k04_rev"]["hardened"]["asm"]["simd_instr"]) == (6, 0)
    assert (cells["k05_stride2"]["none"]["asm"]["simd_instr"], cells["k05_stride2"]["hardened"]["asm"]["simd_instr"]) \
        == (14, 0)
    assert (cells["k08_matmul"]["none"]["asm"]["simd_instr"], cells["k08_matmul"]["hardened"]["asm"]["simd_instr"]) \
        == (22, 0)
    assert all(cells[k]["hardened"]["asm"]["traps"] == 1 for k in cs.KERNELS if k != "k01_sum_fwd")
