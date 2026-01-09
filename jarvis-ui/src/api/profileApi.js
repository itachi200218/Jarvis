// src/api/profileApi.js
const BASE_URL = "http://127.0.0.1:8000";

// 🔐 TOKEN (PER TAB)
function getToken() {
  const token = sessionStorage.getItem("jarvis_token");
  if (!token) {
    throw new Error("Not authenticated");
  }
  return token;
}

// ==============================
// 👤 GET PROFILE
// ==============================
export async function getMyProfile() {
  const response = await fetch(`${BASE_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to load profile");
  }

  return data;
}

// ==============================
// ✏️ UPDATE PROFILE NAME
// ==============================
export async function updateProfileName(name) {
  const response = await fetch(`${BASE_URL}/auth/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ name }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to update name");
  }

  return data;
}

// ==============================
// 🔑 CHANGE PASSWORD
// ==============================
export async function changePassword(oldPassword, newPassword) {
  const response = await fetch(`${BASE_URL}/auth/change-password`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to change password");
  }

  return data;
}

// ==============================
// 🖼 UPLOAD PROFILE AVATAR (NEW)
// ==============================
export async function uploadProfileAvatar(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/auth/upload-avatar`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${getToken()}`,
      // ❌ DO NOT set Content-Type manually
    },
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to upload avatar");
  }

  return data; // { message, avatar }
}
