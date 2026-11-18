"""Patient-level split + multi-label index. No copies of sensitive images by default."""
import argparse
from pathlib import Path
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from common import LABELS, load_labels, image_path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--images", required=True)
    p.add_argument("--output", default="outputs/splits")
    p.add_argument("--seed", type=int, default=42)
    args=p.parse_args()
    f=load_labels(args.csv)
    f=f[(f.quality=="Adequate") & f.image_id.map(lambda x: image_path(args.images,x).is_file())].copy()
    f=f[f[LABELS].notna().all(axis=1)].copy()
    if len(f)<30 or f.patient_id.nunique()<15: raise ValueError("Insufficient patient data.")
    group=GroupShuffleSplit(n_splits=1,test_size=0.20,random_state=args.seed)
    dev,test=next(group.split(f,groups=f.patient_id))
    develop=f.iloc[dev]; test_f=f.iloc[test]
    group2=GroupShuffleSplit(n_splits=1,test_size=0.125,random_state=args.seed)
    train_idx,val_idx=next(group2.split(develop,groups=develop.patient_id))
    parts={"train":develop.iloc[train_idx], "val":develop.iloc[val_idx], "test":test_f}
    ids=[set(x.patient_id) for x in parts.values()]
    assert not(ids[0]&ids[1] or ids[0]&ids[2] or ids[1]&ids[2])
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    for name,data in parts.items():
        data[["image_id","patient_id",*LABELS]].to_csv(out/f"{name}.csv",index=False)
        print(name, "images:",len(data),"patients:",data.patient_id.nunique())
    print("WARNING: patient-level random split is not multi-label stratified; inspect rare-label coverage before training.")
if __name__=="__main__":main()
