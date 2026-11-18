"""Audit local BRSET paths and labels without exposing restricted patient records."""
import argparse
import json
from pathlib import Path
from common import LABELS, load_labels, image_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--images", required=True)
    p.add_argument("--out", default="outputs/audit.json")
    args = p.parse_args()
    frame = load_labels(args.csv)
    existing = frame.image_id.map(lambda x: image_path(args.images, x).is_file())
    counts = frame[LABELS].sum().fillna(0).astype(int).to_dict()
    valid = frame[LABELS].notna().sum().astype(int).to_dict()
    report = {
        "rows": int(len(frame)),
        "unique_patients": int(frame.patient_id.nunique()),
        "images_on_disk": int(existing.sum()),
        "images_missing": int((~existing).sum()),
        "quality": frame.quality.fillna("missing").value_counts().to_dict(),
        "positive_labels": counts,
        "known_labels": valid,
    }
    output = Path(args.out); output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
