// Census driver for hnswlib (header-only): build an HNSW index with L2 and inner-product spaces,
// add points and search, as in the README. Never linked or run.
#include <cstddef>
#include <vector>

#include "hnswlib/hnswlib.h"

std::size_t build_and_search_l2(const std::vector<float>& data, std::size_t dim, const float* q, std::size_t k) {
  hnswlib::L2Space space(dim);
  const std::size_t n = data.size() / dim;
  hnswlib::HierarchicalNSW<float> index(&space, n, 16, 200);
  for (std::size_t i = 0; i < n; ++i) index.addPoint(data.data() + i * dim, i);
  auto result = index.searchKnn(q, k);
  return result.size();
}

std::size_t build_and_search_ip(const std::vector<float>& data, std::size_t dim, const float* q, std::size_t k) {
  hnswlib::InnerProductSpace space(dim);
  const std::size_t n = data.size() / dim;
  hnswlib::HierarchicalNSW<float> index(&space, n, 16, 200);
  for (std::size_t i = 0; i < n; ++i) index.addPoint(data.data() + i * dim, i);
  index.setEf(64);
  return index.searchKnnCloserFirst(q, k).size();
}

std::size_t brute(const std::vector<float>& data, std::size_t dim, const float* q, std::size_t k) {
  hnswlib::L2Space space(dim);
  const std::size_t n = data.size() / dim;
  hnswlib::BruteforceSearch<float> index(&space, n);
  for (std::size_t i = 0; i < n; ++i) index.addPoint(data.data() + i * dim, i);
  return index.searchKnn(q, k).size();
}
