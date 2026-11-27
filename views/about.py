import streamlit as st

from src.ui_theme import page_header

st.markdown(page_header("ℹ️", "About StudyLens AI",
                        "An explainable study assistant: it shows the evidence behind every answer."),
            unsafe_allow_html=True)

st.markdown("### How an answer is made")
a, b, c, d = st.columns(4)
a.markdown('<div class="step"><div class="n">1</div><div><b>Read</b><span>Text is extracted from each PDF page.</span></div></div>', unsafe_allow_html=True)
b.markdown('<div class="step"><div class="n">2</div><div><b>Index</b><span>Passages are turned into embeddings for search.</span></div></div>', unsafe_allow_html=True)
c.markdown('<div class="step"><div class="n">3</div><div><b>Retrieve</b><span>The closest passages to your question are picked.</span></div></div>', unsafe_allow_html=True)
d.markdown('<div class="step"><div class="n">4</div><div><b>Answer</b><span>An AI model answers using only those passages.</span></div></div>', unsafe_allow_html=True)

st.markdown("### Built with")
st.markdown("""
- **Streamlit** for the web app
- **PyMuPDF** to read and highlight PDF pages
- **Sentence-Transformers** (all-MiniLM-L6-v2) for semantic search
- **Groq** language models for answers, notes and quizzes
- **SQLite** to keep notes and question history
""")

st.markdown("### Team")
t1, t2 = st.columns(2)
with t1:
    with st.container(key="tile_team_a"):
        st.markdown("**Reena**  \nStudy tools, answer styles, integration and design")
        st.markdown("**Shirin**  \nSmart Notes and the full-document quiz")
with t2:
    with st.container(key="tile_team_b"):
        st.markdown("**Harsha**  \nMulti-PDF support, website and YouTube notes, scanned-PDF reading")
        st.markdown("**Anjali**  \nHow-to guide and chat history")
