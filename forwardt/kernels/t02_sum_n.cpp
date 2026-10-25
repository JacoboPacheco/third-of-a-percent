// t02_sum_n: s += a[i], i counting up, bound n (size_t), a run-time argument that equals the length of a.
// The function has the parameters and the loop of fwn_sum_n_size_t in forwardn/source.cpp; the plan is forwardt/PLAN.md.
// Usage: ./t02_sum_n <n elements> <inner iterations>
#include "../../kernels/common.hpp"

__attribute__((noinline)) void kern_t02_sum_n(const std::vector<int32_t>& a, size_t n, int64_t* out) {
  int64_t s = 0;
  for (size_t i = 0; i < n; ++i) s += a[i];  // LOOP
  *out = s;
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n);
  fill(a, 1);
  int64_t out = 0;
  kern_t02_sum_n(a, n, &out);  // warm-up, not timed
  int64_t acc = out;
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_t02_sum_n(a, n, &out);
    acc += out;
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, uint64_t(acc) / uint64_t(iters + 1));
  return 0;
}
