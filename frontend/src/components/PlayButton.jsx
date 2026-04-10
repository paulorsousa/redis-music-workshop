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

  const badgeColor =
    elapsed != null
      ? elapsed > 1000
        ? "bg-[#5c1a1a] text-danger"
        : "bg-[#1a3d1a] text-[#69db7c]"
      : "";

  return (
    <span>
      <button
        className="bg-accent text-black border-none px-6 py-2 rounded-full font-bold cursor-pointer text-base hover:bg-accent-hover hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={handlePlay}
        disabled={playing}
      >
        {playing ? "⏳" : "▶ Play"}
      </button>
      {elapsed != null && (
        <span
          className={`inline-block px-2 py-0.5 rounded-xl text-xs ml-2 ${badgeColor}`}
        >
          ⏱ {formatTime(elapsed)}
        </span>
      )}
    </span>
  );
}
