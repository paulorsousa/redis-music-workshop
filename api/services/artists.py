"""
Module 3 — Sets
Module 5 — HyperLogLog

Business logic for artist queries and monthly-listener tracking.
"""

from datetime import datetime
from database import get_connection
from redis_client import r


def _get_listener_count(artist_id: str) -> int:
    """Get monthly listener count using Redis List (intentionally slow — Module 3)."""
    month = datetime.now().strftime("%Y-%m")
    key = f"monthly-listeners:{artist_id}:{month}"
    return r.llen(key)


def list_artists(page: int, per_page: int) -> dict:
    """Return a paginated list of artists with monthly listener counts."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM artists")
    total = cur.fetchone()[0]

    offset = (page - 1) * per_page
    cur.execute(
        "SELECT id, name, genre FROM artists ORDER BY name LIMIT %s OFFSET %s",
        (per_page, offset),
    )
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = []
    for row in rows:
        artist = dict(zip(cols, row))
        artist["monthly_listeners"] = _get_listener_count(artist["id"])
        data.append(artist)

    return {"total": total, "page": page, "per_page": per_page, "data": data}


def get_artist(artist_id: str) -> dict | None:
    """Return a single artist by ID, or None if not found."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, genre FROM artists WHERE id = %s", (artist_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return None
    cols = [d[0] for d in cur.description]
    artist = dict(zip(cols, row))
    cur.close()
    conn.close()
    artist["monthly_listeners"] = _get_listener_count(artist_id)
    return artist


def artist_exists(artist_id: str) -> bool:
    """Check whether an artist exists in the database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM artists WHERE id = %s", (artist_id,))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists


def add_listener(artist_id: str, user_id: str) -> None:
    """Track a listener — intentionally uses Redis List with O(N) dedup (Module 3).

    TODO: Module 3 — replace List + scan with SADD monthly-listeners:{artist_id}:{YYYY-MM} {user_id}
    TODO: Module 5 — replace SADD with PFADD hll-listeners:{artist_id}:{YYYY-MM} {user_id}
    """
    month = datetime.now().strftime("%Y-%m")
    key = f"monthly-listeners:{artist_id}:{month}"

    # O(N) dedup check on a List — intentionally slow (Module 3)
    existing = r.lrange(key, 0, -1)
    if user_id not in existing:
        r.rpush(key, user_id)
