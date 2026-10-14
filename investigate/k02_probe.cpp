// Probe for the k02_add_fwd investigation: the kernel is the repo's own file, included verbatim
// (its main renamed away), so kern_k02_add_fwd is compiled from the same source line for line.
// What the probe adds: control over WHERE the three vectors land, and a print of the addresses.
//
// PROBE_OFFS unset      -> the normal allocator (libc++ operator new -> glibc malloc), addresses printed.
// PROBE_OFFS="0,16,32"  -> a, b, c are placed at a 4096-aligned base each (one fresh page run per
//                          vector) plus the given byte offsets, so their positions mod 4096 are fixed.
// Output: the same one line as every kernel, plus " a=<addr mod 4096> b=... c=..." at the end.
#include <cstring>
#include <new>

#define main k02_original_main
#include "../kernels/k02_add_fwd.cpp"
#undef main

static long g_offs[3] = {0, 0, 0};
static bool g_arena = false;
static int g_count = 0;
static char* g_cursor = nullptr;
static char* g_end = nullptr;

void* operator new(std::size_t sz) {
  if (g_arena && g_count < 3) {
    // each vector gets its own 4096-aligned run, then the requested offset inside the page
    uintptr_t p = (reinterpret_cast<uintptr_t>(g_cursor) + 4095) & ~uintptr_t(4095);
    p += uintptr_t(g_offs[g_count]);
    char* r = reinterpret_cast<char*>(p);
    g_cursor = r + sz + 4096;  // a guard page's worth of distance to the next vector
    if (g_cursor > g_end) std::abort();
    ++g_count;
    return r;
  }
  void* r = std::malloc(sz ? sz : 1);
  if (!r) throw std::bad_alloc();
  return r;
}
void operator delete(void* p) noexcept {
  if (g_arena && p >= (void*)(g_end - (64l << 20)) && p < (void*)g_end) return;  // arena memory
  std::free(p);
}
void operator delete(void* p, std::size_t) noexcept { operator delete(p); }

int main(int argc, char** argv) {
  size_t n;
  long iters;
  parse_args(argc, argv, n, iters);
  if (const char* s = std::getenv("PROBE_OFFS")) {
    std::sscanf(s, "%ld,%ld,%ld", &g_offs[0], &g_offs[1], &g_offs[2]);
    size_t arena_bytes = 64l << 20;
    char* arena = static_cast<char*>(std::aligned_alloc(4096, arena_bytes));
    std::memset(arena, 0, arena_bytes);
    g_cursor = arena;
    g_end = arena + arena_bytes;
    g_arena = true;
  }
  std::vector<int32_t> a(n), b(n), c(n);  // the arena serves only these three (g_count < 3)
  fill(a, 1);
  fill(b, 2);
  kern_k02_add_fwd(c, a, b);  // warm-up, not timed
  BARRIER();
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    kern_k02_add_fwd(c, a, b);
    BARRIER();
  }
  uint64_t t1 = now_ns();
  std::printf("mode=%d n=%zu iters=%ld ns=%.3f checksum=%016llx a=%lu b=%lu c=%lu\n", int(KERNEL_MODE), n, iters,
              double(t1 - t0) / double(iters), (unsigned long long)checksum(c),
              (unsigned long)(reinterpret_cast<uintptr_t>(a.data()) & 4095),
              (unsigned long)(reinterpret_cast<uintptr_t>(b.data()) & 4095),
              (unsigned long)(reinterpret_cast<uintptr_t>(c.data()) & 4095));
  return 0;
}
