# jarvis_core.py
import psutil
import subprocess
import os
import socket
import shutil
import time
import pyautogui

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

# ==============================
# SYSTEM CONTROLS
# ==============================
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
    speak("Increasing volume.")
    for _ in range(10):
        pyautogui.press("volumeup")

def take_screenshot():
    path = os.path.join(os.path.expanduser("~"), "Desktop", "jarvis_screenshot.png")
    pyautogui.screenshot(path)
    speak("Screenshot saved on desktop.")

# ==============================
# SYSTEM INFO
# ==============================
def cpu_usage():
    speak(f"CPU usage is {psutil.cpu_percent()} percent.")

def battery_status():
    b = psutil.sensors_battery()
    speak(f"Battery is at {b.percent} percent." if b else "Battery info unavailable.")

def disk_space():
    total, _, free = shutil.disk_usage("/")
    speak(f"{round(free/1e9,2)} GB free of {round(total/1e9,2)} GB.")

def network_status():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        speak("Internet is connected.")
    except:
        speak("No internet connection.")

# ==============================
# COMMAND ROUTER
# ==============================
def handle_command(command: str):
    command = command.lower().strip()
    if not command:
        return "I did not hear anything."

    if "hello" in command:
        response = "Hello. How can I help you?"

    elif "ram" in command or "memory" in command:
        ram = psutil.virtual_memory()
        response = f"You are using {round(ram.used/1e9,2)} gigabytes out of {round(ram.total/1e9,2)}."

    elif "cpu" in command:
        response = f"CPU usage is {psutil.cpu_percent()} percent."

    elif "battery" in command:
        b = psutil.sensors_battery()
        response = f"Battery level is {b.percent} percent." if b else "Battery information is unavailable."

    elif "open chrome" in command:
        open_chrome()
        response = "Opening Google Chrome."

    elif "open vs code" in command:
        open_vscode()
        response = "Opening Visual Studio Code."

    else:
        response = "Sorry, I did not understand that command."

    speak(response)
    return response
