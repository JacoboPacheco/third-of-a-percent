"""robustness/seeds_x86.py and robustness/seed-sensitivity-x86.json: the x86-64 pool's borderline cells re-drawn under 400
other bootstrap seeds, and the whole analysis of the models that have such a cell under 60 of them.

Three kinds of test.

Stored data. The file's pool hashes are those of the pool it reads; the cells it covers are the ones the selection rule picks
(the rule is written out again here, from results/s7-pooled/pooled.json alone); every number the file derives from its
per-seed lists (summaries, shares, percentiles, tallies, the converged margin) is recomputed here by this file's own code.

Recomputation. One cell's stored-seed numbers and its first alternative seeds are rebuilt from the jobs' own samples with
harness/pool.py's function (this file's own loading and sides, not the script's), and the script's --verify path is run on
a sample.

Tamper. A stored number changed in a temporary copy of the file (a per-seed value, a summary, a whole-analysis row, the
selection screen) makes the checks fail.

Offline and read-only (the tamper tests write to a temporary folder). No fixtures, so scripts/check.py's built-in runner
runs it. About one minute."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import sys
import tempfile
from functools import lru_cache

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402

POOLED = os.path.join(REPO, "results", "s7-pooled", "pooled.json")
STORED = os.path.join(REPO, "robustness", "seed-sensitivity-x86.json")
CRITERIA = os.path.join(REPO, "harness", "criteria-v3.json")
NEAR = 0.01
XEON6973 = "Intel(R) Xeon(R) 6973P-C"
XEON8573 = "INTEL(R) XEON(R) PLATINUM 8573C"
EPYC9V45 = "AMD EPYC 9V45 96-Core Processor"


def _load():
    key = "seeds_x86_under_test"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, "robustness", "seeds_x86.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


S = _load()


def read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha_lf(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(bytes([13, 10]), bytes([10]))).hexdigest()


@lru_cache(None)
def stored():
    return read(STORED)


@lru_cache(None)
def pooled():
    return read(POOLED)


@lru_cache(None)
def criteria():
    return read(CRITERIA)


def block(cpu):
    return next(b for b in pooled()["cpus"] if b["cpu_model"] == cpu)


@lru_cache(None)
def jobs(cpu):
    """The job documents of one CPU model in the order of pooled.json's inputs (this file's own loading)."""
    base = os.path.dirname(POOLED)
    return tuple(read(os.path.join(base, i["path"])) for i in pooled()["inputs"] if i["cpu_model"] == cpu)


def sides(cpu, cid, kind):
    out = []
    for d in jobs(cpu):
        c = next(x for x in d["cells"] if x["cell_id"] == cid)
        a = c["aligned"]
        out.append([a["none_ns"], a["fast_ns"]] if kind == "forward" else [c["none_ns"], c["fast_ns"], a["none_ns"], a["fast_ns"]])
    return out


def ratio_fn(kind):
    return (lambda ma, mb: mb / ma) if kind == "forward" else (lambda n, f, na, fa: (f / n) / (fa / na))


def under(prefix, cpu, cid, kind):
    """pool.pooled_stat of one statistic under a seed prefix, from this file's own sides."""
    old = pool.SEED_PREFIX
    pool.SEED_PREFIX = prefix
    try:
        return pool.pooled_stat(cpu, f"{cid}|{'aligned' if kind == 'forward' else 'placement'}", sides(cpu, cid, kind),
                                ratio_fn(kind), pool.RESAMPLES)
    finally:
        pool.SEED_PREFIX = old


def selection_again():
    """The selection rule of the script's header, applied again to pooled.json: [(cpu, kind, cell_id)] in file order."""
    crit = criteria()["verdict"]
    mn = criteria()["v3"]["pooling"]["minimum_jobs"]
    out = []
    for b in pooled()["cpus"]:
        if b["jobs"] < mn:
            continue
        limit = 1.0 + b["verdict"]["forward_limit_pct"] / 100.0
        for c in b["cells"]:
            if c["size_class"] not in ("L1", "L2") or c["class"] != "kept":
                continue
            hi, ratio = c["aligned"]["ci95"][1], c["aligned"]["ratio"]
            p = c["placement"]
            near1 = min(abs(e - 1.0) for e in p["d"]["ci95"])
            if abs(hi - limit) <= NEAR:
                out.append((b["cpu_model"], "forward", c["cell_id"]))
            if p["mechanical"] and (hi >= limit - NEAR or ratio > crit["forward_point_max_ratio"]) and near1 <= NEAR:
                out.append((b["cpu_model"], "placement", c["cell_id"]))
    return out


# ---------------------------------------------------------------- stored data

def test_file_is_about_this_pool_and_this_rule_file():
    s = stored()
    assert s["kind"] == "seed-sensitivity-x86"
    assert s["pool"]["path"] == "results/s7-pooled/pooled.json"
    assert s["pool"]["sha256"] == sha_lf(POOLED), "the pool file changed: re-run robustness/seeds_x86.py --full"
    assert s["pool"]["criteria_sha256"] == pooled()["criteria_sha256"] == pool.criteria_and_sha()[1]
    assert s["pool"]["resamples"] == pool.RESAMPLES == pooled()["resamples"] == 2000
    assert s["pool"]["jobs"] == len(pooled()["inputs"]) == 95
    assert s["stored_seed"]["prefix"] == pool.SEED_PREFIX == "20261011" and s["stored_seed"]["resamples"] == 2000
    assert s["stored_seed"]["replica_matches"] is True
    assert s["stored_seed"]["reproduced"]["max_rel_diff"] < 1e-12
    a = s["alt_seeds"]
    assert a["count"] == 400 and a["resamples"] == 2000 and a["seed_list"] == [a["pattern"].format(i) for i in range(1, 401)]
    assert a["seed_list"][0] == "seedsens-001" and a["seed_list"][-1] == "seedsens-400"
    assert s["converged"]["resamples"] == s["converged"]["chunks"] * s["converged"]["resamples_per_chunk"] >= 100000
    assert s["whole"]["count"] == 60 and s["whole"]["prefixes"] == a["seed_list"][:60]


def test_the_models_are_those_with_enough_jobs():
    s = stored()
    mn = criteria()["v3"]["pooling"]["minimum_jobs"]
    assert mn == 3
    models = [(b["cpu_model"], b["jobs"], b["verdict"]["form"]) for b in pooled()["cpus"] if b["jobs"] >= mn]
    assert [(m["cpu_model"], m["jobs"], m["stored_form"]) for m in s["pool"]["models"]] == models
    assert [(m["cpu_model"], m["jobs"]) for m in s["selection"]["skipped_models"]] == \
        [(b["cpu_model"], b["jobs"]) for b in pooled()["cpus"] if b["jobs"] < mn]
    assert set(s["selection"]["screen"]) == {m[0] for m in models}
    for m in s["pool"]["models"]:
        assert m["forward_limit"] == 1.0 + block(m["cpu_model"])["verdict"]["forward_limit_pct"] / 100.0


def test_the_selected_cells_are_what_the_rule_picks():
    s = stored()
    want = selection_again()
    got = [(r["cpu_model"], r["kind"], r["cell_id"]) for r in s["cells"]]
    assert got == want, (got, want)
    assert len(got) == len(set(got)) > 0
    # the cells the brief for this piece names must be among them
    assert (XEON6973, "forward", "k03_stencil.L2") in got
    assert (EPYC9V45, "placement", "k03_stencil.L1") in got
    assert any(c == (XEON8573, "forward", "k03_stencil.L2") for c in got)
    # every screen row repeats pooled.json's numbers
    for cpu, rows in s["selection"]["screen"].items():
        b = block(cpu)
        by = {c["cell_id"]: c for c in b["cells"]}
        assert [r["cell_id"] for r in rows] == [c["cell_id"] for c in b["cells"] if c["size_class"] in ("L1", "L2") and c["class"] == "kept"]
        for r in rows:
            c = by[r["cell_id"]]
            assert r["aligned_hi"] == c["aligned"]["ci95"][1] and r["aligned_ratio"] == c["aligned"]["ratio"]
            assert r["d_ci95"] == c["placement"]["d"]["ci95"]
            assert r["judged"] == (c["cell_id"] not in {p["cell_id"] for p in b["verdict"]["placement_sensitive"]})
            assert r["selected"] == [k for k in ("forward", "placement") if (cpu, k, r["cell_id"]) in want]


def test_each_cell_repeats_the_pools_own_numbers():
    for r in stored()["cells"]:
        c = next(x for x in block(r["cpu_model"])["cells"] if x["cell_id"] == r["cell_id"])
        st = c["aligned"] if r["kind"] == "forward" else c["placement"]["d"]
        assert r["stored"]["ratio"] == st["ratio"] and r["stored"]["lo"] == st["ci95"][0] and r["stored"]["hi"] == st["ci95"][1]
        assert r["jobs"] == block(r["cpu_model"])["jobs"] == len(jobs(r["cpu_model"]))
        assert r["stored"]["exempt"] == (r["cell_id"] in {p["cell_id"] for p in block(r["cpu_model"])["verdict"]["placement_sensitive"]})
        assert r["alt"]["draws"] == len(r["alt"]["hi_list"]) == 400
        assert (len(r["alt"].get("lo_list", [])) == 400) == (r["kind"] == "placement")


def test_summaries_follow_from_the_per_seed_lists():
    s = stored()
    for r in s["cells"]:
        his = np.array(r["alt"]["hi_list"])
        sm = r["alt"]["summary"]
        assert all(math.isfinite(x) for x in his)
        key = "hi"
        assert sm[key]["n"] == 400
        assert sm[key]["min"] == his.min() and sm[key]["max"] == his.max()
        assert sm[key]["min"] <= sm[key]["median"] <= sm[key]["max"]
        assert math.isclose(sm[key]["median"], float(np.median(his)), rel_tol=1e-12)
        assert math.isclose(sm[key]["sd"], float(np.std(his, ddof=1)), rel_tol=1e-12) and sm[key]["sd"] > 0
        assert sm[key]["p05"] <= sm[key]["p10"] <= sm[key]["median"] <= sm[key]["p90"] <= sm[key]["p95"]
        pct = sm["stored_hi_percentile"]
        assert 0.0 <= pct <= 100.0
        below, equal = int((his < r["stored"]["hi"]).sum()), int((his == r["stored"]["hi"]).sum())
        assert math.isclose(pct, 100.0 * (below + equal / 2) / 400, rel_tol=1e-12)
        if r["kind"] == "forward":
            lim = sm["limit"]
            assert lim == next(m for m in s["pool"]["models"] if m["cpu_model"] == r["cpu_model"])["forward_limit"]
            assert sm["at_or_above_limit"] == int((his >= lim).sum()) and sm["above_limit"] == int((his > lim).sum())
            assert sm["above_limit"] <= sm["at_or_above_limit"] <= 400
            assert math.isclose(sm["share_at_or_above_limit"], sm["at_or_above_limit"] / 400)
            assert sm["above_stored"] == int((his > r["stored"]["hi"]).sum())
            cv = r["converged"]
            assert math.isclose(cv["margin_to_limit"], cv["hi"] - lim, abs_tol=1e-15) and cv["above_limit"] == (cv["hi"] > lim)
        else:
            los = np.array(r["alt"]["lo_list"])
            assert (los <= his).all()
            ex = int(((los > 1.0) | (his < 1.0)).sum())
            assert sm["excludes_1"] == ex and math.isclose(sm["share_excludes_1"], ex / 400)
            assert sm["excludes_1_above"] == int((los > 1.0).sum()) and sm["excludes_1_below"] == int((his < 1.0).sum())
            assert sm["excludes_1_above"] + sm["excludes_1_below"] == ex
            assert sm["lo"]["min"] == los.min() and sm["lo"]["max"] == los.max()
            assert r["converged"]["excludes_1"] == (r["converged"]["lo"] > 1.0 or r["converged"]["hi"] < 1.0)
        cv = r["converged"]
        assert cv["resamples"] == s["converged"]["resamples"] >= 100000
        assert cv["lo"] <= cv["hi"] and cv["mc_sd_hi"] > 0 and cv["mc_sd_lo"] > 0
        # the Monte Carlo sd of the converged end is the chunk sd over sqrt(chunks). The batch estimate is an order-of-magnitude
        # cross-check only: it is a standard deviation of 10 values (about a quarter of its own size in noise), and the
        # stored file's ratios run from 0.32 to 1.05, so the test asks for the same size within a factor of 4
        assert math.isclose(cv["mc_sd_hi"], cv["chunk_sd_hi"] / math.sqrt(s["converged"]["chunks"]), rel_tol=1e-9)
        assert cv["mc_sd_hi"] / 4 < cv["mc_sd_hi_from_batches"] < cv["mc_sd_hi"] * 4
        # the converged end lies inside the range the 400 single draws span, and within a few chunk sds of their median
        assert sm["hi"]["min"] - 3 * cv["chunk_sd_hi"] < cv["hi"] < sm["hi"]["max"] + 3 * cv["chunk_sd_hi"]


def test_whole_analyses_are_tallied_correctly():
    s = stored()
    cpus_with_cells = {r["cpu_model"] for r in s["cells"]}
    assert set(s["whole"]["models"]) == cpus_with_cells
    for cpu, w in s["whole"]["models"].items():
        b = block(cpu)
        assert w["jobs"] == b["jobs"] and w["stored_form"] == w["stored_seed_form"] == b["verdict"]["form"]
        assert w["stored_placement_sensitive"] == sorted(p["cell_id"] for p in b["verdict"]["placement_sensitive"])
        ps = w["per_seed"]
        assert [p["prefix"] for p in ps] == s["whole"]["prefixes"] and len(ps) == 60
        t = w["tally"]
        forms = {}
        for p in ps:
            forms[p["form"]] = forms.get(p["form"], 0) + 1
        assert t["count"] == 60 and t["forms"] == forms and sum(forms.values()) == 60
        assert math.isclose(sum(t["form_shares"].values()), 1.0) and all(math.isclose(t["form_shares"][k], v / 60) for k, v in forms.items())
        assert sum(x["seeds"] for x in t["placement_sets"]) == 60
        for cid, n in t["forward_missed_counts"].items():
            assert n == sum(1 for p in ps if cid in p["forward_missed"]) > 0
        # a form other than MAP needs a reason: a forward cell missing the rule, or a lost cell, or the A/A control
        for p in ps:
            if p["form"] != "map":
                assert p["forward_missed"] or p["lost_missed"] or p["aa_half_width_pct"] > criteria()["verdict"]["aa_half_width_max_pct"]
        # seeds 1 to 60: the whole analysis and the single-cell draw are the same draw
        for r in s["cells"]:
            if r["cpu_model"] != cpu:
                continue
            for i, p in enumerate(ps):
                got = p["selected"][f"{r['cell_id']}|{r['kind']}"]
                if r["kind"] == "forward":
                    assert math.isclose(got, r["alt"]["hi_list"][i], rel_tol=1e-12)
                else:
                    assert math.isclose(got[0], r["alt"]["lo_list"][i], rel_tol=1e-12) and math.isclose(got[1], r["alt"]["hi_list"][i], rel_tol=1e-12)


def test_the_readings_the_summary_leans_on():
    """The numbers README-seeds-x86.md reads from the file, restated as assertions so that a regenerated file that says
    something else fails here and the document gets re-read."""
    s = stored()
    rows = {(r["cpu_model"], r["kind"], r["cell_id"]): r for r in s["cells"]}
    d = rows[(XEON6973, "forward", "k03_stencil.L2")]
    block6973 = next(c for c in block(XEON6973)["cells"] if c["cell_id"] == "k03_stencil.L2")
    limit = 1.0 + block(XEON6973)["verdict"]["forward_limit_pct"] / 100.0
    assert d["stored"]["judged"] and d["stored"]["hi"] == block6973["aligned"]["ci95"][1] < limit
    # the stored margin is the one the pages quote; it is the stored seed's alone: the stored end sits low among the 400,
    # and the converged end is still under the limit by less than one run's spread
    assert round(limit - d["stored"]["hi"], 4) == 0.0016
    sm = d["alt"]["summary"]
    assert sm["stored_hi_percentile"] < 15.0 and sm["at_or_above_limit"] == 73 and sm["hi"]["median"] > d["stored"]["hi"]
    assert -0.0006 < d["converged"]["margin_to_limit"] < -0.0002 and d["converged"]["above_limit"] is False
    assert d["converged"]["mc_sd_hi"] < abs(d["converged"]["margin_to_limit"]) / 2
    assert sm["hi"]["sd"] > abs(d["converged"]["margin_to_limit"])
    w = s["whole"]["models"][XEON6973]
    assert set(w["tally"]["forms"]) <= {"map", "inconclusive"}
    assert w["stored_form"] == "map" and w["tally"]["forms"] == {"map": 47, "inconclusive": 13}
    assert w["tally"]["forward_missed_counts"] == {"k03_stencil.L2": 13}
    # the 8573C is INCONCLUSIVE under every other seed, through the forward-add cell, which no seed exempts
    assert s["whole"]["models"][XEON8573]["tally"]["forms"] == {"inconclusive": 60}
    assert s["whole"]["models"][XEON8573]["tally"]["forward_missed_counts"] == {"k02_add_fwd.L1": 60}
    assert rows[(XEON8573, "placement", "k02_add_fwd.L1")]["alt"]["summary"]["excludes_1"] == 0
    # the 9V45's placement statistic: stored upper end below 1, and the seeds that put it at or above 1
    p = rows[(EPYC9V45, "placement", "k03_stencil.L1")]
    assert p["stored"]["hi"] < 1.0 and p["stored"]["exempt"]
    assert p["alt"]["summary"]["excludes_1_above"] == 0 and p["alt"]["summary"]["excludes_1"] == 400
    assert s["whole"]["models"][EPYC9V45]["tally"]["forms"] == {"map": 60}
    # its aligned end is at or above the limit in most seeds, so the word rests on the exemption
    f9 = rows[(EPYC9V45, "forward", "k03_stencil.L1")]
    assert not f9["stored"]["judged"] and f9["alt"]["summary"]["at_or_above_limit"] == 366
    # the models without a cell near a line
    assert {r["cpu_model"] for r in s["cells"]} == {XEON6973, XEON8573, EPYC9V45}


# ---------------------------------------------------------------- recomputation

def test_stored_seed_numbers_of_every_selected_cell_come_back_exactly():
    for r in stored()["cells"][:]:
        if r["jobs"] > 10:
            continue                                   # the two large models are covered by the script's own --verify
        got = under(pool.SEED_PREFIX, r["cpu_model"], r["cell_id"], r["kind"])
        assert got["ratio"] == r["stored"]["ratio"] and got["ci95"] == [r["stored"]["lo"], r["stored"]["hi"]], r["id"]


def test_one_cell_under_the_first_alternative_seeds_is_rebuilt_from_the_jobs_samples():
    r = next(x for x in stored()["cells"] if (x["cpu_model"], x["kind"], x["cell_id"]) == (XEON6973, "forward", "k03_stencil.L2"))
    for i in (1, 2, 3, 17, 40):
        got = under(f"seedsens-{i:03d}", r["cpu_model"], r["cell_id"], r["kind"])
        assert math.isclose(got["ci95"][1], r["alt"]["hi_list"][i - 1], rel_tol=1e-12), i
    r = next(x for x in stored()["cells"] if x["kind"] == "placement" and x["cpu_model"] == XEON6973)
    for i in (1, 2):
        got = under(f"seedsens-{i:03d}", r["cpu_model"], r["cell_id"], r["kind"])
        assert math.isclose(got["ci95"][0], r["alt"]["lo_list"][i - 1], rel_tol=1e-12)
        assert math.isclose(got["ci95"][1], r["alt"]["hi_list"][i - 1], rel_tol=1e-12)


@lru_cache(None)
def conv6973():
    return S.converged(S.data().model(XEON6973), "forward", "k03_stencil.L2")


def test_the_converged_reading_of_the_deciding_cell_is_rebuilt():
    r = next(x for x in stored()["cells"] if (x["cpu_model"], x["kind"], x["cell_id"]) == (XEON6973, "forward", "k03_stencil.L2"))
    assert S.same(conv6973(), r["converged"]) is None


def run_main(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = S.main(list(args))
    return code, buf.getvalue()


SAMPLE = ("--verify", "--model", "6973P", "--seeds", "12", "--whole", "2")


def test_verify_path_passes_on_the_stored_file():
    code, out = run_main(*SAMPLE)
    assert code == 0 and "equals the recomputation of its sample" in out, out
    code, out = run_main("--verify", "--model", "8573C", "--seeds", "5", "--whole", "1")
    assert code == 0, out


# ---------------------------------------------------------------- the document robustness/README-seeds-x86.md

README = os.path.join(REPO, "robustness", "README-seeds-x86.md")
NUMBER_4DP = re.compile(r"\d+\.\d{4}\b")


def allowed_numbers(doc):
    """Every 4-decimal number the document may print: the stored values of its tables and the margins between them."""
    ok = set()
    lim = {m["cpu_model"]: m["forward_limit"] for m in doc["pool"]["models"]}
    for r in doc["cells"]:
        sm, cv, st = r["alt"]["summary"], r["converged"], r["stored"]
        ok.update(f"{x:.4f}" for x in (st["lo"], st["hi"], sm["hi"]["min"], sm["hi"]["max"], sm["hi"]["median"], sm["hi"]["sd"],
                                       cv["lo"], cv["hi"]))
        if "lo" in sm:
            ok.update(f"{x:.4f}" for x in (sm["lo"]["min"], sm["lo"]["max"]))
        if r["kind"] == "forward":
            ok.add(f"{lim[r['cpu_model']] - st['hi']:.4f}")
            ok.add(f"{abs(cv['margin_to_limit']):.4f}")
            ok.add(f"{cv['mc_sd_hi']:.4f}")
    return ok


def readme_problems(text, doc):
    """What is wrong in the document against a stored file: the three tables must be the ones the script prints, every
    4-decimal number must be a stored value or margin, and the sentences that carry the readings must carry the file's counts."""
    bad = []
    lines = set(text.splitlines())
    for name, rows in S.tables(doc).items():
        for line in rows:
            if line not in lines:
                bad.append(f"table {name}: missing or changed row: {line[:70]}")
    ok = allowed_numbers(doc)
    for n in sorted(set(NUMBER_4DP.findall(text))):
        if n not in ok and n != "1.0200":
            bad.append(f"number {n} is not a stored value")
    d = next(r for r in doc["cells"] if (r["cpu_model"], r["kind"], r["cell_id"]) == (XEON6973, "forward", "k03_stencil.L2"))
    f9 = next(r for r in doc["cells"] if (r["cpu_model"], r["kind"], r["cell_id"]) == (EPYC9V45, "forward", "k03_stencil.L1"))
    sm, t = d["alt"]["summary"], doc["whole"]["models"][XEON6973]["tally"]["forms"]
    want = [f"{d['stored']['hi']:.4f}, sits {1.02 - d['stored']['hi']:.4f} under the limit",
            f"about the {round(sm['stored_hi_percentile'])}th percentile",
            f"{sm['at_or_above_limit']} of the 400 other seeds end at or above 1.02",
            f"MAP in {t['map']} of the 60 other seeds and INCONCLUSIVE in {t['inconclusive']} of the 60",
            f"the end settles at {d['converged']['hi']:.4f}, which is {abs(d['converged']['margin_to_limit']):.4f} under the limit",
            f"Monte Carlo sd {d['converged']['mc_sd_hi']:.5f}",
            f"{doc['stored_seed']['reproduced']['numbers_checked']} numbers matched exactly",
            f"at or above 1.02 in {f9['alt']['summary']['at_or_above_limit']} of the 400 other seeds"]
    for w in want:
        if w not in text:
            bad.append(f"sentence missing: {w}")
    return bad


def test_the_document_agrees_with_the_stored_file():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    assert readme_problems(text, stored()) == []
    # the words it uses for the models it did not re-draw are the file's models
    assert "EPYC 7763 (29 jobs) and EPYC 9V74 (28 jobs)" in text
    assert {r["cpu_model"] for r in stored()["cells"]}.isdisjoint({"AMD EPYC 7763 64-Core Processor", "AMD EPYC 9V74 80-Core Processor"})


def test_the_tables_flag_prints_the_stored_files_tables():
    code, out = run_main("--tables")
    assert code == 0
    for rows in S.tables(stored()).values():
        assert all(line in out.splitlines() for line in rows)


def test_the_document_tampered_is_caught():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    for old, new in (("73 of the 400 other seeds end", "74 of the 400 other seeds end"),
                     ("MAP in 47 of the 60", "MAP in 48 of the 60"),
                     ("the end settles at 1.0196", "the end settles at 1.0197"),
                     ("sits 0.0016 under the limit", "sits 0.0017 under the limit"),
                     ("| 1.0197 to 1.0211 |", "| 1.0197 to 1.0212 |"),
                     ("about the 10th percentile", "about the 20th percentile"),
                     ("36 numbers matched exactly", "37 numbers matched exactly"),
                     ("at or above 1.02 in 366 of the 400", "at or above 1.02 in 365 of the 400")):
        assert text.count(old) == 1, old
        assert readme_problems(text.replace(old, new), stored()), old


# ---------------------------------------------------------------- tamper

def tampered(edit):
    """verify() on a temporary copy of the stored file after edit(copy) changed one thing: the list of differences it finds
    (the same sample as SAMPLE). The default path is the real file; the copy is the only thing written."""
    doc = copy.deepcopy(stored())
    edit(doc)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "seed-sensitivity-x86.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=1, sort_keys=True)
        return S.verify(path, model="6973P", seeds=6, whole=1)


def test_verify_exit_code_is_one_on_a_difference():
    def edit(doc):
        cell6973(doc)["alt"]["hi_list"][2] += 0.001
    doc = copy.deepcopy(stored())
    edit(doc)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "seed-sensitivity-x86.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=1, sort_keys=True)
        code, out = run_main("--verify", "--model", "6973P", "--seeds", "4", "--whole", "1", "--file", path)
    # the first difference printed is the one found while the file is checked against its own lists; "(and N more)" counts the rest
    assert code == 1 and out.startswith("FAIL") and "6973P-C|forward|k03_stencil.L2" in out and "more)" in out, out


def cell6973(doc):
    return next(r for r in doc["cells"] if (r["cpu_model"], r["kind"], r["cell_id"]) == (XEON6973, "forward", "k03_stencil.L2"))


def test_untouched_copy_passes_so_the_tampers_are_what_fails():
    doc = copy.deepcopy(stored())
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "seed-sensitivity-x86.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=1, sort_keys=True)
        assert S.verify(path, model="6973P", seeds=6, whole=1) == []


def test_tamper_a_per_seed_value_fails():
    def edit(doc):
        cell6973(doc)["alt"]["hi_list"][4] += 0.0005
    bad = tampered(edit)
    assert any("/alt/hi_list[4]" in b for b in bad), bad


def test_tamper_a_summary_number_fails():
    def edit(doc):
        cell6973(doc)["alt"]["summary"]["hi"]["median"] += 0.0005
    bad = tampered(edit)
    assert any("/summary/hi/median" in b for b in bad), bad


def test_tamper_a_share_fails():
    def edit(doc):
        cell6973(doc)["alt"]["summary"]["at_or_above_limit"] += 1
    bad = tampered(edit)
    assert any("/summary/at_or_above_limit" in b for b in bad), bad


def test_tamper_the_converged_margin_fails():
    # the sampled run with --seeds skips the converged reading (it is in the default --verify and in --verify --all);
    # this is the comparison those two make
    doc = copy.deepcopy(stored())
    cell6973(doc)["converged"]["hi"] -= 0.0005
    assert S.same(cell6973(doc)["converged"], conv6973()) is not None


def test_tamper_a_whole_analysis_row_fails():
    def edit(doc):
        w = doc["whole"]["models"][XEON6973]["per_seed"][0]
        w["form"] = "inconclusive" if w["form"] == "map" else "map"
    bad = tampered(edit)
    assert any("/whole/per_seed[0]/form" in b for b in bad), bad


def test_tamper_a_tally_fails():
    def edit(doc):
        t = doc["whole"]["models"][XEON6973]["tally"]
        k = next(iter(t["forms"]))
        t["forms"][k] += 1
    bad = tampered(edit)
    assert any("/tally/forms" in b for b in bad), bad


def test_tamper_the_selection_screen_fails():
    def edit(doc):
        doc["selection"]["screen"][XEON6973][0]["selected"] = ["forward"]
    bad = tampered(edit)
    assert bad and bad[0].startswith("selection/screen"), bad


def test_tamper_the_pool_hash_fails():
    def edit(doc):
        doc["pool"]["sha256"] = "0" * 64
    bad = tampered(edit)
    assert bad and bad[0].startswith("pool/sha256"), bad


def test_a_selected_cell_dropped_fails():
    def edit(doc):
        doc["cells"].pop()
    bad = tampered(edit)
    assert bad and bad[0].startswith("cells/ids"), bad
