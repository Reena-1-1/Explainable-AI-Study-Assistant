from streamlit.testing.v1 import AppTest

SCRIPT = """
import src.study_tools_ui as ui
ui.summarize = lambda chunks, mode: "SUMMARY for " + mode
ui.generate_quiz = lambda chunks, n=5: [
    {"question": "Q one?", "options": ["a", "b", "c", "d"], "answer": "b", "explanation": "because b", "page": 2},
    {"question": "Q two?", "options": ["w", "x", "y", "z"], "answer": "z", "explanation": "because z", "page": 3},
]
ui.generate_flashcards = lambda chunks, n=8: [
    {"front": "F1", "back": "B1", "page": 1}, {"front": "F2", "back": "B2", "page": None}]
ui.render_study_tools([{"page": 1, "text": "hello"}], "doc.pdf")
"""


def run():
    return AppTest.from_string(SCRIPT, default_timeout=30).run()


def test_page_loads_with_three_tabs():
    at = run()
    assert not at.exception
    assert [t.label for t in at.tabs] == ["Summary", "Quiz", "Flashcards"]


def test_summary_is_generated():
    at = run()
    at.button(key="gen_summary").click().run()
    assert not at.exception
    assert any("SUMMARY for short" in m.value for m in at.markdown)


def test_quiz_is_scored():
    at = run()
    at.button(key="gen_quiz").click().run()
    at.radio(key="quiz_q0").set_value("b")      # correct
    at.radio(key="quiz_q1").set_value("w")      # wrong
    at.run()
    at.button(key="submit_quiz").click().run()
    assert not at.exception
    assert at.metric[0].value == "1 / 2"


def test_flashcards_flip_and_navigate():
    at = run()
    at.button(key="gen_cards").click().run()
    assert any("F1" in m.value for m in at.markdown)
    at.button(key="card_flip").click().run()
    assert any("B1" in s.value for s in at.success)
    at.button(key="card_next").click().run()
    assert any("F2" in m.value for m in at.markdown)
    at.button(key="card_known").click().run()   # marks card 2 known, wraps to card 1
    assert not at.exception


def test_ai_error_is_shown_not_crashed():
    script = SCRIPT.replace('lambda chunks, mode: "SUMMARY for " + mode', 'lambda chunks, mode: 1/0')
    at = AppTest.from_string(script, default_timeout=30).run()
    at.button(key="gen_summary").click().run()
    assert not at.exception
    assert any("Could not generate the summary" in e.value for e in at.error)


def test_no_api_key_shows_info():
    script = SCRIPT.replace('lambda chunks, mode: "SUMMARY for " + mode', 'lambda chunks, mode: None')
    at = AppTest.from_string(script, default_timeout=30).run()
    at.button(key="gen_summary").click().run()
    assert any("GROQ_API_KEY" in i.value for i in at.info)
