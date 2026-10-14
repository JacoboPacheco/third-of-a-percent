// Shared pieces of the kernels: input fill, checksum, timing, the driver.
// Usage of every kernel binary: ./kNN <n elements> <inner iterations>
// Prints one line: mode=<hardening mode> n=<n> iters=<iters> ns=<ns per call> checksum=<hex>
#pragma once
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <vector>

#ifndef _LIBCPP_HARDENING_MODE
#define KERNEL_MODE -1
#else
#define KERNEL_MODE _LIBCPP_HARDENING_MODE
#endif

static inline uint64_t now_ns() {
  timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return uint64_t(t.tv_sec) * 1000000000ull + uint64_t(t.tv_nsec);
}

// Tells the compiler that any memory may have changed, so a call cannot be hoisted or merged.
#define BARRIER() asm volatile("" ::: "memory")

// Small non-negative values (0..65535) so no sum or doubling overflows.
static inline void fill(std::vector<int32_t>& v, uint32_t seed) {
  uint32_t x = seed;
  for (auto& e : v) {
    x = x * 1664525u + 1013904223u;
    e = int32_t((x >> 8) & 0xFFFFu);
  }
}

static inline uint64_t checksum(const std::vector<int32_t>& v) {
  uint64_t h = 1469598103934665603ull;  // FNV-1a over the values
  for (int32_t e : v) {
    h ^= uint32_t(e);
    h *= 1099511628211ull;
  }
  return h;
}

static inline void parse_args(int argc, char** argv, size_t& n, long& iters) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: %s <n> <iters>\n", argv[0]);
    std::exit(2);
  }
  n = std::strtoull(argv[1], nullptr, 10);
  iters = std::strtol(argv[2], nullptr, 10);
  if (n < 4 || iters < 1) {
    std::fprintf(stderr, "bad arguments\n");
    std::exit(2);
  }
}

static inline void report(size_t n, long iters, uint64_t ns_total, uint64_t sum) {
  std::printf("mode=%d n=%zu iters=%ld ns=%.3f checksum=%016llx\n", int(KERNEL_MODE), n, iters,
              double(ns_total) / double(iters), (unsigned long long)sum);
}
