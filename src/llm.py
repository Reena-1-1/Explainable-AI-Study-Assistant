"""Shared Groq call used by the summary, quiz and flashcard generators. Owner: Reena."""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "openai/gpt-oss-20b"
EMPTY_REPLY = "The model returned an empty reply. Please try again."
MAX_RETRIES = 3          # how many times to retry after a 429 (rate limit)
DEFAULT_WAIT = 15        # seconds to wait if Groq does not say how long


def _wait_time(resp) -> float:
    """Seconds to wait before retrying: Groq's Retry-After header if present."""
    try:
        return min(float(resp.headers.get("retry-after", DEFAULT_WAIT)), 60)
    except (TypeError, ValueError):
        return DEFAULT_WAIT


def chat(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0):
    """Send one prompt to Groq. Returns text, or None if no GROQ_API_KEY is set.
    Retries automatically when Groq's free-tier rate limit (429) is hit."""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    body = {"model": model, "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]}
    if model.startswith("openai/gpt-oss"):
        # gpt-oss "thinks" before answering; low effort keeps replies fast and
        # stops the thinking from using up the whole answer budget.
        body["reasoning_effort"] = "low"

    for attempt in range(MAX_RETRIES + 1):
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json=body,
            timeout=60,
        )
        if resp.status_code == 429 and attempt < MAX_RETRIES:
            time.sleep(_wait_time(resp))
            continue
        resp.raise_for_status()
        text = (resp.json()["choices"][0]["message"].get("content") or "").strip()
        return text or EMPTY_REPLY