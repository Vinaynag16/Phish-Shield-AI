import pandas as pd
import sys
import os

# This line allows us to import from the 'features' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from features.url_features import URLExtractor

def process_dataset():
    input_path = "data/processed/master_dataset.csv"
    output_path = "data/processed/featured_dataset.csv"
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run dataset_processor.py first!")
        return

    print("--- Extracting Features from Dataset ---")
    df = pd.read_csv(input_path)
    extractor = URLExtractor()

    # Apply the extractor to every URL in the dataframe
    print("Processing... this may take a minute depending on dataset size.")
    features_list = df['url'].apply(lambda x: extractor.extract_features(str(x)))
    
    # Convert list of dictionaries into a DataFrame
    features_df = pd.DataFrame(list(features_list))
    
    # Combine the features with the original labels
    final_df = pd.concat([features_df, df['label']], axis=1)
    
    # Save the new numerical dataset
    final_df.to_csv(output_path, index=False)
    print(f"Success! Featured dataset saved to: {output_path}")
    print(f"Features created: {list(features_df.columns)}")

if __name__ == "__main__":
    process_dataset()