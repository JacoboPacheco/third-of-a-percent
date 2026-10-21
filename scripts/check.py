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
   (real runs; the SAMPLE fixture's made-up rows are exempt). Each cell's stored trap counts (plain and aligned
   builds) are recounted with harness/asm.py from the whole-function listings kept in asm/ beside results.json; a missing
   listing fails, except in the two earliest runs (stages S1 and S2), which kept the diffs only.
   Stage S3: a run that names harness/criteria-v2.json in run.criteria_file is checked against that
   file's hash and rules; its loops-aligned pairs, layout A/A pairs and verdict_v1 (criteria.json)
   are recomputed too, and every combined.json (harness/combine.py) is recomputed from the
   results.json files beside it.
   Stage S4-measurement (harness/criteria-v3.json): the raw A/A and NOVEC samples a v3 results.json
   carries are recomputed too, and every pooled.json (harness/pool.py: every job of a CPU model pooled,
   two-level bootstrap, the per-CPU verdicts) is validated, recomputed from the results.json files it
   names and compared, then a sample of its numbers is recomputed independently by
   harness/pool_check.py (plain Python, its own bootstrap, no import of pool.py or stats.py).
   results/s7-pooled/pooled.json (the file the page reads) must list every job of every s4-run-*, s6-run-*
   and s7-run-* folder once, including all of results/s4-pooled's (the original pool the holdout is compared
   with) and all of results/s6-pooled's (the 75-job intermediate pool, which itself must list every job of
   the s4-run-* and s6-run-* folders once). Every pooled.json under results/ is recomputed, the run-level
   ones in the s6-run and s7-run folders and the three pools alike.
   results/s8-arm-pooled/pooled.json (the Arm column: an AArch64 runner, its own pool, none of the x86-64 inputs)
   must list every job of every s8-arm-run-* folder once and nothing else; it, the run-level pooled.json of
   each s8-arm-run-* folder and every job's results.json there go through the same recomputations as the rest.
   The replication (replication/PLAN.md): results/s9-arm-b-pooled and results/s9-x86-c-pooled (the new sets alone) and
   the secondary pools results/s9-arm-ab-pooled and results/s9-x86-ac-pooled (the earlier pool and the new set together)
   must list every job of the run folders they name (s9-arm-run-*, s9-run-*, and for the secondary pools the earlier
   ones too) once and nothing else, and contain every job of the pools they extend; they and the run-level files are
   recomputed like all pooled.json files. harness/pool_check.py samples only CPU models with at least the minimum
   number of jobs (a model with fewer is listed as skipped). replication/compare.py --verify recomputes
   replication/results.json from the six pooled files and demands it equal the stored file.
   The matrix-multiply d-sweep (dsweep/PLAN.md): dsweep/analyze.py --verify validates every stored dsweep.json and
   recomputes its ratios and intervals from the raw samples; the sha256 of dsweep/PLAN.md must be the plan_sha256 stored in
   every dsweep.json and dsweep-pooled.json (any edit of the plan after a run fails here); results/*dsweep-pooled/
   dsweep-pooled.json must list every dsweep.json of its run folders once and equal a fresh dsweep/analyze.py over them, with
   only the input-path strings ignored (floats to 1e-9 relative), as must each run's own copy.
   Round 7 robustness analyses (each fails if its script or stored file is absent): robustness/seeds_x86.py --verify --model 6973P
   --whole 1 and the same for --model 9V45 (about 2 minutes together; the other models' cells and the 60 whole analyses are
   recomputed only by the default --verify), robustness/aa_l2.py --verify (under a minute) and robustness/calibration.py --verify
   (about a minute).
   The newer-toolchain column (versions/check.py) and the environment column (environment/check.py) run as their own steps. Every step whose script or stored result is not in the repository FAILS the run (a deleted
   checker or result folder does not make it greener); only the page step can be skipped, and then the exit code is 3.
4. The page: scripts/check_site.py --quick (site/data/ equals a fresh build, every number on the page is in
   the data, drawers open, no console errors, no horizontal scroll at 390 px, screenshots). It needs the playwright
   package, Chromium and network access to the font hosts; without the package the step is replaced by
   scripts/build_site_data.py --check and listed as skipped.
Requirements: Python 3, numpy and PyYAML; if either package is missing the run stops at once, says which and prints the
pip line (pytest is optional).
Exit code 0 only if every step passed and none was skipped. A run in which every step that ran passed but one was
skipped (the page was not driven) ends with the line "CHECKS PASSED, WITH SKIPPED STEPS" and exit code 3; a failure is
"CHECKS FAILED" and exit code 1. It does not cover siblings/ (python siblings/summarize.py results/siblings-run-<id>), the
compile-only vectorizer studies (investigate/vectorizer/*) or arm64/seeds.py --check --all; README.md names them.
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

PASSED_WITH_SKIPS = "CHECKS PASSED, WITH SKIPPED STEPS"
EXIT_PASSED_WITH_SKIPS = 3
REQUIRED_PACKAGES = (("numpy", "numpy"), ("yaml", "pyyaml"))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "tests"))

import asm  # noqa: E402
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


def missing_step(what):
    """A step whose script or stored result is not in the repository is a failure, never a pass: the page and the README
    quote what these steps recompute, so deleting a checker or a result folder must not make the run greener."""
    print(f"   FAIL {what}: missing, so the step cannot run (a missing checker or result is a failure, not a pass)")
    return False


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
        return missing_step("results/s5-holdout/RESULT.md")
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


def check_pool_complete(base=None, required=False):
    """Each pool pools every job of the run folders it names exactly once and nothing else, and contains every
    input of the earlier pools it builds on:
      results/s6-pooled/pooled.json  the 75-job intermediate pool: every job of every s4-run-* and s6-run-* folder,
                                     including all of results/s4-pooled (the original pool the holdout is compared with)
      results/s7-pooled/pooled.json  the pool the page reads: every job of every s4-run-*, s6-run-* and s7-run-* folder,
                                     including all of results/s4-pooled and results/s6-pooled
      results/s8-arm-pooled/pooled.json  the Arm column's pool: every job of every s8-arm-run-* folder and nothing else
                                     (an AArch64 runner; it shares no input with the x86-64 pools and does not need them)
    and the four pools of the replication (replication/PLAN.md):
      results/s9-arm-b-pooled/pooled.json   set B alone: every job of every s9-arm-run-* folder and nothing else
      results/s9-x86-c-pooled/pooled.json   set C alone: every job of every s9-run-* folder and nothing else
      results/s9-arm-ab-pooled/pooled.json  sets A and B: the s8-arm-run-* and s9-arm-run-* jobs, including all of
                                            results/s8-arm-pooled and results/s9-arm-b-pooled
      results/s9-x86-ac-pooled/pooled.json  the first pool and set C: the s4-, s6-, s7- and s9-run-* jobs, including all of
                                            results/s7-pooled and results/s9-x86-c-pooled
    `base` is the results folder (default: the repository's); the tests point it at a scratch copy. With `required` (the
    run of main()) a pool whose pooled.json is not there fails; without it the pool is skipped, which the scratch copies
    of the tests rely on (each holds only the pools it is about)."""
    base = base or os.path.join(REPO, "results")

    def listed(rel):
        with open(os.path.join(base, rel, "pooled.json"), encoding="utf-8") as f:
            return [os.path.normpath(os.path.join(base, rel, i["path"])) for i in json.load(f)["inputs"]]
    ok = True
    # (pool folder, the run folders it pools, the earlier pools whose every input it must contain)
    pools = (("s6-pooled", ("s4-run-*", "s6-run-*"), ("s4-pooled",)),
             ("s7-pooled", ("s4-run-*", "s6-run-*", "s7-run-*"), ("s4-pooled", "s6-pooled")),
             ("s8-arm-pooled", ("s8-arm-run-*",), ()),
             ("s9-arm-b-pooled", ("s9-arm-run-*",), ()),
             ("s9-x86-c-pooled", ("s9-run-*",), ()),
             ("s9-arm-ab-pooled", ("s8-arm-run-*", "s9-arm-run-*"), ("s8-arm-pooled", "s9-arm-b-pooled")),
             ("s9-x86-ac-pooled", ("s4-run-*", "s6-run-*", "s7-run-*", "s9-run-*"), ("s7-pooled", "s9-x86-c-pooled")))
    for rel, patterns, earlier in pools:
        if not os.path.exists(os.path.join(base, rel, "pooled.json")):
            if required:
                ok &= missing_step(f"results/{rel}/pooled.json")
            continue
        pooled = listed(rel)
        on_disk = [os.path.normpath(p) for pat in patterns
                   for p in glob.glob(os.path.join(base, pat, "results-*", "results.json"))]
        names = [pat[:-2] for pat in patterns]
        kinds = " and ".join([", ".join(names[:-1]), names[-1]] if len(names) > 2 else names)
        problems = []
        if len(set(pooled)) != len(pooled):
            problems.append("a job is listed twice")
        for p in sorted(set(on_disk) - set(pooled)):
            problems.append(f"{os.path.relpath(p, base)} is on disk but not pooled")
        for p in sorted(set(pooled) - set(on_disk)):
            problems.append(f"{os.path.relpath(p, base)} is pooled but is not in an {kinds.replace(' and ', ' or ')} folder")
        for e in earlier:
            for p in sorted(set(listed(e)) - set(pooled)):
                label = "original" if e == "s4-pooled" else e[:-len("-pooled")]  # s6, s7, s8-arm, s9-arm-b, s9-x86-c
                problems.append(f"{os.path.relpath(p, base)} is in the {label} pool but not in this one")
        for pr in problems:
            print(f"   FAIL results/{rel}/pooled.json: {pr}")
        if not problems:
            incl = " and ".join(f"the {len(listed(e))} of results/{e}" for e in earlier)
            print(f"   ok   results/{rel}/pooled.json pools all {len(on_disk)} jobs of the {kinds} folders "
                  f"once each" + (f", including {incl}" if incl else ""))
        ok &= not problems
    return ok


# ---------------------------------------------------------------- the matrix-multiply d-sweep (dsweep/PLAN.md)
DSWEEP_PLAN = "dsweep/PLAN.md"


def lf_sha(rel_path):
    """sha256 of a file with CRLF read as LF: dsweep/analyze.py hashes the plan this way, so a Windows and a Linux checkout agree."""
    with open(os.path.join(REPO, rel_path), "rb") as f:
        return hashlib.sha256(f.read().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def dsweep_run_files(base):
    """Every per-job dsweep.json in the d-sweep run folders of `base` (results/*dsweep-run-*/<job folder>/dsweep.json)."""
    return sorted(glob.glob(os.path.join(base, "*dsweep-run-*", "*", "dsweep.json")))


def dsweep_pooled_files(base):
    """The pooled d-sweep files: the pool of all runs (results/*dsweep-pooled/dsweep-pooled.json) and, kept as downloaded, each
    run's own (results/*dsweep-run-*/dsweep-pooled/dsweep-pooled.json)."""
    return (sorted(glob.glob(os.path.join(base, "*dsweep-pooled", "dsweep-pooled.json")))
            + sorted(glob.glob(os.path.join(base, "*dsweep-run-*", "dsweep-pooled", "dsweep-pooled.json"))))


def dsweep_norm(doc):
    """A dsweep-pooled.json with its input paths cut to the last two components (job folder, file name). The paths are relative
    to the folder the analysis was told to write to, which is not the same for the stored pool, a workflow's own copy
    and a re-pool; nothing else of the file is changed."""
    doc = json.loads(json.dumps(doc))
    cut = lambda p: "/".join(p.replace("\\", "/").split("/")[-2:])  # noqa: E731
    for i in doc["inputs"]:
        i["path"] = cut(i["path"])
    for c in doc["cpus"]:
        c["inputs"] = [cut(p) for p in c["inputs"]]
    return doc


def dsweep_repool(files):
    """dsweep/analyze.py over exactly `files`, written to a scratch folder: (the pooled document, or None and why)."""
    import subprocess
    import tempfile
    t = tempfile.gettempdir()
    # analyze.py writes the input paths relative to the --out folder, which needs the same drive on Windows
    parent = None if os.path.splitdrive(t)[0].lower() == os.path.splitdrive(REPO)[0].lower() else REPO
    with tempfile.TemporaryDirectory(dir=parent) as tmp:
        out = os.path.join(tmp, "dsweep-pooled.json")
        sys.stdout.flush()
        r = subprocess.run([sys.executable, os.path.join(REPO, "dsweep", "analyze.py")] + list(files) + ["--out", out],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(out):
            return None, f"dsweep/analyze.py exited {r.returncode}: {(r.stdout + r.stderr).strip()[-300:]}"
        with open(out, encoding="utf-8") as f:
            return json.load(f), ""


def check_dsweep_plan(sweeps, pools, plan=DSWEEP_PLAN):
    """The plan (dsweep/PLAN.md) is the one every stored dsweep.json and every pooled d-sweep file was produced under: each stores
    the plan's sha256, so any later edit of the plan, even of one word, shows here and makes the stored runs unusable."""
    want = lf_sha(plan)
    problems = []
    for path in list(sweeps) + list(pools):
        try:
            name = os.path.relpath(path, REPO).replace("\\", "/")
        except ValueError:  # another drive (a scratch copy in a test)
            name = path
        try:
            with open(path, encoding="utf-8") as f:
                have = json.load(f).get("plan_sha256")
        except (OSError, ValueError) as e:
            problems.append(f"{name}: unreadable ({e})")
            continue
        if have != want:
            problems.append(f"{name}: stored plan_sha256 {str(have)[:12]} is not the hash of {plan} as it stands ({want[:12]}); "
                            "the plan was edited after the run, or the file was not produced under it")
    for pr in problems:
        print(f"   FAIL {pr}")
    if not problems:
        print(f"   ok   {plan} (sha256 {want[:12]}) is the plan all {len(sweeps)} dsweep.json and {len(pools)} dsweep-pooled.json files were produced under")
    return not problems


def check_dsweep_pools(base=None):
    """Each pooled d-sweep file is what dsweep/analyze.py gives for the files it names, with only the input paths ignored.
    results/*dsweep-pooled/dsweep-pooled.json must list every per-job dsweep.json of the run folders it names once and nothing
    else, and every dsweep.json in a d-sweep run folder must be in one such pool; each run's own copy (kept as downloaded,
    results/*dsweep-run-*/dsweep-pooled/) is re-pooled from the jobs of its folder. Floats are compared to 1e-9 relative, as for the
    other pooled files (a different numpy may differ in the last digits). `base` is the results folder (default: the repository's)."""
    base = base or os.path.join(REPO, "results")
    on_disk = [os.path.normpath(p) for p in dsweep_run_files(base)]
    pools = sorted(glob.glob(os.path.join(base, "*dsweep-pooled", "dsweep-pooled.json")))
    ok, in_a_pool = True, set()
    if on_disk and not pools:
        print("   FAIL there are dsweep.json files under results/ and no results/*dsweep-pooled/dsweep-pooled.json")
        return False
    for path in pools:
        name = "results/" + os.path.relpath(path, base).replace("\\", "/")
        with open(path, encoding="utf-8") as f:
            stored = json.load(f)
        listed =[os.path.normpath(os.path.join(os.path.dirname(path), i["path"])) for i in stored["inputs"]]
        problems = []
        if len(set(listed)) != len(listed):
            problems.append("a job is listed twice")
        for p in (x for x in listed if not os.path.isfile(x)):
            problems.append(f"{os.path.relpath(p, base)} is listed but is not on disk")
        runs = {os.path.dirname(os.path.dirname(p)) for p in listed}   # <run folder>/<job folder>/dsweep.json
        for p in sorted(x for x in on_disk if os.path.dirname(os.path.dirname(x)) in runs and x not in listed):
            problems.append(f"{os.path.relpath(p, base)} is on disk in a run folder this pool names but not pooled")
        in_a_pool |= set(listed)
        if not problems:
            again, why = dsweep_repool(listed)
            if again is None:
                problems.append(why)
            else:
                diffs = same_doc(dsweep_norm(stored), dsweep_norm(again))
                if diffs:
                    problems.append("stored numbers differ from the recomputed ones: " + "; ".join(diffs[:5]))
        for pr in problems:
            print(f"   FAIL {name}: {pr}")
        if not problems:
            print(f"   ok   {name} equals dsweep/analyze.py over the {len(listed)} dsweep.json it lists (all those of its "
                  f"{len(runs)} run folders; input paths aside): {stored['line']}")
        ok &= not problems
    for p in sorted(set(on_disk) - in_a_pool):
        print(f"   FAIL {os.path.relpath(p, base)} is in no results/*dsweep-pooled/dsweep-pooled.json")
        ok = False
    for path in sorted(glob.glob(os.path.join(base, "*dsweep-run-*", "dsweep-pooled", "dsweep-pooled.json"))):
        name = "results/" + os.path.relpath(path, base).replace("\\", "/")
        run =os.path.dirname(os.path.dirname(path))
        jobs = [p for p in dsweep_run_files(base) if os.path.dirname(os.path.dirname(p)) == run]
        with open(path, encoding="utf-8") as f:
            stored = json.load(f)
        again, why = dsweep_repool(jobs) if jobs else (None, "no dsweep.json in the run folder")
        diffs = same_doc(dsweep_norm(stored), dsweep_norm(again)) if again is not None else [why]
        for d in diffs[:5]:
            print(f"   FAIL {name}: {d}")
        if not diffs:
            print(f"   ok   {name} equals dsweep/analyze.py over the {len(jobs)} dsweep.json of its run folder (input paths aside)")
        ok &= not diffs
    return ok


def check_dsweep():
    """The d-sweep step of main(): every stored dsweep.json validated and its ratios recomputed from the raw samples
    (dsweep/analyze.py --verify), the plan hash, and the pooled files re-pooled. A missing analysis script or no stored sweep fails."""
    import subprocess
    sweeps = sorted(set(glob.glob(os.path.join(REPO, "results", "**", "dsweep.json"), recursive=True)
                        + glob.glob(os.path.join(REPO, "dsweep", "**", "dsweep.json"), recursive=True)))
    analyze = os.path.join(REPO, "dsweep", "analyze.py")
    if not os.path.exists(analyze):
        return missing_step("dsweep/analyze.py")
    if not sweeps:
        return missing_step("results/*dsweep-run-*/**/dsweep.json (no stored d-sweep)")
    sys.stdout.flush()
    ok = subprocess.call([sys.executable, analyze, "--verify"] + sweeps) == 0
    ok &= check_dsweep_plan(sweeps, dsweep_pooled_files(os.path.join(REPO, "results")))
    ok &= check_dsweep_pools()
    return ok


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


# The two earliest runs (stages S1 and S2) kept only each cell's .diff, not the whole-function listings; every later run keeps
# asm/<kernel>.{none,fast,none_a64,fast_a64}.s beside its results.json, and the SAMPLE fixture has no job folder at all.
NO_LISTING_RUNS = ("s1-run-38119008371", "s2-run-38119607308")


def check_trap_counts(path, doc, problems):
    """Each cell's stored traps_none and traps_fast (and the aligned pair's) equal harness/asm.count_traps() over the listing
    kept beside results.json (x86-64 ud2, AArch64 brk #0x1, and calls to __libcpp_verbose_abort). A listing that is missing,
    or a count that differs, is a problem. Returns how many listings were recounted (0 for the fixture and the two early
    runs that kept diffs only). It checks the stored counts against the stored listings; it does not rebuild or disassemble."""
    run_dir = os.path.dirname(path)
    if doc["sample"] or os.path.basename(run_dir) in NO_LISTING_RUNS:
        return 0
    counted, missing = {}, set()
    n = 0
    for c in doc["cells"]:
        for stored, tag in ((c, ""), (c.get("aligned"), "_a64")):
            if stored is None:
                continue
            for build in ("none", "fast"):
                file = f"{c['kernel']}.{build}{tag}.s"
                if file not in counted and file not in missing:
                    listing = os.path.join(run_dir, "asm", file)
                    if os.path.exists(listing):
                        with open(listing, encoding="utf-8") as f:
                            counted[file] = asm.count_traps(f.read().splitlines())
                    else:
                        missing.add(file)
                        problems.append(f"asm/{file} is missing, so the traps_{build} of {c['kernel']} cannot be recounted")
                if file in counted:
                    n += 1
                    if counted[file] != stored[f"traps_{build}"]:
                        problems.append(f"{c['cell_id']}: stored {'aligned ' if tag else ''}traps_{build} {stored[f'traps_{build}']} "
                                        f"differs from the {counted[file]} trap instructions in asm/{file}")
    return n


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
    recounted = check_trap_counts(path, doc, problems)
    v = verdict.compute(doc, verdict.load_criteria(os.path.join(REPO, crit_file)))
    if not verdict.same_verdict(doc["verdict"], v, doc):  # v1/v2 runs: form, numbers and why; the line is historical
        problems.append(f"stored verdict differs from the recomputed one: {v}")
    for pr in problems:
        print(f"   FAIL {name}: {pr}")
    if not problems:
        tag = "SAMPLE" if doc["sample"] else "real"
        print(f"   ok   {name} ({tag}, {len(doc['cells'])} cells, {os.path.basename(crit_file)}, "
              f"{recounted} trap counts recounted from the listings): {v['form']}: {v['line']}")
    return not problems


def results_files():
    """Every results.json under results/ that check_results() goes through (the x86-64 folders and the s8-arm-run-* jobs alike)."""
    # these folders are not x86-64/Arm kernel runs and have another record format: mitigate-run-* and corpus-run-* are
    # gone through by their own steps in main(); siblings-run-* has no step in this script (python siblings/summarize.py)
    own_checker = ("mitigate-run-", "siblings-run-", "corpus-run-")
    return sorted(set(p for p in glob.glob(os.path.join(REPO, "results", "**", "results.json"), recursive=True)
                      if not any(os.path.relpath(p, os.path.join(REPO, "results")).startswith(s) for s in own_checker)))


def pooled_files():
    """Every pooled.json under results/ that check_pooled() goes through (the three x86-64 pools, their run-level files, the Arm pool and its runs)."""
    return sorted(p for p in glob.glob(os.path.join(REPO, "results", "**", "pooled.json"), recursive=True)
                  if os.path.basename(os.path.dirname(p)) != "pooled")  # a workflow's own per-run copy, kept as downloaded


def missing_packages():
    """The pip names of the required packages that cannot be imported."""
    missing = []
    for module, pip_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(pip_name)
    return missing


def finish(ok, skipped):
    """The last line and the exit code: 1 if any step failed, 3 if every step that ran passed but some were skipped, else 0."""
    if not ok:
        print("CHECKS FAILED")
        return 1
    if skipped:
        print(PASSED_WITH_SKIPS)
        for s in skipped:
            print(f"   skipped: {s}")
        return EXIT_PASSED_WITH_SKIPS
    print("ALL CHECKS PASSED")
    return 0


def main():
    missing = missing_packages()
    if missing:
        print(f"MISSING PYTHON PACKAGES: {', '.join(missing)}. Install them with: pip install {' '.join(missing)}")
        print("CHECKS FAILED")
        return 1
    skipped = []
    ok = run_tests()
    print("== results files (schema 1, recomputed intervals, criteria hash, recomputed verdict)")
    with open(os.path.join(REPO, "harness", "criteria.json"), "rb") as f:
        criteria_sha = hashlib.sha256(f.read()).hexdigest()
    files = [os.path.join(REPO, "results", "fixture.json")]
    files += results_files()
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
        ok &= missing_step("results/**/combined.json")
    print("== pooled files (criteria-v3: every job of a CPU model pooled, recomputed, independent sample)")
    pooled = pooled_files()
    for path in pooled:
        ok &= check_pooled(path)
    if not pooled:
        ok &= missing_step("results/**/pooled.json")
    ok &= check_holdout_result()
    ok &= check_pool_complete(required=True)
    import subprocess
    print("== mitigation experiment (every ratio and interval recomputed from the raw samples)")
    mit = sorted(glob.glob(os.path.join(REPO, "results", "mitigate-run-*")))
    if mit:
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "mitigate", "summarize.py"), "--check"] + mit) == 0
    else:
        ok &= missing_step("results/mitigate-run-*")
    print("== real-project census (corpus/run_tests.py: unit tests and schema of every results/corpus-run-*)")
    if os.path.exists(os.path.join(REPO, "corpus", "run_tests.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "corpus", "run_tests.py")]) == 0
    else:
        ok &= missing_step("corpus/run_tests.py")
    print("== compile-only toolchain sweep (ce-sweep/check.py: schema, cache hashes and the matrix recomputed offline from saved responses)")
    if os.path.exists(os.path.join(REPO, "ce-sweep", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "ce-sweep", "check.py")]) == 0
    else:
        ok &= missing_step("ce-sweep/check.py")
    print("== lostloops tool (offline tests with saved compiler records and a stand-in compiler)")
    if os.path.exists(os.path.join(REPO, "tools", "lostloops", "run_tests.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "tools", "lostloops", "run_tests.py")]) == 0
    else:
        ok &= missing_step("tools/lostloops/run_tests.py")
    print("== lostloops live test (tools/lostloops-live/check.py: the stored comparisons recomputed from the stored reports)")
    if os.path.exists(os.path.join(REPO, "tools", "lostloops-live", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "tools", "lostloops-live", "check.py")]) == 0
    else:
        ok &= missing_step("tools/lostloops-live/check.py")
    print("== layout sweep (layout-sweep/check.py: tests, plan, every job and analysis recomputed from the raw samples)")
    if os.path.exists(os.path.join(REPO, "layout-sweep", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "layout-sweep", "check.py")]) == 0
    else:
        ok &= missing_step("layout-sweep/check.py")
    print("== robustness (robustness/check.py: block-bootstrap sensitivity analysis recomputed from the stored samples; fails if absent)")
    if os.path.exists(os.path.join(REPO, "robustness", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "robustness", "check.py")]) == 0
    else:
        ok &= missing_step("robustness/check.py")
    print("== Arm seed sensitivity (arm64/seeds.py --check: the stored seed's numbers, eight other seeds, two whole analyses and the "
          "deciding cell's converged reading recomputed from the pool; the full recomputation is --check --all; fails if absent)")
    if os.path.exists(os.path.join(REPO, "arm64", "seeds.py")) and os.path.exists(os.path.join(REPO, "arm64", "seed-sensitivity.json")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "arm64", "seeds.py"), "--check"]) == 0
    else:
        ok &= missing_step("arm64/seeds.py and arm64/seed-sensitivity.json")
    print("== x86-64 seed sensitivity (robustness/seeds_x86.py --verify --model 6973P --whole 1 and --model 9V45 --whole 1: the cells of the Xeon "
          "6973P-C and of the EPYC 9V45 (the two models whose word rests on a cell near a line) under all 400 other seeds, their converged readings "
          "and one whole analysis each recomputed from the pool, about 2 minutes together; the 7763, 9V74 and 8573C cells and the full 60 whole "
          "analyses are recomputed only by the default --verify (about 5 minutes, run by hand), not by this step; fails if absent)")
    if os.path.exists(os.path.join(REPO, "robustness", "seeds_x86.py")) and os.path.exists(os.path.join(REPO, "robustness", "seed-sensitivity-x86.json")):
        sys.stdout.flush()
        for model in ("6973P", "9V45"):
            ok &= subprocess.call([sys.executable, os.path.join(REPO, "robustness", "seeds_x86.py"), "--verify", "--model", model, "--whole", "1"]) == 0
    else:
        ok &= missing_step("robustness/seeds_x86.py and robustness/seed-sensitivity-x86.json")
    print("== identical-binary A/A at L2 (robustness/aa_l2.py --verify: robustness/aa-l2.json recomputed from the jobs' stored A/A samples, "
          "under a minute; fails if absent)")
    if os.path.exists(os.path.join(REPO, "robustness", "aa_l2.py")) and os.path.exists(os.path.join(REPO, "robustness", "aa-l2.json")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "robustness", "aa_l2.py"), "--verify"]) == 0
    else:
        ok &= missing_step("robustness/aa_l2.py and robustness/aa-l2.json")
    print("== calibration of the run-to-run claim (robustness/calibration.py --verify: robustness/calibration.json recomputed, with the "
          "identity shuffle and one more shuffle of the shuffle null and the J=3 subsets, about 1 minute; fails if absent)")
    if os.path.exists(os.path.join(REPO, "robustness", "calibration.py")) and os.path.exists(os.path.join(REPO, "robustness", "calibration.json")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "robustness", "calibration.py"), "--verify"]) == 0
    else:
        ok &= missing_step("robustness/calibration.py and robustness/calibration.json")
    print("== replication (replication/compare.py --verify: replication/results.json recomputed from the six pooled files; fails if absent)")
    if os.path.exists(os.path.join(REPO, "replication", "compare.py")) and os.path.exists(os.path.join(REPO, "replication", "results.json")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "replication", "compare.py"), "--verify"]) == 0
    else:
        ok &= missing_step("replication/compare.py and replication/results.json")
    print("== d-sweep (dsweep/analyze.py --verify: every stored dsweep.json validated and its numbers recomputed; the plan hash; "
          "the pooled files re-pooled and compared, input paths aside; none is stored until the sweep has run)")
    ok &= check_dsweep()
    print("== PGO column (pgo/check.py: plan, build script, pooled file recomputed from the raw samples, report, tests)")
    if os.path.exists(os.path.join(REPO, "pgo", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "pgo", "check.py")]) == 0
    else:
        ok &= missing_step("pgo/check.py")
    print("== newer toolchains (versions/check.py: plan, criteria hash, workflow, analysis recomputed from the pooled files, tests; fails if absent)")
    if os.path.exists(os.path.join(REPO, "versions", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "versions", "check.py")]) == 0
    else:
        ok &= missing_step("versions/check.py")
    print("== measurement environment (environment/check.py: plan, workflow, analysis recomputed from the per-job records, tests; fails if absent)")
    if os.path.exists(os.path.join(REPO, "environment", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "environment", "check.py")]) == 0
    else:
        ok &= missing_step("environment/check.py")
    print("== real programs (realworld/check.py: drivers, pins, probe records, tests; timings only once measured)")
    if os.path.exists(os.path.join(REPO, "realworld", "check.py")):
        sys.stdout.flush()
        ok &= subprocess.call([sys.executable, os.path.join(REPO, "realworld", "check.py")]) == 0
    else:
        ok &= missing_step("realworld/check.py")
    print("== the page (scripts/check_site.py --quick: site data rebuilt and compared, numbers against data, drawers, screenshots)")
    if os.path.isdir(os.path.join(REPO, "site")):
        import subprocess
        sys.stdout.flush()
        rc = subprocess.call([sys.executable, os.path.join(REPO, "scripts", "check_site.py"), "--quick"])
        if rc == 2:
            print("   skipped: the playwright package is missing, so the page was not driven")
            skipped.append("the page was not driven (playwright is missing; pip install playwright, then playwright install chromium)")
            rc = subprocess.call([sys.executable, os.path.join(REPO, "scripts", "build_site_data.py"), "--check"])
        ok &= rc == 0
    else:
        print("   skipped: site/ is not built yet (stage S4)")
        skipped.append("site/ is not built")
    return finish(ok, skipped)


if __name__ == "__main__":
    sys.exit(main())
