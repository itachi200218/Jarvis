const BASE_URL = "http://127.0.0.1:8000";

// 🔥 CREATE NEW CHAT (ON LOGIN)
export async function createNewChat() {
  const token = sessionStorage.getItem("jarvis_token");

  const res = await fetch(`${BASE_URL}/auth/new-chat`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to create new chat");
  }

  return res.json(); // { chat_id, started_at }
}

// 📜 GET CHAT HISTORY
export async function getChatHistory() {
  const token = sessionStorage.getItem("jarvis_token");

  const res = await fetch(`${BASE_URL}/auth/history`, {
    headers: token
      ? { Authorization: `Bearer ${token}` }
      : {},
  });

  if (!res.ok) {
    throw new Error("Failed to fetch history");
  }

  return res.json();
}
