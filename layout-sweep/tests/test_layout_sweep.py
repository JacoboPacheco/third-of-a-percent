import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SWEEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(SWEEP), "harness"))
sys.path.insert(0, SWEEP)
sys.path.insert(0, HERE)

import analyze as an  # noqa: E402
import lsfixture as fx  # noqa: E402

CRIT, SHA = an.load_criteria()


def jobs(n, kernels, **kw):
    return [(f"job{j}/results.json", fx.make_job(j, kernels, **kw)) for j in range(1, n + 1)]


def cell(block, cid):
    return next(c for c in block["cells"] if c["cell_id"] == cid)


def test_criteria_file_is_consistent_with_the_plan():
    r, d = CRIT["rules"], CRIT["design"]
    m = CRIT["modes"]
    assert (m["fine"]["placements"], m["fine"]["step"], m["coarse"]["placements"], m["coarse"]["step"]) == (16, 4, 4, 16)
    assert m["coarse"]["robust_min_pass"] == 4 and m["coarse"]["dependent_max_pass"] == 1
    assert d["reps_per_side"] == 20 and d["kernels"] == ["k01_sum_fwd", "k02_add_fwd", "k03_stencil", "k04_rev"]
    assert (r["aa_half_width_max_pct"], r["forward_point_max_ratio"], r["lost_ci_lo_min_ratio"]) == (2.0, 1.02, 1.5)
    assert m["fine"]["distinct_start_mod64_required"] == 16 and m["coarse"]["distinct_start_mod64_required"] == 4


def test_probe_ok():
    assert an.probe_ok([(0, 100, 150), (4, 104, 154), (12, 112, 162)])
    assert not an.probe_ok([(0, 100, 150), (4, 104, 150)])      # the loop stayed (16-byte loop alignment)
    assert not an.probe_ok([(0, 100, 150), (4, 112, 166)])      # function alignment swallowed the pad
    assert not an.probe_ok([(0, 100, 150)])


def test_mechanism_verified_and_broken():
    job = fx.make_job(1, {"k02_add_fwd": fx.FLAT})
    pl = job["builds"]["k02_add_fwd"]["placements"]
    assert an.check_mechanism(pl, an.mode_cfg(CRIT, "fine")) == []
    bad = fx.make_job(1, {"k02_add_fwd": fx.FLAT}, break_mech=True)["builds"]["k02_add_fwd"]["placements"]
    pr = an.check_mechanism(bad, an.mode_cfg(CRIT, "fine"))
    assert pr and "p07" in pr[0]
    del pl["p03"]
    assert "missing" in an.check_mechanism(pl, an.mode_cfg(CRIT, "fine"))[0]


def test_flat_forward_is_robust_and_lost_holds():
    a = an.analyse(jobs(4, {"k02_add_fwd": fx.FLAT, "k04_rev": fx.LOST}), CRIT, SHA)
    b = a["cpus"][0]
    assert b["problems"] == []
    c = cell(b, "k02_add_fwd.L1")
    assert c["class"] == "kept" and c["verdict"] == "ROBUST" and c["n_pass"] == 16 and c["n_cost"] == 0
    assert 0.98 < c["ratio_min"] <= c["ratio_median"] <= c["ratio_max"] < 1.02
    assert set(c["refs"]) == {"ref", "a64"}
    l = cell(b, "k04_rev.L1")
    assert l["class"] == "lost" and l["verdict"] == "HOLDS" and l["n_hold"] == 16
    assert b["forward_claim"] == "ROBUST" and b["lost_control"] == "HOLDS"
    assert "ROBUST" in b["line"]


def test_placement_dependent_forward_loop():
    a = an.analyse(jobs(4, {"k02_add_fwd": fx.BAD_HALF, "k04_rev": fx.LOST}), CRIT, SHA)
    b = a["cpus"][0]
    c = cell(b, "k02_add_fwd.L1")
    assert c["n_pass"] == 8 and c["n_cost"] == 8 and c["verdict"] == "MIXED"
    assert c["ratio_min"] < 1.02 < 1.5 < c["ratio_max"]
    assert c["median_by_window"]["fast_extra_window_only"]["n"] == 8
    assert c["median_by_window"]["fast_extra_window_only"]["median"] > 1.5
    assert b["forward_claim"] == "MIXED"
    dep = {"vec": (True, True), "ratio": lambda p: 1.6 if fx.idx(p) < 12 and p[0] == "p" else 1.0}
    b = an.analyse(jobs(4, {"k02_add_fwd": dep, "k04_rev": fx.LOST}), CRIT, SHA)["cpus"][0]
    assert cell(b, "k02_add_fwd.L1")["n_pass"] == 4 and b["forward_claim"] == "PLACEMENT_DEPENDENT"


def test_inconclusive_cases():
    k = {"k02_add_fwd": fx.FLAT, "k04_rev": fx.LOST}
    assert an.analyse(jobs(2, k), CRIT, SHA)["cpus"][0]["forward_claim"] == "INCONCLUSIVE"          # too few jobs
    noisy = an.analyse(jobs(4, k, aa_sd=0.2), CRIT, SHA)["cpus"][0]
    assert noisy["forward_claim"] == "INCONCLUSIVE" and "A/A" in " ".join(cell(noisy, "k02_add_fwd.L1")["inconclusive"])
    bad = an.analyse(jobs(4, k, checksum_ok=False), CRIT, SHA)["cpus"][0]
    assert bad["forward_claim"] == "INCONCLUSIVE"
    broken = an.analyse(jobs(4, k, break_mech=True), CRIT, SHA)["cpus"][0]
    assert broken["forward_claim"] == "INCONCLUSIVE" and any("mechanism" in p for p in broken["problems"])
    only_lost = an.analyse(jobs(4, {"k04_rev": fx.LOST}), CRIT, SHA)["cpus"][0]
    assert only_lost["forward_claim"] == "INCONCLUSIVE"                                              # no negative control
    ents = jobs(4, k)
    ents[0][1]["builds"]["k02_add_fwd"]["placements"]["p02"]["none"]["sha256"] = "other"
    assert any("sha256" in p for p in an.analyse(ents, CRIT, SHA)["cpus"][0]["problems"])
    ents = jobs(4, k)
    del ents[0][1]["cells"][0]["placements"]["p05"]
    assert an.analyse(ents, CRIT, SHA)["cpus"][0]["forward_claim"] == "INCONCLUSIVE"                 # a placement missing


def test_cpu_models_are_separate():
    ents = jobs(3, {"k02_add_fwd": fx.FLAT, "k04_rev": fx.LOST}, cpu="CPU A") + \
        [(f"b{j}/results.json", fx.make_job(j, {"k02_add_fwd": fx.BAD_HALF, "k04_rev": fx.LOST}, cpu="CPU B"))
         for j in range(1, 4)]
    a = an.analyse(ents, CRIT, SHA)
    assert [b["cpu_model"] for b in a["cpus"]] == ["CPU A", "CPU B"]
    assert [b["forward_claim"] for b in a["cpus"]] == ["ROBUST", "MIXED"]


def test_analysis_is_deterministic_and_json_round_trips():
    ents = jobs(3, {"k02_add_fwd": fx.FLAT, "k04_rev": fx.LOST})
    a1 = an.analyse(ents, CRIT, SHA)
    a2 = an.analyse(ents, CRIT, SHA)
    assert json.loads(json.dumps(a1)) == json.loads(json.dumps(a2)) == json.loads(json.dumps(a1, sort_keys=True))
    text = an.report(a1)
    assert "k02_add_fwd.L1" in text and "ROBUST" in text


def test_verify_job_catches_tampering():
    crit = CRIT
    job = fx.make_job(1, {"k02_add_fwd": fx.FLAT}, ci=True)
    job["criteria_sha256"] = SHA
    # fixture CIs were made with 200 resamples; verify_job demands the criteria's 2000, so they differ
    assert an.verify_job(job, crit, SHA)
    job["criteria_sha256"] = "wrong"
    assert any("criteria_sha256" in p for p in an.verify_job(job, crit, SHA))
    small = dict(crit, design=dict(crit["design"], per_job_resamples=200))
    job["criteria_sha256"] = SHA
    assert an.verify_job(job, small, SHA) == []
    job["cells"][0]["placements"]["p03"]["ratio"] += 0.01
    assert any("ratio" in p for p in an.verify_job(job, small, SHA))


def test_load_entries_dir_and_out():
    import tempfile
    d = tempfile.mkdtemp()
    for j in (1, 2, 3):
        os.makedirs(os.path.join(d, f"res-j{j}"))
        with open(os.path.join(d, f"res-j{j}", "results.json"), "w") as f:
            json.dump(fx.make_job(j, {"k02_add_fwd": fx.FLAT, "k04_rev": fx.LOST}), f)
    out = os.path.join(d, "analysis.json")
    assert an.main([d, "--out", out]) == 0
    doc = json.load(open(out))
    assert doc["kind"] == "layout-sweep-analysis" and len(doc["inputs"]) == 3
    assert doc["inputs"][0]["path"] == "res-j1/results.json"


def test_sweep_command_and_inspect_with_a_fake_objdump():
    import sweep
    cmd = sweep.sweep_cmd("k02_add_fwd", "fast", 12, ["-falign-functions=1", "-falign-loops=1"], "/o/x")
    assert cmd[-1] == "layout-sweep/wrap.cpp" and "-DPAD_BYTES=12" in cmd
    assert '-DKERNEL_SRC="kernels/k02_add_fwd.cpp"' in cmd and "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST" in cmd
    assert cmd.index("-falign-loops=1") < cmd.index("-o")
    dump = "\n".join([
        "0000000000401034 <_Z15kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_>:",
        "  401034:\tpush   %rbp",
        "  401040:\tmovdqu (%rax),%xmm0",
        "  401050:\tpaddd  %xmm1,%xmm0",
        "  401060:\tjne    401040 <_Z15kern_k02_add_fwdRSt6vectorIiSaIiEERKS1_S4_+0xc>",
        "  401062:\tret",
        "",
        "0000000000401070 <main>:",
        "  401070:\tret"])

    class R:
        stdout = dump
    old_sh, old_sha = sweep.hr.sh, sweep.hr.sha256
    sweep.hr.sh = lambda c, **k: R()
    sweep.hr.sha256 = lambda p: "abc"
    try:
        info, lines = sweep.inspect("b", "k02_add_fwd", "", "kernels/k02_add_fwd.cpp", 6)
    finally:
        sweep.hr.sh, sweep.hr.sha256 = old_sh, old_sha
    assert info["fn_addr"] == 0x401034 and info["hot"]["start"] == 0x401040 and info["hot"]["bytes"] == 0x22
    assert info["hot"]["start_mod64"] == 0 and info["hot"]["simd"] and info["vectorized"] is None
    assert len(lines) == 6


def test_coarse_mode_four_placements():
    k = {"k02_add_fwd": fx.FLAT, "k04_rev": fx.LOST}
    b = an.analyse(jobs(4, k, mode="coarse"), CRIT, SHA)["cpus"][0]
    assert b["mode"] == "coarse" and b["placements"] == 4 and b["problems"] == []
    c = cell(b, "k02_add_fwd.L1")
    assert c["n_placements"] == 4 and c["n_pass"] == 4 and c["verdict"] == "ROBUST"
    assert list(c["placements"]) == ["p00", "p01", "p02", "p03"]
    assert b["forward_claim"] == "ROBUST" and b["lost_control"] == "HOLDS" and "4 code placements" in b["line"]
    # 3 of 4 passing is not ROBUST in coarse mode; 1 of 4 is PLACEMENT_DEPENDENT
    three = {"vec": (True, True), "ratio": lambda p: 1.6 if p == "p02" else 1.0}
    assert an.analyse(jobs(4, {"k02_add_fwd": three, "k04_rev": fx.LOST}, mode="coarse"), CRIT, SHA)["cpus"][0]["forward_claim"] == "MIXED"
    one = {"vec": (True, True), "ratio": lambda p: 1.0 if p == "p01" else 1.6}
    assert an.analyse(jobs(4, {"k02_add_fwd": one, "k04_rev": fx.LOST}, mode="coarse"), CRIT, SHA)["cpus"][0]["forward_claim"] == "PLACEMENT_DEPENDENT"
    bad = fx.make_job(1, {"k02_add_fwd": fx.FLAT}, mode="coarse")["builds"]["k02_add_fwd"]["placements"]
    assert an.check_mechanism(bad, an.mode_cfg(CRIT, "coarse")) == []
    bad["p02"]["fast"]["hot"]["start"] += 16          # loop no longer moves with the pad
    assert an.check_mechanism(bad, an.mode_cfg(CRIT, "coarse"))


def test_mixed_modes_are_flagged():
    k = {"k02_add_fwd": fx.FLAT, "k04_rev": fx.LOST}
    ents = jobs(3, k) + [("x/results.json", fx.make_job(9, k, mode="coarse"))]
    assert any("different placement modes" in p for p in an.analyse(ents, CRIT, SHA)["cpus"][0]["problems"])


def test_probe_ok_coarse_steps():
    assert an.probe_ok([(0, 100, 150), (16, 116, 166), (32, 132, 182), (48, 148, 198)])
    assert not an.probe_ok([(0, 100, 160), (16, 116, 160)])


def test_pooling_across_runs_dedupes_and_skips_nested_analysis():
    import tempfile
    d = tempfile.mkdtemp()
    k = {"k02_add_fwd": fx.FLAT, "k04_rev": fx.LOST}
    for run, js in (("111", (1, 2)), ("222", (1, 2))):
        for j in js:
            doc = fx.make_job(j, k, run_id=run)
            for sub in (f"{run}/layout-sweep-cpu-j{j}", f"{run}/layout-sweep-analysis/layout-sweep-cpu-j{j}"):
                os.makedirs(os.path.join(d, sub))
                json.dump(doc, open(os.path.join(d, sub, "results.json"), "w"))
    # an exact duplicate of run 111 job 1 in another folder counts once
    os.makedirs(os.path.join(d, "copy"))
    json.dump(fx.make_job(1, k, run_id="111"), open(os.path.join(d, "copy", "results.json"), "w"))
    assert len(an.find_results([d])) == 4
    os.makedirs(os.path.join(d, "pooled"))
    out = os.path.join(d, "pooled", "analysis.json")
    assert an.main([d, "--out", out]) == 0
    doc = json.load(open(out))
    assert len(doc["inputs"]) == 4 and all(len(i["sha256"]) == 64 for i in doc["inputs"])
    assert doc["inputs"][0]["path"].startswith("../")
    assert doc["cpus"][0]["jobs"] == 4 and doc["cpus"][0]["runs"] == ["111", "222"]
