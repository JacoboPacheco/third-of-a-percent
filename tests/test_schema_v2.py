"""harness/schema.py: the stage-S3 optional keys (aligned pairs, loop placement, layout A/A, verdict_v1,
criteria-v2 verdict extras) and combined.json, on the SAMPLE fixture extended the way run.py extends a run."""
import copy
import hashlib
import json
import os

import combine
import schema
import stats
import verdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(REPO, "results", "fixture.json")
LOOP = {"start": "0x12b0", "end": "0x12cf", "bytes": 31, "start_mod64": 48, "crosses64": True, "windows64": 2,
        "min_windows64": 1, "extra_window": True, "insns": 7, "simd": True, "innermost": True}


def v2_doc(cpu="AMD EPYC 7763 64-Core Processor"):
    with open(FIXTURE, encoding="utf-8") as f:
        d = json.load(f)
    d["run"]["runner"]["cpu_model"] = cpu
    d["run"]["criteria_file"] = "harness/criteria-v2.json"
    d["run"]["flags"]["align"] = "-falign-loops=64"
    for c in d["cells"]:
        fast = [x * 1.001 for x in c["fast_ns"]]
        s = stats.summarize(c["none_ns"], fast)
        c["aligned"] = {"none_sha256": "a" * 64, "fast_sha256": "b" * 64, "checksum_match": True,
                        "vectorized_none": dict(c["vectorized_none"]), "vectorized_fast": dict(c["vectorized_fast"]),
                        "traps_none": c["traps_none"], "traps_fast": c["traps_fast"],
                        "none_ns": c["none_ns"], "fast_ns": fast, "ratio": s["ratio"], "ci95": s["ci95"],
                        "asm_diff_path": f"results/asm/{c['cell_id']}.aligned.diff"}
        c["loops"] = {m: [dict(LOOP)] for m in ("none", "fast", "novec", "none_a64", "fast_a64")}
    k02 = next(c for c in d["cells"] if c["cell_id"] == "k02_add_fwd.L1")
    lay = []
    for ident in ("k02_add_fwd.L1", "k02_add_fwd.L2"):
        s = stats.summarize(k02["none_ns"], k02["none_ns"][::-1])
        lay.append({"id": ident, "a_build": "none", "b_build": "none_a64", "a_sha256": "a" * 64, "b_sha256": "c" * 64,
                    "n_per_side": 20, "ratio": s["ratio"], "ci95": s["ci95"], "half_width_pct": s["half_width_pct"],
                    "a_ns": k02["none_ns"], "b_ns": k02["none_ns"][::-1]})
    d["controls"]["layout_aa"] = lay
    for p in d["programs"]:
        s = stats.summarize(p["none_ns"], p["fast_ns"])
        p["aligned"] = {"none_sha256": "d" * 64, "fast_sha256": "e" * 64, "traps_none": 0, "traps_fast": 1,
                        "none_ns": p["none_ns"], "fast_ns": p["fast_ns"], "ratio": s["ratio"], "ci95": s["ci95"],
                        "consistent_with_at_most_pct": 1.0}
    with open(os.path.join(REPO, "harness", "criteria-v2.json"), "rb") as f:
        d["run"]["criteria_sha256"] = hashlib.sha256(f.read()).hexdigest()
    d["verdict"] = verdict.compute(d, verdict.load_criteria(os.path.join(REPO, "harness", "criteria-v2.json")))
    d["verdict_v1"] = verdict.compute(d, verdict.load_criteria(os.path.join(REPO, "harness", "criteria.json")))
    return d


def fails(doc, fn=schema.validate):
    try:
        fn(doc)
    except schema.SchemaError:
        return True
    return False


def test_v2_document_is_valid():
    d = v2_doc()
    schema.validate(d)
    assert d["verdict"]["criteria_version"] == 2
    assert "criteria_version" not in d["verdict_v1"]


def test_v2_drift_fails():
    d = v2_doc()
    for mutate in (
        lambda x: x["cells"][0]["aligned"].pop("ratio"),
        lambda x: x["cells"][0]["aligned"].__setitem__("extra", 1),
        lambda x: x["cells"][0]["loops"].__setitem__("other_build", []),
        lambda x: x["cells"][0]["loops"]["none"][0].__setitem__("start", "12b0"),
        lambda x: x["cells"][0]["loops"]["none"][0].__setitem__("crosses64", 1),
        lambda x: x["controls"]["layout_aa"].append(copy.deepcopy(x["controls"]["layout_aa"][0])),
        lambda x: x["controls"]["layout_aa"][0].pop("a_ns"),
        lambda x: x["run"].__setitem__("criteria_file", "harness/criteria-v9.json"),
        lambda x: x["verdict"].pop("off_axis"),
        lambda x: x["verdict_v1"].__setitem__("criteria_version", 2),
        lambda x: x["programs"][0]["aligned"].__setitem__("ci95", [2, 1]),
        lambda x: x["run"]["flags"].__setitem__("other", "x"),
    ):
        x = copy.deepcopy(d)
        mutate(x)
        assert fails(x)


def test_combined_document_is_valid_and_strict():
    crit_path = os.path.join(REPO, "harness", "criteria-v2.json")
    with open(crit_path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    crit = verdict.load_criteria(crit_path)
    c = combine.combine([("a/results.json", v2_doc("EPYC A")), ("b/results.json", v2_doc("EPYC B"))], crit, sha)
    schema.validate_combined(c)
    x = copy.deepcopy(c)
    x["verdict"]["form"] = "maybe"
    assert fails(x, schema.validate_combined)
    x = copy.deepcopy(c)
    x["files"] = []
    assert fails(x, schema.validate_combined)
    x = copy.deepcopy(c)
    x["cpus"][0]["extra"] = 1
    assert fails(x, schema.validate_combined)
