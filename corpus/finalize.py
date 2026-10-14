#!/usr/bin/env python3
"""The determinism control, and the final results folder.

    python3 corpus/finalize.py --a DIR_A --b DIR_B --out results/corpus-run-<id>

DIR_A and DIR_B are two complete census outputs (corpus/census.py analyze) from two separate
runners of the same workflow run. The census is deterministic when census.json, lost_loops.json,
objects.sha256 (the sha256 of every object file, optimization record and stderr file) and
remarks.tar.gz are byte-identical between them. The result goes into corpus.json as
controls.determinism; the other files are copied from DIR_A. Exit code 1 if anything differs or
the schema check fails.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import schema  # noqa: E402

COMPARED = ["census.json", "lost_loops.json", "objects.sha256", "remarks.tar.gz"]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def determinism(a, b):
    files = []
    for name in COMPARED:
        pa, pb = os.path.join(a, name), os.path.join(b, name)
        ha = sha(pa) if os.path.exists(pa) else None
        hb = sha(pb) if os.path.exists(pb) else None
        files.append({"file": name, "sha256_a": ha, "sha256_b": hb, "identical": ha is not None and ha == hb})
    n_objects = 0
    differing = []
    pa, pb = os.path.join(a, "objects.sha256"), os.path.join(b, "objects.sha256")
    if os.path.exists(pa) and os.path.exists(pb):
        la = {k: h for h, k in (x.split("  ", 1) for x in open(pa).read().splitlines() if x)}
        lb = {k: h for h, k in (x.split("  ", 1) for x in open(pb).read().splitlines() if x)}
        n_objects = len(la)
        differing = sorted(k for k in set(la) | set(lb) if la.get(k) != lb.get(k))
    return {"rule": "two complete census runs on two separate runners give byte-identical outputs",
            "pass": all(f["identical"] for f in files) and not differing,
            "files": files, "build_files_compared": n_objects, "build_files_differing": differing[:50]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    det = determinism(a.a, a.b)
    with open(os.path.join(a.a, "census.json"), encoding="utf-8") as f:
        census = json.load(f)
    census.setdefault("schema", "corpus-1")
    census["controls"]["determinism"] = det
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "corpus.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(census, f, indent=1)
        f.write("\n")
    for name in ("lost_loops.json", "objects.sha256", "remarks.tar.gz"):
        shutil.copyfile(os.path.join(a.a, name), os.path.join(a.out, name))
    problems = schema.check_dir(a.out)
    for p in problems:
        print("schema:", p)
    print("determinism:", "PASS" if det["pass"] else "FAIL", [f["file"] for f in det["files"] if not f["identical"]],
          det["build_files_differing"][:5])
    return 0 if det["pass"] and not problems else 1


if __name__ == "__main__":
    sys.exit(main())
