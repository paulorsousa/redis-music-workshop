import { Link } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch, deriveUserId } from "../api";
import Section from "./Section";

export default function DailyMix({ username }) {
  const userId = deriveUserId(username);
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch("/daily-mix", { userId }),
    [userId],
  );

  const songs = data?.songs || [];

  return (
    <Section
      title="Daily Mix"
      loading={loading}
      error={error}
      elapsed={elapsed}
      onRefresh={refresh}
    >
      <ul className="list-none">
        {songs.map((song, i) => (
          <li
            key={song.id}
            className="px-3 py-2 border-b border-border flex justify-between items-center hover:bg-[#1a1a1a]"
          >
            <span>
              <span className="text-muted mr-2">{i + 1}.</span>
              <Link to={`/songs/${song.id}`}>{song.title}</Link>
              <span className="text-muted"> — {song.artist_name}</span>
            </span>
          </li>
        ))}
      </ul>
    </Section>
  );
}
