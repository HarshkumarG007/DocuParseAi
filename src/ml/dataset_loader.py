from typing import List, Dict
import json

def align_tokens_to_ground_truth(ocr_tokens: List[Dict], ground_truth: Dict[str, str]) -> List[Dict]:
    """
    Naively align OCR tokens to ground truth text and assign BIO tags.
    This uses simple substring matching for the MVP data pipeline.
    """
    aligned_tokens = []
    
    # Initialize all tokens with 'O' (Outside)
    for token in ocr_tokens:
        aligned_tokens.append({
            "word": token["word"],
            "bbox": token["bbox"],
            "label": "O"
        })
        
    # Simple matching algorithm
    for entity_label, entity_value in ground_truth.items():
        if not entity_value:
            continue
            
        entity_words = str(entity_value).split()
        
        # Attempt to find sequence of tokens that matches entity_words
        for i in range(len(aligned_tokens) - len(entity_words) + 1):
            match = True
            for j, e_word in enumerate(entity_words):
                # Basic case-insensitive exact match
                if aligned_tokens[i+j]["word"].lower() != e_word.lower():
                    match = False
                    break
                    
            if match:
                # Assign BIO tags
                aligned_tokens[i]["label"] = f"B-{entity_label.upper()}"
                for j in range(1, len(entity_words)):
                    aligned_tokens[i+j]["label"] = f"I-{entity_label.upper()}"
                # Move forward
                break
                
    return aligned_tokens
