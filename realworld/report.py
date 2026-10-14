#!/usr/bin/env python3
"""Renders the README tables of the real-program study from the pooled file (realworld/check.py
demands that realworld/README.md carries exactly this text between its realworld:tables markers).

Usage: python realworld/report.py [--pooled <realworld.json>] [--write]
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT = os.path.join(REPO, "results", "realworld-pooled", "realworld.json")


def _iv(s):
    return f"{s['ratio']:.3f} [{s['ci95'][0]:.3f}, {s['ci95'][1]:.3f}]"


def _pct(x, digits=2):
    return "-" if x is None else f"{100 * x:.{digits}f}%"


def _rows_meta():
    with open(os.path.join(HERE, "programs.json"), encoding="utf-8") as f:
        return {r["row"]: r for r in json.load(f)["rows"]}


def render(pooled_path=DEFAULT):
    with open(pooled_path, encoding="utf-8") as f:
        d = json.load(f)
    meta = _rows_meta()
    prof = {k: v[0] for k, v in d["context"]["profiles"].items()}
    builds = {k: v[0] for k, v in d["context"]["builds"].items()}
    out = []
    minimum = d["minimum_jobs"]
    blocks = sorted(d["cpus"], key=lambda b: (-b["jobs"], b["cpu_model"]))
    for b in blocks + [d["all_runners"]]:
        enough = b["jobs"] >= minimum
        if b is d["all_runners"]:
            title = f"All runners pooled ({b['jobs']} jobs; descriptive, mixes CPU models, no reading)"
        else:
            title = f"{b['cpu_model']} ({b['jobs']} jobs, {len(b['runs'])} run{'s' if len(b['runs']) != 1 else ''})"
            if not enough:
                title += f": fewer than {minimum} jobs, numbers shown, no reading"
        out.append(f"**{title}**\n")
        out.append("| row | FAST/NONE, time [95%] | loops aligned [95%] | own A/A half-width | layout A/A (NONE aligned / NONE) "
                   "| process wall time FAST/NONE | reading |")
        out.append("|---|---|---|---|---|---|---|")
        for r in b["rows"]:
            P = r["pairs"]
            label = r["row"] + (" (control)" if meta.get(r["row"], {}).get("control") else "") + \
                (" (options chosen to run lost loops)" if meta.get(r["row"], {}).get("chosen_to_run_lost_loops") else "")
            reading = r.get("reading", {}).get("text", "-") if (enough and b is not d["all_runners"]) else "-"
            cell = lambda k, m="time": _iv(P[k][m]) if k in P else "-"  # noqa: E731
            hw = f"{P['aa']['time']['half_width_pct']:.2f}%" if "aa" in P else "-"
            out.append(f"| {label} | {cell('fast')} | {cell('aligned')} | {hw} | {cell('layout')} | "
                       f"{cell('fast', 'wall')} | {reading} |")
        out.append("")
    out.append("**Instructions and where the lost loops sit** (Cachegrind, one workload iteration, the build run's "
               "binaries; instructions, not time)\n")
    out.append("| row | instructions FAST/NONE | lost-loop lines, share of NONE / FAST | functions holding a lost loop, "
               "share of NONE / FAST | functions found / listed | ud2 traps NONE / FAST | census lost locations lost here too |")
    out.append("|---|---|---|---|---|---|---|")
    for name, m in meta.items():
        p = prof.get(name)
        bi = builds.get(m["program"])
        if p is None or bi is None:
            continue
        ins = p["instructions"]["ratio"]
        out.append(f"| {name} | {'-' if ins is None else f'{ins:.4f}'} | "
                   f"{_pct(p['loop_lines_share']['none'], 3)} / {_pct(p['loop_lines_share']['fast'], 3)} | "
                   f"{_pct(p['functions_share']['none'], 3)} / {_pct(p['functions_share']['fast'], 3)} | "
                   f"{p['functions_matched']} / {p['functions_listed']} | {bi['traps']['none']} / {bi['traps']['fast']} | "
                   f"{bi['lost_here_too']} of {bi['lost_locations']} |")
    out.append("")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pooled", default=DEFAULT)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    text = render(a.pooled)
    if not a.write:
        sys.stdout.write(text)
        return 0
    readme = os.path.join(HERE, "README.md")
    with open(readme, encoding="utf-8") as f:
        cur = f.read()
    new, n = re.subn(r"(<!-- realworld:tables:start -->\n).*?(<!-- realworld:tables:end -->)",
                     lambda m: m.group(1) + text + m.group(2), cur, flags=re.S)
    if n != 1:
        raise SystemExit("README: realworld:tables markers not found")
    with open(readme, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
