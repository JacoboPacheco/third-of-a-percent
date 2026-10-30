"""The commands the documents give a reader must work as written.

A command that needs an argument must not be printed without it, and a command that writes a file must not write into the
folders that the stored results and `scripts/check.py` read. These tests read the documents and the page's text files; they
run nothing and write nothing.

Each guard comes with a tamper test: the broken form is built in memory and the guard has to name it.

Runs with or without pytest (scripts/check.py's built-in runner, which CI uses, has none).
"""

import datetime
import glob
import os
import re
import sys
import tempfile

try:
    import pytest  # noqa: F401  (only to learn whether it is installed)
except ImportError:  # scripts/check.py falls back to its own runner when pytest is missing
    pytest = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_readme_numbers as T  # noqa: E402


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


def text_of(rel):
    with open(os.path.join(T.REPO, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def document_files():
    """The documents and the page's text files (the same set the 'pre-planned' scan reads; the records under results/ are left out)."""
    files = T.pre_planned_files()
    assert "README.md" in files and "readme-parts/DETAILS.md" in files and "arm64/README.md" in files and "site/index.html" in files, files[:6]
    return files


# ---- a reader's pool is written under build/, never into results/ --------------------------------------

POOL_OUT = re.compile(r"harness/pool\.py\s+[\"']?(?P<out>[^\s`\"'<>]+)")


def pool_outputs_under_results(name, text):
    """Where a command gives harness/pool.py an output path under results/: scripts/check.py reads every pooled.json there and re-pools it
    from its listed inputs, so a pool a reader wrote into one of those folders would replace a stored pool and the data its figures are tied to."""
    return [f"{name}: harness/pool.py {m.group('out')}" for m in POOL_OUT.finditer(text) if re.match(r"(?:\./)?results/", m.group("out"))]


def test_no_document_gives_the_pool_script_an_output_path_under_results():
    found = []
    commands = 0
    for rel in document_files():
        text = text_of(rel)
        commands += len(POOL_OUT.findall(text))
        found += pool_outputs_under_results(rel, text)
    assert commands >= 2, f"the scan saw only {commands} harness/pool.py commands with a path: the pattern no longer fits the documents"
    assert not found, f"a document tells the reader to write a pool into results/, where the stored pools are: {found}"


GLOB_NOTE = "in a shell that expands the glob (Git Bash, bash, zsh):"


def glob_note_precedes_the_pool_command(block):
    """The Arm block tells the reader which shells expand `build/arm-run-*` (PowerShell and cmd pass it on unexpanded), right before the command."""
    command = "python harness/pool.py build/arm-pooled.json build/arm-run-*"
    i, j = block.find(GLOB_NOTE), block.find(command)
    return 0 <= i < j and block[i + len(GLOB_NOTE):j].strip("\n`") == ""  # only the blank line and the code fence lie between


def test_the_arm_reproduce_block_pools_runs_into_build():
    block = text_of("arm64/README.md")
    assert glob_note_precedes_the_pool_command(block), "arm64/README.md no longer says which shells expand the build/arm-run-* glob right before the pool command"
    assert "python harness/pool.py build/arm-pooled.json build/arm-run-*" in block, "arm64/README.md no longer pools the reader's runs under build/"
    assert "-D build/arm-run-1" in block, "arm64/README.md no longer downloads the reader's runs under build/"
    assert os.path.isfile(os.path.join(T.REPO, "results", "s8-arm-pooled", "pooled.json")), "the stored Arm pool the block compares against is gone"


def test_a_pool_output_under_results_is_caught():
    old = "python harness/pool.py results/s8-arm-pooled/pooled.json results/s8-arm-run-*"
    assert pool_outputs_under_results("arm64/README.md", old), "the old Arm block is not flagged"
    assert pool_outputs_under_results("README.md", "`python harness/pool.py ./results/pooled.json build/run-*`"), "./results/ is not flagged"
    assert pool_outputs_under_results("README.md", "python harness/pool.py 'results/x.json' a"), "a quoted path is not flagged"
    assert not pool_outputs_under_results("arm64/README.md", "python harness/pool.py build/arm-pooled.json build/arm-run-*"), "the build/ form is flagged"
    assert not pool_outputs_under_results("README.md", "`python harness/pool.py <out.json> <run folders>`"), "the placeholder form is flagged"
    # the pinned lines fail when the Arm block is put back to writing into results/
    readme = T.arm64_text()
    broken = readme.replace("python harness/pool.py build/arm-pooled.json build/arm-run-*", old)
    assert broken != readme
    assert pool_outputs_under_results("arm64/README.md", broken)
    # the shell note is required, and only right before the command
    assert glob_note_precedes_the_pool_command(readme)
    assert not glob_note_precedes_the_pool_command(readme.replace(GLOB_NOTE, "Then:")), "a block without the shell note passes"
    assert not glob_note_precedes_the_pool_command(readme.replace(GLOB_NOTE, "in a shell that expands the glob (Git Bash, bash):")), "a block with a shorter shell list passes"
    moved = readme.replace(GLOB_NOTE, "Then:", 1).replace("\n## Reproduce", "\n" + GLOB_NOTE + "\n## Reproduce", 1)
    assert moved != readme and not glob_note_precedes_the_pool_command(moved), "a shell note that sits away from the command passes"
    entries = [e for e in T.guarded_sentences() if e["doc"] == "arm64/README.md" and "harness/pool.py build/arm-pooled.json" in e["sentence"]]
    assert len(entries) == 1, "the Arm block's pool command is not pinned exactly once"
    T.check_guarded_sentence(entries[0])
    original = T.GUARDED_DOCS
    T.GUARDED_DOCS = {**original, "arm64/README.md": lambda: broken}
    try:
        assertion_from(lambda: T.check_guarded_sentence(entries[0]), "the Arm block writing its pool into results/")
    finally:
        T.GUARDED_DOCS = original


# ---- what one measurement run costs, as the README states it ---------------------------------------------

RUN_DURATIONS = "tests/data/run_durations.json"

# One run of the sentence per population of stored runs: the key of each (?P<key_lo>), (?P<key_hi>), (?P<key_n>) group set -> the group name in the data file.
DURATION_GROUPS = {"s7": "s7", "s9x": "s9-x86", "s8": "s8", "s9a": "s9-arm"}
DURATION_FOLDERS = {"s6": "s6-run-*", "s7": "s7-run-*", "s8": "s8-arm-run-*", "s9-arm": "s9-arm-run-*", "s9-x86": "s9-run-*"}


def _range(key):
    return rf"(?P<{key}_lo>\d+)(?: to (?P<{key}_hi>\d+))? minutes"


def _red(key, tail="", bare=False):
    """The optional clause that gives how many of a population's runs did not end green: '<count> of the <n> ended red in the combine step, after every
    measurement job had finished'. Every population has the slot (inside its parenthesis, or after its name in a parenthesis of its own when it has none), so
    a count that is not zero must stand in the sentence and a count that is zero must not. (?P<key_at>) is the empty place where a tamper test inserts one."""
    inner = rf"(?P<{key}_red>\w+) of the (?P<{key}_red_of>\w+) ended red in the combine step, after every measurement job had finished{tail}"
    return rf"(?P<{key}_at>)(?P<{key}_clause> \({inner}\))?" if bare else rf"(?P<{key}_at>)(?P<{key}_clause>; {inner})?"


RUN_DURATION = re.compile(
    r"Of the stored runs, those that ran to the end took, from dispatch to finish and queueing included: "
    + _range("s7") + r" for the (?P<s7_n>\d+) x86-64 runs of `s7` \((?P<s7_jobs>\d+) jobs each; their `measure\.yml` still ran the whole-repository check inside every job" + _red("s7") + r"\), "
    + _range("s9x") + r" for the (?P<s9x_n>\d+) x86-64 runs of `s9` \((?P<s9x_jobs>\d+) jobs each; the workflow without the whole-repository check" + _red("s9x", ", see the set-C paragraph above") + r"\), "
    + _range("s8") + r" for the (?P<s8_n>\d+) Arm runs of `s8`" + _red("s8", bare=True) + " and " + _range("s9a") + r" for the (?P<s9a_n>\d+) Arm runs of `s9`" + _red("s9a", bare=True) + r"\. "
    r"A job is cancelled after (?P<limit>\d+) minutes \(`timeout-minutes` in `measure\.yml`; the earlier (?P<old>\d+)-minute limit cut off the (?P<runs>\w+) `s6` runs "
    r"about (?P<cut>\d+) minutes after dispatch\)\. "
    r"The durations come from the Actions run list, read on (?P<read>\d+ [A-Z][a-z]+ \d{4}) and kept in `tests/data/run_durations\.json`\.")


def _minutes(run):
    """Minutes from createdAt to updatedAt, from the two timestamps (the stored 'minutes' is checked against it, not used)."""
    t = [datetime.datetime.strptime(run[k], "%Y-%m-%dT%H:%M:%SZ") for k in ("created_at", "updated_at")]
    return (t[1] - t[0]).total_seconds() / 60


def _whole(x):
    return int(x + 0.5)


def duration_facts(data=None, workflow=None, results_dir=None):
    """What tests/data/run_durations.json holds, checked against the result folders and the workflow files: per population the run count, the
    smallest and the largest duration in whole minutes, how many of its runs did not end green, and for the s6 runs the whole minutes of each. Fails when a
    stored run has no record, a record has no folder, a stored minutes figure is not its timestamps' difference, or a population's conclusion or workflow
    note contradicts the sentence."""
    data = T.J(RUN_DURATIONS) if data is None else data
    groups = {}
    for run in data["runs"]:
        groups.setdefault(run["group"], []).append(run)
        assert abs(_minutes(run) - run["minutes"]) < 0.006, f"{run['folder']}: stored {run['minutes']} minutes, timestamps give {_minutes(run):.2f}"
        assert run["folder"].endswith("-" + str(run["run_id"])), f"{run['folder']} does not end in its run id {run['run_id']}"
    assert set(groups) == set(DURATION_FOLDERS), f"the data file holds the populations {sorted(groups)}; the folders are {sorted(DURATION_FOLDERS)}"
    for name, pattern in DURATION_FOLDERS.items():
        folders = {os.path.basename(p) for p in glob.glob(os.path.join(T.REPO, "results", pattern))}
        assert folders == {r["folder"] for r in groups[name]}, f"{name}: result folders {sorted(folders)} against recorded runs {sorted(r['folder'] for r in groups[name])}"
    assert all(r["conclusion"] == "cancelled" for r in groups["s6"]), "an s6 run did not end cancelled: the sentence says the limit cut them off"
    for name in groups:
        if name != "s6":
            assert all(r["conclusion"] in ("success", "failure") for r in groups[name]), f"{name}: a run that did not run to the end is in the sentence's list"
    not_green = {key: [r for r in groups[name] if r["conclusion"] != "success"] for key, name in DURATION_GROUPS.items()}
    facts = {key: {"n": len(groups[name]), "lo": _whole(min(map(_minutes, groups[name]))), "hi": _whole(max(map(_minutes, groups[name]))), "red": len(not_green[key])}
             for key, name in DURATION_GROUPS.items()}
    red_runs = [r for runs in not_green.values() for r in runs]
    facts["red_ids"] = sorted(str(r["run_id"]) for r in red_runs)
    # 'after every measurement job had finished': each red run holds the result files of all its jobs
    results_dir = results_dir or os.path.join(T.REPO, "results")
    facts["red_jobs_all_returned"] = all(len(glob.glob(os.path.join(results_dir, r["folder"], "results-*", "results.json"))) == T.jobs_per_run() for r in red_runs)
    facts["cut"] = {_whole(_minutes(r)) for r in groups["s6"]}
    steps = T.J("tests/data/s7_job_steps.json")["runs"]
    assert {s["run"] for s in steps} == {r["run_id"] for r in groups["s7"]}, "tests/data/s7_job_steps.json covers other runs than the s7 folders"
    facts["s7_check_in_every_job"] = all(len(s["jobs"]) == T.jobs_per_run() and all(j.get("check") for j in s["jobs"]) for s in steps)
    if workflow is None:
        with open(os.path.join(T.REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
            workflow = f.read()
    facts["measure_runs_the_check"] = any(re.search(r"scripts/check\.py", ln) for ln in workflow.splitlines() if not ln.lstrip().startswith("#"))
    _, sep, combine = workflow.partition("\n  combine:\n")
    failed_step = T.prov()["replication_combine_runs"]["failed_step"]
    facts["combine_waits_for_every_job"] = bool(sep) and combine.startswith("    needs: measure\n") and f"- name: {failed_step}\n" in combine
    d = datetime.date.fromisoformat(data["read_on"])
    facts["read"] = f"{d.day} {d.strftime('%B')} {d.year}"
    return facts


def red_said(got, key):
    """How many runs of a population the sentence says did not end green: 0 without the clause. The count must be one of the words one to fifteen and the
    'of the <n>' after it must be the population's own run count."""
    word = got.get(f"{key}_red")
    if word is None:
        return 0
    counts = {w: n for n, w in T.WORDS.items()}
    assert word in counts, f"{key}: the clause counts the red runs with {word!r}, which is not one of {sorted(counts)} (a population with none has no clause)"
    assert got[f"{key}_red_of"] == T.WORDS.get(int(got[f"{key}_n"])), f"{key}: the clause says 'of the {got[f'{key}_red_of']}' but the sentence gives {got[f'{key}_n']} runs"
    return counts[word]


def check_run_duration(text, data=None, workflow=None, results_dir=None):
    """The README's duration sentence against the dated list and the files that can be read: per population the run count and the smallest and largest
    duration, the number of runs that did not end green (stated in words where it is not zero and nowhere else), the jobs per run and the job limit of
    measure.yml, the old limit that its comment names, the number of s6 runs and their cut-off minute."""
    m = RUN_DURATION.search(T.squash(text))
    assert m, "README.md no longer holds the sentence that gives what one measurement run costs (or its wording changed): " + RUN_DURATION.pattern[:80]
    got = m.groupdict()
    facts = duration_facts(data, workflow, results_dir)
    later = T.later_runs()
    want = {"limit": str(T.job_limit_now()), "old": str(later["limit"]), "runs": T.word(later["runs"]), "cut": str(next(iter(facts["cut"]))), "read": facts["read"],
            "s7_jobs": str(T.jobs_per_run()), "s9x_jobs": str(T.jobs_per_run())}
    assert len(facts["cut"]) == 1, f"the s6 runs were cut off at different whole minutes: {sorted(facts['cut'])}"
    assert {k: got[k] for k in want} == want, f"the duration sentence disagrees with measure.yml, the s6 folders or the dated list: sentence {({k: got[k] for k in want})}, files {want}"
    for key in DURATION_GROUPS:
        said = {"n": int(got[f"{key}_n"]), "lo": int(got[f"{key}_lo"]), "hi": int(got[f"{key}_hi"] or got[f"{key}_lo"]), "red": red_said(got, key)}
        assert said == facts[key], f"{key}: the sentence says {said}, the dated list gives {facts[key]}"
    assert facts["s7_check_in_every_job"], "the s7 job records do not all show a whole-repository check step: the sentence says they ran one"
    assert not facts["measure_runs_the_check"], "measure.yml runs scripts/check.py inside a job: 'the workflow without the whole-repository check' is no longer true"
    # 'ended red in the combine step, after every measurement job had finished': the red runs are the combine-step failures that the provenance record names,
    # every one of their jobs returned its results, and the combine job of measure.yml waits for all measurement jobs and holds the step that the record says failed
    record = sorted(map(str, T.prov()["replication_combine_runs"]["red"]))
    assert facts["red_ids"] == record, f"the runs that did not end green ({facts['red_ids']}) are not the combine-step failures of the provenance record ({record})"
    assert facts["red_jobs_all_returned"], "a run that ended red does not hold the results of all its jobs: 'after every measurement job had finished' is not shown"
    assert facts["combine_waits_for_every_job"], "measure.yml's combine job no longer waits for the measurement jobs (needs: measure) or no longer holds the step that failed"
    if got["s9x_clause"]:  # 'see the set-C paragraph above': that paragraph has to come before this sentence
        before = T.squash(text)[:m.start()]
        assert "ended red on `harness/pool_check.py`" in before, "the set-C paragraph that the duration sentence points to is not above it"
    return got


def set_group(text, group, value):
    """The sentence's text with one named group of RUN_DURATION replaced (a regex substitution on the group, not a literal that a rewording would remove)."""
    s = T.squash(text)
    m = RUN_DURATION.search(s)
    assert m and m.start(group) >= 0, f"{group} is not in the duration sentence"
    return s[:m.start(group)] + value + s[m.end(group):]


def test_the_readme_duration_sentence_matches_measure_yml():
    got = check_run_duration(T.readme_text())
    assert got["limit"] == "45" and got["old"] == "22", got


def test_the_duration_sentence_is_pinned_and_says_where_the_figures_come_from():
    label = f"The durations come from the Actions run list, read on {duration_facts()['read']} and kept in `{RUN_DURATIONS}`."
    entries = [e for e in T.guarded_sentences() if e["doc"] == "README.md" and e["sentence"] == label]
    assert len(entries) == 1, "the label of the duration figures is not pinned exactly once"
    T.check_guarded_sentence(entries[0])


def test_a_wrong_duration_sentence_is_caught():
    readme = T.readme_text()
    got = check_run_duration(readme)
    changes = {"s7_lo": str(int(got["s7_lo"]) - 1), "s7_n": str(int(got["s7_n"]) + 1), "s7_jobs": str(int(got["s7_jobs"]) + 2), "s9x_lo": str(int(got["s9x_lo"]) - 1),
               "s9x_hi": str(int(got["s9x_hi"]) + 3), "s9x_n": str(int(got["s9x_n"]) - 1), "s8_lo": str(int(got["s8_lo"]) + 1), "s8_hi": str(int(got["s8_hi"]) + 10),
               "s9a_lo": "30 to 40", "s9a_n": str(int(got["s9a_n"]) + 1), "limit": "60", "old": "20", "runs": "nine", "cut": str(int(got["cut"]) + 5), "read": "28 October 2026"}
    for group, value in changes.items():
        assertion_from(lambda b=set_group(readme, group, value): check_run_duration(b), f"{group} -> {value!r}")
    # a low-to-high pair turned round
    assertion_from(lambda b=set_group(set_group(readme, "s9x_lo", got["s9x_hi"]), "s9x_hi", got["s9x_lo"]): check_run_duration(b), "the s9 range turned round")
    # the dated list itself: a run removed, a timestamp moved, a stored minutes figure changed
    data = T.J(RUN_DURATIONS)
    fewer = {**data, "runs": data["runs"][:-1]}
    assertion_from(lambda: check_run_duration(readme, fewer), "a run missing from the dated list")
    later_end = {**data, "runs": [{**r, "updated_at": "2026-12-31T00:00:00Z"} if r["group"] == "s7" else r for r in data["runs"]]}
    assertion_from(lambda: check_run_duration(readme, later_end), "the s7 end times moved")
    wrong_minutes = {**data, "runs": [{**r, "minutes": r["minutes"] + 5} if r["group"] == "s8" else r for r in data["runs"]]}
    assertion_from(lambda: check_run_duration(readme, wrong_minutes), "a stored minutes figure not matching its timestamps")
    # without the label the guarded sentence and the pattern both fail
    label = f"The durations come from the Actions run list, read on {got['read']} and kept in `{RUN_DURATIONS}`."
    unlabelled = readme.replace(" " + label, "")
    assert unlabelled != readme
    assertion_from(lambda: check_run_duration(unlabelled), "the duration sentence without its label")
    entry = next(e for e in T.guarded_sentences() if e["doc"] == "README.md" and e["sentence"] == label)
    original = T.GUARDED_DOCS
    T.GUARDED_DOCS = {**original, "README.md": lambda: unlabelled}
    try:
        assertion_from(lambda: T.check_guarded_sentence(entry), "the label of the duration figures deleted")
    finally:
        T.GUARDED_DOCS = original


RED_CLAUSE = "{count} of the {total} ended red in the combine step, after every measurement job had finished"


def test_the_duration_sentence_counts_the_runs_that_ended_red_where_there_are_some_and_nowhere_else():
    readme = T.readme_text()
    got = check_run_duration(readme)
    data = T.J(RUN_DURATIONS)
    red = [r for r in data["runs"] if r["group"] != "s6" and r["conclusion"] != "success"]  # the s6 runs were cancelled, not red
    assert [r["group"] for r in red] == ["s9-x86", "s9-x86"], "the dated list no longer holds exactly two runs that did not end green, both of the x86-64 runs of s9"
    assert (got["s9x_red"], got["s9x_red_of"]) == (T.word(len(red)), T.word(int(got["s9x_n"]))), "the s9 clause does not count the two red runs of the four"
    assert not any(got[f"{k}_clause"] for k in ("s7", "s8", "s9a")), "a population with no red run carries a clause"
    # the count word, or the total after it, changed (a number written as a digit or as 'zero' is no count word either)
    for group, value in (("s9x_red", "one"), ("s9x_red", "three"), ("s9x_red", "four"), ("s9x_red", "zero"), ("s9x_red", "2"), ("s9x_red_of", "five"), ("s9x_red_of", "three")):
        assertion_from(lambda b=set_group(readme, group, value): check_run_duration(b), f"{group} -> {value!r}")
    # the clause dropped
    dropped = set_group(readme, "s9x_clause", "")
    assert "ended red in the combine step" not in dropped
    assertion_from(lambda: check_run_duration(dropped), "the clause dropped from the population that has red runs")
    # the clause (with any count, zero included) added to a population that has no red run, in each of the three places
    for key, clause in (("s7", "; " + RED_CLAUSE), ("s8", " (" + RED_CLAUSE + ")"), ("s9a", " (" + RED_CLAUSE + ")")):
        n = T.word(int(got[f"{key}_n"]))
        for count in ("one", "zero"):
            added = set_group(readme, f"{key}_at", clause.format(count=count, total=n))
            assertion_from(lambda b=added: check_run_duration(b), f"a clause for the {key} runs, which all ended green ({count})")
    # the dated list itself: a green run turned red, the two red runs turned green, another run in the red runs' place
    first_s7 = next(r for r in data["runs"] if r["group"] == "s7")
    turned_red = {**data, "runs": [{**r, "conclusion": "failure"} if r is first_s7 else r for r in data["runs"]]}
    assertion_from(lambda: check_run_duration(readme, turned_red), "an s7 run recorded as failed while the sentence has no clause for it")
    all_green = {**data, "runs": [{**r, "conclusion": "success"} if r["group"] != "s6" else r for r in data["runs"]]}
    assertion_from(lambda: check_run_duration(readme, all_green), "the two red runs recorded as green while the sentence counts them")
    other = next(r for r in data["runs"] if r["group"] == "s9-x86" and r["conclusion"] == "success")
    swapped = {**data, "runs": [{**r, "conclusion": "success"} if r is red[0] else {**r, "conclusion": "failure"} if r is other else r for r in data["runs"]]}
    assert sum(r["conclusion"] != "success" for r in swapped["runs"] if r["group"] == "s9-x86") == 2
    e = assertion_from(lambda: check_run_duration(readme, swapped), "another run in place of a red run")
    assert "provenance record" in str(e), e
    # 'after every measurement job had finished': a red run whose folder holds fewer than all its jobs; the combine job that does not wait; the step that is not in it
    with tempfile.TemporaryDirectory() as tmp:
        for r in red:
            os.makedirs(os.path.join(tmp, r["folder"]))
            for j in range(T.jobs_per_run() - (1 if r is red[0] else 0)):
                os.makedirs(os.path.join(tmp, r["folder"], f"results-job{j}"))
                with open(os.path.join(tmp, r["folder"], f"results-job{j}", "results.json"), "w", encoding="utf-8") as f:
                    f.write("{}")
        e = assertion_from(lambda: check_run_duration(readme, results_dir=tmp), "a red run with one job missing")
        assert "all its jobs" in str(e), e
    with open(os.path.join(T.REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        workflow = f.read()
    assert "\n  combine:\n    needs: measure\n" in workflow
    for what, broken in (("the combine job without needs: measure", workflow.replace("\n  combine:\n    needs: measure\n", "\n  combine:\n", 1)),
                         ("the combine job's failed step renamed", workflow.replace("- name: " + T.prov()["replication_combine_runs"]["failed_step"], "- name: Pool", 1))):
        assert broken != workflow, what
        e = assertion_from(lambda b=broken: check_run_duration(readme, workflow=b), what)
        assert "combine job" in str(e), e
    # 'see the set-C paragraph above': the paragraph it points to must come first
    no_paragraph = readme.replace("ended red on `harness/pool_check.py`", "ended red on the checker")
    assert no_paragraph != readme
    assertion_from(lambda: check_run_duration(no_paragraph), "no paragraph about the red set-C combine jobs above the duration sentence")


# ---- the d-sweep check needs its run folders -----------------------------------------------------------

D_SWEEP_BARE = re.compile(r"dsweep/analyze\.py --verify(?!\s+results/s10-dsweep-run-)")


def bare_d_sweep_commands(name, text):
    """Where `dsweep/analyze.py --verify` is printed without the run folders: dsweep/analyze.py prints its usage and exits 2 when it gets none."""
    return [f"{name}: ...{text[max(0, m.start() - 20):m.end() + 20]!r}" for m in D_SWEEP_BARE.finditer(text)]


def test_no_document_prints_the_d_sweep_check_without_its_run_folders():
    found = []
    for rel in document_files():
        found += bare_d_sweep_commands(rel, text_of(rel))
    assert not found, f"dsweep/analyze.py --verify without results/s10-dsweep-run-* (it exits 2 and checks nothing): {found}"


def test_the_readme_gives_the_d_sweep_check_with_folders_that_exist():
    readme = T.squash(T.readme_text())
    assert "`python dsweep/analyze.py --verify results/s10-dsweep-run-*`" in readme, "README.md no longer gives the d-sweep check with its run folders"
    assert len(glob.glob(os.path.join(T.REPO, "results", "s10-dsweep-run-*"))) >= 3, "the glob in the README matches fewer than the 3 stored d-sweep runs"


def test_a_bare_d_sweep_command_is_caught():
    old = "`python replication/compare.py --verify`, `python dsweep/analyze.py --verify`, `python forwardt/analyze.py --verify`."
    new = "`python dsweep/analyze.py --verify results/s10-dsweep-run-*` (this one needs the run folders as arguments)"
    assert bare_d_sweep_commands("README.md", old), "the bare form is not flagged"
    assert not bare_d_sweep_commands("README.md", new), "the form with the run folders is flagged"
    assert bare_d_sweep_commands("README.md", "python dsweep/analyze.py --verify\n"), "a bare command at the end of a line is not flagged"
    assert bare_d_sweep_commands("README.md", "python dsweep/analyze.py --verify results/s9-run-1"), "the wrong folders are not flagged"
    # the pinned sentence fails when it is cut back to the bare form
    entry = next(e for e in T.guarded_sentences() if "dsweep/analyze.py --verify results/s10" in e["sentence"])
    T.check_guarded_sentence(entry)
    broken = T.readme_text().replace(" results/s10-dsweep-run-*` (this one needs the run folders as arguments)", "`")
    assert broken != T.readme_text()
    original = T.GUARDED_DOCS
    T.GUARDED_DOCS = {**original, "README.md": lambda: broken}
    try:
        assertion_from(lambda: T.check_guarded_sentence(entry), "the bare form of the pinned sentence")
    finally:
        T.GUARDED_DOCS = original
