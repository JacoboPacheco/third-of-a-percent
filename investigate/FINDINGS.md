# Why k02_add_fwd cost 1.6x on some CPUs (raw data in `investigate/results/run-38119645255/draw1-4/`)

Question: the forward kernel `c[i] = a[i] + b[i]` is vectorized in both builds, yet FAST/NONE was 1.62x (L1) and 1.33x (L2) on AMD EPYC 9V74, 1.59x / 1.33x on EPYC 7763, and 0.98x / 0.91x on EPYC 9V45 in the day-one run, with a byte-identical binary.

## Cause (evidence level: strong for the layout link, inferred for the hardware mechanism)
- The check does not cost this. Where the FAST hot loop sits does.
- Under FAST, clang picks interleave 1, not 2 (the compiler's remark in `draw1/fast.remarks.txt`: "vectorization width: 4, interleaved count: 1"). `docs/dayone-results.md` says interleave 2 for both builds; that line is wrong.
- The resulting 31-byte SIMD loop sits at 0x12b0-0x12ce and crosses the 64-byte boundary at 0x12c0. On Zen 3 (EPYC 7763) and Zen 4 (EPYC 9V74) that placement runs about 2x slower; on Zen 5 (EPYC 9V45) the penalty is small (about 1.26x).
- The mechanism (the front end fetching a small loop one 64-byte window per cycle) is inferred: `perf` reports cycles as not supported on these VMs, so there are timings only.

## Evidence (one Actions run, run 38119645255: drew EPYC 7763 twice, 9V74 and 9V45)
- Binary hashes match the earlier runs; the ratios reproduce: 1.58 / 1.64 / 0.99 at L1; 1.19-1.24 (7763), 1.31 (9V74), 0.95 (9V45) at L2.
- Same source with `-falign-loops=64`: FAST time drops to 0.50-0.53x on the 7763 and 9V74, NONE unchanged. FAST/NONE becomes 0.82-0.86 at L1 and about 1.0 at L2 on all three CPUs.
- It is the boundary crossing, not alignment as such: NONE forced to interleave 1 (same 31-byte shape, offset 32, no crossing) is as fast as aligned FAST. Check-only cost (aligned FAST against NONE at interleave 1) is 0.95-1.01 on every CPU and size. FAST forced to interleave 2 equals NONE (1.00-1.04).
- Ruled out: where the arrays land (a, b, c at 6 different positions mod 4096, within about 3%) and spikes or clock (the gap is in the minimums and in every round).

## Verdict and what it changes
An artefact of code placement and CPU, not a cost of the bounds check. The 0.98x on 9V45 is also luck of placement. A byte-identical A/A cannot see this kind of noise.
For the measurement design:
1. Add NONE and FAST builds with `-falign-loops=64` as a second pair or column.
2. Record each hot loop's start, length and whether it crosses a 64-byte boundary (`investigate/loops.py`).
3. Add a layout A/A: NONE against NONE with a different loop alignment.
4. Report one row per CPU model; draw CPUs with a 4-job matrix.
5. Run the same layout check on the other forward kernels before reading their FAST/NONE ratios.
Not needed: allocation-address control.

Limits: one run, three CPU models, timing only, no hardware counters.
