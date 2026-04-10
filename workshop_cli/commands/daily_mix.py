"""Call the daily-mix endpoint."""

from workshop_cli.utils import api_call, derive_user_id


def cmd_daily_mix(args):
    user_id = derive_user_id(args.user)
    print(f"GET /daily-mix (user: {args.user}, id: {user_id[:12]}...)")
    data, elapsed = api_call("/daily-mix", user_id=user_id)
    print(f"⏱ {elapsed:.2f} s\n")
    for i, song in enumerate(data.get("songs", [])[:5], 1):
        print(f"  {i}. {song['title']} — {song['artist_name']}")
    total = len(data.get("songs", []))
    if total > 5:
        print(f"  ...\n  ({total} songs total)")
