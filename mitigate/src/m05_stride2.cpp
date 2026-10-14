// m05_stride2: rewrites of kernels/k05_stride2.cpp, c[i] = a[2*i] + a[2*i+1], bound c.size().
// One variant per build, picked with -DV_<name>. The marked loop of each variant carries "// LOOP".
// Safety input ("short"): a has 2n - 1 elements, c has n. The original reads a[2n-1] out of range.
#include <span>
#include "common.hpp"

__attribute__((noinline)) void kern_m05_stride2(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
#if defined(V_orig)
  // The original kernel, unchanged.
  for (size_t i = 0; i < c.size(); ++i) c[i] = a[2 * i] + a[2 * i + 1];  // LOOP
#elif defined(V_pre)
  // (a) One up-front precondition (a holds at least 2n elements), then the same operator[] loop.
  const size_t n = c.size();
  REQUIRE(a.size() / 2 >= n);
  for (size_t i = 0; i < n; ++i) c[i] = a[2 * i] + a[2 * i + 1];  // LOOP
#elif defined(V_span)
  // (c) std::span with the bound taken once: first(2n) is checked by libc++ hardening itself.
  const size_t n = c.size();
  REQUIRE(n <= SIZE_MAX / 2);  // so 2n cannot wrap; first() checks the rest
  std::span<const int32_t> as = std::span<const int32_t>(a).first(2 * n);
  std::span<int32_t> cs(c);
  for (size_t i = 0; i < n; ++i) cs[i] = as[2 * i] + as[2 * i + 1];  // LOOP
#elif defined(V_span_il2)
  // (c)+(g) The span variant with the interleave count the NONE build picks (2). Under FAST clang
  // vectorizes the span loop with interleave 1; this asks for 2.
  const size_t n = c.size();
  REQUIRE(n <= SIZE_MAX / 2);
  std::span<const int32_t> as = std::span<const int32_t>(a).first(2 * n);
  std::span<int32_t> cs(c);
#pragma clang loop interleave_count(2)
  for (size_t i = 0; i < n; ++i) cs[i] = as[2 * i] + as[2 * i + 1];  // LOOP
#elif defined(V_raw)
  // (d) Raw data() pointers behind the up-front precondition. Safe ONLY through that one check.
  const size_t n = c.size();
  REQUIRE(a.size() / 2 >= n);
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  for (size_t i = 0; i < n; ++i) cp[i] = ap[2 * i] + ap[2 * i + 1];  // LOOP
#elif defined(V_pairs)
  // (f) Paired loads: walk a two elements at a time with one index j = 2i; the loop is bounded by
  // c, and the precondition is the only check on a.
  const size_t n = c.size();
  REQUIRE(a.size() / 2 >= n);
  for (size_t i = 0, j = 0; i < n; ++i, j += 2) c[i] = a[j] + a[j + 1];  // LOOP
#else
#error "pick a variant with -DV_<name>"
#endif
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  if (short_mode(argc, argv)) {
    std::vector<int32_t> a(2 * n - 1), c(n);
    fill(a, 1);
    kern_m05_stride2(c, a);
    returned_after_short();
  }
  std::vector<int32_t> a(2 * n), c(n);
  fill(a, 1);
  kern_m05_stride2(c, a);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_m05_stride2(c, a);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
