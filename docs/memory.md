# Project Memory & Knowledge Base

## Current Status

```text
Project:         DocuParse AI — Intelligent Document Understanding for Financial Records
Current Phase:   Phase 9 — Testing Suite & Quality Assurance
Current Task:    Final QA and End-to-End verification.
Overall Status:  Phase 8 UI Complete. System is ready for E2E testing.
Last Updated:    2026-09-24
```

---

## Product Context

DocuParse AI is an end-to-end, local-first document intelligence system engineered to extract structured, validated data from invoices, receipts, and purchase orders. It combines spatial token extraction via Tesseract OCR with multimodal deep learning (`microsoft/layoutlmv3-base`) and deterministic mathematical guardrails (date standardizer, currency cleaner, Subtotal + Tax = Total verifier). A side-by-side Streamlit interface presents document bounding box overlays, confidence indicators, and inline correction forms, with export to RFC-compliant CSV and structured JSON.

---

## Current MVP Scope

1. **Document Ingestion:** Ingests `.png`, `.jpg`, `.jpeg`, and single-page `.pdf` files up to 10MB.
2. **Field Extraction (5 Core Targets):**
   - Vendor / Company Name
   - Document / Invoice Date
   - Total Amount
   - Tax / VAT Amount
   - Line Items (itemized array with descriptions and amounts)
3. **Multimodal Inference:** Fine-tuned `LayoutLMv3-base` model processing tokens, 2D coordinates normalized to $[0, 1000]$, and resized document images.
4. **Validation Guardrails:** Date normalization to `YYYY-MM-DD`, currency stripping/formatting, and mathematical balance verification.
5. **Interactive Review UI:** Side-by-side view with visual bounding box highlights and editable correction inputs.
6. **Data Export:** Individual and bulk export to CSV and JSON.
7. **Local Persistence:** Embedded SQLite database operating in Write-Ahead Logging (WAL) mode for concurrency.

---

## Important Technical Decisions

### Decision: LayoutLMv3-base Multimodal Transformer
- **Date:** 2026-09-24
- **Decision:** Select `microsoft/layoutlmv3-base` (86M parameters) as the primary ML model architecture for document token classification.
- **Reason:** LayoutLMv3 jointly models text tokens, visual patches, and 2D spatial layouts, capturing invoice layout semantics where spatial proximity dictates meaning (e.g., "Total" keyword situated adjacent to the monetary sum).
- **Alternatives Considered:** 
  - *OCR + Regex:* Baseline achieves only $\sim 0.45$ F1 due to layout fragility.
  - *Donut-base:* 300M parameters, caused Out-of-Memory (OOM) errors during training on 8GB consumer GPUs.
  - *Commercial Cloud LLM (GPT-4o Vision):* Violates local privacy requirements and incurs recurring per-page API costs.
- **Consequences:** Requires fine-tuning on SROIE/CORD datasets and memory optimizations (mixed-precision FP16, gradient checkpointing) to train within 8GB VRAM.

### Decision: FastAPI Backend + Streamlit Frontend Decoupling
- **Date:** 2026-09-24
- **Decision:** Separate the application into a FastAPI REST backend (port 8000) and a Streamlit interactive frontend (port 8501).
- **Reason:** Provides clean separation of concerns. FastAPI handles file upload sanitization, async ML pipelines, and data validation; Streamlit handles rapid reactive UI rendering, bounding box visualization, and human verification without requiring complex React/Vite build toolchains.
- **Alternatives Considered:** 
  - *Monolithic Streamlit app:* Couples ML inference and database queries directly into UI scripts, causing re-execution slowdowns on UI interactions.
  - *Next.js + React:* Higher engineering overhead for an MVP where rapid ML demonstration and local-first execution are paramount.
- **Consequences:** Requires managing two lightweight processes (orchestrated via `scripts/run_dev.py` or Docker Compose).

### Decision: SQLite Persistence with WAL Mode
- **Date:** 2026-09-24
- **Decision:** Use local embedded SQLite configured with `PRAGMA journal_mode = WAL;`.
- **Reason:** Zero configuration, serverless, self-contained, and preserves 100% data locality. WAL mode allows concurrent readers (Streamlit UI) while FastAPI writes incoming records.
- **Alternatives Considered:** PostgreSQL (introduces external service dependency), flat JSON files (lacks ACID transactions and indexing).
- **Consequences:** Single-node local storage; future multi-tenant cloud versions will migrate to PostgreSQL.

### Decision: Deterministic Post-Processing Validation Layer
- **Date:** 2026-09-24
- **Decision:** Route all raw transformer predictions through deterministic business rules (`dateparser`, regex amount normalizers, mathematical balance checker).
- **Reason:** Pure neural network outputs frequently suffer from small character errors (e.g., OCR `O` vs `0`) or unnormalized dates (`12/03/24` vs `2024-03-12`). Deterministic rules correct $> 30\%$ of extraction errors before human review.
- **Alternatives Considered:** Relying strictly on raw model output (forces excessive manual operator corrections).
- **Consequences:** Requires comprehensive unit test suite covering date formats and currency strings.

---

## Architecture Changes

### 2026-09-24 — Initial System Baseline Established
- **Previous:** None (uninitialized workspace).
- **New:** Established 6-document source of truth (`PRD.md`, `architecture.md`, `rules.md`, `design.md`, `task.md`, `memory.md`).
- **Reason:** Execution of Step 1 in Vibe Coding Workflow to establish complete specifications prior to writing code.
- **Impact:** Architectural boundaries, schema models, and feature scopes are now formally defined.

---

## Major Bugs

*None recorded. Project is in specification phase prior to implementation.*

---

## Current Known Issues

*None recorded.*

---

## Open Decisions

1. **OCR Engine Fallback:** Evaluate EasyOCR or PaddleOCR alongside Tesseract if real-world camera scans show severe OCR degradation. Tesseract remains the primary MVP baseline.
2. **Deployment Preview Method:** Confirm whether external demonstration requires Ngrok tunneling or Docker container export.

---

## Important Constraints

1. **Hardware VRAM Limit:** Fine-tuning must fit within an 8GB VRAM constraint (achieved via batch size 2, gradient accumulation 8, FP16, and gradient checkpointing).
2. **Local Binaries:** Host environment requires Tesseract OCR C++ libraries (`tesseract-ocr`) and Poppler (`poppler-utils` for PDF conversion).
3. **Single-Page Scope for MVP:** First page processing only for multi-page documents; multi-page table reconciliation deferred to v2.

---

## Dependencies & Integrations

- **FastAPI (^0.110.0):** REST API framework
- **Streamlit (^1.32.0):** Interactive UI
- **PyTorch (^2.2.0):** Deep learning tensors
- **Transformers (^4.38.0):** Hugging Face LayoutLMv3
- **Accelerate (^0.27.0):** Memory optimization
- **PyTesseract (^0.3.10):** Tesseract OCR bridge
- **Pydantic (^2.6.0):** Schema validation
- **Pillow (^10.2.0) & OpenCV (^4.9.0):** Image processing & canvas rendering
- **Dateparser (^1.2.0):** Multilingual date standardization
- **Pandas (^2.2.0):** Data manipulation & CSV exports
- **SQLite 3:** Embedded database

---

## Deployment Information

- **Local Development:**
  - FastAPI: `http://localhost:8000` (OpenAPI Swagger at `http://localhost:8000/docs`)
  - Streamlit UI: `http://localhost:8501`
- **Docker Production:** Multi-stage Docker image packaging Tesseract C++ binaries and Python virtual environment.

---

## Recent Changes

- **2026-09-24:** Generated the complete initial 6-document architecture and specification suite in `docs/`:
  - `docs/PRD.md`: Full product requirements, personas, MoSCoW prioritization, and success metrics.
  - `docs/architecture.md`: System components, data flows, database schemas, and folder structure.
  - `docs/rules.md`: Engineering rulebook, AI coding guidelines, security policies, and Definition of Done.
  - `docs/design.md`: Visual design system, dark palette HEX tokens, typography, and component specifications.
  - `docs/task.md`: Master 12-phase sequential task breakdown with acceptance criteria.
  - `docs/memory.md`: Project knowledge base, decision logs, and handoff state.

---

## Session Handoff

### Completed in this Session
- Executed **Phase 3 (Database & Storage Layer)**.
- Implemented `src/db/database.py` utilizing SQLite with Write-Ahead Logging (WAL) for concurrency.
- Built ORM schemas in `src/db/models.py` (`Document`, `Extraction`, `LineItem`, `Correction`).
- Created CRUD utility functions in `src/db/crud.py`.
- Implemented secure file storage utilities in `src/utils/storage.py` and validated via Pytest integration.
- Initialized local DB with `scripts/init_db.py`.

### Completed in this Session
- Executed **Phase 8 (Streamlit Frontend & Visual Workspace)**.
- Completed **Task 8.1**: Configured vibrant dark mode styling in `src/ui/styles.py`.
- Completed **Task 8.2**: Built document upload component mapping to FastAPI.
- Completed **Task 8.3**: Designed `canvas_overlay.py` utilizing Pillow to render coordinate-accurate bounding boxes over the original document.
- Completed **Task 8.4**: Built two-column interactive review UI in `src/ui/components/field_editor.py` syncing corrections to the backend.
- Completed **Task 8.5 & 8.6**: Added Analytics and Export tools tab in `src/ui/app.py`.

### Currently Being Worked On
- Starting **Phase 9 (Testing Suite & Quality Assurance)**.

### What Should Happen Next
1. The user can start the FastAPI and Streamlit servers simultaneously to preview the MVP application end-to-end.
2. Execute final QA validation.
