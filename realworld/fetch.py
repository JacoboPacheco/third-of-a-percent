#!/usr/bin/env python3
"""Downloads the pinned archives of the real programs (realworld/programs.json), checks each sha256
and size, extracts them and writes the generated headers the census also generated.

Usage: python3 realworld/fetch.py <deps dir> <program> [<program> ...]
Layout: <deps>/<program>/<archive root>/..., so a '../<dir>' include of a program points at another
download of the same program. Writes <deps>/MANIFEST (sha256, bytes, file, url per download).
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_programs():
    with open(os.path.join(HERE, "programs.json"), encoding="utf-8") as f:
        return json.load(f)


def generate(root, gen):
    """The census 'generate' block: write 'content' as is, or 'from' a template with 'replace'."""
    for rel, spec in sorted(gen.items()):
        path = os.path.normpath(os.path.join(root, rel))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if "content" in spec:
            text = spec["content"]
        else:
            with open(os.path.normpath(os.path.join(root, spec["from"])), encoding="utf-8") as f:
                text = f.read()
            for a, b in spec.get("replace", {}).items():
                text = text.replace(a, b)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


def fetch_program(name, prog, deps, manifest):
    dest = os.path.join(deps, name)
    os.makedirs(dest, exist_ok=True)
    for d in prog["downloads"]:
        path = os.path.join(dest, d["file"])
        if not (os.path.exists(path) and sha256(path) == d["sha256"]):
            subprocess.run(["curl", "-fsSL", "--retry", "4", "--retry-delay", "3", "-o", path, d["url"]], check=True)
        got = sha256(path)
        size = os.path.getsize(path)
        if got != d["sha256"] or size != d["bytes"]:
            raise SystemExit(f"{name}: {d['file']} sha256 {got} ({size} bytes), expected {d['sha256']} ({d['bytes']} bytes)")
        manifest.append(f"{got}  {size}  {name}/{d['file']}  {d['url']}")
        subprocess.run(["tar", "-xzf", path, "-C", dest], check=True)
    root = os.path.join(dest, prog["root"])
    if not os.path.isdir(root):
        raise SystemExit(f"{name}: root {prog['root']} not found after extraction")
    generate(root, prog.get("generate") or {})
    return root


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    deps = os.path.abspath(argv[1])
    doc = load_programs()
    manifest = []
    for name in argv[2:]:
        fetch_program(name, doc["programs"][name], deps, manifest)
    with open(os.path.join(deps, "MANIFEST"), "a", encoding="utf-8") as f:
        f.write("\n".join(manifest) + "\n")
    print("\n".join(manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
