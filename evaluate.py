"""Evaluate retrieval. Usage: python evaluate.py path/to/doc.pdf docs/test_questions.csv
CSV columns: question,expected_page"""
import csv
import sys

from src.pdf_processor import extract_pages
from src.text_processor import chunk_pages
from src.retriever import Retriever

pdf, csv_path = sys.argv[1], sys.argv[2]
chunks = chunk_pages(extract_pages(open(pdf, "rb").read()))
r = Retriever(); r.build(chunks)

rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
top1 = top3 = 0
for row in rows:
    pages = [x["page"] for x in r.search(row["question"], k=3)]
    exp = int(row["expected_page"])
    top1 += bool(pages) and pages[0] == exp
    top3 += exp in pages
    print(("OK  " if exp in pages else "MISS"), row["question"], "->", pages, "expected", exp)
n = len(rows)
print(f"\nTop-1 accuracy: {top1}/{n} = {top1/n:.0%}\nTop-3 accuracy: {top3}/{n} = {top3/n:.0%}")
