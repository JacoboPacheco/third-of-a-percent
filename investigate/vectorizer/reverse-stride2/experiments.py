"""Every Compiler Explorer request of this folder, as data. `python fetch.py` sends the ones not yet in raw/.

An experiment is (name, compiler id, source, flags, compiler options). The name is the file raw/<name>.json
(or .json.gz for large answers). Groups:

  A  clang's loop-vectorize remarks, five clang versions, checks off (NONE) and on (FAST)
  B  the IR just before the loop vectorizer (-mllvm -print-before=loop-vectorize)
  C  the optimization pipeline viewer: IR before and after every pass, per function
  D  clang 18.1.0 and 20.1.0 builds with assertions: the vectorizer's own debug output
  E  ScalarEvolution's printed trip counts (opt -passes=print<scalar-evolution>), run on the IR of group B
  F  `opt` running the loop vectorizer alone, or loop unswitching and then the loop vectorizer, on the IR of group B
  G  the full -O2 pipeline of `opt` 18.1.0 on the front end's IR, unchanged and with one unswitching pass inserted
  H  hand-written IR (sources/handwritten/s2-bound.ll): ScalarEvolution and the loop vectorizer on a stride-2 loop
     whose bound has a different range in each function
  V  the version line of the trunk compiler and of trunk `opt` at the time of the later requests

Flag groups:
  BASE     -O2 -std=c++20 -march=x86-64 -stdlib=libc++ (x86-64 baseline: SSE2; the main study's setting)
  NONE/FAST  the libc++ hardening mode macro
  REMARKS  clang's loop-vectorize optimization remarks (passed, missed, analysis)
  G0       -g0 after Compiler Explorer's own -g, so that IR dumps carry no llvm.dbg.value lines
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "-O2 -std=c++20 -march=x86-64 -stdlib=libc++"
MODE = {"none": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE",
        "fast": "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"}
REMARKS = "-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize"
G0 = "-g0"
PRINT_BEFORE_LV = "-mllvm -print-before=loop-vectorize"

# Compiler Explorer ids (from raw/compilers-cpp-ids.json). The libc++ used is the one Compiler Explorer
# ships for that compiler; it was not checked beyond the hardening macro taking effect.
CLANGS = [("c18", "clang1810", "18.1.0"), ("c19", "clang1910", "19.1.0"), ("c20", "clang2010", "20.1.0"),
          ("c21", "clang2110", "21.1.0"), ("ctrunk", "clang_trunk", "trunk")]
CLANG_ID = {short: cid for short, cid, _ in CLANGS}
OPT_ID = {"c18": "opt1810", "c19": "opt1910", "c20": "opt2010", "ctrunk": "opttrunk"}
SOURCES = {"kernels": "sources/kernels.cpp", "variants": "sources/variants.cpp", "variants2": "sources/variants2.cpp",
           "variants3": "sources/variants3.cpp"}
# No Compiler Explorer filter at all: the answer is the compiler's text output as it is (used where the answer is IR).
NOFILT = {"binary": False, "binaryObject": False, "commentOnly": False, "demangle": False, "directives": False,
          "execute": False, "intel": False, "labels": False, "libraryCode": False, "trim": False,
          "debugCalls": False}
FRONTEND_IR = "sources/ir/c18-kernels-fast-frontend.ll"
S2_BOUND = "sources/handwritten/s2-bound.ll"
REMARKS_OPT = "-pass-remarks=loop-vectorize -pass-remarks-missed=loop-vectorize -pass-remarks-analysis=loop-vectorize"
# The textual -O2 pipeline of opt 18.1.0 (answer G-opt1810-print-O2-pipeline) has these two groups once each.
INDVARS_GROUP = "loop(loop-idiom,indvars,loop-deletion,loop-unroll-full)"
UNSWITCH = "loop-mssa(simple-loop-unswitch<no-nontrivial;trivial>)"
LV_PASS = "loop-vectorize<no-interleave-forced-only;no-vectorize-forced-only;>"


# The two listings (GET requests) that give the compiler ids used below: name of the raw file, API path.
LISTINGS = [("compilers-cpp-ids", "/compilers/c++?fields=id,name,semver,instructionSet,compilerType"),
            ("compilers-llvm-ids", "/compilers/llvm?fields=id,name,semver,compilerType")]


def exp(name, compiler, source, flags, options=None, lang="c++", filters=None):
    path = SOURCES.get(source, source)
    return {"name": name, "compiler_id": compiler, "source_path": path, "args": flags,
            "compiler_options": options or {}, "lang": lang, "filters": filters}


def o2_pipeline():
    """The textual -O2 pipeline of opt 18.1.0, from the saved answer G-opt1810-print-O2-pipeline (None before it exists)."""
    import ce
    rec = ce._load("G-opt1810-print-O2-pipeline")
    return None if rec is None else ce.stdout_text(rec).strip()


def full_pipelines():
    """{name: pipeline text}: the -O2 pipeline unchanged, with the unswitching pass after the indvars group,
    and with it just before the loop vectorizer."""
    pipe = o2_pipeline()
    if pipe is None:
        return {}
    assert pipe.count(INDVARS_GROUP) == 1 and pipe.count(LV_PASS) == 1
    return {"control": pipe,
            "unswitch-after-indvars": pipe.replace(INDVARS_GROUP, INDVARS_GROUP + "," + UNSWITCH),
            "unswitch-before-lv": pipe.replace(LV_PASS, UNSWITCH + "," + LV_PASS)}


def all_experiments():
    out = []
    # A. Remarks, Compiler Explorer's default flags (-g), five clang versions.
    for short, cid, _ in CLANGS:
        for mode in ("none", "fast"):
            out.append(exp("A-%s-kernels-%s" % (short, mode), cid, "kernels",
                           "%s %s %s" % (BASE, MODE[mode], REMARKS)))
        out.append(exp("A-%s-variants-fast" % short, cid, "variants",
                       "%s %s %s" % (BASE, MODE["fast"], REMARKS)))
    out.append(exp("A-c18-variants-none", "clang1810", "variants", "%s %s %s" % (BASE, MODE["none"], REMARKS)))
    for short in ("c18", "c20", "ctrunk"):
        out.append(exp("A-%s-variants2-fast" % short, CLANG_ID[short], "variants2",
                       "%s %s %s" % (BASE, MODE["fast"], REMARKS)))
    out.append(exp("A-c18-variants3-fast", "clang1810", "variants3", "%s %s %s" % (BASE, MODE["fast"], REMARKS)))
    # B. IR just before the loop vectorizer.
    for short in ("c18", "c20"):
        for mode in ("none", "fast"):
            out.append(exp("B-%s-kernels-%s-ir" % (short, mode), CLANG_ID[short], "kernels",
                           "%s %s %s %s %s" % (BASE, MODE[mode], REMARKS, G0, PRINT_BEFORE_LV)))
        out.append(exp("B-%s-variants-fast-ir" % short, CLANG_ID[short], "variants",
                       "%s %s %s %s %s" % (BASE, MODE["fast"], REMARKS, G0, PRINT_BEFORE_LV)))
    out.append(exp("B-c19-kernels-fast-ir", "clang1910", "kernels",
                   "%s %s %s %s %s" % (BASE, MODE["fast"], REMARKS, G0, PRINT_BEFORE_LV)))
    out.append(exp("B-c18-variants2-fast-ir", "clang1810", "variants2",
                   "%s %s %s %s %s" % (BASE, MODE["fast"], REMARKS, G0, PRINT_BEFORE_LV)))
    out.append(exp("B-c18-variants3-fast-ir", "clang1810", "variants3",
                   "%s %s %s %s %s" % (BASE, MODE["fast"], REMARKS, G0, PRINT_BEFORE_LV)))
    for src in ("kernels", "variants"):
        out.append(exp("B-ctrunk-%s-fast-ir" % src, "clang_trunk", src,
                       "%s %s %s %s %s" % (BASE, MODE["fast"], REMARKS, G0, PRINT_BEFORE_LV)))
    # C. The pass-by-pass pipeline (IR before and after each pass, per function). Large answers, stored gzipped.
    pipe = {"produceOptPipeline": True}
    out.append(exp("C-c18-kernels-fast-pipeline", "clang1810", "kernels",
                   "%s %s %s %s" % (BASE, MODE["fast"], REMARKS, G0), pipe))
    out.append(exp("C-c18-variants-fast-pipeline", "clang1810", "variants",
                   "%s %s %s %s" % (BASE, MODE["fast"], REMARKS, G0), pipe))
    out.append(exp("C-c20-kernels-fast-pipeline", "clang2010", "kernels",
                   "%s %s %s %s" % (BASE, MODE["fast"], REMARKS, G0), pipe))
    # D. Assertion builds: the vectorizer's and IndVarSimplify's own debug output.
    for tag, dbg in (("lv", "loop-vectorize"), ("indvars", "indvars"), ("scev", "scalar-evolution"),
                     ("laa", "loop-accesses")):
        out.append(exp("D-c18assert-kernels-fast-%s" % tag, "clang181assert", "kernels",
                       "%s %s %s %s -mllvm -debug-only=%s" % (BASE, MODE["fast"], REMARKS, G0, dbg)))
    # both debug streams in one run, so that the order of the loop vectorizer's and the loop-access analysis's lines shows
    out.append(exp("D-c18assert-kernels-fast-lv-laa", "clang181assert", "kernels",
                   "%s %s %s %s -mllvm -debug-only=loop-vectorize,loop-accesses" % (BASE, MODE["fast"], REMARKS, G0)))
    for tag, dbg in (("lv", "loop-vectorize"), ("indvars", "indvars"), ("laa", "loop-accesses")):
        out.append(exp("D-c18assert-variants-fast-%s" % tag, "clang181assert", "variants",
                       "%s %s %s %s -mllvm -debug-only=%s" % (BASE, MODE["fast"], REMARKS, G0, dbg)))
    for tag, dbg in (("lv", "loop-vectorize"), ("laa", "loop-accesses")):
        out.append(exp("D-c20assert-kernels-fast-%s" % tag, "clang201assert", "kernels",
                       "%s %s %s %s -mllvm -debug-only=%s" % (BASE, MODE["fast"], REMARKS, G0, dbg)))
    # E. ScalarEvolution on the IR of group B (the .ll files are written by `python extract.py ir`).
    for short, src, mode in (("c18", "kernels", "fast"), ("c18", "kernels", "none"), ("c18", "variants", "fast"),
                             ("c18", "variants2", "fast"), ("c18", "variants3", "fast"), ("c19", "kernels", "fast"),
                             ("c20", "kernels", "fast"), ("c20", "variants", "fast"), ("ctrunk", "kernels", "fast")):
        ll = "sources/ir/%s-%s-%s.ll" % (short, src, mode)
        if os.path.exists(os.path.join(HERE, ll)):
            out.append(exp("E-%s-%s-%s-scev" % (short, src, mode), OPT_ID[short], ll,
                           "-passes=print<scalar-evolution> -disable-output", lang="llvm"))
    # F. The loop vectorizer alone, and with loop unswitching run just before it, on the IR of group B (opt 18.1.0).
    ll = "sources/ir/c18-kernels-fast.ll"
    rem = "-pass-remarks=loop-vectorize -pass-remarks-missed=loop-vectorize -pass-remarks-analysis=loop-vectorize"
    if os.path.exists(os.path.join(HERE, ll)):
        out.append(exp("F-c18-kernels-fast-lv-only", "opt1810", ll,
                       "-passes=loop-vectorize %s -S" % rem, lang="llvm"))
        out.append(exp("F-c18-kernels-fast-unswitch-then-lv", "opt1810", ll,
                       "-passes=loop-mssa(simple-loop-unswitch),loop-vectorize %s -S" % rem, lang="llvm"))
    ll = "sources/ir/ctrunk-kernels-fast.ll"
    if os.path.exists(os.path.join(HERE, ll)):
        out.append(exp("F-ctrunk-kernels-fast-lv-only", "opttrunk", ll,
                       "-passes=loop-vectorize %s -S" % rem, lang="llvm"))
        out.append(exp("F-ctrunk-kernels-fast-unswitch-then-lv", "opttrunk", ll,
                       "-passes=loop-mssa(simple-loop-unswitch),loop-vectorize %s -S" % rem, lang="llvm"))
    ll = "sources/ir/c20-kernels-fast.ll"
    if os.path.exists(os.path.join(HERE, ll)):
        out.append(exp("F-c20-kernels-fast-lv-only", "opt2010", ll,
                       "-passes=loop-vectorize %s -S" % rem, lang="llvm"))
        out.append(exp("F-c20-kernels-fast-unswitch-then-lv", "opt2010", ll,
                       "-passes=loop-mssa(simple-loop-unswitch),loop-vectorize %s -S" % rem, lang="llvm"))
    # G. The full -O2 pipeline of opt 18.1.0 on the front end's IR (clang 18.1.0 with -disable-llvm-passes).
    out.append(exp("G-c18-kernels-fast-frontend-ir", "clang1810", "kernels",
                   "%s %s %s -Xclang -disable-llvm-passes -S -emit-llvm" % (BASE, MODE["fast"], G0), filters=NOFILT))
    if os.path.exists(os.path.join(HERE, FRONTEND_IR)):
        out.append(exp("G-opt1810-print-O2-pipeline", "opt1810", FRONTEND_IR,
                       "-passes=default<O2> -print-pipeline-passes -disable-output", lang="llvm", filters=NOFILT))
        for tag, pipe in full_pipelines().items():
            out.append(exp("G-opt1810-full-O2-%s" % tag, "opt1810", FRONTEND_IR,
                           "-passes=%s %s -S" % (pipe, REMARKS_OPT), lang="llvm", filters=NOFILT))
    # H. Hand-written IR: one stride-2 loop with one check, only the bound's range and the shift's flags differ.
    for oid in ("opt1810", "opt2010", "opttrunk"):
        out.append(exp("H-%s-s2-bound-scev" % oid, oid, S2_BOUND,
                       "-passes=print<scalar-evolution> -disable-output", lang="llvm"))
    out.append(exp("H-opt1810-s2-bound-lv", "opt1810", S2_BOUND,
                   "-passes=loop-vectorize %s -S" % REMARKS_OPT, lang="llvm"))
    # V. The version line of trunk, which is rebuilt every day: recorded at the time of the later requests.
    out.append(exp("V-ctrunk-version", "clang_trunk", "kernels", "--version"))
    out.append(exp("V-opttrunk-version", "opttrunk", S2_BOUND, "--version", lang="llvm"))
    return out
