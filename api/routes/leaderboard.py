from fastapi import APIRouter, Query
from database import get_connection

router = APIRouter()


@router.get("/leaderboard")
def leaderboard(per_page: int = Query(10, ge=1, le=100)):
    """Top songs by play count — queries PostgreSQL directly (Module 4 replaces with Sorted Set)."""
    # TODO: Module 4 — replace with ZREVRANGE top-songs 0 {per_page-1} WITHSCORES
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT s.id, s.title, s.artist_id, a.name as artist_name,
                  s.genre, s.play_count
           FROM songs s JOIN artists a ON s.artist_id = a.id
           ORDER BY s.play_count DESC
           LIMIT %s""",
        (per_page,),
    )
    cols = [d[0] for d in cur.description]
    data = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return {"data": data}
