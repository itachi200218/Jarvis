import { useState } from "react";
import JarvisApp from "./pages/JarvisApp";
import Login from "./pages/Login";

function App() {
  const [showLogin, setShowLogin] = useState(false);

  return (
    <>
      {showLogin ? (
        <Login onClose={() => setShowLogin(false)} />
      ) : (
        <JarvisApp openLogin={() => setShowLogin(true)} />
      )}
    </>
  );
}

export default App;
