import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.database import Base, set_sqlite_pragma
from sqlalchemy.engine import Engine
from sqlalchemy import event
from src.db import crud, models

# In-memory DB for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

@event.listens_for(Engine, "connect")
def set_test_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_and_get_document(db):
    doc_data = {
        "id": "doc_test123",
        "original_filename": "test.jpg",
        "file_path": "/tmp/test.jpg",
        "mime_type": "image/jpeg",
        "image_width": 800,
        "image_height": 600
    }
    doc = crud.create_document(db, doc_data)
    assert doc.id == "doc_test123"
    
    fetched = crud.get_document(db, "doc_test123")
    assert fetched.original_filename == "test.jpg"
    assert fetched.status == "PENDING"

def test_insert_extractions(db):
    doc_data = {
        "id": "doc_test123",
        "original_filename": "test.jpg",
        "file_path": "/tmp/test.jpg",
        "mime_type": "image/jpeg",
        "image_width": 800,
        "image_height": 600
    }
    crud.create_document(db, doc_data)
    
    exts = [
        {"field_type": "vendor_name", "raw_text": "Walmart", "confidence": 0.95, "bbox_json": "[0,0,10,10]"}
    ]
    inserted = crud.insert_extractions(db, "doc_test123", exts)
    assert len(inserted) == 1
    assert inserted[0].raw_text == "Walmart"

def test_save_correction(db):
    doc_data = {
        "id": "doc_test123",
        "original_filename": "test.jpg",
        "file_path": "/tmp/test.jpg",
        "mime_type": "image/jpeg",
        "image_width": 800,
        "image_height": 600
    }
    crud.create_document(db, doc_data)
    crud.insert_extractions(db, "doc_test123", [{"field_type": "total_amount", "raw_text": "100.00", "confidence": 0.9, "bbox_json": "[]"}])
    
    correction = crud.save_correction(db, "doc_test123", "total_amount", "100.00", "150.00")
    assert correction.corrected_value == "150.00"
    
    # Check extraction was updated
    ext = db.query(models.Extraction).filter_by(field_type="total_amount").first()
    assert ext.normalized_text == "150.00"
    assert ext.is_validated == True
