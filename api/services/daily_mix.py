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
    """Return the daily mix songs for a user.

    TODO: Module 1 — check Redis cache first: GET daily-mix:{user_id}
    TODO: Module 1 — after computing, cache: SET daily-mix:{user_id} <json> EX <ttl_in_seconds>
    """
    # check if daily mix already exists in Redis
    # cached_daily_mix = r.get(f"daily-mix:{user_id}")
    # if yes, return cached value directly. Tip: use `json.loads(cached_daily_mix)` to decode JSON

    daily_mix = generate_daily_mix(user_id)  # slow!

    # save songs to Redis. Tip: use `json.dumps(daily_mix)` to encode as JSON

    return daily_mix
