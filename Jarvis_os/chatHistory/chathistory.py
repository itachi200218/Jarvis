import json
import os
from datetime import datetime
from uuid import uuid4

BASE_DIR = "chatHistory/data"
os.makedirs(BASE_DIR, exist_ok=True)


def _get_file(user_id: str):
    return os.path.join(BASE_DIR, f"{user_id}.json")


# ==============================
# LOAD ALL CHATS
# ==============================
def load(user_id: str):
    path = _get_file(user_id)

    if not os.path.exists(path):
        return []

    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


# ==============================
# SAVE ALL CHATS
# ==============================
def save(user_id: str, chats):
    with open(_get_file(user_id), "w") as f:
        json.dump(chats, f, indent=2)


# ==============================
# START NEW CHAT
# ==============================
def start_new_conversation(user_id: str):
    chats = load(user_id)

    convo = {
        "id": str(uuid4()),
        "started_at": datetime.utcnow().isoformat(),
        "messages": []
    }

    chats.append(convo)
    save(user_id, chats)

    return convo["id"]


# ==============================
# ADD MESSAGE
# ==============================
def add_message(chat_id: str, user_id: str, role: str, text: str):
    chats = load(user_id)

    # Try to find existing chat
    for convo in chats:
        if convo["id"] == chat_id:
            convo["messages"].append({
                "role": role,
                "text": text,
                "time": datetime.utcnow().isoformat()
            })
            save(user_id, chats)
            return chat_id

    # 🔥 CHAT NOT FOUND → CREATE NEW ONE
    print("⚠️ Chat ID not found, creating new chat")

    new_convo = {
        "id": str(uuid4()),
        "started_at": datetime.utcnow().isoformat(),
        "messages": [
            {
                "role": role,
                "text": text,
                "time": datetime.utcnow().isoformat()
            }
        ]
    }

    chats.append(new_convo)
    save(user_id, chats)

    return new_convo["id"]
