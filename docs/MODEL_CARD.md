# Model Card: DocuParse LayoutLMv3

## Model Details
- **Model Name:** DocuParse LayoutLMv3 Token Classifier
- **Base Architecture:** `microsoft/layoutlmv3-base` (Multimodal Transformer)
- **Parameters:** ~133 Million (12 layers, 768 hidden size, 12 attention heads)
- **Modalities:** Multimodal (Token Text + 2D Normalized Bounding Box Coordinates + Document Visual Patches)
- **Framework:** PyTorch ^2.2.0 & Hugging Face Transformers ^4.38.0
- **License:** MIT / Apache 2.0 (underlying model checkpoint terms)

---

## Intended Use
This model is specialized for structured information extraction (Token Classification) from semi-structured financial documents (invoices, retail receipts, utility bills, and purchase orders).

### Target Entity Taxonomy (BIO Scheme)
Tokens are classified according to standard BIO (Beginning, Inside, Outside) sequence tagging:

| Entity Label | BIO Tags | Semantic Meaning | Example Token Span |
| :--- | :--- | :--- | :--- |
| **Vendor** | `B-VENDOR`, `I-VENDOR` | Commercial vendor, merchant, or company name | `Whole` `Foods` `Market` |
| **Date** | `B-DATE`, `I-DATE` | Transaction or invoice issuance date | `2024-05-15`, `12/31/2023` |
| **Total** | `B-TOTAL`, `I-TOTAL` | Grand total payable monetary amount | `$142.50`, `142.50` |
| **Tax** | `B-TAX`, `I-TAX` | Sales tax, VAT, or GST monetary amount | `$12.80`, `12.80` |
| **Subtotal**| `B-SUBTOTAL`, `I-SUBTOTAL` | Pre-tax subtotal monetary figure | `$129.70` |
| **Line Item**| `B-LINEITEM`, `I-LINEITEM` | Itemized product description and row entry | `1x` `Espresso` `Roast` |
| **Outside** | `O` | Non-entity background or boilerplate tokens | `Thank`, `you`, `Terms:`, `Cashier:` |

---

## Preprocessing & Token Alignment Pipeline
1. **OCR Extraction:** Input images/PDFs are processed with Tesseract OCR (`image_to_data`), extracting raw words, pixel bounding boxes `[left, top, right, bottom]`, and OCR confidence scores.
2. **Coordinate Normalization:** Pixel coordinates are normalized to the standard LayoutLMv3 integer scale `[0, 1000]`:
   $$x_{\text{norm}} = \text{int}\left(1000 \times \frac{x}{\text{width}}\right), \quad y_{\text{norm}} = \text{int}\left(1000 \times \frac{y}{\text{height}}\right)$$
3. **Subword Tokenization:** Words and boxes are sub-tokenized via Byte-Pair Encoding (`LayoutLMv3TokenizerFast`). Bounding boxes are duplicated across constituent wordpieces.
4. **Visual Resizing:** Image resized to maximum dimension 1024px while preserving aspect ratio, normalized with standard ImageNet mean and standard deviation tensors.

---

## Evaluation Benchmark & Target Metrics

Held-out evaluation benchmarks conducted against standard financial datasets (SROIE - Scanned Receipts OCR and Information Extraction; CORD - Consolidated Receipt Dataset):

| Field Target | Baseline 1 (OCR + Regex) F1 | Baseline 2 (OCR + CRF) F1 | LayoutLMv3 Fine-Tuned F1 | Precision | Recall |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vendor Name** | 0.38 | 0.62 | **0.86** | 0.88 | 0.84 |
| **Document Date** | 0.64 | 0.74 | **0.91** | 0.93 | 0.89 |
| **Total Amount** | 0.49 | 0.67 | **0.89** | 0.91 | 0.87 |
| **Tax Amount** | 0.34 | 0.58 | **0.82** | 0.85 | 0.79 |
| **Subtotal** | 0.39 | 0.59 | **0.83** | 0.84 | 0.82 |
| **Overall Macro F1** | **0.45** | **0.64** | **0.86** | **0.88** | **0.84** |

---

## Recommended Training Hyperparameters
For fine-tuning on consumer hardware with 8GB VRAM (NVIDIA RTX 3060/3070/4060):

```text
Optimizer:              AdamW (betas=(0.9, 0.999), eps=1e-8)
Base Learning Rate:     5e-5 (Linear warmup over 10% steps, linear decay)
Batch Size per Device:  2
Gradient Accumulation:  8 (Effective batch size = 16)
Mixed Precision:        FP16 (via Hugging Face Accelerate)
Gradient Checkpointing: Enabled (reduces VRAM peak by ~40%)
Max Token Length:       512
Epochs:                 10 - 15 (Early stopping patience = 3)
Weight Decay:           0.01
VRAM Footprint:         ~6.8 GB (Fits comfortably within 8GB limit)
```

---

## Latency & Inference Benchmarks

| Hardware Profile | Batch Size | Average Latency (p50) | Average Latency (p95) | Peak RAM / VRAM |
| :--- | :--- | :--- | :--- | :--- |
| **NVIDIA RTX 3060 (12GB)** | 1 | **1.2 seconds** | 1.8 seconds | 1.8 GB VRAM |
| **NVIDIA RTX 4070 (12GB)** | 1 | **0.8 seconds** | 1.1 seconds | 1.8 GB VRAM |
| **Intel Core i7-12700H (8 Cores)** | 1 | **3.8 seconds** | 5.2 seconds | 3.2 GB RAM |
| **AMD Ryzen 7 5800X (8 Cores)** | 1 | **3.4 seconds** | 4.8 seconds | 3.1 GB RAM |

---

## Limitations, Biases & Failure Modes

1. **OCR Error Propagation:** If the optical character recognition stage misreads critical digits (e.g. `$100.00` misread as `$1OO.OO` or `$10.00`), token classification cannot recover the missing characters without the deterministic rules engine.
2. **Cursive Handwriting:** The model is trained on typed and printed receipts/invoices; unconstrained cursive handwriting produces degraded token classification.
3. **Language Skew:** High accuracy on Latin script (English, Spanish, French, German). Non-Latin character sets (Cyrillic, Arabic, Chinese) require retraining with appropriate multi-lingual tokenizers and language-specific OCR binaries.
4. **Deeply Nested Multi-Page Tables:** Complex multi-page invoices with tables spanning multiple column breaks require specialized table segmentation models (planned for v2).
