# Anjali - Streamlit UI
Branch: `feature/ui`
Your file: `app.py` only. Do NOT edit other files. Read GIT_STEPS_COMMON.md first.

Run the app: `streamlit run app.py`. It already works; your job is to make it good.

## Tasks (commit after each one)
1. Run the app with any PDF, ask a question, and check it works. Without an API key you see evidence only. Commit nothing yet, just learn the flow.
2. Highlight the words from the question inside the evidence text (bold them). Commit.
3. Show a similarity bar (st.progress) or coloured label for each evidence item: green above 0.5, orange 0.3-0.5, red below. Commit.
4. Add a sidebar slider "Number of passages (k)" from 1 to 5 and pass it to `search`. Commit.
5. Add a short "How to use" section and a footer with the team names. Commit.
6. Add a chat history list so previous questions stay on screen (use st.session_state). Commit.
7. Take 3 screenshots for the report and give them to Shirin. Open a Pull Request titled "UI improvements".

Do not change how `extract_pages`, `chunk_pages`, `Retriever` or `answer` are called.
