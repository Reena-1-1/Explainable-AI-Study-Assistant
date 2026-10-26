"""LLM answer from retrieved passages only. Owner: Reena.
Uses Groq's free OpenAI-compatible API. Key goes in .env (GROQ_API_KEY)."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOT_FOUND = "Not found in the document."

PROMPT = """Answer the question using ONLY the passages below.
Cite the page number like (p. 3) after each claim.
If the passages do not contain the answer, reply exactly:
"Not found in the document."

Passages:
{passages}

Question: {question}"""


def build_passages(results):
    return "\n\n".join(f"[p. {r['page']}] {r['text']}" for r in results)


def answer(question: str, results, model: str = "llama-3.1-8b-instant"):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None  # app shows evidence only
    if not results:
        return NOT_FOUND
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": model, "temperature": 0,
              "messages": [{"role": "user", "content": PROMPT.format(
                  passages=build_passages(results), question=question)}]},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
