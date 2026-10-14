// tiny-dnn (header-only, CNN_SINGLE_THREAD; realworld/PLAN.md): train a 64-256-256-10 fully connected
// network for <epochs> epochs over <samples> fixed-seed samples (adagrad, batch 32, cross-entropy on
// softmax), then predict every sample. One iteration builds the network from the same seed, so every
// iteration does the same work. The checksum covers every predicted output.
// Usage: tinydnn_mlp <samples> <epochs> <iters>
#include <vector>

#include "rw_common.h"
#include "tiny_dnn/tiny_dnn.h"

namespace {

struct Data {
  std::vector<tiny_dnn::vec_t> x;
  std::vector<tiny_dnn::label_t> y;
};

Data make(int n) {
  Data d;
  rw::Rng rng(20261012);
  const int in = 64, k = 10;
  std::vector<double> w(size_t(in) * k);
  for (auto& v : w) v = rng.sym();
  for (int i = 0; i < n; ++i) {
    tiny_dnn::vec_t v(in);
    for (int j = 0; j < in; ++j) v[j] = tiny_dnn::float_t(rng.sym());
    int best = 0;
    double bs = -1e300;
    for (int c = 0; c < k; ++c) {
      double s = 0.3 * rng.sym();
      for (int j = 0; j < in; ++j) s += w[size_t(c) * in + j] * v[j];
      if (s > bs) { bs = s; best = c; }
    }
    d.x.push_back(v);
    d.y.push_back(tiny_dnn::label_t(best));
  }
  return d;
}

void train_predict(const Data& d, int epochs, std::vector<tiny_dnn::vec_t>& out) {
  using namespace tiny_dnn;
  set_random_seed(1);
  network<sequential> net;
  net << layers::fc(64, 256) << activation::relu() << layers::fc(256, 256) << activation::relu()
      << layers::fc(256, 10) << activation::softmax();
  adagrad opt;
  if (!net.train<cross_entropy>(opt, d.x, d.y, 32, epochs)) rw::fail("train");
  out.resize(d.x.size());
  for (size_t i = 0; i < d.x.size(); ++i) out[i] = net.predict(d.x[i]);
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 4) {
    std::fprintf(stderr, "usage: %s <samples> <epochs> <iters>\n", argv[0]);
    return 2;
  }
  const long iters = rw::iters_arg(argc, argv);
  const int n = std::atoi(argv[1]), epochs = std::atoi(argv[2]);
  if (n < 32 || epochs < 1) rw::fail("need at least 32 samples and 1 epoch");
  Data d = make(n);
  std::vector<tiny_dnn::vec_t> out;
  train_predict(d, epochs, out);  // warm-up, not timed
  const uint64_t t0 = rw::now_ns();
  for (long it = 0; it < iters; ++it) {
    train_predict(d, epochs, out);
    asm volatile("" ::: "memory");
  }
  const uint64_t t1 = rw::now_ns();
  rw::Hash exact, rounded;
  for (const auto& v : out) {
    exact.bytes(v.data(), v.size() * sizeof(v[0]));
    for (auto f : v) rounded.round6(double(f));
  }
  rw::report(t0, t1, iters, exact, rounded);
  return 0;
}
