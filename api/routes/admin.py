import csv
from fastapi import APIRouter
from redis_client import r

router = APIRouter()


@router.post("/admin/load-embeddings")
def load_embeddings():
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
        text = f"{song['title']} {artist_name} {song['genre']}"
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
        # VADD song-vectors FP32 <element> VALUES v1 v2 ...
        r.execute_command(
            "VADD", "song-vectors", "FP32", song_id,
            "VALUES", *[str(v) for v in values]
        )

    return {"loaded": len(song_ids), "dimensions": int(dimensions)}
