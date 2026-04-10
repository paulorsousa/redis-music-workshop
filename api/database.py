import os
import csv
import psycopg2
from psycopg2.extras import execute_values

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://music:music@localhost:5432/music"
)


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            genre TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            artist_id TEXT NOT NULL REFERENCES artists(id),
            genre TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            play_count INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def seed_db():
    """Load CSV data into PostgreSQL, replacing existing data."""
    conn = get_connection()
    cur = conn.cursor()

    # Clear existing data
    cur.execute("DELETE FROM songs;")
    cur.execute("DELETE FROM artists;")

    # Load artists
    artists_count = 0
    with open("/data/artists.csv") as f:
        reader = csv.DictReader(f)
        rows = [(r["id"], r["name"], r["genre"]) for r in reader]
        if rows:
            execute_values(cur, "INSERT INTO artists (id, name, genre) VALUES %s", rows)
            artists_count = len(rows)

    # Load songs
    songs_count = 0
    with open("/data/songs.csv") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["id"],
                r["title"],
                r["artist_id"],
                r["genre"],
                int(r["duration_seconds"]),
            )
            for r in reader
        ]
        if rows:
            execute_values(
                cur,
                "INSERT INTO songs (id, title, artist_id, genre, duration_seconds) VALUES %s",
                rows,
            )
            songs_count = len(rows)

    conn.commit()
    cur.close()
    conn.close()
    return artists_count, songs_count
