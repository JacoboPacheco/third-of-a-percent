#!/usr/bin/env python3
"""The forwardt sweep: what FAST costs, in time, on six forward loops whose bound is a variable (rules: forwardt/PLAN.md).

One job builds the six sources in forwardt/kernels/ five ways each (NONE, FAST, NONE and FAST with -falign-loops=64,
and NOVEC), times them at two sizes (L1, L2) in ABBA order, pinned, and writes <out>/forwardt.json (kind "forwardt",
schema_version 1). Everything that is a rule lives in forwardt/PLAN.md and (the pooling, the bands, the outcomes) in
forwardt/analyze.py; this file builds, times and records. The statistic of a pair stored here is the within-job interval
of harness/stats.py and decides nothing.

While it runs it appends every finished cell to <out>/forwardt.partial.jsonl (removed once forwardt.json is written), so
that a job that stops or is cancelled late keeps its timings; the analysis lists such a job with the reason it stopped
and does not pool it. The other folders are <out>/asm/, <out>/remarks/ and <out>/cachegrind/.

Run on an ubuntu-24.04 or ubuntu-24.04-arm runner with clang-18, libc++-18-dev and valgrind from apt:

  python3 forwardt/sweep.py --job 1 --out out --build build/forwardt
  python3 forwardt/sweep.py --assume-caches 64,1024     # print the sizes n for a 64 KiB L1d and 1 MiB L2 and exit (no Linux needed)

WHAT IS TIMED (plan, "What is timed")
  Loops (LOOPS, table order): t01_sum_size, t02_sum_n, t03_scale_size, t04_scale_n, t05_fill_n, t06_offset. The command
  line of a binary is [n, iterations] (t06_offset: [n, iterations, off] with off = 0), see args_for().
  Builds (MODES): none, fast, none_a64, fast_a64, novec; flags from harness/run.py.
  Sizes (SIZES): n = max(64, target_bytes // BYTES_PER_ELEMENT[loop]), target_bytes = L1d // 2 or L2 // 2 (sizes_for()).
  Per cell (one loop at one size), in this order: calibrate on `none` (best of three runs at one iteration, iterations =
  clamp(round(TARGET_NS / best), 1, 10_000_000)); then the pairs compiled (A none, B fast), aligned (A none_a64, B
  fast_a64), aa (A none, B a byte-identical copy of it, hash checked right before the pair), and novec (A none, B novec)
  for t02, t04, t05, t06 when their `none` loop is vectorized. Cells are timed loop by loop, L1 before L2.
  The cell loop order is stored as `timing_order`. A pair stops the job (after the cell is saved to the partial file)
  when its two sides, or any two pairs of the cell, print different checksums.
  Secondary, instructions and not time: Cachegrind counts of kern_<loop> per call for none and fast at L1 (the one
  untimed warm-up call included in the divisor).

THE forwardt.json SCHEMA (schema_version 1; validate_doc() checks it; one example per type)
  {
   "kind": "forwardt",
   "schema_version": 1,
   "plan_sha256": "<64 hex>",              # forwardt/PLAN.md as the job's checkout held it, CRLF read as LF
   "criteria_sha256": "<64 hex>",          # harness/criteria-v3.json, CRLF read as LF
   "criteria_file": "harness/criteria-v3.json",
   "code_sha256": {"forwardt/sweep.py": "<64 hex>", "forwardt/analyze.py": "<64 hex> | missing", ...},
                                            # exactly one key per entry of CODE_FILES; "missing" for an absent file
   "smoke": false,                         # true exactly when reps_per_side != criteria v3.timing.reps_per_side
   "reps_per_side": 40,                    # int >= 1, processes per side of every pair
   "pinned_cpu": "1",                      # str, the taskset -c argument
   "target_ns_per_process": 75000000.0,    # float, harness/run.py TARGET_NS: a process of a cell lasts about
                                            # iters x (the ns per call of its samples), that is about this
   "run": {
     "id": "39000000000",                  # str: GITHUB_RUN_ID, or "local-<UTC start time>" outside Actions
     "job": "3",                           # str: the --job argument (the matrix job number)
     "attempt": 1,                         # int >= 1: GITHUB_RUN_ATTEMPT (1 outside Actions); 2 or more is a job that
                                            # "Re-run failed jobs" or "Re-run all jobs" ran again under the same run id; a value that is not a
                                            # positive integer stops the job
     "commit": "<40 hex> | null",          # GITHUB_SHA, null outside Actions
     "workflow_run_url": "<url> | null",   # <server>/<repo>/actions/runs/<id>, with /attempts/<n> added when attempt > 1
     "started_at": "2026-10-22T14:03:11Z",
     "runner": {"os": str|null, "kernel": str|null, "arch": "x86_64 | aarch64 | ...", "cpu_model": str|null,
                "cores": int, "l1d_kib": int, "l2_kib": int, "l3_kib": int|null},
     "toolchain": {"clang": "Ubuntu clang version 18.1.3 (1ubuntu1)", "libcxx_package": "libc++-18-dev <version> | null"}
   },
   "machine": {"cache_bytes": {"l1d": int, "l2": int, "l3": int|null, "llc": int}, "lscpu": str},
   "sizes": {                              # what sizes_for(machine.cache_bytes) gives; the analysis recomputes it
     "L1": {"target_bytes": int, "n": {"t01_sum_size": int, ... one key per loop}},
     "L2": {"target_bytes": int, "n": {...}}
   },
   "loop_order": ["t01_sum_size", ..., "t06_offset"],
   "timing_order": ["t01_sum_size.L1", "t01_sum_size.L2", "t02_sum_n.L1", ...],   # the 12 cells in the order timed
   "loops": {                              # one key per loop, in table order
     "t02_sum_n": {
       "source": "forwardt/kernels/t02_sum_n.cpp",
       "loop_line": 8,                     # the line of the // LOOP marker
       "function": "kern_t02_sum_n",
       "bytes_per_element": 4,
       "off": null,                        # 0 for t06_offset only
       "builds": {                         # keys none, fast, none_a64, fast_a64, novec
         "none": {
           "binary_sha256": "<64 hex>", "command": "clang++-18 -O2 ... -o build/forwardt/t02_sum_n.none forwardt/kernels/t02_sum_n.cpp",
           "traps": 0,                     # asm.count_traps of kern_<loop> (ud2 / brk #0x1 / verbose_abort calls)
           "asm_lines": 41,
           "vectorization": {"vectorized": true|false|null, "width": 2|null, "interleave": 2|null, "remarks": [str, ...]},
                                            # the LAST "vectorized loop (vectorization width: W, interleaved count: I)"
                                            # remark at the // LOOP line gives width and interleave; vectorized is true
                                            # only if that remark exists, false if other remarks exist, null if none
           "loops": [ {"start": "0x1a0", "end": "0x1c4", "bytes": 36, "start_mod64": 32, "crosses64": false, "windows64": 1,
                       "min_windows64": 1, "extra_window": false, "insns": 9, "simd": true, "innermost": true}, ... ],
                                            # harness/placement.py loops(); feed {"loops": {"none": ..., "fast": ...}} to
                                            # harness/pool.py placement_differs()
           "hot_loop": {"start", "bytes", "insns", "simd", "start_mod64", "windows64", "extra_window", "crosses64"} | null
         }, "fast": {...}, "none_a64": {...}, "fast_a64": {...}, "novec": {...}
       },
       "words": {                          # words_record(): computed from the vectorization entries only
         "compiled": {"word": "lost | narrower | kept | scalar in both | gained",
                      "direction": "smaller | larger | equal | unknown | null",   # null unless the word is narrower
                      "none": {"vectorized": bool, "width": int|null, "interleave": int|null},
                      "fast": {...}},
         "aligned": {... same with none_a64 and fast_a64 ...},
         "agree": true                     # the two words are equal
       },
       "novec_timed": true,                # the loop is in NOVEC_LOOPS and its `none` loop is vectorized
       "instr": {"size": "L1", "n": int, "args": [n, 20], "calls": 21, "none": int|null, "fast": int|null,
                 "ratio": float|null, "unit": "instructions per kernel call, not time", "note": "ok | <reason>"},
       "cells": {
         "L1": {
           "loop": "t02_sum_n", "size": "L1", "n": 8192, "working_set_bytes": 32768,
           "iters": 2500, "calibration_ns_one_call": 29000.0,
           "calibrate_args": [8192, 1], "timed_args": [8192, 2500],     # t06_offset: a third entry, 0
           "checksum": "<16 hex>",         # the one checksum every side of every pair printed (never null in a file)
           "checksum_match": true,         # every pair matched and all pairs agree with the compiled pair
           "pairs": {
             "compiled": PAIR, "aligned": PAIR, "aa": PAIR,
             "novec": PAIR | null          # null unless novec_timed
           }
         },
         "L2": {...}
       }
     }, ...
   },
   "seconds": 612.3
  }
  PAIR = {
    "a_build": "none", "b_build": "fast",   # (none, fast) compiled; (none_a64, fast_a64) aligned; (none, none_copy) aa;
                                            # (none, novec) novec
    "a_binary_sha256": "<64 hex>", "b_binary_sha256": "<64 hex>",   # aa: equal; others: the hashes in loops.<loop>.builds
    "n_per_side": 40,
    "a_ns": [float x n_per_side], "b_ns": [float x n_per_side],      # mean ns per kernel call of one process (its timed
                                            # total / iters; kernels/common.hpp prints that), in run order
    "order": "ABBAABBA...",                 # 2 * n_per_side letters; side A first in even-numbered repetitions
    "a_checksums": ["<16 hex>"], "b_checksums": ["<16 hex>"], "checksum_match": true,   # both lists are [cell.checksum]
    "ratio": 1.0012, "ci95": [lo, hi], "half_width_pct": 0.8    # within-job summary (harness/stats.py), B over A
  }

Partial file (forwardt.partial.jsonl, one JSON object per line): the first line has kind "forwardt-partial",
schema_version, plan_sha256, code_sha256, smoke, reps_per_side, run, sizes, timing_order, cells_expected (12); then
{"builds": {loop: <loops.<loop> without cells>}}; then {"starting": "<loop>.<size>"} before each cell and
{"cell": <the cell>} after it; a job that stops in code ends with {"stopped": {"reason": str, "at": "<loop>.<size>"}}.
A job that was killed leaves no "stopped" line. The "run" block of the header is the one of forwardt.json, so it carries
run.attempt too.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
# Where a run without --out writes. It lies under build/ (ignored by git), outside forwardt/ and results/, the two
# folders scripts/check.py reads: a test or smoke file left here must not look like an unrecorded measurement.
DEFAULT_OUT = os.path.join(REPO, "build", "forwardt-out")
HARNESS = os.path.join(REPO, "harness")
if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)

import asm  # noqa: E402
import cachegrind  # noqa: E402
import placement  # noqa: E402
import pool  # noqa: E402
import remarks  # noqa: E402
import run as hr  # noqa: E402  (harness/run.py: flag tables, caches, runner_info, toolchain, run_bin, pair, sh, sha256)
import stats  # noqa: E402

KIND = "forwardt"
SCHEMA_VERSION = 1
PLAN_FILE = os.path.join(HERE, "PLAN.md")
CRITERIA_FILE = "harness/criteria-v3.json"
RESULT_NAME = "forwardt.json"
PARTIAL_NAME = "forwardt.partial.jsonl"

LOOPS = ("t01_sum_size", "t02_sum_n", "t03_scale_size", "t04_scale_n", "t05_fill_n", "t06_offset")
# working-set bytes per element of n, counting every array the function takes (plan, "Sizes")
BYTES_PER_ELEMENT = {"t01_sum_size": 4, "t02_sum_n": 4, "t03_scale_size": 8, "t04_scale_n": 8, "t05_fill_n": 4,
                     "t06_offset": 8}
CONTROLS = ("t01_sum_size", "t03_scale_size")
NOVEC_LOOPS = ("t02_sum_n", "t04_scale_n", "t05_fill_n", "t06_offset")   # NOVEC is timed when their `none` loop is vectorized
OFF_LOOPS = ("t06_offset",)                                              # the loops that take <off> as a third argument
OFF = 0
SIZES = ("L1", "L2")
MODES = ("none", "fast", "none_a64", "fast_a64", "novec")
COLUMNS = ("compiled", "aligned", "aa", "novec")
PAIR_BUILDS = {"compiled": ("none", "fast"), "aligned": ("none_a64", "fast_a64"), "aa": ("none", "none_copy"),
               "novec": ("none", "novec")}
WORDS = ("lost", "narrower", "kept", "scalar in both", "gained")
ITERATION_LIMITS = (1, 10_000_000)   # the clamp of harness/run.py's calibrate
CELLS_EXPECTED = len(LOOPS) * len(SIZES)

# The files whose SHA-256 every forwardt.json stores (plan rule 13): the sweep and the analysis, the six sources,
# kernels/common.hpp, and every harness module this file imports directly or through another harness module (run.py
# imports programs, schema and verdict as well as asm, cachegrind, placement, remarks and stats; pool.py imports
# verdict). forwardt/analyze.py is hashed whether or not it exists yet ("missing" until it does). The set is broader
# than the modules on the path of a timing, so that a changed harness file shows in code_sha256 (more than dsweep does).
CODE_FILES = ("forwardt/sweep.py", "forwardt/analyze.py",
              "forwardt/kernels/t01_sum_size.cpp", "forwardt/kernels/t02_sum_n.cpp",
              "forwardt/kernels/t03_scale_size.cpp", "forwardt/kernels/t04_scale_n.cpp",
              "forwardt/kernels/t05_fill_n.cpp", "forwardt/kernels/t06_offset.cpp",
              "kernels/common.hpp",
              "harness/run.py", "harness/pool.py", "harness/stats.py", "harness/placement.py", "harness/asm.py",
              "harness/remarks.py", "harness/cachegrind.py",
              "harness/programs.py", "harness/schema.py", "harness/verdict.py")

LOOP_KEYS = ("start", "bytes", "insns", "simd", "start_mod64", "windows64", "extra_window", "crosses64")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX16 = re.compile(r"^[0-9a-f]{16}$")   # kernels/common.hpp prints the checksum as %016llx
_VEC_REMARK = re.compile(r"vectorized loop \(vectorization width: (\d+)(?:, interleaved count: (\d+))?")


# ---------------------------------------------------------------- hashes and criteria

def _lf_sha256(path):
    """sha256 of a file with CRLF read as LF (git stores LF; a Windows checkout may hold CRLF)."""
    with open(path, "rb") as f:
        raw = f.read().replace(bytes([13, 10]), bytes([10]))
    return hashlib.sha256(raw).hexdigest()


def plan_sha256(path=None):
    return _lf_sha256(path or PLAN_FILE)


def criteria_sha256():
    return _lf_sha256(os.path.join(REPO, CRITERIA_FILE))


def code_sha256():
    """{repo-relative path: sha256 (line endings read as LF)} of CODE_FILES as they stand now; "missing" for a file
    that does not exist."""
    out = {}
    for rel in CODE_FILES:
        p = os.path.join(REPO, rel)
        out[rel] = _lf_sha256(p) if os.path.exists(p) else "missing"
    return out


def criteria():
    with open(os.path.join(REPO, CRITERIA_FILE), encoding="utf-8") as f:
        return json.load(f)


def reps_per_side():
    """40, read from harness/criteria-v3.json (v3.timing.reps_per_side)."""
    return criteria()["v3"]["timing"]["reps_per_side"]


# ---------------------------------------------------------------- which attempt of the run this is

_ATTEMPT = re.compile(r"[1-9][0-9]*")


def run_attempt(environ=None):
    """GITHUB_RUN_ATTEMPT as an int of 1 or more; 1 when the variable is not set (a local run, or the first attempt).
    "Re-run failed jobs" and "Re-run all jobs" run jobs again under the same run id with attempt 2 or more; the plan lists
    a failed job and does not replace it, so the file records which attempt it came from. A value that is not a plain
    positive integer (empty, signed, spaced, fractional, zero) stops the job: guessing 1 would hide a re-run."""
    environ = os.environ if environ is None else environ
    raw = environ.get("GITHUB_RUN_ATTEMPT", "1")
    if not _ATTEMPT.fullmatch(raw):
        raise SystemExit(f"forwardt: GITHUB_RUN_ATTEMPT is {raw!r}, not a positive integer; the file records the attempt "
                         "of the run and cannot guess it")
    return int(raw)


def workflow_run_url(server, repo, run_id, attempt):
    """<server>/<repo>/actions/runs/<id>, and for a second or later attempt GitHub's address of that attempt
    (.../runs/<id>/attempts/<n>); None outside Actions (no run id)."""
    if not run_id:
        return None
    url = f"{server}/{repo}/actions/runs/{run_id}"
    return url + f"/attempts/{attempt}" if attempt > 1 else url


# ---------------------------------------------------------------- sizes and argument lists

def source_rel(loop):
    return f"forwardt/kernels/{loop}.cpp"


def kernel_function(loop):
    return "kern_" + loop


def args_for(loop, n, iterations):
    """The command line of a binary, without the program name: [n, iterations], and for t06_offset [n, iterations, 0].
    Used for the calibration call (iterations = 1), the Cachegrind call (iterations = CG_ITERS) and every timed call."""
    args = [n, iterations]
    if loop in OFF_LOOPS:
        args.append(OFF)
    return args


def target_bytes(cache):
    """Half of L1d and half of L2, as harness/run.py's main does."""
    return {"L1": cache["l1d"] // 2, "L2": cache["l2"] // 2}


def n_for_loop(loop, target):
    """harness/run.py's n_for rule for these loops: max(64, target_bytes // bytes per element of n)."""
    return max(64, target // BYTES_PER_ELEMENT[loop])


def working_set(loop, n):
    return BYTES_PER_ELEMENT[loop] * n


def sizes_for(cache):
    """{"L1": {"target_bytes": int, "n": {loop: n}}, "L2": {...}} for the cache sizes (bytes) of a machine."""
    tb = target_bytes(cache)
    return {size: {"target_bytes": tb[size], "n": {loop: n_for_loop(loop, tb[size]) for loop in LOOPS}} for size in SIZES}


# ---------------------------------------------------------------- the words

def vector_step(v):
    """Elements per pass of a vectorized build (W * I), or None when either is unknown or the loop is not vectorized."""
    if not v or v.get("vectorized") is not True or v.get("width") is None or v.get("interleave") is None:
        return None
    return v["width"] * v["interleave"]


def word(n, h):
    """The word of a loop from its NONE entry n and its FAST entry h (dicts with vectorized, width, interleave):
    lost, narrower, kept, scalar in both, gained. The rule of plan "Words per loop"; forwardn/run.py's word() is the
    same rule (tests/test_forwardt.py compares them)."""
    nv, hv = n["vectorized"] is True, h["vectorized"] is True
    if nv and not hv:
        return "lost"
    if nv and hv:
        return "kept" if (n["width"], n["interleave"]) == (h["width"], h["interleave"]) else "narrower"
    if hv:
        return "gained"
    return "scalar in both"


def direction(n, h):
    """For a narrower loop: whether FAST's elements per pass (W * I) are smaller, larger or equal ("unknown" when a
    width or an interleave count is missing); None for every other word."""
    if word(n, h) != "narrower":
        return None
    sn, sh_ = vector_step(n), vector_step(h)
    if sn is None or sh_ is None:
        return "unknown"
    return "smaller" if sh_ < sn else ("larger" if sh_ > sn else "equal")


def _vec_entry(v):
    return {"vectorized": v["vectorized"] is True, "width": v.get("width"), "interleave": v.get("interleave")}


def _word_block(none, fast):
    return {"word": word(none, fast), "direction": direction(none, fast), "none": _vec_entry(none), "fast": _vec_entry(fast)}


def words_record(builds):
    """The words of one loop from its builds record: compiled (none, fast), aligned (none_a64, fast_a64), and whether
    the two words agree. The word of the loop is the compiled one (plan, "Words per loop")."""
    comp = _word_block(builds["none"]["vectorization"], builds["fast"]["vectorization"])
    alig = _word_block(builds["none_a64"]["vectorization"], builds["fast_a64"]["vectorization"])
    return {"compiled": comp, "aligned": alig, "agree": comp["word"] == alig["word"]}


def vectorization_record(stderr_text, src, line):
    """harness/remarks.py's {"vectorized", "width", "remarks"} plus the interleave count I of the last "vectorized loop
    (vectorization width: W, interleaved count: I)" remark at the loop line (None when there is no such remark)."""
    v = remarks.vectorization(stderr_text, src, line)
    interleave = None
    for msg in v["remarks"]:
        m = _VEC_REMARK.match(msg)
        if m and m.group(2) is not None:
            interleave = int(m.group(2))
        elif m:
            interleave = None
    return {"vectorized": v["vectorized"], "width": v["width"], "interleave": interleave, "remarks": v["remarks"]}


# ---------------------------------------------------------------- build

def _rel(path):
    try:
        return hr.rel(path)
    except ValueError:   # another drive on Windows; never on the runners
        return path.replace("\\", "/")


def compile_cmd(loop, mode, out):
    """harness/run.py's compile_cmd with the source in forwardt/kernels/ (its own hard-codes kernels/<name>.cpp)."""
    return [hr.CXX] + hr.COMMON + hr.BUILD_FLAGS[mode] + hr.REMARK_FLAGS + ["-o", _rel(out), source_rel(loop)]


def _short_loop(lp):
    return {k: lp[k] for k in LOOP_KEYS}


def build_loop(loop, build_dir, out_dir):
    """Compiles one source five ways. Returns {"source", "loop_line", "builds": {mode: {...}}, "diff", "diff_aligned"}
    where each build holds the binary path, its sha256, the command, the vectorization record (with the interleave
    count), the trap count, the assembly line count and the loops of kern_<loop> (harness/placement.py). Writes the
    clang remarks to <out>/remarks/ and the assembly of kern_<loop> to <out>/asm/."""
    src = os.path.join(REPO, "forwardt", "kernels", loop + ".cpp")
    with open(src, encoding="utf-8") as f:
        line = remarks.loop_line(f.read())
    info = {"source": source_rel(loop), "loop_line": line, "builds": {}}
    fn_lines = {}
    for mode in MODES:
        out = os.path.join(build_dir, f"{loop}.{mode}")
        cmd = compile_cmd(loop, mode, out)
        r = hr.sh(cmd)
        if r.returncode != 0:
            raise SystemExit(f"forwardt: build failed {loop} {mode}:\n{r.stderr}")
        with open(os.path.join(out_dir, "remarks", f"{loop}.{mode}.txt"), "w", encoding="utf-8") as f:
            f.write(r.stderr)
        dump = hr.sh([hr.OBJDUMP, "-d", "--no-show-raw-insn", out]).stdout
        lines = asm.function_lines(dump, kernel_function(loop))
        if not lines:
            raise SystemExit(f"forwardt: {kernel_function(loop)} not found in the objdump of {out}")
        fn_lines[mode] = lines
        with open(os.path.join(out_dir, "asm", f"{loop}.{mode}.s"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        info["builds"][mode] = {"binary": out, "sha256": hr.sha256(out), "command": " ".join(cmd),
                                "vectorization": vectorization_record(r.stderr, src, line),
                                "traps": asm.count_traps(lines), "asm_lines": len(lines),
                                "loops": placement.loops(lines)}
    info["diff"] = asm.unified_diff(fn_lines["none"], fn_lines["fast"], f"{loop}.none.s", f"{loop}.fast.s")
    info["diff_aligned"] = asm.unified_diff(fn_lines["none_a64"], fn_lines["fast_a64"], f"{loop}.none_a64.s",
                                            f"{loop}.fast_a64.s")
    return info


def builds_record(info):
    """What the file stores about the five builds of a loop (no binary path)."""
    out = {}
    for mode in MODES:
        b = info["builds"][mode]
        hot = pool.hot_loop(b["loops"])
        out[mode] = {"binary_sha256": b["sha256"], "command": b["command"], "traps": b["traps"],
                     "asm_lines": b["asm_lines"], "vectorization": b["vectorization"], "loops": b["loops"],
                     "hot_loop": _short_loop(hot) if hot else None}
    return out


def loop_record(loop, info):
    """The loops.<loop> entry of the file, without its cells and instruction counts."""
    builds = builds_record(info)
    return {"source": info["source"], "loop_line": info["loop_line"], "function": kernel_function(loop),
            "bytes_per_element": BYTES_PER_ELEMENT[loop], "off": OFF if loop in OFF_LOOPS else None,
            "builds": builds, "words": words_record(builds),
            "novec_timed": loop in NOVEC_LOOPS and builds["none"]["vectorization"]["vectorized"] is True}


# ---------------------------------------------------------------- time

def calibrate(binary, loop, n, cpu):
    """The method of harness/run.py's calibrate, with the argument list of the loop: the best of three runs at one
    iteration, and iterations = round(TARGET_NS / best) clamped to 1 to 10,000,000. Returns (iterations, best ns)."""
    best = min(hr.run_bin(binary, args_for(loop, n, 1), cpu)[0] for _ in range(3))
    if best <= 0:
        raise SystemExit(f"forwardt: {os.path.basename(binary)} reported {best} ns for one iteration at n = {n}")
    lo, hi = ITERATION_LIMITS
    return max(lo, min(hi, int(round(hr.TARGET_NS / best)))), best


def instr_count(binary, loop, n, out_dir, tag):
    """Cachegrind Ir of kern_<loop> per call: the harness's method with the argument list of the loop; the divisor
    CG_ITERS + 1 counts the untimed warm-up call that every main makes. Returns (ir or None, note)."""
    if shutil.which(hr.VALGRIND) is None:
        return None, "valgrind not found"
    cg_file = os.path.join(out_dir, "cachegrind", f"{tag}.out")
    args = [str(a) for a in args_for(loop, n, hr.CG_ITERS)]
    r = hr.sh([hr.VALGRIND, "--tool=cachegrind", "--cache-sim=no", f"--cachegrind-out-file={cg_file}", binary] + args)
    if r.returncode != 0 or not os.path.exists(cg_file):
        return None, f"valgrind exited {r.returncode}: {r.stderr[-300:]}"
    with open(cg_file, encoding="utf-8", errors="replace") as f:
        ir = cachegrind.per_call(f.read(), kernel_function(loop), hr.CG_ITERS + 1)
    return (ir if ir > 0 else None), ("ok" if ir > 0 else "kern function not found in the cachegrind output")


def pair_record(a_build, b_build, shas, reps, pr, summarize):
    """One pair of the file from harness/run.py's pair() output. `shas` maps a build name (and none_copy) to its sha256."""
    s = summarize(pr["a_ns"], pr["b_ns"])
    return {"a_build": a_build, "b_build": b_build, "a_binary_sha256": shas[a_build], "b_binary_sha256": shas[b_build],
            "n_per_side": reps, "a_ns": pr["a_ns"], "b_ns": pr["b_ns"], "order": pr["order"],
            "a_checksums": pr["a_checksums"], "b_checksums": pr["b_checksums"],
            "checksum_match": bool(pr["checksum_match"]), "ratio": s["ratio"], "ci95": s["ci95"],
            "half_width_pct": s["half_width_pct"]}


def cell_checksum(pairs):
    """(checksum, ok): the single checksum the compiled pair's NONE side printed, and whether every pair matched and
    printed it (aligned, aa and novec included). A NONE side that printed more than one value has no single checksum:
    that is a mismatch as harness/run.py's pair() defines it (one value per side, equal on both), so ok is False."""
    comp = pairs["compiled"]
    ref = comp["a_checksums"]
    ok = len(ref) == 1 and all(p["checksum_match"] and p["a_checksums"] == ref and p["b_checksums"] == ref
                               for p in pairs.values() if p is not None)
    return (ref[0] if len(ref) == 1 else None), bool(ok)


def time_cell(loop, size, n, bins, shas, copy, reps, cpu, novec_timed, summarize):
    """Calibrates on `none` and times the pairs of one cell in the order compiled, aligned, aa, novec. `bins` maps a
    build name to its binary path, `copy` is the byte-identical copy of the `none` binary. The A/A's hashes are
    compared right before it is timed. Returns the cell dict of the file."""
    iters, one = calibrate(bins["none"], loop, n, cpu)
    timed = args_for(loop, n, iters)
    shas = dict(shas)
    shas["none_copy"] = hr.sha256(copy)
    pairs = {}
    for col in COLUMNS:
        a_b, b_b = PAIR_BUILDS[col]
        if col == "novec" and not novec_timed:
            pairs[col] = None
            continue
        if col == "aa" and (hr.sha256(copy) != hr.sha256(bins["none"]) or hr.sha256(bins["none"]) != shas["none"]):
            raise SystemExit(f"forwardt: the A/A copy of {loop} is not byte-identical to its NONE binary")
        pr = hr.pair(bins[a_b], copy if b_b == "none_copy" else bins[b_b], timed, reps, cpu)
        pairs[col] = pair_record(a_b, b_b, shas, reps, pr, summarize)
    ck, ok = cell_checksum(pairs)
    return {"loop": loop, "size": size, "n": n, "working_set_bytes": working_set(loop, n), "iters": iters,
            "calibration_ns_one_call": one, "calibrate_args": args_for(loop, n, 1), "timed_args": timed,
            "checksum": ck, "checksum_match": ok, "pairs": pairs}


# ---------------------------------------------------------------- the file

def append_partial(path, rec):
    """One JSON line, written and flushed at once, so that a job that stops (or is cancelled) after its first timing
    keeps every cell it finished in forwardt.partial.jsonl. The analysis lists such a job and never pools it."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
        f.flush()
        try:
            os.fsync(f.fileno())
        except OSError:
            pass


def cell_order():
    return [f"{loop}.{size}" for loop in LOOPS for size in SIZES]


def build_doc(*, smoke, reps, cpu, run, cache, lscpu, sizes, loops, seconds):
    """The forwardt.json document (schema_version 1) from its parts. The hashes of the plan, of the criteria file and of
    the code files (CODE_FILES) are those of the files as they stand when the sweep runs."""
    return {"kind": KIND, "schema_version": SCHEMA_VERSION, "plan_sha256": plan_sha256(),
            "criteria_sha256": criteria_sha256(), "criteria_file": CRITERIA_FILE, "code_sha256": code_sha256(),
            "smoke": smoke, "reps_per_side": reps, "pinned_cpu": cpu, "target_ns_per_process": hr.TARGET_NS,
            "run": run, "machine": {"cache_bytes": cache, "lscpu": lscpu}, "sizes": sizes,
            "loop_order": list(LOOPS), "timing_order": cell_order(), "loops": loops, "seconds": seconds}


def _hex(s):
    return isinstance(s, str) and _HEX64.match(s) is not None


def validate_doc(doc, reps=None):
    """Problems of a forwardt.json document against the schema above and the rules of the sweep (an empty list when it
    passes): keys and types, hashes, the sizes recomputed from the stored cache sizes, the words recomputed from the
    stored remarks, the builds named by every pair, the lengths of the samples, the ABBA order, the stored checksum values
    (one 16-hex value per cell, equal to both stored lists of every pair, besides the flags), and the smoke flag. `reps` is the repetition count the run used (default: the one the document states)."""
    p = []
    if not isinstance(doc, dict):
        return ["not a JSON object"]
    if doc.get("kind") != KIND or doc.get("schema_version") != SCHEMA_VERSION:
        p.append(f"kind/schema_version is {doc.get('kind')!r}/{doc.get('schema_version')!r}, not {KIND!r}/{SCHEMA_VERSION}")
    for key in ("plan_sha256", "criteria_sha256"):
        if not _hex(doc.get(key)):
            p.append(f"{key} is not a sha256")
    code = doc.get("code_sha256")
    if not isinstance(code, dict) or set(code) != set(CODE_FILES):
        p.append("code_sha256 does not have exactly the keys of CODE_FILES")
    elif any(not (_hex(v) or v == "missing") for v in code.values()):
        p.append("code_sha256 has a value that is neither a sha256 nor 'missing'")
    r = doc.get("reps_per_side")
    if not isinstance(r, int) or isinstance(r, bool) or r < 1:
        p.append("reps_per_side is not a positive integer")
        r = None
    elif reps is not None and r != reps:
        p.append(f"reps_per_side is {r}, not {reps}")
    if not isinstance(doc.get("smoke"), bool):
        p.append("smoke is not a boolean")
    elif r is not None and doc["smoke"] != (r != reps_per_side()):
        p.append(f"smoke is {doc['smoke']} with {r} repetitions per side (criteria: {reps_per_side()})")
    if not isinstance(doc.get("pinned_cpu"), str):
        p.append("pinned_cpu is not a string")
    run = doc.get("run")
    if not isinstance(run, dict):
        p.append("run is missing")
    else:
        for key in ("id", "job", "started_at"):
            if not isinstance(run.get(key), str) or not run.get(key):
                p.append(f"run.{key} is not a non-empty string")
        attempt = run.get("attempt")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            p.append("run.attempt is missing or not an integer of 1 or more")
        runner = run.get("runner") or {}
        for key in ("cpu_model", "arch"):
            if not isinstance(runner.get(key), str) or not runner.get(key):
                p.append(f"run.runner.{key} is missing or empty")
        if not isinstance((run.get("toolchain") or {}).get("clang"), str):
            p.append("run.toolchain.clang is missing")
    cache = (doc.get("machine") or {}).get("cache_bytes")
    sizes = doc.get("sizes")
    if not isinstance(cache, dict) or not all(isinstance(cache.get(k), int) for k in ("l1d", "l2")):
        p.append("machine.cache_bytes lacks l1d or l2")
    elif sizes != sizes_for(cache):
        p.append("sizes differ from the sizes the rule gives for the stored cache sizes")
    if doc.get("loop_order") != list(LOOPS):
        p.append("loop_order is not the six loops in table order")
    if doc.get("timing_order") != cell_order():
        p.append("timing_order is not the 12 cells loop by loop, L1 before L2")
    loops = doc.get("loops")
    if not isinstance(loops, dict) or list(loops) != list(LOOPS):
        return p + ["loops does not hold the six loops in table order"]
    for loop in LOOPS:
        p += _validate_loop(loop, loops[loop], sizes, r)
    return p


def _validate_loop(loop, rec, sizes, reps):
    p, tag = [], loop
    if rec.get("source") != source_rel(loop) or rec.get("function") != kernel_function(loop):
        p.append(f"{tag}: source or function name is wrong")
    if not isinstance(rec.get("loop_line"), int):
        p.append(f"{tag}: loop_line is not an integer")
    if rec.get("bytes_per_element") != BYTES_PER_ELEMENT[loop]:
        p.append(f"{tag}: bytes_per_element is not {BYTES_PER_ELEMENT[loop]}")
    if rec.get("off") != (OFF if loop in OFF_LOOPS else None):
        p.append(f"{tag}: off is wrong")
    builds = rec.get("builds")
    if not isinstance(builds, dict) or set(builds) != set(MODES):
        return p + [f"{tag}: builds does not have exactly the keys {list(MODES)}"]
    for m, b in builds.items():
        v = b.get("vectorization") or {}
        if not _hex(b.get("binary_sha256")) or not isinstance(b.get("traps"), int) or not isinstance(b.get("command"), str):
            p.append(f"{tag}.{m}: binary_sha256, traps or command is wrong")
        if v.get("vectorized") not in (True, False, None) or "remarks" not in v or "interleave" not in v:
            p.append(f"{tag}.{m}: the vectorization record is wrong")
        if not isinstance(b.get("loops"), list):
            p.append(f"{tag}.{m}: loops is not a list")
    if not p:
        if rec.get("words") != words_record(builds):
            p.append(f"{tag}: words differ from the words the stored remarks give")
        if rec.get("novec_timed") != (loop in NOVEC_LOOPS and builds["none"]["vectorization"]["vectorized"] is True):
            p.append(f"{tag}: novec_timed does not follow from the loop and its NONE remark")
    ins = rec.get("instr")
    if not isinstance(ins, dict) or ins.get("size") != "L1" or "none" not in ins or "fast" not in ins:
        p.append(f"{tag}: instr is wrong")
    cells = rec.get("cells")
    if not isinstance(cells, dict) or list(cells) != list(SIZES):
        return p + [f"{tag}: cells does not hold L1 and L2"]
    for size in SIZES:
        p += _validate_cell(loop, size, cells[size], builds, sizes, reps, rec.get("novec_timed"))
    return p


def _abba(order, reps):
    return order == "".join(("AB" if k % 2 == 0 else "BA") for k in range(reps))


def _validate_cell(loop, size, cell, builds, sizes, reps, novec_timed):
    p, tag = [], f"{loop}.{size}"
    n = (sizes or {}).get(size, {}).get("n", {}).get(loop) if isinstance(sizes, dict) else None
    if cell.get("loop") != loop or cell.get("size") != size or cell.get("n") != n:
        p.append(f"{tag}: loop, size or n is wrong")
    if cell.get("n") is not None and (cell.get("working_set_bytes") != working_set(loop, cell["n"])
                                      or cell.get("calibrate_args") != args_for(loop, cell["n"], 1)
                                      or cell.get("timed_args") != args_for(loop, cell["n"], cell.get("iters", 0))):
        p.append(f"{tag}: working_set_bytes or an argument list is wrong")
    if not isinstance(cell.get("iters"), int) or not (ITERATION_LIMITS[0] <= cell["iters"] <= ITERATION_LIMITS[1]):
        p.append(f"{tag}: iters is outside 1 to 10,000,000")
    if cell.get("checksum_match") is not True:
        p.append(f"{tag}: checksum_match is not true")
    ck = cell.get("checksum")
    ck_ok = isinstance(ck, str) and _HEX16.match(ck) is not None
    if not ck_ok:
        p.append(f"{tag}: checksum is not a 16-hex string (a complete file stores the one checksum every side printed)")
    pairs = cell.get("pairs")
    if not isinstance(pairs, dict) or set(pairs) != set(COLUMNS):
        return p + [f"{tag}: pairs does not have exactly the keys {list(COLUMNS)}"]
    for col in COLUMNS:
        pr = pairs[col]
        if col == "novec" and not novec_timed:
            if pr is not None:
                p.append(f"{tag}.novec: timed although novec_timed is false")
            continue
        if pr is None:
            p.append(f"{tag}.{col}: missing")
            continue
        a_b, b_b = PAIR_BUILDS[col]
        if (pr.get("a_build"), pr.get("b_build")) != (a_b, b_b):
            p.append(f"{tag}.{col}: builds are not {a_b} against {b_b}")
        a_sha = builds[a_b]["binary_sha256"]
        b_sha = builds["none" if b_b == "none_copy" else b_b]["binary_sha256"]
        if pr.get("a_binary_sha256") != a_sha or pr.get("b_binary_sha256") != b_sha:
            p.append(f"{tag}.{col}: the stored hashes are not those of the builds")
        if pr.get("n_per_side") != reps or len(pr.get("a_ns") or []) != reps or len(pr.get("b_ns") or []) != reps:
            p.append(f"{tag}.{col}: the sides do not hold {reps} samples each")
        if reps is not None and not _abba(pr.get("order"), reps):
            p.append(f"{tag}.{col}: the order is not ABBA")
        if pr.get("checksum_match") is not True:
            p.append(f"{tag}.{col}: the two sides printed different checksums")
        # the flags are not trusted alone (plan rule 7: the clause checks the stored values on reading): both sides of
        # every pair, the A/A and the NOVEC pair included, stored exactly the cell's one checksum
        if ck_ok and not (pr.get("a_checksums") == [ck] and pr.get("b_checksums") == [ck]):
            p.append(f"{tag}.{col}: the checksums stored for the two sides are not both [{ck}], the one checksum of the cell")
        if not (isinstance(pr.get("ci95"), list) and len(pr["ci95"]) == 2 and isinstance(pr.get("ratio"), float)):
            p.append(f"{tag}.{col}: ratio or ci95 is wrong")
    return p


# ---------------------------------------------------------------- the job

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--job", default="0")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--build", default=os.path.join(REPO, "build", "forwardt"))
    ap.add_argument("--reps", type=int, default=None,
                    help="processes per side (default: the criteria file's 40; any other value marks the file as a smoke file)")
    ap.add_argument("--cpu", default=os.environ.get("HARNESS_CPU", "1"))
    ap.add_argument("--no-cachegrind", action="store_true")
    ap.add_argument("--assume-caches", default=None, metavar="L1D_KIB,L2_KIB",
                    help="print the sizes n for these cache sizes and exit")
    a = ap.parse_args(argv)

    if a.assume_caches:
        try:
            l1_kib, l2_kib = (int(x) for x in a.assume_caches.split(","))
        except ValueError:
            raise SystemExit("forwardt: --assume-caches takes two integers, L1D_KIB,L2_KIB (for example 64,1024)")
        print(json.dumps(sizes_for({"l1d": l1_kib * 1024, "l2": l2_kib * 1024}), indent=1))
        return 0

    try:
        return run_sweep(a)
    except RuntimeError as e:   # harness/run.py's run_bin raises this when a kernel process fails
        raise SystemExit(f"forwardt: a timed process failed: {e}")


def run_sweep(a):
    crit_reps = reps_per_side()
    reps = crit_reps if a.reps is None else a.reps   # `is None`: --reps 0 is a value to refuse, not "unset"
    if reps < 1:
        raise SystemExit(f"forwardt: --reps must be at least 1 (got {reps}); leave it out for the criteria file's {crit_reps}")
    smoke = reps != crit_reps
    attempt = run_attempt()   # before anything is created: a value that cannot be read stops the job here
    out_dir, build_dir = os.path.abspath(a.out), os.path.abspath(a.build)
    for d in (out_dir, os.path.join(out_dir, "asm"), os.path.join(out_dir, "remarks"),
              os.path.join(out_dir, "cachegrind"), build_dir):
        os.makedirs(d, exist_ok=True)
    t0 = time.time()
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    cache = hr.caches()
    runner, lscpu = hr.runner_info(cache)
    server, repo, run_id = (os.environ.get(x) for x in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"))
    run = {"id": run_id or ("local-" + started), "job": str(a.job), "attempt": attempt,
           "commit": os.environ.get("GITHUB_SHA"), "workflow_run_url": workflow_run_url(server, repo, run_id, attempt),
           "started_at": started, "runner": runner, "toolchain": hr.toolchain()}
    sizes = sizes_for(cache)
    print(f"[runner] cpu_model: {runner['cpu_model']}  arch: {runner['arch']}  cores: {runner['cores']}  "
          f"L1d {runner['l1d_kib']} KiB  L2 {runner['l2_kib']} KiB  L3 {runner['l3_kib']} KiB", flush=True)
    print(f"[toolchain] {run['toolchain']['clang']}  {run['toolchain']['libcxx_package']}", flush=True)
    for size in SIZES:
        print(f"[sizes] {size}: target {sizes[size]['target_bytes']} B, n = " +
              ", ".join(f"{loop} {sizes[size]['n'][loop]}" for loop in LOOPS), flush=True)
    if "18.1.3" not in (run["toolchain"]["clang"] or ""):
        print(f"WARNING: the compiler is {run['toolchain']['clang']!r}, not clang 18.1.3; the analysis calls that a file "
              "problem of this CPU model.", flush=True)
    if smoke:
        print(f"WARNING: {reps} repetitions per side instead of {crit_reps}: this file is marked as a smoke file and "
              "the analysis will not call it a result.", flush=True)
    if attempt > 1:
        print(f"WARNING: this is attempt {attempt} of the run (a job run again by Re-run failed jobs or Re-run all jobs): the file is marked "
              f"run.attempt {attempt}; the plan lists a failed job and does not replace it.", flush=True)

    # the five builds of every loop
    infos, loops, bins, shas, copies = {}, {}, {}, {}, {}
    for loop in LOOPS:
        info = build_loop(loop, build_dir, out_dir)
        infos[loop] = info
        loops[loop] = loop_record(loop, info)
        bins[loop] = {m: info["builds"][m]["binary"] for m in MODES}
        shas[loop] = {m: info["builds"][m]["sha256"] for m in MODES}
        for m, path in bins[loop].items():
            if not os.path.exists(path):
                raise SystemExit(f"forwardt: the {m} binary of {loop} is missing after the build: {path}")
        with open(os.path.join(out_dir, "asm", f"{loop}.diff"), "w", encoding="utf-8") as f:
            f.write(info["diff"])
        with open(os.path.join(out_dir, "asm", f"{loop}.aligned.diff"), "w", encoding="utf-8") as f:
            f.write(info["diff_aligned"])
        w = loops[loop]["words"]
        print(f"[build] {loop}: word {w['compiled']['word']}" + (f" ({w['compiled']['direction']})" if w["compiled"]["direction"] else "")
              + f", aligned {w['aligned']['word']}, traps none {loops[loop]['builds']['none']['traps']} fast "
              f"{loops[loop]['builds']['fast']['traps']}, novec timed: {loops[loop]['novec_timed']}", flush=True)
        for m in MODES:
            v = loops[loop]["builds"][m]["vectorization"]
            hot = loops[loop]["builds"][m]["hot_loop"]
            print(f"        {m}: vectorized={v['vectorized']} width={v['width']} interleave={v['interleave']} "
                  f"hot loop={hot and (str(hot['insns']) + ' insns, simd=' + str(hot['simd']) + ', at ' + hot['start'])}", flush=True)
        if not w["agree"]:
            print(f"WARNING: {loop}: the word of the aligned pair ({w['aligned']['word']}) differs from the as-compiled "
                  f"word ({w['compiled']['word']}); the analysis calls that a file problem.", flush=True)
        # the A/A copy: the NONE binary against a byte-identical copy of itself
        copy = os.path.join(build_dir, f"{loop}.none_copy")
        shutil.copyfile(bins[loop]["none"], copy)
        shutil.copymode(bins[loop]["none"], copy)
        if hr.sha256(copy) != shas[loop]["none"]:
            raise SystemExit(f"forwardt: the A/A copy of {loop} is not byte-identical to its NONE binary")
        copies[loop] = copy

    partial = os.path.join(out_dir, PARTIAL_NAME)
    with open(partial, "w", encoding="utf-8") as f:   # the header; the cells follow as they finish
        f.write(json.dumps({"kind": KIND + "-partial", "schema_version": SCHEMA_VERSION, "plan_sha256": plan_sha256(),
                            "code_sha256": code_sha256(), "smoke": smoke, "reps_per_side": reps, "run": run,
                            "sizes": sizes, "timing_order": cell_order(), "cells_expected": CELLS_EXPECTED}) + "\n")
    append_partial(partial, {"builds": loops})

    summarize = stats.summarize
    current = None
    try:
        for loop in LOOPS:
            loops[loop]["cells"] = {}
            for size in SIZES:
                current = f"{loop}.{size}"
                t = time.time()
                append_partial(partial, {"starting": current})
                n = sizes[size]["n"][loop]
                cell = time_cell(loop, size, n, bins[loop], shas[loop], copies[loop], reps, a.cpu,
                                 loops[loop]["novec_timed"], summarize)
                append_partial(partial, {"cell": cell})   # kept even when the check below stops the job
                if not cell["checksum_match"]:
                    raise SystemExit(
                        f"forwardt: in cell {current} the pairs print different checksums ("
                        + "; ".join(f"{col}: {pr['a_checksums']} against {pr['b_checksums']}"
                                    for col, pr in cell["pairs"].items() if pr is not None)
                        + "). A build that computes something else cannot be timed against another, so the sweep stops here.")
                loops[loop]["cells"][size] = cell
                c, al, aa = cell["pairs"]["compiled"], cell["pairs"]["aligned"], cell["pairs"]["aa"]
                nv = cell["pairs"]["novec"]
                print(f"[time] {current} n={n} iters={cell['iters']} fast/none {c['ratio']:.3f} [{c['ci95'][0]:.3f}, "
                      f"{c['ci95'][1]:.3f}] aligned {al['ratio']:.3f} [{al['ci95'][0]:.3f}, {al['ci95'][1]:.3f}] "
                      f"aa {aa['ratio']:.4f} (half-width {aa['half_width_pct']:.2f}%)"
                      + (f" novec/none {nv['ratio']:.3f}" if nv else "") + f" {time.time() - t:.0f}s", flush=True)
                if size == "L1":
                    loops[loop]["instr"] = instr_record(loop, n, bins[loop], out_dir, a.no_cachegrind)
                    ins = loops[loop]["instr"]
                    print(f"[instr] {loop} L1: none {ins['none']} fast {ins['fast']} ({ins['note']})", flush=True)
        current = None
    except BaseException as e:   # a stop (checksum mismatch, a failed process, Ctrl-C) keeps what was timed
        append_partial(partial, {"stopped": {"reason": str(e) or type(e).__name__, "at": current}})
        raise

    doc = build_doc(smoke=smoke, reps=reps, cpu=a.cpu, run=run, cache=cache, lscpu=lscpu, sizes=sizes, loops=loops,
                    seconds=round(time.time() - t0, 1))
    path = os.path.join(out_dir, RESULT_NAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    probs = validate_doc(doc, reps=reps)
    if probs:
        raise SystemExit("forwardt: the file just written does not pass its own schema check:\n  " + "\n  ".join(probs))
    os.remove(partial)   # everything in it is in forwardt.json now
    print(f"[done] {CELLS_EXPECTED} cells in {doc['seconds']}s -> {path}", flush=True)
    return 0


def instr_record(loop, n, bins, out_dir, skip):
    """loops.<loop>.instr: the Cachegrind counts of none and fast at L1 (instructions, not time)."""
    rec = {"size": "L1", "n": n, "args": args_for(loop, n, hr.CG_ITERS), "calls": hr.CG_ITERS + 1, "none": None,
           "fast": None, "ratio": None, "unit": "instructions per kernel call, not time", "note": "not taken (--no-cachegrind)"}
    if skip:
        return rec
    ir_n, why_n = instr_count(bins["none"], loop, n, out_dir, f"{loop}.L1.none")
    ir_f, why_f = instr_count(bins["fast"], loop, n, out_dir, f"{loop}.L1.fast")
    rec["none"], rec["fast"] = ir_n, ir_f
    if ir_n and ir_f:
        rec["ratio"], rec["note"] = ir_f / ir_n, "ok"
    else:
        rec["note"] = f"none: {why_n}; fast: {why_f}"
    return rec


if __name__ == "__main__":
    sys.exit(main())
