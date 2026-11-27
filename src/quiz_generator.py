<<<<<<< HEAD

"""Generate multiple-choice quizzes from PDF text using Groq AI."""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(override=True)


QUIZ_PROMPT = """
You are an educational quiz generator.

Create exactly {num_questions} multiple-choice questions using ONLY
the document text provided below.

Return ONLY valid JSON in this exact format:
{{
    "questions": [
        {{
            "question": "Question text",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "explanation": "Short explanation based on the document"
        }}
    ]
}}

Rules:
- Each question must have exactly four options.
- Only one option must be correct.
- correct_answer must be A, B, C, or D.
- Include clear, student-friendly explanations.
- Do not use information outside the document.

Document text:
{document_text}
"""


def generate_quiz(document_text: str, num_questions: int = 5):
    """Generate and validate a multiple-choice quiz."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return {"error": "GROQ_API_KEY is missing. Check your .env file."}

    if not document_text.strip():
        return {"error": "No document text was provided."}

    if not 1 <= num_questions <= 20:
        return {"error": "Choose between 1 and 20 questions."}

    try:
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
                        "content": QUIZ_PROMPT.format(
                            num_questions=num_questions,
                            document_text=document_text[:50000]
                        )
                    }
                ]
            },
            timeout=120
        )

        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"].strip()

        # Remove optional Markdown code fences.
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0].strip()

        quiz = json.loads(content)
        questions = quiz.get("questions")

        if not isinstance(questions, list) or len(questions) != num_questions:
            return {"error": "AI returned an unexpected number of questions. Please try again."}

        for question in questions:
            if not all(key in question for key in (
                "question", "options", "correct_answer", "explanation"
            )):
                return {"error": "AI returned an incomplete question. Please try again."}

            if (
                not isinstance(question["options"], dict)
                or set(question["options"].keys()) != {"A", "B", "C", "D"}
                or question["correct_answer"] not in {"A", "B", "C", "D"}
            ):
                return {"error": "AI returned invalid answer options. Please try again."}

        return quiz

    except requests.exceptions.RequestException as e:
        return {"error": f"Could not generate quiz: {e}"}
    except (KeyError, IndexError, ValueError, TypeError):
        return {"error": "AI returned an invalid response. Please try again."}
=======
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
>>>>>>> 35834996c8de4ebc90e946d4854adb611e3aec05
