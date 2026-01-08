import { useEffect, useRef, useState } from "react";
import "./Login.css";
import { loginUser, registerUser } from "../api/authApi";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const eyesRef = useRef(null);
  const navigate = useNavigate();

  const [focus, setFocus] = useState("none");
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState("Awaiting credentials");
  const [mode, setMode] = useState("login");

  // 🔐 form states
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [mismatch, setMismatch] = useState(false);

  // 👀 Eyes follow mouse
  useEffect(() => {
    const moveEyes = (e) => {
      if (!eyesRef.current) return;

      const eyes = eyesRef.current.querySelectorAll(".eye");
      eyes.forEach((eye) => {
        const rect = eye.getBoundingClientRect();
        const eyeX = rect.left + rect.width / 2;
        const eyeY = rect.top + rect.height / 2;

        const angle = Math.atan2(e.clientY - eyeY, e.clientX - eyeX);
        const moveX = Math.cos(angle) * 6;
        const moveY = Math.sin(angle) * 6;

        eye.style.transform = `translate(${moveX}px, ${moveY}px)`;
      });
    };

    window.addEventListener("mousemove", moveEyes);
    return () => window.removeEventListener("mousemove", moveEyes);
  }, []);

  // 🔴 Password mismatch detection
  useEffect(() => {
    if (mode !== "register") {
      setMismatch(false);
      return;
    }

    if (!password || !confirmPassword) {
      setMismatch(false);
      setStatus("Awaiting registration data");
      return;
    }

    if (password !== confirmPassword) {
      setMismatch(true);
      setStatus("Mismatch detected");
    } else {
      setMismatch(false);
      setStatus("Access keys verified");
    }
  }, [password, confirmPassword, mode]);

  // ============================
  // 🔐 AUTH HANDLER (FIXED)
  // ============================
  const handleAuth = async () => {
    try {
      if (mode === "login") {
        setStatus("Authenticating...");

        const res = await loginUser({ email, password });

        // ✅ PER TAB SESSION STORAGE (IMPORTANT)
        sessionStorage.setItem("jarvis_token", res.access_token);

        setStatus("Authentication successful ✔");

        // 🔁 AUTO REDIRECT
        setTimeout(() => {
          navigate("/");
        }, 700);
      } else {
        setStatus("Registering user...");

        await registerUser({
          name,
          email,
          password,
          confirm_password: confirmPassword,
        });

        setStatus("Registration successful ✔");
        setMode("login");
      }
    } catch (err) {
      console.error(err);
      setStatus("Access denied ❌");
      alert(err.message || "Authentication failed");
    }
  };

  return (
    <div className="page">
      <div className="card holo">

        {/* 🤖 ROBOT */}
        <div
          className={`character
            ${focus === "password" && !showPassword ? "cover" : ""}
            ${mismatch ? "alert" : ""}
          `}
        >
          <div className="robot-head" ref={eyesRef}>
            <div className="visor">
              <div className="eye"><span className="pupil" /></div>
              <div className="eye"><span className="pupil" /></div>
            </div>
            <div className="mouth">
              <span></span><span></span><span></span><span></span>
            </div>
          </div>
          <div className="ai-status">{status}</div>
        </div>

        {/* 🧠 FORM */}
        <div className="form">
          <h2>J.A.R.V.I.S</h2>
          <p className="subtitle">Secure Access Interface</p>

          <div className="robot-home-btn" onClick={() => navigate("/")}>
            <span className="home-dot"></span>
            RETURN TO HOME
          </div>

          <div
            className={`robot-toggle ${mode}`}
            onClick={() => {
              const next = mode === "login" ? "register" : "login";
              setMode(next);
              setName("");
              setEmail("");
              setPassword("");
              setConfirmPassword("");
              setMismatch(false);
              setStatus(
                next === "login"
                  ? "Authentication protocol activated"
                  : "Registration protocol activated"
              );
            }}
          >
            <span className="dot"></span>
            AUTH MODE: {mode.toUpperCase()}
          </div>

          {mode === "register" && (
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          )}

          <input
            type="email"
            placeholder="Authorized Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <div className="password-box">
            <input
              type={showPassword ? "text" : "password"}
              placeholder={mode === "login" ? "Access Key" : "Create Access Key"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={() => setFocus("password")}
            />
            <span onClick={() => setShowPassword(!showPassword)}>
              {showPassword ? "🙈" : "👁️"}
            </span>
          </div>

          {mode === "register" && (
            <div className="password-box">
              <input
                type="password"
                placeholder="Confirm Access Key"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
          )}

          <button
            disabled={mode === "register" && mismatch}
            onClick={handleAuth}
          >
            {mode === "login" ? "INITIATE LOGIN" : "INITIATE REGISTRATION"}
          </button>
        </div>
      </div>
    </div>
  );
}
