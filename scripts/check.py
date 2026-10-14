#!/usr/bin/env python3
"""The one command that verifies everything that can be verified without a compiler.

    python scripts/check.py [more results.json ...]   (extra files, e.g. a fresh run's out/results.json)

1. The tests in tests/ (with pytest when it is installed; otherwise a small built-in runner that
   calls every test_* function, so plain Python is enough).
2. The schema-1 check of results/fixture.json and of every results.json under results/.
3. For each of those files: every ratio and 95 % interval recomputed from the raw samples with
   harness/stats.py must equal the stored one, criteria_sha256 must match harness/criteria.json,
   and the verdict recomputed by harness/verdict.py must equal the stored verdict. Each program row's
   consistent_with_at_most_pct must equal harness/programs.py's rule and never sit below its A/A floor
   (real runs; the SAMPLE fixture's made-up rows are exempt).
   Stage S3: a run that names harness/criteria-v2.json in run.criteria_file is checked against that
   file's hash and rules; its loops-aligned pairs, layout A/A pairs and verdict_v1 (criteria.json)
   are recomputed too, and every combined.json (harness/combine.py) is recomputed from the
   results.json files beside it.
   Stage S4-measurement (harness/criteria-v3.json): the raw A/A and NOVEC samples a v3 results.json
   carries are recomputed too, and every pooled.json (harness/pool.py: every job of a CPU model pooled,
   two-level bootstrap, the per-CPU verdicts) is validated, recomputed from the results.json files it
   names and compared, then a sample of its numbers is recomputed independently by
   harness/pool_check.py (plain Python, its own bootstrap, no import of pool.py or stats.py).
   The newer-toolchain column (versions/check.py) and the environment column (environment/check.py) run as their own steps and skip cleanly when their results are absent.
4. The page: scripts/check_site.py --quick (site/data/ equals a fresh build, every number on the page is in
   the data, drawers open, no console errors, no horizontal scroll at 390 px, screenshots).
Exit code 0 only if every step passed.
"""
import glob
import hashlib
import importlib
import inspect
import json
import math
import os
import sys
import traceback

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "tests"))

import combine  # noqa: E402
import programs  # noqa: E402
import schema  # noqa: E402
import stats  # noqa: E402
import verdict  # noqa: E402


def run_tests():
    try:
        import pytest  # noqa: F401
    except ImportError:
        pytest = None
    if pytest is not None:
        print("== tests (pytest)")
        return pytest.main(["-q", os.path.join(REPO, "tests")]) == 0
    print("== tests (built-in runner; pytest is not installed)")
    passed, failed = 0, []
    for path in sorted(glob.glob(os.path.join(REPO, "tests", "test_*.py"))):
        mod = importlib.import_module(os.path.basename(path)[:-3])
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if not name.startswith("test_") or fn.__module__ != mod.__name__:
                continue
            try:
                fn()
                passed += 1
            except Exception:
                failed.append(f"{mod.__name__}.{name}")
                traceback.print_exc()
    print(f"   {passed} passed, {len(failed)} failed" + (": " + ", ".join(failed) if failed else ""))
    return not failed


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-15)


def file_sha(rel_path):
    with open(os.path.join(REPO, rel_path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def same_pair(stored, a_ns, b_ns):
    s = stats.summarize(a_ns, b_ns)
    return close(s["ratio"], stored["ratio"]) and all(close(x, y) for x, y in zip(s["ci95"], stored["ci95"]))


def check_v2_parts(doc, problems):
    """The stage-S3 keys: present where criteria-v2 needs them, and every number recomputed."""
    v2 = doc["run"].get("criteria_file") == "harness/criteria-v2.json"
    for c in doc["cells"]:
        if "aligned" in c:
            if not same_pair(c["aligned"], c["aligned"]["none_ns"], c["aligned"]["fast_ns"]):
                problems.append(f"{c['cell_id']}: stored aligned ratio/ci95 differ from the recomputed ones")
        elif v2:
            problems.append(f"{c['cell_id']}: a criteria-v2 run without the aligned pair")
        if v2 and "loops" not in c:
            problems.append(f"{c['cell_id']}: a criteria-v2 run without the loop placement record")
    for p in doc["programs"]:
        if "aligned" in p:
            al = p["aligned"]
            if not same_pair(al, al["none_ns"], al["fast_ns"]):
                problems.append(f"program {p['name']}: stored aligned ratio/ci95 differ from the recomputed ones")
            if not doc["sample"] and al["consistent_with_at_most_pct"] is not None:
                bound = programs.consistent_with_at_most_pct(al["ci95"], p["aa_half_width_pct"])
                if not close(bound, al["consistent_with_at_most_pct"]):
                    problems.append(f"program {p['name']}: aligned consistent_with_at_most_pct differs from {bound}")
        elif v2:
            problems.append(f"program {p['name']}: a criteria-v2 run without the aligned pair")
    for la in doc["controls"].get("layout_aa", []):
        s = stats.summarize(la["a_ns"], la["b_ns"])
        if not (same_pair(la, la["a_ns"], la["b_ns"]) and close(s["half_width_pct"], la["half_width_pct"])):
            problems.append(f"layout A/A {la['id']}: stored numbers differ from the recomputed ones")
    if v2 and "layout_aa" not in doc["controls"]:
        problems.append("a criteria-v2 run without controls.layout_aa")
    aa = doc["controls"]["aa"]
    if "a_ns" in aa:
        s = stats.summarize(aa["a_ns"], aa["b_ns"])
        if not (same_pair(aa, aa["a_ns"], aa["b_ns"]) and close(s["half_width_pct"], aa["half_width_pct"])):
            problems.append("controls.aa: stored numbers differ from the ones recomputed from a_ns, b_ns")
    for p in doc["controls"]["positive"]:
        if "none_ns" in p:
            s = stats.summarize(p["none_ns"], p["novec_ns"])
            if not (close(s["ratio"], p["novec_ratio"]) and all(close(x, y) for x, y in zip(s["ci95"], p["ci95"]))):
                problems.append(f"positive {p['cell_id']}: stored numbers differ from the recomputed ones")
    if doc["run"].get("criteria_file") == "harness/criteria-v3.json":
        if "a_ns" not in aa or any("none_ns" not in p for p in doc["controls"]["positive"]):
            problems.append("a criteria-v3 run without the raw A/A or NOVEC samples")
    if v2 and "verdict_v1" not in doc:
        problems.append("a criteria-v2 run without verdict_v1")
    if "verdict_v1" in doc:
        v1 = verdict.compute(doc, verdict.load_criteria(os.path.join(REPO, verdict.V1_FILE)))
        if not verdict.same_verdict(doc["verdict_v1"], v1, doc):  # v1/v2 runs: the stored line is historical
            problems.append(f"stored verdict_v1 differs from the recomputed one: {v1}")


def check_combined(path):
    name = os.path.relpath(path, REPO).replace("\\", "/")
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        schema.validate_combined(doc)
    except Exception as e:
        print(f"   FAIL {name}: schema: {e}")
        return False
    crit_file = doc["criteria_file"]
    problems = []
    if doc["criteria_sha256"] != file_sha(crit_file):
        problems.append(f"criteria_sha256 does not match {crit_file}")
    entries = combine.load_dir(os.path.dirname(path))
    if sorted(e[0] for e in entries) != sorted(f["path"] for f in doc["files"]):
        problems.append("the results.json files beside it are not the ones it lists")
    again = combine.combine(entries, verdict.load_criteria(os.path.join(REPO, crit_file)), doc["criteria_sha256"])
    # combined.json is a criteria-v2 (S3) record: its page line predates the Oct 12 MAP wording, so the
    # line is left out of the comparison; the form, N, X, why and every per-file entry must match
    strip = lambda d: {**d, "verdict": {k: x for k, x in d["verdict"].items() if k != "line"}}  # noqa: E731
    if strip(again) != strip(doc):
        problems.append(f"stored combined verdict differs from the recomputed one: {again['verdict']}")
    for pr in problems:
        print(f"   FAIL {name}: {pr}")
    if not problems:
        print(f"   ok   {name} ({len(doc['files'])} files, {len(doc['cpus'])} CPU models): "
              f"{doc['verdict']['form']}: {doc['verdict']['line']}")
    return not problems


def same_doc(a, b, where="", out=None):
    """Deep comparison with floats equal to 1e-9 relative; returns the first few differing paths."""
    out = [] if out is None else out
    if len(out) > 5:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            out.append(f"{where}: keys {sorted(set(a) ^ set(b))}")
        for k in set(a) & set(b):
            same_doc(a[k], b[k], f"{where}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{where}: length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            same_doc(x, y, f"{where}[{i}]", out)
    elif isinstance(a, float) or isinstance(b, float):
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float))
                and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)):
            out.append(f"{where}: {a!r} vs {b!r}")
    elif a != b:
        out.append(f"{where}: {a!r} vs {b!r}")
    return out


def check_holdout_result():
    """results/s5-holdout/RESULT.md: each CPU row's verdicts, job counts and lost-loop numbers match the two pooled.json files."""
    import statistics
    base = os.path.join(REPO, "results")
    path = os.path.join(base, "s5-holdout", "RESULT.md")
    if not os.path.exists(path):
        return True
    with open(path, encoding="utf-8") as f:
        text = f.read()
    rows = {ln.split("|")[1].strip(): ln for ln in text.splitlines() if ln.startswith("| ") and "EPYC" in ln or "Xeon" in ln and ln.startswith("| ")}
    problems = []
    for tag, rel in (("original", "s4-pooled"), ("holdout", "s5-holdout")):
        with open(os.path.join(base, rel, "pooled.json"), encoding="utf-8") as f:
            doc = json.load(f)
        for c in doc["cpus"]:
            name = c["cpu_model"]
            key = "Intel Xeon 8573C" if "8573C" in name else name.replace("-Core Processor", "").replace(" 64", "").replace(" 80", "").replace(" 96", "").strip()
            row = rows.get(key)
            if row is None:
                problems.append(f"no row for {key}")
                continue
            cells = [x.strip() for x in row.split("|")[2:-1]]
            col = cells[0] if tag == "original" else cells[1]
            if f"({c['jobs']}" not in col or c["verdict"]["form"].upper().split()[0].replace("INCONCLUSIVE", "INCONCLUSIVE") not in col.upper().replace("TOO FEW JOBS", c["verdict"]["form"].upper()) and c["jobs"] >= 3:
                problems.append(f"{key} {tag}: verdict or jobs differ from pooled.json ({c['verdict']['form']}, {c['jobs']}): {col}")
            lost = [x["aligned"]["ratio"] for x in c["cells"] if x["class"] == "lost" and x["size_class"] in ("L1", "L2")]
            if c["jobs"] >= 3 and lost and c["verdict"]["form"] == "map":
                want = f"{min(lost):.2f} to {max(lost):.2f}x, median {statistics.median(lost):.2f}"
                part = cells[2].split("→")[0 if tag == "original" else 1]
                if want not in part:
                    problems.append(f"{key} {tag}: expected '{want}' in '{part.strip()}'")
    for pr in problems:
        print(f"   FAIL results/s5-holdout/RESULT.md: {pr}")
    if not problems:
        print("   ok   results/s5-holdout/RESULT.md matches both pooled.json files (verdicts, job counts, lost-loop cost)")
    return not problems


def check_pooled(path):
    """A pooled.json (criteria-v3): schema, criteria hash, full recomputation, independent sample."""
    import pool
    import pool_check
    name = os.path.relpath(path, REPO).replace("\\", "/")
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        schema.validate_pooled(doc)
    except Exception as e:
        print(f"   FAIL {name}: schema: {e}")
        return False
    problems = []
    if doc["criteria_sha256"] != file_sha(doc["criteria_file"]):
        problems.append(f"criteria_sha256 does not match {doc['criteria_file']} (criteria changed after this run?)")
    base = os.path.dirname(path)
    entries = pool.load_inputs([os.path.join(base, i["path"]) for i in doc["inputs"]], base)
    if [e[0] for e in entries] != [i["path"] for i in doc["inputs"]]:
        problems.append("the inputs on disk are not the ones it lists, in its order")
    crit, sha = pool.criteria_and_sha()
    again = pool.pool(entries, crit, sha)
    diffs = same_doc(doc, again)
    if diffs:
        problems.append("stored pooled numbers differ from the recomputed ones: " + "; ".join(diffs[:5]))
    sys.stdout.flush()
    n, ind = pool_check.check(path)
    problems += ["independent recompute: " + x for x in ind]
    for pr in problems:
        print(f"   FAIL {name}: {pr}")
    if not problems:
        print(f"   ok   {name} ({len(doc['inputs'])} jobs, {len(doc['runs'])} runs, {len(doc['cpus'])} CPU models, "
              f"{n} statistics recomputed independently): {doc['page']['line']}")
    return not problems


def check_results(path, criteria_sha=None):
    name = os.path.relpath(path, REPO).replace("\\", "/")
    problems = []
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        schema.validate(doc)
    except Exception as e:  # SchemaError or bad JSON
        print(f"   FAIL {name}: schema: {e}")
        return False
    crit_file = verdict.criteria_path(doc)
    if doc["run"]["criteria_sha256"] != (criteria_sha if crit_file == verdict.V1_FILE and criteria_sha
                                         else file_sha(crit_file)):
        problems.append(f"criteria_sha256 does not match {crit_file} (criteria changed after this run?)")
    for c in doc["cells"]:
        s = stats.summarize(c["none_ns"], c["fast_ns"])
        if not (close(s["ratio"], c["ratio"]) and all(close(x, y) for x, y in zip(s["ci95"], c["ci95"]))):
            problems.append(f"{c['cell_id']}: stored ratio/ci95 differ from the recomputed {s['ratio']} {s['ci95']}")
    for p in doc["programs"]:
        s = stats.summarize(p["none_ns"], p["fast_ns"])
        if not (close(s["ratio"], p["ratio"]) and all(close(x, y) for x, y in zip(s["ci95"], p["ci95"]))):
            problems.append(f"program {p['name']}: stored ratio/ci95 differ from the recomputed ones")
        # real runs only: the SAMPLE fixture (scripts/make_fixture.py, stage S1) predates the S2 rule
        if not doc["sample"] and p["consistent_with_at_most_pct"] is not None:
            bound = programs.consistent_with_at_most_pct(p["ci95"], p["aa_half_width_pct"])
            if not close(bound, p["consistent_with_at_most_pct"]):
                problems.append(f"program {p['name']}: consistent_with_at_most_pct differs from the recomputed {bound}")
            if p["aa_half_width_pct"] is not None and p["consistent_with_at_most_pct"] < p["aa_half_width_pct"]:
                problems.append(f"program {p['name']}: bound below its own A/A floor")
    aa = doc["controls"]["aa"]
    if not close(stats.half_width_pct(aa["ci95"]), aa["half_width_pct"]):
        problems.append("controls.aa.half_width_pct does not match its ci95")
    check_v2_parts(doc, problems)
    v = verdict.compute(doc, verdict.load_criteria(os.path.join(REPO, crit_file)))
    if not verdict.same_verdict(doc["verdict"], v, doc):  # v1/v2 runs: form, numbers and why; the line is historical
        problems.append(f"stored verdict differs from the recomputed one: {v}")
    for pr in problems:
        print(f"   FAIL {name}: {pr}")
    if not problems:
        tag = "SAMPLE" if doc["sample"] else "real"
        print(f"   ok   {name} ({tag}, {len(doc['cells'])} cells, {os.path.basename(crit_file)}): "
              f"{v['form']}: {v['line']}")
    return not problems


def main():
    ok = run_tests()
    print("== results files (schema 1, recomputed intervals, criteria hash, recomputed verdict)")
    with open(os.path.join(REPO, "harness", "criteria.json"), "rb") as f:
        criteria_sha = hashlib.sha256(f.read()).hexdigest()
    files = [os.path.join(REPO, "results", "fixture.json")]
    own_checker = ("mitigate-run-", "siblings-run-", "corpus-run-")  # these folders have their own checks, below
    files += sorted(set(p for p in glob.glob(os.path.join(REPO, "results", "**", "results.json"), recursive=True)
                        if not any(os.path.relpath(p, os.path.join(REPO, "results")).startswith(s) for s in own_checker)))
    files += [os.path.abspath(x) for x in sys.argv[1:]]
    for path in files:
        if not os.path.exists(path):
            print(f"   FAIL {path}: missing")
            ok = False
            continue
        ok &= check_results(path, criteria_sha)
    print("== combined files (page-level verdict across CPU models, recomputed)")
    combined = sorted(p for p in glob.glob(os.path.join(REPO, "results", "**", "combined.json"), recursive=True)
                      if "corpus-combined" not in p)  # the census table has its own checks
    for path in combined:
        ok &= check_combined(path)
    if not combined:
        print("   none yet")
    print("== pooled files (criteria-v3: every job of a CPU model pooled, recomputed, independent sample)")
    pooled = sorted(p for p in glob.glob(os.path.join(REPO, "results", "**", "pooled.json"), recursive=True)
                    if os.path.basename(os.path.dirname(p)) != "pooled")  # a workflow's own per-run copy, kept as downloaded
    for path in pooled:
        ok &= check_pooled(path)
    if not pooled:
        print("   none yet")
    ok &= check_holdout_result()
    import subprocess
    print("== mitigation experiment (every ratio and interval recomputed from the raw samples)")
    mit = sorted(glob.glob(os.path.join(REPO, "results", "mitigate-run-*")))
    if mit:
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "mitigate", "summarize.py"), "--check"] + mit) == 0
    else:
        print("   none yet")
    print("== real-project census (corpus/run_tests.py: unit tests and schema of every results/corpus-run-*)")
    if os.path.exists(os.path.join(REPO, "corpus", "run_tests.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "corpus", "run_tests.py")]) == 0
    else:
        print("   none yet")
    print("== compile-only toolchain sweep (ce-sweep/check.py: schema, cache hashes and the matrix recomputed offline from saved responses)")
    if os.path.exists(os.path.join(REPO, "ce-sweep", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "ce-sweep", "check.py")]) == 0
    else:
        print("   none yet")
    print("== lostloops tool (offline tests with saved compiler records and a stand-in compiler)")
    if os.path.exists(os.path.join(REPO, "tools", "lostloops", "run_tests.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "tools", "lostloops", "run_tests.py")]) == 0
    else:
        print("   none yet")
    print("== lostloops live test (tools/lostloops-live/check.py: the stored comparisons recomputed from the stored reports)")
    if os.path.exists(os.path.join(REPO, "tools", "lostloops-live", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "tools", "lostloops-live", "check.py")]) == 0
    else:
        print("   none yet")
    print("== layout sweep (layout-sweep/check.py: tests, plan, every job and analysis recomputed from the raw samples)")
    if os.path.exists(os.path.join(REPO, "layout-sweep", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "layout-sweep", "check.py")]) == 0
    else:
        print("   none yet")
    print("== robustness (robustness/check.py: block-bootstrap sensitivity analysis recomputed from the stored samples; skips if absent)")
    if os.path.exists(os.path.join(REPO, "robustness", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "robustness", "check.py")]) == 0
    else:
        print("   none yet")
    print("== PGO column (pgo/check.py: plan, build script, pooled file recomputed from the raw samples, report, tests)")
    if os.path.exists(os.path.join(REPO, "pgo", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "pgo", "check.py")]) == 0
    else:
        print("   none yet")
    print("== newer toolchains (versions/check.py: plan, criteria hash, workflow, analysis recomputed from the pooled files, tests; skips if absent)")
    if os.path.exists(os.path.join(REPO, "versions", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "versions", "check.py")]) == 0
    else:
        print("   none yet")
    print("== measurement environment (environment/check.py: plan, workflow, analysis recomputed from the per-job records, tests; skips if absent)")
    if os.path.exists(os.path.join(REPO, "environment", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "environment", "check.py")]) == 0
    else:
        print("   none yet")
    print("== real programs (realworld/check.py: drivers, pins, probe records, tests; timings only once measured)")
    if os.path.exists(os.path.join(REPO, "realworld", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "realworld", "check.py")]) == 0
    else:
        print("   none yet")
    print("== the page (scripts/check_site.py --quick: site data rebuilt and compared, numbers against data, drawers, screenshots)")
    if os.path.isdir(os.path.join(REPO, "site")):
        import subprocess
        sys.stdout.flush()
        rc = subprocess.call([sys.executable, os.path.join(REPO, "scripts", "check_site.py"), "--quick"])
        if rc == 2:
            print("   skipped: the playwright package is missing, so the page was not driven")
            rc = subprocess.call([sys.executable, os.path.join(REPO, "scripts", "build_site_data.py"), "--check"])
        ok &= rc == 0
    else:
        print("   skipped: site/ is not built yet (stage S4)")
    print("ALL CHECKS PASSED" if ok else "CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
