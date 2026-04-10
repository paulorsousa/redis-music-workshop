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
    (signal) => apiFetch(`/songs/${id}`, { signal }),
    [id],
  );

  const song = data;

  return (
    <div className="py-5">
      <Section
        title="Song Info"
        loading={loading}
        error={error}
        elapsed={elapsed}
        onRefresh={refresh}
      >
        {song && (
          <div>
            <h2 className="text-3xl mb-2">{song.title}</h2>
            <p>
              <Link to={`/artists/${song.artist_id}`}>{song.artist_name}</Link>
              <span className="text-muted ml-3">{song.genre}</span>
            </p>
            <p className="text-muted mt-1">
              {Math.floor(song.duration_seconds / 60)}:
              {(song.duration_seconds % 60).toString().padStart(2, "0")}
            </p>
            <div className="mt-4 flex items-center gap-4">
              <PlayButton songId={id} onPlayed={refresh} />
              <span className="text-lg">
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
