"""Argument parsing and command dispatch for the workshop CLI."""

import argparse
import sys

from workshop_cli.commands.add_listeners import cmd_add_listeners
from workshop_cli.commands.daily_mix import cmd_daily_mix
from workshop_cli.commands.destroy import cmd_destroy
from workshop_cli.commands.list_artists import cmd_list_artists
from workshop_cli.commands.list_songs import cmd_list_songs
from workshop_cli.commands.load_embeddings import cmd_load_embeddings
from workshop_cli.commands.redis_memory import cmd_get_redis_memory
from workshop_cli.commands.reset import cmd_reset
from workshop_cli.commands.similar_songs import cmd_similar_songs
from workshop_cli.commands.simulate_plays import cmd_simulate_plays
from workshop_cli.commands.top_songs import cmd_top_songs


def main():
    parser = argparse.ArgumentParser(
        prog="workshop",
        description="Redis Music Workshop CLI",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("reset", help="Reset PostgreSQL and Redis, reload seed data")
    p = sub.add_parser("destroy", help="Destroy all containers, networks, and volumes")
    p.add_argument(
        "--rmi",
        choices=["local", "all"],
        nargs="?",
        const="local",
        default="local",
        help="Remove images: 'local' (built by compose, default) or 'all'",
    )
    p.add_argument(
        "--prune-build-cache",
        action="store_true",
        help="Also prune Docker build cache",
    )
    sub.add_parser("help", help="Show this help message")

    p = sub.add_parser("list-songs", help="List songs (paginated)")
    p.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    p.add_argument(
        "--per-page", type=int, default=20, help="Items per page (default: 20)"
    )

    p = sub.add_parser("list-artists", help="List artists (paginated)")
    p.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    p.add_argument(
        "--per-page", type=int, default=20, help="Items per page (default: 20)"
    )

    p = sub.add_parser("daily-mix", help="Call the daily-mix endpoint")
    p.add_argument("--user", default="user-1", help="Username (default: user-1)")

    p = sub.add_parser("simulate-plays", help="Fire play events")
    p.add_argument("--song", required=True, help="Song ID (e.g. song-1)")
    p.add_argument(
        "--count", type=int, default=100, help="Number of plays (default: 100)"
    )
    p.add_argument("--concurrent", action="store_true", help="Fire concurrently")

    p = sub.add_parser("add-listeners", help="Add random listeners to an artist")
    p.add_argument("--artist", required=True, help="Artist ID (e.g. artist-1)")
    p.add_argument(
        "--count", type=int, default=1000, help="Number of listeners (default: 1000)"
    )
    p.add_argument(
        "--range",
        type=int,
        default=1_000_000,
        help="Size of the random listener pool (default: 1M)",
    )

    p = sub.add_parser("top-songs", help="Print the leaderboard")
    p.add_argument(
        "--limit", type=int, default=10, help="Number of songs (default: 10)"
    )

    sub.add_parser(
        "get-redis-memory-usage", help="Print Redis memory usage by key pattern"
    )

    sub.add_parser("load-embeddings", help="Compute and load song embeddings")

    p = sub.add_parser("similar-songs", help="Find similar songs via VectorSet")
    p.add_argument("--song", required=True, help="Song ID (e.g. song-42)")
    p.add_argument(
        "--count", type=int, default=5, help="Number of results (default: 5)"
    )

    args = parser.parse_args()

    cmds = {
        "help": lambda a: parser.print_help(),
        "destroy": cmd_destroy,
        "reset": cmd_reset,
        "list-songs": cmd_list_songs,
        "list-artists": cmd_list_artists,
        "daily-mix": cmd_daily_mix,
        "simulate-plays": cmd_simulate_plays,
        "add-listeners": cmd_add_listeners,
        "top-songs": cmd_top_songs,
        "get-redis-memory-usage": cmd_get_redis_memory,
        "load-embeddings": cmd_load_embeddings,
        "similar-songs": cmd_similar_songs,
    }

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds[args.command](args)
