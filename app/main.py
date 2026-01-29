import json
import uuid
import sqlite3
import random
import os
import traceback
import csv
from io import StringIO

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from jiwer import wer

# =================================================
# PATHS
# =================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(ROOT_DIR, "data")
PROJECTS_DIR = os.path.join(DATA_DIR, "projects")
STATIC_DIR = os.path.join(ROOT_DIR, "static")
AUDIO_DIR = os.path.join(ROOT_DIR, "audio")

DB_PATH = os.path.join(ROOT_DIR, "qualification.db")

# =================================================
# APP
# =================================================

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# =================================================
# DB
# =================================================

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    c = db()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            project TEXT,
            intake_json TEXT,
            quiz_json TEXT,
            transcription_json TEXT,
            quiz_score REAL,
            transcription_score REAL,
            passed INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            session_id TEXT,
            task_id TEXT,
            text TEXT
        )
    """)
    c.commit()


init_db()

# =================================================
# HELPERS
# =================================================

def project_path(project: str) -> str:
    return os.path.join(PROJECTS_DIR, project)


def load_json_safe(path: str):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, f"Failed to load JSON: {path}")


def ensure_grading(session_id: str):
    c = db()
    row = c.execute(
        "SELECT quiz_score, transcription_json, transcription_score FROM sessions WHERE session_id=?",
        (session_id,)
    ).fetchone()

    if row["transcription_score"] is not None:
        return

    tasks = json.loads(row["transcription_json"] or "[]")
    subs = c.execute(
        "SELECT task_id, text FROM transcriptions WHERE session_id=?",
        (session_id,)
    ).fetchall()

    gold = {t["task_id"]: t["gold_text"] for t in tasks}
    hyp = {r["task_id"]: r["text"] for r in subs}

    wers = [wer(gold[k], hyp[k]) for k in gold if k in hyp]
    transcription_score = 1 - (sum(wers) / len(wers)) if wers else 0

    passed = int(
        (row["quiz_score"] or 0) >= 0.95 and transcription_score >= 0.98
    )

    c.execute(
        "UPDATE sessions SET transcription_score=?, passed=? WHERE session_id=?",
        (transcription_score, passed, session_id)
    )
    c.commit()

# =================================================
# INTAKE
# =================================================

@app.post("/start")
def start(intake: dict = Body(...), project: str = Query(...)):
    session_id = str(uuid.uuid4())
    c = db()
    c.execute(
        "INSERT INTO sessions VALUES (?, ?, ?, NULL, NULL, NULL, NULL, NULL)",
        (session_id, project, json.dumps(intake))
    )
    c.commit()
    return {"session_id": session_id}

# =================================================
# TRAINING  ✅ RESTORED
# =================================================

@app.get("/training")
def training(project: str = Query(...)):
    path = os.path.join(project_path(project), "guidelines.json")
    if not os.path.exists(path):
        raise HTTPException(404, f"Missing guidelines.json for project {project}")
    return load_json_safe(path)


@app.post("/training_complete")
def training_complete(payload: dict = Body(...)):
    return {"ok": True}

# =================================================
# QUIZ
# =================================================

@app.post("/quiz")
def quiz(payload: dict = Body(...)):
    session_id = payload["session_id"]

    c = db()
    row = c.execute(
        "SELECT project FROM sessions WHERE session_id=?",
        (session_id,)
    ).fetchone()

    base = project_path(row["project"])
    quiz_path = os.path.join(base, "quiz.json")

    data = load_json_safe(quiz_path)
    questions = data["questions"]
    random.shuffle(questions)

    c.execute(
        "UPDATE sessions SET quiz_json=? WHERE session_id=?",
        (json.dumps(questions), session_id)
    )
    c.commit()

    return {"questions": questions}


@app.post("/submit_mcq")
def submit_mcq(payload: dict = Body(...)):
    session_id = payload["session_id"]
    answers = payload["answers"]

    c = db()
    row = c.execute(
        "SELECT quiz_json FROM sessions WHERE session_id=?",
        (session_id,)
    ).fetchone()

    questions = json.loads(row["quiz_json"])
    correct = {q["id"]: q["correct"] for q in questions}

    score = sum(
        1 for qid, ans in answers.items()
        if qid in correct and ans == correct[qid]
    ) / len(correct)

    c.execute(
        "UPDATE sessions SET quiz_score=? WHERE session_id=?",
        (score, session_id)
    )
    c.commit()

    return {"score": score}

# =================================================
# TRANSCRIPTION
# =================================================

@app.post("/transcription_task")
def transcription_task(payload: dict = Body(...)):
    session_id = payload["session_id"]

    c = db()
    row = c.execute(
        "SELECT project FROM sessions WHERE session_id=?",
        (session_id,)
    ).fetchone()

    path = os.path.join(
        project_path(row["project"]),
        "transcription_tasks.json"
    )

    data = load_json_safe(path)
    selected = random.sample(data["tasks"], 4)

    tasks = [{
        "task_id": t["id"],
        "audio_url": f"/audio/{row['project']}/{t['audio_file']}",
        "gold_text": t["gold_text"]
    } for t in selected]

    c.execute(
        "UPDATE sessions SET transcription_json=? WHERE session_id=?",
        (json.dumps(tasks), session_id)
    )
    c.commit()

    return {"tasks": tasks}


@app.post("/submit_transcription")
def submit_transcription(payload: dict = Body(...)):
    c = db()
    c.execute(
        "INSERT INTO transcriptions VALUES (?, ?, ?)",
        (
            payload["session_id"],
            payload["task_id"],
            payload["transcription"]
        )
    )
    c.commit()
    return {"ok": True}

# =================================================
# DONE / GRADING
# =================================================

@app.get("/done")
def done(session_id: str):
    ensure_grading(session_id)
    c = db()
    row = c.execute(
        "SELECT passed FROM sessions WHERE session_id=?",
        (session_id,)
    ).fetchone()
    return {"passed": bool(row["passed"])}

# =================================================
# CSV EXPORT  ✅ FIXED
# =================================================

@app.get("/export/results")
def export_results():
    c = db()
    rows = c.execute("SELECT * FROM sessions").fetchall()

    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    writer.writerow([
        "session_id",
        "project",
        "name",
        "email",
        "country",
        "age_group",
        "native_language",
        "academic_level",
        "qualification",
        "language_proficiency",
        "mcq_score",
        "transcription_score",
        "final_result"
    ])

    for r in rows:
        ensure_grading(r["session_id"])
        intake = json.loads(r["intake_json"])
        updated = c.execute(
            "SELECT quiz_score, transcription_score, passed FROM sessions WHERE session_id=?",
            (r["session_id"],)
        ).fetchone()

        writer.writerow([
            r["session_id"],
            r["project"],
            intake.get("name", ""),
            intake.get("email", ""),
            intake.get("country", ""),
            intake.get("age_group", ""),
            intake.get("native_language", ""),
            intake.get("academic_level", ""),
            intake.get("qualifications", ""),
            json.dumps(intake.get("language_proficiency", []), ensure_ascii=False),
            round(updated["quiz_score"], 6),
            round(updated["transcription_score"], 6),
            "PASS" if updated["passed"] else "FAIL"
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=results.csv"}
    )
