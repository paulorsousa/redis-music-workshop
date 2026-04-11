"""Print the leaderboard."""

from workshop_cli.utils import api_call


def cmd_top_songs(args):
    data, elapsed = api_call("/leaderboard", params={"per_page": str(args.limit)})
    songs = data.get("data", [])
    print(f"\nTop {args.limit} Songs")
    print("─" * 60)
    print(f" {'#':>3}  {'ID':<12}{'Song':<24}{'Artist':<20}{'Plays':>6}")
    for i, s in enumerate(songs, 1):
        print(
            f" {i:>3}. {s['id']:<12}{s['title'][:22]:<24}{s.get('artist_name','')[:18]:<20}{s.get('play_count',0):>6}"
        )
    print(f"⏱ {elapsed*1000:.0f} ms")
