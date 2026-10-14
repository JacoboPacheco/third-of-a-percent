#!/usr/bin/env python3
"""Day-one test, collection half (scratch code; the real harness comes later in harness/).

Runs on a GitHub Actions ubuntu-24.04 x64 runner. Builds every kernel NONE, FAST and NONE-NOVEC with
clang-18 and libc++-18, records hashes, vectorization remarks, trap counts and assembly, then times
pairs of binaries in ABBA order (20 repetitions per side, one process per repetition, pinned to one CPU).
It also builds the two real programs. It writes dayone/out/raw.json; evaluate.py turns that into the
intervals, the criteria and the verdict. Nothing here looks at a FAST timing to choose anything: sizes come
from the cache sizes, inner iterations from the NONE build only, and the kernel list is fixed.
"""
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KDIR = os.path.join(HERE, "kernels")
PDIR = os.path.join(HERE, "programs")
DEPS = os.path.join(HERE, "deps")
BUILD = os.path.join(HERE, "build")
OUT = os.path.join(HERE, "out")
ASM = os.path.join(OUT, "asm")

CXX = os.environ.get("DAYONE_CXX", "clang++-18")
OBJDUMP = os.environ.get("DAYONE_OBJDUMP", "objdump")
CPU = os.environ.get("DAYONE_CPU", "1")
COMMON = ["-O2", "-std=c++20", "-stdlib=libc++"]
FLAGS = {
    "none": ["-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE"],
    "fast": ["-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"],
    "novec": ["-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE", "-fno-vectorize"],
}
REMARK_FLAGS = ["-Rpass=loop-vectorize", "-Rpass-missed=loop-vectorize", "-Rpass-analysis=loop-vectorize"]
# bytes of working set per unit of n, counting every array of the kernel
KERNELS = {"k01_sum_fwd": 4, "k02_add_fwd": 12, "k03_stencil": 8, "k04_rev": 8, "k05_stride2": 12}
AA_KERNEL = "k02_add_fwd"
REPS = 20
TARGET_NS = 75e6
RAM_CAP = 256 * 1024 * 1024


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_size(s):
    s = s.strip()
    mult = {"K": 1024, "M": 1024 ** 2, "G": 1024 ** 3}
    return int(s[:-1]) * mult[s[-1]] if s[-1] in mult else int(s)


def caches():
    base = "/sys/devices/system/cpu/cpu0/cache"
    found = {}
    for d in sorted(os.listdir(base)):
        if not d.startswith("index"):
            continue
        rd = lambda f: open(os.path.join(base, d, f)).read().strip()
        level, typ, size = int(rd("level")), rd("type"), parse_size(rd("size"))
        if typ == "Instruction":
            continue
        found[level] = size
    llc = found[max(found)]
    return {"l1d": found[1], "l2": found[2], "llc": llc, "llc_level": max(found)}


def runner_info():
    lscpu = sh(["lscpu"]).stdout
    model = re.search(r"Model name:\s*(.*)", lscpu)
    return {
        "os": sh(["lsb_release", "-ds"]).stdout.strip(),
        "kernel": sh(["uname", "-r"]).stdout.strip(),
        "arch": sh(["uname", "-m"]).stdout.strip(),
        "cpu_model": model.group(1).strip() if model else None,
        "cores": os.cpu_count(),
        "lscpu": lscpu,
    }


def toolchain():
    v = sh([CXX, "--version"]).stdout.splitlines()
    pkg = sh(["dpkg-query", "-W", "-f=${Version}", "libc++-18-dev"]).stdout.strip()
    return {"clang": v[0] if v else None, "libcxx_package": "libc++-18-dev " + pkg}


def loop_line(src):
    for i, line in enumerate(open(src), 1):
        if "// LOOP" in line:
            return i
    raise SystemExit("no // LOOP marker in " + src)


def parse_remarks(text, fname, line):
    at_line, in_file = [], []
    for ln in text.splitlines():
        if "remark:" not in ln:
            continue
        if os.path.basename(fname) in ln:
            in_file.append(ln)
            if re.search(r"%s:%d:\d+: remark:" % (re.escape(os.path.basename(fname)), line), ln):
                at_line.append(ln.split("remark:", 1)[1].strip())
    vec = None
    width = None
    for r in at_line:
        m = re.match(r"vectorized loop \(vectorization width: (\d+)", r)
        if m:
            vec, width = True, int(m.group(1))
    if vec is None and any(r.startswith("loop not vectorized") for r in at_line):
        vec = False
    return {"vectorized": vec, "width": width, "at_loop_line": at_line, "all_in_file": in_file}


def function_asm(binary, name):
    dump = sh([OBJDUMP, "-d", "--no-show-raw-insn", binary]).stdout
    lines, keep = [], False
    head = re.compile(r"^[0-9a-f]+ <(_Z\d+%s[^>]*)>:$" % re.escape(name))
    for ln in dump.splitlines():
        if head.match(ln):
            keep = True
            lines.append(ln)
            continue
        if keep:
            if not ln.strip():
                break
            lines.append(ln)
    return lines


def count_traps(lines):
    ud2 = sum(1 for l in lines if re.search(r"\bud2\b", l))
    va = sum(1 for l in lines if "call" in l and "verbose_abort" in l)
    return {"ud2": ud2, "verbose_abort_calls": va, "total": ud2 + va}


def simd_lines(lines):
    return sum(1 for l in lines if "%xmm" in l and re.search(r"\b(p[a-z]+|movdq[au]|movups|movaps|shufps|unpck\w+)\b", l))


def normalize(lines):
    out = []
    for l in lines:
        l = re.sub(r"^\s*[0-9a-f]+:\s*", "", l)
        l = re.sub(r"\b[0-9a-f]{4,} <", "<", l)
        l = re.sub(r"<([^>+]*)\+0x[0-9a-f]+>", r"<\1+off>", l)
        out.append(l.rstrip())
    return out


def compile_(out, srcs, flags, extra_inc=()):
    cmd = [CXX] + COMMON + flags + [f"-I{p}" for p in extra_inc] + ["-o", out] + list(srcs)
    t = time.time()
    r = sh(cmd)
    return cmd, r, time.time() - t


def run_bin(binary, args):
    r = sh(["taskset", "-c", CPU, binary] + [str(a) for a in args])
    if r.returncode != 0:
        raise RuntimeError(f"{binary} {args} exited {r.returncode}: {r.stderr[-500:]}")
    d = dict(kv.split("=", 1) for kv in r.stdout.split())
    return {"ns": float(d["ns"]), "checksum": d["checksum"], "mode": int(d["mode"])}


def calibrate(binary, args_before_iters):
    best = min(run_bin(binary, args_before_iters + [1])["ns"] for _ in range(3))
    return max(1, min(10_000_000, int(round(TARGET_NS / best)))), best


def pair(a_bin, b_bin, args):
    """ABBA order: A B B A A B B A ... REPS runs per side."""
    a_ns, b_ns, a_ck, b_ck, order = [], [], set(), set(), []
    for k in range(REPS):
        seq = ("A", "B") if k % 2 == 0 else ("B", "A")
        for side in seq:
            r = run_bin(a_bin if side == "A" else b_bin, args)
            (a_ns if side == "A" else b_ns).append(r["ns"])
            (a_ck if side == "A" else b_ck).add(r["checksum"])
            order.append(side)
    return {"a_ns": a_ns, "b_ns": b_ns, "a_checksums": sorted(a_ck), "b_checksums": sorted(b_ck),
            "order": "".join(order)}


def build_kernels(raw):
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(ASM, exist_ok=True)
    kinfo = {}
    for k in KERNELS:
        src = os.path.join(KDIR, k + ".cpp")
        line = loop_line(src)
        info = {"source": f"dayone/kernels/{k}.cpp", "loop_line": line, "builds": {}}
        asm_by_mode = {}
        for mode, flags in FLAGS.items():
            out = os.path.join(BUILD, f"{k}.{mode}")
            cmd, r, secs = compile_(out, [src], flags + REMARK_FLAGS)
            if r.returncode != 0:
                raise SystemExit(f"build failed {k} {mode}:\n{r.stderr}")
            with open(os.path.join(OUT, f"remarks.{k}.{mode}.txt"), "w") as f:
                f.write(r.stderr)
            lines = function_asm(out, "kern_" + k)
            asm_by_mode[mode] = lines
            with open(os.path.join(ASM, f"{k}.{mode}.s"), "w") as f:
                f.write("\n".join(lines) + "\n")
            info["builds"][mode] = {
                "binary": os.path.relpath(out, HERE),
                "sha256": sha256(out),
                "command": " ".join(cmd),
                "remarks": parse_remarks(r.stderr, src, line),
                "traps": count_traps(lines),
                "asm_lines": len(lines),
                "simd_xmm_lines": simd_lines(lines),
                "compile_seconds": round(secs, 2),
            }
        diff = difflib.unified_diff(normalize(asm_by_mode["none"]), normalize(asm_by_mode["fast"]),
                                    f"{k}.none.s", f"{k}.fast.s", lineterm="")
        with open(os.path.join(ASM, f"{k}.none-vs-fast.diff"), "w") as f:
            f.write("\n".join(diff) + "\n")
        kinfo[k] = info
    # A/A: a byte-identical copy of the NONE binary at a second path
    a = os.path.join(BUILD, f"{AA_KERNEL}.none")
    b = os.path.join(BUILD, f"{AA_KERNEL}.none_copy")
    shutil.copyfile(a, b)
    shutil.copymode(a, b)
    raw["aa_binaries"] = {"a": os.path.relpath(a, HERE), "b": os.path.relpath(b, HERE),
                          "a_sha256": sha256(a), "b_sha256": sha256(b)}
    raw["kernels"] = kinfo


def time_kernels(raw, cache):
    targets = {"L1": cache["l1d"] // 2, "L2": cache["l2"] // 2, "RAM": min(4 * cache["llc"], RAM_CAP)}
    raw["size_targets_bytes"] = targets
    cells = []
    for k, bpe in KERNELS.items():
        for sc, tgt in targets.items():
            n = max(64, tgt // bpe)
            none = os.path.join(BUILD, f"{k}.none")
            iters, one = calibrate(none, [n])
            args = [n, iters]
            t = time.time()
            cell = {"cell_id": f"{k}.{sc}", "kernel": k, "size_class": sc, "n": n,
                    "working_set_bytes": n * bpe, "iters": iters, "calibration_ns_one_call": one,
                    "args": args,
                    "fast": pair(none, os.path.join(BUILD, f"{k}.fast"), args),
                    "novec": pair(none, os.path.join(BUILD, f"{k}.novec"), args)}
            if k == AA_KERNEL:
                cell["aa"] = pair(none, os.path.join(BUILD, f"{k}.none_copy"), args)
            cell["seconds"] = round(time.time() - t, 1)
            print(f"[time] {cell['cell_id']} n={n} iters={iters} {cell['seconds']}s", flush=True)
            cells.append(cell)
    raw["cells"] = cells


def whole_traps(binary):
    dump = sh([OBJDUMP, "-d", "--no-show-raw-insn", binary]).stdout.splitlines()
    return count_traps(dump)


def build_program(name, srcs, inc, run_args_before_iters):
    res = {"name": name, "built": False, "builds": {}}
    for mode in ("none", "fast"):
        out = os.path.join(BUILD, f"{name}.{mode}")
        cmd, r, secs = compile_(out, srcs, FLAGS[mode], inc)
        res["builds"][mode] = {"command": " ".join(cmd), "returncode": r.returncode,
                               "stderr_tail": r.stderr[-3000:], "compile_seconds": round(secs, 1)}
        if r.returncode != 0:
            return res
        res["builds"][mode].update({"binary": os.path.relpath(out, HERE), "sha256": sha256(out),
                                    "traps": whole_traps(out)})
    res["built"] = True
    none, fast = (os.path.join(BUILD, f"{name}.{m}") for m in ("none", "fast"))
    copy = os.path.join(BUILD, f"{name}.none_copy")
    shutil.copyfile(none, copy)
    shutil.copymode(none, copy)
    res["aa_sha256"] = [sha256(none), sha256(copy)]
    try:
        iters, one = calibrate(none, run_args_before_iters)
        args = run_args_before_iters + [iters]
        res.update({"iters": iters, "calibration_ns_one_iter": one, "args": args,
                    "fast": pair(none, fast, args)})
        if name == "json_parse":
            res["aa"] = pair(none, copy, args)
        res["ran"] = True
    except RuntimeError as e:
        res["ran"] = False
        res["run_error"] = str(e)
    return res


def programs(raw):
    progs = []
    json_file = os.path.join(DEPS, "twitter.json")
    progs.append(build_program("json_parse", [os.path.join(PDIR, "json_parse.cpp")],
                               [os.path.join(DEPS, "json")], [json_file]))
    attempts = []
    second = None
    fmt_inc = os.path.join(DEPS, "fmt", "include")
    if os.path.isdir(fmt_inc):
        second = build_program("fmt_format", [os.path.join(PDIR, "fmt_format.cpp")], [fmt_inc], [20000])
        attempts.append({"name": "fmt_format", "built": second["built"]})
    if (second is None or not second["built"]) and os.path.isdir(os.path.join(DEPS, "pugixml", "src")):
        psrc = os.path.join(DEPS, "pugixml", "src")
        second = build_program("pugixml_parse", [os.path.join(PDIR, "pugixml_parse.cpp"),
                                                 os.path.join(psrc, "pugixml.cpp")], [psrc], [20000])
        attempts.append({"name": "pugixml_parse", "built": second["built"]})
    if second is not None:
        progs.append(second)
    raw["second_program_attempts"] = attempts
    raw["programs"] = progs


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    cache = caches()
    raw = {
        "schema": "dayone-raw-1",
        "run": {
            "commit": os.environ.get("GITHUB_SHA"),
            "workflow_run_url": (f"{os.environ.get('GITHUB_SERVER_URL')}/{os.environ.get('GITHUB_REPOSITORY')}"
                                 f"/actions/runs/{os.environ.get('GITHUB_RUN_ID')}"
                                 if os.environ.get("GITHUB_RUN_ID") else None),
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "runner": runner_info(), "cache_bytes": cache, "toolchain": toolchain(),
            "flags": {"common": " ".join(COMMON), **{m: " ".join(f) for m, f in FLAGS.items()},
                      "remarks": " ".join(REMARK_FLAGS)},
            "pinned_cpu": CPU, "reps_per_side": REPS, "target_ns_per_process": TARGET_NS,
            "criteria_sha256": sha256(os.path.join(HERE, "criteria.json")),
        },
    }
    manifest = os.path.join(DEPS, "manifest.json")
    raw["downloads"] = json.load(open(manifest)) if os.path.exists(manifest) else None
    build_kernels(raw)
    print(f"[build] kernels done {time.time() - t0:.0f}s", flush=True)
    programs(raw)
    print(f"[programs] done {time.time() - t0:.0f}s", flush=True)
    time_kernels(raw, cache)
    raw["run"]["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT, "raw.json"), "w") as f:
        json.dump(raw, f, indent=1)
    print(f"[done] {raw['run']['seconds']}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
