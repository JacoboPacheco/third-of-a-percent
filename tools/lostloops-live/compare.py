"""Compares a lostloops report.json with the census's expected lists (PLAN.md, "What counts as PASS").

compare(report, expected, root, outside) -> {"pass": bool, "lists": [...], "details": [...],
"checks": [...], "totals": [...]}, each a list of human-readable differences (empty when equal).
No tolerance: any difference fails.
"""
import collections
import posixpath

CHECK_STATUS = {"check traced to the loop": "checked container access in the loop",
                "no check traced to the loop": "no trap attributed to this loop"}
TOTALS = (("files_in_input", "translation_units"), ("files_compiled", "compiled"),
          ("vectorized_none", "vectorized_none"), ("vectorized_hardened", "vectorized_hardened"),
          ("traps_added", "traps_added"), ("text_bytes_none", "text_bytes_none"),
          ("text_bytes_hardened", "text_bytes_hardened"))


def canon(entry, root, outside):
    """The tool's entry in the census's naming: (tu, function, file, line, column, origin).
    The census calls a file outside the project root but inside the fetched sources (`../fmt-x/..`)
    'project' with a root-relative path; the tool calls it 'system' with an absolute path. The
    census's _census_driver/ files are origin 'driver'; the tool has no such origin."""
    file, origin = entry["file"], entry["origin"]
    if origin == "system" and file.startswith("/") and any(file.startswith(o.rstrip("/") + "/") for o in outside):
        file, origin = posixpath.relpath(file, root), "project"
    if origin == "project" and file.startswith("_census_driver/"):
        origin = "driver"
    return (entry["tu"], entry["function"], file, entry["line"], entry["column"], origin)


def _short(k):
    return "%s %s:%d:%d (%s) in %s" % (k[0], k[2], k[3], k[4], k[5], k[1][:80])


def _count(entries, f):
    c = collections.Counter()
    for e in entries:
        c[f(e)] += e["count"]
    return c


def compare(report, expected, root, outside=()):
    out = {"lists": [], "details": [], "checks": [], "totals": []}
    t = report["totals"]
    for mine, theirs in TOTALS:
        if t.get(mine) != expected[theirs]:
            out["totals"].append("%s: tool %r, census %r" % (mine, t.get(mine), expected[theirs]))
    for kind in ("lost", "moved", "gained"):
        mine_e = report[kind]
        theirs_e = expected[kind]
        a = _count(mine_e, lambda e: canon(e, root, outside))
        b = _count(theirs_e, lambda e: (e["tu"], e["function"], e["file"], e["line"], e["column"], e["origin"]))
        for k in sorted(set(a) | set(b)):
            if a[k] != b[k]:
                out["lists"].append("%s: tool %d, census %d: %s" % (kind, a[k], b[k], _short(k)))
        if kind == "gained":
            continue
        # per-entry details, for the entries both have
        mine_by = {canon(e, root, outside): e for e in mine_e}
        for ex in theirs_e:
            k = (ex["tu"], ex["function"], ex["file"], ex["line"], ex["column"], ex["origin"])
            m = mine_by.get(k)
            if m is None:
                continue
            for f in ("class", "detail", "source_line"):
                if m[f] != ex[f]:
                    out["details"].append("%s %s: %s differs: tool %r, census %r" % (kind, _short(k), f, m[f], ex[f]))
            if sorted(m["hardened_remarks"]) != sorted(ex["hardened_remarks"]):
                out["details"].append("%s %s: hardened remarks differ: tool %r, census %r" % (
                    kind, _short(k), m["hardened_remarks"], ex["hardened_remarks"]))
            if kind == "lost" and "check" in ex:
                c = m.get("check", {})
                got = (CHECK_STATUS.get(c.get("status"), c.get("status")), sorted(c.get("messages", [])),
                       c.get("attributed_checks"))
                want = (ex["check"]["status"], sorted(ex["check"]["messages"]), ex["check"]["attributed"])
                if got != want:
                    out["checks"].append("%s: tool %r, census %r" % (_short(k), got, want))
    out["pass"] = not any(out[k] for k in ("lists", "details", "checks", "totals"))
    return out
