// k03_stencil: c[i] = a[i-1] + a[i] + a[i+1] (forward three-point stencil).
#include "common.hpp"

__attribute__((noinline)) void kern_k03_stencil(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 1; i + 1 < a.size(); ++i) c[i] = a[i - 1] + a[i] + a[i + 1];  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n), c(n);
  fill(a, 1);
  kern_k03_stencil(c, a);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_k03_stencil(c, a);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
