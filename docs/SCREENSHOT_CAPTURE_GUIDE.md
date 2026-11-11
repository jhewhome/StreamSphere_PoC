# StreamSphere PoC — Screenshot Capture Guide (Phase 6)

Keep Docker running, then capture these in order. Save into a folder such as:

`StreamSphere_PoC/docs/evidence/`

Suggested filenames are shown in backticks.

## 0) Prep

```powershell
cd "D:\MSIT\Subjects\AODB\Group Project\StreamSphere_PoC"
docker compose ps
```

Confirm `api`, `postgres`, and `mongo` are Up/healthy.

Open:
- App: http://localhost:8000
- API docs: http://localhost:8000/docs

Demo accounts:
- Viewer: `viewer1` / `viewer123`
- Admin: `admin` / `admin123`

## 1) Infrastructure proof

1. Terminal showing `docker compose ps`  
   File: `01_docker_compose_ps.png`

## 2) Viewer workflow (polyglot + API)

2. Login page  
   URL: http://localhost:8000/login  
   File: `02_login_page.png`

3. Recommendations tab (scores visible)  
   Login as `viewer1`  
   File: `03_recommendations.png`

4. Catalog tab (MongoDB metadata)  
   File: `04_catalog_mongodb.png`

5. History tab (PostgreSQL history + Mongo titles)  
   Mark one movie watched first if history is empty  
   File: `05_history_polyglot.png`

## 3) API / metrics proof

6. Swagger docs landing  
   URL: http://localhost:8000/docs  
   File: `06_openapi_docs.png`

7. Recommendations API response with `elapsed_ms`  
   In `/docs`, authorize with viewer token (login via UI or `POST /api/login`), then execute  
   `GET /api/users/{user_id}/recommendations` using `user_id=2`  
   File: `07_recommendations_api_elapsed_ms.png`

8. Polyglot proof endpoint  
   Login as admin in `/docs`, execute `GET /api/admin/polyglot-proof`  
   File: `08_polyglot_proof_api.png`

## 4) Admin / governance proof

9. Admin page  
   URL: http://localhost:8000/admin  
   File: `09_admin_page.png`

10. Manual import result  
    Import a movie titled something like `Phase6 Evidence Film`  
    File: `10_admin_import.png`

11. Audit logs showing `MOVIE_IMPORT` / `LOGIN`  
    File: `11_audit_logs.png`

12. Optional RBAC proof  
    While logged in as `viewer1`, open http://localhost:8000/admin and show redirect/denial,  
    or call an admin endpoint in `/docs` with viewer token and capture 403  
    File: `12_rbac_denied.png`

## 5) Database evidence (optional but strong)

If you have time, also capture:

13. PostgreSQL sample  
    ```powershell
    docker exec -it streamsphere-postgres psql -U streamsphere -d streamsphere -c "SELECT user_id, username, role FROM users; SELECT * FROM user_preferences WHERE user_id=2; SELECT action, details FROM audit_logs ORDER BY log_id DESC LIMIT 5;"
    ```
    File: `13_postgres_records.png`

14. MongoDB sample  
    ```powershell
    docker exec -it streamsphere-mongo mongosh streamsphere --eval "db.movies.find({}, {movie_id:1,title:1,genres:1}).limit(5).toArray()"
    ```
    File: `14_mongodb_records.png`

## 6) Demo video (3–5 minutes)

Record while doing this script:

1. Show architecture idea: PG = users/activity/audit, Mongo = movies  
2. `docker compose ps`  
3. Login as viewer → recommendations → explain genre-overlap + `movie_id`  
4. Mark watched / rate  
5. Login as admin → import → audit log  
6. Show `/api/admin/polyglot-proof`  
7. Close: what was proven vs full TO-BE (Kafka/Redis/vector deferred)

Upload to Drive/YouTube (unlisted) and keep the link for the report.

## Checklist

- [ ] 01 docker compose ps
- [ ] 02 login
- [ ] 03 recommendations UI
- [ ] 04 catalog
- [ ] 05 history
- [ ] 06 openapi docs
- [ ] 07 recommendations API + elapsed_ms
- [ ] 08 polyglot proof API
- [ ] 09 admin page
- [ ] 10 import
- [ ] 11 audit logs
- [ ] 12 RBAC (optional)
- [ ] 13 postgres (optional)
- [ ] 14 mongodb (optional)
- [ ] demo video link saved
