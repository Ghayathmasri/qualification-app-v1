from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jiwer import wer

# -------------------------------------------------
# App initialization
# -------------------------------------------------
app = FastAPI(
    title="Qualification App v1",
    description="Management demo – v1 (locked)",
    version="1.0"
)

# -------------------------------------------------
# STATIC FILES (if you use them)
# -------------------------------------------------
# Uncomment ONLY if you already had static files locally
# app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------------------------------------
# HOME PAGE (NEW – FOR DEMO)
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Qualification App v1</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f7f7f7;
                    padding: 40px;
                }
                .box {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    max-width: 600px;
                    margin: auto;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { color: #333; }
                a {
                    display: inline-block;
                    margin-top: 15px;
                    padding: 10px 15px;
                    background: #2563eb;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="box">
                <h1>Qualification App v1</h1>
                <p>Status: <b>LIVE</b></p>
                <p>This is a frozen v1 demo environment.</p>
                <a href="/docs">Open API Demo (Swagger UI)</a>
            </div>
        </body>
    </html>
    """

# -------------------------------------------------
# EXISTING ENDPOINTS (KEEP YOURS BELOW)
# -------------------------------------------------

@app.post("/evaluate")
async def evaluate(
    reference: str = Form(...),
    hypothesis: str = Form(...)
):
    score = wer(reference, hypothesis)
    return {
        "wer": score
    }

# -------------------------------------------------
# HEALTH CHECK (OPTIONAL BUT GOOD)
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
