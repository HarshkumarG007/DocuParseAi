import pytest
from src.exporters.csv_exporter import export_document_to_csv
from src.exporters.json_exporter import export_document_to_json

class MockExtraction:
    def __init__(self, field_type, raw_text, normalized_text, confidence, bbox_json="[0,0,10,10]", is_validated=True):
        self.id = 1
        self.field_type = field_type
        self.raw_text = raw_text
        self.normalized_text = normalized_text
        self.confidence = confidence
        self.bbox_json = bbox_json
        self.is_validated = is_validated
        self.validation_notes = "Verified"

class MockLineItem:
    def __init__(self, description, quantity, unit_price, total_amount):
        self.id = 1
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_amount = total_amount

class MockDocument:
    def __init__(self):
        self.id = "doc_test123"
        self.original_filename = "receipt.jpg"
        self.mime_type = "image/jpeg"
        self.image_width = 1000
        self.image_height = 800
        self.uploaded_at = "2024-05-15 12:00:00"
        self.processed_at = "2024-05-15 12:00:02"
        self.status = "PROCESSED"
        self.overall_confidence = 0.92
        self.has_validation_error = False
        self.extractions = [
            MockExtraction("vendor", "ACME STORE", "ACME STORE", 0.95),
            MockExtraction("total", "$50.00", "50.00", 0.90),
            MockExtraction("tax", "$2.50", "2.50", 0.90)
        ]
        self.line_items = [
            MockLineItem("Item A", 2.0, 20.0, 40.0)
        ]

def test_csv_exporter_itemized():
    doc = MockDocument()
    csv_text = export_document_to_csv(doc, mode="itemized")
    assert "Document ID,Filename,Field,Raw Text,Normalized Value,Confidence,Validated" in csv_text
    assert "doc_test123" in csv_text
    assert "vendor" in csv_text
    assert "50.00" in csv_text

def test_csv_exporter_summary():
    doc = MockDocument()
    csv_text = export_document_to_csv(doc, mode="summary")
    assert "document_id,filename,processed_date,vendor_name" in csv_text
    assert "doc_test123" in csv_text
    assert "ACME STORE" in csv_text
    assert "50.00" in csv_text

def test_json_exporter():
    doc = MockDocument()
    json_data = export_document_to_json(doc)
    assert json_data["document_metadata"]["id"] == "doc_test123"
    assert json_data["financial_summary"]["vendor"] == "ACME STORE"
    assert json_data["financial_summary"]["total"] == "50.00"
    assert len(json_data["extractions"]) == 3
    assert len(json_data["line_items"]) == 1
    assert json_data["line_items"][0]["description"] == "Item A"
