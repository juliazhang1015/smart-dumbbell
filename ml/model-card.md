# Model card — curl / idle / other classifier

Version 2026-11-19 (first model trained on real recordings; replaces the synthetic-data headers of 2026-11-03). Owner: Hanson He.

## What it is

Logistic regression on 31 hand features of a 2 s window (208 samples at 104 Hz, 1 s hop) of the six LSM6DSOX channels: mean, std, min, max per channel; mean and std of acceleration and gyro magnitude; zero-crossing count of each gyro axis. 3 classes. Weights: 31 × 3 + 3 = 96 parameters plus 62 scaler values. Exported by `ml/train/train.py` to `model_weights.h`, run on the Nano ESP32 by `firmware/classifier/classifier.h` (plain C++, no TFLite). The firmware's features match Python to 3.2e-7 relative error (host self-test, 2026-11-19).

## Training data

`data/sessions`, 16 files, 764 windows, **2 participants** (P01, P02), both right-handed, no regular strength training, recorded 2026-11-16 and 2026-11-18 on **mount v1** (sensor taped to the bench dumbbell, `ml/data-protocol.md` section 3). `partial` recordings are labelled `curl` (protocol section 3, proposed mapping).

| Class | Windows | Source files |
|---|---|---|
| curl | 352 | curl slow / normal / fast and partial_mixed, both participants |
| idle | 174 | idle stand / table / lap, both participants |
| other | 238 | other_mixed (pick up / put down, carry, lateral and front raises, shaking), both participants |

## Evaluation (leave-one-participant-out)

Scaler and model fitted on one participant, tested on the other, windows pooled.

| Held out | Macro-F1 |
|---|---|
| P01 | 0.892 |
| P02 | 0.977 |
| **Pooled** | **0.937** (AT-01 target ≥ 0.85) |

Confusion matrix, rows = true, columns = predicted (curl, idle, other):

```
curl   339    8    5
idle    29  145    0
other    2    0  236
```

The 29 idle → curl errors are **all 29 windows of `P01_idle_stand_01`** when the model is trained on P02 only: with one training participant the model keys on the static posture (gravity direction in the acceleration mean/min/max features) rather than on motion. The remaining errors are 2–6 windows per file.

An ablation on the same split (not adopted): dropping the 12 acceleration mean/min/max features removes that failure (idle → curl 0, pooled F1 0.951, P01 0.947 / P02 0.955) but raises other → curl from 2 to 18 windows, mostly P01 lateral and front raises. Dropping all acceleration features costs more (F1 0.917–0.922, other → curl 46–47). Decision deferred until a third participant is recorded; the 31-feature model is deployed as is.

## Limits — read before quoting the F1

- Two participants is far below the protocol's target of six. The number above says the model separates these two people's movements; it does not say how it does on a new person, and the idle_stand failure shows posture is being learned.
- All data is mount v1. The assembled dumbbell is a different sensor placement (mount v2 once recorded); the acceleration features in particular will shift. Not validated on the assembled device.
- Runs on the board in **shadow mode** only (`firmware/SmartDumbbell`): the label is displayed, logged and sent, but the rep counter is not gated by it. `firmware/app` has the gate behind `COUNT_GATE 0`.
- Inference time on the board: not yet measured for this model (the 2026-11-06 `firmware/app` run measured 2.26 ms for the same feature and layer sizes). Budget ≤ 50 ms.
- The MLP variant (16 hidden units) scored 0.929 pooled on the same split; not used.

## Reproduce

```bash
.venv/bin/python ml/train/train.py --data data/sessions --out ml/results --model logreg
cp ml/results/model_weights.h ml/results/selftest.h firmware/classifier/
cp firmware/classifier/classifier.h firmware/classifier/model_weights.h firmware/classifier/selftest.h firmware/SmartDumbbell/
cp firmware/classifier/model_weights.h firmware/app/
clang++ -std=c++17 -O2 -I firmware/classifier -o /tmp/clf_test tests/host/classifier_selftest.cpp && /tmp/clf_test
```
