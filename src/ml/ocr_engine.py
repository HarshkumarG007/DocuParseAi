import pytesseract
from PIL import Image
import os
import pandas as pd
from typing import List, Dict

# Set Tesseract path if provided in environment
if os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")

def normalize_bbox(bbox: List[int], width: int, height: int) -> List[int]:
    """Normalize bounding box to [0, 1000] scale for LayoutLMv3."""
    return [
        int(1000 * (bbox[0] / width)),
        int(1000 * (bbox[1] / height)),
        int(1000 * (bbox[2] / width)),
        int(1000 * (bbox[3] / height)),
    ]

def extract_tokens_and_boxes(image_path: str) -> List[Dict]:
    """Run Tesseract OCR and extract word tokens with normalized bounding boxes."""
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Failed to open image {image_path}: {e}")
        
    width, height = img.size
    
    # Run OCR with data output
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME)
    
    # Filter out empty words and nan
    ocr_data = ocr_data[ocr_data.conf != -1]
    ocr_data = ocr_data.dropna(subset=['text'])
    ocr_data = ocr_data[ocr_data.text.str.strip() != '']
    
    tokens = []
    for _, row in ocr_data.iterrows():
        text = str(row['text']).strip()
        if not text:
            continue
            
        x0, y0 = row['left'], row['top']
        x1, y1 = x0 + row['width'], y0 + row['height']
        
        # Ensure boxes are within image bounds
        x1 = min(x1, width)
        y1 = min(y1, height)
        
        norm_bbox = normalize_bbox([x0, y0, x1, y1], width, height)
        
        tokens.append({
            "word": text,
            "bbox": norm_bbox,
            "raw_bbox": [x0, y0, x1, y1],
            "confidence": float(row['conf']) / 100.0  # normalize confidence to 0-1
        })
        
    return tokens
