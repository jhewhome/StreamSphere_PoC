# StreamSphere PoC

Proof of Concept for **MSIT 620 — Advanced Organization of Database** Group 3.

**GitHub:** https://github.com/jhewhome/StreamSphere_PoC

This prototype validates selected StreamSphere TO-BE data architecture decisions:

1. **Polyglot persistence** — PostgreSQL (users, preferences, history, ratings, audit) + MongoDB (movie metadata), joined by `movie_id`
2. **API integration** — FastAPI REST endpoints coordinating both databases
3. **External integration** — TMDB search/import (optional API key; local fallback included)
4. **Data governance basics** — login, Viewer/Admin RBAC, password hashing, audit logs

This is **not** a full streaming platform. Video playback, Kafka, Redis, and vector search are intentionally out of scope for the initial PoC.

## Quick start

### Prerequisites

- Docker Desktop (recommended)
- Optional: free [TMDB API key](https://www.themoviedb.org/settings/api)

### Run

```bash
cd StreamSphere_PoC
copy .env.example .env
docker compose up --build
```

Open:

- App: http://localhost:8000
- API docs: http://localhost:8000/docs

### Demo accounts

| Username | Password   | Role   |
|----------|------------|--------|
| admin    | admin123   | Admin  |
| viewer1  | viewer123  | Viewer |
| viewer2  | viewer123  | Viewer |
| viewer3  | viewer123  | Viewer |
| viewer4  | viewer123  | Viewer |

## What to demonstrate

1. Login as `viewer1`
2. Open **Recommendations** — scores come from PostgreSQL preferences + MongoDB genres
3. Mark a movie watched / rate it — writes go to PostgreSQL while titles live in MongoDB
4. Login as `admin`
5. Search/import a movie, then open **Audit logs**
6. Click **Run proof** on `/admin` or call `GET /api/admin/polyglot-proof`

## Project layout

```
StreamSphere_PoC/
  docker-compose.yml
  backend/app/          # FastAPI application
  frontend/             # Simple web UI
  db/postgres/init.sql  # PostgreSQL schema
  docs/                 # Demo evidence checklist
```

## Evidence for Phase 6 / final report

See `docs/DEMO_EVIDENCE_CHECKLIST.md`.
