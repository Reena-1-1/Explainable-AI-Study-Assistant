
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
