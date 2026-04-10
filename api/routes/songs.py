import time
from fastapi import APIRouter, Query, Request
from database import get_connection

router = APIRouter()


@router.get("/songs")
def list_songs(
    artist_id: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
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


@router.get("/songs/{song_id}")
def get_song(song_id: str):
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
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Song not found")
    cols = [d[0] for d in cur.description]
    result = dict(zip(cols, row))
    cur.close()
    conn.close()
    return result


@router.post("/songs/{song_id}/play")
def play_song(song_id: str):
    """Increment play count — intentionally broken with race condition (Module 2)."""
    conn = get_connection()
    cur = conn.cursor()

    # Step 1: SELECT current count
    cur.execute("SELECT play_count FROM songs WHERE id = %s", (song_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Song not found")

    new_count = row[0] + 1

    # Step 2: UPDATE with incremented value (non-atomic — loses updates under concurrency)
    cur.execute("UPDATE songs SET play_count = %s WHERE id = %s", (new_count, song_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"play_count": new_count}


@router.get("/songs/{song_id}/similar")
def similar_songs(song_id: str, count: int = Query(5, ge=1, le=50)):
    """Similar songs — returns empty until Module 6 is implemented."""
    # TODO: Module 6 — query VectorSet with VSIM
    return {"song_id": song_id, "similar": []}
