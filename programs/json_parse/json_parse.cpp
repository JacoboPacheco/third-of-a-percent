// json_parse: nlohmann/json v3.11.3 (json.hpp from the release assets, programs/json_parse/fetch.sh) parsing twitter.json.
// Usage: ./json_parse <file> <iters>
// Prints: mode=<hardening mode> iters=<iters> ns=<ns per parse> checksum=<hex>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include <sstream>
#include <string>

#include "json.hpp"

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

// Walks the whole document so the parse result is used and its shape is part of the checksum.
static uint64_t walk(const nlohmann::json& j, uint64_t h) {
  h = h * 1099511628211ull ^ uint64_t(j.type());
  if (j.is_object()) {
    for (auto it = j.begin(); it != j.end(); ++it) {
      for (char ch : it.key()) h = (h ^ uint8_t(ch)) * 1099511628211ull;
      h = walk(it.value(), h);
    }
  } else if (j.is_array()) {
    for (size_t i = 0; i < j.size(); ++i) h = walk(j[i], h);
  } else if (j.is_string()) {
    for (char ch : j.get_ref<const std::string&>()) h = (h ^ uint8_t(ch)) * 1099511628211ull;
  } else if (j.is_number_integer()) {
    h ^= uint64_t(j.get<int64_t>());
  } else if (j.is_number_float()) {
    double d = j.get<double>();
    uint64_t bits;
    __builtin_memcpy(&bits, &d, 8);
    h ^= bits;
  } else if (j.is_boolean()) {
    h ^= j.get<bool>() ? 3 : 5;
  }
  return h;
}

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: %s <file> <iters>\n", argv[0]);
    return 2;
  }
  std::ifstream in(argv[1], std::ios::binary);
  std::stringstream ss;
  ss << in.rdbuf();
  const std::string text = ss.str();
  long iters = std::strtol(argv[2], nullptr, 10);
  if (text.empty() || iters < 1) {
    std::fprintf(stderr, "bad input\n");
    return 2;
  }
  uint64_t h = walk(nlohmann::json::parse(text), 1469598103934665603ull);  // warm-up, not timed
  uint64_t t0 = now_ns();
  uint64_t acc = 0;
  for (long it = 0; it < iters; ++it) {
    nlohmann::json j = nlohmann::json::parse(text);
    acc += j.size();
    asm volatile("" ::: "memory");
  }
  uint64_t t1 = now_ns();
  std::printf("mode=%d iters=%ld ns=%.3f checksum=%016llx size=%llu\n", int(PROGRAM_MODE), iters,
              double(t1 - t0) / double(iters), (unsigned long long)h,
              (unsigned long long)(acc / uint64_t(iters)));
  return 0;
}
