---
name: sophnet-pdf
description: 'Use this skill for ALL PDF tasks — creating new PDFs from scratch (reports, whitepapers, invoices, certificates, resumes, charts, presentations), generating complex styled PDF documents with tables/charts/images/multi-page layouts, as well as reading/extracting text and tables, merging/splitting, rotating pages, adding watermarks, filling forms, encrypting/decrypting, extracting images, and OCR. This skill provides a managed Python environment (uv + reportlab/pypdf/pdfplumber) that handles dependencies automatically. Always use this skill whenever the user mentions PDF, .pdf, or asks to create, generate, produce, design, or build any PDF document. Do NOT write standalone Python scripts outside this skill — use the skill''s uv environment instead. CRITICAL CJK RULE: When creating PDFs with Chinese/Japanese/Korean text via reportlab, you MUST register STSong-Light font AND call addMapping() — default Helvetica renders CJK as black boxes. See the ''reportlab - Create PDFs'' section in this SKILL.md for the mandatory setup code. For watermarks, ONLY use Shape.insert_text(morph=...) + show_pdf_page overlay — never use add_text_annot or add_freetext_annot.'
---

# PDF Processing Guide

## MANDATORY: Working Directory

**EVERY command in this skill MUST be executed from THIS skill's directory.** Before running ANY command — Python or bash script — you MUST `cd` into this skill's directory first. Determine the absolute path of this `SKILL.md` file and use its parent directory.

```bash
SKILL_DIR="<absolute-path-to-this-skills-sophnet-pdf-directory>"
cd "$SKILL_DIR"
```

**NEVER run commands from the repository root or any other directory.** If you do, `uv run` won't find `pyproject.toml`, and `python` won't have access to required packages.

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see REFERENCE.md. If you need to fill out a PDF form, read FORMS.md and follow its instructions.

### ⚠️ CJK Text in PDFs — READ FIRST

**If the PDF will contain ANY Chinese/Japanese/Korean text** (including titles, body text, table cells, or watermarks), you MUST handle CJK fonts correctly:

- **reportlab**: Default fonts (`Helvetica`, `Times-Roman`) render CJK as **black boxes (█)**. You MUST register `STSong-Light` and call `addMapping()` before creating any content. See the "reportlab - Create PDFs" section for the exact setup code.
- **PyMuPDF (fitz)**: Use `fontname="china-s"` for `insert_text()` / `insert_textbox()`. This is built-in and requires no extra setup.
- **Rule of thumb**: When in doubt, always use CJK-safe fonts. `STSong-Light` (reportlab) and `china-s` (PyMuPDF) both handle mixed CJK+Latin text correctly.

## Python Runtime (uv)

**CRITICAL: All Python execution in this skill MUST use `uv run --project .` from the skill directory. NEVER use bare `python3`, `python`, or `pip install` directly — the required packages (pdfplumber, reportlab, pypdf, etc.) are ONLY available inside the uv virtual environment defined by this skill's `pyproject.toml`. Direct `python3` will fail with ModuleNotFoundError.**

**IMPORTANT: Only use libraries available in this skill's pyproject.toml (reportlab, pypdf, pdfplumber, pillow, pdf2image, pymupdf). Do NOT import matplotlib, numpy, pandas, or other packages not listed — they will cause ModuleNotFoundError. For charts/graphs, use `reportlab.graphics.charts` (VerticalBarChart, HorizontalBarChart, Pie, etc.) instead of matplotlib.**

First, ensure the environment is set up (run once per session):

```bash
cd "$SKILL_DIR"
bash scripts/ensure_uv_env.sh
```

Then ALL Python commands must use this prefix:

```bash
cd "$SKILL_DIR" && uv run --project . python <script-or-module>
```

This applies to both the provided scripts AND any inline Python code you write. For inline code, use:

```bash
cd "$SKILL_DIR" && uv run --project . python -c "import pdfplumber; ..."
```

## Delivery

Local PDF creation/editing/analysis does not require any Sophnet API key.

**IMPORTANT: After creating or modifying a PDF, ALWAYS upload it and return the download URL to the user.** This is the default behavior — do not skip the upload step.

```bash
bash scripts/upload_file.sh --file <absolute-path-to-pdf>
```

Upload command output contract:

- `FILE_PATH=<absolute-path>`
- `UPLOAD_STATUS=uploaded|skipped`
- `DOWNLOAD_URL=<https://...>` (present only when uploaded)

Delivery rules:

- **ALWAYS call `scripts/upload_file.sh` after producing a PDF file**, then return the `DOWNLOAD_URL` to the user.
- If `UPLOAD_STATUS=uploaded`, return the exact `DOWNLOAD_URL` value to the user as a clickable link.
- If `UPLOAD_STATUS=skipped` (missing API key), return `FILE_PATH` instead of failing the whole task.
- Keep URL output logic independent inside `sophnet-pdf/scripts`. Do not call other skills' upload scripts.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### PyMuPDF (fitz) - Text Search & Replace

**This is the ONLY method for replacing text in existing PDFs. Do NOT fall back to nano-pdf, pdftotext, tesseract, or any external CLI tool — use PyMuPDF exclusively.**

**CRITICAL FONT RULES:**
- NEVER use the original PDF's embedded font names (e.g. `Unnamed-T3`, `NotoSansCJKsc-Regular`, `LiberationSans`) with `insert_text()` — they are embedded fonts and will cause `Exception: need font file or buffer`.
- Always use `page.search_for()` to locate text (it works across spans, unlike iterating `get_text("dict")` spans which may split multi-word terms).
- Use the **fallback font picker** below to choose a suitable built-in font.

**Built-in font aliases (Latin):** `helv` (Helvetica), `heit` (Helvetica-Bold), `tiro` (Times-Roman), `tibo` (Times-Bold), `cour` (Courier), `cobo` (Courier-Bold).

**Built-in CJK font aliases:** `china-s` (Simplified Chinese), `china-t` (Traditional Chinese), `japan` (Japanese), `korea` (Korean). These also render Latin characters correctly.

#### Find & Replace Text in PDF (Complete Example)

```python
import fitz  # PyMuPDF

# --- Font fallback logic ---
BUILTIN_FONTS = {"helv","heit","tiro","tibo","tibi","toit","cour","cobo","cobi","cout","symb","zadb"}
CJK_FONTS = {"china-s","china-ss","china-t","china-ts","japan","japan-s","korea","korea-s"}

def has_cjk(text):
    """Check if text contains CJK characters."""
    return any("\u4e00" <= c <= "\u9fff" or "\u3000" <= c <= "\u303f" for c in text)

def pick_font(original_font, text):
    """Pick a built-in font. Falls back from the original embedded font name."""
    if original_font in BUILTIN_FONTS or original_font in CJK_FONTS:
        return original_font
    if has_cjk(text):
        return "china-s"  # handles both CJK and Latin
    lower = original_font.lower()
    if "bold" in lower:
        return "heit"
    if "mono" in lower or "courier" in lower or "code" in lower:
        return "cour"
    return "helv"

def get_span_info(page, rect):
    """Get font size, font name, and color from the span overlapping rect."""
    for block in page.get_text("dict")["blocks"]:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if fitz.Rect(span["bbox"]).intersects(rect):
                    return span["size"], span["font"], span.get("color", 0)
    return 12, "helv", 0

# --- Main replacement logic ---
search_terms = ["OldText", "Old Text"]  # all variants to search for
replacement  = "NewText"

doc = fitz.open("input.pdf")

for page in doc:
    # Step 1: Find all instances using search_for (works across spans)
    hits = []
    for term in search_terms:
        for rect in page.search_for(term):
            size, font, color = get_span_info(page, rect)
            hits.append({"rect": rect, "size": size, "font": font, "color": color})

    # Step 2: Redact (erase) old text
    for h in hits:
        page.add_redact_annot(h["rect"], fill=(1, 1, 1))
    page.apply_redactions()

    # Step 3: Insert replacement text with fallback font
    for h in hits:
        font = pick_font(h["font"], replacement)
        c = h["color"]
        rgb = (((c>>16)&0xFF)/255, ((c>>8)&0xFF)/255, (c&0xFF)/255) if isinstance(c, int) else (0,0,0)
        page.insert_text(
            (h["rect"].x0, h["rect"].y0 + h["size"] * 0.85),
            replacement,
            fontname=font,
            fontsize=h["size"],
            color=rgb,
        )

doc.save("output.pdf", garbage=4, deflate=True)
```

**After replacement, always verify** by extracting text from the output PDF:

```python
doc2 = fitz.open("output.pdf")
for i, p in enumerate(doc2):
    text = p.get_text()
    old_count = text.lower().count("oldtext")
    new_count = text.lower().count("newtext")
    print(f"Page {i+1}: OldText={old_count}, NewText={new_count}")
```

**Notes:**
- PDF text replacement is inherently imperfect — PDFs are presentation-focused, not text-edit-focused.
- The replacement font may look slightly different from the original embedded font. This is expected.
- `china-s` is the best fallback for mixed CJK+Latin text; `helv` for Latin-only text.

### PyMuPDF (fitz) - Image Operations

**Use PyMuPDF for ALL image operations in existing PDFs.** Key APIs:
- `page.insert_image(rect, filename=...)` — insert a new image
- `page.replace_image(xref, filename=...)` — replace an existing image in-place (keeps original rect)
- `page.delete_image(xref)` — remove an image (replaces with 1×1 transparent pixel)
- `page.get_images(full=True)` — list images on a page (returns xref, etc.)
- `page.get_image_info(xrefs=True)` — list images with bounding box info

**CRITICAL: Always use `page.get_image_info(xrefs=True)` (not `get_images`) when you need the on-page bounding box of each image.**

#### Insert Image into Existing PDF

```python
import fitz

doc = fitz.open("input.pdf")
page = doc[0]

# Define target rectangle (x0, y0, x1, y1) — image will be scaled to fit
# To center horizontally with 50% page width:
pw = page.rect.width
img_w = pw * 0.5
# Load image to get aspect ratio
img = fitz.Pixmap("image.png")
aspect = img.width / img.height
img_h = img_w / aspect
x0 = (pw - img_w) / 2
y0 = 700  # vertical position

rect = fitz.Rect(x0, y0, x0 + img_w, y0 + img_h)
page.insert_image(rect, filename="image.png")
doc.save("output.pdf")
```

#### Replace an Existing Image

```python
import fitz

doc = fitz.open("input.pdf")
page = doc[0]

# Find the image to replace
images = page.get_images(full=True)
target_xref = images[0][0]  # xref of the first image

# Replace it — the new image fills the SAME rect as the original
page.replace_image(target_xref, filename="new_image.png")
doc.save("output.pdf")
```

**Note:** `replace_image` keeps the original bounding box. The new image is scaled to fit.

#### Modify Image Layout (Reposition / Resize)

```python
import fitz

doc = fitz.open("input.pdf")
page = doc[0]

# Get image placements with bounding boxes
img_info = page.get_image_info(xrefs=True)
target = img_info[0]  # first image
xref = target["xref"]
orig_rect = fitz.Rect(target["bbox"])

# Extract original image bytes
pix = fitz.Pixmap(doc, xref)
img_bytes = pix.tobytes("png")

# Delete the original (replaces with 1x1 transparent pixel)
page.delete_image(xref)

# Re-insert at new position/size (e.g. 70% size, centered)
pw = page.rect.width
new_w = orig_rect.width * 0.7
new_h = orig_rect.height * 0.7
new_x0 = (pw - new_w) / 2
new_rect = fitz.Rect(new_x0, orig_rect.y0, new_x0 + new_w, orig_rect.y0 + new_h)
page.insert_image(new_rect, stream=img_bytes)

doc.save("output.pdf", garbage=4, deflate=True)
```

**Notes on image operations:**
- `delete_image` replaces the image data with a 1×1 transparent pixel (the page reference remains but is invisible). This is normal PyMuPDF behavior.
- For layout changes: extract → delete → re-insert at new rect. Do NOT try `doc.update_image()` (does not exist).
- `insert_image` accepts `filename=` (file path) or `stream=` (bytes). Use `stream=` when re-inserting extracted images.
- Use `garbage=4, deflate=True` in `doc.save()` to clean up unused objects and compress.

### pypdf - Basic Operations

#### Merge PDFs

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF

```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata

```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages

```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables

```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction

```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

> ⚠️ **If the PDF contains ANY Chinese/Japanese/Korean text, you MUST follow the CJK rules below. Skipping them causes black boxes (█) or crash errors.**

**FORBIDDEN patterns (these ALL break CJK rendering):**
- ❌ Using `Helvetica`, `Times-Roman`, or `Courier` fonts for CJK text → renders as **black boxes (█)**
- ❌ Registering `STSong-Light` without calling `addMapping()` → `Paragraph()` crashes with `ValueError: Can't map determine family/bold/italic for stsong-light`
- ❌ Using `<font face="STSong-Light">` in Paragraph XML without `addMapping()` → same crash
- ❌ Setting `style.fontName = "STSong-Light"` without `addMapping()` → same crash

**CJK font setup (MUST be at the top of EVERY script with CJK text):**

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.fonts import addMapping

# Step 1: Register the CJK font
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
# Step 2: MANDATORY — register font family mapping (without this Paragraph() crashes)
addMapping("STSong-Light", 0, 0, "STSong-Light")  # normal
addMapping("STSong-Light", 1, 0, "STSong-Light")  # bold
addMapping("STSong-Light", 0, 1, "STSong-Light")  # italic
addMapping("STSong-Light", 1, 1, "STSong-Light")  # bold+italic
```

**After setup, use `"STSong-Light"` as the font EVERYWHERE** — Canvas (`c.setFont`), ParagraphStyle (`fontName=`), TableStyle (`("FONTNAME", ...)`). `STSong-Light` renders both CJK and Latin correctly.

**Alternative**: If reportlab gives trouble, use **PyMuPDF** with `fontname="china-s"` to create PDFs with CJK text (see PyMuPDF section).

#### Complete CJK PDF Template (Platypus — copy-paste this)

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.fonts import addMapping

# ===== CJK FONT SETUP (MANDATORY) =====
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
addMapping("STSong-Light", 0, 0, "STSong-Light")
addMapping("STSong-Light", 1, 0, "STSong-Light")
addMapping("STSong-Light", 0, 1, "STSong-Light")
addMapping("STSong-Light", 1, 1, "STSong-Light")

# ===== STYLES (all use STSong-Light) =====
styles = getSampleStyleSheet()
cn_title = ParagraphStyle("CNTitle", parent=styles["Title"],
    fontName="STSong-Light", fontSize=28, alignment=1, spaceAfter=20)
cn_body = ParagraphStyle("CNBody", parent=styles["Normal"],
    fontName="STSong-Light", fontSize=12, leading=18)

# ===== BUILD CONTENT =====
story = []
story.append(Paragraph("标题文字", cn_title))        # <-- change title here
story.append(Spacer(1, 12))
story.append(Paragraph("正文内容...", cn_body))       # <-- change body here
story.append(PageBreak())

# Table with CJK content
data = [
    ["列1", "列2", "列3"],                            # <-- change table data here
    ["数据A", "数据B", "数据C"],
]
table = Table(data, colWidths=[150, 150, 150])
table.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),  # ALL cells use STSong-Light
    ("FONTSIZE", (0, 0), (-1, 0), 14),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
story.append(table)

doc = SimpleDocTemplate("output.pdf", pagesize=A4)
doc.build(story)
```

#### Basic PDF Creation (Canvas API)

**Note:** This example includes CJK font setup. Even if your content is English-only, including the STSong-Light setup is harmless and avoids CJK issues if content later changes.

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# Always register CJK font — safe even for English-only content
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

c = canvas.Canvas("output.pdf", pagesize=A4)
w, h = A4

c.setFont("STSong-Light", 24)
c.drawCentredString(w / 2, h - 80, "Title Here")

c.setFont("STSong-Light", 12)
c.drawString(72, h - 130, "Body text here. 中文也可以正确显示。")

c.save()
```

#### Create PDF with Multiple Pages (Platypus)

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.fonts import addMapping

# ===== MANDATORY CJK FONT SETUP =====
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
addMapping("STSong-Light", 0, 0, "STSong-Light")
addMapping("STSong-Light", 1, 0, "STSong-Light")
addMapping("STSong-Light", 0, 1, "STSong-Light")
addMapping("STSong-Light", 1, 1, "STSong-Light")

styles = getSampleStyleSheet()
# Override default styles to use STSong-Light
cn_style = ParagraphStyle("CNNormal", parent=styles["Normal"], fontName="STSong-Light")
cn_title = ParagraphStyle("CNTitle", parent=styles["Title"], fontName="STSong-Light")
cn_h1 = ParagraphStyle("CNH1", parent=styles["Heading1"], fontName="STSong-Light")

doc = SimpleDocTemplate("report.pdf", pagesize=A4)
story = []

story.append(Paragraph("Report Title", cn_title))
story.append(Spacer(1, 12))
story.append(Paragraph("This is the body of the report. " * 20, cn_style))
story.append(PageBreak())

story.append(Paragraph("Page 2", cn_h1))
story.append(Paragraph("Content for page 2", cn_style))

doc.build(story)
```

#### Subscripts and Superscripts

**IMPORTANT**: Never use Unicode subscript/superscript characters (₀₁₂₃₄₅₆₇₈₉, ⁰¹²³⁴⁵⁶⁷⁸⁹) in ReportLab PDFs. The built-in fonts do not include these glyphs, causing them to render as solid black boxes.

Instead, use ReportLab's XML markup tags in Paragraph objects:

```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# Subscripts: use <sub> tag
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# Superscripts: use <super> tag
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

For canvas-drawn text (not Paragraph objects), manually adjust font the size and position rather than using Unicode subscripts/superscripts.

## Command-Line Tools

### pdftotext (poppler-utils)

```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf

```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)

```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs

```python
# Requires: uv add pytesseract (pdf2image is already in this skill env)
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark (PyMuPDF — the ONLY correct method)

> ⚠️ **MANDATORY**: Copy-paste the template below. Do NOT invent your own watermark approach.

**FORBIDDEN APIs** (these ALL produce broken or removable watermarks):
- ❌ `page.add_text_annot()` — creates sticky-note pop-ups, not visible text
- ❌ `page.add_freetext_annot()` — creates annotations that any PDF editor can delete; `fontsize` keyword may crash
- ❌ `page.insert_text(rotate=45)` — only accepts 0/90/180/270; raises `ValueError: bad rotate value`
- ❌ `TextWriter.write_text(morph=...)` — text positioning is unreliable, renders off-center
- ❌ `page.rect.ratio` — does NOT exist, raises `AttributeError`

**The ONLY correct method is Shape overlay**: create a temp PDF page, draw text with `Shape.insert_text(morph=...)`, then merge with `show_pdf_page`.

#### Complete Watermark Template (copy-paste this)

```python
import fitz

doc = fitz.open("input.pdf")

for page in doc:
    r = page.rect
    cx, cy = r.width / 2, r.height / 2

    # 1. Create a temporary overlay page (same size as original)
    wm_doc = fitz.open()
    wm_page = wm_doc.new_page(width=r.width, height=r.height)

    # 2. Calculate text dimensions
    font = fitz.Font("helv")  # Use "china-s" for CJK watermark text
    text = "CONFIDENTIAL"     # <-- change watermark text here
    fs = 55                   # <-- change font size here
    text_width = font.text_length(text, fontsize=fs)

    # 3. Draw rotated text via Shape (the ONLY reliable rotation method)
    shape = wm_page.new_shape()
    shape.insert_text(
        fitz.Point(cx - text_width / 2, cy + fs * 0.35),   # center text on page
        text,
        fontname="helv",       # Use "china-s" for CJK
        fontsize=fs,
        color=(0.82, 0.82, 0.82),                          # light grey
        morph=(fitz.Point(cx, cy), fitz.Matrix(45)),        # 45° diagonal rotation
    )
    shape.commit()

    # 4. Merge overlay onto original page (bakes watermark into content stream)
    page.show_pdf_page(r, wm_doc, 0, overlay=True)
    wm_doc.close()

# 5. Save THEN verify (do NOT access doc after save+close)
doc.save("watermarked.pdf", garbage=4, deflate=True)
doc.close()

# 6. Verify — open the SAVED file separately
doc2 = fitz.open("watermarked.pdf")
print(f"Pages: {len(doc2)}")
for i, p in enumerate(doc2):
    annots = list(p.annots()) if p.annots() else []
    print(f"Page {i+1}: annots={len(annots)} (should be 0)")
doc2.close()
```

**Key points:**
- The watermark is permanent — baked into the page content stream, not removable.
- Annotations count MUST be 0 after adding watermark. If > 0, you used the wrong API.
- `doc.close()` before any verification. Open the saved file as a new `fitz.open()` to verify.
- For **semi-transparent** effect: use a light color like `(0.82, 0.82, 0.82)` on white backgrounds.
- For CJK watermark text, use `fontname="china-s"` and `fitz.Font("china-s")`.

### Add Watermark (pypdf — alternative, requires pre-made watermark PDF)

```python
from pypdf import PdfReader, PdfWriter

# Load pre-existing watermark PDF
watermark = PdfReader("watermark.pdf").pages[0]

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images

```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task                       | Best Tool                       | Command/Code                                              |
| -------------------------- | ------------------------------- | --------------------------------------------------------- |
| Prepare Python environment | uv                              | `bash scripts/ensure_uv_env.sh`                           |
| **Find & replace text**    | **PyMuPDF (fitz)**              | **search_for + redact + insert_text (see above)**         |
| **Insert/replace images**  | **PyMuPDF (fitz)**              | **insert_image / replace_image / delete_image (see above)**|
| Merge PDFs                 | pypdf                           | `writer.add_page(page)`                                   |
| Split PDFs                 | pypdf                           | One page per file                                         |
| Extract text               | pdfplumber                      | `page.extract_text()`                                     |
| Extract tables             | pdfplumber                      | `page.extract_tables()`                                   |
| **Add watermark**          | **PyMuPDF (fitz)**              | **Shape.insert_text(morph=...) + show_pdf_page overlay**  |
| Create PDFs                | reportlab                       | Canvas or Platypus (CJK: register `STSong-Light` first)  |
| Command line merge         | qpdf                            | `qpdf --empty --pages ...`                                |
| OCR scanned PDFs           | pytesseract                     | Convert to image first                                    |
| Fill PDF forms             | pdf-lib or pypdf (see FORMS.md) | See FORMS.md                                              |
| Optional upload for URL    | upload script                   | `bash scripts/upload_file.sh --file /abs/path/output.pdf` |

## Dependencies

- `uv` - Python environment and dependency manager for this skill (`bash scripts/ensure_uv_env.sh`)
- `qpdf`, `pdftotext`, `pdftoppm` - optional command-line PDF tools
- `tesseract` - required for OCR workflows using `pytesseract`

## Next Steps

- For advanced pypdfium2 usage, see REFERENCE.md
- For JavaScript libraries (pdf-lib), see REFERENCE.md
- If you need to fill out a PDF form, follow the instructions in FORMS.md
- For troubleshooting guides, see REFERENCE.md
