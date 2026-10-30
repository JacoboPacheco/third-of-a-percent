"""The README sentence that says where the forwardt runs were dispatched from.

The folder map of the README says, for the Arm and d-sweep runs, that they name a commit that only a temporary public branch holds. The
forwardt runs are different: they were dispatched from the public branch `forwardt-run`, but at a commit the default branch holds, so the
branch is not needed to recover their code. The sentence is rebuilt from three stored things and has to match the README:

- the manifest forwardt/runs.json: the branch, the number of runs, how many were measurement runs and how many code tests, and the one
  commit every run was dispatched from (head_sha);
- the result files under results/s11-forwardt-run-*, whose records name that same commit (and no other);
- tests/data/run_links_and_commits.json, the stored reading of the GitHub API: the commit is in the repository, and the default branch's
  head was that commit when it was read.

Nothing is written. Tamper tests: a changed word or number in the sentence, a removed, doubled or moved sentence, and changed copies of the
manifest and of the stored reading have to be named. Runs with or without pytest (scripts/check.py's built-in runner has none).
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_readme_numbers as T  # noqa: E402

BULLET_START = "**Commits and run links in the records.**"
NEXT_SENTENCE = "The run links inside the records work for"
GROUP = "s11-forwardt-run"


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


_NAMED = []


def stored():
    """(manifest, commits the s11 result records name, the stored reading of those commits), private copies."""
    manifest = copy.deepcopy(T.J("forwardt/runs.json"))
    if not _NAMED:  # reading every record of results/ takes a while: once per run
        _NAMED.append(frozenset(T.result_groups()[GROUP]["commits"]))
    named = set(_NAMED[0])
    reading = copy.deepcopy(T.J(T.RUN_LINKS)["commits"][GROUP])
    return manifest, named, reading


def facts(manifest, named, reading):
    shas = {e["head_sha"] for e in manifest["entries"]}
    assert len(shas) == 1, f"the manifest names {len(shas)} commits for its runs; the sentence says they were dispatched from one"
    short = next(iter(shas))[:7]
    assert named == {short}, f"the result records name {sorted(named)}, the manifest {short}"
    assert [c["commit"] for c in reading] == [short], "the stored reading of the GitHub API lists other commits than the manifest"
    assert all(c["in_repository"] for c in reading), "the commit is not recorded as being in the repository: the sentence says the default branch holds it"
    classes = [e["class"] for e in manifest["entries"]]
    assert set(classes) == {"test", "measurement"}, f"the manifest has run classes {sorted(set(classes))}"
    return {"branch": manifest["branch"], "n": len(classes), "meas": classes.count("measurement"), "tests": classes.count("test"), "commit": short}


def sentence(f):
    return (f"The forwardt runs (the {T.word(f['n'])} of `forwardt/runs.json`: {T.word(f['meas'])} measurement runs, stored, and {T.word(f['tests'])} "
            f"code tests, not stored) were dispatched from the public branch `{f['branch']}` at commit {f['commit']}, which the default branch holds, "
            f"so that branch is not needed to recover their code.")


def check(text, manifest, named, reading):
    f = facts(manifest, named, reading)
    flat = T.squash(text)
    want = T.squash(sentence(f))
    assert flat.count(want) == 1, f"the README does not hold, once, the sentence the manifest gives:\n  {want}"
    start, end = flat.index(T.squash(BULLET_START)), flat.index(T.squash(NEXT_SENTENCE))
    assert start < flat.index(want) < end, f"the sentence is not in the folder-map bullet {BULLET_START!r}, before {NEXT_SENTENCE!r}"
    # the sentences for the other two temporary branches stay in front of it
    assert flat.index(T.squash("that branch is kept because the records name its commit.")) < flat.index(want), \
        "the forwardt sentence comes before the one about the Arm runs' branch"


def test_the_manifest_and_the_records_give_one_commit_on_the_branch():
    manifest, named, reading = stored()
    f = facts(manifest, named, reading)
    assert f == {"branch": "forwardt-run", "n": 5, "meas": 3, "tests": 2, "commit": "595e061"}, f
    assert [c["vs_main"] for c in reading] == ["identical"], "the stored reading no longer says the default branch's head was that commit"


def test_the_readme_says_where_the_forwardt_runs_were_dispatched_from():
    manifest, named, reading = stored()
    check(T.readme_text(), manifest, named, reading)


def test_a_changed_word_or_number_is_caught():
    manifest, named, reading = stored()
    text = T.readme_text()
    base = sentence(facts(manifest, named, reading))
    assert text.count(base) == 1
    swaps = [("the five of", "the four of"), ("three measurement", "two measurement"), ("two code tests", "three code tests"),
             ("measurement runs, stored", "measurement runs"), ("code tests, not stored", "code tests, stored"),
             ("public branch `forwardt-run`", "public branch `forwardt-sweep`"), ("at commit 595e061", "at commit 595e062"),
             ("which the default branch holds", "which no branch holds"), ("not needed to recover", "needed to recover"),
             ("`forwardt/runs.json`", "`forwardt/results.json`")]
    for old, new in swaps:
        assert base.count(old) == 1, f"{old!r} is not in the sentence once"
        assertion_from(lambda old=old, new=new: check(text.replace(base, base.replace(old, new)), manifest, named, reading), f"{old!r} -> {new!r}")


def test_a_missing_doubled_or_moved_sentence_is_caught():
    manifest, named, reading = stored()
    text = T.readme_text()
    base = sentence(facts(manifest, named, reading))
    assert text.count(base) == 1
    assertion_from(lambda: check(text.replace(base, ""), manifest, named, reading), "the sentence removed")
    assertion_from(lambda: check(text.replace(base, base + " " + base), manifest, named, reading), "the sentence twice")
    moved = text.replace(" " + base, "", 1) + "\n\n" + base + "\n"
    assertion_from(lambda: check(moved, manifest, named, reading), "the sentence moved to the end of the README")


def test_changed_manifest_or_stored_reading_is_caught():
    manifest, named, reading = stored()
    text = T.readme_text()
    check(text, manifest, named, reading)

    def changed(fn, what, which="manifest"):
        m, n, r = copy.deepcopy(manifest), set(named), copy.deepcopy(reading)
        fn(m if which == "manifest" else r)
        assertion_from(lambda: check(text, m, n, r), what)

    changed(lambda m: m.update(branch="forwardt-sweep"), "another branch name in the manifest")
    changed(lambda m: m["entries"][0].update(**{"class": "measurement"}), "a code test turned into a measurement run")
    changed(lambda m: m["entries"][3].update(**{"class": "test"}), "a measurement run turned into a code test")
    changed(lambda m: m["entries"].append(copy.deepcopy(m["entries"][0])), "a sixth run in the manifest")
    changed(lambda m: m["entries"][4].update(head_sha="0" * 40), "one run dispatched from another commit")
    changed(lambda r: r[0].update(in_repository=False), "the commit recorded as not in the repository", which="reading")
    changed(lambda r: r[0].update(commit="1234567"), "another commit in the stored reading", which="reading")
    assertion_from(lambda: check(text, manifest, {"595e061", "1234567"}, reading), "a result record naming a second commit")
    assertion_from(lambda: check(text, manifest, set(), reading), "result records naming no commit")
