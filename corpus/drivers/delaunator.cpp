// Census driver for delaunator-cpp (header-only): triangulate points and walk the result, as in
// the README. Never linked or run.
#include <cstddef>
#include <vector>

#include <delaunator.hpp>

std::vector<std::size_t> triangulate(const std::vector<double>& coords) {
  delaunator::Delaunator d(coords);
  return d.triangles;
}

double perimeter_sum(const std::vector<double>& coords) {
  delaunator::Delaunator d(coords);
  double s = 0;
  for (std::size_t i = 0; i < d.triangles.size(); i += 3) {
    for (std::size_t k = 0; k < 3; ++k) {
      const std::size_t a = d.triangles[i + k], b = d.triangles[i + (k + 1) % 3];
      const double dx = coords[2 * a] - coords[2 * b], dy = coords[2 * a + 1] - coords[2 * b + 1];
      s += dx * dx + dy * dy;
    }
  }
  return s;
}

std::size_t hull_edges(const std::vector<double>& coords) {
  delaunator::Delaunator d(coords);
  std::size_t n = 0;
  for (std::size_t e = 0; e < d.halfedges.size(); ++e)
    if (d.halfedges[e] == delaunator::INVALID_INDEX) ++n;
  return n;
}
