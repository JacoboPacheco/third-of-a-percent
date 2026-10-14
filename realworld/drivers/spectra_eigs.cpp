// Spectra 1.2.0 on Eigen 3.4.0 (realworld/PLAN.md): the 8 largest eigenvalues of a fixed-seed dense
// symmetric matrix (noise plus 8 planted directions, so the top of the spectrum is well separated) and of
// a sparse banded symmetric matrix with 8 planted diagonal values, with SymEigsSolver (ncv = 24).
// Usage: spectra_eigs <dense n> <sparse n> <iters>
#include <Eigen/Core>
#include <Eigen/SparseCore>
#include <Spectra/MatOp/DenseSymMatProd.h>
#include <Spectra/MatOp/SparseSymMatProd.h>
#include <Spectra/SymEigsSolver.h>

#include <vector>

#include "rw_common.h"

namespace {

Eigen::MatrixXd make_dense(int n, rw::Rng& rng) {
  Eigen::MatrixXd m(n, n);
  const double scale = 1.0 / std::sqrt(double(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j <= i; ++j) {
      const double v = rng.sym() * scale;
      m(i, j) = v;
      m(j, i) = v;
    }
  for (int k = 0; k < 8; ++k) {
    Eigen::VectorXd u(n);
    for (int i = 0; i < n; ++i) u(i) = rng.sym();
    u.normalize();
    m += (3.0 + k) * u * u.transpose();
  }
  return m;
}

Eigen::SparseMatrix<double> make_sparse(int n, rw::Rng& rng) {
  std::vector<Eigen::Triplet<double>> t;
  t.reserve(size_t(n) * 5);
  for (int i = 0; i < n; ++i) {
    t.emplace_back(i, i, 0.5 * rng.uni());
    for (int off : {1, 7}) {
      if (i + off < n) {
        const double v = 0.1 * rng.sym();
        t.emplace_back(i, i + off, v);
        t.emplace_back(i + off, i, v);
      }
    }
  }
  for (int k = 0; k < 8; ++k) t.emplace_back(k * (n / 8), k * (n / 8), 10.0 + k);
  Eigen::SparseMatrix<double> s(n, n);
  s.setFromTriplets(t.begin(), t.end());
  return s;
}

Eigen::VectorXd dense_top(const Eigen::MatrixXd& m) {
  Spectra::DenseSymMatProd<double> op(m);
  Spectra::SymEigsSolver<Spectra::DenseSymMatProd<double>> eigs(op, 8, 24);
  eigs.init();
  eigs.compute(Spectra::SortRule::LargestAlge, 1000, 1e-10);
  if (eigs.info() != Spectra::CompInfo::Successful) rw::fail("dense SymEigsSolver did not converge");
  return eigs.eigenvalues();
}

Eigen::VectorXd sparse_top(const Eigen::SparseMatrix<double>& s) {
  Spectra::SparseSymMatProd<double> op(s);
  Spectra::SymEigsSolver<Spectra::SparseSymMatProd<double>> eigs(op, 8, 24);
  eigs.init();
  eigs.compute(Spectra::SortRule::LargestAlge, 1000, 1e-10);
  if (eigs.info() != Spectra::CompInfo::Successful) rw::fail("sparse SymEigsSolver did not converge");
  return eigs.eigenvalues();
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 4) {
    std::fprintf(stderr, "usage: %s <dense n> <sparse n> <iters>\n", argv[0]);
    return 2;
  }
  const long iters = rw::iters_arg(argc, argv);
  const int nd = std::atoi(argv[1]), ns = std::atoi(argv[2]);
  if (nd < 32 || ns < 64) rw::fail("dense n >= 32 and sparse n >= 64");
  rw::Rng rng(20261012);
  const Eigen::MatrixXd dm = make_dense(nd, rng);
  const Eigen::SparseMatrix<double> sm = make_sparse(ns, rng);
  Eigen::VectorXd a = dense_top(dm), b = sparse_top(sm);  // warm-up, not timed
  const uint64_t t0 = rw::now_ns();
  for (long it = 0; it < iters; ++it) {
    a = dense_top(dm);
    b = sparse_top(sm);
    asm volatile("" ::: "memory");
  }
  const uint64_t t1 = rw::now_ns();
  rw::Hash exact, rounded;
  exact.bytes(a.data(), size_t(a.size()) * sizeof(double));
  exact.bytes(b.data(), size_t(b.size()) * sizeof(double));
  for (int i = 0; i < a.size(); ++i) rounded.round6(a(i));
  for (int i = 0; i < b.size(); ++i) rounded.round6(b(i));
  rw::report(t0, t1, iters, exact, rounded);
  return 0;
}
