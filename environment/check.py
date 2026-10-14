#!/usr/bin/env python3
"""Offline check of the environment column (no compiler, no runner). Passes when there are no results yet.

    python environment/check.py

1. environment/tests (pytest when installed, else a small built-in runner).
2. PLAN.md, runner.py, envlib.py, analyze.py exist and compile; the thresholds in analyze.py equal the ones
   written in PLAN.md and in harness/criteria-v3.json; the workflow exists, names the scripts, and (when
   PyYAML is installed) parses.
3. Every environment/results/**/analysis.json is recomputed from the environment.json files beside it
   and compared exactly with the stored document.
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
    for f in ("PLAN.md", "runner.py", "envlib.py", "analyze.py", "check.py"):
        if not os.path.exists(os.path.join(HERE, f)):
            print("missing", f)
            ok = False
    for f in ("runner.py", "envlib.py", "analyze.py", "check.py"):
        try:
            with open(os.path.join(HERE, f), encoding="utf-8") as fh:
                compile(fh.read(), f, "exec")
        except SyntaxError as e:
            print(f, e)
            ok = False
    plan = open(os.path.join(HERE, "PLAN.md"), encoding="utf-8").read().replace("`", "")
    for needle in ("above 0.5 %", "above 1 %", ">= 1.5", "<= 1.02", "at least one jiffy"):
        if needle not in plan:
            print("PLAN.md no longer states:", needle)
            ok = False
    if (an.STEAL_LARGE_SHARE, an.DRIFT_LARGE_PCT, an.LOST_CI_LO_MIN, an.FORWARD_POINT_MAX) != (0.005, 1.0, 1.5, 1.02):
        print("analyze.py thresholds differ from PLAN.md")
        ok = False
    try:
        crit = json.load(open(os.path.join(REPO, "harness", "criteria-v3.json"), encoding="utf-8"))["verdict"]
        if (crit["lost_ci_lo_min_ratio"], crit["forward_point_max_ratio"]) != (an.LOST_CI_LO_MIN, an.FORWARD_POINT_MAX):
            print("analyze.py class thresholds differ from harness/criteria-v3.json")
            ok = False
    except (OSError, KeyError) as e:
        print("could not read harness/criteria-v3.json:", e)
        ok = False
    wf = os.path.join(REPO, ".github", "workflows", "environment.yml")
    if not os.path.exists(wf):
        print("missing .github/workflows/environment.yml")
        return False
    text = open(wf, encoding="utf-8").read()
    for needle in ("environment/runner.py", "environment/analyze.py", "environment/check.py", "workflow_dispatch"):
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
        docs = an.load_matrix(os.path.dirname(p))
        stored = json.load(open(p, encoding="utf-8"))
        fresh = json.loads(json.dumps(an.analyse(docs)))
        same = fresh == stored
        print(f"{os.path.relpath(p, REPO)}: {'recomputed, identical' if same else 'DIFFERS from recomputation'}")
        ok = ok and same
    return ok


def main():
    results = [("tests", run_tests()), ("static", run_static()), ("results", run_results())]
    for name, ok in results:
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    good = all(ok for _, ok in results)
    print("ENVIRONMENT CHECKS PASSED" if good else "ENVIRONMENT CHECKS FAILED")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
