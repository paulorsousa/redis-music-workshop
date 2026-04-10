import { useState } from "react";
import { Link } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch, deriveUserId } from "../api";
import Section from "./Section";

const PREVIEW_COUNT = 5;

export default function DailyMix({ username }) {
  const userId = deriveUserId(username);
  const { loading, data, error, elapsed, refresh } = useSection(
    (signal) => apiFetch("/daily-mix", { userId, signal }),
    [userId],
  );

  const [expanded, setExpanded] = useState(false);
  const songs = data?.songs || [];
  const visible = expanded ? songs : songs.slice(0, PREVIEW_COUNT);

  return (
    <Section
      title="Daily Mix"
      loading={loading}
      error={error}
      elapsed={elapsed}
      onRefresh={refresh}
    >
      <ul className="list-none">
        {visible.map((song, i) => (
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
      {songs.length > PREVIEW_COUNT && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="w-full py-2 text-sm text-muted hover:text-foreground transition-colors cursor-pointer"
        >
          {expanded ? "Show less" : `See all ${songs.length} songs`}
        </button>
      )}
    </Section>
  );
}
