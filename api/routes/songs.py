from fastapi import APIRouter, HTTPException, Query
from services import songs as songs_service

router = APIRouter()


@router.get("/songs")
def list_songs(
    artist_id: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    return songs_service.list_songs(artist_id, page, per_page)


@router.get("/songs/{song_id}")
def get_song(song_id: str):
    result = songs_service.get_song(song_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return result


@router.post("/songs/{song_id}/play")
def play_song(song_id: str):
    """Increment play count — delegates to service (Module 2)."""
    new_count = songs_service.play_song(song_id)
    if new_count is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return {"play_count": new_count}


@router.get("/songs/{song_id}/similar")
def similar_songs(song_id: str, count: int = Query(5, ge=1, le=50)):
    """Similar songs (Module 6)."""
    return songs_service.find_similar_songs(song_id, count)
