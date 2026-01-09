import threading
import uvicorn
import os
import jwt
from dotenv import load_dotenv

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from jarvis_core import handle_command, speak_async
from auth.router import router as auth_router
from auth.historyrouter import router as history_router

# ==============================
# LOAD ENV
# ==============================
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET not loaded")

security = HTTPBearer(auto_error=False)

# ==============================
# FASTAPI APP
# ==============================
app = FastAPI(title="Jarvis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(auth_router)
app.include_router(history_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==============================
# STARTUP
# ==============================
@app.on_event("startup")
def startup_event():
    threading.Thread(
        target=lambda: speak_async("Hello. I am Jarvis. System is online."),
        daemon=True
    ).start()

# ==============================
# MODELS
# ==============================
class CommandRequest(BaseModel):
    command: str
    chat_id: str | None = None   # 🔥 REQUIRED

# ==============================
# ROUTES
# ==============================
@app.get("/")
def root():
    return {"status": "Jarvis is running"}

@app.post("/command")
def execute_command(
    req: CommandRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_role = "guest"
    user_name = None

    if credentials and credentials.credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )

            name = payload.get("name")
            if name:
                user_role = "user"
                user_name = name

        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass

    return handle_command(
        command=req.command,
        user_role=user_role,
        user_name=user_name,
        chat_id=req.chat_id     # 🔥 PASS IT
    )

# ==============================
# ENTRY
# ==============================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
