"""
Module 1 — Caching & TTL

Workshop task: add Redis caching with SET/GET and a TTL so the
expensive computation only runs once per user per day.

The generation algorithm lives in core/daily_mix_engine.py — treat it as
a slow black box; the fix is to cache its output here.
"""

from core.daily_mix_engine import generate_daily_mix


def get_daily_mix(user_id: str) -> dict:
    """Return the daily mix for a user.

    TODO: Module 1 — check Redis cache first: GET daily-mix:{user_id}
    TODO: Module 1 — after computing, cache: SET daily-mix:{user_id} <json> EX 86400
    """
    songs = generate_daily_mix(user_id)
    return {"user_id": user_id, "songs": songs}
