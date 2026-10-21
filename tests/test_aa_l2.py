"""robustness/aa_l2.py, robustness/aa-l2.json and robustness/README-aa-l2.md: the identical-binary A/A at L2, pooled per CPU model.

Stored data. The schema of the stored file; its counts against the four pooled.json files read again here (jobs per CPU
model, jobs above the ceiling); one CPU model recomputed from the raw per-job files by code written in this file (the
bootstrap only through harness/pool.py, read-only; the per-job ratios, the spread between jobs, the medians and the counts
by hand); the sentences of the README (several times wider at L2, about as wide on two models, above or below the ceiling
under every seed tried, one stored word that the ceiling clause would change if it read L2) against the stored numbers;
the Arm figures against the ones arm64/README.md already prints.

Logic. The rule-at-L2 function on made-up numbers; a changed number, a changed input hash, a reordered key, a missing pool
or a changed generated README block is reported by the verification; the command verifies the stored file and refuses an
unknown flag.

Offline and read-only (the tamper tests write to temporary folders). No fixtures, so scripts/check.py's built-in runner
runs it."""
import copy
import glob
import hashlib
import importlib.util
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402
import stats  # noqa: E402


def _load(key, rel):
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


aa = _load("aa_l2_script", os.path.join("robustness", "aa_l2.py"))

POOL_IDS = ["s7", "s9-x86-c", "s8-arm", "s9-arm-b"]
EPYC7763, EPYC9V45, EPYC9V74 = "AMD EPYC 7763 64-Core Processor", "AMD EPYC 9V45 96-Core Processor", "AMD EPYC 9V74 80-Core Processor"
XEON8573C, XEON6973PC = "INTEL(R) XEON(R) PLATINUM 8573C", "Intel(R) Xeon(R) 6973P-C"
N2 = "Neoverse-N2"
L2 = "k02_add_fwd.L2"
SIDE_KEYS = {"pooled_ratio", "ci95", "half_width_pct", "between_job_sd_pct", "per_job_ratio_min", "per_job_ratio_max",
             "per_job_half_width_median_pct", "per_job_half_width_max_pct", "jobs_above_ceiling"}


def read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return f.read()


def readj(rel):
    return json.loads(read(*rel.split("/")))


@lru_cache(maxsize=None)
def stored():
    return readj("robustness/aa-l2.json")


@lru_cache(maxsize=None)
def fresh():
    """The document built again from the stored files (about ten seconds); the bootstrap runs once for the whole file."""
    return aa.build()


def readme():
    return read("robustness", "README-aa-l2.md")


def row(pool_id, cpu):
    (p,) = [p for p in stored()["pools"] if p["id"] == pool_id]
    (r,) = [r for r in p["models"] if r["cpu_model"] == cpu]
    return r


def rows_with_enough_jobs(cpu):
    return [(p["id"], r) for p in stored()["pools"] for r in p["models"] if r["cpu_model"] == cpu and r["testable"]]


# ------------------------------------------------------------------ the stored file

def test_the_stored_file_has_the_schema_and_sorted_keys():
    doc = stored()
    assert doc["kind"] == "aa-l2" and doc["script"] == "robustness/aa_l2.py"
    assert set(doc) == {"kind", "script", "method", "criteria", "pools", "inventory", "early_ram", "rule_at_l2", "checks", "inputs"}
    assert [p["id"] for p in doc["pools"]] == POOL_IDS
    for p in doc["pools"]:
        assert set(p) == {"id", "arch", "what", "pooled_file", "jobs", "runs", "aa_extra_keys_in_jobs", "jobs_above_ceiling_l1",
                          "jobs_above_ceiling_l2", "models"}, p["id"]
        assert p["arch"] in ("x86-64", "arm64") and p["models"]
        for r in p["models"]:
            assert {"cpu_model", "jobs", "runs", "testable", "l1", "l2", "l2_over_l1_half_width", "l1_matches_pool", "stored_form",
                    "stored_aa_half_width_pct", "stored_forward_limit_pct", "layout_aa_half_width_pct", "rule_at_l2"} <= set(r), r["cpu_model"]
            for s in ("l1", "l2"):
                assert set(r[s]) == SIDE_KEYS, (p["id"], r["cpu_model"], s)
                lo, hi = r[s]["ci95"]
                assert lo <= r[s]["pooled_ratio"] <= hi and r[s]["half_width_pct"] > 0
                assert r[s]["per_job_ratio_min"] <= r[s]["pooled_ratio"] <= r[s]["per_job_ratio_max"]      # a geometric mean lies between its extremes
            assert set(r["rule_at_l2"]) == {"ceiling_pct", "pooled_above_ceiling", "forward_limit_pct_formula_at_l2", "effect"}
            assert r["rule_at_l2"]["effect"] in ("too_few_jobs", "already_inconclusive", "word_would_change_to_inconclusive",
                                                 "no_change", "not_evaluated_limit_differs")
    assert set(doc["rule_at_l2"]) == {"statement", "models_above_ceiling", "models_below_ceiling", "stored_words_that_would_change"}
    assert doc["checks"] == {"problems": []}
    assert list(doc["inputs"]) == sorted(doc["inputs"]) and all(re.fullmatch(r"[0-9a-f]{64}", h) for h in doc["inputs"].values())
    with open(os.path.join(REPO, "robustness", "aa-l2.json"), "rb") as fh:
        text = fh.read().decode("utf-8")                                  # bytes, so that a CRLF checkout is seen
    assert text.endswith("\n") and "\r" not in text
    assert text == json.dumps(json.loads(text), indent=1, sort_keys=True) + "\n", "the file is not the sorted-key dump of its own content"


def test_the_criteria_it_quotes_are_the_ones_in_criteria_v3():
    v3 = readj("harness/criteria-v3.json")
    c = stored()["criteria"]
    assert c["file"] == "harness/criteria-v3.json"
    assert c["aa_half_width_max_pct"] == v3["verdict"]["aa_half_width_max_pct"] == 2.0
    assert c["forward_ci_hi_floor_pct"] == v3["verdict"]["forward_ci_hi_floor_pct"]
    assert c["forward_ci_hi_aa_multiplier"] == v3["verdict"]["forward_ci_hi_aa_multiplier"]
    assert c["minimum_jobs"] == v3["v3"]["pooling"]["minimum_jobs"] == 3
    assert "no_per_job_exclusion" in json.dumps(v3), "the README says no job is excluded on its own A/A: criteria-v3 no longer says so"


def test_job_counts_equal_the_pools_and_the_counts_above_the_ceiling_are_consistent():
    ceiling = stored()["criteria"]["aa_half_width_max_pct"]
    for p in stored()["pools"]:
        pooled = readj(p["pooled_file"])
        assert p["jobs"] == len(pooled["inputs"]) == sum(b["jobs"] for b in pooled["cpus"]) == sum(r["jobs"] for r in p["models"]), p["id"]
        assert [r["cpu_model"] for r in p["models"]] == [b["cpu_model"] for b in pooled["cpus"]], p["id"]
        assert p["runs"] == sorted({i["run_id"] for i in pooled["inputs"]}), p["id"]
        for r, b in zip(p["models"], pooled["cpus"]):
            assert r["jobs"] == b["jobs"] == len([i for i in pooled["inputs"] if (i["cpu_model"] or "unknown") == r["cpu_model"]])
            assert r["testable"] == (r["jobs"] >= 3)
            assert r["l1_matches_pool"] is True
            assert r["stored_form"] == b["verdict"]["form"] and r["stored_aa_half_width_pct"] == b["aa"]["half_width_pct"]
            assert r["l1"]["half_width_pct"] == b["aa"]["half_width_pct"] and r["l1"]["pooled_ratio"] == b["aa"]["ratio"]
            for s in ("l1", "l2"):
                assert 0 <= r[s]["jobs_above_ceiling"] <= r["jobs"], (p["id"], r["cpu_model"], s)
            assert r["rule_at_l2"]["pooled_above_ceiling"] == (r["l2"]["half_width_pct"] > ceiling)
        for s in ("l1", "l2"):
            assert p[f"jobs_above_ceiling_{s}"] == sum(r[s]["jobs_above_ceiling"] for r in p["models"]), (p["id"], s)
        assert p["aa_extra_keys_in_jobs"] == [L2]


def test_one_cpu_model_recomputed_from_the_raw_files():
    """Xeon 6973P-C of the first x86-64 pool, from the seven jobs' own files: the bootstrap through pool.pair_stat, everything else by hand."""
    pooled = readj("results/s7-pooled/pooled.json")
    ins = [i for i in pooled["inputs"] if i["cpu_model"] == XEON6973PC]
    assert len(ins) == 7
    pairs, l2_hw, l1_hw = [], [], []
    for i in ins:
        base = os.path.dirname(os.path.normpath(os.path.join("results", "s7-pooled", i["path"])))
        det = readj(base.replace(os.sep, "/") + "/details.json")
        res = readj(base.replace(os.sep, "/") + "/results.json")
        x = det["aa_extra"][L2]
        pairs.append((x["a_ns"], x["b_ns"]))
        l2_hw.append(x["half_width_pct"])
        l1_hw.append(res["controls"]["aa"]["half_width_pct"])
    ps = pool.pair_stat(XEON6973PC, "aa_extra|" + L2, pairs)
    r = row("s7", XEON6973PC)["l2"]
    assert math.isclose(r["pooled_ratio"], ps["ratio"], rel_tol=1e-12)
    assert all(math.isclose(a, b, rel_tol=1e-12) for a, b in zip(r["ci95"], ps["ci95"]))
    assert math.isclose(r["half_width_pct"], stats.half_width_pct(tuple(ps["ci95"])), rel_tol=1e-12) and r["half_width_pct"] == ps["half_width_pct"]
    # by hand: per-job ratios, their geometric mean, the spread of their logs
    ratios = [statistics.median(b) / statistics.median(a) for a, b in pairs]
    logs = [math.log(x) for x in ratios]
    assert math.isclose(r["pooled_ratio"], math.exp(sum(logs) / len(logs)), rel_tol=1e-12)
    assert math.isclose(r["between_job_sd_pct"], 100 * statistics.stdev(logs), rel_tol=1e-12)
    assert r["per_job_ratio_min"] == min(ratios) and r["per_job_ratio_max"] == max(ratios)
    assert r["per_job_half_width_median_pct"] == statistics.median(l2_hw) and r["per_job_half_width_max_pct"] == max(l2_hw)
    assert r["jobs_above_ceiling"] == sum(1 for h in l2_hw if h > 2.0) and row("s7", XEON6973PC)["l1"]["jobs_above_ceiling"] == sum(1 for h in l1_hw if h > 2.0)
    assert row("s7", XEON6973PC)["l1"]["per_job_half_width_max_pct"] == max(l1_hw)


def test_the_arm_figures_are_the_ones_arm64_readme_prints():
    r = row("s8-arm", N2)
    arm = read("arm64", "README.md")
    assert f"pooled {r['l2']['pooled_ratio']:.4f}, half-width {r['l2']['half_width_pct']:.2f}%" in arm
    assert f"a spread between jobs of {r['l2']['between_job_sd_pct']:.2f}%" in arm
    assert f"per-job ratios from {r['l2']['per_job_ratio_min']:.3f} to {r['l2']['per_job_ratio_max']:.3f}" in arm
    assert f"half-width {r['l1']['half_width_pct']:.3f}%" in arm


def test_the_inventory_of_aa_extra_keys_is_what_is_on_disk():
    inv = stored()["inventory"]
    files = sorted(glob.glob(os.path.join(REPO, "results", "**", "details.json"), recursive=True)
                   + glob.glob(os.path.join(REPO, "versions", "results", "**", "details.json"), recursive=True))
    assert inv["details_files"] == len(files)
    keys, without = set(), set()
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        if "aa_extra" in d:
            keys |= set(d["aa_extra"])
        else:
            without.add(os.path.relpath(f, REPO).replace(os.sep, "/").split("/")[1])
    assert inv["distinct_keys"] == sorted(keys) == [L2, "k02_add_fwd.RAM"]
    assert inv["folders_without_aa_extra"] == sorted(without)
    assert sum(g["details_files"] for g in inv["groups"]) == len(files)
    ram = stored()["early_ram"]
    n_ram = sum(1 for f in files if "k02_add_fwd.RAM" in (json.load(open(f, encoding="utf-8")).get("aa_extra") or {}))
    assert ram["jobs"] == n_ram == sum(r["jobs"] for r in ram["models"])
    pool_folders = {os.path.normpath(os.path.join(os.path.dirname(p["pooled_file"]), i["path"])).replace(os.sep, "/").split("/")[1]
                    for p in stored()["pools"] for i in readj(p["pooled_file"])["inputs"]}
    assert ram["jobs"] > 0 and pool_folders and not (pool_folders & set(ram["folders"])), "a RAM-pair job is inside a pool"


# ------------------------------------------------------------------ the rule read at L2

def test_the_rule_read_at_l2_is_recomputed_from_the_rows_and_changes_no_stored_word():
    ceiling = stored()["criteria"]["aa_half_width_max_pct"]
    changes, above, below = [], [], []
    for p in stored()["pools"]:
        pooled = readj(p["pooled_file"])
        for r, b in zip(p["models"], pooled["cpus"]):
            assert r["stored_form"] == b["verdict"]["form"], "a stored word differs from the pooled file"
            ru = r["rule_at_l2"]
            if not r["testable"]:
                assert ru["effect"] == "too_few_jobs"
                continue
            tag = f"{p['id']}: {r['cpu_model']}"
            if r["l2"]["half_width_pct"] > ceiling:
                above.append(tag)
                assert ru["effect"] == ("already_inconclusive" if r["stored_form"] == "inconclusive" else "word_would_change_to_inconclusive"), tag
                if ru["effect"] == "word_would_change_to_inconclusive":
                    changes.append(tag)
            else:
                below.append(tag)
                assert ru["effect"] in ("no_change", "not_evaluated_limit_differs"), tag
    d = stored()["rule_at_l2"]
    assert d["models_above_ceiling"] == above and d["models_below_ceiling"] == below and d["stored_words_that_would_change"] == changes
    assert changes == [f"s7: {XEON6973PC}"] and row("s7", XEON6973PC)["stored_form"] == "map"


def test_rule_at_l2_on_made_up_numbers():
    crit = {"verdict": {"aa_half_width_max_pct": 2.0, "forward_ci_hi_floor_pct": 2.0, "forward_ci_hi_aa_multiplier": 2.0}}
    f = aa.rule_at_l2
    assert f(2, "map", 5.0, crit, 3)["effect"] == "too_few_jobs"
    assert f(7, "map", 2.01, crit, 3)["effect"] == "word_would_change_to_inconclusive"
    at = f(7, "map", 2.0, crit, 3)                                                  # the comparison is strict, as in the rule
    assert at["pooled_above_ceiling"] is False and at["effect"] == "not_evaluated_limit_differs"
    assert f(7, "inconclusive", 3.0, crit, 3)["effect"] == "already_inconclusive"
    assert f(7, "map", 0.4, crit, 3)["effect"] == "no_change" and f(7, "map", 0.4, crit, 3)["forward_limit_pct_formula_at_l2"] == 2.0
    assert f(7, "map", 1.5, crit, 3)["effect"] == "not_evaluated_limit_differs" and f(7, "map", 1.5, crit, 3)["forward_limit_pct_formula_at_l2"] == 3.0
    assert f(3, "map", 0.1, crit, 3)["effect"] != "too_few_jobs"                   # three jobs are enough


# ------------------------------------------------------------------ the sentences of the README

README_SENTENCES = ("several times noisier at L2 than at L1", "about as wide as the L1 pair or narrower",
                    "The AMD rows and the Xeon 8573C rows stay below it at L2", "stay above it under every alternative seed tried",
                    "would change one stored word", "which would go from MAP to INCONCLUSIVE",
                    "The Arm rows are INCONCLUSIVE already", "the AMD rows and the Xeon 8573C rows would not move")


def test_the_readme_sentences_hold_against_the_stored_numbers():
    """Each sentence listed in README_SENTENCES is in the README (white space collapsed) and is checked below against the stored numbers."""
    flat = re.sub(r"\s+", " ", readme())
    for s in README_SENTENCES:
        assert s in flat, f"README-aa-l2.md no longer says: {s!r} (change this test with the sentence)"
    ceiling = stored()["criteria"]["aa_half_width_max_pct"]
    # "several times noisier at L2 than at L1": Neoverse-N2, EPYC 7763, EPYC 9V74 and (first x86-64 pool) Xeon 6973P-C
    for cpu in (N2, EPYC7763, EPYC9V74, XEON6973PC):
        rows = rows_with_enough_jobs(cpu)
        assert rows, cpu
        for pid, r in rows:
            assert r["l2"]["half_width_pct"] >= 3 * r["l1"]["half_width_pct"], (pid, cpu)
    # "about as wide as the L1 pair or narrower": EPYC 9V45 and Xeon 8573C
    for cpu in (EPYC9V45, XEON8573C):
        rows = rows_with_enough_jobs(cpu)
        assert len(rows) == 2, cpu
        for pid, r in rows:
            assert r["l2"]["half_width_pct"] <= 1.25 * r["l1"]["half_width_pct"], (pid, cpu)
    # below the ceiling at L2: the AMD rows and the Xeon 8573C rows; above it: the Neoverse-N2 rows and the Xeon 6973P-C row of the first pool,
    # under every alternative seed tried
    for cpu in (EPYC7763, EPYC9V45, EPYC9V74, XEON8573C):
        for pid, r in rows_with_enough_jobs(cpu):
            assert r["l2"]["half_width_pct"] <= ceiling, (pid, cpu)
    above = [("s7", XEON6973PC), ("s8-arm", N2), ("s9-arm-b", N2)]
    assert sorted(stored()["rule_at_l2"]["models_above_ceiling"]) == sorted(f"{p}: {c}" for p, c in above)
    for pid, cpu in above:
        r = row(pid, cpu)
        s = r["l2_seed_sensitivity"]
        assert s["draws_above_ceiling"] == s["seeds"] == 20 and s["half_width_pct_min"] > ceiling, (pid, cpu)
        assert r["l2"]["half_width_pct"] > r["l1"]["half_width_pct"]
    # the Arm rows are inconclusive already; the AMD rows and the Xeon 8573C rows would not move
    for pid in ("s8-arm", "s9-arm-b"):
        r = row(pid, N2)
        assert r["stored_form"] == "inconclusive" and r["rule_at_l2"]["effect"] == "already_inconclusive"
    for cpu in (EPYC7763, EPYC9V45, EPYC9V74, XEON8573C):
        for pid, r in rows_with_enough_jobs(cpu):
            assert r["rule_at_l2"]["effect"] == "no_change", (pid, cpu)


def test_the_readme_has_no_standalone_number_outside_the_generated_block_and_code():
    text = readme()
    a, b = aa.block_of(text)
    prose = text[:a] + text[b + len(aa.MARKS[1]):]
    prose = re.sub(r"```.*?```", " ", prose, flags=re.S)
    prose = re.sub(r"`[^`\n]*`", " ", prose)
    prose = prose.replace("EPYC 7763", "EPYC").replace("EPYC 9V45", "EPYC")
    found = re.findall(r"(?<![\w.#/\-])\d+(?:[.,]\d+)?%?(?![\w.]*\w)", prose)
    assert not found, f"numbers in the prose of robustness/README-aa-l2.md that no code reads from a stored file: {found}"


def test_the_readme_block_is_the_rendering_of_the_stored_file_and_the_prose_names_its_own_guard():
    text = readme()
    assert aa.readme_block_ok(REPO, stored()) == []
    assert "tests/test_aa_l2.py" in text and "robustness/aa_l2.py --report" in text
    # the prose says it changes no stored verdict, and the stored words are those of the pooled files (checked above)
    assert "no stored verdict, pool or rule file was changed" in text
    assert "no job is excluded on its own A/A" in text


# ------------------------------------------------------------------ the verification

def test_a_fresh_build_equals_the_stored_file_and_the_inputs_are_the_files_on_disk():
    doc = fresh()
    assert aa.verify_file(os.path.join(REPO, aa.OUT), doc) == []
    for rel, h in list(doc["inputs"].items())[::25]:
        with open(os.path.join(REPO, rel), "rb") as f:
            assert hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest() == h, rel


def _verify_tampered(mutate):
    t = copy.deepcopy(stored())
    mutate(t)
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "aa-l2.json")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(aa.dumps(t))
        return aa.verify_file(p, fresh())


def test_verification_reports_a_changed_number_a_changed_hash_a_missing_pool_and_a_reordered_key():
    assert _verify_tampered(lambda t: None) == []
    d = _verify_tampered(lambda t: t["pools"][0]["models"][4]["l2"].__setitem__("half_width_pct", t["pools"][0]["models"][4]["l2"]["half_width_pct"] * 1.001))
    assert d and "half_width_pct" in d[0]
    d = _verify_tampered(lambda t: t["pools"][2]["models"][0]["l2"].__setitem__("jobs_above_ceiling", 0))
    assert d and "jobs_above_ceiling" in d[0]
    d = _verify_tampered(lambda t: t["inputs"].__setitem__(next(iter(t["inputs"])), "0" * 64))
    assert d and "inputs" in d[0]
    d = _verify_tampered(lambda t: t["pools"].pop())
    assert d and "length" in d[0]
    d = _verify_tampered(lambda t: t["rule_at_l2"].__setitem__("stored_words_that_would_change", []))
    assert d and "stored_words_that_would_change" in d[0]
    d = _verify_tampered(lambda t: t["pools"][0]["models"][0].__setitem__("testable", 1))              # True and 1 are not the same stored value
    assert d
    d = _verify_tampered(lambda t: t.__setitem__("pools", [t["pools"][1], t["pools"][0]] + t["pools"][2:]))
    assert d
    with tempfile.TemporaryDirectory() as tmp:
        assert "missing" in aa.verify_file(os.path.join(tmp, "nope.json"), fresh())[0]
        p = os.path.join(tmp, "unsorted.json")                                                          # same content, top-level keys reversed
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(dict(reversed(list(stored().items()))), indent=1, sort_keys=False) + "\n")
        d = aa.verify_file(p, fresh())
        assert d and "keys" in d[0]


def test_a_changed_or_missing_generated_block_in_the_readme_is_reported():
    doc = fresh()
    text = readme()
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "robustness"))
        p = os.path.join(tmp, "robustness", "README-aa-l2.md")
        assert aa.readme_block_ok(tmp, doc) == [f"{aa.README} is missing"]
        a, b = aa.block_of(text)
        block = text[a:b]
        digit = re.search(r"\d", block[block.index("| s7 |"):]).start() + block.index("| s7 |")
        for label, new in (("a digit in the table", text[:a] + block[:digit] + str((int(block[digit]) + 1) % 10) + block[digit + 1:] + text[b:]),
                           ("a changed job count", text[:a] + block.replace("| s7 | AMD EPYC 7763 64-Core Processor | 29 |", "| s7 | AMD EPYC 7763 64-Core Processor | 28 |", 1) + text[b:]),
                           ("a missing end marker", text.replace(aa.MARKS[1], ""))):
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            assert aa.readme_block_ok(tmp, doc), f"not reported: {label}"
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(text.replace("\n", "\r\n"))                                                         # a CRLF checkout of the same text is the same block
        assert aa.readme_block_ok(tmp, doc) == []


def test_the_command_verifies_the_stored_file_and_refuses_an_unknown_flag():
    cmd = [sys.executable, "-I", os.path.join(REPO, "robustness", "aa_l2.py")]
    r = subprocess.run(cmd + ["--verify"], capture_output=True, text=True, timeout=300, cwd=tempfile.gettempdir())
    assert r.returncode == 0, r.stdout + r.stderr
    assert "equals a recomputation" in r.stdout and "195 jobs in 4 pools" in r.stdout
    for bad in (["--bogus"], ["--deep"]):                       # --deep alone is not a mode
        r = subprocess.run(cmd + bad, capture_output=True, text=True, timeout=60, cwd=tempfile.gettempdir())
        assert r.returncode == 2, (bad, r.stdout + r.stderr)
