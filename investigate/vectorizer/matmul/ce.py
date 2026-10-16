"""Cached client for the Compiler Explorer compile API (https://godbolt.org/api).

Every call is saved to raw/<name>.json (or .json.gz for optimizer-pipeline requests) together with the
exact request, so the answer can be read without the network and the request can be sent again.
A saved name is never fetched twice. The total number of requests is capped (requests.tsv counts them).

    python ce.py --list          # what is saved
"""
import gzip
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://godbolt.org/api"
UA = ("third-of-a-percent-investigate/1.0 (research project; compile-only study of libc++ hardening "
      "and loop vectorization)")
RAW = os.path.join(HERE, "raw")
LOG = os.path.join(HERE, "requests.tsv")
MIN_GAP = 1.5
MAX_REQUESTS = 120
_last = [0.0]

# Same display filters as ce-sweep/cesweep.py, so the assembly reads the same way.
FILTERS = {"binary": False, "binaryObject": False, "commentOnly": True, "demangle": True, "directives": True,
           "execute": False, "intel": True, "labels": True, "libraryCode": True, "trim": False,
           "debugCalls": False}


def read_source(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return f.read()


def request_body(source, args, opt_pipeline=False, filters=None):
    copts = {"skipAsm": False, "executorRequest": False}
    if opt_pipeline:
        copts["produceOptPipeline"] = True
    return {"source": source, "lang": "c++", "allowStoreCodeDebug": True,
            "options": {"userArguments": args, "compilerOptions": copts, "filters": filters or FILTERS,
                        "tools": [], "libraries": []}}


def sha(compiler_id, body):
    blob = json.dumps({"compiler": compiler_id, "body": body}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def path_for(name, opt_pipeline):
    return os.path.join(RAW, name + (".json.gz" if opt_pipeline else ".json"))


def load(name):
    """The saved record for `name`, or None."""
    for p, opener in ((os.path.join(RAW, name + ".json"), open), (os.path.join(RAW, name + ".json.gz"), gzip.open)):
        if os.path.exists(p):
            with opener(p, "rt", encoding="utf-8") as f:
                return json.load(f)
    return None


def requests_used():
    if not os.path.exists(LOG):
        return 0
    with open(LOG, encoding="utf-8") as f:
        return sum(1 for ln in f if ln.strip())


def _log(kind, name, status):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("%s\t%s\t%s\t%s\n" % (datetime.now(timezone.utc).isoformat(timespec="seconds"), kind, name, status))


def _post(url, body):
    wait = MIN_GAP - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"User-Agent": UA, "Content-Type": "application/json",
                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
            status = r.status
    except urllib.error.HTTPError as e:
        _last[0] = time.time()
        raise RuntimeError("HTTP %d from %s" % (e.code, url))
    _last[0] = time.time()
    return status, json.loads(data.decode("utf-8"))


def compile_(name, compiler_id, source_rel, args, opt_pipeline=False, filters=None):
    """Compile `source_rel` with `args` on `compiler_id`; saved under `name`. Returns the saved record."""
    rec = load(name)
    source = read_source(source_rel)
    body = request_body(source, args, opt_pipeline, filters)
    want = sha(compiler_id, body)
    if rec is not None:
        if rec["request_sha256"] != want:
            raise RuntimeError("%s: saved answer was made from a different request (source or options changed)" % name)
        return rec
    if requests_used() >= MAX_REQUESTS:
        raise RuntimeError("request cap (%d) reached" % MAX_REQUESTS)
    url = API + "/compiler/%s/compile" % compiler_id
    try:
        status, resp = _post(url, body)
    except RuntimeError as e:
        _log("compile", name, str(e))
        raise
    _log("compile", name, status)
    rec = {"name": name, "compiler_id": compiler_id, "source_file": source_rel, "url": url, "request": body,
           "request_sha256": want, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "response": resp}
    os.makedirs(RAW, exist_ok=True)
    p = path_for(name, opt_pipeline)
    opener = gzip.open if p.endswith(".gz") else open
    with opener(p, "wt", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    return rec


def stderr_text(rec):
    import re
    ansi = re.compile(r"\x1b\[[0-9;]*m")
    return "\n".join(ansi.sub("", x.get("text", "")) for x in (rec["response"].get("stderr") or []))


def asm_text(rec):
    return "\n".join(x.get("text", "") for x in (rec["response"].get("asm") or []))


if __name__ == "__main__":
    if "--list" in sys.argv:
        for fn in sorted(os.listdir(RAW)):
            print(fn)
        print("requests used:", requests_used())
