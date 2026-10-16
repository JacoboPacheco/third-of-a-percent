"""Offline checks of this folder. Sends no request.

    python verify.py

1. Every quotation in README.md written as a double-backtick span on a line that names one raw file
   (for example ``text`` next to raw/NAME.json) must occur in that raw answer (compiler messages, assembly,
   or the IR text of the pass pipeline), ignoring runs of white space.
2. sources/kernels.cpp still equals the functions in kernels/ (make_sources.py --check).
3. Numbers the README states are recomputed from raw/ and compared (the CHECKS below).
4. Every request in request-index.json that is not a repeat has its raw file, and the total is within the cap.
5. The statements of the README about the checks in the loops, the hand-written IR, the full-pipeline runs, the IR of
   the compilers, the debug output, the trunk build times and the number of requests are recomputed from raw/.
Exit status 0 when everything holds.
"""
import json
import os
import re
import subprocess
import sys

import ce
import excerpts
import experiments
import extract

HERE = ce.HERE
README = os.path.join(HERE, "README.md")
failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL", msg)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


_corpus = {}


def corpus(name):
    if name in _corpus:
        return _corpus[name]
    rec = ce.load(name)
    parts = [ce.stderr_text(rec), ce.stdout_text(rec), ce.asm_text(rec)]
    op = rec["response"].get("optPipelineOutput")
    if op:
        for fn, passes in op["results"].items():
            for e in passes:
                parts.append(e["name"])
                parts += excerpts.text_of(e["before"])
                parts += excerpts.text_of(e["after"])
    _corpus[name] = norm("\n".join(parts))
    return _corpus[name]


def readme_text():
    with open(README, encoding="utf-8") as f:
        return f.read()


def check_quotes():
    n = 0
    with open(README, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for i, ln in enumerate(lines, 1):
        spans = re.findall(r"``(.+?)``", ln)
        if not spans:
            continue
        files = sorted(set(re.findall(r"raw/([A-Za-z0-9_.-]+?)\.json", ln)))
        if len(files) != 1:
            fail("README line %d has quotations and %d raw files" % (i, len(files)))
            continue
        for q in spans:
            n += 1
            if norm(q) not in corpus(files[0]):
                fail("README line %d: not in raw/%s: %s" % (i, files[0], q[:90]))
    print("quotations checked: %d" % n)
    return n


def check_sources():
    r = subprocess.call([sys.executable, os.path.join(HERE, "make_sources.py"), "--check"])
    if r != 0:
        fail("sources/kernels.cpp differs from kernels/")
    r = subprocess.call([sys.executable, os.path.join(HERE, "make_s2_bound.py"), "--check"])
    if r != 0:
        fail("sources/handwritten/s2-bound.ll differs from what make_s2_bound.py writes")


def check_requests():
    with open(os.path.join(HERE, "request-index.json"), encoding="utf-8") as f:
        idx = json.load(f)
    if len(idx) > ce.MAX_REQUESTS:
        fail("%d requests, cap %d" % (len(idx), ce.MAX_REQUESTS))
    for e in experiments.all_experiments():
        if not os.path.exists(ce._path(e["name"])):
            fail("missing raw answer for experiment " + e["name"])
    for name, path in experiments.LISTINGS:
        if ce.load(name).get("path") != path:
            fail("raw/%s was made by another request than experiments.LISTINGS defines" % name)
    for e in experiments.all_experiments():
        rec = ce.load(e["name"])
        if rec["response"].get("code") != 0:
            fail("compiler exit code %s in %s" % (rec["response"].get("code"), e["name"]))
        # the saved answer is the answer to the request that experiments.py defines now
        with open(os.path.join(HERE, e["source_path"]), encoding="utf-8") as f:
            body = ce.request_body(f.read(), e["args"], e["compiler_options"], e.get("filters"), e.get("lang", "c++"))
        if ce.request_sha(e["compiler_id"], body) != rec.get("request_sha256"):
            fail("raw/%s was made by another request than experiments.py defines" % e["name"])
    known = {e["name"] for e in experiments.all_experiments()} | {n for n, _ in experiments.LISTINGS}
    for f in os.listdir(os.path.join(HERE, "raw")):
        if f.replace(".json.gz", "").replace(".json", "") not in known:
            fail("raw/%s belongs to no experiment of experiments.py" % f)
    print("requests sent in total: %d (cap %d)" % (len(idx), ce.MAX_REQUESTS))
    return len(idx)


def tally(name_e, name_a):
    blocks = excerpts.scev_blocks(name_e)
    rem = excerpts.remark_of(name_a)
    res = {"ok": 0, "bad": 0, "mismatch": 0}
    for sym, d in blocks.items():
        fn = excerpts.short_name(sym)
        computable = not (d["btc"] or "").startswith("Unpredictable")
        vec = rem[fn].startswith("vectorized")
        if computable and vec:
            res["ok"] += 1
        elif not computable and not vec:
            res["bad"] += 1
        else:
            res["mismatch"] += 1
    return res


def check_numbers():
    # SCEV against the vectorizer's decision, clang 18.1.0 FAST: kernels 5, variants 14, variants2 4, variants3 6 loops.
    total = {"ok": 0, "bad": 0, "mismatch": 0}
    for src in ("kernels", "variants", "variants2", "variants3"):
        t = tally("E-c18-%s-fast-scev" % src, "A-c18-%s-fast" % src)
        for k in total:
            total[k] += t[k]
        # "the backedge-taken count is computable" must be the same thing as "no exit is ***COULDNOTCOMPUTE***"
        for sym, d in excerpts.scev_blocks("E-c18-%s-fast-scev" % src).items():
            counted = not any("COULDNOTCOMPUTE" in c for _, c in d["exits"])
            if counted != (not (d["btc"] or "").startswith("Unpredictable")):
                fail("exit counts and backedge-taken count disagree for %s" % sym)
    expect = {"ok": 16, "bad": 13, "mismatch": 0}
    if total != expect:
        fail("SCEV tally on clang 18 FAST is %s, README says %s" % (total, expect))
    for short in ("c19", "c20", "ctrunk"):
        t = tally("E-%s-kernels-fast-scev" % short, "A-%s-kernels-fast" % short)
        if t != {"ok": 3, "bad": 2, "mismatch": 0}:
            fail("SCEV tally %s kernels FAST is %s" % (short, t))
    t = tally("E-c18-kernels-none-scev", "A-c18-kernels-none")
    if t != {"ok": 5, "bad": 0, "mismatch": 0}:
        fail("SCEV tally on clang 18 NONE is %s" % t)
    # the opt experiment: which functions get a vector.body
    for short in ("c18", "c20", "ctrunk"):
        a = excerpts.vector_body_counts("F-%s-kernels-fast-lv-only" % short)
        b = excerpts.vector_body_counts("F-%s-kernels-fast-unswitch-then-lv" % short)
        want_a = {"kern_k01_sum_fwd": 1, "kern_k02_add_fwd": 1, "kern_k03_stencil": 1, "kern_k04_rev": 0, "kern_k05_stride2": 0}
        want_b = dict(want_a, kern_k04_rev=1)
        if a != want_a or b != want_b:
            fail("unswitch experiment %s: %s / %s" % (short, a, b))
    # pass order in the clang 18 pipeline: unswitch, then IndVarSimplify, then the loop vectorizer; no unswitch after IndVars
    res = excerpts.pipeline_functions("C-c18-kernels-fast-pipeline")
    for fn, passes in res.items():
        if "kern_k04" in fn:
            names = [e["name"].split(" on ")[0] for e in passes if not e["machine"]]
            iv = names.index("IndVarSimplifyPass")
            lv = names.index("LoopVectorizePass")
            sw = [i for i, n in enumerate(names) if n == "SimpleLoopUnswitchPass"]
            if not sw or max(sw) > iv:
                fail("SimpleLoopUnswitchPass is not before IndVarSimplifyPass in the k04 pipeline: %s" % sw)
            if iv > lv:
                fail("IndVarSimplifyPass after LoopVectorizePass")
            print("k04 pipeline: unswitch at %s, IndVarSimplify at %d, LoopVectorize at %d" % (sw, iv, lv))
    # the reverse loop: IndVarSimplify is the pass that makes the check loop-invariant
    for fn, passes in res.items():
        if "kern_k04" in fn:
            for i, e in enumerate(passes):
                if e["name"].startswith("IndVarSimplifyPass") and e["irChanged"]:
                    before = norm("\n".join(excerpts.text_of(e["before"])))
                    after = norm("\n".join(excerpts.text_of(e["after"])))
                    if "br i1 %20, label %27, label %26" not in after or "br i1 %24, label %26, label %25" not in before:
                        fail("k04 IndVarSimplify before/after not as described")
    print("numbers checked")


def check_tables():
    R = excerpts.remark_of
    # F9: reverse and stride-2 with the checks off and on, five compilers; forward loops keep SIMD
    wording = {"c18": ("could not determine number of loop iterations",) * 2,
               "c19": ("could not determine number of loop iterations",) * 2,
               "c20": ("Cannot vectorize early exit loop with writes to memory",
                       "Cannot vectorize early exit loop with more than one early exit"),
               "c21": ("Cannot vectorize early exit loop with writes to memory",
                       "Cannot vectorize early exit loop with more than one early exit"),
               "ctrunk": ("Cannot vectorize early exit loop with complex writes to memory",) * 2}
    for short, (w4, w5) in wording.items():
        none, fast = R("A-%s-kernels-none" % short), R("A-%s-kernels-fast" % short)
        for fn, w in (("kern_k04_rev", w4), ("kern_k05_stride2", w5)):
            if none[fn] != "vectorized 4x2" or fast[fn] != "not vectorized: " + w:
                fail("F9 %s %s: %s / %s" % (short, fn, none[fn], fast[fn]))
        for fn in ("kern_k01_sum_fwd", "kern_k02_add_fwd", "kern_k03_stencil"):
            if not (none[fn].startswith("vectorized") and fast[fn].startswith("vectorized")):
                fail("F9 forward loop lost: %s %s" % (short, fn))
    # remarks do not depend on -g0
    pairs = 0
    for a, b in (("A-c18-kernels-fast", "B-c18-kernels-fast-ir"), ("A-c18-kernels-none", "B-c18-kernels-none-ir"),
                 ("A-c20-kernels-fast", "B-c20-kernels-fast-ir"), ("A-c20-kernels-none", "B-c20-kernels-none-ir"),
                 ("A-c19-kernels-fast", "B-c19-kernels-fast-ir"), ("A-ctrunk-kernels-fast", "B-ctrunk-kernels-fast-ir"),
                 ("A-c18-variants-fast", "B-c18-variants-fast-ir"), ("A-c20-variants-fast", "B-c20-variants-fast-ir"),
                 ("A-ctrunk-variants-fast", "B-ctrunk-variants-fast-ir"), ("A-c18-variants2-fast", "B-c18-variants2-fast-ir"),
                 ("A-c18-variants3-fast", "B-c18-variants3-fast-ir")):
        pairs += 1
        if R(a) != R(b):
            fail("remarks differ with -g0: %s %s" % (a, b))
    if "The remarks of the %d pairs of runs with and without `-g0`" % pairs not in readme_text():
        fail("README does not say that %d pairs of runs with and without -g0 have identical remarks" % pairs)
    # F8 and F10: the variants on clang 18.1.0 FAST
    f8 = {"v_rev_pre": "vectorized 4x2", "v_rev_span": "vectorized 4x2", "v_rev_raw": "vectorized 4x2",
          "v_rev_fwd": "vectorized 4x2", "v_s2_span": "vectorized 4x1", "v_s2_raw": "vectorized 4x2",
          "v_fwd_manual": "vectorized 4x2"}
    notv = ("v_s2_pre", "v_s2_pre_mul", "v_rev_manual", "v_s2_manual", "v_rev_j", "v_s2_one", "v_s2_j")
    r18 = R("A-c18-variants-fast")
    for fn, want in f8.items():
        if r18[fn] != want:
            fail("F8 %s: %s" % (fn, r18[fn]))
    for fn in notv:
        if not r18[fn].startswith("not vectorized: could not determine number of loop iterations"):
            fail("F8 %s: %s" % (fn, r18[fn]))
    n18 = R("A-c18-variants-none")
    for fn in ("v_rev_manual", "v_s2_manual"):
        if not n18[fn].startswith("not vectorized: could not determine number of loop iterations"):
            fail("F10 NONE %s: %s" % (fn, n18[fn]))
    if n18["v_fwd_manual"] != "vectorized 4x2":
        fail("F10 NONE v_fwd_manual")
    if not n18["v_s2_one"].startswith("not vectorized: the cost-model"):
        fail("v_s2_one with checks off: %s" % n18["v_s2_one"])
    # F8: SCEV status of the variants
    blocks = {excerpts.short_name(k): v for k, v in excerpts.scev_blocks("E-c18-variants-fast-scev").items()}
    single = ("v_rev_pre", "v_rev_span", "v_rev_raw", "v_s2_raw")
    for fn in single:
        if blocks[fn]["exits"] or (blocks[fn]["btc"] or "").startswith("Unpredictable"):
            fail("F8 SCEV %s should be one counted exit" % fn)
    for fn in ("v_rev_fwd", "v_s2_span"):
        d = blocks[fn]
        if not d["exits"] or any("COULDNOTCOMPUTE" in c for _, c in d["exits"]):
            fail("F8 SCEV %s should have all exits counted" % fn)
    for fn in ("v_s2_pre", "v_s2_pre_mul"):
        d = blocks[fn]
        if [("COULDNOTCOMPUTE" in c) for _, c in d["exits"]] != [True, True, False]:
            fail("F8 SCEV %s should have two uncounted exits and a counted latch" % fn)
    # F7
    f7 = {"c18": ("not vectorized", "vectorized", "vectorized", "not vectorized"),
          "c20": ("not vectorized", "vectorized", "vectorized", "not vectorized"),
          "ctrunk": ("not vectorized", "vectorized", "vectorized", "not vectorized")}
    for short, want in f7.items():
        r = R("A-%s-variants2-fast" % short)
        got = tuple("vectorized" if r[fn].startswith("vectorized") else "not vectorized"
                    for fn in ("v2_s2_guard", "v2_s2_guard_masked", "v2_s2_masked", "v2_rev_masked"))
        if got != want:
            fail("F7 %s: %s" % (short, got))
    # F4 / F5: single "Unknown exit count" line
    if ce.stderr_text(ce.load("D-c18assert-kernels-fast-indvars")).count("Unknown exit count") != 1:
        fail("expected exactly one 'Unknown exit count' line")
    laa = [ln for ln in ce.stderr_text(ce.load("D-c18assert-kernels-fast-laa")).splitlines()
           if "SCEV could not compute the loop exit count" in ln]
    if len(laa) != 2:
        fail("expected two LAA lines, found %d" % len(laa))
    # F4: the c20 tally of the 14 variants
    t = tally("E-c20-variants-fast-scev", "A-c20-variants-fast")
    if t != {"ok": 7, "bad": 7, "mismatch": 0}:
        fail("c20 variants tally %s" % t)
    # F8: v_rev_pre has the in-loop conditions proved true by ConstraintElimination, and no such change in v_s2_pre
    res = excerpts.pipeline_functions("C-c18-variants-fast-pipeline")
    for fn, passes in res.items():
        short = excerpts.short_name(fn)
        if short in ("v_rev_pre", "v_s2_pre", "v_s2_pre_mul"):
            changed = []
            for i, e in enumerate(passes):
                if e["machine"]:
                    break
                if e["name"].startswith("ConstraintEliminationPass"):
                    a = sum(1 for ln in excerpts.text_of(e["after"]) if "br i1 true" in ln)
                    b = sum(1 for ln in excerpts.text_of(e["before"]) if "br i1 true" in ln)
                    changed.append((i, b, a))
            if short == "v_rev_pre" and changed != [(35, 0, 2)]:
                fail("v_rev_pre ConstraintElimination: %s" % changed)
            if short != "v_rev_pre" and any(a != b for _, b, a in changed):
                fail("%s ConstraintElimination changed branches: %s" % (short, changed))
    print("tables checked")


def events_by_function(text):
    """{function: [event lines]} from extracted-style text of excerpts.trap_events."""
    out, cur = {}, None
    for ln in text.splitlines():
        if not ln or ln.startswith("#"):
            continue
        if ln.startswith("    "):
            out[cur].append(ln.strip())
        else:
            cur = ln.strip()
            out[cur] = []
    return out


def vector_bodies(name):
    return {excerpts.short_name(k): v for k, v in excerpts.vector_body_counts(name).items()}


def classify(check):
    """Kind of one trap exit from excerpts.trap_checks: (compare predicate, form, counted).
    form: 'invariant' (no phi among the instructions that compute the condition), 'counter' (an `icmp eq` that involves the
    counter), 'scaled' (a compare of a shifted counter)."""
    bb, term, count, lines = check
    pred = re.match(r"%\S+ = icmp (\w+) ", lines[0]).group(1)
    has_phi = any(" = phi " in ln for ln in lines)
    if not has_phi:
        form = "invariant"
    elif pred == "eq":
        form = "counter"
    elif any(" = shl " in ln for ln in lines):
        form = "scaled"
    else:
        form = "other"
    return pred, form, "COULDNOTCOMPUTE" not in count


def check_findings():
    text = norm(readme_text())
    R = excerpts.remark_of

    # ---- ud2 per function and the forward sum's trap call (Setup table)
    ud2 = {}
    for mode in ("fast", "none"):
        cur, ud2[mode] = None, {}
        for ln in ce.asm_text(ce.load("A-c18-kernels-%s" % mode)).splitlines():
            if ln and not ln[0].isspace() and ln.rstrip().endswith(":") and not ln.startswith("."):
                cur = ln.split("(")[0]
                ud2[mode][cur] = 0
            elif cur and re.match(r"\s+ud2\b", ln):
                ud2[mode][cur] += 1
    want = {"kern_k01_sum_fwd": 0, "kern_k02_add_fwd": 1, "kern_k03_stencil": 1, "kern_k04_rev": 1, "kern_k05_stride2": 1}
    if ud2["fast"] != want or any(ud2["none"].values()):
        fail("ud2 per function: FAST %s, NONE %s" % (ud2["fast"], ud2["none"]))
    ev_k = events_by_function(excerpts.trap_events("C-c18-kernels-fast-pipeline"))
    if "JumpThreadingPass (26): trap calls 1->0, `br i1 true` 1->0" not in ev_k["kern_k01_sum_fwd"]:
        fail("the forward sum's trap call is not removed by JumpThreadingPass (26)")

    # ---- F8: pass events of the rewrites
    ev = events_by_function(excerpts.trap_events("C-c18-variants-fast-pipeline"))
    for fn, want_ev in (("v_rev_pre", ["ConstraintEliminationPass (35): trap calls 3->3, `br i1 true` 0->2",
                                       "LoopSimplifyCFGPass (39): trap calls 2->0, `br i1 true` 2->0"]),
                        ("v_rev_span", ["ConstraintEliminationPass (35): trap calls 2->2, `br i1 true` 0->1",
                                        "LoopSimplifyCFGPass (39): trap calls 1->0, `br i1 true` 1->0"])):
        for w in want_ev:
            if w not in ev[fn]:
                fail("pass event missing for %s: %s" % (fn, w))
    for fn in ("v_s2_span", "v_s2_pre", "v_s2_pre_mul"):
        if any(e.startswith("ConstraintEliminationPass") for e in ev[fn]):
            fail("ConstraintEliminationPass changes %s" % fn)

    # ---- F4: the order of the messages in the combined debug run
    t = ce.stderr_text(ce.load("D-c18assert-kernels-fast-lv-laa")).splitlines()
    if sum("LAA: SCEV could not compute the loop exit count." in ln for ln in t) != 2:
        fail("expected two 'SCEV could not compute the loop exit count' lines in the combined debug run")
    checking = [i for i, ln in enumerate(t) if "LV: Checking a loop" in ln]
    seq = ["LAA: Found a loop in", "LAA: SCEV could not compute the loop exit count.",
           "remark: loop not vectorized: could not determine number of loop iterations",
           "LV: Can't vectorize due to memory conflicts", "LV: We can vectorize this loop!",
           "LV: Not vectorizing: Cannot prove legality."]
    for k in ("kern_k04_rev", "kern_k05_stride2"):
        i0 = next(i for i in checking if k in t[i])
        i1 = next((i for i in checking if i > i0), len(t))
        pos = i0
        for needle in seq:
            pos = next((j for j in range(pos + 1, i1) if needle in t[j]), None)
            if pos is None:
                fail("debug run, %s: '%s' not found in order" % (k, needle))
                break

    # ---- trunk build times (Setup table)
    times = [ce.load(e["name"])["fetched_at"] for e in experiments.all_experiments()
             if e["compiler_id"] in ("clang_trunk", "opttrunk") and e["name"][0] in "ABEF"]
    lo, hi = min(times), max(times)
    if lo[:10] != hi[:10] or ("fetched on %s from %s to %s UTC" % (lo[:10], lo[11:19], hi[11:19])) not in text:
        fail("README does not give the trunk fetch times %s to %s" % (lo, hi))
    vc, vo = ce.load("V-ctrunk-version"), ce.load("V-opttrunk-version")
    if not vc["fetched_at"].startswith("2026-10-16T00:41") or "Version line recorded on 2026-10-16 at 00:41 UTC" not in text:
        fail("trunk version time: %s" % vc["fetched_at"])
    so = ce.stdout_text(vc)
    if "clang version 24.0.0git" not in so or "efd496572478672274aaf162a2a924c1cf5cb09c" not in so or "clang-trunk-20261015" not in so \
            or "commit `efd49657`" not in text:
        fail("trunk compiler version line does not match the README")
    if "LLVM version 24.0.0git" not in ce.stdout_text(vo) or re.search(r"[0-9a-f]{40}", ce.stdout_text(vo)):
        fail("trunk opt version line does not match the README")

    # ---- F2, F7, F8: the trap exits of each loop, the compare form and the exit count
    shown = {}
    for src, ir, ev_name, _rem in excerpts.CHECK_SETS:
        for fn, checks in excerpts.trap_checks(ir, ev_name).items():
            shown[fn] = checks
    scev_all = {}
    for src, ir, ev_name, _rem in excerpts.CHECK_SETS:
        for sym, d in excerpts.scev_blocks(ev_name).items():
            scev_all[excerpts.short_name(sym)] = d
    want_kind = {
        "kern_k04_rev": [("ult", "invariant", False)],
        "kern_k05_stride2": [("ugt", "scaled", False), ("ugt", "scaled", False)],
        "v2_s2_guard": [("ult", "scaled", False)],
        "v2_s2_guard_masked": [("eq", "counter", True)],
        "v2_s2_masked": [("eq", "counter", True)],
        "v2_rev_masked": [("ult", "invariant", False)],
        "v3_one_plain": [("ult", "scaled", False)],
        "v3_one_half": [("eq", "counter", True)],
        "v3_one_min": [("eq", "counter", True)],
        "v3_one_assume": [("eq", "counter", True)],
        "v3_two_plain": [("ult", "scaled", False), ("ult", "scaled", False)],
        "v3_two_masked": [("eq", "counter", True), ("eq", "counter", True)],
        "v_s2_span": [("ugt", "scaled", True)],
        "v_s2_pre": [("ugt", "scaled", False), ("ugt", "scaled", False)],
        "v_s2_pre_mul": [("ugt", "scaled", False), ("ugt", "scaled", False)],
        "v_rev_pre": [], "v_rev_span": [], "v_rev_raw": [], "v_s2_raw": [],
    }
    for fn, w in want_kind.items():
        got = [classify(c) for c in shown[fn]]
        if got != w:
            fail("trap exits of %s: %s, README expects %s" % (fn, got, w))
    for fn in ("v_rev_pre", "v_rev_span", "v_rev_raw", "v_s2_raw"):
        if scev_all[fn]["exits"]:
            fail("%s should have a single exit" % fn)
    if len(scev_all["v3_two_masked"]["exits"]) != 3 or any("COULDNOTCOMPUTE" in c for _, c in scev_all["v3_two_masked"]["exits"]):
        fail("v3_two_masked should have three counted exits")
    lines_of = {fn: [ln for c in shown[fn] for ln in c[3]] for fn in shown}
    if not any("shl nuw" in ln for ln in lines_of["v2_s2_guard"]) or any("shl nuw" in ln for ln in lines_of["kern_k05_stride2"]):
        fail("shl flags: v2_s2_guard should have nuw and kern_k05_stride2 should not")
    if not any("lshr exact" in ln for ln in lines_of["v_s2_span"]):
        fail("v_s2_span bound is not an lshr exact")
    for fn in ("v_s2_pre", "v_s2_pre_mul", "kern_k05_stride2"):
        if not any("ashr exact" in ln for ln in lines_of[fn]):
            fail("%s bound is not an ashr exact" % fn)
    c18 = ce.stderr_text(ce.load("B-c18-variants2-fast-ir"))
    if shown["v2_s2_guard"][0][3][0].split(",")[0] != "%29 = icmp ult i64 %28" or "%29 = icmp ult i64 %28, %16" not in c18 \
            or shown["v2_s2_guard_masked"][0][3][0].split(",")[0] != "%29 = icmp eq i64 %28":
        fail("compare lines quoted in F7 for v2_s2_guard and v2_s2_guard_masked")

    # ---- F7: hand-written IR (group H)
    scev = {n: excerpts.h_scev(n) for _, n in excerpts.H_OPTS}
    lv = excerpts.h_lv()
    counted_bounds = {"lshr1", "and62", "umin40", "ptr_lshr"}
    nfun = 0
    for flags in ("plain", "nuw"):
        for bound, pat in excerpts.H_FUNCS:
            fn = pat % flags
            nfun += 1
            for _, n in excerpts.H_OPTS:
                if ("COULDNOTCOMPUTE" not in scev[n][fn]) != (bound in counted_bounds):
                    fail("hand-written IR %s on %s: exit count %s" % (fn, n, scev[n][fn]))
            if lv[fn] != (bound in counted_bounds):
                fail("hand-written IR %s: loop vectorizer decision %s" % (fn, lv[fn]))
    if nfun != 14 or len(lv) != 14 or text.count("all 14 functions") != 2:
        fail("expected 14 hand-written functions, found %d / %d" % (nfun, len(lv)))
    st = ce.stderr_text(ce.load("H-opt1810-s2-bound-lv"))
    if st.count("remark: <unknown>:0:0: vectorized loop (vectorization width: 4, interleaved count: 1)") != 8 or \
            st.count("remark: <unknown>:0:0: loop not vectorized: could not determine number of loop iterations") != 6:
        fail("remark counts of the hand-written IR run")

    # ---- F6: the full -O2 pipeline of opt 18.1.0 (group G)
    base = {"kern_k01_sum_fwd": 1, "kern_k02_add_fwd": 1, "kern_k03_stencil": 1, "kern_k04_rev": 0, "kern_k05_stride2": 0}
    runs = {"control": ("G-opt1810-full-O2-control", base, 2, 1),
            "after": ("G-opt1810-full-O2-unswitch-after-indvars", dict(base, kern_k04_rev=1), 1, 2),
            "before": ("G-opt1810-full-O2-unswitch-before-lv", dict(base, kern_k04_rev=1), 1, 2)}
    for tag, (name, wantv, n_not, n_w4i2) in runs.items():
        got = vector_bodies(name)
        if got != wantv:
            fail("full pipeline %s: %s" % (tag, got))
        se = ce.stderr_text(ce.load(name))
        if se.count("remark: <unknown>:0:0: loop not vectorized: could not determine number of loop iterations") != n_not:
            fail("full pipeline %s: count of the 'could not determine' remark" % tag)
        if se.count("remark: <unknown>:0:0: vectorized loop (vectorization width: 4, interleaved count: 2)") != n_w4i2:
            fail("full pipeline %s: count of the 4x2 remark" % tag)
    pipe = ce.stdout_text(ce.load("G-opt1810-print-O2-pipeline")).strip()
    if pipe.count("simple-loop-unswitch<") != 1 or pipe.index("simple-loop-unswitch<") > pipe.index(experiments.INDVARS_GROUP) \
            or pipe.count(experiments.INDVARS_GROUP) != 1 or pipe.count(experiments.LV_PASS) != 1 \
            or pipe.index(experiments.INDVARS_GROUP) > pipe.index(experiments.LV_PASS):
        fail("the textual O2 pipeline does not have the order the README states")
    pipes = experiments.full_pipelines()
    if experiments.INDVARS_GROUP + "," + experiments.UNSWITCH not in pipes["unswitch-after-indvars"] \
            or experiments.UNSWITCH + "," + experiments.LV_PASS not in pipes["unswitch-before-lv"]:
        fail("the modified pipelines do not have the inserted pass where the README says")
    with open(os.path.join(HERE, "sources", "ir", "c18-kernels-fast-frontend.ll"), encoding="utf-8") as f:
        if f.read() != extract.frontend_text():
            fail("sources/ir/c18-kernels-fast-frontend.ll is not the saved front-end IR")

    # ---- F9: the IR across compilers
    shape = excerpts.ir_shape()
    for fn in ("kern_k02_add_fwd", "kern_k04_rev", "kern_k05_stride2"):
        for ver in ("19.1.0", "20.1.0", "trunk"):
            if shape[(ver, fn)] != shape[("18.1.0", fn)]:
                fail("IR shape of %s differs between 18.1.0 and %s" % (fn, ver))
    f_tr = excerpts.raw_features("B-ctrunk-kernels-fast-ir")
    if f_tr["kern_k04_rev"] != (2, 4, 0) or f_tr["kern_k05_stride2"] != (3, 4, 0):
        fail("trunk assume/ptrtoaddr/ptrtoint counts: %s" % f_tr)
    for name in ("B-c18-kernels-fast-ir", "B-c19-kernels-fast-ir", "B-c20-kernels-fast-ir"):
        f = excerpts.raw_features(name)
        if f["kern_k04_rev"][:2] != (0, 0) or f["kern_k05_stride2"][:2] != (0, 0):
            fail("%s has assume or ptrtoaddr" % name)
    tr = ce.stderr_text(ce.load("B-ctrunk-kernels-fast-ir"))
    if tr.count("call void @llvm.assume(") != len(re.findall(r'call void @llvm\.assume\(i1 true\) \[ "separate_storage"', tr)):
        fail("an assume call of the trunk dump has no separate_storage bundle")

    # ---- F6: metadata the opt inputs lose
    for name in excerpts.OPT_INPUTS:
        kinds, _groups = excerpts.metadata_counts(name)
        for k in ("srcloc", "noundef", "nonnull", "range", "align"):
            if kinds[k]:
                fail("%s has %s metadata, which the README says does not occur" % (name, k))

    # ---- F8: the span variant's interleave count by version
    if R("A-c18-variants-fast")["v_s2_span"] != "vectorized 4x1" or any(
            R("A-%s-variants-fast" % v)["v_s2_span"] != "vectorized 4x2" for v in ("c19", "c20", "c21", "ctrunk")):
        fail("v_s2_span interleave count by version")

    # ---- the tally sentence and the request counts of the README
    per_src = {src: len(R("A-c18-%s-fast" % src)) for src in ("kernels", "variants", "variants2", "variants3")}
    total = sum(per_src.values())
    ok = bad = 0
    for src in per_src:
        t = tally("E-c18-%s-fast-scev" % src, "A-c18-%s-fast" % src)
        ok, bad = ok + t["ok"], bad + t["bad"]
    for s in ("Over the %d loops compiled with FAST on clang 18.1.0" % total,
              "all %d loops with a count for every exit were vectorized, and none of the %d loops with an uncounted exit was" % (ok, bad),
              "%d loops (5 project loops, 14 loops of `sources/variants.cpp`, 4 of `sources/variants2.cpp`, 6 of `sources/variants3.cpp`): %d loops have a count for every exit and all %d are vectorized. %d loops have an exit without a count and none of the %d is vectorized"
              % (total, ok, ok, bad, bad),
              "In all %d loops tried" % total):
        if s not in text:
            fail("README does not say: %s" % s)
    if list(per_src.values()) != [5, 14, 4, 6]:
        fail("loops per source: %s" % per_src)
    with open(os.path.join(HERE, "request-index.json"), encoding="utf-8") as f:
        idx = json.load(f)
    raw_names = {f.replace(".json.gz", "").replace(".json", "") for f in os.listdir(os.path.join(HERE, "raw"))}
    names = [e["name"] for e in idx]
    resent = sum(names.count(n) - 1 for n in set(names) if n in raw_names)
    not_kept = sum(1 for n in names if n not in raw_names)
    ncomp = sum(1 for e in idx if e["kind"] == "compile")
    nget = sum(1 for e in idx if e["kind"] == "get")
    for s in ("%d requests in total (`request-index.json`): %d compiles and %d listings" % (len(idx), ncomp, nget),
              "%d answers are kept in `raw/`" % len(raw_names),
              "other %d requests were repeats: %d were sent again" % (len(idx) - len(raw_names), resent)):
        if s not in text:
            fail("README does not say: %s" % s)
    if resent + not_kept != len(idx) - len(raw_names) or not_kept != 2:
        fail("request repeats: resent %d, not kept %d, total %d, kept %d" % (resent, not_kept, len(idx), len(raw_names)))
    print("findings checked")


def check_replay():
    """The rebuild of raw/ from nothing, replayed offline (replay_check.py), and the numbers the README gives for it."""
    r = subprocess.run([sys.executable, os.path.join(HERE, "replay_check.py")], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        fail("replay_check.py failed: %s" % (r.stdout + r.stderr)[-300:])
        return
    sent = json.loads(re.search(r"requests per fetch.py run: (\[.*?\])", r.stdout).group(1))
    text = norm(readme_text())
    for s in ("The first run sends the %d requests" % sent[0], "the second the %d requests" % sent[1],
              "the third the %d full-pipeline runs" % sent[2], "the fourth sends none"):
        if s not in text:
            fail("README does not say: %s" % s)
    if sent[3] != 0 or "rebuilds all %d answers" % len(os.listdir(os.path.join(HERE, "raw"))) not in text:
        fail("replay: last run sent %s, or the README's number of answers is wrong" % sent[3])


def check_extracted():
    import tempfile
    saved = excerpts.OUT
    with tempfile.TemporaryDirectory() as tmp:
        excerpts.main(tmp)
        excerpts.OUT = saved
        for name in sorted(os.listdir(tmp)):
            with open(os.path.join(tmp, name), encoding="utf-8") as f:
                fresh = f.read()
            path = os.path.join(saved, name)
            if not os.path.exists(path):
                fail("extracted/%s is missing" % name)
                continue
            with open(path, encoding="utf-8") as f:
                if f.read() != fresh:
                    fail("extracted/%s is not what excerpts.py makes from raw/" % name)
        extra = set(os.listdir(saved)) - set(os.listdir(tmp))
        if extra:
            fail("extracted/ has files excerpts.py does not make: %s" % sorted(extra))
    print("extracted files checked")


def check_unswitch_remarks():
    a = ce.stderr_text(ce.load("F-c18-kernels-fast-lv-only")).count("loop not vectorized: could not determine number of loop iterations")
    b = ce.stderr_text(ce.load("F-c18-kernels-fast-unswitch-then-lv")).count("loop not vectorized: could not determine number of loop iterations")
    if (a, b) != (2, 1):
        fail("F6 remark counts %s" % ((a, b),))


def main():
    check_quotes()
    check_sources()
    check_requests()
    check_numbers()
    check_tables()
    check_unswitch_remarks()
    check_findings()
    check_replay()
    check_extracted()
    if failures:
        print("%d failure(s)" % len(failures))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
