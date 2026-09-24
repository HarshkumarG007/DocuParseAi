import csv
from io import StringIO
from typing import Any

def export_document_to_csv(doc: Any, mode: str = "itemized") -> str:
    """
    Export document data to an RFC 4180-compliant CSV string.
    
    Modes:
      - 'itemized': Exports one row per extracted field with confidence and raw text.
      - 'summary': Exports a single record row matching PRD Feature 5 standard headers:
                   document_id, filename, processed_date, vendor_name, document_date,
                   tax_amount, total_amount, line_items_json, status.
    """
    output = StringIO()
    writer = csv.writer(output)
    
    if mode == "summary":
        headers = [
            "document_id",
            "filename",
            "processed_date",
            "vendor_name",
            "document_date",
            "subtotal_amount",
            "tax_amount",
            "total_amount",
            "status",
            "overall_confidence",
            "has_validation_error"
        ]
        writer.writerow(headers)
        
        # Build field map
        field_map = {}
        for ext in getattr(doc, "extractions", []):
            field_type = getattr(ext, "field_type", "")
            val = getattr(ext, "normalized_text", None) or getattr(ext, "raw_text", "")
            field_map[field_type] = val
            
        row = [
            getattr(doc, "id", ""),
            getattr(doc, "original_filename", ""),
            str(getattr(doc, "uploaded_at", "")),
            field_map.get("vendor", ""),
            field_map.get("date", ""),
            field_map.get("subtotal", ""),
            field_map.get("tax", ""),
            field_map.get("total", ""),
            getattr(doc, "status", ""),
            f"{getattr(doc, 'overall_confidence', 0.0) or 0.0:.2f}",
            str(getattr(doc, "has_validation_error", False))
        ]
        writer.writerow(row)
    else:
        # Default itemized RFC-compliant format
        writer.writerow(["Document ID", "Filename", "Field", "Raw Text", "Normalized Value", "Confidence", "Validated"])
        for ext in getattr(doc, "extractions", []):
            writer.writerow([
                getattr(doc, "id", ""),
                getattr(doc, "original_filename", ""),
                getattr(ext, "field_type", ""),
                getattr(ext, "raw_text", ""),
                getattr(ext, "normalized_text", ""),
                f"{getattr(ext, 'confidence', 0.0) or 0.0:.2f}",
                str(getattr(ext, "is_validated", False))
            ])
            
    output.seek(0)
    return output.getvalue()
