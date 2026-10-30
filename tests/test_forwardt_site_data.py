"""site/data/forwardt.json carries the numbers of forwardt/results.json and nothing else: the pooled ratios and intervals, the words,
the decidable flags, the outcome letter and the census count are recomputed here from the stored analysis. A number changed in the
site file, or a cell reported where the analysis marks it undecidable, fails.

Runs with pytest or with the built-in runner of scripts/check.py (pytest is optional here)."""
import copy
import hashlib
import json
import os

try:
    import pytest
except ImportError:  # the built-in runner of scripts/check.py runs this file without pytest
    pytest = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return json.load(fh)


SITE = _load("site/data/forwardt.json")
SRC = _load("forwardt/results.json")
MODELS = SRC["analysis"]["models"]


def _site_model(cpu_model):
    for m in SITE["models"]:
        if m["cpu_model"] == cpu_model:
            return m
    raise AssertionError(f"{cpu_model} is not in site/data/forwardt.json")


def _cells_of(src_model):
    """Every pooled cell of one source model: {(loop, size, column): (ratio, lo, hi)} for the columns the site file keeps."""
    out = {}
    sm = _site_model(src_model["cpu_model"])
    for l in sm["loops"]:
        for size, c in l["cells"].items():
            for col in ("compiled", "aligned", "novec"):
                if c.get(col):
                    out[(l["id"], size, col)] = (c[col]["ratio"], c[col]["ci95"][0], c[col]["ci95"][1])
    return out


def _source_numbers(src_model):
    """Collect (ratio, lo, hi) triples stored in the source model, by walking it; used to find each site number in the analysis."""
    found = set()

    def walk(o):
        if isinstance(o, dict):
            if "ratio" in o and "ci95" in o and isinstance(o["ci95"], list) and len(o["ci95"]) == 2:
                found.add((o["ratio"], o["ci95"][0], o["ci95"][1]))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(src_model)
    return found


def check_every_cell_is_in_the_analysis():
    assert len(SITE["models"]) == len(MODELS)
    for src in MODELS:
        have = _source_numbers(src)
        mine = _cells_of(src)
        if not src.get("read", True):
            assert not mine, f"{src['cpu_model']} is not read; the site file must report none of its cells"
            continue
        assert mine, f"no cells for {src['cpu_model']}"
        for key, triple in mine.items():
            assert triple in have, f"{src['cpu_model']} {key}: {triple} is not a number of forwardt/results.json"


def check_models_and_job_counts_follow_the_source():
    for src in MODELS:
        sm = _site_model(src["cpu_model"])
        assert sm["jobs"] == src["jobs"] and sm["read"] == (src["jobs"] >= SITE["minimum_jobs"])
        if not sm["read"]:
            assert sm["loops"] == [], "a model that is not read has no loop rows"


def check_a_cell_is_decidable_exactly_when_its_aa_is_within_the_limit():
    """The data file keeps the numbers of every cell; the page shows a cell only where this flag is set (site/app.js)."""
    n_no = 0
    for m in SITE["models"]:
        for l in m["loops"]:
            for size, c in l["cells"].items():
                within = c["aa_half_width_pct"] <= SITE["forward_rule"]["floor"]
                assert c["decidable"] == within, (m["cpu_short"], l["id"], size, c["aa_half_width_pct"], c["decidable"])
                n_no += not within
    assert n_no > 0, "the Neoverse-N2 L2 cells are above the A/A limit; the flag must be able to say so"


def check_the_outcome_and_the_census_count_follow_the_source():
    a = SRC["analysis"]
    out = a["outcome"]
    assert SITE["outcome"]["letter"] == out["letter"] and SITE["outcome"]["text"] == out["text"]
    assert SITE["outcome"]["row"] == out["row"] and SITE["outcome"]["column"] == out["column"]
    assert SITE["outcome"]["p2_fail_sides"] == ["above"], "the plan's letter D: P2 fails above"
    assert f"{SITE['census']['lost_loops']} lost loops" in SITE["outcome"]["text"]
    assert f"{SITE['census']['source_locations']} source locations" in SITE["outcome"]["text"]
    assert SITE["outcome"]["may_say_lost_sum_and_lost_writes_differ"] is False


def check_the_plan_is_the_one_the_results_name():
    with open(os.path.join(REPO, "forwardt", "PLAN.md"), "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    assert SITE["plan_sha256"] == sha == SRC["plan_sha256"]


def check_the_forward_listing_covers_the_four_variable_bound_loops():
    ids = {row["loop"] for row in SITE["forward_listing"]}
    assert ids == {"t02_sum_n", "t04_scale_n", "t05_fill_n", "t06_offset"}
    for row in SITE["forward_listing"]:
        assert row["none_decidable"] == (not row["cells"])
        for c in row["cells"]:
            assert c["aa_half_width_pct"] <= SITE["forward_rule"]["floor"]


def check_a_tampered_number_is_caught():
    bad = copy.deepcopy(SITE)
    cell = next(c for l in bad["models"][0]["loops"] for c in l["cells"].values() if c.get("aligned"))
    cell["aligned"]["ratio"] += 0.01
    have = _source_numbers(MODELS[0])
    assert (cell["aligned"]["ratio"], cell["aligned"]["ci95"][0], cell["aligned"]["ci95"][1]) not in have


# Cells are compared by their own key (model, loop id, size, column), and each loop's word is compared with the stored word of the
# same loop: a number that exists in the analysis but sits in the wrong cell, or a word moved to another loop, fails.
COLUMNS = ("compiled", "aligned", "novec", "placement")


def _source_cells(src_model):
    out = {}
    for lid, l in src_model["loops"].items():
        for size, c in l["cells"].items():
            pairs = c.get("pairs") or {}
            for col in COLUMNS:
                p = c.get("placement") if col == "placement" else pairs.get(col)  # the placement pair is stored beside `pairs`
                if p:
                    out[(src_model["cpu_model"], lid, size, col)] = (p["ratio"], p["ci95"][0], p["ci95"][1])
    return out


def _site_cells(site_model):
    out = {}
    for l in site_model["loops"]:
        for size, c in l["cells"].items():
            for col in COLUMNS:
                p = c.get(col)
                if p:
                    out[(site_model["cpu_model"], l["id"], size, col)] = (p["ratio"], p["ci95"][0], p["ci95"][1])
    return out


def _cell_diffs(site_model, src_model):
    """The keys at which the site model's cell differs from the stored one (a missing cell on either side counts)."""
    mine, theirs = _site_cells(site_model), _source_cells(src_model)
    return sorted(k for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k))


def _word_diffs(site_model, src_model):
    diffs = []
    src_ids = set(src_model["loops"])
    site_ids = {l["id"] for l in site_model["loops"]}
    if src_ids != site_ids:
        diffs.append(("loop ids", sorted(src_ids ^ site_ids)))
    for l in site_model["loops"]:
        s = src_model["loops"].get(l["id"])
        if s is None:
            continue
        stored_words = {"agree": s["words"]["agree"], "aligned": s["words"]["aligned"]["word"], "compiled": s["words"]["compiled"]["word"]}
        if l["word"] != s["word"] or l["words"] != stored_words:
            diffs.append((l["id"], l["word"], s["word"]))
    return diffs


def _read_pairs():
    """(site model, source model) for every model the page reads, matched by CPU model name."""
    return [(_site_model(src["cpu_model"]), src) for src in MODELS if src.get("read", True)]


def check_every_cell_sits_in_the_same_cell_of_the_analysis():
    pairs = _read_pairs()
    assert len(pairs) >= 3, "the page reads the two AMD models and Neoverse-N2"
    for sm, src in pairs:
        diffs = _cell_diffs(sm, src)
        assert not diffs, f"{src['cpu_model']}: cells that differ from the stored ones (model, loop, size, column): {diffs[:6]}"


def check_every_loop_word_is_the_stored_word_of_that_loop():
    for sm, src in _read_pairs():
        diffs = _word_diffs(sm, src)
        assert not diffs, f"{src['cpu_model']}: loop words that differ from the stored ones: {diffs}"


def _caption_sums(site):
    """What the caption of Figure 'ft' computes (site/app.js ftSums): the lost sum's aligned L1 ratio of each decidable model."""
    out = {"amd": [], "arm": []}
    for m in site["models"]:
        if not m["read"]:
            continue
        l = next((x for x in m["loops"] if x["id"] == "t02_sum_n"), None)
        c = l and l["cells"].get("L1")
        if c and c["decidable"] and c.get("aligned"):
            out["amd" if m["target"] == "x86-64" else "arm"].append(c["aligned"]["ratio"])
    return out


def _stored_sums():
    """The same numbers read from forwardt/results.json alone, the decidable flag from the stored cell."""
    out = {"amd": [], "arm": []}
    for src in MODELS:
        if not src.get("read", True):
            continue
        c = src["loops"]["t02_sum_n"]["cells"]["L1"]
        if c["decidable"] and (c.get("pairs") or {}).get("aligned"):
            out["amd" if src["target"] == "x86-64" else "arm"].append(c["pairs"]["aligned"]["ratio"])
    return out


def check_the_caption_numbers_are_the_stored_lost_sum_cells():
    site_sums, stored = _caption_sums(SITE), _stored_sums()
    assert site_sums == stored, (site_sums, stored)
    assert len(stored["amd"]) >= 2 and len(stored["arm"]) == 1, stored
    p2 = SITE["models"][0]["predictions"]["P2"]
    hi = max(it["band"]["hi"] for it in p2["items"])
    assert min(stored["amd"]) > hi, f"the caption says the sum failed its band on the AMD models: min {min(stored['amd'])} against the band's upper end {hi}"
    assert min(stored["arm"]) > max(stored["amd"]), "the caption puts the Neoverse-N2 sum above the AMD range"


def check_swapped_cells_and_flipped_words_are_caught():
    src, sm = MODELS[0], _site_model(MODELS[0]["cpu_model"])
    assert _cell_diffs(sm, src) == [] and _word_diffs(sm, src) == []
    # two loops swap their aligned L1 cell: both numbers still exist in the analysis, in the wrong place
    bad = copy.deepcopy(sm)
    a = next(l for l in bad["loops"] if l["id"] == "t02_sum_n")
    b = next(l for l in bad["loops"] if l["id"] == "t04_scale_n")
    a["cells"]["L1"]["aligned"], b["cells"]["L1"]["aligned"] = b["cells"]["L1"]["aligned"], a["cells"]["L1"]["aligned"]
    keys = {k[1] for k in _cell_diffs(bad, src)}
    assert {"t02_sum_n", "t04_scale_n"} <= keys, keys
    # a word moves to another loop's value
    bad = copy.deepcopy(sm)
    loop = next(l for l in bad["loops"] if l["id"] == "t02_sum_n")
    loop["word"] = "kept" if loop["word"] != "kept" else "lost"
    assert [d[0] for d in _word_diffs(bad, src)] == ["t02_sum_n"]
    # a caption number that no stored cell carries
    bad_site = copy.deepcopy(SITE)
    cell = next(l for l in bad_site["models"][0]["loops"] if l["id"] == "t02_sum_n")["cells"]["L1"]
    cell["aligned"]["ratio"] += 0.5
    assert _caption_sums(bad_site) != _stored_sums()


ALL = [check_every_cell_is_in_the_analysis, check_models_and_job_counts_follow_the_source, check_a_cell_is_decidable_exactly_when_its_aa_is_within_the_limit,
       check_the_outcome_and_the_census_count_follow_the_source, check_the_plan_is_the_one_the_results_name,
       check_the_forward_listing_covers_the_four_variable_bound_loops, check_a_tampered_number_is_caught,
       check_every_cell_sits_in_the_same_cell_of_the_analysis, check_every_loop_word_is_the_stored_word_of_that_loop,
       check_the_caption_numbers_are_the_stored_lost_sum_cells, check_swapped_cells_and_flipped_words_are_caught]

if pytest is not None:
    @pytest.mark.parametrize("fn", ALL, ids=[f.__name__ for f in ALL])
    def test_forwardt_site_data(fn):
        fn()
else:
    def test_forwardt_site_data_all():
        for fn in ALL:
            fn()
