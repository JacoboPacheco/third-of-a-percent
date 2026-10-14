// Shared by the real-program drivers (realworld/PLAN.md): clock, fixed-seed generator, output hashes and
// the RESULT line. Each driver runs its workload once untimed, then `iters` times inside one
// CLOCK_MONOTONIC window, and prints
//   RESULT ns=<ns per iteration> iters=<n> checksum=<FNV-1a of the outputs> checksum_r=<the same over
//   the outputs rounded to 6 significant digits>
#pragma once
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>

namespace rw {

inline uint64_t now_ns() {
  timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return uint64_t(t.tv_sec) * 1000000000ull + uint64_t(t.tv_nsec);
}

struct Rng {  // xorshift64, fixed seed: the input is the same in every process and every build
  uint64_t s;
  explicit Rng(uint64_t seed) : s(seed ? seed : 88172645463325252ull) {}
  uint64_t next() {
    s ^= s << 13;
    s ^= s >> 7;
    s ^= s << 17;
    return s;
  }
  double uni() { return double(next() >> 11) * 0x1.0p-53; }  // [0, 1)
  double sym() { return 2.0 * uni() - 1.0; }                  // [-1, 1)
  uint32_t below(uint32_t n) { return uint32_t(next() % n); }
};

struct Hash {  // FNV-1a 64
  uint64_t h = 1469598103934665603ull;
  void bytes(const void* p, size_t n) {
    const unsigned char* c = static_cast<const unsigned char*>(p);
    for (size_t i = 0; i < n; ++i) h = (h ^ c[i]) * 1099511628211ull;
  }
  template <class T>
  void pod(const T& v) { bytes(&v, sizeof v); }
  // 6 significant digits, so last-digit differences in floating point do not change it
  void round6(double x) {
    if (!std::isfinite(x)) { pod(x); return; }
    if (x == 0.0) { pod(int64_t(0)); pod(int32_t(0)); return; }
    int e = int(std::floor(std::log10(std::fabs(x))));
    int64_t q = int64_t(std::llround(x / std::pow(10.0, e - 5)));
    pod(q);
    pod(int32_t(e));
  }
};

inline long iters_arg(int argc, char** argv) {
  long it = std::strtol(argv[argc - 1], nullptr, 10);
  if (it < 1) {
    std::fprintf(stderr, "the last argument is the iteration count (>= 1)\n");
    std::exit(2);
  }
  return it;
}

inline void report(uint64_t t0, uint64_t t1, long iters, const Hash& exact, const Hash& rounded) {
  std::printf("RESULT ns=%.3f iters=%ld checksum=%016llx checksum_r=%016llx\n", double(t1 - t0) / double(iters),
              iters, (unsigned long long)exact.h, (unsigned long long)rounded.h);
  std::fflush(stdout);
}

[[noreturn]] inline void fail(const char* what) {
  std::fprintf(stderr, "failed: %s\n", what);
  std::exit(3);
}

}  // namespace rw
