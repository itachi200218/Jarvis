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
# SPEECH (WINDOWS NATIVE)
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
# 🔥 SINGLE COMMAND ROUTER (FIXED)
# ==============================
def handle_command(command: str):
    raw = command.strip().lower()

    # 🔥 WAKE WORD HANDLER
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

    if intent == "open_chrome":
        open_chrome(); response = "Opening Google Chrome."
    elif intent == "open_vscode":
        open_vscode(); response = "Opening Visual Studio Code."
    elif intent == "shutdown":
        shutdown_system(); response = "Shutting down the system."
    elif intent == "restart":
        restart_system(); response = "Restarting the system."
    elif intent == "volume_up":
        increase_volume(); response = "Increasing volume."
    elif intent == "volume_down":
        decrease_volume(); response = "Decreasing volume."
    elif intent == "mute_volume":
        mute_volume(); response = "Volume muted."
    elif intent == "screenshot":
        take_screenshot(); response = "Screenshot saved successfully."
    elif intent == "cpu_usage": response = cpu_usage()
    elif intent == "ram_usage": response = ram_usage()
    elif intent == "gpu_usage": response = gpu_usage()
    elif intent == "battery_status": response = battery_status()
    elif intent == "disk_space": response = disk_space()
    elif intent == "network_status": response = network_status()
    elif intent == "open_explorer":
        open_explorer(); response = "Opening File Explorer."
    elif intent == "open_settings":
        open_settings(); response = "Opening Settings."
    elif intent == "current_time": response = current_time()
    elif intent == "current_date": response = current_date()
    else:
        response = "Sorry, I did not understand that command."

    speak_async(response)
    return {"reply": response, "intent": intent, "confidence": confidence}
