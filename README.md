# StudyLens AI - Explainable Study Assistant

Upload a PDF, ask a question, and get an answer **with the exact pages it came from**.
Every answer is backed by evidence passages, so you can verify it. If the document does
not contain the answer, the system says "Not found in the document."

## How it works
PDF -> text per page -> sentence-aware chunks -> embeddings -> FAISS -> top 3 passages -> LLM -> answer + page citations

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
