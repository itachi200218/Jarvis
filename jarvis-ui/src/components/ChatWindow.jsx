import "../styles/ChatPage.css";

export default function ChatWindow({ conversation }) {
  if (!conversation) {
    return (
      <div className="chat empty">
        👋 Start a new conversation or click history
      </div>
    );
  }

  return (
    <div className="chat">
      {conversation.messages.map((msg, i) => (
        <div key={i} className={`msg ${msg.role}`}>
          <div className="msg-text">{msg.text}</div>
          {msg.time && (
            <div className="msg-time">
              {new Date(msg.time).toLocaleTimeString()}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
