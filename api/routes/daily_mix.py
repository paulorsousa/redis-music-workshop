import time
import random
from fastapi import APIRouter, Request, HTTPException
from database import get_connection

router = APIRouter()


def _generate_daily_mix(user_id: str) -> list[dict]:
    """Generate a personalised 50-song mix. Intentionally slow (Module 1)."""
    # Simulate expensive computation
    time.sleep(5)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT s.id, s.title, s.artist_id, a.name as artist_name,
                  s.genre, s.duration_seconds
           FROM songs s JOIN artists a ON s.artist_id = a.id"""
    )
    cols = [d[0] for d in cur.description]
    all_songs = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()

    # Deterministic shuffle based on user_id for consistency
    rng = random.Random(user_id)
    rng.shuffle(all_songs)
    return all_songs[:50]


@router.get("/daily-mix")
def daily_mix(request: Request):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-ID header required")

    # TODO: Module 1 — check Redis cache first: GET daily-mix:{user_id}
    # TODO: Module 1 — after computing, cache: SET daily-mix:{user_id} <json> EX 86400

    songs = _generate_daily_mix(user_id)
    return {"user_id": user_id, "songs": songs}
