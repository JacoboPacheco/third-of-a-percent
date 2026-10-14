"""harness/schema.py: the fixture passes; drift in either direction fails."""
import copy
import json
import os

import schema

FIXTURE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "fixture.json")


def load():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)


def fails(doc):
    try:
        schema.validate(doc)
    except schema.SchemaError:
        return True
    return False


def test_fixture_is_valid_and_marked_sample():
    doc = load()
    schema.validate(doc)
    assert doc["sample"] is True


def test_missing_and_extra_keys_fail():
    doc = load()
    d = copy.deepcopy(doc)
    del d["cells"][0]["ratio"]
    assert fails(d)
    d = copy.deepcopy(doc)
    d["cells"][0]["extra"] = 1
    assert fails(d)
    d = copy.deepcopy(doc)
    d["run"]["runner"]["gpu"] = "x"
    assert fails(d)


def test_bad_values_fail():
    doc = load()
    for mutate in (
        lambda d: d["cells"][0].__setitem__("cell_id", "k01_sum_fwd.L3"),
        lambda d: d["cells"][0].__setitem__("ci95", [1.2, 1.1]),
        lambda d: d["cells"][0].__setitem__("none_sha256", "abc"),
        lambda d: d["verdict"].__setitem__("form", "maybe"),
        lambda d: d["verdict"].__setitem__("n", None),
        lambda d: d["controls"].__setitem__("negative", ["k99_x.L1"]),
        lambda d: d["prior_numbers"].append({"source": "s", "figure": "f", "url": "u", "verified": False}),
        lambda d: d.__setitem__("schema", 2),
    ):
        d = copy.deepcopy(doc)
        mutate(d)
        assert fails(d)
