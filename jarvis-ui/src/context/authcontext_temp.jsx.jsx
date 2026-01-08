import { createContext, useContext, useEffect, useState } from "react";
import { getMyProfile } from "../api/profileApi";

const AuthContext = createContext(null);

// ==============================
// 🔐 AUTH PROVIDER
// ==============================
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 🔄 Load user from token
  const refreshUser = async () => {
    try {
      const profile = await getMyProfile();
      setUser(profile);
    } catch {
      setUser(null);
    }
  };

  // 🚪 LOGOUT (THIS WAS MISSING)
  const logout = () => {
    sessionStorage.removeItem("jarvis_token");
    setUser(null);
  };

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
        logout, // ✅ NOW AVAILABLE
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
