"""PDF -> list of pages. Owner: Harsha."""
import fitz  # PyMuPDF


def extract_pages(pdf_bytes: bytes):
    """Return [{"page": 1, "text": "..."}, ...] (page numbers start at 1)."""
    pages = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc, start=1):
            pages.append({"page": i, "text": page.get_text()})
    return pages
