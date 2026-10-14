"""The page-level verdict across CPU models: one line from every results.json of one workflow run.

Stage S3 runs the measurement as a matrix of jobs, so one workflow run draws several runners and
often several CPU models. Each job's results.json carries the verdict for its own CPU model
(harness/verdict.py, criteria-v2). This module reads them all and applies criteria-v2.json
"v2.page_level":
- a file is usable when its byte-identical A/A half-width is at most 2 %; a CPU model with no
  usable file is listed as excluded and does not vote;
- a CPU model's form is the form of its usable files when they agree, inconclusive when they do not;
- the page form is map only if every usable CPU model is map (holds_everywhere likewise);
  otherwise inconclusive, and the line says which CPU model differs and why.
N pools the lost kernels' in-cache aligned ratios of the usable map files; X is their largest X.

Usage: python harness/combine.py <dir>   reads <dir>/*/results.json, writes <dir>/combined.json.
scripts/check.py recomputes every combined.json and demands the same answer.
"""
import glob
import hashlib
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import verdict  # noqa: E402

V2_FILE = "harness/criteria-v2.json"


def slug(cpu_model):
    """A file-name-safe name for a CPU model: 'AMD EPYC 7763 64-Core Processor' -> 'amd-epyc-7763-64-core-processor'."""
    s = re.sub(r"\((r|tm|c)\)", "", (cpu_model or "unknown-cpu").lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "unknown-cpu"


def combine(entries, criteria, criteria_sha256):
    """entries: [(path relative to the combined file, results document)]. Returns the combined document."""
    crit = criteria["verdict"]
    max_hw = crit["aa_half_width_max_pct"]
    files = []
    for path, doc in sorted(entries, key=lambda e: e[0]):
        v = doc["verdict"]
        hw = doc["controls"]["aa"]["half_width_pct"]
        files.append({"path": path, "cpu_model": doc["run"]["runner"]["cpu_model"], "run_id": doc["run"]["id"],
                      "aa_half_width_pct": hw, "usable": hw <= max_hw, "form": v["form"], "line": v["line"],
                      "why": v["why"], "x_pct": v.get("x_pct"),
                      "placement_sensitive": [p["cell_id"] for p in v.get("placement_sensitive", [])]})
    docs = {path: doc for path, doc in entries}

    models = sorted({f["cpu_model"] or "unknown" for f in files})
    cpus = []
    for m in models:
        mine = [f for f in files if (f["cpu_model"] or "unknown") == m]
        usable = [f for f in mine if f["usable"]]
        forms = sorted({f["form"] for f in usable})
        if not usable:
            form, why = None, ("excluded: A/A half-width above %g%% (%s)"
                               % (max_hw, ", ".join(f"{f['aa_half_width_pct']:.2f}%" for f in mine)))
        elif len(forms) == 1:
            form, why = forms[0], usable[0]["why"]
        else:
            form, why = "inconclusive", f"its {len(usable)} usable runs disagree ({', '.join(forms)})"
        cpus.append({"cpu_model": m, "files": [f["path"] for f in mine], "usable": bool(usable), "form": form,
                     "why": why})

    voting = [c for c in cpus if c["usable"]]
    excluded = [c for c in cpus if not c["usable"]]
    exc_text = ""
    if excluded:
        exc_text = (f" Not counted (A/A half-width above {max_hw:g}%): "
                    + "; ".join(c["cpu_model"] + " (" + ", ".join(f"{f['aa_half_width_pct']:.2f}%" for f in files
                                                                  if (f["cpu_model"] or "unknown") == c["cpu_model"])
                                + ")" for c in excluded) + ".")
    ps = [(p, f["cpu_model"]) for f in files if f["usable"] for p in f["placement_sensitive"]]
    ps_text = ""
    if ps:
        ps_text = (" " + verdict.PS_LEAD
                   + "; ".join(f"{p} on {m}" for p, m in ps) + ".")
    names = "; ".join(c["cpu_model"] for c in voting)

    def out(form, line, why, n=None, x=None):
        return {"form": form, "line": line, "why": why, "n": n, "x_pct": x}

    if not voting:
        v = out("inconclusive",
                "INCONCLUSIVE: no CPU model drawn had a usable A/A control, so no headline number is printed." + exc_text,
                "page level: no usable CPU model")
    elif all(c["form"] == "map" for c in voting):
        rs, lost_all = [], set()
        for f in files:
            if f["usable"] and f["form"] == "map":
                d = docs[f["path"]]
                lost = verdict.classes(d["cells"])["lost"]
                lost_all |= set(lost)
                rs += [c["aligned"]["ratio"] for c in d["cells"] if c["kernel"] in lost and c["size_class"] in verdict.IN_CACHE]
        n = {"median": statistics.median(rs), "min": min(rs), "max": max(rs)}
        x = max(f["x_pct"] for f in files if f["usable"] and f["form"] == "map")
        v = out("map",
                f"On every CPU model drawn with a usable A/A control ({names}), "
                + verdict.map_line(sorted(lost_all), n, x, aligned=True) + ps_text + exc_text,
                "page level: every usable CPU model is map", n, x)
    elif all(c["form"] == "holds_everywhere" for c in voting):
        x = max(f["x_pct"] for f in files if f["usable"])
        v = out("holds_everywhere",
                f"On every CPU model drawn with a usable A/A control ({names}), no loop shape we tried paid more "
                f"than {x:.1f}%." + ps_text + exc_text,
                "page level: every usable CPU model is holds_everywhere", x=x)
    else:
        parts = "; ".join(f"{c['form']} on {c['cpu_model']}"
                          + (f" ({c['why']})" if c["form"] != "map" else "") for c in voting)
        v = out("inconclusive",
                f"INCONCLUSIVE across CPU models: {parts}; so no single headline number is printed." + exc_text,
                "page level: the usable CPU models differ")
    return {"kind": "combined", "criteria_file": V2_FILE, "criteria_sha256": criteria_sha256,
            "files": files, "cpus": cpus, "verdict": v}


def load_dir(d):
    entries = []
    for p in sorted(glob.glob(os.path.join(d, "*", "results.json"))):
        with open(p, encoding="utf-8") as f:
            entries.append((os.path.relpath(p, d).replace("\\", "/"), json.load(f)))
    return entries


def criteria_and_sha():
    path = os.path.join(REPO, V2_FILE)
    with open(path, "rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    d = argv[1]
    entries = load_dir(d)
    if not entries:
        print(f"no */results.json under {d}")
        return 1
    crit, sha = criteria_and_sha()
    doc = combine(entries, crit, sha)
    with open(os.path.join(d, "combined.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    for c in doc["cpus"]:
        print(f"[cpu] {c['cpu_model']}: {c['form']}  ({len(c['files'])} file(s)) {c['why']}")
    print(f"[page] {doc['verdict']['form']}: {doc['verdict']['line']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
