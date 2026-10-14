#!/usr/bin/env python3
"""Offline checks of the PGO column (pgo/PLAN.md); needs no compiler and no results.

python pgo/check.py [--pooled results/pgo-pooled/pgo.json] [--baseline results/realworld-pooled/realworld.json]
                    [--no-tests]

Always: the plan exists and says what the rules need; the build script imports and its PGO builds
register next to realworld/build.py's; the workflow has both modes and uses the unchanged realworld
measure script; the report is what analyze.py renders. With a pooled PGO file: every input job
carries the PGO mark and passes realworld/check.py's job checks, the file matches its recomputation
from the raw samples, and pgo/report.md is the rendering of it. Then the unit tests.
"""
import argparse
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "realworld"))
sys.path.insert(0, HERE)

DEFAULT = os.path.join(REPO, "results", "pgo-pooled", "pgo.json")
WORKFLOW = os.path.join(REPO, ".github", "workflows", "pgo.yml")


def check_files(errors):
    plan = os.path.join(HERE, "PLAN.md")
    if not os.path.exists(plan):
        errors.append("pgo/PLAN.md is missing")
    else:
        with open(plan, encoding="utf-8") as f:
            text = f.read()
        for need in ("Rules for the claims", "Training input equals test input", "What the result is compared to",
                     "Expectations (written before any build or run"):
            if need not in text:
                errors.append(f"PLAN.md lacks the section or sentence: {need}")
    if not os.path.exists(WORKFLOW):
        errors.append(".github/workflows/pgo.yml is missing")
        return
    with open(WORKFLOW, encoding="utf-8") as f:
        wf = f.read()
    for need in ("workflow_dispatch", "inputs.mode == 'build'", "inputs.mode == 'measure'", "pgo/build_pgo.py",
                 "realworld/measure.py", "pgo/tag_job.py", "pgo/pool_pgo.py", "pgo/check.py", "llvm-profdata", "libclang-rt-18-dev"):
        if need not in wf:
            errors.append(f"pgo.yml does not mention {need}")
    if re.search(r"(?m)^\s*-?\s*(run|uses): .*pgo.*upload.*", wf):
        errors.append("pgo.yml: suspicious line")


def check_build_script(errors):
    import build_pgo
    import build
    import measure
    build_pgo.register_builds("none", "/x.profdata")
    build_pgo.register_builds("fast", "/x.profdata")
    for m in ("none", "fast"):
        for k in (f"{m}_gen", f"{m}_pgo", f"{m}_pgo_a64"):
            if k not in build.BUILDS:
                errors.append(f"build_pgo does not register {k}")
    if "-fprofile-instr-generate" not in build.BUILDS["none_gen"] or not any(
            f.startswith("-fprofile-instr-use=") for f in build.BUILDS["fast_pgo"]):
        errors.append("build_pgo: the instrument/use flags are wrong")
    if build.ALIGN not in build.BUILDS["fast_pgo_a64"] or build.ALIGN in build.BUILDS["fast_pgo"]:
        errors.append("build_pgo: only the _a64 build may carry -falign-loops")
    if build.NONE not in build.BUILDS["none_pgo"] or build.FAST not in build.BUILDS["fast_pgo"]:
        errors.append("build_pgo: a PGO build carries the wrong hardening mode")
    # the binary names measure.py reads must be the ones the build script writes
    wanted = {n for p in measure.PAIRS.values() for n in p if n != "none_copy"}
    produced = {"none", "fast", "none_a64", "fast_a64"}
    if not wanted <= produced:
        errors.append(f"measure.py reads binaries the PGO build does not write: {sorted(wanted - produced)}")
    with open(os.path.join(REPO, "realworld", "programs.json"), encoding="utf-8") as f:
        doc = json.load(f)
    for r in doc["rows"]:
        if r["program"] not in doc["programs"]:
            errors.append(f"row {r['row']} names an unknown program")


def _load_rw_check():
    import importlib.util
    spec = importlib.util.spec_from_file_location("rw_check", os.path.join(REPO, "realworld", "check.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_pooled(path, errors):
    import pool_pgo
    rwcheck = _load_rw_check()
    with open(path, encoding="utf-8") as f:
        stored = json.load(f)
    if stored.get("kind") != "pgo-pooled":
        errors.append("pooled: kind is not pgo-pooled")
        return stored
    base = os.path.dirname(os.path.abspath(path))
    entries = []
    for inp in stored["inputs"]:
        p = os.path.join(base, inp["path"])
        if not os.path.exists(p):
            errors.append(f"pooled: input {inp['path']} is missing")
            continue
        if pool_pgo.pool_rw.file_sha(p) != inp["sha256"]:
            errors.append(f"pooled: input {inp['path']} sha256 differs from the recorded one")
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if "pgo" not in d:
            errors.append(f"pooled: input {inp['path']} has no PGO mark")
        rwcheck.check_job(inp["path"], d, errors)
        entries.append((inp["path"], d))
    if errors:
        return stored
    again = pool_pgo.pool_doc(entries, base, stored.get("pgo_context_inputs", []))
    again = json.loads(json.dumps(again))
    if rwcheck.same_json(stored, again) is not None:
        for key in ("cpus", "all_runners", "inputs", "runs", "pgo_context", "pgo_binaries"):
            d = rwcheck.same_json(stored.get(key), again.get(key), key)
            if d is not None:
                errors.append(f"pooled: '{key}' does not match its recomputation from the raw samples ({d})")
        if not errors:
            errors.append("pooled: the file does not match its recomputation")
    return stored


def check_report(pooled, baseline, errors):
    import analyze
    report = os.path.join(HERE, "report.md")
    if not os.path.exists(report):
        errors.append("pgo/report.md is missing (run: python pgo/analyze.py --write)")
        return
    want = analyze.render(analyze.load(pooled), analyze.load(baseline))
    with open(report, encoding="utf-8") as f:
        have = f.read()
    if have != want:
        errors.append("pgo/report.md differs from what analyze.py renders (run: python pgo/analyze.py --write)")


def run_tests():
    suite = unittest.defaultTestLoader.discover(os.path.join(HERE, "tests"), top_level_dir=os.path.join(HERE, "tests"))
    return unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pooled", default=DEFAULT)
    ap.add_argument("--baseline", default=os.path.join(REPO, "results", "realworld-pooled", "realworld.json"))
    ap.add_argument("--no-tests", action="store_true")
    ap.add_argument("--no-report", action="store_true")
    a = ap.parse_args(argv)
    errors = []
    print("== plan, workflow, build script")
    check_files(errors)
    check_build_script(errors)
    if os.path.exists(a.pooled):
        print(f"== pooled file {os.path.relpath(a.pooled, REPO)}: marks, jobs, recomputation")
        check_pooled(a.pooled, errors)
    else:
        print(f"== no pooled file at {os.path.relpath(a.pooled, REPO)} (nothing timed yet): skipped")
    if not a.no_report and not errors:
        print("== report")
        check_report(a.pooled, a.baseline, errors)
    ok = True
    if not a.no_tests:
        print("== tests (pgo/tests)")
        ok = run_tests()
    for e in errors[:30]:
        print("FAIL", e)
    if errors or not ok:
        print(f"PGO CHECKS FAILED ({len(errors)} problems{', tests failed' if not ok else ''})")
        return 1
    print("ALL PGO CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
