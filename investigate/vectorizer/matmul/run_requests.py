"""Sends every request listed in MANIFEST that is not saved yet, and saves the raw answers to raw/.

    python run_requests.py                 # all groups (only what is missing is sent)
    python run_requests.py --group base    # one group
    python run_requests.py --dry-run       # print the requests, send nothing

Each entry: name -> (compiler id, source file, user arguments, opt pipeline?).
"""
import argparse
import sys

import ce

R = "-Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize"
NONE = "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE"
FAST = "-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST"
BASE = "-O2 -march=x86-64 -stdlib=libc++"
K08 = "src/k08_matmul.cpp"

MANIFEST = {}


def add(group, name, cid, src, args, pipe=False, filters=None):
    MANIFEST[name] = (group, cid, src, args, pipe, filters)


# base: the remarks of the study's own sweep, repeated on the single kernel
for cid, tag in [("clang1810", "c18"), ("clang1910", "c19")]:
    add("base", "base_%s_none" % tag, cid, K08, "%s %s %s" % (BASE, NONE, R))
    add("base", "base_%s_fast" % tag, cid, K08, "%s %s %s" % (BASE, FAST, R))

# pipe: the optimizer pipeline (IR before and after every pass) of the same builds
for cid, tag in [("clang1810", "c18"), ("clang1910", "c19")]:
    for mode, flag in (("none", NONE), ("fast", FAST)):
        add("pipe", "pipe_%s_%s" % (tag, mode), cid, K08, "%s %s %s" % (BASE, flag, R), True)

# dbg: -mllvm -debug-only=loop-vectorize on the assertions builds (a different compiler binary than the base builds)
DBG = "-mllvm -debug-only=loop-vectorize"
for cid, tag in [("clang181assert", "a18"), ("clang191assert", "a19")]:
    for mode, flag in (("fast", FAST), ("none", NONE)):
        add("dbg", "dbg_%s_%s" % (tag, mode), cid, K08, "%s %s %s %s" % (BASE, flag, R, DBG))

# paths: where each compiler finds its libc++ headers (-v prints the include search list)
for cid, tag in [("clang1810", "c18"), ("clang1910", "c19")]:
    add("paths", "paths_%s" % tag, cid, K08, "%s %s -v" % (BASE, FAST))

# dbgall: the same debug output on the other assertions builds, FAST only
ASSERT = [("clang160assert", "a16", "-D_LIBCPP_ENABLE_ASSERTIONS=1"), ("clang170assert", "a17", "-D_LIBCPP_ENABLE_HARDENED_MODE=1"),
          ("clang201assert", "a20", FAST), ("clang211assert", "a21", FAST), ("clang221assert", "a22", FAST),
          ("clang231assert", "a23", FAST), ("clang_assertions_trunk", "atrunk", FAST)]
for cid, tag, flag in ASSERT:
    add("dbgall", "dbg_%s_fast" % tag, cid, K08, "%s %s %s %s" % (BASE, flag, R, DBG))

# libswap: hold the library fixed, change the compiler (and the reverse). -H lists the headers actually read.
L18 = ("-nostdinc++ -isystem /opt/compiler-explorer/clang-18.1.0/include/x86_64-unknown-linux-gnu/c++/v1 "
       "-isystem /opt/compiler-explorer/clang-18.1.0/include/c++/v1")


def lib(ver):
    root = "/opt/compiler-explorer/clang-%s" % ver
    return "-nostdinc++ -isystem %s/include/x86_64-unknown-linux-gnu/c++/v1 -isystem %s/include/c++/v1" % (root, root)


for cid, tag in [("clang1810", "c18"), ("clang1910", "c19"), ("clang2010", "c20"), ("clang2110", "c21"),
                 ("clang2210", "c22"), ("clang2310", "c231"), ("clang_trunk", "ctrunk")]:
    add("libswap", "libswap_%s_lib18" % tag, cid, K08, "%s %s %s %s -H" % (BASE, lib("18.1.0"), FAST, R))
for ver, tag in [("19.1.0", "lib19"), ("21.1.0", "lib21")]:
    add("libswap", "libswap_c18_%s" % tag, "clang1810", K08, "%s %s %s %s -H" % (BASE, lib(ver), FAST, R))

# emul: the same loop with no library header (src/emul_matmul.cpp), checks set by -D
EM = "src/emul_matmul.cpp"
E_BASE = "-O2 -march=x86-64"
ALLC = [("clang1600", "c16"), ("clang1701", "c17"), ("clang1810", "c18"), ("clang1910", "c19"), ("clang2010", "c20"),
        ("clang2110", "c21"), ("clang2210", "c22"), ("clang2310", "c231"), ("clang_trunk", "ctrunk")]
for cid, tag in ALLC:
    add("emul", "emul_%s_abc" % tag, cid, EM, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s" % (E_BASE, R))
for cid, tag in [("clang1810", "c18"), ("clang1910", "c19"), ("clang2310", "c231")]:
    add("emul", "emul_%s_none" % tag, cid, EM, "%s -DCHK_A=0 -DCHK_B=0 -DCHK_C=0 %s" % (E_BASE, R))
# emul1: only one of the two inner-loop checks (and the middle-loop check on a[])
for cid, tag in [("clang1810", "c18"), ("clang1910", "c19")]:
    add("emul1", "emul_%s_aB" % tag, cid, EM, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=0 %s" % (E_BASE, R))
    add("emul1", "emul_%s_aC" % tag, cid, EM, "%s -DCHK_A=1 -DCHK_B=0 -DCHK_C=1 %s" % (E_BASE, R))
add("emul1", "dbg_emul_a18_abc", "clang181assert", EM, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s %s" % (E_BASE, R, DBG))
add("emul1", "dbg_emul_a18_aB", "clang181assert", EM, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=0 %s %s" % (E_BASE, R, DBG))
add("emul1", "pipe_emul_c18_abc", "clang1810", EM, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s" % (E_BASE, R), True)

# march: the same debug output at other x86-64 levels (SSE4.2 has a 64-bit vector compare, SSE2 does not)
for lvl in ("v2", "v3"):
    add("march", "dbg_a18_fast_%s" % lvl, "clang181assert", K08,
        "-O2 -march=x86-64-%s -stdlib=libc++ %s %s %s" % (lvl, FAST, R, DBG))
    add("march", "dbg_a19_fast_%s" % lvl, "clang191assert", K08,
        "-O2 -march=x86-64-%s -stdlib=libc++ %s %s %s" % (lvl, FAST, R, DBG))
# force: clang 18 told to vectorize anyway (width 4, interleave 2: what clang 19 picks by itself)
add("force", "force_c18_fast", "clang1810", K08, "%s %s %s -mllvm -force-vector-width=4 -mllvm -force-vector-interleave=2" % (BASE, FAST, R))
# pipe23: the optimizer pipeline of the compilers that lose it again
add("pipe23", "pipe_c231_fast", "clang2310", K08, "%s %s %s" % (BASE, FAST, R), True)

# hoist: the pointer loads of b and c moved out of the inner loop in the source
EH = "src/emul_hoist.cpp"
for cid, tag in [("clang1810", "c18"), ("clang1910", "c19"), ("clang2310", "c231"), ("clang_trunk", "ctrunk")]:
    add("hoist", "hoist_%s_bc" % tag, cid, EH, "%s -DCHK_B=1 -DCHK_C=1 %s" % (E_BASE, R))
# licm: what LICM hoisted (assertions builds)
for cid, tag in [("clang191assert", "a19"), ("clang231assert", "a23")]:
    add("licm", "licm_%s_fast" % tag, cid, K08, "%s %s %s -mllvm -debug-only=licm" % (BASE, FAST, R))

# restrict: the same emulation with `c` declared __restrict (does the compiler then hoist c's size loads?)
ER = "src/emul_restrict.cpp"
for cid, tag in [("clang1810", "c18"), ("clang2310", "c231"), ("clang_trunk", "ctrunk")]:
    add("restrict", "restrict_%s_abc" % tag, cid, ER, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s" % (E_BASE, R))
# emit: the optimized LLVM IR (with the default display filters the module metadata is hidden)
for cid, tag in [("clang1910", "c19"), ("clang2310", "c231")]:
    add("emit", "emit_%s_fast" % tag, cid, K08, "%s %s -emit-llvm" % (BASE, FAST))
# emitfull: the same with display filters off, to read the module metadata (the TBAA tags)
FULL = dict(ce.FILTERS, directives=False, commentOnly=False, labels=False, libraryCode=False)
for cid, tag in [("clang1910", "c19"), ("clang2310", "c231")]:
    add("emitfull", "emitfull_%s_fast" % tag, cid, K08, "%s %s -emit-llvm" % (BASE, FAST), False, FULL)

add("emitfull", "emitfull_c22_fast", "clang2210", K08, "%s %s -emit-llvm" % (BASE, FAST), False, FULL)
# ptbaa: pointer-type TBAA switched off in clang 23.1 (and on explicitly in clang 22)
add("ptbaa", "ptbaa_c231_off", "clang2310", K08, "%s %s %s -fno-pointer-tbaa" % (BASE, FAST, R))
add("ptbaa", "ptbaa_c22_off", "clang2210", K08, "%s %s %s -fno-pointer-tbaa" % (BASE, FAST, R))

# emul32: 32-bit indices and sizes in the check (a cheaper vector compare on SSE2)
E32 = "src/emul32_matmul.cpp"
for cid, tag in [("clang1810", "c18"), ("clang1910", "c19")]:
    add("emul32", "emul32_%s_abc" % tag, cid, E32, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s" % (E_BASE, R))
add("emul32", "dbg_emul32_a18_abc", "clang181assert", E32, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s %s" % (E_BASE, R, DBG))

# pipe22: the optimizer pipeline of clang 22.1.0 (its debug output shows a loop without the checks)
add("pipe22", "pipe_c22_fast", "clang2210", K08, "%s %s %s" % (BASE, FAST, R), True)


# pipemid: the optimizer pipeline of clang 20.1.0 and 21.1.0 (to see which pass first makes the clamp there)
for cid, tag in [("clang2010", "c20"), ("clang2110", "c21")]:
    add("pipemid", "pipe_%s_fast" % tag, cid, K08, "%s %s %s" % (BASE, FAST, R), True)

# nopred: clang 22.1.0 with the hidden option that commit 39b0cbe69c adds switched off
NOPRED = "-mllvm -indvars-predicate-loop-traps=false"
add("nopred", "dbg_a22_nopred", "clang221assert", K08, "%s %s %s %s %s" % (BASE, FAST, R, DBG, NOPRED))
add("nopred", "pipe_c22_nopred", "clang2210", K08, "%s %s %s %s" % (BASE, FAST, R, NOPRED), True)

# pipeemul23: the optimizer pipeline of the two library-free counterfactuals on clang 23.1
add("pipeemul23", "pipe_hoist_c231", "clang2310", EH, "%s -DCHK_B=1 -DCHK_C=1 %s" % (E_BASE, R), True)
add("pipeemul23", "pipe_restrict_c231", "clang2310", ER, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s" % (E_BASE, R), True)

# trunk: the trunk builds again, with -v so that the build revision is recorded in the answer
add("trunk", "pipe_ctrunk_fast", "clang_trunk", K08, "%s %s %s -v" % (BASE, FAST, R), True)
add("trunk", "rev_atrunk_fast", "clang_assertions_trunk", K08, "%s %s %s %s -v" % (BASE, FAST, R, DBG))
add("trunk", "licm_atrunk_fast", "clang_assertions_trunk", K08, "%s %s %s -mllvm -debug-only=licm -v" % (BASE, FAST, R))
# the four older clang_trunk answers again, with -v: do they reproduce, and at which revision?
add("trunk", "libswap_ctrunk_lib18_v", "clang_trunk", K08, "%s %s %s %s -H -v" % (BASE, lib("18.1.0"), FAST, R))
add("trunk", "emul_ctrunk_abc_v", "clang_trunk", EM, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s -v" % (E_BASE, R))
add("trunk", "hoist_ctrunk_bc_v", "clang_trunk", EH, "%s -DCHK_B=1 -DCHK_C=1 %s -v" % (E_BASE, R))
add("trunk", "restrict_ctrunk_abc_v", "clang_trunk", ER, "%s -DCHK_A=1 -DCHK_B=1 -DCHK_C=1 %s -v" % (E_BASE, R))

# paths2: the revision of the two assertions builds (-v prints the clang version line)
for cid, tag in [("clang181assert", "a18"), ("clang191assert", "a19")]:
    add("paths2", "paths_%s" % tag, cid, K08, "%s %s -v" % (BASE, FAST))

# g0: the same debug output with -g0 appended (Compiler Explorer adds -g before the user's arguments)
for cid, tag in [("clang181assert", "a18"), ("clang191assert", "a19")]:
    add("g0", "dbg_%s_fast_g0" % tag, cid, K08, "%s %s %s %s -g0" % (BASE, FAST, R, DBG))


# fastmacro: the FAST macro on the compilers whose libc++ has no hardening modes (does it add a check?)
for cid, tag in [("clang1600", "c16"), ("clang1701", "c17")]:
    add("fastmacro", "fastmacro_%s" % tag, cid, K08, "%s %s %s" % (BASE, FAST, R))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    n = 0
    for name, (group, cid, src, args, pipe, filters) in MANIFEST.items():
        if a.group and group != a.group:
            continue
        have = ce.load(name) is not None
        print("%-4s %-34s %-22s %s" % ("have" if have else "SEND", name, cid, args))
        if a.dry_run or have:
            continue
        rec = ce.compile_(name, cid, src, args, pipe, filters)
        r = rec["response"]
        print("      code=%s asm=%d stderr_lines=%d" % (r.get("code"), len(r.get("asm") or []), len(r.get("stderr") or [])))
        n += 1
    print("sent %d; total requests used %d" % (n, ce.requests_used()))


if __name__ == "__main__":
    sys.exit(main())
