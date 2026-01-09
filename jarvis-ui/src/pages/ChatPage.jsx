import { useNavigate } from "react-router-dom";
import ChatHistory from "../components/ChatHistory";
import "../styles/ChatPage.css";

export default function ChatPage() {
  const navigate = useNavigate();

  return (
    <div className="chat-layout">
      <ChatHistory
        onQuestionClick={(chatId) => navigate(`/chat/${chatId}`)}
      />

      <div className="chat empty">
        👋 Start a new conversation or select one from history
      </div>
    </div>
  );
}
