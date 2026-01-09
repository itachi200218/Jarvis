import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getChatHistory } from "../api/historyApi";

export default function ChatHistory() {
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    getChatHistory().then((data) => setHistory(data || []));
  }, []);

  return (
    <div className="history">
      <h3>🗂 Chat History</h3>

      {history.map((chat) => {
        const firstUserMsg = chat.messages.find(
          (m) => m.role === "user"
        );

        if (!firstUserMsg) return null;

        return (
          <div
            key={chat.id}
            className="history-item clickable"
            onClick={() => navigate(`/chat/${chat.id}`)} // ✅ ONLY THIS
          >
            <div className="title">{firstUserMsg.text}</div>
            <div className="time">
              {new Date(chat.started_at).toLocaleString()}
            </div>
          </div>
        );
      })}
    </div>
  );
}
