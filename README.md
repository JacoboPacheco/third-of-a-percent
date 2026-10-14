# Third of a Percent

A re-test of how much C++ bounds checks cost, loop by loop, with the machine code as proof.

Status: measurements complete (Oct 2026); the page and notes may still be edited. Code written by AI coding agents directed by the author (JacoboPacheco).

## In three sentences

1. Google reported that turning on bounds checks in C++'s standard library cost its services 0.30% on average.
2. This study built algorithm kernels and real programs with the checks off and on, timed each pair 20 to 40 times per side in alternating order against an A/A control, and showed from the machine code that the checks were there.
3. The average hides a map: loops that lose SIMD under the check ran 2.8 to 8.0 times slower in cache, forward loops cost little under clang on the AMD models when aligned, and such loops are rare in general libraries but not in numeric code.

**Words used here.**
- **SIMD**: one instruction working on several array elements at once.
- **A/A control**: timing a program against a copy of itself, to see the machine's own noise.
- **NONE / FAST**: the same program built without checks (NONE) and with libc++'s FAST hardening mode (FAST).
- **Verdict**: the per-CPU-model reading, computed from written rules: a map, small cost everywhere, or inconclusive.
- **Placement**: the memory address where a loop's code starts; moving it can change speed.
- **PGO**: profile-guided optimization: the compiler sees a sample run first and tunes to it.

## The question

Google wrote that "Hardening libc++ resulted in an average 0.30% performance impact" across its services ([Google Security Blog, Nov 15 2024](https://security.googleblog.com/2024/11/retrofitting-spatial-safety-to-hundreds.html)). Hardening makes C++'s standard library check every `vector[i]` against the vector's size.

This study timed loops and programs with checks off and on: a different measurement, so it neither confirms nor contradicts Google's average.

## What we found

Some loops lose SIMD when a check is added. A check can stop the program at any element, so the compiler may process several elements at once only if it can show the whole range is in bounds. It can for forward loops (the check moves to the tail) but did not for reverse, stride-2 and matrix-multiply loops. This mechanism is inferred from the machine code and from an up-front size check restoring the speed.

- **2.8x to 8.0x slower** in cache for loops that lose SIMD (reverse, stride-2, matrix multiply on clang 18), on all three AMD models with a verdict; the Intel CPUs lost the same loops.
- **1 of 593** vectorized loops in 19 general libraries lose SIMD, against 444 of 4,968 in 25 numeric projects. Counted, not timed.
- **Real programs timed whole** (six with lost loops): detectably slower for five of six on EPYC 7763 (1.2% to 7.5%, 16 jobs), four on EPYC 9V74 (3 jobs), three on EPYC 9V45 (5 jobs); the rest were not detectable.
- **Code placement and PGO.** Across 4 placements the reverse loop stays at 5.2x to 8.0x and the forward sum near 1x; the forward add swings 0.82x to 1.60x on two models. PGO, trained on the timed input, left the cost in most rows.
- **0.99x to 1.09x** for the reverse loop after one added size check before it, with the checks still on.
- **GCC differs.** With GCC 14's checks at `-O3`, even the forward add loses SIMD and runs 4.9x to 8.5x slower.

## Try it

```
python scripts/check.py
```

Recomputes every interval and verdict from the raw timings and checks the page (Python 3, numpy).

```
gh workflow run measure.yml
```

Reruns the measurement in your fork. Page locally: `python -m http.server 8000 --directory site`.

## How much to trust it

- **Shared machines.** GitHub picks each job's CPU; some got few jobs.
- **Mostly one toolchain.** Ubuntu clang 18, libc++, `-O2`, FAST mode. Clang and libc++ 19 to 21, timed on the eight loops (one CPU model with enough jobs), still lose the reverse and stride-2 loops; matrix multiply is no longer lost (still 1.6x at L1).
- **Machine state.** Over 10 jobs, steal was 0% and reported CPU frequency drifted at most 0.57%; no ratio moved. The driver was seen on the timed core's hyperthread sibling in 8 jobs.
- **Counts are not time.** The 593 and 4,968 are loops, not hotness.
- **Real programs** were picked for their lost loops, not sampled.
- **Rules were loosened after seeing results.** Each rule file predates the runs it judges, except the first; old versions stay.
- **Independence of repetitions.** A block bootstrap changes no verdict form on EPYC 7763 or 9V74; 9V45 is fragile ([report](robustness/report.md)).
- **Holdout.** A fresh, pre-planned run matched on EPYC 7763 and 9V74, not 9V45.

## Where things are

- **Study:** `kernels/` the 8 loops; `programs/` the real programs; `corpus/` and `siblings/` the loop census and compiler sweeps; `harness/` times and judges; `mitigate/` the rewrite that restores SIMD.
- **Runs:** `results/` every run as downloaded; `layout-sweep/`, `pgo/`, `versions/`, `environment/`, `realworld/`, `robustness/`, `ce-sweep/` the follow-up columns, each with its own README or plan.
- **Evidence and review:** `claims-audit/` independent checks of every figure on the page; `gaps/`, `investigate/`, `audit/`, `docs/` notes and audits.
- **Page and checks:** `site/` the page; `scripts/` and `tests/` the one-command check (`python scripts/check.py`).

Method, per-CPU numbers, limits, history: [details](readme-parts/DETAILS.md).
