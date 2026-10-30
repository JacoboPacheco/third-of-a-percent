"""scripts/check.py knows the forwardt/ piece: the step that runs forwardt/analyze.py --verify, the guard on the plan's hash, and
the rule that every stored forwardt.json lies in a folder forwardt/runs.json names.

What state the repository is in, and what these tests pin: forwardt/PLAN.md is in the tree, forwardt/runs.json lists five runs
(two code tests and three measurement runs), 18 forwardt.json files and forwardt/results.json are stored, and the step must PASS
there; the committed state is pinned below (the entries, the 18 files, the jobs per CPU model, the plan hash, the recomputation)
and each pin is shown to fail when a stored number or the manifest is changed. An empty manifest (nothing to verify, which
passes) is still a legal state and is run on scratch trees. The functions are also run on small scratch copies of the repository
(check.REPO is pointed at them for the length of one call) to show what makes them fail: a plan with one changed word, a stored file made under another plan, a stored file in a
folder the manifest does not name, a results.json that is not what a fresh analysis gives, a missing or unreadable one, and a
missing analysis script, plan or manifest. The analysis's own rules (the stops of the plan's "Runs: Accounting", the recomputation
of every ratio) are tested in tests/test_forwardt_analyze.py and are not repeated here.

Plain functions and no pytest: scripts/check.py's built-in runner runs them without it."""
import ast
import contextlib
import copy
import glob
import hashlib
import importlib
import importlib.util
import inspect
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
check = importlib.import_module("check")

# The plan's hash, written here a third time (scripts/check.py and forwardt/analyze.py hold it too).
PLAN_SHA256 = "91a7c6a08a1307a0f04209caeea44f887418ceb5368759814bfaee79cd0a986f"
EMPTY_MANIFEST = {"schema": 1, "entries": []}


def lf_sha(path):
    """Written again here, not imported from check.py: sha256 with CRLF read as LF."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def run(fn, *args, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args, **kw)
    return rc, buf.getvalue()


@contextlib.contextmanager
def repo_at(path):
    """check.REPO pointed at a scratch copy for the length of one block."""
    real = check.REPO
    check.REPO = path
    try:
        yield
    finally:
        check.REPO = real


def put(root, rel, text=None, data=None):
    path = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if data is not None:
        with open(path, "wb") as f:
            f.write(data)
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return path


def scratch(tmp, analysis=True, plan=True, manifest=True, manifest_doc=None):
    """A small repository: the plan, the analysis and what it imports, and the manifest (empty unless manifest_doc is given).
    The plan is copied byte for byte."""
    if plan:
        shutil.copyfile(os.path.join(REPO, "forwardt", "PLAN.md"), put(tmp, "forwardt/PLAN.md", text=""))
    if analysis:
        for rel in ("forwardt/analyze.py", "forwardt/sweep.py"):
            shutil.copyfile(os.path.join(REPO, *rel.split("/")), put(tmp, rel, text=""))
    for name in sorted(glob.glob(os.path.join(REPO, "harness", "*.py"))) + [os.path.join(REPO, "harness", "criteria-v3.json")]:
        shutil.copyfile(name, put(tmp, "harness/" + os.path.basename(name), text=""))
    shutil.copyfile(os.path.join(REPO, "kernels", "common.hpp"), put(tmp, "kernels/common.hpp", text=""))
    if manifest:
        put(tmp, "forwardt/runs.json", text=json.dumps(manifest_doc or EMPTY_MANIFEST, indent=1) + "\n")
    return tmp


def entry(folder, run_id="39000000001"):
    return {"run_id": run_id, "runner": "ubuntu-24.04", "head_sha": "a" * 40, "created_at": "2026-10-22T14:03:11Z",
            "class": "measurement", "clause": "x86-64 run 1", "jobs_started": 1, "jobs_returned": 1, "not_returned": [],
            "folder": folder}


def write_results(tmp):
    """forwardt/results.json as the analysis writes it for the scratch repository's manifest."""
    r = subprocess.run([sys.executable, os.path.join(tmp, "forwardt", "analyze.py")], capture_output=True, text=True, errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
    return os.path.join(tmp, "forwardt", "results.json")


# ---------------------------------------------------------------- the tree as it stands

def test_the_step_passes_on_the_tree_as_it_stands():
    rc, out = run(check.check_forwardt)
    assert rc is True, out
    assert "FAIL" not in out
    assert "ok   forwardt/PLAN.md (sha256 91a7c6a08a13)" in out, out
    # the committed manifest lists runs, so the analysis recomputed results.json and compared it (about a minute and a half)
    assert "results.json matches the recomputation" in out and "nothing to verify" not in out, out
    assert "ok   all 18 stored forwardt.json file(s) lie in a folder forwardt/runs.json names" in out, out


def test_the_three_records_of_the_plan_hash_agree_with_the_plan():
    want = lf_sha(os.path.join(REPO, "forwardt", "PLAN.md"))
    assert want == PLAN_SHA256 == check.FORWARDT_PLAN_SHA256, "forwardt/PLAN.md differs from the plan the hash records"
    with open(os.path.join(REPO, "forwardt", "analyze.py"), encoding="utf-8") as f:
        m = re.search(r'^FIRST_COMMIT_PLAN_SHA256 = "([0-9a-f]{64})"', f.read(), re.M)
    assert m and m.group(1) == want
    assert check.forwardt_recorded_in_analysis() == want


def test_the_header_of_check_py_describes_the_step():
    doc = check.__doc__
    assert "forwardt/PLAN.md" in doc and "forwardt/analyze.py --verify" in doc and "forwardt/runs.json" in doc
    text = " ".join(doc.split())
    assert "a manifest that lists no run has nothing to verify and passes" in text
    assert "forwardt/results.json is stored" in text
    assert "before the planned runs" not in text and "manifest is empty" not in text   # the committed manifest lists runs


def test_main_runs_the_forwardt_step_after_the_d_sweep_step_and_before_the_next_one():
    src = inspect.getsource(check.main)
    a, b, c = src.index("ok &= check_dsweep()"), src.index("ok &= check_forwardt()"), src.index('print("== PGO column')
    assert a < b < c
    assert "forwardt/analyze.py --verify" in src[a:b]
    # every file the step names is in the repository
    body = inspect.getsource(check.check_forwardt)
    for rel in (check.FORWARDT_PLAN, check.FORWARDT_ANALYSIS, check.FORWARDT_MANIFEST):
        assert os.path.exists(os.path.join(REPO, *rel.split("/"))), rel
    assert "analyze, \"--verify\"" in body and "check_forwardt_plan" in body and "check_forwardt_named" in body


# ---------------------------------------------------------------- the plan hash

def test_the_plan_guard_passes_a_copy_with_either_line_ending_and_fails_one_changed_word():
    text = open(os.path.join(REPO, "forwardt", "PLAN.md"), "rb").read()
    lf = text.replace(bytes([13, 10]), bytes([10]))
    with tempfile.TemporaryDirectory() as tmp:
        same = put(tmp, "same.md", data=lf)
        crlf = put(tmp, "crlf.md", data=lf.replace(bytes([10]), bytes([13, 10])))
        edited = put(tmp, "edited.md", data=lf.replace(b"the plan", b"The plan", 1))
        assert edited and lf.replace(b"the plan", b"The plan", 1) != lf, "the planted edit changed nothing"
        for path, want in ((same, True), (crlf, True), (edited, False)):
            rc, out = run(check.check_forwardt_plan, [], [], plan=path)
            assert rc is want, (path, out)
            if not want:
                assert "the plan was edited" in out and out.count("FAIL") == 2, out   # the record here and the record in analyze.py


def test_stored_files_must_carry_the_plans_hash_and_a_result_file_also_the_first_commit_hash():
    with tempfile.TemporaryDirectory() as tmp:
        good = put(tmp, "good/forwardt.json", text=json.dumps({"plan_sha256": PLAN_SHA256}))
        result = put(tmp, "forwardt/results.json", text=json.dumps({"plan_sha256": PLAN_SHA256, "first_commit_plan_sha256": PLAN_SHA256}))
        rc, out = run(check.check_forwardt_plan, [good], [result])
        assert rc is True and "all 1 forwardt.json and 1 result file(s)" in out, out
        # a file produced under another plan
        other = put(tmp, "other/forwardt.json", text=json.dumps({"plan_sha256": "0" * 64}))
        rc, out = run(check.check_forwardt_plan, [good, other], [])
        assert rc is False and "other" in out and "stored plan_sha256 000000000000" in out and out.count("FAIL") == 1, out
        # a file with no hash at all
        none = put(tmp, "none/forwardt.json", text="{}")
        rc, out = run(check.check_forwardt_plan, [none], [])
        assert rc is False and "stored plan_sha256 None" in out, out
        # a result file whose plan hash is right and whose first-commit hash is not
        bad = put(tmp, "bad/results.json", text=json.dumps({"plan_sha256": PLAN_SHA256, "first_commit_plan_sha256": "1" * 64}))
        rc, out = run(check.check_forwardt_plan, [], [bad])
        assert rc is False and "first_commit_plan_sha256 111111111111" in out, out
        # unreadable
        broken = put(tmp, "broken/forwardt.json", text="{not json")
        rc, out = run(check.check_forwardt_plan, [broken], [])
        assert rc is False and "unreadable" in out, out
        # a file that is not an object
        listy = put(tmp, "listy/forwardt.json", text="[1, 2]")
        rc, out = run(check.check_forwardt_plan, [listy], [])
        assert rc is False and "unreadable" in out, out


def test_an_edited_plan_in_a_scratch_repository_fails_the_whole_step():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
            assert rc is True, out
            plan = os.path.join(tmp, "forwardt", "PLAN.md")
            with open(plan, "rb") as f:
                data = f.read()
            with open(plan, "wb") as f:
                f.write(data + b" ")
            rc, out = run(check.check_forwardt)
            assert rc is False and "the plan was edited" in out, out


# ---------------------------------------------------------------- the manifest names every stored file

def test_a_stored_file_in_a_folder_the_manifest_does_not_name_is_caught():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp, manifest_doc={"schema": 1, "entries": [entry("results/named-run")]})
        named = put(tmp, "results/named-run/job-1/forwardt.json", text=json.dumps({"plan_sha256": PLAN_SHA256}))
        stray = put(tmp, "results/stray-run/job-1/forwardt.json", text=json.dumps({"plan_sha256": PLAN_SHA256}))
        near = put(tmp, "results/named-run-2/job-1/forwardt.json", text=json.dumps({"plan_sha256": PLAN_SHA256}))
        with repo_at(tmp):
            rc, out = run(check.check_forwardt_named, [named])
            assert rc is True and "all 1 stored forwardt.json" in out, out
            rc, out = run(check.check_forwardt_named, [named, stray, near])
            assert rc is False and out.count("FAIL") == 2, out
            assert "results/stray-run/job-1/forwardt.json" in out and "results/named-run-2/job-1/forwardt.json" in out, out
            assert "named-run/job-1" not in out.replace("named-run-2/job-1", ""), out   # a folder named only by its prefix is not named
            # found by the same glob the step uses, in results/ and in forwardt/
            put(tmp, "forwardt/odd/forwardt.json", text="{}")
            found = [os.path.relpath(p, tmp).replace("\\", "/") for p in check.forwardt_result_files(tmp)]
            assert found == ["forwardt/odd/forwardt.json", "results/named-run-2/job-1/forwardt.json",
                             "results/named-run/job-1/forwardt.json", "results/stray-run/job-1/forwardt.json"], found
            rc, out = run(check.check_forwardt_named, [])
            assert rc is True and "(no forwardt.json is stored)" in out, out


def test_the_step_fails_on_an_unnamed_stored_file_even_when_the_analysis_alone_passes():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp)
        put(tmp, "results/stray-run/job-1/forwardt.json", text=json.dumps({"plan_sha256": PLAN_SHA256}))
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
        assert rc is False, out
        assert "nothing to verify" in out, out     # the analysis reads only what the manifest names, so it has nothing to object to
        assert "FAIL results/stray-run/job-1/forwardt.json: no entry of forwardt/runs.json names its folder" in out, out


def test_a_malformed_manifest_fails_the_naming_check_and_the_analysis():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp, manifest=False)
        put(tmp, "forwardt/runs.json", text="{not json")
        with repo_at(tmp):
            rc, out = run(check.check_forwardt_named, [])
            assert rc is False and "cannot be read as a manifest" in out, out
            rc, out = run(check.check_forwardt)
            assert rc is False, out


# ---------------------------------------------------------------- results.json

def test_a_results_json_that_matches_a_fresh_analysis_passes_and_one_that_differs_fails():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp)
        path = write_results(tmp)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
            assert rc is True and "matches the recomputation" in out, out
            assert "and 1 result file(s) stored" in out, out
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
            # a number the plan guard does not read: the stored criteria hash
            doc["criteria_sha256"] = "2" * 64
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(doc, f, indent=1, sort_keys=True)
                f.write("\n")
            rc, out = run(check.check_forwardt)
            assert rc is False, out
            assert "results.json differs: /criteria_sha256" in out and "does NOT match the recomputation" in out, out
            assert "ok   forwardt/PLAN.md" in out, out    # the plan guard is not what failed
            # the plan hash stored in it, changed: the plan guard fails as well
            doc["plan_sha256"] = "3" * 64
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(doc, f, indent=1, sort_keys=True)
                f.write("\n")
            rc, out = run(check.check_forwardt)
            assert rc is False and "stored plan_sha256 333333333333" in out, out


def test_a_results_json_that_cannot_be_read_fails_without_running_the_analysis():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp)
        put(tmp, "forwardt/results.json", text="{broken")
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
        assert rc is False and "FAIL forwardt/results.json: unreadable" in out, out
        assert "nothing to verify" not in out and "Traceback" not in out, out


def test_a_missing_results_json_fails_exactly_when_the_manifest_lists_a_run():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp, manifest_doc={"schema": 1, "entries": [entry("results/some-run")]})
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
        assert rc is False and "FAIL forwardt/results.json: missing, but forwardt/runs.json lists 1 run(s)" in out, out
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp)     # an empty manifest (a scratch tree; the committed one lists runs): nothing to verify, which passes
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
        assert rc is True and "nothing to verify" in out, out


# ---------------------------------------------------------------- what must exist

def test_a_missing_analysis_script_plan_or_manifest_is_a_failure_and_never_a_pass():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp, analysis=False)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
        assert rc is False and "FAIL forwardt/analyze.py: missing, so the step cannot run" in out, out
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp, plan=False)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
        assert rc is False and "FAIL forwardt/PLAN.md: missing" in out, out
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp, manifest=False)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
        assert rc is False and "FAIL forwardt/runs.json: missing" in out, out
    with tempfile.TemporaryDirectory() as tmp:
        with repo_at(tmp):     # an empty repository
            rc, out = run(check.check_forwardt)
        assert rc is False and "FAIL forwardt/analyze.py: missing" in out, out


def test_an_analysis_script_without_the_recorded_hash_fails_the_plan_guard():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp)
        path = os.path.join(tmp, "forwardt", "analyze.py")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace("FIRST_COMMIT_PLAN_SHA256", "SOME_OTHER_NAME"))
        with repo_at(tmp):
            rc, out = run(check.check_forwardt_plan, [], [])
        assert rc is False and "no FIRST_COMMIT_PLAN_SHA256 constant found" in out, out
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace(PLAN_SHA256, "4" * 64))
        with repo_at(tmp):
            rc, out = run(check.check_forwardt_plan, [], [])
        assert rc is False and "records the plan as 444444444444" in out, out


# ---------------------------------------------------------------- a checkout whose path has glob characters in it

def test_a_checkout_under_a_folder_with_brackets_in_its_name_still_has_its_stored_files_found():
    want = ["forwardt/odd/forwardt.json", "results/some-run/job-1/forwardt.json"]
    with tempfile.TemporaryDirectory() as base:
        for name in ("repo1", "repo[1]"):
            root = os.path.join(base, name)
            put(root, "results/some-run/job-1/forwardt.json", text="{}")
            put(root, "forwardt/odd/forwardt.json", text="{}")
            found = [os.path.relpath(p, root).replace("\\", "/") for p in check.forwardt_result_files(root)]
            assert found == want, (name, found)
    # the whole step: a stored file no entry names is still caught in a checkout called repo[1]
    with tempfile.TemporaryDirectory() as base:
        root = scratch(os.path.join(base, "repo[1]"))
        put(root, "results/stray-run/job-1/forwardt.json", text=json.dumps({"plan_sha256": PLAN_SHA256}))
        with repo_at(root):
            rc, out = run(check.check_forwardt)
        assert rc is False, out
        assert "FAIL results/stray-run/job-1/forwardt.json: no entry of forwardt/runs.json names its folder" in out, out
        assert "all 0 forwardt.json" not in out and "all 0 stored forwardt.json" not in out, out


# ---------------------------------------------------------------- the step over real stored job files

def helpers():
    """tests/test_forwardt_analyze.py loaded as a module, for its make_doc, write_run and manifest_of: they make job files that
    pass the sweep's own schema check, with the within-job intervals the analysis recomputes."""
    key = "test_forwardt_analyze"
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, key + ".py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]




_RUN_DOCS = {}


def stored_run(tmp, jobs=1, name="named-run"):
    """A scratch repository whose manifest has one entry and whose folder results/<name> holds `jobs` job files made by the faked
    sweep, with within-job intervals made at the number of resamples --verify recomputes them with (so --verify finds the files
    fine). The files are made once per process and copied: making one costs a few seconds."""
    h = helpers()
    if jobs not in _RUN_DOCS:
        rid = h.next_rid()
        _RUN_DOCS[jobs] = [h.make_doc(run_id=rid, job=str(i + 1), boot=h.stats.RESAMPLES) for i in range(jobs)]
    e = h.write_run(tmp, copy.deepcopy(_RUN_DOCS[jobs]), name=name)
    scratch(tmp, manifest_doc=h.manifest_of([e]))
    return e


def job_path(tmp, i=0, name="named-run"):
    return os.path.join(tmp, "results", name, "job-%d" % i, "forwardt.json")


def change_json(path, **fields):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    doc.update(fields)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)


def edit_manifest(tmp, fn):
    path = os.path.join(tmp, "forwardt", "runs.json")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    fn(doc)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")


def verify_alone(tmp):
    """The analysis's own --verify on the scratch repository: (exit code, what it printed)."""
    r = subprocess.run([sys.executable, os.path.join(tmp, "forwardt", "analyze.py"), "--verify"], capture_output=True, text=True,
                       errors="replace")
    return r.returncode, r.stdout + r.stderr


def test_the_step_hands_every_stored_job_file_to_the_plan_guard():
    with tempfile.TemporaryDirectory() as tmp:
        stored_run(tmp)
        write_results(tmp)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
            assert rc is True, out
            assert "verified 1 file(s): 0 with problems" in out and "matches the recomputation" in out, out
            assert "all 1 forwardt.json and 1 result file(s) stored were produced under" in out, out
            # one job file made under another plan; results.json is written again so that --verify has nothing to object to
            change_json(job_path(tmp), plan_sha256="0" * 64)
            write_results(tmp)
            code, text = verify_alone(tmp)
            assert code == 0 and "verified 1 file(s): 0 with problems" in text, text
            rc, out = run(check.check_forwardt)
            assert rc is False, out
            assert "FAIL results/named-run/job-0/forwardt.json: stored plan_sha256 000000000000" in out, out
            assert "verified 1 file(s): 0 with problems" in out and "matches the recomputation" in out, out   # --verify did not object
            assert out.count("FAIL") == 1, out
            # a hash that is the plan's except in its last character is no better
            last = "0" if PLAN_SHA256[-1] != "0" else "1"
            change_json(job_path(tmp), plan_sha256=PLAN_SHA256[:-1] + last)
            write_results(tmp)
            rc, out = run(check.check_forwardt)
            assert rc is False and "job-0/forwardt.json: stored plan_sha256 91a7c6a08a13" in out and out.count("FAIL") == 1, out


def test_a_stored_file_under_forwardt_with_a_wrong_hash_is_caught_by_the_step():
    with tempfile.TemporaryDirectory() as tmp:
        stored_run(tmp)
        os.makedirs(os.path.join(tmp, "forwardt", "runs"))
        shutil.move(os.path.join(tmp, "results", "named-run"), os.path.join(tmp, "forwardt", "runs", "one"))
        edit_manifest(tmp, lambda doc: doc["entries"][0].update(folder="forwardt/runs/one"))
        write_results(tmp)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
            assert rc is True and "all 1 forwardt.json and 1 result file(s) stored were produced under" in out, out
            change_json(os.path.join(tmp, "forwardt", "runs", "one", "job-0", "forwardt.json"), plan_sha256="0" * 64)
            write_results(tmp)
            rc, out = run(check.check_forwardt)
            assert rc is False and out.count("FAIL") == 1, out
            assert "FAIL forwardt/runs/one/job-0/forwardt.json: stored plan_sha256 000000000000" in out, out


def test_a_stop_of_the_analysis_fails_the_step_and_its_words_are_printed():
    with tempfile.TemporaryDirectory() as tmp:
        e = stored_run(tmp)
        write_results(tmp)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
            assert rc is True, out

            # the manifest now says two jobs came back and one file is stored: a stop of 'Runs: Accounting', exit code 3
            def two_returned(doc):
                doc["entries"][0].update(jobs_started=2, jobs_returned=2)
            edit_manifest(tmp, two_returned)
            code, text = verify_alone(tmp)
            assert code == 3 and "stop: run %s: 1 forwardt.json file(s)" % e["run_id"] in text, (code, text)
            rc, out = run(check.check_forwardt)
            assert rc is False, out
            assert "stop: run %s: 1 forwardt.json file(s) with its run id in results/named-run" % e["run_id"] in out, out
            assert "the manifest says 2 job(s) returned" in out, out
            assert "FAIL" not in out, out    # the plan and naming checks pass: the exit code alone failed the step


def test_a_raising_analysis_script_fails_the_step_and_its_traceback_is_printed():
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp)
        with open(os.path.join(tmp, "forwardt", "analyze.py"), "w", encoding="utf-8", newline="\n") as f:
            f.write('FIRST_COMMIT_PLAN_SHA256 = "%s"\nraise RuntimeError("the analysis went wrong here")\n' % PLAN_SHA256)
        with repo_at(tmp):
            rc, out = run(check.check_forwardt)
        assert rc is False, out
        assert "Traceback" in out and "RuntimeError: the analysis went wrong here" in out, out


# ---------------------------------------------------------------- main() calls the step

def _is_step(stmt, name, op=ast.BitAnd):
    """`ok &= name()` as a statement: nothing else (not a comment, not `ok = name()`, not `ok |= name()`, not `name() or ...`)."""
    return (isinstance(stmt, ast.AugAssign) and isinstance(stmt.op, op) and isinstance(stmt.target, ast.Name) and stmt.target.id == "ok"
            and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == name
            and not stmt.value.args and not stmt.value.keywords)


def test_main_ands_the_result_of_the_forwardt_step_into_ok_as_a_statement_of_its_own():
    fn = ast.parse(inspect.getsource(check.main)).body[0]
    assert isinstance(fn, ast.FunctionDef) and fn.name == "main"
    body = fn.body
    at = [i for i, s in enumerate(body) if _is_step(s, "check_forwardt")]
    assert len(at) == 1, "main() has no single top-level statement 'ok &= check_forwardt()' (a comment, a condition or another operator?)"
    i = at[0]
    named = [n for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id == "check_forwardt"]
    assert len(named) == 1, "check_forwardt is named somewhere else in main() as well"
    d = [j for j, s in enumerate(body) if _is_step(s, "check_dsweep")]
    assert len(d) == 1 and d[0] < i, "the step does not come after the d-sweep step"
    heading = body[i - 1]
    assert isinstance(heading, ast.Expr) and "forwardt/analyze.py --verify" in ast.unparse(heading), "the step has no heading of its own"
    assert "== PGO column" in ast.unparse(body[i + 1]), "the next statement is not the next step's heading"
    # nothing before it leaves main() early, nothing after it throws the result away
    assert not any(isinstance(s, (ast.Return, ast.Raise)) for s in body[:i]), "a top-level return or raise comes before the step"
    for s in body[i + 1:]:
        for n in ast.walk(s):
            if isinstance(n, ast.Assign):
                assert not any(isinstance(t, ast.Name) and t.id == "ok" for t in n.targets), "ok is assigned after the step"
            if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) and n.target.id == "ok":
                assert isinstance(n.op, ast.BitAnd), "ok is combined with another operator after the step"
    assert isinstance(body[-1], ast.Return) and ast.unparse(body[-1]) == "return finish(ok, skipped)"


# ---------------------------------------------------------------- the naming check, deeper

def test_the_naming_check_with_folders_of_depth_two_and_three_a_null_folder_and_one_unnamed_file():
    manifest = {"schema": 1, "entries": [entry("results/a", "39000000001"), entry("results/b/c/", "39000000002"),
                                         entry(None, "39000000003")]}
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp, manifest_doc=manifest)
        ok_files = [put(tmp, "results/a/job-1/forwardt.json", text="{}"),
                    put(tmp, "results/a/forwardt.json", text="{}"),
                    put(tmp, "results/b/c/job-1/forwardt.json", text="{}"),
                    put(tmp, "results/b/c/deeper/still/job-2/forwardt.json", text="{}")]
        unnamed = put(tmp, "results/b/job-1/forwardt.json", text="{}")       # the parent of a named folder is not named
        with repo_at(tmp):
            rc, out = run(check.check_forwardt_named, ok_files)
            assert rc is True and "all 4 stored forwardt.json file(s) lie in a folder" in out, out
            rc, out = run(check.check_forwardt_named, ok_files + [unnamed])
            assert rc is False and out.count("FAIL") == 1, out
            assert "FAIL results/b/job-1/forwardt.json: no entry of forwardt/runs.json names its folder" in out, out
            # an entry with no folder names nothing: a file is unnamed when only that entry could have named it
            rc, out = run(check.check_forwardt_named, [put(tmp, "results/d/job-1/forwardt.json", text="{}")])
            assert rc is False and out.count("FAIL") == 1 and "cannot be read as a manifest" not in out, out


# ---------------------------------------------------------------- hashes that differ in the last character only

def test_the_plan_guard_compares_the_whole_hash_including_its_last_character():
    last = "0" if PLAN_SHA256[-1] != "0" else "1"
    near = PLAN_SHA256[:-1] + last
    assert near != PLAN_SHA256 and near[:63] == PLAN_SHA256[:63]
    # the value scripts/check.py records
    rc, out = run(check.check_forwardt_plan, [], [], recorded=near)
    assert rc is False and out.count("FAIL") == 1 and "but scripts/check.py records 91a7c6a08a13" in out and "the plan was edited" in out, out
    # the value forwardt/analyze.py records
    with tempfile.TemporaryDirectory() as tmp:
        scratch(tmp)
        path = os.path.join(tmp, "forwardt", "analyze.py")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        assert text.count(PLAN_SHA256) == 1, "analyze.py is expected to write the plan's hash once"
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace(PLAN_SHA256, near))
        with repo_at(tmp):
            rc, out = run(check.check_forwardt_plan, [], [])
        assert rc is False and out.count("FAIL") == 1 and "records the plan as 91a7c6a08a13" in out, out
        # a 63-character value is no hash
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace(PLAN_SHA256, PLAN_SHA256[:-1]))
        with repo_at(tmp):
            rc, out = run(check.check_forwardt_plan, [], [])
        assert rc is False and "no FIRST_COMMIT_PLAN_SHA256 constant found" in out, out
    # the values a stored job file and a result file carry
    with tempfile.TemporaryDirectory() as tmp:
        job = put(tmp, "job/forwardt.json", text=json.dumps({"plan_sha256": near}))
        rc, out = run(check.check_forwardt_plan, [job], [])
        assert rc is False and out.count("FAIL") == 1 and "stored plan_sha256 91a7c6a08a13" in out, out
        res = put(tmp, "res/results.json", text=json.dumps({"plan_sha256": PLAN_SHA256, "first_commit_plan_sha256": near}))
        rc, out = run(check.check_forwardt_plan, [], [res])
        assert rc is False and out.count("FAIL") == 1 and "stored first_commit_plan_sha256 91a7c6a08a13" in out, out
        res2 = put(tmp, "res2/results.json", text=json.dumps({"plan_sha256": near, "first_commit_plan_sha256": PLAN_SHA256}))
        rc, out = run(check.check_forwardt_plan, [], [res2])
        assert rc is False and out.count("FAIL") == 1 and "stored plan_sha256 91a7c6a08a13" in out, out


# ---------------------------------------------------------------- the documents say "empty manifest" only while it is empty

# Sentences copied from the documents as they stand while forwardt/runs.json lists no run. Every one of them is false from the
# first recorded entry on, so with entries in the manifest none of them may remain; with no entry all of them must.
# (The conditional sentences "With no run in the manifest it says so ..." and "with an empty manifest it has nothing to verify
# and passes" of forwardt/README.md are true at any number of entries and are not listed.)
EMPTY_MANIFEST_SENTENCES = {
    "forwardt/README.md": [
        "No run of the sweep exists, `runs.json` lists none, and no result is claimed here or anywhere else in the repository.",
        "one entry per run (see below). It is empty.",
        "the manifest is empty. `python forwardt/analyze.py` on the empty manifest reports that no run exists.",
        "Until a run is recorded, nothing here says what FAST costs on these loops.",
    ],
    "README.md": [
        "the manifest of runs `forwardt/runs.json` (empty)",
        "no run exists and no result is claimed",
    ],
    "readme-parts/DETAILS.md": [
        "The manifest of runs is empty: no run exists and no result is claimed.",
        "runs.json (empty)",
    ],
}
# The folder-map line of each outer document: it must be found exactly once and carry "(empty)" exactly while the manifest is.
EMPTY_MANIFEST_MAP_LINES = {
    "README.md": "`forwardt/` the timing of six forward loops",
    "readme-parts/DETAILS.md": "forwardt/       the variable-bound timing",
}


def entries_word(n):
    return "1 entry" if n == 1 else "%d entries" % n


def empty_manifest_problems(root):
    """What is wrong in the documents under root about the manifest forwardt/runs.json: a list of words, empty when the
    documents agree with the number of entries."""
    with open(os.path.join(root, "forwardt", "runs.json"), encoding="utf-8") as f:
        n = len(json.load(f)["entries"])
    problems = []
    for rel, sentences in EMPTY_MANIFEST_SENTENCES.items():
        with open(os.path.join(root, *rel.split("/")), encoding="utf-8") as f:
            text = f.read()
        for s in sentences:
            if n == 0 and s not in text:
                problems.append("%s: the manifest has no entry but this sentence is gone: %r" % (rel, s))
            if n > 0 and s in text:
                problems.append("%s: the manifest has %s but this sentence still says it is empty: %r" % (rel, entries_word(n), s))
        marker = EMPTY_MANIFEST_MAP_LINES.get(rel)
        if marker is not None:
            lines = [ln for ln in text.splitlines() if marker in ln]
            if len(lines) != 1:
                problems.append("%s: the folder-map line %r was found %d times, expected once" % (rel, marker, len(lines)))
            elif n == 0 and "(empty)" not in lines[0]:
                problems.append("%s: the manifest has no entry but its folder-map line does not say (empty)" % rel)
            elif n > 0 and "(empty)" in lines[0]:
                problems.append("%s: the manifest has %s but its folder-map line still says (empty)" % (rel, entries_word(n)))
    return problems


def test_the_sentences_that_call_the_manifest_empty_match_the_number_of_recorded_runs():
    problems = empty_manifest_problems(REPO)
    assert not problems, "\n".join(problems)


def rewrite(path, fn):
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(fn(text))
    return text


def synthetic_empty_state(root):
    """Documents as they read while the manifest lists no run (the committed ones no longer do), and an empty manifest."""
    put(root, "forwardt/runs.json", text=json.dumps(EMPTY_MANIFEST) + "\n")
    put(root, "forwardt/README.md", text="\n".join(EMPTY_MANIFEST_SENTENCES["forwardt/README.md"]) + "\n")
    put(root, "README.md", text="intro\nno run exists and no result is claimed\n"
        "- `forwardt/` the timing of six forward loops, the manifest of runs `forwardt/runs.json` (empty)\n")
    put(root, "readme-parts/DETAILS.md", text="intro\r\nThe manifest of runs is empty: no run exists and no result is claimed.\r\n"
        "forwardt/       the variable-bound timing, runs.json (empty)\r\n")


def test_the_empty_manifest_guard_reads_the_manifest_both_ways():
    with tempfile.TemporaryDirectory() as tmp:
        synthetic_empty_state(tmp)
        assert empty_manifest_problems(tmp) == []
        # one sentence gone while the manifest is empty
        gone = EMPTY_MANIFEST_SENTENCES["forwardt/README.md"][3]
        path = os.path.join(tmp, "forwardt", "README.md")
        text = rewrite(path, lambda t: t.replace(gone, ""))
        assert text.count(gone) == 1
        got = empty_manifest_problems(tmp)
        assert len(got) == 1 and "this sentence is gone" in got[0] and "Until a run is recorded" in got[0], got
        rewrite(path, lambda t: text)
        assert empty_manifest_problems(tmp) == []
        # a folder-map line that is not found exactly once
        path = os.path.join(tmp, "readme-parts", "DETAILS.md")
        marker = EMPTY_MANIFEST_MAP_LINES["readme-parts/DETAILS.md"]
        details = rewrite(path, lambda t: t.replace(marker, "forwardt/ the variable-bound timing"))
        got = empty_manifest_problems(tmp)
        assert any("found 0 times" in p for p in got), got
        rewrite(path, lambda t: details + "\n" + marker + " again\n")
        got = empty_manifest_problems(tmp)
        assert any("found 2 times" in p for p in got), got
        rewrite(path, lambda t: details)
        assert empty_manifest_problems(tmp) == []
        # the word "(empty)" gone from a folder-map line while the manifest is empty
        path = os.path.join(tmp, "README.md")
        readme = rewrite(path, lambda t: t.replace("`forwardt/runs.json` (empty)", "`forwardt/runs.json` (none)"))
        got = empty_manifest_problems(tmp)
        assert any("does not say (empty)" in p for p in got), got
        rewrite(path, lambda t: readme)
        assert empty_manifest_problems(tmp) == []
        # one recorded entry (the guard counts entries; their content is the analysis's business): every sentence is now false
        put(tmp, "forwardt/runs.json", text=json.dumps({"schema": 1, "entries": [{"run_id": 1}]}) + "\n")
        got = empty_manifest_problems(tmp)
        n_sentences = sum(len(v) for v in EMPTY_MANIFEST_SENTENCES.values())
        assert len(got) == n_sentences + len(EMPTY_MANIFEST_MAP_LINES), got
        assert all("1 entry" in p for p in got), got
        # the same documents rewritten for a manifest with entries: nothing is left to complain about
        for rel, sentences in EMPTY_MANIFEST_SENTENCES.items():
            def reword(t, sentences=sentences):
                for s in sentences:
                    t = t.replace(s, "a sentence about the recorded runs")
                return t.replace("(empty)", "(2 runs)")
            rewrite(os.path.join(tmp, *rel.split("/")), reword)
        assert empty_manifest_problems(tmp) == [], empty_manifest_problems(tmp)
        # only the folder-map word left over
        for rel, marker in EMPTY_MANIFEST_MAP_LINES.items():
            def add_word(t, marker=marker):
                lines = t.splitlines(True)      # readme-parts/DETAILS.md has CRLF line endings; each line keeps its own
                hit = [i for i, ln in enumerate(lines) if marker in ln]
                assert len(hit) == 1
                body = lines[hit[0]].rstrip("\r\n")
                lines[hit[0]] = body + " (empty)" + lines[hit[0]][len(body):]
                return "".join(lines)
            rewrite(os.path.join(tmp, *rel.split("/")), add_word)
        got = empty_manifest_problems(tmp)
        assert len(got) == 2 and all("folder-map line still says (empty)" in p for p in got), got
        # two entries are spelled "entries"
        put(tmp, "forwardt/runs.json", text=json.dumps({"schema": 1, "entries": [{}, {}]}) + "\n")
        got = empty_manifest_problems(tmp)
        assert got and all("2 entries" in p for p in got), got


# ---------------------------------------------------------------- the committed state: five runs, 18 stored files

# The runs of the committed manifest, in order: (run id, runner, class, clause, jobs started, folder or None).
COMMITTED_RUNS = [
    ("40181023212", "ubuntu-24.04", "test", "code test", 1, None),
    ("40181028100", "ubuntu-24.04-arm", "test", "code test", 1, None),
    ("40861186704", "ubuntu-24.04-arm", "measurement", "Neoverse-N2 run", 6, "results/s11-forwardt-run-40861186704"),
    ("40861190251", "ubuntu-24.04", "measurement", "x86-64 run 1", 6, "results/s11-forwardt-run-40861190251"),
    ("40861193559", "ubuntu-24.04", "measurement", "x86-64 run 2", 6, "results/s11-forwardt-run-40861193559"),
]
COMMITTED_SHA = "595e061f53cf074011ee15f998be14a45f950c1f"
# CPU model fragment -> (jobs in the 18 stored files, read by the analysis, target). EPYC 9V45 has 2 jobs, below the rule's 3.
COMMITTED_MODELS = {"EPYC 7763": (7, True, "x86-64"), "EPYC 9V45": (2, False, "x86-64"), "EPYC 9V74": (3, True, "x86-64"),
                    "Neoverse-N2": (6, True, "Neoverse-N2")}


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def committed_state_problems(root):
    """Where the forwardt runs under root differ from the committed state: the manifest (five entries, two code tests and three
    measurement runs, one commit), the 18 stored forwardt.json files (six per measurement folder, the plan hash, the run id and
    commit each carries) and forwardt/results.json (the plan hash, the jobs per CPU model and which models are read). A list of
    words, empty when everything agrees. It reads files and recomputes nothing; the numbers are forwardt/analyze.py --verify's."""
    problems = []
    try:
        manifest = jload(os.path.join(root, "forwardt", "runs.json"))
        entries = manifest["entries"]
    except (OSError, ValueError, KeyError) as e:
        return ["forwardt/runs.json cannot be read (%s)" % e]
    for key, want in (("branch", "forwardt-run"), ("workflow_file", ".github/workflows/forwardt.yml"),
                      ("time_limit_minutes", 45), ("test_ratios_read", False)):
        if manifest.get(key) != want:
            problems.append("runs.json %s is %r, expected %r" % (key, manifest.get(key), want))
    if len(entries) != len(COMMITTED_RUNS):
        problems.append("runs.json lists %d entries, expected %d" % (len(entries), len(COMMITTED_RUNS)))
    for got, (run_id, runner, cls, clause, jobs, folder) in zip(entries, COMMITTED_RUNS):
        have = (got.get("run_id"), got.get("runner"), got.get("class"), got.get("clause"), got.get("jobs_started"), got.get("folder"))
        if have != (run_id, runner, cls, clause, jobs, folder):
            problems.append("runs.json entry %s differs: %r" % (run_id, have))
        if got.get("jobs_returned") != jobs or got.get("not_returned") != []:
            problems.append("runs.json entry %s: jobs_returned %r, not_returned %r" % (run_id, got.get("jobs_returned"), got.get("not_returned")))
        if got.get("head_sha") != COMMITTED_SHA:
            problems.append("runs.json entry %s: head_sha %r, expected %s" % (run_id, got.get("head_sha"), COMMITTED_SHA))
    files = check.forwardt_result_files(root)
    if len(files) != 18:
        problems.append("%d forwardt.json files are stored, expected 18" % len(files))
    jobs_by_model = {}
    for path in files:
        rel = os.path.relpath(path, root).replace("\\", "/")
        doc = jload(path)
        folder = rel.rsplit("/", 2)[0]
        entry_ = [r for r in COMMITTED_RUNS if r[5] == folder]
        if not entry_:
            problems.append("%s: lies in no folder of the manifest" % rel)
            continue
        run = doc.get("run", {})
        if doc.get("plan_sha256") != PLAN_SHA256 or doc.get("smoke") is not False or doc.get("kind") != "forwardt":
            problems.append("%s: plan_sha256, smoke or kind differs (%r, %r, %r)" % (rel, doc.get("plan_sha256"), doc.get("smoke"), doc.get("kind")))
        if run.get("id") != entry_[0][0] or run.get("commit") != COMMITTED_SHA or run.get("attempt") != 1:
            problems.append("%s: run id, commit or attempt differs (%r, %r, %r)" % (rel, run.get("id"), run.get("commit"), run.get("attempt")))
        want_arch = "aarch64" if entry_[0][1].endswith("arm") else "x86_64"
        if run.get("runner", {}).get("arch") != want_arch:
            problems.append("%s: arch %r, expected %s" % (rel, run.get("runner", {}).get("arch"), want_arch))
        model = run.get("runner", {}).get("cpu_model", "")
        jobs_by_model[model] = jobs_by_model.get(model, 0) + 1
    for frag, (jobs, _read, _target) in COMMITTED_MODELS.items():
        have = sum(n for m, n in jobs_by_model.items() if frag in m)
        if have != jobs:
            problems.append("%d stored files name a CPU model with %r, expected %d" % (have, frag, jobs))
    per_folder = {}
    for path in files:
        folder = os.path.relpath(path, root).replace("\\", "/").rsplit("/", 2)[0]
        per_folder[folder] = per_folder.get(folder, 0) + 1
    for _id, _r, cls, _c, _j, folder in COMMITTED_RUNS:
        if folder and per_folder.get(folder) != 6:
            problems.append("%s holds %r forwardt.json files, expected 6" % (folder, per_folder.get(folder)))
    try:
        results = jload(os.path.join(root, "forwardt", "results.json"))
        models = results["analysis"]["models"]
    except (OSError, ValueError, KeyError) as e:
        return problems + ["forwardt/results.json cannot be read (%s)" % e]
    for key in ("plan_sha256", "first_commit_plan_sha256"):
        if results.get(key) != PLAN_SHA256:
            problems.append("results.json %s is %r" % (key, results.get(key)))
    if len(models) != len(COMMITTED_MODELS):
        problems.append("results.json has %d CPU models, expected %d" % (len(models), len(COMMITTED_MODELS)))
    for frag, (jobs, read, target) in COMMITTED_MODELS.items():
        hit = [m for m in models if frag in m.get("cpu_model", "")]
        if len(hit) != 1 or (hit[0].get("jobs"), hit[0].get("read"), hit[0].get("target")) != (jobs, read, target):
            problems.append("results.json model %r: %r, expected %r" % (
                frag, [(m.get("jobs"), m.get("read"), m.get("target")) for m in hit], (jobs, read, target)))
    return problems


def copy_committed_state(tmp):
    """The files committed_state_problems reads, copied from the repository (plan, manifest, results.json, 18 stored files)."""
    for rel in ("forwardt/runs.json", "forwardt/results.json"):
        shutil.copyfile(os.path.join(REPO, *rel.split("/")), put(tmp, rel, text=""))
    for path in check.forwardt_result_files(REPO):
        rel = os.path.relpath(path, REPO).replace("\\", "/")
        shutil.copyfile(path, put(tmp, rel, text=""))


def test_the_committed_state_is_five_runs_eighteen_files_and_the_models_7_2_3_6():
    problems = committed_state_problems(REPO)
    assert not problems, "\n".join(problems)


def test_the_committed_state_pins_find_a_changed_manifest_or_result_file():
    with tempfile.TemporaryDirectory() as tmp:
        copy_committed_state(tmp)
        assert committed_state_problems(tmp) == []
        manifest_path = os.path.join(tmp, "forwardt", "runs.json")
        results_path = os.path.join(tmp, "forwardt", "results.json")
        stored = check.forwardt_result_files(tmp)
        assert len(stored) == 18

        def changed(path, edit, needle):
            """Edit one JSON file, collect the problems that name needle, restore it."""
            doc = jload(path)
            with open(path, encoding="utf-8", newline="") as f:
                original = f.read()
            edit(doc)
            with open(path, "w", encoding="utf-8", newline="") as f:
                json.dump(doc, f, indent=1)
            try:
                got = committed_state_problems(tmp)
            finally:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(original)
            assert got and any(needle in p for p in got), (needle, got)
            assert committed_state_problems(tmp) == []

        changed(manifest_path, lambda d: d["entries"].pop(), "lists 4 entries")
        changed(manifest_path, lambda d: d["entries"][3].update(jobs_returned=5), "jobs_returned 5")
        changed(manifest_path, lambda d: d["entries"][4].update(head_sha="b" * 40), "head_sha")
        changed(manifest_path, lambda d: d.update(test_ratios_read=True), "test_ratios_read")
        changed(manifest_path, lambda d: d["entries"][2].update(folder="results/s11-forwardt-run-40861190251"), "differs")
        changed(results_path, lambda d: d.update(plan_sha256="3" * 64), "results.json plan_sha256")
        changed(results_path, lambda d: d["analysis"]["models"][0].update(jobs=8), "model 'EPYC 7763'")
        changed(results_path, lambda d: d["analysis"]["models"][1].update(read=True), "model 'EPYC 9V45'")
        changed(stored[0], lambda d: d.update(plan_sha256="4" * 64), "plan_sha256, smoke or kind differs")
        changed(stored[5], lambda d: d.update(smoke=True), "plan_sha256, smoke or kind differs")
        changed(stored[7], lambda d: d["run"]["runner"].update(cpu_model="Another CPU"), "expected")
        changed(stored[9], lambda d: d["run"].update(commit="c" * 40), "run id, commit or attempt differs")
        changed(stored[11], lambda d: d["run"].update(attempt=2), "run id, commit or attempt differs")
        # a stored file gone, and one stray file in a folder the manifest does not name
        removed = stored[17]
        with open(removed, "rb") as f:
            blob = f.read()
        os.remove(removed)
        got = committed_state_problems(tmp)
        assert any("17 forwardt.json files" in p for p in got) and any("holds 5" in p for p in got), got
        with open(put(tmp, os.path.relpath(removed, tmp).replace("\\", "/"), text=""), "wb") as f:
            f.write(blob)
        assert committed_state_problems(tmp) == []
        put(tmp, "results/stray-run/job-1/forwardt.json", data=blob)
        got = committed_state_problems(tmp)
        assert any("19 forwardt.json files" in p for p in got) and any("lies in no folder" in p for p in got), got
