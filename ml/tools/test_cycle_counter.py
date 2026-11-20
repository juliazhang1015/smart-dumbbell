import numpy as np
import pandas as pd
from pathlib import Path


def count_cycles(path, min_raise=70, min_lower=70,
                 threshold=20, smooth_window=10):
    d = pd.read_csv(path)

    t = (d.t_ms - d.t_ms.iloc[0]).to_numpy(dtype=float) / 1000
    gx = d.gx.rolling(
        smooth_window, center=True, min_periods=1
    ).mean().to_numpy()

    dt = np.diff(t, prepend=t[0])

    state = "waiting"
    raise_angle = 0.0
    lower_angle = 0.0
    reps = 0
    events = []

    for i, v in enumerate(gx):
        if state == "waiting":
            if v < -threshold:
                state = "raising"
                raise_angle = 0.0
                lower_angle = 0.0

        if state == "raising":
            if v < -threshold:
                raise_angle += -v * dt[i]

            elif v > threshold:
                if raise_angle >= min_raise:
                    state = "lowering"
                else:
                    state = "waiting"

        elif state == "lowering":
            if v > threshold:
                lower_angle += v * dt[i]

                if lower_angle >= min_lower:
                    reps += 1
                    events.append(round(float(t[i]), 2))
                    state = "waiting"
                    raise_angle = 0.0
                    lower_angle = 0.0

            elif v < -threshold:
                # The movement reversed before completing the lower phase.
                state = "waiting"
                raise_angle = 0.0
                lower_angle = 0.0

    return reps, events


if __name__ == "__main__":
    files = [
        ("P01_curl_slow_01.csv", 13),
        ("P01_curl_normal_01.csv", 17),
        ("P01_curl_fast_02.csv", 26),
    ]

    for name, expected in files:
        predicted, events = count_cycles(
            Path("data/sessions") / name
        )

        print(f"\n{name}")
        print(f"Expected: {expected}")
        print(f"Predicted: {predicted}")
        print(f"Difference: {predicted - expected:+d}")
        print(f"Events: {events}")
