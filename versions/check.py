#!/usr/bin/env python3
"""Offline check of the versions column (no compiler, no runner). Passes when there are no results yet.

    python versions/check.py

1. versions/tests (pytest when installed, else a small built-in runner).
2. criteria.json parses and its reference to harness/criteria-v3.json (sha256) still holds; PLAN.md,
   probe.cpp, install.sh, run_version.py, analyze.py exist and the Python files compile; the workflow
   exists, names the scripts, and (when PyYAML is installed) parses.
3. Every versions/results/**/analysis.json is recomputed from the pooled-<N>.json beside it with
   analyze.py and compared exactly with the stored document.
Exit code 0 only if every step passed.
"""
import glob
import importlib
import inspect
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tests"))

import analyze as an  # noqa: E402


def run_tests():
    try:
        import pytest
    except ImportError:
        pytest = None
    if pytest is not None:
        print("== tests (pytest)")
        return pytest.main(["-q", os.path.join(HERE, "tests")]) == 0
    print("== tests (built-in runner; pytest is not installed)")
    passed, failed = 0, []
    for path in sorted(glob.glob(os.path.join(HERE, "tests", "test_*.py"))):
        mod = importlib.import_module(os.path.basename(path)[:-3])
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("test_") and fn.__module__ == mod.__name__:
                try:
                    fn()
                    passed += 1
                except Exception:
                    failed.append(f"{mod.__name__}.{name}")
                    traceback.print_exc()
    print(f"{passed} passed, {len(failed)} failed")
    return not failed


def run_static():
    ok = True
    mine, v3, problems = an.load_criteria()
    for p in problems:
        print("PROBLEM:", p)
        ok = False
    print(f"criteria.json ok; references {mine['reference']['file']} sha256 {mine['reference']['sha256'][:12]}")
    for f in ("PLAN.md", "probe.cpp", "install.sh", "run_version.py", "analyze.py", "criteria.json"):
        if not os.path.exists(os.path.join(HERE, f)):
            print("missing", f)
            ok = False
    for f in ("run_version.py", "analyze.py", "check.py"):
        try:
            with open(os.path.join(HERE, f), encoding="utf-8") as fh:
                compile(fh.read(), f, "exec")
        except SyntaxError as e:
            print(f, e)
            ok = False
    wf = os.path.join(REPO, ".github", "workflows", "versions.yml")
    if not os.path.exists(wf):
        print("missing .github/workflows/versions.yml")
        return False
    text = open(wf, encoding="utf-8").read()
    for needle in ("versions/run_version.py", "versions/analyze.py", "versions/install.sh", "harness/pool.py",
                   "workflow_dispatch"):
        if needle not in text:
            print("workflow does not mention", needle)
            ok = False
    try:
        import yaml
        doc = yaml.safe_load(text)
        print(f"workflow yaml ok (jobs: {', '.join(doc['jobs'])})")
    except ImportError:
        print("workflow yaml not parsed (PyYAML not installed)")
    except Exception as e:
        print("workflow yaml:", e)
        ok = False
    return ok


def run_results():
    ok = True
    analyses = sorted(glob.glob(os.path.join(HERE, "results", "**", "analysis.json"), recursive=True))
    if not analyses:
        print("no results yet (nothing to recompute)")
        return True
    for p in analyses:
        d = os.path.dirname(p)
        pooled, tcs = an.load_matrix(d)
        stored = json.load(open(p, encoding="utf-8"))
        base_path = os.path.join(REPO, stored["baseline_file"])
        base = json.load(open(base_path, encoding="utf-8")) if os.path.exists(base_path) else None
        fresh = json.loads(json.dumps(an.analyse(pooled, base, tcs)))
        same = fresh == stored
        print(f"{os.path.relpath(p, REPO)}: {'recomputed, identical' if same else 'DIFFERS from recomputation'}")
        ok = ok and same
    return ok


def main():
    results = [("tests", run_tests()), ("static", run_static()), ("results", run_results())]
    for name, ok in results:
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    print("VERSIONS CHECKS PASSED" if all(ok for _, ok in results) else "VERSIONS CHECKS FAILED")
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
