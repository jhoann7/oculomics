"""Shared BRSET research configuration. Raw data and weights are not public."""
from pathlib import Path
import pandas as pd

LABELS = [
    "diabetic_retinopathy", "macular_edema", "scar", "nevus", "amd",
    "vascular_occlusion", "hypertensive_retinopathy", "drusen", "hemorrhage",
    "retinal_detachment", "myopic_fundus", "increased_cup_disc", "other",
]
IMAGE_SUFFIX = ".jpg"
SIZE = 224

def load_labels(path):
    frame = pd.read_csv(path, dtype={"image_id": str, "patient_id": str})
    required = {"image_id", "patient_id", "quality", *LABELS}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing BRSET columns: {sorted(missing)}")
    if frame.image_id.duplicated().any():
        raise ValueError("Duplicated image_id values.")
    for label in LABELS:
        values = pd.to_numeric(frame[label], errors="coerce")
        frame[label] = values.where(values.isin([0, 1]))
    return frame

def image_path(root, image_id):
    return Path(root) / f"{image_id}{IMAGE_SUFFIX}"
