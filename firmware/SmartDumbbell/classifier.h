// Feature extraction and inference for the curl / idle / other classifier.
// Must stay numerically equivalent to ml/train/common.py features() and the
// scaler + dense layers written by ml/train/export_c.py. Plain C++, no TFLite.
#pragma once
#include <math.h>
#include "model_weights.h"

struct ClfResult {
  int label;                      // index into CLF_CLASSES
  float conf;                     // probability of that label
  float probs[CLF_N_CLASSES];
};

// window: CLF_WINDOW rows of {ax, ay, az, gx, gy, gz}, same units as the CSV.
static void clf_features(const float (*window)[6], float* out) {
  int k = 0;
  for (int c = 0; c < 6; c++) {
    double sum = 0, sq = 0;
    float mn = window[0][c], mx = window[0][c];
    for (int i = 0; i < CLF_WINDOW; i++) {
      float v = window[i][c];
      sum += v; sq += (double)v * v;
      if (v < mn) mn = v;
      if (v > mx) mx = v;
    }
    double mean = sum / CLF_WINDOW;
    double var = sq / CLF_WINDOW - mean * mean;
    out[k++] = (float)mean;
    out[k++] = (float)sqrt(var > 0 ? var : 0);     // population std, numpy default
    out[k++] = mn;
    out[k++] = mx;
  }
  for (int part = 0; part < 2; part++) {          // acc magnitude then gyro magnitude
    int c0 = part * 3;
    double sum = 0, sq = 0;
    for (int i = 0; i < CLF_WINDOW; i++) {
      float m = sqrtf(window[i][c0] * window[i][c0] + window[i][c0 + 1] * window[i][c0 + 1] +
                      window[i][c0 + 2] * window[i][c0 + 2]);
      sum += m; sq += (double)m * m;
    }
    double mean = sum / CLF_WINDOW, var = sq / CLF_WINDOW - mean * mean;
    out[k++] = (float)mean;
    out[k++] = (float)sqrt(var > 0 ? var : 0);
  }
  for (int c = 3; c < 6; c++) {                    // zero crossings of mean-removed gyro
    float mean = out[c * 4];
    int zc = 0;
    for (int i = 1; i < CLF_WINDOW; i++) {
      bool a = (window[i][c] - mean) < 0, b = (window[i - 1][c] - mean) < 0;
      if (a != b) zc++;
    }
    out[k++] = (float)zc;
  }
}

static ClfResult clf_infer(const float* feats) {
  float buf_a[64], buf_b[64];                      // largest layer must be <= 64
  float* x = buf_a; float* y = buf_b;
  for (int i = 0; i < CLF_N_FEATURES; i++) x[i] = (feats[i] - CLF_SCALER_MEAN[i]) / CLF_SCALER_SCALE[i];
  for (int l = 0; l < CLF_N_LAYERS; l++) {
    int n_in = CLF_LAYER_SIZES[l], n_out = CLF_LAYER_SIZES[l + 1];
    for (int j = 0; j < n_out; j++) {
      float acc = CLF_B[l][j];
      for (int i = 0; i < n_in; i++) acc += x[i] * CLF_W[l][i * n_out + j];
      y[j] = (l == CLF_N_LAYERS - 1) ? acc : (acc > 0 ? acc : 0);   // relu except last
    }
    float* t = x; x = y; y = t;
  }
  ClfResult r; float mx = x[0];
  for (int j = 1; j < CLF_N_CLASSES; j++) if (x[j] > mx) mx = x[j];
  float sum = 0;
  for (int j = 0; j < CLF_N_CLASSES; j++) { r.probs[j] = expf(x[j] - mx); sum += r.probs[j]; }
  r.label = 0; r.conf = 0;
  for (int j = 0; j < CLF_N_CLASSES; j++) { r.probs[j] /= sum; if (r.probs[j] > r.conf) { r.conf = r.probs[j]; r.label = j; } }
  return r;
}
