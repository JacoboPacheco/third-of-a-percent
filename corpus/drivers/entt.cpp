// Census driver for EnTT (header-only): create entities, attach components, iterate views and
// groups, sort a pool, destroy. The operations of the README. Never linked or run.
#include <cstdint>
#include <vector>

#include <entt/entt.hpp>

struct position { float x, y, z; };
struct velocity { float dx, dy, dz; };
struct health { int hp; };

void spawn(entt::registry& r, int n) {
  for (int i = 0; i < n; ++i) {
    const auto e = r.create();
    r.emplace<position>(e, float(i), float(i), 0.f);
    if (i % 2 == 0) r.emplace<velocity>(e, 1.f, 0.5f, 0.f);
    if (i % 3 == 0) r.emplace<health>(e, 100);
  }
}

void integrate(entt::registry& r, float dt) {
  r.view<position, const velocity>().each([dt](position& p, const velocity& v) {
    p.x += v.dx * dt;
    p.y += v.dy * dt;
    p.z += v.dz * dt;
  });
}

float sum_x(const entt::registry& r) {
  float s = 0.f;
  for (auto [e, p] : r.view<const position>().each()) s += p.x;
  return s;
}

void grouped(entt::registry& r, float dt) {
  auto g = r.group<position>(entt::get<velocity>);
  for (auto e : g) {
    auto [p, v] = g.get<position, velocity>(e);
    p.x += v.dx * dt;
  }
}

void sort_by_x(entt::registry& r) {
  r.sort<position>([](const position& a, const position& b) { return a.x < b.x; });
}

void damage(entt::registry& r, int amount) {
  for (auto e : r.view<health>()) {
    auto& h = r.get<health>(e);
    h.hp -= amount;
    if (h.hp <= 0) r.destroy(e);
  }
}

std::vector<entt::entity> collect(const entt::registry& r) {
  std::vector<entt::entity> out;
  for (auto e : r.view<const position, const health>()) out.push_back(e);
  return out;
}

void clear_all(entt::registry& r) { r.clear(); }
