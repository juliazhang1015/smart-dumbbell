# 2026-11-21 — classifier, leave-one-participant-out on P01–P05 (offline, software check)

Type: software evaluation on recorded data. Not a hardware measurement, not an AT-01 result (AT-01 needs participants excluded from training *and tuning*; the exclusion list was chosen after a first evaluation on these five participants, and the protocol's six-participant target is not met).

- Data: `data/sessions`, 40 files, 1892 windows, P01–P05, mount v1 (P01, P02) and v2 (P03–P05). Five files in `data/sessions/excluded.csv` are not trained on but are tested on.
- Model: logistic regression, 31 features, `ml/train/train.py` defaults (training folds also get idle windows rotated ±90° about X).
- Pooled macro-F1 0.872; held-out P01 0.969, P02 0.970, P03 0.539, P04 0.941, P05 0.875. On the 35 files not in `excluded.csv`: 0.952 (optimistic). Confusion matrix and error breakdown in the model card.
- Known failures: the excluded P03 curl and partial files read as `other` (168 of 176 windows); `P05_other_mixed_01` reads as `curl` in 39 of 119 windows.
- Host parity test of the C++ port against Python: max feature relative error 3.2e-7, max probability error 3.0e-7, PASS.
- Deployed to `firmware/classifier`, `firmware/app` (weights) and `firmware/SmartDumbbell` (label every second, and since the same day confirmation of each rep with `COUNT_GATE 1`; replay in `firmware/SmartDumbbell/README.md`). All three compile for `arduino:esp32:nano_nora`. On the board (2026-11-21, a build with the same weights plus debug prints, board not on a dumbbell): self-test PASS, about 2.2 ms; flat and still reads `idle`, handle axis vertical reads `curl`. Real curls on the board: **not tested**.

Commands: `ml/model-card.md`, "Reproduce".
