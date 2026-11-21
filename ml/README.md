# Motion model

Work split, interface contract, recording plan and timeline: `workplan.md` (agreed 2026-11-03). Recording protocol: `data-protocol.md`. Owner of this folder: Hanson He (classification line).

Status 2026-11-19: first model trained on real recordings (P01 + P02, 764 windows), leave-one-participant-out macro-F1 0.937, deployed to the firmware; see `model-card.md`, including why two participants and one mount version make that number provisional. Recording more participants on the assembled dumbbell is the open work.

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

Evaluation rule: split by participant before windowing; fit the scaler on training folds only; report the pooled confusion matrix and macro-F1 against AT-01 (≥ 0.85). Classification and repetition counting are separate tasks; the counter lives in `firmware/counter/` (Julia Zhang).

Do not commit identifiable recordings. See `../data/README.md` and `../data/sessions/README.md`.

## Experimental offline repetition counter (Julia Zhang)

This Python experiment combines the V3 repetition counter with a 25-feature
Random Forest for offline activity filtering. Hanson He owns the formal
31-feature classification pipeline above, including the LogReg model,
C++ export and firmware inference. [PR #16](https://github.com/juliazhang1015/smart-dumbbell/pull/16)
tracks Hanson's initial P01/P02 evaluation and firmware shadow-mode work.

From the repository root, using the virtual environment created above:

```bash
.venv/bin/python ml/train/extract_features.py
.venv/bin/python ml/train/train_classifier.py
.venv/bin/python ml/tools/test_cycle_counter.py
.venv/bin/python ml/tools/ml_rep_counter.py
```

This trains on the listed P01 recordings and replays the P01 corpus.
Feature CSVs and the Random Forest model bundle are generated locally.

### Architecture

1. Record six-axis IMU data (ax, ay, az, gx, gy, gz).
2. Detect candidate curl repetitions using gyroscope-based cycle detection.
3. Extract 25 statistical features from a two-second window before each candidate.
4. Use a Random Forest classifier to distinguish curl, idle, and other activity.
5. Accept a candidate repetition only when classified as curl.

### Implementation

| File | Purpose |
|---|---|
| `tools/offline_counter.py` | Initial rule-based repetition counter |
| `tools/test_angle_counter.py` | Gyroscope angle-integration experiment |
| `tools/test_cycle_counter.py` | V3 raise/lower cycle detection |
| `tools/ml_rep_counter.py` | V3 counter combined with ML filtering |
| `train/extract_features.py` | Extract 25 IMU features |
| `train/train_classifier.py` | Train the Random Forest classifier |

The Random Forest uses 200 trees, maximum depth 8,
and balanced class weights.

### Preliminary results

| Recording | Observer/reference reps | V3 count | ML count |
|---|---:|---:|---:|
| P01 slow curl | 13 | 13 | 13 |
| P01 normal curl | 17 | 17 | 17 |
| P01 fast curl | 26 | 26 | 26 |

For the P01 Other Mixed recording, V3 produced seven
false-positive candidates, all rejected by ML filtering.

A separate local spot check with two completed curls followed by idle
returned two repetitions with both V3 and Random Forest filtering. That
CSV is unavailable for repository replay. The shared
[sessions.csv](../data/sessions/sessions.csv) lists the official P02
recordings. Store experimental captures outside `data/sessions/` so
the formal classifier's file scan uses the shared recordings.

### Evaluation limitations

- The Random Forest was trained on P01 recordings.
- P01 training-set results are not independent validation.
- The local P02 two-rep take is a preliminary participant-independent
  spot check only; its raw data is not published with this PR.
- The P01 curl reference counts are `observer_adjusted`, not strict
  observer-only ground truth under protocol v0.3.
- More participants and independently labeled recordings
  are needed to measure generalization.
- The Random Forest pipeline currently runs offline in
  Python and has not been deployed to the Nano ESP32.

### Next steps

- Collect additional slow, normal, and fast curl recordings.
- Collect more idle, partial-motion, and non-curl activities.
- Evaluate classification using participant-independent splits.
- Evaluate repetition count error against observer labels.
- Investigate real-time integration after offline validation.
