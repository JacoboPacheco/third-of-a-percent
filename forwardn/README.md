# forwardn: forward loops with a variable bound, compile-only

Does libc++ FAST stop the vectorizer on a forward loop whose bound is a variable (`for (i = 0; i < n; ++i)`) and
not the container's `size()`? The loop census (`corpus/README.md`) counts 228 such lost loops (38 locations) among
its 444, built with clang 18, and none of the eight timed kernels has the shape. This folder compiles 18 small
functions, checks off against checks on, with nine clang versions on [Compiler Explorer](https://godbolt.org) and
reads the compiler's own loop-vectorize remark at each loop. Nothing is timed.

`PLAN.md` holds the question, the functions, six predictions and what each outcome would decide. `source.cpp` is
the file that was compiled. `run.py` sends the 54 requests (9 clang ids x NONE/FAST x x86-64 `-O2`, x86-64 `-O3`,
AArch64 `-O2`; the hardening macro that fits each library version), saves every answer in `cache/`, and writes
`results.json` and `RESULTS.generated.md` (the full tables, one per target and optimization level).
`tests/test_forwardn.py` checks the runner on made-up cells and checks that `results.json` is what the saved answers
give.

```
python forwardn/run.py --offline     # analyse the saved answers; never touches the network
python forwardn/run.py --dry-run     # list the requests that would be sent
```

## Result

Words: **lost** = vectorized with the checks off and not with them on; **narrower** = vectorized in both builds with
a different width or interleave count; **kept** = vectorized in both, the same; **scalar** = vectorized in neither.
The hardening macro changed the code (more traps with it on) in 27 of 27 compile pairs. The table gives the word at
x86-64 `-O2`; where `-O3` or AArch64 differ, the next column says how.

| function (loop) | clang 16.0.0 to 18.1.0 | clang 19.1.0 and later | other targets and levels |
|---|---|---|---|
| `sum_size`, `scale_size`, `inplace_n`, `rangefor` (controls and an in-place update) | kept | kept | the same |
| `sum_n_size_t`, `sum_n_int`, `sum_n_u32`, `sum_n_i64`, `sum_int_size` (sum, bound `n` in four types, or `(int)a.size()`) | **lost** | kept | the same at `-O3` and on AArch64 |
| `sum_member`, `sum_ptr_member` (sum, bound a struct member, or through a pointer to the struct) | **lost** | kept | the same |
| `scale_n_size_t`, `scale_n_int` (`c[i] = a[i] * 2`, bound `n`) | narrower | kept | `-O3`: narrower on 16.0.0 only; AArch64: kept on every version |
| `scale_offset` (`c[i + off] = a[i]`) | **lost** | kept | AArch64: kept on every version |
| `fill_n` (`c[i] = i * 3`) | **lost** | kept | AArch64: kept on every version |
| `dot_n` (two vectors, `int64_t` products) | scalar | scalar; gained on trunk | AArch64: **lost** on 16.0.0 to 18.1.0, kept after |
| `two_stores` (two writes per iteration) | narrower | narrower to 21.1.0, **lost** on 22.1.0 and 23.1.0, kept on trunk | `-O3`: narrower to 18.1.0, kept after; AArch64 as x86-64 `-O2` |
| `member_write` (`FwnWork::run`, writes through the object that holds the bound) | scalar | scalar; kept on trunk | the same |

Where the checks cost the vectorizer a loop, the remark is the same one the census read: "could not determine number
of loop iterations" for the lost sums, and "the cost-model indicates that vectorization is not beneficial" for
`fill_n` on clang 18. The sums are lost whichever of the four integer types the bound has. On clang 22.1.0 and
23.1.0 the `two_stores` loop is lost with the remark "Early exit loop with store but no supported condition load";
the trunk build vectorizes it again. That remark is what the compiler printed; this folder does not test why.

## Predictions

| # | prediction (`PLAN.md`) | outcome |
|---|---|---|
| 1 | The variable-bound sums follow the compiler version and not the counter type: lost on 16.0.0 and 17.0.1 as on 18.1.0, kept on 22.1.0, 23.1.0 and trunk as on 19 to 21 | **held**; no cell contradicts it |
| 2 | AArch64 gives the same word as x86-64 in at least 90% of the cells, and `-O3` the same as `-O2` in at least 90% of the x86-64 cells | **failed**: AArch64 agrees in 141 of 162 cells (87.0%); `-O3` agrees in 153 of 162 (94.4%), so only the second half held. The 21 cells that differ are `dot_n`, `scale_n_*`, `scale_offset` and `fill_n`: the stop on the sums is the same on both targets, the stop on the writes and on the dot product is not |
| 3 | The writes bounded by `n` (`scale_n_*`, `inplace_n`, `fill_n`, `dot_n`) are never lost where the control `scale_size` is kept, and some are narrower on clang 18 | **failed**: `fill_n` is lost on x86-64 16.0.0 to 18.1.0 (at `-O2` and `-O3`) and `dot_n` on AArch64 16.0.0 to 18.1.0, nine cells; the second half held (`scale_n_size_t` and `scale_n_int` are narrower) |
| 4 | Loops bounded by a member or through a pointer are scalar in both builds everywhere | **failed**: `sum_member` and `sum_ptr_member` are vectorized with the checks off on every compiler (lost on 16.0.0 to 18.1.0, kept after); only `member_write` is scalar in both builds, and trunk vectorizes it |
| 5 | The range-for control is kept, with the same width and interleave, everywhere | held |
| 6 | The controls `sum_size` and `scale_size` are kept everywhere | held |

The `member_write` loop is also scalar with the checks off, with the same remark ("could not determine number of
loop iterations"). The loop stores through `c` into memory that may overlap the member that holds the bound; the sums
have no store. That is a reading consistent with the remarks, not something these compiles test. The plan recorded
an earlier scratch probe as finding the member-bound loops scalar in both builds; here the two sums are not, and the
probe was not kept, so whether its functions differed cannot be said.

## What it means for the study, and what it does not show

- The page sentence that a forward loop with a variable bound "cannot be proven in range, so the check stays inside
  and the vectorizer gives up" was a statement about every compiler and every such loop. It holds for the sums on
  clang 16 to 18 and not for clang 19.1.0 and later in these builds, and it does not hold for writes such as
  `c[i] = a[i] * 2`, which stay vectorized (narrower) on clang 18. The sentence on the details page and in
  `corpus/README.md` now says so.
- The census counts, the timed kernels and every number under `results/` are clang 18.1.3 on the Ubuntu runner and
  are unchanged. This folder says the forward-loop part of the 444 lost loops is a clang 16-to-18 effect for the
  sums; whether those loops are still lost under clang 19 or later, and what a lost sum costs, is not measured here.
  A timing of six variable-bound loops on clang 18 has its own plan, `forwardt/PLAN.md`, and its result is in
  `forwardt/README.md`; a census rebuild with a newer clang needs a plan of its own and is not started.
- Compile-only. Nothing here says how fast any loop runs or how often such a loop is hot. In the main study, a forward
  reduction built without vectorization costs 1.09x on one kernel (`docs/dayone-results.md`), so a lost sum may be cheap. The timing in `forwardt/` found a larger cost for the variable-bound sum on the two AMD
  models it read (see the main README, section "Forward loops with a variable bound").
- The compilers are Compiler Explorer's own builds with its own libc++ for each (its `clang1810` is a release candidate
  of 18.1.0, not the Ubuntu 18.1.3 that was timed; "22.1.0", "23.1.0" and "trunk" are what it offered on
  21 October 2026, and trunk moves). `-O2` and `-O3` are the x86-64 baseline target (SSE2), not AVX2; a width-4 loop
  of 32-bit integers is a 128-bit loop. `dot_n` is scalar on x86-64 for every version before trunk with the checks
  off as well; the remark says the cost model finds vectorization not beneficial. Trunk vectorizes it only with the
  checks on ("gained"); one cell, no reading.
- Libraries other than libc++ (libstdc++ assertions, MSVC) are not compiled.

## Order of events

The plan was committed alone, then the source file and the runner, then the first request was sent, in the author's
development history, which this repository does not hold in that form; the order cannot be checked from here and
rests on the author's clock. The commit times were 10:32:32 (plan), 10:33:59 (source and runner) and the first
request in `cache/requests.log` is 14:34:01 UTC, 10:34:01 EDT. The plan's header says "about 10:35 EDT", three
minutes later than its own commit time; it was not edited. The 18-to-21 part of prediction 1 repeats a probe the
author had seen before writing the plan (the plan says so); clang 16.0.0, 17.0.1, 22.1.0, 23.1.0 and trunk, AArch64,
`-O3` and the shapes not in the probe were new. All 54 requests were sent once, in one run, and every answer is saved
in `cache/`; no function, flag or rule was changed after the first answer was read.
