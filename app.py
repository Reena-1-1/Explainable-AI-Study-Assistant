"""StudyLens AI - Streamlit app. Owner: Anjali (UI)."""
import streamlit as st

from src.pdf_processor import extract_pages
from src.text_processor import chunk_pages
from src.retriever import Retriever
from src.answerer import answer

st.set_page_config(page_title="StudyLens AI", page_icon="📚", layout="wide")
st.title("📚 StudyLens AI")
st.caption("Ask questions about your PDF. Every answer comes with its evidence.")


@st.cache_resource
def get_retriever_class():
    return Retriever


uploaded = st.file_uploader("Upload a PDF", type="pdf")

if uploaded:
    if st.session_state.get("file_name") != uploaded.name:
        pages = extract_pages(uploaded.getvalue())
        chunks = chunk_pages(pages)
        if not chunks:
            st.error("No text found. This may be a scanned PDF (OCR not supported yet).")
            st.stop()
        with st.spinner("Indexing document..."):
            r = get_retriever_class()()
            r.build(chunks)
        st.session_state.update(file_name=uploaded.name, pages=pages,
                                chunks=chunks, retriever=r)

    st.success(f"Loaded {len(st.session_state.pages)} pages, "
               f"{len(st.session_state.chunks)} chunks.")

    question = st.text_input("Ask a question about your document")
    if question:
        results = st.session_state.retriever.search(question, k=3)
        st.subheader("Answer")
        try:
            ans = answer(question, results)
        except Exception as e:
            ans = None
            st.warning(f"LLM call failed: {e}")
        st.write(ans if ans else "(No LLM key set - showing evidence only.)")

        st.subheader("Evidence from the document")
        for i, r in enumerate(results, 1):
            with st.expander(f"#{i} - Page {r['page']} (similarity {r['score']:.2f})",
                             expanded=(i == 1)):
                st.write(r["text"])

    with st.sidebar:
        st.header("Document")
        page_no = st.number_input("View page text", 1, len(st.session_state.pages), 1)
        st.text_area("Text", st.session_state.pages[page_no - 1]["text"], height=300)
