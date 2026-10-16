"""Sends every experiment of experiments.py whose answer is not yet in raw/ (one request at a time, 1.5 s apart).

    python fetch.py                  # everything missing
    python fetch.py --only A-c18     # names starting with A-c18 (the two compiler listings: names starting with compilers-)
    python fetch.py --dry-run        # list what would be sent
"""
import argparse
import os
import sys

import ce
import experiments


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated name prefixes")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    prefixes = a.only.split(",") if a.only else None
    sent = 0
    for e in experiments.all_experiments():
        if prefixes and not any(e["name"].startswith(p) for p in prefixes):
            continue
        have = os.path.exists(ce._path(e["name"]))
        if a.dry_run:
            print("%-40s %s %s" % (e["name"], "saved" if have else "TO SEND", e["compiler_id"]))
            continue
        before = ce._state["sent"]
        try:
            rec = ce.compile(e["name"], e["compiler_id"], e["source_path"], e["args"], e["compiler_options"],
                             filters=e.get("filters"), lang=e.get("lang", "c++"))
        except ce.Stop as ex:
            print(ex)
            return 3
        if ce._state["sent"] > before:
            sent += 1
            r = rec["response"]
            print("sent %-38s code=%s asm=%d stderr=%d" % (e["name"], r.get("code"), len(r.get("asm") or []),
                                                        len(ce.stderr_text(rec))))
    for name, path in experiments.LISTINGS:
        if prefixes and not any(name.startswith(p) for p in prefixes):
            continue
        have = os.path.exists(ce._path(name))
        if a.dry_run:
            print("%-40s %s listing %s" % (name, "saved" if have else "TO SEND", path))
            continue
        before = ce._state["sent"]
        try:
            ce.get(name, path)
        except ce.Stop as ex:
            print(ex)
            return 3
        if ce._state["sent"] > before:
            sent += 1
            print("sent %-38s listing" % name)
    print("sent %d requests" % sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
