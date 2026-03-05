import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Hide all TF warnings
import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # CRITICAL: Fixes the hanging issue on Windows
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

def evaluate_model(model_path, tokenizer_path, data_path):
    print(f"--- Loading Model: {os.path.basename(model_path)} ---")
    
    # 1. Load Data
    df = pd.read_csv(data_path)
    X = df['url'].astype(str)
    y_true = df['label'].values
    print(f"Loaded {len(df)} samples.")

    # 2. Process Data
    with open(tokenizer_path, 'rb') as f:
        tokenizer = pickle.load(f)
    
    X_padded = pad_sequences(tokenizer.texts_to_sequences(X), maxlen=150)

    # 3. Predict
    print("Running predictions... please wait...")
    model = load_model(model_path)
    y_pred_prob = model.predict(X_padded, verbose=0)
    y_pred = (y_pred_prob > 0.5).astype(int)

    # 4. Generate Reports
    print("\n" + "="*30)
    print("FINAL CLASSIFICATION REPORT")
    print("="*30)
    print(classification_report(y_true, y_pred, target_names=['Legitimate', 'Phishing']))

    # 5. Save Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix: {os.path.basename(model_path)}')
    
    output_img = f"training/report_visual.png"
    plt.savefig(output_img)
    print(f"Report image saved as: {output_img}")
    print("Pipeline Complete!")

if __name__ == "__main__":
    evaluate_model(
        model_path='models1/phishshield_lstm.h5',
        tokenizer_path='models1/url_tokenizer.pkl',
        data_path='data/processed/master_dataset.csv'
    )