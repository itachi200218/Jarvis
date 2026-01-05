# wake_router.py
import requests
import speech_recognition as sr
import time

API_URL = "http://127.0.0.1:8000/command"
WAKE_WORDS = ("hey jarvis", "hello jarvis", "jarvis")

recognizer = sr.Recognizer()
microphone = sr.Microphone()

def send_to_jarvis(text):
    try:
        requests.post(API_URL, json={"command": text}, timeout=3)
    except Exception as e:
        print("❌ Backend not reachable:", e)

def listen_once():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        audio = recognizer.listen(source, timeout=5)

    try:
        return recognizer.recognize_google(audio).lower()
    except:
        return None

def start_wake_listener():
    print("🟢 Wake-word listener active")

    while True:
        heard = listen_once()
        if not heard:
            continue

        print("🎧 Heard:", heard)

        # 🔥 WAKE WORD ONLY
        if any(wake in heard for wake in WAKE_WORDS):
            print("🟢 Wake detected")

            # Case 1: only wake word
            if heard.strip() in WAKE_WORDS:
                send_to_jarvis("hello")
                continue

            # Case 2: wake + command
            for wake in WAKE_WORDS:
                if wake in heard:
                    command = heard.replace(wake, "").strip()
                    if command:
                        send_to_jarvis(command)
                    break

        time.sleep(0.3)

if __name__ == "__main__":
    try:
        start_wake_listener()
    except KeyboardInterrupt:
        print("\n🔴 Wake listener stopped")
