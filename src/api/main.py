from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from src.db.database import get_db, engine, Base
from src.db import crud
from src.api import schemas
from src.utils.storage import save_upload
from src.ml.ocr_engine import extract_tokens_and_boxes
from src.ml.baselines import run_regex_baseline
from src.rules.normalizers import normalize_date, normalize_currency
from src.rules.verifier import verify_arithmetic_parity

app = FastAPI(title="DocuParse AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # Pipeline processing - currently using Baseline Regex for stability.
        # LayoutLMv3 inference logic from src.ml.layoutlm_model can be injected here.
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
                    
                extracted_fields.append({
                    "field_type": field_type,
                    "raw_text": raw_val,
                    "normalized_value": norm_val,
                    "confidence": 0.85, 
                    "bbox_json": "[]" 
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
        return doc
        
    if format.lower() == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Document ID", "Filename", "Field", "Raw Text", "Normalized Value", "Confidence"])
        for ext in doc.extractions:
            writer.writerow([doc.id, doc.original_filename, ext.field_type, ext.raw_text, ext.normalized_text, ext.confidence])
        
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=export_{document_id}.csv"})

    raise HTTPException(status_code=400, detail="Unsupported format. Use csv or json.")
