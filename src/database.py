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
def create_notes_table(path=DB_PATH):
    """Create a table to store students' personal study notes."""
    with _conn(path) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS study_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

def save_note(title, subject, content, path=DB_PATH):
    """Save a student's personal study note."""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    with _conn(path) as c:
        c.execute("""
            INSERT INTO study_notes
            (title, subject, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title, subject, content, current_time, current_time))

def get_notes(path=DB_PATH):
    """Retrieve all saved study notes."""
    with _conn(path) as c:
        rows = c.execute("""
            SELECT id, title, subject, content, created_at, updated_at
            FROM study_notes
            ORDER BY id DESC
        """).fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "subject": row[2],
            "content": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        }
        for row in rows
    ]
def delete_note(note_id, path=DB_PATH):
    """Delete a study note using its ID."""
    with _conn(path) as c:
        c.execute(
            "DELETE FROM study_notes WHERE id = ?",
            (note_id,)
        )
def update_note(note_id, title, subject, content, path=DB_PATH):
    """Update an existing study note."""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    with _conn(path) as c:
        c.execute("""
            UPDATE study_notes
            SET title = ?, subject = ?, content = ?, updated_at = ?
            WHERE id = ?
        """, (title, subject, content, current_time, note_id))