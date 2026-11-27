import streamlit as st

from src import workspace as ws
from src.ui_theme import page_header

st.markdown(page_header("📖", "Browse documents",
                        "Read the text the app extracted from each page of your PDFs."),
            unsafe_allow_html=True)


def main():
    if not ws.has_docs():
        ws.show_empty("browse every page")
        return

    documents = ws.documents()
    source_id = st.selectbox(
        "Choose a PDF", options=list(documents.keys()),
        format_func=lambda sid: documents[sid]["name"],
    )
    pages = documents[source_id]["pages"]
    page_no = st.number_input("Page", min_value=1, max_value=len(pages), value=1, key="browse_page")
    st.text_area("Extracted text", pages[page_no - 1]["text"], height=420)


main()
