import { Link } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch } from "../api";
import Section from "./Section";

export default function SimilarSongs({ songId }) {
  const { loading, data, error, elapsed, refresh } = useSection(
    (signal) =>
      apiFetch(`/songs/${songId}/similar`, { params: { count: 5 }, signal }),
    [songId],
  );

  const similar = data?.similar || [];

  return (
    <Section
      title="Similar Songs"
      loading={loading}
      error={error}
      elapsed={elapsed}
      onRefresh={refresh}
    >
      {similar.length === 0 ? (
        <p className="text-muted italic">
          🚀 No similar songs available yet — complete Module 6 to enable this
          feature!
        </p>
      ) : (
        <ul className="list-none">
          {similar.map((song, i) => (
            <li
              key={song.id || i}
              className="px-3 py-2 border-b border-border flex justify-between items-center hover:bg-list-hover"
            >
              <span>
                <span className="text-muted mr-2">{i + 1}.</span>
                <Link to={`/songs/${song.id}`}>{song.title}</Link>
                <span className="text-muted"> — {song.artist_name}</span>
              </span>
              {song.score != null && (
                <span className="text-accent text-sm">
                  ({song.score.toFixed(2)})
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </Section>
  );
}
