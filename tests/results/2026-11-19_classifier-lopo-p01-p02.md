# 2026-11-19 — classifier, leave-one-participant-out on P01 + P02 (offline, software check)

Type: software evaluation on recorded data. Not a hardware measurement, not an AT-01 result (AT-01 needs participants excluded from training *and tuning*; with two participants there is no tuning set, and the protocol's six-participant target is not met).

- Data: `data/sessions`, 16 files, 764 windows, P01 and P02, mount v1 (see `ml/model-card.md`).
- Model: logistic regression, 31 features, `ml/train/train.py` defaults.
- Pooled macro-F1 0.937; held-out P01 0.892, P02 0.977. Confusion matrix in the model card.
- Known failure: `P01_idle_stand_01` fully misclassified as curl when trained on P02 alone (29/29 windows) — posture learned as class.
- Host parity test of the C++ port against Python: max feature relative error 3.2e-7, max probability error 2.2e-7, PASS.
- Deployed to `firmware/classifier`, `firmware/app` (weights) and `firmware/SmartDumbbell` (shadow mode). Board run, self-test line and inference time on hardware: **pending**.

Commands: `ml/model-card.md`, "Reproduce".
