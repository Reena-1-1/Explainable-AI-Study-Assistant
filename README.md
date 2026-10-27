StudyLens AI - Explainable Study Assistant

Upload a PDF, ask a question, and get an answer with the pages it came from. Every answer is intended to be supported by evidence passages so users can verify the information. If the document does not contain sufficient information, the system is designed to respond with "Not found in the document."

How It Works

PDF upload → Text extraction per page → Sentence-aware chunking → Embeddings → FAISS retrieval → Top 3 passages → LLM → Answer with page citations

Introduction

StudyLens AI is an Explainable AI Study Assistant designed to help users understand information from PDF documents. Users can upload a PDF and ask questions about its content. The system retrieves relevant passages to support its answers with page references, helping users find information more easily and verify answers using the original document.

Problem Statement

Finding specific information in lengthy PDF notes and textbooks can be time-consuming. AI-generated answers may also be unreliable when they do not provide sources or evidence. A useful study assistant should retrieve relevant information from the uploaded document, show supporting passages and page references, and indicate when sufficient information is not available to answer a question.

Features

- PDF upload: Upload a PDF document for analysis.
- Question answering: Ask questions about the uploaded document.
- Page citations: View page references supporting generated answers.
- Evidence passages: Review relevant text retrieved from the document.
- Not Found response: Indicate when the document does not contain sufficient information to answer a question.
- Evidence-based answers: Use retrieved document passages to support answer generation.

Note: PDF page highlighting and SQLite-based question history should be listed as implemented features only after they have been verified in the application.

Tech Stack

- Python: Core programming language.
- Streamlit: User interface for the application.
- PyMuPDF: Extracts text from PDF documents.
- Sentence Transformers: Converts text into embeddings for semantic search.
- FAISS: Searches for relevant text passages using vector similarity.
- Groq LLM: Generates answers using retrieved document evidence.

Project Structure

Explainable-AI-Study-Assistant/
├── app.py
├── evaluate.py
├── requirements.txt
├── .env.example
├── README.md
└── docs/
    ├── architecture.md
    ├── architecture.png
    ├── literature_survey.md
    ├── report_outline.md
    ├── database_design.md
    ├── user_manual.md
    ├── testing.md
    ├── viva_questions.md
    ├── test_questions.csv
    ├── screenshots/
    │   ├── main_interface.jpeg
    │   ├── pdf_upload.jpeg
    │   └── question_answer.jpeg
    └── sample/
        └── sample.pdf

Check this structure against the actual files in your VS Code Explorer. If your screenshot filenames or any other filenames differ, update this section to match.

Setup

1. Clone the Repository

git clone https://github.com/Reena-1-1/Explainable-AI-Study-Assistant.git
cd Explainable-AI-Study-Assistant

2. Create and Activate a Virtual Environment

Windows:

python -m venv venv
venv\Scripts\activate

macOS/Linux:

python -m venv venv
source venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Configure the API Key

Copy ".env.example" to ".env" and add the API key required by the application.

Windows:

copy .env.example .env

macOS/Linux:

cp .env.example .env

Keep your API key private. Never commit the ".env" file or expose your key in screenshots or logs.

5. Run the Application

streamlit run app.py

Follow the local URL displayed in the terminal to open the application.

API-key requirements and behaviour when a key is missing should be confirmed against the current application.

Tests

Run the automated tests with:

pytest

Evaluation

Run the evaluation script with a PDF and the test-question CSV:

python evaluate.py your.pdf docs/test_questions.csv

Replace "your.pdf" with the path to the PDF you want to evaluate. Record actual results and investigate any failures before reporting evaluation outcomes.

Documentation

- "docs/architecture.md" — System architecture.
- "docs/literature_survey.md" — Literature survey.
- "docs/report_outline.md" — Project report outline.
- "docs/database_design.md" — Database design documentation.
- "docs/user_manual.md" — User instructions and screenshots.
- "docs/testing.md" — Test cases and test results.
- "docs/viva_questions.md" — Viva questions and answers.
- "docs/test_questions.csv" — Evaluation questions.
- "docs/sample/sample.pdf" — Sample PDF for testing.

Team

- Reena: Retrieval, LLM, and integration.
- Harsha: PDF/text processing and tests.
- Anjali: Streamlit user interface.
- Shirin: Documentation and evaluation questions.