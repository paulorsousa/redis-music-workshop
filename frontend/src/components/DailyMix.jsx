import { Link } from 'react-router-dom';
import { useSection } from '../hooks';
import { apiFetch, deriveUserId } from '../api';
import Section from './Section';

export default function DailyMix({ username }) {
  const userId = deriveUserId(username);
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch('/daily-mix', { userId }),
    [userId]
  );

  const songs = data?.songs || [];

  return (
    <Section title="Daily Mix" loading={loading} error={error} elapsed={elapsed} onRefresh={refresh}>
      <ul className="song-list">
        {songs.map((song, i) => (
          <li key={song.id}>
            <span>
              <span style={{ color: '#b3b3b3', marginRight: 8 }}>{i + 1}.</span>
              <Link to={`/songs/${song.id}`}>{song.title}</Link>
              <span style={{ color: '#b3b3b3' }}> — {song.artist_name}</span>
            </span>
          </li>
        ))}
      </ul>
    </Section>
  );
}
