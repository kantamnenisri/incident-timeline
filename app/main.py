from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import os

from .parser import parse_log_text, LogEntry
from .analyzer import analyze_timeline, AnalysisResult

app = FastAPI(title="Incident Timeline Reconstructor")

class LogInput(BaseModel):
    raw_text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    return "OK"

@app.post("/parse-logs", response_model=List[LogEntry])
def parse_logs(input: LogInput):
    try:
        return parse_log_text(input.raw_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/reconstruct", response_model=AnalysisResult)
def reconstruct_timeline(input: LogInput):
    try:
        logs = parse_log_text(input.raw_text)
        return analyze_timeline(logs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def get_index():
    # Read frontend/index.html
    frontend_path = os.path.join(os.getcwd(), "frontend", "index.html")
    if not os.path.exists(frontend_path):
        # Fallback to current dir if running in a different context
        frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    
    with open(frontend_path, "r", encoding="utf-8") as f:
        return f.read()
