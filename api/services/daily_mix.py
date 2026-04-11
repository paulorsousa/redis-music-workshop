"""
Module 1 — Caching & TTL

Workshop task: add Redis caching with SET/GET and a TTL so the
expensive computation only runs once per user per day.

The generation algorithm lives in core/daily_mix_engine.py — treat it as
a slow black box; the fix is to cache its output here.
"""

from core.daily_mix_engine import generate_daily_mix
import json
from redis_client import r


def get_daily_mix(user_id: str) -> list[dict]:
    """Return the daily mix songs for a user."""
    # check if daily mix already exists in Redis
    cached_daily_mix = r.get(f"daily-mix:{user_id}")

    if cached_daily_mix:
        # cache hit: returning cached value directly
        return json.loads(cached_daily_mix)

    # cache miss: generating daily mix
    daily_mix = generate_daily_mix(user_id)  # slow!

    # saving songs to Redis
    r.set(f"daily-mix:{user_id}", json.dumps(daily_mix), ex=86400)

    return daily_mix
