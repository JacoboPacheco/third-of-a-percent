"""The last line and the exit code of scripts/check.py: a failure is 1, a run whose steps all passed but in which one was
skipped is 3 with its own line, a full pass is 0, and a missing required package stops the run at once with the pip line.

README.md and readme-parts/DETAILS.md quote the line and the code; test_readme_numbers.py ties them to the constants here.
No pytest fixtures: scripts/check.py's built-in runner calls every test with no arguments."""
import contextlib
import glob
import importlib
import inspect
import io
import json
import os
import re
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
check = importlib.import_module("check")


def run(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    return rc, buf.getvalue()


def test_a_full_pass_is_exit_0_and_all_checks_passed():
    rc, out = run(check.finish, True, [])
    assert rc == 0
    assert out.strip().splitlines()[-1] == "ALL CHECKS PASSED"


def test_a_pass_with_a_skipped_step_is_its_own_line_and_exit_3():
    rc, out = run(check.finish, True, ["the page was not driven"])
    assert rc == check.EXIT_PASSED_WITH_SKIPS == 3
    assert out.splitlines()[0] == check.PASSED_WITH_SKIPS == "CHECKS PASSED, WITH SKIPPED STEPS"
    assert "ALL CHECKS PASSED" not in out and "the page was not driven" in out


def test_a_failure_is_exit_1_even_when_a_step_was_skipped():
    rc, out = run(check.finish, False, ["the page was not driven"])
    assert rc == 1
    assert out.strip() == "CHECKS FAILED"


def test_a_missing_required_package_stops_the_run_before_any_step():
    real = check.importlib.import_module

    def fake(name, *a, **k):
        if name == "yaml":
            raise ImportError("no module named yaml")
        return real(name, *a, **k)
    real_tests = check.run_tests

    def no_step_may_run():
        raise AssertionError("a step ran before the packages were checked")
    check.importlib.import_module = fake
    check.run_tests = no_step_may_run  # without the pre-flight, main() would start the hour-long run: stop it at the first step
    try:
        assert check.missing_packages() == ["pyyaml"]
        rc, out = run(check.main)
    finally:
        check.importlib.import_module = real
        check.run_tests = real_tests
    assert rc == 1
    assert "MISSING PYTHON PACKAGES: pyyaml" in out and "pip install pyyaml" in out and out.strip().endswith("CHECKS FAILED")


def test_the_required_packages_are_the_ones_the_readme_names():
    assert dict(check.REQUIRED_PACKAGES) == {"numpy": "numpy", "yaml": "pyyaml"}


# ---------------------------------------------------------------- a missing checker or result is a failure, not a pass

def _first_job(run_glob):
    """The first job folder (results.json beside asm/) of the run folders matching `run_glob` under results/."""
    jobs = sorted(glob.glob(os.path.join(REPO, "results", run_glob, "results-*", "results.json")))
    assert jobs, f"no job under results/{run_glob}"
    return os.path.dirname(jobs[0])


def _job_copy(tmp, src, name="job"):
    """results.json and the listings (asm/*.s) of a job folder, copied; the .diff files and the remarks are not needed."""
    dst = os.path.join(tmp, name)
    os.makedirs(os.path.join(dst, "asm"))
    shutil.copyfile(os.path.join(src, "results.json"), os.path.join(dst, "results.json"))
    for f in glob.glob(os.path.join(src, "asm", "*.s")):
        shutil.copyfile(f, os.path.join(dst, "asm", os.path.basename(f)))
    return dst


def _recount(job):
    with open(os.path.join(job, "results.json"), encoding="utf-8") as f:
        doc = json.load(f)
    problems = []
    n = check.check_trap_counts(os.path.join(job, "results.json"), doc, problems)
    return doc, n, problems


def _rewrite(path, fn):
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    new = fn(text)
    assert new != text, f"the edit changed nothing in {path}"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)


def _drop_trap_line(text, pattern):
    lines = text.split("\n")
    at = next(i for i, ln in enumerate(lines) if re.search(pattern, ln))
    return "\n".join(lines[:at] + lines[at + 1:])


def _add_trap_line(text, trap):
    return text + ("    ud2\n" if "ud2" in trap else "    brk    #0x1\n")


def test_the_stored_trap_counts_are_recounted_from_the_listings_of_an_x86_64_and_an_arm_job():
    for run_glob, trap in (("s7-run-*", r"\bud2\b"), ("s8-arm-run-*", r"\bbrk\s+#0x1\b")):
        with tempfile.TemporaryDirectory() as tmp:
            doc, n, problems = _recount(_job_copy(tmp, _first_job(run_glob)))
            assert problems == [] and n == 4 * len(doc["cells"]), (run_glob, n, problems)
            # not vacuous: the FAST builds really hold trap instructions, and the stored counts say so
            assert any(c["traps_fast"] >= 1 for c in doc["cells"]) and all(c["traps_none"] == 0 for c in doc["cells"])
            with open(os.path.join(tmp, "job", "asm", "k02_add_fwd.fast.s"), encoding="utf-8") as f:
                assert re.search(trap, f.read())


def test_a_trap_count_that_the_listing_does_not_bear_out_fails_for_both_architectures():
    for run_glob, trap in (("s7-run-*", r"\bud2\b"), ("s8-arm-run-*", r"\bbrk\s+#0x1\b")):
        src = _first_job(run_glob)
        # a trap instruction removed from a FAST listing, one invented in a NONE listing, and the same in the aligned listings
        for file, edit, word in (("k02_add_fwd.fast.s", lambda t: _drop_trap_line(t, trap), "traps_fast"),
                                 ("k04_rev.none.s", lambda t: _add_trap_line(t, trap), "traps_none"),
                                 ("k04_rev.fast_a64.s", lambda t: _drop_trap_line(t, trap), "aligned traps_fast"),
                                 ("k04_rev.none_a64.s", lambda t: _add_trap_line(t, trap), "aligned traps_none")):
            with tempfile.TemporaryDirectory() as tmp:
                job = _job_copy(tmp, src)
                _rewrite(os.path.join(job, "asm", file), edit)
                _, _, problems = _recount(job)
                assert problems and all(word in p and file in p for p in problems), (run_glob, file, problems)


def test_a_stored_trap_count_changed_in_results_json_fails_too():
    with tempfile.TemporaryDirectory() as tmp:
        job = _job_copy(tmp, _first_job("s7-run-*"))
        _rewrite(os.path.join(job, "results.json"), lambda t: t.replace('"traps_fast": 1', '"traps_fast": 2', 1))
        _, _, problems = _recount(job)
        assert problems and "stored traps_fast 2 differs from the 1 trap instructions" in problems[0], problems


def test_a_missing_listing_fails_but_the_two_early_runs_and_the_fixture_are_exempt():
    with tempfile.TemporaryDirectory() as tmp:
        job = _job_copy(tmp, _first_job("s7-run-*"))
        os.remove(os.path.join(job, "asm", "k05_stride2.fast.s"))
        _, _, problems = _recount(job)
        assert any("asm/k05_stride2.fast.s is missing" in p for p in problems), problems
        # a job folder with no asm/ at all is not exempt under another name ...
        shutil.rmtree(os.path.join(job, "asm"))
        _, n, problems = _recount(job)
        assert n == 0 and problems, problems
        # ... only the two runs named in NO_LISTING_RUNS (diffs only) and the SAMPLE fixture are
        assert check.NO_LISTING_RUNS == ("s1-run-38119008371", "s2-run-38119607308")
        for run_name in check.NO_LISTING_RUNS:
            early = os.path.join(tmp, run_name)
            os.makedirs(early)
            shutil.copyfile(os.path.join(job, "results.json"), os.path.join(early, "results.json"))
            _, n, problems = _recount(early)
            assert n == 0 and problems == [], (run_name, problems)
            assert not glob.glob(os.path.join(REPO, "results", run_name, "asm", "*.s")), f"{run_name} now keeps listings: drop it from NO_LISTING_RUNS"
    fixture = os.path.join(REPO, "results", "fixture.json")
    with open(fixture, encoding="utf-8") as f:
        doc = json.load(f)
    problems = []
    assert doc["sample"] is True and check.check_trap_counts(fixture, doc, problems) == 0 and problems == []


def test_check_results_fails_a_run_whose_listing_was_edited():
    """The whole per-file check, which also recomputes every interval (about 5 s): the only problem found is the trap count."""
    with tempfile.TemporaryDirectory() as tmp:
        job = _job_copy(tmp, _first_job("s8-arm-run-*"))
        _rewrite(os.path.join(job, "asm", "k04_rev.fast.s"), lambda t: _drop_trap_line(t, r"\bbrk\s+#0x1\b"))
        rc, out = run(check.check_results, os.path.join(job, "results.json"))
        fails = [ln for ln in out.splitlines() if "FAIL" in ln]
        assert rc is False and fails and all("k04_rev" in ln and "traps_fast" in ln for ln in fails), out


def test_a_missing_result_or_pool_is_a_failure_in_each_step_that_reads_it():
    real = check.REPO
    try:
        with tempfile.TemporaryDirectory() as tmp:
            check.REPO = tmp
            rc, out = run(check.check_holdout_result)
            assert rc is False and "FAIL results/s5-holdout/RESULT.md: missing" in out, out
            rc, out = run(check.check_dsweep)
            assert rc is False and "FAIL dsweep/analyze.py: missing" in out, out
            os.makedirs(os.path.join(tmp, "dsweep"))
            open(os.path.join(tmp, "dsweep", "analyze.py"), "w").close()
            rc, out = run(check.check_dsweep)
            assert rc is False and "no stored d-sweep" in out, out
    finally:
        check.REPO = real
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "results")
        os.makedirs(base)
        rc, out = run(check.check_pool_complete, base)  # the scratch copies of the other tests hold only the pools they are about
        assert rc is True and out == "", out
        rc, out = run(check.check_pool_complete, base, True)
        assert rc is False
        for pool in ("s6-pooled", "s7-pooled", "s8-arm-pooled", "s9-arm-b-pooled", "s9-x86-c-pooled", "s9-arm-ab-pooled", "s9-x86-ac-pooled"):
            assert f"FAIL results/{pool}/pooled.json: missing" in out, (pool, out)


def test_main_fails_on_a_repository_without_its_checkers_and_results():
    real_repo, real_tests = check.REPO, check.run_tests
    try:
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "harness"))
            shutil.copyfile(os.path.join(real_repo, "harness", "criteria.json"), os.path.join(tmp, "harness", "criteria.json"))
            check.REPO = tmp
            check.run_tests = lambda: True  # the tests of this repository are not what this checks
            rc, out = run(check.main)
    finally:
        check.REPO, check.run_tests = real_repo, real_tests
    assert rc == 1 and out.strip().endswith("CHECKS FAILED"), out
    assert "none yet" not in out and "ALL CHECKS PASSED" not in out
    for what in ("results/**/combined.json", "results/**/pooled.json", "results/s5-holdout/RESULT.md", "results/s7-pooled/pooled.json",
                 "results/mitigate-run-*", "corpus/run_tests.py", "ce-sweep/check.py", "tools/lostloops/run_tests.py",
                 "tools/lostloops-live/check.py", "layout-sweep/check.py", "robustness/check.py", "arm64/seeds.py and arm64/seed-sensitivity.json",
                 "replication/compare.py and replication/results.json", "dsweep/analyze.py", "pgo/check.py", "versions/check.py",
                 "environment/check.py", "realworld/check.py"):
        assert f"FAIL {what}: missing" in out, (what, out)
    assert out.count("FAIL ") >= 20


def test_every_script_main_runs_exists_and_no_step_prints_none_yet():
    src = inspect.getsource(check.main) + inspect.getsource(check.check_dsweep)
    assert "none yet" not in src
    seen = []
    for m in re.finditer(r'os\.path\.join\(REPO, ((?:"[^"]+"(?:, )?)+)\)', src):
        parts = re.findall(r'"([^"]+)"', m.group(1))
        if parts[-1].endswith((".py", ".json")) and not any("*" in p for p in parts):
            seen.append("/".join(parts))
            assert os.path.exists(os.path.join(REPO, *parts)), f"main() runs {'/'.join(parts)}, which is not in the repository"
    assert {"ce-sweep/check.py", "dsweep/analyze.py", "realworld/check.py", "robustness/check.py", "replication/results.json"} <= set(seen), seen
