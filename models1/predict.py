import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np

class PhishShieldInference:
    def __init__(self, model_path='models1/phishshield_lstm.h5', 
                 tokenizer_path='models1/url_tokenizer.pkl'):
        
        print("Loading Phish-Shield AI Engine...")
        # Load the model and tokenizer
        self.model = load_model(model_path)
        with open(tokenizer_path, 'rb') as f:
            self.tokenizer = pickle.load(f)
        self.max_len = 150
        
        # Simple whitelist to prevent flagging common dev tools
        self.whitelist = ["github.com", "google.com", "stackoverflow.com"]

    def predict_url(self, url):  # <--- WE NAME IT THIS
        # 1. Quick Whitelist Check
        domain = url.split("//")[-1].split("/")[0].lower()
        if any(trusted in domain for trusted in self.whitelist):
            return {"url": url, "status": "SAFE", "confidence": "100.00% (Whitelisted)"}

        # 2. Preprocess
        sequences = self.tokenizer.texts_to_sequences([url])
        padded = pad_sequences(sequences, maxlen=self.max_len)
        
        # 3. Predict
        prediction = self.model.predict(padded, verbose=0)[0][0]
        
        # 4. Format
        label = "PHISHING" if prediction > 0.5 else "SAFE"
        confidence = prediction if prediction > 0.5 else (1 - prediction)
        
        return {
            "url": url,
            "status": label,
            "confidence": f"{confidence * 100:.2f}%"
        }

if __name__ == "__main__":
    # Ensure the object name matches what you call below
    engine = PhishShieldInference()
    
    test_urls = [
        "https://www.google.com",
        "http://secure-login-update-verify.com/bank/login.php",
        "https://github.com/settings/profile"
    ]
    
    print("\n--- Live Test Results ---")
    for url in test_urls:
        # This now matches the name in the class above
        res = engine.predict_url(url) 
        print(f"[{res['status']}] ({res['confidence']}) -> {url}")