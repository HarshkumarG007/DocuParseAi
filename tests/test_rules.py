import pytest
from src.rules.normalizers import normalize_date, normalize_currency
from src.rules.verifier import verify_arithmetic_parity

def test_normalize_date():
    assert normalize_date("12/31/2023") == "2023-12-31"
    assert normalize_date("31-12-2023") == "2023-12-31"
    assert normalize_date("Jan 1st, 2024") == "2024-01-01"
    assert normalize_date("2024/05/05") == "2024-05-05"
    assert normalize_date("15 March 2024") == "2024-03-15"
    assert normalize_date("2024-11-20") == "2024-11-20"
    assert normalize_date("04.09.2023") == "2023-04-09"
    assert normalize_date("Oct 25, 2023") == "2023-10-25"
    assert normalize_date("2022.12.01") == "2022-12-01"
    assert normalize_date("28-Feb-2024") == "2024-02-28"
    assert normalize_date("InvalidDate") == None

def test_normalize_currency():
    assert normalize_currency("$1,234.56") == 1234.56
    assert normalize_currency("1.234,56 €") == 1234.56
    assert normalize_currency("£99.95") == 99.95
    assert normalize_currency("¥5000") == 5000.0
    assert normalize_currency("10O.00") == 100.00
    assert normalize_currency("50,00") == 50.00
    assert normalize_currency("abcd") == None

def test_verify_arithmetic_parity():
    fields = [
        {"field_type": "total", "normalized_value": "105.00"},
        {"field_type": "subtotal", "normalized_value": "100.00"},
        {"field_type": "tax", "normalized_value": "5.00"}
    ]
    verified = verify_arithmetic_parity(fields)
    total_field = next(f for f in verified if f["field_type"] == "total")
    assert total_field.get("has_validation_error") == False
    assert "Math verified" in total_field.get("validation_notes")

def test_verify_arithmetic_parity_error():
    fields = [
        {"field_type": "total", "normalized_value": "110.00"},
        {"field_type": "subtotal", "normalized_value": "100.00"},
        {"field_type": "tax", "normalized_value": "5.00"}
    ]
    verified = verify_arithmetic_parity(fields)
    total_field = next(f for f in verified if f["field_type"] == "total")
    assert total_field.get("has_validation_error") == True
    assert "Math discrepancy" in total_field.get("validation_notes")

def test_canvas_overlay_rendering():
    from PIL import Image
    from src.ui.components.canvas_overlay import render_bounding_boxes
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        temp_path = f.name
    try:
        Image.new("RGB", (200, 200), color="white").save(temp_path)
        extractions = [
            {"field_type": "total", "bbox_json": "[10, 20, 150, 60]"},
            {"field_type": "vendor", "bbox_json": "[5, 5, 80, 25]"}
        ]
        result = render_bounding_boxes(temp_path, extractions)
        assert result.size == (200, 200)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
