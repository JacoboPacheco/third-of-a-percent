| compiler | hardening macro | check compiles to | outcome at the loop | cost of each exit compare at VF 4 | exit compares found uniform |
|---|---|---|---|---|---|
| clang 16.0.0 | `_LIBCPP_ENABLE_ASSERTIONS=1` | call of `__libcpp_verbose_abort` | not vectorized: cost model, not beneficial | 14 | no |
| clang 17.0.1 | `_LIBCPP_ENABLE_HARDENED_MODE=1` | call of `__libcpp_verbose_abort` | not vectorized: cost model, not beneficial | 14 | no |
| clang 18.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | not vectorized: cost model, not beneficial | 14 | no |
| clang 19.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | vectorized (width 4, interleave 2) | 1 | yes |
| clang 20.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | vectorized (width 4, interleave 2) | 1 | yes |
| clang 21.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | vectorized (width 4, interleave 2) | 1 | yes |
| clang 22.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | vectorized (width 4, interleave 2) | - | no |
| clang 23.1.0 | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | not vectorized: early-exit loop with a store | - | no |
| trunk (assertions build, e633c7da8f) | `_LIBCPP_HARDENING_MODE_FAST` | trap (`ud2`) | not vectorized: early-exit loop with complex writes | - | no |
