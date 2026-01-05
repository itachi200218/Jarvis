# main.py
import threading
import sys
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from jarvis_core import handle_command, speak_async

# ==============================
# FASTAPI APP
# ==============================
app = FastAPI(title="Jarvis API")

# ==============================
# CORS (REACT SUPPORT)
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# STARTUP GREETING (API MODE)
# ==============================
@app.on_event("startup")
def startup_event():
    threading.Thread(
        target=lambda: speak_async("Hello. I am Jarvis. System is online."),
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
    return handle_command(req.command)

# ==============================
# CMD / WAKE-WORD MODE
# ==============================
def run_cmd_mode():
    if "--greet" in sys.argv:
        speak_async("Yes. How can I help you?")
        return

    if "--command" in sys.argv:
        idx = sys.argv.index("--command") + 1
        if idx < len(sys.argv):
            command = sys.argv[idx]
            handle_command(command)
        return

# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":

    # 🔥 If launched from wake-word listener
    if "--greet" in sys.argv or "--command" in sys.argv:
        run_cmd_mode()

    # 🔥 Normal API server
    else:
        print("🚀 Starting Jarvis FastAPI server...")
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=False
        )
