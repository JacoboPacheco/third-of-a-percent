"""The noise of an identical binary at L2, pooled per CPU model, beside the L1 pair the written rules read.

Every job times one byte-identical A/A pair at the forward add's L1 cell (results.json, controls.aa); the verdict rules
read only that pair (harness/criteria-v3.json: an A/A half-width above the ceiling ends the verdict at INCONCLUSIVE).
harness/run.py also times the same identical-binary pair at every other requested size and keeps it in details.json under
"aa_extra"; nothing read those pairs. This script pools them per CPU model with harness/pool.py's two-level bootstrap
(read-only use of pool.pair_stat), next to the L1 pair, for four stored pools:

    s7        results/s7-pooled/pooled.json        the x86-64 pool the page reads
    s9-x86-c  results/s9-x86-c-pooled/pooled.json  the x86-64 replication set
    s8-arm    results/s8-arm-pooled/pooled.json    the Arm pool
    s9-arm-b  results/s9-arm-b-pooled/pooled.json  the Arm replication set

and it lists every "aa_extra" key that exists under results/ (the early-stage jobs also hold a RAM pair; those are pooled
per CPU model in their own section, descriptive only, not part of any pool).

Nothing here is a verdict. "rule_at_l2" states what the written ceiling clause would do if it read the L2 pair; no stored
verdict and no stored pool is changed, and the rule files are not touched.

    python robustness/aa_l2.py                 write robustness/aa-l2.json
    python robustness/aa_l2.py --report        also rewrite the generated block of robustness/README-aa-l2.md
    python robustness/aa_l2.py --verify        recompute everything and fail on any difference with the stored
                                               file, its input sha256s and the generated README block
    python robustness/aa_l2.py --verify --deep also re-bootstrap every stored per-job half-width (about a minute)

Statistic ids (they seed the generator, so they are part of the method): the L1 pair is pooled as "aa", exactly as
harness/pool.py pools it (so the recomputed pool must equal the stored pool block); an extra pair is pooled as
"aa_extra|<key>", for instance "aa_extra|k02_add_fwd.L2", the id scripts/build_site_data.py already uses for the Arm
pool's L2 pair (so the Arm figures here equal the ones arm64/README.md prints). A row whose pooled L2 half-width lies
within a factor of two of the ceiling is also pooled under SEEDS other ids ("aa_extra|<key>|seed1" ...), to show how
much the number moves with the random draws alone.
"""
import glob
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))

import pool  # noqa: E402  (read-only use: pair_stat, RESAMPLES)
import stats  # noqa: E402  (read-only use: summarize, for --deep)

OUT = "robustness/aa-l2.json"
README = "robustness/README-aa-l2.md"
MARKS = ("<!-- aa-l2:begin -->", "<!-- aa-l2:end -->")
CRITERIA = "harness/criteria-v3.json"
L2_KEY = "k02_add_fwd.L2"
RAM_KEY = "k02_add_fwd.RAM"
SEEDS = 20                       # alternative bootstrap seeds tried for a row whose L2 half-width is near the ceiling
DETAIL_ROOTS = ("results", "versions/results")   # where details.json files live

POOLS = [
    {"id": "s7", "pooled": "results/s7-pooled/pooled.json", "arch": "x86-64",
     "what": "the x86-64 pool the page reads"},
    {"id": "s9-x86-c", "pooled": "results/s9-x86-c-pooled/pooled.json", "arch": "x86-64",
     "what": "the x86-64 replication set, pooled alone"},
    {"id": "s8-arm", "pooled": "results/s8-arm-pooled/pooled.json", "arch": "arm64",
     "what": "the Arm pool (set A)"},
    {"id": "s9-arm-b", "pooled": "results/s9-arm-b-pooled/pooled.json", "arch": "arm64",
     "what": "the Arm replication set (set B), pooled alone"},
]


# ---------------------------------------------------------------- files

def posix(p):
    return p.replace("\\", "/")


def read_json(root, rel, hashes):
    """Parse a JSON file under root and record its sha256 (CRLF read as LF: a Windows checkout and a Linux clone agree)."""
    with open(os.path.join(root, rel), "rb") as f:
        raw = f.read()
    hashes[rel] = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    return json.loads(raw.decode("utf-8"))


def read_job(root, results_rel, hashes):
    """The few fields of one job this script uses (results.json and the details.json beside it)."""
    res = read_json(root, results_rel, hashes)
    det_rel = posix(os.path.join(os.path.dirname(results_rel), "details.json"))
    det = read_json(root, det_rel, hashes)
    aa = res["controls"]["aa"]
    if "a_ns" in aa and (det["aa"]["a_ns"] != aa["a_ns"] or det["aa"]["b_ns"] != aa["b_ns"]):
        raise ValueError(f"{det_rel}: the L1 pair in details.json is not the one in results.json controls.aa")
    # the raw samples of the L1 pair are in details.json (results.json holds them too from the criteria-v3 runs on);
    # the stored summary of the pair is results.json controls.aa
    l1 = {"a_ns": det["aa"]["a_ns"], "b_ns": det["aa"]["b_ns"], "ratio": aa["ratio"], "ci95": aa["ci95"],
          "half_width_pct": aa["half_width_pct"]}
    return {"results": results_rel, "details": det_rel,
            "model": res["run"]["runner"]["cpu_model"] or "unknown", "run": res["run"]["id"],
            "criteria_file": res["run"].get("criteria_file"),
            "reps": det.get("reps_per_side"), "sizes": det.get("sizes_requested"),
            "l1": l1, "extra": dict(det.get("aa_extra") or {})}


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


# ---------------------------------------------------------------- one statistic, one model

def side(ps, per_job_hw, ceiling):
    """The summary of one pooled A/A pair (ps is pool.pair_stat's result) and the per-job half-widths behind it."""
    return {"pooled_ratio": ps["ratio"], "ci95": list(ps["ci95"]), "half_width_pct": ps["half_width_pct"],
            "between_job_sd_pct": ps["between_job_sd_pct"],
            "per_job_ratio_min": min(ps["per_job"]), "per_job_ratio_max": max(ps["per_job"]),
            "per_job_half_width_median_pct": statistics.median(per_job_hw),
            "per_job_half_width_max_pct": max(per_job_hw),
            "jobs_above_ceiling": sum(1 for h in per_job_hw if h > ceiling)}


def rule_at_l2(jobs, stored_form, l2_hw, crit, minimum):
    """What the written clauses would do if they read the L2 pair instead of the L1 pair (a statement about the rule)."""
    v = crit["verdict"]
    ceiling = v["aa_half_width_max_pct"]
    limit_pct = max(v["forward_ci_hi_floor_pct"], v["forward_ci_hi_aa_multiplier"] * l2_hw)
    above = l2_hw > ceiling
    if jobs < minimum:
        effect = "too_few_jobs"
    elif above:
        effect = "already_inconclusive" if stored_form == "inconclusive" else "word_would_change_to_inconclusive"
    else:
        effect = "not_evaluated_limit_differs" if limit_pct != v["forward_ci_hi_floor_pct"] else "no_change"
    return {"ceiling_pct": ceiling, "pooled_above_ceiling": above, "forward_limit_pct_formula_at_l2": limit_pct,
            "effect": effect}


def model_row(cpu, block, jobs, crit, minimum, key=L2_KEY):
    ceiling = crit["verdict"]["aa_half_width_max_pct"]
    l1_pairs = [(j["l1"]["a_ns"], j["l1"]["b_ns"]) for j in jobs]
    l2_pairs = [(j["extra"][key]["a_ns"], j["extra"][key]["b_ns"]) for j in jobs]
    l1 = pool.pair_stat(cpu, "aa", l1_pairs)
    l2 = pool.pair_stat(cpu, f"aa_extra|{key}", l2_pairs)
    row = {"cpu_model": cpu, "jobs": len(jobs), "runs": sorted({j["run"] for j in jobs}),
           "testable": len(jobs) >= minimum,
           "l1": side(l1, [j["l1"]["half_width_pct"] for j in jobs], ceiling),
           "l2": side(l2, [j["extra"][key]["half_width_pct"] for j in jobs], ceiling)}
    row["l2_over_l1_half_width"] = row["l2"]["half_width_pct"] / row["l1"]["half_width_pct"]
    if ceiling / 2 <= row["l2"]["half_width_pct"] <= 2 * ceiling:
        hws = [pool.pair_stat(cpu, f"aa_extra|{key}|seed{i}", l2_pairs)["half_width_pct"] for i in range(1, SEEDS + 1)]
        row["l2_seed_sensitivity"] = {"seeds": SEEDS, "half_width_pct_min": min(hws), "half_width_pct_max": max(hws),
                                      "draws_above_ceiling": sum(1 for h in hws if h > ceiling)}
    if block is not None:
        stored = block["aa"]
        row["l1_matches_pool"] = not same({k: l1[k] for k in ("ratio", "ci95", "half_width_pct", "jobs", "per_job",
                                                              "between_job_sd_pct")},
                                          {k: stored[k] for k in ("ratio", "ci95", "half_width_pct", "jobs", "per_job",
                                                                  "between_job_sd_pct")})
        row["stored_form"] = block["verdict"]["form"]
        row["stored_aa_half_width_pct"] = stored["half_width_pct"]
        row["stored_forward_limit_pct"] = block["verdict"]["forward_limit_pct"]
        row["layout_aa_half_width_pct"] = {sz: block["layout_aa"][f"k02_add_fwd.{sz}"]["half_width_pct"]
                                           for sz in ("L1", "L2")}
        row["rule_at_l2"] = rule_at_l2(len(jobs), row["stored_form"], row["l2"]["half_width_pct"], crit, minimum)
    return row


# ---------------------------------------------------------------- pools

def pool_section(root, spec, crit, minimum, hashes, all_jobs):
    pdoc = read_json(root, spec["pooled"], hashes)
    base = os.path.dirname(spec["pooled"])
    jobs = []
    for inp in pdoc["inputs"]:
        rel = posix(os.path.normpath(os.path.join(base, inp["path"])))
        j = read_job(root, rel, hashes)
        if j["model"] != (inp["cpu_model"] or "unknown") or j["run"] != inp["run_id"]:
            raise ValueError(f"{rel}: model or run differs from the pooled file's input record")
        if L2_KEY not in j["extra"]:
            raise ValueError(f"{j['details']}: no aa_extra[{L2_KEY!r}]")
        jobs.append(j)
    all_jobs.extend((spec["id"], j) for j in jobs)
    rows = []
    for block in pdoc["cpus"]:
        cpu = block["cpu_model"]
        mine = [j for j in jobs if j["model"] == cpu]
        if len(mine) != block["jobs"]:
            raise ValueError(f"{spec['pooled']}: {cpu} has {block['jobs']} jobs, {len(mine)} read")
        rows.append(model_row(cpu, block, mine, crit, minimum))
    if sum(r["jobs"] for r in rows) != len(jobs):
        raise ValueError(f"{spec['pooled']}: the model rows do not cover every job")
    ceiling = crit["verdict"]["aa_half_width_max_pct"]
    return {"id": spec["id"], "arch": spec["arch"], "what": spec["what"], "pooled_file": spec["pooled"],
            "jobs": len(jobs), "runs": sorted({j["run"] for j in jobs}),
            "aa_extra_keys_in_jobs": sorted({k for j in jobs for k in j["extra"]}),
            "jobs_above_ceiling_l1": sum(1 for j in jobs if j["l1"]["half_width_pct"] > ceiling),
            "jobs_above_ceiling_l2": sum(1 for j in jobs if j["extra"][L2_KEY]["half_width_pct"] > ceiling),
            "models": rows}


# ---------------------------------------------------------------- what exists under results/

def inventory(root):
    """Every details.json under DETAIL_ROOTS (results/ and versions/results/): which aa_extra keys it holds, by run folder."""
    groups = {}
    files = sorted(f for r in DETAIL_ROOTS for f in glob.glob(os.path.join(root, *r.split("/"), "**", "details.json"),
                                                               recursive=True))
    for f in files:
        rel = posix(os.path.relpath(f, root))
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        keys = sorted(d["aa_extra"]) if "aa_extra" in d else None
        parts = rel.split("/")
        folder = "/".join(parts[:3]) if parts[0] == "versions" else parts[1]
        gk = (folder, json.dumps(keys), json.dumps(d.get("sizes_requested")), d.get("reps_per_side"))
        groups[gk] = groups.get(gk, 0) + 1
    rows = [{"folder": g[0], "aa_extra_keys": json.loads(g[1]), "sizes_requested": json.loads(g[2]),
             "reps_per_side": g[3], "details_files": n} for g, n in sorted(groups.items(), key=lambda t: tuple(str(x) for x in t[0]))]
    keys = sorted({k for r in rows for k in (r["aa_extra_keys"] or [])})
    return {"details_files": len(files), "distinct_keys": keys,
            "kernels": sorted({k.rsplit(".", 1)[0] for k in keys}),
            "sizes": sorted({k.rsplit(".", 1)[1] for k in keys}),
            "folders_without_aa_extra": sorted({r["folder"] for r in rows if r["aa_extra_keys"] is None}),
            "groups": rows}


def early_ram(root, crit, minimum, hashes, all_jobs):
    """The RAM pair of the early-stage jobs (outside every pool), pooled per CPU model; descriptive."""
    jobs = []
    for f in sorted(glob.glob(os.path.join(root, "results", "**", "details.json"), recursive=True)):
        rel = posix(os.path.relpath(f, root))
        with open(f, encoding="utf-8") as fh:
            if RAM_KEY not in (json.load(fh).get("aa_extra") or {}):
                continue
        j = read_job(root, posix(os.path.join(os.path.dirname(rel), "results.json")), hashes)
        jobs.append(j)
    all_jobs.extend(("early-ram", j) for j in jobs)
    rows = []
    for cpu in sorted({j["model"] for j in jobs}):
        rows.append(model_row(cpu, None, [j for j in jobs if j["model"] == cpu], crit, minimum, key=RAM_KEY))
    reps = sorted({j["reps"] for j in jobs})
    return {"key": RAM_KEY, "jobs": len(jobs), "reps_per_side": reps, "folders": sorted({j["results"].split("/")[1] for j in jobs}),
            "criteria_files": sorted({j["criteria_file"] or "none" for j in jobs}),
            "note": "early-stage jobs, outside every pool and not run under criteria-v3; descriptive only. In these rows "
                    "the 'l1' side is the job's own L1 pair and the 'l2' side is the RAM pair.",
            "models": rows}


# ---------------------------------------------------------------- the whole document

def build_all(root=REPO):
    hashes = {}
    all_jobs = []
    crit = read_json(root, CRITERIA, hashes)
    minimum = crit["v3"]["pooling"]["minimum_jobs"]
    pools = [pool_section(root, spec, crit, minimum, hashes, all_jobs) for spec in POOLS]
    inv = inventory(root)
    ram = early_ram(root, crit, minimum, hashes, all_jobs)
    changes, above, below = [], [], []
    for p in pools:
        for r in p["models"]:
            if not r["testable"]:
                continue
            tag = f"{p['id']}: {r['cpu_model']}"
            (above if r["rule_at_l2"]["pooled_above_ceiling"] else below).append(tag)
            if r["rule_at_l2"]["effect"] == "word_would_change_to_inconclusive":
                changes.append(tag)
    v = crit["verdict"]
    problems = [f"{p['id']}: {r['cpu_model']}: the recomputed L1 pool differs from the stored pool block"
                for p in pools for r in p["models"] if not r["l1_matches_pool"]]
    doc = {"kind": "aa-l2",
           "script": "robustness/aa_l2.py",
           "method": {"pooling": "harness/pool.py pair_stat (two-level bootstrap, splitmix64), read-only",
                      "resamples": pool.RESAMPLES,
                      "l1_statistic_id": "aa", "extra_statistic_id": "aa_extra|<key>", "seeds": SEEDS,
                      "per_job_half_width": "as stored by harness/run.py (stats.summarize, 10000 resamples) in "
                                            "results.json controls.aa (L1) and details.json aa_extra (other sizes); "
                                            "--deep re-bootstraps them",
                      "jobs_above_ceiling": "per-job half-width strictly above the ceiling (the rule's comparison)"},
           "criteria": {"file": CRITERIA, "aa_half_width_max_pct": v["aa_half_width_max_pct"],
                        "forward_ci_hi_floor_pct": v["forward_ci_hi_floor_pct"],
                        "forward_ci_hi_aa_multiplier": v["forward_ci_hi_aa_multiplier"], "minimum_jobs": minimum},
           "pools": pools,
           "inventory": inv,
           "early_ram": ram,
           "rule_at_l2": {"statement": "What the written A/A ceiling clause would do if it read the L2 pair. This is a "
                                       "statement about the rule: no stored verdict, pool or rule file is changed.",
                          "models_above_ceiling": above, "models_below_ceiling": below,
                          "stored_words_that_would_change": changes},
           "checks": {"problems": problems},
           "inputs": dict(sorted(hashes.items()))}
    return doc, all_jobs


def build(root=REPO):
    return build_all(root)[0]


# ---------------------------------------------------------------- the generated README block

def f(x, nd=2):
    return f"{x:.{nd}f}"


def render(doc):
    ceil = doc["criteria"]["aa_half_width_max_pct"]
    c = f"{ceil:g}"
    out = []
    out += ["### Noise of an identical binary, L1 against L2 (generated)", "",
            f"The pooled A/A half-width is the half-width of the 95% interval of the pooled ratio of a binary to a "
            f"byte-identical copy of itself (`harness/pool.py`, two-level bootstrap). The ceiling the written rule reads "
            f"at L1 is {c}%.", "",
            f"| pool | CPU model | jobs | L1 pooled half-width % | L2 pooled half-width % | L2 / L1 | L2 pooled ratio [95% interval] | "
            f"L2 per-job half-width % median / max | jobs above {c}% at L1 / L2 | L2 between-job sd % |",
            "|---|---|---:|---:|---:|---:|---|---|---|---:|"]
    for p in doc["pools"]:
        for r in p["models"]:
            l1, l2 = r["l1"], r["l2"]
            sd = "n/a" if l2["between_job_sd_pct"] is None else f(l2["between_job_sd_pct"])
            note = "" if r["testable"] else " (too few jobs)"
            out.append(f"| {p['id']} | {r['cpu_model']}{note} | {r['jobs']} | {f(l1['half_width_pct'], 3)} | "
                       f"{f(l2['half_width_pct'], 3)} | {f(r['l2_over_l1_half_width'], 1)} | {f(l2['pooled_ratio'], 4)} "
                       f"[{f(l2['ci95'][0], 4)}, {f(l2['ci95'][1], 4)}] | {f(l2['per_job_half_width_median_pct'])} / "
                       f"{f(l2['per_job_half_width_max_pct'])} | {l1['jobs_above_ceiling']} / {l2['jobs_above_ceiling']} | {sd} |")
    out += ["", f"### The written A/A clause read at L2 (generated)", "",
            f"| pool | CPU model | jobs | stored word | L2 pooled half-width % | above the {c}% ceiling | effect if the rule read L2 |",
            "|---|---|---:|---|---:|---|---|"]
    words = {"too_few_jobs": "none: too few jobs for a verdict", "already_inconclusive": "none: stored word already inconclusive",
             "word_would_change_to_inconclusive": f"{{form}} would become inconclusive",
             "no_change": "none: below the ceiling, forward limit unchanged",
             "not_evaluated_limit_differs": "below the ceiling, forward limit would differ (not evaluated)"}
    for p in doc["pools"]:
        for r in p["models"]:
            ru = r["rule_at_l2"]
            out.append(f"| {p['id']} | {r['cpu_model']} | {r['jobs']} | {r['stored_form']} | "
                       f"{f(r['l2']['half_width_pct'], 3)} | {'yes' if ru['pooled_above_ceiling'] else 'no'} | "
                       f"{words[ru['effect']].format(form=r['stored_form'])} |")
    ch = doc["rule_at_l2"]["stored_words_that_would_change"]
    ab = doc["rule_at_l2"]["models_above_ceiling"]
    out += ["", "### Facts read from the data (generated)", ""]
    out.append(f"- Read at L2, the ceiling clause would change the stored word of {len(ch)} CPU model row(s) with at least "
               f"{doc['criteria']['minimum_jobs']} jobs" + (": " + "; ".join(ch) + "." if ch else "."))
    out.append(f"- {len(ab)} of {len(ab) + len(doc['rule_at_l2']['models_below_ceiling'])} such rows have a pooled L2 "
               f"half-width above the ceiling" + (": " + "; ".join(ab) + "." if ab else "."))
    for p in doc["pools"]:
        out.append(f"- {p['id']}: {p['jobs']} jobs in {len(p['runs'])} run(s); jobs above the ceiling at L1 / L2: "
                   f"{p['jobs_above_ceiling_l1']} / {p['jobs_above_ceiling_l2']}; `aa_extra` keys present in the jobs: "
                   + ", ".join(f"`{k}`" for k in p["aa_extra_keys_in_jobs"]) + ".")
    inv = doc["inventory"]
    out.append(f"- Under `results/` and `versions/results/` there are {inv['details_files']} `details.json` files; the distinct `aa_extra` keys are "
               + ", ".join(f"`{k}`" for k in inv["distinct_keys"])
               + f" (kernel: {', '.join(inv['kernels'])}; sizes: {', '.join(inv['sizes'])}). Folders whose jobs hold no "
               f"`aa_extra`: " + (", ".join(f"`{x}`" for x in inv["folders_without_aa_extra"]) or "none") + ".")
    ram = doc["early_ram"]
    out.append(f"- The RAM pair (`{ram['key']}`) exists only in {ram['jobs']} early-stage jobs outside every pool "
               f"({', '.join(str(x) for x in ram['reps_per_side'])} repetitions per side). Pooled per CPU model: "
               + "; ".join(f"{r['cpu_model']} {r['jobs']} job(s), half-width {f(r['l2']['half_width_pct'])}%, "
                           f"{r['l2']['jobs_above_ceiling']} above the ceiling" for r in ram["models"]) + ".")
    return out


def block_of(text):
    a, b = text.index(MARKS[0]), text.index(MARKS[1])
    return a, b


def readme_block_ok(root, doc):
    """True when the generated block of the README equals the rendering of doc (the diffs otherwise)."""
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


# ---------------------------------------------------------------- verify

def dumps(doc):
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


def verify_file(path, doc):
    """The differences between the stored file at `path` and a freshly built document (empty when equal)."""
    if not os.path.exists(path):
        return [f"{path} is missing"]
    with open(path, encoding="utf-8") as fh:
        return same(json.load(fh), json.loads(dumps(doc)))


def deep_check(all_jobs):
    """Re-bootstrap every stored per-job pair with harness/stats.py; the differences from the stored numbers."""
    bad = []
    for label, j in all_jobs:
        for name, pair in [("l1", j["l1"])] + [(k, v) for k, v in j["extra"].items()
                                                if k in (L2_KEY, RAM_KEY)]:
            s = stats.summarize(pair["a_ns"], pair["b_ns"])
            for k in ("ratio", "half_width_pct"):
                if not math.isclose(s[k], pair[k], rel_tol=1e-12):
                    bad.append(f"{label} {j['results']} {name} {k}: stored {pair[k]!r}, recomputed {s[k]!r}")
            if [round(x, 12) for x in s["ci95"]] != [round(x, 12) for x in pair["ci95"]]:
                bad.append(f"{label} {j['results']} {name} ci95 differs")
    return bad


def main(argv):
    flags = set(argv[1:])
    if flags - {"--verify", "--report", "--deep"} or ("--deep" in flags and "--verify" not in flags):
        print(__doc__)
        return 2
    doc, all_jobs = build_all()
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
        if "--deep" in flags:
            bad = deep_check(all_jobs)
            if bad:
                print("FAIL stored per-job half-widths differ from a re-bootstrap:")
                for b in bad[:10]:
                    print("   " + b)
                return 1
        print(f"   ok   {OUT} equals a recomputation ({len(doc['inputs'])} input files, "
              f"{sum(p['jobs'] for p in doc['pools'])} jobs in {len(doc['pools'])} pools"
              + (", per-job half-widths re-bootstrapped" if "--deep" in flags else "") + ")")
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
