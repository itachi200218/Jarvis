import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/command";

function App() {
  const recognitionRef = useRef(null);

  const [listening, setListening] = useState(false);
  const [lastCommand, setLastCommand] = useState("");
  const [textCommand, setTextCommand] = useState("");
  const [jarvisReply, setJarvisReply] = useState("");

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onresult = async (event) => {
      const text =
        event.results[event.results.length - 1][0].transcript.trim();

      console.log("🎙️ You said:", text);
      setLastCommand(text);
      await sendCommand(text);
    };

    recognition.onend = () => setListening(false);

    recognitionRef.current = recognition;
  }, []);

  const sendCommand = async (command) => {
    if (!command) return;

    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command }),
    });

    const data = await res.json();

    // 👇 MUST MATCH BACKEND RESPONSE KEY
    setJarvisReply(data.response || data.reply || "");
  };

  const toggleListening = () => {
    if (!listening) {
      recognitionRef.current.start();
      setListening(true);
    } else {
      recognitionRef.current.stop();
      setListening(false);
    }
  };

  const handleTextSubmit = async () => {
    if (!textCommand.trim()) return;
    setLastCommand(textCommand);
    await sendCommand(textCommand);
    setTextCommand("");
  };

  return (
    <div className="app">
      {/* MIC ORB */}
      <div
        className={`mic-orb ${listening ? "listening" : ""}`}
        onClick={toggleListening}
      >
        🎙️
      </div>

      {/* STATUS */}
      <p className="status">
        {listening ? "Listening…" : "Tap the mic or type a command"}
      </p>

      {/* USER COMMAND */}
      {lastCommand && (
        <div className="command-box user">
          {lastCommand}
        </div>
      )}

      {/* JARVIS REPLY (SIRI STYLE) */}
      {jarvisReply && (
        <div className="command-box jarvis">
          {jarvisReply}
        </div>
      )}

      {/* OPTIONAL TEXT INPUT */}
      <div className="text-input">
        <input
          type="text"
          placeholder="Type a command (optional)"
          value={textCommand}
          onChange={(e) => setTextCommand(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleTextSubmit()}
        />
        <button onClick={handleTextSubmit}>Send</button>
      </div>
    </div>
  );
}

export default App;
