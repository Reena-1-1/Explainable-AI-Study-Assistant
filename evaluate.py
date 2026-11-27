"""Evaluate retrieval quality. Owner: Reena.

Usage:
    python evaluate.py path/to/document.pdf docs/churn_test_questions.csv [threshold]

Question file (tab or comma separated) with columns:
    question       the question
    expected_page  page that contains the answer; several pages separated by |  (e.g. 2|4)
                   use 0 for questions whose answer is NOT in the document
    answerable     yes / no   (optional - if missing, expected_page 0 means "no")

What it measures
    Top-1 / Top-3 accuracy  : is a correct page the best result / among the best 3? (answerable questions)
    Refusal rate            : for out-of-document questions, how many have a best score below the threshold
    Threshold table         : how the cut-off trades "answers kept" against "wrong questions refused"
Results are also saved to docs/evaluation_results.csv.
"""
import csv
import sys

DEFAULT_THRESHOLD = 0.20
SWEEP = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]


def load_questions(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = "\t" if sample.count("\t") >= sample.count(",") and "\t" in sample else ","
        questions = []
        for row in csv.DictReader(f, delimiter=delimiter):
            q = (row.get("question") or "").strip()
            if not q:
                continue
            raw = (row.get("expected_page") or "0").strip()
            pages = {int(p) for p in raw.replace(";", "|").split("|") if p.strip().isdigit() and int(p) > 0}
            flag = (row.get("answerable") or "").strip().lower()
            answerable = (flag == "yes") if flag else bool(pages)
            questions.append({"question": q, "pages": pages, "answerable": answerable})
    return questions


def evaluate(retriever, questions, k=3, threshold=DEFAULT_THRESHOLD):
    rows = []
    for item in questions:
        results = retriever.search(item["question"], k=k)
        pages = [r["page"] for r in results]
        top_score = results[0]["score"] if results else 0.0
        row = {"question": item["question"], "answerable": item["answerable"],
               "expected": "|".join(map(str, sorted(item["pages"]))) or "-",
               "pages_found": pages, "top_score": top_score}
        if item["answerable"]:
            row["top1"] = bool(pages) and pages[0] in item["pages"]
            row["top3"] = any(p in item["pages"] for p in pages)
            row["kept"] = top_score >= threshold
        else:
            row["refused"] = top_score < threshold
        rows.append(row)

    yes = [r for r in rows if r["answerable"]]
    no = [r for r in rows if not r["answerable"]]

    def pct(a, b):
        return a / b if b else None

    summary = {
        "answerable": len(yes), "unanswerable": len(no), "threshold": threshold,
        "top1": pct(sum(r["top1"] for r in yes), len(yes)),
        "top3": pct(sum(r["top3"] for r in yes), len(yes)),
        "answers_kept": pct(sum(r["kept"] for r in yes), len(yes)),
        "refused": pct(sum(r["refused"] for r in no), len(no)),
        "mean_score_answerable": sum(r["top_score"] for r in yes) / len(yes) if yes else None,
        "mean_score_unanswerable": sum(r["top_score"] for r in no) / len(no) if no else None,
        "sweep": [(t, pct(sum(r["top_score"] >= t for r in yes), len(yes)),
                   pct(sum(r["top_score"] < t for r in no), len(no))) for t in SWEEP],
    }
    return rows, summary


def _fmt(x):
    return "n/a" if x is None else f"{x:.0%}"


def print_report(rows, s):
    for r in rows:
        if r["answerable"]:
            mark = "OK  " if r["top3"] else "MISS"
            print(f"{mark} {r['question']}\n       expected page {r['expected']}, found {r['pages_found']}, "
                  f"best score {r['top_score']:.2f}")
        else:
            mark = "OK  " if r["refused"] else "FAIL"
            print(f"{mark} [not in document] {r['question']}\n       best score {r['top_score']:.2f} "
                  f"-> {'refused' if r['refused'] else 'would NOT be refused'}")
    print("\n" + "=" * 60)
    print(f"Answerable questions   : {s['answerable']}")
    print(f"  Top-1 accuracy       : {_fmt(s['top1'])}")
    print(f"  Top-3 accuracy       : {_fmt(s['top3'])}")
    if s["mean_score_answerable"] is not None:
        print(f"  Mean best score      : {s['mean_score_answerable']:.2f}")
    print(f"Out-of-document questions: {s['unanswerable']}")
    print(f"  Refused (score < {s['threshold']:.2f}): {_fmt(s['refused'])}")
    if s["mean_score_unanswerable"] is not None:
        print(f"  Mean best score      : {s['mean_score_unanswerable']:.2f}")
    print("\nThreshold table (pick the cut-off that keeps most answers AND refuses most wrong questions):")
    print("  threshold | answerable kept | out-of-document refused")
    for t, kept, refused in s["sweep"]:
        print(f"     {t:.2f}   |      {_fmt(kept):>5}      |        {_fmt(refused):>5}")


def save_results(rows, path="docs/evaluation_results.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["question", "answerable", "expected_page", "pages_found", "best_score", "result"])
        for r in rows:
            ok = r["top3"] if r["answerable"] else r["refused"]
            w.writerow([r["question"], "yes" if r["answerable"] else "no", r["expected"],
                        ";".join(map(str, r["pages_found"])), f"{r['top_score']:.3f}", "PASS" if ok else "FAIL"])
    return path


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    pdf_path, csv_path = sys.argv[1], sys.argv[2]
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_THRESHOLD

    from src.pdf_processor import extract_pages
    from src.retriever import Retriever
    from src.text_processor import chunk_pages

    with open(pdf_path, "rb") as f:
        chunks = chunk_pages(extract_pages(f.read()))
    retriever = Retriever()
    retriever.build(chunks)
    print(f"{pdf_path}: {len(chunks)} chunks\n")

    rows, summary = evaluate(retriever, load_questions(csv_path), threshold=threshold)
    print_report(rows, summary)
    print("\nSaved:", save_results(rows))


if __name__ == "__main__":
    main()
