"""Reads the few LLVM source passages this note quotes, from the public repository at fixed release tags.

Network: raw.githubusercontent.com (source files) and api.github.com (two commits, ten tag comparisons, two tag listings); no key.
The unauthenticated GitHub API allows 60 requests per hour per address; a full run uses 14 of them.
Writes llvm-src/. Run:  python fetch_llvm_src.py
"""
import hashlib
import http.client
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "llvm-src")
RAW = "https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-%s/llvm/lib/%s"
API = "https://api.github.com/repos/llvm/llvm-project"
UA = "third-of-a-percent-investigate/1.0 (research project)"
COMMIT = "b6a8f5486bc12b132ec984bc8767506e3bcb6694"
COMMIT2 = "39b0cbe69ca8704dbc5846a91d136f0ed6101782"  # [IndVarSimplify] Allow predicateLoopExit on some loops with thread-local writes


COUNT = {"files": 0, "api": 0}


def get(url, accept=None, tries=4):
    COUNT["api" if url.startswith(API) else "files"] += 1
    for attempt in range(tries):
        time.sleep(1.0 + 3 * attempt)
        req = urllib.request.Request(url, headers={"User-Agent": UA, **({"Accept": accept} if accept else {})})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8")
        except (OSError, http.client.HTTPException):  # a dropped connection is retried
            if attempt == tries - 1:
                raise


def function_text(src, header):
    lines = src.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(header))
    end = next(i for i in range(start, len(lines)) if lines[i] == "}")
    return start + 1, "\n".join(lines[start:end + 1]) + "\n"


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    os.makedirs(OUT, exist_ok=True)
    hashes = []
    # 1. collectLoopUniforms at the four tags (the compiler versions on Compiler Explorer and the ones timed)
    for tag in ("18.1.0", "18.1.3", "19.1.0", "19.1.7"):
        url = RAW % (tag, "Transforms/Vectorize/LoopVectorize.cpp")
        src = get(url)
        first, body = function_text(src, "void LoopVectorizationCostModel::collectLoopUniforms")
        blines = body.splitlines()
        k = next(i for i, ln in enumerate(blines) if "Start with the conditional branch" in ln)
        lo, hi = max(0, k - 2), min(len(blines), k + 14)
        sha = hashlib.sha256(body.encode()).hexdigest()
        head = ("// LLVM is licensed under Apache-2.0 with LLVM exceptions. Short excerpt, for reference.\n"
                "// Source: %s\n"
                "// Function LoopVectorizationCostModel::collectLoopUniforms: lines %d to %d at tag llvmorg-%s\n"
                "// (sha256 of the whole function: %s). Excerpt: lines %d to %d.\n\n" % (
                    url, first, first + len(blines) - 1, tag, sha, first + lo, first + hi - 1))
        write("collectLoopUniforms_%s.cpp.txt" % tag, head + "\n".join(blines[lo:hi]) + "\n")
        # where an instruction that is uniform after vectorization is priced as a scalar
        slines = src.splitlines()
        j = next(i for i, ln in enumerate(slines) if "If we know that this instruction will remain uniform, check the cost of" in ln)
        write("getInstructionCost_uniform_%s.cpp.txt" % tag,
              "// LLVM is licensed under Apache-2.0 with LLVM exceptions. Short excerpt, for reference.\n"
              "// Source: %s (tag llvmorg-%s), lines %d to %d\n\n" % (url, tag, j - 2, j + 6) + "\n".join(slines[j - 3:j + 6]) + "\n")
        hashes.append((tag, sha))
        print(tag, "collectLoopUniforms: %d lines, sha256 %s" % (len(blines), sha[:16]))
    # the same function at the exact commits the Compiler Explorer builds report with `-v` (raw/paths_*.json)
    for label, rev in (("commit-461274b81d86", "461274b81d8641eab64d494accddc81d7db8a09e"),
                       ("commit-a4bf6cd7cfb1", "a4bf6cd7cfb1a1421ba92bca9d017b49936c55e4")):
        url = "https://raw.githubusercontent.com/llvm/llvm-project/%s/llvm/lib/Transforms/Vectorize/LoopVectorize.cpp" % rev
        first, body = function_text(get(url), "void LoopVectorizationCostModel::collectLoopUniforms")
        hashes.append((label, hashlib.sha256(body.encode()).hexdigest()))
        print(label, "collectLoopUniforms: %d lines, sha256 %s" % (len(body.splitlines()), hashes[-1][1][:16]))
    write("collectLoopUniforms_sha256.txt", "".join("%s  %s\n" % (h, t) for t, h in hashes))
    d = dict(hashes)
    print("18.1.0 == 18.1.3:", d["18.1.0"] == d["18.1.3"], "| 19.1.0 == 19.1.7:", d["19.1.0"] == d["19.1.7"],
          "| 18 == 19:", d["18.1.0"] == d["19.1.0"])

    # 2. the legality check that sends a loop with a non-computable backedge-taken count down the early-exit path
    for tag in ("19.1.0", "20.1.0", "22.1.0", "23.1.0"):
        url = RAW % (tag, "Transforms/Vectorize/LoopVectorizationLegality.cpp")
        src = get(url)
        lines = src.splitlines()
        hits = [i for i, ln in enumerate(lines) if "isa<SCEVCouldNotCompute>(PSE.getBackedgeTakenCount())" in ln]
        msgs = [i for i, ln in enumerate(lines) if "Early exit loop with store but no supported condition load" in ln]
        out = ["// LLVM is licensed under Apache-2.0 with LLVM exceptions. Short excerpts, for reference.",
               "// Source: %s (tag llvmorg-%s)" % (url, tag), ""]
        for i in hits[:1]:
            out += ["// lines %d to %d" % (i - 1, i + 22)] + lines[max(0, i - 2):i + 22] + [""]
        for i in msgs[:1]:
            out += ["// lines %d to %d" % (i - 7, i + 3)] + lines[max(0, i - 8):i + 3] + [""]
        if not msgs:
            out += ["// the message 'Early exit loop with store but no supported condition load' does not occur in this file", ""]
        write("legality_%s.txt" % tag, "\n".join(out) + "\n")
        print(tag, "legality: backedge check at line", [h + 1 for h in hits[:1]], "message at", [m + 1 for m in msgs])

    # 3. the x86 cost-table entries for a 64-bit vector compare, by feature level (tag 18.1.0)
    url = RAW % ("18.1.0", "Target/X86/X86TargetTransformInfo.cpp")
    src = get(url)
    lines = src.splitlines()
    table, found = None, []
    for i, ln in enumerate(lines):
        m = re.search(r"CostKindTblEntry (\w+CostTbl)\[\]", ln)
        if m:
            table = m.group(1)
        if table and "ISD::SETCC" in ln and ("v2i64" in ln or "v4i64" in ln) and i > 3100:
            found.append("%-18s line %d: %s" % (table, i + 1, ln.strip()))
    write("x86_setcc_i64_18.1.0.txt", "// LLVM is licensed under Apache-2.0 with LLVM exceptions. Short excerpt, for reference.\n// Source: %s (tag llvmorg-18.1.0)\n// 64-bit vector compare (SETCC v2i64 / v4i64) entries, by cost table\n\n%s\n" % (url, "\n".join(found)))
    print("x86 SETCC entries:", len(found))
    # how a table entry becomes the logged cost: legalization factor times (extra cost of the predicate + table cost)
    start = next(i for i, ln in enumerate(lines) if "InstructionCost X86TTIImpl::getCmpSelInstrCost(" in ln)
    leg = next(i for i in range(start, len(lines)) if "getTypeLegalizationCost(ValTy)" in lines[i])
    ult = next(i for i in range(start, len(lines)) if "case CmpInst::Predicate::ICMP_ULT:" in lines[i])
    ult_end = next(i for i in range(ult, len(lines)) if lines[i].strip() == "break;")
    xs = ["// LLVM is licensed under Apache-2.0 with LLVM exceptions. Short excerpts, for reference.",
          "// Source: %s (tag llvmorg-18.1.0), function X86TTIImpl::getCmpSelInstrCost" % url, "",
          "// lines %d to %d: the legalization factor LT.first, the declaration of ExtraCost and the condition under which it is set" % (leg + 1, leg + 16)] + lines[leg:leg + 16] + [
          "", "// lines %d to %d: the extra cost of an unsigned compare of vectors" % (ult + 1, ult_end + 1)] + lines[ult:ult_end + 1] + [""]
    for tbl in ("AVX2CostTbl", "SSE42CostTbl", "SSE2CostTbl"):
        k = next(i for i in range(start, len(lines)) if "CostTableLookup(%s, ISD, MTy)" % tbl in lines[i])
        xs += ["// lines %d to %d: the lookup in %s" % (k + 1, k + 4, tbl)] + lines[k:k + 4] + [""]
    write("x86_cmpsel_cost_18.1.0.txt", "\n".join(xs) + "\n")

    # 4. the commit that changed collectLoopUniforms, and whether each tag contains it
    commit = json.loads(get("%s/commits/%s" % (API, COMMIT), "application/vnd.github+json"))
    write("commit_%s.json" % COMMIT[:10], json.dumps(commit, indent=1, sort_keys=True) + "\n")
    print("commit:", commit["sha"][:10], commit["commit"]["author"]["date"], commit["commit"]["message"].splitlines()[0])
    rows = []
    for tag in ("18.1.0", "18.1.3", "18.1.8", "19.1.0", "19.1.7"):
        cmp_ = json.loads(get("%s/compare/%s...llvmorg-%s" % (API, COMMIT[:10], tag), "application/vnd.github+json"))
        rows.append({"commit": COMMIT, "tag": "llvmorg-" + tag, "status": cmp_["status"],
                     "ahead_by": cmp_["ahead_by"], "behind_by": cmp_["behind_by"]})
        print("  compare %s...llvmorg-%s: %s (ahead_by %d, behind_by %d)" % (COMMIT[:10], tag, cmp_["status"], cmp_["ahead_by"], cmp_["behind_by"]))

    # 5. the IndVarSimplify commit that lets loop exits that trap be predicated in loops with simple stores
    commit2 = json.loads(get("%s/commits/%s" % (API, COMMIT2), "application/vnd.github+json"))
    write("commit_%s.json" % COMMIT2[:10], json.dumps(commit2, indent=1, sort_keys=True) + "\n")
    print("commit:", commit2["sha"][:10], commit2["commit"]["author"]["date"], commit2["commit"]["message"].splitlines()[0])
    for tag in ("19.1.0", "21.1.0", "21.1.8", "22.1.0", "23.1.0"):
        cmp_ = json.loads(get("%s/compare/%s...llvmorg-%s" % (API, COMMIT2[:10], tag), "application/vnd.github+json"))
        rows.append({"commit": COMMIT2, "tag": "llvmorg-" + tag, "status": cmp_["status"],
                     "ahead_by": cmp_["ahead_by"], "behind_by": cmp_["behind_by"]})
        print("  compare %s...llvmorg-%s: %s (ahead_by %d, behind_by %d)" % (
            COMMIT2[:10], tag, cmp_["status"], cmp_["ahead_by"], cmp_["behind_by"]))
    # which release tags exist in the repository (to say which one is the last of a series)
    series = {}
    for prefix in ("18.1.", "21.1."):
        refs = json.loads(get("%s/git/matching-refs/tags/llvmorg-%s" % (API, prefix), "application/vnd.github+json"))
        names = [r["ref"].rsplit("/", 1)[1] for r in refs]
        series[prefix + "x"] = sorted(names, key=lambda t: [int(x) if x.isdigit() else 0 for x in re.split(r"[.-]", t[len("llvmorg-"):])])
        print("tags llvmorg-%s*: %s" % (prefix, " ".join(series[prefix + "x"])))
    write("commit_in_tag.json", json.dumps({"note": "GitHub compare API, trimmed to the status fields. status 'ahead' means the tag contains the commit; 'diverged' or 'behind' means it does not.",
                                              "tags_in_repository": series, "rows": rows}, indent=1) + "\n")

    # 6. IndVarSimplify.cpp at four tags: the option and the side-effect test that decide whether trapping exits are predicated
    lines_out = []
    for tag in ("19.1.0", "21.1.0", "22.1.0", "23.1.0"):
        url = RAW % (tag, "Transforms/Scalar/IndVarSimplify.cpp")
        src = get(url).splitlines()
        hit = ["%d: %s" % (i + 1, ln.strip()) for i, ln in enumerate(src)
               if "indvars-predicate-loop-traps" in ln or "if (I.mayHaveSideEffects())" in ln or "LoopPredicationTraps" in ln]
        lines_out.append("== tag llvmorg-%s (%s)" % (tag, url))
        lines_out += ["  " + h for h in hit] or ["  (no line mentions indvars-predicate-loop-traps or LoopPredicationTraps)"]
        print(tag, "IndVarSimplify: %d matching lines" % len(hit))
    write("indvars_predicate_traps.txt", "\n".join(lines_out) + "\n")
    print("fetched %d files from raw.githubusercontent.com and %d answers from api.github.com" % (COUNT["files"], COUNT["api"]))


if __name__ == "__main__":
    sys.exit(main())
