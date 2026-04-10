"""Find similar songs via VectorSet."""

from workshop_cli.utils import api_call


def cmd_similar_songs(args):
    data, elapsed = api_call(
        f"/songs/{args.song}/similar", params={"count": str(args.count)}
    )
    similar = data.get("similar", [])
    if not similar:
        print(
            f"No similar songs found for {args.song}. Have you run 'workshop load-embeddings'?"
        )
        return
    song_data, _ = api_call(f"/songs/{args.song}")
    print(f'\nSongs similar to "{song_data["title"]}" ({args.song})')
    print("─" * 50)
    for i, s in enumerate(similar, 1):
        score = f"({s.get('score', 0):.2f})" if "score" in s else ""
        print(f"  {i}. {s.get('title', '?')} — {s.get('artist_name', '?')}  {score}")
    print(f"⏱ {elapsed*1000:.0f} ms")
