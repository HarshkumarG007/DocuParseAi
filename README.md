# 📄 DocuParse AI

Intelligent Document Understanding for Financial Records.

## 🚀 Overview
DocuParse AI is a local-first, privacy-focused machine learning pipeline that extracts structured data (Vendor, Date, Subtotal, Tax, Total, and Line Items) from uploaded receipts and invoices.

It utilizes Microsoft's **LayoutLMv3** (zero-shot extraction mapping via BIO tagging) coupled with robust fallback baseline deterministic rules and a beautiful drag-and-drop Streamlit workspace for human-in-the-loop review.

## ✨ Features
- **Privacy-First:** Processes all documents completely locally (SQLite WAL mode + Local Model Weights).
- **Multimodal AI:** Utilizes LayoutLMv3, combining text (OCR) and layout (bounding boxes) for semantic understanding.
- **Smart Validation:** Arithmetic parity checks cross-validate `Subtotal + Tax = Total`.
- **Visual Workspace:** Interactive Streamlit frontend that renders accurate bounding boxes overlaid on uploaded documents.
- **Instant Exports:** Download extracted and validated data directly to CSV or JSON formats.

## 🛠 Tech Stack
- **Backend:** FastAPI, SQLAlchemy, SQLite (WAL mode)
- **Frontend:** Streamlit, Custom CSS
- **Machine Learning:** PyTorch, Hugging Face `transformers`, PyTesseract OCR, Pillow
- **Containerization:** Docker, Docker Compose

## ⚡ Quickstart (Local Dev)
1. **Prerequisites:** 
   - Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) on your machine.
   - Python 3.10+
2. **Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Run Everything:**
   ```bash
   python scripts/run_dev.py
   ```
   Navigate to `http://localhost:8501` to access the Visual Workspace.

## 🐳 Quickstart (Docker)
Ensure you have Docker and Docker Compose installed.
```bash
docker-compose up --build
```
This handles all system dependencies including Tesseract C++ libraries.

## 🔒 Architecture
- `docs/architecture.md`: Comprehensive system architecture and data flow.
- `docs/PRD.md`: Full product requirements and scope.
- `docs/MODEL_CARD.md`: ML parameters and LayoutLMv3 evaluation metrics.
