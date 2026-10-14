"""Shared pieces of the Compiler Explorer sweep: the source, the build matrix, the request, the parsers.

Nothing here touches the network. `sweep.py` sends the requests and caches the answers;
`check.py` rebuilds every result from the cache offline with the same functions.

One request compiles all 8 loop functions (taken verbatim from kernels/kNN_*.cpp) in one
translation unit, so one compile answers 8 cells. Each function is `noinline` and independent, so
sharing a file does not change how any loop is compiled.
"""
import gzip
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
KERNELS = ["k01_sum_fwd", "k02_add_fwd", "k03_stencil", "k04_rev", "k05_stride2", "k06_gather",
           "k07_hist", "k08_matmul"]
# The project's known result (clang 18, libc++ FAST, x86-64 baseline, -O2): audit/out-asm.txt and
# the siblings reference row. The sweep's control must reproduce it.
CONTROL_LOST = ["k04_rev", "k05_stride2", "k08_matmul"]

HEADER = ("// The 8 loop functions of kernels/kNN_*.cpp, copied verbatim, in one file for Compiler Explorer.\n"
          "// Each loop carries a // LOOP comment; the compiler's remarks at that line decide the cell.\n"
          "#include <cstddef>\n#include <cstdint>\n#include <vector>\n")


def extract_kernel(text, name):
    """The `__attribute__((noinline)) ... kern_<name>(...) { ... }` function from a kernel source."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("__attribute__((noinline))") and ("kern_" + name) in ln:
            start = i
            break
    if start is None:
        raise ValueError("no kern_%s in the source" % name)
    for j in range(start, len(lines)):
        if lines[j] == "}":
            return "\n".join(lines[start:j + 1]) + "\n"
    raise ValueError("kern_%s has no closing brace at column 0" % name)


def build_source(kernel_dir=None):
    kernel_dir = kernel_dir or os.path.join(REPO, "kernels")
    parts = [HEADER]
    for k in KERNELS:
        with open(os.path.join(kernel_dir, k + ".cpp"), encoding="utf-8") as f:
            parts.append("\n" + extract_kernel(f.read(), k))
    return "".join(parts)


def single_kernel_source(kernel_dir, name):
    with open(os.path.join(kernel_dir or os.path.join(REPO, "kernels"), name + ".cpp"), encoding="utf-8") as f:
        return HEADER + "\n" + extract_kernel(f.read(), name)


def loop_lines(source):
    """{kernel: 1-based line of its // LOOP comment} in the combined source."""
    out, current = {}, None
    for i, ln in enumerate(source.splitlines(), 1):
        m = re.search(r"\bkern_(k\d\d_\w+)\(", ln)
        if m and ln.startswith("__attribute__"):
            current = m.group(1)
        if "// LOOP" in ln and current:
            out[current] = i
    missing = [k for k in KERNELS if k not in out]
    if missing:
        raise ValueError("no // LOOP line for %s" % missing)
    return out


# ---------------------------------------------------------------- the build matrix
# Compiler Explorer ids, read from /api/compilers/c++ (cache/compilers-cpp.json.gz) on 2026-10-12.
CLANG_X86 = [("clang1600", "16.0.0"), ("clang1701", "17.0.1"), ("clang1810", "18.1.0"), ("clang1910", "19.1.0"),
             ("clang2010", "20.1.0"), ("clang2110", "21.1.0"), ("clang2210", "22.1.0"), ("clang2310", "23.1.0"),
             ("clang_trunk", "trunk")]
CLANG_ARM = [("armv8-clang1600", "16.0.0"), ("armv8-clang1701", "17.0.1"), ("armv8-clang1810", "18.1.0"),
             ("armv8-clang1910", "19.1.0"), ("armv8-clang2010", "20.1.0"), ("armv8-clang2110", "21.1.0"),
             ("armv8-clang2210", "22.1.0"), ("armv8-clang2310", "23.1.0"), ("armv8-clang-trunk", "trunk")]
GCC_X86 = [("g125", "12.5"), ("g134", "13.4"), ("g144", "14.4"), ("g153", "15.3"), ("g162", "16.2")]
GCC_ARM = [("arm64g1250", "12.5.0"), ("arm64g1340", "13.4.0"), ("arm64g1430", "14.3.0"), ("arm64g1520", "15.2.0"),
           ("arm64g1610", "16.1.0")]

TARGETS = {"x86-64": "-march=x86-64", "x86-64-v3": "-march=x86-64-v3", "aarch64": ""}
OPTS = ["-O2", "-O3"]
MODES = ["none", "hardened"]

CLANG_REMARKS = "-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize"
GCC_REMARKS = "-fopt-info-vec-optimized"


def libcxx_major(version):
    return 99 if version == "trunk" else int(version.split(".")[0])


def hardening_flags(family, version, mode):
    """The macro that turns the library's bounds check on or off, per library version.

    libc++ 18 and later: _LIBCPP_HARDENING_MODE (NONE / FAST).
    libc++ 17: _LIBCPP_ENABLE_HARDENED_MODE (the 17 name of the same mode).
    libc++ 16: _LIBCPP_ENABLE_ASSERTIONS (all assertions; no separate fast mode existed).
    libstdc++: _GLIBCXX_ASSERTIONS (on or absent).
    """
    if family == "gcc":
        return ("-D_GLIBCXX_ASSERTIONS", "_GLIBCXX_ASSERTIONS") if mode == "hardened" else ("", "none")
    v = libcxx_major(version)
    if v >= 18:
        m = "_LIBCPP_HARDENING_MODE_FAST" if mode == "hardened" else "_LIBCPP_HARDENING_MODE_NONE"
        return "-D_LIBCPP_HARDENING_MODE=" + m, m
    if v == 17:
        return "-D_LIBCPP_ENABLE_HARDENED_MODE=%d" % (mode == "hardened"), \
            "_LIBCPP_ENABLE_HARDENED_MODE=%d" % (mode == "hardened")
    return "-D_LIBCPP_ENABLE_ASSERTIONS=%d" % (mode == "hardened"), \
        "_LIBCPP_ENABLE_ASSERTIONS=%d" % (mode == "hardened")


def matrix():
    """Every build as a dict: compiler id, family, version, target, opt, mode, flags."""
    out = []
    groups = [("clang", CLANG_X86, ["x86-64", "x86-64-v3"]), ("clang", CLANG_ARM, ["aarch64"]),
              ("gcc", GCC_X86, ["x86-64", "x86-64-v3"]), ("gcc", GCC_ARM, ["aarch64"])]
    for family, compilers, targets in groups:
        for cid, version in compilers:
            for target in targets:
                for opt in OPTS:
                    for mode in MODES:
                        hflag, macro = hardening_flags(family, version, mode)
                        parts = [opt, TARGETS[target]]
                        if family == "clang":
                            parts += ["-stdlib=libc++", hflag, CLANG_REMARKS]
                        else:
                            parts += [hflag, GCC_REMARKS]
                        flags = " ".join(p for p in parts if p)
                        out.append({"compiler_id": cid, "family": family, "version": version, "target": target,
                                    "opt": opt, "mode": mode, "macro": macro, "flags": flags})
    return out


FILTERS = {"binary": False, "binaryObject": False, "commentOnly": True, "demangle": True, "directives": True,
           "execute": False, "intel": True, "labels": True, "libraryCode": True, "trim": False,
           "debugCalls": False}


def request_body(source, flags):
    return {"source": source, "lang": "c++", "allowStoreCodeDebug": True,
            "options": {"userArguments": flags,
                        "compilerOptions": {"skipAsm": False, "executorRequest": False},
                        "filters": FILTERS, "tools": [], "libraries": []}}


def request_sha(compiler_id, body):
    blob = json.dumps({"compiler": compiler_id, "body": body}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def cache_name(build):
    return "%s__%s__%s__%s.json.gz" % (build["compiler_id"], build["target"], build["opt"].lstrip("-"), build["mode"])


# ---------------------------------------------------------------- parsers
_CLANG_VEC = re.compile(r"vectorized loop \(vectorization width: ([^,]+), interleaved count: (\d+)\)")
_GCC_VEC = re.compile(r"optimized: loop vectorized using (\d+) byte vectors")


_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def stderr_text(response):
    """The compiler's stderr as plain text (Compiler Explorer adds terminal colour codes)."""
    return "\n".join(_ANSI.sub("", x.get("text", "")) for x in (response.get("stderr") or []))


def asm_lines(response):
    return [x.get("text", "") for x in response.get("asm", [])]


def remarks_at(text, line):
    """Remark messages at <source>:line: (Compiler Explorer names the file <source>)."""
    pat = re.compile(r"<source>:%d:\d+: (?:remark|optimized|missed|note): ?(.*)$" % line)
    out = []
    for ln in text.splitlines():
        m = pat.search(ln)
        if m:
            # keep the kind word for GCC lines ("optimized: loop vectorized ...")
            kind = re.search(r"<source>:%d:\d+: (remark|optimized|missed|note):" % line, ln).group(1)
            msg = m.group(1).strip()
            out.append(msg if kind == "remark" else "%s: %s" % (kind, msg))
    return out


def vectorization(text, line, family):
    """{"vectorized": True/False/None, "width": .., "interleave": .., "vector_bytes": .., "remarks": [..]}.

    clang: True on a "vectorized loop" remark at the line, False when only other loop-vectorize
    remarks are there, None when clang said nothing about the line (the project's harness/remarks.py rule).
    GCC (-fopt-info-vec-optimized prints successes only): True on "loop vectorized using N byte vectors"
    at the line, else False.
    """
    msgs = remarks_at(text, line)
    res = {"vectorized": None, "width": None, "interleave": None, "vector_bytes": None, "remarks": msgs}
    if family == "clang":
        for msg in msgs:
            m = _CLANG_VEC.search(msg)
            if m:
                res.update(vectorized=True, width=m.group(1), interleave=int(m.group(2)))
        if res["vectorized"] is None and msgs:
            res["vectorized"] = False
        if res["width"] is not None and res["width"].isdigit():
            res["width"] = int(res["width"])
    else:
        best = None
        for msg in msgs:
            m = _GCC_VEC.search(msg)
            if m and "epilogue" not in msg:
                best = int(m.group(1)) if best is None else max(best, int(m.group(1)))
        res["vectorized"] = best is not None
        res["vector_bytes"] = best
    return res


_FUNC_LABEL = re.compile(r'^"?(kern_(k\d\d_\w+?))\(')  # GCC 16 quotes demangled labels
_TRAP = {"x86": re.compile(r"^\s*ud2\b"), "arm": re.compile(r"^\s*(brk\s+#0x1|udf\b)")}
# A call or jump into a check's failure path: libc++ 16/17 call __libcpp_verbose_abort; libstdc++ calls
# __glibcxx_assert_fail (13+), __replacement_assert or abort, and GCC often outlines that call into
# `operator[](...) (.part.0)` / `[clone .part.0]`, which is then the call seen in the kernel.
_ABORT_CALL = re.compile(r"^\s*(call|jmp|bl|b)\s+.*(__libcpp_verbose_abort|__glibcxx_assert_fail|"
                         r"__replacement_assert|\babort\b|operator\[\].*\.part\.)")
_X86_VREG = re.compile(r"\b[xyz]mm\d+\b")
_X86_SCALAR_MOV = re.compile(r"^\s*v?(movd|movq|cvt\w*|movs[sd]|ucomis[sd])\b")
_ARM_VREG = re.compile(r"\bv\d+\.\d*[bhsd]\b|\bq\d+\b")


def split_functions(lines):
    """{kernel: [asm lines]} for each kern_* function (cold clones such as `[clone .cold]` included)."""
    out, current = {}, None
    for ln in lines:
        if ln and not ln[0].isspace() and ln.rstrip().endswith(":") and not ln.startswith("."):
            m = _FUNC_LABEL.match(ln)
            current = m.group(2) if m else None
            if current:
                out.setdefault(current, [])
            continue
        if current:
            out[current].append(ln)
    return out


def asm_counts(lines, arch):
    """traps (ud2 / brk #0x1), calls to an abort or assertion handler, and vector-register instructions."""
    traps = sum(1 for ln in lines if _TRAP[arch].search(ln))
    aborts = sum(1 for ln in lines if _ABORT_CALL.search(ln))
    if arch == "x86":
        simd = sum(1 for ln in lines if _X86_VREG.search(ln) and not _X86_SCALAR_MOV.search(ln))
    else:
        simd = sum(1 for ln in lines if _ARM_VREG.search(ln))
    instr = sum(1 for ln in lines if ln.strip() and not ln.strip().endswith(":"))
    return {"traps": traps, "abort_calls": aborts, "simd_instr": simd, "instructions": instr}


def arch_of(target):
    return "arm" if target == "aarch64" else "x86"


def analyse(build, response, source):
    """Per-kernel facts for one compile: vectorization from the remarks, counts from the asm."""
    lines = loop_lines(source)
    err = stderr_text(response)
    funcs = split_functions(asm_lines(response))
    out = {}
    for k in KERNELS:
        v = vectorization(err, lines[k], build["family"])
        c = asm_counts(funcs.get(k, []), arch_of(build["target"])) if k in funcs else None
        out[k] = dict(v, asm=c)
    return out


def compile_ok(response):
    return response.get("code") == 0 and bool(response.get("asm"))


def cells(builds_with_responses, source):
    """Pair NONE and hardened builds into cells (compiler, target, opt, kernel).

    lost = vectorized in the unhardened build and not in the hardened build (the project's definition).
    """
    by_key = {}
    for b, resp in builds_with_responses:
        by_key[(b["compiler_id"], b["target"], b["opt"], b["mode"])] = (b, resp)
    out = []
    for (cid, target, opt, mode), (b, resp) in sorted(by_key.items()):
        if mode != "none":
            continue
        hb, hresp = by_key.get((cid, target, opt, "hardened"), (None, None))
        if hb is None:
            continue
        ok = compile_ok(resp) and compile_ok(hresp)
        an_n = analyse(b, resp, source) if compile_ok(resp) else {}
        an_h = analyse(hb, hresp, source) if compile_ok(hresp) else {}
        for k in KERNELS:
            n, h = an_n.get(k), an_h.get(k)
            if ok and n["vectorized"] is not None and h["vectorized"] is not None:
                lost = bool(n["vectorized"] and not h["vectorized"])
            else:
                lost = None
            out.append({
                "compiler_id": cid, "family": b["family"], "version": b["version"], "target": target, "opt": opt,
                "kernel": k, "macro_none": b["macro"], "macro_hardened": hb["macro"],
                "flags_none": b["flags"], "flags_hardened": hb["flags"],
                "compiled": ok,
                "none": _cell_side(n), "hardened": _cell_side(h), "lost": lost,
                "request_sha256_none": request_sha(cid, request_body(source, b["flags"])),
                "request_sha256_hardened": request_sha(cid, request_body(source, hb["flags"])),
                "cache_none": cache_name(b), "cache_hardened": cache_name(hb),
            })
    return out


def _cell_side(a):
    if a is None:
        return None
    return {"vectorized": a["vectorized"], "width": a["width"], "interleave": a["interleave"],
            "vector_bytes": a["vector_bytes"], "remarks": a["remarks"][:6], "asm": a["asm"]}


def load_cache(path):
    """One cached answer: {"build", "url", "request_sha256", "fetched_at", "response"} (gzip-compressed JSON)."""
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def save_cache(path, rec):
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump(rec, f, sort_keys=True)
