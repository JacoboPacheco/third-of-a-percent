"""harness/asm.py on real objdump output (day-one run 38116223923) and harness/cachegrind.py on a
hand-written file in the Cachegrind output format (no real Cachegrind file existed when this was written)."""
import os

import asm
import cachegrind

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return f.read()


def objdump_with(fn_text):
    other = "0000000000001100 <main>:\n    1100:\tpush   %rbp\n    1101:\tud2    \n"
    tail = "0000000000001400 <_Z4fillRNSt3__16vectorIiNS_9allocatorIiEEEEj>:\n    1400:\tud2    \n"
    return "\nDisassembly of section .text:\n\n" + other + "\n" + fn_text.rstrip("\n") + "\n\n" + tail


def test_function_cut_and_trap_counts():
    fast = asm.function_lines(objdump_with(read("k04_rev.fast.s")), "kern_k04_rev")
    none = asm.function_lines(objdump_with(read("k04_rev.none.s")), "kern_k04_rev")
    assert fast[0].endswith("<_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:")
    assert asm.count_traps(fast) == 1  # the ud2 of main and fill are outside the cut
    assert asm.count_traps(none) == 0


def test_missing_function_gives_no_lines():
    assert asm.function_lines(objdump_with(read("k04_rev.fast.s")), "kern_k99_none") == []


def test_verbose_abort_calls_count_as_traps():
    lines = ["  10:\tcall   1234 <_ZNSt3__122__libcpp_verbose_abortEPKcz@plt>", "  15:\tret"]
    assert asm.count_traps(lines) == 1


def test_diff_shows_simd_removed():
    none = asm.function_lines(objdump_with(read("k04_rev.none.s")), "kern_k04_rev")
    fast = asm.function_lines(objdump_with(read("k04_rev.fast.s")), "kern_k04_rev")
    d = asm.unified_diff(none, fast, "k04_rev.none.s", "k04_rev.fast.s")
    assert d.startswith("--- k04_rev.none.s\n+++ k04_rev.fast.s\n")
    assert any(ln.startswith("-") and "paddd" in ln for ln in d.splitlines())
    assert any(ln.startswith("+") and "ud2" in ln for ln in d.splitlines())


def test_identical_functions_give_empty_diff():
    none = asm.function_lines(objdump_with(read("k04_rev.none.s")), "kern_k04_rev")
    assert asm.unified_diff(none, none, "a", "b") == "\n"


CG = """desc: I1 cache:
cmd: build/k04_rev.none 6144 20
events: Ir
fl=/home/runner/work/x/kernels/k04_rev.cpp
fn=kern_k04_rev(std::__1::vector<int, std::__1::allocator<int> >&, std::__1::vector<int, std::__1::allocator<int> > const&)
4 21
5 1000
fn=main
12 500
fl=/usr/lib/llvm-18/include/c++/v1/vector
fn=kern_k04_rev(std::__1::vector<int, std::__1::allocator<int> >&, std::__1::vector<int, std::__1::allocator<int> > const&)
1500 50
fn=std::__1::vector<int>::vector(unsigned long)
1200 300
summary: 1871
"""


def test_cachegrind_sums_every_row_of_the_kernel():
    assert cachegrind.function_ir(CG, "kern_k04_rev") == 21 + 1000 + 50


def test_cachegrind_per_call():
    assert cachegrind.per_call(CG, "kern_k04_rev", 21) == 51


def test_cachegrind_absent_function():
    assert cachegrind.function_ir(CG, "kern_k01_sum_fwd") == 0


def test_cachegrind_multi_event_file_reads_ir_column():
    text = "events: Dr Ir\nfn=kern_x()\n3 7 100\n4 1 5\n"
    assert cachegrind.function_ir(text, "kern_x") == 105
