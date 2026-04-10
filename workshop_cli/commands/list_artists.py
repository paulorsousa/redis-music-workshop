"""List artists (paginated)."""

from workshop_cli.utils import api_call


def cmd_list_artists(args):
    params = {"page": str(args.page), "per_page": str(args.per_page)}
    data, elapsed = api_call("/artists", params=params)

    artists = data.get("data", [])
    total = data.get("total", 0)
    page = data.get("page", args.page)
    per_page = data.get("per_page", args.per_page)
    total_pages = (total + per_page - 1) // per_page

    print(f"\nArtists (page {page}/{total_pages}, {total} total)")
    print("─" * 45)
    print(f" {'#':>3}  {'ID':<12} {'Name':<25} {'Genre'}")
    for i, a in enumerate(artists, (page - 1) * per_page + 1):
        print(f" {i:>3}. {a['id']:<12} {a['name'][:23]:<25} {a.get('genre', '')}")
    print(f"⏱ {elapsed * 1000:.0f} ms")
