# StudyLens AI - Explainable Study Assistant

Upload a PDF, ask a question, and get an answer **with the exact pages it came from**.
Every answer is backed by evidence passages, so you can verify it. If the document does
not contain the answer, the system says "Not found in the document."

## How it works
PDF -> text per page -> sentence-aware chunks -> embeddings -> FAISS -> top 3 passages -> LLM -> answer + page citations

Introduction

StudyLens AI is an Explainable AI Study Assistant that helps students understand information from PDF documents. Students can upload a PDF and ask questions about its content. The system retrieves relevant passages to support its answers with page references. This helps students find information more easily and verify answers using the original document.

Problem Statement

Students often spend a lot of time searching lengthy PDF notes and textbooks to find specific information. AI-generated answers may also be unreliable when they do not provide sources or evidence. A study assistant should retrieve relevant information from the uploaded document, show supporting passages and page references, and indicate when the answer cannot be found.

Features

- PDF upload: Upload a PDF document for analysis.
- Question answering: Ask questions about the uploaded document.
- Page citations: View page references supporting the answers.
- Evidence passages: Review relevant text retrieved from the document.
- Not Found response: Indicate when the document does not contain sufficient information to answer a question.

Tech Stack

- Python: Core programming language.
- Streamlit: User interface for the application.
- PyMuPDF: Extracts text from PDF documents.
- Sentence Transformers: Converts text into embeddings for semantic search.
- FAISS: Searches for relevant text passages efficiently.
- Groq LLM: Generates answers using retrieved document evidence.

## Setup
```
git clone https://github.com/Reena-1-1/Explainable-AI-Study-Assistant.git
cd Explainable-AI-Study-Assistant
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env       # Mac/Linux: cp .env.example .env  (then add your key)
streamlit run app.py
```
Without a key the app still works and shows the evidence passages.

## Tests
`pytest`

## Evaluation
`python evaluate.py your.pdf docs/test_questions.csv`

## Team
- Reena - retrieval, LLM, integration
- Harsha - PDF/text processing, tests
- Anjali - Streamlit UI
- Shirin - documentation, evaluation questions
(Shirin: add details, screenshots, and results here.)
