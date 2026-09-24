import pytest
from evaluation.metrics import compute_exact_match, compute_token_f1, evaluate_dataset_predictions
from evaluation.evaluate import run_evaluation

def test_exact_match_metric():
    assert compute_exact_match("ACME Cafe", "acme cafe") == 1.0
    assert compute_exact_match("Total: $50.00", "Total: $51.00") == 0.0
    assert compute_exact_match("", None) == 1.0

def test_token_f1_metric():
    res = compute_token_f1("Acme Cafe Roastery", "Acme Cafe")
    assert res["recall"] == 1.0
    assert res["precision"] == pytest.approx(2/3, rel=1e-3)
    assert res["f1"] > 0.7

def test_run_benchmark_evaluation():
    report = run_evaluation(engine="regex")
    assert "macro_f1" in report
    assert "vendor" in report
    assert "total" in report
    assert report["total_samples"] > 0
