import streamlit as st

from src.pdf_processor import extract_text_from_pdf


st.set_page_config(
    page_title="StudyLens AI",
    page_icon="📚"
)

st.title("📚 StudyLens AI")

st.write(
    "An Explainable Multimodal AI Study Assistant"
)

st.subheader("Upload Study Material")

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    pages = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Text")

    for page in pages:

        st.markdown(f"### Page {page['page']}")

        if page["text"].strip():
            st.text_area(
                f"Page {page['page']} text",
                page["text"],
                height=200
            )
        else:
            st.warning(
                f"No text found on page {page['page']}."
            )