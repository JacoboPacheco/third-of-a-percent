// The same loop as kern_k08_matmul, without any library header. Vec has the layout of
// std::vector<int32_t> (three pointers) and an element check of the shape libc++'s hardened
// operator[] has: trap when the index is not below size(), size() = end - begin, begin loaded on
// every access. CHK_A, CHK_B and CHK_C (0 or 1, set with -D) turn the check on a[], b[] and c[] on.
#include <cstddef>
#include <cstdint>

struct Vec {
  int32_t* begin_;
  int32_t* end_;
  int32_t* cap_;
};

template <bool On, class V>
static inline auto& at(V& v, size_t n) {
  if (On && __builtin_expect(!(n < size_t(v.end_ - v.begin_)), 0)) __builtin_trap();
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

__attribute__((noinline)) void kern_emul_matmul(Vec& c, const Vec& a, const Vec& b, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = at<CHK_A>(a, i * d + k);
      for (size_t j = 0; j < d; ++j) at<CHK_C>(c, i * d + j) += aik * at<CHK_B>(b, k * d + j);  // LOOP
    }
}
