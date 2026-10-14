#!/usr/bin/env python3
"""Runs corpus/tests (pytest when installed, else a small built-in runner), then the schema check of
every results/corpus-run-*/ folder. Plain Python is enough:  python corpus/run_tests.py"""
import glob
import importlib
import inspect
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(HERE, "tests")
sys.path.insert(0, TESTS)
sys.path.insert(0, HERE)


def run_tests():
    try:
        import pytest
    except ImportError:
        pytest = None
    if pytest is not None:
        return pytest.main(["-q", TESTS]) == 0
    passed, failed = 0, []
    for path in sorted(glob.glob(os.path.join(TESTS, "test_*.py"))):
        mod = importlib.import_module(os.path.basename(path)[:-3])
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if name.startswith("test_") and fn.__module__ == mod.__name__:
                try:
                    fn()
                    passed += 1
                except Exception:
                    failed.append("%s.%s" % (mod.__name__, name))
                    traceback.print_exc()
    print("corpus tests: %d passed, %d failed%s" % (passed, len(failed), (": " + ", ".join(failed)) if failed else ""))
    return not failed


def main():
    ok = run_tests()
    import schema
    dirs = sorted(glob.glob(os.path.join(os.path.dirname(HERE), "results", "corpus*-run-*")))
    if dirs:
        ok = schema.main(dirs) == 0 and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
