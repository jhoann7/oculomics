"""Create NON-PUBLIC multi-label diagnosis manifests without copying original images."""
import argparse
import csv
from pathlib import Path
import pandas as pd
LABELS=["diabetic_retinopathy","macular_edema","scar","nevus","amd","vascular_occlusion","hypertensive_retinopathy","drusen","hemorrhage","retinal_detachment","myopic_fundus","increased_cup_disc","other"]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--labels",required=True)
    p.add_argument("--images",required=True)
    p.add_argument("--output",default="outputs/diagnoses")
    args=p.parse_args()
    df=pd.read_csv(args.labels,dtype={"image_id":str,"patient_id":str})
    dest=Path(args.output);dest.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for k in LABELS:
        folder=dest/k;folder.mkdir(exist_ok=True)
        ids=df.loc[pd.to_numeric(df[k],errors="coerce")==1,["image_id","patient_id"]].copy()
        ids["local_path"]=ids.image_id.map(lambda z:str(Path(args.images)/f"{z}.jpg"))
        ids["exists"]=ids.local_path.map(lambda z:Path(z).is_file())
        ids.to_csv(folder/"manifest.csv",index=False)
        manifest.append((k,int(len(ids)),int(ids.exists.sum())))
    with (dest/"summary.csv").open("w",newline="",encoding="utf-8") as fp:
        writer=csv.writer(fp);writer.writerow(["label","positive_records","local_images_found"]);writer.writerows(manifest)
    print("Manifests generated locally. NO patient data or manifests should be committed to GitHub.")
if __name__=="__main__":main()
