"""The verdict: one of three forms and one line, computed from results.json and harness/criteria.json.

Nobody writes the verdict line by hand. run.py calls compute() when a run ends, scripts/check.py
calls it again and demands the same answer, and the page prints `verdict.line` verbatim.

The rules (harness/criteria.json, "verdict", committed before the first run):
- INCONCLUSIVE when a control fails: the A/A half-width is above 2 %, a checksum differs, the
  -fno-vectorize positive control is not seen, or no kernel kept its vectorization (no negative control).
- MAP when every in-cache cell of a kernel that kept vectorization under FAST has ratio <= 1.02 and
  ci95_hi <= 1 + max(0.02, 2 x A/A half-width), and every in-cache cell of a kernel that lost
  vectorization has ci95_lo >= 1.5.
- HOLDS_EVERYWHERE when no in-cache cell on the vectorization axis has ci95_lo above that limit.
- INCONCLUSIVE (mixed picture) otherwise.
RAM cells are reported but never enter N, the limits or the controls.

Stage S3 adds harness/criteria-v2.json (the v1 rules unchanged, plus the loop-placement rules; see
its changelog for when and why it was written). compute() picks the rules by the criteria file's
"version": 1 -> compute_v1 (the function above, unchanged), 2 -> compute_v2. A results.json names
the file that decided its verdict in run.criteria_file; without that key it is a v1 run.
harness/criteria-v3.json (version 3) keeps compute_v2 as its per-job rule (criteria_version 3 in the
output); the v3 verdict proper is per CPU model on pooled data, in harness/pool.py.

Usage: python harness/verdict.py [results.json] [--criteria harness/criteria-v2.json]
prints the form and the line (the criteria default to the file the results name).
"""
import argparse
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
V1_FILE = "harness/criteria.json"
IN_CACHE = ("L1", "L2")
REVERSE_OR_STRIDED = {"k04_rev", "k05_stride2"}


def map_line(lost, n, x, forward=None, n_c=None, aligned=False):
    """The MAP sentence: only what the data measured. No claim about Google's whole-services average
    (the timings neither confirm nor contradict it). Wording changed Oct 12 (stage S4-measurement);
    results files written before keep their stored lines as the record. Starts lowercase."""
    comp = f"; as compiled, median {n_c['median']:.2f}" if n_c else ""
    fwd = f" ({', '.join(forward)})" if forward else ""
    return (f"loops that lose SIMD under the check ({', '.join(lost)}) cost {n['min']:.2f} to {n['max']:.2f} "
            f"times as long in cache (median {n['median']:.2f}{comp}); judged forward loops{fwd} cost at most "
            f"{x:.1f}% more" + (" with loops aligned" if aligned else "") + ".")


PS_LEAD = "Placement-sensitive cells, listed separately and not judged: "


def same_verdict(stored, recomputed, results):
    """Stored against recomputed verdict. Runs under criteria v1/v2 (S1 to S3, written before the MAP
    wording changed on Oct 12) keep their stored 'line' as the historical record, so for them the line
    is left out and every other key (form, numbers, why, lists) must match; criteria-v3 runs match fully."""
    if criteria_path(results) == "harness/criteria-v3.json":
        return stored == recomputed
    strip = lambda v: {k: x for k, x in v.items() if k != "line"}  # noqa: E731
    return strip(stored) == strip(recomputed)


def load_criteria(path=None):
    with open(path or os.path.join(HERE, "criteria.json"), encoding="utf-8") as f:
        return json.load(f)


def classes(cells):
    """Kernel classes from the remarks stored per cell: on_axis, kept, lost, off_axis (sorted lists)."""
    by_kernel = {}
    for c in cells:
        by_kernel.setdefault(c["kernel"], c)
    on_axis = sorted(k for k, c in by_kernel.items() if c["vectorized_none"]["vectorized"] is True)
    kept = [k for k in on_axis if by_kernel[k]["vectorized_fast"]["vectorized"] is True]
    lost = [k for k in on_axis if by_kernel[k]["vectorized_fast"]["vectorized"] is not True]
    off = sorted(k for k in by_kernel if k not in on_axis)
    return {"on_axis": on_axis, "kept": kept, "lost": lost, "off_axis": off}


def _pct(x):
    return 100.0 * (x - 1.0)


def criteria_path(results):
    """The repo-relative criteria file a results.json names (run.criteria_file), or the v1 file."""
    return results.get("run", {}).get("criteria_file") or V1_FILE


def compute(results, criteria=None):
    """The verdict under the given criteria document (default: harness/criteria.json, v1)."""
    criteria = criteria or load_criteria()
    if criteria.get("version", 1) >= 2:  # v3 keeps v2's per-job rule (criteria-v3.json, v3.per_job_verdict)
        return compute_v2(results, criteria)
    return compute_v1(results, criteria)


def compute_v1(results, criteria=None):
    """Returns the verdict object of results.json schema 1:
    {"form", "line", "n", "forward_limit_pct", "why"}."""
    crit = (criteria or load_criteria())["verdict"]
    cells = results["cells"]
    aa_hw = results["controls"]["aa"]["half_width_pct"]
    limit_pct = max(crit["forward_ci_hi_floor_pct"], crit["forward_ci_hi_aa_multiplier"] * aa_hw)
    limit = 1.0 + limit_pct / 100.0
    cls = classes(cells)
    in_cache = [c for c in cells if c["size_class"] in IN_CACHE]

    def cells_of(kernels):
        return [c for c in in_cache if c["kernel"] in kernels]

    def out(form, line, why, n=None):
        return {"form": form, "line": line, "n": n, "forward_limit_pct": limit_pct, "why": why}

    # 1. controls
    if aa_hw > crit["aa_half_width_max_pct"]:
        return out("inconclusive",
                   f"INCONCLUSIVE: the A/A control is too noisy (half-width {aa_hw:.2f}%, above "
                   f"{crit['aa_half_width_max_pct']:.0f}%), so no headline number is printed.",
                   "A/A control: same-run A/A half-width above aa_half_width_max_pct")
    bad = [c["cell_id"] for c in cells if not c["checksum_match"]]
    if bad:
        return out("inconclusive",
                   f"INCONCLUSIVE: the NONE and FAST outputs differ in {', '.join(bad)}, so no headline number is printed.",
                   "checksum control: a cell's NONE and FAST checksums differ")
    pos = results["controls"]["positive"]
    seen = [p for p in pos if p["ci95"][0] > 1.0 + aa_hw / 100.0]
    if not seen:
        return out("inconclusive",
                   "INCONCLUSIVE: the positive control (the same loop built with -fno-vectorize) was not "
                   "seen above the A/A noise, so the harness may be blind; no headline number is printed.",
                   "positive control: no in-cache NOVEC/NONE ci95_lo above 1 + A/A half-width")
    if not cls["kept"]:
        return out("inconclusive",
                   "INCONCLUSIVE: no kernel kept its vectorization under FAST, so there is no negative "
                   "control; no headline number is printed.",
                   "negative control: no kernel in the kept class")

    # 2. MAP
    kept_cells = cells_of(cls["kept"])
    lost_cells = cells_of(cls["lost"])
    fwd_fail = [c["cell_id"] for c in kept_cells
                if not (c["ratio"] <= crit["forward_point_max_ratio"] and c["ci95"][1] <= limit)]
    lost_fail = [c["cell_id"] for c in lost_cells if not c["ci95"][0] >= crit["lost_ci_lo_min_ratio"]]
    if cls["lost"] and lost_cells and kept_cells and not fwd_fail and not lost_fail:
        rs = [c["ratio"] for c in lost_cells]
        n = {"median": statistics.median(rs), "min": min(rs), "max": max(rs)}
        x = max(0.0, max(_pct(c["ci95"][1]) for c in kept_cells))
        line = map_line(cls["lost"], n, x, cls["kept"])
        line = line[0].upper() + line[1:]
        return out("map", line,
                   f"MAP: every in-cache cell of {', '.join(cls['kept'])} has ratio <= "
                   f"{crit['forward_point_max_ratio']} and ci95_hi <= {limit:.4f}; every in-cache cell of "
                   f"{', '.join(cls['lost'])} has ci95_lo >= {crit['lost_ci_lo_min_ratio']}", n)

    # 3. HOLDS EVERYWHERE
    axis_cells = cells_of(cls["on_axis"])
    above = [c["cell_id"] for c in axis_cells if c["ci95"][0] > limit]
    if axis_cells and not above:
        x = max(0.0, max(_pct(c["ci95"][1]) for c in axis_cells))
        return out("holds_everywhere",
                   f"On this toolchain and runner, no loop shape we tried paid more than {x:.1f}%.",
                   f"HOLDS_EVERYWHERE: no in-cache cell on the vectorization axis has ci95_lo above {limit:.4f}")

    # 4. mixed
    reasons = []
    if fwd_fail:
        reasons.append("forward rule missed by " + ", ".join(fwd_fail))
    if lost_fail:
        reasons.append("lost-vectorization minimum missed by " + ", ".join(lost_fail))
    if not cls["lost"]:
        reasons.append("no kernel lost vectorization")
    if above:
        reasons.append("cells above the forward limit: " + ", ".join(above))
    return out("inconclusive",
               "INCONCLUSIVE: a mixed picture that fits neither the map nor holds-everywhere ("
               + "; ".join(reasons) + "); no headline number is printed.",
               "mixed picture: neither MAP nor HOLDS_EVERYWHERE fired; " + "; ".join(reasons))


# ---------------------------------------------------------------- v2 (stage S3, harness/criteria-v2.json)

def layout_aa_half_width(results, criteria):
    """The largest half-width among the designated layout A/A pairs present, or None."""
    want = criteria["v2"]["layout_aa_designated"]
    hws = [p["half_width_pct"] for p in results["controls"].get("layout_aa", []) if p["id"] in want]
    return max(hws) if hws else None


def placement_sensitive(results, criteria):
    """Forward (kept) in-cache cells whose two columns disagree by more than the layout A/A half-width."""
    hw = layout_aa_half_width(results, criteria)
    if hw is None:
        return []
    kept = classes(results["cells"])["kept"]
    out = []
    for c in results["cells"]:
        if c["kernel"] in kept and c["size_class"] in IN_CACHE and c.get("aligned"):
            gap = 100.0 * abs(c["ratio"] - c["aligned"]["ratio"])
            if gap > hw:
                out.append({"cell_id": c["cell_id"], "ratio": c["ratio"], "aligned_ratio": c["aligned"]["ratio"],
                            "gap_pct": gap})
    return out


def compute_v2(results, criteria):
    """The v2 verdict for one results.json (one runner CPU model): the schema-1 keys plus
    criteria_version, cpu_model, x_pct, n_as_compiled, layout_aa_half_width_pct,
    placement_sensitive and off_axis (harness/criteria-v2.json, "v2")."""
    crit = criteria["verdict"]
    cells = results["cells"]
    cpu = results["run"]["runner"].get("cpu_model") or "this runner"
    aa_hw = results["controls"]["aa"]["half_width_pct"]
    limit_pct = max(crit["forward_ci_hi_floor_pct"], crit["forward_ci_hi_aa_multiplier"] * aa_hw)
    limit = 1.0 + limit_pct / 100.0
    cls = classes(cells)
    in_cache = [c for c in cells if c["size_class"] in IN_CACHE]
    lay_hw = layout_aa_half_width(results, criteria)
    ps = placement_sensitive(results, criteria)
    ps_ids = {p["cell_id"] for p in ps}
    off = []
    for c in in_cache:
        if c["kernel"] in cls["off_axis"] and c.get("aligned"):
            off.append({"cell_id": c["cell_id"], "ratio": c["ratio"], "aligned_ratio": c["aligned"]["ratio"],
                        "pays_in_both_columns": c["ci95"][0] > limit and c["aligned"]["ci95"][0] > limit})
    ps_text = ""
    if ps:
        ps_text = (" " + PS_LEAD
                   + "; ".join(f"{p['cell_id']} (as compiled {p['ratio']:.2f}, aligned {p['aligned_ratio']:.2f})"
                               for p in ps) + ".")

    def out(form, line, why, n=None, n_c=None, x=None):
        return {"form": form, "line": f"On {cpu}: {line}", "n": n, "forward_limit_pct": limit_pct, "why": why,
                "criteria_version": criteria.get("version", 2), "cpu_model": results["run"]["runner"].get("cpu_model"), "x_pct": x,
                "n_as_compiled": n_c, "layout_aa_half_width_pct": lay_hw, "placement_sensitive": ps,
                "off_axis": off}

    # 1. controls
    if aa_hw > crit["aa_half_width_max_pct"]:
        return out("inconclusive",
                   f"INCONCLUSIVE: the A/A control is too noisy (half-width {aa_hw:.2f}%, above "
                   f"{crit['aa_half_width_max_pct']:.0f}%), so no headline number is printed.",
                   "A/A control: same-run A/A half-width above aa_half_width_max_pct")
    bad = [c["cell_id"] for c in cells if not c["checksum_match"]]
    bad += [c["cell_id"] + " (aligned)" for c in cells if c.get("aligned") and not c["aligned"]["checksum_match"]]
    if bad:
        return out("inconclusive",
                   f"INCONCLUSIVE: the NONE and FAST outputs differ in {', '.join(bad)}, so no headline number "
                   "is printed.", "checksum control: a cell's NONE and FAST checksums differ in either column")
    missing = [c["cell_id"] for c in cells if not c.get("aligned")]
    drift = [c["cell_id"] for c in cells if c.get("aligned") and (
        c["aligned"]["vectorized_none"]["vectorized"] != c["vectorized_none"]["vectorized"]
        or c["aligned"]["vectorized_fast"]["vectorized"] != c["vectorized_fast"]["vectorized"])]
    if missing or drift:
        what = ((["no aligned pair for " + ", ".join(missing)] if missing else [])
                + (["the aligned builds' remarks differ for " + ", ".join(drift)] if drift else []))
        return out("inconclusive",
                   "INCONCLUSIVE: the loops-aligned column is incomplete (" + "; ".join(what)
                   + "), so no headline number is printed.",
                   "build control: " + "; ".join(what))
    if lay_hw is None:
        return out("inconclusive",
                   "INCONCLUSIVE: the layout A/A control (" + ", ".join(criteria["v2"]["layout_aa_designated"])
                   + ") was not measured, so placement cannot be told apart from the check; no headline number "
                   "is printed.", "layout control: no designated layout A/A pair present")
    pos = results["controls"]["positive"]
    if not [p for p in pos if p["ci95"][0] > 1.0 + aa_hw / 100.0]:
        return out("inconclusive",
                   "INCONCLUSIVE: the positive control (the same loop built with -fno-vectorize) was not "
                   "seen above the A/A noise, so the harness may be blind; no headline number is printed.",
                   "positive control: no in-cache NOVEC/NONE ci95_lo above 1 + A/A half-width")
    if not cls["kept"]:
        return out("inconclusive",
                   "INCONCLUSIVE: no kernel kept its vectorization under FAST, so there is no negative "
                   "control; no headline number is printed.",
                   "negative control: no kernel in the kept class")

    def cells_of(kernels):
        return [c for c in in_cache if c["kernel"] in kernels]

    def both(c):
        return (("", c["ci95"]), (" (aligned)", c["aligned"]["ci95"]))

    # 2. MAP: the forward rule on the aligned column; the lost minimum in both columns
    fwd = [c for c in cells_of(cls["kept"]) if c["cell_id"] not in ps_ids]
    lost_cells = cells_of(cls["lost"])
    fwd_fail = [c["cell_id"] for c in fwd if not (c["aligned"]["ratio"] <= crit["forward_point_max_ratio"]
                                                  and c["aligned"]["ci95"][1] <= limit)]
    lost_fail = [c["cell_id"] + col for c in lost_cells for col, ci in both(c)
                 if not ci[0] >= crit["lost_ci_lo_min_ratio"]]
    if cls["lost"] and lost_cells and fwd and not fwd_fail and not lost_fail:
        rs = [c["aligned"]["ratio"] for c in lost_cells]
        rc = [c["ratio"] for c in lost_cells]
        n = {"median": statistics.median(rs), "min": min(rs), "max": max(rs)}
        n_c = {"median": statistics.median(rc), "min": min(rc), "max": max(rc)}
        x = max(0.0, max(_pct(c["aligned"]["ci95"][1]) for c in fwd))
        fk = sorted({c["kernel"] for c in fwd})
        line = map_line(cls["lost"], n, x, fk, n_c, aligned=True) + ps_text
        why = (f"MAP: every counted in-cache cell of {', '.join(fk)} has aligned ratio <= "
               f"{crit['forward_point_max_ratio']} and aligned ci95_hi <= {limit:.4f}; every in-cache cell of "
               f"{', '.join(cls['lost'])} has ci95_lo >= {crit['lost_ci_lo_min_ratio']} in both columns")
        if ps:
            why += f"; placement-sensitive (layout A/A half-width {lay_hw:.2f}%): " + ", ".join(sorted(ps_ids))
        return out("map", line, why, n, n_c, x)

    # 3. HOLDS EVERYWHERE: either column, placement-sensitive cells excluded
    axis = [c for c in cells_of(cls["on_axis"]) if c["cell_id"] not in ps_ids]
    above = [c["cell_id"] + col for c in axis for col, ci in both(c) if ci[0] > limit]
    if axis and not above:
        x = max(0.0, max(max(_pct(c["ci95"][1]), _pct(c["aligned"]["ci95"][1])) for c in axis))
        return out("holds_everywhere",
                   f"no loop shape we tried paid more than {x:.1f}% (as compiled or with loops aligned)." + ps_text,
                   f"HOLDS_EVERYWHERE: no in-cache cell on the vectorization axis has ci95_lo above {limit:.4f} "
                   "in either column", x=x)

    # 4. mixed
    reasons = []
    if not fwd:
        reasons.append("no forward cell left after the placement-sensitive exclusions")
    if fwd_fail:
        reasons.append("forward rule (aligned) missed by " + ", ".join(fwd_fail))
    if lost_fail:
        reasons.append("lost-vectorization minimum missed by " + ", ".join(lost_fail))
    if not cls["lost"]:
        reasons.append("no kernel lost vectorization")
    if above:
        reasons.append("cells above the forward limit: " + ", ".join(above))
    return out("inconclusive",
               "INCONCLUSIVE: a mixed picture that fits neither the map nor holds-everywhere ("
               + "; ".join(reasons) + "); no headline number is printed." + ps_text,
               "mixed picture: neither MAP nor HOLDS_EVERYWHERE fired; " + "; ".join(reasons))


def main(argv):
    ap = argparse.ArgumentParser(description="Recompute the verdict of a results.json")
    ap.add_argument("path", nargs="?", default=os.path.join(REPO, "results", "results.json"))
    ap.add_argument("--criteria", default=None,
                    help="criteria file (default: the run's run.criteria_file, else harness/criteria.json)")
    a = ap.parse_args(argv[1:])
    with open(a.path, encoding="utf-8") as f:
        results = json.load(f)
    crit_file = a.criteria or os.path.join(REPO, criteria_path(results))
    v = compute(results, load_criteria(crit_file))
    print("criteria:", os.path.relpath(crit_file, REPO).replace("\\", "/"))
    print("form:", v["form"])
    print("line:", v["line"])
    print("why: ", v["why"])
    rc = 0
    stored = results.get("verdict")
    if a.criteria is None and stored is not None and not same_verdict(stored, v, results):
        print("WARNING: the stored verdict differs from the recomputed one")
        rc = 1
    if a.criteria is None and results.get("verdict_v1") is not None:
        if not same_verdict(results["verdict_v1"], compute(results, load_criteria(os.path.join(REPO, V1_FILE))), results):
            print("WARNING: the stored verdict_v1 differs from the recomputed one")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
