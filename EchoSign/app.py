import os
import cv2
import numpy as np
import base64
import json
import io
from PIL import Image
import torch
from torchvision import transforms
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from EchoSign.database import (
    init_db, log_conversation,
    get_recent_conversations, get_analytics_summary
)
from EchoSign.nlp_engine import (
    reconstruct_sentence_from_signs, analyze_sentiment_and_urgency,
    text_to_signs, SIGN_DICTIONARY
)
from EchoSign.sign_engine import sign_recognizer, GESTURE_LABELS
from EchoSign.asl_alphabet_engine import asl_classifier

app = FastAPI(
    title="EchoSign AI - Assistive Communication Hub",
    description="Real-Time Sign-to-Speech & Speech-to-Sign Two-Way AI Bridge with RTX 4060 GPU Acceleration",
    version="2.0.0"
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# -------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------
class LandmarksPayload(BaseModel):
    # Primary hand ke 21 landmark points [x, y, z]
    landmarks: List[List[float]]
    # Optional doosra haath agar screen pe ho (for two-hand gestures like Namaste)
    secondary_landmarks: Optional[List[List[float]]] = None
    # Optional body landmarks (Head/Nose, Mouth/Lips, Neck, Chest, Shoulders)
    body_landmarks: Optional[Dict[str, Any]] = None

class FramePayload(BaseModel):
    image_base64: Optional[str] = ""
    landmarks: Optional[List[List[float]]] = None

class NlpRefinePayload(BaseModel):
    signs: List[str]
    auto_log: Optional[bool] = False

class TextToSignsPayload(BaseModel):
    text: str
    auto_log: Optional[bool] = False

class LogConversationPayload(BaseModel):
    channel: str
    input_raw: str
    output_text: str
    sentiment: str
    urgency: str
    urgency_score: float

# -------------------------------------------------------------
# RTX 4060 GPU Model Loader (NVIDIA Tensor Core Acceleration)
# -------------------------------------------------------------
asl_gpu_model = None
asl_classes = []
asl_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_asl_gpu_model():
    global asl_gpu_model, asl_classes
    weights_path = os.path.join(os.path.dirname(__file__), "models", "asl_rtx4060.pt")
    classes_path = os.path.join(os.path.dirname(__file__), "models", "asl_classes.json")
    if os.path.exists(weights_path) and os.path.exists(classes_path):
        try:
            from EchoSign.train_gpu import ASLResNet
            with open(classes_path) as f:
                asl_classes = json.load(f)
            model = ASLResNet(num_classes=len(asl_classes)).to(asl_device)
            model.load_state_dict(torch.load(weights_path, map_location=asl_device))
            model.eval()
            asl_gpu_model = model
            print(f"🚀 Loaded ASLResNet GPU Model on {asl_device} with {len(asl_classes)} classes!")
        except Exception as e:
            print("Notice: Error loading GPU model:", e)

init_db()
load_asl_gpu_model()

@app.on_event("startup")
def on_startup():
    init_db()
    load_asl_gpu_model()

@app.get("/")
def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "EchoSign AI Backend is Running!"}

@app.post("/api/predict_landmarks")
def predict_landmarks(payload: LandmarksPayload):
    try:
        raw_pts = payload.landmarks
        if len(raw_pts) != 21:
            raise HTTPException(status_code=400, detail="Expected exactly 21 hand landmarks.")
        result = sign_recognizer.predict(
            raw_pts, 
            secondary_landmarks=payload.secondary_landmarks,
            body_landmarks=payload.body_landmarks
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict_asl_landmarks")
def predict_asl_landmarks(payload: LandmarksPayload):
    """Ultra-low latency (<1ms) ASL alphabet prediction using 3D geometric hand landmarks."""
    if not payload.landmarks or len(payload.landmarks) != 21:
        raise HTTPException(status_code=400, detail="Expected exactly 21 hand landmarks.")
    res = asl_classifier.predict(payload.landmarks)
    return res

@app.post("/api/predict_asl_image")
def predict_asl_image(payload: FramePayload):
    """Predicts ASL Alphabet letter using RTX 4060 GPU CNN + 3D Landmark Geometric Engine."""
    geom_res = None
    if payload.landmarks and len(payload.landmarks) == 21:
        try:
            geom_res = asl_classifier.predict(payload.landmarks)
        except Exception:
            geom_res = None

    gpu_pred = None
    gpu_conf = 0.0
    top3_list = []

    # If image is supplied and GPU model is loaded, run PyTorch inference
    if payload.image_base64 and len(payload.image_base64) > 50 and asl_gpu_model is not None:
        try:
            data_str = payload.image_base64
            if "," in data_str:
                data_str = data_str.split(",", 1)[1]
            img_bytes = base64.b64decode(data_str)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

            tx = transforms.Compose([
                transforms.Resize((128, 128)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            t_img = tx(img).unsqueeze(0).to(asl_device)

            with torch.no_grad():
                outputs = asl_gpu_model(t_img)
                probs = torch.softmax(outputs, dim=1)[0]
                top_prob, top_idx = torch.topk(probs, 3)

            gpu_pred = asl_classes[top_idx[0].item()]
            gpu_conf = float(top_prob[0].item())
            top3_list = [
                {
                    "class": asl_classes[top_idx[i].item()],
                    "confidence": round(float(top_prob[i].item()), 4)
                }
                for i in range(len(top_idx))
            ]
        except Exception:
            pass

    # Hybrid Decision Fusion
    if geom_res and geom_res.get("letter") and geom_res.get("letter") != "—":
        final_letter = geom_res["letter"]
        final_conf = geom_res.get("confidence", 0.95)

        # Cross-validation with GPU CNN
        if gpu_pred == final_letter:
            final_conf = min(0.998, final_conf + 0.04)
        elif gpu_pred and gpu_conf > 0.90 and gpu_pred in ["A", "S"] and final_letter in ["A", "S"]:
            final_letter = gpu_pred
            final_conf = gpu_conf

        return {
            "prediction": final_letter,
            "confidence": round(float(final_conf), 4),
            "top3": top3_list if top3_list else [{"class": final_letter, "confidence": round(float(final_conf), 4)}],
            "device": str(asl_device),
            "engine": "hybrid_geometric_gpu"
        }

    if gpu_pred:
        return {
            "prediction": gpu_pred,
            "confidence": round(float(gpu_conf), 4),
            "top3": top3_list,
            "device": str(asl_device),
            "engine": "rtx4060_gpu"
        }

    return {
        "prediction": "—",
        "confidence": 0.0,
        "top3": [],
        "device": str(asl_device),
        "engine": "none"
    }

@app.get("/api/model_info")
def get_model_info():
    card_path = os.path.join(os.path.dirname(__file__), "models", "model_card.json")
    if os.path.exists(card_path):
        with open(card_path) as f:
            return json.load(f)
    return {
        "device": str(asl_device),
        "status": "Loaded" if asl_gpu_model is not None else "Standby",
        "classes_count": len(asl_classes)
    }

@app.post("/api/nlp_refine")
def nlp_refine(payload: NlpRefinePayload):
    try:
        sentence = reconstruct_sentence_from_signs(payload.signs)
        analysis = analyze_sentiment_and_urgency(payload.signs, sentence)
        
        if payload.auto_log and payload.signs:
            log_conversation(
                channel="sign_to_voice",
                input_raw=" ".join(payload.signs),
                output_text=sentence,
                sentiment=analysis["sentiment"],
                urgency=analysis["urgency"],
                urgency_score=analysis["urgency_score"]
            )
            
        return {
            "sentence": sentence,
            "sentiment": analysis["sentiment"],
            "urgency": analysis["urgency"],
            "urgency_score": analysis["urgency_score"],
            "emotion": analysis["emotion"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text_to_signs")
def convert_text_to_signs(payload: TextToSignsPayload):
    try:
        matched = text_to_signs(payload.text)
        analysis = analyze_sentiment_and_urgency([], payload.text)

        if payload.auto_log and payload.text:
            log_conversation(
                channel="voice_to_sign",
                input_raw=payload.text,
                output_text=" -> ".join([s["label"] for s in matched]) if matched else payload.text,
                sentiment=analysis["sentiment"],
                urgency=analysis["urgency"],
                urgency_score=analysis["urgency_score"]
            )

        return {
            "text": payload.text,
            "signs": matched,
            "sentiment": analysis["sentiment"],
            "urgency": analysis["urgency"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dictionary")
def get_dictionary():
    return {
        "signs": SIGN_DICTIONARY,
        "labels": GESTURE_LABELS,
        "alphabet_classes": asl_classes
    }

@app.get("/api/history")
def get_history(limit: int = 30):
    convs = get_recent_conversations(limit=limit)
    return {
        "conversations": convs
    }

@app.get("/api/analytics")
def get_analytics():
    return get_analytics_summary()
