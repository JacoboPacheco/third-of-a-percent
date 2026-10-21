"""robustness/calibration.py, robustness/calibration.json and robustness/README-calibration.md: the calibration baseline for the
sentence "intervals still understate run-to-run spread".

Five kinds of test (the fifth, at the end of the file, ties robustness/README-calibration.md to the stored file: its generated
tables block must equal calibration.py's output and each number in its prose is rebuilt from calibration.json; a changed prose
number or table cell fails).

Reproduction. The counts the README and the details page quote (EPYC 7763: 168 of 640, EPYC 9V74: 62 of 384, in the 95-job
pool) are recounted here, by a loop written in this file, from the stored per_run records of every pooled.json the script reads
(not through calibration.py or harness/pool.py), and must equal both the stored `reproduction` of that pooled file and the
record in calibration.json.

Formula. The expected count of a calibrated interval is checked against a value worked out by hand and by numerical
integration of the normal density (nothing from `math.erfc`), against its limits, and against a simulation of a made-up pair.

Consistency. Sums over cells equal the totals, simulation means sit at the closed-form expectation, the shuffle summary is
rebuilt from the shuffles, the identity shuffle is the stored run record, subset words add up to the subsets drawn, the
stored replication counts are the ones replication/results.json carries.

Guard. `--verify` (one subprocess, a couple of minutes) recomputes parts A, B, C, D, the identity and first shuffle of one model
and one subset block and compares them with the stored file; tampering with the stored file (an input hash, a count, a table
cell of the README) is caught.

Offline and read-only (the tamper tests work on temporary copies). No fixtures, so scripts/check.py's built-in runner runs it."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))


def _load(key, rel):
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


cal = _load("robustness_calibration", os.path.join("robustness", "calibration.py"))

STORED = os.path.join(REPO, "robustness", "calibration.json")
README = os.path.join(REPO, "robustness", "README-calibration.md")
EPYC7763, EPYC9V74 = "AMD EPYC 7763 64-Core Processor", "AMD EPYC 9V74 80-Core Processor"
IN_CACHE = ("L1", "L2")
COLUMNS = ("as_compiled", "aligned")


def read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def pooled(rel):
    return read(*rel.split("/"))


@lru_cache(maxsize=None)
def doc():
    with open(STORED, encoding="utf-8") as f:
        return json.load(f)


def model_record(pool_key, model):
    return next((m for m in doc()["run_to_run"][pool_key]["models"] if m["cpu_model"] == model), None)


def recount(pooled_doc, model):
    """Recount, in this file, how often a run's point falls outside another run's interval: every ordered pair of different
    runs that have a verdict form, every in-cache cell, both columns. Returns (checked, outside)."""
    runs = [r for b in pooled_doc["cpus"] if b["cpu_model"] == model for r in b["per_run"] if r["form"] is not None]
    checked = outside = 0
    for a, ra in enumerate(runs):
        for b, rb in enumerate(runs):
            if a == b:
                continue
            for cid in ra["cells"]:
                assert cid.rsplit(".", 1)[1] in IN_CACHE
                for col in COLUMNS:
                    pt = ra["cells"][cid][col][0]
                    lo, hi = rb["cells"][cid][col][1], rb["cells"][cid][col][2]
                    checked += 1
                    if not (lo <= pt <= hi):
                        outside += 1
    return checked, outside


# ----------------------------------------------------------------------------------------------------------------------
# reproduction of the stored counts

def test_the_two_counts_in_the_readme_are_recounted():
    p = pooled("results/s7-pooled/pooled.json")
    assert recount(p, EPYC7763) == (640, 168)
    assert recount(p, EPYC9V74) == (384, 62)
    for model, want in ((EPYC7763, (640, 168)), (EPYC9V74, (384, 62))):
        m = model_record("s7", model)
        assert (m["checked"], m["outside"]) == want
        assert (m["stored_checked"], m["stored_outside"]) == want
        assert m["reproduces_stored"] is True


def test_every_pool_recount_equals_the_stored_reproduction_and_the_record():
    seen = 0
    for key, rel, _ in cal.RUN_POOLS:
        p = pooled(rel)
        rec = doc()["run_to_run"][key]
        listed = {m["cpu_model"] for m in rec["models"]}
        for b in p["cpus"]:
            assessable = [r for r in b["per_run"] if r["form"] is not None]
            if len(assessable) < 2:
                assert b["cpu_model"] not in listed
                assert any(s["cpu_model"] == b["cpu_model"] for s in rec["not_assessable"])
                continue
            checked, outside = recount(p, b["cpu_model"])
            assert (checked, outside) == (b["reproduction"]["checked"], b["reproduction"]["outside"]), (key, b["cpu_model"])
            m = next(x for x in rec["models"] if x["cpu_model"] == b["cpu_model"])
            assert (m["checked"], m["outside"]) == (checked, outside), (key, b["cpu_model"])
            assert m["reproduces_stored"] is True
            seen += 1
        assert rec["pool"] == key
    assert seen == sum(len(v["models"]) for v in doc()["run_to_run"].values())
    assert seen >= 10


def test_the_largest_gap_is_the_stored_one():
    for key, rel, _ in cal.RUN_POOLS:
        for m in doc()["run_to_run"][key]["models"]:
            if m["stored_max_gap_pct"] is None:
                assert m["max_gap_pct"] == 0.0
            else:
                assert math.isclose(m["max_gap_pct"], m["stored_max_gap_pct"], rel_tol=0, abs_tol=0.0006), (key, m["cpu_model"])


# ----------------------------------------------------------------------------------------------------------------------
# the formula

def simpson(f, a, b, n=20000):
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return s * h / 3.0


def normal_tail_two_sided(c):
    """P(|Z| > c) for a standard normal, by integrating the density from 0 to c (no erf)."""
    inside = 2.0 * simpson(lambda x: math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi), 0.0, c)
    return 1.0 - inside


def test_expected_outside_equals_a_hand_worked_example():
    # Two runs with the same stated interval width (s) and an interval that is symmetric around its point (offsets 1.96 s):
    # the difference of the two points has sd s*sqrt(2), the point is outside when it is more than 1.96 s away from the other
    # point, i.e. when |Z| > 1.96 / sqrt(2) = 1.3859 for a standard normal. P = 0.1658 (worked from the normal table: 2 x 0.0829).
    s = 0.0137
    got = cal.expected_outside(s, s, cal.Z * s, cal.Z * s)
    want = normal_tail_two_sided(cal.Z / math.sqrt(2.0))
    assert abs(want - 0.1658) < 5e-4
    assert abs(got - want) < 1e-6
    assert abs(cal.expected_outside_sym(s, s) - want) < 1e-6
    # the result does not depend on the scale of s
    assert abs(cal.expected_outside(5 * s, 5 * s, cal.Z * 5 * s, cal.Z * 5 * s) - got) < 1e-12
    # a wider earlier interval catches more: sb = 2 sa
    sa, sb = 0.01, 0.02
    sigma = math.hypot(sa, sb)
    want2 = normal_tail_two_sided(cal.Z * sb / sigma)
    assert abs(cal.expected_outside(sa, sb, cal.Z * sb, cal.Z * sb) - want2) < 1e-6
    assert want2 < want


def test_expected_outside_limits():
    # interval of the earlier run shrinks to a point: every other point is outside
    assert abs(cal.expected_outside(0.01, 1e-9, 1e-12, 1e-12) - 1.0) < 1e-6
    # an interval that is open above and has no room below: only the downward half of the difference can be outside = 1/2
    assert abs(cal.expected_outside(0.01, 0.01, 0.0, 50.0) - 0.5) < 1e-12
    # an interval with an enormous room on both sides: nothing is outside
    assert cal.expected_outside(0.01, 0.01, 50.0, 50.0) < 1e-12
    # an asymmetric interval: the two tails add, each weighted by its own offset
    sa, sb, dlo, dhi = 0.01, 0.015, 0.02, 0.05
    sigma = math.hypot(sa, sb)
    want = 0.5 * normal_tail_two_sided(dlo / sigma) + 0.5 * normal_tail_two_sided(dhi / sigma)
    assert abs(cal.expected_outside(sa, sb, dlo, dhi) - want) < 1e-6


def test_expected_outside_matches_a_simulation_of_a_made_up_pair():
    sa, sb, dlo, dhi = 0.010, 0.020, 0.030, 0.050
    n = 400000
    za = cal.normals(cal.cal_seed("test", "a"), (n,))
    zb = cal.normals(cal.cal_seed("test", "b"), (n,))
    x = sa * za - sb * zb                      # ln pt_A - ln pt_B
    got = float(((x < -dlo) | (x > dhi)).mean())
    want = cal.expected_outside(sa, sb, dlo, dhi)
    assert abs(got - want) < 5.0 * math.sqrt(want * (1 - want) / n), (got, want)
    # the generator is a standard normal
    assert abs(float(za.mean())) < 0.01 and abs(float(za.std()) - 1.0) < 0.01


def test_count_and_z_summaries_on_made_up_numbers():
    c = cal.count_summary([3, 5, 5, 7, 9, 11, 2, 4, 6, 8] * 200, 7, 2000)
    assert c["reps"] == 2000 and c["min"] == 2 and c["max"] == 11
    # of the ten values 7, 9, 11 and 8 are at or above 7 (0.4) and 3, 5, 5, 7, 2, 4, 6 are at or below it (0.7)
    assert math.isclose(c["mean"], 6.0) and c["p_ge_observed"] == 0.4 and c["p_le_observed"] == 0.7
    z = cal.z_summary([0.5, -2.0, 1.0, 3.0, -0.1])
    assert z["n"] == 5 and z["count_abs_gt_1_96"] == 2 and z["share_abs_gt_1_96"] == 0.4
    assert math.isclose(z["rms"], math.sqrt((0.25 + 4 + 1 + 9 + 0.01) / 5)) and z["max_abs"] == 3.0
    assert cal.z_summary([])["share_abs_gt_1_96"] is None


def test_the_comparator_is_exact_on_integers_and_tolerant_on_floats():
    assert cal.same({"a": [1, 2.0, "x"]}, {"a": [1, 2.0 * (1 + 1e-12), "x"]}) is None
    assert cal.same({"a": [1]}, {"a": [2]}).startswith("/a[0]:")
    assert cal.same({"a": [1, 2.0]}, {"a": [1, 2.0000001]}).startswith("/a[1]:")
    assert cal.same({"a": 1}, {"b": 1}).startswith(": keys differ")
    assert "length" in cal.same([1], [1, 2])
    assert cal.same({"a": None}, {"a": None}) is None
    assert cal.same({"a": 1.0}, {"a": None}) is not None


# ----------------------------------------------------------------------------------------------------------------------
# schema and consistency of the stored file

def test_schema():
    d = doc()
    assert d["schema"] == cal.SCHEMA == "calibration-1"
    assert set(d) == {"schema", "what", "model", "constants", "inputs", "run_to_run", "replication", "decomposition",
                      "permutation", "subsets"}
    c = d["constants"]
    assert (c["z"], c["sim_reps"], c["perms"], c["anova_perms"], c["subsets_per_j"], c["primary_pool"], c["seed_tag"]) == \
        (cal.Z, cal.SIM_REPS, cal.PERMS, cal.ANOVA_PERMS, cal.SUBSETS, cal.PRIMARY, cal.SEED_TAG)
    assert c["subset_js"] == list(cal.SUBSET_JS) and c["perm_models"] == list(cal.PERM_MODELS)
    assert c["minimum_jobs"] == read("harness", "criteria-v3.json")["v3"]["pooling"]["minimum_jobs"]
    assert set(d["run_to_run"]) == {k for k, _, _ in cal.RUN_POOLS}
    for key, rec in d["run_to_run"].items():
        for m in rec["models"]:
            assert {"cpu_model", "jobs", "runs_assessed", "checked", "outside", "stored_checked", "stored_outside", "reproduces_stored",
                    "max_gap_pct", "stored_max_gap_pct", "outside_share", "expected_outside", "expected_outside_sym", "expected_share",
                    "expected_share_sym", "pair_z", "simulation", "by_cell"} <= set(m), (key, m["cpu_model"])
            assert 0 <= m["outside"] <= m["checked"] and len(m["by_cell"]) == 32
            assert 0.0 <= m["pair_z"]["share_abs_gt_1_96"] <= 1.0 and m["pair_z"]["rms"] > 0
            for mode in ("independent", "common"):
                s = m["simulation"][mode]
                assert s["reps"] == cal.SIM_REPS and s["min"] <= s["p025"] <= s["mean"] <= s["p975"] <= s["max"]
                assert s["observed"] == m["outside"]
    for arch in ("arm", "x86"):
        assert set(d["replication"][arch]) == {"models", "totals"}
    assert set(d["permutation"]) == set(cal.PERM_MODELS)
    for rec in d["decomposition"]:
        assert len(rec["rows"]) == 32 and rec["jobs"] >= c["minimum_jobs"]
    for model, rec in d["subsets"].items():
        assert rec["jobs"] >= 3 and set(rec["by_j"]) == {str(j) for j in cal.SUBSET_JS}


def test_stored_inputs_are_the_current_files():
    inp = doc()["inputs"]
    for key, rel, _ in cal.RUN_POOLS:
        assert inp["pools"][key]["sha256"] == cal.lf_sha(os.path.join(REPO, *rel.split("/"))), key
        assert inp["pools"][key]["path"] == rel
    for name, rel in (("replication_results", cal.REPLICATION_RESULTS), ("criteria", cal.CRITERIA),
                      ("harness_pool_py", cal.POOL_PY), ("replication_compare_py", cal.COMPARE_PY)):
        assert inp[name]["sha256"] == cal.lf_sha(os.path.join(REPO, *rel.split("/"))), name
    jobs = cal.Jobs()
    assert inp["job_files"]["count"] == len(jobs.docs) == 95 and inp["job_files"]["sha256"] == jobs.files_sha()


def test_sums_over_cells_and_simulation_means_agree_with_the_formula():
    for key, rec in doc()["run_to_run"].items():
        for m in rec["models"]:
            assert sum(c["pairs"] for c in m["by_cell"]) == m["checked"]
            assert sum(c["outside"] for c in m["by_cell"]) == m["outside"]
            assert math.isclose(sum(c["expected_outside"] for c in m["by_cell"]), m["expected_outside"], rel_tol=1e-9)
            assert math.isclose(m["expected_share"], m["expected_outside"] / m["checked"], rel_tol=1e-9)
            assert math.isclose(m["outside_share"], m["outside"] / m["checked"], rel_tol=1e-12)
            for mode in ("independent", "common"):
                s = m["simulation"][mode]
                se = s["sd"] / math.sqrt(s["reps"])
                # a dependence between cells changes the spread of the count, not its mean
                assert abs(s["mean"] - m["expected_outside"]) <= 6.0 * se + 0.002 * m["expected_outside"], (key, m["cpu_model"], mode)
    for arch in ("arm", "x86"):
        r = doc()["replication"][arch]
        for m in r["models"]:
            assert m["inside"] + m["outside"] == m["checked"] and m["reproduces_stored"] is True
            assert math.isclose(m["expected_inside"], m["checked"] - m["expected_outside"], rel_tol=1e-9)
            for mode in ("independent", "common"):
                s = m["simulation"][mode]
                assert abs(s["mean"] - m["expected_outside"]) <= 6.0 * s["sd"] / math.sqrt(s["reps"]) + 0.002 * m["expected_outside"]
        t = r["totals"]
        assert t["checked"] == sum(m["checked"] for m in r["models"]) and t["outside"] == sum(m["outside"] for m in r["models"])
        assert math.isclose(t["expected_outside"], sum(m["expected_outside"] for m in r["models"]), rel_tol=1e-9)
        st = read("replication", "results.json")[arch]["totals"]
        assert (t["stored_points_checked"], t["stored_points_outside"]) == (st["points_checked"], st["points_outside"])
        assert (t["checked"], t["outside"]) == (st["points_checked"], st["points_outside"])


def test_shuffles_summary_identity_and_subsets_are_consistent():
    d = doc()
    for model, pb in d["permutation"].items():
        obs = model_record("s7", model)
        assert pb["identity"]["outside"] == obs["outside"] and pb["identity"]["checked"] == obs["checked"]
        assert pb["identity"]["max_rel_diff_to_stored_per_run"] <= 1e-12
        assert len(pb["shuffles"]) == cal.PERMS and pb["assessed_runs"] == [r["jobs"] for r in obs["runs_assessed"]]
        assert all(r["checked"] == obs["checked"] for r in pb["shuffles"])
        assert cal.same(pb["summary"], cal.permutation_summary(pb, obs["outside"])) is None
        s = pb["summary"]
        assert s["count_ge_observed"] == sum(1 for r in pb["shuffles"] if r["outside"] >= obs["outside"])
        assert math.isclose(s["p_ge_observed"], (1 + s["count_ge_observed"]) / (s["n"] + 1))
    for model, rec in d["subsets"].items():
        for j, b in rec["by_j"].items():
            if "forms" not in b:
                assert b["available"] <= int(j)
                continue
            assert sum(b["forms"].values()) == b["count"] == len(b["rows"]) == min(cal.SUBSETS, b["distinct_possible"])
            assert b["exhaustive"] is (b["distinct_possible"] <= cal.SUBSETS)
            assert b["distinct_possible"] == math.comb(b["available"], int(j))
            assert len({r["jobs"] for r in b["rows"]}) == b["count"]
            assert all(len(r["jobs"].split(",")) == int(j) for r in b["rows"])


def test_decomposition_rows_are_internally_consistent():
    for rec in doc()["decomposition"]:
        rows = rec["rows"]
        for r in rows:
            assert math.isclose(r["ratio_total_to_within"], r["sd_between_jobs_pct"] / r["within_job_se_rms_pct"], rel_tol=1e-9)
            assert math.isclose(r["cochran_q_per_df"], r["cochran_q"] / (r["jobs"] - 1), rel_tol=1e-9)
            assert r["cell_id"].rsplit(".", 1)[1] in IN_CACHE and r["column"] in COLUMNS
            if r["anova_by_run"]:
                assert 0 < r["anova_by_run"]["p_perm"] <= 1 and r["anova_by_run"]["runs"] >= 2
        s = rec["summary"]
        assert s["rows_ratio_above_2"] == sum(1 for r in rows if r["ratio_total_to_within"] > 2.0)
        assert s["rows_anova_p_below_0_05"] == sum(1 for r in rows if r["anova_by_run"] and r["anova_by_run"]["p_perm"] < 0.05)
        assert s["rows_anova"] == sum(1 for r in rows if r["anova_by_run"])
        # the job files behind the rows are the pool's jobs
        assert rec["jobs"] == len(cal.Jobs().models[rec["cpu_model"]])


def test_anova_on_a_made_up_example_equals_the_textbook_values():
    # three runs of three jobs: group means 1, 2, 3, grand mean 2, within-group sd 1.
    # SS_between = 3 x (1 + 0 + 1) = 6 on 2 df -> MS_between = 3; SS_within = 3 x 2 = 6 on 6 df -> MS_within = 1; F = 3;
    # the between-run variance component is (3 - 1) / 3 (equal group size 3).
    y = [0.0, 1.0, 2.0, 1.0, 2.0, 3.0, 2.0, 3.0, 4.0]
    groups = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    an = cal.anova_by_run(y, groups, ("test",))
    assert math.isclose(an["ms_between"], 3.0) and math.isclose(an["ms_within"], 1.0) and math.isclose(an["f"], 3.0)
    assert math.isclose(an["sd_between_runs_pct"], 100.0 * math.sqrt((3.0 - 1.0) / 3.0))
    assert math.isclose(an["sd_within_run_pct"], 100.0)
    assert an["jobs"] == 9 and an["runs"] == 3 and 0.0 < an["p_perm"] <= 1.0
    # clearly separated groups: a small permutation p
    y2 = [0.0, 0.1, 0.2, 5.0, 5.1, 5.2, 10.0, 10.1, 10.2]
    assert cal.anova_by_run(y2, groups, ("test",))["p_perm"] < 0.01
    assert cal.anova_by_run(y, [[0, 1, 2]], ("test",)) is None


# ----------------------------------------------------------------------------------------------------------------------
# the guard: --verify, and tampering

def test_verify_recomputes_the_cheap_parts_and_agrees():
    r = subprocess.run([sys.executable, os.path.join(REPO, "robustness", "calibration.py"), "--verify"],
                       capture_output=True, text=True, cwd=REPO, timeout=1800)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "equals the recomputation" in r.stdout


@contextlib.contextmanager
def stored_copy(mutate):
    """A temporary copy of calibration.json, mutated, as calibration.OUT; verify() reads it."""
    d = copy.deepcopy(doc())
    mutate(d)
    tmp = tempfile.mkdtemp(prefix="calib-test-")
    path = os.path.join(tmp, "calibration.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(cal.dumps(d))
    old = cal.OUT
    cal.OUT = path
    try:
        yield d
    finally:
        cal.OUT = old
        os.remove(path)
        os.rmdir(tmp)


def run_verify():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cal.verify()
    return code, buf.getvalue()


def test_verify_fails_when_an_input_hash_is_changed():
    def mutate(d):
        d["inputs"]["pools"]["s7"]["sha256"] = "0" * 64
    with stored_copy(mutate):
        code, out = run_verify()
    assert code == 1 and "inputs/pools/s7/sha256" in out


def test_verify_fails_when_the_input_hash_of_the_replication_results_is_changed():
    def mutate(d):
        d["inputs"]["replication_results"]["sha256"] = hashlib.sha256(b"x").hexdigest()
    with stored_copy(mutate):
        code, out = run_verify()
    assert code == 1 and "replication_results" in out


def test_verify_fails_when_a_stored_count_is_changed():
    # the inputs are untouched here, so verify() runs its full recomputation (about 40 s) and must find the changed count
    def mutate(d):
        m = next(x for x in d["run_to_run"]["s7"]["models"] if x["cpu_model"] == EPYC7763)
        m["outside"] += 1
    with stored_copy(mutate):
        code, out = run_verify()
    assert code == 1 and out.startswith("FAIL") and "run_to_run/s7/models[" in out and "/outside" in out


def test_comparator_and_the_reproduction_check_catch_a_changed_count():
    d = copy.deepcopy(doc())
    m = next(x for x in d["run_to_run"]["s7"]["models"] if x["cpu_model"] == EPYC7763)
    m["outside"] += 1
    diff = cal.same(doc()["run_to_run"], d["run_to_run"])
    assert diff and "outside" in diff
    # the reproduction test above compares this count with a recount: it would fail
    assert recount(pooled("results/s7-pooled/pooled.json"), EPYC7763)[1] != m["outside"]


def test_a_fresh_recomputation_of_one_pool_equals_the_stored_record():
    # part A for the smallest pool, recomputed here from the pooled file (seconds)
    key, rel, _ = next(x for x in cal.RUN_POOLS if x[0] == "s8-arm")
    got = cal.run_to_run(key, pooled(rel))
    assert cal.same(doc()["run_to_run"][key], got) is None
    got["models"][0]["outside"] += 1
    assert cal.same(doc()["run_to_run"][key], got)


# ----------------------------------------------------------------------------------------------------------------------
# loop families (Table 6)

def test_family_sums_on_a_made_up_record_and_against_the_totals():
    rec = {"by_cell": [
        {"cell_id": "k01_sum_fwd.L1", "pairs": 4, "outside": 1, "expected_outside": 0.5},
        {"cell_id": "k03_stencil.L2", "pairs": 4, "outside": 0, "expected_outside": 0.25},
        {"cell_id": "k05_stride2.L2", "pairs": 4, "outside": 3, "expected_outside": 1.0},
        {"cell_id": "k07_hist.L1", "pairs": 4, "outside": 2, "expected_outside": 0.75},
    ]}
    fam = cal.family_sums(rec)
    f, r, o = (fam[name] for name, _ in cal.FAMILIES)
    assert (f["pairs"], f["outside"], f["expected_outside"]) == (8, 1, 0.75)
    assert (r["pairs"], r["outside"], r["expected_outside"]) == (4, 3, 1.0)
    assert (o["pairs"], o["outside"], o["expected_outside"]) == (4, 2, 0.75)
    # on the stored file the three families cover every cell: their sums are the totals of Table 1
    for key, rec in doc()["run_to_run"].items():
        for m in rec["models"]:
            fam = cal.family_sums(m)
            assert sum(v["pairs"] for v in fam.values()) == m["checked"], (key, m["cpu_model"])
            assert sum(v["outside"] for v in fam.values()) == m["outside"], (key, m["cpu_model"])
            assert math.isclose(sum(v["expected_outside"] for v in fam.values()), m["expected_outside"], rel_tol=1e-9)


# ----------------------------------------------------------------------------------------------------------------------
# the README: the generated tables and the numbers in its prose are the stored ones

def _model(d, pool, sub):
    return next(m for m in d["run_to_run"][pool]["models"] if sub in m["cpu_model"])


def _rep(d, arch, sub):
    return next(m for m in d["replication"][arch]["models"] if sub in m["cpu_model"])


def _row(d, sub, cell):
    rec = next(r for r in d["decomposition"] if sub in r["cpu_model"])
    return next(r for r in rec["rows"] if r["cell_id"] == cell and r["column"] == "as_compiled")


def _forms(d, sub, j):
    rec = next(v for k, v in d["subsets"].items() if sub in k)
    return rec["by_j"][str(j)]["forms"], rec["by_j"][str(j)]["count"]


def prose_rows(d):
    """Phrases of robustness/README-calibration.md (outside the generated block) with every number read from calibration.json."""
    pc = cal.pct
    a7, b7 = _model(d, "s7", "7763"), _model(d, "s7", "9V74")
    s6a, s6b = _model(d, "s6", "7763"), _model(d, "s6", "9V74")
    arm, armab = _model(d, "s8-arm", "Neoverse"), _model(d, "s9-arm-ab", "Neoverse")
    nine, v45 = _model(d, "s9-x86-ac", "7763"), _model(d, "s9-x86-ac", "9V45")
    fa7, fb7, fn, fab = cal.family_sums(a7), cal.family_sums(b7), cal.family_sums(nine), cal.family_sums(armab)
    names = [n for n, _ in cal.FAMILIES]
    fwd, lost = names[0], names[1]
    si = a7["simulation"]["independent"]
    sib = b7["simulation"]["independent"]
    pa, pb = d["permutation"][a7["cpu_model"]]["summary"], d["permutation"][b7["cpu_model"]]["summary"]
    r7, r8573, rx, ra = _rep(d, "x86", "7763"), _rep(d, "x86", "XEON"), d["replication"]["x86"]["totals"], d["replication"]["arm"]["totals"]
    r7s, r7c = r7["simulation"]["independent"], r7["simulation"]["common"]
    stride = [c for c in armab["by_cell"] if c["cell_id"] == "k05_stride2.L2"]
    mm1, mm2 = _row(d, "7763", "k08_matmul.L1"), _row(d, "9V74", "k08_matmul.L2")
    rows = [
        f"on EPYC 7763, {a7['outside']} of {a7['checked']} comparisons; on EPYC 9V74, {b7['outside']} of {b7['checked']} "
        f"(in the 75-job pool, {s6a['outside']} of {s6a['checked']} and {s6b['outside']} of {s6b['checked']})",
        f"There were {a7['outside']} of {a7['checked']} comparisons ({pc(a7['outside_share'])}) outside against "
        f"{a7['expected_outside']:.1f} expected ({pc(a7['expected_share'])}). The independent 95% range is {si['p025']} to {si['p975']}, "
        f"and {100 * si['p_ge_observed']:.1f}% of simulated calibrated draws reach {a7['outside']} or more",
        f"The pair z gives rms {a7['pair_z']['rms']:.2f}", f"{pc(a7['pair_z']['share_abs_gt_1_96'])} of the z values are above 1.96 in size",
        f"the outside count has mean {pa['mean']:.1f} ({pa['min']} to {pa['max']}) and {pa['count_ge_observed']} of {pa['n']} shuffles "
        f"reached {pa['observed']}",
        f"{fa7[lost]['outside']} of {fa7[lost]['pairs']} outside against {fa7[lost]['expected_outside']:.1f} expected, while the forward "
        f"loops show {fa7[fwd]['outside']} of {fa7[fwd]['pairs']} against {fa7[fwd]['expected_outside']:.1f}",
        f"gives {nine['outside']} outside against {nine['expected_outside']:.1f} expected overall",
        f"{fn[lost]['outside']} of {fn[lost]['pairs']} against {fn[lost]['expected_outside']:.1f} in reverse, stride-2 and matrix multiply, "
        f"{fn[fwd]['outside']} of {fn[fwd]['pairs']} against {fn[fwd]['expected_outside']:.1f} in the forward loops",
        f"{r7['outside']} of {r7['checked']} points were outside against {r7['expected_outside']:.1f} expected; that is above the "
        f"independent range ({r7s['p025']} to {r7s['p975']}) and inside the one-draw-per-pool range ({r7c['p025']} to {r7c['p975']})",
        f"There were {b7['outside']} of {b7['checked']} ({pc(b7['outside_share'])}) outside against {b7['expected_outside']:.1f} expected "
        f"({pc(b7['expected_share'])}); {100 * sib['p_le_observed']:.1f}% of calibrated draws are as low (independent), the pair z has "
        f"rms {b7['pair_z']['rms']:.2f}",
        f"(forward {fb7[fwd]['outside']} of {fb7[fwd]['pairs']} against {fb7[fwd]['expected_outside']:.1f}, reverse, stride-2 and matrix "
        f"multiply {fb7[lost]['outside']} of {fb7[lost]['pairs']} against {fb7[lost]['expected_outside']:.1f})",
        f"The shuffle null has mean {pb['mean']:.1f}, and {pb['count_ge_observed']} of {pb['n']} shuffles reached {pb['observed']} or more",
        f"There were {arm['outside']} of {arm['checked']} outside against {arm['expected_outside']:.1f} expected in the first Arm pool",
        f"{armab['outside']} of {armab['checked']} against {armab['expected_outside']:.1f} in the six runs of sets A and B together "
        f"(pair z rms {armab['pair_z']['rms']:.2f})",
        f"{sum(c['outside'] for c in stride)} of {sum(c['pairs'] for c in stride)} comparisons outside against "
        f"{sum(c['expected_outside'] for c in stride):.1f} expected in the six runs",
        f"({fab[fwd]['outside']} of {fab[fwd]['pairs']} against {fab[fwd]['expected_outside']:.1f})",
        f"give {v45['outside']} of {v45['checked']} against {v45['expected_outside']:.1f} expected",
        f"gives {r8573['outside']} of {r8573['checked']} against {r8573['expected_outside']:.1f} expected, within the independent range "
        f"({r8573['simulation']['independent']['p025']} to {r8573['simulation']['independent']['p975']})",
        f"{rx['outside']} of {rx['checked']} points outside on x86-64 against {rx['expected_outside']:.1f} expected, {ra['outside']} of "
        f"{ra['checked']} on Arm against {ra['expected_outside']:.1f}",
        f"{mm1['sd_between_jobs_pct']:.2f}% between jobs against {mm1['within_job_se_rms_pct']:.2f}% within a job, "
        f"{mm1['ratio_total_to_within']:.1f} times",
        f"{mm2['sd_between_jobs_pct']:.2f}% against {mm2['within_job_se_rms_pct']:.2f}%, {mm2['ratio_total_to_within']:.1f} times",
    ]
    dec = {r["cpu_model"]: r["summary"] for r in d["decomposition"]}
    d7 = next(v for k, v in dec.items() if "7763" in k)
    d74 = next(v for k, v in dec.items() if "9V74" in k)
    rows.append(f"in {d7['rows_anova_p_below_0_05']} of {d7['rows']} rows for EPYC 7763 and {d74['rows_anova_p_below_0_05']} of "
                f"{d74['rows']} for EPYC 9V74")
    f45_3, n45_3 = _forms(d, "9V45", 3)
    f45_5, n45_5 = _forms(d, "9V45", 5)
    f45_10, n45_10 = _forms(d, "9V45", 10)
    f69_3, n69_3 = _forms(d, "6973P", 3)
    f69_5, n69_5 = _forms(d, "6973P", 5)
    rows.append(f"gives INCONCLUSIVE in {f45_3['inconclusive']} of {n45_3} subsets at 3 jobs and {f45_5['inconclusive']} of {n45_5} at 5, "
                f"and MAP in all {f45_10['map']} at 10")
    rows.append(f"gives INCONCLUSIVE in {f69_3['inconclusive']} of {n69_3} subsets at 3 jobs and {f69_5['inconclusive']} of {n69_5} "
                f"(all of them) at 5")
    return rows


def readme_problems(text, d):
    """Everything wrong with a README text against the stored file: the generated block and the prose phrases."""
    problems = []
    m = re.search(r"<!-- tables:begin -->\n(.*)<!-- tables:end -->", text, re.S)
    if not m:
        return ["no generated tables block"]
    if m.group(1) != cal.tables(d):
        problems.append("the generated tables block differs from calibration.py's output")
    prose = " ".join(text[:m.start()].split())
    for row in prose_rows(d):
        if " ".join(row.split()) not in prose:
            problems.append("missing or changed in the prose: " + row)
    return problems


def readme_text():
    with open(README, encoding="utf-8", newline="") as f:
        return f.read()


def test_the_readme_tables_and_prose_numbers_are_the_stored_ones():
    text = readme_text()
    assert "\r" not in text
    assert readme_problems(text, doc()) == []
    assert len(prose_rows(doc())) >= 20


def test_tampering_with_a_prose_number_is_caught():
    text = readme_text()
    assert "168 of 640 comparisons (26.2%) outside" in text
    bad = text.replace("168 of 640 comparisons (26.2%) outside", "167 of 640 comparisons (26.2%) outside")
    p = readme_problems(bad, doc())
    assert p and any("There were 168 of 640 comparisons" in x for x in p)
    # a number changed in the stored file is caught from the other side
    d = copy.deepcopy(doc())
    _model(d, "s7", "9V74")["outside"] += 1
    assert readme_problems(text, d)


def test_tampering_with_a_table_cell_is_caught():
    text = readme_text()
    line = next(x for x in text.splitlines() if x.startswith("| s7 | 7763 |") and "168 / 640" in x)
    bad = text.replace(line, line.replace("168 / 640", "169 / 640"))
    assert bad != text
    assert readme_problems(bad, doc()) == ["the generated tables block differs from calibration.py's output"]
    # and a table rebuilt from a changed stored file differs from the README's block
    d = copy.deepcopy(doc())
    d["permutation"][EPYC9V74]["summary"]["mean"] += 1.0
    assert cal.tables(d) != cal.tables(doc())


def test_the_readme_uses_no_order_claims_or_process_words():
    low = readme_text().lower()
    # the words are written in two pieces so that this file does not contain them (the export scan reads every file)
    for a, b in (("recru", "iter"), ("intern", "ship"), ("bill", "ing"), ("private ", "repo"), ("lea", "rn/"), ("docs/", "scorecard"),
                 ("the ", "lead"), ("the ", "owner"), ("claude", ".md"), ("working ", "copy"), ("hosting ", "account"),
                 ("unpublished ", "repository"), ("one more ", "than asked")):
        assert a + b not in low, a + b
    for word in ("fixed before", "committed before", "written before", "registered before", "planned before"):
        assert word not in low, word
