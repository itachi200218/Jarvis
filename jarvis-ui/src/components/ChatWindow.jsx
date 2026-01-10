import "../styles/ChatPage.css";

export default function ChatWindow({ conversation }) {
  if (!conversation || !conversation.messages?.length) {
    return (
      <div className="chat empty">
        👋 Start a new conversation or click history
      </div>
    );
  }

  return (
    <div className="chat">
      {conversation.messages.map((msg, i) => {
        const time = msg.time
          ? new Date(msg.time)
          : new Date(); // 🔥 fallback for live messages

        return (
          <div key={i} className={`msg ${msg.role}`}>
            <div className="msg-text">{msg.text}</div>
            <div className="msg-time">
              {time.toLocaleTimeString()}
            </div>
          </div>
        );
      })}
    </div>
  );
}
