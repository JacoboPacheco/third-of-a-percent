#!/usr/bin/env python3
"""Census 1 and census 2 in one table, by project category (corpus/README.md).

    python corpus/combine.py --c1 results/corpus-run-<id> --c2 results/corpus2-baseline-run-<id>
                             [--c2-avx2 results/corpus2-avx2-run-<id>] [--c1-avx2 results/corpus1-avx2-run-<id>]
                             [--json OUT.json]

Prints markdown: one row per category (census 1's categories are given below, census 2's come from
projects2.json), a total per census and a combined total, at the baseline target; then the same
totals for the avx2 runs when given. Only included (compiled) projects count, as in corpus.json.
Every number is a sum of per-project numbers in the corpus.json files; nothing is estimated.
"""
import argparse
import json
import os
import sys

# Census 1 projects.json has no category field; these are the categories its README used.
CENSUS1_CATEGORIES = {
    "nlohmann_json": "parsers", "rapidjson": "parsers", "simdjson": "parsers", "jsoncpp": "parsers",
    "yaml-cpp": "parsers", "pugixml": "parsers", "tinyxml2": "parsers", "tinyobjloader": "parsers",
    "muparser": "parsers", "cli11": "parsers",
    "fmt": "formatting and logging", "spdlog": "formatting and logging",
    "double-conversion": "numeric", "eigen": "numeric",
    "clipper2": "geometry", "lodepng": "image codec",
    "snappy": "compression and storage", "leveldb": "compression and storage",
    "ninja": "build tool",
}


def load(d):
    with open(os.path.join(d, "corpus.json"), encoding="utf-8") as f:
        c = json.load(f)
    with open(os.path.join(d, "lost_loops.json"), encoding="utf-8") as f:
        lost = json.load(f)["lost"]
    c["_lost_unique"] = {}
    for e in lost:
        c["_lost_unique"].setdefault(e["project"], set()).add((e["file"], e["line"], e["column"]))
    return c


def rows_of(c, census_name):
    dropped = {d["name"] for d in c["dropped"]}
    out = []
    for p in c["projects"]:
        if p["name"] in dropped:
            continue
        cat = p.get("category") or CENSUS1_CATEGORIES.get(p["name"], "other")
        out.append({"census": census_name, "category": cat, "project": p["name"],
                    "vectorized": p["none"]["vectorized"], "lost": p["lost"],
                    "vectorized_unique": p["none"]["vectorized_unique"],
                    "lost_unique": len(c["_lost_unique"].get(p["name"], ())),
                    "lost_project_code": p["lost_by_origin"].get("project", 0) + p["lost_by_origin"].get("driver", 0),
                    "vectorized_project_code": p["none"]["vectorized_by_origin"].get("project", 0)
                    + p["none"]["vectorized_by_origin"].get("driver", 0),
                    "ud2_added": p["ud2_added"], "text_none": p["none"]["text_bytes"],
                    "text_fast": p["fast"]["text_bytes"]})
    return out


def agg(rows, label):
    v = sum(r["vectorized"] for r in rows)
    lost = sum(r["lost"] for r in rows)
    vp = sum(r["vectorized_project_code"] for r in rows)
    tn, tf = sum(r["text_none"] for r in rows), sum(r["text_fast"] for r in rows)
    return {"label": label, "projects": len(rows), "projects_with_lost": sum(1 for r in rows if r["lost"]),
            "vectorized": v, "vectorized_project_code": vp, "lost": lost,
            "vectorized_unique": sum(r["vectorized_unique"] for r in rows),
            "lost_unique": sum(r["lost_unique"] for r in rows),
            "lost_pct": round(100.0 * lost / v, 2) if v else None,
            "lost_pct_of_project_code": round(100.0 * sum(r["lost_project_code"] for r in rows) / vp, 2) if vp else None,
            "ud2_added": sum(r["ud2_added"] for r in rows),
            "text_change_pct": round(100.0 * (tf - tn) / tn, 2) if tn else None}


def fmt_row(a):
    pct = "n/a" if a["lost_pct"] is None else "%.2f%%" % a["lost_pct"]
    return "| %s | %d | %s | %s | %s | %d | %s | %d | %d | %s |" % (
        a["label"], a["projects"], format(a["vectorized"], ","), format(a["vectorized_unique"], ","),
        format(a["vectorized_project_code"], ","), a["lost"], pct, a["lost_unique"], a["projects_with_lost"],
        "n/a" if a["text_change_pct"] is None else "%+.2f%%" % a["text_change_pct"])


HEADER = ("| category | projects | vectorized loops (NONE) | distinct source locations | of which in project code "
          "| lost under FAST | lost % | lost, distinct locations | projects with a lost loop | .text change |\n"
          "|---|---|---|---|---|---|---|---|---|---|")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--c1", required=True)
    ap.add_argument("--c2", required=True)
    ap.add_argument("--c1-avx2")
    ap.add_argument("--c2-avx2")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    r1, r2 = rows_of(load(a.c1), "census 1"), rows_of(load(a.c2), "census 2")
    lines = ["**Baseline (x86-64, SSE2), FAST vs NONE**", "", HEADER]
    table = []
    for name, rows in (("census 1", r1), ("census 2", r2)):
        for cat in sorted({r["category"] for r in rows}):
            x = agg([r for r in rows if r["category"] == cat], "%s: %s" % (name, cat))
            table.append(x)
            lines.append(fmt_row(x))
        x = agg(rows, "**%s total**" % name)
        table.append(x)
        lines.append(fmt_row(x))
    x = agg(r1 + r2, "**combined**")
    table.append(x)
    lines.append(fmt_row(x))
    avx = []
    if a.c1_avx2 or a.c2_avx2:
        lines += ["", "**avx2 sensitivity (-march=x86-64-v3), FAST vs NONE**", "", HEADER]
        for name, d in (("census 1", a.c1_avx2), ("census 2", a.c2_avx2)):
            if d:
                x = agg(rows_of(load(d), name), "**%s total (avx2)**" % name)
                avx.append(x)
                lines.append(fmt_row(x))
    print("\n".join(lines))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"inputs": {k: v for k, v in vars(a).items() if k != "json"},
                       "baseline": table, "avx2": avx,
                       "note": "sums of per-project numbers from the corpus.json files; included projects only"},
                      f, indent=1)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
