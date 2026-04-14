import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_security_bot(user_message, scan_context=None):

    extra_context = ""

    if scan_context:
        extra_context = f"""
The user has recently scanned a suspicious URL.

LATEST SCAN RESULT:
Prediction: {scan_context.get("prediction")}
Score: {scan_context.get("score")}
Threat Level: {scan_context.get("threat_level")}
Detection Method: {scan_context.get("method")}
Reason: {scan_context.get("reason")}

IMPORTANT:
If the user says:
- why is this dangerous
- is this safe
- explain this
- why phishing
- tell me about this link

You MUST assume they mean the latest scan result above.
Use that data directly.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": f"""
You are PhishShield AI Security Assistant.

Only answer cybersecurity topics:
phishing, suspicious URLs, scams, malware,
online safety, password security.

Keep answers clear, short, useful.

{extra_context}
"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.3
    }

    response = requests.post(
        GROQ_URL,
        json=payload,
        headers=headers,
        timeout=30
    )

    data = response.json()

    if "choices" in data:
        return data["choices"][0]["message"]["content"]

    if "error" in data:
        return f"⚠️ Groq Error: {data['error']['message']}"

    return "⚠️ Unexpected API response."


