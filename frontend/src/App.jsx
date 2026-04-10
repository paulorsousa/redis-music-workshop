import { useState } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import ArtistDetail from "./pages/ArtistDetail";
import SongDetail from "./pages/SongDetail";

export default function App() {
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
        <div>
          <label className="text-muted text-sm mr-2">User:</label>
          <input
            className="bg-card border border-[#404040] text-gray-200 px-2 py-1 rounded text-sm"
            value={username}
            onChange={(e) => updateUsername(e.target.value)}
          />
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
