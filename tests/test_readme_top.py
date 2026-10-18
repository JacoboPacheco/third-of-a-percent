"""The README's first lines say, in plain words, what the project is, who it is for and what to do first.

The numbers in these sentences are tied to the data in test_readme_numbers.py; this file guards the wording that carries
the structure: what a bounds check is and how it relates to Google's average, the kind of project, the audience, one
first step, the status line with its exact disclosure sentence, no numbered start list, and the order of the commands
under "Check it yourself" (the live page needs nothing installed; the rest is marked optional, then the local check, then the re-measurement)."""
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCLOSURE = "Code written by AI coding agents directed by the author."


def lines():
    with open(os.path.join(REPO, "README.md"), encoding="utf-8") as f:
        return f.read().splitlines()


def top():
    return lines()[:80]


def before_first_heading():
    t = top()
    return t[:next(i for i, ln in enumerate(t) if ln.startswith("## "))]


def test_opening_defines_the_check_and_sets_google_beside_the_loop_range():
    para = next(ln for ln in before_first_heading() if ln.startswith("A bounds check makes a C++ program stop if an index is out of range;"))
    for needed in ("libc++ hardening turns these checks on in the standard library",
                   "0.30% on average across its services, a third of a percent",
                   "Measured one loop at a time",
                   "(reverse, stride-2, matrix multiply)",
                   "(x86-64, one compiler version, data that fits in the CPU cache)",
                   "one command that re-checks every stored measurement and verdict",
                   "(what it does not cover is listed under \"Check it yourself\")"):
        assert needed in para, f"the opening paragraph lost: {needed}"


def test_kind_audience_and_one_first_step_come_before_the_first_heading():
    head = before_first_heading()
    line = next(ln for ln in head if ln.startswith("A measurement study, not a library or a tool to install, for C++ engineers and tech leads deciding whether to turn on libc++ hardening."))
    assert line.count("**Start here:") == 1
    start = line[line.index("**Start here:"):]
    assert "https://jacobopacheco.github.io/third-of-a-percent/" in start
    assert start.endswith("Switch the check off and on, then pick a loop to read its machine code.")


def test_no_numbered_or_ordered_start_list_before_the_first_heading():
    for ln in before_first_heading():
        assert not re.match(r"^\s*(\d+[.)]|[-*])\s", ln), f"the start text is a list: {ln[:60]}"
    assert "in this order" not in "\n".join(before_first_heading()).lower()


def test_status_line_carries_the_exact_disclosure_once_in_the_top():
    t = top()
    status = [ln for ln in t if ln.startswith("Status: work in progress")]
    assert len(status) == 1 and status[0].endswith(DISCLOSURE)
    assert sum(ln.count(DISCLOSURE) for ln in t) == 1


def test_check_it_yourself_says_it_is_optional_and_orders_the_local_check_and_the_rerun():
    text = "\n".join(lines())
    assert "## Try it" not in text
    section = text.split("## Check it yourself", 1)[1].split("\n## ", 1)[0]
    assert section.lstrip().startswith("The live page above needs nothing installed. The rest of this section is optional, for re-checking the numbers:")
    assert section.index("python scripts/check.py") < section.index("gh workflow run measure.yml")
    assert section.index("The live page above needs nothing installed") < section.index("python scripts/check.py")


def test_the_how_much_to_trust_it_heading_is_not_left_alone_at_the_end_of_the_first_80_lines():
    t = lines()
    i = next(n for n, ln in enumerate(t) if ln == "## How much to trust it")
    first_bullet = next(n for n in range(i + 1, len(t)) if t[n].startswith("- "))
    assert first_bullet < 80, f"the section's first bullet is on line {first_bullet + 1}, past the first 80 lines"


def test_the_intel_and_arm_results_sit_under_their_own_heading_not_in_the_three_sentences():
    text = "\n".join(lines())
    section = text.split("## In three sentences", 1)[1].split("\n## ", 1)[0]
    sentences = [ln for ln in section.splitlines() if re.match(r"^[123]\. ", ln)]
    assert len(sentences) == 3
    assert all("Xeon" not in s and "Neoverse" not in s and "Arm" not in s and "Intel" not in s for s in sentences)
    assert "[Results by CPU model](#results-by-cpu-model)" in section
    by_cpu = text.split("## Results by CPU model", 1)[1].split("\n## ", 1)[0]
    assert "Intel:" in by_cpu and "Arm (a separate column" in by_cpu
