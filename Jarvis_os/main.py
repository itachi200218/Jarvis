import threading
import sys
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

app.include_router(auth_router)

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

    if credentials and credentials.credentials:
        try:
            payload = jwt.decode(
                credentials.credentials,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )

            # ✅ THIS LINE IS THE KEY
            if payload.get("sub"):
                user_role = "user"

        except jwt.ExpiredSignatureError:
            user_role = "guest"
        except jwt.InvalidTokenError:
            user_role = "guest"

    return handle_command(req.command, user_role=user_role)

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
