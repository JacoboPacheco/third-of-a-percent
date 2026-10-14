"""Cuts one function out of `objdump -d` output, counts its check traps and diffs two builds.

Copied from harness/asm.py for the sibling toolchains, with two changes:
- GCC may move the failure path of a check into a separate `[clone .cold]` block, or clone the
  function (.isra, .constprop). `function_blocks` returns every block whose symbol carries the name;
  the main body (`main_block`) is the largest block that is not `.cold`, and traps are counted over
  all blocks.
- Traps: libc++ ends a failed check in `ud2` (FAST, EXTENSIVE) or a call to __libcpp_verbose_abort;
  libstdc++ with _GLIBCXX_ASSERTIONS calls std::__glibcxx_assert_fail (GCC 13 and later) or, in
  older headers, __replacement_assert / abort. All of them are counted, and listed separately.
"""
import difflib
import re

_TRAP_CALLS = ("verbose_abort", "__glibcxx_assert_fail", "__replacement_assert", "<abort", "__assert_fail")


def function_blocks(objdump_text, name):
    """{symbol: [lines]} for every function whose symbol contains `name` (mangled, e.g. _Z12kern_k04_rev...)."""
    head = re.compile(r"^[0-9a-f]+ <([^>]*%s[^>]*)>:$" % re.escape(name))
    blocks, cur = {}, None
    for ln in objdump_text.splitlines():
        m = head.match(ln)
        if m:
            cur = m.group(1)
            blocks[cur] = [ln]
            continue
        if cur is not None:
            if not ln.strip():
                cur = None
                continue
            blocks[cur].append(ln)
    return blocks


def main_block(blocks):
    """The lines of the main body: the largest block that is not a .cold part."""
    hot = {k: v for k, v in blocks.items() if ".cold" not in k}
    if not hot:
        return []
    return max(hot.values(), key=len)


def trap_counts(lines):
    """{"ud2": n, "calls": n, "total": n}: ud2 instructions and calls to a check-failure function."""
    ud2 = sum(1 for ln in lines if re.search(r"\bud2\b", ln))
    calls = sum(1 for ln in lines if re.search(r"\b(call|jmp)", ln) and any(t in ln for t in _TRAP_CALLS))
    return {"ud2": ud2, "calls": calls, "total": ud2 + calls}


def normalize(lines):
    """Drops addresses and jump offsets, so a diff shows changed instructions, not moved ones."""
    out = []
    for ln in lines:
        ln = re.sub(r"^\s*[0-9a-f]+:\s*", "", ln)
        ln = re.sub(r"\b[0-9a-f]{4,} <", "<", ln)
        ln = re.sub(r"<([^>+]*)\+0x[0-9a-f]+>", r"<\1+off>", ln)
        out.append(ln.rstrip())
    return out


def unified_diff(a_lines, b_lines, a_name, b_name):
    """Unified diff of two normalized function bodies, as one string."""
    diff = difflib.unified_diff(normalize(a_lines), normalize(b_lines), a_name, b_name, lineterm="")
    return "\n".join(diff) + "\n"
