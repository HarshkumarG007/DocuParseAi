import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.main import app
from src.db.database import get_db, Base
import os
from PIL import Image
import io

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_api.db"):
        try:
            os.remove("./test_api.db")
        except:
            pass

def test_api_health():
    res = client.get("/api/v1/documents")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_document_upload_and_export():
    img = Image.new('RGB', (100, 100), color = 'white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    from unittest.mock import patch
    with patch("src.api.main.extract_tokens_and_boxes", return_value=[{"word": "Total", "bbox": [0,0,10,10]}, {"word": "$50.00", "bbox": [0,0,10,10]}]):
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test_doc.jpg", img_byte_arr, "image/jpeg")}
        )
    
    assert response.status_code == 201, response.text
    doc = response.json()
    assert doc["original_filename"] == "test_doc.jpg"
    doc_id = doc["id"]
    
    res_detail = client.get(f"/api/v1/documents/{doc_id}")
    assert res_detail.status_code == 200
    
    res_export = client.get(f"/api/v1/documents/{doc_id}/export?format=csv")
    assert res_export.status_code == 200
    assert "text/csv" in res_export.headers["content-type"]

def test_document_upload_exceeds_size_limit(monkeypatch):
    import src.api.main as api_main
    monkeypatch.setattr(api_main, "MAX_FILE_SIZE_BYTES", 500)
    
    large_payload = b"A" * 600
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("too_large.jpg", io.BytesIO(large_payload), "image/jpeg")}
    )
    assert response.status_code == 413
    assert "File size exceeds allowable limit" in response.json()["detail"]

def test_document_upload_layoutlmv3_engine(monkeypatch):
    from unittest.mock import patch, MagicMock
    monkeypatch.setenv("EXTRACTION_ENGINE", "layoutlmv3")
    
    mock_model = MagicMock()
    mock_model.is_loaded = True
    mock_model.predict.return_value = [
        {"field_type": "total", "raw_text": "$100.00", "confidence": 0.95, "bbox_json": "[0, 0, 10, 10]"}
    ]
    monkeypatch.setattr("src.api.main.get_layoutlm_model", lambda: mock_model)
    
    img = Image.new('RGB', (100, 100), color = 'white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    with patch("src.api.main.extract_tokens_and_boxes", return_value=[{"word": "$100.00", "bbox": [0,0,10,10], "confidence": 95.0}]):
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("ml_doc.jpg", img_byte_arr, "image/jpeg")}
        )
    assert response.status_code == 201
    doc = response.json()
    assert doc["status"] in ["PROCESSED", "REVIEW_REQUIRED"]

def test_document_upload_review_required_on_math_mismatch():
    img = Image.new('RGB', (100, 100), color = 'white')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    from unittest.mock import patch
    # Total $100, Subtotal $50, Tax $10 -> mismatch 100 != 60 -> math error -> REVIEW_REQUIRED
    mock_tokens = [
        {"word": "Subtotal", "bbox": [0,0,10,10], "confidence": 90.0},
        {"word": "$50.00", "bbox": [0,0,10,10], "confidence": 90.0},
        {"word": "Tax", "bbox": [0,0,10,10], "confidence": 90.0},
        {"word": "$10.00", "bbox": [0,0,10,10], "confidence": 90.0},
        {"word": "Total", "bbox": [0,0,10,10], "confidence": 90.0},
        {"word": "$100.00", "bbox": [0,0,10,10], "confidence": 90.0},
    ]
    with patch("src.api.main.extract_tokens_and_boxes", return_value=mock_tokens):
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("math_mismatch.jpg", img_byte_arr, "image/jpeg")}
        )
    assert response.status_code == 201
    doc = response.json()
    assert doc["status"] == "REVIEW_REQUIRED"
    assert doc["has_validation_error"] is True

