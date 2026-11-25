"""Document-based summaries. Owner: Reena.
Modes: short, detailed, key_points, definitions, exam_notes.
Only uses text from the uploaded document (chunks from chunk_pages)."""
from src import llm

MAX_CHARS = 9000  # keeps the prompt inside Groq's free-tier limits

MODES = {
    "short": "Write a short summary in 3-4 sentences.",
    "detailed": ("Write a detailed summary in several short paragraphs covering "
                 "all the main topics."),
    "key_points": "List the 6-10 most important points as a bulleted list.",
    "definitions": ("List the important terms defined in the text as "
                    "'Term: definition'. Only include terms the text actually defines."),
    "exam_notes": ("Write exam revision notes: headings for each topic, with short "
                   "bullet points under each."),
}

PROMPT = """Use ONLY the document text below. Do not add outside knowledge.
Cite the page number like (p. 3) after each point.
If the text has nothing relevant, reply exactly: "Not found in the document."

Task: {task}

Document text:
{text}"""


def select_chunks(chunks, max_chars: int = MAX_CHARS):
    """Pick chunks spread evenly across the whole document, within max_chars."""
    if not chunks:
        return []
    avg = max(1, sum(len(c["text"]) for c in chunks) // len(chunks))
    want = max(1, max_chars // avg)
    if want >= len(chunks):
        return list(chunks)
    step = len(chunks) / want
    return [chunks[int(i * step)] for i in range(want)]


def build_prompt(chunks, mode: str = "short") -> str:
    task = MODES.get(mode, MODES["short"])
    text = "\n\n".join(f"[p. {c['page']}] {c['text']}" for c in select_chunks(chunks))
    return PROMPT.format(task=task, text=text)


def summarize(chunks, mode: str = "short", model: str = llm.DEFAULT_MODEL):
    """Returns summary text, or None if no API key (same convention as answerer)."""
    if not chunks:
        return "Not found in the document."
    return llm.chat(build_prompt(chunks, mode), model=model)