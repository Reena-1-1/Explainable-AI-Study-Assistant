import sys
from src.pdf_processor import extract_pages
from src.text_processor import chunk_pages
from src.summary_generator import summarize, MODES

# Usage:  python try_summary.py "path\to\your.pdf"
path = sys.argv[1] if len(sys.argv) > 1 else "docs/sample/sample.pdf"
chunks = chunk_pages(extract_pages(open(path, "rb").read()))
print(f"{path}: {len(chunks)} chunks")
for mode in MODES:
    print("=" * 20, mode)
    print(summarize(chunks, mode))
