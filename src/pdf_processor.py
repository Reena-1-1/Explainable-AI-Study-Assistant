import fitz


def extract_text_from_pdf(pdf_file):
    """
    Extract text from every page of an uploaded PDF.
    Returns the extracted text along with page numbers.
    """

    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")

    pages = []

    for page_number, page in enumerate(pdf_document, start=1):
        text = page.get_text("text")

        pages.append({
            "page": page_number,
            "text": text
        })

    pdf_document.close()

    return pages