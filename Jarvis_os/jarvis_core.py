# jarvis_core.py
import os
import psutil
import subprocess
import socket
import shutil
import pyautogui
import re
import threading
from datetime import datetime

from pymongo import MongoClient
from dotenv import load_dotenv
from rapidfuzz import fuzz
from ai_fallback import get_ai_response
from weather_service import get_weather
from time_service import get_time_from_timezone_db
from maps_service import get_distance
from location_service import get_current_location

# ==============================
# LOAD ENV
# ==============================
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("MONGO_DB")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
commands_col = db[COLLECTION_NAME]
# ==============================
# 🔐 GUEST RESTRICTION
# ==============================

GUEST_ALLOWED_INTENTS = {
    "wake",
    "ai_fallback",
}

# ==============================
# 🔐 ROLE BASED ACCESS (ADDED)
# ==============================
AI_ONLY_INTENTS = {
    "wake",
    "weather",
    "time",
    "maps",
    "creator",
    "about_creator",
    "projects_of_creator",
    "ai_fallback",
    "current_time",
    "current_date",
}

SYSTEM_INTENTS = {
    "open_chrome",
    "open_vscode",
    "shutdown",
    "restart",
    "volume_up",
    "volume_down",
    "mute_volume",
    "screenshot",
    "cpu_usage",
    "ram_usage",
    "gpu_usage",
    "battery_status",
    "disk_space",
    "network_status",
    "open_explorer",
    "open_settings",
}

# ==============================
# SPEECH (WINDOWS)
# ==============================
def speak(text: str):
    print("🤖 Jarvis:", text)
    safe_text = text.replace('"', "'")

    ps_script = f'''
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.Rate = 0
    $synth.Volume = 100
    $synth.Speak("{safe_text}")
    '''

    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def speak_async(text: str):
    threading.Thread(target=speak, args=(text,), daemon=True).start()

# ==============================
# NORMALIZE TEXT
# ==============================
STOP_WORDS = {
    "please", "can", "you", "tell", "me", "the",
    "a", "an", "is", "my", "what", "about"
}

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]
    return " ".join(words)

# ==============================
# SYSTEM ACTIONS
# ==============================
def open_chrome(): subprocess.Popen("start chrome", shell=True)
def open_vscode(): subprocess.Popen("code", shell=True)
def shutdown_system(): subprocess.Popen("shutdown /s /t 5", shell=True)
def restart_system(): subprocess.Popen("shutdown /r /t 5", shell=True)

def increase_volume():
    for _ in range(10): pyautogui.press("volumeup")

def decrease_volume():
    for _ in range(10): pyautogui.press("volumedown")

def mute_volume(): pyautogui.press("volumemute")

def take_screenshot():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    path = os.path.join(desktop, "Jarvis", "Screenshots")
    os.makedirs(path, exist_ok=True)

    file = f"jarvis_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    full = os.path.join(path, file)
    pyautogui.screenshot(full)
    return full

def open_explorer(): subprocess.Popen("explorer", shell=True)
def open_settings(): subprocess.Popen("start ms-settings:", shell=True)

# ==============================
# SYSTEM INFO
# ==============================
def cpu_usage(): return f"CPU usage is {psutil.cpu_percent(interval=1)} percent."
def ram_usage():
    r = psutil.virtual_memory()
    return f"You are using {round(r.used/1e9,2)} GB out of {round(r.total/1e9,2)} GB."
def battery_status():
    b = psutil.sensors_battery()
    return f"Battery level is {b.percent} percent." if b else "Battery info unavailable."
def disk_space():
    t, _, f = shutil.disk_usage("/")
    return f"{round(f/1e9,2)} GB free out of {round(t/1e9,2)} GB."
def network_status():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return "Internet is connected."
    except:
        return "No internet connection."

def gpu_usage():
    try:
        out = subprocess.check_output(
            "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits",
            shell=True
        )
        return f"GPU usage is {out.decode().strip()} percent."
    except:
        return "GPU usage information is unavailable."

def current_time(): return datetime.now().strftime("The time is %I:%M %p.")
def current_date(): return datetime.now().strftime("Today is %B %d, %Y.")

# ==============================
# FUZZY MATCH
# ==============================
def find_intent(command: str):
    command = normalize_text(command)
    best_intent, best_score = None, 0

    for doc in commands_col.find():
        for pattern in doc.get("patterns", []):
            score = (
                fuzz.token_set_ratio(command, pattern) * 0.5 +
                fuzz.partial_ratio(command, pattern) * 0.3 +
                fuzz.ratio(command, pattern) * 0.2
            )
            if score > best_score:
                best_score = score
                best_intent = doc["intent"]

    return (best_intent, int(best_score)) if best_score >= 70 else (None, int(best_score))
    # ==============================
    # 👤 USER IDENTITY QUERIES
    # ==============================
    if "my name" in raw:
        if user_role == "guest" or not user_name:
            response = "You are currently using guest access."
        else:
            response = f"Your name is {user_name}."
        speak_async(response)
        return {
            "reply": response,
            "intent": "user_identity",
            "confidence": 100
        }

# ==============================
# 🔥 SINGLE COMMAND ROUTER
# ==============================
def handle_command(command: str, user_role: str = "guest"):
    raw = command.strip().lower()

    # WAKE WORD
    if raw in {"hello", "hey jarvis", "jarvis"}:
        response = "Yes. How can I help you?"
        speak_async(response)
        return {"reply": response, "intent": "wake", "confidence": 100}

    if not raw:
        response = "I did not hear anything."
        speak_async(response)
        return {"reply": response, "intent": None, "confidence": 0}

    intent, confidence = find_intent(raw)
    print(f"🧠 Intent: {intent}, Confidence: {confidence}%")
    # ==============================
    # 🔐 STRICT GUEST ENFORCEMENT
    # ==============================
    if user_role == "guest":
        # intent == None → AI fallback → ALLOW
        if intent is not None and intent not in GUEST_ALLOWED_INTENTS:
            response = (
                "Guest access limited. "
                "Please sign in to access system features."
            )
            speak_async(response)
            return {
                "reply": response,
                "intent": intent,
                "confidence": confidence
            }

 
    # ==============================
    # SYSTEM / DB INTENTS
    # ==============================
    if intent == "open_chrome":
        open_chrome()
        response = "Opening Google Chrome."

    elif intent == "open_vscode":
        open_vscode()
        response = "Opening Visual Studio Code."

    elif intent == "shutdown":
        shutdown_system()
        response = "Shutting down the system."

    elif intent == "restart":
        restart_system()
        response = "Restarting the system."

    elif intent == "volume_up":
        increase_volume()
        response = "Increasing volume."

    elif intent == "volume_down":
        decrease_volume()
        response = "Decreasing volume."

    elif intent == "mute_volume":
        mute_volume()
        response = "Volume muted."

    elif intent == "screenshot":
        take_screenshot()
        response = "Screenshot saved successfully."

    elif intent == "cpu_usage":
        response = cpu_usage()

    elif intent == "ram_usage":
        response = ram_usage()

    elif intent == "gpu_usage":
        response = gpu_usage()

    elif intent == "battery_status":
        response = battery_status()

    elif intent == "disk_space":
        response = disk_space()

    elif intent == "network_status":
        response = network_status()

    elif intent == "open_explorer":
        open_explorer()
        response = "Opening File Explorer."

    elif intent == "open_settings":
        open_settings()
        response = "Opening Settings."

    elif intent == "current_time":
        response = current_time()

    elif intent == "current_date":
        response = current_date()

    elif "weather" in raw:
        city = raw.replace("weather", "").replace("in", "").strip()
        response = get_weather(city or "your location")
        intent = "weather"
        confidence = 100

    elif "time in" in raw:
        location = raw.replace("time in", "").strip()
        response = get_time_from_timezone_db(location)
        intent = "time"
        confidence = 100

    elif "distance" in raw:
        cleaned = raw.replace("distance", "").strip()
        if " to " in cleaned:
            source, destination = cleaned.split(" to ", 1)
            response = get_distance(source.strip(), destination.strip())
        else:
            response = get_distance(None, cleaned)
        intent = "maps"
        confidence = 100

    elif "who created you" in raw or "who made you" in raw:
        response = "I was created by A Chetan. He is my creator."
        intent = "creator"
        confidence = 100

    else:
        response = get_ai_response(command)
        intent = "ai_fallback"
        confidence = 0

    speak_async(response)
    return {"reply": response, "intent": intent, "confidence": confidence}
