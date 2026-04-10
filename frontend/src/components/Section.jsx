import { formatTime } from "../hooks";

export default function Section({
  title,
  loading,
  error,
  elapsed,
  onRefresh,
  children,
}) {
  const badgeClass =
    elapsed != null ? (elapsed > 1000 ? "badge slow" : "badge fast") : "badge";

  return (
    <div className="section">
      <div className="section-header">
        <h2>{title}</h2>
        {elapsed != null && (
          <span className={badgeClass}>⏱ {formatTime(elapsed)}</span>
        )}
        {onRefresh && (
          <button className="refresh-btn" onClick={onRefresh} title="Refresh">
            🔄
          </button>
        )}
      </div>
      {loading && !error && (
        <div>
          <div className="skeleton" style={{ width: "80%" }} />
          <div className="skeleton" style={{ width: "60%" }} />
          <div className="skeleton" style={{ width: "70%" }} />
        </div>
      )}
      {error && (
        <div className="error-msg">
          ⚠️ {error}
          {onRefresh && (
            <button className="refresh-btn" onClick={onRefresh}>
              🔄 Retry
            </button>
          )}
        </div>
      )}
      {!loading && !error && children}
    </div>
  );
}
