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
