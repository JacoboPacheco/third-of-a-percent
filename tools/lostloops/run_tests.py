#!/usr/bin/env python3
"""Runs tools/lostloops/tests (pytest when installed, else a small built-in runner). No compiler needed:
    python tools/lostloops/run_tests.py"""
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


def main():
    try:
        import pytest
    except ImportError:
        pytest = None
    if pytest is not None:
        return 0 if pytest.main(["-q", "-p", "no:cacheprovider", TESTS]) == 0 else 1
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
    print("lostloops tests: %d passed, %d failed%s" % (passed, len(failed), (": " + ", ".join(failed)) if failed else ""))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
