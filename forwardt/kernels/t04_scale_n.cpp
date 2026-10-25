// t04_scale_n: c[i] = a[i] * 2, i counting up, bound n (size_t), a run-time argument that equals the length of a and c.
// The function has the parameters and the loop of fwn_scale_n_size_t in forwardn/source.cpp; the plan is forwardt/PLAN.md.
// Usage: ./t04_scale_n <n elements> <inner iterations>
#include "../../kernels/common.hpp"

__attribute__((noinline)) void kern_t04_scale_n(std::vector<int32_t>& c, const std::vector<int32_t>& a, size_t n) {
  for (size_t i = 0; i < n; ++i) c[i] = a[i] * 2;  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n), c(n);
  fill(a, 1);
  kern_t04_scale_n(c, a, n);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_t04_scale_n(c, a, n);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
