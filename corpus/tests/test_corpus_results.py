"""The committed census results pass the schema check, and the checks catch breakage."""
import copy
import glob
import json
import os
import shutil
import tempfile

import _path  # noqa: F401
import finalize
import schema


def result_dirs():
    return sorted(glob.glob(os.path.join(_path.REPO, "results", "corpus*-run-*")))


def load(d, name):
    with open(os.path.join(d, name), encoding="utf-8") as f:
        return json.load(f)


def test_committed_results_pass_schema():
    for d in result_dirs():
        assert schema.check_dir(d) == [], d


def test_committed_controls_pass():
    for d in result_dirs():
        c = load(d, "corpus.json")
        for name in ("remark_crosscheck", "determinism"):
            assert c["controls"][name]["pass"] is True, (d, name)
        k = c["controls"]["kernels"]
        if c.get("target", "baseline") == "baseline":
            assert k["pass"] is True, (d, "kernels")
            if "index_evidence" in k:
                assert k["index_evidence"]["pass"] is True, (d, "kernel index evidence")
        else:
            # avx2 (corpus/PLAN2.md, change 9): the registered rule expected k08_matmul lost; at
            # -march=x86-64-v3 it is vectorized in both builds. The FAIL is kept, and only that.
            bad = [r["kernel"] for r in k["kernels"] if not r["pass"]]
            assert k["pass"] is True or bad == ["k08_matmul"], (d, bad)


def test_schema_catches_breakage():
    for d in result_dirs()[:1]:
        c, lost = load(d, "corpus.json"), load(d, "lost_loops.json")
        bad = copy.deepcopy(c)
        bad["totals"]["lost"] += 1
        assert schema.check_corpus(bad, lost)
        bad = copy.deepcopy(c)
        bad["projects"][0]["ud2_added"] += 1
        assert schema.check_corpus(bad, lost)
        if lost["lost"]:
            lost2 = copy.deepcopy(lost)
            lost2["lost"][0]["class"] = "sideways"
            assert schema.check_corpus(c, lost2)


def test_determinism_compare():
    tmp = tempfile.mkdtemp()
    try:
        a, b = os.path.join(tmp, "a"), os.path.join(tmp, "b")
        for d in (a, b):
            os.makedirs(d)
            for name in finalize.COMPARED:
                with open(os.path.join(d, name), "w") as f:
                    f.write("same\n" if name != "objects.sha256" else "ab  x/y.o\n")
        assert finalize.determinism(a, b)["pass"]
        with open(os.path.join(b, "objects.sha256"), "w") as f:
            f.write("cd  x/y.o\n")
        r = finalize.determinism(a, b)
        assert not r["pass"] and r["build_files_differing"] == ["x/y.o"]
    finally:
        shutil.rmtree(tmp)
