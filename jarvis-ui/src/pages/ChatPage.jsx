import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ChatHistory from "../components/ChatHistory";
import ChatWindow from "../components/ChatWindow";
import { sendChatMessage } from "../api/chatApi";
import { getChatHistory } from "../api/historyApi";
import "../styles/ChatPage.css";

export default function ChatPage() {
  const navigate = useNavigate();

  const [chatId, setChatId] = useState(null);
  const [conversation, setConversation] = useState({
    messages: [],
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // ==============================
  // RELOAD CHAT FROM BACKEND
  // ==============================
  const reloadConversation = async (id) => {
    const allChats = await getChatHistory();
    const found = allChats.find((c) => c.id === id);
    if (found) {
      setConversation(found);
    }
  };

  // ==============================
  // SEND MESSAGE
  // ==============================
  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userText = input;
    setInput("");
    setLoading(true);

    // show user message instantly
    setConversation((prev) => ({
      messages: [...prev.messages, { role: "user", text: userText }],
    }));

    try {
      const res = await sendChatMessage(userText, chatId);

      const activeChatId = chatId || res.chat_id;

      // first message → new chat
      if (!chatId && res.chat_id) {
        setChatId(res.chat_id);
        navigate(`/chat/${res.chat_id}`);
      }

      // 🔥 IMPORTANT: always reload from backend
      await reloadConversation(activeChatId);

    } catch (err) {
      console.error("Send message failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-layout">
      {/* LEFT SIDEBAR */}
      <ChatHistory onQuestionClick={(id) => navigate(`/chat/${id}`)} />

      {/* CHAT AREA */}
      <div className="chat-main">
        {conversation.messages.length === 0 ? (
          <div className="chat empty">
            👋 Start a new conversation or select one from history
          </div>
        ) : (
          <ChatWindow conversation={conversation} />
        )}

        {/* INPUT */}
        <div className="chat-input">
          <input
            type="text"
            placeholder="Ask Jarvis..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={loading}
          />
          <button onClick={handleSend} disabled={loading}>
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
