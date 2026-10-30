"""What the placement exemption would change if it also required the two loop placements to differ by a minimum amount.

The pooled rule (harness/criteria-v3.json, v3.placement_sensitive; harness/pool.py) exempts a forward in-cache cell from the
forward rule when BOTH hold: the 95% interval of D = (FAST/NONE as compiled) / (FAST/NONE with loops aligned) excludes 1, and
the hot loops of NONE and FAST sit differently relative to 64-byte windows. Neither part has a minimum size: a cell whose D
differs from 1 by half a percent is exempt as soon as its interval clears 1. This script asks how much of the stored picture
depends on that. From the STORED pooled files only (no timing file is read, no number is re-measured), it re-applies
harness/pool.py's own verdict function (read-only use of pool.cpu_verdict) to each stored CPU-model block with the exemption
flag recomputed under four rules:

    written             the rule as stored (statistical and mechanical)
    d_floor_2pct        written, and also |D - 1| >= 2%
    d_floor_layout_aa   written, and also |D - 1| >= the same pool's layout A/A half-width, taken as the largest half-width
                        among the designated pairs (criteria-v2 definition: k02_add_fwd.L1 and k02_add_fwd.L2)
    d_floor_both        written, and also |D - 1| >= the larger of the two floors

For each pool and CPU model it lists the exempt cells (D and its interval, the as-compiled and aligned ratios, whether the
aligned pair would pass the forward rule if the cell were judged), the verdict word under each rule, and the exempt cells that
would not pass the forward rule. The "written" rule must reproduce every stored verdict exactly (word, reason, line and
numbers); a difference is a failure of this script, not a finding.

This is a sensitivity analysis. Nothing here is a verdict: no stored verdict, pool or rule file is changed, and the
alternative rules are not proposed as replacements.

    python robustness/placement_floor.py            write robustness/placement-floor.json
    python robustness/placement_floor.py --report   also rewrite the generated block of robustness/README-placement-floor.md
    python robustness/placement_floor.py --verify   recompute everything and fail on any difference with the stored file,
                                                    its input sha256s and the generated README block
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402  (read-only use: cpu_verdict)

OUT = "robustness/placement-floor.json"
README = "robustness/README-placement-floor.md"
MARKS = ("<!-- placement-floor:begin -->", "<!-- placement-floor:end -->")
CRITERIA = "harness/criteria-v3.json"
D_FLOOR_PCT = 2.0     # the fixed minimum of the second rule, in percent

POOLS = [
    {"id": "s4", "pooled": "results/s4-pooled/pooled.json", "arch": "x86-64",
     "what": "the original 30-job x86-64 pool"},
    {"id": "s6", "pooled": "results/s6-pooled/pooled.json", "arch": "x86-64",
     "what": "the 75-job x86-64 pool"},
    {"id": "s7", "pooled": "results/s7-pooled/pooled.json", "arch": "x86-64",
     "what": "the x86-64 pool the page reads"},
    {"id": "s9-x86-c", "pooled": "results/s9-x86-c-pooled/pooled.json", "arch": "x86-64",
     "what": "the x86-64 replication set, pooled alone"},
    {"id": "s9-x86-ac", "pooled": "results/s9-x86-ac-pooled/pooled.json", "arch": "x86-64",
     "what": "the x86-64 pool and its replication set pooled together"},
    {"id": "s8-arm", "pooled": "results/s8-arm-pooled/pooled.json", "arch": "arm64",
     "what": "the Arm pool (set A)"},
    {"id": "s9-arm-b", "pooled": "results/s9-arm-b-pooled/pooled.json", "arch": "arm64",
     "what": "the Arm replication set (set B), pooled alone"},
    {"id": "s9-arm-ab", "pooled": "results/s9-arm-ab-pooled/pooled.json", "arch": "arm64",
     "what": "the Arm pool and its replication set pooled together"},
]

RULES = [
    {"id": "written", "short": "as stored",
     "text": "the rule as stored: the interval of D excludes 1 and the hot loops differ in placement"},
    {"id": "d_floor_2pct", "short": "D floor 2%",
     "text": "the stored rule, and also |D - 1| >= 2%"},
    {"id": "d_floor_layout_aa", "short": "D floor = layout A/A",
     "text": "the stored rule, and also |D - 1| >= the pool's layout A/A half-width (largest of the designated pairs)"},
    {"id": "d_floor_both", "short": "D floor = larger of the two",
     "text": "the stored rule, and also |D - 1| >= the larger of the 2% floor and the layout A/A half-width"},
]
RULE_IDS = [r["id"] for r in RULES]
ALTERNATIVES = RULE_IDS[1:]


# ---------------------------------------------------------------- files

def posix(p):
    return p.replace("\\", "/")


def read_json(root, rel, hashes):
    """Parse a JSON file under root and record its sha256 (CRLF read as LF: a Windows checkout and a Linux clone agree)."""
    with open(os.path.join(root, rel), "rb") as f:
        raw = f.read()
    hashes[rel] = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    return json.loads(raw.decode("utf-8"))


def criteria_sha_matches(root, stored):
    """True when the sha256 a pooled file stored for the criteria file is the one of the file on disk (LF or CRLF checkout)."""
    with open(os.path.join(root, CRITERIA), "rb") as f:
        raw = f.read()
    return stored in (hashlib.sha256(raw).hexdigest(), hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest())


def same(a, b, where="", out=None):
    """Deep comparison, floats equal to a relative 1e-12; returns the first few differing paths."""
    out = [] if out is None else out
    if len(out) >= 10:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a) != list(b):
            out.append(f"{where}: keys {list(a)[:6]} vs {list(b)[:6]}")
        for k in a:
            if k in b:
                same(a[k], b[k], f"{where}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{where}: length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, f"{where}[{i}]", out)
    elif isinstance(a, float) or isinstance(b, float):
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool)
                and not isinstance(b, bool) and math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-15)):
            out.append(f"{where}: {a!r} vs {b!r}")
    elif a != b or type(a) is not type(b):
        out.append(f"{where}: {a!r} vs {b!r}")
    return out


# ---------------------------------------------------------------- the rules

def d_deviation_pct(pl):
    """|D - 1| in percent, D being the pooled ratio of the as-compiled to the aligned FAST/NONE ratios."""
    return abs(pl["d"]["ratio"] - 1.0) * 100.0


def exempt_flag(rule, pl, layout_floor):
    """Whether the cell is exempt under `rule`; pl is a stored cell["placement"] block."""
    base = bool(pl["statistical"] and pl["mechanical"])
    dev = d_deviation_pct(pl)
    if rule == "written":
        return base
    if rule == "d_floor_2pct":
        return base and dev >= D_FLOOR_PCT
    if rule == "d_floor_layout_aa":
        return base and dev >= layout_floor
    if rule == "d_floor_both":
        return base and dev >= max(D_FLOOR_PCT, layout_floor)
    raise ValueError(rule)


def classes_of(cells):
    """The kernel classes verdict.classes derived from the remarks, read back from the stored per-cell class."""
    kept = sorted({c["kernel"] for c in cells if c["class"] == "kept"})
    lost = sorted({c["kernel"] for c in cells if c["class"] == "lost"})
    off = sorted({c["kernel"] for c in cells if c["class"] == "off_axis"})
    return {"on_axis": sorted(kept + lost), "kept": kept, "lost": lost, "off_axis": off}


def verdict_under(block, rule, layout_floor, cls, problems, crit_doc):
    """pool.cpu_verdict on a copy of the stored block whose exemption flags follow `rule`."""
    cells = []
    for c in block["cells"]:
        if "placement" in c:
            pl = dict(c["placement"])
            pl["sensitive"] = exempt_flag(rule, pl, layout_floor)
            c = dict(c, placement=pl)
        cells.append(c)
    crit, v3 = crit_doc["verdict"], crit_doc["v3"]
    aa_hw = block["aa"]["half_width_pct"]
    limit_pct = max(crit["forward_ci_hi_floor_pct"], crit["forward_ci_hi_aa_multiplier"] * aa_hw)
    limit = 1.0 + limit_pct / 100.0
    return pool.cpu_verdict(dict(block, cells=cells), cls, problems, crit, v3, limit, limit_pct, aa_hw, crit_doc)


# ---------------------------------------------------------------- one CPU model

def exempt_record(c, limit, crit, layout_floor):
    pl = c["placement"]
    d = pl["d"]
    lo, hi = d["ci95"]
    al = c["aligned"]
    point_ok = al["ratio"] <= crit["forward_point_max_ratio"]
    ci_ok = al["ci95"][1] <= limit
    return {"cell_id": c["cell_id"], "kernel": c["kernel"], "size_class": c["size_class"],
            "d_ratio": d["ratio"], "d_ci95": list(d["ci95"]),
            "d_deviation_pct": d_deviation_pct(pl),
            "d_interval_margin_pct": max(lo - 1.0, 1.0 - hi) * 100.0,
            "as_compiled_ratio": c["as_compiled"]["ratio"],
            "aligned_ratio": al["ratio"], "aligned_ci95": list(al["ci95"]),
            "aligned_point_within_limit": point_ok, "aligned_ci_hi_within_limit": ci_ok,
            "passes_forward_rule_if_judged": point_ok and ci_ok,
            "stays_exempt": {r: exempt_flag(r, pl, layout_floor) for r in ALTERNATIVES}}


def model_row(pool_id, block, crit_doc, minimum, problems_out):
    cpu = block["cpu_model"]
    crit = crit_doc["verdict"]
    designated = crit_doc["v2"]["layout_aa_designated"]
    pairs = {i: block["layout_aa"][i]["half_width_pct"] for i in designated if i in block["layout_aa"]}
    tag = f"{pool_id}: {cpu}"
    if len(pairs) != len(designated):
        problems_out.append(f"{tag}: a designated layout A/A pair is missing from the stored block")
        return None
    floor = max(pairs.values())
    limit_pct = max(crit["forward_ci_hi_floor_pct"], crit["forward_ci_hi_aa_multiplier"] * block["aa"]["half_width_pct"])
    limit = 1.0 + limit_pct / 100.0
    cells = block["cells"]
    cls = classes_of(cells)
    problems = {"checksum": [], "build": [], "layout": []}
    in_cache = [c for c in cells if "placement" in c]
    for c in in_cache:
        pl = c["placement"]
        if bool(pl["sensitive"]) != bool(pl["statistical"] and pl["mechanical"]):
            problems_out.append(f"{tag}: {c['cell_id']}: the stored exemption flag is not 'statistical and mechanical'")
    rules = {}
    for r in RULE_IDS:
        v = verdict_under(block, r, floor, cls, problems, crit_doc)
        ids = [c["cell_id"] for c in in_cache if exempt_flag(r, c["placement"], floor)]
        rules[r] = {"word": v["form"], "why": v["why"], "exempt_cell_ids": ids}
        if r == "written":
            diff = same(v, block["verdict"])
            reproduces = not diff
            if diff:
                problems_out.append(f"{tag}: the stored rule does not reproduce the stored verdict: {diff[0]}")
    row = {"cpu_model": cpu, "jobs": block["jobs"], "runs": len(block["runs"]), "testable": block["jobs"] >= minimum,
           "stored_form": block["verdict"]["form"], "stored_why": block["verdict"]["why"],
           "aa_half_width_pct": block["aa"]["half_width_pct"], "forward_limit_pct": limit_pct,
           "layout_aa_pairs_half_width_pct": pairs, "layout_aa_half_width_pct": floor,
           "reproduces_stored_verdict": reproduces,
           "exempt_cells": [exempt_record(c, limit, crit, floor) for c in in_cache if c["placement"]["sensitive"]],
           "rules": rules,
           "words_that_change": [r for r in ALTERNATIVES if rules[r]["word"] != rules["written"]["word"]]}
    return row


# ---------------------------------------------------------------- pools and the summary

def pool_section(root, spec, crit_doc, minimum, hashes, problems):
    pdoc = read_json(root, spec["pooled"], hashes)
    if pdoc.get("kind") != "pooled" or pdoc.get("criteria_file") != CRITERIA:
        problems.append(f"{spec['id']}: {spec['pooled']} is not a pooled file under {CRITERIA}")
    elif not criteria_sha_matches(root, pdoc.get("criteria_sha256")):
        problems.append(f"{spec['id']}: the criteria sha256 stored in {spec['pooled']} is not the one of {CRITERIA}")
    rows = [model_row(spec["id"], block, crit_doc, minimum, problems) for block in pdoc["cpus"]]
    rows = [r for r in rows if r is not None]
    return {"id": spec["id"], "arch": spec["arch"], "what": spec["what"], "pooled_file": spec["pooled"],
            "jobs": len(pdoc["inputs"]), "runs": len(pdoc["runs"]), "models": rows}


def summarise(pools, crit_doc):
    crit = crit_doc["verdict"]
    testable = [(p, r) for p in pools for r in p["models"] if r["testable"]]
    changes = {r: [] for r in ALTERNATIVES}
    unchanged = {r: [] for r in ALTERNATIVES}     # a cell that misses the forward rule is judged, yet the word stays
    for p, row in testable:
        failing_ids = {c["cell_id"] for c in row["exempt_cells"] if not c["passes_forward_rule_if_judged"]}
        for r in ALTERNATIVES:
            lost = [i for i in row["rules"]["written"]["exempt_cell_ids"] if i not in row["rules"][r]["exempt_cell_ids"]]
            judged_failing = [i for i in lost if i in failing_ids]
            if r in row["words_that_change"]:
                changes[r].append({"pool": p["id"], "cpu_model": row["cpu_model"], "jobs": row["jobs"],
                                   "from": row["rules"]["written"]["word"], "to": row["rules"][r]["word"],
                                   "cells_losing_exemption": lost,
                                   "of_which_missing_the_forward_rule": judged_failing,
                                   "why_under_rule": row["rules"][r]["why"]})
            elif judged_failing:
                unchanged[r].append({"pool": p["id"], "cpu_model": row["cpu_model"], "jobs": row["jobs"],
                                     "word": row["rules"]["written"]["word"],
                                     "cells_losing_exemption": lost,
                                     "of_which_missing_the_forward_rule": judged_failing})
    occ_all, above, failing = [], [], {}
    for p in pools:
        for row in p["models"]:
            for c in row["exempt_cells"]:
                occ = {"pool": p["id"], "cpu_model": row["cpu_model"], "jobs": row["jobs"], "testable": row["testable"],
                       "cell_id": c["cell_id"], "aligned_ratio": c["aligned_ratio"],
                       "aligned_ci95_hi": c["aligned_ci95"][1], "d_deviation_pct": c["d_deviation_pct"],
                       "layout_aa_half_width_pct": row["layout_aa_half_width_pct"],
                       "aligned_point_within_limit": c["aligned_point_within_limit"],
                       "aligned_ci_hi_within_limit": c["aligned_ci_hi_within_limit"],
                       "stays_exempt": c["stays_exempt"]}
                occ_all.append(occ)
                if not c["aligned_point_within_limit"]:
                    above.append(occ)
                if not c["passes_forward_rule_if_judged"]:
                    failing.setdefault((row["cpu_model"], c["cell_id"]), []).append(occ)
    distinct = [{"cpu_model": k[0], "cell_id": k[1], "occurrences": v} for k, v in sorted(failing.items())]
    devs = [o["d_deviation_pct"] for o in occ_all]
    return {
        "testable_rows": len(testable),
        "word_changes": changes,
        "word_unchanged_though_a_missing_cell_is_judged": unchanged,
        "exempt_cell_records": len(occ_all),
        "d_deviation_pct_min": min(devs), "d_deviation_pct_max": max(devs),
        "exempt_cell_records_below_2pct": sum(1 for o in occ_all if o["d_deviation_pct"] < D_FLOOR_PCT),
        "exempt_cell_records_below_layout_floor": sum(1 for o in occ_all
                                                       if o["d_deviation_pct"] < o["layout_aa_half_width_pct"]),
        "forward_point_max_ratio": crit["forward_point_max_ratio"],
        "exempt_cells_with_aligned_ratio_above_point_limit": above,
        "distinct_exempt_cells_not_passing_forward_rule": distinct,
    }


def build(root=REPO):
    hashes = {}
    problems = []
    crit_doc = read_json(root, CRITERIA, hashes)
    minimum = crit_doc["v3"]["pooling"]["minimum_jobs"]
    pools = [pool_section(root, spec, crit_doc, minimum, hashes, problems) for spec in POOLS]
    v = crit_doc["verdict"]
    return {"kind": "placement-floor",
            "script": "robustness/placement_floor.py",
            "label": "sensitivity analysis, not a verdict; no stored verdict, pool or rule file is changed",
            "method": {"source": "the stored pooled.json files only; harness/pool.py cpu_verdict is applied read-only to a copy of "
                                 "each stored CPU-model block whose exemption flags follow the rule under test",
                       "d": "D = (FAST/NONE as compiled) / (FAST/NONE with loops aligned), pooled over jobs "
                            "(harness/pool.py placement_stat); its deviation is |D - 1| in percent",
                       "d_floor_pct": D_FLOOR_PCT,
                       "layout_aa_half_width": "the largest half_width_pct among the designated layout A/A pairs "
                                               "present in the stored block (the criteria-v2 definition)",
                       "stored_rule_reproduces_stored_verdict": "required of every row; a difference fails the script"},
            "rules": RULES,
            "criteria": {"file": CRITERIA, "forward_point_max_ratio": v["forward_point_max_ratio"],
                         "forward_ci_hi_floor_pct": v["forward_ci_hi_floor_pct"],
                         "forward_ci_hi_aa_multiplier": v["forward_ci_hi_aa_multiplier"], "minimum_jobs": minimum,
                         "layout_aa_designated": crit_doc["v2"]["layout_aa_designated"]},
            "pools": pools,
            "summary": summarise(pools, crit_doc),
            "checks": {"problems": problems},
            "inputs": dict(sorted(hashes.items()))}


# ---------------------------------------------------------------- the generated README block

def fmt(x, nd=2):
    return f"{x:.{nd}f}"


def short_cpu(name):
    return (name.replace("AMD EPYC ", "EPYC ").replace(" 64-Core Processor", "").replace(" 96-Core Processor", "")
            .replace(" 80-Core Processor", "").replace("INTEL(R) XEON(R) PLATINUM ", "Xeon ")
            .replace("Intel(R) Xeon(R) Platinum ", "Xeon ").replace("Intel(R) Xeon(R) ", "Xeon ")
            .replace(" CPU @ 2.80GHz", ""))


def word_cell(row, rule):
    w = row["rules"][rule]["word"]
    return w if w == row["rules"]["written"]["word"] else f"{w} (changed)"


def render(doc):
    s = doc["summary"]
    out = ["### Verdict words under the alternative exemption rules (generated)", "",
           "One row per pool and CPU model with enough jobs for a verdict. The first word column is the stored word. "
           "A word followed by (changed) differs from it.", "",
           "| pool | CPU model | jobs | stored rule | D floor 2% | D floor = layout A/A | D floor = larger | layout A/A half-width % | "
           "exempt cells: stored / 2% / layout / larger |",
           "|---|---|---:|---|---|---|---|---:|---|"]
    for p in doc["pools"]:
        for r in p["models"]:
            if not r["testable"]:
                continue
            n = " / ".join(str(len(r["rules"][x]["exempt_cell_ids"])) for x in RULE_IDS)
            out.append(f"| {p['id']} | {short_cpu(r['cpu_model'])} | {r['jobs']} | {word_cell(r, 'written')} | "
                       f"{word_cell(r, 'd_floor_2pct')} | {word_cell(r, 'd_floor_layout_aa')} | {word_cell(r, 'd_floor_both')} | "
                       f"{fmt(r['layout_aa_half_width_pct'], 3)} | {n} |")
    out += ["", "### Exempt cells that would not pass the forward rule if they were judged (generated)", "",
            f"A cell is listed when, in at least one pool, its aligned ratio is above {s['forward_point_max_ratio']:g} or its "
            "aligned upper interval end is above the forward limit of that CPU model. Ranges run over the pools in which "
            "the cell is exempt; the last three columns count the pools in which it stays exempt.", "",
            "| CPU model | cell | pools (jobs) | aligned ratio | aligned upper end | \\|D - 1\\| % | pools with ratio above "
            f"{s['forward_point_max_ratio']:g} / interval above limit | stays exempt: 2% floor | layout floor | larger floor |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for d in s["distinct_exempt_cells_not_passing_forward_rule"]:
        o = d["occurrences"]
        pools_txt = ", ".join(f"{x['pool']} ({x['jobs']})" for x in o)
        ar = [x["aligned_ratio"] for x in o]
        hi = [x["aligned_ci95_hi"] for x in o]
        dv = [x["d_deviation_pct"] for x in o]
        rng = lambda v, nd: fmt(min(v), nd) if min(v) == max(v) else f"{fmt(min(v), nd)} to {fmt(max(v), nd)}"  # noqa: E731
        pt = sum(1 for x in o if not x["aligned_point_within_limit"])
        ci = sum(1 for x in o if not x["aligned_ci_hi_within_limit"])
        stay = [sum(1 for x in o if x["stays_exempt"][r]) for r in ALTERNATIVES[:3]]
        out.append(f"| {short_cpu(d['cpu_model'])} | {d['cell_id']} | {pools_txt} | {rng(ar, 4)} | {rng(hi, 4)} | {rng(dv, 2)} | "
                   f"{pt} / {ci} of {len(o)} | {stay[0]} of {len(o)} | {stay[1]} of {len(o)} | {stay[2]} of {len(o)} |")
    out += ["", "### Facts read from the stored files (generated)", ""]
    out.append(f"- {s['testable_rows']} pool and CPU-model rows have enough jobs for a verdict. The stored rule reproduces the "
               "stored verdict of every row, with the same word, reason, line and numbers.")
    for r in RULES[1:]:
        ch = s["word_changes"][r["id"]]
        un = s["word_unchanged_though_a_missing_cell_is_judged"][r["id"]]
        line = f"- {r['text'][0].upper() + r['text'][1:]}: " + (
            f"{len(ch)} row(s) change word: " + "; ".join(
                f"{c['pool']} {short_cpu(c['cpu_model'])} {c['from']} to {c['to']} "
                f"({', '.join(c['of_which_missing_the_forward_rule'])} judged and missing the forward rule)" for c in ch) + "."
            if ch else "no row changes word.")
        if un:
            line += (" Rows whose word stays although a cell missing the forward rule is judged: "
                     + "; ".join(f"{c['pool']} {short_cpu(c['cpu_model'])} {c['word']} "
                                 f"({', '.join(c['of_which_missing_the_forward_rule'])})" for c in un) + ".")
        out.append(line)
    out.append(f"- {s['exempt_cell_records']} exempt-cell records over all pools and CPU models (including rows with too few "
               f"jobs for a verdict). |D - 1| runs from {fmt(s['d_deviation_pct_min'], 3)}% to {fmt(s['d_deviation_pct_max'], 2)}%; "
               f"{s['exempt_cell_records_below_2pct']} records are below 2% and {s['exempt_cell_records_below_layout_floor']} are "
               "below the layout A/A half-width of their pool and CPU model.")
    ab = s["exempt_cells_with_aligned_ratio_above_point_limit"]
    names = sorted({(o["cpu_model"], o["cell_id"]) for o in ab})
    out.append(f"- Exempt cells with an aligned ratio above {s['forward_point_max_ratio']:g}, {len(ab)} records, "
               f"{len(names)} distinct cells: " + "; ".join(f"{short_cpu(c)} {i}" for c, i in names) + ".")
    return out


def block_of(text):
    a, b = text.index(MARKS[0]), text.index(MARKS[1])
    return a, b


def readme_block_ok(root, doc):
    """An empty list when the generated block of the README equals the rendering of doc (the differences otherwise)."""
    path = os.path.join(root, README)
    if not os.path.exists(path):
        return [f"{README} is missing"]
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    try:
        a, b = block_of(text)
    except ValueError:
        return [f"{README}: the generated-block markers are missing"]
    have = text[a + len(MARKS[0]):b].strip("\r\n")
    want = "\n".join(render(doc))
    if have.replace("\r\n", "\n") != want:
        return [f"{README}: the generated block differs from the rendering of {OUT}"]
    return []


def write_readme_block(root, doc):
    path = os.path.join(root, README)
    with open(path, encoding="utf-8", newline="") as fh:
        text = fh.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    a, b = block_of(text)
    new = text[:a + len(MARKS[0])] + nl + nl.join(render(doc)) + nl + text[b:]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(new)


# ---------------------------------------------------------------- verify and main

def dumps(doc):
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


def verify_file(path, doc):
    """The differences between the stored file at `path` and a freshly built document (empty when equal)."""
    if not os.path.exists(path):
        return [f"{path} is missing"]
    with open(path, encoding="utf-8") as fh:
        return same(json.load(fh), json.loads(dumps(doc)))


def main(argv):
    flags = set(argv[1:])
    if flags - {"--verify", "--report"}:
        print(__doc__)
        return 2
    doc = build()
    path = os.path.join(REPO, OUT)
    if doc["checks"]["problems"]:
        for p in doc["checks"]["problems"]:
            print("FAIL " + p)
        return 1
    if "--verify" in flags:
        diffs = verify_file(path, doc)
        rd = readme_block_ok(REPO, doc)
        if diffs or rd:
            print(f"FAIL {OUT} differs from a recomputation from the stored files:")
            for d in diffs + rd:
                print("   " + d)
            return 1
        print(f"   ok   {OUT} equals a recomputation ({len(doc['inputs'])} input files, "
              f"{doc['summary']['testable_rows']} verdict rows in {len(doc['pools'])} pools)")
        return 0
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dumps(doc))
    print(f"wrote {OUT}")
    if "--report" in flags:
        write_readme_block(REPO, doc)
        print(f"rewrote the generated block of {README}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
