import fitz
from src.pdf_processor import extract_pages, count_empty_pages


def make_pdf(texts):
    doc = fitz.open()
    for t in texts:
        doc.new_page().insert_text((72, 72), t)
    data = doc.tobytes()
    doc.close()
    return data


def test_extracts_each_page_with_number():
    pages = extract_pages(make_pdf(["Hello page one", "Second page"]))
    assert [p["page"] for p in pages] == [1, 2]
    assert "Hello" in pages[0]["text"]


def test_blank_page_returns_empty_text():
    pages = extract_pages(make_pdf([""]))
    assert pages[0]["text"].strip() == ""
    
    
def test_count_empty_pages():
    pages = [
        {"page": 1, "text": "Hello"},
        {"page": 2, "text": ""},
        {"page": 3, "text": "   "},
        {"page": 4, "text": "World"},
    ]

    assert count_empty_pages(pages) == 2
