import json

from src import flashcard_generator as fg

CHUNKS = [{"page": i + 1, "text": f"Fact number {i} about topic {i}. " * 10, "chunk_id": i}
          for i in range(5)]


def test_parse_plain_and_fenced_json():
    data = [{"front": "a", "back": "b", "page": 1}]
    assert fg.parse_json_list(json.dumps(data)) == data
    assert fg.parse_json_list("Sure!\n```json\n" + json.dumps(data) + "\n```") == data


def test_parse_garbage_gives_empty_list():
    assert fg.parse_json_list("") == []
    assert fg.parse_json_list("no json here") == []
    assert fg.parse_json_list("[not valid json") == []
    assert fg.parse_json_list('{"front": "x"}') == []


def test_clean_drops_incomplete_and_duplicate_cards():
    items = [{"front": "What is X?", "back": "A thing", "page": 1},
             {"front": "what is x?", "back": "Again", "page": 1},
             {"front": "", "back": "no front"},
             {"front": "no back", "back": ""},
             "junk"]
    cards = fg.clean_cards(items)
    assert [c["front"] for c in cards] == ["What is X?"]


def test_page_must_exist_in_document():
    items = [{"front": "q1", "back": "a1", "page": 3},
             {"front": "q2", "back": "a2", "page": 99},
             {"front": "q3", "back": "a3", "page": "2"},
             {"front": "q4", "back": "a4"}]
    pages = [c["page"] for c in fg.clean_cards(items, valid_pages={2, 3})]
    assert pages == [3, None, 2, None]


def test_prompt_is_grounded_and_has_page_labels():
    p = fg.build_prompt(CHUNKS, 4)
    assert "ONLY the document text" in p and "[p. 1]" in p and "4 study flashcards" in p


def test_generate_returns_cards(monkeypatch):
    reply = json.dumps([{"front": f"Q{i}", "back": f"A{i}", "page": 1} for i in range(10)])
    monkeypatch.setattr(fg.llm, "chat", lambda *a, **k: reply)
    cards = fg.generate_flashcards(CHUNKS, n=3)
    assert len(cards) == 3 and cards[0] == {"front": "Q0", "back": "A0", "page": 1}


def test_no_key_returns_none(monkeypatch):
    monkeypatch.setattr(fg.llm, "chat", lambda *a, **k: None)
    assert fg.generate_flashcards(CHUNKS) is None


def test_empty_document_gives_no_cards():
    assert fg.generate_flashcards([]) == []


def test_unparseable_reply_gives_empty_list(monkeypatch):
    monkeypatch.setattr(fg.llm, "chat", lambda *a, **k: "Sorry, I cannot do that.")
    assert fg.generate_flashcards(CHUNKS) == []
