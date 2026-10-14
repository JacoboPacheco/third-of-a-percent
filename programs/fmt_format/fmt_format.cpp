// fmt_format: {fmt} 11.0.2 (header-only mode, programs/fmt_format/fetch.sh) formatting a fixed, seeded list of
// numbers into a std::string.
// Usage: ./fmt_format <count> <iters> [input-dump-file]
// Prints: mode=<hardening mode> iters=<iters> ns=<ns per iteration> checksum=<hex>
// With a third argument the generated input (count int64 values, then count doubles, raw bytes) is also
// written to that file, so the harness can record its sha256; the dump happens before timing starts.
#define FMT_HEADER_ONLY
#include <fmt/format.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <iterator>
#include <string>
#include <vector>

#ifndef _LIBCPP_HARDENING_MODE
#define PROGRAM_MODE -1
#else
#define PROGRAM_MODE _LIBCPP_HARDENING_MODE
#endif

static uint64_t now_ns() {
  timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return uint64_t(t.tv_sec) * 1000000000ull + uint64_t(t.tv_nsec);
}

static void run(const std::vector<int64_t>& ints, const std::vector<double>& dbls, std::string& out) {
  out.clear();
  for (size_t i = 0; i < ints.size(); ++i)
    fmt::format_to(std::back_inserter(out), "{} {:.6g} {:x}\n", ints[i], dbls[i], uint64_t(ints[i]));
}

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: %s <count> <iters>\n", argv[0]);
    return 2;
  }
  size_t count = std::strtoull(argv[1], nullptr, 10);
  long iters = std::strtol(argv[2], nullptr, 10);
  if (count < 1 || iters < 1) return 2;
  std::vector<int64_t> ints(count);
  std::vector<double> dbls(count);
  uint64_t x = 88172645463325252ull;  // fixed seed: the input is the same on every run
  for (size_t i = 0; i < count; ++i) {
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    ints[i] = int64_t(x >> 20) - (int64_t(1) << 42);
    dbls[i] = double(x >> 11) * 0x1.0p-53 * 1e6;
  }
  if (argc > 3) {
    std::FILE* f = std::fopen(argv[3], "wb");
    if (!f) return 2;
    std::fwrite(ints.data(), sizeof(int64_t), count, f);
    std::fwrite(dbls.data(), sizeof(double), count, f);
    std::fclose(f);
  }
  std::string out;
  run(ints, dbls, out);  // warm-up, not timed
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    run(ints, dbls, out);
    asm volatile("" ::: "memory");
  }
  uint64_t t1 = now_ns();
  uint64_t h = 1469598103934665603ull;
  for (char ch : out) h = (h ^ uint8_t(ch)) * 1099511628211ull;
  std::printf("mode=%d iters=%ld ns=%.3f checksum=%016llx bytes=%zu\n", int(PROGRAM_MODE), iters,
              double(t1 - t0) / double(iters), (unsigned long long)h, out.size());
  return 0;
}
