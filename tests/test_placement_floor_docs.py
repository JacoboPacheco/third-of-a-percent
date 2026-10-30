"""The sentence about the placement-floor sensitivity in README.md and readme-parts/DETAILS.md, tied to the stored file.

Both documents carry one passage of five sentences (none longer than MAX_SENTENCE_WORDS words), labelled a sensitivity and not a verdict,
that says what robustness/README-placement-floor.md found: under a minimum size for |D - 1| of 2%, four pool-and-model rows change from
MAP to INCONCLUSIVE (which rows); which pools the page shows; under each row's own layout A/A half-width no row changes; the same four
under the larger of the two minimums. Every
figure and name in it (the floor, the number of rows, their pools, CPU models and cells, the pool the page reads its verdict words from,
the pool its replication figure shows) is rebuilt here from robustness/placement-floor.json, scripts/build_site_data.py and
site/data/replication.json; nothing is hard-coded in the check and nothing is re-measured or written.

Each check comes with tamper tests: a changed word or number in the passage, and a changed copy of the stored file or of the page data,
have to be named. The whole bullet that holds the passage is also scanned for words that would claim more than a sensitivity.

Pins that repeat a figure on purpose (a second pin, kept apart from the rebuilt passage so that changing the rebuilding code and the
stored file together is still noticed): the literal phrases in test_the_stored_figures_are_the_ones_the_sentence_names, that is the
count "four pool-and-model rows", the floor "at least 2% away from 1", the pools, the two CPU models, the two page pools and the layout
result "instead no row would change".

Runs with or without pytest (scripts/check.py's built-in runner, which CI uses, has none).
"""

import copy
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_readme_numbers as T  # noqa: E402

STORED = "robustness/placement-floor.json"
NOTE = "robustness/README-placement-floor.md"
OPENING = "A sensitivity, not a verdict ("
# (document, the bullet that holds the sentence, the link target as that document writes it)
DOCS = (("README.md", "- **What MAP and INCONCLUSIVE cover.**", NOTE, T.readme_text),
        ("readme-parts/DETAILS.md", "- **The forward verdict leans on placement calls.**", "../" + NOTE, T.details_text))
MAX_SENTENCE_WORDS = 70      # the longest sentence the passage may hold (words split at spaces; a link or a `code` span counts as one)
KERNEL_WORDS = {"k03_stencil": "the stencil", "k02_add_fwd": "the forward add"}
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


def cpu_token(cpu_model):
    m = re.search(r"EPYC (\w+)", cpu_model) or re.search(r"XEON\(R\) \w+ (\w+)", cpu_model)
    assert m, f"no short name for the CPU model {cpu_model!r}"
    return m.group(1)


def cell_words(cell_id):
    kernel, size = cell_id.split(".")
    assert kernel in KERNEL_WORDS and size in ("L1", "L2"), f"the sentence has no words for the cell {cell_id}: write them and extend KERNEL_WORDS"
    return f"{KERNEL_WORDS[kernel]} at {size}"


def listing(items):
    return ", ".join(items[:-1]) + " and " + items[-1] if len(items) > 1 else items[0]


def page_pool_id(stored):
    """The id (in the stored file) of the pool the page reads: the one whose pooled file scripts/build_site_data.py names as POOLED."""
    with open(os.path.join(T.REPO, "scripts", "build_site_data.py"), encoding="utf-8") as f:
        m = re.search(r'^POOLED = "([^"]+)"', f.read(), re.M)
    assert m, "scripts/build_site_data.py no longer names the pooled file the page reads"
    ids = [p["id"] for p in stored["pools"] if p["pooled_file"] == m.group(1)]
    assert len(ids) == 1, f"{m.group(1)} is the pooled file of {len(ids)} pools in {STORED}, not one"
    return ids[0]


SITE_REPLICATION = "site/data/replication.json"
ORDINAL_WORDS = {3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}


def site_pool_id(stored, which, site=None):
    """The id (in the stored file) of the x86-64 pool that site/data/replication.json gives under pools.x86.<which> ("earlier" or "replication")."""
    site = T.J(SITE_REPLICATION) if site is None else site
    path = site["pools"]["x86"][which]["path"]
    ids = [p["id"] for p in stored["pools"] if p["pooled_file"] == path]
    assert len(ids) == 1, f"{path} (pools.x86.{which} of {SITE_REPLICATION}) is the pooled file of {len(ids)} pools in {STORED}, not one"
    return ids[0]


def floor_percent(stored):
    (rule,) = [r for r in stored["rules"] if r["id"] == "d_floor_2pct"]
    m = re.fullmatch(r"the stored rule, and also \|D - 1\| >= (\d+)%", rule["text"])
    assert m, f"the rule d_floor_2pct no longer reads as a floor in percent: {rule['text']!r}"
    return int(m.group(1))


def sentence_from(stored, link, site=None):
    """The passage as the stored file says it: what changes under the percent floor, under the larger of the two minimums and under
    the layout A/A floor, and which pools the page shows (read from site/data/replication.json unless `site` is given)."""
    changes = stored["summary"]["word_changes"]
    rows = changes["d_floor_2pct"]
    assert rows and all(r["from"] == "map" and r["to"] == "inconclusive" for r in rows), "the changed rows are no longer all MAP to INCONCLUSIVE"
    assert all(len(r["of_which_missing_the_forward_rule"]) == 1 for r in rows), "a changed row no longer hinges on exactly one cell"
    by_model = {}
    for r in rows:
        by_model.setdefault(r["cpu_model"], []).append(r)
    (amd,) = [m for m in by_model if "EPYC" in m]
    (intel,) = [m for m in by_model if "XEON" in m]
    assert len(by_model) == 2, f"the changed rows cover {len(by_model)} CPU models; the sentence names an AMD one and an Intel one"
    amd_rows, intel_rows = by_model[amd], by_model[intel]
    (intel_row,) = intel_rows
    amd_cells = {r["of_which_missing_the_forward_rule"][0] for r in amd_rows}
    assert len(amd_cells) == 1, f"the AMD rows hinge on {sorted(amd_cells)}; the sentence names one cell"
    pools = [r["pool"] for r in amd_rows]
    (replication,) = [p for p in stored["pools"] if p["id"] == intel_row["pool"]]
    assert replication["arch"] == "x86-64" and replication["what"].startswith("the x86-64 replication set"), f"{replication['id']} is not the x86-64 replication set"
    page = page_pool_id(stored)
    assert page in pools, f"the page reads {page}, which is not among the AMD rows' pools {pools}"
    assert site_pool_id(stored, "earlier", site) == page, f"{SITE_REPLICATION} no longer shows the pool the page reads ({page}) as its earlier pool"
    shown = site_pool_id(stored, "replication", site)
    assert shown == intel_row["pool"], f"the replication figure shows {shown}, not the pool {intel_row['pool']} that holds the Xeon row"
    both = [(r["pool"], r["cpu_model"], r["from"], r["to"]) for r in changes["d_floor_both"]]
    assert both == [(r["pool"], r["cpu_model"], r["from"], r["to"]) for r in rows], "the larger of the two floors no longer changes the same rows"
    layout = changes["d_floor_layout_aa"]
    n = len(rows)
    assert n in ORDINAL_WORDS and len(amd_rows) == n - 1, f"{n} rows, {len(amd_rows)} of them AMD: the passage calls the Xeon row the last of {n}"
    layout_words = "no row" if not layout else f"{NUMBER_WORDS[len(layout)]} row{'s' if len(layout) > 1 else ''}"
    pool_list = listing([f"`{p}`" for p in pools])
    return (f"{OPENING}[{NOTE}]({link})): if the exemption also required the ratio between a cell's as-compiled and aligned results to be "
            f"at least {floor_percent(stored)}% away from 1, {NUMBER_WORDS[n]} pool-and-model rows would change from MAP to INCONCLUSIVE. "
            f"The {NUMBER_WORDS[n]} are the EPYC {cpu_token(amd)} in each of the pools {pool_list}, on {cell_words(amd_cells.pop())}, "
            f"and the Xeon {cpu_token(intel)} in the x86-64 replication set `{intel_row['pool']}`, on {cell_words(intel_row['of_which_missing_the_forward_rule'][0])}. "
            f"The page's x86-64 verdict words come from `{page}`, so the EPYC {cpu_token(amd)} row of that pool is one of the {NUMBER_WORDS[n]}, "
            f"and the page's replication figure shows `{shown}`, which holds the {ORDINAL_WORDS[n]}. "
            f"With each row's own layout A/A half-width as that minimum instead {layout_words} would change. "
            f"The larger of the two minimums changes the same {NUMBER_WORDS[n]} rows; "
            f"the stored words are unchanged, and the note does not say which rule is right.")


def check_sentence(text, doc, bullet, link, stored):
    """The document holds the sentence rebuilt from the stored file, once, at the end of its bullet."""
    squashed = T.squash(text)
    expected = T.squash(sentence_from(stored, link))
    assert squashed.count(expected) == 1, (f"{doc} does not hold, exactly once, the sentence the stored file {STORED} gives (reworded, a figure changed, "
                                           f"or the stored file moved):\n  {expected}")
    assert squashed.count(OPENING) == 1, f"{doc} holds the opening {OPENING!r} {squashed.count(OPENING)} times, not once"
    bullets = [line for line in text.splitlines() if line.startswith(bullet)]
    assert len(bullets) == 1, f"{doc} has {len(bullets)} bullets that begin {bullet}, not one"
    assert T.squash(bullets[0]).endswith(expected), f"{doc}: the sentence is not at the end of the bullet that begins {bullet}"


def stored_file():
    return copy.deepcopy(T.J(STORED))


def tamper(text, old, new):
    """text with the first old at or after the sentence's opening replaced by new (words like "the Xeon 8573C in" also occur earlier)."""
    start = text.index(OPENING)
    assert old in text[start:], f"the tamper test no longer matches the sentence: {old}"
    return text[:start] + text[start:].replace(old, new, 1)


def test_readme_and_details_carry_the_sensitivity_sentence_built_from_the_stored_file():
    stored = stored_file()
    for doc, bullet, link, reader in DOCS:
        check_sentence(reader(), doc, bullet, link, stored)


def test_the_stored_figures_are_the_ones_the_sentence_names():
    stored = stored_file()
    text = T.squash(sentence_from(stored, NOTE))
    assert "four pool-and-model rows" in text and "at least 2% away from 1" in text and "`s4`, `s6` and `s7`" in text
    assert "EPYC 9V45" in text and "Xeon 8573C" in text and "`s9-x86-c`" in text and "The page's x86-64 verdict words come from `s7`" in text
    assert "the page's replication figure shows `s9-x86-c`, which holds the fourth." in text and "The larger of the two minimums changes the same four rows;" in text
    assert "from MAP to INCONCLUSIVE. The four are the EPYC 9V45 in each of the pools" in text
    assert "on the stencil at L1" in text and "on the forward add at L1. The page's" in text and "instead no row would change." in text
    assert "With each row's own layout A/A half-width as that minimum" in text
    assert T.squash(sentence_from(stored, "../" + NOTE)) != text      # the two documents differ in the link only
    assert T.squash(sentence_from(stored, "../" + NOTE)).replace("../" + NOTE, NOTE) == text


def test_the_note_the_sentence_links_to_exists_and_says_the_same_rows():
    for doc, bullet, link, reader in DOCS:
        target = os.path.normpath(os.path.join(T.REPO, os.path.dirname(doc), link))
        assert os.path.exists(target), f"{doc} links to {link}, which is not a file"
    note = T.squash(open(os.path.join(T.REPO, NOTE), encoding="utf-8").read())
    stored = stored_file()
    assert stored["summary"]["word_changes"]["d_floor_layout_aa"] == []
    for r in stored["summary"]["word_changes"]["d_floor_2pct"]:
        kind = "EPYC" if "EPYC" in r["cpu_model"] else "Xeon"
        row = f"{r['pool']} {kind} {cpu_token(r['cpu_model'])} {r['from']} to {r['to']} ({r['of_which_missing_the_forward_rule'][0]} judged and missing the forward rule)"
        assert row in note, f"the note does not name the changed row: {row}"
    assert "layout A/A half-width (largest of the designated pairs): no row changes word" in note, \
        "the note no longer says that no row changes under the layout A/A floor alone"


def test_the_sentence_claims_no_more_than_a_sensitivity():
    stored = stored_file()
    text = sentence_from(stored, NOTE).lower()
    for word in ("settled", "validated", "proves", "proved", "confirmed", "correct rule", "is right", "should"):
        assert word not in text.replace("which rule is right", ""), f"the sentence uses {word!r}"
    assert "not a verdict" in text and "does not say which rule is right" in text and "stored words are unchanged" in text


def passage_sentences(text):
    """The sentences of the passage in text: from its opening to the end of that line, split where a full stop, a space and a capital letter follow each other."""
    start = text.index(OPENING)
    end = text.find("\n", start)
    return re.split(r"(?<=\.)\s+(?=[A-Z])", T.squash(text[start:] if end < 0 else text[start:end]))


def longest_sentence_words(text):
    return max(len(s.split()) for s in passage_sentences(text))


def check_sentence_length(text, doc):
    sentences = passage_sentences(text)
    assert sentences[-1].endswith("does not say which rule is right."), f"{doc}: the passage no longer ends the way the test expects"
    assert len(sentences) > 2, f"{doc}: the passage holds {len(sentences)} sentences"
    assert longest_sentence_words(text) <= MAX_SENTENCE_WORDS, \
        f"{doc}: a sentence of the passage has {longest_sentence_words(text)} words, more than {MAX_SENTENCE_WORDS}: split it"


def test_no_sentence_of_the_passage_is_longer_than_the_limit():
    for doc, bullet, link, reader in DOCS:
        text = reader()
        check_sentence_length(text, doc)
        # the first three sentences joined into one, as they once were (a sentence of 101 words)
        joined = tamper(tamper(text, "INCONCLUSIVE. The four are the", "INCONCLUSIVE (the"), "L1. The page's", "L1; the page's")
        assertion_from(lambda: check_sentence_length(joined, doc), f"{doc}: the first three sentences joined again")


def test_a_changed_sentence_in_either_document_is_caught():
    stored = stored_file()
    for doc, bullet, link, reader in DOCS:
        text = reader()
        check_sentence(text, doc, bullet, link, stored)
        for old, new, what in (
                ("A sensitivity, not a verdict", "A finding", "the label dropped"),
                ("at least 2% away from 1", "at least 3% away from 1", "the floor changed"),
                ("four pool-and-model rows", "three pool-and-model rows", "the row count lowered"),
                ("four pool-and-model rows", "five pool-and-model rows", "the row count raised"),
                ("from MAP to INCONCLUSIVE", "from INCONCLUSIVE to MAP", "the direction reversed"),
                ("the EPYC 9V45 in each", "the EPYC 9V74 in each", "the AMD model changed"),
                ("`s4`, `s6` and `s7`", "`s4` and `s6`", "a pool dropped"),
                ("`s4`, `s6` and `s7`", "`s4`, `s6` and `s9-x86-c`", "a pool replaced"),
                ("on the stencil at L1,", "on the stencil at L2,", "the AMD cell's size changed"),
                ("on the stencil at L1,", "on the forward sum at L1,", "the AMD cell changed"),
                ("the Xeon 8573C in", "the Xeon 6973P-C in", "the Intel model changed"),
                ("replication set `s9-x86-c`", "replication set `s9-x86-ac`", "the replication pool changed"),
                ("on the forward add at L1.", "on the forward add at L2.", "the Intel cell's size changed"),
                ("The four are the EPYC 9V45", "The three are the EPYC 9V45", "the count of the rows listed changed"),
                ("The four are the EPYC 9V45 in each of the pools `s4`, `s6` and `s7`, on the stencil at L1, and the Xeon 8573C in the x86-64 "
                 "replication set `s9-x86-c`, on the forward add at L1. ", "", "the sentence that names the rows dropped"),
                ("words come from `s7`", "words come from `s6`", "the page's pool changed"),
                ("the page's replication figure shows `s9-x86-c`", "the page's replication figure shows `s9-x86-ac`", "the replication figure's pool changed"),
                ("which holds the fourth", "which holds the third", "the Xeon row's place changed"),
                ("changes the same four", "changes the same three", "the larger-floor result changed"),
                ("The larger of the two minimums changes the same four rows;", "The larger of the two minimums changes none;", "the larger-floor result reversed"),
                ("The larger of the two minimums changes the same four rows; ", "", "the larger-floor clause dropped"),
                ("The page's x86-64 verdict words come from `s7`, so the EPYC 9V45 row of that pool is one of the four, "
                 "and the page's replication figure shows `s9-x86-c`, which holds the fourth. ", "", "the sentence about the page's pools dropped"),
                ("and the page's replication figure shows `s9-x86-c`, which holds the fourth", "and the page's replication figure shows `s9-x86-c`", "the Xeon row's place dropped"),
                ("L1. The page's", "L1; the page's", "the sentence that names the rows joined to the next"),
                ("instead no row would change. The larger", "instead no row would change; the larger", "the last two sentences joined again"),
                ("With each row's own layout A/A", "With the pool's layout A/A", "the layout half-width's scope changed"),
                ("instead no row would change", "instead one row would change", "the layout result changed"),
                ("instead no row would change", "instead no row would change, and the cost is real", "a claim added"),
                ("the stored words are unchanged", "the stored words are changed", "the unchanged words reversed"),
                ("does not say which rule is right", "says which rule is right", "the open question closed"),
                ("(robustness/README-placement-floor.md)" if doc == "README.md" else "(../robustness/README-placement-floor.md)",
                 "(robustness/README-placement-floor-note.md)", "the link changed")):
            assertion_from(lambda: check_sentence(tamper(text, old, new), doc, bullet, link, stored), f"{doc}: {what}")
        sentence = T.squash(sentence_from(stored, link))
        flat = T.squash(text)
        assertion_from(lambda: check_sentence(flat.replace(sentence, ""), doc, bullet, link, stored), f"{doc}: the sentence deleted")
        assertion_from(lambda: check_sentence(text + "\n- " + sentence + "\n", doc, bullet, link, stored), f"{doc}: the sentence repeated")
        raw = sentence_from(stored, link)
        assert raw in text, f"{doc} holds the sentence with other whitespace than the rebuilt one; the move test below needs it verbatim"
        moved = text.replace(" " + raw, "", 1) + "\n\nA later paragraph. " + raw + "\n"
        assertion_from(lambda: check_sentence(moved, doc, bullet, link, stored), f"{doc}: the sentence moved out of its bullet")


def test_a_changed_stored_file_is_caught():
    for doc, bullet, link, reader in DOCS:
        text = reader()
        for what, mutate in (
                ("a changed row dropped", lambda s: s["summary"]["word_changes"]["d_floor_2pct"].pop(0)),
                ("a row added at the layout floor", lambda s: s["summary"]["word_changes"]["d_floor_layout_aa"].append(s["summary"]["word_changes"]["d_floor_2pct"][0])),
                ("a row's new word changed", lambda s: s["summary"]["word_changes"]["d_floor_2pct"][0].__setitem__("to", "map")),
                ("a row's hinge cell changed", lambda s: s["summary"]["word_changes"]["d_floor_2pct"][3].__setitem__("of_which_missing_the_forward_rule", ["k03_stencil.L2"])),
                ("the floor changed", lambda s: [r.__setitem__("text", r["text"].replace("2%", "3%")) for r in s["rules"] if r["id"] == "d_floor_2pct"]),
                ("a row under the larger of the two minimums dropped", lambda s: s["summary"]["word_changes"]["d_floor_both"].pop(0)),
                ("a row's word under the larger of the two minimums changed", lambda s: s["summary"]["word_changes"]["d_floor_both"][0].__setitem__("to", "map")),
                ("the replication pool no longer a replication set", lambda s: [p.__setitem__("what", "the 75-job x86-64 pool") for p in s["pools"] if p["id"] == "s9-x86-c"])):
            tampered = stored_file()
            mutate(tampered)
            assertion_from(lambda: check_sentence(text, doc, bullet, link, tampered), f"{doc}: {what}")


def test_the_pools_the_page_shows_are_read_from_the_site_data():
    stored = stored_file()
    assert site_pool_id(stored, "earlier") == "s7" and site_pool_id(stored, "replication") == "s9-x86-c"
    for which, path, what in (("replication", "results/s9-x86-ac-pooled/pooled.json", "the replication figure moved to another pool"),
                              ("replication", "results/s9-x86-c-pooled/other.json", "the replication figure's file belongs to no pool"),
                              ("earlier", "results/s6-pooled/pooled.json", "the earlier pool moved"),
                              ("earlier", "results/s7-pooled/other.json", "the earlier pool's file belongs to no pool")):
        site = copy.deepcopy(T.J(SITE_REPLICATION))
        site["pools"]["x86"][which]["path"] = path
        assertion_from(lambda: sentence_from(stored, NOTE, site), what)


CLAIM_WORDS = ("settled", "validated", "proves", "proved", "confirmed", "correct rule", "is right")


def bullet_overclaims(text, bullet):
    """The words of CLAIM_WORDS that the whole bullet uses (the quoted question "which rule is right" apart)."""
    (line,) = [ln for ln in text.splitlines() if ln.startswith(bullet)]
    flat = T.squash(line).lower().replace("which rule is right", "")
    return [w for w in CLAIM_WORDS if w in flat]


def test_the_whole_bullet_claims_no_more_than_a_sensitivity():
    for doc, bullet, link, reader in DOCS:
        text = reader()
        assert bullet_overclaims(text, bullet) == [], f"{doc}: the bullet that begins {bullet} claims more than a sensitivity: {bullet_overclaims(text, bullet)}"
        for word in CLAIM_WORDS:
            before = text.replace(bullet, bullet + f" This {word}.", 1)
            assert bullet_overclaims(before, bullet) == [word], f"{doc}: {word!r} added before the sentence was not named"
            after = tamper(text, "the stored words are unchanged", f"the stored words are unchanged and {word}")
            assert bullet_overclaims(after, bullet) == [word], f"{doc}: {word!r} added inside the sentence was not named"


def test_the_page_pool_is_read_from_the_site_data_builder():
    stored = stored_file()
    assert page_pool_id(stored) == "s7"
    tampered = stored_file()
    for p in tampered["pools"]:
        if p["id"] == "s7":
            p["pooled_file"] = "results/s7-pooled/other.json"
    assertion_from(lambda: page_pool_id(tampered), "the page's pooled file belongs to no pool")
