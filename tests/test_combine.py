"""harness/combine.py: the page-level line across CPU models (criteria-v2.json, v2.page_level), on made-up files."""
import combine
import verdict
from test_verdict_v2 import V2, base, get

SHA = "0" * 64


def doc(cpu, aa_hw=0.45, mutate=None, run_id="1"):
    r = base(aa_hw=aa_hw, cpu=cpu)
    if mutate:
        mutate(r)
    r["run"]["id"] = run_id
    r["verdict"] = verdict.compute(r, V2)
    return r


def test_slug():
    assert combine.slug("AMD EPYC 7763 64-Core Processor") == "amd-epyc-7763-64-core-processor"
    assert combine.slug("INTEL(R) XEON(R) PLATINUM 8573C") == "intel-xeon-platinum-8573c"
    assert combine.slug(None) == "unknown-cpu"


def test_map_when_every_usable_cpu_is_map_and_noisy_cpu_is_listed():
    entries = [("a/results.json", doc("EPYC A")), ("b/results.json", doc("EPYC B")),
               ("c/results.json", doc("XEON C", aa_hw=2.1))]
    c = combine.combine(entries, V2, SHA)
    v = c["verdict"]
    assert v["form"] == "map"
    assert v["line"].startswith("On every CPU model drawn with a usable A/A control (EPYC A; EPYC B), loops that lose SIMD")
    assert "Google" not in v["line"]
    assert v["line"].endswith("Not counted (A/A half-width above 2%): XEON C (2.10%).")
    assert v["n"] == {"median": (2.9 + 5.6) / 2, "min": 2.9, "max": 5.6}
    assert [x["form"] for x in c["cpus"]] == ["map", "map", None]


def test_a_cpu_that_differs_is_named():
    def pay(r):
        c = get(r, "k03_stencil.L1")
        c["ratio"], c["ci95"] = 1.10, [1.08, 1.12]
        c["aligned"]["ratio"], c["aligned"]["ci95"] = 1.10, [1.08, 1.12]
    entries = [("a/results.json", doc("EPYC A")), ("b/results.json", doc("EPYC B", mutate=pay))]
    v = combine.combine(entries, V2, SHA)["verdict"]
    assert v["form"] == "inconclusive"
    assert v["line"].startswith("INCONCLUSIVE across CPU models: map on EPYC A; inconclusive on EPYC B (mixed picture")
    assert v["n"] is None


def test_two_runs_of_one_cpu_that_disagree_make_that_cpu_inconclusive():
    def pay(r):
        c = get(r, "k03_stencil.L1")
        c["aligned"]["ratio"], c["aligned"]["ci95"] = 1.10, [1.08, 1.12]
        c["ratio"], c["ci95"] = 1.10, [1.08, 1.12]
    entries = [("a/results.json", doc("EPYC A")), ("b/results.json", doc("EPYC A", mutate=pay))]
    c = combine.combine(entries, V2, SHA)
    assert c["cpus"][0]["form"] == "inconclusive" and "disagree" in c["cpus"][0]["why"]
    assert c["verdict"]["form"] == "inconclusive"


def test_no_usable_cpu():
    entries = [("a/results.json", doc("XEON C", aa_hw=2.1))]
    v = combine.combine(entries, V2, SHA)["verdict"]
    assert v["form"] == "inconclusive" and v["line"].startswith("INCONCLUSIVE: no CPU model drawn had a usable A/A")


def test_noisy_run_of_a_cpu_does_not_vote_when_another_run_of_it_is_usable():
    entries = [("a/results.json", doc("EPYC A")), ("b/results.json", doc("EPYC A", aa_hw=2.5))]
    c = combine.combine(entries, V2, SHA)
    assert c["cpus"][0]["form"] == "map" and c["verdict"]["form"] == "map"


def test_order_of_entries_does_not_matter():
    e = [("b/results.json", doc("EPYC B")), ("a/results.json", doc("EPYC A"))]
    assert combine.combine(e, V2, SHA) == combine.combine(list(reversed(e)), V2, SHA)
