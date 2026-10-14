#!/usr/bin/env python3
"""Non-PGO against PGO, per program and per CPU model (pgo/PLAN.md "What the result is compared to").

Usage: python pgo/analyze.py [--pgo results/pgo-pooled/pgo.json] [--baseline results/realworld-pooled/realworld.json]
                             [--write]
Prints the report; --write also writes pgo/report.md. With no PGO pooled file it prints (and writes)
the "no PGO result yet" text, so pgo/check.py can pass before the first run.

The comparison rule (fixed in PLAN.md before any run): each FAST/NONE interval (as compiled and aligned)
is widened by its own row's A/A half-width on both sides; "PGO lower" if both PGO intervals lie wholly
below both non-PGO intervals, "PGO higher" if wholly above, otherwise "no difference detected". Only
rows with a reading (>= 3 jobs) on both sides are compared.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_PGO = os.path.join(REPO, "results", "pgo-pooled", "pgo.json")
DEFAULT_BASE = os.path.join(REPO, "results", "realworld-pooled", "realworld.json")
REPORT = os.path.join(HERE, "report.md")
NO_RESULT = ("# PGO column: report\n\n"
             "No PGO result yet: `.github/workflows/pgo.yml` has not been run. The rules this report will follow "
             "are in `pgo/PLAN.md`, written before any PGO build.\n")


def fmt(stat):
    r, (lo, hi) = stat["ratio"], stat["ci95"]
    return f"{r:.3f} [{lo:.3f}, {hi:.3f}]"


def _cell(row, pair):
    p = row["pairs"].get(pair)
    return p["time"] if p else None


def _hw(row):
    aa = _cell(row, "aa")
    return aa["half_width_pct"] if aa else None


def has_reading(row):
    rd = row.get("reading")
    return bool(rd) and rd.get("reading") not in (None, "too few jobs", "failed")


def compare(base_row, pgo_row):
    """'PGO lower' | 'PGO higher' | 'no difference detected' | 'not compared (reason)'."""
    if base_row is None:
        return "not compared (row missing in the non-PGO pool)"
    if not has_reading(base_row):
        return "not compared (non-PGO: no reading)"
    if not has_reading(pgo_row):
        return "not compared (PGO: no reading)"
    hb, hp = _hw(base_row), _hw(pgo_row)
    lo_all, hi_all = True, True
    for pair in ("fast", "aligned"):
        b, p = _cell(base_row, pair), _cell(pgo_row, pair)
        if b is None or p is None:
            return "not compared (a column is missing)"
        b_lo, b_hi = b["ci95"][0] - hb / 100.0, b["ci95"][1] + hb / 100.0
        p_lo, p_hi = p["ci95"][0] - hp / 100.0, p["ci95"][1] + hp / 100.0
        lo_all &= p_hi < b_lo
        hi_all &= p_lo > b_hi
    if lo_all:
        return "PGO lower"
    if hi_all:
        return "PGO higher"
    return "no difference detected"


def _by_row(block):
    return {r["row"]: r for r in block["rows"]}


def _short(rd):
    if not rd:
        return "-"
    k = rd.get("reading")
    if k == "not detectable":
        return f"not detectable, at most {rd['at_most_pct']:.2f}%"
    return {"detectably slower": "slower", "detectably faster": "faster"}.get(k, rd.get("text", "-"))


def render_cpu(pgo_block, base_block):
    lines = [f"### {pgo_block['cpu_model']}", ""]
    lines.append(f"PGO: {pgo_block['jobs']} jobs, runs {', '.join(pgo_block['runs'])}. "
                 + (f"Non-PGO: {base_block['jobs']} jobs, runs {', '.join(base_block['runs'])}." if base_block
                    else "Non-PGO: this CPU model is not in the non-PGO pool."))
    lines += ["", "FAST/NONE time ratio with its 95% interval, as compiled and with `-falign-loops=64`:", "",
              "| row | non-PGO as compiled | non-PGO aligned | non-PGO reading | PGO as compiled | PGO aligned | PGO reading | PGO against non-PGO |",
              "|---|---|---|---|---|---|---|---|"]
    base_rows = _by_row(base_block) if base_block else {}
    for r in pgo_block["rows"]:
        b = base_rows.get(r["row"])
        bf, ba = (_cell(b, "fast"), _cell(b, "aligned")) if b else (None, None)
        pf, pa = _cell(r, "fast"), _cell(r, "aligned")
        lines.append("| " + " | ".join([
            r["row"], fmt(bf) if bf else "-", fmt(ba) if ba else "-", _short(b.get("reading")) if b else "-",
            fmt(pf) if pf else "-", fmt(pa) if pa else "-", _short(r.get("reading")), compare(b, r)]) + " |")
    lines += ["", "The PGO runs' own floors and checks:", "",
              "| row | A/A half-width | layout A/A (PGO NONE aligned / PGO NONE) | process wall time FAST/NONE | outputs identical | reading |",
              "|---|---|---|---|---|---|"]
    for r in pgo_block["rows"]:
        hw = _hw(r)
        lay = _cell(r, "layout")
        wall = r["pairs"].get("fast", {}).get("wall")
        ok = "exact" if r.get("checksums_exact_match") else ("rounded only" if r.get("checksums_rounded_match") else "NO")
        lines.append("| " + " | ".join([
            r["row"], f"{hw:.2f}%" if hw is not None else "-", fmt(lay) if lay else "-", fmt(wall) if wall else "-",
            ok, r.get("reading", {}).get("text", "-")]) + " |")
    lines.append("")
    return lines


def _warn(e):
    w = e["profile_warnings"]
    return f"{w['out_of_date']} / {w['missing']}"


def render_builds(ctx):
    lines = ["## What the PGO builds are", "",
             "| program | traps (ud2) PGO NONE / PGO FAST | profile warnings (out of date / missing) NONE, FAST | "
             "census lost locations still vectorized in PGO NONE / in PGO FAST (lost here too) | profile functions NONE / FAST |",
             "|---|---|---|---|---|"]
    for prog in sorted(ctx):
        n, f = ctx[prog].get("none"), ctx[prog].get("fast")
        if not n or not f:
            lines.append(f"| {prog} | - | - | only one mode built | - |")
            continue
        nl = {x["location"]: x["vectorized"] for x in n["census_lost_locations"]}
        fl = {x["location"]: x["vectorized"] for x in f["census_lost_locations"]}
        locs = sorted(nl)
        vn = sum(1 for k in locs if nl[k] > 0)
        vf = sum(1 for k in locs if fl.get(k, 0) > 0)
        lost = sum(1 for k in locs if nl[k] > fl.get(k, 0))
        lines.append(f"| {prog} | {n['traps']['pgo']} / {f['traps']['pgo']} | {_warn(n)}, {_warn(f)} | "
                     f"{vn} / {vf} of {len(locs)} ({lost} lost here too) | "
                     f"{n['profile']['functions']} / {f['profile']['functions']} |")
    lines += ["", "Training input equals the timed input (PLAN.md, limits): a PGO result here is an upper bound on what PGO "
                  "does for these workloads. The census lost locations are those of `realworld/programs.json`.", ""]
    return lines


def render(pgo, base):
    if pgo is None:
        return NO_RESULT
    base_cpus = {b["cpu_model"]: b for b in base["cpus"]} if base else {}
    lines = ["# PGO column: report", "",
             "Generated by `pgo/analyze.py` from the pooled PGO file and `results/realworld-pooled/realworld.json`; "
             "rules in `pgo/PLAN.md` (written before any PGO build). Whatever it says is published.",
             "", f"PGO runs: {', '.join(pgo['runs'])}. A CPU model needs at least {pgo['minimum_jobs']} jobs for a reading.",
             "", "## Per CPU model", ""]
    for b in pgo["cpus"]:
        lines += render_cpu(b, base_cpus.get(b["cpu_model"]))
    tally = {}
    for b in pgo["cpus"]:
        bb = base_cpus.get(b["cpu_model"])
        rows = _by_row(bb) if bb else {}
        for r in b["rows"]:
            k = compare(rows.get(r["row"]), r)
            k = "not compared" if k.startswith("not compared") else k
            tally.setdefault(b["cpu_model"], {}).setdefault(k, []).append(r["row"])
    lines += ["## Summary of the comparison", ""]
    for m in sorted(tally):
        parts = [f"{k}: {len(v)} ({', '.join(v)})" for k, v in sorted(tally[m].items())]
        lines.append(f"- {m}: " + "; ".join(parts))
    lines.append("")
    lines += render_builds(pgo.get("pgo_context", {}))
    return "\n".join(lines).rstrip() + "\n"


def load(path):
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgo", default=DEFAULT_PGO)
    ap.add_argument("--baseline", default=DEFAULT_BASE)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report", default=REPORT)
    a = ap.parse_args(argv)
    pgo, base = load(a.pgo), load(a.baseline)
    if pgo is not None and base is None:
        print(f"note: no non-PGO pooled file at {a.baseline}: the tables show PGO only", file=sys.stderr)
    text = render(pgo, base)
    print(text)
    if a.write:
        with open(a.report, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
