"""Train a preliminary IMU activity classifier using P01 data."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

DATA_PATH = Path("ml/train/p01_features.csv")
MODEL_PATH = Path("ml/train/activity_classifier.joblib")

df = pd.read_csv(DATA_PATH)

metadata = ["label", "source_file", "start_s"]
feature_columns = [c for c in df.columns if c not in metadata]

X = df[feature_columns]
y = df["label"]

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)

model.fit(X, y)

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(
    {
        "model": model,
        "feature_columns": feature_columns,
        "classes": list(model.classes_),
    },
    MODEL_PATH,
)

print("Training complete!")
print(f"Training windows: {len(X)}")
print(f"Features: {len(feature_columns)}")
print(f"Classes: {list(model.classes_)}")
print(f"Model saved: {MODEL_PATH}")

importance = pd.Series(
    model.feature_importances_,
    index=feature_columns,
).sort_values(ascending=False)

print("\nTop 10 important features:")
print(importance.head(10).to_string())
