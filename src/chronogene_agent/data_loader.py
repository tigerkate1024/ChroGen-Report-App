
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

REQUIRED_FILES = {
    "participants": "participants.csv",
    "lifestyle": "lifestyle_questionnaire.csv",
    "face_skin": "face_skin_features.csv",
    "genome": "skin_genomic_variants.csv",
    "skin_scrna": "skin_scRNA_pathway_scores.csv",
    "oral_epi": "oral_epithelial_transcriptome.csv",
    "oral_microbiome": "oral_microbiome.csv",
    "targets": "target_mechanism_scores.csv",
    "ingredients": "ingredient_fingerprints.csv",
}

@dataclass
class MultiModalData:
    tables: dict[str, pd.DataFrame]

def load_tables(data_dir: str | Path) -> MultiModalData:
    data_dir = Path(data_dir)
    tables = {}
    missing = []
    for key, file_name in REQUIRED_FILES.items():
        path = data_dir / file_name
        if not path.exists():
            missing.append(file_name)
        else:
            tables[key] = pd.read_csv(path)
    if missing:
        raise FileNotFoundError(f"Missing files in {data_dir}: {missing}")
    validate_tables(tables)
    return MultiModalData(tables)

def validate_tables(tables: dict[str, pd.DataFrame]) -> None:
    for key, df in tables.items():
        if key != "ingredients" and "subject_id" not in df.columns:
            raise ValueError(f"{key} must contain subject_id")
    base_ids = set(tables["participants"]["subject_id"].astype(str))
    for key, df in tables.items():
        if key == "ingredients":
            continue
        ids = set(df["subject_id"].astype(str))
        missing = base_ids - ids
        if missing:
            raise ValueError(f"{key} is missing subject_ids, e.g. {sorted(list(missing))[:5]}")

def get_subject_payload(data: MultiModalData, subject_id: str) -> dict:
    payload = {}
    for key, df in data.tables.items():
        if "subject_id" not in df.columns:
            continue
        rows = df[df["subject_id"].astype(str) == str(subject_id)]
        if rows.empty:
            raise ValueError(f"{subject_id} not found in {key}")
        if key == "skin_scrna":
            payload[key] = rows.to_dict(orient="records")
        else:
            payload[key] = rows.iloc[0].to_dict()
    return payload
