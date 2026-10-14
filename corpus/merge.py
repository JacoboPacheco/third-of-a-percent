#!/usr/bin/env python3
"""Joins the shards of one census copy into one census output.

    python3 corpus/merge.py --out DIR SHARD_DIR [SHARD_DIR ...]

Each SHARD_DIR is a complete `census.py analyze` output for some of the projects (--shard K).
The result has the same files as one unsharded output: census.json (projects in the order of the
projects file, totals and patterns recomputed from the merged parts, the kernel control from the
first shard after checking that every shard computed the same one), lost_loops.json,
objects.sha256 (sorted by path; the kernels' lines, which every shard has, kept once) and
remarks.tar.gz (every member once). Exit code 1 if two shards disagree about a shared file or the
kernel control.
"""
import argparse
import json
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import census  # noqa: E402


def load(d, name):
    with open(os.path.join(d, name), encoding="utf-8") as f:
        return json.load(f)


def merge(shard_dirs, out):
    problems = []
    shard_dirs = sorted(shard_dirs)
    cs = [load(d, "census.json") for d in shard_dirs]
    ls = [load(d, "lost_loops.json") for d in shard_dirs]
    first = cs[0]
    with open(os.path.join(HERE, first["projects_file"]), encoding="utf-8") as f:
        order = {p["name"]: i for i, p in enumerate(json.load(f)["projects"])}

    def key(name):
        return (order.get(name, len(order)), name)

    summaries = sorted((s for c in cs for s in c["projects"]), key=lambda s: key(s["name"]))
    names = [s["name"] for s in summaries]
    if len(names) != len(set(names)):
        problems.append("a project appears in more than one shard")
    for c in cs[1:]:
        for k in ("target", "projects_file", "schema"):
            if c.get(k) != first.get(k):
                problems.append("shards disagree on %s" % k)
    kernels = first["controls"]["kernels"]
    same_kernels = all(c["controls"]["kernels"] == kernels for c in cs)
    if not same_kernels:
        problems.append("shards computed different kernel controls")
        kernels = dict(kernels, **{"pass": False, "shards_disagree": True})
    crosscheck = {}
    for c in cs:
        crosscheck.update(c["controls"]["remark_crosscheck"]["per_project"])

    def by_project(lists):
        return sorted(lists, key=lambda e: key(e["project"]))  # stable: keeps each shard's order

    lost = by_project([e for l in ls for e in l["lost"]])
    moved = by_project([e for l in ls for e in l["moved"]])
    gained = by_project([e for l in ls for e in l["gained"]])
    included = [s for s in summaries if census.is_included(s)]
    inc_names = {s["name"] for s in included}
    lost_inc = [e for e in lost if e["project"] in inc_names]

    merged = dict(first)
    merged["shards"] = sorted(x for c in cs for x in c.get("shards", []))
    merged["projects"] = summaries
    merged["dropped"] = sorted((d for c in cs for d in c["dropped"]), key=lambda d: key(d["name"]))
    merged["totals"] = census.make_totals(included, lost_inc)
    merged["patterns"] = census.patterns(lost_inc)
    merged["controls"] = {
        "kernels": kernels,
        "remark_crosscheck": {"rule": first["controls"]["remark_crosscheck"]["rule"],
                              "pass": all(v[m][0] == v[m][1] for v in crosscheck.values() for m in v),
                              "per_project": {k: crosscheck[k] for k in sorted(crosscheck, key=key)}},
    }
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "census.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, indent=1)
        f.write("\n")
    with open(os.path.join(out, "lost_loops.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(ls[0], lost=lost, moved=moved, gained=gained), f, indent=1)
        f.write("\n")

    hashes = {}
    for d in shard_dirs:
        with open(os.path.join(d, "objects.sha256"), encoding="utf-8") as f:
            for ln in f.read().splitlines():
                if not ln:
                    continue
                h, path = ln.split("  ", 1)
                if hashes.setdefault(path, h) != h:
                    problems.append("shards disagree on %s" % path)
    with open(os.path.join(out, "objects.sha256"), "w", encoding="utf-8", newline="\n") as f:
        for path in sorted(hashes):
            f.write("%s  %s\n" % (hashes[path], path))

    members = {}
    for d in shard_dirs:
        with tarfile.open(os.path.join(d, "remarks.tar.gz"), "r:gz") as t:
            for m in t.getmembers():
                data = t.extractfile(m).read()
                if members.setdefault(m.name, data) != data:
                    problems.append("shards disagree on remarks member %s" % m.name)
    census.deterministic_targz_bytes(os.path.join(out, "remarks.tar.gz"), list(members.items()))
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("shards", nargs="+")
    a = ap.parse_args(argv)
    problems = merge(a.shards, a.out)
    for p in problems[:20]:
        print("merge:", p)
    print("merged %d shards into %s: %s" % (len(a.shards), a.out, "OK" if not problems else "PROBLEMS"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
