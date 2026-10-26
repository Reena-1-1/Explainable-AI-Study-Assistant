
# PDF Processor Testing Notes

## Real PDF Test

- Script: `tests/try_pdf.py`
- PDF tested: Benefits of Tech in Healthcare.pdf
- Total pages processed: 18
- Empty pages detected: 0

## Observations

1. The PDF was opened and processed successfully.
2. Text was extracted from all 18 pages.
3. No empty pages were detected.
4. The script displayed up to 500 characters from each page.
5. PyMuPDF displayed a deprecation warning for the `fitz` API, but processing completed successfully.

## How to Run

From the project root, run:

`py tests/try_pdf.py`

Enter the full path to a PDF file when prompted.
