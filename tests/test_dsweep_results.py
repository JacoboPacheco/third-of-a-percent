"""The matrix-multiply d-sweep results (plan: dsweep/PLAN.md, hash stored in every file): results/s10-dsweep-*, the pooled
file dsweep/analyze.py wrote, site/data/dsweep.json, and the checks scripts/check.py runs over them.

What the plan fixed before any run, and what the runs gave under it:
  AMD EPYC 7763 (9 jobs, 2 runs)  H2 in both columns: the excess FAST adds per inner call is proportional to d
                                  (fixed share 0.032 as compiled, 0.040 aligned); the extra instructions per inner call grow with d
  Neoverse-N2 (6 jobs, 1 run)     "neither": the two columns disagree (as compiled the excess falls, fixed share 1.332; aligned
                                  H1, 1.090), and the rule does not claim a word that does not survive moving the loops;
                                  the extra instructions per inner call are 77.0x at every d = 4 mod 8 from 12 to 148
  EPYC 9V45 (2 jobs), Xeon 8573C (1 job)  too few jobs: no word

Four kinds of test. (1) The plan hash: sha256 of dsweep/PLAN.md equals the plan_sha256 stored in every s10 file, so any edit to
the plan, even of one word, fails here. (2) Stored data: the values above, and the values quoted for the page, read from the files;
the point values (ratios, the excess per inner call, the fixed share, the instruction counts) are recomputed from the raw samples
of the 18 job files by code written in this file (the intervals are bootstrap numbers and are recomputed by scripts/check.py,
which re-pools); the text files beside the pooled files (table.md, dsweep-pooled.md, report.txt) equal what dsweep/analyze.py's
renderers give for the stored pooled JSON, byte for byte. (3) site/data/dsweep.json: equal to a fresh build, equal to the pooled file where it copies, and additive.
(4) scripts/check.py's d-sweep step on a small scratch world: the plan guard, the completeness of the pool, the re-pool.

Offline; the site builds go to temporary folders. No fixtures, so scripts/check.py's built-in runner runs it."""
import atexit
import contextlib
import copy
import glob
import hashlib
import importlib.util
import io
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

RESULTS = os.path.join(REPO, "results")
POOLED_REL = "results/s10-dsweep-pooled/dsweep-pooled.json"
RUN_IDS = ("39018966032", "39018969973", "39018974239")
COMMIT = "8c874ec4e4d5b6b568a390264eef1f6f0f160885"
EPYC7763, EPYC9V45, XEON8573C, N2 = ("AMD EPYC 7763 64-Core Processor", "AMD EPYC 9V45 96-Core Processor",
                                     "INTEL(R) XEON(R) PLATINUM 8573C", "Neoverse-N2")


def _load(key, rel):
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


def check_module():
    return _load("dsweep_test_check", os.path.join("scripts", "check.py"))


def builder():
    return _load("dsweep_test_build", os.path.join("scripts", "build_site_data.py"))


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def lf_sha256(path):
    """Written again here (not imported from the analysis or check.py): sha256 with CRLF read as LF."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def job_files():
    return sorted(glob.glob(os.path.join(RESULTS, "s10-dsweep-run-*", "dsweep-job-*", "dsweep.json")))


@lru_cache(maxsize=None)
def pooled():
    return read(os.path.join(REPO, *POOLED_REL.split("/")))


@lru_cache(maxsize=None)
def site():
    return read(os.path.join(REPO, "site", "data", "dsweep.json"))


@lru_cache(maxsize=None)
def jobs_by_model():
    out = {}
    for f in job_files():
        doc = read(f)
        out.setdefault(doc["run"]["runner"]["cpu_model"], []).append(doc)
    return out


def block(model):
    return next(b for b in pooled()["cpus"] if b["cpu_model"] == model)


def srow(model, d):
    return next(r for r in next(m for m in site()["models"] if m["cpu_model"] == model)["rows"] if r["d"] == d)


def prow(model, col, d):
    return next(r for r in block(model)["columns"][col]["rows"] if r["d"] == d)


def f3(x):
    return f"{x:.3f}"


def f2(x):
    return f"{x:.2f}"


# ---------------------------------------------------------------- (1) the plan hash

def test_the_plan_hash_is_stored_in_every_s10_file():
    want = lf_sha256(os.path.join(REPO, "dsweep", "PLAN.md"))
    files = job_files()
    assert len(files) == 18
    pools = [os.path.join(REPO, *POOLED_REL.split("/"))] + sorted(
        glob.glob(os.path.join(RESULTS, "s10-dsweep-run-*", "dsweep-pooled", "dsweep-pooled.json")))
    assert len(pools) == 4
    for f in files + pools:
        assert read(f)["plan_sha256"] == want, (
            f"{os.path.relpath(f, REPO)} was produced under another dsweep/PLAN.md: the plan was edited after the runs")
    assert site()["plan_sha256"] == want
    # the plan's own words: the pre-registered statistic and the two hypotheses the words are about
    plan = open(os.path.join(REPO, "dsweep", "PLAN.md"), encoding="utf-8").read()
    assert "H1" in plan and "H2" in plan and "fixed share" in plan


def test_the_check_fails_loudly_when_the_plan_is_edited():
    chk = check_module()
    sweeps = job_files()
    pools = chk.dsweep_pooled_files(RESULTS)
    assert len(pools) == 4

    def run(plan):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = chk.check_dsweep_plan(sweeps, pools, plan=plan)
        return ok, buf.getvalue()
    ok, out = run(chk.DSWEEP_PLAN)
    assert ok and "were produced under" in out and "18 dsweep.json and 4 dsweep-pooled.json" in out, out
    text = open(os.path.join(REPO, "dsweep", "PLAN.md"), "rb").read()
    with tempfile.TemporaryDirectory() as tmp:
        same = os.path.join(tmp, "PLAN.md")
        with open(same, "wb") as f:
            f.write(text)
        assert run(same)[0]
        crlf = os.path.join(tmp, "PLAN-crlf.md")   # a Windows checkout: the same plan
        with open(crlf, "wb") as f:
            f.write(text.replace(bytes([13, 10]), bytes([10])).replace(bytes([10]), bytes([13, 10])))
        assert run(crlf)[0]
        edited = os.path.join(tmp, "PLAN-edited.md")   # one word changed
        with open(edited, "wb") as f:
            f.write(text.replace(b"fixed share", b"fixed-share", 1))
        ok, out = run(edited)
        assert not ok and out.count("FAIL") == 22 and "plan was edited after the run" in out, out
        # and a stored hash that is not the plan's
        bad = os.path.join(tmp, "dsweep.json")
        doc = read(sweeps[0])
        doc["plan_sha256"] = "0" * 64
        with open(bad, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert chk.check_dsweep_plan([bad], []) is False
        assert "stored plan_sha256 000000000000" in buf.getvalue()


# ---------------------------------------------------------------- (2) what was run

def test_three_runs_of_six_jobs_from_one_commit_with_the_full_repetitions():
    docs = [read(f) for f in job_files()]
    assert sorted({d["run"]["id"] for d in docs}) == sorted(RUN_IDS)
    assert {d["run"]["commit"] for d in docs} == {COMMIT}
    assert all(d["smoke"] is False and d["reps_per_side"] == 40 for d in docs)
    per_run = {}
    for d in docs:
        per_run.setdefault(d["run"]["id"], {}).setdefault(d["run"]["runner"]["cpu_model"], 0)
        per_run[d["run"]["id"]][d["run"]["runner"]["cpu_model"]] += 1
    assert per_run == {"39018966032": {N2: 6}, "39018969973": {EPYC7763: 3, EPYC9V45: 2, XEON8573C: 1}, "39018974239": {EPYC7763: 6}}
    assert {m: len(v) for m, v in jobs_by_model().items()} == {EPYC7763: 9, EPYC9V45: 2, XEON8573C: 1, N2: 6}
    assert {d["run"]["runner"]["arch"] for d in jobs_by_model()[N2]} == {"aarch64"}
    assert {d["run"]["runner"]["arch"] for d in jobs_by_model()[EPYC7763]} == {"x86_64"}
    # the ladders (the study L1 d and L2 d, the fit values congruent to the L1 d modulo 8, the scan of the seven below it)
    lad = block(N2)["ladder"]
    assert (lad["study_l1_d"], lad["study_l2_d"], lad["residue"]) == (52, 209, 4)
    assert lad["fit"] == [12, 20, 28, 36, 44, 52] and lad["scan"] == list(range(45, 52)) and lad["bridge"] == [76, 108, 148]
    lad = block(EPYC7763)["ladder"]
    assert (lad["study_l1_d"], lad["study_l2_d"], lad["residue"]) == (36, 147, 4)
    assert lad["fit"] == [12, 20, 28, 36] and lad["scan"] == list(range(29, 36)) and lad["bridge"] == [52, 76, 100]
    assert block(EPYC9V45)["ladder"]["study_l1_d"] == 45 and block(EPYC9V45)["ladder"]["study_l2_d"] == 209


def test_the_words_the_pre_registered_rule_gave():
    p = pooled()
    assert (p["rule"]["minimum_jobs"], p["rule"]["h1_share_band"], p["rule"]["h2_share_band"], p["rule"]["falls_share_above"]) == (
        3, [0.8, 1.2], [-0.2, 0.2], 1.2)
    assert [(b["cpu_model"], b["jobs"], b["verdict"]["word"]) for b in p["cpus"]] == [
        (EPYC7763, 9, "H2"), (EPYC9V45, 2, "too few jobs"), (XEON8573C, 1, "too few jobs"), (N2, 6, "neither")]
    assert [len(b["runs"]) for b in p["cpus"]] == [2, 1, 1, 1] and all(b["problems"] == [] for b in p["cpus"])
    # EPYC 7763: H2 in both columns, the shares and their 95% intervals to three decimals
    b = block(EPYC7763)
    assert b["verdict"]["columns_agree"] is True and {c: w["word"] for c, w in b["words"].items()} == {"as_compiled": "H2", "aligned": "H2"}
    for col, (share, lo, hi) in {"as_compiled": ("0.032", "0.027", "0.035"), "aligned": ("0.040", "0.037", "0.043")}.items():
        ex = b["columns"][col]["excess"]
        assert (f3(ex["share"]), f3(ex["share_ci95"][0]), f3(ex["share_ci95"][1])) == (share, lo, hi), col
        assert -0.2 <= ex["share_ci95"][0] and ex["share_ci95"][1] <= 0.2
    # Neoverse-N2: the columns disagree; the rule claims no word
    b = block(N2)
    assert b["verdict"]["word"] == "neither" and b["verdict"]["columns_agree"] is False
    assert {c: w["word"] for c, w in b["words"].items()} == {"as_compiled": "falls", "aligned": "H1"}
    for col, (share, lo, hi) in {"as_compiled": ("1.332", "1.330", "1.334"), "aligned": ("1.090", "1.089", "1.091")}.items():
        ex = b["columns"][col]["excess"]
        assert (f3(ex["share"]), f3(ex["share_ci95"][0]), f3(ex["share_ci95"][1])) == (share, lo, hi), col
    assert b["columns"]["as_compiled"]["excess"]["share_ci95"][0] > 1.2, "as compiled the whole interval is above the 'falls' line"
    assert 0.8 <= b["columns"]["aligned"]["excess"]["share_ci95"][0] and b["columns"]["aligned"]["excess"]["share_ci95"][1] <= 1.2
    assert "does not survive" in b["verdict"]["reason"] and "not claimed" in b["verdict"]["reason"]
    # the models under the minimum have no word and no analysis
    for m, jobs in ((EPYC9V45, 2), (XEON8573C, 1)):
        b = block(m)
        assert b["jobs"] == jobs < 3 and b["verdict"]["word"] == "too few jobs" and b["verdict"]["columns_agree"] is True
        assert {w["word"] for w in b["words"].values()} == {"too few jobs"}


def test_the_conditions_on_the_way_to_a_word_were_met_for_both_models():
    for m in (EPYC7763, N2):
        b = block(m)
        assert b["aa"]["half_width_pct"] <= 2.0, "the byte-identical A/A is under the rule's ceiling"
        for col in ("as_compiled", "aligned"):
            c = b["columns"][col]
            assert len(c["fit_ds"]) >= 4 and c["cost_unseen"] == []
            assert c["baseline"]["median_max_relative_residual"] <= 0.10
            assert c["excess"]["residual"]["median_max_relative_residual"] <= 0.15
            assert c["excess"]["undefined_fraction"] <= 0.025
    assert f3(block(EPYC7763)["aa"]["half_width_pct"]) == "0.061" and f3(block(N2)["aa"]["half_width_pct"]) == "0.034"
    assert (block(EPYC7763)["aa"]["d"], block(N2)["aa"]["d"]) == (28, 36), "timed at the middle d of the ladder"


def independent(docs, col):
    """From the raw samples of the jobs, with nothing imported from the analysis: per d the pooled FAST/NONE ratio (the geometric mean over
    jobs of the ratio of the medians) and the excess in ns per inner call (the mean over jobs of (t_F - t_N)/d^2), and the fixed share of
    the excess at the study d: the excess in units of each job's t_N per inner call at that d, averaged over jobs, fitted as
    fixed + per_element * d over the fit ladder by least squares, share = fixed / (fixed + per_element * d_max)."""
    lad = docs[0]["ladder"]
    by = [{p["d"]: p for p in doc["points"]} for doc in docs]
    n = len(docs)

    def med(j, d, side):
        return statistics.median(by[j][d][col][side + "_ns"])
    rows = {}
    for d in sorted(by[0]):
        rows[d] = {"ratio": math.exp(sum(math.log(med(j, d, "fast") / med(j, d, "none")) for j in range(n)) / n),
                   "excess": sum((med(j, d, "fast") - med(j, d, "none")) / (d * d) for j in range(n)) / n}
    fit = lad["fit"]
    d_max = fit[-1]
    scale = [med(j, d_max, "none") / (d_max * d_max) for j in range(n)]
    delta = [sum(((med(j, d, "fast") - med(j, d, "none")) / (d * d)) / scale[j] for j in range(n)) / n for d in fit]
    mx, my = sum(fit) / len(fit), sum(delta) / len(delta)
    slope = sum((x - mx) * (y - my) for x, y in zip(fit, delta)) / sum((x - mx) ** 2 for x in fit)
    fixed = my - slope * mx
    return rows, fixed / (fixed + slope * d_max), fixed, slope * d_max


def test_the_point_values_equal_a_recomputation_from_the_raw_samples():
    for m in (EPYC7763, N2):
        docs = jobs_by_model()[m]
        for col in ("as_compiled", "aligned"):
            rows, share, fixed, per_element = independent(docs, col)
            for d, r in rows.items():
                s = prow(m, col, d)
                assert math.isclose(s["ratio"], r["ratio"], rel_tol=1e-9), (m, col, d)
                assert math.isclose(s["excess_ns_per_inner"], r["excess"], rel_tol=1e-9), (m, col, d)
            ex = block(m)["columns"][col]["excess"]
            assert math.isclose(ex["share"], share, rel_tol=1e-9), (m, col)
            assert math.isclose(ex["fixed"], fixed, rel_tol=1e-9, abs_tol=1e-12) and math.isclose(ex["per_element_at_d_max"], per_element, rel_tol=1e-9)


def test_cachegrind_instruction_counts_are_the_same_in_every_job_and_equal_the_stored_ones():
    for m in (EPYC7763, N2, EPYC9V45, XEON8573C):
        docs = jobs_by_model()[m]
        stored = {r["d"]: r for r in block(m)["instructions"]["rows"]}
        assert block(m)["instructions"]["jobs_agree"] is True
        for p in docs[0]["points"]:
            d = p["d"]
            assert all(json.dumps({q["d"]: q["instr"] for q in doc["points"]}[d], sort_keys=True) == json.dumps(p["instr"], sort_keys=True)
                       for doc in docs), (m, d)
            extra = (p["instr"]["fast"] - p["instr"]["none"]) / (d * d)
            assert math.isclose(stored[d]["extra_per_inner"], extra, rel_tol=1e-12), (m, d)
            assert math.isclose(stored[d]["ratio"], p["instr"]["fast"] / p["instr"]["none"], rel_tol=1e-12)


def test_epyc_7763_the_extra_instructions_per_inner_call_grow_with_d():
    ins = {r["d"]: r["extra_per_inner"] for r in block(EPYC7763)["instructions"]["rows"]}
    assert (f2(ins[12]), f2(ins[36]), f2(ins[147])) == ("93.76", "313.60", "1321.90")
    ds = sorted(ins)
    assert ds == [12, 20, 28, 29, 30, 31, 32, 33, 34, 35, 36, 52, 76, 100, 147]
    ladder = [d for d in ds if not 29 <= d <= 35]   # the fit d values, the bridge and the study L2 d
    assert all(ins[a] < ins[b] for a, b in zip(ladder, ladder[1:])), "more extra instructions at every larger d of the ladder"
    # in the scan the count follows the leftover of the loop (d mod 8) as well: 290.55 at d = 32, 286.57 at d = 33
    assert ins[33] < ins[32] and all(ins[d] > ins[28] for d in range(29, 36))
    assert block(EPYC7763)["instructions"]["fit"]["slope"] > 9.0
    assert all(7.5 < ins[d] / d < 9.1 for d in ds), "about 8 to 9 extra instructions per element at every d: it grows with d, it is not a constant"
    # H2 in time as well: the excess per inner call grows with d (6.1 ns at d = 12, 16.8 at d = 36)
    assert (f2(prow(EPYC7763, "as_compiled", 12)["excess_ns_per_inner"]), f2(prow(EPYC7763, "as_compiled", 36)["excess_ns_per_inner"])) == ("6.10", "16.80")


def test_neoverse_n2_the_extra_instructions_per_inner_call_are_the_same_at_every_d_in_the_ladder():
    ins = {r["d"]: r["extra_per_inner"] for r in block(N2)["instructions"]["rows"]}
    assert f2(ins[12]) == "77.22" and f2(ins[148]) == "77.01" and f2(ins[209]) == "53.01"
    same_residue = [d for d in sorted(ins) if d % 8 == 4 and d <= 148]
    assert same_residue == [12, 20, 28, 36, 44, 52, 76, 108, 148]
    assert all(77.0 <= ins[d] < 77.25 for d in same_residue), {d: round(ins[d], 3) for d in same_residue}
    assert all(ins[a] > ins[b] for a, b in zip(same_residue, same_residue[1:])), "a constant just above 77, drifting down"
    assert abs(block(N2)["instructions"]["fit"]["slope"]) < 0.01 and f2(block(N2)["instructions"]["fit"]["intercept"]) == "77.22"
    # the other residues take another count (the leftover of the NEON loop): not a function of d alone
    assert [f2(ins[d]) for d in range(45, 52)] == ["85.05", "93.05", "101.05", "153.04", "53.04", "61.04", "69.04"]


def test_neoverse_n2_the_excess_in_time_is_not_proportional_to_d():
    ex = {d: prow(N2, "as_compiled", d)["excess_ns_per_inner"] for d in (12, 28, 52, 76, 108, 148, 209)}
    assert {d: f"{v:.3f}" for d, v in ex.items()} == {12: "4.857", 28: "3.990", 52: "3.881", 76: "3.808", 108: "3.908", 148: "2.819", 209: "0.462"}
    assert block(N2)["columns"]["as_compiled"]["excess"]["growth"] < 1, "the fitted excess is smaller at d = 52 than at d = 12"
    assert f3(block(N2)["columns"]["as_compiled"]["excess"]["growth"]) == "0.796"
    assert (f3(block(N2)["published"]["L1"]), f3(block(N2)["published"]["L2"])) == ("1.548", "1.016")
    assert (f3(prow(N2, "as_compiled", 52)["ratio"]), f3(prow(N2, "as_compiled", 209)["ratio"])) == ("1.548", "1.016")


def test_neoverse_n2_d_48_is_far_off_its_neighbours():
    r48 = prow(N2, "as_compiled", 48)
    assert (f3(r48["ratio"]), f3(r48["ci95"][0]), f3(r48["ci95"][1])) == ("2.634", "2.633", "2.635")
    assert f2(prow(N2, "as_compiled", 48)["ratio"]) == f2(prow(N2, "aligned", 48)["ratio"]) == "2.63"
    ins = {r["d"]: r["extra_per_inner"] for r in block(N2)["instructions"]["rows"]}
    assert f2(ins[48]) == "153.04"
    near = [prow(N2, "as_compiled", d)["ratio"] for d in (45, 46, 47, 49, 50, 51)]
    assert (f2(min(near)), f2(max(near))) == ("1.50", "1.62")
    assert r48["ratio"] > 1.6 * max(near)
    assert prow(N2, "as_compiled", 48)["roles"] == ["scan"] and 48 % 8 == 0
    # the one d of the scan that is a multiple of 8 is also the one the placement statistic does not flag
    flagged = block(N2)["placement"]["sensitive_ds"]
    assert 48 not in flagged and all(d in flagged for d in (45, 46, 47, 49, 50, 51))


# The text files beside a pooled file are output of dsweep/analyze.py, not data: results/s10-dsweep-pooled/table.md, and in each
# run's folder dsweep-pooled.md and report.txt (the program's printed output, with its two "wrote ..." lines). The functions that
# write them are called here on the stored pooled JSON, without being edited, so a hand-changed digit or a stale copy fails.

def analyze_module():
    return _load("dsweep_test_analyze", os.path.join("dsweep", "analyze.py"))


def derived_text_files():
    """[(pooled json, text file, kind)] for every pool: the pool of all runs and each run's own copy."""
    out = [("results/s10-dsweep-pooled/dsweep-pooled.json", "results/s10-dsweep-pooled/table.md", "markdown")]
    for run in RUN_IDS:
        d = f"results/s10-dsweep-run-{run}/dsweep-pooled"
        out += [(f"{d}/dsweep-pooled.json", f"{d}/dsweep-pooled.md", "markdown"), (f"{d}/dsweep-pooled.json", f"{d}/report.txt", "report")]
    return out


def read_text_lf(rel):
    with open(os.path.join(REPO, *rel.split("/")), "rb") as f:
        return f.read().decode("utf-8").replace("\r\n", "\n")


def check_derived_text(pooled_rel, text_rel, kind, text=None):
    """The text file equals what analyze.py's renderer gives for the stored pooled JSON, byte for byte (line endings aside)."""
    an = analyze_module()
    doc = read(os.path.join(REPO, *pooled_rel.split("/")))
    md = an.render_markdown(doc)
    text = read_text_lf(text_rel) if text is None else text
    if kind == "markdown":
        assert text == md, f"{text_rel} is not what dsweep/analyze.py's render_markdown gives for {pooled_rel}"
        return
    want = an.report(doc) + "\n\n" + md + "\n"
    assert text.startswith(want), f"{text_rel} does not start with what dsweep/analyze.py prints for {pooled_rel}"
    rest = text[len(want):].splitlines()
    assert len(rest) == 2 and all(line.startswith("wrote ") for line in rest), f"{text_rel}: after the printed report come only its two 'wrote' lines, found {rest}"
    assert rest[0].endswith("dsweep-pooled.json") and rest[1].endswith("dsweep-pooled.md"), rest


def test_the_text_files_beside_the_pooled_files_are_what_the_analysis_renders_from_them():
    assert len(derived_text_files()) == 7
    for pooled_rel, text_rel, kind in derived_text_files():
        check_derived_text(pooled_rel, text_rel, kind)


def test_every_text_file_beside_a_d_sweep_pooled_file_is_covered():
    listed = {t for _, t, _ in derived_text_files()}
    found = set()
    for pat in ("results/*dsweep-pooled/*", "results/*dsweep-run-*/dsweep-pooled/*"):
        for p in glob.glob(os.path.join(REPO, *pat.split("/"))):
            if not p.endswith(".json"):
                found.add(os.path.relpath(p, REPO).replace("\\", "/"))
    assert found == listed, f"text files not compared with a re-rendering: {sorted(found - listed)}; listed but missing: {sorted(listed - found)}"


def test_a_changed_digit_or_line_in_a_text_file_fails_the_rendering_check():
    for pooled_rel, text_rel, kind in derived_text_files():
        text = read_text_lf(text_rel)
        i = next(n for n, c in enumerate(text) if c.isdigit() and n > 200)
        changed = text[:i] + str((int(text[i]) + 1) % 10) + text[i + 1:]
        raised = False
        try:
            check_derived_text(pooled_rel, text_rel, kind, text=changed)
        except AssertionError:
            raised = True
        assert raised, f"{text_rel}: a changed digit passed"
        for bad in (text + "an extra line\n", "\n".join(text.split("\n")[1:])):
            try:
                check_derived_text(pooled_rel, text_rel, kind, text=bad)
            except AssertionError:
                continue
            raise AssertionError(f"{text_rel}: an added or removed line passed")


# ---------------------------------------------------------------- (3) site/data/dsweep.json

def test_site_data_equals_a_fresh_build_and_is_registered():
    mod = builder()
    fresh = json.loads(json.dumps(mod.dsweep_data(), sort_keys=True))
    assert fresh == site(), "site/data/dsweep.json differs from a fresh build; run python scripts/build_site_data.py"
    ix = read(os.path.join(REPO, "site", "data", "index.json"))
    assert ix["sections"]["dsweep"] == "data/dsweep.json"
    assert site()["source"] == POOLED_REL and site()["source_sha256"] == mod.sha(os.path.join(REPO, *POOLED_REL.split("/")))
    assert site()["plan"] == "dsweep/PLAN.md" and site()["jobs"] == 18
    assert len(json.dumps(site())) < 60_000, "the d-sweep data file is no longer small"
    json.dumps(site(), allow_nan=False)


def test_site_data_models_runs_and_words():
    s = site()
    assert [(m["cpu_model"], m["cpu_short"], m["slug"], m["arch"], m["jobs"], m["runs"], m["word"]) for m in s["models"]] == [
        (EPYC7763, "EPYC 7763", "epyc-7763", "x86_64", 9, 2, "H2"), (N2, "Neoverse-N2", "neoverse-n2", "aarch64", 6, 1, "neither")]
    assert [(m["cpu_short"], m["jobs"], m["runs"], m["word"]) for m in s["too_few_jobs"]] == [
        ("EPYC 9V45", 2, 1, "too few jobs"), ("Xeon 8573C", 1, 1, "too few jobs")]
    assert all(m["jobs"] < s["rule"]["minimum_jobs"] for m in s["too_few_jobs"]) and "rows" not in s["too_few_jobs"][0]
    assert [(r["run_id"], r["jobs"]) for r in s["runs"]] == [(i, 6) for i in RUN_IDS]
    assert not any("url" in r for r in s["runs"]) and "/actions/runs/" not in json.dumps(s)  # the site carries no workflow-run links
    assert {r["commit"] for r in s["runs"]} == {COMMIT} and all(m["commits"] == [COMMIT] for m in s["models"] + s["too_few_jobs"])
    by = {m["cpu_model"]: m for m in s["models"]}
    assert (by[N2]["l1d_kib"], by[N2]["l2_kib"]) == (64, 1024)
    assert by[EPYC7763]["columns_agree"] is True and by[N2]["columns_agree"] is False
    assert {c: by[N2]["columns"][c]["word"] for c in by[N2]["columns"]} == {"as_compiled": "falls", "aligned": "H1"}
    assert {c: by[EPYC7763]["columns"][c]["word"] for c in by[EPYC7763]["columns"]} == {"as_compiled": "H2", "aligned": "H2"}
    for m in s["models"]:
        src = block(m["cpu_model"])
        assert m["reason"] == src["verdict"]["reason"] and m["aa"] == src["aa"] and m["published"] == src.get("published")
        assert m["ladder"] == {k: src["ladder"][k] for k in m["ladder"]}
        for col in ("as_compiled", "aligned"):
            ex = src["columns"][col]["excess"]
            c = m["columns"][col]
            assert (c["share"], c["share_ci95"], c["fixed"], c["growth"]) == (ex["share"], ex["share_ci95"], ex["fixed"], ex["growth"])
            assert c["fit_ds"] == src["columns"][col]["fit_ds"] and c["word"] == src["words"][col]["word"]
        assert m["placement"]["sensitive_ds"] == src["placement"]["sensitive_ds"] and m["placement"]["mechanical"] is True
        assert [m["builds"][k]["traps"] for k in ("none", "fast")] == [0, 1], "the FAST build holds the one bounds check's trap"
        assert m["builds"]["none"]["elements_per_pass"] == 8 and m["builds"]["none"]["vectorization"] is True
        assert m["instructions"]["fit"] == src["instructions"]["fit"] and m["instructions"]["label"] == "instructions, not time"


def test_site_data_rows_are_the_pooled_rows_with_the_instruction_counts_and_the_placement_flag():
    s = site()
    for m in s["models"]:
        src = block(m["cpu_model"])
        want = [r["d"] for r in src["columns"]["as_compiled"]["rows"]]
        assert [r["d"] for r in m["rows"]] == want
        place = {r["d"]: r for r in src["placement"]["rows"]}
        ins = {r["d"]: r for r in src["instructions"]["rows"]}
        for r in m["rows"]:
            d = r["d"]
            for col in ("as_compiled", "aligned"):
                p = prow(m["cpu_model"], col, d)
                assert (r[col]["ratio"], r[col]["ci95"], r[col]["excess_ns_per_inner"]) == (p["ratio"], p["ci95"], p["excess_ns_per_inner"])
            assert r["roles"] == prow(m["cpu_model"], "as_compiled", d)["roles"] and r["d_mod_8"] == d % 8
            assert r["extra_instr_per_inner"] == ins[d]["extra_per_inner"] and r["instr_ratio"] == ins[d]["ratio"]
            assert (r["placement_d"], r["placement_d_ci95"], r["placement_sensitive"]) == (place[d]["d_ratio"], place[d]["ci95"], place[d]["sensitive"])
            assert r["working_set_bytes"] == 12 * d * d, "three d x d matrices of 4-byte elements"
    assert srow(N2, 48)["extra_instr_per_inner"] > 150 and srow(N2, 48)["placement_sensitive"] is False
    assert srow(EPYC7763, 147)["roles"] == ["study_l2"] and srow(EPYC7763, 36)["roles"] == ["fit", "study_l1"]


def test_site_data_builder_refuses_a_changed_plan_or_a_pool_made_under_another_one():
    mod = builder()
    saved = mod.DSWEEP_PLAN
    try:
        mod.DSWEEP_PLAN = "replication/PLAN.md"   # any other file: its hash is not the one stored
        try:
            mod.dsweep_data()
            raise AssertionError("a plan with another hash was accepted")
        except AssertionError as e:
            assert "never be edited after a run" in str(e), e
    finally:
        mod.DSWEEP_PLAN = saved


BUILD = """
import importlib.util, sys
script, out, flag = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("build_site_data_copy", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if flag != "dsweep":
    mod.DSWEEP_POOLED = "results/does-not-exist/dsweep-pooled.json"
mod.build(out)
"""


def build_into(out, with_dsweep):
    r = subprocess.run([sys.executable, "-I", "-c", BUILD, os.path.join(REPO, "scripts", "build_site_data.py"), out,
                        "dsweep" if with_dsweep else "none"], capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stderr[-2000:]


def tree(root):
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(dp, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root).replace("\\", "/")] = fh.read().replace(bytes([13, 10]), bytes([10]))
    return out


def test_adding_the_d_sweep_changes_no_other_file():
    with tempfile.TemporaryDirectory() as with_d, tempfile.TemporaryDirectory() as without:
        build_into(with_d, True)
        build_into(without, False)
        a, b = tree(with_d), tree(without)
        assert "dsweep.json" in a and "dsweep.json" not in b
        assert sorted(set(a) - set(b)) == ["dsweep.json"] and not set(b) - set(a)
        assert sorted(k for k in b if a[k] != b[k]) == ["index.json"], "other site files changed because of the d-sweep"
        ia, ib = json.loads(a["index.json"]), json.loads(b["index.json"])
        assert ia["sections"].pop("dsweep") == "data/dsweep.json"
        assert ia == ib, "index.json differs by more than its sections.dsweep entry"
        committed = tree(os.path.join(REPO, "site", "data"))
        assert committed == a, f"site/data/ differs from a fresh build: {sorted(k for k in set(a) | set(committed) if a.get(k) != committed.get(k))[:5]}"


# ---------------------------------------------------------------- (4) scripts/check.py on a small scratch world

@lru_cache(maxsize=None)
def world():
    """A scratch results folder holding the six Neoverse-N2 jobs of the first run, the pool of all runs (here: of that run) and
    that run's own copy, both written by dsweep/analyze.py as the real ones were. scripts/check.py's pool check is run on it
    (and on edits of it) without waiting for the 18-job analysis."""
    root = tempfile.mkdtemp(prefix="dsweep-test-")
    atexit.register(shutil.rmtree, root, True)
    base = os.path.join(root, "results")
    run = "s10-dsweep-run-39018966032"
    for f in glob.glob(os.path.join(RESULTS, run, "dsweep-job-*", "dsweep.json")):
        dst = os.path.join(base, run, os.path.basename(os.path.dirname(f)))
        os.makedirs(dst)
        shutil.copyfile(f, os.path.join(dst, "dsweep.json"))
    for out in (os.path.join(base, "s10-dsweep-pooled", "dsweep-pooled.json"), os.path.join(base, run, "dsweep-pooled", "dsweep-pooled.json")):
        os.makedirs(os.path.dirname(out))
        r = subprocess.run([sys.executable, "-I", os.path.join(REPO, "dsweep", "analyze.py"), os.path.join(base, run), "--out", out],
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0 and os.path.exists(out), r.stdout[-500:] + r.stderr[-500:]
    return base


def copy_world():
    tmp = tempfile.mkdtemp(prefix="dsweep-test-copy-")
    atexit.register(shutil.rmtree, tmp, True)
    base = os.path.join(tmp, "results")
    shutil.copytree(world(), base)
    return base


def pools_check(base):
    chk = check_module()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = chk.check_dsweep_pools(base)
    return ok, buf.getvalue()


def edit_pool(path, fn):
    doc = read(path)
    fn(doc)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)


def test_the_scratch_world_passes_and_reports_what_it_checked():
    ok, out = pools_check(world())
    assert ok, out
    assert "results/s10-dsweep-pooled/dsweep-pooled.json equals dsweep/analyze.py over the 6 dsweep.json it lists" in out, out
    assert "results/s10-dsweep-run-39018966032/dsweep-pooled/dsweep-pooled.json equals dsweep/analyze.py over the 6 dsweep.json" in out, out
    assert "Neoverse-N2 (6 jobs, 1 run pooled): neither" in out


def test_a_pooled_file_with_other_input_paths_and_nothing_else_changed_passes():
    base = copy_world()

    def repath(d):   # the same files, listed relative to another folder (the real run copies were written one folder up)
        for i in d["inputs"]:
            i["path"] = "x/" + "/".join(i["path"].split("/")[-2:])
        for c in d["cpus"]:
            c["inputs"] = ["x/" + "/".join(p.split("/")[-2:]) for p in c["inputs"]]
    # a run's own copy is re-pooled from the jobs of its folder, so only its listing changes; the pool of all runs resolves its
    # listing to find the files, so its paths are what they are
    edit_pool(os.path.join(base, "s10-dsweep-run-39018966032", "dsweep-pooled", "dsweep-pooled.json"), repath)
    ok, out = pools_check(base)
    assert ok, out


def test_a_changed_number_in_the_pooled_file_fails():
    base = copy_world()

    def tamper(d):
        d["cpus"][0]["columns"]["aligned"]["excess"]["share"] += 0.001
    edit_pool(os.path.join(base, "s10-dsweep-pooled", "dsweep-pooled.json"), tamper)
    ok, out = pools_check(base)
    assert not ok and "FAIL results/s10-dsweep-pooled/dsweep-pooled.json: stored numbers differ from the recomputed ones" in out, out
    assert "share" in out
    # a changed word is a changed leaf as well
    base = copy_world()
    edit_pool(os.path.join(base, "s10-dsweep-run-39018966032", "dsweep-pooled", "dsweep-pooled.json"),
              lambda d: d["cpus"][0]["verdict"].update(word="H1"))
    ok, out = pools_check(base)
    assert not ok and "FAIL results/s10-dsweep-run-39018966032/dsweep-pooled/dsweep-pooled.json" in out and "word" in out, out


def test_a_job_left_out_of_the_pool_or_listed_twice_or_stray_fails():
    base = copy_world()   # a job dropped from the listing: it is on disk in a run folder the pool names
    edit_pool(os.path.join(base, "s10-dsweep-pooled", "dsweep-pooled.json"), lambda d: d["inputs"].pop())
    ok, out = pools_check(base)
    assert not ok and "is on disk in a run folder this pool names but not pooled" in out, out
    base = copy_world()   # a job listed twice
    edit_pool(os.path.join(base, "s10-dsweep-pooled", "dsweep-pooled.json"), lambda d: d["inputs"].append(dict(d["inputs"][0])))
    ok, out = pools_check(base)
    assert not ok and "a job is listed twice" in out, out
    base = copy_world()   # a job in a run folder that no pool lists
    other = os.path.join(base, "s10-dsweep-run-39999999999", "dsweep-job-neoverse-n2-j1")
    os.makedirs(other)
    shutil.copyfile(os.path.join(base, "s10-dsweep-run-39018966032", "dsweep-job-neoverse-n2-j1", "dsweep.json"), os.path.join(other, "dsweep.json"))
    ok, out = pools_check(base)
    assert not ok and "is in no results/*dsweep-pooled/dsweep-pooled.json" in out, out
    base = copy_world()   # jobs and no pooled file
    shutil.rmtree(os.path.join(base, "s10-dsweep-pooled"))
    ok, out = pools_check(base)
    assert not ok and "no results/*dsweep-pooled/dsweep-pooled.json" in out, out


def test_a_missing_listed_job_fails_without_a_traceback():
    base = copy_world()
    os.remove(os.path.join(base, "s10-dsweep-run-39018966032", "dsweep-job-neoverse-n2-j6", "dsweep.json"))
    ok, out = pools_check(base)
    assert not ok and "is listed but is not on disk" in out, out


def test_no_sweep_stored_means_none_yet_and_the_real_step_is_wired_into_main():
    chk = check_module()
    with tempfile.TemporaryDirectory() as tmp:
        ok, out = pools_check(os.path.join(tmp, "results"))
        assert ok and out == ""
    import inspect
    src = inspect.getsource(chk.main)
    assert "ok &= check_dsweep()" in src and "dsweep/analyze.py --verify" in src
    assert "check_dsweep_plan" in inspect.getsource(chk.check_dsweep) and "check_dsweep_pools" in inspect.getsource(chk.check_dsweep)
    assert "--verify" in inspect.getsource(chk.check_dsweep)
    # the real tree: the plan guard passes on the stored files (the full re-pool and the recomputation of every interval is scripts/check.py's own step)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert chk.check_dsweep_plan(job_files(), chk.dsweep_pooled_files(RESULTS))
