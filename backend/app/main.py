from __future__ import annotations

import time
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from app.database import movies_collection, pg_execute, pg_fetchall, pg_fetchone
from app.seed import run_seed
from app.services import (
    ensure_user_access,
    get_recommendations,
    get_user_or_404,
    import_movie,
    tmdb_movie_details,
    tmdb_search,
    write_audit,
)

app = FastAPI(
    title="StreamSphere PoC API",
    description=(
        "Proof of Concept for StreamSphere polyglot persistence "
        "(PostgreSQL + MongoDB), REST API integration, external TMDB import, "
        "and basic data governance controls."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_APP_DIR = Path(__file__).resolve().parent
_CANDIDATE_FRONTENDS: list[Path] = []
# Docker layout: /app/app/main.py -> /app/frontend
if len(_APP_DIR.parents) > 1:
    _CANDIDATE_FRONTENDS.append(_APP_DIR.parents[1] / "frontend")
# Local layout: StreamSphere_PoC/backend/app/main.py -> StreamSphere_PoC/frontend
if len(_APP_DIR.parents) > 2:
    _CANDIDATE_FRONTENDS.append(_APP_DIR.parents[2] / "frontend")
FRONTEND_DIR = next((p for p in _CANDIDATE_FRONTENDS if p.exists()), Path("/app/frontend"))


class LoginRequest(BaseModel):
    username: str
    password: str


class RatingRequest(BaseModel):
    movie_id: int
    rating: float = Field(ge=1, le=5)


class HistoryRequest(BaseModel):
    movie_id: int


class MovieCreateRequest(BaseModel):
    title: str
    genres: list[str] = []
    description: str = ""
    release_year: int | None = None
    tags: list[str] = []
    poster_url: str | None = None
    tmdb_id: int | None = None
    runtime_minutes: int | None = None
    movie_id: int | None = None


class ImportRequest(BaseModel):
    """Import from TMDB by id, or insert a manual metadata payload."""

    tmdb_id: int | None = None
    title: str | None = None
    genres: list[str] = []
    description: str = ""
    release_year: int | None = None
    tags: list[str] = []
    poster_url: str | None = None
    runtime_minutes: int | None = None
    movie_id: int | None = None


@app.on_event("startup")
def on_startup() -> None:
    # Wait briefly for databases when starting under Compose.
    for _ in range(30):
        try:
            pg_fetchone("SELECT 1 AS ok")
            movies_collection().database.client.admin.command("ping")
            run_seed()
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Databases were not ready during startup")


@app.get("/api/health")
def health() -> dict[str, Any]:
    pg_ok = False
    mongo_ok = False
    try:
        pg_ok = pg_fetchone("SELECT 1 AS ok") is not None
    except Exception as exc:
        return {"status": "degraded", "postgres": False, "mongo": False, "error": str(exc)}
    try:
        movies_collection().database.client.admin.command("ping")
        mongo_ok = True
    except Exception as exc:
        return {"status": "degraded", "postgres": pg_ok, "mongo": False, "error": str(exc)}
    return {"status": "ok", "postgres": pg_ok, "mongo": mongo_ok}


@app.post("/api/login")
def login(body: LoginRequest) -> dict[str, Any]:
    user = pg_fetchone(
        "SELECT user_id, username, role, password_hash FROM users WHERE username = %s",
        (body.username,),
    )
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user["user_id"], user["username"], user["role"])
    write_audit(user["user_id"], "LOGIN", f"User {user['username']} logged in")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
        },
    }


@app.post("/api/logout")
def logout(user: Annotated[dict, Depends(get_current_user)]) -> dict[str, str]:
    write_audit(user["user_id"], "LOGOUT", f"User {user['username']} logged out")
    return {"message": "Logged out"}


@app.get("/api/me")
def me(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    prefs = pg_fetchall(
        "SELECT preferred_genre FROM user_preferences WHERE user_id = %s",
        (user["user_id"],),
    )
    return {
        **user,
        "preferred_genres": [p["preferred_genre"] for p in prefs],
    }


@app.get("/api/movies")
def list_movies(
    user: Annotated[dict, Depends(get_current_user)],
    q: str | None = None,
) -> list[dict]:
    query: dict[str, Any] = {}
    if q:
        query["title"] = {"$regex": q, "$options": "i"}
    return list(movies_collection().find(query, {"_id": 0}).sort("movie_id", 1))


@app.get("/api/movies/{movie_id}")
def movie_detail(movie_id: int, user: Annotated[dict, Depends(get_current_user)]) -> dict:
    movie = movies_collection().find_one({"movie_id": movie_id}, {"_id": 0})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@app.get("/api/users/{user_id}/recommendations")
def recommendations(
    user_id: int,
    user: Annotated[dict, Depends(get_current_user)],
    limit: int = Query(default=10, ge=1, le=50),
) -> dict[str, Any]:
    ensure_user_access(user, user_id)
    get_user_or_404(user_id)
    started = time.perf_counter()
    results = get_recommendations(user_id, limit=limit)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "user_id": user_id,
        "count": len(results),
        "elapsed_ms": elapsed_ms,
        "method": "genre-overlap across PostgreSQL preferences + MongoDB metadata",
        "results": results,
    }


@app.get("/api/users/{user_id}/history")
def history(user_id: int, user: Annotated[dict, Depends(get_current_user)]) -> list[dict]:
    ensure_user_access(user, user_id)
    get_user_or_404(user_id)
    rows = pg_fetchall(
        """
        SELECT history_id, user_id, movie_id, watched_at
        FROM viewing_history
        WHERE user_id = %s
        ORDER BY watched_at DESC
        """,
        (user_id,),
    )
    enriched = []
    for row in rows:
        movie = movies_collection().find_one({"movie_id": row["movie_id"]}, {"_id": 0, "title": 1, "genres": 1})
        enriched.append({**row, "movie": movie})
    return enriched


@app.post("/api/users/{user_id}/history")
def add_history(
    user_id: int,
    body: HistoryRequest,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    ensure_user_access(user, user_id)
    get_user_or_404(user_id)
    if not movies_collection().find_one({"movie_id": body.movie_id}):
        raise HTTPException(status_code=404, detail="Movie not found in MongoDB catalog")
    row = pg_execute(
        """
        INSERT INTO viewing_history (user_id, movie_id)
        VALUES (%s, %s)
        RETURNING history_id, user_id, movie_id, watched_at
        """,
        (user_id, body.movie_id),
    )
    write_audit(user["user_id"], "VIEW_RECORDED", f"user_id={user_id} movie_id={body.movie_id}")
    return row or {}


@app.post("/api/users/{user_id}/ratings")
def add_rating(
    user_id: int,
    body: RatingRequest,
    user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    ensure_user_access(user, user_id)
    get_user_or_404(user_id)
    if not movies_collection().find_one({"movie_id": body.movie_id}):
        raise HTTPException(status_code=404, detail="Movie not found in MongoDB catalog")
    row = pg_execute(
        """
        INSERT INTO ratings (user_id, movie_id, rating)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, movie_id)
        DO UPDATE SET rating = EXCLUDED.rating, created_at = NOW()
        RETURNING rating_id, user_id, movie_id, rating, created_at
        """,
        (user_id, body.movie_id, body.rating),
    )
    write_audit(
        user["user_id"],
        "RATING_UPSERT",
        f"user_id={user_id} movie_id={body.movie_id} rating={body.rating}",
    )
    return row or {}


@app.get("/api/admin/movie-search")
async def admin_movie_search(
    admin: Annotated[dict, Depends(require_admin)],
    q: str = Query(min_length=1),
) -> dict[str, Any]:
    from app.config import get_settings

    settings = get_settings()
    if not settings.tmdb_api_key:
        # Offline-friendly fallback so the PoC still demos admin search without a key.
        local = list(
            movies_collection().find(
                {"title": {"$regex": q, "$options": "i"}},
                {"_id": 0, "movie_id": 1, "title": 1, "description": 1, "release_year": 1, "poster_url": 1},
            )
        )
        write_audit(admin["user_id"], "ADMIN_SEARCH_LOCAL", f"query={q}")
        return {
            "source": "local-mongodb-fallback",
            "note": "TMDB_API_KEY not set. Showing local catalog matches. Add a TMDB key for external search.",
            "results": local,
        }

    results = await tmdb_search(q)
    write_audit(admin["user_id"], "ADMIN_SEARCH_TMDB", f"query={q} results={len(results)}")
    return {"source": "tmdb", "results": results}


@app.post("/api/admin/movies/import")
async def admin_import_movie(
    body: ImportRequest,
    admin: Annotated[dict, Depends(require_admin)],
) -> dict:
    if body.tmdb_id is not None and not body.title:
        details = await tmdb_movie_details(int(body.tmdb_id))
        if not details:
            raise HTTPException(
                status_code=404,
                detail="TMDB movie not found or TMDB_API_KEY missing",
            )
        return import_movie(details, admin["user_id"])

    payload = body.model_dump()
    if not payload.get("title"):
        raise HTTPException(status_code=400, detail="title is required for manual import")
    return import_movie(payload, admin["user_id"])


@app.post("/api/admin/movies")
def admin_create_movie(
    body: MovieCreateRequest,
    admin: Annotated[dict, Depends(require_admin)],
) -> dict:
    return import_movie(body.model_dump(), admin["user_id"])


@app.get("/api/admin/audit-logs")
def admin_audit_logs(
    admin: Annotated[dict, Depends(require_admin)],
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict]:
    return pg_fetchall(
        """
        SELECT log_id, user_id, action, details, created_at
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (limit,),
    )


@app.get("/api/admin/polyglot-proof")
def polyglot_proof(admin: Annotated[dict, Depends(require_admin)]) -> dict[str, Any]:
    """Single workflow evidence: PostgreSQL preferences + MongoDB movies joined by movie_id."""
    sample_user = pg_fetchone(
        "SELECT user_id, username FROM users WHERE role = 'Viewer' ORDER BY user_id LIMIT 1"
    )
    if not sample_user:
        raise HTTPException(status_code=404, detail="No viewer user found")
    prefs = pg_fetchall(
        "SELECT preferred_genre FROM user_preferences WHERE user_id = %s",
        (sample_user["user_id"],),
    )
    mongo_count = movies_collection().count_documents({})
    recs = get_recommendations(sample_user["user_id"], limit=5)
    return {
        "principle": "Polyglot persistence in one workflow",
        "postgresql": {
            "user": sample_user,
            "preferred_genres": [p["preferred_genre"] for p in prefs],
        },
        "mongodb": {"movie_count": mongo_count},
        "joined_recommendations": recs,
    }


# Frontend (static)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/login")
    def login_page() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "login.html")

    @app.get("/admin")
    def admin_page() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "admin.html")
