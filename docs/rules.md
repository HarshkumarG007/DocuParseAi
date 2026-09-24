# Development Rules & AI Engineering Guidelines

## Document Details
- **Project Name:** DocuParse AI — Intelligent Document Understanding for Financial Records
- **Version:** 1.0.0-MVP
- **Status:** Active & Enforced
- **Date:** 2026-09-24
- **Authority:** Senior Full-Stack Developer & AI Systems Architect

---

## 1. Core Principles

The AI Assistant and any contributing developer must strictly obey these core principles during every development, debugging, and refactoring task:

1. **Zero Hallucination:** Never invent libraries, APIs, database fields, configuration flags, or execution results. If an API or variable is unknown, inspect the source code or state that information is missing.
2. **Requirement Fidelity:** Never silently alter product requirements, schema definitions, or feature boundaries.
3. **Dependency Discipline:** Never introduce new third-party dependencies without explicit rationale and alignment with the architecture document.
4. **Targeted Diffs:** Never rewrite unrelated files, refactor existing code merely for cosmetic preference, or alter working functions outside the scope of the assigned task.
5. **Architectural Consistency:** If an implementation requires modifying database schemas, API contracts, or system flows, you must update `docs/architecture.md` and `docs/memory.md` simultaneously.
6. **Zero Secrets in Code:** Never hard-code passwords, API tokens, local file paths with personal usernames, or private keys. Always use environment variables loaded from `.env`.
7. **Strict Validation:** Never bypass client-side or server-side validation for convenience. All data entering the system must be rigorously validated via Pydantic schemas.
8. **Explicit Error Handling:** Never silently catch and swallow exceptions with bare `except: pass`. All errors must be logged with context and returned as structured user feedback.
9. **Factual Integrity:** Never claim tests pass, services are running, or deployments succeeded unless they have actually been executed and verified in the environment.

---

## 2. Before Writing Code: Mandatory 9-Step Checklist

Before generating or modifying any application code, the AI must perform the following sequence:

1. **Read Relevant Documentation:** Review `docs/PRD.md`, `docs/architecture.md`, `docs/rules.md`, and `docs/memory.md`.
2. **Review Current Task:** Inspect `docs/task.md` to confirm the exact task and its stated acceptance criteria.
3. **Inspect Existing Files:** Use file-viewing tools to check existing implementations, utility functions, and imports in the target directory.
4. **Verify Dependencies:** Verify whether required packages are already declared in `requirements.txt` or `requirements-dev.txt`.
5. **Check for Duplicate Code:** Ensure the proposed logic does not already exist in a helper or utility module (`src/rules/normalizers.py`, `src/db/crud.py`, etc.).
6. **Analyze Side Effects:** Check downstream consumers (e.g., will modifying an API response schema break the Streamlit review UI?).
7. **Formulate Minimal Plan:** Design the smallest, cleanest change that completely solves the task.
8. **State Assumptions Clearly:** If any detail requires a low-risk assumption, state it explicitly in the explanation before writing code.
9. **Execute and Verify:** Write the code, run relevant unit tests or syntax checks, and record updates.

---

## 3. Task Discipline

- **Single-Task Execution:** Work strictly on the assigned task provided by the user. Do not preemptively begin tasks scheduled for future phases.
- **Scope Containment:** Do not bundle refactoring, reformatting, or "nice-to-have" features into an assigned bug fix or feature task.
- **Documentation Synchronization:** If a completed task completes a milestone or introduces an architectural adjustment, immediately update `docs/task.md` and `docs/memory.md`.

---

## 4. Technology Rules

### Approved Stack
- **Backend Framework:** FastAPI (`src/api/`)
- **Frontend Framework:** Streamlit (`src/ui/`)
- **Language:** Python 3.10+ (compatible with Python 3.9+)
- **ML Frameworks:** PyTorch, Hugging Face `transformers`, `accelerate`
- **OCR Engine:** Tesseract OCR via `pytesseract`
- **Database:** SQLite 3 with WAL mode enabled, accessed via SQLAlchemy Core / native SQLite3 parameterized statements
- **Data Validation:** Pydantic v2 schemas
- **Image Manipulation:** Pillow (PIL), OpenCV-Python (`cv2`)
- **Testing:** Pytest, HTTPX (FastAPI `TestClient`)
- **Linting & Formatting:** `ruff`, `black`

### Prohibited Technologies
- **No Heavy Client Build Frameworks in MVP:** Do not add Node.js/React/Vite dependencies to the MVP codebase unless an explicit architecture migration task is assigned.
- **No Cloud-Only SDKs:** Do not introduce AWS Boto3, Google Cloud Client Libraries, or Azure SDKs. The MVP is strictly local-first and zero-cloud.
- **No Unvetted Heavy LLM Frameworks:** Do not add LangChain or LlamaIndex for this structured token extraction task. We use direct Hugging Face `LayoutLMv3` inference.
- **No Non-Standard Databases:** Do not introduce MongoDB, Redis, or PostgreSQL dependencies into the MVP runtime.

---

## 5. Coding Standards

### Python & General Conventions
- Follow **PEP 8** style guidelines strictly.
- **Strict Typing:** All function signatures must include Python type hints for arguments and return values:
  ```python
  def normalize_currency(raw_amount: str) -> Optional[Decimal]:
      ...
  ```
- **Pydantic for Data Boundaries:** All HTTP payloads, database transfer objects, and ML output structures must inherit from `pydantic.BaseModel`.
- **Small, Focused Functions:** Functions should adhere to the Single Responsibility Principle and ideally not exceed 50 lines of code.
- **No Magic Numbers:** Replace unexplained numerical constants with descriptive constant variables (e.g., `MAX_IMAGE_DIMENSION = 1024`, `CONFIDENCE_THRESHOLD_HIGH = 0.85`).
- **Docstrings:** All public functions, classes, and API routers must have concise docstrings describing parameters, return values, and potential exceptions.

---

## 6. Frontend / Streamlit Rules

- **State Isolation:** All persistent UI states (e.g., selected document ID, active corrections, zoom level) must be stored in `st.session_state`. Never rely on global script variables.
- **Decoupled Business Logic:** The Streamlit UI must communicate with the backend exclusively via HTTP requests or modular service client functions. Do not write raw SQL queries or invoke ML transformer forward passes directly inside Streamlit view scripts.
- **Visual Feedback:** All asynchronous operations (uploading, running OCR, model inference, exporting) must be wrapped in `st.spinner()` or progress bars.
- **Graceful Empty & Error States:** If no documents exist in SQLite, render a clear empty state with instructions. If an API call fails, display an informative `st.error()` message without exposing raw stack traces.
- **Custom CSS Injections:** All custom CSS for dark/light themes and bounding-box styling must be centralized in `src/ui/styles.py` and applied via `st.markdown("<style>...</style>", unsafe_allow_html=True)`.

---

## 7. API Rules

- **Schema Enforcement:** Every FastAPI route must specify `response_model` and validate incoming parameters using Pydantic models.
- **Standard HTTP Semantics:**
  - `200 OK`: Successful retrieval or synchronous operation.
  - `201 Created`: Document successfully ingested and assigned an ID.
  - `400 Bad Request`: Invalid payload, unsupported image format, or malformed bounding box.
  - `404 Not Found`: Requested document ID does not exist in SQLite.
  - `413 Payload Too Large`: Upload payload exceeds strict 10MB memory safety ceiling.
  - `422 Unprocessable Entity`: Schema validation failure.
  - `500 Internal Server Error`: Masked internal server failure logged securely on the backend.
- **Path Traversal Protection:** Sanitize all incoming filenames. Never use raw client-supplied filenames in `os.path.join()`.
- **API Versioning:** All endpoints must be prefixed with `/api/v1/`.

---

## 8. Database Rules

- **Parameterized Queries:** Never construct SQL queries via string concatenation or f-strings. Always use parameterized queries to eliminate SQL injection vulnerabilities:
  ```python
  # CORRECT
  cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
  
  # PROHIBITED
  cursor.execute(f"SELECT * FROM documents WHERE id = '{document_id}'")
  ```
- **Concurrency Guard:** Always ensure `PRAGMA journal_mode = WAL;` is executed on database connection initialization to prevent database locks between FastAPI and Streamlit.
- **Schema Migrations:** Any table alteration must be scripted in a reproducible Python migration or initialization script (`src/db/database.py`).
- **Data Integrity:** Foreign keys must be enabled (`PRAGMA foreign_keys = ON;`). Deleting a document must cascade to its associated extractions, line items, and corrections.

---

## 9. Error Handling & Resilience

Every operation involving I/O, ML inference, or external binaries must implement comprehensive error handling:

1. **Loading State:** Provide responsive visual feedback to the user while inference is running.
2. **Safe Fallback on OCR Failure:** If Tesseract encounters an unreadable file or corrupted image header, return a structured 400 error indicating the file is unreadable.
3. **Safe Fallback on Model Failure:** If LayoutLMv3 fails (e.g., out of VRAM), catch the exception, log the full traceback to the server console, and return an error state that falls back to raw OCR text extraction so the user can manually input values.
4. **Validation Alerts vs. Hard Errors:** A failed mathematical check (e.g., Subtotal + Tax $\neq$ Total) must **not** abort the request. It must produce a valid response flagged with `has_validation_error = True` and a descriptive message so the human operator can review it.

---

## 10. Security Rules

- **File Upload Restrictions:**
  - Allowed MIME types: `image/jpeg`, `image/png`, `application/pdf`.
  - Check actual magic bytes via `python-magic` or PIL verification, not just the file extension.
  - Enforce a strict maximum file size of **10MB**.
- **No Arbitrary Code Execution:** Never use `eval()`, `exec()`, or unsafe `pickle.load()` on untrusted input or model weights. Use Hugging Face `safetensors` format for saving/loading fine-tuned checkpoints.
- **Information Masking:** Do not leak server file paths (e.g., `C:\Users\username\...`) in API error responses. Return standardized error codes and friendly messages.
- **Local Network Binding:** By default, development servers must bind to `127.0.0.1` unless running inside a Docker container where binding to `0.0.0.0` is required.

---

## 11. Accessibility Guidelines (WCAG 2.2 AA)

- **Color Contrast:** All UI text, badges, and button labels must maintain a contrast ratio of at least **4.5:1** against their background.
- **Non-Color Indicators:** Never rely solely on color to convey status. Accompany color indicators with descriptive text or icons:
  - Green + `[High Confidence / Validated]`
  - Amber + `[Review Recommended]`
  - Red + `[Discrepancy Detected]`
- **Keyboard Usability:** Ensure form inputs, review tabs, and save buttons are fully reachable and activatable via `Tab` and `Enter` keystrokes.
- **High-Contrast Bounding Boxes:** Document bounding box overlays must use high-visibility contrasting borders (2px solid) with semi-transparent fills so underlying receipt text remains legible.

---

## 12. Performance Budgets

- **End-to-End Latency:** Single-document processing (Upload $\rightarrow$ OCR $\rightarrow$ LayoutLMv3 $\rightarrow$ Validation $\rightarrow$ JSON response) must complete in:
  - GPU (NVIDIA RTX 3060/4060): $\le 3.0$ seconds.
  - Modern CPU (x86_64 8-core): $\le 8.0$ seconds.
- **Image Resizing Budget:** All incoming images must be resized so the longest side is $\le 1024$ pixels prior to OCR and transformer ingestion.
- **Model Memory Budget:**
  - Training / Fine-tuning VRAM: $\le 7.5$ GB (fits in 8GB consumer GPU).
  - Inference VRAM: $\le 2.0$ GB.
- **UI Responsiveness:** Streamlit page re-renders must complete in $< 200$ milliseconds once inference data is received.

---

## 13. Testing Rules

- **Execution Requirement:** Never report that tests passed unless you have explicitly run `pytest` via the terminal and observed green exit codes.
- **Unit Testing:**
  - Date normalization rules must be tested against at least 10 international date formats (`DD/MM/YYYY`, `MM/DD/YYYY`, `DD-Mon-YYYY`, etc.).
  - Currency normalization rules must be tested against varied currency symbols (`$`, `€`, `£`, commas, trailing decimals).
  - Mathematical verification logic must be tested with exact matches, allowable rounding tolerance ($\pm \$0.05$), and deliberate discrepancies.
- **API Testing:** Use FastAPI's `TestClient` to test all endpoints (`/upload`, `/{id}`, `/{id}/correct`, `/{id}/export`) with mock inputs and files.
- **Mocking External Binaries:** In unit test environments where Tesseract or a GPU is not installed, mock the OCR engine and model forward pass using clean mock fixtures (`tests/conftest.py`).

---

## 14. Definition of Done (DoD)

A development task is considered complete **only when all of the following conditions are met**:

1. [ ] The requested feature or bug fix works as specified in `docs/PRD.md` and `docs/architecture.md`.
2. [ ] All edge cases, invalid inputs, and error states are handled gracefully.
3. [ ] Code adheres strictly to PEP 8, includes type annotations, and passes linting without warnings.
4. [ ] Relevant unit or integration tests are written and pass via `pytest`.
5. [ ] No existing functionality or tests are broken.
6. [ ] Security implications (file validation, path traversal, SQL injection) have been verified.
7. [ ] Documentation in `docs/task.md` and `docs/memory.md` is updated to reflect the new state.
