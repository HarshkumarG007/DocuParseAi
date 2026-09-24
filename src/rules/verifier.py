from typing import Dict, List, Any

def verify_arithmetic_parity(extracted_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Cross-checks mathematical balance: |Total - (Subtotal + Tax)| <= 0.05.
    Flags discrepancies.
    """
    total = None
    tax = 0.0
    subtotal = 0.0
    
    # Helper to find fields
    for field in extracted_fields:
        if field.get("field_type") == "total" and field.get("normalized_value"):
            total = float(field["normalized_value"])
        elif field.get("field_type") == "tax" and field.get("normalized_value"):
            tax = float(field["normalized_value"])
        elif field.get("field_type") == "subtotal" and field.get("normalized_value"):
            subtotal = float(field["normalized_value"])
            
    # If no total is extracted, we can't verify
    if total is None:
        return extracted_fields
        
    for field in extracted_fields:
        if field.get("field_type") == "total":
            if subtotal > 0:
                diff = abs(total - (subtotal + tax))
                if diff > 0.05:
                    field["validation_notes"] = f"Math discrepancy: Total ({total}) != Subtotal ({subtotal}) + Tax ({tax})"
                    field["has_validation_error"] = True
                else:
                    field["validation_notes"] = "Math verified."
                    field["has_validation_error"] = False
            else:
                # Can't fully verify without subtotal, assume OK for now
                field["validation_notes"] = "Cannot verify math without subtotal."
                
    return extracted_fields
