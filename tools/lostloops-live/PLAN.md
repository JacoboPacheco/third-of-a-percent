# lostloops live test: plan (written Tue Oct 13 2026 13:23, before any live run)

`tools/lostloops/` has never been run with a real clang. This test runs it on GitHub Actions
(ubuntu-24.04, clang-18, libc++-18-dev) on three census projects and compares what it finds with
what the census (`corpus/census.py`) stored for the same projects. The census is the reference
because it is a separate implementation (it compiles with its own flags and reads the same kind of
records), it ran twice with byte-identical output, and its answers are committed.

## The three projects (pins from `corpus/projects.json` and `corpus/projects2.json`)

| project | why | census row | commit |
|---|---|---|---|
| leveldb | a general library with exactly 1 lost loop (db/c.cc:117) | census 1, run 38259934735 | bb74ef739973a70ca9f0d90788a1da89b788c0ad |
| spectra | a numeric project with a few (4 lost) | census 2, run 38273183229 | 6841bcbacaa0f0a8446210314e682057a084be4e |
| lightgbm | the largest count (331 lost, 38 locations, 128 copies of one loop) | census 2, run 38273183229 | 8f7036f03627054d5a54a6f965b13f4b9ff2cb63 |

Sources are fetched by `census.py`'s own `fetch` (sha256 checked against the pins), so the tool
sees the same files, including the census's generated headers and drivers. The tool is given a
`compile_commands.json` with an ordinary user command per file (`clang++-18 -O2 -std=... -I... -D...
-c file -o file.o`, no hardening flags, no `-stdlib`, no record flags) and `--root` the project
root. The expected lists are `expected/<project>.json`, written by `make_expected.py` from the
census's `lost_loops.json` and `corpus.json` for that project and nothing else.

## What counts as PASS (per project, all must hold; no tolerance)

1. The lists `lost`, `moved` and `gained` equal the census's as multisets of
   (translation unit, function, file, line, column, origin, count). Origin and file are compared
   after one stated normalisation: a path outside the project root that the census calls
   "project" (`../fmt-.../x.h`) is `system` and absolute in the tool, and the census's `driver`
   origin is `project` in the tool.
2. For each matched entry: class, detail, source line, and the compiler's remarks for the hardened
   build are equal.
3. Totals equal the census project row: translation units, compiled, vectorized loops NONE and
   FAST, `ud2` added, `.text` bytes NONE and FAST.
4. For each lost entry the check trace (status, messages, number of attributed checks) equals the
   census's `index_evidence`. This is reported as its own line, so a difference in tracing is
   told apart from a difference in the lists; it fails the run too.
5. Every translation unit compiled (the census failed none for these projects).

The workflow fails on any difference and prints the first 40. The tool's `report.json`/`report.md`,
the generated compile database and a `comparison.json` are uploaded as an artifact either way.

## What a difference would mean

- Lists differ, totals equal: matching or normalisation bug in the tool (or the census), look at
  the entries.
- Totals differ: the tool compiled something differently (flags cleaned wrongly, a file dropped,
  path resolution). Compare `example_command` in `report.json` with the census's.
- Only the check traces differ: the tool's trace code (`trace_unit`) differs in a real-toolchain
  detail (symbolizer name, link step); the lists are still valid.
- Everything differs on every project: the environment (clang version, libc++ package) is not the
  census's. Check `clang --version` printed by the workflow against 18.1.3.
- Not a difference: a different `clang` patch version that changes the vectorizer. If the numbers
  move on all three by the same kind of amount, the census (not the tool) is stale; say so, do not
  patch the expected files to match.

## Rules for fixes

- No expected file is edited to make a run pass. They are regenerated only from the stored census
  runs, and only by `make_expected.py`.
- A fix to the tool after a failed live run is logged below with the run id, what failed, what was
  changed, and the offline test added. A live run after a fix is a new run, with its own row.
- The README's "NOT tested live" status line changes only after a run with all three PASS, and then
  names the run id and the clang version.

## Found by reading the tool before the first run (Tue Oct 13 2026; offline tests in `tools/lostloops/tests/test_live_support.py`)

- `-flto*` in a user's flags made clang write bitcode, so the vectorizer would not run at compile time and the
  tool would report "nothing lost" silently: the flags are now removed (and listed in the report).
- The newest `clang++-NN` on PATH was taken even without its `libc++-NN-dev` (GitHub's Ubuntu images have
  several clangs): now the newest one whose libc++ works is taken.
- A timeout or `OSError` in the traced rebuild escaped and ended the run with exit 1 after every file was
  compiled: now the entries say "not traced (...)". The traced rebuilds also ran one after the other; they
  now run in parallel (`--jobs`). `--timeout` sets the per-compile limit (it was fixed at 1800 s).
- Not changed, noted: `@response-file` arguments are not expanded; `objdump -d` of each object runs one
  after the other; the tool names a header outside `--root` `system` with an absolute path (the census
  calls `../fmt-x/...` `project`), which `compare.py` maps for the comparison only.

## Run log

| run id | date | clang | leveldb | spectra | lightgbm | what was changed afterwards |
|---|---|---|---|---|---|---|
| 38438713384 | Tue Oct 13 2026 | Ubuntu clang 18.1.3 | PASS | PASS | PASS | nothing: the first live run matched the census exactly on all three projects, with no change to the tool or the expected lists (artifacts in `results/lostloops-live-38438713384/`) |
