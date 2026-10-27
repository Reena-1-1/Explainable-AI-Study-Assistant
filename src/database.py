"""SQLite storage for question history. Owner: Harsha.
Creates studylens.db in the project folder (ignored by Git)."""
import json
import sqlite3
import time

DB_PATH = "studylens.db"


def _conn(path=DB_PATH):
    return sqlite3.connect(path)


def init_db(path=DB_PATH):
    with _conn(path) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            doc_name TEXT,
            question TEXT NOT NULL,
            answer TEXT,
            pages TEXT,
            top_score REAL)""")


def save_qa(question, answer, results, doc_name="", path=DB_PATH):
    pages = json.dumps([r["page"] for r in results])
    top = results[0]["score"] if results else None
    with _conn(path) as c:
        c.execute("INSERT INTO qa_history (created_at, doc_name, question, answer, pages, top_score)"
                  " VALUES (?,?,?,?,?,?)",
                  (time.strftime("%Y-%m-%d %H:%M:%S"), doc_name, question, answer, pages, top))


def get_history(limit=20, path=DB_PATH):
    with _conn(path) as c:
        rows = c.execute("SELECT created_at, doc_name, question, answer, pages, top_score "
                         "FROM qa_history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [{"created_at": r[0], "doc_name": r[1], "question": r[2], "answer": r[3],
             "pages": json.loads(r[4] or "[]"), "top_score": r[5]} for r in rows]