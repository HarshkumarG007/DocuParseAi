# Design System & UI Specifications

## Document Details
- **Project Name:** DocuParse AI — Intelligent Document Understanding for Financial Records
- **Version:** 1.0.0-MVP
- **Status:** Approved / Design Baseline
- **Date:** 2026-09-24
- **Lead Designer / Architect:** Senior Full-Stack Developer & UI/UX Architect

---

## 1. Design Philosophy

DocuParse AI's visual personality is **Precision-Engineered, Data-Dense, and High-Trust**. 

Financial document extraction is an operational, high-stakes domain where operators must verify sensitive numbers quickly without eye fatigue or visual ambiguity. The interface prioritizes:
- **Calm, High-Contrast Aesthetics:** A deep slate / dark-mode first design palette that minimizes visual glare during prolonged data entry sessions, with a clean light-mode fallback.
- **Clarity Over Decoration:** Elimination of frivolous decorative widgets in favor of high-legibility tabular displays, crisp bounding box highlights, and immediate semantic validation indicators.
- **Immediate Spatial Context:** Simultaneous display of the original source receipt and extracted fields to enable effortless human-in-the-loop verification.
- **Transparent AI Confidence:** Visualizing model certainty at a glance through calibrated color pills (Green, Amber, Red).

---

## 2. Design Principles

1. **Clarity Over Decoration:** Every visual element must serve an operational purpose: identifying fields, signaling errors, or facilitating exports.
2. **Side-by-Side Spatial Grounding:** Extracted data must never be presented in isolation; the source image must remain visible alongside the extracted fields.
3. **Multi-Modal Color Feedback:** Color alone must never convey state. Status tags must always combine distinct colors with descriptive labels or icons.
4. **Forgiving Inline Editing:** Every prediction made by the machine learning model must be directly editable with a single click, providing immediate visual confirmation when corrected.
5. **Zero Latency Feedback:** All compute-intensive actions (OCR scanning, model inference, export compilation) must provide clear progress indicators or spinners.

---

## 3. Color System

All colors are defined as exact HEX values optimized for WCAG 2.2 AA contrast ratios ($> 4.5:1$ for normal text, $> 3:1$ for large text and interactive components).

### Dark Theme Palette (Primary Default)

```text
Background:          #0F172A  (Slate 900 - Deep charcoal background)
Surface:             #1E293B  (Slate 800 - Elevated cards, sidebars, containers)
Surface Elevated:    #334155  (Slate 700 - Hover cards, active rows, dialogs)
Border:              #334155  (Slate 700 - Subtle component borders)
Border Focused:      #6366F1  (Indigo 500 - Active input focus ring)
Text Primary:        #F8FAFC  (Slate 50 - High contrast text)
Text Secondary:      #94A3B8  (Slate 400 - Labels, timestamps, secondary notes)
Text Muted:          #64748B  (Slate 500 - Placeholders, disabled text)
```

### Brand & Accent Colors

```text
Primary:             #6366F1  (Indigo 500 - Primary actions, active highlights)
Primary Hover:       #4F46E5  (Indigo 600 - Hover state)
Primary Active:      #4338CA  (Indigo 700 - Pressed state)
Primary Foreground:  #FFFFFF  (Pure White - High contrast button text)

Secondary:           #0EA5E9  (Sky 500 - Informational badges, secondary buttons)
Secondary Hover:     #0284C7  (Sky 600)
Secondary Foreground:#FFFFFF
```

### Semantic Status Colors

```text
Success (High Conf): #10B981  (Emerald 500 - Confidence >= 0.85, Verified)
Success Background:  #064E3B  (Emerald 900 / 30% alpha)
Success Text:        #34D399  (Emerald 400)

Warning (Mid Conf):  #F59E0B  (Amber 500 - Confidence 0.60 - 0.84, Review needed)
Warning Background:  #78350F  (Amber 900 / 30% alpha)
Warning Text:        #FBBF24  (Amber 400)

Error (Discrepancy): #EF4444  (Red 500 - Discrepancy detected, Confidence < 0.60)
Error Background:    #7F1D1D  (Red 900 / 30% alpha)
Error Text:          #F87171  (Red 400)

Info:                #38BDF8  (Sky 400 - Processing notices, tips)
Info Background:     #0C4A6E  (Sky 900 / 30% alpha)
Info Text:           #7DD3FC  (Sky 300)
```

### Bounding Box Overlay Colors by Entity Type

Each financial entity is assigned a distinct color channel to ensure immediate recognition when overlaid on document scans:

```text
Vendor / Company:    #38BDF8  (Sky Blue   - Border: #0284C7, Fill: rgba(56, 189, 248, 0.25))
Document Date:       #34D399  (Emerald    - Border: #059669, Fill: rgba(52, 211, 153, 0.25))
Total Amount:        #FBBF24  (Amber Gold - Border: #D97706, Fill: rgba(251, 191, 36, 0.25))
Tax / VAT:           #A78BFA  (Purple     - Border: #7C3AED, Fill: rgba(167, 139, 250, 0.25))
Line Items / Rows:   #F472B6  (Rose Pink  - Border: #DB2777, Fill: rgba(244, 114, 182, 0.20))
```

---

## 4. Typography

### Font Families
- **Primary Interface Font:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, `Roboto`, `sans-serif`.
- **Financial & Monospace Font:** `JetBrains Mono`, `"Fira Code"`, `Consolas`, `monospace` (used for all numeric figures, currency amounts, dates, and JSON payloads to ensure tabular digit alignment).

### Typography Scale

| Token | Size | Line Height | Weight | Letter Spacing | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display H1** | 28px (1.75rem) | 36px | 700 (Bold) | -0.02em | Application title, top headers |
| **Heading H2** | 20px (1.25rem) | 28px | 600 (Semibold)| -0.01em | Section headers (Review, Ingest) |
| **Heading H3** | 16px (1.00rem) | 24px | 600 (Semibold)| 0.00em | Card titles, field group labels |
| **Body Standard** | 14px (0.875rem)| 20px | 400 (Regular) | 0.00em | Form inputs, descriptions, table cells |
| **Body Medium** | 14px (0.875rem)| 20px | 500 (Medium)  | 0.00em | Input labels, button text |
| **Monospace Num**| 14px (0.875rem)| 20px | 500 (Medium)  | 0.02em | Currency figures, bounding box tags |
| **Small / Caption**| 12px (0.75rem)| 16px | 400 (Regular) | 0.01em | Timestamps, confidence tags, notes |

---

## 5. Spacing System

A base-4 modular spacing scale ensures visual rhythm across cards, forms, and layouts:

```text
--space-1:   4px    (Micro padding, badge vertical spacing)
--space-2:   8px    (Input internal padding, gap between icon & text)
--space-3:   12px   (Form item gaps, card sub-headers)
--space-4:   16px   (Standard card padding, default grid gap)
--space-6:   24px   (Major section padding, side-by-side gutter)
--space-8:   32px   (Top-level container padding)
--space-12:  48px   (Page margins, empty state vertical space)
--space-16:  64px   (Hero spacing)
```

---

## 6. Border Radius & Elevation

### Border Radius
```text
--radius-sm:   4px    (Badges, tags, inner tooltips)
--radius-md:   8px    (Buttons, form text inputs, selects)
--radius-lg:   12px   (Cards, review canvas panels, modal containers)
--radius-full: 9999px (Pill badges, status indicators, avatar chips)
```

### Elevation & Box Shadows
```text
--shadow-sm:  0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md:  0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.15);
--shadow-lg:  0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.2);
--shadow-glow:0 0 0 3px rgba(99, 102, 241, 0.4); /* Used for input active focus */
```

---

## 7. Component Specifications

### 7.1 Buttons

```text
Primary Button:
- Background: #6366F1
- Text: #FFFFFF, 14px Medium
- Padding: 10px 20px
- Radius: 8px
- Hover: Background #4F46E5, transition 150ms ease
- Active: Background #4338CA

Secondary Button:
- Background: #334155
- Text: #F8FAFC, 14px Medium
- Border: 1px solid #475569
- Hover: Background #475569

Destructive Button:
- Background: #7F1D1D
- Text: #FCA5A5, 14px Medium
- Border: 1px solid #991B1B
- Hover: Background #991B1B

Disabled State:
- Background: #1E293B
- Text: #64748B
- Border: 1px solid #334155
- Cursor: not-allowed, Opacity: 0.6
```

### 7.2 Form Inputs & Text Fields

```text
Standard Input / Date Picker / Number Field:
- Background: #0F172A
- Border: 1px solid #334155
- Text: #F8FAFC, 14px Regular
- Padding: 10px 14px
- Radius: 8px
- Focus: Border #6366F1, Box-Shadow: 0 0 0 3px rgba(99, 102, 241, 0.25)
- Error State: Border #EF4444, Box-Shadow: 0 0 0 3px rgba(239, 68, 68, 0.25)
```

### 7.3 File Uploader Dropzone

- **Container:** Dashed border (2px dashed `#475569`), background `#1E293B`, radius 12px.
- **Drag-Over State:** Border transitions to solid `#6366F1`, background tint `rgba(99, 102, 241, 0.1)`.
- **Text:** "Drag & drop your receipt, invoice, or PO here (PNG, JPG, PDF up to 10MB)" in `#94A3B8`.
- **Upload Progress:** Linear progress bar in `#6366F1` with percentage counter.

### 7.4 Confidence Status Badges (Pills)

- **High Confidence ($\ge 0.85$):**
  - Text: `✓ 94% High Confidence`
  - Style: Background `#064E3B`, Text `#34D399`, Border `1px solid #059669`, Radius `9999px`, Padding `2px 10px`.
- **Medium Confidence ($0.60 - 0.84$):**
  - Text: `⚠ 72% Review Needed`
  - Style: Background `#78350F`, Text `#FBBF24`, Border `1px solid #D97706`, Radius `9999px`, Padding `2px 10px`.
- **Low Confidence / Discrepancy ($< 0.60$):**
  - Text: `✕ 45% Check Math`
  - Style: Background `#7F1D1D`, Text `#F87171`, Border `1px solid #EF4444`, Radius `9999px`, Padding `2px 10px`.

### 7.5 Side-by-Side Review Workspace

```text
┌─────────────────────────────────────────┬─────────────────────────────────────────┐
│ DOCUMENT IMAGE CANVAS                   │ EXTRACTED ENTITIES & CORRECTION FORM   │
│                                         │                                         │
│  ┌───────────────────────────────────┐  │ Vendor Name                             │
│  │ [Sky BBox: Starbucks Coffee]      │  │ [ Starbucks Coffee             ] [98%]  │
│  │                                   │  │                                         │
│  │ [Green BBox: 2026-03-14]          │  │ Invoice Date                            │
│  │                                   │  │ [ 2026-03-14                   ] [94%]  │
│  │ Line Items:                       │  │                                         │
│  │ - 1x Latte           $4.75        │  │ Total Amount                            │
│  │ - 1x Croissant       $3.50        │  │ [ $8.25                        ] [99%]  │
│  │                                   │  │                                         │
│  │ [Amber BBox: Total $8.25]         │  │ Tax / VAT                               │
│  │                                   │  │ [ $0.68                        ] [88%]  │
│  └───────────────────────────────────┘  │                                         │
│                                         │ [ ✓ Save Corrections ]  [ ⤓ Export CSV ] │
└─────────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 8. Navigation & App Layout

The Streamlit UI organizes operational workflows into clean sidebar navigation tabs:

1. **📥 Ingestion & Processing:** Drag-and-drop file upload, instant OCR progress indicator, and batch processing trigger.
2. **🔍 Review & Verification:** The primary side-by-side workspace showing document image bounding boxes, confidence badges, math verification warnings, and inline correction inputs.
3. **📊 Analytics Dashboard:** Aggregate metrics showing total documents parsed, average confidence distribution, and flagged discrepancy rate.
4. **💾 Export & Records:** Filterable data table of all processed documents with one-click CSV and JSON export buttons.

---

## 9. Responsive Layout Behavior

### Breakpoints
- **Desktop ($\ge 1024\text{px}$):** Default side-by-side two-column grid. Left column ($50\%$ width) houses the document zoom/pan canvas with rendered bounding boxes. Right column ($50\%$ width) contains the editable verification form.
- **Tablet ($640\text{px} - 1023\text{px}$):** Proportional two-column split with smaller canvas scaling or stacked top-and-bottom view with toggle buttons ("View Document" / "View Data").
- **Mobile ($< 640\text{px}$):** Single vertical column. Full-width receipt preview thumbnail expandable on click, followed by stacked entity cards and export buttons.

---

## 10. Motion & Interaction

- **Duration:** Standard micro-interactions (hover, border transitions, badge color shifts) use a fast duration of **$150\text{ms}$** to maintain snappy operational velocity.
- **Easing:** `cubic-bezier(0.4, 0, 0.2, 1)` (standard ease-in-out).
- **Reduced Motion:** If user system settings indicate `prefers-reduced-motion: reduce`, all transitions are disabled (`transition: none !important`), rendering instantaneous state changes.
