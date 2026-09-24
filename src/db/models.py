from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True) # doc_uuid4
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="PENDING", index=True) # PENDING, PROCESSED, VERIFIED, ERROR
    overall_confidence = Column(Float, nullable=True)
    has_validation_error = Column(Boolean, default=False)
    
    extractions = relationship("Extraction", back_populates="document", cascade="all, delete-orphan")
    line_items = relationship("LineItem", back_populates="document", cascade="all, delete-orphan")
    corrections = relationship("Correction", back_populates="document", cascade="all, delete-orphan")

class Extraction(Base):
    __tablename__ = "extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    field_type = Column(String, nullable=False) # vendor_name, document_date, total_amount, tax_amount
    raw_text = Column(String, nullable=False)
    normalized_text = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    bbox_json = Column(String, nullable=False) # JSON array [x0, y0, x1, y1]
    is_validated = Column(Boolean, default=False)
    validation_notes = Column(String, nullable=True)
    
    document = relationship("Document", back_populates="extractions")

class LineItem(Base):
    __tablename__ = "line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=False)
    bbox_json = Column(String, nullable=True)
    
    document = relationship("Document", back_populates="line_items")

class Correction(Base):
    __tablename__ = "corrections"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    field_type = Column(String, nullable=False)
    original_value = Column(String, nullable=False)
    corrected_value = Column(String, nullable=False)
    corrected_at = Column(DateTime(timezone=True), server_default=func.now())
    corrected_by = Column(String, default="operator")
    
    document = relationship("Document", back_populates="corrections")
