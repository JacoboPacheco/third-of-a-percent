"""The whole-program ranges of the earlier S3 runs leave out every job whose kernel A/A half-width (the forward add timed against an
identical copy of itself, controls.aa in the job file) is above the S3 limit; the page says how many jobs that is instead of dropping
them without a word, and says that the noise floors printed beside the bounds are a separate control (each program's own).

The jobs are recomputed here from results/s3-*/results-*/results.json and the limit from harness/criteria-v2.json, without the code that
builds site/data/index.json, and compared with index.json's `programs` (rows, excluded, jobs_total, the two ranges of the left-out jobs)
and with the details page (heading, Table 8 note, and the script that binds the count from the data). A run counts when every one of its
jobs timed both programs (the earlier run that timed fmt only does not). No pytest import: the tests are plain functions the built-in
runner of scripts/check.py can call.
"""
import copy
import glob
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRITERIA = "harness/criteria-v2.json"


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def load(rel):
    return json.loads(read(rel))


def recompute():
    """(limit, used, left_out): each job as (run id, job, A/A half-width %, {program: at-most %}), from the raw S3 result files."""
    limit = load(CRITERIA)["verdict"]["aa_half_width_max_pct"]
    runs = {}
    for path in sorted(glob.glob(os.path.join(REPO, "results", "s3-*", "results-*", "results.json"))):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        run_dir = os.path.basename(os.path.dirname(os.path.dirname(path)))
        job = os.path.basename(os.path.dirname(path)).rsplit("-", 1)[-1]
        names = {p["name"].split("_")[0]: p["consistent_with_at_most_pct"] for p in doc.get("programs", [])}
        runs.setdefault(re.search(r"(\d+)$", run_dir).group(1), []).append((job, doc["controls"]["aa"]["half_width_pct"], names))
    used, left_out = [], []
    for run_id, jobs in runs.items():
        if not all({"json", "fmt"} <= set(names) for _, _, names in jobs):
            continue  # the earlier run that timed fmt only is not in the table
        for job, half_width, names in jobs:
            (left_out if half_width > limit else used).append((run_id, job, half_width, names))
    return limit, used, left_out


def span(values):
    return {"min": min(values), "max": max(values)}


def problems(programs, limit, used, left_out):
    """Everything in index.json's `programs` that differs from the recomputed jobs (empty when they agree)."""
    out = []
    if programs["aa_max_pct"] != limit:
        out.append("aa_max_pct")
    if programs["jobs_total"] != len(used) + len(left_out):
        out.append("jobs_total")
    if sorted((r["run_id"], r["job"]) for r in programs["rows"]) != sorted((u[0], u[1]) for u in used):
        out.append("rows")
    if sorted((e["run_id"], e["job"]) for e in programs["excluded"]) != sorted((u[0], u[1]) for u in left_out):
        out.append("excluded jobs")
    by_key = {(e["run_id"], e["job"]): e for e in programs["excluded"]}
    for run_id, job, half_width, names in left_out:
        e = by_key.get((run_id, job))
        if e is None:
            continue
        if abs(e["aa_half_width_pct"] - half_width) > 1e-9:
            out.append(f"A/A of {run_id} {job}")
        if {k: q["at_most_pct"] for k, q in e["programs"].items()} != names:
            out.append(f"at-most of {run_id} {job}")
    if left_out:
        if programs["excluded_aa_pct"] != span([u[2] for u in left_out]):
            out.append("excluded_aa_pct")
        if programs["excluded_at_most_pct"] != span([v for u in left_out for v in u[3].values()]):
            out.append("excluded_at_most_pct")
    if used and programs["at_most_pct"] != span([v for u in used for v in u[3].values()]):
        out.append("at_most_pct")
    return out


def test_the_page_data_counts_the_jobs_left_out_as_recomputed_from_the_s3_results():
    limit, used, left_out = recompute()
    assert limit == 2.0 and (len(used), len(left_out)) == (9, 3), (limit, len(used), len(left_out))
    programs = load("site/data/index.json")["programs"]
    assert problems(programs, limit, used, left_out) == []
    assert programs["criteria"] == CRITERIA


def test_every_left_out_job_has_a_noise_floor_above_the_limit_and_every_row_at_or_below_it():
    limit, used, left_out = recompute()
    assert all(u[2] > limit for u in left_out) and all(u[2] <= limit for u in used)
    programs = load("site/data/index.json")["programs"]
    assert all(e["aa_half_width_pct"] > programs["aa_max_pct"] for e in programs["excluded"])
    # the gate is the job's own kernel-level identical-binary A/A (controls.aa), not a program's own noise floor, which may be larger


def test_the_comparison_catches_a_changed_count_job_or_number():
    limit, used, left_out = recompute()
    programs = load("site/data/index.json")["programs"]
    assert problems(programs, limit, used, left_out) == []
    for label, change in (
        ("jobs_total", lambda p: p.update(jobs_total=p["jobs_total"] + 1)),
        ("a left-out job removed", lambda p: p["excluded"].pop()),
        ("a left-out job moved to the rows", lambda p: p["rows"].append(p["excluded"].pop())),
        ("A/A", lambda p: p["excluded"][0].update(aa_half_width_pct=p["excluded"][0]["aa_half_width_pct"] + 0.01)),
        ("at-most", lambda p: next(iter(p["excluded"][0]["programs"].values())).update(at_most_pct=0.0)),
        ("the A/A range", lambda p: p["excluded_aa_pct"].update(max=p["excluded_aa_pct"]["max"] + 0.01)),
        ("the largest bound", lambda p: p["excluded_at_most_pct"].update(max=p["excluded_at_most_pct"]["max"] + 0.1)),
        ("the limit", lambda p: p.update(aa_max_pct=3.0)),
    ):
        tampered = copy.deepcopy(programs)
        change(tampered)
        assert problems(tampered, limit, used, left_out) != [], label


def test_the_details_page_names_the_limit_and_binds_the_count_from_the_data():
    details = read("site/details.html")
    heading = re.search(r"<h2><span class=\"secno\">7b</span>([^<]*)</h2>", details).group(1)
    assert heading.endswith("every job within the A/A limit"), heading
    cap = re.search(r'<p class="tcap" id="prog-cap">(.*?)</p>', details, re.S).group(1)
    assert "every job within the A/A limit" in cap and '<span data-v="progLeft"></span>' in cap and "fmt only" in cap
    assert not re.search(r"\d+ of \d+ jobs", cap), "the count is bound from the data, not typed"
    script = read("site/app.js")
    assert "v.progLeft = " in script and "P.excluded.length" in script and "P.jobs_total" in script and "P.aa_max_pct" in script
    assert "excluded_aa_pct" in script and "excluded_at_most_pct" in script and "P.rows.length" in script
    assert not re.search(r"\b3 of 12\b", script) and not re.search(r"\b3 of 12\b", details)
    # the control that gates the jobs is the kernel A/A; the floors in the table are another control, bound from the data too
    assert "left out because their kernel A/A was above" in script and "whose kernel A/A (the forward add timed against an identical copy of itself, in the same job)" in script
    assert "are a separate control, each program’s own build timed against an identical copy of itself, and run up to ${pct(P.aa_pct.max)}%" in script
    assert "own A/A was above" not in script and "whose own A/A" not in script
