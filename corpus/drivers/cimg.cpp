// Census driver for CImg (header-only, no display): blur, convolve, resize, gradients,
// statistics and point operations on float images, as in the tutorial. Never linked or run.
#include "CImg.h"

using cimg_library::CImg;
using cimg_library::CImgList;

CImg<float> blurred(const CImg<float>& img, float sigma) { return img.get_blur(sigma); }

CImg<float> convolved(const CImg<float>& img, const CImg<float>& kernel) { return img.get_convolve(kernel); }

CImg<float> resized(const CImg<float>& img, int w, int h) { return img.get_resize(w, h, -100, -100, 3); }

CImg<float> gradient_norm(const CImg<float>& img) {
  CImgList<float> g = img.get_gradient("xy");
  return (g[0].get_sqr() + g[1].get_sqr()).sqrt();
}

float mean_value(const CImg<float>& img) { return static_cast<float>(img.mean()); }

CImg<float> normalized(const CImg<float>& img) { return img.get_normalize(0, 255); }

CImg<float> to_gray(const CImg<float>& rgb) { return rgb.get_RGBtoYCbCr().channel(0); }

CImg<float> mirrored(const CImg<float>& img) { return img.get_mirror('x'); }

CImg<float> eroded(const CImg<float>& img, int s) { return img.get_erode(s); }

CImg<float> thresholded(const CImg<float>& img, float t) { return img.get_threshold(t); }
