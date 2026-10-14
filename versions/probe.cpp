// Macro probe (versions/PLAN.md): does _LIBCPP_HARDENING_MODE_FAST trap on an out-of-range vector index
// on this toolchain? Built NONE and FAST by run_version.py. NONE must run to the end and print "ok";
// FAST must die from a signal (ud2, trap or abort). The index is one past the end of a 4-element vector
// (a 16-byte heap block), read through a volatile so the compiler cannot remove it.
#include <cstdio>
#include <vector>

int main(int argc, char**) {
  std::vector<int> v(4, 1);
  volatile std::size_t i = 3 + static_cast<std::size_t>(argc);  // argc is 1: index 4, one past the end
  volatile int x = v[i];
  (void)x;
  std::puts("ok");
  return 0;
}
