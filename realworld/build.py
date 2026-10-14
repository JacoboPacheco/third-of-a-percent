#!/usr/bin/env python3
"""Builds the real programs NONE, FAST, the aligned pair and the two profile builds (realworld/PLAN.md).

Usage: python3 realworld/build.py --deps <deps> --work <work> --bin <bin dir> --out <json> <program> [...]

For each program: every library source compiled to an object per build (in parallel), the objects
archived with `ar rcsD`, the driver compiled and linked against the archive. Per build it records the
command, sha256, whole-binary ud2 count, the sha256 of the .text section and the compile seconds;
per program the clang "vectorized loop" remark counts, NONE and FAST, at every census-2 lost
location in its sources (common.lost_in_build). Binaries go to <bin>/<program>.<build>.
"""
import argparse
import concurrent.futures
import fnmatch
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import common  # noqa: E402

CXX = os.environ.get("RW_CXX", "clang++-18")
CC = os.environ.get("RW_CC", "clang-18")
OBJDUMP = os.environ.get("RW_OBJDUMP", "objdump")
OBJCOPY = os.environ.get("RW_OBJCOPY", "objcopy")
AR = os.environ.get("RW_AR", "ar")
NONE = "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE"
FAST = "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"
ALIGN = "-falign-loops=64"
DEBUG = "-gline-tables-only"
BUILDS = {"none": [NONE], "fast": [FAST], "none_a64": [NONE, ALIGN], "fast_a64": [FAST, ALIGN],
          "none_g": [NONE, DEBUG], "fast_g": [FAST, DEBUG]}
REMARKS = ["-Rpass=loop-vectorize", "-Rpass-missed=loop-vectorize"]
REMARK_BUILDS = ("none", "fast")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def expand_sources(root, globs, exclude):
    found = set()
    for g in globs:
        for p in glob.glob(os.path.join(root, g), recursive=True):
            rel = os.path.relpath(p, root).replace("\\", "/")
            if any(fnmatch.fnmatch(rel, e) or fnmatch.fnmatch(os.path.basename(rel), e) for e in exclude):
                continue
            found.add(rel)
    return sorted(found)


def flags_for(prog, build, root, cxx=True):
    std = ["-std=" + prog["std"]] if cxx else []
    lib = ["-stdlib=libc++"] if cxx else []
    inc = ["-I" + os.path.normpath(os.path.join(root, i)) for i in prog["includes"]]
    return ["-O2"] + std + lib + BUILDS[build] + ["-D" + d for d in prog["defines"]] + inc + ["-pthread"]


def run(cmd, cwd=None):
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return r, time.time() - t


def objname(rel):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", rel.replace("/", "__")) + ".o"


def text_sha(binary, tmp):
    r = subprocess.run([OBJCOPY, "-O", "binary", "--only-section=.text", binary, tmp], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    s = sha256(tmp)
    os.remove(tmp)
    return s


def traps(binary):
    dump = subprocess.run([OBJDUMP, "-d", "--no-show-raw-insn", binary], capture_output=True, text=True).stdout
    return sum(1 for ln in dump.splitlines() if re.search(r"\bud2\b", ln))


def build_program(name, prog, deps, work, bindir, jobs, builds=None):
    builds = builds or list(BUILDS)
    root = os.path.join(deps, name, prog["root"])
    srcs = expand_sources(root, prog["sources"], prog.get("exclude", []))
    csrcs = [os.path.normpath(os.path.join(root, c)) for c in prog.get("c_sources", [])]
    tasks = []
    for b in builds:
        od = os.path.join(work, name, b)
        os.makedirs(od, exist_ok=True)
        rem = REMARKS if b in REMARK_BUILDS else []
        for rel in srcs:
            obj = os.path.join(od, objname(rel))
            tasks.append((b, [CXX] + flags_for(prog, b, root) + rem + ["-c", os.path.join(root, rel), "-o", obj], obj))
        for c in csrcs:
            obj = os.path.join(od, "c__" + objname(os.path.basename(c)))
            tasks.append((b, [CC] + flags_for(prog, b, root, cxx=False) + ["-c", c, "-o", obj], obj))
    print(f"[build] {name}: {len(srcs)} C++ and {len(csrcs)} C sources x {len(builds)} builds = {len(tasks)} compiles",
          flush=True)
    stderr = {b: [] for b in builds}
    seconds = {b: 0.0 for b in builds}
    objs = {b: [] for b in builds}
    failed = []
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(run, cmd): (b, cmd, obj) for b, cmd, obj in tasks}
        for fu in concurrent.futures.as_completed(futs):
            b, cmd, obj = futs[fu]
            r, dt = fu.result()
            seconds[b] += dt
            stderr[b].append(r.stderr)
            if r.returncode != 0:
                failed.append((cmd[-3], r.stderr[-2000:]))
            else:
                objs[b].append(obj)
    if failed:
        for src, err in failed[:5]:
            print(f"[error] {src}\n{err}", flush=True)
        raise SystemExit(f"{name}: {len(failed)} compiles failed")
    print(f"[build] {name}: objects in {time.time() - t0:.0f} s", flush=True)

    info = {"program": name, "root": prog["root"], "sources": len(srcs), "c_sources": len(csrcs), "builds": {}}
    for b in builds:
        lib = None
        if objs[b]:
            lib = os.path.join(work, name, f"lib{name}.{b}.a")
            if os.path.exists(lib):
                os.remove(lib)
            r, _ = run([AR, "rcsD", lib] + sorted(objs[b]))
            if r.returncode != 0:
                raise SystemExit(f"{name} {b}: ar failed: {r.stderr}")
        out = os.path.join(bindir, f"{name}.{b}")
        rem = REMARKS if b in REMARK_BUILDS else []
        cmd = ([CXX] + flags_for(prog, b, root) + rem + ["-o", out, os.path.join(REPO, prog["driver"])]
               + ([lib] if lib else []))
        r, dt = run(cmd)
        seconds[b] += dt
        stderr[b].append(r.stderr)
        if r.returncode != 0:
            raise SystemExit(f"{name} {b}: driver build or link failed:\n{r.stderr[-4000:]}")
        shown = " ".join(c.replace(REPO + os.sep, "").replace(deps + os.sep, "<deps>/") for c in cmd)
        info["builds"][b] = {"binary": os.path.basename(out), "sha256": sha256(out), "bytes": os.path.getsize(out),
                             "text_sha256": text_sha(out, out + ".text.bin"), "traps": traps(out),
                             "compile_seconds": round(seconds[b], 1), "link_command": shown}
        print(f"[build] {name}.{b}: sha256 {info['builds'][b]['sha256'][:16]} ud2 {info['builds'][b]['traps']} "
              f"text {str(info['builds'][b]['text_sha256'])[:16]}", flush=True)
    bb = info["builds"]
    info["text_identical"] = {f"{m}_vs_{m}_g": bb[m]["text_sha256"] == bb[m + "_g"]["text_sha256"]
                              for m in ("none", "fast") if m in bb and m + "_g" in bb}
    info["example_compile"] = " ".join(tasks[0][1]).replace(deps + os.sep, "<deps>/") if tasks else None
    if not all(b in builds for b in REMARK_BUILDS):
        return info
    # vectorization remarks at the census lost locations
    locs = {b: common.remark_locations("\n".join(stderr[b])) for b in REMARK_BUILDS}
    projects = sorted({r["lost_project"] for r in load_rows() if r["program"] == name and r["lost_project"]})
    loops = [lp for p in projects for lp in common.lost_loops_for(p)]
    info["lost_locations"] = common.lost_in_build(locs["none"], locs["fast"], loops)
    info["vectorized_remarks_total"] = {b: sum(v["vectorized"] for v in locs[b].values()) for b in REMARK_BUILDS}
    n_lost = sum(1 for x in info["lost_locations"] if x["lost_here_too"])
    print(f"[remarks] {name}: {n_lost} of {len(info['lost_locations'])} census lost locations lose vectorization "
          f"here too; vectorized remarks none/fast {info['vectorized_remarks_total']}", flush=True)
    return info


def load_rows():
    with open(os.path.join(HERE, "programs.json"), encoding="utf-8") as f:
        return json.load(f)["rows"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--deps", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--builds", default=",".join(BUILDS), help="comma-separated subset of the six builds")
    ap.add_argument("programs", nargs="+")
    a = ap.parse_args(argv)
    with open(os.path.join(HERE, "programs.json"), encoding="utf-8") as f:
        doc = json.load(f)
    deps, work, bindir = (os.path.abspath(x) for x in (a.deps, a.work, a.bin))
    os.makedirs(bindir, exist_ok=True)
    tool = subprocess.run([CXX, "--version"], capture_output=True, text=True).stdout.splitlines()
    pkg = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "libc++-18-dev"], capture_output=True, text=True).stdout
    out = {"toolchain": {"clang": tool[0] if tool else None, "libcxx_package": pkg or None,
                         "builds": {b: " ".join(f) for b, f in BUILDS.items()},
                         "common": "-O2 -std=<project std> -stdlib=libc++ -pthread (no -march, no -DNDEBUG: the census flags)"},
           "programs": {}}
    for name in a.programs:
        builds = [b.strip() for b in a.builds.split(",") if b.strip()]
        for b in builds:
            if b not in BUILDS:
                raise SystemExit(f"unknown build {b}")
        out["programs"][name] = build_program(name, doc["programs"][name], deps, work, bindir, a.jobs, builds)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
