// Forward loops with a variable bound, for Compiler Explorer. Compile-only; see PLAN.md.
// Each function is noinline and carries one // LOOP comment; the compiler's remarks at that line decide the cell.
#include <cstddef>
#include <cstdint>
#include <vector>

// ---- reductions over one vector
__attribute__((noinline)) void fwn_sum_size(const std::vector<int32_t>& a, int64_t* out) {
  int64_t s = 0;
  for (size_t i = 0; i < a.size(); ++i) s += a[i];  // LOOP
  *out = s;
}
__attribute__((noinline)) void fwn_sum_n_size_t(const std::vector<int32_t>& a, size_t n, int64_t* out) {
  int64_t s = 0;
  for (size_t i = 0; i < n; ++i) s += a[i];  // LOOP
  *out = s;
}
__attribute__((noinline)) void fwn_sum_n_int(const std::vector<int32_t>& a, int n, int64_t* out) {
  int64_t s = 0;
  for (int i = 0; i < n; ++i) s += a[i];  // LOOP
  *out = s;
}
__attribute__((noinline)) void fwn_sum_n_u32(const std::vector<int32_t>& a, uint32_t n, int64_t* out) {
  int64_t s = 0;
  for (uint32_t i = 0; i < n; ++i) s += a[i];  // LOOP
  *out = s;
}
__attribute__((noinline)) void fwn_sum_n_i64(const std::vector<int32_t>& a, int64_t n, int64_t* out) {
  int64_t s = 0;
  for (int64_t i = 0; i < n; ++i) s += a[i];  // LOOP
  *out = s;
}
__attribute__((noinline)) void fwn_sum_int_size(const std::vector<int32_t>& a, int64_t* out) {
  int64_t s = 0;
  for (int i = 0; i < (int)a.size(); ++i) s += a[i];  // LOOP
  *out = s;
}
struct FwnBox {
  int n_;
  std::vector<int32_t> v;
};
__attribute__((noinline)) void fwn_sum_member(const FwnBox& b, int64_t* out) {
  int64_t s = 0;
  for (int i = 0; i < b.n_; ++i) s += b.v[i];  // LOOP
  *out = s;
}
struct FwnOut {
  int num;
  std::vector<int32_t> cat;
};
__attribute__((noinline)) void fwn_sum_ptr_member(const FwnOut* o, int64_t* out) {
  int64_t s = 0;
  for (int i = 0; i < o->num; ++i) s += o->cat[i];  // LOOP
  *out = s;
}
__attribute__((noinline)) void fwn_dot_n(const std::vector<int32_t>& a, const std::vector<int32_t>& b, size_t n,
                                         int64_t* out) {
  int64_t s = 0;
  for (size_t i = 0; i < n; ++i) s += (int64_t)a[i] * b[i];  // LOOP
  *out = s;
}

// ---- writes
__attribute__((noinline)) void fwn_scale_size(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  for (size_t i = 0; i < a.size(); ++i) c[i] = a[i] * 2;  // LOOP
}
__attribute__((noinline)) void fwn_scale_n_size_t(std::vector<int32_t>& c, const std::vector<int32_t>& a, size_t n) {
  for (size_t i = 0; i < n; ++i) c[i] = a[i] * 2;  // LOOP
}
__attribute__((noinline)) void fwn_scale_n_int(std::vector<int32_t>& c, const std::vector<int32_t>& a, int n) {
  for (int i = 0; i < n; ++i) c[i] = a[i] * 2;  // LOOP
}
__attribute__((noinline)) void fwn_scale_offset(std::vector<int32_t>& c, const std::vector<int32_t>& a, int n,
                                                int off) {
  for (int i = 0; i < n; ++i) c[i + off] = a[i];  // LOOP
}
__attribute__((noinline)) void fwn_two_stores(std::vector<int32_t>& c, std::vector<int32_t>& d,
                                              const std::vector<int32_t>& a, int n) {
  for (int i = 0; i < n; ++i) {  // LOOP
    c[i] = a[i] * 2;
    d[i] = a[i] + 1;
  }
}
struct FwnWork {
  int n_;
  std::vector<int32_t> c, a;
  void run();
};
__attribute__((noinline)) void FwnWork::run() {
  for (int i = 0; i < n_; ++i) c[i] = a[i] * 2;  // LOOP
}
__attribute__((noinline)) void fwn_inplace_n(std::vector<int32_t>& c, size_t n) {
  for (size_t i = 0; i < n; ++i) c[i] *= 2;  // LOOP
}
__attribute__((noinline)) void fwn_fill_n(std::vector<int32_t>& c, int n) {
  for (int i = 0; i < n; ++i) c[i] = i * 3;  // LOOP
}

// ---- control without a per-element check
__attribute__((noinline)) void fwn_rangefor(std::vector<int32_t>& c) {
  for (auto& x : c) x *= 2;  // LOOP
}
