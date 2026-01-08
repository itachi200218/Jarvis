import { Routes, Route } from "react-router-dom";
import JarvisApp from "./pages/JarvisApp";
import Login from "./pages/Login";
import Profile from "./pages/profile";

function App() {
  return (
    <Routes>
      <Route path="/" element={<JarvisApp />} />
      <Route path="/auth" element={<Login />} />
      <Route path="/profile" element={<Profile />} />
    </Routes>
  );
}

export default App;
