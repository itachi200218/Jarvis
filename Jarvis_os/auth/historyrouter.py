from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv

from chatHistory.chathistory import (
    load,
    start_new_conversation,
    delete_conversation
)

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
        return load(user_name) if user_name else []

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


@router.delete("/history/{chat_id}")
def delete_chat(
    chat_id: str,
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

        success = delete_conversation(user_name, chat_id)

        if not success:
            return {"error": "chat not found"}

        return {"status": "deleted"}

    except Exception as e:
        print("DELETE CHAT ERROR:", e)
        return {"error": "failed"}
