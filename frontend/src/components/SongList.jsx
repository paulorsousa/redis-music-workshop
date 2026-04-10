import { Link } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch } from "../api";
import Section from "./Section";

export default function SongList({ artistId, title = "Songs" }) {
  const { loading, data, error, elapsed, refresh } = useSection(
    (signal) =>
      apiFetch("/songs", {
        params: { artist_id: artistId, per_page: 100 },
        signal,
      }),
    [artistId],
  );

  const songs = data?.data || [];

  return (
    <Section
      title={title}
      loading={loading}
      error={error}
      elapsed={elapsed}
      onRefresh={refresh}
    >
      <ul className="list-none">
        {songs.map((song) => (
          <li
            key={song.id}
            className="px-3 py-2 border-b border-border flex justify-between items-center hover:bg-[#1a1a1a]"
          >
            <Link to={`/songs/${song.id}`}>{song.title}</Link>
            <span className="text-muted text-sm">
              {Math.floor(song.duration_seconds / 60)}:
              {(song.duration_seconds % 60).toString().padStart(2, "0")}
            </span>
          </li>
        ))}
      </ul>
    </Section>
  );
}
