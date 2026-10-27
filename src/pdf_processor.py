
"""PDF -> list of pages. Owner: Harsha."""
import fitz  # PyMuPDF
import re


def extract_pages(pdf_bytes: bytes):
    """Return [{"page": 1, "text": "..."}, ...] (page numbers start at 1)."""
    pages = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text()

            # Remove lines containing only a page number.
            text = re.sub(r"(?m)^\s*\d+\s*$", "", text)

            pages.append({"page": i, "text": text})
    return pages


def count_empty_pages(pages):
    """Return the number of pages that contain no meaningful text."""
    return sum(1 for page in pages if not page["text"].strip())
