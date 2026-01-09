import requests
import speech_recognition as sr
import time
import os

API_URL = "http://127.0.0.1:8000/command"
WAKE_WORDS = ("hey jarvis", "hello jarvis", "jarvis")

recognizer = sr.Recognizer()
microphone = sr.Microphone()

def get_token():
    return os.getenv("JARVIS_TOKEN")  # token exists only if logged in

def send_to_jarvis(text):
    headers = {}

    token = get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        requests.post(
            API_URL,
            json={"command": text},
            headers=headers,
            timeout=3
        )
    except Exception as e:
        print("❌ Backend not reachable:", e)
