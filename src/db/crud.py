from sqlalchemy.orm import Session
from . import models
from typing import List, Optional

def create_document(db: Session, document_data: dict) -> models.Document:
    db_document = models.Document(**document_data)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: str) -> Optional[models.Document]:
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def list_documents(db: Session, skip: int = 0, limit: int = 100) -> List[models.Document]:
    return db.query(models.Document).order_by(models.Document.uploaded_at.desc()).offset(skip).limit(limit).all()

def update_document_status(db: Session, document_id: str, status: str, confidence: float = None, has_error: bool = False):
    doc = get_document(db, document_id)
    if doc:
        doc.status = status
        doc.has_validation_error = has_error
        if confidence is not None:
            doc.overall_confidence = confidence
        db.commit()
        db.refresh(doc)
    return doc

def insert_extractions(db: Session, document_id: str, extractions_data: List[dict]):
    extractions = []
    for data in extractions_data:
        ext = models.Extraction(document_id=document_id, **data)
        db.add(ext)
        extractions.append(ext)
    db.commit()
    return extractions

def insert_line_items(db: Session, document_id: str, line_items_data: List[dict]):
    items = []
    for data in line_items_data:
        item = models.LineItem(document_id=document_id, **data)
        db.add(item)
        items.append(item)
    db.commit()
    return items

def save_correction(db: Session, document_id: str, field_type: str, original_val: str, corrected_val: str, user: str = "operator"):
    # Log correction
    correction = models.Correction(
        document_id=document_id,
        field_type=field_type,
        original_value=original_val,
        corrected_value=corrected_val,
        corrected_by=user
    )
    db.add(correction)
    
    # Update the extraction
    extraction = db.query(models.Extraction).filter(
        models.Extraction.document_id == document_id,
        models.Extraction.field_type == field_type
    ).first()
    
    if extraction:
        extraction.normalized_text = corrected_val
        extraction.is_validated = True
        
    db.commit()
    return correction
