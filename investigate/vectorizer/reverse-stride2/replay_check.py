"""Replays, offline, the rebuild of raw/ from nothing, and checks that the saved answers cover it.

    python replay_check.py

A copy of this folder without raw/, sources/ir/ and extracted/ is made in a temporary directory. Then the
steps of the README ("Reproduce") run there with the network replaced by the saved answers, looked up by the
hash of the request:

    python fetch.py   ->  python extract.py ir   ->  python fetch.py   ->  python fetch.py   ->  python fetch.py

It prints how many requests each `fetch.py` run sent, and exits with 1 when a request has no saved answer, when
the last run still sends something, or when the rebuilt raw/ differs from the saved one (names and responses).
No request leaves the machine.
"""
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def child(work, orig, stage):
    """Runs one step inside the copy, with ce._http answering from the saved answers."""
    sys.path.insert(0, work)
    os.chdir(work)
    import ce
    by_sha, by_url = {}, {}
    for f in os.listdir(orig):
        rec = load(os.path.join(orig, f))
        if "request_sha256" in rec:
            by_sha[rec["request_sha256"]] = rec
        else:
            by_url[rec["url"]] = rec
    count = []

    def replay(method, url, body=None):
        if method == "GET":
            count.append(url)
            return 200, by_url[url]["response"]
        compiler = url.rsplit("/compile", 1)[0].rsplit("/", 1)[1]
        sha = ce.request_sha(compiler, body)
        if sha not in by_sha:
            print("NO SAVED ANSWER for a request to %s (hash %s)" % (compiler, sha[:12]))
            sys.exit(1)
        count.append(sha)
        return 200, by_sha[sha]["response"]

    ce._http = replay
    ce.MIN_GAP = 0
    import extract
    import fetch
    if stage == "fetch":
        sys.argv = ["fetch.py"]
        fetch.main()
        print("REQUESTS %d" % len(count))
    else:
        extract.write_ir()


def main():
    orig = os.path.join(HERE, "raw")
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "work")
        shutil.copytree(HERE, work, ignore=shutil.ignore_patterns("raw", "extracted", "ir", "__pycache__",
                                                                  "request-index.json"))
        sent = []
        for stage in ("fetch", "extract", "fetch", "fetch", "fetch"):
            r = subprocess.run([sys.executable, os.path.join(work, "replay_check.py"), "--child", work, orig, stage],
                               capture_output=True, text=True, cwd=work)
            if r.returncode != 0:
                print(r.stdout + r.stderr)
                print("FAIL replay step %s" % stage)
                return 1
            if stage == "fetch":
                sent.append(int(r.stdout.split("REQUESTS ")[1].split()[0]))
        print("requests per fetch.py run: %s" % sent)
        if sent[-1] != 0:
            print("FAIL the last fetch.py run still sends requests")
            return 1
        new = os.path.join(work, "raw")
        a, b = sorted(os.listdir(orig)), sorted(os.listdir(new))
        if a != b:
            print("FAIL raw/ differs: only saved %s, only rebuilt %s" % (sorted(set(a) - set(b)), sorted(set(b) - set(a))))
            return 1
        for f in a:
            if load(os.path.join(orig, f))["response"] != load(os.path.join(new, f))["response"]:
                print("FAIL response differs: %s" % f)
                return 1
        print("rebuilt %d answers, all equal to the saved ones" % len(a))
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        child(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        sys.exit(main())
