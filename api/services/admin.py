"""
Module 6 — VectorSets (loading side)

Business logic for computing song embeddings and loading them
into a Redis VectorSet.
"""

import csv
from redis_client import r


def load_embeddings() -> dict:
    """Compute song embeddings and load into Redis VectorSet (Module 6)."""
    # Read songs and artists
    artists = {}
    with open("/data/artists.csv") as f:
        for row in csv.DictReader(f):
            artists[row["id"]] = row["name"]

    songs = []
    with open("/data/songs.csv") as f:
        for row in csv.DictReader(f):
            songs.append(row)

    # Build text for each song
    texts = []
    song_ids = []
    for song in songs:
        artist_name = artists.get(song["artist_id"], "Unknown")
        text = f"{song['title']} {song['genre']} {song['description']} {artist_name}"
        texts.append(text)
        song_ids.append(song["id"])

    # Compute embeddings
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, show_progress_bar=False)

    dimensions = embeddings.shape[1]

    # Load into Redis VectorSet
    for song_id, embedding in zip(song_ids, embeddings):
        values = embedding.tolist()
        # VADD key VALUES num v1 v2 ... element
        r.execute_command(
            "VADD",
            "song-vectors",
            "VALUES",
            len(values),
            *[str(v) for v in values],
            song_id,
        )

    return {"loaded": len(song_ids), "dimensions": int(dimensions)}
