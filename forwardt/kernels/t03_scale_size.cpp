// t03_scale_size: c[i] = a[i] * 2, i counting up, bound a.size() (the control for t04_scale_n; the bound is size()).
// The function has the parameters and the loop of fwn_scale_size in forwardn/source.cpp; the plan is forwardt/PLAN.md.
// Usage: ./t03_scale_size <n elements> <inner iterations>
#include "../../kernels/common.hpp"

__attribute__((noinline)) void kern_t03_scale_size(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < a.size(); ++i) c[i] = a[i] * 2;  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n), c(n);
  fill(a, 1);
  kern_t03_scale_size(c, a);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_t03_scale_size(c, a);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
