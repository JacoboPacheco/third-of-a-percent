// {fmt} 11.0.2, header-only (control; realworld/PLAN.md): the S2/S3 program programs/fmt_format/fmt_format.cpp,
// copied unchanged in its work (the same seed, values and format string) and changed only to print the
// realworld RESULT line. Usage: fmt_format <count> <iters>
#include <fmt/format.h>

#include <cstdint>
#include <iterator>
#include <string>
#include <vector>

#include "rw_common.h"

static void run(const std::vector<int64_t>& ints, const std::vector<double>& dbls, std::string& out) {
  out.clear();
  for (size_t i = 0; i < ints.size(); ++i)
    fmt::format_to(std::back_inserter(out), "{} {:.6g} {:x}\n", ints[i], dbls[i], uint64_t(ints[i]));
}

int main(int argc, char** argv) {
  if (argc != 3) {
    std::fprintf(stderr, "usage: %s <count> <iters>\n", argv[0]);
    return 2;
  }
  const long iters = rw::iters_arg(argc, argv);
  size_t count = std::strtoull(argv[1], nullptr, 10);
  if (count < 1) return 2;
  std::vector<int64_t> ints(count);
  std::vector<double> dbls(count);
  uint64_t x = 88172645463325252ull;  // the S2 program's fixed seed
  for (size_t i = 0; i < count; ++i) {
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    ints[i] = int64_t(x >> 20) - (int64_t(1) << 42);
    dbls[i] = double(x >> 11) * 0x1.0p-53 * 1e6;
  }
  std::string out;
  run(ints, dbls, out);  // warm-up, not timed
  const uint64_t t0 = rw::now_ns();
  for (long it = 0; it < iters; ++it) {
    run(ints, dbls, out);
    asm volatile("" ::: "memory");
  }
  const uint64_t t1 = rw::now_ns();
  rw::Hash h;
  h.bytes(out.data(), out.size());
  rw::report(t0, t1, iters, h, h);
  return 0;
}
