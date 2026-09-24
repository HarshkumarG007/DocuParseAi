from typing import Any, Dict

def export_document_to_json(doc: Any) -> Dict[str, Any]:
    """
    Format document data into a standardized financial JSON export schema.
    """
    extractions_list = []
    field_summary = {}
    
    for ext in getattr(doc, "extractions", []):
        field_type = getattr(ext, "field_type", "")
        norm_val = getattr(ext, "normalized_text", "")
        raw_val = getattr(ext, "raw_text", "")
        conf = getattr(ext, "confidence", 0.0)
        bbox = getattr(ext, "bbox_json", "[]")
        is_val = getattr(ext, "is_validated", False)
        notes = getattr(ext, "validation_notes", None)
        
        extractions_list.append({
            "id": getattr(ext, "id", None),
            "field_type": field_type,
            "raw_text": raw_val,
            "normalized_text": norm_val,
            "confidence": conf,
            "bbox_json": bbox,
            "is_validated": is_val,
            "validation_notes": notes
        })
        field_summary[field_type] = norm_val or raw_val

    line_items_list = []
    for item in getattr(doc, "line_items", []):
        line_items_list.append({
            "id": getattr(item, "id", None),
            "description": getattr(item, "description", ""),
            "quantity": getattr(item, "quantity", 1.0),
            "unit_price": getattr(item, "unit_price", None),
            "total_amount": getattr(item, "total_amount", 0.0)
        })

    return {
        "document_metadata": {
            "id": getattr(doc, "id", ""),
            "original_filename": getattr(doc, "original_filename", ""),
            "mime_type": getattr(doc, "mime_type", ""),
            "image_width": getattr(doc, "image_width", 0),
            "image_height": getattr(doc, "image_height", 0),
            "uploaded_at": str(getattr(doc, "uploaded_at", "")),
            "processed_at": str(getattr(doc, "processed_at", "") or ""),
            "status": getattr(doc, "status", ""),
            "overall_confidence": getattr(doc, "overall_confidence", None),
            "has_validation_error": getattr(doc, "has_validation_error", False)
        },
        "financial_summary": field_summary,
        "extractions": extractions_list,
        "line_items": line_items_list
    }
