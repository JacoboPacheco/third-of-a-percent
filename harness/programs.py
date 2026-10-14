"""The two real programs: what they are, how they are pinned, and the pure arithmetic their rows need.

harness/run.py does the building and timing (the same NONE and FAST flags, the same 20 alternating
processes per side, the same bootstrap as the kernels). This module holds what can be tested on
a laptop without a compiler:

- PROGRAMS: name, pin, source, include directory, arguments and input of each program. The pinned
  downloads and their sha256 live in programs/<name>/fetch.sh; tests/test_programs.py checks that
  every sha256 in a fetch.sh appears in the pin string here, so the two cannot drift.
- consistent_with_at_most_pct(): the only whole-program number results.json prints.
- per_iteration_ir(): Cachegrind instructions of one parse or format, with start-up removed.
- remark_counts(): how many loops clang vectorized or refused in the whole program.

The rule for the whole-program number (written before the first S2 run). A shared runner's A/A
floor for a whole program was 1.14 % on the day-one run, well above 0.30 %, so a program row can
never confirm 0.30 %. It is printed only as an upper bound:
    consistent_with_at_most_pct = max(0, 100 * (ci95_hi - 1), aa_half_width_pct)
that is, the top of the FAST/NONE interval, but never a number smaller than the program's own
A/A noise floor (a bound below the floor would claim a precision the run does not have).
"""
import re

PROGRAMS = {
    "json_parse": {
        "pin": ("nlohmann/json v3.11.3 (tag commit 9cca280a4d0ccf0c08f47a99aa71d1b0e52f8d03; json.hpp release asset "
                "sha256 9bea4c8066ef4a1c206b2be5a36302f8926f7fdc6087af5d20b417d0cf103ea6) parsing twitter.json from "
                "simdjson v3.10.1 (tag commit e341c8b43861b43de29c48ab65f292d997096953; "
                "sha256 30721e496a8d73cfc50658923c34eb2c0fbe15ee6835005e43ee624d8dedf200)"),
        "source": "programs/json_parse/json_parse.cpp",
        "include": "json_parse",            # under the deps directory
        "input": "json_parse/twitter.json",  # under the deps directory; hashed as input_sha256
        "args": ["{input}"],                 # the inner-iteration count is appended
    },
    "fmt_format": {
        "pin": ("{fmt} 11.0.2 (tag commit 0c9fce2ffefecfdce794e1859584e25877b7b592; source archive "
                "sha256 6cb1e6d37bdcb756dbbe59be438790db409cdb4868c66e888d5df9f13f7c027f), header-only, "
                "formatting 20000 seeded int64 and double values"),
        "source": "programs/fmt_format/fmt_format.cpp",
        "include": "fmt_format/fmt/include",
        "input": None,                       # generated from a fixed seed; dumped and hashed by run.py
        "args": ["20000"],
    },
}
ALL_PROGRAMS = list(PROGRAMS)
CG_EXTRA_ITERS = 2  # Cachegrind runs with 1 and 1 + CG_EXTRA_ITERS inner iterations


def consistent_with_at_most_pct(ci95, aa_half_width_pct):
    """The upper bound printed for a whole program (see the module docstring for the rule)."""
    bound = 100.0 * (ci95[1] - 1.0)
    floor = aa_half_width_pct if aa_half_width_pct is not None else 0.0
    return max(0.0, bound, floor)


def summary_ir(text):
    """Total Ir from a Cachegrind output file's `summary:` line (first event column). None if absent."""
    events = None
    for line in text.splitlines():
        if line.startswith("events:"):
            events = line.split(":", 1)[1].split()
        elif line.startswith("summary:"):
            vals = line.split(":", 1)[1].split()
            idx = events.index("Ir") if events and "Ir" in events else 0
            try:
                return int(vals[idx])
            except (IndexError, ValueError):
                return None
    return None


def per_iteration_ir(ir_one, ir_more, extra_iters=CG_EXTRA_ITERS):
    """Instructions of one timed iteration: (Ir with 1 + extra iterations - Ir with 1) / extra.

    Both runs include process start, reading the input and the untimed warm-up, so the difference
    is the timed loop alone. Returns None if either count is missing or the difference is not positive.
    """
    if ir_one is None or ir_more is None or extra_iters < 1:
        return None
    d = ir_more - ir_one
    return int(round(d / extra_iters)) if d > 0 else None


_REMARK = re.compile(r"^(\S+:\d+:\d+): remark: (.*?)\s*\[(-Rpass(?:-missed)?=loop-vectorize)\]\s*$")


def remark_counts(stderr):
    """Counts of distinct loop locations over a whole program build: {"vectorized", "not_vectorized"}.

    A location counts as vectorized when clang printed "vectorized loop" for it (-Rpass), and as not
    vectorized when it printed a -Rpass-missed remark for it and no "vectorized loop". The
    -Rpass-analysis lines (the reasons) are not counted, so one refused loop counts once.
    Includes loops in the library headers (libc++, nlohmann/json, fmt) and template instances at the
    same source location count once: a coarse view kept in details.json, not in results.json.
    """
    vec, missed = set(), set()
    for ln in stderr.splitlines():
        m = _REMARK.match(ln.strip())
        if not m:
            continue
        loc, msg, kind = m.groups()
        if kind == "-Rpass=loop-vectorize" and msg.startswith("vectorized loop"):
            vec.add(loc)
        elif kind == "-Rpass-missed=loop-vectorize":
            missed.add(loc)
    return {"vectorized": len(vec), "not_vectorized": len(missed - vec)}
