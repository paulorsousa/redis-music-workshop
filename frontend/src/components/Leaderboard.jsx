import { Link } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch } from "../api";
import Section from "./Section";

export default function Leaderboard() {
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch("/leaderboard", { params: { per_page: 10 } }),
    [],
  );

  const songs = data?.data || [];

  return (
    <Section
      title="🏆 Top Songs"
      loading={loading}
      error={error}
      elapsed={elapsed}
      onRefresh={refresh}
    >
      {songs.map((song, i) => (
        <div
          className="flex items-center py-2 border-b border-border"
          key={song.id}
        >
          <span className="w-[30px] font-bold text-muted">{i + 1}.</span>
          <div className="flex-1">
            <Link to={`/songs/${song.id}`}>{song.title}</Link>
            <div className="text-xs text-muted">{song.artist_name}</div>
          </div>
          <span className="text-muted text-sm">{song.play_count} plays</span>
        </div>
      ))}
      {songs.length === 0 && <p className="text-muted">No plays yet</p>}
    </Section>
  );
}
