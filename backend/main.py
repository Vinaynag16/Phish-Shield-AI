import os
import uvicorn
import tldextract
import numpy as np
import joblib
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- DYNAMIC PATHING (Replaces Hardcoded C:\...) ---
# This finds the root directory of your project automatically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- NEW: Import your LSTM Engine ---
# Add the project root to the system path for local imports
sys.path.append(BASE_DIR)
from models1.predict import PhishShieldInference

# --- CONFIGURATION ---
app = FastAPI(title="Phish-Shield AI Engine (v2.0)")

# Define paths relative to the BASE_DIR
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODELS1_DIR = os.path.join(BASE_DIR, "models1")
WHITELIST_PATH = os.path.join(BASE_DIR, "backend", "whitelist.txt")

# --- ENGINE INITIALIZATION ---
# Load models using the dynamic paths
text_model = joblib.load(os.path.join(MODEL_DIR, "text_model.pkl"))
url_engine = PhishShieldInference(
    model_path=os.path.join(MODELS1_DIR, 'phishshield_lstm.h5'),
    tokenizer_path=os.path.join(MODELS1_DIR, 'url_tokenizer.pkl')
)

class URLInput(BaseModel): url: str
class TextInput(BaseModel): text: str

# --- HELPER: Whitelist Loader ---
def is_whitelisted(url):
    """Checks if the domain or URL exists in whitelist.txt"""
    try:
        if not os.path.exists(WHITELIST_PATH):
            return False
            
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        
        with open(WHITELIST_PATH, "r") as f:
            whitelist = [line.strip().lower() for line in f if line.strip()]
            
        return any(item in url.lower() or item == domain for item in whitelist)
    except Exception as e:
        print(f"Whitelist Error: {e}")
        return False

# --- HELPER: Threat Level Logic ---
def get_threat_metadata(confidence_str, is_phishing):
    try:
        score = float(str(confidence_str).replace('%', ''))
    except:
        score = 0.0

    if not is_phishing:
        return "Low", "🟢 Safe: Minimal risk detected."
    
    if score > 90:
        return "High", "🔴 Critical: Highly malicious patterns found."
    elif score > 70:
        return "Medium", "🟠 Warning: Suspicious elements. Investigation advised."
    else:
        return "Low", "🟡 Caution: Unusual structure, but low confidence."

# --- URL ANALYZER ---
@app.post("/predict/url")
async def predict_url(data: URLInput):
    url_to_test = data.url.lower().strip()
    
    if is_whitelisted(url_to_test):
        return {
            "prediction": "safe",
            "score": "100%",
            "threat_level": "Low",
            "method": "🛡️ Whitelist Verified",
            "reason": "🟢 Verified Trusted Domain: This site is recognized as safe."
        }

    try:
        result = url_engine.predict_url(url_to_test)
        is_phish = result["status"] == "PHISHING"
        level, advice = get_threat_metadata(result["confidence"], is_phish)
        
        return {
            "prediction": result["status"].lower(),
            "score": result["confidence"],
            "threat_level": level,
            "method": "🧠 Deep Learning (LSTM)",
            "reason": advice
        }
    except Exception as e:
        return {"prediction": "Error", "reason": f"❌ Analysis failed: {e}"}

# --- TEXT ANALYZER ---
@app.post("/predict/text")
async def predict_text(data: TextInput):
    try:
        prediction = text_model.predict([data.text])[0]
        prob = text_model.predict_proba([data.text])[0]
        confidence = round(np.max(prob) * 100, 2)
        
        is_phish = (prediction == 1)
        level, advice = get_threat_metadata(confidence, is_phish)
        
        return {
            "prediction": "phishing" if is_phish else "safe",
            "score": f"{confidence}%",
            "threat_level": level,
            "method": "🧠 NLP Neural Engine",
            "reason": advice
        }
    except Exception:
        return {"prediction": "Error", "reason": "⚠️ NLP Engine error."}

# --- MIDDLEWARE (Updated for security) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # 0.0.0.0 is critical for Docker and Dev Tunnel access
    uvicorn.run(app, host="0.0.0.0", port=8000)