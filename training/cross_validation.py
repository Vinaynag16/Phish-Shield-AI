import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys

print("CHECK: Script started...")

try:
    import pandas as pd
    import numpy as np
    import pickle
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Embedding, LSTM, Dense
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    print("CHECK: Imports successful...")
except ImportError as e:
    print(f"ERROR: Missing library: {e}")
    sys.exit()

def run_cross_val():
    # 1. Check if files exist
    data_path = "data/processed/master_dataset.csv"
    tok_path = "models1/url_tokenizer.pkl"
    
    if not os.path.exists(data_path):
        print(f"ERROR: Cannot find data at {data_path}")
        return
    if not os.path.exists(tok_path):
        print(f"ERROR: Cannot find tokenizer at {tok_path}")
        return
    
    print("CHECK: Files found. Loading data...")
    df = pd.read_csv(data_path).head(1000) # Tiny sample for testing
    
    X_text = df['url'].astype(str)
    y = df['label'].values

    with open(tok_path, 'rb') as f:
        tokenizer = pickle.load(f)
    
    print("CHECK: Data loaded. Starting sequences...")
    X_seq = pad_sequences(tokenizer.texts_to_sequences(X_text), maxlen=150)

    print("CHECK: Initializing Model...")
    model = Sequential([
        Embedding(10000, 32),
        LSTM(32),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    print("CHECK: Starting training loop...")
    # Just train 1 epoch on 1 fold to see if it works
    model.fit(X_seq, y, epochs=1, batch_size=32, verbose=1)
    print("CHECK: Training finished successfully!")

if __name__ == "__main__":
    run_cross_val()