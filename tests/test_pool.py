"""harness/pool.py (criteria-v3): the generator, the two-level bootstrap, the pooled per-CPU verdict,
the placement-sensitive rule, stability across runs and the pooled.json schema, on made-up jobs."""
import json
import os
import random
import tempfile

import pool
import pool_check
import schema

CRIT, SHA = pool.criteria_and_sha()
CPU = "AMD EPYC 7763 64-Core Processor"
SHA_A, SHA_B, SHA_C, SHA_D = ("a" * 64, "b" * 64, "c" * 64, "d" * 64)
# ratio FAST/NONE per cell: (as compiled, aligned)
KERNELS = {"k01_sum_fwd": ("kept", 1.000, 1.000), "k02_add_fwd": ("kept", 1.005, 1.000),
           "k04_rev": ("lost", 5.5, 5.6), "k05_stride2": ("lost", 2.9, 2.9), "k06_gather": ("off", 1.6, 1.7)}


def loop(start, nbytes, simd=True):
    s = int(start, 16)
    win = (s + nbytes - 1) // 64 - s // 64 + 1
    mn = (nbytes + 63) // 64
    return {"start": start, "end": hex(s + nbytes), "bytes": nbytes, "start_mod64": s % 64, "crosses64": win > 1,
            "windows64": win, "min_windows64": mn, "extra_window": win > mn, "insns": 8, "simd": simd,
            "innermost": True}


def samples(rng, level, n=40, noise=0.003):
    return [level * (1 + rng.gauss(0, noise)) for _ in range(n)]


def job(rng, run_id, cpu=CPU, host=1.0, overrides=None, n=40):
    overrides = overrides or {}
    cells = []
    for k, (klass, rc, ra) in KERNELS.items():
        rc, ra = overrides.get(k, (rc, ra))
        vn = klass != "off"
        vf = klass == "kept"
        same_layout = k == "k01_sum_fwd"
        loops = {"none": [loop("0x1260", 52)], "fast": [loop("0x1260" if same_layout else "0x12b0", 52 if same_layout else 31)],
                 "novec": [loop("0x1260", 72, False)], "none_a64": [loop("0x1280", 52)], "fast_a64": [loop("0x1300", 31)]}
        for size in ("L1", "L2"):
            base = 1e6 * host
            cells.append({
                "cell_id": f"{k}.{size}", "kernel": k, "size_class": size, "checksum_match": True,
                "none_sha256": SHA_A, "fast_sha256": SHA_B,
                "vectorized_none": {"vectorized": vn, "width": 4 if vn else None},
                "vectorized_fast": {"vectorized": vf, "width": 4 if vf else None},
                "none_ns": samples(rng, base, n), "fast_ns": samples(rng, base * rc, n),
                "instr": {"none": 100, "fast": 110, "ratio": 1.1},
                "aligned": {"none_sha256": SHA_C, "fast_sha256": SHA_D, "checksum_match": True,
                            "vectorized_none": {"vectorized": vn, "width": 4 if vn else None},
                            "vectorized_fast": {"vectorized": vf, "width": 4 if vf else None},
                            "none_ns": samples(rng, base, n), "fast_ns": samples(rng, base * ra, n),
                            "instr": {"none": 100, "fast": 110, "ratio": 1.1}},
                "loops": loops})
    return {"run": {"id": run_id, "runner": {"cpu_model": cpu}, "criteria_file": pool.V3_FILE},
            "cells": cells,
            "controls": {"aa": {"a_ns": samples(rng, 1e6 * host, n), "b_ns": samples(rng, 1e6 * host, n)},
                         "layout_aa": [{"id": f"k02_add_fwd.{s}", "a_ns": samples(rng, 1e6, n), "b_ns": samples(rng, 1e6, n)}
                                       for s in ("L1", "L2")],
                         "positive": [{"cell_id": "k02_add_fwd.L1", "none_ns": samples(rng, 1e6, n),
                                       "novec_ns": samples(rng, 2.5e6, n)}]}}


def entries(jobs):
    return [(f"r{d['run']['id']}/j{i}/results.json", d) for i, d in enumerate(jobs)]


def test_splitmix64_reference_vector():
    # the published first outputs of splitmix64 from state 0
    out = pool.splitmix64(0, 2)
    assert int(out[0]) == 0xE220A8397B1DCDAF
    assert int(out[1]) == 0x6E789E6AA1B965F4


def test_pooled_ratio_is_geometric_mean_and_reproducible():
    rng = random.Random(1)
    pairs = [(samples(rng, 1.0), samples(rng, r)) for r in (1.10, 1.20, 1.15)]
    s1 = pool.pair_stat(CPU, "x", pairs)
    s2 = pool.pair_stat(CPU, "x", pairs)
    assert s1 == s2
    import math, statistics
    want = math.exp(sum(math.log(statistics.median(b) / statistics.median(a)) for a, b in pairs) / 3)
    assert abs(s1["ratio"] - want) < 1e-12
    assert s1["ci95"][0] <= s1["ratio"] <= s1["ci95"][1]
    assert s1["jobs"] == 3 and len(s1["per_job"]) == 3


def test_between_job_spread_widens_the_interval():
    rng = random.Random(2)
    tight = [(samples(rng, 1.0), samples(rng, 1.10)) for _ in range(6)]
    spread = [(samples(rng, 1.0), samples(rng, r)) for r in (1.02, 1.18, 1.06, 1.14, 1.10, 1.10)]
    a = pool.pair_stat(CPU, "t", tight)
    b = pool.pair_stat(CPU, "s", spread)
    assert b["half_width_pct"] > 3 * a["half_width_pct"]
    assert b["between_job_sd_pct"] > 3 * a["between_job_sd_pct"]


def test_map_on_clean_pooled_data_and_no_single_page_form():
    rng = random.Random(3)
    jobs = [job(rng, rid, host=1 + 0.05 * i) for i, rid in enumerate(["1", "1", "1", "2", "2", "2"])]
    doc = pool.pool(entries(jobs), CRIT, SHA)
    schema.validate_pooled(doc)
    b = doc["cpus"][0]
    assert b["verdict"]["form"] == "map", b["verdict"]["line"]
    assert b["jobs"] == 6 and b["runs"] == ["1", "2"]
    assert b["stability"] == "stable"
    assert doc["page"]["form"] is None
    assert "MAP on " + CPU in doc["page"]["line"]
    assert b["reproduction"]["checked"] > 0


def test_too_few_jobs_is_inconclusive_and_stability_not_assessable():
    rng = random.Random(4)
    doc = pool.pool(entries([job(rng, "1"), job(rng, "1")]), CRIT, SHA)
    b = doc["cpus"][0]
    assert b["verdict"]["form"] == "inconclusive"
    assert "too few jobs" in b["verdict"]["why"]
    assert b["stability"] == "not assessable"


def test_no_job_is_excluded_on_its_own_aa():
    rng = random.Random(5)
    jobs = [job(rng, "1") for _ in range(4)]
    noisy = jobs[0]["controls"]["aa"]
    noisy["b_ns"] = [x * (1 + rng.gauss(0, 0.08)) for x in noisy["b_ns"]]
    doc = pool.pool(entries(jobs), CRIT, SHA)
    assert doc["cpus"][0]["jobs"] == 4
    assert doc["cpus"][0]["aa"]["jobs"] == 4


def test_placement_sensitive_needs_both_parts():
    rng = random.Random(6)
    # k02: compiled 1.08, aligned 1.00 -> statistically different, and NONE/FAST hot loops differ -> sensitive
    # k01: compiled 1.08, aligned 1.00 too, but NONE and FAST hot loops sit identically -> not sensitive
    ov = {"k02_add_fwd": (1.08, 1.00), "k01_sum_fwd": (1.08, 1.00)}
    jobs = [job(rng, "1", overrides=ov) for _ in range(4)]
    doc = pool.pool(entries(jobs), CRIT, SHA)
    cells = {c["cell_id"]: c for c in doc["cpus"][0]["cells"]}
    assert cells["k02_add_fwd.L1"]["placement"]["sensitive"] is True
    assert cells["k01_sum_fwd.L1"]["placement"]["statistical"] is True
    assert cells["k01_sum_fwd.L1"]["placement"]["mechanical"] is False
    assert cells["k01_sum_fwd.L1"]["placement"]["sensitive"] is False
    ids = [p["cell_id"] for p in doc["cpus"][0]["verdict"]["placement_sensitive"]]
    assert "k02_add_fwd.L1" in ids and "k01_sum_fwd.L1" not in ids


def test_unstable_when_one_run_differs():
    rng = random.Random(7)
    bad = {"k02_add_fwd": (1.10, 1.10)}  # the forward rule fails in run 2 only
    jobs = [job(rng, "1") for _ in range(3)] + [job(rng, "2", overrides=bad) for _ in range(3)]
    doc = pool.pool(entries(jobs), CRIT, SHA)
    b = doc["cpus"][0]
    forms = [r["form"] for r in b["per_run"]]
    assert forms[0] == "map" and forms[1] == "inconclusive"
    assert b["stability"] == "unstable"
    assert "NOT the same in every run" in doc["page"]["line"]


def test_build_control_catches_differing_binaries():
    rng = random.Random(8)
    jobs = [job(rng, "1") for _ in range(3)]
    jobs[1]["cells"][0]["fast_sha256"] = "e" * 64
    doc = pool.pool(entries(jobs), CRIT, SHA)
    assert "build control" in doc["cpus"][0]["verdict"]["why"]


def test_independent_check_agrees_on_a_written_file():
    rng = random.Random(9)
    jobs = [job(rng, "1", host=1 + 0.03 * i, n=12) for i in range(3)]
    with tempfile.TemporaryDirectory() as d:
        paths = []
        for i, j in enumerate(jobs):
            os.makedirs(os.path.join(d, f"j{i}"))
            p = os.path.join(d, f"j{i}", "results.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(j, f)
            paths.append(p)
        out = os.path.join(d, "pooled.json")
        doc = pool.pool(pool.load_inputs(paths, d), CRIT, SHA)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        n, problems = pool_check.check(out)
        assert n > 0 and problems == [], problems
        # a pooled interval that ignores the between-job level is caught
        doc["cpus"][0]["cells"][0]["as_compiled"]["ci95"] = [doc["cpus"][0]["cells"][0]["as_compiled"]["ratio"] - 1e-6,
                                                            doc["cpus"][0]["cells"][0]["as_compiled"]["ratio"] + 1e-6]
        with open(out, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        # deliberately tampered (zero-width interval): pool_check must reject it; its FAIL line is
        # captured here so the test run does not print a FAIL that looks like a real pooled file failing
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            n, problems = pool_check.check(out)
        assert problems


def write_pooled(d, jobs):
    """Each job under d/j<i>/results.json, pooled by pool.py; returns (path of pooled.json, the pooled document)."""
    paths = []
    for i, j in enumerate(jobs):
        os.makedirs(os.path.join(d, f"j{i}"))
        p = os.path.join(d, f"j{i}", "results.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(j, f)
        paths.append(p)
    out = os.path.join(d, "pooled.json")
    doc = pool.pool(pool.load_inputs(paths, d), CRIT, SHA)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f)
    return out, doc


def quiet_check(path):
    """pool_check.check(path, skipped) with its output captured: (n, problems, skipped, printed text)."""
    import contextlib
    import io
    skipped, buf = [], io.StringIO()
    with contextlib.redirect_stdout(buf):
        n, problems = pool_check.check(path, skipped)
    return n, problems, skipped, buf.getvalue()


def test_independent_check_skips_cpu_models_below_the_minimum_job_count():
    """A model with fewer jobs than v3.pooling.minimum_jobs is listed and never sampled; a model with exactly the
    minimum is still checked. (The first version of this rule: the lumpy tail of one job's repetitions made the check
    disagree with the stored interval of a one-job model by more than its tolerance, in a real run.)"""
    minimum = CRIT["v3"]["pooling"]["minimum_jobs"]
    assert minimum == 3
    rng = random.Random(10)
    big = [job(rng, "1", host=1 + 0.03 * i, n=12) for i in range(minimum)]
    one = [job(rng, "1", cpu="A 1-job CPU", n=12)]
    two = [job(rng, "1", cpu="B 2-job CPU", n=12) for _ in range(minimum - 1)]
    with tempfile.TemporaryDirectory() as d:
        alone_dir = os.path.join(d, "alone")
        os.makedirs(alone_dir)
        alone_path, _ = write_pooled(alone_dir, big)
        n_alone, problems_alone, skipped_alone, _ = quiet_check(alone_path)
        assert n_alone > 0 and problems_alone == [] and skipped_alone == []

        mixed_dir = os.path.join(d, "mixed")
        os.makedirs(mixed_dir)
        path, doc = write_pooled(mixed_dir, one + big + two)
        assert pool_check.minimum_jobs(doc) == minimum
        assert [b["jobs"] for b in doc["cpus"]] == [1, minimum, minimum - 1]  # the 1-job model sorts before the others
        n, problems, skipped, text = quiet_check(path)
        assert problems == [], problems
        assert n == n_alone, "the skipped models added or removed sampled statistics"
        assert skipped == ["A 1-job CPU", "B 2-job CPU"]
        for name in skipped:
            assert any(ln.lstrip().startswith("skip") and name in ln for ln in text.splitlines()), text
            assert not any(name in ln and ln.lstrip().startswith(("ok", "FAIL")) for ln in text.splitlines()), text
        assert any(ln.lstrip().startswith("ok") and "AMD EPYC 7763" in ln for ln in text.splitlines()), text

        # nothing the check does not sample can fail it: a zero-width interval on every statistic of the small models
        for b in doc["cpus"]:
            if b["jobs"] < minimum:
                for st in [b["aa"]] + [c[col] for c in b["cells"] for col in ("as_compiled", "aligned")]:
                    st["ci95"] = [st["ratio"] - 1e-6, st["ratio"] + 1e-6]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        n2, problems2, skipped2, _ = quiet_check(path)
        assert problems2 == [] and n2 == n and len(skipped2) == 2

        # ... but the same tampering on the model that has the minimum is still caught
        big_block = next(b for b in doc["cpus"] if b["jobs"] == minimum)
        c0 = big_block["cells"][0]["as_compiled"]
        c0["ci95"] = [c0["ratio"] - 1e-6, c0["ratio"] + 1e-6]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        n3, problems3, skipped3, text3 = quiet_check(path)
        assert problems3 and len(skipped3) == 2 and "FAIL" in text3, text3


def test_the_sample_holds_the_three_cells_the_conclusions_rest_on():
    """k03_stencil.L2 decides the word of the Xeon 6973P-C, k02_add_fwd.L2 the word of the Arm core, k05_stride2.L1 is the smallest lost-loop cost."""
    for cell in ("k03_stencil.L2", "k02_add_fwd.L2", "k05_stride2.L1"):
        assert cell in pool_check.SAMPLE_CELLS, f"{cell} is not sampled"
    assert len(set(pool_check.SAMPLE_CELLS)) == len(pool_check.SAMPLE_CELLS)
    rng = random.Random(12)
    jobs = [job(rng, "1", host=1 + 0.03 * i, n=12) for i in range(3)]
    with tempfile.TemporaryDirectory() as d:
        path, _ = write_pooled(d, jobs)
        n, problems, skipped, text = quiet_check(path)
    assert problems == [] and skipped == [], problems
    for cell in ("k02_add_fwd.L2", "k05_stride2.L1"):    # the made-up jobs have no stencil
        for column in ("as compiled", "aligned"):
            assert any(f"{cell} {column}" in ln and ln.lstrip().startswith("ok") for ln in text.splitlines()), f"{cell} {column} is not listed:\n{text}"


def test_the_tolerance_and_the_resampling_of_the_check_are_as_before():
    """The check was widened by cells and a printed margin only: a looser tolerance or fewer resamples would make it agree with more."""
    assert (pool_check.B, pool_check.BOUND_TOL_WIDTH, pool_check.BOUND_TOL_RATIO, pool_check.WIDTH_FACTOR) == (4000, 0.15, 0.0005, 1.5)
    assert pool_check.PLACEMENT_CELLS == ("k02_add_fwd.L1", "k03_stencil.L1")


def test_the_margin_text_says_under_or_over_and_how_far():
    assert pool_check.margin_text(1.0211, 1.02) == "upper end 0.0011 over 1.02"
    assert pool_check.margin_text(1.0184, 1.02) == "upper end 0.0016 under 1.02"
    assert pool_check.margin_text(1.02, 1.02) == "upper end 0.0000 under 1.02"
    assert pool_check.margin_text(6.52, 1.02) == "upper end 5.5000 over 1.02"


def test_the_margin_to_the_forward_limit_is_printed_for_cells_only_and_decides_nothing():
    """Beside the recomputed upper end of every cell statistic (both columns) and of nothing else; a cell far over the limit (a lost loop) still passes."""
    import re
    rng = random.Random(11)
    jobs = [job(rng, "1", host=1 + 0.03 * i, n=12) for i in range(3)]
    with tempfile.TemporaryDirectory() as d:
        path, doc = write_pooled(d, jobs)
        n, problems, skipped, text = quiet_check(path)
    limit = pool_check.forward_limit(doc)
    assert limit == 1 + CRIT["verdict"]["forward_ci_hi_floor_pct"] / 100 == 1.02
    assert problems == [], problems
    lines = [ln for ln in text.splitlines() if ln.lstrip().startswith(("ok", "FAIL"))]
    assert len(lines) == n
    seen = set()
    for ln in lines:
        m = re.search(r"independent [\d.]+ \[[\d.]+, ([\d.]+)\](?:  \(upper end ([\d.]+) (under|over) ([\d.]+)\))?", ln)
        assert m, ln
        hi = float(m.group(1))
        is_cell = "as compiled" in ln or " aligned" in ln
        assert (m.group(2) is not None) == is_cell, f"the margin is {'missing' if is_cell else 'printed'} on: {ln}"
        if not is_cell:
            assert "(upper end" not in ln, ln
            continue
        assert float(m.group(4)) == limit
        assert abs(float(m.group(2)) - abs(limit - hi)) < 1.6e-4, ln     # both numbers are printed to four decimals
        if abs(limit - hi) > 2e-4:
            assert m.group(3) == ("under" if hi < limit else "over"), ln
            seen.add(m.group(3))
    assert seen == {"under", "over"}, f"the made-up pool should show a cell under and a cell over the limit, saw {seen}"
    assert any(" aa " in ln for ln in lines) and any("layout " in ln for ln in lines)


def test_v3_criteria_keep_the_v2_thresholds():
    import verdict
    v2 = verdict.load_criteria(os.path.join(pool.REPO, "harness", "criteria-v2.json"))
    assert CRIT["verdict"] == v2["verdict"]
    assert CRIT["classes_from_remarks"] == v2["classes_from_remarks"]
    assert CRIT["v3"]["timing"]["reps_per_side"] == 40
    assert CRIT["v3"]["pooling"]["minimum_jobs"] == 3
