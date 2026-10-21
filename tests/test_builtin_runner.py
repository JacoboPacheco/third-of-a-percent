"""The tests have to run without pytest.

scripts/check.py runs the tests with its own small runner when pytest is not installed. The CI runner does not install
pytest (it installs playwright, numpy and pyyaml), and a reader who runs `python scripts/check.py` on a fresh machine may
not have it either. That runner imports every tests/test_*.py and calls each module-level test_* function with no
arguments. It never awaits or iterates what it calls, it does not look at classes, and it only looks at files that sit
directly in tests/. This file checks, without running a single test body, that nothing the runner would trip over or
silently skip gets in:

  1. a test module that cannot be imported when `import pytest` fails, or when only the packages CI installs are present;
  2. a test function that needs an argument (a fixture, or a parametrize decorator that is not guarded), is async, or is a
     generator; a name that pytest collects (a `Test*` class, a unittest.TestCase, `testfoo`, a partial, an imported test)
     and the runner skips;
  3. a use of pytest (`pytest.raises`, an alias, `from pytest import ...`, `importlib.import_module("pytest")`, `P = pytest`)
     outside an `if pytest is not None:` block, and any `import pytest` that is not the
     `try: import pytest / except ImportError: pytest = None` form;
  4. an `if pytest is not None:` block that defines tests but has no `else:` branch that defines them too, an else branch
     that does nothing, one whose tests never reach a function the guarded tests call, a guard inside a function, and a
     name that exists only inside the guard but is used outside it;
  5. a file pytest collects that the runner never imports (a file named `*_test.py`, a test file in a subfolder of tests/);
  6. a test module in which the runner would find no test at all;
  7. the two lists of test names, read from the files, from `pytest --collect-only` (when pytest is installed) and from the
     child process that imitates the runner, disagreeing with each other.

What this proves and what it does not: it checks the shape of the tests at import and collection time and that the runner
and pytest see the same test names. It does not run a test body without pytest. A fallback that checks less than the
parametrized test it stands for is only caught by the static rules in item 4. The pattern for a test that wants pytest's
parametrize is in tests/test_readme_numbers.py: `try: import pytest / except ImportError: pytest = None`, the parametrized
tests under `if pytest is not None:`, and one plain looping test under `else:`. A test decorated with something that adds
an argument (`@mock.patch`) is reported as needing arguments, whatever the decorator does; write that test with a context
manager instead.
"""
import ast
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# What .github/workflows/ci.yml installs with pip (test_ci_installs_exactly_the_packages_the_child_allows reads the file).
CI_PACKAGES = ("playwright", "numpy", "pyyaml")

# Run in a child process in which `import pytest` raises ImportError and in which only the standard library, pip and the
# packages above (with what they need) can be imported, like on the CI runner. It imports every test module the way
# scripts/check.py does (the same import path: scripts/ first, then check.py puts harness/ and tests/ in front, and neither
# the working directory nor the repository root is on it) and reads each name and signature; it calls nothing.
CHILD = r"""
import glob, importlib, importlib.abc, importlib.machinery, importlib.metadata as md, inspect, json, os, re, sys, unittest
sys.modules["pytest"] = None
sys.modules["_pytest"] = None
repo = sys.argv[1]
roots = sys.argv[2].split(",")


def canon(s):
    return re.sub(r"[-_.]+", "-", s).lower()


# the top-level names the CI runner can import: the packages above and what they require (extras left out)
closure, todo = set(), [canon(r) for r in roots]
while todo:
    dist = todo.pop()
    if dist in closure:
        continue
    closure.add(dist)
    try:
        requires = md.requires(dist) or []
    except md.PackageNotFoundError:
        continue
    for r in requires:
        if not re.search(r"extra\s*==", r):
            todo.append(canon(re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", r).group(0)))
allowed = {top for top, dists in md.packages_distributions().items() if any(canon(d) in closure for d in dists)}
allowed |= {"pip", "setuptools", "wheel", "pkg_resources", "_distutils_hack"}


class LocalOnly(importlib.abc.MetaPathFinder):
    # a package installed in this interpreter's site-packages that the CI runner does not have
    def find_spec(self, name, path=None, target=None):
        if "." in name or name in allowed or name in sys.stdlib_module_names:
            return None
        spec = importlib.machinery.PathFinder.find_spec(name, path)
        if spec is None:
            return None
        places = [spec.origin or ""] + [str(p) for p in (spec.submodule_search_locations or [])]
        if any("site-packages" in p.replace("\\", "/") or "dist-packages" in p.replace("\\", "/") for p in places):
            raise ModuleNotFoundError("No module named %r" % name, name=name)
        return None


sys.meta_path.insert(0, LocalOnly())
sys.path[:] = [p for p in sys.path if os.path.abspath(p or ".") != os.path.abspath(repo)]
sys.path.insert(0, os.path.join(repo, "scripts"))
sys.path.insert(0, os.path.join(repo, "harness"))
sys.path.insert(0, os.path.join(repo, "tests"))


def unimportable(e):
    missing = getattr(e, "name", None) or ""
    if isinstance(e, ModuleNotFoundError) and missing.split(".")[0] not in ("pytest", "_pytest", ""):
        return "imports %r, which is not available on the CI runner (it installs %s and what they need)" % (missing, ", ".join(roots))
    return "cannot be imported when pytest is not installed (%s: %s)" % (type(e).__name__, e)


problems, count, names = [], 0, []
needs = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
for path in sorted(glob.glob(os.path.join(glob.escape(repo), "tests", "test_*.py"))):
    name = os.path.basename(path)[:-3]
    try:
        mod = importlib.import_module(name)
    except BaseException as e:
        problems.append("%s: %s" % (name, unimportable(e)))
        continue
    ran = 0
    for attr, obj in list(vars(mod).items()):
        if inspect.isclass(obj):
            collected = attr.startswith("Test") and getattr(obj, "__test__", True) or issubclass(obj, unittest.TestCase) and obj is not unittest.TestCase
            if collected:
                problems.append("%s.%s: pytest collects this class, the built-in runner never runs a class" % (name, attr))
            continue
        if not attr.startswith("test") or not callable(obj):
            continue
        plain = inspect.isfunction(obj) and obj.__module__ == mod.__name__ and attr.startswith("test_")
        if not plain:
            problems.append("%s.%s: pytest collects it, the built-in runner only runs plain functions named test_* that are defined in the file" % (name, attr))
            continue
        ran += 1
        names.append("%s.%s" % (name, attr))
        if inspect.iscoroutinefunction(obj) or inspect.isasyncgenfunction(obj) or inspect.isgeneratorfunction(obj):
            problems.append("%s.%s is async or a generator; the built-in runner calls it and never runs the body, so it passes" % (name, attr))
        required = [p.name for p in inspect.signature(obj).parameters.values() if p.default is p.empty and p.kind in needs]
        if required:
            problems.append("%s.%s needs arguments %s; the built-in runner calls it with none" % (name, attr, required))
    if not ran:
        problems.append("%s: the built-in runner would find no test in it" % name)
    count += ran
print()
print("RESULT " + json.dumps({"count": count, "problems": problems, "names": names}))
"""

# Run in a child process with pytest blocked: scripts/check.py's own runner on small trees made for the purpose.
CHILD_RUNNER = r"""
import contextlib, io, json, os, sys
sys.modules["pytest"] = None
sys.modules["_pytest"] = None
repo, cases = sys.argv[1], json.loads(sys.argv[2])
sys.path.insert(0, os.path.join(repo, "scripts"))
import check
out = {}
for case, folder in cases.items():
    sys.path.insert(0, folder)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        ok = check.run_tests(folder)
    sys.path.remove(folder)
    out[case] = [bool(ok), buf.getvalue()[-800:]]
print("RESULT " + json.dumps(out))
"""


def _run_python(code, *args):
    done = subprocess.run([sys.executable, "-c", code, *args], cwd=args[0], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=600)
    tails = f"\nstdout: {(done.stdout or '')[-1500:]}\nstderr: {(done.stderr or '')[-1500:]}"
    assert done.returncode == 0, "the child process failed:" + tails
    lines = [ln for ln in (done.stdout or "").splitlines() if ln.startswith("RESULT ")]
    assert len(lines) == 1, "the child did not report one result line:" + tails
    return json.loads(lines[0][len("RESULT "):])


def _run_child(repo):
    return _run_python(CHILD, repo, ",".join(CI_PACKAGES))


def _test_files():
    files = sorted(glob.glob(os.path.join(glob.escape(HERE), "test_*.py")))
    assert len(files) > 20, f"only {len(files)} test files found in {HERE}"
    return files


def _ci_text():
    with open(os.path.join(REPO, ".github", "workflows", "ci.yml"), encoding="utf-8") as f:
        return f.read()


def _ci_packages(text):
    found = set()
    for line in text.splitlines():
        if "pip install" not in line:
            continue
        words = line.split("pip install", 1)[1].split()
        for i, w in enumerate(words):
            if w.startswith("-") or (i and words[i - 1] == "--upgrade"):
                continue
            found.add(re.split(r"[\[=<>~!;]", w)[0].lower())
    return found


def _ci_python(text):
    m = re.search(r"python-version:\s*[\"']?(\d+)\.(\d+)", text)
    assert m, "no python-version found in .github/workflows/ci.yml"
    return int(m.group(1)), int(m.group(2))


def test_every_test_module_imports_and_every_test_runs_without_arguments_when_pytest_is_missing():
    got = _run_child(REPO)
    assert got["count"] > 400, (f"only {got['count']} test functions were found (there are about 435): "
                                "the child did not import the test modules")
    assert not got["problems"], "scripts/check.py's built-in runner (used without pytest) cannot run these:\n" + "\n".join(got["problems"])


def test_every_file_pytest_would_collect_is_one_the_built_in_runner_runs():
    runs = {os.path.normcase(os.path.normpath(p)) for p in _test_files()}
    collected = set()
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py") and (f.startswith("test_") or f.endswith("_test.py")):
                collected.add(os.path.normcase(os.path.normpath(os.path.join(root, f))))
    missed = sorted(os.path.relpath(p, HERE) for p in collected - runs)
    assert not missed, "pytest collects these, the built-in runner (tests/test_*.py, no subfolders) does not: " + ", ".join(missed)


def test_ci_installs_exactly_the_packages_the_child_allows():
    got = _ci_packages(_ci_text())
    assert got == set(CI_PACKAGES), (f".github/workflows/ci.yml pip-installs {sorted(got)}; this file allows {sorted(CI_PACKAGES)}. "
                                     "Change CI_PACKAGES so the child blocks exactly what the CI runner lacks.")


# ---- reading the test files -------------------------------------------------------------------------------------------

PYTEST_NAMES = ("pytest", "_pytest")
IMPORT_FUNCS = {"import_module", "__import__", "find_spec", "importorskip"}
DEF_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)


def _is_guard(node):
    return isinstance(node, ast.If) and ast.unparse(node.test) == "pytest is not None"


def _direct_tests(stmts):
    """Tests defined at statement level of this branch. A test under `if sys.platform ...:` or `try:` may not exist when
    the runner imports the file, and one inside a def or class never does, so none of those count."""
    return ([s for s in stmts if isinstance(s, DEF_TYPES) and s.name.startswith("test_")]
            + [s for s in stmts if isinstance(s, ast.Assign) and any(isinstance(t, ast.Name) and t.id.startswith("test_") for t in s.targets)])


def _trivial(fn):
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]

    def inert(s):
        return (isinstance(s, ast.Pass)
                or isinstance(s, ast.Return) and (s.value is None or isinstance(s.value, ast.Constant))
                or isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                or isinstance(s, ast.Assert) and isinstance(s.test, ast.Constant))
    return all(inert(s) for s in body)


def _loads(nodes):
    return {n.id for s in nodes for n in ast.walk(s) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def _stores(nodes):
    return ({n.id for s in nodes for n in ast.walk(s) if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del))}
            | {a.arg for s in nodes for n in ast.walk(s) if isinstance(n, ast.arguments) for a in n.args + n.posonlyargs + n.kwonlyargs})


def _defined_top(stmts):
    """Names defined by def, class, assignment or import at statement level (through if, try and with) of these statements."""
    out = set()
    for s in stmts:
        if isinstance(s, DEF_TYPES + (ast.ClassDef,)):
            out.add(s.name)
        elif isinstance(s, ast.Assign):
            for t in s.targets:
                out |= {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}
        elif isinstance(s, (ast.AnnAssign, ast.AugAssign)) and isinstance(s.target, ast.Name):
            out.add(s.target.id)
        elif isinstance(s, (ast.Import, ast.ImportFrom)):
            out |= {(a.asname or a.name).split(".")[0] for a in s.names}
        else:
            for field in ("body", "orelse", "finalbody"):
                v = getattr(s, field, [])
                if isinstance(v, list):
                    out |= _defined_top(v)
            for h in getattr(s, "handlers", []):
                out |= _defined_top(h.body)
    return out


def _pytest_problems(tree):
    """(line, what) for every use of pytest the built-in runner cannot survive, and every guard without a real fallback."""
    found = []

    # ---- every import and use of pytest, and the test shapes pytest collects and the runner skips
    def visit(node, guarded, import_try):
        if _is_guard(node):
            for child in node.body:
                visit(child, True, import_try)
            for child in node.orelse:
                visit(child, guarded, import_try)
            return
        if isinstance(node, ast.Try):
            catches = any(h.type is not None and ("ImportError" in ast.unparse(h.type) or "ModuleNotFoundError" in ast.unparse(h.type))
                          for h in node.handlers)
            for child in node.body:
                visit(child, guarded, catches)
            for part in (node.handlers, node.orelse, node.finalbody):
                for child in part:
                    visit(child, guarded, False)
            return
        if not guarded:
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split(".")[0] in PYTEST_NAMES and (a.asname or a.name != "pytest" or not import_try):
                        found.append((node.lineno, "import pytest is allowed only as `try: import pytest / except ImportError: pytest = None`"))
            elif isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in PYTEST_NAMES:
                found.append((node.lineno, "from pytest import ... fails when pytest is not installed"))
            elif isinstance(node, ast.Name) and node.id == "pytest" and isinstance(node.ctx, ast.Load):
                found.append((node.lineno, "pytest is used outside an `if pytest is not None:` block (the guard has to be written exactly "
                                           "like that; move helpers that use pytest inside it)"))
            if isinstance(node, ast.Call):
                fname = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                first = node.args[0] if node.args else None
                named = isinstance(first, ast.Constant) and isinstance(first.value, str) and first.value.split(".")[0] in PYTEST_NAMES
                if fname in IMPORT_FUNCS and named:
                    found.append((node.lineno, "pytest is imported by name; it is not installed on the CI runner"))
                if fname == "get" and isinstance(node.func, ast.Attribute) and ast.unparse(node.func.value).endswith("modules") \
                        and isinstance(first, ast.Constant) and first.value in PYTEST_NAMES:
                    found.append((node.lineno, "pytest is looked up in sys.modules; the guard has to be `if pytest is not None:`"))
            if isinstance(node, ast.Subscript) and ast.unparse(node.value).endswith("modules") \
                    and isinstance(node.slice, ast.Constant) and node.slice.value in PYTEST_NAMES:
                found.append((node.lineno, "pytest is looked up in sys.modules; the guard has to be `if pytest is not None:`"))
        if isinstance(node, ast.ClassDef):
            if node.name.startswith("Test") or any(ast.unparse(b).split(".")[-1] == "TestCase" for b in node.bases):
                found.append((node.lineno, "pytest collects this test class, the built-in runner never runs a class"))
        for child in ast.iter_child_nodes(node):
            visit(child, guarded, import_try)

    visit(tree, False, False)

    # ---- every guard: where it sits, what its else branch does, what the two branches share
    top_defs = {s.name for s in tree.body if isinstance(s, DEF_TYPES + (ast.ClassDef,))}
    fn_nodes = {s.name: s for s in ast.walk(tree) if isinstance(s, DEF_TYPES) and s.name in top_defs}

    def reach(names):
        """the names plus everything the module-level functions among them load, transitively"""
        seen, todo = set(), list(names)
        while todo:
            n = todo.pop()
            if n in seen:
                continue
            seen.add(n)
            if n in fn_nodes:
                todo += list(_loads([fn_nodes[n]]))
        return seen

    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}

    def inside_def(n):
        while n in parents:
            n = parents[n]
            if isinstance(n, DEF_TYPES + (ast.Lambda, ast.ClassDef)):
                return True
        return False

    guards = [n for n in ast.walk(tree) if _is_guard(n)]
    in_guard_nodes = {id(x) for g in guards for s in g.body for x in ast.walk(s)}
    for g in guards:
        if inside_def(g):
            if not g.orelse:
                found.append((g.lineno, "an `if pytest is not None:` inside a function with no else: its lines are skipped without pytest "
                                        "and the test still passes"))
            continue
        gt, et = _direct_tests(g.body), _direct_tests(g.orelse)
        if gt and not et:
            found.append((g.lineno, "defines tests only when pytest is installed, with no else: branch that defines them too"))
        gt, et = [t for t in gt if isinstance(t, ast.FunctionDef)] or gt, [t for t in et if isinstance(t, ast.FunctionDef)] or et
        if any(isinstance(t, ast.FunctionDef) and _trivial(t) for t in et):
            found.append((g.lineno, "a fallback test in the else: branch does nothing"))
        if gt and et and all(isinstance(t, ast.FunctionDef) for t in gt + et):
            # module-level functions, classes and constants (not imports) that the guarded tests use, their decorators
            # (the parametrize data) included, must be reachable from the fallback tests
            top_vars = _defined_top([s for s in tree.body if isinstance(s, DEF_TYPES + (ast.ClassDef, ast.Assign, ast.AnnAssign))])
            outside = top_vars - _defined_top(g.body)
            used_g = set()
            for t in gt:
                local = _stores([t]) | {t.name}
                used_g |= {n for n in _loads(t.body) | _loads(t.decorator_list) if n in outside and n not in local}
            used_e = reach(set().union(*[_loads(t.body) for t in et]) | {n for t in et for n in _loads(t.decorator_list)})
            miss = sorted(used_g - used_e)
            if miss:
                found.append((g.lineno, f"the guarded tests call {miss} but the else: tests never reach them"))
        # names that exist only because pytest is installed
        only_guard = _defined_top(g.body) - _defined_top(g.orelse) - {s.name for s in tree.body if isinstance(s, (ast.FunctionDef, ast.ClassDef))}
        only_guard -= _defined_top([s for s in tree.body if s is not g])
        if only_guard:
            for n in ast.walk(tree):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in only_guard and id(n) not in in_guard_nodes:
                    found.append((n.lineno, f"{n.id} exists only when pytest is installed (defined under `if pytest is not None:`) "
                                            "but is used outside that block"))
    return sorted(set(found))


def _test_names(stmts):
    names = set()
    for s in _direct_tests(stmts):
        if isinstance(s, ast.Assign):
            names |= {t.id for t in s.targets if isinstance(t, ast.Name) and t.id.startswith("test_")}
        else:
            names.add(s.name)
    return names


def _static_names(tree):
    """(names pytest collects, names the built-in runner runs), read from the module-level statements and the guards."""
    plain, with_pytest, without = _test_names(tree.body), set(), set()
    for s in tree.body:
        if _is_guard(s):
            with_pytest |= _test_names(s.body)
            without |= _test_names(s.orelse)
    return plain | with_pytest, plain | without


def _parse(path):
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read(), path, feature_version=_ci_python(_ci_text()))


def test_every_test_file_follows_the_pytest_optional_pattern():
    files = sorted(glob.glob(os.path.join(glob.escape(HERE), "*.py")))
    assert len(files) > 20 and any(os.path.basename(p) == "conftest.py" for p in files), f"only {len(files)} files read in {HERE}"
    bad = []
    for path in files:
        bad += [f"{os.path.basename(path)}:{n}: {what}" for n, what in _pytest_problems(_parse(path))]
    assert not bad, "these do not survive a run without pytest:\n" + "\n".join(bad)


def test_conftest_defines_no_fixture_the_built_in_runner_cannot_supply():
    tree = _parse(os.path.join(HERE, "conftest.py"))
    defined = [s.name for s in tree.body if isinstance(s, DEF_TYPES + (ast.ClassDef,))]
    assert not defined, f"tests/conftest.py defines {defined}; the built-in runner never reads conftest.py, so nothing in it can be relied on"


def test_the_built_in_runner_and_pytest_run_the_same_test_names():
    static_pytest, static_runner = set(), set()
    for path in _test_files():
        module = os.path.basename(path)[:-3]
        with_pytest, without = _static_names(_parse(path))
        static_pytest |= {f"{module}.{n}" for n in with_pytest}
        static_runner |= {f"{module}.{n}" for n in without}
    got = _run_child(REPO)
    runner = set(got["names"])
    assert runner == static_runner, ("the child that imitates the runner and the files disagree: "
                                     f"only in the child {sorted(runner - static_runner)[:10]}, only in the files {sorted(static_runner - runner)[:10]}")
    version = subprocess.run([sys.executable, "-m", "pytest", "--version"], cwd=REPO, capture_output=True, text=True, timeout=120)
    if version.returncode != 0:
        return  # pytest is not installed (the CI runner): nothing to compare with
    done = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "tests"],
                          cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    assert done.returncode == 0, "pytest --collect-only failed:\n" + (done.stdout or "")[-1500:] + (done.stderr or "")[-1500:]
    collected = set()
    for line in (done.stdout or "").splitlines():
        m = re.match(r"^(?:.*[/\\])?(test_\w+)\.py::(.*)$", line.strip())
        if m:
            collected.add(m.group(1) + "." + m.group(2).split("[", 1)[0].replace("::", "."))
    assert collected == static_pytest, ("pytest and the files disagree: "
                                        f"only in pytest {sorted(collected - static_pytest)[:10]}, only in the files {sorted(static_pytest - collected)[:10]}")
    assert collected - runner == static_pytest - static_runner and runner - collected == static_runner - static_pytest


# ---- the shapes the scans and the child must report ---------------------------------------------------------------------

def _src(text):
    return textwrap.dedent(text).lstrip("\n")


_HEAD = "try:\n    import pytest\nexcept ImportError:\n    pytest = None\n\n"  # the guard starts on line 6
_PATTERN = _src("""
    if pytest is not None:
        @pytest.mark.parametrize("x", [1, 2])
        def test_a(x):
            assert x

    else:
        def test_a():
            assert sorted([2, 1]) == [1, 2]
""")

SAMPLES = (
    # (name, source, the lines that must be reported)
    ("the pattern", _HEAD + _PATTERN, []),
    ("the pattern with ModuleNotFoundError", (_HEAD + _PATTERN).replace("ImportError", "ModuleNotFoundError"), []),
    ("a parenthesized guard", (_HEAD + _PATTERN).replace("if pytest is not None:", "if (pytest is not None):"), []),
    ("two guards", _HEAD + _PATTERN + "\n" + _PATTERN.replace("test_a", "test_b"), []),
    ("a helper that only the guarded tests use", _HEAD + _src("""
        if pytest is not None:
            def _rows():
                return [1, 2]

            @pytest.mark.parametrize("x", _rows())
            def test_a(x):
                assert x
        else:
            def test_a():
                assert sorted([2, 1]) == [1, 2]
    """), []),
    ("guard with helpers only", _HEAD + "if pytest is not None:\n    def helper():\n        pass\n", []),
    ("bare import and use", "import pytest\n\ndef test_a():\n    with pytest.raises(ValueError):\n        pass\n", [1, 4]),
    ("use in the else branch", "pytest = None\nif pytest is not None:\n    pass\nelse:\n    def test_a():\n        pytest.fail('x')\n", [6]),
    ("guard without an else branch", _HEAD + _PATTERN.split("\nelse:")[0].rstrip() + "\n", [6]),
    ("import under an alias", "try:\n    import pytest as pt\nexcept ImportError:\n    pt = None\n", [2]),
    ("from-import", "from pytest import raises\n\ndef test_a():\n    with raises(ValueError):\n        pass\n", [1]),
    ("alias by assignment", "try:\n    import pytest\nexcept ImportError:\n    pytest = None\nP = pytest\n", [5]),
    ("import inside a function", "def test_a():\n    import pytest\n    pytest.skip('x')\n", [2, 3]),
    ("import under a try that does not catch ImportError", "try:\n    import pytest\nexcept ValueError:\n    pytest = None\n", [2]),
    ("the private package", "import _pytest\n", [1]),
    ("import by name", "import importlib\n\n\ndef test_a():\n    importlib.import_module('pytest')\n", [5]),
    ("lookup in sys.modules", "import sys\n\n\ndef test_a():\n    return sys.modules['pytest']\n", [5]),
    ("a test class", "class TestA:\n    def test_a(self):\n        pass\n\n\ndef test_ok():\n    pass\n", [1]),
    ("a TestCase next to a plain test", "import unittest\n\n\nclass Check(unittest.TestCase):\n    def test_a(self):\n        pass\n\n\ndef test_ok():\n    pass\n", [4]),
    ("a helper that exists only in the guard, used by the fallback", _HEAD + _src("""
        if pytest is not None:
            def _helper():
                return 1

            @pytest.mark.parametrize("x", [1])
            def test_a(x):
                assert _helper()
        else:
            def test_a():
                assert _helper()
    """), [15]),
    ("a fallback test that does nothing", _HEAD + _PATTERN.replace("assert sorted([2, 1]) == [1, 2]", "pass"), [6]),
    ("a guard inside a test", _HEAD + "def test_a():\n    if pytest is not None:\n        assert 1 + 1\n", [7]),
    ("the fallback test nested in a function", _HEAD + _src("""
        if pytest is not None:
            @pytest.mark.parametrize("x", [1])
            def test_a(x):
                assert x
        else:
            def _wrap():
                def test_a():
                    assert 1 + 1
    """), [6]),
    ("the fallback test under a condition", _HEAD + _src("""
        if pytest is not None:
            @pytest.mark.parametrize("x", [1])
            def test_a(x):
                assert x
        else:
            if sys.platform == "win32":
                def test_a():
                    assert 1 + 1
    """), [6]),
    ("a fallback that never reaches the checker", _HEAD + _src("""
        def _check(x):
            assert x


        if pytest is not None:
            @pytest.mark.parametrize("x", [1])
            def test_a(x):
                _check(x)
        else:
            def test_a():
                assert 1 + 1
    """), [10]),
)


def test_the_scan_reports_each_unsafe_shape_and_passes_the_pattern():
    assert len(SAMPLES) > 20
    for name, source, lines in SAMPLES:
        got = [n for n, _ in _pytest_problems(ast.parse(source))]
        assert got == lines, f"{name}: reported lines {got}, expected {lines}"


SYNTHETIC = {
    # module -> source; every module but the clean one must be reported by the child
    "test_c01_class": "class TestX:\n    def test_a(self):\n        pass\n\n\ndef test_ok():\n    pass\n",
    "test_c02_noprefix": "def testfoo():\n    pass\n\n\ndef test_ok():\n    pass\n",
    "test_c03_async": "async def test_a():\n    pass\n",
    "test_c04_generator": "def test_g():\n    yield 1\n",
    "test_c05_args": "def test_a(x):\n    pass\n",
    "test_c06_empty": "X = 1\n",
    "test_c07_testcase": "import unittest\n\n\nclass Check(unittest.TestCase):\n    def test_a(self):\n        pass\n\n\ndef test_ok():\n    pass\n",
    "test_c08_partial": "import functools\n\n\ndef _f(x):\n    pass\n\n\ntest_p = functools.partial(_f, 1)\n\n\ndef test_ok():\n    pass\n",
    "test_c09_imported": "from test_c99_clean import test_clean\n\n\ndef test_ok():\n    pass\n",
    "test_c10_import": "import pytest\n\n\ndef test_ok():\n    pass\n",
    "test_c11_from": "from pytest import raises\n\n\ndef test_ok():\n    pass\n",
    "test_c12_private": "import _pytest\n\n\ndef test_ok():\n    pass\n",
    "test_c13_ci_only": "import pluggy\n\n\ndef test_ok():\n    pass\n",
    "test_c14_broken": "raise RuntimeError('boom')\n",
    "test_c15_exit": "import sys\nsys.exit(0)\n",
}
SYNTHETIC_CLEAN = {"test_c99_clean": "import json\n\n\ndef test_clean():\n    assert json.dumps(1) == '1'\n"}


def test_the_child_reports_every_shape_the_runner_would_trip_over_and_leaves_a_clean_module_alone():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "tests"))
        for module, source in {**SYNTHETIC, **SYNTHETIC_CLEAN}.items():
            with open(os.path.join(tmp, "tests", module + ".py"), "w", encoding="utf-8") as f:
                f.write(source)
        got = _run_child(tmp)
    problems = got["problems"]
    for module in SYNTHETIC:
        assert any(re.match(re.escape(module) + r"[.:]", p) for p in problems), f"{module} was not reported:\n" + "\n".join(problems)
    assert not [p for p in problems if p.startswith("test_c99_clean")], "the clean module was reported:\n" + "\n".join(problems)
    assert "test_c99_clean.test_clean" in got["names"] and "test_c02_noprefix.testfoo" not in got["names"]
    ci_only = [p for p in problems if p.startswith("test_c13_ci_only")]
    assert ci_only and "pluggy" in ci_only[0] and "CI runner" in ci_only[0], ci_only


def test_the_built_in_runner_fails_a_test_that_exits_a_folder_without_tests_and_a_path_with_brackets():
    cases = {
        "passing": ("tests_pass", {"test_runner_pass.py": "def test_a():\n    pass\n"}),
        "exits": ("tests_exit", {"test_runner_exit.py": "import sys\n\n\ndef test_a():\n    sys.exit(0)\n"}),
        "fails": ("tests_fail", {"test_runner_fail.py": "def test_a():\n    assert 1 == 2\n"}),
        "empty": ("tests_empty", {"helper.py": "X = 1\n"}),
        "brackets": ("tests[1]", {"test_runner_bracket.py": "def test_a():\n    pass\n"}),
    }
    with tempfile.TemporaryDirectory() as tmp:
        folders = {}
        for case, (folder, files) in cases.items():
            folders[case] = os.path.join(tmp, folder)
            os.makedirs(folders[case])
            for name, source in files.items():
                with open(os.path.join(folders[case], name), "w", encoding="utf-8") as f:
                    f.write(source)
        got = _run_python(CHILD_RUNNER, REPO, json.dumps(folders))
    assert got["passing"][0] and "1 passed, 0 failed" in got["passing"][1], got["passing"]
    assert got["brackets"][0] and "1 passed, 0 failed" in got["brackets"][1], got["brackets"]
    assert not got["exits"][0] and "1 failed" in got["exits"][1], got["exits"]
    assert not got["fails"][0] and "1 failed" in got["fails"][1], got["fails"]
    assert not got["empty"][0] and "no test to run" in got["empty"][1], got["empty"]
