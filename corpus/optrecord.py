"""Reads clang's optimization record files (-fsave-optimization-record, YAML) without a YAML library.

The census builds with `-foptimization-record-passes=loop-vectorize`, so each file holds one
document per loop decision, for example:

    --- !Passed
    Pass:            loop-vectorize
    Name:            Vectorized
    DebugLoc:        { File: 'src/a.cpp', Line: 5, Column: 3 }
    Function:        _Z3fooRNSt3__16vectorIiNS_9allocatorIiEEEE
    Args:
      - String:          'vectorized loop (vectorization width: '
      - VectorizationFactor: '4'
      - String:          ', interleaved count: '
      - InterleaveCount: '2'
      - String:          ')'
    ...

Unlike the text remarks on stderr, a record names the function the loop was compiled in, which
the census needs to match a loop between the NONE and FAST builds. Only the subset of YAML that
LLVM writes for these records is handled: a tag line, top-level `Key: value` pairs, the
`DebugLoc` flow mapping, and the `Args` list of one-key mappings (with an optional DebugLoc).
"""
import re

_KEY = re.compile(r"^(\s*)(- )?([A-Za-z_][A-Za-z0-9_]*):(?:\s+(.*))?$")
_LOC = re.compile(
    r"File:\s*('(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\"|[^,}]+?)\s*,\s*Line:\s*(\d+)\s*,\s*Column:\s*(\d+)")


def scalar(text):
    """A YAML scalar as LLVM writes it: 'single' (with '' escapes), "double" or plain."""
    t = (text or "").strip()
    if len(t) >= 2 and t[0] == "'" and t[-1] == "'":
        return t[1:-1].replace("''", "'")
    if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
        return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), t[1:-1])
    return t


def debug_loc(text):
    """{'file', 'line', 'column'} from `{ File: 'x.cpp', Line: 5, Column: 3 }`, or None."""
    m = _LOC.search(text or "")
    if not m:
        return None
    return {"file": scalar(m.group(1)), "line": int(m.group(2)), "column": int(m.group(3))}


def _join_flow_mappings(lines):
    """LLVM wraps a long flow mapping (`DebugLoc: { File: '...',` / `Line: 5, Column: 3 }`) over
    several lines; join such lines back into one."""
    out, buf = [], None
    for raw in lines:
        if buf is not None:
            buf += " " + raw.strip()
            if "}" in _STR_RE.sub("", buf.split("{", 1)[1]):
                out.append(buf)
                buf = None
            continue
        m = _KEY.match(raw)
        if m and (m.group(4) or "").startswith("{") and "}" not in _STR_RE.sub("", m.group(4)):
            buf = raw
            continue
        out.append(raw)
    if buf is not None:
        out.append(buf)
    return out


_STR_RE = re.compile("'(?:[^']|'')*'" + r'|"(?:[^"\\]|\\.)*"')


def parse(text):
    """Every record in an optimization record file, as dicts:
    {'kind': 'Passed'|'Missed'|'Analysis'|..., 'pass', 'name', 'function', 'loc' (or None),
     'args': [(key, value), ...], 'message': the Args strings joined, as clang prints the remark}.
    """
    records = []
    cur = None
    in_args = False
    last = None  # (container, key) of the last scalar, for a continuation line
    lines = _join_flow_mappings(text.splitlines())
    for raw in lines:
        if raw.startswith("--- !"):
            cur = {"kind": raw[5:].strip(), "pass": "", "name": "", "function": "", "loc": None, "args": []}
            records.append(cur)
            in_args, last = False, None
            continue
        if cur is None or not raw.strip():
            continue
        if raw.startswith("..."):
            cur, in_args, last = None, False, None
            continue
        m = _KEY.match(raw)
        if not m:
            # A scalar continued on the next line (folded long value): join with one space.
            if last is not None:
                box, idx = last
                if box is cur:
                    cur[idx] = (cur[idx] + " " + scalar(raw)).strip()
                else:
                    k, v = box[idx]
                    box[idx] = (k, (v + " " + scalar(raw)).strip())
            continue
        indent, dash, key, val = len(m.group(1)), m.group(2), m.group(3), m.group(4) or ""
        if indent == 0 and not dash:
            in_args = key == "Args"
            if key == "DebugLoc":
                cur["loc"] = debug_loc(val)
                last = None
            elif key in ("Pass", "Name", "Function"):
                cur[key.lower()] = scalar(val)
                last = (cur, key.lower())
            else:
                last = None
            continue
        if in_args:
            if key == "DebugLoc":
                last = None
                continue  # a location inside an argument (a callee's); not part of the message
            cur["args"].append((key, scalar(val)))
            last = (cur["args"], len(cur["args"]) - 1)
    for r in records:
        r["message"] = "".join(v for _, v in r["args"])
    return records


def loop_vectorize(records):
    """Only the loop vectorizer's records."""
    return [r for r in records if r["pass"] == "loop-vectorize"]


def is_vectorized(rec):
    """True for the record clang writes when it vectorized a loop."""
    return rec["kind"] == "Passed" and rec["name"] == "Vectorized"
