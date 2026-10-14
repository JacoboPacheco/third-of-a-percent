// k08_matmul: d x d matrices, order i-k-j, c[i*d+j] += a[i*d+k] * b[k*d+j] (inner loop forward and
// contiguous; stays vectorized by hypothesis). The first argument is the dimension d, not an element count.
// Inputs are masked to 0..3 so c grows by at most 9*d per call and never overflows int32 in a calibrated run.
#include "common.hpp"

__attribute__((noinline)) void kern_k08_matmul(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& b, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      for (size_t j = 0; j < d; ++j) c[i * d + j] += aik * b[k * d + j];  // LOOP
    }
}

int main(int argc, char** argv) {
  size_t d;
  long iters;
  parse_args(argc, argv, d, iters);
  std::vector<int32_t> a(d * d), b(d * d), c(d * d, 0);
  fill(a, 1);
  fill(b, 2);
  for (auto& e : a) e &= 3;
  for (auto& e : b) e &= 3;
  kern_k08_matmul(c, a, b, d);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_k08_matmul(c, a, b, d);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(d, iters, t1 - t0, checksum(c));
  return 0;
}
