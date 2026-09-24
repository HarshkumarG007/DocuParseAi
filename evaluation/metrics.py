"""
Evaluation metrics computation module for DocuParse AI.
Calculates Exact Match (EM), Token-level Precision/Recall/F1, and Field-level Macro F1.
"""
from typing import Dict, List, Any, Optional
import re

def normalize_text_for_eval(text: Optional[str]) -> str:
    """Lowercase, strip punctuation and collapse whitespace for normalized evaluation."""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    return " ".join(text.split())

def compute_exact_match(prediction: Optional[str], ground_truth: Optional[str]) -> float:
    """Returns 1.0 if normalized strings match exactly, 0.0 otherwise."""
    norm_p = normalize_text_for_eval(prediction)
    norm_gt = normalize_text_for_eval(ground_truth)
    if not norm_p and not norm_gt:
        return 1.0
    return 1.0 if norm_p == norm_gt else 0.0

def compute_token_f1(prediction: Optional[str], ground_truth: Optional[str]) -> Dict[str, float]:
    """Computes token-level precision, recall, and F1 score between two text strings."""
    pred_tokens = normalize_text_for_eval(prediction).split()
    gt_tokens = normalize_text_for_eval(ground_truth).split()
    
    if not pred_tokens and not gt_tokens:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not pred_tokens or not gt_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
    common = set(pred_tokens) & set(gt_tokens)
    num_same = sum(min(pred_tokens.count(token), gt_tokens.count(token)) for token in common)
    
    if num_same == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
        
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gt_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }

def evaluate_dataset_predictions(
    predictions_list: List[Dict[str, Any]], 
    ground_truth_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates predictions across a dataset against ground truth annotations.
    Computes per-field Precision, Recall, F1, and overall Macro F1.
    """
    field_types = ["vendor", "date", "subtotal", "tax", "total"]
    field_stats = {f: {"tp": 0, "fp": 0, "fn": 0, "em_total": 0, "count": 0} for f in field_types}
    
    for pred_dict, gt_dict in zip(predictions_list, ground_truth_list):
        for field in field_types:
            p_val = pred_dict.get(field)
            gt_val = gt_dict.get(field)
            
            if gt_val is not None:
                field_stats[field]["count"] += 1
                
            em = compute_exact_match(p_val, gt_val)
            field_stats[field]["em_total"] += em
            
            has_pred = bool(normalize_text_for_eval(p_val))
            has_gt = bool(normalize_text_for_eval(gt_val))
            
            if has_pred and has_gt:
                if em == 1.0:
                    field_stats[field]["tp"] += 1
                else:
                    field_stats[field]["fp"] += 1
                    field_stats[field]["fn"] += 1
            elif has_pred and not has_gt:
                field_stats[field]["fp"] += 1
            elif not has_pred and has_gt:
                field_stats[field]["fn"] += 1

    summary = {}
    f1_scores = []
    
    for field, stats in field_stats.items():
        tp = stats["tp"]
        fp = stats["fp"]
        fn = stats["fn"]
        count = stats["count"]
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        em_rate = stats["em_total"] / count if count > 0 else 1.0
        
        summary[field] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "exact_match": round(em_rate, 4),
            "support": count
        }
        if count > 0:
            f1_scores.append(f1)
            
    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0
    summary["macro_f1"] = round(macro_f1, 4)
    summary["total_samples"] = len(ground_truth_list)
    
    return summary
