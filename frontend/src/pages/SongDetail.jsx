import { useParams } from "react-router-dom";
import { Link } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch } from "../api";
import Section from "../components/Section";
import PlayButton from "../components/PlayButton";
import SimilarSongs from "../components/SimilarSongs";

export default function SongDetail({ username }) {
  const { id } = useParams();
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch(`/songs/${id}`),
    [id],
  );

  const song = data;

  return (
    <div style={{ padding: "20px 0" }}>
      <Section
        title="Song Info"
        loading={loading}
        error={error}
        elapsed={elapsed}
        onRefresh={refresh}
      >
        {song && (
          <div>
            <h2 style={{ fontSize: "2rem", marginBottom: 8 }}>{song.title}</h2>
            <p>
              <Link to={`/artists/${song.artist_id}`}>{song.artist_name}</Link>
              <span style={{ color: "#b3b3b3", marginLeft: 12 }}>
                {song.genre}
              </span>
            </p>
            <p style={{ color: "#b3b3b3", marginTop: 4 }}>
              {Math.floor(song.duration_seconds / 60)}:
              {(song.duration_seconds % 60).toString().padStart(2, "0")}
            </p>
            <div
              style={{
                marginTop: 16,
                display: "flex",
                alignItems: "center",
                gap: 16,
              }}
            >
              <PlayButton songId={id} onPlayed={refresh} />
              <span style={{ fontSize: "1.1rem" }}>
                {song.play_count.toLocaleString()} plays
              </span>
            </div>
          </div>
        )}
      </Section>
      <SimilarSongs songId={id} />
    </div>
  );
}
