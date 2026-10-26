import pytest
pytest.importorskip("sentence_transformers")
pytest.importorskip("faiss")
from src.retriever import Retriever


def test_search_returns_relevant_page():
    chunks = [
        {"text": "Photosynthesis converts sunlight into energy.", "page": 1},
        {"text": "The French Revolution began in 1789.", "page": 2},
    ]
    r = Retriever(); r.build(chunks)
    assert r.search("When did the French Revolution start?", k=1)[0]["page"] == 2


def test_search_before_build_is_empty():
    r = Retriever.__new__(Retriever)
    r.index, r.chunks = None, []
    assert r.search("anything") == []
