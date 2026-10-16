"""Writes sources/handwritten/s2-bound.ll: hand-written LLVM IR for a stride-2 loop with one in-loop check.

    python make_s2_bound.py            # write
    python make_s2_bound.py --check    # exit 1 if the file differs from what this script makes

Every function has the same loop. The counter is `i`. The checked index is `e = (i << 1) | 1`. The check is
`bound > e` (an unsigned compare, the form clang 18.1.0 prints for kern_k05_stride2), the failing branch calls
`llvm.trap`, and the latch compares `i + 1` with `max(n, 1)`. Only the expression for `bound` differs, and
whether the shift carries `nuw`:

  bound     expression
  full      the argument %an as it is (full range)
  ashr2     ashr %an, 2
  lshr1     lshr %an, 1
  and62     and %an, 2^62 - 1
  umin40    umin(%an, 2^40)
  ptr_ashr  ashr exact (end - begin), 2 with two pointer arguments (the size of a std::vector<int32_t>, as in k05)
  ptr_lshr  lshr exact (end - begin), 1 with two pointer arguments (the bound of v_s2_span)

  flags     plain: `shl i, 1` (as in kern_k05_stride2)   nuw: `shl nuw i, 1` (as in v_s2_span)

The `or` has the `disjoint` flag in both, as in the dumps of group B.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sources", "handwritten", "s2-bound.ll")
NL = "\n"

BOUNDS = [
    ("full", "i64 %an", ["  %bound = add i64 %an, 0"]),
    ("ashr2", "i64 %an", ["  %bound = ashr i64 %an, 2"]),
    ("lshr1", "i64 %an", ["  %bound = lshr i64 %an, 1"]),
    ("and62", "i64 %an", ["  %bound = and i64 %an, 4611686018427387903"]),
    ("umin40", "i64 %an", ["  %bound = call i64 @llvm.umin.i64(i64 %an, i64 1099511627776)"]),
    ("ptr_ashr", "ptr %beg, ptr %end",
     ["  %pe = ptrtoint ptr %end to i64", "  %pb = ptrtoint ptr %beg to i64", "  %bytes = sub i64 %pe, %pb",
      "  %bound = ashr exact i64 %bytes, 2"]),
    ("ptr_lshr", "ptr %beg, ptr %end",
     ["  %pe = ptrtoint ptr %end to i64", "  %pb = ptrtoint ptr %beg to i64", "  %bytes = sub i64 %pe, %pb",
      "  %bound = lshr exact i64 %bytes, 1"]),
]
FLAGS = [("plain", ""), ("nuw", " nuw")]

HEAD = """; Hand-written (make_s2_bound.py). One stride-2 loop with one in-loop check; only the bound's expression and the
; flags of the shift differ between the functions. See the docstring of make_s2_bound.py.
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

declare void @llvm.trap() #0
declare i64 @llvm.umax.i64(i64, i64)
declare i64 @llvm.umin.i64(i64, i64)
attributes #0 = { cold noreturn nounwind }
"""

FUNC = """
define void @f_{bound}_{flags}(ptr noalias %c, ptr noalias %a, i64 %n, {args}) {{
entry:
{pre}
  %n1 = call i64 @llvm.umax.i64(i64 %n, i64 1)
  br label %loop
loop:
  %i = phi i64 [ 0, %entry ], [ %i.next, %cont ]
  %d = shl{shl} i64 %i, 1
  %e = or disjoint i64 %d, 1
  %ok = icmp ugt i64 %bound, %e
  br i1 %ok, label %cont, label %trap
trap:
  call void @llvm.trap()
  unreachable
cont:
  %pa = getelementptr inbounds i32, ptr %a, i64 %d
  %va = load i32, ptr %pa, align 4
  %pb2 = getelementptr inbounds i32, ptr %a, i64 %e
  %vb = load i32, ptr %pb2, align 4
  %s = add nsw i32 %vb, %va
  %pc = getelementptr inbounds i32, ptr %c, i64 %i
  store i32 %s, ptr %pc, align 4
  %i.next = add nuw i64 %i, 1
  %done = icmp eq i64 %i.next, %n1
  br i1 %done, label %exit, label %loop
exit:
  ret void
}}
"""


def build():
    parts = [HEAD]
    for flags, shl in FLAGS:
        for bound, args, pre in BOUNDS:
            parts.append(FUNC.format(bound=bound, flags=flags, args=args, pre=NL.join(pre), shl=shl))
    return "".join(parts)


if __name__ == "__main__":
    text = build()
    if "--check" in sys.argv:
        with open(OUT, encoding="utf-8") as f:
            sys.exit(0 if f.read() == text else 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline=NL) as f:
        f.write(text)
    print("wrote", OUT)
