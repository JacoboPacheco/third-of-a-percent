"""forwardt/analyze.py (the rules 1 to 13 of forwardt/PLAN.md, the predictions P0 to P6 and P2n, the outcome letters A to K,
the manifest of forwardt/runs.json and its stops, the second printing, results.json and --verify).

Generated data only: no network, no compiler, no timing. The files are made by the faked sweep of tests/test_forwardt.py
(real sweep code, made-up builds and samples) and then given the words, ratios and noise each test needs. Plain functions:
scripts/check.py's built-in runner runs them without pytest."""
import contextlib
import copy
import importlib.util
import io
import json
import math
import os
import random
import re
import statistics
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def _load(key, rel):
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


sw = _load("forwardt_sweep", os.path.join("forwardt", "sweep.py"))
tf = _load("forwardt_tests_helpers", os.path.join("tests", "test_forwardt.py"))
an = _load("forwardt_analyze", os.path.join("forwardt", "analyze.py"))
import pool  # noqa: E402
import stats  # noqa: E402

LOOPS = sw.LOOPS
SIZES = sw.SIZES
INF = float("inf")
X86 = "AMD EPYC 7763 64-Core Processor"
X86B = "AMD EPYC 9V74 80-Core Processor"
N2 = "Neoverse-N2"
V3 = "Neoverse-V3"
X86_WORDS = ("kept", "lost", "kept", "narrower", "lost", "lost")
N2_WORDS = ("kept", "lost", "kept", "kept", "kept", "kept")
SC = {"kept": {"none": (True, 4, 2), "fast": (True, 4, 2)},
      "lost": {"none": (True, 4, 2), "fast": (False, None, None)},
      "narrower": {"none": (True, 4, 2), "fast": (True, 4, 1)},
      "scalar": {"none": (False, None, None), "fast": (False, None, None)}}
BASE = {"t01_sum_size": 1.0, "t02_sum_n": 1.10, "t03_scale_size": 1.0, "t04_scale_n": 1.10, "t05_fill_n": 2.0,
        "t06_offset": 2.0}
BASE_N2 = {"t01_sum_size": 1.0, "t02_sum_n": 1.2, "t03_scale_size": 1.0, "t04_scale_n": 1.0, "t05_fill_n": 1.05,
           "t06_offset": 1.05}
_ORIG_BOOT = stats.bootstrap_ratio_ci


def _boot_n(n):
    def f(a, b, resamples=None, seed=stats.SEED, level=stats.LEVEL):
        return _ORIG_BOOT(a, b, resamples=n, seed=seed, level=level)
    return f


# ---------------------------------------------------------------- made-up files, runs and manifests

_BASE_DOCS = {}


def base_doc(words, arm, smoke=False):
    """A forwardt.json written by the faked sweep (real validate_doc passes) with the loops given these words."""
    key = (tuple(words), arm, smoke)
    if key not in _BASE_DOCS:
        scen = {loop: SC[w] for loop, w in zip(LOOPS, words)}
        with tempfile.TemporaryDirectory() as tmp:
            with tf.patched((stats, "bootstrap_ratio_ci", _boot_n(20))):
                code, text, _c, _i, out, _b = tf.run_job(tmp, extra=(["--reps", "4"] if smoke else []), crit_reps=40,
                                                           scen=scen, machine=tf.ARM if arm else tf.EPYC)
            assert code == 0, text
            _BASE_DOCS[key] = tf.load_json(os.path.join(out, sw.RESULT_NAME))
    return copy.deepcopy(_BASE_DOCS[key])


def lookup(spec, loop, size, col, default):
    if not isinstance(spec, dict):
        return default if spec is None else spec
    for k in ((loop, size, col), (loop, size), loop, "default"):
        if k in spec:
            return spec[k]
    return default


def make_doc(words=X86_WORDS, arm=False, cpu=X86, arch=None, run_id="39000000001", job="1", over=None, noise=0.002,
             boot=20, fast_traps=None, smoke=False, seed=0):
    """One job's forwardt.json: the faked sweep's file with the run, the CPU model, the ratios `over` (a dict: loop, or
    (loop, size), or (loop, size, column) -> the FAST/NONE ratio the samples are made to have) and `noise` (a number or a
    dict with the same keys) put in."""
    doc = base_doc(words, arm, smoke)
    doc["run"]["id"], doc["run"]["job"] = run_id, str(job)
    doc["run"]["runner"]["cpu_model"] = cpu
    doc["run"]["runner"]["arch"] = arch or ("aarch64" if arm else "x86_64")
    if fast_traps:
        for loop, nt in fast_traps.items():
            for m in ("fast", "fast_a64"):
                doc["loops"][loop]["builds"][m]["traps"] = nt
    if smoke:
        return doc
    rng = random.Random("%s|%s|%s" % (run_id, job, seed))
    over = over or {}
    table = BASE_N2 if arm else BASE
    for loop in LOOPS:
        for size in SIZES:
            cell = doc["loops"][loop]["cells"][size]
            for col, pr in cell["pairs"].items():
                if pr is None:
                    continue
                r = 1.0 if col == "aa" else lookup(over, loop, size, col, table[loop])
                nz = lookup(noise, loop, size, col, 0.002)
                reps = len(pr["a_ns"])
                base = 1000.0 * cell["n"]
                a = [base * (1 + rng.uniform(-nz, nz)) for _ in range(reps)]
                b = [base * r * (1 + rng.uniform(-nz, nz)) for _ in range(reps)]
                lo, hi = _ORIG_BOOT(a, b, resamples=boot)
                pr.update(a_ns=a, b_ns=b, ratio=stats.ratio_of_medians(a, b), ci95=[lo, hi],
                          half_width_pct=stats.half_width_pct((lo, hi)))
    return doc


_COUNTER = [0]


def next_rid():
    _COUNTER[0] += 1
    return "39%09d" % _COUNTER[0]


def write_run(tmp, docs, name=None, clause="x86-64 run 1", cls="measurement", reason=None, started=None, returned=None,
              runner="ubuntu-24.04", **kw):
    """Stores the docs under tmp/results/<name>/job-<i>/forwardt.json and returns the manifest entry of the run."""
    run_id = str(docs[0]["run"]["id"])
    folder = "results/" + (name or ("run-" + run_id))
    for i, d in enumerate(docs):
        p = os.path.join(tmp, folder, "job-%d" % i)
        os.makedirs(p, exist_ok=True)
        with open(os.path.join(p, sw.RESULT_NAME), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
    c = _COUNTER[0]
    e = {"run_id": run_id, "runner": runner, "head_sha": "a" * 40,
         "created_at": "2026-10-22T%02d:%02d:00Z" % (10 + c // 60 % 12, c % 60), "class": cls, "clause": clause,
         "jobs_started": len(docs) if started is None else started,
         "jobs_returned": len(docs) if returned is None else returned, "not_returned": [], "folder": folder}
    if reason:
        e["reason"] = reason
    e.update(kw)
    gone = e["jobs_started"] - e["jobs_returned"]
    if gone > 0 and not e["not_returned"]:
        e["not_returned"] = [{"job": str(100 + i), "reason": "cancelled at the time limit"} for i in range(gone)]
    return e


def model_entry(tmp, words=X86_WORDS, arm=False, cpu=X86, n=3, over=None, noise=0.002, mutate=None, fast_traps=None,
                smoke=False, arch=None, **entry_kw):
    rid = next_rid()
    docs = []
    for i in range(n):
        d = make_doc(words, arm, cpu, arch=arch, run_id=rid, job=str(i + 1), over=over, noise=noise,
                     fast_traps=fast_traps, smoke=smoke)
        if mutate:
            mutate(i, d)
        docs.append(d)
    entry_kw.setdefault("clause", "Neoverse-N2 run" if arm else "x86-64 run 1")
    entry_kw.setdefault("runner", "ubuntu-24.04-arm" if (arm or arch == "aarch64") else "ubuntu-24.04")
    return write_run(tmp, docs, **entry_kw)


META = {"repository": "owner/name", "branch": "forwardt-run", "workflow_file": ".github/workflows/forwardt-run.yml",
        "time_limit_minutes": 45, "query": "gh run list -R owner/name --branch forwardt-run --limit 200",
        "test_ratios_read": False}


def manifest_of(entries, **meta):
    """A manifest of these entries; with entries it carries the top-level description the report needs (META)."""
    m = {"schema": 1, "entries": list(entries)}
    if m["entries"]:
        m.update(META)
    m.update(meta)
    return m


def run_world(tmp, entries, resamples=200, **kw):
    return an.analyse(manifest_of(entries), tmp, resamples, **kw)


def model(res, cpu, key="analysis"):
    for m in res[key]["models"]:
        if m["cpu_model"] == cpu:
            return m
    raise AssertionError("no model %r in %s" % (cpu, [m["cpu_model"] for m in res[key]["models"]]))


_DEFAULT = {}


def default_result():
    """The analysis of one EPYC 7763 model, three jobs, every word and ratio as the plan predicts."""
    if "r" not in _DEFAULT:
        with tempfile.TemporaryDirectory() as tmp:
            _DEFAULT["r"] = run_world(tmp, [model_entry(tmp)])
    return copy.deepcopy(_DEFAULT["r"])


def stop_text(entries, tmp):
    try:
        run_world(tmp, entries)
    except an.ManifestError as exc:
        return " | ".join(exc.problems)
    raise AssertionError("the analysis did not stop")


# ---------------------------------------------------------------- the plan, the empty manifest, results.json

def test_the_first_commit_hash_constant_is_the_hash_of_the_plan_as_it_stands():
    assert an.FIRST_COMMIT_PLAN_SHA256 == sw.plan_sha256()
    assert len(an.FIRST_COMMIT_PLAN_SHA256) == 64


def test_the_comment_above_the_first_commit_hash_names_the_commit_a_reader_of_the_public_repository_can_see():
    with open(os.path.join(REPO, "forwardt", "analyze.py"), encoding="utf-8") as f:
        src = f.read()
    at = src.index("FIRST_COMMIT_PLAN_SHA256 = ")
    comment = src[src.rindex("RESULTS_FILE = ", 0, at):at]      # the comment lines directly above the constant
    assert "the commit that first holds forwardt/PLAN.md (3ea4001 in the public repository)" in " ".join(comment.split())
    assert comment.count("#") == 3 and "7a8098f" not in src


def test_an_empty_manifest_says_no_run_exists_and_every_prediction_is_not_testable():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [])
    assert res["no_run"] is True and res["analysis"]["models"] == []
    for target, s in res["analysis"]["summaries"].items():
        assert all(p["state"] == "not testable" for p in s["P0"].values()), target
        assert all(p["state"] == "not testable" for p in s["preds"].values()), target
    assert res["analysis"]["outcome"]["letter"] == "J"
    assert res["analysis_without_not_in_plan"] == {"same_as_analysis": True}
    assert "no run exists" in an.render_report(res)


def test_the_stored_manifest_is_valid():
    # the committed forwardt/runs.json: empty before the first dispatch and well formed after every later one (this test
    # must not break at the first recorded run, so it does not ask for the empty manifest)
    with open(an.MANIFEST_FILE, encoding="utf-8") as f:
        m = json.load(f)
    assert an.validate_manifest(m) == []


def test_main_writes_a_deterministic_results_file_and_prints_the_report():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "results.json")
        man = os.path.join(tmp, "runs.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "entries": []}, f)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert an.main(["--manifest", man, "--base", tmp, "--out", out]) == 0
        assert "no run exists" in buf.getvalue()
        with open(out, "rb") as f:
            first = f.read()
        with contextlib.redirect_stdout(io.StringIO()):
            an.main(["--manifest", man, "--base", tmp, "--out", out])
        with open(out, "rb") as f:
            assert f.read() == first
        text = first.decode("utf-8")
        assert text.endswith("\n") and "NaN" not in text and "Infinity" not in text and "\r" not in text
        doc = json.loads(text)
        assert doc["kind"] == "forwardt-results" and doc["plan_sha256"] == sw.plan_sha256()
        assert doc["first_commit_plan_sha256"] == an.FIRST_COMMIT_PLAN_SHA256
        assert doc["criteria_sha256"] == sw.criteria_sha256() and set(doc["code_sha256"]) == set(sw.CODE_FILES)
        keys = list(json.loads(text, object_pairs_hook=lambda p: [k for k, _ in p]))
        assert keys == sorted(keys)
        out2 = os.path.join(tmp, "none.json")
        with contextlib.redirect_stdout(io.StringIO()):
            assert an.main(["--manifest", man, "--base", tmp, "--out", out2, "--no-write"]) == 0
        assert not os.path.exists(out2)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert an.main(["--manifest", man, "--base", tmp, "--out", out, "--verify"]) == 0
            assert an.main(["--manifest", man, "--base", tmp, "--out", out, "--bogus-flag"]) == 2
        assert "matches the recomputation" in buf.getvalue()


# ---------------------------------------------------------------- the manifest and its stops

def _entry(tmp):
    return model_entry(tmp)


def test_manifest_clauses_each_have_a_testable_consequence():
    with tempfile.TemporaryDirectory() as tmp:
        good = _entry(tmp)
        assert an.validate_manifest(manifest_of([good])) == []

        def bad(**kw):
            e = dict(copy.deepcopy(good), **kw)
            return an.validate_manifest(manifest_of([e]))

        assert any("digits" in p for p in bad(run_id="local-12"))
        assert any("head_sha" in p for p in bad(head_sha="abc"))
        assert any("created_at" in p for p in bad(created_at="yesterday"))
        assert any("class" in p for p in bad(**{"class": "other"}))
        assert any("clause" in p for p in bad(clause="a fifth run"))
        assert any("no reason" in p for p in bad(clause="not in the plan"))
        assert bad(clause="not in the plan", reason="a rerun after a typo") == []
        assert any("not_returned" in p for p in bad(jobs_started=4))
        assert bad(jobs_started=4, not_returned=[{"job": "9", "reason": "cancelled"}]) == []
        assert any("returned" in p for p in bad(jobs_returned=5))
        assert any("folder" in p for p in bad(folder=None))
        assert bad(folder=None, jobs_returned=0, jobs_started=0) == []
        assert any("unknown key" in p for p in bad(color="red"))
        dup = manifest_of([good, copy.deepcopy(good)])
        assert any("twice" in p for p in an.validate_manifest(dup))
        assert any("schema" in p for p in an.validate_manifest({"schema": 2, "entries": []}))
        assert any("not a list" in p for p in an.validate_manifest({"schema": 1, "entries": {}}))
        try:
            run_world(tmp, [dict(good, head_sha="x")])
        except an.ManifestError as exc:
            assert exc.problems
        else:
            raise AssertionError("a malformed manifest must stop the analysis")


def test_entries_out_of_creation_order_are_a_note_and_not_a_stop():
    with tempfile.TemporaryDirectory() as tmp:
        e1, e2 = _entry(tmp), model_entry(tmp, cpu=X86B)
        e1["created_at"], e2["created_at"] = "2026-10-22T12:00:00Z", "2026-10-22T11:00:00Z"
        res = run_world(tmp, [e1, e2])
        assert any("not in order" in n for n in res["manifest_notes"])
        assert len(res["analysis"]["models"]) == 2


def test_the_report_names_the_branch_the_workflow_the_limit_the_query_and_whether_a_test_ratio_was_read():
    with tempfile.TemporaryDirectory() as tmp:
        e = _entry(tmp)
        e["note"] = "restarted by hand after the runner lost power"
        meta = dict(META, branch="forwardt-temp-7", workflow_file=".github/workflows/ft-7.yml", time_limit_minutes=47.5,
                    query="gh run list -R me/repo --branch forwardt-temp-7 --limit 200", note="dispatched twice")
        res = an.analyse(manifest_of([e], **meta), tmp, 200)
        d = res["run_description"]
        assert d == dict(meta) and set(d) == set(an.TOP_OPTIONAL)
        text = an.render_report(res)
        for s in ("forwardt-temp-7", ".github/workflows/ft-7.yml", "47.5 minutes", meta["query"], "owner/name", "dispatched twice",
                  "no ratio of a test run was read", "restarted by hand after the runner lost power"):
            assert s in text, s
        # the branch is named by the dispatch line itself, not only inside the query that happens to carry its name
        assert ("dispatches: repository owner/name; temporary branch forwardt-temp-7; workflow file .github/workflows/ft-7.yml; "
                "workflow time limit 47.5 minutes") in text
        assert "a ratio of a test run was read" not in text.replace("no ratio of a test run was read", "")
        res = an.analyse(manifest_of([e], test_ratios_read=True), tmp, 200)
        text = an.render_report(res)
        assert "a ratio of a test run was read" in text and "no ratio of a test run was read" not in text
        assert an.analyse(manifest_of([e]), tmp, 200)["run_description"]["note"] is None
        # the lines stand beside the entries, before the analysis
        assert text.index("temporary branch") < text.index("[run] ") < text.index("== all measurement runs ==")


def test_with_entries_the_branch_workflow_limit_query_and_test_ratio_statement_are_required_top_level_keys():
    with tempfile.TemporaryDirectory() as tmp:
        e = _entry(tmp)
        assert an.validate_manifest(manifest_of([e])) == []
        for key in ("branch", "workflow_file", "time_limit_minutes", "query", "test_ratios_read"):
            m = manifest_of([e])
            del m[key]
            probs = an.validate_manifest(m)
            assert len(probs) == 1 and key in probs[0] and "lacks the top-level key" in probs[0], (key, probs)
            try:
                an.analyse(m, tmp, 200)
            except an.ManifestError as exc:
                assert exc.problems == probs
            else:
                raise AssertionError("a manifest without %s must stop" % key)
        # the repository and the note stay optional; the empty manifest needs none of the keys
        m = manifest_of([e])
        del m["repository"]
        assert an.validate_manifest(m) == []
        assert an.validate_manifest({"schema": 1, "entries": []}) == []
        assert an.run_description({"schema": 1, "entries": []}) == {k: None for k in an.TOP_OPTIONAL}
        # types
        assert any("time_limit_minutes" in p for p in an.validate_manifest(manifest_of([e], time_limit_minutes=0)))
        assert any("time_limit_minutes" in p for p in an.validate_manifest(manifest_of([e], time_limit_minutes="45")))
        assert any("time_limit_minutes" in p for p in an.validate_manifest(manifest_of([e], time_limit_minutes=True)))
        assert any("time_limit_minutes" in p for p in an.validate_manifest(manifest_of([e], time_limit_minutes=INF)))
        assert any("test_ratios_read" in p for p in an.validate_manifest(manifest_of([e], test_ratios_read="no")))
        assert any("test_ratios_read" in p for p in an.validate_manifest(manifest_of([e], test_ratios_read=0)))
        assert any("branch" in p for p in an.validate_manifest(manifest_of([e], branch="  ")))
        assert any("query" in p for p in an.validate_manifest(manifest_of([e], query=5)))
        assert any("unknown top-level" in p for p in an.validate_manifest(manifest_of([e], flavour="x")))


def test_an_entry_can_carry_its_own_time_limit_and_the_run_line_prints_the_one_that_applies():
    with tempfile.TemporaryDirectory() as tmp:
        plain = model_entry(tmp)                                                 # no limit of its own
        longer = model_entry(tmp, cpu=X86B, time_limit_minutes=50)               # differs from the top-level 45
        same = model_entry(tmp, clause="x86-64 run 2", time_limit_minutes=45)    # equal to it
        res = run_world(tmp, [plain, longer, same])
        lines = _run_lines(an.render_report(res))
        frac = an.analyse(manifest_of([dict(longer, time_limit_minutes=47.5)], time_limit_minutes=47.5), tmp, 200)
        frac_lines = _run_lines(an.render_report(frac))
        short = an.analyse(manifest_of([dict(longer, time_limit_minutes=30)], time_limit_minutes=47.5), tmp, 200)
        short_lines = _run_lines(an.render_report(short))
    assert len(lines) == 3
    assert "; time limit 45 minutes; jobs 3/3" in lines[0] and "this entry" not in lines[0]
    assert "; time limit this entry: 50 minutes (top-level: 45); jobs 3/3" in lines[1]
    assert "; time limit 45 minutes; jobs 3/3" in lines[2] and "this entry" not in lines[2]
    assert "; time limit 47.5 minutes; jobs" in frac_lines[0] and "this entry" not in frac_lines[0]
    assert "; time limit this entry: 30 minutes (top-level: 47.5); jobs" in short_lines[0]
    # the stored manifest keeps the key as written and only where it was written; the top-level line is unchanged
    assert res["manifest"][1]["time_limit_minutes"] == 50 and "time_limit_minutes" not in res["manifest"][0]
    assert "workflow time limit 45 minutes" in an.render_report(res)


def test_an_entry_time_limit_is_validated_like_the_top_level_one():
    with tempfile.TemporaryDirectory() as tmp:
        good = _entry(tmp)
        assert an.validate_manifest(manifest_of([good])) == []                    # absent is fine
        assert an.validate_manifest(manifest_of([dict(good, time_limit_minutes=50)])) == []
        assert an.validate_manifest(manifest_of([dict(good, time_limit_minutes=47.5)])) == []
        for bad in (0, -5, "50", True, False, None, INF, float("nan"), [50]):
            probs = an.validate_manifest(manifest_of([dict(good, time_limit_minutes=bad)]))
            assert len(probs) == 1 and "entries[0].time_limit_minutes is not a positive number" in probs[0], (bad, probs)
        assert an.validate_manifest({"schema": 1, "entries": []}) == []           # the empty manifest still needs nothing
        try:
            run_world(tmp, [dict(good, time_limit_minutes=0)])
        except an.ManifestError as exc:
            assert any("time_limit_minutes" in p for p in exc.problems)
        else:
            raise AssertionError("an invalid entry time limit must stop the analysis")


def _edit_file(tmp, entry, i, fn):
    """Rewrites job i of an entry through fn(doc) and returns the path the analysis names for it."""
    path = os.path.join(tmp, entry["folder"], "job-%d" % i, sw.RESULT_NAME)
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    fn(d)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return entry["folder"] + "/job-%d/" % i + sw.RESULT_NAME


def test_a_file_whose_commit_is_not_the_entrys_head_sha_stops_and_names_the_file_and_both_values():
    for idx in (0, 1, 2):                                      # the first, the middle and the last file of a three-job run
        with tempfile.TemporaryDirectory() as tmp:
            e = model_entry(tmp)
            rel = _edit_file(tmp, e, idx, lambda d: d["run"].update(commit="b" * 40))
            text = stop_text([e], tmp)
        assert " | " not in text, (idx, text)                  # one stop, for that file only
        assert text.startswith(rel + ": ") and "bbbbbbbbbb" in text and "aaaaaaaaaa" in text and "b" * 11 not in text, (idx, text)
        assert "its run.commit is bbbbbbbbbb but the manifest gives head_sha aaaaaaaaaa for run " + e["run_id"] in text


def test_a_manifest_head_sha_that_is_wrong_for_the_whole_entry_names_every_file():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        text = stop_text([dict(e, head_sha="c" * 40)], tmp)
    assert text.count(" | ") == 2 and text.count("head_sha cccccccccc") == 3
    for i in range(3):
        assert e["folder"] + "/job-%d/" % i + sw.RESULT_NAME in text
    assert text.count("its run.commit is aaaaaaaaaa") == 3


def test_a_commit_that_differs_from_the_head_sha_only_late_in_the_hash_stops():
    """The whole 40 characters are compared: a shortened comparison (the first 7 or 10, or all but the last) must not pass."""
    for label, commit in (("last character", "a" * 39 + "b"), ("character 12", "a" * 11 + "b" + "a" * 28),
                          ("character 8", "a" * 7 + "b" + "a" * 32), ("character 39", "a" * 38 + "b" + "a")):
        with tempfile.TemporaryDirectory() as tmp:
            e = model_entry(tmp)
            rel = _edit_file(tmp, e, 1, lambda d: d["run"].update(commit=commit))
            text = stop_text([e], tmp)
        assert " | " not in text and text.startswith(rel + ": its run.commit is "), (label, text)
        assert "but the manifest gives head_sha aaaaaaaaaa" in text, (label, text)


def test_a_missing_or_malformed_commit_in_a_file_stops_too():
    for label, fn in (("none", lambda d: d["run"].update(commit=None)), ("missing", lambda d: d["run"].pop("commit")),
                      ("number", lambda d: d["run"].update(commit=12345)), ("empty", lambda d: d["run"].update(commit="")),
                      ("short", lambda d: d["run"].update(commit="aaaa"))):
        with tempfile.TemporaryDirectory() as tmp:
            e = model_entry(tmp)
            rel = _edit_file(tmp, e, 1, fn)
            text = stop_text([e], tmp)
        assert " | " not in text and text.startswith(rel + ": its run.commit is "), (label, text)
        assert "but the manifest gives head_sha aaaaaaaaaa" in text, (label, text)


def test_the_commit_comparison_ignores_case_and_the_run_line_says_which_commit_the_files_name():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        for i in range(3):
            _edit_file(tmp, e, i, lambda d: d["run"].update(commit="A" * 40))      # upper case in every file of the run
        res = run_world(tmp, [e])
        none = dict(model_entry(tmp, cpu=X86B), folder=None, jobs_started=0, jobs_returned=0, not_returned=[])
        res_none = run_world(tmp, [e, none])
    assert model(res, X86)["jobs"] == 3 and model(res, X86)["problems"] == []
    line = _run_lines(an.render_report(res))[0]
    assert "; jobs 3/3 (3 pooled); files say aaaaaaaaaa; folder " + e["folder"] in line, line
    assert res["entry_files"][0]["commit"] == "aaaaaaaaaa"
    lines = _run_lines(an.render_report(res_none))
    assert "files say" in lines[0] and "files say" not in lines[1], lines                   # an entry with no file says nothing
    assert res_none["entry_files"][1]["commit"] is None and res_none["entry_files"][1]["files"] == 0


def test_the_commit_comparison_covers_smoke_files_and_test_entries_too():
    with tempfile.TemporaryDirectory() as tmp:
        real = model_entry(tmp)
        smoke_doc = make_doc(smoke=True, run_id=real["run_id"], job="9")
        smoke_doc["run"]["commit"] = "d" * 40                    # a smoke file in a measurement folder, from another commit
        p = os.path.join(tmp, real["folder"], "job-9")
        os.makedirs(p)
        with open(os.path.join(p, sw.RESULT_NAME), "w", encoding="utf-8") as f:
            json.dump(smoke_doc, f)
        real["jobs_started"] = real["jobs_returned"] = 4
        text = stop_text([real], tmp)
        assert " | " not in text and "job-9/" + sw.RESULT_NAME in text and "dddddddddd" in text
        # a test entry: smoke files, and a non-smoke file, each from the wrong commit
        smoke_test = model_entry(tmp, cpu=X86B, smoke=True, n=2, clause="code test", cls="test",
                                 mutate=lambda i, d: d["run"].update(commit="e" * 40) if i == 1 else None)
        text = stop_text([smoke_test], tmp)
        assert " | " not in text and "job-1/" + sw.RESULT_NAME in text and "eeeeeeeeee" in text
        plain_test = model_entry(tmp, cpu=N2, arm=True, n=1, clause="code test", cls="test", runner="ubuntu-24.04-arm",
                                 mutate=lambda i, d: d["run"].update(commit="f" * 40))
        assert "ffffffffff" in stop_text([plain_test], tmp)


def test_the_runner_label_must_be_one_of_the_two_labels_of_the_plan():
    with tempfile.TemporaryDirectory() as tmp:
        good = _entry(tmp)
        arm = model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2)
        assert good["runner"] == "ubuntu-24.04" and arm["runner"] == "ubuntu-24.04-arm"
        assert an.validate_manifest(manifest_of([good, arm])) == []
        for bad in ("", " ", "ubuntu-22.04", "ubuntu-24.04-ARM", "ubuntu-24.04 ", "ubuntu-latest", "ubuntu-24.04-arm64", 5, None,
                    True, ["ubuntu-24.04"], {"runner": "ubuntu-24.04"}):
            probs = an.validate_manifest(manifest_of([dict(good, runner=bad)]))
            assert len(probs) == 1 and probs[0].startswith("entries[0].runner ") and "is not ubuntu-24.04 or ubuntu-24.04-arm" in probs[0], (bad, probs)
        try:
            run_world(tmp, [dict(good, runner="ubuntu-latest")])
        except an.ManifestError as exc:
            assert any("ubuntu-latest" in p for p in exc.problems)
        else:
            raise AssertionError("an unknown runner label must stop the analysis")


def test_a_file_whose_arch_does_not_belong_to_the_runner_label_stops_and_names_the_file():
    for idx in (0, 1, 2):                                      # the first, the middle and the last file of a three-job run
        with tempfile.TemporaryDirectory() as tmp:
            e = model_entry(tmp)                               # ubuntu-24.04: its files store x86_64
            rel = _edit_file(tmp, e, idx, lambda d: d["run"]["runner"].update(arch="aarch64"))
            text = stop_text([e], tmp)
        assert " | " not in text, (idx, text)                  # one stop, for that file only
        assert text == (rel + ": its stored arch is 'aarch64' but the manifest gives runner ubuntu-24.04 (x86_64 expected) for run "
                        + e["run_id"]), (idx, text)
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2)    # ubuntu-24.04-arm: its files store aarch64
        rel = _edit_file(tmp, e, 1, lambda d: d["run"]["runner"].update(arch="x86_64"))
        text = stop_text([e], tmp)
    assert text == (rel + ": its stored arch is 'x86_64' but the manifest gives runner ubuntu-24.04-arm (aarch64 expected) for run "
                    + e["run_id"]), text


def test_a_missing_or_other_arch_in_a_file_is_a_mismatch_with_either_label():
    for label, fn in (("none", lambda d: d["run"]["runner"].update(arch=None)), ("missing", lambda d: d["run"]["runner"].pop("arch")),
                      ("other", lambda d: d["run"]["runner"].update(arch="riscv64")), ("case", lambda d: d["run"]["runner"].update(arch="X86_64")),
                      ("amd64", lambda d: d["run"]["runner"].update(arch="amd64"))):
        with tempfile.TemporaryDirectory() as tmp:
            x86 = model_entry(tmp)
            rel = _edit_file(tmp, x86, 0, fn)
            text = stop_text([x86], tmp)
        assert " | " not in text and text.startswith(rel + ": its stored arch is ") and "(x86_64 expected)" in text, (label, text)
        with tempfile.TemporaryDirectory() as tmp:
            arm = model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2)
            rel = _edit_file(tmp, arm, 2, fn)
            text = stop_text([arm], tmp)
        assert " | " not in text and text.startswith(rel + ": its stored arch is ") and "(aarch64 expected)" in text, (label, text)


def test_the_arch_comparison_covers_smoke_files_and_test_entries_and_leaves_matching_labels_alone():
    with tempfile.TemporaryDirectory() as tmp:
        real = model_entry(tmp)
        smoke_doc = make_doc(smoke=True, run_id=real["run_id"], job="9", arm=True)         # an Arm smoke file in an x86 folder
        p = os.path.join(tmp, real["folder"], "job-9")
        os.makedirs(p)
        with open(os.path.join(p, sw.RESULT_NAME), "w", encoding="utf-8") as f:
            json.dump(smoke_doc, f)
        real["jobs_started"] = real["jobs_returned"] = 4
        text = stop_text([real], tmp)
        assert " | " not in text and text.startswith(real["folder"] + "/job-9/" + sw.RESULT_NAME + ": its stored arch is 'aarch64'")
        smoke_test = model_entry(tmp, cpu=X86B, smoke=True, n=2, clause="code test", cls="test", arch="aarch64", runner="ubuntu-24.04")
        assert "(x86_64 expected)" in stop_text([smoke_test], tmp)
        # entries whose label matches their files pass, whatever their class and whether the file is a smoke file
        ok_test = model_entry(tmp, cpu=X86B, smoke=True, n=2, clause="code test", cls="test")
        ok_arm_test = model_entry(tmp, cpu=N2, arm=True, n=1, clause="code test", cls="test")
        ok_arm = model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2)
        assert ok_arm_test["runner"] == ok_arm["runner"] == "ubuntu-24.04-arm" and ok_test["runner"] == "ubuntu-24.04"
        res = run_world(tmp, [ok_test, ok_arm_test, ok_arm])
        assert model(res, N2)["jobs"] == 3 and model(res, N2)["problems"] == []


def test_a_file_written_by_a_later_attempt_stops_and_says_to_remove_it_and_record_the_job_as_not_returned():
    for idx in (0, 1, 2):                                      # the first, the middle and the last file of a three-job run
        with tempfile.TemporaryDirectory() as tmp:
            e = model_entry(tmp)
            rel = _edit_file(tmp, e, idx, lambda d: d["run"].update(attempt=2))
            text = stop_text([e], tmp)
        assert " | " not in text, (idx, text)                  # one stop, for that file only
        assert text.startswith(rel + ": it was written by attempt 2 of run " + e["run_id"] + " (run.attempt 2); "), (idx, text)
        assert "does not replace it" in text and "remove this file" in text and "did not return, with the reason" in text, text
    with tempfile.TemporaryDirectory() as tmp:                 # a larger attempt, a smoke file of a test entry
        e = model_entry(tmp, cpu=X86B, smoke=True, n=2, clause="code test", cls="test")
        rel = _edit_file(tmp, e, 1, lambda d: d["run"].update(attempt=12))
        assert stop_text([e], tmp).startswith(rel + ": it was written by attempt 12 of run ")
    with tempfile.TemporaryDirectory() as tmp:                 # two files of two runs: each run's stop names its own file
        e1, e2 = model_entry(tmp), model_entry(tmp, cpu=X86B, clause="x86-64 run 2")
        r1 = _edit_file(tmp, e1, 2, lambda d: d["run"].update(attempt=2))
        r2 = _edit_file(tmp, e2, 0, lambda d: d["run"].update(attempt=3))
        text = stop_text([e1, e2], tmp)
        assert text.count(" | ") == 1 and r1 in text and r2 in text and "attempt 3 of run " + e2["run_id"] in text, text


def test_an_absent_attempt_is_a_schema_problem_and_an_attempt_of_one_changes_nothing():
    """Every file records run.attempt (the schema check of sweep.py requires it): a file without it is not read as the first
    attempt, it is a file problem, and the model is not read; an attempt of 1 is the ordinary case."""
    with tempfile.TemporaryDirectory() as tmp:
        plain = run_world(tmp, [model_entry(tmp, mutate=lambda i, d: d["run"].pop("attempt", None))])
        one = run_world(tmp, [model_entry(tmp, mutate=lambda i, d: d["run"].update(attempt=1))])
    m_plain, m_one = model(plain, X86), model(one, X86)
    assert m_one["problems"] == [] and m_one["pooled"] and m_one["jobs"] == 3
    _assert_clause_makes_the_model_not_testable("schema", plain)
    texts = [p["text"] for p in m_plain["problems"] if p["code"] == "schema"]
    assert texts == ["run.attempt is missing or not an integer of 1 or more"] * 3, texts


def test_an_attempt_that_is_not_a_whole_number_from_one_is_a_schema_problem_of_the_file():
    for bad in (0, -1, 1.5, 2.0, "2", "1", True, False, None, [2], {"n": 2}):
        with tempfile.TemporaryDirectory() as tmp:
            res = run_world(tmp, [model_entry(tmp, mutate=lambda i, d: d["run"].update(attempt=bad) if i == 2 else None)])
        _assert_clause_makes_the_model_not_testable("schema", res)
        texts = [p["text"] for p in model(res, X86)["problems"] if p["code"] == "schema"]
        assert any(t.startswith("run.attempt is %r, not a whole number of 1 or more" % (bad,)) for t in texts), (bad, texts)


def test_the_consistency_stops_of_runs_accounting():
    with tempfile.TemporaryDirectory() as tmp:
        e = _entry(tmp)
        assert "folder" in stop_text([dict(e, folder="results/nowhere")], tmp) and "missing" in stop_text([dict(e, folder="results/nowhere")], tmp)
        assert "manifest says 2" in stop_text([dict(e, jobs_returned=2, jobs_started=2)], tmp)
        # a file with a run id the manifest does not list
        stray = make_doc(run_id="39999999999", job="9")
        p = os.path.join(tmp, e["folder"], "job-9")
        os.makedirs(p)
        with open(os.path.join(p, sw.RESULT_NAME), "w", encoding="utf-8") as f:
            json.dump(stray, f)
        assert "does not list" in stop_text([e], tmp)
        # a file that carries the id of another listed run
        other = model_entry(tmp, cpu=X86B)
        shutil_copy = os.path.join(tmp, other["folder"], "job-0", sw.RESULT_NAME)
        with open(shutil_copy, "rb") as f:
            raw = f.read()
        with open(os.path.join(p, sw.RESULT_NAME), "wb") as f:
            f.write(raw)
        assert "lies in the folder of run" in stop_text([e, other], tmp)
        os.remove(os.path.join(p, sw.RESULT_NAME))
        os.rmdir(p)
        # an id that is not an Actions run id
        local = make_doc(run_id="local-2026-10-22", job="1")
        with open(os.path.join(tmp, e["folder"], "job-0", sw.RESULT_NAME), "w", encoding="utf-8") as f:
            json.dump(local, f)
        assert "not an Actions run id" in stop_text([e], tmp)
        with open(os.path.join(tmp, e["folder"], "job-0", sw.RESULT_NAME), "w", encoding="utf-8") as f:
            f.write("{not json")
        assert "not readable JSON" in stop_text([e], tmp)


def test_a_stop_writes_no_result_and_main_exits_with_3():
    with tempfile.TemporaryDirectory() as tmp:
        e = _entry(tmp)
        man, out = os.path.join(tmp, "runs.json"), os.path.join(tmp, "results.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump(manifest_of([dict(e, folder="results/gone")]), f)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = an.main(["--manifest", man, "--base", tmp, "--out", out])
        assert code == 3 and not os.path.exists(out) and "stop" in buf.getvalue()


def test_partial_files_are_listed_with_the_reason_and_never_pooled():
    with tempfile.TemporaryDirectory() as tmp:
        e = _entry(tmp)
        p = os.path.join(tmp, e["folder"], "job-7")
        os.makedirs(p)
        head = {"kind": "forwardt-partial", "cells_expected": 12, "run": {"id": e["run_id"], "job": "7", "runner": {"cpu_model": X86}}}
        with open(os.path.join(p, sw.PARTIAL_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps(head) + "\n" + json.dumps({"cell": {"loop": "t01_sum_size"}}) + "\n"
                    + json.dumps({"stopped": {"reason": "the 45-minute limit", "at": "t02_sum_n.L1"}}) + "\n")
        # a partial file next to a result is not a partial run
        with open(os.path.join(tmp, e["folder"], "job-0", sw.PARTIAL_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps(head) + "\n")
        res = run_world(tmp, [e])
        part = res["analysis"]["partial"]
        assert len(part) == 1 and part[0]["reason"] == "the 45-minute limit" and part[0]["cells_done"] == 1
        assert model(res, X86)["jobs"] == 3
        assert "[partial]" in an.render_report(res)


# ---------------------------------------------------------------- rule 1: smoke files, targets, the 3-job minimum

def test_smoke_files_and_test_runs_are_set_aside_and_never_pooled():
    with tempfile.TemporaryDirectory() as tmp:
        real = model_entry(tmp)
        smoke_doc = make_doc(smoke=True, run_id=real["run_id"], job="9")
        smoke_doc["plan_sha256"] = "0" * 64
        p = os.path.join(tmp, real["folder"], "job-9")
        os.makedirs(p)
        with open(os.path.join(p, sw.RESULT_NAME), "w", encoding="utf-8") as f:
            json.dump(smoke_doc, f)
        real["jobs_started"] = real["jobs_returned"] = 4       # the smoke file counts as a file of the run
        code_test = model_entry(tmp, cpu=X86B, smoke=True, n=2, clause="code test", cls="test")
        nonsmoke_in_test = model_entry(tmp, cpu=N2, arm=True, n=1, clause="code test", cls="test")
        res = run_world(tmp, [real, code_test, nonsmoke_in_test])
        assert [m["cpu_model"] for m in res["analysis"]["models"]] == [X86]
        assert model(res, X86)["jobs"] == 3
        reasons = sorted(a["reason"] for a in res["analysis"]["set_aside"])
        assert reasons.count("smoke file") == 3 and sum("class test" in r for r in reasons) == 1
        assert any("differs from the plan" in n for n in res["analysis"]["notes"])


def test_target_of_follows_rule_1():
    assert an.target_of(X86, ["x86_64"] * 3) == "x86-64"
    assert an.target_of(N2, ["aarch64"] * 3) == "Neoverse-N2"
    assert an.target_of(V3, ["aarch64"] * 3) is None
    assert an.target_of(N2, ["aarch64", "x86_64", "aarch64"]) is None
    assert an.target_of(X86, ["x86_64", None, "x86_64"]) is None
    assert an.target_of(X86, []) is None


def test_neoverse_v3_and_a_missing_cpu_model_belong_to_no_target():
    with tempfile.TemporaryDirectory() as tmp:
        v3 = model_entry(tmp, words=N2_WORDS, arm=True, cpu=V3)
        none = model_entry(tmp, cpu="")
        res = run_world(tmp, [v3, none])
        m = model(res, V3)
        assert m["target"] is None and m["pooled"] is True and m["pred"] is None
        assert res["analysis"]["summaries"]["Neoverse-N2"]["models"] == []
        u = model(res, "unknown")
        assert u["pooled"] is False and "not pooled" in u["reason_not_read"]
        assert "target none" in an.render_report(res)


def test_fewer_than_three_jobs_are_pooled_and_printed_but_not_read():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, n=2)])
        m = model(res, X86)
        assert m["pooled"] is True and m["read"] is False and "fewer than the minimum of 3" in m["reason_not_read"]
        assert all(p["state"] == "not testable" for p in m["pred"]["P0"].values())
        assert all(p["state"] == "not testable" for p in m["pred"]["preds"].values() if p)
        assert m["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["ratio"] > 1.0
        # two jobs in one run and one in another make three jobs of one model
        a = model_entry(tmp, n=2)
        b = model_entry(tmp, n=1)
        res = run_world(tmp, [a, b])
        assert model(res, X86)["read"] is True and model(res, X86)["jobs"] == 3


# ---------------------------------------------------------------- rule 7: one planted problem per clause

def _m_all(fn):
    def mut(i, d):
        fn(d)
    return mut


def _m_last(fn):
    def mut(i, d):
        if i == 2:
            fn(d)
    return mut


def _t01_builds(d):
    return d["loops"]["t01_sum_size"]["builds"]


def _plant_aligned_word(d):
    b = _t01_builds(d)
    b["none_a64"]["vectorization"] = tf.vec((False, None, None))
    d["loops"]["t01_sum_size"]["words"] = sw.words_record(b)


def _plant_n(d):
    d["sizes"]["L2"]["n"]["t01_sum_size"] += 8


PLANTS = {
    "plan_hash": _m_last(lambda d: d.update(plan_sha256="0" * 64)),
    "criteria_hash": _m_last(lambda d: d.update(criteria_sha256="1" * 64)),
    "reps": _m_last(lambda d: d.update(reps_per_side=41)),
    "sizes": _m_last(lambda d: d["sizes"]["L1"]["n"].update(t01_sum_size=d["sizes"]["L1"]["n"]["t01_sum_size"] + 8)),
    "checksum": _m_last(lambda d: d["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["compiled"].update(
        b_checksums=["deadbeefdeadbeef"])),
    "schema": _m_last(lambda d: d["loops"]["t01_sum_size"].pop("source")),
    "aligned_word": _m_all(_plant_aligned_word),
    "clang": _m_all(lambda d: d["run"]["toolchain"].update(clang="Ubuntu clang version 19.1.0")),
    "commit": _m_last(lambda d: d["run"].update(commit="b" * 40)),
    "code_hash": _m_last(lambda d: d["code_sha256"].update({sorted(d["code_sha256"])[0]: "0" * 64})),
    "binary_hash": _m_last(lambda d: _t01_builds(d)["none"].update(binary_sha256="0" * 64)),
    "traps": _m_last(lambda d: _t01_builds(d)["fast"].update(traps=5)),
    "remark": _m_last(lambda d: _t01_builds(d)["none"]["vectorization"].update(width=8)),
    "cache": _m_last(lambda d: d["machine"]["cache_bytes"].update(l1d=d["machine"]["cache_bytes"]["l1d"] + 1024)),
    "n": _m_last(_plant_n),
    "pair_reps": _m_last(lambda d: d["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["aa"].update(
        a_ns=d["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["aa"]["a_ns"][:-1])),
    "arch": _m_last(lambda d: d["run"]["runner"].update(arch="aarch64")),
}


def test_a_clean_model_has_no_file_problem():
    m = model(default_result(), X86)
    assert m["problems"] == [] and m["pooled"] is True and m["read"] is True
    assert set(PLANTS) == set(an.CODE_SINGLE) | set(an.CODE_CROSS)      # one planted problem per code of rule 7


def _assert_clause_makes_the_model_not_testable(code, res):
    m = model(res, X86)
    codes = {p["code"] for p in m["problems"]}
    assert code in codes, (code, sorted(codes))
    assert m["pooled"] is False and m["read"] is False, code
    assert "file problem" in m["reason_not_read"]
    if m["pred"] is not None:
        assert all(p["state"] == "not testable" for p in m["pred"]["P0"].values()), code
        assert all(p["state"] == "not testable" for p in m["pred"]["preds"].values() if p), code
    assert an.render_report(res).count("file problem [%s]" % code) >= 1


# a deviation inside one run is a stop before the analysis starts (the commit against the manifest's head_sha, the arch against
# the runner label); those clauses show up only between two runs of one model, and have their own tests below
_BETWEEN_RUNS = ("commit", "arch")


def test_each_clause_of_rule_7_makes_every_prediction_of_the_model_not_testable():
    for code, mut in sorted(PLANTS.items()):
        if code in _BETWEEN_RUNS:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            _assert_clause_makes_the_model_not_testable(code, run_world(tmp, [model_entry(tmp, mutate=mut)]))


def test_a_commit_that_differs_between_two_runs_of_one_model_makes_the_model_not_testable():
    with tempfile.TemporaryDirectory() as tmp:
        first = model_entry(tmp)
        second = model_entry(tmp, clause="x86-64 run 2", head_sha="b" * 40,
                             mutate=lambda i, d: d["run"].update(commit="b" * 40))
        res = run_world(tmp, [first, second])
        _assert_clause_makes_the_model_not_testable("commit", res)
        m = model(res, X86)
        assert m["jobs"] == 6 and {p["code"] for p in m["problems"] if p["code"] == "commit"} == {"commit"}
        # the run lines say which commit each run's files name
        lines = _run_lines(an.render_report(res))
        assert "files say aaaaaaaaaa" in lines[0] and "files say bbbbbbbbbb" in lines[1]


def test_an_arch_that_differs_between_two_runs_of_one_model_makes_the_model_not_testable():
    with tempfile.TemporaryDirectory() as tmp:
        first = model_entry(tmp)                                                     # ubuntu-24.04, files store x86_64
        second = model_entry(tmp, clause="x86-64 run 2", arch="aarch64")             # ubuntu-24.04-arm, files store aarch64
        assert first["runner"] == "ubuntu-24.04" and second["runner"] == "ubuntu-24.04-arm"
        res = run_world(tmp, [first, second])                                        # each run agrees with its own label: no stop
        _assert_clause_makes_the_model_not_testable("arch", res)
        m = model(res, X86)
        assert m["jobs"] == 6 and {p["code"] for p in m["problems"] if p["code"] == "arch"} == {"arch"}
        assert m["arch"] == ["aarch64", "x86_64"]


def test_the_placeholder_in_the_first_five_lines_of_the_plan_is_a_problem_of_every_model():
    with open(sw.PLAN_FILE, encoding="utf-8") as f:
        text = f.read()
    assert an.plan_placeholder_problem() is None
    with tempfile.TemporaryDirectory() as tmp:
        plan = os.path.join(tmp, "PLAN.md")
        lines = text.split("\n")
        with open(plan, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines[:3] + ["Fixed at __TIME__ by the clock."] + lines[3:]))
        assert "__TIME__" in an.plan_placeholder_problem(plan)
        late = os.path.join(tmp, "LATE.md")
        with open(late, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines[:5] + ["a token __TIME__ on line six"] + lines[5:]))
        assert an.plan_placeholder_problem(late) is None
        h = sw.plan_sha256(plan)

        def own_hash(d):
            d["plan_sha256"] = h
        res = run_world(tmp, [model_entry(tmp, mutate=_m_all(own_hash))], plan_path=plan)
        m = model(res, X86)
        assert {p["code"] for p in m["problems"]} == {"placeholder"}
        assert m["pooled"] is False
        assert any("placeholder" in n for n in res["analysis"]["notes"])


# ---------------------------------------------------------------- rule 13: hashes

def test_hash_notes_flag_a_plan_other_than_the_first_commit_and_changed_code_files():
    with open(sw.PLAN_FILE, encoding="utf-8") as f:
        text = f.read()
    with tempfile.TemporaryDirectory() as tmp:
        plan = os.path.join(tmp, "PLAN.md")
        with open(plan, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\nOne more line.\n")
        h = sw.plan_sha256(plan)

        def own_hash(d):
            d["plan_sha256"] = h
        code_now = sw.code_sha256()
        key = sorted(code_now)[0]
        code_now[key] = "f" * 64
        res = run_world(tmp, [model_entry(tmp, mutate=_m_all(own_hash))], plan_path=plan, code_now=code_now)
        m = model(res, X86)
        assert m["problems"] == [] and m["read"] is True
        assert len(m["hash_notes"]["plan_differs_from_first_commit"]) == 3
        assert m["hash_notes"]["plan_differs_from_current"] == []
        assert m["hash_notes"]["code_files_changed_since_run"] == [key]
        assert any("FIRST_COMMIT_PLAN_SHA256" in n for n in res["analysis"]["notes"])
    # in the ordinary case the stored hashes are the first commit's
    m = model(default_result(), X86)
    assert m["hash_notes"] == {"plan_differs_from_current": [], "plan_differs_from_first_commit": [],
                               "code_files_changed_since_run": []}


# ---------------------------------------------------------------- rules 4 and 6: decidable cells, the forward test

def test_a_cell_is_decidable_at_three_jobs_and_an_aa_half_width_of_exactly_2_percent():
    assert an.cell_decidable(3, 2.0, 3, 2.0) is True
    assert an.cell_decidable(3, 2.0000001, 3, 2.0) is False
    assert an.cell_decidable(2, 0.1, 3, 2.0) is False
    assert an.cell_decidable(3, None, 3, 2.0) is False


def test_the_forward_test_is_the_point_limit_and_the_interval_limit_with_the_floor_and_twice_the_aa_width():
    crit = {"point": 1.02, "floor": 2.0, "multiplier": 2.0}

    def t(ratio, hi, aa):
        return an.forward_test({"ratio": ratio, "ci95": [ratio - 0.001, hi]}, aa, crit)

    assert t(1.02, 1.02, 0.5)["inside"] is True and abs(t(1.0, 1.0, 0.5)["ci_hi_limit"] - 1.02) < 1e-12
    assert t(1.0, 1.0201, 0.5)["inside"] is False
    assert t(1.0201, 1.0201, 0.5)["inside"] is False
    assert abs(t(1.0, 1.0, 1.5)["ci_hi_limit"] - 1.03) < 1e-12
    assert t(1.0, 1.03, 1.5)["inside"] is True and t(1.0, 1.0301, 1.5)["inside"] is False


def test_a_cell_with_a_noisy_identical_binary_pair_is_not_decidable_and_stays_out_of_the_predictions():
    noisy = {("t05_fill_n", "L1", "aa"): 0.3}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, noise=noisy)])
    m = model(res, X86)
    cell = m["loops"]["t05_fill_n"]["cells"]["L1"]
    assert cell["aa_half_width_pct"] > 2.0 and cell["decidable"] is False and cell["forward"] is None
    p3 = m["pred"]["preds"]["P3"]
    assert [i["loop"] for i in p3["items"]] == ["t06_offset"]
    assert p3["not_decidable"] == [{"loop": "t05_fill_n", "size": "L1", "aa_half_width_pct": cell["aa_half_width_pct"]}]
    ok = m["loops"]["t02_sum_n"]["cells"]["L1"]
    assert ok["decidable"] is True and ok["forward"] is not None


# ---------------------------------------------------------------- rules 8 and 9: bands, pairs, judgement

def test_bands_are_closed_at_both_edges():
    b = an.BANDS["P1"]
    assert an.band_state((0.97, 1.03), b) == "inside"
    assert an.band_state((0.9699, 1.0), b) == "straddle"
    assert an.band_state((1.0, 1.0301), b) == "straddle"
    assert an.band_state((0.5, 0.9699), b) == "below"
    assert an.band_state((0.5, 0.97), b) == "straddle"          # hi equals the edge: not below
    assert an.band_state((1.0301, 1.2), b) == "above"
    assert an.band_state((1.03, 1.2), b) == "straddle"          # lo equals the edge: not above
    assert an.band_state((0.5, 1.2), b) == "straddle"
    p3 = an.BANDS["P3"]
    assert an.band_state((1.5, 9.0), p3) == "inside" and an.band_state((1.0, 1.4999), p3) == "below"
    assert an.band_state((1.2, 1.6), p3) == "straddle" and an.band_state((5.0, 1e9), p3) == "inside"
    p4 = an.BANDS["P4"]
    assert an.band_state((0.9, 1.30), p4) == "inside" and an.band_state((1.3001, 1.4), p4) == "above"
    assert an.BANDS["P2"] == (0.97, 1.35) and an.BANDS["P2n"] == (0.90, 1.35) and an.BANDS["P5"] == (0.80, 1.25)
    assert an.BANDS["P6"] == (0.95, 1.15) and an.BANDS["P1_t03_x86"] == (0.79, 1.23)


def test_a_pair_is_inside_outside_or_split_and_the_judgement_follows():
    ps = an.pair_state
    assert ps("inside", "inside") == "inside"
    assert ps("above", "above") == "above" and ps("below", "below") == "below"
    for a, b in (("inside", "above"), ("above", "below"), ("straddle", "straddle"), ("straddle", "above"),
                 ("inside", "straddle")):
        assert ps(a, b) == "split", (a, b)
    j = an.judge
    assert j([]) == "not testable"
    assert j(["inside", "inside"]) == "holds"
    assert j(["inside", "above"]) == "fails" and j(["split", "below"]) == "fails"
    assert j(["inside", "split"]) == "undecided" and j(["straddle"]) == "undecided"


def test_a_split_pair_is_undecided_and_prints_that_the_columns_disagree():
    over = {("t02_sum_n", "L1", "compiled"): 1.10, ("t02_sum_n", "L1", "aligned"): 1.6}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, over=over)])
    p2 = model(res, X86)["pred"]["preds"]["P2"]
    l1 = [i for i in p2["items"] if i["size"] == "L1"][0]
    assert l1["state"] == "split" and p2["state"] == "undecided" and p2["split_items"] == 1
    assert res["analysis"]["summaries"]["x86-64"]["preds"]["P2"]["undecided_resting_on_split"] == 1
    assert "columns disagree" in an.render_report(res)


# ---------------------------------------------------------------- P0 to P6 on one model

def _states(res, cpu=X86):
    m = model(res, cpu)
    out = {p: (r["state"] if r else None) for p, r in m["pred"]["preds"].items()}
    out.update({"P0." + k: v["state"] for k, v in m["pred"]["P0"].items()})
    return out


def test_every_prediction_holds_on_a_model_made_to_match_the_plan():
    st = _states(default_result())
    assert all(v == "holds" for v in st.values() if v), st
    assert st["P6"] is None
    res = default_result()
    assert res["analysis"]["summaries"]["x86-64"]["preds"]["P2"]["word"] == "holds on all 1 readable models"
    assert res["analysis"]["outcome"]["letter"] == "A"


def test_p0_needs_the_predicted_word_and_for_four_loops_a_fast_trap():
    words = ("kept", "lost", "kept", "kept", "lost", "lost")     # t04 is kept, not narrower
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, words=words, fast_traps={"t02_sum_n": 0, "t01_sum_size": 0})])
    m = model(res, X86)
    p0 = m["pred"]["P0"]
    assert p0["t04_scale_n"]["state"] == "fails" and p0["t04_scale_n"]["observed_word"] == "kept"
    assert p0["t02_sum_n"]["state"] == "fails" and p0["t02_sum_n"]["word_ok"] is True and p0["t02_sum_n"]["trap_ok"] is False
    assert p0["t01_sum_size"]["state"] == "holds" and p0["t01_sum_size"]["trap_clause"] is False
    assert p0["t05_fill_n"]["state"] == "holds"
    p4 = m["pred"]["preds"]["P4"]
    assert p4["state"] == "not testable" and p4["left_out"] == ["t04_scale_n"]


def test_p1_bands_differ_for_scale_by_target_and_a_failed_control_marks_the_model():
    over = {"t03_scale_size": 1.15}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, over=over), model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2, over=over)])
    x = model(res, X86)
    assert x["pred"]["preds"]["P1"]["state"] == "holds" and x["pred"]["control_failed"] is None
    n = model(res, N2)
    assert n["pred"]["preds"]["P1"]["state"] == "fails" and "P1 fails" in n["pred"]["control_failed"]
    for pred in ("P6",):
        assert n["pred"]["preds"][pred]["state"] == "not testable (control failed)"
    assert n["pred"]["P0"]["t05_fill_n"]["state"] == "holds"       # P0 is unchanged by the mark
    assert res["analysis"]["summaries"]["Neoverse-N2"]["preds"]["P6"]["marked_control_failed"] == [N2]
    assert res["analysis"]["summaries"]["Neoverse-N2"]["preds"]["P6"]["n_readable"] == 0
    assert res["analysis"]["summaries"]["Neoverse-N2"]["preds"]["P6"]["word"] == "not testable"


def test_a_control_without_its_predicted_word_marks_the_model_and_is_left_out_of_p1():
    words = ("lost", "lost", "kept", "narrower", "lost", "lost")
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, words=words)])
    m = model(res, X86)
    assert "t01_sum_size" in m["pred"]["control_failed"]
    assert m["pred"]["preds"]["P1"]["left_out"] == ["t01_sum_size"]
    assert m["pred"]["preds"]["P2"]["state"] == "not testable (control failed)"
    assert m["pred"]["P0"]["t01_sum_size"]["state"] == "fails"


def test_p2_pairs_t02_across_columns_and_p2n_reads_the_novec_column_alone():
    over = {("t02_sum_n", "L2", "novec"): 1.6}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, over=over)])
    m = model(res, X86)
    assert m["pred"]["preds"]["P2"]["state"] == "holds"
    p2n = m["pred"]["preds"]["P2n"]
    assert p2n["state"] == "fails" and p2n["fail_sides"] == ["above"] and p2n["items"][0]["mode"] == "single"
    assert [i["size"] for i in p2n["items"]] == ["L1", "L2"] and list(p2n["items"][0]["columns"]) == ["novec"]
    words = ("kept", "scalar", "kept", "narrower", "lost", "lost")      # t02 is not lost: nothing to compare
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, words=words)])
    m = model(res, X86)
    assert m["pred"]["preds"]["P2"]["state"] == "not testable" and m["pred"]["preds"]["P2n"]["state"] == "not testable"
    assert m["pred"]["preds"]["P2"]["left_out"] == ["t02_sum_n"]


def test_p3_p4_and_p6_read_their_loops_sizes_and_columns():
    over = {("t05_fill_n", "L1", "aligned"): 1.2, ("t04_scale_n", "L2", "aligned"): 1.5, ("t04_scale_n", "L2", "compiled"): 1.0}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, over=over),
                              model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2, over={("t06_offset", "L2", "compiled"): 1.3})])
    x = model(res, X86)["pred"]["preds"]
    assert x["P3"]["state"] == "undecided" and {i["loop"]: i["state"] for i in x["P3"]["items"]} == {"t05_fill_n": "split", "t06_offset": "inside"}
    assert [i["size"] for i in x["P3"]["items"]] == ["L1", "L1"]            # L1 only
    assert x["P4"]["state"] == "fails" and [(i["size"], i["state"]) for i in x["P4"]["items"]] == [("L1", "inside"), ("L2", "above")]
    assert list(x["P4"]["items"][0]["columns"]) == ["aligned"]              # aligned only
    n = model(res, N2)["pred"]["preds"]
    assert n["P6"]["state"] == "fails" and n["P6"]["fail_sides"] == ["above"]
    assert len(n["P6"]["items"]) == 8 and n["P1"]["state"] == "holds"
    assert "P2" not in n or n["P2"] is None


def test_the_lost_loops_that_are_not_lost_are_left_out_of_a_prediction_with_the_others_read():
    words = ("kept", "lost", "kept", "narrower", "kept", "lost")          # t05 is kept on this model
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, words=words)])
    p3 = model(res, X86)["pred"]["preds"]["P3"]
    assert p3["left_out"] == ["t05_fill_n"] and p3["state"] == "holds" and [i["loop"] for i in p3["items"]] == ["t06_offset"]
    s = res["analysis"]["summaries"]["x86-64"]["preds"]["P3"]
    assert s["left_out"] == {X86: ["t05_fill_n"]} and "left out" in an.render_report(res)


# ---------------------------------------------------------------- P5 and the joint bootstrap (rule 10)

def test_p5_is_the_quotient_of_l2_over_l1_with_one_joint_bootstrap():
    over = {("t02_sum_n", "L1"): 1.10, ("t02_sum_n", "L2"): 1.6}
    with tempfile.TemporaryDirectory() as tmp:
        rid = next_rid()
        docs = [make_doc(run_id=rid, job=str(i + 1), over=over) for i in range(3)]
        res = run_world(tmp, [write_run(tmp, docs)])
    m = model(res, X86)
    q = m["loops"]["t02_sum_n"]["p5"]["compiled"]
    l1 = m["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["ratio"]
    l2 = m["loops"]["t02_sum_n"]["cells"]["L2"]["pairs"]["compiled"]["ratio"]
    assert abs(q["quotient"] - l2 / l1) < 1e-12 and q["state"] == "above" and q["ci95"][0] < q["quotient"] < q["ci95"][1]
    again = an.joint_quotient(X86, "t02_sum_n", "compiled", docs, 200)
    assert again == {k: q[k] for k in again}
    # the joint interval is not the ratio of the two marginal intervals
    c1 = m["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["ci95"]
    c2 = m["loops"]["t02_sum_n"]["cells"]["L2"]["pairs"]["compiled"]["ci95"]
    assert q["ci95"] != [c2[0] / c1[1], c2[1] / c1[0]]
    p5 = m["pred"]["preds"]["P5"]
    assert p5["state"] == "fails" and p5["fail_sides"] == ["above"]
    assert [i["loop"] for i in p5["items"]] == ["t02_sum_n", "t05_fill_n", "t06_offset"]
    assert p5["items"][0]["size"] == "L2/L1" and p5["items"][1]["state"] == "inside"
    assert pool.seed_for(X86, "forwardt|t02_sum_n|compiled|joint", "jobs") != pool.seed_for(X86, "forwardt|t02_sum_n|L1|compiled", "jobs")


def test_p5_needs_both_sizes_decidable_and_a_lost_loop():
    noisy = {("t02_sum_n", "L2", "aa"): 0.3}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, noise=noisy)])
    m = model(res, X86)
    assert m["loops"]["t02_sum_n"]["p5"] == {}
    p5 = m["pred"]["preds"]["P5"]
    assert [i["loop"] for i in p5["items"]] == ["t05_fill_n", "t06_offset"] and p5["state"] == "holds"
    assert p5["not_decidable"][0]["loop"] == "t02_sum_n"
    words = ("kept", "scalar", "kept", "narrower", "kept", "kept")
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, words=words)])
    m = model(res, X86)
    p5 = m["pred"]["preds"]["P5"]
    assert p5["state"] == "not testable" and p5["left_out"] == ["t02_sum_n", "t05_fill_n", "t06_offset"]
    assert all(m["loops"][lp]["p5"] == {} for lp in LOOPS)          # no quotient is computed for a loop that is not lost
    assert set(default_result()["analysis"]["models"][0]["loops"]["t05_fill_n"]["p5"]) == {"compiled", "aligned"}


def test_the_joint_quotient_draws_its_jobs_under_the_joint_stat_id_and_each_size_under_its_own():
    asked = []
    real = pool.seed_for

    def spy(cpu, stat_id, stream):
        asked.append((stat_id, stream))
        return real(cpu, stat_id, stream)

    with tempfile.TemporaryDirectory() as tmp:
        rid = next_rid()
        docs = [make_doc(run_id=rid, job=str(i + 1)) for i in range(3)]
        pool.seed_for = spy
        try:
            an.joint_quotient(X86, "t05_fill_n", "aligned", docs, 50)
        finally:
            pool.seed_for = real
    assert ("forwardt|t05_fill_n|aligned|joint", "jobs") in asked
    for size in SIZES:
        sid = "forwardt|t05_fill_n|%s|aligned" % size
        assert (sid, "side0") in asked and (sid, "side1") in asked
    assert not any(s == "jobs" and i.endswith("|L1|aligned") for i, s in asked)


# ---------------------------------------------------------------- rule 11: summaries over the models of a target

def test_the_summary_words_of_rule_11():
    s = an.summarize_target
    row = lambda c, st, lo=None: {"cpu_model": c, "state": st, "left_out": lo}
    a = s([row("a", "holds"), row("b", "holds")])
    assert a["word"] == "holds on all 2 readable models" and a["state"] == "holds"
    b = s([row("a", "holds"), row("b", "fails")])
    assert b["word"] == "fails on at least one" and b["failed_on"] == ["b"]
    c = s([row("a", "holds"), row("b", "undecided")])
    assert c["word"] == "undecided" and c["undecided_on"] == ["b"]
    d = s([row("a", "fails"), row("b", "undecided")])
    assert d["word"] == "fails on at least one"
    e = s([row("a", "not testable"), row("b", "not testable (control failed)")])
    assert e["word"] == "not testable" and e["n_readable"] == 0 and len(e["not_testable_on"]) == 2
    f = s([row("a", "holds"), row("b", "not testable (control failed)"), row("c", "not testable", ["t05_fill_n"])])
    assert f["word"] == "holds on all 1 readable models" and f["left_out"] == {"c": ["t05_fill_n"]}


def test_a_model_marked_control_failed_stays_outside_the_readable_models_of_a_prediction():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp), model_entry(tmp, cpu=X86B, over={"t01_sum_size": 1.3})])
    s = res["analysis"]["summaries"]["x86-64"]["preds"]["P2"]
    assert s["word"] == "holds on all 1 readable models" and s["marked_control_failed"] == [X86B]
    assert model(res, X86B)["pred"]["preds"]["P2"]["state"] == "not testable (control failed)"
    assert res["analysis"]["summaries"]["x86-64"]["P0"]["t02_sum_n"]["word"] == "holds on all 2 readable models"


# ---------------------------------------------------------------- the outcome table

LETTER_CASES = {
    "A": ("holds", "holds"), "B": ("holds", "fails"), "C": ("holds", "undecided"), "D": ("above", "holds"),
    "E": ("above", "fails"), "F": ("above", "undecided"), "G": ("below", "holds"), "H": ("untestable", "holds"),
    "I": ("undecided", "fails"), "J": ("undecided", "undecided"), "K": ("both", "holds"),
}


def _letter_world(p2, p3):
    over, noise = {}, {}
    if p2 == "above":
        over["t02_sum_n"] = 1.6
    elif p2 == "below":
        over["t02_sum_n"] = 0.5
    elif p2 == "both":
        over[("t02_sum_n", "L1")], over[("t02_sum_n", "L2")] = 1.6, 0.5
    elif p2 == "undecided":
        over["t02_sum_n"] = 1.35
        noise["t02_sum_n"] = 0.05
    elif p2 == "untestable":
        noise.update({("t02_sum_n", "L1", "aa"): 0.3, ("t02_sum_n", "L2", "aa"): 0.3})
    if p3 == "fails":
        over["t05_fill_n"] = over["t06_offset"] = 1.2
    elif p3 == "undecided":
        over["t05_fill_n"] = over["t06_offset"] = 1.5
        noise["t05_fill_n"] = noise["t06_offset"] = 0.05
    return over, noise


def test_each_of_the_eleven_letters_is_reached_from_planted_p2_and_p3_states():
    for letter, (p2, p3) in sorted(LETTER_CASES.items()):
        over, noise = _letter_world(p2, p3)
        with tempfile.TemporaryDirectory() as tmp:
            res = run_world(tmp, [model_entry(tmp, over=over, noise=noise or 0.002)])
        oc = res["analysis"]["outcome"]
        assert oc["letter"] == letter, (letter, oc["row"], oc["column"], p2, p3)
        assert oc["text"] == an.LETTER_TEXT[letter]
        assert oc["may_say_lost_sum_and_lost_writes_differ"] is (letter == "A")
    assert sorted(LETTER_CASES) == list("ABCDEFGHIJK")


def test_the_outcome_table_gives_the_letter_of_all_twenty_cells():
    want = {"holds": "ABCC", "fails above 1.35": "DEFF", "fails below 0.97": "GGGG", "fails on both sides": "KKKK",
            "undecided or not testable": "HIJJ"}
    assert set(an.TABLE) == set(an.ROWS) == set(want)
    for row, letters in want.items():
        for col, letter in zip(an.COLS, letters):
            assert an.letter_for(row, col) == letter, (row, col)
    assert set(an.LETTER_TEXT) == set("ABCDEFGHIJK")


def test_p2_row_and_p3_column_are_read_off_the_models():
    rec = lambda st, sides=(): {"state": st, "items": [{"state": s} for s in sides], "left_out": []}
    assert an.p2_row([("a", rec("holds"))]) == ("holds", [])
    assert an.p2_row([("a", rec("fails", ["above"])), ("b", rec("holds"))]) == ("fails above 1.35", ["above"])
    assert an.p2_row([("a", rec("fails", ["below"]))]) == ("fails below 0.97", ["below"])
    assert an.p2_row([("a", rec("fails", ["above"])), ("b", rec("fails", ["below"]))])[0] == "fails on both sides"
    assert an.p2_row([("a", rec("holds")), ("b", rec("undecided"))])[0] == "undecided or not testable"
    assert an.p2_row([("a", rec("not testable (control failed)"))])[0] == "undecided or not testable"
    assert an.p2_row([])[0] == "undecided or not testable"
    sm = lambda st: {"state": st}
    assert [an.p3_column(sm(x)) for x in ("holds", "fails", "undecided", "not testable")] == list(an.COLS)


def test_two_models_decide_the_p2_row_together_and_only_models_where_both_are_read_allow_the_differ_sentence():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp), model_entry(tmp, cpu=X86B, over={"t02_sum_n": 1.6}),
                              model_entry(tmp, cpu="AMD EPYC 9V45 96-Core Processor", n=2)])
    oc = res["analysis"]["outcome"]
    assert oc["row"] == "fails above 1.35" and oc["letter"] == "D"
    assert oc["p2_read_models"] == [X86, X86B] and oc["both_read_models"] == [X86, X86B]
    assert oc["may_say_lost_sum_and_lost_writes_differ"] is False
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp), model_entry(tmp, cpu=X86B, n=2)])
    oc = res["analysis"]["outcome"]
    assert oc["letter"] == "A" and oc["both_read_models"] == [X86] and oc["may_say_lost_sum_and_lost_writes_differ"] is True


def test_a_limit_is_stated_only_for_a_cell_whose_own_interval_meets_it():
    assert an.cell_limits("t02_sum_n", (1.0, 1.35)) == ["at most 1.35x"]
    assert an.cell_limits("t02_sum_n", (1.0, 1.36)) == []
    assert an.cell_limits("t05_fill_n", (1.0, 1.49)) == ["less than 1.5x"]
    assert an.cell_limits("t05_fill_n", (1.0, 1.5)) == []
    assert an.cell_limits("t06_offset", (1.5, 2.0)) == ["at or above 1.5x"]
    assert an.cell_limits("t06_offset", (1.49, 2.0)) == []
    assert an.cell_limits("t01_sum_size", (0.9, 1.0)) == []
    oc = default_result()["analysis"]["outcome"]
    t02 = [c for c in oc["cells"] if c["loop"] == "t02_sum_n"]
    assert len(t02) == 4 and all(c["limits"] == ["at most 1.35x"] for c in t02)
    assert {c["inside_forward_range"] for c in t02 if c["column"] == "aligned"} == {False}
    w = [c for c in oc["cells"] if c["loop"] != "t02_sum_n"]
    assert len(w) == 4 and all(c["limits"] == ["at or above 1.5x"] and c["size"] == "L1" for c in w)


def test_the_standing_listing_of_the_four_variable_bound_loops():
    over = {"t04_scale_n": 1.0}
    noise = {("t06_offset", "L1", "aa"): 0.3, ("t06_offset", "L2", "aa"): 0.3}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, over=over, noise=noise), model_entry(tmp, cpu=X86B, n=2)])
    rows = {(r["cpu_model"], r["loop"]): r for r in res["analysis"]["forward_listing"]}
    assert sorted({k[1] for k in rows}) == ["t02_sum_n", "t04_scale_n", "t05_fill_n", "t06_offset"]
    assert len(rows) == 8
    t04 = rows[(X86, "t04_scale_n")]
    assert [c["size"] for c in t04["decidable_aligned_cells"]] == ["L1", "L2"]
    assert all(c["inside_forward_range"] is True for c in t04["decidable_aligned_cells"])
    assert rows[(X86, "t02_sum_n")]["decidable_aligned_cells"][0]["inside_forward_range"] is False
    assert rows[(X86, "t06_offset")]["none_decidable"] is True and rows[(X86B, "t02_sum_n")]["none_decidable"] is True
    report = an.render_report(res)
    assert "no decidable cell" in report and "standing listing" in report


# ---------------------------------------------------------------- the second printing, rule 12 content

def test_the_second_printing_leaves_out_the_runs_marked_not_in_the_plan():
    with tempfile.TemporaryDirectory() as tmp:
        a = model_entry(tmp)
        b = model_entry(tmp, cpu=X86B, clause="not in the plan", reason="a rerun after the runner type changed")
        res = run_world(tmp, [a, b])
        assert [m["cpu_model"] for m in res["analysis"]["models"]] == sorted([X86B, X86])
        sec = res["analysis_without_not_in_plan"]
        assert [m["cpu_model"] for m in sec["models"]] == [X86]
        assert any("not in the plan" in s["reason"] and s["run_id"] == b["run_id"] for s in sec["set_aside"])
        assert res["manifest_summary"]["not_in_the_plan"] == 1 and res["manifest_summary"]["entries"] == 2
        rep = an.render_report(res)
        assert "without the measurement runs marked 'not in the plan'" in rep and "1 marked 'not in the plan'" in rep
        assert "a rerun after the runner type changed" in rep
    assert default_result()["analysis_without_not_in_plan"] == {"same_as_analysis": True}


def test_the_n2_sum_ratios_are_reported_without_a_band_and_the_placement_statistic_is_stored():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2)])
    rep = res["analysis"]["reported_n2_t02"]
    assert len(rep) == 1 and rep[0]["word"] == "lost" and 1.1 < rep[0]["cells"]["L1"]["compiled"] < 1.3
    m = model(res, N2)
    cell = m["loops"]["t02_sum_n"]["cells"]["L1"]
    assert cell["placement"]["jobs"] == 3 and "ci95" in cell["placement"]
    assert m["loops"]["t02_sum_n"]["hot_loops"]["any_differs"] is False
    assert m["loops"]["t02_sum_n"]["traps"]["fast"] == 1 and m["loops"]["t02_sum_n"]["traps"]["none"] == 0
    assert "contains_one" in cell["pairs"]["compiled"] and cell["pairs"]["novec"] is not None
    assert m["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["novec"] is None


# ---------------------------------------------------------------- the statistics

def test_the_statistic_ids_and_seeds_follow_rule_2():
    res = default_result()
    m = model(res, X86)
    with tempfile.TemporaryDirectory() as tmp:
        rid = next_rid()
        docs = [make_doc(run_id=rid, job=str(i + 1)) for i in range(3)]
    cells = [d["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"] for d in docs]
    st = pool.pair_stat(X86, "forwardt|t02_sum_n|L1|compiled", [(c["compiled"]["a_ns"], c["compiled"]["b_ns"]) for c in cells], 200)
    with tempfile.TemporaryDirectory() as tmp:
        again = run_world(tmp, [write_run(tmp, docs)])
    got = model(again, X86)["loops"]["t02_sum_n"]["cells"]["L1"]
    assert got["pairs"]["compiled"]["ratio"] == st["ratio"] and got["pairs"]["compiled"]["ci95"] == st["ci95"]
    pl = pool.placement_stat(X86, "forwardt|t02_sum_n|L1|placement",
                             [(c["compiled"]["a_ns"], c["compiled"]["b_ns"], c["aligned"]["a_ns"], c["aligned"]["b_ns"]) for c in cells], 200)
    assert got["placement"]["ratio"] == pl["ratio"] and got["placement"]["ci95"] == pl["ci95"]
    aa = pool.pair_stat(X86, "forwardt|t02_sum_n|L1|aa", [(c["aa"]["a_ns"], c["aa"]["b_ns"]) for c in cells], 200)
    assert got["aa_half_width_pct"] == aa["half_width_pct"]
    assert m["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["jobs"] == 3


def _indep(samples, B=4000, seed=7):
    """The pooled interval by a second implementation: plain Python, random.Random(seed), as harness/pool_check.py does."""
    rng = random.Random(seed)
    J, L = len(samples), len(samples[0][0])
    out = []
    for _ in range(B):
        total = 0.0
        for _j in range(J):
            a, b = samples[rng.randrange(J)]
            ma = statistics.median([a[rng.randrange(L)] for _ in range(L)])
            mb = statistics.median([b[rng.randrange(L)] for _ in range(L)])
            total += math.log(mb / ma)
        out.append(math.exp(total / J))
    out.sort()
    return out[int(0.025 * B)], out[int(0.975 * B) - 1]


def test_an_independent_recomputation_of_a_pooled_ratio_and_interval_agrees():
    over = {"t02_sum_n": 1.2}
    with tempfile.TemporaryDirectory() as tmp:
        rid = next_rid()
        docs = [make_doc(run_id=rid, job=str(i + 1), over=over, noise=0.02) for i in range(3)]
        res = run_world(tmp, [write_run(tmp, docs)], resamples=pool.RESAMPLES)
    st = model(res, X86)["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]
    samples = [(d["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["a_ns"],
                d["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["b_ns"]) for d in docs]
    per_job = [statistics.median(b) / statistics.median(a) for a, b in samples]
    assert all(abs(x - y) < 1e-12 for x, y in zip(per_job, st["per_job"]))
    pooled = math.exp(sum(math.log(r) for r in per_job) / 3)
    assert abs(pooled - st["ratio"]) < 1e-9
    lo, hi = _indep(samples)
    width = st["ci95"][1] - st["ci95"][0]
    tol = 0.15 * width + 0.0005 * st["ratio"]
    assert abs(lo - st["ci95"][0]) <= tol and abs(hi - st["ci95"][1]) <= tol, ((lo, hi), st["ci95"])
    assert width / 1.5 <= (hi - lo) <= width * 1.5
    assert st["ci95"][0] < st["ratio"] < st["ci95"][1]


# ---------------------------------------------------------------- --verify

def _stored_world(tmp, boot=100, resamples=None, name="results.json"):
    """Three jobs stored under tmp and analysed by main() into tmp/<name>; the registered 2000 resamples unless given."""
    rid = next_rid()
    docs = [make_doc(run_id=rid, job=str(i + 1), boot=boot) for i in range(3)]
    e = write_run(tmp, docs)
    man = os.path.join(tmp, "runs.json")
    with open(man, "w", encoding="utf-8") as f:
        json.dump(manifest_of([e]), f)
    out = os.path.join(tmp, name)
    extra = [] if resamples is None else ["--resamples", str(resamples)]
    with contextlib.redirect_stdout(io.StringIO()):
        assert an.main(["--manifest", man, "--base", tmp, "--out", out] + extra) == 0
    return e, man, out


def test_verify_round_trip_and_the_three_ways_it_fails():
    with tempfile.TemporaryDirectory() as tmp:
        e, man, out = _stored_world(tmp)
        manifest = an.read_manifest(man)
        code, lines = an.verify(manifest, tmp, out, file_resamples=100)
        assert code == 0, lines
        assert any("verified 3 file(s): 0 with problems" in x for x in lines) and any("matches the recomputation" in x for x in lines)
        # (1) a number of results.json changed
        with open(out, encoding="utf-8") as f:
            stored = json.load(f)
        stored["analysis"]["models"][0]["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["ratio"] += 1e-6
        bad = os.path.join(tmp, "bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump(stored, f)
        code, lines = an.verify(manifest, tmp, bad, file_resamples=100)
        assert code == 1 and any("differs" in x and "ratio" in x for x in lines)
        # (2) a stored sample changed, so the stored within-job ratio is not what the samples give
        path = os.path.join(tmp, e["folder"], "job-1", sw.RESULT_NAME)
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        pr = doc["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["compiled"]
        pr["a_ns"] = [x * 2.0 for x in pr["a_ns"]]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        code, lines = an.verify(manifest, tmp, out, file_resamples=100)
        assert code == 1 and any("not what the samples give" in x for x in lines) and any("1 with problems" in x for x in lines)
        # (3) a stop
        code, lines = an.verify(manifest_of([dict(e, folder="results/gone")]), tmp, out, file_resamples=100)
        assert code == 3 and any("missing" in x for x in lines)


def test_the_default_run_stores_the_registered_2000_resamples_and_a_file_made_with_200_fails_verify():
    assert pool.RESAMPLES == 2000
    with tempfile.TemporaryDirectory() as tmp:
        e, man, out = _stored_world(tmp)
        with open(out, encoding="utf-8") as f:
            assert json.load(f)["analysis"]["resamples"] == pool.RESAMPLES == 2000
        manifest = an.read_manifest(man)
        code, lines = an.verify(manifest, tmp, out, file_resamples=100)
        assert code == 0, lines
        few = os.path.join(tmp, "few.json")
        with contextlib.redirect_stdout(io.StringIO()):
            assert an.main(["--manifest", man, "--base", tmp, "--out", few, "--resamples", "200"]) == 0
        with open(few, encoding="utf-8") as f:
            assert json.load(f)["analysis"]["resamples"] == 200
        code, lines = an.verify(manifest, tmp, few, file_resamples=100)
        assert code == 1 and any("stored resamples 200 is not 2000" in x for x in lines), lines
        assert any("does NOT match" in x for x in lines)
        # the stored number alone is enough to fail: the same document with 2000 written over the 200 still differs in its numbers
        with open(few, encoding="utf-8") as f:
            doc = json.load(f)
        doc["analysis"]["resamples"] = 2000
        with open(few, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        code, lines = an.verify(manifest, tmp, few, file_resamples=100)
        assert code == 1 and not any("stored resamples" in x for x in lines) and any("differs" in x for x in lines)


def test_diff_paths_compares_floats_with_a_tolerance_and_everything_else_exactly():
    base = {"f": 1.2345, "i": 3, "w": "kept", "b": True, "n": None, "l": [1.0, 2.0], "z": 0.0}
    same = copy.deepcopy(base)
    same["f"] = 1.2345 * (1 + 1e-13)
    same["l"] = [1.0 + 1e-13, 2.0]
    same["z"] = 1e-13                       # absolute tolerance near zero
    assert an.diff_paths(base, same) == []
    for key, val in (("f", 1.2345 * (1 + 1e-6)), ("i", 4), ("w", "lost"), ("b", False), ("b", 1), ("n", 0.0), ("z", 1e-9),
                     ("l", [1.0, 2.0, 3.0])):
        other = copy.deepcopy(base)
        other[key] = val
        assert an.diff_paths(base, other), (key, val)
    # the relative part of the tolerance matters at large magnitudes, where 1e-10 of the value is far above the absolute part
    assert an.diff_paths({"big": 1000.0}, {"big": 1000.0 * (1 + 1e-10)}) == []
    assert an.diff_paths({"big": 1000.0}, {"big": 1000.0 * (1 + 1e-7)}) != []
    assert an.diff_paths({"i": 3}, {"i": 3.0}) == [] and an.diff_paths({"i": 3}, {"i": 3.0000001}) != []
    assert an.diff_paths({"a": 1}, {"a": 1, "b": 2}) and an.diff_paths({"a": 1}, {"a": "1"})


def test_verify_tolerates_last_bit_noise_and_recomputes_with_the_hashes_the_results_file_stored():
    with tempfile.TemporaryDirectory() as tmp:
        e, man, out = _stored_world(tmp)
        manifest = an.read_manifest(man)
        with open(out, encoding="utf-8") as f:
            stored = json.load(f)
        pair = stored["analysis"]["models"][0]["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]
        ratio = pair["ratio"]

        def with_ratio(value):
            pair["ratio"] = value
            path = os.path.join(tmp, "noisy.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(stored, f)
            return an.verify(manifest, tmp, path, file_resamples=100)

        code, lines = with_ratio(ratio * (1 + 1e-13))
        assert code == 0, lines
        code, lines = with_ratio(ratio * (1 + 1e-6))
        assert code == 1 and any("differs" in x and "ratio" in x for x in lines)
        pair["ratio"] = ratio
        # a hashed file of the wider project changed after results.json was written: a line of its own, exit code 0
        key = sorted(sw.CODE_FILES)[0]
        changed = dict(sw.code_sha256(), **{key: "0" * 64})
        code, lines = an.verify(manifest, tmp, out, code_now=changed, file_resamples=100)
        assert code == 0, lines
        moved = [x for x in lines if x.startswith("code files changed since results.json was written")]
        assert len(moved) == 1 and key in moved[0] and moved[0].count(",") == 0
        assert not any(x.startswith("plan changed") for x in lines)
        code, lines = an.verify(manifest, tmp, out, file_resamples=100)
        assert code == 0 and not any("code files changed" in x for x in lines)
        # a plan that does not hash to the stored plan hash: its own line, and a failure
        with open(sw.PLAN_FILE, "rb") as f:
            raw = f.read()
        other = os.path.join(tmp, "PLAN.md")
        with open(other, "wb") as f:
            f.write(raw + b"\nan edit\n")
        code, lines = an.verify(manifest, tmp, out, plan_path=other, file_resamples=100)
        assert code == 1 and sum(x.startswith("plan changed since results.json") for x in lines) == 1, lines
        assert any("matches the recomputation" in x for x in lines)


def test_verify_takes_no_resamples_flag_and_an_unregistered_run_may_not_write_the_registered_results_file():
    with tempfile.TemporaryDirectory() as tmp:
        man = os.path.join(tmp, "runs.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "entries": []}, f)
        out = os.path.join(tmp, "results.json")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert an.main(["--manifest", man, "--base", tmp, "--out", out, "--verify", "--resamples", "200"]) == 2
            assert an.main(["--manifest", man, "--base", tmp, "--out", out, "--resamples", "2000", "--verify"]) == 2
        assert "takes no --resamples" in buf.getvalue()
        # --resamples other than 2000: loud note; the registered path is refused, another --out is written
        saved = an.RESULTS_FILE
        an.RESULTS_FILE = os.path.join(tmp, "registered", "results.json")
        os.makedirs(os.path.dirname(an.RESULTS_FILE))
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                assert an.main(["--manifest", man, "--base", tmp, "--resamples", "200"]) == 2
                assert an.main(["--manifest", man, "--base", tmp, "--resamples", "200", "--out", an.RESULTS_FILE]) == 2
            assert not os.path.exists(an.RESULTS_FILE)
            text = buf.getvalue()
            assert text.count("NOT THE REGISTERED STATISTIC") == 2 and text.count("refusing to write") == 2
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                assert an.main(["--manifest", man, "--base", tmp, "--resamples", "200", "--no-write"]) == 0
                assert an.main(["--manifest", man, "--base", tmp, "--resamples", "200", "--out", out]) == 0
            assert "NOT THE REGISTERED STATISTIC" in buf.getvalue() and os.path.exists(out) and not os.path.exists(an.RESULTS_FILE)
            # the registered number writes the registered file
            with contextlib.redirect_stdout(io.StringIO()):
                assert an.main(["--manifest", man, "--base", tmp]) == 0
            assert os.path.exists(an.RESULTS_FILE)
        finally:
            an.RESULTS_FILE = saved


def test_verify_with_an_empty_manifest_and_no_results_file_is_ok_and_with_one_it_must_match():
    with tempfile.TemporaryDirectory() as tmp:
        code, lines = an.verify({"schema": 1, "entries": []}, tmp, os.path.join(tmp, "results.json"))
        assert code == 0 and "nothing to verify" in lines[0]
        out = os.path.join(tmp, "results.json")
        empty = os.path.join(tmp, "empty-runs.json")           # its own empty manifest: the committed one will not stay empty
        with open(empty, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "entries": []}, f)
        with contextlib.redirect_stdout(io.StringIO()):
            an.main(["--manifest", empty, "--base", tmp, "--out", out])
        code, lines = an.verify({"schema": 1, "entries": []}, tmp, out)
        assert code == 0, lines
        code, lines = an.verify(manifest_of([model_entry(tmp)]), tmp, out)
        assert code == 1 and any("does NOT match" in x for x in lines)


def test_the_results_file_stores_the_open_upper_end_of_the_p3_band_as_null():
    text = an.dump_results(default_result())
    assert "Infinity" not in text and "NaN" not in text
    doc = json.loads(text)
    items = doc["analysis"]["models"][0]["pred"]["preds"]["P3"]["items"]
    assert items[0]["band"] == {"lo": 1.5, "hi": None}
    assert json.loads(an.dump_results(json.loads(text))) == doc          # nothing is lost on a second pass


# ---------------------------------------------------------------- bad input does not crash

def _cli(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = an.main(list(argv))
    return code, buf.getvalue()


def _problem_codes(res, cpu=X86):
    return sorted({p["code"] for p in model(res, cpu)["problems"]})


def test_a_record_of_the_wrong_type_is_a_schema_problem_and_not_a_crash():
    def pair(d):
        d["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["compiled"] = "x"

    def pair_list(d):
        d["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["compiled"] = [1, 2]

    def vec_str(d):
        d["loops"]["t01_sum_size"]["builds"]["none"]["vectorization"] = "x"

    def vec_list(d):
        d["loops"]["t01_sum_size"]["builds"]["none"]["vectorization"] = ["a"]

    for name, fn in (("pair as a string", pair), ("pair as a list", pair_list), ("vectorization as a string", vec_str),
                     ("vectorization as a list", vec_list)):
        for which in ("every job", "one job"):
            def mut(i, d, fn=fn, which=which):
                if which == "every job" or i == 1:
                    fn(d)

            with tempfile.TemporaryDirectory() as tmp:
                res = run_world(tmp, [model_entry(tmp, mutate=mut)])
                m = model(res, X86)
                assert "schema" in _problem_codes(res), (name, which)
                assert not m["read"] and not m["pooled"], (name, which)
                assert m["pred"]["preds"]["P2"]["state"] == "not testable", (name, which)
                assert "file problem [schema]" in an.render_report(res), (name, which)


def test_timing_samples_that_are_not_finite_numbers_above_zero_are_a_schema_problem():
    cases = (("zero", 0.0), ("negative", -3.0), ("nan", float("nan")), ("infinity", float("inf")),
             ("negative infinity", float("-inf")), ("a string", "12.5"), ("a bool", True))
    for side in ("a_ns", "b_ns"):
        for name, value in cases:
            def mut(i, d, side=side, value=value):
                if i == 1:
                    d["loops"]["t02_sum_n"]["cells"]["L2"]["pairs"]["aligned"][side][3] = value

            with tempfile.TemporaryDirectory() as tmp:
                res = run_world(tmp, [model_entry(tmp, mutate=mut)])
                m = model(res, X86)
                texts = [p["text"] for p in m["problems"] if p["code"] == "schema"]
                assert any("t02_sum_n.L2.aligned." + side in t and "1 timing sample" in t for t in texts), (side, name, texts)
                assert not m["read"] and not m["pooled"] and m["pred"]["preds"]["P2"]["state"] == "not testable", (side, name)
    with tempfile.TemporaryDirectory() as tmp:           # the same world with ordinary samples has no such problem
        res = run_world(tmp, [model_entry(tmp)])
        assert model(res, X86)["problems"] == [] and model(res, X86)["read"]


def test_a_model_whose_pooling_raises_is_listed_and_not_read_and_the_other_models_are_analysed():
    original = an.analyse_model
    for exc_type in (ValueError, ZeroDivisionError, AttributeError, KeyError, TypeError, OverflowError):
        def broken(cpu, recs, ctx, resamples, exc_type=exc_type):
            if cpu == X86B:
                raise exc_type("planted failure")
            return original(cpu, recs, ctx, resamples)

        an.analyse_model = broken
        try:
            with tempfile.TemporaryDirectory() as tmp:
                res = run_world(tmp, [model_entry(tmp), model_entry(tmp, cpu=X86B)])
                bad, good = model(res, X86B), model(res, X86)
                text = an.render_report(res)
        finally:
            an.analyse_model = original
        assert good["read"] and good["pooled"] and good["problems"] == []
        assert not bad["read"] and not bad["pooled"] and bad["jobs"] == 3
        assert [p["code"] for p in bad["problems"]] == ["analysis_error"]
        assert exc_type.__name__ in bad["problems"][0]["text"] and "planted failure" in bad["problems"][0]["text"]
        assert bad["pred"]["preds"]["P2"]["state"] == "not testable" and "file problem" in bad["pred"]["preds"]["P2"]["reason"]
        assert good["pred"]["preds"]["P2"]["state"] != "not testable"
        assert "file problem [analysis_error] model:" in text
        assert res["analysis_without_not_in_plan"] == {"same_as_analysis": True}


def test_the_command_line_ends_bad_input_in_one_line_and_an_exit_code():
    with tempfile.TemporaryDirectory() as tmp:
        man = os.path.join(tmp, "runs.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "entries": []}, f)
        out = os.path.join(tmp, "results.json")
        base = ["--manifest", man, "--base", tmp, "--out", out]

        def one_line(code_text, want, *needles):
            code, text = code_text
            assert code == want, (code, text)
            assert text.count("\n") == 1 and "Traceback" not in text, text
            for n in needles:
                assert n in text, (n, text)
            return text

        # a stop (3): the manifest is missing, is a directory, is not JSON, is not UTF-8 text
        one_line(_cli("--manifest", os.path.join(tmp, "nope.json"), "--base", tmp, "--out", out), 3, "cannot read the manifest")
        one_line(_cli("--manifest", tmp, "--base", tmp, "--out", out), 3, "cannot read the manifest")
        bad = os.path.join(tmp, "bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("{not json")
        one_line(_cli("--manifest", bad, "--base", tmp, "--out", out), 3, "not readable JSON")
        with open(bad, "wb") as f:
            f.write(b"\xff\xfe\x00{")
        one_line(_cli("--manifest", bad, "--base", tmp, "--out", out), 3, "not readable JSON")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("[1, 2]")
        code, text = _cli("--manifest", bad, "--base", tmp, "--out", out)
        assert code == 3 and "not a JSON object" in text and "Traceback" not in text
        assert not os.path.exists(out)
        # usage (2): a flag without its value, a number that is not one, a directory for --out, an unwritable --out
        one_line(_cli("--manifest"), 2, "--manifest needs a value")
        one_line(_cli(*base, "--resamples"), 2, "--resamples needs a value")
        one_line(_cli("--manifest", man, "--base", tmp, "--out", "--verify"), 2, "--out needs a value")
        one_line(_cli(*base, "--resamples", "many"), 2, "not a whole number")
        one_line(_cli(*base, "--resamples", "2.5"), 2, "not a whole number")
        one_line(_cli(*base, "--resamples", "0"), 2, "not above zero")
        one_line(_cli(*base, "--resamples", "-4"), 2, "not above zero")
        one_line(_cli("--manifest", man, "--base", tmp, "--out", tmp), 2, "is a directory")
        code, text = _cli("--manifest", man, "--base", tmp, "--out", os.path.join(tmp, "no-such-folder", "r.json"))
        assert code == 2 and "forwardt: cannot write" in text and "Traceback" not in text
        assert not os.path.exists(out)
        # --verify with a results file that is a directory or is not JSON: a failure (1), a line, no traceback
        code, text = _cli("--manifest", man, "--base", tmp, "--out", tmp, "--verify")
        assert code == 1 and "cannot be read" in text and "Traceback" not in text, (code, text)
        with open(out, "w", encoding="utf-8") as f:
            f.write("{broken")
        code, text = _cli(*base, "--verify")
        assert code == 1 and "is not readable JSON" in text and "Traceback" not in text, (code, text)
        # and the good case still works
        os.remove(out)
        assert _cli(*base)[0] == 0 and os.path.exists(out)
        assert _cli(*base, "--verify")[0] == 0


def test_the_docstring_lists_the_exit_codes_the_command_line_uses():
    doc = an.__doc__
    assert "EXIT CODES" in doc
    table = doc.split("EXIT CODES", 1)[1].split("WHAT IT WRITES", 1)[0]
    for code in ("0", "1", "2", "3"):
        assert any(line.strip().startswith(code + " ") for line in table.splitlines()), code
    # the cases the table once left out, each tied to what the command line really does
    flat = " ".join(table.split())
    for phrase in ("nothing to verify", "its stored resamples is not 2000", "the plan file no longer hashes to the plan hash",
                   "(unless --verify,", "or --no-write,", "other letter case", "a short message", "prints this text"):
        assert phrase in flat, phrase
    assert "one line on stdout" not in doc


NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
DOC_ENTRY = {"run_id": "39000000000", "runner": "ubuntu-24.04", "head_sha": "a" * 40, "created_at": "2026-10-22T14:03:11Z",
             "class": "measurement", "clause": "x86-64 run 1", "jobs_started": 6, "jobs_returned": 6, "not_returned": [],
             "folder": "results/x"}


def test_the_docstring_documents_every_manifest_key_every_value_it_names_and_stays_within_120_columns():
    doc = an.__doc__
    assert all(len(line) <= 120 for line in doc.splitlines()), [ln for ln in doc.splitlines() if len(ln) > 120]
    manifest = doc.split("THE MANIFEST", 1)[1].split("EXIT CODES", 1)[0]
    top, rest = manifest.split("ENTRY = {", 1)
    entry, stops = rest.split("The analysis stops", 1)
    # every key the validator knows is shown in the part of the example it belongs to
    for k in ("schema", "entries") + tuple(an.TOP_OPTIONAL):
        assert f'"{k}":' in top, k
    for k in an.ENTRY_REQUIRED + an.ENTRY_OPTIONAL:
        assert f'"{k}":' in entry, k
    # the keys required once there are entries are the run of keys the example marks, the others stand outside that run
    req = an.TOP_REQUIRED_WITH_ENTRIES
    pos = [top.index(f'"{k}":') for k in req]
    assert pos == sorted(pos) and req[0] == "branch" and req[-1] == "test_ratios_read", pos
    assert f"the {NUMBER_WORDS[len(req)]} keys from here to" in top and "REQUIRED once" in top
    for k in (k for k in an.TOP_OPTIONAL if k not in req):
        assert not pos[0] <= top.index(f'"{k}":') <= pos[-1], k
    # the optional keys of an entry are the last ones of the example and each says so
    assert f"except the last {NUMBER_WORDS[len(an.ENTRY_OPTIONAL)]} is REQUIRED" in entry
    lines = entry.splitlines()
    for k in an.ENTRY_OPTIONAL:
        assert "optional" in next(ln for ln in lines if ln.strip().startswith(f'"{k}":')), k
    for k in an.ENTRY_REQUIRED:
        assert all("optional" not in ln for ln in lines if f'"{k}":' in ln), k
    # the values it names are the ones the validator accepts
    flat = " ".join(manifest.split())
    assert " | ".join((an.RUNNER_X86, an.RUNNER_ARM)) in flat and " | ".join(an.CLASSES) in flat
    assert " | ".join(an.CLAUSES + (an.NOT_IN_PLAN,)) in flat
    assert "40 lower-case hex" in flat and "UTC" in flat and "positive finite number" in flat
    # every cause of a stop is named
    flat_stops = " ".join(stops.split())
    for phrase in ("manifest itself is malformed", "folder named in the manifest is missing", "run id that the manifest does not list",
                   "stored twice", "run.commit is not the entry's head_sha", "stored arch is not the one of the entry's runner label",
                   "run.attempt is above 1", "differs from that entry's jobs_returned", "is not an Actions run id",
                   "cannot be read or is not readable JSON", "nested too deeply"):
        assert phrase in flat_stops, phrase


def test_what_the_docstring_says_a_manifest_value_may_be_is_what_the_validator_accepts():
    def probs(**kw):
        return an.validate_manifest({"schema": 1, "entries": [dict(DOC_ENTRY, **kw)], **META})

    assert probs() == []
    assert any("head_sha" in p for p in probs(head_sha="A" * 40))                       # 40 lower-case hex
    for bad in ("2026-10-22 14:03:11", "2026-10-22T14:03:11+00:00", "2026-10-22T14:03:11.5Z", "2026-10-22T14:03Z"):
        assert any("created_at" in p for p in probs(created_at=bad)), bad               # UTC, written exactly like the example
    assert any("digits" in p for p in probs(run_id=39000000000))                        # a text of digits
    assert probs(time_limit_minutes=47.5) == [] and any("time_limit_minutes" in p for p in probs(time_limit_minutes=-1))
    assert any("gives no reason" in p for p in probs(clause="not in the plan"))
    assert probs(clause="not in the plan", reason="typed by hand") == []
    assert any("folder" in p for p in probs(folder=None))                               # a measurement run with returned jobs
    assert probs(**{"class": "test"}, folder=None) == []
    assert any("unknown key" in p for p in probs(colour="red"))
    base = {"schema": 1, "entries": [], "note": "free text"}
    assert an.validate_manifest(base) == []
    for bad in (True, "1", 2):
        assert any("schema" in p for p in an.validate_manifest(dict(base, schema=bad))), bad
    assert any("note" in p for p in an.validate_manifest(dict(base, note="")))
    assert any("unknown top-level" in p for p in an.validate_manifest(dict(base, flavour=1)))


def test_the_exit_codes_the_table_names_are_the_ones_the_command_line_returns():
    with tempfile.TemporaryDirectory() as tmp:
        man = os.path.join(tmp, "runs.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "entries": []}, f)
        out = os.path.join(tmp, "results.json")
        base = ["--manifest", man, "--base", tmp]
        code, text = _cli(*base, "--out", out, "--verify")                 # no run and no results.json: nothing to verify, 0
        assert code == 0 and "nothing to verify" in text
        code, text = _cli(*base, "--out", tmp, "--no-write")               # a directory as --out is no harm when nothing is written
        assert code == 0 and "Traceback" not in text
        code, text = _cli(*base, "--out", tmp)                             # when something would be written, it is a usage error
        assert code == 2 and "is a directory" in text
        code, text = _cli(*base, "--out", out, "--bogus-flag")             # an unknown argument prints the module text
        assert code == 2 and text.strip() == an.__doc__.strip()


# ---------------------------------------------------------------- bad input of unusual kinds ends in a message, not a traceback

HUGE = 10 ** 400                    # a whole number that json reads and that no float can hold
DEEP = "[" * 200000                 # nested far beyond the interpreter's recursion limit


def test_a_whole_number_too_large_for_a_float_is_not_a_time_limit_or_a_sample_and_is_no_crash():
    assert an._is_time_limit(45) and an._is_positive_finite(3.5)
    assert not an._is_time_limit(HUGE) and not an._is_positive_finite(HUGE) and not an._is_positive_finite(-HUGE)
    for side in ("a_ns", "b_ns"):
        def mut(i, d, side=side):
            if i == 1:
                d["loops"]["t02_sum_n"]["cells"]["L2"]["pairs"]["aligned"][side][3] = HUGE

        with tempfile.TemporaryDirectory() as tmp:
            res = run_world(tmp, [model_entry(tmp, mutate=mut)])
            m = model(res, X86)
            texts = [p["text"] for p in m["problems"] if p["code"] == "schema"]
            assert any("t02_sum_n.L2.aligned." + side in t and "1 timing sample" in t for t in texts), (side, texts)
            assert all(len(t) < 400 for t in texts)                    # the number is cut short, not printed in full
            assert not m["read"] and not m["pooled"] and m["pred"]["preds"]["P2"]["state"] == "not testable"
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        man, out = os.path.join(tmp, "runs.json"), os.path.join(tmp, "results.json")
        for label, manifest in (("top level", manifest_of([e], time_limit_minutes=HUGE)),
                                ("entry", manifest_of([dict(e, time_limit_minutes=HUGE)]))):
            with open(man, "w", encoding="utf-8") as f:
                json.dump(manifest, f)
            code, text = _cli("--manifest", man, "--base", tmp, "--out", out)
            assert code == 3 and text.count("\n") == 2 and "time_limit_minutes is not a positive number" in text, (label, text)
            assert "Traceback" not in text and not os.path.exists(out), label


def test_a_stored_whole_number_too_large_for_a_float_is_a_difference_and_not_a_crash():
    assert an._same_scalar(HUGE, 1.0) is False and an._same_scalar(1.0, HUGE) is False
    assert an._same_scalar(HUGE, float(10 ** 300)) is False and an._same_scalar(HUGE, HUGE) is True
    assert an._same_scalar(3, 3.0) is True
    d = an.diff_paths({"analysis": {"ratio": HUGE}}, {"analysis": {"ratio": 1.0}})
    assert len(d) == 1 and d[0].startswith("/analysis/ratio: ") and len(d[0]) < 200, d
    with tempfile.TemporaryDirectory() as tmp:                         # the same through --verify
        e, man, out = _stored_world(tmp)
        manifest = an.read_manifest(man)
        with open(out, encoding="utf-8") as f:
            stored = json.load(f)
        stored["analysis"]["models"][0]["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["ratio"] = HUGE
        bad = os.path.join(tmp, "huge.json")
        with open(bad, "w", encoding="utf-8") as f:
            json.dump(stored, f)
        code, lines = an.verify(manifest, tmp, bad, file_resamples=100)
        assert code == 1 and any(x.startswith("results.json differs: ") and "ratio" in x for x in lines), lines
        assert all(len(x) < 300 for x in lines)


def test_a_folder_in_the_place_of_a_result_or_partial_file_is_a_line_and_not_a_crash():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        os.makedirs(os.path.join(tmp, e["folder"], "job-x", sw.RESULT_NAME))
        text = stop_text([e], tmp)
        assert "job-x/" + sw.RESULT_NAME + ": cannot be read: " in text and "not readable JSON" not in text, text
        man, out = os.path.join(tmp, "runs.json"), os.path.join(tmp, "results.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump(manifest_of([e]), f)
        code, text = _cli("--manifest", man, "--base", tmp, "--out", out)
        assert code == 3 and text.count("\n") == 2 and "cannot be read" in text and "Traceback" not in text   # a header, one problem
        assert not os.path.exists(out)
    with tempfile.TemporaryDirectory() as tmp:                         # a partial file that is a folder: listed, not pooled
        e = model_entry(tmp)
        os.makedirs(os.path.join(tmp, e["folder"], "job-7", sw.PARTIAL_NAME))
        res = run_world(tmp, [e])
        (part,) = res["analysis"]["partial"]
        assert part["reason"].startswith("the file cannot be read: ") and part["cells_done"] == 0
        assert model(res, X86)["jobs"] == 3
        assert "[partial]" in an.render_report(res)


def test_json_nested_beyond_the_recursion_limit_is_unreadable_JSON_and_not_a_crash():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        man, out = os.path.join(tmp, "runs.json"), os.path.join(tmp, "results.json")
        with open(man, "w", encoding="utf-8") as f:
            f.write(DEEP)                                              # the manifest
        code, text = _cli("--manifest", man, "--base", tmp, "--out", out)
        assert code == 3 and text.count("\n") == 1 and "not readable JSON" in text and "Traceback" not in text, (code, text)
        with open(man, "w", encoding="utf-8") as f:
            json.dump(manifest_of([e]), f)
        p = os.path.join(tmp, e["folder"], "job-x")
        os.makedirs(p)
        with open(os.path.join(p, sw.RESULT_NAME), "w", encoding="utf-8") as f:
            f.write(DEEP)                                              # a result file
        text = stop_text([e], tmp)
        assert "job-x/" + sw.RESULT_NAME + ": not readable JSON" in text, text
        os.remove(os.path.join(p, sw.RESULT_NAME))
        with open(os.path.join(p, sw.PARTIAL_NAME), "w", encoding="utf-8") as f:       # a partial file with a deep line in it
            f.write(json.dumps({"kind": "forwardt-partial", "cells_expected": 12}) + "\n" + DEEP + "\n"
                    + json.dumps({"cell": {"loop": "t01_sum_size"}}) + "\n")
        res = run_world(tmp, [e])
        (part,) = res["analysis"]["partial"]
        assert part["cells_done"] == 1 and part["cells_expected"] == 12
    with tempfile.TemporaryDirectory() as tmp:                         # the stored results.json under --verify
        e, man, out = _stored_world(tmp)
        with open(out, "w", encoding="utf-8") as f:
            f.write(DEEP)
        code, text = _cli("--manifest", man, "--base", tmp, "--out", out, "--verify")
        assert code == 1 and "is not readable JSON" in text and "Traceback" not in text, (code, text)


def test_the_registered_results_file_is_refused_under_another_spelling_of_its_path():
    with tempfile.TemporaryDirectory() as tmp:
        man = os.path.join(tmp, "runs.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "entries": []}, f)
        saved = an.RESULTS_FILE
        an.RESULTS_FILE = os.path.join(tmp, "registered", "results.json")
        os.makedirs(os.path.dirname(an.RESULTS_FILE))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                assert an.main(["--manifest", man, "--base", tmp]) == 0          # the registered file, written with 2000
            with open(an.RESULTS_FILE, "rb") as f:
                before = f.read()
            variants = [os.path.join(tmp, "registered", "..", "registered", "results.json"),
                        os.path.join(tmp, "registered", ".", "results.json")]
            upper = an.RESULTS_FILE.upper()
            if os.path.exists(upper) or os.path.normcase("A") != "A":
                variants.append(upper)          # a file system that does not tell the cases apart names the same file
            alias = os.path.join(tmp, "alias.json")
            try:
                os.link(an.RESULTS_FILE, alias)
                variants.append(alias)          # a hard link is the same file under another name
            except (OSError, NotImplementedError, AttributeError):
                pass
            assert len(variants) >= 2
            for v in variants:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    assert an.main(["--manifest", man, "--base", tmp, "--resamples", "200", "--out", v]) == 2, v
                assert "refusing to write" in buf.getvalue(), v
                with open(an.RESULTS_FILE, "rb") as f:
                    assert f.read() == before, v
            other = os.path.join(tmp, "other.json")                            # another file is still written
            with contextlib.redirect_stdout(io.StringIO()):
                assert an.main(["--manifest", man, "--base", tmp, "--resamples", "200", "--out", other]) == 0
            assert os.path.exists(other)
            assert an._same_path(an.RESULTS_FILE, an.RESULTS_FILE) and not an._same_path(an.RESULTS_FILE, other)
            assert not an._same_path(os.path.join(tmp, "nope-1.json"), os.path.join(tmp, "nope-2.json"))
        finally:
            an.RESULTS_FILE = saved


def test_a_registered_results_file_that_does_not_exist_yet_is_refused_under_another_spelling_too():
    with tempfile.TemporaryDirectory() as tmp:
        man = os.path.join(tmp, "runs.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump({"schema": 1, "entries": []}, f)
        folder = os.path.join(tmp, "registered")
        os.makedirs(folder)
        saved = an.RESULTS_FILE
        an.RESULTS_FILE = os.path.join(folder, "results.json")            # not written: only the spellings can decide
        try:
            variants = []
            if os.path.normcase("A") != "A":
                variants.append(an.RESULTS_FILE.upper())                  # a file system that folds case
            link = os.path.join(tmp, "link")
            try:
                os.symlink(folder, link, target_is_directory=True)
                variants.append(os.path.join(link, "results.json"))       # the same folder under a link
            except (OSError, NotImplementedError, AttributeError):
                pass
            assert variants, "this system neither folds case nor makes links: no spelling to try"
            for v in variants:
                assert an._same_path(v, an.RESULTS_FILE), v
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    assert an.main(["--manifest", man, "--base", tmp, "--resamples", "200", "--out", v]) == 2, v
                assert "refusing to write" in buf.getvalue(), v
                assert not os.path.exists(an.RESULTS_FILE), v
            other = os.path.join(folder, "other.json")                    # another name in the same folder is still written
            with contextlib.redirect_stdout(io.StringIO()):
                assert an.main(["--manifest", man, "--base", tmp, "--resamples", "200", "--out", other]) == 0
            assert os.path.exists(other) and not os.path.exists(an.RESULTS_FILE)
        finally:
            an.RESULTS_FILE = saved


def test_a_mismatch_of_kinds_in_verify_names_the_kinds_and_a_long_value_is_cut():
    d = an.diff_paths({"analysis": {"a": list(range(5000))}}, {"analysis": 5})
    assert d == ["/analysis: type dict vs int"], d
    assert an.diff_paths({"x": [1, 2]}, {"x": {"k": 1}}) == ["/x: type list vs dict"]
    assert an.diff_paths({"x": 5}, {"x": [1, 2]}) == ["/x: type int vs list"]
    assert an.diff_paths({"x": None}, {"x": {"k": 1}}) == ["/x: type NoneType vs dict"]
    # a scalar that differs is printed as before when it is short, and cut at 80 characters when it is not
    assert an.diff_paths({"w": "kept"}, {"w": "lost"}) == ["/w: 'kept' vs 'lost'"]
    (line,) = an.diff_paths({"w": "x" * 500}, {"w": "y" * 500})
    assert line == "/w: " + repr("x" * 500)[:77] + "..." + " vs " + repr("y" * 500)[:77] + "...", line
    (line,) = an.diff_paths({"w": HUGE}, {"w": 7})
    assert len(line) < 200 and line.endswith("... vs 7"), line
    # the number of lines is still limited
    many = an.diff_paths({str(i): "a" for i in range(100)}, {str(i): "b" for i in range(100)})
    assert len(many) == 20


# ---------------------------------------------------------------- the job count beside every number, the few-jobs caveat

_INTERVAL = re.compile(r"\(\d+\.\d{4} to \d+\.\d{4}\)")
_JOBS = re.compile(r"\(\d+ jobs?\)")


def _caveat():
    return sw.criteria()["v3"]["pooling"]["few_jobs_caveat"]


def _statistic_rows(x, path=""):
    """Every dict below x that is a printed statistic (it has a ratio and an interval)."""
    if isinstance(x, dict):
        if "ratio" in x and "ci95" in x:
            yield path, x
        for k, v in x.items():
            yield from _statistic_rows(v, path + "/" + str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _statistic_rows(v, "%s[%d]" % (path, i))


def test_the_caveat_and_the_range_it_names_are_the_criteria_sentence_and_the_minimum():
    assert an.FEW_JOBS_MAX == 5
    sentence = _caveat()
    minimum = sw.criteria()["v3"]["pooling"]["minimum_jobs"]
    assert "with %d to %d jobs" % (minimum, an.FEW_JOBS_MAX) in sentence       # a change of either side shows here
    res = default_result()
    assert res["analysis"]["few_jobs"] == {"minimum": minimum, "maximum": an.FEW_JOBS_MAX, "caveat": sentence}


def test_every_stored_statistic_carries_the_job_count_of_its_model():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, n=3), model_entry(tmp, cpu=X86B, n=4),
                              model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2, n=6)])
    an_ = res["analysis"]
    jobs = {m["cpu_model"]: m["jobs"] for m in an_["models"]}
    assert jobs == {X86: 3, X86B: 4, N2: 6}
    for m in an_["models"]:
        seen = 0
        for path, st in _statistic_rows(m):
            assert st.get("jobs") == m["jobs"], (m["cpu_model"], path)
            seen += 1
        assert seen >= 60, (m["cpu_model"], seen)          # every model brings its statistics: the walk is not empty
    for c in an_["outcome"]["cells"]:
        assert c["jobs"] == jobs[c["cpu_model"]]
    for r in an_["forward_listing"]:
        for c in r["decidable_aligned_cells"]:
            assert c["jobs"] == jobs[r["cpu_model"]]
    assert an_["outcome"]["cells"] and any(r["decidable_aligned_cells"] for r in an_["forward_listing"])
    for r in an_["reported_n2_t02"]:
        assert r["jobs"] == jobs[r["cpu_model"]]
    for target, s in an_["summaries"].items():
        assert s["jobs"] == {c: jobs[c] for c in s["models"]}
        for loop in an.LOOPS:
            for x in s["P0"][loop]["models"]:
                assert x["jobs"] == jobs[x["cpu_model"]]


def test_a_model_with_three_to_five_jobs_prints_the_caveat_and_every_number_prints_its_job_count():
    sentence = _caveat()
    for n in (3, 4, 5):
        with tempfile.TemporaryDirectory() as tmp:
            res = run_world(tmp, [model_entry(tmp, n=n)])
        text = an.render_report(res)
        assert text.count(sentence) == 3, (n, text.count(sentence))       # the model block and the two later sections
        assert any(line.startswith("   caveat (%d jobs): " % n) and sentence in line for line in text.split("\n")), n
        assert model(res, X86)["few_jobs_caveat"] == sentence
        intervals = 0
        for line in text.split("\n"):
            k = len(_INTERVAL.findall(line))
            if k:
                intervals += k
                assert len(_JOBS.findall(line)) >= k, line
                assert set(_JOBS.findall(line)) == {"(%d jobs)" % n}, line
        assert intervals >= 60, intervals          # the loop looked at the interval-bearing lines of the report
        assert any("t02_sum_n" in line and "%d jobs" % n in line for line in text.split("\n"))
        assert "(models: %s (%d jobs))" % (X86, n) in text
        # the sections that stand away from the model block say it too, once each
        assert sum(line.startswith("   caveat for %s (%d jobs): " % (X86, n)) for line in text.split("\n")) == 2


def test_a_model_with_six_jobs_prints_the_count_and_no_caveat_and_an_unread_model_prints_none():
    sentence = _caveat()
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, n=6)])
    text = an.render_report(res)
    assert sentence not in text and "caveat" not in text and model(res, X86)["few_jobs_caveat"] is None
    for line in text.split("\n"):
        k = len(_INTERVAL.findall(line))
        if k:
            assert len(_JOBS.findall(line)) >= k and set(_JOBS.findall(line)) == {"(6 jobs)"}, line
    with tempfile.TemporaryDirectory() as tmp:           # 2 jobs: not read, so no number to qualify and no caveat
        res = run_world(tmp, [model_entry(tmp, n=2)])
    assert sentence not in an.render_report(res) and model(res, X86)["few_jobs_caveat"] is None
    # one job is "1 job" in the text
    assert an.jobs_text(1) == "1 job" and an.jobs_text(3) == "3 jobs"


def test_the_caveat_line_before_a_section_names_only_the_models_of_three_to_five_jobs_whose_numbers_it_lists():
    sentence = _caveat()
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, n=3), model_entry(tmp, cpu=X86B, n=6)])
    lines = an.render_report(res).split("\n")
    caveat_for = [x for x in lines if x.startswith("   caveat for ")]
    assert len(caveat_for) == 2 and all(X86 in x and X86B not in x and "(3 jobs)" in x and sentence in x for x in caveat_for)
    own = [x for x in lines if x.startswith("   caveat (")]
    assert len(own) == 1 and "(3 jobs)" in own[0]
    at = [i for i, x in enumerate(lines) if x.startswith("   caveat for ")]
    i_out = next(i for i, x in enumerate(lines) if x.startswith("-- outcome"))
    j_list = next(i for i, x in enumerate(lines) if x.startswith("-- the four variable-bound loops"))
    assert i_out < at[0] < j_list < at[1]



# ---------------------------------------------------------------- partial coverage: "holds at L1; L2 not decidable"

def _section(lines, start, stop_prefix="-- "):
    """The lines from the first one that starts with `start` up to (not including) the next section line."""
    i = next(k for k, x in enumerate(lines) if x.startswith(start))
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith(stop_prefix)), len(lines))
    return lines[i:j]


def test_an_undecidable_l2_cell_of_the_sum_gives_the_qualifier_in_the_target_summary_and_in_the_outcome_block():
    undec = {("t02_sum_n", "L2", "aa"): 0.3}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, noise=undec)])
    a = res["analysis"]
    cell = model(res, X86)["loops"]["t02_sum_n"]["cells"]["L2"]
    assert cell["decidable"] is False and cell["aa_half_width_pct"] > 2.0
    want = "holds at t02_sum_n L1; t02_sum_n L2 not decidable"
    p2 = a["summaries"][an.TARGET_X86]["preds"]["P2"]
    assert p2["state"] == "holds" and p2["word"] == "holds on all 1 readable models"           # the word is unchanged
    assert p2["coverage"] == {X86: {"state": "holds", "decided": [{"loop": "t02_sum_n", "size": "L1"}],
                                    "not_decidable": [{"loop": "t02_sum_n", "size": "L2",
                                                       "aa_half_width_pct": cell["aa_half_width_pct"]}],
                                    "text": want}}
    oc = a["outcome"]
    assert oc["partial_coverage"]["P2"][X86]["text"] == want and oc["partial_coverage"]["P3"] == {}
    assert oc["letter"] == default_result()["analysis"]["outcome"]["letter"]                 # the letter logic did not move
    lines = an.render_report(res).split("\n")
    out = _section(lines, "-- outcome")
    assert "   partial coverage P2 on %s: %s" % (X86, want) in out
    assert not any("partial coverage P3" in x for x in out)
    summ = _section(lines, "-- " + an.TARGET_X86)
    i = summ.index("   P2: holds on all 1 readable models")
    assert summ[i + 1] == "      partial coverage on %s: %s" % (X86, want)


def test_the_p3_and_p5_qualifiers_name_the_combinations_that_were_not_decidable():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, noise={("t06_offset", "L1", "aa"): 0.3})])
    oc = res["analysis"]["outcome"]
    assert oc["partial_coverage"]["P3"][X86]["text"] == "holds at t05_fill_n L1; t06_offset L1 not decidable"
    assert oc["partial_coverage"]["P2"] == {}
    assert oc["p3_summary"]["coverage"][X86]["not_decidable"][0]["loop"] == "t06_offset"
    # the pair of the P5 quotient needs both sizes: one noisy size takes the whole pair out
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, noise={("t02_sum_n", "L2", "aa"): 0.3})])
    p5 = res["analysis"]["summaries"][an.TARGET_X86]["preds"]["P5"]["coverage"][X86]
    assert p5["text"] == "holds at t05_fill_n L2/L1, t06_offset L2/L1; t02_sum_n L1+L2 not decidable", p5
    assert "      partial coverage on %s: %s" % (X86, p5["text"]) in an.render_report(res).split("\n")


def test_no_qualifier_without_an_undecidable_cell_or_for_a_model_that_is_not_read():
    res = default_result()["analysis"]
    assert res["outcome"]["partial_coverage"] == {"P2": {}, "P3": {}}
    for target in res["summaries"].values():
        for p in target["preds"].values():
            assert p["coverage"] == {}
        for p in target["P0"].values():
            assert p["coverage"] == {}
    assert "partial coverage" not in an.render_report(default_result())
    # a model with every t02_sum_n cell undecidable has P2 not testable: nothing to qualify
    both = {("t02_sum_n", "L1", "aa"): 0.3, ("t02_sum_n", "L2", "aa"): 0.3}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, noise=both)])
    assert model(res, X86)["pred"]["preds"]["P2"]["state"] == "not testable"
    assert res["analysis"]["outcome"]["partial_coverage"]["P2"] == {}
    # a model marked control failed is outside the summary of P2 and P3
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, over={"t01_sum_size": 1.3}, noise={("t02_sum_n", "L2", "aa"): 0.3})])
    assert model(res, X86)["pred"]["control_failed"]
    assert res["analysis"]["outcome"]["partial_coverage"] == {"P2": {}, "P3": {}}


def test_the_qualifier_names_only_the_models_with_an_undecidable_cell():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, noise={("t02_sum_n", "L2", "aa"): 0.3}), model_entry(tmp, cpu=X86B)])
    p2 = res["analysis"]["summaries"][an.TARGET_X86]["preds"]["P2"]
    assert p2["word"] == "holds on all 2 readable models" and list(p2["coverage"]) == [X86]
    assert list(res["analysis"]["outcome"]["partial_coverage"]["P2"]) == [X86]
    text = an.render_report(res)
    assert "partial coverage on %s:" % X86 in text and "partial coverage on %s:" % X86B not in text
    assert "partial coverage P2 on %s:" % X86B not in text



# ---------------------------------------------------------------- the cells of the outcome block under each letter (plan, outcome table)

def test_the_stored_text_of_letter_d_is_the_plans_row_verbatim():
    plan_path = os.path.join(os.path.dirname(os.path.abspath(an.__file__)), "PLAN.md")
    with open(plan_path, encoding="utf-8", newline="") as f:
        plan = f.read().replace("\r\n", "\n")
    rows = [x for x in plan.split("\n") if x.startswith("| D | ")]
    assert len(rows) == 1 and rows[0].endswith(" |")
    assert an.LETTER_TEXT["D"] == rows[0][len("| D | "):-2]
    # the clause with the census count, its unit and its method is whole (the plan allows that sentence and no shorter one)
    for part in ("228 lost loops", "a per-function count at 38 source locations", "with the share that has one of the six shapes not counted",
                 "a sentence that names none, everywhere"):
        assert part in an.LETTER_TEXT["D"], part


WRITES_BOTH = ["less than 1.5x", "at or above 1.5x"]
# what each letter's row lets the page state about a cell, written out here from PLAN.md (sum limit and forward-range
# statement together; the write limits that may be stated): a letter can only take away from the standing rule
PERMITS = {"A": (True, WRITES_BOTH), "B": (True, WRITES_BOTH), "C": (True, []),
           "D": (False, ["at or above 1.5x"]), "E": (False, []), "F": (False, []),
           "G": (False, WRITES_BOTH), "H": (False, ["at or above 1.5x"]), "I": (False, WRITES_BOTH),
           "J": (False, []), "K": (False, WRITES_BOTH)}


def test_the_permission_of_each_letter_and_p3_column():
    assert sorted(PERMITS) == sorted(an.LETTER_CELLS) == list("ABCDEFGHIJK")
    for letter, (sum_ok, writes) in PERMITS.items():
        for column in an.COLS:
            perm = an.cell_permission(letter, column)
            w = [] if letter in "GK" and column in ("undecided", "not testable") else writes
            assert (perm["sum"], perm["write_limits"]) == (sum_ok, w), (letter, column)
            assert perm["letter"] == letter and perm["p3_column"] == column
            # a reason is given for exactly the statements that are withheld, and it names the letter
            assert (perm["why_sum"] is None) == sum_ok, (letter, column)
            assert (perm["why_writes"] is None) == bool(w), (letter, column)
            assert (perm["why_writes_cut"] is not None) == (0 < len(w) < 2), (letter, column)
            for why in (perm["why_sum"], perm["why_writes"], perm["why_writes_cut"]):
                assert why is None or why.startswith("letter %s: " % letter), why


def test_gate_cell_keeps_what_the_letter_permits_and_says_why_it_takes_the_rest():
    c, d, h = (an.cell_permission(x, "holds") for x in "CDH")
    # a sum cell: the limit and the forward flag of the aligned pair go together
    assert an.gate_cell(c, "t02_sum_n", ["at most 1.35x"], True) == (["at most 1.35x"], None, True, None)
    assert an.gate_cell(c, "t02_sum_n", [], False) == ([], None, False, None)
    assert an.gate_cell(c, "t02_sum_n", ["at most 1.35x"], None) == (["at most 1.35x"], None, None, None)
    assert an.gate_cell(d, "t02_sum_n", ["at most 1.35x"], True) == (None, d["why_sum"], None, d["why_sum"])
    assert an.gate_cell(d, "t02_sum_n", ["at most 1.35x"], None) == (None, d["why_sum"], None, None)      # compiled column
    # a write cell: no forward flag; the limits the letter does not name are cut, and the cut is said
    assert an.gate_cell(c, "t06_offset", ["at or above 1.5x"], None) == (None, c["why_writes"], None, None)
    assert an.gate_cell(d, "t06_offset", ["at or above 1.5x"], None) == (["at or above 1.5x"], None, None, None)
    assert an.gate_cell(d, "t05_fill_n", ["less than 1.5x"], None) == ([], d["why_writes_cut"], None, None)
    assert an.gate_cell(h, "t05_fill_n", ["less than 1.5x"], None) == ([], h["why_writes_cut"], None, None)
    assert an.gate_cell(h, "t05_fill_n", [], None) == ([], None, None, None)            # a straddling cell: nothing to cut
    a = an.cell_permission("A", "holds")
    assert an.gate_cell(a, "t05_fill_n", ["less than 1.5x"], None) == (["less than 1.5x"], None, None, None)
    # G and K state the writes under the word rule 11 gives for P3: none where P3 is undecided or not testable
    for letter in "GK":
        g = an.cell_permission(letter, "undecided")
        assert an.gate_cell(g, "t06_offset", ["at or above 1.5x"], None) == (None, g["why_writes"], None, None)
        assert "undecided" in g["why_writes"]


def _strad(loop, size, at, width=0.05):
    """over and noise that make the compiled and aligned pairs of one cell straddle `at` (the A/A pair stays quiet)."""
    keys = [(loop, size, "compiled"), (loop, size, "aligned")]
    return {k: at for k in keys}, {k: width for k in keys}


def _letter_entries(tmp, letter):
    """Entries for the letter, built so that the cells of every group are decidable: where the letter's row withholds a
    statement, some cell of that group would meet the limit (a second model holds where the first fails)."""
    d = model_entry
    if letter == "A":
        return [d(tmp)]
    if letter == "B":
        return [d(tmp, over={"t06_offset": 1.2})]
    if letter == "C":
        over, noise = _strad("t05_fill_n", "L1", 1.5)
        return [d(tmp, over=over, noise=noise)]
    if letter in "HIJ":
        over, noise = _strad("t02_sum_n", "L1", 1.35)
        if letter == "I":
            over["t06_offset"] = 1.2
        if letter == "J":
            o2, n2 = _strad("t05_fill_n", "L1", 1.5)
            over.update(o2)
            noise.update(n2)
        return [d(tmp, over=over, noise=noise)]
    over, noise = {"t02_sum_n": 1.6}, 0.002
    if letter == "E":
        over["t06_offset"] = 1.2
    elif letter == "F":
        over, noise = _strad("t05_fill_n", "L1", 1.5)
        over["t02_sum_n"] = 1.6
    elif letter == "G":
        over = {"t02_sum_n": 0.5}
    elif letter == "K":
        over = {("t02_sum_n", "L1"): 1.6, ("t02_sum_n", "L2"): 0.5}
    return [d(tmp, over=over, noise=noise), d(tmp, cpu=X86B)]


def test_each_letter_states_a_limit_or_a_forward_range_only_for_the_cells_its_row_permits():
    for letter in "ABCDEFGHIJK":
        with tempfile.TemporaryDirectory() as tmp:
            res = run_world(tmp, _letter_entries(tmp, letter))
        oc = res["analysis"]["outcome"]
        assert oc["letter"] == letter, (letter, oc["row"], oc["column"])
        sum_ok, writes = PERMITS[letter]
        assert oc["cell_permission"]["sum"] is sum_ok and oc["cell_permission"]["write_limits"] == writes
        assert oc["cell_permission"] == an.cell_permission(letter, oc["column"]) and oc["cell_permission"]["p3_column"] == oc["column"]
        lines = an.render_report(res).split("\n")
        block = _section(lines, "-- outcome")
        listing = _section(lines, "-- the four variable-bound loops")
        would_have_said = 0
        groups = set()
        for c in oc["cells"]:
            ungated = an.cell_limits(c["loop"], c["ci95"])
            line = [x for x in block if x.startswith("   %s %s %s %s: " % (c["cpu_model"], c["loop"], c["size"], c["column"]))]
            assert len(line) == 1, (letter, c)
            line = line[0]
            if c["loop"] == "t02_sum_n":
                groups.add("sum")
                if sum_ok:
                    assert c["limits"] == ungated and c["limits_withheld"] is None, (letter, c)
                    assert (c["inside_forward_range"] is not None) == (c["column"] == "aligned") and c["forward_range_withheld"] is None
                    assert ("limit: at most 1.35x (word %s)" % c["word"] in line) == bool(ungated)
                    assert ("inside the forward range: %s" % c["inside_forward_range"] in line) == (c["column"] == "aligned")
                else:
                    assert c["limits"] is None and c["limits_withheld"].startswith("letter %s: " % letter), (letter, c)
                    assert c["inside_forward_range"] is None
                    assert (c["forward_range_withheld"] == c["limits_withheld"]) == (c["column"] == "aligned")
                    would_have_said += bool(ungated)
                    # nothing of what the row does not permit is in the rendered line
                    for gone in ("at most 1.35x", "limit:", "inside the forward range: True", "inside the forward range: False"):
                        assert gone not in line, (letter, gone, line)
                    assert "no limit stated (letter %s: " % letter in line
                    assert ("inside the forward range: not stated (letter %s: " % letter in line) == (c["column"] == "aligned")
            else:
                groups.add("writes")
                assert c["inside_forward_range"] is None and c["forward_range_withheld"] is None and "inside the forward range" not in line
                if writes:
                    assert c["limits"] == [x for x in ungated if x in writes], (letter, c)
                    assert (c["limits_withheld"] is not None) == (c["limits"] != ungated), (letter, c)
                    for x in c["limits"]:
                        assert "limit: %s (word %s)" % (x, c["word"]) in line
                else:
                    assert c["limits"] is None and c["limits_withheld"].startswith("letter %s: " % letter), (letter, c)
                    would_have_said += bool(ungated)
                    for gone in ("at or above 1.5x", "less than 1.5x", "limit:"):
                        assert gone not in line, (letter, gone, line)
        assert groups == {"sum", "writes"}, (letter, groups)
        # the world would have produced a statement for a withheld group (so the check above can fail), except where nothing is withheld
        assert (would_have_said > 0) == (letter not in "AB"), (letter, would_have_said)
        # the standing listing of the four variable-bound loops is made under every letter, with the forward-range flag
        listed = 0
        for r in res["analysis"]["forward_listing"]:
            if r["none_decidable"]:
                assert "   %s %s: no decidable cell" % (r["cpu_model"], r["loop"]) in listing, (letter, r)
            for cc in r["decidable_aligned_cells"]:
                listed += 1
                assert any(x.startswith("   %s %s %s: " % (r["cpu_model"], r["loop"], cc["size"]))
                           and x.endswith("; inside the forward range: %s" % cc["inside_forward_range"]) for x in listing), (letter, r)
        assert listed >= 4, (letter, listed)


def test_a_limit_line_names_the_loops_word_and_a_cut_limit_says_so():
    words = ("kept", "lost", "kept", "narrower", "kept", "lost")           # t05_fill_n kept here, lost in the plan
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, words=words)])
    oc = res["analysis"]["outcome"]
    assert {(c["loop"], c["word"]) for c in oc["cells"]} >= {("t02_sum_n", "lost"), ("t06_offset", "lost"), ("t05_fill_n", "kept")}
    block = _section(an.render_report(res).split("\n"), "-- outcome")
    for c in oc["cells"]:
        if c["limits"]:
            line = [x for x in block if x.startswith("   %s %s %s %s: " % (c["cpu_model"], c["loop"], c["size"], c["column"]))][0]
            assert "; limit: %s (word %s)" % (", ".join(c["limits"]), c["word"]) in line, line
    assert any("t05_fill_n L1 aligned" in x and "(word kept)" in x for x in block)
    # a limit the letter does not name is cut and the line says why (letter D: the writes are given as "at or above 1.5x" only)
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, _letter_entries(tmp, "D"))
    assert res["analysis"]["outcome"]["letter"] == "D"
    cut = an.gate_cell(an.cell_permission("D", "holds"), "t05_fill_n", ["less than 1.5x"], None)
    assert cut[0] == [] and cut[1].startswith("letter D: only 'at or above 1.5x'")
    cell = {"cpu_model": "m", "loop": "t05_fill_n", "size": "L1", "column": "aligned", "word": "lost", "ratio": 1.2, "ci95": [1.19, 1.21],
            "jobs": 3, "limits": cut[0], "limits_withheld": cut[1], "inside_forward_range": None, "forward_range_withheld": None}
    an_ = copy.deepcopy(res["analysis"])
    an_["outcome"]["cells"] = [cell]
    text = "\n".join(an.render_analysis(an_, "x"))
    assert "; no limit stated; a further limit is withheld (letter D: only 'at or above 1.5x' is stated for a write cell)" in text


def test_the_forward_range_is_printed_with_its_rule():
    assert an.forward_rule_text({"point": 1.05, "floor": 3.0, "multiplier": 2.5}) == (
        "pooled aligned ratio at most 1.05 and interval upper end at most 1 + max(3%, 2.5 x A/A half-width); no lower bound")
    res = default_result()
    rule = res["analysis"]["forward_rule"]
    assert (rule["point"], rule["floor"], rule["multiplier"]) == (1.02, 2.0, 2.0)
    want = ("   inside the forward range (rule 6): pooled aligned ratio at most 1.02 and interval upper end at most "
            "1 + max(2%, 2 x A/A half-width); no lower bound")
    assert rule["text"] == want.strip().split(": ", 1)[1]
    lines = an.render_report(res).split("\n")
    block, listing = _section(lines, "-- outcome"), _section(lines, "-- the four variable-bound loops")
    for part in (block, listing):
        assert want in part and sum("inside the forward range: " in x for x in part) >= 1
        # the rule comes before the first line that uses it
        assert part.index(want) < min(i for i, x in enumerate(part) if "inside the forward range: " in x)
    assert lines.count(want) == 2
    # with no decidable cell there is nothing to explain
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [])
    assert "inside the forward range (rule 6)" not in an.render_report(res)


def test_a_model_marked_control_failed_is_marked_in_the_standing_listing():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, over={"t01_sum_size": 1.3}), model_entry(tmp, cpu=X86B)])
    why = model(res, X86)["pred"]["control_failed"]
    assert why and model(res, X86B)["pred"]["control_failed"] is None
    rows = res["analysis"]["forward_listing"]
    assert {r["control_failed"] for r in rows if r["cpu_model"] == X86} == {why}
    assert {r["control_failed"] for r in rows if r["cpu_model"] == X86B} == {None}
    assert all(r["decidable_aligned_cells"] for r in rows if r["cpu_model"] == X86 and r["loop"] != "t01_sum_size")     # still listed
    listing = _section(an.render_report(res).split("\n"), "-- the four variable-bound loops")
    mark = "   %s: MARKED control failed: %s" % (X86, why)
    assert listing.count(mark) == 1 and not any("MARKED" in x and X86B in x for x in listing)
    first = min(i for i, x in enumerate(listing) if x.startswith("   %s t0" % X86))
    assert listing.index(mark) < first
    # the mark is the one the model block carries
    assert "   MARKED control failed: %s" % why in an.render_report(res)
    # a model that is not marked has none
    assert not any("MARKED" in x for x in _section(an.render_report(default_result()).split("\n"), "-- the four variable-bound loops"))

# ---------------------------------------------------------------- the same job stored twice, a missing file, a folder name

def _store_copy(tmp, e, dst, src_job="job-0", change=None):
    """Writes a second copy of one stored file below the entry's folder (a different sub-folder); `change(doc)` edits the
    copy so that it is no longer byte-identical. Returns the repo-relative path of the copy."""
    with open(os.path.join(tmp, e["folder"], src_job, sw.RESULT_NAME), "rb") as f:
        raw = f.read()
    if change:
        doc = json.loads(raw.decode("utf-8"))
        change(doc)
        raw = json.dumps(doc, indent=1).encode("utf-8")
    p = os.path.join(tmp, e["folder"], dst)
    os.makedirs(p, exist_ok=True)
    with open(os.path.join(p, sw.RESULT_NAME), "wb") as f:
        f.write(raw)
    return e["folder"] + "/" + dst + "/" + sw.RESULT_NAME


def _nudge_one_sample(doc):
    doc["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["compiled"]["a_ns"][0] *= 1.01


def test_a_byte_identical_copy_of_one_job_is_a_stop_naming_both_paths_and_the_distinct_count():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        copy_rel = _store_copy(tmp, e, "zcopy")
        first = e["folder"] + "/job-0/" + sw.RESULT_NAME
        counted = dict(e, jobs_started=4, jobs_returned=4)        # the manifest counts both files, so the count stop is quiet
        text = stop_text([counted], tmp)
    assert ("run %s: 4 %s files but 3 distinct jobs: %s is a byte-identical copy of %s" % (
        e["run_id"], sw.RESULT_NAME, copy_rel, first)) in text, text
    assert "manifest says" not in text                        # only the copy stop: the count of files agrees with the manifest
    assert text.count("byte-identical") == 1


def test_an_honest_five_job_run_with_a_downloaded_twice_copy_stops_with_six_files_but_five_distinct_jobs():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp, n=5)
        assert len(run_world(tmp, [e])["analysis"]["models"]) == 1            # the run alone is fine
        copy_rel = _store_copy(tmp, e, "zcopy", src_job="job-3")
        text = stop_text([e], tmp)                                            # the manifest still says five
    first = e["folder"] + "/job-3/" + sw.RESULT_NAME
    assert "6 %s files but 5 distinct jobs: %s is a byte-identical copy of %s" % (sw.RESULT_NAME, copy_rel, first) in text, text
    assert "manifest says 5" in text                           # the plan's own count stop shows as well


def test_a_manifest_that_counts_files_cannot_hide_a_job_that_never_returned():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)                                   # three jobs came back; a fourth was started and lost
        _store_copy(tmp, e, "zcopy")
        # four files on disk and 'four returned' in the manifest: the file count agrees, the distinct jobs (three) do not
        text = stop_text([dict(e, jobs_started=4, jobs_returned=4)], tmp)
        assert "4 %s files but 3 distinct jobs" % sw.RESULT_NAME in text
        # the same run described correctly (three returned, one lost) is stopped by the copy and by the count, not accepted
        both = stop_text([dict(e, jobs_started=4, jobs_returned=3, not_returned=[{"job": "4", "reason": "cancelled"}])], tmp)
        assert "byte-identical copy" in both and "manifest says 3" in both


def test_a_copy_in_a_run_marked_not_in_the_plan_stops_too_and_main_exits_with_3():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp, clause="x86-64 run 1")
        other = model_entry(tmp, cpu=X86B, clause=an.NOT_IN_PLAN, reason="a run outside the plan")
        copy_rel = _store_copy(tmp, other, "zcopy")
        man, out = os.path.join(tmp, "runs.json"), os.path.join(tmp, "results.json")
        with open(man, "w", encoding="utf-8") as f:
            json.dump(manifest_of([e, dict(other, jobs_started=4, jobs_returned=4)]), f)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = an.main(["--manifest", man, "--base", tmp, "--out", out])
    assert code == 3 and not os.path.exists(out)
    assert copy_rel in buf.getvalue() and "byte-identical copy" in buf.getvalue()


def test_a_second_file_of_the_same_job_with_other_content_is_a_stop_naming_both_paths():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        copy_rel = _store_copy(tmp, e, "zcopy", change=_nudge_one_sample)
        text = stop_text([dict(e, jobs_started=4, jobs_returned=4)], tmp)
    first = e["folder"] + "/job-0/" + sw.RESULT_NAME
    assert copy_rel in text and first in text and "with other content" in text, text
    assert "manifest says" not in text                         # the count was honest about four files


def test_the_count_stop_and_the_copy_stop_both_show_when_the_manifest_count_is_honest():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        copy1 = _store_copy(tmp, e, "zcopy")
        text = stop_text([e], tmp)                             # three jobs returned, four files
        assert "4 " + sw.RESULT_NAME in text and "manifest says 3" in text
        assert "byte-identical copy" in text and copy1 in text
        other = model_entry(tmp, cpu=X86B)
        copy2 = _store_copy(tmp, other, "zcopy", change=_nudge_one_sample)
        both = stop_text([e, other], tmp)
        assert both.count("manifest says 3") == 2 and "with other content" in both and copy2 in both
        assert both.count("byte-identical copy") == 1


def test_jobs_with_the_same_name_in_two_runs_are_not_copies():
    with tempfile.TemporaryDirectory() as tmp:
        first = model_entry(tmp)
        second = model_entry(tmp)                              # another run id; its jobs carry the same names 1, 2, 3
        res = run_world(tmp, [first, second])
    assert model(res, X86)["jobs"] == 6 and res["analysis"]["set_aside"] == []


def _run_lines(text):
    return [x for x in text.splitlines() if x.startswith("[run] ")]


def test_the_run_line_prints_the_pooled_job_count_beside_the_manifest_count():
    with tempfile.TemporaryDirectory() as tmp:
        real = model_entry(tmp)
        smoke_doc = make_doc(smoke=True, run_id=real["run_id"], job="9")
        p = os.path.join(tmp, real["folder"], "job-9")
        os.makedirs(p)
        with open(os.path.join(p, sw.RESULT_NAME), "w", encoding="utf-8") as f:
            json.dump(smoke_doc, f)
        real["jobs_started"] = real["jobs_returned"] = 4           # the smoke file counts as a file of the run
        code_test = model_entry(tmp, cpu=X86B, smoke=True, n=2, clause="code test", cls="test")
        small = model_entry(tmp, cpu=X86B, n=2, clause="x86-64 run 2")
        res = run_world(tmp, [real, code_test, small])
        lines = _run_lines(an.render_report(res))
    assert len(lines) == 3
    assert "jobs 4/4 (3 pooled)" in lines[0] and "folder %s" % real["folder"] in lines[0]    # the smoke file is read, not pooled
    assert "jobs 2/2 (0 pooled)" in lines[1]                                                   # a test entry pools nothing
    assert "jobs 2/2 (2 pooled)" in lines[2]                                                   # fewer than 3 jobs: listed in the pool, not read
    assert [x["pooled"] for x in res["entry_files"]] == [3, 0, 2] and [x["files"] for x in res["entry_files"]] == [4, 2, 2]
    assert [x["run_id"] for x in res["entry_files"]] == [e["run_id"] for e in (real, code_test, small)]


def test_a_folder_name_with_pattern_characters_is_used_literally():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp, name="run[1]")                    # glob would read [1] as a character class
        head = {"kind": "forwardt-partial", "cells_expected": 12, "run": {"id": e["run_id"], "job": "7", "runner": {"cpu_model": X86}}}
        p = os.path.join(tmp, e["folder"], "job-7")
        os.makedirs(p)
        with open(os.path.join(p, sw.PARTIAL_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps(head) + "\n" + json.dumps({"stopped": {"reason": "the limit", "at": "t02_sum_n.L1"}}) + "\n")
        res = run_world(tmp, [e])
        # a sibling folder that the unescaped pattern would match is not read
        sib = os.path.join(tmp, "results", "run1", "job-0")
        os.makedirs(sib)
        with open(os.path.join(sib, sw.RESULT_NAME), "w", encoding="utf-8") as f:
            json.dump(make_doc(run_id="39888888888"), f)
        again = run_world(tmp, [e])
    assert e["folder"].endswith("run[1]") and model(res, X86)["jobs"] == 3 and model(again, X86)["jobs"] == 3
    assert len(res["analysis"]["partial"]) == 1


def test_one_result_file_removed_from_a_three_job_run_stops_the_analysis():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        os.remove(os.path.join(tmp, e["folder"], "job-1", sw.RESULT_NAME))
        text = stop_text([e], tmp)
        assert "2 " + sw.RESULT_NAME in text and "manifest says 3" in text
        # the same run with an honest count of two is not a stop
        res = run_world(tmp, [dict(e, jobs_started=3, jobs_returned=2, not_returned=[{"job": "2", "reason": "cancelled"}])])
        assert model(res, X86)["jobs"] == 2


def _four_docs(rid):
    return [make_doc(run_id=rid, job=str(i + 1)) for i in range(4)]


def _recs(docs):
    return [{"rel": "results/run-x/job-%d/%s" % (i, sw.RESULT_NAME), "doc": d} for i, d in enumerate(docs)]


def test_the_comparison_between_files_finds_a_deviating_file_at_every_position():
    ctx = an.make_ctx()
    assert an.cross_problems(_recs(_four_docs("39000000777")), ctx) == []
    for idx in (1, 2, 3):                                      # second, third and last of four
        docs = _four_docs("39000000777")
        docs[idx]["loops"]["t01_sum_size"]["builds"]["fast"]["binary_sha256"] = "f" * 64
        recs = _recs(docs)
        out = an.cross_problems(recs, ctx)
        assert len(out) == 1, (idx, out)
        code, text, rel = out[0]
        assert code == "binary_hash" and rel == recs[idx]["rel"] and recs[0]["rel"] in text and recs[idx]["rel"] in text
        # the same through the model's file problems: the file is named, no other file is
        problems = an.model_problems(recs, ctx)
        named = [p["file"] for p in problems if p["code"] == "binary_hash"]
        assert named == [recs[idx]["rel"]]


def test_the_comparison_names_each_deviating_file_when_several_deviate():
    ctx = an.make_ctx()
    docs = _four_docs("39000000778")
    docs[1]["run"]["commit"] = "1" * 40
    docs[3]["loops"]["t03_scale_size"]["builds"]["none"]["traps"] = 5
    recs = _recs(docs)
    out = an.cross_problems(recs, ctx)
    assert sorted((c, r) for c, _, r in out) == sorted([("commit", recs[1]["rel"]), ("traps", recs[3]["rel"])]), out


def test_verify_after_regenerating_results_with_one_edited_sample_finds_one_file_with_problems():
    with tempfile.TemporaryDirectory() as tmp:
        e, man, out = _stored_world(tmp)
        path = os.path.join(tmp, e["folder"], "job-1", sw.RESULT_NAME)
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        pr = doc["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"]["compiled"]
        pr["a_ns"] = [x * 2.0 for x in pr["a_ns"]]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        regenerated = os.path.join(tmp, "regenerated.json")
        with contextlib.redirect_stdout(io.StringIO()):
            an.main(["--manifest", man, "--base", tmp, "--out", regenerated])
        manifest = an.read_manifest(man)
        code, lines = an.verify(manifest, tmp, regenerated, file_resamples=100)
        assert code == 1, lines
        assert any("verified 3 file(s): 1 with problems" in x for x in lines), lines
        assert any("not what the samples give" in x and "job-1" in x for x in lines), lines
        assert any("matches the recomputation" in x for x in lines), lines

# ---------------------------------------------------------------- small things: the code list, the notes, the listed files

def test_the_hashed_code_files_are_the_sweeps_one_list_and_there_is_no_dead_helper():
    assert an.CODE_FILES is sw.CODE_FILES
    assert set(an.CODE_FILES) == set(sw.code_sha256())
    assert set(default_result()["code_sha256"]) == set(an.CODE_FILES)
    assert not hasattr(an, "_hot")


def _cell_line(text, loop, size):
    """The report line of one cell: the first line starting with the size that follows the loop's own line."""
    lines = text.splitlines()
    i = next(k for k, x in enumerate(lines) if x.startswith("   %s: word" % loop))
    return next(x for x in lines[i + 1:i + 4] if x.strip().startswith(size + " n="))


def test_the_contains_one_note_names_each_of_the_four_columns_whose_interval_contains_one():
    # t02 has no cost and wide noise: every column contains 1.00; t05 costs 2x, so only its A/A can contain 1.00. Whether the
    # A/A interval of one made-up draw contains 1.00 is chance (the run ids that seed the draws come from a counter that every
    # earlier test advances), so the t05 part asks the report to agree with the stored flag in both directions
    over = {"t02_sum_n": 1.0}
    noise = {"t02_sum_n": 0.03}
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, over=over, noise=noise)])
    text = an.render_report(res)
    cells = model(res, X86)["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]
    assert all(cells[c]["contains_one"] for c in ("compiled", "aligned", "aa", "novec"))
    line = _cell_line(text, "t02_sum_n", "L1")
    for col in ("compiled", "aligned", "aa", "novec"):
        assert "%s: interval contains 1.00" % col in line, (col, line)
    only_aa = _cell_line(text, "t05_fill_n", "L1")
    t05 = model(res, X86)["loops"]["t05_fill_n"]["cells"]["L1"]["pairs"]
    for col in ("compiled", "aligned", "novec"):
        assert not t05[col]["contains_one"]
        assert "%s: interval contains 1.00" % col not in only_aa, (col, only_aa)
    assert ("aa: interval contains 1.00" in only_aa) == bool(t05["aa"]["contains_one"]), (t05["aa"], only_aa)
    # a column the loop does not have (t01 has no novec pair) is not named
    assert "novec: interval" not in _cell_line(text, "t01_sum_size", "L1")


def test_a_set_aside_smoke_file_is_listed_with_its_repetitions_and_stored_plan_hash():
    with tempfile.TemporaryDirectory() as tmp:
        real = model_entry(tmp)
        smoke = model_entry(tmp, cpu=X86B, smoke=True, n=2, clause="code test", cls="test")
        nonsmoke = model_entry(tmp, cpu=N2, arm=True, n=1, clause="code test", cls="test")
        with open(os.path.join(tmp, smoke["folder"], "job-0", sw.RESULT_NAME), encoding="utf-8") as f:
            sdoc = json.load(f)
        res = run_world(tmp, [real, smoke, nonsmoke])
    lines = [x for x in an.render_report(res).splitlines() if x.startswith("[set aside]")]
    smoke_lines = [x for x in lines if ": smoke file" in x]
    assert len(smoke_lines) == 2 and len(lines) == 3
    for x in smoke_lines:
        assert "repetitions per side %s" % sdoc["reps_per_side"] in x and "stored plan hash %s" % sdoc["plan_sha256"] in x, x
    other = [x for x in lines if ": smoke file" not in x]
    assert len(other) == 1 and "repetitions per side" not in other[0] and "stored plan hash" not in other[0]


def _write_partial(tmp, e, job, run_id, with_run=True):
    head = {"kind": "forwardt-partial", "cells_expected": 12}
    if with_run:
        head["run"] = {"id": run_id, "job": job, "runner": {"cpu_model": X86}}
    p = os.path.join(tmp, e["folder"], "job-" + job)
    os.makedirs(p)
    with open(os.path.join(p, sw.PARTIAL_NAME), "w", encoding="utf-8") as f:
        f.write(json.dumps(head) + "\n" + json.dumps({"stopped": {"reason": "the 45-minute limit", "at": "t02_sum_n.L1"}}) + "\n")


def test_a_partial_file_is_listed_with_its_run_id_and_a_note_when_the_manifest_does_not_list_that_run_id():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        _write_partial(tmp, e, "7", e["run_id"])
        _write_partial(tmp, e, "8", "39777777777")
        _write_partial(tmp, e, "9", None, with_run=False)
        res = run_world(tmp, [e])                              # a note, not a stop
    by_job = {p["job"]: p for p in res["analysis"]["partial"]}
    assert by_job["7"]["run_id_listed"] is True and by_job["8"]["run_id_listed"] is False and by_job["None"]["run_id_listed"] is False
    lines = {x.split(":")[0]: x for x in an.render_report(res).splitlines() if x.startswith("[partial]")}
    one = [x for k, x in lines.items() if "job-7" in k][0]
    two = [x for k, x in lines.items() if "job-8" in k][0]
    three = [x for k, x in lines.items() if "job-9" in k][0]
    assert "run id %s" % e["run_id"] in one and "does not list" not in one
    assert "run id 39777777777" in two and "the manifest does not list this run id" in two
    # a file with no run id has none to look up: the line says which run's folder it lies in and does not call it unlisted
    assert "no run id stored in the file" in three and "it lies in the folder of run %s" % e["run_id"] in three
    assert "does not list" not in three
    for x in (one, two, three):
        assert "not pooled" in x and "45-minute limit" in x and "of 12 cells" in x
    assert model(res, X86)["jobs"] == 3


def test_an_empty_partial_file_prints_no_cell_recorded_and_a_headerless_one_the_cells_it_has():
    with tempfile.TemporaryDirectory() as tmp:
        e = model_entry(tmp)
        p = os.path.join(tmp, e["folder"], "job-7")
        os.makedirs(p)
        with open(os.path.join(p, sw.PARTIAL_NAME), "w", encoding="utf-8"):
            pass                                               # a zero-byte file: the job was killed before it wrote anything
        p2 = os.path.join(tmp, e["folder"], "job-8")
        os.makedirs(p2)
        with open(os.path.join(p2, sw.PARTIAL_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps({"cell": {"loop": "t01_sum_size"}}) + "\n")      # no header line, one cell
        p3 = os.path.join(tmp, e["folder"], "job-9")
        os.makedirs(p3)
        with open(os.path.join(p3, sw.PARTIAL_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps({"cell": {"loop": "t01_sum_size"}}) + "\n" + json.dumps({"cell": {"loop": "t02_sum_n"}}) + "\n")
        res = run_world(tmp, [e])
    lines = {x.split(":")[0]: x for x in an.render_report(res).splitlines() if x.startswith("[partial]")}
    empty, one, two = [[x for k, x in lines.items() if "job-%d" % j in k][0] for j in (7, 8, 9)]
    assert ": no cell recorded; " in empty and "None" not in empty
    assert ": 1 cell recorded (the number expected is not stored); " in one and "None" not in one
    assert ": 2 cells recorded (the number expected is not stored); " in two
    for x in (empty, one, two):
        assert "no run id stored in the file; it lies in the folder of run %s" % e["run_id"] in x and "does not list" not in x
        assert "no 'stopped' line" in x and "not pooled" in x


def test_the_n2_sum_line_of_a_model_below_the_minimum_says_it_was_not_read_and_gives_no_word_or_ratio():
    for n, jobs in ((2, "2 jobs"), (1, "1 job")):
        with tempfile.TemporaryDirectory() as tmp:
            res = run_world(tmp, [model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2, n=n)])
        m = model(res, N2)
        assert m["jobs"] == n and m["pooled"] is True and m["read"] is False
        (rep,) = res["analysis"]["reported_n2_t02"]
        assert rep == {"cpu_model": N2, "jobs": n, "read": False, "word": None, "cells": None}
        lines = [x for x in an.render_report(res).splitlines() if x.startswith("   t02_sum_n on ")]
        assert lines == ["   t02_sum_n on %s: not read (%s, fewer than the minimum of 3)" % (N2, jobs)], lines
    with tempfile.TemporaryDirectory() as tmp:                 # at the minimum the line is the one with the word and the ratios
        res = run_world(tmp, [model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2, n=3)])
    (rep,) = res["analysis"]["reported_n2_t02"]
    assert rep["read"] is True and rep["word"] == "lost" and rep["cells"]["L1"]["compiled"] > 1.1
    lines = [x for x in an.render_report(res).splitlines() if x.startswith("   t02_sum_n on ")]
    assert len(lines) == 1 and "(word lost, reported without a band, 3 jobs)" in lines[0] and "not read" not in lines[0]


def test_a_neoverse_n2_model_with_a_file_problem_is_not_pooled_and_has_no_sum_line_at_all():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2, n=3, mutate=PLANTS["reps"])])
    m = model(res, N2)
    assert m["problems"] and m["pooled"] is False and m["read"] is False
    assert res["analysis"]["reported_n2_t02"] == []                      # neither read nor listed as not read
    assert [x for x in an.render_report(res).splitlines() if x.startswith("   t02_sum_n on ")] == []
    with tempfile.TemporaryDirectory() as tmp:                           # a clean model of the same CPU is listed
        res = run_world(tmp, [model_entry(tmp, words=N2_WORDS, arm=True, cpu=N2, n=3)])
    assert [r["cpu_model"] for r in res["analysis"]["reported_n2_t02"]] == [N2]


NOTE_ONE = "interval contains 1.00 (indistinguishable from no cost at this noise)"


def test_the_note_that_an_interval_contains_one_is_printed_on_the_outcome_and_listing_lines_too():
    with tempfile.TemporaryDirectory() as tmp:
        # the sum has no cost in this world (an interval around 1.00), the fill has a large one (an interval far from it)
        res = run_world(tmp, [model_entry(tmp, over={"t02_sum_n": 1.0, "t05_fill_n": 3.0, "t06_offset": 3.0})])
    text = an.render_report(res).splitlines()
    cells = res["analysis"]["outcome"]["cells"]
    listing = [(r, c) for r in res["analysis"]["forward_listing"] for c in r["decidable_aligned_cells"]]
    assert cells and listing
    seen = {True: 0, False: 0}
    for c in cells:
        prefix = "   %s %s %s %s: " % (c["cpu_model"], c["loop"], c["size"], c["column"])
        line = [x for x in text if x.startswith(prefix) and "(" in x][0]
        spans = c["ci95"][0] <= 1.0 <= c["ci95"][1]
        assert (NOTE_ONE in line) == spans, (line, c["ci95"])
        assert line.count(NOTE_ONE) <= 1
        seen[spans] += 1
    for r, c in listing:
        prefix = "   %s %s %s: " % (r["cpu_model"], r["loop"], c["size"])
        line = [x for x in text if x.startswith(prefix)][0]
        spans = c["ci95"][0] <= 1.0 <= c["ci95"][1]
        assert (NOTE_ONE in line) == spans, (line, c["ci95"])
        seen[spans] += 1
    assert seen[True] >= 2 and seen[False] >= 2, seen           # both kinds of line were checked, on both sections
    # the per-model cell lines still carry the note, once per column that spans 1.00, as before
    assert any(x.startswith("      L1 n=") and NOTE_ONE in x for x in text)


def test_an_interval_that_ends_exactly_at_one_contains_it_as_the_stored_flag_says():
    for ci in ([0.9, 1.0], [1.0, 1.1], [1.0, 1.0], (0.5, 1.5)):
        assert an._spans_one(ci), ci
    for ci in ([1.0001, 1.1], [0.9, 0.9999], (1.2, 1.3), (0.7, 0.8)):
        assert not an._spans_one(ci), ci
    res = default_result()
    cells = res["analysis"]["outcome"]["cells"]
    assert cells
    c = cells[0]
    prefix = "   %s %s %s %s: " % (c["cpu_model"], c["loop"], c["size"], c["column"])
    for ci, shown in (([1.0, 1.2], True), ([0.8, 1.0], True), ([1.0001, 1.2], False), ([0.8, 0.9999], False)):
        c["ci95"] = list(ci)
        line = [x for x in an.render_report(res).splitlines() if x.startswith(prefix) and "(" in x][0]
        assert (NOTE_ONE in line) == shown, (ci, line)


def test_the_p0_lines_of_a_target_with_no_model_say_so_instead_of_ending_in_a_colon():
    with tempfile.TemporaryDirectory() as tmp:
        res = run_world(tmp, [model_entry(tmp)])                # an x86-64 model only: the Neoverse-N2 target has no model
    text = an.render_report(res).splitlines()
    heads = [i for i, x in enumerate(text) if x.startswith("-- Neoverse-N2 (models: none)")]
    assert len(heads) == 1, [x for x in text if x.startswith("-- ")]
    p0 = []
    for x in text[heads[0] + 1:]:
        if x.startswith("-- "):
            break
        if x.startswith("   P0."):
            p0.append(x)
    assert len(p0) == len(LOOPS)
    for x in p0:
        assert x.endswith("): no model of this target"), x
    # a target with a model keeps its list of models after the colon
    own = [x for x in text if x.startswith("   P0.t01_sum_size: ") and "no model of this target" not in x]
    assert own and all(not x.rstrip().endswith(":") for x in text), own


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items(), key=lambda kv: kv[1].__code__.co_firstlineno if callable(kv[1]) and hasattr(kv[1], "__code__") else 0):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception:
                failed += 1
                traceback.print_exc()
    sys.exit(1 if failed else 0)
