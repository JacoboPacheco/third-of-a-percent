"""Cuts one function out of `objdump -d` output, counts its check traps and diffs two builds.

A libc++ hardening check that fails ends in a trap. With libc++ 18 in FAST mode the trap is the
`ud2` instruction on x86-64 (day-one test: no calls to __libcpp_verbose_abort were found) and
`brk #0x1` on AArch64; calls to __libcpp_verbose_abort are counted as well.
"""
import difflib
import re


def function_lines(objdump_text, name):
    """The lines of the function whose mangled name contains `name` (e.g. kern_k04_rev),
    from its header line to the blank line that ends it."""
    head = re.compile(r"^[0-9a-f]+ <(_Z\d+%s[^>]*)>:$" % re.escape(name))
    lines, keep = [], False
    for ln in objdump_text.splitlines():
        if not keep and head.match(ln):
            keep = True
            lines.append(ln)
            continue
        if keep:
            if not ln.strip():
                break
            lines.append(ln)
    return lines


def count_traps(lines):
    """Number of trap instructions (x86-64 ud2, AArch64 brk #0x1) plus calls to __libcpp_verbose_abort
    (x86-64 call, AArch64 bl) in the given lines."""
    traps = sum(1 for ln in lines if re.search(r"\bud2\b", ln) or re.search(r"\bbrk\s+#0x1\b", ln))
    va = sum(1 for ln in lines if re.search(r"\b(call|bl)\b", ln) and "verbose_abort" in ln)
    return traps + va


def normalize(lines):
    """Drops addresses and jump offsets, so a diff shows changed instructions, not moved ones."""
    out = []
    for ln in lines:
        ln = re.sub(r"^\s*[0-9a-f]+:\s*", "", ln)
        ln = re.sub(r"\b[0-9a-f]{4,} <", "<", ln)
        ln = re.sub(r"<([^>+]*)\+0x[0-9a-f]+>", r"<\1+off>", ln)
        out.append(ln.rstrip())
    return out


def unified_diff(none_lines, fast_lines, none_name, fast_name):
    """Unified diff of the normalized NONE and FAST function bodies, as one string."""
    diff = difflib.unified_diff(normalize(none_lines), normalize(fast_lines), none_name, fast_name, lineterm="")
    return "\n".join(diff) + "\n"
