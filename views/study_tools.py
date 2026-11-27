import streamlit as st

from src import workspace as ws
from src.study_tools_ui import render_study_tools
from src.ui_theme import page_header

st.markdown(page_header("🛠️", "Study tools",
                        "Summaries, page-linked quizzes and flashcards made from your documents."),
            unsafe_allow_html=True)


def main():
    if not ws.has_docs():
        ws.show_empty("use summaries, quizzes and flashcards")
        return
    render_study_tools(ws.chunks(), st.session_state.file_signature)


main()
