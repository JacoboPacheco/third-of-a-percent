#!/usr/bin/env python3
"""Offline check of the layout sweep (no compiler, no runner). Passes when there are no results yet.

    python layout-sweep/check.py

1. layout-sweep/tests (pytest when installed, else a small built-in runner).
2. criteria.json parses, PLAN.md and wrap.cpp exist, the scripts compile, the workflow is valid YAML
   (when PyYAML is installed) and names the sweep script.
3. Every layout-sweep/results/**/results.json: criteria_sha256 matches criteria.json and every
   per-job ratio and 95 % interval is recomputed from the raw samples (harness/stats.py).
4. Every layout-sweep/results/**/analysis.json: recomputed from the results.json files it names
   (harness/pool.py, unchanged) and compared exactly with the stored document.
Exit code 0 only if every step passed.
"""
import glob
import hashlib
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


def close(a, b, tol=1e-9):
    """Equal, except floats may differ in the last digits (summation order differs between machines)."""
    if isinstance(a, float) or isinstance(b, float):
        return (isinstance(a, (int, float)) and isinstance(b, (int, float))
                and abs(a - b) <= tol * max(1.0, abs(a), abs(b)))
    if isinstance(a, dict):
        return isinstance(b, dict) and a.keys() == b.keys() and all(close(a[k], b[k], tol) for k in a)
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    return a == b


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
    try:
        crit, sha = an.load_criteria()
        print(f"criteria.json ok, sha256 {sha[:12]}")
    except Exception as e:
        print("criteria.json:", e)
        return False
    for f in ("PLAN.md", "wrap.cpp", "sweep.py", "analyze.py", "criteria.json"):
        if not os.path.exists(os.path.join(HERE, f)):
            print("missing", f)
            ok = False
    for f in ("sweep.py", "analyze.py", "check.py"):
        try:
            with open(os.path.join(HERE, f), encoding="utf-8") as fh:
                compile(fh.read(), f, "exec")
        except SyntaxError as e:
            print(f, e)
            ok = False
    wf = os.path.join(REPO, ".github", "workflows", "layout-sweep.yml")
    if not os.path.exists(wf):
        print("missing .github/workflows/layout-sweep.yml")
        return False
    text = open(wf, encoding="utf-8").read()
    if "layout-sweep/sweep.py" not in text or "layout-sweep/analyze.py" not in text:
        print("workflow does not call the sweep and analysis scripts")
        ok = False
    try:
        import yaml
        doc = yaml.safe_load(text)
        steps = doc["jobs"]["sweep"]["steps"]
        print(f"workflow yaml ok ({len(steps)} sweep steps)")
    except ImportError:
        print("workflow yaml not parsed (PyYAML not installed)")
    except Exception as e:
        print("workflow yaml:", e)
        ok = False
    return ok


def run_results():
    crit, sha = an.load_criteria()
    ok = True
    base = os.path.join(HERE, "results")
    jobs = sorted(glob.glob(os.path.join(base, "**", "results.json"), recursive=True))
    analyses = sorted(glob.glob(os.path.join(base, "**", "analysis.json"), recursive=True))
    if not jobs and not analyses:
        print("no results yet (nothing to recompute)")
        return True
    seen = {}
    for p in jobs:
        with open(p, "rb") as f:
            raw = f.read()
        digest = hashlib.sha256(raw).hexdigest()
        if digest in seen:  # an artifact download can carry a second copy of the same file
            print(f"{os.path.relpath(p, REPO)}: duplicate of {os.path.relpath(seen[digest], REPO)}, counted once")
            continue
        seen[digest] = p
        doc = json.loads(raw.decode("utf-8"))
        problems = an.verify_job(doc, crit, sha)
        print(f"{os.path.relpath(p, REPO)}: {'ok' if not problems else 'PROBLEMS'}")
        for pr in problems[:10]:
            print("   ", pr)
        ok = ok and not problems
    for p in analyses:
        with open(p, encoding="utf-8") as f:
            stored = json.load(f)
        base_dir = os.path.dirname(p)
        if not all(os.path.exists(os.path.join(base_dir, i["path"])) for i in stored["inputs"]):
            # the workflow's analysis artifact: a copy of analysis.json one level down, without the inputs
            print(f"{os.path.relpath(p, REPO)}: copy of the analysis artifact (inputs are not beside it); "
                  "the analysis.json next to the jobs is the one recomputed")
            continue
        entries, hashes_ok = [], True
        for i in stored["inputs"]:
            fp = os.path.join(base_dir, i["path"])
            with open(fp, encoding="utf-8") as f:
                entries.append((i["path"], json.load(f)))
            if "sha256" in i and i["sha256"] != an.file_sha256(fp):
                print(f"   input {i['path']} does not match its stored sha256")
                hashes_ok = False
        shas = [i["sha256"] for i in stored["inputs"] if "sha256" in i]
        if len(set(shas)) != len(shas):
            print("   the same results.json is listed twice")
            hashes_ok = False
        if os.path.basename(base_dir) == "pooled":  # the pooled file must hold every distinct results.json under results/
            every = {an.file_sha256(q) for q in an.find_results([base])}
            if set(shas) != every:
                print(f"   pooled inputs ({len(set(shas))}) are not all the distinct results.json files under results/ ({len(every)})")
                hashes_ok = False

        def strip(d):
            return {**d, "inputs": [{k: v for k, v in i.items() if k != "sha256"} for i in d["inputs"]]}
        fresh = json.loads(json.dumps(strip(an.analyse(entries, crit, sha)), sort_keys=True))
        same = hashes_ok and close(fresh, json.loads(json.dumps(strip(stored), sort_keys=True)))
        print(f"{os.path.relpath(p, REPO)}: {'recomputed, identical' if same else 'DIFFERS from the recomputation'}")
        ok = ok and same
    return ok


def main():
    results = [("tests", run_tests()), ("static", run_static()), ("results", run_results())]
    for name, r in results:
        print(f"{name}: {'ok' if r else 'FAILED'}")
    good = all(r for _, r in results)
    print("LAYOUT-SWEEP CHECKS PASSED" if good else "LAYOUT-SWEEP CHECKS FAILED")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
