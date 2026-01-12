import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { getChatHistory } from "../api/historyApi";

const API_BASE = "http://127.0.0.1:8000";

export default function ChatHistory() {
  const [history, setHistory] = useState([]);
  const [deleteTarget, setDeleteTarget] = useState(null); // 🔥 modal state
  const navigate = useNavigate();
  const location = useLocation();

  const loadHistory = () => {
    getChatHistory().then((data) => setHistory(data || []));
  };

  useEffect(() => {
    loadHistory();
  }, [location.pathname]);

  // 🗑️ CONFIRM DELETE
  const confirmDelete = async () => {
    if (!deleteTarget) return;

    const token = sessionStorage.getItem("jarvis_token");
    if (!token) return;

    try {
      const res = await fetch(
        `${API_BASE}/auth/history/${deleteTarget}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await res.json();

      if (data.status === "deleted") {
        if (location.pathname.includes(deleteTarget)) {
          navigate("/");
        }
        loadHistory();
      }
    } catch (err) {
      console.error("Delete failed", err);
    } finally {
      setDeleteTarget(null); // close modal
    }
  };

  return (
    <>
      <div className="history">
        <h3>🗂 Chat History</h3>

        {history.length === 0 && (
          <div className="history-empty">No conversations yet</div>
        )}

        {history.map((chat) => {
          const firstUserMsg = chat.messages.find(
            (m) => m.role === "user"
          );
          if (!firstUserMsg) return null;

          return (
            <div key={chat.id} className="history-item">
              <div
                className="history-main"
                onClick={() => navigate(`/chat/${chat.id}`)}
              >
                <div className="title">{firstUserMsg.text}</div>
                <div className="time">
                  {new Date(chat.started_at).toLocaleString()}
                </div>
              </div>

              <button
                className="delete-btn"
                title="Delete chat"
                onClick={(e) => {
                  e.stopPropagation();
                  setDeleteTarget(chat.id); // 🔥 open modal
                }}
              >
                🗑
              </button>
            </div>
          );
        })}
      </div>

      {/* 🔥 JARVIS DELETE CONFIRM MODAL */}
      {deleteTarget && (
        <div className="jarvis-modal-backdrop">
          <div className="jarvis-modal">
            <div className="jarvis-modal-title">
              ⚠️ DELETE CONVERSATION
            </div>

            <div className="jarvis-modal-text">
              This action will permanently erase this chat history.
            </div>

            <div className="jarvis-modal-actions">
              <button
                className="jarvis-btn cancel"
                onClick={() => setDeleteTarget(null)}
              >
                CANCEL
              </button>
              <button
                className="jarvis-btn delete"
                onClick={confirmDelete}
              >
                DELETE
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
