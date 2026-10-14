#!/usr/bin/env python3
"""A stand-in for clang++ in the tests: it compiles nothing.

It answers --version like clang 18, passes the libc++ probe (unless FAKE_CLANG_NO_LIBCXX is set),
and for a compile writes the canned optimization record of the census's real build:
$FAKE_CLANG_DATA/<source file name>.<none|fast>.opt.yaml[.gz], picked by the source's name and the
-D_LIBCPP_HARDENING_MODE flag. It writes an empty object file. Each call's arguments are appended
as one JSON file in the folder $FAKE_CLANG_LOG when that is set (one file per call, since calls run in
parallel), so a test can check the exact flags.
"""
import gzip
import json
import os
import re
import sys
import uuid

args = sys.argv[1:]
log = os.environ.get("FAKE_CLANG_LOG")
if log:
    with open(os.path.join(log, uuid.uuid4().hex + ".json"), "w", encoding="utf-8") as f:
        json.dump({"args": args, "cwd": os.getcwd().replace("\\", "/")}, f)

if "--version" in args:
    print("Ubuntu clang version 18.1.3 (fake for tests)\nTarget: x86_64-pc-linux-gnu")
    sys.exit(0)
if "-fsyntax-only" in args:
    sys.stdin.read()
    if os.environ.get("FAKE_CLANG_NO_LIBCXX"):
        print("<stdin>:1:10: fatal error: 'version' file not found", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)

mode = record = obj = src = None
for i, a in enumerate(args):
    m = re.match(r"-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_(\w+)$", a)
    if m:
        mode = m.group(1).lower()
    if a.startswith("-foptimization-record-file="):
        record = a.split("=", 1)[1]
    if a == "-o":
        obj = args[i + 1]
    if not a.startswith("-") and re.search(r"\.(cc|cpp|cxx)$", a) and (i == 0 or args[i - 1] != "-o"):
        src = a
if not (mode and record and obj and src):
    print("fake clang: cannot read this command: %r" % args, file=sys.stderr)
    sys.exit(3)
if mode == "fail":
    print("error: told to fail", file=sys.stderr)
    sys.exit(1)
data_dir = os.environ["FAKE_CLANG_DATA"]
name = os.path.basename(src)
want = "fast" if mode != "none" else "none"
for ext, opener in ((".opt.yaml", open), (".opt.yaml.gz", gzip.open)):
    p = os.path.join(data_dir, "%s.%s%s" % (name, want, ext))
    if os.path.exists(p):
        with opener(p, "rb") as f:
            data = f.read()
        break
else:
    print("%s:1:1: error: no canned record for %s (%s)" % (src, name, want), file=sys.stderr)
    sys.exit(1)
with open(record, "wb") as f:
    f.write(data)
with open(obj, "wb") as f:
    f.write(b"")
sys.exit(0)
