#!/usr/bin/env bash
# Fetches the pinned inputs of the json_parse program and checks every download's sha256.
#   nlohmann/json v3.11.3 (tag commit 9cca280a4d0ccf0c08f47a99aa71d1b0e52f8d03): the single header json.hpp
#     from the release assets
#   twitter.json from simdjson v3.10.1 (tag commit e341c8b43861b43de29c48ab65f292d997096953): the parsed input
# Usage: programs/json_parse/fetch.sh [dest]   (default: build/deps/json_parse)
# A hash mismatch stops with a non-zero exit; nothing is built from an unchecked file.
set -euo pipefail
DEST="${1:-build/deps/json_parse}"
mkdir -p "$DEST"
cd "$DEST"

fetch() {  # url file sha256
  curl -fsSL --retry 3 -o "$2" "$1"
  echo "$3  $2" | sha256sum -c -
  echo "$3  $(stat -c %s "$2")  $2  $1" >> MANIFEST
}

: > MANIFEST
fetch https://github.com/nlohmann/json/releases/download/v3.11.3/json.hpp json.hpp \
  9bea4c8066ef4a1c206b2be5a36302f8926f7fdc6087af5d20b417d0cf103ea6
fetch https://raw.githubusercontent.com/simdjson/simdjson/v3.10.1/jsonexamples/twitter.json twitter.json \
  30721e496a8d73cfc50658923c34eb2c0fbe15ee6835005e43ee624d8dedf200
cat MANIFEST
