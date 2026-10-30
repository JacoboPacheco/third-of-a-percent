"""The real-program bounds ("consistent with at most 0.2% to 3.3%") and which jobs they cover.

The three early runs that timed json and fmt (the S3 runs, named by scripts/build_site_data.py) returned 12 jobs. A job counts for the page
only when its kernel A/A half-width (the forward add timed against an identical copy of itself, controls.aa in the job file) is at most the
limit of the rule file the same script names. The range of the bounds and of the programs' own A/A floors (a separate control, so they can
exceed the limit) is taken over those jobs only, so the DETAILS bullet has to say how many of the 12 that is, what the others had for an
A/A and how large their bounds were. All of it is recomputed here from the job files under results/ and the rule file; nothing is read from
the site data except as a cross-check of the job count and the limit.

Nothing is written. Tamper tests: a changed number or word in the sentence, and changed copies of the job files or of the limit, have to be
named. Runs with or without pytest (scripts/check.py's built-in runner, which CI uses, has none).
"""

import copy
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_readme_numbers as T  # noqa: E402

BUILDER = os.path.join("scripts", "build_site_data.py")
BULLET = "- **The whole-program columns are an upper bound, not a confirmation.**"


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


def builder_source():
    with open(os.path.join(T.REPO, BUILDER), encoding="utf-8") as f:
        return f.read()


def run_dirs_and_criteria():
    src = builder_source()
    block = re.search(r"^S3_RUNS = \[(.*?)^\]", src, re.M | re.S)
    assert block, f"{BUILDER} no longer lists the S3 runs"
    dirs = re.findall(r'"dir": "([^"]+)"', block.group(1))
    crit = re.search(r'^S3_CRITERIA = "([^"]+)"', src, re.M)
    assert crit, f"{BUILDER} no longer names the rule file of the S3 runs"
    assert len(dirs) == 3, f"{BUILDER} lists {len(dirs)} S3 runs, the sentence is written for three"
    return dirs, crit.group(1)


def load_jobs():
    """Every job file of the S3 runs, as stored (a private copy)."""
    dirs, _ = run_dirs_and_criteria()
    files = [f for d in dirs for f in sorted(glob.glob(os.path.join(T.REPO, "results", d, "results-*", "results.json")))]
    assert files, "no job file under the S3 run folders"
    return [copy.deepcopy(T.J(os.path.relpath(f, T.REPO).replace(os.sep, "/"))) for f in files]


def aa_limit():
    _, crit = run_dirs_and_criteria()
    return T.J(crit)["verdict"]["aa_half_width_max_pct"]


def facts(jobs, limit):
    """The counts and ranges the sentence prints, from the job files."""
    assert all(j.get("programs") for j in jobs), "a job file of the S3 runs holds no program rows: the counts of jobs would change meaning"
    usable = [j for j in jobs if j["controls"]["aa"]["half_width_pct"] <= limit]
    left = [j for j in jobs if j["controls"]["aa"]["half_width_pct"] > limit]
    assert usable and left, "the sentence is about the jobs that were used and the ones that were not: one of the two groups is empty"
    bounds = [p["consistent_with_at_most_pct"] for j in usable for p in j["programs"]]
    floors = [p["aa_half_width_pct"] for j in usable for p in j["programs"]]
    return {
        "used": len(usable), "all": len(jobs), "limit": limit, "left": len(left),
        "lo": min(bounds), "hi": max(bounds), "flo": min(floors), "fhi": max(floors),
        "dlo": min(j["controls"]["aa"]["half_width_pct"] for j in left),
        "dhi": max(j["controls"]["aa"]["half_width_pct"] for j in left),
        "dbound": max(p["consistent_with_at_most_pct"] for j in left for p in j["programs"]),
    }


def sentence(f):
    p = lambda x: f"{x:.1f}"  # noqa: E731
    return (f'json and fmt (earlier runs, S3) are "consistent with at most {p(f["lo"])}% to {p(f["hi"])}%" over the {f["used"]} of {f["all"]} jobs '
            f'whose kernel A/A (the forward add timed against an identical copy of itself, in the same job) was at most {p(f["limit"])}%; '
            f'the {f["left"]} others had a kernel A/A of {p(f["dlo"])}% to {p(f["dhi"])}% and bounds up to {p(f["dbound"])}%. '
            f'Each bound is given next to the program\'s own A/A floor ({p(f["flo"])}% to {p(f["fhi"])}%, a separate control that can exceed {p(f["limit"])}%);')


RANGE = re.compile(r"consistent with at most (\d+\.\d)% to (\d+\.\d)%")


def check(text, jobs, limit, site_rows=None, site_limit=None):
    f = facts(jobs, limit)
    assert f["fhi"] > f["limit"], "the sentence says the programs' own floors can exceed the limit, and no floor of a used job does"
    flat = T.squash(text)
    want = T.squash(sentence(f))
    assert flat.count(want) == 1, f"the document does not hold, once, the sentence the job files give:\n  {want}"
    bullets = [ln for ln in text.splitlines() if ln.startswith(BULLET)]
    assert len(bullets) == 1 and want in T.squash(bullets[0]), f"the sentence is not in the bullet that begins {BULLET}"
    for m in RANGE.finditer(flat):
        assert flat[m.start():].startswith(want[want.index("consistent with"):]), \
            f"the range {m.group(0)!r} appears without the statement of the jobs it covers"
    if site_rows is not None:
        assert site_rows == f["used"], f"the site data lists {site_rows} job rows and the job files give {f['used']} used jobs"
    if site_limit is not None:
        assert site_limit == f["limit"], f"the site data names the limit {site_limit} and the rule file {f['limit']}"


def site_figures():
    p = T.J("site/data/index.json")["programs"]
    return len(p["rows"]), p["aa_max_pct"]


def test_the_counts_and_ranges_are_the_printed_ones():
    f = facts(load_jobs(), aa_limit())
    assert (f["used"], f["all"], f["left"], f["limit"]) == (9, 12, 3, 2.0), f
    p = lambda x: f"{x:.1f}"  # noqa: E731
    assert (p(f["lo"]), p(f["hi"]), p(f["flo"]), p(f["fhi"])) == ("0.2", "3.3", "0.2", "2.4"), f
    assert (p(f["dlo"]), p(f["dhi"]), p(f["dbound"])) == ("3.0", "3.8", "9.7"), f


def test_the_details_say_which_jobs_the_range_covers():
    rows, site_limit = site_figures()
    check(T.details_text(), load_jobs(), aa_limit(), rows, site_limit)


def test_the_readme_gives_no_range_without_its_jobs():
    jobs, limit = load_jobs(), aa_limit()
    flat = T.squash(T.readme_text())
    assert not RANGE.search(flat), "the README gives a real-program range: it needs the sentence about the jobs it covers (see the DETAILS bullet)"
    assert facts(jobs, limit)


def test_a_changed_word_or_number_in_the_sentence_is_caught():
    jobs, limit = load_jobs(), aa_limit()
    f = facts(jobs, limit)
    text = T.details_text()
    base = sentence(f)
    assert text.count(base) == 1
    swaps = [("at most 0.2% to", "at most 0.3% to"), ("to 3.3%\"", "to 3.4%\""), ("over the 9 of 12", "over the 8 of 12"),
             ("over the 9 of 12", "over the 9 of 13"), ("whose kernel A/A (the forward add", "whose A/A (the forward add"),
             ("in the same job)", "in the same run)"), ("at most 2.0%;", "at most 2.5%;"),
             ("the 3 others had a kernel A/A of", "the 3 others had an A/A of"), ("the 3 others", "the 4 others"),
             ("A/A of 3.0%", "A/A of 2.9%"), ("to 3.8% and", "to 3.9% and"),
             ("bounds up to 9.7%", "bounds up to 9.6%"), ("floor (0.2% to 2.4%,", "floor (0.2% to 2.5%,"),
             ("the program's own A/A floor", "the job's own A/A floor"), ("a separate control", "the same control"),
             ("can exceed 2.0%", "can exceed 3.0%"), ("(earlier runs, S3)", "(earlier runs)")]
    for old, new in swaps:
        assert base.count(old) == 1, f"{old!r} is not in the sentence once"
        e = assertion_from(lambda old=old, new=new: check(text.replace(base, base.replace(old, new)), jobs, limit), f"{old!r} -> {new!r}")
        assert "sentence" in str(e) or "range" in str(e), e


def test_a_missing_doubled_or_stray_sentence_is_caught():
    jobs, limit = load_jobs(), aa_limit()
    text = T.details_text()
    base = sentence(facts(jobs, limit))
    assert text.count(base) == 1
    assertion_from(lambda: check(text.replace(base, ""), jobs, limit), "the sentence removed")
    assertion_from(lambda: check(text.replace(base, base + " " + base), jobs, limit), "the sentence twice")
    stray = text + '\n\nA second place says json and fmt are "consistent with at most 0.2% to 3.3%" and stops there.\n'
    assertion_from(lambda: check(stray, jobs, limit), "a range without its jobs, elsewhere in the document")
    moved = text.replace(base, "").replace("\n- **The whole-program columns", "\n" + base + "\n- **The whole-program columns", 1)
    assertion_from(lambda: check(moved, jobs, limit), "the sentence outside the bullet")


def test_changed_job_files_or_limit_are_caught():
    jobs, limit = load_jobs(), aa_limit()
    text = T.details_text()
    check(text, jobs, limit)

    def mutate(fn, what):
        mutated = copy.deepcopy(jobs)
        fn(mutated)
        assertion_from(lambda: check(text, mutated, limit), what)

    def aa_of(job_list, i, v):
        job_list[i]["controls"]["aa"]["half_width_pct"] = v

    used = [i for i, j in enumerate(jobs) if j["controls"]["aa"]["half_width_pct"] <= limit]
    left = [i for i, j in enumerate(jobs) if j["controls"]["aa"]["half_width_pct"] > limit]
    assert len(used) == 9 and len(left) == 3
    mutate(lambda m: aa_of(m, left[0], 1.0), "a left-out job with a small A/A")
    mutate(lambda m: aa_of(m, used[0], 2.5), "a used job with a large A/A")
    mutate(lambda m: m[used[0]]["programs"][0].update(consistent_with_at_most_pct=5.0), "a larger bound in a used job")
    mutate(lambda m: m[used[0]]["programs"][0].update(aa_half_width_pct=0.01), "a smaller floor in a used job")
    mutate(lambda m: [p.update(consistent_with_at_most_pct=12.0) for p in m[left[0]]["programs"]], "a larger bound in a left-out job")
    mutate(lambda m: aa_of(m, left[1], 5.0), "a larger A/A in a left-out job")
    mutate(lambda m: m.append(copy.deepcopy(m[used[0]])), "a thirteenth job")
    mutate(lambda m: m[used[0]].update(programs=[]), "a job with no program rows")
    low_floors = copy.deepcopy(jobs)
    for i in used:
        for p in low_floors[i]["programs"]:
            p["aa_half_width_pct"] = 0.5
    e = assertion_from(lambda: check(text, low_floors, limit), "program floors that no longer exceed the limit")
    assert "can exceed the limit" in str(e), e
    assertion_from(lambda: check(text, jobs, 4.0), "a limit that lets every job in")
    assertion_from(lambda: check(text, jobs, limit, site_rows=8, site_limit=limit), "a site list of 8 rows")
    assertion_from(lambda: check(text, jobs, limit, site_rows=9, site_limit=2.5), "a site limit of 2.5")
