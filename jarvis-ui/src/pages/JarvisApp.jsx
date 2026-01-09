import { useEffect, useRef, useState } from "react";
import "../App.css";
import JarvisScene from "../3dModel/JarvisScene";
import { useAuth } from "../context/authcontext_temp.jsx";
import { useNavigate } from "react-router-dom";
import { SYSTEM_COMMAND_KEYWORDS } from "../SystemCommands/commands";
import "../styles/jarvisToast.css";
import Fuse from "fuse.js"; // 🔥 ADDED

const API_URL = "http://127.0.0.1:8000/command";

// 🔥 ADDED: Frontend fuzzy matcher (same idea as backend)
const fuse = new Fuse(SYSTEM_COMMAND_KEYWORDS, {
  includeScore: true,
  threshold: 0.4, // works well for chrome / crome / cromr / chorme
});

function JarvisApp({ openLogin }) {
  const recognitionRef = useRef(null);
  const typingIntervalRef = useRef(null);
  const jarvisTextRef = useRef(null);

  const [listening, setListening] = useState(false);
  const [status, setStatus] = useState("Awaiting command");
  const [lastCommand, setLastCommand] = useState("");
  const [textCommand, setTextCommand] = useState("");
  const [jarvisReply, setJarvisReply] = useState("");

  // 🔥 ROBOTIC HUD NOTIFICATION STATE
  const [showRestriction, setShowRestriction] = useState(false);

  const { user, loading } = useAuth();
  const navigate = useNavigate();

  // =========================
  // 🔊 FRONTEND JARVIS VOICE (DENIAL ONLY)
  // =========================
  const speakFrontend = (text) => {
    if (!window.speechSynthesis) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 0.8;
    utterance.volume = 1;

    window.speechSynthesis.speak(utterance);
  };

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
  // TYPING EFFECT
  // =========================
  const typeJarvisReply = (text) => {
    if (typeof text !== "string") {
      setJarvisReply("⚠️ Invalid response from Jarvis");
      return;
    }

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
  async function sendCommand(command) {
    if (!command || !command.trim()) return;

    const token = sessionStorage.getItem("jarvis_token");
    const isGuest = !token;

    // 🔥 UPDATED: REAL fuzzy matching (frontend = backend behavior)
    const isSystemCommand = fuse.search(command.toLowerCase()).length > 0;

    // 🔒 GUEST + SYSTEM COMMAND → UI + VOICE (FRONTEND)
    if (isGuest && isSystemCommand) {
      const denyText =
        "Access denied. Guest users cannot execute system commands.";

      setStatus("Restricted");
      typeJarvisReply(
        "⛔ ACCESS DENIED — Guest users cannot execute system commands."
      );
      speakFrontend(denyText);

      setShowRestriction(true);
      setTimeout(() => setShowRestriction(false), 3000);

      return;
    }

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({ command: command.trim() }),
      });

      if (!res.ok) {
        const err = await res.json();
        typeJarvisReply(
          err?.reply ||
            err?.detail?.[0]?.msg ||
            "⚠️ Request failed"
        );
        return;
      }

      const data = await res.json();

      if (!data || typeof data.reply !== "string") {
        typeJarvisReply("⚠️ Invalid response from Jarvis");
        return;
      }

      setStatus("Responding…");
      typeJarvisReply(data.reply);
    } catch (err) {
      console.error(err);
      typeJarvisReply("Something went wrong.");
      setStatus("Awaiting command");
    }
  }

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

  if (loading) {
    return <div className="status">Initializing Jarvis…</div>;
  }

  // =========================
  // UI
  // =========================
  return (
    <div className="hud">
      <div className="hud-grid">
        <div className="box-aura" />
      </div>

      <div className="three-bg">
        <JarvisScene />
      </div>

      <div className="hud-login" onClick={() => navigate("/auth")}>
        <span className="hud-login-icon">🔐</span>
        <span className="hud-login-text">SECURE MODE</span>
      </div>

      <div className="hud-frame">
        <div className="hud-header">
          <div className="hud-title">J.A.R.V.I.S</div>

          <div className="hud-subtitle">
            <div className="hud-user">
              <div className="hud-user-info">
                <div className="hud-welcome">Welcome</div>
                <div className="hud-username">
                  {user ? user.name : "GUEST"}
                </div>
                <div className="hud-role">
                  ROLE: {user ? user.role.toUpperCase() : "LIMITED"}
                </div>
                <div
                  className={`hud-system-status ${
                    user ? "enabled" : "restricted"
                  }`}
                >
                  SYSTEM COMMANDS: {user ? "ENABLED" : "RESTRICTED"}
                </div>
              </div>

              {user && (
                <>
                  <div className="hud-divider" />
                  <button
                    className="hud-profile-btn"
                    onClick={() => navigate("/profile")}
                  >
                    PROFILE
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

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

        <div className="status">{status}</div>

        {lastCommand && (
          <div className="command-box user">
            <span className="label">USER</span>
            <span className="text">{lastCommand}</span>
          </div>
        )}

        {jarvisReply && (
          <div className="command-box jarvis">
            <span className="label">JARVIS</span>
            <span className="text" ref={jarvisTextRef}>
              {jarvisReply}
            </span>
          </div>
        )}

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

      {showRestriction && (
        <div className="jarvis-toast">
          <div className="jarvis-toast-title">🔒 ACCESS RESTRICTED</div>
          <div className="jarvis-toast-text">
            Please login to use system commands
          </div>
        </div>
      )}
    </div>
  );
}

export default JarvisApp;
