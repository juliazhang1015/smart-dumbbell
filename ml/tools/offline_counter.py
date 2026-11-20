"""Baseline offline dumbbell repetition counter."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def count_reps(csv_path, threshold=35.0, smooth_ms=100):
    df = pd.read_csv(csv_path)

    required = {"t_ms", "gx"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns: {required - set(df.columns)}")

    t = df["t_ms"].to_numpy(dtype=float) / 1000.0
    gx = df["gx"].to_numpy(dtype=float)

    if len(t) < 2 or np.any(np.diff(t) <= 0):
        raise ValueError("Invalid timestamps")

    dt = float(np.median(np.diff(t)))
    window = max(1, round(smooth_ms / (dt * 1000)))

    # Moving-average smoothing
    gx_smooth = (
        pd.Series(gx)
        .rolling(window=window, center=True, min_periods=1)
        .mean()
        .to_numpy()
    )

    reps = 0
    state = "waiting_for_raise"
    raise_start = None
    events = []

    for i, value in enumerate(gx_smooth):
        if state == "waiting_for_raise":
            if value < -threshold:
                raise_start = t[i]
                state = "waiting_for_lower"

        elif state == "waiting_for_lower":
            if value > threshold:
                duration = t[i] - raise_start

                # Reject extremely short motions
                if duration >= 0.25:
                    reps += 1
                    events.append(round(t[i] - t[0], 2))

                state = "waiting_for_raise"

    return reps, events


def main():
    parser = argparse.ArgumentParser(
        description="Count dumbbell curls from IMU CSV"
    )
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--threshold", type=float, default=35.0)
    args = parser.parse_args()

    reps, events = count_reps(
        args.csv_file,
        threshold=args.threshold,
    )

    print(f"File: {args.csv_file.name}")
    print(f"Predicted repetitions: {reps}")
    print(f"Detected events (s): {events}")


if __name__ == "__main__":
    main()
