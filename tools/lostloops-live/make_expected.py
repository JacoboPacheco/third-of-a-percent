#!/usr/bin/env python3
"""Writes tools/lostloops-live/expected/<project>.json from the census results stored in results/.

    python tools/lostloops-live/make_expected.py

Nothing else feeds the expected files (PLAN.md): the census's lost_loops.json (lost, moved,
gained, index evidence) and corpus.json (the project's row: units, vectorized counts, ud2, text bytes).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SOURCES = {
    "leveldb": ("projects.json", "results/corpus-run-38259934735"),
    "spectra": ("projects2.json", "results/corpus2-baseline-run-38273183229"),
    "lightgbm": ("projects2.json", "results/corpus2-baseline-run-38273183229"),
}
ENTRY = ("tu", "function", "file", "line", "column", "origin", "count")
EXTRA = ("class", "detail", "source_line")


def entry(e, kind):
    out = {k: e[k] for k in ENTRY}
    if kind != "gained":
        out.update({k: e[k] for k in EXTRA})
        out["hardened_remarks"] = e["fast_remarks"]
    ev = e.get("index_evidence")
    if kind == "lost" and ev:
        out["check"] = {"status": ev["status"], "messages": ev["messages"], "attributed": ev["attributed_traps"]}
    return out


def main():
    os.makedirs(os.path.join(HERE, "expected"), exist_ok=True)
    for name, (plist, run) in SOURCES.items():
        d = os.path.join(REPO, run)
        lost = json.load(open(os.path.join(d, "lost_loops.json"), encoding="utf-8"))
        corpus = json.load(open(os.path.join(d, "corpus.json"), encoding="utf-8"))
        row = next(p for p in corpus["projects"] if p["name"] == name)
        pin = next(p for p in json.load(open(os.path.join(REPO, "corpus", plist), encoding="utf-8"))["projects"]
                   if p["name"] == name)
        out = {
            "project": name, "projects_file": plist, "census_run": run, "commit": pin["commit"],
            "translation_units": row["translation_units"], "compiled": row["compiled"],
            "vectorized_none": row["none"]["vectorized"], "vectorized_hardened": row["fast"]["vectorized"],
            "traps_added": row["ud2_added"],
            "text_bytes_none": row["none"]["text_bytes"], "text_bytes_hardened": row["fast"]["text_bytes"],
        }
        for kind in ("lost", "moved", "gained"):
            es = [entry(e, kind) for e in lost[kind] if e["project"] == name]
            out[kind] = sorted(es, key=lambda e: (e["tu"], e["function"], e["file"], e["line"], e["column"]))
        assert not row["failed"], name
        assert sum(e["count"] for e in out["lost"]) == row["lost"], name
        with open(os.path.join(HERE, "expected", name + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=0, sort_keys=False)
            f.write("\n")
        print(name, out["commit"][:10], "lost", row["lost"], "moved", row["moved"], "gained", row["gained"],
              "TUs", row["translation_units"])


if __name__ == "__main__":
    main()
