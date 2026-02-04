import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

# 1. Setup paths
BASE_DIR = r"C:\Users\nagav\Desktop\phish-shield-ai"
MODEL_DIR = os.path.join(BASE_DIR, "models")

if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# 2. Create a small sample dataset (since the CSV was missing)
data = {
    'text': [
        "Your account is suspended, click here to verify",
        "Free gift card winners click now",
        "Meeting scheduled for tomorrow at 10am",
        "Please review the attached document for the project",
        "Urgent security alert: unauthorized login attempt",
        "Hello, how are you doing today?"
    ]
}
df = pd.DataFrame(data)

# 3. Create and Train the Vectorizer
# TfidfVectorizer converts text into numerical features
vectorizer = TfidfVectorizer(stop_words='english')
vectorizer.fit(df['text'])

# 4. Save the Vectorizer
vectorizer_path = os.path.join(MODEL_DIR, "vectorizer.pkl")
joblib.dump(vectorizer, vectorizer_path)

print(f"✅ Success! Generated vectorizer.pkl at: {vectorizer_path}")