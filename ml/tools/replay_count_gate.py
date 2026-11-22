"""Replay the SmartDumbbell rep counter on data/sessions, with and without model confirmation.

Python port of counterSample() and gateAccept() in firmware/SmartDumbbell/SmartDumbbell.ino (fixed
dt = 1/104 s, gyro X from the CSV in deg/s). Every file is classified by the leave-one-participant-out
model that has not seen its participant, trained exactly as ml/train/train.py trains (files in
excluded.csv not trained on, rotated idle windows). Reference counts: true_reps in sessions.csv for
curl and partial files, 0 for other_mixed; files without a reference are listed but not scored.

Modes:
  angle   swing gate only (COUNT_GATE 0)
  last    rep counts only if the last once-per-second label is curl (not used; for comparison)
  at_rep  rep counts only if the 2 s ending at the rep are classified curl (COUNT_GATE 1);
          accepted when fewer than 2 s are buffered, as on the board

Run from the repository root:
  python ml/tools/replay_count_gate.py [--swing-min-deg 60]
"""
import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml" / "train"))
from common import CLASSES, HOP, WINDOW, features_batch, load_csv, load_dataset, read_excluded, rotate_about_x, windows  # noqa: E402
import train  # noqa: E402

CURL = CLASSES.index("curl")
MODES = ("angle", "last", "at_rep")


def loo_models(data: Path):
    excluded = read_excluded(data / "excluded.csv")
    X, y, groups, meta = load_dataset(data)
    ex = np.concatenate([np.full(m["windows"], m["file"] in excluded) for m in meta])
    xa, ga = [], []
    for m in meta:
        if m["label"] != "idle" or m["file"] in excluded:
            continue
        ws = windows(load_csv(data / m["file"]))
        for deg in train.AUGMENT_IDLE_DEGREES:
            xa.append(features_batch(rotate_about_x(ws, deg)))
            ga.append(np.full(len(ws), m["participant"], dtype=object))
    Xa, ga = np.concatenate(xa), np.concatenate(ga)
    ya = np.full(len(Xa), CLASSES.index("idle"))
    models = {}
    for p in sorted(set(groups)):
        tr, keep = (groups != p) & ~ex, ga != p
        Xt, yt = np.vstack([X[tr], Xa[keep]]), np.concatenate([y[tr], ya[keep]])
        sc = StandardScaler().fit(Xt)
        models[p] = (sc, train.make_model("logreg").fit(sc.transform(Xt), yt))
    return models, meta, excluded


def count(raw, t_ms, label, mode, swing_min_deg):
    """label[i]: class of the 2 s window ending at sample i (-1 if fewer than 2 s)."""
    d2r = math.pi / 180
    lifting = returning = False
    swing = peak = 0.0
    phase_at, sign, reps = 0.0, 1, 0
    dt = 1 / 104
    for i in range(len(raw)):
        sp, now = raw[i, 3] * d2r, t_ms[i]
        if lifting:
            swing += sp * dt * sign
            peak = max(peak, swing)
            if now - phase_at > 8000:
                lifting = False
                continue
        if not lifting:
            if abs(sp) > 0.9:
                lifting, returning, phase_at = True, False, now
                sign = 1 if sp > 0 else -1
                swing = peak = abs(sp) * dt
        elif not returning:
            if now - phase_at > 200 and sp * sign < -0.9:
                returning = True
        elif abs(sp) < 0.35 and now - phase_at > 450:
            if peak < swing_min_deg * d2r:
                lifting = False
            elif swing <= 0.5 * peak:
                lifting = False
                if mode == "angle":
                    ok = True
                elif mode == "at_rep":
                    ok = label[i] < 0 or label[i] == CURL
                else:  # last periodic inference: windows ending at WINDOW-1 + k*HOP
                    j = i - (i - (WINDOW - 1)) % HOP if i >= WINDOW - 1 else -1
                    ok = j >= 0 and label[j] == CURL
                reps += ok
    return reps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=ROOT / "data" / "sessions")
    ap.add_argument("--swing-min-deg", type=float, default=60.0)
    args = ap.parse_args()
    models, meta, excluded = loo_models(args.data)
    ref = {r["file"]: r for r in csv.DictReader(open(args.data / "sessions.csv"))}
    rows = []
    for m in meta:
        if m["label"] == "idle":
            continue
        df = load_csv(args.data / m["file"])
        raw = df[["ax", "ay", "az", "gx", "gy", "gz"]].to_numpy(np.float32)
        t = df["t_ms"].to_numpy()
        ends = np.arange(WINDOW - 1, len(raw))
        sc, clf = models[m["participant"]]
        ws = np.stack([raw[e - WINDOW + 1:e + 1] for e in ends])
        label = np.full(len(raw), -1)
        label[ends] = clf.predict(sc.transform(features_batch(ws)))
        r = ref[m["file"]]
        kind = r["record_label"]
        truth = 0 if kind == "other" else (float(r["true_reps"]) if r["true_reps"] else None)
        rows.append((m["file"], kind, truth, [count(raw, t, label, md, args.swing_min_deg) for md in MODES]))

    print(f"swing_min_deg {args.swing_min_deg:.0f}")
    print(f"{'file':28s} {'ref':>4s} " + " ".join(f"{md:>7s}" for md in MODES))
    for f, _, truth, c in rows:
        note = "  (excluded from training)" if f in excluded else ""
        print(f"{f:28s} {'' if truth is None else int(truth):>4} " + " ".join(f"{x:7d}" for x in c) + note)
    print()
    for kind in ("curl", "partial", "other"):
        sel = [r for r in rows if r[1] == kind and r[2] is not None]
        total = sum(r[2] for r in sel)
        parts = []
        for k, md in enumerate(MODES):
            n = sum(r[3][k] for r in sel)
            err = sum(abs(r[3][k] - r[2]) for r in sel)
            parts.append(f"{md} {n} (|error| {err:.0f})")
        print(f"{kind:8s} {len(sel):2d} files, reference {total:.0f}: " + ", ".join(parts))


if __name__ == "__main__":
    main()
