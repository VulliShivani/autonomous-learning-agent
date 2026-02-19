from fastapi import FastAPI
from backend.db import get_connection

app = FastAPI(title="Learning Agent Backend")

@app.get("/")
def root():
    return {"status": "Backend running"}

@app.get("/progress")
def get_progress():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT mode, topic, score, attempt, created_at FROM progress"
    )
    rows = cur.fetchall()
    conn.close()
    return rows