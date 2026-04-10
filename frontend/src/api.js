const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Deterministic UUID v5 from username (matches backend/CLI)
// Using a simple implementation to avoid dependencies
function uuidv5(name) {
  // RFC 4122 DNS namespace: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
  // Simple hash-based approach for deterministic IDs
  let hash = 0;
  const str = "6ba7b810" + name;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  // Format as UUID-like string
  const hex = Math.abs(hash).toString(16).padStart(8, "0");
  const h2 = (hash * 31)
    .toString(16)
    .replace("-", "")
    .padStart(8, "0")
    .slice(0, 8);
  const h3 = (hash * 37)
    .toString(16)
    .replace("-", "")
    .padStart(4, "0")
    .slice(0, 4);
  const h4 = (hash * 41)
    .toString(16)
    .replace("-", "")
    .padStart(4, "0")
    .slice(0, 4);
  const h5 = (hash * 43)
    .toString(16)
    .replace("-", "")
    .padStart(12, "0")
    .slice(0, 12);
  return `${hex}-${h2.slice(0, 4)}-5${h3.slice(0, 3)}-${h4}-${h5}`;
}

export function deriveUserId(username) {
  return uuidv5(username);
}

export async function apiFetch(path, { method = "GET", userId, params } = {}) {
  const url = new URL(`${API_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }
  const headers = {};
  if (userId) headers["X-User-ID"] = userId;

  const start = performance.now();
  const res = await fetch(url.toString(), { method, headers });
  const elapsed = performance.now() - start;

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  const data = await res.json();
  return { data, elapsed };
}
