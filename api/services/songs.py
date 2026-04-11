"""
Module 2 — Atomic Counters
Module 3 — Sorted Sets (ZINCRBY replaces INCR + powers the leaderboard)
Module 6 — VectorSets  (read side: VSIM for similar songs)

Business logic for song queries and play-count tracking.
"""

from database import get_connection
from redis_client import r


def play_song(song_id: str) -> int | None:
    """Increment play count and return the new count.

    Returns None if the song does not exist.

    NOTE: Intentionally broken with race condition (Module 2 fixes it with INCR).
    NOTE: After Module 2, the leaderboard breaks (Module 3 fixes it with ZINCRBY).

    TODO: Module 2 — replace SELECT/+1/UPDATE with INCR play-count:song:{song_id}
    TODO: Module 3 — replace INCR with ZINCRBY top-songs 1 {song_id} (i.e., sorted set replaces the counter)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Step 1: SELECT current count
    cur.execute("SELECT play_count FROM songs WHERE id = %s", (song_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return None

    new_count = row[0] + 1

    # Step 2: UPDATE with incremented value (non-atomic — loses updates under concurrency)
    cur.execute("UPDATE songs SET play_count = %s WHERE id = %s", (new_count, song_id))
    conn.commit()
    cur.close()
    conn.close()
    return new_count


def find_similar_songs(song_id: str, count: int) -> dict:
    """Similar songs — returns empty until Module 6 is implemented.

    TODO: Module 6 — query VectorSet with VSIM song-vectors ELE {song_id} COUNT {count}
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
    # TODO: Module 3 — replace with r.zscore("top-songs", song_id)
    redis_count = r.get(f"play-count:song:{song_id}")
    if redis_count:
        result["play_count"] = int(redis_count)

    cur.close()
    conn.close()
    return result
