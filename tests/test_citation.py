"""CITATION.cff: how GitHub's "Cite this repository" box reads the repository.

The file has to parse, carry the keys the Citation File Format requires (cff-version, message, title, authors) and the ones the
repository relies on (license, repository-code, url, abstract), name the author the way LICENSE names the copyright holder, and
point at the same repository and page as the README. It carries no version and no doi: neither exists yet, and a version in the
file would be a claim about a tag that has to exist first.

Nothing is written. Each check has a tamper test: the broken document is built in memory and the check has to name it.

Runs with or without pytest (scripts/check.py's built-in runner, which CI uses, has none).
"""

import copy
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED = ("cff-version", "message", "title", "authors", "license", "repository-code", "url", "abstract")
REPOSITORY = "https://github.com/JacoboPacheco/third-of-a-percent"
PAGE = "https://jacobopacheco.github.io/third-of-a-percent/"
ABSTRACT = "A loop-by-loop measurement of what libc++ bounds checks cost, set next to Google's 0.30% average, with the machine code as proof."


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def load():
    import yaml

    doc = yaml.safe_load(read("CITATION.cff"))
    assert isinstance(doc, dict), "CITATION.cff does not parse to a mapping"
    return doc


def license_holder(license_text):
    """'Jacobo Pacheco' from the 'Copyright (c) 2026 Jacobo Pacheco' line of LICENSE."""
    m = re.search(r"^Copyright \(c\) \d{4} (?P<holder>.+?)\s*$", license_text, re.M)
    assert m, "LICENSE has no 'Copyright (c) <year> <holder>' line"
    return m.group("holder")


def check_citation(doc, license_text, readme_text):
    missing = [k for k in REQUIRED if k not in doc or doc[k] in (None, "", [])]
    assert not missing, f"CITATION.cff lacks {missing}"
    assert doc["cff-version"] == "1.2.0", f"cff-version is {doc['cff-version']!r}, not '1.2.0'"
    assert isinstance(doc["message"], str) and doc["message"].strip(), "the message is empty"
    assert doc["title"] == "Third of a Percent", f"the title is {doc['title']!r}; the README's is 'Third of a Percent'"
    authors = doc["authors"]
    assert isinstance(authors, list) and len(authors) == 1 and isinstance(authors[0], dict), f"authors is {authors!r}, not one person"
    person = authors[0]
    assert set(person) == {"family-names", "given-names"}, f"the author carries {sorted(person)}; only family-names and given-names are expected"
    name = f"{person['given-names']} {person['family-names']}"
    holder = license_holder(license_text)
    assert name == holder, f"the author is {name!r}; LICENSE names {holder!r} as the copyright holder"
    assert doc["license"] == "MIT" and license_text.startswith("MIT License"), f"license is {doc['license']!r}; LICENSE is not the MIT text"
    assert doc["repository-code"] == REPOSITORY, f"repository-code is {doc['repository-code']!r}, not {REPOSITORY!r}"
    assert doc["url"] == PAGE, f"url is {doc['url']!r}, not {PAGE!r}"
    assert doc["abstract"] == ABSTRACT, f"the abstract is {doc['abstract']!r}, not the repository description"
    assert REPOSITORY in readme_text and PAGE in readme_text, "the README no longer names the repository and the page CITATION.cff points at"
    assert not {"version", "doi", "date-released"} & set(doc), "CITATION.cff carries a version, doi or release date before any tag or archive exists"


def test_citation_cff_parses_and_is_consistent_with_the_licence_and_readme():
    check_citation(load(), read("LICENSE"), read("README.md"))


def test_the_author_is_the_licence_holder():
    doc = load()
    person = doc["authors"][0]
    assert f"{person['given-names']} {person['family-names']}" == license_holder(read("LICENSE")) == "Jacobo Pacheco"


def assertion_from(fn, what):
    """The AssertionError that fn() raises. Fails if it raises none: the stand-in for pytest.raises, which the built-in runner lacks."""
    try:
        fn()
    except AssertionError as e:
        return e
    raise AssertionError(f"{what}: no AssertionError was raised")


def test_a_broken_citation_is_caught():
    good, lic, readme = load(), read("LICENSE"), read("README.md")
    check_citation(good, lic, readme)
    for key in REQUIRED:
        broken = copy.deepcopy(good)
        del broken[key]
        assertion_from(lambda b=broken: check_citation(b, lic, readme), f"key {key} removed")
        emptied = copy.deepcopy(good)
        emptied[key] = ""
        assertion_from(lambda b=emptied: check_citation(b, lic, readme), f"key {key} emptied")
    edits = (("cff-version", "1.1.0"), ("title", "Third of a percent"), ("license", "Apache-2.0"), ("repository-code", REPOSITORY + "-old"),
             ("url", PAGE.replace("jacobopacheco", "someone")), ("abstract", ABSTRACT.replace("0.30%", "0.3%")),
             ("authors", [{"family-names": "Pacheco", "given-names": "Jacobo"}, {"family-names": "Other", "given-names": "Person"}]),
             ("authors", [{"family-names": "Pacheco", "given-names": "Jacob"}]),
             ("authors", [{"family-names": "Pacheco", "given-names": "Jacobo", "orcid": "https://orcid.org/0000-0000-0000-0000"}]),
             ("version", "1.0.0"), ("doi", "10.0000/none"), ("date-released", "2026-10-29"))
    for key, value in edits:
        broken = copy.deepcopy(good)
        broken[key] = value
        assertion_from(lambda b=broken: check_citation(b, lic, readme), f"{key} set to {value!r}")
    assertion_from(lambda: check_citation(good, lic.replace("Jacobo Pacheco", "Someone Else"), readme), "LICENSE holder changed")
    assertion_from(lambda: check_citation(good, lic.replace("MIT License", "Some Licence", 1), readme), "LICENSE text changed")
    assertion_from(lambda: check_citation(good, lic, readme.replace(PAGE, "")), "README no longer names the page")


def test_the_licence_holder_reader_needs_a_copyright_line():
    assertion_from(lambda: license_holder("MIT License\n\nNo year here\n"), "a LICENSE without a copyright line")


def cff_author(cff_text):
    """'Pacheco, Jacobo' (BibTeX's family-name-first form) from the family-names and given-names lines of CITATION.cff."""
    fam = re.search(r'^\s*-?\s*family-names:\s*"([^"]+)"\s*$', cff_text, re.M)
    giv = re.search(r'^\s*-?\s*given-names:\s*"([^"]+)"\s*$', cff_text, re.M)
    assert fam and giv, "CITATION.cff has no family-names and given-names lines"
    return f"{fam.group(1)}, {giv.group(1)}"


def check_bibtex_author(app_text, cff_text):
    """The page's BibTeX (site/app.js, the text of #cmd-cite) names the author the way CITATION.cff does, family name first."""
    found = re.findall(r"^\s*author\s*=\s*\{([^}]*)\},?\s*$", app_text, re.M)
    assert len(found) == 1, f"site/app.js has {len(found)} BibTeX author lines, not one"
    assert found[0] == cff_author(cff_text), f"the BibTeX author is {found[0]!r}; CITATION.cff names {cff_author(cff_text)!r}"


def test_the_page_bibtex_author_is_the_citation_cff_author():
    check_bibtex_author(read("site/app.js"), read("CITATION.cff"))
    assert cff_author(read("CITATION.cff")) == "Pacheco, Jacobo"


def test_a_changed_bibtex_author_is_caught():
    app, cff = read("site/app.js"), read("CITATION.cff")
    check_bibtex_author(app, cff)
    assertion_from(lambda: check_bibtex_author(app.replace("author = {Pacheco, Jacobo},", "author = {JacoboPacheco},"), cff), "the old one-word author")
    assertion_from(lambda: check_bibtex_author(app.replace("author = {Pacheco, Jacobo},", "author = {Jacobo Pacheco},"), cff), "given name first")
    assertion_from(lambda: check_bibtex_author(app.replace("author = {Pacheco, Jacobo},", ""), cff), "no author line")
    assertion_from(lambda: check_bibtex_author(app, cff.replace('family-names: "Pacheco"', 'family-names: "Someone"')), "CITATION.cff author changed")
