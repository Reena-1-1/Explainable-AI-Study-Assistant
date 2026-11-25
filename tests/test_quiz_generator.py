import json
import random

from src import quiz_generator as qg

GOOD = {"question": "What is overfitting?",
        "options": ["Memorising training data", "Fast training", "Low memory", "Big data"],
        "answer": "Memorising training data",
        "explanation": "The text says overfitting means memorising the training data.",
        "page": 4}


def test_prompt_is_grounded_and_asks_for_json():
    chunks = [{"page": 2, "text": "Deep learning uses neural networks.", "chunk_id": 0}]
    p = qg.build_prompt(chunks, 3)
    assert "ONLY the document text" in p and "JSON array" in p and "[p. 2]" in p
    assert "3 multiple-choice" in p


def test_parses_clean_json():
    quiz = qg.parse_quiz(json.dumps([GOOD]), shuffle=False)
    assert quiz == [GOOD]


def test_parses_json_inside_code_fences_and_text():
    raw = "Here you go:\n```json\n" + json.dumps([GOOD]) + "\n```\nHope it helps!"
    assert len(qg.parse_quiz(raw)) == 1


def test_letter_answer_is_converted_to_option_text():
    q = dict(GOOD, answer="B")
    assert qg.parse_quiz(json.dumps([q]), shuffle=False)[0]["answer"] == "Fast training"


def test_malformed_questions_are_dropped():
    bad = [dict(GOOD, options=["a", "b", "c"]),                 # only 3 options
           dict(GOOD, answer="not an option"),                   # answer not in options
           dict(GOOD, options=["a", "a", "b", "c"]),             # duplicate options
           dict(GOOD, explanation=""),                           # no explanation
           "junk"]
    assert qg.parse_quiz(json.dumps(bad + [GOOD])) != []
    assert len(qg.parse_quiz(json.dumps(bad + [GOOD]))) == 1


def test_garbage_reply_gives_empty_list():
    assert qg.parse_quiz("sorry, I cannot do that") == []
    assert qg.parse_quiz("[not json") == []


def test_shuffle_keeps_answer_among_options():
    quiz = qg.parse_quiz(json.dumps([GOOD]), rng=random.Random(1))
    assert quiz[0]["answer"] in quiz[0]["options"]
    assert sorted(quiz[0]["options"]) == sorted(GOOD["options"])


def test_generate_quiz_end_to_end_with_fake_llm(monkeypatch):
    chunks = [{"page": 4, "text": "Overfitting is memorising data.", "chunk_id": 0}]
    monkeypatch.setattr(qg.llm, "chat", lambda *a, **k: json.dumps([GOOD, GOOD]))
    assert len(qg.generate_quiz(chunks, n=1)) == 1


def test_no_key_returns_none_and_empty_doc_returns_empty(monkeypatch):
    monkeypatch.setattr(qg.llm, "chat", lambda *a, **k: None)
    assert qg.generate_quiz([{"page": 1, "text": "x", "chunk_id": 0}]) is None
    assert qg.generate_quiz([]) == []