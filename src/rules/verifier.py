from decimal import Decimal, InvalidOperation
from typing import Dict, List, Any

def verify_arithmetic_parity(extracted_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Cross-checks mathematical balance: |Total - (Subtotal + Tax)| <= 0.05 using Decimal.
    Produces structured arithmetic_status: PASS, FAIL, or UNVERIFIABLE.
    """
    total = None
    tax = Decimal("0.00")
    subtotal = None
    
    # Helper to find fields
    for field in extracted_fields:
        val_str = str(field.get("normalized_value", "")).strip()
        if not val_str:
            continue
        try:
            if field.get("field_type") == "total":
                total = Decimal(val_str)
            elif field.get("field_type") == "tax":
                tax = Decimal(val_str)
            elif field.get("field_type") == "subtotal":
                subtotal = Decimal(val_str)
        except (InvalidOperation, TypeError):
            continue
            
    # If no total is extracted, we cannot verify
    if total is None:
        return extracted_fields
        
    for field in extracted_fields:
        if field.get("field_type") == "total":
            if subtotal is not None and subtotal > Decimal("0.00"):
                diff = abs(total - (subtotal + tax))
                if diff > Decimal("0.05"):
                    field["validation_notes"] = f"Math discrepancy: Total ({total}) != Subtotal ({subtotal}) + Tax ({tax})"
                    field["has_validation_error"] = True
                    field["arithmetic_status"] = "FAIL"
                else:
                    field["validation_notes"] = f"Math verified: {subtotal} + {tax} == {total}"
                    field["has_validation_error"] = False
                    field["arithmetic_status"] = "PASS"
            else:
                field["validation_notes"] = "Cannot verify math without subtotal."
                field["has_validation_error"] = False
                field["arithmetic_status"] = "UNVERIFIABLE"
                
    return extracted_fields

