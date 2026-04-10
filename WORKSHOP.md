# Redis Music Workshop

> A 2-hour, hands-on workshop to introduce Redis

## Context

You work at a music-streaming company. The product has a **React web front-end** backed by a **Python REST API** (FastAPI) that uses **PostgreSQL** as its primary database for songs and artists.

Everything works — until it doesn't. As the platform grows, several parts of the system start showing performance, correctness, and scalability problems.
In each module you will **observe a concrete problem**, then **fix it with the right Redis data structure**.

---

## Architecture

```
┌────────────┐       ┌────────────┐       ┌────────────┐
│   React    │──────▶│  REST API  │──────▶│ PostgreSQL │
│  Frontend  │◀──────│  (Python)  │◀──────│            │
└────────────┘       └────┬───┬───┘       └────────────┘
                          │   ▲
                          ▼   │
                     ┌────────────┐
                     │   Redis    │
                     └────────────┘
```

All services run via **Docker Compose**. Students clone the repo and run `docker compose up`.

---

## Time budget

| Block                  | Duration | Content                                                        |
| ---------------------- | -------- | -------------------------------------------------------------- |
| Setup & intro          | 10 min   | Architecture walkthrough, `docker compose up`, verify UI works |
| Module 1 — Caching     | 20 min   | Strings, `SET`/`GET`, TTL                                      |
| Module 2 — Counters    | 15 min   | `INCR`, atomicity                                              |
| Module 3 — Sorted Sets | 15 min   | `ZINCRBY`, `ZREVRANGE`                                         |
| Module 4 — Sets        | 15 min   | `SADD`, `SCARD`, `SISMEMBER`                                   |
| Module 5 — HyperLogLog | 15 min   | `PFADD`, `PFCOUNT`, memory comparison                          |
| Module 6 — VectorSets  | 20 min   | `VADD`, `VSIM` _(bonus — only if time allows)_                 |
| Wrap-up                | 10 min   | Recap, Q&A                                                     |

---

## CLI utility — `workshop`

A Python CLI tool (`workshop`) ships with the repo. It wraps every simulation, data-loading, and verification step so students don't waste time writing boilerplate. It is implemented with `argparse` and uses the same RESTful API / Redis / PostgreSQL connections as the application.

The `--user` flag accepts a **username** (e.g. `user-1`) and derives the 36-char UUID internally, matching the frontend behaviour.

```
./workshop <command> [options]
```

### Commands

| Command                                                            | Module | What it does                                                             |
| ------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------ |
| `./workshop reset`                                                 | —      | Resets PostgreSQL and Redis, reloads CSV data into PostgreSQL            |
| `./workshop help`                                                  | —      | Prints a detailed help message                                           |
| `./workshop list-songs [--page N] [--per-page N]`                  | —      | Lists songs                                                              |
| `./workshop list-artists [--page N] [--per-page N]`                | —      | Lists artists                                                            |
| `./workshop daily-mix [--user <username>]`                         | 1      | Calls the daily-mix endpoint and prints the response time                |
| `./workshop simulate-plays --song <id> [--count N] [--concurrent]` | 2      | Fires N play events (optionally concurrent) and prints the final counter |
| `./workshop top-songs [--limit N]`                                 | 3      | Prints the current Top-N most-played songs                               |
| `./workshop add-listeners --artist <id> [--count N]`               | 4, 5   | Adds N random listeners using the API, prints timing                     |
| `./workshop get-redis-memory-usage`                                | 5      | Prints the memory used by Redis                                          |
| `./workshop load-embeddings`                                       | 6      | Triggers the API to compute embeddings and load them into a VectorSet    |
| `./workshop similar-songs --song <id> [--count N]`                 | 6      | Queries the VectorSet for similar songs                                  |

---

## Module 1 — Caching & TTL

**⏱ 20 min**

### Problem

The platform generates **daily mixes** for every user. The algorithm is slow: for each request it loops over all songs, scoring each one before returning the top 50.

> _Simulated in code with a `time.sleep(5)` inside the generation function. Keep it to simulate a real-world expensive computation._

Calling the endpoint twice for the same user runs the expensive algorithm twice.

### Observe

```bash
./workshop daily-mix --user user-1          # ~5 s
./workshop daily-mix --user user-1          # ~5 s again — no caching
```

### Goal

Use Redis as a **cache** so the computation runs once and subsequent requests are instant.

### Key Redis commands

| Command                    | Purpose                                   |
| -------------------------- | ----------------------------------------- |
| `SET key value EX seconds` | Store the result with an automatic expiry |
| `GET key`                  | Retrieve the cached result                |
| `TTL key`                  | Check remaining time-to-live              |
| `DEL key`                  | Manually invalidate                       |

### Steps

1. Open `api/services/daily_mix.py`.
2. Before the slow computation, check Redis: `GET daily-mix:{user_id}`. If found, return it.
3. After computing, store: `SET daily-mix:{user_id} <json> EX 86400`.
4. Verify:

```bash
./workshop daily-mix --user user-1          # ~5 s (cold)
./workshop daily-mix --user user-1          # < 10 ms (cached)
```

### Discussion

- What happens after 24 h?
- How would the user force a refresh? (`DEL`)
- What are the risks of caching? (stale data, cold starts, thundering herd)

---

## Module 2 — Atomic Counters

**⏱ 15 min**

### Problem

Every play event increments a counter in PostgreSQL using `SELECT` → add 1 → `UPDATE`.
Under concurrency, two requests can read the same value and both write `count + 1` — **losing an increment**!

### Observe

```bash
./workshop simulate-plays --song song-1 --concurrent
# Expected: 100 — Actual: less than 100 (lost updates)
```

> [!TIP]
> Use `--concurrent` to fire requests in parallel — without it, requests run sequentially and the race condition won't manifest.

### Goal

Implement song play counts with Redis **atomic counters**.

### Key Redis commands

| Command    | Purpose                   |
| ---------- | ------------------------- |
| `INCR key` | Atomically increment by 1 |
| `GET key`  | Read the current count    |

### Steps

1. Open `api/services/songs.py` — find the `play_song` function.
2. Replace the SELECT/UPDATE with `INCR play-count:song:{song_id}`.
3. Verify:

```bash
./workshop simulate-plays --song song-1 --count 500 --concurrent
# Now: exactly 500 added
```

### Discussion

- How / when do you sync back to PostgreSQL?
- What happens if Redis restarts? (persistence: RDB / AOF)

> [!NOTE]
> By moving play counts to Redis, the **Top Songs** leaderboard (which still reads from PostgreSQL) is now broken — it will always show zero plays. We'll fix this right away in the next module.

---

## Module 3 — Sorted Sets

**⏱ 15 min**

### Problem

The leaderboard on the home page shows the **"Top Songs"** by play count. It queries PostgreSQL:

```sql
SELECT * FROM songs ORDER BY play_count DESC LIMIT 50;
```

After Module 2 moved play counts to Redis, this query returns stale data — PostgreSQL's `play_count` column is no longer updated.

### Goal

We need a data structure that:

1. **Associates each song with a numeric score** (its play count).
2. **Keeps members sorted by score** at all times — no need to re-sort on every read.
3. **Updates scores atomically** — concurrent play events never lose an increment.

A Redis **Sorted Set** does exactly this. Every member has a floating-point score, and Redis keeps them sorted automatically. Inserts, score updates, and range queries are all **O(log N)**.

Use a Sorted Set where every play event atomically updates the ranking, and the leaderboard reads directly from it.

### Key Redis commands

| Command                        | Purpose                            |
| ------------------------------ | ---------------------------------- |
| `ZINCRBY key increment member` | Atomically add to a member's score |
| `ZREVRANGE key 0 N WITHSCORES` | Top N members by score             |
| `ZREVRANK key member`          | "What position is this song?"      |
| `ZSCORE key member`            | "How many plays?"                  |

### Steps

1. Open `api/services/songs.py` — in the `play_song` function, after `INCR`, also call `ZINCRBY top-songs 1 {song_id}`.
2. Open `api/services/leaderboard.py` — replace the PostgreSQL query with `ZREVRANGE top-songs 0 49 WITHSCORES`.
3. Verify:

```bash
./workshop simulate-plays --song song-1 --count 20 --concurrent
./workshop simulate-plays --song song-2 --count 35 --concurrent
./workshop top-songs --limit 10
# song-2: 35, song-1: 20
```

### Discussion

- How would you build a "trending this week" chart? (time-windowed key + `EXPIRE`)

---

## Module 4 — Sets

**⏱ 15 min**

### Problem

The platform tracks **monthly distinct listeners** per artist. The current implementation uses a Redis **List**: before appending a user ID, it scans the list to check for duplicates — **O(N) per event**.

### Observe

```bash
./workshop add-listeners --artist artist-1 --count 100000     # note the time
./workshop add-listeners --artist artist-1 --count 100000     # same operation, but slower — List now has 100K entries, O(N) check on every insert
```

### Goal

Use a Redis **Set** for **O(1)** add-with-dedup.

### Key Redis commands

| Command                | Purpose                                 |
| ---------------------- | --------------------------------------- |
| `SADD key member`      | Add; ignores duplicates                 |
| `SCARD key`            | Count distinct members                  |
| `SISMEMBER key member` | Check membership in O(1)                |
| `SINTER key1 key2`     | Listeners in common between two artists |

### Steps

1. Open `api/services/artists.py` — find the `add_listener` function.
2. Replace the List + scan with `SADD monthly-listeners:{artist_id}:{YYYY-MM} {user_id}`.
3. Verify:

```bash
./workshop reset
./workshop add-listeners --artist artist-1 --count 100000
# Constant speed regardless of size
```

### Discussion

- Sets store each member in full — what about memory at 100 M scale? (→ Module 5)

---

## Module 5 — HyperLogLog

**⏱ 15 min**

### Problem

Module 4 improved speed, but **not memory** usage. Each user ID is stored in full in the Set.
Our top-5 artists count with ~100 M monthly listeners (36-char UUIDs each):

```
100 000 000 × 36 bytes ≈ 3.4 GiB per artist
5 artists ≈ 17 GiB — just for 5 artists
```

### Goal

Use **HyperLogLog**: approximate distinct count in ~12 KB of memory, regardless of cardinality.

### Key Redis commands

| Command                  | Purpose                                            |
| ------------------------ | -------------------------------------------------- |
| `PFADD key element`      | Observe an element                                 |
| `PFCOUNT key`            | Approximate distinct count (0.81 % standard error) |
| `PFMERGE dest src1 src2` | Merge HLLs (e.g. weekly → monthly)                 |

### Observe & compare

```bash
./workshop reset
./workshop add-listeners --artist artist-1 --count 1000000
./workshop get-redis-memory-usage

# TODO – add actual numbers
# Output:
#   Set   — count: ??, memory: ~?? MiB
#   HLL   — count: ~??, memory: ~?? KiB
#   Error: ~?? %
```

### Steps

1. Open `api/services/artists.py`.
2. Replace `SADD` with `PFADD hll-listeners:{artist_id}:{YYYY-MM} {user_id}`.
3. Replace the `SCARD` count endpoint with `PFCOUNT`.
4. Re-run the listener ingestion and compare memory with `./workshop get-redis-memory-usage`.

### Discussion

- HLL is **probabilistic** — you cannot list members or check membership.
- When is ~1 % error acceptable? When isn't it?

---

## Module 6 — VectorSets _(bonus — if time allows)_

**⏱ 20 min**

### Problem

The product team wants a **"Similar Songs"** section. Traditional tag-based matching is too coarse.

### Goal

Use Redis **VectorSets** (Redis 8.0+) to store song embeddings and perform similarity search.

### Pre-requisites

- Song data in `data/songs.csv` (already used to seed PostgreSQL).
- The API container has `sentence-transformers` installed and computes embeddings when triggered via `POST /admin/load-embeddings`.
- Redis 8.0+ (included in the Docker Compose setup).

### Key Redis commands

| Command                                               | Purpose                      |
| ----------------------------------------------------- | ---------------------------- |
| `VADD key [REDUCE dim] FP32 element VALUES v1 v2 ...` | Store an embedding           |
| `VSIM key ELE element COUNT N`                        | Find N most similar elements |

### Steps

1. Load the embeddings:

```bash
./workshop load-embeddings
# Loaded 500 song embeddings into VectorSet "song-vectors"
```

2. Query:

```bash
./workshop similar-songs --song song-42 --count 5
# 1. song-108  (score: 0.94)
# 2. song-271  (score: 0.91)
# ...
```

3. Wire `GET /songs/{id}/similar` to `VSIM song-vectors ELE {song_id} COUNT 10`.

### Discussion

- How do you update embeddings when metadata changes?
- Trade-offs vs a dedicated vector database?

---

## Summary

| Module | Data structure    | Problem                                   | Time             |
| ------ | ----------------- | ----------------------------------------- | ---------------- |
| 1      | Strings + TTL     | Redundant expensive computation           | 20 min           |
| 2      | Counters (`INCR`) | Lost updates under concurrency            | 15 min           |
| 3      | Sorted Sets       | Real-time leaderboards                    | 15 min           |
| 4      | Sets              | O(N) deduplication                        | 15 min           |
| 5      | HyperLogLog       | Memory explosion for cardinality counting | 15 min           |
| 6      | VectorSets        | Semantic similarity search                | 20 min _(bonus)_ |

Each module builds on the same application. By the end, students have seen how Redis **complements** a relational database — not as a replacement, but as the right tool for specific problems.
