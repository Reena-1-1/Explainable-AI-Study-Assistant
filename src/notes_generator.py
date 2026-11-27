"""Generate structured study notes from PDF text."""

import os
from urllib import response
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

NOTES_PROMPT = """
You are an educational study assistant.

Create clear, well-organized study notes using ONLY the
provided document text.

Organize the notes with:
1. Topic-wise headings
2. Important concepts and explanations
3. Key definitions
4. Important points
5. Examples, if available in the document
6. Keywords
7. A short revision summary

Use simple language that students can understand.
Do not add information that is not present in the document.
Mention relevant page numbers wherever possible.

Document text:
{document_text}
"""

def generate_notes(document_text: str):
    """Generate study notes from extracted PDF text using Groq."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "Error: GROQ_API_KEY is missing. Check your .env file."

    if not document_text.strip():
        return "Error: No document text was provided."

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-oss-20b",
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": NOTES_PROMPT.format(
                        document_text=document_text
                    )
                }
            ]
        },
        timeout=120
    )

    try:
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        return f"Error generating notes: {e}"

    except (KeyError, IndexError):
        return "Error: Unexpected response received from AI."