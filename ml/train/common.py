"""Shared loading, windowing and feature code for the motion classifier.

Everything the firmware must reproduce lives here: FS, WINDOW, HOP, FEATURE_NAMES
and features(). Keep features() simple enough to port to C++ by hand.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

FS = 104                      # Hz, LSM6DSOX ODR used by 04_imu_stream
WINDOW = 2 * FS               # 208 samples = 2 s
HOP = FS                      # 1 s -> 50 % overlap
COLUMNS = ["t_ms", "ax", "ay", "az", "gx", "gy", "gz"]
CLASSES = ["curl", "idle", "other"]

# record_label -> training class (data-protocol.md section 5)
RECORD_TO_CLASS = {"curl": "curl", "idle": "idle", "other": "other", "partial": "curl"}

NAME_RE = re.compile(r"^(P\d{2})_(curl|idle|other|partial)_([a-z]+)_(\d{2})\.csv$")


def parse_name(path: Path) -> dict:
    m = NAME_RE.match(path.name)
    if not m:
        raise ValueError(f"file name does not follow data-protocol.md section 7: {path.name}")
    participant, record_label, variant, take = m.groups()
    return {"participant": participant, "record_label": record_label,
            "variant": variant, "take": int(take), "label": RECORD_TO_CLASS[record_label]}


def load_csv(path: Path) -> pd.DataFrame:
    """Read a 04_imu_stream capture. Header line optional (cat captures have none)."""
    with open(path) as f:
        first = f.readline()
    header = 0 if first.startswith("t_ms") else None
    return pd.read_csv(path, header=header, names=COLUMNS, dtype=float)


def check_timing(df: pd.DataFrame, max_gap_ms: float = 15.0) -> dict:
    dt = np.diff(df["t_ms"].to_numpy())
    dur_s = (df["t_ms"].iloc[-1] - df["t_ms"].iloc[0]) / 1000.0
    return {"n": len(df), "duration_s": dur_s,
            "rate_hz": (len(df) - 1) / dur_s if dur_s > 0 else float("nan"),
            "dt_max_ms": float(dt.max()) if len(dt) else float("nan"),
            "gaps": int((dt > max_gap_ms).sum())}


def windows(df: pd.DataFrame, window: int = WINDOW, hop: int = HOP) -> np.ndarray:
    """Return (n_windows, window, 6) array of ax..gz. Drops the trailing partial window."""
    x = df[["ax", "ay", "az", "gx", "gy", "gz"]].to_numpy(dtype=np.float32)
    n = (len(x) - window) // hop + 1
    if n <= 0:
        return np.empty((0, window, 6), dtype=np.float32)
    idx = np.arange(window)[None, :] + hop * np.arange(n)[:, None]
    return x[idx]


FEATURE_NAMES: list[str] = []
for ch in ["ax", "ay", "az", "gx", "gy", "gz"]:
    FEATURE_NAMES += [f"{ch}_mean", f"{ch}_std", f"{ch}_min", f"{ch}_max"]
FEATURE_NAMES += ["acc_mag_mean", "acc_mag_std", "gyr_mag_mean", "gyr_mag_std",
                  "gx_zc", "gy_zc", "gz_zc"]
N_FEATURES = len(FEATURE_NAMES)   # 31


def features(w: np.ndarray) -> np.ndarray:
    """w: (window, 6) -> (N_FEATURES,). Order must match FEATURE_NAMES and classifier.h."""
    out = []
    for c in range(6):
        col = w[:, c]
        out += [col.mean(), col.std(), col.min(), col.max()]
    acc = np.sqrt((w[:, 0:3] ** 2).sum(axis=1))
    gyr = np.sqrt((w[:, 3:6] ** 2).sum(axis=1))
    out += [acc.mean(), acc.std(), gyr.mean(), gyr.std()]
    for c in (3, 4, 5):
        col = w[:, c] - w[:, c].mean()
        out.append(float((np.signbit(col[1:]) != np.signbit(col[:-1])).sum()))
    return np.asarray(out, dtype=np.float32)


def features_batch(ws: np.ndarray) -> np.ndarray:
    return np.stack([features(w) for w in ws]) if len(ws) else np.empty((0, N_FEATURES), np.float32)


def rotate_about_x(ws: np.ndarray, degrees: float) -> np.ndarray:
    """Rotate the sensor frame of raw windows (n, window, 6) about X, the handle axis: the same
    motion with the dumbbell held at another angle. Training-only; the firmware never calls it."""
    t = np.radians(degrees)
    c, s = np.cos(t), np.sin(t)
    r = np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float32)
    out = ws.copy()
    out[:, :, 0:3] = ws[:, :, 0:3] @ r.T
    out[:, :, 3:6] = ws[:, :, 3:6] @ r.T
    return out


def read_excluded(path: Path) -> dict:
    """excluded.csv (columns file, reason) -> {file name: reason}. Missing file -> {}."""
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype=str).fillna("")
    return dict(zip(df["file"], df["reason"]))


def load_dataset(session_dir: Path, exclude: set | None = None):
    """All sessions under session_dir, except the file names in exclude ->
    X (n, N_FEATURES), y (n,) class idx, groups (n,) participant, meta."""
    exclude = exclude or set()
    X, y, g, meta = [], [], [], []
    for path in sorted(session_dir.glob("P*.csv")):
        if path.name in exclude:
            continue
        info = parse_name(path)
        df = load_csv(path)
        ws = windows(df)
        if len(ws) == 0:
            continue
        X.append(features_batch(ws))
        y.append(np.full(len(ws), CLASSES.index(info["label"])))
        g.append(np.full(len(ws), info["participant"]))
        meta.append({**info, "file": path.name, "windows": len(ws), **check_timing(df)})
    if not X:
        raise SystemExit(f"no P??_*.csv files found in {session_dir}")
    return np.concatenate(X), np.concatenate(y), np.concatenate(g), meta
