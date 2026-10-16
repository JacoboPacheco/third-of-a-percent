// src/emul_matmul.cpp with 32-bit indices and a 32-bit size in the check (the only change): the
// compare that guards each element is then a 32-bit compare instead of a 64-bit compare.
#include <cstddef>
#include <cstdint>

struct Vec {
  int32_t* begin_;
  int32_t* end_;
  int32_t* cap_;
};

template <bool On, class V>
static inline auto& at(V& v, uint32_t n) {
  if (On && __builtin_expect(!(n < uint32_t(v.end_ - v.begin_)), 0)) __builtin_trap();
  return v.begin_[n];
}

#ifndef CHK_A
#define CHK_A 0
#endif
#ifndef CHK_B
#define CHK_B 0
#endif
#ifndef CHK_C
#define CHK_C 0
#endif

__attribute__((noinline)) void kern_emul32_matmul(Vec& c, const Vec& a, const Vec& b, uint32_t d) {
  for (uint32_t i = 0; i < d; ++i)
    for (uint32_t k = 0; k < d; ++k) {
      int32_t aik = at<CHK_A>(a, i * d + k);
      for (uint32_t j = 0; j < d; ++j) at<CHK_C>(c, i * d + j) += aik * at<CHK_B>(b, k * d + j);  // LOOP
    }
}
