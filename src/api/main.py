from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os
import json

from src.db.database import get_db, engine, Base
from src.db import crud
from src.api import schemas
from src.utils.storage import save_upload
from src.ml.ocr_engine import extract_tokens_and_boxes
from src.ml.baselines import run_regex_baseline
from src.rules.normalizers import normalize_date, normalize_currency
from src.rules.verifier import verify_arithmetic_parity
from src.exporters.csv_exporter import export_document_to_csv
from src.exporters.json_exporter import export_document_to_json
from src.db import models

# Ensure tables are created automatically on service initialization
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocuParse AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_bbox_for_text(text: str, tokens: list) -> str:
    """Find union bounding box for tokens matching text span."""
    if not text or not tokens:
        return "[]"
    clean_parts = [p.strip().lower() for p in text.split() if p.strip()]
    matched_boxes = []
    for part in clean_parts:
        for t in tokens:
            word = t.get("word", "").lower()
            if part in word or word in part:
                if "bbox" in t and len(t["bbox"]) == 4:
                    matched_boxes.append(t["bbox"])
                break
    if not matched_boxes:
        return "[]"
    x0 = min(b[0] for b in matched_boxes)
    y0 = min(b[1] for b in matched_boxes)
    x1 = max(b[2] for b in matched_boxes)
    y1 = max(b[3] for b in matched_boxes)
    return f"[{x0},{y0},{x1},{y1}]"

@app.post("/api/v1/documents/upload", response_model=schemas.DocumentResponse, status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        saved_info = save_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    doc = crud.create_document(db, saved_info)
    crud.update_document_status(db, doc.id, "PROCESSING")
    
    try:
        # OCR Extraction
        tokens = extract_tokens_and_boxes(saved_info["file_path"])
        words = [t["word"] for t in tokens]
        
        # Pipeline processing - Baseline Regex extraction with spatial bounding box matching
        predictions = run_regex_baseline(words)
        
        extracted_fields = []
        for field_type, raw_val in predictions.items():
            if raw_val:
                norm_val = raw_val
                if field_type == "date":
                    norm_val = normalize_date(raw_val) or raw_val
                elif field_type in ["total", "tax", "subtotal"]:
                    parsed = normalize_currency(raw_val)
                    norm_val = str(parsed) if parsed is not None else raw_val
                    
                bbox = find_bbox_for_text(raw_val, tokens)
                extracted_fields.append({
                    "field_type": field_type,
                    "raw_text": raw_val,
                    "normalized_value": norm_val,
                    "confidence": 0.85, 
                    "bbox_json": bbox
                })
                
        # Verification
        verified_fields = verify_arithmetic_parity(extracted_fields)
        
        # Save extractions
        db_fields = []
        has_error = False
        for f in verified_fields:
            if f.get("has_validation_error"):
                has_error = True
            db_fields.append({
                "field_type": f["field_type"],
                "raw_text": f["raw_text"],
                "normalized_text": str(f.get("normalized_value", "")),
                "confidence": f["confidence"],
                "bbox_json": f["bbox_json"],
                "is_validated": not f.get("has_validation_error", False),
                "validation_notes": f.get("validation_notes")
            })
            
        crud.insert_extractions(db, doc.id, db_fields)
        crud.update_document_status(db, doc.id, "PROCESSED", confidence=0.85, has_error=has_error)
        
    except Exception as e:
        crud.update_document_status(db, doc.id, "ERROR")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
        
    return crud.get_document(db, doc.id)

@app.get("/api/v1/documents", response_model=List[schemas.DocumentResponse])
def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_documents(db, skip, limit)

@app.get("/api/v1/documents/{document_id}", response_model=schemas.DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.post("/api/v1/documents/{document_id}/correct")
def correct_document(document_id: str, correction: schemas.CorrectionRequest, db: Session = Depends(get_db)):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    crud.save_correction(db, document_id, correction.field_type, correction.original_value, correction.corrected_value)
    return {"status": "success", "message": "Correction saved."}

@app.get("/api/v1/documents/{document_id}/export")
def export_document(document_id: str, format: str = "json", db: Session = Depends(get_db)):
    doc = crud.get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if format.lower() == "json":
        json_data = export_document_to_json(doc)
        return JSONResponse(content=json_data)
        
    if format.lower() == "csv":
        csv_text = export_document_to_csv(doc, mode="itemized")
        return Response(
            content=csv_text,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=export_{document_id}.csv"}
        )

    raise HTTPException(status_code=400, detail="Unsupported format. Use csv or json.")
