# lostloops: which of your loops would lose SIMD under libc++ hardening?

**Status: tested live once (Tue Oct 13 2026, GitHub Actions run 38438713384, Ubuntu clang 18.1.3): on leveldb, Spectra and LightGBM its lists matched the census exactly.** That is one run on three projects, not a general guarantee. Everything below the compiler is
tested on saved real compiler output (see "Tests"); the steps to test it live are at the end.

## What it does

1. You point it at your project's `compile_commands.json` (or a list of files and your flags).
2. It compiles each file twice with clang, using your flags as they are: once with libc++'s safety checks off, once with them on.
3. It reads the compiler's own notes on which loops it turned into fast SIMD code in each build.
4. It lists the loops that were fast with the checks off and are no longer fast with them on, with the file and line.
5. For each one it says what shape the loop has, and what fixed that shape in our timed tests.

It times nothing. A loop on the list is a place where turning the checks on *might* cost time;
whether it does depends on how often that loop runs. Time it before you change it.

## Install and run

Linux, with Python 3.8+, clang 18 or newer and libc++ 18 or newer. On Ubuntu 24.04:

```sh
sudo apt install clang-18 libc++-18-dev libc++abi-18-dev binutils llvm-18
```

Copy this folder (`lostloops.py`, `ll_optrecord.py`, `ll_classify.py`, `evidence/`) anywhere. Then:

```sh
# CMake: export the compile commands of your release configuration (no need to build)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
python3 lostloops.py --compile-commands build/compile_commands.json --out lostloops-report

# or a few files with your flags after --
python3 lostloops.py --files src/a.cpp src/b.cpp -- -O2 -std=c++20 -Iinclude
```

Options: `--mode fast|extensive|debug` (default `fast`), `--filter REGEX` (only matching files),
`--root DIR` (what counts as your code), `--add-flag F` (e.g. `-Wno-error`), `--jobs N`,
`--clang clang++-19`, `--timeout SECONDS` (per compile, default 1800), `--no-trace` (skip the extra build that looks for the check inside each lost
loop), `--objdump none`, `--keep-work`. Output: a summary on screen, `report.md` and `report.json`
in `--out`. Exit code 0 when a report was written, whatever it says; 2 when clang, libc++ or the
input is missing (so on Windows or a machine without libc++ it stops with a message); 1 only if the
tool itself breaks. A ready-made GitHub Actions job is in [example-workflow.yml](example-workflow.yml)
(copy it into your repository's `.github/workflows/`; it is not run here).

What it adds to your command, and nothing else: `-stdlib=libc++`,
`-D_LIBCPP_HARDENING_MODE=_LIBCPP_HARDENING_MODE_NONE` (or `_FAST`, `_EXTENSIVE`, `_DEBUG`),
`-fsave-optimization-record -foptimization-record-passes=loop-vectorize
-foptimization-record-file=<temp>` and `-c -o <temp object>`. It removes from your command only what
would clash: `-o`, `-c`, dependency-file flags (`-MD -MF ...`), any other `-stdlib=`, any
`_LIBCPP_HARDENING_MODE` (or old `_LIBCPP_ENABLE_*ASSERTIONS/SAFE/DEBUG_MODE`) define, and any
optimization-record flag of yours, and `-flto*` / `-fwhole-program-vtables` (with LTO clang compiles to
bitcode and the vectorizer runs only at link time, so a compile-only run would see nothing; the report lists what was removed). It never adds `-O2`: if a file's flags have no `-O` level it says
so, because clang then compiles at `-O0`, where nothing is vectorized. The object is written to a
temporary folder (not `/dev/null`) so the check traps and the code size can be counted.

## What the numbers mean, and do not mean

| number | means | does not mean |
|---|---|---|
| vectorized loops (off / on) | loops clang turned into SIMD code, per build, from its own records | how much time they take |
| **lost** | vectorized with the checks off, not with them on, at the same file:line:column in the same function | that your program is slower: a lost loop that rarely runs costs nothing |
| locations | each source line once; a header loop inlined into many functions counts once here, many times in "lost" | |
| gained / moved | vectorized only with the checks on / a loop that left one function and is vectorized in another | |
| check traps added | `ud2` instructions added by hardening (`objdump`) | how often a check runs |
| code size change | `.text` bytes, checks on vs off | run time |
| shape | read from the source text with regular expressions: reverse index, strided, indirect, forward bounded by a variable, other | a proof: check the line yourself |
| check in the loop | a third build traces each libc++ check to its source line; "yes" means a check (e.g. `vector[] index out of bounds`) sits inside the loop | that this check is what stopped the vectorizer (it is the usual reason) |

## Limits

- **Counts, not time.** The tool cannot know how often a loop runs.
- **One compiler, flags as given.** The clang and libc++ on your machine; another version, another `-march`, or GCC's own `_GLIBCXX_ASSERTIONS` can give a different list. The census this is taken from used clang 18.1.3 and libc++ 18 only.
- A file whose flags are for GCC may not compile with clang; it is listed under "Files that did not compile" and left out. Precompiled headers made by another compiler fail the same way. Header code counts only where a compiled file uses it.
- The "what to try" lines come from timed tests of four small kernels on AMD EPYC cloud machines, FAST mode, clang 18 (this project's `mitigate/README.md`). They are starting points, not results for your code.
- The trace of checks into loops needs `objdump` (binutils) and, for the precise path, `llvm-symbolizer` and `ld.bfd`; without them the column says "not traced". It was written for libc++ 18's `<__assertion_handler>` header; a newer libc++ may need a change there.

## What to try, by shape

From `mitigate/README.md` (timed, FAST mode, ratios against the unchecked loop). **Time your own code before and after.**

| shape | what worked in our tests | what did not |
|---|---|---|
| reverse index (`for (i = n; i-- > 0;) c[i] = ...`) | one size check before the loop (`if (c.size() < n) abort();`), or index a `std::span(c).first(n)` taken once: 1.00x on 2 of 3 CPUs, 1.06x to 1.09x on the third | `#pragma clang loop vectorize(enable)` changes nothing; `std::transform` over `rbegin()/rend()` is fast but **unchecked**: libc++ 18 FAST does not check vector iterators |
| strided (`a[2*i]`, `a[2*i+1]`) | `std::span(a).first(2*n)` once plus `#pragma clang loop interleave_count(2)`: 0.96x to 1.03x; or raw `data()` pointers behind one size check (safety rests on that one line) | a size check with `operator[]`: clang 18 cannot prove `2*i+1 < size()`, still about 5x |
| matrix row (`c[i*n + j]`) | raw row pointers behind one check that each matrix holds `n*n` elements: 1.00x | row spans keep every access checked but cost 1.1x to 1.4x in L1; a size check with `operator[]` does nothing |
| indirect (`a[idx[i]]`) | move out what can be moved: one size check (or spans) for the arrays indexed by `i`; cut 1.6x to 1.8x down to about 1.3x in L1 | the check on `a[idx[i]]` stays; clamping or validating the indexes first was slower |
| forward, bounded by a variable (`for (i = 0; i < n; ++i) v[i] = ...`) | not timed for this shape; the reverse-loop rule (one size check before the loop, when the index is the loop counter) is the first thing to try | |
| other | no measured fix | |

## Tests

```sh
python tools/lostloops/run_tests.py
```

No compiler needed. The tests use real optimization records saved by this project's census runs
(`tests/data/records/`, copied from `results/corpus-*/remarks.tar.gz`) and check that the tool's
matching gives exactly the census's `lost_loops.json` entries for spectra (census 2: 79 vectorized,
75 under FAST, 4 lost), leveldb's `db/c.cc` and the 8 kernels; that the ABI-tag mapping is needed
(ninja's `src/dyndep.cc`); and they run the whole tool end to end through `tests/fake_clang.py`, a
stand-in compiler that returns those saved records, checking the exact flags passed. The source
files under `tests/data/src/` are stubs holding only the reported loop at its real line.

## How to test it live

The prepared test is [tools/lostloops-live/](../lostloops-live/PLAN.md): the workflow
`.github/workflows/lostloops-live.yml` (workflow_dispatch) runs the tool on leveldb, Spectra and
LightGBM at the census's pinned commits and fails on any difference from the census's stored lists.
The manual steps below do the same by hand on a small scale.

On Linux with the packages above (an Ubuntu 24.04 machine or a GitHub Actions `ubuntu-24.04` job):

```sh
# 1. The kernels of this repository: expect 3 lost (k04_rev.cpp:5, k05_stride2.cpp:5, k08_matmul.cpp:11),
#    shapes reverse / strided / strided, each with "yes: vector[] index out of bounds".
cd kernels
python3 ../tools/lostloops/lostloops.py --files k0*.cpp --out /tmp/ll-kernels -- -O2 -std=c++20 -I.
cd ..

# 2. A real CMake project: leveldb at the census's pinned commit; expect 1 lost loop at db/c.cc:117
#    (census 1, run 38259934735; the commit is the census's pin in corpus/projects.json).
git clone https://github.com/google/leveldb && cd leveldb && git checkout bb74ef739973a70ca9f0d90788a1da89b788c0ad
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=clang++-18 \
      -DCMAKE_CXX_FLAGS=-stdlib=libc++ -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
      -DLEVELDB_BUILD_TESTS=OFF -DLEVELDB_BUILD_BENCHMARKS=OFF
python3 ../tools/lostloops/lostloops.py --compile-commands build/compile_commands.json --out /tmp/ll-leveldb

# 3. The polite failure: on a machine without libc++ the tool must exit 2 with a message.
python3 tools/lostloops/lostloops.py --files kernels/k04_rev.cpp -- -O2; echo "exit $?"
```

Step 2 can differ from the census because CMake's flags (e.g. `-O3 -DNDEBUG`) are not the census's
`-O2`; that difference is the point of using flags as given.
