"""Streamlit tab with AI study tools: summary, quiz and flashcards. Owner: Reena.

Use in app.py:   render_study_tools(chunks, doc_key)
  chunks  = list of chunks of the uploaded document (from chunk_pages)
  doc_key = any value that changes when another document is loaded (e.g. the file name)
"""
import streamlit as st

from src.flashcard_generator import generate_flashcards
from src.quiz_generator import generate_quiz
from src.summary_generator import MODES, summarize

MODE_LABELS = {
    "short": "Short summary",
    "detailed": "Detailed summary",
    "key_points": "Key points",
    "definitions": "Important definitions",
    "exam_notes": "Exam revision notes",
}
NO_KEY = "No GROQ_API_KEY found in .env, so the AI features are switched off."
STATE_KEYS = ("study_summary", "study_quiz", "study_submitted", "study_cards",
              "study_card_i", "study_show_back", "study_known")


def _reset_when_document_changes(doc_key):
    if st.session_state.get("study_doc") != doc_key:
        for key in STATE_KEYS:
            st.session_state.pop(key, None)
        st.session_state.study_doc = doc_key


def _run(function, *args):
    """Call an AI function; never crash the page. Returns (result, error_text)."""
    try:
        with st.spinner("The AI is working..."):
            return function(*args), None
    except Exception as error:  # Groq errors (429 rate limit, network ...)
        return None, str(error)


# ------------------------------------------------------------------ summary
def _summary_tab(chunks):
    mode = st.selectbox("Type of summary", list(MODES), format_func=lambda m: MODE_LABELS.get(m, m),
                        key="summary_mode")
    if st.button("Generate summary", key="gen_summary"):
        text, error = _run(summarize, chunks, mode)
        if error:
            st.error(f"Could not generate the summary: {error}")
        elif text is None:
            st.info(NO_KEY)
        else:
            st.session_state.study_summary = (mode, text)

    saved = st.session_state.get("study_summary")
    if saved:
        st.caption(MODE_LABELS.get(saved[0], saved[0]))
        st.markdown(saved[1])
        st.download_button("Download as text file", saved[1], file_name="summary.txt", key="dl_summary")


# --------------------------------------------------------------------- quiz
def _clear_quiz_answers():
    for key in [k for k in st.session_state if str(k).startswith("quiz_q")]:
        del st.session_state[key]


def _quiz_tab(chunks):
    n = st.slider("Number of questions", 3, 10, 5, key="quiz_n")
    if st.button("Generate quiz", key="gen_quiz"):
        quiz, error = _run(generate_quiz, chunks, n)
        if error:
            st.error(f"Could not generate the quiz: {error}")
        elif quiz is None:
            st.info(NO_KEY)
        elif not quiz:
            st.warning("The AI reply could not be used this time. Click the button again.")
        else:
            _clear_quiz_answers()
            st.session_state.study_quiz = quiz
            st.session_state.study_submitted = False

    quiz = st.session_state.get("study_quiz")
    if not quiz:
        return
    submitted = st.session_state.get("study_submitted", False)

    for i, q in enumerate(quiz):
        page = f"  (p. {q['page']})" if q.get("page") else ""
        st.markdown(f"**Q{i + 1}. {q['question']}**{page}")
        choice = st.radio("Choose one answer", q["options"], index=None, key=f"quiz_q{i}",
                          disabled=submitted, label_visibility="collapsed")
        if submitted:
            if choice == q["answer"]:
                st.success("Correct")
            else:
                st.error(f"Your answer: {choice or 'not answered'}  |  Correct answer: {q['answer']}")
            if q.get("explanation"):
                st.caption(q["explanation"])

    if not submitted:
        if st.button("Submit answers", key="submit_quiz"):
            st.session_state.study_submitted = True
            st.rerun()
    else:
        score = sum(1 for i, q in enumerate(quiz) if st.session_state.get(f"quiz_q{i}") == q["answer"])
        st.metric("Your score", f"{score} / {len(quiz)}")


# --------------------------------------------------------------- flashcards
def _go(step):
    cards = st.session_state.get("study_cards") or []
    if cards:
        st.session_state.study_card_i = (st.session_state.get("study_card_i", 0) + step) % len(cards)
        st.session_state.study_show_back = False


def _flip():
    st.session_state.study_show_back = not st.session_state.get("study_show_back", False)


def _mark(known):
    i = st.session_state.get("study_card_i", 0)
    st.session_state.setdefault("study_known", {})[i] = known
    _go(1)


def _cards_tab(chunks):
    n = st.slider("Number of cards", 4, 15, 8, key="cards_n")
    if st.button("Generate flashcards", key="gen_cards"):
        cards, error = _run(generate_flashcards, chunks, n)
        if error:
            st.error(f"Could not generate flashcards: {error}")
        elif cards is None:
            st.info(NO_KEY)
        elif not cards:
            st.warning("The AI reply could not be used this time. Click the button again.")
        else:
            st.session_state.study_cards = cards
            st.session_state.study_card_i = 0
            st.session_state.study_show_back = False
            st.session_state.study_known = {}

    cards = st.session_state.get("study_cards")
    if not cards:
        return
    i = st.session_state.get("study_card_i", 0)
    card = cards[i]
    known = st.session_state.get("study_known", {})

    st.progress((i + 1) / len(cards))
    st.caption(f"Card {i + 1} of {len(cards)}   |   Known: {sum(known.values())}   |   "
               f"Needs revision: {sum(1 for v in known.values() if not v)}")
    st.markdown(f"### {card['front']}")
    if st.session_state.get("study_show_back"):
        page = f"  (p. {card['page']})" if card.get("page") else ""
        st.success(card["back"] + page)

    c1, c2, c3 = st.columns(3)
    c1.button("Previous", key="card_prev", on_click=_go, args=(-1,))
    c2.button("Hide answer" if st.session_state.get("study_show_back") else "Show answer",
              key="card_flip", on_click=_flip)
    c3.button("Next", key="card_next", on_click=_go, args=(1,))
    k1, k2 = st.columns(2)
    k1.button("I know this", key="card_known", on_click=_mark, args=(True,))
    k2.button("Needs revision", key="card_revise", on_click=_mark, args=(False,))


# --------------------------------------------------------------------- main
def render_study_tools(chunks, doc_key=""):
    _reset_when_document_changes(doc_key)
    st.caption("Everything here is created only from your uploaded document.")
    tab_summary, tab_quiz, tab_cards = st.tabs(["Summary", "Quiz", "Flashcards"])
    with tab_summary:
        _summary_tab(chunks)
    with tab_quiz:
        _quiz_tab(chunks)
    with tab_cards:
        _cards_tab(chunks)
