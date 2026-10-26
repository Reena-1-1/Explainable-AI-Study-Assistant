# Shirin - Documentation and evaluation
Branch: `feature/docs`
Your files: `README.md`, `docs/` folder. Do NOT edit code files. Read GIT_STEPS_COMMON.md first.

## Tasks (commit after each one)
1. Improve `README.md`: add project introduction, problem statement, features, tech stack (Python, Streamlit, PyMuPDF, sentence-transformers, FAISS, Groq LLM), and screenshots (ask Anjali). Commit.
2. Extend `docs/architecture.md` and draw a pipeline diagram (draw.io or diagrams.net, save PNG in docs/). Commit.
3. Write `docs/literature_survey.md`: 5-6 papers/articles (RAG by Lewis et al. 2020, Sentence-BERT, FAISS, LIME, SHAP, a paper on explainable QA). For each: title, year, 3-line summary, how it relates to our project. Use your own words. Commit.
4. Choose one PDF (a textbook chapter, 10+ pages). Write 15-20 questions in `docs/test_questions.csv` with the correct page number. Format: `question,expected_page`. Commit the PDF too, if it is small, in `docs/sample/`.
5. Prepare the report outline and PPT (problem, objectives, architecture, demo, results, future work). Put the outline in `docs/report_outline.md`.
6. Open a Pull Request titled "Documentation".

Reena will run `python evaluate.py sample.pdf docs/test_questions.csv` and give you the results to put in the report.
