#!/usr/bin/env python3
"""Offline check of the live test of tools/lostloops (tools/lostloops-live/PLAN.md); needs no compiler.

    python tools/lostloops-live/check.py

For every results/lostloops-live-*/lostloops-live-<project>/out-<project>/: the stored comparison.json
says pass, and recomputing compare.compare() from the stored report.json, the expected/<project>.json
and the root named in compile_commands.json gives the same lists, details, checks and totals.
Passes when no live result is stored yet. Exit code 0 only if every step passed.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import compare as cmp  # noqa: E402


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    outs = sorted(glob.glob(os.path.join(REPO, "results", "lostloops-live-*", "lostloops-live-*", "out-*")))
    if not outs:
        print("no live result stored yet (nothing to recompute)")
        return 0
    ok = True
    for out in outs:
        project = os.path.basename(out)[len("out-"):]
        name = os.path.relpath(out, REPO).replace("\\", "/")
        problems = []
        try:
            stored = load(os.path.join(out, "comparison.json"))
            report = load(os.path.join(out, "report", "report.json"))
            expected = load(os.path.join(HERE, "expected", project + ".json"))
            db = load(os.path.join(out, "compile_commands.json"))
            root = db[0]["directory"].replace("\\", "/")
            outside = [os.path.dirname(root)]
            fresh = cmp.compare(report, expected, root, outside)
            for k in ("lists", "details", "checks", "totals"):
                if fresh[k] != stored[k]:
                    problems.append(f"{k}: the stored comparison differs from the recomputed one")
            if not stored["pass"] or not fresh["pass"]:
                problems.append("the comparison with the census lists does not pass")
            if stored["commit"] != expected["commit"]:
                problems.append("comparison.json and expected/ name different commits")
        except Exception as e:  # a missing or malformed file is a failure, not a skip
            problems.append(f"cannot check: {e!r}")
        print(f"{name}: {'ok (recomputed, pass)' if not problems else 'PROBLEMS'}")
        for p in problems:
            print("   ", p)
        ok = ok and not problems
    print("LOSTLOOPS-LIVE CHECKS PASSED" if ok else "LOSTLOOPS-LIVE CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
