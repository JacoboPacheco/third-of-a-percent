// Loop-shape variants for the question "does the vectorization loss depend on two vectors?".
// Each function has exactly one // LOOP line; the compiler's remarks at that line decide the cell.
// Naming: var_<shape>_<variant>.  ctrl = the project's kernel, verbatim (two vectors, bound by one,
// indexed into the other).  inplace / onevec = one vector only.  iter = iterator form.
// same_scope = two vectors of equal size created in the same function (the compiler sees both sizes).
#include <cstddef>
#include <cstdint>
#include <vector>

// ---------------------------------------------------------------- reverse
__attribute__((noinline)) void var_rev_ctrl(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = a.size(); i-- > 0;) c[i] = a[i] * 2;  // LOOP
}
__attribute__((noinline)) void var_rev_inplace(std::vector<int32_t>& a) {
  for (size_t i = a.size(); i-- > 0;) a[i] *= 2;  // LOOP
}
__attribute__((noinline)) void var_rev_iter(std::vector<int32_t>& a) {
  for (auto it = a.rbegin(); it != a.rend(); ++it) *it *= 2;  // LOOP
}
__attribute__((noinline)) void var_rev_iter_two(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  auto o = c.rbegin();
  for (auto it = a.rbegin(); it != a.rend(); ++it, ++o) *o = *it * 2;  // LOOP
}
__attribute__((noinline)) int32_t var_rev_same_scope(size_t n) {
  std::vector<int32_t> a(n), c(n);
  for (size_t i = 0; i < n; ++i) a[i] = (int32_t)i;
  for (size_t i = a.size(); i-- > 0;) c[i] = a[i] * 2;  // LOOP
  return c[n / 2];
}

// ---------------------------------------------------------------- stride 2
__attribute__((noinline)) void var_stride2_ctrl(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < c.size(); ++i) c[i] = a[2 * i] + a[2 * i + 1];  // LOOP
}
// One vector: a[i] = a[2i] + a[2i+1] for i < size/2. Carries a true dependence at small i
// (a[i] is later read as a[2j]), so the loop may be refused in BOTH builds for that reason.
__attribute__((noinline)) void var_stride2_inplace(std::vector<int32_t>& a) {
  for (size_t i = 0; i < a.size() / 2; ++i) a[i] = a[2 * i] + a[2 * i + 1];  // LOOP
}
// One vector, no dependence: output in the upper half, input in the lower half.
__attribute__((noinline)) void var_stride2_onevec_halves(std::vector<int32_t>& m) {
  size_t h = m.size() / 2, q = h / 2;
  for (size_t i = 0; i < q; ++i) m[h + i] = m[2 * i] + m[2 * i + 1];  // LOOP
}
__attribute__((noinline)) void var_stride2_iter(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  auto p = a.begin();
  for (auto o = c.begin(); o != c.end(); ++o, p += 2) *o = p[0] + p[1];  // LOOP
}
__attribute__((noinline)) int32_t var_stride2_same_scope(size_t n) {
  std::vector<int32_t> a(2 * n), c(n);
  for (size_t i = 0; i < 2 * n; ++i) a[i] = (int32_t)i;
  for (size_t i = 0; i < c.size(); ++i) c[i] = a[2 * i] + a[2 * i + 1];  // LOOP
  return c[n / 2];
}

// ---------------------------------------------------------------- matrix multiply (inner loop)
__attribute__((noinline)) void var_matmul_ctrl(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& b, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      for (size_t j = 0; j < d; ++j) c[i * d + j] += aik * b[k * d + j];  // LOOP
    }
}
// One vector m of 3*d*d: c = m[0..dd), a = m[dd..2dd), b = m[2dd..3dd). Regions are disjoint but
// the compiler sees one base pointer and cannot prove it.
__attribute__((noinline)) void var_matmul_onevec_regions(std::vector<int32_t>& m, size_t d) {
  size_t dd = d * d;
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = m[dd + i * d + k];
      for (size_t j = 0; j < d; ++j) m[i * d + j] += aik * m[2 * dd + k * d + j];  // LOOP
    }
}
// One vector, truly in place (c, a, b are all m). The aliasing is real.
__attribute__((noinline)) void var_matmul_inplace(std::vector<int32_t>& m, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = m[i * d + k];
      for (size_t j = 0; j < d; ++j) m[i * d + j] += aik * m[k * d + j];  // LOOP
    }
}
// Iterator form of the inner loop: row iterators, index loop bound d.
__attribute__((noinline)) void var_matmul_iter(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                               const std::vector<int32_t>& b, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      auto cp = c.begin() + i * d;
      auto bp = b.begin() + k * d;
      for (size_t j = 0; j < d; ++j) cp[j] += aik * bp[j];  // LOOP
    }
}
// Iterator form, loop driven by the iterators themselves: range [cp, cp+d).
__attribute__((noinline)) void var_matmul_iter_range(std::vector<int32_t>& c, const std::vector<int32_t>& a,
                                                     const std::vector<int32_t>& b, size_t d) {
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      auto bp = b.begin() + k * d;
      for (auto cp = c.begin() + i * d, ce = cp + d; cp != ce; ++cp, ++bp) *cp += aik * *bp;  // LOOP
    }
}
__attribute__((noinline)) int32_t var_matmul_same_scope(size_t d) {
  std::vector<int32_t> a(d * d), b(d * d), c(d * d, 0);
  for (size_t i = 0; i < d * d; ++i) {
    a[i] = (int32_t)(i & 3);
    b[i] = (int32_t)((i >> 1) & 3);
  }
  for (size_t i = 0; i < d; ++i)
    for (size_t k = 0; k < d; ++k) {
      int32_t aik = a[i * d + k];
      for (size_t j = 0; j < d; ++j) c[i * d + j] += aik * b[k * d + j];  // LOOP
    }
  return c[d / 2];
}
