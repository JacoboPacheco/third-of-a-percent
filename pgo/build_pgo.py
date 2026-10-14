#!/usr/bin/env python3
"""Builds the PGO pair of one hardening mode for the real programs (pgo/PLAN.md "What is built").

Usage: python3 pgo/build_pgo.py --mode none|fast --deps <deps> --work <work> --bin <bin dir>
                                --out <json> <program> [...]

Per program, in this order, all with realworld/build.py's own functions (imported, not edited):
  1. instrumented build  (<mode> flag + -fprofile-instr-generate)
  2. training: the instrumented binary runs once per row of the program (the row's arguments and an
     iteration count of 1), one .profraw per run
  3. llvm-profdata merge -> <dir of --out>/<program>.<mode>.profdata
  4. PGO build and aligned PGO build (the same flags + -fprofile-instr-use=<profdata>, and + -falign-loops=64)
Binaries are written as <bin>/<program>.<mode> and <bin>/<program>.<mode>_a64, the names
realworld/measure.py reads. The profile is per mode and per program: NONE and FAST never share one.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RW = os.path.join(REPO, "realworld")
sys.path.insert(0, RW)
import build  # noqa: E402  (realworld/build.py)
import common  # noqa: E402  (realworld/common.py)

PROFDATA = os.environ.get("PGO_PROFDATA", "llvm-profdata-18")
GEN = "-fprofile-instr-generate"
TRAIN_TIMEOUT_S = 1200
WARN_OUT_OF_DATE = re.compile(r"profile-instr-out-of-date|function control flow change detected|hash mismatch")
WARN_MISSING = re.compile(r"profile-instr-missing|no profile data available")


def mode_flag(mode):
    return {"none": build.NONE, "fast": build.FAST}[mode]


def register_builds(mode, profdata=None):
    """Adds this mode's PGO builds to realworld/build.py's table (in this process only)."""
    m = mode_flag(mode)
    build.BUILDS[f"{mode}_gen"] = [m, GEN]
    if profdata:
        use = f"-fprofile-instr-use={profdata}"
        build.BUILDS[f"{mode}_pgo"] = [m, use]
        build.BUILDS[f"{mode}_pgo_a64"] = [m, use, build.ALIGN]


class RemarkCapture:
    """Wraps build.run: for the PGO (not the aligned) compiles, appends clang's vectorizer remark flags
    and keeps the stderr, so the remarks and the profile warnings can be counted afterwards."""

    def __init__(self):
        self.stderr = []
        self.orig = build.run

    def __call__(self, cmd, cwd=None):
        use = any(a.startswith("-fprofile-instr-use=") for a in cmd)
        compile_only = "-c" in cmd
        aligned = build.ALIGN in cmd
        if use and compile_only and not aligned:
            cmd = cmd + build.REMARKS
        r, dt = self.orig(cmd, cwd)
        if use and compile_only:
            self.stderr.append((aligned, r.stderr))
        return r, dt

    def install(self):
        build.run = self

    def restore(self):
        build.run = self.orig


def train(binary, rows, outdir, mode, program):
    """Runs the instrumented binary once per row; returns the per-row records and the .profraw paths."""
    os.makedirs(outdir, exist_ok=True)
    recs = []
    for r in rows:
        raw = os.path.join(outdir, f"{program}.{mode}.{r['row']}.%p.profraw")
        env = dict(os.environ, LLVM_PROFILE_FILE=raw)
        t = time.time()
        p = subprocess.run([binary] + r["args"] + ["1"], capture_output=True, text=True, env=env,
                           timeout=TRAIN_TIMEOUT_S)
        if p.returncode != 0:
            raise SystemExit(f"training {r['row']} exited {p.returncode}: {p.stderr[-800:]}")
        res = common.parse_result(p.stdout)
        recs.append({"row": r["row"], "args": r["args"] + ["1"], "checksum": res["checksum"],
                     "checksum_r": res["checksum_r"], "seconds": round(time.time() - t, 1)})
        print(f"[train] {program}.{mode} {r['row']}: {recs[-1]['seconds']} s checksum {res['checksum']}", flush=True)
    raws = sorted(os.path.join(outdir, f) for f in os.listdir(outdir)
                  if f.startswith(f"{program}.{mode}.") and f.endswith(".profraw"))
    if len(raws) < len(rows):
        raise SystemExit(f"{program}.{mode}: {len(raws)} .profraw files for {len(rows)} runs "
                         "(the instrumented binary wrote no profile?)")
    return recs, raws


def merge(raws, out):
    r = subprocess.run([PROFDATA, "merge", "-o", out] + raws, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"llvm-profdata merge failed: {r.stderr[-1500:]}")
    show = subprocess.run([PROFDATA, "show", out], capture_output=True, text=True).stdout
    funcs = re.search(r"Total functions:\s*(\d+)", show)
    top = re.search(r"Maximum function count:\s*(\d+)", show)
    return {"functions": int(funcs.group(1)) if funcs else None,
            "max_function_count": int(top.group(1)) if top else None}


def count_warnings(captured):
    """Profile-mismatch warnings in the plain PGO compiles."""
    lines = "\n".join(s for aligned, s in captured if not aligned).splitlines()
    return {"out_of_date": sum(1 for ln in lines if WARN_OUT_OF_DATE.search(ln)),
            "missing": sum(1 for ln in lines if WARN_MISSING.search(ln))}


def lost_vectorized(captured, loops):
    """Per census lost location: clang's 'vectorized loop' remark count in this PGO build."""
    text = "\n".join(s for aligned, s in captured if not aligned)
    rows = common.lost_in_build(common.remark_locations(text), {}, loops)
    return [{"location": x["location"], "vectorized": x["vectorized_none"]} for x in rows]


def build_one(program, prog, rows, mode, deps, work, bindir, jobs, metadir):
    # 1. instrumented build
    register_builds(mode)
    genbin = os.path.join(work, "genbin")
    os.makedirs(genbin, exist_ok=True)
    gen = build.build_program(program, prog, deps, os.path.join(work, "gen"), genbin, jobs, [f"{mode}_gen"])
    shutil.rmtree(os.path.join(work, "gen"), ignore_errors=True)
    # 2. training, 3. merge
    recs, raws = train(os.path.join(genbin, f"{program}.{mode}_gen"), rows, os.path.join(work, "raw"), mode, program)
    profdata = os.path.abspath(os.path.join(metadir, f"{program}.{mode}.profdata"))
    summary = merge(raws, profdata)
    summary.update({"file": os.path.basename(profdata), "bytes": os.path.getsize(profdata),
                    "sha256": build.sha256(profdata), "raw_files": len(raws),
                    "raw_bytes": sum(os.path.getsize(x) for x in raws)})
    # 4. the PGO builds, with the remark capture
    register_builds(mode, profdata)
    cap = RemarkCapture()
    cap.install()
    try:
        pgo = build.build_program(program, prog, deps, os.path.join(work, "pgo"), genbin, jobs,
                                  [f"{mode}_pgo", f"{mode}_pgo_a64"])
    finally:
        cap.restore()
    shutil.rmtree(os.path.join(work, "pgo"), ignore_errors=True)
    for suffix, final in (("pgo", ""), ("pgo_a64", "_a64")):
        src = os.path.join(genbin, f"{program}.{mode}_{suffix}")
        dst = os.path.join(bindir, f"{program}.{mode}{final}")
        shutil.copyfile(src, dst)
        shutil.copymode(src, dst)
    projects = sorted({r["lost_project"] for r in rows if r["lost_project"]})
    loops = [lp for p in projects for lp in common.lost_loops_for(p)]
    return {"program": program, "mode": mode,
            "instrumented": gen["builds"][f"{mode}_gen"],
            "training": {"rows": recs, "note": "the same fixed input that is timed (training input equals test input)"},
            "profile": summary,
            "builds": {"pgo": pgo["builds"][f"{mode}_pgo"], "pgo_a64": pgo["builds"][f"{mode}_pgo_a64"]},
            "binary_names": {"pgo": f"{program}.{mode}", "pgo_a64": f"{program}.{mode}_a64"},
            "profile_warnings": count_warnings(cap.stderr),
            "census_lost_locations": lost_vectorized(cap.stderr, loops)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["none", "fast"])
    ap.add_argument("--deps", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("programs", nargs="+")
    a = ap.parse_args(argv)
    with open(os.path.join(RW, "programs.json"), encoding="utf-8") as f:
        doc = json.load(f)
    deps, work, bindir = (os.path.abspath(x) for x in (a.deps, a.work, a.bin))
    metadir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(bindir, exist_ok=True)
    os.makedirs(metadir, exist_ok=True)
    tool = subprocess.run([build.CXX, "--version"], capture_output=True, text=True).stdout.splitlines()
    pd = subprocess.run([PROFDATA, "--version"], capture_output=True, text=True).stdout.splitlines()
    out = {"kind": "pgo-build", "schema": 1, "mode": a.mode,
           "toolchain": {"clang": tool[0] if tool else None, "llvm_profdata": pd[1].strip() if len(pd) > 1 else None,
                         "common": "-O2 -std=<project std> -stdlib=libc++ -pthread (no -march, no -DNDEBUG), "
                                   "-fprofile-instr-generate, then -fprofile-instr-use=<own profile>"},
           "programs": {}}
    for name in a.programs:
        rows = [r for r in doc["rows"] if r["program"] == name]
        if not rows:
            raise SystemExit(f"no row of realworld/programs.json uses program {name}")
        out["programs"][name] = build_one(name, doc["programs"][name], rows, a.mode, deps, work, bindir, a.jobs, metadir)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
