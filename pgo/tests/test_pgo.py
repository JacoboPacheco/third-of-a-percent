"""Tests of the PGO column's code (pgo/*.py) on made-up inputs; no compiler, no runner, no results.

Run: python -m unittest discover -s pgo/tests   (or pytest pgo/tests: the tests are plain unittest cases)
"""
import json
import os
import stat
import subprocess
import sys
import tempfile
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PGO = os.path.dirname(HERE)
REPO = os.path.dirname(PGO)
for p in (os.path.join(REPO, "harness"), os.path.join(REPO, "realworld"), os.path.join(REPO, "realworld", "tests"), PGO):
    sys.path.insert(0, p)

import analyze  # noqa: E402
import build  # noqa: E402
import build_pgo  # noqa: E402
import pool_pgo  # noqa: E402
import tag_job  # noqa: E402
from test_realworld import job  # noqa: E402  (made-up realworld-job documents)

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("pgo_check", os.path.join(PGO, "check.py"))
pgo_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pgo_check)  # by path: realworld/check.py has the same module name

CPU = "AMD EPYC 7763 64-Core Processor"
ROWS_NOPGO = {"a": (1.05, 1.05, 1.0), "b": (1.00, 1.00, 1.0), "c": (1.03, 1.03, 1.0)}
ROWS_PGO = {"a": (1.01, 1.01, 1.0), "b": (1.00, 1.00, 1.0), "c": (1.06, 1.06, 1.0)}


def tagged_jobs(rows, run_id, n=3, cpu=CPU, seed0=1):
    docs = []
    with tempfile.TemporaryDirectory() as d:
        for prog in rows:
            for name in ("none", "fast", "none_a64", "fast_a64"):
                with open(os.path.join(d, f"{prog}.{name}"), "wb") as f:
                    f.write(name.encode())
        for j in range(n):
            doc = job(run_id, j + 1, cpu, rows, seed0 + j)
            tag_job.tag(doc, d, run_id)
            docs.append(doc)
    return docs


def write_jobs(base, docs, prefix="results"):
    entries = []
    for i, doc in enumerate(docs):
        rel = f"jobs/{prefix}-{i}/results-{prefix}-{i}.json"
        os.makedirs(os.path.join(base, os.path.dirname(rel)), exist_ok=True)
        with open(os.path.join(base, rel), "w", encoding="utf-8") as f:
            json.dump(doc, f)
        entries.append(rel)
    return entries


class TestBuildRegistration(unittest.TestCase):
    def test_flags(self):
        build_pgo.register_builds("fast", "/p/x.profdata")
        self.assertIn(build.FAST, build.BUILDS["fast_gen"])
        self.assertIn("-fprofile-instr-generate", build.BUILDS["fast_gen"])
        self.assertIn("-fprofile-instr-use=/p/x.profdata", build.BUILDS["fast_pgo"])
        self.assertNotIn(build.ALIGN, build.BUILDS["fast_pgo"])
        self.assertIn(build.ALIGN, build.BUILDS["fast_pgo_a64"])
        self.assertNotIn(build.NONE, build.BUILDS["fast_pgo"])

    def test_each_mode_has_its_own_profile(self):
        build_pgo.register_builds("none", "/p/none.profdata")
        build_pgo.register_builds("fast", "/p/fast.profdata")
        self.assertIn("-fprofile-instr-use=/p/none.profdata", build.BUILDS["none_pgo"])
        self.assertIn("-fprofile-instr-use=/p/fast.profdata", build.BUILDS["fast_pgo"])


class FakeRun:
    def __init__(self, stderr=""):
        self.cmds, self.stderr = [], stderr

    def __call__(self, cmd, cwd=None):
        self.cmds.append(cmd)
        return types.SimpleNamespace(returncode=0, stdout="", stderr=self.stderr), 0.1


class TestRemarkCapture(unittest.TestCase):
    def setUp(self):
        self.orig = build.run

    def tearDown(self):
        build.run = self.orig

    def test_remark_flags_only_on_plain_pgo_compiles(self):
        fake = FakeRun("a.cpp:10:3: remark: vectorized loop [-Rpass=loop-vectorize]\n")
        build.run = fake
        cap = build_pgo.RemarkCapture()
        cap.install()
        use = ["clang++-18", "-O2", "-fprofile-instr-use=/x.profdata"]
        build.run(use + ["-c", "a.cpp", "-o", "a.o"])
        build.run(use + [build.ALIGN, "-c", "a.cpp", "-o", "a.o"])
        build.run(["clang++-18", "-O2", "-c", "b.cpp", "-o", "b.o"])
        build.run(use + ["-o", "bin", "driver.cpp", "lib.a"])  # link: no -c
        cap.restore()
        self.assertEqual(fake.cmds[0][-2:], build.REMARKS)
        self.assertNotIn("-Rpass=loop-vectorize", fake.cmds[1])
        self.assertNotIn("-Rpass=loop-vectorize", fake.cmds[2])
        self.assertNotIn("-Rpass=loop-vectorize", fake.cmds[3])
        self.assertEqual([a for a, _ in cap.stderr], [False, True])  # plain and aligned PGO compiles are kept
        self.assertIs(build.run, fake)

    def test_warning_counts_ignore_aligned_compiles(self):
        cap = [(False, "x.cpp:1:1: warning: profile data may be out of date: of 3 functions, 1 has mismatched data "
                       "that will be ignored [-Wprofile-instr-out-of-date]\n"
                       "y.cpp:2:2: warning: no profile data available for function 'f' [-Wprofile-instr-missing]\n"),
               (True, "z.cpp:1:1: warning: [-Wprofile-instr-out-of-date]\n")]
        self.assertEqual(build_pgo.count_warnings(cap), {"out_of_date": 1, "missing": 1})

    def test_lost_vectorized(self):
        loops = [{"file": "src/a.cpp", "line": 10, "column": 3, "loop_lines": [10, 12], "function": "f"},
                 {"file": "src/b.cpp", "line": 20, "column": 5, "loop_lines": [20, 21], "function": "g"}]
        err = "/w/src/a.cpp:10:3: remark: vectorized loop (vectorization width: 4) [-Rpass=loop-vectorize]\n"
        got = build_pgo.lost_vectorized([(False, err)], loops)
        self.assertEqual({x["location"]: x["vectorized"] for x in got}, {"src/a.cpp:10:3": 1, "src/b.cpp:20:5": 0})


@unittest.skipUnless(os.name == "posix", "needs a shell script as the fake binary")
class TestTraining(unittest.TestCase):
    def test_train_collects_one_profraw_per_row(self):
        with tempfile.TemporaryDirectory() as d:
            fake = os.path.join(d, "prog.none_gen")
            with open(fake, "w") as f:
                f.write('#!/bin/sh\necho "[log]"\n: > "$(echo "$LLVM_PROFILE_FILE" | sed "s/%p/$$/")"\n'
                        'echo "RESULT ns=5 iters=1 checksum=ab checksum_r=cd"\n')
            os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
            rows = [{"row": "r1", "args": ["x"]}, {"row": "r2", "args": ["y", "z"]}]
            recs, raws = build_pgo.train(fake, rows, os.path.join(d, "raw"), "none", "prog")
            self.assertEqual(len(raws), 2)
            self.assertEqual([r["checksum"] for r in recs], ["ab", "ab"])
            self.assertEqual(recs[1]["args"], ["y", "z", "1"])


class TestTagAndPool(unittest.TestCase):
    def test_tag_records_binary_hashes(self):
        doc = tagged_jobs({"a": (1.0, 1.0, 1.0)}, "r1", n=1)[0]
        self.assertEqual(doc["pgo"]["column"], "pgo-v1")
        self.assertEqual(sorted(doc["pgo"]["binary_sha256"]), ["a.fast", "a.fast_a64", "a.none", "a.none_a64"])

    def test_untagged_job_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            docs = [job("r1", j, CPU, ROWS_PGO, j) for j in range(3)]
            write_jobs(d, docs)
            with self.assertRaises(SystemExit):
                pool_pgo.load([d], d)

    def test_pool_and_recheck(self):
        with tempfile.TemporaryDirectory() as d:
            write_jobs(d, tagged_jobs(ROWS_PGO, "r1", n=3))
            entries, builds = pool_pgo.load([d], d)
            self.assertEqual(builds, [])
            doc = pool_pgo.pool_doc(entries, d, builds)
            self.assertEqual(doc["kind"], "pgo-pooled")
            self.assertNotIn("context", doc)
            out = os.path.join(d, "pgo.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=1)
            errors = []
            pgo_check.check_pooled(out, errors)
            self.assertEqual(errors, [])
            blk = doc["cpus"][0]
            self.assertEqual(blk["jobs"], 3)
            self.assertEqual(blk["rows"][0]["reading"]["reading"], "detectably slower")
            # tampering with a job file is caught
            with open(os.path.join(d, entries[0][0]), "a") as f:
                f.write(" ")
            errors = []
            pgo_check.check_pooled(out, errors)
            self.assertTrue(errors)

    def test_two_different_builds_of_one_mode_are_an_error(self):
        def bj(sha):
            b = {"sha256": sha, "text_sha256": sha, "traps": 3}
            return {"kind": "pgo-build", "mode": "fast", "programs": {"p": {
                "builds": {"pgo": b, "pgo_a64": b}, "instrumented": {"sha256": "g"},
                "profile": {"functions": 1, "bytes": 2, "sha256": "h"}, "profile_warnings": {"out_of_date": 0, "missing": 0},
                "census_lost_locations": [], "training": {"rows": [{"row": "r", "checksum": "c"}]}}}}
        with tempfile.TemporaryDirectory() as d:
            for name, sha in (("pgo-build-fast-1.json", "a"), ("pgo-build-fast-2.json", "b")):
                with open(os.path.join(d, name), "w") as f:
                    json.dump(bj(sha), f)
            with self.assertRaises(SystemExit):
                pool_pgo.build_context(["pgo-build-fast-1.json", "pgo-build-fast-2.json"], d)


def pooled(rows, run_id, n=3, cpu=CPU, tagged=True):
    with tempfile.TemporaryDirectory() as d:
        docs = tagged_jobs(rows, run_id, n, cpu) if tagged else [job(run_id, j, cpu, rows, j + 1) for j in range(n)]
        write_jobs(d, docs)
        import pool_rw
        entries, _, _ = pool_rw.load_entries([d], d)
        if tagged:
            return pool_pgo.pool_doc(entries, d, [])
        return json.loads(json.dumps(pool_rw.pool_all(entries, d, (), ())))


class TestAnalyze(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = pooled(ROWS_NOPGO, "base", n=4, tagged=False)
        cls.pgo = json.loads(json.dumps(pooled(ROWS_PGO, "pgo", n=4)))

    def rows(self, doc):
        return {r["row"]: r for r in doc["cpus"][0]["rows"]}

    def test_lower_same_higher(self):
        b, p = self.rows(self.base), self.rows(self.pgo)
        self.assertEqual(analyze.compare(b["a"], p["a"]), "PGO lower")
        self.assertEqual(analyze.compare(b["b"], p["b"]), "no difference detected")
        self.assertEqual(analyze.compare(b["c"], p["c"]), "PGO higher")

    def test_not_compared(self):
        b, p = self.rows(self.base), self.rows(self.pgo)
        self.assertTrue(analyze.compare(None, p["a"]).startswith("not compared"))
        few = pooled(ROWS_PGO, "few", n=2)
        self.assertTrue(analyze.compare(b["a"], self.rows(few)["a"]).startswith("not compared (PGO"))
        self.assertTrue(analyze.compare(self.rows(few)["a"], p["a"]).startswith("not compared (non-PGO"))

    def test_the_widening_is_by_the_own_floor(self):
        b = json.loads(json.dumps(self.rows(self.base)["a"]))
        p = json.loads(json.dumps(self.rows(self.pgo)["a"]))
        for row, lo, hi in ((b, 1.040, 1.060), (p, 1.030, 1.0399)):
            for pair in ("fast", "aligned"):
                row["pairs"][pair]["time"]["ci95"] = [lo, hi]
            row["pairs"]["aa"]["time"]["half_width_pct"] = 0.5
        # PGO upper 1.0399 + 0.005 = 1.0449 is not below non-PGO lower 1.040 - 0.005 = 1.035
        self.assertEqual(analyze.compare(b, p), "no difference detected")
        p["pairs"]["fast"]["time"]["ci95"] = p["pairs"]["aligned"]["time"]["ci95"] = [1.0, 1.02]
        self.assertEqual(analyze.compare(b, p), "PGO lower")

    def test_no_result_text(self):
        self.assertEqual(analyze.render(None, self.base), analyze.NO_RESULT)

    def test_render_has_tables_and_summary(self):
        text = analyze.render(self.pgo, self.base)
        self.assertIn("### AMD EPYC 7763", text)
        self.assertIn("PGO lower", text)
        self.assertIn("## Summary of the comparison", text)
        self.assertIn("PGO higher: 1 (c)", text)
        self.assertEqual(text, analyze.render(self.pgo, self.base))  # deterministic

    def test_render_without_baseline(self):
        text = analyze.render(self.pgo, None)
        self.assertIn("this CPU model is not in the non-PGO pool", text)
        self.assertIn("not compared", text)

    def test_other_cpu_model_is_not_compared(self):
        other = json.loads(json.dumps(self.pgo))
        other["cpus"][0]["cpu_model"] = "Some Other CPU"
        text = analyze.render(other, self.base)
        self.assertIn("not compared", text)
        self.assertNotIn("PGO lower", text)


class TestBuildTable(unittest.TestCase):
    def test_lost_locations_table(self):
        def e(vec, traps):
            return {"traps": {"pgo": traps}, "profile": {"functions": 10}, "profile_warnings": {"out_of_date": 1, "missing": 2},
                    "census_lost_locations": [{"location": f"f.cpp:{i}:1", "vectorized": v} for i, v in enumerate(vec)]}
        ctx = {"p": {"none": e([1, 1, 0], 3), "fast": e([0, 1, 0], 40)}, "q": {"none": e([1], 0)}}
        text = chr(10).join(analyze.render_builds(ctx))
        self.assertIn("| p | 3 / 40 | 1 / 2, 1 / 2 | 2 / 1 of 3 (1 lost here too) | 10 / 10 |", text)
        self.assertIn("| q | - | - | only one mode built | - |", text)


class TestOfflineCheck(unittest.TestCase):
    def test_files_and_build_script(self):
        errors = []
        pgo_check.check_files(errors)
        pgo_check.check_build_script(errors)
        self.assertEqual(errors, [])

    def test_report_matches_when_nothing_is_timed(self):
        errors = []
        pooled = pgo_check.DEFAULT
        base = os.path.join(pgo_check.REPO, "results", "realworld-pooled", "realworld.json")
        if not (os.path.exists(pooled) and os.path.exists(base)):  # nothing timed yet: the report says so
            pooled = os.path.join(tempfile.gettempdir(), "no-such-pgo.json")
            base = os.path.join(tempfile.gettempdir(), "no-such-base.json")
        pgo_check.check_report(pooled, base, errors)
        if not os.path.exists(os.path.join(PGO, "report.md")):
            self.skipTest("report.md not written yet")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
