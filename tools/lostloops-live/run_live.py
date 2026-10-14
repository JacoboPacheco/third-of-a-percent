#!/usr/bin/env python3
"""One live test of tools/lostloops/ against the census (tools/lostloops-live/PLAN.md).

    python3 tools/lostloops-live/run_live.py --project leveldb|spectra|lightgbm --work DIR [--jobs N]
                                             [--clang clang++-18] [--out DIR]

1. fetches the project with corpus/census.py's own fetch (sha256 checked, drivers and generated
   headers included),
2. writes a compile_commands.json with an ordinary user command per translation unit,
3. runs tools/lostloops/lostloops.py on it (--root the project root),
4. compares report.json with expected/<project>.json (compare.py) and writes comparison.json.
Exit 0 only when nothing differs; 1 on a difference; 2 when the tool did not run.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "corpus"))

import compare as cmp  # noqa: E402


def user_command(p, tu, clang):
    """What a build system would run for this file: the project's flags, none of lostloops's."""
    return [clang, "-O2", "-std=" + (p.get("std") or "c++20")] + ["-I" + i for i in p["includes"]] + \
           ["-D" + d for d in p["defines"]] + ["-c", tu, "-o", tu.replace("/", "__") + ".o"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, choices=["leveldb", "spectra", "lightgbm"])
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", help="where report/, compile_commands.json and comparison.json go (default WORK/out)")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--clang", default="clang++-18")
    a = ap.parse_args(argv)
    work = os.path.abspath(a.work)
    out = os.path.abspath(a.out or os.path.join(work, "out"))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(HERE, "expected", a.project + ".json"), encoding="utf-8") as f:
        expected = json.load(f)

    import census  # corpus/census.py; needs corpus/ in the checkout
    p = census.load_projects([a.project], expected["projects_file"])[0]
    if p["commit"] != expected["commit"]:
        print("run_live: the pinned commit in corpus/%s (%s) is not the one the expected list was made at (%s)"
              % (expected["projects_file"], p["commit"], expected["commit"]), file=sys.stderr)
        return 2
    deps = os.path.join(work, "deps")
    census.fetch([p], deps)
    root = census.project_root(p, deps).replace("\\", "/")
    tus = census.translation_units(p, root)
    db = [{"directory": root, "file": tu, "arguments": user_command(p, tu, a.clang)} for tu in tus]
    ccpath = os.path.join(out, "compile_commands.json")
    with open(ccpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(db, f, indent=1)
    print("run_live: %s: %d translation units, root %s" % (a.project, len(tus), root), flush=True)

    tool = os.path.join(REPO, "tools", "lostloops", "lostloops.py")
    cmd = [sys.executable, tool, "--compile-commands", ccpath, "--root", root, "--out", os.path.join(out, "report"),
           "--clang", a.clang, "--jobs", str(a.jobs)]
    r = subprocess.run(cmd)
    repath = os.path.join(out, "report", "report.json")
    if r.returncode != 0 or not os.path.exists(repath):
        print("run_live: lostloops exited %d without a report" % r.returncode, file=sys.stderr)
        return 2
    with open(repath, encoding="utf-8") as f:
        report = json.load(f)
    outside = [os.path.dirname(root).replace("\\", "/")]
    res = cmp.compare(report, expected, root, outside)
    res.update({"project": a.project, "census_run": expected["census_run"], "commit": expected["commit"],
                "clang": report["toolchain"]["clang"], "tool": report["tool"],
                "tool_totals": report["totals"], "failed_files": report["failed"]})
    with open(os.path.join(out, "comparison.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print("clang: %s" % res["clang"])
    for k in ("totals", "lists", "details", "checks"):
        print("%s: %s" % (k, "equal" if not res[k] else "%d difference(s)" % len(res[k])))
        for x in res[k][:40]:
            print("   " + x)
    if report["failed"]:
        print("files that did not compile: %d" % len(report["failed"]))
        for x in report["failed"][:10]:
            print("   %(file)s (%(build)s): %(error)s" % x)
    print("RESULT %s: %s" % (a.project, "PASS" if res["pass"] else "FAIL"))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
