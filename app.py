"""StudyLens AI - Streamlit app (redesigned UI)."""
import html
import re

import fitz  # PyMuPDF
import streamlit as st

from src.pdf_processor import extract_pages
from src.text_processor import chunk_pages
from src.retriever import Retriever
from src.answerer import answer
from src.database import init_db, save_qa, get_history

try:
    from src.pdf_processor import count_empty_pages
except ImportError:
    def count_empty_pages(pages):
        return sum(1 for p in pages if not p["text"].strip())

st.set_page_config(page_title="StudyLens AI", page_icon="📚", layout="wide")
init_db()

st.markdown("""
<style>
.hero {padding: 1.6rem 2rem; border-radius: 16px; color: white;
       background: linear-gradient(120deg, #1F2A44 0%, #0F9D8A 100%); margin-bottom: 1rem;}
.hero h1 {margin: 0; font-size: 2.2rem; color: white;}
.hero p {margin: .3rem 0 0 0; opacity: .9; font-size: 1.05rem;}
.step {border: 1px solid #d5dbe3; border-radius: 14px; padding: 1rem 1.2rem; height: 100%;}
.answer {border-left: 6px solid #0F9D8A; background: rgba(15,157,138,.10);
         padding: 1rem 1.2rem; border-radius: 10px; font-size: 1.05rem;}
.answer.nf {border-left-color: #E08A00; background: rgba(224,138,0,.12);}
.badge {display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: .8rem;
        color: white; margin-left: 8px;}
mark {background: #FFE066; color: black; padding: 0 2px; border-radius: 3px;}
.ev {border: 1px solid #d5dbe3; border-radius: 12px; padding: .8rem 1rem; margin-bottom: .4rem;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def highlight(text, question):
    safe = html.escape(text)
    for w in {w for w in re.findall(r"\w+", question) if len(w) > 3}:
        safe = re.sub(f"(?i)\\b({re.escape(w)})\\b", r"<mark>\1</mark>", safe)
    return safe


def match_label(score):
    if score > 0.5:
        return "Strong match", "#1B9E5A"
    if score > 0.3:
        return "Partial match", "#E08A00"
    return "Weak match", "#D64545"


def render_page(pdf_bytes, page_no, passage, zoom=1.4):
    """Render the cited PDF page as an image with the evidence highlighted."""
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


def set_question(text):
    st.session_state.q = text


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📄 Document")
    uploaded = st.file_uploader("Upload a PDF", type="pdf")
    k = st.slider("Passages to retrieve", 1, 5, 3)
    show_pages = st.toggle("Show highlighted PDF page", value=True)
    st.divider()
    st.subheader("🕘 Recent questions")
    history = get_history(limit=5)
    if not history:
        st.caption("No questions yet.")
    for h in history:
        st.caption(f"**{h['question']}**  \nPages: {h['pages']}")

# ---------------- Hero ----------------
st.markdown("""<div class="hero"><h1>📚 StudyLens AI</h1>
<p>Ask questions about your PDF. Every answer shows the exact evidence it came from.</p></div>""",
            unsafe_allow_html=True)

if not uploaded:
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="step"><b>1. Upload</b><br>Add a lecture PDF in the sidebar.</div>', unsafe_allow_html=True)
    c2.markdown('<div class="step"><b>2. Ask</b><br>Type any question about the document.</div>', unsafe_allow_html=True)
    c3.markdown('<div class="step"><b>3. Verify</b><br>Check the cited pages and highlighted evidence.</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- Process PDF ----------------
if st.session_state.get("file_name") != uploaded.name:
    pdf_bytes = uploaded.getvalue()
    pages = extract_pages(pdf_bytes)
    chunks = chunk_pages(pages)
    if not chunks:
        st.error("No text found. This may be a scanned PDF (OCR is not supported yet).")
        st.stop()
    with st.spinner("Reading and indexing your document..."):
        r = Retriever(model=load_model())
        r.build(chunks)
    st.session_state.update(file_name=uploaded.name, pdf_bytes=pdf_bytes,
                            pages=pages, chunks=chunks, retriever=r, q="")

pages, chunks = st.session_state.pages, st.session_state.chunks
m1, m2, m3 = st.columns(3)
m1.metric("Pages", len(pages))
m2.metric("Chunks indexed", len(chunks))
empty = count_empty_pages(pages)
m3.metric("Pages without text", empty)
if empty:
    st.warning(f"{empty} page(s) have no extractable text (possibly scanned images).")

tab_ask, tab_doc = st.tabs(["💬 Ask", "📖 Browse document"])

with tab_ask:
    st.caption("Try an example:")
    e1, e2, e3 = st.columns(3)
    e1.button("Summarize the main idea", on_click=set_question, args=("What is the main idea of this document?",), use_container_width=True)
    e2.button("Key definitions", on_click=set_question, args=("What are the key definitions in this document?",), use_container_width=True)
    e3.button("Important points", on_click=set_question, args=("What are the most important points?",), use_container_width=True)

    question = st.text_input("Your question", key="q", placeholder="e.g. What is overfitting?")

    if question:
        results = st.session_state.retriever.search(question, k=k)
        cache_key = (st.session_state.file_name, question, k)
        if st.session_state.get("last_key") != cache_key:
            with st.spinner("Thinking..."):
                try:
                    ans = answer(question, results)
                except Exception as e:
                    ans = None
                    st.warning(f"LLM call failed: {e}")
            save_qa(question, ans or "", results, st.session_state.file_name)
            st.session_state.last_key, st.session_state.last_ans = cache_key, ans
        ans = st.session_state.last_ans

        st.subheader("Answer")
        if ans is None:
            st.info("No LLM key set. Showing evidence only.")
        else:
            cls = "answer nf" if ans.lower().startswith("not found") else "answer"
            st.markdown(f'<div class="{cls}">{html.escape(ans)}</div>', unsafe_allow_html=True)

        st.subheader("Evidence from the document")
        for i, r in enumerate(results, 1):
            label, color = match_label(r["score"])
            st.markdown(
                f'<div class="ev"><b>#{i} · Page {r["page"]}</b>'
                f'<span class="badge" style="background:{color}">{label} · {r["score"]:.2f}</span><br><br>'
                f'{highlight(r["text"], question)}</div>', unsafe_allow_html=True)
            st.progress(max(0.0, min(1.0, r["score"])))
            if show_pages:
                with st.expander(f"View page {r['page']} in the PDF"):
                    img = render_page(st.session_state.pdf_bytes, r["page"], r["text"])
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("Could not render this page.")

with tab_doc:
    page_no = st.number_input("Page", 1, len(pages), 1)
    st.text_area("Extracted text", pages[page_no - 1]["text"], height=350)

st.divider()
st.caption("StudyLens AI · Team: Reena, Harsha, Anjali, Shirin")