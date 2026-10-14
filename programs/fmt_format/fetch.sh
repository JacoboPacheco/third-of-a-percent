#!/usr/bin/env bash
# Fetches the pinned source of the fmt_format program and checks the download's sha256.
#   {fmt} 11.0.2 (tag commit 0c9fce2ffefecfdce794e1859584e25877b7b592): the source archive of the tag,
#     used header-only (FMT_HEADER_ONLY), so only include/ is needed
# The program's input is generated inside it from a fixed seed; harness/run.py hashes that input
# (fmt_format <count> 1 <dump-file>) so results.json carries an input_sha256 like any other program.
# Usage: programs/fmt_format/fetch.sh [dest]   (default: build/deps/fmt_format)
set -euo pipefail
DEST="${1:-build/deps/fmt_format}"
mkdir -p "$DEST"
cd "$DEST"

fetch() {  # url file sha256
  curl -fsSL --retry 3 -o "$2" "$1"
  echo "$3  $2" | sha256sum -c -
  echo "$3  $(stat -c %s "$2")  $2  $1" >> MANIFEST
}

: > MANIFEST
fetch https://github.com/fmtlib/fmt/archive/refs/tags/11.0.2.tar.gz fmt-11.0.2.tar.gz \
  6cb1e6d37bdcb756dbbe59be438790db409cdb4868c66e888d5df9f13f7c027f
rm -rf fmt
mkdir fmt
tar -xzf fmt-11.0.2.tar.gz -C fmt --strip-components=1
test -f fmt/include/fmt/format.h
cat MANIFEST
