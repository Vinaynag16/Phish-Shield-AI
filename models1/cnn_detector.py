import pandas as pd
import numpy as np
import pickle
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

def train_cnn():
    print("--- Starting CNN Model Training ---")
    
    # 1. Load Processed Data
    data_path = "data/processed/master_dataset.csv"
    if not os.path.exists(data_path):
        print("Error: processed dataset not found!")
        return

    df = pd.read_csv(data_path)
    X = df['url'].astype(str)
    y = df['label'].values

    # 2. Tokenization & Padding
    with open('models1/url_tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    
    sequences = tokenizer.texts_to_sequences(X)
    X_padded = pad_sequences(sequences, maxlen=150)
    
    X_train, X_test, y_train, y_test = train_test_split(X_padded, y, test_size=0.2, random_state=42)

    # 3. Build CNN Architecture
    # CNNs are great at detecting 'keywords' or 'patterns' in URLs
    model = Sequential([
        Embedding(input_dim=10000, output_dim=32),
        Conv1D(filters=64, kernel_size=3, activation='relu'),
        GlobalMaxPooling1D(),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # 4. Train
    print("Training CNN... this is usually faster than LSTM.")
    model.fit(X_train, y_train, epochs=3, batch_size=64, validation_split=0.1)

    # 5. Save
    model_path = 'models1/phishshield_cnn.h5'
    model.save(model_path)
    print(f"CNN Model saved successfully to: {model_path}")

if __name__ == "__main__":
    train_cnn()