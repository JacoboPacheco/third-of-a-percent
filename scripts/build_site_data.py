#!/usr/bin/env python3
"""Writes site/data/, the one committed copy of the results the page reads.

    python scripts/build_site_data.py           write site/data/ from results/ and the study folders
    python scripts/build_site_data.py --check   rebuild in memory and fail if site/data/ differs

Copied unchanged:
  pooled.json        results/s7-pooled/pooled.json (criteria-v3: every job of a CPU model pooled across
                     jobs and runs, two-level bootstrap intervals, both columns, instruction counts;
                     the jobs of results/s4-pooled plus those of the later runs of the same workflow;
                     results/s6-pooled is the 75-job intermediate pool, kept; only its size is read here,
                     for index.json pooled.steps)
  asm/<cpu>/         for each CPU model with enough jobs, the machine code of ONE of its jobs (the
                     none, fast, none_a64 and fast_a64 listings; the binaries are byte-identical across
                     jobs, which the pooled build control checks), plus builds.json extracted from that
                     job's details.json (commands, remarks, traps)
Derived, never invented (every number is computed here from the files named, and --check recomputes it):
  index.json         what the first screen and the prose print: per-CPU summaries of pooled.json, the
                     whole-program rows of the S3 runs (S4 did not time programs), the day-one record
                     and the criteria files' own 'written' lines; `provenance`: per group of runs the
                     commits and rule-file hashes their records stamp, which of those commits and run links
                     the public repository can show (a few facts read from the GitHub API on a stated date,
                     kept as constants), and the order-of-events times the page states
  mitigate.json      mitigate/ results: per loop shape and rewrite, the aligned ratio range per CPU
                     model (cells over the 2% A/A limit left out, as mitigate/README.md does), the
                     safety test, the code of each variant copied from mitigate/src/
  siblings.json      siblings/summary.json reduced to toolchain x loop: lost or not, ratio ranges
  corpus.json        the two censuses: per category, per project, shapes, controls, example loops
  fixture/pooled.json  results/fixture.json (SAMPLE, made up) in the pooled shape, for ?data=fixture
  arm64.json         the Arm column (arm64/PLAN.md): results/s8-arm-pooled/pooled.json (one CPU model, an AArch64
                     runner) and the per-job files of results/s8-arm-run-*: cells, verdict, controls, the
                     compiler remarks, check traps and NEON instruction counts of each kernel, and a short
                     x86-64 comparison read from the pool above. Additive: nothing else in this folder reads it
                     or changes because of it (tests/test_arm64_data.py builds without it and compares)
  replication.json   the replication (replication/PLAN.md): replication/results.json, which replication/compare.py
                     derives from the six pooled files of the earlier pools, the new sets B and C and the two
                     secondary pools, reduced to what the page prints: one row per CPU model (verdict words,
                     jobs, the share of points inside the earlier interval, the cause cell of a verdict that is not
                     MAP), the cells behind each flip, the Arm cell, the lost-SIMD range, the models not testable.
                     Additive: it reads none of the files above and changes none of them, except the sections entry
                     of index.json (tests/test_replication.py builds without it and compares)
  dsweep.json        the matrix-multiply d-sweep (dsweep/PLAN.md): results/s10-dsweep-pooled/dsweep-pooled.json, which
                     dsweep/analyze.py writes from the per-job dsweep.json files, reduced to what the page prints: for each
                     CPU model with at least the minimum number of jobs the word the pre-registered rule gave (and the
                     word of each column), the fixed share with its interval, the A/A, the d ladder and one row per d
                     (ratios and intervals in both columns, the excess in ns per inner call, the extra instructions, the
                     placement flag); for the models below the minimum their job counts. Additive in the same way as
                     replication.json (tests/test_dsweep_results.py builds without it and compares)
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

POOLED = "results/s7-pooled/pooled.json"
# The first pooled measurement (3 runs, 30 jobs). The holdout (results/s5-holdout) was judged against this file,
# so the holdout comparison keeps reading it; everything else on the page reads POOLED.
POOLED_ORIGINAL = "results/s4-pooled/pooled.json"
# The 75-job intermediate pool (ten more runs than the original three). Kept; read here only for the sizes of the pools in the history
# of the pool's growth (index.json pooled.steps).
POOLED_S6 = "results/s6-pooled/pooled.json"
# The CPU model the first screen opens on (the race, the figure, the README image). It was the model with the most
# jobs when the page was built, and it stays the opening view so that more jobs of another model do not move it;
# if it is absent or has too few jobs, the model with the most jobs opens instead.
DEFAULT_CPU_MODEL = "AMD EPYC 7763 64-Core Processor"
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
# The public repository's address. File links on the page point into it. Workflow-run addresses in the
# results files use a different base than REPO_BASE and are not reachable by readers, so they are dropped from
# site/data.
REPO_BASE = "https://github.com/JacoboPacheco/third-of-a-percent"
REPO_INFO = {
    "base": REPO_BASE,
    "measure_command": "gh workflow run measure.yml",
    "check_command": "python scripts/check.py",
}


# Related work: only sources that the related-work table in gaps/GAPS.md records as actually read, with its wording.
# Every claim about a source is "as reported"; the search-summary-only items are titles, with no claim.
RELATED = {
    "gaps_file": "gaps/GAPS.md",
    "summary": (
        "Google’s post reports an average 0.30% performance impact across its services, and says profile-guided "
        "optimization (PGO) improved performance further. Its 2025 sequel in ACM Queue, as reported (read in a browser; "
        "scripted fetches get HTTP 403, so unconfirmed from a copy), calls PGO critical. The closest per-benchmark "
        "study, NADER (OOPSLA 2021, on Rust), reports little, no or negative cost from unchecked indexing in 76.4% "
        "of benchmarks, and NIST (2013) vector.at(i) 0.881% slower than a C array on sequential writes. As reported, link order and "
        "environment size can reverse a measured speedup (Mytkowicz et al., 2009), hence the aligned build and the "
        "layout A/A here."
    ),
    "none_found": (
        "This search found no public per-loop measurement of libc++’s FAST mode (sources searched: the LLVM "
        "documentation, the LLVM Discourse, GitHub issues, Phoronix, Chromium’s spanification commits and the "
        "Microsoft STL hardening documentation); finding none is not the same as none existing."
    ),
    "main_rows": ["google", "queue", "nader", "nist", "readyset"],
    "sources": [
        {"id": "google", "m_short": "An average 0.30% across Google’s services; PGO further improved performance", "d_short": "A fleet average; no loop shapes or machine code", "name": "Google Security Blog, Nov 15 2024", "short": "Google’s post (2024)",
         "url": "https://security.googleblog.com/2024/11/retrofitting-spatial-safety-to-hundreds.html",
         "measured": "As reported: an average 0.30% performance impact across Google’s services; fixing one unnecessary check took the overhead from 0.35% to 0.3%; PGO further improved performance, though the overhead remains minimal even without such techniques; a handful of performance-critical code paths still use explicitly unsafe accesses.",
         "differs": "A fleet average on production workloads; the post does not say whether the 0.30% includes PGO, a toolchain version or a hardening mode; no per-loop breakdown, machine code or controls a stranger can rerun. This study tests none of its numbers."},
        {"id": "queue", "m_short": "PGO critical; five services opted out; the unsafe-access API used in seven places", "d_short": "The same fleet; PGO tested here only with the timed input as training", "name": "Dionne, Rebert, Shavrick, Varlamov, “Practical Security in Production: Hardening the C++ Standard Library at Massive Scale”, ACM Queue 23(5), 2025", "short": "ACM Queue sequel (2025)",
         "url": "https://queue.acm.org/detail.cfm?id=3773097",
         "measured": "As reported, read in a browser (its address returned HTTP 403 to a scripted fetch when re-checked, so the figures are not confirmed from a saved copy): key services were benchmarked; PGO was critical, letting the compiler move checks out of hot paths; only five services opted out entirely; the fine-grained unsafe-access API was used in just seven distinct places; a non-verbose mode cut the binary-size cost from 2% to under 0.5%.",
         "differs": "The same fleet, with its method; no loop shapes. This study’s one PGO test (training input equal to the timed input, one CPU model) did not make the cost vanish in most rows; its census (the expensive shape is rare in general code) is consistent with few unsafe sites, a link not tested here."},
        {"id": "carruth", "name": "Chandler Carruth, “Story-time: C++, bounds checking, performance, and compilers”, Nov 2024", "short": "Carruth (2024)",
         "url": "https://chandlerc.blog/posts/2024/11/story-time-bounds-checking/",
         "measured": "An expert account, not a measurement. As reported: credits LLVM’s check optimization and PGO; says without PGO the overhead would not be tolerable for most performance-sensitive workloads; warns that benchmarks of pervasive patterns skew toward confirmation bias.",
         "differs": "This study’s PGO column trains on the timed input, so it tests his PGO point only in part (it did not make the cost vanish in most rows on one CPU model); its loops are the cases where the check stays inside the loop."},
        {"id": "nader", "m_short": "76.4% of benchmarks of top Rust crates pay little, nothing or less", "d_short": "Rust; layout not controlled, here it is", "name": "Popescu, Xu, Apostolakis, August, Levy, “Safer at Any Speed” (NADER), OOPSLA 2021", "short": "NADER, OOPSLA 2021 (Rust)",
         "url": "https://www.cs.princeton.edu/~npopescu/papers/nader.pdf",
         "measured": "As reported: 76.4% of benchmarks of top Rust crates show little, no or negative cost from unchecked indexing; 23.6% are more than 1% slower with checks and 11.8% more than 1% faster; brotli’s overhead 7.7%, 6.5% on an older rustc, 2.5% on Apple M1; about 200 benchmarks with 95% intervals.",
         "differs": "Rust, many real benchmarks, several machines. As reported, it attributes checks-make-it-faster results to code layout and inlining heuristics without controlling layout; this study controls layout on eight C++ loops."},
        {"id": "nist", "m_short": "vector.at(i) 0.881% slower on sequential writes (GCC 4.6.2, a PC with two Xeon X5450 CPUs)", "d_short": "One forward shape; vectorization not analysed", "name": "Flater and Guthrie (NIST), “A Case Study of Performance Degradation Attributable to Run-Time Bounds Checks on C++ Vector Access”, J. Res. NIST 118, 2013", "short": "NIST (2013)",
         "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4487316/",
         "measured": "As reported: GCC 4.6.2 on a PC with two Xeon X5450 CPUs (a Dell Precision T5400) under Linux, with Turbo Boost unsupported, frequency scaling left out of the kernel and SpeedStep off, 63 runs per cell; vector.at(i) 0.881% (±0.009) slower than a C array at -O3; sequential write loops only; vectorization not analysed.",
         "differs": "A dedicated machine with frequency scaling off and a far tighter interval, but one forward shape and an old compiler. Forward loops cost little here too; the shapes that lose SIMD are what it did not test."},
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
    """Sets every workflow_run_url to None: the run addresses in the results files use a different base than REPO_BASE."""
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
    for f in files:  # git log in a shallow or re-created clone cannot reproduce the recorded commits: the stored value wins
        for k in ("added_commit", "last_commit", "added_at"):
            rec = stored.get(f["file"], {}).get(k)
            if rec is not None:
                f[k] = rec
    v1 = load(os.path.join(REPO, "harness", "criteria.json"))["verdict"]
    v1_rule = {"point_max": v1["forward_point_max_ratio"], "ci_floor_pct": v1["forward_ci_hi_floor_pct"],
               "aa_multiplier": v1["forward_ci_hi_aa_multiplier"]}
    return {"dayone": runs, "criteria_files": files, "v1_forward_rule": v1_rule}


def stored_holdout_time():
    """The time recorded in the committed site/data/holdout.json, if any: git log in a shallow or re-created clone cannot reproduce it."""
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


RAM_EARLY_GLOBS = ["results/s2-run-*/results.json", "results/s3-run-*/results-*/results.json", "results/s3-audit-run-*/results-*/results.json"]


def ram_early():
    """The RAM-sized cells: timed only in the early jobs (S2, S3 and the S3 audit), as compiled, never in the pooled runs. The reverse and stride-2
    loops' ranges, the reverse loop at the L2 size in the same jobs, how far jobs of one CPU model differ and how often two jobs of one model have
    intervals that do not overlap. Fails if a results file outside those runs holds a RAM cell, so a later run cannot be left out silently."""
    has_ram = lambda f: any(c.get("size_class") == "RAM" for c in load(f).get("cells", []))  # noqa: E731
    files = sorted(f for g in RAM_EARLY_GLOBS for f in glob.glob(os.path.join(REPO, g)) if has_ram(f))
    every = [f for pat in ("results/*/results.json", "results/*/*/results.json") for f in glob.glob(os.path.join(REPO, pat))]
    for f in every:
        if f not in files and "RAM" in open(f, encoding="utf-8").read() and has_ram(f):
            raise AssertionError(f"{rel(f)} holds RAM cells but is not among the early runs the page describes")
    jobs = []
    for f in files:
        doc = load(f)
        cells = {c["cell_id"]: c for c in doc["cells"]}
        assert all(c in cells for c in ("k04_rev.RAM", "k05_stride2.RAM", "k04_rev.L2")), rel(f)
        jobs.append({"cpu_short": cpu_short(doc["run"]["runner"]["cpu_model"]), "cells": cells})
    out = {"jobs": len(jobs), "cell": "as compiled", "rev": minmax([j["cells"]["k04_rev.RAM"]["ratio"] for j in jobs]),
           "stride2": minmax([j["cells"]["k05_stride2.RAM"]["ratio"] for j in jobs]), "rev_l2": minmax([j["cells"]["k04_rev.L2"]["ratio"] for j in jobs]),
           "pairs": {}, "spread": {}}
    for cid, key in (("k04_rev.RAM", "rev"), ("k05_stride2.RAM", "stride2")):
        dis = tot = 0
        best = None
        for m in sorted({j["cpu_short"] for j in jobs}):
            cs = [j["cells"][cid] for j in jobs if j["cpu_short"] == m]
            for i in range(len(cs)):
                for k in range(i + 1, len(cs)):
                    tot += 1
                    dis += cs[i]["ci95"][1] < cs[k]["ci95"][0] or cs[k]["ci95"][1] < cs[i]["ci95"][0]
            if len(cs) > 1:
                sp = (max(c["ratio"] for c in cs) / min(c["ratio"] for c in cs) - 1) * 100
                if best is None or sp > best["pct"]:
                    best = {"pct": sp, "cpu_short": m, "jobs": len(cs)}
        out["pairs"][key] = {"disjoint": int(dis), "total": tot}
        out["spread"][key] = best
    return out


def intel_forward(pooled):
    """The forward add at L1, aligned, in every Intel job of the S3 runs, the S4 smoke run and the pooled runs, one row per
    job (no verdict; the pooled Intel models are listed in cpus[] with their own pooled numbers)."""
    jobs = []
    files = glob.glob(os.path.join(REPO, "results", "s3-*", "results-intel-*", "results.json"))
    files += glob.glob(os.path.join(REPO, "results", "s4-smoke-*", "results-intel-*", "results.json"))
    for f in sorted(files):
        doc = load(f)
        c = next((q for q in doc["cells"] if q["cell_id"] == "k02_add_fwd.L1"), None)
        if c and c.get("aligned"):
            jobs.append({"source": rel(os.path.dirname(f)), "cpu_short": cpu_short(doc["run"]["runner"]["cpu_model"]),
                         "aligned": c["aligned"]["ratio"], "aa_pct": doc["controls"]["aa"]["half_width_pct"]})
    for i in pooled["inputs"]:  # one row per pooled Intel job, from that job's own file (the rows are jobs, not pools)
        if "INTEL" in i["cpu_model"].upper():
            f = os.path.normpath(os.path.join(REPO, os.path.dirname(POOLED), i["path"]))
            doc = load(f)
            c = next((q for q in doc["cells"] if q["cell_id"] == "k02_add_fwd.L1"), None)
            if c and c.get("aligned"):
                jobs.append({"source": rel(os.path.dirname(f)), "cpu_short": cpu_short(i["cpu_model"]),
                             "aligned": c["aligned"]["ratio"], "aa_pct": doc["controls"]["aa"]["half_width_pct"]})
    # The Intel jobs of replication set C (the second x86-64 set, Figure 8) are not among the rows above: they are counted
    # beside them so that the page can say what its count leaves out.
    set_c = []
    for f in sorted(glob.glob(os.path.join(REPO, "results", "s9-run-*", "results-*", "results.json"))):
        doc = load(f)
        if "INTEL" not in doc["run"]["runner"]["cpu_model"].upper():
            continue
        c = next((q for q in doc["cells"] if q["cell_id"] == "k02_add_fwd.L1"), None)
        if c and c.get("aligned"):
            set_c.append({"cpu_short": cpu_short(doc["run"]["runner"]["cpu_model"]), "aligned": c["aligned"]["ratio"]})
    return {"cell": "k02_add_fwd.L1", "jobs": jobs, "aligned": minmax([j["aligned"] for j in jobs]),
            "cpus": sorted({j["cpu_short"] for j in jobs}),
            "set_c": {"jobs": len(set_c), "aligned": minmax([j["aligned"] for j in set_c]),
                      "per_cpu": {m: sum(1 for j in set_c if j["cpu_short"] == m) for m in sorted({j["cpu_short"] for j in set_c})}}}


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


# ---- what the public repository can and cannot show about the order of events and the origin of the result records
# The scan of results/ below is derived. The facts here cannot be derived offline: they were read on PROVENANCE_READ
# from the public repository's GitHub API (compare/main...<commit>, actions/runs, the contents of dsweep/PLAN.md on the
# branch dsweep-smoke) and are a record of what was read, not a proof. A commit that the result records stamp and that
# is not listed here is not in the public repository. check_site.py compares the times with
# tests/data/s8_arm_timeline.json and tests/data/s9_s10_provenance.json.
PROVENANCE_READ = "2026-10-18"
PUBLIC_COMMITS = {"293b6b9": "main", "60f487d": "main", "32ab03c": "main", "6176991": "arm-smoke", "8c874ec": "dsweep-smoke"}
PUBLIC_FIRST_RUN_ID = 38556089577   # the earliest Actions run of the public repository: an earlier run id cannot be one of its runs
# the first commit of the public repository's history (read on PROVENANCE_READ; check_site.py compares it with tests/data/s9_s10_provenance.json
# and requires every record of the earlier groups to have started before it)
PUBLIC_HISTORY_FIRST = {"commit": "8674f5f", "utc": "2026-10-14T10:32:49Z"}
# the replication's plan: the author date (UTC) of the commit that added replication/PLAN.md, in the author's unpublished
# development history, and the creation time (public Actions record) of the first run it dispatched
REPLICATION_PLAN_COMMIT_UTC = "2026-10-17T07:14:52Z"
REPLICATION_FIRST_RUN = {"id": "39012918474", "created_utc": "2026-10-17T07:14:54Z"}
# creation times (public Actions record) of the three Arm runs of 16 October: how long after its creation a run's first record starts
DISPATCH_LAG_RUNS = {"38905055834": "2026-10-16T13:04:16Z", "38905081930": "2026-10-16T13:04:29Z", "38905108936": "2026-10-16T13:04:43Z"}
# the d-sweep plan on the public repository: the first commit of the branch dsweep-smoke that held dsweep/PLAN.md (together with
# the sweep code), its commit time, and that the plan file in it has the stored hash
DSWEEP_PUBLIC = {"branch": "dsweep-smoke", "commit": "f7f7d48", "commit_utc": "2026-10-17T08:44:06Z", "plan_sha256_equal": True}
PROVENANCE_GROUPS = [
    ("early", "s1 to s4 and the audit",
     ["results/s1-run-*/results.json", "results/s2-run-*/results.json", "results/s3-run-*/results-*/results.json",
      "results/s3-audit-run-*/results-*/results.json", "results/s4-run-*/results-*/results.json",
      "results/s4-smoke-*/results-*/results.json"]),
    ("holdout", "s5, the holdout", ["results/s5-holdout/runs/*/results-*/results.json"]),
    ("rewrite", "the rewrite runs", ["results/mitigate-run-*/mitigate-*/results.json"]),
    ("s6", "s6", ["results/s6-run-*/results-*/results.json"]),
    ("s7", "s7", ["results/s7-run-*/results-*/results.json"]),
    ("arm", "s8, the Arm runs", ["results/s8-arm-run-*/results-*/results.json"]),
    ("s9", "s9, the replication sets", ["results/s9-run-*/results-*/results.json", "results/s9-arm-run-*/results-*/results.json"]),
    ("dsweep", "s10, the d-sweep", ["results/s10-dsweep-run-*/dsweep-*/dsweep.json"]),
]


def _utc_seconds(s):
    import datetime
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()


def _record_starts(pattern):
    """{run id: earliest run.started_at} over the records that match the pattern."""
    out = {}
    for f in sorted(glob.glob(os.path.join(REPO, pattern))):
        r = load(f)["run"]
        out[str(r["id"])] = min(out.get(str(r["id"]), r["started_at"]), r["started_at"])
    return out


def provenance_data():
    """What the result records say about where they came from. Per group of runs: the number of records, the commits they
    stamp (and where the public repository holds each), how many carry the hash of the rule file now in the repository,
    how many run links can open (a link opens only for a run of this repository's Actions, whose ids start at
    PUBLIC_FIRST_RUN_ID). Plus the order-of-events facts the page states for the replication and the d-sweep plans."""
    crit_sha = sha(os.path.join(REPO, CRITERIA_FILE))
    groups, first_start = [], {}
    for gid, label, pats in PROVENANCE_GROUPS:
        files = sorted(f for p in pats for f in glob.glob(os.path.join(REPO, p)))
        commits, match, linked, opened, first = {}, 0, 0, 0, None
        for f in files:
            d = load(f)
            r = d["run"] if isinstance(d.get("run"), dict) else d
            c = (r.get("commit") or "")[:7]
            commits[c] = commits.get(c, 0) + 1
            match += (r.get("criteria_sha256") or d.get("criteria_sha256")) == crit_sha
            url = r.get("workflow_run_url") or r.get("url") or ""
            if url:
                linked += 1
                m = re.match(re.escape(REPO_BASE) + r"/actions/runs/(\d+)$", url)
                opened += bool(m) and int(m.group(1)) >= PUBLIC_FIRST_RUN_ID
            first = min(first, r["started_at"]) if first and r.get("started_at") else r.get("started_at") or first
        first_start[gid] = first
        groups.append({"id": gid, "label": label, "records": len(files),
                       "commits": [{"commit": c, "records": n, "where": PUBLIC_COMMITS.get(c)} for c, n in sorted(commits.items())],
                       "criteria_match": match, "links": {"records": linked, "open": opened}})
    empty = [g["id"] for g in groups if not g["records"]]
    assert not empty, f"no result records found for {empty}"
    arm_starts = _record_starts("results/s8-arm-run-*/results-*/results.json")
    assert set(arm_starts) == set(DISPATCH_LAG_RUNS), "the Arm runs changed: update DISPATCH_LAG_RUNS"
    lags = {rid: int(_utc_seconds(arm_starts[rid]) - _utc_seconds(t)) for rid, t in DISPATCH_LAG_RUNS.items()}
    rep_start = _record_starts("results/s9-arm-run-*/results-*/results.json")[REPLICATION_FIRST_RUN["id"]]
    return {
        "read_on": PROVENANCE_READ, "first_public_run_id": PUBLIC_FIRST_RUN_ID,
        "public_history": {"first_commit": PUBLIC_HISTORY_FIRST["commit"], "first_commit_utc": PUBLIC_HISTORY_FIRST["utc"]},
        "rule_file": {"file": CRITERIA_FILE, "sha256": crit_sha},
        "groups": groups,
        "replication": {
            "plan_commit_utc": REPLICATION_PLAN_COMMIT_UTC, "first_record_start_utc": first_start["s9"],
            "margin_s": int(_utc_seconds(first_start["s9"]) - _utc_seconds(REPLICATION_PLAN_COMMIT_UTC)),
            "first_run_created_utc": REPLICATION_FIRST_RUN["created_utc"],
            "first_run_lag_s": int(_utc_seconds(rep_start) - _utc_seconds(REPLICATION_FIRST_RUN["created_utc"])),
            "arm_run_lags_s": lags},
        "dsweep": {**DSWEEP_PUBLIC, "first_record_start_utc": first_start["dsweep"],
                   "gap_s": int(_utc_seconds(first_start["dsweep"]) - _utc_seconds(DSWEEP_PUBLIC["commit_utc"]))},
    }


# ---------------------------------------------------------------- build
def holdout_data(min_jobs):
    """The holdout run beside the original pooled runs: same rules, fresh draws (numbers read from both pooled.json)."""
    import statistics
    orig, hold = load(os.path.join(REPO, POOLED_ORIGINAL)), load(os.path.join(REPO, HOLDOUT))
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
    # what the holdout's own records show about the order: when its first job started (run.started_at, the clock of the
    # runner) and whether every job records the hash of the rule file now in the repository
    docs = [load(os.path.join(REPO, os.path.dirname(HOLDOUT), i["path"])) for i in hold["inputs"]]
    starts = sorted(d["run"]["started_at"] for d in docs)
    rule_sha = sha(os.path.join(REPO, CRITERIA_FILE))
    return {"source": HOLDOUT, "original_source": POOLED_ORIGINAL, "preregistration": HOLDOUT_PREREG,
            "result": "results/s5-holdout/RESULT.md",
            "preregistration_committed_utc": stored_holdout_time() or git_time(HOLDOUT_PREREG),
            "first_job_start_utc": starts[0],
            "jobs_with_rule_hash": sum(1 for d in docs if d["run"]["criteria_sha256"] == rule_sha), "rule_file": CRITERIA_FILE,
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
    # `original` marks the runs of the first pooled measurement (results/s4-pooled): "returned every job" is not the same
    # thing, since the two newest runs also returned all of theirs.
    original_runs = set(load(os.path.join(REPO, POOLED_ORIGINAL))["runs"])
    for rid in pooled["runs"]:
        url = run_urls.get(rid)
        if url is None:
            first = next(i for i in pooled["inputs"] if i["run_id"] == rid)
            url = load(os.path.normpath(os.path.join(REPO, os.path.dirname(POOLED), first["path"])))["run"]["workflow_run_url"]
        index["pooled"]["runs"].append({"run_id": rid, "workflow_run_url": url,
                                        "jobs": sum(1 for i in pooled["inputs"] if i["run_id"] == rid),
                                        "original": rid in original_runs})
    index["pooled"]["original"] = {"source": POOLED_ORIGINAL, "runs": len(original_runs),
                                   "jobs": sum(r["jobs"] for r in index["pooled"]["runs"] if r["original"])}
    # the sizes of the three pools in order (30, 75 and 95 jobs), each from its own pooled file: the kernel pool grew by further runs
    index["pooled"]["steps"] = [{"source": src, "runs": len(d["runs"]), "jobs": len(d["inputs"])}
                                for src, d in ((s, load(os.path.join(REPO, s))) for s in (POOLED_ORIGINAL, POOLED_S6, POOLED))]
    good = [c for c in index["cpus"] if c["enough"]]
    # The page-level ranges (the lost-loop range, the forward range) describe the CPU models whose pooled verdict
    # reached a form (map or holds-everywhere). A model with enough jobs and an inconclusive verdict is listed in
    # cpus[] with its own numbers but is not folded into these ranges, since its forward cells are the ones that
    # missed the written rule.
    judged = [c for c in good if c["form"] != "inconclusive"] or good
    # `forward` is the forward-loop range on the judged AMD models: the page and the README state it for the AMD models
    # and give the Intel forward add separately (intel_forward), because it costs clearly more there. An Intel model with
    # a MAP verdict (the Xeon 6973P-C in the 95-job pool) is in `judged_cpus` and so in `lost`, but its forward add at
    # L1 (placement-sensitive, left out of the verdict's forward test) would set the top of this range;
    # `forward_all_judged` keeps the range over every judged model.
    forward_cpus = [c for c in judged if c["cpu_model"].upper().startswith("AMD")] or judged

    def forward_range(cs):
        return {"aligned": minmax([v for c in cs for v in (c["forward_aligned"]["min"], c["forward_aligned"]["max"])]),
                "compiled": minmax([v for c in cs for v in (c["forward_compiled"]["min"], c["forward_compiled"]["max"])]),
                "compiled_max_cell": max((c["forward_compiled_max_cell"] for c in cs), key=lambda x: x["ratio"])}
    index["page"] = {
        "cpus_enough": len(good), "jobs_enough": sum(c["jobs"] for c in good),
        "cpus_few": [{"cpu_short": c["cpu_short"], "jobs": c["jobs"], "form": c["form"]} for c in index["cpus"] if not c["enough"]],
        "judged_cpus": [c["cpu_short"] for c in judged],
        "lost": minmax([v for c in judged for v in (c["lost"]["min"], c["lost"]["max"])]),
        "lost_instr": minmax([v for c in judged for v in (c["lost_instr"]["min"], c["lost_instr"]["max"])]),
        "forward_cpus": [c["cpu_short"] for c in forward_cpus],
        "forward": forward_range(forward_cpus),
        "forward_all_judged": forward_range(judged),
        "forms": sorted({c["form"] for c in good}),
    }
    index["page"]["lost_all_above_min"] = all(c["lost_ci_lo_min"] >= crit["verdict"]["lost_ci_lo_min_ratio"] for c in good)
    index["default_cpu"] = next((c for c in good if c["cpu_model"] == DEFAULT_CPU_MODEL),
                                max(good, key=lambda c: c["jobs"]))["slug"]
    index["method"] = method_record()
    index["programs"] = s3_programs()
    index["intel_forward"] = intel_forward(pooled)
    index["s1_forward"] = s1_forward()
    index["provenance"] = provenance_data()
    index["ram_early"] = ram_early()
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
    if os.path.exists(os.path.join(REPO, ARM_POOLED)):  # the Arm column: its own file, read from nothing above except the x86 numbers it sets beside
        dump(arm64_data(index, pooled), os.path.join(out_dir, "arm64.json"))
        index["sections"]["arm64"] = "data/arm64.json"
    if os.path.exists(os.path.join(REPO, REPLICATION)):  # the replication: its own file, read from replication/results.json only
        dump(replication_data(), os.path.join(out_dir, "replication.json"))
        index["sections"]["replication"] = "data/replication.json"
    if os.path.exists(os.path.join(REPO, DSWEEP_POOLED)):  # the d-sweep: its own file, read from the pooled d-sweep file only
        dump(dsweep_data(), os.path.join(out_dir, "dsweep.json"))
        index["sections"]["dsweep"] = "data/dsweep.json"
    fx =os.path.join(REPO, "results", "fixture.json")
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


# ---------------------------------------------------------------- the Arm column (arm64/, results/s8-arm-*)
ARM_POOLED = "results/s8-arm-pooled/pooled.json"
ARM_PLAN = "arm64/PLAN.md"
ARM_BUILDS = ("none", "fast", "novec", "none_a64", "fast_a64")
ARM_DIFFS = (("L1", "L1.diff"), ("L1_aligned", "L1.aligned.diff"), ("L2", "L2.diff"), ("L2_aligned", "L2.aligned.diff"))
# arm64/PLAN.md, "Written before the full results": the class each kernel was predicted to have under FAST on this runner
# ("lost" or "kept" SIMD), None where the plan wrote no prediction. tests/test_arm64_data.py checks the plan's own words.
ARM_PREDICTED = {"k01_sum_fwd": "kept", "k02_add_fwd": "kept", "k03_stencil": "kept", "k04_rev": "lost",
                 "k05_stride2": "lost", "k06_gather": None, "k07_hist": None, "k08_matmul": "kept"}
# the plan's "Forward loops (sum, add, stencil)"; the same section says "No placement effect is predicted" for them
ARM_FORWARD = ("k01_sum_fwd", "k02_add_fwd", "k03_stencil")


def _harness_module(name):
    """harness/<name>.py loaded by path (no change to sys.path): the Arm listings are read with the harness's own code."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("harness_" + name, os.path.join(REPO, "harness", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _lscpu_field(text, key):
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), text or "", re.M)
    return m.group(1).strip() if m else None


def _arm_stat(p, spread=False):
    """A pooled statistic as pooled.json stores it (ratio, 95% interval, half-width, jobs, between-job SD); with `spread`,
    also the smallest and largest of the per-job ratios it was pooled from (the 30 values stay in pooled.json)."""
    out = {k: p[k] for k in ("ratio", "ci95", "half_width_pct", "jobs", "between_job_sd_pct")}
    if spread:
        out["per_job_range"] = [min(p["per_job"]), max(p["per_job"])]
    return out


def _arm_listing(job_dir, name):
    with open(os.path.join(job_dir, "asm", name), encoding="utf-8") as f:
        return f.read().splitlines()


def _arm_simd_mnemonics(lines, hp):
    """The opcode sequence of the first (lowest-address) innermost loop with a NEON operand; None when the function has none."""
    insns = hp.instructions(lines)
    for lp in sorted(hp.hot(hp.loops(lines)), key=lambda x: int(x["start"], 16)):
        if lp["simd"]:
            lo, hi = int(lp["start"], 16), int(lp["end"], 16)
            return [t.split()[0] for a, t in insns if lo <= a < hi]
    return None


def _arm_build(job_dir, kernel, build, bd, hp, template):
    """One build of one kernel: the run's own record (traps, compiler remarks, loop count) and what the listing shows (NEON
    instructions). The compile command is the build's template with the kernel's id filled in; a kernel whose recorded command
    is not that carries its own in `command`."""
    insns = hp.instructions(_arm_listing(job_dir, f"{kernel}.{build}.s"))
    vec = bd.get("vectorization") or {}
    remarks = vec.get("remarks") or []
    interleave = None
    for r in remarks:
        m = re.search(r"interleaved count: (\d+)", r)
        if m:
            interleave = int(m.group(1))
            break
    why_not = next((re.sub(r"\s*\[-R[^\]]*\]$", "", r) for r in remarks if r.startswith("loop not vectorized:")), None)
    out = {"sha256": bd["sha256"], "traps": bd["traps"], "asm_lines": bd["asm_lines"],
           "neon_instructions": sum(1 for _, t in insns if hp._NEON.search(t)),
           "vectorized": vec.get("vectorized"), "width": vec.get("width"), "interleave": interleave,
           "remarks": remarks, "why_not_vectorized": why_not,
           "hot_loops": sum(1 for lp in bd["loops"] if lp["innermost"]),
           "hot_simd_loops": sum(1 for lp in bd["loops"] if lp["innermost"] and lp["simd"])}
    if bd["command"] != template.replace("{kernel}", kernel):
        out["command"] = bd["command"]
    return out


def _arm_diff(job_dir, kernel, suffix):
    name = f"{kernel}.{suffix}"
    lines = _arm_listing(job_dir, name)
    return {"file": name, "added": sum(1 for x in lines if x.startswith("+") and not x.startswith("+++")),
            "removed": sum(1 for x in lines if x.startswith("-") and not x.startswith("---"))}


def _arm_agreement(job_dirs, det_docs, res_docs, kernels):
    """In how many jobs each kernel's record (all five builds: the run's own facts, the listings, the four diffs, the
    compiler-remark files) and the machine facts equal those of the first job. The binaries are expected to be the same
    in every job (one image, one toolchain); this counts it."""
    def read(path):
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def kernel_sig(job_dir, det, k):
        kd = det["kernels"][k]
        parts = [kd.get("loop_line")]
        for b in ARM_BUILDS:
            parts += [kd[b], read(os.path.join(job_dir, "asm", f"{k}.{b}.s")), read(os.path.join(job_dir, "remarks", f"{k}.{b}.txt"))]
        parts += [read(os.path.join(job_dir, "asm", f"{k}.{s}")) for _, s in ARM_DIFFS]
        return json.dumps(parts, sort_keys=True)

    def machine_sig(det, res):
        ls = det["lscpu"]
        return json.dumps([res["run"]["runner"], res["run"]["toolchain"], res["run"]["flags"], det["cache_bytes"],
                           det["size_targets_bytes"], det["pinned_cpu"], det["reps_per_side"],
                           [_lscpu_field(ls, k) for k in ("Model name", "Vendor ID", "Stepping", "CPU(s)", "Thread(s) per core", "Flags")]],
                          sort_keys=True)
    sigs = [{k: kernel_sig(d, det, k) for k in kernels} for d, det in zip(job_dirs, det_docs)]
    msig = [machine_sig(det, res) for det, res in zip(det_docs, res_docs)]
    per_kernel = {k: sum(1 for s in sigs if s[k] == sigs[0][k]) for k in kernels}
    return per_kernel, sum(1 for s in msig if s == msig[0])


def _arm_x86(index, x86):
    """The x86-64 numbers the Arm column is set beside, read from the pool the page is built on (nothing recomputed):
    the model the page opens on (the one with the most jobs), the page-level ranges, the judged models' ranges per lost kernel."""
    model = next(e for e in index["cpus"] if e["slug"] == index["default_cpu"])
    block = next(b for b in x86["cpus"] if b["cpu_model"] == model["cpu_model"])
    cells = {}
    for x in block["cells"]:
        cell = {"class": x["class"], "as_compiled": {k: x["as_compiled"][k] for k in ("ratio", "ci95", "jobs")},
                "aligned": {k: x["aligned"][k] for k in ("ratio", "ci95", "jobs")}}
        pos = (block.get("positive") or {}).get(x["cell_id"])
        cell["positive"] = {k: pos[k] for k in ("ratio", "ci95", "jobs")} if pos else None
        cells[x["cell_id"]] = cell
    judged = index["page"]["judged_cpus"]
    by_kernel = {}
    for e in index["cpus"]:
        if e["cpu_short"] in judged:
            for k, r in (e.get("lost_by_kernel") or {}).items():
                a = by_kernel.setdefault(k, {"min": r["min"], "max": r["max"]})
                a["min"], a["max"] = min(a["min"], r["min"]), max(a["max"], r["max"])
    return {"source": index["pooled"]["source"], "source_sha256": index["pooled"]["source_sha256"],
            "jobs": index["pooled"]["jobs"], "runs": len(index["pooled"]["runs"]),
            "criteria_sha256": x86["criteria_sha256"],
            "model": {k: model[k] for k in ("cpu_model", "cpu_short", "slug", "jobs", "form", "aa_half_width_pct", "lost_by_kernel",
                                            "forward_aligned", "forward_compiled")},
            "cells": cells,
            "page": {"lost": index["page"]["lost"], "forward_aligned": index["page"]["forward"]["aligned"],
                     "forward_compiled": index["page"]["forward"]["compiled"], "forward_cpus": index["page"]["forward_cpus"],
                     "judged_cpus": judged, "cpus_enough": index["page"]["cpus_enough"], "jobs_enough": index["page"]["jobs_enough"]},
            "lost_by_kernel_judged": by_kernel}


ARM_SEEDS = "arm64/seed-sensitivity.json"
ARM_ROBUSTNESS = "robustness/results-arm.json"
ARM_SLOW_SHARE = 0.05          # a process is "slow" when it runs more than 5% above the fastest process of its series in its job
ARM_AA_L2_CELL = "k02_add_fwd.L2"   # the one cell whose identical-binary A/A each job also stored (details.json, aa_extra)
ARM_AA_L1_CELL = "k02_add_fwd.L1"   # the cell of the A/A control the written rules read (controls.aa)
ARM_METHOD_NAMES = {"a": "harness bootstrap", "b": "block bootstrap, 1 ABBA quartet", "b2": "block bootstrap, 2 ABBA quartets",
                    "b5": "block bootstrap, 5 ABBA quartets", "c": "jobs-only bootstrap", "ct": "jobs-only t interval",
                    "d": "lag-1 effective sample size", "d0": "first form of the lag-1 correction"}


def _pool_module():
    """harness/pool.py loaded by path, for the bootstrap statistics that pooled.json does not hold. It puts harness/ on
    sys.path to import placement, stats and verdict; the path is restored afterwards."""
    import importlib.util
    saved = sys.path[:]
    try:
        spec = importlib.util.spec_from_file_location("harness_pool", os.path.join(REPO, "harness", "pool.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path[:] = saved
    return mod


def _geomean(vals):
    import math
    return math.exp(math.fsum(math.log(v) for v in vals) / len(vals))


def _series_mixture(series_per_job):
    """Descriptive statistics of the processes that run more than ARM_SLOW_SHARE above the fastest process of their own
    series in their own job (one list of timings per job). Not a model: it says how many processes are slow, by how much,
    and whether a slow process tends to follow a slow one (the previous repetition of the same side)."""
    import numpy as np
    total = slow = jobs_with = 0
    job_share, excess, job_cv = [], [], []
    after_slow = after_slow_n = after_ok = after_ok_n = 0
    for x in series_per_job:
        a = np.asarray(x, dtype=np.float64)
        e = a / a.min() - 1.0
        s = e > ARM_SLOW_SHARE
        job_cv.append(100.0 * float(a.std(ddof=1) / a.mean()))
        total += len(a)
        n_slow = int(s.sum())
        slow += n_slow
        jobs_with += 1 if n_slow else 0
        job_share.append(n_slow / len(a))
        excess += [float(v) for v in e[s]]
        prev, cur = s[:-1], s[1:]
        after_slow_n += int(prev.sum())
        after_slow += int((prev & cur).sum())
        after_ok_n += int((~prev).sum())
        after_ok += int((~prev & cur).sum())
    q = [float(v) for v in np.percentile(excess, [10, 50, 90])] if excess else None
    return {"processes": total, "slow": slow, "share_slow": slow / total, "jobs": len(series_per_job), "jobs_with_slow": jobs_with,
            "job_share_min": min(job_share), "job_share_max": max(job_share),
            "cv_pct": {"median": float(np.median(job_cv)), "min": min(job_cv), "max": max(job_cv)},
            "excess_pct": {"q10": 100.0 * q[0], "median": 100.0 * q[1], "q90": 100.0 * q[2]} if q else None,
            "pairs_after_slow": after_slow_n, "p_slow_after_slow": after_slow / after_slow_n if after_slow_n else None,
            "pairs_after_ok": after_ok_n, "p_slow_after_ok": after_ok / after_ok_n if after_ok_n else None}


def _floor_ratio(none_per_job, fast_per_job):
    """FAST over NONE at the fast end of the timings instead of the middle: the geometric mean over jobs of the ratio of the
    10th percentiles (linear interpolation) and of the ratio of the fastest processes. Descriptive; the written rules use medians."""
    import numpy as np
    p10 = [float(np.percentile(f, 10) / np.percentile(n, 10)) for n, f in zip(none_per_job, fast_per_job)]
    mn = [min(f) / min(n) for n, f in zip(none_per_job, fast_per_job)]
    return {"p10_ratio": _geomean(p10), "p10_job_range": [min(p10), max(p10)], "min_ratio": _geomean(mn), "min_job_range": [min(mn), max(mn)]}


def _arm_aa_row(pooled_stat, ratios, job_hw, mixture, rule_max):
    return {"pooled": {k: pooled_stat[k] for k in ("ratio", "ci95", "half_width_pct", "between_job_sd_pct")},
            "jobs": len(ratios), "job_ratio_range": [min(ratios), max(ratios)],
            "job_half_width_pct": {"min": min(job_hw), "max": max(job_hw)},
            "per_job": {"ratio": list(ratios), "half_width_pct": list(job_hw)},
            "jobs_above_rule_max": sum(1 for h in job_hw if h > rule_max),
            "above_rule_max": pooled_stat["half_width_pct"] > rule_max, "mixture": mixture}


def _arm_noise(pool, c, res, det, cells, rule_max):
    """The L2 noise facts: the identical-binary A/A at L1 and L2, the same cell's other controls, and how the processes of
    each series are spread (a fast floor and a share of slower processes), from the stored per-job samples."""
    import statistics
    aa1 = [(r["controls"]["aa"]["a_ns"], r["controls"]["aa"]["b_ns"]) for r in res]
    aa2 = [(d["aa_extra"][ARM_AA_L2_CELL]["a_ns"], d["aa_extra"][ARM_AA_L2_CELL]["b_ns"]) for d in det]
    aa = {}
    for size, cell, pairs, pooled_stat, job_hw, source in (
            ("L1", ARM_AA_L1_CELL, aa1, c["aa"], [r["controls"]["aa"]["half_width_pct"] for r in res],
             "controls.aa of each job's results.json, pooled in pooled.json"),
            ("L2", ARM_AA_L2_CELL, aa2, pool.pair_stat(c["cpu_model"], "aa_extra|" + ARM_AA_L2_CELL, aa2),
             [d["aa_extra"][ARM_AA_L2_CELL]["half_width_pct"] for d in det],
             "aa_extra of each job's details.json, pooled here with harness/pool.py pair_stat under the stat id "
             "'aa_extra|" + ARM_AA_L2_CELL + "' (a statistic pooled.json does not hold)")):
        ratios = [statistics.median(b) / statistics.median(a) for a, b in pairs]
        aa[size] = {"cell_id": cell, "source": source,
                    **_arm_aa_row(pooled_stat, ratios, job_hw,
                                  {"a": _series_mixture([p[0] for p in pairs]), "b": _series_mixture([p[1] for p in pairs])}, rule_max)}
    same = next(x for x in cells if x["cell_id"] == ARM_AA_L2_CELL)
    same_cell = {"cell_id": ARM_AA_L2_CELL,
                 "identical_binary_aa": {k: aa["L2"]["pooled"][k] for k in ("half_width_pct", "between_job_sd_pct")},
                 "layout_aa": {k: same["layout_aa"][k] for k in ("half_width_pct", "between_job_sd_pct")},
                 "as_compiled": {k: same["as_compiled"][k] for k in ("half_width_pct", "between_job_sd_pct")},
                 "aligned": {k: same["aligned"][k] for k in ("half_width_pct", "between_job_sd_pct")}}
    by_id = [{x["cell_id"]: x for x in r["cells"]} for r in res]
    rows = []
    for x in cells:
        cid = x["cell_id"]
        cs = [b[cid] for b in by_id]
        none = [c_["none_ns"] for c_ in cs]
        fast = [c_["fast_ns"] for c_ in cs]
        rows.append({"cell_id": cid, "size_class": x["size_class"], "class": x["class"],
                     "none": _series_mixture(none), "fast": _series_mixture(fast),
                     "floor_ratio": {"as_compiled": _floor_ratio(none, fast),
                                     "aligned": _floor_ratio([c_["aligned"]["none_ns"] for c_ in cs], [c_["aligned"]["fast_ns"] for c_ in cs])}})
    by_size = {}
    for size in sorted({r["size_class"] for r in rows}):
        sel = [r for r in rows if r["size_class"] == size]
        entry = {"cells": len(sel)}
        for side in ("none", "fast"):
            tot, sl = sum(r[side]["processes"] for r in sel), sum(r[side]["slow"] for r in sel)
            shares = [r[side]["share_slow"] for r in sel]
            entry[side] = {"processes": tot, "slow": sl, "share_slow": sl / tot, "cell_share_min": min(shares), "cell_share_max": max(shares)}
        by_size[size] = entry
    return {"slow_share": ARM_SLOW_SHARE,
            "definition": "a process is slow when it takes more than 5% longer than the fastest process of the same series "
                          "(one side of one cell, in one job); the excess is that process's time over the fastest, in percent; "
                          "p_slow_after_slow is the share of slow processes among those whose previous repetition on the same side "
                          "was slow. Descriptive only: no cause is established and no hardware counter was read.",
            "rule_aa_half_width_max_pct": rule_max, "identical_binary_aa": aa, "same_cell_l2": same_cell,
            "mixture": {"cells": rows, "by_size": by_size}}


def _arm_layout_vs_placement(pool, c, res, cells):
    """The layout A/A (NONE against NONE built with -falign-loops=64) beside the placement statistic D of the main pair
    (FAST over NONE as compiled, over the same ratio with loops aligned) for all 16 cells. D is in pooled.json for the
    kept-SIMD in-cache cells and is computed here with the same function for the others."""
    by_id = [{x["cell_id"]: x for x in r["cells"]} for r in res]
    builds = {tuple((p["a_build"], p["b_build"]) for p in r["controls"]["layout_aa"] if p["id"] == cells[0]["cell_id"])[0] for r in res}
    assert builds == {("none", "none_a64")}, builds
    rows = []
    for x in cells:
        cid = x["cell_id"]
        stored = next(q for q in c["cells"] if q["cell_id"] == cid).get("placement")
        if stored:
            d, src = stored["d"], "pooled.json"
        else:
            d = pool.placement_stat(c["cpu_model"], f"{cid}|placement",
                                    [(b[cid]["none_ns"], b[cid]["fast_ns"], b[cid]["aligned"]["none_ns"], b[cid]["aligned"]["fast_ns"]) for b in by_id])
            src = "computed here with harness/pool.py placement_stat (not stored in pooled.json)"
        lay = x["layout_aa"]
        rows.append({"cell_id": cid, "class": x["class"], "size_class": x["size_class"],
                     "layout_aa": {k: lay[k] for k in ("ratio", "ci95", "half_width_pct")},
                     "d": {k: d[k] for k in ("ratio", "ci95", "half_width_pct")}, "d_source": src,
                     "as_compiled_over_aligned": x["as_compiled"]["ratio"] / x["aligned"]["ratio"],
                     "d_excludes_1": d["ci95"][0] > 1.0 or d["ci95"][1] < 1.0,
                     "layout_aa_excludes_1": lay["ci95"][0] > 1.0 or lay["ci95"][1] < 1.0,
                     "d_shift_pct": 100.0 * (d["ratio"] - 1.0), "layout_aa_shift_pct": 100.0 * (lay["ratio"] - 1.0),
                     "implied_fast_side_ratio": d["ratio"] / lay["ratio"]})
    blind = [r["cell_id"] for r in rows if r["d_excludes_1"] and not r["layout_aa_excludes_1"]]
    top = max(rows, key=lambda r: abs(r["d_shift_pct"]))
    top_l1 = max((r for r in rows if r["size_class"] == "L1"), key=lambda r: abs(r["d_shift_pct"]))
    return {"note": "D = (FAST/NONE as compiled) / (FAST/NONE aligned), the pooled geometric mean over jobs. The layout A/A moves only "
                    "NONE's loops (NONE against NONE aligned); D moves both builds' loops, so D / layout A/A ratio is what the pooled "
                    "numbers imply for FAST's own placement shift (arithmetic on two pooled ratios from separate timings of the same "
                    "binaries; implied_fast_side_ratio).",
            "layout_aa_builds": ["none", "none_a64"], "rows": rows,
            "d_excludes_1_layout_aa_includes_1": blind, "largest_d_shift": {"cell_id": top["cell_id"], "d_shift_pct": top["d_shift_pct"]},
            "largest_d_shift_l1": {"cell_id": top_l1["cell_id"], "d_shift_pct": top_l1["d_shift_pct"]},
            "largest_layout_aa_shift_l1_pct": max(abs(r["layout_aa_shift_pct"]) for r in rows if r["size_class"] == "L1")}


def _arm_matmul_cost(cells, ks, res):
    """Matrix multiply at the two sizes: the time ratio against Cachegrind's instruction ratio, and what differs between
    the two cells (cache level, d, the elements left after whole vector passes)."""
    import math
    k = next(x for x in ks if x["kernel"] == "k08_matmul")
    width, interleave = k["builds"]["fast"]["width"], k["builds"]["fast"]["interleave"]
    out = {"vector_pass_elements": width * interleave, "width": width, "interleave": interleave, "sizes": {}}
    for size in ("L1", "L2"):
        x = next(q for q in cells if q["cell_id"] == f"k08_matmul.{size}")
        cmd = res[0]["cells"][[q["cell_id"] for q in res[0]["cells"]].index(x["cell_id"])]["command"].splitlines()[-1]
        d = int(cmd.split()[-2])
        row = {"d": d, "d_mod_pass": d % (width * interleave), "whole_passes": d // (width * interleave),
               "working_set_bytes": res[0]["cells"][[q["cell_id"] for q in res[0]["cells"]].index(x["cell_id"])]["working_set_bytes"]}
        for col in ("as_compiled", "aligned"):
            t, i = x[col]["ratio"], x["instr_ratio"][col]
            row[col] = {"time_ratio": t, "instr_ratio": i, "log_time_over_log_instr": math.log(t) / math.log(i)}
        out["sizes"][size] = row
    return out


def _arm_forward_instr(cells_in, res):
    """The three forward loops: Cachegrind's instruction counts of the two builds at both sizes, as compiled and aligned, beside
    the time ratio. The instructions the check adds are the same number at both sizes (a constant per call), so the share they
    make of a call depends on the array length chosen for the size."""
    rows = []
    for x in cells_in:
        if x["kernel"] not in ARM_FORWARD:
            continue
        rc = next(q for q in res[0]["cells"] if q["cell_id"] == x["cell_id"])
        row = {"cell_id": x["cell_id"], "kernel": x["kernel"], "size_class": x["size_class"],
               "elements": int(rc["command"].splitlines()[-1].split()[-2])}
        for col, ik in (("as_compiled", "instr"), ("aligned", "aligned_instr")):
            i = x[ik]
            row[col] = {"none": i["none"], "fast": i["fast"], "added": i["fast"] - i["none"], "instr_ratio": i["ratio"],
                        "time_ratio": x[col]["ratio"]}
        rows.append(row)
    same = {}
    for k in ARM_FORWARD:
        sel = [r for r in rows if r["kernel"] == k]
        same[k] = {col: len({r[col]["added"] for r in sel}) == 1 for col in ("as_compiled", "aligned")}
    return {"cells": rows, "added_same_at_both_sizes": same}


def _arm_interval_methods(c, rob, rob_sha):
    """The eight interval methods of robustness/analyze.py on the Arm pool, read from robustness/results-arm.json: per method
    the verdict form, which counted forward cells miss the rule, and the interval of the deciding cell."""
    import statistics
    ds = rob["datasets"]["s8arm"]
    r = ds["cpus"][c["cpu_model"]]
    a = r["methods"]["a"]
    methods = []
    for m in rob["methods"]:
        x = r["methods"][m]
        cells = x["cells"]
        flips = {"fwd_pass": [], "lost_ok": [], "placement_sensitive": []}
        widths = []
        for cid, ca in a["cells"].items():
            cx = cells[cid]
            for key, fk in (("fwd_pass", "fwd_pass"), ("lost_ok", "lost_ok"), ("ps", "placement_sensitive")):
                if key in ca and ca[key] != cx[key]:
                    flips[fk].append(cid)
            for col in ("ac", "al"):
                widths.append((cx[col][2] - cx[col][1]) / (ca[col][2] - ca[col][1]))
        lost = [min(q["ac"][1], q["al"][1]) for q in cells.values() if q["class"] == "lost"]
        fwd = [q["al"][2] for q in cells.values() if q["class"] == "kept" and not q.get("ps")]
        dec = cells[ARM_AA_L2_CELL]["al"]
        methods.append({"id": m, "name": ARM_METHOD_NAMES[m], "form": x["form"], "aa_half_width_pct": x["aa_hw_pct"],
                        "forward_limit": 1.0 + x["limit_pct"] / 100.0,
                        "forward_misses": sorted(cid for cid, q in cells.items() if q["class"] == "kept" and not q.get("ps") and not q["fwd_pass"]),
                        "placement_sensitive": sorted(cid for cid, q in cells.items() if q.get("ps")),
                        "deciding_cell": {"cell_id": ARM_AA_L2_CELL, "column": "aligned", "ratio": dec[0], "ci95": [dec[1], dec[2]]},
                        "flips": {k: len(v) for k, v in flips.items()},
                        "width_ratio_median": statistics.median(widths), "width_ratio_max": max(widths),
                        "min_lost_ci95_lo": min(lost), "max_forward_ci95_hi": max(fwd)})
    forms = {}
    for m in methods:
        forms[m["form"]] = forms.get(m["form"], 0) + 1
    return {"source": ARM_ROBUSTNESS, "source_sha256": rob_sha, "plan": "robustness/PLAN.md", "report": "robustness/report.md",
            "pool_form_of_record": c["verdict"]["form"], "self_test": ds["self_test"], "autocorr": r["autocorr"], "jobs": r["jobs"],
            "methods": methods, "forms": forms, "map_methods": [m["id"] for m in methods if m["form"] == "map"],
            "inconclusive_methods": [m["id"] for m in methods if m["form"] == "inconclusive"]}


def _arm_seed_sensitivity(seeds, seeds_sha, pooled_sha):
    """The compact form of arm64/seed-sensitivity.json (arm64/seeds.py): what the page and the README quote."""
    assert seeds["pool"]["sha256"] == pooled_sha, "arm64/seed-sensitivity.json was made from another version of the pool; run python arm64/seeds.py"
    rows = []
    for r in seeds["rows"]:
        e = {"id": r["id"], "kind": r["kind"], "cell_id": r["cell_id"], "column": r["column"], "stored": r["stored"]}
        if r["kind"] == "forward":
            e.update({"judged": r["judged"], "limit": r["limit"], "alt_hi": r["alt"]["hi"], "alt_at_or_above_limit": r["alt"]["at_or_above_limit"],
                      "alt_above_limit": r["alt"]["above_limit"], "alt_above_stored": r["alt"]["above_stored"],
                      "converged_hi": r["converged"]["hi"], "converged_above_limit": r["converged"]["above_limit"]})
        elif r["kind"] == "lost":
            e.update({"limit": r["limit"], "alt_lo": r["alt"]["lo"], "alt_below_limit": r["alt"]["below_limit"]})
        elif r["kind"] == "placement":
            e.update({"mechanical": r["mechanical"], "stored_excludes_1": r["stored_excludes_1"], "stored_sensitive": r["stored_sensitive"],
                      "alt_excludes_1": r["alt"]["excludes_1"], "alt_sensitive": r["alt"]["sensitive"]})
        elif r["kind"] == "positive":
            e.update({"alt_lo": r["alt"]["lo"], "alt_seen": r["alt"]["seen"]})
        else:
            e.update({"limit": r["limit"], "alt_half_width_pct": r["alt"]["half_width_pct"], "alt_above_limit": r["alt"]["above_limit"],
                      "alt_forward_limit_above_floor": r["alt"]["forward_limit_above_floor"]})
        e["draws"] = r["alt"]["draws"]
        rows.append(e)
    d = seeds["deciding_cell"]
    full = seeds["full"]
    derived = seeds["derived"]
    return {"source": ARM_SEEDS, "source_sha256": seeds_sha, "script": "arm64/seeds.py", "pool_sha256": pooled_sha,
            "stored_seed": {k: seeds["stored_seed"][k] for k in ("prefix", "resamples", "fixed_on", "fixed_in")},
            "alt_seeds": {k: seeds["alt_seeds"][k] for k in ("pattern", "count", "resamples")},
            "converged_resamples": seeds["converged"]["resamples"],
            "deciding_cell": {k: d[k] for k in d if k not in ("upper_ends", "seeds_at_or_above_limit")},
            "rows": rows,
            "full": {k: full[k] for k in ("count", "forms", "forward_missed_counts", "lost_missed_any", "placement_sets", "aa_half_width_pct",
                                          "forward_limit_pct", "deciding_hi")},
            "derived": {k: derived[k] for k in ("basis", "seeds", "equals_analyse_cpu_on_first", "forms", "forward_missed_counts",
                                                "lost_missed_any", "placement_sets", "positive_seen_in_all", "not_map_seeds")}}


def _arm_stored_diffs(ks, job_dirs):
    """The stored Arm .diff files were written when harness/asm.py normalised branch targets of four or more hex digits only,
    so a branch that moved between NONE and FAST with a three-digit target shows as one removed and one added line. Per kernel
    and diff: the stored counts of added and removed lines, and the counts of the diff the fixed normalize() makes of the same
    two saved listings (the stored files themselves are not regenerated)."""
    asm_mod = _harness_module("asm")
    builds = {"L1": ("none", "fast"), "L2": ("none", "fast"), "L1_aligned": ("none_a64", "fast_a64"), "L2_aligned": ("none_a64", "fast_a64")}

    def counts(lines):
        return (sum(1 for x in lines if x.startswith("+") and not x.startswith("+++")),
                sum(1 for x in lines if x.startswith("-") and not x.startswith("---")))

    out = []
    for kr in ks:
        k = kr["kernel"]
        row = {"kernel": k}
        for name, suffix in ARM_DIFFS:
            a, r = counts(_arm_listing(job_dirs[0], f"{k}.{suffix}"))
            nb, fb = builds[name]
            a2, r2 = counts(asm_mod.unified_diff(_arm_listing(job_dirs[0], f"{k}.{nb}.s"), _arm_listing(job_dirs[0], f"{k}.{fb}.s"),
                                                 f"{k}.{nb}.s", f"{k}.{fb}.s").splitlines())
            row[name] = {"added": a, "removed": r, "added_after_fix": a2, "removed_after_fix": r2}
        out.append(row)
    return {"normalize_fixed_in": "harness/asm.py normalize(): targets of three or more hex digits (was four); applies to future runs",
            "stored_diffs_predate_fix": True,
            "note": "The .diff files of results/s8-arm-run-* were written before the fix and are not regenerated. A branch whose "
                    "three-digit target moved between the builds appears in them as one removed and one added line; the "
                    "after_fix counts are those of the diff the fixed normalize() makes of the same saved listings.",
            "kernels": out}


def arm64_data(index, x86):
    """site/data/arm64.json: the Arm column. Everything is read from results/s8-arm-pooled/pooled.json and the per-job
    files of the runs it names (nothing is recomputed by hand and nothing is typed in, except ARM_PREDICTED, which copies
    the plan's own words); the x86-64 numbers come from `index` and `x86` (the pool the page is built on), read-only."""
    import statistics
    path = os.path.join(REPO, ARM_POOLED)
    pooled = load(path)
    crit = load(os.path.join(REPO, CRITERIA_FILE))
    assert pooled["criteria_file"] == CRITERIA_FILE and len(pooled["cpus"]) == 1, "the Arm pool is one CPU model under criteria-v3"
    c = pooled["cpus"][0]
    v, vc = c["verdict"], crit["verdict"]
    min_jobs = crit["v3"]["pooling"]["minimum_jobs"]
    base = os.path.dirname(path)
    job_dirs = [os.path.normpath(os.path.join(base, os.path.dirname(i["path"]))) for i in pooled["inputs"]]
    res = [load(os.path.join(d, "results.json")) for d in job_dirs]
    det = [load(os.path.join(d, "details.json")) for d in job_dirs]
    hp = _harness_module("placement")
    cells_in = c["cells"]
    kernels = sorted({x["kernel"] for x in cells_in})
    sizes = sorted({x["size_class"] for x in cells_in})
    ps_ids = [p["cell_id"] for p in v["placement_sensitive"]]
    limit = 1.0 + v["forward_limit_pct"] / 100.0

    # runs
    runs = []
    for rid in pooled["runs"]:
        rd = [r for r in res if r["run"]["id"] == rid]
        pr = next(x for x in c["per_run"] if x["run_id"] == rid)
        runs.append({"run_id": rid, "workflow_run_url": rd[0]["run"]["workflow_run_url"], "commit": rd[0]["run"]["commit"],
                     "started_at": min(r["run"]["started_at"] for r in rd), "jobs": len(rd), "form": pr["form"], "line": pr["line"]})

    # machine and toolchain (the first job's record; the agreement count says how many jobs report the same)
    per_kernel_agree, machine_agree = _arm_agreement(job_dirs, det, res, kernels)
    r0, d0 = res[0], det[0]
    ls = d0["lscpu"]
    flag_set = set((_lscpu_field(ls, "Flags") or "").split())
    commands = [bd["command"] for kd in d0["kernels"].values() for bd in kd.values() if isinstance(bd, dict) and "command" in bd]
    templates = {b: d0["kernels"][kernels[0]][b]["command"].replace(kernels[0], "{kernel}") for b in ARM_BUILDS}
    runner = r0["run"]["runner"]
    machine = {"os": runner["os"], "kernel": runner["kernel"], "arch": runner["arch"], "cpu_model": runner["cpu_model"],
               "vendor_id": _lscpu_field(ls, "Vendor ID"), "stepping": _lscpu_field(ls, "Stepping"), "vcpus": runner["cores"],
               "threads_per_core": int(_lscpu_field(ls, "Thread(s) per core")),
               "l1d_kib": runner["l1d_kib"], "l2_kib": runner["l2_kib"], "l3_kib": runner["l3_kib"],
               "cache_bytes": d0["cache_bytes"], "size_targets_bytes": d0["size_targets_bytes"],
               "pinned_cpu": d0["pinned_cpu"], "reps_per_side": d0["reps_per_side"],
               "isa_flags": {f: f in flag_set for f in ("asimd", "sve", "sve2")},
               "march_flag_in_builds": any(re.search(r"-m(?:arch|cpu)=", x) for x in commands),
               "toolchain": r0["run"]["toolchain"], "flags": r0["run"]["flags"], "commands": templates,
               "jobs": len(res), "jobs_agreeing": machine_agree}

    # cells
    run_cells = [r.get("cells") for r in c["per_run"]]
    cells = []
    for x in cells_in:
        cid = x["cell_id"]
        pl = x.get("placement")
        pos = c["positive"].get(cid)
        cells.append({
            "cell_id": cid, "kernel": x["kernel"], "size_class": x["size_class"], "class": x["class"],
            "as_compiled": _arm_stat(x["as_compiled"], True), "aligned": _arm_stat(x["aligned"], True),
            "instr_ratio": {"as_compiled": x["instr"]["ratio"], "aligned": x["aligned_instr"]["ratio"]}, "instr_agree": x["instr_agree"],
            "layout_aa": _arm_stat(c["layout_aa"][cid]),
            "positive": _arm_stat(pos) if pos else None,
            "placement": ({k: pl[k] for k in ("statistical", "mechanical", "sensitive", "hot_none", "hot_fast")}
                          | {"d": _arm_stat(pl["d"])}) if pl else None,
            "placement_sensitive": cid in ps_ids,
            "per_run": {col: [rc[cid][col][0] if rc else None for rc in run_cells] for col in ("as_compiled", "aligned")},
        })
    by_id = {x["cell_id"]: x for x in cells}
    sd = [(x[col]["between_job_sd_pct"], x["cell_id"], col) for x in cells for col in ("as_compiled", "aligned")]
    sd_l1 = max(s for s in sd if s[1].endswith(".L1"))
    sd_l2 = max(s for s in sd if s[1].endswith(".L2"))

    # kernels
    src = kernel_sources(kernels)
    ks = []
    for k in kernels:
        job_dir = job_dirs[0]
        builds = {b: _arm_build(job_dir, k, b, d0["kernels"][k][b], hp, templates[b]) for b in ARM_BUILDS}
        vn, vf = builds["none"]["vectorized"], builds["fast"]["vectorized"]
        remark_class = "off_axis" if not vn else "kept" if vf else "lost"
        classes = {by_id[f"{k}.{s}"]["class"] for s in sizes}
        flagged = [cid for cid in ps_ids if cid.startswith(k + ".")]
        pred = ARM_PREDICTED[k]
        simd = {}
        for col, (nb, fb) in (("as_compiled", ("none", "fast")), ("aligned", ("none_a64", "fast_a64"))):
            mn = _arm_simd_mnemonics(_arm_listing(job_dir, f"{k}.{nb}.s"), hp)
            mf = _arm_simd_mnemonics(_arm_listing(job_dir, f"{k}.{fb}.s"), hp)
            simd[col] = {"none_instructions": len(mn) if mn is not None else None, "fast_instructions": len(mf) if mf is not None else None,
                         "same_opcodes": (mn == mf) if mn is not None and mf is not None else None}
        ks.append({
            "kernel": k, "name": VERSIONS_KERNELS[k], "source": src[k], "class": classes.pop() if len(classes) == 1 else None,
            "class_from_remarks": remark_class,
            "prediction": {"class": pred, "class_held": (pred == remark_class) if pred else None,
                           "placement_effect": "none" if k in ARM_FORWARD else None,
                           "placement_held": (not flagged) if k in ARM_FORWARD else None},
            "placement_sensitive_cells": flagged,
            "builds": builds, "simd_loop": simd,
            "asm_lines_delta": builds["fast"]["asm_lines"] - builds["none"]["asm_lines"],
            "neon_removed": builds["none"]["neon_instructions"] - builds["fast"]["neon_instructions"],
            "diffs": {name: _arm_diff(job_dir, k, suffix) for name, suffix in ARM_DIFFS},
            "source_job": rel(job_dir), "jobs_agreeing": per_kernel_agree[k],
        })

    # verdict
    kept_rows, lost_rows, above = [], [], []
    for x in cells:
        a = x["aligned"]
        if x["class"] == "kept":
            judged = x["cell_id"] not in ps_ids
            kept_rows.append({"cell_id": x["cell_id"], "kernel": x["kernel"], "size_class": x["size_class"], "judged": judged,
                              "as_compiled_ratio": x["as_compiled"]["ratio"], "aligned_ratio": a["ratio"], "aligned_ci_hi": a["ci95"][1],
                              "passes": (a["ratio"] <= vc["forward_point_max_ratio"] and a["ci95"][1] <= limit) if judged else None})
        if x["class"] == "lost":
            lo = {col: x[col]["ci95"][0] for col in ("as_compiled", "aligned")}
            lost_rows.append({"cell_id": x["cell_id"], "kernel": x["kernel"], "size_class": x["size_class"],
                              "as_compiled_ci_lo": lo["as_compiled"], "aligned_ci_lo": lo["aligned"],
                              "passes": all(q >= vc["lost_ci_lo_min_ratio"] for q in lo.values())})
        if x["class"] in ("kept", "lost") and x["cell_id"] not in ps_ids:
            for col in ("as_compiled", "aligned"):
                if x[col]["ci95"][0] > limit:
                    above.append({"cell_id": x["cell_id"], "column": col, "ci_lo": x[col]["ci95"][0]})
    verdict = {"form": v["form"], "line": v["line"], "why": v["why"], "stability": c["stability"], "page_line": pooled["page"]["line"],
               "forward_limit_pct": v["forward_limit_pct"], "limit": limit, "forward_point_max_ratio": vc["forward_point_max_ratio"],
               "lost_ci_lo_min_ratio": vc["lost_ci_lo_min_ratio"], "aa_half_width_max_pct": vc["aa_half_width_max_pct"],
               "aa_half_width_pct": v["aa_half_width_pct"], "minimum_jobs": min_jobs,
               "n": v["n"], "n_as_compiled": v["n_as_compiled"], "x_pct": v["x_pct"],
               "forward_rule_cells": kept_rows, "forward_missed": [r["cell_id"] for r in kept_rows if r["judged"] and not r["passes"]],
               "lost_rule_cells": lost_rows, "above_forward_limit": above,
               "placement_sensitive": v["placement_sensitive"], "off_axis": v["off_axis"]}

    # cpu_summary() names the cells of kernels that keep SIMD "forward"; here that group also holds matrix multiply, so the
    # keys say "kept", and the three forward loops of the plan get their own ranges
    summary = cpu_summary(c, min_jobs)
    for k in ("forward_aligned", "forward_compiled", "forward_compiled_max_cell", "forward_judged_aligned"):
        if k in summary:
            summary["kept" + k[len("forward"):]] = summary.pop(k)
    forward_loops = {"kernels": list(ARM_FORWARD)}
    for s in sizes:
        fc = [x for x in cells if x["kernel"] in ARM_FORWARD and x["size_class"] == s]
        forward_loops[s] = {col: minmax([x[col]["ratio"] for x in fc]) for col in ("as_compiled", "aligned")}

    aa = c["aa"]
    layout_hw = [x["layout_aa"]["half_width_pct"] for x in cells]
    job_hw = [r["controls"]["aa"]["half_width_pct"] for r in res]
    rep = c["reproduction"]

    # sensitivity readings beside the stored verdict (they change nothing in it): the other seeds (arm64/seeds.py, stored in
    # arm64/seed-sensitivity.json), the other interval methods (robustness/analyze.py --arm, stored in robustness/results-arm.json),
    # the noise of the L2 timings, the layout A/A against D, the matrix multiply cost against its instruction count
    seeds_path, rob_path = os.path.join(REPO, ARM_SEEDS), os.path.join(REPO, ARM_ROBUSTNESS)
    seeds, rob = load(seeds_path), load(rob_path)
    dec_cell = ARM_AA_L2_CELL
    dec = by_id[dec_cell]["aligned"]
    sdc = seeds["deciding_cell"]
    assert (sdc["cell_id"], sdc["column"]) == (dec_cell, "aligned") and sdc["stored_hi"] == dec["ci95"][1], "the seed file is not about this pool"
    ra = rob["datasets"]["s8arm"]["cpus"][c["cpu_model"]]["methods"]["a"]
    import math
    assert ra["form"] == v["form"] and all(math.isclose(p, q, rel_tol=1e-9) for p, q in zip(ra["cells"][dec_cell]["al"], [dec["ratio"], *dec["ci95"]])), \
        "results-arm.json is not about this pool"
    pool_mod = _pool_module()
    noise = _arm_noise(pool_mod, c, res, det, cells, vc["aa_half_width_max_pct"])
    return {
        "note": "derived by scripts/build_site_data.py from " + ARM_POOLED + " and the per-job files of the runs it names; "
                "an additive column: it changes no x86-64 file or number, and its x86 block only repeats numbers read from the "
                "pool the page is built on",
        "plan": ARM_PLAN, "source": ARM_POOLED, "source_sha256": sha(path), "arch": machine["arch"],
        "cpu_model": c["cpu_model"], "cpu_short": cpu_short(c["cpu_model"]), "slug": slug(cpu_short(c["cpu_model"])),
        "criteria": {"file": CRITERIA_FILE, "sha256": pooled["criteria_sha256"],
                     "same_as_x86_pool": pooled["criteria_sha256"] == x86["criteria_sha256"],
                     "resamples": pooled["resamples"], "minimum_jobs": min_jobs, "jobs_per_run": crit["v3"]["matrix"]["jobs_per_run"],
                     "reps_per_side": crit["v3"]["timing"]["reps_per_side"]},
        "jobs": len(res), "runs": runs, "machine": machine,
        "summary": summary, "forward_loops": forward_loops,
        "aa": {"ratio": aa["ratio"], "ci95": aa["ci95"], "half_width_pct": aa["half_width_pct"], "jobs": aa["jobs"],
               "between_job_sd_pct": aa["between_job_sd_pct"], "per_job": aa["per_job"],
               "job_half_width_pct": {"min": min(job_hw), "median": statistics.median(job_hw), "max": max(job_hw)},
               "layout_half_width_pct": {"min": min(layout_hw), "max": max(layout_hw)}},
        "between_job_sd": {"l1_max_pct": sd_l1[0], "l1_max_cell": sd_l1[1], "l1_max_column": sd_l1[2],
                           "l2_max_pct": sd_l2[0], "l2_max_cell": sd_l2[1], "l2_max_column": sd_l2[2]},
        "reproduction": {"checked": rep["checked"], "outside": rep["outside"],
                         "max_gap_pct": max([m["gap_pct"] for m in rep["misses"]], default=None), "misses": rep["misses"]},
        "verdict": verdict, "cells": cells, "kernels": ks,
        "instr_label": cells_in[0]["instr_label"],
        "build_facts": {"jobs": len(res), "kernels": len(kernels), "builds_per_kernel": len(ARM_BUILDS),
                        "files_per_kernel": len(ARM_BUILDS) * 2 + len(ARM_DIFFS), "machine_jobs_agreeing": machine_agree,
                        "all_agree": machine_agree == len(res) and all(n == len(res) for n in per_kernel_agree.values())},
        "x86": _arm_x86(index, x86),
        "seed_sensitivity": _arm_seed_sensitivity(seeds, sha(seeds_path), sha(path)),
        "interval_methods": _arm_interval_methods(c, rob, sha(rob_path)),
        "noise": noise,
        "layout_vs_placement": _arm_layout_vs_placement(pool_mod, c, res, cells),
        "matmul_cost": _arm_matmul_cost(cells, ks, res),
        "forward_instr": _arm_forward_instr(cells_in, res),
        "stored_diffs": _arm_stored_diffs(ks, job_dirs),
    }


# ---------------------------------------------------------------- the replication (replication/PLAN.md, replication/results.json)
REPLICATION = "replication/results.json"
REPLICATION_PLAN = "replication/PLAN.md"
REPLICATION_COMPARE = "replication/compare.py"


def _repl_form(rec):
    """One pool's reading of one CPU model as the page prints it: the cause of a verdict that is not MAP is kept as cell ids
    and numbers (the stored sentence, which lists every cell above the limit, is left in replication/results.json)."""
    if rec is None:
        return None
    forms = {}
    for r in rec["per_run"]:
        k = r["form"] or "too_few_jobs"
        forms[k] = forms.get(k, 0) + 1
    return {"jobs": rec["jobs"], "runs": rec["runs"], "enough": rec["enough"], "form": rec["form"], "stability": rec["stability"],
            "run_forms": dict(sorted(forms.items())), "aa_half_width_pct": rec["aa_half_width_pct"],
            "forward_limit_pct": rec["forward_limit_pct"], "placement_sensitive": rec["placement_sensitive"],
            "closest_forward": rec["closest_forward"],
            "cause": ({k: v for k, v in rec["cause"].items() if k != "why"} if rec["cause"] else None)}


def _repl_names(row):
    return {"cpu_model": row["cpu_model"], "cpu_short": cpu_short(row["cpu_model"]), "slug": slug(cpu_short(row["cpu_model"]))}


def replication_data():
    """site/data/replication.json: replication/results.json reduced to what the page prints. Nothing is computed here except the
    per-run verdict counts, the row status words and the order of the rows; every number is read from the file
    (replication/compare.py --verify ties that file to the six pooled files)."""
    path = os.path.join(REPO, REPLICATION)
    r = load(path)
    assert r["schema"] == "replication-1", "replication/results.json has another schema"
    assert r["plan_sha256"] == sha(os.path.join(REPO, REPLICATION_PLAN)), \
        "replication/PLAN.md differs from the one replication/results.json was derived under"
    assert r["criteria"]["sha256"] == sha(os.path.join(REPO, CRITERIA_FILE)), "replication/results.json was derived under other criteria"
    rows = []
    for arch in ("x86", "arm"):
        a = r[arch]
        for m in sorted(a["models"], key=lambda x: (-(x["earlier"]["jobs"] if x["earlier"] else 0), x["cpu_model"])):
            ins = m["inside"]
            rows.append({
                "arch": arch, **_repl_names(m),
                "earlier": _repl_form(m["earlier"]), "replication": _repl_form(m["replication"]), "secondary": _repl_form(m["secondary"]),
                "testable": m["testable"], "same_form": m["same_form"],
                "status": "not testable" if not m["testable"] else "same" if m["same_form"] else "flipped",
                "inside": ({k: ins[k] for k in ("checked", "inside", "outside", "max_gap_pct", "max_abs_point_diff_pct",
                                                "point_diff_under_1pct", "largest_point_diffs", "misses")} if ins else None)})
    out_arch = {}
    for arch in ("x86", "arm"):
        a = r[arch]
        out_arch[arch] = {
            "names": a["names"], "totals": a["totals"],
            "flips": [{"cpu_model": f["cpu_model"], "cpu_short": cpu_short(f["cpu_model"]), "slug": slug(cpu_short(f["cpu_model"])),
                       "earlier_form": f["earlier_form"], "replication_form": f["replication_form"],
                       "cells": [{"cell_id": c["cell_id"], **{k: c[k] for k in ("earlier", "replication", "secondary")}}
                                 for c in f["cells"]]} for f in a["flips"]],
            "not_testable": [{"cpu_model": n["cpu_model"], "cpu_short": cpu_short(n["cpu_model"]), "slug": slug(cpu_short(n["cpu_model"])),
                              "earlier_jobs": n["earlier_jobs"], "replication_jobs": n["replication_jobs"],
                              "earlier_form": n["earlier_form"], "secondary": _repl_form(n["secondary"])} for n in a["not_testable"]]}
    arm = r["arm"]
    out_arch["arm"]["model"] = _repl_names({"cpu_model": arm["model"]})
    out_arch["arm"]["named_cells"] = [{"cell_id": c["cell_id"], "decides_earlier_verdict": c["decides_earlier_verdict"],
                                       **{k: c[k] for k in ("earlier", "replication", "secondary")}} for c in arm["named_cells"]]
    h = r["x86"]["headline"]
    out_arch["x86"]["headline"] = {
        "page_range": h["page_range"], "replication_judged_range": h["replication_judged_range"],
        "replication_enough_range": h["replication_enough_range"], "outside_printed_range": h["outside_printed_range"],
        "outside_stored_range": h["outside_stored_range"],
        "earlier": [{**_repl_names(x), **{k: v for k, v in x.items() if k != "cpu_model"}} for x in h["earlier"]],
        "replication": [{**_repl_names(x), **{k: v for k, v in x.items() if k != "cpu_model"}} for x in h["replication"]]}
    q = r["questions"]
    q2 = dict(q["xeon_6973pc"])
    q2["secondary_cause"] = {k: v for k, v in q2["secondary_cause"].items() if k != "why"} if q2["secondary_cause"] else None
    q2 = {**_repl_names({"cpu_model": q2["model"]}), **{k: v for k, v in q2.items() if k != "model"}}
    return {
        "note": "derived by scripts/build_site_data.py from " + REPLICATION + " (replication/compare.py derives that file from the six "
                "pooled files named in `pools`); do not edit by hand. The separate sets are the result; the pooled forms are "
                "secondary, because the sets were requested after a borderline reading, so the stopping point depended on the data.",
        "plan": REPLICATION_PLAN, "plan_sha256": r["plan_sha256"], "source": REPLICATION, "source_sha256": sha(path),
        "compare": REPLICATION_COMPARE, "criteria": {k: v for k, v in r["criteria"].items() if k not in ("sha256", "pooled_under_sha256")},
        "pools": {arch: {role: {"path": p["path"], "sha256": p["sha256"], "jobs": p["jobs"], "runs": len(p["runs"]),
                               "run_ids": p["runs"], "models_drawn": p["models_drawn"]} for role, p in r["pools"][arch].items()}
                  for arch in ("x86", "arm")},
        "rows": rows, "arch": out_arch,
        "questions": {"arm_cell": q["arm_cell"], "xeon_6973pc": q2},
    }


# ---------------------------------------------------------------- the matrix-multiply d-sweep (dsweep/PLAN.md, results/s10-dsweep-*)
DSWEEP_POOLED = "results/s10-dsweep-pooled/dsweep-pooled.json"
DSWEEP_TABLE = "results/s10-dsweep-pooled/table.md"
DSWEEP_PLAN = "dsweep/PLAN.md"
DSWEEP_ANALYSIS = "dsweep/analyze.py"
DSWEEP_COLUMNS = ("as_compiled", "aligned")
DSWEEP_MODES = ("none", "fast", "none_a64", "fast_a64")


def _ds_column(b, col):
    """What the rule read for one column of one CPU model, and the word it gave."""
    c = b["columns"][col]
    ex = c["excess"]
    return {"word": b["words"][col]["word"], "reason": b["words"][col]["reason"],
            "share": ex["share"], "share_ci95": ex["share_ci95"],
            "fixed": ex["fixed"], "fixed_ci95": ex["fixed_ci95"],
            "per_element_at_d_max": ex["per_element_at_d_max"], "per_element_at_d_max_ci95": ex["per_element_at_d_max_ci95"],
            "excess_at_d_min": ex["at_d_min"], "excess_at_d_max": ex["at_d_max"],
            "growth": ex["growth"], "growth_ci95": ex["growth_ci95"], "undefined_fraction": ex["undefined_fraction"],
            "excess_residual": ex["residual"]["median_max_relative_residual"],
            "baseline_residual": c["baseline"]["median_max_relative_residual"],
            "cost_threshold": c["cost_threshold"], "cost_unseen": c["cost_unseen"], "fit_ds": c["fit_ds"]}


def _ds_rows(b):
    """One row per d, in the order of the analysis: both columns (FAST/NONE with its 95% interval and the excess in ns per
    inner call), the Cachegrind instruction counts (instructions, not time) and the placement statistic."""
    ali = {r["d"]: r for r in b["columns"]["aligned"]["rows"]}
    pla = {r["d"]: r for r in b["placement"]["rows"]}
    ins = {r["d"]: r for r in b["instructions"]["rows"]}
    rows = []
    for r in b["columns"]["as_compiled"]["rows"]:
        d = r["d"]
        a = ali[d]
        assert a["roles"] == r["roles"], f"d = {d}: the two columns disagree on the role"
        rows.append({
            "d": d, "roles": r["roles"], "d_mod_8": r["d_mod_8"], "working_set_bytes": r["working_set_bytes"],
            "as_compiled": {"ratio": r["ratio"], "ci95": r["ci95"], "excess_ns_per_inner": r["excess_ns_per_inner"]},
            "aligned": {"ratio": a["ratio"], "ci95": a["ci95"], "excess_ns_per_inner": a["excess_ns_per_inner"]},
            "extra_instr_per_inner": ins[d]["extra_per_inner"], "instr_ratio": ins[d]["ratio"],
            "placement_d": pla[d]["d_ratio"], "placement_d_ci95": pla[d]["ci95"], "placement_sensitive": pla[d]["sensitive"]})
    return rows


def dsweep_data():
    """site/data/dsweep.json: the pooled d-sweep (results/s10-dsweep-pooled/dsweep-pooled.json, which dsweep/analyze.py
    writes from the per-job dsweep.json files; scripts/check.py re-pools them and compares) reduced to what the page prints:
    for each CPU model with at least the minimum number of jobs the word the pre-registered rule gave, the word of each
    column, the fixed share with its interval, the A/A, the d ladder and one row per d; for the others the job count.
    Nothing is computed here; the plan and criteria hashes must be those of the files as they stand."""
    path = os.path.join(REPO, DSWEEP_POOLED)
    p = load(path)
    assert p["kind"] == "dsweep-pooled" and p["schema_version"] == 1, "results/s10-dsweep-pooled has another schema"
    assert p["plan_sha256"] == sha(os.path.join(REPO, DSWEEP_PLAN)), \
        "dsweep/PLAN.md differs from the plan the d-sweep was pooled under (it must never be edited after a run)"
    assert p["criteria_sha256"] == sha(os.path.join(REPO, p["criteria_file"])), "the d-sweep was pooled under other criteria"
    assert not p["incomplete_jobs"], "a d-sweep job began and left no result"
    minimum = p["rule"]["minimum_jobs"]
    # the facts of the jobs that the pooled file does not repeat: the runner's architecture and caches, the commit that ran
    meta, per_run = {}, {}
    for i in p["inputs"]:
        d = load(os.path.normpath(os.path.join(os.path.dirname(path), i["path"])))
        assert d["plan_sha256"] == p["plan_sha256"], f"{i['path']} was run under another plan"
        run, rn = d["run"], d["run"]["runner"]
        m = meta.setdefault(i["cpu_model"], {"arch": rn["arch"], "l1d_kib": rn["l1d_kib"], "l2_kib": rn["l2_kib"], "commits": set()})
        assert (m["arch"], m["l1d_kib"], m["l2_kib"]) == (rn["arch"], rn["l1d_kib"], rn["l2_kib"]), f"{i['cpu_model']}: jobs on other machines"
        m["commits"].add(run["commit"])
        # no workflow-run address here: the served site carries none (scripts/check_site.py); the stored files keep theirs
        pr = per_run.setdefault(i["run_id"], {"run_id": i["run_id"], "jobs": 0,
                                              "models": {}, "commit": run["commit"], "started_at": run["started_at"]})
        assert pr["commit"] == run["commit"], f"run {i['run_id']}: jobs from two commits"
        pr["jobs"] += 1
        pr["models"][i["cpu_model"]] = pr["models"].get(i["cpu_model"], 0) + 1
    models, few = [], []
    for b in sorted(p["cpus"], key=lambda x: (-x["jobs"], x["cpu_model"])):
        m = meta[b["cpu_model"]]
        head = {**_repl_names(b), "arch": m["arch"], "l1d_kib": m["l1d_kib"], "l2_kib": m["l2_kib"], "commits": sorted(m["commits"]),
                "jobs": b["jobs"], "runs": len(b["runs"]), "run_ids": b["runs"]}
        if b["jobs"] < minimum:
            few.append({**head, "word": b["verdict"]["word"], "reason": b["verdict"]["reason"]})
            continue
        assert not b["problems"], f"{b['cpu_model']}: file problems in the d-sweep: {b['problems']}"
        lad = b["ladder"]
        models.append({
            **head, "word": b["verdict"]["word"], "columns_agree": b["verdict"]["columns_agree"], "reason": b["verdict"]["reason"],
            "columns": {c: _ds_column(b, c) for c in DSWEEP_COLUMNS},
            "aa": b["aa"], "published": b.get("published"),
            "ladder": {k: lad[k] for k in ("modulus", "residue", "min_d", "study_l1_d", "study_l2_d", "fit", "scan", "bridge", "mid_d")},
            "builds": {mode: {"traps": b["builds"][mode]["traps"], "elements_per_pass": b["builds"][mode]["elements_per_pass"],
                              "vectorization": b["builds"][mode]["vectorization"]["vectorized"],
                              "width": b["builds"][mode]["vectorization"].get("width"), "hot_loop": b["builds"][mode]["hot_loop"]}
                       for mode in DSWEEP_MODES},
            "placement": {k: b["placement"][k] for k in ("mechanical", "hot_none", "hot_fast", "sensitive_ds")},
            "instructions": {"label": b["instructions"]["label"], "jobs_agree": b["instructions"]["jobs_agree"],
                             "fit": b["instructions"]["fit"]},
            "rows": _ds_rows(b)})
    return {
        "note": "derived by scripts/build_site_data.py from " + DSWEEP_POOLED + " (dsweep/analyze.py writes that file from the "
                "per-job dsweep.json files; scripts/check.py re-pools them and compares); do not edit by hand. The words are the "
                "ones the rule fixed in " + DSWEEP_PLAN + " before the runs gave; instruction counts are instructions, not time.",
        "plan": DSWEEP_PLAN, "plan_sha256": p["plan_sha256"], "analysis": DSWEEP_ANALYSIS, "source": DSWEEP_POOLED,
        "source_sha256": sha(path), "table": DSWEEP_TABLE, "criteria_file": p["criteria_file"], "rule": p["rule"],
        "resamples": p["resamples"], "seed_prefix": p["seed_prefix"], "jobs": len(p["inputs"]), "line": p["line"],
        "runs": [per_run[k] for k in sorted(per_run)], "models": models, "too_few_jobs": few}


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
    # the real-program counts and the share of the biggest project, as the page's script words them (site/app.js numWord, shareWords)
    words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    prog = [r for r in rw["rows"] if not r["control"]]
    main_g = next(g for g in rw["timing"]["groups"] if g["cpu_model"] == rw["timing"]["main_cpu"])
    detected = [r for r in prog if main_g["rows"][r["row"]]["reading"] == "detectably slower"]
    share = co["census2"]["projects"][0]["lost"] / t2["lost"]
    share_words = ("about three quarters" if abs(share - 0.75) <= 0.03 else "about half" if abs(share - 0.5) <= 0.03
                   else f"{int(share * 100 + 0.5)}%")
    hwhat = {"lost": "Clang 18 could not vectorize it with the check inside.",
             "kept": "The loop keeps SIMD; the check only rides on the leftover tail.",
             }.get(hc["class"], "No SIMD in either build; the check adds work to every element.")
    # the NOVEC clause of site/app.js novecClause(): the same sentence (brief form), from the same pooled control
    pos = (pc.get("positive") or {}).get("k04_rev.L1")
    if pos and hc["as_compiled"]["ratio"] > 1:
        novec_share = 100 * (pos["ratio"] - 1) / (hc["as_compiled"]["ratio"] - 1)
        hwhat += (f" Switching SIMD off by hand costs {_fx(pos['ratio'])}× "
                  f"({'about a third' if 30 <= novec_share <= 37 else f'about {round(novec_share)}%'} of the as-compiled extra); "
                  "the rest is the compare and jump (inferred).")
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
        "avx2Short": _fx(max(hits)), "ceCompilers": f"{len({(r['family'], 'trunk' if r['version'] == 'trunk' else r['major']) for r in ce['rows']})} compiler versions ({ce['counts']['compilers']} Compiler Explorer compiler ids)",
        "rwWorkloads": words[len(prog)], "rwWorkloadsCap": words[len(prog)].capitalize(),
        "rwProjects": words[len({r["project"] for r in prog})], "rwDetect": words[len(detected)],
        "rwDetectProjects": words[len({r["project"] for r in detected})], "rwOthers": words[len(rw["timing"]["groups"]) - 1], "bigShare": share_words,
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
