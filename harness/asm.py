"""Cuts one function out of `objdump -d` output, counts its check traps and diffs two builds.

A libc++ hardening check that fails ends in a trap. With libc++ 18 in FAST mode the trap is the
`ud2` instruction (day-one test: no calls to __libcpp_verbose_abort were found); both are counted.
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
    """Number of ud2 instructions plus calls to __libcpp_verbose_abort in the given lines."""
    ud2 = sum(1 for ln in lines if re.search(r"\bud2\b", ln))
    va = sum(1 for ln in lines if "call" in ln and "verbose_abort" in ln)
    return ud2 + va


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
