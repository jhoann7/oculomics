"""Private research inference API; deliberately refuses unvalidated model deployment."""
import io
import json
import os
from pathlib import Path
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, UnidentifiedImageError
from torch import nn
from torchvision import models, transforms
from common import LABELS, SIZE

model_dir=Path(os.getenv("OCULOMICS_MODEL_DIR","outputs/model"))
card_path=model_dir/"model_card.json"
card=json.loads(card_path.read_text(encoding="utf-8")) if card_path.exists() else {}
app=FastAPI(title="Oculomics Research Inference")
allowed_origins=[x.strip() for x in os.getenv("OCULOMICS_ALLOWED_ORIGINS","").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=allowed_origins,allow_methods=["POST"],allow_headers=["Content-Type"])
net=None
if card.get("validation_status")=="validated" and (model_dir/"resnet18_brset.pt").exists():
    net=models.resnet18(weights=None)
    net.fc=nn.Linear(net.fc.in_features,len(LABELS))
    net.load_state_dict(torch.load(model_dir/"resnet18_brset.pt",map_location="cpu",weights_only=True))
    net.eval()
tf=transforms.Compose([transforms.Resize((SIZE,SIZE)),transforms.ToTensor(),transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])

@app.get("/health")
def health():
    return {"ready":net is not None,"validation_status":card.get("validation_status","unavailable")}

@app.post("/predict")
async def predict(file: UploadFile=File(...)):
    if net is None:
        raise HTTPException(status_code=503,detail="Validated model not available")
    if file.content_type not in {"image/jpeg","image/png","image/webp"}:
        raise HTTPException(status_code=415,detail="Unsupported image type")
    raw=await file.read(10*1024*1024+1)
    if len(raw)>10*1024*1024:raise HTTPException(status_code=413,detail="File too large")
    try:
        with Image.open(io.BytesIO(raw)) as image:
            x=tf(ImageOps.exif_transpose(image).convert("RGB")).unsqueeze(0)
    except (UnidentifiedImageError,OSError):
        raise HTTPException(status_code=400,detail="Invalid image")
    with torch.inference_mode():
        probs=torch.sigmoid(net(x))[0].tolist()
    # Research-only uncalibrated sigmoid scores must not be misrepresented.
    # Production deployment requires independent clinical review, calibration, and release governance.
    return {"model_version":card["model_version"],"validation_status":"validated",
            "probabilities":dict(zip(LABELS,probs))}
