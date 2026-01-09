from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv

from chatHistory.chathistory import load, start_new_conversation

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)
router = APIRouter(prefix="/auth", tags=["Chat History"])


@router.get("/history")
def get_chat_history(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not credentials:
        return []

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        user_name = payload.get("name")
        if not user_name:
            return []

        return load(user_name)

    except Exception as e:
        print("JWT ERROR:", e)
        return []


@router.post("/new-chat")
def new_chat(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not credentials:
        return {"error": "unauthorized"}

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        user_name = payload.get("name")
        if not user_name:
            return {"error": "invalid user"}

        chat_id = start_new_conversation(user_name)
        return {"chat_id": chat_id}

    except Exception as e:
        print("JWT ERROR:", e)
        return {"error": "invalid token"}
