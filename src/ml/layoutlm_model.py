import torch
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
from typing import List, Dict
import os

# We map our core targets to BIO tags
LABELS = [
    "O",
    "B-VENDOR", "I-VENDOR",
    "B-DATE", "I-DATE",
    "B-TOTAL", "I-TOTAL",
    "B-TAX", "I-TAX",
    "B-LINEITEM", "I-LINEITEM"
]
id2label = {v: k for v, k in enumerate(LABELS)}
label2id = {k: v for v, k in enumerate(LABELS)}

class DocumentParserModel:
    def __init__(self, model_path: str = "microsoft/layoutlmv3-base"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading LayoutLMv3 model on {self.device}...")
        
        try:
            self.processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
            
            # Disable strict matching to allow loading base model with custom num_labels
            self.model = LayoutLMv3ForTokenClassification.from_pretrained(
                model_path, 
                num_labels=len(LABELS),
                id2label=id2label,
                label2id=label2id,
                ignore_mismatched_sizes=True
            )
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
        except Exception as e:
            print(f"Failed to load model from {model_path}: {e}")
            self.is_loaded = False
            
    def predict(self, image: Image.Image, words: List[str], boxes: List[List[int]]) -> List[Dict]:
        """
        Run inference on a document image with pre-extracted OCR tokens and boxes.
        Returns a list of extracted entities.
        """
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded.")
            
        if not words or not boxes:
            return []
            
        # Prepare inputs
        encoding = self.processor(
            image, 
            words, 
            boxes=boxes, 
            return_tensors="pt", 
            truncation=True, 
            padding="max_length",
            max_length=512
        )
        
        # Move to device
        for k, v in encoding.items():
            if hasattr(v, 'to'):
                encoding[k] = v.to(self.device)
                
        with torch.no_grad():
            outputs = self.model(**encoding)
            
        logits = outputs.logits
        predictions = logits.argmax(-1).squeeze().tolist()
        probabilities = torch.nn.functional.softmax(logits, dim=-1).max(-1)[0].squeeze().tolist()
        
        # Handle case where output is a single scalar (e.g. 1 token)
        if not isinstance(predictions, list):
            predictions = [predictions]
            probabilities = [probabilities]
            
        word_ids = encoding.word_ids()
        
        # Decode BIO tags back to structured entities
        entities = []
        current_entity = None
        
        for idx, word_id in enumerate(word_ids):
            if word_id is None:
                continue
                
            pred_id = predictions[idx]
            label = id2label[pred_id]
            prob = probabilities[idx]
            
            if label == "O":
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
                continue
                
            prefix = label[:2] # B- or I-
            entity_type = label[2:]
            
            if prefix == "B-":
                if current_entity:
                    entities.append(current_entity)
                
                # word_id corresponds to the original words list
                current_entity = {
                    "field_type": entity_type.lower(),
                    "text": words[word_id],
                    "confidence": [prob],
                    "bboxes": [boxes[word_id]]
                }
            elif prefix == "I-" and current_entity and current_entity["field_type"] == entity_type.lower():
                # Prevent duplicate text appending if word_id is the same as previous token
                if current_entity["text"] and words[word_id] not in current_entity["text"]:
                    current_entity["text"] += " " + words[word_id]
                current_entity["confidence"].append(prob)
                current_entity["bboxes"].append(boxes[word_id])
                
        if current_entity:
            entities.append(current_entity)
            
        # Post-process entities to merge confidence and bounding boxes
        structured_results = []
        for ent in entities:
            avg_conf = sum(ent["confidence"]) / len(ent["confidence"])
            
            # Compute a union bounding box
            x0 = min([b[0] for b in ent["bboxes"]])
            y0 = min([b[1] for b in ent["bboxes"]])
            x1 = max([b[2] for b in ent["bboxes"]])
            y1 = max([b[3] for b in ent["bboxes"]])
            
            structured_results.append({
                "field_type": ent["field_type"],
                "raw_text": ent["text"],
                "confidence": avg_conf,
                "bbox_json": f"[{x0},{y0},{x1},{y1}]"
            })
            
        return structured_results
