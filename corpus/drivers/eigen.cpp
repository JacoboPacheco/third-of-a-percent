// Census driver for Eigen (header-only): common dense operations on dynamic-size matrices and
// vectors, plus a copy into a std::vector. Never linked or run.
#include <vector>

#include <Eigen/Dense>

using Eigen::MatrixXd;
using Eigen::VectorXd;

MatrixXd mul(const MatrixXd& a, const MatrixXd& b) { return a * b; }
VectorXd matvec(const MatrixXd& a, const VectorXd& x) { return a * x; }
VectorXd solve_lu(const MatrixXd& a, const VectorXd& b) { return a.partialPivLu().solve(b); }
VectorXd solve_qr(const MatrixXd& a, const VectorXd& b) { return a.householderQr().solve(b); }
double dot(const VectorXd& a, const VectorXd& b) { return a.dot(b); }
VectorXd axpy(double s, const VectorXd& x, const VectorXd& y) { return s * x + y; }
MatrixXd symmetrize(const MatrixXd& a) { return a + a.transpose(); }
double norm(const VectorXd& v) { return v.norm(); }
VectorXd reversed(const VectorXd& v) { return v.reverse(); }
std::vector<double> to_std(const VectorXd& v) { return std::vector<double>(v.data(), v.data() + v.size()); }
VectorXd from_std(const std::vector<double>& v) { return Eigen::Map<const VectorXd>(v.data(), Eigen::Index(v.size())); }
