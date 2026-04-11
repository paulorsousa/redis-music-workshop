"""Shared helpers for service modules."""

from database import get_connection


def decode_redis(value) -> str:
    """Decode a Redis response value to str."""
    return value if isinstance(value, str) else value.decode()


_SONG_METADATA_QUERY = """SELECT s.id, s.title, s.artist_id, a.name as artist_name, s.genre
                          FROM songs s JOIN artists a ON s.artist_id = a.id"""

_SONG_METADATA_COLS = ["id", "title", "artist_id", "artist_name", "genre"]


def enrich_with_metadata(songs: list[dict]) -> list[dict]:
    """Add title, artist and genre info from PostgreSQL to a list of song dicts.

    Unlike fetch_songs_by_ids, this mutates the incoming dicts (preserving extra
    keys like ``score``) instead of creating new ones.
    """
    ids = [s["id"] for s in songs]
    if not ids:
        return songs

    lookup = {d["id"]: d for d in fetch_songs_by_ids(ids)}
    for s in songs:
        meta = lookup.get(s["id"])
        if meta:
            s["title"] = meta["title"]
            s["artist_id"] = meta["artist_id"]
            s["artist_name"] = meta["artist_name"]
            s["genre"] = meta["genre"]

    return songs


def fetch_songs_by_ids(song_ids: list[str]) -> list[dict]:
    """Fetch song metadata from PostgreSQL for the given IDs, preserving order."""
    if not song_ids:
        return []
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"{_SONG_METADATA_QUERY} WHERE s.id = ANY(%s)", (song_ids,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    rows.sort(key=lambda row: song_ids.index(row[0]))
    return [dict(zip(_SONG_METADATA_COLS, row)) for row in rows]


def fetch_songs_excluding(exclude_ids: list[str], limit: int) -> list[dict]:
    """Fetch additional songs from PostgreSQL, excluding the given IDs."""
    if limit <= 0:
        return []
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"{_SONG_METADATA_QUERY} WHERE s.id <> ALL(%s) ORDER BY s.id DESC LIMIT %s",
        (exclude_ids, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(zip(_SONG_METADATA_COLS, row)) for row in rows]
