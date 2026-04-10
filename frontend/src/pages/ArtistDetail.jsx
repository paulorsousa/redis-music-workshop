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
    <div style={{ padding: "20px 0" }}>
      <Section
        title="Artist Info"
        loading={loading}
        error={error}
        elapsed={elapsed}
        onRefresh={refresh}
      >
        {artist && (
          <div>
            <h2 style={{ fontSize: "2rem", marginBottom: 8 }}>{artist.name}</h2>
            <p style={{ color: "#b3b3b3" }}>Genre: {artist.genre}</p>
            <p style={{ color: "#b3b3b3", marginTop: 4 }}>
              {artist.monthly_listeners.toLocaleString()} monthly listeners
            </p>
          </div>
        )}
      </Section>
      <SongList artistId={id} title={`Songs by ${artist?.name || "..."}`} />
    </div>
  );
}
