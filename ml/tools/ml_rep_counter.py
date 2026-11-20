"""Offline repetition counter with ML activity filtering."""

import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml" / "tools"))
sys.path.insert(0, str(ROOT / "ml" / "train"))

from test_cycle_counter import count_cycles
from extract_features import extract_window_features


def count_ml_reps(csv_path, model_path):
    df = pd.read_csv(csv_path)

    bundle = joblib.load(model_path)
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    candidate_count, events = count_cycles(csv_path)

    time_s = (
        df["t_ms"].to_numpy(dtype=float)
        - float(df["t_ms"].iloc[0])
    ) / 1000.0

    accepted = []
    rejected = []

    for event in events:
        # Use the two seconds preceding the candidate event.
        mask = (
            (time_s >= event - 2.0)
            & (time_s <= event)
        )

        window = df.loc[mask]

        if len(window) < 150:
            rejected.append((event, "insufficient_data"))
            continue

        features = extract_window_features(window)

        X = pd.DataFrame(
            [[features[col] for col in feature_columns]],
            columns=feature_columns,
        )

        prediction = model.predict(X)[0]

        if prediction == "curl":
            accepted.append(event)
        else:
            rejected.append((event, prediction))

    return candidate_count, accepted, rejected


def main():
    model_path = ROOT / "ml/train/activity_classifier.joblib"

    files = [
        "P01_curl_slow_01.csv",
        "P01_curl_normal_01.csv",
        "P01_curl_fast_02.csv",
        "P01_idle_stand_01.csv",
        "P01_idle_table_01.csv",
        "P01_idle_lap_01.csv",
        "P01_other_mixed_01.csv",
        "P01_partial_mixed_01.csv",
    ]

    for filename in files:
        path = ROOT / "data/sessions" / filename

        candidates, accepted, rejected = count_ml_reps(
            path, model_path
        )

        print(f"\n{filename}")
        print(f"V3 candidates: {candidates}")
        print(f"ML accepted: {len(accepted)}")
        print(f"ML rejected: {len(rejected)}")
        print(f"Accepted events: {accepted}")


if __name__ == "__main__":
    main()
