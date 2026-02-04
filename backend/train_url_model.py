import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from feature_extractor import get_url_features

# 1. Provide your FULL absolute path
csv_path = r"C:\Users\nagav\Desktop\phish-shield-ai\notebooks\phishing_urls.csv"

print(f"Loading data from: {csv_path}")

try:
    df = pd.read_csv(csv_path)
    # Clean column names
    df.columns = df.columns.str.strip().str.lower()
    print(f"✅ Data Loaded! Columns found: {df.columns.tolist()}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# 2. MATCH THE COLUMNS TO YOUR DATA (FIXED HERE)
URL_COL = 'url'
# In your PhishTank file, 'verified' acts as our label (1 for phishing)
LABEL_COL = 'verified' 

# 3. Feature Extraction
print("Extracting URL features (this may take 1-2 minutes)...")
def extract(u):
    return list(get_url_features(str(u)).values())

X = df[URL_COL].apply(extract).tolist()
y = df[LABEL_COL]

# Convert 'yes'/'no' or strings to 1s and 0s if necessary
# PhishTank 'verified' is usually 'yes' or 1.
if y.dtype == 'object':
    y = y.map({'yes': 1, 'no': 0, 'y': 1, 'n': 0}).fillna(0)

# 4. Train the Model
print("Training the AI...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 5. Save the 'Brain'
os.makedirs('../models', exist_ok=True)
joblib.dump(model, '../models/url_model.pkl')

print(f"🎯 Done! Model Accuracy: {model.score(X_test, y_test)*100:.2f}%")
print("✅ File created: models/url_model.pkl")