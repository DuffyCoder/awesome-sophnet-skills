---
name: sophnet-image-ocr
description: OCR text and table extraction from images and PDF using SophNet API. Supports local files and URLs; PDFs are converted page-by-page (low resource), results merged, temp images deleted.
---

# Image / PDF OCR (SophNet API)

Extract text and tables from **images** or **PDF** using the SophNet API.
Supports local image/PDF files and direct URLs, returning Markdown-formatted output.
- **PDF**：多页 PDF 按页转成图片（低 DPI 以节省内存），逐页调用 OCR 后合并结果，并自动删除缓存的临时图片。

## Image Path Resolution

**Important:** When users upload images via webchat or other channels, Moltbot saves them to `media/inbound/images/` in the workspace. The system prompt includes media understanding logs that show the resolved absolute path.

Look for logs like:
```
[Media Understanding] Resolved relative path: "media/inbound/images/xxx.jpg" -> "/absolute/path/to/workspace/media/inbound/images/xxx.jpg"
```

## Quick Start

Run OCR on an image or PDF:
```bash
uv run {baseDir}/scripts/ocr.py <image-or-pdf-path-or-url>
```

This will:
- **Image**：Convert local images to base64, call PaddleOCR-VL API, output Markdown.
- **PDF**：Create a temp dir → render each page to PNG (150 DPI, low resource) → OCR each page → merge text with page markers → delete temp images and temp dir.

## Usage Examples

**Local image file:**
```bash
uv run {baseDir}/scripts/ocr.py /path/to/image.jpg
uv run {baseDir}/scripts/ocr.py media/inbound/images/uploaded_image.png
```

**Local PDF (multi-page supported):**
```bash
uv run {baseDir}/scripts/ocr.py /path/to/document.pdf
```

**URL (image or PDF):**
```bash
uv run {baseDir}/scripts/ocr.py https://example.com/image.jpg
uv run {baseDir}/scripts/ocr.py https://example.com/doc.pdf
```

**Custom options:**
```bash
uv run {baseDir}/scripts/ocr.py <image> \
  --model PaddleOCR-VL-0.9B \
  --no-prettify-markdown \
  --show-formula-number
```

## Script Options

- `<image-or-pdf-path-or-url>` (required): Local image/PDF path or HTTP/HTTPS URL
- `--model` (optional): Model to use. Default: `PaddleOCR-VL-0.9B`
- `--prettify-markdown` / `--no-prettify-markdown` (optional): Format output as Markdown. Default: enabled
- `--show-formula-number` / `--no-show-formula-number` (optional): Show formula numbering. Default: disabled

## Output Contract

The script outputs:
- **Success**: Markdown-formatted text with tables (stdout)
- **Error**: Error message to stderr

## Workflow

**Image：**
1. Input validation (file path or URL)
2. Convert local files to base64 data URLs
3. Call SophNet OCR API (timeout: 60s)
4. Parse and return Markdown output

**PDF：**
1. Detect PDF (by path/URL extension)
2. Create temp directory；若为 URL 则先下载 PDF 到 temp
3. 使用 PyMuPDF 按页渲染为 PNG（150 DPI，低内存），逐页：OCR → 追加结果 → 删除该页临时图
4. 合并各页文本（带「第 N 页」分隔），删除 temp 目录
5. 输出合并后的 Markdown

## Agent Usage

When extracting text/tables from images or PDF for users:

1. Run the OCR script:
   ```bash
   uv run {baseDir}/scripts/ocr.py <image-or-pdf-path>
   ```
2. Capture the stdout output
3. Present the extracted text/tables to the user
4. If the file is a Moltbot-uploaded image, check `media/inbound/images/` for the path
5. PDF 会逐页识别并合并输出，临时图片会在完成后自动删除

## Common Errors

- `Unsupported file type: ...` → Ensure the file is a valid image format (PDF 单独支持，不经过此检查)
- `文件不存在` / 下载 PDF 失败 → 检查路径或 URL 是否可访问
- `PDF 处理错误` → 确认已安装 pymupdf、PDF 未损坏

## API Details

**Endpoint:** `https://www.sophnet.com/api/open-apis/projects/easyllms/image-ocr`
**Model:** `PaddleOCR-VL-0.9B`
**Request timeout:** 60 seconds

**PDF 依赖：** 需安装 `pymupdf`（pyproject.toml 已声明）；PDF 按 150 DPI 转图以兼顾清晰度与低内存。

## Supported Input Formats

- **PDF**：本地 `.pdf` 或 URL 指向的 PDF；多页时按页转图（150 DPI）后识别，结果合并，临时图片自动删除
- **Image**：JPEG/JPG、PNG、GIF、WebP、BMP 及其他 `image/*` MIME 类型

## Real Example

**Image:**
```bash
uv run {baseDir}/scripts/ocr.py /path/to/document_with_tables.jpg
```

**PDF（多页会带页码分隔）：**
```bash
uv run {baseDir}/scripts/ocr.py /path/to/report.pdf
```

Output (Markdown，PDF 多页示例):
```markdown
--- 第 1 页 ---

| Name | Age | Occupation |
|------|-----|------------|
| John | 30  | Engineer   |

--- 第 2 页 ---

This document contains important information about the team structure...
```

**Request timeout:**
Check your network connection. The script uses a 60-second timeout.

**Empty output:**
Verify the image contains readable text. Some images may not have extractable content.

**Base64 conversion issues:**
Ensure local file paths are correct and the file exists.