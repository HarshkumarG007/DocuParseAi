from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

class ExtractionBase(BaseModel):
    field_type: str
    raw_text: str
    normalized_text: Optional[str] = None
    confidence: float
    bbox_json: str
    is_validated: bool = False
    validation_notes: Optional[str] = None

class ExtractionResponse(ExtractionBase):
    id: int
    document_id: str
    model_config = ConfigDict(from_attributes=True)

class LineItemBase(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: Optional[float] = None
    total_amount: float
    bbox_json: Optional[str] = None

class LineItemResponse(LineItemBase):
    id: int
    document_id: str
    model_config = ConfigDict(from_attributes=True)

class DocumentBase(BaseModel):
    original_filename: str
    mime_type: str
    status: str
    overall_confidence: Optional[float] = None
    has_validation_error: bool = False

class DocumentResponse(DocumentBase):
    id: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    extractions: List[ExtractionResponse] = []
    line_items: List[LineItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class CorrectionRequest(BaseModel):
    field_type: str
    original_value: str
    corrected_value: str
