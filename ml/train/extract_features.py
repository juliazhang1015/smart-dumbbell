"""Extract window-level IMU features from P01 recordings."""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data/sessions"
OUTPUT = Path(__file__).resolve().with_name("p01_features.csv")

AXES = ["ax", "ay", "az", "gx", "gy", "gz"]

FILES = {
    "curl": [
        "P01_curl_slow_01.csv",
        "P01_curl_normal_01.csv",
        "P01_curl_fast_02.csv",
    ],
    "idle": [
        "P01_idle_stand_01.csv",
        "P01_idle_table_01.csv",
        "P01_idle_lap_01.csv",
    ],
    "other": [
        "P01_other_mixed_01.csv",
    ],
}


def extract_window_features(window):
    features = {}

    for axis in AXES:
        values = window[axis].to_numpy(dtype=float)

        features[f"{axis}_mean"] = float(np.mean(values))
        features[f"{axis}_std"] = float(np.std(values))
        features[f"{axis}_rms"] = float(
            np.sqrt(np.mean(values ** 2))
        )
        features[f"{axis}_range"] = float(
            np.max(values) - np.min(values)
        )

    gx = window["gx"].to_numpy(dtype=float)
    gy = window["gy"].to_numpy(dtype=float)
    gz = window["gz"].to_numpy(dtype=float)

    total = np.sqrt(gx**2 + gy**2 + gz**2)

    features["x_dominance"] = float(
        np.mean(np.abs(gx) / np.maximum(total, 1e-6))
    )

    return features


def main():
    records = []

    for label, filenames in FILES.items():
        for filename in filenames:
            df = pd.read_csv(DATA_DIR / filename)

            # Use timestamps rather than assuming exact sample rate.
            time_s = (
                df["t_ms"].to_numpy(dtype=float)
                - float(df["t_ms"].iloc[0])
            ) / 1000.0

            duration = float(time_s[-1])
            start = 0.0

            while start + 2.0 <= duration:
                mask = (
                    (time_s >= start)
                    & (time_s < start + 2.0)
                )

                window = df.loc[mask]

                if len(window) >= 150:
                    features = extract_window_features(window)
                    features["label"] = label
                    features["source_file"] = filename
                    features["start_s"] = round(start, 2)
                    records.append(features)

                start += 1.0

    if not records:
        raise ValueError("No P01 windows contain enough samples for training")

    result = pd.DataFrame(records)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    print(f"Saved: {OUTPUT}")
    print(f"Total windows: {len(result)}")
    print("\nWindows per class:")
    print(result["label"].value_counts().to_string())
    print(f"\nFeature count: {len(result.columns) - 3}")


if __name__ == "__main__":
    main()
