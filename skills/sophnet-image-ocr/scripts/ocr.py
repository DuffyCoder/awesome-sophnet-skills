#!/usr/bin/env python3
"""
Image/PDF OCR utility for Sophnet PaddleOCR API.

Supports local image/PDF files and direct URLs.
PDF: multi-page PDFs are converted to images page-by-page (low DPI to save memory),
     each page is OCR'd, results merged; temporary images are deleted after use.
Returns Markdown-formatted text and table extraction results.
Base64 conversion is handled automatically for local files.
"""

import os
import sys
import base64
import mimetypes
import json
import tempfile
import shutil
import requests
import sophnet_tools

# API Configuration
API_URL = "https://www.sophnet.com/api/open-apis/projects/easyllms/image-ocr"
API_KEY = sophnet_tools.get_api_key()

if not API_KEY:
    print("Error: SOPH_API_KEY environment variable not set.", file=sys.stderr)
    print("Please set it with: export SOPH_API_KEY='your-key'", file=sys.stderr)
    print("Or obtain a key using the sophnet-key skill.", file=sys.stderr)
    sys.exit(1)


def image_to_base64(image_path):
    """Convert a local image file to base64 data URL."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported file type: {image_path}")

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{image_data}"


def is_pdf_input(path_or_url):
    """Return True if input looks like a PDF (by path/URL extension)."""
    s = path_or_url.strip().lower()
    if s.startswith(("http://", "https://")):
        return s.rstrip("/").endswith(".pdf") or ".pdf?" in s
    return s.endswith(".pdf")


def pdf_to_images_one_page_at_a_time(pdf_path, temp_dir, dpi=150):
    """
    Render PDF pages to PNG in temp_dir, one at a time (low memory).
    Yields (page_1based, image_path) and does not keep multiple images on disk.
    """
    import fitz
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    doc = fitz.open(pdf_path)
    try:
        for i in range(len(doc)):
            page = doc[i]
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out_path = os.path.join(temp_dir, f"page_{i + 1}.png")
            pix.save(out_path)
            yield (i + 1, out_path)
    finally:
        doc.close()


def download_pdf_to_temp(url, temp_dir):
    """Download PDF from URL to a file in temp_dir; return local path."""
    r = requests.get(url, timeout=60, stream=True)
    r.raise_for_status()
    path = os.path.join(temp_dir, "source.pdf")
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            f.write(chunk)
    return path


def run_ocr_on_pdf(pdf_path, temp_dir, prettify_markdown=True, show_formula_number=False, dpi=150):
    """
    OCR a PDF: render each page to image, call API, merge results; delete page images after each use.
    """
    parts = []
    for page_no, image_path in pdf_to_images_one_page_at_a_time(pdf_path, temp_dir, dpi=dpi):
        try:
            image_url = image_to_base64(image_path)
            result = call_ocr_api(image_url, prettify_markdown=prettify_markdown, show_formula_number=show_formula_number)
            if result is None:
                continue
            if result.get("code") != 0:
                continue
            text = result.get("markdown", {}).get("text", "").strip()
            if text:
                if len(parts) > 0:
                    parts.append("\n\n")
                parts.append(f"--- 第 {page_no} 页 ---\n\n{text}")
        finally:
            try:
                os.remove(image_path)
            except OSError:
                pass
    return "".join(parts)


def prepare_image_url(image_input):
    """
    Prepare image URL from file path or URL.

    Args:
        image_input: Local file path or HTTP/HTTPS URL

    Returns:
        Base64 data URL (for local files) or original URL
    """
    if image_input.startswith(("http://", "https://")):
        # Direct URL - pass through
        return image_input
    else:
        # Convert to base64
        return image_to_base64(image_input)


def call_ocr_api(image_url, prettify_markdown=True, show_formula_number=False):
    """
    Call the Sophnet OCR API.

    Args:
        image_url: Base64 data URL or direct image URL
        prettify_markdown: Return formatted Markdown output
        show_formula_number: Show formula numbering in output

    Returns:
        Dict with API response or None on error
    """
    payload = {
        "model": "PaddleOCR-VL-0.9B",
        "type": "image_url",
        "image_url": {
            "url": image_url
        },
        "prettifyMarkdown": prettify_markdown,
        "showFormulaNumber": show_formula_number
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.request("POST", API_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, timeout=60)
        if response.status_code == 200 :
            return response.json()
        else:
            print(f"HTTP请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP请求超时: {e}")
        return None
        
def main():
    if len(sys.argv) < 2:
        print("Usage: ocr.py <image-or-pdf-path-or-url>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  ocr.py /path/to/image.jpg", file=sys.stderr)
        print("  ocr.py /path/to/document.pdf", file=sys.stderr)
        print("  ocr.py https://example.com/image.jpg", file=sys.stderr)
        print("  ocr.py media/inbound/images/uploaded_image.png", file=sys.stderr)
        print("\nFor Moltbot-uploaded images, check media/inbound/images/ in the workspace.", file=sys.stderr)
        sys.exit(1)

    image_input = sys.argv[1].strip()

    # PDF: multi-page → images (one at a time), OCR each, merge, then delete cache
    if is_pdf_input(image_input):
        temp_dir = tempfile.mkdtemp(prefix="ocr_pdf_")
        try:
            if image_input.startswith(("http://", "https://")):
                try:
                    pdf_path = download_pdf_to_temp(image_input, temp_dir)
                except requests.RequestException as e:
                    print(f"下载 PDF 失败: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                if not os.path.isfile(image_input):
                    print(f"文件不存在: {image_input}", file=sys.stderr)
                    sys.exit(1)
                pdf_path = os.path.abspath(image_input)
            merged = run_ocr_on_pdf(pdf_path, temp_dir, prettify_markdown=True, show_formula_number=False, dpi=150)
            print(merged)
        except Exception as e:
            print(f"PDF 处理错误: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except OSError:
                pass
        return

    # Image path or URL
    image_url = prepare_image_url(image_input)
    result = call_ocr_api(image_url)

    if result is None:
        sys.exit(1)

    # Check response code
    if result.get("code") != 0:
        print(f"API Error (code {result.get('code')}): {result.get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    # Output markdown text
    markdown_text = result.get("markdown", {}).get("text", "")
    print(markdown_text)


if __name__ == "__main__":
    main()