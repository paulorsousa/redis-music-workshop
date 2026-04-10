import { Link } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch } from "../api";
import Section from "./Section";

export default function SimilarSongs({ songId }) {
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch(`/songs/${songId}/similar`, { params: { count: 5 } }),
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
        <p style={{ color: "#b3b3b3", fontStyle: "italic" }}>
          🚀 No similar songs available yet — complete Module 6 to enable this
          feature!
        </p>
      ) : (
        <ul className="song-list">
          {similar.map((song, i) => (
            <li key={song.id || i}>
              <span>
                <span style={{ color: "#b3b3b3", marginRight: 8 }}>
                  {i + 1}.
                </span>
                <Link to={`/songs/${song.id}`}>{song.title}</Link>
                <span style={{ color: "#b3b3b3" }}> — {song.artist_name}</span>
              </span>
              {song.score != null && (
                <span style={{ color: "#1db954", fontSize: "0.85rem" }}>
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
