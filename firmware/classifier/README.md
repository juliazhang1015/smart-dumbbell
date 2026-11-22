# classifier — on-device curl / idle / other model

Status 2026-11-21: `model_weights.h` and `selftest.h` come from the five-participant training run (P01–P05, leave-one-participant-out macro-F1 0.872; see `ml/model-card.md` for the limits). Host self-test passes (3.2e-7); compiles for `arduino:esp32:nano_nora` (Flash 10 %). Still **not run on the board** as a standalone sketch; the same code runs inside `firmware/SmartDumbbell`, where it labels every second and confirms each rep (`COUNT_GATE 1`). Copies of the three headers live in `firmware/SmartDumbbell/` and `firmware/app/` (weights only) — regenerate here and copy.

## What it does

- Reads the LSM6DSOX at 104 Hz (same settings as `firmware/bringup/04_imu_stream`), keeps the last 2 s (208 samples) in a ring buffer.
- Every 1 s computes 31 hand features (`classifier.h`, `clf_features`) and runs the exported dense model (`clf_infer`). Plain C++, no TensorFlow Lite.
- Prints one line per second in the format agreed in `ml/workplan.md` section 4:

  ```
  C,<t_ms>,<label>,<conf>,<inference_us>
  ```

  and, with `STREAM_RAW 1`, the raw CSV stream so `record_serial.py` still works.
- On boot runs a self-test: features and probabilities for one recorded window must match the Python values in `selftest.h` to 1e-3, and prints how many microseconds features + inference took.

## Files

| File | Who writes it |
|---|---|
| `classifier.ino`, `classifier.h` | by hand; `classifier.h` must stay equivalent to `ml/train/common.py` `features()` |
| `model_weights.h` | `ml/train/train.py` (scaler, layer sizes, weights) |
| `selftest.h` | `ml/train/train.py` (one raw window + expected features/probabilities) |

## Regenerate after training

```bash
python3 ml/train/train.py --data data/sessions --out ml/results --model logreg
cp ml/results/model_weights.h ml/results/selftest.h firmware/classifier/
arduino-cli compile --fqbn arduino:esp32:nano_nora firmware/classifier
```

Then upload and read the serial port; the first line after the banner must be `SELFTEST,PASS,...`. Record the `features+inference_us` figure in `ml/model-card.md` (workplan budget: ≤ 50 ms).

## Host-side check without a board

```bash
clang++ -std=c++17 -O2 -I firmware/classifier -o /tmp/clf_test tests/host/classifier_selftest.cpp && /tmp/clf_test
```

Run this whenever `classifier.h` or `common.py` changes. 2026-11-03 result: max feature relative error 6.6e-7, max probability error 3.1e-7.

## Why not TensorFlow Lite Micro

`Chirale_TensorFlowLite` hello_world does compile for this board, so the path exists. But a feature-based logistic regression or one-hidden-layer MLP is ~100 to ~1500 weights; writing the dense layers by hand removes the TFLite dependency, the converter step and the arena sizing, and keeps the firmware readable for the team. If a window-based CNN ever becomes necessary, switch back.
