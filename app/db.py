import sqlite3
import json
from pathlib import Path

# -------------------------------------------------
# Explicit DB location (PROJECT ROOT)
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "qualification.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        data TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def save_session(session_id: str, data: dict):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO sessions (session_id, data)
    VALUES (?, ?)
    """, (session_id, json.dumps(data)))

    conn.commit()
    conn.close()


def load_session(session_id: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT data FROM sessions WHERE session_id = ?",
        (session_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return json.loads(row[0])


def load_all_sessions():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT session_id, data FROM sessions")
    rows = cur.fetchall()
    conn.close()

    return {
        sid: json.loads(data)
        for sid, data in rows
    }
