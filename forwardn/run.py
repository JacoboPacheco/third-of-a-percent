#!/usr/bin/env python3
"""Compile-only sweep: do forward loops with a variable bound lose SIMD under libc++ hardening? See PLAN.md.

    python forwardn/run.py                # fetch what forwardn/cache/ lacks from Compiler Explorer, then analyse
    python forwardn/run.py --offline      # analyse the cache only; never touches the network
    python forwardn/run.py --dry-run      # list the requests that would be sent
    python forwardn/run.py --refresh      # ignore the cache and re-fetch

Compiler Explorer public API (godbolt.org), the clang ids of ce-sweep/cesweep.py for x86-64 (-O2 and -O3) and
AArch64 (-O2), `-stdlib=libc++`, the hardening macro that fits each library version, NONE (off) against hardened
(on). For every function in source.cpp the script records clang's loop-vectorize remark at the function's
// LOOP line and counts traps and vector instructions in the function's assembly. No timing is done.
Reuses ce-sweep/cesweep.py (request body, cache format, remark parser) and ce-sweep/sweep.py (polite spacing, a
full stop on HTTP 429/403). Writes results.json and RESULTS.generated.md next to this file.
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

CACHE = os.path.join(HERE, "cache")
FUNC_NAME = re.compile(r"\b(fwn_\w+|FwnWork::run)\(")
FUNC_LABEL = re.compile(r'^"?(fwn_\w+|FwnWork::run)\(')
# (target, opt) pairs, in the order of the tables
CONFIGS = [("x86-64", "-O2"), ("x86-64", "-O3"), ("aarch64", "-O2")]
CONTROLS = ("sum_size", "scale_size")
REDUCTIONS_N = ("sum_n_size_t", "sum_n_int", "sum_n_u32", "sum_n_i64", "sum_int_size")
WRITES_N = ("scale_n_size_t", "scale_n_int", "inplace_n", "fill_n", "dot_n")
MEMBER_BOUND = ("sum_member", "sum_ptr_member", "member_write")
OLD_CLANG = ("16.0.0", "17.0.1")
NEW_CLANG = ("22.1.0", "23.1.0", "trunk")


def short(fn):
    """fwn_sum_size -> sum_size; FwnWork::run -> member_write"""
    return "member_write" if fn == "FwnWork::run" else fn[len("fwn_"):]


def loop_lines(src):
    cur, out = None, {}
    for i, ln in enumerate(src.splitlines(), 1):
        m = FUNC_NAME.search(ln)
        if m and ln.startswith("__attribute__"):
            cur = m.group(1)
        if "// LOOP" in ln and cur:
            out[cur] = i
    return out


def builds():
    """The compiles: every clang id of ce-sweep for the configs above, NONE and hardened."""
    out = []
    groups = [(cs.CLANG_X86, ["x86-64"]), (cs.CLANG_ARM, ["aarch64"])]
    for compilers, targets in groups:
        for cid, version in compilers:
            for target, opt in CONFIGS:
                if target not in targets:
                    continue
                for mode in cs.MODES:
                    hflag, macro = cs.hardening_flags("clang", version, mode)
                    parts = [opt, cs.TARGETS[target], "-std=c++20", "-stdlib=libc++", hflag, cs.CLANG_REMARKS]
                    out.append({"compiler_id": cid, "family": "clang", "version": version, "target": target,
                                "opt": opt, "mode": mode, "macro": macro,
                                "flags": " ".join(p for p in parts if p)})
    return out


def split_funcs(lines):
    out, cur = {}, None
    for ln in lines:
        if ln and not ln[0].isspace() and ln.rstrip().endswith(":") and not ln.startswith("."):
            m = FUNC_LABEL.match(ln)
            cur = m.group(1) if m else None
            if cur:
                out.setdefault(cur, [])
            continue
        if cur:
            out[cur].append(ln)
    return out


def fetch(builds_, source, refresh, dry, cap):
    os.makedirs(CACHE, exist_ok=True)
    sweep.CACHE = CACHE
    todo = [b for b in builds_ if refresh or not os.path.exists(os.path.join(CACHE, cs.cache_name(b)))]
    print("%d of %d builds to fetch" % (len(todo), len(builds_)))
    sent = 0
    for b in todo:
        body = cs.request_body(source, b["flags"])
        if dry:
            print(b["compiler_id"], b["flags"])
            continue
        if sent >= cap:
            print("cap reached")
            break
        try:
            resp = sweep.post_retrying("/compiler/%s/compile" % b["compiler_id"], body)
        except sweep.Stop as e:
            raise SystemExit("BLOCKED: " + str(e))
        except (urllib.error.URLError, OSError) as e:
            raise SystemExit("BLOCKED: Compiler Explorer unreachable: %s" % e)
        sent += 1
        if resp is None:
            print("   skipped %s (server errors)" % cs.cache_name(b))
            continue
        rec = {"build": b, "url": sweep.API + "/compiler/%s/compile" % b["compiler_id"],
               "request_sha256": cs.request_sha(b["compiler_id"], body),
               "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "response": {k: resp.get(k) for k in ("code", "stderr", "asm", "compilationOptions", "okToCache")}}
        cs.save_cache(os.path.join(CACHE, cs.cache_name(b)), rec)
        print("%3d %-18s %-8s %s %-8s code=%s asm=%d" % (sent, b["compiler_id"], b["target"], b["opt"], b["mode"],
                                                         resp.get("code"), len(resp.get("asm") or [])))
    print("sent %d requests" % sent)


def analyse_build(b, resp, ll):
    err = cs.stderr_text(resp)
    funcs = split_funcs(cs.asm_lines(resp))
    arch = cs.arch_of(b["target"])
    out = {}
    for fn, line in ll.items():
        v = cs.vectorization(err, line, "clang")
        c = cs.asm_counts(funcs.get(fn, []), arch)
        out[short(fn)] = {"vectorized": v["vectorized"], "width": v["width"], "interleave": v["interleave"],
                          "remarks": v["remarks"][:3], "traps": c["traps"] + c["abort_calls"],
                          "simd_instr": c["simd_instr"], "instructions": c["instructions"]}
    return out


def word(n, h):
    nv, hv = n["vectorized"] is True, h["vectorized"] is True
    if nv and not hv:
        return "lost"
    if nv and hv:
        return "kept" if (n["width"], n["interleave"]) == (h["width"], h["interleave"]) else "narrower"
    if hv:
        return "gained"
    return "scalar in both"


def collect(builds_, ll):
    """{(cid, target, opt): {"version", "functions": {short: {"none":..., "hardened":..., "word":...}}, "macro_effective"}}"""
    by_key = {}
    for b in builds_:
        path = os.path.join(CACHE, cs.cache_name(b))
        if not os.path.exists(path):
            continue
        rec = cs.load_cache(path)
        by_key[(b["compiler_id"], b["target"], b["opt"], b["mode"])] = (b, rec["response"])
    cells = {}
    for (cid, target, opt, mode), (b, resp) in sorted(by_key.items()):
        if mode != "none":
            continue
        hb, hresp = by_key.get((cid, target, opt, "hardened"), (None, None))
        if hb is None:
            continue
        ok = cs.compile_ok(resp) and cs.compile_ok(hresp)
        entry = {"version": b["version"], "compiled": ok, "macro_none": b["macro"], "macro_hardened": hb["macro"],
                 "flags_none": b["flags"], "flags_hardened": hb["flags"], "functions": {}}
        if ok:
            an, ah = analyse_build(b, resp, ll), analyse_build(hb, hresp, ll)
            for fn in an:
                entry["functions"][fn] = {"none": an[fn], "hardened": ah[fn], "word": word(an[fn], ah[fn])}
            entry["macro_effective"] = sum(x["traps"] for x in ah.values()) > sum(x["traps"] for x in an.values())
        cells[(cid, target, opt)] = entry
    return cells


def words_at(cells, target, opt, version):
    for (cid, t, o), e in cells.items():
        if t == target and o == opt and e["version"] == version and e["compiled"]:
            return {fn: v["word"] for fn, v in e["functions"].items()}
    return None


def evaluate(cells):
    """The six predictions of PLAN.md, each as {"holds": bool/None, "detail": str}. None = not enough cells."""
    out = {}
    versions = sorted({e["version"] for e in cells.values()})

    # 1. variable-bound reductions: lost on clang 16 and 17, kept on 22, 23, trunk (x86-64 -O2)
    bad, missing = [], []
    for fn in REDUCTIONS_N:
        for v in OLD_CLANG + NEW_CLANG:
            w = words_at(cells, "x86-64", "-O2", v)
            if w is None or fn not in w:
                missing.append((fn, v))
                continue
            want_lost = v in OLD_CLANG
            ok = (w[fn] == "lost") if want_lost else (w[fn] in ("kept", "narrower"))
            if not ok:
                bad.append("%s on clang %s: %s" % (fn, v, w[fn]))
    out["1"] = {"holds": None if missing and not bad else not bad,
                "detail": "; ".join(bad) if bad else ("no cell contradicts it" if not missing else "missing cells")}

    # 2. aarch64 = x86-64 at -O2 in >= 90% of the (function, version) cells; -O3 = -O2 on x86-64 in >= 90%
    def agreement(t1, o1, t2, o2):
        same = total = 0
        for v in versions:
            a, b = words_at(cells, t1, o1, v), words_at(cells, t2, o2, v)
            if a is None or b is None:
                continue
            for fn in a:
                if fn in b:
                    total += 1
                    same += a[fn] == b[fn]
        return same, total
    s1, t1 = agreement("aarch64", "-O2", "x86-64", "-O2")
    s2, t2 = agreement("x86-64", "-O3", "x86-64", "-O2")
    out["2"] = {"holds": (t1 > 0 and t2 > 0 and s1 >= 0.9 * t1 and s2 >= 0.9 * t2) if (t1 and t2) else None,
                "detail": "aarch64 -O2 agrees with x86-64 -O2 in %d of %d cells; x86-64 -O3 agrees with -O2 in %d of %d"
                          % (s1, t1, s2, t2)}

    # 3. writes bounded by n are never lost where the control scale_size is not lost (any config)
    bad = []
    for (cid, t, o), e in sorted(cells.items()):
        if not e["compiled"]:
            continue
        w = {fn: v["word"] for fn, v in e["functions"].items()}
        if w.get("scale_size") in ("kept", "narrower"):
            bad += ["%s %s %s clang %s: %s" % (fn, t, o, e["version"], w[fn]) for fn in WRITES_N
                    if w.get(fn) == "lost"]
    out["3"] = {"holds": not bad, "detail": "; ".join(bad) if bad else "no write bounded by n is lost where the control is kept"}

    # 4. member and pointer bounds: not vectorized in either build, everywhere
    bad = []
    for (cid, t, o), e in sorted(cells.items()):
        if not e["compiled"]:
            continue
        for fn in MEMBER_BOUND:
            f = e["functions"].get(fn)
            if f and (f["none"]["vectorized"] is True or f["hardened"]["vectorized"] is True):
                bad.append("%s %s %s clang %s: %s" % (fn, t, o, e["version"], f["word"]))
    out["4"] = {"holds": not bad, "detail": "; ".join(bad) if bad else "scalar in both builds in every cell"}

    # 5. range-for control: kept (same width and interleave) everywhere
    bad = [("%s %s clang %s: %s" % (t, o, e["version"], e["functions"]["rangefor"]["word"]))
           for (cid, t, o), e in sorted(cells.items())
           if e["compiled"] and e["functions"]["rangefor"]["word"] != "kept"]
    out["5"] = {"holds": not bad, "detail": "; ".join(bad) if bad else "kept with equal width and interleave in every cell"}

    # 6. sum_size and scale_size vectorized in both builds everywhere
    bad = []
    for (cid, t, o), e in sorted(cells.items()):
        if not e["compiled"]:
            continue
        for fn in CONTROLS:
            if e["functions"][fn]["word"] not in ("kept", "narrower"):
                bad.append("%s %s %s clang %s: %s" % (fn, t, o, e["version"], e["functions"][fn]["word"]))
    out["6"] = {"holds": not bad, "detail": "; ".join(bad) if bad else "vectorized in both builds in every cell"}
    return out


FUNCTION_ORDER = ["sum_size", "sum_n_size_t", "sum_n_int", "sum_n_u32", "sum_n_i64", "sum_int_size", "sum_member",
                  "sum_ptr_member", "dot_n", "scale_size", "scale_n_size_t", "scale_n_int", "scale_offset",
                  "two_stores", "member_write", "inplace_n", "fill_n", "rangefor"]


def version_key(v):
    return (99, 0) if v == "trunk" else tuple(int(x) for x in v.split(".")[:2])


def render(cells, preds):
    out = ["Compile-only. Compiler Explorer clang ids of `ce-sweep/cesweep.py`, `-stdlib=libc++`, hardening off against on."
           " Words: lost = vectorized with checks off and not with them on; narrower = vectorized in both builds with a"
           " different width or interleave count; kept = vectorized in both builds, same; scalar = not vectorized in either.", ""]
    ineffective = [("%s %s %s" % k) for k, e in sorted(cells.items()) if e["compiled"] and not e.get("macro_effective")]
    uncompiled = [("%s %s %s" % k) for k, e in sorted(cells.items()) if not e["compiled"]]
    out.append("Hardening macro took effect (more traps with it on) in %d of %d compile pairs%s."
               % (sum(1 for e in cells.values() if e.get("macro_effective")), len(cells),
                  "; no effect: " + ", ".join(ineffective) if ineffective else ""))
    if uncompiled:
        out.append("Did not compile: " + ", ".join(uncompiled) + ".")
    out.append("")
    for target, opt in CONFIGS:
        ks = sorted([(e["version"], k) for k, e in cells.items() if k[1] == target and k[2] == opt and e["compiled"]],
                    key=lambda x: version_key(x[0]))
        if not ks:
            continue
        out += ["### %s %s" % (target, opt), "",
                "| function | " + " | ".join("clang " + v for v, _ in ks) + " |",
                "|---|" + "---|" * len(ks)]
        for fn in FUNCTION_ORDER:
            row = []
            for v, k in ks:
                f = cells[k]["functions"].get(fn)
                row.append(f["word"] if f else "")
            out.append("| `%s` | " % fn + " | ".join(row) + " |")
        out.append("")
    out += ["### Predictions of PLAN.md", "", "| # | holds | detail |", "|---|---|---|"]
    for n in sorted(preds):
        p = preds[n]
        out.append("| %s | %s | %s |" % (n, {True: "yes", False: "NO", None: "not enough cells"}[p["holds"]],
                                         p["detail"].replace("|", "/")[:600]))
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--max", type=int, default=80, help="request cap for this run")
    a = ap.parse_args()
    with open(os.path.join(HERE, "source.cpp"), encoding="utf-8") as f:
        source = f.read()
    ll = loop_lines(source)
    bs = builds()
    if not a.offline:
        fetch(bs, source, a.refresh, a.dry_run, a.max)
    if a.dry_run:
        return
    cells = collect(bs, ll)
    if not cells:
        raise SystemExit("no cached compile found in %s (run without --offline)" % CACHE)
    preds = evaluate(cells)
    rec = {"plan": "forwardn/PLAN.md", "functions": {short(k): v for k, v in ll.items()},
           "cells": [dict(e, compiler_id=k[0], target=k[1], opt=k[2]) for k, e in sorted(cells.items())],
           "predictions": preds}
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write("\n")
    text = render(cells, preds)
    with open(os.path.join(HERE, "RESULTS.generated.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
