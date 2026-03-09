# 🛡️ Phish-Shield AI v2.0

### Hybrid Deep Learning & Deterministic Phishing Defense Platform

Phish-Shield AI is an enterprise-grade cybersecurity stack designed to neutralize phishing threats in real-time. Moving beyond traditional machine learning, version 2.0 implements a **Long Short-Term Memory (LSTM) Neural Network** for sequence-based URL analysis and a **Deterministic Whitelist Layer** for zero-latency verification of global infrastructure.

---

## 🚀 Enterprise Features

- **🧠 LSTM Neural Engine:** Analyzes URLs as character-level time-series data to detect sophisticated "look-alike" domains and zero-day phishing patterns.
- **🛡️ Hybrid Whitelist Layer:** A pre-inference filter cross-referencing **1,000,000+ verified domains** to ensure 100% accuracy for trusted global services.
- **📡 Live Threat Intelligence:** Integrated **NewsData.io API** feed providing real-time global hacking alerts and cybersecurity news directly on the dashboard.
- **⚡ FastAPI High-Performance Backend:** Sub-50ms inference latency for seamless user experience.
- **📊 SOC-Style Analytics:** Responsive dashboard featuring real-time accuracy metrics and a persistent scan history ledger.

---

## 🏗️ System Architecture

Phish-Shield AI follows a **Layered Defense-in-Depth** model:

1.  **Ingestion:** User submits URL/Text via the frontend interface.
2.  **Static Layer:** `tldextract` processes the URL for a match in the `whitelist.txt` database.
3.  **Neural Layer:** If unknown, the **LSTM Model** (`phishshield_lstm.h5`) performs deep sequence inference.
4.  **NLP Layer:** Textual content is analyzed via an **NLP Neural Engine** for social engineering triggers.
5.  **Verdict:** Results are mapped to High/Medium/Low threat levels with actionable security advice.

---

## 🛠️ Tech Stack

### **Backend & AI**

- **Python / FastAPI:** High-performance asynchronous API for threat detection.
- **TensorFlow / Keras:** Powers the **LSTM** deep learning architecture for URL sequence analysis.
- **Scikit-Learn / Joblib:** Used for the NLP text classification engine and feature extraction.
- **TLDExtract:** Precise domain and suffix parsing for the deterministic whitelisting layer.

### **Frontend & Intel**

- **Vanilla JS / CSS3:** Custom-built SOC-style dark theme dashboard.
- **NewsData.io API:** Powers the global threat intelligence feed with live alerts.
- **FontAwesome:** Professional security iconography and UI feedback.

---

## 📁 Project Structure

````text
Phish-Shield-AI/
├── frontend/             # Dashboard, Scanner, Features, and Docs
│   ├── js/               # script.js (Scanner) & news.js (Intel Feed)
│   ├── css/              # Professional Dark-Theme Styles
│   ├── index.html        # Main Dashboard & Threat Intel
│   └── scanner.html      # AI Analysis Interface
├── backend/              # FastAPI Server Logic
│   ├── main.py           # API Endpoints & Logic
│   └── whitelist.txt     # 1M+ Trusted Domain Database
├── models1/              # Deep Learning LSTM Model & Tokenizers
├── models/               # NLP Text Models (joblib)
├── notebooks/            # Research, EDA, and Model Training logs
└── requirements.txt      # Python dependencies
````
---
## ⚙️ Quick Start

1. Initialize Backend
```bash
# Install required dependencies
pip install -r requirements.txt
````

## Start the FastAPI server

```bash
cd backend
python main.py
```

2. Launch Dashboard

Simply open frontend/index.html in your browser.
Ensure the API_BASE in your JavaScript points to your running backend

```bash
(default: http://localhost:8000).
```

## 📊 Model Training & Research

The notebooks/ directory contains the complete lifecycle of the project:

Data Cleaning:
Handling imbalanced datasets of malicious vs. benign URLs.

EDA:
Visualizing character distribution and domain entropy.

Training:
Comparative analysis between Random Forest and LSTM architectures.

## 🔐 Security Engineering Highlight

This project demonstrates the transition from Traditional ML (Random Forest)
to Deep Learning (LSTM).

By treating URLs as character sequences rather than static word counts,
Phish-Shield AI can identify malicious patterns in obfuscated URLs.

Example:

```bash
paypa1-security-update.com
vs
paypal.com
```

These attacks often bypass traditional filters but can be detected through
sequence-based neural analysis.

## 👨‍💻 Developed By

Vinay Nag
Software Developer | Cybersecurity Enthusiast
Focus: AI-Driven Threat Detection & SOC Automation

# ⭐ If you find this architecture interesting, please consider starring the repository!




