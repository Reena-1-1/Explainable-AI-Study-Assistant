"""StudyLens AI - Streamlit app (redesigned UI)."""
import html
import re
import hashlib

import fitz  # PyMuPDF
import streamlit as st

from src.pdf_processor import extract_pages
from src.text_processor import chunk_pages
from src.retriever import Retriever
from src.answerer import answer
from src.database import init_db, save_qa, get_history
from src.website_processor import extract_website_text, generate_website_notes
from src.youtube_processor import extract_youtube_transcript

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


# ---------------- Website to Notes ----------------
st.markdown("## 🌐 Website to Notes")
st.caption("Enter a webpage URL to extract its content and generate study notes.")

website_url = st.text_input(
    "Website URL",
    placeholder="https://example.com"
)

if st.button("Generate Website Notes", key="generate_website_notes"):
    if not website_url.strip():
        st.warning("Please enter a website URL.")
    else:
        try:
            with st.spinner("Extracting website content and generating notes..."):
                website = extract_website_text(website_url)

                source_text = website["text"][:12000]

                results = [{
                    "page": 1,
                    "text": source_text
                }]

                notes = generate_website_notes(source_text)

            st.subheader(website["title"])
            st.caption(f"Source: {website['url']}")

            if notes:
                st.markdown(notes)
            else:
                st.warning(
                    "Website text was extracted, but AI notes could not be "
                    "generated. Check your GROQ_API_KEY in the .env file."
                )

            with st.expander("View extracted website text"):
                st.write(source_text)

        except Exception as error:
            st.error(f"Website processing failed: {error}")



# ---------------- YouTube to Notes ----------------

st.markdown("## 🎥 YouTube Video to Notes")
st.caption("Enter a YouTube video URL to extract its transcript and generate study notes.")

youtube_url = st.text_input(
    "YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

if st.button("Generate YouTube Notes", key="generate_youtube_notes"):
    if not youtube_url.strip():
        st.warning("Please enter a YouTube video URL.")
    else:
        try:
            with st.spinner("Extracting transcript and generating notes..."):
                video = extract_youtube_transcript(youtube_url)

                transcript_text = video["text"][:12000]

                notes = generate_website_notes(transcript_text)

            st.subheader("YouTube Study Notes")
            st.caption(f"Source: {video['url']}")

            if notes:
                st.markdown(notes)
            else:
                st.warning("Transcript extracted, but notes could not be generated.")

            with st.expander("View extracted transcript"):
                st.write(transcript_text)

        except Exception as error:
            st.error(f"YouTube processing failed: {error}")




# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📄 Document")
    uploaded = st.file_uploader(
    "Upload PDF documents",
    type="pdf",
    accept_multiple_files=True
)
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
file_payloads = [(file.name, file.getvalue()) for file in uploaded]

file_signature = tuple(
    (name, hashlib.sha256(data).hexdigest())
    for name, data in file_payloads
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
        chunks_for_file = chunk_pages(pages_for_file)

        for chunk in chunks_for_file:
            chunk["source_id"] = source_id
            chunk["source_name"] = file_name
            all_chunks.append(chunk)

        documents[source_id] = {
            "name": file_name,
            "pdf_bytes": pdf_bytes,
            "pages": pages_for_file
        }

    if not all_chunks:
        st.error(
            "No extractable text found in the uploaded PDFs. "
            "Please check whether the PDF contains readable text or scanned pages."
        )
        st.stop()

    with st.spinner("Reading and indexing your PDF documents..."):
        r = Retriever(model=load_model())
        r.build(all_chunks)

    st.session_state.update(
        file_signature=file_signature,
        documents=documents,
        chunks=all_chunks,
        retriever=r,
        q="",
        last_key=None
    )

documents = st.session_state.documents
chunks = st.session_state.chunks

total_pages = sum(
    len(document["pages"]) for document in documents.values()
)

empty = sum(
    count_empty_pages(document["pages"])
    for document in documents.values()
)

m1, m2, m3 = st.columns(3)
m1.metric("PDFs uploaded", len(documents))
m2.metric("Pages", total_pages)
m3.metric("Chunks indexed", len(chunks))

if empty:
    st.warning(
        f"{empty} page(s) have no extractable text "
        "(possibly scanned images)."
    )


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

        cache_key = (file_signature, question, k)
        doc_names = ", ".join(
            document["name"] for document in documents.values()
        )

        if st.session_state.get("last_key") != cache_key:
            with st.spinner("Thinking..."):
                try:
                    ans = answer(question, results)
                except Exception as e:
                    ans = None
                    st.warning(f"LLM call failed: {e}")

            save_qa(question, ans or "", results, doc_names)
            st.session_state.last_key = cache_key
            st.session_state.last_ans = ans

        ans = st.session_state.last_ans

        st.subheader("Answer")

        if ans is None:
            st.info("No LLM key set. Showing evidence only.")
        else:
            cls = "answer nf" if ans.lower().startswith("not found") else "answer"
            st.markdown(
                f'<div class="{cls}">{html.escape(ans)}</div>',
                unsafe_allow_html=True
            )

        st.subheader("Evidence from the documents")

        for i, result in enumerate(results, 1):
            label, color = match_label(result["score"])

            st.markdown(
                f'<div class="ev"><b>#{i} · '
                f'{html.escape(result["source_name"])} · '
                f'Page {result["page"]}</b>'
                f'<span class="badge" style="background:{color}">'
                f'{label} · {result["score"]:.2f}</span><br><br>'
                f'{highlight(result["text"], question)}</div>',
                unsafe_allow_html=True
            )

            st.progress(max(0.0, min(1.0, result["score"])))

            if show_pages:
                with st.expander(
                    f"View {result['source_name']} - Page {result['page']}"
                ):
                    source_document = documents[result["source_id"]]

                    img = render_page(
                        source_document["pdf_bytes"],
                        result["page"],
                        result["text"]
                    )

                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("Could not render this page.")


with tab_doc:
    source_ids = list(documents.keys())

    selected_source_id = st.selectbox(
        "Choose a PDF",
        options=source_ids,
        format_func=lambda source_id: documents[source_id]["name"]
    )

    selected_document = documents[selected_source_id]
    selected_pages = selected_document["pages"]

    page_no = st.number_input(
        "Page",
        min_value=1,
        max_value=len(selected_pages),
        value=1,
        key="browse_page"
    )

    st.text_area(
        "Extracted text",
        selected_pages[page_no - 1]["text"],
        height=350
    )
