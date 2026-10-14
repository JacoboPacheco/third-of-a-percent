#!/usr/bin/env python3
"""Checks the real-program study without a compiler (realworld/PLAN.md, realworld/README.md).

Usage: python realworld/check.py [--pooled <realworld.json>] [--no-readme] [--no-tests]
Default pooled file: results/realworld-pooled/realworld.json (skipped with a note if it does not exist).

1. The pins in realworld/programs.json still equal the census pins (corpus/projects2.json) and the
   fmt pin (programs/fmt_format/fetch.sh).
2. Every input of the pooled file is present with the recorded sha256; every job is well formed:
   40 (or the recorded count) samples per side, ABBA order, checksums as recorded, the A/A copy
   byte-identical to NONE.
3. The pooled file is recomputed from the raw samples (realworld/pool_rw.py, which uses
   harness/pool.py's two-level bootstrap) and must match exactly, every ratio, interval and reading.
4. The tables in realworld/README.md between the "realworld:tables" markers equal what
   realworld/report.py renders from the pooled file.
5. The tests in realworld/tests.
Prints ALL REALWORLD CHECKS PASSED or the first failures, and exits non-zero on failure.
"""
import argparse
import json
import math
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
DEFAULT = os.path.join(REPO, "results", "realworld-pooled", "realworld.json")


class Fail(Exception):
    pass


def check_pins(errors):
    with open(os.path.join(HERE, "programs.json"), encoding="utf-8") as f:
        doc = json.load(f)
    with open(os.path.join(REPO, "corpus", "projects2.json"), encoding="utf-8") as f:
        census = {p["name"]: p for p in json.load(f)["projects"]}
    with open(os.path.join(REPO, "programs", "fmt_format", "fetch.sh"), encoding="utf-8") as f:
        fetch_sh = f.read()
    for name, p in doc["programs"].items():
        if p["pin_source"] == "corpus/projects2.json":
            c = census.get(p["census"])
            if c is None:
                errors.append(f"pins: {name}: census project {p['census']} not in corpus/projects2.json")
                continue
            for k in ("commit", "root", "version"):
                if p[k] != c[k]:
                    errors.append(f"pins: {name}: {k} {p[k]} differs from the census {c[k]}")
            if [(d["url"], d["sha256"], d["bytes"]) for d in p["downloads"]] != \
               [(d["url"], d["sha256"], d["bytes"]) for d in c["downloads"]]:
                errors.append(f"pins: {name}: downloads differ from the census")
        else:
            for d in p["downloads"]:
                if d["sha256"] not in fetch_sh or d["url"] not in fetch_sh:
                    errors.append(f"pins: {name}: {d['file']} sha256 or url not in programs/fmt_format/fetch.sh")
    rows = [r["row"] for r in doc["rows"]]
    if len(rows) != len(set(rows)):
        errors.append("programs.json: duplicate row names")
    for r in doc["rows"]:
        if r["program"] not in doc["programs"]:
            errors.append(f"programs.json: row {r['row']} names unknown program {r['program']}")
    return doc


def check_job(path, d, errors):
    reps = d["run"]["reps_per_side"]
    for r in d["rows"]:
        if r["sha256"]["none"] != r["sha256"]["none_copy"]:
            errors.append(f"{path}: {r['row']}: A/A copy sha256 differs from NONE")
        for p, x in r["pairs"].items():
            for k in ("a_ns", "b_ns", "a_wall_ns", "b_wall_ns"):
                if len(x[k]) != reps:
                    errors.append(f"{path}: {r['row']} {p}: {len(x[k])} samples in {k}, expected {reps}")
            want = "".join("AB" if k % 2 == 0 else "BA" for k in range(reps))
            if x["order"] != want:
                errors.append(f"{path}: {r['row']} {p}: order is not ABBA")
            exact = len(x["a_checksums"]) == 1 and x["a_checksums"] == x["b_checksums"]
            if exact != x["checksum_exact_match"]:
                errors.append(f"{path}: {r['row']} {p}: checksum_exact_match does not follow from the checksums")
            if any(v <= 0 for v in x["a_ns"] + x["b_ns"]):
                errors.append(f"{path}: {r['row']} {p}: a non-positive time")


def same_json(x, y, path=""):
    """Equal up to relative 1e-9 on floats (the last bits of log/exp/quantile differ between platforms); everything
    else must be equal. Returns the first difference or None."""
    if isinstance(x, dict) and isinstance(y, dict):
        if x.keys() != y.keys():
            return f"{path}: keys differ"
        for k in x:
            d = same_json(x[k], y[k], f"{path}/{k}")
            if d:
                return d
        return None
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return f"{path}: length differs"
        for i, (p, q) in enumerate(zip(x, y)):
            d = same_json(p, q, f"{path}[{i}]")
            if d:
                return d
        return None
    if isinstance(x, float) or isinstance(y, float):
        if x is None or y is None or isinstance(x, (str, bool)) or isinstance(y, (str, bool)):
            return f"{path}: {x!r} != {y!r}"
        if not math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12):
            return f"{path}: {x} != {y}"
        return None
    return None if x == y else f"{path}: {x!r} != {y!r}"


def check_pooled(path, errors):
    import pool_rw  # needs numpy (harness/pool.py)
    with open(path, encoding="utf-8") as f:
        stored = json.load(f)
    base = os.path.dirname(os.path.abspath(path))
    entries = []
    for inp in stored["inputs"]:
        p = os.path.join(base, inp["path"])
        if not os.path.exists(p):
            errors.append(f"pooled: input {inp['path']} is missing")
            continue
        if pool_rw.file_sha(p) != inp["sha256"]:
            errors.append(f"pooled: input {inp['path']} sha256 differs from the recorded one")
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        check_job(inp["path"], d, errors)
        entries.append((inp["path"], d))
    if errors:
        return stored
    ci = stored.get("context_inputs", {"builds": [], "profiles": []})
    again = pool_rw.pool_all(entries, base, ci["builds"], ci["profiles"])
    again = json.loads(json.dumps(again))
    if same_json(stored, again) is not None:
        for key in ("cpus", "all_runners", "inputs", "context", "runs"):
            d = same_json(stored.get(key), again.get(key), key)
            if d is not None:
                errors.append(f"pooled: '{key}' does not match its recomputation from the raw samples ({d})")
        if not errors:
            errors.append("pooled: the file does not match its recomputation")
    return stored


def check_readme(pooled_path, errors):
    import report
    readme = os.path.join(HERE, "README.md")
    if not os.path.exists(readme):
        errors.append("realworld/README.md is missing")
        return
    with open(readme, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"<!-- realworld:tables:start -->\n(.*?)<!-- realworld:tables:end -->", text, re.S)
    if not m:
        errors.append("README: the realworld:tables markers are missing")
        return
    want = report.render(pooled_path)
    if m.group(1) != want:
        errors.append("README: the tables differ from what realworld/report.py renders from the pooled file "
                      "(run: python realworld/report.py --write)")


def run_tests():
    suite = unittest.defaultTestLoader.discover(os.path.join(HERE, "tests"), top_level_dir=os.path.join(HERE, "tests"))
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    return res.wasSuccessful()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pooled", default=None)
    ap.add_argument("--no-readme", action="store_true")
    ap.add_argument("--no-tests", action="store_true")
    a = ap.parse_args(argv)
    errors = []
    print("== pins")
    check_pins(errors)
    pooled = a.pooled or DEFAULT
    if os.path.exists(pooled):
        print(f"== pooled file {os.path.relpath(pooled, REPO)}: inputs, jobs, recomputation")
        check_pooled(pooled, errors)
        if not a.no_readme and not errors:
            print("== README tables")
            check_readme(pooled, errors)
    else:
        print(f"== no pooled file at {os.path.relpath(pooled, REPO)} (nothing timed yet): skipped")
    ok_tests = True
    if not a.no_tests:
        print("== tests (realworld/tests)")
        ok_tests = run_tests()
    for e in errors[:30]:
        print("FAIL", e)
    if errors or not ok_tests:
        print(f"REALWORLD CHECKS FAILED ({len(errors)} problems{', tests failed' if not ok_tests else ''})")
        return 1
    print("ALL REALWORLD CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
