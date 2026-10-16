// Same loop as src/emul_matmul.cpp, with the data pointer and the size of b and c read into locals
// before the inner loop, so no pointer load sits inside it. CHK_B / CHK_C turn the two checks on.
#include <cstddef>
#include <cstdint>

struct Vec {
  int32_t* begin_;
  int32_t* end_;
  int32_t* cap_;
};

#ifndef CHK_B
#define CHK_B 0
#endif
#ifndef CHK_C
#define CHK_C 0
#endif

__attribute__((noinline)) void kern_emul_hoist(Vec& c, const Vec& a, const Vec& b, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      size_t an = size_t(a.end_ - a.begin_);
      if (!(i * d + k < an)) __builtin_trap();
      int32_t aik = a.begin_[i * d + k];
      int32_t* cp = c.begin_;
      size_t cn = size_t(c.end_ - c.begin_);
      const int32_t* bp = b.begin_;
      size_t bn = size_t(b.end_ - b.begin_);
      for (size_t j = 0; j < d; ++j) {  // LOOP
        size_t ci = i * d + j, bi = k * d + j;
        if (CHK_C && __builtin_expect(!(ci < cn), 0)) __builtin_trap();
        if (CHK_B && __builtin_expect(!(bi < bn), 0)) __builtin_trap();
        cp[ci] += aik * bp[bi];
      }
    }
}
