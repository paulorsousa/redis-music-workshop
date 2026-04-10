import { useParams } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch } from "../api";
import Section from "../components/Section";
import SongList from "../components/SongList";

export default function ArtistDetail() {
  const { id } = useParams();
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch(`/artists/${id}`),
    [id],
  );

  const artist = data;

  return (
    <div className="py-5">
      <Section
        title="Artist Info"
        loading={loading}
        error={error}
        elapsed={elapsed}
        onRefresh={refresh}
      >
        {artist && (
          <div>
            <h2 className="text-3xl mb-2">{artist.name}</h2>
            <p className="text-muted">Genre: {artist.genre}</p>
            <p className="text-muted mt-1">
              {artist.monthly_listeners.toLocaleString()} monthly listeners
            </p>
          </div>
        )}
      </Section>
      <SongList artistId={id} title={`Songs by ${artist?.name || "..."}`} />
    </div>
  );
}
