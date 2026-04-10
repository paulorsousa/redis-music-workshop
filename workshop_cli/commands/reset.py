"""Reset PostgreSQL and Redis, reload seed data."""

import subprocess
import time

from workshop_cli.utils.spinner import run_with_spinner


def cmd_reset(args):
    run_with_spinner(
        "Flushing redis...",
        subprocess.run,
        ["docker", "compose", "exec", "redis", "redis-cli", "FLUSHDB"],
        capture_output=True,
    )

    result = run_with_spinner(
        "Seeding database...",
        subprocess.run,
        [
            "docker",
            "compose",
            "exec",
            "api",
            "python",
            "-c",
            "from database import init_db, seed_db; init_db(); a,s = seed_db(); print(f'{a} artists, {s} songs loaded')",
        ],
        capture_output=True,
        text=True,
    )
    print(f"  {result.stdout.strip()}")
