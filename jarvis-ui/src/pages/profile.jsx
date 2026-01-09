import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getMyProfile,
  updateProfileName,
  changePassword,
  uploadProfileAvatar
} from "../api/profileApi";
import { useAuth } from "../context/authcontext_temp.jsx";
import "../App.css";

export default function Profile() {
  const navigate = useNavigate();

  // 🔥 ADDED user (NOT changing anything else)
  const { user, logout, refreshUser } = useAuth();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [editMode, setEditMode] = useState(false);
  const [passwordMode, setPasswordMode] = useState(false);

  const [newName, setNewName] = useState("");
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const [savingProfile, setSavingProfile] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  // 🖼 Avatar states
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);

  // =========================
  // LOAD PROFILE
  // =========================
  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await getMyProfile();
        setProfile(data);
        setNewName(data.name);
      } catch (err) {
        setError(err.message || "Not authenticated");
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  // =========================
  // UPDATE NAME
  // =========================
  const handleProfileUpdate = async () => {
    if (savingProfile) return;

    try {
      setSavingProfile(true);
      await updateProfileName(newName);
      setProfile({ ...profile, name: newName });
      setEditMode(false);
    } catch (err) {
      alert(err.message);
    } finally {
      setSavingProfile(false);
    }
  };

  // =========================
  // CHANGE PASSWORD
  // =========================
  const handlePasswordChange = async () => {
    if (changingPassword) return;

    if (!oldPassword || !newPassword) {
      alert("Fill all fields");
      return;
    }

    try {
      setChangingPassword(true);
      await changePassword(oldPassword, newPassword);
      alert("Password updated 🔐");
      setOldPassword("");
      setNewPassword("");
      setPasswordMode(false);
    } catch (err) {
      alert(err.message);
    } finally {
      setChangingPassword(false);
    }
  };

  // =========================
  // UPLOAD AVATAR
  // =========================
  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Instant preview
    setAvatarPreview(URL.createObjectURL(file));

    try {
      setUploadingAvatar(true);
      await uploadProfileAvatar(file);

      // Refresh user from backend
      await refreshUser();
      const updated = await getMyProfile();
      setProfile(updated);
    } catch (err) {
      alert(err.message);
    } finally {
      setUploadingAvatar(false);
    }
  };

  // =========================
  // UI STATES
  // =========================
  if (loading) {
    return <div className="status">🔄 Loading profile…</div>;
  }

  if (error) {
    return (
      <div className="status error">
        🔒 {error}
        <br />
        <button onClick={() => navigate("/")}>Return to Jarvis</button>
      </div>
    );
  }

  // =========================
  // UI
  // =========================
  return (
    <div className="hud profile-hud">
      <div className="hud-frame profile-frame">

        <div className="hud-header">
          <div className="hud-title">USER PROFILE</div>
          <div className="hud-subtitle">Identity & Security Module</div>
        </div>

        <div className="profile-card">

          {/* 🖼 PROFILE AVATAR */}
          <div className="profile-avatar-section">
            <img
              src={
                avatarPreview ||
                profile.avatar ||
                "/default-avatar.png"
              }
              alt="Profile"
              className="profile-avatar"
            />

            <label className="avatar-upload-btn">
              {uploadingAvatar ? "UPLOADING..." : "CHANGE PHOTO"}
              <input
                type="file"
                accept="image/png, image/jpeg"
                hidden
                onChange={handleAvatarUpload}
              />
            </label>
          </div>

          <p><strong>Name:</strong> {profile.name}</p>
          <p><strong>Email:</strong> {profile.email}</p>

          {/* 🔥 FIXED ROLE DISPLAY (LOGIN STATE, NOT DB) */}
          <p>
            <strong>Role:</strong>{" "}
            {user ? user.role.toUpperCase() : "GUEST"}
          </p>

          <p>
            <strong>Secure Mode:</strong>{" "}
            {profile.secure_mode ? "ENABLED 🔐" : "DISABLED"}
          </p>
        </div>

        <div className="profile-actions">
          <button onClick={() => setEditMode(true)}>EDIT PROFILE</button>
          <button onClick={() => setPasswordMode(true)}>CHANGE PASSWORD</button>

          <button
            className="danger"
            onClick={() => {
              logout();
              navigate("/");
            }}
          >
            LOGOUT
          </button>
        </div>

        {editMode && (
          <div className="profile-modal">
            <h3>Edit Name</h3>
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
            <button onClick={handleProfileUpdate}>
              {savingProfile ? "SAVING..." : "SAVE"}
            </button>
            <button onClick={() => setEditMode(false)}>CANCEL</button>
          </div>
        )}

        {passwordMode && (
          <div className="profile-modal">
            <h3>Change Password</h3>
            <input
              type="password"
              placeholder="Current password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
            />
            <input
              type="password"
              placeholder="New password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            <button onClick={handlePasswordChange}>
              {changingPassword ? "UPDATING..." : "UPDATE"}
            </button>
            <button onClick={() => setPasswordMode(false)}>CANCEL</button>
          </div>
        )}

        <div className="profile-footer">
          <button onClick={() => navigate("/")}>⬅ RETURN TO JARVIS</button>
        </div>

      </div>
    </div>
  );
}
