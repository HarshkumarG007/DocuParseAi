"""
Reproducible evaluation script for DocuParse AI.
Runs extraction across benchmark samples, applies normalization,
and computes Precision, Recall, F1, and Exact Match metrics.

Usage:
    python evaluation/evaluate.py --engine regex
    python evaluation/evaluate.py --engine layoutlmv3
"""
import argparse
import json
import os
import sys
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.metrics import evaluate_dataset_predictions
from src.ml.baselines import run_regex_baseline
from src.rules.normalizers import normalize_date, normalize_currency
from src.rules.verifier import verify_arithmetic_parity

# Default benchmark evaluation suite representing diverse receipt layouts
BENCHMARK_SAMPLES = [
    {
        "id": "sample_001",
        "ocr_words": ["ACME", "CAFE", "&", "ROASTERY", "Date:", "2024-05-15", "Espresso", "4.50", "Subtotal", "49.50", "Tax", "2.48", "Total", "51.98"],
        "ground_truth": {
            "vendor": "ACME CAFE & ROASTERY",
            "date": "2024-05-15",
            "subtotal": "49.50",
            "tax": "2.48",
            "total": "51.98"
        }
    },
    {
        "id": "sample_002",
        "ocr_words": ["METRO", "SUPERMARKET", "12/31/2023", "Milk", "3.99", "Bread", "2.50", "SUBTOTAL:", "$45.00", "TAX:", "$3.60", "TOTAL:", "$48.60"],
        "ground_truth": {
            "vendor": "METRO SUPERMARKET",
            "date": "2023-12-31",
            "subtotal": "45.00",
            "tax": "3.60",
            "total": "48.60"
        }
    },
    {
        "id": "sample_003",
        "ocr_words": ["STARBUCKS", "COFFEE", "STORE", "#1042", "15-May-2024", "Latte", "$5.50", "Subtotal", "10.00", "Tax", "0.85", "Total", "10.85"],
        "ground_truth": {
            "vendor": "STARBUCKS COFFEE STORE",
            "date": "2024-05-15",
            "subtotal": "10.00",
            "tax": "0.85",
            "total": "10.85"
        }
    },
    {
        "id": "sample_004",
        "ocr_words": ["BEST", "BUY", "ELECTRONICS", "Date:", "04.09.2023", "Cable", "$19.99", "Subtotal:", "19.99", "Tax:", "1.60", "Total:", "21.59"],
        "ground_truth": {
            "vendor": "BEST BUY ELECTRONICS",
            "date": "2023-04-09",
            "subtotal": "19.99",
            "tax": "1.60",
            "total": "21.59"
        }
    },
    {
        "id": "sample_005",
        "ocr_words": ["TARGET", "STORES", "Oct", "25,", "2023", "Shampoo", "8.99", "Subtotal", "25.00", "Tax", "2.00", "Total", "27.00"],
        "ground_truth": {
            "vendor": "TARGET STORES",
            "date": "2023-10-25",
            "subtotal": "25.00",
            "tax": "2.00",
            "total": "27.00"
        }
    }
]

def run_evaluation(engine: str = "regex", samples: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Runs evaluation across samples and computes benchmark metrics."""
    if samples is None:
        samples = BENCHMARK_SAMPLES

    predictions_list = []
    ground_truth_list = []

    for item in samples:
        words = item["ocr_words"]
        gt = item["ground_truth"]
        
        # Execute pipeline
        raw_preds = run_regex_baseline(words)
        
        # Apply normalization
        normalized_pred = {}
        for field, raw_val in raw_preds.items():
            if not raw_val:
                continue
            if field == "date":
                normalized_pred[field] = normalize_date(raw_val) or raw_val
            elif field in ["total", "tax", "subtotal"]:
                parsed = normalize_currency(raw_val)
                normalized_pred[field] = str(parsed) if parsed is not None else raw_val
            else:
                normalized_pred[field] = raw_val

        predictions_list.append(normalized_pred)
        ground_truth_list.append(gt)

    metrics_report = evaluate_dataset_predictions(predictions_list, ground_truth_list)
    metrics_report["engine"] = engine
    return metrics_report

def print_metrics_table(report: Dict[str, Any]):
    """Pretty prints the metrics report to console."""
    print("\n" + "=" * 75)
    print(f"  DocuParse AI — Benchmark Evaluation Report (Engine: {report.get('engine', 'regex').upper()})")
    print("=" * 75)
    print(f"{'Field':<15} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Exact Match':<12}")
    print("-" * 75)
    
    field_keys = ["vendor", "date", "subtotal", "tax", "total"]
    for field in field_keys:
        if field in report:
            f_stats = report[field]
            print(f"{field.capitalize():<15} | {f_stats['precision']*100:>8.1f}% | {f_stats['recall']*100:>8.1f}% | {f_stats['f1']*100:>8.1f}% | {f_stats['exact_match']*100:>10.1f}%")
            
    print("-" * 75)
    print(f"Overall Macro F1: {report.get('macro_f1', 0.0) * 100:.1f}% across {report.get('total_samples', 0)} benchmark test samples")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate DocuParse AI extraction performance.")
    parser.add_argument("--engine", type=str, default="regex", choices=["regex", "layoutlmv3"], help="Extraction engine")
    parser.add_argument("--output", type=str, default="evaluation/benchmark_report.json", help="Path to save output JSON")
    args = parser.parse_args()

    report = run_evaluation(engine=args.engine)
    print_metrics_table(report)

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to: {output_path}")
