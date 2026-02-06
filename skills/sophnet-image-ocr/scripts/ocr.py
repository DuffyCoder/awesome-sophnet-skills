#!/usr/bin/env python3
"""
Image OCR utility for Sophnet PaddleOCR API.

Supports local image files and direct URLs.
Returns Markdown-formatted text and table extraction results.
Base64 conversion is handled automatically for local files.
"""

import os
import sys
import base64
import mimetypes
import json
import requests

# API Configuration
API_URL = "https://www.sophnet.com/api/open-apis/projects/easyllms/image-ocr"
API_KEY = os.environ.get("SOPH_API_KEY")

if not API_KEY:
    print("Error: SOPH_API_KEY environment variable not set.", file=sys.stderr)
    print("Please set it with: export SOPH_API_KEY='your-key'", file=sys.stderr)
    print("Or obtain a key using the sophon-key skill.", file=sys.stderr)
    sys.exit(1)


def image_to_base64(image_path):
    """Convert a local image file to base64 data URL."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported file type: {image_path}")

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{image_data}"


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
        print("Usage: ocr.py <image-path-or-url>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  ocr.py /path/to/image.jpg", file=sys.stderr)
        print("  ocr.py https://example.com/image.jpg", file=sys.stderr)
        print("  ocr.py media/inbound/images/uploaded_image.png", file=sys.stderr)
        print("\nFor Moltbot-uploaded images, check media/inbound/images/ in the workspace.", file=sys.stderr)
        sys.exit(1)

    image_input = sys.argv[1]
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