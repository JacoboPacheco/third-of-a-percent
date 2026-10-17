#!/usr/bin/env python3
"""Offline check of robustness/ (no compiler, numpy only).

    python robustness/check.py [--quick]

1. robustness/tests (pytest when installed, otherwise a small built-in runner).
2. Recomputes the whole analysis from the stored raw samples and demands: method (a) reproduces the stored pooled.json
   (self-test), results.json equals the recomputation, and the tables block of report.md equals the tables generated
   from it. --quick skips steps 2 and 3.
3. The same for the Arm pool (analyze.py --arm): self-test, results-arm.json and the second tables block of report.md.
Skips cleanly (exit 0, says SKIP) when the stored results are not present.
"""
import importlib
import inspect
import json
import math
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tests"))

import analyze  # noqa: E402

BEGIN, END = "<!-- tables:begin -->", "<!-- tables:end -->"


def run_tests():
    try:
        import pytest  # noqa: F401
        import subprocess
        return subprocess.call([sys.executable, "-m", "pytest", "-q", os.path.join(HERE, "tests")]) == 0
    except ImportError:
        pass
    mod = importlib.import_module("test_analyze")
    bad = 0
    for name, fn in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("test_"):
            try:
                fn()
                print(f"  ok   {name}")
            except Exception:
                bad += 1
                print(f"  FAIL {name}\n{traceback.format_exc()}")
    return bad == 0


def same(x, y, path=""):
    """Equal up to relative 1e-9 on floats; returns the first difference or None."""
    if isinstance(x, dict) and isinstance(y, dict):
        if x.keys() != y.keys():
            return f"{path}: keys differ"
        for k in x:
            d = same(x[k], y[k], f"{path}/{k}")
            if d:
                return d
        return None
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return f"{path}: length differs"
        for i, (p, q) in enumerate(zip(x, y)):
            d = same(p, q, f"{path}[{i}]")
            if d:
                return d
        return None
    if isinstance(x, float) or isinstance(y, float):
        if x is None or y is None or not math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12):
            return f"{path}: {x} != {y}"
        return None
    return None if x == y else f"{path}: {x!r} != {y!r}"


def main(argv):
    ok = True
    print("[1] tests")
    ok &= run_tests()
    if "--quick" in argv:
        print("[2] skipped (--quick)")
        print("ROBUSTNESS CHECKS " + ("PASSED (quick)" if ok else "FAILED"))
        return 0 if ok else 1
    print("[2] recomputation from the stored raw samples")
    out = analyze.run_all()
    if not out["datasets"]:
        print("SKIP: the stored pooled results or their job files are not present")
        print("ROBUSTNESS CHECKS " + ("PASSED (tests only)" if ok else "FAILED"))
        return 0 if ok else 1
    for name, ds in out["datasets"].items():
        st = ds["self_test"]
        good = st["forms_equal"] and st["max_rel_diff"] <= 1e-12
        print(f"  self-test {name}: {st['exact']}/{st['numbers_checked']} exact, max rel diff {st['max_rel_diff']:.1e}, "
              f"forms equal {st['forms_equal']} -> {'ok' if good else 'FAIL'}")
        ok &= good
    rj = os.path.join(HERE, "results.json")
    if not os.path.exists(rj):
        print("  FAIL robustness/results.json missing")
        ok = False
    else:
        with open(rj, encoding="utf-8") as f:
            stored = json.load(f)
        d = same(stored, json.loads(json.dumps(out)))
        print("  results.json equals the recomputation" if d is None else f"  FAIL results.json: {d}")
        ok &= d is None
    rp = os.path.join(HERE, "report.md")
    if not os.path.exists(rp):
        print("  FAIL robustness/report.md missing")
        ok = False
    else:
        with open(rp, encoding="utf-8") as f:
            text = f.read()
        if BEGIN not in text or END not in text:
            print("  FAIL report.md has no tables block")
            ok = False
        else:
            block = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
            want = analyze.tables_md(out).strip()
            if block == want:
                print("  report.md tables equal the recomputed tables")
            else:
                print("  FAIL report.md tables differ from the recomputed tables (run analyze.py --report)")
                ok = False
    ok &= check_arm()
    print("ROBUSTNESS CHECKS " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def check_arm():
    """[3] The Arm pool (analyze.py --arm): self-test of method (a), results-arm.json and the second tables block of report.md
    equal the recomputation. Skips when the Arm outputs or the Arm pool are not there."""
    print("[3] the Arm pool (s8arm), recomputed from the stored raw samples")
    rj = os.path.join(HERE, analyze.ARM_RESULTS)
    if not os.path.exists(rj):
        print("  SKIP: no robustness/" + analyze.ARM_RESULTS)
        return True
    out = analyze.run_all(analyze.ARM_DATASETS)
    if not out["datasets"]:
        print("  SKIP: the Arm pool or its job files are not present")
        return True
    ok = True
    for name, ds in out["datasets"].items():
        st = ds["self_test"]
        good = st["forms_equal"] and st["max_rel_diff"] <= 1e-12
        print(f"  self-test {name}: {st['exact']}/{st['numbers_checked']} exact, max rel diff {st['max_rel_diff']:.1e}, "
              f"forms equal {st['forms_equal']} -> {'ok' if good else 'FAIL'}")
        ok &= good
    with open(rj, encoding="utf-8") as f:
        stored = json.load(f)
    d = same(stored, json.loads(json.dumps(out)))
    print("  results-arm.json equals the recomputation" if d is None else f"  FAIL results-arm.json: {d}")
    ok &= d is None
    with open(os.path.join(HERE, "report.md"), encoding="utf-8") as f:
        text = f.read()
    b, e = analyze.ARM_MARKS
    if b not in text or e not in text:
        print("  FAIL report.md has no Arm tables block")
        return False
    block = text.split(b, 1)[1].split(e, 1)[0].strip()
    if block == analyze.arm_tables_md(out).strip():
        print("  report.md Arm tables equal the recomputed tables")
    else:
        print("  FAIL report.md Arm tables differ from the recomputed tables (run analyze.py --arm --report)")
        ok = False
    return ok


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
