import sqlite3
import json
from typing import Optional, Dict
DB_PATH = "quiz_app.db"
def init_db():
    conn = _connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT    NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS questions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id     INTEGER NOT NULL REFERENCES quizzes(id),
            question    TEXT    NOT NULL,
            options     TEXT    NOT NULL,   -- JSON array
            correct     TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id         INTEGER NOT NULL REFERENCES quizzes(id),
            level           TEXT,
            chances_percent REAL,
            submitted_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def save_quiz(source_file: str, questions: list) -> int:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO quizzes (source_file) VALUES (?)", (source_file,))
    quiz_id = cur.lastrowid
    for q in questions:
        cur.execute(
            "INSERT INTO questions (quiz_id, question, options, correct) VALUES (?,?,?,?)",
            (quiz_id, q["question"], json.dumps(q["options"]), q["correct_answer"])
        )
    conn.commit()
    conn.close()
    return quiz_id


def get_quiz(quiz_id: int) -> Optional[Dict]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id, source_file, created_at FROM quizzes WHERE id=?", (quiz_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    questions = []
    cur.execute(
        "SELECT id, question, options, correct FROM questions WHERE quiz_id=?", (quiz_id,)
    )
    for qrow in cur.fetchall():
        questions.append({
            "id": qrow[0],
            "question": qrow[1],
            "options": json.loads(qrow[2]),
            "correct_answer": qrow[3],
        })
    conn.close()
    return {"quiz_id": row[0], "source_file": row[1], "created_at": row[2], "questions": questions}


def save_result(quiz_id: int, level: str, chances: float):
    conn = _connect()
    conn.execute(
        "INSERT INTO results (quiz_id, level, chances_percent) VALUES (?,?,?)",
        (quiz_id, level, chances)
    )
    conn.commit()
    conn.close()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
