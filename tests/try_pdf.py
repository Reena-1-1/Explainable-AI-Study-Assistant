
from pathlib import Path
import sys

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.pdf_processor import extract_pages, count_empty_pages


def main():
    pdf_path = input("Enter the path to a PDF file: ").strip().strip('"')

    if not Path(pdf_path).is_file():
        print("Error: PDF file not found.")
        return

    try:
        pdf_bytes = Path(pdf_path).read_bytes()
        pages = extract_pages(pdf_bytes)

        print(f"\nTotal pages: {len(pages)}")
        print(f"Empty pages: {count_empty_pages(pages)}")

        for page in pages:
            print(f"\n--- Page {page['page']} ---")
            print(page["text"][:500] or "[No text found]")

    except Exception as error:
        print(f"Error processing PDF: {error}")


if __name__ == "__main__":
    main()
