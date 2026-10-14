"""Reads clang's loop-vectorize remarks for the one loop a kernel is about.

Each kernel marks its loop with a `// LOOP` comment. The build passes
`-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize`, and clang
prints one line per loop decision on stderr, for example:

    .../k04_rev.cpp:5:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]
    .../k04_rev.cpp:5:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]

Only remarks at the marked file and line count; remarks about the driver loops or common.hpp
are ignored. The result is the SPEC's {"vectorized": bool | None, "width": int | None}:
True when a "vectorized loop" remark is at that line, False when only other remarks are (such as
"loop not vectorized: ..." or "the cost-model indicates that vectorization is not beneficial"),
None when clang said nothing about that line.
"""
import os
import re

_VEC = re.compile(r"vectorized loop \(vectorization width: (\d+)")


def loop_line(source_text, marker="// LOOP"):
    """The 1-based line number of the line carrying the marker comment."""
    for i, line in enumerate(source_text.splitlines(), 1):
        if marker in line:
            return i
    raise ValueError("no %r marker in the source" % marker)


def remarks_at(stderr_text, source_name, line):
    """The remark messages clang printed for `source_name` (a basename) at `line`."""
    pat = re.compile(r"(^|[/\\])%s:%d:\d+: remark: (.*)$" % (re.escape(os.path.basename(source_name)), line))
    out = []
    for ln in stderr_text.splitlines():
        m = pat.search(ln)
        if m:
            out.append(m.group(2).strip())
    return out


def vectorization(stderr_text, source_name, line):
    """{"vectorized": True/False/None, "width": int or None, "remarks": [messages at that line]}."""
    msgs = remarks_at(stderr_text, source_name, line)
    vec, width = None, None
    for msg in msgs:
        m = _VEC.match(msg)
        if m:
            vec, width = True, int(m.group(1))
    # Any other remark at the loop's line ("loop not vectorized: ...", "the cost-model indicates that
    # vectorization is not beneficial", ...) means clang looked at the loop and did not vectorize it.
    if vec is None and msgs:
        vec = False
    return {"vectorized": vec, "width": width, "remarks": msgs}
