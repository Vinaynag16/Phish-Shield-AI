import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import pickle
import os

def build_and_train_lstm():
    # 1. Load the data we created in Phase 2
    data_path = "data/processed/master_dataset.csv"
    if not os.path.exists(data_path):
        print("Error: master_dataset.csv not found!")
        return

    df = pd.read_csv(data_path)
    X = df['url'].astype(str)
    y = df['label'].values

    # 2. Tokenize the URLs (Convert characters to numbers)
    max_words = 10000 
    max_len = 150 # Max length of a URL we will analyze
    
    tokenizer = Tokenizer(num_words=max_words, char_level=True) # Learning character by character
    tokenizer.fit_on_texts(X)
    sequences = tokenizer.texts_to_sequences(X)
    X_padded = pad_sequences(sequences, maxlen=max_len)

    # 3. Split data
    X_train, X_test, y_train, y_test = train_test_split(X_padded, y, test_size=0.2, random_state=42)

    # 4. Build the LSTM Architecture
    model = Sequential([
        Embedding(max_words, 32, input_length=max_len),
        LSTM(64, dropout=0.2, recurrent_dropout=0.2),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid') # Binary classification (0 or 1)
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # 5. Train
    print("--- Starting LSTM Training ---")
    model.fit(X_train, y_train, epochs=5, batch_size=64, validation_split=0.1)

    # 6. Save Model and Tokenizer
    # We save the tokenizer so we can use the same character-mapping for predictions later
    model.save('models1/phishshield_lstm.h5')
    with open('models1/url_tokenizer.pkl', 'wb') as f:
        pickle.dump(tokenizer, f)
        
    print("\nSuccess! LSTM model saved to models1/phishshield_lstm.h5")

if __name__ == "__main__":
    build_and_train_lstm()