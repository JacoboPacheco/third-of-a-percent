# Lost loops: libc++ hardening NONE vs FAST

> This tool counts loops; it times nothing. A lost loop is only a candidate for a cost: how often it runs is unknown at compile time. Time the code with hardening off and on before changing anything.

Compiler: `Ubuntu clang version 18.1.3 (1ubuntu1)`. Project root: `/home/runner/work/third-of-a-percent-public/third-of-a-percent-public/build/live/leveldb/deps/src/leveldb-bb74ef739973a70ca9f0d90788a1da89b788c0ad`. Tool: lostloops 0.1.

| | |
|---|---|
| files compiled | 39 of 39 |
| vectorized loops, hardening off | 36 (13 source locations) |
| vectorized loops, FAST | 35 |
| **lost** (vectorized off, not with FAST) | **1** (2.78%), 1 locations, 1 in the project |
| gained / moved | 0 / 0 |
| check traps (ud2) added | 35 |
| code size (.text) change | +0.16% |
| lost loops with a libc++ check traced inside | 1 |

## Lost loops

| where | origin | shape | functions | check in the loop | compiler says (FAST) | source | what to try |
|---|---|---|---|---|---|---|---|
| `db/c.cc:117:5` | project | forward, bounded by a variable | 1 | yes: vector[] index out of bounds | the cost-model indicates that interleaving is not beneficial; the cost-model indicates that vectorization is not beneficial | `for (int i = 0; i < n; i++) {` | The loop runs to a variable, not the container's size(), so clang cannot prove each index is in range. Try one check before the loop that the bound fits (if (v.size() < n) abort();) or index a std::span(v).first(n): that worked in our reverse-loop test, where the index is the loop counter itself; this exact shape was not timed. |

## Limits

- Counts, not time: a loop that runs once at start-up and a loop that runs a billion times count the same.
- One compiler: the clang and libc++ found on this machine, with your flags as given. Another clang version, another -march or GCC's own checks can give a different list.
- A loop counts once per function it was compiled into: a header loop inlined into three functions counts three times. The table groups them by source line and shows how many functions.
- The shape (reverse, strided, indirect, ...) is read from the source text with regular expressions: a heuristic, not a proof. Each loop is listed with its line so you can check the call.
- Only translation units in the input are compiled; header code counts only where a compiled file instantiates it.
- libc++ writes the hardening mode into the ABI tag of its inline functions ([abi:ne180100] with NONE, [abi:fe180100] with FAST); the hardened spelling is mapped to the NONE spelling before matching.
- The 'what to try' lines come from timed tests of four small kernels on AMD EPYC cloud machines (clang 18, FAST mode; this project's mitigate/README.md), not from your code.
