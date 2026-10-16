// Variants of the reverse (k04) and stride-2 (k05) loops, for compile-only tests (needs -std=c++20 for <span>).
// Every function has one "// LOOP" line. REQUIRE is the project's up-front check (mitigate/src/common.hpp).
// "pre", "span" and "raw" are the three rewrites of mitigate/src/m04_rev.cpp and m05_stride2.cpp.
// "fwd" counts up instead of down. "manual" keeps the check inside the loop but writes it by hand on raw
// pointers (no libc++ hardening macro involved), to show that the loop shape, not the library, matters.
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

#define REQUIRE(cond)              \
  do {                             \
    if (!(cond)) __builtin_trap(); \
  } while (0)

// ------------------------------------------------------------------ reverse: c[i] = a[i] * 2, i down
// One up-front check, then the same operator[] loop (m04_rev V_pre).
__attribute__((noinline)) void v_rev_pre(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  const size_t n = a.size();
  REQUIRE(c.size() >= n);
  for (size_t i = n; i-- > 0;) c[i] = a[i] * 2;  // LOOP
}

// std::span with the bound taken once (m04_rev V_span).
__attribute__((noinline)) void v_rev_span(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  const size_t n = a.size();
  std::span<int32_t> cs = std::span<int32_t>(c).first(n);
  std::span<const int32_t> as(a);
  for (size_t i = n; i-- > 0;) cs[i] = as[i] * 2;  // LOOP
}

// Raw pointers behind the up-front check (m04_rev V_raw).
__attribute__((noinline)) void v_rev_raw(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  const size_t n = a.size();
  REQUIRE(c.size() >= n);
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  for (size_t i = n; i-- > 0;) cp[i] = ap[i] * 2;  // LOOP
}

// The same loop counting up, operator[] checks kept (m04_rev V_fwd).
__attribute__((noinline)) void v_rev_fwd(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < a.size(); ++i) c[i] = a[i] * 2;  // LOOP
}

// In-loop check written by hand, counting down.
__attribute__((noinline)) void v_rev_manual(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t cn = c.size();
  for (size_t i = a.size(); i-- > 0;) {  // LOOP
    if (i >= cn) __builtin_trap();
    cp[i] = ap[i] * 2;
  }
}

// In-loop check written by hand, counting up.
__attribute__((noinline)) void v_fwd_manual(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t cn = c.size();
  for (size_t i = 0; i < a.size(); ++i) {  // LOOP
    if (i >= cn) __builtin_trap();
    cp[i] = ap[i] * 2;
  }
}

// Reverse memory order with an index that counts up: step j touches element n - 1 - j.
__attribute__((noinline)) void v_rev_j(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  const size_t n = a.size();
  for (size_t j = 0; j < n; ++j) c[n - 1 - j] = a[n - 1 - j] * 2;  // LOOP
}

// ------------------------------------------------------------------ stride-2: c[i] = a[2i] + a[2i+1], bound c.size()
// One up-front check in the form of m05_stride2 V_pre, then the same operator[] loop.
__attribute__((noinline)) void v_s2_pre(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  const size_t n = c.size();
  REQUIRE(a.size() / 2 >= n);
  for (size_t i = 0; i < n; ++i) c[i] = a[2 * i] + a[2 * i + 1];  // LOOP
}

// The same up-front check written as a multiplication (with a guard against wrap-around).
__attribute__((noinline)) void v_s2_pre_mul(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  const size_t n = c.size();
  REQUIRE(n <= SIZE_MAX / 2 && 2 * n <= a.size());
  for (size_t i = 0; i < n; ++i) c[i] = a[2 * i] + a[2 * i + 1];  // LOOP
}

// std::span with the bound taken once (m05_stride2 V_span).
__attribute__((noinline)) void v_s2_span(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  const size_t n = c.size();
  REQUIRE(n <= SIZE_MAX / 2);
  std::span<const int32_t> as = std::span<const int32_t>(a).first(2 * n);
  std::span<int32_t> cs(c);
  for (size_t i = 0; i < n; ++i) cs[i] = as[2 * i] + as[2 * i + 1];  // LOOP
}

// Raw pointers behind the up-front check (m05_stride2 V_raw).
__attribute__((noinline)) void v_s2_raw(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  const size_t n = c.size();
  REQUIRE(a.size() / 2 >= n);
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  for (size_t i = 0; i < n; ++i) cp[i] = ap[2 * i] + ap[2 * i + 1];  // LOOP
}

// In-loop check written by hand.
__attribute__((noinline)) void v_s2_manual(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t an = a.size();
  for (size_t i = 0; i < c.size(); ++i) {  // LOOP
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// Only one checked read per element (a[2i]): one trap exit instead of two.
__attribute__((noinline)) void v_s2_one(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < c.size(); ++i) c[i] = a[2 * i];  // LOOP
}

// The counter itself steps by 2 (j = 2i); the output is written through a raw pointer, so only a is checked.
__attribute__((noinline)) void v_s2_j(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const size_t n2 = 2 * c.size();
  for (size_t j = 0; j < n2; j += 2) cp[j / 2] = a[j] + a[j + 1];  // LOOP
}
