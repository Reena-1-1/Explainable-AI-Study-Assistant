import re


def clean_text(text):
    """
    Clean extracted PDF text.
    """

    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text)

    # Remove leading and trailing spaces
    text = text.strip()

    return text


def create_chunks(pages, chunk_size=1000, overlap=200):
    """
    Convert page-wise extracted text into overlapping chunks.

    Each chunk keeps its source page number.
    """

    chunks = []

    for page in pages:

        text = clean_text(page["text"])

        if not text:
            continue

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "page": page["page"]
            })

            start += chunk_size - overlap

    return chunks