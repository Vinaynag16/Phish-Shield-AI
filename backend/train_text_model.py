import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# 1. Your verified absolute path
email_path = r"C:\Users\nagav\Desktop\phish-shield-ai\notebooks\phishing_email.csv"

print(f"Loading Email Data from: {email_path}")

try:
    df = pd.read_csv(email_path, encoding='latin1')
    df.columns = df.columns.str.strip().str.lower()
    print(f"✅ Data Loaded! Columns found: {df.columns.tolist()}")
except Exception as e:
    print(f"❌ Error loading file: {e}")
    exit()

# 2. MATCHED COLUMNS (Updated to text_combined)
TEXT_COL = 'text_combined' 
LABEL_COL = 'label'

# 3. Clean Data
df = df.dropna(subset=[TEXT_COL, LABEL_COL])

# 4. Build the NLP Pipeline
model = make_pipeline(
    TfidfVectorizer(stop_words='english', max_features=5000),
    MultinomialNB()
)

# 5. Train
print("Training the Email Text AI... almost done!")
X_train, X_test, y_train, y_test = train_test_split(df[TEXT_COL], df[LABEL_COL], test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# 6. Save the Brain
os.makedirs('../models', exist_ok=True)
joblib.dump(model, '../models/text_model.pkl')

print(f"🎯 Text Model Accuracy: {model.score(X_test, y_test)*100:.2f}%")
print("✅ SUCCESS: models/text_model.pkl created!")