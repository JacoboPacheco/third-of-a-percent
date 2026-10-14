"""Pure helpers of the real-program study (realworld/PLAN.md), testable on a laptop without a compiler.

- parse_result(): the RESULT line every driver prints.
- cachegrind_lines(): per (file, function, line) instruction counts from a Cachegrind output file.
- iteration_counts(): one workload iteration = the iters=2 run minus the iters=1 run, per line.
- lost_loops_for(): the census 2 lost loops of a project (file, line range, function).
- shares(): the two profile shares (loop lines, containing functions) of one iteration.
- remark_locations(): "vectorized loop" remark counts per source location, from clang's stderr.
- verdict_row(): the pre-registered reading of one pooled row (detectably slower / faster / at most X %).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LOST_FILE = os.path.join(REPO, "results", "corpus2-baseline-run-38273183229", "lost_loops.json")


# ---------------------------------------------------------------- driver output

def parse_result(stdout):
    """{'ns': float, 'iters': int, 'checksum': str, 'checksum_r': str} from the last RESULT line."""
    line = None
    for ln in stdout.splitlines():
        if ln.startswith("RESULT "):
            line = ln
    if line is None:
        raise ValueError("no RESULT line in the program's output")
    kv = dict(tok.split("=", 1) for tok in line.split()[1:] if "=" in tok)
    return {"ns": float(kv["ns"]), "iters": int(kv["iters"]), "checksum": kv["checksum"],
            "checksum_r": kv.get("checksum_r", kv["checksum"])}


# ---------------------------------------------------------------- cachegrind

_NAME = re.compile(r"^\((\d+)\)(?: (.*))?$")


def cachegrind_lines(text):
    """{(file, fn, line): Ir} and the summary total from a Cachegrind output file.

    Handles fl=/fi=/fe= (file; fi/fe are inlined-file switches in some versions) and fn=, and the
    "(id) name" compression callgrind uses, so it reads either tool's line-level output. Only the
    first event column (Ir) is used.
    """
    names = {}
    counts = {}
    total = None
    fl = fn = None
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln:
            continue
        if ln.startswith(("fl=", "fi=", "fe=", "fn=")):
            key, val = ln[:2], ln[3:]
            m = _NAME.match(val)
            if m:
                ident, name = m.group(1), m.group(2)
                if name is not None:
                    names[(key[0], ident)] = name
                val = names.get((key[0], ident), val)
            if key == "fn":
                fn = val
            else:
                fl = val
            continue
        if ln.startswith("summary:"):
            try:
                total = int(ln.split(":", 1)[1].split()[0])
            except (IndexError, ValueError):
                total = None
            continue
        if ln[0].isdigit():
            parts = ln.split()
            if len(parts) < 2:
                continue
            try:
                line_no, ir = int(parts[0]), int(parts[1])
            except ValueError:
                continue
            k = (fl, fn, line_no)
            counts[k] = counts.get(k, 0) + ir
    return counts, total


def iteration_counts(counts_one, counts_two):
    """Per-line Ir of one workload iteration: the iters=2 run minus the iters=1 run (negatives kept,
    they are noise from allocation order and sum to almost nothing)."""
    out = dict(counts_two)
    for k, v in counts_one.items():
        out[k] = out.get(k, 0) - v
    return {k: v for k, v in out.items() if v != 0}


# ---------------------------------------------------------------- the census lost loops

def load_lost(path=LOST_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["lost"]


def lost_loops_for(project, lost=None):
    """The census 2 lost loops of one project, one entry per distinct (file, line, function)."""
    if project is None:
        return []
    lost = load_lost() if lost is None else lost
    seen = {}
    for e in lost:
        if e["project"] != project:
            continue
        lines = (e.get("index_evidence") or {}).get("loop_lines") or [e["line"], e["line"]]
        key = (e["file"], e["line"], e["function"])
        if key not in seen:
            seen[key] = {"file": e["file"], "line": e["line"], "column": e.get("column"),
                         "loop_lines": [int(lines[0]), int(lines[-1])], "function": e["function"],
                         "function_name": e.get("function_name"), "class": e.get("class"),
                         "count": 0}
        seen[key]["count"] += e.get("count", 1)
    return sorted(seen.values(), key=lambda x: (x["file"], x["line"], x["function"]))


def _file_matches(path, census_file):
    if path is None:
        return False
    p = path.replace("\\", "/")
    return p == census_file or p.endswith("/" + census_file)


def shares(iter_counts, loops):
    """Shares of one iteration's instructions: on the lost loops' own source lines (lower bound) and
    in the functions that contain a lost loop (upper bound). Also the per-loop detail."""
    total = sum(iter_counts.values())
    funcs = {lp["function"] for lp in loops}
    on_lines = 0
    in_funcs = 0
    per_loop = {}
    for (fl, fn, line), ir in iter_counts.items():
        if fn in funcs:
            in_funcs += ir
        for lp in loops:
            lo, hi = lp["loop_lines"]
            if lo <= line <= hi and _file_matches(fl, lp["file"]):
                on_lines += ir
                key = f"{lp['file']}:{lp['line']}"
                per_loop[key] = per_loop.get(key, 0) + ir
                break
    per_func = {}
    for (fl, fn, line), ir in iter_counts.items():
        if fn in funcs:
            per_func[fn] = per_func.get(fn, 0) + ir
    return {"iteration_ir": total,
            "loop_lines_ir": on_lines, "loop_lines_share": (on_lines / total) if total > 0 else None,
            "functions_ir": in_funcs, "functions_share": (in_funcs / total) if total > 0 else None,
            "per_loop_ir": dict(sorted(per_loop.items())),
            "per_function_ir": dict(sorted(per_func.items(), key=lambda kv: -kv[1])[:20]),
            "functions_matched": sum(1 for f in funcs if f in per_func), "functions_listed": len(funcs)}


# ---------------------------------------------------------------- clang remarks

_REMARK = re.compile(r"^(.+?):(\d+):(\d+): remark: (.*?)\s*\[(-Rpass(?:-missed|-analysis)?=loop-vectorize)\]\s*$")


def remark_locations(stderr):
    """{(path, line, col): {'vectorized': n, 'missed': n}} over a build's stderr."""
    out = {}
    for ln in stderr.splitlines():
        m = _REMARK.match(ln.strip())
        if not m:
            continue
        path, line, col, msg, kind = m.groups()
        k = (path.replace("\\", "/"), int(line), int(col))
        d = out.setdefault(k, {"vectorized": 0, "missed": 0})
        if kind == "-Rpass=loop-vectorize" and msg.startswith("vectorized loop"):
            d["vectorized"] += 1
        elif kind == "-Rpass-missed=loop-vectorize":
            d["missed"] += 1
    return out


def lost_in_build(none_locs, fast_locs, loops):
    """For each distinct census lost location (file:line:col): vectorized-remark counts in NONE and FAST."""
    rows = []
    seen = set()
    for lp in loops:
        key = (lp["file"], lp["line"], lp["column"])
        if key in seen:
            continue
        seen.add(key)

        def count(locs):
            return sum(v["vectorized"] for (p, l, c), v in locs.items()
                       if l == lp["line"] and (lp["column"] is None or c == lp["column"]) and _file_matches(p, lp["file"]))
        n, f = count(none_locs), count(fast_locs)
        rows.append({"location": f"{lp['file']}:{lp['line']}:{lp['column']}", "vectorized_none": n,
                     "vectorized_fast": f, "lost_here_too": n > f})
    return rows


# ---------------------------------------------------------------- the pre-registered reading

def at_most_pct(his, aa_hw):
    return max(0.0, max(100.0 * (h - 1.0) for h in his), aa_hw)


def verdict_row(as_compiled, aligned, aa_hw, jobs, minimum_jobs=3):
    """The PLAN.md rule for one pooled row: as_compiled/aligned are {'ratio', 'ci95'}; aa_hw in percent."""
    if jobs < minimum_jobs:
        return {"reading": "too few jobs", "jobs": jobs, "at_most_pct": None,
                "text": f"too few jobs ({jobs}; the minimum is {minimum_jobs}): no reading"}
    up, down = 1.0 + aa_hw / 100.0, 1.0 - aa_hw / 100.0
    slow = [c["ci95"][0] > up for c in (as_compiled, aligned)]
    fast = [c["ci95"][1] < down for c in (as_compiled, aligned)]
    his = [as_compiled["ci95"][1], aligned["ci95"][1]]
    if all(slow):
        return {"reading": "detectably slower", "jobs": jobs, "at_most_pct": None,
                "text": f"FAST detectably slower in both columns (as compiled {as_compiled['ratio']:.4f}, "
                        f"aligned {aligned['ratio']:.4f}; A/A half-width {aa_hw:.2f}%)"}
    if all(fast):
        return {"reading": "detectably faster", "jobs": jobs, "at_most_pct": None,
                "text": f"FAST detectably faster in both columns (as compiled {as_compiled['ratio']:.4f}, "
                        f"aligned {aligned['ratio']:.4f}; A/A half-width {aa_hw:.2f}%)"}
    x = at_most_pct(his, aa_hw)
    note = ""
    if any(slow) or any(fast):
        col = "as compiled" if (slow[0] or fast[0]) else "aligned"
        note = f" (only the {col} column crossed the A/A floor)"
    return {"reading": "not detectable", "jobs": jobs, "at_most_pct": x,
            "text": f"not detectable: at most {x:.2f}%{note}"}
