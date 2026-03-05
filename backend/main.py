import os
import uvicorn
import tldextract
import numpy as np
import joblib
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- NEW: Import your LSTM Engine ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models1.predict import PhishShieldInference

# --- CONFIGURATION ---
app = FastAPI(title="Phish-Shield AI Engine (v2.0)")
BASE_DIR = r"C:\Users\nagav\Desktop\phishing project"
MODEL_DIR = os.path.join(BASE_DIR, "models")
WHITELIST_PATH = os.path.join(BASE_DIR, "backend", "whitelist.txt")

# --- ENGINE INITIALIZATION ---
text_model = joblib.load(os.path.join(MODEL_DIR, "text_model.pkl"))
url_engine = PhishShieldInference(
    model_path=os.path.join(BASE_DIR, 'models1', 'phishshield_lstm.h5'),
    tokenizer_path=os.path.join(BASE_DIR, 'models1', 'url_tokenizer.pkl')
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
            # Read lines, strip whitespace, and ignore empty lines
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
    
    # 1. Check Whitelist First
    if is_whitelisted(url_to_test):
        return {
            "prediction": "safe",
            "score": "100%",
            "threat_level": "Low",
            "method": "🛡️ Whitelist Verified",
            "reason": "🟢 Verified Trusted Domain: This site is recognized as safe."
        }

    # 2. Run AI Engine if not whitelisted
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