"""List songs (paginated)."""

from workshop_cli.utils import api_call


def cmd_list_songs(args):
    params = {"page": str(args.page), "per_page": str(args.per_page)}
    data, elapsed = api_call("/songs", params=params)

    songs = data.get("data", [])
    total = data.get("total", 0)
    page = data.get("page", args.page)
    per_page = data.get("per_page", args.per_page)
    total_pages = (total + per_page - 1) // per_page

    print(f"\nSongs (page {page}/{total_pages}, {total} total)")
    print("─" * 60)
    print(f" {'#':>3}  {'ID':<10} {'Title':<30} {'Artist':<20} {'Genre'}")
    for i, s in enumerate(songs, (page - 1) * per_page + 1):
        print(
            f" {i:>3}. {s['id']:<10} {s['title'][:28]:<30} {s['artist_name'][:18]:<20} {s.get('genre', '')}"
        )
    print(f"⏱ {elapsed * 1000:.0f} ms")
