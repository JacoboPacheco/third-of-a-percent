// m06_gather: rewrites of kernels/k06_gather.cpp, c[i] = a[idx[i]], idx a fixed-seed permutation of 0..n-1.
// One variant per build, picked with -DV_<name>. The marked loop of each variant carries "// LOOP".
// Safety input ("short"): a has n - 1 elements, idx and c have n. idx holds n - 1 somewhere, so the
// original reads a[n-1] out of range. This check depends on the data (the value of idx[i]): no size
// comparison made before the loop can replace it.
#include <span>
#include "common.hpp"

__attribute__((noinline)) void kern_m06_gather(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& idx) {
#if defined(V_orig)
  // The original kernel, unchanged.
  for (size_t i = 0; i < idx.size(); ++i) c[i] = a[idx[i]];  // LOOP
#elif defined(V_pre)
  // (a) One up-front precondition on c's size; the check on a[idx[i]] stays (it depends on data).
  const size_t n = idx.size();
  REQUIRE(c.size() >= n);
  for (size_t i = 0; i < n; ++i) c[i] = a[idx[i]];  // LOOP
#elif defined(V_span)
  // (c) std::span for c and idx with the bound taken once; a[idx[i]] is still checked per element.
  const size_t n = idx.size();
  std::span<int32_t> cs = std::span<int32_t>(c).first(n);
  std::span<const int32_t> is(idx);
  std::span<const int32_t> as(a);
  for (size_t i = 0; i < n; ++i) cs[i] = as[size_t(is[i])];  // LOOP
#elif defined(V_clamp)
  // (f) Never read out of range, trap after the loop: each index is clamped into a's range (so every
  // load is in bounds), a flag remembers whether any index was out of range, and the program stops
  // after the loop if one was. c holds clamped values at that point, but the program does not go on.
  // Safe through the clamp and the final REQUIRE (not through hardening); assumes a is not empty.
  const size_t n = idx.size();
  REQUIRE(c.size() >= n && (n == 0 || !a.empty()));
  const int32_t* ip = idx.data();
  const int32_t* ap = a.data();
  int32_t* cp = c.data();
  const size_t last = a.size() - 1;
  size_t bad = 0;
  for (size_t i = 0; i < n; ++i) {  // LOOP
    size_t j = uint32_t(ip[i]);
    bad |= j > last;
    cp[i] = ap[j > last ? last : j];
  }
  REQUIRE(bad == 0);
#elif defined(V_validate)
  // (d) Validate every index in a first pass (an unsigned max, which vectorizes), then gather through
  // raw pointers. Safe ONLY through the two up-front checks; costs a second read of idx.
  const size_t n = idx.size();
  REQUIRE(c.size() >= n);
  const int32_t* ip = idx.data();
  uint32_t hi = 0;
  for (size_t i = 0; i < n; ++i) hi = uint32_t(ip[i]) > hi ? uint32_t(ip[i]) : hi;
  REQUIRE(n == 0 || size_t(hi) < a.size());  // a negative index becomes a huge unsigned one and fails
  const int32_t* ap = a.data();
  int32_t* cp = c.data();
  for (size_t i = 0; i < n; ++i) cp[i] = ap[uint32_t(ip[i])];  // LOOP
#elif defined(V_raw)
  // (d') Raw pointers behind the size check on c only: the index VALUES are not checked against a's
  // size (a may legally be any size the indices fit in, so no size check on a is implied). Expected UNSAFE.
  const size_t n = idx.size();
  REQUIRE(c.size() >= n);
  const int32_t* ip = idx.data();
  const int32_t* ap = a.data();
  int32_t* cp = c.data();
  for (size_t i = 0; i < n; ++i) cp[i] = ap[ip[i]];  // LOOP
#else
#error "pick a variant with -DV_<name>"
#endif
}

// Fisher-Yates shuffle driven by the same LCG as fill(), so every build sees the same permutation.
static void permutation(std::vector<int32_t>& idx, uint32_t seed) {
  for (size_t i = 0; i < idx.size(); ++i) idx[i] = int32_t(i);
  uint64_t x = seed;
  for (size_t i = idx.size() - 1; i > 0; --i) {
    x = x * 6364136223846793005ull + 1442695040888963407ull;
    size_t j = size_t((x >> 33) % (i + 1));
    int32_t t = idx[i];
    idx[i] = idx[j];
    idx[j] = t;
  }
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  if (short_mode(argc, argv)) {
    std::vector<int32_t> a(n - 1), c(n), idx(n);
    fill(a, 1);
    permutation(idx, 3);
    kern_m06_gather(c, a, idx);
    returned_after_short();
  }
  std::vector<int32_t> a(n), c(n), idx(n);
  fill(a, 1);
  permutation(idx, 3);
  kern_m06_gather(c, a, idx);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_m06_gather(c, a, idx);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
