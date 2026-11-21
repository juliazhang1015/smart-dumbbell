#!/usr/bin/env python3
"""Train and evaluate the curl / idle / other classifier.

usage: python3 ml/train/train.py --data data/sessions --out ml/results [--model logreg|mlp] [--include-excluded]

Files listed in <data>/excluded.csv (columns file, reason) are left out of training and of the
evaluation; --include-excluded uses every file.

Evaluation is leave-one-participant-out (windows from the held-out person are never
seen in training or in scaler fitting). Reports per-fold and pooled confusion matrix and
macro-F1 (AT-01 target: >= 0.85). Then refits on everybody and writes model.json plus
model_weights.h for firmware/classifier/.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).parent))
from common import CLASSES, FEATURE_NAMES, FS, HOP, WINDOW, load_dataset, read_excluded  # noqa: E402
from export_c import write_header, write_selftest_header  # noqa: E402


def make_model(kind: str):
    if kind == "logreg":
        return LogisticRegression(C=1.0, max_iter=2000)
    if kind == "mlp":
        return MLPClassifier(hidden_layer_sizes=(16,), max_iter=3000, random_state=0)
    raise ValueError(kind)


def macro_f1_from_cm(cm: np.ndarray) -> float:
    f1s = []
    for i in range(cm.shape[0]):
        denom = cm[i, :].sum() + cm[:, i].sum()
        f1s.append(2 * cm[i, i] / denom if denom else 0.0)
    return float(np.mean(f1s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path("data/sessions"))
    ap.add_argument("--out", type=Path, default=Path("ml/results"))
    ap.add_argument("--model", choices=["logreg", "mlp"], default="logreg")
    ap.add_argument("--synthetic", action="store_true", help="mark outputs as synthetic")
    ap.add_argument("--include-excluded", action="store_true", help="ignore <data>/excluded.csv")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    excluded = {} if args.include_excluded else read_excluded(args.data / "excluded.csv")
    X, y, groups, meta = load_dataset(args.data, set(excluded))
    if excluded:
        print(f"left out {len(excluded)} files listed in {args.data / 'excluded.csv'}: {' '.join(sorted(excluded))}")
    parts = sorted(set(groups))
    print(f"{len(meta)} files, {len(X)} windows, {len(parts)} participants: {' '.join(parts)}")
    for c in range(len(CLASSES)):
        print(f"  {CLASSES[c]:6s} {int((y == c).sum()):5d} windows")

    cm_total = np.zeros((3, 3), dtype=int)
    fold_f1 = {}
    for p in parts:
        tr, te = groups != p, groups == p
        if te.sum() == 0 or len(set(y[tr])) < 3:
            continue
        sc = StandardScaler().fit(X[tr])
        clf = make_model(args.model).fit(sc.transform(X[tr]), y[tr])
        pred = clf.predict(sc.transform(X[te]))
        fold_f1[p] = f1_score(y[te], pred, average="macro", labels=[0, 1, 2], zero_division=0)
        cm_total += confusion_matrix(y[te], pred, labels=[0, 1, 2])
    pooled_f1 = macro_f1_from_cm(cm_total)

    print("\nLeave-one-participant-out")
    for p, f in fold_f1.items():
        print(f"  held out {p}: macro-F1 {f:.3f}")
    print(f"  pooled macro-F1 {pooled_f1:.3f}  (AT-01 target >= 0.85)")
    print("  confusion matrix, rows = true, cols = predicted, order", CLASSES)
    for i, row in enumerate(cm_total):
        print(f"  {CLASSES[i]:6s} {row}")

    sc = StandardScaler().fit(X)
    clf = make_model(args.model).fit(sc.transform(X), y)
    model = {
        "synthetic": args.synthetic, "model": args.model, "fs": FS, "window": WINDOW, "hop": HOP,
        "classes": CLASSES, "feature_names": FEATURE_NAMES,
        "scaler_mean": sc.mean_.tolist(), "scaler_scale": sc.scale_.tolist(),
        "lopo_macro_f1": {k: float(v) for k, v in fold_f1.items()}, "pooled_macro_f1": pooled_f1,
        "confusion": cm_total.tolist(), "n_windows": int(len(X)), "participants": parts,
        "excluded_files": sorted(excluded),
    }
    if args.model == "logreg":
        model["layers"] = [{"W": clf.coef_.T.tolist(), "b": clf.intercept_.tolist(), "act": "softmax"}]
    else:
        acts = ["relu"] * (len(clf.coefs_) - 1) + ["softmax"]
        model["layers"] = [{"W": W.tolist(), "b": b.tolist(), "act": a}
                           for W, b, a in zip(clf.coefs_, clf.intercepts_, acts)]
    (args.out / "model.json").write_text(json.dumps(model, indent=1))
    write_header(model, args.out / "model_weights.h")
    (args.out / "files.json").write_text(json.dumps(meta, indent=1, default=str))

    # firmware self-test: one raw window from the first file, its features and expected probabilities
    from common import load_csv, windows
    first = args.data / meta[0]["file"]
    w0 = windows(load_csv(first))[0]
    probs = clf.predict_proba(sc.transform(X[:1]))[0]
    (args.out / "selftest.json").write_text(json.dumps(
        {"file": first.name, "features": X[0].tolist(), "probs": probs.tolist(),
         "label": CLASSES[int(probs.argmax())]}, indent=1))
    write_selftest_header(w0, X[0], probs, first.name, args.out / "selftest.h")
    print(f"\nwrote model.json, model_weights.h, selftest.h, files.json, selftest.json to {args.out}")
    if args.synthetic:
        print("SYNTHETIC data: these numbers say the pipeline runs, nothing about real performance.")


if __name__ == "__main__":
    main()
