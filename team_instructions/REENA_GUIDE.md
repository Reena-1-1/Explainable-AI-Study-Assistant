# Reena - your step-by-step guide
Branch: `feature/retrieval` (your files: src/retriever.py, src/answerer.py, evaluate.py, final integration)

## Day 0: set up the repo
1. Unzip this kit. Copy ALL files into your project folder (overwrite existing app.py, src/*.py, requirements.txt, README.md). Note: src/pdf_processor.py and src/text_processor.py are new versions with function names `extract_pages` and `chunk_pages`.
2. In the project folder:
```
pip install -r requirements.txt
pytest
streamlit run app.py
```
3. Upload a PDF and ask a question. You should see evidence passages.
4. Push to main (only time you push directly):
```
git add .
git commit -m "Add retrieval, answerer, tests, docs and team kit"
git push origin main
```
5. GitHub -> Settings -> Collaborators -> add Harsha, Anjali, Shirin.
6. GitHub -> Settings -> Branches -> add rule for `main` -> require pull request.
7. Send each member: GIT_STEPS_COMMON.md + their own file (HARSHA.md / ANJALI.md / SHIRIN.md) via WhatsApp or email, plus the repo link. Tell them to read it in the repo too (team_instructions/ folder).

## Day 1-2: LLM
1. Create a free key at console.groq.com. Copy `.env.example` to `.env` and paste the key.
2. Run the app again. You should now get an answer with (p. N) citations.
3. Test "Not found": ask something not in the PDF. It should say "Not found in the document."
4. `git checkout -b feature/retrieval`, commit, push, open a Pull Request.

## Week 2: evaluation
1. Wait for Shirin's test_questions.csv. Run `python evaluate.py sample.pdf docs/test_questions.csv`.
2. Record Top-1 and Top-3 accuracy. If low, try chunk size 600/overlap 150 or model `all-mpnet-base-v2`.
3. Also test 5 out-of-document questions and count how many correctly return "Not found".

## Every few days
Review and merge pull requests on GitHub. Check that everyone has 5+ commits (Insights -> Contributors).

## Questions to settle with your faculty
SHAP topic vs StudyLens AI, and which LLM is allowed.
