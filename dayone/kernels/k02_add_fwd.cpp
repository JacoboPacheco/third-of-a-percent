// k02_add_fwd: c[i] = a[i] + b[i], i counting up, bound a.size() (forward two-array add; negative control).
#include "common.hpp"

__attribute__((noinline)) void kern_k02_add_fwd(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                                const std::vector<int32_t>& b) {
  for (size_t i = 0; i < a.size(); ++i) c[i] = a[i] + b[i];  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n), b(n), c(n);
  fill(a, 1);
  fill(b, 2);
  kern_k02_add_fwd(c, a, b);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_k02_add_fwd(c, a, b);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
