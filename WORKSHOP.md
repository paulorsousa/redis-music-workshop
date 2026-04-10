# Redis Music Workshop

> An introductory, hands-on workshop about Redis for university software-engineering students.

## Context

You work at a music-streaming company. The product has a **React web front-end** backed by a **RESTful API** that uses **PostgreSQL** as its primary database for songs, artists, and playlists.

Everything works — until it doesn't. As the platform grows, several parts of the system start showing performance, correctness, and scalability problems. In each module of this workshop you will **identify a concrete problem**, then **solve it with the right Redis data structure or feature**.

---

## Architecture overview

```
┌────────────┐       ┌────────────┐       ┌────────────┐
│   React    │──────▶│  REST API  │──────▶│ PostgreSQL │
│  Frontend  │◀──────│  (Node.js) │◀──────│            │
└────────────┘       └─────┬──────┘       └────────────┘
                           │
                           ▼
                     ┌───────────┐
                     │   Redis   │
                     └───────────┘
```

---

## Module 1 — Caching & TTL

### Problem

The platform generates **personalised daily mixes** for every user. The algorithm is powerful but **slow and resource-intensive**: for each request it iterates over the entire song catalogue, scoring and ranking every track before returning the top 50.

> _Simulated in code with a deliberate `sleep` / busy-loop inside the generation function._

Calling the endpoint twice for the same user runs the expensive algorithm twice — wasting time and compute.

### Goal

Use Redis as a **cache** so the expensive computation only runs once, and subsequent requests are served instantly.

### Key concepts

| Concept             | Redis command   | Why it matters                                                          |
| ------------------- | --------------- | ----------------------------------------------------------------------- |
| String / JSON value | `SET`, `GET`    | Store the serialised playlist                                           |
| Time-to-live        | `EXPIRE`, `TTL` | Auto-invalidate after 24 h so users get a fresh mix daily               |
| Cache-aside pattern | —               | App checks cache first, falls back to computation, then populates cache |

### Steps

1. **Observe the problem** — call `GET /users/{id}/daily-mix` twice; both calls take ~5 s.
2. **Add a cache check** — before running the algorithm, `GET daily-mix:{userId}` from Redis.
3. **Populate the cache** — after computing the mix, `SET daily-mix:{userId} <json> EX 86400`.
4. **Verify** — second call returns in < 10 ms. Inspect `TTL daily-mix:{userId}`.

### Discussion

- What happens when the TTL expires?
- What if the user explicitly asks for a new mix? (`DEL daily-mix:{userId}`)
- What are the risks of caching (stale data, cold starts)?

---

## Module 2 — Atomic Counters

### Problem

Every time a song is played, the API increments a **play counter** in PostgreSQL:

```sql
SELECT play_count FROM songs WHERE id = ?;
-- application adds 1 --
UPDATE songs SET play_count = ? WHERE id = ?;
```

Under concurrent requests the read-modify-write cycle is **not atomic**. Two requests can read the same value and both write `count + 1`, losing an increment.

> _Simulated by adding a `sleep` between the SELECT and the UPDATE._

### Goal

Use a Redis **atomic counter** so increments are never lost, regardless of concurrency.

### Key concepts

| Concept          | Redis command    | Why it matters                                           |
| ---------------- | ---------------- | -------------------------------------------------------- |
| Atomic increment | `INCR`, `INCRBY` | Single-threaded execution guarantees no lost updates     |
| Key naming       | —                | `play-count:song:{songId}` — predictable, collision-free |

### Steps

1. **Observe the problem** — fire 100 concurrent play events for the same song; final count < 100.
2. **Replace with `INCR`** — each play event calls `INCR play-count:song:{songId}`.
3. **Verify** — fire 100 concurrent events again; final count = 100.
4. **Read the counter** — `GET play-count:song:{songId}`.

### Discussion

- How / when do you sync the counter back to PostgreSQL?
- What happens if Redis restarts? (persistence: RDB / AOF)

---

## Module 3 — Sets

### Problem

The platform tracks **monthly distinct listeners** per artist. The current implementation appends every `userId` to a **PostgreSQL array** (or a Redis List), then checks for duplicates with a linear scan before inserting.

As the number of distinct listeners grows, the duplicate check becomes **O(N)** per play event — unacceptably slow for popular artists.

### Goal

Use a Redis **Set** to track distinct listeners with **O(1)** add and membership check.

### Key concepts

| Concept         | Redis command      | Why it matters                                                   |
| --------------- | ------------------ | ---------------------------------------------------------------- |
| Add to set      | `SADD`             | Ignores duplicates automatically                                 |
| Cardinality     | `SCARD`            | Distinct listener count in O(1)                                  |
| Membership test | `SISMEMBER`        | O(1) lookup                                                      |
| Set operations  | `SINTER`, `SUNION` | Listeners in common between artists, total unique across artists |

### Steps

1. **Observe the problem** — add listeners to a list, measure time for the 1 000th vs the 100 000th insert.
2. **Switch to a Set** — `SADD monthly-listeners:artist:{artistId}:{YYYY-MM} {userId}`.
3. **Query** — `SCARD` for count, `SISMEMBER` for "has this user listened?".
4. **Bonus** — `SINTER` to find users who listen to both Artist A and Artist B.

### Discussion

- Sets store each member in full — what happens when you have 100 M members? (→ Module 5)
- How do you "reset" at the end of the month? (key-per-month + `EXPIRE`)

---

## Module 4 — Sorted Sets

### Problem

The product team wants a **"Top 50 Most Played Songs"** leaderboard on the homepage, updated in real time. Currently this requires a full-table query:

```sql
SELECT * FROM songs ORDER BY play_count DESC LIMIT 50;
```

This is expensive, especially under heavy write load, and the result is only as fresh as the last query.

### Goal

Use a Redis **Sorted Set** to maintain a real-time leaderboard where every play event automatically updates the ranking.

### Key concepts

| Concept            | Redis command              | Why it matters                                 |
| ------------------ | -------------------------- | ---------------------------------------------- |
| Add / update score | `ZINCRBY`                  | Atomically increment a member's score          |
| Top-N query        | `ZREVRANGE ... WITHSCORES` | Get the top N members by score in O(log N + M) |
| Rank lookup        | `ZREVRANK`                 | "What position is this song at?"               |
| Score lookup       | `ZSCORE`                   | "How many plays does this song have?"          |

### Steps

1. **Observe the problem** — run the SQL query under load; note latency.
2. **Increment on play** — every play event calls `ZINCRBY top-songs {songId} 1`.
3. **Query the leaderboard** — `ZREVRANGE top-songs 0 49 WITHSCORES`.
4. **Lookup a song** — `ZREVRANK top-songs {songId}` → position, `ZSCORE top-songs {songId}` → count.
5. **Bonus** — build a per-genre leaderboard: `ZINCRBY top-songs:genre:{genre} {songId} 1`.

### Discussion

- How does this relate to the counters in Module 2? Could you replace the per-song counter with the Sorted Set score?
- How would you implement a "trending this week" chart? (use a time-windowed key + `EXPIRE`)

---

## Module 5 — HyperLogLog

### Problem

Module 3 solved the correctness problem, but **not the memory problem**. Each member of a Set is stored in full. Consider the top 5 artists, each with ~100 M monthly listeners represented by a 36-character UUID:

```
100 000 000 listeners × 36 bytes ≈ 3.4 GiB per artist per month
5 artists × 3.4 GiB ≈ 17 GiB per month — just for 5 artists
```

This does not scale.

### Goal

Use **HyperLogLog** to estimate the number of distinct listeners using a fixed ~12 KB of memory per counter — regardless of cardinality.

### Key concepts

| Concept         | Redis command | Why it matters                                     |
| --------------- | ------------- | -------------------------------------------------- |
| Add element     | `PFADD`       | Observe a listener                                 |
| Estimated count | `PFCOUNT`     | Approximate distinct count (standard error 0.81 %) |
| Merge           | `PFMERGE`     | Combine multiple HLLs (e.g. weekly → monthly)      |

### Steps

1. **Observe the problem** — check `MEMORY USAGE` of the Set from Module 3 after adding 100 K members.
2. **Switch to HLL** — `PFADD hll-listeners:artist:{artistId}:{YYYY-MM} {userId}`.
3. **Query** — `PFCOUNT hll-listeners:artist:{artistId}:{YYYY-MM}`.
4. **Compare** — Set count vs HLL estimate (should be within ~1 %). Compare memory usage.
5. **Merge** — `PFMERGE` weekly HLLs into a monthly HLL.

### Discussion

- HyperLogLog is **probabilistic** — you cannot list the members or check membership. When is that trade-off acceptable?
- When would you still prefer a Set? (when you need to know _who_, not just _how many_)

---

## Module 6 — VectorSets _(bonus / advanced)_

### Problem

The product team wants a **"Similar Songs"** section on every song page. Traditional approaches (genre tags, collaborative filtering) are either too coarse or require heavy infrastructure.

### Goal

Use Redis **VectorSets** (available since Redis 8.0) to store song embeddings and perform real-time similarity searches.

### Key concepts

| Concept           | Redis command | Why it matters                                                     |
| ----------------- | ------------- | ------------------------------------------------------------------ |
| Add a vector      | `VADD`        | Store a song embedding with its ID                                 |
| Similarity search | `VSIM`        | Find the K nearest neighbours                                      |
| Dimensionality    | —             | Depends on the embedding model (e.g. 384-d for `all-MiniLM-L6-v2`) |

### Pre-requisites

- **Redis 8.0+**
- A set of **pre-computed song embeddings** (provided as a JSON/CSV file to avoid workshop-time computation)
- Embeddings generated from song metadata (title + artist + genre + mood tags) using a HuggingFace sentence-transformer model

### Steps

1. **Load embeddings** — iterate over the embeddings file and `VADD song-vectors {songId} VALUES {dim} {v1} {v2} ...`.
2. **Query** — `VSIM song-vectors VALUES {dim} {v1} {v2} ... COUNT 10` → 10 most similar songs.
3. **Lookup by song** — `VSIM song-vectors ELE {songId} COUNT 10` → 10 songs most similar to a given song.
4. **Integrate** — wire the API endpoint `GET /songs/{id}/similar` to the VectorSet query.

### Discussion

- How do you update embeddings when song metadata changes?
- What are the trade-offs vs. a dedicated vector database?
- How would you combine vector similarity with business rules (e.g. exclude explicit content)?

---

## Summary

| Module | Data structure    | Problem solved                        | Complexity |
| ------ | ----------------- | ------------------------------------- | ---------- |
| 1      | Strings + TTL     | Avoid redundant expensive computation | ⭐         |
| 2      | Counters (`INCR`) | Lost updates under concurrency        | ⭐         |
| 3      | Sets              | O(N) deduplication                    | ⭐⭐       |
| 4      | Sorted Sets       | Real-time leaderboards                | ⭐⭐       |
| 5      | HyperLogLog       | Memory explosion for cardinality      | ⭐⭐⭐     |
| 6      | VectorSets        | Semantic similarity search            | ⭐⭐⭐     |

Each module builds on a single, consistent application so that by the end of the workshop students have seen how Redis complements a relational database — not as a replacement, but as the right tool for specific problems.

1. **Observe the problem** — add listeners to a list, measure time for the 1 000th vs the 100 000th insert.
2. **Switch to a Set** — `SADD monthly-listeners:artist:{artistId}:{YYYY-MM} {userId}`.
3. **Query** — `SCARD` for count, `SISMEMBER` for "has this user listened?".
4. **Bonus** — `SINTER` to find users who listen to both Artist A and Artist B.

### Discussion

- Sets store each member in full — what happens when you have 100 M members? (→ Module 5)
- How do you "reset" at the end of the month? (key-per-month + `EXPIRE`)
