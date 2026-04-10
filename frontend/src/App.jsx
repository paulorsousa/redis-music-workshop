import { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import ArtistDetail from './pages/ArtistDetail';
import SongDetail from './pages/SongDetail';

export default function App() {
  const [username, setUsername] = useState(
    () => localStorage.getItem('username') || 'user-1'
  );

  const updateUsername = (val) => {
    setUsername(val);
    localStorage.setItem('username', val);
  };

  return (
    <BrowserRouter>
      <header>
        <h1><Link to="/" style={{ color: 'inherit', textDecoration: 'none' }}>🎵 Redis Music Workshop</Link></h1>
        <div>
          <label style={{ color: '#b3b3b3', fontSize: '0.85rem', marginRight: 8 }}>User:</label>
          <input
            className="user-input"
            value={username}
            onChange={e => updateUsername(e.target.value)}
          />
        </div>
      </header>
      <div className="container">
        <Routes>
          <Route path="/" element={<Home username={username} />} />
          <Route path="/artists/:id" element={<ArtistDetail />} />
          <Route path="/songs/:id" element={<SongDetail username={username} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
