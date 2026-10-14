// m04_rev: rewrites of kernels/k04_rev.cpp, c[i] = a[i] * 2 with i counting down.
// One variant per build, picked with -DV_<name>. The marked loop of each variant carries "// LOOP".
// Safety input ("short"): c has n - 1 elements, a has n. The original writes c[n-1] out of range.
#include <algorithm>
#include <span>
#include "common.hpp"

__attribute__((noinline)) void kern_m04_rev(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
#if defined(V_orig)
  // The original kernel, unchanged.
  for (size_t i = a.size(); i-- > 0;) c[i] = a[i] * 2;  // LOOP
#elif defined(V_pre)
  // (a) One up-front precondition, then the same operator[] loop.
  const size_t n = a.size();
  REQUIRE(c.size() >= n);
  for (size_t i = n; i-- > 0;) c[i] = a[i] * 2;  // LOOP
#elif defined(V_span)
  // (c) std::span with the bound taken once: first(n) is checked by libc++ hardening itself.
  const size_t n = a.size();
  std::span<int32_t> cs = std::span<int32_t>(c).first(n);
  std::span<const int32_t> as(a);
  for (size_t i = n; i-- > 0;) cs[i] = as[i] * 2;  // LOOP
#elif defined(V_raw)
  // (d) Raw data() pointers behind the up-front precondition. Safe ONLY through that one check.
  const size_t n = a.size();
  REQUIRE(c.size() >= n);
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  for (size_t i = n; i-- > 0;) cp[i] = ap[i] * 2;  // LOOP
#elif defined(V_fwd)
  // (f) The same loop counting up: every element is independent, so the order does not matter.
  for (size_t i = 0; i < a.size(); ++i) c[i] = a[i] * 2;  // LOOP
#elif defined(V_rtransform)
  // (b)+(e) Reverse iterators and std::transform: no index, so no operator[] check at all.
  std::transform(a.rbegin(), a.rend(), c.rbegin(), [](int32_t x) { return x * 2; });  // LOOP
#elif defined(V_pragma)
  // (g) The original with a vectorize pragma: does asking the vectorizer change anything?
#pragma clang loop vectorize(enable)
  for (size_t i = a.size(); i-- > 0;) c[i] = a[i] * 2;  // LOOP
#else
#error "pick a variant with -DV_<name>"
#endif
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  if (short_mode(argc, argv)) {
    std::vector<int32_t> a(n), c(n - 1);
    fill(a, 1);
    kern_m04_rev(c, a);
    returned_after_short();
  }
  std::vector<int32_t> a(n), c(n);
  fill(a, 1);
  kern_m04_rev(c, a);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_m04_rev(c, a);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
