# Arm column: the same loops on an AArch64 runner

Written Fri Oct 16, 09:30 EDT, after one two-kernel smoke run (run 38904557204) and before any of the full
runs below had finished. The smoke run is the only Arm timing seen so far: k04_rev (reverse) 6.58x and
k02_add_fwd 1.005x, with an A/A half-width of 0.04%.

## Question

The x86-64 results say loops that lose SIMD under libc++'s FAST hardening pay 2.8x to 8.0x in cache, and
that forward loops pay little on the AMD models. Do the same loop shapes lose their vector code and pay on an
AArch64 core (NEON), and what do forward loops cost on a machine quiet enough to resolve a third of a percent?

## Setup (nothing about the method changes)

- Runner label `ubuntu-24.04-arm` (GitHub-hosted, 4 vCPUs; `lscpu` reports `Neoverse-N2`). The only workflow
  change is the `runner` input of `measure.yml`; the CPU name is read from `lscpu` when `/proc/cpuinfo` has none.
- Same packages (clang-18 and libc++-18-dev from Ubuntu noble), same kernels, same flags (`-O2`, no `-march`),
  same harness (`harness/run.py`), same rules (`harness/criteria-v3.json`, unchanged), same pooling
  (`harness/pool.py`, two-level bootstrap over jobs then repetitions, at least 3 jobs for a verdict).
- The harness reads AArch64 `objdump` text: `brk #0x1` counts as a trap, `b.cond`/`cbz`/`cbnz`/`tbz`/`tbnz` as
  loop branches, NEON operands (`v0.4s`, `q0`) as SIMD (`harness/asm.py`, `harness/placement.py`,
  `tests/test_arm64_asm.py`). The 64-byte-window placement fields are computed for Arm as for x86-64 but were
  defined for x86 fetch windows; the layout A/A (NONE against NONE with `-falign-loops=64`) is the control
  that matters for placement on both.
- Three full runs of ten jobs, dispatched together. Every job that returns is pooled; none is dropped.

## What is reported, and what is not

- The pooled verdict form for Neoverse-N2 exactly as `pool.py` gives it (MAP or INCONCLUSIVE), whatever it is.
- Per cell: FAST/NONE as compiled and with loops aligned, intervals, the compiler's vectorization remark, the
  count of check traps, packed (NEON) instructions per build, Cachegrind instruction counts (secondary).
- The A/A and layout A/A floors of the pool. If the A/A half-width is below 0.30%, the forward loops are
  reported against it as a description ("the forward loops cost x%, the A/A floor is y%"). No threshold is
  changed or added to the verdict rules; the forward-loop rule stays at 1.02 with the 2 x A/A allowance.
- No claim about Apple, AWS or any other Arm core, other compilers or libc++ versions, or services.
  One core type, one hypervisor, shared machines.

## Written before the full results (from the Compiler Explorer sweep, compile-only; ce-sweep/README.md)

- Reverse and stride-2: lost under FAST on clang 18 AArch64 (the sweep says so for clang 18.1.0).
  Reverse was already seen in the smoke run, so it is not a blind prediction.
- Matrix multiply: the sweep lists it as NOT lost on AArch64 for clang 18.1.0 through 22 (it is lost on
  x86-64 for 18.1.0). The timed Ubuntu build is 18.1.3; if matmul is lost or kept on the timed runner, the
  remarks decide which, and the difference from x86-64 is reported, not explained.
- Forward loops (sum, add, stencil): vectorized in both builds. No placement effect is predicted.
- Gather and histogram: no prediction.

## Limits (stated now)

Compile-time and run-time facts come from one runner image and one core type. 30 jobs on a shared pool. The
runs were chosen to be pooled together before any of them finished. The `ubuntu-24.04-arm` label could map to
other core types later; the pool is per `lscpu` model name.
