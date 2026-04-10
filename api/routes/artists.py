from fastapi import APIRouter, Query, Request, HTTPException
from database import get_connection
from redis_client import r

router = APIRouter()


def _get_listener_count(artist_id: str) -> int:
    """Get monthly listener count using Redis List (intentionally slow — Module 3)."""
    from datetime import datetime
    month = datetime.now().strftime("%Y-%m")
    key = f"monthly-listeners:{artist_id}:{month}"
    return r.llen(key)


@router.get("/artists")
def list_artists(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
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


@router.get("/artists/{artist_id}")
def get_artist(artist_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, genre FROM artists WHERE id = %s", (artist_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Artist not found")
    cols = [d[0] for d in cur.description]
    artist = dict(zip(cols, row))
    cur.close()
    conn.close()
    artist["monthly_listeners"] = _get_listener_count(artist_id)
    return artist


@router.post("/artists/{artist_id}/listeners")
def add_listener(artist_id: str, request: Request):
    """Track a listener — intentionally uses Redis List with O(N) dedup (Module 3)."""
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-ID header required")

    # Verify artist exists
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM artists WHERE id = %s", (artist_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Artist not found")
    cur.close()
    conn.close()

    from datetime import datetime
    month = datetime.now().strftime("%Y-%m")
    key = f"monthly-listeners:{artist_id}:{month}"

    # O(N) dedup check on a List — intentionally slow (Module 3)
    existing = r.lrange(key, 0, -1)
    if user_id not in existing:
        r.rpush(key, user_id)

    return {"status": "ok"}
