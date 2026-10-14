#!/usr/bin/env python3
"""Writes site/data/, the one committed copy of the results the page reads.

    python scripts/build_site_data.py           write site/data/ from results/ and the study folders
    python scripts/build_site_data.py --check   rebuild in memory and fail if site/data/ differs

Copied unchanged:
  pooled.json        results/s4-pooled/pooled.json (criteria-v3: every job of a CPU model pooled across
                     jobs and runs, two-level bootstrap intervals, both columns, instruction counts)
  asm/<cpu>/         for each CPU model with enough jobs, the machine code of ONE of its jobs (the
                     none, fast, none_a64 and fast_a64 listings; the binaries are byte-identical across
                     jobs, which the pooled build control checks), plus builds.json extracted from that
                     job's details.json (commands, remarks, traps)
Derived, never invented (every number is computed here from the files named, and --check recomputes it):
  index.json         what the first screen and the prose print: per-CPU summaries of pooled.json, the
                     whole-program rows of the S3 runs (S4 did not time programs), the day-one record
                     and the criteria files' own 'written' lines
  mitigate.json      mitigate/ results: per loop shape and rewrite, the aligned ratio range per CPU
                     model (cells over the 2% A/A limit left out, as mitigate/README.md does), the
                     safety test, the code of each variant copied from mitigate/src/
  siblings.json      siblings/summary.json reduced to toolchain x loop: lost or not, ratio ranges
  corpus.json        the two censuses: per category, per project, shapes, controls, example loops
  fixture/pooled.json  results/fixture.json (SAMPLE, made up) in the pooled shape, for ?data=fixture
scripts/check_site.py checks that every number printed on the page is in these files.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "site", "data")

POOLED = "results/s4-pooled/pooled.json"
HOLDOUT = "results/s5-holdout/pooled.json"
HOLDOUT_PREREG = "results/s5-holdout/PREREGISTRATION.md"
CRITERIA_FILE = "harness/criteria-v3.json"
ASM_BUILDS = ("none", "fast", "none_a64", "fast_a64")
IN_CACHE = ("L1", "L2")
# S3 runs, read only for the whole-program rows (S4 runs time no programs, criteria-v3 v3.matrix.programs)
S3_RUNS = [
    {"run_id": "38121166129", "label": "S3 full run", "dir": "s3-run-38121166129"},
    {"run_id": "38121825636", "label": "S3 reproduction run", "dir": "s3-run-38121825636"},
    {"run_id": "38127024171", "label": "S3 audit run", "dir": "s3-audit-run-38127024171"},
]
S3_CRITERIA = "harness/criteria-v2.json"
MITIGATE_GLOB = "results/mitigate-run-*/mitigate-*/results.json"
SIBLINGS_SUMMARY = "siblings/summary.json"
SIBLINGS_GLOB = "results/siblings-run-*/siblings-*/siblings.json"
CORPUS = {
    "c1": "results/corpus-run-38259934735",
    "c2": "results/corpus2-baseline-run-38273183229",
    "c1_avx2": "results/corpus1-avx2-run-38273218567",
    "c2_avx2": "results/corpus2-avx2-run-38273183229",
    "combined": "results/corpus-combined-38273183229/combined.json",
}
# The rewrite each shape's section shows first: option (1) of mitigate/README.md, "What to do, per loop
# shape". Every other variant is shown beside it with its own numbers.
MITIGATE_RECOMMENDED = {"m04_rev": "pre", "m05_stride2": "span_il2", "m06_gather": "pre", "m08_matmul": "rowptr"}
# Real loops the census section quotes (project, file, line); their text and counts are read from lost_loops.json.
CORPUS_EXAMPLES = [
    ("lightgbm", "src/treelearner/feature_histogram.cpp", 736),
    ("llama.cpp", "src/llama-batch.cpp", 1247),
    ("whisper.cpp", "src/parakeet.cpp", 2821),
    ("stockfish", "src/search.cpp", 2072),
]
CLAIM = {
    "quote": "Hardening libc++ resulted in an average 0.30% performance impact",
    "after_quote": "across Google's services",
    "source": "Google Security Blog",
    "date": "Nov 15 2024",
    "url": "https://security.googleblog.com/2024/11/retrofitting-spatial-safety-to-hundreds.html",
    "google_pct": 0.30,
    "google_ratio": 1.003,
}
# The public repository's address. File links on the page point into it. Workflow-run addresses from the
# results files belong to the original private repository (404 for strangers), so they are dropped from
# site/data.
REPO_BASE = "https://github.com/JacoboPacheco/third-of-a-percent"
REPO_INFO = {
    "base": REPO_BASE,
    "measure_command": "gh workflow run measure.yml",
    "check_command": "python scripts/check.py",
}


# Related work: only sources that gaps/GAPS.md (section 0) records as actually read, with its wording.
# Every claim about a source is "as reported"; the search-summary-only items are titles, with no claim.
RELATED = {
    "gaps_file": "gaps/GAPS.md",
    "summary": (
        "Google’s post reports an average 0.30% performance impact across its services, with profile-guided "
        "optimization (PGO) improving it further. Its 2025 sequel in ACM Queue, as reported, calls PGO critical, "
        "says only five services opted out entirely, and that the fine-grained unsafe-access API was used in just "
        "seven distinct places. The closest per-benchmark study, NADER (OOPSLA 2021, on Rust), "
        "reports 76.4% of benchmarks of top crates with little, no or negative cost from unchecked indexing; NIST "
        "(2013) reports vector.at(i) 0.881% slower than a C array on sequential writes. As reported, Mytkowicz and "
        "colleagues (2009) found that link order and environment size can reverse a measured speedup, and Stabilizer "
        "(2013) treats one binary as one sample of possible layouts; that is why this study times an aligned build and "
        "a layout A/A."
    ),
    "none_found": (
        "In this search we found no public per-loop measurement of libc++’s FAST mode (we looked in the LLVM "
        "documentation, the LLVM Discourse, GitHub issues, Phoronix, Chromium’s spanification commits and the "
        "Microsoft STL hardening documentation); we found none, which is not the same as none existing."
    ),
    "main_rows": ["google", "queue", "nader", "nist", "readyset"],
    "sources": [
        {"id": "google", "m_short": "An average 0.30% across Google’s services, with PGO builds", "d_short": "A fleet average; no loop shapes or machine code", "name": "Google Security Blog, Nov 15 2024", "short": "Google’s post (2024)",
         "url": "https://security.googleblog.com/2024/11/retrofitting-spatial-safety-to-hundreds.html",
         "measured": "As reported: an average 0.30% performance impact across Google’s services; fixing one unnecessary check took the overhead from 0.35% to 0.3%; PGO further improved performance; a handful of performance-critical code paths still use explicitly unsafe accesses.",
         "differs": "A fleet average on production workloads with PGO builds; no per-loop breakdown, machine code or controls a stranger can rerun. This study tests none of its numbers."},
        {"id": "queue", "m_short": "PGO critical; five services opted out; the unsafe-access API used in seven places", "d_short": "The same fleet; PGO tested here only with the timed input as training", "name": "Dionne, Rebert, Shavrick, Varlamov, “Practical Security in Production: Hardening the C++ Standard Library at Massive Scale”, ACM Queue 23(5), 2025", "short": "ACM Queue sequel (2025)",
         "url": "https://queue.acm.org/detail.cfm?id=3773097",
         "measured": "As reported: key services were benchmarked; PGO was critical, letting the compiler move checks out of hot paths; only five services opted out entirely; the fine-grained unsafe-access API was used in just seven distinct places; a non-verbose mode cut the binary-size cost from 2% to under 0.5%.",
         "differs": "The same fleet, with its method; no loop shapes. This study’s one PGO test (training input equal to the timed input, one CPU model) did not make the cost vanish in most rows; its census (the expensive shape is rare in general code) is consistent with few unsafe sites, a link not tested here."},
        {"id": "carruth", "name": "Chandler Carruth, “Story-time: C++, bounds checking, performance, and compilers”, Nov 2024", "short": "Carruth (2024)",
         "url": "https://chandlerc.blog/posts/2024/11/story-time-bounds-checking/",
         "measured": "An expert account, not a measurement. As reported: credits LLVM’s check optimization and PGO; says without PGO the overhead would not be tolerable for most performance-sensitive workloads; warns that benchmarks of pervasive patterns skew toward confirmation bias.",
         "differs": "This study’s PGO column trains on the timed input, so it tests his PGO point only in part (it did not make the cost vanish in most rows on one CPU model); its loops are the cases where the check stays inside the loop."},
        {"id": "nader", "m_short": "76.4% of benchmarks of top Rust crates pay little, nothing or less", "d_short": "Rust; layout not controlled, here it is", "name": "Popescu, Xu, Apostolakis, August, Levy, “Safer at Any Speed” (NADER), OOPSLA 2021", "short": "NADER, OOPSLA 2021 (Rust)",
         "url": "https://www.cs.princeton.edu/~npopescu/papers/nader.pdf",
         "measured": "As reported: 76.4% of benchmarks of top Rust crates show little, no or negative cost from unchecked indexing; 23.6% are more than 1% slower with checks and 11.8% more than 1% faster; brotli’s overhead 7.7%, 6.5% on an older rustc, 2.5% on Apple M1; about 200 benchmarks with 95% intervals.",
         "differs": "Rust, many real benchmarks, several machines. As reported, it attributes checks-make-it-faster results to code layout and inlining heuristics without controlling layout; this study controls layout on eight C++ loops."},
        {"id": "nist", "m_short": "vector.at(i) 0.881% slower on sequential writes (GCC 4.6.2, bare metal)", "d_short": "One forward shape; vectorization not analysed", "name": "Flater and Guthrie (NIST), “A Case Study of Performance Degradation Attributable to Run-Time Bounds Checks on C++ Vector Access”, J. Res. NIST 118, 2013", "short": "NIST (2013)",
         "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4487316/",
         "measured": "As reported: GCC 4.6.2 on one bare-metal Xeon with frequency scaling off, 63 runs per cell; vector.at(i) 0.881% (±0.009) slower than a C array at -O3; sequential write loops only; vectorization not analysed.",
         "differs": "Bare metal and a far tighter interval, but one forward shape and an old compiler. Forward loops cost little here too; the shapes that lose SIMD are what it did not test."},
        {"id": "readyset", "m_short": "Every check removed from one Rust program: within the noise", "d_short": "A whole program; no intervals or controls", "name": "Readyset, “How much does Rust’s bounds checking actually cost?”", "short": "Readyset (blog)",
         "url": "https://readyset.io/blog/bounds-checks",
         "measured": "As reported: a rustc patched to drop every bounds check; 1,227 checks per warm read; results well within the noise threshold; no hardware or run count stated.",
         "differs": "A whole real program with every check removed; no intervals, A/A or machine code. This study times loops, not a whole program."},
        {"id": "mytkowicz", "name": "Mytkowicz, Diwan, Hauswirth, Sweeney, “Producing Wrong Data Without Doing Anything Obviously Wrong!”, ASPLOS 2009", "short": "Mytkowicz et al. (2009)",
         "url": "https://sape.inf.usi.ch/publications/asplos09.html",
         "measured": "As reported: link order and environment size change measured speedups enough to reverse conclusions; none of 133 surveyed papers adequately addressed it; the remedy is setup randomization and causal analysis.",
         "differs": "This study does a causal analysis of one layout effect (the forward add, section 3) but samples only two layouts there (section 3b adds four placements, still not many)."},
        {"id": "stabilizer", "name": "Curtsinger and Berger, Stabilizer, ASPLOS 2013", "short": "Stabilizer (2013)",
         "url": "https://github.com/ccurtsinger/stabilizer",
         "measured": "As reported: rerandomizes code, stack and heap layout at run time, because a single binary is just one sample from the space of program layouts; LLVM 3.1 only, unmaintained.",
         "differs": "Many layout samples per build; this study has two (as compiled and aligned) on a current toolchain."},
        {"id": "rustcperf", "name": "rustc-perf, the Rust compiler’s benchmark dashboard and its comparison-analysis docs", "short": "rustc-perf",
         "url": "https://github.com/rust-lang/rustc-perf/blob/master/docs/comparison-analysis.md",
         "measured": "As reported: a change counts as significant only if it is an outlier against the benchmark’s historical noise (an IQR fence), with a compare view per benchmark.",
         "differs": "A noise history drawn beside every result; Figure 1 here draws only each job’s ratio and the A/A band."},
        {"id": "quickbench", "name": "Quick C++ Benchmark", "short": "Quick C++ Benchmark",
         "url": "https://quick-bench.com/",
         "measured": "As reported: browser-run micro-benchmarks with a compiler, standard-library and flags selector, a disassembly view and share links.",
         "differs": "A stranger reruns a micro-benchmark in seconds in a browser; this study needs a checkout of its repository and GitHub Actions."},
    ],
    "not_read": [
        {"name": "Shnatsel, “How to avoid bounds checks in Rust (without unsafe!)”", "url": "https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e"},
        {"name": "Apple, -fbounds-safety, EuroLLVM 2025 slides", "url": "https://www.llvm.org/devmtg/2025-04/slides/tutorial/olsonn-stefaniski_fbounds.pdf"},
        {"name": "GCC’s _GLIBCXX_ASSERTIONS discussions (gcc-patches 2022; Ubuntu LP #2016042)", "url": ""},
        {"name": "Denis Bakhvalov, “Code alignment issues”", "url": "https://easyperf.net/blog/2018/01/18/Code_alignment_issues"},
    ],
}


def sha(path):
    """sha256 with CRLF read as LF: a Windows checkout and a Linux clone give the same value."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def rel(path):
    return os.path.relpath(path, REPO).replace("\\", "/")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_links(obj):
    """Sets every workflow_run_url to None: the runs live in the original private repository, not in REPO_BASE."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "workflow_run_url":
                m = re.search(r"/actions/runs/(\d+)", v or "")
                obj[k] = None
            else:
                run_links(v)
    elif isinstance(obj, list):
        for x in obj:
            run_links(x)
    return obj


def dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(run_links(obj), f, indent=1, sort_keys=True)
        f.write("\n")


def cpu_short(model):
    """'AMD EPYC 7763 64-Core Processor' -> 'EPYC 7763'; 'INTEL(R) XEON(R) PLATINUM 8573C' -> 'Xeon 8573C'."""
    m = re.search(r"EPYC\s+(\S+)", model or "")
    if m:
        return f"EPYC {m.group(1)}"
    m = re.search(r"Xeon(?:\(R\))?\s+(?:Platinum|Gold|Silver)?\s*(\S+)", model or "", re.I)
    if m:
        return f"Xeon {m.group(1).upper()}"
    return model or "unknown CPU"


def slug(s):
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))


def minmax(vals):
    vals = [v for v in vals if v is not None]
    return {"min": min(vals), "max": max(vals)} if vals else None


def builds_json(details):
    """Figure 2's per-build facts, taken from one job's details.json (the run's own record)."""
    out = {"pinned_cpu": details.get("pinned_cpu"), "remark_flags": details.get("remark_flags"), "kernels": {}}
    for k, kd in details.get("kernels", {}).items():
        out["kernels"][k] = {"loop_line": kd.get("loop_line")}
        for b in ("none", "fast", "novec", "none_a64", "fast_a64"):
            if b in kd:
                bd = kd[b]
                out["kernels"][k][b] = {"sha256": bd.get("sha256"), "command": bd.get("command"),
                                        "traps": bd.get("traps"),
                                        "remarks": (bd.get("vectorization") or {}).get("remarks", [])}
    return out


DAYONE_RUNS = [
    {"run_id": "38116223923", "label": "day-one run"},
    {"run_id": "38116640203", "label": "day-one rerun"},
]
CRITERIA_HISTORY = ("dayone/criteria.json", "harness/criteria.json", "harness/criteria-v2.json", "harness/criteria-v3.json")


def method_record():
    """The day-one forward cells that missed the rule as written (dayone/results/*/dayone.json) and each
    criteria file's own 'written' line."""
    dc = load(os.path.join(REPO, "dayone", "criteria.json"))
    limit = next(c for c in dc["criteria"] if c["id"] == "C2_loop_shape")["forward_max_ratio_hi"]
    runs = []
    for r in DAYONE_RUNS:
        base = os.path.join(REPO, "dayone", "results", f"run-{r['run_id']}")
        d = load(os.path.join(base, "dayone.json"))
        missed = []
        for c in d["criteria"]["C2_loop_shape"]["cells"]:
            if c["rule"].startswith("ci95_hi") and not c["met"]:
                k = c["cell"].split(".")[0]
                with open(os.path.join(base, "asm", f"{k}.none-vs-fast.diff"), encoding="utf-8") as f:
                    identical = not f.read().strip()
                missed.append({"cell_id": c["cell"], "ratio": c["ratio"], "ci95_hi": c["ci95"][1],
                               "miss_pp": (c["ci95"][1] - limit) * 100, "code_identical": identical})
        runs.append({"run_id": r["run_id"], "label": r["label"], "go": d["go"], "started_at": d["run"].get("started_at"),
                     "workflow_run_url": d["run"]["workflow_run_url"], "rule": f"ci95_hi < {limit}",
                     "limit": limit, "missed": missed})
    stored = {}
    try:
        stored = {f["file"]: f for f in load(os.path.join(OUT, "index.json"))["method"]["criteria_files"]}
    except (OSError, KeyError, ValueError):
        pass
    files = [{"file": p, "written": load(os.path.join(REPO, p)).get("written"),
              "added_commit": git_hash(p, added=True), "last_commit": git_hash(p, added=False),
              "added_at": git_time(p)} for p in CRITERIA_HISTORY]
    for f in files:  # a squashed clone's git log cannot reproduce the original commits: the recorded value wins
        for k in ("added_commit", "last_commit", "added_at"):
            rec = stored.get(f["file"], {}).get(k)
            if rec is not None:
                f[k] = rec
    v1 = load(os.path.join(REPO, "harness", "criteria.json"))["verdict"]
    v1_rule = {"point_max": v1["forward_point_max_ratio"], "ci_floor_pct": v1["forward_ci_hi_floor_pct"],
               "aa_multiplier": v1["forward_ci_hi_aa_multiplier"]}
    return {"dayone": runs, "criteria_files": files, "v1_forward_rule": v1_rule}


def stored_holdout_time():
    """The time recorded in the committed site/data/holdout.json, if any: a squashed public clone's git log cannot reproduce it."""
    try:
        return load(os.path.join(OUT, "holdout.json")).get("preregistration_committed_utc")
    except (OSError, ValueError, AttributeError):
        return None


def git_hash(path, added):
    """The short hash of the commit that added (or last changed) a file; None without git history."""
    import subprocess
    args = ["git", "-C", REPO, "log", "--format=%h"] + (["--diff-filter=A"] if added else ["-1"]) + ["--", path]
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=30).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return None
    return out[-1] if out else None


def git_time(path):
    """The UTC time (ISO 8601) of the commit that added a file; None without git history."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", REPO, "log", "--diff-filter=A", "--format=%cI", "--", path],
                             capture_output=True, text=True, timeout=30).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return None
    if not out:
        return None
    from datetime import datetime, timezone
    return datetime.fromisoformat(out[-1]).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def kernel_sources(kernels):
    """Per kernel: the one source line the timing measures (marked '// LOOP' in kernels/<k>.cpp), verbatim."""
    out = {}
    for k in kernels:
        with open(os.path.join(REPO, "kernels", f"{k}.cpp"), encoding="utf-8") as f:
            lines = f.read().splitlines()
        for i, line in enumerate(lines, 1):
            if "// LOOP" in line:
                out[k] = {"file": f"kernels/{k}.cpp", "line": i, "text": line.split("// LOOP")[0].strip()}
                break
    return out


# ---------------------------------------------------------------- the pooled measurement (Figure 1)
def cpu_summary(c, min_jobs):
    """One CPU model's pooled numbers in the shape the first screen prints."""
    cells = c["cells"]
    lost = [x for x in cells if x["class"] == "lost" and x["size_class"] in IN_CACHE]
    kept = [x for x in cells if x["class"] == "kept" and x["size_class"] in IN_CACHE]
    v = c["verdict"]
    out = {
        "cpu_model": c["cpu_model"], "cpu_short": cpu_short(c["cpu_model"]), "slug": slug(cpu_short(c["cpu_model"])),
        "jobs": c["jobs"], "runs": len(c["runs"]), "enough": c["jobs"] >= min_jobs,
        "form": v["form"], "stability": c["stability"], "why": v.get("why"),
        "aa_half_width_pct": c["aa"]["half_width_pct"],
        "n": v.get("n"), "n_as_compiled": v.get("n_as_compiled"), "x_pct": v.get("x_pct"),
        "placement_sensitive": v.get("placement_sensitive", []), "off_axis": v.get("off_axis", []),
        "reproduction": ({k: c["reproduction"][k] for k in ("checked", "outside")}
                         | {"max_gap_pct": max([m["gap_pct"] for m in c["reproduction"].get("misses", [])], default=None)})
        if c.get("reproduction") else None,
        "per_run": [{"run_id": r["run_id"], "jobs": r["jobs"], "form": r["form"]} for r in c["per_run"]],
    }
    pos = (c.get("positive") or {}).get("k04_rev.L1")
    rev = next((x for x in cells if x["cell_id"] == "k04_rev.L1"), None)
    if pos and rev:
        out["novec_rev_share_pct"] = 100.0 * (pos["ratio"] - 1) / (rev["as_compiled"]["ratio"] - 1)
        out["novec_rest_pct"] = 100.0 - out["novec_rev_share_pct"]
    if lost:
        out["lost"] = minmax([x[col]["ratio"] for x in lost for col in ("as_compiled", "aligned")])
        out["lost_aligned"] = minmax([x["aligned"]["ratio"] for x in lost])
        out["lost_compiled"] = minmax([x["as_compiled"]["ratio"] for x in lost])
        out["lost_by_kernel"] = {}
        for x in lost:
            r = out["lost_by_kernel"].setdefault(x["kernel"], {"min": None, "max": None})
            for col in ("as_compiled", "aligned"):
                q = x[col]["ratio"]
                r["min"] = q if r["min"] is None else min(r["min"], q)
                r["max"] = q if r["max"] is None else max(r["max"], q)
        out["lost_ci_lo_min"] = min(x[col]["ci95"][0] for x in lost for col in ("as_compiled", "aligned"))
        out["lost_instr"] = minmax([(x.get("aligned_instr") or {}).get("ratio") for x in lost])
    if kept:
        ps = {p["cell_id"] for p in v.get("placement_sensitive", [])}
        out["forward_judged_aligned"] = minmax([x["aligned"]["ratio"] for x in kept if x["cell_id"] not in ps])
        out["forward_aligned"] = minmax([x["aligned"]["ratio"] for x in kept])
        out["forward_compiled"] = minmax([x["as_compiled"]["ratio"] for x in kept])
        top = max(kept, key=lambda x: x["as_compiled"]["ratio"])
        out["forward_compiled_max_cell"] = {"cell_id": top["cell_id"], "ratio": top["as_compiled"]["ratio"],
                                            "aligned_ratio": top["aligned"]["ratio"]}
    return out


def copy_asm(c, inputs, out_dir):
    """The machine code and build facts of the first pooled job of this CPU model."""
    first = next(i for i in inputs if i["cpu_model"] == c["cpu_model"])
    job_dir = os.path.normpath(os.path.join(REPO, os.path.dirname(POOLED), os.path.dirname(first["path"])))
    s = slug(cpu_short(c["cpu_model"]))
    dst = os.path.join(out_dir, "asm", s)
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(os.path.join(job_dir, "asm"))):
        if any(f.endswith(f".{b}.s") for b in ASM_BUILDS):
            shutil.copyfile(os.path.join(job_dir, "asm", f), os.path.join(dst, f))
    dump(builds_json(load(os.path.join(job_dir, "details.json"))), os.path.join(dst, "builds.json"))
    doc = load(os.path.join(job_dir, "results.json"))
    job = os.path.basename(job_dir).rsplit("-", 1)[-1]
    return {"dir": f"data/asm/{s}/", "builds": f"data/asm/{s}/builds.json", "run_id": first["run_id"],
            "job": job, "source": rel(job_dir), "workflow_run_url": doc["run"]["workflow_run_url"]}, doc


def s3_programs():
    """Whole-program rows of the S3 runs (S4 runs time no programs): every job usable under criteria-v2."""
    aa_max = load(os.path.join(REPO, S3_CRITERIA))["verdict"]["aa_half_width_max_pct"]
    rows, runs = [], []
    for run in S3_RUNS:
        url = None
        for job_dir in sorted(glob.glob(os.path.join(REPO, "results", run["dir"], "results-*"))):
            doc = load(os.path.join(job_dir, "results.json"))
            url = doc["run"]["workflow_run_url"]
            hw = doc["controls"]["aa"]["half_width_pct"]
            if hw > aa_max:
                continue
            progs = {}
            for p in doc.get("programs", []):
                progs[p["name"].split("_")[0]] = {"ratio": p["ratio"], "ci95": p["ci95"],
                                                  "at_most_pct": p["consistent_with_at_most_pct"],
                                                  "aa_pct": p["aa_half_width_pct"], "traps_fast": p.get("traps_fast")}
            rows.append({"run_id": run["run_id"], "run_label": run["label"], "job": os.path.basename(job_dir).rsplit("-", 1)[-1],
                         "cpu_short": cpu_short(doc["run"]["runner"]["cpu_model"]), "programs": progs})
        runs.append({"run_id": run["run_id"], "label": run["label"], "workflow_run_url": url})
    allp = [p for r in rows for p in r["programs"].values()]
    traps = {}
    for r in rows:
        for name, p in r["programs"].items():
            traps.setdefault(name, p["traps_fast"])
    return {"criteria": S3_CRITERIA, "aa_max_pct": aa_max, "runs": runs, "rows": rows,
            "at_most_pct": minmax([p["at_most_pct"] for p in allp]), "aa_pct": minmax([p["aa_pct"] for p in allp]),
            "traps_fast": traps}


def s1_forward():
    """The forward add at L1, as compiled, in the first harness run (S1): what was seen before the aligned column (v2)."""
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "results", "s1-run-*", "results.json"))):
        doc = load(f)
        c = next((q for q in doc["cells"] if q["cell_id"] == "k02_add_fwd.L1"), None)
        if c:
            out.append({"source": rel(os.path.dirname(f)), "run_id": str(doc["run"].get("run_id") or re.search(r"(\d+)$", os.path.dirname(f)).group(1)),
                        "cpu_short": cpu_short(doc["run"]["runner"]["cpu_model"]), "ratio": c["ratio"], "ci95": c["ci95"]})
    return out


def intel_forward(pooled):
    """The forward add at L1, aligned, in every Intel job of the S3 runs, the S4 smoke run and the pooled runs (no verdict)."""
    jobs = []
    files = glob.glob(os.path.join(REPO, "results", "s3-*", "results-intel-*", "results.json"))
    files += glob.glob(os.path.join(REPO, "results", "s4-smoke-*", "results-intel-*", "results.json"))
    for f in sorted(files):
        doc = load(f)
        c = next((q for q in doc["cells"] if q["cell_id"] == "k02_add_fwd.L1"), None)
        if c and c.get("aligned"):
            jobs.append({"source": rel(os.path.dirname(f)), "cpu_short": cpu_short(doc["run"]["runner"]["cpu_model"]),
                         "aligned": c["aligned"]["ratio"], "aa_pct": doc["controls"]["aa"]["half_width_pct"]})
    for c in pooled["cpus"]:
        if "INTEL" in c["cpu_model"].upper():
            x = next((q for q in c["cells"] if q["cell_id"] == "k02_add_fwd.L1"), None)
            if x:
                jobs.append({"source": POOLED, "cpu_short": cpu_short(c["cpu_model"]), "aligned": x["aligned"]["ratio"],
                             "aa_pct": c["aa"]["half_width_pct"], "pooled_jobs": c["jobs"]})
    return {"cell": "k02_add_fwd.L1", "jobs": jobs, "aligned": minmax([j["aligned"] for j in jobs]),
            "cpus": sorted({j["cpu_short"] for j in jobs})}


# ---------------------------------------------------------------- what to change (mitigate/)
def variant_code(src_path, variant):
    """The lines of one variant's #if block in mitigate/src/<kernel>.cpp, comments dropped, verbatim otherwise."""
    with open(os.path.join(REPO, src_path), encoding="utf-8") as f:
        lines = f.read().splitlines()
    out, on = [], False
    for line in lines:
        s = line.strip()
        if s.startswith(("#if defined(V_", "#elif defined(V_")):
            on = s.endswith(f"defined(V_{variant})")
            continue
        if s.startswith(("#else", "#endif")):
            on = False
            continue
        if on and not s.startswith("//"):
            out.append(line.split("  // LOOP")[0].rstrip())
    ind = min((len(l) - len(l.lstrip()) for l in out if l.strip() and not l.lstrip().startswith("#")), default=0)
    return [l[ind:] if not l.lstrip().startswith("#") else l.lstrip() for l in out]


def mitigate_data():
    files = sorted(glob.glob(os.path.join(REPO, MITIGATE_GLOB)))
    crit = load(os.path.join(REPO, "mitigate", "criteria.json"))
    aa_max = 2.0  # the reading rules' usable_job limit and the cell rule in mitigate/README.md (2 %)
    assert "2%" in crit["reading"]["usable_job"]
    shapes, jobs, cpus = {}, [], []
    for f in files:
        d = load(f)
        model = d["run"]["cpu_model"]
        cs = cpu_short(model)
        if cs not in cpus:
            cpus.append(cs)
        hws = [kd["aa"][sz]["half_width_pct"] for kd in d["kernels"].values() for sz in IN_CACHE]
        jobs.append({"run_id": d["run"]["id"], "job": d["run"]["job"], "cpu_short": cs, "aa_max_pct": max(hws),
                     "usable": max(hws) <= aa_max})
        for k, kd in d["kernels"].items():
            sh = shapes.setdefault(k, {"kernel": k, "original_kernel": kd["original_kernel"], "shape": kd["shape"],
                                       "source": kd["source"], "variants": {}, "order": list(kd["variants"].keys())})
            for v in kd["variants"]:
                if v not in sh["order"]:
                    sh["order"].append(v)
            for v, vd in kd["variants"].items():
                e = sh["variants"].setdefault(v, {"variant": v, "what": vd["what"], "safety_claim": vd["safety_claim"],
                                                  "readability_cost": vd["readability_cost"], "keeps_safety": [],
                                                  "short_none": [], "short_fast": [], "per_cpu": {}, "cells_left_out": 0,
                                                  "vectorized_fast": None, "code": variant_code(kd["source"], v)})
                e["keeps_safety"].append(vd["keeps_safety"])
                e["short_none"].append(vd["safety"]["none"]["outcome"])
                e["short_fast"].append(vd["safety"]["fast"]["outcome"])
                vf = (vd["builds"].get("fast_a64") or vd["builds"].get("fast") or {}).get("vectorization") or {}
                e["vectorized_fast"] = vf.get("vectorized")
                for sz in IN_CACHE:
                    t = (vd.get("timing") or {}).get(sz)
                    if not t:
                        continue
                    if kd["aa"][sz]["half_width_pct"] > aa_max:
                        e["cells_left_out"] += 1
                        continue
                    p = t["vs_original_aligned"]
                    pc = e["per_cpu"].setdefault(cs, {"L1": [], "L2": []})
                    pc[sz].append({"ratio": p["ratio"], "ci95": p["ci95"], "run_id": d["run"]["id"], "job": d["run"]["job"]})
    out_shapes = []
    for k in ("m04_rev", "m05_stride2", "m06_gather", "m08_matmul"):
        sh = shapes[k]
        vs = []
        for v in sh["order"]:
            e = sh["variants"][v]
            allr = [c["ratio"] for pc in e["per_cpu"].values() for sz in IN_CACHE for c in pc[sz]]
            e["keeps_safety"] = all(e["keeps_safety"])
            e["short_none"] = sorted(set(e["short_none"]))
            e["short_fast"] = sorted(set(e["short_fast"]))
            e["range"] = minmax(allr)
            e["cells"] = len(allr)
            e["per_cpu_range"] = {cs: {sz: minmax([c["ratio"] for c in pc[sz]]) for sz in IN_CACHE}
                                  | {"both": minmax([c["ratio"] for sz in IN_CACHE for c in pc[sz]]),
                                     "jobs": len({(c["run_id"], c["job"]) for sz in IN_CACHE for c in pc[sz]})}
                                  for cs, pc in e["per_cpu"].items()}
            vs.append(e)
        out_shapes.append({"kernel": k, "original_kernel": sh["original_kernel"], "shape": sh["shape"],
                           "source": sh["source"], "recommended": MITIGATE_RECOMMENDED[k], "variants": vs})
    usable = [j for j in jobs if j["usable"]]
    return {
        "note": "derived by scripts/build_site_data.py from " + MITIGATE_GLOB + ", mitigate/criteria.json and mitigate/src/",
        "sources": sorted({rel(os.path.dirname(os.path.dirname(f))) for f in files}),
        "aa_max_pct": aa_max, "cpus": cpus, "jobs": jobs, "job_count": len(jobs),
        "usable_jobs": len(usable), "usable_cpus": sorted({j["cpu_short"] for j in usable}),
        "rules_written": crit["what"], "added_after_first_run": crit["added_after_the_first_timed_run"],
        "headline_rule": crit["reading"]["headline_claim"], "recovered_rule": crit["reading"]["recovered"],
        "shapes": out_shapes,
    }


# ---------------------------------------------------------------- other toolchains (siblings/)
SIB_VARIANTS = [
    ("clang18-fast", "clang 18, libc++ FAST", "the setup of every other section"),
    ("clang18-extensive", "clang 18, libc++ EXTENSIVE", ""),
    ("clang18-debug", "clang 18, libc++ DEBUG", ""),
    ("clang20-fast", "clang 20, libc++ 20 FAST", ""),
    ("clang18v3-fast", "clang 18, FAST, AVX2", "-march=x86-64-v3"),
    ("gcc14-O2-assert", "GCC 14 -O2, assertions", "libstdc++ _GLIBCXX_ASSERTIONS"),
    ("gcc14-O3-assert", "GCC 14 -O3, assertions", "libstdc++ _GLIBCXX_ASSERTIONS"),
]


def siblings_data():
    s = load(os.path.join(REPO, SIBLINGS_SUMMARY))
    vec = {}  # (variant, kernel) -> (vectorized unhardened, vectorized hardened), from one job per part
    seen = set()
    for f in sorted(glob.glob(os.path.join(REPO, SIBLINGS_GLOB))):
        d = load(f)
        for c in d["cells"]:
            key = (c["variant"], c["kernel"])
            if key in seen:
                continue
            seen.add(key)
            vec[key] = (bool(c["vectorized_none"]["vectorized"]), bool(c["vectorized_hard"]["vectorized"]))
    kernels = sorted({k.split("|")[1] for k in s["cells"]})
    rows = []
    thin = 0
    groups = 0
    for vid, label, note in SIB_VARIANTS:
        cells = {}
        for k in kernels:
            vn, vh = vec.get((vid, k), (None, None))
            status = "lost" if vn and not vh else "kept" if vn and vh else "neither"
            per_cpu = {}
            for key, lst in s["cells"].items():
                v, kk, sz, cpu = key.split("|")
                if v != vid or kk != k:
                    continue
                groups += 1
                thin += len(lst) == 1
                pc = per_cpu.setdefault(cpu, {"L1": None, "L2": None, "jobs": 0})
                pc[sz] = minmax([x["ratio"] for x in lst])
                pc["jobs"] = max(pc["jobs"], len(lst))
            allr = [x["ratio"] for key, lst in s["cells"].items() if key.split("|")[0] == vid and key.split("|")[1] == k for x in lst]
            cells[k] = {"status": status, "range": minmax(allr), "jobs": max([p["jobs"] for p in per_cpu.values()], default=0),
                        "single_job_cpus": sorted(c for c, p in per_cpu.items() if p["jobs"] == 1), "per_cpu": per_cpu}
        rows.append({"variant": vid, "label": label, "note": note, "lost": s["lost"][vid], "cells": cells,
                     "cpus": sorted({cpu for c in cells.values() for cpu in c["per_cpu"]})})
    runs = sorted({j["file"].split("/")[0] for j in s["jobs"]})
    return {"note": "derived by scripts/build_site_data.py from " + SIBLINGS_SUMMARY + " and one siblings.json per part",
            "source": SIBLINGS_SUMMARY, "runs": runs, "jobs": len(s["jobs"]), "excluded": len(s["excluded"]),
            "cpus": s["cpus"], "kernels": kernels, "rows": rows, "groups": groups, "single_job_groups": thin}


# ---------------------------------------------------------------- the censuses (corpus/)
def corpus_data():
    comb = load(os.path.join(REPO, CORPUS["combined"]))
    c1 = load(os.path.join(REPO, CORPUS["c1"], "corpus.json"))
    c2 = load(os.path.join(REPO, CORPUS["c2"], "corpus.json"))
    c1a = load(os.path.join(REPO, CORPUS["c1_avx2"], "corpus.json"))
    c2a = load(os.path.join(REPO, CORPUS["c2_avx2"], "corpus.json"))
    lost2 = load(os.path.join(REPO, CORPUS["c2"], "lost_loops.json"))["lost"]

    def clean(r):
        r = dict(r)
        r["label"] = r["label"].replace("*", "")
        return r

    cats = []
    for r in comb["baseline"]:
        r = clean(r)
        census, _, name = r["label"].partition(": ")
        r["census"] = 1 if census.startswith("census 1") else 2 if census.startswith("census 2") else 0
        r["category"] = name if name else census
        r["total"] = "total" in r["label"] or r["label"] == "combined"
        cats.append(r)

    projects = []
    for p in c2["projects"]:
        projects.append({"name": p["name"], "category": p["category"], "kind": p.get("kind"),
                         "vectorized": p["none"]["vectorized"], "vectorized_unique": p["none"]["vectorized_unique"],
                         "lost": p["lost"], "lost_with_index_evidence": p.get("lost_with_index_evidence"),
                         "ud2_added": p["ud2_added"], "text_change_pct": p["text_bytes_change_pct"]})
    locs = {}
    for x in lost2:
        locs.setdefault((x["project"], x["file"], x["line"]), set()).add(x["column"])
    lost_unique_by_project = {}
    for x in lost2:
        lost_unique_by_project.setdefault(x["project"], set()).add((x["file"], x["line"], x["column"]))
    for p in projects:
        p["lost_unique"] = len(lost_unique_by_project.get(p["name"], ()))
    projects.sort(key=lambda p: (-p["lost"], p["name"]))

    big = max(projects, key=lambda p: p["lost"])
    t2 = c2["totals"]
    without = {"project": big["name"], "vectorized": t2["none"]["vectorized"] - big["vectorized"],
               "lost": t2["lost"] - big["lost"], "lost_unique": t2["lost_unique_locations"] - big["lost_unique"]}
    without["lost_pct"] = 100 * without["lost"] / without["vectorized"]

    ev_locs = {}
    for x in lost2:
        key = (x["project"], x["file"], x["line"], x["column"])
        ev_locs[key] = ev_locs.get(key, False) or x["index_evidence"]["status"].startswith("checked")
    # per category, every project (corpus/combine.py's own grouping, so the rows add up to Figure 4's)
    sys.path.insert(0, os.path.join(REPO, "corpus"))
    import combine  # noqa: E402  (read-only use of the census's own table code)
    by_category = {}
    for cen, key in ((1, "c1"), (2, "c2")):
        for r in combine.rows_of(combine.load(os.path.join(REPO, CORPUS[key])), f"census {cen}"):
            by_category.setdefault(f"{cen}|{r['category']}", []).append(
                {k: r[k] for k in ("project", "vectorized", "vectorized_unique", "lost", "lost_unique")})
    for rows in by_category.values():
        rows.sort(key=lambda r: (-r["lost"], -r["vectorized"], r["project"]))
    examples = []
    for proj, path, line in CORPUS_EXAMPLES:
        xs = [x for x in lost2 if x["project"] == proj and x["file"] == path and x["line"] == line]
        x = xs[0]
        examples.append({"project": proj, "where": f"{path}:{line}", "count": sum(e["count"] for e in xs),
                         "class": x["class"], "detail": x["detail"], "bound": x["trip_count"].get("bound"),
                         "context": x["context"], "fast_remark": x["fast_remarks"][-1] if x["fast_remarks"] else None,
                         "evidence": x["index_evidence"]["status"], "messages": sorted(set(x["index_evidence"]["messages"]))})

    def ctl(c):
        out = {}
        for k, v in c["controls"].items():
            e = {"pass": v.get("pass"), "rule": v.get("rule")}
            if k == "kernels":
                bad = [x for x in v.get("kernels", []) if not x.get("pass")]
                e["misses"] = [{"kernel": x["kernel"], "status": x["status"], "expected": x["expected"]} for x in bad]
                e["lost_kernels"] = v.get("lost_kernels")
                ie = v.get("index_evidence")
                if ie:
                    e["index_evidence_pass"] = ie.get("pass")
            out[k] = e
        return out

    return {
        "note": "derived by scripts/build_site_data.py from " + ", ".join(CORPUS.values()),
        "sources": CORPUS, "categories": cats, "avx2": [clean(r) for r in comb["avx2"]],
        "census1": {"totals": c1["totals"], "controls": ctl(c1), "projects": c1["totals"]["projects"]},
        "census2": {"totals": t2, "controls": ctl(c2), "patterns": [{k: p[k] for k in ("class", "detail", "count", "unique_locations")} for p in c2["patterns"]],
                    "patterns_unlabelled": {"count": t2["lost"] - sum(p["count"] for p in c2["patterns"]),
                                            "unique_locations": t2["lost_unique_locations"] - sum(p["unique_locations"] for p in c2["patterns"])},
                    "lost_unique_with_evidence": sum(ev_locs.values()), "projects": projects, "without_biggest": without,
                    "toolchain": c2["toolchain"]["clang"]},
        "census1_avx2": {"totals": c1a["totals"], "controls": ctl(c1a), "dropped": c1a.get("dropped")},
        "census2_avx2": {"totals": c2a["totals"], "controls": ctl(c2a)},
        "examples": examples,
        "by_category": by_category,
        "plan": "corpus/PLAN2.md",
    }


# ---------------------------------------------------------------- the SAMPLE fixture
def fixture_pooled(fx):
    """results/fixture.json (made-up numbers, sample: true) in the pooled shape the page reads."""
    d = load(fx)
    cells = []
    for c in d["cells"]:
        vn, vf = c["vectorized_none"]["vectorized"], c["vectorized_fast"]["vectorized"]
        cls = "lost" if vn and not vf else "kept" if vn and vf else "off_axis"
        e = {"cell_id": c["cell_id"], "kernel": c["kernel"], "size_class": c["size_class"], "class": cls,
             "as_compiled": {"ratio": c["ratio"], "ci95": c["ci95"], "jobs": 1}, "instr": c.get("instr")}
        if c.get("aligned"):
            e["aligned"] = {"ratio": c["aligned"]["ratio"], "ci95": c["aligned"]["ci95"], "jobs": 1}
        cells.append(e)
    model = d["run"]["runner"]["cpu_model"]
    return {"kind": "pooled", "sample": True, "source": rel(fx),
            "cpus": [{"cpu_model": model, "jobs": 1, "runs": ["SAMPLE"], "cells": cells, "positive": {},
                      "verdict": {"form": d["verdict"]["form"], "placement_sensitive": [], "off_axis": []}}]}


# ---------------------------------------------------------------- build
def holdout_data(min_jobs):
    """The holdout run beside the original pooled runs: same rules, fresh draws (numbers read from both pooled.json)."""
    import statistics
    orig, hold = load(os.path.join(REPO, POOLED)), load(os.path.join(REPO, HOLDOUT))
    assert orig["criteria_sha256"] == hold["criteria_sha256"], "holdout was judged under other criteria"

    def side(doc):
        out = {}
        for c in doc["cpus"]:
            lost = [x["aligned"]["ratio"] for x in c["cells"] if x["class"] == "lost" and x["size_class"] in IN_CACHE]
            out[c["cpu_model"]] = {
                "jobs": c["jobs"], "runs": len(c["runs"]), "form": c["verdict"]["form"],
                "enough": c["jobs"] >= min_jobs, "stability": c["stability"],
                "lost": ({"min": min(lost), "max": max(lost), "median": statistics.median(lost)} if lost else None),
                "runs_with_enough": sum(1 for r in c["per_run"] if r["jobs"] >= min_jobs),
            }
        return out
    a, b = side(orig), side(hold)
    rows = []
    for m in sorted(set(a) | set(b)):
        o, h = a.get(m), b.get(m)
        both = bool(o and h and o["enough"] and h["enough"])
        rows.append({"cpu_model": m, "cpu_short": cpu_short(m), "original": o, "holdout": h,
                     "reproduced": (o["form"] == h["form"]) if both else None})
    return {"source": HOLDOUT, "original_source": POOLED, "preregistration": HOLDOUT_PREREG,
            "result": "results/s5-holdout/RESULT.md",
            "preregistration_committed_utc": stored_holdout_time() or git_time(HOLDOUT_PREREG),
            "criteria_sha256": hold["criteria_sha256"], "runs": hold["runs"], "jobs": len(hold["inputs"]),
            "rows": rows}


def build(out_dir):
    pooled_path = os.path.join(REPO, POOLED)
    pooled = load(pooled_path)
    crit = load(os.path.join(REPO, CRITERIA_FILE))
    v3 = crit["v3"]
    assert pooled["criteria_file"] == CRITERIA_FILE
    min_jobs = v3["pooling"]["minimum_jobs"]
    with open(pooled_path, "rb") as f:  # unchanged except line endings (LF, as .gitattributes stores it)
        raw = f.read().replace(b"\r\n", b"\n")
    with open(os.path.join(out_dir, "pooled.json"), "wb") as f:
        f.write(raw)
    index = {
        "schema": "site-2",
        "note": "written by scripts/build_site_data.py from results/ and the study folders; do not edit by hand",
        "claim": CLAIM, "repo": REPO_INFO,
        "criteria": {
            "file": CRITERIA_FILE, "sha256": sha(os.path.join(REPO, CRITERIA_FILE)), "written": crit["written"],
            "aa_half_width_max_pct": crit["verdict"]["aa_half_width_max_pct"],
            "forward_point_max_ratio": crit["verdict"]["forward_point_max_ratio"],
            "forward_ci_hi_floor_pct": crit["verdict"]["forward_ci_hi_floor_pct"],
            "lost_ci_lo_min_ratio": crit["verdict"]["lost_ci_lo_min_ratio"],
            "align_flag": crit["v2"]["align_flag"],
            "reps_per_side": v3["timing"]["reps_per_side"],
            "resamples": pooled["resamples"],
            "minimum_jobs": min_jobs,
            "jobs_per_run": v3["matrix"]["jobs_per_run"],
            "kernels": crit["design"]["kernels"],
            "builds": crit["design"]["builds"],
        },
        "kernel_source": kernel_sources(crit["design"]["kernels"]),
        "pooled": {"path": "data/pooled.json", "source": POOLED, "source_sha256": hashlib.sha256(raw).hexdigest(),
                   "runs": [], "jobs": len(pooled["inputs"])},
        "cpus": [],
    }
    run_urls = {}
    for c in pooled["cpus"]:
        e = cpu_summary(c, min_jobs)
        if e["enough"]:
            e["asm"], doc = copy_asm(c, pooled["inputs"], out_dir)
            run_urls.setdefault(e["asm"]["run_id"], e["asm"]["workflow_run_url"])
            if "toolchain" not in index:
                index["toolchain"] = {"clang": doc["run"]["toolchain"]["clang"],
                                      "libcxx_package": doc["run"]["toolchain"]["libcxx_package"],
                                      "os": doc["run"]["runner"]["os"], "common_flags": doc["run"]["flags"]["common"]}
        index["cpus"].append(e)
    for rid in pooled["runs"]:
        url = run_urls.get(rid)
        if url is None:
            first = next(i for i in pooled["inputs"] if i["run_id"] == rid)
            url = load(os.path.normpath(os.path.join(REPO, os.path.dirname(POOLED), first["path"])))["run"]["workflow_run_url"]
        index["pooled"]["runs"].append({"run_id": rid, "workflow_run_url": url,
                                        "jobs": sum(1 for i in pooled["inputs"] if i["run_id"] == rid)})
    good = [c for c in index["cpus"] if c["enough"]]
    index["page"] = {
        "cpus_enough": len(good), "jobs_enough": sum(c["jobs"] for c in good),
        "cpus_few": [{"cpu_short": c["cpu_short"], "jobs": c["jobs"], "form": c["form"]} for c in index["cpus"] if not c["enough"]],
        "lost": minmax([v for c in good for v in (c["lost"]["min"], c["lost"]["max"])]),
        "lost_instr": minmax([v for c in good for v in (c["lost_instr"]["min"], c["lost_instr"]["max"])]),
        "forward": {"aligned": minmax([v for c in good for v in (c["forward_aligned"]["min"], c["forward_aligned"]["max"])]),
                    "compiled": minmax([v for c in good for v in (c["forward_compiled"]["min"], c["forward_compiled"]["max"])]),
                    "compiled_max_cell": max((c["forward_compiled_max_cell"] for c in good), key=lambda x: x["ratio"])},
        "forms": sorted({c["form"] for c in good}),
    }
    index["page"]["lost_all_above_min"] = all(c["lost_ci_lo_min"] >= crit["verdict"]["lost_ci_lo_min_ratio"] for c in good)
    index["default_cpu"] = max(good, key=lambda c: c["jobs"])["slug"]
    index["method"] = method_record()
    index["programs"] = s3_programs()
    index["intel_forward"] = intel_forward(pooled)
    index["s1_forward"] = s1_forward()
    index["sections"] = {"mitigate": "data/mitigate.json", "siblings": "data/siblings.json", "corpus": "data/corpus.json",
                         "realworld": "data/realworld.json", "holdout": "data/holdout.json", "related": "data/related.json", "cesweep": "data/cesweep.json",
                         "layout": "data/layout.json", "pgo": "data/pgo.json",
                         "versions": "data/versions.json", "environment": "data/environment.json"}
    dump(versions_data(min_jobs), os.path.join(out_dir, "versions.json"))
    dump(environment_data(), os.path.join(out_dir, "environment.json"))
    dump(holdout_data(min_jobs), os.path.join(out_dir, "holdout.json"))
    dump(ce_sweep_data(), os.path.join(out_dir, "cesweep.json"))
    dump(layout_data(), os.path.join(out_dir, "layout.json"))
    dump(pgo_data(), os.path.join(out_dir, "pgo.json"))
    dump(RELATED, os.path.join(out_dir, "related.json"))
    dump(realworld_data(index["page"]["lost"]["max"]), os.path.join(out_dir, "realworld.json"))
    dump(mitigate_data(), os.path.join(out_dir, "mitigate.json"))
    dump(siblings_data(), os.path.join(out_dir, "siblings.json"))
    dump(corpus_data(), os.path.join(out_dir, "corpus.json"))
    fx = os.path.join(REPO, "results", "fixture.json")
    dump(fixture_pooled(fx), os.path.join(out_dir, "fixture", "pooled.json"))
    index["fixture"] = {"path": "data/fixture/pooled.json", "source": rel(fx), "source_sha256": sha(fx),
                        "cpu_model": load(fx)["run"]["runner"]["cpu_model"]}
    dump(index, os.path.join(out_dir, "index.json"))
    return index


RW_POOLED = "results/realworld-pooled/realworld.json"
RW_BUILD_RUN = "38402534350"  # the build run whose binaries the three measure runs timed
RW_LABELS = {
    "lightgbm_default": ("LightGBM", "binary classification, default options", False, "lightgbm"),
    "lightgbm_multiclass": ("LightGBM", "8 classes, categorical features, bagging (options chosen to run lost loops)", False, "lightgbm"),
    "lightgbm_linear": ("LightGBM", "linear trees (an option chosen to run lost loops)", False, "lightgbm"),
    "draco": ("Draco", "mesh and point-cloud encode and decode", False, "draco"),
    "tinydnn": ("tiny-dnn", "train a small fully connected network one epoch", False, "tinydnn"),
    "spectra": ("Spectra", "top-8 eigenvalues, dense and sparse", False, "spectra"),
    "meshopt": ("meshoptimizer", "mesh optimization pipeline; no lost loop (control)", True, "meshopt"),
    "fmt": ("{fmt}", "number formatting; no lost loop (control)", True, "fmt"),
}
# realworld/PLAN.md, "What is expected" (written before any build or run): (low, high, call)
RW_EXPECT = {
    "lightgbm_default": (0.99, 1.03, "probably not"), "lightgbm_multiclass": (1.00, 1.06, "maybe"),
    "lightgbm_linear": (1.02, 1.20, "yes"), "draco": (0.99, 1.04, "probably not"),
    "tinydnn": (1.00, 1.10, "maybe"), "spectra": (0.99, 1.02, "no"),
    "meshopt": (0.99, 1.01, "no"), "fmt": (0.97, 1.02, "no, or faster"),
}


def rw_pair(p):
    t = p["time"]
    return {"ratio": t["ratio"], "lo": t["ci95"][0], "hi": t["ci95"][1], "half_width_pct": t["half_width_pct"]}


def rw_group(g, minimum):
    rows = {}
    for r in g["rows"]:
        pr = r["pairs"]
        rows[r["row"]] = {"fast": rw_pair(pr["fast"]), "aligned": rw_pair(pr["aligned"]), "aa": rw_pair(pr["aa"]),
                          "layout": rw_pair(pr["layout"]), "reading": r["reading"].get("reading"),
                          "at_most_pct": r["reading"].get("at_most_pct"), "text": r["reading"].get("text")}
    m = re.search(r"EPYC (\w+)", g["cpu_model"])
    return {"cpu_model": g["cpu_model"], "cpu_short": ("EPYC " + m.group(1)) if m else g["cpu_model"],
            "jobs": g["jobs"], "runs": len(g.get("runs", [])), "enough": g["jobs"] >= minimum, "rows": rows}


def realworld_data(lost_max):
    """The real programs: Cachegrind profiles and build facts of the timed build run, and the pooled timing
    (results/realworld-pooled/realworld.json, checked by realworld/check.py)."""
    pooled = load(os.path.join(REPO, RW_POOLED))
    ctx = pooled["context"]
    out = []
    for name, (project, what, control, proj) in RW_LABELS.items():
        pr = ctx["profiles"][name][0]
        b = ctx["builds"][proj][0]
        r = {"instr_ratio": pr["instructions"]["ratio"],
             "lines_none": pr["loop_lines_share"]["none"] * 100, "lines_fast": pr["loop_lines_share"]["fast"] * 100,
             "funcs_none": pr["functions_share"]["none"] * 100, "funcs_fast": pr["functions_share"]["fast"] * 100,
             "funcs_matched": pr["functions_matched"], "funcs_listed": pr["functions_listed"],
             "traps_none": b["traps"]["none"], "traps_fast": b["traps"]["fast"],
             "lost_listed": b["lost_locations"], "lost_here_too": b["lost_here_too"],
             "outputs_match": bool(pr["checksums_exact_match"]), "approximate": not all(b["text_identical"].values()),
             "build_run": RW_BUILD_RUN, "source": RW_POOLED,
             "row": name, "project": project, "what": what, "control": control}
        if not control:
            r["est_lines_pct"] = r["lines_none"] * (lost_max - 1)
            r["est_funcs_pct"] = r["funcs_none"] * (lost_max - 1)
            # the share of FAST's extra instructions that falls on the lost loops' lines and functions (in NONE units)
            if r["instr_ratio"] > 1.001:
                d = r["instr_ratio"] - 1
                r["extra_lines_pct"] = (r["lines_fast"] * r["instr_ratio"] - r["lines_none"]) / d
                r["extra_funcs_pct"] = (r["funcs_fast"] * r["instr_ratio"] - r["funcs_none"]) / d
        out.append(r)
    minimum = pooled["minimum_jobs"]
    groups = [rw_group(g, minimum) for g in pooled["cpus"]]
    allr = rw_group(pooled["all_runners"], 0)
    main = next(g for g in groups if g["enough"])  # the one CPU model with enough jobs
    expect = []
    for name, (lo, hi, call) in RW_EXPECT.items():
        m = main["rows"][name]
        inside = all(lo <= m[c]["ratio"] <= hi for c in ("fast", "aligned"))
        det = m["reading"]
        call_ok = {"yes": det == "detectably slower", "probably not": det == "not detectable", "no": det == "not detectable",
                   "maybe": True, "no, or faster": det in ("not detectable", "detectably faster")}[call]
        expect.append({"row": name, "low": lo, "high": hi, "call": call, "inside": inside, "call_ok": call_ok,
                       "held": inside and call_ok, "reading": det, "fast": m["fast"]["ratio"], "aligned": m["aligned"]["ratio"]})
    slow = [m[c]["ratio"] for m in main["rows"].values() if m["reading"] == "detectably slower" for c in ("fast", "aligned")]
    return {"source": RW_POOLED, "plan": "realworld/PLAN.md", "readme": "realworld/README.md", "rows": out,
            "est_ratio": lost_max, "minimum_jobs": minimum, "build_run": RW_BUILD_RUN, "runs": pooled["runs"],
            "timing": {"groups": groups, "all": allr, "main_cpu": main["cpu_model"], "expect": expect,
                       "slow_min": min(slow), "slow_max": max(slow),
                       "jobs": len(pooled["inputs"]), "processes_per_side": 40, "abba_pairs": 4}}


# ---------------------------------------------------------------- layout sweep (layout-sweep/) and PGO column (pgo/)
LAYOUT_GLOB = "layout-sweep/results/pooled/analysis.json"  # all runs pooled, one row per CPU model (checked by layout-sweep/check.py)
PGO_POOLED = "results/pgo-pooled/pgo.json"
PGO_REPORT = "pgo/report.md"
KERNEL_NAMES = {"k01_sum_fwd": "forward sum", "k02_add_fwd": "forward add", "k03_stencil": "stencil", "k04_rev": "reverse"}
PGO_NAMES = {"lightgbm_default": "LightGBM (default)", "lightgbm_multiclass": "LightGBM (multiclass)",
             "lightgbm_linear": "LightGBM (linear)", "draco": "Draco", "tinydnn": "tiny-dnn", "spectra": "Spectra",
             "meshopt": "meshoptimizer (control)", "fmt": "{fmt} (control)"}


def layout_data():
    """layout-sweep/results/pooled/analysis.json (checked by layout-sweep/check.py), reduced to what the page prints."""
    paths = sorted(glob.glob(os.path.join(REPO, LAYOUT_GLOB)))
    if not paths:
        return {"sources": [], "cpus": []}
    docs = [(p, load(p)) for p in paths]
    cpus, modes = [], set()
    for p, d in docs:
        for b in d["cpus"]:
            modes.add((b["mode"], b["placements"], b["step_bytes"]))
            rows = []
            for c in b["cells"]:
                rows.append({"kernel": c["kernel"], "name": KERNEL_NAMES.get(c["kernel"], c["kernel"]), "size": c["size_class"],
                             "class": c["class"], "min": c["ratio_min"], "median": c["ratio_median"], "max": c["ratio_max"],
                             "n_pass": c["n_pass"], "n_cost": c["n_cost"], "n_placements": c["n_placements"], "verdict": c["verdict"],
                             "aa_half_width_pct": c["aa"]["half_width_pct"],
                             "as_compiled": c["refs"]["ref"]["ratio"] if "ref" in c["refs"] else None,
                             "aligned": c["refs"]["a64"]["ratio"] if "a64" in c["refs"] else None})
            cpus.append({"cpu_model": b["cpu_model"], "cpu_short": cpu_short(b["cpu_model"]), "jobs": b["jobs"],
                         "runs": b["runs"], "enough": not any(x.startswith("too few jobs") for x in b["problems"]),
                         "mode": b["mode"], "placements": b["placements"], "step_bytes": b["step_bytes"],
                         "forward_claim": b["forward_claim"], "lost_control": b["lost_control"], "rows": rows})
    assert len(modes) == 1, "the layout sweep analyses mix placement modes"
    mode, n, step = next(iter(modes))
    good = [c for c in cpus if c["enough"]]
    rev = [r for c in good for r in c["rows"] if r["class"] == "lost"]
    out = {"sources": [rel(p) for p, _ in docs], "sources_sha256": [sha(p) for p, _ in docs],
           "plan": "layout-sweep/PLAN.md", "mode": mode, "placements": n, "step_bytes": step,
           "residues": [step * i for i in range(n)], "cpus": cpus}
    crit = load(os.path.join(REPO, "layout-sweep", "criteria.json"))
    r, m = crit["rules"], crit["modes"][mode]
    out["rules"] = {"file": "layout-sweep/criteria.json", "forward_point_max_ratio": r["forward_point_max_ratio"],
                    "forward_ci_hi_floor_pct": r["forward_ci_hi_floor_pct"], "forward_ci_hi_aa_multiplier": r["forward_ci_hi_aa_multiplier"],
                    "aa_half_width_max_pct": r["aa_half_width_max_pct"], "lost_ci_lo_min_ratio": r["lost_ci_lo_min_ratio"],
                    "robust_min_pass": m["robust_min_pass"], "dependent_max_pass": m["dependent_max_pass"],
                    "min_jobs": crit["design"]["min_jobs_per_cpu"], "reps_per_side": crit["design"]["reps_per_side"]}
    if rev:
        out["reverse"] = {"min": min(r["min"] for r in rev), "max": max(r["max"] for r in rev)}
    for k in ("k01_sum_fwd", "k02_add_fwd", "k03_stencil"):
        rs = [r for c in good for r in c["rows"] if r["kernel"] == k]
        if rs:
            out.setdefault("kernels", {})[k] = {"name": KERNEL_NAMES[k], "min": min(r["min"] for r in rs),
                                                 "max": max(r["max"] for r in rs),
                                                 "verdicts": sorted({r["verdict"] for r in rs})}
    return out


def pgo_data():
    """The pooled PGO file against the non-PGO pool (the same readings pgo/analyze.py renders in pgo/report.md)."""
    sys.path.insert(0, os.path.join(REPO, "pgo"))
    import analyze as pa  # pgo/analyze.py
    sys.path.pop(0)
    path = os.path.join(REPO, PGO_POOLED)
    if not os.path.exists(path):
        return {"cpus": []}
    pgo = load(path)
    base = load(os.path.join(REPO, RW_POOLED))
    base_cpus = {b["cpu_model"]: b for b in base["cpus"]}
    minimum = pgo["minimum_jobs"]

    def side(row, kind):
        if row is None:
            return None
        out = {}
        for pair in ("fast", "aligned"):
            c = pa._cell(row, pair)
            out[pair] = {"ratio": c["ratio"], "lo": c["ci95"][0], "hi": c["ci95"][1]}
        rd = row.get("reading") or {}
        out["reading"] = rd.get("reading")
        out["at_most_pct"] = rd.get("at_most_pct")
        out["aa_half_width_pct"] = pa._hw(row)
        return out

    cpus = []
    for b in pgo["cpus"]:
        bb = base_cpus.get(b["cpu_model"])
        brows = {r["row"]: r for r in bb["rows"]} if bb else {}
        rows = []
        for r in b["rows"]:
            rows.append({"row": r["row"], "name": PGO_NAMES[r["row"]], "base": side(brows.get(r["row"]), "base"),
                         "pgo": side(r, "pgo"), "compare": pa.compare(brows.get(r["row"]), r)})
        cpus.append({"cpu_model": b["cpu_model"], "cpu_short": cpu_short(b["cpu_model"]), "jobs": b["jobs"], "runs": b["runs"],
                     "base_jobs": bb["jobs"] if bb else 0, "enough": b["jobs"] >= minimum, "rows": rows})
    builds = []
    for prog, m in sorted(pgo["pgo_context"].items()):
        n, f = m.get("none"), m.get("fast")
        if not n or not f:
            continue
        nl = {x["location"]: x["vectorized"] for x in n["census_lost_locations"]}
        fl = {x["location"]: x["vectorized"] for x in f["census_lost_locations"]}
        builds.append({"program": prog, "traps_none": n["traps"]["pgo"], "traps_fast": f["traps"]["pgo"], "locations": len(nl),
                       "vectorized_none": sum(1 for k in nl if nl[k] > 0), "vectorized_fast": sum(1 for k in nl if fl.get(k, 0) > 0)})
    return {"source": PGO_POOLED, "source_sha256": sha(path), "baseline": RW_POOLED, "report": PGO_REPORT, "plan": "pgo/PLAN.md",
            "runs": pgo["runs"], "minimum_jobs": minimum, "jobs": len(pgo["inputs"]), "cpus": cpus, "builds": builds,
            "rows_built": len(PGO_NAMES), "programs_built": len(builds)}


# ---------------------------------------------------------------- compile-only sweep (ce-sweep/)
CE_SWEEP = "ce-sweep/results.json"
CE_TARGETS = {"x86-64": "x86-64 (SSE2)", "x86-64-v3": "x86-64-v3 (AVX2)", "aarch64": "AArch64 (armv8-a)"}


def ce_remark(side, family):
    """One short remark per cell side: the compiler's own reason, without the -R flag tag."""
    rs = [re.sub(r"\s*\[-R[^\]]*\]$", "", x) for x in side.get("remarks") or []]
    if family == "gcc":
        return rs[0] if rs else "no vectorization remark (GCC reports only the loops it vectorizes)"
    why = [x for x in rs if x.startswith("loop not vectorized:")] or [x for x in rs if "vectorized loop" in x] or rs
    return why[0] if why else ""


def ce_sweep_data():
    """A thin copy of ce-sweep/results.json: per row (compiler, target, opt) the state of each loop and one remark."""
    path = os.path.join(REPO, CE_SWEEP)
    d = load(path)
    cells = {(c["compiler_id"], c["target"], c["opt"], c["kernel"]): c for c in d["cells"]}
    kernels = sorted({c["kernel"] for c in d["cells"]})
    rows = []
    for m in d["matrix"]:
        st, rem = {}, {}
        for k in kernels:
            c = cells[(m["compiler_id"], m["target"], m["opt"], k)]
            vn, vh = bool(c["none"]["vectorized"]), bool(c["hardened"]["vectorized"])
            st[k] = {"none": vn, "checked": vh}
            rem[k] = ce_remark(c["hardened"], m["family"])
        major = 0 if m["version"] == "trunk" else int(m["version"].split(".")[0])
        rows.append({"family": m["family"], "version": m["version"], "major": major, "compiler_id": m["compiler_id"], "target": m["target"],
                     "opt": m["opt"], "macro": m["macro_hardened"], "lost": sorted(m["lost"]), "vec": st, "remark": rem,
                     "macro_effective": bool(m["macro_effective"])})
    links = {k: v["url"] for k, v in d["permalinks_clang18_fast"].items() if v.get("verified")}
    cl = [r for r in rows if r["family"] == "clang"]
    gc = [r for r in rows if r["family"] == "gcc"]
    o3 = [r for r in gc if r["opt"] == "-O3"]
    summary = {"clang_rows": len(cl), "gcc_rows": len(gc), "gcc_o3_rows": len(o3),
               "clang_rev_s2_lost": sum(1 for r in cl if {"k04_rev", "k05_stride2"} <= set(r["lost"])),
               "clang_fwd_lost": sum(1 for r in cl if set(r["lost"]) & {"k01_sum_fwd", "k02_add_fwd", "k03_stencil"}),
               "gcc_o2_lost": sum(len(r["lost"]) for r in gc if r["opt"] == "-O2"),
               "gcc_o3_lost": {k: sum(1 for r in o3 if k in r["lost"]) for k in kernels},
               "majors": sorted({r["major"] for r in rows if r["major"]})}
    return {"source": CE_SWEEP, "source_sha256": sha(path), "counts": d["counts"], "control": d["control"],
            "targets": CE_TARGETS, "kernels": kernels, "rows": rows, "links": links, "summary": summary,
            "note": "compile-only: which loops lose vectorization, not what they cost; clang N is paired with the libc++ Compiler Explorer provides (assumed to be libc++ N)"}


# ---------------------------------------------------------------- newer toolchains (versions/) and environment (environment/)
VERSIONS_GLOB = "versions/results/*/versions-analysis/analysis.json"  # checked by versions/check.py
ENVIRONMENT_GLOB = "environment/results/*/analysis.json"  # checked by environment/check.py
VERSIONS_KERNELS = {"k01_sum_fwd": "forward sum", "k02_add_fwd": "forward add", "k03_stencil": "stencil", "k04_rev": "reverse",
                    "k05_stride2": "stride-2", "k06_gather": "gather", "k07_hist": "histogram", "k08_matmul": "matrix multiply"}
VERSIONS_JUDGED = ("k04_rev", "k05_stride2", "k08_matmul")


def _ver3(text):
    m = re.search(r"\d+\.\d+\.\d+", text or "")
    return m.group(0) if m else None


def _join_and(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def _kernel_names(cell_ids):
    ks = []
    for c in cell_ids:
        k = c.split(".")[0]
        if k not in ks:
            ks.append(k)
    return [VERSIONS_KERNELS.get(k, k) for k in ks]


def _why_inconclusive(b, jobs, min_jobs):
    """Plain words for why a CPU model on a toolchain is INCONCLUSIVE, from the analysis's own fields."""
    if b["form"] != "INCONCLUSIVE":
        return None
    if jobs < min_jobs:
        return f"too few jobs ({jobs}; a verdict needs {min_jobs})"
    failed = [f["cell_id"] for f in b["forward"] if not f["passes"]]
    if failed:
        return f"the forward-loop rule is missed by {_join_and(_kernel_names(failed))}"
    return "the pooled verdict is inconclusive (" + "; ".join(b["inconclusive_because"]) + ")"


def versions_data(min_jobs):
    """versions/results/<run>/versions-analysis/analysis.json (versions/analyze.py over the pooled files,
    rules in versions/PLAN.md written before the run), reduced to what the page prints. Nothing is recomputed."""
    paths = sorted(glob.glob(os.path.join(REPO, VERSIONS_GLOB)))
    if not paths:
        return {"toolchains": [], "source": None}
    path = paths[-1]
    d = load(path)
    adir = os.path.dirname(path)
    run_id = os.path.basename(os.path.dirname(adir))
    job_docs = sorted(glob.glob(os.path.join(os.path.dirname(adir), "versions-*", "results.json")))
    run_url = load(job_docs[0])["run"]["workflow_run_url"] if job_docs else None
    nums = d["numbers_from_criteria_v3"]
    tcs = []
    for ver, v in sorted(d["versions"].items(), key=lambda kv: int(kv[0])):
        tc = v["toolchain"]
        vec = tc["vectorization"]
        cpus = []
        for model, b in v["cpus"].items():
            cells = []
            for c in b["cells"]:
                kern, size = c["cell_id"].split(".")
                vs = b["vs_clang18"].get(c["cell_id"]) if b.get("in_clang18_pool") else None
                cells.append({"cell_id": c["cell_id"], "kernel": kern, "name": VERSIONS_KERNELS[kern], "size": size, "class": c["class"],
                              "ratio": c["as_compiled"], "lo": c["as_compiled_ci95"][0], "hi": c["as_compiled_ci95"][1],
                              "aligned": c["aligned"], "aligned_lo": c["aligned_ci95"][0], "aligned_hi": c["aligned_ci95"][1],
                              "clang18": vs["clang18"] if vs else None, "class18": vs["class_clang18"] if vs else None,
                              "over18": vs["this_over_clang18"] if vs else None})
            cpus.append({"cpu_model": model, "cpu_short": cpu_short(model), "jobs": b["jobs"], "runs": b["runs"],
                         "enough": b["jobs"] >= min_jobs, "form": b["form"], "why": _why_inconclusive(b, b["jobs"], min_jobs),
                         "aa_half_width_pct": b["aa_half_width_pct"], "n_hold": b["n_hold"],
                         "kernels": [{"kernel": k, "name": VERSIONS_KERNELS[k], "holds": b["kernels"][k]["holds"], "reason": b["kernels"][k]["reason"]}
                                     for k in VERSIONS_JUDGED],
                         "forward": [{"kernel": f["cell_id"].split(".")[0], "name": VERSIONS_KERNELS[f["cell_id"].split(".")[0]],
                                      "size": f["cell_id"].split(".")[1], "aligned": f["aligned"], "ci_hi": f["aligned_ci95"][1],
                                      "limit": f["limit"], "passes": f["passes"]} for f in b["forward"]],
                         "in_clang18_pool": b["in_clang18_pool"], "cells": cells})
        cpus.sort(key=lambda c: (-c["jobs"], c["cpu_short"]))
        lost_in_fast = [k for k, x in vec.items() if x["none"]["vectorized"] and not x["fast"]["vectorized"]]
        tcs.append({"version": int(ver), "clang": _ver3(tc["clang"]), "libcxx": _ver3(tc["packages"].get(f"libc++-{ver}-dev")),
                    "compiler": tc["compiler"], "form": v["form"], "probe_traps": bool(tc["probe"]["fast_traps"]),
                    "probe_clean": bool(tc["probe"]["none_runs_clean"]),
                    "lost_by_remarks": [VERSIONS_KERNELS[k] for k in lost_in_fast],
                    "matmul_vectorized_both": bool(vec["k08_matmul"]["none"]["vectorized"] and vec["k08_matmul"]["fast"]["vectorized"]),
                    "jobs": sum(c["jobs"] for c in cpus), "cpus": cpus})
    rows = [(t, c, x) for t in tcs for c in t["cpus"] for x in c["cells"]]

    def span(kernel, size, pred=lambda t, c: True):
        vs = [x["ratio"] for t, c, x in rows if x["kernel"] == kernel and x["size"] == size and pred(t, c)]
        return {"min": min(vs), "max": max(vs)} if vs else None
    main = lambda t, c: c["enough"]  # noqa: E731
    judged = lambda k: [kk["holds"] for t in tcs for c in t["cpus"] for kk in c["kernels"] if kk["kernel"] == k]  # noqa: E731
    summary = {"toolchains": len(tcs), "jobs": sum(t["jobs"] for t in tcs), "cpu_models": len({c["cpu_model"] for t in tcs for c in t["cpus"]}),
               "enough": [{"version": t["version"], "cpu_short": c["cpu_short"], "jobs": c["jobs"]} for t in tcs for c in t["cpus"] if c["enough"]],
               "reverse_all": minmax([x["ratio"] for t, c, x in rows if x["kernel"] == "k04_rev"]),
               "stride2_all": minmax([x["ratio"] for t, c, x in rows if x["kernel"] == "k05_stride2"]),
               "reverse_holds_all": all(judged("k04_rev")), "stride2_holds_all": all(judged("k05_stride2")),
               "matmul_holds_any": any(judged("k08_matmul")),
               "matmul_vectorized_both_all": all(t["matmul_vectorized_both"] for t in tcs),
               "matmul": {s: span("k08_matmul", s) for s in ("L1", "L2")},
               "matmul_main": {s: span("k08_matmul", s, main) for s in ("L1", "L2")},
               "reverse_main": {s: span("k04_rev", s, main) for s in ("L1", "L2")},
               "stride2_main": {s: span("k05_stride2", s, main) for s in ("L1", "L2")},
               "sum_all": minmax([x["ratio"] for t, c, x in rows if x["kernel"] == "k01_sum_fwd"]),
               "forms": sorted({t["form"] for t in tcs}), "all_probes_trap": all(t["probe_traps"] and t["probe_clean"] for t in tcs),
               "matmul_clang18": minmax([x["clang18"] for t, c, x in rows if x["kernel"] == "k08_matmul" and x["clang18"] is not None])}
    return {"source": rel(path), "source_sha256": sha(path), "run_id": run_id, "workflow_run_url": run_url,
            "report": rel(os.path.join(adir, "report.txt")), "plan": "versions/PLAN.md", "criteria": "versions/criteria.json",
            "forward_limit_floor": nums["fwd_floor"] * 100, "forward_point_max": nums["fwd_point"], "lost_lo": nums["lost_lo"],
            "aa_max": nums["aa_max"], "min_jobs": nums["min_jobs"], "toolchains": tcs, "summary": summary}


def environment_data():
    """environment/results/<run>/analysis.json (environment/analyze.py, rules in environment/PLAN.md written before the
    run), reduced to what the page prints: per CPU model and job, steal, reported frequency, topology, and whether
    leaving out steal-affected processes moves any cell."""
    paths = sorted(glob.glob(os.path.join(REPO, ENVIRONMENT_GLOB)))
    if not paths:
        return {"models": [], "source": None}
    path = paths[-1]
    d = load(path)
    run_id = os.path.basename(os.path.dirname(path))
    models, jobs_all = [], []
    for m in d["models"]:
        jobs = []
        for j in m["jobs"]:
            mh = j["mhz"]
            jobs.append({"job": j["job"], "processes": j["n_processes"], "steal_share_pct": j["steal_share"] * 100,
                         "processes_with_steal": j["processes_with_steal"], "mhz_median": mh["median"], "mhz_constant": mh["constant"],
                         "half_drift_pct": abs(mh["half_drift_pct"]), "side_drift_pct": abs(mh["side_drift_pct"]),
                         "shares_core": j["topology"]["shares_core_with_driver"], "driver_on_pinned": j["topology"]["driver_on_pinned_vcpu"],
                         "online": j["online"], "cgroup_cpu_max": j["cgroup_cpu_max_present"], "governor": j["governor"],
                         "kernel": j["kernel"], "large": j["job_large"]})
        jobs_all += jobs
        models.append({"cpu_model": m["cpu_model"], "cpu_short": cpu_short(m["cpu_model"]), "n_jobs": m["n_jobs"],
                       "steal_share_median_pct": m["steal_share_median"] * 100, "steal_share_max_pct": m["steal_share_max"] * 100,
                       "jobs_steal_large": m["jobs_steal_large"], "jobs_drift_large": m["jobs_drift_large"],
                       "half_drift_median_pct": m["half_drift_abs_pct_median"], "half_drift_max_pct": m["half_drift_abs_pct_max"],
                       "side_drift_median_pct": m["side_drift_abs_pct_median"], "side_drift_max_pct": m["side_drift_abs_pct_max"],
                       "jobs_sharing_core": m["jobs_sharing_core_with_driver"], "jobs_driver_on_pinned": m["jobs_driver_on_pinned_vcpu"],
                       "jobs_cgroup": m["jobs_with_cgroup_cpu_max"], "mhz_sources": m["mhz_sources"],
                       "cells": len(m["cells"]), "excluded_processes": sum(c["excluded"] for c in m["cells"]),
                       "cells_moved": len(m["cells_moved"]), "large_jobs": len(m["large_jobs"]), "jobs": jobs})
    th = d["thresholds"]
    docs = [load(os.path.join(os.path.dirname(path), j["path"])) for m in d["models"] for j in m["jobs"]]
    ticks = sorted(s["total"] for x in docs for s in x["samples"])
    summary = {"reps_per_side": docs[0]["facts"]["reps_per_side"], "process_ticks_median": ticks[len(ticks) // 2],
               "process_ms_median": ticks[len(ticks) // 2] * 10, "jobs": len(jobs_all), "cpu_models": len(models),
               "steal_max_pct": max(m["steal_share_max_pct"] for m in models),
               "half_drift_max_pct": max(m["half_drift_max_pct"] for m in models),
               "side_drift_max_pct": max(m["side_drift_max_pct"] for m in models),
               "jobs_sharing_core": sum(m["jobs_sharing_core"] for m in models),
               "jobs_driver_on_pinned": sum(m["jobs_driver_on_pinned"] for m in models),
               "jobs_cgroup": sum(m["jobs_cgroup"] for m in models),
               "processes": sum(j["processes"] for j in jobs_all), "processes_with_steal": sum(j["processes_with_steal"] for j in jobs_all),
               "excluded_processes": sum(m["excluded_processes"] for m in models), "cells_moved": sum(m["cells_moved"] for m in models),
               "large_jobs": sum(m["large_jobs"] for m in models), "mhz_constant_jobs": sum(1 for j in jobs_all if j["mhz_constant"]),
               "governor_files": sum(1 for j in jobs_all if j["governor"]), "online": sorted({j["online"] for j in jobs_all}),
               "kernels": sorted({j["kernel"] for j in jobs_all}), "page_text_may_change": bool(d["page_text_may_change"])}
    return {"source": rel(path), "source_sha256": sha(path), "run_id": run_id, "report": rel(os.path.join(os.path.dirname(path), "report.txt")),
            "plan": d["plan"], "steal_large_pct": th["steal_large_share"] * 100, "drift_large_pct": th["drift_large_pct"],
            "min_left_per_side": th["min_left_per_side"], "models": models, "summary": summary}


def tree(root):
    out = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = sha(p)
    return out


# ---- the first screen's key numbers, baked into site/index.html (a no-JS view or a link preview shows
# real numbers). app.js overwrites the same spans at run time with the same formatting; check_site.py
# compares the two.
INDEX_HTML = os.path.join(REPO, "site", "index.html")


def _fx(v):
    return f"{v:.1f}" if v >= 2 else f"{v:.2f}"


def baked_values(data_dir):
    def load(n):
        with open(os.path.join(data_dir, n), encoding="utf-8") as f:
            return json.load(f)
    ix, co, mi, si, rw, ce = (load(n) for n in ("index.json", "corpus.json", "mitigate.json", "siblings.json", "realworld.json", "cesweep.json"))
    ver = lambda t: (re.search(r"\d+\.\d+\.\d+", t or "") or [""])[0]
    fix = [next(v for v in sh["variants"] if v["variant"] == sh["recommended"])["range"]
           for sh in mi["shapes"] if sh["kernel"] in ("m04_rev", "m08_matmul")]
    row = next(r for r in si["rows"] if r["variant"] == "clang18v3-fast")
    hits = [v["L1"]["max"] for m, v in row["cells"]["k02_add_fwd"]["per_cpu"].items() if m.startswith("EPYC")]
    t1, t2 = co["census1"]["totals"], co["census2"]["totals"]
    tc = ix["toolchain"]
    # the hero's default view (reverse loop, default CPU model, aligned build, smallest size): the same cell
    # site/race.js prints at run time, so a no-JS view or a link preview shows the measured ratio, not a range
    dcpu = next(c for c in ix["cpus"] if c["slug"] == ix["default_cpu"])
    pooled = load("pooled.json")
    pc = next(c for c in pooled["cpus"] if c["cpu_model"] == dcpu["cpu_model"])
    hc = next(c for c in pc["cells"] if c["cell_id"] == "k04_rev.L1")
    hcol = hc.get("aligned") or hc["as_compiled"]
    # the contrast band's default view: the worst loop (largest pooled ratio at the smallest size) of the default CPU model
    short = {"k01_sum_fwd": "forward sum", "k02_add_fwd": "forward add", "k03_stencil": "stencil", "k04_rev": "reverse",
             "k05_stride2": "stride-2", "k06_gather": "gather", "k07_hist": "histogram", "k08_matmul": "matrix multiply"}
    worst = max(((c["cell_id"].split(".")[0], (c.get("aligned") or c["as_compiled"])["ratio"])
                 for c in pc["cells"] if c["cell_id"].endswith(".L1") and (c.get("aligned") or c.get("as_compiled"))),
                key=lambda t: t[1])
    hwhat = {"lost": "The compiler could not vectorize it once the check was inside: it no longer knows how many times the loop runs, so four at a time becomes one at a time.",
             "kept": "The loop keeps SIMD; the check only rides on the leftover tail.",
             }.get(hc["class"], "No SIMD in either build; the check adds work to every element.")
    return {
        "heroRatio": _fx(hcol["ratio"]), "heroCpu": dcpu["cpu_short"], "heroJobs": str(hcol["jobs"]), "heroWhat": hwhat,
        "bandWorst": _fx(worst[1]), "bandName": short.get(worst[0], worst[0]),
        "googlePct": f"{ix['claim']['google_pct']:.2f}",
        "lostMin": f"{ix['page']['lost']['min']:.1f}", "lostMax": f"{ix['page']['lost']['max']:.1f}",
        "clang": f"clang {ver(tc.get('clang'))}", "libcxx": f"libc++ {ver(tc.get('libcxx_package'))}",
        "c1Lost": f"{t1['lost']:,}", "c1Vec": f"{t1['none']['vectorized']:,}",
        "c2Lost": f"{t2['lost']:,}", "c2Vec": f"{t2['none']['vectorized']:,}",
        "fixMin": _fx(min(r["min"] for r in fix)), "fixMax": _fx(max(r["max"] for r in fix)),
        "rwSlowMin": f"{(rw['timing']['slow_min'] - 1) * 100:.1f}", "rwSlowMax": f"{(rw['timing']['slow_max'] - 1) * 100:.1f}",
        "avx2Short": _fx(max(hits)), "ceCompilers": str(ce["counts"]["compilers"]),
    }


def bake_html(data_dir, write):
    """Fill the baked spans of site/index.html; returns the keys whose text differs from the data."""
    vals = baked_values(data_dir)
    with open(INDEX_HTML, encoding="utf-8", newline="") as f:
        html = f.read()
    stale = []

    def sub(m):
        k = m.group(2)
        if k in vals and m.group(3) != vals[k]:
            stale.append(k)
            return m.group(1) + vals[k] + m.group(4)
        return m.group(0)
    new = re.sub(r'(<span data-v="([A-Za-z0-9]+)"[^>]*>)([^<]*)(</span>)', sub, html)
    if write and new != html:
        with open(INDEX_HTML, "w", encoding="utf-8", newline="") as f:
            f.write(new)
    return sorted(set(stale))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if site/data/ differs from a fresh build")
    a = ap.parse_args()
    if a.check:
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            want, have = tree(tmp), tree(OUT) if os.path.isdir(OUT) else {}
        bad = sorted(set(want) ^ set(have)) + sorted(k for k in want if k in have and want[k] != have[k])
        if bad:
            print(f"site/data/ differs from a fresh build in {len(bad)} files, e.g. {bad[:5]}; "
                  f"run python scripts/build_site_data.py")
            return 1
        stale = bake_html(OUT, False)
        if stale:
            print(f"site/index.html bakes stale numbers for {stale}; run python scripts/build_site_data.py")
            return 1
        print(f"site/data/ equals a fresh build ({len(want)} files)")
        return 0
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    idx = build(OUT)
    bake_html(OUT, True)
    print(f"wrote site/data/: pooled.json ({idx['pooled']['jobs']} jobs, {len(idx['pooled']['runs'])} runs), "
          f"{len(idx['cpus'])} CPU models ({idx['page']['cpus_enough']} with enough jobs), mitigate, siblings, corpus")
    return 0


if __name__ == "__main__":
    sys.exit(main())
