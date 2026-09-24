import os
import json

def setup_dataset_structure():
    """Sets up the required directories for SROIE and CORD datasets."""
    print("Initializing dataset directories...")
    dirs = [
        "data/raw/sroie/images",
        "data/raw/sroie/annotations",
        "data/raw/cord/images",
        "data/raw/cord/annotations",
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created {d}")
        
    print("\nDataset structure ready.")
    print("Note: Full download of SROIE and CORD datasets requires manual Kaggle or HuggingFace API access.")
    print("Please place image files (.jpg) in the 'images' folder and annotation files (.json/.txt) in the 'annotations' folder.")

if __name__ == "__main__":
    setup_dataset_structure()
