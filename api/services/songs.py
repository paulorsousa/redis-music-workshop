"""
Module 2 — Atomic Counters
Module 3 — Sorted Sets (ZINCRBY replaces INCR + powers the leaderboard)

Business logic for song queries and play-count tracking.
"""

from database import get_connection
from redis_client import r


def play_song(song_id: str) -> int | None:
    """Increment play count and return the new count."""
    new_count = r.zincrby("top-songs", 1, song_id)  # O(log N)
    return new_count


def find_similar_songs(song_id: str, count: int) -> list[dict]:
    """Similar songs – Module 6: query VectorSet with VSIM

    TODO: Implement in the 'vectorsets' branch.
    """
    return []


def list_songs(artist_id: str | None, page: int, per_page: int) -> dict:
    """Return a paginated list of songs, optionally filtered by artist."""
    conn = get_connection()
    cur = conn.cursor()

    where = ""
    params: list = []
    if artist_id:
        where = "WHERE s.artist_id = %s"
        params.append(artist_id)

    # Count
    cur.execute(f"SELECT COUNT(*) FROM songs s {where}", params)
    total = cur.fetchone()[0]

    # Fetch page
    offset = (page - 1) * per_page
    cur.execute(
        f"""SELECT s.id, s.title, s.artist_id, a.name as artist_name,
                   s.genre, s.duration_seconds, s.play_count
            FROM songs s JOIN artists a ON s.artist_id = a.id
            {where}
            ORDER BY s.title
            LIMIT %s OFFSET %s""",
        params + [per_page, offset],
    )
    cols = [d[0] for d in cur.description]
    data = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()

    return {"total": total, "page": page, "per_page": per_page, "data": data}


def get_song(song_id: str) -> dict | None:
    """Return a single song by ID, or None if not found."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT s.id, s.title, s.artist_id, a.name as artist_name,
                  s.genre, s.duration_seconds, s.play_count
           FROM songs s JOIN artists a ON s.artist_id = a.id
           WHERE s.id = %s""",
        (song_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return None
    cols = [d[0] for d in cur.description]
    result = dict(zip(cols, row))

    # Get play count from Redis, fallback to PostgreSQL if missing
    redis_count = r.zscore("top-songs", song_id)
    if redis_count:
        result["play_count"] = int(redis_count)

    cur.close()
    conn.close()
    return result
