import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ENV), "harness"))
sys.path.insert(0, ENV)

import analyze as an  # noqa: E402
import envlib  # noqa: E402

STAT1 = "cpu  100 0 50 800 10 0 5 3 0 0\ncpu0 40 0 20 400 5 0 2 1 0 0\ncpu1 60 0 30 400 5 0 3 2 0 0\nintr 1\n"
STAT2 = "cpu  150 0 70 900 12 0 6 8 0 0\ncpu0 60 0 30 450 6 0 2 2 0 0\ncpu1 90 0 40 450 6 0 4 6 0 0\n"
CPUINFO = ("processor\t: 0\nmodel name\t: AMD EPYC 7763 64-Core Processor\ncpu MHz\t\t: 2445.426\n\n"
           "processor\t: 1\nmodel name\t: AMD EPYC 7763 64-Core Processor\ncpu MHz\t\t: 2445.500\n\n")


def test_parse_proc_stat_and_delta():
    a, b = envlib.parse_proc_stat(STAT1), envlib.parse_proc_stat(STAT2)
    assert set(a) == {"cpu", "cpu0", "cpu1"}
    assert a["cpu1"]["steal"] == 2 and a["cpu1"]["iowait"] == 5
    d = envlib.stat_delta(a["cpu1"], b["cpu1"])
    assert d["steal"] == 4 and d["total"] == (90 + 40 + 450 + 6 + 4 + 6) - (60 + 30 + 400 + 5 + 3 + 2)


def test_cpuinfo_mhz():
    assert envlib.mhz_of(CPUINFO, 1) == 2445.5
    assert envlib.mhz_of(CPUINFO, 7) is None
    assert envlib.parse_cpuinfo(CPUINFO)[0]["model name"].startswith("AMD EPYC")
    assert envlib.mhz_of("processor : 0\nmodel name : x\n", 0) is None  # no MHz line


def test_cpu_list_and_core_sharing():
    assert envlib.parse_cpu_list("0-1,3") == [0, 1, 3]
    assert envlib.parse_cpu_list("") == []
    assert envlib.shares_core(1, 0, [0, 1]) is True
    assert envlib.shares_core(1, 0, [1]) is False
    assert envlib.shares_core(1, 1, [0, 1]) is False  # same vCPU is a different finding
    assert envlib.shares_core(1, None, [0, 1]) is False


def test_cgroup_and_driver_cpu():
    assert envlib.parse_cgroup_cpu_max("max 100000")["cpus"] is None
    assert envlib.parse_cgroup_cpu_max("200000 100000")["cpus"] == 2.0
    assert envlib.parse_cgroup_cpu_max("garbage") is None
    stat = "1234 (my (odd) prog) S " + " ".join(["0"] * 35 + ["5"]) + " 0 0"
    assert envlib.driver_cpu(stat) == 5
    assert envlib.slug("AMD EPYC 7763 64-Core Processor") == "amd-epyc-7763-64-core-processor"


def sample(i, cell, side, ns, steal=0, mhz=2500.0, total=8, driver=0):
    return {"i": i, "cell": cell, "side": side, "rep": i // 2, "ns": ns, "steal": steal, "iowait": 0, "total": total,
            "steal_all": steal, "total_all": total * 4, "mhz": mhz, "scaling_cur_mhz": None, "driver_cpu": driver}


def make_doc(job, model="CPU A", n=20, steal_every=0, mhz_second_half=2500.0, fast_ratio=1.0, siblings="0-1"):
    samples, i = [], 0
    for cid in ("k02_add_fwd.L1", "k04_rev.L1"):
        for rep in range(n):
            for side in (("none", "fast") if rep % 2 == 0 else ("fast", "none")):
                steal = 1 if steal_every and i % steal_every == 0 else 0
                ns = 1000.0 * (1 + 0.001 * (i % 5)) * (fast_ratio if side == "fast" else 1.0)
                s = sample(i, cid, side, ns, steal=steal, mhz=2500.0 if i < n * 2 else mhz_second_half)
                s["rep"] = rep
                samples.append(s)
                i += 1
    return {"job": str(job), "cpu_model": model, "_path": f"j{job}/environment.json",
            "facts": {"pinned_cpu": 1, "online": "0-3", "cgroup_cpu_max": None,
                      "cpufreq": {}, "topology": {"1": {"thread_siblings_list": siblings}}},
            "cells": [{"cell_id": "x", "checksum_match": True}], "samples": samples}


def test_quiet_job_is_not_large():
    j = an.job_summary(make_doc(1))
    assert j["steal_share"] == 0 and not j["steal_large"]
    assert j["mhz"]["constant"] is True and not j["mhz"]["drift_large"]
    assert j["topology"]["shares_core_with_driver"] is True
    assert j["topology"]["driver_on_pinned_vcpu"] is False


def test_steal_above_half_percent_is_large():
    # 1 process in 10 sees 1 tick of 8: share = 1/80 = 1.25 %
    j = an.job_summary(make_doc(1, steal_every=10))
    assert abs(j["steal_share"] - 0.0125) < 1e-9 and j["steal_large"]
    assert j["processes_with_steal"] == 8


def test_frequency_drift_threshold_is_one_percent():
    just_over = an.job_summary(make_doc(1, mhz_second_half=2500 * 1.011))
    just_under = an.job_summary(make_doc(1, mhz_second_half=2500 * 1.009))
    assert just_over["mhz"]["drift_large"] and not just_under["mhz"]["drift_large"]
    assert abs(just_over["mhz"]["half_drift_pct"] - 1.1) < 1e-9
    assert just_over["mhz"]["constant"] is False


def test_no_mhz_reading_is_reported_not_crashed():
    d = make_doc(1)
    for s in d["samples"]:
        s["mhz"] = None
    j = an.job_summary(d)
    assert j["mhz"] == {"source": None} and not j["job_large"]


def test_scaling_cur_freq_preferred_when_present():
    d = make_doc(1)
    for s in d["samples"]:
        s["scaling_cur_mhz"] = 3000.0
    assert an.job_summary(d)["mhz"]["source"] == "scaling_cur_freq"


def test_no_steal_means_no_cell_moves_and_no_page_change():
    a = an.analyse([make_doc(j) for j in range(1, 4)])
    m = a["models"][0]
    assert m["cells_moved"] == [] and a["page_text_may_change"] is False
    assert all(r["excluded"] == 0 and r["moves"] is False for r in m["cells"])


def test_steal_that_biases_the_ratio_moves_a_cell():
    # FAST equals NONE in truth; steal-affected processes are 3x slower and sit on the FAST side only
    docs = []
    for j in range(1, 4):
        d = make_doc(j)
        for s in d["samples"]:
            if s["side"] == "fast" and s["rep"] % 2 == 0:
                s["steal"] = 1
                s["ns"] *= 3
        docs.append(d)
    a = an.analyse(docs)
    m = a["models"][0]
    row = next(r for r in m["cells"] if r["cell_id"] == "k02_add_fwd.L1")
    assert row["excluded"] > 0 and row["judged"] and row["moves"] is True
    assert row["class"] == "forward-fails" and row["class_wo_steal"] == "forward-passes"
    assert m["page_text_may_change"] is True and a["page_text_may_change"] is True


def test_steal_without_ratio_effect_does_not_move():
    docs = [make_doc(j, steal_every=7) for j in range(1, 4)]
    m = an.analyse(docs)["models"][0]
    assert m["jobs_steal_large"] == 3
    assert m["cells_moved"] == [] and m["page_text_may_change"] is False


def test_lost_kernel_class_uses_ci_lo_1_5():
    a = an.analyse([make_doc(j, fast_ratio=4.0) for j in range(1, 3)])
    rows = {r["cell_id"]: r for r in a["models"][0]["cells"]}
    assert rows["k04_rev.L1"]["class"] == "lost-holds"
    assert rows["k02_add_fwd.L1"]["class"] == "forward-fails"


def test_too_few_left_is_not_judged():
    d = make_doc(1)
    for s in d["samples"]:
        if s["cell"] == "k04_rev.L1" and s["rep"] < 15:
            s["steal"] = 1
    row = next(r for r in an.analyse([d])["models"][0]["cells"] if r["cell_id"] == "k04_rev.L1")
    assert row["judged"] is False and row["moves"] is None


def test_models_are_kept_apart():
    a = an.analyse([make_doc(1, model="A"), make_doc(2, model="B"), make_doc(3, model="A")])
    assert [(m["cpu_model"], m["n_jobs"]) for m in a["models"]] == [("A", 2), ("B", 1)]


def test_report_renders_and_is_deterministic():
    docs = [make_doc(j, steal_every=9) for j in range(1, 3)]
    r1, r2 = an.report(an.analyse(docs)), an.report(an.analyse(docs))
    assert r1 == r2 and "CPU A" in r1 and "Overall:" in r1
