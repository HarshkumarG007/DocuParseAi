import torch
from torch.utils.data import Dataset
from PIL import Image
import json
import os

class DocumentDataset(Dataset):
    def __init__(self, data_dir: str, processor, max_length: int = 512):
        self.data_dir = data_dir
        self.processor = processor
        self.max_length = max_length
        self.image_dir = os.path.join(data_dir, "images")
        self.annotation_dir = os.path.join(data_dir, "annotations")
        
        self.samples = []
        if os.path.exists(self.annotation_dir):
            for file in os.listdir(self.annotation_dir):
                if file.endswith(".json"):
                    self.samples.append(file)
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        annotation_file = self.samples[idx]
        base_name = annotation_file.replace(".json", "")
        
        # Load image
        image_path = os.path.join(self.image_dir, base_name + ".jpg")
        image = Image.open(image_path).convert("RGB")
        
        # Load annotations
        with open(os.path.join(self.annotation_dir, annotation_file), "r", encoding="utf-8") as f:
            data = json.load(f)
            
        words = [item["word"] for item in data]
        boxes = [item["bbox"] for item in data]
        labels = [item["label"] for item in data] # integer labels
        
        encoding = self.processor(
            image,
            words,
            boxes=boxes,
            word_labels=labels,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        # Remove batch dimension
        encoding = {k: v.squeeze(0) for k, v in encoding.items()}
        return encoding
