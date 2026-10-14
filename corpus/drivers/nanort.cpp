// Census driver for nanort (header-only): build a BVH over a triangle mesh and trace rays, as in
// the README. Never linked or run.
#include <vector>

#include "nanort.h"

bool build(const std::vector<float>& vertices, const std::vector<unsigned int>& faces,
           nanort::BVHAccel<float>& accel) {
  const unsigned int n = static_cast<unsigned int>(faces.size() / 3);
  nanort::TriangleMesh<float> mesh(vertices.data(), faces.data(), sizeof(float) * 3);
  nanort::TriangleSAHPred<float> pred(vertices.data(), faces.data(), sizeof(float) * 3);
  nanort::BVHBuildOptions<float> options;
  return accel.Build(n, mesh, pred, options);
}

int trace_grid(const nanort::BVHAccel<float>& accel, const std::vector<float>& vertices,
               const std::vector<unsigned int>& faces, int w, int h, std::vector<float>& depth) {
  nanort::TriangleIntersector<> isector(vertices.data(), faces.data(), sizeof(float) * 3);
  depth.assign(static_cast<size_t>(w) * h, 0.f);
  int hits = 0;
  for (int y = 0; y < h; ++y) {
    for (int x = 0; x < w; ++x) {
      nanort::Ray<float> ray;
      ray.org[0] = (x + 0.5f) / w - 0.5f;
      ray.org[1] = (y + 0.5f) / h - 0.5f;
      ray.org[2] = 2.f;
      ray.dir[0] = 0.f;
      ray.dir[1] = 0.f;
      ray.dir[2] = -1.f;
      ray.min_t = 0.f;
      ray.max_t = 1.0e30f;
      nanort::TriangleIntersection<> isect;
      if (accel.Traverse(ray, isector, &isect)) {
        depth[static_cast<size_t>(y) * w + x] = isect.t;
        ++hits;
      }
    }
  }
  return hits;
}
