import { useEffect, useRef, useState } from "react";
import "../App.css";
import JarvisScene from "../3dModel/JarvisScene";

const API_URL = "http://127.0.0.1:8000/command";

// 🔽 RENAMED COMPONENT (IMPORTANT)
function JarvisApp({ openLogin }) {
  const recognitionRef = useRef(null);
  const typingIntervalRef = useRef(null);
  const jarvisTextRef = useRef(null);

  const [listening, setListening] = useState(false);
  const [status, setStatus] = useState("Awaiting command");
  const [lastCommand, setLastCommand] = useState("");
  const [textCommand, setTextCommand] = useState("");
  const [jarvisReply, setJarvisReply] = useState("");

  // =========================
  // SPEECH RECOGNITION
  // =========================
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech Recognition not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript.trim();
      recognition.stop();
      setListening(false);
      setStatus("Processing…");
      setLastCommand(text);
      sendCommand(text);
    };

    recognition.onend = () => {
      setListening(false);
      setStatus("Awaiting command");
    };

    recognitionRef.current = recognition;
  }, []);

  // =========================
  // TYPING EFFECT (UNCHANGED)
  // =========================
  const typeJarvisReply = (text) => {
    clearInterval(typingIntervalRef.current);

    const cleanText = text.trim();
    let index = 0;
    setJarvisReply("");

    const CHARS_PER_SECOND = 13.5;
    const estimatedSpeechTime = Math.max(
      500,
      (cleanText.length / CHARS_PER_SECOND) * 1000 - 1000
    );

    const typingSpeed = Math.max(
      18,
      Math.floor(estimatedSpeechTime / cleanText.length)
    );

    typingIntervalRef.current = setInterval(() => {
      index++;
      setJarvisReply(cleanText.slice(0, index));

      if (jarvisTextRef.current) {
        jarvisTextRef.current.scrollTop =
          jarvisTextRef.current.scrollHeight;
      }

      if (index >= cleanText.length) {
        clearInterval(typingIntervalRef.current);
      }
    }, typingSpeed);
  };

  // =========================
  // BACKEND CALL
  // =========================
  const sendCommand = async (command) => {
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });

      const data = await res.json();
      setStatus("Responding…");

      typeJarvisReply(
        typeof data.reply === "string" ? data.reply : "Command executed."
      );

      setTimeout(() => setStatus("Awaiting command"), 800);
    } catch (err) {
      console.error(err);
      typeJarvisReply("Something went wrong.");
      setStatus("Awaiting command");
    }
  };

  // =========================
  // MIC TOGGLE
  // =========================
  const toggleListening = () => {
    if (!listening) {
      recognitionRef.current.start();
      setListening(true);
      setStatus("Listening…");
    } else {
      recognitionRef.current.stop();
      setListening(false);
      setStatus("Awaiting command");
    }
  };

  // =========================
  // TEXT COMMAND
  // =========================
  const handleTextSubmit = async () => {
    if (!textCommand.trim()) return;
    setLastCommand(textCommand);
    setStatus("Processing…");
    await sendCommand(textCommand);
    setTextCommand("");
  };

  // =========================
  // UI
  // =========================
return (
  <div className="hud">

    {/* 🌐 HOLOGRAPHIC GRID LAYER */}
 <div className="hud-grid">
  <div className="box-aura" />
</div>


    {/* 🎥 3D BACKGROUND */}
    <div className="three-bg">
      <JarvisScene />
    </div>

    {/* 🔐 HUD LOGIN CONTROL (TOP RIGHT) */}
    <div className="hud-login" onClick={openLogin}>
      <span className="hud-login-icon">🔐</span>
      <span className="hud-login-text">SECURE MODE</span>
    </div>

    {/* 🧠 MAIN HUD FRAME */}
    <div className="hud-frame">

      {/* HEADER */}
      <div className="hud-header">
        <div className="hud-title">J.A.R.V.I.S</div>
        <div className="hud-subtitle">
          Just A Rather Very Intelligent System
        </div>
      </div>

      {/* 🎙️ MIC ORB */}
      <div
        className={`mic-orb 
          ${listening ? "listening" : ""} 
          ${status === "Processing…" ? "processing" : ""} 
          ${status === "Responding…" ? "speaking" : ""}
        `}
        onClick={toggleListening}
      >
        🎙️
      </div>

      {/* 📡 STATUS */}
      <div className="status">{status}</div>

      {/* 👤 USER COMMAND */}
      {lastCommand && (
        <div className="command-box user">
          <span className="label">USER</span>
          <span className="text">{lastCommand}</span>
        </div>
      )}

      {/* 🤖 JARVIS REPLY */}
      {jarvisReply && (
        <div className="command-box jarvis">
          <span className="label">JARVIS</span>
          <span className="text" ref={jarvisTextRef}>
            {jarvisReply}
          </span>
        </div>
      )}

      {/* ⌨️ TEXT INPUT */}
      <div className="text-input">
        <input
          type="text"
          placeholder="Type command…"
          value={textCommand}
          onChange={(e) => setTextCommand(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleTextSubmit()}
        />
        <button onClick={handleTextSubmit}>EXECUTE</button>
      </div>

    </div>
  </div>
)}


export default JarvisApp;
