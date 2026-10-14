// k07_hist: h[a[i] & 255]++ (histogram, a data-dependent store; scalar in both builds by hypothesis).
// The counters keep growing across calls; the count per bucket stays far below 2^31 for any
// calibrated run (about 75 ms of calls), so no counter overflows.
#include "common.hpp"

__attribute__((noinline)) void kern_k07_hist(std::vector<int32_t>& h, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < a.size(); ++i) h[a[i] & 255]++;  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n), h(256, 0);
  fill(a, 1);
  kern_k07_hist(h, a);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_k07_hist(h, a);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(h));
  return 0;
}
