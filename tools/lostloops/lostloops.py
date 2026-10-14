#!/usr/bin/env python3
"""lostloops: which of your loops stop being vectorized when you turn on libc++ hardening?

    python lostloops.py --compile-commands build/compile_commands.json [--mode fast|extensive|debug]
                        [--out lostloops-report] [--filter REGEX] [--root DIR] [--jobs N]
    python lostloops.py --files a.cpp b.cpp [--out DIR] -- <your compile flags, e.g. -O2 -std=c++20 -Iinclude>

Every C++ file is compiled twice with clang, with your flags exactly as given: once with libc++
hardening off (NONE) and once with it on (--mode, FAST by default). Only these are added:
-stdlib=libc++, -D_LIBCPP_HARDENING_MODE=..., the optimization-record flags, and -c -o <a temp
object>. The compiler's own records say which loops it vectorized in each build; a loop vectorized
with hardening off and not with it on is LOST. Nothing is linked, run or timed: a lost loop is a
candidate for a cost, not a measured cost. Time it before you change it.

Exit code: 0 when a report was written (whatever it says); 2 when clang, libc++ or the input is
missing; 1 only if the tool itself fails. Needs Python 3.8+, clang 18 or newer and libc++ 18 or
newer (on Ubuntu 24.04: apt install clang-18 libc++-18-dev libc++abi-18-dev binutils llvm-18).
The matching, classification and trap tracing are copied from the census in corpus/census.py.
"""
import argparse
import collections
import concurrent.futures
import json
import os
import posixpath
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ll_classify as classify  # noqa: E402
import ll_optrecord as optrecord  # noqa: E402

VERSION = "0.1"
EVIDENCE_DIR = os.path.join(HERE, "evidence")  # holds the <__assertion_handler> for the trap tracing
TRAP_SYMBOL = "__census_trap"
ORIGINS = ("project", "libc++", "system")
MODES = {
    "none": "_LIBCPP_HARDENING_MODE_NONE",
    "fast": "_LIBCPP_HARDENING_MODE_FAST",
    "extensive": "_LIBCPP_HARDENING_MODE_EXTENSIVE",
    "debug": "_LIBCPP_HARDENING_MODE_DEBUG",
}
CXX_EXT = (".cc", ".cpp", ".cxx", ".c++", ".cp", ".C", ".CPP", ".ixx", ".cppm")
LAUNCHERS = ("ccache", "sccache", "distcc", "icecc", "buildcache")

DISCLAIMER = ("This tool counts loops; it times nothing. A lost loop is only a candidate for a cost: how "
              "often it runs is unknown at compile time. Time the code with hardening off and on before "
              "changing anything.")

LIMITS = [
    "Counts, not time: a loop that runs once at start-up and a loop that runs a billion times count the same.",
    "One compiler: the clang and libc++ found on this machine, with your flags as given. Another clang "
    "version, another -march or GCC's own checks can give a different list.",
    "A loop counts once per function it was compiled into: a header loop inlined into three functions "
    "counts three times. The table groups them by source line and shows how many functions.",
    "The shape (reverse, strided, indirect, ...) is read from the source text with regular expressions: a "
    "heuristic, not a proof. Each loop is listed with its line so you can check the call.",
    "Only translation units in the input are compiled; header code counts only where a compiled file "
    "instantiates it.",
    "libc++ writes the hardening mode into the ABI tag of its inline functions ([abi:ne180100] with NONE, "
    "[abi:fe180100] with FAST); the hardened spelling is mapped to the NONE spelling before matching.",
    "The 'what to try' lines come from timed tests of four small kernels on AMD EPYC cloud machines "
    "(clang 18, FAST mode; this project's mitigate/README.md), not from your code.",
]

SHAPES = ("reverse index", "strided", "indirect", "forward, bounded by a variable", "other")

TRY = {
    "reverse index":
        "One size check before the loop (if (c.size() < n) abort();), or index a std::span(c).first(n) "
        "taken once: in our reverse-loop test either brought SIMD back (1.00x on 2 of 3 CPUs, 1.06x to 1.09x "
        "on the third). Do not switch to std::transform over rbegin()/rend(): libc++ 18 FAST does not check those "
        "iterators, so it is fast but unchecked.",
    "strided":
        "A size check with operator[] does not help here (clang 18 cannot prove 2*i+1 < size()). Take "
        "std::span(a).first(2*n) once and add #pragma clang loop interleave_count(2), or use raw data() "
        "pointers behind one size check (safety then rests on that one line).",
    "strided-matrix":
        "If the index is a matrix row (a[i*n + j]): raw row pointers behind one check that the matrix holds "
        "n*n elements (1.00x in our test); row spans (subspan(i*n, n)) keep every access checked but cost "
        "1.1x to 1.4x in cache. If it is a stride (a[2*i]): span first(2*n) plus interleave_count(2). A plain "
        "size check with operator[] does not help.",
    "indirect":
        "The check on a[idx[i]] depends on the data and cannot leave the loop. Move out what can: one size "
        "check (or spans) for the arrays indexed by i; in our gather test that cut 1.6x-1.8x to about 1.3x "
        "in L1. Clamping or validating the indexes first was slower.",
    "forward, bounded by a variable":
        "The loop runs to a variable, not the container's size(), so clang cannot prove each index is in "
        "range. Try one check before the loop that the bound fits (if (v.size() < n) abort();) or index a "
        "std::span(v).first(n): that worked in our reverse-loop test, where the index is the loop counter "
        "itself; this exact shape was not timed.",
    "other":
        "No measured fix for this shape. Read the compiler's remark; if the loop indexes a container with "
        "the loop counter, the up-front size check or span (see the reverse and forward rows) is the "
        "first thing to try.",
}


class ToolMissing(Exception):
    """clang, libc++ or the input is missing: a polite message and exit code 2."""


# ---------------------------------------------------------------- tools on this machine

class Tools:
    def __init__(self, clang, objdump=None, symbolizer=None, cxxfilt=None, version=""):
        self.clang = clang          # a list: the compiler command (may include a launcher)
        self.objdump = objdump      # a path or None (then no trap count, no text size, no tracing)
        self.symbolizer = symbolizer
        self.cxxfilt = cxxfilt
        self.version = version


def run(cmd, **kw):
    """subprocess.run with text output; one place for tests to replace."""
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace", **kw)


def _which_versioned(names, version_hint):
    """The first program found: a version-matched name first (e.g. llvm-symbolizer-18), then the rest."""
    cands = []
    for n in names:
        if version_hint:
            cands.append("%s-%s" % (n, version_hint))
    for v in range(25, 17, -1):
        for n in names:
            cands.append("%s-%d" % (n, v))
    cands += list(names)
    for c in cands:
        p = shutil.which(c)
        if p:
            return p
    return None


def clang_candidates():
    """Every clang++-NN on PATH, newest first, then plain clang++ (each as a command list)."""
    out = []
    for v in range(25, 17, -1):
        p = shutil.which("clang++-%d" % v)
        if p:
            out.append([p])
    p = shutil.which("clang++")
    if p:
        out.append([p])
    return out


def find_clang(explicit):
    if explicit:
        cmd = shlex.split(explicit)
        if not cmd or not (shutil.which(cmd[0]) or os.path.exists(cmd[0])):
            raise ToolMissing("clang not found: %r. Install clang 18 or newer (Ubuntu 24.04: sudo apt install "
                              "clang-18 libc++-18-dev libc++abi-18-dev) or pass --clang PATH." % explicit)
        return cmd
    cands = clang_candidates()
    if cands:
        return cands[0]
    raise ToolMissing("clang++ not found on PATH. This tool needs clang 18 or newer with libc++ (it runs on "
                      "Linux; Windows and macOS's Apple clang are not supported). Ubuntu 24.04: sudo apt "
                      "install clang-18 libc++-18-dev libc++abi-18-dev binutils llvm-18")


LIBCXX_PROBE = """#include <version>
#if !defined(_LIBCPP_VERSION)
#error "not libc++"
#endif
#if _LIBCPP_VERSION < 180000
#error "libc++ older than 18: no _LIBCPP_HARDENING_MODE"
#endif
int lostloops_probe = _LIBCPP_VERSION;
"""


def check_toolchain(clang):
    """(clang --version first line, major version) or ToolMissing."""
    try:
        r = run(clang + ["--version"], timeout=60)
    except OSError as e:
        raise ToolMissing("could not run clang (%s): %s" % (" ".join(clang), e))
    first = (r.stdout.splitlines() or ["?"])[0]
    if r.returncode != 0 or "clang" not in r.stdout.lower():
        raise ToolMissing("%s does not look like clang (got: %s)" % (" ".join(clang), first))
    m = re.search(r"version (\d+)", r.stdout)
    major = m.group(1) if m else ""
    if major and int(major) < 18:
        raise ToolMissing("clang %s found; libc++ hardening modes need clang and libc++ 18 or newer" % major)
    try:
        p = run(clang + ["-x", "c++", "-std=c++17", "-stdlib=libc++", "-fsyntax-only", "-"], input=LIBCXX_PROBE,
                timeout=120)
    except OSError as e:
        raise ToolMissing("could not run clang: %s" % e)
    if p.returncode != 0:
        err = " | ".join([x for x in p.stderr.splitlines() if "error" in x][:2]) or p.stderr.strip()[:300]
        raise ToolMissing("libc++ 18 or newer is not usable with %s (%s). Ubuntu 24.04: sudo apt install "
                          "libc++-18-dev libc++abi-18-dev" % (" ".join(clang), err))
    return first, major


def find_tools(args):
    explicit = args.clang or os.environ.get("LOSTLOOPS_CLANG")
    if explicit:
        clang = find_clang(explicit)
        version, major = check_toolchain(clang)
    else:
        # A machine can have a newer clang++-NN on PATH without libc++-NN-dev (GitHub's Ubuntu images
        # have several clangs): take the newest one whose libc++ works, report the first failure.
        cands = clang_candidates() or [find_clang(None)]
        first_error = None
        for clang in cands:
            try:
                version, major = check_toolchain(clang)
                break
            except ToolMissing as e:
                first_error = first_error or e
        else:
            raise first_error
    if args.objdump == "none":
        objdump = None
    else:
        objdump = args.objdump or shutil.which("objdump") or _which_versioned(["llvm-objdump"], major)
    return Tools(clang, objdump=objdump, symbolizer=_which_versioned(["llvm-symbolizer"], major),
                 cxxfilt=_which_versioned(["llvm-cxxfilt"], major) or shutil.which("c++filt"), version=version)


# ---------------------------------------------------------------- inputs: translation units and flags

def is_abs(p):
    return p.startswith("/") or bool(re.match(r"^[A-Za-z]:/", p))


def slash(p):
    return p.replace("\\", "/")


def resolve(path, directory):
    """An absolute, normalized, forward-slash path."""
    p = slash(path)
    if not is_abs(p):
        p = slash(directory).rstrip("/") + "/" + p
    return posixpath.normpath(p)


def load_compile_commands(path):
    """[{"directory", "file" (absolute), "args" (without the compiler)}] for the C++ entries."""
    try:
        with open(path, encoding="utf-8") as f:
            db = json.load(f)
    except OSError as e:
        raise ToolMissing("cannot read %s: %s" % (path, e))
    except ValueError as e:
        raise ToolMissing("%s is not valid JSON: %s" % (path, e))
    if not isinstance(db, list):
        raise ToolMissing("%s is not a compile_commands.json list" % path)
    out, seen = [], set()
    for e in db:
        if not isinstance(e, dict) or "file" not in e or "directory" not in e:
            continue
        argv = e.get("arguments") or shlex.split(e.get("command", ""))
        if not argv:
            continue
        argv = strip_compiler(argv)
        file = resolve(e["file"], e["directory"])
        if not is_cxx(file, argv):
            continue
        key = (file, tuple(argv))
        if key in seen:
            continue
        seen.add(key)
        out.append({"directory": slash(e["directory"]), "file": file, "args": argv})
    return out


def strip_compiler(argv):
    """The arguments without the compiler (and a launcher such as ccache in front of it)."""
    i = 1
    if os.path.basename(argv[0]).split(".")[0] in LAUNCHERS and len(argv) > 1:
        i = 2
    return list(argv[i:])


def is_cxx(file, args):
    for i, a in enumerate(args[:-1]):
        if a == "-x":
            return args[i + 1] in ("c++", "c++-header")
        if a.startswith("-x") and len(a) > 2:
            return a[2:] in ("c++", "c++-header")
    return file.endswith(CXX_EXT)


# Flags removed from the user's command: those that write files, pick the standard library or set the
# hardening mode. Everything else is kept exactly as given.
_DROP_WITH_VALUE = {"-o", "-MF", "-MT", "-MQ"}
_DROP = {"-c", "-MD", "-MMD", "-MP", "-M", "-MM", "-fsave-optimization-record",
         "-fwhole-program-vtables", "-fvirtual-function-elimination", "-fsplit-lto-unit"}
# -flto (also -flto=thin, -flto-jobs=N) is dropped: with it clang compiles to bitcode and the loop
# vectorizer only runs at link time, so a compile-only run would see no vectorized loop at all.
_DROP_PREFIX = ("-flto", "-stdlib=", "-foptimization-record-file=", "-foptimization-record-passes=",
                "-fsave-optimization-record=", "-MF", "-MT", "-MQ", "-D_LIBCPP_HARDENING_MODE",
                "-U_LIBCPP_HARDENING_MODE", "-D_LIBCPP_ENABLE_ASSERTIONS", "-D_LIBCPP_ENABLE_HARDENED_MODE",
                "-D_LIBCPP_ENABLE_SAFE_MODE", "-D_LIBCPP_ENABLE_DEBUG_MODE")
_OPT = re.compile(r"^(?:-O\d*|-Os|-Oz|-Ofast|-Og|/O\w+)$")


def clean_args(args):
    """(kept arguments, removed arguments). A '-D' or '-U' given as two arguments is handled."""
    kept, removed, i = [], [], 0
    while i < len(args):
        a = args[i]
        nxt = args[i + 1] if i + 1 < len(args) else ""
        if a in _DROP_WITH_VALUE:
            removed += [a, nxt]
            i += 2
            continue
        if a in ("-D", "-U") and nxt.startswith(("_LIBCPP_HARDENING_MODE", "_LIBCPP_ENABLE_")):
            removed += [a, nxt]
            i += 2
            continue
        if a in _DROP or a.startswith(_DROP_PREFIX):
            removed.append(a)
            i += 1
            continue
        kept.append(a)
        i += 1
    return kept, removed


def has_opt_level(args):
    return any(_OPT.match(a) for a in args)


def build_cmd(tools, unit, mode, obj, record, extra=()):
    """The compile command for one build. Our flags go right after the compiler, before the user's
    (so they also come before a '--' that ends the options)."""
    kept, _ = clean_args(unit["args"])
    ours = ["-stdlib=libc++", "-D_LIBCPP_HARDENING_MODE=" + MODES[mode], "-fsave-optimization-record",
            "-foptimization-record-passes=loop-vectorize", "-foptimization-record-file=" + record,
            "-c", "-o", obj] + list(extra)
    return tools.clang + ours + kept


# ---------------------------------------------------------------- compile

def obj_name(i, unit):
    base = re.sub(r"[^A-Za-z0-9_.-]", "_", posixpath.basename(unit["file"]))
    return "%04d_%s" % (i, base)


def compile_all(tools, units, modes, work, jobs, extra_flags=(), timeout=1800):
    """Each unit compiled in each mode. Returns {(i, mode): {"rc", "stderr", "obj", "record"}}."""
    tasks = [(i, u, m) for i, u in enumerate(units) for m in modes]

    def one(task):
        i, u, m = task
        base = os.path.join(work, m, obj_name(i, u))
        os.makedirs(os.path.dirname(base), exist_ok=True)
        obj, rec = base + ".o", base + ".opt.yaml"
        cmd = build_cmd(tools, u, m, slash(obj), slash(rec)) + list(extra_flags)
        try:
            r = run(cmd, cwd=u["directory"], timeout=timeout)
            rc, err = r.returncode, r.stderr
        except (OSError, subprocess.TimeoutExpired) as e:
            rc, err = -1, "error: %s" % e
        return (i, m), {"rc": rc, "stderr": err, "obj": obj, "record": rec, "cmd": cmd}

    out = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        for key, res in ex.map(one, tasks):
            out[key] = res
    return out


# ---------------------------------------------------------------- analysis (as in corpus/census.py)

_ABI_TAG = re.compile(r"B8[nfsd]([en]\d{6})")


def norm_function(mangled):
    """libc++ writes the hardening mode into the ABI tag of its inline functions ([abi:ne180100] with
    NONE, [abi:fe180100] with FAST, s for extensive, d for debug), so the same function has two names.
    The hardened spelling is mapped to NONE's before loops are matched."""
    return _ABI_TAG.sub(lambda m: "B8n" + m.group(1), mangled)


def norm_file(abs_path, root):
    """(stable name, origin): project-relative, 'libc++/<header>', or the absolute path ('system')."""
    p = slash(abs_path)
    if "/include/c++/v1/" in p:
        return "libc++/" + p.split("/include/c++/v1/", 1)[1], "libc++"
    r = posixpath.normpath(slash(root)).rstrip("/") + "/"
    if p.startswith(r):
        return p[len(r):], "project"
    return p, "system"


def read_records(text, directory, root, paths):
    """Loop-vectorize records of one build -> (vectorized Counter, other messages, vectorized message).
    The key is (function with the ABI tag mapped, file, line, column, origin). `paths` collects each
    file's absolute path, for reading the source later."""
    recs = optrecord.loop_vectorize(optrecord.parse(text))
    vec = collections.Counter()
    msgs = collections.defaultdict(set)
    vmsg = {}
    for r in recs:
        loc = r["loc"] or {"file": "?", "line": 0, "column": 0}
        absp = resolve(loc["file"], directory) if loc["file"] != "?" else "?"
        file, origin = norm_file(absp, root)
        paths.setdefault(file, absp)
        key = (norm_function(r["function"]), file, loc["line"], loc["column"], origin)
        if optrecord.is_vectorized(r):
            vec[key] += 1
            vmsg[key] = r["message"]
        else:
            msgs[key].add(r["message"])
    return vec, msgs, vmsg


def match_unit(tu, none_data, hard_data):
    """lost / moved / gained entries for one translation unit, exactly as corpus/census.py matches:
    a loop is LOST when its (function, file:line:column) has more vectorized copies in NONE than in
    the hardened build, and MOVED when the same source location gained a vectorized copy in another
    function of the same unit."""
    vn, mn, vmn = none_data
    vf, mf, _ = hard_data
    loc_n, loc_f = collections.Counter(), collections.Counter()
    for k, c in vn.items():
        loc_n[k[1:4]] += c
    for k, c in vf.items():
        loc_f[k[1:4]] += c
    budget = {loc: max(0, loc_n[loc] - loc_f[loc]) for loc in loc_n}
    lost, moved, gained = [], [], []
    for key in sorted(set(vn) | set(vf)):
        n, f = vn.get(key, 0), vf.get(key, 0)
        func, file, line, col, origin = key
        entry = {"tu": tu, "function": func, "file": file, "line": line, "column": col, "origin": origin}
        if n > f:
            k_lost = min(n - f, budget[key[1:4]])
            budget[key[1:4]] -= k_lost
            entry.update({"none_remark": vmn.get(key, ""), "hardened_remarks": sorted(mf.get(key, set()))})
            if k_lost:
                lost.append(dict(entry, count=k_lost))
            if n - f - k_lost:
                moved.append(dict(entry, count=n - f - k_lost))
        elif f > n:
            gained.append(dict(entry, count=f - n, none_remarks=sorted(mn.get(key, set()))))
    return lost, moved, gained


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


def shape_of(cls, detail):
    if cls == "reverse":
        return "reverse index"
    if cls in ("strided", "indirect"):
        return cls
    if detail.startswith("forward loop bounded by a variable"):
        return "forward, bounded by a variable"
    return "other"


def what_to_try(shape, detail):
    if shape == "strided" and detail.startswith("multiplied index"):
        return TRY["strided-matrix"]
    return TRY[shape]


def describe(entries, paths):
    """Source text, census class, shape, trip count and 'what to try' for each entry (in place)."""
    for e in entries:
        lines = source_lines(paths.get(e["file"], e["file"]))
        idx = e["line"] - 1
        ctx = classify.loop_context(lines, idx) if 0 <= idx < len(lines) else []
        e["source_line"] = clip(ctx[0].strip()) if ctx else ""
        e["context"] = [clip(x) for x in ctx]
        cls, detail = classify.classify(ctx, e["column"], e["origin"],
                                        " | ".join(e.get("hardened_remarks", [])))
        e["class"], e["detail"] = cls, detail
        e["shape"] = shape_of(cls, detail)
        if "hardened_remarks" in e:
            e["trip_count"] = classify.trip_count(e["context"], e["column"])
            e["what_to_try"] = what_to_try(e["shape"], detail)


# ---------------------------------------------------------------- objdump: traps and text size

def parse_ud2(dump):
    return sum(1 for ln in dump.splitlines() if re.search(r":\s+ud2\b", ln))


def parse_text_bytes(headers):
    text = 0
    for ln in headers.splitlines():
        f = ln.split()
        if len(f) >= 3 and f[0].isdigit() and f[1].startswith(".text"):
            try:
                text += int(f[2], 16)
            except ValueError:
                pass
    return text


def objdump_stats(tools, obj):
    """(ud2 count, .text* bytes) of one object, or (None, None) without objdump."""
    if not tools.objdump or not os.path.exists(obj):
        return None, None
    d = run([tools.objdump, "-d", "--no-show-raw-insn", obj])
    h = run([tools.objdump, "-h", obj])
    if d.returncode != 0 or h.returncode != 0:
        return None, None
    return parse_ud2(d.stdout), parse_text_bytes(h.stdout)


# ---------------------------------------------------------------- trap tracing (as in corpus/census.py)

_SYM = re.compile(r"^[0-9a-f]+ <(.+)>:\s*$")
_PLAIN_INSN = re.compile(r"^\s+([0-9a-f]+):\s+([a-z][\w.]*)\s*(.*)$")
_LOCLINE = re.compile(r"^(/[^:]*|[^\s<:][^:]*):(\d+)(?: \(discriminator \d+\))?\s*$")
_INLINED = re.compile(r"^inlined by (.+?):(\d+)(?:\s.*)?$")
_INSN = re.compile(r"^\s+([0-9a-f]+):\s+([a-z][\w.]*)")
_RELOC = re.compile(r"^\s+[0-9a-f]+:\s+R_[A-Z0-9_]+\s+(\S+)")
_ASSERT = re.compile(r"_LIBCPP_ASSERT\w*\s*\(")
_STRLIT = re.compile(r'"((?:[^"\\]|\\.)*)"')


def parse_objdump_checks(text):
    """`objdump -d --no-show-raw-insn` of a linked file -> {symbol: [address of each check]}."""
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
    """`llvm-symbolizer --inlining` output -> [chain], chain = ((file, line), ...) innermost first."""
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


def parse_objdump_lines(text):
    """`objdump -d -r -l --inlines --no-show-raw-insn` -> {symbol: [(mnemonic, chain)]}; a call whose
    relocation names TRAP_SYMBOL is reported with the mnemonic "check"."""
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
    """The message of the libc++ assertion at (or just above) 1-based `line`, or None."""
    for j in range(line - 1, max(-1, line - 5), -1):
        if 0 <= j < len(lines) and _ASSERT.search(lines[j]):
            for k in (j, j + 1, j + 2):
                if k < len(lines):
                    lits = _STRLIT.findall(lines[k])
                    if lits:
                        return lits[-1]
            return "(assertion without a message)"
    return None


def evidence_for(entry, chains, root, paths):
    """Whether a check (a libc++ assertion) was traced to a line inside the lost loop."""
    src = source_lines(paths.get(entry["file"], entry["file"]))
    idx = entry["line"] - 1
    body = classify.loop_context(src, idx, max_lines=80) if 0 <= idx < len(src) else []
    lo, hi = entry["line"], entry["line"] + max(0, len(body) - 1)
    msgs, attributed = set(), 0
    example = []
    for chain in chains:
        frames = []
        for f, ln in chain:
            name, origin = norm_file(posixpath.normpath(slash(f)), root)
            frames.append((name, origin, ln, slash(f)))
        msg = None
        for name, origin, ln, absf in frames:
            if origin == "libc++":
                msg = libcxx_assertion(source_lines(absf), ln)
                if msg:
                    break
        in_loop = any(name == entry["file"] and lo <= ln <= hi for name, _, ln, _ in frames)
        if msg and in_loop:
            attributed += 1
            msgs.add(msg)
            if not example:
                example = ["%s:%d" % (n, ln) for n, _, ln, _ in frames]
    return {"status": "check traced to the loop" if attributed else "no check traced to the loop",
            "messages": sorted(msgs), "attributed_checks": attributed, "checks_in_function": len(chains),
            "loop_lines": [lo, hi], "example_chain": example}


def trace_unit(tools, unit, i, mode, work, entries, root, paths, timeout=1800):
    """Adds "check" to each lost entry of one unit (in place): one more hardened build with line
    tables and the evidence handler (each libc++ check a separate call), every check located with
    objdump and traced with llvm-symbolizer (or objdump -l when linking fails). A timeout or an
    unrunnable tool leaves "not traced (...)" on the entries; it never aborts the report."""
    try:
        _trace_unit(tools, unit, i, mode, work, entries, root, paths, timeout)
    except (OSError, subprocess.SubprocessError) as ex:
        for e in entries:
            e["check"] = {"status": "not traced (%s)" % clip(str(ex), 200)}


def _trace_unit(tools, unit, i, mode, work, entries, root, paths, timeout):
    if not tools.objdump:
        for e in entries:
            e["check"] = {"status": "not traced (objdump not found)"}
        return
    base = os.path.join(work, mode + "-g", obj_name(i, unit))
    os.makedirs(os.path.dirname(base), exist_ok=True)
    obj, rec = base + ".o", base + ".opt.yaml"
    cmd = build_cmd(tools, unit, mode, slash(obj), slash(rec), ["-gline-tables-only", "-I" + slash(EVIDENCE_DIR)])
    r = run(cmd, cwd=unit["directory"], timeout=timeout)
    if r.returncode != 0:
        err = " | ".join([x for x in r.stderr.splitlines() if "error" in x][:2])
        for e in entries:
            e["check"] = {"status": "not traced (the traced rebuild failed: %s)" % clip(err, 200)}
        return
    chains_by_sym = {}
    elf = base + ".elf"
    lk = run(tools.clang + ["-fuse-ld=bfd", "-pie", "-nostdlib", "-Wl,--unresolved-symbols=ignore-all",
                            "-Wl,-e,0", "-o", elf, obj], timeout=timeout)
    if lk.returncode == 0 and tools.symbolizer:
        d = run([tools.objdump, "-d", "--no-show-raw-insn", elf], timeout=timeout).stdout
        checks = parse_objdump_checks(d)
        addrs = sorted({a for v in checks.values() for a in v})
        sy = run([tools.symbolizer, "--obj=" + elf, "--inlining", "--functions=linkage"],
                 input="".join("0x%x\n" % a for a in addrs))
        got = dict(zip(addrs, parse_symbolizer(sy.stdout))) if sy.returncode == 0 else {}
        for sym, v in checks.items():
            chains_by_sym[sym] = [got.get(a, ()) for a in v]
        how = "linked; objdump + llvm-symbolizer"
    else:
        d = run([tools.objdump, "-d", "-r", "-l", "--inlines", "--no-show-raw-insn", obj], timeout=timeout).stdout
        for sym, insns in parse_objdump_lines(d).items():
            chains_by_sym[sym] = [c for mn, c in insns if mn in ("check", "ud2")]
        how = "objdump -l --inlines on the object"
    for e in entries:
        chains = [c for sym, cs in chains_by_sym.items() if norm_function(sym) == e["function"] for c in cs]
        ev = evidence_for(e, chains, root, paths)
        ev["tracing"] = how
        e["check"] = ev


# ---------------------------------------------------------------- the whole pipeline

def demangle(tools, names):
    names = sorted(set(n for n in names if n))
    if not names or not tools.cxxfilt:
        return {n: n for n in names}
    r = run([tools.cxxfilt], input="\n".join(names) + "\n")
    out = r.stdout.splitlines()
    if r.returncode == 0 and len(out) == len(names):
        return dict(zip(names, out))
    return {n: n for n in names}


def pct(a, b):
    return round(100.0 * a / b, 3) if b else None


def analyze(tools, units, mode, results, root, work, trace=True, jobs=1, timeout=1800):
    """The report dict from the compile results."""
    paths = {}
    failed, ok = [], []
    for i, u in enumerate(units):
        bad = [m for m in ("none", mode) if results[(i, m)]["rc"] != 0 or not os.path.exists(results[(i, m)]["record"])]
        if bad:
            st = results[(i, bad[0])]["stderr"]
            err = " | ".join([x for x in st.splitlines() if "error" in x][:3]) or st.strip()[:300]
            failed.append({"file": norm_file(u["file"], root)[0], "build": bad[0], "error": clip(err, 400)})
        else:
            ok.append(i)
    stats = {m: {"vectorized": 0, "vectorized_locations": set(), "ud2": 0, "text_bytes": 0, "measured": True}
             for m in ("none", mode)}
    lost, moved, gained, by_unit = [], [], [], collections.defaultdict(list)
    for i in ok:
        u = units[i]
        tu = norm_file(u["file"], root)[0]
        data = {}
        for m in ("none", mode):
            with open(results[(i, m)]["record"], encoding="utf-8", errors="replace") as f:
                data[m] = read_records(f.read(), u["directory"], root, paths)
            st = stats[m]
            st["vectorized"] += sum(data[m][0].values())
            st["vectorized_locations"].update((tu,) + k[1:4] for k in data[m][0])
            ud2, text = objdump_stats(tools, results[(i, m)]["obj"])
            if ud2 is None:
                st["measured"] = False
            else:
                st["ud2"] += ud2
                st["text_bytes"] += text
        lo, mo, ga = match_unit(tu, data["none"], data[mode])
        lost += lo
        moved += mo
        gained += ga
        by_unit[i] += lo
    describe(lost + moved + gained, paths)
    if trace:
        todo = [(i, es) for i, es in sorted(by_unit.items()) if es]
        # one rebuild per unit with lost loops, in parallel (a large project has many such units)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
            list(ex.map(lambda t: trace_unit(tools, units[t[0]], t[0], mode, work, t[1], root, paths, timeout), todo))
    else:
        for e in lost:
            e["check"] = {"status": "not traced (--no-trace)"}
    names = demangle(tools, [e["function"] for e in lost + moved + gained])
    for e in lost + moved + gained:
        e["function_name"] = clip(names.get(e["function"], e["function"]), 300)

    measured = stats["none"]["measured"] and stats[mode]["measured"] and bool(ok)
    n_lost = sum(e["count"] for e in lost)
    groups = group_lost(lost)
    totals = {
        "files_in_input": len(units), "files_compiled": len(ok), "files_failed": len(failed),
        "vectorized_none": stats["none"]["vectorized"], "vectorized_hardened": stats[mode]["vectorized"],
        "vectorized_locations_none": len(stats["none"]["vectorized_locations"]),
        "lost": n_lost, "lost_locations": len(groups),
        "lost_locations_in_project": sum(1 for g in groups if g["origin"] == "project"),
        "lost_pct_of_vectorized": pct(n_lost, stats["none"]["vectorized"]),
        "moved": sum(e["count"] for e in moved), "gained": sum(e["count"] for e in gained),
        "traps_none": stats["none"]["ud2"] if measured else None,
        "traps_hardened": stats[mode]["ud2"] if measured else None,
        "traps_added": stats[mode]["ud2"] - stats["none"]["ud2"] if measured else None,
        "text_bytes_none": stats["none"]["text_bytes"] if measured else None,
        "text_bytes_hardened": stats[mode]["text_bytes"] if measured else None,
        "text_change_pct": pct(stats[mode]["text_bytes"] - stats["none"]["text_bytes"],
                               stats["none"]["text_bytes"]) if measured else None,
        "lost_by_shape": {s: sum(e["count"] for e in lost if e["shape"] == s) for s in SHAPES},
        "lost_with_check_traced": sum(e["count"] for e in lost
                                      if e.get("check", {}).get("status") == "check traced to the loop"),
    }
    return {"failed": failed, "totals": totals, "lost_by_location": groups,
            "lost": lost, "moved": moved, "gained": gained, "traps_measured": measured}


def group_lost(lost):
    """One row per source location: the functions it was lost in, the shape, the remarks."""
    rows = collections.OrderedDict()
    for e in sorted(lost, key=lambda e: (ORIGINS.index(e["origin"]), e["file"], e["line"], e["column"])):
        k = (e["file"], e["line"], e["column"])
        if k not in rows:
            rows[k] = {"where": "%s:%d:%d" % k, "file": e["file"], "line": e["line"], "column": e["column"],
                       "origin": e["origin"], "shape": e["shape"], "detail": e["detail"],
                       "source_line": e["source_line"], "count": 0, "functions": [],
                       "none_remark": e["none_remark"], "hardened_remarks": set(), "check": "not traced",
                       "check_messages": set(), "what_to_try": e["what_to_try"]}
        r = rows[k]
        r["count"] += e["count"]
        r["functions"].append(e.get("function_name", e["function"]))
        r["hardened_remarks"].update(e["hardened_remarks"])
        st = e.get("check", {}).get("status", "not traced")
        if st == "check traced to the loop":
            r["check"] = "yes"
            r["check_messages"].update(e["check"].get("messages", []))
        elif st == "no check traced to the loop" and r["check"] != "yes":
            r["check"] = "no"
        elif r["check"] not in ("yes", "no"):
            r["check"] = st
    out = []
    for r in rows.values():
        r["hardened_remarks"] = sorted(r["hardened_remarks"])
        r["check_messages"] = sorted(r["check_messages"])
        r["functions"] = sorted(set(r["functions"]))
        out.append(r)
    return out


# ---------------------------------------------------------------- report

def short_remark(remarks):
    """The most telling of clang's remarks for the hardened build."""
    for r in remarks:
        if r.startswith("loop not vectorized: "):
            return r[len("loop not vectorized: "):]
    for r in remarks:
        if "vectorization is not beneficial" in r:
            return "cost model: vectorization not beneficial"
    return remarks[0] if remarks else "(no remark for this loop in the hardened build)"


def check_cell(row, short=False):
    if row["check"] == "yes":
        return "yes: " + "; ".join(row["check_messages"])
    if short and row["check"].startswith("not traced"):
        return "not traced"
    return row["check"]


def render_text(rep, top=40):
    t = rep["totals"]
    m = rep["mode"].upper()
    out = []
    out.append("lostloops %s: libc++ hardening NONE vs %s, %s" % (VERSION, m, rep["toolchain"]["clang"]))
    out.append("")
    out.append("Files compiled: %d of %d%s" % (t["files_compiled"], t["files_in_input"],
                                              (" (%d failed, see the report)" % t["files_failed"]) if t["files_failed"] else ""))
    if rep["no_opt_level"]:
        out.append("NOTE: %d file(s) have no -O level in their flags, so clang compiled them at -O0, where it "
                   "vectorizes nothing. Use your release build's compile_commands.json." % len(rep["no_opt_level"]))
    out.append("Vectorized loops with hardening off: %d (%d source locations); with %s: %d"
               % (t["vectorized_none"], t["vectorized_locations_none"], m, t["vectorized_hardened"]))
    out.append("LOST under %s: %d (%s of the vectorized), at %d source locations (%d in your project)"
               % (m, t["lost"], ("%.2f%%" % t["lost_pct_of_vectorized"]) if t["lost_pct_of_vectorized"] is not None
                  else "n/a", t["lost_locations"], t["lost_locations_in_project"]))
    out.append("Gained (vectorized only with %s): %d; moved to another function: %d" % (m, t["gained"], t["moved"]))
    if t["traps_added"] is not None:
        out.append("Check traps (ud2) added: %d; code size (.text) change: %+.2f%%"
                   % (t["traps_added"], t["text_change_pct"] or 0.0))
    else:
        out.append("Check traps and code size: not measured (objdump not found)")
    out.append("")
    rows = rep["lost_by_location"]
    if rows:
        out.append("%-44s %-30s %-5s %-24s %s" % ("where", "shape", "fns", "check in the loop", "compiler says (hardened)"))
        for r in rows[:top]:
            out.append("%-44s %-30s %-5d %-24s %s" % (clip(r["where"], 44), r["shape"], len(r["functions"]),
                                                      clip(check_cell(r, short=True), 24), short_remark(r["hardened_remarks"])))
            if r["source_line"]:
                out.append("    %s" % clip(r["source_line"], 110))
        if len(rows) > top:
            out.append("... %d more in report.md" % (len(rows) - top))
        out.append("")
        out.append("What to try, by shape (from timed tests of small kernels under FAST, not of your code%s):"
                   % ("; not tested for " + m if m != "FAST" else ""))
        for s in SHAPES:
            if any(r["shape"] == s for r in rows):
                keys = ["strided-matrix"] if s == "strided" and all(
                    r["detail"].startswith("multiplied") for r in rows if r["shape"] == s) else [s]
                out.append("  %s: %s" % (s, TRY[keys[0]]))
    else:
        out.append("No loop lost vectorization under %s." % m)
    out.append("")
    out.append(DISCLAIMER)
    out.append("Report: %s" % rep["out_files"])
    return "\n".join(out) + "\n"


def md_cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def render_md(rep):
    t = rep["totals"]
    m = rep["mode"].upper()
    L = ["# Lost loops: libc++ hardening NONE vs %s" % m, "",
         "> %s" % DISCLAIMER, "",
         "Compiler: `%s`. Project root: `%s`. Tool: lostloops %s." % (rep["toolchain"]["clang"], rep["root"], VERSION), "",
         "| | |", "|---|---|",
         "| files compiled | %d of %d |" % (t["files_compiled"], t["files_in_input"]),
         "| vectorized loops, hardening off | %d (%d source locations) |" % (t["vectorized_none"], t["vectorized_locations_none"]),
         "| vectorized loops, %s | %d |" % (m, t["vectorized_hardened"]),
         "| **lost** (vectorized off, not with %s) | **%d** (%s), %d locations, %d in the project |" % (
             m, t["lost"], ("%.2f%%" % t["lost_pct_of_vectorized"]) if t["lost_pct_of_vectorized"] is not None else "n/a",
             t["lost_locations"], t["lost_locations_in_project"]),
         "| gained / moved | %d / %d |" % (t["gained"], t["moved"]),
         "| check traps (ud2) added | %s |" % ("not measured" if t["traps_added"] is None else t["traps_added"]),
         "| code size (.text) change | %s |" % ("not measured" if t["text_change_pct"] is None else "%+.2f%%" % t["text_change_pct"]),
         "| lost loops with a libc++ check traced inside | %d |" % t["lost_with_check_traced"], ""]
    if rep["no_opt_level"]:
        L += ["**Note:** %d file(s) have no -O level in their flags (clang's default is -O0, where nothing is "
              "vectorized): %s" % (len(rep["no_opt_level"]), ", ".join("`%s`" % f for f in rep["no_opt_level"][:10])), ""]
    L += ["## Lost loops", ""]
    if rep["lost_by_location"]:
        L += ["| where | origin | shape | functions | check in the loop | compiler says (%s) | source | what to try |" % m,
              "|---|---|---|---|---|---|---|---|"]
        for r in rep["lost_by_location"]:
            L.append("| `%s` | %s | %s | %d | %s | %s | `%s` | %s |" % (
                md_cell(r["where"]), r["origin"], md_cell(r["shape"]), len(r["functions"]), md_cell(check_cell(r)),
                md_cell("; ".join(r["hardened_remarks"]) or "(none)"), md_cell(r["source_line"]), md_cell(r["what_to_try"])))
    else:
        L.append("None.")
    if rep["failed"]:
        L += ["", "## Files that did not compile", ""]
        for f in rep["failed"]:
            L.append("- `%s` (%s build): %s" % (f["file"], f["build"], md_cell(f["error"])))
    L += ["", "## Limits", ""] + ["- %s" % x for x in LIMITS] + [""]
    return "\n".join(L)


def write_report(rep, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rep["out_files"] = "%s, %s" % (slash(os.path.join(out_dir, "report.md")), slash(os.path.join(out_dir, "report.json")))
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, indent=1)
        f.write("\n")
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(rep))


# ---------------------------------------------------------------- command line

def parse_args(argv):
    flags = []
    if "--" in argv:
        k = argv.index("--")
        argv, flags = argv[:k], argv[k + 1:]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--compile-commands", help="your build's compile_commands.json (CMake: -DCMAKE_EXPORT_COMPILE_COMMANDS=ON)")
    src.add_argument("--files", nargs="+", help="C++ files to compile; put your compile flags after --")
    ap.add_argument("--mode", default="fast", choices=["fast", "extensive", "debug"], help="the hardening mode to compare against NONE")
    ap.add_argument("--out", default="lostloops-report", help="folder for report.md and report.json")
    ap.add_argument("--root", help="your project's root (default: the common folder of the files and the compile_commands.json)")
    ap.add_argument("--filter", help="only files whose path matches this regular expression")
    ap.add_argument("--add-flag", action="append", default=[], help="one more compile flag for every file (e.g. -Wno-error); repeatable")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--clang", help="the clang++ to use (default: the newest clang++-NN on PATH, then clang++; env LOSTLOOPS_CLANG)")
    ap.add_argument("--objdump", help="objdump to use, or 'none' to skip traps, code size and tracing")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds allowed for one compile (default 1800)")
    ap.add_argument("--no-trace", action="store_true", help="skip the extra build that traces checks into lost loops")
    ap.add_argument("--keep-work", action="store_true", help="keep the objects and records (printed path)")
    ap.add_argument("--top", type=int, default=40, help="rows printed on screen (all rows go into report.md)")
    a = ap.parse_args(argv)
    a.flags = flags
    if a.files is None and flags:
        ap.error("flags after -- go with --files; with --compile-commands use --add-flag")
    return a


def units_from_args(a):
    if a.compile_commands:
        units = load_compile_commands(a.compile_commands)
        anchor = [slash(os.path.dirname(os.path.abspath(a.compile_commands)))]
    else:
        cwd = slash(os.getcwd())
        units = []
        for f in a.files:
            p = resolve(f, cwd)
            if not os.path.exists(p):
                raise ToolMissing("file not found: %s" % f)
            units.append({"directory": cwd, "file": p, "args": list(a.flags) + [p]})
        anchor = [cwd]
    if a.filter:
        rx = re.compile(a.filter)
        units = [u for u in units if rx.search(u["file"])]
    if not units:
        raise ToolMissing("no C++ files to compile (check the input%s)" % (" and --filter" if a.filter else ""))
    if a.root:
        root = resolve(a.root, slash(os.getcwd()))
    else:
        dirs = [posixpath.dirname(u["file"]) for u in units] + anchor
        try:
            root = slash(os.path.commonpath([d.replace("/", os.sep) for d in dirs]))
        except ValueError:  # different drives
            root = posixpath.dirname(units[0]["file"])
    return units, posixpath.normpath(root)


def main(argv=None, tools=None):
    a = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        units, root = units_from_args(a)
        if tools is None:
            tools = find_tools(a)
    except ToolMissing as e:
        print("lostloops: %s" % e, file=sys.stderr)
        return 2
    if a.objdump == "none":
        tools.objdump = None
    work = tempfile.mkdtemp(prefix="lostloops-")
    try:
        print("lostloops: compiling %d file(s) twice (NONE and %s) with %s ..." % (
            len(units), a.mode.upper(), " ".join(tools.clang)), file=sys.stderr)
        results = compile_all(tools, units, ["none", a.mode], work, a.jobs, a.add_flag, a.timeout)
        rep = analyze(tools, units, a.mode, results, root, work, trace=not a.no_trace, jobs=a.jobs, timeout=a.timeout)
        rep = dict({"schema": "lostloops-1", "tool": "lostloops " + VERSION, "mode": a.mode, "root": root,
                    "toolchain": {"clang": tools.version, "command": tools.clang,
                                  "objdump": tools.objdump, "symbolizer": tools.symbolizer},
                    "flags_added": ["-stdlib=libc++", "-D_LIBCPP_HARDENING_MODE=<NONE or %s>" % MODES[a.mode],
                                    "-fsave-optimization-record", "-foptimization-record-passes=loop-vectorize",
                                    "-foptimization-record-file=<temp>", "-c", "-o", "<temp object>"] + a.add_flag,
                    "flags_removed_from_your_commands": sorted({x for u in units for x in clean_args(u["args"])[1]
                                                                if x.startswith("-")}),
                    "no_opt_level": [norm_file(u["file"], root)[0] for u in units
                                     if not has_opt_level(clean_args(u["args"])[0] + a.add_flag)],
                    "example_command": " ".join(shlex.quote(x) for x in results[(0, a.mode)]["cmd"]),
                    "disclaimer": DISCLAIMER, "limits": LIMITS}, **rep)
        write_report(rep, a.out)
        sys.stdout.write(render_text(rep, a.top))
    finally:
        if a.keep_work:
            print("lostloops: work files kept in %s" % work, file=sys.stderr)
        else:
            shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
