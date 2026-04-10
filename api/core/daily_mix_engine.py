"""
Daily-mix generation algorithm.

DO NOT OPTIMIZE THIS CODE.

This simulates an expensive recommendation engine. The time.sleep(5)
represents heavy computation — do NOT optimize this function.
The workshop fix is to cache its result in Redis (Module 1).
"""

import time
import random
from database import get_connection


def generate_daily_mix(user_id: str) -> list[dict]:
    """Generate a personalised 50-song mix. Intentionally slow (Module 1)."""

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

    # Our "algorithm" is just shuffling deterministically based on user_id and day of year
    time.sleep(5)  # But let's pretend it's expensive :D – DO NOT REMOVE THIS LINE
    rng = random.Random(user_id + str(time.localtime().tm_yday))
    rng.shuffle(all_songs)
    return all_songs[:50]
