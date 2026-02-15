---
name: sophnet-image-ocr
description: OCR text and table extraction from images using SophNet API. Automatically handles local files and URLs. Integrates with sophnet-key skill for API key management.
---

# Image OCR (SophNet API)

Extract text and tables from images using the SophNet API.
Supports local image files and direct URLs, returning Markdown-formatted output.

## Image Path Resolution

**Important:** When users upload images via webchat or other channels, Moltbot saves them to `media/inbound/images/` in the workspace. The system prompt includes media understanding logs that show the resolved absolute path.

Look for logs like:
```
[Media Understanding] Resolved relative path: "media/inbound/images/xxx.jpg" -> "/absolute/path/to/workspace/media/inbound/images/xxx.jpg"
```

## Quick Start

Run OCR on an image (absolute path):
```bash
uv run {baseDir}/scripts/ocr.py <image-path-or-url>
```

This will:
1. Check for `SOPH_API_KEY` (via sophnet-key skill or environment variable)
2. Convert local images to base64 automatically
3. Call the PaddleOCR-VL API
4. Output Markdown-formatted text with tables

## Usage Examples

**Local image file:**
```bash
uv run {baseDir}/scripts/ocr.py /path/to/image.jpg
uv run {baseDir}/scripts/ocr.py media/inbound/images/uploaded_image.png
```

**URL:**
```bash
uv run {baseDir}/scripts/ocr.py https://example.com/image.jpg
```

**Custom options:**
```bash
uv run {baseDir}/scripts/ocr.py <image> \
  --model PaddleOCR-VL-0.9B \
  --no-prettify-markdown \
  --show-formula-number
```

## Script Options

- `<image-path-or-url>` (required): Local file path or HTTP/HTTPS URL
- `--model` (optional): Model to use. Default: `PaddleOCR-VL-0.9B`
- `--prettify-markdown` / `--no-prettify-markdown` (optional): Format output as Markdown. Default: enabled
- `--show-formula-number` / `--no-show-formula-number` (optional): Show formula numbering. Default: disabled
- `--api-key` (optional): Override SOPH_API_KEY environment variable

## Output Contract

The script outputs:
- **Success**: Markdown-formatted text with tables (stdout)
- **Error**: Error message to stderr

## Workflow

1. Input validation (file path or URL)
2. API key resolution via sophnet-key skill
3. Convert local files to base64 data URLs
4. Call SophNet OCR API (timeout: 60s)
5. Parse and return Markdown output

## Agent Usage

When extracting text/tables from images for users:

1. Run the OCR script:
   ```bash
   uv run {baseDir}/scripts/ocr.py <image-path>
   ```
2. Capture the stdout output
3. Present the extracted text/tables to the user
4. If the image is a Moltbot-uploaded file, check `media/inbound/images/` for the path

## API Key Management

API Key is automatically resolved in this order:
1. Environment variable `SOPH_API_KEY` (highest priority)
2. Via `sophnet-key` skill (reads from Moltbot config)

If no key is found, the script will guide you through setup using the sophnet-key skill.

## Common Errors

- `Error: SOPH_API_KEY environment variable not set.` → Run `sophnet-key` skill to configure
- `HTTP请求失败，状态码: ...` → Check network connection and API key validity
- `API Error (code ...): ...` → Check API response details and key permissions
- `Unsupported file type: ...` → Ensure the file is a valid image format

## API Details

**Endpoint:** `https://www.sophnet.com/api/open-apis/projects/easyllms/image-ocr`
**Model:** `PaddleOCR-VL-0.9B`
**Request timeout:** 60 seconds

## Supported Image Formats

- JPEG/JPG
- PNG
- GIF
- WebP
- BMP
- Other MIME types starting with `image/`

## Real Example

Command:
```bash
uv run {baseDir}/scripts/ocr.py /path/to/document_with_tables.jpg
```

Output (Markdown):
```markdown
| Name | Age | Occupation |
|------|-----|------------|
| John | 30  | Engineer   |
| Mary | 25  | Designer   |

This document contains important information about the team structure...
```

## Troubleshooting

**Key not found:**
```bash
# Check environment variable
echo $SOPH_API_KEY

# Or run sophnet-key skill to configure
```

**Request timeout:**
Check your network connection. The script uses a 60-second timeout.

**Empty output:**
Verify the image contains readable text. Some images may not have extractable content.

**Base64 conversion issues:**
Ensure local file paths are correct and the file exists.