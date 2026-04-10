import { v5 as uuidv5 } from "uuid";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// RFC 4122 DNS namespace — same one used by Python's uuid.uuid5 and the CLI
const NAMESPACE = "6ba7b810-9dad-11d1-80b4-00c04fd430c8";

export function deriveUserId(username) {
  return uuidv5(username, NAMESPACE);
}

export async function apiFetch(
  path,
  { method = "GET", userId, params, signal } = {},
) {
  const url = new URL(`${API_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }
  const headers = {};
  if (userId) headers["X-User-ID"] = userId;

  const start = performance.now();
  const res = await fetch(url.toString(), { method, headers, signal });
  const elapsed = performance.now() - start;

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  const data = await res.json();
  return { data, elapsed };
}
