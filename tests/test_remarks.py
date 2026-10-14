"""harness/remarks.py on real clang-18 remark text saved by day-one run 38116223923."""
import os

import remarks

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return f.read()


def test_reverse_loop_vectorized_in_none():
    v = remarks.vectorization(read("remarks.k04_rev.none.txt"), "k04_rev.cpp", 5)
    assert v["vectorized"] is True
    assert v["width"] == 4


def test_reverse_loop_not_vectorized_in_fast():
    v = remarks.vectorization(read("remarks.k04_rev.fast.txt"), "k04_rev.cpp", 5)
    assert v["vectorized"] is False
    assert v["width"] is None
    assert any(m.startswith("loop not vectorized: could not determine number of loop iterations")
               for m in v["remarks"])


def test_novec_build_not_vectorized():
    v = remarks.vectorization(read("remarks.k04_rev.novec.txt"), "k04_rev.cpp", 5)
    assert v == {"vectorized": False, "width": None, "remarks": ["loop not vectorized [-Rpass-missed=loop-vectorize]"]}


def test_sum_width_two():
    v = remarks.vectorization(read("remarks.k01_sum_fwd.none.txt"), "k01_sum_fwd.cpp", 6)
    assert (v["vectorized"], v["width"]) == (True, 2)


def test_forward_add_stays_vectorized_in_fast():
    v = remarks.vectorization(read("remarks.k02_add_fwd.fast.txt"), "k02_add_fwd.cpp", 6)
    assert (v["vectorized"], v["width"]) == (True, 4)


def test_stride2_not_vectorized_in_fast():
    v = remarks.vectorization(read("remarks.k05_stride2.fast.txt"), "k05_stride2.cpp", 5)
    assert v["vectorized"] is False


def test_matmul_cost_model_refusal_counts_as_not_vectorized():
    # real text from measure run 38118762125: under FAST the i-k-j inner loop is judged not worth vectorizing
    fast = remarks.vectorization(read("remarks.k08_matmul.fast.txt"), "k08_matmul.cpp", 11)
    none = remarks.vectorization(read("remarks.k08_matmul.none.txt"), "k08_matmul.cpp", 11)
    assert (fast["vectorized"], fast["width"]) == (False, None)
    assert fast["remarks"][0].startswith("the cost-model indicates that vectorization is not beneficial")
    assert (none["vectorized"], none["width"]) == (True, 4)


def test_other_lines_and_common_hpp_are_ignored():
    text = read("remarks.k04_rev.none.txt")
    # line 17 is the driver loop in main: not vectorized, but not the kernel's loop
    assert remarks.vectorization(text, "k04_rev.cpp", 17)["vectorized"] is False
    # no remark at all on a line clang said nothing about
    assert remarks.vectorization(text, "k04_rev.cpp", 3) == {"vectorized": None, "width": None, "remarks": []}
    # the same line number in another file does not count
    assert remarks.vectorization(text, "other.cpp", 5)["vectorized"] is None


def test_loop_line_finds_the_marker():
    src = "#include <x>\nvoid f() {\n  for (;;) {}  // LOOP\n}\n"
    assert remarks.loop_line(src) == 3


def test_every_kernel_has_one_marker():
    kdir = os.path.join(os.path.dirname(DATA), "..", "kernels")
    for name in sorted(os.listdir(kdir)):
        if name.endswith(".cpp"):
            with open(os.path.join(kdir, name), encoding="utf-8") as f:
                text = f.read()
            assert text.count("// LOOP") == 1, name
            assert f"kern_{name[:-4]}(" in text, name
