"""Tests of the real-program study's pure code (realworld/common.py, pool_rw.py, report.py, check.py) on
made-up inputs; no compiler, no runner."""
import json
import os
import random
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RW = os.path.dirname(HERE)
sys.path.insert(0, RW)

import common  # noqa: E402

CPU = "AMD EPYC 7763 64-Core Processor"


def samples(rng, level, n=40, noise=0.004):
    return [level * 1e8 * (1 + rng.gauss(0, noise)) for _ in range(n)]


def job(run_id, jobno, cpu, ratios, seed, reps=40, checksum="ab"):
    """A made-up realworld-job document: ratios = {row: (fast, aligned, layout)}."""
    rng = random.Random(seed)
    order = "".join("AB" if k % 2 == 0 else "BA" for k in range(reps))
    rows = []
    for name, (rf, ra, rl) in ratios.items():
        pairs = {}
        for p, r in (("fast", rf), ("aa", 1.0), ("aligned", ra), ("layout", rl)):
            a, b = samples(rng, 1.0, reps), samples(rng, r, reps)
            pairs[p] = {"a_ns": a, "b_ns": b, "a_wall_ns": [x * 1.1 for x in a], "b_wall_ns": [x * 1.1 for x in b],
                        "a_checksums": [checksum], "b_checksums": [checksum], "checksum_exact_match": True,
                        "checksum_rounded_match": True, "order": order}
        rows.append({"row": name, "program": name, "args": [], "iters": 1, "calibration_ns_one_iter": 1e8,
                     "sha256": {"none": "a" * 64, "none_copy": "a" * 64, "fast": "b" * 64, "none_a64": "c" * 64,
                                "fast_a64": "d" * 64}, "pairs": pairs})
    return {"kind": "realworld-job", "schema": 1, "sample": True,
            "run": {"id": run_id, "job": str(jobno), "runner": {"cpu_model": cpu, "cores": 4}, "reps_per_side": reps},
            "rows": rows}


class TestParse(unittest.TestCase):
    def test_result_line(self):
        out = "[LightGBM] noise\nRESULT ns=123.5 iters=3 checksum=00ff checksum_r=0abc\n"
        r = common.parse_result(out)
        self.assertEqual((r["ns"], r["iters"], r["checksum"], r["checksum_r"]), (123.5, 3, "00ff", "0abc"))

    def test_result_missing(self):
        with self.assertRaises(ValueError):
            common.parse_result("ns=1 checksum=2\n")

    def test_result_without_rounded(self):
        self.assertEqual(common.parse_result("RESULT ns=1 iters=1 checksum=ab")["checksum_r"], "ab")


class TestCachegrind(unittest.TestCase):
    TEXT = ("desc: x\ncmd: ./a\nevents: Ir\n"
            "fl=/w/src/a.cpp\nfn=_Z1fv\n10 100\n11 50\n"
            "fl=/w/include/v.h\nfn=_Z1fv\n5 7\n"
            "fl=/w/src/a.cpp\nfn=_Z1gv\n20 1000\n"
            "summary: 1157\n")

    def test_lines_and_summary(self):
        c, total = common.cachegrind_lines(self.TEXT)
        self.assertEqual(total, 1157)
        self.assertEqual(c[("/w/src/a.cpp", "_Z1fv", 10)], 100)
        self.assertEqual(c[("/w/include/v.h", "_Z1fv", 5)], 7)
        self.assertEqual(sum(c.values()), 1157)

    def test_compressed_names(self):
        c, _ = common.cachegrind_lines("events: Ir\nfl=(1) /a.cpp\nfn=(2) _Z1hv\n3 4\nfn=(3) _Z1kv\n3 1\nfn=(2)\n3 6\n")
        self.assertEqual(c[("/a.cpp", "_Z1hv", 3)], 10)
        self.assertEqual(c[("/a.cpp", "_Z1kv", 3)], 1)

    def test_iteration_difference(self):
        one = {("a", "f", 1): 100, ("a", "f", 2): 10}
        two = {("a", "f", 1): 150, ("a", "f", 2): 10, ("a", "g", 3): 5}
        self.assertEqual(common.iteration_counts(one, two), {("a", "f", 1): 50, ("a", "g", 3): 5})


class TestShares(unittest.TestCase):
    LOOPS = [{"file": "src/a.cpp", "line": 10, "column": 3, "loop_lines": [10, 11], "function": "_Z1fv",
              "function_name": "f()", "class": "other", "count": 1}]

    def test_bounds(self):
        it = {("/w/src/a.cpp", "_Z1fv", 10): 100, ("/w/src/a.cpp", "_Z1fv", 11): 50,
              ("/w/include/v.h", "_Z1fv", 5): 7, ("/w/src/a.cpp", "_Z1gv", 20): 1000,
              ("/w/other/src/a.cpp.bak", "_Z1gv", 10): 9}
        s = common.shares(it, self.LOOPS)
        self.assertEqual(s["iteration_ir"], 1166)
        self.assertEqual(s["loop_lines_ir"], 150)          # the loop's own lines only
        self.assertEqual(s["functions_ir"], 157)           # all of f, inlined header code included
        self.assertLessEqual(s["loop_lines_share"], s["functions_share"])
        self.assertEqual(s["functions_matched"], 1)

    def test_no_loops(self):
        s = common.shares({("a", "f", 1): 10}, [])
        self.assertEqual((s["loop_lines_share"], s["functions_share"]), (0.0, 0.0))

    def test_suffix_match_is_on_path_components(self):
        self.assertTrue(common._file_matches("/x/src/a.cpp", "src/a.cpp"))
        self.assertFalse(common._file_matches("/x/xsrc/a.cpp", "src/a.cpp"))


class TestRemarks(unittest.TestCase):
    def test_locations_and_lost(self):
        none = ("/w/src/a.cpp:10:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) "
                "[-Rpass=loop-vectorize]\n/w/src/a.cpp:20:3: remark: loop not vectorized [-Rpass-missed=loop-vectorize]\n")
        fast = "/w/src/a.cpp:10:3: remark: loop not vectorized [-Rpass-missed=loop-vectorize]\n"
        n, f = common.remark_locations(none), common.remark_locations(fast)
        self.assertEqual(n[("/w/src/a.cpp", 10, 3)], {"vectorized": 1, "missed": 0})
        rows = common.lost_in_build(n, f, TestShares.LOOPS)
        self.assertEqual(rows, [{"location": "src/a.cpp:10:3", "vectorized_none": 1, "vectorized_fast": 0,
                                 "lost_here_too": True}])

    def test_census_file_has_the_projects(self):
        lost = common.load_lost()
        for p in ("lightgbm", "draco", "tiny-dnn", "spectra"):
            self.assertTrue(common.lost_loops_for(p, lost), p)
        self.assertEqual(common.lost_loops_for("meshoptimizer", lost), [])
        self.assertEqual(common.lost_loops_for(None, lost), [])
        for lp in common.lost_loops_for("lightgbm", lost):
            self.assertLessEqual(lp["loop_lines"][0], lp["loop_lines"][1])


class TestReading(unittest.TestCase):
    def c(self, r, lo, hi):
        return {"ratio": r, "ci95": [lo, hi]}

    def test_slower_both_columns(self):
        v = common.verdict_row(self.c(1.1, 1.08, 1.12), self.c(1.09, 1.07, 1.11), 0.5, 6)
        self.assertEqual(v["reading"], "detectably slower")

    def test_faster(self):
        v = common.verdict_row(self.c(0.97, 0.96, 0.98), self.c(0.98, 0.97, 0.985), 0.5, 6)
        self.assertEqual(v["reading"], "detectably faster")

    def test_not_detectable_never_below_floor(self):
        v = common.verdict_row(self.c(1.001, 0.998, 1.003), self.c(1.0, 0.997, 1.002), 0.8, 6)
        self.assertEqual(v["reading"], "not detectable")
        self.assertAlmostEqual(v["at_most_pct"], 0.8)

    def test_not_detectable_top_of_interval(self):
        v = common.verdict_row(self.c(1.01, 0.999, 1.03), self.c(1.0, 0.99, 1.01), 0.5, 6)
        self.assertAlmostEqual(v["at_most_pct"], 3.0)

    def test_one_column_only(self):
        v = common.verdict_row(self.c(1.05, 1.04, 1.06), self.c(1.0, 0.99, 1.01), 0.5, 6)
        self.assertEqual(v["reading"], "not detectable")
        self.assertIn("only the as compiled column", v["text"])

    def test_too_few_jobs(self):
        v = common.verdict_row(self.c(2, 1.9, 2.1), self.c(2, 1.9, 2.1), 0.5, 2)
        self.assertEqual(v["reading"], "too few jobs")


class TestPool(unittest.TestCase):
    def setUp(self):
        try:
            import numpy  # noqa: F401
        except ImportError:
            self.skipTest("numpy not installed")
        import pool_rw
        self.pool_rw = pool_rw
        self.tmp = tempfile.mkdtemp()
        ratios = {"big": (1.20, 1.21, 1.00), "flat": (1.00, 1.00, 1.01)}
        self.paths = []
        for k in range(4):
            cpu = CPU if k < 3 else "Intel Xeon"
            d = job("r1", k + 1, cpu, ratios, seed=k)
            p = os.path.join(self.tmp, "r1", f"results-x-j{k + 1}.json")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(d, f)
            self.paths.append(p)

    def pooled(self):
        entries, b, p = self.pool_rw.load_entries([self.tmp], self.tmp)
        return self.pool_rw.pool_all(entries, self.tmp, b, p)

    def test_per_cpu_and_readings(self):
        d = self.pooled()
        blocks = {b["cpu_model"]: b for b in d["cpus"]}
        self.assertEqual(blocks[CPU]["jobs"], 3)
        rows = {r["row"]: r for r in blocks[CPU]["rows"]}
        self.assertAlmostEqual(rows["big"]["pairs"]["fast"]["time"]["ratio"], 1.20, delta=0.01)
        self.assertEqual(rows["big"]["reading"]["reading"], "detectably slower")
        self.assertEqual(rows["flat"]["reading"]["reading"], "not detectable")
        xeon = {r["row"]: r for r in blocks["Intel Xeon"]["rows"]}
        self.assertEqual(xeon["big"]["reading"]["reading"], "too few jobs")
        self.assertEqual(d["all_runners"]["jobs"], 4)

    def test_deterministic_and_wall_metric(self):
        a, b = self.pooled(), self.pooled()
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        r = a["cpus"][0]["rows"][0]
        self.assertIn("wall", r["pairs"]["fast"])

    def test_checksum_mismatch_fails_the_row(self):
        with open(self.paths[0], encoding="utf-8") as f:
            d = json.load(f)
        x = d["rows"][0]["pairs"]["fast"]
        x["b_checksums"] = ["cd"]
        x["checksum_exact_match"] = False
        x["checksum_rounded_match"] = False
        with open(self.paths[0], "w", encoding="utf-8") as f:
            json.dump(d, f)
        blk = [b for b in self.pooled()["cpus"] if b["cpu_model"] == CPU][0]
        self.assertEqual(blk["rows"][0]["reading"]["reading"], "failed")

    def test_check_recomputes_and_detects_tampering(self):
        import check
        out = os.path.join(self.tmp, "realworld.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(self.pooled(), f)
        errors = []
        check.check_pooled(out, errors)
        self.assertEqual(errors, [])
        with open(out, encoding="utf-8") as f:
            d = json.load(f)
        d["cpus"][0]["rows"][0]["pairs"]["fast"]["time"]["ratio"] += 0.001
        with open(out, "w", encoding="utf-8") as f:
            json.dump(d, f)
        errors = []
        check.check_pooled(out, errors)
        self.assertTrue(any("cpus" in e for e in errors))

    def test_report_renders(self):
        import report
        out = os.path.join(self.tmp, "realworld.json")
        d = self.pooled()
        d["context"] = {"builds": {}, "profiles": {}}
        with open(out, "w", encoding="utf-8") as f:
            json.dump(d, f)
        text = report.render(out)
        self.assertIn("detectably slower", text)
        self.assertIn("fewer than 3 jobs", text)


class TestPins(unittest.TestCase):
    def test_pins_match_the_census(self):
        import check
        errors = []
        check.check_pins(errors)
        self.assertEqual(errors, [])

    def test_job_checker(self):
        import check
        d = job("r", 1, CPU, {"x": (1.0, 1.0, 1.0)}, seed=1)
        errors = []
        check.check_job("j", d, errors)
        self.assertEqual(errors, [])
        d["rows"][0]["pairs"]["fast"]["order"] = "AB" * 40
        check.check_job("j", d, errors)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
