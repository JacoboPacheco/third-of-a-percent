"""Ties the numbers that the documents state about the forwardt result to
forwardt/results.json.

Every table row of the Result section of forwardt/README.md is formed here
from the stored results and must appear in the README word for word; the
README may state no other row, and no decimal number in that section other
than the ones formed here, the band edges of the plan and a few counts. The
sentences of README.md and readme-parts/DETAILS.md that carry the forwardt
result are formed the same way (tests below). Each guard is tamper-tested:
a changed number in a copy of the text, or in a copy of the results, fails.

The tests use no pytest feature, so the built-in runner of scripts/check.py
runs them unchanged.
"""

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "forwardt" / "results.json"
FORWARDT_README = ROOT / "forwardt" / "README.md"

LOOPS = ("t01_sum_size", "t02_sum_n", "t03_scale_size", "t04_scale_n", "t05_fill_n", "t06_offset")
VARIABLE = ("t02_sum_n", "t04_scale_n", "t05_fill_n", "t06_offset")
SIZES = ("L1", "L2")
SHORT = {
    "AMD EPYC 7763 64-Core Processor": "EPYC 7763",
    "AMD EPYC 9V45 96-Core Processor": "EPYC 9V45",
    "AMD EPYC 9V74 80-Core Processor": "EPYC 9V74",
    "Neoverse-N2": "Neoverse-N2",
}
# Edges of the bands the plan fixed (forwardt/PLAN.md, Predictions). They are
# the plan's numbers, not results, so they may stand in the README beside the
# measured ones.
PLAN_EDGES = ("0.97", "1.03", "0.79", "1.23", "1.35", "0.90", "1.5", "1.30", "0.80", "1.25", "0.95", "1.15", "1.00")


def load(path=None):
    with open(path or RESULTS, encoding="utf-8") as handle:
        return json.load(handle)


def fmt(value):
    return f"{value:.3f}"


def pair_text(pair):
    low, high = pair["ci95"]
    return f"{fmt(pair['ratio'])} ({fmt(low)} to {fmt(high)})"


def models_by_name(results):
    return {m["cpu_model"]: m for m in results["analysis"]["models"]}


def read_models(results, target):
    return [m for m in results["analysis"]["models"] if m["target"] == target and m["read"]]


def table_rows(model):
    """The markdown rows of one CPU model's table: 6 loops, 2 sizes each."""
    rows = []
    for loop in LOOPS:
        entry = model["loops"][loop]
        for size in SIZES:
            cell = entry["cells"][size]
            pairs = cell["pairs"]
            novec = pairs.get("novec")
            novec = pair_text(novec) if novec and novec.get("ci95") else "-"
            aa = f"{cell['aa_half_width_pct']:.2f} %"
            if not cell["decidable"]:
                aa += " (not decidable)"
            rows.append(
                f"| `{loop}` | {entry['word']} | {size} | {pair_text(pairs['compiled'])} | "
                f"{pair_text(pairs['aligned'])} | {novec} | {aa} |"
            )
    return rows


def table_header():
    return [
        "| Loop | Word | Size | As compiled | Aligned (`-falign-loops=64`) | No-vectorize build | A/A half-width |",
        "|---|---|---|---|---|---|---|",
    ]


def sum_cells_above(results):
    """The P2 cells wholly above 1.35 (letter D prints them): rows of a table."""
    rows = []
    for model in read_models(results, "x86-64"):
        for size in SIZES:
            cell = model["loops"]["t02_sum_n"]["cells"][size]
            for column in ("compiled", "aligned"):
                pair = cell["pairs"][column]
                if pair["ci95"][0] > 1.35:
                    rows.append(
                        f"| {SHORT[model['cpu_model']]} ({model['jobs']} jobs) | {size} | {column} | "
                        f"{pair_text(pair)} |"
                    )
    return rows


BANDS = {
    "x86-64": (
        ("P0", "the six words; one or more FAST traps in each variable-bound loop"),
        ("P1", "controls: `t01_sum_size` 0.97 to 1.03, `t03_scale_size` aligned 0.79 to 1.23"),
        ("P2", "`t02_sum_n`, both columns: 0.97 to 1.35"),
        ("P2n", "`t02_sum_n`, no-vectorize build: 0.90 to 1.35"),
        ("P3", "`t05_fill_n`, `t06_offset` at L1, both columns: above 1.5"),
        ("P4", "`t04_scale_n`, aligned: at most 1.30"),
        ("P5", "L2 ratio over L1 ratio of each lost loop: 0.80 to 1.25"),
    ),
    "Neoverse-N2": (
        ("P0", "the six words; one or more FAST traps in each variable-bound loop"),
        ("P1", "controls, both columns: 0.97 to 1.03"),
        ("P6", "`t05_fill_n`, `t06_offset`, both columns: 0.95 to 1.15"),
    ),
}


def prediction_text(model, name):
    """The state of one prediction on one model, as the README words it."""
    if name == "P0":
        states = [entry["state"] for entry in model["pred"]["P0"].values()]
        holding = sum(1 for state in states if state == "holds")
        return f"{'holds' if holding == len(states) else 'fails'} on {holding} of {len(states)} loops"
    entry = model["pred"]["preds"][name]
    items = entry["items"]
    undecided = entry["not_decidable"]
    states = {}
    for item in items:
        states[item["state"]] = states.get(item["state"], 0) + 1
    notes = [f"{count} {state}" for state, count in sorted(states.items()) if state != "inside"]
    if undecided:
        notes.append(f"{len(items)} of {len(items) + len(undecided)} combinations judged, {len(undecided)} not decidable")
    return entry["state"] + (": " + "; ".join(notes) if notes else "")


def prediction_rows(results, target):
    models = read_models(results, target)
    rows = [
        "| Prediction | Band | " + " | ".join(f"{SHORT[m['cpu_model']]} ({m['jobs']} jobs)" for m in models) + " |",
        "|---|---|" + "---|" * len(models),
    ]
    for name, band in BANDS[target]:
        rows.append(f"| {name} | {band} | " + " | ".join(prediction_text(m, name) for m in models) + " |")
    return rows


def placement_text(model, loop, size):
    return pair_text(model["loops"][loop]["cells"][size]["placement"])


def run_lines(results):
    """The three bullets of the Result section that say what was run."""
    entries = results["manifest"]
    tests = [e for e in entries if e["class"] == "test"]
    measured = [e for e in entries if e["class"] == "measurement"]
    models = results["analysis"]["models"]
    return [
        f"- Code tests ({len(tests)}), started with `jobs` = `[1]` and `reps` = 4, so their files are smoke files "
        "that the analysis sets aside: "
        + " and ".join(f"run {e['run_id']} on `{e['runner']}`" for e in tests)
        + ". They were not stored or pooled, and no ratio of either was read.",
        f"- Measurement runs ({len(measured)}), {sum(e['jobs_returned'] for e in measured)} of "
        f"{sum(e['jobs_started'] for e in measured)} jobs returned: "
        + ", ".join(
            f"run {e['run_id']} on `{e['runner']}` ({e['jobs_returned']} of {e['jobs_started']} jobs, `{e['folder']}`)"
            for e in measured
        )
        + ".",
        "- CPU models that GitHub drew: "
        + ", ".join(f"{SHORT[m['cpu_model']]} for {m['jobs']} jobs" for m in models)
        + ".",
    ]


NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def n2_undecidable_text(results):
    """The sentence on the Neoverse-N2 cells that cannot be decided (rule 4)."""
    model = models_by_name(results)["Neoverse-N2"]
    bad = []
    for loop in LOOPS:
        for size in SIZES:
            cell = model["loops"][loop]["cells"][size]
            if not cell["decidable"]:
                bad.append((loop, size, cell["aa_half_width_pct"]))
    loops = sorted({loop for loop, _, _ in bad}, key=LOOPS.index)
    sizes = sorted({size for _, size, _ in bad})
    widths = [width for _, _, width in bad]
    decidable_loops = [
        loop
        for loop in LOOPS
        if all(model["loops"][loop]["cells"][size]["decidable"] for size in sizes)
    ]
    other = [size for size in SIZES if size not in sizes]
    text = (
        f"The cells of {NUMBER_WORDS[len(loops)]} of the six loops at {' and '.join(sizes)} are not decidable: "
        f"the A/A half-width there is {min(widths):.2f} to {max(widths):.2f} %, above the 2.0 % ceiling of the "
        "plan's rule 4. Such a cell is reported with its numbers and neither holds nor fails a prediction."
    )
    if other:
        text += f" Every cell at {' and '.join(other)} is decidable"
        if decidable_loops:
            text += f"; at {' and '.join(sizes)} only " + " and ".join(f"`{loop}`" for loop in decidable_loops) + " is"
        text += "."
    return text


def sum_table_header():
    return ["| Model | Size | Column | FAST over NONE (95 % interval) |", "|---|---|---|---|"]


def x86_models(results):
    return {m["cpu_model"]: m for m in read_models(results, "x86-64")}


def reading_paragraph(results, below=True):
    """Which CPU models are read, and on how many jobs from which runs. `below` is the wording of forwardt/README.md, whose
    tables follow the paragraph; README.md and the details page say it without the pointer."""
    parts = ["A CPU model is read only when at least 3 jobs of it returned (rule 1 of the plan)."]
    for model in results["analysis"]["models"]:
        name = SHORT[model["cpu_model"]]
        runs = model["runs"]
        where = f"run {runs[0]}" if len(runs) == 1 else "runs " + " and ".join(runs)
        if not model["read"]:
            parts.append(
                f"{name} has {model['jobs']} jobs and is not read: its numbers are in `results.json`, marked as "
                "not read, and it enters no table, word or prediction" + (" below." if below else ".")
            )
        elif model["few_jobs_caveat"]:
            parts.append(
                f"{name} has {model['jobs']} jobs from {where}, so its intervals are coarse and understate the "
                "spread between jobs."
            )
        else:
            parts.append(f"{name} has {model['jobs']} jobs from {where}.")
    return " ".join(parts)


def x86_write_sentence(results):
    m7763 = models_by_name(results)["AMD EPYC 7763 64-Core Processor"]
    cells = m7763["loops"]["t05_fill_n"]["cells"]["L1"]
    return (
        "P3 held: at L1 the intervals of `t05_fill_n` and `t06_offset` lie above 1.5 in both columns on both "
        "models. For a write cell the plan allows the words \"at or above 1.5x\" and no other limit. The two "
        "columns of `t05_fill_n` differ: on EPYC 7763 at L1 it is "
        + pair_text(cells["pairs"]["compiled"])
        + " as compiled and "
        + pair_text(cells["pairs"]["aligned"])
        + " aligned, and the plan's placement statistic (the as-compiled ratio over the aligned one) is "
        + pair_text(cells["placement"])
        + ". A single cost for that loop is not read from the two columns."
    )


def n2_sum_sentence(results):
    cell = models_by_name(results)["Neoverse-N2"]["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]
    return (
        "`t02_sum_n` is lost on this core: "
        + pair_text(cell["compiled"])
        + " as compiled and "
        + pair_text(cell["aligned"])
        + " aligned at L1. The plan gives it no band here, so the numbers are reported without one."
    )


def n2_p6_sentence(results):
    model = models_by_name(results)["Neoverse-N2"]
    cells = model["loops"]["t05_fill_n"]["cells"]
    return (
        "P6 failed on one cell: `t05_fill_n` at L1 as compiled is "
        + pair_text(cells["L1"]["pairs"]["compiled"])
        + ", wholly below the lower edge 0.95. The same loop aligned at L1 is "
        + pair_text(cells["L1"]["pairs"]["aligned"])
        + ", inside the band, and the plan's placement statistic for that cell is "
        + pair_text(cells["L1"]["placement"])
        + ". At L2 the aligned cell is "
        + pair_text(cells["L2"]["pairs"]["aligned"])
        + ", whose interval contains the lower edge, so it is neither inside nor outside the band. The two columns "
        "of this loop differ, and nothing here says which of them is the cost of the loop on this core."
    )


def n2_lead_sentence(results):
    """The sentence under the Neoverse-N2 heading of forwardt/README.md: how many runs and jobs the column rests on, and
    whether prediction P6 held. The count of runs is the one reading of the model's runs: more than one run would be
    said differently."""
    model = models_by_name(results)["Neoverse-N2"]
    state = {"holds": "held", "fails": "failed"}[model["pred"]["preds"]["P6"]["state"]]
    runs = len(model["runs"])
    if runs == 1:
        head = f"One run of {NUMBER_WORDS[model['jobs']]} jobs on one core type."
    else:
        head = f"{NUMBER_WORDS[runs].capitalize()} runs with {NUMBER_WORDS[model['jobs']]} jobs in all on one core type."
    return f"### Neoverse-N2\n\n{head} Prediction P6 {state}."


CENSUS_SENTENCE = (
    "The loop census (`corpus/README.md`, clang 18) counts 444 lost loops, one per function a loop was compiled "
    "into; 228 of them, at 38 source locations, fall in its class \"forward loop bounded by a variable\", assigned "
    "by a text pattern on the loop header and body. The census does not know how often any of them runs, and how "
    "many of the 228 have one of the six shapes timed here is not counted. The ratios above are for six "
    "hand-written loops: they are not a cost for those 228 loops and not a share of a program's run time."
)


def generated_lines(results):
    """Every line and sentence of the Result section that is formed from the results."""
    lines = []
    lines.extend(run_lines(results))
    lines.append(reading_paragraph(results))
    lines.extend(sum_table_header())
    lines.extend(sum_cells_above(results))
    lines.extend(prediction_rows(results, "x86-64"))
    lines.append(x86_write_sentence(results))
    for model in read_models(results, "x86-64"):
        lines.append(f"#### {SHORT[model['cpu_model']]} ({model['jobs']} jobs)")
        lines.extend(table_header() + table_rows(model))
    n2 = models_by_name(results)["Neoverse-N2"]
    lines.append(n2_lead_sentence(results))
    lines.extend(prediction_rows(results, "Neoverse-N2"))
    lines.extend(table_header() + table_rows(n2))
    lines.extend([n2_undecidable_text(results), n2_sum_sentence(results), n2_p6_sentence(results), CENSUS_SENTENCE])
    return lines


def decimals(text):
    return re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])", text)


def result_section(readme_text):
    start = readme_text.index("\n## Result\n")
    end = readme_text.find("\n## ", start + 1)
    return readme_text[start:end if end != -1 else len(readme_text)]


def readme_problems(readme_text, results):
    """What differs between the Result section of forwardt/README.md and results.json."""
    try:
        section = result_section(readme_text)
    except ValueError:
        return ["forwardt/README.md has no Result section"]
    lines = generated_lines(results)
    problems = [f"missing from the Result section: {line[:90]}" for line in lines if line not in section]
    generated_rows = {line for line in lines if line.startswith("|")}
    for line in section.splitlines():
        if line.startswith("|") and line not in generated_rows:
            problems.append(f"table row not formed from results.json: {line[:90]}")
    allowed = set(decimals("\n".join(lines))) | set(PLAN_EDGES)
    for number in sorted(set(decimals(section)) - allowed):
        problems.append(f"number not formed from results.json or the plan: {number}")
    entries = results["manifest"]
    measured = [e for e in entries if e["class"] == "measurement"]
    returned = sum(e["jobs_returned"] for e in measured)
    started = sum(e["jobs_started"] for e in measured)
    if f"All {NUMBER_WORDS[len(entries)]} runs started from commit {entries[0]['head_sha'][:7]}" not in section:
        problems.append("the commit sentence of the Result section differs from the manifest")
    if len({e["head_sha"] for e in entries}) != 1:
        problems.append("the runs do not share one commit, and the Result section says they do")
    state = readme_text[readme_text.index("\n## State\n") : readme_text.index("\n## Result\n")]
    for needle in (f"lists {NUMBER_WORDS[len(entries)]} runs", f"{returned} of {started} measurement jobs returned"):
        if needle not in state:
            problems.append(f"the State section lacks: {needle}")
    return problems


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


# ---- README.md and readme-parts/DETAILS.md ---------------------------------------------------------------------

README = ROOT / "README.md"
DETAILS = ROOT / "readme-parts" / "DETAILS.md"
README_SECTION = "## Forward loops with a variable bound"
README_ANCHOR = "#forward-loops-with-a-variable-bound"
README_LINK = f"[Forward loops with a variable bound]({README_ANCHOR})"
DETAILS_BULLET_START = "- **Forward loops with a variable bound were timed separately (`forwardt/`).** "
DETAILS_LIMITS_START = "- **The variable-bound loops (`forwardt/`): what they do not show.** "

OUTER_INTRO = (
    "The forward loops timed elsewhere in this study (the forward sum, the forward add and the stencil) are bounded "
    "by the container's own length, `size()` (the stencil's by `size()` less one). "
    "[forwardt/](forwardt/README.md) times six forward loops with clang 18.1.3 and libc++ 18: two controls "
    "bounded by `size()` and four loops bounded by a variable `n` (`t02_sum_n`, `t04_scale_n`, `t05_fill_n`, "
    "`t06_offset`). Its plan, [forwardt/PLAN.md](forwardt/PLAN.md), fixes the predictions (named P0 to P6) and the "
    "rules that turn the ratios into sentences. The plan is the only file of its commit in the public history; that "
    "its commit came before the code and the runs rests on the author's clock and on that history, and is not "
    "otherwise checkable. The plan's sha256 is stored in every result file, and `scripts/check.py` compares it "
    "with the file."
)
OUTER_SCOPE = (
    "These are results for six hand-written loops with clang 18.1.3 and libc++ 18 at `-O2`. The sentences "
    "elsewhere that say forward loops cost little or keep SIMD are about loops bounded by `size()`; they are not "
    "a result for forward loops with another bound."
)
OUTER_TABLES_POINTER = (
    "Every cell of the six loops is in [forwardt/README.md](forwardt/README.md), and the decidable aligned cells "
    "of the four variable-bound loops are listed in the [details](readme-parts/DETAILS.md)."
)

# Each row: the document, the wording that says the loops are bounded by `size()` (or points to the variable-bound
# section), and the older unscoped wording that must not come back.
SCOPE_PAIRS = (
    (
        "README.md",
        "Loops that count upward to the container's own `size()` (forward loops bounded by `size()`) kept SIMD",
        "Loops that count upward (forward loops) kept SIMD",
    ),
    (
        "README.md",
        "- **Forward sum, forward add**: `s += a[i]` and `c[i] = a[i] + b[i]` over a vector's `size()`, indices counting up",
        "- **Forward sum, forward add**: `s += a[i]` and `c[i] = a[i] + b[i]`, indices counting up",
    ),
    (
        "README.md",
        "- Forward loops bounded by `size()` cost little on the AMD models",
        "- Forward loops cost little on the AMD models",
    ),
    (
        "README.md",
        "forward loops bounded by `size()` cost 1.000x to 1.007x at L1",
        "forward loops cost 1.000x to 1.007x at L1",
    ),
    (
        "README.md",
        "For forward loops bounded by `size()` it can (the check moves to the tail)",
        "For forward loops it can (the check moves to the tail)",
    ),
    (
        "DETAILS.md",
        "(forward, two-array, stencil, reverse, stride-2, gather, histogram, matrix multiply; the first three count up "
        "to the vector's own `size()`, the stencil's to `size()` less one) twice",
        "(forward, two-array, stencil, reverse, stride-2, gather, histogram, matrix multiply) twice",
    ),
    (
        "DETAILS.md",
        "**Forward loops bounded by `size()` pay little under clang on the AMD models.**",
        "**Forward loops pay little under clang on the AMD models.**",
    ),
    ("DETAILS.md", "forward loops bounded by `size()` ran ", "forward loops ran "),
    ("DETAILS.md", "| forward loops bounded by `size()`, aligned |", "| forward loops, aligned |"),
    (
        "DETAILS.md",
        "both ends of the forward column (the loops bounded by `size()`) are placement-sensitive cells",
        "both ends of the forward column are placement-sensitive cells",
    ),
    (
        "DETAILS.md",
        "draw the same line for the forward loops bounded by `size()`, the reverse loop and the stride-2 loop",
        "draw the same line for forward, reverse and stride-2 loops",
    ),
    ("DETAILS.md", "Forward loops bounded by `size()` keep their NEON loops and cost ", "Forward loops keep their NEON loops and cost "),
    (
        "DETAILS.md",
        'So "forward loops near 1x" (loops bounded by `size()`) holds for the sum',
        'So "forward loops near 1x" holds for the sum',
    ),
    (
        "DETAILS.md",
        "- **Negative**: the forward loops bounded by `size()`, vectorized in both builds, expected near 1.0x.",
        "- **Negative**: the forward loops, vectorized in both builds, expected near 1.0x.",
    ),
)
# Pointers from the sentences that name the AMD models, the Arm core or the sum to the variable-bound section.
POINTERS = (
    (
        "README.md",
        f"Loops with a variable bound are not covered by this line: see {README_LINK}.",
    ),
    (
        "README.md",
        f"Loops with a variable bound are timed separately on this core too (see {README_LINK}).",
    ),
)


def outer_runs_sentence(results):
    models = results["analysis"]["models"]
    measured = [e for e in results["manifest"] if e["class"] == "measurement"]
    returned = sum(e["jobs_returned"] for e in measured)
    started = sum(e["jobs_started"] for e in measured)
    parts = [f"{SHORT[m['cpu_model']]} for {m['jobs']}" for m in models]
    drew = ", ".join(parts[:-1]) + " and " + parts[-1]
    text = (
        f"{NUMBER_WORDS[len(measured)].capitalize()} measurement runs ({returned} of {started} jobs returned) drew "
        f"{drew} jobs. A CPU model is read only with 3 or more jobs"
    )
    unread = [SHORT[m["cpu_model"]] for m in models if not m["read"]]
    if unread:
        text += f", so {' and '.join(unread)} {'is' if len(unread) == 1 else 'are'} not read"
    return text + "."


def x86_sum_values(results):
    values = []
    for model in read_models(results, "x86-64"):
        for size in SIZES:
            for column in ("compiled", "aligned"):
                values.append(model["loops"]["t02_sum_n"]["cells"][size]["pairs"][column]["ratio"])
    return values


def outer_sum_sentence(results):
    models = read_models(results, "x86-64")
    names = " and ".join(SHORT[m["cpu_model"]] for m in models)
    values = x86_sum_values(results)
    return (
        f"On the {NUMBER_WORDS[len(models)]} x86-64 models read ({names}) the prediction for the sum with a "
        "variable bound failed: `t02_sum_n` was predicted at 0.97 to 1.35 times the unchecked time, and its "
        f"{len(values)} cells (two sizes and two columns on each model) ran {fmt(min(values))} to "
        f"{fmt(max(values))} times, each interval wholly above 1.35."
    )


def x86_letter_sentence(results):
    outcome = results["analysis"]["outcome"]
    sides = " and ".join(outcome["p2_fail_sides"])
    return (
        f"The plan's outcome for the x86-64 models is letter {outcome['letter']}: the prediction for the sum (P2) "
        f"failed {sides} its band, so the plan states no limit and no forward-range word for the sum cells, and "
        "they are reported as measured."
    )


def prediction_holds(model, name):
    """True when the prediction holds on the model (P0 holds when it holds on every loop)."""
    if name == "P0":
        return all(entry["state"] == "holds" for entry in model["pred"]["P0"].values())
    return model["pred"]["preds"][name]["state"] == "holds"


def outer_controls_sentence(results):
    models = read_models(results, "x86-64")
    assert all(prediction_holds(m, "P1") for m in models)
    return (
        "Prediction P1 held on both x86-64 models: the two controls, `t01_sum_size` and `t03_scale_size`, which "
        "are bounded by `size()`, stayed inside their bands."
    )


def join_and(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def outer_others_sentence(results):
    models = read_models(results, "x86-64")
    names = ("P0", "P2n", "P4", "P5")
    held = [name for name in names if all(prediction_holds(m, name) for m in models)]
    rest = [name for name in names if name not in held]
    text = f"The other predictions on these models ({join_and(held)}) held." if held else ""
    if rest:
        text += f" {join_and(rest)} did not hold on both."
    return text.strip()


def outer_n2_controls_sentence(results):
    model = models_by_name(results)["Neoverse-N2"]
    entry = model["pred"]["preds"]["P1"]
    judged, undecided = len(entry["items"]), len(entry["not_decidable"])
    return (
        f"Prediction P1, for the two controls, {'held' if entry['state'] == 'holds' else 'did not hold'} on the "
        f"{judged} of {judged + undecided} combinations of loop, size and column that were decidable; "
        f"{undecided} were not."
    )


def n2_p6_rest_sentence(results):
    """The rest of prediction P6 on Neoverse-N2 beside its one failed cell: the cell whose interval straddles the lower
    edge of the band and the cells that cannot be decided. forwardt/README.md says the same in its P6 bullet and its
    prediction row ("1 below; 1 straddle; 6 of 8 combinations judged, 2 not decidable")."""
    entry = models_by_name(results)["Neoverse-N2"]["pred"]["preds"]["P6"]
    straddle = [item for item in entry["items"] if item["state"] == "straddle"]
    undecided = entry["not_decidable"]
    assert len(straddle) == 1 and len(entry["items"]) + len(undecided) == 8
    assert undecided and len({(item["loop"], item["size"]) for item in undecided}) == 1
    item = straddle[0]
    (column,) = item["columns"]
    assert item["band"]["lo"] == 0.95 and item["columns"][column]["ci95"][0] < 0.95 < item["columns"][column]["ci95"][1]
    width = undecided[0]["aa_half_width_pct"]
    return (
        f"At {item['size']} the {column} cell of `{item['loop']}` is {pair_text(item['columns'][column])}, whose interval "
        f"contains the lower edge {item['band']['lo']}, so it is neither inside nor outside the band; the "
        f"{NUMBER_WORDS[len(undecided)]} `{undecided[0]['loop']}` cells at {undecided[0]['size']} are not decidable "
        f"(A/A half-width {width:.2f} %), so {len(entry['items'])} of the 8 combinations of P6 are judged."
    )


def outer_n2_sentence(results):
    model = models_by_name(results)["Neoverse-N2"]
    cells = model["loops"]["t05_fill_n"]["cells"]["L1"]
    return (
        f"Neoverse-N2 is one run of {NUMBER_WORDS[model['jobs']]} jobs, so its intervals cannot show spread between "
        "runs. "
        + outer_n2_controls_sentence(results)
        + " "
        + n2_sum_sentence(results)
        + " Prediction P6, for the writes, failed on one cell: `t05_fill_n` at L1 as compiled is "
        + pair_text(cells["pairs"]["compiled"])
        + ", wholly below the lower edge 0.95, and aligned it is "
        + pair_text(cells["pairs"]["aligned"])
        + ", inside the band; the two columns of that loop differ. "
        + n2_p6_rest_sentence(results)
    )


def top_clause(results):
    """The sentence the top of README.md adds beside its statement about the loops bounded by `size()`."""
    values = x86_sum_values(results)
    models = read_models(results, "x86-64")
    return (
        "Forward loops with another bound, a variable `n`, were timed separately and that sentence does not cover "
        f"them: on the {NUMBER_WORDS[len(models)]} x86-64 models read, the sum with a variable bound took "
        f"{fmt(min(values))} to {fmt(max(values))} times as long with the checks on, where 0.97 to 1.35 was "
        f"predicted (see {README_LINK})."
    )


def runs_word(results):
    entries = results["manifest"]
    measured = [e for e in entries if e["class"] == "measurement"]
    tests = [e for e in entries if e["class"] == "test"]
    return entries, measured, tests


def readme_map_text(results):
    entries, measured, tests = runs_word(results)
    return (
        f"the manifest of {NUMBER_WORDS[len(entries)]} runs `forwardt/runs.json`, the stored result "
        f"`forwardt/results.json` and the workflow `forwardt.yml` (runs `s11-forwardt-run-*`: the "
        f"{NUMBER_WORDS[len(measured)]} measurement runs; the {NUMBER_WORDS[len(tests)]} code tests were not stored)"
    )


def details_map_text(results):
    entries, _, _ = runs_word(results)
    return f"runs.json ({NUMBER_WORDS[len(entries)]} runs), results.json, README.md"


def details_folder_text(results):
    entries, _, _ = runs_word(results)
    return (
        f"`analyze.py` for the analysis, `runs.json` listing the {NUMBER_WORDS[len(entries)]} runs and "
        "`results.json` holding the result (above)."
    )


def outer_readme_paragraphs(results):
    """The README.md section: its paragraphs, in order; every sentence formed from the results is in one of them."""
    return [
        OUTER_INTRO,
        " ".join(
            [
                outer_runs_sentence(results),
                outer_controls_sentence(results),
                outer_sum_sentence(results),
                x86_letter_sentence(results),
                x86_write_sentence(results),
                outer_others_sentence(results),
            ]
        ),
        outer_n2_sentence(results),
        OUTER_SCOPE + " " + CENSUS_SENTENCE,
        OUTER_TABLES_POINTER,
    ]


def outer_readme_lines(results):
    """Every piece of the section that must appear in README.md word for word."""
    return [
        OUTER_INTRO,
        outer_runs_sentence(results),
        outer_controls_sentence(results),
        outer_sum_sentence(results),
        x86_letter_sentence(results),
        x86_write_sentence(results),
        outer_others_sentence(results),
        outer_n2_sentence(results),
        OUTER_SCOPE + " " + CENSUS_SENTENCE,
        OUTER_TABLES_POINTER,
    ]


def forward_listing_header():
    return [
        "| Model | Loop | Size | Aligned FAST over NONE (95 % interval) | Inside the forward range (rule 6) |",
        "|---|---|---|---|---|",
    ]


def forward_listing_rows(results):
    """One row per decidable aligned cell of the four variable-bound loops on each read model."""
    read = {m["cpu_model"]: m for m in results["analysis"]["models"] if m["read"]}
    rows = []
    for entry in results["analysis"]["forward_listing"]:
        model = read.get(entry["cpu_model"])
        if model is None:
            continue
        label = f"{SHORT[entry['cpu_model']]} ({model['jobs']} jobs)"
        if not entry["decidable_aligned_cells"]:
            rows.append(f"| {label} | `{entry['loop']}` | none | no decidable cell | - |")
        for cell in entry["decidable_aligned_cells"]:
            word = "yes" if cell["inside_forward_range"] else "no"
            rows.append(f"| {label} | `{entry['loop']}` | {cell['size']} | {pair_text(cell)} | {word} |")
    return rows


def listing_note(results):
    analysis = results["analysis"]
    return (
        f"Inside the forward range is rule 6 of the plan applied as written: {analysis['forward_rule']['text']}. "
        "With no lower bound, \"yes\" does not mean that the cost is near 1: a ratio far below 1 is inside. "
        "The flag is a reading of the rule and not of the loop. For the sum cells (`t02_sum_n`) of the two x86-64 "
        f"models the plan's outcome (letter {analysis['outcome']['letter']}) states no forward-range word, so \"no\" "
        "there says only that the ratio is above 1.02. A cell that is not decidable (rule 4: a pooled A/A half-width "
        "above 2.0 %) has no row, and a loop with no decidable cell on a model has one row saying none. Only the "
        "models that are read have rows."
    )


def details_bullet(results):
    return (
        DETAILS_BULLET_START
        + " ".join(
            [
                outer_runs_sentence(results),
                outer_controls_sentence(results),
                outer_sum_sentence(results),
                x86_letter_sentence(results),
                x86_write_sentence(results),
                outer_others_sentence(results),
                outer_n2_sentence(results),
                OUTER_SCOPE,
                CENSUS_SENTENCE,
                "Every decidable aligned cell of the four variable-bound loops is listed below.",
            ]
        )
    )


def limits_bullet(results):
    models = results["analysis"]["models"]
    intel = [m for m in models if "Xeon" in m["cpu_model"]]
    if intel:
        drawn = " Intel models drawn: " + ", ".join(f"{m['cpu_model']} ({m['jobs']} jobs)" for m in intel) + "."
    else:
        drawn = " No Intel model was drawn, so nothing is said about Intel for these loops."
    return (
        DETAILS_LIMITS_START
        + reading_paragraph(results, below=False)
        + drawn
        + " The loops are six hand-written ones, built with one compiler and library (clang 18.1.3, libc++ 18) at "
        "`-O2` and timed at two sizes (L1 and L2); no hardware counters were read, and the ratios are not a share "
        "of any program's run time."
    )


def outer_section(readme_text):
    start = readme_text.index("\n" + README_SECTION + "\n")
    end = readme_text.find("\n## ", start + 1)
    return readme_text[start : end if end != -1 else len(readme_text)]


def outer_problems(readme_text, details_text, results):
    """What differs between README.md / readme-parts/DETAILS.md and results.json for the forwardt sentences."""
    problems = []
    details = details_text.replace("\r\n", "\n")
    try:
        section = outer_section(readme_text)
    except ValueError:
        problems.append(f"README.md has no section '{README_SECTION}'")
        section = ""
    lines = outer_readme_lines(results)
    for line in lines:
        if section and line not in section:
            problems.append(f"missing from the README.md section: {line[:90]}")
    if section:
        allowed = set(decimals("\n".join(lines))) | set(PLAN_EDGES)
        for number in sorted(set(decimals(section)) - allowed):
            problems.append(f"README.md section: number not formed from results.json or the plan: {number}")
    clause = top_clause(results)
    check_it = readme_text.find("\n## Check it yourself")
    if readme_text.count(clause) != 1 or not 0 <= readme_text.find(clause) < check_it:
        problems.append("the sentence about the variable-bound sum in the top of README.md differs from results.json")
    if readme_map_text(results) not in readme_text:
        problems.append("the folder-map text for forwardt/ in README.md differs from the manifest")
    if details_map_text(results) not in details:
        problems.append("the folder-map text for forwardt/ in readme-parts/DETAILS.md differs from the manifest")
    if details_folder_text(results) not in details:
        problems.append("the description of forwardt/ in readme-parts/DETAILS.md differs from the manifest")
    for start, expected in ((DETAILS_BULLET_START, details_bullet(results)), (DETAILS_LIMITS_START, limits_bullet(results))):
        bullets = [line for line in details.splitlines() if line.startswith(start)]
        if bullets != [expected]:
            problems.append(f"the bullet '{start[:60]}' of readme-parts/DETAILS.md differs from the one formed from results.json")
    rows = forward_listing_rows(results)
    block = "\n".join(forward_listing_header() + rows)
    if block not in details:
        problems.append("the listing of the variable-bound loops in readme-parts/DETAILS.md differs from results.json")
    for line in details.splitlines():
        if line.startswith("| ") and "| `t0" in line and line not in rows:
            problems.append(f"DETAILS.md listing row not formed from results.json: {line[:90]}")
    if "  " + listing_note(results) not in details:
        problems.append("the note under the listing in readme-parts/DETAILS.md differs from results.json")
    if len(x86_sum_values(results)) != len(sum_cells_above(results)):
        problems.append("a sum cell is not wholly above 1.35, and the sentences say every one is")
    texts = {"README.md": readme_text, "DETAILS.md": details}
    for doc, scoped, flat in SCOPE_PAIRS:
        if scoped not in texts[doc]:
            problems.append(f"{doc}: scoped wording missing: {scoped[:80]}")
        if flat in texts[doc]:
            problems.append(f"{doc}: unscoped wording is back: {flat[:80]}")
    for doc, snippet in POINTERS:
        if snippet not in texts[doc]:
            problems.append(f"{doc}: pointer to the variable-bound section missing: {snippet[:80]}")
    return problems


def test_the_forwardt_sentences_of_readme_and_details_match_results_json():
    assert outer_problems(read(README), read(DETAILS), load()) == []


def test_the_section_link_matches_the_heading_it_points_to():
    slug = README_SECTION.lstrip("# ").lower().replace(" ", "-")
    assert README_ANCHOR == "#" + slug


def test_a_changed_forwardt_sentence_or_listing_row_in_readme_or_details_is_found():
    readme = read(README)
    details = read(DETAILS)
    results = load()
    assert "2.043 (2.003 to 2.085)" in details
    assert outer_problems(readme, details.replace("2.043 (2.003 to 2.085)", "2.044 (2.003 to 2.085)", 1), results)
    assert outer_problems(readme, details.replace("| `t06_offset` | L1 |", "| `t06_offset` | L2 |", 1), results)
    row = next(
        line
        for line in details.replace("\r\n", "\n").splitlines()
        if line.startswith("| EPYC 9V74 (3 jobs) | `t04_scale_n` | L2")
    )
    assert row.endswith("| yes |")
    assert outer_problems(readme, details.replace(row, row.replace("| yes |", "| no |")), results)
    assert outer_problems(readme, details.replace("\r\n", "\n").replace(row + "\n", "", 1), results)
    assert outer_problems(readme.replace("each interval wholly above 1.35", "each interval above 1.35", 1), details, results)
    assert outer_problems(readme.replace("228 of them", "229 of them", 1), details.replace("228 of them", "229 of them"), results)
    assert outer_problems(readme.replace("18 of 18 jobs returned", "17 of 18 jobs returned", 1), details, results)
    assert outer_problems(readme.replace(README_SECTION, "## Forward loops", 1), details, results)
    assert outer_problems(
        readme,
        details.replace("- **Forward loops with a variable bound were timed separately", "- **Forward loops were timed separately", 1),
        results,
    )
    assert outer_problems(readme.replace("is letter D:", "is letter C:", 1), details, results)
    assert outer_problems(readme, details.replace("No Intel model was drawn", "An Intel model was drawn", 1), results)
    assert outer_problems(readme, details.replace("a ratio far below 1 is inside", "a ratio far below 1 is outside", 1), results)


def sentence_cannot_be_formed(readme, details, results):
    """True when the documents are stale for results from which the sentence on P6's straddling and undecidable cells is
    no longer formed (the former assertions of the sentence's own function) or no longer matches the documents."""
    try:
        return bool(outer_problems(readme, details, results))
    except AssertionError:
        return True


def test_the_straddling_and_undecidable_cells_of_p6_are_stated_in_readme_and_details():
    readme = read(README)
    details = read(DETAILS)
    results = load()
    sentence = n2_p6_rest_sentence(results)
    assert "0.949 (0.947 to 0.952)" in sentence and "5.98 %" in sentence and "6 of the 8 combinations" in sentence
    assert readme.count(sentence) == 1 and details.replace("\r\n", "\n").count(sentence) == 1
    # a number changed, a word turned round, or the sentence dropped, in either document
    for old, new in (
        ("0.949 (0.947 to 0.952)", "0.949 (0.947 to 0.953)"),
        ("5.98 %", "2.98 %"),
        ("6 of the 8 combinations", "7 of the 8 combinations"),
        ("neither inside nor outside the band", "inside the band"),
        ("are not decidable", "are decidable"),
        (sentence, ""),
    ):
        assert outer_problems(readme.replace(sentence, sentence.replace(old, new, 1), 1), details, results), old
        assert outer_problems(readme, details.replace(sentence, sentence.replace(old, new, 1), 1), results), old
    # the results changed: the straddling cell moves out of the band, or one of the cells that could not be decided is
    # gone from the list of them
    changed = copy.deepcopy(results)
    for item in models_by_name(changed)["Neoverse-N2"]["pred"]["preds"]["P6"]["items"]:
        if item["state"] == "straddle":
            item["state"] = "below"
    assert sentence_cannot_be_formed(readme, details, changed)
    changed = copy.deepcopy(results)
    preds = models_by_name(changed)["Neoverse-N2"]["pred"]["preds"]["P6"]
    preds["not_decidable"] = preds["not_decidable"][:1]
    assert sentence_cannot_be_formed(readme, details, changed)
    changed = copy.deepcopy(results)
    for item in models_by_name(changed)["Neoverse-N2"]["pred"]["preds"]["P6"]["items"]:
        if item["state"] == "straddle":
            item["columns"]["aligned"]["ci95"] = [0.947, 0.953]
    assert outer_problems(readme, details, changed)


def test_a_changed_sentence_in_the_top_or_the_folder_maps_is_found():
    readme = read(README)
    details = read(DETAILS)
    results = load()
    clause = top_clause(results)
    assert clause in readme
    assert outer_problems(readme.replace(clause, clause.replace(fmt(min(x86_sum_values(results))), "1.985x", 1), 1), details, results)
    assert outer_problems(readme.replace(clause, "", 1), details, results)
    assert outer_problems(readme.replace(clause, clause + " " + clause, 1), details, results)
    assert outer_problems(readme.replace(readme_map_text(results), "the manifest of runs `forwardt/runs.json` (empty)", 1), details, results)
    assert outer_problems(readme, details.replace(details_map_text(results), "runs.json (empty), README.md", 1), results)


def test_taking_the_scope_out_of_a_forward_sentence_is_found():
    readme = read(README)
    details = read(DETAILS)
    results = load()
    for doc, scoped, flat in SCOPE_PAIRS:
        if doc == "README.md":
            assert scoped in readme and flat not in readme
            assert outer_problems(readme.replace(scoped, flat, 1), details, results)
            assert outer_problems(readme + "\n" + flat, details, results)
        else:
            assert scoped in details and flat not in details
            assert outer_problems(readme, details.replace(scoped, flat, 1), results)
            assert outer_problems(readme, details + "\n" + flat, results)
    for doc, snippet in POINTERS:
        assert snippet in readme
        assert outer_problems(readme.replace(snippet, "", 1), details, results)


def test_a_changed_result_makes_the_forwardt_sentences_of_readme_and_details_stale():
    readme = read(README)
    details = read(DETAILS)
    results = load()
    changed = copy.deepcopy(results)
    models_by_name(changed)["AMD EPYC 9V74 80-Core Processor"]["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["ratio"] = 2.5
    assert outer_problems(readme, details, changed)
    changed = copy.deepcopy(results)
    for entry in changed["analysis"]["forward_listing"]:
        if entry["cpu_model"] == "Neoverse-N2" and entry["loop"] == "t04_scale_n":
            entry["decidable_aligned_cells"][0]["inside_forward_range"] = False
    assert outer_problems(readme, details, changed)
    changed = copy.deepcopy(results)
    changed["manifest"][3]["jobs_returned"] = 5
    assert outer_problems(readme, details, changed)
    changed = copy.deepcopy(results)
    changed["analysis"]["outcome"]["letter"] = "C"
    assert outer_problems(readme, details, changed)
    changed = copy.deepcopy(results)
    models_by_name(changed)["Neoverse-N2"]["jobs"] = 5
    assert outer_problems(readme, details, changed)


def test_the_forwardt_readme_result_section_matches_results_json():
    assert readme_problems(read(FORWARDT_README), load()) == []


def test_a_changed_number_or_row_in_the_readme_result_section_is_found():
    text = read(FORWARDT_README)
    results = load()
    assert "2.038 (1.996 to 2.084)" in text
    assert readme_problems(text.replace("2.038 (1.996 to 2.084)", "2.039 (1.996 to 2.084)", 1), results)
    assert readme_problems(text.replace("| `t06_offset` | lost | L2 |", "| `t06_offset` | kept | L2 |", 1), results)
    row = next(line for line in text.splitlines() if line.startswith("| `t05_fill_n` | lost | L1 |"))
    assert readme_problems(text.replace(row + "\n", "", 1), results)
    assert readme_problems(text.replace(row, row + "\n" + row.replace("lost", "kept"), 1), results)
    assert readme_problems(text.replace("1.35 (the lower end", "1.36 (the lower end", 1), results)
    assert readme_problems(text.replace("228 of them", "229 of them", 1), results)
    assert readme_problems(text.replace("18 of 18 measurement jobs returned", "17 of 18 measurement jobs returned", 1), results)
    # the sentence under the Neoverse-N2 heading: the number of runs, the number of jobs and the state of P6
    assert "One run of six jobs on one core type. Prediction P6 failed." in text
    for changed in (
        text.replace("One run of six jobs on one core type.", "Two runs of six jobs on one core type.", 1),
        text.replace("One run of six jobs on one core type.", "One run of five jobs on one core type.", 1),
        text.replace("One run of six jobs on one core type.", "One run of six jobs.", 1),
        text.replace("Prediction P6 failed.", "Prediction P6 held.", 1),
        text.replace("Prediction P6 failed.", "", 1),
        text.replace("### Neoverse-N2\n\nOne run", "### Neoverse-N2\n\nThe single run", 1),
    ):
        assert changed != text
        assert readme_problems(changed, results)


def test_a_changed_result_makes_the_readme_stale():
    text = read(FORWARDT_README)
    results = load()
    changed = copy.deepcopy(results)
    model = models_by_name(changed)["AMD EPYC 7763 64-Core Processor"]
    model["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"]["compiled"]["ratio"] = 2.5
    assert readme_problems(text, changed)
    changed = copy.deepcopy(results)
    models_by_name(changed)["Neoverse-N2"]["loops"]["t05_fill_n"]["cells"]["L1"]["decidable"] = False
    assert readme_problems(text, changed)
    changed = copy.deepcopy(results)
    changed["manifest"][3]["jobs_returned"] = 5
    assert readme_problems(text, changed)
    # the sentence under the Neoverse-N2 heading follows the results: more jobs, a second run, P6 holding
    changed = copy.deepcopy(results)
    models_by_name(changed)["Neoverse-N2"]["jobs"] = 5
    assert readme_problems(text, changed)
    changed = copy.deepcopy(results)
    models_by_name(changed)["Neoverse-N2"]["runs"] = ["40861186704", "40861186705"]
    assert readme_problems(text, changed)
    changed = copy.deepcopy(results)
    models_by_name(changed)["Neoverse-N2"]["pred"]["preds"]["P6"]["state"] = "holds"
    assert readme_problems(text, changed)


def test_the_outcome_claims_of_the_readme_match_results_json():
    """The prose says: letter D; P2 failed above 1.35 on both read models, every sum pair wholly above it;
    P3 held with every L1 write interval above 1.5; P1 held; P6 failed on Neoverse-N2."""
    results = load()
    outcome = results["analysis"]["outcome"]
    assert outcome["letter"] == "D" and outcome["p2_fail_sides"] == ["above"]
    assert outcome["column"] == "holds" and outcome["may_say_lost_sum_and_lost_writes_differ"] is False
    assert len(outcome["both_read_models"]) == 2
    models = read_models(results, "x86-64")
    assert len(models) == 2
    for model in models:
        assert model["pred"]["preds"]["P2"]["state"] == "fails"
        assert model["pred"]["preds"]["P1"]["state"] == "holds"
        assert model["pred"]["preds"]["P3"]["state"] == "holds"
        for loop in ("t05_fill_n", "t06_offset"):
            pairs = model["loops"][loop]["cells"]["L1"]["pairs"]
            assert pairs["compiled"]["ci95"][0] > 1.5 and pairs["aligned"]["ci95"][0] > 1.5
    assert len(sum_cells_above(results)) == 4 * len(models)
    n2 = models_by_name(results)["Neoverse-N2"]
    assert n2["pred"]["preds"]["P6"]["state"] == "fails" and n2["pred"]["preds"]["P6"]["fail_sides"] == ["below"]
    assert n2["jobs"] == 6 and len(n2["runs"]) == 1
    nine_v45 = models_by_name(results)["AMD EPYC 9V45 96-Core Processor"]
    assert nine_v45["read"] is False and nine_v45["jobs"] == 2


def test_the_census_numbers_match_the_plan_and_the_corpus_readme():
    results = load()
    outcome = results["analysis"]["outcome"]["text"]
    assert "228 lost loops" in outcome and "38 source locations" in outcome
    assert "counts 444 lost loops" in read(ROOT / "forwardt" / "PLAN.md")
    assert "forward loops bounded by a variable 228 (38)" in read(ROOT / "corpus" / "README.md")


# ---- the folder READMEs that say "forward loops" --------------------------------------------------------------
# Each row: the file, the wording that names the loops it is about (or points to the variable-bound result), and the
# older flat wording that must not come back (None: the row only requires the new wording to be there).
FOLDER_SCOPE = (
    (
        "arm64/README.md",
        "and that forward loops bounded by `size()` pay little on the AMD models",
        "and that forward loops pay little on the AMD models",
    ),
    (
        "arm64/README.md",
        "- **Forward loops bounded by `size()` keep NEON and cost 1.000x to 1.007x at L1**",
        "- **Forward loops keep NEON and cost 1.000x to 1.007x at L1**",
    ),
    ("arm64/README.md", "matrix multiply and the forward loops bounded by `size()` kept.", "matrix multiply and the forward loops kept."),
    (
        "arm64/README.md",
        "The forward loops here are the sum, the add and the stencil, all bounded by `size()`; loops with a variable bound are not "
        "covered in this folder (see [forwardt/README.md](../forwardt/README.md)).",
        None,
    ),
    (
        "arm64/README.md",
        "- **Negative control** (the forward loops bounded by `size()` stay vectorized in both builds, expected near 1)",
        "- **Negative control** (the forward loops stay vectorized in both builds, expected near 1)",
    ),
    (
        "arm64/README.md",
        "- **Forward loops (sum, add, stencil) vectorized in both builds, no placement effect.**",
        "- **Forward loops vectorized in both builds, no placement effect.**",
    ),
    (
        "siblings/README.md",
        "and the part about forward loops bounded by `size()` holds only under clang.**",
        "and the forward-loop part holds only under clang.**",
    ),
    (
        "siblings/README.md",
        "(18 and 20, every libc++ mode tried):** forward loops bounded by `size()` keep their vectorization.",
        "(18 and 20, every libc++ mode tried):** forward loops keep their vectorization.",
    ),
    (
        "siblings/README.md",
        "`_GLIBCXX_ASSERTIONS`:** forward loops bounded by `size()` pay too.",
        "`_GLIBCXX_ASSERTIONS`:** forward loops pay too.",
    ),
    ("siblings/README.md", "  - forward loops bounded by `size()`: about 1.00x;", "  - forward loops: about 1.00x;"),
    (
        "siblings/README.md",
        "In loops bounded by `size()`, a vectorized loop whose check stays out of the vector body costs about 1.00x on the AMD models",
        "A vectorized loop whose check stays out of the vector body costs about 1.00x on the AMD models",
    ),
    (
        "siblings/README.md",
        '"forward loops pay about nothing" (loops bounded by `size()`) is a property of clang',
        '"forward loops pay about nothing" is a property of clang',
    ),
    ("forwardn/README.md", "and its result is in `forwardt/README.md`;", "(no run of it exists yet)"),
    (
        "forwardn/README.md",
        'The timing in `forwardt/` found a larger cost for the variable-bound sum on the two AMD models it read (see the main README, '
        'section "Forward loops with a variable bound").',
        None,
    ),
    ("corpus/README.md", "The variable-bound sum was timed on clang 18 in `forwardt/`.", None),
    (
        "investigate/vectorizer/reverse-stride2/README.md",
        "The forward loops bounded by `size()` stay vectorized. The only message",
        "The forward loops stay vectorized. The only message",
    ),
    (
        "investigate/vectorizer/reverse-stride2/README.md",
        "In the forward loops bounded by `size()` the counts of the trap exits",
        "In the forward loops the counts of the trap exits",
    ),
    (
        "investigate/vectorizer/reverse-stride2/README.md",
        "### F3. Forward loops bounded by `size()`: the exit counts go into the vector trip count",
        "### F3. Forward loops: the exit counts go into the vector trip count",
    ),
)


def folder_texts():
    return {rel: read(ROOT / rel) for rel in sorted({row[0] for row in FOLDER_SCOPE})}


def squash(text):
    return re.sub(r"\s+", " ", text)


def folder_problems(texts):
    """Words for what is wrong; a line break inside a sentence does not matter."""
    problems = []
    for rel, scoped, flat in FOLDER_SCOPE:
        text = squash(texts[rel])
        if text.count(squash(scoped)) != 1:
            problems.append(f"{rel}: the wording that names the loops is missing or repeated: {scoped[:80]}")
        if flat is not None and squash(flat) in text:
            problems.append(f"{rel}: the older flat wording is back: {flat[:80]}")
    return problems


def test_the_folder_readmes_name_the_loops_their_forward_sentences_are_about():
    assert folder_problems(folder_texts()) == []


def test_taking_the_scope_out_of_a_folder_readme_is_found():
    texts = folder_texts()
    assert len(FOLDER_SCOPE) == 18
    for rel, scoped, flat in FOLDER_SCOPE:
        changed = dict(texts)
        flat_form = squash(flat) if flat is not None else ""
        assert squash(scoped) in squash(texts[rel]), (rel, scoped[:60])
        changed[rel] = squash(texts[rel]).replace(squash(scoped), flat_form, 1)
        assert folder_problems(changed), (rel, scoped[:60])
        if flat is not None:
            changed = dict(texts)
            changed[rel] = texts[rel] + "\n" + flat
            assert folder_problems(changed), (rel, flat[:60])
        changed = dict(texts)
        changed[rel] = texts[rel] + "\n" + scoped
        assert folder_problems(changed), (rel, "repeated", scoped[:60])


if __name__ == "__main__":
    results = load()
    for model in results["analysis"]["models"]:
        if model["read"]:
            print("MODEL", model["cpu_model"], model["jobs"])
            print("\n".join(table_header() + table_rows(model)))
    print("\n".join(sum_cells_above(results)))
