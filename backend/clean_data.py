import pandas as pd
import os

def clean_phishing_data():
    # Define paths based on your file explorer structure
    base_path = "../notebooks/"
    phish_file = os.path.join(base_path, "phishing_urls.csv")
    safe_file = os.path.join(base_path, "online-valid.csv")
    
    print("📂 Loading datasets...")
    
    # 1. Load Data
    # Adjust 'url' column name if your CSV headers are different
    df_phish = pd.read_csv(phish_file)
    df_safe = pd.read_csv(safe_file)
    
    # 2. Add Labels (1 for Phishing, 0 for Safe)
    df_phish['label'] = 1
    df_safe['label'] = 0
    
    # 3. Combine into one DataFrame
    df = pd.concat([df_phish, df_safe], ignore_index=True)
    
    # 4. Remove Duplicates
    initial_count = len(df)
    df.drop_duplicates(subset=['url'], inplace=True)
    print(f"🧹 Removed {initial_count - len(df)} duplicate URLs.")
    
    # 5. Ensure 'http' prefix
    def add_prefix(url):
        if not str(url).startswith(('http://', 'https://')):
            return 'http://' + str(url)
        return str(url)
    
    df['url'] = df['url'].apply(add_prefix)
    print("🌐 Standardized all URL prefixes.")
    
    # 6. Save Cleaned Data
    output_path = os.path.join(base_path, "cleaned_dataset.csv")
    df.to_csv(output_path, index=False)
    print(f"✅ Success! Cleaned data saved to: {output_path}")

if __name__ == "__main__":
    clean_phishing_data()