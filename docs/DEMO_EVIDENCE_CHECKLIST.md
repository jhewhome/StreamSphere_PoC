# StreamSphere PoC — Demo Evidence Checklist

Use this while preparing Phase 6 / final-report PoC artifacts.

## Required guideline artifacts

- [ ] GitHub repository link
- [ ] Demo video (3–5 minutes)
- [ ] Screenshots of PostgreSQL data
- [ ] Screenshots of MongoDB data
- [ ] API response screenshots (or `/docs` try-outs)
- [ ] Performance notes (recommendation `elapsed_ms`, basic response times)
- [ ] Lessons learned paragraph for the report

## Suggested screenshot set

1. Docker containers running (`docker compose ps`)
2. Login page
3. Viewer recommendations page with scores
4. `GET /api/users/{id}/recommendations` JSON showing method + elapsed_ms
5. PostgreSQL query result for `user_preferences` / `viewing_history` / `audit_logs`
6. MongoDB `movies` documents (Compass, mongosh, or API catalog)
7. Admin search + import
8. Audit log table after import
9. Viewer denied from `/admin` (optional governance proof)
10. `/api/admin/polyglot-proof` response

## Demo script (about 4 minutes)

1. Show architecture slide: PostgreSQL vs MongoDB responsibilities
2. Start app / open UI
3. Login as `viewer1` → recommendations
4. Explain score formula and cross-database join by `movie_id`
5. Mark watched / rate → show PostgreSQL write
6. Login as `admin` → import movie → show MongoDB write + audit log
7. Open `/api/admin/polyglot-proof`
8. Close with what was proven vs full TO-BE (Kafka/Redis/vector deferred)

## Principles proven

| Principle | Evidence |
|-----------|----------|
| Polyglot persistence | Recommendations + history enrich Mongo titles from PG ids |
| API integration | REST endpoints used by UI and `/docs` |
| External integration | TMDB search/import (or documented local fallback) |
| Data governance | Hashed passwords, RBAC, audit logs |
