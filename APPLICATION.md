# Application Specification

> Base React frontend and Python REST API that students receive before the workshop.

The application is a **music catalogue** — functional but intentionally broken in specific ways that each workshop module fixes with Redis.

---

## Data model (PostgreSQL)

### `artists`

| Column  | Type      | Notes           |
| ------- | --------- | --------------- |
| `id`    | `TEXT` PK | e.g. `artist-1` |
| `name`  | `TEXT`    |                 |
| `genre` | `TEXT`    |                 |

### `songs`

| Column             | Type                | Notes                                                                |
| ------------------ | ------------------- | -------------------------------------------------------------------- |
| `id`               | `TEXT` PK           | e.g. `song-1`                                                        |
| `title`            | `TEXT`              |                                                                      |
| `artist_id`        | `TEXT` FK → artists |                                                                      |
| `genre`            | `TEXT`              |                                                                      |
| `duration_seconds` | `INTEGER`           |                                                                      |
| `play_count`       | `INTEGER`           | Default `0`. Incremented via the broken read-modify-write (Module 2) |

---

## Seed data

Two CSV files in `data/`:

### `data/artists.csv`

| Column  | Example    |
| ------- | ---------- |
| `id`    | `artist-1` |
| `name`  | `Queen`    |
| `genre` | `Rock`     |

### `data/songs.csv`

| Column             | Example             |
| ------------------ | ------------------- |
| `id`               | `song-1`            |
| `title`            | `Bohemian Rhapsody` |
| `artist_id`        | `artist-1`          |
| `genre`            | `Rock`              |
| `duration_seconds` | `354`               |

~20 artists and ~500 songs spanning 5–6 genres.

Both files are loaded into PostgreSQL by `./workshop reset` (and automatically when DB is empty). The API reads from PostgreSQL at runtime — the CSVs are only used for seeding and for computing embeddings (Module 6).

Song embeddings for Module 6 are **computed by the API** from the CSV data when triggered via `POST /admin/load-embeddings`. The API container has `sentence-transformers` installed. No pre-computed embeddings file is shipped.

---

## REST API (Python / FastAPI)

Base URL: `http://localhost:8000`

The user ID is a 36-char UUID sent in the `X-User-ID` header. The frontend derives it from the username and includes it in every request.

All collection endpoints (e.g. `/songs`, `/artists`) must be **paginated** using `?page=1&per_page=20` query parameters. Responses include `total`, `page`, `per_page`, and `data` fields.

### Songs

| Method | Path                  | Description                                    | Module |
| ------ | --------------------- | ---------------------------------------------- | ------ |
| `GET`  | `/songs`              | List all songs (supports `?artist_id=` filter) | —      |
| `GET`  | `/songs/{id}`         | Song detail (includes `play_count`)            | —      |
| `POST` | `/songs/{id}/play`    | Increment play count                           | 2, 4   |
| `GET`  | `/songs/{id}/similar` | Similar songs _(empty until Module 6)_         | 6      |

### Artists

| Method | Path                      | Description                                           | Module |
| ------ | ------------------------- | ----------------------------------------------------- | ------ |
| `GET`  | `/artists`                | List all artists (includes `monthly_listeners` count) | —      |
| `GET`  | `/artists/{id}`           | Artist detail (includes `monthly_listeners` count)    | —      |
| `POST` | `/artists/{id}/listeners` | Record a listener (user ID from `X-User-ID` header)   | 3, 5   |

### Daily mix

| Method | Path         | Description                                                        | Module |
| ------ | ------------ | ------------------------------------------------------------------ | ------ |
| `GET`  | `/daily-mix` | Generate a personalised 50-song mix (user from `X-User-ID` header) | 1      |

### Leaderboard

| Method | Path           | Description             | Module |
| ------ | -------------- | ----------------------- | ------ |
| `GET`  | `/leaderboard` | Top songs by play count | 4      |

### Admin

| Method | Path                     | Description                                                         | Module |
| ------ | ------------------------ | ------------------------------------------------------------------- | ------ |
| `POST` | `/admin/load-embeddings` | Compute song embeddings from CSV data and load into Redis VectorSet | 6      |

#### `POST /admin/load-embeddings` — details

1. Read `data/songs.csv` and `data/artists.csv`, join on `artist_id` to resolve artist names.
2. For each song, build a text string: `"{title} {artist_name} {genre}"`.
3. Load sentence-transformer model (`all-MiniLM-L6-v2`, 384 dimensions).
4. Compute embeddings for all songs in a single batch.
5. For each song, store the embedding: `VADD song-vectors FP32 {song_id} VALUES {v1} {v2} ...`.
6. Return a JSON summary: `{ "loaded": 500, "dimensions": 384 }`.

---

## React frontend

Base URL: `http://localhost:3000`

A simple single-page app styled with Tailwind CSS— just enough to look like a music platform so students have visual feedback when things improve.

### Loading behaviour

Each section of a page fetches its data **independently and concurrently**. Every section has its own loading state:

- **Loading** — a skeleton placeholder while the API call is in flight.
- **Loaded** — the data is displayed, with a small **response-time badge** (e.g. `⏱ 4.8 s` or `⏱ 12 ms`) showing how long the API call took, and a **refresh button** (🔄) to re-fetch that section independently.
- **Error** — an inline error message if the call fails, with the same refresh button to retry.

This makes performance problems (and their fixes) immediately visible: a cached daily mix drops from `⏱ 5.0 s` to `⏱ 8 ms` right in front of the student.

### Pages

| Route           | Page          | Description                                                 | Shows effect of |
| --------------- | ------------- | ----------------------------------------------------------- | --------------- |
| `/`             | Home          | Daily mix, artist grid, "Top Songs" leaderboard sidebar     | Modules 1, 4    |
| `/artists/{id}` | Artist detail | Artist info, song list, monthly listener count              | Modules 3, 5    |
| `/songs/{id}`   | Song detail   | Song info, play button, play count, "Similar Songs" section | Modules 2, 6    |

### Sections per page

Each page is composed of sections that load concurrently:

**Home (`/`)**
| Section | API call | Notes |
|---------|----------|-------|
| Daily mix | `GET /daily-mix` | ~5 s uncached → ~10 ms cached (Module 1) |
| Artist grid | `GET /artists` | Includes monthly listener count (Modules 3, 5) |
| Leaderboard sidebar | `GET /leaderboard` | Slow until Module 4 |

**Artist detail (`/artists/{id}`)**
| Section | API call | Notes |
|---------|----------|-------|
| Artist info | `GET /artists/{id}` | Includes monthly listener count (Modules 3, 5) |
| Song list | `GET /songs?artist_id={id}` | |

**Song detail (`/songs/{id}`)**
| Section | API call | Notes |
|---------|----------|-------|
| Song info + play count | `GET /songs/{id}` | Play count affected by Module 2 |
| Similar songs | `GET /songs/{id}/similar` | Hyped teaser until Module 6 |

### Key interactions

- **Play button** (song detail) — calls `POST /songs/{id}/play`, then refreshes the displayed count. Students see the count go wrong under concurrency (Module 2) and then get fixed. The response-time badge updates after each call.
- **Daily Mix section** (home) — shows a skeleton while loading and shows the elapsed time when loaded. Makes the 5 s delay (and the caching fix) very visible. Loads concurrently with the other home sections.
- **Leaderboard sidebar** (home) — fetches `GET /leaderboard`. Initially slow; after Module 4 it updates in real time.
- **Monthly listeners** (artist detail) — displays the count from `GET /artists/{id}`. Changes meaning across Modules 3 → 5.
- **Similar Songs** (song detail) — initially shows "No similar songs available". Lights up after Module 6.

### State / user identity

There is no authentication. User identity is derived from a **username** displayed in the header:

- The username defaults to `user-1` and is stored in `localStorage`.
- It can be edited directly in the header (e.g. an inline text field) so students can switch users quickly.
- The **user ID** is a deterministic 36-char UUID generated from the username (e.g. `uuid5` / name-based UUID). This ensures the same username always produces the same ID, which matters for caching (Module 1) and listener tracking (Modules 3, 5).

---

## Project structure

```
redis-music-workshop/
├── docker-compose.yml
├── workshop                    # CLI utility (Python / argparse)
├── WORKSHOP.md
├── APPLICATION.md
│
├── api/                        # Python / FastAPI
│   ├── main.py                 # App entry point, CORS, lifespan
│   ├── database.py             # PostgreSQL connection (psycopg / SQLAlchemy), CSV seed loader
│   ├── redis_client.py         # Redis connection (redis-py)
│   ├── core/                   # Core code (DO NOT EDIT during the workshop)
│   │   └── daily_mix_engine.py  # Slow recommendation algorithm (time.sleep)
│   ├── routes/                 # HTTP layer (request parsing, error responses)
│   │   ├── songs.py            # /songs, /songs/{id}, /songs/{id}/play, /songs/{id}/similar
│   │   ├── artists.py          # /artists, /artists/{id}, /artists/{id}/listeners
│   │   ├── daily_mix.py        # /daily-mix
│   │   ├── leaderboard.py      # /leaderboard
│   │   └── admin.py            # /admin/load-embeddings
│   └── services/               # Business logic (what students edit during the workshop)
│       ├── songs.py            # Modules 2, 4, 6 — play counts, sorted sets, vectors
│       ├── artists.py          # Modules 3, 5 — listener tracking (sets, HLL)
│       ├── daily_mix.py        # Module 1 — caching & TTL
│       ├── leaderboard.py      # Module 4 — sorted set reads
│       └── admin.py            # Module 6 — embedding loading
│
├── frontend/                   # React (Vite)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── ArtistDetail.jsx
│   │   │   └── SongDetail.jsx
│   │   └── components/
│   │       ├── DailyMix.jsx
│   │       ├── Leaderboard.jsx
│   │       ├── SongList.jsx
│   │       ├── PlayButton.jsx
│   │       ├── Section.jsx
│   │       └── SimilarSongs.jsx
│   └── ...
│
└── data/
    ├── artists.csv             # Artist catalogue
    └── songs.csv               # Song catalogue (also used for embeddings in Module 6)
```

---

## Intentionally broken behaviours

These are the problems students will observe and fix during the workshop:

| #   | Endpoint                       | What's broken                                           | Simulated how                                            |
| --- | ------------------------------ | ------------------------------------------------------- | -------------------------------------------------------- |
| 1   | `GET /daily-mix`               | Always recomputes from scratch — no caching             | `time.sleep(5)` in the generation function               |
| 2   | `POST /songs/{id}/play`        | Non-atomic counter — loses increments under concurrency | Read-modify-write (`SELECT` then `UPDATE`) without locks |
| 3   | `POST /artists/{id}/listeners` | Tracks listeners in a Redis List with O(N) dedup scan   | `LRANGE` + linear membership check before `RPUSH`        |
| 4   | `GET /leaderboard`             | Queries PostgreSQL directly — slow and stale under load | `SELECT ... ORDER BY play_count DESC`                    |
| 5   | (same as 3)                    | Set from Module 3 uses too much memory at scale         | N/A — observed via `./workshop get-redis-memory-usage`   |
| 6   | `GET /songs/{id}/similar`      | Not implemented                                         | Returns `null` (frontend shows a teaser)                 |
