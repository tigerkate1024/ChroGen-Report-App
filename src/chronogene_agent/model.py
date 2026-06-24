
from __future__ import annotations

from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .features import build_feature_table, make_preprocessor
from .mechanisms import MECHANISM_COLUMNS

def train_baseline(tables: dict[str, pd.DataFrame], model_path: str | Path):
    features = build_feature_table(tables)
    targets = tables["targets"][["subject_id"] + MECHANISM_COLUMNS].copy()
    df = features.merge(targets, on="subject_id", how="inner")

    X = df.drop(columns=["subject_id"] + MECHANISM_COLUMNS, errors="ignore")
    y = df[MECHANISM_COLUMNS]

    preprocessor = make_preprocessor(X)
    regressor = RandomForestRegressor(n_estimators=260, min_samples_leaf=3, random_state=42, n_jobs=-1)
    pipe = Pipeline([("preprocessor", preprocessor), ("regressor", regressor)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    pipe.fit(X_train, y_train)
    pred = pipe.predict(X_test)
    mae = float(mean_absolute_error(y_test, pred))

    bundle = {
        "pipeline": pipe,
        "mechanism_columns": MECHANISM_COLUMNS,
        "mae": mae,
        "feature_columns": list(X.columns),
    }
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    return {"model_path": str(model_path), "mae": mae, "n_train": len(X_train), "n_test": len(X_test)}

def load_model(model_path: str | Path):
    return joblib.load(model_path)

def predict_subject(tables: dict[str, pd.DataFrame], model_bundle: dict, subject_id: str) -> dict[str, float]:
    features = build_feature_table(tables)
    row = features[features["subject_id"].astype(str) == str(subject_id)]
    if row.empty:
        raise ValueError(f"Subject not found: {subject_id}")
    X = row.drop(columns=["subject_id"], errors="ignore")
    pred = model_bundle["pipeline"].predict(X)[0]
    return {m: float(round(v, 1)) for m, v in zip(model_bundle["mechanism_columns"], pred)}

def get_target_scores(tables: dict[str, pd.DataFrame], subject_id: str) -> dict[str, float]:
    row = tables["targets"][tables["targets"]["subject_id"].astype(str) == str(subject_id)]
    if row.empty:
        raise ValueError(f"Subject not found: {subject_id}")
    return {m: float(row.iloc[0][m]) for m in MECHANISM_COLUMNS}
