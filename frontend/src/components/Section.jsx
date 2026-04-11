import { formatTime } from "../hooks";

export default function Section({
  title,
  loading,
  error,
  elapsed,
  onRefresh,
  children,
}) {
  const badgeColor =
    elapsed != null
      ? elapsed > 1000
        ? "bg-badge-slow-bg text-badge-slow-text"
        : "bg-badge-fast-bg text-badge-fast-text"
      : "bg-card text-muted";

  return (
    <div className="bg-surface rounded-lg p-5 mb-5">
      <div className="flex items-center mb-3">
        <h2 className="text-[1.1rem]">{title}</h2>
        {elapsed != null && (
          <span
            className={`inline-block px-2 py-0.5 rounded-xl text-xs ml-2 ${badgeColor}`}
          >
            ⏱ {formatTime(elapsed)}
          </span>
        )}
        {onRefresh && (
          <button
            className="bg-transparent border-none cursor-pointer text-base px-1.5 py-0.5 rounded text-muted hover:enabled:bg-card disabled:opacity-40 disabled:cursor-not-allowed"
            onClick={onRefresh}
            title="Refresh"
            disabled={loading}
          >
            🔄
          </button>
        )}
      </div>
      {loading && !error && (
        <div>
          <div className="skeleton w-4/5" />
          <div className="skeleton w-3/5" />
          <div className="skeleton w-[70%]" />
        </div>
      )}
      {error && (
        <div className="text-danger p-3">
          ⚠️ {error}
          {onRefresh && (
            <button
              className="bg-transparent border-none cursor-pointer text-base px-1.5 py-0.5 rounded text-muted hover:enabled:bg-card disabled:opacity-40 disabled:cursor-not-allowed"
              onClick={onRefresh}
              disabled={loading}
            >
              🔄 Retry
            </button>
          )}
        </div>
      )}
      {!loading && !error && children}
    </div>
  );
}
