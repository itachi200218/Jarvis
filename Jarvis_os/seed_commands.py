# seed_commands.py
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# ==============================
# LOAD ENV
# ==============================
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = "Jarvis"
COLLECTION_NAME = "commands"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
commands_col = db[COLLECTION_NAME]

# ==============================
# COMMAND SEED DATA
# ==============================
COMMANDS = [
    {
        "intent": "open_chrome",
        "patterns": [
            "open chrome",
            "open crome",
            "launch chrome",
            "start chrome",
            "open google chrome"
        ]
    },
    {
        "intent": "open_vscode",
        "patterns": [
            "open vs code",
            "open vscode",
            "launch vscode",
            "start vs code"
        ]
    },
    {
        "intent": "shutdown",
        "patterns": [
            "shutdown",
            "shut down system",
            "turn off pc",
            "power off"
        ]
    },
    {
        "intent": "restart",
        "patterns": [
            "restart",
            "restart system",
            "reboot pc"
        ]
    },
    {
        "intent": "volume_up",
        "patterns": [
            "increase volume",
            "volume up",
            "raise volume"
        ]
    },
    {
        "intent": "volume_down",
        "patterns": [
            "decrease volume",
            "volume down",
            "lower volume"
        ]
    },
    {
        "intent": "mute_volume",
        "patterns": [
            "mute",
            "mute volume",
            "silence sound"
        ]
    },
    {
        "intent": "screenshot",
        "patterns": [
            "take screenshot",
            "capture screen",
            "take a screenshot"
        ]
    },
    {
        "intent": "cpu_usage",
        "patterns": [
            "cpu usage",
            "cpu status",
            "processor usage"
        ]
    },
    {
        "intent": "ram_usage",
        "patterns": [
            "ram usage",
            "memory usage",
            "ram status"
        ]
    },
    {
        "intent": "gpu_usage",
        "patterns": [
            "gpu usage",
            "graphics usage",
            "gpu status",
            "graphics card usage"
        ]
    },
    {
        "intent": "battery_status",
        "patterns": [
            "battery",
            "battery percentage",
            "battery level",
            "battery status"
        ]
    },
    {
        "intent": "disk_space",
        "patterns": [
            "disk space",
            "storage",
            "free space"
        ]
    },
    {
        "intent": "network_status",
        "patterns": [
            "network status",
            "internet status",
            "am i connected to internet"
        ]
    },
    {
        "intent": "open_explorer",
        "patterns": [
            "open file explorer",
            "open explorer",
            "open files"
        ]
    },
    {
        "intent": "open_settings",
        "patterns": [
            "open settings",
            "open system settings",
            "open windows settings"
        ]
    },
    {
        "intent": "current_time",
        "patterns": [
            "what time is it",
            "current time",
            "tell me the time"
        ]
    },
    {
        "intent": "current_date",
        "patterns": [
            "what is today's date",
            "current date",
            "tell me the date"
        ]
    },
    {
        "intent": "exit",
        "patterns": [
            "exit",
            "stop",
            "close jarvis",
            "quit"
        ]
    }
]

# ==============================
# INSERT LOGIC (SAFE)
# ==============================
def seed_commands():
    inserted = 0

    for cmd in COMMANDS:
        exists = commands_col.find_one({"intent": cmd["intent"]})

        if exists:
            print(f"⚠️ Already exists: {cmd['intent']}")
            continue

        cmd["createdAt"] = datetime.utcnow()
        cmd["updatedAt"] = datetime.utcnow()
        commands_col.insert_one(cmd)
        inserted += 1
        print(f"✅ Inserted: {cmd['intent']}")

    print(f"\n🎉 Done. Inserted {inserted} new commands.")

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    seed_commands()
