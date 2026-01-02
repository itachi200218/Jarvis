# main.py
import threading
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from jarvis_core import handle_command, speak

# ==============================
# FASTAPI APP
# ==============================
app = FastAPI(title="Jarvis API")

# ==============================
# CORS (REQUIRED FOR REACT)
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# STARTUP EVENT
# ==============================
@app.on_event("startup")
def startup_event():
    threading.Thread(
        target=lambda: speak("Hello. I am Jarvis. System is online."),
        daemon=True
    ).start()

# ==============================
# REQUEST MODEL
# ==============================
class CommandRequest(BaseModel):
    command: str

# ==============================
# ROUTES
# ==============================
@app.get("/")
def root():
    return {"status": "Jarvis is running"}

@app.post("/command")
def execute_command(req: CommandRequest):
    reply = handle_command(req.command)
    return {
        "command": req.command,
        "reply": reply
    }

# ==============================
# ENTRY POINT (THIS IS THE KEY)
# ==============================
if __name__ == "__main__":
    print("🚀 Starting Jarvis FastAPI server...")
    uvicorn.run(
        "main:app",      # important
        host="127.0.0.1",
        port=8000,
        reload=False
    )
