import pandas as pd

# Path to your file
file_path = "notebooks/phishing_urls.csv"

try:
    df = pd.read_csv(r"C:\Users\nagav\Desktop\phish-shield-ai\notebooks\phishing_urls.csv")
    print("--- DATASET DIAGNOSTIC ---")
    print(f"Total Rows: {len(df)}")
    print(f"Actual Column Names: {df.columns.tolist()}")
    print("\nFirst 3 rows of data:")
    print(df.head(3))
except Exception as e:
    print(f"Could not read the file: {e}")