// pugixml_parse: pugixml (pinned release) parsing a fixed, generated XML document. Fallback second program,
// used only if fmt does not build. Usage: ./pugixml_parse <records> <iters>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <string>

#include "pugixml.hpp"

#ifndef _LIBCPP_HARDENING_MODE
#define DAYONE_MODE -1
#else
#define DAYONE_MODE _LIBCPP_HARDENING_MODE
#endif

static uint64_t now_ns() {
  timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return uint64_t(t.tv_sec) * 1000000000ull + uint64_t(t.tv_nsec);
}

static uint64_t walk(pugi::xml_node n, uint64_t h) {
  for (const char* p = n.name(); *p; ++p) h = (h ^ uint8_t(*p)) * 1099511628211ull;
  for (const char* p = n.value(); *p; ++p) h = (h ^ uint8_t(*p)) * 1099511628211ull;
  for (pugi::xml_attribute a : n.attributes())
    for (const char* p = a.value(); *p; ++p) h = (h ^ uint8_t(*p)) * 1099511628211ull;
  for (pugi::xml_node c : n.children()) h = walk(c, h);
  return h;
}

int main(int argc, char** argv) {
  if (argc < 3) return 2;
  size_t records = std::strtoull(argv[1], nullptr, 10);
  long iters = std::strtol(argv[2], nullptr, 10);
  std::string xml = "<root>";
  uint64_t x = 88172645463325252ull;
  for (size_t i = 0; i < records; ++i) {
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    xml += "<item id=\"" + std::to_string(i) + "\" v=\"" + std::to_string(x % 100000) + "\"><name>n" +
           std::to_string(x >> 40) + "</name></item>";
  }
  xml += "</root>";
  uint64_t h = 0;
  {
    pugi::xml_document d;
    if (!d.load_buffer(xml.data(), xml.size())) return 3;
    h = walk(d, 1469598103934665603ull);
  }
  uint64_t t0 = now_ns();
  for (long it = 0; it < iters; ++it) {
    pugi::xml_document d;
    d.load_buffer(xml.data(), xml.size());
    asm volatile("" ::: "memory");
  }
  uint64_t t1 = now_ns();
  std::printf("mode=%d iters=%ld ns=%.3f checksum=%016llx\n", int(DAYONE_MODE), iters,
              double(t1 - t0) / double(iters), (unsigned long long)h);
  return 0;
}
