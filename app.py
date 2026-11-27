
"""StudyLens AI - Explainable Study Assistant."""
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
from src.quiz_generator import generate_quiz
from src.study_tools_ui import render_study_tools

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


# ---------------- Sidebar ----------------

with st.sidebar:
    st.header("📄 Document")
uploaded = st.file_uploader(
    "Upload a PDF",
    type="pdf"
)

k = st.slider(
    "Passages to retrieve",
    1, 5, 3
)

style_label = st.selectbox(
    "Explanation style",
    ["Simple", "Detailed", "Step-by-step"]
)

style = style_label.lower()

show_pages = st.toggle(
    "Show highlighted PDF page",
    value=True
)
st.divider()
st.subheader("🕘 Recent questions")
history = get_history(limit=5)
if not history:
        st.caption("No questions yet.")

for h in history:
        st.caption(
            f"**{h['question']}**  \nPages: {h['pages']}"
        )


# ---------------- Hero ----------------

st.markdown("""
<div class="hero">
    <h1>📚 StudyLens AI</h1>
    <p>Ask questions about your PDF. Every answer shows the exact evidence it came from.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- Main Tabs ----------------
tab_ask, tab_doc, tab_notes, tab_quiz = st.tabs([
    "💬 Ask",
    "📖 Browse document",
    "📝 Smart Notes",
    "🧠 Quizzes & Tests"
])

tab_ask, tab_doc, tab_notes, tab_quiz, tab_study = st.tabs([
    "💬 Ask",
    "📖 Browse document",
    "📝 Smart Notes",
    "🧠 Quizzes & Tests",
    "🛠️ Study tools"
])
with tab_ask:

    if not uploaded:
        c1, c2, c3 = st.columns(3)

        c1.markdown(
            '<div class="step"><b>1. Upload</b><br>Add a lecture PDF in the sidebar.</div>',
            unsafe_allow_html=True
        )

    if question:
        results = st.session_state.retriever.search(question, k=k)
        cache_key = (st.session_state.file_name, question, k, style)
        if st.session_state.get("last_key") != cache_key:
            with st.spinner("Thinking..."):
                try:
                    ans = answer(question, results, style=style)
                except Exception as e:
                    ans = None
                    st.warning(f"LLM call failed: {e}")
                save_qa(question, ans or "", results, st.session_state.file_name)
                st.session_state.last_key, st.session_state.last_ans = cache_key, ans
        ans = st.session_state.last_ans
        c2.markdown(
            '<div class="step"><b>2. Ask</b><br>Type any question about the document.</div>',
            unsafe_allow_html=True
        )

        c3.markdown(
            '<div class="step"><b>3. Verify</b><br>Check the cited pages and highlighted evidence.</div>',
            unsafe_allow_html=True
        )

    else:

        if st.session_state.get("file_name") != uploaded.name:

            pdf_bytes = uploaded.getvalue()
            pages = extract_pages(pdf_bytes)
            chunks = chunk_pages(pages)

            if not chunks:
                st.error(
                    "No text found. This may be a scanned PDF (OCR is not supported yet)."
                )
                st.stop()

            with st.spinner(
                "Reading and indexing your document..."
            ):
                retriever = Retriever(model=load_model())
                retriever.build(chunks)

            st.session_state.update(
                file_name=uploaded.name,
                pdf_bytes=pdf_bytes,
                pages=pages,
                chunks=chunks,
                retriever=retriever,
                q=""
            )

        pages = st.session_state.pages
        chunks = st.session_state.chunks

        m1, m2, m3 = st.columns(3)

        m1.metric("Pages", len(pages))
        m2.metric("Chunks indexed", len(chunks))

        empty = count_empty_pages(pages)
        m3.metric("Pages without text", empty)

        if empty:
            st.warning(
                f"{empty} page(s) have no extractable text (possibly scanned images)."
            )

        st.caption("Try an example:")

        e1, e2, e3 = st.columns(3)

        e1.button(
            "Summarize the main idea",
            on_click=set_question,
            args=("What is the main idea of this document?",),
            use_container_width=True
        )

        e2.button(
            "Key definitions",
            on_click=set_question,
            args=("What are the key definitions in this document?",),
            use_container_width=True
        )

        e3.button(
            "Important points",
            on_click=set_question,
            args=("What are the most important points?",),
            use_container_width=True
        )

        question = st.text_input(
            "Your question",
            key="q",
            placeholder="e.g. What is overfitting?"
        )

        if question:

            results = st.session_state.retriever.search(
                question,
                k=k
            )

            cache_key = (
                st.session_state.file_name,
                question,
                k
            )

            if st.session_state.get("last_key") != cache_key:

                with st.spinner("Thinking..."):
                    try:
                        ans = answer(question, results)
                    except Exception as e:
                        ans = None
                        st.warning(f"LLM call failed: {e}")

                save_qa(
                    question,
                    ans or "",
                    results,
                    st.session_state.file_name
                )

                st.session_state.last_key = cache_key
                st.session_state.last_ans = ans

            ans = st.session_state.last_ans

            st.subheader("Answer")

            if ans is None:
                st.info(
                    "No LLM key set. Showing evidence only."
                )
            else:
                cls = (
                    "answer nf"
                    if ans.lower().startswith("not found")
                    else "answer"
                )

                st.markdown(
                    f'<div class="{cls}">{html.escape(ans)}</div>',
                    unsafe_allow_html=True
                )

            st.subheader("Evidence from the document")

            for i, result in enumerate(results, 1):

                label, color = match_label(
                    result["score"]
                )

                st.markdown(
                    f'<div class="ev"><b>#{i} · Page {result["page"]}</b>'
                    f'<span class="badge" style="background:{color}">'
                    f'{label} · {result["score"]:.2f}</span><br><br>'
                    f'{highlight(result["text"], question)}</div>',
                    unsafe_allow_html=True
                )

                st.progress(
                    max(0.0, min(1.0, result["score"]))
                )

                if show_pages:
                    with st.expander(
                        f"View page {result['page']} in the PDF"
                    ):

                        img = render_page(
                            st.session_state.pdf_bytes,
                            result["page"],
                            result["text"]
                        )

                        if img:
                            st.image(
                                img,
                                use_container_width=True
                            )
                        else:
                            st.caption(
                                "Could not render this page."
                            )


# ---------------- Browse Document Tab ----------------

with tab_doc:

    if (
        uploaded
        and "pages" in st.session_state
    ):
        pages = st.session_state.pages

        page_no = st.number_input(
            "Page",
            1,
            len(pages),
            1
        )

        st.text_area(
            "Extracted text",
            pages[page_no - 1]["text"],
            height=350
        )

    else:
        st.info(
            "Upload a PDF in the sidebar to browse its pages."
        )


# ---------------- Smart Notes Tab ----------------

with tab_notes:

    st.header("📝 Smart Notes")
    st.write(
        "Create, save, edit, and manage your personal study notes."
    )
    st.divider()
    st.subheader("🤖 Generate Notes with AI")

    if uploaded and "pages" in st.session_state:

        if st.button("✨ Generate Notes from Uploaded PDF"):

            document_text = "\n\n".join(
                f"[Page {i + 1}]\n{page['text']}"
                for i, page in enumerate(st.session_state.pages)
            )

            with st.spinner("AI is preparing your study notes..."):
                try:
                    generated = generate_notes(document_text)
                    st.session_state["generated_notes_editor"] = generated
                    st.session_state["generated_notes_title"] = (
                        uploaded.name.rsplit(".", 1)[0] + " - Study Notes"
                    )
                except Exception as e:
                    st.error(f"Could not generate notes: {e}")

        if "generated_notes_editor" in st.session_state:

            generated_title = st.text_input(
                "Generated note title",
                key="generated_notes_title"
            )

            st.text_area(
                "Review and edit your generated notes",
                height=350,
                key="generated_notes_editor"
            )

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

        new_title = st.text_input(
            "Note title",
            placeholder="e.g. Introduction to Machine Learning"
        )

        new_subject = st.text_input(
            "Subject",
            placeholder="e.g. Artificial Intelligence"
        )

        new_content = st.text_area(
            "Note content",
            placeholder="Write your study notes here...",
            height=180
        )

        save_button = st.form_submit_button(
            "💾 Save Note"
        )

        if save_button:

            if not new_title.strip() or not new_content.strip():
                st.error(
                    "Please enter both a title and note content."
                )

            else:
                save_note(
                    new_title.strip(),
                    new_subject.strip(),
                    new_content.strip()
                )

                st.success("Your note has been saved!")
                st.rerun()

    st.divider()

    st.subheader("📚 Your saved notes")

    notes = get_notes()

    if not notes:
        st.info(
            "You haven't saved any notes yet. Create your first note above!"
        )

    else:

        for note in notes:

            with st.expander(
                f"📄 {note['title']}  |  {note['subject'] or 'No subject'}"
            ):

                st.caption(
                    f"Created: {note['created_at']}"
                )

                st.write(note["content"])

                st.divider()
                st.write("✏️ Edit this note")

                with st.form(
                    f"edit_note_{note['id']}"
                ):

                    edit_title = st.text_input(
                        "Title",
                        value=note["title"],
                        key=f"title_{note['id']}"
                    )

                    edit_subject = st.text_input(
                        "Subject",
                        value=note["subject"] or "",
                        key=f"subject_{note['id']}"
                    )

                    edit_content = st.text_area(
                        "Content",
                        value=note["content"],
                        height=150,
                        key=f"content_{note['id']}"
                    )

                    update_button = st.form_submit_button(
                        "Update Note"
                    )

                    if update_button:

                        if not edit_title.strip() or not edit_content.strip():
                            st.error(
                                "Title and content cannot be empty."
                            )

                        else:
                            update_note(
                                note["id"],
                                edit_title.strip(),
                                edit_subject.strip(),
                                edit_content.strip()
                            )

                            st.success(
                                "Note updated successfully!"
                            )
                            st.rerun()

                if st.button(
                    "🗑️ Delete Note",
                    key=f"delete_{note['id']}"
                ):

                    delete_note(note["id"])

                    st.success("Note deleted.")
                    st.rerun()


# ---------------- Quizzes and Tests Tab ----------------

with tab_quiz:

    st.header("🧠 Quizzes & Tests")
    st.write("Generate a multiple-choice quiz from your uploaded study PDF.")

    if uploaded and "pages" in st.session_state:

        num_questions = st.slider(
            "Number of questions",
            min_value=1,
            max_value=20,
            value=5,
            key="quiz_num_questions"
        )

        if st.button("✨ Generate Quiz from Uploaded PDF", key="generate_quiz_button"):

            previous_quiz = st.session_state.get("generated_quiz", {})
            for i in range(len(previous_quiz.get("questions", []))):
                answer_key = f"quiz_answer_{i}"
                if answer_key in st.session_state:
                    del st.session_state[answer_key]

            document_text = "\n\n".join(
                f"[Page {i + 1}]\n{page['text']}"
                for i, page in enumerate(st.session_state.pages)
            )

            with st.spinner("AI is preparing your quiz..."):
                try:
                    generated = generate_quiz(document_text, num_questions)

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

                for i, question in enumerate(questions):
                    st.markdown(f"**Question {i + 1}. {question['question']}**")

                    option_keys = ["A", "B", "C", "D"]

                    st.radio(
                        "Choose your answer:",
                        options=option_keys,
                        format_func=lambda option, opts=question["options"]: (
                            f"{option}. {opts[option]}"
                        ),
                        key=f"quiz_answer_{i}",
                        index=None
                    )

                submitted = st.form_submit_button("Submit Quiz")

                if submitted:
                    st.session_state["quiz_submitted"] = True

            if st.session_state.get("quiz_submitted"):

                score = sum(
                    1 for i, question in enumerate(questions)
                    if st.session_state.get(f"quiz_answer_{i}") == question["correct_answer"]
                )

                percentage = (score / len(questions)) * 100

                st.divider()
                st.subheader("📊 Your Quiz Result")
                st.metric(
                    "Your Score",
                    f"{score} / {len(questions)}",
                    f"{percentage:.0f}%"
                )

                if percentage >= 80:
                    st.success("Excellent work! You have a strong understanding of this material.")
                elif percentage >= 50:
                    st.info("Good effort! Review the explanations below to strengthen your understanding.")
                else:
                    st.warning("Keep practising. Review the correct answers and try again.")

                st.subheader("📝 Answer Review")

                for i, question in enumerate(questions):
                    user_answer = st.session_state.get(f"quiz_answer_{i}")
                    correct_answer = question["correct_answer"]

                    if user_answer == correct_answer:
                        st.success(f"Question {i + 1}: Correct")
                    elif user_answer is None:
                        st.warning(f"Question {i + 1}: Not answered")
                    else:
                        st.error(f"Question {i + 1}: Incorrect")

                    st.write(
                        f"**Correct answer:** {correct_answer}. "
                        f"{question['options'][correct_answer]}"
                    )
                    st.write(f"**Explanation:** {question['explanation']}")
                    st.divider()

                if st.button("🔄 Generate a New Quiz", key="new_quiz_button"):
                    st.session_state.pop("generated_quiz", None)
                    st.session_state["quiz_submitted"] = False
                    st.rerun()

    else:
        st.info("Upload a PDF in the sidebar before generating a quiz.")



# ---------------- Footer ----------------

with tab_study:
    render_study_tools(chunks, st.session_state.file_name)
st.divider()

st.caption(
    "StudyLens AI · Team: Reena, Harsha, Anjali, Shirin"
)
