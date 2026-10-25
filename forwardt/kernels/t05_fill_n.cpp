// t05_fill_n: c[i] = i * 3, i counting up (int), bound n (int), a run-time argument that equals the length of c.
// The function has the parameters and the loop of fwn_fill_n in forwardn/source.cpp; the plan is forwardt/PLAN.md.
// Usage: ./t05_fill_n <n elements> <inner iterations>
#include <climits>

#include "../../kernels/common.hpp"

__attribute__((noinline)) void kern_t05_fill_n(std::vector<int32_t>& c, int n) {
  for (int i = 0; i < n; ++i) c[i] = i * 3;  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  if (n > size_t(INT_MAX / 3)) {  // the bound is an int and i * 3 must not overflow
    std::fprintf(stderr, "n too large for an int bound\n");
    return 2;
  }
  std::vector<int32_t> c(n);
  kern_t05_fill_n(c, static_cast<int>(n));  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_t05_fill_n(c, static_cast<int>(n));
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
