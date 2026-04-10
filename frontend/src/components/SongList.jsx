import { Link } from 'react-router-dom';
import { useSection } from '../hooks';
import { apiFetch } from '../api';
import Section from './Section';

export default function SongList({ artistId, title = 'Songs' }) {
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch('/songs', { params: { artist_id: artistId, per_page: 100 } }),
    [artistId]
  );

  const songs = data?.data || [];

  return (
    <Section title={title} loading={loading} error={error} elapsed={elapsed} onRefresh={refresh}>
      <ul className="song-list">
        {songs.map(song => (
          <li key={song.id}>
            <Link to={`/songs/${song.id}`}>{song.title}</Link>
            <span style={{ color: '#b3b3b3', fontSize: '0.85rem' }}>
              {Math.floor(song.duration_seconds / 60)}:{(song.duration_seconds % 60).toString().padStart(2, '0')}
            </span>
          </li>
        ))}
      </ul>
    </Section>
  );
}
