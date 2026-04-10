from fastapi import APIRouter, HTTPException, Query, Request
from services import artists as artists_service

router = APIRouter()


@router.get("/artists")
def list_artists(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    return artists_service.list_artists(page, per_page)


@router.get("/artists/{artist_id}")
def get_artist(artist_id: str):
    artist = artists_service.get_artist(artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.post("/artists/{artist_id}/listeners")
def add_listener(artist_id: str, request: Request):
    """Track a listener (Module 4)."""
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-ID header required")

    if not artists_service.artist_exists(artist_id):
        raise HTTPException(status_code=404, detail="Artist not found")

    artists_service.add_listener(artist_id, user_id)
    return {"status": "ok"}
