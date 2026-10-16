// kern_k08_matmul from kernels/k08_matmul.cpp, copied verbatim (the function only, no main).
#include <cstddef>
#include <cstdint>
#include <vector>

__attribute__((noinline)) void kern_k08_matmul(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& b, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      for (size_t j = 0; j < d; ++j) c[i * d + j] += aik * b[k * d + j];  // LOOP
    }
}
