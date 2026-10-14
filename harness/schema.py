"""Checks a results.json against schema version 1 (docs/SPEC.md section 4), with no third-party library.

The check is strict on purpose: every key the SPEC names must be there with the right type, and
no key the SPEC does not name may appear, so the seam between the harness, the Actions run and the
page cannot drift silently. Extra details a run collects go to results/details.json, not here.

Stage S3 adds OPTIONAL keys (the version stays 1; every existing key keeps its meaning and type):
run.criteria_file, run.flags.align, controls.layout_aa, cells[].aligned, cells[].loops,
programs[].aligned, verdict_v1, and the criteria-v2 extras of verdict (criteria_version, cpu_model,
x_pct, n_as_compiled, layout_aa_half_width_pct, placement_sensitive, off_axis). When present they
are checked as strictly as the rest. validate_combined() checks harness/combine.py's combined.json.
Stage S4-measurement (criteria-v3) adds optional raw samples in controls.aa (a_ns, b_ns) and
controls.positive (none_ns, novec_ns), cells[].aligned.instr, criteria_version 3, and
validate_pooled() for harness/pool.py's pooled.json.

Usage: python harness/schema.py results/fixture.json [more.json ...]   (a combined.json is recognised by its "kind")
"""
import json
import re
import sys

NUM = (int, float)
SIZE_CLASSES = ("L1", "L2", "RAM")
FORMS = ("map", "holds_everywhere", "inconclusive")
CELL_ID = re.compile(r"^k\d\d_[a-z0-9_]+\.(L1|L2|RAM)$")


class SchemaError(Exception):
    pass


def _is_num(x):
    return isinstance(x, NUM) and not isinstance(x, bool)


def _keys(obj, where, required, optional=()):
    if not isinstance(obj, dict):
        raise SchemaError(f"{where}: expected an object")
    missing = [k for k in required if k not in obj]
    extra = [k for k in obj if k not in required and k not in optional]
    if missing:
        raise SchemaError(f"{where}: missing keys {missing}")
    if extra:
        raise SchemaError(f"{where}: keys not in schema 1: {extra}")


def _num(x, where, nullable=False):
    if x is None and nullable:
        return
    if not _is_num(x):
        raise SchemaError(f"{where}: expected a number, got {x!r}")


def _str(x, where, nullable=False):
    if x is None and nullable:
        return
    if not isinstance(x, str):
        raise SchemaError(f"{where}: expected a string, got {x!r}")


def _ci(x, where):
    if not (isinstance(x, list) and len(x) == 2 and all(_is_num(v) for v in x) and x[0] <= x[1]):
        raise SchemaError(f"{where}: expected [lo, hi] with lo <= hi, got {x!r}")


def _samples(x, where):
    if not (isinstance(x, list) and x and all(_is_num(v) and v > 0 for v in x)):
        raise SchemaError(f"{where}: expected a non-empty list of positive numbers")


def _sha(x, where):
    if not (isinstance(x, str) and re.fullmatch(r"[0-9a-f]{64}", x)):
        raise SchemaError(f"{where}: expected a sha256 hex string, got {x!r}")


def _instr(x, where):
    if x is None:
        return
    _keys(x, where, ("none", "fast", "ratio"))
    for k in ("none", "fast", "ratio"):
        _num(x[k], f"{where}.{k}")


def _vec(x, where):
    _keys(x, where, ("vectorized", "width"))
    if x["vectorized"] not in (True, False, None):
        raise SchemaError(f"{where}.vectorized: expected true, false or null")
    if x["width"] is not None and not (isinstance(x["width"], int) and x["width"] > 0):
        raise SchemaError(f"{where}.width: expected a positive integer or null")


LOOP_KEYS = ("start", "end", "bytes", "start_mod64", "crosses64", "windows64", "min_windows64", "extra_window",
             "insns", "simd", "innermost")
LOOP_BUILDS = ("none", "fast", "novec", "none_a64", "fast_a64")
V2_VERDICT_KEYS = ("criteria_version", "cpu_model", "x_pct", "n_as_compiled", "layout_aa_half_width_pct",
                   "placement_sensitive", "off_axis")
CRITERIA_FILES = ("harness/criteria.json", "harness/criteria-v2.json", "harness/criteria-v3.json")


def _bool(x, where):
    if not isinstance(x, bool):
        raise SchemaError(f"{where}: expected true or false")


def _nonneg_int(x, where):
    if not (isinstance(x, int) and not isinstance(x, bool) and x >= 0):
        raise SchemaError(f"{where}: expected a non-negative integer")


def _n(x, where):
    if x is None:
        return
    _keys(x, where, ("median", "min", "max"))
    for k in ("median", "min", "max"):
        _num(x[k], f"{where}.{k}")


def _verdict(v, where):
    _keys(v, where, ("form", "line", "n", "forward_limit_pct", "why"), V2_VERDICT_KEYS)
    if v["form"] not in FORMS:
        raise SchemaError(f"{where}.form: expected one of {FORMS}")
    _str(v["line"], f"{where}.line")
    _str(v["why"], f"{where}.why")
    _num(v["forward_limit_pct"], f"{where}.forward_limit_pct")
    _n(v["n"], f"{where}.n")
    if (v["form"] == "map") != (v["n"] is not None):
        raise SchemaError(f"{where}.n: must be set for map and null otherwise")
    present = [k for k in V2_VERDICT_KEYS if k in v]
    if present and len(present) != len(V2_VERDICT_KEYS):
        raise SchemaError(f"{where}: the criteria-v2 keys come all together, missing "
                          f"{[k for k in V2_VERDICT_KEYS if k not in v]}")
    if present:
        if v["criteria_version"] not in (2, 3):
            raise SchemaError(f"{where}.criteria_version: expected 2 or 3")
        _str(v["cpu_model"], f"{where}.cpu_model", nullable=True)
        _num(v["x_pct"], f"{where}.x_pct", nullable=True)
        _num(v["layout_aa_half_width_pct"], f"{where}.layout_aa_half_width_pct", nullable=True)
        _n(v["n_as_compiled"], f"{where}.n_as_compiled")
        if (v["form"] == "map") != (v["n_as_compiled"] is not None):
            raise SchemaError(f"{where}.n_as_compiled: must be set for map and null otherwise")
        if not isinstance(v["placement_sensitive"], list):
            raise SchemaError(f"{where}.placement_sensitive: expected a list")
        for i, p in enumerate(v["placement_sensitive"]):
            _keys(p, f"{where}.placement_sensitive[{i}]", ("cell_id", "ratio", "aligned_ratio", "gap_pct"))
            for k in ("ratio", "aligned_ratio", "gap_pct"):
                _num(p[k], f"{where}.placement_sensitive[{i}].{k}")
        if not isinstance(v["off_axis"], list):
            raise SchemaError(f"{where}.off_axis: expected a list")
        for i, p in enumerate(v["off_axis"]):
            _keys(p, f"{where}.off_axis[{i}]", ("cell_id", "ratio", "aligned_ratio", "pays_in_both_columns"))
            _num(p["ratio"], f"{where}.off_axis[{i}].ratio")
            _num(p["aligned_ratio"], f"{where}.off_axis[{i}].aligned_ratio")
            _bool(p["pays_in_both_columns"], f"{where}.off_axis[{i}].pays_in_both_columns")


def _loops(x, where):
    _keys(x, where, (), LOOP_BUILDS)
    for b, lst in x.items():
        if not isinstance(lst, list):
            raise SchemaError(f"{where}.{b}: expected a list")
        for i, lp in enumerate(lst):
            w = f"{where}.{b}[{i}]"
            _keys(lp, w, LOOP_KEYS)
            for k in ("start", "end"):
                if not (isinstance(lp[k], str) and re.fullmatch(r"0x[0-9a-f]+", lp[k])):
                    raise SchemaError(f"{w}.{k}: expected a hex address")
            for k in ("bytes", "start_mod64", "windows64", "min_windows64", "insns"):
                _nonneg_int(lp[k], f"{w}.{k}")
            for k in ("crosses64", "extra_window", "simd", "innermost"):
                _bool(lp[k], f"{w}.{k}")


def _aligned_cell(x, where):
    _keys(x, where, ("none_sha256", "fast_sha256", "checksum_match", "vectorized_none", "vectorized_fast",
                     "traps_none", "traps_fast", "none_ns", "fast_ns", "ratio", "ci95", "asm_diff_path"), ("instr",))
    if "instr" in x:
        _instr(x["instr"], f"{where}.instr")
    _sha(x["none_sha256"], f"{where}.none_sha256")
    _sha(x["fast_sha256"], f"{where}.fast_sha256")
    _bool(x["checksum_match"], f"{where}.checksum_match")
    _vec(x["vectorized_none"], f"{where}.vectorized_none")
    _vec(x["vectorized_fast"], f"{where}.vectorized_fast")
    _nonneg_int(x["traps_none"], f"{where}.traps_none")
    _nonneg_int(x["traps_fast"], f"{where}.traps_fast")
    _samples(x["none_ns"], f"{where}.none_ns")
    _samples(x["fast_ns"], f"{where}.fast_ns")
    _num(x["ratio"], f"{where}.ratio")
    _ci(x["ci95"], f"{where}.ci95")
    if not (isinstance(x["asm_diff_path"], str) and x["asm_diff_path"].startswith("results/asm/")):
        raise SchemaError(f"{where}.asm_diff_path: expected a path under results/asm/")


def _aligned_program(x, where):
    _keys(x, where, ("none_sha256", "fast_sha256", "traps_none", "traps_fast", "none_ns", "fast_ns", "ratio", "ci95",
                     "consistent_with_at_most_pct"))
    _sha(x["none_sha256"], f"{where}.none_sha256")
    _sha(x["fast_sha256"], f"{where}.fast_sha256")
    _nonneg_int(x["traps_none"], f"{where}.traps_none")
    _nonneg_int(x["traps_fast"], f"{where}.traps_fast")
    _samples(x["none_ns"], f"{where}.none_ns")
    _samples(x["fast_ns"], f"{where}.fast_ns")
    _num(x["ratio"], f"{where}.ratio")
    _ci(x["ci95"], f"{where}.ci95")
    _num(x["consistent_with_at_most_pct"], f"{where}.consistent_with_at_most_pct", nullable=True)


def _layout_aa(lst, where):
    if not isinstance(lst, list):
        raise SchemaError(f"{where}: expected a list")
    ids = set()
    for i, p in enumerate(lst):
        w = f"{where}[{i}]"
        _keys(p, w, ("id", "a_build", "b_build", "a_sha256", "b_sha256", "n_per_side", "ratio", "ci95",
                     "half_width_pct", "a_ns", "b_ns"))
        _str(p["id"], f"{w}.id")
        if p["id"] in ids:
            raise SchemaError(f"{w}.id: duplicate {p['id']}")
        ids.add(p["id"])
        _str(p["a_build"], f"{w}.a_build")
        _str(p["b_build"], f"{w}.b_build")
        _sha(p["a_sha256"], f"{w}.a_sha256")
        _sha(p["b_sha256"], f"{w}.b_sha256")
        if not (isinstance(p["n_per_side"], int) and p["n_per_side"] > 0):
            raise SchemaError(f"{w}.n_per_side: expected a positive integer")
        _num(p["ratio"], f"{w}.ratio")
        _ci(p["ci95"], f"{w}.ci95")
        _num(p["half_width_pct"], f"{w}.half_width_pct")
        _samples(p["a_ns"], f"{w}.a_ns")
        _samples(p["b_ns"], f"{w}.b_ns")


def validate(doc):
    """Raises SchemaError with the first problem found; returns None when the document is valid."""
    _keys(doc, "top", ("schema", "sample", "run", "controls", "cells", "programs", "verdict", "prior_numbers"),
          ("verdict_v1",))
    if doc["schema"] != 1:
        raise SchemaError("top.schema: expected 1")
    if not isinstance(doc["sample"], bool):
        raise SchemaError("top.sample: expected true or false")

    run = doc["run"]
    _keys(run, "run", ("id", "commit", "workflow_run_url", "started_at", "runner", "toolchain", "flags",
                       "criteria_sha256"), ("criteria_file",))
    if "criteria_file" in run and run["criteria_file"] not in CRITERIA_FILES:
        raise SchemaError(f"run.criteria_file: expected one of {CRITERIA_FILES}")
    _str(run["id"], "run.id")
    _str(run["commit"], "run.commit", nullable=True)
    _str(run["workflow_run_url"], "run.workflow_run_url", nullable=True)
    _str(run["started_at"], "run.started_at")
    _keys(run["runner"], "run.runner", ("os", "kernel", "arch", "cpu_model", "cores", "l1d_kib", "l2_kib", "l3_kib"))
    for k in ("os", "kernel", "arch", "cpu_model"):
        _str(run["runner"][k], f"run.runner.{k}", nullable=True)
    for k in ("cores", "l1d_kib", "l2_kib", "l3_kib"):
        _num(run["runner"][k], f"run.runner.{k}", nullable=True)
    _keys(run["toolchain"], "run.toolchain", ("clang", "libcxx_package"))
    _keys(run["flags"], "run.flags", ("common", "none", "fast", "novec"), ("align",))
    for k, v in list(run["toolchain"].items()) + list(run["flags"].items()):
        _str(v, f"run.* {k}", nullable=True)
    _sha(run["criteria_sha256"], "run.criteria_sha256")

    ctl = doc["controls"]
    _keys(ctl, "controls", ("aa", "negative", "positive"), ("layout_aa",))
    if "layout_aa" in ctl:
        _layout_aa(ctl["layout_aa"], "controls.layout_aa")
    aa = ctl["aa"]
    _keys(aa, "controls.aa", ("ratio", "ci95", "half_width_pct", "n_per_side", "binary_sha256"), ("a_ns", "b_ns"))
    if ("a_ns" in aa) != ("b_ns" in aa):
        raise SchemaError("controls.aa: a_ns and b_ns come together")
    if "a_ns" in aa:
        _samples(aa["a_ns"], "controls.aa.a_ns")
        _samples(aa["b_ns"], "controls.aa.b_ns")
    _num(aa["ratio"], "controls.aa.ratio")
    _ci(aa["ci95"], "controls.aa.ci95")
    _num(aa["half_width_pct"], "controls.aa.half_width_pct")
    if not (isinstance(aa["n_per_side"], int) and aa["n_per_side"] > 0):
        raise SchemaError("controls.aa.n_per_side: expected a positive integer")
    _sha(aa["binary_sha256"], "controls.aa.binary_sha256")

    cell_ids = []
    if not isinstance(doc["cells"], list) or not doc["cells"]:
        raise SchemaError("cells: expected a non-empty list")
    for i, c in enumerate(doc["cells"]):
        w = f"cells[{i}]"
        _keys(c, w, ("cell_id", "kernel", "size_class", "working_set_bytes", "none_sha256", "fast_sha256",
                     "checksum_match", "vectorized_none", "vectorized_fast", "traps_none", "traps_fast",
                     "none_ns", "fast_ns", "ratio", "ci95", "instr", "command", "asm_diff_path"),
              ("aligned", "loops"))
        if "aligned" in c:
            _aligned_cell(c["aligned"], f"{w}.aligned")
        if "loops" in c:
            _loops(c["loops"], f"{w}.loops")
        if not (isinstance(c["cell_id"], str) and CELL_ID.match(c["cell_id"])):
            raise SchemaError(f"{w}.cell_id: expected <kernel>.<L1|L2|RAM>, got {c['cell_id']!r}")
        if c["size_class"] not in SIZE_CLASSES:
            raise SchemaError(f"{w}.size_class: expected one of {SIZE_CLASSES}")
        if c["cell_id"] != f"{c['kernel']}.{c['size_class']}":
            raise SchemaError(f"{w}.cell_id: does not equal kernel.size_class")
        if c["cell_id"] in cell_ids:
            raise SchemaError(f"{w}.cell_id: duplicate {c['cell_id']}")
        cell_ids.append(c["cell_id"])
        if not (isinstance(c["working_set_bytes"], int) and c["working_set_bytes"] > 0):
            raise SchemaError(f"{w}.working_set_bytes: expected a positive integer")
        _sha(c["none_sha256"], f"{w}.none_sha256")
        _sha(c["fast_sha256"], f"{w}.fast_sha256")
        if not isinstance(c["checksum_match"], bool):
            raise SchemaError(f"{w}.checksum_match: expected true or false")
        _vec(c["vectorized_none"], f"{w}.vectorized_none")
        _vec(c["vectorized_fast"], f"{w}.vectorized_fast")
        for k in ("traps_none", "traps_fast"):
            if not (isinstance(c[k], int) and c[k] >= 0):
                raise SchemaError(f"{w}.{k}: expected a non-negative integer")
        _samples(c["none_ns"], f"{w}.none_ns")
        _samples(c["fast_ns"], f"{w}.fast_ns")
        _num(c["ratio"], f"{w}.ratio")
        _ci(c["ci95"], f"{w}.ci95")
        _instr(c["instr"], f"{w}.instr")
        _str(c["command"], f"{w}.command")
        if not (isinstance(c["asm_diff_path"], str) and c["asm_diff_path"].startswith("results/asm/")):
            raise SchemaError(f"{w}.asm_diff_path: expected a path under results/asm/")

    if not isinstance(ctl["negative"], list) or any(x not in cell_ids for x in ctl["negative"]):
        raise SchemaError("controls.negative: expected a list of cell_ids present in cells")
    if not isinstance(ctl["positive"], list):
        raise SchemaError("controls.positive: expected a list")
    for i, p in enumerate(ctl["positive"]):
        _keys(p, f"controls.positive[{i}]", ("cell_id", "novec_ratio", "ci95"), ("none_ns", "novec_ns"))
        if ("none_ns" in p) != ("novec_ns" in p):
            raise SchemaError(f"controls.positive[{i}]: none_ns and novec_ns come together")
        if "none_ns" in p:
            _samples(p["none_ns"], f"controls.positive[{i}].none_ns")
            _samples(p["novec_ns"], f"controls.positive[{i}].novec_ns")
        if p["cell_id"] not in cell_ids:
            raise SchemaError(f"controls.positive[{i}].cell_id: not in cells")
        _num(p["novec_ratio"], f"controls.positive[{i}].novec_ratio")
        _ci(p["ci95"], f"controls.positive[{i}].ci95")

    if not isinstance(doc["programs"], list):
        raise SchemaError("programs: expected a list")
    for i, p in enumerate(doc["programs"]):
        w = f"programs[{i}]"
        _keys(p, w, ("name", "pin", "input_sha256", "none_sha256", "fast_sha256", "traps_none", "traps_fast",
                     "ratio", "ci95", "aa_half_width_pct", "consistent_with_at_most_pct", "none_ns", "fast_ns",
                     "instr"), ("aligned",))
        if "aligned" in p:
            _aligned_program(p["aligned"], f"{w}.aligned")
        _str(p["name"], f"{w}.name")
        _str(p["pin"], f"{w}.pin")
        for k in ("input_sha256", "none_sha256", "fast_sha256"):
            _sha(p[k], f"{w}.{k}")
        for k in ("traps_none", "traps_fast"):
            if not (isinstance(p[k], int) and p[k] >= 0):
                raise SchemaError(f"{w}.{k}: expected a non-negative integer")
        _num(p["ratio"], f"{w}.ratio")
        _ci(p["ci95"], f"{w}.ci95")
        _num(p["aa_half_width_pct"], f"{w}.aa_half_width_pct", nullable=True)
        _num(p["consistent_with_at_most_pct"], f"{w}.consistent_with_at_most_pct", nullable=True)
        _samples(p["none_ns"], f"{w}.none_ns")
        _samples(p["fast_ns"], f"{w}.fast_ns")
        _instr(p["instr"], f"{w}.instr")

    _verdict(doc["verdict"], "verdict")
    if "verdict_v1" in doc:
        _verdict(doc["verdict_v1"], "verdict_v1")
        if "criteria_version" in doc["verdict_v1"]:
            raise SchemaError("verdict_v1: carries criteria-v2 keys")

    if not isinstance(doc["prior_numbers"], list):
        raise SchemaError("prior_numbers: expected a list")
    for i, p in enumerate(doc["prior_numbers"]):
        _keys(p, f"prior_numbers[{i}]", ("source", "figure", "url", "verified"))
        if p["verified"] is not True:
            raise SchemaError(f"prior_numbers[{i}]: an unverified figure is not listed at all")


def validate_combined(doc):
    """Checks a combined.json written by harness/combine.py."""
    _keys(doc, "combined", ("kind", "criteria_file", "criteria_sha256", "files", "cpus", "verdict"))
    if doc["kind"] != "combined":
        raise SchemaError("combined.kind: expected 'combined'")
    if doc["criteria_file"] != "harness/criteria-v2.json":
        raise SchemaError("combined.criteria_file: expected harness/criteria-v2.json")
    _sha(doc["criteria_sha256"], "combined.criteria_sha256")
    if not isinstance(doc["files"], list) or not doc["files"]:
        raise SchemaError("combined.files: expected a non-empty list")
    for i, f in enumerate(doc["files"]):
        w = f"combined.files[{i}]"
        _keys(f, w, ("path", "cpu_model", "run_id", "aa_half_width_pct", "usable", "form", "line", "why", "x_pct",
                     "placement_sensitive"))
        _str(f["path"], f"{w}.path")
        _num(f["aa_half_width_pct"], f"{w}.aa_half_width_pct")
        _bool(f["usable"], f"{w}.usable")
        if f["form"] not in FORMS:
            raise SchemaError(f"{w}.form: expected one of {FORMS}")
    if not isinstance(doc["cpus"], list) or not doc["cpus"]:
        raise SchemaError("combined.cpus: expected a non-empty list")
    for i, c in enumerate(doc["cpus"]):
        w = f"combined.cpus[{i}]"
        _keys(c, w, ("cpu_model", "files", "usable", "form", "why"))
        _bool(c["usable"], f"{w}.usable")
        if c["form"] not in FORMS + (None,):
            raise SchemaError(f"{w}.form: expected one of {FORMS} or null")
    v = doc["verdict"]
    _keys(v, "combined.verdict", ("form", "line", "why", "n", "x_pct"))
    if v["form"] not in FORMS:
        raise SchemaError(f"combined.verdict.form: expected one of {FORMS}")
    _str(v["line"], "combined.verdict.line")
    _str(v["why"], "combined.verdict.why")
    _num(v["x_pct"], "combined.verdict.x_pct", nullable=True)
    _n(v["n"], "combined.verdict.n")
    if (v["form"] == "map") != (v["n"] is not None):
        raise SchemaError("combined.verdict.n: must be set for map and null otherwise")


POOLED_STAT_KEYS = ("ratio", "ci95", "half_width_pct", "jobs", "per_job", "between_job_sd_pct")


def _pstat(x, where):
    _keys(x, where, POOLED_STAT_KEYS)
    _num(x["ratio"], f"{where}.ratio")
    _ci(x["ci95"], f"{where}.ci95")
    _num(x["half_width_pct"], f"{where}.half_width_pct")
    if not (isinstance(x["jobs"], int) and x["jobs"] > 0):
        raise SchemaError(f"{where}.jobs: expected a positive integer")
    _samples(x["per_job"], f"{where}.per_job")
    if len(x["per_job"]) != x["jobs"]:
        raise SchemaError(f"{where}.per_job: expected one ratio per job")
    _num(x["between_job_sd_pct"], f"{where}.between_job_sd_pct", nullable=True)


def _compact3(x, where):
    if not (isinstance(x, list) and len(x) == 3 and all(_is_num(v) for v in x) and x[1] <= x[2]):
        raise SchemaError(f"{where}: expected [ratio, lo, hi]")


def validate_pooled(doc):
    """Checks a pooled.json written by harness/pool.py (criteria-v3)."""
    _keys(doc, "pooled", ("kind", "criteria_file", "criteria_sha256", "resamples", "inputs", "runs", "cpus", "page"))
    if doc["kind"] != "pooled":
        raise SchemaError("pooled.kind: expected 'pooled'")
    if doc["criteria_file"] != "harness/criteria-v3.json":
        raise SchemaError("pooled.criteria_file: expected harness/criteria-v3.json")
    _sha(doc["criteria_sha256"], "pooled.criteria_sha256")
    _nonneg_int(doc["resamples"], "pooled.resamples")
    if not isinstance(doc["inputs"], list) or not doc["inputs"]:
        raise SchemaError("pooled.inputs: expected a non-empty list")
    for i, f in enumerate(doc["inputs"]):
        _keys(f, f"pooled.inputs[{i}]", ("path", "run_id", "cpu_model"))
        for k in ("path", "run_id", "cpu_model"):
            _str(f[k], f"pooled.inputs[{i}].{k}")
    if not (isinstance(doc["runs"], list) and all(isinstance(r, str) for r in doc["runs"])):
        raise SchemaError("pooled.runs: expected a list of run ids")
    if not isinstance(doc["cpus"], list) or not doc["cpus"]:
        raise SchemaError("pooled.cpus: expected a non-empty list")
    for i, b in enumerate(doc["cpus"]):
        w = f"pooled.cpus[{i}]"
        _keys(b, w, ("cpu_model", "jobs", "runs", "aa", "layout_aa", "positive", "cells", "verdict", "per_run",
                     "stability", "reproduction"))
        _str(b["cpu_model"], f"{w}.cpu_model")
        _pstat(b["aa"], f"{w}.aa")
        if b["aa"]["jobs"] != b["jobs"]:
            raise SchemaError(f"{w}.aa.jobs: expected {b['jobs']}")
        for k in ("layout_aa", "positive"):
            if not isinstance(b[k], dict):
                raise SchemaError(f"{w}.{k}: expected an object")
            for name, st in b[k].items():
                _pstat(st, f"{w}.{k}.{name}")
        for j, c in enumerate(b["cells"]):
            cw = f"{w}.cells[{j}]"
            _keys(c, cw, ("cell_id", "kernel", "size_class", "class", "as_compiled", "aligned"),
                  ("instr", "aligned_instr", "instr_agree", "instr_label", "placement"))
            if not CELL_ID.match(c["cell_id"]):
                raise SchemaError(f"{cw}.cell_id: bad id")
            if c["class"] not in ("kept", "lost", "off_axis"):
                raise SchemaError(f"{cw}.class: expected kept, lost or off_axis")
            _pstat(c["as_compiled"], f"{cw}.as_compiled")
            _pstat(c["aligned"], f"{cw}.aligned")
            if "instr" in c:
                _instr(c["instr"], f"{cw}.instr")
                _instr(c["aligned_instr"], f"{cw}.aligned_instr")
                _bool(c["instr_agree"], f"{cw}.instr_agree")
                if c["instr_label"] != "instructions, not time":
                    raise SchemaError(f"{cw}.instr_label: expected 'instructions, not time'")
            if "placement" in c:
                pl = c["placement"]
                _keys(pl, f"{cw}.placement", ("d", "statistical", "mechanical", "hot_none", "hot_fast", "sensitive"))
                _pstat(pl["d"], f"{cw}.placement.d")
                for k in ("statistical", "mechanical", "sensitive"):
                    _bool(pl[k], f"{cw}.placement.{k}")
                if pl["sensitive"] != (pl["statistical"] and pl["mechanical"]):
                    raise SchemaError(f"{cw}.placement.sensitive: must equal statistical and mechanical")
        v = b["verdict"]
        _keys(v, f"{w}.verdict", ("form", "line", "why", "n", "n_as_compiled", "x_pct", "forward_limit_pct",
                                  "aa_half_width_pct", "placement_sensitive", "off_axis"))
        if v["form"] not in FORMS:
            raise SchemaError(f"{w}.verdict.form: expected one of {FORMS}")
        _str(v["line"], f"{w}.verdict.line")
        _str(v["why"], f"{w}.verdict.why")
        _n(v["n"], f"{w}.verdict.n")
        _n(v["n_as_compiled"], f"{w}.verdict.n_as_compiled")
        if (v["form"] == "map") != (v["n"] is not None):
            raise SchemaError(f"{w}.verdict.n: must be set for map and null otherwise")
        _num(v["x_pct"], f"{w}.verdict.x_pct", nullable=True)
        _num(v["forward_limit_pct"], f"{w}.verdict.forward_limit_pct")
        _num(v["aa_half_width_pct"], f"{w}.verdict.aa_half_width_pct")
        if b["stability"] not in ("stable", "unstable", "not assessable"):
            raise SchemaError(f"{w}.stability: expected stable, unstable or not assessable")
        for j, r in enumerate(b["per_run"]):
            rw = f"{w}.per_run[{j}]"
            _keys(r, rw, ("run_id", "jobs", "form", "line", "cells"))
            if r["form"] not in FORMS + (None,):
                raise SchemaError(f"{rw}.form: expected one of {FORMS} or null")
            if r["cells"] is not None:
                for cid, cols in r["cells"].items():
                    _keys(cols, f"{rw}.cells.{cid}", ("as_compiled", "aligned"))
                    _compact3(cols["as_compiled"], f"{rw}.cells.{cid}.as_compiled")
                    _compact3(cols["aligned"], f"{rw}.cells.{cid}.aligned")
        _keys(b["reproduction"], f"{w}.reproduction", ("checked", "outside", "misses"))
    pg = doc["page"]
    _keys(pg, "pooled.page", ("form", "line", "per_cpu"))
    if pg["form"] is not None:
        raise SchemaError("pooled.page.form: criteria-v3 has no single page-level form (expected null)")
    _str(pg["line"], "pooled.page.line")


def main(argv):
    rc = 0
    for path in argv[1:]:
        try:
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
            kind = doc.get("kind") if isinstance(doc, dict) else None
            {"combined": validate_combined, "pooled": validate_pooled}.get(kind, validate)(doc)
            print(f"schema ok: {path}")
        except (SchemaError, ValueError) as e:
            print(f"schema FAIL: {path}: {e}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
