from fastapi import APIRouter, Request, HTTPException
from services.daily_mix import get_daily_mix

router = APIRouter()


@router.get("/daily-mix")
def daily_mix(request: Request):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-ID header required")

    return {"user_id": user_id, "songs": get_daily_mix(user_id)}
