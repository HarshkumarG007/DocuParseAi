# Model Card: DocuParse LayoutLMv3

## Model Details
- **Architecture:** LayoutLMv3-base (Microsoft)
- **Parameters:** ~133 Million
- **Modality:** Text + Bounding Box Coordinates (2D) + Image (Optional)
- **Framework:** PyTorch & Hugging Face Transformers

## Intended Use
This model is intended for structured data extraction from financial documents (receipts and invoices). It operates via Token Classification, mapping OCR tokens to predefined semantic BIO tags:
- `B-VENDOR` / `I-VENDOR`
- `B-DATE` / `I-DATE`
- `B-TOTAL` / `I-TOTAL`
- `B-TAX` / `I-TAX`
- `B-SUBTOTAL` / `I-SUBTOTAL`

## Preprocessing Requirements
1. Raw documents must be processed through Tesseract OCR.
2. Bounding boxes must be extracted at the token level.
3. Coordinates must be normalized to a `[0, 1000]` scale relative to image dimensions before passing to the `LayoutLMv3Processor`.

## Training Data & Limitations
- Baseline model uses zero-shot token representations from the Hugging Face hub.
- Full fine-tuning is designed for the SROIE (Scanned Receipts OCR and Information Extraction) and CORD datasets.
- **Limitations:** The model struggles with handwritten annotations and highly unstructured document layouts (e.g., deeply nested tables).

## Hardware Constraints
- Fine-tuning requires at least 8GB of VRAM (RTX 3070+).
- Inference can run on CPU, but processing times increase to ~1.5 - 3 seconds per page depending on document complexity.
