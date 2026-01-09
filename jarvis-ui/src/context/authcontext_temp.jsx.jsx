import { createContext, useContext, useEffect, useState } from "react";
import { getMyProfile } from "../api/profileApi";

const AuthContext = createContext(null);

// ==============================
// 🔐 AUTH PROVIDER
// ==============================
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔄 Refresh user based on TOKEN (NOT DB ROLE)
  const refreshUser = async () => {
    const token = sessionStorage.getItem("jarvis_token");

    // ❌ No token → GUEST
    if (!token) {
      setUser(null);
      return;
    }

    // ✅ Token exists → USER
    try {
      const profile = await getMyProfile();

      setUser({
        ...profile,
        role: "user", // 🔥 FORCE USER ROLE (your rule)
      });
    } catch (err) {
      // Even if profile API fails, token = logged in
      setUser({
        name: "User",
        role: "user",
      });
    }
  };

  // 🚪 LOGOUT
  const logout = () => {
    sessionStorage.removeItem("jarvis_token");
    setUser(null);
  };

  // 🔁 INIT ON APP LOAD
  useEffect(() => {
    async function init() {
      try {
        await refreshUser();
      } finally {
        setLoading(false);
      }
    }
    init();
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
