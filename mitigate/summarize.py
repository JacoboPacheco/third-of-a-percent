#!/usr/bin/env python3
"""Reads mitigate results.json files and prints the tables of mitigate/README.md (markdown).

  python mitigate/summarize.py results/mitigate-run-<id>          # every job file under the folder
  python mitigate/summarize.py out/results.json                     # one job
  python mitigate/summarize.py --check results/mitigate-run-<id>    # recompute every ratio and interval

Plain standard-library Python: runs on the laptop. The reading rules are mitigate/criteria.json.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stats  # noqa: E402

AA_LIMIT_PCT = 2.0
SIZES = ("L1", "L2")


def load(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, "**", "results.json"), recursive=True))
        else:
            files.append(p)
    out = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            r = json.load(fh)
        r["_file"] = f
        out.append(r)
    return out


def short_cpu(m):
    m = (m or "?").replace("(R)", "").replace("(TM)", "").replace(" CPU", "")
    for a, b in (("AMD EPYC ", "EPYC "), ("Intel Xeon Platinum ", "Xeon "), (" 64-Core Processor", ""),
                 (" 96-Core Processor", ""), (" 48-Core Processor", ""), (" 32-Core Processor", "")):
        m = m.replace(a, b)
    m = re.sub(r" \d+-Core Processor", "", m)
    return m.split(" @")[0].strip()


def job_usable(r):
    for k in r["kernels"].values():
        for sc, aa in k.get("aa", {}).items():
            if aa["half_width_pct"] > AA_LIMIT_PCT:
                return False
    return True


def cell_usable(r, kname, sc):
    """The per-cell reading (written AFTER run 38256846461, beside the criteria's whole-job rule):
    a kernel and size counts in a job when its own A/A half-width is at most 2%."""
    return r["kernels"][kname]["aa"][sc]["half_width_pct"] <= AA_LIMIT_PCT


def recovered_job(r, kname, v):
    """criteria.json 'recovered' for one job: at L1 and L2, ci95 hi of vs_original_aligned <= 1 + A/A hw."""
    k = r["kernels"][kname]
    t = k["variants"][v].get("timing")
    if not t:
        return None
    for sc in SIZES:
        if sc not in t:
            return None
        hi = t[sc]["vs_original_aligned"]["ci95"][1]
        if hi > 1 + k["aa"][sc]["half_width_pct"] / 100:
            return False
    return True


def check(results):
    bad = 0
    for r in results:
        for kname, k in r["kernels"].items():
            prs = [("aa", sc, k["aa"][sc]) for sc in k.get("aa", {})]
            for v, info in k["variants"].items():
                for sc, t in info.get("timing", {}).items():
                    for key in ("vs_original", "vs_own", "vs_original_aligned", "vs_own_aligned"):
                        if isinstance(t[key], dict):
                            prs.append((f"{v}.{key}", sc, t[key]))
            for name, sc, p in prs:
                s = stats.summarize(p["a_ns"], p["b_ns"])
                if s["ratio"] != p["ratio"] or s["ci95"] != p["ci95"] or len(p["a_ns"]) != 20 or len(p["b_ns"]) != 20:
                    bad += 1
                    print(f"MISMATCH {r['_file']} {kname}.{name}.{sc}")
    n = sum(1 for r in results for k in r["kernels"].values() for _ in k.get("aa", {}))
    print(f"check: {len(results)} files, {'all ratios and intervals recomputed exactly' if not bad else f'{bad} mismatches'}"
          f" ({n} A/A pairs among them)")
    return 1 if bad else 0


def fmt_pair(p):
    return f"{p['ratio']:.2f} [{p['ci95'][0]:.2f}, {p['ci95'][1]:.2f}]"


def headline(results, by_cpu, cpus):
    """One row per loop shape and rewrite: the aligned FAST / ORIGINAL NONE median, its range across
    the jobs of each CPU model (cells whose own A/A was above 2% left out), L1 and L2."""
    print("| loop shape | rewrite | keeps safety | " + " | ".join(f"{c} L1 / L2" for c in cpus)
          + " | recovers, per CPU (criteria: whole usable jobs) | usable cells within A/A noise | readability cost |")
    print("|---" * (6 + len(cpus)) + "|")
    names = []
    for r in results:
        for kn in r["kernels"]:
            if kn not in names:
                names.append(kn)
    for kname in names:
        files = [r for r in results if kname in r["kernels"]]
        k = max((r["kernels"][kname] for r in files), key=lambda x: len(x["variants"]))
        for v, info in k["variants"].items():
            cols = []
            for c in cpus:
                parts = []
                for sc in SIZES:
                    vals = [r["kernels"][kname]["variants"][v]["timing"][sc]["vs_original_aligned"]["ratio"]
                            for r in by_cpu[c] if kname in r["kernels"] and v in r["kernels"][kname]["variants"]
                            and "timing" in r["kernels"][kname]["variants"][v] and cell_usable(r, kname, sc)]
                    if not vals:
                        parts.append("-")
                    elif max(vals) - min(vals) < 0.005:
                        parts.append(f"{vals[0]:.2f}")
                    else:
                        parts.append(f"{min(vals):.2f}-{max(vals):.2f}")
                cols.append(" / ".join(parts))
            per = []
            for c in cpus:
                rec = [recovered_job(r, kname, v) for r in by_cpu[c] if kname in r["kernels"] and job_usable(r)
                       and v in r["kernels"][kname]["variants"]]
                per.append(f"{c}: " + ("yes" if rec and all(rec) else ("no usable job" if not rec else "no")))
            strict = "; ".join(per)
            within = [r["kernels"][kname]["variants"][v]["timing"][sc]["vs_original_aligned"]["ci95"][1]
                      <= 1 + r["kernels"][kname]["aa"][sc]["half_width_pct"] / 100
                      for r in files if v in r["kernels"][kname]["variants"]
                      and "timing" in r["kernels"][kname]["variants"][v] for sc in SIZES if cell_usable(r, kname, sc)]
            print(f"| {k['shape']} | {v}: {info['what']} | {'yes' if info['keeps_safety'] else 'NO'} | "
                  + " | ".join(cols) + f" | {strict} | {sum(within)}/{len(within)} | {info['readability_cost']} |")
    return 0


def main(argv):
    do_check = "--check" in argv
    paths = [a for a in argv if not a.startswith("--")]
    results = load(paths)
    if not results:
        print("no results.json found")
        return 1
    if do_check:
        return check(results)
    by_cpu = {}
    for r in results:
        by_cpu.setdefault(short_cpu(r["run"]["cpu_model"]), []).append(r)
    cpus = sorted(by_cpu)
    if "--headline" in argv:
        return headline(results, by_cpu, cpus)
    print(f"Files: {len(results)}; CPU models: " + ", ".join(
        f"{c} ({len(by_cpu[c])} job{'s' if len(by_cpu[c]) > 1 else ''})" for c in cpus) + "\n")
    print("A/A half-width per job (byte-identical copy of the original NONE build), % at L1 / L2:\n")
    for r in results:
        hws = [f"{kn} {k['aa']['L1']['half_width_pct']:.2f}/{k['aa']['L2']['half_width_pct']:.2f}"
               for kn, k in r["kernels"].items() if "L1" in k.get("aa", {}) and "L2" in k["aa"]]
        print(f"- {short_cpu(r['run']['cpu_model'])}, run {r['run'].get('id')} job {r['run'].get('job')}: " + "; ".join(hws)
              + ("" if job_usable(r) else "  NOT USABLE (A/A above 2%)"))
    print()
    kernel_names = []
    for r in results:
        for kn in r["kernels"]:
            if kn not in kernel_names:
                kernel_names.append(kn)
    for kname in kernel_names:
        files = [r for r in results if kname in r["kernels"]]
        k = max((r["kernels"][kname] for r in files), key=lambda x: len(x["variants"]))
        variants = list(k["variants"])
        print(f"### {kname} ({k['shape']}; original kernels/{k['original_kernel']}.cpp)\n")
        print("| variant | what | vectorized NONE / FAST | ud2 in kernel NONE / FAST | short input NONE / FAST | keeps safety |")
        print("|---|---|---|---|---|---|")
        for v, info in k["variants"].items():
            b = info["builds"]

            def vec(m):
                x = b[m]["vectorization"]["vectorized"]
                s = "yes" if b[m]["simd_innermost_loops"] else "no"
                return s + ("" if x is None or (x is True) == (s == "yes") else f" (remark {x})")
            print(f"| {v} | {info['what']} | {vec('none')} / {vec('fast')} | {b['none']['traps']} / {b['fast']['traps']} | "
                  f"{info['safety']['none']['outcome']} / {info['safety']['fast']['outcome']} | "
                  f"{'yes' if info['keeps_safety'] else 'NO (UNSAFE)'} |")
        print()
        if not any("timing" in r["kernels"][kname]["variants"]["orig"] for r in files):
            continue
        hdr = " | ".join(f"{c} L1 | {c} L2" for c in cpus)

        def series(v, c, sc, key):
            """(pair, usable) for every job of CPU c that timed variant v at size sc."""
            out = []
            for r in by_cpu[c]:
                kk = r["kernels"].get(kname)
                t = kk and kk["variants"].get(v, {}).get("timing")
                if not t or sc not in t:
                    continue
                p = t[sc][key]
                if not isinstance(p, dict):  # the original: vs_own is vs_original
                    p = t[sc][key.replace("own", "original")]
                out.append((p, cell_usable(r, kname, sc), kk["aa"][sc]["half_width_pct"], r))
            return out

        print("FAST time / ORIGINAL NONE time, loops aligned: median ratio [95% CI], one line per job; "
              "* = that kernel and size had an A/A half-width above 2% in that job:\n")
        print(f"| variant | {hdr} | keeps safety | recovers (criteria, whole job) | recovers (per cell) | worst ratio |")
        print("|---" * (5 + 2 * len(cpus)) + "|")
        for v in variants:
            cells, worst, per_cell, covered = [], 0.0, [], True
            for c in cpus:
                for sc in SIZES:
                    ser = series(v, c, sc, "vs_original_aligned")
                    cells.append("<br>".join(fmt_pair(p) + ("" if ok else "*") for p, ok, _, _ in ser) or "-")
                    covered &= any(ok for _, ok, _, _ in ser)
                    for p, ok, hw, _ in ser:
                        if ok:
                            worst = max(worst, p["ratio"])
                            per_cell.append(p["ci95"][1] <= 1 + hw / 100)
            rec = [recovered_job(r, kname, v) for r in files if job_usable(r) and v in r["kernels"][kname]["variants"]]
            strict = "yes" if rec and all(rec) else ("no usable job" if not rec else "no")
            pc = "yes" if per_cell and all(per_cell) and covered else "no"
            safe = "yes" if k["variants"][v]["keeps_safety"] else "NO"
            print(f"| {v} | " + " | ".join(cells) + f" | {safe} | {strict} | {pc} | {worst:.2f} |")
        print("\nFAST / the variant's own NONE, loops aligned (what hardening costs this rewrite):\n")
        print(f"| variant | {hdr} |")
        print("|---" * (1 + 2 * len(cpus)) + "|")
        for v in variants:
            cells = ["<br>".join(fmt_pair(p) + ("" if ok else "*") for p, ok, _, _ in series(v, c, sc, "vs_own_aligned"))
                     or "-" for c in cpus for sc in SIZES]
            print(f"| {v} | " + " | ".join(cells) + " |")
        print("\nAs compiled (no alignment), FAST / ORIGINAL NONE, median ratio per job:\n")
        print(f"| variant | {hdr} |")
        print("|---" * (1 + 2 * len(cpus)) + "|")
        for v in variants:
            cells = [" / ".join(f"{p['ratio']:.2f}" + ("" if ok else "*") for p, ok, _, _ in series(v, c, sc, "vs_original"))
                     or "-" for c in cpus for sc in SIZES]
            print(f"| {v} | " + " | ".join(cells) + " |")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
