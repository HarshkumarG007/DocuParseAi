# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-09-25

### 🚀 Initial Production Release

#### Added
- **Local-First Extraction Gateway:** Asynchronous FastAPI backend providing single-page receipt and invoice parsing with zero cloud data egress.
- **Pluggable Extraction Pipeline:** Router supporting both high-speed spatial regex heuristics (`EXTRACTION_ENGINE=regex`) and deep multimodal token classification via Microsoft's `LayoutLMv3-base` (`EXTRACTION_ENGINE=layoutlmv3`).
- **Deterministic Decimal Parity Engine:** High-precision accounting validation using Python's `decimal.Decimal` enforcing $|\text{Total} - (\text{Subtotal} + \text{Tax})| \le 0.05$ across a 3-state parity machine (`PASS`, `FAIL`, `UNVERIFIABLE`).
- **Document Lifecycle State Machine:** Strict processing states (`PROCESSING`, `PROCESSED`, `REVIEW_REQUIRED`, `FAILED`) with automatic flagging of mathematical discrepancies and low-confidence extractions ($< 0.70$).
- **Reproducible Evaluation Harness:** Standalone benchmarking CLI (`evaluation/evaluate.py`) calculating field-level Exact Match (EM), Token F1, Precision, and Recall with JSON report serialization (`evaluation/benchmark_report.json`).
- **Interactive Human-in-the-Loop Canvas:** Streamlit presentation interface featuring side-by-side document inspection, dynamic colored bounding box projection, confidence indicators, and inline correction forms.
- **Embedded Concurrent Storage:** SQLite 3 configured with Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) enabling non-blocking concurrent reads during document review.
- **Decoupled Exporters:** Modular export factory (`BaseExporter`) generating RFC 4180 itemized/summary CSVs and hierarchical JSON records.
- **Multi-Stage Containerization:** Production `Dockerfile` and `docker-compose.yml` packaging Debian base, Tesseract OCR C++ libraries, Poppler utilities, and volume-persisted storage.

#### Security
- **Chunked Ingestion Streaming:** 64 KB chunked upload processing with strict 10 MB ceiling and HTTP 413 Payload Too Large rejection to prevent memory-exhaustion Denial-of-Service (DoS) attacks.
- **Binary Signature Inspection:** Magic-byte sniffing (`FF D8 FF` for JPEG, `89 50 4E 47` for PNG) preventing spoofed file uploads.
- **Path Traversal Protection:** RFC 4122 UUIDv4 identifiers and sanitized file paths for all persisted assets.
- **Configurable CORS:** Restricted API access via `ALLOWED_ORIGINS` environment configuration.

#### Testing & Quality
- **Automated Verification:** 27 unit and integration tests across API, evaluation, database, rules, model inference, and storage with 100% pass rate.
- **Pre-flight Diagnostics:** Automated diagnostic utility (`scripts/diagnostics.py`) checking Python runtime, CUDA availability, and OCR binary health.

---
