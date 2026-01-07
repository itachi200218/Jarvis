// src/api/authApi.js

const BASE_URL = "http://127.0.0.1:8000/auth";

// 🔐 REGISTER
export async function registerUser(payload) {
  try {
    const response = await fetch(`${BASE_URL}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Registration failed");
    }

    return data;
  } catch (error) {
    console.error("Register API Error:", error);
    throw error;
  }
}

// 🔐 LOGIN
export async function loginUser(payload) {
  try {
    const response = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Login failed");
    }

    return data;
  } catch (error) {
    console.error("Login API Error:", error);
    throw error;
  }
}
