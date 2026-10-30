"""requirements.txt, and the two documents' sentences about installing what the check needs.

The file lists, as plain names, exactly the pip packages that scripts/check.py refuses to start without (REQUIRED_PACKAGES, read from
the source with a regular expression, not imported), and its comment lines name playwright (needed by the page check only) and say
that pytest is optional. README.md and readme-parts/DETAILS.md say that `pip install -r requirements.txt` installs the same
packages as the typed `pip install` line, and that CI runs the Python version that .github/workflows/ci.yml sets; the package names
and the version in those sentences are rebuilt here from the two files, not typed.

Nothing is written. Each check has a tamper test: the broken file or sentence is built in memory and the check has to name it.

Runs with or without pytest (scripts/check.py's built-in runner, which CI uses, has none).
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_readme_numbers as T  # noqa: E402

REQUIREMENTS = "requirements.txt"
CHECK = "scripts/check.py"
CI = ".github/workflows/ci.yml"


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


def read(rel):
    with open(os.path.join(T.REPO, rel), encoding="utf-8") as f:
        return f.read()


def required_pip_names(source):
    """The pip names of REQUIRED_PACKAGES in scripts/check.py, in the order the source gives them."""
    m = re.search(r"^REQUIRED_PACKAGES = \((.*)\)\s*$", source, re.M)
    assert m, "scripts/check.py no longer has a one-line REQUIRED_PACKAGES tuple"
    pairs = re.findall(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', m.group(1))
    assert pairs, "REQUIRED_PACKAGES holds no (module, pip name) pairs"
    return [pip for _, pip in pairs]


def requirement_names(text):
    """The package names on the non-comment lines of a requirements file (a version specifier after the name is ignored)."""
    names = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", line)
        assert m, f"{REQUIREMENTS}: the line {line!r} does not begin with a package name"
        names.append(m.group(0).lower())
    return names


def comment_text(text):
    return " ".join(line.strip().lstrip("#").strip() for line in text.splitlines() if line.strip().startswith("#")).lower()


def check_requirements(text, source):
    names = requirement_names(text)
    assert len(names) == len(set(names)), f"{REQUIREMENTS} names a package twice: {names}"
    assert sorted(names) == sorted(n.lower() for n in required_pip_names(source)), \
        f"{REQUIREMENTS} lists {names}, scripts/check.py requires {required_pip_names(source)}"
    comments = comment_text(text)
    assert "playwright" in comments and "page check" in comments, f"{REQUIREMENTS} no longer says that the page check needs playwright"
    assert "pytest" in comments and "optional" in comments, f"{REQUIREMENTS} no longer says that pytest is optional"
    assert "playwright" not in names and "pytest" not in names, f"{REQUIREMENTS} lists a package that is optional or installed apart"


def ci_python_version(ci_text):
    versions = set(re.findall(r'python-version:\s*"?([0-9]+(?:\.[0-9]+)*)"?', ci_text))
    assert len(versions) == 1, f"{CI} sets {len(versions)} Python versions ({sorted(versions)}), not one"
    return versions.pop()


def install_phrase(source):
    """The typed install line and the requirements form, as the two documents write them."""
    names = required_pip_names(source)
    count_words = {2: "two", 3: "three"}
    assert len(names) in count_words, f"scripts/check.py requires {len(names)} packages; the sentence has words for two or three"
    return f"`pip install {' '.join(names)}`, or `pip install -r {REQUIREMENTS}` for the same {count_words[len(names)]}"


def check_document(doc, text, source, ci_text):
    flat = T.squash(text)
    phrase = T.squash(install_phrase(source))
    assert flat.count(phrase) == 1, f"{doc} does not hold, once, the install sentence {phrase!r}"
    version = ci_python_version(ci_text)
    needle = f"CI runs {version}"
    assert flat.count(needle) == 1, f"{doc} does not say, once, {needle!r} (the Python version {CI} sets)"


def test_requirements_txt_lists_what_scripts_check_py_requires():
    check_requirements(read(REQUIREMENTS), read(CHECK))


def test_every_requirement_is_also_installed_by_ci():
    ci = read(CI)
    lines = [ln for ln in ci.splitlines() if "pip install" in ln and "--upgrade pip" not in ln]
    assert lines, f"{CI} has no pip install line for the packages"
    for name in requirement_names(read(REQUIREMENTS)):
        assert any(name in ln.lower().split() for ln in lines), f"{CI} does not install {name}"


def test_a_changed_requirements_file_or_check_py_is_caught():
    text, source = read(REQUIREMENTS), read(CHECK)
    check_requirements(text, source)
    for what, broken in (
            ("a package dropped", text.replace("pyyaml\n", "", 1)),
            ("a package added", text.replace("pyyaml\n", "pyyaml\nrequests\n", 1)),
            ("a package renamed", text.replace("pyyaml\n", "yaml\n", 1)),
            ("a package listed twice", text.replace("numpy\n", "numpy\nnumpy\n", 1)),
            ("playwright listed as a requirement", text.replace("pyyaml\n", "pyyaml\nplaywright\n", 1)),
            ("pytest listed as a requirement", text.replace("pyyaml\n", "pyyaml\npytest\n", 1)),
            ("the playwright comment dropped", text.replace("playwright", "a browser driver")),
            ("the optional pytest comment dropped", text.replace("optional", "needed")),
            ("a requirement commented out", text.replace("numpy\n", "# numpy\n", 1))):
        assert broken != text, f"the tamper test no longer matches the file: {what}"
        assertion_from(lambda: check_requirements(broken, source), what)
    assert 'REQUIRED_PACKAGES = (("numpy", "numpy"), ("yaml", "pyyaml"))' in source
    for what, broken in (
            ("a package added to check.py", source.replace('("yaml", "pyyaml"))', '("yaml", "pyyaml"), ("scipy", "scipy"))', 1)),
            ("a package dropped from check.py", source.replace('("numpy", "numpy"), ', "", 1)),
            ("a package renamed in check.py", source.replace('("yaml", "pyyaml")', '("yaml", "PyYAML-ng")', 1))):
        assertion_from(lambda: check_requirements(text, broken), what)
    assertion_from(lambda: required_pip_names("no tuple here"), "no REQUIRED_PACKAGES tuple")


def test_the_readme_and_details_say_what_the_requirements_file_installs_and_the_ci_python():
    source, ci = read(CHECK), read(CI)
    for doc, reader in (("README.md", T.readme_text), ("readme-parts/DETAILS.md", T.details_text)):
        text = reader()
        check_document(doc, text, source, ci)
        phrase = install_phrase(source)
        version = ci_python_version(ci)
        for what, broken in (
                ("the requirements form dropped", T.squash(text).replace("or `pip install -r requirements.txt` for the same two", "")),
                ("the file renamed", T.squash(text).replace("-r requirements.txt", "-r requirements-dev.txt")),
                ("the count of packages changed", T.squash(text).replace("for the same two", "for the same three")),
                ("the typed line changed", T.squash(text).replace("`pip install numpy pyyaml`", "`pip install numpy pyyaml scipy`")),
                ("the Python version changed", T.squash(text).replace(f"CI runs {version}", "CI runs 3.9")),
                ("the Python version dropped", T.squash(text).replace(f"CI runs {version}", "CI runs"))):
            assert broken != T.squash(text), f"the tamper test no longer matches {doc}: {what}"
            assertion_from(lambda: check_document(doc, broken, source, ci), f"{doc}: {what}")
        assertion_from(lambda: check_document(doc, T.squash(text) + " " + T.squash(phrase), source, ci), f"{doc}: the install sentence repeated")
    changed_ci = ci.replace(f'python-version: "{ci_python_version(ci)}"', 'python-version: "3.13"')
    assertion_from(lambda: check_document("README.md", T.readme_text(), source, changed_ci), "the CI Python version moved")
    assertion_from(lambda: ci_python_version("steps: []"), "no Python version in the workflow")
