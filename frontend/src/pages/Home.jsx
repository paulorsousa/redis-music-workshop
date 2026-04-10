import { Link } from "react-router-dom";
import { useSection } from "../hooks";
import { apiFetch } from "../api";
import DailyMix from "../components/DailyMix";
import Leaderboard from "../components/Leaderboard";
import Section from "../components/Section";

export default function Home({ username }) {
  const { loading, data, error, elapsed, refresh } = useSection(
    () => apiFetch("/artists", { params: { per_page: 20 } }),
    [],
  );

  const artists = data?.data || [];

  return (
    <div className="home-layout">
      <div>
        <DailyMix username={username} />
        <Section
          title="Artists"
          loading={loading}
          error={error}
          elapsed={elapsed}
          onRefresh={refresh}
        >
          <div className="grid">
            {artists.map((artist) => (
              <Link
                to={`/artists/${artist.id}`}
                key={artist.id}
                style={{ textDecoration: "none" }}
              >
                <div className="card">
                  <div style={{ fontWeight: "bold", marginBottom: 4 }}>
                    {artist.name}
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#b3b3b3" }}>
                    {artist.genre}
                  </div>
                  <div
                    style={{
                      fontSize: "0.8rem",
                      color: "#b3b3b3",
                      marginTop: 4,
                    }}
                  >
                    {artist.monthly_listeners.toLocaleString()} monthly
                    listeners
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </Section>
      </div>
      <aside>
        <Leaderboard />
      </aside>
    </div>
  );
}
