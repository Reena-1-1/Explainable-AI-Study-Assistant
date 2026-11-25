"""Document-based multiple-choice quiz generator. Owner: Reena.

generate_quiz(chunks, n=5) -> list of
  {"question", "options": [4 strings], "answer": one of options,
   "explanation", "page"}
Questions come only from the uploaded document's text."""
import json
import random
import re

from src import llm
from src.summary_generator import select_chunks

LETTERS = "ABCD"

PROMPT = """Write {n} multiple-choice quiz questions using ONLY the document text below.
Rules:
- Every question must be answerable from the text. Do not use outside knowledge.
- Exactly 4 options per question; only ONE is correct; the wrong options must be
  plausible but clearly wrong according to the text.
- "answer" must be copied exactly from one of the options.
- "explanation" is one sentence saying why the answer is correct, based on the text.
- "page" is the page number (integer) where the answer is found.
Reply with ONLY a JSON array, no other text, no code fences, in this shape:
[{{"question": "...", "options": ["...", "...", "...", "..."],
  "answer": "...", "explanation": "...", "page": 1}}]

Document text:
{text}"""


def build_prompt(chunks, n: int = 5) -> str:
    text = "\n\n".join(f"[p. {c['page']}] {c['text']}" for c in select_chunks(chunks))
    return PROMPT.format(n=n, text=text)


def _extract_json(raw: str):
    """Pull a JSON list out of the model's reply (handles code fences / extra text)."""
    raw = re.sub(r"```(?:json)?", "", raw or "")
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end <= start:
        return []
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _clean_question(q):
    """Return a valid question dict, or None if it is malformed."""
    if not isinstance(q, dict):
        return None
    question = str(q.get("question", "")).strip()
    options = [str(o).strip() for o in q.get("options", []) if str(o).strip()]
    answer = str(q.get("answer", "")).strip()
    explanation = str(q.get("explanation", "")).strip()
    if len(answer) == 1 and answer.upper() in LETTERS[:len(options)]:
        answer = options[LETTERS.index(answer.upper())]      # "B" -> option text
    if (not question or not explanation or len(options) != 4
            or len(set(options)) != 4 or answer not in options):
        return None
    page = q.get("page")
    return {"question": question, "options": options, "answer": answer,
            "explanation": explanation, "page": page if isinstance(page, int) else None}


def parse_quiz(raw: str, shuffle: bool = True, rng=None):
    """Turn the model's reply into a list of valid questions (bad ones are dropped)."""
    rng = rng or random.Random()
    quiz = []
    for q in _extract_json(raw):
        q = _clean_question(q)
        if q:
            if shuffle:
                rng.shuffle(q["options"])   # models love putting the answer first
            quiz.append(q)
    return quiz


def generate_quiz(chunks, n: int = 5, model: str = llm.DEFAULT_MODEL):
    """Returns a list of questions, [] if none could be made, or None if no API key."""
    if not chunks:
        return []
    raw = llm.chat(build_prompt(chunks, n), model=model, temperature=0.3)
    if raw is None:
        return None
    return parse_quiz(raw)[:n]