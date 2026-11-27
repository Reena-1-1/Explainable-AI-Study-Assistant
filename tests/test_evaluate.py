from evaluate import evaluate, load_questions


class FakeRetriever:
    """Returns scripted results so the maths can be checked without any AI model."""

    def __init__(self, table):
        self.table = table

    def search(self, question, k=3):
        return self.table.get(question, [])[:k]


def res(*pairs):
    return [{"page": p, "score": s} for p, s in pairs]


def test_load_tab_and_comma_files_and_multiple_pages(tmp_path):
    tab = tmp_path / "t.csv"
    tab.write_text("question\texpected_page\tanswerable\nQ1?\t2|4\tyes\nQ2?\t0\tno\n", encoding="utf-8")
    comma = tmp_path / "c.csv"
    comma.write_text('question,expected_page\n"Q1, with comma?",3\nQ2?,0\n', encoding="utf-8")
    a, b = load_questions(str(tab)), load_questions(str(comma))
    assert a[0]["pages"] == {2, 4} and a[0]["answerable"] and not a[1]["answerable"]
    assert b[0]["question"] == "Q1, with comma?" and b[0]["answerable"] and not b[1]["answerable"]


def test_top1_top3_and_refusal_maths():
    qs = [{"question": "A", "pages": {1}, "answerable": True},
          {"question": "B", "pages": {2}, "answerable": True},
          {"question": "C", "pages": {3}, "answerable": True},
          {"question": "X", "pages": set(), "answerable": False},
          {"question": "Y", "pages": set(), "answerable": False}]
    fake = FakeRetriever({
        "A": res((1, 0.6), (5, 0.3)),            # top-1 hit
        "B": res((7, 0.5), (2, 0.4)),            # top-3 hit only
        "C": res((8, 0.3), (9, 0.2)),            # miss
        "X": res((1, 0.05)),                     # weak -> refused
        "Y": res((2, 0.35)),                     # strong -> would not be refused
    })
    rows, s = evaluate(fake, qs, threshold=0.2)
    assert s["top1"] == 1 / 3 and s["top3"] == 2 / 3
    assert s["refused"] == 0.5
    assert s["answers_kept"] == 1.0
    assert rows[0]["top1"] and not rows[1]["top1"] and rows[1]["top3"] and not rows[2]["top3"]


def test_threshold_table_and_empty_results():
    qs = [{"question": "A", "pages": {1}, "answerable": True},
          {"question": "X", "pages": set(), "answerable": False}]
    fake = FakeRetriever({"A": res((1, 0.45))})   # X returns nothing -> score 0
    rows, s = evaluate(fake, qs, threshold=0.2)
    assert rows[1]["top_score"] == 0.0 and rows[1]["refused"]
    kept = {t: k for t, k, _ in s["sweep"]}
    assert kept[0.40] == 1.0 and kept[0.50] == 0.0


def test_only_answerable_or_only_unanswerable_does_not_crash():
    rows, s = evaluate(FakeRetriever({}), [{"question": "X", "pages": set(), "answerable": False}])
    assert s["top1"] is None and s["refused"] == 1.0
