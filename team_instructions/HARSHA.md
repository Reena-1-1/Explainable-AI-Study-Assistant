# Harsha - PDF/text processing + tests
Branch: `feature/processing-tests`
Your files: `src/pdf_processor.py`, `src/text_processor.py`, `tests/test_text_processor.py`, `tests/test_pdf_processor.py`
Do NOT edit other files. Read GIT_STEPS_COMMON.md first.

## Tasks (commit after each one)
1. Run `pytest tests/test_text_processor.py tests/test_pdf_processor.py`. Make sure all pass. Commit.
2. Add 3 more tests in `tests/test_text_processor.py`: very long sentence without a full stop, text with hyphenated line breaks ("exam-\nple" becomes "example"), and chunk_id being sequential. Commit.
3. Improve `clean_text`: remove page-number-only lines and repeated headers/footers. Add a test for it. Commit.
4. Add a function to `pdf_processor.py` that returns the number of pages that had no text, so the UI can warn about scanned PDFs. Add a test. Commit.
5. (Bonus) OCR for scanned PDFs using pytesseract. Ask Reena before adding it.
6. Open a Pull Request titled "Processing improvements and tests".

Keep the return format: pages = [{"page": int, "text": str}], chunks = [{"chunk_id", "page", "text"}]. Other people's code depends on it.
