import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

def tune_lstm():
    # 1. Load Data
    df = pd.read_csv("data/processed/master_dataset.csv")
    X = df['url'].astype(str)
    y = df['label'].values

    # 2. Preprocess
    max_words, max_len = 10000, 150
    with open('models1/url_tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    sequences = tokenizer.texts_to_sequences(X)
    X_padded = pad_sequences(sequences, maxlen=max_len)
    X_train, X_test, y_train, y_test = train_test_split(X_padded, y, test_size=0.2)

    # 3. Tuning Parameters to Test
    neuron_options = [32, 64]
    dropout_options = [0.2, 0.4]
    
    results = []

    print("--- Starting Hyperparameter Tuning ---")
    for neurons in neuron_options:
        for dropout in dropout_options:
            print(f"Testing: Neurons={neurons}, Dropout={dropout}")
            
            model = Sequential([
                Embedding(max_words, 32),
                LSTM(neurons),
                Dropout(dropout),
                Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            
            # Train for just 2 epochs to save time during tuning
            history = model.fit(X_train, y_train, epochs=2, batch_size=128, validation_split=0.1, verbose=0)
            val_acc = max(history.history['val_accuracy'])
            
            results.append({'neurons': neurons, 'dropout': dropout, 'val_accuracy': val_acc})
            print(f"Result: Val Accuracy = {val_acc:.4f}")

    # 4. Show Best Result
    tuning_df = pd.DataFrame(results)
    best = tuning_df.loc[tuning_df['val_accuracy'].idxmax()]
    print("\n--- Best Configuration Found ---")
    print(best)

if __name__ == "__main__":
    tune_lstm()