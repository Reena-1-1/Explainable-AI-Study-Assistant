<<<<<<< HEAD

"""LLM answer from retrieved passages only.
Uses Groq's OpenAI-compatible API.
API key is stored in .env as GROQ_API_KEY.
"""

=======
"""LLM answer from retrieved passages only. Owner: Reena.
Uses Groq's free OpenAI-compatible API. Key goes in .env (GROQ_API_KEY).

answer(question, results) still works exactly as before (default style = simple).
New: answer(question, results, style="detailed") or style="step-by-step".
"""
>>>>>>> 35834996c8de4ebc90e946d4854adb611e3aec05
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(override=True)

NOT_FOUND = "Not found in the document."

# Style name -> extra instruction inserted into the prompt.
STYLES = {
    "simple": "Explain in easy English with short sentences. Keep it to 2-4 sentences.",
    "detailed": ("Give a thorough, well-organised explanation covering all relevant "
                 "details from the passages. Use short paragraphs."),
    "step-by-step": ("Explain as a numbered list (1., 2., 3., ...). Each step must be "
                     "one clear sentence taken from the passages."),
}
DEFAULT_STYLE = "simple"

PROMPT = """Answer the question using ONLY the passages below.
Cite the page number like (p. 3) after each claim.
If the passages do not contain the answer, reply exactly:
"Not found in the document."

Style: {style_instruction}

Passages:
{passages}

Question: {question}"""


def build_passages(results):
    """Combine retrieved passages with their page numbers."""
    return "\n\n".join(
        f"[p. {r['page']}] {r['text']}"
        for r in results
    )


<<<<<<< HEAD
def answer(
    question: str,
    results,
    model: str = "openai/gpt-oss-20b"
):
    """Generate an answer using only the retrieved document passages."""

=======
def build_prompt(question: str, results, style: str = DEFAULT_STYLE) -> str:
    """Build the full prompt (separate function so it can be tested without the API)."""
    instruction = STYLES.get(style, STYLES[DEFAULT_STYLE])
    return PROMPT.format(style_instruction=instruction,
                         passages=build_passages(results), question=question)


def answer(question: str, results, model: str = "openai/gpt-oss-20b",
           style: str = DEFAULT_STYLE):
>>>>>>> 35834996c8de4ebc90e946d4854adb611e3aec05
    key = os.getenv("GROQ_API_KEY")

    if not key:
        return None

    if not results:
        return NOT_FOUND

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
<<<<<<< HEAD
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
=======
        headers={"Authorization": f"Bearer {key}"},
        json={"model": model, "temperature": 0,
              "messages": [{"role": "user",
                            "content": build_prompt(question, results, style)}]},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
>>>>>>> 35834996c8de4ebc90e946d4854adb611e3aec05
