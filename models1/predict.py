import os
import pickle
import numpy as np

# Suppress log noise
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.sequence import pad_sequences

class PhishShieldInference:
    def __init__(self, model_path='models1/phishshield_lstm.h5', 
                 tokenizer_path='models1/url_tokenizer.pkl'):
        
        print("Loading Phish-Shield AI Engine (Manual Mode)...")
        
        # 1. Define the architecture manually
        # This bypasses the need for Keras to 'guess' the config from the file
        self.model = Sequential([
            Input(shape=(150,)),
            Embedding(input_dim=10000, output_dim=32),
            LSTM(64, dropout=0.2, recurrent_dropout=0.2),
            Dense(32, activation='relu'),
            Dropout(0.3),
            Dense(1, activation='sigmoid')
        ])
        
        # 2. Load the weights into the architecture we just built
        # This is much more stable than load_model() across different versions
        self.model.load_weights(model_path)
        
        with open(tokenizer_path, 'rb') as f:
            self.tokenizer = pickle.load(f)
            
        self.max_len = 150
        self.whitelist = ["github.com", "google.com", "stackoverflow.com"]

    def predict_url(self, url):
        # Preprocess
        sequences = self.tokenizer.texts_to_sequences([url])
        padded = pad_sequences(sequences, maxlen=self.max_len)
        
        # Predict
        prediction = self.model.predict(padded, verbose=0)[0][0]
        
        # Format
        label = "PHISHING" if prediction > 0.5 else "SAFE"
        confidence = prediction if prediction > 0.5 else (1 - prediction)
        
        return {
            "status": label, 
            "confidence": f"{confidence * 100:.2f}%"
        }