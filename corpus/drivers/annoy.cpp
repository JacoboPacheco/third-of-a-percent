// Census driver for Annoy (header-only): build angular and Euclidean indexes and query them, as
// in the README. Never linked or run.
#include <vector>

#include "annoylib.h"
#include "kissrandom.h"

using Angular = Annoy::AnnoyIndex<int, float, Annoy::Angular, Annoy::Kiss32Random,
                                  Annoy::AnnoyIndexSingleThreadedBuildPolicy>;
using Euclid = Annoy::AnnoyIndex<int, float, Annoy::Euclidean, Annoy::Kiss32Random,
                                 Annoy::AnnoyIndexSingleThreadedBuildPolicy>;

std::vector<int> angular_nns(const std::vector<std::vector<float>>& items, const std::vector<float>& q, int k) {
  Angular t(static_cast<int>(q.size()));
  for (int i = 0; i < static_cast<int>(items.size()); ++i) t.add_item(i, items[i].data());
  t.build(10);
  std::vector<int> out;
  std::vector<float> dist;
  t.get_nns_by_vector(q.data(), k, -1, &out, &dist);
  return out;
}

float euclid_distance_sum(const std::vector<std::vector<float>>& items, int k) {
  Euclid t(static_cast<int>(items.empty() ? 1 : items[0].size()));
  for (int i = 0; i < static_cast<int>(items.size()); ++i) t.add_item(i, items[i].data());
  t.build(10);
  float s = 0;
  for (int i = 0; i < static_cast<int>(items.size()); ++i) {
    std::vector<int> out;
    std::vector<float> dist;
    t.get_nns_by_item(i, k, -1, &out, &dist);
    for (float d : dist) s += d;
  }
  return s;
}
