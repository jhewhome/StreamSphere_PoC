# Phase 6 / Final Report — PoC Write-up Outline

Use this as your group’s drafting guide for **Part 5: Proof of Concept**.  
Write in your own words. Do not paste this outline unchanged into TURNITIN.

Measured smoke-test values from the local run (replace with your final screenshot values if different):

- Health: PostgreSQL connected, MongoDB connected
- Recommendations for `viewer1`: 10 results, about **25–30 ms**
- Method: genre-overlap across PostgreSQL preferences + MongoDB metadata
- Catalog size after seed: 30 movies
- Governance: login, Viewer/Admin RBAC, bcrypt password hashes, audit logs
- Import proof: admin can insert movie metadata into MongoDB and write audit row in PostgreSQL

---

## 5.1 PoC Objectives

Draft points:

- Validate that StreamSphere’s polyglot design can work in a reduced prototype
- Prove API integration across two data stores in one user workflow
- Demonstrate basic governance controls required by the acceptance conditions
- Keep scope intentionally small: no video streaming, Kafka, Redis, or vector search in this PoC

Suggested objective statement:

> The PoC aims to prove that separating structured subscriber activity data in PostgreSQL from flexible catalog metadata in MongoDB can support a practical recommendation workflow through a unified REST API, with authentication, authorization, and audit logging.

Principles validated:

1. Polyglot persistence
2. API integration
3. External/admin metadata integration
4. Data governance basics

## 5.2 PoC Architecture

Describe components:

- Frontend (catalog, recommendations, admin)
- FastAPI REST API
- PostgreSQL: users, preferences, viewing history, ratings, audit logs
- MongoDB: movie documents
- Shared key: `movie_id`
- Optional TMDB key for external search; manual import supported without it

Include / reference:

- PoC architecture diagram (required among final diagrams)
- Short note that this is a subset of the full TO-BE architecture from Phase 4

## 5.3 PoC Implementation

Step-by-step (from what you actually built):

1. Docker Compose for PostgreSQL, MongoDB, and API
2. PostgreSQL schema + seed users/preferences/history
3. MongoDB movie seed collection
4. REST endpoints for login, catalog, recommendations, history, ratings, admin import/audit
5. Genre-overlap recommendation scoring
6. Frontend screens for viewer and admin flows
7. Security: JWT auth, password hashing, role checks, audit writes

Technologies:

- Docker / Docker Compose
- PostgreSQL 16
- MongoDB 7
- FastAPI / Uvicorn
- HTML/CSS/JS frontend
- Optional TMDB API

Challenges encountered (edit to match your experience):

- Docker engine dependency on WSL / Desktop startup
- Keeping Phase 5 evaluation claims aligned with reduced PoC scope
- Cross-store consistency without foreign keys across databases
- Balancing demo completeness vs. avoiding overbuilding the full TO-BE stack

## 5.4 PoC Results

What worked:

- Single recommendation workflow successfully read PostgreSQL preferences and MongoDB genres
- REST API coordinated both stores
- Admin import wrote MongoDB metadata and PostgreSQL audit evidence
- RBAC separated Viewer and Admin capabilities
- Basic performance measurement available through recommendation `elapsed_ms`

What did not / deferred:

- Kafka event propagation not implemented in PoC
- Redis cache not implemented
- Vector/semantic recommendation not implemented
- Live TMDB calls require an API key; PoC still works with manual/local import

Performance metrics table (fill from screenshots):

| Metric | Observed value | Notes |
|---|---|---|
| Recommendation response time | ~25–30 ms | Local Docker environment |
| Movie catalog size | 30 (+ imported titles) | Seed + admin import |
| Databases used in one workflow | 2 | PostgreSQL + MongoDB |
| Auth model | JWT + bcrypt | Viewer/Admin roles |

Evidence to attach/link:

- GitHub repository URL
- Demo video URL
- Screenshots 01–14 from `SCREENSHOT_CAPTURE_GUIDE.md`

## 5.5 Lessons Learned

Possible lessons (rewrite in group voice):

1. Polyglot persistence is valuable when workloads differ, but the application layer must own cross-store joins and consistency rules.
2. A focused PoC is more persuasive than a broad unfinished prototype.
3. Governance controls (authn/authz/audit) should be demonstrated early because they are part of architectural credibility, not only paperwork.
4. Full TO-BE components (Kafka, Redis, vectors) remain justified for production-scale StreamSphere, but are not required to prove the core data-organization idea.
5. Clear service/data ownership and shared identifiers (`movie_id`) are essential for multi-database designs.

How the design would be improved next:

- Add CDC/event propagation for catalog changes
- Introduce Redis for hot feeds / reference checks
- Add vector retrieval for semantic recommendations
- Strengthen automated reconciliation between PostgreSQL references and MongoDB catalog IDs

---

## Submission package checklist

- [ ] Working PoC runnable via `docker compose up --build`
- [ ] GitHub repo public or shared with instructor
- [ ] Demo video 3–5 minutes
- [ ] Screenshots saved and inserted in report
- [ ] Part 5 sections written in group members’ own words
- [ ] PoC architecture diagram included
- [ ] Phase 5 wording aligned so it does not claim Kafka/vector PoC validation
