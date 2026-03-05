import pandas as pd
import requests
import os

class PhishDataProcessor:
    def __init__(self):
        self.raw_path = "data/raw/"
        self.processed_path = "data/processed/"
        
        # Publicly accessible CSV/Text versions of these datasets
        self.urls = {
            "phishtank": "https://raw.githubusercontent.com/arvindeybram/phishing/master/phishtank.csv",
            "openphish": "https://openphish.com/feed.txt"
        }

    def download_datasets(self):
        print("--- Downloading Datasets ---")
        # PhishTank
        print("Fetching PhishTank...")
        r = requests.get(self.urls["phishtank"])
        with open(f"{self.raw_path}phishtank.csv", 'wb') as f:
            f.write(r.content)
            
        # OpenPhish
        print("Fetching OpenPhish...")
        r = requests.get(self.urls["openphish"])
        with open(f"{self.raw_path}openphish.txt", 'wb') as f:
            f.write(r.content)
        print("Download Complete.\n")

    def clean_and_merge(self):
        print("--- Cleaning and Merging ---")
        
        # Load PhishTank (URL, Label 1)
        df_pt = pd.read_csv(f"{self.raw_path}phishtank.csv")
        df_pt = df_pt[['url']].copy()
        df_pt['label'] = 1
        df_pt['source'] = 'phishtank'

        # Load OpenPhish (URL, Label 1)
        with open(f"{self.raw_path}openphish.txt", 'r') as f:
            openphish_urls = f.read().splitlines()
        df_op = pd.DataFrame(openphish_urls, columns=['url'])
        df_op['label'] = 1
        df_op['source'] = 'openphish'

        # Merging Phishing URLs
        phish_df = pd.concat([df_pt, df_op]).drop_duplicates(subset='url')

        # FOR LEGITIMATE DATA (Simulated for this step - Enron/SpamAssassin integration)
        # Note: In a real environment, you'd download the 1.7GB Enron file. 
        # For our starter pipeline, we'll create a placeholder for 'safe' URLs 
        # to ensure the model has '0' labels to learn from.
        legit_urls = [
            "https://www.google.com", "https://www.github.com", "https://www.microsoft.com",
            "https://www.apple.com", "https://www.wikipedia.org", "https://www.amazon.com"
        ] * 1000 # Artificial boost for demo
        legit_df = pd.DataFrame(legit_urls, columns=['url'])
        legit_df['label'] = 0
        legit_df['source'] = 'legit_source'

        # Final Combined Dataset
        master_df = pd.concat([phish_df, legit_df])
        
        # Shuffle
        master_df = master_df.sample(frac=1).reset_index(drop=True)
        
        # Save
        save_path = f"{self.processed_path}master_dataset.csv"
        master_df.to_csv(save_path, index=False)
        print(f"Master Dataset created at: {save_path}")
        print(f"Total records: {len(master_df)}")
        print(f"Phishing: {len(master_df[master_df['label']==1])}")
        print(f"Legitimate: {len(master_df[master_df['label']==0])}")

if __name__ == "__main__":
    processor = PhishDataProcessor()
    processor.download_datasets()
    processor.clean_and_merge()