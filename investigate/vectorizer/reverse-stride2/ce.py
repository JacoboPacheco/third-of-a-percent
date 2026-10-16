"""Minimal Compiler Explorer client for this folder: one request at a time, every answer saved to raw/.

    ce.compile(name, compiler_id, source_path, args, ...)  -> saved raw/<name>.json, returns the record
    ce.get(name, path)                                      -> saved raw/<name>.json for a GET request

A request is sent only when raw/<name>.json is missing, or when the stored request differs from
the one asked for. Otherwise the saved answer is read back (no network). Requests are at least
1.5 s apart. HTTP 429, 401 and 403 stop the run. Python standard library only.
"""
import gzip
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
API = "https://godbolt.org/api"
UA = 'third-of-a-percent-vectorizer-notes/1.0 (research project "Third of a Percent": compile-only notes)'
NL = chr(10)
MIN_GAP = 1.5
MAX_REQUESTS = 120
_state = {"last": 0.0, "sent": 0}

# Compiler Explorer's stock filters (as used by ce-sweep/cesweep.py), asm in AT&T order off, no binary.
FILTERS = {"binary": False, "binaryObject": False, "commentOnly": True, "demangle": True,
           "directives": True, "execute": False, "intel": True, "labels": True,
           "libraryCode": True, "trim": False, "debugCalls": False}


class Stop(Exception):
    pass


def _sleep_gap():
    wait = MIN_GAP - (time.time() - _state["last"])
    if wait > 0:
        time.sleep(wait)


def _http(method, url, body=None):
    if _state["sent"] >= MAX_REQUESTS:
        raise Stop("request cap of %d reached" % MAX_REQUESTS)
    _sleep_gap()
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    status = None
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            status = r.status
            payload = r.read()
    except urllib.error.HTTPError as e:
        status = e.code
        if e.code in (429, 401, 403):
            raise Stop("HTTP %d from %s (stopping)" % (e.code, url))
        raise
    finally:
        _state["last"] = time.time()
        _state["sent"] += 1
    return status, json.loads(payload.decode("utf-8"))


def _path(name):
    """raw/<name>.json, or raw/<name>.json.gz when the answer is large (over 1 MB as JSON)."""
    plain = os.path.join(RAW, name + ".json")
    return plain if os.path.exists(plain) or not os.path.exists(plain + ".gz") else plain + ".gz"


def _load(name):
    p = _path(name)
    if not os.path.exists(p):
        return None
    opener = gzip.open if p.endswith(".gz") else open
    with opener(p, "rt", encoding="utf-8") as f:
        return json.load(f)


def _save(name, rec):
    os.makedirs(RAW, exist_ok=True)
    text = json.dumps(rec, indent=1, sort_keys=True, ensure_ascii=False) + NL
    plain = os.path.join(RAW, name + ".json")
    for stale in (plain, plain + ".gz"):
        if os.path.exists(stale):
            os.remove(stale)
    if len(text) > 1000000:
        with gzip.GzipFile(plain + ".gz", "wb", compresslevel=9, mtime=0) as f:
            f.write(text.encode("utf-8"))
    else:
        with open(plain, "w", encoding="utf-8", newline=NL) as f:
            f.write(text)


def request_body(source, args, compiler_options=None, filters=None, lang="c++"):
    co = {"skipAsm": False, "executorRequest": False}
    co.update(compiler_options or {})
    return {"source": source, "lang": lang, "allowStoreCodeDebug": True,
            "options": {"userArguments": args, "compilerOptions": co,
                        "filters": filters or FILTERS, "tools": [], "libraries": []}}


def request_sha(compiler_id, body):
    blob = json.dumps({"compiler": compiler_id, "body": body}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def load(name):
    """A saved raw/<name>.json (never sends a request)."""
    rec = _load(name)
    if rec is None:
        raise FileNotFoundError(name)
    return rec


def _log_request(name, kind, status):
    p = os.path.join(HERE, "request-index.json")
    idx = []
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            idx = json.load(f)
    idx.append({"n": len(idx) + 1, "name": name, "kind": kind, "http_status": status,
                "time": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    with open(p, "w", encoding="utf-8", newline=NL) as f:
        json.dump(idx, f, indent=1)
        f.write(NL)


def compile(name, compiler_id, source_path, args, compiler_options=None, filters=None, retries=2, replace=False,
            lang="c++"):
    """Compile source_path with `args` on Compiler Explorer compiler `compiler_id`; cache as raw/<name>.json.

    A saved answer for the same request is read back. A saved answer for a different request under
    the same name is an error unless replace=True.
    """
    with open(os.path.join(HERE, source_path), encoding="utf-8") as f:
        source = f.read()
    body = request_body(source, args, compiler_options, filters, lang)
    sha = request_sha(compiler_id, body)
    rec = _load(name)
    if rec is not None and rec.get("request_sha256") == sha:
        return rec
    if rec is not None and not replace:
        raise RuntimeError("raw/%s.json holds a different request; pass replace=True to overwrite it" % name)
    url = "%s/compiler/%s/compile" % (API, compiler_id)
    err = None
    for attempt in range(retries + 1):
        try:
            status, resp = _http("POST", url, body)
            break
        except Stop:
            raise
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            err = e
            print("   %s: %s (retry %d)" % (name, e, attempt + 1))
            time.sleep(20)
    else:
        raise RuntimeError("%s failed: %s" % (name, err))
    rec = {"name": name, "compiler_id": compiler_id, "url": url, "source_path": source_path,
           "user_arguments": args, "compiler_options": compiler_options or {},
           "request_sha256": sha, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "http_status": status, "request_body": body, "response": resp}
    _save(name, rec)
    _log_request(name, "compile", status)
    return rec


def get(name, path):
    """GET API + path (a listing), cached as raw/<name>.json."""
    rec = _load(name)
    if rec is not None and rec.get("path") == path:
        return rec
    url = API + path
    status, resp = _http("GET", url)
    rec = {"name": name, "url": url, "path": path,
           "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "http_status": status, "response": resp}
    _save(name, rec)
    _log_request(name, "get", status)
    return rec


ANSI = re.compile(r"\x1b\[[0-9;]*m")


def stderr_text(rec):
    """The compiler's stderr as plain text."""
    return "\n".join(ANSI.sub("", x.get("text", "")) for x in (rec["response"].get("stderr") or []))


def stdout_text(rec):
    return "\n".join(ANSI.sub("", x.get("text", "")) for x in (rec["response"].get("stdout") or []))


def asm_text(rec):
    return "\n".join(x.get("text", "") for x in (rec["response"].get("asm") or []))
