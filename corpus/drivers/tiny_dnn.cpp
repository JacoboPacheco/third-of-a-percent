// Census driver for tiny-dnn (header-only): a small convolutional network built, trained for an
// epoch and used to predict, as in the README. Never linked or run.
#include <vector>

#include "tiny_dnn/tiny_dnn.h"

using namespace tiny_dnn;
using namespace tiny_dnn::activation;
using namespace tiny_dnn::layers;

network<sequential> make_net() {
  network<sequential> net;
  net << conv(32, 32, 5, 1, 6) << relu() << max_pool(28, 28, 6, 2) << fc(14 * 14 * 6, 120) << relu()
      << fc(120, 10) << softmax();
  return net;
}

void train_one_epoch(network<sequential>& net, const std::vector<vec_t>& x, const std::vector<label_t>& y) {
  adagrad opt;
  net.train<cross_entropy>(opt, x, y, 16, 1);
}

vec_t predict(network<sequential>& net, const vec_t& in) { return net.predict(in); }

float_t loss(network<sequential>& net, const std::vector<vec_t>& x, const std::vector<vec_t>& t) {
  return net.get_loss<mse>(x, t);
}
