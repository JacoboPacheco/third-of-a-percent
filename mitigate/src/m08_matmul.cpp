// m08_matmul: rewrites of kernels/k08_matmul.cpp, d x d matrices, order i-k-j,
// c[i*d+j] += a[i*d+k] * b[k*d+j]. The first argument is the dimension d, not an element count.
// One variant per build, picked with -DV_<name>. The marked loop of each variant carries "// LOOP".
// Safety input ("short"): b has d*d - 1 elements, a and c have d*d. The original reads b[d*d-1]
// out of range (k = j = d - 1).
#include <algorithm>
#include <span>
#include "common.hpp"

__attribute__((noinline)) void kern_m08_matmul(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& b, size_t d) {
#if defined(V_orig)
  // The original kernel, unchanged.
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      for (size_t j = 0; j < d; ++j) c[i * d + j] += aik * b[k * d + j];  // LOOP
    }
#elif defined(V_pre)
  // (a) One up-front precondition (all three hold d*d elements), then the same operator[] loops.
  size_t dd;
  REQUIRE(!__builtin_mul_overflow(d, d, &dd) && a.size() >= dd && b.size() >= dd && c.size() >= dd);
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      for (size_t j = 0; j < d; ++j) c[i * d + j] += aik * b[k * d + j];  // LOOP
    }
#elif defined(V_span)
  // (c)+(f) Local row spans: subspan(row * d, d) is checked by libc++ hardening once per row, and
  // inside the row j < d == row.size(), which the compiler can see.
  for (size_t i = 0; i < d; ++i) {
    std::span<int32_t> crow = std::span<int32_t>(c).subspan(i * d, d);
    std::span<const int32_t> arow = std::span<const int32_t>(a).subspan(i * d, d);
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = arow[k];
      std::span<const int32_t> brow = std::span<const int32_t>(b).subspan(k * d, d);
      for (size_t j = 0; j < d; ++j) crow[j] += aik * brow[j];  // LOOP
    }
  }
#elif defined(V_span_il2)
  // (c)+(g) The span variant with the interleave count the NONE build picks (2).
  for (size_t i = 0; i < d; ++i) {
    std::span<int32_t> crow = std::span<int32_t>(c).subspan(i * d, d);
    std::span<const int32_t> arow = std::span<const int32_t>(a).subspan(i * d, d);
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = arow[k];
      std::span<const int32_t> brow = std::span<const int32_t>(b).subspan(k * d, d);
#pragma clang loop interleave_count(2)
      for (size_t j = 0; j < d; ++j) crow[j] += aik * brow[j];  // LOOP
    }
  }
#elif defined(V_rowptr)
  // (d)+(f) Raw local row pointers behind the up-front precondition. Safe ONLY through that check.
  size_t dd;
  REQUIRE(!__builtin_mul_overflow(d, d, &dd) && a.size() >= dd && b.size() >= dd && c.size() >= dd);
  for (size_t i = 0; i < d; ++i) {
    int32_t* crow = c.data() + i * d;
    const int32_t* arow = a.data() + i * d;
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = arow[k];
      const int32_t* brow = b.data() + k * d;
      for (size_t j = 0; j < d; ++j) crow[j] += aik * brow[j];  // LOOP
    }
  }
#elif defined(V_transform)
  // (e) std::transform over checked row spans: the subspans are checked, the algorithm is not.
  for (size_t i = 0; i < d; ++i) {
    std::span<int32_t> crow = std::span<int32_t>(c).subspan(i * d, d);
    std::span<const int32_t> arow = std::span<const int32_t>(a).subspan(i * d, d);
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = arow[k];
      std::span<const int32_t> brow = std::span<const int32_t>(b).subspan(k * d, d);
      std::transform(crow.begin(), crow.end(), brow.begin(), crow.begin(),
                     [aik](int32_t x, int32_t y) { return x + aik * y; });  // LOOP
    }
  }
#else
#error "pick a variant with -DV_<name>"
#endif
}

int main(int argc, char** argv) {
  size_t d;
  long iters;
  parse_args(argc, argv, d, iters);
  if (short_mode(argc, argv)) {
    std::vector<int32_t> a(d * d), b(d * d - 1), c(d * d, 0);
    fill(a, 1);
    fill(b, 2);
    for (auto& e : a) e &= 3;
    for (auto& e : b) e &= 3;
    kern_m08_matmul(c, a, b, d);
    returned_after_short();
  }
  std::vector<int32_t> a(d * d), b(d * d), c(d * d, 0);
  fill(a, 1);
  fill(b, 2);
  for (auto& e : a) e &= 3;
  for (auto& e : b) e &= 3;
  kern_m08_matmul(c, a, b, d);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_m08_matmul(c, a, b, d);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(d, iters, t1 - t0, checksum(c));
  return 0;
}
