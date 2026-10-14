// meshoptimizer 1.3 (control: census 2 found no lost loop and no added checks in it; realworld/PLAN.md):
// a grid x grid mesh with shuffled triangles through the usual pipeline: vertex remap, vertex-cache,
// overdraw and vertex-fetch optimization, simplification to 25 % of the triangles, meshlets, and the
// index and vertex buffer codecs. The checksum covers every output buffer.
// Usage: meshopt_pipeline <grid> <iters>
#include <utility>
#include <vector>

#include "meshoptimizer.h"
#include "rw_common.h"

namespace {

struct Vertex {
  float px, py, pz, nx, ny, nz, u, v;
};

struct Input {
  std::vector<Vertex> verts;
  std::vector<unsigned int> idx;
};

Input make(int g) {
  Input in;
  rw::Rng rng(20261012);
  in.verts.resize(size_t(g) * g);
  for (int i = 0; i < g; ++i)
    for (int j = 0; j < g; ++j) {
      Vertex& v = in.verts[size_t(i) * g + j];
      v.px = float(i) / g;
      v.py = float(j) / g;
      v.pz = float(0.05 * rng.sym());
      v.nx = 0.f;
      v.ny = 0.f;
      v.nz = 1.f;
      v.u = float(i) / g;
      v.v = float(j) / g;
    }
  std::vector<unsigned int> tris;
  for (int i = 0; i + 1 < g; ++i)
    for (int j = 0; j + 1 < g; ++j) {
      const unsigned a = i * g + j, b = (i + 1) * g + j, c = i * g + j + 1, d = (i + 1) * g + j + 1;
      tris.insert(tris.end(), {a, b, d, a, d, c});
    }
  const size_t nt = tris.size() / 3;
  for (size_t t = nt - 1; t > 0; --t) {  // shuffle whole triangles (Fisher-Yates)
    const size_t s = size_t(rng.next() % (t + 1));
    for (int k = 0; k < 3; ++k) std::swap(tris[3 * t + k], tris[3 * s + k]);
  }
  in.idx = tris;
  return in;
}

struct Out {
  std::vector<unsigned int> opt, simp, mverts;
  std::vector<unsigned char> mtris, ib, vb;
  size_t meshlets = 0;
};

void pipeline(const Input& in, Out& o) {
  const size_t ni = in.idx.size(), nv = in.verts.size();
  std::vector<unsigned int> remap(nv);
  const size_t uv = meshopt_generateVertexRemap(remap.data(), in.idx.data(), ni, in.verts.data(), nv, sizeof(Vertex));
  std::vector<unsigned int> i0(ni), i1(ni);
  meshopt_remapIndexBuffer(i0.data(), in.idx.data(), ni, remap.data());
  std::vector<Vertex> v0(uv), v1(uv);
  meshopt_remapVertexBuffer(v0.data(), in.verts.data(), nv, sizeof(Vertex), remap.data());
  meshopt_optimizeVertexCache(i1.data(), i0.data(), ni, uv);
  meshopt_optimizeOverdraw(i0.data(), i1.data(), ni, &v0.data()->px, uv, sizeof(Vertex), 1.05f);
  meshopt_optimizeVertexFetch(v1.data(), i0.data(), ni, v0.data(), uv, sizeof(Vertex));
  o.opt = i0;
  o.simp.resize(ni);
  float err = 0.f;
  o.simp.resize(meshopt_simplify(o.simp.data(), i0.data(), ni, &v1.data()->px, uv, sizeof(Vertex), ni / 4, 1e-2f, 0,
                                 &err));
  const size_t mx = meshopt_buildMeshletsBound(ni, 64, 124);
  std::vector<meshopt_Meshlet> ml(mx);
  o.mverts.resize(mx * 64);
  o.mtris.resize(mx * 124 * 3);
  o.meshlets = meshopt_buildMeshlets(ml.data(), o.mverts.data(), o.mtris.data(), i0.data(), ni, &v1.data()->px, uv,
                                     sizeof(Vertex), 64, 124, 0.f);
  if (o.meshlets > 0) {
    const meshopt_Meshlet& last = ml[o.meshlets - 1];
    o.mverts.resize(last.vertex_offset + last.vertex_count);
    o.mtris.resize(last.triangle_offset + ((last.triangle_count * 3 + 3) & ~3u));
  }
  o.ib.resize(meshopt_encodeIndexBufferBound(ni, uv));
  o.ib.resize(meshopt_encodeIndexBuffer(o.ib.data(), o.ib.size(), i0.data(), ni));
  o.vb.resize(meshopt_encodeVertexBufferBound(uv, sizeof(Vertex)));
  o.vb.resize(meshopt_encodeVertexBuffer(o.vb.data(), o.vb.size(), v1.data(), uv, sizeof(Vertex)));
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 3) {
    std::fprintf(stderr, "usage: %s <grid> <iters>\n", argv[0]);
    return 2;
  }
  const long iters = rw::iters_arg(argc, argv);
  const int g = std::atoi(argv[1]);
  if (g < 8) rw::fail("grid must be at least 8");
  Input in = make(g);
  Out o;
  pipeline(in, o);  // warm-up, not timed
  const uint64_t t0 = rw::now_ns();
  for (long it = 0; it < iters; ++it) {
    pipeline(in, o);
    asm volatile("" ::: "memory");
  }
  const uint64_t t1 = rw::now_ns();
  rw::Hash h;
  h.bytes(o.opt.data(), o.opt.size() * sizeof(unsigned));
  h.bytes(o.simp.data(), o.simp.size() * sizeof(unsigned));
  h.bytes(o.mverts.data(), o.mverts.size() * sizeof(unsigned));
  h.bytes(o.mtris.data(), o.mtris.size());
  h.bytes(o.ib.data(), o.ib.size());
  h.bytes(o.vb.data(), o.vb.size());
  h.pod(uint64_t(o.meshlets));
  rw::report(t0, t1, iters, h, h);
  return 0;
}
