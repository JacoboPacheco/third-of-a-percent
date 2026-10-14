#!/usr/bin/env python3
"""One job of the versions column: the unchanged harness with clang++-<N>, plus the macro probe.

    python3 versions/run_version.py --version 20 --out out

1. Records the toolchain (clang --version, dpkg versions of clang-N, libc++-N-dev, libc++abi-N-dev).
2. Macro probe (versions/probe.cpp): NONE must run clean, FAST must die from a signal. Recorded, not
   enforced here; versions/analyze.py makes a toolchain INCONCLUSIVE if FAST does not trap.
3. Runs harness/run.py UNCHANGED with HARNESS_CXX=clang++-N: all eight kernels, sizes L1 and L2, no
   programs, harness/criteria-v3.json. Nothing of the harness is imported or patched.
4. Writes <out>/toolchain.json: version, toolchain, probe, and the vectorization remark result
   (vectorized, width) of every kernel in NONE and FAST, read from <out>/results.json.

Exit code is the harness's.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CRITERIA = "harness/criteria-v3.json"
PKGS = ("clang-{n}", "libc++-{n}-dev", "libc++abi-{n}-dev", "libunwind-{n}-dev")
MACRO = {"none": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE",
         "fast": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, **kw)


def packages(n):
    out = {}
    for p in PKGS:
        name = p.format(n=n)
        out[name] = run(["dpkg-query", "-W", "-f=${Version}", name]).stdout.strip() or None
    return out


def probe_verdict(none_rc, fast_rc):
    """NONE exit code 0 and FAST killed by a signal (negative return code) or a nonzero exit."""
    return {"none_exit": none_rc, "fast_exit": fast_rc,
            "none_runs_clean": none_rc == 0,
            "fast_traps": fast_rc is not None and fast_rc != 0}


def macro_probe(cxx, build_dir):
    os.makedirs(build_dir, exist_ok=True)
    rc = {}
    for mode in ("none", "fast"):
        exe = os.path.join(build_dir, f"probe.{mode}")
        b = run([cxx, "-O2", "-std=c++20", "-stdlib=libc++", MACRO[mode], "-o", exe, "versions/probe.cpp"])
        if b.returncode != 0:
            return {"built": False, "error": b.stderr[-2000:], "mode": mode,
                    **probe_verdict(None, None)}
        r = run([exe])
        rc[mode] = r.returncode
    return {"built": True, **probe_verdict(rc["none"], rc["fast"])}


def vectorization_map(results):
    """{kernel: {"none": {"vectorized", "width"}, "fast": {...}}} from the L1 (else first) cell of each kernel."""
    out = {}
    for c in results.get("cells", []):
        k = c["kernel"]
        if k in out and c.get("size_class") != "L1":
            continue
        out[k] = {"none": {"vectorized": c["vectorized_none"]["vectorized"], "width": c["vectorized_none"].get("width")},
                  "fast": {"vectorized": c["vectorized_fast"]["vectorized"], "width": c["vectorized_fast"].get("width")}}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--version", required=True, help="LLVM major version, e.g. 20")
    ap.add_argument("--out", default="out")
    ap.add_argument("--build", default="build/versions")
    ap.add_argument("--kernels", default="all")
    ap.add_argument("--sizes", default="L1,L2")
    ap.add_argument("--dry-run", action="store_true", help="print the harness command and stop")
    a = ap.parse_args(argv)
    if not a.version.isdigit():
        raise SystemExit("--version must be a number")
    cxx = f"clang++-{a.version}"
    out = os.path.abspath(a.out)
    cmd = [sys.executable, "harness/run.py", "--kernels", a.kernels, "--sizes", a.sizes, "--programs", "none",
           "--criteria", CRITERIA, "--out", out, "--build", os.path.abspath(os.path.join(a.build, "kernels"))]
    if a.dry_run:
        print(f"HARNESS_CXX={cxx} " + " ".join(cmd))
        return 0
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, HARNESS_CXX=cxx)
    tc = {"version": int(a.version), "clang": (run([cxx, "--version"]).stdout.splitlines() or [None])[0],
          "packages": packages(a.version), "compiler": cxx}
    tc["probe"] = macro_probe(cxx, os.path.abspath(os.path.join(a.build, "probe")))
    print("[probe]", json.dumps(tc["probe"]), flush=True)
    rc = subprocess.run(cmd, cwd=REPO, env=env).returncode
    res = os.path.join(out, "results.json")
    tc["vectorization"] = {}
    if os.path.exists(res):
        with open(res, encoding="utf-8") as f:
            tc["vectorization"] = vectorization_map(json.load(f))
    with open(os.path.join(out, "toolchain.json"), "w", encoding="utf-8") as f:
        json.dump(tc, f, indent=1)
    return rc


if __name__ == "__main__":
    sys.exit(main())
