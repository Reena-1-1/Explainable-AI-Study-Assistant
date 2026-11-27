"""Shared document workspace: upload processing and helpers used by every page."""
import hashlib
import html
import re

import fitz
import streamlit as st

from src.pdf_processor import extract_pages
from src.text_processor import chunk_pages
from src.retriever import Retriever
from src.ui_theme import empty_state

try:
    from src.pdf_processor import count_empty_pages
except ImportError:
    def count_empty_pages(pages):
        return sum(1 for p in pages if not p["text"].strip())


@st.cache_resource
def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def process_uploads(uploaded):
    """Read, chunk and index the uploaded PDFs. Returns True when documents are ready."""
    has_docs = False
    file_signature = None

    if uploaded:
        file_payloads = [(f.name, f.getvalue()) for f in uploaded]
        file_signature = tuple(
            (name, hashlib.sha256(data).hexdigest()) for name, data in file_payloads
        )

        if st.session_state.get("file_signature") != file_signature:
            documents = {}
            all_chunks = []

            for index, (file_name, pdf_bytes) in enumerate(file_payloads):
                content_hash = hashlib.sha256(pdf_bytes).hexdigest()
                source_id = hashlib.sha256(
                    f"{index}:{file_name}:{content_hash}".encode()
                ).hexdigest()[:12]

                pages_for_file = extract_pages(pdf_bytes)
                for chunk in chunk_pages(pages_for_file):
                    chunk["source_id"] = source_id
                    chunk["source_name"] = file_name
                    all_chunks.append(chunk)

                documents[source_id] = {
                    "name": file_name,
                    "pdf_bytes": pdf_bytes,
                    "pages": pages_for_file,
                }

            if not all_chunks:
                st.session_state.pop("file_signature", None)
                st.sidebar.error(
                    "No readable text found. These PDFs may be scanned images "
                    "and Tesseract (OCR) is not installed."
                )
            else:
                with st.spinner("Reading and indexing your PDF documents..."):
                    retriever = Retriever(model=load_model())
                    retriever.build(all_chunks)

                st.session_state.update(
                    file_signature=file_signature,
                    documents=documents,
                    chunks=all_chunks,
                    retriever=retriever,
                    file_name=", ".join(d["name"] for d in documents.values()),
                    q="",
                    last_key=None,
                )

        has_docs = st.session_state.get("file_signature") == file_signature

    st.session_state["has_docs"] = has_docs
    return has_docs


def has_docs():
    return bool(st.session_state.get("has_docs"))


def documents():
    return st.session_state.get("documents", {})


def chunks():
    return st.session_state.get("chunks", [])


def all_document_text():
    """Text of every uploaded PDF, labelled with file name and page number."""
    parts = []
    for document in documents().values():
        for page in document["pages"]:
            parts.append(f"[{document['name']} - Page {page['page']}]\n{page['text']}")
    return "\n\n".join(parts)


def show_empty(what):
    """Friendly empty state shown on pages that need a PDF."""
    st.markdown(
        empty_state(
            "📄", "Add a PDF to get started",
            f"Use the sidebar to upload one or more PDFs. Then you can {what}.",
        ),
        unsafe_allow_html=True,
    )


def highlight(text, question):
    safe = html.escape(text)
    for word in {w for w in re.findall(r"\w+", question) if len(w) > 3}:
        safe = re.sub(f"(?i)\\b({re.escape(word)})\\b", r"<mark>\1</mark>", safe)
    return safe


def match_label(score):
    if score > 0.5:
        return "Strong match", "#1B9E5A"
    if score > 0.3:
        return "Partial match", "#C77700"
    return "Weak match", "#D64545"


def render_page(pdf_bytes, page_no, passage, zoom=1.4):
    """Render the cited PDF page with the evidence highlighted."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[page_no - 1]
        words = passage.split()
        for i in range(0, min(len(words), 80), 4):
            phrase = " ".join(words[i:i + 4])
            if len(phrase) < 8:
                continue
            for rect in page.search_for(phrase):
                page.add_highlight_annot(rect)
        png = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).tobytes("png")
        doc.close()
        return png
    except Exception:
        return None
