"""Builds the readable files in extracted/ from the saved answers in raw/. Offline: no request is sent.

    python excerpts.py

Every file starts with the list of raw files it was made from. Nothing here adds information: each line is
either copied from a raw answer or counted from it.
"""
import os
import re

import ce
import extract
import experiments as E

OUT = os.path.join(ce.HERE, "extracted")
NL = chr(10)
LOOP_FN = re.compile(r"\b(kern_k\d\d_\w+|v[23]?_\w+)\(")


# ---------------------------------------------------------------- remarks
def loop_lines(source_text):
    """{1-based line of a // LOOP marker: function name} for a source file."""
    out, cur = {}, None
    for i, ln in enumerate(source_text.splitlines(), 1):
        m = LOOP_FN.search(ln)
        if m and ln.startswith("__attribute__"):
            cur = m.group(1)
        if "// LOOP" in ln and cur:
            out[i] = cur
    return out


def remark_of(name):
    """{function: 'vectorized WxI' or 'not vectorized: reason'} from the loop-vectorize remarks of raw/<name>."""
    rec = ce.load(name)
    with open(os.path.join(ce.HERE, rec["source_path"]), encoding="utf-8") as f:
        lines = loop_lines(f.read())
    res = {fn: None for fn in lines.values()}
    reason = {}
    for ln in ce.stderr_text(rec).splitlines():
        m = re.match(r"<source>:(\d+):\d+: remark: (.*?) \[-Rpass(?:-missed|-analysis)?=loop-vectorize\]$", ln)
        if not m or int(m.group(1)) not in lines:
            continue
        fn, msg = lines[int(m.group(1))], m.group(2)
        v = re.match(r"vectorized loop \(vectorization width: (\d+), interleaved count: (\d+)\)", msg)
        if v:
            res[fn] = "vectorized %sx%s" % (v.group(1), v.group(2))
        elif msg.startswith("loop not vectorized: "):
            reason[fn] = msg[len("loop not vectorized: "):]
        elif msg == "loop not vectorized" and fn not in reason:
            reason[fn] = ""
        elif "vectorization is not beneficial" in msg:
            reason[fn] = msg
    for fn in res:
        if res[fn] is None:
            res[fn] = "not vectorized" + (": " + reason[fn] if reason.get(fn) else "")
    return res


def remarks_table():
    cols = [("18.1.0 NONE", "A-c18-%s-none"), ("18.1.0", "A-c18-%s-fast"),
            ("19.1.0 NONE", "A-c19-%s-none"), ("19.1.0", "A-c19-%s-fast"),
            ("20.1.0 NONE", "A-c20-%s-none"), ("20.1.0", "A-c20-%s-fast"),
            ("21.1.0 NONE", "A-c21-%s-none"), ("21.1.0", "A-c21-%s-fast"),
            ("trunk NONE", "A-ctrunk-%s-none"), ("trunk", "A-ctrunk-%s-fast")]
    out, used = [], []
    for src in ("kernels", "variants", "variants2", "variants3"):
        data = {}
        for label, pat in cols:
            name = pat % src
            if os.path.exists(ce._path(name)):
                data[label] = remark_of(name)
                used.append(name)
        fns = list(next(iter(data.values())).keys())
        out.append("## %s (sources/%s.cpp), libc++ hardening FAST unless the column says NONE" % (src, src))
        out.append("")
        for fn in fns:
            out.append(fn)
            for label, _ in cols:
                if label in data:
                    out.append("    %-12s %s" % (label, data[label][fn]))
        out.append("")
    return used, NL.join(out)


# ---------------------------------------------------------------- IR before the loop vectorizer
def clean_ir(body):
    keep = []
    for ln in body.splitlines():
        if ln.startswith("; Function Attrs") or ln.strip() == "":
            continue
        ln = re.sub(r", !(?:dbg|tbaa|prof|llvm\.loop|srcloc|noundef) !\d+", "", ln)
        ln = re.sub(r" !dbg !\d+", "", ln)
        keep.append(ln)
    return NL.join(keep)


def ir_before_lv(name, wanted):
    dumps = extract.ir_dumps(name)
    out = []
    for sym, body in dumps.items():
        short = re.sub(r"^_Z\d+", "", sym)
        short = re.split(r"R?K?N?St3", short)[0]
        if wanted is None or any(w in sym for w in wanted):
            out.append(clean_ir(body))
            out.append("")
    return NL.join(out)


# ---------------------------------------------------------------- pipeline
def text_of(lines):
    return [x["text"] if isinstance(x, dict) else x for x in lines]


def pipeline_functions(name):
    return ce.load(name)["response"]["optPipelineOutput"]["results"]


def clean_pipeline_ir(lines):
    out = []
    for ln in text_of(lines):
        if "llvm.dbg" in ln or ln.startswith("define") or ln.startswith("; Function Attrs") or not ln.strip():
            continue
        ln = re.sub(r", !(?:dbg|tbaa|prof|llvm\.loop|srcloc|noundef) !\d+", "", ln)
        out.append(ln)
    return NL.join(out)


def pipeline_text(name, kernels):
    res = pipeline_functions(name)
    out = []
    for fn, passes in res.items():
        if not any(k in fn for k in kernels):
            continue
        short = re.sub(r"^_Z\d+", "", fn)[:20]
        out.append("=" * 100)
        out.append("function %s" % fn)
        out.append("passes of the loop pipeline and the vectorizer (index, name, whether the IR changed):")
        order = []
        for i, e in enumerate(passes):
            if e["machine"]:
                break
            nm = e["name"].split(" on ")[0]
            if nm.startswith("Loop") or nm in ("IndVarSimplifyPass", "SimpleLoopUnswitchPass", "LICMPass",
                                                 "ConstraintEliminationPass", "JumpThreadingPass",
                                                 "InstCombinePass", "SimplifyCFGPass"):
                order.append("%d %s%s" % (i, nm, " *" if e["irChanged"] else ""))
        out.append("  " + "; ".join(order))
        for i, e in enumerate(passes):
            if e["machine"]:
                break
            if e["name"].startswith("IndVarSimplifyPass") and e["irChanged"]:
                out.append("-" * 100)
                out.append("IR before pass %d (%s)" % (i, e["name"].split(" on ")[0]))
                out.append(clean_pipeline_ir(e["before"]))
                out.append("-" * 100)
                out.append("IR after pass %d (%s)" % (i, e["name"].split(" on ")[0]))
                out.append(clean_pipeline_ir(e["after"]))
    return NL.join(out)


def trap_events(name):
    """Per function: the passes at which the number of `br i1 true` and of trap calls changes."""
    res = pipeline_functions(name)
    out = []
    for fn, passes in res.items():
        if not fn.startswith("_Z") or not re.match(r"^_Z\d+(kern_k|v_|v2_|v3_)", fn):
            continue
        short = re.sub(r"^_Z\d+", "", fn)
        short = re.split(r"R?K?N?St3", short)[0]
        ev, prev_t, prev_b = [], None, None
        for i, e in enumerate(passes):
            if e["machine"]:
                break
            a = text_of(e["after"])
            t = sum(1 for ln in a if "call void @llvm.trap" in ln)
            b = sum(1 for ln in a if "br i1 true" in ln)
            if prev_t is not None and (t != prev_t or b != prev_b):
                ev.append("%s (%d): trap calls %d->%d, `br i1 true` %d->%d" %
                          (e["name"].split(" on ")[0], i, prev_t, t, prev_b, b))
            prev_t, prev_b = t, b
        out.append(short)
        out.extend("    " + x for x in ev)
    return NL.join(["# Counts come from the IR text the pipeline viewer prints after each pass. A function pass prints the whole",
                    "# function, a loop pass prints only the loop, so the counts also move when the pass kind changes.",
                    ""] + out)


# ---------------------------------------------------------------- ScalarEvolution
def scev_blocks(name):
    """{function symbol: {'exits': [str], 'btc': str}} from the output of print<scalar-evolution>."""
    t = ce.stderr_text(ce.load(name))
    out = {}
    for b in re.split(r"(?m)^(?=Printing analysis)", t):
        m = re.match(r"Printing analysis .*? for function '(\S+)'", b)
        if not m:
            continue
        i = b.find("Determining loop execution counts")
        part = b[i:]
        exits = re.findall(r"(?m)^  exit count for (\S+): (.*)$", part)
        btc = None
        for ln in part.splitlines():
            mm = re.match(r"Loop \S+: (?:<multiple exits> )?(backedge-taken count is .*|Unpredictable backedge-taken count\.)$", ln)
            if mm and "constant max" not in ln and "symbolic max" not in ln and "Predicated" not in ln:
                btc = mm.group(1)
                break
        out[m.group(1)] = {"exits": exits, "btc": btc}
    return out


def short_name(sym):
    s = re.sub(r"^_Z\d+", "", sym)
    return re.split(r"R?K?N?St3", s)[0]


def scev_table():
    sets = [("c18", "kernels", "fast"), ("c18", "kernels", "none"), ("c18", "variants", "fast"),
            ("c18", "variants2", "fast"), ("c18", "variants3", "fast"), ("c19", "kernels", "fast"),
            ("c20", "kernels", "fast"), ("c20", "variants", "fast"), ("ctrunk", "kernels", "fast")]
    used, out = [], []
    for short, src, mode in sets:
        name = "E-%s-%s-%s-scev" % (short, src, mode)
        if not os.path.exists(ce._path(name)):
            continue
        used.append(name)
        rem = None
        rname = "A-%s-%s-%s" % (short, src, mode)
        if os.path.exists(ce._path(rname)):
            used.append(rname)
            rem = remark_of(rname)
        out.append("## %s, %s, hardening %s (ScalarEvolution of opt on the IR just before the loop vectorizer; remark of clang)" %
                   (short, src, mode.upper()))
        out.append("")
        tally = {"computable and vectorized": 0, "not computable and not vectorized": 0, "mismatch": 0}
        for sym, d in scev_blocks(name).items():
            fn = short_name(sym)
            exits = ", ".join(("COULDNOTCOMPUTE" if "COULDNOTCOMPUTE" in c else c) + " [%s]" % bb for bb, c in d["exits"]) \
                if d["exits"] else "(single exit)"
            btc = d["btc"] or "?"
            btc = "NOT computable" if btc.startswith("Unpredictable") else "computable"
            r = rem.get(fn) if rem else None
            out.append("%-18s backedge-taken count %-15s exits: %s" % (fn, btc, exits))
            if r:
                out.append("%-18s clang: %s" % ("", r))
                ok = btc == "computable"
                vec = r.startswith("vectorized")
                if ok and vec:
                    tally["computable and vectorized"] += 1
                elif not ok and not vec:
                    tally["not computable and not vectorized"] += 1
                else:
                    tally["mismatch"] += 1
        if rem:
            out.append("tally: " + ", ".join("%s %d" % (k, v) for k, v in tally.items()))
        out.append("")
    return used, NL.join(out)


# ---------------------------------------------------------------- debug output of the assertion builds
def grep_lines(name, patterns, context_before=0, context_after=0):
    t = ce.stderr_text(ce.load(name)).splitlines()
    out = []
    for i, ln in enumerate(t):
        if any(re.search(p, ln) for p in patterns):
            for j in range(max(0, i - context_before), min(len(t), i + 1 + context_after)):
                if not out or out[-1] != t[j][:300]:
                    out.append(t[j][:300])
    return out


def debug_text():
    parts = []
    parts.append("# clang 18.1.0 (assertions build), -mllvm -debug-only=indvars: the line about an exit whose count is unknown (the compare is the reverse loop's check; see README)")
    parts += grep_lines("D-c18assert-kernels-fast-indvars", [r"Unknown exit count"], 0, 0)
    parts.append("")
    parts.append("# clang 18.1.0 (assertions build), -mllvm -debug-only=loop-accesses")
    parts += grep_lines("D-c18assert-kernels-fast-laa", [r"kern_k0[45]", r"could not compute"], 0)
    parts.append("")
    parts.append("# clang 18.1.0 (assertions build), -mllvm -debug-only=loop-vectorize,loop-accesses in one run, with the compiler's")
    parts.append("# remarks in between: the order of the messages for each loop. For the two rejected loops the loop-access analysis's line")
    parts.append("# comes first, then the remark, then `LV: Can't vectorize due to memory conflicts`. On this build `LV: We can vectorize")
    parts.append("# this loop!` is also printed for those two loops, right before `LV: Not vectorizing: Cannot prove legality.`. Why that")
    parts.append("# line is printed there is NOT ESTABLISHED by these files; the verdict is the `Not vectorizing` line and the remark")
    parts.append("# `loop not vectorized`.")
    parts += grep_lines("D-c18assert-kernels-fast-lv-laa", [r"LV: Checking a loop", r"LAA: Found a loop", r"LAA: SCEV could not",
                                                            r"Found an induction variable", r"Did not find one integer",
                                                            r"Can't vectorize due to", r"Not vectorizing", r"We can vectorize",
                                                            r"remark: (loop not vectorized|vectorized loop)"], 0)
    parts.append("")
    parts.append("# clang 20.1.0 (assertions build), -mllvm -debug-only=loop-vectorize: the verdict of each loop")
    parts += grep_lines("D-c20assert-kernels-fast-lv", [r"LV: Checking a loop", r"Not vectorizing", r"We can vectorize",
                                                         r"requires scalar epilogue"], 0)
    return NL.join(parts)


# ---------------------------------------------------------------- opt: loop vectorizer alone, or unswitching first
def vector_body_counts(name):
    asm = ce.asm_text(ce.load(name)).splitlines()
    cur, res = None, {}
    for ln in asm:
        m = re.match(r"define .*@(\S+?)\(", ln)
        if m:
            cur = short_name(m.group(1))
            res[cur] = 0
        elif cur and ln.strip().startswith("vector.body"):
            res[cur] += 1
    return res


def unswitch_text():
    out = []
    used = []
    for short in ("c18", "c20", "ctrunk"):
        a, b = "F-%s-kernels-fast-lv-only" % short, "F-%s-kernels-fast-unswitch-then-lv" % short
        if not (os.path.exists(ce._path(a)) and os.path.exists(ce._path(b))):
            continue
        used += [a, b]
        ca, cb = vector_body_counts(a), vector_body_counts(b)
        out.append("## %s: opt run on the IR just before the loop vectorizer" % short)
        out.append("%-20s %-28s %s" % ("function", "loop-vectorize only", "simple-loop-unswitch, then loop-vectorize"))
        for fn in ca:
            out.append("%-20s %-28s %s" % (fn, "vectorized" if ca[fn] else "not vectorized",
                                           "vectorized" if cb[fn] else "not vectorized"))
        out.append("remarks, loop-vectorize only:")
        out += ["    " + ln for ln in ce.stderr_text(ce.load(a)).splitlines()]
        out.append("remarks, unswitch then loop-vectorize:")
        out += ["    " + ln for ln in ce.stderr_text(ce.load(b)).splitlines()]
        out.append("")
    # structure of the reverse loop after unswitching (clang 18)
    rec = ce.load("F-c18-kernels-fast-unswitch-then-lv")
    asm = ce.asm_text(rec).splitlines()
    grab, body = False, []
    for ln in asm:
        if ln.startswith("define") and "kern_k04_rev" in ln:
            grab = True
        if grab:
            body.append(ln)
            if ln.strip() == "}":
                break
    out.append("## clang 18 opt, simple-loop-unswitch then loop-vectorize: the reverse loop's IR (raw/F-c18-kernels-fast-unswitch-then-lv.json)")
    out.append(clean_ir(NL.join(body)))
    return used, NL.join(out)


# ---------------------------------------------------------------- the checks in the loops: compare form and exit count
def _parse_blocks(text):
    """({label: [instruction lines]}, {value name: its defining line}) of one sanitized function body."""
    blocks, defs, cur = {}, {}, None
    for ln in text.splitlines():
        m = re.match(r"^(\w+):", ln)
        if m:
            cur = m.group(1)
            blocks[cur] = []
            continue
        if cur and ln.startswith("  "):
            ln = ln.strip()
            blocks[cur].append(ln)
            m2 = re.match(r"(%[\w.]+) = (.*)", ln)
            if m2:
                defs[m2.group(1)] = ln
    return blocks, defs


def trap_checks(ir_name, scev_name):
    """{function: [(exit block, terminator, exit count, [defining lines of the condition and its operands])]}
    for the loop exits whose branch leads to a block that calls llvm.trap. Exit blocks are the ones ScalarEvolution
    lists as `exit count for bbN`; the IR is the sanitized dump of raw/<ir_name>."""
    sc = scev_blocks(scev_name)
    out = {}
    for sym, body in extract.ir_dumps(ir_name).items():
        text, _ = extract.sanitize(body)
        blocks, defs = _parse_blocks(text)
        res = []
        for bb, count in sc[sym]["exits"]:
            term = blocks[bb][-1]
            m = re.match(r"br i1 (%[\w.]+), label %(\w+), label %(\w+)", term)
            if not m or not any(any("llvm.trap" in x for x in blocks[t]) for t in (m.group(2), m.group(3))):
                continue
            seen, lines = set(), []

            def walk(v, depth):
                if v in seen or v not in defs or depth > 20:
                    return
                seen.add(v)
                lines.append(defs[v])
                for o in re.findall(r"%[\w.]+", defs[v].split("=", 1)[1]):
                    walk(o, depth + 1)

            walk(m.group(1), 0)
            res.append((bb, term, count, lines))
        out[short_name(sym)] = res
    return out


CHECK_SETS = [("kernels", "B-c18-kernels-fast-ir", "E-c18-kernels-fast-scev", "A-c18-kernels-fast"),
              ("variants", "B-c18-variants-fast-ir", "E-c18-variants-fast-scev", "A-c18-variants-fast"),
              ("variants2", "B-c18-variants2-fast-ir", "E-c18-variants2-fast-scev", "A-c18-variants2-fast"),
              ("variants3", "B-c18-variants3-fast-ir", "E-c18-variants3-fast-scev", "A-c18-variants3-fast")]


def checks_text():
    """For every loop of clang 18.1.0 FAST: each in-loop trap branch, its exit count, and the instructions that compute
    its condition (the whole chain of operand definitions inside the function)."""
    used, out = [], []
    for src, ir, ev, rem in CHECK_SETS:
        used += [ir, ev, rem]
        r = remark_of(rem)
        out.append("## %s (sources/%s.cpp), clang 18.1.0, hardening FAST, IR just before the loop vectorizer" % (src, src))
        out.append("")
        for fn, checks in trap_checks(ir, ev).items():
            out.append("%s   (clang: %s)" % (fn, r[fn]))
            if not checks:
                out.append("    no trap branch among the loop's exits")
            for bb, term, count, lines in checks:
                out.append("    exit %s: %s" % (bb, term))
                out.append("    exit count: %s" % ("COULDNOTCOMPUTE" if "COULDNOTCOMPUTE" in count else count))
                for ln in lines:
                    out.append("        " + ln)
            out.append("")
    return used, NL.join(out)


# ---------------------------------------------------------------- hand-written IR: one stride-2 loop, different bounds
H_FUNCS = [("full", "f_full_%s"), ("ashr2", "f_ashr2_%s"), ("lshr1", "f_lshr1_%s"), ("and62", "f_and62_%s"),
           ("umin40", "f_umin40_%s"), ("ptr_ashr", "f_ptr_ashr_%s"), ("ptr_lshr", "f_ptr_lshr_%s")]
H_OPTS = [("opt 18.1.0", "H-opt1810-s2-bound-scev"), ("opt 20.1.0", "H-opt2010-s2-bound-scev"),
          ("opt trunk", "H-opttrunk-s2-bound-scev")]


def h_scev(name):
    """{function: exit count of the checked exit (the exit named `loop`)} from the print<scalar-evolution> answer."""
    t = ce.stderr_text(ce.load(name))
    res = {}
    for b in re.split(r"(?m)^(?=Printing analysis)", t):
        m = re.match(r"Printing analysis .*? for function '(\S+)'", b)
        if not m:
            continue
        part = b[b.find("Determining loop execution counts"):]
        c = re.search(r"(?m)^  exit count for loop: (.*)$", part)
        res[m.group(1)] = c.group(1)
    return res


def h_lv(name="H-opt1810-s2-bound-lv"):
    """{function: True when the loop vectorizer made a vector.body} from the opt answer."""
    cur, res = None, {}
    for ln in ce.asm_text(ce.load(name)).splitlines():
        m = re.match(r"define .*@(\w+)\(", ln)
        if m:
            cur = m.group(1)
            res[cur] = False
        elif cur and ln.strip().startswith("vector.body"):
            res[cur] = True
    return res


def handwritten_text():
    used = [n for _, n in H_OPTS] + ["H-opt1810-s2-bound-lv"]
    out = ["# One stride-2 loop, one check `bound > ((i << 1) | 1)`, the same in every function (sources/handwritten/s2-bound.ll).",
           "# Only the expression of the bound differs, and whether the shift has `nuw`.",
           "# Columns: ScalarEvolution's count of the checked exit on opt 18.1.0, 20.1.0 and trunk (`no` = ***COULDNOTCOMPUTE***);",
           "# then whether `opt -passes=loop-vectorize` (18.1.0) made a vector.body; then the exit count on opt 18.1.0.", ""]
    scev = {n: h_scev(n) for _, n in H_OPTS}
    lv = h_lv()
    out.append("%-10s %-6s %-8s %-8s %-8s %-11s %s" % ("bound", "shift", "18.1.0", "20.1.0", "trunk", "vectorized", "exit count on opt 18.1.0"))
    for flags in ("plain", "nuw"):
        for bound, pat in H_FUNCS:
            fn = pat % flags
            cells = ["no" if "COULDNOTCOMPUTE" in scev[n][fn] else "count" for _, n in H_OPTS]
            out.append("%-10s %-6s %-8s %-8s %-8s %-11s %s" % (bound, flags, cells[0], cells[1], cells[2],
                                                              "yes" if lv[fn] else "no", scev[H_OPTS[0][1]][fn][:100]))
    return used, NL.join(out)


# ---------------------------------------------------------------- the full -O2 pipeline of opt 18.1.0 with and without unswitching
FULL_RUNS = [("control", "G-opt1810-full-O2-control"), ("unswitch after indvars", "G-opt1810-full-O2-unswitch-after-indvars"),
             ("unswitch before vectorizer", "G-opt1810-full-O2-unswitch-before-lv")]


def full_pipeline_text():
    used = ["G-c18-kernels-fast-frontend-ir", "G-opt1810-print-O2-pipeline"] + [n for _, n in FULL_RUNS]
    pipes = E.full_pipelines()
    out = ["# Input: the IR clang 18.1.0 prints with -O2 -disable-llvm-passes (sources/ir/c18-kernels-fast-frontend.ll).",
           "# Pipeline: the text `opt -passes=default<O2> -print-pipeline-passes` prints (raw/G-opt1810-print-O2-pipeline.json),",
           "# run unchanged, with `%s` inserted right after `%s`, or just before `%s`." % (E.UNSWITCH, E.INDVARS_GROUP, E.LV_PASS),
           ""]
    names = ["kern_k01_sum_fwd", "kern_k02_add_fwd", "kern_k03_stencil", "kern_k04_rev", "kern_k05_stride2"]
    counts = {tag: {short_name(k): v for k, v in vector_body_counts(n).items()} for tag, n in FULL_RUNS}
    out.append("%-18s %s" % ("function", "  ".join("%-26s" % tag for tag, _ in FULL_RUNS)))
    for fn in names:
        out.append("%-18s %s" % (fn, "  ".join("%-26s" % ("vectorized" if counts[tag][fn] else "not vectorized") for tag, _ in FULL_RUNS)))
    out.append("")
    for tag, n in FULL_RUNS:
        out.append("remarks, %s:" % tag)
        out += ["    " + ln for ln in ce.stderr_text(ce.load(n)).splitlines()]
        out.append("")
    out.append("simple-loop-unswitch passes in each pipeline text, with their character offsets; offsets of the indvars group and of loop-vectorize:")
    for tag, key in (("control", "control"), ("unswitch after indvars", "unswitch-after-indvars"),
                     ("unswitch before vectorizer", "unswitch-before-lv")):
        p = pipes[key]
        out.append("    %-26s unswitch at %s; indvars at %d; loop-vectorize at %d" % (
            tag, [m.start() for m in re.finditer(re.escape("simple-loop-unswitch<"), p)], p.index("indvars,"),
            p.index("loop-vectorize<")))
    return used, NL.join(out)


# ---------------------------------------------------------------- IR shape across compilers
def normalized_function(body):
    """Instruction lines of one dump, with the spellings that differ between compiler versions made equal:
    no debug, TBAA, branch-weight or loop metadata; no `llvm.assume` calls; ptrtoaddr as ptrtoint; `inbounds nuw` as
    `inbounds`; the vector's member access as a byte offset; `icmp ugt a, b` as `icmp ult b, a`; values numbered by first
    appearance."""
    lines = []
    for ln in body.splitlines():
        if ln.startswith(";") or ln.startswith("define") or ln.startswith("}") or not ln.strip():
            continue
        ln = re.sub(r", !(?:dbg|tbaa|prof|llvm\.loop|srcloc|noundef|nonnull|range|align) !\d+", "", ln)
        ln = re.sub(r" !dbg !\d+", "", ln)
        if "@llvm.assume" in ln:
            continue
        ln = ln.replace("ptrtoaddr", "ptrtoint").replace("getelementptr inbounds nuw", "getelementptr inbounds")
        ln = re.sub(r" #\d+\b", "", ln)
        ln = ln.replace("[4 x i8]", "i32")
        ln = re.sub(r'getelementptr inbounds %"class\.std::__1::vector", ptr (%\d+), i64 0, i32 1',
                    r"getelementptr inbounds i8, ptr \1, i64 8", ln)
        ln = re.sub(r"icmp ugt (i64) (%\d+), (%\d+)", r"icmp ult \1 \3, \2", ln)
        lines.append(re.sub(r";.*", "", ln).strip())
    num = {}

    def ren(m):
        num.setdefault(m.group(0), "%%v%d" % len(num))
        return num[m.group(0)]

    return [re.sub(r"%\d+", ren, ln) for ln in lines]


IR_SHAPE = [("18.1.0", "B-c18-kernels-fast-ir"), ("19.1.0", "B-c19-kernels-fast-ir"), ("20.1.0", "B-c20-kernels-fast-ir"),
            ("trunk", "B-ctrunk-kernels-fast-ir")]
IR_SHAPE_FUNCS = ["kern_k01_sum_fwd", "kern_k02_add_fwd", "kern_k03_stencil", "kern_k04_rev", "kern_k05_stride2"]


def ir_shape():
    """{(version, function): normalized instruction lines} for the five project loops."""
    res = {}
    for ver, name in IR_SHAPE:
        for sym, body in extract.ir_dumps(name).items():
            res[(ver, short_name(sym))] = normalized_function(body)
    return res


def raw_features(name):
    """{function: (llvm.assume calls, ptrtoaddr instructions, ptrtoint instructions)} in the dumps of raw/<name>."""
    out = {}
    for sym, body in extract.ir_dumps(name).items():
        out[short_name(sym)] = (body.count("call void @llvm.assume("), body.count("= ptrtoaddr "), body.count("= ptrtoint "))
    return out


def ir_shape_text():
    import difflib
    used = [n for _, n in IR_SHAPE]
    shape = ir_shape()
    out = ["# The IR just before the loop vectorizer for the five project loops, clang 18.1.0 against 19.1.0, 20.1.0 and trunk (hardening FAST).",
           "# Each function is reduced to its instruction lines with these spellings made equal: no debug, TBAA, branch-weight or",
           "# loop metadata; no `llvm.assume` calls; `ptrtoaddr` as `ptrtoint`; `inbounds nuw` as `inbounds`; the vector's member",
           "# access written as a byte offset; `icmp ugt a, b` as `icmp ult b, a`; values numbered by first appearance.",
           "# `same` means the lists are identical, so the blocks, the operations, the operands and the trap branches agree.", ""]
    for fn in IR_SHAPE_FUNCS:
        base = shape[("18.1.0", fn)]
        for ver, _ in IR_SHAPE[1:]:
            o = shape[(ver, fn)]
            if o == base:
                out.append("%-18s 18.1.0 against %-6s same (%d lines)" % (fn, ver, len(base)))
            else:
                out.append("%-18s 18.1.0 against %-6s differs:" % (fn, ver))
                for ln in difflib.unified_diff(base, o, lineterm="", n=0):
                    if not ln.startswith(("---", "+++", "@@")):
                        out.append("        " + ln)
    out.append("")
    out.append("In the raw dumps (every assume call has a `separate_storage` operand bundle), per function: llvm.assume calls, ptrtoaddr, ptrtoint:")
    for ver, name in IR_SHAPE:
        f = raw_features(name)
        out.append("    %-7s " % ver + "; ".join("%s: %d, %d, %d" % ((fn.replace("kern_", ""),) + f[fn]) for fn in IR_SHAPE_FUNCS[3:]))
    return used, NL.join(out)


# ---------------------------------------------------------------- metadata the opt inputs lose
METADATA_KINDS = ["dbg", "tbaa", "prof", "llvm.loop", "srcloc", "noundef", "nonnull", "range", "align"]
OPT_INPUTS = ["B-c18-kernels-fast-ir", "B-c18-kernels-none-ir", "B-c18-variants-fast-ir", "B-c18-variants2-fast-ir",
              "B-c18-variants3-fast-ir", "B-c19-kernels-fast-ir", "B-c20-kernels-fast-ir", "B-c20-variants-fast-ir",
              "B-ctrunk-kernels-fast-ir"]


def metadata_counts(name):
    """({kind: occurrences}, call-site attribute groups) in the IR dumps of raw/<name>, before extract.sanitize."""
    kinds = {k: 0 for k in METADATA_KINDS}
    groups = 0
    for _, body in extract.ir_dumps(name).items():
        for k in re.findall(r"[,\s]!(\w[\w.]*) !\d+", body):
            if k in kinds:
                kinds[k] += 1
        groups += len(re.findall(r"(?m)^  .* #\d+(?= |,|$)", body))
    return kinds, groups


def metadata_text():
    out = ["# What extract.sanitize removes from the IR dumps that become the input of `opt` (groups E and F), and how often each kind",
           "# occurs in each dump: metadata attachments `!kind !N` and call-site attribute groups (` #N` on an instruction).",
           "# Function attributes, instruction flags and operand bundles are kept.", ""]
    out.append("%-30s %s  %s" % ("raw answer", " ".join("%-6s" % k[:6] for k in METADATA_KINDS), "call-site groups"))
    for name in OPT_INPUTS:
        kinds, groups = metadata_counts(name)
        out.append("%-30s %s  %d" % (name, " ".join("%-6d" % kinds[k] for k in METADATA_KINDS), groups))
    return OPT_INPUTS, NL.join(out)


# ---------------------------------------------------------------- which build served the trunk answers
def versions_text():
    used = ["V-ctrunk-version", "V-opttrunk-version"]
    out = ["# The version lines Compiler Explorer's trunk compiler and trunk opt printed when asked with --version, with the time of that request.",
           "# The earlier trunk answers carry no version line; the request times of all trunk answers are listed below. Whether the",
           "# same build served every trunk request is NOT ESTABLISHED by these files.", ""]
    for n in used:
        rec = ce.load(n)
        out.append("%s (%s)" % (n, rec["fetched_at"]))
        out += ["    " + ln for ln in ce.stdout_text(rec).splitlines()]
    out.append("")
    out.append("requests to trunk compilers, by time (UTC):")
    rows = []
    for e in E.all_experiments():
        if e["compiler_id"] in ("clang_trunk", "opttrunk") and os.path.exists(ce._path(e["name"])):
            rows.append((ce.load(e["name"])["fetched_at"], e["name"]))
    out += ["    %s  %s" % r for r in sorted(rows)]
    return used, NL.join(out)


def asm_function(name, kernel):
    """The assembly text of one kern_* function from raw/<name> (labels and instructions, as Compiler Explorer printed them)."""
    lines = ce.asm_text(ce.load(name)).splitlines()
    out, grab = [], False
    for ln in lines:
        if ln and not ln[0].isspace() and ln.rstrip().endswith(":") and not ln.startswith("."):
            grab = ln.startswith("kern_" + kernel)
        if grab:
            out.append(ln)
    return NL.join(out)


def main(out_dir=None):
    global OUT
    if out_dir:
        OUT = out_dir
    os.makedirs(OUT, exist_ok=True)

    def write(name, header_files, text):
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline=NL) as f:
            f.write("# Made by excerpts.py from: %s" % ", ".join("raw/" + h for h in header_files) + NL)
            f.write(text.rstrip() + NL)
        print("wrote extracted/" + name)

    used, text = remarks_table()
    write("remarks.txt", used, text)
    used, text = scev_table()
    write("scalar-evolution.txt", used, text)
    write("ir-before-loop-vectorizer-clang18-fast.txt", ["B-c18-kernels-fast-ir"],
          ir_before_lv("B-c18-kernels-fast-ir", None))
    write("ir-before-loop-vectorizer-clang18-none.txt", ["B-c18-kernels-none-ir"],
          ir_before_lv("B-c18-kernels-none-ir", ["k04", "k05", "k02"]))
    write("ir-before-loop-vectorizer-clang20-fast.txt", ["B-c20-kernels-fast-ir"],
          ir_before_lv("B-c20-kernels-fast-ir", ["k04", "k05"]))
    write("ir-before-loop-vectorizer-trunk-fast.txt", ["B-ctrunk-kernels-fast-ir"],
          ir_before_lv("B-ctrunk-kernels-fast-ir", ["k04", "k05"]))
    write("pipeline-clang18-fast.txt", ["C-c18-kernels-fast-pipeline"],
          pipeline_text("C-c18-kernels-fast-pipeline", ["kern_k02", "kern_k04", "kern_k05"]))
    write("pipeline-clang20-fast.txt", ["C-c20-kernels-fast-pipeline"],
          pipeline_text("C-c20-kernels-fast-pipeline", ["kern_k02", "kern_k04", "kern_k05"]))
    write("pass-events-clang18-fast.txt", ["C-c18-kernels-fast-pipeline", "C-c18-variants-fast-pipeline"],
          "# kernels" + NL + trap_events("C-c18-kernels-fast-pipeline") + NL + "# variants" + NL +
          trap_events("C-c18-variants-fast-pipeline"))
    write("debug-output.txt", ["D-c18assert-kernels-fast-indvars", "D-c18assert-kernels-fast-laa",
                               "D-c18assert-kernels-fast-lv-laa", "D-c20assert-kernels-fast-lv"], debug_text())
    write("asm-clang18.txt", ["A-c18-kernels-fast", "A-c18-kernels-none"],
          (NL + NL).join("# %s, hardening %s" % (k, m.upper()) + NL + asm_function("A-c18-kernels-%s" % m, k)
                       for k, m in (("k02_add_fwd", "fast"), ("k04_rev", "none"), ("k04_rev", "fast"),
                                    ("k05_stride2", "fast"))))
    used, text = unswitch_text()
    write("unswitch-before-vectorizer.txt", used, text)
    used, text = checks_text()
    write("checks-in-loops.txt", used, text)
    used, text = handwritten_text()
    write("handwritten-bound.txt", used, text)
    used, text = full_pipeline_text()
    write("full-pipeline-unswitch.txt", used, text)
    used, text = ir_shape_text()
    write("ir-shape-across-compilers.txt", used, text)
    used, text = metadata_text()
    write("ir-metadata-removed.txt", used, text)
    used, text = versions_text()
    write("trunk-versions.txt", used, text)


if __name__ == "__main__":
    main()
