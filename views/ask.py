import html

import streamlit as st

from src import workspace as ws
from src.answerer import answer
from src.database import save_qa
from src.ui_theme import page_header

st.markdown(page_header("💬", "Ask your documents",
                        "Ask in your own words. Every answer comes with the exact passages and pages it used."),
            unsafe_allow_html=True)


def set_question(text):
    st.session_state.q = text


def main():
    if not ws.has_docs():
        ws.show_empty("ask questions and see the evidence")
        return

    k = st.session_state.get("k", 3)
    style = st.session_state.get("style_label", "Simple").lower()
    show_pages = st.session_state.get("show_pages", True)
    documents = ws.documents()
    file_signature = st.session_state.file_signature

    st.caption("Try an example:")
    e1, e2, e3 = st.columns(3)
    e1.button("Summarize the main idea", on_click=set_question,
              args=("What is the main idea of this document?",), use_container_width=True)
    e2.button("Key definitions", on_click=set_question,
              args=("What are the key definitions in this document?",), use_container_width=True)
    e3.button("Important points", on_click=set_question,
              args=("What are the most important points?",), use_container_width=True)

    question = st.text_input("Your question", key="q", placeholder="e.g. What is overfitting?")
    if not question:
        return

    results = st.session_state.retriever.search(question, k=k)
    cache_key = (file_signature, question, k, style)

    if st.session_state.get("last_key") != cache_key:
        with st.spinner("Thinking..."):
            try:
                ans = answer(question, results, style=style)
            except Exception as e:
                ans = None
                st.warning(f"The AI call failed: {e}")
        save_qa(question, ans or "", results, st.session_state.file_name)
        st.session_state.last_key = cache_key
        st.session_state.last_ans = ans

    ans = st.session_state.last_ans

    history = st.session_state.chat_history
    if not history or history[-1]["question"] != question:
        history.append({"question": question, "answer": ans or "No answer available."})

    st.subheader("Answer")
    if ans is None:
        st.info("No AI key is set, so only the evidence is shown. Add GROQ_API_KEY to your .env file.")
    else:
        cls = "answer nf" if ans.lower().startswith("not found") else "answer"
        st.markdown(f'<div class="{cls}">{html.escape(ans)}</div>', unsafe_allow_html=True)

    st.subheader("Evidence from the documents")
    for i, result in enumerate(results, 1):
        label, color = ws.match_label(result["score"])
        st.markdown(
            f'<div class="ev"><b>#{i} · {html.escape(result["source_name"])} · '
            f'Page {result["page"]}</b>'
            f'<span class="badge" style="background:{color}">{label} · {result["score"]:.2f}</span>'
            f'<br><br>{ws.highlight(result["text"], question)}</div>',
            unsafe_allow_html=True,
        )
        st.progress(max(0.0, min(1.0, result["score"])))

        if show_pages:
            with st.expander(f"View {result['source_name']} - Page {result['page']}"):
                src = documents[result["source_id"]]
                img = ws.render_page(src["pdf_bytes"], result["page"], result["text"])
                if img:
                    st.image(img, use_container_width=True)
                else:
                    st.caption("Could not render this page.")


main()
