#!/usr/bin/env python3
"""Day-one test, evaluation half. Pure standard-library Python, so it runs on the runner and on Windows alike.

Reads dayone/out/raw.json (or the path given) and dayone/criteria.json, computes every ratio and its
percentile-bootstrap 95 % interval (10000 resamples, fixed seed), then the three criteria, the two
informational checks and the SPEC section 1 verdict. Writes dayone/out/dayone.json and prints a summary.
Usage: python dayone/evaluate.py [raw.json] [out.json]
"""
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261011
RESAMPLES = 10000
FORWARD = ["k01_sum_fwd", "k02_add_fwd", "k03_stencil"]
REVSTRIDE = ["k04_rev", "k05_stride2"]
IN_CACHE = ["L1", "L2"]


def ratio_ci(a, b):
    """ratio = median(b) / median(a); percentile bootstrap, each side resampled independently."""
    rng = random.Random(SEED)
    ma, mb = statistics.median(a), statistics.median(b)
    na, nb = len(a), len(b)
    rs = []
    for _ in range(RESAMPLES):
        rs.append(statistics.median(rng.choices(b, k=nb)) / statistics.median(rng.choices(a, k=na)))
    rs.sort()
    lo = rs[int(0.025 * RESAMPLES)]
    hi = rs[int(0.975 * RESAMPLES) - 1]
    return {"ratio": mb / ma, "ci95": [lo, hi], "half_width_pct": (hi - lo) / 2 * 100,
            "median_a_ns": ma, "median_b_ns": mb, "n_a": na, "n_b": nb}


def summarize_pair(p):
    s = ratio_ci(p["a_ns"], p["b_ns"])
    s["checksum_match"] = len(p["a_checksums"]) == 1 and p["a_checksums"] == p["b_checksums"]
    s["order"] = p["order"]
    return s


def main():
    raw_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out", "raw.json")
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(raw_path), "dayone.json")
    raw = json.load(open(raw_path))
    crit = json.load(open(os.path.join(HERE, "criteria.json")))
    kern = raw["kernels"]
    vec = {k: {m: kern[k]["builds"][m]["remarks"]["vectorized"] for m in ("none", "fast", "novec")} for k in kern}
    width = {k: {m: kern[k]["builds"][m]["remarks"]["width"] for m in ("none", "fast")} for k in kern}

    cells = {}
    for c in raw["cells"]:
        e = {"kernel": c["kernel"], "size_class": c["size_class"], "n": c["n"],
             "working_set_bytes": c["working_set_bytes"], "iters": c["iters"],
             "fast": summarize_pair(c["fast"]), "novec": summarize_pair(c["novec"])}
        if "aa" in c:
            e["aa"] = summarize_pair(c["aa"])
        cells[c["cell_id"]] = e

    progs = {}
    for p in raw.get("programs", []):
        e = {"built": p["built"], "ran": p.get("ran", False),
             "traps": {m: p["builds"][m].get("traps") for m in p["builds"]},
             "sha256": {m: p["builds"][m].get("sha256") for m in p["builds"]}}
        if p.get("ran"):
            e["fast"] = summarize_pair(p["fast"])
            if "aa" in p:
                e["aa"] = summarize_pair(p["aa"])
                e["aa_identical"] = p["aa_sha256"][0] == p["aa_sha256"][1]
        progs[p["name"]] = e

    # ---- C1: the A/A floor
    aa = []
    ident_k = raw["aa_binaries"]["a_sha256"] == raw["aa_binaries"]["b_sha256"]
    for sc in ("L1", "L2", "RAM"):
        cid = f"k02_add_fwd.{sc}"
        if cid in cells and "aa" in cells[cid]:
            a = cells[cid]["aa"]
            aa.append({"pair": cid, "identical": ident_k, "half_width_pct": a["half_width_pct"],
                       "ratio": a["ratio"], "ci95": a["ci95"], "n": [a["n_a"], a["n_b"]]})
    jp = progs.get("json_parse", {})
    if "aa" in jp:
        a = jp["aa"]
        aa.append({"pair": "program:json_parse", "identical": jp["aa_identical"],
                   "half_width_pct": a["half_width_pct"], "ratio": a["ratio"], "ci95": a["ci95"],
                   "n": [a["n_a"], a["n_b"]]})
    expected_pairs = crit["design_fixed_before_any_run"]["aa_pairs"]
    c1_met = (len(aa) == len(expected_pairs) and all(x["identical"] for x in aa)
              and all(x["n"] == [20, 20] for x in aa))
    c1_val = max((x["half_width_pct"] for x in aa), default=None)
    if c1_val is None:
        branch = None
    elif c1_val <= 0.3:
        branch = "can_test_0.30"
    elif c1_val >= 1.0:
        branch = "sanity_check"
    else:
        branch = "between"
    kernel_aa_floor = max((x["half_width_pct"] for x in aa if x["pair"].startswith("k02")), default=None)

    # ---- C2: the loop-shape effect
    c2_rows, c2_met = [], True
    for k in REVSTRIDE + FORWARD:
        for sc in IN_CACHE:
            f = cells[f"{k}.{sc}"]["fast"]
            if k in REVSTRIDE:
                ok = f["ci95"][0] >= 1.5
                rule = "ci95_lo >= 1.5"
            else:
                ok = f["ci95"][1] < 1.02
                rule = "ci95_hi < 1.02"
            ok = ok and f["checksum_match"]
            c2_met &= ok
            c2_rows.append({"cell": f"{k}.{sc}", "rule": rule, "ratio": f["ratio"], "ci95": f["ci95"],
                            "checksum_match": f["checksum_match"], "met": ok})

    # ---- C3: toolchain
    def prog_ok(e):
        return bool(e) and e["built"] and e["ran"] and e["fast"]["checksum_match"] and \
            all(e["traps"].get(m) is not None for m in ("none", "fast"))
    second_name = next((n for n in progs if n != "json_parse"), None)
    c3_json = prog_ok(progs.get("json_parse"))
    c3_second = prog_ok(progs.get(second_name)) if second_name else False
    c3_met = c3_json and c3_second

    # ---- informational checks
    v1_rows = []
    for k in kern:
        expect = (True, True) if k in FORWARD else (True, False)
        got = (vec[k]["none"], vec[k]["fast"])
        v1_rows.append({"kernel": k, "expected_none_fast": expect, "remarks_none_fast": got,
                        "width_none_fast": (width[k]["none"], width[k]["fast"]),
                        "novec_vectorized": vec[k]["novec"], "as_expected": got == expect})
    v2_rows = []
    for k in kern:
        tn = kern[k]["builds"]["none"]["traps"]["total"]
        tf = kern[k]["builds"]["fast"]["traps"]["total"]
        v2_rows.append({"kernel": k, "traps_none": tn, "traps_fast": tf, "fast_has_more": tf > tn})

    # ---- verdict, SPEC section 1
    fl = crit["verdict_rule_spec_section_1"]["forward_limit_pct"]
    rmin = crit["verdict_rule_spec_section_1"]["reverse_min_ratio"]
    on_axis = [k for k in kern if vec[k]["none"] is True]
    lost = [k for k in on_axis if vec[k]["fast"] is False]
    kept = [k for k in on_axis if vec[k]["fast"] is True]
    pos_cells = []
    for k in on_axis:
        for sc in IN_CACHE:
            nv = cells[f"{k}.{sc}"]["novec"]
            pos_cells.append({"cell": f"{k}.{sc}", "novec_ratio": nv["ratio"], "ci95": nv["ci95"],
                              "seen": kernel_aa_floor is not None and nv["ci95"][0] > 1 + kernel_aa_floor / 100})
    positive_seen = any(p["seen"] for p in pos_cells)
    cache_ck = all(cells[f"{k}.{sc}"]["fast"]["checksum_match"] and cells[f"{k}.{sc}"]["novec"]["checksum_match"]
                   for k in kern for sc in IN_CACHE)
    why = []
    if not all(x["identical"] for x in aa):
        why.append("an A/A pair is not byte-identical")
    if kernel_aa_floor is None or kernel_aa_floor >= fl:
        why.append(f"kernel A/A floor {kernel_aa_floor} % is not below the {fl} % forward limit")
    if not positive_seen:
        why.append("the -fno-vectorize positive control was not seen")
    if not cache_ck:
        why.append("a checksum differs between builds of an in-cache cell")
    n_block, line = None, None
    if why:
        form = "inconclusive"
    else:
        fwd_ok = all(cells[f"{k}.{sc}"]["fast"]["ci95"][1] < 1 + fl / 100 for k in kept for sc in IN_CACHE)
        lost_ok = bool(lost) and all(cells[f"{k}.{sc}"]["fast"]["ci95"][0] >= rmin for k in lost for sc in IN_CACHE)
        if fwd_ok and lost_ok:
            form = "map"
            rs = [cells[f"{k}.{sc}"]["fast"]["ratio"] for k in lost for sc in IN_CACHE]
            n_block = {"median": statistics.median(rs), "min": min(rs), "max": max(rs)}
            fwd_hi = max(cells[f"{k}.{sc}"]["fast"]["ci95"][1] for k in kept for sc in IN_CACHE)
            line = (f"Google's 0.30% holds for forward loops (at most {100 * (fwd_hi - 1):.1f}% on "
                    f"{', '.join(kept)}); a reverse or strided loop under the same check pays "
                    f"{n_block['median']:.2f} times (range {n_block['min']:.2f} to {n_block['max']:.2f}), "
                    f"because it loses SIMD.")
            why.append("MAP: every kept-vectorization kernel under the forward limit in cache, every "
                       "lost-vectorization kernel at or above the reverse minimum in cache")
        elif not any(cells[f"{k}.{sc}"]["fast"]["ci95"][0] >= 1 + fl / 100 for k in on_axis for sc in IN_CACHE):
            form = "holds_everywhere"
            x = max(cells[f"{k}.{sc}"]["fast"]["ci95"][1] for k in on_axis for sc in IN_CACHE)
            line = f"On this toolchain and runner, no loop shape we tried paid more than {100 * (x - 1):.1f}%."
            why.append("HOLDS_EVERYWHERE: no in-cache cell on the axis has ci95_lo above the forward limit")
        else:
            form = "inconclusive"
            why.append("mixed picture: neither the MAP nor the HOLDS_EVERYWHERE rule fired")

    go = c1_met and c2_met and c3_met
    result = {
        "schema": "dayone-1",
        "raw": os.path.relpath(raw_path, os.path.dirname(HERE)).replace("\\", "/"),
        "run": {k: v for k, v in raw["run"].items() if k != "runner"} | {
            "runner": {k: v for k, v in raw["run"]["runner"].items() if k != "lscpu"}},
        "criteria": {
            "C1_aa_floor": {"met": c1_met, "value_pct": c1_val, "branch": branch, "pairs": aa},
            "C2_loop_shape": {"met": c2_met, "cells": c2_rows},
            "C3_toolchain": {"met": c3_met, "json_parse": c3_json, "second_program": second_name,
                             "second_met": c3_second, "attempts": raw.get("second_program_attempts")},
        },
        "informational": {"V1_vectorization_shape": v1_rows, "V2_hardening_present": v2_rows},
        "go": go,
        "verdict": {"form": form, "line": line, "n": n_block, "forward_limit_pct": fl,
                    "kernel_aa_floor_pct": kernel_aa_floor, "on_axis": on_axis, "lost_vectorization": lost,
                    "kept_vectorization": kept, "positive_control": pos_cells, "why": why},
        "cells": cells,
        "programs": progs,
    }
    with open(out_path, "w") as f:
        json.dump(result, f, indent=1)

    print(f"GO: {go}   verdict form: {form}")
    print(f"C1 met={c1_met} largest A/A half-width={c1_val} % branch={branch}")
    for x in aa:
        print(f"   A/A {x['pair']}: ratio {x['ratio']:.4f} ci {x['ci95'][0]:.4f}..{x['ci95'][1]:.4f} "
              f"half-width {x['half_width_pct']:.3f} % identical={x['identical']}")
    print(f"C2 met={c2_met}")
    for r in c2_rows:
        print(f"   {r['cell']}: {r['ratio']:.3f} [{r['ci95'][0]:.3f}, {r['ci95'][1]:.3f}] {r['rule']} -> {r['met']}")
    print(f"C3 met={c3_met} json={c3_json} second={second_name}:{c3_second}")
    print("cells (FAST/NONE, NOVEC/NONE):")
    for cid, e in cells.items():
        f, nv = e["fast"], e["novec"]
        print(f"   {cid:18s} fast {f['ratio']:.3f} [{f['ci95'][0]:.3f},{f['ci95'][1]:.3f}]  "
              f"novec {nv['ratio']:.3f} [{nv['ci95'][0]:.3f},{nv['ci95'][1]:.3f}]  ck={f['checksum_match']}")
    for r in v1_rows:
        print(f"   V1 {r['kernel']}: remarks none/fast {r['remarks_none_fast']} width {r['width_none_fast']} "
              f"expected {r['expected_none_fast']}")
    for r in v2_rows:
        print(f"   V2 {r['kernel']}: traps none {r['traps_none']} fast {r['traps_fast']}")
    for n, e in progs.items():
        print(f"   program {n}: built={e['built']} ran={e['ran']} traps={e['traps']}"
              + (f" fast {e['fast']['ratio']:.4f} {e['fast']['ci95']}" if e.get('ran') else ""))
    print("verdict:", line, why)


if __name__ == "__main__":
    main()
