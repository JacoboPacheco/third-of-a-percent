#!/usr/bin/env python3
"""Compile-only check: do loop-shape variants lose SIMD under libc++ FAST? One command:

    python variants/run.py            # uses variants/cache/ when it matches, else asks Compiler Explorer
    python variants/run.py --refresh  # ignore the cache and re-fetch

Compiler Explorer public API (godbolt.org), clang 18.1.0 (id clang1810; the only 18.x release listed),
x86-64 baseline (SSE2), -O2 -std=c++20 -stdlib=libc++, hardening NONE vs FAST. For every function in
source.cpp the script records clang's loop-vectorize remark at the function's // LOOP line and counts
packed-SSE instructions in the function's assembly. No timing is done. Reuses ce-sweep/cesweep.py
(request body, cache format, remark parser) and ce-sweep/sweep.py (polite request spacing).
Writes results.json and RESULTS.generated.md next to this file.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "ce-sweep"))
import cesweep as cs  # noqa: E402
import sweep  # noqa: E402

COMPILER = "clang1810"
OPT = "-O2 -std=c++20 -march=x86-64 -stdlib=libc++"
MODES = {"NONE": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE",
         "FAST": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"}
CACHE = os.path.join(HERE, "cache")
PACKED = re.compile(r"^\s*v?(paddd|paddq|pmulld|pmuludq|pshufd|pshufb|punpck\w+|pmovzx\w+|pmaddwd|psrl\w+|psll\w+|"
                    r"movdqu|movdqa|movups|movaps|pxor|pand|pandn|por|pcmp\w+)\b")
FUNC = re.compile(r'^"?(var_\w+?)\(')
SHAPES = [("rev", "reverse"), ("stride2", "stride-2"), ("matmul", "matrix multiply (inner loop)")]


def loop_lines(src):
    out, cur = {}, None
    for i, ln in enumerate(src.splitlines(), 1):
        m = re.search(r"\b(var_\w+)\(", ln)
        if m and ln.startswith("__attribute__"):
            cur = m.group(1)
        if "// LOOP" in ln and cur:
            out[cur] = i
    return out


def split_funcs(lines):
    out, cur = {}, None
    for ln in lines:
        if ln and not ln[0].isspace() and ln.rstrip().endswith(":") and not ln.startswith("."):
            m = FUNC.match(ln)
            cur = m.group(1) if m else None
            if cur:
                out.setdefault(cur, [])
            continue
        if cur:
            out[cur].append(ln)
    return out


def fetch(src, mode, refresh):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, "%s_%s.json.gz" % (COMPILER, mode))
    flags = "%s %s %s" % (OPT, MODES[mode], cs.CLANG_REMARKS)
    body = cs.request_body(src, flags)
    sha = cs.request_sha(COMPILER, body)
    if os.path.exists(path) and not refresh:
        rec = cs.load_cache(path)
        if rec.get("request_sha256") == sha:
            return rec["response"], flags
    sweep.CACHE = CACHE
    resp = sweep.post_retrying("/compiler/%s/compile" % COMPILER, body)
    if resp is None:
        raise SystemExit("BLOCKED: Compiler Explorer unreachable (server errors after retries)")
    cs.save_cache(path, {"build": mode, "request_sha256": sha, "flags": flags,
                         "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "response": resp})
    return resp, flags


def describe(v):
    if v["vectorized"] is True:
        return "vectorized (width %s, interleave %s)" % (v["width"], v["interleave"])
    if v["vectorized"] is False:
        return "NOT vectorized: " + "; ".join(r[:110] for r in v["remarks"][:2])
    return "no loop-vectorize remark"


def verdict(r):
    n, f = r["NONE"], r["FAST"]
    if n["vectorized"] and not f["vectorized"]:
        return "LOST"
    if n["vectorized"] and f["vectorized"]:
        return "kept"
    if not n["vectorized"] and not f["vectorized"]:
        return "scalar in both"
    return "gained"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(HERE, "source.cpp"), encoding="utf-8") as f:
        src = f.read()
    ll = loop_lines(src)
    res, flags_used = {}, {}
    try:
        for mode in MODES:
            resp, flags_used[mode] = fetch(src, mode, a.refresh)
            if not cs.compile_ok(resp):
                raise SystemExit("compile failed (%s): %s" % (mode, cs.stderr_text(resp)[:800]))
            err = cs.stderr_text(resp)
            funcs = split_funcs(cs.asm_lines(resp))
            for fn, line in ll.items():
                v = cs.vectorization(err, line, "clang")
                lines = funcs.get(fn, [])
                c = cs.asm_counts(lines, "x86")
                res.setdefault(fn, {})[mode] = dict(
                    v, packed=sum(1 for x in lines if PACKED.search(x)), vreg=c["simd_instr"],
                    traps=c["traps"], abort_calls=c["abort_calls"], instructions=c["instructions"])
    except sweep.Stop as e:
        raise SystemExit("BLOCKED: " + str(e))
    except (urllib.error.URLError, OSError) as e:
        raise SystemExit("BLOCKED: Compiler Explorer unreachable: %s" % e)
    write(res, flags_used)


def write(res, flags):
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump({"compiler": COMPILER, "flags": flags, "results": res}, f, indent=1, sort_keys=True)
    out = ["Compile-only. Compiler Explorer `%s` (clang 18.1.0, x86-64 baseline SSE2), `%s`." % (COMPILER, OPT),
           "NONE = `%s`, FAST = `%s`." % (MODES["NONE"], MODES["FAST"]), ""]
    for key, title in SHAPES:
        out += ["### " + title, "",
                "| variant | build | loop-vectorize remark | packed SSE | ud2/abort | NONE to FAST |",
                "|---|---|---|---|---|---|"]
        for fn in sorted(res, key=lambda s: (s != "var_%s_ctrl" % key, s)):
            if not fn.startswith("var_%s_" % key):
                continue
            for mode in ("NONE", "FAST"):
                r = res[fn][mode]
                out.append("| `%s` | %s | %s | %d | %d | %s |" % (
                    fn[4:], mode, describe(r).replace("|", "/"), r["packed"], r["traps"] + r["abort_calls"],
                    verdict(res[fn]) if mode == "FAST" else ""))
        out.append("")
    text = "\n".join(out)
    with open(os.path.join(HERE, "RESULTS.generated.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
