// Census driver for nanoflann (header-only): build a 3-D k-d tree over a point cloud and run
// k-nearest and radius searches, as in examples/pointcloud_example.cpp. Never linked or run.
#include <cstddef>
#include <cstdint>
#include <vector>

#include <nanoflann.hpp>

struct Cloud {
  struct Point { double x, y, z; };
  std::vector<Point> pts;
  std::size_t kdtree_get_point_count() const { return pts.size(); }
  double kdtree_get_pt(std::size_t i, std::size_t dim) const {
    return dim == 0 ? pts[i].x : dim == 1 ? pts[i].y : pts[i].z;
  }
  template <class BBOX>
  bool kdtree_get_bbox(BBOX&) const { return false; }
};

using Tree = nanoflann::KDTreeSingleIndexAdaptor<nanoflann::L2_Simple_Adaptor<double, Cloud>, Cloud, 3>;

std::size_t knn(const Cloud& cloud, const double* q, std::size_t k, std::vector<uint32_t>& idx,
                std::vector<double>& dist) {
  Tree index(3, cloud, nanoflann::KDTreeSingleIndexAdaptorParams(10));
  idx.resize(k);
  dist.resize(k);
  return index.knnSearch(q, k, idx.data(), dist.data());
}

std::size_t radius(const Cloud& cloud, const double* q, double r2) {
  Tree index(3, cloud, nanoflann::KDTreeSingleIndexAdaptorParams(10));
  std::vector<nanoflann::ResultItem<unsigned int, double>> matches;
  return index.radiusSearch(q, r2, matches);
}

std::size_t nearest_each(const Cloud& cloud, const Cloud& queries, std::vector<std::size_t>& out) {
  Tree index(3, cloud, nanoflann::KDTreeSingleIndexAdaptorParams(16));
  out.resize(queries.pts.size());
  std::size_t found = 0;
  for (std::size_t i = 0; i < queries.pts.size(); ++i) {
    const double q[3] = {queries.pts[i].x, queries.pts[i].y, queries.pts[i].z};
    std::size_t id;
    double d;
    nanoflann::KNNResultSet<double> rs(1);
    rs.init(&id, &d);
    if (index.findNeighbors(rs, q)) ++found;
    out[i] = id;
  }
  return found;
}
