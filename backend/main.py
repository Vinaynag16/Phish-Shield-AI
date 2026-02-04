import os
import pandas as pd
import time
import joblib
import uvicorn
import tldextract
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from feature_extractor import get_url_features

# --- CONFIGURATION ---
app = FastAPI(title="Phish-Shield AI Engine")
BASE_DIR = r"C:\Users\nagav\Desktop\phish-shield-ai"
MODEL_DIR = os.path.join(BASE_DIR, "models")
WHITELIST_PATH = os.path.join(BASE_DIR, "backend", "whitelist.txt")

# --- MODEL LOADING ---
# Load models once at startup. We assume text_model is a Pipeline.
url_model = joblib.load(os.path.join(MODEL_DIR, "url_model.pkl"))
text_model = joblib.load(os.path.join(MODEL_DIR, "text_model.pkl"))

def load_whitelist():
    trusted = {"google.com", "github.com", "microsoft.com", "apple.com", "linkedin.com"}
    if os.path.exists(WHITELIST_PATH):
        try:
            with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    domain = line.strip().lower()
                    if domain:
                        if "," in domain: domain = domain.split(",")[-1]
                        trusted.add(domain)
        except Exception: pass
    return trusted

SAFE_DOMAINS = load_whitelist()

class URLInput(BaseModel): url: str
class TextInput(BaseModel): text: str

# --- URL ANALYZER ---
@app.post("/predict/url")
async def predict_url(data: URLInput):
    url_to_test = data.url.lower().strip()
    ext = tldextract.extract(url_to_test)
    main_domain = f"{ext.domain}.{ext.suffix}".lower()

    # 1. IMMEDIATE BRAND BYPASS (Emojis + No AI needed)
    if main_domain in SAFE_DOMAINS or any(d in url_to_test for d in ["google.com", "github.com"]):
        return {
            "prediction": "Safe",
            "score": 0.0,
            "method": "🌐 Domain Reputation",
            "reason": "✅ Verified trusted domain. This site is globally recognized as safe."
        }

    # 2. AI DEEP SCAN
    try:
        # Extract features and predict
        features = list(get_url_features(url_to_test).values())
        prediction = url_model.predict([features])[0]
        
        # Calculate Confidence Score
        prob = url_model.predict_proba([features])[0]
        confidence = round(np.max(prob) * 100, 2)
        
        if prediction == 1:
            return {
                "prediction": "phishing",
                "score": confidence,
                "method": "🤖 Random Forest AI",
                "reason": f"🚨 High Risk! AI is {confidence}% confident this structure is malicious."
            }
        else:
            return {
                "prediction": "Safe",
                "score": confidence,
                "method": "🤖 Random Forest AI",
                "reason": f"🛡️ AI is {confidence}% confident this URL pattern is legitimate."
            }
    except Exception:
        return {"prediction": "Error", "reason": "❌ Analysis failed.", "method": "System"}

# --- TEXT ANALYZER ---
@app.post("/predict/text")
async def predict_text(data: TextInput):
    try:
        # Direct prediction via Pipeline
        prediction = text_model.predict([data.text])[0]
        prob = text_model.predict_proba([data.text])[0]
        confidence = round(np.max(prob) * 100, 2)
        
        verdict = "phishing" if prediction == 1 else "Safe"
        emoji = "🚩" if prediction == 1 else "✨"
        
        return {
            "prediction": verdict,
            "score": confidence,
            "method": "🧠 NLP Neural Engine",
            "reason": f"{emoji} AI is {confidence}% confident this message is {verdict}."
        }
    except Exception:
        return {"prediction": "Error", "reason": "⚠️ NLP Engine error."}

origins = [
    "http://127.0.0.1:5500", # Common for VS Code Live Server
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "*"                      # The "Open Door" (Use only for testing)
]
# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)