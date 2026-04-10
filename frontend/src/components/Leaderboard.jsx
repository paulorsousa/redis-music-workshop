import { Link } from 'react-router-dom';
import { useSection } from '../hooks';
import { apiFetch } from '../api';
import Section from './Section';

export default function Leaderboard() {
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch('/leaderboard', { params: { per_page: 10 } }),
    []
  );

  const songs = data?.data || [];

  return (
    <Section title="🏆 Top Songs" loading={loading} error={error} elapsed={elapsed} onRefresh={refresh}>
      {songs.map((song, i) => (
        <div className="leaderboard-item" key={song.id}>
          <span className="rank">{i + 1}.</span>
          <div style={{ flex: 1 }}>
            <Link to={`/songs/${song.id}`}>{song.title}</Link>
            <div style={{ fontSize: '0.8rem', color: '#b3b3b3' }}>{song.artist_name}</div>
          </div>
          <span style={{ color: '#b3b3b3', fontSize: '0.85rem' }}>{song.play_count} plays</span>
        </div>
      ))}
      {songs.length === 0 && <p style={{ color: '#b3b3b3' }}>No plays yet</p>}
    </Section>
  );
}
