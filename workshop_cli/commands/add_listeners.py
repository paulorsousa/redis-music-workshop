"""Add random listeners to an artist."""

import time
from concurrent.futures import ThreadPoolExecutor

from workshop_cli.utils import ProgressTracker, api_call, derive_user_id


def cmd_add_listeners(args):
    artist_id = args.artist
    count = args.count
    print(f"\nAdding {count} listeners to {artist_id}...")
    progress = ProgressTracker(count, label="Listeners")
    start = time.time()

    def add_one(i):
        username = f"listener-{i:06d}"
        uid = derive_user_id(username)
        try:
            api_call(f"/artists/{artist_id}/listeners", method="POST", user_id=uid)
            progress.advance()
        except Exception:
            progress.advance(error=True)

    with ThreadPoolExecutor(max_workers=20) as pool:
        list(pool.map(add_one, range(count)))

    progress.finish()
    elapsed = time.time() - start
    data, _ = api_call(f"/artists/{artist_id}")
    print(f"⏱ {elapsed:.2f} s")
    print(f"Monthly listeners: {data.get('monthly_listeners', '?')}")
