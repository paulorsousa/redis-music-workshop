import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import ArtistDetail from "./pages/ArtistDetail";
import SongDetail from "./pages/SongDetail";

function useTheme() {
  const [dark, setDark] = useState(() =>
    document.documentElement.classList.contains("dark"),
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return [dark, () => setDark((d) => !d)];
}

export default function App() {
  const [dark, toggleTheme] = useTheme();

  const [username, setUsername] = useState(
    () => localStorage.getItem("username") || "user-1",
  );

  const updateUsername = (val) => {
    setUsername(val);
    localStorage.setItem("username", val);
  };

  return (
    <BrowserRouter>
      <header className="bg-surface border-b border-border px-5 py-3 flex items-center justify-between sticky top-0 z-50">
        <h1 className="text-lg text-accent">
          <Link to="/" className="text-inherit no-underline hover:no-underline">
            🎵 Redis Music Workshop
          </Link>
        </h1>
        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            className="bg-card border border-input-border text-foreground px-2 py-1 rounded text-sm cursor-pointer hover:bg-surface-hover"
            title={dark ? "Switch to light mode" : "Switch to dark mode"}
          >
            {dark ? "☀️" : "🌙"}
          </button>
          <div>
            <label className="text-muted text-sm mr-2">User:</label>
            <input
              className="bg-card border border-input-border text-foreground px-2 py-1 rounded text-sm"
              value={username}
              onChange={(e) => updateUsername(e.target.value)}
            />
          </div>
        </div>
      </header>
      <div className="max-w-[1200px] mx-auto px-5">
        <Routes>
          <Route path="/" element={<Home username={username} />} />
          <Route path="/artists/:id" element={<ArtistDetail />} />
          <Route
            path="/songs/:id"
            element={<SongDetail username={username} />}
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
