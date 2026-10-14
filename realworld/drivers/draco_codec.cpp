// Draco 1.5.7 (realworld/PLAN.md): a torus mesh from an in-memory triangle soup (position, normal,
// texcoord per corner; the builder de-duplicates values, as Draco's own OBJ/PLY loaders do), encoded and
// decoded with draco_encoder's default options (quantization 11/10/8/8 bits, compression level 7 =
// speed 3), and the same vertices as a point cloud, encoded and decoded.
// Usage: draco_codec <grid> <iters>     (grid x grid vertices, 2 x grid x grid triangles)
#include <cmath>
#include <memory>
#include <vector>

#include "draco/compression/decode.h"
#include "draco/compression/encode.h"
#include "draco/core/decoder_buffer.h"
#include "draco/core/encoder_buffer.h"
#include "draco/mesh/triangle_soup_mesh_builder.h"
#include "draco/point_cloud/point_cloud_builder.h"
#include "rw_common.h"

namespace {

struct Soup {
  int nv = 0, nf = 0;
  std::vector<float> pos, nrm, uv;  // per vertex
  std::vector<int> tri;             // 3 per face
};

Soup make(int g) {
  Soup s;
  s.nv = g * g;
  s.nf = 2 * g * g;
  s.pos.resize(3 * size_t(s.nv));
  s.nrm.resize(3 * size_t(s.nv));
  s.uv.resize(2 * size_t(s.nv));
  rw::Rng rng(20261012);
  const double R = 1.0, r = 0.35, tau = 6.283185307179586;
  for (int i = 0; i < g; ++i)
    for (int j = 0; j < g; ++j) {
      const int v = i * g + j;
      const double u = tau * i / g, w = tau * j / g;
      const double rr = r * (1.0 + 0.02 * rng.sym());
      s.pos[3 * v + 0] = float((R + rr * std::cos(w)) * std::cos(u));
      s.pos[3 * v + 1] = float((R + rr * std::cos(w)) * std::sin(u));
      s.pos[3 * v + 2] = float(rr * std::sin(w));
      s.nrm[3 * v + 0] = float(std::cos(w) * std::cos(u));
      s.nrm[3 * v + 1] = float(std::cos(w) * std::sin(u));
      s.nrm[3 * v + 2] = float(std::sin(w));
      s.uv[2 * v + 0] = float(double(i) / g);
      s.uv[2 * v + 1] = float(double(j) / g);
    }
  s.tri.reserve(3 * size_t(s.nf));
  for (int i = 0; i < g; ++i)
    for (int j = 0; j < g; ++j) {
      const int a = i * g + j, b = ((i + 1) % g) * g + j, c = i * g + (j + 1) % g, d = ((i + 1) % g) * g + (j + 1) % g;
      s.tri.insert(s.tri.end(), {a, b, d, a, d, c});
    }
  return s;
}

struct Out {
  std::vector<char> mesh_bytes, pc_bytes;
  std::vector<float> mesh_pos, pc_pos;
  std::vector<uint32_t> faces;
};

void codec(const Soup& s, Out& o) {
  // mesh
  draco::TriangleSoupMeshBuilder mb;
  mb.Start(s.nf);
  const int pa = mb.AddAttribute(draco::GeometryAttribute::POSITION, 3, draco::DT_FLOAT32);
  const int na = mb.AddAttribute(draco::GeometryAttribute::NORMAL, 3, draco::DT_FLOAT32);
  const int ta = mb.AddAttribute(draco::GeometryAttribute::TEX_COORD, 2, draco::DT_FLOAT32);
  const float* P = s.pos.data();
  const float* N = s.nrm.data();
  const float* T = s.uv.data();
  const int* F = s.tri.data();
  for (int f = 0; f < s.nf; ++f) {
    const int a = F[3 * f], b = F[3 * f + 1], c = F[3 * f + 2];
    const draco::FaceIndex fi(f);
    mb.SetAttributeValuesForFace(pa, fi, P + 3 * a, P + 3 * b, P + 3 * c);
    mb.SetAttributeValuesForFace(na, fi, N + 3 * a, N + 3 * b, N + 3 * c);
    mb.SetAttributeValuesForFace(ta, fi, T + 2 * a, T + 2 * b, T + 2 * c);
  }
  std::unique_ptr<draco::Mesh> mesh = mb.Finalize();
  if (!mesh) rw::fail("TriangleSoupMeshBuilder::Finalize");

  draco::Encoder enc;
  enc.SetAttributeQuantization(draco::GeometryAttribute::POSITION, 11);
  enc.SetAttributeQuantization(draco::GeometryAttribute::TEX_COORD, 10);
  enc.SetAttributeQuantization(draco::GeometryAttribute::NORMAL, 8);
  enc.SetAttributeQuantization(draco::GeometryAttribute::GENERIC, 8);
  enc.SetSpeedOptions(3, 3);
  draco::EncoderBuffer eb;
  if (!enc.EncodeMeshToBuffer(*mesh, &eb).ok()) rw::fail("EncodeMeshToBuffer");
  o.mesh_bytes.assign(eb.data(), eb.data() + eb.size());

  draco::DecoderBuffer db;
  db.Init(eb.data(), eb.size());
  draco::Decoder dec;
  auto dm = dec.DecodeMeshFromBuffer(&db);
  if (!dm.ok()) rw::fail("DecodeMeshFromBuffer");
  std::unique_ptr<draco::Mesh> m2 = std::move(dm).value();
  const draco::PointAttribute* mp = m2->GetNamedAttribute(draco::GeometryAttribute::POSITION);
  if (!mp) rw::fail("decoded mesh has no positions");
  o.mesh_pos.resize(3 * size_t(m2->num_points()));
  for (uint32_t i = 0; i < m2->num_points(); ++i) mp->GetMappedValue(draco::PointIndex(i), &o.mesh_pos[3 * size_t(i)]);
  o.faces.resize(3 * size_t(m2->num_faces()));
  for (uint32_t f = 0; f < m2->num_faces(); ++f) {
    const auto& face = m2->face(draco::FaceIndex(f));
    for (int k = 0; k < 3; ++k) o.faces[3 * size_t(f) + k] = face[k].value();
  }

  // point cloud of the same vertices
  draco::PointCloudBuilder pb;
  pb.Start(s.nv);
  const int pp = pb.AddAttribute(draco::GeometryAttribute::POSITION, 3, draco::DT_FLOAT32);
  const int pn = pb.AddAttribute(draco::GeometryAttribute::NORMAL, 3, draco::DT_FLOAT32);
  pb.SetAttributeValuesForAllPoints(pp, P, 0);
  pb.SetAttributeValuesForAllPoints(pn, N, 0);
  std::unique_ptr<draco::PointCloud> pc = pb.Finalize(false);
  if (!pc) rw::fail("PointCloudBuilder::Finalize");
  draco::EncoderBuffer pe;
  if (!enc.EncodePointCloudToBuffer(*pc, &pe).ok()) rw::fail("EncodePointCloudToBuffer");
  o.pc_bytes.assign(pe.data(), pe.data() + pe.size());
  draco::DecoderBuffer pd;
  pd.Init(pe.data(), pe.size());
  draco::Decoder dec2;
  auto dp = dec2.DecodePointCloudFromBuffer(&pd);
  if (!dp.ok()) rw::fail("DecodePointCloudFromBuffer");
  std::unique_ptr<draco::PointCloud> pc2 = std::move(dp).value();
  const draco::PointAttribute* q = pc2->GetNamedAttribute(draco::GeometryAttribute::POSITION);
  if (!q) rw::fail("decoded point cloud has no positions");
  o.pc_pos.resize(3 * size_t(pc2->num_points()));
  for (uint32_t i = 0; i < pc2->num_points(); ++i) q->GetMappedValue(draco::PointIndex(i), &o.pc_pos[3 * size_t(i)]);
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 3) {
    std::fprintf(stderr, "usage: %s <grid> <iters>\n", argv[0]);
    return 2;
  }
  const long iters = rw::iters_arg(argc, argv);
  const int g = std::atoi(argv[1]);
  if (g < 4) rw::fail("grid must be at least 4");
  Soup s = make(g);
  Out o;
  codec(s, o);  // warm-up, not timed
  const uint64_t t0 = rw::now_ns();
  for (long it = 0; it < iters; ++it) {
    codec(s, o);
    asm volatile("" ::: "memory");
  }
  const uint64_t t1 = rw::now_ns();
  rw::Hash exact, rounded;
  auto shared = [&](rw::Hash& h) {
    h.bytes(o.mesh_bytes.data(), o.mesh_bytes.size());
    h.bytes(o.pc_bytes.data(), o.pc_bytes.size());
    h.bytes(o.faces.data(), o.faces.size() * sizeof(uint32_t));
  };
  shared(exact);
  shared(rounded);
  exact.bytes(o.mesh_pos.data(), o.mesh_pos.size() * sizeof(float));
  exact.bytes(o.pc_pos.data(), o.pc_pos.size() * sizeof(float));
  for (float v : o.mesh_pos) rounded.round6(v);
  for (float v : o.pc_pos) rounded.round6(v);
  rw::report(t0, t1, iters, exact, rounded);
  return 0;
}
