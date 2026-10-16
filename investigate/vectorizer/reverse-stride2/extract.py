"""Turns the saved raw/ answers into readable text files. Offline: no request is sent.

    python extract.py ir         # sources/ir/*.ll: the IR dumps of group B as modules `opt` can read (input of group E),
                                 # and the front end's IR of group G (input of the full-pipeline runs)
    python extract.py excerpts   # extracted/*.txt: remarks, IR before the loop vectorizer, pass-by-pass excerpts, ScalarEvolution output
    python extract.py all
"""
import gzip
import json
import os
import re
import sys

import ce

HERE = ce.HERE
IR_DIR = os.path.join(HERE, "sources", "ir")
OUT_DIR = os.path.join(HERE, "extracted")
NL = chr(10)

# ---------------------------------------------------------------- IR dumps (-print-before=loop-vectorize)
DUMP = re.compile(r"(?m)^(?=; \*\*\* IR Dump)")
KNOWN_DECLS = {
    "llvm.trap": "declare void @llvm.trap() #9999",
    "llvm.umax.i64": "declare i64 @llvm.umax.i64(i64, i64)",
    "llvm.umin.i64": "declare i64 @llvm.umin.i64(i64, i64)",
    "llvm.assume": "declare void @llvm.assume(i1 noundef)",
}


def ir_dumps(name):
    """{function symbol: text of its dump} from the compiler's stderr of raw/<name>."""
    text = ce.stderr_text(ce.load(name))
    out = {}
    for part in DUMP.split(text):
        if not part.startswith("; *** IR Dump"):
            continue
        m = re.match(r"; \*\*\* IR Dump Before LoopVectorizePass on (\S+) \*\*\*", part)
        body = part.split(NL + "<source>")[0].rstrip() + NL
        out[m.group(1)] = body
    return out


def sanitize(body):
    """Drops debug and TBAA metadata, which a standalone module has no definitions for, and gives the unnamed
    basic blocks readable names (entry, bbN, with N the number the dump printed), so that ScalarEvolution's
    output can say which exit is which. Keeps the function attributes (mustprogress matters to ScalarEvolution)
    and every instruction flag."""
    lines = body.splitlines()
    attrs = None
    define = [ln for ln in lines if ln.startswith("define")][0]
    entry = len(set(re.findall(r"%\d+", define)))  # unnamed parameters are %0..%(n-1); the entry block is next
    labels = set()
    for ln in lines:
        m = re.match(r"^(\d+):", ln)
        if m:
            labels.add(int(m.group(1)))

    def rename(mm):
        n = int(mm.group(1))
        if n in labels:
            return "%bb" + str(n)
        if n == entry:
            return "%entry"
        return mm.group(0)

    out = []
    for ln in lines:
        m = re.match(r"; Function Attrs: (.*)$", ln)
        if m:
            attrs = m.group(1)
        ln = re.sub(r", !(?:dbg|tbaa|prof|llvm\.loop|srcloc|noundef|nonnull|range|align) !\d+", "", ln)
        ln = re.sub(r" !dbg !\d+", "", ln)
        if not ln.startswith(";") and not ln.startswith("define"):
            ln = re.sub(r"%(\d+)(?!\d)", rename, ln)
            ln = re.sub(r"^(\d+):", lambda mm: "bb%s:" % mm.group(1), ln)
            if ln.startswith("  "):
                ln = re.sub(r" #\d+(?= |,|$)", "", ln)  # call-site attribute groups
        out.append(ln)
        if ln.startswith("define"):
            out.append("entry:")
    return NL.join(out) + NL, attrs


def build_module(name):
    dumps = ir_dumps(name)
    funcs, calls = [], set()
    for sym, body in dumps.items():
        text, attrs = sanitize(body)
        # keep the attribute group: re-attach #N from the original define line
        orig = [ln for ln in body.splitlines() if ln.startswith("define")][0]
        gm = re.search(r"\s#(\d+)\s", orig)
        if gm:
            text = re.sub(r"(?m)^(define [^\n]*?\))\s*(local_unnamed_addr)?\s*\{$",
                          lambda mm: "%s %s #%s {" % (mm.group(1), mm.group(2) or "", gm.group(1)), text, count=1)
            funcs.append((int(gm.group(1)), attrs, text))
        else:
            funcs.append((None, attrs, text))
        calls |= set(re.findall(r"@(llvm\.[\w.]+)\(", text))
    head = ["; Standalone module made from the IR dumps in raw/%s.json (see extract.py)." % name,
            "target datalayout = \"e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128\"",
            "target triple = \"x86_64-unknown-linux-gnu\"", "",
            "%\"class.std::__1::vector\" = type { ptr, ptr, ptr }", ""]
    for c in sorted(calls):
        if c not in KNOWN_DECLS:
            raise SystemExit("no declaration known for " + c)
        head.append(KNOWN_DECLS[c])
    if any("@__gxx_personality_v0" in t for _, _, t in funcs):
        head.append("declare i32 @__gxx_personality_v0(...)")
    seen = {}
    for g, attrs, _ in funcs:
        if g is not None:
            seen[g] = attrs
    body = (NL + NL).join(t for _, _, t in funcs)
    tail = NL.join("attributes #%d = { %s }" % (g, a) for g, a in sorted(seen.items()))
    if "llvm.trap" in calls:
        tail += NL + "attributes #9999 = { cold noreturn nounwind memory(inaccessiblemem: write) }"
    return NL.join(head) + NL + NL + body + NL + tail + NL


def write_ir():
    os.makedirs(IR_DIR, exist_ok=True)
    for raw, out in (("B-c18-kernels-fast-ir", "c18-kernels-fast"), ("B-c18-kernels-none-ir", "c18-kernels-none"),
                     ("B-c18-variants-fast-ir", "c18-variants-fast"), ("B-c18-variants2-fast-ir", "c18-variants2-fast"),
                     ("B-c18-variants3-fast-ir", "c18-variants3-fast"),
                     ("B-c19-kernels-fast-ir", "c19-kernels-fast"), ("B-c20-kernels-fast-ir", "c20-kernels-fast"), ("B-ctrunk-kernels-fast-ir", "ctrunk-kernels-fast"),
                     ("B-c20-variants-fast-ir", "c20-variants-fast")):
        text = build_module(raw)
        with open(os.path.join(IR_DIR, out + ".ll"), "w", encoding="utf-8", newline=NL) as f:
            f.write(text)
        print("wrote sources/ir/%s.ll (%d lines)" % (out, text.count(NL)))
    write_frontend()


def frontend_text(name="G-c18-kernels-fast-frontend-ir"):
    """The IR text clang 18.1.0 printed with -disable-llvm-passes (the answer's `asm` lines, as they are)."""
    return NL.join(x.get("text", "") for x in (ce.load(name)["response"].get("asm") or [])) + NL


def write_frontend():
    path = os.path.join(IR_DIR, "c18-kernels-fast-frontend.ll")
    text = frontend_text()
    with open(path, "w", encoding="utf-8", newline=NL) as f:
        f.write(text)
    print("wrote sources/ir/c18-kernels-fast-frontend.ll (%d lines)" % text.count(NL))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("ir", "all"):
        write_ir()
