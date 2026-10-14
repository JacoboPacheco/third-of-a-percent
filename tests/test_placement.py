"""harness/placement.py on the real k02_add_fwd FAST builds from the investigation run 38119645255
(EPYC 7763, draw1): as compiled the 31-byte SIMD loop sits at 0x12b0 and crosses 0x12c0; with
-falign-loops=64 it starts at 0x1300 and crosses nothing (investigate/results/.../loops.jsonl)."""
import os

import placement

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def read_lines(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return f.read().splitlines()


def test_fast_as_compiled_simd_loop_crosses_64():
    lps = placement.loops(read_lines("k02_add_fwd.fast_s1.s"))
    assert [(lp["start"], lp["bytes"]) for lp in lps] == [("0x12b0", 31), ("0x12f0", 30)]
    simd = lps[0]
    assert simd["simd"] and simd["crosses64"] and simd["extra_window"]
    assert simd["start_mod64"] == 48 and simd["windows64"] == 2 and simd["min_windows64"] == 1
    assert simd["insns"] == 7
    assert all(lp["innermost"] for lp in lps)
    assert placement.summary(lps) == "0x12b0/31Bs+ 0x12f0/30B+"


def test_fast_aligned_loops_cross_nothing():
    lps = placement.loops(read_lines("k02_add_fwd.fast_a64_s1.s"))
    assert [(lp["start"], lp["bytes"], lp["crosses64"]) for lp in lps] == [("0x1300", 31, False),
                                                                          ("0x1340", 30, False)]
    assert lps[0]["simd"] and not lps[1]["simd"]
    assert placement.summary(lps) == "0x1300/31Bs 0x1340/30B"


def test_long_loop_crossing_is_not_an_extra_window_when_unavoidable():
    lines = ["0000000000001000 <_Z6kern_xv>:", "    1000:\tnop", "    1048:\tjne    1000 <_Z6kern_xv>",
             "    104a:\tret"]
    lp = placement.loops(lines)[0]
    assert lp["bytes"] == 0x4a and lp["crosses64"] and lp["windows64"] == 2 and not lp["extra_window"]


def test_outer_loop_is_not_innermost_and_jmp_is_not_a_loop():
    lines = ["0000000000001000 <_Z6kern_xv>:",
             "    1000:\txor    %eax,%eax",
             "    1010:\tadd    $0x1,%eax",
             "    1014:\tjne    1010 <_Z6kern_xv+0x10>",
             "    1016:\tjmp    1000 <_Z6kern_xv>",
             "    1018:\tjb     1000 <_Z6kern_xv>",
             "    101a:\tret"]
    lps = placement.loops(lines)
    assert [(lp["start"], lp["end"], lp["innermost"]) for lp in lps] == [("0x1010", "0x1016", True),
                                                                        ("0x1000", "0x101a", False)]
    assert len(placement.hot(lps)) == 1


def test_binary_summary_counts_innermost_loops_per_function():
    a = read_lines("k02_add_fwd.fast_s1.s")
    b = read_lines("k02_add_fwd.fast_a64_s1.s")
    s = placement.binary_summary(a + [""] + b)
    assert s == {"innermost_loops": 4, "crosses64": 2, "extra_window": 2, "simd_loops": 2, "simd_crosses64": 1}
