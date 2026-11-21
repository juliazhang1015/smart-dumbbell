# Offline repetition counter regression

## Identification

- Date: 2026-11-20
- Related work: PR #18, offline evidence for FR-05 and FR-06
- Baseline: `c38a25dc` (PR #18 before the merge with `main`)
- Environment: Python 3.12.14, NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0
- Model and data: 25-feature Random Forest trained on seven P01 recordings, 323 windows. Replay covers all eight P01 recordings and the eight official P02 recordings.
- Test level: software

## Objective and predefined acceptance criterion

All eight P01 recordings must return the same V3 count and event times, and the same Random Forest accepted and rejected events, before and after the merge and fixes. All official recording CSVs and metadata must match `main`.

## Setup and procedure

In each revision, run `python ml/train/extract_features.py` and `python ml/train/train_classifier.py` from the repository root to regenerate the model. For each shared P01 CSV, compare the full return values of `count_cycles` and `count_ml_reps` across revisions. Replay official P02 CSVs with the model trained on P01. Check shared data with `git diff --exit-code origin/main -- data`.

## Observations and measurements

- All eight P01 results matched exactly. Slow, normal, and fast curls returned 13, 17, and 26 for both V3 and the filter. The filter rejected all seven V3 candidates in P01 Other Mixed.
- All eight official P02 files replayed successfully. Slow, normal, and fast curls gave V3 counts of 8, 9, and 23 and filtered counts of 8, 9, and 22. All three idle files and Other Mixed returned zero. Partial Mixed produced 17 V3 candidates, of which the filter accepted eight.
- Git reported no difference from `main` under `data/`. `python -m unittest discover -s tests` passed all 15 tests.

## Result and limitations

- Outcome: Pass for the regression criteria.
- P01 replay includes training data. P02 uses a single held-out participant, and some shared reference counts are inferred or observer-adjusted. The private two-rep spot check was unavailable for replay. Hardware acceptance tests remain open.
