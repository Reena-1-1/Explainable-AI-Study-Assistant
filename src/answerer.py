
"""LLM answer from retrieved passages only.
Uses Groq's OpenAI-compatible API.
API key is stored in .env as GROQ_API_KEY.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(override=True)

NOT_FOUND = "Not found in the document."

PROMPT = """Answer the question using ONLY the passages below.
Cite the page number like (p. 3) after each claim.
If the passages do not contain the answer, reply exactly:
"Not found in the document."

Passages:
{passages}

Question: {question}"""


def build_passages(results):
    """Combine retrieved passages with their page numbers."""
    return "\n\n".join(
        f"[p. {r['page']}] {r['text']}"
        for r in results
    )


def answer(
    question: str,
    results,
    model: str = "openai/gpt-oss-20b"
):
    """Generate an answer using only the retrieved document passages."""

    key = os.getenv("GROQ_API_KEY")

    if not key:
        return None

    if not results:
        return NOT_FOUND

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": PROMPT.format(
                        passages=build_passages(results),
                        question=question
                    )
                }
            ]
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"].strip()
