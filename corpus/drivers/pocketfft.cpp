// Census driver for pocketfft (C++ header-only): complex and real FFTs in one and two
// dimensions, as in pocketfft_demo.cc. Never linked or run.
#include <complex>
#include <cstddef>
#include <vector>

#include "pocketfft_hdronly.h"

using pocketfft::shape_t;
using pocketfft::stride_t;

void c2c_1d(std::vector<std::complex<double>>& data, bool forward) {
  shape_t shape{data.size()};
  stride_t stride{sizeof(std::complex<double>)};
  pocketfft::c2c(shape, stride, stride, shape_t{0}, forward, data.data(), data.data(), 1.0);
}

std::vector<std::complex<float>> r2c_1d(const std::vector<float>& in) {
  std::vector<std::complex<float>> out(in.size() / 2 + 1);
  pocketfft::r2c(shape_t{in.size()}, stride_t{sizeof(float)}, stride_t{sizeof(std::complex<float>)}, 0,
                 pocketfft::FORWARD, in.data(), out.data(), 1.0f);
  return out;
}

void c2c_2d(std::vector<std::complex<double>>& data, std::size_t rows, std::size_t cols) {
  shape_t shape{rows, cols};
  stride_t stride{static_cast<std::ptrdiff_t>(cols * sizeof(std::complex<double>)),
                  static_cast<std::ptrdiff_t>(sizeof(std::complex<double>))};
  pocketfft::c2c(shape, stride, stride, shape_t{0, 1}, pocketfft::FORWARD, data.data(), data.data(), 1.0);
}

std::vector<double> c2r_1d(const std::vector<std::complex<double>>& in, std::size_t n) {
  std::vector<double> out(n);
  pocketfft::c2r(shape_t{n}, stride_t{sizeof(std::complex<double>)}, stride_t{sizeof(double)}, 0,
                 pocketfft::BACKWARD, in.data(), out.data(), 1.0 / double(n));
  return out;
}
