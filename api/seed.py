"""Seed script — run with: python -m seed"""

from database import init_db, seed_db

if __name__ == "__main__":
    init_db()
    artists, songs = seed_db()
    print(f"{artists} artists, {songs} songs loaded")
