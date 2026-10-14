// Census driver for earcut.hpp (header-only): triangulate a polygon with holes, as in the
// README, for double and int coordinates. Never linked or run.
#include <array>
#include <cstdint>
#include <vector>

#include <mapbox/earcut.hpp>

using PointD = std::array<double, 2>;
using PointI = std::array<int32_t, 2>;

std::vector<uint32_t> triangulate(const std::vector<std::vector<PointD>>& polygon) {
  return mapbox::earcut<uint32_t>(polygon);
}

std::vector<uint32_t> triangulate_int(const std::vector<std::vector<PointI>>& polygon) {
  return mapbox::earcut<uint32_t>(polygon);
}

double area(const std::vector<std::vector<PointD>>& polygon) {
  const auto idx = mapbox::earcut<uint32_t>(polygon);
  std::vector<PointD> flat;
  for (const auto& ring : polygon) flat.insert(flat.end(), ring.begin(), ring.end());
  double a = 0;
  for (size_t i = 0; i + 2 < idx.size(); i += 3) {
    const auto& p = flat[idx[i]];
    const auto& q = flat[idx[i + 1]];
    const auto& r = flat[idx[i + 2]];
    a += (q[0] - p[0]) * (r[1] - p[1]) - (r[0] - p[0]) * (q[1] - p[1]);
  }
  return a / 2;
}
