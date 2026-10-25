"""The GitHub actions the workflows use: which workflows pin them by commit, and that none is added with a moving tag unnoticed.

ci.yml and pages.yml were written with actions pinned to a full commit (the version in a comment). measure.yml, siblings.yml,
dsweep.yml and forwardt.yml, the workflows that produced (or are to produce) the measurements, are pinned to the same commits. The
runs under results/ ran before the pins and used the moving v4 tags. The ten other workflows (the follow-up columns) still use the moving tags and are
listed below by name, so a new workflow with a moving tag fails here until it is pinned or listed on purpose, and a listed one
that has been pinned must come off the list."""
import glob
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = os.path.join(REPO, ".github", "workflows")

PINNED = ("ci.yml", "pages.yml", "measure.yml", "siblings.yml", "dsweep.yml", "forwardt.yml")
MOVING_TAGS = ("corpus.yml", "dayone.yml", "environment.yml", "investigate.yml", "layout-sweep.yml", "lostloops-live.yml",
               "mitigate.yml", "pgo.yml", "realworld.yml", "versions.yml")
# the first-party actions the measurement workflows use, and the commit each is pinned to (version in the trailing comment)
EXPECTED_PINS = {
    "actions/checkout": ("11d5960a326750d5838078e36cf38b85af677262", "v4"),
    "actions/upload-artifact": ("ea165f8d65b6e75b540449e92b4886f43607fa02", "v4.6.2"),
    "actions/download-artifact": ("d3f86a106a0bac45b974a628896c90dbdf5c8093", "v4.3.0"),
}
USES = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<ref>[^\s#]+)(?:\s*#\s*(?P<comment>.*))?$")


def actions(name):
    """[(action, ref, comment)] for every remote action a workflow uses; local actions (./...) are not remote."""
    out = []
    with open(os.path.join(WORKFLOWS, name), encoding="utf-8") as f:
        for line in f:
            m = USES.match(line.rstrip("\n"))
            if m and not m.group("ref").startswith("./"):
                action, _, ref = m.group("ref").partition("@")
                out.append((action, ref, (m.group("comment") or "").strip()))
    return out


def is_commit(ref):
    return re.fullmatch(r"[0-9a-f]{40}", ref) is not None


def test_every_workflow_is_either_pinned_or_listed():
    on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(WORKFLOWS, "*.yml"))}
    assert on_disk == set(PINNED) | set(MOVING_TAGS), (
        f"workflows not placed: {sorted(on_disk - set(PINNED) - set(MOVING_TAGS))}; listed but missing: {sorted((set(PINNED) | set(MOVING_TAGS)) - on_disk)}")


def test_pinned_workflows_use_a_full_commit_and_name_the_version():
    for name in PINNED:
        found = actions(name)
        assert found, f"{name}: no remote action found, the pattern is wrong"
        for action, ref, comment in found:
            assert is_commit(ref), f"{name}: {action}@{ref} is not a full commit"
            assert re.match(r"v\d+(\.\d+)*\b", comment), f"{name}: {action}@{ref[:7]} has no version in its comment ({comment!r})"


def test_the_measurement_workflows_use_the_expected_commits():
    for name in ("measure.yml", "siblings.yml", "dsweep.yml", "forwardt.yml", "ci.yml", "pages.yml"):
        for action, ref, comment in actions(name):
            if action in EXPECTED_PINS:
                sha, version = EXPECTED_PINS[action]
                assert ref == sha, f"{name}: {action} is pinned to {ref[:12]}, not to {sha[:12]} ({version})"
                assert comment.startswith(version), f"{name}: {action} says {comment!r}, expected {version}"


def test_listed_workflows_still_use_a_moving_tag():
    """A workflow that has been pinned must leave the list, so the list never hides a pinned one or a moving one."""
    for name in MOVING_TAGS:
        refs = [ref for _, ref, _ in actions(name)]
        assert refs and not all(is_commit(r) for r in refs), f"{name} is fully pinned: move it to PINNED"


def test_no_first_party_action_of_a_pinned_workflow_floats():
    for name in PINNED:
        assert not [(a, r) for a, r, _ in actions(name) if not is_commit(r)], f"{name}: an action floats on a tag or branch"


def test_the_pin_check_itself_sees_a_floating_tag():
    """Tamper check: a line with a moving tag is read as not pinned, a commit with a version comment as pinned."""
    m = USES.match("      - uses: actions/checkout@v4")
    assert m and not is_commit(m.group("ref").partition("@")[2])
    m = USES.match("      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4")
    assert m and is_commit(m.group("ref").partition("@")[2]) and m.group("comment") == "v4"
    assert USES.match("        uses: ./local-action") is not None
