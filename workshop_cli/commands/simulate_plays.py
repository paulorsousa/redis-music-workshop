"""Fire play events for a song (sequential or concurrent)."""

import time
from concurrent.futures import ThreadPoolExecutor

from workshop_cli.utils import FAIL, OK, ProgressTracker, api_call


def cmd_simulate_plays(args):
    song_id = args.song
    count = args.count
    label = "concurrent" if args.concurrent else "sequential"

    # Read current play count before firing
    before_data, _ = api_call(f"/songs/{song_id}")
    before = before_data["play_count"]

    print(f"\nFiring {count} {label} plays for {song_id} (current: {before})...")
    progress = ProgressTracker(count, label="Plays")

    def fire_play(_):
        try:
            api_call(f"/songs/{song_id}/play", method="POST")
            progress.advance()
        except Exception:
            progress.advance(error=True)

    start = time.time()
    if args.concurrent:
        with ThreadPoolExecutor(max_workers=50) as pool:
            list(pool.map(fire_play, range(count)))
    else:
        for i in range(count):
            fire_play(i)
    elapsed = time.time() - start
    progress.finish()

    data, _ = api_call(f"/songs/{song_id}")
    after = data["play_count"]
    gained = after - before
    print(f"⏱ {elapsed:.2f} s")
    print(f"Expected: {before} + {count} = {before + count}")
    if gained == count:
        print(f"Actual:   {after} {OK}")
    else:
        print(f"Actual:   {after} {FAIL} ({count - gained} lost)")
