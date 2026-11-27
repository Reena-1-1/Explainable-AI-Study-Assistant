import streamlit as st

from src import workspace as ws
from src.document_quiz import generate_document_quiz
from src.ui_theme import page_header

st.markdown(page_header("🧠", "Quizzes & Tests",
                        "Test yourself on your whole document. You get a score and an explanation for every answer."),
            unsafe_allow_html=True)


def main():
    if not ws.has_docs():
        ws.show_empty("generate a quiz")
        return

    num_questions = st.slider("Number of questions", 1, 20, 5, key="quiz_num_questions")

    if st.button("✨ Generate quiz", key="generate_quiz_button", type="primary"):
        previous = st.session_state.get("generated_quiz", {})
        for i in range(len(previous.get("questions", []))):
            st.session_state.pop(f"quiz_answer_{i}", None)

        with st.spinner("AI is preparing your quiz..."):
            try:
                generated = generate_document_quiz(ws.all_document_text(), num_questions)
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
    if not (quiz and quiz.get("questions")):
        return

    questions = quiz["questions"]
    st.success(f"Your quiz is ready: {len(questions)} questions.")

    with st.form("generated_quiz_form"):
        for i, q in enumerate(questions):
            st.markdown(f"**Question {i + 1}. {q['question']}**")
            st.radio(
                "Choose your answer:", options=["A", "B", "C", "D"],
                format_func=lambda option, opts=q["options"]: f"{option}. {opts[option]}",
                key=f"quiz_answer_{i}", index=None,
            )
        if st.form_submit_button("Submit quiz", type="primary"):
            st.session_state["quiz_submitted"] = True

    if not st.session_state.get("quiz_submitted"):
        return

    score = sum(1 for i, q in enumerate(questions)
                if st.session_state.get(f"quiz_answer_{i}") == q["correct_answer"])
    percentage = score / len(questions) * 100

    st.divider()
    st.subheader("📊 Your result")
    st.metric("Your score", f"{score} / {len(questions)}", f"{percentage:.0f}%")

    if percentage >= 80:
        st.success("Excellent work. You have a strong grasp of this material.")
    elif percentage >= 50:
        st.info("Good effort. Read the explanations below to strengthen weak spots.")
    else:
        st.warning("Keep practising. Review the correct answers, then try a new quiz.")

    st.subheader("📝 Answer review")
    for i, q in enumerate(questions):
        user_answer = st.session_state.get(f"quiz_answer_{i}")
        correct = q["correct_answer"]
        if user_answer == correct:
            st.success(f"Question {i + 1}: Correct")
        elif user_answer is None:
            st.warning(f"Question {i + 1}: Not answered")
        else:
            st.error(f"Question {i + 1}: Incorrect")
        st.write(f"**Correct answer:** {correct}. {q['options'][correct]}")
        st.write(f"**Explanation:** {q['explanation']}")
        st.divider()

    if st.button("🔄 Generate a new quiz", key="new_quiz_button"):
        st.session_state.pop("generated_quiz", None)
        st.session_state["quiz_submitted"] = False
        st.rerun()


main()
