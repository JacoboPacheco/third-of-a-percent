#!/usr/bin/env python3
"""The forwardt analysis: pools the forwardt.json files of forwardt/runs.json per CPU model and applies the rules of
forwardt/PLAN.md (rules 1 to 13, the predictions P0 to P6 and P2n, the outcome letters A to K). Nothing in this file
chooses a rule: the plan fixes them, and this file only carries them out.

  python3 forwardt/analyze.py                  # read forwardt/runs.json, write forwardt/results.json, print the report
  python3 forwardt/analyze.py --verify         # recompute from the stored files and compare with forwardt/results.json
  python3 forwardt/analyze.py --manifest M --base B --out O --resamples N --no-write

Input is forwardt/runs.json and nothing else (plan, "Runs: Accounting"). The folders it names are read relative to
the repository root (or --base). Output: forwardt/results.json (deterministic: sorted keys, indent 1, LF) and a text
report on stdout. With no entry in the manifest it says that no run exists and writes a results.json in which every
prediction is "not testable".

THE MANIFEST (forwardt/runs.json), schema 1
  {"schema": 1,                                 # the number 1 (a different number, a text or true is refused)
   "repository": "<owner>/<name>",              # optional, a non-empty text
   "branch": "<temporary branch>",              # a non-empty text; the five keys from here to "test_ratios_read" are
   "workflow_file": ".github/workflows/<f>",    #   REQUIRED once "entries" is not empty: the report names them
   "time_limit_minutes": 45,                    #   (plan, "Runs"); workflow_file and query are non-empty texts; the
   "query": "gh run list -R <repository> --branch <branch> --limit 200",   # time limit is a positive finite number
   "test_ratios_read": false,                   # true or false: true when any ratio of a test run was read
   "note": "<free text>",                       # optional, a non-empty text
   "entries": [ENTRY, ...]}                     # a list, in order of creation time (another order is printed as a note)
  Any other top-level key is refused. An empty manifest ({"schema": 1, "entries": []}) is valid and needs none of
  the optional keys. The folder text of an entry is used literally (no glob, no variable): the files are looked for in
  exactly that folder, relative to --base.
  ENTRY = {                                     # every key below except the last three is REQUIRED; others are refused
   "run_id": "39000000000",                     # a text of digits: the Actions run id; no two entries share one
   "runner": "ubuntu-24.04 | ubuntu-24.04-arm", # exactly one of these two labels
   "head_sha": "<40 hex>",                      # the commit the run started from: 40 lower-case hex characters
   "created_at": "2026-10-22T14:03:11Z",        # created_at of the Actions API, UTC, written exactly like this
   "class": "test | measurement",               # test: the run's repetitions per side differ from the criteria number
   "clause": "code test | Neoverse-N2 run | x86-64 run 1 | x86-64 run 2 | restart after a code fix |
              restart after a platform failure | restart after the time limit | not in the plan",
   "jobs_started": 6, "jobs_returned": 6,       # whole numbers, 0 <= jobs_returned <= jobs_started
   "not_returned": [{"job": "4", "reason": "..."}],   # a list of exactly jobs_started - jobs_returned entries, each
                                                #   with a job (text) and a reason (non-empty text)
   "folder": "results/<name> | null",           # where its forwardt.json files are stored (a non-empty text), or null
                                                #   for a run that is not stored; a measurement run with returned
                                                #   jobs needs a folder
   "reason": "<why>",                           # optional, but required (non-empty) when clause is "not in the plan"
   "time_limit_minutes": 50,                    # optional: this run's own workflow time limit (a positive finite
                                                #   number); it replaces the top-level value for this entry and the
                                                #   report prints it
   "note": "<free text>"}                       # optional
  The analysis stops with an error and writes no result when the manifest itself is malformed (every problem is named),
  when a folder named in the manifest is missing, when a file in a named folder carries a run id that the manifest does
  not list (or the id of another entry), when one job is stored twice in an entry's folder (a byte-identical copy of a
  download, or two files of one job with other content), when a file's run.commit is not the entry's head_sha, when a
  file's stored arch is not the one of the entry's runner label (aarch64 for ubuntu-24.04-arm, x86_64 for ubuntu-24.04),
  when a file's run.attempt is above 1 (the file of a re-run: the plan lists a failed job and does not replace it),
  when the number of forwardt.json files with a run id in an entry's folder differs from that entry's jobs_returned,
  when a file's run id is not an Actions run id (digits), or when a file cannot be read or is not readable JSON (a
  folder in the place of a file, a file nested too deeply).

EXIT CODES (a bad input ends in a short message on stdout and one of these codes, never a traceback; a stop names every
problem it found, each on a line of its own, and an unknown argument prints this text)
  0  done (the report printed; results.json written unless --no-write; with --verify: the stored results.json
     matches the recomputation, or no run exists and no results.json is stored, which prints "nothing to verify")
  1  --verify: a stored file has a problem, results.json differs from the recomputation, is unreadable or is
     missing, its stored resamples is not 2000, or the plan file no longer hashes to the plan hash it stores (the
     line "results.json matches the recomputation" can still be printed before the line about the plan)
  2  command line: an unknown argument, a flag without its value, --resamples not a whole number above zero,
     --verify together with --resamples, an unregistered --resamples written over forwardt/results.json (the same file
     under another spelling, such as other letter case, a link or a dot segment, is refused too), --out a directory
     (unless --verify, which reports the directory as a results.json it cannot read (1), or --no-write, which writes
     nothing) or a file that cannot be written
  3  a stop (plan, "Runs: Accounting"): the manifest or a file it names is missing, unreadable (a folder in place of the
     file, a file nested too deeply) or inconsistent; no result is written

WHAT IT WRITES (forwardt/results.json, kind "forwardt-results", schema_version 1)
  plan_sha256 / first_commit_plan_sha256 / criteria_sha256 / code_sha256 (the files as they stand now), manifest (every
  entry), manifest_summary, analysis (models, predictions per model, summaries per target, p0_grid, outcome, forward
  listing, set-aside files, partial files, notes) and analysis_without_not_in_plan (the same, without the measurement
  runs marked "not in the plan"; {"same_as_analysis": true} when no run is so marked).
"""
import glob
import hashlib
import importlib.util
import json
import math
import os
import re
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
HARNESS = os.path.join(REPO, "harness")
if HARNESS not in sys.path:
    sys.path.insert(0, HARNESS)

import pool  # noqa: E402
import stats  # noqa: E402


def _load_sweep():
    key = "forwardt_sweep"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(HERE, "sweep.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


sw = _load_sweep()

KIND = "forwardt-results"
SCHEMA_VERSION = 1
MANIFEST_SCHEMA = 1
MANIFEST_FILE = os.path.join(HERE, "runs.json")
RESULTS_FILE = os.path.join(HERE, "results.json")
# SHA-256 of forwardt/PLAN.md as the commit that first holds forwardt/PLAN.md (3ea4001 in the public repository) has it,
# line endings read as LF. It sits in code the author can edit: it is a record the author keeps and not independent
# evidence (plan, top).
FIRST_COMMIT_PLAN_SHA256 = "91a7c6a08a1307a0f04209caeea44f887418ceb5368759814bfaee79cd0a986f"

TARGET_X86 = "x86-64"
TARGET_N2 = "Neoverse-N2"
N2_MODEL = "Neoverse-N2"
UNKNOWN = "unknown"
LOOPS = sw.LOOPS
SIZES = sw.SIZES
CONTROLS = sw.CONTROLS
CODE_FILES = sw.CODE_FILES          # the hashed set is the sweep's: one list, so the two modules cannot disagree on it
TRAP_LOOPS = ("t02_sum_n", "t04_scale_n", "t05_fill_n", "t06_offset")
VARIABLE_BOUND = TRAP_LOOPS
INF = float("inf")
NOT_IN_PLAN = "not in the plan"
CLASSES = ("test", "measurement")
CLAUSES = ("code test", "Neoverse-N2 run", "x86-64 run 1", "x86-64 run 2", "restart after a code fix",
           "restart after a platform failure", "restart after the time limit")
ENTRY_REQUIRED = ("run_id", "runner", "head_sha", "created_at", "class", "clause", "jobs_started", "jobs_returned",
                  "not_returned", "folder")
ENTRY_OPTIONAL = ("reason", "note", "time_limit_minutes")
RUNNER_X86 = "ubuntu-24.04"
RUNNER_ARM = "ubuntu-24.04-arm"
RUNNER_ARCH = {RUNNER_X86: "x86_64", RUNNER_ARM: "aarch64"}     # the two runner labels of the plan and the arch each stores
TOP_OPTIONAL = ("repository", "branch", "workflow_file", "time_limit_minutes", "query", "note", "test_ratios_read")
TOP_STRINGS = ("repository", "branch", "workflow_file", "query", "note")
TOP_REQUIRED_WITH_ENTRIES = ("branch", "workflow_file", "time_limit_minutes", "query", "test_ratios_read")

PREDICTED_WORD = {
    TARGET_X86: {"t01_sum_size": "kept", "t02_sum_n": "lost", "t03_scale_size": "kept", "t04_scale_n": "narrower",
                 "t05_fill_n": "lost", "t06_offset": "lost"},
    TARGET_N2: {"t01_sum_size": "kept", "t02_sum_n": "lost", "t03_scale_size": "kept", "t04_scale_n": "kept",
                "t05_fill_n": "kept", "t06_offset": "kept"},
}
BANDS = {"P1": (0.97, 1.03), "P1_t03_x86": (0.79, 1.23), "P2": (0.97, 1.35), "P2n": (0.90, 1.35), "P3": (1.5, INF),
         "P4": (0.0, 1.30), "P5": (0.80, 1.25), "P6": (0.95, 1.15)}
PRED_TARGETS = {"P1": (TARGET_X86, TARGET_N2), "P2": (TARGET_X86,), "P2n": (TARGET_X86,), "P3": (TARGET_X86,),
                "P4": (TARGET_X86,), "P5": (TARGET_X86,), "P6": (TARGET_N2,)}
MARKED = ("P2", "P2n", "P3", "P4", "P5", "P6")      # the predictions that get "not testable (control failed)"
P5_LOOPS = ("t02_sum_n", "t05_fill_n", "t06_offset")
PRED_ORDER = ("P1", "P2", "P2n", "P3", "P4", "P5", "P6")
HEADS = ("holds", "fails", "undecided", "not testable")

ROWS = ("holds", "fails above 1.35", "fails below 0.97", "fails on both sides", "undecided or not testable")
COLS = ("holds", "fails below 1.5", "undecided", "not testable")
TABLE = {"holds": ("A", "B", "C", "C"), "fails above 1.35": ("D", "E", "F", "F"),
         "fails below 0.97": ("G", "G", "G", "G"), "fails on both sides": ("K", "K", "K", "K"),
         "undecided or not testable": ("H", "I", "J", "J")}
LETTER_TEXT = {
    "A": "P2 holds and P3 holds. The page gives each ratio with its model, size and column, and says that on each model "
         "where both are read the lost sum and the lost writes differ. It calls a sum cell 'inside the forward range' "
         "only if that cell passes rule 6.",
    "B": "P2 holds; P3 fails (at least one decidable L1 write pair is wholly below 1.5). The page gives every write "
         "ratio and interval, reports P3 as failed, names the pairs wholly below 1.5, and says for each write cell "
         "whether its interval lies below 1.5, contains 1.5 or lies at or above 1.5. A write loop costs less than 1.5x "
         "only for the cells whose interval lies below 1.5; nothing of the kind is said for the write loops as a group "
         "or carried to the census loops.",
    "C": "P2 holds; P3 undecided or not testable. The page gives each sum ratio with its model, size and column and the "
         "forward-range statement for the sum cells that pass rule 6; each write ratio with its interval and no word; "
         "it does not say that the lost sum and the lost writes differ.",
    "D": "P2 fails above 1.35 on the models and pairs named, none below 0.97, and P3 holds as in A. The page "
         "reports P2 as failed and prints the cells wholly above 1.35. It scopes its statements that forward "
         "loops cost little or stay vectorized to loops bounded by `size()`: a sentence that names its "
         "models, on the models on which the sum failed; a sentence that names none, everywhere. It reports "
         "the census count beside the cost, with its unit and method (228 lost loops, a per-function count at "
         "38 source locations, in a class assigned by a text pattern, with no knowledge of how often any of "
         "them runs, and with the share that has one of the six shapes not counted), and gives the writes as "
         "at or above 1.5x only for the cells whose interval lies at or above 1.5.",
    "E": "P2 fails above 1.35 and P3 fails. The page gives the ratios and intervals of every cell, reports both as "
         "failed, names for each prediction the models and pairs on which it failed, and draws no rule from the shape "
         "of the loop.",
    "F": "P2 fails above 1.35; P3 undecided or not testable. The page reports P2 as failed, prints the cells wholly "
         "above 1.35 and scopes its forward-loop statements to size()-bounded loops as in D; it gives each write ratio "
         "with its interval and no word.",
    "G": "P2 fails below 0.97 in the pairs named, none above: the sum is faster under FAST than under NONE by more than "
         "the band allows in those cells. The aligned column, the placement list and the novec pair are read first. "
         "The page reports the cells as measured and as a failed prediction, and gives the writes as measured under "
         "the word rule 11 gives for P3, with the cell reading of B for any interval below 1.5.",
    "H": "P2 undecided or not testable; P3 holds. The page gives each write ratio with its model, size and column and "
         "says 'at or above 1.5x' for each write cell whose interval lies at or above 1.5; each sum ratio with its "
         "interval and no word; it does not say that the lost sum and the lost writes differ.",
    "I": "P2 undecided or not testable; P3 fails. The page makes the write statements of B (every write ratio and "
         "interval, the pairs wholly below 1.5, the cell reading); each sum ratio with its interval and no word.",
    "J": "Neither is decided. The page gives all ratios with intervals and no word.",
    "K": "P2 fails on both sides (at least one pair wholly above 1.35 and at least one wholly below 0.97). The page "
         "gives each failing pair with its model, size, column, side, ratio and interval, says the prediction failed on "
         "both sides, and draws no sentence from either side about what a lost sum costs. The writes are reported as "
         "measured under the word rule 11 gives.",
}

# What the page may state about a cell of the outcome block, letter by letter (plan, outcome table). The standing rule makes
# a limit, or a word such as "cheap", an "only for a cell whose own interval meets it": a letter can only take away from
# that. A group of cells is withheld where the letter's row gives the cells "with their intervals and no word", where it
# reports them as measured against a failed prediction, or where the row says nothing of the statement. The forward-range
# statement for a sum cell is given with the sum limit: the rows that name it are A, B ("as in A") and C.
WRITE_LIMITS = ("less than 1.5x", "at or above 1.5x")
LETTER_CELLS = {      # letter: (sum limit and forward-range statement may be stated, the write limits that may be stated)
    "A": (True, WRITE_LIMITS), "B": (True, WRITE_LIMITS), "C": (True, ()),
    "D": (False, ("at or above 1.5x",)), "E": (False, ()), "F": (False, ()),
    "G": (False, WRITE_LIMITS), "H": (False, ("at or above 1.5x",)), "I": (False, WRITE_LIMITS),
    "J": (False, ()), "K": (False, WRITE_LIMITS),
}

# the problem codes of rule 7: single-file clauses first, then the clauses that compare two files of one model
CODE_SINGLE = ("plan_hash", "criteria_hash", "reps", "sizes", "checksum", "schema", "aligned_word", "clang")
CODE_CROSS = ("commit", "code_hash", "binary_hash", "traps", "remark", "cache", "n", "pair_reps", "arch")
CODE_GLOBAL = ("placeholder",)
FEW_JOBS_MAX = 5          # "with 3 to 5 jobs" of v3.pooling.few_jobs_caveat: the upper end (the lower end is minimum_jobs)
CODE_ANALYSIS = ("analysis_error",)       # the pooling of a model raised: the model is listed, not read

_RUN_ID = re.compile(r"^[0-9]+$")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA64 = re.compile(r"^[0-9a-f]{64}$")
_TIME = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_PLACEHOLDER = re.compile(r"__[A-Za-z0-9_]+__")


class ManifestError(Exception):
    """The manifest or the files it names are inconsistent: the analysis stops and writes no result."""

    def __init__(self, problems):
        self.problems = list(problems)
        super().__init__("; ".join(self.problems))


# ---------------------------------------------------------------- small helpers

def jsonable(x):
    """Recursively turns numpy scalars into numbers and non-finite floats into null."""
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return jsonable(x.tolist())
    if isinstance(x, np.generic):
        x = x.item()
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    return x


def _sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def _get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _is_time_limit(t):
    """A workflow time limit in minutes: a finite number above zero (true and false are not numbers here)."""
    if not isinstance(t, (int, float)) or isinstance(t, bool):
        return False
    try:
        return math.isfinite(t) and t > 0
    except OverflowError:       # a whole number too large to be a float is not a time limit
        return False


def _is_positive_finite(v):
    """A timing sample: a number (not a bool) that is finite and above zero. A whole number too large to be a float is not."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return False
    try:
        return math.isfinite(v) and v > 0
    except OverflowError:
        return False


def jobs_text(n):
    return f"{n} job" if n == 1 else f"{n} jobs"


def fmt_ci(st):
    """ratio (interval) (N jobs): the job count of the pooled statistic stands beside the number (plan, rule 1)."""
    if not st:
        return "no value"
    jobs = f" ({jobs_text(st['jobs'])})" if st.get("jobs") is not None else ""
    return f"{st['ratio']:.4f} ({st['ci95'][0]:.4f} to {st['ci95'][1]:.4f}){jobs}"


def band_text(band):
    lo, hi = band
    if hi == INF:
        return f"above {lo:g}"
    if lo == 0.0:
        return f"at most {hi:g}"
    return f"{lo:g} to {hi:g}"


def band_json(band):
    return {"lo": band[0], "hi": None if band[1] == INF else band[1]}


# ---------------------------------------------------------------- the manifest

def read_manifest(path=None):
    """The manifest as stored. Raises ManifestError (a stop) when the file is missing, is not a file, is not UTF-8 text or
    is not JSON."""
    path = path or MANIFEST_FILE
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except OSError as exc:
        raise ManifestError([f"cannot read the manifest {path}: {exc.strerror or exc}"])
    except ValueError as exc:                    # JSONDecodeError and UnicodeDecodeError
        raise ManifestError([f"the manifest {path} is not readable JSON: {exc}"])
    except RecursionError:                       # a file of thousands of '['
        raise ManifestError([f"the manifest {path} is not readable JSON: nested too deeply"])


def validate_manifest(m):
    """The problems of a manifest (an empty list when it is well formed)."""
    if not isinstance(m, dict):
        return ["the manifest is not a JSON object"]
    p = []
    if m.get("schema") != MANIFEST_SCHEMA or isinstance(m.get("schema"), bool):
        p.append(f"schema is {m.get('schema')!r}, not {MANIFEST_SCHEMA}")
    unknown = sorted(set(m) - {"schema", "entries"} - set(TOP_OPTIONAL))
    if unknown:
        p.append("unknown top-level key(s): " + ", ".join(unknown))
    for k in TOP_STRINGS:
        if k in m and not (isinstance(m[k], str) and m[k].strip()):
            p.append(f"{k} is not a non-empty string")
    if "time_limit_minutes" in m and not _is_time_limit(m["time_limit_minutes"]):
        p.append("time_limit_minutes is not a positive number")
    if "test_ratios_read" in m and not isinstance(m["test_ratios_read"], bool):
        p.append("test_ratios_read is not true or false")
    entries = m.get("entries")
    if not isinstance(entries, list):
        return p + ["entries is not a list"]
    missing = [k for k in TOP_REQUIRED_WITH_ENTRIES if k not in m]
    if entries and missing:
        p.append("the manifest has entries and lacks the top-level key(s) " + ", ".join(missing)
                 + " (the report names the branch, the workflow file, the time limit and the query, and says whether a test ratio was read)")
    seen = set()
    for i, e in enumerate(entries):
        tag = f"entries[{i}]"
        if not isinstance(e, dict):
            p.append(f"{tag} is not an object")
            continue
        miss = [k for k in ENTRY_REQUIRED if k not in e]
        if miss:
            p.append(f"{tag} lacks " + ", ".join(miss))
            continue
        extra = sorted(set(e) - set(ENTRY_REQUIRED) - set(ENTRY_OPTIONAL))
        if extra:
            p.append(f"{tag} has unknown key(s) " + ", ".join(extra))
        rid = e["run_id"]
        if not isinstance(rid, str) or not _RUN_ID.match(rid):
            p.append(f"{tag}.run_id {rid!r} is not a string of digits (an Actions run id)")
        elif rid in seen:
            p.append(f"{tag}.run_id {rid} is listed twice")
        else:
            seen.add(rid)
        if not (isinstance(e["runner"], str) and e["runner"] in RUNNER_ARCH):
            p.append(f"{tag}.runner {e['runner']!r} is not {RUNNER_X86} or {RUNNER_ARM}")
        if "time_limit_minutes" in e and not _is_time_limit(e["time_limit_minutes"]):
            p.append(f"{tag}.time_limit_minutes is not a positive number")
        if not isinstance(e["head_sha"], str) or not _SHA40.match(e["head_sha"]):
            p.append(f"{tag}.head_sha is not 40 hex characters")
        if not isinstance(e["created_at"], str) or not _TIME.match(e["created_at"]):
            p.append(f"{tag}.created_at is not a UTC time like 2026-10-22T14:03:11Z")
        if e["class"] not in CLASSES:
            p.append(f"{tag}.class is {e['class']!r}, not test or measurement")
        if e["clause"] != NOT_IN_PLAN and e["clause"] not in CLAUSES:
            p.append(f"{tag}.clause {e['clause']!r} is not a clause of 'Runs' or {NOT_IN_PLAN!r}")
        if e["clause"] == NOT_IN_PLAN and not (isinstance(e.get("reason"), str) and e["reason"].strip()):
            p.append(f"{tag} is marked {NOT_IN_PLAN!r} and gives no reason")
        started, returned = e["jobs_started"], e["jobs_returned"]
        if not (_is_int(started) and _is_int(returned) and 0 <= returned <= started):
            p.append(f"{tag}: jobs_started and jobs_returned must be integers with 0 <= returned <= started")
        else:
            nr = e["not_returned"]
            if not isinstance(nr, list) or len(nr) != started - returned or any(
                    not (isinstance(x, dict) and isinstance(x.get("job"), str) and isinstance(x.get("reason"), str)
                         and x["reason"]) for x in nr):
                p.append(f"{tag}.not_returned must list {started - returned} job(s), each with a job and a reason")
        if e["folder"] is not None and not (isinstance(e["folder"], str) and e["folder"]):
            p.append(f"{tag}.folder is neither null nor a non-empty string")
        if e["folder"] is None and e["class"] == "measurement" and _is_int(returned) and returned > 0:
            p.append(f"{tag}: a measurement run with returned jobs needs a folder")
    return p


def manifest_notes(m):
    """Observations on a well-formed manifest that are not stops: the order of the entries."""
    notes = []
    times = [e["created_at"] for e in m["entries"]]
    if times != sorted(times):
        notes.append("the entries are not in order of creation time")
    return notes


def run_description(m):
    """The validated top-level description of the dispatches (plan, 'Runs'): only the keys of TOP_OPTIONAL, an absent key
    is None."""
    return {k: m.get(k) for k in TOP_OPTIONAL}


def manifest_summary(m):
    entries = m["entries"]
    return {"entries": len(entries), "not_in_the_plan": sum(1 for e in entries if e["clause"] == NOT_IN_PLAN),
            "measurement": sum(1 for e in entries if e["class"] == "measurement"),
            "test": sum(1 for e in entries if e["class"] == "test"),
            "jobs_started": sum(e["jobs_started"] for e in entries),
            "jobs_returned": sum(e["jobs_returned"] for e in entries)}


# ---------------------------------------------------------------- the files of the entries

def _rel(path, base):
    return os.path.relpath(os.path.abspath(path), os.path.abspath(base)).replace("\\", "/")


def _partial_info(path, base):
    header, done, starting, stopped = {}, 0, None, None
    unreadable = None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                try:
                    rec = json.loads(ln)
                except (ValueError, RecursionError):
                    continue    # a line cut short by a killed process, or a line of thousands of '['
                if not isinstance(rec, dict):
                    continue
                if rec.get("kind") == "forwardt-partial":
                    header = rec
                elif "cell" in rec:
                    done += 1
                elif "starting" in rec:
                    starting = rec["starting"]
                elif "stopped" in rec:
                    stopped = rec["stopped"]
    except OSError as exc:      # a folder that carries the file's name, a file another program holds open
        unreadable = exc.strerror or str(exc)
    run = header.get("run") or {}
    reason = (stopped or {}).get("reason") if isinstance(stopped, dict) else None
    if unreadable is not None:
        reason = f"the file cannot be read: {unreadable}"
    return {"path": _rel(path, base), "run_id": str(run.get("id")), "job": str(run.get("job")),
            "cpu_model": _get(run, "runner", "cpu_model"), "cells_done": done,
            "cells_expected": header.get("cells_expected"), "last_started": starting,
            "reason": reason or "no 'stopped' line: the job was killed or cancelled",
            "smoke": header.get("smoke")}


def gather(manifest, base_dir):
    """Reads the files of every stored entry. Returns {"records": [...], "partial": [...]} and raises ManifestError for the
    stops of 'Runs: Accounting'. A record is {rel, doc, sha, entry}. The folder string of an entry is used literally: it is
    joined to base_dir as it stands (glob.escape keeps '*', '?' and '[' in a folder name from being read as a pattern) and the
    files are looked for in that folder and below it. A job stored twice in one folder (a download made twice) is a stop
    that names both files, whether the copy is byte-identical or not; it is looked for before the files are counted."""
    stops, records, partial = [], [], []
    listed = {e["run_id"] for e in manifest["entries"]}
    for e in manifest["entries"]:
        if e["folder"] is None:
            continue
        folder = os.path.join(base_dir, e["folder"])
        if not os.path.isdir(folder):
            stops.append(f"run {e['run_id']}: the folder {e['folder']} named in the manifest is missing")
            continue
        found = sorted(glob.glob(os.path.join(glob.escape(folder), "**", sw.RESULT_NAME), recursive=True),
                       key=lambda x: _rel(x, base_dir))
        own = []
        for p in found:
            rel = _rel(p, base_dir)
            try:
                with open(p, "rb") as fh:
                    raw = fh.read()
            except OSError as exc:      # a folder that carries the file's name, a file another program holds open
                stops.append(f"{rel}: cannot be read: {exc.strerror or exc}")
                continue
            try:
                doc = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError, RecursionError):    # RecursionError: a file of thousands of '['
                stops.append(f"{rel}: not readable JSON")
                continue
            rid = str(_get(doc, "run", "id"))
            if not _RUN_ID.match(rid):
                stops.append(f"{rel}: its run id {rid!r} is not an Actions run id")
                continue
            if rid not in listed:
                stops.append(f"{rel}: carries run id {rid}, which the manifest does not list")
                continue
            if rid != e["run_id"]:
                stops.append(f"{rel}: carries run id {rid} but lies in the folder of run {e['run_id']}")
                continue
            own.append({"rel": rel, "doc": doc, "sha": _sha256_bytes(raw), "entry": e})
        records += own
        _copy_stops(own, e, stops)
        _commit_stops(own, e, stops)
        _runner_stops(own, e, stops)
        _attempt_stops(own, e, stops)
        if len(own) != e["jobs_returned"]:
            stops.append(f"run {e['run_id']}: {len(own)} {sw.RESULT_NAME} file(s) with its run id in {e['folder']}, "
                         f"the manifest says {e['jobs_returned']} job(s) returned")
        for q in sorted(glob.glob(os.path.join(glob.escape(folder), "**", sw.PARTIAL_NAME), recursive=True),
                        key=lambda x: _rel(x, base_dir)):
            if os.path.exists(os.path.join(os.path.dirname(q), sw.RESULT_NAME)):
                continue
            info = _partial_info(q, base_dir)
            info["entry_run_id"] = e["run_id"]
            info["run_id_listed"] = info["run_id"] in listed
            partial.append(info)
    if stops:
        raise ManifestError(stops)
    return {"records": records, "partial": partial}


def _copy_stops(own, e, stops):
    """Appends to `stops` a line for every file of one entry that carries the same run id and job as an earlier file: one job
    stored twice. Two cases, both a stop that names both paths. A byte-identical second file (an artifact downloaded twice)
    is reported with the count of files against the count of distinct jobs, so that a manifest that counts files cannot hide
    a job that never returned ('6 files but 5 distinct jobs'); a second file with other content is reported as such. This runs
    before the count of files is compared with the entry's jobs_returned: that count stop (the plan's) then adds its line,
    so a run whose copy and count are both wrong shows both causes. A file with no job name is its own job."""
    first, dups, distinct = {}, [], 0
    for r in own:
        run = _dict(_dict(r["doc"]).get("run"))
        job = run.get("job")
        if not (isinstance(job, str) and job):
            distinct += 1
            continue
        key = (str(run.get("id")), job)
        if key not in first:
            first[key] = r
            distinct += 1
        else:
            dups.append((r, first[key], key, job))
    for r, f, key, job in dups:
        if f["sha"] == r["sha"]:
            stops.append(f"run {e['run_id']}: {len(own)} {sw.RESULT_NAME} files but {distinct} distinct jobs: {r['rel']} is a "
                         f"byte-identical copy of {f['rel']} (the same run id and job; remove the copy)")
        else:
            stops.append(f"{r['rel']}: carries run id {key[0]} and job {job!r} like {f['rel']}, with other content")


def _short_sha(x):
    """The first 10 characters of a commit, or the repr of whatever else a file holds (None, a number, an empty string)."""
    return x[:10] if isinstance(x, str) and x else repr(x)


def _commit_stops(own, e, stops):
    """Appends to `stops` a line for every file of one entry whose run.commit is not the entry's head_sha (compared in lower
    case; test entries and smoke files are compared too). The commit a run started from is what the manifest records and
    what every file of the run carries, so a difference means a file from another run, or a manifest line that was typed
    wrong; the line names the file and both values (their first 10 characters)."""
    want = e["head_sha"].lower()
    for r in own:
        got = _get(r["doc"], "run", "commit")
        if not (isinstance(got, str) and got.lower() == want):
            stops.append(f"{r['rel']}: its run.commit is {_short_sha(got)} but the manifest gives head_sha {want[:10]} "
                         f"for run {e['run_id']}")


def _runner_stops(own, e, stops):
    """Appends to `stops` a line for every file of one entry whose stored arch does not belong to the entry's runner label:
    ubuntu-24.04-arm stores aarch64 and ubuntu-24.04 stores x86_64 (test entries and smoke files are compared too). The
    targets of the analysis come from the stored arch, so a wrong label would only mislabel the report; it is still a stop,
    because it means the manifest line or the folder is not what the operator thinks it is."""
    want = RUNNER_ARCH.get(e["runner"])
    if want is None:        # a label the manifest check has already refused
        return
    for r in own:
        got = _get(r["doc"], "run", "runner", "arch")
        if got != want:
            stops.append(f"{r['rel']}: its stored arch is {got!r} but the manifest gives runner {e['runner']} ({want} "
                         f"expected) for run {e['run_id']}")


_NO_ATTEMPT = object()


def _attempt_of(doc):
    """The run.attempt a file stores (GitHub's run attempt, a whole number from 1): _NO_ATTEMPT when the file has none (the
    schema check of sweep.py reports that as a file problem), otherwise the stored value, whatever it is."""
    run = doc.get("run") if isinstance(doc, dict) else None
    return run.get("attempt", _NO_ATTEMPT) if isinstance(run, dict) else _NO_ATTEMPT


def _attempt_ok(a):
    return a is _NO_ATTEMPT or (_is_int(a) and a >= 1)


def _attempt_stops(own, e, stops):
    """Appends to `stops` a line for every file of one entry that a later attempt of the run wrote (run.attempt above 1). The
    plan lists a job that failed and does not replace it, so the file of a re-run is not pooled: the line says to remove it
    and to record the job as one that did not return, with the reason. A missing attempt, or one that is not a whole number
    from 1, is not a stop here; it is a schema problem of the file (file_problems)."""
    for r in own:
        a = _attempt_of(r["doc"])
        if _is_int(a) and a > 1:
            stops.append(f"{r['rel']}: it was written by attempt {a} of run {e['run_id']} (run.attempt {a}); the plan lists a "
                         f"failed job and does not replace it, so remove this file from the downloaded folder and record the "
                         f"job as one that did not return, with the reason")


def _job_key(rec):
    """(run id, length of the job name, job name, file sha256): the order of dsweep/analyze.py's _job_key, so that the
    bootstrap draws do not depend on the folder layout."""
    run = rec["doc"].get("run") if isinstance(rec["doc"], dict) else None
    run = run if isinstance(run, dict) else {}
    job = str(run.get("job"))
    return (str(run.get("id")), len(job), job, rec["sha"])


def model_key(doc):
    cpu = _get(doc, "run", "runner", "cpu_model")
    return cpu if isinstance(cpu, str) and cpu else UNKNOWN


def split_records(records, exclude_unplanned=False, plan_now=None):
    """(candidates, set_aside): rule 1. Smoke files are set aside before any file is assigned to a model; a non-smoke
    file in a test entry is set aside too. With exclude_unplanned the measurement entries marked 'not in the plan' are
    left out of the candidates (and listed as such)."""
    cands, aside = [], []
    plan_now = plan_now or sw.plan_sha256()
    for r in records:
        doc, e = r["doc"], r["entry"]
        smoke = isinstance(doc, dict) and doc.get("smoke") is True
        info = {"path": r["rel"], "run_id": e["run_id"], "job": str(_get(doc, "run", "job"))}
        if smoke:
            stored = doc.get("plan_sha256")
            info.update(reason="smoke file", reps_per_side=doc.get("reps_per_side"), stored_plan_sha256=stored,
                        plan_hash_note=None if stored == plan_now else "its stored plan hash differs from the plan as it stands")
            aside.append(info)
        elif e["class"] == "test":
            info.update(reason="non-smoke file in an entry of class test (never pooled)")
            aside.append(info)
        elif exclude_unplanned and e["clause"] == NOT_IN_PLAN:
            info.update(reason="measurement run marked 'not in the plan' (left out of this printing)")
            aside.append(info)
        else:
            cands.append(r)
    return cands, aside


# ---------------------------------------------------------------- rule 7: file problems

def plan_placeholder_problem(plan_path=None):
    """None, or the text of the line of the plan that still holds a double-underscore token in its first five lines."""
    with open(plan_path or sw.PLAN_FILE, encoding="utf-8") as f:
        head = [next(f, "") for _ in range(5)]
    for ln in head:
        if _PLACEHOLDER.search(ln):
            return ln.strip()
    return None


def _classify(msg):
    if msg.startswith("sizes differ"):
        return "sizes"
    if msg.startswith("smoke is not a boolean"):
        return "schema"
    if msg.startswith("smoke is"):
        return "reps"
    if "checksum" in msg:
        return "checksum"
    return "schema"


def file_problems(doc, ctx):
    """Rule 7, single-file clauses: [(code, text)] for one complete non-smoke file."""
    if not isinstance(doc, dict):
        return [("schema", "not a JSON object")]
    out = []
    if doc.get("plan_sha256") != ctx["plan_sha"]:
        out.append(("plan_hash", "its stored plan hash is not the hash of the plan as it stands"))
    if doc.get("criteria_sha256") != ctx["crit_sha"]:
        out.append(("criteria_hash", "its stored criteria hash is not that of harness/criteria-v3.json as it stands"))
    if doc.get("smoke") is False and doc.get("reps_per_side") != ctx["reps"]:
        out.append(("reps", f"smoke is false and repetitions per side are {doc.get('reps_per_side')!r}, not {ctx['reps']}"))
    try:
        msgs = sw.validate_doc(doc)
    except Exception as exc:   # a malformed file can break the validator itself
        msgs = [f"the schema check raised {type(exc).__name__}: {exc}"]
    for m in msgs:
        code = _classify(m)
        if code == "reps" and any(c == "reps" for c, _ in out):
            continue
        out.append((code, m))
    if not any(c == "checksum" for c, _ in out):
        bad = _checksum_problem(doc)
        if bad:
            out.append(("checksum", bad))
    out += _sample_problems(doc)
    out += _aligned_word_problems(doc)
    clang = _get(doc, "run", "toolchain", "clang")
    if not (isinstance(clang, str) and "18.1.3" in clang):
        out.append(("clang", f"its stored clang++-18 version string {clang!r} does not contain 18.1.3"))
    attempt = _attempt_of(doc)
    if not _attempt_ok(attempt):
        out.append(("schema", f"run.attempt is {attempt!r}, not a whole number of 1 or more"))
    return out


def _checksum_problem(doc):
    """A stored checksum mismatch the schema check does not name: sides of a cell that do not print one value."""
    try:
        for loop in LOOPS:
            for size in SIZES:
                cell = doc["loops"][loop]["cells"][size]
                vals = set()
                for pr in cell["pairs"].values():
                    if pr is not None:
                        vals.update(pr["a_checksums"])
                        vals.update(pr["b_checksums"])
                if len(vals) != 1 or (cell.get("checksum") is not None and cell["checksum"] not in vals):
                    return f"{loop}.{size}: the sides of the cell do not print one checksum"
    except (KeyError, TypeError, AttributeError):
        return None
    return None


def _sample_problems(doc):
    """Rule 7, schema clause: every timing sample of every pair is a finite number above zero (a bool is not a number); the
    schema check of the sweep does not look at the values."""
    out = []
    try:
        loops = doc["loops"]
        for loop in LOOPS:
            for size in SIZES:
                pairs = loops[loop]["cells"][size]["pairs"]
                for col in sw.COLUMNS:
                    pr = pairs.get(col)
                    if not isinstance(pr, dict):
                        continue
                    for side in ("a_ns", "b_ns"):
                        vals = pr.get(side)
                        if not isinstance(vals, list):
                            continue
                        bad = [v for v in vals if not _is_positive_finite(v)]
                        if bad:
                            out.append(("schema", f"{loop}.{size}.{col}.{side}: {len(bad)} timing sample(s) are not finite "
                                                  f"numbers above zero (the first is {_short(bad[0])})"))
    except (KeyError, TypeError, AttributeError):
        pass
    return out


def _aligned_word_problems(doc):
    out = []
    for loop in LOOPS:
        try:
            wr = sw.words_record(doc["loops"][loop]["builds"])
        except (KeyError, TypeError, AttributeError):
            continue
        if wr["compiled"]["word"] != wr["aligned"]["word"]:
            out.append(("aligned_word", f"{loop}: the word of the aligned pair ({wr['aligned']['word']}) differs from "
                                        f"the word of the as-compiled pair ({wr['compiled']['word']})"))
    return out


def _dict(x):
    """x when it is a JSON object, else an empty one: a stored file whose record has another type is a schema problem
    (reported by the single-file clause), and the comparison between files must not fail on it."""
    return x if isinstance(x, dict) else {}


def _len(x):
    return len(x) if isinstance(x, list) else 0


def _vec_key(b):
    v = _dict(_dict(b).get("vectorization"))
    return (v.get("vectorized"), v.get("width"), v.get("interleave"))


def cross_problems(recs, ctx):
    """Rule 7, clauses that compare two files of one model: [(code, text, file)], each file against the first."""
    out = []
    docs = [r["doc"] for r in recs]
    if len(docs) < 2 or not all(isinstance(d, dict) for d in docs):
        return out
    ref, ref_rel = docs[0], recs[0]["rel"]

    def add(code, what, i):
        out.append((code, f"{what} differs between {ref_rel} and {recs[i]['rel']}", recs[i]["rel"]))

    for i in range(1, len(docs)):
        d = docs[i]
        if _get(ref, "run", "commit") != _get(d, "run", "commit"):
            add("commit", "the stored run.commit", i)
        for key in sorted(set(_dict(ref.get("code_sha256"))) | set(_dict(d.get("code_sha256")))):
            if _dict(ref.get("code_sha256")).get(key) != _dict(d.get("code_sha256")).get(key):
                add("code_hash", f"the stored SHA-256 of {key}", i)
        if _get(ref, "machine", "cache_bytes") != _get(d, "machine", "cache_bytes"):
            add("cache", "the stored cache sizes", i)
        if ref.get("sizes") != d.get("sizes"):
            add("n", "the stored sizes n", i)
        if _get(ref, "run", "runner", "arch") != _get(d, "run", "runner", "arch"):
            add("arch", "the stored arch", i)
        for loop in LOOPS:
            lr, ld = _dict(_dict(ref.get("loops")).get(loop)), _dict(_dict(d.get("loops")).get(loop))
            for mode in sw.MODES:
                br, bd = _dict(_dict(lr.get("builds")).get(mode)), _dict(_dict(ld.get("builds")).get(mode))
                if br.get("binary_sha256") != bd.get("binary_sha256"):
                    add("binary_hash", f"the stored binary SHA-256 of {loop}.{mode}", i)
                if br.get("traps") != bd.get("traps"):
                    add("traps", f"the stored trap count of {loop}.{mode}", i)
                if _vec_key(br) != _vec_key(bd):
                    add("remark", f"the remark stored for {loop}.{mode}", i)
            for size in SIZES:
                cr = _dict(_dict(_dict(lr.get("cells")).get(size)).get("pairs"))
                cd = _dict(_dict(_dict(ld.get("cells")).get(size)).get("pairs"))
                for col in sw.COLUMNS:
                    pr, pd = cr.get(col), cd.get(col)
                    if (pr is None) != (pd is None) or (pr is not None and (
                            _dict(pr).get("n_per_side") != _dict(pd).get("n_per_side")
                            or _len(_dict(pr).get("a_ns")) != _len(_dict(pd).get("a_ns"))
                            or _len(_dict(pr).get("b_ns")) != _len(_dict(pd).get("b_ns")))):
                        add("pair_reps", f"the repetitions of {loop}.{size}.{col}", i)
    return out


def model_problems(recs, ctx):
    """Every file problem of one model's files: [{code, text, file}]; a placeholder in the plan applies to all."""
    out = []
    for r in recs:
        for code, text in file_problems(r["doc"], ctx):
            out.append({"code": code, "text": text, "file": r["rel"]})
    for code, text, rel in cross_problems(recs, ctx):
        out.append({"code": code, "text": text, "file": rel})
    if ctx.get("placeholder"):
        out.append({"code": "placeholder", "file": None,
                    "text": "the line of the plan that states the time of fixing still holds a placeholder: "
                            + ctx["placeholder"]})
    return out


# ---------------------------------------------------------------- targets, words

def target_of(cpu, archs):
    """Rule 1: 'Neoverse-N2' when the model is exactly Neoverse-N2 and every job stores aarch64; 'x86-64' when every job
    stores x86_64; any other model belongs to no target. `archs` is the list of the arch of every job (None if missing)."""
    if not archs:
        return None
    if cpu == N2_MODEL and all(a == "aarch64" for a in archs):
        return TARGET_N2
    if all(a == "x86_64" for a in archs):
        return TARGET_X86
    return None


def cell_decidable(jobs_returning, aa_half_width_pct, minimum, ceiling):
    """Rule 4: at least `minimum` jobs returned the cell and its pooled aa half-width is at most the ceiling."""
    return jobs_returning >= minimum and aa_half_width_pct is not None and aa_half_width_pct <= ceiling


def forward_test(aligned, aa_half_width_pct, crit):
    """Rule 6 for a decidable cell: pooled aligned ratio <= point limit and aligned ci95_hi <= 1 + max(floor, multiplier
    x the aa half-width) / 100."""
    limit = 1.0 + max(crit["floor"], crit["multiplier"] * aa_half_width_pct) / 100.0
    return {"inside": bool(aligned["ratio"] <= crit["point"] and aligned["ci95"][1] <= limit),
            "point_limit": crit["point"], "ci_hi_limit": limit}


# ---------------------------------------------------------------- rules 8 and 9: bands, pairs, judgement

def band_state(ci, band):
    """Rule 8: 'inside' (ci95_lo >= lower edge and ci95_hi <= upper edge), 'below' (ci95_hi < lower edge), 'above'
    (ci95_lo > upper edge), else 'straddle'."""
    lo_e, hi_e = band
    lo, hi = ci
    if lo >= lo_e and hi <= hi_e:
        return "inside"
    if hi < lo_e:
        return "below"
    if lo > hi_e:
        return "above"
    return "straddle"


def pair_state(s1, s2):
    """Rule 9: inside when both columns are inside; below / above when both are outside on that same side; else split."""
    if s1 == "inside" and s2 == "inside":
        return "inside"
    if s1 == s2 and s1 in ("below", "above"):
        return s1
    return "split"


def judge(states):
    """Rule 9 on the states of the decidable combinations or pairs: holds, fails, undecided, or not testable (none)."""
    if not states:
        return "not testable"
    if any(s in ("below", "above") for s in states):
        return "fails"
    if all(s == "inside" for s in states):
        return "holds"
    return "undecided"


def combos(pred, target):
    """The combinations a prediction names on a target: [(loop, size, columns, band, mode)]. 'single' combinations have
    one column; 'pair' combinations have the two columns read as a pair (rule 9). P5 is handled apart."""
    out = []
    if pred == "P1":
        for size in SIZES:
            for col in ("compiled", "aligned"):
                out.append(("t01_sum_size", size, (col,), BANDS["P1"], "single"))
        for size in SIZES:
            if target == TARGET_X86:
                out.append(("t03_scale_size", size, ("aligned",), BANDS["P1_t03_x86"], "single"))
            else:
                for col in ("compiled", "aligned"):
                    out.append(("t03_scale_size", size, (col,), BANDS["P1"], "single"))
    elif pred == "P2":
        for size in SIZES:
            out.append(("t02_sum_n", size, ("compiled", "aligned"), BANDS["P2"], "pair"))
    elif pred == "P2n":
        for size in SIZES:
            out.append(("t02_sum_n", size, ("novec",), BANDS["P2n"], "single"))
    elif pred == "P3":
        for loop in ("t05_fill_n", "t06_offset"):
            out.append((loop, "L1", ("compiled", "aligned"), BANDS["P3"], "pair"))
    elif pred == "P4":
        for size in SIZES:
            out.append(("t04_scale_n", size, ("aligned",), BANDS["P4"], "single"))
    elif pred == "P6":
        for loop in ("t05_fill_n", "t06_offset"):
            for size in SIZES:
                for col in ("compiled", "aligned"):
                    out.append((loop, size, (col,), BANDS["P6"], "single"))
    return out


# ---------------------------------------------------------------- pooling one model

def _pairs_of(docs, loop, size, col):
    out = []
    for d in docs:
        pr = d["loops"][loop]["cells"][size]["pairs"].get(col)
        if pr is not None:
            out.append((pr["a_ns"], pr["b_ns"]))
    return out


def _clean(st):
    """The stored form of a pool.py statistic."""
    return {"ratio": st["ratio"], "ci95": [st["ci95"][0], st["ci95"][1]], "half_width_pct": st["half_width_pct"],
            "jobs": st["jobs"], "between_job_sd_pct": st["between_job_sd_pct"], "per_job": list(st["per_job"]),
            "contains_one": bool(st["ci95"][0] <= 1.0 <= st["ci95"][1])}


def joint_quotient(cpu, loop, column, docs, resamples=pool.RESAMPLES):
    """Rule 10: the pooled L2 ratio divided by the pooled L1 ratio of one column of one lost loop, over all jobs. In
    each resample the same drawn jobs serve both sizes (job draws from the stat id forwardt|<loop>|<column>|joint, stream
    jobs); each size redraws its repetitions under its own stat id of rule 2. Interval: positions 50 and 1949 of 2000."""
    J = len(docs)
    job_idx = pool.draws(pool.seed_for(cpu, f"forwardt|{loop}|{column}|joint", "jobs"), (resamples, J), J)
    rstar, point = {}, {}
    for size in SIZES:
        pairs = _pairs_of(docs, loop, size, column)
        sid = f"forwardt|{loop}|{size}|{column}"
        ma = pool._side_medians(cpu, sid, 0, job_idx, [a for a, _ in pairs])
        mb = pool._side_medians(cpu, sid, 1, job_idx, [b for _, b in pairs])
        rstar[size] = np.exp(np.mean(np.log(mb / ma), axis=1))
        logs = [math.log(statistics.median(b) / statistics.median(a)) for a, b in pairs]
        point[size] = math.exp(math.fsum(logs) / J)
    q = rstar["L2"] / rstar["L1"]
    lo, hi = stats.percentile_interval(sorted(float(x) for x in q))
    return {"quotient": point["L2"] / point["L1"], "ci95": [lo, hi], "l1": point["L1"], "l2": point["L2"], "jobs": J}


def analyse_model(cpu, recs, ctx, resamples):
    """Everything about one CPU model: files, file problems, target, the pooled statistics of every loop and size, the
    words, the traps, the placement statistic and hot loops (rule 12)."""
    docs = [r["doc"] for r in recs]
    archs = [_get(d, "run", "runner", "arch") if isinstance(d, dict) else None for d in docs]
    problems = model_problems(recs, ctx)
    target = target_of(cpu, archs) if cpu != UNKNOWN else None
    J = len(recs)
    plan_stored = [d.get("plan_sha256") if isinstance(d, dict) else None for d in docs]
    notes = {"plan_differs_from_current": [r["rel"] for r, s in zip(recs, plan_stored) if s != ctx["plan_sha"]],
             "plan_differs_from_first_commit": [r["rel"] for r, s in zip(recs, plan_stored) if s != FIRST_COMMIT_PLAN_SHA256],
             "code_files_changed_since_run": []}
    code_now = ctx.get("code_now") or {}
    if docs and isinstance(docs[0], dict) and isinstance(docs[0].get("code_sha256"), dict) and code_now:
        notes["code_files_changed_since_run"] = sorted(k for k, v in docs[0]["code_sha256"].items() if code_now.get(k) != v)
    block = {"cpu_model": cpu, "target": target, "jobs": J, "runs": sorted({r["entry"]["run_id"] for r in recs}),
             "files": [r["rel"] for r in recs], "arch": sorted({str(a) for a in archs}), "problems": problems,
             "hash_notes": notes, "pooled": False, "read": False, "reason_not_read": None, "few_jobs_caveat": None,
             "loops": {}}
    if cpu == UNKNOWN:
        block["reason_not_read"] = "files with no cpu_model: listed, not pooled"
        return block
    if problems:
        block["reason_not_read"] = "file problem: every prediction on this model is not testable"
        return block
    block["pooled"] = True
    block["read"] = J >= ctx["minimum"]
    if block["read"] and J <= FEW_JOBS_MAX:
        block["few_jobs_caveat"] = ctx["few_jobs_caveat"]
    if not block["read"]:
        block["reason_not_read"] = f"{J} job(s), fewer than the minimum of {ctx['minimum']}"
    for loop in LOOPS:
        first = docs[0]["loops"][loop]
        wr = sw.words_record(first["builds"])
        lb = {"word": wr["compiled"]["word"], "direction": wr["compiled"]["direction"], "words": wr,
              "traps": {m: first["builds"][m]["traps"] for m in sw.MODES},
              "vectorization": {m: {"vectorized": first["builds"][m]["vectorization"]["vectorized"] is True,
                                    "width": first["builds"][m]["vectorization"].get("width"),
                                    "interleave": first["builds"][m]["vectorization"].get("interleave")} for m in sw.MODES},
              "novec_timed": bool(first.get("novec_timed")),
              "instr": [{"none": d["loops"][loop]["instr"].get("none"), "fast": d["loops"][loop]["instr"].get("fast")}
                        for d in docs],
              "cells": {}}
        cell_for_hot = {"loops": {"none": first["builds"]["none"]["loops"], "fast": first["builds"]["fast"]["loops"]}}
        try:
            differs, hn, hf = pool.placement_differs(cell_for_hot)
        except (KeyError, TypeError, ValueError):
            differs, hn, hf = None, None, None
        lb["hot_loops"] = {"none": pool._short(hn) if hn else None, "fast": pool._short(hf) if hf else None,
                           "any_differs": differs}
        for size in SIZES:
            cell = {"n": first["cells"][size]["n"], "pairs": {}, "jobs": J}
            for col in ("compiled", "aligned", "aa", "novec"):
                pairs = _pairs_of(docs, loop, size, col)
                if not pairs:
                    cell["pairs"][col] = None
                    continue
                cell["pairs"][col] = _clean(pool.pair_stat(cpu, f"forwardt|{loop}|{size}|{col}", pairs, resamples))
            quads = [(d["loops"][loop]["cells"][size]["pairs"]["compiled"]["a_ns"],
                      d["loops"][loop]["cells"][size]["pairs"]["compiled"]["b_ns"],
                      d["loops"][loop]["cells"][size]["pairs"]["aligned"]["a_ns"],
                      d["loops"][loop]["cells"][size]["pairs"]["aligned"]["b_ns"]) for d in docs]
            cell["placement"] = _clean(pool.placement_stat(cpu, f"forwardt|{loop}|{size}|placement", quads, resamples))
            aa_hw = cell["pairs"]["aa"]["half_width_pct"]
            cell["aa_half_width_pct"] = aa_hw
            cell["decidable"] = cell_decidable(J, aa_hw, ctx["minimum"], ctx["aa_ceiling"])
            cell["forward"] = forward_test(cell["pairs"]["aligned"], aa_hw, ctx["forward"]) if cell["decidable"] else None
            lb["cells"][size] = cell
        lb["p5"] = {}
        if (target == TARGET_X86 and loop in P5_LOOPS and lb["word"] == "lost"
                and all(lb["cells"][s]["decidable"] for s in SIZES)):
            for col in ("compiled", "aligned"):
                q = joint_quotient(cpu, loop, col, docs, resamples)
                q["state"] = band_state(q["ci95"], BANDS["P5"])
                lb["p5"][col] = q
        block["loops"][loop] = lb
    return block


# ---------------------------------------------------------------- predictions on a model

def _cell_view(m, loop, size, col):
    st = m["loops"][loop]["cells"][size]["pairs"].get(col)
    return st


def _item(m, loop, size, cols, band, mode):
    cell = m["loops"][loop]["cells"][size]
    views = {}
    for col in cols:
        st = _cell_view(m, loop, size, col)
        views[col] = {"ratio": st["ratio"], "ci95": list(st["ci95"]), "contains_one": st["contains_one"],
                      "state": band_state(st["ci95"], band), "jobs": st["jobs"]}
    if len(cols) == 2:
        state = pair_state(views[cols[0]]["state"], views[cols[1]]["state"])
    else:
        state = views[cols[0]]["state"]
    return {"loop": loop, "size": size, "columns": views, "mode": mode, "band": band_json(band),
            "aa_half_width_pct": cell["aa_half_width_pct"], "state": state, "jobs": cell["jobs"]}


def p0_state(m, target, loop):
    """P0.<loop> on one model: not testable (fewer than 3 jobs or a file problem); else holds when the word is the
    predicted one and, where the trap clause applies, the common FAST trap count is at least 1; else fails."""
    predicted = PREDICTED_WORD[target][loop]
    rec = {"loop": loop, "predicted_word": predicted, "trap_clause": loop in TRAP_LOOPS, "observed_word": None,
           "direction": None, "fast_traps": None, "word_ok": None, "trap_ok": None}
    if not m["read"]:
        rec.update(state="not testable", reason=m["reason_not_read"])
        return rec
    lb = m["loops"][loop]
    rec.update(observed_word=lb["word"], direction=lb["direction"], fast_traps=lb["traps"]["fast"])
    rec["word_ok"] = lb["word"] == predicted
    rec["trap_ok"] = (lb["traps"]["fast"] >= 1) if rec["trap_clause"] else True
    rec["state"] = "holds" if rec["word_ok"] and rec["trap_ok"] else "fails"
    return rec


def predict_model(m):
    """The state of every prediction on one model of a target (not for a model with no target): P0 per loop, then P1,
    then the control-failed mark, then P2, P2n, P3, P4, P5, P6 where they are stated for its target."""
    target = m["target"]
    out = {"P0": {loop: p0_state(m, target, loop) for loop in LOOPS}}
    out["control_failed"] = None
    out["preds"] = {}

    def one(pred):
        if not m["read"]:
            return {"state": "not testable", "reason": m["reason_not_read"], "items": [], "left_out": [], "not_decidable": []}
        if pred in MARKED and out["control_failed"]:
            return {"state": "not testable (control failed)", "reason": out["control_failed"], "items": [],
                    "left_out": [], "not_decidable": []}
        if pred == "P5":
            return _p5(m)
        wanted = combos(pred, target)
        named = sorted({c[0] for c in wanted}, key=LOOPS.index)
        have = [lp for lp in named if m["loops"][lp]["word"] == PREDICTED_WORD[target][lp]]
        left = [lp for lp in named if lp not in have]
        if not have:
            return {"state": "not testable", "reason": "no loop it names has the predicted word here", "items": [],
                    "left_out": left, "not_decidable": []}
        items, undec = [], []
        for loop, size, cols, band, mode in wanted:
            if loop not in have:
                continue
            if not m["loops"][loop]["cells"][size]["decidable"]:
                undec.append({"loop": loop, "size": size, "aa_half_width_pct": m["loops"][loop]["cells"][size]["aa_half_width_pct"]})
                continue
            if any(_cell_view(m, loop, size, c) is None for c in cols):
                continue
            items.append(_item(m, loop, size, cols, band, mode))
        state = judge([i["state"] for i in items])
        rec = {"state": state, "items": items, "left_out": left, "not_decidable": undec}
        if state == "not testable":
            rec["reason"] = "no combination it names is decidable"
        sides = sorted({i["state"] for i in items if i["state"] in ("below", "above")})
        rec["fail_sides"] = sides if state == "fails" else []
        rec["split_items"] = sum(1 for i in items if i["state"] == "split")
        return rec

    out["preds"]["P1"] = one("P1")
    p1 = out["preds"]["P1"]
    if m["read"]:
        wrong = [lp for lp in CONTROLS if m["loops"][lp]["word"] != PREDICTED_WORD[target][lp]]
        if p1["state"] == "fails":
            out["control_failed"] = "P1 fails on this model"
        elif wrong:
            out["control_failed"] = "the control " + ", ".join(wrong) + " does not have its predicted word"
    for pred in PRED_ORDER[1:]:
        out["preds"][pred] = one(pred) if target in PRED_TARGETS[pred] else None
    return out


def _p5(m):
    items, left, undec = [], [], []
    for loop in P5_LOOPS:
        lb = m["loops"][loop]
        if lb["word"] != "lost":
            left.append(loop)
            continue
        if not lb["p5"]:
            undec.append({"loop": loop, "size": "L1+L2", "aa_half_width_pct": max(lb["cells"][s]["aa_half_width_pct"] for s in SIZES)})
            continue
        views = {c: {"ratio": lb["p5"][c]["quotient"], "ci95": list(lb["p5"][c]["ci95"]), "state": lb["p5"][c]["state"],
                     "l1": lb["p5"][c]["l1"], "l2": lb["p5"][c]["l2"], "jobs": lb["p5"][c]["jobs"]} for c in ("compiled", "aligned")}
        items.append({"loop": loop, "size": "L2/L1", "columns": views, "mode": "pair", "band": band_json(BANDS["P5"]),
                      "state": pair_state(views["compiled"]["state"], views["aligned"]["state"]),
                      "jobs": views["compiled"]["jobs"]})
    if not items and len(left) == len(P5_LOOPS):
        return {"state": "not testable", "reason": "no loop it names has the predicted word here", "items": [],
                "left_out": left, "not_decidable": undec}
    state = judge([i["state"] for i in items])
    rec = {"state": state, "items": items, "left_out": left, "not_decidable": undec,
           "fail_sides": sorted({i["state"] for i in items if i["state"] in ("below", "above")}) if state == "fails" else [],
           "split_items": sum(1 for i in items if i["state"] == "split")}
    if state == "not testable":
        rec["reason"] = "no loop it names has both sizes decidable"
    return rec


# ---------------------------------------------------------------- rule 11: summary for a target

def coverage_text(state, decided, undec):
    """Rule 9: a word resting on fewer combinations than the prediction names is printed with them ("holds at L1; L2 not
    decidable"). decided and undec are lists of {loop, size, ...}."""
    at = ", ".join(f"{d['loop']} {d['size']}" for d in decided)
    nd = ", ".join(f"{u['loop']} {u['size']}" for u in undec)
    return (f"{state} at {at}; " if at else f"{state}; ") + f"{nd} not decidable"


def summary_row(cpu, rec):
    """The row summarize_target reads for one model: the state, what was left out, the combinations the state rests on
    (loop and size of every item) and the ones that were not decidable."""
    return {"cpu_model": cpu, "state": rec["state"], "left_out": rec.get("left_out"),
            "decided": [{"loop": i["loop"], "size": i["size"]} for i in rec.get("items", [])],
            "not_decidable": [dict(u) for u in rec.get("not_decidable", [])]}


def summarize_target(rows):
    """rows: [{cpu_model, state, left_out}] for the models of one target (summary_row also gives decided and
    not_decidable). The readable models are those with state holds, fails or undecided; a model marked control failed is
    outside N. `coverage` names, per readable model, the combinations that were not decidable, with the sentence of rule 9."""
    readable = [r for r in rows if r["state"] in ("holds", "fails", "undecided")]
    failed = [r["cpu_model"] for r in readable if r["state"] == "fails"]
    undec = [r["cpu_model"] for r in readable if r["state"] == "undecided"]
    n = len(readable)
    if n == 0:
        state, word = "not testable", "not testable"
    elif failed:
        state, word = "fails", "fails on at least one"
    elif undec:
        state, word = "undecided", "undecided"
    else:
        state, word = "holds", f"holds on all {n} readable models"
    coverage = {r["cpu_model"]: {"state": r["state"], "decided": list(r.get("decided") or []),
                                 "not_decidable": list(r["not_decidable"]),
                                 "text": coverage_text(r["state"], r.get("decided") or [], r["not_decidable"])}
                for r in readable if r.get("not_decidable")}
    return {"state": state, "word": word, "n_readable": n, "readable": [r["cpu_model"] for r in readable],
            "failed_on": failed, "undecided_on": undec,
            "not_testable_on": [{"cpu_model": r["cpu_model"], "state": r["state"]} for r in rows if r["state"] not in ("holds", "fails", "undecided")],
            "left_out": {r["cpu_model"]: r["left_out"] for r in rows if r.get("left_out")},
            "coverage": coverage}


# ---------------------------------------------------------------- outcomes

def p2_row(models_p2):
    """The row of the outcome table from the P2 records of the x86-64 models on which P2 is read: (row, sides)."""
    rows = [(m, rec) for m, rec in models_p2 if rec["state"] in ("holds", "fails", "undecided")]
    if not rows:
        return "undecided or not testable", []
    summary = summarize_target([{"cpu_model": m, "state": rec["state"], "left_out": rec.get("left_out")} for m, rec in models_p2])
    if summary["state"] == "holds":
        return "holds", []
    if summary["state"] == "fails":
        sides = sorted({i["state"] for _, rec in rows for i in rec["items"] if i["state"] in ("below", "above")})
        if sides == ["above"]:
            return "fails above 1.35", sides
        if sides == ["below"]:
            return "fails below 0.97", sides
        return "fails on both sides", sides
    return "undecided or not testable", []


def p3_column(summary):
    return {"holds": "holds", "fails": "fails below 1.5", "undecided": "undecided", "not testable": "not testable"}[summary["state"]]


def letter_for(row, column):
    return TABLE[row][COLS.index(column)]


def cell_permission(letter, column):
    """What the page may state about the cells of the outcome block under this letter. `column` is the P3 column: G and K
    state the writes "under the word rule 11 gives", which is no word where P3 is undecided or not testable."""
    sum_ok, writes = LETTER_CELLS[letter]
    if letter in ("G", "K") and column in ("undecided", "not testable"):
        writes = ()
    if sum_ok:
        why_sum = None
    elif letter in ("H", "I", "J"):
        why_sum = (f"letter {letter}: P2 is undecided or not testable, and the row gives each sum ratio with its interval "
                   "and no word")
    else:
        why_sum = (f"letter {letter}: P2 failed, and the row reports the sum cells as measured and states no limit and no "
                   "forward-range word for them")
    if writes:
        why_writes = None
        why_cut = (f"letter {letter}: only 'at or above 1.5x' is stated for a write cell") if len(writes) < len(WRITE_LIMITS) else None
    else:
        why_cut = None
        if letter == "E":
            why_writes = ("letter E: the row gives the ratios and intervals of every cell, reports both predictions as failed "
                          "and draws no rule from the shape of the loop, and states no limit for a write cell")
        elif letter == "J":
            why_writes = "letter J: neither prediction is decided, and the row gives all ratios with intervals and no word"
        elif letter in ("G", "K"):
            why_writes = (f"letter {letter}: P3 is {column}, so the writes are reported as measured under the word rule 11 "
                          "gives, which is none")
        else:
            why_writes = (f"letter {letter}: P3 is undecided or not testable, and the row gives each write ratio with its "
                          "interval and no word")
    return {"letter": letter, "p3_column": column, "sum": sum_ok, "write_limits": list(writes),
            "why_sum": why_sum, "why_writes": why_writes, "why_writes_cut": why_cut}


def gate_cell(perm, loop, ungated, inside):
    """(limits, why limits are None or cut, inside_forward_range, why it is None) for one cell: what `cell_limits` and the
    forward flag of an aligned sum cell (`inside`, None where it does not apply) give, cut down to what the letter permits.
    None, with the reason, is a statement withheld; an empty list is a cell whose own interval meets no limit."""
    if loop == "t02_sum_n":
        if perm["sum"]:
            return list(ungated), None, inside, None
        return None, perm["why_sum"], None, (perm["why_sum"] if inside is not None else None)
    if not perm["write_limits"]:
        return None, perm["why_writes"], None, None
    kept = [x for x in ungated if x in perm["write_limits"]]
    return kept, (perm["why_writes_cut"] if len(kept) != len(ungated) else None), None, None


def cell_limits(loop, ci):
    """Rule of the outcomes: a limit may be stated only for a cell whose own interval meets it."""
    out = []
    if loop == "t02_sum_n" and ci[1] <= 1.35:
        out.append("at most 1.35x")
    if loop in ("t05_fill_n", "t06_offset"):
        if ci[1] < 1.5:
            out.append("less than 1.5x")
        if ci[0] >= 1.5:
            out.append("at or above 1.5x")
    return out


def outcome(models):
    """The outcome letter for x86-64 from the P2 and P3 summaries, with the cells every sentence may use."""
    x86 = [m for m in models if m["target"] == TARGET_X86]
    recs_p2 = [(m["cpu_model"], m["pred"]["preds"]["P2"]) for m in x86]
    recs_p3 = [(m["cpu_model"], m["pred"]["preds"]["P3"]) for m in x86]
    sum_p3 = summarize_target([summary_row(c, r) for c, r in recs_p3])
    sum_p2 = summarize_target([summary_row(c, r) for c, r in recs_p2])
    row, sides = p2_row(recs_p2)
    col = p3_column(sum_p3)
    letter = letter_for(row, col)
    read = ("holds", "fails", "undecided")
    p2_read = [c for c, r in recs_p2 if r["state"] in read]
    p3_read = [c for c, r in recs_p3 if r["state"] in read]
    both = [c for c in p2_read if c in p3_read]
    perm = cell_permission(letter, col)
    cells = []
    for m in x86:
        for loop, sizes in (("t02_sum_n", SIZES), ("t05_fill_n", ("L1",)), ("t06_offset", ("L1",))):
            if not m["read"] or m["pred"]["control_failed"]:
                continue
            lb = m["loops"][loop]
            for size in sizes:
                cell = lb["cells"][size]
                if not cell["decidable"]:
                    continue
                for col_ in ("compiled", "aligned"):
                    st = cell["pairs"][col_]
                    inside = cell["forward"]["inside"] if loop == "t02_sum_n" and col_ == "aligned" else None
                    limits, lwhy, fwd, fwhy = gate_cell(perm, loop, cell_limits(loop, st["ci95"]), inside)
                    cells.append({"cpu_model": m["cpu_model"], "loop": loop, "size": size, "column": col_,
                                  "word": lb["word"], "ratio": st["ratio"], "ci95": list(st["ci95"]), "jobs": st["jobs"],
                                  "limits": limits, "limits_withheld": lwhy,
                                  "inside_forward_range": fwd, "forward_range_withheld": fwhy})
    return {"letter": letter, "row": row, "column": col, "p2_fail_sides": sides, "text": LETTER_TEXT[letter],
            "p2_read_models": p2_read, "p3_read_models": p3_read, "both_read_models": both,
            "may_say_lost_sum_and_lost_writes_differ": letter == "A" and bool(both),
            "p3_summary": sum_p3, "partial_coverage": {"P2": sum_p2["coverage"], "P3": sum_p3["coverage"]},
            "cell_permission": perm, "cells": cells}


def forward_listing(models):
    """The standing listing: for each of the four variable-bound loops, each model, each decidable aligned cell with its
    pooled ratio, interval and whether it is inside the forward range; a loop with no decidable cell is listed as having none.
    A model marked "control failed" is listed with the mark (the plan makes the listing whatever the ratios are)."""
    out = []
    for m in models:
        for loop in VARIABLE_BOUND:
            rows = []
            if m["pooled"] and m["read"]:
                for size in SIZES:
                    cell = m["loops"][loop]["cells"][size]
                    if cell["decidable"]:
                        st = cell["pairs"]["aligned"]
                        rows.append({"size": size, "ratio": st["ratio"], "ci95": list(st["ci95"]), "jobs": st["jobs"],
                                     "inside_forward_range": cell["forward"]["inside"], "aa_half_width_pct": cell["aa_half_width_pct"]})
            out.append({"cpu_model": m["cpu_model"], "loop": loop, "decidable_aligned_cells": rows,
                        "none_decidable": not rows, "control_failed": (m.get("pred") or {}).get("control_failed")})
    return out


# ---------------------------------------------------------------- the whole analysis

def forward_rule_text(crit):
    """Rule 6 in words, printed beside every 'inside the forward range': it has no lower bound, so 'inside' does not say
    'close to 1'. crit is ctx["forward"]."""
    return (f"pooled aligned ratio at most {crit['point']:g} and interval upper end at most 1 + max({crit['floor']:g}%, "
            f"{crit['multiplier']:g} x A/A half-width); no lower bound")


def make_ctx(plan_path=None, code_now=None, plan_sha=None):
    """plan_sha and code_now are given by --verify, which recomputes with the hashes a results.json stored."""
    crit = sw.criteria()
    v, v3 = crit["verdict"], crit["v3"]
    return {"plan_sha": plan_sha or sw.plan_sha256(plan_path), "crit_sha": sw.criteria_sha256(), "reps": v3["timing"]["reps_per_side"],
            "minimum": v3["pooling"]["minimum_jobs"], "aa_ceiling": v["aa_half_width_max_pct"],
            "few_jobs_caveat": v3["pooling"]["few_jobs_caveat"],
            "forward": {"point": v["forward_point_max_ratio"], "floor": v["forward_ci_hi_floor_pct"],
                        "multiplier": v["forward_ci_hi_aa_multiplier"]},
            "placeholder": plan_placeholder_problem(plan_path),
            "code_now": sw.code_sha256() if code_now is None else code_now}


def failed_model(cpu, recs, exc):
    """The block of a model whose analysis raised: a file problem of its own, nothing pooled, every prediction not
    testable; the other models are analysed as usual."""
    try:
        archs = [_get(r["doc"], "run", "runner", "arch") if isinstance(r["doc"], dict) else None for r in recs]
        target = target_of(cpu, archs) if cpu != UNKNOWN else None
    except Exception:
        archs, target = [], None
    text = f"the analysis of this model raised {type(exc).__name__}: {exc}"
    return {"cpu_model": cpu, "target": target, "jobs": len(recs), "runs": sorted({r["entry"]["run_id"] for r in recs}),
            "files": [r["rel"] for r in recs], "arch": sorted({str(a) for a in archs}),
            "problems": [{"code": "analysis_error", "file": None, "text": text}],
            "hash_notes": {"plan_differs_from_current": [], "plan_differs_from_first_commit": [],
                           "code_files_changed_since_run": []},
            "pooled": False, "read": False, "reason_not_read": "file problem: every prediction on this model is not testable",
            "few_jobs_caveat": None, "loops": {}}


def analyse_files(cands, aside, partial, ctx, resamples):
    groups = {}
    for r in cands:
        groups.setdefault(model_key(r["doc"]), []).append(r)
    models = []
    for cpu in sorted(groups):
        recs = sorted(groups[cpu], key=_job_key)
        try:
            m = analyse_model(cpu, recs, ctx, resamples)
        except (ValueError, ZeroDivisionError, AttributeError, KeyError, TypeError, OverflowError) as exc:
            m = failed_model(cpu, recs, exc)
        if m["target"] is not None:
            m["pred"] = predict_model(m)
        else:
            m["pred"] = None
        models.append(m)
    # the placeholder in the plan makes a "file problem of every model": with no model there is nothing to mark
    summaries = {}
    for target in (TARGET_X86, TARGET_N2):
        tm = [m for m in models if m["target"] == target]
        summ = {"models": [m["cpu_model"] for m in tm], "jobs": {m["cpu_model"]: m["jobs"] for m in tm}, "P0": {}, "preds": {}}
        for loop in LOOPS:
            s = summarize_target([{"cpu_model": m["cpu_model"], "state": m["pred"]["P0"][loop]["state"]} for m in tm])
            s["predicted_word"] = PREDICTED_WORD[target][loop]
            s["trap_clause"] = loop in TRAP_LOOPS
            s["models"] = [{"cpu_model": m["cpu_model"], "jobs": m["jobs"], "observed_word": m["pred"]["P0"][loop]["observed_word"],
                            "direction": m["pred"]["P0"][loop]["direction"],
                            "fast_traps": m["pred"]["P0"][loop]["fast_traps"], "state": m["pred"]["P0"][loop]["state"]}
                           for m in tm]
            summ["P0"][loop] = s
        for pred in PRED_ORDER:
            if target not in PRED_TARGETS[pred]:
                continue
            s = summarize_target([summary_row(m["cpu_model"], m["pred"]["preds"][pred]) for m in tm])
            s["marked_control_failed"] = [m["cpu_model"] for m in tm if m["pred"]["control_failed"]]
            s["undecided_resting_on_split"] = sum(
                1 for m in tm if m["pred"]["preds"][pred]["state"] == "undecided" and m["pred"]["preds"][pred].get("split_items"))
            summ["preds"][pred] = s
        summaries[target] = summ
    x86_models = [m for m in models if m["target"] == TARGET_X86]
    oc = outcome(models)
    notes = []
    if ctx.get("placeholder"):
        notes.append("the plan's time line still holds a placeholder: a file problem of every model")
    stale = sorted({m["cpu_model"] for m in models if m["hash_notes"]["plan_differs_from_first_commit"]})
    if stale:
        notes.append("a stored plan hash differs from FIRST_COMMIT_PLAN_SHA256 on: " + ", ".join(stale)
                     + " (a note that flags a mismatch; it does not show when a change was made)")
    for m in models:
        for k in ("plan_differs_from_current", "code_files_changed_since_run"):
            if m["hash_notes"][k]:
                notes.append(f"{m['cpu_model']}: {k.replace('_', ' ')}: " + ", ".join(m["hash_notes"][k]))
    for a in aside:
        if a.get("plan_hash_note"):
            notes.append(f"{a['path']}: smoke file, {a['plan_hash_note']} (decides nothing)")
    return {"resamples": resamples, "few_jobs": {"minimum": ctx["minimum"], "maximum": FEW_JOBS_MAX, "caveat": ctx["few_jobs_caveat"]},
            "forward_rule": dict(ctx["forward"], text=forward_rule_text(ctx["forward"])),
            "models": models, "summaries": summaries, "outcome": oc,
            "forward_listing": forward_listing(models), "set_aside": aside, "partial": partial, "notes": notes,
            "reported_n2_t02": reported_n2_t02(models),
            "x86_models": [m["cpu_model"] for m in x86_models]}


def reported_n2_t02(models):
    """t02_sum_n on a Neoverse-N2 model, reported without a band (P5 and P6 do not test it there): its word and the ratios of
    both columns and every size. A model below the 3-job minimum is not read (rule 1): it is listed with `read` false and no
    word and no ratio."""
    out = []
    for m in models:
        if m["target"] != TARGET_N2 or not m["pooled"]:
            continue
        rec = {"cpu_model": m["cpu_model"], "jobs": m["jobs"], "read": m["read"], "word": None, "cells": None}
        if m["read"]:
            lb = m["loops"]["t02_sum_n"]
            rec["word"] = lb["word"]
            rec["cells"] = {s: {c: (lb["cells"][s]["pairs"][c] or {}).get("ratio") for c in ("compiled", "aligned")} for s in SIZES}
        out.append(rec)
    return out


def entry_files(manifest, records, main_an):
    """For every entry of the manifest, in its order: how many forwardt.json files were read from its folder and how many of
    those jobs went into the pool of a CPU model (a model with a file problem pools none). The report prints the pooled
    count beside the manifest's own count, so that a job that was read but not pooled shows. `commit` is the commit the
    files of the entry say they were run from (first 10 characters; a file that disagrees with the manifest's head_sha is a
    stop, so by the time this is built they all agree), None for an entry with no file."""
    pooled = {rel for m in main_an["models"] if m["pooled"] for rel in m["files"]}
    out = []
    for e in manifest["entries"]:
        mine = [r for r in records if r["entry"]["run_id"] == e["run_id"]]
        said = sorted({_short_sha(str(_get(r["doc"], "run", "commit")).lower()) for r in mine})
        out.append({"run_id": e["run_id"], "files": len(mine), "pooled": sum(1 for r in mine if r["rel"] in pooled),
                    "commit": ",".join(said) if said else None})
    return out


def analyse(manifest, base_dir, resamples=pool.RESAMPLES, plan_path=None, code_now=None, plan_sha=None):
    """The whole analysis; raises ManifestError for a malformed manifest or for the stops of 'Runs: Accounting'."""
    probs = validate_manifest(manifest)
    if probs:
        raise ManifestError(probs)
    got = gather(manifest, base_dir)
    ctx = make_ctx(plan_path, code_now, plan_sha)
    cands, aside = split_records(got["records"], plan_now=ctx["plan_sha"])
    main_an = analyse_files(cands, aside, got["partial"], ctx, resamples)
    unplanned = [e for e in manifest["entries"] if e["clause"] == NOT_IN_PLAN and e["class"] == "measurement"]
    if unplanned:
        cands2, aside2 = split_records(got["records"], exclude_unplanned=True, plan_now=ctx["plan_sha"])
        second = analyse_files(cands2, aside2, got["partial"], ctx, resamples)
    else:
        second = {"same_as_analysis": True}
    return {"kind": KIND, "schema_version": SCHEMA_VERSION, "plan_sha256": ctx["plan_sha"],
            "first_commit_plan_sha256": FIRST_COMMIT_PLAN_SHA256, "criteria_sha256": ctx["crit_sha"],
            "code_sha256": ctx["code_now"], "manifest": manifest["entries"], "manifest_summary": manifest_summary(manifest),
            "entry_files": entry_files(manifest, got["records"], main_an),
            "manifest_notes": manifest_notes(manifest), "run_description": run_description(manifest),
            "no_run": not manifest["entries"],
            "analysis": main_an, "analysis_without_not_in_plan": second}


def strip(an_all):
    """The stored form: model blocks keep their numbers; nothing else is removed."""
    return jsonable(an_all)


# ---------------------------------------------------------------- the report

def _states_line(rec):
    return rec["state"] + (f" ({rec.get('reason')})" if rec.get("reason") else "")


def _caveat_lines(an, cpus):
    """One line naming the models, among `cpus`, that have 3 to 5 jobs, with the sentence of criteria-v3 (the statistics of a
    later section stand away from their model's own block)."""
    few = [m for m in an["models"] if m["cpu_model"] in cpus and m.get("few_jobs_caveat")]
    if not few:
        return []
    return ["   caveat for " + ", ".join(f"{m['cpu_model']} ({jobs_text(m['jobs'])})" for m in few) + ": " + an["few_jobs"]["caveat"]]


CONTAINS_ONE = "interval contains 1.00 (indistinguishable from no cost at this noise)"      # rule 8


def _spans_one(ci):
    return bool(ci[0] <= 1.0 <= ci[1])


def _cells_text(p):
    """How many cells a partial file recorded: 'n of N cells', or, for a file with no header (the number expected is not
    stored), the cells it did record."""
    done, expected = p["cells_done"], p["cells_expected"]
    if expected is None:
        return "no cell recorded" if not done else f"{done} cell{'' if done == 1 else 's'} recorded (the number expected is not stored)"
    return f"{done} of {expected} cells"


def render_analysis(an, title):
    L = [f"== {title} =="]
    if not an["models"]:
        L.append("no CPU model has a file: every prediction is not testable")
    for m in an["models"]:
        L.append(f"[model] {m['cpu_model']}: target {m['target'] or 'none'}, {m['jobs']} job(s), runs {', '.join(m['runs'])}"
                 + ("" if m["read"] else f"; NOT READ: {m['reason_not_read']}"))
        for p in m["problems"]:
            L.append(f"   file problem [{p['code']}] {p['file'] or ('model' if p['code'] in CODE_ANALYSIS else 'plan')}: {p['text']}")
        for k, v in m["hash_notes"].items():
            if v:
                L.append(f"   note {k.replace('_', ' ')}: {', '.join(v)}")
        if m.get("few_jobs_caveat"):
            L.append(f"   caveat ({jobs_text(m['jobs'])}): {m['few_jobs_caveat']}")
        if not m["pooled"]:
            continue
        for loop in LOOPS:
            lb = m["loops"][loop]
            w = lb["word"] + (f" ({lb['direction']})" if lb["direction"] else "")
            L.append(f"   {loop}: word {w}; FAST traps {lb['traps']['fast']}; hot loop differs: {lb['hot_loops']['any_differs']}")
            for size in SIZES:
                c = lb["cells"][size]
                bits = [f"{col} {fmt_ci(c['pairs'][col])}" for col in ("compiled", "aligned", "novec") if c["pairs"].get(col)]
                one = "; ".join(f"{col}: {CONTAINS_ONE}"
                                for col in ("compiled", "aligned", "aa", "novec")
                                if c["pairs"].get(col) and c["pairs"][col]["contains_one"])
                L.append(f"      {size} n={c['n']}: " + "; ".join(bits) + f"; aa half-width {c['aa_half_width_pct']:.3f}%; "
                         f"D {fmt_ci(c['placement'])}; {'decidable' if c['decidable'] else 'NOT decidable'}"
                         + (f"; forward range: {'inside' if c['forward']['inside'] else 'outside'}" if c["forward"] else "")
                         + (f"; {one}" if one else ""))
        if m["pred"] is not None:
            for loop in LOOPS:
                r = m["pred"]["P0"][loop]
                L.append(f"   P0.{loop}: {r['state']}; observed {r['observed_word']}, predicted {r['predicted_word']}, FAST traps {r['fast_traps']}")
            if m["pred"]["control_failed"]:
                L.append(f"   MARKED control failed: {m['pred']['control_failed']}")
            for pred in PRED_ORDER:
                r = m["pred"]["preds"][pred]
                if r is None:
                    continue
                L.append(f"   {pred}: {_states_line(r)}" + (f"; left out {', '.join(r['left_out'])}" if r.get("left_out") else ""))
                for it in r["items"]:
                    cols = "; ".join(f"{c} {v['ratio']:.4f} ({v['ci95'][0]:.4f} to {v['ci95'][1]:.4f}) ({jobs_text(v['jobs'])}) {v['state']}"
                                     for c, v in it["columns"].items())
                    tag = " columns disagree" if it["state"] == "split" else ""
                    L.append(f"      {it['loop']} {it['size']}: {it['state']}{tag}: {cols}")
                for u in r.get("not_decidable", []):
                    L.append(f"      {u['loop']} {u['size']}: not decidable (aa half-width {u['aa_half_width_pct']:.3f}%)")
    for target, s in an["summaries"].items():
        names = ", ".join(c + " (" + jobs_text(s["jobs"][c]) + ")" for c in s["models"]) or "none"
        L.append(f"-- {target} (models: {names})")
        for loop in LOOPS:
            p = s["P0"][loop]
            L.append(f"   P0.{loop}: {p['word']} (predicted {p['predicted_word']}): " + ("; ".join(
                f"{x['cpu_model']} {x['observed_word']} traps {x['fast_traps']}" for x in p["models"]) or "no model of this target"))
        for pred, p in s["preds"].items():
            extra = ""
            if p["failed_on"]:
                extra += f"; failed on {', '.join(p['failed_on'])}"
            if p["marked_control_failed"]:
                extra += f"; control failed: {', '.join(p['marked_control_failed'])}"
            if p["undecided_resting_on_split"]:
                extra += f"; {p['undecided_resting_on_split']} undecided on a split pair"
            if p["left_out"]:
                extra += "; left out " + "; ".join(f"{k}: {', '.join(v)}" for k, v in p["left_out"].items())
            L.append(f"   {pred}: {p['word']}{extra}")
            for cpu, c in p["coverage"].items():
                L.append(f"      partial coverage on {cpu}: {c['text']}")
    oc = an["outcome"]
    L.append(f"-- outcome (x86-64): letter {oc['letter']} (P2 row: {oc['row']}; P3 column: {oc['column']})")
    L.append("   " + oc["text"])
    L.append(f"   lost sum and lost writes differ may be said: {oc['may_say_lost_sum_and_lost_writes_differ']} "
             f"(models where both are read: {', '.join(oc['both_read_models']) or 'none'})")
    for pred_ in ("P2", "P3"):
        for cpu, c in oc["partial_coverage"][pred_].items():
            L.append(f"   partial coverage {pred_} on {cpu}: {c['text']}")
    L += _caveat_lines(an, {c["cpu_model"] for c in oc["cells"]})
    if any(c["inside_forward_range"] is not None or c["forward_range_withheld"] for c in oc["cells"]):
        L.append("   inside the forward range (rule 6): " + an["forward_rule"]["text"])
    for c in oc["cells"]:
        if c["limits"] is None:
            lim = f"; no limit stated ({c['limits_withheld']})"
        elif c["limits"]:
            lim = f"; limit: {', '.join(c['limits'])} (word {c['word']})"
        else:
            lim = "; no limit stated"
        if c["limits"] is not None and c["limits_withheld"]:
            lim += f"; a further limit is withheld ({c['limits_withheld']})"
        if c["inside_forward_range"] is not None:
            fr = f"; inside the forward range: {c['inside_forward_range']}"
        elif c["forward_range_withheld"]:
            fr = f"; inside the forward range: not stated ({c['forward_range_withheld']})"
        else:
            fr = ""
        L.append(f"   {c['cpu_model']} {c['loop']} {c['size']} {c['column']}: {c['ratio']:.4f} ({c['ci95'][0]:.4f} to {c['ci95'][1]:.4f})"
                 f" ({jobs_text(c['jobs'])})" + lim + fr + (f"; {CONTAINS_ONE}" if _spans_one(c["ci95"]) else ""))
    L.append("-- the four variable-bound loops, decidable aligned cells (the standing listing; the loops measured elsewhere are "
             "bounded by size())")
    L += _caveat_lines(an, {r["cpu_model"] for r in an["forward_listing"] if r["decidable_aligned_cells"]}
                       | {r["cpu_model"] for r in an["reported_n2_t02"]})
    if any(r["decidable_aligned_cells"] for r in an["forward_listing"]):
        L.append("   inside the forward range (rule 6): " + an["forward_rule"]["text"])
    marked = None
    for r in an["forward_listing"]:
        if r.get("control_failed") and r["cpu_model"] != marked:
            marked = r["cpu_model"]
            L.append(f"   {r['cpu_model']}: MARKED control failed: {r['control_failed']}")
        if r["none_decidable"]:
            L.append(f"   {r['cpu_model']} {r['loop']}: no decidable cell")
        for c in r["decidable_aligned_cells"]:
            L.append(f"   {r['cpu_model']} {r['loop']} {c['size']}: {c['ratio']:.4f} ({c['ci95'][0]:.4f} to {c['ci95'][1]:.4f}) "
                     f"({jobs_text(c['jobs'])}); inside the forward range: {c['inside_forward_range']}"
                     + (f"; {CONTAINS_ONE}" if _spans_one(c["ci95"]) else ""))
    for r in an["reported_n2_t02"]:
        if not r["read"]:
            L.append(f"   t02_sum_n on {r['cpu_model']}: not read ({jobs_text(r['jobs'])}, fewer than the minimum of "
                     f"{an['few_jobs']['minimum']})")
            continue
        L.append(f"   t02_sum_n on {r['cpu_model']} (word {r['word']}, reported without a band, {jobs_text(r['jobs'])}): {r['cells']}")
    for a in an["set_aside"]:
        tail = ""
        if a.get("reps_per_side") is not None or a.get("stored_plan_sha256") is not None:
            tail = f" (repetitions per side {a.get('reps_per_side')}; stored plan hash {a.get('stored_plan_sha256')})"
        L.append(f"[set aside] {a['path']}: {a['reason']}{tail}")
    for p in an["partial"]:
        if p["run_id"] == "None":
            # no id to look up in the manifest: say which entry's folder the file lies in instead of calling it unlisted
            rid = "no run id stored in the file"
            where = p.get("entry_run_id")
            listed = f"; it lies in the folder of run {where}" if where else ""
        else:
            rid = f"run id {p['run_id']}"
            listed = "" if p.get("run_id_listed", True) else "; the manifest does not list this run id"
        L.append(f"[partial] {p['path']}: {_cells_text(p)}; {p['reason']}; not pooled; {rid}{listed}")
    for n in an["notes"]:
        L.append(f"[note] {n}")
    return L


def render_description(d, has_entries):
    """The lines that name the temporary branch, the workflow file and its time limit, the query that lists the same runs,
    and say whether a ratio of a test run was read (plan, 'Runs'). Nothing is printed for an empty manifest without keys."""
    if not has_entries and all(v is None for v in d.values()):
        return []
    t = d.get("test_ratios_read")
    return [f"dispatches: repository {d['repository'] or 'not stated'}; temporary branch {d['branch'] or 'not stated'}; "
            f"workflow file {d['workflow_file'] or 'not stated'}; workflow time limit "
            + (f"{d['time_limit_minutes']:g} minutes" if d["time_limit_minutes"] is not None else "not stated"),
            f"   query that lists the same runs: {d['query'] or 'not stated'}",
            "   " + ("a ratio of a test run was read" if t is True else "no ratio of a test run was read" if t is False
                     else "whether a ratio of a test run was read: not stated")] + (
        [f"   note: {d['note']}"] if d.get("note") else [])


def entry_limit_text(e, top):
    """The workflow time limit that applies to one entry, for its '[run]' line: the entry's own value when it has one (and,
    when that differs from the top-level value, both are named), otherwise the top-level value."""
    own = e.get("time_limit_minutes")
    if own is None:
        return f"time limit {top:g} minutes" if top is not None else "time limit not stated"
    if top is None or own != top:
        return f"time limit this entry: {own:g} minutes (top-level: {'not stated' if top is None else f'{top:g}'})"
    return f"time limit {own:g} minutes"


def render_report(res):
    L = []
    ms = res["manifest_summary"]
    L.append(f"forwardt analysis: {ms['entries']} manifest entr{'y' if ms['entries'] == 1 else 'ies'}, "
             f"{ms['not_in_the_plan']} marked '{NOT_IN_PLAN}'; plan sha256 {res['plan_sha256']}")
    if res["no_run"]:
        L.append("no run exists: every prediction is not testable")
    L += render_description(res["run_description"], bool(res["manifest"]))
    top_limit = res["run_description"].get("time_limit_minutes")
    for e, ef in zip(res["manifest"], res["entry_files"]):
        L.append(f"[run] {e['run_id']} {e['created_at']} {e['runner']} {e['head_sha'][:10]} class {e['class']}; {e['clause']}"
                 + (f" ({e['reason']})" if e["clause"] == NOT_IN_PLAN else "")
                 + f"; {entry_limit_text(e, top_limit)}"
                 + f"; jobs {e['jobs_returned']}/{e['jobs_started']} ({ef['pooled']} pooled)"
                 + (f"; files say {ef['commit']}" if ef["commit"] else "") + f"; folder {e['folder']}")
        for nr in e["not_returned"]:
            L.append(f"      job {nr['job']} did not return: {nr['reason']}")
        if e.get("note"):
            L.append(f"      note: {e['note']}")
    for n in res["manifest_notes"]:
        L.append(f"[note] {n}")
    L += render_analysis(res["analysis"], "all measurement runs")
    L.append("")
    sec = res["analysis_without_not_in_plan"]
    if sec.get("same_as_analysis"):
        L.append(f"== without runs marked '{NOT_IN_PLAN}' == no measurement run is so marked: the result is the one above")
    else:
        L += render_analysis(sec, f"without the measurement runs marked '{NOT_IN_PLAN}'")
    return "\n".join(L)


# ---------------------------------------------------------------- verification

def verify_file(doc, resamples=stats.RESAMPLES):
    """Problems of one forwardt.json: the schema, then every stored within-job ratio, interval and half-width recomputed
    from its raw samples (harness/stats.py, as sweep.py stored them)."""
    probs = list(sw.validate_doc(doc))
    if probs:
        return probs
    for loop in LOOPS:
        for size in SIZES:
            for col, pr in doc["loops"][loop]["cells"][size]["pairs"].items():
                if pr is None:
                    continue
                lo, hi = stats.bootstrap_ratio_ci(pr["a_ns"], pr["b_ns"], resamples=resamples)
                ratio = stats.ratio_of_medians(pr["a_ns"], pr["b_ns"])
                if pr["ratio"] != ratio or list(pr["ci95"]) != [lo, hi] or pr["half_width_pct"] != stats.half_width_pct((lo, hi)):
                    probs.append(f"{loop}.{size}.{col}: the stored ratio, ci95 or half_width_pct is not what the samples give")
    return probs


FLOAT_REL_TOL = 1e-9
FLOAT_ABS_TOL = 1e-12


def _same_scalar(a, b):
    """Floats are equal when they agree to FLOAT_REL_TOL relative or FLOAT_ABS_TOL absolute (a recomputation on another
    machine or numpy build may differ in the last bits); every other value, the words and letters among them, exactly."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and (isinstance(a, float) or isinstance(b, float)):
        try:
            return math.isclose(a, b, rel_tol=FLOAT_REL_TOL, abs_tol=FLOAT_ABS_TOL)
        except OverflowError:           # a whole number too large to be a float: no tolerance applies, compare exactly
            return a == b
    return a == b


SHORT_REPR = 80


def _short(x):
    """repr(x), cut to SHORT_REPR characters (a stored text or a 400-digit number does not fill a line)."""
    t = repr(x)
    return t if len(t) <= SHORT_REPR else t[:SHORT_REPR - 3] + "..."


def diff_paths(a, b, path="", out=None, limit=20):
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: present in only one")
            else:
                diff_paths(a[k], b[k], f"{path}/{k}", out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            diff_paths(x, y, f"{path}[{i}]", out, limit)
    elif isinstance(a, (dict, list)) or isinstance(b, (dict, list)):
        # one side is a record or a list and the other is not (or they are a record and a list): the objects are not printed
        out.append(f"{path}: type {type(a).__name__} vs {type(b).__name__}")
    elif not _same_scalar(a, b):
        out.append(f"{path}: {_short(a)} vs {_short(b)}")
    return out


def dump_results(res):
    return json.dumps(jsonable(res), indent=1, sort_keys=True) + "\n"


def verify(manifest, base_dir, results_path, plan_path=None, code_now=None, file_resamples=stats.RESAMPLES):
    """Recomputes from the stored files and compares with the stored results.json. Returns (exit code, lines). The
    recomputation always uses the registered number of resamples (pool.RESAMPLES = 2000, rules 2 and 10): a results.json that
    states another number is reported and fails."""
    lines = []
    probs = validate_manifest(manifest)
    if probs:
        return 3, ["manifest: " + p for p in probs]
    if not manifest["entries"] and not os.path.exists(results_path):
        return 0, ["no run exists and no results.json is stored: nothing to verify"]
    try:
        got = gather(manifest, base_dir)
    except ManifestError as exc:
        return 3, ["stop: " + p for p in exc.problems]
    bad = 0
    for r in got["records"]:
        fp = verify_file(r["doc"], file_resamples) if isinstance(r["doc"], dict) else ["not a JSON object"]
        for p in fp:
            lines.append(f"{r['rel']}: {p}")
        bad += bool(fp)
    lines.append(f"verified {len(got['records'])} file(s): {bad} with problems")
    if not os.path.exists(results_path):
        lines.append(f"{results_path} does not exist")
        return 1, lines
    try:
        with open(results_path, encoding="utf-8") as f:
            stored = json.load(f)
    except OSError as exc:
        lines.append(f"{results_path} cannot be read: {exc.strerror or exc}")
        return 1, lines
    except ValueError as exc:
        lines.append(f"{results_path} is not readable JSON: {exc}")
        return 1, lines
    except RecursionError:                       # a file of thousands of '['
        lines.append(f"{results_path} is not readable JSON: nested too deeply")
        return 1, lines
    their = (stored.get("analysis") or {}).get("resamples") if isinstance(stored, dict) and isinstance(stored.get("analysis"), dict) else None
    wrong_n = their != pool.RESAMPLES
    if wrong_n:
        lines.append(f"stored resamples {their} is not {pool.RESAMPLES} (the registered statistic): the recomputation uses {pool.RESAMPLES}")
    # the recomputation uses the plan hash and the code hashes the stored file records, so that editing a hashed file of the
    # wider project later does not change it; the two differences are reported on lines of their own
    sd = stored if isinstance(stored, dict) else {}
    plan_then = sd.get("plan_sha256") if isinstance(sd.get("plan_sha256"), str) and _SHA64.match(sd["plan_sha256"]) else None
    code_then = sd.get("code_sha256") if isinstance(sd.get("code_sha256"), dict) else None
    new = json.loads(dump_results(analyse(manifest, base_dir, pool.RESAMPLES, plan_path, code_then, plan_then)))
    d = diff_paths(stored, new)
    for x in d:
        lines.append(f"results.json differs: {x}")
    lines.append("results.json " + ("matches the recomputation" if not d and not wrong_n else "does NOT match the recomputation"))
    plan_moved = plan_then is not None and plan_then != sw.plan_sha256(plan_path)
    if plan_moved:
        lines.append(f"plan changed since results.json: stored plan sha256 {plan_then}, the plan file now has {sw.plan_sha256(plan_path)}")
    if code_then is not None:
        now = sw.code_sha256() if code_now is None else code_now
        moved = sorted(k for k in set(code_then) | set(now) if code_then.get(k) != now.get(k))
        if moved:
            lines.append("code files changed since results.json was written: " + ", ".join(moved)
                         + " (not a failure: the recomputation used the hashes stored in results.json)")
    return (1 if (bad or d or wrong_n or plan_moved) else 0), lines


# ---------------------------------------------------------------- command line

def _same_path(a, b):
    """True when two path strings name the same file: the same absolute path after links are resolved and, on a file system
    that does not tell upper from lower case, with case folded; or, when both exist, the same file (a hard link, another
    spelling)."""
    if os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b)):
        return True
    try:
        return os.path.samefile(a, b)
    except OSError:                     # one of them does not exist (yet): the spellings alone decide
        return False


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    class Usage(Exception):
        pass

    def take(flag):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                raise Usage(f"forwardt: {flag} needs a value")
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return None

    try:
        manifest_path = take("--manifest") or MANIFEST_FILE
        base = take("--base") or REPO
        out = take("--out") or RESULTS_FILE
        resamples_given = "--resamples" in argv
        given = take("--resamples")
        try:
            resamples = pool.RESAMPLES if given is None else int(given)
        except ValueError:
            raise Usage(f"forwardt: --resamples {given!r} is not a whole number")
        if resamples < 1:
            raise Usage(f"forwardt: --resamples {resamples} is not above zero")
    except Usage as exc:
        print(exc)
        return 2
    do_verify = "--verify" in argv
    if do_verify:
        argv.remove("--verify")
    no_write = "--no-write" in argv
    if no_write:
        argv.remove("--no-write")
    if argv:
        print(__doc__)
        return 2
    if do_verify and resamples_given:
        print(f"forwardt: --verify always recomputes with the registered {pool.RESAMPLES} resamples and takes no --resamples")
        return 2
    if resamples != pool.RESAMPLES:
        print(f"NOT THE REGISTERED STATISTIC: {resamples} resamples, the plan fixes {pool.RESAMPLES} (rules 2 and 10); "
              "the numbers below are not a result of the study")
        if not no_write and _same_path(out, RESULTS_FILE):
            print("forwardt: refusing to write the registered results file with an unregistered number of resamples; "
                  "name another file with --out")
            return 2
    if not do_verify and not no_write and os.path.isdir(out):
        print(f"forwardt: --out {out} is a directory, not a file")
        return 2
    try:
        manifest = read_manifest(manifest_path)
    except ManifestError as exc:
        print("forwardt: stop, no result written: " + "; ".join(exc.problems))
        return 3
    if do_verify:
        code, lines = verify(manifest, base, out)
        print("\n".join(lines))
        return code
    try:
        res = analyse(manifest, base, resamples)
    except ManifestError as exc:
        print("forwardt: stop, no result written:")
        for p in exc.problems:
            print("  " + p)
        return 3
    print(render_report(res))
    if no_write:
        return 0
    try:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(dump_results(res))
    except OSError as exc:
        print(f"forwardt: cannot write {out}: {exc.strerror or exc}")
        return 2
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
