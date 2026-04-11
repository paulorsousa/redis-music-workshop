from fastapi import APIRouter, Query
from services.leaderboard import get_leaderboard

router = APIRouter()


@router.get("/leaderboard")
def leaderboard(per_page: int = Query(10, ge=1, le=100)):
    """Top songs by play count (Module 3)."""
    return {"data": get_leaderboard(per_page)}
