#!/usr/bin/env python3
"""The compile-time census: how many vectorized loops in real C++ code lose SIMD under libc++ FAST.

    python3 corpus/census.py all --deps DIR --work DIR --out DIR [--jobs N] [--only a,b]
                             [--projects projects2.json] [--target baseline|avx2] [--shard K]

  fetch    download every pinned file in corpus/projects.json and check its sha256 (a mismatch
           stops the run); unpack; copy the drivers; write the configured headers
  build    compile every translation unit of every project twice, NONE and FAST, with clang's
           loop-vectorize remarks on stderr and an optimization record (YAML) per object
  analyze  match loops between the two builds and write census.json, lost_loops.json,
           objects.sha256 and remarks.tar.gz into --out; every lost loop's translation unit is
           rebuilt in FAST with -gline-tables-only and its traps traced to source (index evidence)

--projects picks the list (projects.json: census 1; projects2.json: census 2, corpus/PLAN2.md).
--target avx2 adds -march=x86-64-v3 (a labelled sensitivity run). --shard K compiles only the
projects whose "shard" is K (corpus/merge.py joins the shards); the kernels are in every shard.

No linking, no running: every number comes from the compiler's own records and from objdump.
The 8 kernels in kernels/ go through the same pipeline as a control ("controls.kernels").
Needs clang++-18 with libc++-18 (Ubuntu noble apt), objdump (binutils) and llvm-cxxfilt-18.
"""
import argparse
import collections
import concurrent.futures
import fnmatch
import glob
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import classify  # noqa: E402
import optrecord  # noqa: E402

CXX = os.environ.get("CENSUS_CXX", "clang++-18")
CXXFILT = os.environ.get("CENSUS_CXXFILT", "llvm-cxxfilt-18")
OBJDUMP = os.environ.get("CENSUS_OBJDUMP", "objdump")
LIBCXX_DIR = "/usr/lib/llvm-18/include/c++/v1/"
ORIGINS = ("project", "driver", "libc++", "system")

MODES = {
    "none": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE",
    "fast": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST",
}
BASE_FLAGS = ["-O2", "-std=c++20", "-stdlib=libc++",
              "-Rpass=loop-vectorize", "-Rpass-missed=loop-vectorize", "-Rpass-analysis=loop-vectorize",
              "-fsave-optimization-record", "-foptimization-record-passes=loop-vectorize"]
TARGETS = {"baseline": [], "avx2": ["-march=x86-64-v3"]}
TARGET_NAMES = {"baseline": "x86-64 baseline (no -march)", "avx2": "x86-64-v3 (-march=x86-64-v3, AVX2)"}
TARGET = "baseline"  # set by main(); compile_cmd() adds TARGETS[TARGET]

KERNELS = {
    "name": "kernels", "kind": "control (this project's 8 kernels)", "version": "repo",
    "repo": "kernels/", "commit": "", "downloads": [], "root": "",
    "sources": ["k0*.cpp"], "exclude": [], "includes": ["."], "defines": [],
}
# What the kernel control must show (docs/SPEC.md; confirmed by the measured remarks and assembly).
KERNEL_EXPECT = {
    "k01_sum_fwd": "both", "k02_add_fwd": "both", "k03_stencil": "both",
    "k04_rev": "lost", "k05_stride2": "lost", "k06_gather": "neither", "k07_hist": "neither",
    "k08_matmul": "lost",
}
KERNEL_EXPECT_CLASS = {"k04_rev": "reverse", "k05_stride2": "strided", "k08_matmul": "strided"}
# At -march=x86-64-v3 the gather kernels may vectorize under NONE (AVX2 has gathers), so k06 and k07
# may be "neither" or "lost" (corpus/PLAN2.md, Controls).
KERNEL_EXPECT_AVX2 = {k: ({"neither", "lost"} if k in ("k06_gather", "k07_hist") else {v})
                      for k, v in KERNEL_EXPECT.items()}

LIMITS = [
    "Compile-time counts only: a lost loop is only potentially expensive. How often it runs (its "
    "hotness) is unknown at compile time, so no runtime cost is claimed from this census.",
    "Every vectorized loop counts once per function it was compiled into: a header loop inlined into "
    "three functions counts three times. Unique source locations are reported beside the counts.",
    "One toolchain and target: clang 18 with libc++ 18 (Ubuntu noble), -O2, baseline x86-64 (SSE2), "
    "FAST mode only. Other compilers, -march levels and the extensive mode are not covered.",
    "Header-only libraries are measured through a small driver that instantiates common operations; "
    "loops the driver does not instantiate are not counted.",
    "The classification of why a loop lost SIMD is a regular-expression heuristic over the source "
    "text, not a proof; each lost loop is listed with its line so the call can be checked.",
    "libc++ 18 spells the hardening mode into the ABI tag of its inline functions ([abi:ne180100] "
    "under NONE, [abi:fe180100] under FAST); FAST names are mapped to the NONE spelling before matching.",
    "A loop vectorized in NONE whose function is not inlined the same way in FAST can move: it is "
    "counted as moved (not lost) when the same source location gains a vectorized copy in another "
    "function of the same file.",
]


# ---------------------------------------------------------------- projects and fetch

def load_projects(only=None, file="projects.json", shard=0):
    with open(os.path.join(HERE, file), encoding="utf-8") as f:
        projects = json.load(f)["projects"]
    if only:
        names = set(only)
        projects = [p for p in projects if p["name"] in names]
    if shard:
        projects = [p for p in projects if p.get("shard", 1) == shard]
    return projects


def project_root(p, deps):
    if p["name"] == "kernels":
        return os.path.join(REPO, "kernels")
    return os.path.join(deps, "src", p["root"])


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(projects, deps):
    """Download, check, unpack. Any sha256 mismatch raises before anything is unpacked."""
    dl = os.path.join(deps, "dl")
    src = os.path.join(deps, "src")
    os.makedirs(dl, exist_ok=True)
    os.makedirs(src, exist_ok=True)
    manifest = []
    for p in projects:
        for d in p["downloads"]:
            path = os.path.join(dl, d["file"])
            if not os.path.exists(path) or sha256_file(path) != d["sha256"]:
                req = urllib.request.Request(d["url"], headers={"User-Agent": "corpus-census"})
                with urllib.request.urlopen(req, timeout=120) as r, open(path + ".part", "wb") as out:
                    shutil.copyfileobj(r, out)
                os.replace(path + ".part", path)
            got = sha256_file(path)
            if got != d["sha256"]:
                raise SystemExit("sha256 mismatch for %s: expected %s, got %s" % (d["url"], d["sha256"], got))
            size = os.path.getsize(path)
            manifest.append("%s  %d  %s  %s" % (got, size, d["file"], d["url"]))
            if "dest" in d:
                dest = os.path.join(src, d["dest"])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copyfile(path, dest)
            else:
                with tarfile.open(path, "r:gz") as t:
                    t.extractall(src, filter="data") if hasattr(tarfile, "data_filter") else t.extractall(src)
        root = project_root(p, deps)
        if p.get("driver"):
            ddir = os.path.join(root, "_census_driver")
            os.makedirs(ddir, exist_ok=True)
            shutil.copyfile(os.path.join(HERE, "drivers", p["driver"]), os.path.join(ddir, p["driver"]))
        for out_rel, spec in sorted(p.get("generate", {}).items()):
            if "content" in spec:
                text = spec["content"]
            else:
                with open(os.path.join(root, spec["from"]), encoding="utf-8") as f:
                    text = f.read()
            for k, v in spec.get("replace", {}).items():
                text = text.replace(k, v)
            ones = spec.get("cmakedefine01", {})
            text = re.sub(r"#cmakedefine01 (\w+)",
                          lambda m: "#define %s %d" % (m.group(1), int(ones.get(m.group(1), 0))), text)
            if "cmakedefine" in spec:
                on = spec["cmakedefine"]
                text = re.sub(r"#cmakedefine (\w+)[^\n]*",
                              lambda m: ("#define %s" % m.group(1)) if on.get(m.group(1)) else
                              ("/* #undef %s */" % m.group(1)), text)
            out = os.path.join(root, out_rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
    with open(os.path.join(deps, "MANIFEST"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(manifest) + "\n")
    return manifest


# ---------------------------------------------------------------- build

def translation_units(p, root):
    tus = set()
    for pat in p["sources"]:
        for path in glob.glob(os.path.join(root, pat), recursive=True):
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if not any(fnmatch.fnmatch(rel, ex) for ex in p["exclude"]):
                tus.add(rel)
    if p.get("driver"):
        tus.add("_census_driver/" + p["driver"])
    return sorted(tus)


def obj_name(tu):
    return tu.replace("/", "__") + ".o"


def compile_cmd(p, tu, mode, obj, record):
    flags = [("-std=" + p["std"]) if f == "-std=c++20" and p.get("std") else f for f in BASE_FLAGS]
    cmd = [CXX] + flags + TARGETS[TARGET] + [MODES[mode], "-foptimization-record-file=" + record]
    cmd += ["-I" + i for i in p["includes"]] + ["-D" + d for d in p["defines"]]
    cmd += ["-c", tu, "-o", obj]
    return cmd


def build(projects, deps, work, jobs):
    tasks = []
    for p in projects:
        root = project_root(p, deps)
        for mode in MODES:
            os.makedirs(os.path.join(work, p["name"], mode), exist_ok=True)
        for tu in translation_units(p, root):
            for mode in MODES:
                base = os.path.join(work, p["name"], mode, obj_name(tu))
                tasks.append((p, root, tu, mode, base))

    def one(task):
        p, root, tu, mode, base = task
        obj = os.path.abspath(base)
        rec = obj[:-2] + ".opt.yaml"
        r = subprocess.run(compile_cmd(p, tu, mode, obj, rec), cwd=root, capture_output=True, text=True,
                           errors="replace", timeout=600)
        with open(obj[:-2] + ".stderr.txt", "w", encoding="utf-8", newline="\n") as f:
            f.write(r.stderr)
        with open(obj[:-2] + ".rc", "w") as f:
            f.write(str(r.returncode))
        return p["name"], tu, mode, r.returncode

    failed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for name, tu, mode, rc in ex.map(one, tasks):
            if rc != 0:
                failed.append((name, tu, mode))
    for name, tu, mode in sorted(failed):
        print("FAILED %s %s %s" % (name, mode, tu), file=sys.stderr)
    return failed


# ---------------------------------------------------------------- analyze

def norm_file(path, root):
    """A loop's file as a stable name and its origin: project-relative, 'libc++/<header>', or a
    system path."""
    p = path.replace("\\", "/")
    if "/include/c++/v1/" in p:
        return "libc++/" + p.split("/include/c++/v1/", 1)[1], "libc++"
    if os.path.isabs(p) or p.startswith("/"):
        rp = os.path.normpath(p).replace("\\", "/")
        rr = os.path.normpath(root).replace("\\", "/") + "/"
        if rp.startswith(rr):
            p = rp[len(rr):]
        else:
            return rp, "system"
    p = os.path.normpath(p).replace("\\", "/")
    return p, ("driver" if p.startswith("_census_driver/") else "project")


def source_path(file, origin, root):
    if origin == "libc++":
        return LIBCXX_DIR + file[len("libc++/"):]
    if origin == "system":
        return file
    return os.path.join(root, file)


_LINES = {}


def source_lines(path):
    if path not in _LINES:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                _LINES[path] = f.read().splitlines()
        except OSError:
            _LINES[path] = []
    return _LINES[path]


def clip(s, n=200):
    s = s.rstrip()
    return s if len(s) <= n else s[:n - 3] + "..."


def demangle(names):
    names = sorted(set(n for n in names if n))
    if not names:
        return {}
    try:
        r = subprocess.run([CXXFILT], input="\n".join(names) + "\n", capture_output=True, text=True, check=True)
        out = r.stdout.splitlines()
        if len(out) == len(names):
            return dict(zip(names, out))
    except (OSError, subprocess.CalledProcessError):
        pass
    return {n: n for n in names}


def objdump_stats(obj):
    """(ud2 count, .text* bytes) of one object file."""
    d = subprocess.run([OBJDUMP, "-d", "--no-show-raw-insn", obj], capture_output=True, text=True, check=True).stdout
    ud2 = sum(1 for ln in d.splitlines() if re.search(r":\s+ud2\b", ln))
    h = subprocess.run([OBJDUMP, "-h", obj], capture_output=True, text=True, check=True).stdout
    text = 0
    for ln in h.splitlines():
        f = ln.split()
        if len(f) >= 3 and f[0].isdigit() and f[1].startswith(".text"):
            text += int(f[2], 16)
    return ud2, text


# ---------------------------------------------------------------- index evidence (traps traced to source)

EVIDENCE = True  # rebuild lost loops' translation units with line tables and trace their checks
EVIDENCE_DIR = os.path.join(HERE, "evidence")  # holds the <__assertion_handler> of the evidence rebuild
TRAP_SYMBOL = "__census_trap"
SYMBOLIZER = os.environ.get("CENSUS_SYMBOLIZER", "llvm-symbolizer-18")
_PLAIN_INSN = re.compile(r"^\s+([0-9a-f]+):\s+([a-z][\w.]*)\s*(.*)$")


def parse_objdump_checks(text):
    """`objdump -d --no-show-raw-insn` of a linked file -> {symbol: [address of each check]}: a call
    or jump to TRAP_SYMBOL (through its PLT entry), or a ud2."""
    out, sym = {}, None
    for ln in text.splitlines():
        m = _SYM.match(ln)
        if m:
            sym = m.group(1)
            out.setdefault(sym, [])
            continue
        m = _PLAIN_INSN.match(ln)
        if m and sym is not None:
            mn, rest = m.group(2), m.group(3)
            if mn == "ud2" or (mn.startswith(("call", "jmp")) and "<" + TRAP_SYMBOL in rest):
                out[sym].append(int(m.group(1), 16))
    return out


def parse_symbolizer(text):
    """`llvm-symbolizer --inlining` output (blocks of function / file:line:column lines, one block
    per address, blank line between) -> [chain], chain = ((file, line), ...) innermost first."""
    chains = []
    for block in text.replace("\r", "").split("\n\n"):
        lines = [x for x in block.split("\n") if x.strip()]
        chain = []
        for loc in lines[1::2]:
            m = re.match(r"^(.*):(\d+):(\d+)$", loc.strip()) or re.match(r"^(.*):(\d+)$", loc.strip())
            if m and m.group(1) not in ("??", ""):
                chain.append((m.group(1), int(m.group(2))))
        if lines:
            chains.append(tuple(chain))
    return chains
_SYM = re.compile(r"^[0-9a-f]+ <(.+)>:\s*$")
_LOCLINE = re.compile(r"^(/[^:]*|[^\s<:][^:]*):(\d+)(?: \(discriminator \d+\))?\s*$")
_INLINED = re.compile(r"^inlined by (.+?):(\d+)(?:\s.*)?$")
_INSN = re.compile(r"^\s+([0-9a-f]+):\s+([a-z][\w.]*)")
_RELOC = re.compile(r"^\s+[0-9a-f]+:\s+R_[A-Z0-9_]+\s+(\S+)")
_ASSERT = re.compile(r"_LIBCPP_ASSERT\w*\s*\(")
_STRLIT = re.compile(r'"((?:[^"\\]|\\.)*)"')


def parse_objdump_lines(text):
    """`objdump -d -r -l --inlines --no-show-raw-insn` output -> {symbol: [(mnemonic, chain)]}, where
    chain is the source location of the instruction as [(file, line), ...], innermost first (the
    location line, then each `inlined by` line). A call or jump whose relocation names TRAP_SYMBOL
    is reported with the mnemonic "check"."""
    out, sym, chain = {}, None, []
    for ln in text.splitlines():
        m = _SYM.match(ln)
        if m:
            sym, chain = m.group(1), []
            out.setdefault(sym, [])
            continue
        if sym is None or not ln.strip():
            continue
        m = _INLINED.match(ln)
        if m:
            chain = chain + [(m.group(1), int(m.group(2)))]
            continue
        m = _RELOC.match(ln)
        if m:
            if re.split(r"[-+]", m.group(1))[0] == TRAP_SYMBOL and out[sym]:
                out[sym][-1] = ("check", out[sym][-1][1])
            continue
        m = _INSN.match(ln)
        if m:
            out[sym].append((m.group(2), tuple(chain)))
            continue
        if ln.rstrip().endswith("():"):
            continue
        m = _LOCLINE.match(ln)
        if m:
            chain = [(m.group(1), int(m.group(2)))]
    return out


def libcxx_assertion(lines, line):
    """The message of the libc++ assertion at (or just above) 1-based `line` of a libc++ header, or
    None: e.g. 'vector[] index out of bounds'."""
    for j in range(line - 1, max(-1, line - 5), -1):
        if 0 <= j < len(lines) and _ASSERT.search(lines[j]):
            for k in (j, j + 1, j + 2):
                if k < len(lines):
                    lits = _STRLIT.findall(lines[k])
                    if lits:
                        return lits[-1]
            return "(assertion without a message)"
    return None


CONTAINERS = (("string_view", "std::string_view"), ("span", "std::span"), ("array", "std::array"),
              ("vector", "std::vector"), ("deque", "std::deque"), ("string", "std::basic_string"),
              ("optional", "std::optional"), ("mdspan", "std::mdspan"))


def container_of(message):
    low = message.lower()
    for key, name in CONTAINERS:
        if key in low:
            return name
    return "other libc++ check"


def trap_chains(dump, function):
    """The inline chains of every check (a call to TRAP_SYMBOL, or a ud2) in the symbol whose
    normalized name is `function`."""
    chains = []
    for sym, insns in dump.items():
        if norm_function(sym) == function:
            chains += [c for mn, c in insns if mn in ("check", "ud2")]
    return chains


def evidence_for(entry, chains, root, still_lost):
    """Whether a lost loop indexes a checked libc++ container: a trap whose chain has a libc++
    assertion frame and a frame inside the loop's source lines (corpus/PLAN2.md, Metrics)."""
    src = source_lines(source_path(entry["file"], entry["origin"], root))
    idx = entry["line"] - 1
    body = classify.loop_context(src, idx, max_lines=80) if 0 <= idx < len(src) else []
    lo, hi = entry["line"], entry["line"] + max(0, len(body) - 1)
    attributed, others = [], []
    for chain in chains:
        frames = [norm_file(f, root) + (ln,) for f, ln in chain]  # (file, origin, line)
        msg = None
        for f, origin, ln in frames:
            if origin == "libc++":
                msg = libcxx_assertion(source_lines(source_path(f, origin, root)), ln)
                if msg:
                    break
        in_loop = any(f == entry["file"] and lo <= ln <= hi for f, _, ln in frames)
        where = ["%s:%d" % (f, ln) for f, _, ln in frames]
        if msg and in_loop:
            attributed.append({"message": msg, "chain": where})
        else:
            others.append({"message": msg or "", "chain": where[:4]})
    msgs = sorted({a["message"] for a in attributed})
    return {
        "status": "checked container access in the loop" if attributed else "no trap attributed to this loop",
        "messages": msgs,
        "containers": sorted({container_of(m) for m in msgs}),
        "attributed_traps": len(attributed),
        "traps_in_function": len(chains),
        "loop_lines": [lo, hi],
        "example_chain": attributed[0]["chain"] if attributed else [],
        "other_traps": sorted(others, key=lambda o: (o["message"], o["chain"]))[:5],
        "evidence_build_loop_not_vectorized": still_lost,
        "method": "FAST rebuilt with -gline-tables-only and corpus/evidence/__assertion_handler (each libc++ "
                  "check a separate, never-merged call), linked without libraries, every check in the loop's "
                  "function located with objdump and traced with llvm-symbolizer --inlining; a check counts "
                  "when its chain has a libc++ assertion frame and a frame within the loop's source lines",
    }


def index_evidence(p, root, work, entries):
    """Adds "index_evidence" to each lost entry (in place). One rebuild per translation unit."""
    by_tu = collections.defaultdict(list)
    for e in entries:
        by_tu[e["tu"]].append(e)
    for tu, es in sorted(by_tu.items()):
        gdir = os.path.join(work, p["name"], "fast-g")
        os.makedirs(gdir, exist_ok=True)
        obj = os.path.abspath(os.path.join(gdir, obj_name(tu)))
        rec = obj[:-2] + ".opt.yaml"
        cmd = compile_cmd(p, tu, "fast", obj, rec)
        cmd[-4:-4] = ["-gline-tables-only", "-I" + EVIDENCE_DIR]
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, errors="replace", timeout=900)
        if r.returncode != 0:
            err = " | ".join([x for x in r.stderr.splitlines() if "error" in x][:2])
            for e in es:
                e["index_evidence"] = {"status": "evidence rebuild failed", "messages": [], "containers": [],
                                       "attributed_traps": 0, "traps_in_function": 0, "error": clip(err, 300)}
            continue
        vec = set()
        with open(rec, encoding="utf-8", errors="replace") as f:
            for x in optrecord.loop_vectorize(optrecord.parse(f.read())):
                if optrecord.is_vectorized(x) and x["loc"]:
                    vec.add((norm_function(x["function"]), norm_file(x["loc"]["file"], root)[0],
                             x["loc"]["line"], x["loc"]["column"]))
        # Link the object (nothing resolved, nothing run) so every section has its own address, then
        # find each check's address with objdump and its inline chain with llvm-symbolizer.
        elf = obj[:-2] + ".elf"
        lk = subprocess.run([CXX, "-fuse-ld=bfd", "-pie", "-nostdlib", "-Wl,--unresolved-symbols=ignore-all",
                             "-Wl,-e,0", "-o", elf, obj], capture_output=True, text=True, errors="replace")
        chains_by_sym = {}
        if lk.returncode == 0:
            d = subprocess.run([OBJDUMP, "-d", "--no-show-raw-insn", elf],
                               capture_output=True, text=True, errors="replace", check=True).stdout
            checks = parse_objdump_checks(d)
            addrs = sorted({a for v in checks.values() for a in v})
            sy = subprocess.run([SYMBOLIZER, "--obj=" + elf, "--inlining", "--functions=linkage"],
                                input="".join("0x%x\n" % a for a in addrs), capture_output=True, text=True,
                                errors="replace")
            got = dict(zip(addrs, parse_symbolizer(sy.stdout))) if sy.returncode == 0 else {}
            for sym, v in checks.items():
                chains_by_sym[sym] = [got.get(a, ()) for a in v]
            how = "linked; objdump + llvm-symbolizer (%d checks in the file, %d traced)" % (
                len(addrs), sum(1 for a in addrs if got.get(a)))
        else:
            d = subprocess.run([OBJDUMP, "-d", "-r", "-l", "--inlines", "--no-show-raw-insn", obj],
                               capture_output=True, text=True, errors="replace", check=True).stdout
            for sym, insns in parse_objdump_lines(d).items():
                chains_by_sym[sym] = [c for mn, c in insns if mn in ("check", "ud2")]
            how = "link failed (%s); objdump -l --inlines on the object" % clip(
                " | ".join([x for x in lk.stderr.splitlines() if x.strip()][:2]), 300)
        for e in es:
            still = (e["function"], e["file"], e["line"], e["column"]) not in vec
            chains = [c for sym, cs in chains_by_sym.items() if norm_function(sym) == e["function"] for c in cs]
            e["index_evidence"] = evidence_for(e, chains, root, still)
            e["index_evidence"]["tracing"] = how


_ABI_TAG = re.compile(r"B8[nfsd]([en]\d{6})")


def norm_function(mangled):
    """libc++ 18 writes the hardening mode into the ABI tag of its inline functions
    ([abi:ne180100] with NONE, [abi:fe180100] with FAST), so the same function has two names.
    FAST's spelling is mapped to NONE's before loops are matched."""
    return _ABI_TAG.sub(lambda m: "B8n" + m.group(1), mangled)


def read_tu(work, name, mode, tu, root):
    base = os.path.join(work, name, mode, obj_name(tu))[:-2]
    with open(base + ".opt.yaml", encoding="utf-8", errors="replace") as f:
        recs = optrecord.loop_vectorize(optrecord.parse(f.read()))
    with open(base + ".stderr.txt", encoding="utf-8", errors="replace") as f:
        stderr = f.read()
    vec = collections.Counter()
    msgs = collections.defaultdict(set)
    vmsg = {}
    for r in recs:
        loc = r["loc"] or {"file": "?", "line": 0, "column": 0}
        file, origin = norm_file(loc["file"], root)
        key = (norm_function(r["function"]), file, loc["line"], loc["column"], origin)
        if optrecord.is_vectorized(r):
            vec[key] += 1
            vmsg[key] = r["message"]
        else:
            msgs[key].add(r["message"])
    stderr_vec = sum(1 for ln in stderr.splitlines() if "remark: vectorized loop" in ln)
    return vec, msgs, vmsg, stderr_vec


def analyze_project(p, deps, work):
    root = project_root(p, deps)
    tus = translation_units(p, root)
    failed, ok = [], []
    for tu in tus:
        rcs = {}
        for mode in MODES:
            path = os.path.join(work, p["name"], mode, obj_name(tu))[:-2] + ".rc"
            rcs[mode] = open(path).read().strip() if os.path.exists(path) else "missing"
        if all(v == "0" for v in rcs.values()):
            ok.append(tu)
        else:
            err = ""
            for mode in MODES:
                sp = os.path.join(work, p["name"], mode, obj_name(tu))[:-2] + ".stderr.txt"
                if rcs[mode] != "0" and os.path.exists(sp):
                    lines = [x for x in open(sp, encoding="utf-8", errors="replace").read().splitlines() if "error" in x]
                    err = " | ".join(lines[:3])
                    break
            failed.append({"tu": tu, "error": clip(err, 400)})

    stats = {m: {"vectorized": 0, "vectorized_unique": set(), "loops_reported": 0, "ud2": 0, "text_bytes": 0,
                 "stderr_vectorized": 0, "vectorized_by_origin": {o: 0 for o in ORIGINS}} for m in MODES}
    lost, moved, gained = [], [], []
    for tu in ok:
        data = {m: read_tu(work, p["name"], m, tu, root) for m in MODES}
        for m in MODES:
            vec, msgs, _, sv = data[m]
            st = stats[m]
            st["vectorized"] += sum(vec.values())
            for k, c in vec.items():
                st["vectorized_by_origin"][k[4]] += c
            st["vectorized_unique"].update((k[1], k[2], k[3]) for k in vec)
            st["loops_reported"] += len(set(vec) | set(msgs))
            st["stderr_vectorized"] += sv
            u, t = objdump_stats(os.path.join(work, p["name"], m, obj_name(tu)))
            st["ud2"] += u
            st["text_bytes"] += t
        vn, mn, vmn, _ = data["none"]
        vf, mf, _, _ = data["fast"]
        loc_n, loc_f = collections.Counter(), collections.Counter()
        for k, c in vn.items():
            loc_n[k[1:4]] += c
        for k, c in vf.items():
            loc_f[k[1:4]] += c
        budget = {loc: max(0, loc_n[loc] - loc_f[loc]) for loc in loc_n}  # net loss per source location
        for key in sorted(set(vn) | set(vf)):
            n, f = vn.get(key, 0), vf.get(key, 0)
            func, file, line, col, origin = key
            entry = {"project": p["name"], "tu": tu, "function": func, "file": file, "line": line,
                     "column": col, "origin": origin}
            if n > f:
                k_lost = min(n - f, budget[key[1:4]])
                budget[key[1:4]] -= k_lost
                entry.update({"none_remark": vmn.get(key, ""), "fast_remarks": sorted(mf.get(key, set()))})
                if k_lost:
                    lost.append(dict(entry, count=k_lost))
                if n - f - k_lost:
                    moved.append(dict(entry, count=n - f - k_lost))
            elif f > n:
                gained.append(dict(entry, count=f - n, none_remarks=sorted(mn.get(key, set()))))
    for st in stats.values():
        st["vectorized_unique"] = len(st["vectorized_unique"])

    for e in lost + moved + gained:
        lines = source_lines(source_path(e["file"], e["origin"], root))
        idx = e["line"] - 1
        ctx = classify.loop_context(lines, idx) if 0 <= idx < len(lines) else []
        e["source_line"] = clip(ctx[0].strip()) if ctx else ""
        e["context"] = [clip(x) for x in ctx]
        cls, detail = classify.classify(ctx, e["column"], e["origin"], " | ".join(e.get("fast_remarks", [])))
        e["class"], e["detail"] = cls, detail
    for e in lost:
        e["trip_count"] = classify.trip_count(e["context"], e["column"])
    if EVIDENCE and lost:
        index_evidence(p, root, work, lost)

    n_lost = sum(e["count"] for e in lost)
    summary = {
        "name": p["name"], "category": p.get("category", ""), "kind": p["kind"], "version": p["version"],
        "repo": p["repo"], "commit": p["commit"],
        "downloads": [{"url": d["url"], "sha256": d["sha256"], "bytes": d["bytes"]} for d in p["downloads"]],
        "translation_units": len(tus), "compiled": len(ok), "failed": failed,
        "example_command": " ".join(compile_cmd(p, tus[0], "fast", "OUT.o", "OUT.opt.yaml")) if tus else "",
        "none": stats["none"], "fast": stats["fast"],
        "lost": n_lost,
        "moved": sum(e["count"] for e in moved),
        "gained": sum(e["count"] for e in gained),
        "lost_pct_of_vectorized": pct(n_lost, stats["none"]["vectorized"]),
        "ud2_added": stats["fast"]["ud2"] - stats["none"]["ud2"],
        "text_bytes_change_pct": pct(stats["fast"]["text_bytes"] - stats["none"]["text_bytes"],
                                     stats["none"]["text_bytes"]),
        "lost_by_class": count_by(lost, "class", classify.CLASSES),
        "lost_by_origin": count_by(lost, "origin", ORIGINS),
        "lost_with_index_evidence": sum(e["count"] for e in lost if e.get("index_evidence", {}).get(
            "status") == "checked container access in the loop"),
    }
    return summary, lost, moved, gained


def pct(a, b):
    return round(100.0 * a / b, 3) if b else None


def count_by(entries, field, keys):
    c = {k: 0 for k in keys}
    for e in entries:
        c[e[field]] = c.get(e[field], 0) + e["count"]
    return c


def patterns(lost, top=5):
    groups = collections.defaultdict(list)
    for e in lost:
        groups[(e["class"], e["detail"])].append(e)
    ranked = sorted(groups.items(), key=lambda kv: (-sum(e["count"] for e in kv[1]), kv[0]))
    out = []
    for (cls, detail), es in ranked[:top]:
        examples, seen_proj, seen = [], set(), set()
        for pass_ in (0, 1):
            for e in sorted(es, key=lambda e: (e["project"], e["file"], e["line"])):
                where = "%s:%d" % (e["file"], e["line"])
                if (e["project"], where) in seen or (pass_ == 0 and e["project"] in seen_proj):
                    continue
                if len(examples) >= 3:
                    break
                examples.append({"project": e["project"], "where": where, "source_line": e["source_line"]})
                seen.add((e["project"], where))
                seen_proj.add(e["project"])
        out.append({"class": cls, "detail": detail, "count": sum(e["count"] for e in es),
                    "unique_locations": len({(e["project"], e["file"], e["line"], e["column"]) for e in es}),
                    "examples": examples})
    return out


def kernel_control(lost, moved, gained, deps, work):
    """For each kernel, the status of its `// LOOP` line in its kern_ function: both / lost / gained /
    neither. Pass when it equals KERNEL_EXPECT and the lost ones carry KERNEL_EXPECT_CLASS."""
    p = KERNELS
    root = project_root(p, deps)
    rows, ok, evidence_rows = [], True, []
    for tu in translation_units(p, root):
        kid = tu[:-4]
        line = next(i for i, t in enumerate(source_lines(os.path.join(root, tu)), 1) if "// LOOP" in t)
        data = {m: read_tu(work, "kernels", m, tu, root) for m in MODES}
        names = demangle(k[0] for m in MODES for k in data[m][0])

        def vec_at(m):
            return sum(c for k, c in data[m][0].items()
                       if k[1] == tu and k[2] == line and names.get(k[0], k[0]).startswith("kern_" + kid))
        n, f = vec_at("none"), vec_at("fast")
        status = "both" if n and f else "lost" if n and not f else "gained" if f else "neither"
        entry = next((e for e in lost if e["tu"] == tu and e["line"] == line), None)
        cls = entry["class"] if entry else None
        exp = KERNEL_EXPECT.get(kid)
        allowed = KERNEL_EXPECT_AVX2.get(kid, set()) if TARGET == "avx2" else {exp}
        exp_cls = KERNEL_EXPECT_CLASS.get(kid, "indirect")
        good = status in allowed and (status != "lost" or cls == exp_cls)
        ok = ok and good
        ev = (entry or {}).get("index_evidence")
        if status == "lost":
            ev_ok = bool(ev) and ev.get("status") == "checked container access in the loop" \
                and "std::vector" in ev.get("containers", [])
            evidence_rows.append({"kernel": kid, "pass": ev_ok,
                                  "status": ev.get("status") if ev else "not computed",
                                  "messages": ev.get("messages", []) if ev else [],
                                  "example_chain": ev.get("example_chain", []) if ev else [],
                                  "evidence_build_loop_not_vectorized":
                                      ev.get("evidence_build_loop_not_vectorized") if ev else None})
        fast_msgs = set()
        for k, v in data["fast"][1].items():
            if k[1] == tu and k[2] == line:
                fast_msgs |= v
        fast_msgs = sorted(fast_msgs)
        rows.append({"kernel": kid, "loop_line": line, "none_vectorized": n, "fast_vectorized": f,
                     "status": status, "expected": exp, "class": cls,
                     "expected_class": KERNEL_EXPECT_CLASS.get(kid), "fast_remarks": fast_msgs, "pass": good})
    lost_set = sorted(r["kernel"] for r in rows if r["status"] == "lost")
    others = [{"tu": e["tu"], "line": e["line"], "function": e["function"]} for e in lost
              if not any(e["tu"] == r["kernel"] + ".cpp" and e["line"] == r["loop_line"] for r in rows)]
    core = {"k04_rev", "k05_stride2", "k08_matmul"}
    if TARGET == "avx2":
        set_ok = core <= set(lost_set) <= core | {"k06_gather", "k07_hist"}
        rule = ("avx2: k01 to k03 vectorized in both builds; k04_rev, k05_stride2, k08_matmul LOST at their "
                "// LOOP line (reverse, strided, strided); k06_gather and k07_hist either in neither build or "
                "LOST (class indirect), reported as found")
    else:
        set_ok = lost_set == sorted(core)
        rule = ("exactly k04_rev, k05_stride2, k08_matmul LOST at their // LOOP line (classes reverse, "
                "strided, strided); k06_gather and k07_hist vectorized in neither build; k01 to k03 in both")
    out = {"pass": ok and set_ok, "target": TARGET,
           "lost_kernels": lost_set, "kernels": rows,
           "other_lost_loops_in_kernel_files": others, "rule": rule}
    if EVIDENCE:
        out["index_evidence"] = {
            "rule": "every lost kernel loop shows a std::vector operator[] check within its loop lines",
            "pass": bool(evidence_rows) and all(r["pass"] for r in evidence_rows), "kernels": evidence_rows}
    return out


def tool_versions():
    out = {}
    try:
        out["clang"] = subprocess.run([CXX, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    except (OSError, IndexError):
        out["clang"] = "unknown"
    try:
        r = subprocess.run(["dpkg-query", "-W", "-f", "${Package} ${Version}\n", "clang-18", "libc++-18-dev",
                            "libc++abi-18-dev", "binutils", "llvm-18"], capture_output=True, text=True)
        out["packages"] = sorted(r.stdout.splitlines())
    except OSError:
        out["packages"] = []
    return out


def deterministic_targz(path, files):
    """A .tar.gz whose bytes depend only on the files' names and contents."""
    items = []
    for arc, src in sorted(files):
        with open(src, "rb") as f:
            items.append((arc, f.read()))
    deterministic_targz_bytes(path, items)


def deterministic_targz_bytes(path, items):
    """deterministic_targz() from (name, bytes) pairs."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as t:
        for arc, data in sorted(items):
            ti = tarfile.TarInfo(arc)
            ti.size, ti.mtime, ti.mode, ti.uid, ti.gid, ti.uname, ti.gname = len(data), 0, 0o644, 0, 0, "", ""
            t.addfile(ti, io.BytesIO(data))
    with open(path, "wb") as f:
        with gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0, compresslevel=9) as g:
            g.write(buf.getvalue())


def make_totals(included, lost_inc):
    """The totals over the included projects' summaries (also used by merge.py)."""
    tot = {m: {k: sum(s[m][k] for s in included) for k in ("vectorized", "vectorized_unique", "loops_reported",
                                                            "ud2", "text_bytes", "stderr_vectorized")}
           for m in MODES}
    for m in MODES:
        tot[m]["vectorized_by_origin"] = {o: sum(s[m]["vectorized_by_origin"][o] for s in included) for o in ORIGINS}
    n_lost = sum(e["count"] for e in lost_inc)
    totals = {
        "projects": len(included),
        "translation_units": sum(s["compiled"] for s in included),
        "none": tot["none"], "fast": tot["fast"],
        "lost": n_lost,
        "lost_unique_locations": len({(e["project"], e["file"], e["line"], e["column"]) for e in lost_inc}),
        "moved": sum(s["moved"] for s in included), "gained": sum(s["gained"] for s in included),
        "lost_pct_of_vectorized": pct(n_lost, tot["none"]["vectorized"]),
        "ud2_added": tot["fast"]["ud2"] - tot["none"]["ud2"],
        "text_bytes_change_pct": pct(tot["fast"]["text_bytes"] - tot["none"]["text_bytes"], tot["none"]["text_bytes"]),
        "lost_by_class": count_by(lost_inc, "class", classify.CLASSES),
        "lost_by_origin": count_by(lost_inc, "origin", ORIGINS),
        "projects_with_a_lost_loop": sum(1 for s in included if s["lost"] > 0),
        "lost_with_index_evidence": sum(e["count"] for e in lost_inc if e.get("index_evidence", {}).get(
            "status") == "checked container access in the loop"),
    }
    return totals


def is_included(s):
    return s["compiled"] > 0 and not s["failed"]


def dropped_entry(s):
    return {"name": s["name"], "reason": "translation units failed: " + "; ".join(
        f["tu"] + ": " + f["error"] for f in s["failed"][:3])}


def analyze(projects, deps, work, out, projects_file="projects.json", shard=0):
    os.makedirs(out, exist_ok=True)
    summaries, all_lost, all_moved, all_gained = [], [], [], []
    for p in projects:
        s, lost, moved, gained = analyze_project(p, deps, work)
        summaries.append(s)
        all_lost += lost
        all_moved += moved
        all_gained += gained
    ks, klost, kmoved, kgained = analyze_project(KERNELS, deps, work)

    names = demangle(e["function"] for e in all_lost + all_moved + all_gained + klost)
    for e in all_lost + all_moved + all_gained + klost:
        e["function_name"] = clip(names.get(e["function"], e["function"]), 300)

    included = [s for s in summaries if is_included(s)]
    lost_inc = [e for e in all_lost if e["project"] in {s["name"] for s in included}]
    totals = make_totals(included, lost_inc)
    crosscheck = {s["name"]: {m: [s[m]["vectorized"], s[m]["stderr_vectorized"]] for m in MODES}
                  for s in summaries + [ks]}
    census = {
        "schema": "corpus-2",
        "what": "Compile-time census: loops clang 18 vectorizes with libc++ hardening NONE and not with FAST.",
        "projects_file": projects_file, "shards": [shard] if shard else [],
        "target": TARGET,
        "toolchain": dict(tool_versions(), flags=BASE_FLAGS + TARGETS[TARGET], modes=MODES,
                          target=TARGET_NAMES[TARGET]),
        "source": {"repo_sha": os.environ.get("GITHUB_SHA", ""), "run_id": os.environ.get("GITHUB_RUN_ID", "")},
        "projects": summaries,
        "dropped": [dropped_entry(s) for s in summaries if s not in included],
        "totals": totals,
        "patterns": patterns(lost_inc),
        "controls": {
            "kernels": kernel_control(klost, kmoved, kgained, deps, work),
            "remark_crosscheck": {"rule": "vectorized records in the YAML == 'vectorized loop' remarks on stderr",
                                  "pass": all(v[m][0] == v[m][1] for v in crosscheck.values() for m in MODES),
                                  "per_project": crosscheck},
        },
        "limits": LIMITS,
    }
    with open(os.path.join(out, "census.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(census, f, indent=1, sort_keys=False)
        f.write("\n")
    with open(os.path.join(out, "lost_loops.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"schema": "corpus-lost-2",
                   "note": "lost: vectorized in NONE, not in FAST, at the same file:line:column in the same "
                           "function of the same translation unit. moved: such a loop whose source location "
                           "gained a vectorized copy in another function of the same file. gained: the reverse. "
                           "Each lost loop carries trip_count (a heuristic from its header) and index_evidence "
                           "(its traps traced to source; corpus/PLAN2.md).",
                   "lost": all_lost, "moved": all_moved, "gained": all_gained, "kernels_lost": klost},
                  f, indent=1)
        f.write("\n")
    # Hashes of every object, record and stderr file, for the determinism control.
    files = []
    for name in [p["name"] for p in projects] + ["kernels"]:
        for mode in MODES:
            d = os.path.join(work, name, mode)
            for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                if fn.endswith((".o", ".opt.yaml", ".stderr.txt")):
                    files.append(("%s/%s/%s" % (name, mode, fn), os.path.join(d, fn)))
    with open(os.path.join(out, "objects.sha256"), "w", encoding="utf-8", newline="\n") as f:
        for arc, src in files:
            f.write("%s  %s\n" % (sha256_file(src), arc))
    deterministic_targz(os.path.join(out, "remarks.tar.gz"),
                        [(a, s) for a, s in files if not a.endswith(".o")])
    return census


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["fetch", "build", "analyze", "all"])
    ap.add_argument("--deps", default="build/corpus-deps")
    ap.add_argument("--work", default="build/corpus-work")
    ap.add_argument("--out", default="build/corpus-out")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--only", default="", help="comma-separated project names (default: all)")
    ap.add_argument("--projects", default="projects.json", help="the list in corpus/ (projects2.json: census 2)")
    ap.add_argument("--target", default="baseline", choices=sorted(TARGETS))
    ap.add_argument("--shard", type=int, default=0, help="compile only projects with this shard (0: all)")
    a = ap.parse_args(argv)
    global TARGET
    TARGET = a.target
    deps, work, out = (os.path.abspath(x) for x in (a.deps, a.work, a.out))
    projects = load_projects([x for x in a.only.split(",") if x], a.projects, a.shard)
    if a.step in ("fetch", "all"):
        for line in fetch(projects, deps):
            print(line)
    if a.step in ("build", "all"):
        build(projects + [KERNELS], deps, work, a.jobs)
    if a.step in ("analyze", "all"):
        c = analyze(projects, deps, work, out, a.projects, a.shard)
        t = c["totals"]
        print("projects %d, vectorized NONE %d FAST %d, lost %d (%.2f%%), ud2 added %d, text %+.2f%%" % (
            t["projects"], t["none"]["vectorized"], t["fast"]["vectorized"], t["lost"],
            t["lost_pct_of_vectorized"] or 0, t["ud2_added"], t["text_bytes_change_pct"] or 0))
        print("kernel control:", "PASS" if c["controls"]["kernels"]["pass"] else "FAIL",
              c["controls"]["kernels"]["lost_kernels"])
        for d in c["dropped"]:
            print("dropped:", d["name"], d["reason"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
