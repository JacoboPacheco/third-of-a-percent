// Stride-2 loops with the check written by hand on raw pointers (no libc++ hardening macro involved).
// They vary the number of in-loop checks, the range of the bound `an` (the size of `a`) and the way the
// check is written:
//   one check `2*i+1 >= an` (as variants2.cpp), or two checks (`2*i` and `2*i+1`, as kern_k05_stride2);
//   the bound as it is (full range), masked, limited with std::min, or limited with __builtin_assume;
//   the check written on the counter itself (`i >= an / 2`).
// Every function has one "// LOOP" line.
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <vector>

// one check, bound as it is
__attribute__((noinline)) void v3_one_plain(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = a.size();
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// one check written on the counter, bound as it is
__attribute__((noinline)) void v3_one_half(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = a.size();
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (i >= an / 2) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// one check, bound limited to 2^40 with std::min
__attribute__((noinline)) void v3_one_min(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = std::min<size_t>(a.size(), size_t(1) << 40);
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// one check, bound as it is, with an assumption that it is below 2^40
__attribute__((noinline)) void v3_one_assume(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = a.size();
  __builtin_assume(an < (size_t(1) << 40));
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// two checks (2*i and 2*i+1), bound as it is
__attribute__((noinline)) void v3_two_plain(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = a.size();
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (2 * i >= an) __builtin_trap();
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}

// two checks, bound masked with SIZE_MAX >> 1
__attribute__((noinline)) void v3_two_masked(std::vector<int32_t>& c, const std::vector<int32_t>& a) {
  int32_t* cp = c.data();
  const int32_t* ap = a.data();
  const size_t n = c.size();
  const size_t an = a.size() & (SIZE_MAX >> 1);
  for (size_t i = 0; i < n; ++i) {  // LOOP
    if (2 * i >= an) __builtin_trap();
    if (2 * i + 1 >= an) __builtin_trap();
    cp[i] = ap[2 * i] + ap[2 * i + 1];
  }
}
