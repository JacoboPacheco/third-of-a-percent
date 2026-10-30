"""The "2.8x to 8.0x" range, and the statement that it covers both columns (as compiled and with the loops aligned).

The lowest and the highest ratio of a loop that loses SIMD (reverse, stride-2, matrix multiply; in cache) over the CPU models with
enough jobs are read from the pooled file the page reads (scripts/build_site_data.py names it) in both columns. The smallest of the
two columns' values has to be a cell as compiled and the largest a cell with the loops aligned, because the documents say so. The
range of each column and the two cells that set the printed ends are rebuilt from the file, and three places are tied to them:

- the README's third numbered claim (inside the first 80 lines), which says the smallest is as compiled and the largest aligned;
- the README's "Sizes" bullet, which gives the range of each column and names the two cells that set the ends;
- the DETAILS bullet "Loops that lose SIMD under the check pay several times over", which gives the range of each column.

Nothing is written. Each check has tamper tests: a changed number, word or column in a sentence, and a changed copy of the pooled
file, have to be named.

Runs with or without pytest (scripts/check.py's built-in runner, which CI uses, has none).
"""

import copy
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_readme_numbers as T  # noqa: E402

COLUMNS = ("as_compiled", "aligned")
KERNEL_WORDS = {"k04_rev": "reverse", "k05_stride2": "stride-2", "k08_matmul": "matrix-multiply"}
TOP_LINES = 80
DETAILS_BULLET = "- **Loops that lose SIMD under the check pay several times over.**"


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


def pooled_path():
    with open(os.path.join(T.REPO, "scripts", "build_site_data.py"), encoding="utf-8") as f:
        m = re.search(r'^POOLED = "([^"]+)"', f.read(), re.M)
    assert m, "scripts/build_site_data.py no longer names the pooled file the page reads"
    return m.group(1)


def pooled_file():
    return copy.deepcopy(T.J(pooled_path()))


def minimum_jobs():
    return T.J("site/data/index.json")["criteria"]["minimum_jobs"]


def lost_values(pooled, minimum):
    """(ratio, CPU model, cell id, column) of every lost-loop cell of every CPU model with at least `minimum` jobs, in both columns."""
    out = [(cell[column]["ratio"], cpu["cpu_model"], cell["cell_id"], column)
           for cpu in pooled["cpus"] if cpu["jobs"] >= minimum
           for cell in cpu["cells"] if cell["class"] == "lost" for column in COLUMNS]
    assert out, "the pooled file holds no lost-loop cell for a CPU model with enough jobs"
    return out


def facts(pooled, minimum):
    """The ends of the whole range, and the range of each column, with the cells that set them."""
    values = lost_values(pooled, minimum)
    lo, hi = min(values), max(values)
    assert lo[3] == "as_compiled" and hi[3] == "aligned", \
        f"the smallest ratio is a cell {lo[3]} and the largest one {hi[3]}: the documents say the smallest is as compiled and the largest aligned"
    per_column = {c: (min(v for v in values if v[3] == c), max(v for v in values if v[3] == c)) for c in COLUMNS}
    return lo, hi, per_column


def one(v):
    return f"{v[0]:.1f}"


def cell_words(v):
    """'EPYC 9V45 stride-2 loop at L1' for a cell tuple."""
    kernel, size = v[2].split(".")
    assert kernel in KERNEL_WORDS, f"no words for the kernel of {v[2]}: write them and extend KERNEL_WORDS"
    m = re.search(r"EPYC (\w+)", v[1])
    assert m, f"the end of the range is set by {v[1]}, which the sentence has no short name for"
    return f"EPYC {m.group(1)} {KERNEL_WORDS[kernel]} loop at {size}"


def readme_sizes_sentence(lo, hi, per_column):
    (c_lo, c_hi), (a_lo, a_hi) = per_column["as_compiled"], per_column["aligned"]
    return (f"The range covers both columns: as compiled the in-cache cells of these loops range "
            f"from {one(c_lo)}x to {one(c_hi)}x, with the loops aligned from {one(a_lo)}x to {one(a_hi)}x "
            f"(the lowest is the {cell_words(lo)} as compiled, {lo[0]:.2f}x; the highest the {cell_words(hi)} aligned, {hi[0]:.2f}x).")


def readme_top_clause(lo, hi):
    return (f"took {one(lo)} to {one(hi)} times as long in cache at the study's sizes "
            f"(the smallest as compiled, the largest with the loops aligned).")


def details_clause(lo, hi, per_column):
    (c_lo, c_hi), (a_lo, a_hi) = per_column["as_compiled"], per_column["aligned"]
    return (f"**{one(lo)}x to {one(hi)}x slower** on every x86-64 CPU model drawn (pooled over runs, `{pooled_path()}`); "
            f"the range covers both columns: {one(c_lo)}x to {one(c_hi)}x as compiled and {one(a_lo)}x to {one(a_hi)}x with the loops aligned.")


def check_readme(text, pooled, minimum):
    lo, hi, per_column = facts(pooled, minimum)
    flat = T.squash(text)
    top = T.squash("\n".join(text.splitlines()[:TOP_LINES]))
    clause = T.squash(readme_top_clause(lo, hi))
    assert top.count(clause) == 1, f"the README's first {TOP_LINES} lines do not say, once, {clause!r}"
    assert flat.count(clause) == 1, f"the README says {clause!r} {flat.count(clause)} times, not once"
    sentence = T.squash(readme_sizes_sentence(lo, hi, per_column))
    assert flat.count(sentence) == 1, f"the README does not hold, once, the Sizes sentence the pooled file gives:\n  {sentence}"
    assert flat.index(sentence) > flat.index(clause), "the Sizes sentence comes before the claim it qualifies"
    assert sentence not in top, f"the per-column figures are meant to sit below the first {TOP_LINES} lines"


def check_details(text, pooled, minimum):
    lo, hi, per_column = facts(pooled, minimum)
    flat = T.squash(text)
    clause = T.squash(details_clause(lo, hi, per_column))
    assert flat.count(clause) == 1, f"DETAILS does not hold, once, the clause the pooled file gives:\n  {clause}"
    bullets = [ln for ln in text.splitlines() if ln.startswith(DETAILS_BULLET)]
    assert len(bullets) == 1 and clause in T.squash(bullets[0]), f"the clause is not in the bullet that begins {DETAILS_BULLET}"


def test_the_ends_of_the_range_are_the_printed_ones_and_sit_in_the_two_columns():
    lo, hi, per_column = facts(pooled_file(), minimum_jobs())
    assert (one(lo), one(hi)) == ("2.8", "8.0"), f"the range is {one(lo)} to {one(hi)}, not the printed 2.8 to 8.0"
    assert lo[3] == "as_compiled" and hi[3] == "aligned"
    assert per_column["as_compiled"][0] == lo and per_column["aligned"][1] == hi
    assert one(per_column["as_compiled"][1]) == "7.7" and one(per_column["aligned"][0]) == "2.9"
    assert cell_words(lo) == "EPYC 9V45 stride-2 loop at L1" and cell_words(hi) == "EPYC 7763 reverse loop at L1"


def test_the_readme_gives_the_range_of_each_column():
    pooled, minimum = pooled_file(), minimum_jobs()
    check_readme(T.readme_text(), pooled, minimum)


def test_the_details_give_the_range_of_each_column():
    pooled, minimum = pooled_file(), minimum_jobs()
    check_details(T.details_text(), pooled, minimum)


def test_a_changed_sentence_is_caught():
    pooled, minimum = pooled_file(), minimum_jobs()
    lo, hi, per_column = facts(pooled, minimum)
    readme, details = T.readme_text(), T.details_text()
    sentence, clause = readme_sizes_sentence(lo, hi, per_column), readme_top_clause(lo, hi)
    dclause = details_clause(lo, hi, per_column)
    assert sentence in readme and clause in readme and dclause in details, \
        "a document holds the sentences with other whitespace than the rebuilt ones; the tamper tests need them verbatim"
    for what, old, new in (
            ("the as-compiled top changed", "range from 2.8x to 7.7x", "range from 2.9x to 7.7x"),
            ("the as-compiled end changed", "range from 2.8x to 7.7x", "range from 2.8x to 7.6x"),
            ("the aligned bottom changed", "with the loops aligned from 2.9x", "with the loops aligned from 2.8x"),
            ("the aligned top changed", "aligned from 2.9x to 8.0x", "aligned from 2.9x to 8.1x"),
            ("the columns swapped", "as compiled the in-cache cells of these loops range from 2.8x to 7.7x, with the loops aligned from 2.9x to 8.0x",
             "as compiled the in-cache cells of these loops range from 2.9x to 8.0x, with the loops aligned from 2.8x to 7.7x"),
            ("the lowest cell's CPU changed", "the lowest is the EPYC 9V45", "the lowest is the EPYC 9V74"),
            ("the lowest cell's kernel changed", "the EPYC 9V45 stride-2 loop", "the EPYC 9V45 reverse loop"),
            ("the lowest cell's ratio changed", "as compiled, 2.81x", "as compiled, 2.91x"),
            ("the highest cell's column changed", "loop at L1 aligned, 8.01x", "loop at L1 as compiled, 8.01x"),
            ("the highest cell's ratio changed", "aligned, 8.01x", "aligned, 8.11x"),
            ("the claim of both columns dropped", "The range covers both columns: ", "")):
        assert old in sentence, f"the tamper test no longer matches the Sizes sentence: {what}: {old}"
        assertion_from(lambda: check_readme(readme.replace(sentence, sentence.replace(old, new, 1), 1), pooled, minimum), f"README: {what}")
    for what, old, new in (
            ("the top clause dropped", clause, "took 2.8 to 8.0 times as long in cache at the study's sizes."),
            ("the column words swapped", "the smallest as compiled, the largest with the loops aligned", "the smallest with the loops aligned, the largest as compiled"),
            ("a number changed", "took 2.8 to 8.0 times", "took 2.8 to 8.1 times")):
        assert old in readme, f"the tamper test no longer matches the README: {what}: {old}"
        assertion_from(lambda: check_readme(readme.replace(old, new, 1), pooled, minimum), f"README: {what}")
    assertion_from(lambda: check_readme(readme + "\n" + sentence + "\n", pooled, minimum), "README: the Sizes sentence repeated")
    assertion_from(lambda: check_readme(readme.replace(sentence, ""), pooled, minimum), "README: the Sizes sentence deleted")
    for what, old, new in (
            ("the as-compiled end changed", "2.8x to 7.7x as compiled", "2.8x to 7.6x as compiled"),
            ("the aligned bottom changed", "2.9x to 8.0x with the loops aligned", "2.8x to 8.0x with the loops aligned"),
            ("the columns swapped", "2.8x to 7.7x as compiled and 2.9x to 8.0x with the loops aligned", "2.9x to 8.0x as compiled and 2.8x to 7.7x with the loops aligned"),
            ("the claim of both columns dropped", "the range covers both columns: ", ""),
            ("the pooled file changed", "`results/s7-pooled/pooled.json`", "`results/s6-pooled/pooled.json`")):
        assert old in dclause, f"the tamper test no longer matches the DETAILS clause: {what}: {old}"
        assertion_from(lambda: check_details(details.replace(dclause, dclause.replace(old, new, 1), 1), pooled, minimum), f"DETAILS: {what}")
    assertion_from(lambda: check_details(details.replace(dclause, ""), pooled, minimum), "DETAILS: the clause deleted")
    assertion_from(lambda: check_details(details + "\n- " + dclause + "\n", pooled, minimum), "DETAILS: the clause repeated")


def test_a_changed_pooled_file_is_caught():
    pooled, minimum = pooled_file(), minimum_jobs()
    readme, details = T.readme_text(), T.details_text()

    def cell(p, model_part, cell_id):
        (cpu,) = [c for c in p["cpus"] if model_part in c["cpu_model"]]
        (found,) = [c for c in cpu["cells"] if c["cell_id"] == cell_id]
        return found

    for what, mutate in (
            ("the lowest cell moved", lambda p: cell(p, "EPYC 9V45", "k05_stride2.L1")["as_compiled"].__setitem__("ratio", 2.95)),
            ("the highest cell moved", lambda p: cell(p, "EPYC 7763", "k04_rev.L1")["aligned"].__setitem__("ratio", 8.5)),
            ("the as-compiled top moved", lambda p: cell(p, "EPYC 7763", "k04_rev.L2")["as_compiled"].__setitem__("ratio", 7.9)),
            ("the aligned bottom moved", lambda p: cell(p, "EPYC 9V45", "k05_stride2.L1")["aligned"].__setitem__("ratio", 2.7)),
            ("an as-compiled cell above every aligned one", lambda p: cell(p, "EPYC 7763", "k04_rev.L1")["as_compiled"].__setitem__("ratio", 9.0)),
            ("an aligned cell below every as-compiled one", lambda p: cell(p, "EPYC 9V45", "k05_stride2.L1")["aligned"].__setitem__("ratio", 2.0))):
        tampered = copy.deepcopy(pooled)
        mutate(tampered)
        assertion_from(lambda: check_readme(readme, tampered, minimum), f"README: {what}")
        assertion_from(lambda: check_details(details, tampered, minimum), f"DETAILS: {what}")
    assertion_from(lambda: facts({"cpus": []}, minimum), "no CPU model with enough jobs")
