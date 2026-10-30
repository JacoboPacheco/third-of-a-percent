"""scripts/check.py says at the start of a run, not after an hour of other steps, that the page check at the end cannot run.

The page step needs the playwright package and its Chromium. Without either, scripts/check_site.py returns 2 and the run ends with
exit 3 ("CHECKS PASSED, WITH SKIPPED STEPS"); before this preflight a reader found that out at the very end. Now `check_site.py
--preflight` (the import plus an empty page, a few seconds) runs right after the package preflight, and check.py prints one line
when it exits 2. Nothing fails at that point and the step order is unchanged.

Four things are checked:
  1. the real --preflight, started with PLAYWRIGHT_BROWSERS_PATH pointing at an empty folder, exits 2 and names the missing Chromium
     (or the missing package, on a machine without playwright);
  2. launch_chromium() turns only a missing-browser launch error into that message; any other launch error is raised as it is;
  3. check.py's page_tools_preflight() prints the skip line for exit 2 only, and a different line for any other failure;
  4. the wiring in the two scripts (flag, call order, message text) is read from the source, and each part has a tamper test.

No pytest import: plain functions that scripts/check.py's built-in runner can call. It does not prove that a browser starts on a
machine where one is installed, or that the preflight's verdict matches the full page step's on every kind of broken install.
"""
import contextlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHROMIUM_MESSAGE = "the Chromium browser for playwright is not installed (playwright install chromium; on Linux add --with-deps)"
PACKAGE_MESSAGE = "the Python playwright package is not installed"


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


def load(rel, key):
    spec = importlib.util.spec_from_file_location(key, os.path.join(REPO, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def have_playwright():
    return importlib.util.find_spec("playwright") is not None


# ---- 1. the real flag

def test_preflight_exits_2_and_names_the_missing_chromium_when_the_browser_folder_is_empty():
    with tempfile.TemporaryDirectory() as empty:
        env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=empty)
        r = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "check_site.py"), "--preflight"],
                           capture_output=True, text=True, env=env, timeout=180)
    out = r.stdout + r.stderr
    assert r.returncode == 2, f"exit {r.returncode}, not 2:\n{out}"
    want = CHROMIUM_MESSAGE if have_playwright() else PACKAGE_MESSAGE
    assert want in r.stdout, f"the output does not say {want!r}:\n{out}"
    assert "FAIL" in r.stdout and "Traceback" not in out, out


# ---- 2. launch_chromium() catches only the missing browser

class FakeChromium:
    def __init__(self, error=None):
        self.error, self.args = error, None

    def launch(self, args=None):
        self.args = args
        if self.error is not None:
            raise self.error
        return "a browser"


class FakePlaywright:
    def __init__(self, error=None):
        self.chromium = FakeChromium(error)


def test_launch_chromium_catches_a_missing_browser_and_nothing_else():
    if not have_playwright():
        return  # the missing-package side is test 1; there is no playwright Error class to raise here
    from playwright.sync_api import Error as PlaywrightError
    cs = load("scripts/check_site.py", "check_site_for_the_preflight_test")
    p = FakePlaywright()
    assert cs.launch_chromium(p) == "a browser" and p.chromium.args == cs.BROWSER_ARGS
    out = io.StringIO()
    missing = PlaywrightError("BrowserType.launch: Executable doesn't exist at /nowhere/chrome\nLooks like Playwright was just installed")
    with contextlib.redirect_stdout(out):
        assert cs.launch_chromium(FakePlaywright(missing)) is None
    assert out.getvalue().strip() == f"FAIL {CHROMIUM_MESSAGE}", out.getvalue()
    for other in (PlaywrightError("BrowserType.launch: Host system is missing dependencies to run browsers"),
                  PlaywrightError("BrowserType.launch: Target page, context or browser has been closed"), RuntimeError("boom")):
        try:
            got = cs.launch_chromium(FakePlaywright(other))
        except (PlaywrightError, RuntimeError) as e:
            assert e is other
        else:
            raise AssertionError(f"{other!r} was swallowed (launch_chromium returned {got!r}) instead of raised")


# ---- 3. check.py's line

def run_preflight_with(check, rc):
    """What page_tools_preflight() prints when `check_site.py --preflight` exits rc (subprocess.call stands in for the child)."""
    calls = []
    real = subprocess.call
    subprocess.call = lambda cmd, *a, **k: (calls.append(cmd), rc)[1]
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            check.page_tools_preflight()
    finally:
        subprocess.call = real
    return out.getvalue(), calls


def test_check_py_prints_the_skip_line_for_exit_2_only():
    check = load("scripts/check.py", "check_for_the_preflight_test")
    text, calls = run_preflight_with(check, 2)
    assert len(calls) == 1 and calls[0][-1] == "--preflight" and calls[0][-2].endswith("check_site.py"), calls
    lines = [x for x in text.splitlines() if x.strip()]
    assert len(lines) == 1, lines
    assert lines[0].startswith("the page check at the end will be skipped: playwright or its Chromium is missing"), lines[0]
    assert lines[0].endswith("the run will end with exit 3"), lines[0]
    text0, _ = run_preflight_with(check, 0)
    assert text0 == "", f"a working install prints nothing, not {text0!r}"
    text1, _ = run_preflight_with(check, 1)
    assert "will be skipped" not in text1 and "exited 1" in text1, text1


# ---- 4. the wiring, read from the source

def wiring_problems(check_src, site_src):
    """What is missing or out of order in the two scripts (empty when the preflight is wired as described above)."""
    out = []
    m = re.search(r"^def main\(\):.*?(?=^def |^if __name__|\Z)", check_src, re.M | re.S)
    body = m.group(0) if m else ""
    i_pkg, i_pre, i_run = body.find("missing_packages()"), body.find("page_tools_preflight()"), body.find("run_tests()")
    if not 0 <= i_pkg < i_pre < i_run:
        out.append("check.py main() does not call page_tools_preflight() after the package check and before run_tests()")
    pf = re.search(r"^def page_tools_preflight\(\):.*?(?=^def )", check_src, re.M | re.S)
    pf = pf.group(0) if pf else ""
    for need in ('"--preflight"', "the page check at the end will be skipped:", "the run will end with exit", "rc == 2"):
        if need not in pf:
            out.append(f"page_tools_preflight() lacks {need!r}")
    if 'PAGE_TOOLS_MISSING = "playwright or its Chromium is missing"' not in check_src:
        out.append("check.py does not define PAGE_TOOLS_MISSING as 'playwright or its Chromium is missing'")
    last = check_src.rfind("if rc == 2:")  # the page step's own branch, after the preflight function's
    final = check_src[last:].split("rc = subprocess", 1)[0] if last >= 0 else ""
    if "skipped: {PAGE_TOOLS_MISSING}, so the page was not driven" not in final or "{PAGE_TOOLS_MISSING}; {PAGE_TOOLS_HINT}" not in final:
        out.append("the page step's exit-2 message does not use PAGE_TOOLS_MISSING")
    if 'ap.add_argument("--preflight", action="store_true"' not in site_src or not re.search(r"if a\.preflight:\n\s+return preflight\(\)", site_src):
        out.append("check_site.py has no --preflight flag that returns preflight()")
    if f'CHROMIUM_MISSING = "{CHROMIUM_MESSAGE}"' not in site_src or "Executable doesn't exist" not in site_src:
        out.append("check_site.py does not name the missing Chromium the way the tests expect")
    if site_src.count("p.chromium.launch(") != 1 or "browser = launch_chromium(p)" not in site_src:
        out.append("check_site.py launches Chromium outside launch_chromium()")
    return out


def test_the_scripts_wire_the_preflight_as_described():
    assert wiring_problems(read("scripts/check.py"), read("scripts/check_site.py")) == []


def test_each_part_of_the_wiring_is_caught_when_taken_out():
    check_src, site_src = read("scripts/check.py"), read("scripts/check_site.py")
    assert wiring_problems(check_src, site_src) == []
    moved = check_src.replace("    page_tools_preflight()\n    skipped = []\n    ok = run_tests()", "    skipped = []\n    ok = run_tests()\n    page_tools_preflight()")
    removed = check_src.replace("    page_tools_preflight()\n    skipped = []", "    skipped = []")
    assert moved != check_src and removed != check_src
    tampered = (
        ("the call moved after run_tests()", moved, site_src),
        ("the call removed", removed, site_src),
        ("the skip line reworded", check_src.replace("the page check at the end will be skipped:", "the page check will not run:"), site_src),
        ("the exit hint removed", check_src.replace("the run will end with exit", "the run ends with"), site_src),
        ("the constant reworded", check_src.replace('PAGE_TOOLS_MISSING = "playwright or its Chromium is missing"', 'PAGE_TOOLS_MISSING = "the playwright package is missing"'), site_src),
        ("the final message back to the old text", check_src.replace("skipped: {PAGE_TOOLS_MISSING}, so", "skipped: the playwright package is missing, so"), site_src),
        ("the flag removed", check_src, site_src.replace('ap.add_argument("--preflight", action="store_true"', 'ap.add_argument("--no-preflight", action="store_true"')),
        ("the flag ignored", check_src, site_src.replace("    if a.preflight:\n        return preflight()\n", "")),
        ("the Chromium message reworded", check_src, site_src.replace("is not installed (playwright install chromium; on Linux", "is not installed (on Linux")),
        ("the missing-browser test removed", check_src, site_src.replace("Executable doesn't exist", "Executable is gone")),
        ("a second bare launch", check_src, site_src.replace("browser = launch_chromium(p)", "browser = p.chromium.launch(args=[])", 1)),
    )
    for label, c, s in tampered:
        assert c != check_src or s != site_src, f"{label}: the edit did not change anything"
        assert wiring_problems(c, s) != [], f"{label}: not caught"
