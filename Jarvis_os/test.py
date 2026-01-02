import sounddevice as sd
import queue
import json
import psutil
import time
import threading
import subprocess
import os
import socket
import shutil
import pyautogui
from vosk import Model, KaldiRecognizer

# ======================================
# WINDOWS NATIVE SPEECH (100% RELIABLE)
# ======================================
def speak(text):
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

# ======================================
# SYSTEM CONTROL FUNCTIONS
# ======================================
def open_chrome():
    speak("Opening Google Chrome.")
    subprocess.Popen("start chrome", shell=True)

def open_vscode():
    speak("Opening Visual Studio Code.")
    subprocess.Popen("code", shell=True)

def shutdown_system():
    speak("Shutting down the system.")
    subprocess.Popen("shutdown /s /t 5", shell=True)

def restart_system():
    speak("Restarting the system.")
    subprocess.Popen("shutdown /r /t 5", shell=True)

def increase_volume():
    speak("Increasing system volume.")
    for _ in range(10):
        pyautogui.press("volumeup")

def take_screenshot():
    path = os.path.join(os.path.expanduser("~"), "Desktop", "jarvis_screenshot.png")
    pyautogui.screenshot(path)
    speak("Screenshot taken and saved on desktop.")

# ======================================
# SYSTEM INFO FUNCTIONS
# ======================================
def cpu_usage():
    usage = psutil.cpu_percent(interval=1)
    speak(f"CPU usage is {usage} percent.")

def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        speak(f"Battery level is {battery.percent} percent.")
    else:
        speak("Battery information is not available.")

def disk_space():
    total, used, free = shutil.disk_usage("/")
    free_gb = round(free / (1024**3), 2)
    total_gb = round(total / (1024**3), 2)
    speak(f"You have {free_gb} gigabytes free out of {total_gb}.")

def network_status():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        speak("You are connected to the internet.")
    except OSError:
        speak("No internet connection detected.")

# ======================================
# COMMAND HANDLER
# ======================================
def handle_command(command):
    command = command.lower().strip()
    if not command:
        return

    print("🧠 Command:", command)

    if "hello" in command:
        speak("Hello. How can I help you?")

    elif "open chrome" in command:
        open_chrome()

    elif "open vs code" in command or "open vscode" in command:
        open_vscode()

    elif "shutdown" in command:
        shutdown_system()

    elif "restart" in command:
        restart_system()

    elif "increase volume" in command:
        increase_volume()

    elif "screenshot" in command:
        take_screenshot()

    elif "cpu" in command:
        cpu_usage()

    elif "battery" in command:
        battery_status()

    elif "disk" in command:
        disk_space()

    elif "network" in command or "internet" in command:
        network_status()

    elif "ram" in command or "memory" in command:
        ram = psutil.virtual_memory()
        used = round(ram.used / (1024 ** 3), 2)
        total = round(ram.total / (1024 ** 3), 2)
        speak(f"You are using {used} gigabytes of RAM out of {total}.")

    elif "exit" in command or "stop" in command:
        speak("Shutting down. Goodbye.")
        time.sleep(1)
        exit(0)

    else:
        speak("I did not understand that command.")

# ======================================
# TEXT INPUT THREAD
# ======================================
def text_input_loop():
    while True:
        text = input("⌨️ You: ")
        handle_command(text)

threading.Thread(target=text_input_loop, daemon=True).start()

# ======================================
# VOICE INPUT (VOSK)
# ======================================
audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    audio_queue.put(bytes(indata))

model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

print("🎙️ Jarvis is listening (voice + text)...")
speak("Hello. I am Jarvis. System is online.")

# ======================================
# VOICE LOOP
# ======================================
while True:
    stream = sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    )
    stream.start()

    while True:
        data = audio_queue.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()

            if text:
                stream.stop()
                stream.close()
                handle_command(text)
                time.sleep(0.3)
                break
