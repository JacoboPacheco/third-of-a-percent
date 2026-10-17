"""site/data/arm64.json (the Arm column) against the files it is built from, and the proof that it is additive.

The Arm pool (results/s8-arm-pooled/pooled.json, 30 jobs, one AArch64 CPU model) and the per-job files of the
runs it names are the only inputs. These tests read those files again, by their own code, and compare:
  - the counts (jobs, runs, cells) and the run list;
  - every ratio, interval, spread, layout A/A, positive control and placement flag of every cell;
  - the verdict (form, line, why) and the rows that explain it, recomputed from the cells with the
    thresholds of harness/criteria-v3.json;
  - the NEON instruction counts, the trap counts and the line counts, recomputed from the stored listings
    (results/s8-arm-run-*/results-*/asm/*.s), and the agreement of every job with the first one;
  - the typed predictions (scripts/build_site_data.py ARM_PREDICTED) against the words of arm64/PLAN.md;
  - the x86-64 numbers set beside it against the committed index.json and results/s7-pooled/pooled.json;
  - the sensitivity readings kept beside the stored verdict (they change nothing in it): arm64/seed-sensitivity.json
    (arm64/seeds.py: the bootstrap re-drawn under 400 other seeds; the deciding cell, the first seeds of every statistic and the
    converged reading are re-derived here from the pool), robustness/results-arm.json (the eight interval methods), the L2 noise
    facts (identical-binary A/A at L2, the share of slow processes), the layout A/A against the placement statistic D, the matrix
    multiply cost against its instruction count, the instructions the check adds to the forward loops, and the stored diffs'
    counts before and after the normalize fix. Each key of arm64.json is compared leaf by leaf with a recomputation written
    again in this file, and a one-part-in-a-million change to any single leaf is shown to be caught.
test_adding_the_arm_column_changes_no_other_file builds site/data/ twice (with the Arm pool and with its path pointed
at nothing) and requires every other file to be byte-identical and index.json to differ by its sections.arm64 entry only.
The scripts/check.py tests make scratch copies of the pool listing: dropping a job from results/s8-arm-pooled/pooled.json,
listing one twice or adding a stray job folder must fail check_pool_complete().

Offline and read-only (the builds go to temporary folders). No fixtures, so scripts/check.py's built-in runner runs it."""
import contextlib
import difflib
import glob
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import shutil
import statistics
import tempfile
from functools import lru_cache

import asm
import placement

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARM_POOLED = "results/s8-arm-pooled/pooled.json"
SITE_DATA = os.path.join(REPO, "site", "data")
BUILDS = ("none", "fast", "novec", "none_a64", "fast_a64")
# written here again on purpose: the test must not share the builder's pattern (test_neon_pattern_is_the_harness_one ties them)
NEON = re.compile(r"\bv\d+\.\d*[bhsd]\b|\bq\d+\b")
INSN = re.compile(r"^\s*([0-9a-f]+):\s*(.*)$")


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@lru_cache(maxsize=None)
def builder():
    return _load_module(os.path.join(REPO, "scripts", "build_site_data.py"), "arm_test_build_site_data")


def read_json(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def arm():
    return read_json("site", "data", "arm64.json")


@lru_cache(maxsize=None)
def pooled():
    return read_json(*ARM_POOLED.split("/"))


@lru_cache(maxsize=None)
def block():
    d = pooled()
    assert len(d["cpus"]) == 1
    return d["cpus"][0]


@lru_cache(maxsize=None)
def job_dirs():
    base = os.path.join(REPO, "results", "s8-arm-pooled")
    return [os.path.normpath(os.path.join(base, os.path.dirname(i["path"]))) for i in pooled()["inputs"]]


@lru_cache(maxsize=None)
def job_docs():
    return [(read_json(os.path.relpath(d, REPO), "results.json"), read_json(os.path.relpath(d, REPO), "details.json")) for d in job_dirs()]


def listing(job_dir, name):
    with open(os.path.join(job_dir, "asm", name), encoding="utf-8") as f:
        return f.read().splitlines()


def cell(cid):
    return next(c for c in arm()["cells"] if c["cell_id"] == cid)


def kernel(k):
    return next(x for x in arm()["kernels"] if x["kernel"] == k)


# ---------------------------------------------------------------- counts and sources

def test_counts_runs_and_sources():
    a, p, c = arm(), pooled(), block()
    on_disk = sorted(glob.glob(os.path.join(REPO, "results", "s8-arm-run-*", "results-*", "results.json")))
    assert a["jobs"] == len(p["inputs"]) == len(on_disk) == c["jobs"]
    assert a["source"] == ARM_POOLED
    assert a["cpu_model"] == c["cpu_model"] == p["inputs"][0]["cpu_model"]
    assert all(i["cpu_model"] == c["cpu_model"] for i in p["inputs"]), "the Arm pool is one CPU model"
    assert [r["run_id"] for r in a["runs"]] == p["runs"] == c["runs"]
    assert sum(r["jobs"] for r in a["runs"]) == a["jobs"]
    for r in a["runs"]:
        assert r["jobs"] == sum(1 for i in p["inputs"] if i["run_id"] == r["run_id"])
        pr = next(x for x in c["per_run"] if x["run_id"] == r["run_id"])
        assert (r["form"], r["line"], r["jobs"]) == (pr["form"], pr["line"], pr["jobs"])
    assert len(a["cells"]) == len(c["cells"]) == 16 and len(a["kernels"]) == 8
    assert a["arch"] == "aarch64" == a["machine"]["arch"]
    assert a["criteria"]["sha256"] == p["criteria_sha256"]
    crit = read_json("harness", "criteria-v3.json")["v3"]
    assert a["criteria"]["file"] == p["criteria_file"] == "harness/criteria-v3.json"
    assert (a["criteria"]["resamples"], a["criteria"]["minimum_jobs"], a["criteria"]["jobs_per_run"], a["criteria"]["reps_per_side"]) == \
        (p["resamples"], crit["pooling"]["minimum_jobs"], crit["matrix"]["jobs_per_run"], crit["timing"]["reps_per_side"])
    assert a["verdict"]["minimum_jobs"] == crit["pooling"]["minimum_jobs"] and a["machine"]["reps_per_side"] == crit["timing"]["reps_per_side"]
    assert a["criteria"]["same_as_x86_pool"] == (p["criteria_sha256"] == read_json("results", "s7-pooled", "pooled.json")["criteria_sha256"])
    sha = hashlib.sha256(open(os.path.join(REPO, *ARM_POOLED.split("/")), "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    assert a["source_sha256"] == sha, "arm64.json was built from another version of the pool"


def test_runs_commits_and_start_times_are_the_jobs_own():
    a = arm()
    for r in a["runs"]:
        docs = [res for res, _ in job_docs() if res["run"]["id"] == r["run_id"]]
        assert len(docs) == r["jobs"]
        assert {d["run"]["commit"] for d in docs} == {r["commit"]}
        assert min(d["run"]["started_at"] for d in docs) == r["started_at"]


def test_machine_facts_are_the_runs_own():
    m = arm()["machine"]
    res, det = job_docs()[0]
    runner = res["run"]["runner"]
    assert (m["os"], m["kernel"], m["vcpus"], m["l1d_kib"], m["l2_kib"], m["l3_kib"]) == \
        (runner["os"], runner["kernel"], runner["cores"], runner["l1d_kib"], runner["l2_kib"], runner["l3_kib"])
    assert m["cache_bytes"] == det["cache_bytes"] and m["size_targets_bytes"] == det["size_targets_bytes"]
    assert m["toolchain"] == res["run"]["toolchain"] and m["flags"] == res["run"]["flags"]
    lscpu = {k.strip(): v.strip() for k, _, v in (ln.partition(":") for ln in det["lscpu"].splitlines())}
    assert m["cpu_model"] == lscpu["Model name"] and m["vendor_id"] == lscpu["Vendor ID"]
    assert str(m["vcpus"]) == lscpu["CPU(s)"] and str(m["threads_per_core"]) == lscpu["Thread(s) per core"]
    flags = set(lscpu["Flags"].split())
    assert m["isa_flags"] == {f: f in flags for f in ("asimd", "sve", "sve2")}
    commands = [bd["command"] for kd in det["kernels"].values() for bd in kd.values() if isinstance(bd, dict) and "command" in bd]
    assert m["march_flag_in_builds"] == any("-march" in x or "-mcpu" in x for x in commands)
    # every job reports the same machine, toolchain and flags
    for r, d in job_docs():
        assert r["run"]["runner"] == runner and r["run"]["toolchain"] == res["run"]["toolchain"] and r["run"]["flags"] == res["run"]["flags"]
        assert d["cache_bytes"] == det["cache_bytes"] and d["lscpu"].split("Flags:")[1].split("\n")[0] == det["lscpu"].split("Flags:")[1].split("\n")[0]
    assert m["jobs"] == m["jobs_agreeing"] == arm()["jobs"]


# ---------------------------------------------------------------- the cells

def stat(p, spread=False):
    out = {"ratio": p["ratio"], "ci95": p["ci95"], "half_width_pct": p["half_width_pct"], "jobs": p["jobs"],
           "between_job_sd_pct": p["between_job_sd_pct"]}
    if spread:
        out["per_job_range"] = [min(p["per_job"]), max(p["per_job"])]
    return out


def test_every_cell_is_the_pools():
    c = block()
    assert [x["cell_id"] for x in arm()["cells"]] == [x["cell_id"] for x in c["cells"]]
    ps = {p["cell_id"] for p in c["verdict"]["placement_sensitive"]}
    for want in c["cells"]:
        got = cell(want["cell_id"])
        cid = want["cell_id"]
        assert (got["kernel"], got["size_class"], got["class"]) == (want["kernel"], want["size_class"], want["class"]), cid
        assert got["as_compiled"] == stat(want["as_compiled"], True) and got["aligned"] == stat(want["aligned"], True), cid
        assert got["instr_ratio"] == {"as_compiled": want["instr"]["ratio"], "aligned": want["aligned_instr"]["ratio"]}, cid
        assert got["instr_agree"] == want["instr_agree"], cid
        assert got["layout_aa"] == stat(c["layout_aa"][cid]), cid
        pos = c["positive"].get(cid)
        assert got["positive"] == (stat(pos) if pos else None), cid
        assert got["placement_sensitive"] == (cid in ps), cid
        pl = want.get("placement")
        if pl is None:
            assert got["placement"] is None, cid
        else:
            assert got["placement"] == {k: pl[k] for k in ("statistical", "mechanical", "sensitive", "hot_none", "hot_fast")} | {"d": stat(pl["d"])}, cid
            assert pl["sensitive"] == (cid in ps), cid
        for col in ("as_compiled", "aligned"):
            assert got["per_run"][col] == [r["cells"][cid][col][0] for r in c["per_run"]], (cid, col)
        assert got["as_compiled"]["jobs"] == got["aligned"]["jobs"] == arm()["jobs"], cid
    assert instr_label_ok()


def instr_label_ok():
    return arm()["instr_label"] == block()["cells"][0]["instr_label"] and all(x["instr_label"] == arm()["instr_label"] for x in block()["cells"])


def test_positive_control_covers_the_vectorized_kernels_and_is_seen():
    c = block()
    for x in arm()["cells"]:
        has = x["class"] in ("kept", "lost")
        assert (x["positive"] is not None) == has, x["cell_id"]
        if has:  # the no-vectorize build is slower than the default build, beyond the pooled A/A
            assert x["positive"]["ci95"][0] > 1.0 + c["aa"]["half_width_pct"] / 100.0, x["cell_id"]


def test_controls_are_the_pools():
    a, c = arm()["aa"], block()["aa"]
    assert (a["ratio"], a["ci95"], a["half_width_pct"], a["jobs"], a["between_job_sd_pct"], a["per_job"]) == \
        (c["ratio"], c["ci95"], c["half_width_pct"], c["jobs"], c["between_job_sd_pct"], c["per_job"])
    hw = sorted(r["controls"]["aa"]["half_width_pct"] for r, _ in job_docs())
    assert a["job_half_width_pct"] == {"min": hw[0], "median": (hw[14] + hw[15]) / 2, "max": hw[-1]}
    lay = [block()["layout_aa"][x["cell_id"]]["half_width_pct"] for x in arm()["cells"]]
    assert a["layout_half_width_pct"] == {"min": min(lay), "max": max(lay)}
    rep, want = arm()["reproduction"], block()["reproduction"]
    assert (rep["checked"], rep["outside"], rep["misses"]) == (want["checked"], want["outside"], want["misses"])
    assert rep["max_gap_pct"] == max(m["gap_pct"] for m in want["misses"])
    sd = arm()["between_job_sd"]
    for size in ("L1", "L2"):
        best = max(((x[col]["between_job_sd_pct"], x["cell_id"], col) for x in arm()["cells"] if x["size_class"] == size
                    for col in ("as_compiled", "aligned")))
        assert (sd[size.lower() + "_max_pct"], sd[size.lower() + "_max_cell"], sd[size.lower() + "_max_column"]) == best


def test_summary_is_the_pools_cpu_summary_with_kept_not_forward_names():
    s = arm()["summary"]
    c = block()
    assert (s["cpu_model"], s["jobs"], s["form"], s["stability"], s["why"]) == (c["cpu_model"], c["jobs"], c["verdict"]["form"], c["stability"], c["verdict"]["why"])
    assert s["aa_half_width_pct"] == c["aa"]["half_width_pct"]
    assert not [k for k in s if k.startswith("forward")], "matrix multiply keeps SIMD here, so 'forward' would mislead"
    kept = [x for x in c["cells"] if x["class"] == "kept"]
    assert s["kept_compiled"] == {"min": min(x["as_compiled"]["ratio"] for x in kept), "max": max(x["as_compiled"]["ratio"] for x in kept)}
    assert s["kept_aligned"] == {"min": min(x["aligned"]["ratio"] for x in kept), "max": max(x["aligned"]["ratio"] for x in kept)}
    lost = [x for x in c["cells"] if x["class"] == "lost"]
    assert s["lost"] == {"min": min(x[col]["ratio"] for x in lost for col in ("as_compiled", "aligned")),
                         "max": max(x[col]["ratio"] for x in lost for col in ("as_compiled", "aligned"))}
    fl = arm()["forward_loops"]
    assert fl["kernels"] == ["k01_sum_fwd", "k02_add_fwd", "k03_stencil"]
    for size in ("L1", "L2"):
        fc = [x for x in c["cells"] if x["kernel"] in fl["kernels"] and x["size_class"] == size]
        for col in ("as_compiled", "aligned"):
            vals = [x[col]["ratio"] for x in fc]
            assert fl[size][col] == {"min": min(vals), "max": max(vals)}, (size, col)


# ---------------------------------------------------------------- the verdict

def test_verdict_is_the_pools_and_its_rows_explain_it():
    v, want = arm()["verdict"], block()["verdict"]
    crit = read_json("harness", "criteria-v3.json")["verdict"]
    for k in ("form", "line", "why", "forward_limit_pct", "aa_half_width_pct", "placement_sensitive", "off_axis", "n", "n_as_compiled", "x_pct"):
        assert v[k] == want[k], k
    assert v["page_line"] == pooled()["page"]["line"] and v["stability"] == block()["stability"]
    limit = 1.0 + want["forward_limit_pct"] / 100.0
    assert v["limit"] == limit == 1.02 or abs(v["limit"] - limit) < 1e-12
    assert (v["forward_point_max_ratio"], v["lost_ci_lo_min_ratio"], v["aa_half_width_max_pct"]) == \
        (crit["forward_point_max_ratio"], crit["lost_ci_lo_min_ratio"], crit["aa_half_width_max_pct"])
    ps = {p["cell_id"] for p in want["placement_sensitive"]}
    cells = block()["cells"]
    # the rule's group (kernels that keep SIMD under FAST), judged on the aligned column, placement-sensitive cells left out
    rows = [r for r in v["forward_rule_cells"]]
    assert [r["cell_id"] for r in rows] == [x["cell_id"] for x in cells if x["class"] == "kept"]
    missed = []
    for r in rows:
        x = next(c for c in cells if c["cell_id"] == r["cell_id"])
        judged = r["cell_id"] not in ps
        assert r["judged"] == judged
        assert (r["aligned_ratio"], r["aligned_ci_hi"], r["as_compiled_ratio"]) == (x["aligned"]["ratio"], x["aligned"]["ci95"][1], x["as_compiled"]["ratio"])
        passes = x["aligned"]["ratio"] <= crit["forward_point_max_ratio"] and x["aligned"]["ci95"][1] <= limit
        assert r["passes"] == (passes if judged else None), r["cell_id"]
        if judged and not passes:
            missed.append(r["cell_id"])
    assert v["forward_missed"] == missed
    if missed:  # the stored sentence names exactly these cells
        assert "forward rule (aligned) missed by " + ", ".join(missed) in v["why"]
        assert v["form"] != "map"
    lost = [r for r in v["lost_rule_cells"]]
    assert [r["cell_id"] for r in lost] == [x["cell_id"] for x in cells if x["class"] == "lost"]
    for r in lost:
        x = next(c for c in cells if c["cell_id"] == r["cell_id"])
        assert (r["as_compiled_ci_lo"], r["aligned_ci_lo"]) == (x["as_compiled"]["ci95"][0], x["aligned"]["ci95"][0])
        assert r["passes"] == (min(r["as_compiled_ci_lo"], r["aligned_ci_lo"]) >= crit["lost_ci_lo_min_ratio"])
    above = [(x["cell_id"], col) for x in cells if x["class"] in ("kept", "lost") and x["cell_id"] not in ps
             for col in ("as_compiled", "aligned") if x[col]["ci95"][0] > limit]
    assert [(r["cell_id"], r["column"]) for r in v["above_forward_limit"]] == above
    if above:
        text = ", ".join(cid + (" (aligned)" if col == "aligned" else "") for cid, col in above)
        assert "cells above the forward limit: " + text in v["why"]


def block_criteria_file():
    return pooled()["criteria_file"]


def test_verdict_is_not_reworded_into_a_map():
    """The Arm pool is judged by the written rules (criteria-v3.json, unchanged): whatever the form is, the stored
    sentence names it in capitals and the lowercase form is the pool's own."""
    v = arm()["verdict"]
    assert v["form"] == block()["verdict"]["form"]
    assert v["form"].upper() in v["line"], "the stored sentence does not name the form"
    assert arm()["criteria"]["file"] == "harness/criteria-v3.json" == block_criteria_file()


# ---------------------------------------------------------------- the machine code, per kernel

def test_neon_pattern_is_the_harness_one():
    assert NEON.pattern == placement._NEON.pattern
    assert arm()["machine"]["isa_flags"]["asimd"] is True


def count_listing(lines):
    insns = [m.group(2).strip() for m in (INSN.match(ln) for ln in lines) if m and m.group(2).strip()]
    return len(insns), sum(1 for t in insns if NEON.search(t))


def test_neon_traps_and_line_counts_recomputed_from_the_listings():
    for k in kernel_ids():
        kr = kernel(k)
        job_dir = os.path.join(REPO, kr["source_job"])
        assert os.path.normpath(job_dir) in job_dirs()
        for b in BUILDS:
            lines = listing(job_dir, f"{k}.{b}.s")
            n_insns, n_neon = count_listing(lines)
            rec = kr["builds"][b]
            assert rec["asm_lines"] == len(lines) == n_insns + 1, (k, b)  # the header line is not an instruction
            assert rec["neon_instructions"] == n_neon, (k, b)
            assert rec["traps"] == asm.count_traps(lines), (k, b)
        assert kr["asm_lines_delta"] == kr["builds"]["fast"]["asm_lines"] - kr["builds"]["none"]["asm_lines"]
        assert kr["neon_removed"] == kr["builds"]["none"]["neon_instructions"] - kr["builds"]["fast"]["neon_instructions"]
        for name, suffix in (("L1", "L1.diff"), ("L1_aligned", "L1.aligned.diff"), ("L2", "L2.diff"), ("L2_aligned", "L2.aligned.diff")):
            lines = listing(job_dir, f"{k}.{suffix}")
            assert kr["diffs"][name] == {"file": f"{k}.{suffix}",
                                         "added": sum(1 for x in lines if x.startswith("+") and not x.startswith("+++")),
                                         "removed": sum(1 for x in lines if x.startswith("-") and not x.startswith("---"))}


def kernel_ids():
    return [x["kernel"] for x in arm()["kernels"]]


def test_class_matches_the_compiler_remarks_and_the_listings():
    for kr in arm()["kernels"]:
        k = kr["kernel"]
        classes = {cell(f"{k}.{s}")["class"] for s in ("L1", "L2")}
        assert classes == {kr["class"]} == {kr["class_from_remarks"]}, k
        none, fast = kr["builds"]["none"], kr["builds"]["fast"]
        if kr["class"] == "lost":
            assert none["vectorized"] and not fast["vectorized"] and none["neon_instructions"] > 0 and fast["neon_instructions"] == 0, k
            assert fast["why_not_vectorized"] and fast["hot_simd_loops"] == 0 and none["hot_simd_loops"] > 0, k
        elif kr["class"] == "kept":
            assert none["vectorized"] and fast["vectorized"] and none["neon_instructions"] > 0 and fast["neon_instructions"] > 0, k
            assert (none["width"], none["interleave"]) == (fast["width"], fast["interleave"]), k
        else:
            assert not none["vectorized"] and not fast["vectorized"] and none["neon_instructions"] == fast["neon_instructions"] == 0, k
        assert kr["builds"]["novec"]["vectorized"] is False and kr["builds"]["novec"]["neon_instructions"] == 0, k
        assert fast["traps"] >= 1 or k == "k01_sum_fwd", k  # FAST adds a trap wherever it adds a check (the plain sum has none in its loop)
        assert none["traps"] == 0 and kr["builds"]["novec"]["traps"] == 0, k
        if kr["class"] == "kept":
            ops = kr["simd_loop"]["as_compiled"]
            assert ops["same_opcodes"] is True and ops["none_instructions"] == ops["fast_instructions"], k


def test_remarks_are_the_compilers_words():
    for kr in arm()["kernels"]:
        _, det = job_docs()[0]
        for b in BUILDS:
            rec = kr["builds"][b]
            vec = det["kernels"][kr["kernel"]][b]["vectorization"]
            assert rec["remarks"] == vec["remarks"] and rec["vectorized"] == vec["vectorized"] and rec["width"] == vec["width"], (kr["kernel"], b)
            if rec["why_not_vectorized"]:
                assert any(r.startswith(rec["why_not_vectorized"]) for r in rec["remarks"]), (kr["kernel"], b)
            if rec["interleave"] is not None:
                assert f"interleaved count: {rec['interleave']}" in " ".join(rec["remarks"]), (kr["kernel"], b)
            assert rec["sha256"] == det["kernels"][kr["kernel"]][b]["sha256"]
            template = arm()["machine"]["commands"][b]
            assert rec.get("command", template.replace("{kernel}", kr["kernel"])) == det["kernels"][kr["kernel"]][b]["command"], (kr["kernel"], b)


def test_every_job_has_the_same_binaries_listings_and_remarks():
    first = None
    for job_dir, (res, det) in zip(job_dirs(), job_docs()):
        sig = {}
        for k, kd in det["kernels"].items():
            for b in BUILDS:
                bd = kd[b]
                vec = bd["vectorization"]
                files = [listing(job_dir, f"{k}.{b}.s")]
                with open(os.path.join(job_dir, "remarks", f"{k}.{b}.txt"), "rb") as f:
                    remarks_file = hashlib.sha256(f.read()).hexdigest()
                sig[(k, b)] = (bd["sha256"], bd["command"], bd["traps"], bd["asm_lines"], vec["vectorized"], vec["width"], tuple(vec["remarks"]),
                               tuple(files[0]), remarks_file)
        first = first or sig
        assert sig == first, job_dir
    a = arm()
    assert a["build_facts"]["all_agree"] is True and a["build_facts"]["jobs"] == a["jobs"]
    assert all(kr["jobs_agreeing"] == a["jobs"] for kr in a["kernels"])


# ---------------------------------------------------------------- what the plan said

PLAN_WORDS = {
    "k04_rev": "Reverse and stride-2: lost under FAST", "k05_stride2": "Reverse and stride-2: lost under FAST",
    "k08_matmul": "Matrix multiply: the sweep lists it as NOT lost",
    "k01_sum_fwd": "Forward loops (sum, add, stencil): vectorized in both builds",
    "k02_add_fwd": "Forward loops (sum, add, stencil): vectorized in both builds",
    "k03_stencil": "Forward loops (sum, add, stencil): vectorized in both builds",
    "k06_gather": "Gather and histogram: no prediction", "k07_hist": "Gather and histogram: no prediction",
}


def test_predictions_are_the_plans_words_and_held_is_derived():
    with open(os.path.join(REPO, "arm64", "PLAN.md"), encoding="utf-8") as f:
        plan = f.read()
    assert "No placement effect is predicted" in plan
    section = plan.split("## Written before the full results")[1].split("## Limits")[0]
    for k, words in PLAN_WORDS.items():
        assert words in section, k
    typed = builder().ARM_PREDICTED
    assert typed == {"k01_sum_fwd": "kept", "k02_add_fwd": "kept", "k03_stencil": "kept", "k04_rev": "lost", "k05_stride2": "lost",
                     "k06_gather": None, "k07_hist": None, "k08_matmul": "kept"}
    for kr in arm()["kernels"]:
        k, pr = kr["kernel"], kr["prediction"]
        assert pr["class"] == typed[k]
        assert pr["class_held"] == (None if typed[k] is None else typed[k] == kr["class_from_remarks"]), k
        forward = k in ("k01_sum_fwd", "k02_add_fwd", "k03_stencil")
        assert pr["placement_effect"] == ("none" if forward else None)
        flagged = [c["cell_id"] for c in arm()["cells"] if c["kernel"] == k and c["placement_sensitive"]]
        assert kr["placement_sensitive_cells"] == flagged
        assert pr["placement_held"] == ((not flagged) if forward else None), k


# ---------------------------------------------------------------- the x86-64 numbers beside it

def test_x86_comparison_is_read_from_the_page_pool_unchanged():
    x = arm()["x86"]
    index = read_json("site", "data", "index.json")
    s7 = read_json("results", "s7-pooled", "pooled.json")
    assert x["source"] == index["pooled"]["source"] == "results/s7-pooled/pooled.json"
    assert x["source_sha256"] == index["pooled"]["source_sha256"]
    assert x["jobs"] == index["pooled"]["jobs"] == len(s7["inputs"]) and x["runs"] == len(index["pooled"]["runs"])
    assert x["criteria_sha256"] == s7["criteria_sha256"]
    model = next(c for c in index["cpus"] if c["slug"] == index["default_cpu"])
    assert x["model"]["cpu_model"] == model["cpu_model"] and x["model"]["jobs"] == model["jobs"]
    block7 = next(b for b in s7["cpus"] if b["cpu_model"] == model["cpu_model"])
    assert set(x["cells"]) == {c["cell_id"] for c in block().get("cells")}
    for c7 in block7["cells"]:
        if c7["cell_id"] not in x["cells"]:
            continue
        got = x["cells"][c7["cell_id"]]
        assert got["class"] == c7["class"]
        for col in ("as_compiled", "aligned"):
            assert got[col] == {"ratio": c7[col]["ratio"], "ci95": c7[col]["ci95"], "jobs": c7[col]["jobs"]}
        pos = block7["positive"].get(c7["cell_id"])
        assert got["positive"] == ({"ratio": pos["ratio"], "ci95": pos["ci95"], "jobs": pos["jobs"]} if pos else None)
    page = index["page"]
    assert x["page"]["lost"] == page["lost"] and x["page"]["forward_aligned"] == page["forward"]["aligned"]
    assert x["page"]["forward_compiled"] == page["forward"]["compiled"] and x["page"]["judged_cpus"] == page["judged_cpus"]
    # nothing of the Arm pool is in an x86-64 aggregate
    assert not [c for c in index["cpus"] if "Neoverse" in c["cpu_model"] or "aarch64" in json.dumps(c)]
    assert not [c for c in read_json("site", "data", "pooled.json")["cpus"] if "Neoverse" in c["cpu_model"]]
    assert index["pooled"]["source"] != ARM_POOLED and all("s8-arm" not in i["path"] for i in s7["inputs"])
    for k, r in x["lost_by_kernel_judged"].items():
        per = [e["lost_by_kernel"][k] for e in index["cpus"] if e["cpu_short"] in page["judged_cpus"] and k in (e.get("lost_by_kernel") or {})]
        assert r == {"min": min(p["min"] for p in per), "max": max(p["max"] for p in per)}, k


# ---------------------------------------------------------------- the sensitivity readings beside the verdict
# arm64/seed-sensitivity.json (arm64/seeds.py), robustness/results-arm.json (robustness/analyze.py --arm) and the noise,
# layout and matrix-multiply facts of arm64.json. Each is re-derived here from the pool and the per-job samples, by code
# written for the test (pure Python where the arithmetic is simple), and compared with the stored numbers.

SEEDS = "arm64/seed-sensitivity.json"
ROBUST = "robustness/results-arm.json"
DECIDING = "k02_add_fwd.L2"
NEW_KEYS = ("seed_sensitivity", "interval_methods", "noise", "layout_vs_placement", "matmul_cost", "forward_instr", "stored_diffs")


def first_diff(x, y, path=""):
    """The first place two JSON values differ (floats to 1e-9 relative), or None."""
    if isinstance(x, bool) or isinstance(y, bool):
        return None if x is y else f"{path}: {x!r} != {y!r}"
    if isinstance(x, dict) and isinstance(y, dict):
        if x.keys() != y.keys():
            return f"{path}: keys differ {sorted(set(x) ^ set(y))}"
        for k in x:
            d = first_diff(x[k], y[k], f"{path}/{k}")
            if d:
                return d
        return None
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return f"{path}: length {len(x)} != {len(y)}"
        for i, (p, q) in enumerate(zip(x, y)):
            d = first_diff(p, q, f"{path}[{i}]")
            if d:
                return d
        return None
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return None if math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12) else f"{path}: {x} != {y}"
    return None if x == y else f"{path}: {x!r} != {y!r}"


def leaves(obj, path=()):
    """Every leaf of a JSON value as (path, value)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, path + (i,))
    else:
        yield path, obj


def tampered(obj, path):
    """A deep copy of obj with the leaf at `path` changed (a number by one part in a million, a flag flipped, a text extended)."""
    import copy
    out = copy.deepcopy(obj)
    node = out
    for p in path[:-1]:
        node = node[p]
    v = node[path[-1]]
    if isinstance(v, bool):
        node[path[-1]] = not v
    elif isinstance(v, (int, float)):
        node[path[-1]] = v * (1.0 + 1e-6) + (1e-6 if v == 0 else 0.0)
    elif v is None:
        node[path[-1]] = 0
    else:
        node[path[-1]] = str(v) + "x"
    return out


def pct(values, q):
    """Percentile by linear interpolation between order statistics (numpy's default), in pure Python."""
    s = sorted(values)
    k = (len(s) - 1) * q / 100.0
    f = math.floor(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def gmean(vals):
    return math.exp(math.fsum(math.log(v) for v in vals) / len(vals))


def mixture(series_per_job):
    """Written again for the test: processes more than 5% above the fastest process of their own series and job."""
    total = slow = jobs_with = 0
    job_share, excess, cvs = [], [], []
    a_s = a_sn = a_o = a_on = 0
    for x in series_per_job:
        cvs.append(100.0 * statistics.stdev(x) / statistics.fmean(x))
        m = min(x)
        e = [v / m - 1.0 for v in x]
        s = [v > 0.05 for v in e]
        total += len(x)
        slow += sum(s)
        jobs_with += 1 if any(s) else 0
        job_share.append(sum(s) / len(x))
        excess += [v for v, f in zip(e, s) if f]
        for k in range(1, len(x)):
            if s[k - 1]:
                a_sn += 1
                a_s += s[k]
            else:
                a_on += 1
                a_o += s[k]
    return {"processes": total, "slow": slow, "share_slow": slow / total, "jobs": len(series_per_job), "jobs_with_slow": jobs_with,
            "job_share_min": min(job_share), "job_share_max": max(job_share),
            "cv_pct": {"median": statistics.median(cvs), "min": min(cvs), "max": max(cvs)},
            "excess_pct": {"q10": 100.0 * pct(excess, 10), "median": 100.0 * pct(excess, 50), "q90": 100.0 * pct(excess, 90)} if excess else None,
            "pairs_after_slow": a_sn, "p_slow_after_slow": a_s / a_sn if a_sn else None,
            "pairs_after_ok": a_on, "p_slow_after_ok": a_o / a_on if a_on else None}


def per_job_cells():
    """[{cell_id: cell}] of the 30 jobs, in the pool's order."""
    return [{c["cell_id"]: c for c in r["cells"]} for r, _ in job_docs()]


@lru_cache(maxsize=None)
def pool_mod():
    import pool
    return pool


def with_prefix(prefix, fn):
    """fn() with harness/pool.py's seed prefix replaced for the duration of the call."""
    pool = pool_mod()
    old = pool.SEED_PREFIX
    pool.SEED_PREFIX = prefix
    try:
        return fn()
    finally:
        pool.SEED_PREFIX = old


def without(obj, drop):
    """A copy of a JSON value without the dictionary keys in `drop` (the prose fields), which are checked for being text instead."""
    if isinstance(obj, dict):
        return {k: without(v, drop) for k, v in obj.items() if k not in drop}
    if isinstance(obj, list):
        return [without(v, drop) for v in obj]
    return obj


def prose_keys_are_text(obj, keys):
    found = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys:
                assert isinstance(v, str) and v.strip(), k
                found += 1
            else:
                found += prose_keys_are_text(v, keys)
    elif isinstance(obj, list):
        for v in obj:
            found += prose_keys_are_text(v, keys)
    return found


def guard(key, expected, prose=()):
    """arm64.json[key] equals `expected` (its prose fields aside), and a change to any single number or flag of it is seen."""
    got = arm()[key]
    assert prose_keys_are_text(got, set(prose)) >= (1 if prose else 0), key
    have = without(got, set(prose))
    d = first_diff(have, expected)
    assert d is None, f"{key}{d}"
    n = 0
    for path, _ in leaves(have):
        assert first_diff(tampered(have, path), expected) is not None, f"{key}: a change at {path} goes unseen"
        n += 1
    assert n > 5, key


# ---- the L2 noise facts

def expected_noise():
    c, pool = block(), pool_mod()
    res = [r for r, _ in job_docs()]
    det = [d for _, d in job_docs()]
    rule_max = read_json("harness", "criteria-v3.json")["verdict"]["aa_half_width_max_pct"]
    aa1 = [(r["controls"]["aa"]["a_ns"], r["controls"]["aa"]["b_ns"]) for r in res]
    aa2 = [(d["aa_extra"][DECIDING]["a_ns"], d["aa_extra"][DECIDING]["b_ns"]) for d in det]
    aa = {}
    for size, cell, pairs, st, job_hw in (("L1", "k02_add_fwd.L1", aa1, c["aa"], [r["controls"]["aa"]["half_width_pct"] for r in res]),
                                         ("L2", DECIDING, aa2, pool.pair_stat(c["cpu_model"], "aa_extra|" + DECIDING, aa2),
                                          [d["aa_extra"][DECIDING]["half_width_pct"] for d in det])):
        ratios = [statistics.median(b) / statistics.median(a) for a, b in pairs]
        aa[size] = {"cell_id": cell, "pooled": {k: st[k] for k in ("ratio", "ci95", "half_width_pct", "between_job_sd_pct")},
                    "jobs": len(pairs), "job_ratio_range": [min(ratios), max(ratios)],
                    "job_half_width_pct": {"min": min(job_hw), "max": max(job_hw)},
                    "per_job": {"ratio": ratios, "half_width_pct": job_hw},
                    "jobs_above_rule_max": sum(1 for h in job_hw if h > rule_max), "above_rule_max": st["half_width_pct"] > rule_max,
                    "mixture": {"a": mixture([p[0] for p in pairs]), "b": mixture([p[1] for p in pairs])}}
    cells = {x["cell_id"]: x for x in c["cells"]}
    x = cells[DECIDING]
    lay = c["layout_aa"][DECIDING]
    same = {"cell_id": DECIDING,
            "identical_binary_aa": {k: aa["L2"]["pooled"][k] for k in ("half_width_pct", "between_job_sd_pct")},
            "layout_aa": {k: lay[k] for k in ("half_width_pct", "between_job_sd_pct")},
            "as_compiled": {k: x["as_compiled"][k] for k in ("half_width_pct", "between_job_sd_pct")},
            "aligned": {k: x["aligned"][k] for k in ("half_width_pct", "between_job_sd_pct")}}
    jobs = per_job_cells()
    rows = []
    for cell in c["cells"]:
        cid = cell["cell_id"]
        none = [j[cid]["none_ns"] for j in jobs]
        fast = [j[cid]["fast_ns"] for j in jobs]
        an = [j[cid]["aligned"]["none_ns"] for j in jobs]
        af = [j[cid]["aligned"]["fast_ns"] for j in jobs]

        def floor(ns, fs):
            p10 = [pct(f, 10) / pct(n, 10) for n, f in zip(ns, fs)]
            mn = [min(f) / min(n) for n, f in zip(ns, fs)]
            return {"p10_ratio": gmean(p10), "p10_job_range": [min(p10), max(p10)], "min_ratio": gmean(mn), "min_job_range": [min(mn), max(mn)]}
        rows.append({"cell_id": cid, "size_class": cell["size_class"], "class": cell["class"], "none": mixture(none), "fast": mixture(fast),
                     "floor_ratio": {"as_compiled": floor(none, fast), "aligned": floor(an, af)}})
    by_size = {}
    for size in ("L1", "L2"):
        sel = [r for r in rows if r["size_class"] == size]
        e = {"cells": len(sel)}
        for side in ("none", "fast"):
            tot, sl = sum(r[side]["processes"] for r in sel), sum(r[side]["slow"] for r in sel)
            sh = [r[side]["share_slow"] for r in sel]
            e[side] = {"processes": tot, "slow": sl, "share_slow": sl / tot, "cell_share_min": min(sh), "cell_share_max": max(sh)}
        by_size[size] = e
    return {"slow_share": 0.05, "rule_aa_half_width_max_pct": rule_max, "identical_binary_aa": aa, "same_cell_l2": same,
            "mixture": {"cells": rows, "by_size": by_size}}


def test_noise_facts_are_rederived_from_the_per_job_samples():
    guard("noise", expected_noise(), prose=("definition", "source"))


def test_the_l2_identical_binary_aa_is_as_wide_as_the_l2_cell_and_the_rule_ceiling():
    """What the stored samples say (not a cause): an identical binary against itself is as scattered at L2 as the FAST/NONE pair,
    and its pooled half-width is above the rule's own A/A ceiling, while the L1 one is not."""
    n = arm()["noise"]
    l1, l2 = n["identical_binary_aa"]["L1"], n["identical_binary_aa"]["L2"]
    assert l1["pooled"]["half_width_pct"] == block()["aa"]["half_width_pct"] and not l1["above_rule_max"]
    assert l2["above_rule_max"] and l2["pooled"]["half_width_pct"] > n["rule_aa_half_width_max_pct"]
    same = n["same_cell_l2"]
    assert same["identical_binary_aa"]["half_width_pct"] > 0.5 * same["aligned"]["half_width_pct"]
    assert same["identical_binary_aa"]["between_job_sd_pct"] > 0.5 * same["aligned"]["between_job_sd_pct"]
    assert l2["jobs_above_rule_max"] > l2["jobs"] // 2 and l1["jobs_above_rule_max"] == 0
    # both sides of the identical binary carry the slow processes at L2, and none at L1
    assert l2["mixture"]["a"]["share_slow"] > 0.2 and l2["mixture"]["b"]["share_slow"] > 0.2
    assert l1["mixture"]["a"]["slow"] == l1["mixture"]["b"]["slow"] == 0


def test_the_slow_processes_are_in_the_l2_timings_and_only_in_none_for_the_lost_loops():
    rows = {r["cell_id"]: r for r in arm()["noise"]["mixture"]["cells"]}
    assert len(rows) == 16
    for cid in ("k04_rev.L2", "k05_stride2.L2"):
        assert rows[cid]["none"]["share_slow"] > 0.3 and rows[cid]["fast"]["slow"] == 0, cid
    sizes = arm()["noise"]["mixture"]["by_size"]
    assert sizes["L2"]["none"]["share_slow"] > 5 * sizes["L1"]["none"]["share_slow"]


# ---- the layout A/A against the placement statistic D

def expected_layout_vs_placement():
    c, pool = block(), pool_mod()
    jobs = per_job_cells()
    rows = []
    for x in c["cells"]:
        cid = x["cell_id"]
        st = x.get("placement")
        if st:
            d, src = st["d"], "pooled.json"
        else:
            d = pool.placement_stat(c["cpu_model"], f"{cid}|placement",
                                    [(j[cid]["none_ns"], j[cid]["fast_ns"], j[cid]["aligned"]["none_ns"], j[cid]["aligned"]["fast_ns"]) for j in jobs])
            src = "computed here"
        lay = c["layout_aa"][cid]
        rows.append({"cell_id": cid, "class": x["class"], "size_class": x["size_class"],
                     "layout_aa": {k: lay[k] for k in ("ratio", "ci95", "half_width_pct")},
                     "d": {k: d[k] for k in ("ratio", "ci95", "half_width_pct")}, "d_source": src,
                     "as_compiled_over_aligned": x["as_compiled"]["ratio"] / x["aligned"]["ratio"],
                     "d_excludes_1": d["ci95"][0] > 1 or d["ci95"][1] < 1, "layout_aa_excludes_1": lay["ci95"][0] > 1 or lay["ci95"][1] < 1,
                     "d_shift_pct": 100 * (d["ratio"] - 1), "layout_aa_shift_pct": 100 * (lay["ratio"] - 1),
                     "implied_fast_side_ratio": d["ratio"] / lay["ratio"]})
    top = max(rows, key=lambda r: abs(r["d_shift_pct"]))
    top1 = max((r for r in rows if r["size_class"] == "L1"), key=lambda r: abs(r["d_shift_pct"]))
    return {"layout_aa_builds": ["none", "none_a64"], "rows": rows,
            "d_excludes_1_layout_aa_includes_1": [r["cell_id"] for r in rows if r["d_excludes_1"] and not r["layout_aa_excludes_1"]],
            "largest_d_shift": {"cell_id": top["cell_id"], "d_shift_pct": top["d_shift_pct"]},
            "largest_d_shift_l1": {"cell_id": top1["cell_id"], "d_shift_pct": top1["d_shift_pct"]},
            "largest_layout_aa_shift_l1_pct": max(abs(r["layout_aa_shift_pct"]) for r in rows if r["size_class"] == "L1")}


def test_layout_aa_and_placement_statistic_are_rederived_for_all_sixteen_cells():
    got = arm()["layout_vs_placement"]
    want = expected_layout_vs_placement()
    stored_d = {q["cell_id"] for q in block()["cells"] if q.get("placement")}
    for r, w in zip(got["rows"], want["rows"]):
        # where D comes from is text: "pooled.json" for the kept cells that have it there, else the words of the builder
        assert (r["d_source"] == "pooled.json") == (r["cell_id"] in stored_d), r["cell_id"]
        assert w["d_source"] == "pooled.json" or r["d_source"].startswith("computed here"), r["cell_id"]
        w["d_source"] = r["d_source"]
    guard("layout_vs_placement", want, prose=("note",))
    assert "FAST" in got["note"] and "layout A/A" in got["note"]
    assert len(got["rows"]) == 16 and got["layout_aa_builds"] == ["none", "none_a64"]


def test_the_layout_aa_does_not_see_the_placement_shifts_that_d_sees():
    """The layout A/A moves NONE's loops only. On this core the stencil, the stride-2 loop and the gather at L1 move
    (FAST over NONE, compiled against aligned) by 3 to 11 percent, where the layout A/A moves them by 0.2% or less."""
    got = arm()["layout_vs_placement"]
    rows = {r["cell_id"]: r for r in got["rows"]}
    for cid, lo in (("k03_stencil.L1", 3.0), ("k06_gather.L1", 10.0), ("k05_stride2.L1", 4.0)):
        r = rows[cid]
        assert r["d_shift_pct"] > lo and abs(r["layout_aa_shift_pct"]) < 0.2, cid
        assert r["d_excludes_1"], cid
    # D's interval excludes 1 while the layout A/A interval includes it: the stencil at L1
    assert "k03_stencil.L1" in got["d_excludes_1_layout_aa_includes_1"] and not rows["k03_stencil.L1"]["layout_aa_excludes_1"]
    # matrix multiply at L1 is the one cell where the layout A/A moves a lot (NONE alone), in the direction opposite to D
    mm = rows["k08_matmul.L1"]
    assert mm["layout_aa_shift_pct"] > 3.0 and mm["d_shift_pct"] < 0
    assert got["largest_layout_aa_shift_l1_pct"] == abs(mm["layout_aa_shift_pct"])
    assert got["largest_d_shift"]["cell_id"] == "k06_gather.L1" and got["largest_d_shift_l1"] == got["largest_d_shift"]
    # D is the as-compiled ratio over the aligned one (pooled geometric mean over jobs): the two ways of writing it agree
    for r in got["rows"]:
        assert math.isclose(r["d"]["ratio"], r["as_compiled_over_aligned"], rel_tol=1e-6), r["cell_id"]


# ---- matrix multiply: time against instructions

def expected_matmul_cost():
    c = block()
    _, det = job_docs()[0]
    res, _ = job_docs()[0]
    vec = det["kernels"]["k08_matmul"]["fast"]["vectorization"]
    width = vec["width"]
    inter = int(re.search(r"interleaved count: (\d+)", " ".join(vec["remarks"])).group(1))
    out = {"vector_pass_elements": width * inter, "width": width, "interleave": inter, "sizes": {}}
    for size in ("L1", "L2"):
        x = next(q for q in c["cells"] if q["cell_id"] == f"k08_matmul.{size}")
        rc = next(q for q in res["cells"] if q["cell_id"] == x["cell_id"])
        d = int(rc["command"].splitlines()[-1].split()[-2])
        row = {"d": d, "d_mod_pass": d % (width * inter), "whole_passes": d // (width * inter), "working_set_bytes": rc["working_set_bytes"]}
        for col, ic in (("as_compiled", "instr"), ("aligned", "aligned_instr")):
            t, i = x[col]["ratio"], x[ic]["ratio"]
            row[col] = {"time_ratio": t, "instr_ratio": i, "log_time_over_log_instr": math.log(t) / math.log(i)}
        out["sizes"][size] = row
    return out


def test_matmul_time_against_instruction_ratio():
    guard("matmul_cost", expected_matmul_cost())
    m = arm()["matmul_cost"]
    s = m["sizes"]
    assert (m["width"], m["interleave"], m["vector_pass_elements"]) == (4, 2, 8)
    # the two cells differ in cache level, d and the elements left after whole vector passes; the instruction ratio is 1.8
    # and 1.2, the time ratio 1.55 and 1.02: the time follows the instruction count at L1 and hardly at L2
    assert s["L1"]["d"] == 52 and s["L2"]["d"] == 209 and (s["L1"]["d_mod_pass"], s["L2"]["d_mod_pass"]) == (4, 1)
    assert (s["L1"]["whole_passes"], s["L2"]["whole_passes"]) == (6, 26)
    for col in ("as_compiled", "aligned"):
        for size in ("L1", "L2"):
            assert 0 < s[size][col]["log_time_over_log_instr"] < 1, (size, col)
            assert s[size][col]["time_ratio"] < s[size][col]["instr_ratio"], (size, col)
        assert s["L1"][col]["time_ratio"] > 1.5 and s["L2"][col]["time_ratio"] < 1.03
        assert s["L2"][col]["log_time_over_log_instr"] < 0.5 * s["L1"][col]["log_time_over_log_instr"]
    assert s["L1"]["working_set_bytes"] < s["L2"]["working_set_bytes"]


# ---- the forward loops: instructions added per call

def expected_forward_instr():
    c = block()
    res, _ = job_docs()[0]
    rows = []
    for x in c["cells"]:
        if x["kernel"] not in ("k01_sum_fwd", "k02_add_fwd", "k03_stencil"):
            continue
        rc = next(q for q in res["cells"] if q["cell_id"] == x["cell_id"])
        n = int(rc["command"].splitlines()[-1].split()[-2])
        row = {"cell_id": x["cell_id"], "kernel": x["kernel"], "size_class": x["size_class"], "elements": n}
        for col, ik in (("as_compiled", "instr"), ("aligned", "aligned_instr")):
            row[col] = {"none": x[ik]["none"], "fast": x[ik]["fast"], "added": x[ik]["fast"] - x[ik]["none"],
                        "instr_ratio": x[ik]["fast"] / x[ik]["none"], "time_ratio": x[col]["ratio"]}
        rows.append(row)
    same = {k: {col: len({r[col]["added"] for r in rows if r["kernel"] == k}) == 1 for col in ("as_compiled", "aligned")}
            for k in ("k01_sum_fwd", "k02_add_fwd", "k03_stencil")}
    return {"cells": rows, "added_same_at_both_sizes": same}


def test_forward_loops_instruction_counts_added_per_call():
    guard("forward_instr", expected_forward_instr())
    f = arm()["forward_instr"]
    rows = {r["cell_id"]: r for r in f["cells"]}
    assert len(rows) == 6
    # Cachegrind counts: the check adds 0 (sum), 26 (add) and 35 (stencil) instructions per call as compiled, at both sizes
    assert [rows[f"{k}.{s}"]["as_compiled"]["added"] for k in ("k01_sum_fwd", "k02_add_fwd", "k03_stencil") for s in ("L1", "L2")] == [0, 0, 26, 26, 35, 35]
    assert all(all(v.values()) for v in f["added_same_at_both_sizes"].values())
    # a constant per call is a smaller share of a longer call: the add at L1 (2730 elements) against L2 (43690)
    a1, a2 = rows["k02_add_fwd.L1"], rows["k02_add_fwd.L2"]
    assert (a1["elements"], a2["elements"]) == (2730, 43690)
    assert a1["as_compiled"]["instr_ratio"] - 1.0 > 10 * (a2["as_compiled"]["instr_ratio"] - 1.0)


# ---- the stored diffs predate the normalize fix

def _old_normalize(lines):
    """harness/asm.normalize as it was when the stored Arm diffs were written: branch targets of four or more hex digits."""
    out = []
    for ln in lines:
        ln = re.sub(r"^\s*[0-9a-f]+:\s*", "", ln)
        ln = re.sub(r"\b[0-9a-f]{4,} <", "<", ln)
        ln = re.sub(r"<([^>+]*)\+0x[0-9a-f]+>", r"<\1+off>", ln)
        out.append(ln.rstrip())
    return out


def _changed(lines):
    """The added and removed lines of a unified diff (not its two header lines)."""
    return [x for x in lines if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))]


def test_stored_diff_counts_and_what_the_fixed_normalize_makes_of_the_same_listings():
    pat = re.compile(r"\b[0-9a-f]{3,} <")
    names = (("L1", "L1.diff"), ("L1_aligned", "L1.aligned.diff"), ("L2", "L2.diff"), ("L2_aligned", "L2.aligned.diff"))
    builds_of = {"L1": ("none", "fast"), "L2": ("none", "fast"), "L1_aligned": ("none_a64", "fast_a64"), "L2_aligned": ("none_a64", "fast_a64")}
    job = job_dirs()[0]
    kernels = sorted({x["kernel"] for x in block()["cells"]})
    want = []
    for k in kernels:
        row = {"kernel": k}
        for name, suffix in names:
            stored_body = _changed(listing(job, f"{k}.{suffix}"))
            a, b = builds_of[name]
            none_l, fast_l = listing(job, f"{k}.{a}.s"), listing(job, f"{k}.{b}.s")
            # provenance: the stored diff is what the old normalize makes of the saved listings
            old_body = _changed(list(difflib.unified_diff(_old_normalize(none_l), _old_normalize(fast_l), "a", "b", lineterm="")))
            assert stored_body == old_body, (k, name)
            fresh_body = _changed(asm.unified_diff(none_l, fast_l, "a", "b").splitlines())
            assert not [x for x in fresh_body if pat.search(x)], (k, name)   # no three-digit target survives the fix
            row[name] = {"added": sum(1 for x in stored_body if x[0] == "+"), "removed": sum(1 for x in stored_body if x[0] == "-"),
                         "added_after_fix": sum(1 for x in fresh_body if x[0] == "+"), "removed_after_fix": sum(1 for x in fresh_body if x[0] == "-")}
        want.append(row)
    got = arm()["stored_diffs"]
    assert got["stored_diffs_predate_fix"] is True and "before the fix" in got["note"]
    assert prose_keys_are_text(got, {"note", "normalize_fixed_in"}) == 2
    d = first_diff(got["kernels"], want)
    assert d is None, d
    for path, _ in leaves(got["kernels"]):
        assert first_diff(tampered(got["kernels"], path), want) is not None, path
    # the counts the page already printed (kernels[].diffs[name].added / removed) are the stored ones
    for kr, row in zip(arm()["kernels"], want):
        for name, _ in names:
            assert kr["diffs"][name]["added"] == row[name]["added"] and kr["diffs"][name]["removed"] == row[name]["removed"]
    # the fix changes counts: the stored Arm diffs hold moved-branch lines (a line added and a line removed per moved branch)
    lost = [(row["kernel"], n) for row in want for n, _ in names
            if row[n]["added_after_fix"] < row[n]["added"] or row[n]["removed_after_fix"] < row[n]["removed"]]
    assert len(lost) >= 8 and all(row[n]["added_after_fix"] <= row[n]["added"] and row[n]["removed_after_fix"] <= row[n]["removed"]
                                  for row in want for n, _ in names)
    # every kernel whose stored diff is empty stays empty
    assert [row["kernel"] for row in want if row["L1"]["added"] == row["L1"]["removed"] == 0] == ["k01_sum_fwd"]
    assert want[0]["L1"]["added_after_fix"] == 0


# ---- the interval methods (robustness/analyze.py --arm)

METHOD_NAMES = {"a": "harness bootstrap", "b": "block bootstrap, 1 ABBA quartet", "b2": "block bootstrap, 2 ABBA quartets",
                "b5": "block bootstrap, 5 ABBA quartets", "c": "jobs-only bootstrap", "ct": "jobs-only t interval",
                "d": "lag-1 effective sample size", "d0": "first form of the lag-1 correction"}


@lru_cache(maxsize=None)
def analyze_mod():
    return _load_module(os.path.join(REPO, "robustness", "analyze.py"), "arm_test_robustness_analyze")


def expected_interval_methods():
    an = analyze_mod()
    rob = read_json("robustness", "results-arm.json")
    r = rob["datasets"]["s8arm"]["cpus"][block()["cpu_model"]]
    out = []
    for m in rob["methods"]:
        x = r["methods"][m]
        cmp_ = an.compare(r, m)
        lo, hi = an.margins(r, m)
        dec = x["cells"][DECIDING]["al"]
        out.append({"id": m, "name": METHOD_NAMES[m], "form": cmp_["form"], "aa_half_width_pct": cmp_["aa_hw_pct"],
                    "forward_limit": 1.0 + x["limit_pct"] / 100.0, "forward_misses": an.forward_misses(r, m),
                    "placement_sensitive": sorted(cid for cid, q in x["cells"].items() if q.get("ps")),
                    "deciding_cell": {"cell_id": DECIDING, "column": "aligned", "ratio": dec[0], "ci95": [dec[1], dec[2]]},
                    "flips": {k: len(v) for k, v in cmp_["flips"].items()},
                    "width_ratio_median": cmp_["width_median"], "width_ratio_max": cmp_["width_max"],
                    "min_lost_ci95_lo": lo, "max_forward_ci95_hi": hi})
    return rob, r, out


def test_interval_methods_are_the_robustness_files_numbers():
    rob, r, want = expected_interval_methods()
    got = arm()["interval_methods"]
    d = first_diff(got["methods"], want)
    assert d is None, d
    for path, _ in leaves(got["methods"]):
        assert first_diff(tampered(got["methods"], path), want) is not None, path
    forms = {}
    for m in want:
        forms[m["form"]] = forms.get(m["form"], 0) + 1
    assert got["forms"] == forms and got["map_methods"] == [m["id"] for m in want if m["form"] == "map"]
    assert got["inconclusive_methods"] == [m["id"] for m in want if m["form"] == "inconclusive"]
    assert got["pool_form_of_record"] == block()["verdict"]["form"] and got["jobs"] == r["jobs"] == arm()["jobs"]
    assert got["self_test"] == rob["datasets"]["s8arm"]["self_test"] and got["autocorr"] == r["autocorr"]
    assert got["source"] == ROBUST and got["source_sha256"] == hashlib.sha256(open(os.path.join(REPO, *ROBUST.split("/")), "rb").read().replace(b"\r\n", b"\n")).hexdigest()


def test_method_a_of_the_robustness_file_is_the_pool():
    rob = read_json("robustness", "results-arm.json")
    st = rob["datasets"]["s8arm"]["self_test"]
    assert st["forms_equal"] and st["exact"] == st["numbers_checked"] == 99 and st["max_rel_diff"] <= 1e-12
    a = rob["datasets"]["s8arm"]["cpus"][block()["cpu_model"]]["methods"]["a"]
    assert a["form"] == block()["verdict"]["form"] and a["limit_pct"] == block()["verdict"]["forward_limit_pct"]
    for x in block()["cells"]:
        if x["size_class"] in ("L1", "L2"):
            c = a["cells"][x["cell_id"]]
            d1 = first_diff(c["ac"], [x["as_compiled"]["ratio"], *x["as_compiled"]["ci95"]])
            d2 = first_diff(c["al"], [x["aligned"]["ratio"], *x["aligned"]["ci95"]])
            assert d1 is None and d2 is None, (x["cell_id"], d1, d2)
    # the Arm analysis is its own dataset: the x86-64 robustness file does not hold it
    assert "s8arm" not in read_json("robustness", "results.json")["datasets"]


# ---- the seed sensitivity (arm64/seeds.py)

def seeds_doc():
    return read_json(*SEEDS.split("/"))


def aligned_pairs(cid):
    return [(j[cid]["aligned"]["none_ns"], j[cid]["aligned"]["fast_ns"]) for j in per_job_cells()]


def test_seed_file_is_about_this_pool_and_reproduces_its_stored_numbers():
    s, c = seeds_doc(), block()
    sha = hashlib.sha256(open(os.path.join(REPO, *ARM_POOLED.split("/")), "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    assert s["pool"]["sha256"] == sha and s["pool"]["jobs"] == c["jobs"] and s["pool"]["cpu_model"] == c["cpu_model"]
    assert s["pool"]["stored_form"] == c["verdict"]["form"] == "inconclusive"
    assert s["pool"]["criteria_sha256"] == pooled()["criteria_sha256"]
    assert s["pool"]["stored_forward_missed"] == [DECIDING]
    st = s["stored_seed"]
    assert st["prefix"] == pool_mod().SEED_PREFIX == "20261011" and st["resamples"] == pool_mod().RESAMPLES == pooled()["resamples"]
    assert st["reproduced"]["max_rel_diff"] <= 1e-12 and st["reproduced"]["numbers_checked"] == 3 * len(s["rows"]) and st["replica_matches"] is True
    assert st["fixed_on"].startswith("2026-10-12") and "unpublished" in st["fixed_in"]
    assert s["alt_seeds"]["count"] == 400 and s["alt_seeds"]["resamples"] == 2000 and "{:03d}" in s["alt_seeds"]["pattern"]
    # the rows are the statistics that enter the rules, and their stored values are the pool's
    want = []
    for x in c["cells"]:
        if x["size_class"] not in ("L1", "L2"):
            continue
        if x["class"] == "kept":
            want += [("forward", x["cell_id"], "aligned"), ("placement", x["cell_id"], "d")]
        elif x["class"] == "lost":
            want += [("lost", x["cell_id"], "as_compiled"), ("lost", x["cell_id"], "aligned")]
    want.append(("aa", None, "aa"))
    want += [("positive", pid, "novec") for pid in c["positive"]]
    assert [(r["kind"], r["cell_id"], r["column"]) for r in s["rows"]] == want
    assert len({r["id"] for r in s["rows"]}) == len(want)
    for r in s["rows"]:
        if r["kind"] == "aa":
            ref = c["aa"]
        elif r["kind"] == "positive":
            ref = c["positive"][r["cell_id"]]
        else:
            x = next(q for q in c["cells"] if q["cell_id"] == r["cell_id"])
            ref = x["placement"]["d"] if r["kind"] == "placement" else x[r["column"]]
        assert r["stored"] == {"ratio": ref["ratio"], "lo": ref["ci95"][0], "hi": ref["ci95"][1], "half_width_pct": ref["half_width_pct"]}, r["id"]
        assert r["alt"]["draws"] == 400 and len(r["alt"]["first"]) == s["alt_seeds"]["sample_seeds"] == 8, r["id"]


def test_deciding_cell_numbers_are_rederived_from_the_pool_under_a_few_seeds():
    s, c = seeds_doc(), block()
    d = s["deciding_cell"]
    pool = pool_mod()
    cpu = c["cpu_model"]
    sid = DECIDING + "|aligned"
    stored = next(x for x in c["cells"] if x["cell_id"] == DECIDING)["aligned"]
    again = pool.pair_stat(cpu, sid, aligned_pairs(DECIDING))
    assert again["ci95"] == stored["ci95"] and again["ratio"] == stored["ratio"]
    limit = 1.0 + c["verdict"]["forward_limit_pct"] / 100.0
    assert d["cell_id"] == DECIDING and d["column"] == "aligned" and d["limit"] == limit
    assert d["stored_hi"] == stored["ci95"][1] and abs(d["margin_over_limit"] - (stored["ci95"][1] - limit)) < 1e-12 and d["margin_over_limit"] > 0
    ups = d["upper_ends"]
    assert len(ups) == d["alt_draws"] == 400
    for i in (1, 2, 3, 150, 399, 400):
        prefix = s["alt_seeds"]["pattern"].format(i)
        got = with_prefix(prefix, lambda: pool.pair_stat(cpu, sid, aligned_pairs(DECIDING)))
        assert math.isclose(got["ci95"][1], ups[i - 1], rel_tol=1e-12), i
    # the summaries are these 400 values
    d_ = first_diff(d["alt_hi"], {"median": pct(ups, 50), "p05": pct(ups, 5), "p95": pct(ups, 95), "min": min(ups), "max": max(ups)})
    assert d_ is None, d_
    assert d["alt_at_or_above_limit"] == sum(1 for h in ups if h >= limit) and d["alt_above_limit"] == sum(1 for h in ups if h > limit)
    assert math.isclose(d["alt_share_at_or_above_limit"], d["alt_at_or_above_limit"] / 400)
    assert math.isclose(d["stored_hi_at_or_below_share"], sum(1 for h in ups if h <= stored["ci95"][1]) / 400)
    assert d["stored_rank_from_top"] == 1 + sum(1 for h in ups if h > stored["ci95"][1])
    assert d["seeds_at_or_above_limit"] == [s["alt_seeds"]["pattern"].format(i + 1) for i, h in enumerate(ups) if h >= limit]


def row_stat_id(r):
    if r["kind"] == "aa":
        return "aa"
    if r["kind"] == "positive":
        return "novec|" + r["cell_id"]
    if r["kind"] == "placement":
        return r["cell_id"] + "|placement"
    return f"{r['cell_id']}|{r['column']}"


def row_sides(r):
    """The per-job samples behind one row of the seed file, taken from the jobs' own files by the test's own code."""
    docs = [d for d, _ in job_docs()]
    if r["kind"] == "aa":
        return [[d["controls"]["aa"]["a_ns"], d["controls"]["aa"]["b_ns"]] for d in docs]
    if r["kind"] == "positive":
        prs = [next(p for p in d["controls"]["positive"] if p["cell_id"] == r["cell_id"]) for d in docs]
        return [[p["none_ns"], p["novec_ns"]] for p in prs]
    cs = [next(c for c in d["cells"] if c["cell_id"] == r["cell_id"]) for d in docs]
    if r["kind"] == "placement":
        return [[c["none_ns"], c["fast_ns"], c["aligned"]["none_ns"], c["aligned"]["fast_ns"]] for c in cs]
    if r["column"] == "aligned":
        return [[c["aligned"]["none_ns"], c["aligned"]["fast_ns"]] for c in cs]
    return [[c["none_ns"], c["fast_ns"]] for c in cs]


def test_every_statistic_of_the_first_two_alternative_seeds_is_rederived():
    """All rows of the seed file (forward, lost, placement, A/A, positive control), seeds 1 and 2: the interval ends and the
    half-width are the pool's own function applied to the jobs' samples under that seed prefix."""
    s, c = seeds_doc(), block()
    pool = pool_mod()
    cpu = c["cpu_model"]
    for i in (1, 2):
        prefix = s["alt_seeds"]["pattern"].format(i)
        for r in s["rows"]:
            comb = (lambda n, f, na, fa: (f / n) / (fa / na)) if r["kind"] == "placement" else (lambda ma, mb: mb / ma)
            got = with_prefix(prefix, lambda: pool.pooled_stat(cpu, row_stat_id(r), row_sides(r), comb))
            d = first_diff(r["alt"]["first"][i - 1], [got["ci95"][0], got["ci95"][1], got["half_width_pct"]])
            assert d is None, f"{r['id']} seed {i}: {d}"
            assert math.isclose(got["ratio"], r["alt"]["ratio"], rel_tol=1e-12) and math.isclose(got["ratio"], r["stored"]["ratio"], rel_tol=1e-12), r["id"]


def test_derived_forms_follow_from_the_deciding_cells_upper_ends():
    """Under each of the 400 seeds the form is MAP unless the deciding cell's upper end is above the limit: the other judged
    forward cells, the lost cells, the A/A control and the positive control pass under every seed, and the placement-sensitive
    cells are the same four under every seed."""
    s, c = seeds_doc(), block()
    limit = 1.0 + c["verdict"]["forward_limit_pct"] / 100.0
    ups = s["deciding_cell"]["upper_ends"]
    prefixes = [s["alt_seeds"]["pattern"].format(i) for i in range(1, 401)]
    d = s["derived"]
    miss = [p for p, h in zip(prefixes, ups) if h > limit]
    assert d["seeds"] == len(ups) == 400 and d["equals_analyse_cpu_on_first"] == s["full"]["count"] == 40
    assert d["not_map_seeds"] == miss
    assert d["forms"] == {k: n for k, n in (("map", 400 - len(miss)), ("inconclusive", len(miss))) if n}
    assert d["forward_missed_counts"] == ({DECIDING: len(miss)} if miss else {})
    assert d["lost_missed_any"] is False and d["positive_seen_in_all"] is True
    always = sorted(r["cell_id"] for r in s["rows"] if r["kind"] == "placement" and r["alt"]["sensitive"] == 400)
    never = [r["id"] for r in s["rows"] if r["kind"] == "placement" and r["alt"]["sensitive"] == 0]
    assert d["placement_sets"] == [{"cells": always, "seeds": 400}] and always == sorted(p["cell_id"] for p in c["verdict"]["placement_sensitive"])
    assert len(always) + len(never) == sum(1 for r in s["rows"] if r["kind"] == "placement")
    for r in s["rows"]:
        a = r["alt"]
        if r["kind"] == "forward" and r["judged"] and r["cell_id"] != DECIDING:
            assert a["above_limit"] == 0 and not a["ratio_above_point_max"], r["id"]
        if r["kind"] == "lost":
            assert a["below_limit"] == 0, r["id"]
        if r["kind"] == "aa":
            assert a["above_limit"] == 0 and a["forward_limit_above_floor"] == 0
        if r["kind"] == "positive":
            assert a["seen"] == 400, r["id"]
    # the whole analysis of the first 40 seeds gives the same forms
    f = s["full"]
    assert [p["prefix"] in d["not_map_seeds"] for p in f["per_seed"]] == [p["form"] != "map" for p in f["per_seed"]]


def test_converged_reading_of_the_deciding_cell_is_rederived():
    """100 000 draws (50 independent streams of 2000) under the stored prefix: the interval ends without Monte-Carlo noise."""
    import numpy as np
    s, c = seeds_doc(), block()
    pool = pool_mod()
    cpu, sid = c["cpu_model"], DECIDING + "|aligned"
    sbj = [[a, b] for a, b in aligned_pairs(DECIDING)]
    J = len(sbj)
    r = []
    for n in range(s["converged"]["chunks"]):
        stat_id = f"{sid}|conv{n:03d}"
        idx = pool.draws(pool.seed_for(cpu, stat_id, "jobs"), (pool.RESAMPLES, J), J)
        meds = [pool._side_medians(cpu, stat_id, k, idx, [q[k] for q in sbj]) for k in range(2)]
        r.append(np.exp(np.mean(np.log(meds[1] / meds[0]), axis=1)))
    r = sorted(float(x) for x in np.concatenate(r))
    assert len(r) == s["converged"]["resamples"] == 100000
    lo, hi = r[int(round(0.025 * len(r), 9))], r[int(round(0.975 * len(r), 9)) - 1]
    conv = s["deciding_cell"]["converged"]
    assert math.isclose(conv["lo"], lo, rel_tol=1e-9) and math.isclose(conv["hi"], hi, rel_tol=1e-9) and conv["resamples"] == len(r)
    limit = 1.0 + block()["verdict"]["forward_limit_pct"] / 100.0
    assert conv["above_limit"] == (hi > limit)


def test_full_analysis_under_two_other_seeds_is_rederived():
    s, c = seeds_doc(), block()
    pool = pool_mod()
    crit = pool.criteria_and_sha()[0]
    docs = [r for r, _ in job_docs()]
    for i in (1, 2):
        prefix = s["alt_seeds"]["pattern"].format(i)
        blk = with_prefix(prefix, lambda: pool.analyse_cpu(c["cpu_model"], docs, crit, full=False))
        rec = s["full"]["per_seed"][i - 1]
        assert rec["prefix"] == prefix and rec["form"] == blk["verdict"]["form"]
        dec = next(x for x in blk["cells"] if x["cell_id"] == DECIDING)["aligned"]
        assert math.isclose(rec["deciding_hi"], dec["ci95"][1], rel_tol=1e-12) and math.isclose(rec["deciding_lo"], dec["ci95"][0], rel_tol=1e-12)
        assert rec["placement_sensitive"] == sorted(p["cell_id"] for p in blk["verdict"]["placement_sensitive"])
        assert math.isclose(rec["aa_half_width_pct"], blk["aa"]["half_width_pct"], rel_tol=1e-12)
        # the deciding cell's upper end here is the one of the 400-seed list for the same seed
        assert math.isclose(rec["deciding_hi"], s["deciding_cell"]["upper_ends"][i - 1], rel_tol=1e-12)
    f = s["full"]
    assert f["count"] == len(f["per_seed"]) == len(f["prefixes"]) == 40 and sum(f["forms"].values()) == 40
    assert [p["prefix"] for p in f["per_seed"]] == f["prefixes"] == [s["alt_seeds"]["pattern"].format(i) for i in range(1, 41)]
    for cid, n in f["forward_missed_counts"].items():
        assert n == sum(1 for p in f["per_seed"] if cid in p["forward_missed"]), cid
    assert f["forms"] == {k: sum(1 for p in f["per_seed"] if p["form"] == k) for k in f["forms"]}
    assert f["lost_missed_any"] == any(p["lost_missed"] for p in f["per_seed"])
    assert sum(q["seeds"] for q in f["placement_sets"]) == 40


def test_seed_rows_summaries_are_consistent_with_their_rules():
    s = seeds_doc()
    limit = 1.0 + block()["verdict"]["forward_limit_pct"] / 100.0
    crit = read_json("harness", "criteria-v3.json")["verdict"]
    for r in s["rows"]:
        a = r["alt"]
        if r["kind"] == "forward":
            assert a["hi"]["min"] <= a["hi"]["p05"] <= a["hi"]["median"] <= a["hi"]["p95"] <= a["hi"]["max"], r["id"]
            assert a["at_or_above_limit"] >= a["above_limit"] >= 0 and r["limit"] == limit
            assert r["converged"]["above_limit"] == (r["converged"]["hi"] > limit) and r["converged"]["resamples"] == 100000
            assert r["converged"]["ratio_check"] is True
            # judged = not placement-sensitive in the pool
            assert r["judged"] == (r["cell_id"] not in {p["cell_id"] for p in block()["verdict"]["placement_sensitive"]})
        elif r["kind"] == "lost":
            assert r["limit"] == crit["lost_ci_lo_min_ratio"] and a["lo"]["min"] > r["limit"] and a["below_limit"] == 0, r["id"]
        elif r["kind"] == "placement":
            assert 0 <= a["excludes_1"] <= 400 and a["sensitive"] == (a["excludes_1"] if r["mechanical"] else 0), r["id"]
        elif r["kind"] == "aa":
            assert a["above_limit"] == 0 and a["forward_limit_above_floor"] == 0 and r["limit"] == crit["aa_half_width_max_pct"]
            assert a["half_width_pct"]["max"] < crit["aa_half_width_max_pct"]
        else:
            assert r["kind"] == "positive" and 0 <= a["seen"] <= 400 and a["lo"]["min"] <= a["lo"]["median"] <= a["lo"]["max"], r["id"]
        if r["kind"] != "aa":
            assert a["lo"]["min"] <= a["lo"]["p05"] <= a["lo"]["median"] <= a["lo"]["p95"] <= a["lo"]["max"], r["id"]


def test_seed_sensitivity_in_arm64_json_is_the_stored_file():
    s, got = seeds_doc(), arm()["seed_sensitivity"]
    assert got["source"] == SEEDS and got["script"] == "arm64/seeds.py"
    assert got["source_sha256"] == hashlib.sha256(open(os.path.join(REPO, *SEEDS.split("/")), "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    assert got["pool_sha256"] == s["pool"]["sha256"] == arm()["source_sha256"]
    assert got["deciding_cell"] == {k: v for k, v in s["deciding_cell"].items() if k not in ("upper_ends", "seeds_at_or_above_limit")}
    assert len(got["rows"]) == len(s["rows"])
    for g, r in zip(got["rows"], s["rows"]):
        assert (g["id"], g["kind"], g["cell_id"], g["column"], g["stored"], g["draws"]) == (r["id"], r["kind"], r["cell_id"], r["column"], r["stored"], r["alt"]["draws"])
        if r["kind"] == "forward":
            assert g["alt_hi"] == r["alt"]["hi"] and g["converged_hi"] == r["converged"]["hi"] and g["alt_at_or_above_limit"] == r["alt"]["at_or_above_limit"]
            assert (g["judged"], g["limit"], g["alt_above_limit"], g["alt_above_stored"], g["converged_above_limit"]) == \
                (r["judged"], r["limit"], r["alt"]["above_limit"], r["alt"]["above_stored"], r["converged"]["above_limit"])
        elif r["kind"] == "lost":
            assert g["alt_lo"] == r["alt"]["lo"] and g["alt_below_limit"] == r["alt"]["below_limit"] and g["limit"] == r["limit"]
        elif r["kind"] == "placement":
            assert (g["alt_excludes_1"], g["alt_sensitive"], g["mechanical"]) == (r["alt"]["excludes_1"], r["alt"]["sensitive"], r["mechanical"])
            assert (g["stored_excludes_1"], g["stored_sensitive"]) == (r["stored_excludes_1"], r["stored_sensitive"])
        elif r["kind"] == "positive":
            assert g["alt_lo"] == r["alt"]["lo"] and g["alt_seen"] == r["alt"]["seen"]
        else:
            assert g["alt_half_width_pct"] == r["alt"]["half_width_pct"] and g["alt_above_limit"] == r["alt"]["above_limit"]
            assert g["alt_forward_limit_above_floor"] == r["alt"]["forward_limit_above_floor"] and g["limit"] == r["limit"]
        assert not ({"first", "rule"} & set(g)), "the per-seed samples and the rule texts stay in the seed file"
    assert got["full"] == {k: s["full"][k] for k in ("count", "forms", "forward_missed_counts", "lost_missed_any", "placement_sets",
                                                     "aa_half_width_pct", "forward_limit_pct", "deciding_hi")}
    assert got["derived"] == {k: s["derived"][k] for k in ("basis", "seeds", "equals_analyse_cpu_on_first", "forms", "forward_missed_counts",
                                                           "lost_missed_any", "placement_sets", "positive_seen_in_all", "not_map_seeds")}
    assert got["stored_seed"] == {k: s["stored_seed"][k] for k in ("prefix", "resamples", "fixed_on", "fixed_in")}
    assert got["alt_seeds"] == {k: s["alt_seeds"][k] for k in ("pattern", "count", "resamples")}
    assert got["converged_resamples"] == s["converged"]["resamples"]


def test_a_seed_file_made_from_another_pool_is_refused():
    """The builder demands that the seed file's pool hash is the pool's: a stale or edited file stops the build."""
    b = builder()
    s = seeds_doc()
    sha = arm()["seed_sensitivity"]["pool_sha256"]
    b._arm_seed_sensitivity(s, "x" * 64, sha)  # the right pool: accepted
    bad = json.loads(json.dumps(s))
    bad["pool"]["sha256"] = "0" * 64
    try:
        b._arm_seed_sensitivity(bad, "x" * 64, sha)
    except AssertionError:
        pass
    else:
        raise AssertionError("a seed file made from another pool was accepted")


def test_the_builder_refuses_a_seed_file_or_robustness_file_that_is_not_about_this_pool():
    """A seed file whose deciding-cell interval end is not the pool's, or a robustness file whose method (a) does not reproduce
    the pool's verdict form, stops the build (nothing is written)."""
    s, rob = seeds_doc(), read_json("robustness", "results-arm.json")
    tmp = tempfile.mkdtemp(prefix="arm-tamper-")
    try:
        bad_s = json.loads(json.dumps(s))
        bad_s["deciding_cell"]["stored_hi"] += 1e-6
        bad_r = json.loads(json.dumps(rob))
        bad_r["datasets"]["s8arm"]["cpus"][block()["cpu_model"]]["methods"]["a"]["form"] = "map"
        for attr, doc in (("ARM_SEEDS", bad_s), ("ARM_ROBUSTNESS", bad_r)):
            path = os.path.join(tmp, attr + ".json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(doc, f)
            b = _load_module(os.path.join(REPO, "scripts", "build_site_data.py"), "arm_test_tamper_" + attr)
            setattr(b, attr, path)   # an absolute path replaces the repository-relative one in os.path.join
            try:
                b.arm64_data(None, None)
            except AssertionError:
                pass
            else:
                raise AssertionError(f"a changed {attr} file was accepted")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_the_seed_script_constants_are_the_stored_files():
    """arm64/seeds.py and arm64/seed-sensitivity.json describe the same run (seed list, counts, deciding cell), and the
    script's own comparison finds a changed number."""
    s = seeds_doc()
    sc = _load_module(os.path.join(REPO, "arm64", "seeds.py"), "arm_test_seeds_script")
    assert sc.SEED_PATTERN == s["alt_seeds"]["pattern"] and sc.ALT_COUNT == s["alt_seeds"]["count"] == 400
    assert sc.RESAMPLES == s["alt_seeds"]["resamples"] == s["stored_seed"]["resamples"]
    assert sc.SAMPLE_SEEDS == s["alt_seeds"]["sample_seeds"] and sc.FULL_COUNT == s["full"]["count"]
    assert sc.CONVERGED_CHUNKS == s["converged"]["chunks"] and sc.STORED_PREFIX == s["stored_seed"]["prefix"] == s["converged"]["seed_prefix"]
    assert sc.DECIDING == (s["deciding_cell"]["cell_id"], s["deciding_cell"]["column"]) and sc.POOLED == s["pool"]["path"]
    assert sc.FIXED_ON == s["stored_seed"]["fixed_on"] and sc.CHECK_FULL <= sc.FULL_COUNT and sc.SAMPLE_SEEDS <= sc.ALT_COUNT
    assert sc.seed_prefixes(3) == ["seedsens-001", "seedsens-002", "seedsens-003"]
    assert sc.same(s, json.loads(json.dumps(s))) is None
    n = 0
    for path, v in leaves({k: s[k] for k in ("stored_seed", "deciding_cell", "full", "derived")}):
        if isinstance(v, (int, float)) and not isinstance(v, bool) and n < 60:
            assert sc.same(s, tampered(s, path)) is not None, path
            n += 1
    assert n == 60


# ---------------------------------------------------------------- the file itself

def test_new_keys_are_all_present_and_the_old_ones_unchanged():
    a = arm()
    for k in NEW_KEYS:
        assert k in a, k
    assert a["verdict"]["form"] == block()["verdict"]["form"] == "inconclusive"  # the stored verdict is what it was


def test_file_is_small_and_has_no_run_links_or_sample_notice():
    path = os.path.join(SITE_DATA, "arm64.json")
    size = os.path.getsize(path)
    # 88 KB with the cells, kernels and verdict; the sensitivity readings (seeds, interval methods, noise, layout, matrix
    # multiply, forward instructions, stored diffs) add about 80 KB; the other data files of site/data are 37 to 465 KB
    assert size < 200_000, f"arm64.json is {size} bytes"
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "/actions/runs/" not in text, "the page may not link workflow runs (scripts/check_site.py)"
    assert not re.search(r'SAMPLE|"sample"|fixture', text), "the test fixture's notice text may not reach a data file"
    assert "NaN" not in text and "Infinity" not in text
    for r in arm()["runs"]:
        assert r["workflow_run_url"] is None, "run addresses are dropped from site/data by dump()"


def tree(root):
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(dp, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root).replace("\\", "/")] = hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()
    return out


# the builder runs in its own interpreter: it imports corpus/combine.py as `combine`, which collides with harness/combine.py
# in a process (scripts/check.py's, a pytest session) that has already imported the harness one
BUILD = """
import importlib.util, sys
script, out, arm = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("build_site_data_copy", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if arm != "arm":
    mod.ARM_POOLED = "results/does-not-exist/pooled.json"
mod.build(out)
"""


def build_into(out, with_arm):
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "-I", "-c", BUILD, os.path.join(REPO, "scripts", "build_site_data.py"), out,
                        "arm" if with_arm else "no-arm"], capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stderr[-2000:]


def test_adding_the_arm_column_changes_no_other_file():
    with tempfile.TemporaryDirectory() as with_arm, tempfile.TemporaryDirectory() as without:
        build_into(with_arm, True)
        build_into(without, False)
        a, b = tree(with_arm), tree(without)
        assert "arm64.json" in a and "arm64.json" not in b
        assert sorted(set(a) - set(b)) == ["arm64.json"], "the Arm column added files other than arm64.json"
        assert not set(b) - set(a)
        changed = sorted(k for k in b if a[k] != b[k])
        assert changed == ["index.json"], f"x86-64 files changed because of the Arm column: {changed}"
        ia = json.load(open(os.path.join(with_arm, "index.json"), encoding="utf-8"))
        ib = json.load(open(os.path.join(without, "index.json"), encoding="utf-8"))
        assert ia["sections"].pop("arm64") == "data/arm64.json"
        assert ia == ib, "index.json differs by more than its sections.arm64 entry"
        # the committed copy is this build, byte for byte (so the x86-64 numbers the page prints are the ones without the Arm column)
        committed = tree(SITE_DATA)
        assert committed == a, f"site/data/ differs from a fresh build: {sorted(k for k in set(a) | set(committed) if a.get(k) != committed.get(k))[:5]}"


# ---------------------------------------------------------------- scripts/check.py covers the Arm folders

def check_module():
    return _load_module(os.path.join(REPO, "scripts", "check.py"), "arm_test_check")


def test_check_py_goes_through_the_arm_pool_the_run_pools_and_every_job():
    chk = check_module()
    pooled_files = [os.path.relpath(p, REPO).replace("\\", "/") for p in chk.pooled_files()]
    assert ARM_POOLED in pooled_files
    runs = sorted(glob.glob(os.path.join(REPO, "results", "s8-arm-run-*")))
    assert len(runs) == len(pooled()["runs"])
    for r in runs:
        assert os.path.relpath(os.path.join(r, "pooled.json"), REPO).replace("\\", "/") in pooled_files
    results = {os.path.normpath(p) for p in chk.results_files()}
    jobs = {os.path.normpath(os.path.join(d, "results.json")) for d in job_dirs()}
    assert jobs <= results and len(jobs) == arm()["jobs"]


def scratch_results(tmp):
    """A copy of the pool listing with empty job files: check_pool_complete() reads the listing and the folder names only."""
    base = os.path.join(tmp, "results")
    os.makedirs(os.path.join(base, "s8-arm-pooled"))
    shutil.copyfile(os.path.join(REPO, *ARM_POOLED.split("/")), os.path.join(base, "s8-arm-pooled", "pooled.json"))
    for i in pooled()["inputs"]:
        job = os.path.normpath(os.path.join(base, "s8-arm-pooled", i["path"]))
        os.makedirs(os.path.dirname(job), exist_ok=True)
        open(job, "w").close()
    return base


def run_complete(base):
    chk = check_module()
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        ok = chk.check_pool_complete(base)
    return ok, out.getvalue()


def edit_pool(base, fn):
    path = os.path.join(base, "s8-arm-pooled", "pooled.json")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    fn(doc)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f)


def test_pool_complete_accepts_the_arm_pool_without_any_x86_input():
    with tempfile.TemporaryDirectory() as tmp:
        base = scratch_results(tmp)
        assert not os.path.exists(os.path.join(base, "s4-pooled"))
        ok, out = run_complete(base)
        assert ok, out
        assert "results/s8-arm-pooled/pooled.json pools all 30 jobs of the s8-arm-run folders once each" in out, out


def test_pool_complete_fails_when_a_job_is_dropped_from_the_pool_file():
    with tempfile.TemporaryDirectory() as tmp:
        base = scratch_results(tmp)
        edit_pool(base, lambda d: d["inputs"].pop())
        ok, out = run_complete(base)
        assert not ok and "is on disk but not pooled" in out, out


def test_pool_complete_fails_on_a_stray_job_folder():
    with tempfile.TemporaryDirectory() as tmp:
        base = scratch_results(tmp)
        stray = os.path.join(base, "s8-arm-run-38905055834", "results-neoverse-n2-j99")
        os.makedirs(stray)
        open(os.path.join(stray, "results.json"), "w").close()
        ok, out = run_complete(base)
        assert not ok and "results-neoverse-n2-j99/results.json is on disk but not pooled".replace("/", os.sep) in out.replace("\\", os.sep), out


def test_pool_complete_fails_on_a_job_listed_twice_or_missing_from_disk():
    with tempfile.TemporaryDirectory() as tmp:
        base = scratch_results(tmp)
        edit_pool(base, lambda d: d["inputs"].append(dict(d["inputs"][0])))
        ok, out = run_complete(base)
        assert not ok and "a job is listed twice" in out, out
    with tempfile.TemporaryDirectory() as tmp:
        base = scratch_results(tmp)
        edit_pool(base, lambda d: d["inputs"].append({"path": "../s8-arm-run-38905055834/results-neoverse-n2-j77/results.json",
                                                      "run_id": "38905055834", "cpu_model": "Neoverse-N2"}))
        ok, out = run_complete(base)
        assert not ok and "is pooled but is not in an s8-arm-run folder" in out, out


def test_pool_complete_leaves_the_x86_messages_alone():
    """The s6 and s7 pools are checked as before: with the real results/ folder the three lines are ok."""
    ok, out = run_complete(os.path.join(REPO, "results"))
    assert ok, out
    assert "results/s7-pooled/pooled.json pools all" in out and "including the 30 of results/s4-pooled and the 75 of results/s6-pooled" in out, out
    assert "results/s8-arm-pooled/pooled.json pools all 30 jobs" in out, out
