#!/usr/bin/env python3
"""Pools the PGO jobs per CPU model (pgo/PLAN.md), with realworld/pool_rw.py's logic imported unchanged.

Usage: python pgo/pool_pgo.py <out.json> <dir or results-job json> [...]
  a dir means every results-*.json under it (each must carry the "pgo" mark of pgo/tag_job.py) and
  every pgo-build-*.json found there (per program and mode: hashes, traps, profile warnings, census
  lost locations still vectorized, training checksums).
"""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "realworld"))
sys.path.insert(0, os.path.join(REPO, "harness"))
import pool_rw  # noqa: E402  (realworld/pool_rw.py, not edited)


def find_builds(paths):
    found = []
    for p in paths:
        if os.path.isdir(p):
            found += glob.glob(os.path.join(p, "**", "pgo-build-*.json"), recursive=True)
    seen = {}
    for p in sorted(set(found), key=lambda x: (len(x), x)):
        with open(p, "rb") as f:
            seen.setdefault(hashlib.sha256(f.read()).hexdigest(), p)
    return sorted(seen.values())


def build_context(build_files, base):
    """{program: {mode: summary}} from the pgo-build files; two different builds of one program and mode
    are an error (every timing run must time the same bytes)."""
    ctx = {}
    for rel in build_files:
        with open(os.path.join(base, rel), encoding="utf-8") as f:
            d = json.load(f)
        for prog, info in d["programs"].items():
            cur = ctx.setdefault(prog, {})
            entry = {"file": os.path.basename(rel),
                     "sha256": {k: v["sha256"] for k, v in info["builds"].items()},
                     "text_sha256": {k: v["text_sha256"] for k, v in info["builds"].items()},
                     "traps": {k: v["traps"] for k, v in info["builds"].items()},
                     "instrumented_sha256": info["instrumented"]["sha256"],
                     "profile": {k: info["profile"][k] for k in ("functions", "bytes", "sha256")},
                     "profile_warnings": info["profile_warnings"],
                     "census_lost_locations": info["census_lost_locations"],
                     "training_checksums": {r["row"]: r["checksum"] for r in info["training"]["rows"]}}
            if d["mode"] in cur and cur[d["mode"]]["sha256"] != entry["sha256"]:
                raise SystemExit(f"{prog} {d['mode']}: two different PGO builds in the inputs")
            cur[d["mode"]] = entry
    return ctx


def pool_doc(entries, base, build_files):
    doc = pool_rw.pool_all(entries, base, (), ())
    doc["kind"] = "pgo-pooled"
    doc["method"] = ("realworld/pool_rw.py pool_all (harness/pool.py pair_stat, two-level bootstrap, 2000 resamples), "
                     "per CPU model; PGO FAST/NONE, each mode built and profiled separately (pgo/PLAN.md)")
    doc.pop("context", None)
    doc.pop("context_inputs", None)
    doc["pgo_context"] = build_context(build_files, base)
    doc["pgo_context_inputs"] = list(build_files)
    doc["pgo_binaries"] = sorted({json.dumps(d["pgo"]["binary_sha256"], sort_keys=True) for _, d in entries})
    return doc


def load(paths, base):
    entries, _, _ = pool_rw.load_entries(paths, base)
    for rel, d in entries:
        if "pgo" not in d:
            raise SystemExit(f"{rel} carries no PGO mark (pgo/tag_job.py): refusing to pool it as PGO")
    builds = [pool_rw.rel(b, base) for b in find_builds(paths)]
    return entries, builds


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    out = os.path.abspath(argv[1])
    base = os.path.dirname(out)
    entries, builds = load(argv[2:], base)
    if not entries:
        print("no results-*.json found")
        return 1
    doc = pool_doc(entries, base, builds)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    for b in doc["cpus"] + [doc["all_runners"]]:
        print(f"== {b['cpu_model']}: {b['jobs']} jobs, runs {', '.join(b['runs'])}")
        for r in b["rows"]:
            P = r["pairs"]
            s = lambda k: (f"{P[k]['time']['ratio']:.4f} [{P[k]['time']['ci95'][0]:.4f}, {P[k]['time']['ci95'][1]:.4f}]"  # noqa: E731
                           if k in P else "-")
            hw = P["aa"]["time"]["half_width_pct"] if "aa" in P else float("nan")
            print(f"  {r['row']:20s} PGO fast {s('fast')}  aligned {s('aligned')}  A/A hw {hw:.3f}%  "
                  f"layout {s('layout')}  -> {r.get('reading', {}).get('text')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
