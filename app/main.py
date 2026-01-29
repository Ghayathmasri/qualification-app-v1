from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jiwer import wer
import os

# -------------------------------------------------
# App initialization
# -------------------------------------------------
app = FastAPI(
    title="Qualification App v1",
    description="Management demo – v1 (locked)",
    version="1.0"
)

# -------------------------------------------------
# STATIC FILES (THIS IS THE MISSING PIECE)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Qualification App v1</title>
        </head>
        <body style="font-family: Arial; padding: 40px;">
            <h1>Qualification App v1</h1>
            <p>Status: <b>LIVE</b></p>

            <ul>
                <li><a href="/static/intake.html?project=transcription">
                    Open Qualification Intake Form
                </a></li>
                <li><a href="/docs">API Documentation</a></li>
            </ul>
        </body>
    </html>
    """

# -------------------------------------------------
# API ENDPOINTS (UNCHANGED)
# -------------------------------------------------
@app.post("/evaluate")
async def evaluate(
    reference: str = Form(...),
    hypothesis: str = Form(...)
):
    score = wer(reference, hypothesis)
    return {"wer": score}

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
