// Stride-2 loops (and one reverse loop) with the check written by hand on raw pointers (no libc++ hardening macro involved).
// They differ only in two things: whether a guard says 2*n cannot wrap (REQUIRE(n <= SIZE_MAX / 2)), and
// whether the bound `an` is masked with SIZE_MAX >> 1. The mask changes nothing for any real vector (a size
// is below 2^62) but tells the compiler the largest value the bound can have.
#include <cstddef>
#include <cstdint>
#include <vector>

#define REQUIRE(cond)              \
  do {                             \
    if (!(cond)) __builtin_trap(); \
  } while (0)

// guard, bound as it is
__attribute__((noinline)) void v2_s2_guard(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = a.size();
  REQUIRE(n <= SIZE_MAX / 2);
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// guard, bound masked
__attribute__((noinline)) void v2_s2_guard_masked(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = a.size() & (SIZE_MAX >> 1);
  REQUIRE(n <= SIZE_MAX / 2);
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// no guard, bound masked
__attribute__((noinline)) void v2_s2_masked(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = a.size() & (SIZE_MAX >> 1);
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// Reverse loop, check written by hand, bound masked: does a bound with a known range make the exit countable?
__attribute__((noinline)) void v2_rev_masked(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t cn = c.size() & (SIZE_MAX >> 1);
  for (size_t i = a.size(); i-- > 0;) {  // LOOP
    if (i >= cn) __builtin_trap();
    cp[i] = ap[i] * 2;
  }
}
