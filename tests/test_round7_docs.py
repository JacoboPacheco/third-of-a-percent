"""Tamper tests for the round 7 wording of README.md, readme-parts/DETAILS.md and arm64/README.md.

The sentences that quote the three stored readings of round 7 (robustness/seed-sensitivity-x86.json, robustness/aa-l2.json,
robustness/calibration.json) are tied to those files by rows of tests/test_readme_numbers.py. A row that matches its anchor and
checks nothing would be worse than no row, so this file changes every typed number of every one of those rows, one at a time,
in a copy of the text held in memory, and requires the row to fail with the typed-number message (not only with "the anchor no
longer matches"). It does the same for the A/A table, the cited paths and the sentences pinned word for word.

Nothing is written; the documents on disk are read only.
"""

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_readme_numbers as T  # noqa: E402

NUMBER_WORDS = {w: i for i, w in T.WORDS.items()}
NEXT_WORD = {w: T.WORDS[i + 1] for w, i in NUMBER_WORDS.items() if i + 1 in T.WORDS}
VERDICT_SWAP = {"MAP": "INCONCLUSIVE", "INCONCLUSIVE": "MAP"}

README_LABELS = (
    "sentence 3: Intel forward add",
    "trust: independence and holdout",
    "trust: floors, sizes and builds, the A/A at L2",
    "trust: what MAP and INCONCLUSIVE cover, the closing sentence (seeds, subsets, the A/A at L2)",
    "folders: the seed re-draws in robustness/",
)
DETAILS_LABELS = (
    "details: table, EPYC 9V45 borderline",
    "details: table, Xeon 6973P-C verdict",
    "details: table, the note on the Intel rows",
    "details: replication, why",
)


def rows_by_label(rows, labels):
    found = {r[0]: r for r in rows}
    missing = [lb for lb in labels if lb not in found]
    assert not missing, f"rows of tests/test_readme_numbers.py are gone or renamed: {missing}"
    return [found[lb] for lb in labels]


def alter(value):
    """A different value of the same kind: the last digit moved, a number word moved to the next one, a verdict word swapped; None if the text is none of these."""
    if re.fullmatch(r"[\d.,]*\d[\d.,]*", value):  # a number; a name that holds digits (EPYC 7763 and 9V74) is not one
        i = max(m.start() for m in re.finditer(r"\d", value))
        return value[:i] + str((int(value[i]) + 1) % 10) + value[i + 1:]
    if value.lower() in NEXT_WORD:
        new = NEXT_WORD[value.lower()]
        return new.capitalize() if value[0].isupper() else new
    return VERDICT_SWAP.get(value)


def tampered_cases():
    """(id, row, doc, text, group) for every group of every round 7 row that carries a number, a number word or a verdict word."""
    suites = (
        (rows_by_label(T.ROWS, README_LABELS), "README.md", T.readme_text),
        (rows_by_label(T.DETAILS_ROWS, DETAILS_LABELS) + list(T.ROUND7_DETAILS_ROWS), "readme-parts/DETAILS.md", T.details_text),
        (list(T.ARM64_ROUND7_ROWS), "arm64/README.md", T.arm64_text),
    )
    cases = []
    for rows, doc, getter in suites:
        text = getter()
        for row in rows:
            m = re.search(row[3], text, re.S)
            assert m, f"{row[0]}: the anchor does not match {doc}"
            groups = [g for g in m.re.groupindex if alter(m.group(g)) is not None]
            assert groups, f"{row[0]}: the row has no typed number to tamper with"
            for g in groups:
                cases.append(pytest.param(row, doc, text, g, id=f"{doc}: {row[0]} / {g}={m.group(g)}"))
    return cases


@pytest.mark.parametrize("row,doc,text,group", tampered_cases())
def test_changing_one_typed_number_fails_its_row(row, doc, text, group):
    check = lambda t: T.check_row(row, t, doc)  # noqa: E731
    check(text)  # the real text passes
    m = re.search(row[3], text, re.S)
    a, b = m.span(group)
    new = alter(m.group(group))
    bad = text[:a] + new + text[b:]
    with pytest.raises(AssertionError) as err:
        check(bad)
    assert f"types '{new}' for '{group}'" in str(err.value), f"{row[0]}: the row failed, but not on the typed value of '{group}': {str(err.value)[:200]}"


# ---- the A/A table of the details --------------------------------------------------------------------

def aa_l2_block_lines(text):
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip() == T.AA_L2_TABLE_HEADER)
    return lines, start


def test_the_aa_l2_table_fails_when_a_cell_a_row_or_the_order_changes():
    text = T.details_text()
    rows = T.aa_l2_table_rows()
    T.check_table_rows("details: the A/A at L1 and L2", rows, text, "readme-parts/DETAILS.md")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines, start = aa_l2_block_lines(text)
    first = start + 2  # the first data row, under the header and the separator
    assert lines[first].startswith("| AMD EPYC 7763 |")

    def run(new_lines):
        T.check_table_rows("details: the A/A at L1 and L2", rows, nl.join(new_lines), "readme-parts/DETAILS.md")

    cell = lines[:]
    cell[first] = re.sub(r"(\d+\.\d+)%", lambda m: f"{float(m.group(1)) + 0.001:.3f}%", lines[first], count=1)
    assert cell[first] != lines[first]
    with pytest.raises(AssertionError):
        run(cell)
    last = first + len(rows) - 2
    assert lines[last].startswith("| Arm Neoverse-N2 |") and not lines[last + 1].startswith("|"), "the table no longer ends with the Arm core"
    dropped = lines[:last] + lines[last + 1:]
    with pytest.raises(AssertionError):
        run(dropped)
    swapped = lines[:]
    swapped[first], swapped[first + 1] = lines[first + 1], lines[first]
    with pytest.raises(AssertionError):
        run(swapped)
    jobs = lines[:]
    jobs[last] = re.sub(r"\| (\d+) \|", lambda m: f"| {int(m.group(1)) + 1} |", lines[last], count=1)
    assert jobs[last] != lines[last]
    with pytest.raises(AssertionError):
        run(jobs)


def test_the_aa_l2_table_has_one_row_per_pooled_model():
    """The table lists every model of the two pools that the rule gives a verdict to, by the same job counts as the pooled files."""
    s7 = T.aa_l2_pool("s7")
    keys = {key for _, pool, key in T.AA_L2_TABLE_ROWS if pool == "s7"}
    enough = {m["cpu_model"] for m in s7["models"] if m["jobs"] >= T.J("site/data/index.json")["criteria"]["minimum_jobs"] and any(k in m["cpu_model"] for k in keys)}
    assert len(enough) == len(keys), "the A/A pool holds a model with a verdict-sized job count that the details table does not list (or the reverse)"


# ---- the cited paths ---------------------------------------------------------------------------------

ROUND7_PATHS = ("robustness/seeds_x86.py", "robustness/aa_l2.py", "robustness/calibration.py", "robustness/seed-sensitivity-x86.json",
                "robustness/aa-l2.json", "robustness/calibration.json", "robustness/README-calibration.md")


def test_the_round7_paths_are_cited_and_a_misspelling_is_caught():
    cited = set()
    for doc in ("README.md", "readme-parts/DETAILS.md"):
        cited |= {rel for _, rel in T.cited_paths(doc)}
    cited |= {rel for _, rel in T.cited_paths_in(T.arm64_text(), "arm64/README.md")}
    named = [p for p in ROUND7_PATHS if p in cited]
    assert "robustness/README-calibration.md" in named and "robustness/aa-l2.json" in named and "robustness/seeds_x86.py" in named, \
        f"the documents no longer cite the round 7 files by path: {named}"
    for p in ROUND7_PATHS:
        assert os.path.exists(os.path.join(T.REPO, p)), f"{p} is gone"
        assert T.missing_cited(f"`{p}`") == []
        bad = p.replace("robustness/", "robustness/x") if p.endswith("md") else p[:-1]
        assert T.missing_cited(f"`{bad}`") == [bad], f"a misspelled {p} is not caught"
    assert T.missing_cited("[calibration](robustness/README-calibrations.md)") == ["robustness/README-calibrations.md"]
    assert T.missing_cited("([calibration baseline](../robustness/README-calibration.md))", "arm64/README.md") == []
    assert T.missing_cited("([calibration baseline](../robustness/README-calibratio.md))", "arm64/README.md") == ["../robustness/README-calibratio.md"]


# ---- sentences pinned word for word ------------------------------------------------------------------

ROUND7_PINNED = ("undecided", "exactly calibrated", "ceiling clause", "lie inside that range", "against 53.8", "against 34.7")


def test_the_round7_sentences_are_pinned_and_a_reversal_is_caught():
    entries = [e for e in T.guarded_sentences() if any(w in e["sentence"] for w in ROUND7_PINNED) or "against 61.7 expected" in e["sentence"]]
    assert len(entries) >= 7, f"only {len(entries)} pinned sentences carry the round 7 wording"
    for e in entries:
        T.check_guarded_sentence(e)
        text = T.GUARDED_DOCS[e["doc"]]()
        flat = T.squash(text)
        sentence = T.squash(e["sentence"])
        assert sentence in flat
        for old, new in (("undecided", "decided"), ("below", "above"), ("inside", "outside"), ("would", "would not"), ("is not changed", "is changed"),
                         ("not in the forward", "in the forward")):
            if old in sentence:
                broken = flat.replace(sentence, sentence.replace(old, new, 1))
                assert sentence not in broken
                with pytest.raises(AssertionError):
                    entry_text = {**T.GUARDED_DOCS, e["doc"]: lambda broken=broken: broken}
                    original = T.GUARDED_DOCS
                    T.GUARDED_DOCS = entry_text
                    try:
                        T.check_guarded_sentence(e)
                    finally:
                        T.GUARDED_DOCS = original
                break
        else:
            pytest.fail(f"no reversal was tried on: {e['sentence'][:80]}")


# ---- the wording that was replaced -------------------------------------------------------------------

def test_no_document_still_says_the_intervals_understate_the_spread():
    """The calibration baseline supports 'understate' for EPYC 7763's lost-loop cells and the Arm stride-2 cells at L2 only; the flat sentence is gone."""
    flat = re.compile(r"intervals (?:still )?understate", re.I)
    for doc, getter in (("README.md", T.readme_text), ("readme-parts/DETAILS.md", T.details_text), ("arm64/README.md", T.arm64_text),
                        ("siblings/README.md", T.siblings_text)):
        assert not flat.search(T.squash(getter())), f"{doc} says again that the intervals understate the spread, flat"


def test_the_calibration_readme_is_in_the_past_tense_and_keeps_the_required_phrase():
    with open(os.path.join(T.REPO, "robustness", "README-calibration.md"), encoding="utf-8") as f:
        text = f.read()
    flat = T.squash(text)
    assert "said that the pooled intervals understate run-to-run spread" in flat and "they have since been reworded to what this note supports" in flat, \
        "robustness/README-calibration.md no longer says that the sentence it examines was replaced"
    assert "say that the pooled intervals understate" not in flat, "robustness/README-calibration.md is in the present tense again"


# ---- the check hooks ---------------------------------------------------------------------------------

HOOKS = ("robustness/seeds_x86.py", "robustness/aa_l2.py", "robustness/calibration.py")


def test_scripts_check_runs_the_three_round7_analyses_with_verify():
    with open(os.path.join(T.REPO, "scripts", "check.py"), encoding="utf-8") as f:
        src = f.read()
    for script in HOOKS:
        # the call itself, not the docstring that names it: a subprocess call list holding the script and --verify, and a missing_step beside it
        folder, name = script.split("/")
        calls = [m.start() for m in re.finditer(r"subprocess\.call\(\[sys\.executable, os\.path\.join\(REPO, \"" + folder + r"\", \"" + re.escape(name) + r"\"\), [^\]]*\]", src)]
        assert calls, f"scripts/check.py does not run {script}"
        i = calls[0]
        assert "--verify" in src[i:i + 300], f"scripts/check.py runs {script} without --verify"
        assert "missing_step" in src[i:i + 900], f"scripts/check.py does not report a missing {script} as a skipped step"
        assert os.path.exists(os.path.join(T.REPO, script))


def test_scripts_check_recomputes_the_cells_of_both_models_whose_word_rests_on_a_cell_near_a_line():
    """The DETAILS figures for the Xeon 6973P-C and for the EPYC 9V45 are tied to robustness/seed-sensitivity-x86.json; check.py has to recompute both models' cells."""
    with open(os.path.join(T.REPO, "scripts", "check.py"), encoding="utf-8") as f:
        src = f.read()
    assert re.search(r"for model in \(\"6973P\", \"9V45\"\):\s+ok &= subprocess\.call\(\[sys\.executable, os\.path\.join\(REPO, \"robustness\", \"seeds_x86\.py\"\), "
                     r"\"--verify\", \"--model\", model, \"--whole\", \"1\"\]\) == 0", src), \
        "scripts/check.py no longer runs robustness/seeds_x86.py --verify for both the 6973P and the 9V45 cells"


def test_the_folder_map_names_the_three_round7_readings():
    text = T.squash(T.readme_text())
    for name in ("seeds_x86.py", "aa_l2.py", "calibration.py", "seed-sensitivity-x86.json", "aa-l2.json", "calibration.json"):
        assert name in text, f"the README's folder map no longer names {name}"
    assert "interval ends re-drawn under" in text
