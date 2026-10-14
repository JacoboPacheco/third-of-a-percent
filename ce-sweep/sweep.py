#!/usr/bin/env python3
"""Sends the sweep's compile requests to Compiler Explorer's public API and caches every answer.

    python ce-sweep/sweep.py              # every build not yet in ce-sweep/cache/
    python ce-sweep/sweep.py --only clang1810 --dry-run

Polite by construction: one request at a time, at least 1.2 s apart, a User-Agent naming this
research project, a hard cap on requests per run, and a full stop on HTTP 429 or any 403
(the cache keeps everything already fetched, so a later run resumes). Nothing secret is sent: the
source is the 8 open loop functions of kernels/.

Then `python ce-sweep/build_results.py` turns the cache into results.json and the README matrix.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cesweep as cs  # noqa: E402

API = "https://godbolt.org/api"
UA = ("third-of-a-percent-ce-sweep/1.0 (research project \"Third of a Percent\": compile-only study of "
      "libc++ hardening and loop vectorization)")
CACHE = os.path.join(cs.HERE, "cache")
MIN_GAP = 1.2
_last = [0.0]


class Stop(Exception):
    pass


def post(path, body):
    wait = MIN_GAP - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(API + path, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"User-Agent": UA, "Content-Type": "application/json",
                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        if e.code in (429, 403, 401):
            raise Stop("HTTP %d from %s: %s (stopping; retry later)" % (e.code, path, e.headers.get("Retry-After")))
        raise
    finally:
        _last[0] = time.time()
        with open(os.path.join(CACHE, "requests.log"), "a", encoding="utf-8") as log:
            log.write("%s POST %s\n" % (datetime.now(timezone.utc).isoformat(timespec="seconds"), path))
    return json.loads(data.decode("utf-8"))


def post_retrying(path, body, tries=3):
    """Server errors (5xx, timeouts) are retried after 15 s and 45 s; 429/403/401 stop at once."""
    for i in range(tries):
        try:
            return post(path, body)
        except Stop:
            raise
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code < 500:
                raise
            print("   %s; waiting before retry %d" % (e, i + 1))
            if i == tries - 1:
                return None
            time.sleep(15 * (3 ** i))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated compiler ids")
    ap.add_argument("--max", type=int, default=250, help="request cap for this run")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    source = cs.build_source()
    with open(os.path.join(cs.HERE, "source.cpp"), "w", encoding="utf-8", newline="\n") as f:
        f.write(source)
    only = set(a.only.split(",")) if a.only else None
    todo = [b for b in cs.matrix() if (only is None or b["compiler_id"] in only)
            and not os.path.exists(os.path.join(CACHE, cs.cache_name(b)))]
    print("%d builds to fetch (cap %d)" % (len(todo), a.max))
    sent = 0
    for b in todo:
        if sent >= a.max:
            print("cap reached")
            break
        body = cs.request_body(source, b["flags"])
        if a.dry_run:
            print(b["compiler_id"], b["flags"])
            continue
        try:
            resp = post_retrying("/compiler/%s/compile" % b["compiler_id"], body)
        except Stop as e:
            print(e)
            return 3
        sent += 1
        if resp is None:
            print("   skipped %s (server errors)" % cs.cache_name(b))
            continue
        rec = {"build": b, "url": API + "/compiler/%s/compile" % b["compiler_id"],
               "request_sha256": cs.request_sha(b["compiler_id"], body),
               "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "response": {k: resp.get(k) for k in ("code", "stderr", "asm", "compilationOptions", "okToCache")}}
        cs.save_cache(os.path.join(CACHE, cs.cache_name(b)), rec)
        print("%3d %-22s %-10s %s %-8s code=%s asm=%d" % (sent, b["compiler_id"], b["target"], b["opt"], b["mode"],
                                                          resp.get("code"), len(resp.get("asm") or [])))
    print("sent %d requests" % sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
