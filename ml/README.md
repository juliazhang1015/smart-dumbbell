# Motion model

Work split, interface contract, recording plan and timeline: `workplan.md` (agreed 2026-11-03). Recording protocol: `data-protocol.md`. Owner of this folder: Hanson He (classification line).

Status 2026-11-03: no real recordings yet. The training pipeline below runs end to end on synthetic data and its C++ port compiles for the Nano ESP32; every performance number so far is from synthetic data and means nothing about real motion.

## Pipeline (`train/`)

```bash
python3 -m venv .venv && .venv/bin/pip install -r ml/train/requirements.txt
.venv/bin/python ml/train/check_recording.py data/sessions/P01_curl_slow_01.csv 40   # after each recording
.venv/bin/python ml/train/train.py --data data/sessions --out ml/results --model logreg
```

| File | Purpose |
|---|---|
| `common.py` | Constants (104 Hz, 2 s window, 1 s hop), file-name parsing, CSV loading, windowing, the 31 hand features. The firmware reproduces exactly this. |
| `check_recording.py` | Pass/fail check for one recording: rate, gaps, duration, dominant gyro axis. |
| `train.py` | Leave-one-participant-out evaluation (macro-F1, confusion matrix), refit on all data, export. |
| `export_c.py` | Writes `model_weights.h` and `selftest.h` for `firmware/classifier/`. |
| `make_synthetic.py` | Synthetic sessions for exercising the pipeline. Never mix with `data/sessions/`. |

Features per window: mean, std, min, max of each of the six channels; mean and std of acceleration and gyro magnitude; zero-crossing count of each gyro axis. Models: logistic regression (default) or a 16-unit MLP. Both export to the same header format.

Files listed in `data/sessions/excluded.csv`, with the reason for each, are left out of **training only**. The evaluation still tests on every file of the held-out participant, so the list cannot raise the reported score by hiding hard recordings; the score on the remaining files is printed as a secondary, optimistic figure. `--include-excluded` also trains on every file. The recordings themselves stay in `data/sessions/` and in `sessions.csv`.

The five files were flagged in `sessions.csv` for recording quality when they were recorded, but the decision to stop training on them was taken on 2026-11-20 after a first evaluation had been seen. Treat the gain from the list as tuned on these five participants, not as independent evidence.

`train.py` also adds training copies of the idle windows rotated by ±90° about X, the handle axis, so that a dumbbell held upright while standing still reads as idle (P01 held it upright, everyone else level). Held-out participants are evaluated on unmodified recordings. `--no-augment` switches it off. It changes only the training set: the 31 features and the firmware are unchanged.

Evaluation rule: split by participant before windowing; fit the scaler on training folds only; report the pooled confusion matrix and macro-F1 against AT-01 (≥ 0.85). Classification and repetition counting are separate tasks; the counter lives in `firmware/counter/` (Julia Zhang).

Do not commit identifiable recordings. See `../data/README.md` and `../data/sessions/README.md`.
