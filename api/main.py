from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, seed_db
from routes import songs, artists, daily_mix, leaderboard, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB and seed if empty
    init_db()
    from database import get_connection

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM songs")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    if count == 0:
        a, s = seed_db()
        print(f"Seeded: {a} artists, {s} songs")
    yield


app = FastAPI(title="Redis Music Workshop API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(songs.router)
app.include_router(artists.router)
app.include_router(daily_mix.router)
app.include_router(leaderboard.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}
