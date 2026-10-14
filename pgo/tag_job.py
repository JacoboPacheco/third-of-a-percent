#!/usr/bin/env python3
"""Marks a realworld/measure.py job file as a PGO job (pgo/PLAN.md) and records the binaries it timed.

Usage: python3 pgo/tag_job.py <results-job.json> --bin <pgo bin dir> [--bins-run <build run id>]

pgo/pool_pgo.py refuses job files without this mark, so a non-PGO job can never be pooled into the
PGO column (and the other way round: realworld/pool_rw.py output never contains this mark).
"""
import argparse
import hashlib
import json
import os
import sys

COLUMN = "pgo-v1"
NAMES = ("none", "fast", "none_a64", "fast_a64")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tag(doc, bindir, bins_run=None):
    progs = sorted({r["program"] for r in doc["rows"]})
    doc["pgo"] = {"column": COLUMN, "bins_run": bins_run or None,
                  "binary_sha256": {f"{p}.{n}": sha256(os.path.join(bindir, f"{p}.{n}"))
                                    for p in progs for n in NAMES if os.path.exists(os.path.join(bindir, f"{p}.{n}"))}}
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--bin", required=True)
    ap.add_argument("--bins-run", default=None)
    a = ap.parse_args(argv)
    with open(a.job, encoding="utf-8") as f:
        doc = json.load(f)
    tag(doc, a.bin, a.bins_run)
    with open(a.job, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print(f"tagged {a.job}: {len(doc['pgo']['binary_sha256'])} binaries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
