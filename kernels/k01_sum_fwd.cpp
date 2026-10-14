// k01_sum_fwd: s += a[i], i counting up (forward one-array sum; negative control).
#include "common.hpp"

__attribute__((noinline)) int64_t kern_k01_sum_fwd(const std::vector<int32_t>& a) {
  int64_t s = 0;
  for (size_t i = 0; i < a.size(); ++i) s += a[i];  // LOOP
  return s;
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n);
  fill(a, 1);
  int64_t acc = kern_k01_sum_fwd(a);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    acc += kern_k01_sum_fwd(a);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, uint64_t(acc) / uint64_t(iters + 1));
  return 0;
}
