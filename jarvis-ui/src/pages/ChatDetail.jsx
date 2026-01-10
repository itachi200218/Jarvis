import { useParams, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { getChatHistory } from "../api/historyApi";
import JarvisScene from "../3dModel/JarvisScene";

export default function ChatDetail() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [chat, setChat] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    getChatHistory().then((data) => {
      const found = data.find((c) => c.id === chatId);
      setChat(found || null);
      setLoading(false);
    });
  }, [chatId, location.pathname]); // 🔥 refresh when URL changes

  if (loading) {
    return <div>Loading chat...</div>;
  }

  if (!chat) {
    return <div>Chat not found</div>;
  }

  return (
    <div className="hud chat-history-page">
      {/* SAME GRID + AURA */}
      <div className="hud-grid">
        <div className="box-aura" />
      </div>

      {/* SAME 3D BACKGROUND */}
      <div className="three-bg">
        <JarvisScene />
      </div>

      {/* CHAT CONTENT */}
      <div className="hud-frame chat-detail">
        {/* 🔙 BACK TO HOME BUTTON */}
        <button
          className="back-home-btn"
          onClick={() => navigate("/")}
        >
          ⬅ Back to Home
        </button>

        <div className="hud-header">
          <div className="hud-title">J.A.R.V.I.S</div>
        </div>

        {chat.messages.length === 0 ? (
          <div className="chat empty">
            No messages in this conversation yet.
          </div>
        ) : (
          chat.messages.map((msg, i) => (
            <div key={i} className={`command-box ${msg.role}`}>
              <span className="label">{msg.role.toUpperCase()}</span>
              <span className="text">{msg.text}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
