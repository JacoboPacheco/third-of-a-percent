// The 8 loop functions of kernels/kNN_*.cpp, copied verbatim, in one file for Compiler Explorer.
// Each loop carries a // LOOP comment; the compiler's remarks at that line decide the cell.
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

__attribute__((noinline)) void kern_k06_gather(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& idx) {
  for (size_t i = 0; i < idx.size(); ++i) c[i] = a[idx[i]];  // LOOP
}

__attribute__((noinline)) void kern_k07_hist(std::vector<int32_t>& h, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < a.size(); ++i) h[a[i] & 255]++;  // LOOP
}

__attribute__((noinline)) void kern_k08_matmul(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& b, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      for (size_t j = 0; j < d; ++j) c[i * d + j] += aik * b[k * d + j];  // LOOP
    }
}
