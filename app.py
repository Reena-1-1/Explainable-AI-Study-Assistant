import streamlit as st

from src.pdf_processor import extract_text_from_pdf
from src.text_processor import create_chunks


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

    # Step 1: Extract text from PDF
    pages = extract_text_from_pdf(uploaded_file)

    # Step 2: Display extracted text
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


    # Step 3: Create chunks
    chunks = create_chunks(pages)


    # Step 4: Display chunks
    st.subheader("Document Chunks")

    st.write(
        f"Total chunks created: {len(chunks)}"
    )


    for i, chunk in enumerate(chunks[:5], start=1):

        st.markdown(f"### Chunk {i}")

        st.write(
            f"Source page: {chunk['page']}"
        )

        st.text(chunk["text"])