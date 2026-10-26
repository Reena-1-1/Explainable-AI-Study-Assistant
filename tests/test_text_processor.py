from src.text_processor import clean_text, chunk_pages


def test_clean_text_collapses_whitespace():
    assert clean_text("a   b\n\nc") == "a b c"


def test_chunks_keep_page_numbers():
    pages = [{"page": 1, "text": "One. Two."}, {"page": 5, "text": "Three. Four."}]
    assert {c["page"] for c in chunk_pages(pages)} == {1, 5}


def test_chunks_respect_size_and_end_at_sentences():
    text = " ".join(f"This is sentence number {i}." for i in range(100))
    chunks = chunk_pages([{"page": 1, "text": text}], size=200, overlap=50)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c["text"]) <= 200
        assert c["text"].endswith(".")


def test_overlap_shares_text():
    text = " ".join(f"Sentence {i} here." for i in range(60))
    c = chunk_pages([{"page": 1, "text": text}], size=200, overlap=60)
    assert c[1]["text"].split(".")[0] in c[0]["text"]


def test_empty_page_gives_no_chunks():
    assert chunk_pages([{"page": 1, "text": "   "}]) == []
    
    


def test_long_text_without_full_stops():
    text = "word " * 500
    pages = [{"page": 1, "text": text}]
    chunks = chunk_pages(pages, size=200, overlap=20)

    assert len(chunks) > 1
    assert all(len(chunk["text"]) <= 200 for chunk in chunks)


def test_chunk_ids_are_sequential():
    text = "This is a sample sentence. " * 30
    pages = [{"page": 1, "text": text}]
    chunks = chunk_pages(pages, size=100, overlap=20)

    assert [chunk["chunk_id"] for chunk in chunks] == list(range(len(chunks)))

