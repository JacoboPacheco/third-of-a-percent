# Lost loops: libc++ hardening NONE vs FAST

> This tool counts loops; it times nothing. A lost loop is only a candidate for a cost: how often it runs is unknown at compile time. Time the code with hardening off and on before changing anything.

Compiler: `Ubuntu clang version 18.1.3 (1ubuntu1)`. Project root: `/home/runner/work/third-of-a-percent-public/third-of-a-percent-public/build/live/spectra/deps/src/spectra-6841bcbacaa0f0a8446210314e682057a084be4e`. Tool: lostloops 0.1.

| | |
|---|---|
| files compiled | 1 of 1 |
| vectorized loops, hardening off | 79 (15 source locations) |
| vectorized loops, FAST | 75 |
| **lost** (vectorized off, not with FAST) | **4** (5.06%), 1 locations, 1 in the project |
| gained / moved | 0 / 0 |
| check traps (ud2) added | 27 |
| code size (.text) change | +0.99% |
| lost loops with a libc++ check traced inside | 4 |

## Lost loops

| where | origin | shape | functions | check in the loop | compiler says (FAST) | source | what to try |
|---|---|---|---|---|---|---|---|
| `include/Spectra/Util/SelectionRule.h:215:9` | project | forward, bounded by a variable | 4 | yes: vector[] index out of bounds | the cost-model indicates that interleaving is not beneficial; the cost-model indicates that vectorization is not beneficial | `for (Index i = 0; i < size; i++)` | The loop runs to a variable, not the container's size(), so clang cannot prove each index is in range. Try one check before the loop that the bound fits (if (v.size() < n) abort();) or index a std::span(v).first(n): that worked in our reverse-loop test, where the index is the loop counter itself; this exact shape was not timed. |

## Limits

- Counts, not time: a loop that runs once at start-up and a loop that runs a billion times count the same.
- One compiler: the clang and libc++ found on this machine, with your flags as given. Another clang version, another -march or GCC's own checks can give a different list.
- A loop counts once per function it was compiled into: a header loop inlined into three functions counts three times. The table groups them by source line and shows how many functions.
- The shape (reverse, strided, indirect, ...) is read from the source text with regular expressions: a heuristic, not a proof. Each loop is listed with its line so you can check the call.
- Only translation units in the input are compiled; header code counts only where a compiled file instantiates it.
- libc++ writes the hardening mode into the ABI tag of its inline functions ([abi:ne180100] with NONE, [abi:fe180100] with FAST); the hardened spelling is mapped to the NONE spelling before matching.
- The 'what to try' lines come from timed tests of four small kernels on AMD EPYC cloud machines (clang 18, FAST mode; this project's mitigate/README.md), not from your code.
