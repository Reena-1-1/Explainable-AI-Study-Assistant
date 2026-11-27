"""StudyLens AI - entry point: theme, sidebar, navigation. Each feature is a page in views/."""
import streamlit as st

from src.database import init_db, create_notes_table, get_history
from src.ui_theme import theme_css, FLOATING_HELP_HTML
from src import workspace as ws

st.set_page_config(page_title="StudyLens AI", page_icon="🔎", layout="wide")

init_db()
create_notes_table()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- Pages ----------------

pages = {
    "Start": [
        st.Page("views/home.py", title="Home", icon="🏠", default=True),
    ],
    "Study": [
        st.Page("views/ask.py", title="Ask", icon="💬"),
        st.Page("views/browse.py", title="Browse documents", icon="📖"),
        st.Page("views/notes.py", title="Smart Notes", icon="📝"),
        st.Page("views/quizzes.py", title="Quizzes & Tests", icon="🧠"),
        st.Page("views/study_tools.py", title="Study tools", icon="🛠️"),
        st.Page("views/web_video.py", title="Web & video notes", icon="🌐"),
    ],
    "Project": [
        st.Page("views/about.py", title="About", icon="ℹ️"),
    ],
}
page = st.navigation(pages)

# ---------------- Sidebar (shared by every page) ----------------

dark_mode = st.sidebar.toggle("🌙 Dark mode", value=True, key="dark_mode")
st.markdown(theme_css(dark_mode), unsafe_allow_html=True)
st.markdown(FLOATING_HELP_HTML, unsafe_allow_html=True)

with st.sidebar:
    st.divider()
    st.subheader("📄 Your documents")
    uploaded = st.file_uploader(
        "Upload PDF documents", type="pdf",
        accept_multiple_files=True, key="pdf_uploader",
    )
    ready = ws.process_uploads(uploaded)

    if ready:
        docs = ws.documents()
        pages_total = sum(len(d["pages"]) for d in docs.values())
        st.markdown(
            f'<div class="status"><b>{len(docs)}</b> PDF(s) · <b>{pages_total}</b> pages · '
            f'<b>{len(ws.chunks())}</b> passages ready</div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption("No document loaded yet.")

    with st.expander("⚙️ Answer settings"):
        st.slider("Passages to retrieve", 1, 5, 3, key="k")
        st.selectbox("Explanation style", ["Simple", "Detailed", "Step-by-step"], key="style_label")
        st.toggle("Show highlighted PDF page", value=True, key="show_pages")

    st.subheader("🕘 Recent questions")
    history = get_history(limit=5)
    if not history:
        st.caption("No questions yet.")
    for h in history:
        st.caption(f"**{h['question']}**  \nPages: {h['pages']}")

    chat_slot = st.container()

# ---------------- Run the selected page ----------------

page.run()

# ---------------- Chat history (filled after the page so it is always current) ----------------

with chat_slot:
    with st.expander("💬 Chat history (this session)"):
        if st.session_state.chat_history:
            for item in reversed(st.session_state.chat_history):
                st.markdown(f"**Q:** {item['question']}")
                st.write(f"**A:** {item['answer']}")
                st.divider()
        else:
            st.caption("No chat history yet.")
