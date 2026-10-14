#!/usr/bin/env python3
"""Offline check of the Compiler Explorer sweep. No network.

    python ce-sweep/check.py

1. the unit tests in test_cesweep.py (pytest when installed, else a small built-in runner);
2. source.cpp is exactly the 8 loop functions of kernels/ as they are now;
3. every build of the matrix has a cached answer whose stored request hash equals the hash of the
   request rebuilt from today's source and flags (so the cache answers exactly this request);
4. results.json has the expected schema and every cell is internally consistent;
5. results.json and the README matrix equal a fresh recomputation from the cache;
6. the control: clang 18.1 x86-64 -O2 loses exactly reverse, stride-2 and matmul.
Exit 0 when all pass.
"""
import importlib
import inspect
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_results  # noqa: E402
import cesweep as cs  # noqa: E402

CELL_KEYS = {"compiler_id", "family", "version", "target", "opt", "kernel", "macro_none", "macro_hardened",
             "flags_none", "flags_hardened", "compiled", "none", "hardened", "lost", "request_sha256_none",
             "request_sha256_hardened", "cache_none", "cache_hardened"}
SIDE_KEYS = {"vectorized", "width", "interleave", "vector_bytes", "remarks", "asm"}
ROW_KEYS = {"compiler_id", "family", "version", "target", "opt", "macro_hardened", "vectorized_none",
            "vectorized_hardened", "lost", "unknown", "remark_asm_disagree", "check_sites_none",
            "check_sites_hardened", "macro_effective"}


def run_tests():
    try:
        import pytest
    except ImportError:
        pytest = None
    if pytest is not None:
        return pytest.main(["-q", "-p", "no:cacheprovider", os.path.join(HERE, "test_cesweep.py")]) == 0
    mod = importlib.import_module("test_cesweep")
    failed = 0
    names = [n for n, f in inspect.getmembers(mod, inspect.isfunction) if n.startswith("test_")]
    for n in names:
        try:
            getattr(mod, n)()
        except Exception:
            failed += 1
            print("FAIL", n)
            traceback.print_exc()
    print("   %d tests, %d failed" % (len(names), failed))
    return failed == 0


def check_schema(doc, problems):
    for k in ("schema", "source_sha256", "loop_lines", "control", "counts", "matrix", "builds", "cells",
              "definition_lost"):
        if k not in doc:
            problems.append("results.json: missing %s" % k)
    if doc.get("schema") != "ce-sweep/1":
        problems.append("results.json: schema is not ce-sweep/1")
    if len(doc.get("builds", [])) != len(cs.matrix()):
        problems.append("results.json: %d builds, the matrix has %d" % (len(doc.get("builds", [])), len(cs.matrix())))
    if len(doc.get("cells", [])) != len(cs.matrix()) // 2 * len(cs.KERNELS):
        problems.append("results.json: wrong number of cells")
    for c in doc.get("cells", []):
        where = "%s %s %s %s" % (c.get("compiler_id"), c.get("target"), c.get("opt"), c.get("kernel"))
        if set(c) != CELL_KEYS:
            problems.append("cell %s: keys %s" % (where, sorted(set(c) ^ CELL_KEYS)))
            continue
        if c["kernel"] not in cs.KERNELS:
            problems.append("cell %s: unknown kernel" % where)
        for side in ("none", "hardened"):
            s = c[side]
            if s is not None and set(s) != SIDE_KEYS:
                problems.append("cell %s: %s keys" % (where, side))
        if len(c["request_sha256_none"]) != 64 or len(c["request_sha256_hardened"]) != 64:
            problems.append("cell %s: request hash missing" % where)
        for f in (c["cache_none"], c["cache_hardened"]):
            if not os.path.exists(os.path.join(HERE, "cache", f)):
                problems.append("cell %s: cache file %s missing" % (where, f))
        if c["lost"] is not None:
            want = bool(c["none"]["vectorized"]) and not c["hardened"]["vectorized"]
            if c["lost"] != want:
                problems.append("cell %s: lost=%s contradicts its own vectorized flags" % (where, c["lost"]))
    for r in doc.get("matrix", []):
        if set(r) != ROW_KEYS:
            problems.append("row %s: keys" % r.get("compiler_id"))


def main():
    ok = True
    print("== ce-sweep unit tests")
    sys.stdout.flush()
    ok &= run_tests()
    problems = []
    print("== ce-sweep source, cache, schema, recomputation, control (offline)")
    src = cs.build_source()
    with open(os.path.join(HERE, "source.cpp"), encoding="utf-8") as f:
        if f.read() != src:
            problems.append("source.cpp is not the current kernels/ loop functions (rerun sweep.py?)")
    for b in cs.matrix():
        p = os.path.join(HERE, "cache", cs.cache_name(b))
        if not os.path.exists(p):
            problems.append("no cached answer for %s" % cs.cache_name(b))
            continue
        rec = cs.load_cache(p)
        if rec["request_sha256"] != cs.request_sha(b["compiler_id"], cs.request_body(src, b["flags"])):
            problems.append("%s: cached request hash differs from today's request" % cs.cache_name(b))
        if rec["build"] != b:
            problems.append("%s: cached build description differs from the matrix" % cs.cache_name(b))
    with open(os.path.join(HERE, "results.json"), encoding="utf-8") as f:
        doc = json.load(f)
    check_schema(doc, problems)
    sys.argv = [sys.argv[0], "--check"]
    if build_results.main() != 0:
        problems.append("results.json or the README matrix is stale (python ce-sweep/build_results.py)")
    ctl = doc.get("control", {})
    if not ctl.get("ok") or ctl.get("observed_lost") != cs.CONTROL_LOST:
        problems.append("control failed: clang 18.1 x86-64 -O2 lost %s, expected %s" %
                        (ctl.get("observed_lost"), cs.CONTROL_LOST))
    for p in problems:
        print("   PROBLEM:", p)
    if not problems:
        print("   %d builds, %d cells, %d matrix rows; control reproduced (%s)" %
              (len(doc["builds"]), len(doc["cells"]), len(doc["matrix"]), ", ".join(ctl["observed_lost"])))
    ok &= not problems
    print("CE-SWEEP CHECK PASSED" if ok else "CE-SWEEP CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
