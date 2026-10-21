"""The page's pointer to tools/lostloops/ and the break-even arithmetic in section 10 are tied to the files they come from.

Break-even: loops that take r times as long with the check on and hold a share f of a program's run time add f * (r - 1) to it, so an average
of g per cent needs f = g / (r - 1). The page prints f at the two ends of the headline range. This file recomputes r from the pooled file
(not from site/data/index.json), g from the claim, and f from both, and compares them with page.break_even in index.json and with the numbers
printed in the served HTML of site/index.html. It is arithmetic: the file does not read a measurement of any program's share f.

The pointer: the command, the limits and the word "untested" on the page, in the README's top and in the details are compared with the
tool's own README and example workflow. The page's same checks, with the rendered page and its two links, are in scripts/check_site.py
(pinned_text_checks). The cited-path guard that keeps the example workflow's path real is in tests/test_readme_numbers.py.

Read-only and offline.
"""
import html as htmllib
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOLED = "results/s7-pooled/pooled.json"
TOOL_README = "tools/lostloops/README.md"
TOOL_WORKFLOW = "tools/lostloops/example-workflow.yml"
COMMAND = re.compile(r"^(python3 lostloops\.py --compile-commands \S+ --out \S+)$", re.M)


def text(rel):
    with open(os.path.join(REPO, *rel.split("/")), encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def data(rel):
    return json.loads(text(rel))


def page_html():
    return text("site/index.html")


def headline_range():
    """The lowest and highest ratio of a lost loop over the CPU models with enough jobs, in both columns, read from the pooled file."""
    index = data("site/data/index.json")
    minimum = index["criteria"]["minimum_jobs"]
    values = [c[column]["ratio"] for cpu in data(POOLED)["cpus"] if cpu["jobs"] >= minimum
              for c in cpu["cells"] if c["class"] == "lost" for column in ("as_compiled", "aligned")]
    return min(values), max(values)


def shares():
    index = data("site/data/index.json")
    g = index["claim"]["google_pct"]
    lo, hi = headline_range()
    return g, lo, hi, g / (lo - 1), g / (hi - 1)


def span(html, name):
    """The texts of the data-v spans of one name in a served HTML file."""
    return re.findall(r'<span data-v="' + name + r'"[^>]*>([^<]*)</span>', html)


def paragraph(html, pid):
    m = re.search(r'<p id="' + pid + r'">(.*?)</p>', html, re.S)
    assert m, f"site/index.html has no paragraph with id {pid}"
    return m.group(1)


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def test_the_break_even_shares_are_recomputed_from_the_pooled_file():
    g, lo, hi, f_lo, f_hi = shares()
    be = data("site/data/index.json")["page"]["break_even"]
    assert be["google_pct"] == g
    assert abs(be["at_min"]["r"] - lo) < 1e-9 and abs(be["at_max"]["r"] - hi) < 1e-9, "the r values are not the pooled file's lowest and highest lost-loop ratios"
    assert abs(be["at_min"]["share_pct"] - f_lo) < 1e-9, f"share at the lowest r: index.json {be['at_min']['share_pct']}, recomputed {f_lo}"
    assert abs(be["at_max"]["share_pct"] - f_hi) < 1e-9, f"share at the highest r: index.json {be['at_max']['share_pct']}, recomputed {f_hi}"
    # sanity of the arithmetic itself: the average of a program whose only slow part is that share is the claim again
    assert abs(f_lo * (lo - 1) - g) < 1e-9 and abs(f_hi * (hi - 1) - g) < 1e-9


def test_the_break_even_paragraph_prints_those_numbers_and_nothing_else():
    g, lo, hi, f_lo, f_hi = shares()
    par = paragraph(page_html(), "break-even")
    assert span(par, "beLo") == [f"{f_lo:.2g}"], f"the page prints {span(par, 'beLo')} for the share at the lowest r; the data give {f_lo:.2g}"
    assert span(par, "beHi") == [f"{f_hi:.2g}"], f"the page prints {span(par, 'beHi')} for the share at the highest r; the data give {f_hi:.2g}"
    assert span(par, "lostMin") == [f"{lo:.1f}"] and span(par, "lostMax") == [f"{hi:.1f}"], "the r values printed are not the headline range"
    assert span(par, "googlePct") == [f"{g:.2f}", f"{g:.2f}"]
    # a reader who redoes the sum with the printed r gets the printed share
    assert f"{g / (float(f'{lo:.1f}') - 1):.2g}" == f"{f_lo:.2g}" and f"{g / (float(f'{hi:.1f}') - 1):.2g}" == f"{f_hi:.2g}"
    plain = squash(re.sub(r"<[^>]+>", "", par))
    assert "not a measurement or prediction for any program" in plain
    assert not re.search(r"\b(because|caused?|due to|explains?)\b", plain), "the arithmetic paragraph says nothing about what costs a program"
    # every digit in it is one of the numbers above or the formula's 1
    digits = re.sub(r"<span data-v=\"\w+\"[^>]*>[^<]*</span>", "", par)
    assert not re.search(r"\d", re.sub(r"<[^>]+>", "", digits).replace("&minus;1", "")), f"a number typed into the break-even paragraph: {digits}"


def test_the_break_even_paragraph_is_in_section_ten_and_the_pointer_in_section_four():
    html = page_html()
    sections = re.split(r'<section\b', html)
    owner = {}
    for s in sections[1:]:
        sid = re.match(r'[^>]*\bid="([^"]+)"', s)
        for pid in ("break-even", "find-loops"):
            if f'id="{pid}"' in s and sid:
                owner[pid] = sid.group(1)
    assert owner == {"break-even": "average", "find-loops": "census"}, owner


def tool_command():
    m = COMMAND.search(text(TOOL_README))
    assert m, "the tool's README has no command line of the form python3 lostloops.py --compile-commands X --out Y"
    return m.group(1)


def test_the_command_on_the_page_the_readme_and_the_details_is_the_tools_own():
    cmd = tool_command()
    # the flags are the ones the tool accepts
    src = text("tools/lostloops/lostloops.py")
    assert '"--compile-commands"' in src and '"--out"' in src, "the command uses a flag the tool does not define"
    page = squash(re.sub(r"<[^>]+>", "", paragraph(page_html(), "find-loops")))
    assert cmd in page, "the page's pointer does not carry the tool README's command"
    assert cmd in text("README.md") and cmd in text("readme-parts/DETAILS.md"), "the README or the details do not carry the tool README's command"


def test_the_limits_named_in_the_pointers_are_the_tools_own():
    tool = text(TOOL_README)
    # what the tool's own README says: these are the sources of every limit the pointers state
    for phrase in ("Linux, with Python 3.8+, clang 18 or newer and libc++ 18 or newer", "**Counts, not time.**", "`-flto*`", "tested live once",
                   "on leveldb, Spectra and LightGBM", "(documentation only; it is not run here)"):
        assert phrase in tool, f"the tool's README no longer says {phrase!r}"
    assert "NOT tested yet" in text(TOOL_WORKFLOW), "the example workflow no longer says it is not tested, but the pointers call it untested"
    # the page's pointer, as a reader sees it
    pointer = squash(htmllib.unescape(re.sub(r"<[^>]+>", "", paragraph(page_html(), "find-loops"))))
    for own in ("Linux, clang and libc++ only", "counts loops, not time", "link-time optimization flags removed", "tested once, on three projects", "untested"):
        assert own in pointer, f"the page's pointer does not state {own!r}"
    # the README's top, in its first 80 lines
    top = "\n".join(text("README.md").split("\n")[:80])
    for own in ("Linux, clang and libc++ 18 or newer", "counts loops, not time", "link-time optimization flags are removed", "tested once, on three projects", "documentation only"):
        assert own in top, f"the README's top (first 80 lines) does not state {own!r}"
    # the details
    details = text("readme-parts/DETAILS.md")
    for own in ("Linux with clang and libc++ 18 or newer", "counts loops, not time", "documentation only and was not run"):
        assert own in details, f"the details do not state {own!r}"


def test_the_readme_top_points_at_the_tool_and_its_example_workflow_in_an_existing_line():
    lines = text("README.md").split("\n")
    top = lines[:80]
    hits = [n for n, ln in enumerate(top) if "`tools/lostloops/`" in ln and f"`{TOOL_WORKFLOW}`" in ln]
    assert len(hits) == 1, f"the pointer to tools/lostloops/ and its example workflow is on {len(hits)} lines of the README's first 80"
    assert lines[hits[0]].startswith("- **1 of 593**"), "the pointer sits in the census bullet, not on a line of its own"


def test_the_details_point_at_the_example_workflow_in_the_tool_paragraph():
    lines = [ln for ln in text("readme-parts/DETAILS.md").split("\n") if ln.startswith("- **The lostloops tool, run live")]
    assert len(lines) == 1 and f"`{TOOL_WORKFLOW}`" in lines[0] and "was not run" in lines[0], "the tool paragraph of the details does not say the example workflow was not run"
