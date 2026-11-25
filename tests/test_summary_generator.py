from src import summary_generator as sg

CHUNKS = [{"page": i + 1, "text": f"Sentence about topic {i}. " * 20, "chunk_id": i}
          for i in range(60)]


def test_every_mode_gives_a_different_prompt():
    prompts = {m: sg.build_prompt(CHUNKS, m) for m in sg.MODES}
    assert len(set(prompts.values())) == len(sg.MODES)


def test_unknown_mode_falls_back_to_short():
    assert sg.build_prompt(CHUNKS, "zzz") == sg.build_prompt(CHUNKS, "short")


def test_prompt_is_grounded_and_has_pages():
    p = sg.build_prompt(CHUNKS, "short")
    assert "ONLY the document text" in p and "[p. 1]" in p


def test_selection_respects_budget_and_covers_document():
    chosen = sg.select_chunks(CHUNKS, max_chars=3000)
    assert sum(len(c["text"]) for c in chosen) <= 3000 + len(CHUNKS[0]["text"])
    assert chosen[0]["page"] == 1 and chosen[-1]["page"] > 30


def test_small_document_keeps_everything():
    assert sg.select_chunks(CHUNKS[:3]) == CHUNKS[:3]


def test_empty_document_is_not_found():
    assert sg.summarize([], "short") == "Not found in the document."


def test_no_key_returns_none(monkeypatch):
    monkeypatch.setattr(sg.llm, "chat", lambda *a, **k: None)
    assert sg.summarize(CHUNKS, "short") is None