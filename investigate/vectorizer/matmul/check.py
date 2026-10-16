"""Offline check of this folder (no network).

    python check.py

1. Every saved answer in raw/ was made from the request the manifest builds today (same source, same options).
2. derived/ is exactly what analyze.py computes from raw/.
3. The statements the README makes about the saved answers hold (the assertions below).
4. The saved LLVM source passages say what the README quotes from them.
Exit status 0 when all four hold.
"""
import json
import os
import re
import subprocess
import sys

import ce
import cost_table
import loadtrack
import run_requests as rr

HERE = os.path.dirname(os.path.abspath(__file__))
failures = []


def need(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        failures.append(what)


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as f:
        return f.read()


def text(name):
    return ce.stderr_text(ce.load(name))


# 1. requests match the saved answers
bad, missing = [], []
for name, (group, cid, src, args, pipe, filters) in rr.MANIFEST.items():
    rec = ce.load(name)
    if rec is None:
        missing.append(name)
        continue
    body = ce.request_body(ce.read_source(src), args, pipe, filters)
    if rec["request_sha256"] != ce.sha(cid, body):
        bad.append(name)
need(not missing, "all %d manifest requests have a saved answer (missing: %s)" % (len(rr.MANIFEST), missing or "none"))
need(not bad, "each saved answer was made from today's source and options (differing: %s)" % (bad or "none"))
need(ce.requests_used() == len(rr.MANIFEST), "requests.tsv counts %d requests, the manifest has %d" % (ce.requests_used(), len(rr.MANIFEST)))
need(ce.requests_used() <= ce.MAX_REQUESTS, "request cap %d respected" % ce.MAX_REQUESTS)
need(all(ln.rstrip().endswith("\t200") for ln in read("requests.tsv").splitlines() if ln.strip()), "every request was answered with HTTP 200")
readme = read("README.md")
need("%d compile requests" % len(rr.MANIFEST) in readme, "the README states the request count (%d)" % len(rr.MANIFEST))

need(read("derived", "readme-table.md").strip() in readme, "the README repeats derived/readme-table.md exactly")
missing_paths = []
for mm in re.finditer(r"`((?:raw|derived|llvm-src|src)/[A-Za-z0-9_.\-]+?\.(?:json\.gz|json|txt|md|tsv|ll|cpp))`", readme):
    if not os.path.exists(os.path.join(HERE, mm.group(1))):
        missing_paths.append(mm.group(1))
need(not missing_paths, "every raw/, derived/, llvm-src/ and src/ file the README names exists (missing: %s)" % (missing_paths or "none"))

# 2. derived files are current
r = subprocess.run([sys.executable, os.path.join(HERE, "analyze.py"), "--check"], capture_output=True, text=True)
need(r.returncode == 0, "derived/ matches raw/ (%s)" % r.stdout.strip())

# 3. the README's statements about the saved answers
import analyze  # noqa: E402

o = analyze.by_name(analyze.outcomes())
FASTM = "_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"


def vec(n):
    return o[n]["status"] == "vectorized"


# F1: the reproduction, and which builds are FAST
need(not vec("base_c18_fast") and vec("base_c19_fast"), "k08 under FAST: clang 18.1.0 does not vectorize, clang 19.1.0 does")
need(vec("base_c18_none") and vec("base_c19_none"), "k08 with the checks off: both vectorize")
need("not beneficial" in o["base_c18_fast"]["detail"], "clang 18's remark is the cost-model remark")
need(o["base_c18_fast"]["simd"] == 0 and o["base_c19_fast"]["simd"] == 22, "vector-register instruction lines: 0 for clang 18 FAST, 22 for clang 19 FAST")
need(analyze.mode_macro("dbg_a16_fast") == "_LIBCPP_ENABLE_ASSERTIONS=1" and analyze.mode_macro("dbg_a17_fast") == "_LIBCPP_ENABLE_HARDENED_MODE=1",
     "clang 16 was built with _LIBCPP_ENABLE_ASSERTIONS=1 and clang 17 with _LIBCPP_ENABLE_HARDENED_MODE=1, not with FAST")
need(all(o[n]["ud2"] == 0 and o[n]["asm"] == 126 and "__libcpp_verbose_abort" in ce.asm_text(ce.load(n)) for n in ("dbg_a16_fast", "dbg_a17_fast")),
     "clang 16 and 17: the check compiles to a call of __libcpp_verbose_abort, no ud2, 126 assembly lines")
fast_names = ["base_c18_fast", "base_c19_fast"] + ["dbg_%s_fast" % t for t in ("a18", "a19", "a20", "a21", "a22", "a23", "atrunk")] + [
    "libswap_c%s_lib18" % t for t in ("18", "19", "20", "21", "22", "231", "trunk")] + ["libswap_c18_lib19"]
need(all(analyze.mode_macro(n) == FASTM and o[n]["ud2"] == 1 for n in fast_names if "trunk" not in n or n == "dbg_atrunk_fast"),
     "clang 18 and later: every FAST build of k08 that compiled has the FAST macro and exactly one ud2")
need(o["dbg_a18_fast"]["asm"] == 77, "clang 18 FAST: 77 assembly lines")
all_fast = [n for n, (g_, cid_, src_, args_, pipe_, f_) in rr.MANIFEST.items()
            if FASTM in args_ and cid_ not in ("clang1600", "clang1701") and n in o and o[n]["status"] != "compile error" and "emul" not in src_]
need(len(all_fast) >= 40 and all(o[n]["ud2"] == 1 for n in all_fast),
     "all %d k08 builds with the FAST macro on clang 18 or later that compiled have exactly one ud2" % len(all_fast))
need(all(vec(n) and o[n]["ud2"] == 0 and "__libcpp_verbose_abort" not in ce.asm_text(ce.load(n)) for n in ("fastmacro_c16", "fastmacro_c17")),
     "clang 16 and 17 with the FAST macro: vectorized, no ud2, no abort call (the macro adds no check)")

# F2 / F3: legality passed, the decision is the cost model's
t = {tag: analyze.lv_numbers("dbg_%s_fast" % tag) for tag in ("a16", "a17", "a18", "a19", "a20", "a21", "a22")}
need("We can vectorize this loop (with a runtime bound check)!" in text("dbg_a18_fast"), "clang 18.1.0: legality passed")
need(all(any("EXPAND SCEV" in ln and "umin_seq" in ln for ln in text(n_).splitlines()) for n_ in ("dbg_a18_fast", "dbg_a19_fast")),
     "clang 18 and 19 plans: the trip count is expanded from a SCEV with umin_seq (both size checks folded into one bound)")
need(all("We can vectorize this loop" in text(n_) for n_ in ("dbg_a18_fast", "dbg_a19_fast", "dbg_a22_fast")), "clang 18, 19 and 22: legality passes")
need("Vectorization is possible but not beneficial." in text("dbg_a18_fast") and "Selecting VF: 1." in text("dbg_a18_fast"),
     "clang 18.1.0: the log ends with 'possible but not beneficial' and 'Selecting VF: 1'")
need(all(t[k]["scalar"] == "11" and t[k]["vf4"] == "11" and t[k]["cmp4"] == "14/14" for k in ("a16", "a17", "a18")),
     "clang 16, 17, 18: scalar 11, vector (width 4) 11 per lane, exit compares 14 each")
need(all(t[k]["scalar"] == "11" and t[k]["vf4"] == "4" and t[k]["cmp4"] == "1/1" and t[k]["uniform"] == "yes" for k in ("a19", "a20", "a21")),
     "clang 19, 20, 21: scalar 11, vector (width 4) 4 per lane, exit compares 1 each and uniform")
need(t["a22"]["scalar"] == "7" and t["a22"]["vf4"] == "3", "clang 22: scalar 7, vector 3 (the exit compares are no longer in the loop)")
need(cost_table.table("dbg_a18_fast")[1] == {1: 11, 4: 45} and cost_table.table("dbg_a19_fast")[1] == {1: 11, 4: 16},
     "sum of the logged instruction costs: clang 18 11 (scalar) and 45 (width 4); clang 19 11 and 16")
need("Found an estimated cost of 14 for VF 4 For instruction:   %cmp.i42 = icmp ugt i64 %sub.ptr.div.i.i41, %add10" in text("dbg_a18_fast"),
     "clang 18.1.0: the quoted 14-unit compare line is in the log")
ir = read("derived", "ir_diff_before_loopvectorize_c18_c19.txt")
m = re.search(r"; (\d+) lines removed, (\d+) added", ir)
need("getelementptr inbounds i8, ptr %1, i64 8" in ir and m is not None and (int(m.group(1)), int(m.group(2))) == (3, 3)
     and "96 lines (pipe_c18_fast), 96 lines (pipe_c19_fast)" in ir,
     "the IR clang 18 and clang 19 hand to the vectorizer: 96 lines each, 3 lines removed and 3 added, all the address of the vector's end pointer")


def loop_facts(path):
    """(llvm.trap calls in the dump, how many of them are exits of the innermost loop, exit edges of the innermost loop)."""
    blocks, order = loadtrack.parse(read(*path))
    h_, body = loadtrack.innermost_loop(blocks, order)
    traps = [b for b in order if any("llvm.trap" in i for i in blocks[b])]
    exits = [(x, y) for x in body for y in loadtrack.succs(blocks[x]) if y not in body]
    return len(traps), sum(1 for b in traps if any(b in loadtrack.succs(blocks[x]) for x in body)), len(exits)


need(loop_facts(("derived", "ir_before_loopvectorize_c18_fast.ll")) == (3, 2, 3) == loop_facts(("derived", "ir_before_loopvectorize_c19_fast.ll")),
     "clang 18 and 19 IR before the vectorizer: three llvm.trap calls, two of them exits of the innermost loop (three exit edges)")
need(loop_facts(("derived", "ir_before_loopvectorize_c22_fast.ll"))[2] == 1, "clang 22 IR before the vectorizer: the innermost loop has a single exit edge")
need("%49 = load ptr, ptr %15, align 8" in read("derived", "ir_before_loopvectorize_c231_fast.ll")
     and "%50 = load ptr, ptr %0, align 8" in read("derived", "ir_before_loopvectorize_c231_fast.ll")
     and "%57 = call i64 @llvm.umin.i64(i64 %56, i64 %16)" in read("derived", "ir_before_loopvectorize_c22_fast.ll"),
     "the IR lines quoted for clang 23.1 (two pointer loads) and clang 22 (the clamp) are in the dumps")

# F4: which compares are uniform
unif18 = set(re.findall(r"Found uniform instruction:\s+(%\S+) = icmp", text("dbg_a18_fast")))
unif19 = set(re.findall(r"Found uniform instruction:\s+(%\S+) = icmp", text("dbg_a19_fast")))
need(unif18 == {"%exitcond.not"}, "clang 18.1.0: the only compare found uniform is the latch compare")
need({"%cmp.i42", "%cmp.i51", "%exitcond.not"} <= unif19, "clang 19.1.0: the two bounds-check compares are found uniform as well")
need("Loop requires scalar epilogue: multiple exits" in text("dbg_a19_fast"), "clang 19.1.0: 'Loop requires scalar epilogue: multiple exits'")

# F5: forced width
need(vec("force_c18_fast") and o["force_c18_fast"]["detail"] == "width 4, interleave 2", "clang 18.1.0 forced to width 4, interleave 2 vectorizes the loop")
asmd = read("derived", "asm_diff_c19_vs_c18_forced.txt")
m = re.search(r"# (\d+) lines against (\d+) lines; (\d+) lines removed, (\d+) added", asmd)
need(m is not None and tuple(map(int, m.groups())) == (209, 212, 12, 15), "forced clang 18 against clang 19: 209 against 212 lines, 12 lines removed and 15 added")
need("+        mov     rdi, r13" in asmd and "-        mov     qword ptr [rsp - 96], 0" in asmd and "+        mov     qword ptr [rsp - 96], rax" in asmd,
     "the forced-width difference contains an extra mov, a constant stored through a register, and moved instructions")

# F6: the cost of a 64-bit vector compare by target
need(vec("dbg_a18_fast_v2") and vec("dbg_a18_fast_v3"), "clang 18.1.0 vectorizes at x86-64-v2 and x86-64-v3")
need(o["dbg_a18_fast_v2"]["detail"] == "width 4, interleave 1" and o["dbg_a18_fast_v3"]["detail"] == "width 8, interleave 1", "x86-64-v2: width 4, interleave 1; x86-64-v3: width 8, interleave 1")
tbl = {}
for ln in read("llvm-src", "x86_setcc_i64_18.1.0.txt").splitlines():
    mm = re.match(r"(\w+)\s+line \d+: \{ ISD::SETCC,\s+MVT::(v\d+i64),\s+\{ (\d+),", ln)
    if mm:
        tbl[(mm.group(1), mm.group(2))] = int(mm.group(3))
cmpsel = read("llvm-src", "x86_cmpsel_cost_18.1.0.txt")
need("case CmpInst::Predicate::ICMP_ULT:" in cmpsel and "ExtraCost = 2;" in cmpsel and "return LT.first * (ExtraCost + *KindCost);" in cmpsel,
     "LLVM 18.1.0: an unsigned vector compare has ExtraCost 2 and the cost is LT.first * (ExtraCost + table cost)")


def expected_cost(target, vf):
    """LT.first (number of legal-width pieces, inferred from the fit) * (ExtraCost 2 + table cost)."""
    if target == "sse2":
        width, base = 128, tbl[("SSE2CostTbl", "v2i64")]
    elif target == "v2":
        width, base = 128, tbl[("SSE42CostTbl", "v2i64")]
    else:
        width = 256
        base = tbl[("AVX2CostTbl", "v4i64")] if vf >= 4 else tbl[("SSE42CostTbl", "v2i64")]
    return -(-vf * 64 // width) * (2 + base)


ok_all, n_cmp = True, 0
for target, name in (("sse2", "dbg_a18_fast"), ("v2", "dbg_a18_fast_v2"), ("v3", "dbg_a18_fast_v3")):
    seen = {}
    for mm in re.finditer(r"Found an estimated cost of (\d+) for VF (\d+) For instruction:\s+%cmp\.i\d+ = icmp ugt i64", text(name)):
        seen.setdefault(int(mm.group(2)), set()).add(int(mm.group(1)))
    for vf, costs in seen.items():
        if vf >= 2:
            n_cmp += 1
            ok_all = ok_all and costs == {expected_cost(target, vf)}
need(ok_all and n_cmp == 7, "all %d logged compare costs (VF 2, 4 and 8, three targets) equal LT.first * (2 + table cost)" % n_cmp)

# F7: one check instead of two
need(vec("emul_c18_aB") and vec("emul_c18_aC") and not vec("emul_c18_abc"), "clang 18.1.0: one inner-loop check vectorizes, two do not")
need(o["emul_c18_aB"]["detail"] == "width 4, interleave 1" and o["emul_c18_aC"]["detail"] == "width 4, interleave 1", "one-check variants: width 4, interleave 1")
need("Scalar loop costs: 9." in text("dbg_emul_a18_aB") and "Vector loop of width 4 costs: 7." in text("dbg_emul_a18_aB"), "one check: scalar 9, vector (width 4) 7 per lane")
need(vec("emul_c19_aB") and vec("emul_c19_aC"), "clang 19.1.0 vectorizes both one-check variants")

# F8: the library is not the cause
for n in ("emul_c16_abc", "emul_c17_abc", "emul_c18_abc", "emul_c231_abc", "emul_ctrunk_abc"):
    need(not vec(n), "library-free loop, checks on: %s not vectorized" % n)
for n in ("emul_c19_abc", "emul_c20_abc", "emul_c21_abc", "emul_c22_abc"):
    need(vec(n), "library-free loop, checks on: %s vectorized" % n)
need(all(vec(n) for n in ("emul_c18_none", "emul_c19_none", "emul_c231_none")), "library-free loop, checks off: clang 18, 19 and 23.1 vectorize")
need((o["emul_c18_abc"]["asm"], o["emul_c19_abc"]["asm"], o["emul_c22_abc"]["asm"], o["emul_c231_abc"]["asm"]) == (77, 209, 200, 72)
     == (o["base_c18_fast"]["asm"], o["base_c19_fast"]["asm"], o["dbg_a22_fast"]["asm"], o["dbg_a23_fast"]["asm"]),
     "assembly line counts of the library-free and the libc++ builds are equal (77, 209, 200, 72)")
need(all(o["emul_%s_abc" % t_]["ud2"] == 1 for t_ in ("c16", "c17", "c18", "c19", "c20", "c21", "c22", "c231", "ctrunk")),
     "library-free loop, checks on: every build has exactly one ud2")
need(vec("libswap_c19_lib18") and vec("libswap_c20_lib18") and vec("libswap_c21_lib18") and vec("libswap_c22_lib18")
     and not vec("libswap_c18_lib18") and not vec("libswap_c231_lib18") and not vec("libswap_ctrunk_lib18"),
     "libc++ 18.1.0 headers held fixed: clang 19 to 22 vectorize; clang 18, 23.1 and trunk do not")
need(not vec("libswap_c18_lib19"), "clang 18.1.0 with libc++ 19.1.0 headers: not vectorized")
need(o["libswap_c18_lib21"]["status"] == "compile error" and "__builtin_ctzg" in o["libswap_c18_lib21"]["detail"],
     "clang 18.1.0 with libc++ 21.1.0 headers: does not compile")
for n in ("libswap_c19_lib18", "libswap_c18_lib19"):
    want = "/clang-18.1.0/include/c++/v1/vector" if n.endswith("lib18") else "/clang-19.1.0/include/c++/v1/vector"
    need(want in text(n), "%s: -H shows the headers came from %s" % (n, want))
for n in ("libswap_c231_lib18", "libswap_ctrunk_lib18"):
    need("Early exit loop with store but no supported condition load" in o[n]["detail"], "%s: rejected as an early-exit loop with a store" % n)

# F9: clang 19 to 22, where the clamp first appears
umin, umin_idx = {}, {}
for ln in read("derived", "first_umin.txt").splitlines():
    mm = re.match(r"(\S+)\s+first appears in the output of: (?:#(\d+) (\w+)|\(never\))\s+\| in the IR handed to LoopVectorizePass: (\w+)", ln)
    if mm:
        umin[mm.group(1)] = (mm.group(3), mm.group(4) == "yes")
        umin_idx[mm.group(1)] = int(mm.group(2)) if mm.group(2) else None
need(all(umin["pipe_c%s_fast" % v] == ("LoopVectorizePass", False) for v in ("19", "20", "21")),
     "clang 19, 20, 21: the clamp first appears in LoopVectorize's output and is not in the IR handed to it")
need([umin_idx[n] for n in ("pipe_c19_fast", "pipe_c20_fast", "pipe_c21_fast", "pipe_c22_fast", "pipe_c22_nopred")] == [117, 118, 118, 63, 120],
     "first appearance of the clamp, by pass number: clang 19 #117, 20 #118, 21 #118, 22 #63, 22 with the option off #120")
need(umin["pipe_c22_fast"] == ("IndVarSimplifyPass", True), "clang 22: the clamp first appears in IndVarSimplify's output and is in the IR handed to the vectorizer")
need(umin["pipe_c22_nopred"] == ("LoopVectorizePass", False), "clang 22 with -indvars-predicate-loop-traps=false: the clamp first appears in LoopVectorize's output")
need(umin["pipe_c18_fast"] == (None, False) and umin["pipe_emul_c18_abc"] == (None, False), "clang 18: the clamp never appears in the pipeline")
need(analyze.lv_numbers("dbg_a22_nopred") == analyze.lv_numbers("dbg_a19_fast") and vec("dbg_a22_nopred") and vec("pipe_c22_nopred"),
     "clang 22 with the option off: scalar 11, width 2 costs 8, width 4 costs 4, exit compares 1 each and uniform (the clang 19 numbers), vectorized")
need(analyze.epilogue_reasons("dbg_a19_fast") == ["multiple exits"]
     and analyze.epilogue_reasons("dbg_a20_fast") == analyze.epilogue_reasons("dbg_a21_fast") == analyze.epilogue_reasons("dbg_a22_nopred") == ["not exiting from latch block"]
     and analyze.epilogue_reasons("dbg_a22_fast") == [],
     "scalar-epilogue reason: clang 19 'multiple exits'; clang 20, 21 and 22-with-option-off 'not exiting from latch block'; clang 22 default none")
commit2 = json.loads(read("llvm-src", "commit_39b0cbe69c.json"))
patch = next(f["patch"] for f in commit2["files"] if f["filename"].endswith("IndVarSimplify.cpp"))
need('+    "indvars-predicate-loop-traps", cl::Hidden, cl::init(true),' in patch and "+static cl::opt<bool> LoopPredicationTraps(" in patch
     and "-      if (I.mayHaveSideEffects())\n-        return false;" in patch,
     "commit 39b0cbe69c adds the hidden option indvars-predicate-loop-traps (default true) and replaces the unconditional bail-out on side effects")
sections = {}
for blk in read("llvm-src", "indvars_predicate_traps.txt").split("== tag llvmorg-")[1:]:
    sections[blk.split(" ", 1)[0]] = blk
need("indvars-predicate-loop-traps" not in sections["19.1.0"] and "indvars-predicate-loop-traps" not in sections["21.1.0"]
     and "indvars-predicate-loop-traps" in sections["22.1.0"] and "indvars-predicate-loop-traps" in sections["23.1.0"],
     "the option exists in the IndVarSimplify source of 22.1.0 and 23.1.0, not of 19.1.0 and 21.1.0")

# F10: clang 23.1 and trunk
need("Early exit loop with store but no supported condition load" in o["dbg_a23_fast"]["detail"], "clang 23.1: rejected as an early-exit loop with a store")
need("Complex writes to memory unsupported in early exit loops" in text("dbg_atrunk_fast") and "Complex writes to memory unsupported in early exit loops" in text("rev_atrunk_fast"),
     "assertions trunk: rejected with 'Complex writes to memory unsupported in early exit loops'")
rev = {n: analyze.revision(n) for n in ("pipe_ctrunk_fast", "libswap_ctrunk_lib18_v", "emul_ctrunk_abc_v", "hoist_ctrunk_bc_v", "restrict_ctrunk_abc_v",
                                         "rev_atrunk_fast", "licm_atrunk_fast", "paths_c18", "paths_a18", "paths_c19", "paths_a19")}
need(len({rev[n] for n in rev if n.endswith(("ctrunk_fast", "ctrunk_lib18_v", "ctrunk_abc_v", "ctrunk_bc_v"))}) == 1 and rev["pipe_ctrunk_fast"] == "efd4965724",
     "five clang_trunk answers made with -v: one revision, efd4965724")
need(rev["rev_atrunk_fast"] == rev["licm_atrunk_fast"] == "e633c7da8f" and rev["rev_atrunk_fast"] != rev["pipe_ctrunk_fast"],
     "two assertions-trunk answers made with -v: one revision, e633c7da8f, not the revision of clang_trunk")
need(analyze.installed_dir("rev_atrunk_fast") in text("dbg_atrunk_fast"),
     "the older assertions-trunk answer names the install directory of the answers with revision e633c7da8f")
need(rev["paths_c18"] == rev["paths_a18"] == "461274b81d" and rev["paths_c19"] == rev["paths_a19"] == "a4bf6cd7cf",
     "the assertions builds report the same LLVM revisions as the release builds (clang 18.1.0rc 461274b81d, clang 19.1.0 a4bf6cd7cf)")
need(all(analyze.installed_dir(n).endswith("-20261015/bin") for n in ("pipe_ctrunk_fast", "rev_atrunk_fast")),
     "both trunk builds are installed in directories dated 20261015")
need(all(analyze.build_line(n).startswith("clang version 24.0.0git") for n in ("pipe_ctrunk_fast", "rev_atrunk_fast")), "both trunk builds report clang version 24.0.0git")
for older, newer in (("libswap_ctrunk_lib18", "libswap_ctrunk_lib18_v"), ("emul_ctrunk_abc", "emul_ctrunk_abc_v"),
                     ("hoist_ctrunk_bc", "hoist_ctrunk_bc_v"), ("restrict_ctrunk_abc", "restrict_ctrunk_abc_v")):
    need((o[older]["status"], o[older]["detail"]) == (o[newer]["status"], o[newer]["detail"]), "%s: the answer made with -v gives the same outcome as the older answer" % older)
need("Cannot vectorize early exit loop with complex writes to memory" in o["pipe_ctrunk_fast"]["detail"]
     and "Early exit loop with store but no supported condition load" in o["libswap_ctrunk_lib18_v"]["detail"]
     and "Early exit loop with store but no supported condition load" in o["emul_ctrunk_abc_v"]["detail"],
     "clang_trunk efd4965724: 'complex writes to memory' for k08 with its own headers; 'no supported condition load' with libc++ 18.1.0 headers and library-free")
leg = {v: read("llvm-src", "legality_%s.txt" % v) for v in ("19.1.0", "20.1.0", "22.1.0", "23.1.0")}
need("could not determine number of loop iterations" in leg["19.1.0"] and "isVectorizableEarlyExitLoop" not in leg["19.1.0"],
     "LLVM 19.1.0: a non-computable backedge-taken count is a plain rejection, with no early-exit route")
need(all("isVectorizableEarlyExitLoop()" in leg[v] and "TheLoop->getExitingBlock()" in leg[v] for v in ("20.1.0", "22.1.0", "23.1.0")),
     "LLVM 20.1.0, 22.1.0, 23.1.0: a non-computable count with more than one exiting block goes to isVectorizableEarlyExitLoop()")
need("Early exit loop with store but no supported condition load" in leg["23.1.0"] and "Early exit loop with store but no supported condition load" in leg["22.1.0"]
     and "does not occur in this file" in leg["20.1.0"],
     "the 'no supported condition load' rejection is in the 22.1.0 and 23.1.0 sources, not in 20.1.0")
rows = {n: loadtrack.track(n) for n in ("pipe_c19_fast", "pipe_c22_fast", "pipe_c231_fast", "pipe_ctrunk_fast")}


def after_inlining(n):
    r_ = rows[n]
    k = max(i for i, x in enumerate(r_) if x[3] == 4)  # the last pass whose loop still holds the inlined bodies (4 blocks, 4 loads)
    return r_[k + 1:]


need(all(after_inlining(n) and all(x[3] == 0 for x in after_inlining(n)) for n in ("pipe_c19_fast", "pipe_c22_fast")),
     "clang 19 and 22: after the last pass whose loop holds the inlined bodies (4 blocks, 4 loads) and before the vectorizer, the innermost loop has 0 pointer loads inside")
need(all(after_inlining(n) and all(x[3] == 2 for x in after_inlining(n)) for n in ("pipe_c231_fast", "pipe_ctrunk_fast")),
     "clang 23.1 and trunk (efd4965724): after the last pass whose loop holds the inlined bodies and before the vectorizer, the innermost loop has 2 pointer loads inside")
need(umin["pipe_c231_fast"] == (None, False) and umin["pipe_ctrunk_fast"] == (None, False), "clang 23.1 and trunk: the clamp never appears before the vectorizer")
lic = {}
for blk in read("derived", "licm_hoisting.txt").split("== ")[1:]:
    lic[blk.split("\n", 1)[0]] = blk
need("load ptr, ptr %c" in lic["licm_a19_fast"] and "load ptr, ptr %b" in lic["licm_a19_fast"],
     "LICM, clang 19: hoists the pointer loads of both b and c out of the inner loop")
need(all("load ptr, ptr %b" in lic[n] and "load ptr, ptr %c" not in lic[n] and "getelementptr inbounds nuw i8, ptr %c, i64 8" in lic[n]
         for n in ("licm_a23_fast", "licm_atrunk_fast")),
     "LICM, clang 23.1 and assertions trunk: hoists the loads of b, and for c only the address of the end pointer, not its loads")
need(all(vec(n) for n in ("hoist_c19_bc", "hoist_c231_bc", "hoist_ctrunk_bc", "hoist_ctrunk_bc_v")) and not vec("hoist_c18_bc"),
     "library-free, pointer loads hoisted in the source: clang 19, 23.1, trunk vectorize, clang 18 does not")
need(all(vec(n) for n in ("restrict_c231_abc", "restrict_ctrunk_abc", "restrict_ctrunk_abc_v")) and not vec("restrict_c18_abc"),
     "library-free, c declared __restrict: clang 23.1 and trunk vectorize, clang 18 does not")
need(umin["pipe_hoist_c231"] == ("IndVarSimplifyPass", True) and umin["pipe_restrict_c231"] == ("IndVarSimplifyPass", True),
     "clang 23.1, library-free hoisted and restrict variants: the clamp first appears in IndVarSimplify's output and is in the IR handed to the vectorizer")
need(not vec("ptbaa_c231_off") and vec("ptbaa_c22_off"), "-fno-pointer-tbaa changes nothing for clang 23.1 or clang 22")
tb = read("derived", "tbaa_pointer_loads.txt")
need("emitfull_c19_fast    6 `load ptr`: 4 no !tbaa tag; 2 tagged, access type `any pointer`" in tb
     and "emitfull_c22_fast    6 `load ptr`: 4 no !tbaa tag; 2 tagged, access type `p1 int`" in tb
     and "emitfull_c231_fast   6 `load ptr`: 6 tagged, access type `p1 int`" in tb,
     "tagged pointer loads: access type `any pointer` in clang 19, `p1 int` in clang 22 and 23.1")

sweep = os.path.join(HERE, "..", "..", "..", "ce-sweep", "README.md")
if os.path.exists(sweep):
    rows_ = [ln for ln in open(sweep, encoding="utf-8").read().splitlines() if ln.startswith("| clang 1") and "| x86-64-v3 |" in ln]
    need(len(rows_) >= 3 and all("rev, stride2**" in ln and "matmul" not in ln.split("|")[5] for ln in rows_ if ln.split("|")[1].strip() in ("clang 16.0.0", "clang 17.0.1", "clang 18.1.0")),
         "ce-sweep/README.md: at x86-64-v3 matmul is not lost on clang 16, 17 and 18")

# F11: 32-bit indices
need(not vec("emul32_c18_abc") and vec("emul32_c19_abc"), "32-bit index variant: same outcome as the 64-bit one")
need("%cmp.not.i43 = icmp ult i64 %13, %5" in text("dbg_emul32_a18_abc"), "32-bit index variant: the compare in the log is still an i64 compare")

# Method: -g, tags
g0 = read("derived", "g0_comparison.txt")
need(g0.count(": identical;") == 2 and "DIFFERENT" not in g0
     and analyze._lv_lines("dbg_a18_fast") == analyze._lv_lines("dbg_a18_fast_g0") and analyze._lv_lines("dbg_a19_fast") == analyze._lv_lines("dbg_a19_fast_g0"),
     "-g0 appended: every LV line and remark of the clang 18 and clang 19 logs is the same after normalizing metadata ids")
need(all(ce.load(n)["response"]["compilationOptions"][0] == "-g" for n in rr.MANIFEST),
     "Compiler Explorer's first compiler option is -g in all %d saved answers" % len(rr.MANIFEST))
need("-g0" in ce.load("dbg_a18_fast_g0")["response"]["compilationOptions"], "the -g0 answers list -g0 among the options")

# 4. saved LLVM passages
src = os.path.join(HERE, "llvm-src")
if os.path.isdir(src):
    f18 = read("llvm-src", "collectLoopUniforms_18.1.0.cpp.txt")
    f19 = read("llvm-src", "collectLoopUniforms_19.1.0.cpp.txt")
    need("Latch->getTerminator()->getOperand(0)" in f18 and "getExitingBlocks(Exiting)" not in f18, "LLVM 18.1.0: only the latch branch condition starts the uniform worklist")
    need("TheLoop->getExitingBlocks(Exiting)" in f19, "LLVM 19.1.0: every exiting branch condition starts the uniform worklist")
    gic = read("llvm-src", "getInstructionCost_uniform_18.1.0.cpp.txt")
    need("if (isUniformAfterVectorization(I, VF))" in gic and "VF = ElementCount::getFixed(1);" in gic,
         "LLVM 18.1.0: an instruction that is uniform after vectorization is costed as a scalar")
    h = dict(ln.split()[::-1] for ln in read("llvm-src", "collectLoopUniforms_sha256.txt").splitlines())
    need(h["18.1.0"] == h["18.1.3"] and h["19.1.0"] == h["19.1.7"] and h["18.1.0"] != h["19.1.0"],
         "collectLoopUniforms is identical in 18.1.0 and 18.1.3, identical in 19.1.0 and 19.1.7, different between 18 and 19")
    need(h["commit-461274b81d86"] == h["18.1.0"] and h["commit-a4bf6cd7cfb1"] == h["19.1.0"],
         "collectLoopUniforms at the commits the Compiler Explorer 18.1.0 and 19.1.0 builds report is identical to the tag text of 18.1.0 and 19.1.0")
    c1 = json.loads(read("llvm-src", "commit_b6a8f5486b.json"))["commit"]
    c2 = json.loads(read("llvm-src", "commit_39b0cbe69c.json"))["commit"]
    need((c1["author"]["name"], c1["author"]["date"][:10]) == ("Florian Hahn", "2024-04-28") and (c2["author"]["name"], c2["author"]["date"][:10]) == ("Florian Mayer", "2025-10-16")
         and c1["message"].startswith("[LV] Consider all exit branch conditions uniform.") and "This also allowed the loop to be vectorized." in c2["message"],
         "the two commits: authors, dates and the quoted message lines")
    cit = json.loads(read("llvm-src", "commit_in_tag.json"))
    st = {(r_["commit"][:10], r_["tag"]): r_["status"] for r_ in cit["rows"]}
    need(st[("b6a8f5486b", "llvmorg-19.1.0")] == "ahead" and st[("b6a8f5486b", "llvmorg-19.1.7")] == "ahead"
         and all(st[("b6a8f5486b", "llvmorg-%s" % v)] == "diverged" for v in ("18.1.0", "18.1.3", "18.1.8")),
         "commit b6a8f5486b is in llvmorg-19.1.0 and 19.1.7 and not in llvmorg-18.1.0, 18.1.3 or 18.1.8")
    need(st[("39b0cbe69c", "llvmorg-22.1.0")] == "ahead" and st[("39b0cbe69c", "llvmorg-23.1.0")] == "ahead"
         and all(st[("39b0cbe69c", "llvmorg-%s" % v)] == "diverged" for v in ("19.1.0", "21.1.0", "21.1.8")),
         "commit 39b0cbe69c is in llvmorg-22.1.0 and 23.1.0 and not in llvmorg-19.1.0, 21.1.0 or 21.1.8")
    last = {k: [t_ for t_ in v if "-rc" not in t_][-1] for k, v in cit["tags_in_repository"].items()}
    need(last == {"18.1.x": "llvmorg-18.1.8", "21.1.x": "llvmorg-21.1.8"}, "the last 18.1.x tag in the repository is llvmorg-18.1.8 and the last 21.1.x tag is llvmorg-21.1.8")
    x86 = read("llvm-src", "x86_setcc_i64_18.1.0.txt")
    need("SSE2CostTbl" in x86 and "pcmpeqd/pcmpgtd expansion" in x86 and tbl[("SSE2CostTbl", "v2i64")] == 5
         and tbl[("SSE42CostTbl", "v2i64")] == 1 and tbl[("AVX2CostTbl", "v4i64")] == 1,
         "LLVM 18.1.0 X86 cost table: SSE2 expands the 64-bit vector compare (5), SSE4.2 has it (1), AVX2 has the 256-bit one (1)")
else:
    need(False, "llvm-src/ exists (run fetch_llvm_src.py)")

print("\n%d failure(s)" % len(failures))
sys.exit(1 if failures else 0)
