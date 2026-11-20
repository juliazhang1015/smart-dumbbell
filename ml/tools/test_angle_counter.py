import numpy as np
import pandas as pd
from pathlib import Path


def count_angle_reps(path, min_range=80, return_tolerance=25):
    d = pd.read_csv(path)

    t = (d.t_ms - d.t_ms.iloc[0]).to_numpy() / 1000
    gx = d.gx.rolling(10, center=True, min_periods=1).mean().to_numpy()

    dt = np.diff(t, prepend=t[0])
    angle = np.cumsum(gx * dt)

    # Track the starting position and completed raise/lower cycles.
    baseline = float(np.median(angle[:min(20, len(angle))]))
    lowest_angle = baseline
    state = "waiting"
    reps = 0
    events = []

    for i, a in enumerate(angle):
        if state == "waiting":
            # Update the baseline only when near the resting position.
            if abs(a - baseline) <= return_tolerance:
                baseline = 0.995 * baseline + 0.005 * a

            if a <= baseline - min_range:
                lowest_angle = a
                state = "raised"

        elif state == "raised":
            lowest_angle = min(lowest_angle, a)

            # Count only after returning close to the starting angle.
            if a >= baseline - return_tolerance:
                reps += 1
                events.append(round(float(t[i]), 2))
                baseline = float(a)
                state = "waiting"

    return reps, events


files = [
    ("P01_curl_slow_01.csv", 13),
    ("P01_curl_normal_01.csv", 17),
    ("P01_curl_fast_02.csv", 26),
]

for name, expected in files:
    path = Path("data/sessions") / name
    predicted, events = count_angle_reps(path)

    print(f"\n{name}")
    print(f"Expected: {expected}")
    print(f"Predicted: {predicted}")
    print(f"Difference: {predicted - expected:+d}")
    print(f"Events: {events}")
