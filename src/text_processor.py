"""Cleaning + sentence-aware chunking. Owner: Harsha."""
import re


def clean_text(text: str) -> str:
    text = text.replace("\u00ad", "")          # soft hyphens
    text = re.sub(r"-\n(\w)", r"\1", text)     # re-join hyphenated line breaks
    text = re.sub(r"\s+", " ", text)           # collapse whitespace
    return text.strip()


def split_sentences(text: str):
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p for p in parts if p]


def _hard_split(s: str, size: int):
    return [s[i:i + size] for i in range(0, len(s), size)]


def chunk_pages(pages, size: int = 1000, overlap: int = 200):
    """pages: [{"page", "text"}]  ->  [{"chunk_id", "page", "text"}]
    Chunks end at sentence boundaries; each keeps its page number."""
    chunks = []
    for p in pages:
        sentences = []
        for s in split_sentences(clean_text(p["text"])):
            sentences.extend(_hard_split(s, size) if len(s) > size else [s])

        cur, cur_len = [], 0
        for s in sentences:
            if cur and cur_len + len(s) + 1 > size:
                chunks.append({"page": p["page"], "text": " ".join(cur)})
                keep, total = [], 0
                for t in reversed(cur):
                    if total + len(t) > overlap:
                        break
                    keep.insert(0, t)
                    total += len(t) + 1
                cur, cur_len = keep, total
            cur.append(s)
            cur_len += len(s) + 1
        if cur:
            chunks.append({"page": p["page"], "text": " ".join(cur)})

    for i, c in enumerate(chunks):
        c["chunk_id"] = i
    return chunks
