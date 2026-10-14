// k05_stride2: c[i] = a[2*i] + a[2*i+1], bound c.size() (stride-2 loop; positive control by hypothesis).
#include "common.hpp"

__attribute__((noinline)) void kern_k05_stride2(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < c.size(); ++i) c[i] = a[2 * i] + a[2 * i + 1];  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(2 * n), c(n);
  fill(a, 1);
  kern_k05_stride2(c, a);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_k05_stride2(c, a);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
