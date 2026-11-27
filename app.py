"""StudyLens AI - Explainable Study Assistant."""
import hashlib
import html
import re

import fitz
import streamlit as st

from src.pdf_processor import extract_pages
from src.text_processor import chunk_pages
from src.retriever import Retriever
from src.answerer import answer
from src.database import (
    init_db,
    save_qa,
    get_history,
    create_notes_table,
    save_note,
    get_notes,
    update_note,
    delete_note,
)
from src.notes_generator import generate_notes
from src.document_quiz import generate_document_quiz
from src.study_tools_ui import render_study_tools
from src.website_processor import extract_website_text, generate_website_notes
from src.youtube_processor import extract_youtube_transcript

try:
    from src.pdf_processor import count_empty_pages
except ImportError:
    def count_empty_pages(pages):
        return sum(1 for p in pages if not p["text"].strip())


st.set_page_config(
    page_title="StudyLens AI",
    page_icon="📚",
    layout="wide"
)

# Initialize databases
init_db()
create_notes_table()


# ---------------- Styling ----------------

st.markdown("""
<style>
.hero {
    padding: 1.6rem 2rem;
    border-radius: 16px;
    color: white;
    background: linear-gradient(120deg, #1F2A44 0%, #0F9D8A 100%);
    margin-bottom: 1rem;
}
.hero h1 {
    margin: 0;
    font-size: 2.2rem;
    color: white;
}
.hero p {
    margin: .3rem 0 0 0;
    opacity: .9;
    font-size: 1.05rem;
}
.step {
    border: 1px solid #d5dbe3;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    height: 100%;
}
.answer {
    border-left: 6px solid #0F9D8A;
    background: rgba(15,157,138,.10);
    padding: 1rem 1.2rem;
    border-radius: 10px;
    font-size: 1.05rem;
}
.answer.nf {
    border-left-color: #E08A00;
    background: rgba(224,138,0,.12);
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: .8rem;
    color: white;
    margin-left: 8px;
}
mark {
    background: #FFE066;
    color: black;
    padding: 0 2px;
    border-radius: 3px;
}
.ev {
    border: 1px solid #d5dbe3;
    border-radius: 12px;
    padding: .8rem 1rem;
    margin-bottom: .4rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------- Helper Functions ----------------

@st.cache_resource
def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def highlight(text, question):
    safe = html.escape(text)

    for word in {
        word for word in re.findall(r"\w+", question)
        if len(word) > 3
    }:
        safe = re.sub(
            f"(?i)\\b({re.escape(word)})\\b",
            r"<mark>\1</mark>",
            safe
        )

    return safe


def match_label(score):
    if score > 0.5:
        return "Strong match", "#1B9E5A"
    if score > 0.3:
        return "Partial match", "#E08A00"
    return "Weak match", "#D64545"


def render_page(pdf_bytes, page_no, passage, zoom=1.4):
    """Render the cited PDF page with highlighted evidence."""
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

        png = page.get_pixmap(
            matrix=fitz.Matrix(zoom, zoom)
        ).tobytes("png")

        doc.close()
        return png

    except Exception:
        return None


def set_question(text):
    st.session_state.q = text


def all_document_text():
    """Text of every uploaded PDF, with file name and page number labels."""
    parts = []
    for document in st.session_state.documents.values():
        for page in document["pages"]:
            parts.append(f"[{document['name']} - Page {page['page']}]\n{page['text']}")
    return "\n\n".join(parts)


def show_generated_notes(state_key):
    """Show notes made from a website / YouTube video, with a Save button."""
    item = st.session_state.get(state_key)
    if not item:
        return
    st.subheader(item["title"])
    st.caption(f"Source: {item['source']}")
    st.markdown(item["notes"])
    with st.expander("View the extracted text"):
        st.write(item["text"])
    if st.button("💾 Save to Smart Notes", key=f"save_{state_key}"):
        save_note(item["title"], item["subject"], item["notes"])
        st.success("Saved! Open the Smart Notes tab to see it.")


# ---------------- Sidebar ----------------

with st.sidebar:
    st.header("📄 Documents")
    uploaded = st.file_uploader(
        "Upload PDF documents",
        type="pdf",
        accept_multiple_files=True
    )
    k = st.slider("Passages to retrieve", 1, 5, 3)
    style_label = st.selectbox(
        "Explanation style",
        ["Simple", "Detailed", "Step-by-step"]
    )
    style = style_label.lower()
    show_pages = st.toggle("Show highlighted PDF page", value=True)
    st.divider()
    st.subheader("🕘 Recent questions")
    history = get_history(limit=5)
    if not history:
        st.caption("No questions yet.")
    for h in history:
        st.caption(f"**{h['question']}**  \nPages: {h['pages']}")


# ---------------- Hero ----------------

st.markdown("""
<div class="hero">
    <h1>📚 StudyLens AI</h1>
    <p>Ask questions about your PDFs. Every answer shows the exact evidence it came from.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- Process the uploaded PDFs ----------------

has_docs = False
file_signature = None

if uploaded:
    file_payloads = [(file.name, file.getvalue()) for file in uploaded]
    file_signature = tuple(
        (name, hashlib.sha256(data).hexdigest()) for name, data in file_payloads
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
            for chunk in chunk_pages(pages_for_file):
                chunk["source_id"] = source_id
                chunk["source_name"] = file_name
                all_chunks.append(chunk)

            documents[source_id] = {
                "name": file_name,
                "pdf_bytes": pdf_bytes,
                "pages": pages_for_file,
            }

        if not all_chunks:
            st.session_state.pop("file_signature", None)
            st.error(
                "No extractable text found in the uploaded PDFs. "
                "They may be scanned images and OCR (Tesseract) is not installed."
            )
        else:
            with st.spinner("Reading and indexing your PDF documents..."):
                retriever = Retriever(model=load_model())
                retriever.build(all_chunks)

            st.session_state.update(
                file_signature=file_signature,
                documents=documents,
                chunks=all_chunks,
                retriever=retriever,
                file_name=", ".join(d["name"] for d in documents.values()),
                q="",
                last_key=None,
            )

    has_docs = st.session_state.get("file_signature") == file_signature

if has_docs:
    documents = st.session_state.documents
    chunks = st.session_state.chunks
    total_pages = sum(len(d["pages"]) for d in documents.values())
    empty = sum(count_empty_pages(d["pages"]) for d in documents.values())

    m1, m2, m3 = st.columns(3)
    m1.metric("PDFs uploaded", len(documents))
    m2.metric("Pages", total_pages)
    m3.metric("Chunks indexed", len(chunks))
    if empty:
        st.warning(f"{empty} page(s) have no extractable text (possibly scanned images).")


# ---------------- Main Tabs ----------------

tab_ask, tab_doc, tab_notes, tab_quiz, tab_study, tab_web = st.tabs([
    "💬 Ask",
    "📖 Browse documents",
    "📝 Smart Notes",
    "🧠 Quizzes & Tests",
    "🛠️ Study tools",
    "🌐 Web & video notes",
])


# ---------------- Ask Tab ----------------

with tab_ask:

    if not has_docs:
        c1, c2, c3 = st.columns(3)
        c1.markdown(
            '<div class="step"><b>1. Upload</b><br>Add one or more PDFs in the sidebar.</div>',
            unsafe_allow_html=True
        )
        c2.markdown(
            '<div class="step"><b>2. Ask</b><br>Type any question about your documents.</div>',
            unsafe_allow_html=True
        )
        c3.markdown(
            '<div class="step"><b>3. Verify</b><br>Check the cited pages and highlighted evidence.</div>',
            unsafe_allow_html=True
        )

    else:
        st.caption("Try an example:")
        e1, e2, e3 = st.columns(3)
        e1.button("Summarize the main idea", on_click=set_question,
                  args=("What is the main idea of this document?",), use_container_width=True)
        e2.button("Key definitions", on_click=set_question,
                  args=("What are the key definitions in this document?",), use_container_width=True)
        e3.button("Important points", on_click=set_question,
                  args=("What are the most important points?",), use_container_width=True)

        question = st.text_input("Your question", key="q", placeholder="e.g. What is overfitting?")

        if question:
            results = st.session_state.retriever.search(question, k=k)
            cache_key = (file_signature, question, k, style)
            doc_names = st.session_state.file_name

            if st.session_state.get("last_key") != cache_key:
                with st.spinner("Thinking..."):
                    try:
                        ans = answer(question, results, style=style)
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
                st.markdown(f'<div class="{cls}">{html.escape(ans)}</div>', unsafe_allow_html=True)

            st.subheader("Evidence from the documents")
            for i, result in enumerate(results, 1):
                label, color = match_label(result["score"])
                st.markdown(
                    f'<div class="ev"><b>#{i} · {html.escape(result["source_name"])} · '
                    f'Page {result["page"]}</b>'
                    f'<span class="badge" style="background:{color}">'
                    f'{label} · {result["score"]:.2f}</span><br><br>'
                    f'{highlight(result["text"], question)}</div>',
                    unsafe_allow_html=True
                )
                st.progress(max(0.0, min(1.0, result["score"])))

                if show_pages:
                    with st.expander(f"View {result['source_name']} - Page {result['page']}"):
                        source_document = documents[result["source_id"]]
                        img = render_page(source_document["pdf_bytes"], result["page"], result["text"])
                        if img:
                            st.image(img, use_container_width=True)
                        else:
                            st.caption("Could not render this page.")


# ---------------- Browse Documents Tab ----------------

with tab_doc:

    if has_docs:
        source_ids = list(documents.keys())
        selected_source_id = st.selectbox(
            "Choose a PDF",
            options=source_ids,
            format_func=lambda source_id: documents[source_id]["name"]
        )
        selected_pages = documents[selected_source_id]["pages"]
        page_no = st.number_input(
            "Page", min_value=1, max_value=len(selected_pages), value=1, key="browse_page"
        )
        st.text_area("Extracted text", selected_pages[page_no - 1]["text"], height=350)
    else:
        st.info("Upload a PDF in the sidebar to browse its pages.")


# ---------------- Web & Video Notes Tab ----------------
# (placed before Smart Notes in the code so a saved note appears in the list straight away)

with tab_web:

    st.header("🌐 Website to notes")
    st.caption("Paste a webpage link. Some websites block automatic reading - then copy the text into Smart Notes by hand.")
    website_url = st.text_input("Website URL", placeholder="https://example.com", key="website_url")

    if st.button("Generate website notes", key="generate_website_notes"):
        if not website_url.strip():
            st.warning("Please enter a website URL.")
        else:
            try:
                with st.spinner("Reading the website and writing notes..."):
                    website = extract_website_text(website_url)
                    source_text = website["text"][:12000]
                    notes = generate_website_notes(source_text)
                st.session_state["web_notes"] = {
                    "title": website["title"], "source": website["url"],
                    "notes": notes, "text": source_text, "subject": "Website",
                }
            except Exception as error:
                st.session_state.pop("web_notes", None)
                st.error(f"Website processing failed: {error}")
    show_generated_notes("web_notes")

    st.divider()
    st.header("🎥 YouTube video to notes")
    st.caption("Works only for videos that have captions / a transcript.")
    youtube_url = st.text_input(
        "YouTube video URL", placeholder="https://www.youtube.com/watch?v=...", key="youtube_url"
    )

    if st.button("Generate YouTube notes", key="generate_youtube_notes"):
        if not youtube_url.strip():
            st.warning("Please enter a YouTube video URL.")
        else:
            try:
                with st.spinner("Getting the transcript and writing notes..."):
                    video = extract_youtube_transcript(youtube_url)
                    transcript_text = video["text"][:12000]
                    notes = generate_website_notes(transcript_text)
                st.session_state["youtube_notes"] = {
                    "title": f"YouTube notes ({video['video_id']})", "source": video["url"],
                    "notes": notes, "text": transcript_text, "subject": "YouTube",
                }
            except Exception as error:
                st.session_state.pop("youtube_notes", None)
                st.error(f"YouTube processing failed: {error}")
    show_generated_notes("youtube_notes")


# ---------------- Smart Notes Tab ----------------

with tab_notes:

    st.header("📝 Smart Notes")
    st.write("Create, save, edit, and manage your personal study notes.")
    st.divider()
    st.subheader("🤖 Generate Notes with AI")

    if has_docs:

        if st.button("✨ Generate Notes from Uploaded PDFs"):
            with st.spinner("AI is preparing your study notes..."):
                try:
                    generated = generate_notes(all_document_text())
                    if generated.startswith("Error"):
                        st.error(generated)
                    else:
                        first_name = list(documents.values())[0]["name"].rsplit(".", 1)[0]
                        st.session_state["generated_notes_editor"] = generated
                        st.session_state["generated_notes_title"] = first_name + " - Study Notes"
                except Exception as e:
                    st.error(f"Could not generate notes: {e}")

        if "generated_notes_editor" in st.session_state:

            generated_title = st.text_input("Generated note title", key="generated_notes_title")
            st.text_area("Review and edit your generated notes", height=350, key="generated_notes_editor")

            if st.button("💾 Save AI-generated Notes"):
                if generated_title.strip() and st.session_state["generated_notes_editor"].strip():
                    save_note(
                        generated_title.strip(),
                        "AI Generated",
                        st.session_state["generated_notes_editor"]
                    )
                    del st.session_state["generated_notes_editor"]
                    del st.session_state["generated_notes_title"]
                    st.success("AI-generated notes saved successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a title and note content.")

    else:
        st.info("Upload a PDF in the sidebar before generating AI notes.")

    st.subheader("➕ Create a new note")

    with st.form("create_note_form"):
        new_title = st.text_input("Note title", placeholder="e.g. Introduction to Machine Learning")
        new_subject = st.text_input("Subject", placeholder="e.g. Artificial Intelligence")
        new_content = st.text_area("Note content", placeholder="Write your study notes here...", height=180)
        save_button = st.form_submit_button("💾 Save Note")

        if save_button:
            if not new_title.strip() or not new_content.strip():
                st.error("Please enter both a title and note content.")
            else:
                save_note(new_title.strip(), new_subject.strip(), new_content.strip())
                st.success("Your note has been saved!")
                st.rerun()

    st.divider()
    st.subheader("📚 Your saved notes")

    notes = get_notes()

    if not notes:
        st.info("You haven't saved any notes yet. Create your first note above!")
    else:
        for note in notes:
            with st.expander(f"📄 {note['title']}  |  {note['subject'] or 'No subject'}"):
                st.caption(f"Created: {note['created_at']}")
                st.write(note["content"])
                st.divider()
                st.write("✏️ Edit this note")

                with st.form(f"edit_note_{note['id']}"):
                    edit_title = st.text_input("Title", value=note["title"], key=f"title_{note['id']}")
                    edit_subject = st.text_input("Subject", value=note["subject"] or "", key=f"subject_{note['id']}")
                    edit_content = st.text_area("Content", value=note["content"], height=150, key=f"content_{note['id']}")
                    update_button = st.form_submit_button("Update Note")

                    if update_button:
                        if not edit_title.strip() or not edit_content.strip():
                            st.error("Title and content cannot be empty.")
                        else:
                            update_note(note["id"], edit_title.strip(), edit_subject.strip(), edit_content.strip())
                            st.success("Note updated successfully!")
                            st.rerun()

                if st.button("🗑️ Delete Note", key=f"delete_{note['id']}"):
                    delete_note(note["id"])
                    st.success("Note deleted.")
                    st.rerun()


# ---------------- Quizzes and Tests Tab ----------------

with tab_quiz:

    st.header("🧠 Quizzes & Tests")
    st.write("Generate a multiple-choice quiz from your uploaded study PDFs.")

    if has_docs:

        num_questions = st.slider(
            "Number of questions", min_value=1, max_value=20, value=5, key="quiz_num_questions"
        )

        if st.button("✨ Generate Quiz from Uploaded PDFs", key="generate_quiz_button"):

            previous_quiz = st.session_state.get("generated_quiz", {})
            for i in range(len(previous_quiz.get("questions", []))):
                answer_key = f"quiz_answer_{i}"
                if answer_key in st.session_state:
                    del st.session_state[answer_key]

            with st.spinner("AI is preparing your quiz..."):
                try:
                    generated = generate_document_quiz(all_document_text(), num_questions)

                    if isinstance(generated, dict) and "error" in generated:
                        st.session_state["quiz_generation_error"] = generated["error"]
                        st.session_state.pop("generated_quiz", None)
                    else:
                        st.session_state["generated_quiz"] = generated
                        st.session_state["quiz_submitted"] = False
                        st.session_state.pop("quiz_generation_error", None)

                except Exception as e:
                    st.session_state["quiz_generation_error"] = str(e)
                    st.session_state.pop("generated_quiz", None)

        if st.session_state.get("quiz_generation_error"):
            st.error(st.session_state["quiz_generation_error"])

        quiz = st.session_state.get("generated_quiz")

        if quiz and quiz.get("questions"):

            questions = quiz["questions"]
            st.success(f"Your quiz is ready! It contains {len(questions)} questions.")

            with st.form("generated_quiz_form"):

                for i, quiz_question in enumerate(questions):
                    st.markdown(f"**Question {i + 1}. {quiz_question['question']}**")
                    st.radio(
                        "Choose your answer:",
                        options=["A", "B", "C", "D"],
                        format_func=lambda option, opts=quiz_question["options"]: f"{option}. {opts[option]}",
                        key=f"quiz_answer_{i}",
                        index=None
                    )

                submitted = st.form_submit_button("Submit Quiz")
                if submitted:
                    st.session_state["quiz_submitted"] = True

            if st.session_state.get("quiz_submitted"):

                score = sum(
                    1 for i, q in enumerate(questions)
                    if st.session_state.get(f"quiz_answer_{i}") == q["correct_answer"]
                )
                percentage = (score / len(questions)) * 100

                st.divider()
                st.subheader("📊 Your Quiz Result")
                st.metric("Your Score", f"{score} / {len(questions)}", f"{percentage:.0f}%")

                if percentage >= 80:
                    st.success("Excellent work! You have a strong understanding of this material.")
                elif percentage >= 50:
                    st.info("Good effort! Review the explanations below to strengthen your understanding.")
                else:
                    st.warning("Keep practising. Review the correct answers and try again.")

                st.subheader("📝 Answer Review")

                for i, q in enumerate(questions):
                    user_answer = st.session_state.get(f"quiz_answer_{i}")
                    correct_answer = q["correct_answer"]

                    if user_answer == correct_answer:
                        st.success(f"Question {i + 1}: Correct")
                    elif user_answer is None:
                        st.warning(f"Question {i + 1}: Not answered")
                    else:
                        st.error(f"Question {i + 1}: Incorrect")

                    st.write(f"**Correct answer:** {correct_answer}. {q['options'][correct_answer]}")
                    st.write(f"**Explanation:** {q['explanation']}")
                    st.divider()

                if st.button("🔄 Generate a New Quiz", key="new_quiz_button"):
                    st.session_state.pop("generated_quiz", None)
                    st.session_state["quiz_submitted"] = False
                    st.rerun()

    else:
        st.info("Upload a PDF in the sidebar before generating a quiz.")


# ---------------- Study Tools Tab ----------------

with tab_study:
    if has_docs:
        render_study_tools(chunks, file_signature)
    else:
        st.info("Upload a PDF in the sidebar to use summaries, quizzes and flashcards.")


# ---------------- Footer ----------------

st.divider()
st.caption("StudyLens AI · Team: Reena, Harsha, Anjali, Shirin")
