#!/usr/bin/env python3
"""Pools the real-program jobs per CPU model (realworld/PLAN.md "Timing" and "Rules for the claims").

Usage: python realworld/pool_rw.py <out.json> <dir or results-job json> [...] [--build b.json ...] [--profile p.json ...]
  a dir means every results-*.json under it (recursively), plus build-*.json and profile-*.json found
  there, which are attached as context (instruction ratios, profile shares, traps, remarks).

The statistics are harness/pool.py's, imported unchanged: for each pair, r_j = median(B)/median(A)
inside job j, the pooled ratio is the geometric mean over jobs, and the 95 % interval is the
two-level bootstrap (jobs, then repetitions within each job; 2000 resamples; splitmix64 seeded from
the CPU model and the statistic id "rw|<row>|<pair>|<time or wall>").
"""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "harness"))
import common  # noqa: E402
import pool  # noqa: E402  (harness/pool.py, not edited)

MINIMUM_JOBS = 3
ALL = "all runners (descriptive: mixes CPU models)"
METRICS = {"time": ("a_ns", "b_ns"), "wall": ("a_wall_ns", "b_wall_ns")}


def find_inputs(paths):
    jobs, builds, profiles = [], [], []
    for p in paths:
        if os.path.isdir(p):
            jobs += glob.glob(os.path.join(p, "**", "results-*.json"), recursive=True)
            builds += glob.glob(os.path.join(p, "**", "build-*.json"), recursive=True)
            profiles += glob.glob(os.path.join(p, "**", "profile-*.json"), recursive=True)
        else:
            jobs.append(p)
    return _unique_content(jobs), sorted(set(builds)), sorted(set(profiles))


def _unique_content(paths):
    """One path per distinct file content: a run downloaded twice (a job folder and a copy of it)
    must count each job once."""
    seen = {}
    for p in sorted(set(paths), key=lambda x: (len(x), x)):
        with open(p, "rb") as f:
            seen.setdefault(hashlib.sha256(f.read()).hexdigest(), p)
    return sorted(seen.values())


def rel(path, base):
    return os.path.relpath(os.path.abspath(path), base).replace("\\", "/")


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def pool_block(label, docs, row_names, pair_names):
    """One CPU model (or all runners): every row and pair pooled over the given job documents."""
    block = {"cpu_model": label, "jobs": len(docs), "runs": sorted({d["run"]["id"] for d in docs}), "rows": []}
    for name in row_names:
        rs = [next(r for r in d["rows"] if r["row"] == name) for d in docs if any(r["row"] == name for r in d["rows"])]
        if not rs:
            continue
        out = {"row": name, "jobs": len(rs), "iters": sorted({r["iters"] for r in rs}), "pairs": {},
               "sha256_agree": len({json.dumps(r["sha256"], sort_keys=True) for r in rs}) == 1}
        exact = rounded = True
        for p in pair_names:
            prs = [r["pairs"][p] for r in rs if p in r["pairs"]]
            if len(prs) != len(rs):
                continue
            exact &= all(x["checksum_exact_match"] for x in prs)
            rounded &= all(x["checksum_rounded_match"] for x in prs)
            out["pairs"][p] = {m: pool.pair_stat(label, f"rw|{name}|{p}|{m}", [(x[ka], x[kb]) for x in prs])
                               for m, (ka, kb) in METRICS.items()}
        ck = set()
        for r in rs:
            for x in r["pairs"].values():
                ck |= set(x["a_checksums"]) | set(x["b_checksums"])
        out["checksums_exact_match"] = exact and len(ck) == 1
        out["checksums_rounded_match"] = rounded
        P = out["pairs"]
        if "fast" in P and "aligned" in P and "aa" in P:
            if out["checksums_exact_match"] or out["checksums_rounded_match"]:
                out["reading"] = common.verdict_row(P["fast"]["time"], P["aligned"]["time"],
                                                    P["aa"]["time"]["half_width_pct"], len(rs), MINIMUM_JOBS)
            else:
                out["reading"] = {"reading": "failed", "jobs": len(rs), "at_most_pct": None,
                                  "text": "outputs differ between builds: no ratio is read"}
            if not out["checksums_exact_match"] and out["checksums_rounded_match"]:
                out["reading"]["text"] += " (outputs differ in the last digits; rounded checksums match)"
        block["rows"].append(out)
    return block


def context(builds, profiles):
    """Instruction ratio, profile shares, traps and remark checks per row, from each run's build and profile files."""
    ctx = {"builds": {}, "profiles": {}}
    for b in builds:  # a program may be built in more than one job (LightGBM: the aligned pair apart)
        with open(b, encoding="utf-8") as f:
            d = json.load(f)
        for name, info in d["programs"].items():
            if name not in ctx["builds"]:
                ctx["builds"][name] = [{"files": [], "sha256": {}, "traps": {}, "text_sha256": {}, "text_identical": {}}]
            e = ctx["builds"][name][0]
            e["files"].append(os.path.basename(b))
            e["sha256"].update({k: v["sha256"] for k, v in info["builds"].items()})
            e["traps"].update({k: v["traps"] for k, v in info["builds"].items()})
            e["text_sha256"].update({k: v["text_sha256"] for k, v in info["builds"].items()})
            if "lost_locations" in info:
                e["lost_locations"] = len(info["lost_locations"])
                e["lost_here_too"] = sum(1 for x in info["lost_locations"] if x["lost_here_too"])
    for e in (v[0] for v in ctx["builds"].values()):
        t = e["text_sha256"]
        e["text_identical"] = {f"{m}_vs_{m}_g": t[m] == t[m + "_g"] for m in ("none", "fast") if m in t and m + "_g" in t}
    for p in profiles:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        for name, r in d["rows"].items():
            ctx["profiles"].setdefault(name, []).append({
                "file": os.path.basename(p),
                "instructions": r["instructions"],
                "none_ns_per_iteration_probe": r["smoke"]["none"]["ns_per_iteration"],
                "checksums_exact_match": r["checksums_exact_match"],
                "loop_lines_share": {k: r["profile"][k]["loop_lines_share"] for k in ("none", "fast")},
                "functions_share": {k: r["profile"][k]["functions_share"] for k in ("none", "fast")},
                "functions_matched": r["profile"]["none"]["functions_matched"],
                "functions_listed": r["profile"]["none"]["functions_listed"]})
    return ctx


def pool_all(entries, base_dir, builds=(), profiles=()):
    """entries: [(path, job doc)] sorted by relative path -> the pooled document."""
    row_names, pair_names = [], []
    for _, d in entries:
        for r in d["rows"]:
            if r["row"] not in row_names:
                row_names.append(r["row"])
            for p in r["pairs"]:
                if p not in pair_names:
                    pair_names.append(p)
    models = sorted({d["run"]["runner"]["cpu_model"] or "unknown" for _, d in entries})
    cpus = []
    for m in models:
        docs = [d for _, d in entries if (d["run"]["runner"]["cpu_model"] or "unknown") == m]
        cpus.append(pool_block(m, docs, row_names, pair_names))
    return {"kind": "realworld-pooled", "schema": 1,
            "method": "harness/pool.py pair_stat (two-level bootstrap, 2000 resamples), per CPU model; "
                      "readings by realworld/common.verdict_row (realworld/PLAN.md, Rules for the claims)",
            "minimum_jobs": MINIMUM_JOBS,
            "inputs": [{"path": p, "sha256": file_sha(os.path.join(base_dir, p)), "run_id": d["run"]["id"],
                        "job": d["run"].get("job"), "cpu_model": d["run"]["runner"]["cpu_model"]} for p, d in entries],
            "runs": sorted({d["run"]["id"] for _, d in entries}),
            "cpus": cpus,
            "all_runners": pool_block(ALL, [d for _, d in entries], row_names, pair_names),
            "context": context([os.path.join(base_dir, b) for b in builds],
                               [os.path.join(base_dir, p) for p in profiles]),
            "context_inputs": {"builds": list(builds), "profiles": list(profiles)}}


def load_entries(paths, base_dir):
    jobs, builds, profiles = find_inputs(paths)
    entries = []
    for j in sorted(jobs, key=lambda x: rel(x, base_dir)):
        with open(j, encoding="utf-8") as f:
            entries.append((rel(j, base_dir), json.load(f)))
    return entries, [rel(b, base_dir) for b in builds], [rel(p, base_dir) for p in profiles]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    out = os.path.abspath(argv[1])
    base = os.path.dirname(out)
    entries, builds, profiles = load_entries(argv[2:], base)
    if not entries:
        print("no results-*.json found")
        return 1
    doc = pool_all(entries, base, builds, profiles)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    for b in doc["cpus"] + [doc["all_runners"]]:
        print(f"== {b['cpu_model']}: {b['jobs']} jobs, runs {', '.join(b['runs'])}")
        for r in b["rows"]:
            P = r["pairs"]
            s = lambda k: (f"{P[k]['time']['ratio']:.4f} [{P[k]['time']['ci95'][0]:.4f}, {P[k]['time']['ci95'][1]:.4f}]"  # noqa: E731
                           if k in P else "-")
            print(f"  {r['row']:20s} fast {s('fast')}  aligned {s('aligned')}  A/A hw "
                  f"{P['aa']['time']['half_width_pct'] if 'aa' in P else float('nan'):.3f}%  layout {s('layout')}  "
                  f"-> {r.get('reading', {}).get('text')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
