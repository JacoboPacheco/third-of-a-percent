"""The headline range of the loops that lose SIMD joins two columns (as compiled, aligned); the page prints each column's own range
beside it, in small print only.

The ranges are recomputed here from the cells of results/s7-pooled/pooled.json (the CPU models with enough jobs and a verdict
that reached a form, the lost loops at the two in-cache sizes), without the code that builds site/data/index.json, and compared with
the data file and with the numbers printed in site/index.html and site/details.html. No pytest import: the tests are plain functions
the built-in runner of scripts/check.py can call.
"""
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOLED = "results/s7-pooled/pooled.json"
IN_CACHE = ("L1", "L2")


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def load(rel):
    return json.loads(read(rel))


def column_ranges():
    """{column: (lowest, highest)} over the lost cells of the judged CPU models, from the raw pooled file."""
    minimum = load("site/data/index.json")["criteria"]["minimum_jobs"]
    values = {"as_compiled": [], "aligned": []}
    models = []
    for cpu in load(POOLED)["cpus"]:
        if cpu["jobs"] < minimum or cpu["verdict"]["form"] == "inconclusive":
            continue
        models.append(cpu["cpu_model"])
        for cell in cpu["cells"]:
            if cell["class"] == "lost" and cell["size_class"] in IN_CACHE:
                for column in values:
                    values[column].append(cell[column]["ratio"])
    return {column: (min(v), max(v)) for column, v in values.items()}, models


def spans(html, name):
    return re.findall(r'<span data-v="%s"[^>]*>([^<]*)</span>' % name, html)


def test_the_page_data_holds_each_columns_range_from_the_pooled_file():
    ranges, models = column_ranges()
    page = load("site/data/index.json")["page"]
    assert len(models) == len(page["judged_cpus"]) > 0, "the judged CPU models in the data are not the ones the pooled file gives"
    for key, column in (("lost_compiled", "as_compiled"), ("lost_aligned", "aligned")):
        lo, hi = ranges[column]
        assert abs(page[key]["min"] - lo) < 1e-9 and abs(page[key]["max"] - hi) < 1e-9, \
            f"page.{key} is {page[key]}, the pooled file gives {lo} to {hi}"
    union = (min(ranges["as_compiled"][0], ranges["aligned"][0]), max(ranges["as_compiled"][1], ranges["aligned"][1]))
    assert abs(page["lost"]["min"] - union[0]) < 1e-9 and abs(page["lost"]["max"] - union[1]) < 1e-9, \
        "the headline range is no longer the union of the two columns"


def test_the_ends_of_the_headline_range_belong_to_one_column_each():
    """The sentence next to the pair says the smallest figure is as compiled and the largest is aligned; hold the data to it."""
    ranges, _ = column_ranges()
    assert ranges["as_compiled"][0] < ranges["aligned"][0], "the smallest figure is no longer the as-compiled one"
    assert ranges["aligned"][1] > ranges["as_compiled"][1], "the largest figure is no longer the aligned one"


def test_the_printed_pair_equals_the_data_and_sits_in_small_print_only():
    ranges, _ = column_ranges()
    want = {"lostCompMin": ranges["as_compiled"][0], "lostCompMax": ranges["as_compiled"][1],
            "lostAlnMin": ranges["aligned"][0], "lostAlnMax": ranges["aligned"][1]}
    index = read("site/index.html")
    details = read("site/details.html")
    start = index.index('<section id="result">')
    end = index.index("</section>", start)
    for name, value in want.items():
        for label, html in (("index.html", index), ("details.html", details)):
            printed = spans(html, name)
            assert printed == [f"{value:.1f}"], f"{label}: {name} prints {printed}, the data gives {value:.1f}"
        # on the main page the pair is only in the Result section (not in the hero, the abstract, the no-script text or the share card)
        assert start < index.index(f'data-v="{name}"') < end, f"index.html: {name} is outside the Result section"
    # on the details page it stands in the line that gives the headline range
    li = details[details.rindex("<li>", 0, details.index('data-v="lostCompMin"')):]
    li = li[:li.index("</li>")]
    assert 'data-v="lostMin"' in li and 'data-v="lostAlnMax"' in li, "details.html: the pair is not in the headline range's line"


def test_the_script_binds_the_four_numbers_from_the_data():
    js = read("site/app.js")
    for name, source in (("lostCompMin", "pg.lost_compiled.min"), ("lostCompMax", "pg.lost_compiled.max"),
                         ("lostAlnMin", "pg.lost_aligned.min"), ("lostAlnMax", "pg.lost_aligned.max")):
        assert f"{name}: {source}.toFixed(1)" in js, f"site/app.js does not bind {name} to {source}"
