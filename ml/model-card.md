# Model card — curl / idle / other classifier

Version 2026-11-21 (five participants; replaces the P01 + P02 model of 2026-11-19, which replaced the synthetic-data headers of 2026-11-03). Owner: Hanson He.

## What it is

Logistic regression on 31 hand features of a 2 s window (208 samples at 104 Hz, 1 s hop) of the six LSM6DSOX channels: mean, std, min, max per channel; mean and std of acceleration and gyro magnitude; zero-crossing count of each gyro axis. 3 classes. Weights: 31 × 3 + 3 = 96 parameters plus 62 scaler values. Exported by `ml/train/train.py` to `model_weights.h`, run on the Nano ESP32 by `firmware/classifier/classifier.h` (plain C++, no TFLite). The firmware's features match Python to 3.2e-7 relative error (host self-test, 2026-11-21).

## Training data

`data/sessions`, 40 files, 1892 windows, **5 participants** (P01–P05), all right-handed, one with regular strength training, recorded 2026-11-16 to 2026-11-20. P01 and P02 on **mount v1**, P03–P05 on **mount v2** (`ml/data-protocol.md` section 3). `partial` recordings are labelled `curl` (protocol section 3).

| Class | Windows | Source files |
|---|---|---|
| curl | 880 | curl slow / normal / fast and partial_mixed |
| idle | 435 | idle stand / table / lap |
| other | 577 | other_mixed (pick up / put down, carry, lateral and front raises, shaking) |

The five files in `data/sessions/excluded.csv` (four P03 files, one P04 file; reasons in the file) are **not trained on** but are tested on. The final model is fitted on the remaining 35 files plus 870 rotated idle windows: copies of the idle windows rotated ±90° about X, the handle axis, so that a dumbbell held upright while standing still reads as idle (`ml/README.md`). 1657 recorded windows + 870 rotated = 2527 training windows.

## Evaluation (leave-one-participant-out)

Scaler and model fitted on four participants, tested on **every file** of the fifth, windows pooled. Excluded files and rotated windows never enter the test side's training fold; the held-out participant is tested on unmodified recordings.

| Held out | Macro-F1 |
|---|---|
| P01 | 0.969 |
| P02 | 0.970 |
| P03 | 0.539 |
| P04 | 0.941 |
| P05 | 0.875 |
| **Pooled** | **0.872** (AT-01 target ≥ 0.85) |

Confusion matrix, rows = true, columns = predicted (curl, idle, other):

```
curl   669   31  180
idle     0  434    1
other   49    4  524
```

Where the 265 errors are:

- **182 are in the five excluded files.** The three P03 curl files and `P03_partial_mixed_02` are read as `other` in 168 of their 176 windows: those curls were about 45° with the rotation axis 33–49° off sensor X, unlike every other participant's curls. That is why P03 scores 0.539.
- **39 are `P05_other_mixed_01` read as `curl`** (39 of 119 windows), the largest error in a file that is trained on elsewhere.
- **28 are `partial_mixed` windows read as `idle`** (6 each for P01, P02 and P05, 10 in the excluded P04 file): the pauses between partial raises.
- The rest are 1–7 windows per file.

On the 35 files not in `excluded.csv` the pooled macro-F1 is 0.952. That figure removes hard recordings from the test side and is optimistic; quote 0.872.

## Limits — read before quoting the F1

- Five participants, all right-handed, is below the protocol's target of six with both hands and both training-experience groups. The exclusion list was decided after a first evaluation had been seen (`ml/README.md`), so even 0.872 is tuned on these five people, not an independent test. There is no held-out sixth participant.
- Two mount versions are mixed, and neither is the sensor inside the assembled enclosure. The orientation of the board in the enclosure relative to mount v2 has not been checked; acceleration features shift with it.
- Board check, 2026-11-21, same weights, board not mounted on a dumbbell: lying flat and still reads `idle`; held with the handle axis vertical it reads `curl`. That pose is not in the recordings and not covered by the rotation about X. Real curls on the board: **not tested**.
- Used for counting in `firmware/SmartDumbbell` (`COUNT_GATE 1`, 2026-11-21): a rep counts only if the 2 s ending at it are classified `curl`. Offline replay (`ml/tools/replay_count_gate.py`): reps during other movement 26 → 1, complete curls 218 → 217 of 223; half curls are not rejected because `partial` is trained as `curl`. Not run on the board. `firmware/app` still has its older gate (last label) behind `COUNT_GATE 0`.
- Inference time on the board: self-test PASS at boot, about 2.2 ms for features + inference (2026-11-21, a build of `firmware/SmartDumbbell` with these weights plus debug prints). Budget ≤ 50 ms.

## History

- 2026-11-19: P01 + P02 only, 764 windows, pooled 0.937 (`tests/results/2026-11-19_classifier-lopo-p01-p02.md`). Its main failure, `P01_idle_stand_01` read as curl when trained on P02 alone, is gone here (0 errors in that file) through more participants and the rotated idle windows.
- An ablation on the 2026-11-19 split, dropping the acceleration mean/min/max features, was not adopted and has not been re-run on five participants.

## Reproduce

```bash
.venv/bin/python ml/train/train.py --data data/sessions --out ml/results --model logreg
cp ml/results/model_weights.h ml/results/selftest.h firmware/classifier/
cp firmware/classifier/classifier.h firmware/classifier/model_weights.h firmware/classifier/selftest.h firmware/SmartDumbbell/
cp firmware/classifier/model_weights.h firmware/app/
clang++ -std=c++17 -O2 -I firmware/classifier -o /tmp/clf_test tests/host/classifier_selftest.cpp && /tmp/clf_test
```
