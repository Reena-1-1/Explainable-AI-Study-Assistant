
"""PDF text extraction with OCR fallback for scanned pages."""

import os
import re
from io import BytesIO

import fitz

try:  # OCR is optional: the app still works without Tesseract installed
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

# Configure the Tesseract executable on Windows.
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if pytesseract is not None and os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_pages(pdf_bytes: bytes):
    """Extract text from PDF pages, using OCR for scanned pages."""

    pages = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc, start=1):

            # First, try normal PDF text extraction.
            text = page.get_text()

            # Use OCR if the page contains no selectable text.
            if not text.strip() and pytesseract is not None:
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False
                )

                try:
                    image = Image.open(BytesIO(pix.tobytes("png")))
                    text = pytesseract.image_to_string(image, lang="eng")
                except Exception:
                    text = ""  # Tesseract missing/failed: leave page empty

            # Remove lines containing only a page number.
            text = re.sub(r"(?m)^\s*\d+\s*$", "", text)

            pages.append({
                "page": i,
                "text": text
            })

    return pages

def count_empty_pages(pages):
    """Return the number of pages containing no meaningful text."""

    return sum(
        1 for page in pages
        if not page["text"].strip()
    )