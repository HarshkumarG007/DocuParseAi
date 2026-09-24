import pytest
from src.rules.normalizers import normalize_date, normalize_currency
from src.rules.verifier import verify_arithmetic_parity

def test_normalize_date():
    assert normalize_date("12/31/2023") == "2023-12-31"
    assert normalize_date("31-12-2023") == "2023-12-31"
    assert normalize_date("Jan 1st, 2024") == "2024-01-01"
    assert normalize_date("2024/05/05") == "2024-05-05"
    assert normalize_date("InvalidDate") == None

def test_normalize_currency():
    assert normalize_currency("$1,234.56") == 1234.56
    assert normalize_currency("1.234,56 €") == 1234.56
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
