from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv

from chatHistory.chathistory import (
    start_new_conversation,
    add_message
)

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)
router = APIRouter(prefix="/chat", tags=["Chat"])


def generate_jarvis_reply(text: str) -> str:
    if "joke" in text.lower():
        return "Why couldn't the bicycle stand up by itself? Because it was two tired!"
    return "I am Jarvis, ready to help you."


@router.post("/message")
def send_message(
    data: dict,
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

        user_text = data.get("text")
        chat_id = data.get("chat_id")
        print("🔥 /chat/message HIT:", user_text)

        if not user_text:
            return {"error": "empty message"}

        # ✅ CREATE CHAT ONLY ONCE
        if not chat_id:
            chat_id = start_new_conversation(user_name)

        # ✅ SAVE USER MESSAGE
        add_message(chat_id, user_name, "user", user_text)

        # 🤖 JARVIS REPLY
        jarvis_reply = generate_jarvis_reply(user_text)

        # ✅ SAVE JARVIS MESSAGE IN SAME CHAT
        add_message(chat_id, user_name, "jarvis", jarvis_reply)

        return {
            "chat_id": chat_id,
            "reply": jarvis_reply
        }

    except Exception as e:
        print("MESSAGE ERROR:", e)
        return {"error": "invalid token"}
