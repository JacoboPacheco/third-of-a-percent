// k06_gather: c[i] = a[idx[i]], idx a fixed-seed permutation of 0..n-1 (indirect load; scalar in both builds by hypothesis).
#include "common.hpp"

__attribute__((noinline)) void kern_k06_gather(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& idx) {
  for (size_t i = 0; i < idx.size(); ++i) c[i] = a[idx[i]];  // LOOP
}

// Fisher-Yates shuffle driven by the same LCG as fill(), so every build sees the same permutation.
static void permutation(std::vector<int32_t>& idx, uint32_t seed) {
  for (size_t i = 0; i < idx.size(); ++i) idx[i] = int32_t(i);
  uint64_t x = seed;
  for (size_t i = idx.size() - 1; i > 0; --i) {
    x = x * 6364136223846793005ull + 1442695040888963407ull;
    size_t j = size_t((x >> 33) % (i + 1));
    int32_t t = idx[i];
    idx[i] = idx[j];
    idx[j] = t;
  }
}

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  std::vector<int32_t> a(n), c(n), idx(n);
  fill(a, 1);
  permutation(idx, 3);
  kern_k06_gather(c, a, idx);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_k06_gather(c, a, idx);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  report(n, iters, t1 - t0, checksum(c));
  return 0;
}
