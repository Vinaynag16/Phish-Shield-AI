import os
import shutil
import pickle
from tensorflow.keras.models import load_model

def export_final_assets():
    print("--- Exporting Best Model for Production ---")
    
    # Define paths
    source_model = 'models1/phishshield_lstm.h5'
    source_tokenizer = 'models1/url_tokenizer.pkl'
    
    target_dir = 'models1/production/'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 1. Verify sources exist
    if not os.path.exists(source_model) or not os.path.exists(source_tokenizer):
        print("Error: Training files not found. Ensure Phase 4 and 6 are complete.")
        return

    # 2. Copy the best model to production folder
    # We use .keras format for better compatibility with modern TensorFlow
    model = load_model(source_model)
    model.save(f"{target_dir}final_phish_model.keras")
    
    # 3. Copy the tokenizer
    shutil.copy(source_tokenizer, f"{target_dir}final_tokenizer.pkl")

    print(f"\nSuccess! Production assets saved to: {target_dir}")
    print("Files ready for backend integration:")
    print(f" - {target_dir}final_phish_model.keras (The Brain)")
    print(f" - {target_dir}final_tokenizer.pkl (The Translator)")

if __name__ == "__main__":
    export_final_assets()