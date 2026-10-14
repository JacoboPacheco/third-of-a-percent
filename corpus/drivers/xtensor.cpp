// Census driver for xtensor (header-only, with xtl): element-wise arithmetic, views,
// broadcasting and reductions on xarray and xtensor, as in the README. Never linked or run.
#include <cmath>
#include <cstddef>
#include <vector>

#include <xtensor/containers/xadapt.hpp>
#include <xtensor/containers/xarray.hpp>
#include <xtensor/containers/xtensor.hpp>
#include <xtensor/core/xmath.hpp>
#include <xtensor/misc/xmanipulation.hpp>
#include <xtensor/views/xview.hpp>

xt::xarray<double> axpy(double a, const xt::xarray<double>& x, const xt::xarray<double>& y) { return a * x + y; }

xt::xtensor<double, 2> scale_rows(const xt::xtensor<double, 2>& m, const xt::xtensor<double, 1>& s) {
  return m * xt::view(s, xt::all(), xt::newaxis());
}

double total(const xt::xtensor<double, 2>& m) { return xt::sum(m)(); }

xt::xtensor<double, 1> column_means(const xt::xtensor<double, 2>& m) { return xt::mean(m, {0}); }

xt::xtensor<double, 2> transpose_copy(const xt::xtensor<double, 2>& m) { return xt::transpose(m); }

xt::xtensor<double, 1> every_other(const xt::xtensor<double, 1>& v) {
  return xt::view(v, xt::range(0, static_cast<std::ptrdiff_t>(v.size()), 2));
}

xt::xtensor<double, 1> reversed(const xt::xtensor<double, 1>& v) { return xt::flip(v, 0); }

double norm_of(const std::vector<double>& v) {
  auto a = xt::adapt(v, {v.size()});
  return std::sqrt(xt::sum(a * a)());
}

xt::xtensor<double, 2> clipped_exp(const xt::xtensor<double, 2>& m) { return xt::clip(xt::exp(m), 0.0, 10.0); }
