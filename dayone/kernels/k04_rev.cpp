// k04_rev: c[i] = a[i] * 2, i counting down (reverse loop; positive control by hypothesis).
#include "common.hpp"

__attribute__((noinline)) void kern_k04_rev(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = a.size(); i-- > 0;) c[i] = a[i] * 2;  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n), c(n);
  fill(a, 1);
  kern_k04_rev(c, a);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_k04_rev(c, a);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
