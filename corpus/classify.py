"""Sorts a lost loop into a coarse pattern from its source text: a heuristic, not a proof.

A loop is LOST when clang vectorized it in the NONE build and not in the FAST build. Why it lost
SIMD is read from two things: the loop's own source text (the line clang's record points at and
the body that follows) and clang's FAST remark. The four classes asked for:

  reverse     the index counts down (`i--`, `--i`, `-= 1`, reverse iterators) or reads `[n - 1 - i]`
  strided     the index is computed: a step other than 1 (`i += k`), a multiplied or shifted
              index (`[2 * i]`, `[i * n + j]`, `[i << 2]`), or the counter plus another variable
  indirect    the index is read from memory (`a[b[i]]`, `h[a[i] & 255]`)
  other       none of these in the text, with a detail: an early exit (break/return in the body,
              `&&` in the condition), a loop inside libc++'s own headers, an iterator or pointer
              loop with no subscript, a while/do loop, a forward loop whose bound is not the
              container's size() (so the compiler cannot prove the check always passes), or
              "unclear"

The text is matched with regular expressions, so a macro, a helper function or a loop whose body
is far from its header can land in the wrong class; every lost loop is listed with its source
line so a reader can check the call.
"""
import re

CLASSES = ("reverse", "strided", "indirect", "other")

_STR = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
_LINE_COMMENT = re.compile(r"//.*$")
_DEC = re.compile(r"(?:\b[A-Za-z_]\w*\s*--|--\s*[A-Za-z_]\w*|-=\s*1\b)")
_REV_ITER = re.compile(r"\b(?:rbegin|rend|crbegin|crend|reverse_iterator)\b")
_REV_INDEX = re.compile(r"\[[^\[\]]*\b\w+\s*-\s*1\s*-\s*\w+[^\[\]]*\]|\[[^\[\]]*\b\w+\s*-\s*\w+\s*-\s*1\s*\]")
_STEP = re.compile(r"\+=\s*(?!1\b)(?:\d+|[A-Za-z_(])")
_SUBSCRIPT = re.compile(r"\[([^\[\]]*)\]")
_NESTED = re.compile(r"\[[^\[\]]*\[")
_EXIT = re.compile(r"\b(?:break|return|goto|throw)\b")


def code_only(line):
    """The line with string literals and // comments removed."""
    return _LINE_COMMENT.sub("", _STR.sub('""', line))


def loop_context(lines, index, max_lines=12):
    """The loop's text: its header line (0-based `index`) and the body after it, up to the brace
    that closes the body, the end of a one-statement body, or `max_lines` lines."""
    out, depth, opened = [], 0, False
    for j in range(index, min(len(lines), index + max_lines)):
        code = code_only(lines[j])
        out.append(lines[j])
        depth += code.count("{") - code.count("}")
        if "{" in code:
            opened = True
        if opened and depth <= 0:
            break
        if not opened and code.rstrip().endswith(";") and (j > index or ")" in code):
            break
    return out


def _header(line, column):
    """The header text from the loop's column on (clang's column is 1-based)."""
    return code_only(line[max(0, column - 1):] if column else line)


def loop_control(head):
    """The part of the header that drives the loop: the parenthesized `for (...)` or `while (...)`
    when the header starts with one, else the whole header."""
    m = re.match(r"\s*(?:for|while)\s*\(", head)
    if not m:
        return head
    depth, start = 0, m.end() - 1
    for i in range(start, len(head)):
        if head[i] == "(":
            depth += 1
        elif head[i] == ")":
            depth -= 1
            if depth == 0:
                return head[start + 1:i]
    return head[start + 1:]


def trip_count(context, column=1):
    """What bounds the loop, from its header text (a heuristic, like classify()):
    {"kind": ..., "bound": <the condition text>}. Kinds: "container size()" (the condition calls
    size() or length()), "range or iterator loop" (range-for, begin()/end(), iterators), "other bound"
    (any other expression: a variable, a parameter, a constant), "no condition", "not a for/while
    header" (clang pointed at a line that is not the loop's header)."""
    if not context:
        return {"kind": "source not available", "bound": ""}
    head = _header(context[0], column)
    stripped = head.lstrip()
    if not (stripped.startswith("for") or stripped.startswith("while")):
        return {"kind": "not a for/while header", "bound": clip_text(stripped)}
    control = loop_control(head).strip()
    if stripped.startswith("for"):
        parts = control.split(";")
        if len(parts) < 3:
            return {"kind": "range or iterator loop", "bound": clip_text(control)}
        cond = parts[1].strip()
    else:
        cond = control
    if not cond:
        return {"kind": "no condition", "bound": ""}
    if re.search(r"\b(?:size|length)\s*\(\s*\)", cond):
        return {"kind": "container size()", "bound": clip_text(cond)}
    if re.search(r"\b(?:c?r?begin|c?r?end)\s*\(\s*\)|\bit\b|iter", cond):
        return {"kind": "range or iterator loop", "bound": clip_text(cond)}
    return {"kind": "other bound", "bound": clip_text(cond)}


def clip_text(s, n=160):
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n - 3] + "..."


def classify(context, column=1, origin="project", fast_message=""):
    """(class, detail) for one lost loop. `context` is loop_context()'s lines, the first being the
    line clang pointed at; `origin` is 'project', 'driver', 'libc++' or 'system'."""
    if not context:
        return "other", "source not available"
    head = _header(context[0], column)
    body = "\n".join(code_only(x) for x in context[1:])
    text = head + "\n" + body
    subs = _SUBSCRIPT.findall(text)

    if _NESTED.search(text):
        return "indirect", "index read from memory (a[b[i]])"
    if _REV_ITER.search(text):
        return "reverse", "reverse iterators"
    control = loop_control(head)
    if _DEC.search(control):
        return "reverse", "counter counts down (i--, --i)"
    if _REV_INDEX.search(text):
        return "reverse", "index n - 1 - i"
    if _STEP.search(control):
        return "strided", "step other than 1 (i += k)"
    for s in subs:
        if "<<" in s:
            return "strided", "shifted index ([i << k])"
    for s in subs:
        if "*" in s and not s.strip().startswith("*"):
            return "strided", "multiplied index ([2 * i], [i * n + j])"
    for s in subs:
        if re.search(r"[A-Za-z_]\w*\s*[+-]\s*[A-Za-z_]\w*", s):
            return "strided", "counter plus another variable ([i + j])"

    if origin == "libc++":
        return "other", "loop inside libc++'s own code"
    if _EXIT.search(text) or "&&" in control or "||" in control:
        return "other", "early exit (break/return or a compound condition)"
    stripped = head.lstrip()
    if stripped.startswith("while") or stripped.startswith("do"):
        return "other", "while/do loop"
    if not subs:
        return "other", "no subscript (iterator, pointer or range loop)"
    if re.search(r"<=?|!=", control) and "size()" not in control and "end()" not in control:
        return "other", "forward loop bounded by a variable, not the container's size()"
    return "other", "unclear from the text"
