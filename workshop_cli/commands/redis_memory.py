"""Print Redis memory usage by key pattern."""

import subprocess

from workshop_cli.utils import format_bytes


def cmd_get_redis_memory(args):
    print("\nRedis Memory Usage")
    print("─" * 50)
    patterns = [
        "daily-mix:*",
        "play-count:song:*",
        "monthly-listeners:*",
        "hll-listeners:*",
        "top-songs",
        "song-vectors",
    ]
    total_mem = 0
    total_patterns = len(patterns)
    print(f"  {'Key pattern':<25} {'Count':>6}  {'Memory':>10}")
    for idx, pattern in enumerate(patterns, 1):
        print(f"\r  Scanning {idx}/{total_patterns}: {pattern}...", end="", flush=True)
        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "redis",
                "redis-cli",
                "--scan",
                "--pattern",
                pattern,
            ],
            capture_output=True,
            text=True,
        )
        keys = [k.strip() for k in result.stdout.strip().split("\n") if k.strip()]
        count = len(keys)
        mem = 0
        for key in keys:
            r = subprocess.run(
                [
                    "docker",
                    "compose",
                    "exec",
                    "redis",
                    "redis-cli",
                    "MEMORY",
                    "USAGE",
                    key,
                ],
                capture_output=True,
                text=True,
            )
            try:
                mem += int(r.stdout.strip())
            except ValueError:
                pass
        total_mem += mem
        mem_str = format_bytes(mem) if count > 0 else "—"
        print(f"\r  {pattern:<25} {count:>6}  {mem_str:>10}")
    print("─" * 50)
    print(f"  {'Total':<25} {'':>6}  {format_bytes(total_mem):>10}")
