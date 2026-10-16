"""Writes sources/kernels.cpp from the project's kernels/ (the functions are copied verbatim).

    python make_sources.py            # write
    python make_sources.py --check    # exit 1 if sources/kernels.cpp differs from what kernels/ gives

The five functions are the forward sum (k01), the forward add (k02), the stencil (k03), the reverse
loop (k04) and the stride-2 loop (k05). Each is `noinline` and independent, so putting them in one
file does not change how any loop is compiled. sources/variants.cpp is hand-written and is not touched.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KERNELS = ["k01_sum_fwd", "k02_add_fwd", "k03_stencil", "k04_rev", "k05_stride2"]
HEADER = ("// Five of the project's loop functions, copied verbatim from kernels/kNN_*.cpp (written by make_sources.py).\n"
          "// k01 forward sum, k02 forward add, k03 stencil (forward), k04 reverse, k05 stride-2.\n"
          "#include <cstddef>\n#include <cstdint>\n#include <vector>\n")


def extract(text, name):
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines)
                 if ln.startswith("__attribute__((noinline))") and ("kern_" + name) in ln)
    end = next(j for j in range(start, len(lines)) if lines[j] == "}")
    return "\n".join(lines[start:end + 1]) + "\n"


def build():
    parts = [HEADER]
    for k in KERNELS:
        with open(os.path.join(REPO, "kernels", k + ".cpp"), encoding="utf-8") as f:
            parts.append("\n" + extract(f.read(), k))
    return "".join(parts)


if __name__ == "__main__":
    out = os.path.join(HERE, "sources", "kernels.cpp")
    src = build()
    if "--check" in sys.argv:
        with open(out, encoding="utf-8") as f:
            sys.exit(0 if f.read() == src else 1)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(src)
    print("wrote", out)
