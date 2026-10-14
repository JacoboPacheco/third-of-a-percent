"""Tests for harness/programs.py: the pins, the whole-program bound, Cachegrind totals and remark counts."""
import os
import re

import programs

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fetch_shas(name):
    with open(os.path.join(REPO, "programs", name, "fetch.sh"), encoding="utf-8") as f:
        text = f.read()
    return re.findall(r"^\s+([0-9a-f]{64})\s*$", text, re.M), text


def test_every_program_has_a_fetch_script_and_a_source():
    for name, spec in programs.PROGRAMS.items():
        assert os.path.isfile(os.path.join(REPO, "programs", name, "fetch.sh")), name
        assert os.path.isfile(os.path.join(REPO, spec["source"])), name


def test_fetch_scripts_check_every_download_and_match_the_pins():
    for name, spec in programs.PROGRAMS.items():
        shas, text = _fetch_shas(name)
        assert shas, f"{name}: no sha256 in fetch.sh"
        assert text.count("fetch https://") == len(shas), f"{name}: a download without a sha256"
        assert "sha256sum -c" in text and "set -euo pipefail" in text
        for sha in shas:
            assert sha in spec["pin"], f"{name}: {sha} is in fetch.sh but not in the pin string"


def test_pins_name_a_tag_commit():
    for spec in programs.PROGRAMS.values():
        assert re.search(r"tag commit [0-9a-f]{40}", spec["pin"])


def test_bound_is_the_interval_top_when_above_the_floor():
    assert abs(programs.consistent_with_at_most_pct([0.99, 1.031], 1.14) - 3.1) < 1e-9


def test_bound_never_below_the_aa_floor():
    # day-one json_parse: ci95_hi 1.003 but A/A floor 1.14 %: the row may not claim 0.3 %
    assert programs.consistent_with_at_most_pct([0.986, 1.003], 1.14) == 1.14


def test_bound_never_negative():
    assert programs.consistent_with_at_most_pct([0.949, 0.993], 0.0) == 0.0
    assert programs.consistent_with_at_most_pct([0.949, 0.993], None) == 0.0


CG = """version: 1
creator: valgrind-3.22.0
cmd: build/json_parse.none build/deps/json_parse/twitter.json 1
events: Ir
fl=/x/json.hpp
fn=main
5 100
summary: 123456789
"""


def test_summary_ir():
    assert programs.summary_ir(CG) == 123456789
    assert programs.summary_ir("events: Ir\nfn=main\n1 2\n") is None
    multi = "events: Dr Ir\nsummary: 7 42\n"
    assert programs.summary_ir(multi) == 42


def test_per_iteration_ir_removes_startup():
    assert programs.per_iteration_ir(1_000_000, 1_000_000 + 2 * 40_000) == 40_000
    assert programs.per_iteration_ir(None, 5) is None
    assert programs.per_iteration_ir(10, 10) is None


REMARKS = """\
/w/json.hpp:100:5: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]
/w/json.hpp:100:5: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]
/w/json.hpp:200:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]
/w/json.hpp:200:3: remark: loop not vectorized [-Rpass-missed=loop-vectorize]
  200 |   for (;;) {}
      |   ^
/w/vector:300:7: remark: loop not vectorized [-Rpass-missed=loop-vectorize]
/w/vector:300:7: remark: vectorized loop (vectorization width: 2, interleaved count: 1) [-Rpass=loop-vectorize]
"""


def test_remark_counts_distinct_locations():
    # 100:5 vectorized (twice, one location); 200:3 refused once (analysis line not counted);
    # 300:7 refused in one instance and vectorized in another: counted as vectorized
    assert programs.remark_counts(REMARKS) == {"vectorized": 2, "not_vectorized": 1}
    assert programs.remark_counts("") == {"vectorized": 0, "not_vectorized": 0}
