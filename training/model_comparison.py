import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import accuracy_score, f1_score
import pickle

def compare_models():
    print("--- Starting Model Comparison Leaderboard ---")
    
    # 1. Load Data
    data_path = "data/processed/master_dataset.csv"
    df = pd.read_csv(data_path)
    X_raw = df['url'].astype(str)
    y_true = df['label'].values

    # 2. Prepare Data (Tokenization)
    with open('models1/url_tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    X_seq = pad_sequences(tokenizer.texts_to_sequences(X_raw), maxlen=150)

    # 3. List of models to compare
    # Make sure you have run cnn_detector.py to generate the .h5 file!
    model_files = {
        "LSTM Network": "models1/phishshield_lstm.h5",
        "CNN Network": "models1/phishshield_cnn.h5"
    }

    results = []

    for name, path in model_files.items():
        if not os.path.exists(path):
            print(f"Skipping {name}: File not found at {path}")
            continue
            
        print(f"Evaluating {name}...")
        model = load_model(path)
        
        # Predict
        y_prob = model.predict(X_seq, verbose=0)
        y_pred = (y_prob > 0.5).astype(int)
        
        # Metrics
        acc = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        
        results.append({"Model": name, "Accuracy": f"{acc:.4f}", "F1-Score": f"{f1:.4f}"})

    # 4. Display Leaderboard
    leaderboard = pd.DataFrame(results)
    print("\n" + "="*40)
    print("      PHISH-SHIELD AI LEADERBOARD")
    print("="*40)
    print(leaderboard.to_string(index=False))
    print("="*40)

if __name__ == "__main__":
    compare_models()