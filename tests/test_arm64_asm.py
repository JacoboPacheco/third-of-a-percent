"""harness/asm.py and harness/placement.py on AArch64 `objdump -d --no-show-raw-insn` text.

The samples are written by hand in the format objdump prints for AArch64 (address, tab, mnemonic, tab,
operands, branch targets as `addr <symbol+offset>`). The x86-64 behaviour is covered in test_placement.py
and test_asm_cachegrind.py."""
import os
import re

import asm
import placement

FWD_ADD = [
    "0000000000001000 <_Z14kern_k02_addfwdv>:",
    "    1000:\tcbz\tx2, 1030 <_Z14kern_k02_addfwdv+0x30>",
    "    1004:\tmov\tx8, xzr",
    "    1008:\tldr\tq0, [x0, x8]",
    "    100c:\tldr\tq1, [x1, x8]",
    "    1010:\tadd\tv0.4s, v0.4s, v1.4s",
    "    1014:\tstr\tq0, [x3, x8]",
    "    1018:\tadd\tx8, x8, #0x10",
    "    101c:\tcmp\tx8, x2",
    "    1020:\tb.ne\t1008 <_Z14kern_k02_addfwdv+0x8>",
    "    1024:\tldr\tw9, [x0, x8]",
    "    1028:\tadd\tx8, x8, #0x4",
    "    102c:\tcbnz\tx9, 1024 <_Z14kern_k02_addfwdv+0x24>",
    "    1030:\tret",
]


def test_neon_loop_is_found_and_marked_simd():
    lps = placement.loops(FWD_ADD)
    assert [(lp["start"], lp["end"], lp["bytes"]) for lp in lps] == [("0x1008", "0x1024", 28),
                                                                    ("0x1024", "0x1030", 12)]
    assert lps[0]["simd"] and not lps[1]["simd"]
    assert lps[0]["insns"] == 7 and lps[1]["insns"] == 3
    assert all(lp["innermost"] for lp in lps)
    assert placement.summary(lps) == "0x1008/28Bs 0x1024/12B"


def test_forward_compare_branch_is_not_a_loop_and_bl_is_not_a_branch_target():
    lines = ["0000000000001000 <_Z6kern_xv>:",
             "    1000:\ttbz\tw8, #0, 1010 <_Z6kern_xv+0x10>",
             "    1004:\tbl\t2000 <__libcpp_verbose_abort>",
             "    1008:\tb\t1000 <_Z6kern_xv>",
             "    100c:\tret",
             "    1010:\ttbnz\tw8, #3, 1000 <_Z6kern_xv>",
             "    1014:\tret"]
    lps = placement.loops(lines)
    assert [(lp["start"], lp["end"]) for lp in lps] == [("0x1000", "0x1014")]


def test_scalar_registers_are_not_simd():
    lines = ["0000000000001000 <_Z6kern_xv>:",
             "    1000:\tldr\ts0, [x0], #4",
             "    1004:\tfadd\td1, d1, d0",
             "    1008:\tsubs\tx1, x1, #0x1",
             "    100c:\tb.ne\t1000 <_Z6kern_xv>",
             "    1010:\tret"]
    lp = placement.loops(lines)[0]
    assert not lp["simd"] and lp["bytes"] == 0x10


def test_brk_counts_as_a_trap_like_ud2():
    fn = FWD_ADD + ["    1034:\tbrk\t#0x1", "    1038:\tbrk\t#0x3e8"]
    assert asm.count_traps(fn) == 1
    assert asm.count_traps(["    1000:\tud2"]) == 1


def test_verbose_abort_call_counts_as_a_trap_on_both_architectures():
    assert asm.count_traps(["    1000:\tbl\t2000 <_ZNSt3__122__libcpp_verbose_abortEPKcz>"]) == 1
    assert asm.count_traps(["    1000:\tcall\t2000 <_ZNSt3__122__libcpp_verbose_abortEPKcz>"]) == 1
    assert asm.count_traps(["    1000:\tbl\t2000 <memcpy>"]) == 0


def _normalize_with_four_digit_targets(lines):
    """harness/asm.normalize as it was before the targets of three digits were handled (the pattern was {4,})."""
    out = []
    for ln in lines:
        ln = re.sub(r"^\s*[0-9a-f]+:\s*", "", ln)
        ln = re.sub(r"\b[0-9a-f]{4,} <", "<", ln)
        ln = re.sub(r"<([^>+]*)\+0x[0-9a-f]+>", r"<\1+off>", ln)
        out.append(ln.rstrip())
    return out


# an AArch64 function laid out at 0xe28, as the Arm runs' listings are (branch targets e28..fff have three hex digits)
ARM_LOW = [
    "0000000000000e28 <_Z6kern_xv>:",
    "     e28:\tsub\tsp, sp, #0x70",
    "     e44:\tcbz\tx3, 1028 <_Z6kern_xv+0x200>",
    "     ebc:\tb.ls\tf48 <_Z6kern_xv+0x120>  // b.plast",
    "     f4c:\tcbz\tx3, f50 <_Z6kern_xv+0x128>",
    "     f50:\tadd\tx8, x8, #0xe28",
    "     f54:\tbl\t8a0 <memcpy@plt>",
    "     f58:\tret",
]


def test_normalize_drops_three_digit_aarch64_branch_targets():
    got = asm.normalize(ARM_LOW)
    assert got == ["<_Z6kern_xv>:", "sub\tsp, sp, #0x70", "cbz\tx3, <_Z6kern_xv+off>",
                   "b.ls\t<_Z6kern_xv+off>  // b.plast", "cbz\tx3, <_Z6kern_xv+off>", "add\tx8, x8, #0xe28",
                   "bl\t<memcpy@plt>", "ret"]
    assert not [ln for ln in got if re.search(r"\b[0-9a-f]{3,} <", ln)]


def test_a_moved_aarch64_branch_is_not_a_diff_line():
    moved = [ln.replace("f48 <_Z6kern_xv+0x120>", "f9c <_Z6kern_xv+0x174>").replace("f50 <_Z6kern_xv+0x128>", "fa4 <_Z6kern_xv+0x17c>")
             for ln in ARM_LOW]
    assert moved != ARM_LOW
    assert asm.unified_diff(ARM_LOW, moved, "a", "b") == "\n"
    changed = [ln.replace("sub\tsp, sp, #0x70", "sub\tsp, sp, #0x80") for ln in moved]
    d = asm.unified_diff(ARM_LOW, changed, "a", "b")
    changed_lines = [ln for ln in d.splitlines() if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    assert changed_lines == ["-sub\tsp, sp, #0x70", "+sub\tsp, sp, #0x80"]  # the real change shows; the moved branches do not


def test_x86_listings_normalize_exactly_as_before():
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    names = ["k04_rev.fast.s", "k04_rev.none.s", "k02_add_fwd.fast_s1.s", "k02_add_fwd.fast_a64_s1.s"]
    total = 0
    for n in names:
        with open(os.path.join(here, n), encoding="utf-8") as f:
            lines = f.read().splitlines()
        assert asm.normalize(lines) == _normalize_with_four_digit_targets(lines), n
        total += len(lines)
    assert total > 100  # real day-one listings, not a stub


def test_function_is_cut_out_of_an_aarch64_dump():
    dump = "\n".join(["Disassembly of section .text:", ""] + FWD_ADD + ["", "0000000000002000 <main>:",
                                                                         "    2000:\tret", ""])
    got = asm.function_lines(dump, "kern_k02_addfwd")
    assert got[0].endswith("<_Z14kern_k02_addfwdv>:") and got[-1].endswith("ret") and len(got) == len(FWD_ADD)
