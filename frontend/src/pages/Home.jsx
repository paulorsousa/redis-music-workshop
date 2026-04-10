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
    <div className="grid grid-cols-[1fr_300px] gap-5 py-5 max-md:grid-cols-1">
      <div>
        <DailyMix username={username} />
        <Section
          title="Artists"
          loading={loading}
          error={error}
          elapsed={elapsed}
          onRefresh={refresh}
        >
          <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-4">
            {artists.map((artist) => (
              <Link
                to={`/artists/${artist.id}`}
                key={artist.id}
                className="!no-underline"
              >
                <div className="bg-card rounded-lg p-4 cursor-pointer transition-colors hover:bg-surface-hover">
                  <div className="font-bold mb-1">{artist.name}</div>
                  <div className="text-xs text-muted">{artist.genre}</div>
                  <div className="text-xs text-muted mt-1">
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
