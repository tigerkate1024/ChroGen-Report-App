
from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def aggregate_skin_scrna(df: pd.DataFrame) -> pd.DataFrame:
    value_cols = [c for c in df.columns if c not in {"subject_id", "cell_type"}]
    wide = df.pivot_table(index="subject_id", columns="cell_type", values=value_cols, aggfunc="mean")
    wide.columns = [f"skin_scrna__{metric}__{cell_type}" for metric, cell_type in wide.columns]
    return wide.reset_index()

def build_feature_table(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    base = tables["participants"].copy()
    for key in ["lifestyle", "face_skin", "genome", "oral_epi", "oral_microbiome"]:
        df = tables[key].copy()
        rename = {c: f"{key}__{c}" for c in df.columns if c != "subject_id"}
        base = base.merge(df.rename(columns=rename), on="subject_id", how="left")
    scrna = aggregate_skin_scrna(tables["skin_scrna"])
    base = base.merge(scrna, on="subject_id", how="left")
    return base

def make_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    categorical = [c for c in X.columns if X[c].dtype == "object"]
    numeric = [c for c in X.columns if c not in categorical]
    return ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
