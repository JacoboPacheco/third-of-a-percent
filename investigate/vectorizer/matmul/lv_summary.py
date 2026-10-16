"""Short summary of a saved -debug-only=loop-vectorize answer (offline)."""
import re
import sys

import ce

KEEP = re.compile(r"(Not vectorizing|Cannot|cannot|early exit|Early exit|uncountable|multiple exits|"
                  r"Scalar loop costs|Vector loop of width \d+ costs|Selecting VF|not beneficial|"
                  r"We can vectorize|Found trip count|Loop cost is|IC is|VF is|Vectorizing:|remark:|"
                  r"Loop hints|Found a loop|Checking a loop)")
CMPS = re.compile(r"%cmp\.i\d+ = icmp ugt")


def summarize(name, width=230):
    rec = ce.load(name)
    text = ce.stderr_text(rec)
    out = ["== %s (%s, %s)" % (name, rec["compiler_id"], rec["fetched_at"])]
    seen = set()
    for ln in text.splitlines():
        if KEEP.search(ln):
            key = ln[:100]
            if key in seen and "Found a loop" not in ln:
                continue
            seen.add(key)
            out.append("   " + ln[:width])
        elif "uniform instruction" in ln and CMPS.search(ln):
            out.append("   " + ln[:width])
        elif re.search(r"Found an estimated cost of \d+ for VF 4 For instruction:\s+%cmp\.i\d+ = icmp ugt", ln):
            out.append("   " + ln[:width])
    return "\n".join(out)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        print(summarize(n))
