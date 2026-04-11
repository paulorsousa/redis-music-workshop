"""
Module 3 — Sorted Sets (read side)

Business logic for the top-songs leaderboard.
"""

from redis_client import r
from services._helpers import fetch_songs_by_ids, fetch_songs_excluding


def get_leaderboard(per_page: int) -> list:
    """Top songs by play count — queries PostgreSQL directly (Module 3 replaces with Sorted Set)."""

    leaderboard = r.zrevrange("top-songs", 0, per_page - 1, withscores=True)
    song_ids = [song_id for song_id, _ in leaderboard]

    data = fetch_songs_by_ids(song_ids)

    if len(data) < per_page:
        data += fetch_songs_excluding(song_ids, per_page - len(data))

    # Override play_count with the score from the sorted set
    scores = {song_id: int(score) for song_id, score in leaderboard}
    for song in data:
        song["play_count"] = scores.get(song["id"], 0)

    return data
