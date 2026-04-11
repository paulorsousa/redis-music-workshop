"""Shared helpers for service modules."""

from database import get_connection


def decode_redis(value) -> str:
    """Decode a Redis response value to str."""
    return value if isinstance(value, str) else value.decode()


def parse_vsim_results(results: list, exclude_id: str | None = None) -> list[dict]:
    """Parse alternating element/score pairs from a VSIM response."""
    parsed = []
    for i in range(0, len(results), 2):
        elem = decode_redis(results[i])
        score = float(decode_redis(results[i + 1]))
        if elem == exclude_id:
            continue
        parsed.append({"id": elem, "score": score})
    return parsed


def enrich_with_metadata(songs: list[dict]) -> list[dict]:
    """Add title, artist and genre info from PostgreSQL to a list of song dicts."""
    ids = [s["id"] for s in songs]
    if not ids:
        return songs

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT s.id, s.title, s.artist_id, a.name as artist_name, s.genre
            FROM songs s JOIN artists a ON s.artist_id = a.id
            WHERE s.id = ANY(%s)""",
        (ids,),
    )
    rows = {row[0]: row for row in cur.fetchall()}
    cur.close()
    conn.close()

    for s in songs:
        row = rows.get(s["id"])
        if row:
            s["title"] = row[1]
            s["artist_id"] = row[2]
            s["artist_name"] = row[3]
            s["genre"] = row[4]

    return songs
