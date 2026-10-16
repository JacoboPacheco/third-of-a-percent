// Five of the project's loop functions, copied verbatim from kernels/kNN_*.cpp (written by make_sources.py).
// k01 forward sum, k02 forward add, k03 stencil (forward), k04 reverse, k05 stride-2.
#include <cstddef>
#include <cstdint>
#include <vector>

__attribute__((noinline)) int64_t kern_k01_sum_fwd(const std::vector<int32_t>& a) {
  int64_t s = 0;
  for (size_t i = 0; i < a.size(); ++i) s += a[i];  // LOOP
  return s;
}

__attribute__((noinline)) void kern_k02_add_fwd(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                                const std::vector<int32_t>& b) {
  for (size_t i = 0; i < a.size(); ++i) c[i] = a[i] + b[i];  // LOOP
}

__attribute__((noinline)) void kern_k03_stencil(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 1; i + 1 < a.size(); ++i) c[i] = a[i - 1] + a[i] + a[i + 1];  // LOOP
}

__attribute__((noinline)) void kern_k04_rev(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = a.size(); i-- > 0;) c[i] = a[i] * 2;  // LOOP
}

__attribute__((noinline)) void kern_k05_stride2(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < c.size(); ++i) c[i] = a[2 * i] + a[2 * i + 1];  // LOOP
}
