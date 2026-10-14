// Census driver for Spectra (header-only, on Eigen 3.4.0): largest eigenvalues of a dense
// symmetric and of a sparse symmetric matrix, as in the README. Never linked or run.
#include <Eigen/Core>
#include <Eigen/SparseCore>
#include <Spectra/MatOp/DenseSymMatProd.h>
#include <Spectra/MatOp/SparseSymMatProd.h>
#include <Spectra/SymEigsSolver.h>

Eigen::VectorXd dense_top(const Eigen::MatrixXd& m, int nev) {
  Spectra::DenseSymMatProd<double> op(m);
  Spectra::SymEigsSolver<Spectra::DenseSymMatProd<double>> eigs(op, nev, 2 * nev + 1);
  eigs.init();
  eigs.compute(Spectra::SortRule::LargestAlge);
  return eigs.info() == Spectra::CompInfo::Successful ? eigs.eigenvalues() : Eigen::VectorXd();
}

Eigen::VectorXd sparse_top(const Eigen::SparseMatrix<double>& m, int nev) {
  Spectra::SparseSymMatProd<double> op(m);
  Spectra::SymEigsSolver<Spectra::SparseSymMatProd<double>> eigs(op, nev, 2 * nev + 1);
  eigs.init();
  eigs.compute(Spectra::SortRule::LargestMagn);
  return eigs.info() == Spectra::CompInfo::Successful ? eigs.eigenvalues() : Eigen::VectorXd();
}
