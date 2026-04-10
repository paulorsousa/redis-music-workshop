"""Print the leaderboard."""

from workshop_cli.utils import api_call


def cmd_top_songs(args):
    data, elapsed = api_call("/leaderboard", params={"per_page": str(args.limit)})
    songs = data.get("data", [])
    print(f"\nTop {args.limit} Songs")
    print("─" * 40)
    print(f" {'#':>3}  {'Song':<30} {'Plays':>6}")
    for i, s in enumerate(songs, 1):
        print(f" {i:>3}. {s['title'][:28]:<30} {s['play_count']:>6}")
    print(f"⏱ {elapsed*1000:.0f} ms")
