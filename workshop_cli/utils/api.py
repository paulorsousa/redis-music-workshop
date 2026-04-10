"""HTTP helpers for talking to the workshop API."""

import json
import os
import time
from urllib.request import Request, urlopen

API_URL = os.environ.get("API_URL", "http://localhost:8000")


def api_call(path, method="GET", user_id=None, params=None):
    """Issue an HTTP request to the API and return (parsed_json, elapsed_seconds)."""
    url = f"{API_URL}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    req = Request(url, method=method)
    if user_id:
        req.add_header("X-User-ID", user_id)
    if method == "POST":
        req.add_header("Content-Length", "0")
    start = time.time()
    with urlopen(req) as resp:
        data = json.loads(resp.read())
    elapsed = time.time() - start
    return data, elapsed
