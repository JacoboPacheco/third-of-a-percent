"""harness/asm.py and harness/placement.py on AArch64 `objdump -d --no-show-raw-insn` text.

The samples are written by hand in the format objdump prints for AArch64 (address, tab, mnemonic, tab,
operands, branch targets as `addr <symbol+offset>`). The x86-64 behaviour is covered in test_placement.py
and test_asm_cachegrind.py."""
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


def test_function_is_cut_out_of_an_aarch64_dump():
    dump = "\n".join(["Disassembly of section .text:", ""] + FWD_ADD + ["", "0000000000002000 <main>:",
                                                                         "    2000:\tret", ""])
    got = asm.function_lines(dump, "kern_k02_addfwd")
    assert got[0].endswith("<_Z14kern_k02_addfwdv>:") and got[-1].endswith("ret") and len(got) == len(FWD_ADD)
