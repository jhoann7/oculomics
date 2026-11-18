"""Baseline supervised multi-label fundus classifier (research only)."""
import argparse
import json
import random
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageOps
from sklearn.metrics import roc_auc_score, average_precision_score
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from common import LABELS, SIZE, image_path

class Brset(Dataset):
    def __init__(self, csv, images, train=False):
        self.frame=pd.read_csv(csv)
        self.images=images
        self.tf=transforms.Compose([
            transforms.Resize((SIZE,SIZE)),
            transforms.RandomHorizontalFlip() if train else transforms.Lambda(lambda x:x),
            transforms.ToTensor(),
            transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
        ])
    def __len__(self):return len(self.frame)
    def __getitem__(self, i):
        row=self.frame.iloc[i]
        with Image.open(image_path(self.images,row.image_id)) as im:
            image=self.tf(ImageOps.exif_transpose(im).convert("RGB"))
        y=torch.tensor(row[LABELS].to_numpy(dtype=np.float32),dtype=torch.float32)
        return image,y

def evaluate(model, loader, device):
    model.eval(); ys=[]; ps=[]
    with torch.no_grad():
        for x,y in loader:
            probs=torch.sigmoid(model(x.to(device))).cpu().numpy()
            ys.append(y.numpy());ps.append(probs)
    y=np.concatenate(ys); prob=np.concatenate(ps)
    metrics={}
    for i,label in enumerate(LABELS):
        vals=y[:,i]
        if len(np.unique(vals))<2:
            metrics[label]={"auroc":None,"auprc":None,"positives":int(vals.sum())}
        else:
            metrics[label]={"auroc":float(roc_auc_score(vals,prob[:,i])),
                            "auprc":float(average_precision_score(vals,prob[:,i])),
                            "positives":int(vals.sum())}
    return metrics

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--images",required=True)
    p.add_argument("--splits",default="outputs/splits")
    p.add_argument("--epochs",type=int,default=8)
    p.add_argument("--batch-size",type=int,default=16)
    p.add_argument("--lr",type=float,default=1e-4)
    p.add_argument("--out",default="outputs/model")
    args=p.parse_args()
    random.seed(42);np.random.seed(42);torch.manual_seed(42)
    device="cuda" if torch.cuda.is_available() else "cpu"
    root=Path(args.splits); out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    train=Brset(root/"train.csv",args.images,True)
    val=Brset(root/"val.csv",args.images)
    # Test set intentionally NOT used during training or model selection.
    train_loader=DataLoader(train,batch_size=args.batch_size,shuffle=True,num_workers=0)
    val_loader=DataLoader(val,batch_size=args.batch_size,num_workers=0)
    net=models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    net.fc=nn.Linear(net.fc.in_features,len(LABELS));net.to(device)
    optimizer=torch.optim.AdamW(net.parameters(),lr=args.lr)
    loss_fn=nn.BCEWithLogitsLoss()
    best=float("inf")
    for epoch in range(args.epochs):
        net.train();total=0
        for x,y in train_loader:
            optimizer.zero_grad()
            loss=loss_fn(net(x.to(device)),y.to(device))
            loss.backward(); optimizer.step()
            total+=float(loss.item())
        net.eval(); val_loss=0
        with torch.no_grad():
            for x,y in val_loader:
                val_loss+=float(loss_fn(net(x.to(device)),y.to(device)).item())
        val_loss/=max(len(val_loader),1)
        print(f"epoch {epoch+1} train_loss={total/max(len(train_loader),1):.4f} val_loss={val_loss:.4f}")
        if val_loss<best:
            best=val_loss
            torch.save(net.state_dict(),out/"resnet18_brset.pt")
    net.load_state_dict(torch.load(out/"resnet18_brset.pt",map_location=device,weights_only=True))
    metrics=evaluate(net,val_loader,device)
    (out/"validation_metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    (out/"model_card.json").write_text(json.dumps({
      "model_version":"resnet18-brset-experimental-0.1",
      "validation_status":"research_only",
      "labels":LABELS,
      "image_size":SIZE,
      "note":"NOT clinically validated. Raw scores are not calibrated disease probabilities."
    },indent=2),encoding="utf-8")
    print("Saved research checkpoint and validation report. Not cleared for clinical or public predictions.")
if __name__=="__main__":main()
