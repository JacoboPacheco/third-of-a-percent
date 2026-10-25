// t01_sum_size: s += a[i], i counting up, bound a.size() (the control for t02_sum_n; the bound is size()).
// The function has the parameters and the loop of fwn_sum_size in forwardn/source.cpp; the plan is forwardt/PLAN.md.
// Usage: ./t01_sum_size <n elements> <inner iterations>
#include "../../kernels/common.hpp"

__attribute__((noinline)) void kern_t01_sum_size(const std::vector<int32_t>& a, int64_t* out) {
  int64_t s = 0;
  for (size_t i = 0; i < a.size(); ++i) s += a[i];  // LOOP
  *out = s;
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n);
  fill(a, 1);
  int64_t out = 0;
  kern_t01_sum_size(a, &out);  // warm-up, not timed
  int64_t acc = out;
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_t01_sum_size(a, &out);
    acc += out;
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, uint64_t(acc) / uint64_t(iters + 1));
  return 0;
}
