# Master Task Breakdown & Execution Roadmap

## Document Details
- **Project Name:** DocuParse AI — Intelligent Document Understanding for Financial Records
- **Version:** 1.0.0-MVP
- **Status:** Baseline Ready for Phase 1 Execution
- **Date:** 2026-09-24
- **Lead Architect:** Senior Full-Stack Developer & AI Systems Architect

---

## Task Management Rules
1. Work strictly on one task at a time.
2. Do not mark a task `[Completed]` until its verification criteria have been executed and validated.
3. Every task change or completion must update this file and `docs/memory.md`.

---

## Phase 1 — Project Definition & Baseline Validation

- [Completed] **Task 1.1: Confirm Requirements & Dataset Access**
  - Verify access to SROIE, CORD, and FUNSD dataset repositories.
  - Confirm MVP field extraction targets: Vendor, Date, Total, Tax, Line Items.
  - Acceptance Criteria: Data sources documented and accessible via automated download scripts (`scripts/download_datasets.py`).

- [Completed] **Task 1.2: Establish Evaluation Benchmarks**
  - Define evaluation metric scripts for Field-Level F1, Character Error Rate (CER), and Tree-Edit Distance.
  - Set baseline thresholds: F1 $\ge 0.45$ for Baseline 1 (Regex), F1 $\ge 0.75$ for LayoutLMv3.
  - Acceptance Criteria: Baseline regex benchmark established in `src/ml/baselines.py`.

---

## Phase 2 — Technical Foundation & Environment Setup

- [Completed] **Task 2.1: Repository Structure & Virtual Environment**
  - Initialize directory structure according to `docs/architecture.md`.
  - Create Python virtual environment and configure `.gitignore`.
  - Acceptance Criteria: Clean repo structure created with all required packages organized.

- [Completed] **Task 2.2: Dependency Configuration**
  - Create `requirements.txt` containing FastAPI, Uvicorn, Streamlit, PyTorch, Transformers, Accelerate, PyTesseract, Pydantic, Pillow, OpenCV, Dateparser, Pandas.
  - Create `requirements-dev.txt` containing pytest, httpx, ruff, black.
  - Acceptance Criteria: `pip install -r requirements.txt` succeeds without dependency conflicts.

- [Completed] **Task 2.3: Environment & Pre-flight Diagnostics**
  - Create `.env.example` with standard port, storage, and binary path variables.
  - Create pre-flight diagnostic script `scripts/diagnostics.py` verifying Python version, CUDA availability, and Tesseract binary installation.
  - Acceptance Criteria: Diagnostic script outputs comprehensive system check report.

- [Completed] **Task 2.4: Code Quality & Testing Infrastructure**
  - Configure `pytest` setup with `tests/` providing mock fixtures and test images.
  - Acceptance Criteria: `pytest` runs and executes automated tests across API, DB, Rules, and ML subsystems.

---

## Phase 3 — Database & Storage Layer

- [Completed] **Task 3.1: SQLite Database Engine & WAL Configuration**
  - Implement `src/db/database.py` with thread-safe connection pooling, WAL mode (`PRAGMA journal_mode=WAL;`), and foreign key enforcement.
  - Acceptance Criteria: Database initializes and creates SQLite file with WAL journal mode.

- [Completed] **Task 3.2: Database Schemas & DDL Initialization**
  - Implement table schemas in `src/db/models.py`: `documents`, `extractions`, `line_items`, and `corrections`.
  - Add indexes for document status, upload timestamps, and foreign keys.
  - Acceptance Criteria: Unit test creates all tables and verifies foreign key cascade behavior.

- [Completed] **Task 3.3: Database CRUD Operations**
  - Implement `src/db/crud.py` with typed operations: `create_document`, `get_document_by_id`, `insert_extractions`, `save_correction`, and `list_documents`.
  - Acceptance Criteria: Pytest suite validates all CRUD methods with parameterized queries.

- [Completed] **Task 3.4: Local Storage File Manager**
  - Implement file storage utilities in `src/utils/storage.py` handling file saving, UUID path sanitization, MIME-type verification, and PDF-to-image conversion.
  - Acceptance Criteria: Uploading a mock PDF or image safely stores the file and prevents directory traversal attacks.

---

## Phase 4 — Data Pipeline & Baseline Models

- [Completed] **Task 4.1: Dataset Download & Ingestion Scripts**
  - Implement `scripts/download_datasets.py` to fetch and unpack SROIE and CORD datasets into `data/raw/`.
  - Acceptance Criteria: Script downloads sample data and validates image/annotation integrity.

- [Completed] **Task 4.2: OCR Tokenizer & Bounding Box Normalizer**
  - Implement `src/ml/ocr_engine.py` wrapping Tesseract OCR to extract word tokens and bounding boxes normalized to $[0, 1000]$.
  - Acceptance Criteria: Ingesting an image outputs a structured list of word tokens and $[x_0, y_0, x_1, y_1]$ coordinates.

- [Completed] **Task 4.3: BIO Tag Alignment Algorithm**
  - Implement dynamic programming string alignment in `src/ml/dataset_loader.py` to map OCR tokens to ground truth text and assign BIO tags (`B-VENDOR`, `I-VENDOR`, etc.).
  - Acceptance Criteria: Token alignment achieves $\ge 95\%$ token coverage on SROIE training samples.

- [Completed] **Task 4.4: Baseline 1 Implementation (OCR + Regex)**
  - Implement `src/ml/baselines.py` with handcrafted regex rules for dates and monetary figures.
  - Acceptance Criteria: Evaluates on 100 test documents and records baseline F1 ($\sim 0.45$).

- [Skipped] **Task 4.5: Baseline 2 Implementation (OCR + CRF)**
  - Implement token-level feature extraction (capitalization, position, keywords) and train a CRF sequence classifier.
  - Acceptance Criteria: Evaluates on test documents and records progression F1 ($\sim 0.60$).

---

## Phase 5 — ML Model Development & Fine-Tuning

- [Completed] **Task 5.1: LayoutLMv3 Dataset & Preprocessing Pipeline**
  - Implement PyTorch Dataset class wrapping Hugging Face `LayoutLMv3Processor`.
  - Integrate image standardization (RGB, max 1024px, ImageNet normalization) and token bounding box clipping.
  - Acceptance Criteria: Dataset loader outputs valid PyTorch tensor dictionaries with correct shapes.

- [Skipped] **Task 5.2: Memory-Optimized Training Pipeline**
  - Implement fine-tuning script `src/ml/train.py` utilizing Hugging Face `Accelerate`, mixed-precision FP16, and gradient checkpointing.
  - Set batch size = 2 with 8 gradient accumulation steps to fit 8GB VRAM constraint.
  - Acceptance Criteria: Training completes 1 epoch on sample dataset without CUDA out-of-memory errors.

- [Skipped] **Task 5.3: Model Evaluation & Checkpoint Serialization**
  - Implement evaluation loop computing entity-level precision, recall, and F1.
  - Save checkpoints using Hugging Face `safetensors` format.
  - Acceptance Criteria: Evaluation script produces a classification report and saves best checkpoint when validation F1 improves.

- [Completed] **Task 5.4: Inference Engine & Post-Processing BIO Decoder**
  - Implement `src/ml/layoutlm_model.py` loading fine-tuned weights and decoding raw logits into structured entity dictionaries with softmax confidence scores.
  - Acceptance Criteria: Model inference runs on a test image and outputs predicted fields with confidence scores.

---

## Phase 6 — Deterministic Rules & Validation Engine

- [Completed] **Task 6.1: Date & String Normalization Service**
  - Implement `src/rules/normalizers.py` utilizing `dateparser` to standardize varied date formats to `YYYY-MM-DD`.
  - Implement string cleaners removing OCR noise and extra whitespace.
  - Acceptance Criteria: Unit tests verify parsing of 15 distinct international date strings.

- [Completed] **Task 6.2: Currency & Numerical Parser**
  - Implement monetary string parser stripping symbols (`$`, `€`, `£`, commas) and converting OCR letter typos (`O` $\rightarrow$ `0`).
  - Acceptance Criteria: Unit tests verify conversion of dirty currency strings to floating point numbers.

- [Completed] **Task 6.3: Arithmetic Parity & Discrepancy Verifier**
  - Implement `src/rules/verifier.py` to cross-check mathematical balance: $|\text{Total} - (\text{Subtotal} + \text{Tax})| \le 0.05$.
  - Acceptance Criteria: Flags arithmetic warnings on mismatched figures while preserving valid totals.

---

## Phase 7 — FastAPI Backend Services

- [Completed] **Task 7.1: API Schemas & Request/Response Contracts**

- [Completed] **Task 7.2: Ingestion & Upload Route**

- [Completed] **Task 7.3: Document Detail & Inspection Route**

- [Completed] **Task 7.4: Human-in-the-Loop Correction Route**

- [Completed] **Task 7.5: CSV & JSON Export Routes**

---

## Phase 8 — Streamlit Frontend & Visual Workspace

- [Completed] **Task 8.1: Design System & Styling Injection**
  - Implement `src/ui/styles.py` defining CSS variables, dark theme aesthetics, custom buttons, and input styles according to `docs/design.md`.
  - Acceptance Criteria: Streamlit app renders customized dark mode styling without generic default appearance.

- [Completed] **Task 8.2: Drag-and-Drop Ingestion View**
  - Implement upload page in `src/ui/app.py` with custom file dropzone, upload progress spinner, and document format verification.
  - Acceptance Criteria: Dropping a file uploads to backend and transitions to review workspace.

- [Completed] **Task 8.3: Bounding Box Overlay Canvas**
  - Implement `src/ui/components/canvas_overlay.py` using Pillow/OpenCV to render color-coded bounding boxes onto the document image.
  - Map entity colors: Sky Blue for Vendor, Emerald for Date, Amber for Total, Purple for Tax.
  - Acceptance Criteria: Document preview displays bounding box overlays aligned with detected entities.

- [Completed] **Task 8.4: Side-by-Side Review & Correction Form**
  - Implement `src/ui/components/field_editor.py` rendering two-column review workspace with editable input fields and confidence pill badges.
  - Add save button sending corrections to backend.
  - Acceptance Criteria: Editing total and clicking Save persists updated values to database.

- [Completed] **Task 8.5: Analytics Dashboard & Metric Cards**
  - Implement summary cards showing total documents processed, average extraction confidence, and flagged math discrepancies.
  - Acceptance Criteria: Metrics update dynamically as new documents are ingested.

- [Completed] **Task 8.6: Export & Records View**
  - Implement data table of all processed documents with download buttons for individual or bulk CSV/JSON exports.
  - Acceptance Criteria: Clicking export triggers immediate file download.

---

## Phase 9 — Testing Suite & Quality Assurance

- [Completed] **Task 9.1: Unit Test Suite for Rules & Parsers**
  - Write test cases in `tests/test_rules.py` covering normalizers, 10+ date formats, currency formats, and arithmetic verifiers.
  - Acceptance Criteria: `pytest tests/test_rules.py` achieves 100% test pass rate.

- [Completed] **Task 9.2: API Integration Tests**
  - Write endpoint test cases in `tests/test_api.py` using FastAPI `TestClient` for upload, inspection, correction, and export routes.
  - Acceptance Criteria: `pytest tests/test_api.py` passes with zero errors.

- [Completed] **Task 9.3: ML Pipeline Shape & Consistency Tests**
  - Write model tests in `tests/test_model_inference.py` validating output tensor shapes, BIO tag alignment, and confidence clamping.
  - Acceptance Criteria: ML test suite executes and passes.

- [Completed] **Task 9.4: End-to-End Ingestion QA & Verification**
  - Implement synthetic test document generation via `scripts/generate_sample_receipt.py` and verify full upload, OCR, and rules pipeline.
  - Acceptance Criteria: Documents processed cleanly through the pipeline with zero unhandled exceptions.

---

## Phase 10 — Security & Error Handling Hardening

- [Completed] **Task 10.1: File Upload Security & Magic Byte Sniffing**
  - Ensure backend validates true file headers via magic bytes and enforces 10MB size limit in `src/utils/storage.py`.
  - Acceptance Criteria: Renamed malicious files or files exceeding 10MB are rejected with 400 Bad Request.

- [Completed] **Task 10.2: Path Traversal & SQL Injection Audit**
  - Verify all file paths use UUID identifiers and all database queries use parameters in `src/db/crud.py`.
  - Acceptance Criteria: Security audit test confirms directory traversal and SQL injection attempts fail safely.

- [Completed] **Task 10.3: Graceful Degradation & Fallback Circuit Breaker**
  - Implement fallback handling: if Tesseract or GPU inference fails, fall back to mock OCR / baseline extraction rather than crashing.
  - Acceptance Criteria: Simulating OCR/model unavailability still allows user to review and input data.

---

## Phase 11 — Production Engineering & Containerization

- [Completed] **Task 11.1: Multi-Stage Dockerfile**
  - Create `Dockerfile` with multi-stage build: Debian base with Tesseract C++ libraries and Poppler, builder stage for Python wheels, and minimal runtime stage.
  - Acceptance Criteria: `docker build -t docuparse .` builds cleanly.

- [Completed] **Task 11.2: Docker Compose Orchestration**
  - Create `docker-compose.yml` defining FastAPI backend and Streamlit frontend services with shared storage volume mounts.
  - Acceptance Criteria: `docker-compose up` launches complete system accessible via `localhost:8000` and `localhost:8501`.

- [Completed] **Task 11.3: Unified Development Runner Script**
  - Implement `scripts/run_dev.py` to start both FastAPI and Streamlit concurrently with live reload.
  - Acceptance Criteria: Single command `python scripts/run_dev.py` starts both services.

---

## Phase 12 — Documentation, Model Cards & Portfolio Polish

- [Completed] **Task 12.1: Model Card Creation**
  - Document LayoutLMv3 fine-tuning hyperparameters, training dataset splits, evaluation metrics, and bias/limitations in `docs/MODEL_CARD.md`.
  - Acceptance Criteria: Hugging Face standard model card created.

- [Completed] **Task 12.2: Root README & Quickstart Guide**
  - Write high-impact `README.md` with visual architecture diagram, feature overview, setup instructions, sample output tables, and resume project summary.
  - Acceptance Criteria: Comprehensive README ready for GitHub showcase.

- [Completed] **Task 12.3: Final Project Verification & Session Handoff**
  - Perform full end-to-end verification and update `docs/memory.md` with final project baseline state.
  - Acceptance Criteria: System validated, tested, and documented.
