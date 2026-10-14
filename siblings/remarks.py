"""Reads the compiler's vectorization remarks for the one loop a kernel is about.

Copied from harness/remarks.py (the clang part is unchanged) and extended with a GCC reader.

Each kernel marks its loop with a `// LOOP` comment; only remarks at that file and line count.

clang (-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize):
    k04_rev.cpp:5:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [...]
    k04_rev.cpp:5:3: remark: loop not vectorized: ... [...]
GCC (-fopt-info-vec-optimized -fopt-info-vec-missed):
    kernels/k04_rev.cpp:5:30: optimized: loop vectorized using 16 byte vectors
    kernels/k04_rev.cpp:5:30: missed: couldn't vectorize loop
    kernels/k04_rev.cpp:5:30: missed: not vectorized: ...

Result: {"vectorized": True/False/None, "width": int or None, "vector_bytes": int or None, "remarks": [...]}.
True when a "vectorized loop" (clang) or "loop vectorized using N byte vectors" (GCC) remark is at the
line; False when only other remarks are; None when the compiler said nothing about the line. For
clang, width is the vectorization factor; for GCC, vector_bytes is the widest vector it reported
(an epilogue may add a narrower one) and width is left None, since GCC does not print the factor.
GCC's "basic block part vectorized" (SLP inside one iteration) is not a vectorized loop.
"""
import os
import re

_VEC = re.compile(r"vectorized loop \(vectorization width: (\d+)")
_GCC_VEC = re.compile(r"loop vectorized using (\d+) byte vectors")


def loop_line(source_text, marker="// LOOP"):
    """The 1-based line number of the line carrying the marker comment."""
    for i, line in enumerate(source_text.splitlines(), 1):
        if marker in line:
            return i
    raise ValueError("no %r marker in the source" % marker)


def remarks_at(stderr_text, source_name, line, gcc=False):
    """The remark messages the compiler printed for `source_name` (a basename) at `line`."""
    kind = r"(?:optimized|missed|note)" if gcc else r"remark"
    pat = re.compile(r"(^|[/\\])%s:%d:\d+: %s: (.*)$" % (re.escape(os.path.basename(source_name)), line, kind))
    out = []
    for ln in stderr_text.splitlines():
        m = pat.search(ln)
        if m:
            tag = re.search(r": (optimized|missed|note|remark): ", ln).group(1)
            out.append(m.group(2).strip() if not gcc else f"{tag}: {m.group(2).strip()}")
    return out


def vectorization(stderr_text, source_name, line, gcc=False):
    """{"vectorized", "width", "vector_bytes", "remarks"} for the marked loop."""
    msgs = remarks_at(stderr_text, source_name, line, gcc)
    vec, width, vbytes = None, None, None
    for msg in msgs:
        if gcc:
            m = _GCC_VEC.search(msg)
            if m and msg.startswith("optimized:"):
                vec = True
                vbytes = max(vbytes or 0, int(m.group(1)))
        else:
            m = _VEC.match(msg)
            if m:
                vec, width = True, int(m.group(1))
    if vec is None and msgs:
        vec = False
    # keep the stored list short: GCC can print dozens of "missed" notes for one loop
    uniq = list(dict.fromkeys(msgs))
    return {"vectorized": vec, "width": width, "vector_bytes": vbytes, "remarks": uniq[:12],
            "remarks_total": len(msgs)}
