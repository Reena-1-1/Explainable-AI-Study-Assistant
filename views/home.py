import streamlit as st

from src import workspace as ws
from src.ui_theme import HERO_HTML

st.markdown(HERO_HTML, unsafe_allow_html=True)


def main():
    if ws.has_docs():
        docs = ws.documents()
        m1, m2, m3 = st.columns(3)
        m1.metric("PDFs loaded", len(docs))
        m2.metric("Pages", sum(len(d["pages"]) for d in docs.values()))
        m3.metric("Passages indexed", len(ws.chunks()))
        empty = sum(ws.count_empty_pages(d["pages"]) for d in docs.values())
        if empty:
            st.warning(f"{empty} page(s) have no readable text (possibly scanned images).")
        st.page_link("views/ask.py", label="Ask your first question", icon="💬")
    else:
        st.markdown("### Start in three steps")
        c1, c2, c3 = st.columns(3)
        c1.markdown('<div class="step"><div class="n">1</div><div><b>Upload</b>'
                    '<span>Add one or more PDFs in the sidebar.</span></div></div>',
                    unsafe_allow_html=True)
        c2.markdown('<div class="step"><div class="n">2</div><div><b>Ask</b>'
                    '<span>Type any question about your material.</span></div></div>',
                    unsafe_allow_html=True)
        c3.markdown('<div class="step"><div class="n">3</div><div><b>Check</b>'
                    '<span>Open the cited page and see the highlighted evidence.</span></div></div>',
                    unsafe_allow_html=True)

    st.markdown("### Everything you need to study")

    top_a, top_b = st.columns([2, 1])
    with top_a:
        with st.container(key="tile_ask"):
            st.markdown('<p class="tile-title">💬 Ask with evidence</p>'
                        '<p class="tile-text">Get a simple, detailed or step-by-step answer. '
                        'Every answer lists the passages it used, with file name, page number, '
                        'a match score and the page itself, highlighted.</p>',
                        unsafe_allow_html=True)
            st.page_link("views/ask.py", label="Open Ask", icon="💬")
    with top_b:
        with st.container(key="tile_notes"):
            st.markdown('<p class="tile-title">📝 Smart Notes</p>'
                        '<p class="tile-text">Write your own notes or let AI draft them from your '
                        'PDFs. Edit, save and manage them in one place.</p>',
                        unsafe_allow_html=True)
            st.page_link("views/notes.py", label="Open Smart Notes", icon="📝")

    st.write("")
    b1, b2, b3 = st.columns(3)
    with b1:
        with st.container(key="tile_quiz"):
            st.markdown('<p class="tile-title">🧠 Quizzes &amp; Tests</p>'
                        '<p class="tile-text">Choose how many questions you want. Get a score and '
                        'an explanation for every answer.</p>', unsafe_allow_html=True)
            st.page_link("views/quizzes.py", label="Take a quiz", icon="🧠")
    with b2:
        with st.container(key="tile_tools"):
            st.markdown('<p class="tile-title">🛠️ Study tools</p>'
                        '<p class="tile-text">Summaries, page-linked quizzes and flashcards '
                        'built from your documents.</p>', unsafe_allow_html=True)
            st.page_link("views/study_tools.py", label="Open Study tools", icon="🛠️")
    with b3:
        with st.container(key="tile_web"):
            st.markdown('<p class="tile-title">🌐 Web &amp; video notes</p>'
                        '<p class="tile-text">Paste a website or a YouTube lecture link and get '
                        'clean notes you can save.</p>', unsafe_allow_html=True)
            st.page_link("views/web_video.py", label="Make notes from a link", icon="🌐")

    st.write("")
    with st.expander("📌 How to use StudyLens AI"):
        st.markdown("""
1. Upload one or more PDFs in the sidebar.
2. Open **Ask** and type your question.
3. Read the answer, then check the highlighted evidence and page numbers.
4. Use **Smart Notes**, **Quizzes & Tests**, **Study tools** and **Web & video notes** to revise.
""")


main()
