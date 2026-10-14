// LightGBM 4.7.0 through its C API (realworld/PLAN.md): build a Dataset from an in-memory matrix, train,
// predict the training rows. Single-threaded (built without OpenMP; num_threads=1 deterministic=true).
// Usage: lightgbm_train <binary|multiclass|linear> <rows> <features> <rounds> <iters>
// The matrix and labels come from a fixed seed, generated before timing. One iteration = Dataset
// construction + training + prediction, freed again. The checksum covers every prediction.
#include <LightGBM/c_api.h>

#include <cmath>
#include <cstring>
#include <string>
#include <vector>

#include "rw_common.h"

namespace {

struct Problem {
  int rows = 0, cols = 0, rounds = 0, num_class = 1;
  std::vector<double> x;  // row-major
  std::vector<float> y;
  std::string params;
};

void check(int rc, const char* what) {
  if (rc != 0) {
    std::fprintf(stderr, "%s failed: %s\n", what, LGBM_GetLastError());
    std::exit(3);
  }
}

const char* kCommon = "num_threads=1 deterministic=true verbosity=-1 seed=7";

Problem make(const std::string& kind, int rows, int cols, int rounds) {
  Problem p;
  p.rows = rows;
  p.cols = cols;
  p.rounds = rounds;
  p.x.resize(size_t(rows) * cols);
  p.y.resize(rows);
  rw::Rng rng(20261012);
  if (kind == "binary") {
    std::vector<double> w(cols);
    for (auto& v : w) v = rng.sym();
    for (int i = 0; i < rows; ++i) {
      double s = 0;
      for (int j = 0; j < cols; ++j) {
        double v = rng.uni();
        p.x[size_t(i) * cols + j] = v;
        s += w[j] * (v - 0.5);
      }
      s += 0.5 * std::sin(6.0 * p.x[size_t(i) * cols]) + 0.3 * rng.sym();
      p.y[i] = s > 0 ? 1.0f : 0.0f;
    }
    p.params = std::string("objective=binary force_col_wise=true ") + kCommon;
  } else if (kind == "multiclass") {
    const int K = 8, ncat = 4, levels = 20;
    if (cols <= ncat) rw::fail("multiclass needs more than 4 features");
    p.num_class = K;
    std::vector<double> w(size_t(K) * cols), c(size_t(K) * ncat * levels);
    for (auto& v : w) v = rng.sym();
    for (auto& v : c) v = 1.5 * rng.sym();
    for (int i = 0; i < rows; ++i) {
      double* xi = &p.x[size_t(i) * cols];
      for (int j = 0; j < ncat; ++j) xi[j] = double(rng.below(levels));
      for (int j = ncat; j < cols; ++j) xi[j] = rng.uni();
      int best = 0;
      double bs = -1e300;
      for (int k = 0; k < K; ++k) {
        double s = 0.4 * rng.sym();
        for (int j = ncat; j < cols; ++j) s += w[size_t(k) * cols + j] * (xi[j] - 0.5);
        for (int j = 0; j < ncat; ++j) s += c[(size_t(k) * ncat + j) * levels + int(xi[j])];
        if (s > bs) { bs = s; best = k; }
      }
      p.y[i] = float(best);
    }
    p.params = std::string("objective=multiclass num_class=8 bagging_fraction=0.8 bagging_freq=1 "
                           "force_row_wise=true categorical_feature=0,1,2,3 ") + kCommon;
  } else if (kind == "linear") {
    if (cols < 6) rw::fail("linear needs at least 6 features");
    for (int i = 0; i < rows; ++i) {
      double* xi = &p.x[size_t(i) * cols];
      for (int j = 0; j < cols; ++j) xi[j] = rng.uni();
      double s = 3.0 * xi[0] + (xi[1] > 0.5 ? 2.0 * xi[2] : -xi[3]) + xi[4] * xi[5] + 0.05 * rng.sym();
      p.y[i] = float(s);
    }
    p.params = std::string("objective=regression linear_tree=true force_col_wise=true ") + kCommon;
  } else {
    rw::fail("workload must be binary, multiclass or linear");
  }
  return p;
}

void train_predict(const Problem& p, std::vector<double>& pred) {
  DatasetHandle ds = nullptr;
  check(LGBM_DatasetCreateFromMat(p.x.data(), C_API_DTYPE_FLOAT64, p.rows, p.cols, 1, p.params.c_str(), nullptr, &ds),
        "LGBM_DatasetCreateFromMat");
  check(LGBM_DatasetSetField(ds, "label", p.y.data(), p.rows, C_API_DTYPE_FLOAT32), "LGBM_DatasetSetField");
  BoosterHandle b = nullptr;
  check(LGBM_BoosterCreate(ds, p.params.c_str(), &b), "LGBM_BoosterCreate");
  for (int r = 0; r < p.rounds; ++r) {
    int finished = 0;
    check(LGBM_BoosterUpdateOneIter(b, &finished), "LGBM_BoosterUpdateOneIter");
    if (finished) break;
  }
  pred.assign(size_t(p.rows) * p.num_class, 0.0);
  int64_t len = 0;
  check(LGBM_BoosterPredictForMat(b, p.x.data(), C_API_DTYPE_FLOAT64, p.rows, p.cols, 1, C_API_PREDICT_NORMAL, 0, -1,
                                  "num_threads=1", &len, pred.data()),
        "LGBM_BoosterPredictForMat");
  if (len != int64_t(pred.size())) rw::fail("unexpected prediction length");
  check(LGBM_BoosterFree(b), "LGBM_BoosterFree");
  check(LGBM_DatasetFree(ds), "LGBM_DatasetFree");
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 6) {
    std::fprintf(stderr, "usage: %s <binary|multiclass|linear> <rows> <features> <rounds> <iters>\n", argv[0]);
    return 2;
  }
  const long iters = rw::iters_arg(argc, argv);
  Problem p = make(argv[1], std::atoi(argv[2]), std::atoi(argv[3]), std::atoi(argv[4]));
  std::vector<double> pred;
  train_predict(p, pred);  // warm-up, not timed
  const uint64_t t0 = rw::now_ns();
  for (long it = 0; it < iters; ++it) {
    train_predict(p, pred);
    asm volatile("" ::: "memory");
  }
  const uint64_t t1 = rw::now_ns();
  rw::Hash exact, rounded;
  exact.bytes(pred.data(), pred.size() * sizeof(double));
  for (double v : pred) rounded.round6(v);
  rw::report(t0, t1, iters, exact, rounded);
  return 0;
}
