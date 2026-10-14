#!/usr/bin/env python3
"""Creates one Compiler Explorer short link per loop: clang 18.1 x86-64 -O2 with libc++, two compiler
panes side by side (hardening NONE and FAST), the loop function alone as the source.

    python ce-sweep/make_links.py          # 8 POSTs to /api/shortener, then 8 GETs to check each link

The public shortener needs no account or key. Answers go to ce-sweep/permalinks.json; links already
there are not created again.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cesweep as cs  # noqa: E402
import sweep  # noqa: E402

OUT = os.path.join(cs.HERE, "permalinks.json")
COMPILER = "clang1810"
BASE = "-O2 -march=x86-64 -stdlib=libc++ -D_LIBCPP_HARDENING_MODE="
FILTERS = {"binary": False, "commentOnly": True, "demangle": True, "directives": True, "intel": True,
           "labels": True, "libraryCode": True, "trim": False, "execute": False}


def client_state(source):
    return {"sessions": [{
        "id": 1, "language": "c++", "source": source,
        "compilers": [{"id": COMPILER, "options": BASE + "_LIBCPP_HARDENING_MODE_NONE", "filters": FILTERS,
                       "libs": [], "specialoutputs": [], "tools": []},
                      {"id": COMPILER, "options": BASE + "_LIBCPP_HARDENING_MODE_FAST", "filters": FILTERS,
                       "libs": [], "specialoutputs": [], "tools": []}],
        "executors": []}]}


def get_json(url):
    time.sleep(sweep.MIN_GAP)
    req = urllib.request.Request(url, headers={"User-Agent": sweep.UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    links = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            links = json.load(f)["links"]
    for k in cs.KERNELS:
        if k in links and links[k].get("verified"):
            continue
        src = cs.single_kernel_source(None, k)
        if k not in links:
            try:
                resp = sweep.post("/shortener", client_state(src))
            except sweep.Stop as e:
                print(e)
                break
            links[k] = {"url": resp.get("url"), "compiler": COMPILER,
                        "options_none": BASE + "_LIBCPP_HARDENING_MODE_NONE",
                        "options_fast": BASE + "_LIBCPP_HARDENING_MODE_FAST", "source": src, "verified": False}
        # Read the link back: the stored source and both option strings must be what was sent.
        lid = links[k]["url"].rstrip("/").rsplit("/", 1)[-1]
        info = get_json("https://godbolt.org/api/shortlinkinfo/" + lid)
        sess = (info.get("sessions") or [{}])[0]
        opts = sorted(c.get("options", "") for c in sess.get("compilers", []))
        links[k]["verified"] = (sess.get("source") == src and
                                opts == sorted([links[k]["options_none"], links[k]["options_fast"]]))
        print(k, links[k]["url"], "verified" if links[k]["verified"] else "NOT VERIFIED")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"what": "Compiler Explorer short links, clang 18.1.0 x86-64 -O2 libc++, NONE and FAST panes",
                   "links": links}, f, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
