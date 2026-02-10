#!/usr/bin/env python3
"""Extract text from PDF to understand its content."""

import pdfplumber
import sys

pdf_path = "/Data/shutong.shan/clawd/media/inbound/documents/Image-Edit_教程.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")
        print("=" * 80)
        print("PDF Content:")
        print("=" * 80 + "\n")

        for i, page in enumerate(pdf.pages, 1):
            print(f"\n--- Page {i} ---\n")
            text = page.extract_text()
            if text:
                print(text)
            else:
                print("[No text found on this page]")

            # Check for tables
            tables = page.extract_tables()
            if tables:
                print(f"\n[Found {len(tables)} table(s) on this page]")
                for j, table in enumerate(tables, 1):
                    print(f"\nTable {j}:")
                    for row in table:
                        print(row)

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)