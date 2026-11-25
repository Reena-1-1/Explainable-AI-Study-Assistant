"""Flashcards (front/back) grounded in the uploaded document. Owner: Reena.

generate_flashcards(chunks, n=8) -> [{"front", "back", "page"}, ...]
Returns None if no GROQ_API_KEY is set (same convention as answerer / summary generator).
"""
import json
import re

from src import llm
from src.summary_generator import select_chunks

PROMPT = """Create {n} study flashcards using ONLY the document text below.
Rules:
- front = a short question or a term; back = a short, clear answer (1-2 sentences).
- Every card must be answerable from the text. Do not invent facts or use outside knowledge.
- page = the page number from the [p. N] label of the passage the card comes from.
- No two cards about the same thing.
Reply with ONLY a JSON list, no other words:
[{{"front": "...", "back": "...", "page": 3}}]

Document text:
{text}"""


def parse_json_list(raw: str):
    """Get a JSON list out of the model reply (handles ```json fences and extra words)."""
    if not raw:
        return []
    text = re.sub(r"```(?:json)?", "", raw)
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end <= start:
        return []
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def clean_cards(items, valid_pages=None):
    """Keep only good cards: both sides present, no duplicates, page must really exist."""
    cards, seen = [], set()
    for item in items:
        if not isinstance(item, dict):
            continue
        front = str(item.get("front", "")).strip()
        back = str(item.get("back", "")).strip()
        if not front or not back or front.lower() in seen:
            continue
        seen.add(front.lower())
        page = item.get("page")
        if isinstance(page, str) and page.strip().isdigit():
            page = int(page)
        if not isinstance(page, int) or (valid_pages is not None and page not in valid_pages):
            page = None
        cards.append({"front": front, "back": back, "page": page})
    return cards


def build_prompt(chunks, n: int = 8) -> str:
    text = "\n\n".join(f"[p. {c['page']}] {c['text']}" for c in select_chunks(chunks))
    return PROMPT.format(n=n, text=text)


def generate_flashcards(chunks, n: int = 8, model: str = llm.DEFAULT_MODEL):
    if not chunks:
        return []
    raw = llm.chat(build_prompt(chunks, n), model=model)
    if raw is None:                      # no API key
        return None
    pages = {c["page"] for c in select_chunks(chunks)}
    return clean_cards(parse_json_list(raw), pages)[:n]
