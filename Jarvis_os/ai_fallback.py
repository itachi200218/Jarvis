# ai_fallback.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_ai_response(user_command: str) -> str:
    if not OPENROUTER_API_KEY:
        return "My AI brain is not configured."

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a calm and intelligent AI assistant. "
                        "Reply briefly and clearly."
                    )
                },
                {
                    "role": "user",
                    "content": user_command
                }
            ],
            "temperature": 0.7
        }

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=10
        )

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except Exception:
        return "I encountered an issue accessing my AI intelligence."
