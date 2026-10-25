"""forwardt/ (timing six forward loops whose bound is a variable; the plan is forwardt/PLAN.md): the six sources, the
argument lists, the sizes, the word of a loop, the build and timing code with the compiler, Linux and valgrind faked,
the file the sweep writes (schema, hashes, smoke flag, partial file) and the workflow.

Generated data only: no network, no compiler, no timing. Plain functions: scripts/check.py's built-in runner runs them
without pytest, and `python3 tests/test_forwardt.py` (the workflow's offline self-test) runs them in file order."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import random
import re
import shlex
import shutil
import stat
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FWT = os.path.join(REPO, "forwardt")


def _load(key, rel):
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


sw = _load("forwardt_sweep", os.path.join("forwardt", "sweep.py"))
import asm  # noqa: E402
import pool  # noqa: E402
import remarks  # noqa: E402
import run as hr  # noqa: E402

LOOPS = sw.LOOPS
ARM = (64 * 1024, 1024 * 1024)       # Neoverse-N2: L1d, L2
EPYC = (32 * 1024, 512 * 1024)       # EPYC 7763
INTEL = (48 * 1024, 2048 * 1024)     # a 48 KiB L1d
CK = "0123456789abcdef"
FORWARDN_TWIN = {"t01_sum_size": "fwn_sum_size", "t02_sum_n": "fwn_sum_n_size_t", "t03_scale_size": "fwn_scale_size",
                 "t04_scale_n": "fwn_scale_n_size_t", "t05_fill_n": "fwn_fill_n", "t06_offset": "fwn_scale_offset"}

# (vectorized, width, interleave) of the NONE and FAST build of each loop in the made-up runs
KEPT = {"none": (True, 4, 2), "fast": (True, 4, 2)}
SCEN = {"t01_sum_size": KEPT,
        "t02_sum_n": {"none": (True, 4, 2), "fast": (False, None, None)},
        "t03_scale_size": KEPT,
        "t04_scale_n": {"none": (True, 4, 2), "fast": (True, 4, 1)},
        "t05_fill_n": KEPT,
        "t06_offset": {"none": (False, None, None), "fast": (False, None, None)}}
WORD_OF = {"t01_sum_size": "kept", "t02_sum_n": "lost", "t03_scale_size": "kept", "t04_scale_n": "narrower",
           "t05_fill_n": "kept", "t06_offset": "scalar in both"}
NOVEC_TIMED = {"t01_sum_size": False, "t02_sum_n": True, "t03_scale_size": False, "t04_scale_n": True,
               "t05_fill_n": True, "t06_offset": False}


@contextlib.contextmanager
def patched(*triples):
    """patched((obj, "name", value), ...): sets attributes and restores them on exit."""
    old = []
    try:
        for obj, name, value in triples:
            old.append((obj, name, getattr(obj, name)))
            setattr(obj, name, value)
        yield
    finally:
        for obj, name, value in reversed(old):
            setattr(obj, name, value)


@contextlib.contextmanager
def env(**kv):
    """Sets the GITHUB_* variables the sweep reads to exactly these (the others removed), restores them on exit."""
    names = ("GITHUB_RUN_ID", "GITHUB_SHA", "GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ATTEMPT")
    old = {k: os.environ.get(k) for k in names}
    try:
        for k in names:
            os.environ.pop(k, None)
        os.environ.update(kv)
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


ACTIONS = dict(GITHUB_RUN_ID="39000000000", GITHUB_SHA="a" * 40, GITHUB_SERVER_URL="https://github.com",
               GITHUB_REPOSITORY="owner/repo")


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- made-up builds, pairs and runs

def vec(t):
    v, w, i = t
    if v:
        msg = f"vectorized loop (vectorization width: {w}, interleaved count: {i}) [-Rpass=loop-vectorize]"
    else:
        msg = "loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]"
    return {"vectorized": v, "width": w, "interleave": i, "remarks": [msg]}


def fake_loop(simd, start="0x1a0", nbytes=36):
    s = int(start, 16)
    return {"start": start, "end": hex(s + nbytes), "bytes": nbytes, "start_mod64": s % 64, "crosses64": False,
            "windows64": 1, "min_windows64": 1, "extra_window": False, "insns": 9, "simd": simd, "innermost": True}


def fake_info(loop, build_dir, scen, a64=None, missing=None):
    """What sw.build_loop returns, without a compiler: tiny files for the binaries and the vectorization of `scen`
    (a64: {loop: {"none_a64"|"fast_a64": (v, w, i)}} to make the aligned builds differ from the as-compiled ones)."""
    os.makedirs(build_dir, exist_ok=True)
    sc = scen[loop]
    over = (a64 or {}).get(loop, {})
    spec = {"none": sc["none"], "fast": sc["fast"], "none_a64": over.get("none_a64", sc["none"]),
            "fast_a64": over.get("fast_a64", sc["fast"]), "novec": (False, None, None)}
    info = {"source": sw.source_rel(loop), "loop_line": 7, "builds": {}, "diff": "--- none\n+++ fast\n",
            "diff_aligned": "--- none_a64\n+++ fast_a64\n"}
    for m in sw.MODES:
        p = os.path.join(build_dir, f"{loop}.{m}")
        content = f"binary {loop} {m}".encode()
        if m != missing:
            with open(p, "wb") as f:
                f.write(content)
            os.chmod(p, 0o755)
        info["builds"][m] = {"binary": p, "sha256": hashlib.sha256(content).hexdigest(), "command": f"clang++-18 -o {m}",
                             "vectorization": vec(spec[m]), "traps": 1 if m.startswith("fast") else 0, "asm_lines": 20,
                             "loops": [fake_loop(spec[m][0])]}
    return info


def gen_pair(rng, base, nreps, ratio, noise=0.002):
    """A pair() result with generated samples in ABBA order; B takes `ratio` times as long as A."""
    a_ns, b_ns, order = [], [], []
    for k in range(nreps):
        for side in (("A", "B") if k % 2 == 0 else ("B", "A")):
            v = base * (ratio if side == "B" else 1.0) * (1 + rng.uniform(-noise, noise))
            (a_ns if side == "A" else b_ns).append(v)
            order.append(side)
    return {"a_ns": a_ns, "b_ns": b_ns, "a_checksums": [CK], "b_checksums": [CK], "checksum_match": True,
            "order": "".join(order)}


class Calls(list):
    """The pair calls (a, b, args) of a faked run, as before; besides, what the stubs saw:
    .calibrate  (binary path, loop, n, cpu) of every calibrate call, in order
    .pair_cpu   the cpu argument of every hr.pair call, in order
    .copymode   (src, dst) of every shutil.copymode call
    .aa_modes   (permission bits of the copy, of the NONE binary) at the moment each A/A pair is timed"""

    def __init__(self):
        super().__init__()
        self.calibrate, self.pair_cpu, self.copymode, self.aa_modes = [], [], [], []


@contextlib.contextmanager
def faked(crit_reps=4, scen=None, a64=None, missing=None, break_at=None, raise_at=None, fast_ratio=1.5, clang=None,
          machine=ARM):
    """harness/run.py with no compiler, no Linux and no valgrind: build_loop writes tiny files, pair() returns generated
    samples, calibrate and instr_count are stubs. The sweep's own run_sweep and main run for real. `crit_reps` is what
    harness/criteria-v3.json is made to say (the real value is 40). Yields the list of pair calls (a, b, args) and the
    list of instr_count calls."""
    scen = scen or SCEN
    rng = random.Random(7)
    calls, instr_calls = Calls(), []
    sizes = sw.sizes_for({"l1d": machine[0], "l2": machine[1]})
    real_copymode = shutil.copymode

    def cell_of(b_name, args):
        loop = b_name.split(".")[0]
        for size in sw.SIZES:
            if sizes[size]["n"][loop] == args[0]:
                return f"{loop}.{size}"
        raise AssertionError(f"no cell has n = {args[0]} for {loop}")

    def build_loop(loop, build_dir, out_dir):
        return fake_info(loop, build_dir, scen, a64, missing)

    def calibrate(binary, loop, n, cpu):
        calls.calibrate.append((binary, loop, n, cpu))
        return 1000 + n % 7, 1.0e6

    def copymode(src, dst):
        calls.copymode.append((src, dst))
        real_copymode(src, dst)

    def instr_count(binary, loop, n, out_dir, tag):
        instr_calls.append(tag)
        return n * 100 + (77 if tag.endswith(".fast") else 0), "ok"

    def pair_fn(a, b, args, nreps, cpu):
        bb = os.path.basename(b)
        calls.append((os.path.basename(a), bb, list(args)))
        calls.pair_cpu.append(cpu)
        if bb.endswith(".none_copy"):
            calls.aa_modes.append((stat.S_IMODE(os.stat(b).st_mode), stat.S_IMODE(os.stat(a).st_mode)))
        where = cell_of(bb, args)
        if raise_at == where and bb.endswith(".fast"):
            raise RuntimeError("fake: a timed process exited 1")
        pr = gen_pair(rng, 1000.0 * args[0], nreps, fast_ratio if "fast" in bb else 1.0)
        if break_at == where and bb.endswith(".fast"):
            pr["b_checksums"], pr["checksum_match"] = ["deadbeefdeadbeef"], False
        return pr

    runner = {"os": "Fake", "kernel": "k", "arch": "aarch64", "cpu_model": "Fake-N2", "cores": 4, "l1d_kib": machine[0] // 1024,
              "l2_kib": machine[1] // 1024, "l3_kib": 32768}
    tool = {"clang": clang or "Ubuntu clang version 18.1.3 (1ubuntu1)", "libcxx_package": "libc++-18-dev 1:18.1.3-1"}
    with patched((sw, "reps_per_side", lambda: crit_reps),
                 (hr, "caches", lambda: {"l1d": machine[0], "l2": machine[1], "l3": 32 << 20, "llc": 32 << 20}),
                 (hr, "runner_info", lambda cache: (dict(runner), "lscpu text")),
                 (hr, "toolchain", lambda: dict(tool)),
                 (sw, "build_loop", build_loop),
                 (sw, "calibrate", calibrate),
                 (sw, "instr_count", instr_count),
                 (shutil, "copymode", copymode),
                 (hr, "pair", pair_fn)):
        yield calls, instr_calls


def run_job(tmp, extra=(), environment=ACTIONS, **fk):
    """sw.main with the harness faked; returns (exit code, stdout text, the calls, the instr_count calls, out, build)."""
    out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
    buf = io.StringIO()
    with faked(**fk) as (calls, icalls):
        with env(**environment), contextlib.redirect_stdout(buf):
            code = sw.main(["--job", "3", "--out", out, "--build", build, "--cpu", "2"] + list(extra))
    return code, buf.getvalue(), calls, icalls, out, build


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_GOOD = {}


def good_doc():
    """A forwardt.json written by the faked sweep (crit_reps = reps = 4, so smoke is false), cached; returns a copy."""
    if "doc" not in _GOOD:
        with tempfile.TemporaryDirectory() as tmp:
            run_job(tmp)
            _GOOD["doc"] = load_json(os.path.join(tmp, "out", sw.RESULT_NAME))
    return copy.deepcopy(_GOOD["doc"])


def valid(doc, crit=4):
    """validate_doc with the criteria file made to say `crit` repetitions per side."""
    with patched((sw, "reps_per_side", lambda: crit)):
        return sw.validate_doc(doc, reps=doc.get("reps_per_side"))


# ---------------------------------------------------------------- the sources

def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def _function(src, name):
    """(parameters, body) of `void name(...) { ... }` (the closing brace in column 0), whitespace-normalized."""
    m = re.search(r"void %s\((.*?)\)\s*\{\n(.*?)\n\}\n" % re.escape(name), src, re.S)
    assert m, f"{name} not found"
    return _norm(m.group(1)), _norm(m.group(2))


def test_every_source_has_one_loop_marker_on_a_for_line_and_its_twin_in_forwardn():
    twin_src = read_text(os.path.join(REPO, "forwardn", "source.cpp"))
    for loop in LOOPS:
        path = os.path.join(FWT, "kernels", loop + ".cpp")
        src = read_text(path)
        lines = src.splitlines()
        marked = [i for i, ln in enumerate(lines, 1) if "// LOOP" in ln]
        assert len(marked) == 1, f"{loop}: {len(marked)} lines carry the // LOOP marker"
        assert re.match(r"\s*for \(", lines[marked[0] - 1]), f"{loop}: the marker is not on a for line"
        assert remarks.loop_line(src) == marked[0]
        assert "__attribute__((noinline)) void kern_" + loop + "(" in src and '#include "../../kernels/common.hpp"' in src
        params, body = _function(src, "kern_" + loop)
        t_params, t_body = _function(twin_src, FORWARDN_TWIN[loop])
        assert params == t_params, f"{loop}: the parameters differ from {FORWARDN_TWIN[loop]}"
        assert body == t_body, f"{loop}: the body differs from {FORWARDN_TWIN[loop]}"
        usage = [ln for ln in lines if ln.startswith("// Usage:")]
        assert len(usage) == 1
        assert usage[0].count("<") == len(sw.args_for(loop, 1, 1)), f"{loop}: the usage line and args_for disagree"
        has_off = "argv[3]" in src
        assert has_off == (loop in sw.OFF_LOOPS), f"{loop}: only the offset loop reads a third argument"


def test_the_driver_of_each_source_reports_through_the_common_header():
    for loop in LOOPS:
        src = read_text(os.path.join(FWT, "kernels", loop + ".cpp"))
        assert "parse_args(argc, argv, n, iters)" in src and "report(n, iters," in src
        assert src.count("BARRIER();") == 2, f"{loop}: one barrier after the warm-up and one inside the timed loop"
    assert "checksum(c)" in read_text(os.path.join(FWT, "kernels", "t05_fill_n.cpp"))


# ---------------------------------------------------------------- arguments and sizes

def test_args_for_gives_two_arguments_and_the_offset_loop_a_third():
    for loop in LOOPS:
        assert sw.args_for(loop, 4096, 1) == ([4096, 1, 0] if loop == "t06_offset" else [4096, 1])
        assert sw.args_for(loop, 64, 20)[:2] == [64, 20]
    assert sw.OFF == 0 and sw.OFF_LOOPS == ("t06_offset",)


def test_sizes_follow_the_rule_for_each_cache_size():
    got = sw.sizes_for({"l1d": ARM[0], "l2": ARM[1]})
    assert got["L1"]["target_bytes"] == 32768 and got["L2"]["target_bytes"] == 524288
    assert got["L1"]["n"] == {"t01_sum_size": 8192, "t02_sum_n": 8192, "t03_scale_size": 4096, "t04_scale_n": 4096,
                              "t05_fill_n": 8192, "t06_offset": 4096}
    assert got["L2"]["n"] == {"t01_sum_size": 131072, "t02_sum_n": 131072, "t03_scale_size": 65536,
                              "t04_scale_n": 65536, "t05_fill_n": 131072, "t06_offset": 65536}
    for machine in (ARM, EPYC, INTEL):
        s = sw.sizes_for({"l1d": machine[0], "l2": machine[1]})
        assert list(s) == ["L1", "L2"]
        for size, half in (("L1", machine[0] // 2), ("L2", machine[1] // 2)):
            assert s[size]["target_bytes"] == half
            for loop in LOOPS:
                n = s[size]["n"][loop]
                assert n == max(64, half // sw.BYTES_PER_ELEMENT[loop])
                assert sw.working_set(loop, n) <= half and sw.working_set(loop, n + 1) > half
    assert sw.BYTES_PER_ELEMENT == {"t01_sum_size": 4, "t02_sum_n": 4, "t03_scale_size": 8, "t04_scale_n": 8,
                                    "t05_fill_n": 4, "t06_offset": 8}
    assert sw.n_for_loop("t01_sum_size", 100) == 64, "a tiny cache still gets 64 elements"


def test_assume_caches_prints_the_sizes_and_stops():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert sw.main(["--assume-caches", "64,1024"]) == 0
    assert json.loads(buf.getvalue()) == sw.sizes_for({"l1d": ARM[0], "l2": ARM[1]})
    try:
        sw.main(["--assume-caches", "64"])
    except SystemExit as e:
        assert "two integers" in str(e)
    else:
        raise AssertionError("one number must be refused")


def test_the_default_output_folder_is_one_the_repository_check_does_not_read():
    """A run without --out (a code test on a Linux checkout) must leave nothing that scripts/check.py takes for an unrecorded
    measurement: the default lies under build/, which git ignores, and not under forwardt/ or results/."""
    chk = _load("repo_check_script", os.path.join("scripts", "check.py"))
    assert sw.DEFAULT_OUT == os.path.join(REPO, "build", "forwardt-out")
    with open(os.path.join(FWT, "sweep.py"), encoding="utf-8") as f:
        assert 'ap.add_argument("--out", default=DEFAULT_OUT)' in f.read(), "the --out default must be DEFAULT_OUT"
    with open(os.path.join(REPO, ".gitignore"), encoding="utf-8") as f:
        assert "build/" in [ln.strip() for ln in f], "build/ must stay in .gitignore"
    with tempfile.TemporaryDirectory() as tmp:
        for sub in (os.path.join("build", "forwardt-out"), os.path.join("forwardt", "out")):
            os.makedirs(os.path.join(tmp, sub))
            with open(os.path.join(tmp, sub, "forwardt.json"), "w", encoding="utf-8") as f:
                f.write("{}")
        seen = [os.path.relpath(p, tmp).replace(os.sep, "/") for p in chk.forwardt_result_files(tmp)]
        # the old default is found (so this test would have failed on it), the new one is not
        assert seen == ["forwardt/out/forwardt.json"], seen


# ---------------------------------------------------------------- the words

def _entry(t):
    return {"vectorized": t[0], "width": t[1], "interleave": t[2]}


def _forwardn():
    key = "forwardn_run"
    if key in sys.modules:
        return sys.modules[key]
    ce = os.path.join(REPO, "ce-sweep")
    sys.path.insert(0, ce)
    try:
        return _load(key, os.path.join("forwardn", "run.py"))
    finally:
        if ce in sys.path:
            sys.path.remove(ce)


def test_word_names_each_case_and_agrees_with_the_forwardn_classifier():
    fw = _forwardn()
    cases = [((True, 4, 2), (False, None, None), "lost"), ((True, 4, 2), (True, 4, 2), "kept"),
             ((True, 4, 2), (True, 4, 1), "narrower"), ((True, 4, 2), (True, 2, 2), "narrower"),
             ((False, None, None), (False, None, None), "scalar in both"), ((False, None, None), (True, 4, 2), "gained")]
    for n, h, want in cases:
        assert sw.word(_entry(n), _entry(h)) == want == fw.word(_entry(n), _entry(h)), (n, h)
    silent = {"vectorized": None, "width": None, "interleave": None}
    assert sw.word(_entry((True, 4, 2)), silent) == "lost", "no remark with the checks on counts as not vectorized"
    assert sw.word(silent, silent) == "scalar in both" and fw.word(silent, silent) == "scalar in both"
    assert set(sw.WORDS) == {c[2] for c in cases}


def test_direction_of_a_narrower_loop_is_stored_and_none_for_other_words():
    d = sw.direction
    assert d(_entry((True, 4, 2)), _entry((True, 4, 1))) == "smaller"
    assert d(_entry((True, 4, 1)), _entry((True, 8, 1))) == "larger"
    assert d(_entry((True, 4, 2)), _entry((True, 8, 1))) == "equal", "(W, I) differ and W * I is the same"
    assert d(_entry((True, 4, 2)), _entry((True, 4, None))) == "unknown", "no interleave count in the remark"
    for n, h in (((True, 4, 2), (True, 4, 2)), ((True, 4, 2), (False, None, None)), ((False, None, None), (True, 4, 2)),
                 ((False, None, None), (False, None, None))):
        assert d(_entry(n), _entry(h)) is None
    assert sw.vector_step(_entry((True, 4, 2))) == 8 and sw.vector_step(_entry((False, None, None))) is None
    assert sw.vector_step(_entry((True, 4, None))) is None


def test_words_record_follows_the_vectorization_of_the_builds_and_flags_disagreement():
    def builds(none, fast, none_a, fast_a):
        return {"none": {"vectorization": vec(none)}, "fast": {"vectorization": vec(fast)},
                "none_a64": {"vectorization": vec(none_a)}, "fast_a64": {"vectorization": vec(fast_a)}}
    a, off = (True, 4, 2), (False, None, None)
    w = sw.words_record(builds(a, off, a, off))
    assert w["compiled"]["word"] == "lost" and w["aligned"]["word"] == "lost" and w["agree"] is True
    assert w["compiled"]["direction"] is None and w["compiled"]["none"] == {"vectorized": True, "width": 4, "interleave": 2}
    assert w["compiled"]["fast"] == {"vectorized": False, "width": None, "interleave": None}
    w = sw.words_record(builds(a, (True, 4, 1), a, (True, 4, 1)))
    assert w["compiled"]["word"] == "narrower" and w["compiled"]["direction"] == "smaller" and w["agree"] is True
    w = sw.words_record(builds(a, a, a, off))
    assert w["compiled"]["word"] == "kept" and w["aligned"]["word"] == "lost" and w["agree"] is False


def test_vectorization_record_reads_the_last_remark_and_its_interleave_count():
    src = "forwardt/kernels/t02_sum_n.cpp"
    first = f"{src}:8:3: remark: vectorized loop (vectorization width: 2, interleaved count: 1) [-Rpass=loop-vectorize]"
    second = f"{src}:8:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]"
    other_line = f"{src}:9:3: remark: vectorized loop (vectorization width: 16, interleaved count: 4) [-Rpass=loop-vectorize]"
    v = sw.vectorization_record("\n".join([first, other_line, second]), src, 8)
    assert (v["vectorized"], v["width"], v["interleave"]) == (True, 4, 2) and len(v["remarks"]) == 2
    nv = f"{src}:8:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]"
    v = sw.vectorization_record(nv, src, 8)
    assert (v["vectorized"], v["width"], v["interleave"]) == (False, None, None)
    v = sw.vectorization_record(other_line, src, 8)
    assert (v["vectorized"], v["width"], v["interleave"]) == (None, None, None), "clang said nothing about line 8"
    v = sw.vectorization_record(f"{src}:8:3: remark: vectorized loop (vectorization width: 8) [-Rpass=loop-vectorize]", src, 8)
    assert (v["vectorized"], v["width"], v["interleave"]) == (True, 8, None)
    v = sw.vectorization_record("\n".join([second, nv]), src, 8)
    assert (v["vectorized"], v["width"], v["interleave"]) == (True, 4, 2), "a later 'not vectorized' remark does not undo it"


# ---------------------------------------------------------------- build, calibrate, instructions (tools faked)

class Res:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def objdump_text(loop, trap):
    name = f"_Z{len('kern_' + loop)}kern_{loop}RKNSt3__16vectorIiNS_9allocatorIiEEEEmPl"
    body = ["    1180:\txor    %eax,%eax", "    1182:\tpxor   %xmm0,%xmm0", "    1186:\tpaddd  (%rdi,%rax,4),%xmm0",
            "    118b:\tadd    $0x4,%rax", "    118f:\tcmp    %rax,%rsi",
            f"    1192:\tjne    1186 <{name}+0x6>"]
    if trap:
        body.append("    1194:\tud2")
    body.append("    1196:\tret")
    return "0000000000001180 <" + name + ">:\n" + "\n".join(body) + "\n\ndead beef\n"


def fake_toolchain(loop, line, fail_on=None, no_function=False):
    """A stand-in for harness/run.py's sh(): writes the binaries a compile asks for, answers with canned clang remarks
    (NONE vectorizes the loop, FAST does not) and a canned objdump. Returns (sh, commands)."""
    cmds = []
    src = f"forwardt/kernels/{loop}.cpp"

    def sh(cmd, **kw):
        cmds.append(list(cmd))
        if cmd[0] == hr.CXX:
            o = cmd[cmd.index("-o") + 1]
            mode = o.rsplit(".", 1)[1]
            if fail_on == mode:
                return Res(1, "", "error: boom")
            path = os.path.normpath(os.path.join(sw.REPO, o))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(f"bin {loop} {mode}".encode())
            if mode.startswith("fast") or mode == "novec":
                err = f"{src}:{line}:3: remark: loop not vectorized: could not determine number of loop iterations [-Rpass-analysis=loop-vectorize]\n"
            else:
                err = f"{src}:{line}:3: remark: vectorized loop (vectorization width: 4, interleaved count: 2) [-Rpass=loop-vectorize]\n"
            return Res(0, "", err)
        if cmd[0] == hr.OBJDUMP:
            mode = cmd[-1].rsplit(".", 1)[1]
            return Res(0, "nothing here\n" if no_function else objdump_text(loop, mode.startswith("fast")), "")
        return Res(0)
    return sh, cmds


def test_build_loop_with_a_stubbed_toolchain_records_every_build():
    loop = "t02_sum_n"
    line = remarks.loop_line(read_text(os.path.join(FWT, "kernels", loop + ".cpp")))
    with tempfile.TemporaryDirectory() as tmp:
        build_dir, out_dir = os.path.join(tmp, "build"), os.path.join(tmp, "out")
        for sub in ("remarks", "asm"):
            os.makedirs(os.path.join(out_dir, sub))
        sh, cmds = fake_toolchain(loop, line)
        with patched((hr, "sh", sh)):
            info = sw.build_loop(loop, build_dir, out_dir)
        clang = [c for c in cmds if c[0] == hr.CXX]
        assert len(clang) == 5 and len([c for c in cmds if c[0] == hr.OBJDUMP]) == 5
        by_mode = {c[c.index("-o") + 1].rsplit(".", 1)[1]: c for c in clang}
        assert set(by_mode) == set(sw.MODES)
        for mode, c in by_mode.items():
            assert c[-1] == "forwardt/kernels/t02_sum_n.cpp" and "-stdlib=libc++" in c and "-O2" in c
            assert "-Rpass=loop-vectorize" in c and "-Rpass-missed=loop-vectorize" in c
            assert ("-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_FAST" in c) == mode.startswith("fast")
            assert ("-falign-loops=64" in c) == mode.endswith("_a64"), mode
            assert ("-fno-vectorize" in c) == (mode == "novec")
        assert info["source"] == "forwardt/kernels/t02_sum_n.cpp" and info["loop_line"] == line
        b = info["builds"]
        assert set(b) == set(sw.MODES) and b["fast"]["traps"] == 1 and b["none"]["traps"] == 0
        assert b["none"]["vectorization"]["vectorized"] is True and b["none"]["vectorization"]["interleave"] == 2
        assert b["fast"]["vectorization"]["vectorized"] is False and b["novec"]["vectorization"]["vectorized"] is False
        assert b["none"]["sha256"] != b["fast"]["sha256"] and b["none"]["command"].endswith("forwardt/kernels/t02_sum_n.cpp")
        assert "ud2" in info["diff"] and "ud2" in info["diff_aligned"]
        rec = sw.builds_record(info)
        hot = rec["none"]["hot_loop"]
        assert hot["simd"] is True and hot["start"] == "0x1186" and hot["bytes"] == 0x1196 - 0x1186
        assert set(rec["none"]["hot_loop"]) == set(sw.LOOP_KEYS) and rec["none"]["loops"][0]["innermost"] is True
        assert "binary" not in rec["none"] and rec["fast"]["asm_lines"] == 9
        lr = sw.loop_record(loop, info)
        assert lr["words"]["compiled"]["word"] == "lost" and lr["novec_timed"] is True and lr["off"] is None
        assert lr["function"] == "kern_t02_sum_n" and lr["bytes_per_element"] == 4
        for sub, name in (("remarks", "t02_sum_n.fast.txt"), ("asm", "t02_sum_n.fast.s"), ("asm", "t02_sum_n.novec.s")):
            assert os.path.exists(os.path.join(out_dir, sub, name)), name
        assert asm.count_traps(read_text(os.path.join(out_dir, "asm", "t02_sum_n.fast.s")).splitlines()) == 1


def test_build_loop_stops_on_a_failed_compile_or_a_missing_function():
    loop = "t06_offset"
    line = remarks.loop_line(read_text(os.path.join(FWT, "kernels", loop + ".cpp")))
    with tempfile.TemporaryDirectory() as tmp:
        build_dir, out_dir = os.path.join(tmp, "build"), os.path.join(tmp, "out")
        for sub in ("remarks", "asm"):
            os.makedirs(os.path.join(out_dir, sub))
        sh, _ = fake_toolchain(loop, line, fail_on="fast_a64")
        with patched((hr, "sh", sh)):
            try:
                sw.build_loop(loop, build_dir, out_dir)
            except SystemExit as e:
                assert "build failed t06_offset fast_a64" in str(e) and "boom" in str(e)
            else:
                raise AssertionError("a failed compile must stop the job")
        sh, _ = fake_toolchain(loop, line, no_function=True)
        with patched((hr, "sh", sh)):
            try:
                sw.build_loop(loop, build_dir, out_dir)
            except SystemExit as e:
                assert "kern_t06_offset not found in the objdump" in str(e)
            else:
                raise AssertionError("a binary without the kernel function must stop the job")


def test_calibrate_is_the_harness_rule_with_the_argument_list_of_each_loop():
    for loop in LOOPS:
        seen, vals = [], iter([3e6, 1e6, 2e6])

        def run_bin(binary, args, cpu):
            seen.append((binary, list(args), cpu))
            return next(vals), CK
        with patched((hr, "run_bin", run_bin)):
            iters, best = sw.calibrate("bin", loop, 4096, "2")
        assert (iters, best) == (75, 1e6), "round(75e6 / 1e6) iterations from the best of three"
        assert seen == [("bin", [4096, 1, 0] if loop == "t06_offset" else [4096, 1], "2")] * 3
    # the same answer as the harness's own calibrate on a loop with two arguments
    for ns in ([3e6, 1e6, 2e6], [8e7, 9e7, 7e7], [1e12, 2e12, 3e12], [1e-3, 5e-3, 1e-2]):
        a, b = iter(ns), iter(ns)
        with patched((hr, "run_bin", lambda binary, args, cpu: (next(a), CK))):
            ours = sw.calibrate("bin", "t01_sum_size", 4096, "2")
        with patched((hr, "run_bin", lambda binary, args, cpu: (next(b), CK))):
            assert ours == hr.calibrate("bin", 4096, "2")
    assert ours[0] == 10_000_000 and sw.ITERATION_LIMITS == (1, 10_000_000)
    with patched((hr, "run_bin", lambda binary, args, cpu: (1e12, CK))):
        assert sw.calibrate("bin", "t01_sum_size", 4096, "2")[0] == 1
    with patched((hr, "run_bin", lambda binary, args, cpu: (0.0, CK))):
        try:
            sw.calibrate("bin", "t01_sum_size", 4096, "2")
        except SystemExit as e:
            assert "reported 0.0 ns" in str(e)
        else:
            raise AssertionError("a zero time cannot calibrate anything")


def test_instr_count_uses_the_cachegrind_call_and_divides_by_the_calls():
    text = "events: Ir\nfl=x.cpp\nfn=kern_t06_offset(std::vector&)\n11 2100\nfn=main\n5 99999\nsummary: 102099\n"
    seen = []

    def sh(cmd, **kw):
        seen.append(list(cmd))
        if cmd[0] == hr.VALGRIND:
            target = next(c for c in cmd if c.startswith("--cachegrind-out-file=")).split("=", 1)[1]
            with open(target, "w", encoding="utf-8") as f:
                f.write(text)
        return Res(0)
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "cachegrind"))
        with patched((sw.shutil, "which", lambda x: "/usr/bin/valgrind"), (hr, "sh", sh)):
            ir, note = sw.instr_count("bin/t06", "t06_offset", 4096, tmp, "t06_offset.L1.none")
            ir2, note2 = sw.instr_count("bin/t01", "t01_sum_size", 4096, tmp, "t01_sum_size.L1.none")
        assert (ir, note) == (100, "ok"), "2100 instructions in kern_t06_offset over 21 calls"
        assert ir2 is None and "not found" in note2, "the output names only kern_t06_offset and main"
        assert seen[0][seen[0].index("bin/t06"):] == ["bin/t06", "4096", "20", "0"], "t06 gets the third argument"
        assert seen[1][seen[1].index("bin/t01"):] == ["bin/t01", "4096", "20"]
        assert "--tool=cachegrind" in seen[0] and "--cache-sim=no" in seen[0]
        assert os.path.exists(os.path.join(tmp, "cachegrind", "t06_offset.L1.none.out"))
        # valgrind exits non-zero, writes nothing, or the function is not in the output
        with patched((sw.shutil, "which", lambda x: "/usr/bin/valgrind"), (hr, "sh", lambda cmd, **kw: Res(1, "", "boom"))):
            ir, note = sw.instr_count("b", "t01_sum_size", 64, tmp, "failing")
        assert ir is None and note.startswith("valgrind exited 1") and "boom" in note
        text = "events: Ir\nfn=main\n5 99\n"
        with patched((sw.shutil, "which", lambda x: "/usr/bin/valgrind"), (hr, "sh", sh)):
            ir, note = sw.instr_count("b", "t01_sum_size", 64, tmp, "nofn")
        assert ir is None and "not found" in note
        with patched((sw.shutil, "which", lambda x: None)):
            assert sw.instr_count("b", "t01_sum_size", 64, tmp, "x") == (None, "valgrind not found")


# ---------------------------------------------------------------- cells and pairs

def _pairs(**changes):
    def p(a_ck=(CK,), b_ck=(CK,), match=True):
        return {"a_checksums": list(a_ck), "b_checksums": list(b_ck), "checksum_match": match}
    pairs = {"compiled": p(), "aligned": p(), "aa": p(), "novec": p()}
    pairs.update(changes)
    return pairs


def test_cell_checksum_needs_every_pair_to_print_the_one_checksum():
    assert sw.cell_checksum(_pairs()) == (CK, True)
    assert sw.cell_checksum(_pairs(novec=None)) == (CK, True), "a loop without NOVEC has three pairs"
    assert sw.cell_checksum(_pairs(aligned={"a_checksums": [CK], "b_checksums": ["other"], "checksum_match": False}))[1] is False
    assert sw.cell_checksum(_pairs(aa={"a_checksums": ["other"], "b_checksums": ["other"], "checksum_match": True}))[1] is False, \
        "every pair agrees with itself but not with the compiled pair"
    assert sw.cell_checksum(_pairs(compiled={"a_checksums": [CK, "x"], "b_checksums": [CK, "x"], "checksum_match": False}))[1] is False
    assert sw.cell_checksum(_pairs(novec={"a_checksums": [CK], "b_checksums": ["z"], "checksum_match": False}))[1] is False
    # a NONE side that printed two values has no single checksum, even if a pair claims a match: not ok, none stored
    two = {"a_checksums": [CK, "x"], "b_checksums": [CK, "x"], "checksum_match": True}
    assert sw.cell_checksum(_pairs(compiled=two, aligned=two, aa=two, novec=two)) == (None, False)
    assert sw.cell_checksum(_pairs(compiled={"a_checksums": [], "b_checksums": [], "checksum_match": True}))[1] is False


def test_time_cell_times_the_pairs_in_order_with_the_right_arguments_and_builds():
    rng = random.Random(3)
    calls, cal = [], []

    def pair_fn(a, b, args, nreps, cpu):
        calls.append((os.path.basename(a), os.path.basename(b), list(args), nreps, cpu))
        return gen_pair(rng, 1000.0, nreps, 1.4 if b.endswith(".fast") else 1.0)

    def calibrate_fn(binary, lp, n, cpu):
        cal.append((binary, lp, n, cpu))
        return 321, 2.5e6

    for loop in ("t04_scale_n", "t06_offset"):
        for novec_timed in (True, False):
            calls.clear()
            cal.clear()
            with tempfile.TemporaryDirectory() as tmp:
                info = fake_info(loop, tmp, SCEN)
                bins = {m: info["builds"][m]["binary"] for m in sw.MODES}
                shas = {m: info["builds"][m]["sha256"] for m in sw.MODES}
                copy_path = os.path.join(tmp, loop + ".none_copy")
                shutil.copyfile(bins["none"], copy_path)
                with patched((sw, "calibrate", calibrate_fn), (hr, "pair", pair_fn)):
                    cell = sw.time_cell(loop, "L1", 4096, bins, shas, copy_path, 4, "2", novec_timed, sw.stats.summarize)
                assert cal == [(bins["none"], loop, 4096, "2")], "one calibration, on the NONE binary, at this n, on the pinned CPU"
            tail = [0] if loop == "t06_offset" else []
            names = [(a.split(".")[1], b.split(".")[1]) for a, b, *_ in calls]
            want = [("none", "fast"), ("none_a64", "fast_a64"), ("none", "none_copy")] + ([("none", "novec")] if novec_timed else [])
            assert names == want
            assert all(c[2] == [4096, 321] + tail and c[3] == 4 and c[4] == "2" for c in calls)
            assert cell["iters"] == 321 and cell["calibration_ns_one_call"] == 2.5e6 and cell["n"] == 4096
            assert cell["calibrate_args"] == [4096, 1] + tail and cell["timed_args"] == [4096, 321] + tail
            assert cell["working_set_bytes"] == 4096 * sw.BYTES_PER_ELEMENT[loop]
            assert cell["checksum"] == CK and cell["checksum_match"] is True
            assert (cell["pairs"]["novec"] is not None) == novec_timed
            aa = cell["pairs"]["aa"]
            assert aa["a_binary_sha256"] == aa["b_binary_sha256"] == shas["none"] and aa["b_build"] == "none_copy"
            comp = cell["pairs"]["compiled"]
            assert (comp["a_build"], comp["b_build"]) == ("none", "fast") and comp["b_binary_sha256"] == shas["fast"]
            assert comp["ratio"] > 1.3 and comp["n_per_side"] == 4 and len(comp["ci95"]) == 2
            al = cell["pairs"]["aligned"]
            assert (al["a_build"], al["b_build"]) == ("none_a64", "fast_a64") and al["a_binary_sha256"] == shas["none_a64"]


def test_time_cell_refuses_an_a_a_copy_that_is_not_the_none_binary():
    with tempfile.TemporaryDirectory() as tmp:
        info = fake_info("t01_sum_size", tmp, SCEN)
        bins = {m: info["builds"][m]["binary"] for m in sw.MODES}
        shas = {m: info["builds"][m]["sha256"] for m in sw.MODES}
        copy_path = os.path.join(tmp, "t01_sum_size.none_copy")
        with open(copy_path, "wb") as f:
            f.write(b"not the same")
        timed, cal = [], []
        rng = random.Random(5)

        def pair_fn(a, b, args, nreps, cpu):
            timed.append((a, b))
            return gen_pair(rng, 1000.0, nreps, 1.0)

        def calibrate_fn(binary, lp, n, cpu):
            cal.append((binary, lp, n, cpu))
            return 10, 1e6
        with patched((sw, "calibrate", calibrate_fn), (hr, "pair", pair_fn)):
            try:
                sw.time_cell("t01_sum_size", "L1", 64, bins, shas, copy_path, 4, "2", False, sw.stats.summarize)
            except SystemExit as e:
                assert "not byte-identical" in str(e)
            else:
                raise AssertionError("a copy that differs must stop the cell")
        assert cal == [(bins["none"], "t01_sum_size", 64, "2")], "the calibration comes before the A/A check, on the NONE binary"
        assert [t for t in timed if t[0].endswith("none_copy") or t[1].endswith("none_copy")] == [], "the A/A was not timed"


# ---------------------------------------------------------------- the job and its file

def test_run_sweep_end_to_end_with_the_harness_faked():
    with tempfile.TemporaryDirectory() as tmp:
        code, text, calls, icalls, out, build = run_job(tmp)
        assert code == 0
        doc = load_json(os.path.join(out, sw.RESULT_NAME))
        assert valid(doc) == [], valid(doc)
        assert doc["kind"] == "forwardt" and doc["schema_version"] == 1 and doc["criteria_file"] == "harness/criteria-v3.json"
        assert doc["smoke"] is False and doc["reps_per_side"] == 4 and doc["pinned_cpu"] == "2"
        assert doc["target_ns_per_process"] == hr.TARGET_NS
        assert doc["sizes"] == sw.sizes_for({"l1d": ARM[0], "l2": ARM[1]})
        assert doc["machine"]["cache_bytes"]["l1d"] == ARM[0] and doc["machine"]["lscpu"] == "lscpu text"
        assert doc["loop_order"] == list(LOOPS) and list(doc["loops"]) == list(LOOPS)
        assert doc["timing_order"] == [f"{lp}.{s}" for lp in LOOPS for s in ("L1", "L2")] and len(doc["timing_order"]) == 12
        assert doc["run"]["id"] == "39000000000" and doc["run"]["job"] == "3" and doc["run"]["commit"] == "a" * 40
        assert doc["run"]["attempt"] == 1 and "attempt" not in text.lower(), "the first attempt says nothing about attempts"
        assert doc["run"]["workflow_run_url"] == "https://github.com/owner/repo/actions/runs/39000000000"
        assert doc["run"]["runner"]["cpu_model"] == "Fake-N2" and "18.1.3" in doc["run"]["toolchain"]["clang"]
        assert doc["plan_sha256"] == sw.plan_sha256() and doc["criteria_sha256"] == sw.criteria_sha256()
        assert doc["code_sha256"] == sw.code_sha256()
        for loop in LOOPS:
            rec = doc["loops"][loop]
            assert rec["words"]["compiled"]["word"] == WORD_OF[loop] and rec["words"]["agree"] is True
            assert rec["novec_timed"] is NOVEC_TIMED[loop]
            assert rec["builds"]["fast"]["traps"] == 1 and rec["builds"]["none"]["traps"] == 0
            for size in ("L1", "L2"):
                cell = rec["cells"][size]
                assert cell["n"] == doc["sizes"][size]["n"][loop] and cell["checksum"] == CK
                assert (cell["pairs"]["novec"] is not None) == NOVEC_TIMED[loop]
                assert cell["pairs"]["aa"]["a_binary_sha256"] == rec["builds"]["none"]["binary_sha256"]
            ins = rec["instr"]
            n1 = doc["sizes"]["L1"]["n"][loop]
            assert ins["none"] == n1 * 100 and ins["fast"] == n1 * 100 + 77 and ins["size"] == "L1" and ins["note"] == "ok"
            assert abs(ins["ratio"] - (n1 * 100 + 77) / (n1 * 100)) < 1e-12 and "not time" in ins["unit"]
            assert ins["args"] == sw.args_for(loop, n1, hr.CG_ITERS) and ins["calls"] == hr.CG_ITERS + 1
            assert os.path.exists(os.path.join(out, "asm", loop + ".diff")) and os.path.exists(os.path.join(out, "asm", loop + ".aligned.diff"))
        assert icalls == [f"{lp}.L1.{m}" for lp in LOOPS for m in ("none", "fast")]
        assert not os.path.exists(os.path.join(out, sw.PARTIAL_NAME)), "the partial file goes once forwardt.json is written"
        # the pairs: 3 per cell, 4 where NOVEC is timed, in the stored cell order, with the argument list of the loop
        assert len(calls) == 2 * (3 + 4 + 3 + 4 + 4 + 3)
        for a, b, args in calls:
            loop = b.split(".")[0]
            assert len(args) == (3 if loop == "t06_offset" else 2) and (args[2:] == [0] or loop != "t06_offset")
        first_cell = [(a, b) for a, b, args in calls[:3]]
        assert first_cell == [("t01_sum_size.none", "t01_sum_size.fast"), ("t01_sum_size.none_a64", "t01_sum_size.fast_a64"),
                              ("t01_sum_size.none", "t01_sum_size.none_copy")]
        assert calls[3][:2] == ("t01_sum_size.none", "t01_sum_size.fast"), "t01 has no NOVEC pair: the next call is its L2 cell"
        assert calls[3][2][0] == doc["sizes"]["L2"]["n"]["t01_sum_size"]
        assert calls[6][:2] == ("t02_sum_n.none", "t02_sum_n.fast") and calls[9][:2] == ("t02_sum_n.none", "t02_sum_n.novec")
        assert "[done]" in text and "[time] t06_offset.L2" in text and "[build] t02_sum_n: word lost" in text
        assert "WARNING" not in text


def test_the_a_a_copy_keeps_the_mode_of_the_none_binary_and_calibration_uses_the_none_binary_on_the_pinned_cpu():
    def norm(path):
        return os.path.normcase(os.path.abspath(path))
    with tempfile.TemporaryDirectory() as tmp:
        _, _, calls, _, out, build = run_job(tmp)
        doc = load_json(os.path.join(out, sw.RESULT_NAME))
        # A1: the copy is made with copymode(NONE binary, copy), once per loop, and is timed with the mode it has then
        # (a copyfile alone gives a file that is not executable on Linux, and the A/A pair dies on the first process)
        want_modes = [(norm(os.path.join(build, f"{lp}.none")), norm(os.path.join(build, f"{lp}.none_copy"))) for lp in LOOPS]
        assert [(norm(a), norm(b)) for a, b in calls.copymode] == want_modes
        assert len(calls.aa_modes) == 12 and all(copy_mode == none_mode for copy_mode, none_mode in calls.aa_modes), calls.aa_modes
        if os.name == "posix":
            assert all(copy_mode & 0o111 == 0o111 for copy_mode, _ in calls.aa_modes), "the copy can be executed"
        # A5: calibrate runs the NONE binary of the loop, at the n of the cell, on the pinned CPU, once per cell, in cell order
        want_cal = [(norm(os.path.join(build, f"{lp}.none")), lp, doc["sizes"][size]["n"][lp], "2")
                    for lp in LOOPS for size in ("L1", "L2")]
        assert [(norm(b), lp, n, cpu) for b, lp, n, cpu in calls.calibrate] == want_cal
        assert doc["pinned_cpu"] == "2" and calls.pair_cpu == ["2"] * len(calls) and len(calls) == 42


def test_the_timed_loop_order_is_loop_by_loop_with_l1_before_l2():
    with tempfile.TemporaryDirectory() as tmp:
        _, _, calls, _, out, _ = run_job(tmp)
        doc = load_json(os.path.join(out, sw.RESULT_NAME))
        sizes = doc["sizes"]
        seen = []
        for a, b, args in calls:
            loop = b.split(".")[0]
            size = "L1" if args[0] == sizes["L1"]["n"][loop] else "L2"
            if not seen or seen[-1] != f"{loop}.{size}":
                seen.append(f"{loop}.{size}")
        assert seen == doc["timing_order"]


def test_a_run_outside_actions_gets_a_local_id_and_no_commit():
    with tempfile.TemporaryDirectory() as tmp:
        _, _, _, _, out, _ = run_job(tmp, environment={})
        run = load_json(os.path.join(out, sw.RESULT_NAME))["run"]
        assert run["id"].startswith("local-") and run["commit"] is None and run["workflow_run_url"] is None
        assert run["attempt"] == 1, "outside Actions there is no attempt variable: the attempt is 1"


def test_the_attempt_of_the_run_is_stored_in_the_file_and_in_the_partial_header_and_names_its_url():
    base = "https://github.com/owner/repo/actions/runs/39000000000"
    for attempt, want_url in ((None, base), ("1", base), ("2", base + "/attempts/2"), ("13", base + "/attempts/13")):
        environment = dict(ACTIONS) if attempt is None else dict(ACTIONS, GITHUB_RUN_ATTEMPT=attempt)
        want = 1 if attempt is None else int(attempt)
        with tempfile.TemporaryDirectory() as tmp:
            _, text, _, _, out, _ = run_job(tmp, environment=environment)
            doc = load_json(os.path.join(out, sw.RESULT_NAME))
            assert doc["run"]["attempt"] == want and type(doc["run"]["attempt"]) is int
            assert doc["run"]["workflow_run_url"] == want_url and doc["run"]["id"] == "39000000000"
            assert valid(doc) == [], valid(doc)
            assert ("attempt %d of the run" % want in text) == (want > 1), "a second attempt says so on the log, the first does not"
        # the partial header (the file a job that stops leaves) carries the same run block
        with tempfile.TemporaryDirectory() as tmp:
            out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
            with faked(break_at="t02_sum_n.L1"), env(**environment), contextlib.redirect_stdout(io.StringIO()):
                try:
                    sw.main(["--job", "3", "--out", out, "--build", build])
                except SystemExit:
                    pass
            head = json.loads(read_text(os.path.join(out, sw.PARTIAL_NAME)).splitlines()[0])
            assert head["kind"] == "forwardt-partial" and head["run"]["attempt"] == want
            assert head["run"]["workflow_run_url"] == want_url
    # a local run has no run id: attempt 1 and no address (an attempt variable alone gives no run to point at)
    with tempfile.TemporaryDirectory() as tmp:
        _, _, _, _, out, _ = run_job(tmp, environment={"GITHUB_RUN_ATTEMPT": "3"})
        run = load_json(os.path.join(out, sw.RESULT_NAME))["run"]
        assert run["attempt"] == 3 and run["workflow_run_url"] is None and run["id"].startswith("local-")


def test_workflow_run_url_adds_the_attempt_only_from_the_second_attempt():
    assert sw.workflow_run_url("https://github.com", "o/r", "77", 1) == "https://github.com/o/r/actions/runs/77"
    assert sw.workflow_run_url("https://github.com", "o/r", "77", 2) == "https://github.com/o/r/actions/runs/77/attempts/2"
    assert sw.workflow_run_url("https://github.com", "o/r", "77", 10) == "https://github.com/o/r/actions/runs/77/attempts/10"
    assert sw.workflow_run_url("https://github.com", "o/r", None, 2) is None
    assert sw.workflow_run_url("https://github.com", "o/r", "", 1) is None


def test_the_attempt_variable_is_read_strictly_and_a_value_that_is_not_a_positive_integer_stops_the_job():
    assert sw.run_attempt({}) == 1 and sw.run_attempt({"GITHUB_RUN_ATTEMPT": "1"}) == 1
    assert sw.run_attempt({"GITHUB_RUN_ATTEMPT": "2"}) == 2 and sw.run_attempt({"GITHUB_RUN_ATTEMPT": "120"}) == 120
    bad_values = ("abc", "", "0", "-1", "1.5", " 2", "2 ", "2\n", "+2", "02", "0x2", "1e0", "\u0663", "1\u0663")   # the last two: an Arabic-Indic 3, and a 1 followed by one (int() would read that as 13)
    for bad in bad_values:
        try:
            sw.run_attempt({"GITHUB_RUN_ATTEMPT": bad})
        except SystemExit as e:
            assert "GITHUB_RUN_ATTEMPT" in str(e) and repr(bad) in str(e), str(e)
        else:
            raise AssertionError(f"GITHUB_RUN_ATTEMPT={bad!r} must stop the job, not be read as 1")
    # through the whole job: nothing is created, nothing is built, nothing is timed
    for bad in bad_values:
        with tempfile.TemporaryDirectory() as tmp:
            out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
            with faked(crit_reps=4) as (calls, icalls), env(**dict(ACTIONS, GITHUB_RUN_ATTEMPT=bad)), \
                    contextlib.redirect_stdout(io.StringIO()) as buf:
                try:
                    sw.main(["--job", "1", "--out", out, "--build", build])
                except SystemExit as e:
                    assert "GITHUB_RUN_ATTEMPT" in str(e), str(e)
                else:
                    raise AssertionError(f"GITHUB_RUN_ATTEMPT={bad!r} must stop the sweep")
            assert calls == [] and icalls == [] and buf.getvalue() == ""
            assert not os.path.exists(out) and not os.path.exists(build), "nothing is created before the refusal"


def test_validate_doc_requires_the_attempt_as_an_integer_of_one_or_more():
    doc = good_doc()
    assert doc["run"]["attempt"] == 1 and valid(doc) == []
    ok = _mut(doc, lambda d: d["run"].__setitem__("attempt", 2))
    assert valid(ok) == [], "a second attempt is a valid file; the analysis decides what to do with it"
    for bad in (0, -1, "1", True, False, 1.5, 2.0, None, [], [1]):
        problems = valid(_mut(doc, lambda d: d["run"].__setitem__("attempt", bad)))
        assert any("run.attempt" in p for p in problems), (bad, problems)
    missing = valid(_mut(doc, lambda d: d["run"].pop("attempt")))
    assert any("run.attempt" in p for p in missing), missing
    assert not any("run.attempt" in p for p in valid(doc))


def test_a_file_made_with_other_repetitions_than_the_criteria_is_marked_as_smoke():
    with tempfile.TemporaryDirectory() as tmp:
        _, text, _, _, out, _ = run_job(tmp, extra=["--reps", "4"], crit_reps=40)
        doc = load_json(os.path.join(out, sw.RESULT_NAME))
        assert doc["smoke"] is True and doc["reps_per_side"] == 4
        assert valid(doc, crit=40) == []
        assert "smoke file" in text and "WARNING" in text
        doc["smoke"] = False
        assert any("smoke is False with 4 repetitions" in p for p in valid(doc, crit=40))
    with tempfile.TemporaryDirectory() as tmp:
        _, text, _, _, out, _ = run_job(tmp, extra=["--reps", "4"], crit_reps=4)
        assert load_json(os.path.join(out, sw.RESULT_NAME))["smoke"] is False, "equal to the criteria number is a measurement"
        assert "smoke" not in text.lower()
    assert sw.reps_per_side() == 40, "the real criteria file says 40"


def test_reps_zero_or_negative_is_refused_before_anything_is_built_and_is_not_read_as_unset():
    for bad in ("0", "-3"):
        with tempfile.TemporaryDirectory() as tmp:
            out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
            with faked(crit_reps=40) as (calls, icalls), env(**ACTIONS), contextlib.redirect_stdout(io.StringIO()) as buf:
                try:
                    sw.main(["--job", "1", "--out", out, "--build", build, "--reps", bad])
                except SystemExit as e:
                    assert "--reps must be at least 1" in str(e) and f"got {bad}" in str(e), str(e)
                else:
                    raise AssertionError(f"--reps {bad} must stop the job")
            assert calls == [] and icalls == [] and buf.getvalue() == ""
            assert not os.path.exists(out) and not os.path.exists(build), "nothing is created before the refusal"
    # no --reps at all is the criteria number (a measurement), and an explicit 1 is a smoke file
    with tempfile.TemporaryDirectory() as tmp:
        _, _, _, _, out, _ = run_job(tmp, crit_reps=4)
        assert load_json(os.path.join(out, sw.RESULT_NAME))["reps_per_side"] == 4
    with tempfile.TemporaryDirectory() as tmp:
        _, _, _, _, out, _ = run_job(tmp, extra=["--reps", "1"], crit_reps=4)
        doc = load_json(os.path.join(out, sw.RESULT_NAME))
        assert doc["reps_per_side"] == 1 and doc["smoke"] is True


def test_no_cachegrind_leaves_the_counts_empty_with_a_note():
    with tempfile.TemporaryDirectory() as tmp:
        _, _, _, icalls, out, _ = run_job(tmp, extra=["--no-cachegrind"])
        doc = load_json(os.path.join(out, sw.RESULT_NAME))
        assert icalls == [] and valid(doc) == []
        for loop in LOOPS:
            ins = doc["loops"][loop]["instr"]
            assert ins["none"] is None and ins["fast"] is None and ins["ratio"] is None and "no-cachegrind" in ins["note"]


def test_an_aligned_word_that_differs_and_an_unexpected_compiler_are_warned_about_and_stored():
    with tempfile.TemporaryDirectory() as tmp:
        _, text, _, _, out, _ = run_job(tmp, a64={"t01_sum_size": {"fast_a64": (False, None, None)}},
                                        clang="Ubuntu clang version 18.1.8 (1)")
        doc = load_json(os.path.join(out, sw.RESULT_NAME))
        w = doc["loops"]["t01_sum_size"]["words"]
        assert w["compiled"]["word"] == "kept" and w["aligned"]["word"] == "lost" and w["agree"] is False
        assert valid(doc) == [], "the sweep records the disagreement; the analysis calls it a file problem"
        assert "t01_sum_size: the word of the aligned pair (lost) differs" in text and "not clang 18.1.3" in text


def test_a_checksum_mismatch_stops_the_job_and_keeps_every_cell_timed_so_far():
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        with faked(break_at="t02_sum_n.L1"), env(**ACTIONS), contextlib.redirect_stdout(io.StringIO()):
            try:
                sw.main(["--job", "3", "--out", out, "--build", build])
            except SystemExit as e:
                assert "different checksums" in str(e) and "t02_sum_n.L1" in str(e)
            else:
                raise AssertionError("a checksum mismatch must stop the job")
        assert not os.path.exists(os.path.join(out, sw.RESULT_NAME))
        recs = [json.loads(x) for x in read_text(os.path.join(out, sw.PARTIAL_NAME)).splitlines() if x.strip()]
        head = recs[0]
        assert head["kind"] == "forwardt-partial" and head["cells_expected"] == 12 and head["smoke"] is False
        assert head["plan_sha256"] == sw.plan_sha256() and head["run"]["job"] == "3" and head["reps_per_side"] == 4
        assert head["timing_order"] == [f"{lp}.{s}" for lp in LOOPS for s in ("L1", "L2")]
        assert list(recs[1]["builds"]) == list(LOOPS) and "cells" not in recs[1]["builds"]["t01_sum_size"]
        cells = [r["cell"] for r in recs if "cell" in r]
        assert [f"{c['loop']}.{c['size']}" for c in cells] == ["t01_sum_size.L1", "t01_sum_size.L2", "t02_sum_n.L1"]
        assert cells[-1]["checksum_match"] is False and cells[0]["checksum_match"] is True
        assert [r["starting"] for r in recs if "starting" in r] == ["t01_sum_size.L1", "t01_sum_size.L2", "t02_sum_n.L1"]
        assert set(recs[-1]) == {"stopped"} and recs[-1]["stopped"]["at"] == "t02_sum_n.L1"
        assert "different checksums" in recs[-1]["stopped"]["reason"]


def test_a_failed_timed_process_stops_the_job_with_a_plain_message_and_keeps_the_partial_file():
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        with faked(raise_at="t03_scale_size.L1"), env(**ACTIONS), contextlib.redirect_stdout(io.StringIO()):
            try:
                sw.main(["--job", "3", "--out", out, "--build", build])
            except SystemExit as e:
                assert "a timed process failed" in str(e) and "exited 1" in str(e)
            else:
                raise AssertionError("a failed kernel process must stop the job")
        recs = [json.loads(x) for x in read_text(os.path.join(out, sw.PARTIAL_NAME)).splitlines() if x.strip()]
        assert len([r for r in recs if "cell" in r]) == 4, "t01 and t02 at both sizes"
        assert recs[-2] == {"starting": "t03_scale_size.L1"} and recs[-1]["stopped"]["at"] == "t03_scale_size.L1"
        assert not os.path.exists(os.path.join(out, sw.RESULT_NAME))


def test_a_missing_binary_or_a_copy_that_differs_stops_the_job_before_anything_is_timed():
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        with faked(missing="fast_a64") as (calls, _), env(**ACTIONS), contextlib.redirect_stdout(io.StringIO()):
            try:
                sw.main(["--job", "1", "--out", out, "--build", build])
            except SystemExit as e:
                assert "fast_a64 binary of t01_sum_size is missing" in str(e)
            else:
                raise AssertionError("a missing binary must stop the job")
        assert calls == [] and not os.path.exists(os.path.join(out, sw.PARTIAL_NAME))
    original = hr.sha256
    with tempfile.TemporaryDirectory() as tmp:
        out, build = os.path.join(tmp, "out"), os.path.join(tmp, "build")
        with faked() as (calls, _), env(**ACTIONS), contextlib.redirect_stdout(io.StringIO()):
            with patched((hr, "sha256", lambda p: original(p) if not p.endswith("none_copy") else "0" * 64)):
                try:
                    sw.main(["--job", "1", "--out", out, "--build", build])
                except SystemExit as e:
                    assert "not byte-identical" in str(e)
                else:
                    raise AssertionError("an A/A copy that differs must stop the job")
        assert calls == []


def test_the_abba_check_refuses_every_order_that_is_not_abab_reversed_each_repetition():
    assert sw._abba("ABBAABBA", 4) and sw._abba("AB", 1) and sw._abba("ABBA", 2)
    for order, reps in (("ABABABAB", 4),      # right length and counts, no reversal
                        ("BAABBAAB", 4),      # starts with B
                        ("ABBAABAB", 4),      # reversal lost in the last repetition
                        ("ABBAABBB", 4),      # wrong counts
                        ("ABBA", 4),          # too short
                        ("ABBAABBAAB", 4),    # too long
                        ("abbaabba", 4), ("", 4), (None, 4), (["A", "B"], 1),
                        ("ABBAABBA", 3)):
        assert not sw._abba(order, reps), (order, reps)


def test_append_partial_writes_one_json_line_per_call():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "p.jsonl")
        sw.append_partial(path, {"a": 1})
        sw.append_partial(path, {"b": [1, 2]})
        lines = read_text(path).splitlines()
        assert [json.loads(x) for x in lines] == [{"a": 1}, {"b": [1, 2]}]


# ---------------------------------------------------------------- the schema check

def _mut(doc, fn):
    d = copy.deepcopy(doc)
    fn(d)
    return d


def _first_pair(d, loop="t02_sum_n", size="L1", col="compiled"):
    return d["loops"][loop]["cells"][size]["pairs"][col]


def _both_sides(pair, value):
    """Both sides of a pair print `value` and the flag stays true: a pair that is equal to itself, not to the cell."""
    pair["a_checksums"], pair["b_checksums"] = [value], [value]


def test_validate_doc_accepts_a_good_file_and_names_what_is_wrong_in_a_bad_one():
    doc = good_doc()
    assert valid(doc) == []
    assert sw.validate_doc(doc, reps=5) == ["reps_per_side is 4, not 5"] or any("not 5" in p for p in sw.validate_doc(doc, reps=5))

    def swap_order(d):
        _first_pair(d)["order"] = "BAAB" * 1
    mutations = {
        "kind/schema_version": lambda d: d.__setitem__("kind", "dsweep"),
        "plan_sha256 is not a sha256": lambda d: d.__setitem__("plan_sha256", "zz"),
        "criteria_sha256": lambda d: d.__setitem__("criteria_sha256", None),
        "code_sha256 does not have exactly": lambda d: d["code_sha256"].pop("harness/run.py"),
        "neither a sha256 nor 'missing'": lambda d: d["code_sha256"].__setitem__("harness/run.py", "abc"),
        "reps_per_side is not a positive": lambda d: d.__setitem__("reps_per_side", 0),
        "smoke is True with 4 repetitions": lambda d: d.__setitem__("smoke", True),
        "smoke is not a boolean": lambda d: d.__setitem__("smoke", "no"),
        "pinned_cpu": lambda d: d.__setitem__("pinned_cpu", 1),
        "run.id": lambda d: d["run"].__setitem__("id", ""),
        "run.runner.cpu_model": lambda d: d["run"]["runner"].__setitem__("cpu_model", ""),
        "run.runner.arch": lambda d: d["run"]["runner"].pop("arch"),
        "run.toolchain.clang": lambda d: d["run"]["toolchain"].__setitem__("clang", None),
        "sizes differ": lambda d: d["sizes"]["L1"]["n"].__setitem__("t01_sum_size", d["sizes"]["L1"]["n"]["t01_sum_size"] + 1),
        "machine.cache_bytes": lambda d: d["machine"]["cache_bytes"].pop("l2"),
        "loop_order": lambda d: d.__setitem__("loop_order", list(reversed(d["loop_order"]))),
        "timing_order": lambda d: d["timing_order"].reverse(),
        "t02_sum_n: words differ": lambda d: d["loops"]["t02_sum_n"]["words"]["compiled"].__setitem__("word", "kept"),
        "t02_sum_n: novec_timed": lambda d: d["loops"]["t02_sum_n"].__setitem__("novec_timed", False),
        "t06_offset: off is wrong": lambda d: d["loops"]["t06_offset"].__setitem__("off", None),
        "t01_sum_size: bytes_per_element": lambda d: d["loops"]["t01_sum_size"].__setitem__("bytes_per_element", 8),
        "t01_sum_size: builds does not have": lambda d: d["loops"]["t01_sum_size"]["builds"].pop("novec"),
        "t01_sum_size.none: binary_sha256": lambda d: d["loops"]["t01_sum_size"]["builds"]["none"].__setitem__("binary_sha256", "x"),
        "t01_sum_size: instr": lambda d: d["loops"]["t01_sum_size"].pop("instr"),
        "t02_sum_n.L1: loop, size or n": lambda d: d["loops"]["t02_sum_n"]["cells"]["L1"].__setitem__("n", 5),
        "t02_sum_n.L1: working_set_bytes or an argument list": lambda d: d["loops"]["t02_sum_n"]["cells"]["L1"].__setitem__("timed_args", [1, 2]),
        "t02_sum_n.L1: iters": lambda d: d["loops"]["t02_sum_n"]["cells"]["L1"].__setitem__("iters", 0),
        "t02_sum_n.L1: checksum_match": lambda d: d["loops"]["t02_sum_n"]["cells"]["L1"].__setitem__("checksum_match", False),
        "t02_sum_n.L1.compiled: builds are not": lambda d: _first_pair(d).__setitem__("b_build", "novec"),
        "t02_sum_n.L1.compiled: the stored hashes": lambda d: _first_pair(d).__setitem__("b_binary_sha256", "0" * 64),
        "t02_sum_n.L1.aa: the stored hashes": lambda d: _first_pair(d, col="aa").__setitem__("b_binary_sha256", "0" * 64),
        "t02_sum_n.L1.compiled: the sides do not hold 4": lambda d: _first_pair(d)["a_ns"].pop(),
        "t02_sum_n.L1.compiled: the order is not ABBA": swap_order,
        # right length, right counts of A and B, wrong pattern
        "t02_sum_n.L1.aligned: the order is not ABBA": lambda d: _first_pair(d, col="aligned").__setitem__("order", "ABABABAB"),
        "t02_sum_n.L1.aa: the order is not ABBA": lambda d: _first_pair(d, col="aa").__setitem__("order", "BAABBAAB"),
        "t04_scale_n.L2.compiled: the order is not ABBA": lambda d: _first_pair(d, "t04_scale_n", "L2").__setitem__("order", "ABBAABAB"),
        "t05_fill_n.L1.compiled: the order is not ABBA": lambda d: _first_pair(d, "t05_fill_n", "L1").__setitem__("order", "ABBAABBB"),
        "t06_offset.L2.compiled: the order is not ABBA": lambda d: _first_pair(d, "t06_offset", "L2").__setitem__("order", None),
        "t02_sum_n.L1.compiled: the two sides printed different": lambda d: _first_pair(d).__setitem__("checksum_match", False),
        # the stored checksum VALUES (plan rule 7), with every flag left true
        "t02_sum_n.L1.compiled: the checksums stored for the two sides": lambda d: _first_pair(d).__setitem__("b_checksums", ["0000000000000001"]),
        "t02_sum_n.L1.aligned: the checksums stored for the two sides": lambda d: _first_pair(d, col="aligned").__setitem__("a_checksums", ["0000000000000002"]),
        "t02_sum_n.L1.aa: the checksums stored for the two sides": lambda d: _both_sides(_first_pair(d, col="aa"), "1111111111111111"),
        "t02_sum_n.L1.novec: the checksums stored for the two sides": lambda d: _both_sides(_first_pair(d, col="novec"), "2222222222222222"),
        "t04_scale_n.L2.compiled: the checksums stored for the two sides": lambda d: _first_pair(d, "t04_scale_n", "L2").__setitem__("a_checksums", [CK, "0000000000000003"]),
        "t01_sum_size.L1.compiled: the checksums stored for the two sides": lambda d: _first_pair(d, "t01_sum_size", "L1").__setitem__("b_checksums", []),
        "t06_offset.L1.compiled: the checksums stored for the two sides": lambda d: _first_pair(d, "t06_offset", "L1").__setitem__("a_checksums", [CK, CK]),
        "t02_sum_n.L1: checksum is not a 16-hex string": lambda d: d["loops"]["t02_sum_n"]["cells"]["L1"].__setitem__("checksum", None),
        "t03_scale_size.L2: checksum is not a 16-hex string": lambda d: d["loops"]["t03_scale_size"]["cells"]["L2"].__setitem__("checksum", "zz"),
        "t04_scale_n.L1: checksum is not a 16-hex string": lambda d: d["loops"]["t04_scale_n"]["cells"]["L1"].__setitem__("checksum", CK.upper()),
        "t05_fill_n.L1: checksum is not a 16-hex string": lambda d: d["loops"]["t05_fill_n"]["cells"]["L1"].__setitem__("checksum", CK[:15]),
        "t02_sum_n.L1.compiled: ratio or ci95": lambda d: _first_pair(d).__setitem__("ci95", [1.0]),
        "t01_sum_size.L1.novec: timed although": lambda d: d["loops"]["t01_sum_size"]["cells"]["L1"]["pairs"].__setitem__("novec", _first_pair(d, "t02_sum_n")),
        "t02_sum_n.L1.novec: missing": lambda d: d["loops"]["t02_sum_n"]["cells"]["L1"]["pairs"].__setitem__("novec", None),
        "pairs does not have exactly": lambda d: d["loops"]["t03_scale_size"]["cells"]["L2"]["pairs"].pop("aa"),
        "t04_scale_n: cells does not hold": lambda d: d["loops"]["t04_scale_n"]["cells"].pop("L2"),
        "loops does not hold the six loops": lambda d: d["loops"].pop("t05_fill_n"),
    }
    for want, fn in mutations.items():
        problems = valid(_mut(doc, fn))
        assert any(want in p for p in problems), (want, problems)
    assert sw.validate_doc([], reps=4) == ["not a JSON object"]


# ---------------------------------------------------------------- hashes and constants

def test_the_plan_the_criteria_and_the_code_files_are_hashed_with_line_endings_read_as_lf():
    with open(sw.PLAN_FILE, "rb") as f:
        raw = f.read()
    assert sw.plan_sha256() == hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    with open(os.path.join(REPO, "harness", "criteria-v3.json"), "rb") as f:
        assert sw.criteria_sha256() == hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    with tempfile.TemporaryDirectory() as tmp:
        lf, crlf = os.path.join(tmp, "lf.md"), os.path.join(tmp, "crlf.md")
        with open(lf, "wb") as f:
            f.write(b"one\ntwo\n")
        with open(crlf, "wb") as f:
            f.write(b"one\r\ntwo\r\n")
        assert sw.plan_sha256(lf) == sw.plan_sha256(crlf) == hashlib.sha256(b"one\ntwo\n").hexdigest()
    code = sw.code_sha256()
    assert set(code) == set(sw.CODE_FILES) and len(sw.CODE_FILES) == len(set(sw.CODE_FILES))
    for rel, h in code.items():
        assert (h == "missing") == (not os.path.exists(os.path.join(REPO, rel))), rel
        assert h == "missing" or re.match(r"^[0-9a-f]{64}$", h)
    assert code["forwardt/sweep.py"] != "missing" and code["kernels/common.hpp"] != "missing"


def test_code_files_cover_the_sources_the_sweep_and_the_harness_modules_it_imports():
    assert all("\\" not in c and not c.startswith("/") for c in sw.CODE_FILES)
    missing = [c for c in sw.CODE_FILES if not os.path.exists(os.path.join(REPO, c)) and c != "forwardt/analyze.py"]
    assert missing == [], missing
    for loop in LOOPS:
        assert f"forwardt/kernels/{loop}.cpp" in sw.CODE_FILES
    assert "forwardt/sweep.py" in sw.CODE_FILES and "forwardt/analyze.py" in sw.CODE_FILES and "kernels/common.hpp" in sw.CODE_FILES
    imported = re.findall(r"^import (\w+)(?: as \w+)?\s+# noqa", read_text(os.path.join(FWT, "sweep.py")), re.M)
    harness_mods = [m for m in imported if os.path.exists(os.path.join(REPO, "harness", m + ".py"))]
    assert sorted(harness_mods) == sorted(["asm", "cachegrind", "placement", "pool", "remarks", "run", "stats"])
    for m in harness_mods:
        assert f"harness/{m}.py" in sw.CODE_FILES, m
    # the modules those modules import in turn (harness/run.py: programs, schema, verdict; harness/pool.py: verdict) are
    # hashed too: the transitive closure of the harness imports, read from the files, is inside CODE_FILES
    closure, todo = set(), list(harness_mods)
    while todo:
        m = todo.pop()
        if m in closure:
            continue
        closure.add(m)
        src = read_text(os.path.join(REPO, "harness", m + ".py"))
        todo += [x for x in re.findall(r"^import (\w+)(?: as \w+)?\s+# noqa", src, re.M)
                 if os.path.exists(os.path.join(REPO, "harness", x + ".py"))]
    assert {"programs", "schema", "verdict"} <= closure, closure   # the reason for the three entries below
    for m in sorted(closure):
        assert f"harness/{m}.py" in sw.CODE_FILES, m
    harness_listed = sorted(c for c in sw.CODE_FILES if c.startswith("harness/"))
    assert harness_listed == sorted(f"harness/{m}.py" for m in closure), harness_listed
    assert len(sw.CODE_FILES) == 19, len(sw.CODE_FILES)   # 2 forwardt + 6 sources + common.hpp + 10 harness modules
    assert "forwardt/PLAN.md" not in sw.CODE_FILES, "the plan has its own hash field"


def test_the_builds_pairs_and_columns_are_the_ones_the_plan_names():
    assert set(hr.BUILD_FLAGS) == set(sw.MODES) and len(sw.MODES) == 5
    assert sw.COLUMNS == ("compiled", "aligned", "aa", "novec")
    assert sw.PAIR_BUILDS == {"compiled": ("none", "fast"), "aligned": ("none_a64", "fast_a64"),
                              "aa": ("none", "none_copy"), "novec": ("none", "novec")}
    assert sw.NOVEC_LOOPS == ("t02_sum_n", "t04_scale_n", "t05_fill_n", "t06_offset")
    assert sw.CONTROLS == ("t01_sum_size", "t03_scale_size") and set(sw.CONTROLS).isdisjoint(sw.NOVEC_LOOPS)
    assert sw.LOOPS == ("t01_sum_size", "t02_sum_n", "t03_scale_size", "t04_scale_n", "t05_fill_n", "t06_offset")
    assert sw.SIZES == ("L1", "L2") and sw.CELLS_EXPECTED == 12
    assert sw.RESULT_NAME == "forwardt.json" and sw.PARTIAL_NAME == "forwardt.partial.jsonl"
    assert hr.CG_ITERS == 20 and hr.TARGET_NS == 75e6


def test_the_stored_samples_are_ns_per_kernel_call_as_the_docstring_says():
    assert "mean ns per kernel call of one process" in sw.__doc__ and "a process of a cell lasts about" in sw.__doc__
    # the unit comes from the header the kernels print through: the timed total divided by the iterations
    assert "double(ns_total) / double(iters)" in read_text(os.path.join(REPO, "kernels", "common.hpp"))
    # the sweep stores what the harness returns, unchanged: a sample is not scaled by the iteration count
    pr = {"a_ns": [11.5, 12.5], "b_ns": [13.5, 14.5], "order": "ABBA", "a_checksums": [CK], "b_checksums": [CK],
          "checksum_match": True}
    shas = {"none": "1" * 64, "fast": "2" * 64}
    rec = sw.pair_record("none", "fast", shas, 2, pr, sw.stats.summarize)
    assert rec["a_ns"] == [11.5, 12.5] and rec["b_ns"] == [13.5, 14.5]
    # and the iteration count is chosen so that iters x (ns per call) is the target of a process
    with patched((hr, "run_bin", lambda binary, args, cpu: (123456.0, CK))):
        iters, one = sw.calibrate("bin", "t01_sum_size", 4096, "2")
    assert abs(iters * one - hr.TARGET_NS) <= one / 2 and iters > 1


def test_the_docstring_names_every_key_the_file_has():
    doc = good_doc()
    text = sw.__doc__
    keys = set(doc) | set(doc["run"]) | set(doc["run"]["runner"]) | set(doc["machine"]) | set(doc["sizes"]["L1"])
    loop = doc["loops"]["t02_sum_n"]
    keys |= set(loop) | set(loop["builds"]["none"]) | set(loop["builds"]["none"]["vectorization"]) | set(loop["words"]) | set(loop["words"]["compiled"])
    keys |= set(loop["instr"]) | set(loop["cells"]["L1"]) | set(loop["cells"]["L1"]["pairs"]["compiled"])
    keys |= set(loop["builds"]["none"]["hot_loop"])
    undocumented = sorted(k for k in keys if f'"{k}"' not in text and f"{k}:" not in text)
    assert undocumented == [], f"keys the file has and the module docstring does not name: {undocumented}"


# ---------------------------------------------------------------- the workflow

def test_workflow_structure():
    import yaml
    with open(os.path.join(REPO, ".github", "workflows", "forwardt.yml"), encoding="utf-8") as f:
        text = f.read()
    wf = yaml.safe_load(text)
    assert wf["name"] == "forwardt"
    on = wf.get("on") if "on" in wf else wf.get(True)
    assert list(on) == ["workflow_dispatch"]
    inputs = on["workflow_dispatch"]["inputs"]
    assert inputs["runner"]["default"] == "ubuntu-24.04" and inputs["runner"]["options"] == ["ubuntu-24.04", "ubuntu-24.04-arm"]
    assert json.loads(inputs["jobs"]["default"]) == [1, 2, 3, 4, 5, 6]
    assert inputs["reps"]["default"] == "" and "SMOKE" in inputs["reps"]["description"]
    assert wf["permissions"] == {"contents": "read"}
    assert list(wf["jobs"]) == ["sweep"], "no pool job: the analysis and its runs.json belong to forwardt/analyze.py"
    sweep = wf["jobs"]["sweep"]
    assert set(inputs) == {"runner", "jobs", "reps", "time_limit"}, sorted(inputs)
    limit = inputs["time_limit"]
    assert limit["type"] == "string" and limit["default"] == "45" and "minutes" in limit["description"], limit
    assert json.loads(limit["default"]) == 45, "the default is something fromJSON turns into the number of minutes"
    assert sweep["runs-on"] == "${{ inputs.runner }}"
    assert sweep["timeout-minutes"] == "${{ fromJSON(inputs.time_limit) }}", "the job's timeout is the input, not a literal"
    assert sweep["strategy"]["fail-fast"] is False and "fromJSON(inputs.jobs)" in sweep["strategy"]["matrix"]["job"]
    steps = sweep["steps"]
    run_idx = next(i for i, s in enumerate(steps) if "forwardt/sweep.py --job" in s.get("run", ""))
    up_idx = next(i for i, s in enumerate(steps) if "upload-artifact" in s.get("uses", ""))
    assert up_idx == run_idx + 1, "the upload comes right after the sweep"
    assert steps[up_idx]["if"] == "always()" and steps[up_idx]["with"]["path"] == "out/"
    assert steps[up_idx]["with"]["name"].startswith("forwardt-job-") and steps[up_idx]["with"]["name"].endswith("-j${{ matrix.job }}")
    run_step = steps[run_idx]
    assert "${{" not in run_step["run"] and run_step["env"] == {"JOB": "${{ matrix.job }}", "REPS": "${{ inputs.reps }}"}
    assert '--reps "$REPS"' in run_step["run"] and '--job "$JOB"' in run_step["run"]
    assert "--out out" in run_step["run"] and "--build build/forwardt" in run_step["run"]
    offline = [i for i, s in enumerate(steps) if "tests/test_forwardt.py" in s.get("run", "")]
    assert len(offline) == 1 and offline[0] < run_idx and "python3-yaml" in steps[offline[0]]["run"]
    assert "analyze.py" not in text.split("\njobs:")[1], "the analysis is not part of this workflow"
    for s in steps:
        if "uses" in s:
            assert re.match(r"^[\w.-]+/[\w.-]+@[0-9a-f]{40}$", s["uses"]), s["uses"]
    # what a substring check lets through: --reps passed empty, no checkout, jobs of one run that cannot be told apart,
    # a concurrency group that cancels the second x86-64 run, a pipe that hides the sweep's exit status
    guard = 'if [ -n "$REPS" ]; then ARGS+=(--reps "$REPS"); fi'
    run_lines = run_step["run"].splitlines()
    assert guard in run_lines and [ln for ln in run_lines if "--reps" in ln] == [guard.strip()], \
        "--reps is passed only when the input is not empty, and nowhere else"
    sweep_lines = [ln for ln in run_lines if "forwardt/sweep.py --job" in ln]
    assert len(sweep_lines) == 1 and "|" not in sweep_lines[0] and '"${ARGS[@]}"' in sweep_lines[0], sweep_lines
    # the sweep writes where the upload reads: the argument after --out, split as the shell splits the line, is the upload
    # path without its trailing slash (the substring "--out out" above also passes "--out outx" and "--out out/")
    tokens = shlex.split(sweep_lines[0])
    assert tokens.count("--out") == 1, tokens
    assert tokens[tokens.index("--out") + 1] == steps[up_idx]["with"]["path"].removesuffix("/"), tokens
    # nothing goes on after a failure, and the upload says exactly what it did when out/ is empty (a warning, not an
    # error and not silence), with no other option
    assert "continue-on-error" not in text, "a failed step must fail the job"
    assert steps[up_idx]["with"]["if-no-files-found"] == "warn", steps[up_idx]["with"]
    assert set(steps[up_idx]["with"]) == {"name", "path", "if-no-files-found"}, sorted(steps[up_idx]["with"])
    checkouts = [i for i, st in enumerate(steps) if str(st.get("uses", "")).startswith("actions/checkout@")]
    first_python = next(i for i, st in enumerate(steps) if "python3" in st.get("run", ""))
    assert len(checkouts) == 1 and checkouts[0] < first_python, "the repository is checked out before the first python3 step"
    cpu_step = next(st for st in steps if st.get("id") == "cpu")
    assert 'echo "slug=' in cpu_step["run"], "the step the artifact name reads the slug from writes it"
    assert "steps.cpu.outputs.slug" in steps[up_idx]["with"]["name"], "an artifact name carries the CPU it ran on"
    # the limit the job was started with is printed in the summary, right after the CPU line (a step of its own: the
    # CPU step is measure.yml's word for word)
    limit_step = steps[steps.index(cpu_step) + 1]
    assert limit_step["env"] == {"JOB": "${{ matrix.job }}", "TIME_LIMIT": "${{ inputs.time_limit }}"} and "${{" not in limit_step["run"]
    summary_lines = [ln for ln in limit_step["run"].splitlines() if 'time limit: $TIME_LIMIT minutes' in ln and ">> \"$GITHUB_STEP_SUMMARY\"" in ln]
    assert len(summary_lines) == 1 and summary_lines[0].startswith('echo "Job $JOB time limit: '), limit_step["run"]
    assert "concurrency" not in wf and "concurrency" not in sweep, "no concurrency group: it would cancel one of two runs"
    compared = compare_with_measure_yml(steps, wf["name"])
    assert compared is (os.environ.get("GITHUB_WORKFLOW") != wf["name"]), "made everywhere but inside the forwardt job"
    pinned = compare_pins_with_dsweep_yml(text, wf["name"])
    assert pinned is compared


MEASURE_STEPS_TAKEN_OVER = ("Runner CPU (read every result against this)",
                            "Install clang-18, libc++-18, valgrind and numpy (Ubuntu noble apt)")


def skipped_inside_the_forwardt_job(what, workflow_name, environ=None):
    """True (after saying so) inside a forwardt measurement job, that is when GITHUB_WORKFLOW is the name: of forwardt.yml."""
    environ = os.environ if environ is None else environ
    if environ.get("GITHUB_WORKFLOW") == workflow_name:
        print(f"note: {what} is skipped inside the {workflow_name!r} measurement job (GITHUB_WORKFLOW is this workflow's "
              "name); a local run and ci.yml make it")
        return True
    return False


def uses_lines(text):
    """Every `uses:` value of a workflow file as written, with the version comment (`sha # v4`)."""
    return [m.strip() for m in re.findall(r"^\s*(?:-\s+)?uses:\s*(.+?)\s*$", text, re.M)]


def compare_pins_with_dsweep_yml(forwardt_text, workflow_name, environ=None, dsweep_path=None):
    """The actions forwardt.yml uses are pinned to exactly the commits (and version comments) of dsweep.yml, whose runs
    returned 18 of 18 jobs: compared as strings, not by shape. Skipped inside the forwardt job like the measure.yml
    comparison (a dispatch branch may carry other sibling workflows). Returns True when it compared."""
    if skipped_inside_the_forwardt_job("the comparison of the action pins with dsweep.yml", workflow_name, environ):
        return False
    mine = uses_lines(forwardt_text)
    theirs = uses_lines(read_text(dsweep_path or os.path.join(REPO, ".github", "workflows", "dsweep.yml")))
    assert sorted(u.split("@")[0] for u in mine) == ["actions/checkout", "actions/upload-artifact"], mine
    assert all(u in theirs for u in mine), [u for u in mine if u not in theirs]
    return True


def compare_with_measure_yml(steps, workflow_name, environ=None, measure_path=None):
    """forwardt.yml takes two steps over from measure.yml word for word; this compares them with measure.yml as it
    stands in the checkout. Inside a forwardt measurement job (GITHUB_WORKFLOW is the name: of forwardt.yml) the
    comparison is skipped, and says so: the job's offline self-test runs before any timing, and a temporary dispatch
    branch can carry another measure.yml, which must not stop a run over a file the run does not use. Everywhere else
    (a local run, ci.yml) it is made. Returns True when it compared, False when it skipped."""
    import yaml
    if skipped_inside_the_forwardt_job("the comparison of the two shared steps with measure.yml", workflow_name, environ):
        return False
    with open(measure_path or os.path.join(REPO, ".github", "workflows", "measure.yml"), encoding="utf-8") as f:
        measure = yaml.safe_load(f)
    m_steps = {s.get("name"): s for s in measure["jobs"]["measure"]["steps"]}
    s_steps = {s.get("name"): s for s in steps}
    for name in MEASURE_STEPS_TAKEN_OVER:
        assert s_steps[name]["run"] == m_steps[name]["run"], name
    return True


def test_the_action_pins_are_compared_with_dsweep_yml_as_strings_and_skipped_only_inside_the_forwardt_job():
    text = read_text(os.path.join(REPO, ".github", "workflows", "forwardt.yml"))
    mine = uses_lines(text)
    assert [u.split("@")[0] for u in mine] == ["actions/checkout", "actions/upload-artifact"]
    assert all(re.match(r"^[\w./-]+@[0-9a-f]{40} # v[\d.]+$", u) for u in mine), mine   # the commit and its version comment
    assert compare_pins_with_dsweep_yml(text, "forwardt", environ={}) is True
    # a different but well-formed commit, a different version comment, a moved tag, a third action: all refused
    sha = re.search(r"@([0-9a-f]{40})", mine[0]).group(1)
    other = "0" * 40 if sha != "0" * 40 else "1" * 40
    for bad in (text.replace(sha, other), text.replace(mine[1].split(" # ")[1], "v4.6.3"),
                text.replace(mine[0], "actions/checkout@v4"),
                text + "      - uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4.3.0\n"):
        for environ in ({}, {"GITHUB_WORKFLOW": "ci"}):
            try:
                compare_pins_with_dsweep_yml(bad, "forwardt", environ=environ)
            except AssertionError:
                pass
            else:
                raise AssertionError("pins other than dsweep.yml's must fail the comparison")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            assert compare_pins_with_dsweep_yml(bad, "forwardt", environ={"GITHUB_WORKFLOW": "forwardt"}) is False
        assert "comparison of the action pins with dsweep.yml is skipped inside the 'forwardt' measurement job" in buf.getvalue()


def test_the_measure_yml_comparison_is_skipped_only_inside_the_forwardt_job():
    import yaml
    with open(os.path.join(REPO, ".github", "workflows", "forwardt.yml"), encoding="utf-8") as f:
        wf = yaml.safe_load(f)
    name = wf["name"]
    assert name == "forwardt"
    steps = copy.deepcopy(wf["jobs"]["sweep"]["steps"])
    changed = copy.deepcopy(steps)
    for st in changed:
        if st.get("name") == MEASURE_STEPS_TAKEN_OVER[0]:
            st["run"] += "echo changed\n"
    # unset, another workflow's name (ci.yml), or empty: the comparison is made, passes on the real steps, fails on a changed one
    for environ in ({}, {"GITHUB_WORKFLOW": "ci"}, {"GITHUB_WORKFLOW": ""}, {"GITHUB_WORKFLOW": "Forwardt"}):
        assert compare_with_measure_yml(steps, name, environ=environ) is True, environ
        try:
            compare_with_measure_yml(changed, name, environ=environ)
        except AssertionError as e:
            assert MEASURE_STEPS_TAKEN_OVER[0] in str(e)
        else:
            raise AssertionError(f"a changed shared step must fail the comparison when GITHUB_WORKFLOW is {environ}")
    # inside the forwardt job: skipped with a note, even for a changed step and for a measure.yml that is not there at all
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert compare_with_measure_yml(changed, name, environ={"GITHUB_WORKFLOW": name}) is False
        assert compare_with_measure_yml(changed, name, environ={"GITHUB_WORKFLOW": name},
                                        measure_path=os.path.join(REPO, "no", "such", "measure.yml")) is False
    assert buf.getvalue().count("is skipped inside the 'forwardt' measurement job") == 2, buf.getvalue()
    # the real environment is what test_workflow_structure passes: this process is not a forwardt job unless Actions says so
    with patched((os, "environ", {k: v for k, v in os.environ.items() if k != "GITHUB_WORKFLOW"})):
        assert compare_with_measure_yml(steps, name) is True
    with patched((os, "environ", dict(os.environ, GITHUB_WORKFLOW=name))), contextlib.redirect_stdout(io.StringIO()):
        assert compare_with_measure_yml(changed, name) is False


def run_all_tests():
    """`python3 tests/test_forwardt.py`: every test_* function in the order of the file (plain Python, no pytest)."""
    names = [n for n, f in list(globals().items()) if n.startswith("test_") and callable(f)]
    failed = []
    for n in names:
        try:
            globals()[n]()
            print(f"ok    {n}", flush=True)
        except Exception:
            failed.append(n)
            traceback.print_exc()
            print(f"FAIL  {n}", flush=True)
    print(f"{len(names) - len(failed)} passed, {len(failed)} failed" + (": " + ", ".join(failed) if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
