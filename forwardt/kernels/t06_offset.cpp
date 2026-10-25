// t06_offset: c[i + off] = a[i], i counting up (int), bound n (int) and offset off (int), both run-time arguments.
// n equals the length of a, c has n + off elements, and off is 0 in every run of the plan (it comes from argv so that
// the compiler cannot see it). The function has the parameters and the loop of fwn_scale_offset in
// forwardn/source.cpp; the plan is forwardt/PLAN.md.
// Usage: ./t06_offset <n elements> <inner iterations> <off>
#include <climits>

#include "../../kernels/common.hpp"

__attribute__((noinline)) void kern_t06_offset(std::vector<int32_t>& c, const std::vector<int32_t>& a, int n, int off) {
  for (int i = 0; i < n; ++i) c[i + off] = a[i];  // LOOP
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);  // reads <n> and <iters>; <off> follows
  if (argc < 4) {
    std::fprintf(stderr, "usage: %s <n> <iters> <off>\n", argv[0]);
    return 2;
  }
  long off_arg = std::strtol(argv[3], nullptr, 10);
  if (off_arg < 0 || off_arg > 1 << 20 || n > size_t(INT_MAX / 2)) {  // a negative offset would index below c
    std::fprintf(stderr, "bad off or n too large for an int bound\n");
    return 2;
  }
  int off = static_cast<int>(off_arg);
  std::vector<int32_t> a(n), c(n + size_t(off));
  fill(a, 1);
  kern_t06_offset(c, a, static_cast<int>(n), off);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_t06_offset(c, a, static_cast<int>(n), off);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
