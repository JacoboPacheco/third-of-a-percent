"""dsweep/ (the matrix-multiply d-sweep, rules in dsweep/PLAN.md): the d ladder from the cache sizes, the pooled
analysis on made-up jobs, the file schema, the sweep runner with a faked harness, the workflow, and the numbers of the
rule against the plan, the criteria and the stored Neoverse-N2 results.

No compiler, no Linux and no fixtures (scripts/check.py's built-in runner runs plain functions, and so does
`python3 tests/test_dsweep.py`, which the workflow runs before it times anything): the jobs are generated here with the
same writer the sweep uses (sweep.build_doc, make_point, builds_record), under the accounts of the plan:

    H1     E(d) = c          a fixed cost per inner call (the excess t_F - t_N does not depend on d)
    H2     E(d) = c2 * d     a cost per element
    falls  E(d) smaller at the larger d
    mixes  E(d) = c + c2 * d

and under no cost at all. The bootstrap here uses 300 resamples (the rule uses 2000); one test runs the full 2000
through the command line."""
import contextlib
import importlib.util
import io
import json
import math
import os
import random
import re
import sys
import tempfile
import traceback
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


an = _load("dsweep_analyze", os.path.join("dsweep", "analyze.py"))
sw = _load("dsweep_sweep", os.path.join("dsweep", "sweep.py"))
import pool  # noqa: E402
import remarks  # noqa: E402
import run as hr  # noqa: E402
import stats  # noqa: E402

ARM = (64 * 1024, 1024 * 1024)       # Neoverse-N2: L1d, L2
EPYC = (32 * 1024, 512 * 1024)       # EPYC 7763
INTEL = (48 * 1024, 2048 * 1024)     # a 48 KiB L1d
RES = 300
SHAS = {"none": "a" * 64, "fast": "b" * 64, "none_a64": "c" * 64, "fast_a64": "d" * 64}
EPYC_NAME = "AMD EPYC 7763 64-Core Processor"
STEP_REMARK = "vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]"


# ---------------------------------------------------------------- made-up jobs

# Scenarios that give the excess E(d) in ns per inner call directly, on the baseline t_N = 0.02 + 0.1357 d of the stored
# Neoverse-N2 data and an excess of C52 ns at d = 52 (the stored value is 3.878).
C52 = 3.88
EXCESS = {}
for _pct in (100, 75, 50, 35, 25, 10, 0):       # the fixed share of the excess at d = 52, in percent
    EXCESS[f"fixed{_pct}"] = lambda d, f=_pct / 100.0: C52 * (f + (1.0 - f) * d / 52.0)
for _p in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):  # an excess that falls as d^-p
    EXCESS[f"pow{_p}"] = lambda d, p=_p: C52 * (52.0 / d) ** p
EXCESS["affine_fall"] = lambda d: 7.0 - 0.06 * d
EXCESS["sqrt"] = lambda d: C52 * (d / 52.0) ** 0.5
EXCESS["big_fall"] = lambda d: 3.0 - 0.04 * d


BASE = {}      # name -> t_N(d) for a scenario that needs another baseline than 0.02 + 0.1357 d


def times(scen, d):
    """(t_N, t_F) in ns per inner call under a scenario."""
    if scen in EXCESS:
        tn = BASE[scen](d) if scen in BASE else 0.02 + 0.1357 * d
        return tn, tn + EXCESS[scen](d)
    a, b = 0.5, 0.05
    tn = a + b * d
    if scen == "h1":
        return tn, tn + 1.5
    if scen == "h2":                 # a cost per element on top of a fixed baseline: the ratio rises with d
        return tn, a + (b + 0.03) * d
    if scen == "h2flat":             # a = 0: the ratio is constant
        return b * d, 1.6 * b * d
    if scen == "mix":                # a fixed and a per-element part
        return tn, tn + 0.4 + 0.015 * d
    if scen == "null":
        return tn, tn
    raise ValueError(scen)


def loop(start, nbytes, simd=True):
    s = int(start, 16)
    win = (s + nbytes - 1) // 64 - s // 64 + 1
    mn = (nbytes + 63) // 64
    return {"start": start, "end": hex(s + nbytes), "bytes": nbytes, "start_mod64": s % 64, "crosses64": win > 1,
            "windows64": win, "min_windows64": mn, "extra_window": win > mn, "insns": 9, "simd": simd, "innermost": True}


def fake_info(same_layout=False, remark=STEP_REMARK):
    """What harness/run.py build_kernel returns, as far as the writer reads it."""
    loops = {"none": [loop("0x1260", 36)], "fast": [loop("0x1260" if same_layout else "0x12b0", 36)],
             "none_a64": [loop("0x1280", 36)], "fast_a64": [loop("0x1300", 36)]}
    return {"source": "kernels/k08_matmul.cpp", "loop_line": 11, "builds": {
        m: {"sha256": SHAS[m], "command": f"clang++-18 ... {m}", "traps": 0 if m.startswith("none") else 1, "asm_lines": 76,
            "vectorization": {"vectorized": True, "width": 4, "remarks": [remark] if remark else []}, "loops": loops[m]}
        for m in sw.an.MODES}}


def pair(rng, level, noise, reps, ratio=1.0):
    a = [level * math.exp(rng.gauss(0, noise)) for _ in range(reps)]
    b = [level * ratio * math.exp(rng.gauss(0, noise)) for _ in range(reps)]
    order = "".join(("AB" if k % 2 == 0 else "BA") for k in range(reps))
    return {"a_ns": a, "b_ns": b, "a_checksums": ["00ff"], "b_checksums": ["00ff"], "checksum_match": True, "order": order}


def cheap_summary(a, b):
    r = stats.ratio_of_medians(a, b)
    return {"ratio": r, "ci95": [r * 0.99, r * 1.01], "half_width_pct": 1.0}


def fake_doc(job, scen, scen_aligned=None, cpu="Neoverse-N2", caches=ARM, reps=40, noise=0.003, aa_noise=0.003,
             smoke=False, bad_checksum=False, plan_sha=None, same_layout=False, remark=STEP_REMARK):
    rng = random.Random(f"{cpu}|{job}|{scen}|{scen_aligned}")
    host = 1.0 + rng.uniform(-0.15, 0.15)
    lad = an.ladder(*caches)
    roles = an.roles_of(lad)
    order = sw.timing_order(job, list(roles))
    pts = []
    for d in sorted(roles):
        cols = {}
        for col, sc in (("as_compiled", scen), ("aligned", scen_aligned or scen)):
            tn, tf = times(sc, d)
            cols[col] = pair(rng, tn * d * d * host, noise, reps, tf / tn)
        fp, apr = cols["as_compiled"], cols["aligned"]
        if bad_checksum and d == lad["fit"][1]:
            fp["b_checksums"], fp["checksum_match"] = ["dead"], False
        tn, tf = times(scen, d)
        irn = int(d * d * (20 + 1.0 * d))
        instr = {"none": irn, "fast": irn + int(d * d * (tf - tn) * 40), "ratio": 1.0}
        instr["ratio"] = instr["fast"] / instr["none"]
        pts.append(sw.make_point(d, roles[d], caches[0], 1000, 1.0, fp, apr, instr, "ok", SHAS, summarize=cheap_summary))
    mid = lad["mid_d"]
    aa_level = times("null", mid)[0] * mid * mid * host
    aa = pair(rng, aa_level, aa_noise, reps)
    s = cheap_summary(aa["a_ns"], aa["b_ns"])
    aa_doc = {"d": mid, "binary_sha256": SHAS["none"], "n_per_side": reps, "iters": 1000, "a_ns": aa["a_ns"],
              "b_ns": aa["b_ns"], "order": aa["order"], **s}
    cache = {"l1d": caches[0], "l2": caches[1], "l3": 32 * 1024 * 1024, "llc": 32 * 1024 * 1024}
    run = {"id": f"run-{cpu[:3]}-{job // 6}", "job": str(job), "commit": "0" * 40, "workflow_run_url": None,
           "started_at": "2026-10-17T12:00:00Z", "runner": {"cpu_model": cpu, "cores": 4}, "toolchain": {"clang": "18.1.3"}}
    doc = sw.build_doc(smoke=smoke, reps=reps, cpu="1", run=run, cache=cache, lscpu="lscpu text", kernel={"source": "k", "loop_line": 11},
                       lad=lad, order=order, builds=sw.builds_record(fake_info(same_layout, remark)), aa=aa_doc, points=pts,
                       seconds=1.0)
    if plan_sha is not None:
        doc["plan_sha256"] = plan_sha
    return doc


@lru_cache(maxsize=None)
def jobs_of(scen, scen_aligned=None, n=5, cpu="Neoverse-N2", noise=0.003):
    caches = EPYC if "7763" in cpu else INTEL if "Xeon" in cpu else ARM
    return tuple((f"{cpu.replace(' ', '_')}/j{j}/dsweep.json",
                  fake_doc(j, scen, scen_aligned, cpu=cpu, caches=caches, noise=noise)) for j in range(1, n + 1))


def copy_items(items):
    return [(rel, json.loads(json.dumps(d))) for rel, d in items]


def analyse_items(items, cpu="Neoverse-N2", **kw):
    return an.analyse_cpu(cpu, list(items), an.plan_sha256(), an.criteria_sha256(), resamples=RES, **kw)


def word(items, cpu="Neoverse-N2"):
    return analyse_items(items, cpu)["verdict"]["word"]


@contextlib.contextmanager
def patched(*triples):
    """patched((obj, "name", value), ...): sets attributes and restores them on exit."""
    old = []
    try:
        for obj, name, value in triples:
            old.append((obj, name, getattr(obj, name)))
            setattr(obj, name, value)
        yield
    finally:
        for obj, name, value in reversed(old):
            setattr(obj, name, value)


def write_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f)


def read_plan():
    with open(os.path.join(REPO, "dsweep", "PLAN.md"), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- the ladder

def check_ladder(caches):
    lad = an.ladder(*caches)
    l1d, l2 = caches
    d1, d2 = lad["study_l1_d"], lad["study_l2_d"]
    assert d1 == hr.n_for("k08_matmul", l1d // 2) and d2 == hr.n_for("k08_matmul", l2 // 2)
    fit = lad["fit"]
    assert fit == sorted(set(fit)) and len(fit) >= 4
    assert fit[-1] == d1 and d1 in an.roles_of(lad) and "study_l1" in an.roles_of(lad)[d1] and "fit" in an.roles_of(lad)[d1]
    assert all(12 * d * d <= l1d // 2 for d in fit + lad["scan"]), "every fitted and scanned d is L1-resident"
    assert 12 * d2 * d2 <= l2 // 2 < 12 * (d2 + 1) ** 2 and d2 > d1
    assert 12 * d2 * d2 > l1d // 2, "the study L2 d is above L1 (context, not fitted)"
    assert d2 not in fit and "study_l2" in an.roles_of(lad)[d2]
    assert {d % an.MODULUS for d in fit} == {d1 % an.MODULUS}, "one residue class"
    assert all(b - a == an.MODULUS for a, b in zip(fit, fit[1:])) and fit[0] >= an.MIN_D
    assert sorted((d1 - 7 + k) % an.MODULUS for k in range(8)) == list(range(8))
    assert sorted(lad["scan"] + [d1]) == list(range(d1 - 7, d1 + 1)), "scan + study L1 d cover every residue"
    assert lad["mid_d"] in fit and lad["mid_d"] == fit[len(fit) // 2]
    br = lad["bridge"]
    assert br == sorted(set(br)) and 1 <= len(br) <= an.BRIDGE_POINTS
    assert all(d1 < d < d2 for d in br), "the bridge lies between the two study sizes"
    assert {d % an.MODULUS for d in br} == {d1 % an.MODULUS}, "the bridge keeps the leftover count of the study L1 d"
    assert all(12 * d * d > l1d // 2 for d in br), "bridge points are not L1-resident (context, not fitted)"
    roles = an.roles_of(lad)
    assert all(roles[d] == ["bridge"] for d in br) and not set(br) & set(fit)
    assert len(roles) == len(set(fit) | set(lad["scan"]) | set(br) | {d1, d2})
    return lad


def test_ladder_arm_like():
    lad = check_ladder(ARM)
    assert (lad["study_l1_d"], lad["study_l2_d"]) == (52, 209)
    assert lad["fit"] == [12, 20, 28, 36, 44, 52] and lad["scan"] == [45, 46, 47, 48, 49, 50, 51] and lad["mid_d"] == 36
    assert lad["bridge"] == [76, 108, 148], "the bridge the plan names for Neoverse-N2"
    assert len(an.roles_of(lad)) == 17


def test_ladder_epyc_like():
    lad = check_ladder(EPYC)
    assert (lad["study_l1_d"], lad["study_l2_d"]) == (36, 147)
    assert lad["fit"] == [12, 20, 28, 36]
    assert lad["bridge"] == [52, 76, 100], "the bridge the plan names for EPYC 7763"


def test_ladder_intel_like_and_odd_sizes():
    lad = check_ladder(INTEL)
    assert lad["study_l1_d"] == 45 and lad["fit"] == [13, 21, 29, 37, 45]
    for l1d in (16 * 1024, 24 * 1024, 80 * 1024, 96 * 1024, 128 * 1024):
        lad = an.ladder(l1d, 16 * l1d)
        assert lad["fit"][-1] == lad["study_l1_d"] and lad["mid_d"] in lad["fit"]
        assert all(12 * d * d <= l1d // 2 for d in lad["fit"])
        assert all(lad["study_l1_d"] < d < lad["study_l2_d"] and d % an.MODULUS == lad["residue"] for d in lad["bridge"])


def test_ladder_cli_prints_it_without_linux():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert sw.main(["--assume-caches", "64,1024"]) == 0
    assert json.loads(buf.getvalue()) == an.ladder(*ARM)
    try:
        sw.main(["--assume-caches", "64"])
    except SystemExit as e:
        assert "L1D_KIB,L2_KIB" in str(e)
    else:
        raise AssertionError("a malformed --assume-caches must stop with a plain message")


def test_timing_order_is_a_fixed_shuffle_per_job():
    ds = list(an.roles_of(an.ladder(*ARM)))
    assert sw.timing_order(3, ds) == sw.timing_order(3, ds) and sorted(sw.timing_order(3, ds)) == sorted(ds)
    assert any(sw.timing_order(j, ds) != sw.timing_order(1, ds) for j in range(2, 8))
    assert sw.timing_order(1, ds) != sorted(ds) or sw.timing_order(2, ds) != sorted(ds)


# ---------------------------------------------------------------- the numbers of the rule

def test_rule_numbers_match_the_criteria_file_and_the_plan():
    crit = an.criteria()
    assert an.RULE["minimum_jobs"] == crit["v3"]["pooling"]["minimum_jobs"] == 3
    assert an.RULE["aa_half_width_max_pct"] == crit["verdict"]["aa_half_width_max_pct"] == 2.0
    assert an.reps_per_side() == crit["v3"]["timing"]["reps_per_side"] == 40
    assert pool.RESAMPLES == 2000 and pool.SEED_PREFIX == "20261011"
    plan = read_plan()
    for phrase in ("Fewer than 3 jobs", "above 2.0%", "Fewer than 4 fit d values", "above 0.10", "above 0.15",
                   "More than 2.5% of the resamples", "inside 0.8 to 1.2", "inside -0.2 to 0.2", "above 1.2",
                   "2000 resamples", "20261011", "40 processes per side", "congruent to", "76, 108, 148", "52, 76, 100"):
        assert phrase in plan, f"the plan does not say {phrase!r}"
    assert an.RULE == {"minimum_jobs": 3, "aa_half_width_max_pct": 2.0, "minimum_fit_points": 4,
                       "baseline_max_relative_residual": 0.10, "excess_max_relative_residual": 0.15,
                       "undefined_resamples_max_fraction": 0.025, "h1_share_band": [0.8, 1.2],
                       "h2_share_band": [-0.2, 0.2], "falls_share_above": 1.2}


def test_the_plans_machine_readable_rule_block_is_the_rule_in_the_code():
    plan = read_plan()
    head = plan.index("## The numbers of the rule, as the code reads them")
    block = re.search(r"```json\n(.*?)\n```", plan[head:], re.S)
    assert block, "the plan has no json block with the numbers of the rule"
    assert json.loads(block.group(1)) == an.RULE, "the numbers in dsweep/PLAN.md and RULE in dsweep/analyze.py differ"
    # the conditions are numbered in the plan in the order decide_column applies them
    sec = plan[plan.index("**Conditions, in this order.**"):plan.index("Why these numbers")]
    items = re.findall(r"^(\d+)\. (.*?)(?=^\d+\. |\Z)", sec, re.M | re.S)
    assert [int(n) for n, _ in items] == list(range(1, 13)), "the plan lists 12 conditions"
    phrases = ("Fewer than 3 jobs", "A file problem in any job", "half-width above 2.0%", "Fewer than 4 fit d values",
               "The cost is not seen", "is not affine in d", "is not a straight line in d", "More than 2.5% of the resamples",
               '"H1" if', '"H2" if', '"falls" if', 'Otherwise "neither"')
    for (n, body), text in zip(items, phrases):
        assert text in body, (n, text)
    # and the code answers them in that order: each reason names the condition that stopped it
    reasons = [
        ("too few", decide_reason(J=2)), ("file problems", decide_reason(problems=["x"])),
        ("byte-identical A/A", decide_reason(aa_half_width_pct=9.0)), ("fit d values", decide_reason(fit_ds=[12])),
        ("not separated", decide_reason(cost_unseen=[12])),
        ("not affine in d", decide_reason(baseline={"median_max_relative_residual": 0.5})),
        ("straight line", decide_reason(excess_residual=0.5)), ("of the resamples", decide_reason(undefined_fraction=0.5)),
        ("same at every d", decide_reason()), ("proportional to d", decide_reason(share=0.0, share_ci95=[-0.1, 0.1])),
        ("smaller at the larger d", decide_reason(share=2.0, share_ci95=[1.5, 2.5])),
        ("not inside the H1 band", decide_reason(share=0.5, share_ci95=[0.4, 0.6]))]
    for text, reason in reasons:
        assert text in reason or (text == "too few" and "minimum" in reason), (text, reason)


def test_the_predictions_in_the_plan_are_the_algebra_of_the_stored_numbers():
    a, b, c = 0.0218, 0.13574, 3.878
    plan = read_plan()
    for d in (12, 20, 28, 36, 44, 52):
        h1 = 1 + c / (a + b * d)
        h2 = 1 + (c / 52 * d) / (a + b * d)
        assert f"| {d} | {h1:.2f} | {h2:.2f} |" in plan, (d, h1, h2)


def test_the_stored_neoverse_n2_numbers_quoted_in_the_plan():
    import glob
    files = sorted(glob.glob(os.path.join(REPO, "results", "s8-arm-run-*", "results-*", "results.json")))
    if not files:
        return   # the stored results are not in this checkout
    per = {"L1": [], "L2": []}
    for f in files:
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        for sz, dd in (("L1", 52), ("L2", 209)):
            c = next(x for x in d["cells"] if x["cell_id"] == "k08_matmul." + sz)
            tn = stats.median(c["none_ns"]) / dd ** 2
            tf = stats.median(c["fast_ns"]) / dd ** 2
            per[sz].append((tn, tn / dd, tf - tn))
    assert len(files) == 30 and all(len(v) == 30 for v in per.values())
    mean = lambda sz, i: sum(p[i] for p in per[sz]) / len(per[sz])  # noqa: E731
    assert abs(mean("L1", 0) - 7.080) < 0.001 and abs(mean("L2", 0) - 28.392) < 0.001
    assert abs(mean("L1", 1) - 0.1362) < 0.0001 and abs(mean("L2", 1) - 0.1358) < 0.0001
    assert abs(mean("L1", 2) - 3.878) < 0.001 and abs(mean("L2", 2) - 0.462) < 0.001
    per_el = [per["L2"][i][1] / per["L1"][i][1] for i in range(30)]
    fall = [per["L1"][i][2] / per["L2"][i][2] for i in range(30)]
    assert (round(min(per_el), 3), round(max(per_el), 3)) == (0.993, 0.999), \
        "the NONE time per element does not change from d = 52 to 209"
    assert (round(min(fall), 1), round(max(fall), 1)) == (8.2, 8.6), "the excess per inner call falls 8.2 to 8.6 times in every job"
    # the lines the plan quotes: a, b from the two NONE times
    b = (mean("L2", 0) - mean("L1", 0)) / (209 - 52)
    a = mean("L1", 0) - b * 52
    assert abs(b - 0.13574) < 0.00002 and abs(a - 0.0218) < 0.001
    with open(os.path.join(REPO, "results", "s8-arm-pooled", "pooled.json"), encoding="utf-8") as fh:
        block = json.load(fh)["cpus"][0]
    cells = {c["cell_id"]: c for c in block["cells"] if c["kernel"] == "k08_matmul"}
    extra = {sz: (cells["k08_matmul." + sz]["instr"]["fast"] - cells["k08_matmul." + sz]["instr"]["none"]) / dd ** 2
             for sz, dd in (("L1", 52), ("L2", 209))}
    assert abs(extra["L1"] - 77.0) < 0.05 and abs(extra["L2"] - 53.0) < 0.05
    plan = read_plan()
    for text in ("| 77.0 | 53.0 |", "8.2 to 8.6", "0.993 and 0.999", "| 3.878 | 0.462 |", "| 7.080 | 28.392 |"):
        assert text in plan, text


def test_published_context_numbers_are_the_pooled_files_numbers():
    for cpu, rec in an.PUBLISHED.items():
        path = os.path.join(REPO, rec["source"])
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        block = next(b for b in doc["cpus"] if b["cpu_model"] == cpu)
        got = {c["cell_id"]: c["as_compiled"]["ratio"] for c in block["cells"] if c["kernel"] == "k08_matmul"}
        assert abs(got["k08_matmul.L1"] - rec["L1"]) < 0.0006 and abs(got["k08_matmul.L2"] - rec["L2"]) < 0.0006, cpu


def decide_both(J=5, problems=(), **over):
    good = {"aa_half_width_pct": 0.1, "fit_ds": [12, 20, 28, 36], "cost_unseen": [],
            "baseline": {"median_max_relative_residual": 0.01},
            "excess": {"undefined_fraction": 0.0, "share": 1.0, "share_ci95": [0.9, 1.1],
                       "residual": {"median_max_relative_residual": 0.01}}}
    col = json.loads(json.dumps(good))
    for k, v in over.items():
        if k == "excess_residual":
            col["excess"]["residual"]["median_max_relative_residual"] = v
        elif k in col["excess"]:
            col["excess"][k] = v
        else:
            col[k] = v
    return an.decide_column(J, list(problems), col)


def decide(*a, **kw):
    return decide_both(*a, **kw)[0]


def decide_reason(*a, **kw):
    return decide_both(*a, **kw)[1]


def test_decide_column_conditions_in_their_order():
    d = decide
    assert d() == an.H1
    assert d(J=2) == an.TOO_FEW and d(J=2, problems=["x"]) == an.TOO_FEW, "too few jobs is checked first"
    assert d(problems=["x"]) == an.NEITHER
    assert d(aa_half_width_pct=2.01) == an.NEITHER and d(aa_half_width_pct=2.0) == an.H1
    assert d(fit_ds=[12, 20, 28]) == an.NEITHER
    assert d(cost_unseen=[12]) == an.NEITHER
    assert d(baseline={"median_max_relative_residual": 0.1001}) == an.NEITHER
    assert d(baseline={"median_max_relative_residual": 0.10}) == an.H1
    assert d(excess_residual=0.1501) == an.NEITHER and d(excess_residual=0.15) == an.H1
    assert d(undefined_fraction=0.026) == an.NEITHER and d(undefined_fraction=0.025) == an.H1
    # the order: a failed earlier condition wins over a later one that also fails
    assert "byte-identical A/A" in decide_reason(aa_half_width_pct=3.0, cost_unseen=[12])
    assert "not separated" in decide_reason(cost_unseen=[12], baseline={"median_max_relative_residual": 0.2})
    assert decide_reason(baseline={"median_max_relative_residual": 0.2}, excess_residual=0.5).startswith(
        "the time per inner call is not affine"), "condition 6 is checked before condition 7"
    assert "straight line" in decide_reason(excess_residual=0.5, undefined_fraction=0.5), "condition 7 before 8"
    assert "of the resamples" in decide_reason(undefined_fraction=0.5, share=0.5, share_ci95=[0.4, 0.6])


def test_the_share_bands():
    d = decide
    # H1: the point estimate and the whole interval inside 0.8 to 1.2
    assert d(share=1.0, share_ci95=[0.8, 1.2]) == an.H1
    assert d(share=0.8, share_ci95=[0.8, 0.9]) == an.H1 and d(share=1.2, share_ci95=[1.1, 1.2]) == an.H1
    assert d(share=1.0, share_ci95=[0.79, 1.1]) == an.NEITHER
    assert d(share=1.0, share_ci95=[0.9, 1.21]) == an.NEITHER
    assert d(share=0.79, share_ci95=[0.8, 0.9]) == an.NEITHER, "the point estimate must lie inside as well"
    # H2: inside -0.2 to 0.2
    assert d(share=0.0, share_ci95=[-0.2, 0.2]) == an.H2
    assert d(share=0.0, share_ci95=[-0.21, 0.1]) == an.NEITHER and d(share=0.0, share_ci95=[-0.1, 0.21]) == an.NEITHER
    # falls: above 1.2
    assert d(share=2.0, share_ci95=[1.21, 3.0]) == an.FALLS and d(share=2.0, share_ci95=[1.3, 3.0]) == an.FALLS
    assert d(share=2.0, share_ci95=[1.2, 3.0]) == an.NEITHER, "an interval that reaches 1.2 is not 'falls'"
    assert d(share=1.2, share_ci95=[1.19, 1.4]) == an.NEITHER
    # in between: a mixture
    for s in (0.25, 0.5, 0.75):
        assert d(share=s, share_ci95=[s - 0.02, s + 0.02]) == an.NEITHER
    # a share below the H2 band (the excess grows faster than d) is not a word either
    assert d(share=-0.5, share_ci95=[-0.6, -0.4]) == an.NEITHER
    nan = float("nan")
    assert d(share=nan, share_ci95=[nan, nan]) == an.NEITHER and d(share=1.0, share_ci95=[nan, nan]) == an.NEITHER
    assert an.headline((an.H1, "r"), (an.H1, "r"))["word"] == an.H1
    h = an.headline((an.H1, "r"), (an.NEITHER, "s"))
    assert h["word"] == an.NEITHER and not h["columns_agree"] and "disagree" in h["reason"]
    assert an.headline((an.FALLS, "r"), (an.H1, "s"))["word"] == an.NEITHER
    assert an.headline((an.TOO_FEW, "r"), (an.TOO_FEW, "r"))["word"] == an.TOO_FEW


# ---------------------------------------------------------------- the analysis on made-up jobs

def test_h1_data_gives_h1():
    b = analyse_items(jobs_of("h1"))
    assert b["verdict"]["word"] == an.H1 and b["verdict"]["columns_agree"], b["verdict"]["reason"]
    ex = b["columns"]["as_compiled"]["excess"]
    assert 0.95 < ex["share"] < 1.05 and ex["share_ci95"][0] > 0.9 and ex["share_ci95"][1] < 1.1
    assert 0.95 < ex["growth"] < 1.05 and ex["undefined_fraction"] == 0
    assert b["columns"]["as_compiled"]["fit_ds"] == [12, 20, 28, 36, 44, 52]
    r = {x["d"]: x["ratio"] for x in b["columns"]["as_compiled"]["rows"]}
    assert r[12] > r[20] > r[36] > r[52] > 1.3, "under H1 the ratio falls with d"
    e = {x["d"]: x["excess_ns_per_inner"] for x in b["columns"]["as_compiled"]["rows"]}
    fixed = [e[d] for d in (12, 20, 28, 36, 44, 52)]
    assert max(fixed) / min(fixed) < 1.03, "the excess per inner call is the same at every d"
    assert b["instructions"]["fit"]["slope"] < 0.5 and b["instructions"]["jobs_agree"]
    y = b["columns"]["as_compiled"]["y_view"]
    assert y["slope_ci95"][0] > 0, "the y view of the first draft is still printed"


def test_h2_data_with_a_baseline_gives_h2():
    b = analyse_items(jobs_of("h2"))
    assert b["verdict"]["word"] == an.H2, b["verdict"]["reason"]
    r = {x["d"]: x["ratio"] for x in b["columns"]["as_compiled"]["rows"]}
    assert r[12] < r[52], "a per-element cost on a fixed baseline: the ratio rises with d"
    ex = b["columns"]["as_compiled"]["excess"]
    assert abs(ex["share"]) < 0.05 and 2.5 < ex["growth"] <= 52 / 12 + 0.3


def test_h2_data_with_no_baseline_gives_h2():
    b = analyse_items(jobs_of("h2flat"))
    assert b["verdict"]["word"] == an.H2, b["verdict"]["reason"]
    ex = b["columns"]["as_compiled"]["excess"]
    assert abs(ex["share"]) < 0.05 and abs(ex["growth"] - 52 / 12) < 0.3


def test_no_cost_at_all_is_neither():
    b = analyse_items(jobs_of("null"))
    assert b["verdict"]["word"] == an.NEITHER and "not separated" in b["verdict"]["reason"], b["verdict"]["reason"]


def test_a_mixture_between_the_bands_is_neither():
    b = analyse_items(jobs_of("mix"))
    ex = b["columns"]["as_compiled"]["excess"]
    assert 0.2 < ex["share"] < 0.8 and 0.2 < ex["share_ci95"][0] and ex["share_ci95"][1] < 0.8, ex["share"]
    assert b["verdict"]["word"] == an.NEITHER and "not inside the H1 band" in b["verdict"]["reason"], b["verdict"]["reason"]


def test_an_excess_that_falls_with_d_is_falls():
    b = analyse_items(jobs_of("big_fall"))
    ex = b["columns"]["as_compiled"]["excess"]
    assert ex["share"] > 1.2 and ex["share_ci95"][0] > 1.2 and ex["growth"] < 0.87, ex["share"]
    assert b["verdict"]["word"] == an.FALLS, b["verdict"]["reason"]
    assert "smaller at the larger d" in b["verdict"]["reason"]


def test_the_shapes_the_first_draft_called_h1():
    """The review of the first draft (slope of 1/(R-1) on d with Q >= 1.5 was 'H1') showed it said 'H1' for these.
    The fixed share of the excess per inner call must not."""
    want = {"fixed100": an.H1, "fixed75": an.NEITHER, "fixed50": an.NEITHER, "fixed35": an.NEITHER,
            "fixed25": an.NEITHER, "fixed10": an.H2, "fixed0": an.H2,
            "pow0.2": an.FALLS, "pow0.3": an.FALLS, "pow0.4": an.FALLS, "pow0.5": an.FALLS,
            "pow0.6": an.NEITHER, "pow0.7": an.NEITHER, "affine_fall": an.FALLS, "sqrt": an.NEITHER}
    got = {}
    for name in want:
        b = analyse_items(jobs_of(name))
        got[name] = b["verdict"]["word"]
        if want[name] != an.H1:
            assert b["verdict"]["word"] != an.H1, (name, b["verdict"]["reason"])
    assert got == want, {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    # every excess that falls as d^-p with p >= 0.2, and the affine fall, is not H1 although the y view's dilution was
    # above 4.33, the largest value a fixed cost can give on the Neoverse-N2 ladder
    for name in ("pow0.3", "pow0.5", "affine_fall"):
        q = analyse_items(jobs_of(name))["columns"]["as_compiled"]["y_view"]["q"]
        assert q > 52 / 12, (name, q)
    # a strongly curved fall is 'neither' because the excess is not a straight line, with that reason
    r = analyse_items(jobs_of("pow0.7"))["verdict"]["reason"]
    assert "straight line" in r or "not affine" in r, r


def test_a_fixed_cost_is_still_h1_with_realistic_job_noise():
    items = jobs_of("fixed100", n=6, noise=0.01)
    b = analyse_items(items)
    ex = b["columns"]["as_compiled"]["excess"]
    assert b["verdict"]["word"] == an.H1, (b["verdict"]["reason"], ex["share"], ex["share_ci95"])
    assert 0.8 < ex["share_ci95"][0] and ex["share_ci95"][1] < 1.2


def test_too_few_jobs():
    items = jobs_of("h1", n=6)[:2]
    b = analyse_items(items)
    assert b["verdict"]["word"] == an.TOO_FEW and b["jobs"] == 2
    assert b["columns"]["as_compiled"] is not None, "the table is still computed for a smaller set"
    one = analyse_items(items[:1])
    assert one["verdict"]["word"] == an.TOO_FEW and one["columns"]["as_compiled"]["rows"]


def test_columns_that_disagree_give_neither():
    b = analyse_items(jobs_of("h1", "null"))
    assert b["words"]["as_compiled"]["word"] == an.H1 and b["words"]["aligned"]["word"] == an.NEITHER
    assert b["verdict"]["word"] == an.NEITHER and not b["verdict"]["columns_agree"]
    assert "disagree" in b["verdict"]["reason"]


def test_x86_style_lost_simd_loop_is_h2_not_h1():
    # the negative control of the plan: a per-element loss of SIMD on an EPYC-like ladder (4 fit points) must not read as a fixed cost
    items = jobs_of("h2", cpu=EPYC_NAME)
    b = analyse_items(items, EPYC_NAME)
    assert b["columns"]["as_compiled"]["fit_ds"] == [12, 20, 28, 36]
    assert b["verdict"]["word"] == an.H2, b["verdict"]["reason"]
    assert b["published"]["L1"] == 3.19


def test_x86_style_regime_change_at_the_smallest_d_is_neither_whatever_the_check_does():
    # the weak-control caveat of the plan: a NONE vector loop that is not entered at d = 12 is a change of regime
    items = []
    for j in range(1, 6):
        doc = fake_doc(j, "h1", cpu=EPYC_NAME, caches=EPYC)
        for p in doc["points"]:
            if p["d"] == 12:
                for col in ("as_compiled", "aligned"):
                    p[col]["none_ns"] = [x * 1.4 for x in p[col]["none_ns"]]
        items.append((f"j{j}/dsweep.json", doc))
    b = analyse_items(items, EPYC_NAME)
    assert b["verdict"]["word"] == an.NEITHER and "not affine" in b["verdict"]["reason"], b["verdict"]["reason"]


def test_file_problems_give_neither_with_the_reason():
    ok = list(jobs_of("h1"))

    def with_(j, mutate):
        items = copy_items(ok)
        mutate(items[j][1])
        return items

    cases = {
        "a smoke file": lambda d: d.update(smoke=True),
        "plan hash": lambda d: d.update(plan_sha256="0" * 64),
        "criteria hash": lambda d: d.update(criteria_sha256="0" * 64),
        "different code": lambda d: d["code_sha256"].update({"harness/run.py": "e" * 64}),
        "code list": lambda d: d["code_sha256"].pop("kernels/common.hpp"),
        "checksums": lambda d: d["points"][1].update(checksum_match=False),
        "samples": lambda d: d["points"][1]["as_compiled"]["fast_ns"].pop(),
        "ladder": lambda d: d["ladder"].update(mid_d=44),
        "binaries": lambda d: d["builds"]["fast"].update(sha256="e" * 64),
        "a missing d": lambda d: d["points"].pop(2),
        "schema": lambda d: d.update(schema_version=2),
        "a pass of 16 elements": lambda d: d["builds"]["none"].update(elements_per_pass=16),
    }
    for name, mutate in cases.items():
        b = analyse_items(with_(2, mutate))
        assert b["verdict"]["word"] == an.NEITHER and b["problems"], name
        assert b["columns"]["as_compiled"] is None
    # the cross-job difference of the code names the file and says what to do
    b = analyse_items(with_(2, cases["different code"]))
    assert any("ran different code" in p and "harness/run.py" in p for p in b["problems"]), b["problems"]


def test_a_noisy_ab_control_gives_neither():
    items = tuple((f"j{j}/dsweep.json", fake_doc(j, "h1", aa_noise=0.12)) for j in range(1, 6))
    b = analyse_items(items)
    assert b["aa"]["half_width_pct"] > 2.0
    assert b["verdict"]["word"] == an.NEITHER and "A/A" in b["verdict"]["reason"]


def test_a_baseline_that_is_not_affine_gives_neither():
    # a regime change at the smallest d (for example a vector loop that is not entered): t_N jumps by 30% at d = 12
    items = []
    for j in range(1, 6):
        doc = fake_doc(j, "h1")
        for p in doc["points"]:
            if p["d"] == 12:
                for col in ("as_compiled", "aligned"):
                    p[col]["none_ns"] = [x * 1.3 for x in p[col]["none_ns"]]
        items.append((f"j{j}/dsweep.json", doc))
    b = analyse_items(items)
    assert b["verdict"]["word"] == an.NEITHER and "not affine" in b["verdict"]["reason"], b["verdict"]["reason"]


def test_an_excess_that_is_not_a_straight_line_gives_neither():
    # a baseline with a large fixed part (5 ns) and an excess of 3 ns that alternates by 0.6 ns from one d to the next:
    # a wobble of 20% of the excess but under 10% of t_F, so condition 6 does not fire first and condition 7 does
    BASE["wobble"] = lambda d: 5.0 + 0.1357 * d
    EXCESS["wobble"] = lambda d: 3.0 + (0.6 if (d // 8) % 2 else -0.6)
    items = jobs_of("wobble", n=5)
    b = analyse_items(items)
    c = b["columns"]["as_compiled"]
    assert c["baseline"]["median_max_relative_residual"] <= 0.10, c["baseline"]["median_max_relative_residual"]
    assert c["excess"]["residual"]["median_max_relative_residual"] > 0.15, c["excess"]["residual"]
    assert b["verdict"]["word"] == an.NEITHER and "straight line" in b["verdict"]["reason"], b["verdict"]["reason"]


def test_deterministic_and_json_clean():
    a = analyse_items(jobs_of("h1"))
    b = analyse_items(jobs_of("h1"))
    assert json.dumps(an.jsonable(a), sort_keys=True) == json.dumps(an.jsonable(b), sort_keys=True)
    text = json.dumps(an.jsonable(a), allow_nan=False)
    assert "Infinity" not in text and "NaN" not in text
    # the seed rule is the pooled file's: other seeds give other draws, the same seed the same draws
    d1 = pool.draws(pool.seed_for("cpu", "dsweep|as_compiled|jobs", "jobs"), (4, 3), 3)
    d2 = pool.draws(pool.seed_for("cpu", "dsweep|as_compiled|jobs", "jobs"), (4, 3), 3)
    d3 = pool.draws(pool.seed_for("cpu2", "dsweep|as_compiled|jobs", "jobs"), (4, 3), 3)
    assert (d1 == d2).all() and not (d1 == d3).all()


def test_job_order_does_not_change_the_words():
    items = list(jobs_of("h1"))
    assert word(items) == word(list(reversed(items))) == an.H1


def test_markdown_table():
    a = an.analyse(list(jobs_of("h1")), resamples=RES)
    md = an.render_markdown(a)
    assert "### Neoverse-N2: H1" in md and "| d | role |" in md and "fit+study_l1" in md and "study_l2" in md
    assert "published" in md and "1.548" in md and "1.016" in md, "the published ratios are set beside the study d values"
    assert md.count("| 12 |") == 1 and "scan" in md and "| 76 | bridge |" in md and "excess ns per inner call" in md
    assert a["line"].startswith("On Neoverse-N2 (5 jobs, 1 run pooled): H1")
    other = an.render_markdown(an.analyse([], resamples=RES))
    assert "no jobs" in other


def test_two_cpu_models_are_pooled_separately():
    items = list(jobs_of("h1")) + list(jobs_of("h2", cpu=EPYC_NAME))
    a = an.analyse(items, resamples=RES)
    got = {b["cpu_model"]: b["verdict"]["word"] for b in a["cpus"]}
    assert got == {"Neoverse-N2": an.H1, EPYC_NAME: an.H2}


# ---------------------------------------------------------------- records: code hashes, the plan file, job order, partial files

def test_code_that_differs_from_the_jobs_is_flagged_beside_the_verdict():
    items = copy_items(jobs_of("h1"))
    for _, d in items:
        d["code_sha256"]["harness/run.py"] = "9" * 64      # every job ran with another harness/run.py than the one now
    b = analyse_items(items)
    assert b["verdict"]["word"] == an.H1, "the same code in every job: not a file problem"
    assert b["code_changed_since_run"] == ["harness/run.py"]
    a = an.analyse(items, resamples=RES)
    assert "harness/run.py" in an.render_markdown(a) and "harness/run.py" in an.report(a)
    clean = analyse_items(jobs_of("h1"))
    assert clean["code_changed_since_run"] == []
    h = an.code_sha256()
    assert sorted(h) == sorted(an.CODE_FILES) and all(len(v) == 64 for v in h.values()), "every code file exists and is hashed"


def test_the_plan_option_analyses_against_a_restored_plan_text():
    with tempfile.TemporaryDirectory() as tmp:
        restored = os.path.join(tmp, "plan.md")
        text = read_plan() + "\nA sentence added later.\n"
        with open(restored, "w", encoding="utf-8", newline="") as f:
            f.write(text.replace("\n", "\r\n"))            # line endings do not count
        sha = an.plan_sha256(restored)
        assert sha != an.plan_sha256() and sha == an.plan_sha256(restored)
        items = [(f"j{j}/dsweep.json", fake_doc(j, "h1", plan_sha=sha)) for j in range(1, 6)]
        refused = an.analyse(items, resamples=RES)
        assert refused["cpus"][0]["verdict"]["word"] == an.NEITHER
        assert any("plan hash" in p for p in refused["cpus"][0]["problems"])
        accepted = an.analyse(items, resamples=RES, plan_path=restored)
        assert accepted["cpus"][0]["verdict"]["word"] == an.H1 and accepted["plan_sha256"] == sha
        assert accepted["plan_file"].endswith("plan.md")
        try:
            an.main([tmp, "--plan", os.path.join(tmp, "nothing.md")])
        except SystemExit as e:
            assert "--plan" in str(e)
        else:
            raise AssertionError("a --plan that is not a file must stop with a plain message")


def test_the_bootstrap_does_not_depend_on_the_folder_layout():
    jobs = [(f"x/j{j}", fake_doc(j, "h1")) for j in range(1, 6)]
    with tempfile.TemporaryDirectory() as tmp:
        # layout A: the folder names sort in the reverse order of the job numbers; layout B: in job order
        for rel, doc in jobs:
            j = int(doc["run"]["job"])
            write_json(os.path.join(tmp, "a", f"zz{10 - j}", "dsweep.json"), doc)
            write_json(os.path.join(tmp, "b", "deep", "er", f"j{j}", "dsweep.json"), doc)
        ea = an.load_entries([os.path.join(tmp, "a")], os.path.join(tmp, "a"))
        eb = an.load_entries([os.path.join(tmp, "b")], os.path.join(tmp, "b", "out"))
        assert [d["run"]["job"] for _, d in ea] == [d["run"]["job"] for _, d in eb] == ["1", "2", "3", "4", "5"]
        pa, pb = an.analyse(ea, resamples=RES), an.analyse(eb, resamples=RES)
        assert json.dumps(an.jsonable(pa["cpus"][0]["columns"]), sort_keys=True) == \
            json.dumps(an.jsonable(pb["cpus"][0]["columns"]), sort_keys=True), "the intervals depend on where the files lie"
        # job 10 sorts after job 9
        assert an._job_key({"run": {"id": "r", "job": "10"}}, "h") > an._job_key({"run": {"id": "r", "job": "9"}}, "h")
        assert an._job_key("not a dict", "h") and an._job_key({"run": None}, "h")


def test_a_job_that_stopped_after_its_first_timing_is_listed_not_pooled():
    with tempfile.TemporaryDirectory() as tmp:
        for j in (1, 2, 3):
            write_json(os.path.join(tmp, "m", f"dsweep-job-x-j{j}", "dsweep.json"), fake_doc(j, "h1"))
        partial_dir = os.path.join(tmp, "m", "dsweep-job-x-j4")
        os.makedirs(partial_dir)
        header = {"kind": "dsweep-partial", "run": {"id": "run-Neo-0", "job": "4", "runner": {"cpu_model": "Neoverse-N2"}},
                  "points_expected": 17}
        with open(os.path.join(partial_dir, an.PARTIAL_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n")
            f.write(json.dumps({"starting": 28}) + "\n")
            f.write(json.dumps({"point": {"d": 28}}) + "\n")
            f.write(json.dumps({"starting": 12}) + "\n")
            f.write(json.dumps({"point": {"d": 12}}) + "\n")
            f.write(json.dumps({"starting": 52}) + "\n")
            f.write('{"point": {"d": 5')                    # the process was killed in the middle of a line
        # a job that finished leaves no partial file; one that has both is a finished job
        twin = os.path.join(tmp, "m", "dsweep-job-x-j1")
        with open(os.path.join(twin, an.PARTIAL_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n")
        inc = an.find_incomplete([os.path.join(tmp, "m")], tmp)
        assert len(inc) == 1, inc
        j4 = inc[0]
        assert j4["job"] == "4" and j4["points_done"] == 2 and j4["d_done"] == [28, 12] and j4["last_d_started"] == 52
        assert j4["points_expected"] == 17 and j4["path"].endswith("dsweep-job-x-j4/" + an.PARTIAL_NAME)
        entries = an.load_entries([os.path.join(tmp, "m")], tmp)
        assert len(entries) == 3, "a partial file is never loaded as a result"
        a = an.analyse(entries, resamples=RES, incomplete=inc)
        assert a["incomplete_jobs"] == inc and a["cpus"][0]["jobs"] == 3
        assert "d values timed" in an.render_markdown(a) and "[incomplete]" in an.report(a)
        # no dsweep.json at all: the command line lists the partial job and says there is nothing to pool
        only = os.path.join(tmp, "only")
        os.makedirs(os.path.join(only, "j9"))
        with open(os.path.join(only, "j9", an.PARTIAL_NAME), "w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n" + json.dumps({"starting": 28}) + "\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert an.main([only]) == 1
        assert "no dsweep.json found" in buf.getvalue() and "[incomplete]" in buf.getvalue()
        # naming the partial file itself does not make it a result
        assert an.find_files([os.path.join(only, "j9", an.PARTIAL_NAME)]) == []


# ---------------------------------------------------------------- the file

def real_doc(reps, job=1, smoke=False, remark=STEP_REMARK):
    """A file whose intervals are the real within-job bootstrap (so that verify_job has something to recompute)."""
    rng = random.Random(7 + job)
    lad = an.ladder(*ARM)
    roles = an.roles_of(lad)
    pts = []
    for d in sorted(roles):
        fp, apr = pair(rng, 100.0 * d, 0.01, reps, 1.5), pair(rng, 100.0 * d, 0.01, reps, 1.5)
        pts.append(sw.make_point(d, roles[d], ARM[0], 10, 1.0, fp, apr, None, "x", SHAS, summarize=stats.summarize))
    aa = pair(rng, 100.0, 0.01, reps)
    aa_doc = {"d": lad["mid_d"], "binary_sha256": SHAS["none"], "n_per_side": reps, "iters": 10, "a_ns": aa["a_ns"],
              "b_ns": aa["b_ns"], "order": aa["order"], **stats.summarize(aa["a_ns"], aa["b_ns"])}
    return sw.build_doc(smoke=smoke, reps=reps, cpu="1",
                        run={"id": "x", "job": str(job), "commit": None, "workflow_run_url": None, "started_at": "t",
                             "runner": {"cpu_model": "m"}, "toolchain": {}},
                        cache={"l1d": ARM[0], "l2": ARM[1]}, lscpu="", kernel={}, lad=lad, order=sorted(roles),
                        builds=sw.builds_record(fake_info(remark=remark)), aa=aa_doc, points=pts, seconds=0)


def test_the_writer_produces_a_valid_file_with_the_documented_fields():
    doc = fake_doc(1, "h1")
    assert an.validate_doc(doc) == []
    for k in an.TOP_KEYS:
        assert k in doc
    assert doc["kind"] == "dsweep" and doc["schema_version"] == 1 and doc["smoke"] is False and doc["reps_per_side"] == 40
    assert doc["plan_sha256"] == an.plan_sha256() and doc["criteria_sha256"] == an.criteria_sha256()
    assert doc["code_sha256"] == an.code_sha256() and sorted(doc["code_sha256"]) == sorted(an.CODE_FILES)
    assert doc["ladder"] == an.ladder(*ARM) and sorted(doc["timing_order"]) == [p["d"] for p in doc["points"]]
    assert [p["d"] for p in doc["points"]] == sorted(p["d"] for p in doc["points"])
    p = next(x for x in doc["points"] if x["d"] == 52)
    assert p["roles"] == ["fit", "study_l1"] and p["d_mod_8"] == 4 and p["working_set_bytes"] == 12 * 52 * 52
    assert p["l1_resident"] is True
    assert next(x for x in doc["points"] if x["d"] == 209)["l1_resident"] is False
    assert next(x for x in doc["points"] if x["d"] == 108)["roles"] == ["bridge"]
    for col in ("as_compiled", "aligned"):
        assert len(p[col]["none_ns"]) == len(p[col]["fast_ns"]) == 40 and p[col]["checksum_match"]
        for k in an.PAIR_KEYS:
            assert k in p[col]
    assert doc["aa"]["d"] == doc["ladder"]["mid_d"] == 36 and len(doc["aa"]["a_ns"]) == 40
    for m in an.MODES:
        for k in an.BUILD_KEYS:
            assert k in doc["builds"][m]
        assert doc["builds"][m]["interleave"] == 2 and doc["builds"][m]["elements_per_pass"] == 8
    assert doc["builds"]["fast"]["hot_loop"]["simd"] is True and doc["builds"]["fast"]["inner_loops"]
    json.dumps(doc, allow_nan=False)
    # removing or breaking things is caught, with a plain message
    for mutate, text in ((lambda d: d.pop("aa"), "missing aa"), (lambda d: d.update(kind="x"), "kind"),
                         (lambda d: d["points"][0].pop("instr"), "missing instr"),
                         (lambda d: d["aa"].update(d=44), "middle d"),
                         (lambda d: d.pop("code_sha256"), "missing code_sha256"),
                         (lambda d: d["code_sha256"].update({"harness/run.py": "nope"}), "code_sha256"),
                         (lambda d: d["builds"]["none"].pop("elements_per_pass"), "builds.none"),
                         (lambda d: d["machine"]["cache_bytes"].update(l1d=32 * 1024), "ladder")):
        broken = json.loads(json.dumps(doc))
        mutate(broken)
        probs = an.validate_doc(broken)
        assert probs and any(text in p for p in probs), (text, probs)
    assert an.validate_doc("not a dict") and an.validate_doc({}) and an.validate_doc({"kind": "dsweep"})


def test_the_elements_per_pass_of_the_none_loop_must_divide_the_ladder_step():
    assert sw.vector_step({"vectorized": True, "width": 4, "remarks": [STEP_REMARK]}) == (2, 8)
    assert sw.vector_step({"vectorized": True, "width": 2, "remarks": [
        "vectorized loop (vectorization width: 2, interleaved count: 4) [-Rpass=loop-vectorize]"]}) == (4, 8)
    assert sw.vector_step({"vectorized": False, "width": None, "remarks": ["the cost-model indicates ..."]}) == (None, None)
    assert sw.vector_step({"vectorized": True, "width": 4, "remarks": []}) == (None, None)
    assert sw.vector_step(None) == (None, None)
    for step, fine in ((8, True), (4, True), (2, True), (1, True), (None, True), (16, False), (3, False), (12, False)):
        doc = fake_doc(1, "h1")
        doc["builds"]["none"]["elements_per_pass"] = step
        probs = an.validate_doc(doc)
        assert (probs == []) == fine, (step, probs)
        if not fine:
            assert any("elements per pass" in p for p in probs), probs
    # a remark with a wider pass yields the file problem through the writer, end to end
    wide = "vectorized loop (vectorization width: 4, interleaved count: 4) [-Rpass=loop-vectorize]"
    assert any("16 elements per pass" in p for p in an.validate_doc(fake_doc(1, "h1", remark=wide)))
    # the stored clang remarks of the Neoverse-N2 and the x86-64 jobs say 4 x 2 for the NONE loop
    for rel, text in (("results/s8-arm-run-38905055834/results-neoverse-n2-j1/remarks/k08_matmul.none.txt", "Neoverse"),
                      ("results/s6-run-38674961339/results-amd-epyc-9v45-96-core-processor-j10/remarks/k08_matmul.none.txt", "x86")):
        path = os.path.join(REPO, rel)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                vec = remarks.vectorization(f.read(), "kernels/k08_matmul.cpp", 11)
            assert sw.vector_step(vec) == (2, 8), text


def test_a_checksum_difference_is_a_file_problem():
    doc = fake_doc(1, "h1", bad_checksum=True)
    assert any("checksum" in p for p in an.validate_doc(doc))
    fp = pair(random.Random(1), 100.0, 0.01, 4)
    ap = dict(pair(random.Random(2), 100.0, 0.01, 4), a_checksums=["beef"], b_checksums=["beef"])
    pt = sw.make_point(12, ["fit"], ARM[0], 10, 1.0, fp, ap, None, "x", SHAS, summarize=cheap_summary)
    assert pt["checksum_match"] is False, "the aligned builds must print the same checksum as the as-compiled ones"
    assert pt["instr"] is None and pt["instr_note"] == "x"


def test_smoke_files_are_marked_and_refused():
    doc = fake_doc(1, "h1", reps=4, smoke=True)
    probs = an.validate_doc(doc)
    assert any("smoke" in p for p in probs) and any("reps_per_side 4" in p for p in probs)
    assert probs[0].startswith("a smoke file")
    assert an.validate_doc(doc, reps=4) == [probs[0]], "against its own repetition count the only problem left is the smoke mark"
    b = analyse_items([(f"j{j}", fake_doc(j, "h1", reps=4, smoke=True)) for j in range(1, 6)])
    assert b["verdict"]["word"] == an.NEITHER and any("smoke" in p for p in b["problems"])


def test_verify_job_recomputes_the_stored_intervals():
    doc = real_doc(8, smoke=True)
    assert an.verify_job(doc) == []
    doc["points"][3]["aligned"]["ci95"][1] += 1e-9
    probs = an.verify_job(doc)
    assert len(probs) == 1 and "aligned" in probs[0] and "ci95" in probs[0]
    doc["points"][3]["aligned"]["ci95"][1] -= 1e-9
    doc["aa"]["ratio"] += 1e-6
    assert len(an.verify_job(doc)) == 1


def test_verify_on_the_command_line_passes_a_good_file_and_fails_a_tampered_one():
    with tempfile.TemporaryDirectory() as tmp:
        doc = real_doc(8)
        write_json(os.path.join(tmp, "j1", "dsweep.json"), doc)
        with patched((an, "reps_per_side", lambda: 8)):
            good = io.StringIO()
            with contextlib.redirect_stdout(good):
                assert an.main([tmp, "--verify"]) == 0
            assert "verified 1 file(s): 0 with problems" in good.getvalue()
            doc["points"][2]["as_compiled"]["ci95"][0] -= 0.001
            write_json(os.path.join(tmp, "j1", "dsweep.json"), doc)
            bad = io.StringIO()
            with contextlib.redirect_stdout(bad):
                assert an.main([tmp, "--verify"]) == 1
            assert "stored ci95" in bad.getvalue() and "1 with problems" in bad.getvalue()


def test_find_files_loads_each_distinct_file_once_in_a_fixed_order():
    with tempfile.TemporaryDirectory() as tmp:
        for j in (2, 1, 3):
            sub = os.path.join(tmp, "run", f"dsweep-job-x-j{j}")
            write_json(os.path.join(sub, "dsweep.json"), {"kind": "dsweep", "j": j, "run": {"id": "r", "job": str(j)}})
        write_json(os.path.join(tmp, "run", "copy", "dsweep.json"), {"kind": "dsweep", "j": 1, "run": {"id": "r", "job": "1"}})
        entries = an.load_entries([tmp], tmp)
        assert len(entries) == 3, "the byte-identical copy counts once"
        assert [e[1]["j"] for e in entries] == [1, 2, 3]
        assert [e[0] for e in entries] in (
            ["run/copy/dsweep.json", "run/dsweep-job-x-j2/dsweep.json", "run/dsweep-job-x-j3/dsweep.json"],
            ["run/dsweep-job-x-j1/dsweep.json", "run/dsweep-job-x-j2/dsweep.json", "run/dsweep-job-x-j3/dsweep.json"]), \
            "one of the two identical files is kept, the rest in job order"


def test_command_line_end_to_end_with_the_full_resamples():
    with tempfile.TemporaryDirectory() as tmp:
        for rel, doc in jobs_of("h1", n=3):
            write_json(os.path.join(tmp, "matrix", rel.split("/")[1], "dsweep.json"), doc)
        out, md = os.path.join(tmp, "matrix", "dsweep-pooled.json"), os.path.join(tmp, "matrix", "dsweep-pooled.md")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = an.main([os.path.join(tmp, "matrix"), "--out", out, "--md", md])
        assert code == 0 and "[cpu] Neoverse-N2: H1 (3 jobs" in buf.getvalue()
        with open(out, encoding="utf-8") as f:
            pooled = json.load(f)
        assert pooled["kind"] == "dsweep-pooled" and pooled["resamples"] == 2000 and pooled["seed_prefix"] == "20261011"
        assert pooled["cpus"][0]["verdict"]["word"] == "H1" and pooled["rule"] == an.RULE
        assert pooled["code_sha256"] == an.code_sha256() and pooled["plan_file"] == "dsweep/PLAN.md"
        assert pooled["incomplete_jobs"] == [] and pooled["cpus"][0]["code_changed_since_run"] == []
        assert [i["job"] for i in pooled["inputs"]] == ["1", "2", "3"]
        with open(md, encoding="utf-8") as f:
            assert f.read().startswith("### Neoverse-N2: H1")
        os.makedirs(os.path.join(tmp, "empty"))
        empty = io.StringIO()
        with contextlib.redirect_stdout(empty):
            assert an.main([os.path.join(tmp, "empty")]) == 1
        assert "no dsweep.json found" in empty.getvalue()
        try:
            an.main([os.path.join(tmp, "nothing-here")])
        except SystemExit as e:
            assert "neither a file nor a folder" in str(e)
        else:
            raise AssertionError("a path that does not exist must stop with a plain message")


# ---------------------------------------------------------------- the sweep runner, with the harness faked

@contextlib.contextmanager
def faked_harness(reps=4, break_at=None, raise_at=None, fast_ratio=1.5, remark=STEP_REMARK, missing=None):
    """harness/run.py with no compiler, no Linux and no valgrind: build_kernel writes tiny files, pair() returns
    generated samples. The sweep's own code (sweep.run_sweep and main) runs for real."""
    rng = random.Random(5)
    calls = []

    def build_kernel(kernel, build_dir, out_dir):
        info = fake_info(remark=remark)
        for m in sw.an.MODES:
            p = os.path.join(build_dir, f"{kernel}.{m}")
            if m != missing:
                with open(p, "wb") as f:
                    f.write(f"binary {m}".encode())
            info["builds"][m]["binary"] = p
        info["diff"], info["diff_aligned"] = "--- none\n+++ fast\n", "--- none_a64\n+++ fast_a64\n"
        return info

    def pair_fn(a, b, args, nreps, cpu):
        d, bb = args[0], os.path.basename(b)
        calls.append((os.path.basename(a), bb, d))
        if raise_at == d and "fast" in bb:
            raise RuntimeError("fake: a timed process exited 1")
        pr = pair(rng, 0.1357 * d * d, 0.002, nreps, fast_ratio if "fast" in bb else 1.0)
        if break_at == d and "fast" in bb and "a64" not in bb:
            pr["b_checksums"], pr["checksum_match"] = ["dead"], False
        return pr

    runner = {"os": "Fake", "kernel": "k", "arch": "aarch64", "cpu_model": "Fake-N2", "cores": 4, "l1d_kib": 64,
              "l2_kib": 1024, "l3_kib": 32768}
    with patched((an, "reps_per_side", lambda: reps),
                 (hr, "caches", lambda: {"l1d": ARM[0], "l2": ARM[1], "l3": 32 << 20, "llc": 32 << 20}),
                 (hr, "runner_info", lambda cache: (dict(runner), "lscpu text")),
                 (hr, "toolchain", lambda: {"clang": "18.1.3", "libcxx_package": None}),
                 (hr, "build_kernel", build_kernel),
                 (hr, "calibrate", lambda binary, n, cpu: (1000, 1.0)),
                 (hr, "pair", pair_fn),
                 (hr, "instr_count", lambda binary, kernel, n, out_dir, tag:
                  (n * n * (20 + n) + (0 if "none" in tag else n * n * 77), "ok"))):
        yield calls


def test_run_sweep_end_to_end_with_a_faked_harness():
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        with faked_harness(reps=4) as calls:
            assert sw.main(["--job", "3", "--out", out, "--build", build]) == 0
            with open(os.path.join(out, "dsweep.json"), encoding="utf-8") as f:
                doc = json.load(f)
            assert an.validate_doc(doc) == [], an.validate_doc(doc)
            verify = io.StringIO()
            with contextlib.redirect_stdout(verify):
                assert an.main([out, "--verify"]) == 0, verify.getvalue()
        lad = an.ladder(*ARM)
        roles = an.roles_of(lad)
        assert doc["smoke"] is False and doc["reps_per_side"] == 4 and len(doc["points"]) == len(roles) == 17
        assert doc["timing_order"] == sw.timing_order("3", list(roles)) and sorted(doc["timing_order"]) == sorted(roles)
        assert [p["d"] for p in doc["points"]] == sorted(roles)
        assert doc["aa"]["d"] == lad["mid_d"] and doc["aa"]["binary_sha256"] == hr.sha256(os.path.join(build, "k08_matmul.none"))
        assert doc["plan_sha256"] == an.plan_sha256() and doc["code_sha256"] == an.code_sha256()
        assert doc["run"]["job"] == "3" and doc["run"]["runner"]["cpu_model"] == "Fake-N2"
        assert all(p["instr"]["fast"] > p["instr"]["none"] for p in doc["points"])
        assert len(calls) == 2 * 17 + 1, "two pairs per d and one A/A"
        assert sum(1 for c in calls if c[1] == "k08_matmul.none_copy") == 1
        # the d values were timed in the stored order
        seen = []
        for c in calls:
            if not seen or seen[-1] != c[2]:
                seen.append(c[2])
        assert seen == doc["timing_order"]
        assert not os.path.exists(os.path.join(out, an.PARTIAL_NAME)), "the partial file goes once dsweep.json is written"
        for name in ("k08_matmul.diff", "k08_matmul.aligned.diff"):
            assert os.path.exists(os.path.join(out, "asm", name))
        # the file is a result the analysis accepts as far as the file goes (one job: too few to pool)
        b = an.analyse_cpu("Fake-N2", [("j3", doc)], an.plan_sha256(), an.criteria_sha256(), resamples=RES)
        assert b["problems"] == [] or all("smoke" not in p and "plan hash" not in p for p in b["problems"]), b["problems"]


def test_run_sweep_marks_a_file_made_with_other_repetitions_as_smoke():
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        with faked_harness(reps=4):
            assert sw.main(["--job", "1", "--out", out, "--build", build, "--reps", "6"]) == 0
        with open(os.path.join(out, "dsweep.json"), encoding="utf-8") as f:
            doc = json.load(f)
        assert doc["smoke"] is True and doc["reps_per_side"] == 6
        assert an.validate_doc(doc, reps=6) == ["a smoke file (fewer repetitions than harness/criteria-v3.json): not a result"]


def test_a_job_that_stops_late_keeps_the_d_values_it_timed():
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        lad = an.ladder(*ARM)
        roles = an.roles_of(lad)
        order = sw.timing_order("3", list(roles))
        stop = order[9]                                          # a late d, ten points in
        with faked_harness(reps=4, break_at=stop):
            try:
                sw.main(["--job", "3", "--out", out, "--build", build])
            except SystemExit as e:
                assert "different checksums" in str(e) and f"d = {stop}" in str(e)
            else:
                raise AssertionError("a checksum mismatch must stop the job")
        assert not os.path.exists(os.path.join(out, "dsweep.json"))
        with open(os.path.join(out, an.PARTIAL_NAME), encoding="utf-8") as f:
            recs = [json.loads(x) for x in f if x.strip()]
        assert recs[0]["kind"] == "dsweep-partial" and recs[0]["points_expected"] == 17 and recs[0]["timing_order"] == order
        assert recs[0]["plan_sha256"] == an.plan_sha256() and recs[0]["run"]["job"] == "3"
        done = [r["point"]["d"] for r in recs if "point" in r]
        assert done == order[:10], "every d up to and including the one that failed was written"
        assert set(recs[-1]) == {"point"} and recs[-1]["point"]["checksum_match"] is False
        inc = an.find_incomplete([out], tmp)
        assert len(inc) == 1 and inc[0]["points_done"] == 10 and inc[0]["points_expected"] == 17
        assert inc[0]["last_d_started"] == stop and inc[0]["d_done"] == order[:10]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert an.main([out]) == 1
        assert "[incomplete]" in buf.getvalue() and "10 of 17" in buf.getvalue()


def test_a_failed_timed_process_stops_the_job_with_a_plain_message_and_keeps_the_partial_file():
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        order = sw.timing_order("2", list(an.roles_of(an.ladder(*ARM))))
        with faked_harness(reps=4, raise_at=order[2]):
            try:
                sw.main(["--job", "2", "--out", out, "--build", build])
            except SystemExit as e:
                assert "a timed process failed" in str(e)
            else:
                raise AssertionError("a failed kernel process must stop the job")
        inc = an.find_incomplete([out], tmp)
        assert len(inc) == 1 and inc[0]["points_done"] == 2 and inc[0]["last_d_started"] == order[2]


def test_the_a_a_copy_must_be_byte_identical_and_a_missing_binary_stops_the_job():
    original = hr.sha256
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        with faked_harness(reps=4):
            with patched((hr, "sha256", lambda p: original(p) if not p.endswith("none_copy") else "0" * 64)):
                try:
                    sw.main(["--job", "1", "--out", out, "--build", build])
                except SystemExit as e:
                    assert "not byte-identical" in str(e)
                else:
                    raise AssertionError("an A/A copy that differs must stop the job")
        assert not os.path.exists(os.path.join(out, "dsweep.json"))
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        with faked_harness(reps=4, missing="fast_a64"):
            try:
                sw.main(["--job", "1", "--out", out, "--build", build])
            except SystemExit as e:
                assert "fast_a64 binary is missing" in str(e)
            else:
                raise AssertionError("a missing binary must stop the job before anything is timed")
        assert not os.path.exists(os.path.join(out, an.PARTIAL_NAME)), "nothing was timed, so there is no partial file"


# ---------------------------------------------------------------- the workflow

def test_workflow_structure():
    import yaml
    with open(os.path.join(REPO, ".github", "workflows", "dsweep.yml"), encoding="utf-8") as f:
        wf = yaml.safe_load(f)
    on = wf.get("on") if "on" in wf else wf.get(True)
    inputs = on["workflow_dispatch"]["inputs"]
    assert inputs["runner"]["default"] == "ubuntu-24.04" and inputs["runner"]["options"] == ["ubuntu-24.04", "ubuntu-24.04-arm"]
    assert json.loads(inputs["jobs"]["default"]) == [1, 2, 3, 4, 5, 6]
    assert inputs["reps"]["default"] == "" and "SMOKE" in inputs["reps"]["description"]
    assert wf["permissions"] == {"contents": "read"}
    sweep, pooljob = wf["jobs"]["sweep"], wf["jobs"]["pool"]
    assert sweep["runs-on"] == "${{ inputs.runner }}" and sweep["timeout-minutes"] == 45
    assert sweep["strategy"]["fail-fast"] is False and "fromJSON(inputs.jobs)" in sweep["strategy"]["matrix"]["job"]
    steps = sweep["steps"]
    names = [s.get("name", s.get("uses", "")) for s in steps]
    run_idx = next(i for i, s in enumerate(steps) if "dsweep/sweep.py --job" in s.get("run", ""))
    up_idx = next(i for i, s in enumerate(steps) if "upload-artifact" in s.get("uses", ""))
    assert up_idx == run_idx + 1, "the upload comes right after the sweep"
    assert steps[up_idx]["if"] == "always()" and steps[up_idx]["with"]["path"] == "out/"
    assert steps[up_idx]["with"]["name"].startswith("dsweep-job-")
    # the job number and the repetitions reach the shell through env, not through the text of the script
    run_step = steps[run_idx]
    assert "${{" not in run_step["run"] and run_step["env"] == {"JOB": "${{ matrix.job }}", "REPS": "${{ inputs.reps }}"}
    assert '--reps "$REPS"' in run_step["run"] and "--job \"$JOB\"" in run_step["run"]
    # the offline self-test runs this file before anything is timed; every check of the RESULTS comes after the upload
    offline = [i for i, s in enumerate(steps) if "tests/test_dsweep.py" in s.get("run", "")]
    assert len(offline) == 1 and offline[0] < run_idx, "the self-test runs before the timing"
    assert "python3-yaml" in steps[offline[0]]["run"]
    for i, s in enumerate(steps):
        text = (s.get("name", "") + " " + s.get("run", "")).lower()
        if i == offline[0]:
            continue
        if "analyze.py" in text or "check" in text.replace("runner cpu (read every result against this)", ""):
            assert i > up_idx, f"step {names[i]!r} is a check and must come after the upload"
    # the toolchain and CPU steps are measure.yml's
    with open(os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        measure = yaml.safe_load(f)
    m_steps = {s.get("name"): s for s in measure["jobs"]["measure"]["steps"]}
    s_steps = {s.get("name"): s for s in steps}
    assert s_steps["Runner CPU (read every result against this)"]["run"] == m_steps["Runner CPU (read every result against this)"]["run"]
    install = "Install clang-18, libc++-18, valgrind and numpy (Ubuntu noble apt)"
    assert s_steps[install]["run"] == m_steps[install]["run"]
    assert "lscpu | sed -n 's/^Model name: *//p'" in s_steps["Runner CPU (read every result against this)"]["run"], "the Arm fallback for the CPU name"
    # a smoke run is never pooled; the pool job reads partial files too
    assert pooljob["needs"] == "sweep" and pooljob["if"] == "always() && inputs.reps == ''" and pooljob["runs-on"] == "ubuntu-24.04"
    uploads = [s for s in pooljob["steps"] if "upload-artifact" in s.get("uses", "")]
    assert len(uploads) == 1 and uploads[0]["with"]["name"] == "dsweep-pooled" and "dsweep-pooled.json" in uploads[0]["with"]["path"]
    pool_run = " ".join(s.get("run", "") for s in pooljob["steps"])
    assert "dsweep/analyze.py matrix --out matrix/dsweep-pooled.json" in pool_run
    assert pool_run.count("python3 dsweep/analyze.py matrix |") == 1, "when no job wrote a result the partial jobs are listed"
    install_idx = next(i for i, s in enumerate(pooljob["steps"]) if "python3-numpy" in s.get("run", ""))
    first_analysis = next(i for i, s in enumerate(pooljob["steps"]) if "analyze.py" in s.get("run", ""))
    assert install_idx < first_analysis, "numpy is installed before the first analysis"
    downloads = [s for s in pooljob["steps"] if "download-artifact" in s.get("uses", "")]
    assert downloads and downloads[0]["with"]["pattern"] == "dsweep-job-*"


def run_all_tests():
    """`python3 tests/test_dsweep.py`: every test_* function in the order of the file (plain Python, no pytest)."""
    names = [n for n, f in list(globals().items()) if n.startswith("test_") and callable(f)]
    failed = []
    for n in names:
        try:
            globals()[n]()
            print(f"ok    {n}", flush=True)
        except Exception:
            failed.append(n)
            traceback.print_exc()
            print(f"FAIL  {n}", flush=True)
    print(f"{len(names) - len(failed)} passed, {len(failed)} failed" + (": " + ", ".join(failed) if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
