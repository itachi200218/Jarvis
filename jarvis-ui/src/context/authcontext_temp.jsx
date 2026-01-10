import { createContext, useContext, useEffect, useState } from "react";
import { getMyProfile } from "../api/profileApi";

const AuthContext = createContext(null);

// ==============================
// 🔐 AUTH PROVIDER
// ==============================
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ==============================
  // 🔄 REFRESH USER FROM TOKEN
  // ==============================
  const refreshUser = async () => {
    const token = sessionStorage.getItem("jarvis_token");

    // ❌ NO TOKEN → LOGGED OUT
    if (!token) {
      setUser(null);
      return;
    }

    try {
      const profile = await getMyProfile();

      setUser({
        ...profile,
        role: "user", // 🔥 FORCE USER ROLE (your rule)
      });
    } catch (err) {
      // Even if API fails → still logged in
      setUser({
        name: "User",
        role: "user",
      });
    }
  };

  // ==============================
  // 🚪 LOGOUT (CRITICAL FIX)
  // ==============================
  const logout = () => {
    // 🔥 REMOVE TOKEN
    sessionStorage.removeItem("jarvis_token");

    // 🔥 CLEAR ANY USER-SCOPED DATA
    sessionStorage.removeItem("active_chat_id");

    // 🔥 FORCE FULL USER RESET
    setUser(null);
  };

  // ==============================
  // 🔁 INIT ON APP LOAD
  // ==============================
  useEffect(() => {
    const init = async () => {
      try {
        await refreshUser();
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  // ==============================
  // 🔁 REACT TO TOKEN CHANGE (SAME TAB FIX)
  // ==============================
  useEffect(() => {
    const originalSetItem = sessionStorage.setItem;
    const originalRemoveItem = sessionStorage.removeItem;

    sessionStorage.setItem = function (key, value) {
      originalSetItem.apply(this, arguments);
      if (key === "jarvis_token") {
        refreshUser();
      }
    };

    sessionStorage.removeItem = function (key) {
      originalRemoveItem.apply(this, arguments);
      if (key === "jarvis_token") {
        setUser(null);
      }
    };

    return () => {
      sessionStorage.setItem = originalSetItem;
      sessionStorage.removeItem = originalRemoveItem;
    };
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        loading,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ==============================
// 🧠 AUTH HOOK
// ==============================
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}
