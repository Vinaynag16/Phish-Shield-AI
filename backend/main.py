import os
import uvicorn
import tldextract
import numpy as np
import joblib
import sys
import whois
import re
from chatbot import ask_security_bot
from pydantic import BaseModel 
from typing import Optional
from datetime import datetime, UTC
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, log_scan, get_stats

# --- IMPORT LSTM ENGINE ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models1.predict import PhishShieldInference


# ---------------- CONFIG ----------------
app = FastAPI(title="Phish-Shield AI Engine v2.0")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))     # backend folder
BASE_DIR = os.path.dirname(CURRENT_DIR)
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL1_DIR = os.path.join(BASE_DIR, "models1")
WHITELIST_PATH = os.path.join(BASE_DIR, "backend", "whitelist.txt")


# ---------------- LOAD MODELS ----------------
text_model = joblib.load(os.path.join(MODEL_DIR, "text_model.pkl"))

url_engine = PhishShieldInference(
    model_path=os.path.join(MODEL1_DIR, "phishshield_lstm.h5"),
    tokenizer_path=os.path.join(MODEL1_DIR, "url_tokenizer.pkl")
)

# ---------------- DATABASE ----------------
init_db()


# ---------------- INPUT MODELS ----------------
class URLInput(BaseModel):
    url: str
class ChatInput(BaseModel):
    message: str
    scan_context: Optional[dict] = None
class TextInput(BaseModel):
    text: str


# ---------------- WHITELIST ----------------
def is_whitelisted(url):
    try:
        if not os.path.exists(WHITELIST_PATH):
            return False

        url = url.lower().strip()

        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        ext = tldextract.extract(url)
        domain = f"{ext.domain}.{ext.suffix}"

        whitelist = []
        skipped = 0

        with open(WHITELIST_PATH, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    skipped += 1
                    continue
                parts = line.split(",", 1)
                if len(parts) == 2:
                    whitelist.append(parts[1].lower())
                else:
                    skipped += 1
                    print(f"WHITELIST WARN: line {line_num} malformed ({len(parts)} fields): {line[:80]}")

        print(f"Whitelist loaded: {len(whitelist)} domains, skipped {skipped} malformed lines")
        return domain in whitelist

    except Exception as e:
        print("Whitelist Error:", e)
        return False


# ---------------- THREAT LOGIC ----------------
def get_threat_metadata(confidence, is_phishing):

    try:
        score = float(str(confidence).replace("%", ""))
    except:
        score = 0

    if not is_phishing:
        return "Low", "🟢 Safe: Minimal risk detected."

    if score > 90:
        return "High", "🔴 Critical: Highly malicious patterns found."
    elif score > 70:
        return "Medium", "🟠 Warning: Suspicious elements detected."
    else:
        return "Low", "🟡 Low confidence phishing detection."


# ---------------- TYPOSQUATTING ----------------
def check_typosquatting(url):

    ext = tldextract.extract(url)
    domain = ext.domain.lower()

    visual_swaps = [
        ("0", "o"),
        ("1", "l"),
        ("rn", "m"),
        ("vv", "w")
    ]

    normalized = domain

    for pattern, repl in visual_swaps:
        normalized = normalized.replace(pattern, repl)

    brands = [
        "google", "paypal", "amazon",
        "apple", "microsoft", "onedrive", "live"
    ]

    if normalized in brands and domain not in brands:
        return True

    if "-" in domain and any(b in domain for b in brands):
        return True

    return False


# ---------------- SUSPICIOUS TLD ----------------
def suspicious_tld(domain):

    risky_tlds = [
        "xyz", "top", "site", "online",
        "store", "live", "info", "club"
    ]

    ext = tldextract.extract(domain)
    return ext.suffix in risky_tlds


# ---------------- SUBDOMAIN ABUSE ----------------
def excessive_subdomains(url):

    ext = tldextract.extract(url)

    if not ext.subdomain:
        return False

    subdomains = ext.subdomain.split(".")
    return len(subdomains) >= 3


# ---------------- URL ANALYZER ----------------
@app.post("/predict/url")
async def predict_url(data: URLInput):

    url_to_test = data.url.lower().strip()

    is_white = is_whitelisted(url_to_test)

    # -------- TYPOSQUATTING --------
    if check_typosquatting(url_to_test):
        return {
            "prediction": "phishing",
            "score": "98%",
            "threat_level": "High",
            "method": "⚠️ Heuristic Guard",
            "reason": "🔴 Brand impersonation detected"
        }

    # -------- WHOIS LOOKUP --------
    try:

        ext = tldextract.extract(url_to_test)
        domain = f"{ext.domain}.{ext.suffix}"

        w = whois.whois(domain)

        creation = w.creation_date
        expiry = w.expiration_date

        if isinstance(creation, list):
            creation = creation[0]

        if isinstance(expiry, list):
            expiry = expiry[0]

        domain_age = "Unknown"

        if creation:

            if hasattr(creation, "tzinfo") and creation.tzinfo is not None:
                creation = creation.replace(tzinfo=None)

            today = datetime.now(UTC).replace(tzinfo=None)

            age_days = (today - creation).days

            if age_days < 30:
                domain_age = f"{age_days} days ⚠️ (Very New Domain)"
            elif age_days < 180:
                domain_age = f"{age_days} days (Recently Registered)"
            else:
                domain_age = f"{age_days} days"

        whois_data = {
            "registrar": w.registrar or "Unknown",
            "creation_date": str(creation) if creation else "Unknown",
            "expiry_date": str(expiry) if expiry else "Unknown",
            "domain_age": domain_age,
            "raw_text": str(w)[:800]
        }

    except Exception:

        whois_data = {
            "registrar": "Hidden/Unknown ⚠️",
            "creation_date": "Unavailable",
            "expiry_date": "Unavailable",
            "domain_age": "Unavailable ⚠️ (Possible phishing or new domain)",
            "raw_text": "Domain registry information is hidden or unavailable."
        }

    # -------- SUBDOMAIN SIGNAL --------
    subdomain_flag = ""

    if excessive_subdomains(url_to_test):
        subdomain_flag = "⚠️ Excessive subdomains detected"

    # -------- AI MODEL / WHITELIST --------
    if is_white:

        result = {
            "status": "SAFE",
            "confidence": "100%"
        }

        is_phish = False

    else:

        result = url_engine.predict_url(url_to_test)

        is_phish = result["status"] == "PHISHING"

    level, advice = get_threat_metadata(result["confidence"], is_phish)

    # -------- TLD SIGNAL --------
    tld_flag = ""

    if suspicious_tld(url_to_test):
        print("⚠️ Suspicious TLD detected")
        tld_flag = "⚠️ Suspicious TLD detected"

    prediction_str = result["status"].lower()
    log_scan("url", url_to_test, prediction_str, level, result["confidence"])

    return {
        "prediction": result["status"].lower(),
        "score": result["confidence"],
        "threat_level": level,
        "method": "🛡️ Whitelist Verified" if is_white else "🧠 Deep Learning (LSTM)",
        "reason": advice,
        "tld_warning": tld_flag,
        "subdomain_warning": subdomain_flag,
        "whois": whois_data
    }


# ---------------- TEXT ANALYZER ----------------
@app.post("/predict/text")
async def predict_text(data: TextInput):
    try:
        user_text = data.text.strip()

        if not user_text:
            return {
                "prediction": "Error",
                "reason": "Empty input text"
            }

        prediction = text_model.predict([user_text])[0]

        if hasattr(text_model, "predict_proba"):
            prob = text_model.predict_proba([user_text])[0]
            confidence = round(np.max(prob) * 100, 2)
        else:
            confidence = 85.0

        is_phish = prediction == 1
        level, advice = get_threat_metadata(confidence, is_phish)

        pred_str = "phishing" if is_phish else "safe"
        log_scan("text", user_text[:200], pred_str, level, f"{confidence}%")

        return {
            "prediction": "phishing" if is_phish else "safe",
            "score": f"{confidence}%",
            "threat_level": level,
            "method": "🧠 NLP Engine",
            "reason": advice
        }

    except Exception as e:
        return {
            "prediction": "Error",
            "reason": str(e)
        }
#----------------- CHATBOT ----------------
@app.post("/chat")
async def chat_ai(data: ChatInput):
    try:
        reply = ask_security_bot(data.message,data.scan_context)
        return {"reply": reply}
    except Exception as e:
        print("CHATBOT ERROR:", e)
        return {"reply": f"⚠️ Backend error: {str(e)}"}


# ---------------- STATS ----------------
@app.get("/stats")
async def stats():
    return get_stats()


# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)