import { Routes, Route } from "react-router-dom";

import JarvisApp from "./pages/JarvisApp";
import Login from "./pages/Login";
import Profile from "./pages/profile";

import ChatPage from "./pages/ChatPage";
import ChatDetail from "./pages/ChatDetail";

function App() {
  return (
    <Routes>
      <Route path="/" element={<JarvisApp />} />
      <Route path="/auth" element={<Login />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route path="/chat/:chatId" element={<ChatDetail />} />
    </Routes>
  );
}

export default App;
