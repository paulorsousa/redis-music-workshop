import { useState } from "react";
import { apiFetch } from "../api";
import { formatTime } from "../hooks";

export default function PlayButton({ songId, onPlayed }) {
  const [playing, setPlaying] = useState(false);
  const [elapsed, setElapsed] = useState(null);

  const handlePlay = async () => {
    setPlaying(true);
    try {
      const { elapsed } = await apiFetch(`/songs/${songId}/play`, {
        method: "POST",
      });
      setElapsed(elapsed);
      if (onPlayed) onPlayed();
    } catch (e) {
      console.error(e);
    } finally {
      setPlaying(false);
    }
  };

  return (
    <span>
      <button className="play-btn" onClick={handlePlay} disabled={playing}>
        {playing ? "⏳" : "▶ Play"}
      </button>
      {elapsed != null && (
        <span className={`badge ${elapsed > 1000 ? "slow" : "fast"}`}>
          ⏱ {formatTime(elapsed)}
        </span>
      )}
    </span>
  );
}
