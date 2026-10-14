#!/usr/bin/env python3
"""Turns the cached Compiler Explorer answers into results.json and the README matrix. Offline.

    python ce-sweep/build_results.py           # write results.json and the matrix block in README.md
    python ce-sweep/build_results.py --check   # recompute and compare, write nothing (used by check.py)
"""
import glob
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cesweep as cs  # noqa: E402

RESULTS = os.path.join(cs.HERE, "results.json")
README = os.path.join(cs.HERE, "README.md")
LINKS = os.path.join(cs.HERE, "permalinks.json")
BEGIN, END = "<!-- matrix:begin (written by build_results.py) -->", "<!-- matrix:end -->"
SHORT = {k: k.split("_", 1)[1] for k in cs.KERNELS}


def load_pairs():
    pairs = []
    for b in cs.matrix():
        p = os.path.join(cs.HERE, "cache", cs.cache_name(b))
        if os.path.exists(p):
            rec = cs.load_cache(p)
            pairs.append((b, rec))
    return pairs


def compute():
    source = cs.build_source()
    pairs = load_pairs()
    builds = []
    for b, rec in pairs:
        resp = rec["response"]
        an = cs.analyse(b, resp, source) if cs.compile_ok(resp) else {}
        checks = sum((a["asm"] or {}).get("traps", 0) + (a["asm"] or {}).get("abort_calls", 0)
                     for a in an.values() if a.get("asm"))
        builds.append(dict(b, cache=cs.cache_name(b), request_sha256=cs.request_sha(b["compiler_id"],
                           cs.request_body(source, b["flags"])), cached_request_sha256=rec["request_sha256"],
                           fetched_at=rec["fetched_at"], compiled=cs.compile_ok(resp), check_sites=checks))
    cells = cs.cells([(b, rec["response"]) for b, rec in pairs], source)
    rows = {}
    for c in cells:
        key = (c["compiler_id"], c["target"], c["opt"])
        r = rows.setdefault(key, {"compiler_id": c["compiler_id"], "family": c["family"], "version": c["version"],
                                  "target": c["target"], "opt": c["opt"], "macro_hardened": c["macro_hardened"],
                                  "vectorized_none": [], "vectorized_hardened": [], "lost": [], "unknown": [],
                                  "remark_asm_disagree": []})
        if c["lost"] is None:
            r["unknown"].append(c["kernel"])
            continue
        if c["none"]["vectorized"]:
            r["vectorized_none"].append(c["kernel"])
        if c["hardened"]["vectorized"]:
            r["vectorized_hardened"].append(c["kernel"])
        if c["lost"]:
            r["lost"].append(c["kernel"])
        for side in ("none", "hardened"):
            s = c[side]
            if s["asm"] is not None and bool(s["vectorized"]) != (s["asm"]["simd_instr"] > 0):
                r["remark_asm_disagree"].append("%s/%s" % (c["kernel"], side))
    # The hardening macro must have an effect: more check sites in the hardened build than in NONE.
    bk = {(b["compiler_id"], b["target"], b["opt"], b["mode"]): b for b in builds}
    for (cid, target, opt), r in rows.items():
        n, h = bk[(cid, target, opt, "none")], bk[(cid, target, opt, "hardened")]
        r["check_sites_none"], r["check_sites_hardened"] = n["check_sites"], h["check_sites"]
        r["macro_effective"] = h["check_sites"] > n["check_sites"]
    order = {b["compiler_id"]: i for i, b in enumerate(cs.matrix())}
    matrix = sorted(rows.values(), key=lambda r: (order[r["compiler_id"]], r["target"], r["opt"]))
    ctl = rows.get(("clang1810", "x86-64", "-O2"))
    control = {"row": "clang1810 (x86-64 clang 18.1.0), x86-64, -O2, libc++ FAST vs NONE",
               "expected_lost": cs.CONTROL_LOST, "observed_lost": ctl["lost"] if ctl else None,
               "ok": bool(ctl) and ctl["lost"] == cs.CONTROL_LOST}
    links = None
    if os.path.exists(LINKS):
        with open(LINKS, encoding="utf-8") as f:
            links = {k: {"url": v["url"], "verified": v["verified"]} for k, v in json.load(f)["links"].items()}
    return {
        "schema": "ce-sweep/1",
        "what": "Compile-only sweep on Compiler Explorer: which of the 8 kernel loops lose vectorization when the "
                "standard library's bounds checks are on. No timing.",
        "api": "https://godbolt.org/api/compiler/<compiler_id>/compile (POST); answers cached in ce-sweep/cache/",
        "source_file": "ce-sweep/source.cpp",
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "loop_lines": cs.loop_lines(source),
        "definition_lost": "vectorized in the unhardened build and not vectorized in the hardened build, read from "
                           "the compiler's own remarks at the // LOOP line (clang: -Rpass=loop-vectorize; GCC: "
                           "-fopt-info-vec-optimized)",
        "control": control,
        "counts": {"builds": len(builds), "cells": len(cells), "rows": len(matrix),
                   "compilers": len({b["compiler_id"] for b in builds})},
        "matrix": matrix,
        "builds": builds,
        "cells": cells,
        "permalinks_clang18_fast": links,
    }


def label(r):
    fam = "clang" if r["family"] == "clang" else "GCC"
    return "%s %s" % (fam, r["version"])


def matrix_md(doc):
    out = ["| compiler | target | opt | hardening macro | lost under hardening | vectorized unhardened |",
           "|---|---|---|---|---|---|"]
    for r in doc["matrix"]:
        lost = ", ".join(SHORT[k] for k in r["lost"]) or "none"
        if r["unknown"]:
            lost += " (unknown: %s)" % ", ".join(SHORT[k] for k in r["unknown"])
        vec = ", ".join(SHORT[k] for k in r["vectorized_none"]) or "none"
        flag = "" if r["macro_effective"] else " (no extra checks seen)"
        out.append("| %s | %s | %s | `%s`%s | **%s** | %s |" % (label(r), r["target"], r["opt"], r["macro_hardened"],
                                                              flag, lost, vec))
    # Compact grid: the three loops of the finding, one line per compiler.
    out += ["", "Compact view, the three loops of the finding (R = reverse, S = stride2, M = matmul; "
                "a letter means lost, `.` kept vectorized, `x` not vectorized even unhardened), "
                "cells are -O2 / -O3:", "",
            "| compiler | x86-64 | x86-64-v3 | aarch64 |", "|---|---|---|---|"]
    by, names = {}, {}
    for r in doc["matrix"]:
        major = r["version"].split(".")[0]
        by.setdefault((r["family"], major), {})[(r["target"], r["opt"])] = r
        names.setdefault((r["family"], major), [])
        if r["version"] not in names[(r["family"], major)]:
            names[(r["family"], major)].append(r["version"])
    for (fam, major), d in by.items():
        ver = " / ".join(names[(fam, major)])
        def cell(t):
            parts = []
            for o in cs.OPTS:
                r = d.get((t, o))
                if r is None:
                    continue
                s = ""
                for k, ch in (("k04_rev", "R"), ("k05_stride2", "S"), ("k08_matmul", "M")):
                    s += ch if k in r["lost"] else ("." if k in r["vectorized_none"] else "x")
                parts.append(s)
            return " / ".join(parts) if parts else "-"
        out.append("| %s %s | %s | %s | %s |" % ("clang" if fam == "clang" else "GCC", ver, cell("x86-64"),
                                                 cell("x86-64-v3"), cell("aarch64")))
    return "\n".join(out)


def write_readme_block(md):
    with open(README, encoding="utf-8") as f:
        text = f.read()
    a, b = text.index(BEGIN), text.index(END)
    new = text[:a + len(BEGIN)] + "\n" + md + "\n" + text[b:]
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)


def readme_block():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    a, b = text.index(BEGIN), text.index(END)
    return text[a + len(BEGIN):b].strip("\n")


def main():
    doc = compute()
    md = matrix_md(doc)
    if "--check" in sys.argv:
        ok = True
        with open(RESULTS, encoding="utf-8") as f:
            stored = json.load(f)
        if stored != json.loads(json.dumps(doc)):
            print("results.json differs from the recomputation"); ok = False
        if readme_block() != md:
            print("README matrix differs from the recomputation"); ok = False
        return 0 if ok else 1
    with open(RESULTS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    if os.path.exists(README) and BEGIN in open(README, encoding="utf-8").read():
        write_readme_block(md)
    print(md)
    print("control ok:", doc["control"]["ok"], doc["control"]["observed_lost"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
