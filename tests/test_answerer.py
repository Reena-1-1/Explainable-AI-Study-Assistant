from src import answerer
from src.answerer import build_prompt, answer, NOT_FOUND, STYLES

RESULTS = [{"page": 2, "text": "Deep learning uses many-layered neural networks.", "score": 0.8}]


def test_each_style_changes_prompt():
    prompts = {s: build_prompt("What is DL?", RESULTS, s) for s in STYLES}
    assert len(set(prompts.values())) == 3
    assert "numbered list" in prompts["step-by-step"]


def test_unknown_style_falls_back_to_simple():
    assert build_prompt("q", RESULTS, "weird") == build_prompt("q", RESULTS, "simple")


def test_prompt_keeps_grounding_rules():
    p = build_prompt("q", RESULTS)
    assert "ONLY the passages" in p and "[p. 2]" in p and NOT_FOUND in p


def test_no_key_returns_none(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(answerer, "load_dotenv", lambda *a, **k: None)
    assert answer("q", RESULTS) is None


def test_no_results_returns_not_found(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "x")
    assert answer("q", []) == NOT_FOUND


def test_old_call_signature_still_works(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "x")

    class R:
        def raise_for_status(self): pass
        def json(self): return {"choices": [{"message": {"content": " ok (p. 2) "}}]}
    monkeypatch.setattr(answerer.requests, "post", lambda *a, **k: R())
    assert answer("q", RESULTS) == "ok (p. 2)"
    assert answer("q", RESULTS, style="detailed") == "ok (p. 2)"