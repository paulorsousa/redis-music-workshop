# CLI Tool — Technical Specification

> Implementation details for the `workshop` CLI utility.

## Overview

The CLI is a single Python script (`workshop`) at the repo root. It uses **only the Python 3 standard library** — no third-party packages required.

- HTTP calls to the REST API use `urllib.request`.
- Concurrent requests use `concurrent.futures.ThreadPoolExecutor`.
- Argument parsing uses `argparse`.
- Docker operations use `subprocess` to call `docker compose`.

```
./workshop <command> [options]
```

---

## Configuration

All connection details are read from environment variables with sensible defaults for the Docker Compose setup:

| Variable  | Default                 | Used by                        |
| --------- | ----------------------- | ------------------------------ |
| `API_URL` | `http://localhost:8000` | All commands that call the API |

---

## User ID derivation

Commands that accept `--user` receive a **username** (e.g. `user-1`) and derive a deterministic 36-char UUID using `uuid5` with a fixed namespace:

```python
import uuid

NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # RFC 4122 DNS namespace

def derive_user_id(username: str) -> str:
    return str(uuid.uuid5(NAMESPACE, username))
```

The derived UUID is sent as the `X-User-ID` header on API calls, matching the frontend behaviour.

---

## Commands

### `./workshop reset`

Resets Redis and PostgreSQL, then reloads seed data. No arguments.

**Behaviour:**

1. `docker compose exec redis redis-cli FLUSHDB` — flush all Redis keys.
2. `docker compose exec api python -c "from database import init_db, seed_db; init_db(); seed_db()"` — trigger the API container to reload `data/artists.csv` and `data/songs.csv` into PostgreSQL.
3. Print summary.

**Output:**

```
  ✓ Flushing redis... done
  ✓ Seeding database... done
  20 artists, 500 songs loaded
```

---

### `./workshop help`

Prints a summary of all commands with descriptions and examples. Implemented via `argparse` subparsers with epilog text, aliased as a subcommand for discoverability.

---

### `./workshop list-songs [--page N] [--per-page N]`

Lists songs with pagination.

| Option       | Required | Default | Description              |
| ------------ | -------- | ------- | ------------------------ |
| `--page`     | No       | `1`     | Page number              |
| `--per-page` | No       | `20`    | Number of items per page |

**Behaviour:**

1. `GET /songs?page={page}&per_page={per_page}`.
2. Print a numbered table with ID, title, artist, and genre.

**Output:**

```
Songs (page 1/25, 500 total)
────────────────────────────────────────────────────────────
   #  ID         Title                          Artist               Genre
   1. song-1     Bohemian Rhapsody              Queen                Rock
   2. song-2     Stairway to Heaven             Led Zeppelin         Rock
   ...
⏱ 12 ms
```

---

### `./workshop list-artists [--page N] [--per-page N]`

Lists artists with pagination.

| Option       | Required | Default | Description              |
| ------------ | -------- | ------- | ------------------------ |
| `--page`     | No       | `1`     | Page number              |
| `--per-page` | No       | `20`    | Number of items per page |

**Behaviour:**

1. `GET /artists?page={page}&per_page={per_page}`.
2. Print a numbered table with ID, name, and genre.

**Output:**

```
Artists (page 1/1, 20 total)
─────────────────────────────────────────────
   #  ID           Name                      Genre
   1. artist-1     Queen                     Rock
   2. artist-2     Led Zeppelin              Rock
   ...
⏱ 8 ms
```

---

### `./workshop daily-mix --user <username>`

Calls the daily-mix API endpoint and reports timing.

| Option   | Required | Default  | Description                     |
| -------- | -------- | -------- | ------------------------------- |
| `--user` | No       | `user-1` | Username to derive user ID from |

**Behaviour:**

1. Derive user ID from `--user`.
2. `GET /daily-mix` with `X-User-ID` header. Measure wall-clock time.
3. Print response time and the first 5 song titles as a preview.

**Output:**

```
GET /daily-mix (user: user-1, id: 553d2075-...)
⏱ 5.03 s

  1. Bohemian Rhapsody — Queen
  2. Stairway to Heaven — Led Zeppelin
  3. Hotel California — Eagles
  ...
  (50 songs total)
```

---

### `./workshop simulate-plays --song <id> [--count N] [--concurrent]`

Fires play events and reports the final counter.

| Option         | Required | Default | Description                                                 |
| -------------- | -------- | ------- | ----------------------------------------------------------- |
| `--song`       | Yes      | —       | Song ID (e.g. `song-1`)                                     |
| `--count`      | No       | `100`   | Number of play events                                       |
| `--concurrent` | No       | `false` | If set, fires all requests concurrently using a thread pool |

**Behaviour:**

1. If `--concurrent`: use `concurrent.futures.ThreadPoolExecutor` to fire all `POST /songs/{id}/play` requests in parallel.
2. If sequential: fire requests one by one.
3. After all requests complete, `GET /songs/{id}` to read the current `play_count`.
4. Print expected vs actual count to highlight lost updates (Module 2).

**Output (broken):**

```
Firing 500 concurrent plays for song-1 (current: 0)...
  Plays [█████████████████████████] 500/500
⏱ 3.21 s
Expected: 0 + 500 = 500
Actual:   487 ✗ (13 lost)
```

**Output (fixed):**

```
Firing 500 concurrent plays for song-1 (current: 0)...
  Plays [█████████████████████████] 500/500
⏱ 1.85 s
Expected: 0 + 500 = 500
Actual:   500 ✓
```

---

### `./workshop add-listeners --artist <id> [--count N] [--range R]`

Adds random listeners to an artist via the API and reports timing.

| Option     | Required | Default   | Description                                     |
| ---------- | -------- | --------- | ----------------------------------------------- |
| `--artist` | Yes      | —         | Artist ID (e.g. `artist-1`)                     |
| `--count`  | No       | `1000`    | Number of listener events to send               |
| `--range`  | No       | `1000000` | Size of the random listener pool to sample from |

**Behaviour:**

1. Sample `N` unique indices from a pool of `R` possible listeners (e.g. `listener-000000` through `listener-{R-1}`).
2. For each, derive the user ID and call `POST /artists/{id}/listeners` with the `X-User-ID` header.
3. Print elapsed time and the current listener count from `GET /artists/{id}`.

**Output:**

```
Adding 100000 listeners (from pool of 1000000) to artist-1...
  Listeners [█████████████████████████] 100000/100000
⏱ 12.45 s
Monthly listeners: 100000
```

---

### `./workshop top-songs [--limit N]`

Prints the current leaderboard.

| Option    | Required | Default | Description                    |
| --------- | -------- | ------- | ------------------------------ |
| `--limit` | No       | `10`    | Number of top songs to display |

**Behaviour:**

1. `GET /leaderboard?per_page={limit}`.
2. Print a numbered table with rank, song ID, title, artist, and play count.

**Output:**

```

Top 10 Songs
──────────────────────────────────────────────────────────
 #   ID         Song                   Artist              Plays
 1.  song-1     Bohemian Rhapsody      Queen                 35
 2.  song-2     Stairway to Heaven     Led Zeppelin          20
 3.  song-3     Hotel California       Eagles                12
 ...
⏱ 3 ms
```

---

### `./workshop get-redis-memory-usage`

Prints memory stats for workshop-related Redis keys using `docker exec`. No arguments.

**Behaviour:**

1. Run `docker compose exec redis redis-cli INFO memory` to get overall memory usage.
2. Run `docker compose exec redis redis-cli --scan --pattern '<pattern>'` for each key group, then `MEMORY USAGE` per key.
3. Parse output and print a breakdown by key pattern.

**Output:**

```
Redis Memory Usage
──────────────────────────────────────────────
  Key pattern              Count    Memory
  daily-mix:*                  1    1.2 KiB
  play-count:song:*           12    0.9 KiB
  monthly-listeners:*          2    4.8 MiB
  hll-listeners:*              2   24.0 KiB
  top-songs                    1    1.1 KiB
  song-vectors                 0        —
──────────────────────────────────────────────
  Total                                4.8 MiB
⏱ 150 ms
```

---

### `./workshop load-embeddings`

Triggers the API to compute song embeddings and load them into a Redis VectorSet. No arguments.

The embedding computation (`sentence-transformers`) runs inside the API container, which already has the dependency installed.

**Behaviour:**

1. `POST /admin/load-embeddings` — the API reads the CSV data, computes embeddings using `sentence-transformers`, and loads them into Redis via `VADD`.
2. The CLI polls or streams the response and prints progress.

**Output:**

```
  ⠹ Loading embeddings (this may take a while)...
  ✓ Loading embeddings (this may take a while)... done
  ✓ 500 song embeddings loaded (384 dimensions)
  ⏱ 18.72 s
```

---

### `./workshop similar-songs --song <id> [--count N]`

Queries the VectorSet for similar songs.

| Option    | Required | Default | Description                       |
| --------- | -------- | ------- | --------------------------------- |
| `--song`  | Yes      | —       | Song ID (e.g. `song-42`)          |
| `--count` | No       | `5`     | Number of similar songs to return |

**Behaviour:**

1. `GET /songs/{id}/similar?count={count}`.
2. Print a numbered list with song title, artist, and similarity score.

**Output:**

```

Songs similar to "Bohemian Rhapsody" (song-42)
───────────────────────────────────────────────

1.  We Will Rock You — Queen           (0.94)
2.  Somebody to Love — Queen           (0.91)
3.  Don't Stop Me Now — Queen          (0.88)
4.  Back in Black — AC/DC              (0.82)
5.  Thunderstruck — AC/DC              (0.79)
⏱ 2 ms
```
