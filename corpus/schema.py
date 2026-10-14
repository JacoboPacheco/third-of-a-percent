#!/usr/bin/env python3
"""Schema and consistency check of a census results folder (no compiler needed).

    python corpus/schema.py results/corpus-run-<id> [more folders]

Checks corpus.json and lost_loops.json: required fields and types; every download pinned with a
64-hex sha256; each project's lost count equals its entries in lost_loops.json; the totals equal
the sum over included projects; every percentage and ud2_added recomputed from its parts; every
lost loop carries a class from classify.CLASSES and its source line; the controls (kernels,
remark cross-check, determinism) are present with a boolean pass. Exit code 1 on any problem.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import classify  # noqa: E402

HEX64 = re.compile(r"^[0-9a-f]{64}$")
MODE_FIELDS = ("vectorized", "vectorized_unique", "loops_reported", "ud2", "text_bytes")
LOST_FIELDS = {"project": str, "tu": str, "function": str, "function_name": str, "file": str, "line": int,
               "column": int, "origin": str, "count": int, "none_remark": str, "fast_remarks": list,
               "class": str, "detail": str, "source_line": str, "context": list}


def pct(a, b):
    return round(100.0 * a / b, 3) if b else None


def check_corpus(c, lost_doc=None, require_determinism=True):
    problems = []

    def need(obj, key, typ, where):
        if key not in obj:
            problems.append("%s: missing %s" % (where, key))
            return False
        if not isinstance(obj[key], typ) or (typ is int and isinstance(obj[key], bool)):
            problems.append("%s: %s is %s, expected %s" % (where, key, type(obj[key]).__name__, typ))
            return False
        return True

    for key, typ in (("schema", str), ("toolchain", dict), ("projects", list), ("dropped", list),
                     ("totals", dict), ("patterns", list), ("controls", dict), ("limits", list)):
        need(c, key, typ, "corpus")
    if problems:
        return problems
    if c["schema"] not in ("corpus-1", "corpus-2"):
        problems.append("corpus: schema is %r" % c["schema"])
    v2 = c["schema"] == "corpus-2"
    if v2 and c.get("target") not in ("baseline", "avx2"):
        problems.append("corpus: target is %r" % c.get("target"))
    names = set()
    for p in c["projects"]:
        w = "project %s" % p.get("name")
        for key, typ in (("name", str), ("kind", str), ("version", str), ("commit", str), ("downloads", list),
                         ("translation_units", int), ("compiled", int), ("failed", list), ("none", dict),
                         ("fast", dict), ("lost", int), ("moved", int), ("gained", int), ("ud2_added", int),
                         ("lost_by_class", dict), ("lost_by_origin", dict)):
            need(p, key, typ, w)
        names.add(p.get("name"))
        for d in p.get("downloads", []):
            if not HEX64.match(str(d.get("sha256", ""))) or not isinstance(d.get("bytes"), int) \
                    or not str(d.get("url", "")).startswith("https://"):
                problems.append("%s: download not pinned: %r" % (w, d))
        for m in ("none", "fast"):
            for f in MODE_FIELDS:
                if not isinstance(p.get(m, {}).get(f), int):
                    problems.append("%s: %s.%s missing" % (w, m, f))
        if problems:
            continue
        if p["ud2_added"] != p["fast"]["ud2"] - p["none"]["ud2"]:
            problems.append("%s: ud2_added does not match" % w)
        if p.get("lost_pct_of_vectorized") != pct(p["lost"], p["none"]["vectorized"]):
            problems.append("%s: lost_pct_of_vectorized does not match" % w)
        if sum(p["lost_by_class"].values()) != p["lost"]:
            problems.append("%s: lost_by_class does not add up" % w)
        if p["lost"] > p["none"]["vectorized"]:
            problems.append("%s: more lost loops than vectorized ones" % w)
    if problems:
        return problems

    dropped = {d["name"] for d in c["dropped"]}
    inc = [p for p in c["projects"] if p["name"] not in dropped]
    t = c["totals"]
    if t.get("projects") != len(inc):
        problems.append("totals: projects %r != %d" % (t.get("projects"), len(inc)))
    for m in ("none", "fast"):
        for f in MODE_FIELDS:
            if t.get(m, {}).get(f) != sum(p[m][f] for p in inc):
                problems.append("totals: %s.%s is not the sum over projects" % (m, f))
    for f in ("lost", "moved", "gained", "ud2_added"):
        if t.get(f) != sum(p[f] for p in inc):
            problems.append("totals: %s is not the sum over projects" % f)
    if t.get("lost_pct_of_vectorized") != pct(t.get("lost", 0), t.get("none", {}).get("vectorized", 0)):
        problems.append("totals: lost_pct_of_vectorized does not match")
    tb = t.get("none", {}).get("text_bytes", 0)
    if t.get("text_bytes_change_pct") != pct(t.get("fast", {}).get("text_bytes", 0) - tb, tb):
        problems.append("totals: text_bytes_change_pct does not match")
    if sum(t.get("lost_by_class", {}).values()) != t.get("lost"):
        problems.append("totals: lost_by_class does not add up")
    if v2 and t.get("lost_with_index_evidence") != sum(p.get("lost_with_index_evidence", 0) for p in inc):
        problems.append("totals: lost_with_index_evidence is not the sum over projects")
    for pat in c["patterns"]:
        if pat.get("class") not in classify.CLASSES or not isinstance(pat.get("count"), int) or not pat.get("examples"):
            problems.append("pattern malformed: %r" % pat.get("detail"))

    ctl = c["controls"]
    for name in ("kernels", "remark_crosscheck") + (("determinism",) if require_determinism else ()):
        if not isinstance(ctl.get(name), dict) or not isinstance(ctl[name].get("pass"), bool):
            problems.append("controls: %s missing or without a boolean pass" % name)
    k = ctl.get("kernels", {})
    if isinstance(k, dict) and len(k.get("kernels", [])) != 8:
        problems.append("controls.kernels: expected 8 kernels")

    if lost_doc is not None:
        for key in ("lost", "moved", "gained"):
            if not isinstance(lost_doc.get(key), list):
                problems.append("lost_loops: %s missing" % key)
        for i, e in enumerate(lost_doc.get("lost", [])):
            for f, typ in LOST_FIELDS.items():
                if not isinstance(e.get(f), typ):
                    problems.append("lost_loops[%d]: %s missing or not %s" % (i, f, typ.__name__))
                    break
            else:
                if e["class"] not in classify.CLASSES:
                    problems.append("lost_loops[%d]: class %r" % (i, e["class"]))
                if e["count"] < 1:
                    problems.append("lost_loops[%d]: count < 1" % i)
                if e["project"] not in names:
                    problems.append("lost_loops[%d]: unknown project %r" % (i, e["project"]))
                if v2 and not (isinstance(e.get("trip_count"), dict) and isinstance(e.get("index_evidence"), dict)
                               and isinstance(e["index_evidence"].get("status"), str)):
                    problems.append("lost_loops[%d]: trip_count or index_evidence missing" % i)
        for p in c["projects"]:
            n = sum(e["count"] for e in lost_doc.get("lost", []) if e.get("project") == p["name"])
            if n != p["lost"]:
                problems.append("project %s: lost %d but lost_loops.json lists %d" % (p["name"], p["lost"], n))
    return problems


def check_dir(path):
    try:
        with open(os.path.join(path, "corpus.json"), encoding="utf-8") as f:
            c = json.load(f)
        with open(os.path.join(path, "lost_loops.json"), encoding="utf-8") as f:
            lost = json.load(f)
    except (OSError, ValueError) as e:
        return ["%s: %s" % (path, e)]
    problems = check_corpus(c, lost)
    if not os.path.exists(os.path.join(path, "remarks.tar.gz")):
        problems.append("%s: remarks.tar.gz missing" % path)
    return problems


def main(argv):
    bad = 0
    for path in argv:
        problems = check_dir(path)
        for p in problems:
            print("%s: %s" % (path, p))
        print("%s: %s" % (path, "OK" if not problems else "%d problems" % len(problems)))
        bad += bool(problems)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
