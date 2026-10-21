Compile-only. Compiler Explorer clang ids of `ce-sweep/cesweep.py`, `-stdlib=libc++`, hardening off against on. Words: lost = vectorized with checks off and not with them on; narrower = vectorized in both builds with a different width or interleave count; kept = vectorized in both builds, same; scalar = not vectorized in either.

Hardening macro took effect (more traps with it on) in 27 of 27 compile pairs.

### x86-64 -O2

| function | clang 16.0.0 | clang 17.0.1 | clang 18.1.0 | clang 19.1.0 | clang 20.1.0 | clang 21.1.0 | clang 22.1.0 | clang 23.1.0 | clang trunk |
|---|---|---|---|---|---|---|---|---|---|
| `sum_size` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `sum_n_size_t` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_int` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_u32` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_i64` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_int_size` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_member` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_ptr_member` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `dot_n` | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | gained |
| `scale_size` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `scale_n_size_t` | narrower | narrower | narrower | kept | kept | kept | kept | kept | kept |
| `scale_n_int` | narrower | narrower | narrower | kept | kept | kept | kept | kept | kept |
| `scale_offset` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `two_stores` | narrower | narrower | narrower | narrower | narrower | narrower | lost | lost | kept |
| `member_write` | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | kept |
| `inplace_n` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `fill_n` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `rangefor` | kept | kept | kept | kept | kept | kept | kept | kept | kept |

### x86-64 -O3

| function | clang 16.0.0 | clang 17.0.1 | clang 18.1.0 | clang 19.1.0 | clang 20.1.0 | clang 21.1.0 | clang 22.1.0 | clang 23.1.0 | clang trunk |
|---|---|---|---|---|---|---|---|---|---|
| `sum_size` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `sum_n_size_t` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_int` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_u32` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_i64` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_int_size` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_member` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_ptr_member` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `dot_n` | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | gained |
| `scale_size` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `scale_n_size_t` | narrower | kept | kept | kept | kept | kept | kept | kept | kept |
| `scale_n_int` | narrower | kept | kept | kept | kept | kept | kept | kept | kept |
| `scale_offset` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `two_stores` | narrower | narrower | narrower | kept | kept | kept | kept | kept | kept |
| `member_write` | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | kept |
| `inplace_n` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `fill_n` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `rangefor` | kept | kept | kept | kept | kept | kept | kept | kept | kept |

### aarch64 -O2

| function | clang 16.0.0 | clang 17.0.1 | clang 18.1.0 | clang 19.1.0 | clang 20.1.0 | clang 21.1.0 | clang 22.1.0 | clang 23.1.0 | clang trunk |
|---|---|---|---|---|---|---|---|---|---|
| `sum_size` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `sum_n_size_t` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_int` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_u32` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_n_i64` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_int_size` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_member` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `sum_ptr_member` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `dot_n` | lost | lost | lost | kept | kept | kept | kept | kept | kept |
| `scale_size` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `scale_n_size_t` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `scale_n_int` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `scale_offset` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `two_stores` | narrower | narrower | narrower | narrower | narrower | narrower | lost | lost | kept |
| `member_write` | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | scalar in both | kept |
| `inplace_n` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `fill_n` | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| `rangefor` | kept | kept | kept | kept | kept | kept | kept | kept | kept |

### Predictions of PLAN.md

| # | holds | detail |
|---|---|---|
| 1 | yes | no cell contradicts it |
| 2 | NO | aarch64 -O2 agrees with x86-64 -O2 in 141 of 162 cells; x86-64 -O3 agrees with -O2 in 153 of 162 |
| 3 | NO | dot_n aarch64 -O2 clang 16.0.0: lost; dot_n aarch64 -O2 clang 17.0.1: lost; dot_n aarch64 -O2 clang 18.1.0: lost; fill_n x86-64 -O2 clang 16.0.0: lost; fill_n x86-64 -O3 clang 16.0.0: lost; fill_n x86-64 -O2 clang 17.0.1: lost; fill_n x86-64 -O3 clang 17.0.1: lost; fill_n x86-64 -O2 clang 18.1.0: lost; fill_n x86-64 -O3 clang 18.1.0: lost |
| 4 | NO | sum_member aarch64 -O2 clang trunk: kept; sum_ptr_member aarch64 -O2 clang trunk: kept; member_write aarch64 -O2 clang trunk: kept; sum_member aarch64 -O2 clang 16.0.0: lost; sum_ptr_member aarch64 -O2 clang 16.0.0: lost; sum_member aarch64 -O2 clang 17.0.1: lost; sum_ptr_member aarch64 -O2 clang 17.0.1: lost; sum_member aarch64 -O2 clang 18.1.0: lost; sum_ptr_member aarch64 -O2 clang 18.1.0: lost; sum_member aarch64 -O2 clang 19.1.0: kept; sum_ptr_member aarch64 -O2 clang 19.1.0: kept; sum_member aarch64 -O2 clang 20.1.0: kept; sum_ptr_member aarch64 -O2 clang 20.1.0: kept; sum_member aarch64 |
| 5 | yes | kept with equal width and interleave in every cell |
| 6 | yes | vectorized in both builds in every cell |
